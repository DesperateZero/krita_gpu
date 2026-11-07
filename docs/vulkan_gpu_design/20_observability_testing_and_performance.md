# 可观测性、正确性测试与性能门禁

> 本文定义什么证据可以支持“正确、无阻塞、性能达标”的声明。不存在 GPU timestamp、sequence accounting
> 和压力/故障测试时，不允许用 CPU 录制时间或主观手感替代。
> 全局构建图、禁止 API、旧符号、唯一 SSD 和 capability 守卫以
> [30_p0_ci_architecture_guards.md](30_p0_ci_architecture_guards.md) 为准；本文不能用性能测试替代结构守卫。
> 虚拟纹理的 workload、成本模型、参数选择和 UMA/dGPU/SSD/温度专项门禁见
> [39_virtual_texture_performance_gates.md](39_virtual_texture_performance_gates.md)。BR1 写侧 plan、backing handoff、复制分类和
> 硬预算的指标语义见 [68](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md)。

## 1. 验证顺序

固定顺序：

1. 协议与状态机正确；
2. 像素输出正确；
3. 同步与资源生命周期正确；
4. 迁移、取消和失败正确；
5. UI/host wait 审计；
6. 延迟与吞吐；
7. 功耗、内存带宽和长期稳定性。

任何性能结果都必须基于前四项通过的构建。缺少 barrier、丢 dab 或绕过回写得到的更高 FPS 无效。

## 2. Trace 数据模型

### 2.1 统一关联标识

每个事件尽可能携带：

```text
DocumentId
DocumentSessionId
EvaluationEpochId
StrokeId
BatchId
ChunkId
SequenceRange
OperationId
Ticket/Lane/TimelineValue
SurfaceId/PageId
Generation
ReplicaDomain
ThreadId
Timestamp
Result/Error
```

### 2.2 事件

```text
InputReceived
DabResolved
JournalAccepted/Sealed/Retired
BatchCompileBegin/End
LeaseRequested/Ready/Released
MigrationBegin/End
SubmissionQueued/Submitted/Signaled/Published
StrokePageWrite
CompositePageReady
DisplaySnapshotSelected
PresentSubmitted/Completed
SnapshotCreated
TransactionPublished
SavePageRead
BackpressureBegin/End
Failure/Recovery
```

trace 必须可在 release profiling build 以低开销 ring/stream 启用，并支持导出稳定格式。

### 2.3 性能比较上下文

性能 run header 必须携带以下上下文；事件引用 header/operation ID，避免每次像素访问重复构造记录。统一语义由
[39 的 5.6–5.9](39_virtual_texture_performance_gates.md#56-四类证据与基线配对统一定义) 定义：

```text
BenchmarkRunId / PairedBaselineId / WorkloadId / EvidenceClass(M,K,X,E)
SourceAndBinaryIdentity / MeasurementPurpose(diagnostic,qualification) / EvidenceStatus
SemanticScope / AdditionalSemantics / RequiredEndpoint
MetricScope(management-self,lifecycle-inclusive,resident-kernel,handoff-transfer,endpoint) / TimerBoundaries / Exclusions
Executor(CPU,GPU) / ReplicaDomain / PhysicalBackingDomain / AccessPath
HeapIndex / MemoryType / HostCached / HostCoherent / ResidencyEvidence
InitialExactGenerationValidReplicas / HistoryCowCondition
WritePlanMode / WritePlanFallbackReason / RecoverabilitySource
ReadWriteMode / PixelStride / LogicalWork / ActualPageWork(N,K,H)
CacheState / Threads / InFlightLimit / BatchSize / ArrivalSchedule / QueueDepth
ClockDomain / TimestampScope / InstrumentationMode / ProfileBudgetVersion
MRequiredBuckets / MRelativeAbsoluteMargins / MConfidenceLevelMethod
MPairedSamplingStoppingPlan / MRatioOrDifferenceBounds / MQualificationStatus
CounterOwner / CounterInterval / CounterExclusions / LivePeakCumulativeKind / DrainEndpoint
UmaMigrationApplicability / SharedAllocationExactBytesEvidence / LayoutResidencyEvidence
MeasuredHandoffCountDirections / PayloadMigrationCopyCountBytes / CopyCounterCoverage
BeforeImageCopyCountBytes / NewPayloadAllocationCountBytes / PayloadRetagCountBytes
BackingBytesCurrentRetainedPendingInFlightRetiringOptional / BackingBudgetHighHard
BackpressureCountDuration / ResourcePressureCount / RetirementDebtPeakDrain
```

`ReplicaDomain` 是逻辑域，不能单独证明物理驻留或访问路径；CPU/RAM、CPU/shared、GPU/shared、GPU/local-VRAM、
GPU/remote-host、CPU/BAR-mapped 分桶。不可观测物理流量/驻留填 N/A 或明确估算方法，不能按 UMA 标签推定零成本。
记录布局/算法差异及 prewarm/setup，确保 CPU/GPU、direct/VT 与 upstream 的配对可重建。
这些是报告必需信息，不表示当前 recorder 已实现全部字段；定义和结论判词统一引用
[39 的 5.11](39_virtual_texture_performance_gates.md#511-统一口径速查与报告判词)。目标、实现范围、已测诊断与资格状态分开写。
零迁移记录须同时说明交接次数、方向和计数覆盖，不能以未发生交接的零 counter 授予 UMA Pass；不适用/未测均写明原因。
硬件成本、软件管理与未归因残余遵守 39 的归因证据责任；新字段是报告契约，不表示 recorder 或公共 API 已经实装。

## 3. 延迟定义

必须分别记录：

- input-to-resolved；
- resolved-to-accepted；
- accepted-to-compiled；
- residency wait；
- queue wait；
- GPU stroke duration；
- stroke-to-display-ready；
- display-ready-to-present-submit；
- input-to-visible；
- stroke-end-to-recoverable；
- transaction publication latency。

不能只报告平均值。至少报告 p50/p95/p99、最大值、样本数和分布；长笔迹、首笔、冷页、资源切换、
多层和内存压力分别统计。

管理 API 延迟、驻留算子延迟和产品交付延迟是不同端点：M 是共同管理语义，K 是输入已就绪的真实算子，E 是完整
resident operation 或 CpuReadable/GpuConsumable/PublishedEpoch/Visible/Recoverable 端点；X 记录跨域与交接。
CPU-readable 必要读回不能排除，GPU-consumable 不强制读回，Visible 包含双方必要显示准备。present submit 不等于 visible。
吞吐按达到同一端点的有效完成量/墙钟统计，不能用提交速率或延迟倒数；与单操作延迟分别给出固定并发及饱和负载结果。

## 4. GPU 时间

- StrokeCompute、Composite、DisplayGraphics 使用 GPU timestamp query。
- 记录 timestamp period、valid bits、queue/lane 和校准方法。
- CPU submit/record 时间单独记录，不能命名为 compute time。
- queue wait 可通过 submission/timeline correlation 推导，并与 kernel duration 分开。
- query pool slot 按 last-use ticket 回收，不因读 timestamp 阻塞热路径。
- K 中包含 shader 实际 load/store、cache miss 和虚拟寻址；GPU remote-host 的跨总线等待也在 K，不能再加一份估算传输时间。
- GPU/VRAM 与主干 CPU/RAM 的 K 比值只表示异构驻留算子性能。VT 额外寻址成本要与同 GPU、同域 direct 控制组比较；
  CPU 管理开销则与主干 CPU/RAM tile 的共同语义比较。CPU 并行算子用 makespan 对照，thread CPU 总量单列。
- 同步/传输/barrier 作为单独阶段；timestamp 边界、queue overlap 和 host/device 时钟关联须保存，不能把等待全部叫 kernel。

## 5. Command Accounting

每个 stroke 必须闭合：

```text
resolved count
accepted count
compiled logical dab count
PageJob reference count
executed/no-op/cancelled/failed count
last accepted sequence
last executed sequence per target/page
```

不变量：

- accepted 不会无终态消失；
- page duplication 只增加 ref count，不增加逻辑 dab count；
- ring/journal pressure 测试中 resolved-to-accepted 差异必须由明确 admission/backpressure/cancel 解释；
- transaction sequence range 与 End marker 前 accepted range 一致。

## 6. CPU Reference 与像素 Golden

### 6.1 Reference

- 消费同一 StrokeEpoch、ResolvedDab、PageJob 顺序。
- 明确浮点/rounding/color/blend 规范。
- 产生 page checksum 和完整图像。
- 无 GPU 环境可运行。

### 6.2 比较

- RGBA8 exact 或按明确 blend rounding 规范比较。
- 4/8/16 字节像素、浮点/高位深按每通道定义容差和统计，不使用肉眼相似。
- alpha、premultiplication、colorspace 分别检查。
- 输出差异附带 StrokeId、sequence、PageId、pixel coordinate 和前后值。

### 6.3 Golden 场景

- 单 dab、连续重叠 dab、低 opacity/flow；
- page/microtile 边界；
- 镜像、旋转、aspect、subpixel center；
- 超大 dab 和长 list；
- batch 任意切分；
- resource sampling；
- indirect/neighbor stage；
- undo/redo/replay。

## 7. Property/State-machine 测试

### 7.1 PageStateMachine

随机生成：

- CPU/GPU read/write lease；
- upload/download；
- SSD write/read；
- generation competition；
- cancel/timeout/failure；
- pin/evict；
- late completion。

检查：唯一 authority replica（virtual default 另验精确恢复描述）、最后安全副本、新写 generation 分配高水位单调、publish/cancel lease 终态、SSD checksum commit、
derived page 不接管 canonical authority、in-flight allocation 不复用。

### 7.2 Ticket DAG

- 随机 dependency graph；
- 环检测；
- queue/lane remapping；
- completion 重排；
- submit failure；
- device lost；
- deferred reclamation。

检查任何 consumer 不在 prerequisite publish 前运行。

### 7.3 Journal

- 随机 chunk 边界；
- 极小 budget；
- producer/compiler/executor 不同速度；
- end/cancel race；
- recovery/retirement。

检查 accepted sequence 全闭合。

## 8. Vulkan/Backend 验证

- validation layer 无同步、layout、descriptor、lifetime、sparse binding 错误。
- synchronization validation 必须开启的 CI/本地层级明确。
- shader 编译只是最低门槛，还需 offscreen execution/output test。
- command buffer reset、descriptor free、staging reuse 都有 in-flight 压力测试。
- queue family ownership 在 dedicated/shared queue 拓扑下分别测试。
- 同一/独立 family、独立 compute/transfer/present queue 拓扑分别测试；Presenter 不得直接调用 queue API。
- UMA coherent/non-coherent 和 dGPU/sparse/atlas 组合覆盖能力矩阵。

Validation layer 未报告不等于 shader read-modify-write 语义正确，因此 overlap golden test 仍是必需。

## 9. Host-wait 审计

### 9.1 静态检查

对交互模块扫描：

- `vkDeviceWaitIdle`；
- `vkQueueWaitIdle`；
- `vkWaitForFences`；
- blocking timeline wait；
- condition wait 包裹的 GPU completion；
- UI paint/resize 中 pixel download。

允许调用必须集中在明确 teardown/debug/background consumer 文件，并有注释/测试说明。

### 9.2 运行时检查

- 给 UI、input、stroke worker、presenter thread 注册 role。
- blocking GPU wait wrapper 在禁止 role 上断言/trace failure。
- 记录 wait ticket、时长、调用点。
- swapchain blocked test 验证 stroke sequence/generation 继续推进。

“零阻塞”只表示指定交互热路径无 host GPU wait，不表示系统没有依赖或 CPU consumer 永不等待数据。

## 10. 性能工作负载

### 10.1 Warm steady-state

- 单层 Auto Round；
- 小/中/大笔尖；
- 多种输入采样率和 spacing；
- working set 全驻留；
- 记录 input-to-visible 和 GPU duration。

### 10.2 Cold/resource

- 第一次选择 preset；
- predefined/texture/mask 冷资源；
- pipeline/resource prepare；
- 验证首个 dab 不 host wait，整笔 policy 可观察。

### 10.3 Residency pressure

- 极小 VRAM/RAM；
- 轨迹持续进入冷页；
- viewport pan 与绘画同时；
- SSD restore/writeback；
- non-target pages 和 derived cache 竞争。

### 10.4 Layer/composite

- lower checkpoint 命中/失效；
- upper overlay/operator/replay；
- 多目标；
- 大 viewport/高 DPI；
- decorations 开关。

### 10.5 Adversarial

- 500px+ 大 dab；
- 同一页数千重叠 dab；
- 超长笔迹；
- 快速 preset 切换；
- undo-before-complete；
- swapchain 阻塞/resize/minimize；
- device/transfer/SSD failure。
- GPU 低功耗/热降频、CPU-fast + GPU queue contention；
- UMA CPU/GPU 共享带宽争用和 shared-mapping CPU access 退化；
- tiny workload/短笔迹，重复到成熟 CPU baseline 可稳定计时。

## 11. 性能指标

报告至少包括：

```text
input-to-visible p50/p95/p99/max
GPU stroke/composite/display duration
batch compile CPU time
queue/residency wait
PageJob/microtile/dab-ref count
bytes migrated among VRAM/RAM/SSD
journal/residency high-water marks
presented/stale/repeated frame count
backpressure duration
resolved dab loss（必须为 0）
CPU usage / memory bandwidth（可测设备）
power/thermal state（移动设备）
CPU-only / forced accelerator / Auto route p50/p95/p99/max
predicted CpuETA / AcceleratorETA / confidence / risk margin
route decision / profile freshness / realized regret / demotion
M paired management ns-per-op / ops-per-second / CPU-self / wait-hold / metadata bytes
K same-domain direct-vs-VT and heterogeneous RAM-Tile latency / completed throughput
X direction / copy bytes / cache-ownership cost / exposed critical-path time
E completed ops-pixels-logical-bytes per second / endpoint latency
physical traffic measured-estimated-N-A / setup / drain CPU-wall / retired backlog
M_time_ratio / M_throughput_ratio / K_local_time_ratio / K_heterogeneous_speedup / E_latency_ratio / E_throughput_ratio
```

性能门槛按目标硬件 profile 定义，不写一个脱离设备的普遍 FPS。每个 profile 记录：CPU/GPU、内存架构、
驱动、屏幕刷新率、页面预算、文档、图层、笔刷和脚本版本。CPU 基线必须是同机启用产品 SIMD/线程/COW/PageStore 的
真实产品路径，并先通过 52 的 upstream 差分门禁；scalar reference 或已退化 CPU 路径不能作为 accelerator 分母。

归因必须区分进程 wall、各线程 CPU、operation body wall、test/product lock wait 和采样 stack occupancy。多线程 body
wall/等待之和可以大于进程 wall；调用栈 inclusive 父子不能相加；采样中阻塞线程不算 CPU 热点。至少 5 次重复用于
median 与离散程度，P95/P99 使用足量事件/独立 replay 并说明样本量、不确定性和事件单位。禁止并发跑竞争性性能用例，
固定 seed 还须报告实际 page work，不能把调度造成的删除页数变化误当作锁伸缩性。BR1 的实证方法和图表见
[53_br1_performance_attribution_review_20260920.md](archive/br1_pre_m6_20260925/documents/53_br1_performance_attribution_review_20260920.md)。

必须同时交付 M 管理对照与 K/E 的吞吐、延迟对照，按 39 的统一比值方向、初末状态和 workload ID 整合。CPU/CpuRam
同义管理以主干等价或更优为目标，按 39 的 5.6 预先冻结相对/近零绝对容差、required bucket、置信水平、配对采样/停止规则；
管理时间比的单侧上界及独立完成吞吐比的单侧下界分别通过。报告 Pass/Fail/Inconclusive/NotMeasured，差异不显著不能证明
等价，完整操作 1.2×/1.3×/1.5× 上限也不是 M 容差。证据不足保持门禁未通过，不在看到结果后放宽预算。
只有实际新增对外语义且无主干同义项时给绝对成本预算，不伪造零分母或从 E 扣除；同义操作引入的 generation/proof/adapter
内部记账仍计入 M。不能用显存带宽优势冲抵管理回归，或用管理 microbench 代替产品性能。alias/default/no-op 的逻辑吞吐与
真实读写分列，不冒充物理带宽。GPU/UMA provider 的 host-side 管理须在实际路径补测；共同生命周期与主干配对，实际异构
执行新增 binding/proof/ticket 等工作单列预算，不能用 CPU bridge 的 M 结果代替。shader 寻址留在 K；同域 COW/default-fill
列为 E 数据准备子阶段，不漏记、不重复计费。

UMA 同一已驻留、布局兼容 backing 的零 payload migration 只对应 copy count/bytes；不能把 X、cache/order、queue/ticket
或全部额外耗时记零。CPU-only 无 GPU 交接时不应执行无用 GPU 协议，剩余软件冗余也不能直接归为“硬件事实”。

拆段至少覆盖 prepare、内容判断、proof/preflight、root 构造/发布、adapter 更新和 retire；互斥 self 与 inclusive 分开，
provider/CPU/GPU 异步事件用依赖关联，不对 P95 或重叠时长机械求和。细粒度埋点放在 opt-in、线程本地缓冲中并做扰动对照，
正式门禁关闭 profiler。回收挪到后台时同时报告 drained 总成本、积压峰值/持续时间，不把推迟到计时结束后的工作当消失。
固定负载测试应保留到达时间并覆盖过载，避免因测试等待完成才生成下一个事件而隐藏排队尾延迟。

切片证据更新遵循 39 的 5.10：记录源文件/二进制身份，将历史采样、当前结构断言和当前性能配对分开。
default 删除优化必须跟踪后续读/首写/prune/restore/purge/drain 的成本，不以迟后物化掩盖成本转移；残余耗时显式保留，
不预设 `E_VT - E_Tile` 全是硬件跨域开销。D1 当前结构/正确性、前后诊断及未取得同主干资格的边界见 54；旧 53 图表只解释原采样版本。
后续 D2 阶段 scope、固定 N/K/H 真写及扰动结果见 55；开启细阶段时钟的运行不能与无 profiler E 混用，短区间 CPU/wall 的
时钟端点成本不得解释为负等待。已知 no-op 与内容相同但缓存 miss 分桶，warmup 及冗余 canonical work 单列。
后续 D2-B 见 [56](archive/br1_pre_m6_20260925/documents/56_br1_prepared_metadata_publication_20260920.md)：preflight 已合并 write/default/removal，root 构造与最终
发布另分 phase，不能沿同名字段误作等端点 before/after。candidate、revision/claim/install、descriptor、GC/retire 均计入
总工作；直接 transition timer 与 prepared/installed publication counter 不混分母。保留初版局部慢化及修正版原件。
操作级抽样及完整 writeBytes 父/子区间见 [57](archive/br1_pre_m6_20260925/documents/57_br1_sampled_write_pipeline_and_immutable_directory_20260920.md)：
同一操作的嵌套阶段一起采样，日志保存周期/offset/真实 sampled count；父区间包含子区间，不能重复加和。
整体扰动变小不使 sampled 单次变成无扰动 self；关闭态不同 binary 也需校准，正式 A/B 冻结同一诊断接口和 harness。
报告同时区分代码/存储复用与管线同构，CPU-only 混合接入不因共用 TileData 就视为与主干完全相同。
counter 的 owner、临时 source/其他 manager 是否纳入、累计/终值/峰值及 drain 区间须明确；单 manager 的 default 物化为零
不是整个进程的零物化证明。已测诊断与正式资格分开标识，不再以全局“性能未测”覆盖局部新证据，也不把它升级为 M/K/E Pass。
此外 defaultMaterializationRequests 是语义请求计数，不覆盖新写 backing 内部默认填充；D3 确认 preserve 有 default-fill
再 source-copy（57），D4 已在支持 native 初始化的 preserve 路径消除该冗余（58）。这是版本化事实，不继续把 D3 的
填充归为 D4 当前热点。provider default-initialized/copied/adopted payload 工作量需独立计量，不能由请求为零推导额外 RAM 写入为零。

固定 fixture 的 `alias` 名称也不保证纯管理：D4 的交替 `clear()` 在 timed region 内生成 uniform source backing，
该初始化不在目标 provider 的 payload counter 内。操作总时长保留，纯 M 对照须另外隔离并配对共同管理语义；不以
provider 零值排除 caller/临时 source 的数据准备。`MetricScope` 必须来自实际调用链，而非函数名或用例名。

D5 同源主干对照见 [59](archive/br1_pre_m6_20260925/documents/59_br1_shared_upstream_cpu_baseline_20260920.md)：两侧只使用原生 tiles3 API，预备 alias source
移到计时外，但该操作仍含内容判断/提交，属于 E；暖 guard/lookup 属 lifecycle-inclusive，不冒充隔离 self。
窗口完成吞吐与固定-work、单次延迟分别存档，不能用 `1/rate` 填 P50/P95。若校准后的长桶会被累计 ticket/replay
记录增长混杂，应在配对前记录原因、预算及未执行项，另冻限时 rate 协议；不能静默缩短候选工作量、丢弃失败或授予原门禁 Pass。
不同 rate 完成量下的进程 RSS 不能证明每操作内存效率；补相同累计操作数的 active/pending/terminal/replay、root/history
与 drain 分项。manager destruction 不代表完整后台 drain，calling-thread CPU 接近 process CPU 也不证明窗口外工作为零。
保存实际执行的 driver 版本/hash、测试源码、构建 profile、实际装载库及原始结果；补充协议独立标识，不伪装成原批次。
59 已测 CPU 暖路径吞吐，但没有冻结正式 M 不劣性容差，固定-work、尾分位、H/并发/产品 E 和 GPU/UMA 仍未取得资格。

D6的完成记录研究见 [60](archive/br1_pre_m6_20260925/documents/60_br1_completion_coverage_and_sparse_terminal_status_20260920.md)：组件固定-work、真实操作
完成吞吐和全进程RSS分开报告。压缩需覆盖成功、永久pending gap、稀疏失败和高碎片终态；节点/记录减少不自动等于字节
减少。首轮区间不足100ms时保留原件、双方同步扩展工作量，不降低门槛。初版同状态区间的时间/RSS退化不能从证据中删掉。
已完成覆盖与具体终态允许不同物理布局，但每个ticket的状态必须精确；大量分散pending、非成功留存及drain继续单列。
组件约90%降耗而真实写吞吐仅改善约2.9%–5.5%，须据此校准优化排序，不能拿组件倍率解释整个PageStore或主干差距。

### 11.1 Native 初始化、payload 工作与抽样验收

下列为 native 初始化的计量契约，**不表示当前 recorder 已有全部字段**。D4 已接入 provider payload 计数及 prepare/transfer
子区间（58），后台 preclone/峰值 reserve/硬件流量仍未完整计量。字段名可由实现确定，含义和归属不可省略：

| 计量项 | 定义与边界 |
|---|---|
| default-initialized pages/bytes | provider 实际执行 default 初始化的目标页及逻辑写字节；包含为 preserve 写新建 backing 时的填充，不等于语义 default request 数 |
| explicit source-copy pages/bytes | provider 显式复制 source 的调用/页数、逻辑读写字节；同域 source copy 不属于跨域 X |
| native-duplicate pages/bytes | 由 native duplicate 初始化目标的页数/逻辑字节；可能来自预克隆，不直接当作前台 memcpy 字节 |
| adopted pages/bytes | 已有 immutable backing 的接纳/共享规模；不能当作像素复制量或物理带宽 |
| preclone work/reserve | 命中/未命中、后台预制与补充、未使用 clone、reserve 峰值及回收 CPU/wall；不能只记前台命中收益 |
| physical traffic | 硬件观测的 RAM/VRAM/link 流量，或注明方法的估算；不可观测填 N/A，不以逻辑字节代替 |

每项附 owner/provider、执行原因、线程和计量区间；所有已执行工作（含失败后丢弃的候选）进入累计量，成功发布量单列。
请求、分配、复制、发布、回收各有自己的分母，不能把 native duplicate 计数直接当 COW 次数或 generation 数。
同一物理动作的重复观测用关联 ID 对齐，不跨层重复加字节。改用后台预克隆时，预热、稳态补充与最终 drain 均保留。

对 `writeBytes → acquireWrite` 先保留既有父区间，再将其内部按管理校验/identity、allocation、payload 初始化、完成交接、
metadata transition 拆分；只在实际存在边界时计时，不靠相减猜测 allocator/复制各占多少。resident COW/default-fill 是
E 的数据准备子阶段，不混入 isolated K 或跨域 X；COW 决策、allocation bookkeeping 等管理工作不从 M 豁免。未拆开的
provider 区间保留 inclusive 标签及未归因残余，不将 acquireWrite 全段视为纯管理或全段归给冗余填充。

细分前先冻结同 ABI/同测量脚手架的 before/after，检查实际装载 library；新旧 recorder 关闭态的差异单列。
抽样以完整操作为单位，保存 period/offset/actual sample count，并检查周期混叠；必要时改用固定 seed 的随机选择。
同时校准空 scope、关闭态和稀疏开启态。子阶段数据只用于定位，不能据 overall 扰动较小便把被采单次当无扰动计时；
不得乘采样周期重建精确 E，也不将循环内事件当成独立进程重复。正式 M 不劣性和 E/尾延迟沿用 39 的独立冻结方案。

UMA 零迁移证据另须覆盖真实 CPU↔GPU 交接及同一 shared allocation/exact bytes；未交接为 NotApplicable、未计量为
NotMeasured。copy count/bytes 为零不令同步或总 X/E 自动为零，CPU-only 的这些 payload 计数不能授予 UMA 性能资格。
确认无迁移执行区间时记录“未执行迁移”，不合成 `0 ns`；已执行但低于计时分辨率的路径报告上界/分辨率而非严格零。
scope 内 identity lookup、backing pin/像素访问、scope capture/release 分别记录，避免仅消除查表锁便声称整条读路径免全局锁；
为相同操作建立/释放 scope 的成本保留在完整 M/E，retention/pin/last-use 保护不能作为测量前提被省略。

D7 的 identity lookup、capture/lookup/release 与完整 generic read session 必须按不同 scope 报告，见
[61](archive/br1_pre_m6_20260925/documents/61_br1_captured_read_scope_and_integration_cost_20260920.md)。旧 public retained API 的 manifest导出/full-scan释放属于该
scope比较，不得移植为原session的历史工作；新增capture成本仍留在操作M/E。该切片计量的是200ms独立完成吞吐及窗口
process CPU/完成量，不是单次延迟；source/loader、每操作generic request数和回收页数共同解释接通是否真正消除了重复工作。

### 11.2 Native read 接通后的测量契约

按 [39 的 5.12](39_virtual_texture_performance_gates.md#512-native-resident-read-的分层验收) 记录以下区间；此为待落实的
完整报告契约，不声明现有 recorder 已能采集全部字段。D8已有部分结构/完整暖读证据（见本节末），不因此标记全部分段已测：

| 区间 | 核心观测 | 不能混同 |
|---|---|---|
| capture | root/retention 创建、owner gate、scope 分配 | identity lookup；捕获一致性不是零成本 |
| resolve/bind | scope cache/root 查找、metadata shard、首次 provider lookup/初始化 | payload 冷页；驻留和 binding 冷暖是两维 |
| guard acquire/release | native/generic 选择、page-local gate、swap pin、读者计数、重试 | 全局无锁；共享引用不代替 residency pin |
| payload | 实际读字节/页、算子与访问域、page transition | 预绑定 isolated K 与整个 accessor E |
| scope release/retire/drain | unpin、root release、扫描/释放页数、CPU/wall、退休字节峰值/持续时间 | 仅析构返回、最后旧 root 回收及后台完全 drain |

区间可嵌套或由调用者交错执行，须按真实调用链保存父子关系和唯一 accounting owner，不把表的行机械相加。
阶段埋点采用 opt-in 操作级抽样并校准扰动；先报告长窗口和结构计数，短函数不足分辨率时批量测量，不盲目提高全程采样频率。
独立无 profiler 运行保留 capture 到 release 的完整操作；后台回收以单独 drain 端点补齐，不提前释放真实 reader 来缩短窗口。

每组报告至少补 `ReadScopeKind / PayloadResidency / BindingCacheState / ReadOutcome / FallbackReason / RetryCount`，
以及按 capture、首次 binding、暖 guard、scope cache、retire 分开的 allocation/lock 计数。结果计数以逻辑读为分母，
try/重试以尝试为分母，不重复计算同一成功读；generic request=0 只证明请求路径未执行，不证明没有访问、同步或分配成本。
unsupported-provider、binding-miss、busy、not-resident、producer/handoff-pending 分开；invalid/stale 单列拒绝结果。
若旧接口只返回空 guard，须先补可核验的诊断原因或标缺测，不能假定全部 miss 都是 swap-in/迁移。

最小诊断矩阵包括 K=1 与多页/重复读、首次与暖 binding、retained 历史/长 reader、最后旧 scope 释放、同页与异页竞争、
swap-out 与 generic fallback，并补真实写控制组以检测共享 provider gate 的间接回归。缓存扩容/record 建立、generic/native
交互与实际 scope/发布边界计入；后续正式样本量和容差仍按 39 的预冻结协议确定。
如果组件 lookup/guard 更快而完整 session 仍慢，先保留反证并复核 capture、cache 分配、fallback 比例和回收成本；不预设
全部差额来自锁等待，也不以新的术语、零请求 counter 或旧版本比例替代因果对照。

D8的实际覆盖见[62](archive/br1_pre_m6_20260925/documents/62_br1_native_resident_read_and_write_cost_20260920.md)：18个integration桶与5个原生控制桶各8对，
共184对/368次独立计时运行；另4次loader检查。新facade每次capture/cache/release在窗口内，payload/binding已暖；
session/accessor每页只触达一个字节，不能当作全页RAM带宽；rect包含实际完整拷贝与输出buffer分配，归为操作级E。
generic request的两侧预期为D7每页1次、D8为0，旧fixture的6个数量断言失败另存反例，不混作像素错误或丢弃样本。
单页/多页读收益与原生真实写下降2.3%–4.8%分别报告；不得以读倍率抵消写回归。当前状态枚举能表达部分native try结果，
不表示全部fallback/重试/锁分段计数已经采集。冷binding self、锁wait/hold、单次尾延迟、高H/并发性能、完整drain仍缺测。

后续eager/lazy缓存对照须在新证据目录预冻结协议：除暖读外，加入首次native访问、从不调用新读API的写/legacy控制、
相同累计工作量下的record/cache建立/销毁及峰值。把预建工作移到首次读属于成本位置变化，只有完整生命周期复测才能判断
净收益；保留共享read/write/transfer/retire gate。细分归因另做opt-in抽样并校准扰动，无profiler配对不与构建/测试并发；
未测得record、allocator或mutex的self时间前，只登记可检验假设。诊断通过、结构通过与正式M/E资格不得互换。

D9的实施对照见[63](archive/br1_pre_m6_20260925/documents/63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md)：新增generation-cycle的K0/1/16桶，
64页写入/发布→首次读取→释放，setup/close及configure→close窗口另报；原`lifecycle_ns`尚不含facade/provider容器析构，
不授予全部生命周期或drain资格。它混有真实fill/COW，不是纯M或孤立binding成本。
四个inclusive phase桶另做D9 plain/profile配对；其中一个约1.2%反向扰动，不能声称零扰动或用分段和重建精确E。
真实写改善、冷读成本转移、暖读/rect退化及直接D7残余分别登记。warm request=0不能证明暖路径没有新增handle初始化、
局部同步或内存布局成本；若需解释rect，须另分输出分配/清零、accessor与同域copy，不把其整个差额归给管理。
高H冷version查找、锁self/等待、单事件尾与完整后台drain仍未取得资格；768次运行数量不替代这些覆盖。

D10的已测补充见[64](archive/br1_pre_m6_20260925/documents/64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md)：

- 新增held-view guard，capture/root release/close在计时外，每操作K页pin/触达1byte/unpin；这是组件M诊断，不能替代
  capture→session release的完整读M/E。D9/D10暖K16 guard约5%–7%、完整session/accessor约4%的吞吐改善分别记录。
- 直接D8/D10宽格式/单页负偏移、首次K16 read scope时间比约1.63–1.73，以及直接D7真写残余分别保留；不以完整
  fill64/发布周期稀释首读成本，不把inclusive首读区间改称cold binding/局部锁self。
- 新共用fixture保留`configure_to_close_ns`，`destroy_ns`覆盖最终facade/provider容器析构；`lifecycle_ns`和相应process CPU
  止于实际析构完成，endpoint为`Facade-and-provider-containers-destroyed`。D9旧数据仍只有close端点，不补造缺失时间。
- 固定256cycle与>=200ms完成吞吐分别分析；固定-work总墙钟/CPU不叫持续吞吐或单事件尾延迟。每侧setup/close/destroy
  均单列，相同工作量配对防止把rate窗口完成量差误当回收效率。全局tiles3 pool/worker drain仍为NotMeasured。
- 新read binary仅用于D8+；直接D7只用兼容的旧native fixture。111个配对桶/1776次计时及28次loader不能替代未测维度。

### 11.3 环境变异与端点可核验性

当前 [67](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md) 的执行顺序为整体结构重构后再统一性能测试。

67 §10 的 packed read 迁移单列 `read_bytes_capture / read_bytes_page / read_bytes_release`：capture 包含 publication gate
协调和固定 View 建立，page 包含本页 native/control 获取、像素 memcpy 与归还，不是纯虚拟纹理管理 M 或纯 RAM 内核 K。
release 包含该操作最后 View 的归还；frozen overlay 的 K 项逻辑 token 登记/释放目前仍有同步工作，不能忽略或声称 O(1)。
记录 selector（动态单页 / captured committed / captured base / frozen sealed overlay）、sealed delta 大小、访问页数、
同时持有 pin 的峰值、generic request 与真实 fallback 原因。packed read 至多一个页 pin，不代表所有 accessor 已有相同上界。
默认页裁剪等嵌套提交的读取/像素比较与 packed read 分开归因；默认初始化、同域复制和比较不计为硬件跨域 X。
phase observer 可在页间注入发布用于可见性测试，此时 owner/backend publication gate 均未持有，但 data-manager read lock 仍在；
禁止重入同一 manager 的写锁。此类运行不得用作性能样本，最终需要 disabled/recording 扰动校准及完整 E 配对。

67 §11 将同一契约扩展到独立只读 H/V/random、wrapped/repeat peers 与 planar read：每个 iterator cursor 至多 4 对 pin，
同一 exact current/before 只 pin 一次；wrapped 最多 4 个独立 cursor 共用一次逻辑选择，不把“每 cursor 上界”写成“每操作 4 页”。
planar 追加 `read_planar_capture / read_planar_page / read_planar_release`，page 包含像素拆平面与页访问/归还，
输出平面分配仍计入完整 E，不能用该区间代表纯 M 或已分配 RAM K。空区域不捕获 View。
另列 `live-legacy-writer-overlap` 路径：同线程仍有旧 writer 时保持旧读语义；它没有 immutable View 资格，
不能与驻留 native/control fallback 合并，也不能只挑无 writer 微基准声称全部生产贯通。
新增回归检查跨 commit/abort、default 变化、淘汰/reset、包裹循环、异线程读和仍存活的裸写指针；
语义与结构计数通过不授予主干性能资格。真实 brush/dab 的捕获/发布边界及直接 tile 借用仍需独立覆盖。

67 §12 的 `activeControlWritePages / activeCpuWritePages` 记录活跃按页预约；准备尚无 request 时也须计入，
释放 provider access 前不得清零，关闭后必须为零。`writePageClaimChecks / writePageClaimConflicts` 分别统计
首写/删除的按页冲突探测及命中；同段重复访问不重复首写探测。它们不是 physical claim、COW、in-place permit 或锁次数。
固定 K、扩大无关 request/lease 数 R 的计数只证明冲突检查不扫描全局 map；不能外推 metadata 历史 H、abort、
owner wait/hold、proof/commit 或整段 E 的复杂度。另测同页冲突与不同页并发、准备前后 metadata 变更、失败重试和最终关闭。
semaphore/phase observer 的确定性交错与故障注入属于正确性证据，不能混入主干 M/K/E 吞吐或尾延迟样本。

67 §13 将 native 未发布页的驻留改为 guard 生命周期。`writablePinsAcquired/Released` 是成功 guard 的目标 pin 计数，
`maximumPinnedPagesPerSegment` 是终结段峰值的累计最大值，不可对两个快照相减来求后一个段的峰值。
这些数在局部累计、seal/cancel 汇总，运行中未归还的 guard 不会提前计入；不能当作即时全进程 RAM pin 仪表。
source/oldData、metadata logical pin、额外 legacy pin 和 CPU access session 的全 span 保活分别统计，
目标 writable pin 为 1 不等于整次操作只有一个物理 pin，更不等于总 dirty backing/记账大小为 O(1)。
`write_writable_pin` 包括首次/再次局部 pin；NonResident 后切到 `write_pending_materialize`，后者是 owner gate 外的
tiles3 同步 swap 恢复；`pendingWriteMaterializations` 计恢复尝试，不等于实测 I/O 次数或 bytes。
两个阶段是 write_acquire 子区间，禁重复求和；新增 pin/unpin、控制恢复及最终 drain 均计入 E，RAM/SSD 事实分别标注。
只是减少长期 pinned 页，不授予性能提升、异步通用物化或 GPU/UMA 资格。结构验收须同时包含真实换出、保留 bytes、
同 generation/COW 次数、parked 排他、borrowed pointer 寿命和生产 writeBytes/memento，而不是只检查新 token 可构造。

67 §14 增加显式访问寿命维度：`OperationSpans`、native `CursorPage`、generic 写 cursor 分开报告。
native cursor 当前 target/before-image 各至多一个 guard；generic 的 before/read pin 可以归还，但所有未发布 write leases
仍随 dirty 页增长，不能归入同一个“单页工作集”指标。readRect/writeRect 的页块优先遍历应使每个相交页只借用一次 target pin，
并验证同页多行/像素不重复进入 session；另测同页重访、真实换出、失败换页、旧 View/default 与 OperationSpans 长寿命。
这些工作次数不是耗时或吞吐；实际收益需连同 pin/unpin、页块寻址、源 before-image、临时 buffer、发布/回收一起测 E。
CPU SurfaceOps/line facade 与其他 tiles3/brush 生产入口覆盖范围单列，不把 facade 的通过外推为全部产品迁移完成。

67 §15 的 production planar/trim 需同时检查 session 数和每页 generation/COW/seal/pin 数，而不是只看 root commit 数。
同页多个裁剪带应共享一次准备；整页删除和空/全缺失 channel 操作不做像素工作。原 kernel 的平面合并/填充 bytes、
compatibility wrapper/租约、allocated-page 枚举与索引重建都保留在完整 E；不以零 generic write request 推导零管理成本。
owned transaction failure 与 caller-history 已 sealed/staged delta 的保留分开验证，不能声称 markFailed 回滚整个 history。
坐标资格按 canonical PageStore 与所选 legacy index 分开；产品范围外必须前置拒绝，不以 SAFE ASSERT 后 detached tile 的
像素正确性充当支持证据。合法边界/越界拒绝两组同时保留，修复前“Qt totals 全过但有 SAFE ASSERT”的日志不算通过。

67 §16 的 canonical mutation 另验证私有删除/像素混合操作：删除暂存、provider 锁外准备、seal/cancel/proof 失败及并发 capture；
真实 trim/clearAll/removePages 故障后保留 prior history 与外部 writer。metadata capability 的第二页 revision 失配不得先安装第一页；
旧 prepared 版本转 Historical 后仍可被已有 View/read lease/pin/last-use 访问，实际释放另由回收判定。
67 §17 补齐 private alias 及 fill/clear、PageStore copy：序列复用、provider/proof 故障、后页冲突、源图像复制中途发布、
default/current/before/rough 与 1/4/8/16 BPP 都必须覆盖，旧 View、caller history 和外部 writer 不得被取消。
另测源 raw tile 的 live write intent/已暴露 pointer：旧共享观察分流与 immutable copy 分开；history old-source 不误走 live。
保留 low-memory hangingTilesTest 原指针、COW、swap 断言；复制入口按访问范围检查 wrapper intent 的额外 O(K) 成本纳入 M/E。
非法 alias 在 private batch 中被拒绝后，显式 finish/析构必须取消本段；验证 owned/history 都不会提交先前私有删除。
计数用 `operationSessionsCreated` 与 CPU-only 的 `sessionsCreated` 区分纯语义段，`removalsSealed/Cancelled` 不计像素 work；
`activeMutationPages`（旧 `activeCpuWritePages` 为兼容别名）不等于 writable pin。删除后复用 pending 的 `pendingDefaultResetBytes`
是额外必要软件初始化，和 provider 首次初始化按不同事件相加，不计硬件跨域 X。metadata mutation 安装与 epoch publication 安装分别计数。
本轮 owner 内准备/复验、旧版本转 Historical 后的回收和完整操作成本仍在 E，不能用“原子安装成功”替代短发布/主干不劣性证据。

67 §18 将 mutation seal 私有 metadata/proof/detach 准备移出 owner 后，必须验证：provider 阻塞不阻止无关页提交；
准备期间捕获完整旧 overlay；同事务兄弟段按键合并不丢 delta；迟到 View、read lease 取得/释放不丢保护、不反复构造候选。
紧凑 detach delta 全部取得短 claim 并复验 exact Prepared/transaction/无 writer 后，只修改当前 publication/preparedBy；
以完整状态机逐字段比较准备后新增 capture/lease/last-use/handoff pin 的 16 种组合。第二页真实 writer 冲突必须整批拒绝。
provider proof、adoption、COW、generation 不重复。收尾锁外释放输入/私有容器，仍保留 claims；
新捕获者在此时看到完整新 overlay。`sealMetadataPreparations/Rejections` 分别统计候选构造及准备/安装拒绝，
与 root publication 计数分开。并发成功率/失败率、失败清理和最终 drain 都须进入后续 E/尾延迟分布。
首轮 full snapshot + 8 次重试在正常读者 churn 下出现 4 次失败，保留 `full-*` 反证；不能只凭完整套件一次通过验收。
`mutation_seal_*` 的 owner_wait/inputs/private_publish/proof_prepare/metadata_prepare/publish_owner_wait/install/cleanup
是顺序业务阶段；inputs 的 alias 子调用会解锁，失败 install 含取消，尾部 owner_wait 含少量 claim/stat 收尾，不能直接充当纯锁持有分布。
`write_publish_host` 是 inclusive 父区间，嵌套 provider/alias 计时不重复求和；精确 owner wait/hold 与后台工作仍需独立采样。
§18 的紧凑语义合并只用于 mutation detach，不修改下文 root commit/restore 的严格 revision 复验及重试口径；不是 wait-free 或硬时间预算。

67 §19 的真实 painter bitBlt 验收须经过生产调用链，不能只直接测试新 accessor：current source 使用 rawDataConst，
明确 old-source 才选 oldRawData，selection mask 始终读其 current View。第二个实际块前更新 source/default/mask，
必须断言注入执行、旧捕获输出稳定及新 accessor 可见更新；并测 history、wrap/offset、live writer 与重叠 self-copy。
各 owner 的固定 View 不是联合原子快照，确定性交错不是多线程/TSAN。整数逐字节比较；F32 同一 kernel 的连续 oracle
与分块产品结果逐分量检查有限性及 float epsilon × max(1, abs(expected)) 上界，保留原 exact-byte 失败和量化差值。
不得为了绕过 const 契约恢复只读 rawData 的可写权限。目标 legacy accessor 的非空检查不等于整操作失败原子性。
新增 `painter_bitblt_prepare`、`painter_source_resolve`、`painter_composite`、`painter_bitblt_finish` 仅由 unfiltered
product recorder 归集；单 owner recorder 仍记录其嵌套管理步骤。resolve 包括 source/destination/mask 移动与参数准备，
workItems 是块数；composite 的 workItems 是像素数，但区间还含循环边界计算及可能的 mask 析构，不能直接当 K。
finish 含 dirty rect 和剩余 accessor 释放，不是全部发布或后台回收端点；fast-copy 留在 prepare 内。
相位 observer 的注入写也计入 instrumented 时间，嵌套 commit/mutation/provider 区间不可与其相加。
最终须另测纯 kernel/self、关闭/开启扰动、完整 E/drain 与硬件存储事实；只读接通不授予 painter 写段迁移或 M/K/X/E 资格。

67 §20 的实际 bitBlt 目标迁移必须另验 native 与已有 borrower 两条路线，不能混成一次整操作原子性结论。
目标专用 cursor 不暴露 before-image；1/4/8/16 BPP、history、同页重访、wrap/offset、极值坐标、超范围后再次合法移动、
后页 canonical 冲突、主动取消均需验证首写/generation、pin、generic request、旧/新 View、undo/redo 与下一操作无泄漏。
反序目标范围的并发必须实际到达 native range wait 后再释放首操作，覆盖首操作成功与取消；不得降级到逐 tile 发布。
同线程重入拒绝不能被目标集中另一 legacy borrower 掩盖；已有 batch 内拒绝发生在加入匿名事务之前。
额外验证共享匿名事务：外部 legacy client 持续存在，先成功 seal 一段，再取消另一私有段，最终此前成功页与外部指针修改
必须保留。新操作/既有 CPU batch 均覆盖；修复前 `client-negative-*` 的两例丢数据/SAFE ASSERT 保留，不能忽略断言算通过。
仅已确认的私有取消可健康归还 client，错误仍返回失败；无法证明取消的失败不豁免 transaction abort。

新增 `pixel_operation_range_prepare/wait/body/finish`，prepare 只含 backend 去重、预约、事务/mutation/布局准备；
此前 DataManager 的目标矩形扫描、wrapper 探测、第一份去重和 m_lock 等待尚未隔离，仍归 painter prepare/E，不能算成零成本。
重复 wait 后的 prepare workItems 为重查范围，不能累加作 unique 页。wait observer 入口持 registry mutex，只可发信号；
实际 wait 释放它并包含唤醒后重取。body 不持该 mutex/DataManager 锁，但内部仍有 canonical 局部协调，不得称整管线无锁。
body workItems 为操作数；finish 为 touched 页，包含 callback 后 seal/client finish、范围归还和私有对象销毁；
callback 前失败收尾留在 prepare。finish 不含外层索引更新前 m_lock 等待或 `mutation_index_refresh`。
本轮 painter finish 扩展至 callback 返回后的终结/索引刷新，仍非最终后台 drain；不得沿用 §19 范围直接对比阶段倍率。
全部相位 inclusive，不将父子时间相加，composite 仍非纯 K。951/9 passed 与 240 次重放是正确性检查点，不是性能采样。
未迁移 producer、内部 write-plan/handoff、完整 owner 临界区和总 backing/回收预算继续开放，最终保持同义主干 M、
同域驻留 K、硬件 X、完整 E 分离配对。

67 §21 的生产 metadata 布局以完整 reference 状态机为 oracle：局部转换须逐字段比对 header、writer、handoff、全部版本、
replica、captured token、lease/pin/last-use 和退休 effects；序列后半失败不得安装前缀。历史 slot 冲突必须覆盖不同 allocation
generation/domain，slot 真正回收后重用不能被陈旧索引拒绝。并发 capture token、诊断快照稳定性、真实旧 View/abort/close 均单独验。
新增用例发现完整 reference 误禁多事务独立 Prepared：`invariant-negative-*` 的 152/1 失败与同期生产 326 passed 保留；
修正后活动 writer/slot 唯一性、foreign Prepared read 拒绝、root 冲突及败者保留的 captured 版本仍须通过。

`localTransitionSequences/localVersionInputs/localVersionInstalls` 只数局部投影，`mutationBaseVersionInputs` 含首写与 proof 的
精确版本输入；均在已有 shard 锁内累计、冷查询汇总，不增加跨 shard 共享原子计数。失败计输入但不计安装；这些不是 unique 页、
hash probe、字节复制或全部 M。`transitionDecisionNanoseconds` 不含局部输入构造/索引安装，不能当完整 owner/shard hold。
`fullSnapshotExports/fullSnapshotVersionInputs` 记录明确完整导出（控制转换、root/restore、GC、diagnostics 都可能贡献）；
`backgroundSnapshotExports/backgroundSnapshotVersionInputs` 是其中后台回收子集，不能与总数相加，也不能把后台工作移出 E/drain。
真实 1/4/8/16 BPP × 0/7/63 段的局部输入 3、安装 4、exact 输入 3/5/5 和前台完整导出 0 是结构计数，
不证明完整提交/GC/内存与 H 无关；reference exact lookup 的 4095 历史门禁同样不替代产品 E/尾延迟。
新 trackedPayloadBytes 包含 exact/slot 索引逻辑字段，仍不含完整 allocator/hash/list node 开销；跨布局不能沿用旧 ABI 常数。
最终计时必须把索引维护、fallback 及全 snapshot 的可能回退算入，不预设每个小 H 桶必然更快。

67 §22 扩展到生产 root 发布：候选按 current/target/own Prepared 与 mutable/slot 见证投影，安装仅改 publication 字段；
完整 oracle 必须覆盖独立事务 Prepared、不选最新 own Prepared 的拒绝、旧历史槽位冲突、活动 writer 与保护状态。
严格 revision 拒绝、多页无前缀安装、晚到 reader/last-use/completion 与 root/directory/retention 重做门禁继续运行。
缺失默认版本恢复须验证：候选构造期间 live version 数不变；新事务导致失败不留预检安装；成功后 descriptor 在 root 前就绪。
H=0/7/63 × 1/4/8/16 BPP 的真实提交/恢复分别为版本输入/安装 2/2、3/2，所测前台整页导出为零，旧 View/close 均验证；
这是限定子链的结构证据，不是完整 E/H 独立性或主干等价性。普通完整 restore/default 目录仍计 headers N。

新增 `publicationVersionInputs/Installs/Removals` 分别记录候选输入、delta/新增（fused 为保留记录安装）和 fused 移除；
`publicationFullSnapshotPages/FusedBudgetDeferrals` 分开记录完整捷径和预算拒绝；
`publicationLookupVersionInputs/DirectoryHeaders` 记录 owner 预检输入。失败/重做候选照计，不能当 unique 页数或除进旧 decision timer。
单页 fused 32 条记录预算须验证 32/33 边界，超预算在完整导出前回退普通提交，不能变成事务失败；后台 GC/drain 不得从 E 扣掉。
trackedPayloadBytes 同时计入 prepared/mutable 索引逻辑字段，仍不等于容器实际分配/RSS。
新默认/hash/descriptor 插入、临界区协调与候选销毁仍可耗时/分配；完整计时需重新测相位、自身开销和小 H 回退，
不得从这些计数宣称整个发布零分配、全局无锁，或把 RAM/显存差异混入 M/K。

67 §23 的后台历史枚举须分别验证单页上限 32 与每 pass 历史输入上限 512（16 keys），不能只验页数。
reference 覆盖 H=0/31/32/33/511/4095、删除游标记录、default revision 与重启；历史/Prepared discard 逐项比较全状态及退休效果集合，
包含 token、lease、pin、last-use、外来/重复 identity、非 superseded/foreign Prepared 与活动 writer；失败不得安装部分记录。
真实 H=65/257 × BPP=1/4/8/16 的旧 View 保留/最后 pin 释放/回收/close，及 provider barrier 之间恢复旧 generation 再写，
验证 head 缓存失效、游标前插入需要 repeat、最终无遗留 history/cache 和正确像素；候选/生产两类证据不可替代。

`historySliceQueries/VersionInputs/maximumHistorySliceVersionInputs`、`historicalGcVersionsVisited/maximumHistoryVersionsPerPass`
只数历史输入；`historyReachabilityRefreshes` 另数刷新，刷新内 root 遍历和单记录保护列表的时间仍须测。
67 §26 增加 `historyReachabilityRootsVisited`：累计上述 worker 刷新实际查询的 distinct **admitted roots**，每次同一 root 只算一次。
不是 root tree node 数、token 数、物理 registry 数、总 GC 工作或 wall time；`immutableRoots` 仍含未销毁退休 roots，二者不能互换。
验证须在不运行 collector 的情况下扩大退休 root 数，确认只查询固定 current/合法保留集合；另扩大合法 R_live，承认其必要成本。
snapshot 与 active-base 重叠、重复 token/current 去重、最终 snapshot release/事务终结与新接入的先后及竞争均需覆盖。
在真实 owner 阻塞后台 collector，确认旧 epoch 不能复活，同时旧 View/native guard/generic lease 仍按各自保护读到正确像素；
generic lease 仅保护 exact replica，不授予整个旧 epoch 的历史访问。失败 metadata install 和 retained restore 不能绕过准入。
扩大退休积压后，必须观察到物理 root 队列尚未清空时已有 provider retirement，而非只验证 drain 后的终态；
每轮 root/finished-transaction 候选各 32 与 history 16×32 分别记账，旧队列屏障不能隐藏为调度等待成本。
67 §27 的内嵌退休链接须覆盖 1/33/513 个 epochs、hash 增长与 reserved-slot erase、重复 root 入队、事务 FIFO、
零/小/批量预算及两类队列任意先后收集；metadata callback 拒绝不能产生候选退休条目或提早终结事务。
current/protected root 的检查和最后保护释放后重新入队须单独验证。无额外 queue/dedup 分配是限定结构事实，
不得外推 metadata 安装、completion、worker 调度、完整提交或 E/drain 免分配/无锁；固定链接字段的内存成本必须保留。
同一 head 下接入仅能增加已可达 root 的保护计数，不能扩张 root 集合；最终保护释放触发保守缓存重扫。仍须实测 R_live 刷新、
动态保护列表、队列积压及完整 drain 的 CPU/时间/内存预算，不从固定 root 查询计数推导 M/K/X/E 性能通过。
`activeHistoryScans/cachedHistoryReachableVersions` 是派生缓存 debt，不是逻辑所有权、实际内存字节或 RSS。
`localVersionRemovals` 单列退休移除；`backgroundLocalTransitionSequences/VersionInputs/VersionInstalls/VersionRemovals` 与
`backgroundMutationBaseVersionInputs` 是相应总数子集。GC 已使用 local 通道，前台首写断言必须取 total−background，
完整 E/drain 仍包括后台 CPU、缓存构造/析构、root 刷新和物理退休，不能删窗口或把子集再相加。
新增 ordered history 索引逻辑字段进入 trackedPayloadBytes，allocator/map node、owner 可达性缓存与队列另量，不假称该数是总内存。
构建失败后的旧二进制 PASS 不算新增实现证据；本轮 `indexed-*` 明确排除，重新构建的 guards/final 与源码 hashes 才有效。

67 §24 的 packed native write 使用完整范围保留、一次业务 View、逐页 no-op 比较和直接 mutation guard。
验收需区分完整覆盖零 source copy 与 provider 仍有 default initialization；不能只验 nativeDuplicatePages=0 就称零准备工作。
1/4/8/16 BPP、history/full/partial/no-op、padding/负坐标、后页冲突取消、旧 View/undo、共享 client、borrower、范围等待和
DataManager 并发读都必须覆盖。正常写体不持有 DataManager 锁，不等于 PageStore/binding/swap 全无锁。
`packed_write_capture/compare/prepare/copy/release` 嵌套于共用 `pixel_operation_body`；range prepare/wait 与 finish 仍用
`pixel_operation_*` 名称。native `write_bytes_body` 已包含整个生命周期及 commit，`write_bytes_batch_finish` 包括重新取
DataManager 锁和派生索引刷新；不能把新旧分桶直接相减，也不能累加父子 inclusive 时间。
compare 的解析/pin、prepare 的 allocation/default-fill/COW 均不属纯 memcpy K；完整 M/K/E 保留它们，软件源复制不是硬件 X。
业务 View 与成功 changed-key 刷新的额外派生 View 分开统计；零 generic request 不替代整个入口的管理等价证明。

67 §25 将正常 packed 整页写改成同步完整输入初始化。新增 `payloadInitializedPages/Bytes`（fresh provider work，含失败后丢弃），
`pendingPayloadCopyBytes`（pending/fallback CPU copy，seal/cancel 汇总），不得混入 default fill、before-image COW 或硬件 X。
生产 full page 应恰好一次 payload 初始化、零旧页 copy、零 default fill；partial/default preserve 的必要初始化不得为了过计数被跳过。
整页 allocation+input copy 现在位于 `packed_write_prepare/write_provider_prepare`，`packed_write_copy` 仅含 partial 行复制；
`mutation_payload_copy` 测 pending/fallback 复制，不含此前 pin/真实 swap-in。不能拿旧 §24 copy 桶直接推算性能变化，所有父子区间仍 inclusive。
验收覆盖带 padding 与末行最小 buffer、负/溢出布局、调用后输入改变、不保留 alias、default/resident/removed、direct/fallback、
旧 View、真实 swap/reload、同段复用与 cancel/commit；provider 声明能力后失败必须取消，不能用 fallback 隐藏故障。
prepare 中独立 capture/提交以及 abort/close 拒绝须实测；provider 返回前已完整初始化的保证还须核对 allocator 在 register 前复制的代码顺序。

§17 新增 `aliasGenerationsReserved`、`aliasPagesSealed`：前者是纯 alias 新 generation，后者是最终 alias keys；native
`generationsReserved/pagesSealed/Cancelled` 保留实际 native preparation 口径。write → alias 可同时进入 native 与 final-alias
两类，禁止相加当 unique 页数。uniform cache/input 的构造、保留及销毁需另计入 K/E/内存，provider adoptedBytes 只是逻辑引用。
新增 `copy_prepare/copy_source_page/copy_finish`、`fill_page`、`mutation_alias_prepare`、`mutation_source_initialize`、
`mutation_index_refresh` 的 nested inclusive 区间不能直接相加；`write_publish_host` native workItems 为 distinct claimed keys，
含 removal/alias，不等于 payload 或 root commit。关闭/开启扰动及性能归因需重新校准，不复用旧相位定义得出提速结论。
变化页刷新使用额外 post-publication cache View；业务固定读 View 与注入写操作自己的 View 分开计数。计时 observer 只在显式
`next()` 边界触发；“未实际注入 source 更新但复制正确”不算并发通过。显存/RAM 和 M/K/X/E 定义不变，软件 copy/adoption 不计硬件 X。

67 §16.5 将“影响可见版本的 provider operation”和“已 detached 的 retirement acknowledgement”分开验证。
公开 `providerOperations` 包含两者；恢复阻塞判断用单次 ledger 锁内的 blocking count，不能先后采样相减。
延迟退休确认不得使无关 undo/redo 随机失败；close 必须能轮询此前保存的退休 operation，不能被其自身债务永久拒绝，
也不能在非终态/失败时报告关闭成功。测试需同时保留旧 View、default/resident、完整/稀疏恢复、后台/关闭首次退休，
验证不重发 retire、非退休 operation 仍阻塞、总债务最终归零。保留偶发和确定性修复前负样本；一次重跑变绿不是豁免。
该分类不是免除回收开销：排队、后台执行、完成等待、重试与最终 drain 仍整合到 E，不计作已消除成本或硬件 X。

67 §9 的回收迁移进一步改变端点：在 tiles3 CPU opt-in 配置中，`CommitHistoryCollect` 主要记录候选入队，
`CommitProviderRetire` 主要记录 binding 撤销/物理退休入队，不能再将这两个前台区间当作完整历史评估或 provider 退休耗时。
后台历史任务、首次物理退休和 persistent-tree continuation 必须单独归因，并与 enqueue、等待/drain、峰值债务一起整合到 E。
现有 TLS recorder 不会自动把另一线程的回收归入提交者；正式性能测试前须补齐后台 trace/CPU 采样，不用前台缩短值代替整条管线收益。
结构检查记录每批 root/transaction 候选、history pages、replicas、tree reference drops，区分合法 retained 历史与 pending/blocked/in-flight 债务。
`waitForRetirementIdle()` 只等待已调度历史/首次退休；失败或 pinned 债务仍须有界重试/完成通知，最终 `closeSession()` 还需全部退休成功。
数量批次不证明单页版本评估、owner 等待、单次 provider 调用或总队列积压具备硬时间上界。
过程中的 QtTest 用时、结构计数与失败复现仅用于正确性诊断，不生成新的主干性能判词。
2026-09-21 提交准备外移后，`CommitProviderValidation`、`CommitEpochDeltaPrepare`、
`CommitTransitionPreflight`、`CommitEpochPrepare` 分别记录锁外 provider proof 验证、事务 delta 准备、metadata 候选评估、root 构造。
`CommitInputOwnerWait` 和 `CommitPublishOwnerWait` 分别是准备输入与安装前回到 owner 的等待；`CommitPublicationRevalidate` 是 head/retention/目录复验；
`CommitMetadataApply` 包含所有页面 revision claim/安装，`CommitRootPublication` 才是 root 可见性切换。
`CommitProofValidation` 的 owner 侧输入比对、`CommitDefaultRemovalPreparation`、`CommitTransitionInputs` 与后续历史整理仍不能漏算。
restore 单列 `RestoreTransitionPreflight`、`RestorePublishOwnerWait`、`RestorePublication`；最后一项不是整个 undo/redo。
`publicationStatistics()` 区分 root rebase、retention/metadata/页目录重做；所有失败候选及重试都属于实际工作量，不能只记最后成功尝试。
并发重做不具有固定次数或等待上界，必须测竞争条件下完整 E 的尾延迟；不能将“准备锁外执行”表述成 wait-free 或发布成本已达标。
最终计时须绑定新阶段边界，不能直接拿旧 `CommitRoot` 数字推导“短发布”提速。
私有诊断 phase observer 只用于确定性交错测试；启用 observer 的运行不得进入性能样本。
native mutation、legacy unlock 段、operation batch、root commit 继续分别计数。
共享 default 的 cache 存量与 guard 保留的全部 live bytes 分开，累计 default buffer 构造/初始化 bytes 进入软件数据准备成本。
失败退休债务与合法历史/CPU pin/last-use 分开；测量必须包含重试与最终释放，不以 metadata 已移除计为 backing 已回收。
原生等待局部 gate、实际非驻留和 unsupported fallback 分开归因，不能把全部非 Ready 归为物化/跨域传输。

D11 生产写段的测量边界与反证见 [65](archive/br1_pre_m6_20260925/documents/65_br1_native_cpu_mutation_segment_20260920.md)：`write_acquire` 在 native 路径
覆盖 beginWrite/reserve/binding，`write_provider_prepare` 是其子区间；`write_publish_host` 改为一次 native 段的 seal，
workItems 为 dirty 页数，不能把其 intervals 与旧 per-lease publish 数量直接比较。`write_resolve=0` 只证明不走该通用入口。
固定 N/K/H/BPP 的 generation/seal/copy/commit 计数与独立完整 E 同时报；计数下降、K16 提升不抵消 K1 回归。
CPU-only prebound RAM memcpy 为 K，guard/intent 仅是对应管理动作的 M 代理，真实 scanline write 为 E；不得把 E-K 差额
全部解释为纯管理或硬件跨域。upstream 与候选同源 fixture 可分别编译，必须检查头文件/inline ABI 和各自实际库。

本节是后续测量契约，不宣称历史harness已记录全部字段。D10保留原始结果和诊断地位，不因补写契约取得资格。

D12物理claim前置切片见[66](archive/br1_pre_m6_20260925/documents/66_br1_physical_exclusivity_prerequisite_20260920.md)：claim未被生产owner消费时，测试关注
既有路径引入的成本与安全性，不把它预期成已消除COW的提速。inline lifetime-ref协议变化要求各版本fixture分别编译并使用
匹配runtime；源文件相同不能授权交叉装载。physical claim成功/失败与owner permit/原位页数是不同计数，禁止混报。

- workload随机种子、统计bootstrap种子、容器hash种子是三件事。记录测试进程实际hash seed/配置及其采集方式，
  不由当前shell、只记环境变量或workload seed反推；未记录标Unknown。每侧同时记录allocator/相关配置、warmup与
  payload/binding冷热状态、并发后台活动或其观测缺口。代码/ABI/库身份不替代这些运行时条件。
- 大区间或负偏移先保留，再提出可证伪假设。可另冻结固定hash seed/布局的benchmark子进程诊断，与默认生产配置
  独立进程重复并列；不得改变生产hash策略求跑分、事后筛选有利seed或把单个确定性布局当产品不劣性证明。
  若增添记录/埋点会影响布局或关闭态，两侧共用兼容harness并校准；不得篡改旧protocol后重解释已采样数据。
- pooler有后台工作路径不证明测量时发生了干扰，未观测活动不证明静默；查明CPU/调度/资源归属前，不把差额指派给它。
- endpoint必须对应实际代码位置及完成条件。operation release、close、facade/provider容器析构、最后旧root释放、
  全后台drain分别标识；不能仅凭`lifecycle`/`destroy`字段名推定覆盖。资源峰值与积压持续时间另测，不能由单次终值推导。
- rect等混合路径分配/清零、访问管理和payload copy分段可用于归因；完整无profiler E独立保留。优化初始化须保留
  padding/失败时可见性等原语义，不能用删去对外承诺或不同初末状态制造收益。
- 结构迁移报告须列真实生产入口与fallback覆盖率。现有操作batch、tile publish/proof与root commit分别计数，不能把
  它们混为同一次提交；同页重复写按未发布段记录generation/allocation/COW/request/proof/commit，不能按history名称合并。
  新facade microbench不替代生产writeBytes/accessor的同源upstream M/K/E及生命周期对照，下一切片契约见52第12节。

## 12. 回归门禁

合入新基线前的硬门禁：

- `kritavulkanbackend` 不链接 `kritaui`，target graph 无环；
- queue submit/bind/present 只有 `SubmissionCoordinator` 一个源码/二进制 owner；
- global router、旧 stroke-end download、固定 fallback canvas 和第二套 Vulkan SSD store 不存在；
- resolved dab loss = 0；
- overlap/batch partition/page boundary golden 通过；
- 强制 VRAM/RAM/SSD 迁移 checksum 通过；
- UI/input/stroke-end/presenter 更新路径 host GPU wait = 0；
- swapchain blocked 时 stroke/transaction 推进；
- undo/save/cancel/device-loss 测试通过；
- 多文档、多 canvas、关闭其中一个 canvas 测试通过；
- 4/8/16 字节像素和不支持格式的前置 CPU 路由通过；
- EvalGraphIR 随机 DAG、Layer/Flow equivalent lowering 与 derived dependency generation 校验通过；
- validation/sync validation 通过；
- CPU-only、forced GPU/UMA、Auto 同输入同质量对照通过 39 的 CPU-relative 门禁；GPU 劣势 profile 下未达标 bucket 在
  首次写入前整操作 CPU route，不能以 GPU timestamp、零拷贝或 correctness `Supported` 代替；
- 当前阶段适用的 M/K/X/E 证据、同域 direct 控制组及 RAM Tile 比对齐全；混用 executor/domain/endpoint 的管理倍率判无效；
- CPU 同义管理所有 required bucket 通过 39 的独立不劣性判据；不得以阶段操作上限、无显著差异或 M 成本重分类代替；
- latency 与完成吞吐均通过预先冻结的 profile，未测项填 NotMeasured，不把 CPU-only BR1 测量当作 UMA/dGPU 性能证据；
- p95/p99 不超过目标 profile 已批准预算；
- 无未解释 latency spike 或 generation mismatch。

性能优化若破坏任一正确性门禁，不得以 feature flag 保留为可选路径。

## 13. CI 分层

### Tier 0：无 GPU

- dependency graph、public header、forbidden API/symbol 和唯一 SSD store 守卫；
- schema/journal/state-machine/property tests；
- PageWork compiler/reference；
- transaction/save generation tests；
- documentation/link checks。

### Tier 1：软件/基础 Vulkan

- shader compilation；
- offscreen Auto Round output；
- ticket/resource lifetime；
- validation layer。

### Tier 2：UMA

- shared canonical page；
- coherent/non-coherent cache；
- CPU pointer bypass；
- input-to-visible benchmark；
- shared CPU access 对 native CpuRam，以及 CPU-only/forced UMA/Auto 的劣势 profile 对照。

### Tier 3：dGPU

- transfer/sparse/atlas；
- dirty eviction；
- VRAM/RAM/SSD stress；
- queue topology；
- cold/tiny/queue-contended/低功耗下 CPU-only/forced dGPU/Auto route 对照。

### Tier 4：产品场景

- 完整 BR0–BR6 后的正常 Krita 入口；此前入口必须保持关闭；
- undo/save/reopen；
- 多文档/多 canvas/关闭、图层随机变化、viewport/decorations；
- color/display filter、SurfaceFormat 和 truthful LoD/capability；
- 长时间/功耗/热状态。

## 14. 实现路线

### OT0：事件与 trace schema

- 稳定 id/correlation。
- 低开销 recorder/exporter。
- current code facts 可先接入，但不得把旧指标当验收。

### OT1：Reference/golden harness

- CPU PageJob executor。
- offscreen Vulkan executor/readback。
- per-pixel/page diff。

### OT2：State/property/fault harness

- fake backend/ticket scheduler。
- completion reorder、failure、device-loss。

### OT3：GPU timing/latency

- query pool/timestamp。
- input-to-present correlation。
- p50/p95/p99 report。

### OT4：CI 与 profile gate

- UMA/dGPU device matrix。
- reproducible scripts/documents/presets。
- baseline storage 和 regression threshold。

## 15. 验收门槛

- 每个性能结论可追溯到构建、硬件、脚本和 trace。
- CPU recording 与 GPU execution 指标名称/数值分离。
- 每个 accepted sequence 有终态 accounting。
- 自动测试覆盖正确性、同步、迁移、transaction、present isolation 和故障。
- “零阻塞”由静态与运行时 wait audit 支持。
- 性能门禁在正确性全部通过后执行。
- correctness capability 与 performance qualification 分开；产品 Auto 相对真实 CPU 满足 39，forced accelerator 结果不冒充
  产品通过。
- 文档中的完成状态与 CI/运行证据一致。

### 15.1 发布准备计数的解释（2026-09-21）

BR1 增加 `publicationHistoryNodesPrepared/Transferred` 与
`publicationReplacementRecordsPrepared/Installed`，用于证明可移交 history node 与 fused record-set 的工作是在准备还是安装阶段发生。
失败/取消候选允许只有 prepared 无 transferred/installed；成功值按实际 record 数记账。指标不代表分配器调用、内存字节、锁等待或
wall time，也不能与 RAM/VRAM/UMA 的 M/K/X 时间混算。对应正确性矩阵见
[67 §28](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#28-2026-09-21metadata-候选持有发布所需存储)。

本检查点只运行 correctness；benchmark consumer 虽重建但未采样。任何“短发布更快”“CPU 对主干不劣”或 GPU/UMA 产品路由结论，
仍须按 39 冻结硬件、存储域、端点、样本与停止规则后另行验证。

### 15.2 新增 record 准备计数（2026-09-21）

`publicationAdditionRecordsPrepared/Transferred` 记录缺失 exact default 的 owning record node 在候选准备与成功安装中的数量；它与
existing-version history node 及 fused replacement set 分开。失败、取消或 foreign candidate 允许 prepared 增长而 transferred 不变。
hash capacity 的安装前后不变由断言覆盖，但该指标仍不代表 Qt allocator 调用或锁等待；descriptor 也不在其范围内。
正确性证据见 [67 §29](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#29-2026-09-21新增-default-record-的候选存储与容量准备)。

### 15.3 descriptor 准备与重做计数（2026-09-21）

`descriptorCapacityPreparations`、`descriptorInstallations`、`descriptorRepreparations` 与
`restoreDescriptorRepreparations` 分别记录候选容量准备、成功安装和解锁期间语义变更造成的重做。capacity 不增长有运行时断言；这些仍是
结构计数，不是 allocator call、hold/wait 或端到端耗时，不能与 metadata record 指标重复相加成“节省时间”。见
[67 §30](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#30-2026-09-21descriptor-容量准备与解锁期变更复验)。

### 15.4 publication cleanup 相位口径（2026-09-21）

[67 §31](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#31-2026-09-21publication-cleanup-所有权移出-owner-gate)
把已消费 metadata candidate 与 fused 旧 record-set 的析构移到 PageStore owner gate 外。`CommitCleanup` 因而可作为“owner 已释放”的
结构断言点；它不是后台回收时间，也不是纯管理 M。当前 `clear()` 仍同步发生在完整操作返回前，其 CPU/wall/destructor 工作必须留在 E。

后续引入预算队列时要分别报告：入队记录/字节、每批实际销毁数/字节/CPU/wall、队列峰值、等待时长、背压及最终 drain；不能只把前台
锁等待下降称为总成本消失。此次仅跑 correctness，没有产生可与 upstream、RAM/VRAM 或 UMA/dGPU 比较的新性能样本。

### 15.5 metadata cleanup 队列与 host completion 口径（2026-09-21）

[67 §32](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#32-2026-09-21分批-metadata-cleanup-与预完成-host-evidence)
将大于 8 个 candidate-page units 的 cleanup 送入单线程 reclaimer；每 pass 最多 16 units，并在 unit 之间检查 1 ms 协作预算。
`metadataCleanup*` 统计区分候选、unit、pass、pending/peak、pass time 与 queue sojourn。unit 不是 record/byte，1 ms 也不是单 unit 硬上限；
这些后台数值属于完整 E 的回收相位，不能从 M/K/X 中扣除后称为跨域成本。

host-logical completion 现为 configure 时建立的单一已终态证据；`allocatedTickets==1` 证明同步热路径不再按操作增长 registry，不能解释为
只发生了一次业务操作。GPU/CPU-job/I/O source 仍逐次计数。此次仍只有 correctness，没有产生新的 upstream/UMA/dGPU 性能资格结论。

### 15.6 write-plan、backing 与零冗余复制口径（2026-09-21）

[68](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 要求每个 first-write 记录最终计划模式：
`ReusePending/HandoffRecoverable/HandoffCommitOnly/FreshPayload/FreshDiscard/FreshCow/SemanticOnly`。未选择 handoff 时记录单一首要 fallback
原因和必要的次级诊断，例如 retained root、active base、exact reader、alias、last-use/in-flight、cancelable/fallible、claim conflict、
budget pressure 或 provider unsupported。selector 尝试数不能冒充成功数；调用方不可自行上报“独占”。

“zero-copy”禁止作为单一通过指标。报告至少分开：

- `beforeImageCopyCount/Bytes`：为保留旧值而复制的 payload；
- `newPayloadAllocationCount/Bytes`：本次写新取得的像素 backing；
- `payloadMigrationCopyCount/Bytes`：跨 domain/heap 的 payload 搬运；
- `payloadRetagCount/Bytes`：同一 allocation 经 owner handoff 绑定到新 generation，只计身份转移，不计为复制；
- `payloadInitializationBytes`：default/full-input/partial-preserve 实际初始化，不能藏在 allocation 或 migration 下。

每个 PageStore 同时采样 current canonical、retained exact history、active pending、in-flight、retirement debt、optional cache 的 live/peak bytes，
并记录预算版本、高/低/硬水位、背压次数/时长、`ResourcePressure`、worker progress 和最终 drain debt。记录数量上限不能替代字节上限；
RSS 不能替代 owner ledger，owner ledger 也不能代替 RSS/allocator 对照。

metadata arena 另报各 shard/type 的 blocks、slots used/free、reserved/used/slack/high-water/released bytes，index capacity reservation、
prepare rehash 和 install rehash；publication install 的 allocator call、install rehash 和大对象析构必须分别计数并恒为零。小文档
还要报告 lazy 首块成本，不能只用大 N 摊薄 slab slack。`KisPageWriteIntent/Plan/Entry`、physical claim、guard 和公开 snapshot 的
`sizeof/alignof` 随检查点保存，防止字段增长重新引入页级堆对象。

普通无 history、无旧 View、无 in-flight 且已预检的 resident write 只有在 before-image copy=0、new payload allocation=0、
payload migration=0、计划稳定选择 handoff、峰值 backing 未越硬上限时，才可报告“零冗余复制热写”。这仍包含真实像素写流量、metadata、
cache coherence 与同步成本。当前 recorder 和生产 handoff 尚未实现这些字段，本节是观测合同，不产生新的资格结论。
