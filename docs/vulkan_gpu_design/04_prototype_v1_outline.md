# 第一个原型版本大纲 (Prototype V1 MVP)

> **状态更新**：Prototype V1 的目标是验证“Vulkan 画布 + GPU 计算 + 显示”链路可行性，目前相关基础设施已落地并可运行；但仍需要把 Krita 的真实输入/笔刷/图层系统接线到 Vulkan 入口，才能进入日常可用阶段。

## MVP 目标 (Minimum Viable Product)
第一个原型（Prototype V1）的目标是**验证核心架构的可行性**，即证明 "UI输入 -> Compute Shader处理 -> Vulkan Swapchain显示" 这条纯 GPU 管线能够跑通，并展现出超越现有 CPU 架构的潜力。

MVP 将极其精简，暂时剥离所有非核心功能（如滤镜、变形、复杂的笔刷引擎特性等）。

## 核心功能范围

1. **单图层渲染 (Single Layer Rendering)**
   * 不支持图层组、蒙版、混合模式（仅支持 Normal 模式）。
   * 画布完全驻留在 VRAM 中（通过 `VK_KHR_sparse_binding` 实现逻辑上的无限画布）。
   * 仅处理一个基础的像素图层。

2. **基础笔刷 (Basic Brush Engine)**
   * 仅支持最基础的圆形笔刷（Round Brush）。
   * 不包含纹理、动态颗粒或复杂的动态形状。
   * 支持基本的压力感应（控制不透明度和笔刷大小）。
   * 通过 Ring Buffer 将笔迹点传递给 Compute Shader 进行 Dab 生成与混合。

3. **基础画布导航 (Canvas Navigation)**
   * 丝滑的平移 (Pan) 和缩放 (Zoom)。
   * 平移和缩放操作必须是完全异步的，不能因渲染未完成而掉帧。

## 技术实现要点

* **Vulkan 基础设施**：一个能在主窗口正常显示的 `KisVulkanCanvas`，以及一个管理实例、设备、队列的 `VulkanDeviceManager`。
* **稀疏纹理 (Sparse Texture)**：分配一张巨大的逻辑 2D Image，但在 MVP 阶段，我们只需为其中心（视口初始位置）以及笔刷划过的地方绑定物理内存页面。
* **Compute Shader 管线**：
  * 一个简单的 `.comp` 着色器，读取 Ring Buffer 中的 `(x, y, pressure)`。
  * 将圆形图案（通过 SDF 距离场或基础算法）绘制到绑定的物理 Tile 上。
* **无锁输入与呈现 (Lock-free Input & Present)**：
  * UI 线程负责将鼠标/压感笔事件推入无锁队列。
  * 渲染线程负责消耗队列，调用 `vkCmdDispatch`，并在完成后执行 `vkQueuePresentKHR`。

## 成功标准 (Success Criteria) [已达成]
1. 在 4K/8K 分辨率画布下，使用 1000px 以上的巨型笔刷快速涂抹，UI 界面（包括平移缩放）帧率稳定在 60Hz/120Hz（取决于显示器），没有任何“笔刷跟手感”卡顿。
2. 通过 RenderDoc 抓帧证明：整个绘制过程中没有任何 CPU 到 GPU 的像素数据回传或同步阻塞（除了命令提交和 Ring Buffer 更新）。
3. 显存分配平稳，没有发生频繁的 `vkAllocateMemory` 调用。

> 说明：上述“已达成”主要针对 Vulkan 子系统内部的原型链路验证；并不等同于 Krita 真实笔刷系统/图层系统已全量切换到 Vulkan。

---
👉 **下一步计划**：核心计算管线已通，即将进入前端表现层完善阶段，详见 [Prototype V2 (Feature Parity) 大纲](05_prototype_v2_outline.md)。
👉 **并行推进**：在前端表现层对齐的同时，需要启动“核心接线”工作（输入接线、图层栈接线、撤销/保存一致性），详见 [开发步骤蓝图](03_development_steps.md) 的 Phase 7。
