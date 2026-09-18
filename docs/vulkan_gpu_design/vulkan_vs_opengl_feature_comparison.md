# Krita OpenGL 与实验 Vulkan 路径对比

> 本表区分“代码存在”和“已验证”。统一状态口径见 [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md)，
> 全局 P0 校正见 [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)。

| 能力 | 现有 OpenGL/CPU 路径 | Vulkan 分支当前事实 | 状态 |
|---|---|---|---|
| 正常应用入口 | 成熟 | Vulkan 初始化没有接入正常启动链 | 未接线 |
| 画布显示 | 成熟 | graphics pipeline、swapchain 和 shader 代码存在 | 未构建/未运行验证 |
| Pan/Zoom/Rotation | 成熟 | transform push constants 和相关代码存在 | 未验证 |
| Brush compute | CPU 成熟 | round/stamp compute 和 ring buffer 存在 | GPU 输出未验证 |
| Predefined brush | 成熟 | preset 解析和灰度 tip CPU 测试存在 | 非端到端 |
| Texture/Masking/Airbrush | 成熟 | 有实验实现 | 未验收 |
| ColorSource/Lightness/Wash | 成熟 | analyzer/运行语义不完整 | 必须回退 |
| 图层合成 | 成熟 | compositor/NodeSync 代码存在，但输出绑定、清零、descriptor 和失效有问题 | 阻断 |
| 撤销/保存 | 成熟 | 异步下载与 transaction 框架存在 | 未验证且同步不完整 |
| VRAM/RAM 页面 | CPU tile + 显示纹理 | sparse/staging 实验代码存在 | 状态机未完成 |
| SSD backing | Krita 已有 `KisTileDataStore`/`KisSwappedDataStore` swap 基础 | Vulkan `L3_Cold` 未接入现有 swap，也没有 generation/checksum/authority 闭环 | 未统一 |
| UMA 指针旁路 | 非目标 | 只检测 UMA/host-visible，画布仍需 staging/image 路径 | 未实现 |
| 自动温度管理 | CPU 缓存策略成熟 | 简单 age/prefetch | 未实现 |
| 目标图层剪枝 | CPU 投影体系 | 尚无 MutationRootSet/segment/checkpoint 模型 | 未实现 |
| 高位深/色彩/OCIO | 成熟 | 主要固定 RGBA8，占位接口 | 未实现 |
| 滤镜/非破坏节点 | 成熟 | NodeSync 只处理直接 paint layer | 未实现 |
| 自动测试 | 大量 | 3 组 Vulkan 相关 CPU 侧测试 | 明显不足 |

## Vulkan 路径的潜在优势

- UMA 上 CPU/GPU 共享权威页，避免画布像素复制。
- 独显上以 VRAM cache、RAM backing 和 SSD spill 支持超大工作集。
- 当前目标图层是唯一常见写入点，可用 lower/upper 派生缓存剪枝非目标层。
- compute brush、局部合成和页面温度可以由同一绘画预测信息驱动。

这些是目标能力，不是当前性能结论。

## 下一步

先执行 BR0 受控重置并保持 Vulkan 用户入口关闭，再依次完成 canonical PageStore、SubmissionCoordinator、
replica、EvaluationEpoch、GPU stroke/undo/save，最后在 BR6 接入 UI/display。基本多层剪枝、格式身份和三层转录属于
首个 MVP，不能推迟到入口启用后。详细顺序见 [03_development_steps.md](03_development_steps.md)。
全局重建与旧路径删除顺序见 [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md)，
GPU stroke 内部施工见 [21_implementation_and_baseline_cutover.md](21_implementation_and_baseline_cutover.md)，
验证证据要求见 [20_observability_testing_and_performance.md](20_observability_testing_and_performance.md)。
