# 难点与重点分析 (Challenges & Key Points)

> **状态更新**：Vulkan 侧的基础设施与显示管线已可运行，但“接入 Krita 真实核心链路”和“结果正确性对齐（位深/色彩/混合/非破坏）”已成为主难点。

## 重点 (Key Points)

1. **Vulkan Compute Shader 的笔刷引擎**
   传统的 `KisPainter` 高度依赖 CPU。将其转换为 Compute Shader (`.comp`) 是重中之重。需要设计一套能够在 GPU 上高效并行执行的印迹生成 (Dab Generation) 和混合 (Blending) 算法。

2. **稀疏绑定 (Sparse Binding) 的显存管理**
   利用 `VK_KHR_sparse_binding` 和 `VK_KHR_sparse_residency` 管理无尽画布。重点在于维护一张逻辑上的大纹理（Virtual Texture Page Table），并根据视口和笔刷位置，动态进行物理显存的 Bind 和 Unbind。

3. **无锁同步机制 (Lock-free Synchronization)**
   UI 线程（捕获压感笔输入）与 Vulkan 渲染队列（执行 Compute 和 Present）必须彻底解耦。重点是利用 Vulkan Timeline Semaphores 和 Ring Buffers 实现高效的多重缓冲（Double/Triple Buffering）。

4. **UMA 架构专属优化路径**
   在 Apple Silicon (通过 MoltenVK) 或 PC 核显上，准确识别 `HOST_VISIBLE | DEVICE_LOCAL` 内存类型，实现真正的零拷贝数据交互。

5. **核心接线与一致性（Undo/Save/Projection）**
   将 Vulkan 管线真正接入 Krita 现有的输入/工具/笔刷系统、图层/投影系统，以及撤销/保存/导出等关键流程。
   重点不在“能跑”，而在于数据一致性与可回退策略：CPU 与 GPU 的 tile 状态、脏矩形、同步时机必须可验证。

6. **视觉正确性（位深/色彩管理/混合模式）**
   Krita 的核心价值包含多位深与颜色空间支持、显示滤镜/OCIO、以及大量混合模式与通道控制。
   Vulkan 实现必须在这些维度与现有路径对齐，否则会出现肉眼可见偏差并阻塞落地。

## 难点 (Challenges)

1. **与现有 Krita 架构的深度解耦**
   Krita 的 `KisImage`、`KisLayer` 和 `KisTileManager` 是深度耦合的。最大的难点在于如何“不动原有 CPU 逻辑”的前提下，剥离出一个纯 GPU 的平行管线（例如建立 `libs/image_vulkan` 模块），并保证基础数据结构的兼容性。

2. **稀疏绑定的硬件碎片化与兼容性**
   虽然现代 GPU 都支持 Sparse Binding，但在不同厂商（NVIDIA/AMD/Intel）以及 MoltenVK（Metal 的 Vulkan 封装）上，稀疏纹理的 Page Size（通常是 64KB）和具体行为可能存在差异。处理对齐和兼容性 fallback 将非常棘手。

3. **笔刷插值与轨迹平滑的 GPU 化**
   Krita 现有的贝塞尔曲线插值、防抖（Stabilizer）算法都在 CPU 执行。如果仅仅把离散的点传给 GPU，高分辨率下可能会出现笔触断层。需要将轨迹插值算法部分迁移到 GPU，或者在 CPU 端极速生成密集点并写入 Ring Buffer。

4. **显存溢出 (OOM) 兜底策略**
   尽管有 L1/L2/L3 缓存机制，但在极端情况（成百上千个图层）下，VRAM 的换入换出可能引发性能骤降（Thrashing）。设计一个低延迟的后台异步驱逐/加载队列（Transfer Queue）是一个巨大的工程挑战。

5. **Shader 构建与分发的工程可靠性**
   Vulkan 路线高度依赖 `.spv` 产物。需要保证开发机/CI/打包产物中 shader 编译与安装路径稳定，否则会出现“能编译但运行缺 shader”“部分功能 silent fallback”的情况，影响排障效率与用户体验。

6. **跨平台碎片化（Sparse/Queue/Format/Sync）**
   稀疏绑定、队列族能力、可用格式（HDR/高位深）、同步语义在不同驱动与 MoltenVK 上差异明显。
   需要为关键能力设计 feature gate 与 fallback（例如：无 sparse residency 的降级路径、无 HDR 的 8-bit 路径、不同格式的渲染与混合实现）。
