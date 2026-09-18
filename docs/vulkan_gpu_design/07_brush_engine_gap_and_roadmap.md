# Vulkan 笔刷能力差距与路线

> 笔刷不是独立 MVP。它必须消费统一 surface/page/residency 和 page-batched stroke 系统，不能继续把当前 sparse canvas 或逐 dab dispatch 当作目标存储/执行层。总口径见 [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md)，执行模型见 [10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md)。
> 页级 kernel 与 brush resource/capability 的具体设计分别见 [13_page_work_compiler_and_gpu_kernel.md](13_page_work_compiler_and_gpu_kernel.md) 和 [19_brush_resources_and_capability_gate.md](19_brush_resources_and_capability_gate.md)。
> 全局 PaintRouter/factory wrap 在 BR0 删除；新 PaintOp 只能通过 `KisPaintExecutionContext` 获取
> `DocumentGpuSession`，见 [24_p0_backend_lifecycle_and_document_sessions.md](24_p0_backend_lifecycle_and_document_sessions.md)。

## 1. 当前已有代码

- `KisVulkanPaintOpFactory`、`KisVulkanPaintOp` 和 `KisVulkanPaintRouter` 实验代码；其中 global factory/router
  只作为失败证据留在归档历史，不迁移到新 runtime。
- preset analyzer、brush runtime、dynamics。
- round/stamp backend。
- predefined tip、texture、masking 的 CPU 资源加载代码。
- brush resource cache 和预上传队列。
- 固定 ring buffer、逐 dab compute pipeline 和 15 个共享 blend enum/mapping。
- predefined preset 解析/资源加载测试。

上述内容只证明接口和 CPU 资源路径存在。当前没有 Vulkan 输出图像测试，不能声明 predefined、texture、masking 或完整 paintbrush 已端到端支持。

## 2. 当前主要问题

### 能力门禁过宽

- 非 plain `ColorSource` 被 analyzer 放行，但运行时没有完整实现。
- `LightnessStrength` 被计算后没有应用到最终 dab 颜色。
- Wash 使用直接画布写入的近似逻辑，没有正确的 indirect painting surface。
- Sharpness、wrap-around、部分 brush tip/格式仍未实现。

这些能力在真实输出测试通过前必须明确回退。

### 资源路径未进入统一 Residency

- brush tip/texture/mask 的 GPU texture cache 有独立生命周期。
- 预上传会在 render thread 等待 fence。
- 请求缺少稳定的合并、取消、预算和回收策略。
- 资源缓存没有与画布页竞争统一 UMA/VRAM/RAM/SSD 预算。

### 生命周期和线程

- paintop 持有的 backend 会被 render thread 读取，需要明确所有权或 generation handle。
- 无 dab 的 paintop 销毁也必须清理当前 backend。
- preset 切换不能留下悬空 backend 或无限预上传队列。

### 执行模型不成立

- ring 满时丢 dab，不能保证命令完整性。
- brush compute 与 swapchain frame 共用提交生命周期。
- 同页重叠 dab 缺少正确有序的 read-modify-write 模型。
- stroke end 依赖 pause/download，不能作为长期提交边界。

## 3. Brush V1 的定义

Brush V1 在页面 MVP 完成后进入验收，至少包括：

- Auto Round Brush；
- Predefined bitmap tip；
- pressure size/opacity/flow；
- spacing/auto spacing；
- mirror；
- Normal 和明确列入白名单的 blend；
- texture/masking 的最小正确路径；
- airbrush 时间重采样；
- undo/redo/save/reopen；
- UMA 与 dGPU 两条 page backend；
- 内存压力下自动转录。

未完成的 ColorSource、Lightness、Wash、Sharpness、Text/ABR/SVG 等必须稳定回退。

## 4. 实施顺序

### B0：收紧门禁

- analyzer 默认拒绝没有运行时消费者的能力。
- 建立 preset feature manifest 和明确 fallback reason。
- 不允许“解析成功”等价于“GPU 支持”。

### B1：接入统一页面系统

- 本节只允许在全局 BR1–BR4 已通过后实施；这里的 `B*` 是 brush 内部工作包，不是全局阶段。
- `PageWorkCompiler` 按页批量取得 writable lease，brush backend 不逐 dab 操作页面。
- 当前正在写的页面进入 `CurrentWrite`，预测 corridor 进入有期限的 `PredictedWrite`。
- 根据轨迹、半径、spacing 生成预热 halo。
- brush resource 注册为只读 resource surface/cache entry；它可以有自己的不可变资源 cache，但不得创建第二套
  canonical canvas page store 或 SSD swap。
- residency、resource、previous-writer 和 snapshot 通过 ticket 成为 submission 依赖。

### B2：Auto Round golden path

- CPU reference 与 GPU output 对照。
- 快速连续 dab、边界 tile、透明度/flow、不同压力曲线。
- page-batched kernel 保证同页顺序，batch 任意切分保持输出一致。
- compute lane 不依赖 swapchain；固定队列压力下 resolved dab 零丢失。
- UMA 不发生画布像素 copy；dGPU transfer 有显式依赖。

### B3：Predefined/Texture/Masking

- 每类资源建立确定性样本。
- 验证 GPU upload/residency 生命周期，而不只是 QImage 加载。
- 对旋转、缩放、spacing 和缓存失效做输出测试。

### B4：Airbrush 与 Wash

- Airbrush 验证时间采样和重复 dab。
- Wash 必须使用独立 indirect target/segment，并在 stroke commit 正确合成；近似 max-alpha 不能作为完成标准。

### B5：性能与稳定性

- preset 快速切换；
- 大笔尖和资源压力；
- 页面迁移期间绘画；
- backend 取消和设备失败；
- p50/p95 输入到显示延迟。

## 5. 完成标准

只有同时满足以下条件，某项笔刷能力才能标记“完成”：

1. analyzer 门禁正确；
2. 正常应用入口可以触发；
3. GPU shader 输出与 CPU reference 在定义容差内一致；
4. undo/save 一致；
5. UMA/dGPU 页面路径均正确；
6. 内存压力下不会丢失或错误复用资源；
7. 有自动测试和失败回退。
