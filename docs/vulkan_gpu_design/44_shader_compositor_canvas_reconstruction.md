# Shader、Compositor 与 Vulkan Canvas 重建方案

> 本文回答 BR0 清理后最容易遗漏的三类基础能力如何重建。它不恢复旧 `GraphicsPipeline`、
> `LayerCompositor`、`RenderThread` 或 `Canvas` 对象图，而是保留算法成果、重写资源 ABI 与生命周期。

## 1. 总体拆分

旧路径：

```text
Canvas
 -> TileManager/sparse canvas
 -> RenderThread
 -> BrushEngine / LayerCompositor / GraphicsPipeline
 -> Swapchain
```

新路径：

```text
Layer/Flow Authoring Snapshot
 -> schema-specific Lowerer -> EvalGraphIR
 -> EvaluationPlanner -> immutable execution task DAG
 -> PageStore/ValueStore exact access plan
 -> pass-specific executor
 -> SubmissionCoordinator
 -> published canonical generation or derived DisplaySurface
 -> backend WSI SwapchainSession
 -> UI ViewAttachment
```

新结构不保留“一个大 graphics/compute pipeline manager”。每种 pass 有独立语义契约，共享 shader catalog、
pipeline repository、descriptor/command arena 和 resource retirement。

## 2. Shader 源码布局

```text
libs/vulkanbackend/shaders/
  manifest/
  math/
    blend/
    brush/
    sampling/
    color/
  abi/
    page_access.glsl
    surface_codec.glsl
    pass_common.glsl
  stroke/
  composite/
  display/
  diagnostics/
```

### `math/`

- 只有纯函数；
- 不声明 descriptor/push constant；
- 明确输入/输出范围、alpha、working color space 和精度；
- 可由多个 pass include；
- 每个算法族有 CPU reference/golden。

### `abi/`

- operation-scoped page handle/binding；
- canonical format decode/encode；
- descriptor set/push constant 的生成/校验定义；
- 不允许 shader 热路径查询全局可变 hash page table。

### pass 目录

- 只组合 math + ABI；
- manifest 显式声明读写资源和 required feature；
- 不把画布、active layer 或 swapchain 固定为某个全局 descriptor。

## 3. Shader build 与版本

每个 shader asset identity：

```text
LogicalShaderId
Stage + EntryPoint
SemanticVersion
PassAbiVersion
SourceDependencyHash
SPIR-V Hash
ReflectionDigest
RequiredCapabilities
SupportedFormat/Alpha Classes
```

版本变化规则：

- 只改优化、不改像素语义：SPIR-V hash 变，semantic version 可不变；
- 改 rounding/blend/alpha/coverage：semantic version 必须变；
- 改 descriptor/push constant：pass ABI 必须变；
- 改 format/codec support：capability descriptor 与 golden matrix 必须同步变。

pipeline cache key 使用这些字段和 device generation，不能复用旧 ABI 的 pipeline。

## 4. 旧 Blend GLSL 的迁移

### 4.1 先定义 reference contract

每个 mode 先回答：

- 对应哪个 Krita `KoCompositeOp`；
- source/destination 是 straight 还是 premultiplied；
- blend function 在 alpha composite 前还是后执行；
- working space 是线性还是 profile/perceptual；
- integer/float rounding 与 clamp；
- 无效值/除零策略。

### 4.2 测试分层

1. scalar/vector fixtures：0、1、边界、随机值；
2. CPU reference 与 GLSL compute buffer 输出；
3. 小图 source/destination/alpha golden；
4. 多 format codec 往返；
5. stroke 与 layer composite 分别验证，因为它们的 coverage/opacity 语义不相同；
6. 多 GPU/driver tolerance 记录。

只有通过的 mode 才进入 capability；其他 mode 在 begin stroke/composite planning 时显式 CPU route 或 replay。

## 5. Stroke shader 重建

旧 round/stamp shader 中仅提取纯数学。新 kernel 接口以 page job 为单位：

```text
PageJobHeader[]
PageDabRef[]
ResolvedDab[]
MicrotileRange[]
ResourceHandleTable
TargetPageAccessView[]
Snapshot/MaskPageAccessView[]
```

约束：

- 一个目标像素只能由一个 invocation 写；
- 同 page/microtile 内按 `(sequence, subSequence)` 应用 dab；
- 不同 page 或无重叠 microtile 并行；
- kernel 不提交、不获取 lease、不 publish generation；
- codec 在 pass 边界明确 decode/encode，不假定 rgba8；
- page handle 在 operation 封存后不可被 residency 原地改写；
- resource 缺失使 batch pending/failed，不能采样透明替代。

首个 Auto Round/RGBA8 golden 可用于验证结构，但不改变 MVP 多格式和完整存储目标。

## 6. Composite 语义分层

### 6.1 Lowerer 与 Planner 位于 `kritaimage`

Layer Tree、未来 Flow graph 和外部 workflow adapter 先生成 versioned immutable authoring snapshot，再由各自 lowerer
生成同一个 `EvalGraphIR`：

```text
EvaluationEpoch
MutationRootSet
Typed Node/Port/Edge descriptors
RequestedOutputs
OperationId / SemanticVersion
Region/Purity/Determinism contract
Input ValueVersions
```

`KisEvaluationPlanner` 再从 requested outputs 反向裁剪并产生 backend-neutral execution task DAG。只有
`KisLayerStackLowerer` 可以把线性图层结构标记为 lower/target/upper 优化，并决定什么可 checkpoint、什么可作为
overlay/operator、什么必须 replay。该分类不能进入通用 IR 或 Vulkan ABI。

Vulkan executor 不解释 Krita node tree/Flow graph，也不因为 shader 支持一个 blend mode 就跳过 mask/filter/group 语义。

### 6.2 Access plan

PageStore/derived cache 把 task DAG 中一个 surface operation 解析成 exact access plan：

- input read leases；
- output write/derived leases；
- halo/neighborhood；
- dependency generations；
- codec/working representation；
- readiness tickets；
- cache publication/cancel token。

### 6.3 Vulkan executor

`KisVulkanCompositeExecutor`：

- 选择已验证 pass/pipeline；
- 编码 page/dirty-region batch；
- 声明资源 use/barrier；
- 返回 submission packet/producer ticket；
- 不直接把 derived page 标记 valid。

completion 后由 cache/PageStore 核对 EvaluationEpoch、operation semantic version、evaluation context 和 dependency
vector，再发布 derived surface。过期结果直接丢弃。

## 7. Composite 能力梯度

不能用一个“GPU compositor supported”布尔值。能力按 operation id/semantic version/value type/format 声明：

### C0：基础验证

- 单一 source-over；
- 明确 alpha/working space；
- dirty page；
- output derived surface；
- CPU/GPU golden。

### C1：普通 paint layer 栈

- 已验证 blend mode；
- opacity/visibility；
- group 边界的明确规则；
- dependency invalidation。

### C2：mask/clipping/inherit alpha

- transparency/selection mask；
- clipping/alpha inheritance；
- required halo/extra input。

### C3：filter/group/pass-through/backdrop

- filter mask/generator/file layer；
- pass-through group；
- backdrop-dependent operator；
- replay bundle 与非局部 invalidation。

某 operation 超出能力时 planner 选择 CPU/reference producer；Layer 优化也可保留 replay，不允许 shader 静默忽略节点。

## 8. DisplaySurface 与显示 pass

需要新增独立于 page version 的类型：

```text
SurfaceVersion {
  SurfaceId
  SurfaceGeneration / Epoch
  Format
  Extent
  DependencyDigest
}

DisplaySnapshot {
  SurfaceVersion
  ReadyTicket
  DamageRegion
  Color/DisplayTransformId
}
```

显示链：

```text
Composite/Projection derived pages
 -> optional DisplaySurface materialization/atlas
 -> image transform + sampling
 -> color/proof/display transform
 -> checker/background
 -> pixel grid
 -> view overlays/outline/decorations
 -> swapchain image
```

旧 bicubic/checker/pixel-grid 可提取到 math/view 层；旧 `sampler2D canvasTexture` descriptor 不能迁移。显示 pass 必须
绑定 snapshot 的 exact surface generation，并通过 last-use ticket 保证资源在 present 完成前不回收。

## 9. Color 与格式决策

必须区分：

- canonical document format；
- shader working representation；
- derived composite/display format；
- swapchain/output format/color space。

codec contract：

```text
canonical bytes
 -> decode to declared working representation
 -> brush/composite math
 -> encode canonical or derived representation
```

display color transform 不得反写 canonical page。没有对应 codec/pipeline/golden 的 format 在 capability 中为不支持，
整笔或整个 segment 在操作开始前路由成熟路径。

## 10. WSI 与 Canvas 重建

### 10.1 UI 侧

`KisVulkanViewAttachment` 维护：

- view id/document session weak handle；
- native window/screen generation；
- logical/physical extent、DPR；
- viewport transform；
- visibility/minimize；
- display filter request；
- overlay scene snapshot。

它把 immutable view state 交给 backend，不持 `VkDevice/VkQueue/VkSwapchainKHR`。

### 10.2 backend WSI 侧

`KisVulkanSwapchainSession` 维护：

- device generation；
- native surface/surface generation；
- selected format/present mode/extent；
- swapchain generation/images/views；
- bounded frame slots；
- acquire/present status；
- 每资源 last-use ticket；
- retirement chain。

present 仍由 coordinator 执行。WSI session 产生 packet，不直接调用 queue。

### 10.3 resize/out-of-date

```text
ViewState extent generation changes
 -> request new swapchain generation
 -> old generation stops new acquire
 -> completed frame slots retire by ticket
 -> new generation becomes current
 -> old surface/resources destroy after last use
```

不调用 device/queue idle，不暂停 stroke，不阻止 save/undo。

### 10.4 macOS

UI adapter 负责 `CAMetalLayer`/native view 生命周期与线程要求；backend 只接收有 generation/lifetime token 的 native
surface descriptor，并创建 Vulkan surface/swapchain。旧 `.mm` 代码只作为平台事实参考，不恢复旧 Canvas 类。

## 11. Outline 与 Decorations

二者属于 view-derived overlay：

- 输入是 immutable geometry/bitmap snapshot；
- 有独立 resource upload ticket；
- 不读写 canonical page；
- 随 view/screen/DPR generation 失效；
- 可在缺失时降级为 UI/CPU overlay，不影响 document correctness；
- graphics pass 与 canvas sampling 的顺序由 submission packet 明确。

旧 shader 可提取，但资源 upload、descriptor、command 和 lifetime 必须接入共享 backend 基础设施。

## 12. 验证矩阵

### Shader

- source manifest/reflect/layout 一致；
- missing asset、bad SPIR-V、unsupported feature 硬失败；
- CPU/GPU math golden；
- pipeline cache key 不跨 ABI/device generation 复用。

### Composite

- operation/version/value-type/format capability matrix；
- source/diamond/fan-out/multi-output/random DAG 和 random layer graph 对 CPU reference；
- Layer Tree 与等价 Flow lowering 结果一致；
- graph/property generation 变化使旧输出不可发布；
- lower/upper cache 与 full recomposite 相同；
- backdrop-dependent 节点不被错误拍平。

### Display

- exact DisplaySurface generation 被采样；
- transform/bicubic/checker/grid golden；
- color/proof/display filter 对照；
- derived resource eviction 后可重建。

### WSI/Canvas

- acquire timeout/无 frame slot 跳帧；
- resize/out-of-date/minimize/restore；
- 多 canvas 同文档、关闭其一；
- device loss 与 CPU/OpenGL 回退；
- validation 零错误；
- UI/input thread 无 Vulkan wait。

## 13. 完成判定

下列事实同时成立前，不得说“GPU 图层混合/Shader/Vulkan Canvas 已重建”：

- 算法有明确 semantic contract 和 CPU/GPU golden；
- pass ABI 有 manifest/reflection 校验；
- executor 只消费 lease/work plan，不拥有 canonical storage；
- submission/resource lifetime 接入 coordinator；
- compositor 覆盖声明与实际节点语义一致；
- display 绑定 exact derived generation；
- WSI resize/present 不阻塞 document work；
- 产品入口通过 BR6 原子门禁并可安全回退。

在此之前只能分别写“算法已提取”“offscreen pass 已验证”“WSI 状态机已验证”，不能用旧原型截图或 shader
文件存在替代完整能力结论。
