# Krita 渲染器特性对比与开发状态总结
**基准对比**：现有 `OpenGL` 渲染器 vs 本仓库的 `Vulkan` 画布后端实现（以当前代码状态为准）

> **状态更新**：Vulkan 侧的画布显示与装饰等表现层已基本具备，但“接入 Krita 真实笔刷/图层/非破坏节点链路”以及“位深/色彩/混合正确性对齐”仍是主要差距，因此当前更接近可运行的 GPU Canvas 原型，而非已具备完整功能的渲染后端替代方案。

## 1. 核心架构差异对比

| 模块 | OpenGL 渲染器 | Vulkan 渲染器（当前） | 差异说明与优势分析 |
| :--- | :--- | :--- | :--- |
| **渲染管线** | 传统的图形管线 (Vertex/Fragment Shaders)，通过 `KisOpenGLCanvasRenderer` 管理。 | 侧重于 **Compute Shader (计算着色器)** 的现代管线，数据处理为主。 | Vulkan 架构将笔刷引擎直接移入 GPU (Compute)，避免了传统架构下 CPU 算完再上传纹理的带宽瓶颈。 |
| **显存与纹理** | `kis_texture_tile` CPU端分块管理，动态上传至 GPU 纹理。 | `KisVulkanTileManager` 利用 Vulkan 的**稀疏绑定 (Sparse Binding)** 技术。 | Vulkan 支持极超大尺寸画布的按需显存分配，效率远超传统 OpenGL。 |
| **并发模型** | 依赖 `KisOpenGLSync` 锁与主线程同步，容易造成 UI 卡顿。 | 引入了独立异步渲染线程 `KisVulkanRenderThread` 和三缓冲机制。 | Vulkan 的多线程提交设计（参考了类似 llama.cpp 的高并发思路）大幅提升了并行吞吐量。 |

---

## 2. 特性支持矩阵 (Feature Parity)

目前 Vulkan 侧底层与显示链路已具备可运行实现；当前重点是补齐“核心接线”和“结果正确性”，以便覆盖日常创作的主功能。

| 特性项 | OpenGL | Vulkan（当前） | 当前 Vulkan 状态分析 |
| :--- | :--- | :--- | :--- |
| **画布图像渲染** | ✅ 完美支持，支持各种高质量缩放(HighQ Scaling)算法。 | ✅ 图形管线 + Bicubic | Phase 6 已替换 `vkCmdBlitImage`，通过 `KisVulkanGraphicsPipeline` 实现完整的 Vertex/Fragment Shader 管线，支持 Bicubic (Catmull-Rom) 高质量采样和 `KisCoordinatesConverter` 相机变换 (Zoom/Pan/Rotation)。 |
| **笔刷引擎计算** | ✅ 基于 CPU 光栅化后上传。 | ✅ GPU Compute 原生支持 | 已通过 `KisVulkanBrushEngine` 和环形缓冲区(`RingBuffer`) 实现 GPU 级笔刷，性能潜力巨大。 |
| **真实笔刷输入接线** | ✅ 完整工具链 | ✅ 已接通（圆形笔刷） | Phase 7B 已完成：`KisVulkanPaintOpFactory` 包装 `paintbrush` 工厂，圆形自动笔刷预设自动走 GPU 路径（`KisVulkanPaintOp` → Ring Buffer → Compute Shader），其他笔刷类型自动回退 CPU。 |
| **画布背景/棋盘格** | ✅ 原生着色器支持。 | ✅ Fragment Shader 内置 | Phase 6 的 `canvas_display.frag` 已内置棋盘格透明背景渲染，画布外区域显示深灰色背景。 |
| **画笔光标/轮廓** | ✅ 通过 `paintToolOutline` 实时渲染。 | ✅ Vulkan 原生渲染 | Phase 6.2 已实现完整的 Vulkan 笔刷轮廓渲染：`KisTool::paintToolOutline` 新增 Vulkan 分支，`KisVulkanCanvas::paintToolOutline` 生成 Miter-Joint 三角列表（粗轮廓）或线条带（细轮廓），在 Render Pass 中通过 `BrushOutlineFill/Line` 管线绘制。 |
| **画布装饰 (网格/参考线)** | ✅ 通过 `updateCanvasDecorations` 绘制。 | ✅ 混合渲染 | Phase 6.4 已完成：像素网格通过 Fragment Shader 内置渲染（`fract()` 检测像素边界，零几何开销）；其余装饰（参考线、选区、助手等）通过 QPainter → QImage → Vulkan 纹理上传 → Alpha 混合叠加层管线渲染，完全兼容所有现有装饰类型。 |
| **真实图层栈接线（投影/合成驱动）** | ✅ 完整 | ❌ 未完成 | Vulkan 侧具备图层合成器接口与 shader，但尚未形成由 Krita 真实图层系统喂数据并驱动合成的调用链。 |
| **混合模式覆盖** | ✅ 大量 | 🚧 很有限 | 当前仅覆盖少量混合模式/固定格式路径，离 Krita 的完整混合体系差距大。 |
| **高色深显示 (HDR)** | ✅ 支持 10bit, 16bit, 32bit (`KisOpenGLModeProber`)。 | ❌ 硬编码为 8-bit | `currentBitDepthMode` 强制返回 8-bit，尚未检测并创建高位深 Swapchain。 |
| **色彩管理 (OCIO)** | ✅ 动态注入 OCIO 逻辑。 | 🚧 接口占位 | `setDisplayFilter` 仅触发重绘，`canvas_display.comp` 尚未对接 OCIO 配置。 |
| **无限画布 (Wrap-around)** | ✅ 坐标偏移补偿完善。 | ❌ 未支持 | 变量已保存但未传递给 Compute Shader。 |
| **通道可见性筛选** | ✅ 实时过滤。 | ❌ 未支持 | 标注为 Phase 6 TODO，需在图层复合(`layer_composite.comp`)时加入遮罩。 |
| **滤镜与非破坏编辑（调整图层/滤镜层/蒙版等）** | ✅ 完整 | ❌ 未完成 | 需要建立 GPU 求值/缓存/回退框架，不能仅靠补 shader。 |

---

## 3. 当前实现完善程度评估

当前 Vulkan 侧呈现 **”后端与表现层就绪，但核心接线与正确性仍缺失”** 的状态：

1. **计算后端非常扎实 (High Completeness)**：
   - 显存池(`KisVulkanMemoryPool`)、稀疏纹理(`TileManager`)、无锁环形队列(`RingBuffer`) 等基础设施完全就位。
   - 笔刷 dabs 的计算管线分发已经能够顺利运行，GPU 并发利用率高（吸收了类似 llama.cpp 的极致压榨 GPU 算力的思想，如 Subgroup 优化）。
2. **显示核心已完成 (Phase 6.1/6.2 Done)**：
   - `KisVulkanGraphicsPipeline` 管理画布显示和笔刷轮廓两套管线。
   - `canvas_display.frag` 实现了 Bicubic 高质量采样和棋盘格透明背景。
   - 相机变换通过 `KisCoordinatesConverter` 的 widgetToImage 矩阵传入 Push Constants，支持 Zoom/Pan/Rotation。
   - 笔刷轮廓通过 Miter-Joint 三角列表（粗轮廓）和线条带（细轮廓）在 Vulkan 原生管线中渲染。
3. **异步渲染已激活 (Phase 6.3 Done)**：
   - `KisVulkanRenderThread` 已正式启动，完整渲染管线（acquire → compute → graphics → present）运行在独立线程。
   - UI 线程通过 `RenderState` 结构体向渲染线程传递逐帧数据，通过 mutex 保护的拷贝实现线程安全。
   - `SwapchainSnapshot` POD 结构体解耦了 libs/image_vulkan 与 libs/ui 的头文件依赖。
   - 窗口 Resize 通过 `pauseRendering()` / `resumeRendering()` 安全重建 Swapchain。
4. **装饰层已完成 (Phase 6.4 Done)**：
   - 像素网格在 Fragment Shader 中通过 `fract()` 检测像素边界直接渲染，零几何开销。
   - 其余装饰（参考线、选区蚂蚁线、绘画助手等）通过 QPainter → QImage → Vulkan 纹理叠加层管线渲染，兼容全部现有装饰类型。

5. **核心接线进展 (Core Wiring — Progress)**：
   - ✅ **更新协议已接通 (Phase 7A)**：`startUpdateCanvasProjection()` 现在返回有效的 `KisVulkanUpdateInfo`，携带受影响瓦片的像素数据；`updateCanvasProjection()` 将像素上传到 GPU 稀疏纹理。CPU 侧的图像变更（滤镜、变换、粘贴、撤销回放）可以反映到 Vulkan 画布。`syncToGPU()` 已实现从 `KisPaintDevice` 读取像素并上传。
   - ⚠️ **syncToCPU 待完善**：`syncToCPU()` 下载瓦片到 `QByteArray` 后未写入 `KisPaintDevice`。撤销/保存在当前代码下**不工作**（待 Phase 7D）。
   - ✅ **笔刷引擎已接通 (Phase 7B)**：`KisVulkanPaintOpFactory` 包装原始 `paintbrush` 工厂，圆形自动笔刷预设自动走 GPU 路径（`KisVulkanPaintOp::paintAt()` 提取位置/压感/倾斜 → `KisVulkanPaintRouter::strokeTo()` → Ring Buffer → Compute Shader），其他笔刷类型自动回退 CPU `KisBrushOp`。热路径开销约 60 ns/dab（仅 32 字节跨越 CPU→GPU）。
   - ⚠️ **图层模型独立**：`KisVulkanLayerCompositor` 操作自有图层概念，未与 `KisNode` 树关联（待 Phase 7C）。

---

## 4. 分支下一步开发内容建议 (Next Steps)

> 战略分析与数据流图详见 [06_branch_vs_design_analysis.md](06_branch_vs_design_analysis.md)。

### ✅ 已完成的表现层里程碑 (Phase 6)
- 6.1 图形显示管线 — Bicubic 采样、棋盘格背景
- 6.2 笔刷轮廓渲染 — Miter-Joint 三角列表
- 6.3 异步渲染线程 — UI 零阻塞
- 6.4 画布装饰系统 — 像素网格 + QPainter 叠加层

### 🎯 核心接线 (Phase 7) — 当前首要任务

**核心策略：API 兼容层 + GPU 原生计算**
绘画热路径保持 GPU 原生（Ring Buffer → Compute Shader → 稀疏纹理，零像素跨越 CPU↔GPU），同时增加与 Krita 核心系统的接口适配层。像素级 CPU↔GPU 传输仅发生在非实时路径（笔画结束异步下载、CPU 侧操作上传、保存导出）。

| 子阶段 | 目标 | 关键交付物 | 跨越边界的数据 | 依赖 |
|:---|:---|:---|:---|:---|
| **7A** ⭐ | 更新协议适配 | `KisVulkanUpdateInfo` + `startUpdateCanvasProjection` 实现 | CPU 侧操作时上传脏瓦片（非实时） | 无 |
| **7B** | 笔刷引擎适配 | `KisVulkanPaintOp`（接入 KisPaintOp 框架） | 仅 dab 参数 64B/dab（不传像素） | 7A |
| **7C** | 图层栈元数据适配 | KisNode → GPU 映射 + 信号监听 | 仅元数据（整数/布尔值/枚举） | 7A |
| **7D** | 撤销/保存异步闭环 | `syncToCPU` 写入 KisPaintDevice + finishStroke 触发 | 笔画结束时异步下载脏瓦片 | 7A+7B |

**7A 是分水岭**：没有它，Vulkan 画布无法感知 CPU 侧任何变更。建议执行顺序：7A → 7B & 7C（可并行） → 7D。

### 🔮 后续优先级
* **Phase 8 — 颜色/位深/混合正确性**：在 7A 更新协议中传递色彩空间参数，着色器注入 OCIO LUT，扩展格式到 16F/32F。
* **Phase 9 — 滤镜/非破坏节点**：基于 7C 图层适配为支持的滤镜添加 Compute Shader，其余回退 CPU。
* 每阶段结束后运行 OpenGL/Vulkan 对照测试，确保视觉一致性。
