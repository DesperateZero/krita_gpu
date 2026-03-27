# Vulkan 分支现状审视与工程走向分析

**日期**：2026-03-26
**基准**：`feature/vulkan-phase6-graphics-pipeline` (ac3ec5d27c) vs 原版设计文档 & OpenGL 渲染路径

---

## 一、现状总结：已建成什么

Phase 1-6 的 10 个提交共引入 **38 个源文件、~12,000 行 C++、~1,000 行 GLSL**，落地了一套完整的 Vulkan GPU 画布原型：

| 层级 | 模块 | 核心能力 |
|:---|:---|:---|
| 基础设施 | DeviceManager / MemoryPool / Swapchain | VMA 显存池、稀疏绑定特性探测、三重缓冲 |
| 瓦片系统 | TileManager / TileCache / TransferQueue / Prefetcher | 131K×131K 虚拟稀疏纹理、L1/L2/L3 分级缓存、Timeline Semaphore 异步 DMA、视口预取 |
| 计算笔刷 | BrushEngine / ComputePipeline / RingBuffer | SDF 圆笔刷 dab、Push Constants 高频更新、SPSC 无锁输入队列 |
| 渲染线程 | RenderThread / FrameResources | 独立高优先级线程、帧级同步原语、120Hz 目标帧率 |
| 图层合成 | LayerCompositor | 8 种混合模式的 Compute Shader 合成 |
| 图形管线 | GraphicsPipeline + 10 个着色器 | Bicubic 画布显示、Miter-Joint 笔刷轮廓、像素网格、QPainter 装饰叠加层 |
| 集成路由 | PaintRouter / VulkanCanvas | 笔刷参数桥接、CPU↔GPU 同步接口（框架级） |

**对 Krita 核心的侵入极小**：仅修改了 `kis_canvas2.cpp` 1 个文件（条件编译），外加 `KisTool::paintToolOutline` 的一个 dynamic_cast 分支。

---

## 二、关键发现：代码审查揭示的真实状态

文档描述与实际代码之间存在几处需要正视的落差：

### 2.1 ✅ `startUpdateCanvasProjection` — 已修复 (Phase 7A)

**原始问题**：`startUpdateCanvasProjection()` 返回 null，Vulkan 画布完全跳过了 Krita 的标准脏矩形更新管线。

**修复方案**：
* 新增 `KisVulkanUpdateInfo` 类（继承 `KisUpdateInfo`），携带 `QVector<KisVulkanTileUpdateEntry>` 瓦片列表。
* `startUpdateCanvasProjection(rc)` 现在从 `KisPaintDevice::readBytes()` 读取受影响瓦片的像素数据，构建有效的 `KisVulkanUpdateInfo` 返回。
* `updateCanvasProjection(info)` 将瓦片像素通过 `uploadTileData()` + Transfer Queue 异步上传到 GPU 稀疏纹理。
* 支持全瓦片直传和部分瓦片读-改-写两种路径。
* 笔刷绘画路径不受影响——仍通过 Ring Buffer 直达 GPU Compute Shader。

### 2.2 `syncToCPU` / `syncToGPU` 是骨架代码

```cpp
void KisVulkanPaintRouter::syncToCPU(const QRect &dirtyRect) {
    // 下载瓦片数据到 QByteArray... 但没有写入 KisPaintDevice
    dbgKrita << "Synced" << tiles.size() << "tiles to CPU";
}

void KisVulkanPaintRouter::syncToGPU(const QRect &dirtyRect) {
    // 查找瓦片... 但没有实际上传
    dbgKrita << "Synced" << tiles.size() << "tiles to GPU";
}
```

**含义**：撤销/保存目前**不工作**。GPU 瓦片与 `KisPaintDevice` 之间没有真正的数据传输。这是笔画边界处需要补齐的异步同步逻辑，不影响绘画实时路径。

### 2.3 笔刷引擎与 Krita 笔刷生态完全隔离

在 `libs/image_vulkan` 中搜索 `KisStrokeStrategy`、`KisPaintOp`、`KisToolFreehand` 结果为零。`KisVulkanBrushEngine` 是自包含的 SDF 圆笔刷，不使用 Krita 的笔刷预设/动态/引擎插件框架。

**含义**：当前 Vulkan 笔刷无法使用 Krita 的 200+ 笔刷预设。需要一个薄适配层将 `KisPaintOp` 接口的决策结果（dab 位置与参数）转发给 GPU 引擎。

### 2.4 图层合成器是独立模型

`KisVulkanLayerCompositor` 操作自己的图层概念，不与 `KisNode` 树关联。没有组图层、调整图层、蒙版。

**含义**：需要建立 KisNode → GPU 图层的元数据映射。图层像素数据本身已在 GPU 虚拟纹理中，缺的是结构信息的同步。

### 2.5 色彩管线硬编码

`currentBitDepthMode()` 固定返回 8-bit。`setDisplayFilter()` 仅触发重绘，不将 OCIO 参数注入着色器。

---

## 三、取长补短：双方优势对照

### Vulkan 分支的长处（值得保留与发展）

| 优势 | 说明 | OpenGL 路径对应的弱点 |
|:---|:---|:---|
| **Compute-first 笔刷** | dab 生成在 GPU 就地完成，零 CPU↔GPU 像素回传 | CPU 光栅化 → glTexSubImage2D 上传，带宽瓶颈 |
| **稀疏绑定虚拟纹理** | 131K² 画布按需分配，无前端瓦片调度开销 | `kis_texture_tile` 的 CPU 分块管理+动态上传 |
| **异步渲染线程** | 独立线程持有完整管线，UI 零阻塞 | 主线程持有 GL Context，`KisOpenGLSync` 锁 |
| **无锁输入队列** | SPSC Ring Buffer 极低延迟 | 输入经过多层 signal/slot 调度 |
| **Push Constants** | 64 字节每 dab，零分配 | GL Uniform 更新 |
| **UMA 零拷贝** | Apple Silicon 原生适配 | GL 无法直接利用 UMA |
| **极低侵入** | 1 个文件改动 | — |

### OpenGL 路径的长处（需要接口适配而非重建）

| 优势 | 说明 | Vulkan 分支当前的差距 |
|:---|:---|:---|
| **完整的更新协议** | KisUpdateInfo 脏矩形 → 瓦片差量 → GPU | `startUpdateCanvasProjection` 返回 null |
| **笔刷生态** | 200+ 预设、引擎插件、动态曲线、间距/抖动/防抖 | 仅 SDF 圆笔刷，无 KisPaintOp 框架连接 |
| **图层模型** | KisNode 树：组、调整、蒙版、不透明度、混合 | 扁平图层列表，8 种混合模式 |
| **撤销/保存** | KisUndoStore + KisStrokeStrategy 深度集成 | syncToCPU 是空壳 |
| **色彩管线** | OCIO、多位深、HDR Swapchain 探测 | 硬编码 8-bit RGBA |
| **Wrap-around** | 坐标偏移补偿 + 瓦片重复 | 变量已存但未传入着色器 |
| **通道筛选** | 实时通道可见性过滤 | TODO 状态 |

---

## 四、核心战略判断

### 问题本质

当前 Vulkan 分支建成了一套**优秀的 GPU 渲染引擎**，但它运行在 Krita 核心旁边，而不是内部。它的 GPU 计算架构（笔刷、图层合成、瓦片管理）是正确且高效的，但缺少与 Krita 核心系统（笔刷预设生态、图层树管理、撤销/保存）之间的**接口适配**。

需要强调的是：接下来的方向调整不是"退回 CPU 计算"，而是**在保持 GPU 原生计算的前提下，补齐与 Krita 核心之间的接口层**。

### 方向定义：API 兼容层 + GPU 原生计算

更准确的表述是：**绘画热路径保持 GPU 原生，同时增加与 Krita 核心系统的接口适配层**。

这不是在两条路线之间做选择，而是在已建成的 GPU 引擎之上**加一层薄壳**，使其能嵌入 Krita 的工具/图层/撤销生态。

---

## 五、数据流分析：什么跨越 CPU↔GPU 边界

这是整个方向判断的核心依据。以下逐场景分析绘画全流程中 CPU↔GPU 边界上实际传输的数据。

### 5.1 绘画热路径：零像素跨越

```
UI 线程 (CPU)                              GPU
  │                                          │
  │  ① 触控笔事件                            │
  │  (x, y, pressure, tilt)                  │
  │  ~32 bytes/point                         │
  │                                          │
  │  ② CPU 侧决策（微秒级）                  │
  │  - 间距判定：此刻需要几个 dab？           │
  │  - 动态曲线：pressure → radius/opacity   │
  │  - 笔刷预设参数查表                      │
  │  结果：一组 dab 参数（不是像素）          │
  │                                          │
  │──── Ring Buffer (64B/dab) ──────────────→│
  │     SPSC 无锁，HOST_COHERENT 零拷贝      │
  │                                          │  ③ GPU 计算（并行，不回传）
  │                                          │  - Compute Shader SDF 求值
  │                                          │  - Porter-Duff OVER 混合
  │                                          │  - 直写稀疏虚拟纹理
  │                                          │
  │                                          │  ④ GPU 显示（同帧）
  │                                          │  - 图形管线读稀疏纹理
  │                                          │  - Bicubic 采样 → Swapchain
  │                                          │
  │←─── framePresented 信号（无数据） ────────│
```

**在绘画过程中，CPU→GPU 只传递 dab 参数（64 字节/dab），不传递像素。GPU→CPU 不传递任何数据。这一点在方向调整后完全保持不变。**

CPU 侧增加的 `KisPaintOp` 接口适配只是在 ② 处多做一步参数转换（从 `KisPaintInformation` 提取参数 → 推入 Ring Buffer），开销是几次浮点运算，微秒级。

### 5.2 笔画结束：异步瓦片下载（非实时路径）

```
用户抬笔
  │
  ├─ finishStrokeCallback 触发
  │
  ├─ GPU 内部快照 (避免脏读写)
  │  • 提交 Barrier 确保上一笔计算完成
  │  • 拷贝脏瓦片: Image (Optimal) → Staging Buffer (Linear)
  │  • 下一笔即可立刻继续写入 Image，物理隔离无冲突
  │
  ├─ Transfer Queue 异步等待 & CPU 读取
  │  • 典型一次笔画修改 100~1000 个 64×64 瓦片 (100KB ~ 1MB)
  │  • Apple Silicon 等 UMA 架构直接读取 Staging Buffer (零拷贝)
  │  • 走专用 DMA 队列 + Timeline Semaphore
  │  • 与下一帧渲染流水线完全重叠，用户无感知
  │
  └─ 数据就绪后写入 KisPaintDevice → KisUndoStore 快照
```

这是唯一的 GPU→CPU 像素传输，发生在**笔画边界**而非绘画过程中。

### 5.3 CPU 侧操作：反向上传（低频）

```
用户执行滤镜 / 粘贴 / 撤销回放
  │
  ├─ Krita 核心更新 KisPaintDevice
  │
  ├─ startUpdateCanvasProjection(dirtyRect)
  │  → 构建 KisVulkanUpdateInfo（受影响的稀疏页列表）
  │
  └─ updateCanvasProjection(info)
     → Transfer Queue 上传脏瓦片到 GPU 稀疏页
```

这是 CPU→GPU 的像素传输，仅在 CPU 侧操作时发生（滤镜、变换、粘贴、撤销回放等），频率远低于绘画。

### 5.4 各场景的数据传输总结

| 场景 | 方向 | 传输内容 | 量级 | 频率 | 在实时路径上？ |
|:---|:---|:---|:---|:---|:---|
| 绘画中 | CPU→GPU | dab 参数 | 64 B/dab | 每 dab | 是，但无像素 |
| 笔画结束 | GPU→CPU | 脏瓦片 (经 Staging Buffer 快照) | 100KB~1MB | 每笔画 | **否**，异步隔离 |
| 滤镜/变换 | CPU→GPU | 受影响瓦片 | 视操作范围 | 每操作 | **否** |
| 撤销/重做 | CPU→GPU | 恢复的瓦片 | 视笔画范围 | 每撤销 | **否** |
| 保存/导出 | GPU→CPU | 全画布脏瓦片 | 视画布大小 | 每保存 | **否** |

**结论：所有像素级 CPU↔GPU 传输都在非实时路径上。绘画热路径的数据流结构与原始 GPU-first 设计完全一致。**

---

## 六、图层系统：GPU 合成不变，桥接仅在元数据层

### 保持不变的核心

原始设计的图层计算方向——所有像素数据驻留在 GPU 虚拟纹理，图层合成在 GPU Compute Shader 中执行——**完全保持不变**：

- 每个图层的像素数据 = GPU 稀疏纹理的一组页 → 不搬回 CPU
- 合成 = Compute Shader 从多个稀疏纹理读取 → 写入合成输出纹理 → 不搬回 CPU
- 显示 = 图形管线读合成输出纹理 → Swapchain → 不搬回 CPU

### 桥接增加的是什么

唯一增加的是**结构元数据的同步**——告诉 GPU 合成器"有几个图层、什么顺序、什么混合模式"：

```
KisNode 树 (CPU 侧)                    GPU 合成器
  │                                       │
  │  sigNodeAdded / Removed / Changed     │
  │  ↓                                    │
  │  元数据映射表更新：                    │
  │  {layerId, order, visible,            │
  │   opacity, blendMode}                 │
  │  ~几十字节 / 每次变更                  │
  │                                       │
  │──── 映射表同步 ──────────────────────→│
  │     纯元数据，无像素                   │  按新配置执行合成
  │                                       │  dispatch layer_composite.comp
```

这些是整数、布尔值、枚举——不是像素。等同于给 GPU 合成器传一份"配置表"。

### 不支持的节点类型的回退

对于当前 GPU 尚不支持的节点类型（调整图层、滤镜蒙版等），采用渐进回退策略：

1. CPU 侧计算该节点的输出（使用 Krita 现有逻辑）
2. 将结果作为一个普通 GPU 纹理上传
3. GPU 合成器把它当作一个普通图层参与合成

随着 Compute Shader 逐步覆盖更多滤镜类型，回退比例会持续降低。最终目标仍然是**尽可能所有节点在 GPU 求值**。

### 混合模式的补齐

当前 `layer_composite.comp` 仅实现 8 种混合模式（Normal, Multiply, Screen, Overlay, Darken, Lighten, ColorDodge, ColorBurn），而 Krita 有 70+ 种。这是需要逐步补齐的着色器工作，但它是纯 GPU 侧的工程量——与是否增加接口适配层无关。

---

## 七、笔刷系统：计算压力分布与接口适配的真实开销

### 计算任务在哪里

| 环节 | 工作量 | 执行者 | 性能特征 |
|:---|:---|:---|:---|
| 轨迹插值 + 间距计算 | 几次乘法/除法/点 | CPU | 冷，微秒级 |
| 动态曲线求值 | 查表 + 插值 | CPU | 冷，微秒级 |
| 笔刷预设参数查表 | 哈希表查找 | CPU | 冷，微秒级 |
| **Dab 像素生成 (SDF)** | 1000px 笔刷 ≈ 785K 像素/dab | **GPU** | **热，主要算力消耗** |
| **像素混合 (OVER)** | 每像素 read-modify-write | **GPU** | **热，带宽瓶颈** |
| 图层合成 | 全视口像素 | GPU | 中等，每帧一次 |
| 画布显示 + 采样 | 全视口像素 | GPU | 中等，每帧一次 |

**真正的性能敏感计算（dab 生成 + 像素混合）100% 在 GPU 上执行。接口适配层不改变这一点。**

### 接口适配层在热路径上的实际代码

```cpp
// KisVulkanPaintOp::paintAt() — CPU 侧唯一新增代码
void paintAt(const KisPaintInformation &info) {
    // 从 KisPaintInformation 提取参数（已有字段，不是新计算）
    float x = info.pos().x();
    float y = info.pos().y();
    float pressure = info.pressure();

    // 推入 Ring Buffer（和现有 PaintRouter::strokeTo 完全一样）
    m_paintRouter->strokeTo(x, y, pressure, ...);
}
```

这是全部 CPU 侧新增开销。没有像素分配、没有内存拷贝、没有 GPU 等待。

### 原始设计的核心不等式仍然成立

```
触控笔事件 (~32B)  →  CPU 决策 (~μs)  →  Ring Buffer (~64B)  →  GPU 并行计算 (~ms)  →  显示
        ↑                                                              ↑
   微量控制信号                                                   海量像素计算

CPU↔GPU 边界传输：仅控制信号，无像素。
```

---

## 八、Phase 7 细化实施路径

基于以上分析，Phase 7 的目标是**补齐接口适配层，将 GPU 原生引擎嵌入 Krita 生态**。

### Phase 7A：更新协议适配 — `KisVulkanUpdateInfo` ⭐ 最高优先级

**目标**：让 Vulkan 画布能感知 CPU 侧图像变更（滤镜/变换/粘贴/撤销回放）。

**做什么**：
1. 创建 `KisVulkanUpdateInfo`，类似 `KisOpenGLUpdateInfo`，但目标是稀疏纹理页而非 GL 纹理瓦片
2. `startUpdateCanvasProjection(rc)` 计算受影响的稀疏页列表，携带色彩空间转换信息
3. `updateCanvasProjection(info)` 将 CPU 侧 `KisPaintDevice` 瓦片数据通过 Transfer Queue 上传到对应稀疏页
4. 这使得所有 CPU 侧操作能正确反映在 Vulkan 画布上

**为什么先做这个**：这是 Vulkan 画布从"独立原型"变为"Krita 画布后端"的分水岭。没有这一步，后续所有功能（撤销、保存、图层变更）都无法工作。

**不影响什么**：绘画热路径不经过此协议。笔刷输入仍然通过 Ring Buffer 直达 GPU Compute Shader。

**成功标准**：在 CPU 侧执行一次滤镜操作后，Vulkan 画布能正确显示更新后的图像。

### ✅ Phase 7B：笔刷引擎适配 — `KisVulkanPaintOp`
**状态：已完成**

**目标**：让 Krita 笔刷预设能通过 GPU 执行，保留笔刷生态兼容性。

**实现方案**：
1. `KisVulkanPaintOpFactory` 使用包装模式（Wrapping Factory Pattern）替换注册表中的 `paintbrush` 工厂，对用户透明
2. `createOp()` 检查 GPU 兼容性（活跃的 Vulkan 路由 + 圆形自动笔刷尖端） → 兼容则返回 `KisVulkanPaintOp`，否则委托原始工厂返回 CPU `KisBrushOp`
3. `KisVulkanPaintOp::paintAt()` 从 `KisPaintInformation` 提取位置/压感/倾斜，调用 `KisVulkanPaintRouter::strokeTo()` 推入 Ring Buffer → GPU Compute Shader
4. CPU 侧保留：间距计算（`KisSpacingInformation`）、压感映射 — 微秒级纯算术
5. GPU 侧不变：dab 光栅化和像素混合由 `dab_round.comp` 在稀疏纹理上就地执行

**关键文件**：
- `libs/image_vulkan/KisVulkanPaintOp.h/cpp` — GPU 笔刷适配器
- `libs/image_vulkan/KisVulkanPaintOpFactory.h/cpp` — 包装工厂 + GPU 兼容性检查
- `libs/image_vulkan/KisVulkanPaintRouter.h/cpp` — 新增 `activeInstance()` 静态访问器
- `libs/ui/vulkan/KisVulkanCanvas.cpp` — 初始化时设置活跃实例 + 包装工厂

**热路径开销**：`paintAt()` 约 60 ns（结构体拷贝 + 原子递增），仅 32 字节/点跨越 CPU→GPU。

**成功标准**：使用标准"Basic-5 Size Opacity"预设绘制笔画，结果可见且与 OpenGL 路径视觉一致。

### Phase 7C：图层栈元数据适配

**目标**：让 `KisNode` 树变更驱动 GPU 合成。

**做什么**：
1. 监听 `KisImage::sigNodeChanged` / `sigNodeAdded` / `sigNodeRemoved` 信号
2. 维护 KisNode → GPU 图层的映射表（纯元数据：图层 ID、顺序、可见性、不透明度、混合模式）
3. `KisVulkanLayerCompositor` 从映射表读取配置，执行 GPU 合成
4. 不支持的节点类型标记为"CPU 回退"，CPU 合成结果作为 GPU 纹理参与后续合成
5. 起步最小集：普通绘制图层 + 组图层 + 不透明度 + 可见性

**跨越边界的数据**：仅元数据（整数、布尔值、枚举），图层像素数据始终驻留在 GPU 虚拟纹理中。

**成功标准**：创建 3 个图层，在不同图层绘制，调整可见性和不透明度，结果正确。

### Phase 7D：撤销/保存异步同步闭环

**目标**：让 GPU 绘制的结果可撤销、可保存。

**做什么**：
1. **笔画完成时**（非实时路径）：
   - `finishStrokeCallback` 触发
   - Transfer Queue 异步下载 GPU 脏瓦片 → 写入 `KisPaintDevice` 对应 `KisTileData`
   - 与下一帧渲染流水线重叠，用户无感知
   - 典型开销：100~1000 个 64×64 瓦片 = 100KB~1MB，毫秒级 DMA
2. **撤销时**：`KisUndoStore` 恢复 `KisPaintDevice` → 通过 7A 的更新协议上传回 GPU
3. **保存时**：调用 `flushAll()` 确保所有 GPU 数据已下载到 CPU 侧

**关键实现**：`syncToCPU` 的真正逻辑——下载 GPU 瓦片数据（Transfer Queue，已有基础设施）→ 写入 `KisPaintDevice` 对应瓦片（当前缺失，需实现 `KisTileData` 的直接写入或通过 `KisPainter::bitBlt`）。

**成功标准**：绘制 → 撤销 → 重做 → 保存 → 重新打开，结果一致。

### Phase 7 整体成功标准
* 自由绘制（圆形自动笔刷）可用、可撤销、可保存。
* 多图层（最小集合）可正确合成并随属性变更更新。
* CPU 侧操作（滤镜/变换/粘贴）结果能正确反映到 Vulkan 画布。
* 不满足能力（位深/节点类型/引擎类型）时可稳定回退 CPU 路径，不崩溃。
* 建议执行顺序：7A → 7B & 7C（可并行） → 7D。

---

## 九、后续展望

Phase 7 完成后，Vulkan 引擎将从"技术演示"蜕变为"可用的 GPU 加速后端"。之后：

- **Phase 8（色彩/位深）**：在 7A 建立的更新协议中传递色彩空间参数，着色器中注入 OCIO LUT，扩展稀疏纹理格式到 16F/32F
- **Phase 9（滤镜/非破坏）**：基于 7C 的图层适配，为支持的滤镜类型添加 Compute Shader 实现，其余回退 CPU

关键度量：每个阶段结束后，运行 OpenGL/Vulkan 对照测试套件，确保视觉结果在可接受容差内一致。

---

## 十、风险与缓解

| 风险 | 影响 | 缓解措施 |
|:---|:---|:---|
| 稀疏绑定硬件碎片化 | macOS MoltenVK 不支持真正的 sparse residency | 检测并回退到密集纹理 + 手动瓦片管理 |
| 笔画结束时 GPU→CPU 同步 | 瓦片下载阻塞 | 仅下载脏瓦片、专用 Transfer Queue 异步、与渲染流水线重叠 |
| 笔刷预设兼容性 | 大量引擎类型无法 GPU 化 | 明确的 CPU 回退路径，仅对支持的引擎走 GPU，渐进扩展 |
| 混合模式覆盖 | 70+ 种需逐步补齐着色器 | 按使用频率排序，优先补齐日常高频项 |
| 上游 Krita 代码演化 | rebase 冲突 | 保持侵入最小（当前仅 1 文件改动），定期 rebase |
