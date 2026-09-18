# GPU Stroke 最终奠基方案

> 本文定义 GPU stroke 的长期权威架构。页面、驻留和图层剪枝仍服从
> [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md) 与
> [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)。Canonical PageStore
> 服从 [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md)，
> 本文不能定义第二套 tile/COW/swap 身份。
> 本文不是对现有逐 dab dispatch 路径的优化清单，而是替代该路径的基线设计。

## 0. 文档分层与专题索引

本文保留 GPU stroke 重建方向的全部总纲内容，不因专题拆分而删除或缩写任何不变量、对象、时序、
施工阶段或验收门槛。以下专题文档在本文基础上继续展开具体接口、状态机、线程责任、实现顺序和测试，
不构成另一套可选方案：

| 具体问题 | 权威专题 |
|---|---|
| 当前逐 dab/render-thread 路径为什么必须退出 | [11_current_path_failure_inventory.md](11_current_path_failure_inventory.md) |
| StrokeEpoch、ResolvedDab、命令日志、容量和 backpressure | [12_stroke_protocol_and_journal.md](12_stroke_protocol_and_journal.md) |
| 稳定页面分桶、microtile、页内顺序和 GPU kernel | [13_page_work_compiler_and_gpu_kernel.md](13_page_work_compiler_and_gpu_kernel.md) |
| timeline ticket、queue 拓扑、线程所有权和资源回收 | [14_submission_tickets_and_queue_topology.md](14_submission_tickets_and_queue_topology.md) |
| Stroke 与 UMA/dGPU/SSD Residency 的连接 | [15_stroke_residency_and_memory_backends.md](15_stroke_residency_and_memory_backends.md) |
| MutationRootSet、增量合成、DisplaySurface 和 Presenter | [16_incremental_composite_and_presenter.md](16_incremental_composite_and_presenter.md) |
| PageStore 如何成为 `KisPaintDevice` 的同一权威存储 | [17_krita_pagestore_integration.md](17_krita_pagestore_integration.md) |
| Undo/Redo、保存、取消、失败和设备恢复 | [18_undo_save_cancel_and_recovery.md](18_undo_save_cancel_and_recovery.md) |
| Brush resource、PreparedBrushProgram 和能力门禁 | [19_brush_resources_and_capability_gate.md](19_brush_resources_and_capability_gate.md) |
| 可观测性、正确性、性能和压力验收 | [20_observability_testing_and_performance.md](20_observability_testing_and_performance.md) |
| GPU stroke 代码施工、提交边界和 BR5 接入 | [21_implementation_and_baseline_cutover.md](21_implementation_and_baseline_cutover.md) |
| 全局旧路径删除和 BR0–BR6 基线切换 | [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md) |

文档权威顺序如下：

1. 全项目状态和 MVP 边界以 [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md) 为准。
2. Vulkan 全局 P0 模块、数据和线程边界以 [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md) 为准。
3. 唯一全局 BR0–BR6 顺序以 [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md) 为准。
4. 统一页面与三层转录专题语义以 [09_virtual_texture_status_and_roadmap.md](09_virtual_texture_status_and_roadmap.md) 为准。
5. GPU stroke 跨专题不变量以本文为准。
6. 每个具体问题的接口和施工细节以对应专题为准。
7. 当前完成状态以可复现源码调用链、构建和测试证据为准，计划文档不得覆盖事实。

## 1. 架构结论

GPU stroke 的成熟基线不是“CPU 产生 dab，然后渲染线程逐个调用
`vkCmdDispatch`”，也不是“把现有 render thread 改得更异步”。目标必须同时满足：

1. **GPU 像素执行与 swapchain 完全解耦**：窗口 acquire、present、遮挡和重建不能阻塞笔迹计算。
2. **以页面为执行单元**：同一页面内按严格 dab 顺序混合，不同页面并行；禁止逐 dab dispatch 加逐 dab barrier。
3. **全链路票据化**：驻留、稀疏绑定、资源上传、笔迹计算、合成和 CPU 访问都通过 GPU timeline ticket 建立依赖。
4. **交互热路径无 host GPU wait**：输入、Krita stroke worker、stroke end 和 presenter 不调用 fence wait、queue idle 或 device idle。
5. **已解析 dab 永不丢弃**：队列压力只能增加排队延迟或触发整笔回退，不能静默漏画。
6. **页面版本可证明**：任何时刻都能回答某页的基准 generation、待发布 generation、最后写者和可恢复来源。
7. **UMA 与独显共享语义**：两者只在页面 backend 和 cache maintenance 上不同，stroke compiler/executor 不分叉。
8. **笔迹提交不等于像素回读**：stroke end 关闭 epoch 并返回 commit ticket；undo/save 通过快照与 read lease 工作。

以上是首个 MVP 的硬边界，不是后期性能优化。

## 2. “GPU 原生笔迹”的准确含义

GPU 原生不要求原始平板事件到最终像素的所有逻辑都运行在 GPU。Krita 的输入调度、
preset 语义、传感器曲线和部分资源解析天然位于 CPU。必须保证的是：

- CPU 只把输入解析为不可变的 `ResolvedDab` 序列；
- CPU 不为每个 dab 提交 GPU 工作，也不等待每个 dab；
- 页面分桶后，一个 page job 在 GPU 内完成该页的一段有序 dab 混合；
- 目标像素、局部合成和显示派生结果在 GPU/共享页面系统内流动；
- 只有显式 CPU 消费者申请 read lease 时才发生可见性切换或独显回传。

首版使用 CPU 稳定分桶是长期可接受设计，不是临时妥协。以后可以用 GPU prefix-sum/radix
实现同一 `PageWorkCompiler` 契约，但不得改变 dab 顺序、页面版本和提交语义。

## 3. 不可破坏的不变量

### 3.1 顺序与像素所有权

- 每个 stroke epoch 有唯一 `StrokeId`。
- 每个 resolved dab 有单调递增的 `(sequence, subSequence)`；镜像 dab 使用相同 sequence、不同 subSequence。
- 同一目标页面同一时刻只有一个逻辑写者。
- 同一页面的 dab list 必须保持全局序列顺序。
- 一个 page job 中，每个目标像素只由一个 shader invocation 写入；该 invocation 按序遍历影响该像素的 dab。
- 不同页面没有像素重叠，可以并行执行。
- 同页相邻 micro-batch 通过明确的 compute dependency 排序，不能依靠 queue submission 的偶然执行顺序。

### 3.2 数据与版本

- 页写入前固定 `baseGeneration`，写入产生唯一 `pendingGeneration`。
- GPU completion 只能发布与当前 pending generation 匹配的结果。
- 旧 ticket、取消操作或迟到 I/O 不能覆盖更新 generation。
- dirty canonical page 始终至少有一个可恢复来源：安全 backing、before-image 加 journal，或共享权威页。
- derived display/checkpoint page 可以丢弃，但不能成为文档唯一权威数据。

### 3.3 线程与等待

- UI/输入线程不等待 GPU、SSD 或 brush resource 上传。
- Krita stroke worker 不调用 `vkWaitForFences`、`vkQueueWaitIdle` 或 `vkDeviceWaitIdle`。
- Vulkan queue 的 host 提交由单一 `SubmissionCoordinator` 串行化；不能让 transfer、render 和 brush 线程并发调用同一 `VkQueue`。
- CPU 等待只允许发生在明确的非交互阻塞 API、关闭/设备恢复，或专用后台 CPU consumer 中。
- `StrokeCompute` 与 `Present` 可以位于同一 queue family，但必须使用不同的 `VkQueue`，或后端中语义等价的独立 command queue；同一串行 queue 上的不同 command buffer 不构成隔离。无法提供隔离执行资源的设备不能宣称满足低延迟 GPU stroke capability。
- swapchain acquire 使用有界/非阻塞策略；resize 只暂停 presenter，不暂停 stroke executor。

### 3.4 容量与退化

- 已接受的 `ResolvedDab` 不允许因固定 ring 满而丢失。
- command journal 使用分块、受预算管理的存储；持久超载时在 Krita stroke worker 上施加可观测 backpressure，不能冻结 UI。
- GPU 资源未准备好时，策略以整笔为单位决定 GPU 延迟执行或 CPU 回退，禁止一笔中途切换 backend。
- 不支持的 preset 在 stroke begin 前被 capability gate 拒绝，不能在 GPU 热路径中近似执行。

## 4. 核心对象模型

### 4.1 `PreparedBrushProgram`

笔画开始前冻结的不可变资源集合：

```text
BrushProgramId
BrushSemanticVersion
CapabilityManifest
PipelineVariant
ImmutableResourceHandles
ResourceGenerations
PixelFormat / ColorSpace
```

- preset 选择时异步 prepare，不在首个 dab 内同步上传。
- 资源通过统一 ResidencyController 获取 read lease。
- descriptor/pipeline 生命周期按 generation 管理，不跨线程暴露裸 backend 指针。

### 4.2 `StrokeEpoch`

一次笔迹的不可变语义边界：

```text
StrokeId
EvaluationEpoch
WritableTargetSet
TargetSurfaceGenerations
PreparedBrushProgram
CanvasTransform
CompositePolicy
UndoPolicy
BackendSelection
```

`WritableTargetSet`、EvaluationEpoch、brush program 和 backend 在 stroke epoch 中不改变。图层切换、
资源失效或不兼容操作必须关闭当前 epoch，再创建新 epoch。

### 4.3 `ResolvedDab`

CPU dynamics 的确定性输出：

```text
StrokeId
sequence / subSequence
targetIndex
bounds
shape parameters
opacity / flow / blend
color
resource references
time semantics
```

它不包含 `VkImage`、descriptor、staging buffer 或物理页地址。相同 epoch 和输入序列必须生成
可重放的相同命令。

### 4.4 `StrokeJournal`

替代固定覆盖式 ring buffer。journal 由不可变 chunk 组成：

```text
Open -> Sealed -> Compiled -> Submitted -> Recoverable -> Retired
```

- 输入追加只写当前 chunk。
- sealed chunk 永不原地修改或覆盖。
- chunk 在相关 page generation 已可恢复前不能退休。
- 设备丢失或提交失败时，可以从 before-image 和 journal 重放。
- journal budget、积压深度和最老 sequence 必须可观测。

### 4.5 `StrokeBatch` 与 `PageJob`

`StrokeBatch` 是连续 sequence 区间，不以显示帧为边界。它由延迟 deadline、命令数量、
预测 GPU 成本和资源状态共同切分。

`PageWorkCompiler` 把 batch 稳定分桶为：

```text
PageJob
  target SurfaceId/PageId
  baseGeneration -> pendingGeneration
  ordered DabRef[]
  immutable resource leases
  page write lease
  before-image ticket（首次写该页时）
  prerequisite tickets
```

大 dab 可以出现在多个 page job 中。同一 page job 的 `DabRef[]` 必须保持 sequence 顺序。

### 4.6 `SubmissionTicket`

所有异步工作返回统一逻辑票据：

```text
SubmissionTicket
  lane
  timelineValue
  operationId
  affected generations
  failure state
```

逻辑 lane 至少包括 `Residency`、`StrokeCompute`、`Composite` 和 `Present`。它们可以映射到
同一物理 queue family，但依赖关系不能因此省略。

### 4.7 协调器

- `StrokeCoordinator`：管理 epoch、journal、batch deadline、结束和取消。
- `PageWorkCompiler`：稳定分桶、成本切分、获取 page/resource lease。
- `StrokeExecutor`：生成 page-batched compute workload。
- `SubmissionCoordinator`：唯一拥有 queue submission 顺序和 timeline 分配。
- `StrokeCommitter`：发布 generation、undo transaction 和 recoverability 状态。
- `IncrementalEvaluationScheduler`：只重算受目标页影响的可见派生页。
- `Presenter`：显示最近已完成的 DisplaySurface generation，不参与 stroke 完成判定。

## 5. 端到端时序

```text
Krita input/stroke worker
  -> resolve input into ResolvedDab
  -> append immutable journal chunk
  -> seal StrokeBatch

PageWorkCompiler
  -> stable page binning
  -> acquire target write leases
  -> acquire immutable resource read leases
  -> request first-write before-images
  -> attach residency/resource/previous-writer tickets

SubmissionCoordinator
  -> submit page-batched stroke work
  -> signal StrokeCompute ticket

PageStateMachine
  -> publish matching pending generations after completion
  -> emit dirty page/revision events

IncrementalEvaluationScheduler
  -> wait on StrokeCompute ticket in GPU dependency graph
  -> rebuild affected Lower/Target/Upper/Display pages only
  -> signal DisplayReady ticket

Presenter
  -> select newest already-complete DisplaySurface generation
  -> render/present it
  -> if none is newer, present the previous generation
```

关键点：`vkAcquireNextImageKHR` 永远不位于 stroke compute 的前置路径中。窗口无法 present 时，
笔迹仍可执行、提交版本和形成 undo；恢复显示后 presenter 获取最新 DisplaySurface。

## 6. Page-batched kernel

### 6.1 稳定页面分桶

首版可在 CPU 执行：

1. 按 batch 原始顺序遍历 `ResolvedDab`。
2. 根据逻辑页面几何求 dab 覆盖页集合。
3. 向每个目标页的 list 追加 `DabRef`。
4. 不排序 list；追加顺序就是严格混合顺序。
5. 对小 dab 可继续稳定分桶到页面内 microtile，减少每个像素需要测试的无关 dab；microtile list 仍保持原始顺序。
6. 根据 page/microtile list 长度、覆盖像素和资源采样成本切成有上限的 micro-batch。

这一步只处理轻量元数据，不读取或写入目标像素。

### 6.2 GPU 执行模型

一个 indirect dispatch 处理一组 page job。每个 workgroup 对应一个页面或页面 microtile：

- invocation 以 stride 方式覆盖页面像素；
- 每个像素只被该 job 中一个 invocation 所有；
- invocation 按该 page/microtile 的 `DabRef[]` 顺序测试覆盖并执行混合；
- 不命中的 dab 快速跳过；
- 同一 job 内不需要 dab 间全局 barrier；
- job 结束后设置一次 page-batch 写可见性依赖。

这样把当前 `N 个 dab × N 次 dispatch/barrier` 改为 `M 个页面 × 有序像素循环`。它同时满足
重叠 dab 正确性和 GPU 并行性。

### 6.3 超大工作负载

- 大 dab 按不相交页面自然拆分，可以跨多个受预算控制的 submission 渐进完成。
- 同一页 dab list 过长时按连续 sequence 区间切 micro-batch；相邻 micro-batch 之间只需要一次明确依赖。
- `BatchCostModel` 限制单次 kernel 的预测时间，避免一个超大笔尖长期占据 GPU。
- 成本模型只决定切分，不允许改变像素语义或丢 dab。

### 6.4 特殊笔刷

- Incremental/Normal 类笔刷直接写目标 page。
- Wash、smudge 或需要 indirect painting 的笔刷使用独立 canonical/transient surface 和显式 stage DAG。
- 多目标笔刷按 `(target, page)` 分桶；目标间存在语义依赖时通过 stage ticket 排序。
- 不能把需要背景或邻域的算法硬塞进 direct RMW kernel。

## 7. 同步与提交模型

### 7.1 依赖图

每个 stroke submission 显式等待：

- 目标页 residency/restore ticket；
- sparse bind 或 direct/local binding publish ticket；
- brush resource ready ticket；
- before-image snapshot ticket；
- 每个目标页的 previous-writer ticket。

完成后信号 `StrokeComputeTicket`。合成 submission 等待该 ticket，CPU 不参与串联。

### 7.2 页面状态

推荐把“内容版本”和“存储位置”分开：

```text
PublishedGeneration
WriteGeneration
LastWriterTicket
AuthorityReplica
ValidReplicas[domain, generation]
ReadLeases / WriteLease
CpuVisibilityState
```

- 新 writer 可以依赖尚未完成的 `LastWriterTicket`，无需 CPU 等待。
- CPU read lease 只等待自己需要的 generation。
- UMA CPU lease 在 ticket 完成后执行必要 invalidate；CPU release 后执行必要 flush。
- dGPU CPU lease 触发页级 download ticket，不阻塞 stroke/present lane。

### 7.3 禁止的同步

以下调用不得出现在交互热路径：

- `vkDeviceWaitIdle`；
- `vkQueueWaitIdle`；
- 无限期 `vkWaitForFences`；
- “暂停 render thread，再下载页面”；
- stroke end 全局 flush；
- 为资源上传阻塞首个 dab；
- 让 graphics submit 只等待 swapchain semaphore，却忽略 transfer/sparse ticket。

资源销毁使用 deferred reclamation：对象在其最后 ticket 完成后由回收器释放。

## 8. UMA 与独显

### 8.1 UMA

- canonical target page 位于持久映射的 shared buffer arena。
- stroke kernel 通过 direct PageHandle 或 operation-scoped binding table 和 storage buffer offset 直接读写该页。
- CPU paint consumer 通过 read/write lease 获得指针。
- coherent 内存仍需要执行顺序；non-coherent 内存额外执行 flush/invalidate。
- stroke end 不复制像素，不生成 staging download。
- display atlas/image 只是 derived cache，可以按脏页更新或丢弃重建。

### 8.2 dGPU

- logical generation 是 canonical identity；VRAM、RAM、SSD 都是 replica，任一 domain 只有在同 generation
  内容完成并校验后才能接管 authority。
- stroke 写入可以让 VRAM pending generation 成为最新版本，但 journal/before-image 必须保留到该版本可恢复。
- CPU 消费、保存或 dirty eviction 才请求回传，不因松笔自动回传所有脏页。
- upload/download/sparse bind 只产生 ticket，不允许调用者直接等待 queue idle。
- 不支持 sparse residency 时使用 paged buffer/atlas backend，stroke 上层语义不变。

## 9. 图层剪枝与局部合成

单目标 epoch：

```text
LowerCheckpoint + WritableTarget + UpperOverlay/Operator/Replay
                                      -> DisplaySurface
```

- LowerCheckpoint 在 epoch 内不因目标页写入失效。
- 目标 page generation 变化只使相交的下游派生页失效。
- 安全 upper overlay 直接复用；operator/replay 只在脏区重算。
- presenter 只消费 DisplaySurface，不直接采样正在写入的 canonical target。
- grid、guide、selection 等 UI decoration 使用独立 overlay 或脏区更新，不允许每帧创建并上传全窗口 QImage。

这使目标图层之外的 canonical 页可以依据缓存覆盖度降温，同时让显示与 stroke 写入不存在读写竞争。

## 10. Stroke end、Undo、保存与恢复

### 10.1 Stroke end

`endStroke()` 只做：

1. 追加不可变 End marker；
2. seal 最后 batch；
3. 关闭 epoch 的新输入；
4. 返回 `StrokeCommitTicket`。

它不暂停 executor、不等待 GPU、不回读画布。下一笔若写相同页面，通过 page last-writer ticket 自动排序；
写不同目标时可以并行。

### 10.2 三种完成状态

- **Accepted**：命令已进入 journal，不能静默丢失。
- **Visible**：对应 DisplaySurface generation 已完成，可被 presenter 选择。
- **Recoverable**：新页面数据已有安全 backing，或 before-image + journal 足以确定性恢复。

Krita undo transaction 只能在 Recoverable 后发布，但发布过程由异步 stroke job 完成，不阻塞输入/UI。

### 10.3 Undo/Redo

- 页面第一次写入前创建 COW before-image。
- 同一 stroke 对同一页只保留一份 before-image。
- undo 是一次新的页面版本切换/恢复 operation，并依赖尚未完成的 writer ticket。
- 已提交但尚未执行的 batch 可以取消；已经执行的 batch 必须通过 snapshot 恢复，不能只丢命令。
- derived composite/display page 不进入文档 undo。

### 10.4 保存和 CPU consumer

- 保存开始时捕获 evaluation epoch 与 canonical page generation map。
- serializer 在后台逐页申请该 generation 的 read lease。
- UMA 直接读共享页；独显按页异步回传。
- 后续笔迹生成新 generation，不改变已捕获的保存快照。
- 禁止为保存调用全局 device idle 或把整幅文档复制回 CPU 后才开始序列化。

### 10.5 失败与设备丢失

- pending generation 失败时不能覆盖 committed generation。
- SSD/transfer 失败时保留最后权威 allocation 和 journal。
- dGPU 最新数据尚未回写而设备丢失时，从 before-image 与确定性 journal 重建。
- 无法确定性重放的 brush 不得进入 GPU capability manifest。
- 恢复失败必须显式终止 transaction 并报告，不能把页面标记为 clean。

## 11. 线程和所有权

```text
UI/Input
  只产生输入事件，不接触 Vulkan

Krita Stroke Worker
  dynamics -> ResolvedDab -> StrokeJournal

Stroke Compiler Worker
  stable page binning、lease request、batch compilation

Residency/IO Workers
  RAM/SSD 工作和 ticket completion

SubmissionCoordinator
  唯一 queue submission owner、timeline 分配、deferred reclamation

Presenter
  选择最近完成的 DisplaySurface，构造 PresentRequest

SubmissionCoordinator
  实际执行 submit/bind/present，独占所有 VkQueue
```

command pool、descriptor arena 和 transient buffer 按 submission lane/frames-in-flight 管理，不能由另一个线程在
GPU 尚未完成时 reset。任何跨线程对象都使用 generation handle 或不可变 shared state，不共享裸 backend 指针。

## 12. Krita 集成边界

GPU stroke 不能在 `KisPaintDevice` 之外维护第二份长期权威画布，再靠 `writeBytes()` 回灌。长期边界应为：

- `KisPaintDevice` 通过 canonical PageStore access facade 暴露逻辑 tile、extent 和 iterator 语义；该 facade
  是现有 tiles3/COW/swap 的演进，不是并列 provider；
- GPU brush、CPU brush、滤镜、保存和 undo 都申请同一 canonical surface 的 domain lease；
- dirty 通知携带 `(SurfaceId, Region, Generation)`，不携带另一份镜像像素所有权；
- Vulkan canvas/UI 只消费 DisplaySurface 和 presenter 状态，不直接操作 target page、transfer queue 或 brush executor；
- `KisTransaction` 保存 page snapshot handle/generation，而不是依赖 stroke end 把 GPU 像素写回另一套 CPU tile；
- 传统同步 CPU API 必须在进入像素内循环前声明访问区域和读写模式，由后台 stroke job 完成一次域切换；禁止 iterator 每触达一个 tile 就隐式等待 GPU；
- 无法预声明范围的旧 CPU 操作可以请求整个相关 surface 的 CPU lease，但等待发生在调度 worker，并且仍使用同一 PageStore，不产生永久双副本。

整笔 CPU fallback 也必须写同一 canonical surface：UMA 取得 CPU write lease；dGPU 后端使所需页转为
CPU-authoritative，再由后续 GPU consumer 按 ticket 恢复。回退不是另一套画布，也不能与 GPU backend 在同一
stroke epoch 中混写。

这条边界负责控制对 Krita `libs/image` 与 `libs/ui` 的咬合：`kritaimage` 只定义
surface/page/lease/ticket 和 backend-neutral document session slot；`kritavulkanbackend` 不链接 `kritaui`；
UI adapter 只管理 WSI/display。PaintOp 通过 `KisPaintExecutionContext` 获取 session，不访问 canvas 或全局 router。

## 13. Brush resource 与能力门禁

- `PreparedBrushProgram` 在 preset 选中时异步建立。
- begin stroke 时一次性决定 GPU 或 CPU backend。
- GPU program 未 ready 时，可以延迟该笔 GPU 执行或整笔走 CPU；策略必须可配置和可观测。
- Auto Round 不依赖外部纹理，应作为首个永远 ready 的 golden path。
- predefined tip、texture、mask 作为 immutable resource surface 进入统一预算。
- descriptor 不按 dab 或 frame 分配；使用稳定 ResourceSet 和延迟回收。
- shader 有字段、CPU 能解析 QImage 或资源上传成功，都不能单独构成 GPU 能力声明。

## 14. 可观测性与性能验证

每个 batch 至少记录：

```text
input/admission latency
journal backlog
compile time
page fault and restore latency
queue wait
GPU stroke timestamp
GPU composite timestamp
visible latency
page count / dab references / covered pixels
migration bytes
oldest outstanding sequence
```

验收必须区分 CPU 命令录制时间和 GPU timestamp。性能报告必须附带硬件、驱动、页面预算、
文档尺寸、图层结构、笔刷和输入脚本。

核心自动测试：

1. **batch partition invariance**：任意切分同一 dab 序列，输出一致。
2. **overlap ordering**：大量重叠半透明 dab 与 CPU reference 一致。
3. **page boundary**：跨页、大 dab、镜像和多目标不出现接缝。
4. **forced migration**：绘制中强制 VRAM/RAM/SSD 循环转录，像素与 generation 一致。
5. **no-drop pressure**：人为降低 GPU 吞吐，resolved dab 数量与执行数量相等。
6. **presentation isolation**：阻塞/销毁 swapchain 时 stroke 仍能完成并可恢复。
7. **undo-before-complete**：GPU 工作尚在途时撤销，最终状态正确。
8. **save snapshot isolation**：保存与新笔迹并发，文件对应捕获 generation。
9. **fault injection**：上传、SSD、提交和设备丢失不能静默丢失最后权威数据。
10. **validation**：无 queue ownership、layout、descriptor lifetime 和 in-flight reuse 错误。

首个性能出口不是一个脱离硬件的绝对 FPS 数字，而是：

- resolved dab 丢失数恒为零；
- UI/输入/stroke-end 热路径 host GPU wait 恒为零；
- warm working set 下 p50/p95/p99 输入到显示延迟可复现；
- 大笔尖通过 micro-batch 保持有界 GPU 占用；
- 正确性测试通过后再接受性能数据。

## 15. 与当前代码的取舍

可以提取并重新验证：

- `KisVulkanPaintOp` 的 Krita 输入适配和部分 dynamics 计算；
- `StrokePoint` 中已解析参数的字段设计；
- round/stamp shader 的数学逻辑；
- blend enum/mapping；
- transfer timeline 封装的接口经验；
- `KisStrokeJob` 与 transaction 的集成位置。

必须替换，而不是继续补丁化：

| 当前路径 | 目标路径 |
|---|---|
| 固定 2048 ring，满后丢 dab | 分块 `StrokeJournal`，无已解析命令丢失 |
| render thread 读取 ring 并逐 dab dispatch | `PageWorkCompiler` + page-batched indirect execution |
| brush compute 放在 acquire/present command buffer | 独立 `StrokeCompute` lane |
| 所有 dab 后只有一次 compute→fragment barrier | 页内有序 kernel + page-batch dependency |
| render thread 同步上传 brush texture | 异步 `PreparedBrushProgram` 和 resource ticket |
| `flushAndPause()` 作为 stroke end | End marker + `StrokeCommitTicket` |
| stroke end GPU→CPU tile 下载 | snapshot/journal + 按需 read lease |
| render/present 线程拥有所有 Vulkan 时序 | `SubmissionCoordinator` 统一 submission，present 只是消费者 |
| 全屏 decoration QImage 每帧上传 | 独立 overlay/脏区更新 |

最终校正版本中必须删除旧热路径及其开关、兼容适配和双重状态源。开发分支可以分提交建设新模块，
但进入新基线时不能同时保留两套可选的 GPU stroke 状态机。

## 16. 施工顺序

以下 `GS*` 只是 BR5 内部及其前置 reference 工作包。BR0 必须先删除旧 runtime，BR1–BR4 必须先冻结
PageStore、SubmissionCoordinator、replica 和 EvaluationEpoch；本文不构成另一条全局切换路线。

### GS0：协议与 reference executor

- 冻结 `StrokeEpoch`、`ResolvedDab`、journal chunk、PageJob 和 ticket 类型。
- 建立 CPU page-batched reference executor。
- 验证顺序、batch partition invariance 和 page boundary。

### GS1：SubmissionCoordinator

- 建立逻辑 lane、timeline ticket、依赖 DAG 和 deferred reclamation。
- queue 外部同步归一到单一 coordinator。
- 用 fake backend/validation tests 验证无 host wait API 契约。

### GS2：StrokeJournal 与 PageWorkCompiler

- 分块 journal、预算和 backpressure。
- CPU 稳定页面分桶与 cost-bounded micro-batch。
- 获取 PageStore lease、previous-writer 和 before-image ticket。

### GS3：UMA golden path

- shared canonical buffer page。
- Auto Round/Normal page-batched kernel。
- generation publish、dirty event 和 CPU pointer lease。
- 无像素 copy 的 undo/save 对照。

### GS4：独显与三层转录

- dGPU VRAM page、RAM backing、SSD restore/writeback ticket。
- 计算提交等待 transfer/sparse/direct-local binding publish。
- dirty safe eviction、device-loss replay 和强制小预算测试。

### GS5：增量合成与 presenter

- LowerCheckpoint/Target/Upper 分类进入 dirty propagation。
- DisplaySurface 按页更新。
- presenter 只显示已完成 generation；阻塞 swapchain 不阻塞 stroke。

### GS6：Krita transaction 闭环

- End marker、Recoverable commit、异步 undo transaction。
- undo-before-complete、redo、save snapshot 和取消。
- 删除 stroke-end 下载及 `flushAndPause()` 依赖。

### GS7：能力扩展与基线切换

- predefined/texture/mask/airbrush 逐项通过 capability manifest 和 golden test。
- 删除逐 dab dispatch、固定 ring、brush/render 耦合和双状态源。
- 完成 GPU stroke 能力矩阵；正常应用入口仍只能在全局 BR6/Tier 0–4 全部通过后启用，失败时整笔回退到成熟 CPU backend。

GS0–GS6 与虚拟纹理 VT1–VT7 共享 PageStore、ResidencyController 和 ticket，不允许再建一套
stroke 私有页面缓存或 transfer queue。

## 17. 首个 GPU Stroke MVP 验收门槛

必须同时满足：

- 完整 BR0–BR6 后正常 Krita 入口可触发，不依赖隐藏配置或手工初始化；
- Auto Round/Normal、单目标页与 CPU reference 在定义容差内一致；
- `SurfaceFormat` 身份完整，4/8/16 字节像素与不支持格式的 stroke-begin CPU 路由通过测试；
- 同页大量重叠 dab 的顺序正确，没有依赖未定义执行顺序；
- GPU stroke 与 swapchain/present 完全解耦；
- UI、输入、stroke end 无 host GPU wait；
- 已解析 dab 零丢失；
- UMA canonical page 无像素 staging copy；
- dGPU VRAM/RAM/SSD 自动迁移且 dirty page 不丢失；
- 当前目标、预测 halo 和可见合成页按语义温度管理；
- undo/redo/save/reopen 与并发新笔迹一致；
- swapchain 阻塞、资源压力、SSD 失败和设备丢失有确定行为；
- GPU timestamp、迁移和延迟 trace 可复现；
- 旧逐 dab/render-thread/stroke-end-download 路径从新基线删除。

没有同时达到这些门槛时，只能称为 GPU stroke 实验实现，不能作为后续高级笔刷和节点图的地基。
