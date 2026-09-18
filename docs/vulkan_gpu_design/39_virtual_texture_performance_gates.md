# 虚拟纹理性能模型、基准设计与决策门禁

> 本文规定如何把 32–38 中的可调参数转化为可复现决策。它不预设未经测量的性能数字。通用可观测性见
> [20_observability_testing_and_performance.md](20_observability_testing_and_performance.md)，CI 硬边界见
> [30_p0_ci_architecture_guards.md](30_p0_ci_architecture_guards.md)。

## 1. 原则

1. correctness、无丢失和线程边界先于性能比较；不正确方案不参与排名。
2. 使用端到端绘画 trace 决定架构可选策略，microbenchmark 只校准成本系数。
3. 报告 P50/P95/P99、最坏有界行为和预算，而不只报平均吞吐。
4. UMA、dGPU、SSD、图层剪枝分别测量，也必须在组合 workload 中验证相互作用。
5. 每个结果记录 commit、device/driver、OS、SurfaceFormat、文档和预算。
6. 未通过门禁的 capability 返回 Unsupported；不能用运行时静默 fallback 继续宣称支持。

## 2. 决策分层

### 2.1 已冻结、不再 A/B

- canonical PageVersion 和 replica set；
- lease/ticket/authority handoff；
- operation-scoped binding；
- fixed-slot slab 算法族；
- append-only segmented SSD；
- safety + semantic class + cost/history 温度框架；
- native sparse 为 optional provider。

### 2.2 需要 microbenchmark 校准

- CPU/GPU buffer load/store bandwidth；
- image sampling与manual buffer sampling；
- copy engine bandwidth/提交固定成本；
- host coherent/non-coherent flush/invalidate；
- codec encode/decode；
- SSD sequential/random/queue-depth；
- command/binding table publish；
- allocation/retirement metadata。

### 2.3 需要 trace 决策

- arena chunk size；
- batch byte/deadline threshold；
- predictor horizon/TTL；
- atlas promotion；
- high/low water和minimum residence；
- semantic prior/CLOCK hot target；
- SSD codec/durability group；
- per-document budget share。

## 3. 测试平台矩阵

至少覆盖：

```text
UMA coherent-like path
UMA non-coherent path or conformance fake
dGPU shared graphics/compute/transfer queue family
dGPU dedicated transfer and/or compute family
no-sparse device/path
sparse-capable optional path
low/medium/high memory budget profiles
SSD fast/slow and injected-latency profiles
```

无法获得真实硬件时，fake provider 可验证状态和延迟策略，但不能替代真实 UMA/dGPU 性能结论。

## 4. 文档/格式矩阵

- 4/8/16 字节及已声明支持的更大 pixel stride；
- 小画布高频笔迹、大画布局部笔迹；
- 稀疏内容和高覆盖内容；
- 单层、深图层栈、group/mask/filter/blend；
- 单目标与显式多目标操作；
- 大量 COW/undo generation；
- viewport zoom/pan/rotate；
- save/reopen 和后台 recovery checkpoint；
- 多文档、多 canvas。

每个 workload 固定随机 seed、输入事件、brush resource 和 CPU reference output。

## 5. Microbenchmarks

### 5.1 Arena/binding

- slot allocation/free/ABA validation；
- sequential/random page reads/writes；
- direct PageHandle vs local binding window；
- binding snapshot build/upload/publish；
- arena size与descriptor bank切换；
- metadata/fragmentation bytes。

### 5.2 UMA

- CPU iterator read/write；
- GPU read-modify-write；
- alternating CPU/GPU ownership；
- coherent/non-coherent atom ranges；
- BDA vs descriptor+offset；
- shared buffer vs copy-to-device buffer作为对照。

### 5.3 dGPU migration

- bytes/pages/regions per batch sweep；
- queue submission固定成本；
- upload/download双向并发；
- staging ring wrap和retirement；
- same/dedicated queue family；
- binding publish included end-to-end latency。

### 5.4 SSD

- raw/default/LZF 类型数据；
- encode/write/read/decode/checksum；
- queue depth与segment size；
- SessionSpill和RecoveryCheckpoint；
- GC live ratio/write amplification；
- cold read P95/P99。

## 6. 端到端 workload

### W0：稳定当前目标

持续在一个图层局部绘画，验证 current/predicted target 稳态无 domain-copy UMA、dGPU fault 收敛和笔迹延迟。

### W1：快速长线与方向突变

检验 trajectory corridor、deadline miss、错误预取和大笔尖 page set。

### W2：大画布 pan/zoom/teleport

检验 viewport 工作集、一次性扫描污染、local binding window 和不可预测 cold fault。

### W3：深图层栈目标绘画

检验 lower checkpoint、upper replay、CoverageCertificate 和非目标页降温。

### W4：频繁切层/属性/滤镜

检验 GraphEpoch 失效、derived rebuild、旧 coverage 拒绝和反向迁移。

### W5：Undo/save 并发

检验 generation retention、immutable save epoch、VRAM→RAM exact demand 和 SSD durability。

### W6：预算阶跃

运行中降低/恢复 VRAM/RAM/SSD 预算，检验 high/low water、reserve、writeback debt和ping-pong。

### W7：多文档竞争

前台 stroke、后台 save/GC、多个可见 canvas，检验公平性和 starvation。

### W8：故障

注入 OOM、device loss、short write、checksum corruption、取消和 shutdown。

## 7. 核心指标

### 7.1 Correctness hard gates

- pixel golden/checksum/generation mismatch：0；
- lost accepted dab：0；
- stale completion accepted：0；
- torn/partially committed ImageEpoch observed：0；
- authority released without valid backing：0；
- invalid derived dependency displayed/saved：0；
- validation error：0。

任何 hard gate 失败，该参数/策略结果无效。

### 7.2 Latency

- input sample -> journal accepted；
- journal -> PageJob ready；
- PageJob residency wait；
- submit -> writer complete；
- writer -> visible DisplaySurface；
- cold page fault；
- save/CPU lease；
- SSD read/write/GC；
- UI/input host waits（必须为 0）。

### 7.3 Work amplification

```text
uploaded/downloaded bytes / changed canonical bytes
SSD written/read bytes / canonical spill bytes
GC copied bytes / bytes reclaimed
derived rebuild pixels / visible dirty pixels
dispatch/submission count / page job
prefetched pages used / prefetched pages
reverse migrations / migrations
```

### 7.4 Capacity

- exact/derived/transient/reserved bytes by domain；
- metadata bytes per instantiated page/version/replica；
- logical/physical/padding ratio；
- retired-but-not-free bytes；
- OS/driver heap usage差异；
- SSD live/dead/slack bytes。

## 8. 成本模型校准

### 8.1 Replica source ETA

```text
ETA = queueDelayP95
    + codecP95
    + bytes / effectiveBandwidth
    + bindingPublishP95
    + contentionPenalty
```

系数按 device、direction、StorageClass、batch-size bucket 更新。策略使用稳定 EWMA/quantile，不直接追随单个异常值。

### 8.2 Atlas promotion

```text
Promote if:
populateCost + expectedReads * imageSampleCost + riskMargin
    < expectedReads * bufferSampleCost
```

必须使用完整 composite/display trace验证，包括 populate、gutter、dependency invalidation 和回收，不允许只比较 shader
单次采样吞吐。

### 8.3 Prefetch horizon

```text
H = materializationP95 + schedulerP95 + safetyMargin
```

以 deadline miss 与错误预取 bytes 的 Pareto 曲线选择，不以 hit rate 单指标选择。

### 8.4 Eviction

比较 semantic policy 和 age/LRU reference：

- current target deadline miss 不增加；
- cold fault P95/P99 降低或相当；
- reverse migration/write amplification 降低；
- 非目标 layer source 能在 valid coverage 下释放容量；
- metadata/CPU policy 开销有界。

## 9. 参数选择流程

1. 在固定 commit/hardware 上运行 microbench 校准。
2. 生成候选参数 profile，不直接写生产默认值。
3. 对 W0–W8 和预算 sweep 全量 replay。
4. 先过滤 correctness/hard-thread gates。
5. 对剩余方案比较 P95/P99 latency、amplification、capacity。
6. 选择非支配方案并记录 trade-off；需要设备差异时生成明确 capability profile。
7. 将 profile、原始 trace、脚本和结果一同版本化。
8. 驱动/实现变化超过定义阈值时重跑，不能沿用旧结论。

## 10. MVP 门禁

### 10.1 UMA

- W0/W1 稳态 `DomainSyncCopyBytes == 0`；
- CPU/GPU ownership golden 全通过；
- shared path 在完整 trace 中满足交互预算，不能只证明功能；
- derived display copy 独立统计。

### 10.2 dGPU

- 强制小预算完成 VRAM→RAM→SSD→RAM→VRAM；
- per-page/per-fault submit 为 0；
- dirty authority 无不安全解绑；
- batch/deadline policy在 W0–W8 无 starvation。

### 10.3 SSD

- SessionSpill/RecoveryCheckpoint failure matrix 全通过；
- GC 中断可恢复；
- cold fault和write amplification有可复现报告；
- disk full保持旧 authority并触发 backpressure。

### 10.4 Temperature/layer pruning

- `CoveredCold` 只来自有效 certificate；
- graph变更后 stale coverage接受数为0；
- 相对 LRU reference，完整 trace 不产生更差的 current-target deadline tail；
- budget sweep 无持续 ping-pong和文档 starvation。

## 11. 报告格式

每份结果至少包含：

```text
commit/build flags
device/driver/OS/queue topology
memory types and capability descriptor
document/format/layer graph
brush/preset/input trace id
VRAM/RAM/SSD budgets and watermarks
policy/profile version
raw event trace location
P50/P95/P99 metrics
correctness/validation result
comparison baseline
decision and rejected alternatives
```

禁止使用“感觉更快”“平均 FPS 更高”替代 stroke-to-visible、fault tail、迁移放大和 correctness 数据。

## 12. CI 分层

- Tier 0：state/policy simulator、record/layout、deterministic trace。
- Tier 1：软件/基础 Vulkan binding、codec、fault injection。
- Tier 2：真实 UMA ownership/copy counter。
- Tier 3：真实 dGPU migration/queue topology/heap pressure。
- Tier 4：完整 Krita W0–W8、undo/save/display、长时间 soak。

性能回归阈值在有稳定基线后按硬件 profile 建立；在此之前至少保存原始结果并阻止 correctness/thread hard gate 回归。

## 13. 完成定义

- 每个可调参数都能追溯到 benchmark/profile；
- 每项 capability有真实硬件证据或明确 Unsupported；
- microbenchmark和端到端trace均可复现；
- 报告包含 tail latency、amplification和capacity，不只均值；
- 所有 hard correctness gate 为零失败；
- 最终 profile 不改变 32–38 冻结的身份、状态机和接口边界。
