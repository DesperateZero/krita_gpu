> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1/M5 批次 1–7 收敛执行记录（2026-09-25）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

> 当前状态：后续 [89](89_br1_m5_reaudit_findings_resolution_20260925.md) 已在 `6ac53223ef`、`095193d11a` 修复 88 重开的资源、管理成本和 selector 问题，并以最终源码重跑双架构矩阵。**M5 已重新达到关闭条件。**本文与 88 继续保留为中间执行及复审记录；当前验收状态以 89 为准。

> 后续复审修正：同一源码上的 [88](88_br1_m5_post_convergence_reaudit_20260925.md) 已复现多 Store 物理 RAM 超限和 MetadataArena owning 分配漏计费，并确认剩余管理成本与审计口径问题。**当时的 M5 整体关闭结论已撤回，资源及相应清理门重开。**下文保留当时的实现、实验和关闭判断作为历史记录；该中间状态随后由 89 关闭。

本文以 [85](85_br1_m5_code_readiness_audit_20260924.md) 的问题清单为基线，按
[86](86_br1_m5_final_convergence_plan_20260925.md) 的顺序记录已经落到当前源码的实现和仍保持开放的验收项。
它是执行记录。批次 7 已在同一最终源码提交上完成 M5 要求的正确性、资源、结构、兼容性和 selector 门禁；
本文据此关闭 M5，但不把 M5 结论外推为正式 CPU BR1-PERF、M6/M7 或完整 BR1 优化版本验收。

对应 Krita 源码提交为 `06016dafac61d3a979a89bea9f52fdb334f5a8ed`（批次 1 与 2B）和
`4544efdf1e499e37ddf62cc2c2961fbc203ac087`（批次 2A、3 及相关清理）、
`f789eaba36813ec4126dcb23b2e6800af71359b6`（批次 4）、
`1df35725bdba5c10ab0b00ea6ed101f7d6692613`（批次 4 空 overlay 修正）和
`c3a627262a81d5f065a63522613496c417865208`（批次 3 退出条件与批次 5 失败契约前置）、
`419b6efb2edd3da1208f2db0cd93ca10c9c23d31`（5A compatibility copy 失败回滚）和
`7572c37cc5a522ab760a14a378078d55a684581d`（5B iterator write boundary 收缩）、
`061b4c0b8e`（5B 共享 iterator mutation scope 与 boundary registry 删除）和
`ca1793a556`（5C tile capability 有界化与保留状态裁决）、
`8e8d478ef0`（批次 6 热路径诊断、测试 provider 与 default revision 收口）和
`37939881ba`（批次 6 ownership 事实拆分与裁决），以及
`db42387d2d`（重新编译业务测试发现的 borrowed iterator fallback 与单次 seal 修正）、
`fe5da2706a`（压力测试资源完全归零断言）和
`a0400cf0f7484004dd520e5c03dbc71cbe6827b4`（selector mutable hot branch 最终收口）。

## 当前结论

| 批次 | 当前状态 | 已落地范围 | 仍开放 |
|---|---|---|---|
| 1：domain 版本协议 | 已完成 | storage 线性化点产生 revision；provider journal 保留每个 physical 的最新事件；ledger 拒绝旧、冲突及未准入的新观察；双架构全矩阵与并发压力通过 | TSAN 环境缺口已单列，不冒充通过 |
| 2A：产品有限预算 | 已完成 | 正常 tiled backend 从现有图像配置一次性推导 provider 与 Store limits，在 provider/store 初始化前生效；多 manager 压力仍经既有进程物理 allocator | 正式跨文档性能容量规划属于后续 BR1-PERF |
| 2B：MetadataArena | 已完成 | directory、锁外候选 block、安装、取消和析构均由现有 backing controller 预约、转 live、释放；零/极小预算和归零检查通过 | 无 M5 阻塞项 |
| 3：物理域事前准入 | 已完成 | RAM↔SSD 在物理变化前对所有 owner 全有或全无预约；复验 physical/revision/observer set；I/O 失败保留源；journal 只核对与确认；tile pin 以 bool 传播失败 | TSAN 环境缺口已单列，不冒充通过 |
| 4：overlay seal/替换/取消 | 已实现并通过交叉路径回归 | native 多页和 generic 单页共同使用 PublicationCoordinator 的短寿命 overlay candidate；proof、metadata detach、overlay 安装和历史回收只有一份协议 | root commit 继续由 `KisPreparedMutationCommit` 负责；native pin、generic completion 和各自私有写取消仍保留为必要边界 |
| 5：compatibility 收缩 | 已完成 | tile lock、wrapper、compressor、H/V/random iterator 与 packed/planar body 已传播 swap-in 失败；PageStore-backed exact/rough copy 中途失败取消整批并从 canonical before-image 恢复 index；writable iterator 共享一个 native mutation；独立 iterator boundary 表已删除；tile capability 固定为一个 read 槽和一个 write 槽；剩余 cache/intent/pin/anonymous 状态均有不可推导的寿命反例 | backend-unavailable 纯 legacy void API 保留为非 BR1 模式的最小 ABI fallback；它不计入 BR1 原子性结论 |
| 6：冗余与口径 | 已完成 | metadata transition 关闭态不再读时钟或更新共享原子；CPU reference provider 移入 tests support；default revision 只经 owner import/reserve；5 个混合 `split` 拆为 21 个单 owner 事实 | 43 个静态 unreached 候选仍按其他配置、模板/虚调用和行为证据保留，未误报为死代码 |
| 7：关闭证据 | 已完成 | 最终提交双架构 7 套核心、Painter、tiles3、Vulkan foundation 全通过；结构 gate 与自测通过；压力退出资源归零；冻结 selector v2 通过 | TSAN 混合插桩结果为 Inconclusive；完整 BR1-PERF 与 M6/M7 仍开放 |

因此，85 的旧快照覆盖、产品仍使用无限占位、MetadataArena 空 bucket、swap 后才批准预算四项阻塞均已有真实实现路径；
批次 3、批次 4 和批次 5 的源码收口已达到 86 的实现退出条件；C3.4 的剩余适配器都有真实消费者、
不同寿命和对应反例，不再维护第二份 canonical 状态。批次 6 已完成源码与结构口径收口，批次 7 的 M5 门禁也已通过。
因此按 86 的两个出口定义，**M5 在 `a0400cf0f7` 关闭**。完整 BR1 优化版本仍需 M6/M7 和 39 的正式 CPU BR1-PERF、
生命周期与尾延迟资格，当前不能宣称完成。

## 冻结的产品预算推导

所有来源值来自 `KisImageConfig`，单位为 MiB，经检查后的整数运算转为 bytes。负值或溢出使 backend 初始化失败；
零值保持为零，不静默替换成无限值。记 `R = tilesHardLimit`、`P = poolLimit`、`S = maxSwapSize` 的 byte 值。
若这些有限值不足以建立 PageStore 的必需 metadata directory，tiled data manager 会禁用该可选 backend 并继续使用既有 tiles3 路径，
不会把一个配置失败但仍被挂接的 bridge 暴露给旧 tile API。

| 限额 | 来源/公式 | 计费粒度与权威 | 拒绝/释放 | 最小可工作行为 |
|---|---|---|---|---|
| tiles3 provider | `R + S` | 每个真实 physical payload 一次；provider 是 allocation 身份与 payload 存量权威 | 分配前硬拒绝，最后 logical reference 释放 | 小于一页时首次需要 payload 的操作失败 |
| Current logical | `R + S` | owner ledger 对 physical 只计一次；alias 按 class 优先级共享该项 charge | publication/reclassify/domain move 使用同一 reservation 槽 | 零值不允许安装 Current payload |
| History logical | `R + S` | 与 Current 相同的 physical 去重规则 | history 释放或 retirement 终结时归还 | 零值不允许保留实际 history payload |
| Current/History domain | CPU=`R`，SSD=`S`，UMA/VRAM=`0` | ledger 是 Store 分类权威；tiles3/swap allocator 是进程物理库存权威 | 目标域先预约，成功后以 signed delta 原子迁移 | 目标域为零时保留有效源并返回失败 |
| ActivePending | `R` | 未发布写 payload，按 physical 一次 | cancel/seal/retirement 的既有终结 owner 释放 | 零值使首次需要 pending payload 的写失败 |
| InFlight | `0` | BR1 CPU 当前没有 GPU transfer provider | 所有实际请求均拒绝 | 零值是明确未支持，不是空覆盖 |
| RetirementDebt | `R + S` | detached physical 的终结分类 | provider terminal release 后归还 | 无可用 debt escrow 时在暴露资源前拒绝 |
| OptionalCache | `R + P` | Store default/cache 的实际 owning allocation | reserve 后分配，缓存析构释放 | 默认 `P=0` 时仍由 `R` 支持必需 default read；总量为零则首次需求失败 |
| MetadataArena | `R + P` | Store metadata directory 与实际 arena block；逻辑 record 不重复计像素 payload | 候选 block 分配前 reserve，安装转 live，冲突/析构释放 | 零值在 directory 初始化前失败 |
| Durable capacity | `S` | 所有 class 的 SSD live 与净增长合计 | RAM→SSD 预约净 SSD 增长，SSD→RAM 不新增 durable charge | 零值拒绝 swap-out，resident 源保持有效 |

aggregate class 上限对域迁移使用净 class 增长；per-domain 上限仍预约目标域正增长。因此恰好占满 Current logical 的 RAM 页可以迁移到 SSD，
同时 SSD 目标或 durable 容量不足仍会在写 swap 之前拒绝。

## 本轮唯一权威与已删除的事后批准

- `KisTileDataStore` 只拥有 physical resident/swap 状态和单调 revision；它不决定 Store class 预算。
- `KisTiles3PageReplicaProvider::ResidencyObserver` 只把同一 physical 的 observer 集合冻结成一次转移，并保存最新 journal 投影；它不另造物理顺序。
- 每个 `KisPageOwnerLedger` 通过一个 domain admission authority 冻结该 owner 的 physical/class 状态，并使用既有 `KisBackingBudgetController` 预约。
- class 变更的冻结集合和预算由一个 move-only `KisBackingClassChangeReservation` 持有；publication 不再分别保存一份 changes 和一份可脱节的 budget token。
- `synchronizeBackingDomains()` 只验证与确认已经由 token 安装的 revision。发现 owned physical 的更高 revision 会失败，不再扫描后事后改账。
- swap allocator 容量失败与 swap-in I/O 失败改为返回失败；已分配 chunk、SSD 源和 RAM 源各自按失败点保留或归还，不再以 fatal 作为资源协议。
- swapper 离开 iterator lock 后再做两阶段准入；候选引用按 64 个固定批次处理，不保存与总 tile 数成比例的临时列表。

注册和终结也加入同一互斥关系：physical 注册期间不能开始 domain transition；domain/class claim 期间不能注册、重分类或释放；
provider 注册先占用唯一 ID 槽位，避免虚调用成功后因并发冲突留下半注册 observer；publication 取消和安装失败立即释放 class claim。

## 批次 4：overlay 发布协议对照

`KisPreparedOverlayUpdate` 是 PublicationCoordinator 内的 move-only、短寿命准备结果。它只保存本批 change、精确 superseded proof、
metadata detach candidate 与是否已安装；不复制 transaction 生命周期、writer 集合或 committed root。候选建立时验证活动 transaction、
key/generation 和 ledger proof，锁外一次准备 metadata，回到 owner gate 后复验精确旧 overlay 与新旧 proof，随后一次安装 metadata、
替换 overlay 并收集不可达历史。未安装候选析构时只撤销自己接管的新 proof，旧 overlay 始终保持可见。

| 原分支 | 共同实现 | 已删除位置/状态 | 行为验证 |
|---|---|---|---|
| native seal 自行枚举旧 proof、构造 detach transition、prepare/install metadata | `prepareOverlayUpdateLocked` + `KisPreparedOverlayUpdate::prepare/tryInstallLocked` | `KisPageMutationSession::sealImpl` 中本地 `superseded/transitions/candidate` 编排已删除 | `sealPreservesReaderChanges`、`sealPreparationClaimsAndSibling`、`failedSealKeepsEarlierSegment` |
| native seal 自行 revoke 旧 proof、安装 proof/removal、收集历史 | 同一 candidate 的精确复验与批量安装 | `sealImpl` 中 `historical`、逐 proof revoke/install/setRemoval 分支已删除 | `capturedOverlayConcurrentSegments`、default/alias/removal 全套回归 |
| generic finish 自行读取 prior、立即 `applyOwner(DetachPreparedVersion)`、revoke/install/collect | 单页作为一项 `OverlayChange` 进入同一 candidate | `KisPageStore::finishWrite` 中第二套替换协议已删除 | `supersededOverlayUsesHistoricalLifetime` 覆盖 native/generic 四种前后组合、7 类旧读者、成功/abort/新 proof 失败 |
| 两入口分别保管新 proof 的失败撤销 | candidate 在验证成功后接管新 proof；入口保留各自 private write 的物理取消出口 | 共同 proof 失败协议不再由入口拼装 | `genericRemovalRemainsAbsentUntilSeal`、`consumedGenericLeaseCanRetryAbort`、中间 proof 失败批次回归 |

保留的入口差异没有进入共同事实层：native 仍以现有 entry/claim 承担多页原子批次和 CPU pin，generic 仍消费单 lease 与异步 completion；
失败后的私有 allocation 继续由各自既有 cancel 路径终结。committed root 发布未并入 overlay candidate。

全量 tiles3 压力回归随后暴露了一处空变更边界：native session 的 reserved write entries 可以非空，
但所有写入均为 no-op 时 `overlayChanges` 为空。seal 过去把 reserved entry 数量误作需要发布的 overlay，
最终以空诊断返回失败。`1df35725bd` 改为以实际 `overlayChanges` 判定是否进入 overlay 发布，
并为所有 bool-only seal failure gate 补齐非空诊断。固定 seed 全量压力和既有 32 组 packed no-op 用例均通过。

## 批次 3 收尾与批次 5 失败契约、copy 回滚

- `KisTile::lockForRead/Write` 与内部 swap pin 改为 bool 契约。失败表示没有获得 tile lock 或 backing pin，
  调用者不得读取 `data()`，也不得执行对应 unlock；COW clone/pin 失败会撤销源 pin 和 mutex。
- swap-in 的 mapping、allocation、decompression 三个位置提供一次性确定性故障注入。
  低层回归验证失败后数据仍为 swapped、chunk identity/size 和 swap 用量不变，随后重试恢复原始字节。
- PageStore 回归同时验证 physical slot、domain/revision、journal、live/reserved budget 与可见 current 均不因失败改变；
  `ensureTileDataLoaded()` 不再把一次真实 I/O 失败当作 stale race 静默重试。
- `KisTileDataWrapper`、compressor、packed/planar body 和直接 tile 调用点检查 bool 结果。
  compatibility batch 在 body 失败时取消未发布写并刷新派生索引，不把失败重放到另一条管线。
- exact/rough `bitBlt` 的 compatibility 路径现在由 scope guard 统一终结：任何早退都会先取消私有 mutation，
  再从 canonical before-image 重建目标范围的 hash/extent/read cache；成功 publication 不做额外刷新。
  6 组 mapping/allocation/decompression 回归覆盖 partial exact copy 与 whole-tile rough copy，确认早期页、提交计数和失败源均保持原状。
- H/V iterator 的多页预取采用全有或全无回滚；未成功加锁的 old tile 不再进入 unlock，跨行/跨列失败清空公开指针。
  random accessor 在 miss 失败后保持 cache 计数一致，只移动已初始化的 cache entries，既有有效项可继续命中。
- writable H/V/random iterator 直接持有 opaque tiles3 write scope；backend 复用 `cpuMutationBatches` 中已有的 native mutation，
  同线程嵌套 iterator 只增加 client，不再创建第二个 transaction/session。tile guard 先释放，最后一个 iterator client 再 seal；
  跨线程最后析构使用既有 legacy-unlock 终结边界。计数降到零后 map entry 只作为终结 barrier，不能被重新加入或借用。
- 原 `iteratorWriteBoundaries` 表、register/unregister API、base iterator key/thread 字段以及 H/V/random 的注册分支已全部删除。
  `cpuMutationBatches` 现在同时承担显式 scope 与同线程未发布写的唯一发现职责；iterator 只依赖 DataManager 的 opaque RAII 契约，
  没有把 backend include 扩散到 iterator header。

这些变更闭合了批次 3 的 read mapping/decompression 与 native pin 失败传播门槛，并完成了 5B 的写 scope 收口。
PageStore-backed copy 已补齐“取消 canonical 批次后恢复 compatibility 派生状态”的整操作边界。
backend 不可用时，操作在任何 PageStore 工作开始前进入既有 pure-legacy `clear`、`bitBlt`、`setExtent`；
这些 public ABI 为 void，也没有可保持有界工作集的私有版本空间。预锁或保存全部旧 tile 才能补出整操作回滚，
会把工作集扩为 O(N)，因此不为非 BR1 模式另造第二套 transaction。该路径保留为最小 ABI fallback，
不把 I/O 失败原子性计入 BR1 结论；BR1 优化配置以 operational PageStore 为前提。

## 批次 5C：保留状态与删除裁决

| 状态/对象 | 裁决 | 不能由其他状态推导的反例或已删除内容 |
|---|---|---|
| `m_pageStoreNativeReadReady` | 保留 cache validity，不是数据权威 | 相同 `KisTileData*` 不能证明它对应当前 canonical version；refresh 在外层 raw pointer 存活时必须把 cache 标成 stale，不能替换 backing |
| `m_pageStoreWriteLockCount` | 保留 pre-exposure write intent | `lockForWrite()` 到首次 `data()` 之间尚无 write lease，但 operation range 必须识别 borrowed writer，且空写不能创建 generation |
| `m_pageStoreWriteIntentOwnsNativePin` | 保留外层 pin 交接顺序 | write-first 后嵌套 read 与 read-first 后嵌套 write 可具有相同计数，却分别需要释放当前 native pin或保留旧 exact backing |
| tile lease 容器 | 删除动态 vector，改为固定 read/write 两槽 | `m_lockCounter` 让同类嵌套共享外层 capability；read-first/write 嵌套最多同时需要一个旧 read 与一个新 write backing，没有第三个合法槽位 |
| `anonymousTransaction/Clients/Failed` | 保留为 standalone legacy writers 的一个 transaction group | clients 决定最后发布，failed 在仍有暴露 writer 时拒绝新加入并使最后 client abort；mutation session 只管理单个私有 delta，不能替代 group terminal |
| `anonymousLeases` | 保留 barrier cancellation capability | client 数量不能定位仍持有 raw pointer 的 lease；`clear()` 必须先逐项取消，晚来的 detached pointer 写不能重新发布已取消 transaction |
| `cpuMutationBatches` | 保留为显式 operation/iterator mutation 的唯一线程发现源 | 已同时承担 lease 借用与同线程 live-write 可见性；原 `iteratorWriteBoundaries`、register/unregister API 和三套 iterator 注册分支已删除 |

固定两槽回归覆盖 read-first、write-first、正反解锁和 history；clear barrier 回归在 raw pointer 仍存活时执行清空，
确认旧 mutation 被取消、晚写不再发布、active transaction/write page 归零。以上保留项均为 ABI capability/cache 生命周期，
canonical page、transaction overlay 和 publication 仍只由 PageStore owner 修改。

## 批次 6：冗余删除与 ownership 口径

- 删除 metadata transition 每次调用的 `QElapsedTimer`、总纳秒/最大纳秒两个跨 shard 原子及相应 metrics 字段。
  ReferenceTest 不再以机器速度阈值判断行为，只核对 accepted/rejected transition、工作量和实际 footprint。
  诊断关闭态因此没有这组时钟读取和共享原子写。
- 全仓构造、工厂、构建选项和调用图复核确认 `KisCpuPageReplicaProvider` 只由三套 PageStore 测试使用；实现与头文件已移入
  `kritapagestoretestsupport`，并从 `kritaimage` 源列表删除。测试 provider 继续复用生产 `KisCpuResidentBinding` 的一套 helper，
  通过私有 `_p` 符号导出链接，没有复制第二份 binding 协议，也没有把 CPU reference storage 与 tiles3 storage 硬合并。
- `defaultRevisionHighWaterLocked()` 的可写引用已删除。初始 epoch 只能经 `importDefaultRevisionLocked()` 导入一次；
  default 变更只能由 PublicationCoordinator 的 `reserveDefaultRevisionLocked()` 校验并推进。中止仍消耗 revision，
  retained-root restore 只改变可见 root，不回退 lifetime high-water；现有测试验证 2→3→5 的身份序列。
- 原 ownership 清单把 transaction 与 compatibility client group、physical allocation 与 binding claim、logical last-use 与 provider 执行、
  revision allocator 与已发布 surface、binding generation 与 tile cache validity 各合成一个 `split`。现拆成 21 个独立事实：
  每个事实只有一个 writer；兼容 client/barrier 与 tile cache 作为独立寿命事实保留，不冒充 transaction、payload 或 root 权威。
- 强制重新编译 Painter 后发现，活动 random accessor 的 iterator batch 被 pixel operation 预检查误判为非法 native 嵌套，
  使四组 borrowed copy 未进入既有 compatibility fallback。当前预检查区分 operation reentry 与活动 iterator client：
  前者仍返回 `Failed`，后者返回 `Borrowed`。fallback 加入同一 mutation，raw pointer 存活时 0 次 seal，最后 client 退出时恰好 seal 1 次；
  tiles3 增加了同路径回归，Painter 更新了旧的“多次 seal”断言。该修正没有恢复第二套 transaction 或 publication。
- `8e8d478ef0` 的 `libs/image` 源码与测试变化为新增 58 行、删除 57 行；新增主要是显式 import/reserve 失败契约，删除的是常驻诊断工作，
  provider 为路径迁移。该净行数不表述为删除收益。调用图由 1473 APIs/13732 edges 降至 1452 APIs/13648 edges；
  相对本批起点，production/indirect/test-only/unreached 分类从 1010/283/137/43 变为 997/279/133/43。
  borrowed fallback 修正后 API 数不变，当前 edge 为 13650；仍未到达的 43 项没有因此被认定为死代码。

## 批次 7：最终验证与关闭裁决

最终证据目录为 [evidence/br1_m5_final_20260925](../../../evidence/br1_m5_final_20260925/README.md)，源码身份统一为
`a0400cf0f7484004dd520e5c03dbc71cbe6827b4`。最终构建重新链接后执行，不沿用旧二进制：

- arm64 与 x86_64 分别通过 7 套 PageStore/Completion：Completion 11、Foundation 28、PhysicalClaim 14、
  CpuMutation 577、ResidentRead 33、Reference 297、ReadBaseline 45，均为 0 failed/0 skipped。
- 两个架构分别通过 Painter 99/99 和 tiles3 361/361，tiles3 使用 `KIS_BR1_SEED=12345`。
  `finiteBackingLimitMatrix`、`cancelAndClaims`、swap-in 三故障点、close/retirement/history 与临时 source manager 路径均在矩阵内。
- `stressTest` 在 worker 全部退出后等待 history/retirement idle，并断言 capability、pending/deferred history、scan/job、
  全部 reserved bytes 以及 ActivePending/InFlight/RetirementDebt live bytes 为零；arm64 与 x86_64 均通过。
- Vulkan foundation contract 在 arm64 与 x86_64 分别为 14/14。首次配置遗漏
  `CMAKE_OSX_DEPLOYMENT_TARGET=12` 的失败日志保留，修正配置后的结果才计入通过。
- 最终 architecture gate 为 1452 APIs、13654 reverse-call edges、21 个单 owner ownership facts、
  16 个 runtime census groups、19 个 frozen external intrusion files；gate 和 6 个 reachability 工具自测通过。
  43 个静态 unreached 候选保持审慎裁决，没有为压低数字批量删除。

第一次冻结的 20 对 selector 试验在 `fe5da2706a` 上失败：K=1 与 K=16 的单侧 97.5% 下界分别为
0.97364 和 0.96771，低于 0.98。该结果没有被重解释为通过。生产 selector 随后把 mutable 输入集中到单一 hot branch，
并删除同一事实在多段条件中的重复判断；变更提交为 `a0400cf0f7`。针对变更后的实现重新预注册 v2 协议，固定 40 对、
每对 750 ms、无可选停止或样本替换。candidate/control 使用同字节 fixture，loader 日志确认装载不同的
`libkritaimage`。最终 K=1 的 paired median 为 0.99163、单侧 97.5% 下界 0.98685；K=16 分别为
1.01092 和 0.99773。两桶下界均高于 0.98，按 Bonferroni 给出至少 95% familywise confidence，M5 selector 门通过。

TSAN 编译与最小 runtime probe 可用；完整工程插桩下 Completion 11、Foundation 28、PhysicalClaim 14 通过且未报告告警。
CpuMutation 进入 Qt `QMutex`/`QWaitCondition` 路径后，TSAN 同时报 `double lock`，并把冲突两侧都标为持有同一个 M0。
当前 Qt 动态库未以 TSAN 插桩，工具不能正确观察 wait 的 unlock/relock，因此这次混合插桩不能区分真实竞态和同步建模缺口。
该项记录为 **Inconclusive**，既不写成 race-free，也不据此认定源码存在已证实竞态；M5 依赖确定性交错、双架构并发压力与退出资源断言关闭。

## 下一步顺序

1. 以已关闭的 M5 为稳定前置进入 M6/M7；不得重新引入并行 selector、publication、budget 或 compatibility 权威。
2. 在优化实现冻结后，按 39 完成 upstream 同义操作、M/K/X/E、吞吐、尾延迟和完整生命周期资格，才能宣称 BR1 优化版本完成。
3. 若需要 race detector 作为发布资格，先建立 Qt 与工程同步原语均可被同一 TSAN runtime 观察的全插桩工具链，再重新运行；当前普通压力证据不能替代该项。
