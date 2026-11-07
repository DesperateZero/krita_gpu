# 虚拟纹理性能模型、基准设计与决策门禁

> 本文规定如何把 32–38 中的可调参数转化为可复现决策。它不预设未经测量的性能数字。通用可观测性见
> [20_observability_testing_and_performance.md](20_observability_testing_and_performance.md)，CI 硬边界见
> [30_p0_ci_architecture_guards.md](30_p0_ci_architecture_guards.md)。
> BR1 resident CPU路径在进入后续Vulkan性能工作前必须先通过本文§10.1的upstream差分门禁；
> 写侧plan、backing handoff、硬预算和零冗余复制按[92当前合同](92_br1_m6_m8_execution_baseline.md)。
> M6机会型能力门见[92 §6.1](92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)，产品与GPU评价见本文§10.1.1/§10.2。
> 后续backend不能建立在数量级退化或无界backing的CPU control path上。

## 1. 原则

1. correctness、无丢失和线程边界先于性能比较；不正确方案不参与排名。
2. 使用端到端绘画 trace 决定架构可选策略，microbenchmark 只校准成本系数。
3. 报告 P50/P95/P99、最坏有界行为和预算，而不只报平均吞吐。
4. UMA、dGPU、SSD、图层剪枝分别测量，也必须在组合 workload 中验证相互作用。
5. 每个结果记录 commit、device/driver、OS、SurfaceFormat、文档和预算。
6. 未通过 correctness 门禁的 capability 返回 Unsupported；未通过性能门禁的 bucket 返回 `AutoPreferred=false` 并可观察地
   前置 CPU route。不能静默 fallback 后仍宣称该次操作由 GPU/UMA 加速。
7. GPU/UMA 的基线是同机、同质量、启用产品 SIMD/线程优化的成熟 CPU 实现，不是 scalar reference executor。零拷贝、
   GPU timestamp 或 shader 吞吐不能替代端到端 CPU-relative 结果。
8. correctness support、performance qualification 和 Auto route eligibility 分开记录；语义可运行但比 CPU 慢的路径只能
   留作诊断/强制测试，不能成为产品 Auto 默认。
9. 必须分别证明虚拟纹理/PageStore 对主干 tile 的**管理成本**和虚拟纹理对 RAM Tile 的**吞吐/延迟**，再用同一
   workload 的端到端证据整合；GPU/VRAM 与 CPU/RAM 的内核差值不能归因为虚拟纹理管理开销。统一口径见 5.6–5.9。
10. CPU/CpuRam 同义管理以主干等价或更优为目标，不为虚拟纹理抽象预留常驻开销豁免；阶段操作上限不等于管理等价。
    UMA 同一已驻留、布局兼容的 shared backing 不应发生 CPU↔GPU 像素迁移复制，但不能据此把同步或全部 X/E 记为零。
11. “仅支付真实存储/执行需求”是优化约束，不是未经测量的恒等式。不得预设 `E_VT - E_Tile = 硬件跨域成本`，
    更不能预设 UMA 上该差值为零；剩余软件工作、同域访存差异、同步和实际新增语义须独立解释并按各自门禁验收。
12. [67 §10](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#10-2026-09-21冻结-sealed-overlay-与生产-packed-读取) 的 frozen overlay / packed read
    正确性与零重复请求计数只是结构证据。正式配对必须保留相同跨页可见性、default/history/abort 语义，计入 capture/release
    及必要的逻辑保留；不能拿逐页可变读取与固定快照混比，或把 `read_bytes_page` 的像素复制时间当作纯管理成本。

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
GPU low-power/thermal-throttled profile
CPU-fast + GPU-slow/queue-contended profile
UMA shared-bandwidth contention profile
```

无法获得真实硬件时，fake provider 可验证状态和延迟策略，但不能替代真实 UMA/dGPU 性能结论。

平台标签不能替代访问路径。每项结果必须记录 executor、physical memory domain、heap/type/cache 属性、access path、
输入 exact-generation valid replica set、读写类型和输出 endpoint。UMA 共享物理页不证明 CPU/GPU 读写等价；dGPU 的
host-visible device-local/BAR 映射也不是原生 CpuRam。实际驻留无法观测时注明未知/推定，不把 allocation 标志当作实测。

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

### 5.5 Resident CPU/PageStore

- 32767+ 不同 blank coordinates 读取的 wall time、RSS、PageKey/version/replica/allocation 数；
- resident sequential/random accessor read，拆分 root lookup、cached-handle validation、pin/unpin；
- resident write 按 PageStore 内部 `ReusePending/HandoffRecoverable/HandoffCommitOnly/FreshPayload/FreshDiscard/FreshCow/SemanticOnly`
  分桶，并覆盖 active reader、memento/undo/save retention、multi-page Prepared、alias 和 cross-domain in-flight；调用方没有公共 permit；
- 同一 mutation 的同一未发布段对同页重复 1/10/1000 次写，统计 generation reserve、before-image copy、new payload allocation、
  payload retag、seal、root commit；另测中途发布后重新选择 write plan；
- 未升级的 write intent，要求 generation/allocation/proof 为零；另测真实修改像素与 identical write-back，不能混为一个 write 指标；
- default 全生命周期：virgin read、write→default clear、trim/remove、undo/redo-to-default、purge；删除操作不能逐页创建
  新 default pixel allocation，retained 历史 identity/旧 backing 与新 default payload 的成本分别计数；
- epoch sweep：固定 K changed pages，扩大 N manifest pages，统计时延、分配、root nodes copied、full scan/sort；
- 该 K/N sweep 必须覆盖事务起点、adapter history/index 更新、删除 extent、commit/GC 全部阶段，不能只测 tree mutation；
- shard/page 并行扩展，以及 global mutex/map/provider reverse-scan 命中计数。
- metadata arena 按 shard/type 报 reserved/used/slack/high-water/released bytes 与 slot ABA 拒绝；publication prepare/install 分开报告
  allocator、index capacity reservation 和 rehash，install 三项必须为零；另测 1/64/4096 页以暴露 lazy slab 首块成本。
- tiny-budget 压力阶跃：分别限制 pending、in-flight、retirement debt 和 transient versions，验证固定回收顺序、背压、
  `ResourcePressure`、恢复后进度及 close/drain；峰值 physical backing 不得越冻结硬上限。

归因报告必须包含 operation/phase wall、thread CPU、wait 和互斥的采样调用结构；`sample` 包含阻塞线程，不能把其占比
当作 CPU time。先用 1/5 ms 等粗粒度和长窗口检查热点稳定性，再对短路径用批量计时/少量 scope 埋点，不能无条件提高
全进程采样频率。工具与测试口径详见 [53_br1_performance_attribution_review_20260920.md](archive/br1_pre_m6_20260925/documents/53_br1_performance_attribution_review_20260920.md)。

### 5.6 四类证据与基线配对（统一定义）

本文的 `M/K/X/E` 是报告分类，不是新增 PageStore 域或公共 ABI。原生 CPU tile 指固定 upstream revision、启用实际
SIMD/线程/COW 的实现；scalar oracle 只用于正确性。每个 workload 必须先固定相同的语义、输入、工作量和观察端点。

| 类别 | 要证明的性质 | 必需对照 | 不得推出的结论 |
|---|---|---|---|
| M：管理 | lookup/guard、稀疏页、版本/COW 决策、extent、history、commit、回收的成本与复杂度 | 主干 tile + CPU/CpuRam ↔ PageStore + CPU/CpuRam，共同语义逐项配对 | GPU shader 更快不证明 M 更轻 |
| K：驻留算子 | 指定 executor/domain 中，真实像素算子的执行延迟及持续吞吐 | 同域同 executor 的直接访问 ↔ 虚拟纹理访问；另列与主干 CPU/RAM 的异构比值 | 异构比值不等于虚拟纹理开销或产品加速 |
| X：跨域/执行交接 | 跨域 materialization、上传/读回、必要 cache maintenance、ownership/queue-family 交接的成本 | 固定方向、字节/region、batch、queue topology 与已有副本 | 零显式 copy 不证明无跨总线成本或无同步；同域 default fill/COW 不归为跨域迁移 |
| E：整合 | 完整 resident operation 或 W0–W8 的产品吞吐与延迟 | upstream、PageStore CPU-only、forced accelerator、Auto；相同外部任务及 endpoint | M/K/X 的倍率、P95 或并发时长不能直接相加/相乘 |

M 的最小实验：固定已驻留 backing/页集，分别测 lookup + guard acquire/release、未升级 intent、页增删、first-change
登记、changed-page commit、extent、undo/redo、retention release/GC。记录 ns/op、ops/s、thread CPU、wall、wait/hold、
allocation/metadata bytes、transition/scan 数及 N/K/H（总页/变化页/保留 root 数；版本数另计）规模。COW 分配/像素复制另列，管理生命周期
总时间仍保留，不能通过不执行必要 COW 或销毁来“减轻管理成本”。只有实际新增的对外语义、且确无主干同义项时，才标记
`additional semantics` 并给绝对成本/预算及 E 影响；不虚构主干零耗时，也不从真实产品总成本扣除。为完成同义操作而引入的
generation/proof/adapter 记账仍属于该操作的 M，不能仅凭内部类型不同重分类免责。no-op/fake 只用于诊断，不独立授予资格。

GPU/UMA 阶段还必须测实际 provider 路径的 host-side 管理：共同页生命周期在同一 CPU、相同 N/K/H 下对照主干 tile；
实际异构执行新增的 binding build、proof/ticket、驻留调度等 CPU 工作单列成本和总管理预算，queue/transfer 等待分开；
是否属于 additional semantics 按上述对外契约判定，不能笼统归为不可优化的硬件成本。
不能仅凭 CPU/CpuRam bridge 的 M 通过就外推 GPU 管理已达标，也不能把 shader 内的寻址时间当 host-side 管理时间。

CPU 同义管理的“等价或更优”采用独立的工程不劣性验收，而非要求每次计时逐周期相等：

- 理论目标为 `M_time_ratio <= 1`。在同 CPU/CpuRam、同管理语义和 N/K/H 的配对 profile 中，验收前冻结各指标的
  相对容差 `epsilon_M`、绝对容差（仅适用于近零基线）、采样/停止规则、置信水平和 required bucket 清单；容差须有
  测量分辨率与工程敏感度依据，不能沿用完整操作的 20%–50% 阶段余量，也不能看完结果再放宽。
- 对预先指定的管理 CPU 成本、生命周期延迟及尾指标，候选/主干时间比的单侧置信上界须不高于 `1 + epsilon_M`；
  置信水平默认至少 95%。管理完成吞吐单独测量，其候选/主干比的单侧下界须不低于 `1 - epsilon_M_rate`，不能由延迟
  取倒数生成。更优结果允许通过，不要求落入对称区间。
- 近零时间基线按事先指定的绝对差值上界判定，不用不稳定倍率；零分配/零 request 等结构硬门槛仍严格为零，不给容差。
- 重复采用独立配对运行/回放，说明运行顺序、漂移和相关性处理，不能把同一次运行的大量相关事件伪装成独立重复。
  所有 required bucket 分别验收；多指标置信处理须预先说明，不能用平均值掩盖单类退化。
- 只报告“差异不显著”而无上述不劣性证据，或置信区间跨越通过边界、容差未冻结、样本不足，均不能证明等价；
  报告 `Inconclusive`/`NotMeasured` 并
  保持门禁未通过。内部额外记账不能从 M 中剔除；真正新增语义的绝对预算与完整 E 也必须通过。

正式结论用“在冻结容差内通过同义管理不劣性”，与目标 `M_time_ratio <= 1` 分开。它不是严格相等、对称统计等价或
“没有任何软件成本”的证明。M 的剥离方法须对双方一致：版本/COW 决策、allocator 调用的管理部分和回收记账仍需归属，
不能把整个 provider/acquireWrite 区间排除后只比较剩余轻量管理；混有分配、初始化、复制和等待且尚未拆开的区间标为
inclusive/未拆分，不授予纯 M 或纯 K 资格。被剥离的数据准备仍留在完整 E 与生命周期总成本中。

报告须为每项时间和比值绑定 `MetricScope`，如 management-self、lifecycle-inclusive、resident-kernel、handoff-transfer、endpoint，
并注明 CPU/wall、计时边界及排除项。管理 API 的 inclusive 延迟不等于管理 self；若包含像素初始化/复制，不能只凭
`alias`、`adoption` 或 `commit` 的用例名称授予纯 M 资格。管理 self 与生命周期总延迟分别保存、分别按冻结指标验收，
不能事后更换分子范围。此字段是报告契约，不是已实装的 recorder 字段或新公共 ABI。

K 的计时在输入已就绪、guard/binding 已建立、所需 COW/输出 allocation 已准备后开始，到对应算子完成结束；显式排除的
setup/lease/submit/transfer/commit 成本必须在 M/X/E 找到归属。CPU 使用同算子的并行 makespan，另报各线程 CPU 总量；
GPU 使用匹配执行范围的 timestamp，不能拿 CPU thread-time 总和与 GPU duration 直接比延迟。真实 load/store、cache miss、
shader 内地址解析和访存停顿属于 K，不能扣成“非内核”。pre-bound K 不替代包含 iterator/page transition 的 resident E。

必需配对矩阵：

| 配对 | 固定条件与用途 |
|---|---|
| 主干 CPU/RAM Tile ↔ PageStore CPU/CpuRam | M 对共同管理语义；K 对驻留算子；resident E 对实际 iterator/operation 的总成本，三项分别报告 |
| GPU direct/pre-resolved addressing ↔ GPU VT，均本地 VRAM | 相同设备、格式、计算、数据集、dispatch/workgroup 和可比布局/缓存；只变寻址/绑定策略时才可归因 VT 开销 |
| GPU direct ↔ GPU VT，均 UmaShared | 同上，另控制 CPU/GPU 共享带宽争用；不得借 UMA 标签假设与 VRAM 或 CpuRam 等效 |
| CPU/CpuRam ↔ CPU/UmaShared mapping | 相同 CPU 算子及管理实现，read/write/RMW 分桶，测映射/cache policy 的影响 |
| GPU/VRAM 或 GPU/UmaShared ↔ 主干 CPU/RAM Tile | 只称“异构驻留算子速度比”；保留双方各自的内存系统优势和限制，不称“管理成本比” |

GPU direct 控制组不是另一个生产 authority，只是隔离 benchmark。无法只改变一个因素时列明差异，结果称实现/布局综合比较，
不得宣称纯 page-table 开销。shader 内寻址成本与 CPU binding build/发布分别记录，不能既计入 K 又加一遍到 M。

### 5.7 存储域、读写方向及跨域边界

| executor → backing/access path | K 中的实际访问 | X/E 中必须追踪的额外成本 |
|---|---|---|
| CPU → native CpuRam | CPU cache/DRAM | 管理、COW、commit；显示任务所需上传 |
| CPU → UmaShared mapping | 该 mapping 的 CPU 读写与缓存行为 | 先前 GPU writer 完成、必要 invalidate/flush、ownership |
| GPU → UmaShared | GPU cache/共享内存及争用 | CPU 准备、排队、交接、publication；零 domain-copy 不等于零成本 |
| GPU → resident DiscreteVram | GPU cache/本地显存 | 必要 upload/download、缺页、binding、queue、publication |
| GPU → host RAM，经跨总线直访 | 内核内含跨总线访存停顿，单独标记 remote access | 不得因没有 copy command 就当成本地 VRAM；可观测 link bytes 独立记录 |
| CPU → mapped dGPU VRAM/BAR | CPU 跨映射路径读写，不属于 native CpuRam | 同步、cache policy；不得合入 UMA shared 统计 |

每种路径至少区分 read-only、full overwrite、read-modify-write、partial update，sequential/random、hot/cold cache，
并分别测 4/8/16 BPP。full overwrite 不强加旧像素上传；RMW 仅在无适用 exact valid replica 时 materialize。CPU fallback
也可能需要 VRAM→RAM，不能假设 CpuETA 永远从 RAM-ready 开始；authority 位置不等于唯一可读副本位置。

显式 domain copy、COW、undo、derived/display copy 各自计数。GPU 直访 host RAM 的等待已在 K，不允许再加估算 PCIe 时间；
UMA cache/order 成本则不能因为 domain-copy bytes 为零而省略。硬件事实依据
[Vulkan memory specification](https://docs.vulkan.org/spec/latest/chapters/memory.html) 与
[Vulkan memory allocation guide](https://docs.vulkan.org/guide/latest/memory_allocation.html)，实际性能由设备实测决定。

UMA 的零迁移要求限定于所需 exact bytes 已在同一已驻留、布局兼容的 shared backing；此时 CPU↔GPU payload migration
copy count/bytes 必须为零，不应创建空迁移任务伪造一次域转换。它不代表 DRAM/cache 流量、访问顺序、必要 cache maintenance、
queue/ticket 或执行等待为零，也不覆盖 SSD 换入、COW/undo 和 derived/display copy。CPU-only 且无需 GPU 交接时，不应仅因
backing 可被 GPU 使用就执行 GPU binding/submit/ownership 协议；真正交接时的必要成本如实保留。所有剩余差值须区分必要
硬件/执行依赖、实际新增语义与可消除的软件冗余，不能把差值全部命名为“硬件存储事实”。

零迁移须同时给出 shared allocation/exact generation/布局与驻留证据，以及覆盖该交接的实际 copy count/bytes。
CPU-only 未发生交接标 `NotApplicable`，不能作为 UMA 零迁移通过；发生过交接但未覆盖相应计数范围标 `NotMeasured`，
不能填零。已证明无需搬运的路径不应有 payload migration 执行区间，但其访问开销和 handoff 仍单独测量；不从两个
微基准的耗时差或硬件标签推出“硬件存储事实总开销为零”。

### 5.8 吞吐、延迟与初末状态

每个结果记录 `InitialState -> RequiredEndpoint`：

- `InitialState` 包括各 exact generation 的 valid replica set/ready 状态、缓存和驻留、history/COW 条件、预算、queue depth；
- `CpuReadable`：相同输出 bytes 可由合法 CPU lease 读取，GPU 路径包括必要 readback/invalidate/order；
- `GpuConsumable`：相同输出可被下一 GPU consumer 正确使用，CPU 路径包括必要上传，GPU 不强制无用读回；
- `PublishedEpoch`：相同逻辑结果已原子发布，但不冒充 CPU 已读到或屏幕已显示；
- `Visible`/`Recoverable`：按 20 的定义继续到相同可观察/恢复端点，present submit 不冒充 visible。

正确性检查所需额外 readback 可在 timed region 外完成，但须单独报告，且不能排除所选 endpoint 本来要求的读回。
“warm”必须说明是 RAM、VRAM 或 shared 全驻留，首次上传/预热不隐去：K 可排除，cold E 必须计入；warm E 另列 setup
和明确的复用次数。局部路由对照从同一实际状态出发；产品 trace 从相同外部文档/事件开始，允许各实现形成不同内部驻留，
但必须统计完整 trace 内全部迁移，不能以 GPU 预驻留的局部优势代替整段产品收益。

延迟按单次完成的上述端点测 P50/P95/P99/max，报告事件数及置信范围；吞吐为达到同一端点的有效工作量/测量墙钟，不能
用 enqueue/submit 速率。报告 ops/s、有效 pixels/s；标为 logical GB/s 时明确 R/W 字节定义，不把 alias/default/no-op 当作
物理带宽。物理 RAM/VRAM/link bytes 来自硬件 counter 或单独标记的估算，未知填 N/A。RMW 的读、写字节分别给出。

单操作/固定并发延迟和饱和吞吐分别测；固定工作量、线程/in-flight 上限、batch、到达率、queue depth，并报告排队/背压与
完成数，不用扩大队列掩盖尾延迟，不用 1/P95 推导吞吐。交互 replay 保留原事件时间，不能把批量计时重复改成大 batch 后
据此宣称单笔交互达标。冷启动/稳态/压力分桶，不将它们平均为一个“VT 性能”。

### 5.9 整合报告与证明边界

每个 workload 生成同一关联 ID 下的四联结果，缺失项填 `NotMeasured` 或附原因的 `NotApplicable`，不能填零：

| 证据 | 必填结果 | 用途 |
|---|---|---|
| M | 配对管理成本、结构 counter、N/K/H scaling；新增语义成本单列 | 证明管理层是否接近主干，定位新增开销 |
| K | 同域 direct/VT 与异构 RAM Tile 的 latency/throughput 两组对照 | 区分虚拟寻址影响和硬件/存储系统收益 |
| X | 方向、字节、batch、交接与实际关键路径暴露时间 | 解释迁移、同步、远端访问为何改变收益 |
| E | resident operation 与完整 trace 的 CPU-only/forced/Auto 吞吐、延迟、资源占用 | 决定产品性能资格 |

比值统一命名：`M_time_ratio = VT_management / mainline_tile_management`（仅同义配对）；
`M_throughput_ratio = VT_management_completed_work_rate / mainline_tile_management_completed_work_rate`（同义完成端点）；
`K_local_time_ratio = VT_kernel / direct_kernel`（同 executor/domain）；
`K_heterogeneous_speedup = mainline_RAM_kernel / accelerator_resident_kernel`；
`E_latency_ratio = candidate_endpoint_latency / baseline_endpoint_latency`；
`E_throughput_ratio = candidate_completed_work_rate / baseline_completed_work_rate`。
时间比小更好、speedup/吞吐比大更好；注明 median/分位数、样本和不确定性，不混名、倒置分母或把不同 bucket 合并。

M/K/X 的 CPU self、GPU timestamp、资源忙时间和等待以同一 dependency trace 关联到 E；重叠、嵌套和时钟相关误差单列，
端到端取实际关键路径而非机械求和。cache/TLB/访存与算术常常重叠，不能用两个独立 microbench 相减“还原纯计算”。
M/K/X 是归因视角，并非穷尽且可相加的三个时间桶；同域 default fill/COW 等数据准备单列为 E 子阶段，不硬归入跨域 X。
每个实际区间指定唯一 accounting owner，copy reason（COW/undo/domain/derived）作为正交标签；管理生命周期 inclusive
已经包含的数据准备或等待，不再与其 self/子阶段重复求和。
管理拆段和 isolated K 用于归因；最终 E 另跑无 profiler 的原产品路径，不能把拆段改造后的合成测试当产品结果。

集成时保留管理与产品两个独立判定：K/E 的 GPU 带宽优势不能抵消 M 的结构硬门槛或 CPU 主干回归；M 通过也不代表
VT 总吞吐/延迟通过。异构 K 较慢不自动判定架构失败（可能省去后续迁移），K 较快也不自动获得 Auto 资格；由 X/E 证明。
新增 GPU direct/VT 比值用于归因，硬件 profile 的数值预算须在验收前冻结，不能杜撰通用阈值或事后为通过而调宽。

### 5.10 归因与实现证据的更新纪律

“等价”默认指相同对外语义下的性能目标，不指源代码、容器或整条管线完全同构。复用 `KisTileData`/pool/swap 只证明
存储层复用；新增 PageStore 协议、adapter 和 epoch 工作仍需测量。报告须按存储、访问、写入、提交、历史和回收分别说明
复用/新增路径，不能以一个“同构”标签替代 M/K/E 证据。

每个优化切片保留 `设计目标 → 代码路径/版本 → 结构断言 → 分段归因 → 无 profiler 配对计时 → 门禁状态` 的证据链：

- 保存源码与二进制/库身份、workload/seed、实际 N/K/H、线程/交错限制、初末状态及计时端点。已有报告只描述其采样版本；
  修复后不能继续把旧热点称为当前热点，也不能把“代码删除了该路径”写成“已经测得同比耗时下降”。
- counter 标明 owner/manager、采集区间及排除项；单个目标 manager 的零值不能证明临时 source manager、整个进程或整个
  产品 trace 均为零。累计创建数、结束时存活数和峰值分别记录，退出后的 drain 未观测时不能据终值宣称回收长期有界。
- 按 `prepare → 内容判断 → proof/preflight → root 构造 → 发布 → adapter 更新 → retire/drain` 拆段，记录 wall、thread CPU、
  wait/hold、调用/页数、分配/复制字节和重试。互斥 self、父级 inclusive、GPU timestamp 和采样 occupancy 分开；
  未归因残余显式报告，不把采样比例乘总墙钟当作精确阶段时长，也不把残余自动归给锁或硬件。
- 默认先复查已有粗采样的窗口与符号覆盖。路径、输入或热点发生变化时重采样；短路径用固定批量计时和少量 opt-in scope，
  多线程用固定 page-work 及 K/N/H 对照。是否改用更细采样由覆盖和扰动证据决定，不无条件提高全程频率。
- 删除/alias/default 优化须检查后续读、首次真实写、history prune、restore/purge 和最终 drain，防止把工作移出测量区间。
  真正按需的物化单列发生原因；目标 native default 共享读取与过渡 generic materialization 分别标识。
- 结构测试通过、正确性套件通过、性能通过分别记录。任何未测的 after、同主干配对、尾延迟或 GPU/UMA profile 均为
  `NotMeasured`；缺少证据不得沿用旧 Pass，也不得把五次 before-only 运行称为 before/after 或不劣性证明。
  已有切片 before/after 诊断则记为“已测诊断、未取得资格”，不能继续笼统写“性能未测”。按 workload/bucket/版本逐项保留
  状态，诊断存在不自动授予 formal M/K/X/E Pass。先跑完 before 再跑 after 的结果注明顺序/漂移限制；不把同 seed 等同于
  同 page work 或同主干配对。两次 after 区间重叠时，不能把均值/中位数差直接分配给某个附带修复。

偏差登记至少包含预期、实际计数/时长、失败原件、定位、修正及复验、剩余假设。若消除预期放大项后 E 无明显改善，
先核对实际工作量、成本转移、计时边界、扰动与串行关键路径，再据新证据调整研究顺序；不能直接断言方向已失败，
也不能反过来用理论收益替代实测。当前 BR1 历史归因见 53，切片实施与偏差见
[54_br1_optimization_execution_and_deviations_20260920.md](archive/br1_pre_m6_20260925/documents/54_br1_optimization_execution_and_deviations_20260920.md)。
后续 D2 的固定页集、实际阶段计时与明显 scope 扰动见
[55_br1_d2_phase_measurement_and_atomic_transaction_begin_20260920.md](archive/br1_pre_m6_20260925/documents/55_br1_d2_phase_measurement_and_atomic_transaction_begin_20260920.md)。
即使一项结构放大已消除，整体验收也不能由定向高收益桶替代；warm known-noop 与 cold identical 的 canonical 额外工作须分开报告。
同步 prepared metadata publication 的首版反证、修正与新证据见
[56](archive/br1_pre_m6_20260925/documents/56_br1_prepared_metadata_publication_20260920.md)。新旧 phase 同名不保证计时端点相同；preflight 移入 removal/default
后必须合并对应阶段对照，并报告完整无 profiler 操作时间。私有 trusted-state 复用不得变成 caller skip-validation 开关，
必要 transition-local guards、provider/lifetime 复验与 full reference 对照不因优化豁免。
后续长区间交替与操作级抽样见 [57](archive/br1_pre_m6_20260925/documents/57_br1_sampled_write_pipeline_and_immutable_directory_20260920.md)。小样本探索性 paired
bootstrap 以进程 pair 为单位，不把循环内操作当独立重复；区间跨 1 既不证明加速，也不自动证明不劣性。
新诊断 binary 的关闭态偏移、采样条件下的单次时钟成本和历史工作量/循环长度区别，均须保留，不能反向改写旧版本证据。
语义 default request 计数不包含 write allocation 的内部初始化；额外 fill/copy 必须作为 resident payload 工作报告，
不能因 default request=0 便记为零，也不能归入 X 掩盖 CPU 同域额外工作。

native COW 切片必须执行以下计量纪律（具体字段见 20 的 11.1）：

- 分开报告 default 初始化、显式 source copy、native duplicate 和 backing adoption；明确逻辑字节、代码发起的复制字节
  与硬件观测流量。预克隆命中仅说明前台没有当场执行对应 memcpy，必须计入后台预制/补充、未使用 clone 的占用与回收。
- 新增埋点/API/统计布局时，先冻结带相同测量脚手架的 before，再比较优化 after；保存两侧源码、ABI、实际装载库和
  executable 身份。不能用不兼容的旧测试二进制交替加载新库，也不能把诊断代码布局带来的偏移计为算法收益。
- 操作级周期抽样记录实际 sample 数并轮换 offset；检查与 workload 周期的相关性，必要时采用可复现的随机抽样。
  空 scope/关闭态/稀疏开启态分别校准；抽样父子区间只作归因，正式 E 与尾延迟仍用独立的无 profiler 测量。
- after 即使 default-fill 字节归零，也要复验首次真实写、宽格式、history/abort 与完整操作/drain，不能仅凭少了一遍
  逻辑写入宣称节省同量 DRAM 流量、具体加速倍数或主干管理等价。必要 COW 保留，不能为追求零 copy 破坏旧版本。

D4 的 provider 计数、十桶交替配对与两侧抽样校准见 [58](archive/br1_pre_m6_20260925/documents/58_br1_native_cow_initialization_and_payload_accounting_20260920.md)。
真实写有切片收益，但 preclone 命中为0、后台计量未齐，部分抽样桶仍有约1%及反向偏移。须保留这些限制，不能把新证据
写成主干 M/K/E、预克隆预算或零扰动通过；报告解析须遵守当前 schema（零 interval 阶段可省略），并以实际 copy 计数交叉核对。

D5 同源主干 fixture 及 11 桶各 12 对窗口吞吐见 [59](archive/br1_pre_m6_20260925/documents/59_br1_shared_upstream_cpu_baseline_20260920.md)。其 guard/lookup
是管理生命周期而非隔离 self，alias/read/write 是操作级 E，预绑定 memcpy 仅为 resident K 控制。已有主干诊断不再标作
“全部未测”，但没有预冻结 M 容差，不能授予不劣性 Pass；暖 H=0、单线程结果也不外推为产品或无限长稳态。
独立限时完成吞吐不能代替固定工作量、单次延迟分位或长时压力。固定-work 因累计记录增长风险暂缓时，须事前存档
协议决定和未执行范围，随后补同累计操作数的 completion/replay/root/retire 占用与 drain；不以不同完成量的 RSS 比声称
每操作内存优势。保留原件与 driver/library 身份，未知归因不能通过吞吐倒数或移植旧采样比例补造。

D6组件长桶、操作吞吐与全进程RSS对照见 [60](archive/br1_pre_m6_20260925/documents/60_br1_completion_coverage_and_sparse_terminal_status_20260920.md)。
压缩计数通过不替代字节/峰值/回收预算；连续成功收益不豁免高碎片或失败/取消分布。初版区间树反证与修正版均须保留，
scope/version明确。组件收益远大于原生操作收益时据此调整主线，不将组件倍率乘进主干M/K/E，不授予未测分布有界性。

D7 captured identity、generic session 与 native adapter 三组对照见
[61](archive/br1_pre_m6_20260925/documents/61_br1_captured_read_scope_and_integration_cost_20260920.md)。旧 retained scope 的 owning manifest/full-scan 与新 captured
scope 的组件比较不能冒充原 session 加速；新 session仍有逐页generic lease，实测单页吞吐下降23%–25%。并发不满足捕获
不变式的D6路径仅用于稳定head诊断，不作为可回退的合格实现。retention一致性修正、component收益、完整像素路径性能
分别给结论；不得从前两项授予M/E Pass。原生写约0.9%反向偏移保留，尚未归因或取得不劣性资格。

D8新facade原生像素读与共享provider gate见[62](archive/br1_pre_m6_20260925/documents/62_br1_native_resident_read_and_write_cost_20260920.md)。23桶各8对
（184对/368次计时运行，另4次loader检查）证明该版本暖读逐页generic request为零、完整scope窗口吞吐较D7改善；
却同时观察到原生真实写吞吐下降2.3%–4.8%。两项独立登记，不作读写加权抵消，不把D8/D7连乘历史比值冒充主干重测。
这是分支内诊断，非预冻结不劣性、单次尾延迟或完整drain资格。eager binding/record维护是待因果对照的假设，
无分段self证据不能将全部写差额归给缓存/锁；后续lazy候选须保留冷读、只写控制与完整生命周期，不借搬移setup宣布消除成本。

D9按需cache的六组配对见[63](archive/br1_pre_m6_20260925/documents/63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md)。相对D8收回部分真写成本，
直接D7控制仍有残余；首次read scope成本增加、部分暖读/rect反向偏移均须保留。完整写读周期改善不能豁免独立读回归。
inclusive phase timing需附plain/profile扰动，不能改名为binding/锁self；暖request为零不等于暖管理未增加工作。
该检查点要求后续热/冷API拆分直接对照冻结版本，不用多轮比值相乘。D9仍是诊断候选，非M/K/E或GPU/UMA正式资格。

D10的直接D9/D8对照及独立D7原生控制见[64](archive/br1_pre_m6_20260925/documents/64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md)。
冷热查询分离提高部分暖K16 guard/session吞吐，不消除D8-relative宽格式/单页负偏移、首次读成本转移或D7真写残余。
held-view guard不含capture/release，不能授予完整session资格；新固定-work已覆盖facade/provider容器析构，不覆盖全后台drain。
实际hash seed、布局/allocator与后台活动未完整记录，不能反推它们导致偏移，也不能拿“环境噪声”豁免反证。
后续环境控制按20的11.3冻结：控制seed/layout的定向诊断与生产默认配置独立复验，不变更生产策略、不筛掉不利样本。
旧`lifecycle_ns`与新同名字段端点不同，须用明确完成条件比较；新增记录/fixture关闭态偏移也计入校准。

### 5.11 统一口径速查与报告判词

本文 5.6–5.10 是定义来源；20 负责计量，30 负责拒绝条件，52 负责实施计划。下表是这些规则的摘要，不另设性能预算：

| 场景或结论 | 统一表述与验收边界 | 不可替代的证据 |
|---|---|---|
| CPU/CpuRam 同义管理 | 目标为主干 Tile 等价或更优；虚拟纹理抽象没有固定软件开销豁免 | M 逐 required bucket 的预冻结不劣性；管理 self、生命周期延迟及完成吞吐分别给出 |
| CPU-only、无需 GPU 交接 | 不执行无用 GPU 协议；同域 COW/初始化和 PageStore 记账不是跨域成本 | 实际路径/counter 与 resident E；UMA 交接项目为 NotApplicable，不能借此授予 UMA Pass |
| UMA 同一兼容驻留 backing 的真实 CPU↔GPU 交接 | payload migration copy count/bytes 为零；必要 cache/order/queue/ticket 和访问成本不记零 | shared allocation/exact generation/布局/驻留及覆盖交接的 copy 证据；M/K/X/E 独立验收 |
| dGPU 或 UMA 不满足上述共享条件 | 只在缺少适用 exact valid replica、且 endpoint 确实需要时搬运；不预设迁移量或耗时 | 实际副本、访问路径、方向/字节和关键路径；GPU remote-host 停顿在 K，不能再加一次 X |
| 与主干性能、结构的关系 | “底层复用”“管线同构”“通过不劣性”“产品性能达标”是四种结论 | 分层源码/结构证据与独立 M/K/E 配对，不能相互推导 |

“VT 额外时间只来自真实跨域需求”只表达**消除无必要软件工作的目标**，不是 `E_VT - E_Tile == X` 的等式；
“UMA 存储事实开销为零”统一收窄为上表的零 payload migration。不能把同域访问差异、必要语义或未解释残余
打包成硬件开销，也不能用术语收窄来删除这些成本：全部实际工作仍在生命周期与完整 E 中接受预算检查。

对“额外成本”的归因须满足以下证据责任；没有证据的差值保留为未归因残余，而不是新增免责类别：

| 成本判断 | 必须核对的事实 | 处理规则 |
|---|---|---|
| 同义操作的软件管理差额 | 相同语义/工作量/初末状态下，实际 lookup、guard、版本、分配记账、提交及回收路径 | 留在 M 和完整 E；不能以 VT 所需协议或内部类型不同为由豁免 |
| RAM/shared/VRAM 访问差异 | executor、实际 backing/access path、cache 属性、read/write/RMW 及同域 direct/VT 控制 | 由 K 与 resident E 解释；内核内已计入的远端访存停顿不再加到 X |
| 必要搬运或执行交接 | exact valid replicas、目标 endpoint、真实 copy/cache/order/queue 事件及依赖关键路径 | X 分开记录 payload migration 与 handoff；软件构建/调度成本不自动成为硬件下界 |
| 尚未解释或超过预算的差额 | 计时边界、scope、未覆盖工作、抽样扰动和配对不确定性 | 登记偏差并继续研究；不得用“UMA”“必要同步”或异构 K 加速自动结清 |

阶段摘要中的“UMA copy=0”一律引用 5.7 的完整适用条件，不能扩展为所有 UMA workload。零是有计数覆盖的
payload migration **count/bytes**；已证明没有执行迁移时记录“未执行迁移”，不造一个计时值 `0 ns`。真实交接的
次数/方向仍须记录；未交接为 `NotApplicable`，未覆盖为 `NotMeasured`。耗时低于分辨率则报告测量上界/分辨率，
不能写成严格零耗时。没有搬运不代表 X 中的执行交接消失，也不免除 M/K/E 门禁。

报告结论按顺序写明 `目标 / 实现范围 / 已测证据 / 资格状态`，并绑定切片/源码/二进制身份。例如 D5 是同源 upstream
窗口吞吐诊断，D6 是分支内 completion 布局对照；不能把 D6 的局部收益乘入 D5 比值，生成未经重测的“当前主干性能”。
工作树中的后续接线不继承旧 binary 的测试或性能 Pass。仍非整条 CPU 管线同构，正式 upstream M/K/E 未取得资格，
GPU/UMA 产品性能为 `NotMeasured`。诊断收益不授予性能 Pass；
`NotApplicable` 必须说明条件为何不适用，`NotMeasured`/`Inconclusive` 不能当作零值或通过。未知残余保留为待研究项。

### 5.12 Native resident read 的分层验收

本节细化 5.6 的 M 与 resident E，不新增容差，也不将草稿接口存在视为实现通过。必须区分四种计量范围：

| 范围 | 必须保留的工作 | 可支持的结论 |
|---|---|---|
| scope capture/release | root 捕获、retention、退出及触发的 GC；最后旧 reader 单列 | 一次操作的一致性与固定管理成本，不是逐页访问成本 |
| scope 内首次 exact binding | 受保护 root resolve、metadata 查找、provider record 建立/首次解析及局部 pin | 冷 binding 管理；payload 已驻留不代表 binding/cache 已暖 |
| scope 内暖 resident guard | cached binding 校验、局部同步、first/last pin/unpin | 指定路径的逐页 M；不能外推整个 session 无锁或零分配 |
| 完整 session/accessor/operation | 上述工作、真实像素访问、page transition、scope cache 分配、释放及必要后续回收 | resident E；单独测吞吐、单次/负载延迟和 drained 总成本 |

“读侧免 PageStore 全局锁”只在明确的路径范围内声明。metadata shard 锁、page-local gate、swap barrier、首次 provider
lookup/once 初始化、capture/release 的 owner gate 都分别报告调用数与可测 wait/hold；短锁、`tryLock`、原子引用计数或
`call_once` 本身不证明严格 lock-free、wait-free 或无阻塞。仅 identity lookup 免锁也不证明像素路径具备相同性质。
必要局部同步须通过扩展性与 M/E 验收；不能因被命名为“局部”便视为无成本。

resident hit 的零 heap request/lease、零全局 request-map 插入、零 owner 热访问锁是结构要求；它们不等于 scope、
索引或 provider record 零分配。冷热 setup 分开计量，所有实际分配仍进入完整 M/E。首次 binding 的管理查找不能记为
payload fault，更不能记为硬件跨域 X；不能把每次操作必经的 setup 永久移到窗口外制造稳态优势。

每次逻辑读的结果与内部尝试分开计数：scope-cache hit、native resident hit、virtual-default hit、generic completion、
失败/取消；重试另计。generic 原因至少区分真实 non-resident、producer/handoff 未就绪、provider 尚无 native 能力、
binding 未建立、局部 busy，以及无效身份/能力。过渡实现缺口、局部竞争与身份错误不能统称“硬件缺页”；无效身份必须被拒绝，
不得借 fallback 读到其他 generation。busy 可有安全的有界重试/延后或过渡 generic 路径，但必须计入软件成本与未完成项，
不能据此放宽最终 ready-resident 门禁。未能观测细分原因时填 `NotMeasured`，不从总 miss 数推断迁移。

新 guard 需证明 root/metadata、physical pin、异步 last-use 三类寿命协调，以及 generic/native 读写、transfer、retire、
swap 和 session close 的互斥/回收边界。回收资格检查必须看见 native pin，不能先丢 canonical metadata，再忽略 provider
的 busy/retire 失败。多个 allocation handle 共享 payload 时，单个 record 的 reader 数不构成物理独占或原位写 permit。
这些安全测试、结构计数、完整读/真实写回归及同主干配对分别给证据；减少 generic 请求数不是独立性能 Pass。

同一稳定 head 的旧库可作诊断控制，但若其并发读语义已不满足捕获不变式，不能作为合格回退或降低新实现语义的依据。
增加新 guard/provider 接口后，跨版本装载先验证双方 ABI 和实际库身份；不支持的新版入口不能由旧库补出“before”。
最新工作树候选、最新已归档切片和正式资格分别标识，具体状态以52第11节为准。D8已有新facade暖读和生命周期证据，
D9补按需cache/冷周期，D10补冷热分离、held-view guard及固定-work局部析构；各自不覆盖旧历史结果，不证明所有legacy
traversal已迁移，也不令本节全部计量自动完成。最新缺测项与反证见64、20的11.2–11.3；暖管理、冷首次读、真实写和
完整生命周期分别给结论，任何一项改善均不自动豁免其余项。

D11 生产 writeBytes 写段及直接主干对照见 [65](archive/br1_pre_m6_20260925/documents/65_br1_native_cpu_mutation_segment_20260920.md)。原生 generation/seal
计数必须与 generic request 分列，不能让新路由的零 request 把实际 COW/变更页记成零。按未发布段统计，段持有 pin 的峰值/
持续时间另测。native seal 的计时是批量 inclusive 区间，不是逐页 proof self 或短发布锁 hold。
本次 K16 改善与 K1 回归同时保留；M 代理、预持 RAM copy K 和 writeBytes E 分开判读，仍无正式 M/K/E 不劣性、尾延迟、
全后台 drain 或 GPU/UMA 资格。实际时钟边界见20的11.3；不把主干头文件 ABI 不同的 fixture 强行交叉装载。

D12 physical claim 正确性只证明其物理排他边界；没有 production `KisPageWriteCoordinator`/inline plan 消费、backing handoff、
零冗余复制稳态、硬字节预算及完整 E 证据时不能给原位写资格。
新增负例应覆盖legacy/native/generic pin、provider alias/seed、并发ref、swap miss、preclone失效、撤销与最终释放。
已知owner引用数不等于采样的总refcount；等待alias释放后仍需exact identity复验。普通ref路径改动需分别编译的直接配对
验收，结果与缺测见[66](archive/br1_pre_m6_20260925/documents/66_br1_physical_exclusivity_prerequisite_20260920.md)，不以物理claim微测试代替M/K/E。

## 6. 端到端 workload

### W0：稳定当前目标

持续在一个图层局部绘画，验证 current/predicted target 满足 5.7 条件时的 UMA 零 payload migration、dGPU fault 收敛和笔迹延迟。

### W1：快速长线与方向突变

检验 trajectory corridor、deadline miss、错误预取和大笔尖 page set。

### W2：大画布 pan/zoom/teleport

检验 viewport 工作集、一次性扫描污染、local binding window 和不可预测 cold fault。

### W3：深图层栈目标绘画

检验 lower checkpoint、upper replay、CoverageCertificate 和非目标页降温。

### W4：频繁切层/属性/滤镜

检验 EvaluationEpoch 失效、derived rebuild、旧 coverage 拒绝和反向迁移。

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
auto-route misprediction time / total execution time
accelerator-regret = max(0, measured accelerator time - predicted/paired CPU time)
```

### 7.4 Capacity

- exact/derived/transient/reserved bytes by domain；
- current canonical/retained exact history/active pending/in-flight/retirement debt/optional cache bytes 与各自 live/peak；
- metadata bytes per instantiated page/version/replica；
- logical/physical/padding ratio；
- retired-but-not-free bytes；
- OS/driver heap usage差异；
- SSD live/dead/slack bytes。

## 8. 成本模型校准

### 8.1 CPU-relative execution route

每个 operation family、StorageClass、page-count/work-size bucket 和 device profile 必须进一步按 executor、backing/access
path、read/write/RMW、initial valid replica set、required endpoint、history/COW、queue/cache/pressure 状态校准。统一比较
边界见 5.6–5.9；以下是成本特征，不是直接相加的测量端到端时间：

```text
RouteFeatures(executor, initialState, endpoint) = {
    managementAndCompile,
    requiredMaterializationAndCow,
    queueAndDependencyDelay,
    residentKernelByAccessPath,
    requiredCacheAndOwnershipMaintenance,
    commitAndEndpointDelivery
}
CpuETA         = calibratedCriticalPath(CPU, RouteFeatures)
AcceleratorETA = calibratedCriticalPath(GPU, RouteFeatures)
```

CPU 数值来自相同产品路径的 replay/profile，必须包含实际 SIMD、线程调度、COW 和 PageStore 成本。GPU/UMA 数值必须包含
CPU 编译、page fault、迁移、flush/invalidate、queue、publication 和达到相同 observable endpoint 的成本，不能只用
device timestamp。

分段 P95 相加不等于总时长的 P95，也不自动构成保守上界；阶段之间可能相关或重叠。
下面的 `UpperP95/LowerP95` 必须用相同 workload 的端到端分布和校准误差建立，不得直接把分段加和当作置信界。
已有适用 exact RAM replica 时 CPU 不付无用下载；仅 VRAM 可用时则不能套用 RAM-ready 内核时间。GPU 同理。输出仍供 GPU
使用时不强制读回；CpuReadable/Visible/Recoverable 各付其真实交付成本，不能跨 endpoint 选择较便宜数字。

产品 `Auto` 只有在以下条件同时成立时选择 accelerator：

```text
semantic/correctness capability ready
performance profile fresh and hardware state matched
AcceleratorUpperP95 + riskMargin < CpuLowerP95 * 0.90
queue/residency/backpressure within calibrated envelope
```

10% 预测收益是吸收模型误差的默认迟滞，不进入公共 ABI，可由完整 trace 校准得更保守。route 在 stroke/operation 首次
写入前冻结；MVP 不允许 per-dab、per-page 临时切换。设备丢失等故障必须 abort 未提交 accelerator transaction，再由
journal/recoverable generation 重放，不能在同一 epoch 混写。

运行时只用已校准 profile 加当前 queue/residency 信号决策，不在用户交互中同时执行 CPU/GPU 两份像素。离线 replay、
CI 或低频非交互采样校准 prediction error。profile 必须有最大年龄和适用状态包络；首个 submit/write 前 power/thermal、
queue delay、residency 或带宽离开包络就直接选 CPU。

运行时使用 circuit breaker：单次 measured end-to-end 超过 paired/predicted CPU upper bound 1.25× 或绝对交互预算，立即隔离
该 bucket；较小 prediction miss 连续超过校准阈值也降级为 CPU-only，直到 profile 重建。route 已开始后不得把同一 epoch
剩余页改走 CPU；只有整个 pending transaction 尚未 publish，且“已耗时间 + abort + CPU replay”仍在 tail guard 内时，才可
整操作 abort/replay。否则完成当前 operation、记录 regret，并让后续 operation 走 CPU。该规则承认不可预测硬件事件，但
阻止慢路径持续成为产品默认或用混合结果掩盖退化。

### 8.2 Replica source ETA

```text
SourceETA = calibratedCriticalPath(source -> target, {
    sourceReady, queueDelay, codec,
    bytes / effectiveBandwidth, bindingPublish, contention
})
```

系数按 device、direction、StorageClass、batch-size bucket 更新。策略使用稳定 EWMA/quantile，不直接追随单个异常值。
来源候选必须是适用 exact valid replicas；各特征以真实 materialization 的依赖/重叠和完成分布校准，不把阶段 P95 之和
命名为 SourceETA 的 P95。与 36/38 的迁移/回收模型采用同一口径。

### 8.3 Atlas promotion

```text
Promote if:
populateCost + expectedReads * imageSampleCost + riskMargin
    < expectedReads * bufferSampleCost
```

必须使用完整 composite/display trace验证，包括 populate、gutter、dependency invalidation 和回收，不允许只比较 shader
单次采样吞吐。

### 8.4 Prefetch horizon

```text
Horizon = requestToConsumerReadyP95 + safetyMargin
```

`requestToConsumerReadyP95` 为完整 materialization（含 scheduler/queue/codec/transfer/binding）的实测分布分位数，
不重复加 scheduler，也不把阶段 P95 之和当尾延迟保证。Horizon 按 38 的 configuredMin/Max 限幅；以 deadline miss 与
错误预取 bytes 的 Pareto 曲线选择，不以 hit rate 单指标选择。

### 8.5 Eviction

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

### 10.1 BR1-PERF CPU 前置门禁

2026-09-20 在同机同类构建参数下、优化开始前的历史审计基线：

| 用例 | 历史 `origin/master@9a24ae0d8c` | 优化前 BR1 审计值 |
|---|---:|---:|
| `stressTest` | 2.529 s | 144.530 s |
| `stressTestLazyCopying` | 0.990 s | 99.605 s |
| tiled manager suite | 11.826 s / 21 cases | 260.062 s / 23 cases |
| 32767 blank reads | <1 ms / 49.0 MiB RSS | 331 ms / 485.7 MiB RSS |

tiled manager suite 的 case 数不同，只作为整体现象，不替代精确同用例 gate。BR1-PERF 结清必须以同机、同构建
profile、重复运行和保存原始结果为准。对 upstream 单轮小于计时分辨率/噪声下限的 microbenchmark，增加固定循环量，
直到 upstream 中位数至少 100 ms，再比较单位操作成本；不得直接对“<1 ms”结果计算 1.2×：

- blank/default read：零 PageKey/version/replica allocation、O(1) pixel backing、wall time ≤ upstream 1.2×；
- resident read ≤ upstream 1.2×；
- resident write、无 history ≤ upstream 1.3×；满足 handoff 前置条件的常见桶必须稳定选择 handoff，并达到
  before-image copy=0、new payload allocation=0、payload migration=0、retirement payload=0；
- first-write COW/undo ≤ upstream 1.5×，且同 mutation 的同一未发布段每页最多一次 COW；
- `stressTest` 和 `stressTestLazyCopying` 均 ≤ upstream 1.5×；
- K 固定、N 扩大时 production epoch commit 不出现 O(N) rebuild/export/sort/extent scan；
- resident hit 的 heap request/lease、global request-map insert、provider active-lease scan、tile-unlock commit 均为 0；
- current/history/pending/in-flight/retiring/optional backing 有精确字节 ledger；tiny-budget、持续写、旧 View、undo、GPU/I/O
  last-use 和 provider retire 拒绝下均不越硬上限，并给出背压/`ResourcePressure` 与 drain 证据；
- 既有 BR1 correctness/property/fault test 不回退。

阈值是阶段退出上限，不是性能目标；结构硬门槛失败时，即使总耗时达标也不能通过。
上表是历史起点。两个原始 stress 主要测试 1 BPP、整页 fill/alias、未暴露 writable pointer 的锁与 history/delete；
lazy-copying 单项观察低于历史阈值不证明实际像素写、4/8/16 BPP、SIMD brush 或整体 CPU 等价。计时必须单独执行且 endpoint 一致，
至少 5 次用于 median/离散程度；P95/P99 另用足量事件与独立 replay 并报告样本量/不确定性，不以 5 个 run 外推尾分位数。
BR1 须同时提交 M 的同义管理对照和 CPU/CpuRam 的 K/resident E 吞吐/延迟；上述 1.2×/1.3×/1.5× 是相应完整 CPU 操作
时间上限，不能挪给隔离 K 或用它放宽管理结构门槛。BR1-PERF 还必须独立通过 5.6 的 CPU 同义管理不劣性判据；
只通过上述阶段上限不得宣称管理等价或 BR1-PERF 结清。M 各阶段预算在配对基线冻结时事先分配，管理 self 与总操作共同检查。
新增吞吐门槛按硬件 profile、固定资源和 5.8 的端点冻结，不把延迟阈值取倒数充当吞吐阈值。

<a id="handoff-value-gates"></a>
#### 10.1.1 M6局部资格、业务价值与GPU条件评价

2026-10-06修订：M6 K1下降20%/K16下降30%不再作为阶段硬出口；其原协议结果和研究目标保留。当前CPU能力按[92 §6.1](92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)验收同状态命中正收益、miss及固定M5控制不劣性、零额外copy、资源和metadata结构要求。本文§5.6的M容差、§10.1的upstream上限以及§10.2产品门均不因该修改放宽。新门必须事前冻结并取得新样本，不能把已有诊断区间改标签后宣告通过。

报告分开给出三项裁决：**M6机会型能力、真实业务默认策略、GPU硬件profile**。局部能力通过不要求把尚未实现的GPU接入CP3，也不授予自然命中率或业务收益。业务trace必须覆盖来源/保留/维护、命中与拒绝、代际冻结、恢复和退出；初始双副本仅用于隔离局部因果，不假设免费产生。按实际分层分布检查`p·d−(1−p)·e−q`与完整E；模型项和定义见[92 §6.2](92_br1_m6_m8_execution_baseline.md#m6-business-value)。相同未发布段的pending复用不重复记成handoff收益。

GPU评价须区分“避免新增显存需求”和“降低完成延迟”。独显自然已有CPU/GPU exact副本且旧last-use完成时，前者可能更有价值；UMA双映射同一allocation不构成独立before。旧GPU读者未完成时，复用增加依赖或被拒绝，Fresh可能保留并行；算法需要独立旧输入时也不能强行原地写。已有精确副本必须满足内容/layout、物理独立、恢复retention与generation条件，不能用derived display替代。

对照Fresh应采用正常池化/子分配，resident RMW只做必要本地COW，full overwrite不复制无用旧像素。不得默认每页对应一次昂贵的驱动分配，或把handoff一律解释为省PCIe传输。Vulkan建议大块子分配；复用中的读后写仍需执行依赖，依据[Khronos内存指南](https://docs.vulkan.org/guide/latest/memory_allocation.html)和[同步示例](https://docs.vulkan.org/guide/latest/synchronization_examples.html)。GPU kernel、CPU准备、queue、cache/order、copy及publication用同一依赖trace确定关键路径，不把时间简单相加；更高GPU带宽不会自动消除CPU管理成本。

后继GPU阶段至少事前登记下列轴；required交叉组合按真实consumer和支持范围冻结，不把未实现组合填Pass，也不根据结果挑选正例：

| 轴 | 对照与必须记录 |
|---|---|
| 设备/访问路径 | UMA shared与dGPU resident分开；device/driver、executor、格式/layout、实际backing，CPU/Rosetta结果不替代GPU |
| 恢复来源 | 自然已有独立exact alternate／没有／物理alias／未Ready或旧generation；H与Fresh起始副本集合、预算相同 |
| 执行依赖 | source空闲／真实在途reader、display或transfer；miss原因、等待、并行重叠和最后使用完成 |
| 工作形状 | partial/RMW／完整输入覆盖；可原地／需要独立源；首写／多次发布／同段多dab |
| 资源 | 正常／接近硬上限；每域payload与metadata的used/reserved/peak、retirement尾、驱逐/恢复/拒绝/完整drain；纳入合法回收后Fresh对照 |
| 完成端点 | CPU prepare、GPU timestamp、实际copy方向/字节分开；GpuConsumable、PublishedEpoch、Visible等按业务选定同义端点，cancel/old-version恢复另验 |

GPU的延迟优先或容量优先策略必须在profile测量前冻结：主要收益指标、最小有意义收益、正常/压力下延迟与尾预算、必要恢复成本、固定对照及统计family；不能测后挑“延迟或容量有一项好”就通过。容量优先仍受§10.2产品交互/回退门，不能以少分配掩盖GPU等待。当前Vulkan provider未实现native执行，以上仅为后继验证合同；没有GPU收益百分比、30%可达性或AutoPreferred资格。

### 10.2 GPU/UMA 相对 CPU 的产品门禁

对 W0–W8、格式/文档矩阵和上述 GPU 劣势 profile，使用相同输入、输出质量和 observable endpoint 比较产品 Auto 与
CPU-only：

- 10.1 必须先通过；不得用尚未恢复主干级性能的 PageStore CPU 路径作为较慢分母，给 GPU/UMA 制造虚假相对优势；报告还需
  保留同机 upstream/mature CPU 的归一化结果；
- route 校准必须使用当前实际 workload 的端到端分段结果（含真实像素修改、history/delete、迁移与可见性），不得从
  no-op/lazy-copy stress 的胜负推导 brush/composite 加速资格；用实际依赖关键路径校准，不把分段 P95 相加当作整操作 P95；
- 5.9 的 M/K/X/E 证据齐全，缺少真实 dGPU/UMA 实测时该 profile 不能取得资格；CPU-only 功能可继续，不用 fake 补性能结论；
- Auto route 的 end-to-end median/P95 不得高于 CPU-only 1.10×；
- Auto route 的 P99/最长交互停顿不得高于 CPU-only 1.25×，且仍须满足绝对交互预算；
- fallback 本身的 route/capability/PageStore 开销不得使 CPU 路径高于直接 CPU 1.05×；该开销对照从相同 valid replica set
  到相同 endpoint，双方均包含必要 materialization，不能拿需读回的 fallback 与 RAM-ready 内核直接求比；
- 单个 accelerator bucket 只有在校准数据预测至少 10% P95 收益时才 `AutoPreferred`；实测稳定超过 CPU 1.15× 或
  tail 超过 1.25× 时取消资格；
- tiny workload 保持每次操作的 batch/dispatch 语义，先重复到 CPU 中位数至少 100 ms 再比较单位成本；这不替代原到达率
  下的交互尾延迟测量，也不能通过合并成大 batch 制造 GPU 收益；
- 报告必须同时给出 CPU-only、forced accelerator 和 Auto 三组结果。forced accelerator 只用于诊断，不能掩盖 Auto
  已路由 CPU 的事实。
- 除交互延迟，还须提交固定资源/到达率及饱和 sweep 的完成吞吐、queue/backpressure、drained total work 和峰值退休内存；
  不满足预先冻结的 workload 吞吐预算时同样不能 AutoPreferred，不能只通过内核吞吐或单次延迟。

这里的 1.10×/1.25× 是“不能严重劣于 CPU”的硬上限，不代表 GPU 成功目标；正常 `AutoPreferred` 应有正收益。若某设备、
格式、brush、page-count 或并发状态无法满足，保持 CPU route 并将相应 bucket 标记 `AutoPreferred=false`；只有 correctness
本身不支持时 capability 才是 `Unsupported`。不能因为 GPU/UMA 名义可用而强行启用。

### 10.3 UMA

- W0/W1 在同一兼容驻留 backing 上发生真实 CPU↔GPU 交接时，`DomainSyncCopyBytes == 0` 且 copy count 为零；
  按 5.7/5.11 给出适用条件与计数覆盖，CPU-only 未交接不构成此项 Pass；
- CPU/GPU ownership golden 全通过；
- shared path 在完整 trace 中满足交互预算，不能只证明功能；
- CPU 在 shared mapping 上的 resident read/write 分别对照原生 CpuRam/upstream；超过 1.20× 或 tail 1.25× 时，该
  StorageClass 不得作为 UMA CPU hot backing，改用 CpuRam + dGPU-style replica/CPU route；
- GPU 使用 shared memory 在带宽争用/低功耗下仍服从 10.2；零 domain-copy 不能抵消 kernel/带宽劣势；
- derived display copy 独立统计。

### 10.4 dGPU

- 强制小预算完成 VRAM→RAM→SSD→RAM→VRAM；
- per-page/per-fault submit 为 0；
- dirty authority 无不安全解绑；
- batch/deadline policy在 W0–W8 无 starvation。
- 本地 VRAM、GPU remote-host、CPU BAR-mapped 三种访问独立分桶；同域 GPU direct/VT 对照与 RAM Tile 异构对照分开；
- cold/small workload、queue contention 和传输成本使 10.2 失败时，该 GPU profile 不得 AutoPreferred，前置 CPU route
  必须计入当前实际副本到交付端点的 materialization。预算无法满足时可观察地背压/降级，不能以假设 RAM-ready 掩盖
  fallback 代价，也不能因读回昂贵就重新启用未取得资格的 accelerator。

### 10.5 SSD

- SessionSpill/RecoveryCheckpoint failure matrix 全通过；
- GC 中断可恢复；
- cold fault和write amplification有可复现报告；
- disk full保持旧 authority并触发 backpressure。

### 10.6 Temperature/layer pruning

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
M/K/X/E classification and paired baseline id / semantic scope
metric scope(management-self,lifecycle-inclusive,resident-kernel,handoff-transfer,endpoint) / timer boundaries-exclusions
executor / backing domain / access path / heap-type-cache attributes
initial exact-generation valid replicas / required endpoint / residency evidence
read-write-RMW / N-K-H / cache state / threads-in-flight / batch / arrival rate
document/format/layer graph
brush/preset/input trace id
VRAM/RAM/SSD budgets and watermarks
policy/profile version
raw event trace location
P50/P95/P99 metrics
completed ops-pixels-logical-bytes per second / physical traffic or N-A
M self / K duration / X direction-bytes / critical-path overlap / attribution residual
setup-cold-warm / drain cost / retired backlog peak / profile budgets
read scope capture-release / cold binding / warm guard / full operation boundaries
read outcome counts / fallback reasons / retry counts / allocation-and-lock scopes
M required buckets / relative-absolute margins / confidence level-method / paired sample plan
M ratio-or-difference confidence bounds / Pass-Fail-Inconclusive-NotMeasured
correctness/validation result
CPU-only / forced accelerator / Auto route results
route decision、profile freshness、predicted CPU/GPU ETA 与实际 regret
decision and rejected alternatives
```

上述是报告的必需信息，不声明当前 trace/recorder 已自动输出全部字段；未实现字段须补充可复核证据或标缺测，不能填默认零。
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
- M 的主干 tile 管理对照与 K/E 的 RAM Tile 吞吐/延迟对照分别成立，并按 5.9 同 workload 关联，不能以一项替代另一项；
- 报告包含 tail latency、amplification和capacity，不只均值；
- 所有 hard correctness gate 为零失败；
- GPU 劣势 profile 下 Auto 相对成熟 CPU product path 达到 10.2，未达标 bucket 已取消 `AutoPreferred`；
- 最终 profile 不改变 32–38 冻结的身份、状态机和接口边界。
