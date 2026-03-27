# 开发步骤蓝图 (Development Steps Roadmap)

整个新架构将分阶段推进，确保在每个阶段都能获得可运行、可测试、可回退的结果。
> **当前状态（以仓库现状为准）**：Phase 1-7 全部完成（7A 更新协议、7B 笔刷适配、7C 图层栈、7D 撤销/保存闭环）；接下来推进 Phase 8-9 补齐位深/色彩/混合/非破坏等正确性与主要功能。

## 里程碑分层（建议）
为避免“底层很强但无法用于日常创作”，路线图按三层推进：
1. **后端可跑（Phase 1-6）**：Vulkan 设备/显存/稀疏画布/线程/显示与装饰就绪。
2. **核心可用（Phase 7）**：打通 Krita 的真实输入/笔刷/图层栈/撤销保存最小闭环。
3. **结果正确 + 主要功能（Phase 8-9）**：位深与色彩管理对齐、混合模式覆盖、滤镜与非破坏节点逐步接入。

## ✅ Phase 1: 搭建基于 Vulkan 的底层显存管理与虚拟纹理 (Sparse Binding) 框架
**状态：已完成**
* 引入 Vulkan SDK 和 MoltenVK 依赖。
* 开发 `VulkanDeviceManager`，处理设备选择、队列族提取及基本扩展启用（特别是 Sparse Binding 相关）。
* 集成 Vulkan Memory Allocator (VMA)，预分配大块显存池（Memory Pooling），避免运行时 `vkAllocateMemory`。
* 在 `libs/ui/canvas` 创建 `KisVulkanCanvas`，建立基本的三重缓冲 Swapchain 交换机制，替换原有的 OpenGL Canvas 显示逻辑（仅做纯色/简单纹理填充验证）。

## ✅ Phase 2: 重构 KisTileManager，实现 GPU 驻留画布与 L1/L2/L3 分级缓存机制
**状态：已完成**
* 建立平行模块 `libs/image_vulkan`。
* 开发 `KisVulkanTileData`，利用 `VK_KHR_sparse_binding` 和 `VK_KHR_sparse_residency`，创建一个逻辑上巨大的虚拟 2D 图像画布。
* 实现 L1 (VRAM) 与 L2 (RAM) 的缓存置换逻辑：
  * 创建专用的 Vulkan Transfer Queue。
  * 利用 Timeline Semaphores (`VK_KHR_timeline_semaphore`) 编写异步预取队列，在视口平移（Pan）时提前加载 Tile。
* 对 Apple Silicon / PC 核显开启 UMA 内存类型分配（`HOST_VISIBLE | HOST_COHERENT | DEVICE_LOCAL`），实现零拷贝（Zero-copy）。

## ✅ Phase 3: 开发 Vulkan Compute Shader 驱动的核心笔刷引擎，对标 llama.cpp 的高效 GPU 调度
**状态：已完成**
* 编写第一批 `.comp` (Compute Shader) 代码，替代 `KisPainter` 的 CPU 像素生成与混合。
* 将 UI 线程捕获的触控笔输入流（坐标、压感、倾斜）映射到 GPU 的 Ring Buffer（环形缓冲区）。
* 借助 `Push Constants` 实现极低延迟的高频笔刷参数更新。
* 使用 Compute Shader 读取 Ring Buffer 数据，并行生成笔尖印迹（Dab Generation）并写入 L1 VRAM 绑定的物理页面。

## ✅ Phase 4: 实现 UMA 架构的零拷贝优化与异步多重缓冲 (Multi-buffering) 渲染管线
**状态：已完成**
* 彻底分离 UI 输入采集线程和 GPU Compute 提交线程。
* 完善三重缓冲机制：
  * **Buffer A (Front)**: 当前显示的 Swapchain 图像。
  * **Buffer B (Compute)**: 正在执行 Compute Shader 混合的后台缓冲。
  * **Buffer C (Input)**: 正在接收 UI 无锁写入笔刷数据的输入缓冲。
* 探索 Vulkan Subgroup 操作（如 `subgroupAdd`），优化超大笔刷像素混合的内存带宽瓶颈。

## ✅ Phase 5: 剥离并替换现有的 OpenGL Canvas，完成核心图层与笔刷显示链路的打通
**状态：已完成**
* 在 Vulkan 画布模式下初始化笔刷引擎、图层合成器与同步路由（CPU↔GPU 的最小框架）。
* 提供基础的图层合成计算路径（用于验证合成调度与资源绑定模型）。
* 增加性能基准与调试信息，便于衡量 VRAM 驻留与提交开销。

> 说明：Phase 5 的“打通”主要指 Vulkan 子系统内部链路可运行；与 Krita 真实工具输入链路、真实图层栈/投影系统的接线仍属于后续阶段（见 Phase 7）。

## ✅ Phase 6: 构建完整的图形显示管线与前端交互层 (Graphics Pipeline & UI)
**状态：已完成 — 图形管线、异步渲染、画布装饰全部就绪**

### 6.1 ✅ 核心图形管线 (已完成)
* 废弃临时 `vkCmdBlitImage`，实现真正的 Vulkan 图形管线 (Graphics Pipeline)。
* 新增 `KisVulkanGraphicsPipeline` 类，管理画布显示和笔刷轮廓两套图形管线。
* 新增 `canvas_display.vert` / `canvas_display.frag` 着色器：
  * 支持相机变换 (Camera Transform)：从 `KisCoordinatesConverter` 获取 widgetToImage 矩阵，通过 Push Constants 传入 Shader。
  * 实现 Bicubic (Catmull-Rom) 高质量图像采样，替代最近邻采样。
  * 内置棋盘格透明背景渲染。
  * 高倍缩放时自动切换为最近邻采样以保持像素艺术清晰度。
* 新增 `brush_outline.vert` / `brush_outline.frag` 着色器，为原生 Vulkan 笔刷轮廓渲染提供基础。
* `renderFrame()` 完全重构：Compute Shader (笔刷) → Barrier → Render Pass (图形管线显示 + 叠加层)。

### 6.2 ✅ 笔刷轮廓渲染 (已完成)
* `KisTool::paintToolOutline()` 新增 `KisVulkanCanvas` 分支（`dynamic_cast` 路由）。
* `KisVulkanCanvas::paintToolOutline()` 实现完整的轮廓顶点生成：
  * 粗轮廓 (thickness > 1)：Miter-Joint 三角列表，含接头限制和法线计算。
  * 细轮廓 (thickness == 1)：直接线条带。
* `paintEvent()` 在 `renderFrame()` 前通过 `drawDecorations()` 收集轮廓数据。
* `renderFrame()` 在 Render Pass 中使用 `BrushOutlineFill/Line` 管线绘制轮廓。

### 6.3 ✅ 异步渲染线程激活 (已完成)
* 正式启动 `KisVulkanRenderThread`，将完整渲染管线（acquire → compute → graphics → present）移至独立线程。
* 新增 `SwapchainSnapshot` POD 结构体，避免 libs/image_vulkan 对 libs/ui 的头文件依赖。
* 新增 `RenderState` 结构体，UI 线程通过 mutex 保护的拷贝机制向渲染线程传递逐帧数据（相机矩阵、轮廓顶点、画布状态）。
* 实现 `pauseRendering()` / `resumeRendering()` 暂停/恢复机制，用于窗口 Resize 时安全重建 Swapchain。
* `renderFrame()` 重构为轻量级状态更新包装：收集轮廓数据 → 构建 RenderState → 信号唤醒渲染线程。
* 通过 `framePresented` 信号驱动 `update()` 形成持续渲染循环，彻底消除 UI 线程的 GPU 阻塞。

### 6.4 ✅ 画布装饰渲染 (已完成)
* 在 `canvas_display.frag` 片段着色器中实现像素网格 (Pixel Grid) 渲染：
  * Push Constants 扩展至 112 字节，新增 `pixelGridColor`、`pixelGridThreshold`、`pixelGridEnabled` 参数。
  * 使用 `fract()` 在图像坐标上检测像素边界，零几何开销，比 OpenGL 的 `GL_LINES` 方案更高效。
  * 支持用户自定义颜色和缩放阈值（从 `KisConfig` 读取）。
* 新增 QPainter 装饰叠加层 (Decoration Overlay) 管线：
  * `decoration_overlay.vert` / `decoration_overlay.frag` 着色器：全屏三角形 + 纹理采样 + Alpha 混合。
  * `KisVulkanGraphicsPipeline` 新增叠加层纹理管理：`resizeDecorationOverlay()`、`uploadDecorationOverlay()`、`recordDecorationOverlay()`。
  * 使用 VMA 分配 GPU 端 RGBA8 图像和 CPU 端暂存缓冲区（持久映射），通过 `vkCmdCopyBufferToImage` 上传。
* `paintEvent()` 重构：将装饰绘制目标从 1x1 虚拟 QImage 改为匹配 widget 尺寸的全尺寸 QImage。
* `RenderState` 新增 `decorationPixels` / `decorationWidth` / `decorationHeight` / `hasDecoration` 字段。
* `processFrame()` 在 Render Pass 前上传叠加层纹理，在 Render Pass 内（画布 + 轮廓之后）绘制装饰叠加层。
* 兼容所有现有 QPainter 装饰类型：网格、参考线、选区蚂蚁线、绘画助手、画布镜像轴等。

## ✅ Phase 7: Krita 核心链路接线 (Core Wiring & Minimal Usability)
**状态：已完成**
**核心策略：API 兼容层 + GPU 原生计算** — 绘画热路径保持 GPU 原生（Ring Buffer → Compute Shader → 稀疏纹理，零像素跨越 CPU↔GPU），同时增加与 Krita 核心系统的接口适配层。

> 详细分析与数据流图见 [06_branch_vs_design_analysis.md](06_branch_vs_design_analysis.md)。
>
> **方向澄清**：Phase 7 不是”退回 CPU 计算”。绘画过程中 CPU→GPU 只传递 dab 参数（64 字节），不传递像素。所有像素级计算（dab 生成、混合、图层合成）保持 GPU 执行。CPU↔GPU 像素传输仅发生在非实时路径（笔画结束异步下载、CPU 侧操作上传、保存导出等）。
>
> **关键断层已全部补齐**：~~`startUpdateCanvasProjection` 返回 null（7A）~~、~~`syncToCPU` 骨架代码（7D：现已写入 `KisPaintDevice::writeBytes()`）~~、~~笔刷引擎零连接（7B）~~、~~图层栈零连接（7C）~~。Phase 7 核心链路完整闭环。

### ✅ Phase 7A: 更新协议适配 — `KisVulkanUpdateInfo`
**状态：已完成**
**前置依赖**：无（Phase 6 已完成）
**目标**：让 Vulkan 画布能感知 CPU 侧图像变更（滤镜/变换/粘贴/撤销回放）。
* 创建 `KisVulkanUpdateInfo`（类似 `KisOpenGLUpdateInfo`），携带受影响瓦片列表与像素数据。
* 创建 `KisVulkanTileUpdateEntry`，每个条目对应一个 64×64 GPU 瓦片的像素数据（通过 `KisPaintDevice::readBytes()` 读取）。
* 实现 `startUpdateCanvasProjection(rc)`：计算 rc 覆盖的瓦片网格，从 CPU 投影读取像素，构建 `KisVulkanUpdateInfo`。
* 实现 `updateCanvasProjection(info)`：将瓦片像素数据通过 `uploadTileData()` + Transfer Queue 上传到 GPU 稀疏纹理页。
* 完善 `syncToGPU(rect, projection)` 方法：从指定 `KisPaintDevice` 读取像素并上传到 GPU 瓦片。
* 支持全瓦片直接上传和部分瓦片读-改-写两种路径。
* 支持更新压缩（`tryMergeWith`）——合并脏矩形与瓦片列表。
* 修复了 Phase 5 中 `startUpdateCanvasProjection` 返回 null 导致 `KisCanvasUpdatesCompressor::putUpdateInfo()` 崩溃的问题。

**不影响绘画热路径**：笔刷输入仍然通过 Ring Buffer 直达 GPU Compute Shader，不经过此协议。此协议仅服务于 CPU 侧操作→GPU 的单向同步。

**成功标准**：CPU 侧执行滤镜/变换后，Vulkan 画布正确显示更新结果。

### ✅ Phase 7B: 笔刷引擎适配 — `KisVulkanPaintOp`
**状态：已完成**
**前置依赖**：7A（需要更新协议来显示撤销回放结果）
**目标**：让 Krita 笔刷预设能通过 GPU 执行，保留笔刷生态兼容性。
* 创建 `KisVulkanPaintOp`（实现 `KisPaintOp` 接口），在 `paintAt()`/`paintLine()` 中将 dab 参数转发给 Ring Buffer → GPU 引擎。
* **CPU 侧保留**（微秒级纯算术，非瓶颈）：间距计算、动态曲线、压感映射。
* **GPU 侧不变**：dab 光栅化和像素混合仍由 Compute Shader 在稀疏纹理上就地执行。
* 初始版本仅支持圆形自动笔刷（`dab_round.comp`），其他引擎自动回退 CPU 路径。
* 在 `KisPaintOpRegistry` 中注册 Vulkan 加速标记，由引擎自动选择。

**热路径新增开销**：仅 `KisPaintInformation` → Ring Buffer 的参数提取（几次浮点运算），无像素分配/拷贝/GPU 等待。

**成功标准**：标准”Basic-5 Size Opacity”预设绘制笔画，结果可见且与 OpenGL 路径视觉一致。

### ✅ Phase 7C: 图层栈元数据适配
**状态：已完成**
**前置依赖**：7A
**目标**：让 `KisNode` 树变更驱动 GPU 合成。图层像素数据始终驻留在 GPU 虚拟纹理中，合成始终在 GPU 执行。
* `KisVulkanNodeSync`（新类）：监听 `KisImage::sigNodeChanged` / `sigLayersChangedAsync` 和 `KisNodeManager::sigNodeActivated` 信号。
* 遍历 KisNode 树，提取可见 `KisPaintLayer` 的元数据（不透明度、可见性、混合模式、堆叠顺序）。
* 活跃图层 → 使用稀疏纹理（零开销），其他可见图层 → 每层独立 VkImage（从 CPU projection 上传）。
* `KisVulkanLayerCompositor` 从映射表读取配置，执行 GPU Compute 合成（8 种混合模式）。
* 渲染线程 `processFrame()` 插入 Phase A2 合成阶段（笔刷 dab 后、图形管线前），仅在 >1 可见图层时激活。
* 不支持的节点类型（调整图层、滤镜蒙版等）：静默跳过，待 Phase 9。

**实现文件**：
* `libs/image_vulkan/KisVulkanNodeSync.h/cpp` — 信号监听 + KisNode 树遍历 + VkImage 管理
* `libs/image_vulkan/KisVulkanRenderThread.h/cpp` — 新增 `setLayerCompositor()` + Phase A2 合成调度
* `libs/ui/vulkan/KisVulkanCanvas.cpp` — 创建 NodeSync、连接信号、传递合成器至渲染线程

**跨越边界的数据**：仅元数据（整数/布尔值/枚举，几十字节/次变更）。像素上传仅在图层切换时发生（非实时路径）。

**成功标准**：创建 3 个图层，在不同图层绘制，调整可见性和不透明度，结果正确。

### ✅ Phase 7D: 撤销/保存异步同步闭环
**状态：已完成**
**前置依赖**：7A + 7B
**目标**：让 GPU 绘制的结果可撤销、可保存。
* **笔画完成时**（非实时路径）：
  - `~KisVulkanPaintOp` 调用 `strokeEnd()` → `flushAndPause()` 确保渲染线程完成所有 GPU 计算
  - `syncToCPU(strokeBounds)` 下载脏瓦片：`downloadTileData()` 通过 `vkCmdCopyImageToBuffer` 将瓦片从 Sparse Image 拷贝到 Staging Buffer，`submitAndWait()` 阻塞等待 DMA 完成
  - 下载的像素通过 `KisPaintDevice::writeBytes()` 写入 CPU 侧画板设备
  - `finishStrokeCallback()` 中 `KisTransaction::endAndTake()` → `commit()` memento → 撤销系统正确捕获 diff
  - **UMA 优化**：Apple Silicon 上 Staging Buffer 位于 `HOST_VISIBLE | HOST_COHERENT` 内存，CPU 直接读取（Zero-copy）
* **撤销时**：`KisTransactionData::undo()` → `rollback(memento)` → `KisPaintDevice` 恢复 → `sigNodeChanged` → Phase 7A 更新协议自动上传回 GPU。
* **保存时**：`flushAll()` 暂停渲染线程 → 下载所有已分配瓦片到 `KisPaintDevice` → 恢复渲染。
* **渲染线程同步**：新增 `flushAndPause()` 方法，先 `notifyNewInput()` + `requestRepaint()` 确保最后的 dab 被处理，再暂停等待帧完成（通过 in-flight fence 保证）。

**实现文件**：
* `libs/image_vulkan/KisVulkanPaintRouter.h/cpp` — `setPaintDevice()`、`syncToCPU()` 写入 `writeBytes()`、`strokeEnd()` 暂停+同步+恢复、`flushAll()` 全量下载
* `libs/image_vulkan/KisVulkanRenderThread.h/cpp` — 新增 `flushAndPause()` 方法
* `libs/image_vulkan/KisVulkanPaintOp.cpp` — 构造函数传递 `painter()->device()` 到路由器

**成功标准**：绘制 → 撤销 → 重做 → 保存 → 重新打开，结果一致。

### Phase 7 整体成功标准
* 自由绘制（圆形自动笔刷）可用、可撤销、可保存。
* 多图层（最小集合）可正确合成并随属性变更更新。
* CPU 侧操作（滤镜/变换/粘贴）结果能正确反映到 Vulkan 画布。
* 不满足能力（位深/节点类型/引擎类型）时可稳定回退 CPU 路径，不崩溃。
* 建议执行顺序：7A → 7B & 7C（可并行） → 7D。

## 📅 Phase 8: 颜色/位深/显示正确性 (Color, Bit Depth & Display Correctness)
**状态：计划中**
* **位深与格式**：从 8-bit 路径扩展到 Krita 常用高位深显示与处理路径（含 HDR Swapchain 的能力探测与降级策略）。
* **色彩管理**：对接显示滤镜与 OCIO，确保显示与现有路径一致（LUT、色彩空间转换、曝光等）。
* **混合与通道**：扩展混合模式覆盖，并支持通道可见性筛选等核心调试/创作能力。

### Phase 8 成功标准
* 同一文档在 OpenGL 与 Vulkan 下视觉结果可对照一致（定义一组基准用例与容差）。
* HDR/高位深能力可用或可降级，且行为可预测。

## 📅 Phase 9: 滤镜与非破坏节点最小闭环 (Filters & Non-destructive Nodes)
**状态：计划中**
* **选择最小集**：先支持 1-2 类最常用非破坏节点（如调整图层/滤镜蒙版的最小功能集），建立 GPU 求值与缓存策略。
* **扩展滤镜框架**：逐步覆盖滤镜（xxxFilter）、生成器与变换类节点的执行与回退。
* **性能与稳定性**：建立跨节点的缓存复用、tile 驻留策略与一致性验证流程。

### Phase 9 成功标准
* 非破坏编辑在 Vulkan 模式下可用且结果可对照一致。
* 常用滤镜可在 Vulkan 下执行或可回退，且不会破坏撤销/保存语义。
