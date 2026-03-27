# 最终愿景与开发方向 (Vision & Direction)

> **状态更新**：Vulkan 画布后端的基础设施（设备/队列/显存池/稀疏画布）、异步渲染线程，以及一套可运行的 compute+graphics 显示管线已落地；但与 Krita 的核心逻辑（真实笔刷系统、真实图层栈/投影/非破坏节点、位深与色彩管理）仍存在关键“接线”与正确性差距，当前更接近可运行的 GPU Canvas 原型。

## 最终愿景
将 Krita 现有的、以 CPU 为核心的图像处理管线（Tile Manager & CPU Rasterizer）全面重构为**纯 GPU 驱动的渲染与计算架构**。
新架构的终极目标是**对标 Procreate**，实现一个以 GPU 计算为基础、针对现代大显存平台和 UMA（统一内存架构，如 Apple Silicon、Intel/AMD 核显）高度优化的绘制系统。
它将彻底消除高分辨率画布和超大复杂笔刷下的输入延迟与渲染卡顿，为数字艺术家提供丝滑、零延迟的创作体验。

除此之外，Vulkan 路线必须满足两个硬性目标：
1. **视觉正确性**：不同位深/颜色空间/显示滤镜（含 OCIO）下结果与现有渲染路径一致。
2. **功能可替代性**：覆盖日常创作的主功能链路（笔刷、图层、常用混合、撤销/保存、基础非破坏编辑）。

## 开发方向 (Core Directions)

1. **GPU 驻留画布 (VRAM Residency)**
   抛弃传统的“CPU 计算像素 -> 上传纹理 -> GPU 显示”流程。整个活动图层堆栈都将驻留在显存 (VRAM) 中。所有的笔刷印迹生成 (Dab Generation)、像素混合 (Compositing) 都在 GPU 端通过 Compute Shader 直接完成。

2. **虚拟纹理分级缓存 (Virtual Texturing & Tiers)**
   借鉴 Unreal Engine 5 的虚拟纹理思想，解决超大画布的显存分配问题：
   * **L1 缓存 (VRAM - Hot Tiles)**：仅为当前视口可见及正在绘制的图层 Tile 分配物理显存（基于 Vulkan `VK_KHR_sparse_binding`）。
   * **L2 缓存 (RAM - Warm Tiles)**：利用 Vulkan Timeline Semaphores 进行异步预取，当笔刷靠近边界或视口平移时，提前从内存推入显存。
   * **L3 缓存 (SSD - Cold Tiles)**：针对隐藏或非活跃图层，利用 DirectStorage / Vulkan Video DMA 直接流式传输到 GPU，绕过 CPU 解压。

3. **异步绘制与零拷贝 (Asynchronous & Zero-Copy)**
   * **三重缓冲 (Triple Buffering)**：解耦 UI 线程与渲染线程。UI 永远不会因等待 GPU 混合完成而卡死。
   * **UMA 零拷贝**：在核显/统一内存架构设备上，利用 `HOST_VISIBLE` 和 `HOST_COHERENT` 特性，使 CPU 输入与 GPU 渲染物理上共享同一块内存，消除总线传输延迟。

4. **压榨 GPU 极限性能**
   参考 `llama.cpp` 在 Transformer 推理中对显存同步的苛刻优化：
   * 采用自定义显存池 (Memory Pooling)，避免绘制中途分配内存。
   * 使用 `Push Constants` 传递高频笔刷参数（压感、倾斜等）。
   * 探索 Vulkan Subgroup 操作（如 `subgroupAdd`），在 Wavefront/Warp 级别进行极速像素混合。

5. **与 Krita 核心的可控接线（分阶段、可回退）**
   * 保持 Vulkan 与现有 CPU/OpenGL 路径可并行、可对照、可回退，避免“一刀切替换”导致不可用。
   * 明确“接线面”：输入事件 → 笔刷引擎 → 图层/投影合成 → 显示色彩管理 → CPU↔GPU 同步（撤销/保存）。
   * 以可验证的最小闭环推进：先打通最常用链路，再扩展更多 paintop、混合模式、滤镜与非破坏节点。
