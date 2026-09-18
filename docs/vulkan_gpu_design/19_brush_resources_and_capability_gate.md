# Brush Resource、PreparedBrushProgram 与能力门禁

> 本文定义 preset 能力如何被声明、准备、固定到一次 stroke epoch，并进入统一 Residency，而不在首个 dab
> 或 render thread 中同步上传。笔刷像素执行见
> [13_page_work_compiler_and_gpu_kernel.md](13_page_work_compiler_and_gpu_kernel.md)。
> `SurfaceFormat` 与 capability 的全局真值规则见
> [29_p0_surface_format_lod_capabilities.md](29_p0_surface_format_lod_capabilities.md)。

## 1. 原则

- “能解析 preset”不等于“GPU 支持”。
- “shader 有字段”不等于运行时已经消费完整语义。
- “资源上传成功”不等于像素结果与 CPU 一致。
- capability gate 必须在 begin stroke 前给出整笔决定。
- brush program/resource 在 epoch 内不可变。
- tip、texture、mask 与 canvas/snapshot/derived page 竞争统一预算。
- 首个 dab 不做同步 resource upload/pipeline build。
- 每个放行能力必须有 GPU golden output、undo/save 和压力测试。

## 2. 两层能力模型

### 2.1 `BrushSemanticManifest`

从 preset/Krita paintop 解析出的完整需求：

```text
paintop id/version
brush tip kind/format
dynamics set
spacing/auto-spacing
mirror/scatter/rotation
opacity/flow
blend/composite mode
texture/masking
color source/lightness
airbrush/time semantics
wash/indirect painting
sharpness/wrap
neighbor-read/smudge requirements
resource identities/generations
target format/colorspace requirements
```

manifest 必须描述所有会改变输出的特性。未知字段默认 unsupported，不能忽略后继续放行。

### 2.2 `GpuBrushCapabilityReport`

将 manifest 与设备/backend/kernel 能力求交：

```text
Supported
SupportedWithVariant
RequiresPreparedResource
RequiresIndirectSurface
RequiresReadHalo
Unsupported(reason code)
BackendUnavailable(reason code)
```

reason code 是稳定、可测试、可显示的枚举，不用自由文本作为逻辑判断。

## 3. `PreparedBrushProgram`

### 3.1 身份

```text
BrushProgramId
SemanticManifestHash
BrushSemanticVersion
DeviceCapabilityKey
KernelVariantSet
PipelineGeneration
ResourceSetId
ResourceGenerationSet
DescriptorLayoutVersion
Color/FormatVariant
RecoverySupport
```

同一 preset 在不同设备、格式、颜色空间或 shader version 下可以产生不同 program id。

### 3.2 状态机

```text
Requested
  -> Analyzed
  -> ResourceResolving
  -> PipelinePreparing
  -> Ready
  -> Retiring
  -> Retired

Any pre-ready -> Failed(reason)
Ready -> Invalidated(new generation/device loss)
```

- Ready program 完全不可变。
- preset 编辑创建新 generation/program，不原地修改旧 program。
- 旧 program 在引用它的 epoch/journal 全部退休后释放。
- Invalidated program 不能接受新 stroke，但旧 journal 的恢复材料必须保留或转为显式失败。

### 3.3 准备时机

在 preset 被选中、悬停预热或资源更新时异步 prepare：

- CPU 解析和规范化；
- resource content hash/generation；
- resource surface 注册；
- pipeline/shader variant cache lookup/build；
- descriptor/resource table 准备；
- residency prefetch；
- ready ticket 发布。

不在 `paintAt()`、PageWorkCompiler 或 Presenter 中执行同步准备。

## 4. Resource Identity

资源 key 至少包含：

```text
content hash
semantic role（tip/texture/mask/...）
dimensions/format/colorspace
sampling/wrap/filter semantics
normalization/version
source revision
```

只用文件名、指针或 QImage 地址不能保证 identity。相同内容和语义可以复用 immutable surface；语义不同即使
像素相同也可能需要不同 cache entry。

## 5. Resource Surface 与 Residency

- tip、texture、mask 注册为 immutable `BrushResourceSurface`。
- CPU source、shared page、VRAM sampled atlas/image 都是该 resource generation 的 backing/cache。
- current program resource read-hot/pinned 到 epoch 结束和 journal recoverable。
- 最近 preset 可以 warm，但优先级低于当前 target、before-image 和 visible composite。
- resource upload/atlas placement/binding publish 返回 ticket。
- PageJob 把 ready/resource ticket 加入 GPU waits；host 不等待。
- 独立 brush GPU cache 不得拥有脱离 ResidencyController 的无限预算。

## 6. Descriptor 与 Pipeline

### 6.1 Descriptor

- program 建立稳定 ResourceSet。
- descriptor 不按 dab、PageJob 或 frame 重复分配。
- descriptor slot 的 last-use ticket 决定延迟回收。
- resource atlas/binding table 更新先发布 ticket，再允许新 batch 引用。
- 旧 batch 保持旧 generation view，不被新 preset 更新原地覆盖。

### 6.2 Pipeline variant

variant key 包含：

- brush algorithm；
- target format；
- blend family；
- resource sampling feature；
- subgroup/descriptor/device feature；
- semantic/shader version。

pipeline cache miss 不允许阻塞首个 dab。若 begin 时 program 未 Ready，按整笔 backend policy 处理。

## 7. Begin Stroke Policy

begin stroke 检查 program：

1. `Ready + Supported`：选择 GPU。
2. `Preparing`：产品策略可以短暂排队整笔，或立即选择同一 PageStore 上的 CPU execution path。
3. `Failed/Unsupported`：整笔 CPU fallback。
4. `BackendUnavailable`：整笔选择成熟非 GPU backend。

策略必须：

- 在产生第一个 accepted GPU dab 前决定；
- 对用户和 trace 可见；
- 不在 epoch 中切换；
- fallback 仍写同一 canonical pixel store；
- 不因 GPU 不支持而输出近似结果。

Auto Round/Normal 不依赖外部 bitmap resource，应作为首个总是可准备、可重放的 GPU golden program。

## 8. 能力分级

### 8.1 Auto Round

首条 GPU golden path 可以从以下范围开始：

- RGBA8；
- Normal；
- pressure size/opacity/flow；
- spacing/auto spacing；
- rotation/aspect；
- mirror；
- 明确测试的 eraser/alpha 语义。

必须先通过 overlapping dab、page boundary、batch partition、undo/save 和迁移测试。
但首个产品 MVP 不能把底层固定为 RGBA8：必须覆盖 4/8/16 字节像素 `SurfaceFormat`，不支持的组合在
begin stroke 前稳定路由 CPU。

### 8.2 Predefined Tip

需要：

- CPU resource normalization 与 Krita 语义一致；
- scale/rotation/subpixel sampling；
- grayscale/alpha interpretation；
- resource generation invalidation；
- atlas/descriptor 生命周期；
- GPU output golden image。

`QImage` 加载成功只证明输入资源存在。

### 8.3 Texture/Masking

分别声明：

- coordinate space；
- wrap/repeat；
- filter；
- strength/inversion；
-与 opacity/flow/tip 的组合顺序；
- colorspace/linearization。

不能把 texture 与 masking 合并成一个近似 multiplier 后宣称完整支持。

### 8.4 Airbrush

- 使用 journal 显式时间记录或已解析 restamp dab。
- 重放不读取当前 wall-clock。
- 长按、移动、压力变化与 CPU reference 一致。
- background timer 不直接提交 Vulkan。

### 8.5 Wash/Indirect

- capability report 标记 `RequiresIndirectSurface`。
- 使用 stroke-local indirect surface 和明确 composite stage。
- overlap/opacity 语义与 CPU reference 对齐。
- 直接 target max-alpha 近似不能标记支持。

### 8.6 ColorSource/Lightness

- manifest 完整记录 source、颜色转换和 strength。
- CPU dynamics 计算出的值必须进入 kernel 最终颜色路径。
- 未实现的非 plain ColorSource 和 LightnessStrength 明确 fallback。

### 8.7 Sharpness/Wrap/Smudge

- Sharpness 的像素 snap/coverage 语义必须有 reference。
- Wrap 影响 bounds/page enumeration，不能只修改 shader 坐标。
- Smudge/neighbor-read 需要 read halo、输入输出 generation 分离和特殊 stage DAG。

## 9. 生命周期与线程

- PaintOp 只持有 `PreparedBrushProgramHandle`，并从 `KisPaintExecutionContext` 获取文档 session；不持有
  backend 裸指针或 UI canvas。
- handle 包含 program id/generation，跨线程只读。
- Resource prepare worker 只产生逻辑资源和 upload request，不直接与 Presenter queue 竞争。
- SubmissionCoordinator 提交 upload/publish。
- 快速切换 preset 可以取消未提交 prepare，但 in-flight resource 按 ticket 延迟回收。
- 无 dab 的 paintop 销毁也正确释放 program handle/epoch reservation。

## 10. 恢复要求

一个 GPU brush program 只有在以下条件满足时才可标记 RecoverySupport：

- journal 命令足够重建所有随机/时间语义；
- resource generation 在 recoverability 前可访问；
- CPU reference 或新 GPU device 能执行相同 semantic version；
- shader/device-specific 不确定行为已排除；
- indirect/neighbor stage 的 base/snapshot 完整。

无法恢复的能力不能让 dGPU VRAM 成为用户已接受笔迹的唯一最新数据。

## 11. 测试矩阵

每个能力：

1. analyzer manifest 单元测试；
2. capability allow/reject reason 测试；
3. resource identity/generation 测试；
4. CPU reference vs GPU output；
5. page boundary/rotation/scale；
6. preset 快速切换和旧 program retention；
7. 资源上传延迟/失败；
8. 极小预算 residency；
9. undo/save/reopen；
10. device-loss replay 或明确不放行。

## 12. 实现路线

以下 `BC*` 是 brush capability 内部工作包，只能在全局 BR5/BR6 的相应门禁内执行，不得与全局 BR0–BR6
同名或改变其顺序。

### BC0：Manifest 与门禁

- 覆盖所有已知 preset feature。
- 默认拒绝未知/未消费语义。
- 稳定 fallback reason。

### BC1：Prepared program 生命周期

- program id/generation/state machine。
- async prepare、Ready ticket、快速切换取消。
- 删除跨线程 backend 裸指针。

### BC2：Resource surface

- immutable identity/content hash。
- 统一 Residency budget 和 read lease。
- descriptor/pipeline 延迟回收。

### BC3：Auto Round

- 最小 always-ready program。
- page-batched golden tests。

### BC4：Predefined/Texture/Mask

- 逐项 schema、resource semantics 和输出测试。
- 每项独立解除门禁。

### BC5：Time/Indirect/Neighbor algorithms

- Airbrush journal time。
- Wash indirect surface。
- Smudge read halo/stage DAG。

### BC6：颜色和扩展能力

- ColorSource/Lightness/更多 blend/format。
- 只在端到端证据完成后更新 manifest allow list。

## 13. 验收门槛

- begin stroke 前确定 GPU/CPU backend，epoch 中不切换。
- 首个 dab 不同步上传 resource 或构建 pipeline。
- PaintOp/worker 不持有跨线程 backend 裸指针。
- resource 使用统一 Residency 和 ticket。
- descriptor/pipeline/resource 不在 in-flight 时销毁或原地更新。
- capability allow list 与真实 kernel/resource/transaction 支持一一对应。
- 每项放行能力有 CPU/GPU golden、迁移、undo/save 和失败测试。
- 近似 Wash、未消费 ColorSource/Lightness 等不再宣称支持。
