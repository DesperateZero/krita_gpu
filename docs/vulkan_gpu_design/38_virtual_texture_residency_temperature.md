# 虚拟纹理语义温度、自动驻留与预测方案

> 本文定义 ResidencyController 的选择算法。状态正确性服从
> [33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md)，GraphEpoch 与图层剪枝服从
> [28_p0_graph_epoch_projection_display.md](28_p0_graph_epoch_projection_display.md)。温度策略只能提出 operation，不能直接
> 修改 PageStore 或 provider 状态。

同类内部历史借鉴 [CLOCK-Pro](https://www.usenix.org/conference/2005-usenix-annual-technical-conference/clock-pro-effective-improvement-clock-replacement)
和 [ARC](https://www.usenix.org/conference/fast-03/presentation/arc-self-tuning-low-overhead-replacement-cache) 的低开销、
scan-resistant 思路；它们不替代本文的绘画语义和安全层。

## 1. 决策

最终算法由四层组成：

```text
Safety eligibility
    -> Semantic class
    -> Cost/value ordering with CLOCK-style history
    -> Budget/deadline/backpressure execution
```

不采用：

- 单纯 LRU/age；
- 一个可覆盖安全规则的全局浮点分数；
- 每次 dab 更新全局 priority heap；
- MVP 使用 ML 黑盒预测；
- 把 page 当成只能位于一个 tier；
- 因 derived cache 存在就删除 canonical data。

## 2. 策略对象

ResidencyController 管理的是 replica 保留价值和迁移意图：

```text
Page semantic state
Replica domain/state/cost
Budgets and watermarks
Deadlines and soft pins
Coverage certificates
Reuse history/ghost entries
Document fairness shares
Measured transfer/codec/rebuild costs
```

输出仅包括：

```text
Keep
Prefetch/materialize
Promote sampled replica
Handoff authority
Retire replica
Drop derived replica
Expire soft pin
Apply backpressure
```

PageStore/provider 对每个输出重新做安全校验。

## 3. Safety eligibility

任何打分前先排除：

- active write lease；
- active read lease 对应的唯一 physical replica；
- hard pin；
- in-flight producer/consumer；
- 未完成 transaction 的唯一 before-image；
- 未建立其他 exact backing 的 canonical authority；
- last-use ticket 未完成的 mapping/allocation；
- 当前 operation 必需且 deadline 已进入不可替代窗口的 replica；
- dependency 不完整但仍被显示/保存引用的 derived page。

对于唯一 authority，策略只能提出 `HandoffThenRetire`，不能直接列为 victim。

## 4. 语义事件

所有热度来自明确事件，而不是模块私自修改 age：

```text
StrokeEpochBegin/End
ActiveTargetSetChanged
TargetPageRequested/Published
TrajectoryPredictionAdded/Expired
ViewportEntered/Left
DisplayDependencyAdded/Released
GraphEpochChanged
CoverageCertificateCreated/Invalidated
UndoRetentionAdded/Released
SaveEpochCaptured/Released
CpuDemand/GpuDemand
ReplicaFault/Materialized/Retired
BudgetChanged
DocumentFocused/Backgrounded/Closed
```

事件包含 Page/Surface/GraphEpoch、deadline、reason 和 dependency generation。策略日志必须可重放。

## 5. Semantic class

从高保留价值到低：

1. `CurrentWrite`：正在写、已接受 stroke 的 base/output 和必要 before-image。
2. `PredictedWrite`：预测 corridor 内即将写的 target 页；soft pin，有期限。
3. `VisibleExact`：当前 viewport 精确显示/合成必需页。
4. `UndoOrSaveRetention`：未结束 transaction、undo 或 immutable save 引用页。
5. `ReplayOrCheckpoint`：lower/upper replay/checkpoint重建链上的页。
6. `ReusableCanonical`：近期重复访问且没有 coverage 的 canonical 页。
7. `CoveredCold`：被有效 derived 结果覆盖的非目标 canonical 页。
8. `OffscreenCold`：不可见、非目标、近期无需求。
9. `DerivedDiscardable`：有完整重建路径、无当前 reader 的 derived replica。

`CurrentWrite` 中 active lease/in-flight 仍由 safety 层禁止淘汰；class 本身不代替 pin。

## 6. CoverageCertificate

非目标图层快速降温必须有可验证证书：

```text
CoverageCertificate
  GraphEpochId
  ActiveTargetSet
  covered Surface/Page range
  lower/upper derived Surface/Page generations
  source dependency generation vector
  layer/property/mask/filter revisions
  valid viewport/region
  replay/rebuild route
  certificate generation
```

只有以下条件同时满足才标记 `CoveredCold`：

- 当前 epoch 内该 source 不在 ActiveTargetSet；
- derived result 精确覆盖需要的合成区域；
- dependency vector 与 source/property generations 相符；
- backdrop-dependent 内容有 replay/operator 而非错误透明 flatten；
- invalidation 能从 graph/property/frame/target 变化传播到证书。

证书失效只改变温度/合成选择，不改变 canonical source generation。需要 source 时按 exact generation materialize。

## 7. 同类内部访问历史

使用 CLOCK-Pro/ghost-history 思路，而不是精确 LRU：

- resident replica 保存 referenced bit、hot/cold class 和有限历史；
- 策略扫描候选时清 referenced bit并给第二次机会；
- 被回收 key 进入有上限 ghost set，不保留 payload；
- ghost hit 调整对应 semantic/domain 的 hot target；
- viewport 扫描或一次性 save 不应污染长期 hot 集；
- 每次访问只做 O(1) 标记，不移动全局链表/堆节点。

CLOCK 参数按 domain 和 semantic class 分离。例如 SSD/RAM history 不能直接驱动 VRAM atlas admission。

## 8. Cost/value model

通过测量的 EWMA/quantile 更新成本：

```text
RestoreCost =
    queueDelayP95
  + transfer/decodeP95
  + binding/rebuildP95

RetentionValue =
    reuseProbability(horizon) * RestoreCost
  + dirtyHandoffCost
  + rebuildCost
  + dependencyFanoutPenalty
  + deadlinePenalty

VictimValue = RetentionValue / physicalBytesFreed
```

规则：

- 在允许回收的最低 semantic class 中选择最低 VictimValue；
- canonical/derived、exact/auxiliary 分开计算；
- `dirtyHandoffCost` 不使不安全 authority 成为 eligible；
- `dependencyFanoutPenalty` 防止驱逐会触发大量上游恢复的关键 checkpoint；
- physical bytes 包含 padding/metadata份额，避免只按 logical bytes 误判。

不要求在线计算精确概率。初始 prior 由语义类给出，再用 ghost hit/miss 和 trace 更新。

## 9. 多域决策

同一 PageVersion 可有多个 replica，策略分别决定：

```text
Keep VRAM, drop RAM duplicate
Keep RAM/SSD, retire VRAM
Keep UMA shared, drop sampled atlas
Write SSD, then retire RAM/UMA
Drop derived without migration
```

不能把整个 page 简化成 `Hot/Warm/Cold` 单状态。Page semantic class 与每个 replica 的 domain value 是两组信息。

典型优先回收：

1. stale/无引用 derived；
2. 可重建 sampled/display replica；
3. 已有安全 backing 的 cold exact duplicate；
4. CoveredCold/OffscreenCold authority 经 handoff 后的源 replica；
5. 其他低价值 canonical replica。

## 10. Budget、水位与迟滞

每个 domain 和全局 session 有：

```text
hard limit
high water
low water
emergency reserve
minimum residence time
promotion/demotion cooldown
writeback debt
```

- 超 high water 启动回收；回到 low water 才停止。
- minimum residence 防止刚 materialize 即被逆向迁移。
- cooldown 针对同一 PageVersion/domain pair，压力越高可以缩短但不能绕过 safety。
- emergency reserve 不计入普通可分配额度。
- 外部预算骤降先取消 speculation/derived，不驱逐 current write。

## 11. 轨迹预测与 prefetch

### 11.1 输入

- 最近有序输入样本；
- velocity、bounded acceleration/curvature；
- brush conservative bounds、spacing、rotation/scatter 上界；
- selection/filter/neighborhood halo；
- current ActiveTargetSet；
- measured materialization P95。

### 11.2 Horizon

```text
H = clamp(
      materializationP95 + schedulerP95 + safetyMargin,
      configuredMin,
      configuredMax)
```

### 11.3 Corridor

预测有限时间内的 piecewise trajectory，并与 brush/algorithm halo 做 Minkowski sum，映射为 logical page set：

- target write 页生成带 deadline 的 prefetch；
- lower/upper dependency 只按实际 composite plan 请求；
- soft pin TTL 不超过 horizon + grace；
- pen-up、方向突变、target/graph epoch变化立即让旧 hint 过期；
- prefetch 不创建 generation，不获取长期 write lease。

预测 miss 只导致异步 residency wait/跳过中间显示帧，不能漏画。

## 12. Atlas admission

sampled atlas 只在预期复用覆盖建立成本时 promotion：

```text
ExpectedManualCost = readsWithinHorizon * measuredBufferSampleCost
ExpectedAtlasCost  = populateCost + readsWithinHorizon * measuredImageSampleCost
```

只有 `ExpectedAtlasCost + riskMargin < ExpectedManualCost` 且预算允许才创建。证据不足时保持 buffer path。

## 13. 多文档公平性

分配：

- 当前输入文档得到 latency reserve；
- 可见但非当前文档得到 display minimum；
- 后台 save/GC 有有界进度配额；
- 后台文档不能占用 current target emergency reserve；
- 单个超大文档不能无限挤出其他文档的最小工作集。

公平性不能把 active stroke deadline 降为普通 background，但必须防止 save/authority writeback永久饥饿。

## 14. Backpressure

按顺序：

1. expire speculative hints；
2. stop atlas/derived promotion；
3. drop DerivedDiscardable；
4. increase cold authority writeback priority；
5. reduce new GPU batch admission window；
6. expose pressure to StrokeCoordinator/journal；
7. 若硬资源仍不能满足，operation 显式 Pending/Failed并保留旧 generation。

禁止：覆盖 journal、返回空 page、释放最后 authority、UI thread 等待 SSD/GPU、无限增长内存。

## 15. Trace simulator

在接入 production 前，使用相同 event schema 运行离线模拟：

- 真实画笔轨迹/viewport/layer graph trace；
- synthetic scribble、直线、快速转向、随机 teleport；
- 图层切换、属性变化、undo storm、save；
- RAM/VRAM/SSD budget sweep；
- transfer/codec 延迟分布和故障；
- 多文档前后台切换。

比较 LRU、CLOCK-only、semantic CLOCK/cost。选择参数必须以 p95/p99 latency、迁移字节、fault、write amplification 和
correctness gates 为依据，不能只比较 cache hit rate。

## 16. 指标

- replica residency by semantic class/domain；
- safety-ineligible reason；
- ghost hit/miss；
- promotion/demotion/reverse migration；
- predicted page precision/recall 与 deadline hit；
- cold fault source/latency；
- CoverageCertificate hit/invalidation/rebuild；
- bytes freed per eviction operation；
- writeback debt；
- budget oscillation；
- per-document share/starvation；
- UI/input waits（必须为零）。

## 17. 实施顺序

### RT0：Event/schema 与 simulator

- deterministic policy input/output；
- LRU/CLOCK/semantic baseline comparison；
- trace replay。

### RT1：Safety/candidate API

- PageStore eligible snapshot；
- HandoffThenRetire；
- high/low water。

### RT2：Semantic classes/CoverageCertificate

- GraphEpoch/ActiveTargetSet；
- derived dependency invalidation；
- CoveredCold。

### RT3：CLOCK/cost

- ghost history；
- measured restore/rebuild model；
- domain-specific decisions。

### RT4：Prediction/fairness/backpressure

- bounded corridor；
- EDF hints/TTL；
- multi-document share；
- pressure integration。

## 18. 完成门槛

- safety 规则不能被任何 score 覆盖；
- `CoveredCold` 必须有有效 CoverageCertificate；
- page 与 replica 温度/价值分离；
- current target corridor 在正常预算下无可避免 cold fault；
- predictor miss 不影响最终像素；
- budget oscillation 不造成持续 VRAM/RAM/SSD ping-pong；
- 多文档无 starvation；
- trace 表明 semantic policy 在完整绘画 workload 上优于 age/LRU，且没有新增 correctness failure。
