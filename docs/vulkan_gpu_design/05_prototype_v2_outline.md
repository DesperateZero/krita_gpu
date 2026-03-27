# 第二个原型版本大纲 (Prototype V2: Feature Parity)

## 目标 (Objective)
在 Prototype V1 成功验证了纯 GPU 渲染管线底层计算架构的基础上，Prototype V2 的核心目标是**实现与现有 OpenGL 画布的前端特性完全对齐 (Feature Parity)**。
重点解决目前“后端强，前端弱”的问题，补齐缺失的表现层细节，让 Vulkan 渲染器能够真正胜任日常的数字绘画交互。

> **状态更新（以仓库现状为准）**：画布图形管线、笔刷轮廓与装饰叠加等“前端表现层”已基本具备；剩余主要集中在色彩管理/高位深显示，以及与 Krita 核心链路的接线与正确性对齐（见本文末“下一阶段”）。

## 核心功能范围

### 1. 完整的画布导航与图形管线 (Full Canvas Transformations)
* ✅ **废弃 Blit 方案**：使用完整的 Vertex / Fragment Shader 图形渲染管线替代 `vkCmdBlitImage`。
* ✅ **平滑变换**：支持缩放 (Zoom)、平移 (Pan)、旋转 (Rotation) 等相机变换。
* ✅ **高质量采样**：支持双三次插值 (Bicubic/Catmull-Rom) 等高质量采样策略。

### 2. 完善的 UI 与交互反馈 (UI & Interaction Feedback)
* ✅ **原生笔刷轮廓 (Brush Outline)**：Vulkan 侧绘制笔刷轮廓，减少对 Qt 原生绘制路径的依赖。
* ✅ **画布装饰层 (Decorations)**：网格、参考线、选区等叠加层具备可运行实现。
* ✅ **背景系统**：棋盘格/背景等程序化绘制具备可运行实现。

### 3. 色彩管理与高色深 (Color Management & HDR)
* 🚧 **OCIO 对接**：需要将 `KisDisplayFilter` / OCIO 相关参数可靠传入 shader 并应用，建立与现有路径可对照的验证用例。
* 🚧 **HDR 支持**：需要完善 swapchain 格式探测与降级策略，支持 10-bit 或 16-bit float 等高动态范围格式（无法满足能力时应可预测回退）。

### 4. 高级渲染特性 (Advanced Rendering Features)
* **无限画布 (Wrap-around)**：将 `wrapAroundMode` 参数传递给 Compute Shader，实现边缘坐标自动折叠渲染。
* **通道可见性筛选**：在图层复合 (`layer_composite.comp`) 时加入遮罩控制，支持单通道 (R/G/B/A) 独立预览。

## 技术实现要点

* **解耦与并发**：全面激活 `KisVulkanRenderThread`。使用 Vulkan Timeline Semaphores 和 Fences 实现 UI 线程输入提交与 GPU 渲染命令队列的彻底解耦。
* **Uniform Buffers / Push Constants**：合理划分数据更新频率。使用 Push Constants 传递高频变动的相机矩阵（视口平移/缩放），使用 UBO 传递低频变动的配置（色彩 LUT、网格偏好等）。
* **多管线管理**：设计一套简洁的管线切换机制，在同一个 Render Pass 中依次执行 背景绘制 -> 图像采样映射 -> UI叠加层渲染。

## 成功标准 (Success Criteria)

1. **视觉一致性**：在所有常用操作下，Vulkan 画布的视觉体验（色彩准确度、缩放清晰度、辅助线清晰度等）与现有的 OpenGL 渲染器完全一致。
2. **零闪烁交互**：彻底消除 UI 操作（如快速连续旋转画布、开启复杂的笔刷轮廓）导致的任何画面撕裂、闪烁或掉帧。
3. **极限帧率**：在开启所有 UI 叠加层和 OCIO 色彩管理的极端测试条件下，仍能保持极限巨型笔刷输入时的 60Hz/120Hz 稳定刷新率。

---
## 下一阶段：Prototype V3（核心接线与正确性）
V2 解决“看起来像 Krita 画布”的表现层后，下一阶段优先解决“真的能画、能撤销、能保存、结果正确”：
* **核心接线**：真实工具输入/笔刷系统接入 Vulkan 输入面；真实图层栈/投影驱动 GPU 合成。
* **一致性闭环**：撤销/重做/保存/导出与 CPU↔GPU tile 同步边界可验证。
* **正确性对齐**：位深、颜色空间、混合模式与显示滤镜/OCIO 对齐现有路径，并建立对照测试集。
