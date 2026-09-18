# P0：Evaluation Graph、Projection、Derived Cache 与 Display

> 本文定义图像求值的长期中间表示和运行边界。现有 Layer Tree 与未来 Flow/ComfyUI 风格节点编辑器都是
> authoring frontend；两者必须 lower 到同一个 backend-neutral `EvalGraphIR`，不能各自建立 PageStore、
> compositor 或 Vulkan runtime。文件名保留旧 `graph_epoch` 仅为现有链接稳定，不代表继续采用 layer-only 模型。

## 1. 永久架构：三种图不可混同

```text
Authoring Graph
  Layer Tree / Flow Graph / imported workflow
        |
        | immutable snapshot + schema-specific lowerer
        v
Evaluation Graph IR (EvalGraphIR)
  typed ports / semantic operations / ROI rules / exact generations
        |
        | EvaluationPlanner + cache/capability resolution
        v
Execution Task DAG
  page/region jobs / CPU-GPU-external partition / tickets
        |
        v
PageStore + ValueStore + backend executors + publication
```

- **Authoring Graph** 是保存、撤销和 UI 编辑对象；可以是树，也可以是任意 DAG。
- **EvalGraphIR** 是不可变的语义 DAG；不持有 `KisNode*`、QObject、VkImage、queue 或 canvas。
- **Execution Task DAG** 是一次请求的物理计划；可因 viewport、缓存、预算和设备能力不同而变化，不进入文档。
- UI 节点不能直接生成 Vulkan command；Vulkan executor 也不能解释 Layer Tree 或 Flow 文档格式。

## 2. Surface 与通用 Value

### 2.1 Surface

每个 `KisPaintDevice`/frame 有独立 canonical surface：

- paint content；
- mask/selection canonical data；
- filter/clone 等节点自身的 canonical 参数或源数据。

canonical surface 由 PageStore 管理，不是 VkImage，也不由 canvas 拥有。ProjectionSurface、DisplaySurface、
checkpoint、LOD 和中间图像输出都是带 dependency identity 的 derived surface，可丢弃重建且不进入文档 undo。

### 2.2 非 Surface value

Flow 若需要 scalar、vector、color、text、metadata、tensor、latent、model reference 或 external artifact，使用
`KisEvaluationValueId/Version` 表达。非图像值由独立 Value/Resource Store 管理；禁止为了节点通用性把
PageStore 扩成万能对象仓库。

端口类型使用开放的 `typeId + semanticVersion`，因此未来 Flow/custom node 无需扩充核心类型枚举；封闭的
`StorageClass` 只区分 Surface、inline value、resource 与 external ownership，不承担节点语义。
Surface 端口同时携带逐端口 `SurfaceFormatId`；能力描述符匹配完整 input/output port signature，不能用一个
无位置含义的“支持格式集合”误判 format conversion 或多输入节点。

## 3. Authoring Snapshot 与 Lowerer

`KisAuthoringGraphSnapshot` 是带 `schemaId/schemaVersion` 的不可变输入，payload 不得含 native pointer。

```text
KisImage/KisNode Layer Tree -> KisLayerStackLowerer --+
Future Flow document       -> KisFlowGraphLowerer -----+-> EvalGraphIR
Imported external workflow -> adapter/lowerer ---------+
```

- `KisLayerStackLowerer` 是兼容 frontend，不是全局 planner。
- lowerer 必须完整表达 group、mask、filter、blend、animation、color semantics；无法证明时 fail closed。
- `.kra` Layer Tree 可长期保留；Flow 可包含 LayerStack 子图，Layer 面板也可成为受约束子图的专用视图。
- 第一阶段不冻结外部插件 ABI；先用内部、可版本化描述符和 CPU reference 固定语义。

## 4. `EvaluationEpoch` 与 EvalGraphIR

```text
EvaluationEpochId
DocumentId / GraphRevision
EvaluationContext(time/frame/LOD/working-space/policy)
Typed Node/Port/Edge descriptors
RequestedOutputs
MutationRootSet (optional)
PropertyGenerations
OperationId / SemanticVersion
Region/Purity/Determinism contracts
```

epoch 不可变。下列变化创建新 epoch：

- authoring topology、连接或 requested output 改变；
- node property、resource、seed 或 implementation semantic version 改变；
- animation time/frame、LOD、working space 或 display/evaluation policy 改变；
- writable target/mutation root 改变；
- 无法局部表达的外部编辑。

纯生成、查看或导出图允许空 `MutationRootSet`。绘画 stroke 自己仍必须声明非空 `writableTargets`，lowering 时将
对应 value 映射为 mutation roots。旧 epoch 的工作可以完成物理执行，但只有 epoch、依赖和 output reservation
全部匹配时才能 publish。

Authoring snapshot 中的每个 mutation root 必须精确引用一个 surface-backed canonical input；重复、悬空或
非 Surface root 一律拒绝。Lowering 后的 root 再指向该 epoch 对应的 produced value，避免 SurfaceId/ValueId
之间靠约定猜测。

## 5. 节点语义契约

每个 EvalGraphIR node 至少声明：

- 稳定 `OperationId + SemanticVersion`；
- 带开放 ValueType 与逐 Surface 端口格式的 input/output ports；
- immutable parameters/property generations；
- `Pointwise/Halo/Transform/Global/External` region policy；
- `Pure/Stateful/SideEffecting` purity；
- `Deterministic/Seeded/NonDeterministic` determinism；
- format/working-space requirements；
- CPU reference 或明确 unsupported 路径。

每个 node 都必须产生至少一个带 generation 的可追踪 output；真正 side-effecting node 也必须产生 receipt/effect
token，并由 requested output 显式触发，不能依靠“遍历到它就执行”的隐式副作用。

能力按 operation/version/value type/format 声明，不能用单一“GPU compositor supported”布尔值。未知 operation、
不匹配 semantic version 或缺资源必须 pending/unsupported/failed，不能当透明像素继续执行。

## 6. EvaluationPlanner 与 Execution Task DAG

`KisEvaluationPlanner` 只消费 exact EvalGraphIR：

1. 从 requested outputs 反向裁剪不可达节点；
2. 校验 DAG、port type、format 和 cycle policy；
3. 传播 dirty region、transform 和 halo；
4. 查询 exact derived cache；
5. 依据 capability 将任务分配给 CPU、GPU 或 external async executor；
6. 产生显式 task dependencies、output reservations 和 cancellation identity；
7. 再由 PageStore/ValueStore 解析 access plan 和 readiness tickets。

普通图只允许 DAG。需要反馈的工作流必须使用有明确 state/time 边界的 delay/state node，不能把隐式 cycle 交给
scheduler 猜测。

## 7. Layer Stack 是 lowering 优化，不是核心模型

现有图层栈可被 lower 为通用语义 DAG：

```text
CanonicalSurfaceSource -> mask/filter/style -> CompositeOp -> ... -> Projection output
```

在此 DAG 上，`KisLayerStackLowerer` 可以识别绘画时的线性结构并附加优化提示：

```text
LowerReadOnlySegment -> LowerCheckpoint
WritableTarget       -> changed target pages
UpperReadOnlySegment -> Overlay / Operator / Replay
```

多目标可形成 `C0 -> T0 -> C1 -> ... -> Tn -> Cn`。Lower/Upper 是 layer-stack-specific optimization，不能出现在
通用 EvalGraphIR 或 executor ABI 中；任意分叉、合流、多输出和共享子图仍由通用 edge/task DAG 表达。

未知/未证明的 upper 语义默认 Replay 或 CPU reference：

- backdrop-independent 内容才允许 Overlay；
- 可参数化应用到任意 backdrop 的内容可缓存 Operator；
- backdrop-dependent blend/filter/mask/group 保存 prepared inputs 并按脏区 Replay。

## 8. Derived Surface Cache

每个 derived page 的 key 至少包含：

```text
EvaluationEpochId
ProducerNodeId / OutputPortId
OperationId / SemanticVersion
Input ValueVersions
Input Surface/Page/Generations
PropertyGenerations
EvaluationContextDigest
Output Page/ValidRegion
ProducerTicket
```

常量 generator 可以没有 surface input，但仍必须携带 operation、parameter/context 和 output identity。cache hit 必须
逐项匹配；只比较“节点最近修改时间”、全局 dirty bool 或透明占位输出都不成立。

## 9. Dirty/ROI 传播与发布

canonical publish event：

```text
Value/Surface/Page identity
Old/New Generation
EvaluationEpochId
WriterTicket
ChangedRegion
```

scheduler 根据 node region contract 把 region 传播到下游。Pointwise 保持局部，Halo 扩张，Transform 做坐标映射，
Global 才允许全值失效，External 按其显式契约处理。每个 output page/value 只有在完整 producer 完成，且 epoch、输入
generation、semantic version 和 reservation 仍匹配时发布；过期结果直接丢弃。

## 10. Composite access plan 与 executor

`KisCompositeAccessPlan` 是一种 surface-specific operation plan，不是全局图计划。它携带 extensible
`operationId/semanticVersion`、exact input generations、output reservation、working format、page leases 和 tickets。

`KisVulkanCompositeExecutor`：

- 只验证并编码已支持 operation；
- 不读取 Authoring Graph；
- 不做全图调度或 capability fallback；
- 不自行申请 canonical authority；
- 不直接 publish derived output；
- 不持有或调用 raw queue。

CPU reference、Vulkan 和 future external executor 必须服从同一 output reservation/publication 规则。

## 11. Projection 与 DisplaySurface

`KisImage::projection()` 对应 EvalGraphIR 某个 requested output 的 derived ProjectionSurface/view：

- projection 从 canonical/value inputs 与 EvaluationEpoch 求值；
- writable target 保持自己的 canonical surface；
- projection 不 alias writable target；
- Canvas 不把 CPU projection raw bytes 覆盖 target GPU replica；
- GPU/CPU producer 都发布 exact output generation。

DisplaySurface 是面向 view 的进一步 derived output，包含 EvaluationEpoch、projection dependencies、display transform、
viewport/LOD、page generations 和 ready tickets。多个 canvas 共享 document evaluation/cache，但拥有独立 view transform、
DisplaySurface variant 和 WSI lifetime。

Presenter 只采样最新已完成 snapshot；显示/resize/surface lost 不阻塞 stroke 或 EvaluationPlanner。

## 12. Residency 与 CoverageCertificate

EvaluationGraph 提供的语义类别至少包括：

- writable mutation root/output：`CurrentWrite`；
- trajectory corridor：`PredictedWrite`；
- visible requested-output dependencies：`VisibleExact`；
- replay/checkpoint source：`ReplayOrCheckpoint`；
- undo/save retention：`UndoOrSaveRetention`；
- 被有效 derived output 覆盖的 canonical：`CoveredCold`；
- rebuildable output：`DerivedDiscardable`。

`CoverageCertificate` 必须包含 EvaluationEpoch、mutation roots、source/property generations、evaluation context 和
producer/replay route。通用图的空 mutation roots 合法；但证书仍必须证明被覆盖 canonical page 的完整依赖。

## 13. 交互与重型/外部节点

- 交互绘画任务使用低延迟、page/ROI 优先的 QoS。
- tensor/model/remote generation 使用异步、可取消、可恢复的 QoS。
- external node 不得让 presenter 或 brush host thread 无界等待。
- 非确定节点必须把 seed/run identity 纳入 generation/cache key；真正 side effect 不得由普通 cache replay 重复执行。

## 14. 实现路线

### EG0：接口与 reference

- `KisEvaluationGraphTypes`、authoring snapshot/lowerer、`KisEvaluationPlanner` skeleton。
- Layer Tree reference lowerer 与 CPU evaluator。
- source/diamond/fan-out/multi-output/random DAG tests。

### EG1：Derived surface/value core

- exact cache key、invalid/publish/rebuild。
- non-surface ValueStore contract；PageStore 保持图像页专用。

### EG2：ROI 与 mixed execution

- pointwise/halo/transform/global propagation。
- CPU/GPU mixed task DAG、unsupported operation fallback 和 stale completion rejection。

### EG3：Layer optimization 与 composite

- lower/target/upper optimization pass。
- overlay/operator/replay golden；page-batched composite access plan。

### EG4：Projection/Display

- projection requested output、per-page DisplaySurface publish。
- Presenter exact snapshot、多 canvas、color/display dependencies。

### EG5：Flow authoring frontend

- Flow serialization/undo/UI；与 Layer frontend lower 到同一 EvalGraphIR。
- 外部 workflow adapter 只通过 versioned operation/value contracts 接入。

## 15. 验收门槛

- Layer Tree 与等价 Flow graph 对 CPU reference 产生相同像素和 dependency identity。
- EvalGraphIR 支持 source、diamond、fan-out、多输出及空 MutationRootSet。
- property/input/time/format/semantic-version 任一变化都只失效正确下游。
- CPU/GPU/external 混合任务不能发布旧 epoch 或半完成 output。
- PageStore 不持有 model/text/tensor 等非 surface object。
- layer lower/upper 优化不出现在通用 planner/executor ABI。
- projection/display 不 alias canonical writable target；多 canvas 共享文档结果且 WSI 隔离。
- 旧 raw projection upload、NodeSync 整图路径和 layer-only global planner 不得恢复。
