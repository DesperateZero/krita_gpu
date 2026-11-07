> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 目标结构整体重构工作清单（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

本轮代码及正确性回归持续更新至 2026-09-21；不将日期变化解释为新性能切片。

2026-09-23 当前执行补充：[84 全性能优化链路收敛方案](84_br1_full_optimization_convergence_and_cleanup_20260923.md)
重新审查 52 起全部优化增量，而非仅 M1–M5；以下结构目标保留，历史局部完成记录不能替代当前收敛验收。

状态：实施中；不是结构完成或性能通过报告。承接 [52](52_br1_cpu_fast_path_optimization_plan_20260920.md)，
保留 [65](65_br1_native_cpu_mutation_segment_20260920.md)、[66](66_br1_physical_exclusivity_prerequisite_20260920.md)
及其封存证据，不改写历史结果。写侧最终结构已在
[68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 冻结：旧文中的通用 `owner-issued permit` 仅保留为历史问题名，
当前统一口径是 PageStore 私有 `KisPageWriteCoordinator`、内联 plan/claim、metadata stable-slot arena、条件 backing handoff/COW
与硬内存预算；arena 和 allocation-free publication 是生产 handoff 的前置条件。`KisPageStore` 系列类的拆分、重复状态归并、
外部侵入 manifest 和重构前 R0 门槛服从
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md)，不能以机械分文件或先删兼容状态代替。

## 1. 目标与执行顺序

单一 Canonical PageStore 管理版本与可见性；已驻留 CPU 操作走轻量原生路径。
仅真实数据准备、异步等待、执行交接进入对应控制路径；工作量主要随本次访问、修改及必要保留的数据增长。

先整体重构，后统一性能测试。正确性、并发、失败原子性、生命周期及结构计数贯穿重构过程，
不等待每个切片完成吞吐采样再进入下一结构依赖。最终沿用
[39 的 M/K/X/E 判据](../../../39_virtual_texture_performance_gates.md#56-四类证据与基线配对统一定义)，
计量沿用 [20](../../../20_observability_testing_and_performance.md)，CI 沿用 [30](../../../30_p0_ci_architecture_guards.md)。
最终测试前重新冻结源码、二进制、同义操作、存储事实、容差与端点；不得把旧切片结果外推到新实现。

## 2. 六项不可放宽的结构约束

1. **统一权威和生产入口。** generation、authority、事务、历史、发布仅由 PageStore 决定；TileData 是 backing，
   tiles3 hash/binding 是索引或缓存。iterator/accessor/区域操作/画笔都要接通，native 与 generic 安全语义相同。
2. **明确可见性范围。** read scope 一次捕获、保护同一 View；写 session 保护 base 和 overlay。
   中途发布必须结束当前段，后续段重新授权，不能合并原有业务可见性边界。
3. **按就绪事实分流。** exact version 的就绪 CPU 副本即可 native read，含历史和非 authority 副本。
   共享 default 必须匹配 View；缓存 miss/tag 失配先刷新，busy/unsupported/invalid 与真正物化分开。
   暖驻留逐页访问不创建 generic request/lease，不进全局 request map。
4. **写侧只做必要准备。** 同段同页复用 pending generation/backing；guard 释放归还它持有的 pin 并汇总 dirty。
   若 segment 保留 writable 指针，必须由 segment 自己的 backing pin/claim 持续保护，否则下次访问重新 pin。
   PageStore coordinator 必须按可见性、恢复能力、alias、执行交接和失败面生成内部 inline plan：安全时移交 current allocation，
   只有旧值仍可观察或操作仍可取消/失败时才建立独立 backing/COW。瞬时物理独占不能代替选择器证明，调用方不得自签授权。
   partial preserve 未改内容，full overwrite 省源复制；删除/alias/no-op 只生成必要语义 delta；fallback backing 受硬字节预算与背压约束。
5. **准备与发布分开。** 候选 root、metadata、extent、索引和退休记录尽量预构造，以 pin/claim 保护动态依赖。
   production metadata 使用 shard-owned generational slot arena、shard-global exact/physical index 和 intrusive history；
   publication install 消费预留 slot/capacity token，不执行 allocator、rehash 或大对象析构。
   发布复验后先使 metadata/backing 完整可用，再切换 root；失败不得暴露半批。
   root 候选 token 不是数据写权限，也不能代替 provider、事务、retention/capture claim。
   保留 owner gate 的阶段不能声称已完成短发布；最后测量包括复验与安装的完整临界区。
6. **预算回收。** root retention、CPU pin、GPU/I/O last-use 分别保护逻辑版本、物理 backing、在途执行。
   满足资格才进入有预算释放；不能把全量扫描/析构交给最后 reader、unlock 或交互线程。
   合法历史占用与未回收记账分别统计，必须存在队列进度和 drain/关闭语义。

## 3. 实施依赖与当前缺口

| 工作面 | 当前事实 | 完成必须具备的证据 |
|---|---|---|
| 源消费者安全 | native copy 已使用 binding read gate；D12 物理 claim 仍仅是基础 | generic/native/physical writer 下 copy/read/transfer/retire 一致拒绝，释放后恢复；preclone 不提前消费 |
| 准备/发布 | 事务 claim、锁外候选与多维复验；§22 root metadata indexed delta、默认恢复候选化、header/精确生产预检 | root/descriptor/新增记录安装、目录输入、候选销毁/历史整理仍有 owner 成本；完整临界区及竞争重做的成本/尾延迟仍待验收 |
| metadata 存储 | 生产路径仍有 `std::list/std::map`、每页多容器和 snapshot 尺寸放大 | compact authoritative records、typed generational slot arena、shard index、intrusive history；install 零 allocator/rehash，common record 内存至少下降 25% |
| native mutation | packed/planar 写、trim 部分页、legacy tile 写、CPU access session；§16–17 私有语义 delta；§20 painter bitBlt 目标段；§24 packed 固定 View/no-op 与缩锁；§25 完整输入直接初始化新 backing、同段复用 | 混合 legacy-source copy、冷源准备及其余 multi-dab/fill/line producer；全 span/legacy 借用、generic write leases；普通 discard/无能力 fallback 初始化、swapped pending 重载；dirty metadata；统一 write-plan 选择器、条件 handoff 与硬 backing 预算未完成 |
| backing handoff | 有物理独占和 epoch admission 基础；生产 mutation 仍统一独立 backing/COW | PageStore coordinator 选择 `ReusePending/HandoffRecoverable/HandoffCommitOnly/FreshPayload/FreshDiscard/FreshCow/SemanticOnly`；协调 capture/active base/alias/history/交接与失败恢复，不靠瞬时 reader count，调用方不持有公开 permit |
| native read | CPU session 含 frozen sealed overlay；独立 H/V/random/wrapped/repeat 与 packed/planar 固定 View，cursor 有界 pin；§19 接通 painter bitBlt 的公开 const source/mask 契约 | live-writer 重叠读及完整 brush/dab 写边界、直接 tile 借用者迁移；完整冷 binding/执行交接覆盖 |
| 增量布局 | root 的 sparse persistent tree/subtree extent；§21 独立版本；§22 root delta；§23 ordered history cursor、局部 discard 与跨切片 reachability 缓存 | 未分类控制/同步兼容 GC 的完整 snapshot、单版本动态列表；目录 N、root reachability 刷新、完整 K/N/H 成本及总预算 |
| 回收 | tiles3 CPU 后台历史/退休；root/transaction/replica/树分批；§22 fused 预算；§23 每页历史 32 记录续扫、每 pass 16 keys、FIFO 与事件重扫；§32 metadata cleanup 按 candidate-page unit/time 协作分批；drain/close | root reachability 刷新、单记录保护列表、所有 current/retained/pending/in-flight/retiring backing 的硬字节预算、背压与完整成本仍待结清；candidate unit/协作时间预算不是 payload 字节硬上限 |

按依赖推进：authoritative record/snapshot 分离 → shard slot arena → shard index/intrusive history → allocation-free publication →
coordinator/fresh 路径统一 → recoverable/commit-only handoff → 生产入口及读分流 → 预算与资格。
接口应随真实调用迁移，不新增一个未被生产入口消费的 facade 后就勾选完成。

## 4. 必须逐项核验的生产入口

- `KisPaintDevice` 创建 H/V line iterator、random accessor：包含 writable 与 oldData/current 配对、线程克隆。
- `KisTiledDataManager` 的 getTile/getTilesPair、legacy tile lock/unlock：嵌套 pin、共享 wrapper、销毁边界。
- `writeBytes/readBytes` 及跨页、跨行访问：scope 与可见性边界一致，不逐页追 head。
- clear/fill/setDefaultPixel、full/partial bitBlt、alias/no-op、extent：语义 delta 与实际像素准备分离。
- 画笔的上述实际调用链和中途提交：不能以只直接构造新 accessor 的测试代替。
- memento/undo/redo、保存/历史读、swap、provider shutdown 与在途 I/O/GPU：retention/pin/last-use 分离。

当前以上是待核验清单，不是迁移完成列表。每项最终记录生产调用点及正确性测试；剩余 generic 使用写出真实控制需求。

## 5. 整体性能测试准入

六项结构约束及生产入口正确性通过后，执行同义主干 M、相同存储事实的驻留 K、实际交接 X、完整操作 E。
RAM/显存/shared backing 分桶，CPU-only 不能证明 UMA/GPU；UMA 同一兼容 backing 零 payload migration
不代表零同步/缓存/软件成本。计入 scope capture/release、完整 prepare/publish、退休调度与 drain，单列交互尾延迟。

先检查真实工作量：暖读零重复协议、同段首写一次、普通无历史热写零 before-image copy 且零新 payload allocation、
稀疏修改不全图扫描、published/retained/pending/in-flight/retiring backing 总量不越硬上限、发布和回收有界。
再冻结容差做配对吞吐/延迟；保留旧反证及新反向结果。结构通过与性能通过分别判定，不用某个 facade 的加速抵消未迁移路径。

## 6. 本轮已落代码及不可外推的边界

本节保留 D13 检查点的实现记录；其“仍同步/尚无后台”描述不是 §9 之后的当前状态。

- 源复制在触碰 bytes/preclone 之前取得 binding read gate；调用 `duplicatePinnedTileData` 复用已有 pin，
  不在持有 provider mutex 时再次等待同一物理 writer。新增有效修复前负例记录在 evidence 的 `pre-fix-native-source-copy-v2.log`。
- `PreparedCommit` 为 owner-bound/move-only/一次消费的内部候选，绑定事务 revision 和预期 current root。
  不可见的 hash slot 在准备阶段预留；取消自动释放，不能成为 root 查询、retention、transaction base 或 reachable version。
  immutable tree 构造脱离 model mutex，install 复验后安装 metadata 再切 root。2026-09-21 又补齐事务 claim 与锁外准备/动态复验，见 §8。
  undo/redo 的 retained restore 也已改为批量 metadata 候选/全部 revision 复验/安装后切 root；不再先切 root 再逐页恢复。
  正常 commit 与 restore 的失败都不得暴露半批；准备外移不等于整个提交已成为短临界区或成本达标。
- `nativeCpuMutation` 显式声明 native writable binding 与同步独立 backing 的组合能力；仅有 copy 能力不能自动选此路径。
  CPU access session 捕获一次事务 base 供 oldData，native 路由失败不重放 generic；能力不支持时在开始工作前选 generic。
  `KisCpuWriteGuard::baseVersion` 是此次准备的源版本，oldData 仍是事务 base；动态 selector 与 §10 捕获后的 frozen overlay 必须区分。
- native 空白首写保留逻辑 default before-image，只分配并初始化目标；非空页 discard 不复制源。
  期间 generic reader 后续物化旧 default 不改变 writer 的逻辑 before-image，也不凭空增加 writer 未拥有的源 pin。
  若物化发生在锁外目标准备之后、writer reservation 之前，重新进入 owner gate 后复验 exact base，
  对已变成物理 authority 的源取得必要保护，再申请 writer；不能携带过期的空 source 进入状态机。
  discard 当前仍可能执行目标 default 初始化，**不是已证明所有 full overwrite 都零初始化**。
- CPU session 的 read/oldData 已消费共享 immutable default buffer，不为每个空白 key 建 provider allocation/request/metadata。
  同一 View 的 surface/default revision 决定内容与逻辑 identity，不伪造 replica；不同 key 可共享 bytes，guard 仍持有各自 exact version。
  初始 payload manifest/adoption 拒绝 semantic default identity，防止外部任意像素冒用 default revision 破坏两条读路径的一致性。
  owner cache 上限为 64 项且 8 MiB，View/guard 的强引用可在 cache 淘汰后继续保留合法旧内容；超 cache 预算的单项仅由 scope 持有。
  单列 cache bytes、全部存活 default bytes、累计构造数及初始化 bytes（含竞争中未进入 cache 的构造），不能把软件填默认数据记为硬件迁移。
  非阻塞 try 保留；CPU session 可在原生路径等待局部 mutex/swap barrier 后重查，但不在该路径启动 swap-in。
  writer capability busy、非法 identity/retired、资源不足返回各自错误；真正 nonresident/不支持 native 才进入相应 generic 控制路径。
- legacy tile 写现在走同一个 mutation 实现，unlock 仍是原边界；operation batch 仍在段末 seal。
  共享 wrapper 的最后 unlock 可能在另一线程：仅兼容 lease 可请求 terminal seal，且必须已无活跃 writable guard；
  普通 session 的 beginWrite/seal 仍限制原线程，不将该终止交接扩展为任意跨线程写。
  新 H/V line iterator、random accessor 的直接生产实现测试覆盖跨负坐标页、oldData、undo/redo、generic write request 为零。
  这不宣称整个 traversal 的捕获范围已迁移，也不吞并历史发布边界来减少 commit 次数。
- persistent page tree 节点维护跨 surface 有序范围及逻辑页 bounds；删除 extent 只沿 delta 路径计算，
  用 3 个 surface / 6144 页的独立 manifest oracle 测试边界收缩及历史 root 不变，另测空 surface、新增和整数溢出。
  root retention 和 active transaction base 使用计数与变化事件建立候选，不再每次 collection 扫描全部事务/root。
  这是减少扫描，不是整条像素退休队列或树析构预算已完成；发布仍有必要队列/metadata 记账要继续外移。
- provider 拒绝退休的 exact replica/provider/last-use 记录不再丢失。`processRetirements(budget)` 每次最多尝试预算项，
  拒绝项轮转保留；已有 production retirement 点也会尝试最多 8 个旧记录，close 汇总 metadata 已不可见的退休债务。
  延迟 completion 复验原 operation，不重复发同一 retire；provider 尚未完成时不宣告释放成功。
  `pendingRetiredReplicas/Bytes` 与合法历史分开；本轮尚无独立后台退休调度，初次 retire 和历史扫描仍不受这个重试预算限制。
  同一 `retireOrDefer` 还覆盖默认页/初始导入/generic write/native write/host adoption 的失败分配清理；
  不仅 commit/abort 产生的 retirement effect 才有失败记账。

前一轮构建与正确性原件在 [evidence/br1_d13_20260920](../../../evidence/br1_d13_20260920/README.md)。
该目录是历史工作检查点，不使用 D13 名称宣告六项约束已结清，不运行 Dx 性能配对。
其 live-file hash 与当前代码不再匹配是预期变化，不改写旧 manifest；本轮检查点见 §8。

完整 `kis_iterator_test`/`kis_iterators_ng_test` 首次因缺 `KIS_TEST_PREFIX_PATH` 在资源路径计算失败；
补上已存在的安装目录后，NG 测试在 QtTest 正文开始前的字体资源初始化崩溃，堆栈为
`KoSvgTextShape::Private::collectPaths → KoFontFamily::updateThumbnail → KisResourceLocator::initialize`。
这批旧日志不得算通过或据此归因 PageStore。2026-09-21 已确认测试使用的安装插件目录缺少 shape 工厂，
补充 `KIS_TEST_PLUGIN_PATH` 测试专用覆盖并使用当前构建插件后，两套完整 iterator 测试均通过，见 §8。
不改字体业务代码；也不由 iterator 套件通过外推全部画笔路径/可见性 scope 已迁移。

## 7. 前一轮正确性检查点与继续边界

前一轮 CPU-only / Vulkan contract 构建通过；12 个测试可执行文件累计 QtTest totals 为 306 passed / 0 failed / 0 skipped
（包含各套件 init/cleanup，不是 306 个独立业务场景），验收还要求日志无 `SAFE ASSERT`。生产并发写补做 40 次重放；
新增确定性用例覆盖 default 物化前后交错、terminal unlock 跨线程、失败分配的退休债务、缓存淘汰后的旧 default 寿命。
测试名称、二进制、运行库和源码哈希见工作证据的 `checkpoint-manifest.json`，可用 `verify-checkpoint.mjs` 重验。
低内存测试的旧假通过/断言日志仍保留；最终检查点使用 `checkpoint-` 前缀日志。D11/D12 封存原件及分析未改写。

**这仍不是整体重构完成。** 下一轮必须关闭以下结构问题，不能用当前回归或局部 facade 替代：

1. owner-issued 原位 permit：协调 capture/旧 View/alias/执行交接和 abort 恢复，不能把瞬时 pin/ref count 当授权。
2. 继续缩短完整发布临界区：§8 已外移 proof/metadata/root 准备；默认/删除输入组装、安装、历史整理仍在 owner 内，
   重试尚无固定次数/时间上界，需要实际竞争与最终性能证据，不能将锁外 prepare 直接等同短发布结清。
3. production iterator/accessor/画笔的完整 read scope：尤其当前事务 overlay 的可见性不能偷换成 committed head 或旧 base。
   现有 legacy 写的 native 接入和 CPU session 内的固定 View，不等于所有业务操作已统一一次捕获。
4. §9 已卸载 tiles3 CPU 历史收集、首次退休及树递归析构；继续解决单页版本规模、root reachability、积压背压与完整 drain 成本，不能把分批数量当硬时间预算。
5. iterator 资源初始化障碍已解除；继续补齐画笔等真实入口、取消、关闭与交接端点，不以启动修复代替生产 scope 迁移。

这些边界关闭之后，才重新冻结当前源码与同义主干 M / 驻留 K / 实际交接 X / 完整 E 的统一性能协议。

## 8. 2026-09-21：提交核心准备外移与恢复保护

实现及回归记录在 [本轮工作证据](../../../evidence/br1_core_reconstruction_20260921/README.md)。这是正确性检查点，仍不是六项结构或 BR1-PERF 结清。

### 8.1 实际生产提交已消费的协议

- `preparingCommits` 在 owner 内冻结本事务的 delta，拒绝同事务的新 native session、generic write、adoption、删除、surface 变更、abort 和重复 commit。
  通用写在首次释放 owner 之前取得 `mutationPreparations`，request→lease→publish/cancel 用事务计数保护完整寿命，避免提交漏掉尚未出现 proof 的写。
  这些计数按事务索引，不为 commit 再扫描整个 request map；其他事务和读捕获不受本事务 claim 阻塞。
- provider proof 验证、epoch delta 准备、metadata 状态机候选评估、persistent root 构造都在 PageStore owner gate 外。
  Prepared 版本/事务 base 及不可变 provider 注册维持逻辑对象寿命；这里不读取像素，不假造 resident pin，也不是原位写 permit。
- 安装前在 owner 内复验 head；无冲突页面可针对新 head 重建候选，真正版本/表面冲突整批拒绝。
  合并 idle-history 回收还要重新检查 retention/其他事务，不能只看 metadata lease：native guard 通过受保护 View 保留旧版本。
- metadata 所有 revision 先 claim 再安装，新增读 lease/last-use 等变化会导致重做，不能覆盖后来的状态。
  默认值全目录计划另检查 page registration count；仅检查已列入批次的页会漏掉准备期间首次物化的空白 key。
  目录计数只在注册时推进，不增加每次暖读的全局计数。
- undo/redo 为源 root 取得独立 retention 后锁外构造 metadata 候选；调用者释放原 token 不会失去恢复源。
  新事务或 head 变化拒绝本次恢复；lease revision、全量/默认值恢复期间新增页触发重新准备。
  full restore 去掉了逐页在 target vector 内再扫描的二次复杂度，使用 key set 去重。

### 8.2 证据与剩余成本

新增 13 个测试覆盖 late native capture、lease revision、无冲突 rebase、冲突批次原子性、generic request/lease/首个 provider 调用的事务保护、
失败 claim 释放、恢复源 token 释放/新事务/新 head、新注册 default key，以及 12 线程不同页并发提交。
mutation 套件从 31 增为 44 个 QtTest totals；全部 14 个可执行文件累计 **339 passed / 0 failed / 0 skipped**，
包括应用级 iterator 的 9 和 11，以及 Vulkan contract 的 13；这些 totals 含 init/cleanup，不是 339 个独立业务场景。
日志还必须无 SAFE ASSERT；并发提交与生产并发写各重复 40 次。CPU-only 和 Vulkan contract 均重新构建。

测试框架仍默认使用配置的安装插件目录，仅显式 `KIS_TEST_PLUGIN_PATH` 才覆盖。当前两套 iterator 使用
`KIS_TEST_PREFIX_PATH=krita/_install` 与 `KIS_TEST_PLUGIN_PATH=krita/_build-br0-cpu/bin`（运行时均用绝对路径），
该 bin 内的 shape/color 插件与当前构建匹配。前一轮仅设置 prefix、插件目录却只有 `kritalcmsengine.so` 的启动失败记录保留。

`publicationStatistics()` 报告 candidate、root rebase、retention/metadata/目录重做，不把失败尝试从工作量中扣掉。
阶段计量已在 [20](../../../20_observability_testing_and_performance.md#113-环境变异与端点可核验性) 更新。
在此检查点，默认/删除输入组装、全批安装及历史清理仍在 owner 内；候选拒绝/旧树析构与首次退休的预算卸载仍待完成。后续回收改动见 §9，不改写本节历史证据。
持续竞争下的重做次数没有固定上界，本轮不宣称 wait-free、尾延迟有界、原位 permit 已实现或主干性能已追平。

## 9. 2026-09-21：生产 CPU 回收链路卸载

后续代码与正确性原件单列在 [回收重构检查点](../../../evidence/br1_reclamation_20260921/README.md)，不覆盖 §8 的源码哈希和原始日志。

### 9.1 实际路径与保护

- `backgroundRetirement` 是显式 provider 并发契约，不能从 synchronous completion 推断线程安全；当前 tiles3 CPU provider 声明支持。
  一个 owner 的全部 provider 都支持时，历史清理才迁往后台。未声明的配置保持同步控制路径，不冒用 CPU/GPU/UMA 通用资格。
- 提交/abort/restore/lease release/last-use acknowledge 只提交本次候选页；最后一个旧 View 释放只释放 retention 并请求历史 sweep，
  不在 reader 栈上复制整个 deferred key set 或扫描历史。当前 root 或仍有其他逻辑引用的 root 不因此触发历史 sweep。
  结束旧 base 的事务需要重新检查它可能保护的历史；普通同 head 提交使用本次 delta，避免每次都扫被长期 reader 保留的全部历史。
- 独立于画笔线程池的回收执行器处理 continuation，不依赖 GUI event loop。每个历史任务至多处理 32 条 finished transaction、32 条 root 候选、16 个历史页；
  root 候选预算按检查项而非成功删除数计。先完成待处理 root 资格记账，再判断历史版本是否仍 reachable。
  metadata 历史评估仍在 owner gate 内，但由后台分批执行；不是已完成无锁历史布局。
- 首次物理退休也进入队列，单任务至多 32 个 replica；拒绝项保持 exact identity/provider/last-use/operation，进入失败债务队列，不忙等重放。
  支持后台回收的配置在后台历史进度点最多重试 8 项，`processRetirements(budget)` 仍是显式有界重试。
  已发出的异步 completion 只复验原 operation；当前 opt-in 要求同步 provider，不能据此称通用异步回收调度已完成。
- persistent page tree 的最后引用最多在释放者线程销毁一个节点，子引用交给后台迭代释放；每个 continuation 至多释放 128 个树引用。
  已共享分支只减引用，不提前遍历/删除；后台不会递归析构整棵独占大树。候选丢弃、旧 View、model/owner 销毁都消费同一机制。
- 队列任务独立保留 owner 寿命，不持有悬空 facade。支持后台回收的 owner 最后销毁也在回收线程，非 opt-in 配置不强改其析构线程。
  native guard 仍先释放实际 CPU pin，再释放逻辑 View；后台清理不绕过物理 pin 或 GPU/I/O last-use。

### 9.2 端点与统计

`waitForRetirementIdle()` 在生产者静止时等待已调度历史和首次退休任务；失败/pinned 债务仍保留，不表示强制释放成功。
`closeSession()` 先冻结新回收调度，在 owner gate 外等待在途任务，再汇总 metadata、未开始队列和失败债务；
存在业务 capability 时关闭仍拒绝，并恢复调度。provider 退休失败保留可重试关闭状态，不重复枚举已成功退休对象。
不能在回收线程调用等待它自己的 drain/close。全局树回收 drain 是测试/静止端点，不放到 guard 析构或交互操作里。

`pendingRetiredReplicas/Bytes` 包含尚未开始、失败以及正在执行的物理退休；不能在出队时提前从债务里扣除。
另列 pending/deferred historical pages、scheduled jobs、后台退休 pass 及最大批次；deferred history 可能仍合法可达或被 pin/last-use 阻挡，不能全部算泄漏。
history 页访问区分总数与 foreground 数；树销毁区分前后台，并记录每批引用释放量。

### 9.3 尚未消除的成本

这关闭了“只有失败重试有预算，而正常首次退休及树析构仍完全同步”的缺口，但**不是整体预算回收或核心重构结清**：

- §9 阶段页级批次没有限制单页 `versions`；§23 已补 historical 索引与 32 记录续扫。单记录 replicas/protection 及 root reachability 刷新仍不受该记录预算限制。
- 显式 sweep 对实际待检查历史有成本；长期大量历史和高频新操作下，不能只以 batch 数量证明总工作量、尾延迟或公平性。
- 总队列/树引用积压、allocator 压力反馈、背压和非交互 drain 成本尚需实装/验证；provider 的 allocation budget 不是整个软件队列预算。
- 非 opt-in provider、GPU/I/O completion 唤醒，以及外部直接 pin 释放后的通知仍不能外推；显式重试/close 继续保留。
- 默认/删除输入组装、完整安装、原位 permit、生产 iterator/brush read scope 仍按 §7 推进。

性能验收必须把 enqueue、后台 CPU 工作、完整 drain/close、峰值债务和交互尾延迟一起纳入 E；只测前台返回时间会漏算实际工作。
本轮仅做正确性/结构计数与并发回归，不重新宣告 M/K/X/E 或 BR1-PERF 通过。

最终 CPU-only / Vulkan contract 构建与 14 套回归通过，合计 **345 passed / 0 failed / 0 skipped**（含 init/cleanup）；
并发提交、生产并发写、五项后台回收场景各重放 40 次，共 120 次额外运行，全部成功且无 SAFE ASSERT。
前两轮端点断言失败与迁移记录保留在同一 evidence 下，不覆盖为通过；源码/二进制/运行库/文档/日志由新 manifest 绑定。

## 10. 2026-09-21：冻结 sealed overlay 与生产 packed 读取

新增正确性检查点独立保存在 [overlay/readBytes 工作证据](../../../evidence/br1_overlay_read_20260921/README.md)，不覆盖前轮原件。
本节是继续实施，不是核心重构、CPU 同义管理或 GPU/UMA 性能目标结清。

### 10.1 可见性与寿命

- owner 内一次捕获 base root、sealed proof delta、删除集合、staged surface metadata；lookup 不追逐 current head 或可变事务。
  `epoch()` 仍为 base epoch，`isTransactionOverlay()` 区分此语义；未 sealed writer bytes 不进入读视图。
- 每个捕获对 sealed Prepared exact version 持有独立逻辑 token，native 历史/私有就绪 CPU 副本可直接 pin。
  supersede 不丢弃仍被捕获的版本；commit 保持保护，abort/删除转 detached Historical。最后 view/guard 释放才归还逻辑 token，
  物理 pin/lease/last-use 仍独立参与回收资格；版本寿命不再附着于事务是否仍 Open。
- CPU access session 的 beginRead 对所有 selector 统一捕获；fallback 使用同一捕获对象的 exact identity 和 surface metadata，
  不在缓存冷时重新解析 mutable overlay。直接单页 acquireRead 的动态 overlay 语义保留，需新可见性边界时重新 capture。
- 删除后的写意图不提前撤销 removal；成功 seal 才安装新 proof 并撤销 removal，失败/cancel 保留删除语义。
  删除操作在 provider retirement 解锁之前完整安装语义 delta，不能暴露“proof 已移除、removal 尚未安装”的中间状态。
- default revision 使用 owner/surface 生命周期高水位，abort/restore 不回退；生产 setDefaultPixel 使用 owner 分配 API。
  A→B→A 允许最终 identity 继续推进；发布按 revision 而非只按 bytes 判断默认 identity 变更。旧 captured default 的 native/generic bytes 一致。

### 10.2 真实入口与成本归因

- `KisTiledDataManager::readBytes → backend::readBytes`：在 publication gate 下选取当前 head/历史事务 overlay，完成 capture 后释放 gate；
  不通过逐页 tile wrapper。一次捕获，按页块直接 memcpy 至调用方缓冲区，每次至多一个页 pin/控制 lease，没有整区域临时 payload。
  保留负坐标、跨页/行、1/4/8/16 BPP、紧密/带 padding row stride 语义；空指针/非正大小延续 no-op。
- `commitHistory → pruneDefaultPreparedPages` 也捕获 sealed overlay，用同一驻留/控制分流读取待裁剪版本；
  `stagePageRemovalIfUnchanged` 在 owner 内复验实际检查的 exact identity，拒绝删掉后来被替换的页面。
  仍需要的像素默认值比较没有被记成跨域迁移；没有宣称这项扫描本身已消失。
- 单列 `read_bytes_capture / read_bytes_page / read_bytes_release`；page 包含 acquire/fallback、像素拷贝和本页归还，
  不是纯管理时间。无 recorder 时不读时钟；最终需重新校准扰动，不能把这些正确性运行当性能样本。

### 10.3 继续边界

- overlay capture/release 仍按 sealed delta 的 K 个版本登记/归还 token；最后释放的这部分仍同步，不能声称已经 O(1) 或硬时间有界。
  单页版本/引用容器及 metadata 状态机成本、root reachability 与总回收背压按 §9.3 继续。
- packed read 的单页 pin 不是 CPU access session 全部返回 span 的新寿命契约；后者在该阶段仍保留已访问页到 finish（§14 后默认 OperationSpans 仍保留此契约），
  legacy H/V/random accessor、planar、完整画笔 traversal 仍需各自显式 scope 与有界 hot pin set 迁移。
- 原位 permit、完整短发布及非 CPU 交接仍未完成；安全 COW 不等于写性能目标完成，不宣称全管线 lock-free/wait-free。
  在这些结构问题结清后才冻结并执行整体 M/K/X/E；本轮不重新授予性能资格。

CPU-only 与 Vulkan contract 重建通过；最终 14 套回归为 **364 passed / 0 failed / 0 skipped**（含 init/cleanup），
120 次并发/overlay 生命周期重放全部成功，无 SAFE ASSERT；架构门禁通过。源码、实际二进制/插件、文档和原始日志由该工作检查点 manifest 绑定。

## 11. 2026-09-21：生产 iterator 与 planar 读作用域

本轮独立证据见 [iterator/planar 检查点](../../../evidence/br1_iterator_scope_20260921/README.md)，不重写 §10 的历史源码哈希。
这是生产入口结构迁移，不是核心重构结清，也不是主干 M/K/X/E 性能验证。

### 11.1 固定选择与有界 pin cache

- `KisHLineIterator2 / KisVLineIterator2 / KisRandomAccessor2` 的独立只读操作在构造时捕获 current/before；
  有 history 时是 sealed overlay/base，没有 history 时 before 与同一 captured current 共用。
  current/before 分属两个受保护选择，并在同一 backend publication gate 下取得；跨页、LRU 淘汰和 reset 不重新追逐 head。
- 每个 `KisPageStoreReadCursor` 使用内嵌 4 项 LRU，只缓存所访问页，不按整行/整列宽度预取。
  current/before 是同一 exact version 时共用一个物理 guard；不同则分别 pin，最多 4 对、8 个页访问。
  空白返回该 View 的共享 default；热命中不再创建 tile wrapper、通用 request/lease 或页级 heap cache entry。
- wrapped H/V 最多 4 个子 iterator 共享不可变 scope，各自拥有独立 cursor/pin；包裹重复、条带切换复用原选择。
  不能把每 cursor 上界写成整个 wrapped 操作仅 4 个 pin。外部传入的 peer scope 校验 owner/surface/读写模式，不匹配显式失效。
- repeat-border H/V 由外层持有 scope，边缘重复行/列重建内部 iterator 时传递原选择；不能在重建时隐式取得新 head。
  新增两项先捕获、随后发布、跨上/下及左/右边缘反复读取的回归，并检查整次操作只捕获一次。
- 公共 `KisPageStoreReadPage` 内部辅助器统一 native-first 与 exact fallback，并用 move-only RAII 归还 pin/lease。
  历史及 aborted overlay 的合法 CPU 副本可读；非驻留/能力不足/无 binding 才走原控制路径，busy/非法 identity 不伪装为物化。
  通用 fallback 保持同一 exact captured version；单独回归覆盖 move、abort 后读取与 lease 释放。
- planar 不再逐页选择 current tile，改为一次 capture、每次一个页访问、直接拆平面至调用方输出；
  覆盖负坐标、跨页、1/4/8/16 BPP、零宽 channel 与空区域。H/V `nextPixels` 同步推进 before 指针，V 按行 stride 推进。

### 11.2 不隐式撤销旧 writable 指针

已有业务允许 writable iterator 尚存活时查询 exactBounds/开启读取，并继续使用先前借出的裸指针。
不能把新读构造自动解释为 writer 的 unlock/seal，否则即使已有 iterator 测试通过，也可能留下悬空指针或修改已发布 backing。
本轮试验的自动收尾方案已撤回，正式路径没有该行为。

当前保守兼容规则：

- 后端仅登记并检查调用线程的旧 writer 是否仍有 tile 访问，不在检查回调里修改 cursor、publish 或通知完成。
  该短只读检查与 unregister 共用注册表 gate，最终析构必须先注销，防止另一线程最终释放与 raw-receiver 回调交错；
  回调不允许重入 backend。此协调在操作选择边界，不能称整个 capture 无锁，也不进入驻留像素循环。
  发现这类 writer 时，iterator scope 显式标记 `observesLiveLegacyWriter()`；packed/planar 同样选择旧 tiles3 读取。
  这条路径观察现有可变 backing，**不是 immutable Epoch View**，不能计为目标结构已完成。
- 不跨线程读取 writer cache 或结束别人的写段；另一线程的独立读只看到当时已 sealed 的视图。
  显式 `captureReadView()` 从不借用未 sealed bytes。直接手持 tile writer 等未注册的生产用法仍需迁移审核。
- writable 的 no-memento oldData 仍与当前可写 bytes 别名；有 history 的 oldData 使用受保护 base。
  writable stripe cache、原 unlock/提交边界仍保留，没有把只读 4 页上界外推为 mutation dirty set 的上界。
- 新增测试在独立读前后保留同一个裸写指针、检查无新增 seal，并在随后写入/最终提交/回滚验证值；
  另覆盖异线程读不暴露或收尾未完成写。不能仅凭没有 crash 宣称 lifetime 正确。

### 11.3 下一核心缺口与验收边界

独立只读入口已经迁移，但 live-writer 重叠读还未迁移；这不是“仅剩性能调优”。下一纵向写切片必须明确真实
brush/dab/algorithm 的 mutation 边界、所有 borrowed pointer 的寿命与 before/current 语义，再消除兼容分支。
长期保留的 sampler/accessor 不得跨业务操作暗中追逐 head，也不能为了减少 capture 把多个 dab 合成一个不可见的大段。
已有 `KisCrossDeviceColorSampler` 的 paintAt 生命周期约束继续有效。

owner-issued in-place permit、完整短发布/重做上界、单页长历史与 root reachability、总回收队列/背压、
CPU access session 的全 span pin 寿命、GPU/I/O 非 opt-in 进度仍按前节推进。本轮没有证明无锁、wait-free、
全部生产路径贯通或管理不劣性；结构完成后再统一重跑 M/K/X/E，旧反证不撤销。

CPU-only、受影响的 selection 插件与 Vulkan contract 构建通过。最终 14 套完整回归共 **390 passed / 0 failed / 0 skipped**，
另外选定 7 个 paint-device 槽为 **9 passed**（均含 init/cleanup，不冒称整个 paint-device 套件）；
并发提交、生产并发写、overlay 生命周期、iterator 生命周期四组各重放 40 次，共 **160 次**额外运行，全部成功且无 SAFE ASSERT。
26 个新增数据场景与扩展的 generic helper 测试只证明这里列明的语义/结构；架构门禁、旧 D11/D12 归档校验通过。

## 12. 2026-09-21：写准备 claim 与语义 seal 一致性

本轮证据见 [write-claim 检查点](../../../evidence/br1_write_claims_20260921/README.md)。这是写生命周期结构补强，
不把 §11 的读入口迁移当作整条管线完成；历史检查点不覆盖本轮源文件和二进制。

### 12.1 按页保护准备、request、lease 与终结

- owner 内维护 `controlWritePages`，与 `cpuMutationPages` 共同检查 PageKey 冲突。
  generic write 和 full-page adoption 在第一次 provider 调用/owner unlock **之前**登记，即使尚未建立通用 request。
  generic claim 随 request → lease → publish/cancel 连续保留；provider `releaseAccess` 结束前仍不可授予同页新 writer。
  adoption 在 proof/语义 delta 安装及必要收尾后释放；失败路径同样归还 claim。
- native 首写及删除的冲突判定不再遍历全局 request/active-write map；同一未发布段同页复用不重复判定。
  同页来自其他事务的控制准备也须拒绝，不能因尚无 metadata writer 或只是准备 default 而漏过。
  这是 **owner-gated 的索引化预约**，既不是像素访问权，也不是物理排他/owner-issued in-place permit。
- 本事务仍在 native segment、generic request/lease、锁外 provider 准备或 terminal publish/cancel 时，
  不允许改变 surface/default 契约；先结束当前写段再改变。不同事务/不同页仍可继续准备和提交。
  测试以 semaphore 暂停真实 provider 线程，覆盖 request 建立前、allocation 准备中、adoption 三处以及成功/失败。
  同页冲突、metadata/commit/abort/close 必须拒绝；另一页提交必须完成，失败/cancel 后同页可重新授权。

### 12.2 删除后写入仅在成功 seal 恢复可见

- generic write 与 adoption 的准备不得提前清除 `stagedPageRemovals`。请求/lease/失败期间，
  overlay 仍解析到该 View 的语义 default；只有成功安装 prepared proof 时才在同一 owner 区间解除 removal。
  与 native segment 的规则一致，不借 preparation、copy 或生成新 identity 作为可见性事件。
- 部分写从当前 staged default 初始化目标，不复制已删除像素；adoption 提供完整 payload，
  目标描述符须来自当前 surface overlay，不能以历史 before-version 的 default 描述替换 provider seed 契约。
- captured removed/default View 可以在另一 exact version 处于 Reserved/Writable/Prepared 时走 generic exact read。
  `AttachHistoricalDefault` 仅追加独立 immutable identity，不改变 head/writer；仍拒绝 duplicate identity 和
  与任意已有 replica 相同物理 slot（包括新 allocation generation 的假别名）。物化及 read lease 也不改变 writer 授权。
  普通 `ReplaceDefaultPixel`、restore 和写转换的排他约束不因此放宽。
- 新增状态机和 owner 回归覆盖取消 request/lease、失败 completion、allocation failure、abort、seal/commit、
  default revision 变化及旧 View 跨终结读取；保留修复前失败日志，不仅验证 native read 而遗漏 generic materialization。

### 12.3 计量与剩余核心缺口

`activeControlWritePages / activeCpuWritePages` 是活跃预约数量，纳入关闭检查；
`writePageClaimChecks / writePageClaimConflicts` 是首写/删除尝试的索引探测和命中数，不是 lock、COW 或 permit 数。
固定目标页、增加无关 pending reads（0/32/256）与 writes（0/32），16 次同段同页访问仍只有一次首写冲突探测；
额外删除只增加一次探测，不创建 native generic write request。

该证据只关闭 **冲突判定扫描**，不证明完整 mutation 为 O(1)。metadata 的单页历史 H、abort 的全局 lease/request
检查、prepared proof、owner 等待、surface 级协调和退休仍各自存在成本。session pin 预算、生产 brush/dab/重叠读迁移、
owner permit、完整短发布及总回收背压仍开放；继续按结构依赖推进，不能恢复到仅围绕读缓存微调。
本轮正确性重放不能作为吞吐/延迟样本；完整 M/K/X/E 仍待结构完成后重新冻结并测量。

最终 CPU-only/selection 插件/Vulkan contract 重建通过；14 套完整回归 **414 passed / 0 failed / 0 skipped**，
选定 paint-device 槽 **9 passed**（均含 init/cleanup）。五组各 40 次、共 **200 次**额外重放全部成功且无 SAFE ASSERT。
相对 §11 新增 24 个数据场景并加强既有生命周期断言；架构门禁及历史 D11/D12 归档校验通过。
最终 `verified-*` 绑定当前源码/二进制/文档；较早 `checkpoint-*` 的 413 项通过记录保留，不与最终版本混算。

## 13. 2026-09-21：未发布 writer 预约与 RAM 驻留分离

证据见 [writable-residency 检查点](../../../evidence/br1_writable_residency_20260921/README.md)。这是生产 mutation 生命周期改造，
不是用一个 facade 的局部加速代替结构完成。§12 以前的 dirty-page 长期 pin 描述只对应当时实现。

### 13.1 预约保留，guard 归还真实 pin

- `KisCpuWriteBindingReservation` 是 move-only 的 page-local 预约，守住已经分配的独立未发布 backing。
  它与 canonical writer/transaction claim 共同存在，不分配第二份 generation，也不进入 generic request/lease map。
  binding 的同一个局部门同时排除 native/generic read/write、copy、transfer、retire；park 不开放这些消费者。
- `KisCpuWriteGuard` 释放时实际 unpin，并清除 pending Page 中的裸指针；段只保留预约与 backing identity。
  再访同页重新 pin 同一 allocation/generation，不重新首写/COW。RAM 中已就绪的 backing 只经过局部 gate/swap barrier。
  guard 尚存活时 seal/cancel 继续拒绝，销毁 session 仍由最后 guard 延迟取消，不缩短指针有效期。
- parked backing 可以由 tiles3 换出。只有 resident pin 返回 `NonResident` 才进入显式 `WritePendingMaterialize`，
  在 PageStore owner gate 外经现有 tiles3 同步 swap control 恢复；不是 cache miss、不是重新分配版本或重新 COW。
  `Busy/Retired/InvalidIdentity` 不作为缺页重试。这里仍是同步 CPU 控制路径，**不是通用异步 GPU/I/O 物化已完成**。
- seal/proof 与 cancel 不读取 pending payload，也不强制将 parked 页换回 RAM；预约保留至 metadata/proof 安装或撤销。
  provider revoke/destruction 不能释放仍有 token/guard 的 backing；旧 token 不可再创建访问，最后 token 负责归还寿命。
- 这是局部 mutex 与明确所有权，不是无锁/CAS 化，也不是物理独占或 owner-issued 原位写 permit。

### 13.2 独立 writable backing 不得消费 alias seed

检查发现旧 tiles3 `prepareWrite(DiscardContents)` 能消费 `seedNextWrite` 并直接复用 TileData。
该 seed 可能与已提交/历史页共享；即使新 allocation handle 不同，也不具备独立可变 backing 的事实。
新增 native/generic 双路径负例均复现：目标应初始化为 default，却读到 source seed 像素。

现把语义分开：普通 `prepareWrite` 只分配独立目标，synchronous preserve copy 只返回独立副本；
seed 仅由明确的完整 payload `adoptSynchronousHostReplica` 消费。adoption 仍保留零 payload copy 的合法整页别名路径，
mutable 准备不会消费、写入或撤销其他 operation 的 seed；adoption 失败由原 caller discard。
budget failure 回归同步改为验证 seed 保留、后续 adoption/retirement 正好消费并释放一次。

### 13.3 生产工作集证据与计量边界

- 64 个 dirty 页逐个借用/归还 guard：目标 writable pin 峰值为 1；同时保留 64 个 guard：峰值为 64，全部旧指针仍有效。
  后者证明没有为了降低计数而偷偷撤销借用。
- 实际 `KisTiledDataManager::writeBytes` 修改 2/32/256 页、1/4 BPP，目标 writable pin 峰值均为 1，
  generation/seal 仍每页一次，generic write request 为零；包含读回、memento undo/redo。
- 1/4/8/16 BPP 覆盖 guard 存活拒绝换出、归还后实际换出、同 generation 再访恢复 bytes、再次换出后 seal/cancel，
  以及旧 View 保持不变。parked writer 的 copy/transfer/read/retire 排他另有带/不带 preclone 的回归。
- `writablePinsAcquired/Released` 计成功返回 guard 的目标 pin，`maximumPinnedPagesPerSegment` 计已终结段的最大值；
  在段内局部累计、seal/cancel 汇总，不为每次释放增加全局 owner 锁/原子计数。
  `pendingWriteMaterializations` 计观察到真实 NonResident 后的恢复尝试；不是复制页数、实际磁盘 bytes 或硬件跨域 X。
  `WriteWritablePin` 与 `WritePendingMaterialize` 分段报告，两者仍属于 `WriteAcquire` 的子区间，不重复加总。

上述上界只针对 **native 目标 writable pin**，不包含 source/oldData read pin、metadata 的逻辑 pin 或额外 legacy pin。
此阶段 CPU access session 返回的非 owning span 仍按原契约保活到 finish；legacy iterator 的多个借用页也仍保活（§14 新增显式游标模式，默认 span 契约不变）。
因此全部业务 pin 工作集、dirty metadata/allocation 总量、回收背压与内存预算没有结清。新的重复 pin/unpin 与冷恢复成本
也必须进入最终完整 E，不得用 pin 数下降推导吞吐提升。
后续仍须完成 brush/dab/重叠读边界、owner permit、完整短发布/历史与队列预算、非 CPU 交接，再统一测 M/K/X/E。

最终 CPU-only/selection 插件/Vulkan contract 构建通过；14 套完整回归 **441 passed / 0 failed / 0 skipped**，
选定 paint-device 槽 **9 passed**；八组各 40 次、共 **320 次**额外重放全部成功，无 SAFE ASSERT。
相对 §12 新增 27 个场景，含双线程 pinned/parked 交错；架构门禁和旧 D11/D12 归档校验通过。
最终 `final-*` 绑定当前版本；较早 `verified-*` 的 440 项完整通过记录保留，不与最终结果混算。

## 14. 2026-09-21：accessor 游标寿命与区域页块遍历

证据见 [access-cursor 检查点](../../../evidence/br1_access_cursor_20260921/README.md)。在 §13 的 parked writer 基础上，
本轮把明确的移动边界接到 CPU accessor/line iterator/SurfaceOps；不把 span 的寿命默认缩短到一次函数调用。

### 14.1 显式区分操作 span 与游标 span

- `KisPageStoreCpuAccessSession` 的默认 `OperationSpans` 保留原契约：所有已借出 span 到 finish/cancel/析构才失效。
  新的 `CursorPage` 在尝试访问不同 PageKey 时释放旧页 pin，即使新页获取失败；同页访问不重复准备。
  两种模式在 beginRead/beginWrite 都只捕获一次受保护 View，淘汰物理 pin 不丢失逻辑版本保护。
- native 写游标使用一个内联 record 保存当前 guard/before-image，不再为每个换入页建立额外 heap record/hash entry。
  跨页归还 guard 后，mutation 保留 pending generation/backing/writer reservation；再访重新 pin，同段不重复 COW。
  before-image 每次仍解析同一 transaction base，不追逐 current head，也不拿 pending 内容冒充 oldData。
- generic 写游标只释放离开页的 before-image read lease；所有未发布 write leases 保留至 finish/cancel。
  没有 provider suspension 契约时，不得为了 pin 上界而换页即 publish/cancel。通用 before-image 保持原 control 获取路径，
  不为没有 native writer 的 producer 额外预热 native binding。读游标的 generic fallback 同样只保留当前 read lease。
- `KisPageStoreRandomAccessor` 显式使用 CursorPage。同页坐标移动直接偏移缓存 span，不重新调用 session/查表/pin。
  尝试跨页前先清空缓存标记和裸指针；失败后不得暴露原页缓存。native allocation 失败会使整个未发布段失败，
  换回原页不能恢复或转 generic 重放；finish 失败并撤销本段，调用方可按既有事务契约 abort 后另起操作。
  只读 fallback 的实际 NonResident、unsupported 与 Busy/非法 identity 分类不因此改变。

### 14.2 区域遍历必须与 pin 寿命一起改变

`readRect/writeRect` 从逐行跨页改成页块优先：获取一页后处理该页相交区域的所有行，再移到下一页。
否则“单页 pin”会把宽矩形每页重新 pin 的次数放大到相交行数。外部 buffer 的行序与 padding 不变，
块坐标使用宽整数，覆盖正负极限；write 的 buffer layout 从 accessor 已取得的 surface state 校验。
`fillRect` 已是页块顺序，同页多行现复用 accessor span。`copyRect` 仍先读完整受保护 source 到临时 buffer 再写，
保留重叠复制语义；**没有**把该临时 buffer、dirty allocation/metadata 或总进程 RAM 降为常数空间。

生产边界须准确表述：PageStore H/V facade 通过 RandomAccessor 获得游标语义，backend 的部分页 fill/trim 调用 SurfaceOps。
其他 tiles3 生产 iterator 保持 §11 已迁移的固定 View/四对 hot pins；writeBytes 保持 §13 原生批量路径。
本轮没有宣称所有 brush/dab 或 legacy writable iterator 已替换成这个新游标。

### 14.3 结构回归与剩余缺口

新增 15 个场景：native/generic × seal/cancel；固定旧 View 跨新提交/default 变化、实际换出后的精确版本恢复；
失败换页不可复用陈旧指针或重放；1/4/16 BPP 的负坐标、双向跨页、padding、重叠复制与正负坐标极限。
区域 native 写逐页只有一次成功 target pin、generation/seal，峰值为 1；同页多行不重复 pin。
同时加强默认 OperationSpans 的旧指针存活和两页同时 pin 断言，不能只验证新短寿命模式。

两个开发期反例保留：测试最初错误要求 poisoned native segment 可继续写，现验证整段失败回滚；
通用写 before-image 尝试 native 导致 lazy binding 多建，现恢复 control 路径，而非放宽按需 binding 断言。
首轮编译记录也保留：lease 禁止移动赋值是能力安全约束，采用 release 后 optional/emplace，不开放覆盖活 lease 的 API。

本轮只验收上述 pin 与重复工作边界，不授予无锁、完整短发布、原位 permit、总预算或性能资格。
旧 View/capture 释放、反复 pin/unpin、冷恢复、generic 长期 write lease 和 copy 临时内存都计入最终 E。
owner-issued in-place permit、brush/dab/重叠读迁移、完整发布准备、长历史/退休队列背压与非 CPU 交接仍未结清；
结构完成后再冻结同义主干 M、驻留 K、事实交接 X 与完整 E 的整体测试。

最终 CPU-only/selection 插件/Vulkan contract 构建通过；14 套完整回归 **456 passed / 0 failed / 0 skipped**，
paint-device 选定槽 **9 passed**（均含 init/cleanup）。既有八组与新增 access-cursor 组各 40 次，共 **360 次**重放；
连同完整及选定套件共 **375 次运行**全部成功，无 SAFE ASSERT。架构门禁与旧 D11/D12 归档校验通过。
`final-*` 绑定本轮版本，不与 §13 的 441 项结果或开发期结果混算。

## 15. 2026-09-21：生产 planar 写与 trim 共用原生段

证据见 [production-mutation 检查点](../../../evidence/br1_production_mutation_20260921/README.md)。本轮迁移真实
`KisTiledDataManager::writePlanarBytes/setExtent → backend::trimToRect`，不是新增一个仅测试调用的 facade。

### 15.1 planar 写：一次业务调用对应一个未发布段

- 原先 planar 只有 root commit 的外层 batch，页写仍在各 tile unlock seal。现在与 packed writeBytes 一样，
  使用 `beginCpuMutationBatch`，各页只归还 guard/pin，操作末统一 seal；不提前 commit 调用方的 memento 事务。
  能力 fallback 在开始时选择，native 失败不改路重放。
- 保留原按页块、逐 channel 的像素循环。缺失 channel 保留源内容，零大小 channel 不进行指针解引用/复制；
  空矩形、全部缺失或没有实际 channel bytes 时，在申请事务/session 前结束，不产生 generation/proof。
  channel 数、大小/总量及坐标/平面偏移的溢出先检查；平面可用内存长度仍由原有无长度指针 API 的调用方保证。
- body 使用可失败的 `tryWriteData`，不在权限获取失败后偏移/写入空指针。失败给 batch 标记不可成功，
  归还全部 guard 后取消本段并刷新兼容索引；不把未发布 backing 留成“已就绪”的 cache。
  平面字节偏移改用 `qsizetype`，末块不再把坐标推进到 qint32 终点之外；负坐标余数运算避免对最小整数取负溢出。
  每行/像素按合法偏移寻址，不在最后一行继续推进带 channel/横向偏移的指针至缓冲区 one-past 之外；
  contiguous 范围端点用宽整数计算。该源码级修正不冒充 sanitizer 已验证。

### 15.2 trim：部分页所有裁剪带只做一次首写

- 先从 canonical allocated pages 区分完全保留、整页删除和部分修改。完全保留不写；整页删除保持原 semantic removal，
  不申请 pixel backing/guard/COW。仅当存在部分页时才为该操作开启 native mutation 段。
- 一个部分页取得一次受能力保护的 `KisTilePageStoreLease`；上/下/左/右裁剪带直接共用它的 writable backing，
  不再分别创建 SurfaceOps session、读取 before-image、COW 和 seal。页处理后归还 pin，段末准备各页 proof。
  这仍是必要的独立 backing，不是原位 permit；全部保留像素和旧 View 必须保持不变。
- 对变化页采用一致的 row/column 顺序，保留 backend/owner 的页预约；未增加全局像素锁或 CAS 状态机。
  `setExtent` 的兼容索引重建仍存在；allocated-page 枚举和变更计划不是 O(K) 发布已完成的证据。

### 15.3 batch 失败与兼容坐标能力不能含混

`markFailed()` 只把本 batch 标为不可成功；仍借出的指针不立即撤销，finish/析构在 guard 归还后取消 native 段，
并在本 batch 拥有匿名事务时 abort。调用方 history 中**此前已 sealed/staged 的修改不自动回滚**。
因此语义删除/alias 等与 writable 页统一到可整体撤销的私有 mutation delta，仍是后续核心工作；
不能把这次生产像素接通称为所有混合语义操作已获得段级失败原子性。

嵌套 native batch/trim 必须在加入匿名事务之前拒绝。开发反例证明：先加入一个新 client 再拒绝并 cancel，
会把仍在运行的外层事务标记失败。现验证拒绝不改变外层 client/claim，外层仍可成功 seal/commit。

借出的 native lease 持有 batch control block 的强引用。public batch 在 guard 存活时析构，由最后强引用的析构
取消未完成段；不让异线程 unlock 读取可竞争的 `abandoned` 标志。沿用既有共享所有权，不增加逐页全局锁/原子状态机。
弱注册表的槽位保留到 transaction client 终结之后，即使弱引用已经失效也拒绝新 batch；不能让下一操作加入尚在取消的
匿名事务。128 轮交错覆盖异线程最后 unlock、batch 析构及原线程立即重入，验证只能全段 seal 或全段 cancel，
无遗留事务/页预约且新 batch 不受旧取消污染。这是所有权推理与压力回归，不是 TSAN 或穷尽调度证明。

边界测试还区分了 canonical logical coordinates 与 tiles3 compatibility index 的能力：当前 concurrent hash 用
打包 key，要求每轴 tile 坐标在 `(-0x7fff, 0x7fff)`。超范围原路径会 SAFE ASSERT 并创建未入索引的 detached tile，
不能因像素读取成功就算产品支持。hash 暴露 `supportsCoordinates`，planar 写在建事务前按所选索引检查并拒绝；
chained hash 的完整坐标比较实现独立声明能力，不能把 packed 限制当作 PageStore、GPU 或硬件存储事实。
底层断言保留并复用同一范围谓词；纯 PageStore §14 的 qint32 边界回归不因兼容层限制而删除。

### 15.4 验收范围与下一核心依赖

新增 58 个 Qt 场景：16 个 planar、32 个 trim、合法边界/越界拒绝与 no-op 输入各 1 个，
另有 nested rejection 1 个、owned/history batch failure 2 个、真实 planar/trim 中途失败 4 个和并发放弃/重入 1 个。
边界槽内部覆盖四个方向，不另把子循环算成 Qt 场景。
生产测试覆盖 1/4/8/16 BPP、负偏移、多页、缺失/零大小通道、已提交/历史事务、旧 View 和 undo/redo；
检查需要像素修改的操作只有一 native 段、每个变化页一 generation/seal、必要 COW 至多一次、目标 pin 峰值 1、零 generic write request。
同页四带的工作量由四次首写降为一次；这些是结构计数，不是吞吐加速或延迟达标证明。
实际入口中途失败通过另一事务占用第二页触发：第一页已经修改，但整段未 seal 时取消，兼容缓存重新读取原版本；
旧的 caller-history 内容与外部 writer 均保留，零新 root commit。只涉及部分页的这组失败证据不能外推到混合 semantic deletion。

最终 CPU-only/selection 插件/Vulkan contract 构建通过；14 套完整回归 **514 passed / 0 failed / 0 skipped**，
paint-device 选定槽 **9 passed**，均含 init/cleanup。此前九组与 production-regions/batch-failure 两组各 40 次，
共 **440 次重放、455 次运行**全部成功，无 SAFE ASSERT；架构门禁与旧 D11/D12 归档校验通过。
证据目录的 `current-*` 测试与 manifest 对应最终源码；`final-*` 的 513 项和 `verified-*` 的 514 项为此前版本，
保留但不混算，也不把其总运行次数相加作为当前资格。最后源码修正消除了 planar 末行多余指针推进，再完整重跑。

下一步继续处理私有语义 delta 与失败恢复、真实画笔/重叠读边界、owner-issued 原位授权、完整短发布和回收总预算。
planar 的页租约/兼容 wrapper、trim 的页面枚举和索引重建仍计入完整 E；不得以 native request 为零删掉这些成本。
整体结构与最终同义 M/K/X/E 资格仍未结清。

### 15.5 下一纵向切片：私有语义 delta 的落实约束

以下是 §15 检查点冻结的实施约束；§16 落实删除/像素组合，§17 继续落实 alias 与完整 fill/PageStore copy，不能沿用本节作为全部未实现的描述。

不能通过“失败后把旧页写回”来补混合操作原子性：中途捕获的 View 已可能观察到变化，回写还会产生额外版本和像素工作。
应在 canonical owner 中准备独立于已 sealed transaction overlay 的 operation delta，沿用现有 claim/发布语义：

1. removal/alias/no-op 与 writable target 在同一操作里按 PageKey 合并；删除仅预约 key 和记录语义，不申请像素 guard，
   纯语义操作也不以 provider 支持 `nativeCpuMutation` 为前提。不能另建由 compatibility hash 决定版本的事务。
2. 暂存删除不立即调用当前 `stagePageRemovalImpl` 撤销 caller-history 的旧 proof/backing；保留进入操作时可见的
   prepared version/default identity 和必要引用。alias 的 exact source 同样必须受保护，不能在 seal 时追 current head。
3. 全部候选完成后先批量复验 operation/page/provider/transaction 事实，再一次安装到 sealed overlay；metadata/proof、
   removal/revival 与引用退休必须具有同一个可见性边界。失败时只丢弃本段候选，不能删除调用方此前的 history delta。
4. 活 guard、并发 capture、其他 writer、整页删除后重写及 alias 后部分写均须使用同一 claim 规则；不靠排序最后执行删除
   来冒充原子性，也不为了减少提交跨越原有业务发布边界。准备、取消和最终退休成本均计入 E。
5. 真实 trim/fill/copy 入口的混合测试必须包含“先成功暂存整页删除，再在后续部分页/alias 准备或 seal 注入失败”，
   覆盖 owned/history、旧 View、操作中途 capture、undo/redo、外部 writer 不受污染，以及零无意义 pixel allocation/COW。
   §15.4 当前只有部分页的故障用例不是这项验收的替代品。

## 16. 2026-09-21：Canonical mutation 私有删除与像素统一安装

证据见 [semantic-mutation 检查点](../../../evidence/br1_semantic_mutation_20260921/README.md)。本轮跨越 §15 的失败边界：
真正改变 owner 私有 delta、metadata 生命周期与生产入口，不以延后 root commit 或失败后回写像素替代原子性。

### 16.1 Provider-independent 操作，CPU 是可选执行能力

`KisPageStore::beginMutation` 返回 `KisPageMutationSession`，保护 transaction/base 并预约实际涉及的 PageKey；
`removePage` 只暂存语义 absence，不调用旧 `stagePageRemovalImpl` 撤销 prior proof，也不申请 generation、CPU backing 或 read lease。
纯语义操作无需 native CPU provider；`enableCpuWrites` 在像素工作前选择同步 resident 执行能力，`beginCpuMutation` 是它的便捷入口。
早先 `KisCpuMutationSession` 仅保留 source alias，实际是同一 control block/claim/可见性权威，不存在两个 mutation owner。
这是分支内 C++ API 的演进，不承诺旧二进制 ABI 无需重编译；全部相关目标需重新构建。

同 key 重复删除合并。同段删除后重写从当前 surface default 开始：已有 pending backing/generation 可重新 pin、初始化并复用；
没有 pending backing 时只准备目标，不从已删除源复制。删除不能撤销仍借出的 guard；最终动作是删除时，seal 取消本段多余
像素目标但不修改此前已 sealed 的 caller-history 内容。通用 `stagePageRemoval` 仍保留其显式、立即 sealed 的旧 API 语义，
不把它静默变成私有暂存，也不允许它绕过新段的 key claim。

### 16.2 所有候选先成功，再一次安装 sealed overlay

- 像素页的 publish/proof 先在 owner 内准备，但尚未进入对外的 `preparedProofs` overlay；任一 proof 失败，只取消本段新版本。
- 对被替换/删除的旧 prepared version 构造 `DetachPreparedVersion` metadata 候选。它仅转为 Historical、清除 preparedBy，
  不撤销 captured View、generic read lease、physical pin 或 last-use。后续历史收集复用既有 reachability/预算/退休流程。
- mutation metadata candidate 是 coordinator 私有、owner-bound、move-only、一次消费能力：复验全部 revision 后才安装任一页。
  它不能作为 epoch publication candidate 使用，反向也不允许；不修改 committed epoch/generation cache tag。
- 安装成功后，在同一 owner 临界区撤销旧 proof、合并新 proof 与 removal/revival，再让 capture 看到完整新 overlay。
  失败不撤销旧 proof，不丢调用方此前修改；旧 View 继续读取旧版本，即使该版本只曾存在于 history overlay、从未进入 root。

该阶段仍在 owner gate 内完成 native proof 与 mutation metadata 准备/安装；新增批量完整性不是短发布、无全局锁或有界耗时资格。
旧 prepared 版本转 Historical 带来的队列/扫描及完整销毁成本必须记入 E，不能当作已消除的成本。

### 16.3 生产入口及边界

`trimToRect` 的整页删除与部分页修改现共用一个私有段；`clearAll/removePages` 使用 provider-independent semantic batch。
整页删除不会新增 writable pin/像素初始化；已知空操作不创建段。backend 使用相同 key 预约与最后强引用终结协议，
拒绝嵌套发生在加入匿名 transaction client 之前；失败不能污染旧 history 或外部 writer。
private batch 拒绝尚不支持的 alias 时必须标记整段失败，不能让 finish/析构继续 seal 先前暂存的删除或像素。
`batch-negative.log` 保留 owned/history × 显式结束/析构的 4 个修复前失败；对应回归保留旧内容与 undo/redo。

新增 44 个 Qt 场景：4 个纯语义能力/读保护，16 个混合 seal/cancel/第一或第二 proof 失败，16 个删除重写复用，
1 个并发 mixed capture，1 个 metadata capability/整批复验，2 个真实 mixed trim 故障和 4 个 clearAll/removePages 故障。
另扩展既有 full-reference 差分槽，覆盖 detach 的 16 种 read lease/pin/last-use/captured-view 组合；子循环不另计 Qt 场景。
包含 provider 实际锁外准备中的 capture、128 轮交替删除/写入的跨线程 capture，以及旧 View、history undo/redo 与外部 writer。

在 §16 冻结时，**alias 与完整 fill/copy 的原子私有 delta 尚未迁移**，旧 whole-page adoption 仍是独立 sealed 路径；
不能把该次删除/像素组合的通过外推为所有语义操作完成。后续 exact alias source 保活与混合替换的实际进展以 §17 为准。

### 16.4 计数与性能口径

`mutationStatistics` 是规范入口，旧 `cpuMutationStatistics` 保留 source compatibility：`operationSessionsCreated` 计 canonical 段，
`sessionsCreated` 仍只计启用 CPU 写的段；`removalsSealed/Cancelled` 计合并后的语义 key，不代表 payload 页数或 root commit。
`activeMutationPages` 是全部 key claim；旧 `activeCpuWritePages` 明确为此计数的兼容别名，不得解释为物理 writer/pin 数。
`pendingDefaultResetBytes` 单列“删除后复用 pending backing”的软件默认初始化，不与 provider 首次初始化混为同一事件，不计硬件 X。
metadata 的 `prepared/installedMutationPages` 与 root 的 `prepared/installedPublicationPages` 分开；新段 seal 不是 root publication。
这些结构计数及正确性回归不授予 CPU 主干不劣性、GPU/UMA、TSAN 或最终 M/K/X/E 资格。

### 16.5 回收与历史恢复的控制边界

`verified-iterator-lifetime-24.log` 捕获一次实际 HLine/history 撤销后仍读到新像素的失败；该轮不是通过资格，
不能以其 14 套完整回归已绿或再运行变绿掩盖。随后 provider 延迟 retirement acknowledgement 的确定性测试证明：
旧 `restoreRetainedEpochImpl` 将 ledger 的全部 operation 都当作恢复阻塞项，无关、已 detached 的退休操作也会使恢复失败。
正常同步 retirement 同样有 bind → terminal verification → release 的短暂 ledger 窗口；后台执行使此前隐藏的错误边界可见。

owner ledger 现在显式区分普通 provider operation 与 detached retirement；分类由 owner 选择，不接受 provider 自报安全性。
`publicationBlockingOperationCount()` 在同一 ledger 锁下 O(1) 取值，不用两个先后采样计数相减。历史恢复只排除前者，
保留 source retention、transaction/head 冲突检查、metadata revision 复验与旧 View 保护；不等待无关队列，也不跳过物理 last-use。
`providerOperations` 仍统计全部未释放 ledger 项，不能解释为可见数据的在途操作数或硬件 X。

同一问题还会使异步 close 永久无法重试：退休已完成，但入口总 operation 检查阻止它轮询保存的 operation。
close 冻结/等待 worker 后，仅从“进入 drain 前的活能力检查”排除 detached retirement；这些记录必须进入原有 drain，
未终态/失败仍返回失败并保存债务，下次查询同一 operation，不能重发 retire 或提前宣告关闭完成。
公开 stats 与 `hasOutstandingCapabilities()` 仍包含这些债务；不是删掉计数换取成功。

新增 7 个 Qt 场景：整份/稀疏 memento 恢复 × default/resident 4 个、后台/关闭首次退休后的 close 重试 2 个、
ledger 混合分类/重复 bind/非终态/一次释放 1 个。`rollback-negative.log` 保留修复前四个稳定失败，
`close-negative.log` 保留两个关闭重试失败。连同 §16.3 及 unsupported-alias failure，本轮共新增 55 个 Qt 场景。
`repaired-*` 的回归 fixture 曾假定显式 drain 独占两个记录，忽略历史 worker 已能轮询同一退休队列；
现先等待 worker idle 再确认 ticket，仍严格断言退休 2 项和不重发调用，不以放宽计数掩盖竞态。负样本与正式重放见证据目录。
这是正确性与进度边界修复，不是短发布性能、无锁或 GPU/UMA 执行资格。

### 16.6 本轮验收边界

最终 `checkpoint-*`：14 套完整回归 **569 passed**，paint-device 选定槽 **9 passed**，14 组各 40 次、
共 **560 次重放**（合计 575 个测试进程）全部通过；无 FAIL/SAFE ASSERT/QFATAL。Qt totals 含 init/cleanup。
CPU/Vulkan 两套相关目标与 selection-tools 插件均重新构建后才执行，loader 检查使用当前 build 的 image/shape/color 插件。
架构检查与 diff whitespace 检查通过；D12/D11 封存证据只做 archive-only 核验，未重跑或改写旧性能样本。
`verify-checkpoint.mjs` 核验测试 inventory、负样本、源码/二进制/插件/文档 hashes 和本地链接；未来编辑会使 live checkpoint
失效，不能覆盖旧 manifest 维持假通过。§16.2–16.4 列出的结构与 M/K/X/E 缺项仍开放，不授予核心重构整体完成资格。

## 17. 2026-09-21：私有 alias source 与生产 fill/copy 贯通

本节更新 §16 的 alias/fill/copy 缺口，不覆盖此前封存的结果。当前代码将完整 `clear/fillRect` 和
PageStore → PageStore 的 `bitBlt/bitBltOldData/bitBltRough/bitBltRoughOldData` 接入同一 canonical mutation 段，
包含部分页像素、整页别名和稀疏删除；不是仅延后 root commit。仍不授予核心重构整体完成资格。
证据与重放入口见 [本轮目录](../../../evidence/br1_alias_mutation_20260921/README.md)。

### 17.1 输入能力与段内生命周期

- `KisPageReplicaSource` 是 provider 签发、保持确切 immutable backing 的输入能力，不是目标 generation、authority 或 root。
  provider 在实际准备时验证私有 mint identity；仅复制 provider ID/epoch 不构成能力。tiles3 的 source 持有 COW-user 引用，
  使 legacy 新写不能修改已捕获输入，但不持有 RAM pin。capture/alias seal 不因验证地址而强制 swap-in。
- `captureCpuReadSource` 接受 owner 保护的 exact read guard；`captureCompletedTileSource` 只适配已完成且由调用方保护的
  immutable/locked legacy 输入。后者不是把任意可写指针冻结的 API，不能用于仍可能被 producer 修改的字节。
- `aliasPage` 私有暂存 source，重复 alias 合并，不创建 target generation、像素 allocation 或 proof；输入直到首写/seal
  才消费。首个部分修改采用独立 backing 并初始化；已有 pending 页上的 alias → write 只重新初始化该 pending backing，
  不重复 reservation/generation。显式 `DiscardContents` 不复制被覆盖的 alias 输入。
- 最终动作是 alias 时，seal 才请求 immutable adoption；同段已完成真实修改的目标通过 owner-only
  `ReplacePrivatePreparedBacking` 换 backing、保留 generation。这不是原位覆盖历史 backing 的 permit。
  状态机要求私有 Prepared、正确 transaction/source/version、无 writer/view/read lease/pin/last-use、唯一有效 replica，
  新 allocation token 不得占用已有 slot。已对外 sealed 的旧历史走原有 detach，不使用此替换捷径。
- 所有新 native/alias proofs 成功后，才一次安装完整 overlay；provider/proof 失败仅取消本段，旧 history、旧 View 和
  外部 writer 保留。非法 alias 输入必须 poison compatibility batch，不能由析构悄悄提交前面的删除。

### 17.2 生产操作及索引

`fillRect` 使用一次固定 before View：整页默认值变为删除，整页 uniform 使用缓存的 immutable source，部分页走 native guard。
重复已知 uniform backing 是 no-op；不能在未知裸 pointer 写后推断没有变化。
`copyFrom` 一次捕获 source current/before 与 target View；即使复制中途 source 发布新内容或更换 default，后续页仍来自原 View。
整页替换不读取、物化或逐字节比较旧目标来证明 no-op，只使用 exact version、共享 backing 或已知 uniform 身份。
相同默认值的整页 sparse copy 直接删除；部分页保留未改区域。source 的初次获取目前仍会按 ReadPage 路由取得 pin，
真实冷源可进入 generic/synchronous swap 控制路径；不能把底层 source capability 可非驻留外推为所有产品复制均免 source fault-in。

操作成功才返回实际 changed keys，失败返回空列表；DataManager 用一次 post-publication View 和原生读 guard
刷新这些 compatibility hash/extent 项，不遍历整图，也不为暖驻留索引刷新创建 generic read request。
已借出的 legacy pointer 不被缓存刷新撤销；其 tile cache 标记失效，后续访问重新绑定。
发布后的索引 View 是缓存同步，不属于复制源的业务可见性 View，测试和计数必须分开。
混合 legacy-source fallback、其他仍用 rectangle/full index rebuild 的入口、全部 brush/dab 边界并未因此完成迁移。
完整回归发现源 raw tile 尚有 write intent（即使未升级 mutable pointer）时，旧 bitBlt 要求 live backing 观察/共享；
不能静默改读 sealed before-image。DataManager 现在只探测本次源坐标范围的已有 wrapper 和局部 intent 状态，
这类调用保留明确 legacy 分流；history 的 old-source 仍读保护过的 base View。探测不创建 wrapper、不升级 intent，
不在每次 tile lock/unlock 新增全局计数或全局锁，但这次额外 O(访问页数) 分类成本仍需计入 M/E。
live producer 分流不是 immutable source 能力，也不授予其跨操作 alias 不变性；未迁移边界必须保留，不能据正常复制通过覆盖它。

### 17.3 归因口径与尚未授予的资格

`aliasGenerationsReserved` 只计纯 alias 首次 target generation，native `generationsReserved` 不改口径；
`aliasPagesSealed` 计最终 alias keys，`pagesSealed/Cancelled` 仍计做过 native preparation 的页。
write → alias 同页可同时进入 native-preparation 与 final-alias 类别，二者不是互斥分区，禁止相加当 unique dirty 页数。
`synchronousHostWrites` 兼容计数包含成功 alias seal；adoptedBytes 是逻辑引用字节，绝非搬运流量。
uniform source 的新建及保留内存位于 TileDataStore/cache，不能因不计 provider allocation 就写成零 payload/零内存成本。
pending-source 重初始化的 `explicitCopyBytes` 是软件复制，依旧属于 K/E，不是硬件跨域 X。

新增 opt-in 相位：`copy_prepare`、逐页 `copy_source_page`、`copy_finish`；后者包含 View 释放、seal 和必要 root finish，
其内部 alias/proof/commit timer 属嵌套 inclusive 区间，不得重复求和。`fill_page`、`mutation_alias_prepare`、
`mutation_source_initialize`、`mutation_index_refresh` 分别记录页处理、alias provider 准备、pending 源初始化与变化页缓存更新。
`write_publish_host` 的 native 分支现在以 distinct claimed semantic/pixel keys 计 workItems，而非仅 native payload 页；
这不是新 root commit 计数。observer 只在显式 `timer.next()` 边界触发；构造 timer 只计时，不是并发注入点。
关闭态/开启态扰动和完整归因尚未重新采样，不从正确性日志推导阶段占比或提速。

仍开放：owner-issued in-place permit；全部 brush/legacy-source 生产边界；owner 内 proof/metadata/input 准备的剩余拆分；
同步 overlay claim/release、单页长历史与队列总预算/背压。read/source COW reference、RAM pin、logical retention、异步 last-use
继续分别判定，不能用任一种替代其他。当前 GPU/UMA 未实测，不能声称零软件开销或不劣 CPU；最终 M/K/X/E 仍待结构收口后执行。
tiles3 source 初始化仍可能在 provider mutex 内进行同步换入/复制；source mint、逐页 adoption/completion/proof 和索引 binding
适配也不是零开销。下一阶段须把这些真实步骤连同兼容分类计入准备/协调成本，再以合法 pin/claim 拆分；
不能把新 semantic API 的零像素复制等价成零管理时间，或以安全 COW 子路径通过宣布 permit、短发布及主干等价已经完成。

### 17.4 本轮验收

最终 `verified-*`：CPU/Vulkan 相关目标及 selection-tools 插件重建后，14 套完整回归 **758 passed**，
paint-device 选定槽 **9 passed**，17 组各 40 次、共 **680 次重放**全部通过（695 个测试进程，Qt totals 含 init/cleanup）。
包含原 low-memory hangingTilesTest 的 40 次原断言重放；所有最终日志均无 FAIL/SAFE ASSERT/QFATAL。
首轮 `checkpoint-*` 的 live-source 失败、开发中的 fixture 错误及修复前日志全部保留，不以再次变绿替代归因。
架构、diff whitespace、当前运行库/插件及文档本地链接校验通过；D11/D12 封存性能原件只作 archive-only 验证。
新 live manifest 绑定本轮源码、测试二进制、插件、日志和文档，后续修改会使之失效，不覆盖旧检查点。
本轮只结清 §17 所述私有 alias/正常 fill-copy 切片与明确的兼容分流；§17.3 的结构缺口及最终 M/K/X/E 仍开放。

## 18. 2026-09-21：mutation seal 的锁外准备与紧凑语义安装

本节推进 §17.3 的 owner 内准备缺口，**不把 overlay seal 当作 root commit，也不授予整体短发布资格**。
实现/回归证据见 [本轮记录](../../../evidence/br1_mutation_seal_20260921/README.md)。旧 §17 live manifest 已因后续源码修改失效，
历史日志不覆盖；最终性能测试仍等待结构收口。

### 18.1 保护依据与执行阶段

`KisPageMutationSession` 从开始至收尾连续持有 owner lifetime、事务 claim 及本段 PageKey claims，session mutex
保护私有 delta。事务 claim 排除同事务 commit/abort/surface metadata 改动与关闭；PageKey claim 排除同页的新写、删除、
adoption，不排除旧 sealed 版本的读者。provider registry 在 operational 期间不变，Prepared 目标不作为 Historical 回收。
这些保护使私有 `BeginPublish/PublishWrite`、completion、provider proof 验证可以不持有全局 owner gate；它们不是像素 pin，
也不是原位写 permit。未进入 `preparedProofs` 的新 Prepared 目标对捕获者不可见，准备期间仍读完整旧 overlay。

alias 仍先按既有两阶段协议取得目标，所有新 proof 均成功后才准备旧 proof 的 detach。输入只复制本段变化 key 对应的旧 proof
与 transition，**不跨 unlock 保存整个 overlay 的可写引用/迭代器，不用旧 map 覆盖最新 map**。同事务不同页的兄弟段允许并行 seal；
最终只合并本段键。所有 guard 已归还时，在目标仍私有的阶段于 owner 外释放 writable reservation，安装后新读者即可取得合法 binding。

`prepareMutation` 在 owner 外构造绑定 coordinator/transaction 的 move-only **紧凑 detach delta**，每页只保留 exact version，
不复制整页 version/reader/replica snapshot。返回 owner 后复验本段 claims；coordinator 对所有页面先检查 exact Prepared 身份、
preparedBy 和无 writer，并全部取得短 publication claim，再安装。第二页真实语义冲突时第一页也不能改变。
安装仅在**当前** metadata 中把 publication 改为 Historical、清除 preparedBy 并推进 revision；当前 captured View、read lease、
pin、last-use、authority handoff、replica 和 committed epoch 完整保留。晚到读者不导致丢保护，也不再使 detach 候选反复失效。
这更新 §16 的全 snapshot/revision mutation 协议；**root publication/restore 仍严格检查 snapshot revision，不允许通用陈旧快照合并**。
不重发 alias adoption、payload 初始化/COW、generation 或 proof 验证，也没有读者 churn 的 retry loop。
准备/安装的真实语义拒绝仍取消本段，保留此前 sealed history 和并行兄弟段；这不是 wait-free 或硬时间上界。

完整 overlay 安装后，private page/source 容器销毁及 physical retirement 工作移到 owner 外，claims 保留到收尾。
收尾期间新捕获者可以读完整新 overlay，旧 View 仍读旧版本。失败继续按 canonical cancel 撤销本段新版本/新 proof，不能回滚旧 history。
现有 alias 输入组装/metadata adoption、旧 proof 收集、全批 metadata 安装、proof map 合并、历史分类和部分取消仍有 owner 成本；
exact version 查找仍随单页历史量增长；有外部 snapshot 时对当前 versions 的写入仍可能触发 QVector COW，未获得硬预算。
不能把移出几个阶段等价为全提交无全局锁。

### 18.2 相位和工作量

新增 append-only 相位：`mutation_seal_owner_wait`、`mutation_seal_inputs`、`mutation_seal_private_publish`、
`mutation_seal_proof_prepare`、`mutation_seal_metadata_prepare`、`mutation_seal_publish_owner_wait`、
`mutation_seal_install`、`mutation_seal_cleanup`。前述 private/proof/metadata prepare、publish-owner wait 与 cleanup
进入时不持 owner，session mutex 仍持有，observer 不可重入同一 session。
这些是 seal 内的顺序业务相位，不是每段都等价于纯锁持有时间；inputs 包含嵌套的 alias provider 解锁阶段，
install 在失败路径还含取消/退休，末尾 owner-wait 包含重新入锁后的少量 claim/stat 收尾。精确 owner hold 仍需另采锁区间。
`write_publish_host` 是 inclusive 父区间，alias provider 与这些相位不可重复求和。失败、全部重做、收尾和后台 drain 都纳入 E。

`sealMetadataPreparations` 计实际候选构造尝试（首次 seal 无旧 proof 可为 0）；`sealMetadataRejections` 计这类候选的准备/安装拒绝。
它们不计 root publication，也不代表真实像素 work。被淘汰的 retry 实验计数不作为当前 API 保留。
本轮只验证结构和正确性；不从 QtTest/observer 日志推出阶段占比、吞吐提速、主干等价或 GPU/UMA 不劣性。

### 18.3 验收矩阵与剩余方向

新增 57 个场景：1/4/8/16 BPP 的混合 removal/native/alias proof 成功或失败（8）；native 与混合删除的
迟到 captured View、generic read lease、新 release 和持续 churn（32）；阻塞 provider 验证期间独立事务完成提交（1）。
以及 compact delta 在候选准备后新增 capture/lease/last-use/handoff pin 的 16 种组合，与完整状态机结果逐字段对照（16）。
验证旧/新 overlay 完整性、claim 阻止危险操作但不阻止无关页、兄弟段不丢失、失败保留 caller history、读者变化不重复准备，
以及旧 View/lease 可读、最终 close 债务和 provider 内存归零。原 capability/错误类型/事务绑定/整批拒绝测试继续保留，
整批拒绝由第二页真实 writer 冲突触发，不能继续把合法读者到来当错误。

首轮全 snapshot 锁外候选采用最多 8 次重试：单次 14 套完整回归虽通过，但 200 次重复回归中出现 4 次正常并发写失败
（3 次 capturedOverlayConcurrentSegments、1 次 concurrentMixedSemanticCapture）。这不是 flaky 豁免：读者进出使候选持续陈旧，
因此淘汰该方案，改用上述语义 delta；修复前 `full-*` 报告和日志保留。最终构建/重复验收以本轮记录为准。

最终 `final-*`：CPU/Vulkan 相关目标与 selection-tools 插件重建后，14 套完整测试 **815 passed**、paint-device
选定测试 **9 passed**；10 组各 20 次、**200 次重复**全部通过（215 个测试进程，Qt totals 含 init/cleanup）。
中间 oracle 清理误用裸 last-use acknowledge 的 fixture 失败也保留，改用 registry-issued terminal proof 后通过，未放宽生产能力门。
运行库/插件、架构、diff whitespace、文档链接与 live hashes 另行核验；不将正确性耗时当性能样本，旧 D11/D12 只做 archive-only 验证。

后续仍优先完成 owner-issued 原位 permit 的历史/捕获/abort 证明、全部 brush 与 live legacy-source 边界、
输入/安装/单页历史布局及回收队列预算；本节降低准备对 owner 的占用，但没有减少所有 per-page proof/metadata 工作量。
必须保留 P1–P6 的未结清项，结构完成后再做完整固定工作量的 M/K/X/E 及显存/RAM 分离测试。

## 19. 2026-09-21：真实 painter source/mask 消费者的 const 契约贯通

本节继续核验生产调用链，关闭一个由只读 accessor 原生化暴露的实际崩溃，不将其记为完整画笔写迁移。
证据见 [本轮记录](../../../evidence/br1_painter_mutation_20260921/README.md)。§18 的 live manifest 因本轮源码修改失效，
历史记录不覆盖；整体重构及最终 M/K/X/E 仍未完成。

### 19.1 生产缺陷、修复及可见性

`KisRandomAccessor2::rawData()` 只对 writable accessor 返回指针；只读访问必须使用 `rawDataConst()`。
`KisPainter::bitBltImpl` 却将 source/mask 的 const 接口强制转换为具体 mutable accessor，再调用 `rawData()`。
修复前原有 `testSimpleBlt` 实际触发 SIGSEGV，记录在 `baseline-painter.log`；不是只有新测试或新 facade 出错。
生产代码现直接使用公开 const 契约：current source 为 `rawDataConst()`，明确 old-source 才用 `oldRawData()`，
selection mask 始终读其 captured current，不因源图像选择 old-data 而读 mask history。删除对具体 tiles3 accessor 的依赖，
并在合成前检查输入/目标指针；不恢复只读 accessor 的可写指针、不新增绕过 pin/View 的入口。

正常 source 与 mask 分别保持各自一次捕获的 current/before View；后续块不追逐新 head。它们可能属于不同 PageStore，
这是每个输入自己的固定 View，**不是多个 owner 的原子联合快照**。wrap/offset 继续由公开 accessor 实现。
已有 live legacy writer 的 source 仍按既有兼容分流观察；history old-source 保持 before 语义，不把可变 producer 计作 immutable View。
源等于目标的重叠复制使用先捕获的 source，不能因为写目标前进而读取本次刚写出的像素。

### 19.2 可验证的产品边界与归因限制

新增 72 个实际 painter 场景：1/4/8/16 BPP × 无 history/驻留 history/语义 default history/wrapped history ×
current/old-source × 有/无 mask，共 64 个；另有 history/current-old 组合的 live writer 4 个和重叠 self-copy 4 个。
在第二个真实 source-resolve 块前确定性更新 source/default 与 mask，并断言注入确已执行；结果须仍来自原捕获输入，
新建 accessor 则读取更新后的值。这是可重放的交错测试，不冒充多线程、TSAN 或异步 GPU 覆盖。
oracle 直接用同一色彩合成操作处理连续输入，整数格式逐字节比较；F32 必须有限，逐分量误差不超过
`float epsilon × max(1, abs(expected))`。保留 exact-byte 失败及量化日志：8 个带 mask 的 F32 组合最大差为
`2.98023e-08` 或 `5.96046e-08`。这是分块/整缓冲浮点结果的严格容差，不修改生产合成，也不放宽整数或 View 语义断言。

新增 opt-in `painter_bitblt_prepare`、`painter_source_resolve`、`painter_composite`、`painter_bitblt_finish` 使用 unfiltered product recorder，
因为 source、destination、mask 可属于不同 owner；单 owner recorder 仍只记录其嵌套 PageStore 工作。
source-resolve 在 accessor 移动前进入，不持 PageStore owner gate，workItems 为实际块数；composite 为块像素数。
这些相位是顺序业务区间：source-resolve 包含目标和 mask 的移动/参数准备；composite 包含合成及后续循环边界计算，
mask accessor 的作用域析构也可能计入其末段；finish 包含 dirty rect 和剩余 accessor 释放。
fast-copy 分支在 prepare 内返回。**composite 不能直接作为纯内核 K；finish 不是完整发布或回收端点。**
嵌套 mutation/commit/provider 时间不与父区间相加；observer 注入自身的写工作也在 instrumented 区间内。
精确 kernel/协调 self、关闭/开启扰动、后台 drain 与跨域事实仍须在最终采样中单独测量。

### 19.3 下一写侧结构边界

目标端仍使用 legacy writable random accessor：其缓存淘汰/最终 unlock 可以 seal 各自 tile 段。
本节不授予同一 painter 操作同页仅一次首写、全操作失败回滚、操作级原子发布或原位 permit 资格。
非空指针检查只是阻止无效输入继续进入 kernel，不回滚此前已完成的块，也不补齐 legacy accessor 的全部失败协议。

下一迁移必须显式解决操作私有 writer 与已借出 legacy tile/writer 的归属：不能只在外层创建 batch，
因为现存 wrapper 可复用一个在 batch 之前创建的 write lease，既不加入新段，也不能被新段擅自撤销。
需要在首次目标修改前选择受保护的 native 段或明确兼容边界，保留 source/mask View 与 wrap/offset 契约，
并验证同页重访、外部借用、history、后页失败及 changed-key 索引刷新；不得失败后回放已写过的半次操作。
multi-dab/fill/line 等其余真实 producer 逐项迁移，不把此次 bitBlt 读消费者通过外推到它们。
owner-issued permit、owner 安装/输入与单页历史布局、回收总预算仍按 §18.3 开放。

### 19.4 本轮正确性检查点

最终 `final-*`：CPU/Vulkan 相关目标与 selection-tools 插件重建结束后，15 套完整回归 **905 passed**，
paint-device 选定槽 **9 passed**；11 组各 20 次、共 **220 次重复**全部通过，合计 **236 个测试进程**。
其中完整 painter 套件 90 项包含新增 72 场景；Qt totals 含 init/cleanup，重复进程不混算进完整套件 totals。
所有最终日志均无 FAIL/SAFE ASSERT/QFATAL；修复前 SIGSEGV 及 F32 量化失败保留。
架构、whitespace、实际加载库/插件、文档链接及一次性 live source/binary/doc hashes 纳入独立核验。
旧 D11/D12 仅作 archive-only 检查，不改写原性能样本。正确性通过不授予 P6 结清或整体结构/性能资格。

## 20. 2026-09-21：painter 目标写的显式操作段

本节接续 §19 的目标写缺口，代码及回归记录见 [本轮目录](../../../evidence/br1_painter_write_scope_20260921/README.md)。
当前接入的是实际 `KisPainter::bitBltImpl`，不是仅供测试构造的新 facade；最终验收以本节后续记录为准。
不把此入口迁移外推全部 brush/dab，也不授予原位 permit、完整短发布或回收预算资格。

### 20.1 目标专用接口与一次操作

`KisPaintDevice::applyPixelOperation` 接受声明的目标矩形和同步 callback。`KisPixelWriteCursor` 只提供目标指针及移动/布局，
不提供 `oldRawData`：source、mask、current/before 的输入 View 由调用者另外捕获，避免历史含义随目标写路由变化。
最初的通用 random-accessor 接线在复核后替换为直接 `KisCpuMutationSession/KisCpuWriteGuard`，
因此不为 painter 不消费的目标 before-image 再捕获读 View 或逐页 pin。base 的逻辑保护仍由 canonical mutation 持有，不能省略。

正常 bitBlt 的色彩 kernel 和 source/mask 分块规则保留；目标在同一私有段中首次准备、重访复用。
cursor 同页移动复用当前 guard，换页先归还 pin，pending backing/版本继续由段预约保护；callback 不得保留游标或跨换页借用指针。
全部目标像素完成后才 seal；中途捕获者继续读此前完整 overlay，成功后才刷新实际 touched keys 的 compatibility cache/extent。
快速整页 copy 仍沿 §17 的 alias/removal 路径，不退回像素循环。touched 是获得 writable guard 的页，不是逐字节比较后的净 dirty 集。

offset/wrap 只做坐标适配，不创建目标 tiles3 wrapper，也不改变 generation/authority。
offset 和边界计算先在 64 位中检查，合法极值偏移可以映射到可支持的局部页；不可表示的范围在 callback 前拒绝。
非法移动或后页获取失败使整段失败，后续有效 move 不能掩盖它；失败后的 native callback 不通过 legacy 重放。

### 20.2 范围准入、争用与旧借用

DataManager 只检查本次目标范围内已有 wrapper 的 write intent，不全图扫描、不为检查创建 wrapper。
backend 在实际执行前检查当前线程 batch 和完整目标集：已存在的 mutation batch 内不建立新操作；
同线程重入自己的目标预约直接失败，不能被范围中其他 legacy 借用掩盖，也不先加入/污染外层匿名事务。
真实 legacy intent/lease 导致 callback 前的明确兼容分流，不撤销已借出的 pointer，不把外部 write lease 偷渡到新段。
仅因其他 native 操作占用目标而争用时，等待整组范围可用，不持部分目标、不退化为逐 tile 发布的兼容路线。
范围检查和预约是 backend 的准入协调，不是 PageStore 写授权；其他 canonical writer 的后页冲突仍由 owner 拒绝并取消本段。

native 执行直接请求指定 provider 的 mutation，无法取得它即失败，不因 begin 失败偷偷切到 generic writer。
CPU 暖驻留目标不经过 legacy tile lease 或通用 request map。回调及像素遍历不持有 backend registry mutex 或 DataManager `m_lock`；
native claim、局部 pin 和 swap barrier 仍必需，不是整条路径无锁。只有成功后才按 changed keys 更新兼容索引。
范围预约持续到本 client 的终结，释放后唤醒等待者；进入 canonical 的 transaction/PageKey claims 仍按原协议保护准备及发布。

已有借用的兼容分支保留原 tile unlock/可变观察边界，不授予原子取消或原生首写复用资格。
owned operation 的 root finish 与 caller history 的 overlay seal 仍按不同边界报告，不能把一个 seal 当作一次 root commit。

本轮复核发现并修复了共享匿名事务的失败传播缺陷：当另一 legacy writer 保持 client 时，先成功 seal 的页与随后失败的
私有段会属于同一匿名事务。此前取消私有段后仍调用事务级 abort，最终使先前成功修改丢失、外部 writer unlock 触发断言。
新操作和既有 CPU mutation batch 均已修正：**只有 canonical cancel 确认整个私有段已取消，才正常归还本 client**，
保留其他已 sealed delta 和外部 writer；本操作仍返回失败，不将取消伪装成成功。无法证明私有取消、generic 或可能已发布的
失败仍保留事务级 abort，不能一律吞掉失败。没有其他修改的空匿名事务按原 empty finish 终结，不产生虚假 root commit。
`client-negative-*` 保留两条路径修复前的真实丢数据与 SAFE ASSERT 记录，不作为可接受 flaky。

### 20.3 计量边界与剩余结构

新增 `pixel_operation_range_prepare`、`pixel_operation_range_wait`、`pixel_operation_body`、`pixel_operation_finish`。
prepare 从 backend 入口开始，包含其目标集合构造、完整范围检查/预约与事务/mutation/布局准备；重复等待后的 prepare
计实际重新检查的范围，不能当作新增 unique pages。**此前 DataManager 的矩形扫描、wrapper 探测、第一份去重集合及其 m_lock
等待不在此相位内**，仍计入 painter prepare/E，尚未单独隔离；不能把 backend prepare 当成全部范围准入成本。
wait 入口持 backend registry mutex，observer 仅可发测试信号，不得重入 owner/backend；实际等待释放该 mutex，包含唤醒后的重新取得。
body 包含整个 callback，workItems 为操作数；finish 的 workItems 是 touched 页，包含进入 callback 后的成功/失败终结、
范围归还与私有对象销毁。callback 前的准入/准备失败收尾仍在 prepare。finish 不包含外层索引更新前的 m_lock 等待或
`mutation_index_refresh`；painter 的 `bitblt_finish` 现在覆盖 callback 返回后的终结和索引刷新，不是最终后台 drain。
嵌套 color/source/mutation/commit 区间均为 inclusive；`painter_composite` 仍非纯 K，不能通过相加重建 E 或用正确性日志宣告提速。

范围集合、兼容分类、backend registry 协调、逐页 proof/metadata、owner 输入/安装及退休仍有真实成本；
CPU target pin 收口不等于总 dirty backing、源 pin 或历史内存 O(1)。当前目标写保持安全 COW，不是每段必须复制整页的最终性能设计。
已确认完整覆盖的进一步 DiscardContents 消费、全部 multi-dab/fill/line producer、legacy 借用的最终迁移、
owner-issued 原位 permit、单页长历史布局与回收总预算均未结清。最终 M/K/X/E 和 RAM/显存/UMA 配对仍在整体结构完成后执行。

### 20.4 正确性验收与版本边界

新增 46 个场景：1/4/8/16 BPP × history × 成功/主动取消/非法目标后重试/后页 canonical writer 冲突（32）；
嵌套 batch 与 live borrower 分流（1）；反序目标范围的真实 native 争用，分别首操作成功/取消（2）；
共享匿名事务下新操作/既有 CPU batch 私有取消保留此前 sealed 页与外部指针（2）；
真实 painter 的 history × wrap/offset × 外部目标 borrower（8）；极值坐标与非法移动毒化（1）。
断言段内 generation/首写次数、pin、无 generic request、中途 View、失败无泄漏、undo/redo 和后续操作仍能成功。
争用测试等待实际 `range_wait` 信号后才释放首操作，不用一次 sleep 假定已经等待；不是 TSAN 或硬延迟证明。

最终 `closure-*` 在 `closure-build` 的 CPU/Vulkan 构建全部结束后运行：15 套完整测试 **951 passed**，
paint-device 选定槽 **9 passed**，12 组各 20 次、**240 次重复**全部通过，合计 **256 个测试进程**。
其中 painter 为 99、tiled manager 为 291；Qt totals 含 init/cleanup，不把重复进程混入完整套件总数。
最终日志无 FAIL/SAFE ASSERT/QFATAL；负向记录、初次 fixture 编译失败与中间原型证据保留。
独立 verifier 检查构建/测试顺序、实际 CPU 库/插件、架构、whitespace、链接与一次性源码/二进制/文档 hashes；
§19 live manifest 已因本轮源码变化失效，旧记录不改写，D11/D12 仅 archive-only。整体结构、P3/P6 和性能资格仍未完成。

## 21. 2026-09-21：生产 metadata 的精确版本记录与局部更新

本轮继续写侧核心布局，证据见 [本轮目录](../../../evidence/br1_metadata_records_20260921/README.md)。
普通 mutation 仍允许后页失败/取消，root 候选也仍可能复验失败；当前不能直接把 D12 physical claim 当作原位写许可。
本节先移除首写/私有 seal 对整页历史容器的依赖，**不是原位 permit 已完成，也不把目标改成永久每段 COW**。

### 21.1 生产记录与安全边界

`MetadataPage` 不再继承、持有完整 reference snapshot 作为可写版本容器。page header 与逐版本稳定记录分离，
有序节点保留 diagnostic/oracle 的版本顺序，exact-version 索引用于查找，独立 physical-slot 索引用于冲突见证。
节点与索引只在所属 shard mutex 下访问；已有 snapshot 不共享其 owning version 容器，修改一个版本不触发整页历史 QVector COW。
单版本的 replica/lease/captured-view 列表仍有实际复制与访问成本，不称整个 metadata 已无分配或严格 lock-free。

owner 的首写从受保护 base 和**本事务 sealed proof**取输入，不通过扫描全历史寻找“最新版本”；已有 pending 的 alias 重写
保留其准确 before-version。provider 准备后的 default 复验与 proof seal/validate 也只读取指定版本。
暖读的冷 binding discovery、mutation detach 的准备与安装使用 exact 索引；epoch head/事务/proof 仍由原 canonical owner 决定，
这些索引不增加第二个可见性权威。

`applyOwner/Sequence` 仅对明确白名单的 native writer、adoption、私有取消、capture token 和 detach 转换建立局部投影，
使用**同一个** `KisPageStateMachine::applyKnownValid` 的转换保护。输入包括现有 writer 的 base/target、本次声明的版本，
以及全页 physical-slot 索引找到的冲突记录；slot 身份按 provider/epoch/slot 判断，不能因 allocation generation/domain 不同放过旧历史冲突。
整序列成功前不改权威记录，失败不安装前缀；成功只合并投影中的版本、更新相应索引与 revision，未涉及历史及其保护保持原样。
owner 返回结果不携带伪装成完整 page 的局部 snapshot。未知/控制转换保留完整路径，不以不完整输入运行需要全历史的转换。

局部投影省略的历史**不等于没有 reader/alias/retention**，不能用于证明原位 permit 或 root 可达性。
§21 时 root commit/restore 仍使用完整候选；§22 改成 indexed 候选但保留严格 revision/retention/目录复验及 metadata-before-root 安装，不能外推为陈旧 root 合并。

### 21.2 reference 与生产的 Prepared 归属一致性

新 oracle 用例发现已有规则矛盾：生产 `commitRejectsConflictingPublicationAtomically` 已允许两个事务分别 seal 同页的独立版本，
但完整 `validateInvariants` 仍禁止同页存在不同 preparedBy。修复前 `invariant-negative-*` 记录 **152 passed / 1 failed**，
具体失败为第二个独立版本 PublishWrite 的“prepared generations from competing transactions”；同期 CpuMutation **326 passed**。
原生产 known-valid 路径不会执行该全边界扫描，因此既有产品测试通过不代表 reference 口径一致。

现校准为：**每页一个活动 writer、每个 Prepared 版本一个所属事务**。不同事务的独立 sealed 版本可以共存，
foreign transaction 仍不能读取其 Prepared 内容；root owner 仍负责 base/head 冲突及整批提交拒绝。
这是将 oracle 与既有 optimistic publication 契约对齐，不是允许并发覆写同一 backing，也不取消 root 冲突、slot 唯一性或最后释放检查。
新用例逐转换对照完整 oracle，验证 foreign read 拒绝、较新版本提交后较旧版本不能倒退 head、败者取消仍保留已捕获版本。

### 21.3 计量与尚未迁移的成本

新增冷查统计 `localTransitionSequences/localVersionInputs/localVersionInstalls/mutationBaseVersionInputs`；末项也包含 proof 的
exact-version 输入。计数在已有 shard 临界区更新，冷查询逐 shard 汇总，不为每次局部操作增加跨 shard 的共享原子计数。
这些是实际投影/记录工作，不是 unique 页面数、字节复制量、哈希 probe 数或整操作成本；序列失败仍计输入，不计安装。
原 `transitionDecisionNanoseconds` 仍不能当作 shard/owner hold 或完整 M；局部输入构造、索引安装、provider 及外层生命周期另计。

完整 snapshot 导出改成显式调用并统计 `fullSnapshotExports/fullSnapshotVersionInputs`；
`backgroundSnapshotExports/backgroundSnapshotVersionInputs` 是其中回收线程子集，**不能相加**。commit/restore、通用控制转换、
GC 与 diagnostic 导出均可能产生这项成本，不以局部桶减少掩盖全管线债务。新增索引的逻辑字段计入 trackedPayloadBytes，
该指标仍不含完整 allocator/hash/list node 开销，也不是 RSS；新旧布局不可直接套旧常数推导内存性能。

真实 native 用例的 1/4/8/16 BPP × 保留 0/7/63 段：一次首写+同页重访+seal 的局部输入均为 **3**、安装均为 **4**，
exact snapshot 输入分别 **3/5/5**；前台没有整页 snapshot 导出。旧 captured overlay 与事务 abort 后的旧像素继续可读，最终 close 归零。
这证明所测子链不再随历史版本数线性复制容器，**不证明完整 E、GC、root commit 或总内存也已独立于 H**。
reference 输入 lookup 另覆盖 0/255/4095 个历史版本；并发 token 进出、slot 拒绝/回收后重用及全部字段差分单独验证。

§21 检查点的剩余成本：完整候选/控制路径仍导出并安装全页历史（root 候选的后续迁移见 §22），节点/哈希分配及索引维护需要最终实测；历史 GC/总积压预算、
owner 输入/安装、全部 producer/legacy 迁移、原位 permit 仍开放。完整 M/K/X/E 和 RAM/显存/UMA 验收仍在整体重构完成后执行。

### 21.4 最终正确性检查点

新增 66 个场景：16 类局部 writer/cancel/capture/alias/fallback 成功或拒绝 × 0/17/257 历史（48），
exact lookup 0/255/4095 历史（3），四线程 capture token 进出（1），slot 回收重用（1），多事务 Prepared 完整 oracle（1），
真实 native 1/4/8/16 BPP × 0/7/63 retained overlay（12）。所有局部序列同时验证失败无前缀安装与完整状态/退休 effects；
旧诊断快照、实际 retained 像素和并发回归继续保留。

`final-build` 的 CPU/Vulkan 构建均结束后，`final-*` 完成 15 套完整测试 **1017 passed**、paint-device 选定槽 **9 passed**，
14 组各 20 次、**280 次重复**全部通过，合计 **296 个测试进程**。Reference 为 153、CpuMutation 为 326，
painter 99、tiled manager 291；Qt totals 含 init/cleanup，重复进程不混入完整套件总数。最终无 FAIL/SAFE ASSERT/QFATAL。
架构、whitespace、实际库/插件加载路径、文档链接及当前 source/binary/doc hashes 由独立 verifier 核对；
§20 旧 manifest 不改写，D11/D12 仅 archive-only，reference 负例保留。此检查点不授予 P3/P4/P6 结清或性能资格。

## 22. 2026-09-21：root metadata 的索引候选与发布 delta

本轮继续推进写生命周期中的发布结构，不追加读缓存微调。实现、可重跑日志与当前检查点位于
[br1_publication_delta_20260921](../../../evidence/br1_publication_delta_20260921/README.md)。
它替代 §21 阶段普通 root commit/restore 导出和安装整页 history 的路径；不是整个短发布/回收阶段结清。

### 22.1 单一权威下的有界输入

`VersionRecords` 增加 `preparedByTransaction` 与 `mutableVersions` 索引，和 exact/physical-slot 索引一起，
由所有 put/remove、完整兼容安装与局部 publication 修改同步维护；不是新增事务权威。
普通 commit 只取当前 Published、目标和**本事务全部 Prepared**：必须继续拒绝非最新 own Prepared，
把旧 own Prepared 转成 Historical，同时保留独立事务的 Prepared。工作量为本次相关记录 P，不取无关保留历史 H。
restore/default 取当前与目标，并从 mutable/slot 索引取得必要拒绝见证；不能把未投影历史误当“没有冲突”。
已知有效边界内仍执行共享状态机，不对部分投影运行完整页面不变量验证；测试在安装后导出完整页面、逐字段和 full oracle 比对。

普通候选输出 header、publication/preparedBy delta 和至多一个新 default 记录；候选不携带要重装的全页 snapshot。
安装先 claim 全批页面并逐页严格复验 revision，再修改实际变化记录；不会重写未变的 replica、lease、pin、last-use、captured token 列表。
这与 §18 的 detach 动态保护合并不同：**root 发布没有放宽 revision 检查，也不合并任意陈旧候选**。
mutation detach 同步改用 publication 字段安装，不再为两个标量的变化重建 replica slot 索引。

### 22.2 生产输入、默认恢复及同步退休预算

实际 `PageStore::commit/restoreRetainedEpochImpl` 已接入：默认改变/完整恢复的目录读取只导出 headers；
需要的当前/目标记录通过精确 lookup 获取，删除预检也不复制 H。目录扫描仍为 O(N)，只在原语义需要时执行，
不能宣称整个默认变更或 full restore 是 O(K)；pageRegistrationCount、head、事务与 retention 复验保留。

恢复尚未注册的 exact default **版本**时，metadata 候选生成该版本，descriptor 随成功 metadata 安装后、root 切换前安装。
预检不再调用 `ensureVirtualDefaultLocked` 修改 live history；被新事务/冲突拒绝时，不留下默认版本或 descriptor 的预检安装。
这不改变缺失 **page** 的注册协议，也不删除其他消费者的 default materialization/control 路径。

`CommitTransactionAndDiscardIdleHistory` 只是同步退休捷径：单个 changed page 超过 **32 条版本记录**时，
在导出 snapshot 前拒绝该捷径。现有 owner fallback 改跑普通 commit，随后把历史收集交给后台。
32 是显式同步记录工作预算，不是性能最优值、物理字节上限或全局退休队列预算；小批 fused 仍检查每个实际 replica 的保护状态。
边界测试包含 32/33 条输入。不得把“超过预算”当成用户事务失败，也不得隐藏后台 GC/drain 的代价。

### 22.3 计数、证据与剩余边界

新增 shard-local 冷查计数：`publicationVersionInputs` 数候选实际投影记录（含失败/重做），
`publicationVersionInstalls` 数普通 delta/新增记录，fused 则数完整安装的保留记录；
`publicationVersionRemovals` 单列 fused 移除记录，不能用“只安装 1 条”掩盖历史销毁。
`publicationFullSnapshotPages/publicationFusedBudgetDeferrals` 区分完整捷径输入与预算回退，
`publicationLookupVersionInputs/publicationDirectoryHeaders` 单列生产预检输入与目录扫描。
这些不是时间、unique 页数、hash probes 或完整 M/E；完整 snapshot 与后台子集计数保留且不相加。

新增完整 oracle：18 类提交/恢复/default/冲突/保护场景 × H=0/31/511，及 fused 预算 4 个边界场景。
真实 1/4/8/16 BPP × H=0/7/63 的单页提交固定输入 **2**、安装 **2**；两页 root 恢复固定输入 **3**、安装 **2**，
lookup **3**、目录 headers **2**；这两段没有前台完整 snapshot 导出。旧 View 在恢复后仍读旧像素，close/provider bytes 归零。
缺失 default 的准备不可见/新事务拒绝/成功后 descriptor 可用另覆盖 8 个场景，前台完整导出同样为零。
以上只是所测实际子链的工作量证据；历史引用、provider、后台收集、root/extent 及完整操作总成本仍须分别归因。

仍未完成：owner-issued 原位 permit、其余 producer/legacy 入口统一；通用控制/GC 的全历史布局与总积压预算；
root/extent/descriptor 的完整 owner 临界区与候选销毁/冲突重做成本。
新 default 记录/hash 与 descriptor 插入仍可能在发布区分配；小 fused 仍完整安装，单版本的 replica/protection 列表也不是零成本。
所以本轮是**按变化记录安装**，不是“无锁”“零分配”“整个提交已为 O(K)”或“全部短发布完成”。
最终 RAM/显存/UMA 与 M/K/X/E 整体性能测试仍在结构完成后运行，不拿正确性并行测试的耗时宣称性能达标。

### 22.4 当前正确性检查点

新增 78 个场景：reference root 差分/预算 58，实际提交/恢复 H 矩阵 12，默认恢复候选/拒绝 8。
`final-build` CPU/Vulkan 完成后，15 套完整测试 **1095 passed**，paint-device 选定 **9 passed**；
16 组各 20 次、**320 次重复**全部通过，合计 **336 个测试进程**。Reference 211、CpuMutation 346、painter 99、tiled manager 291。
Qt totals 含 init/cleanup，重复进程不混入完整套件总数，最终无 FAIL/SAFE ASSERT/QFATAL。
verifier 核对完整 inventory、54 行 root oracle/4 行预算边界、真实工作量矩阵、默认恢复 8 行、构建时序、实际库/插件路径、
架构/whitespace、文档链接及 source/binary/doc hashes。§21 及更早证据不覆盖，D11/D12 仅 archive-only。
本轮仍为 working correctness checkpoint：structural_completion=false，performance_qualification=false。

## 23. 2026-09-21：长历史续扫与局部退休

本轮从实际后台 history worker 贯通到 metadata 退休，不仅增加预算字段。证据见
[br1_history_slices_20260921](../../../evidence/br1_history_slices_20260921/README.md)。

### 23.1 有序历史索引、值游标和同一安全状态机

`VersionRecords` 新增按 generation/default revision 排序的 Historical 索引，所有 publication 变化、record put/remove 均维护。
pin/reader 等不改变 publication 的更新不再删除/重建 publication 索引；新增索引的分配与维护不是免费工作。
`historySlice` 用 exact identity 值游标和 upper_bound 续扫，每次最多返回 32 个 Historical 记录；没有指向已删除 list node 的借用迭代器。
删除游标所在记录不影响下一次定位；同 generation 的不同 default revision 分开。重新变为 Historical 的旧 generation 可能在游标之前，
因此值游标不是不可变 View，不能遗漏“有语义/资格事件时完成当前轮后重新从头扫描”的协议。

`DiscardHistoricalVersions/DiscardSupersededPreparedVersions` 进入 owner 局部转换白名单：仅选择指定记录及必要 own Prepared 见证，
仍运行同一状态机，对 captured token、authority、lease、pin、last-use、provider operation 以及 superseded 归属逐项拒绝。
整个选择集成功才安装；不重装未涉及历史。局部退休 effects 的顺序不作为契约，完整 oracle 比对身份/效果集合、数量及全部最终字段。
最后一次 captured Prepared 释放的查询也改用 exact lookup。root 可达性与物理保护仍独立，局部 discard 并不自行证明 root 已不可达。

### 23.2 真实 worker 续扫、失效与销毁

生产后台 worker 每 pass 最多选择 **16 keys**，每 key 最多 **32 historical records**，故枚举最多 **512 条历史记录**。
未完成页面排到 FIFO 尾部；新候选按预算加入，长页不会反复占据 QSet 首项。外部语义/资格事件标记进行中 sweep 需要再扫，
continuation 自身不设置 repeat，合法保留的历史不会触发无事件忙循环。§23 时先清空 root/事务记账才判断历史；§26 已解除此队列屏障。

§23 检查点的同一页/轮可达版本集合取自全部已注册 root（当前实现已由 §26 改为逻辑 admitted roots），跨切片复用；current epoch 改变时必须刷新。
该缓存安全性的前提是：新可见 root 总会推进 current epoch，保留/事务只能引用已注册 root，reserved root slot 尚不可见；
删除 root 只会缩小集合，旧缓存最多保守多保留，并由原 retention-release rescan 请求触发新轮。
这些前提若改变，必须重新证明失效机制，不能用当前 head 代替受保护旧 root 的可达性证明；§26 给出了新的准入与单调性条件。
没有历史输入的切片不建立 reachability 缓存。替换/完成 sweep 后，旧集合移出 owner 临界区，在 worker 上析构。

恢复旧版本再写入会把旧 generation 重新插到游标之前；真实 provider barrier 回归验证了该事件与 head 改变后继续/重扫，
最终只剩正确 current 页，无漏回收或旧像素损坏。last-use、旧事务 base 和拒绝 close 后恢复调度的既有回归继续运行。

### 23.3 口径与尚未结清部分

`historySliceQueries/historySliceVersionInputs/maximumHistorySliceVersionInputs` 数局部枚举；
read-scope stats 的 `historicalGcVersionsVisited/maximumHistoryVersionsPerPass/historyReachabilityRefreshes` 数 worker 输入和刷新。
`activeHistoryScans/cachedHistoryReachableVersions` 另列临时派生缓存，完成后归零；不是逻辑 ownership，也不是精确 bytes/RSS。
`localVersionRemovals` 显式记录移除。现在 GC 同样使用 local transition，因此新增 `backgroundLocal*` 及
`backgroundMutationBaseVersionInputs` 作为总数子集；native 前台结构断言改算 total−background，后台代价仍留在完整 M/E/drain 中。
不能把后台 local 输入混入“单次首写”计数，也不能相加重复计费。原 fullSnapshot/background 子集口径不变。

新 reference 验证 0/31/32/33/511/4095 历史续扫、删 cursor 记录、default revision 与重启，及 20 类历史/Prepared 退休接受或拒绝。
真实 1/4/8/16 BPP × H=65/257 的保留、分批回收和 pin 释放，切片上限 32，最终恰好移除 H，前台/后台均无整页 metadata snapshot 导出；
root 改变/游标前重新插入另覆盖四种 BPP，临时缓存与 provider bytes 最终归零。

**仍未结清**：reachability 刷新仍可能在 owner 内遍历 R 个 root；单记录 replicas/protection、索引节点分配、缓存集合构造和总队列背压
没有硬时间/字节预算；非 background provider 的同步兼容收集、部分控制转换及 cold close 仍可导出整页。
本轮消除了生产长页枚举/退休对全页 snapshot 的依赖，不宣称整个 GC 零分配、O(1)、无全局锁或回收总预算完成。
原位 permit、其余生产入口、完整短发布及最终 RAM/显存/UMA 的 M/K/X/E 验收仍开放。

### 23.4 当前正确性检查点

最终以 `verified-build/verified-*` 为准：CPU/Vulkan 构建均结束后，15 套完整测试 **1133 passed**、paint-device 选定 **9 passed**，
18 组各 20 次、**360 次重复**全部通过，合计 **376 个测试进程**。Reference 237、CpuMutation 358、painter 99、tiled manager 291；
Qt totals 含 init/cleanup，重复不混入完整套件总数，最终无 FAIL/SAFE ASSERT/QFATAL。
两个 CPU benchmark consumer 也按新增统计结构重建，但未运行性能采样。

`indexed-build` 的 private 调度器符号链接失败原样保留；其后的 `indexed-*` 误跑旧二进制结果明确排除。
补齐 private symbol 导出后，guards 回归、新计数的 final 全矩阵，以及测试早退生命周期加固后的 verified 全矩阵分别留档，
不覆盖旧日志、不把旧 binary PASS 冒充新测试。runner 已要求最新两套 build 均成功才允许测试。
verifier 核对当前矩阵、阶段/排除清单、loader、源码/二进制/文档 hashes、链接/whitespace/架构与 D11/D12 archive-only。
structural_completion=false，performance_qualification=false；本检查点不授予 P3/P4/P5/P6 或 BR1 结清资格。

## 24. 2026-09-21：packed write 原生生产入口与锁边界

### 24.1 一条实际写入口，复用同一生命周期

`KisTiledDataManager::writeBytes` 正常路径不再经 `KisTileDataWrapper` 的逐页 read/write lease。
backend 的 `runCpuMutationOperation` 与 §20 像素操作共用完整目标集保留、匿名/history client、私有 mutation、seal、失败取消和终结。
共用层直接使用调用方去重后的 target set，不为像素操作重复构造同一范围集合；范围 workItems 按 distinct targets 计。
保留目标范围后捕获一次 frozen sealed overlay，再逐页比较输入；确认相同不创建 generation/backing/proof。
真实修改直接取得 mutation guard，部分覆盖 preserve，整页覆盖 `DiscardContents`，每页释放 read pin 后再取得 writable pin，
写 guard 释放只归还 pin，整个段成功才 seal。失败不重放兼容路径，也不撤回同事务之前已 seal 的合法兄弟段。

有 live legacy borrower/intent 时在任何像素工作前返回 Borrowed，沿用兼容路径和原有裸指针可见性；不能把它报成 native 原子操作。
无能力才 Unavailable；Failed 不是退路信号。空输入是无工作；stride/坐标/索引范围在业务入口先验证。
写体使用负坐标安全的页块遍历，输入 padding 不写入页；changed-key 索引仍在完成后单独刷新，不按全图扫描。

DataManager 写锁现在只覆盖入口检查和成功后的派生索引刷新。范围等待、比较、像素复制及 canonical seal/commit 不持有该锁；
backend 的全范围保留与 PageStore claims 仍有效。这不是整体无锁：backend registry、owner、binding/swap 等必要协调仍存在。
新增并发读回归在修改中的页上读取完整旧像素；收窄锁之前该测试稳定因读者不能进入而失败，反例保留。

### 24.2 性能归因和未完成部分

完整写入口仍计 `write_bytes_owner_wait/batch_begin/body/batch_finish`：native body **包含**通用操作阶段的范围保留、事务和 seal/commit；
batch_finish 包含重新取得 DataManager 锁及索引刷新，不能继续沿用旧版“body 仅像素、finish 才 commit”的归因。
共用生命周期暂保留 `pixel_operation_*` 相位名（也覆盖 packed 路径），其中 body 的子阶段另列
`packed_write_capture/compare/prepare/copy/release`。compare 包括 exact 解析与 pin，prepare 包括 allocation/COW/pin，copy 才是用户字节复制；
全部 nested inclusive，不能相加成为 E，也不能把 compare/prepare 时间混进纯 memcpy K。
成功 changed-key 刷新另捕获一次派生 View，不冒充业务读体的逐页 View；no-op 没有这次刷新。

本轮整页写消除的是**旧页源复制**，provider 的 discard 分配仍做默认初始化，必须保留 `defaultInitializedPages/Bytes`；
部分写仍需独立 backing/COW。no-op 比较、范围集合、版本协议及派生 wrapper/cache 的准备也不是免费工作。
下一步省初始化需要明确区分“虚拟 default 的 preserve 初始化”和“承诺完整覆盖”，不能直接取消所有 discard 初始化。
原位 permit 尚未落地：本路径仍允许后页准备/校验失败、整段 cancel，以及 history/共享匿名事务稍后 abort；
“memcpy 本身不会失败”不足以把前面的 backing 改成原位。
必须先落实 66 的 recoverable-before 或 all-fallible-preparation-before-write 的 exclusive-immediate 协议，
并协调 capture/base/alias/identity 失效；不能把物理 claim 当逻辑 permit。完整短发布、其余 producer 和总回收预算仍开放。

### 24.3 正确性证据

证据目录：[br1_packed_native_20260921](../../../evidence/br1_packed_native_20260921/README.md)。
新增矩阵覆盖 1/4/8/16 BPP × history × full/partial × no-op，含负坐标、带 padding 输入、旧 View、undo/redo、
零 generic read/write request、distinct generation、bounded pins，以及 full-write 零源复制但默认初始化仍存在的显式计数。
第二页 writer 冲突验证第一页面取消和此前 history 不丢失；borrower、非法布局/坐标、空输入、与 native pixel operation 的
竞争发布/取消及写体内 DataManager 并发旧读另验。不以计数或这些 correctness 时长授予性能资格。
等待后输入与初始 before 相同的分支另验：竞争者发布后应真实改回 before，竞争者取消后则仍为 no-op；不得在等待前比较后跳写。

最终以 `confirmed-build/confirmed-*` 为准：CPU/Vulkan 构建均结束后，15 套完整测试 **1175 passed**、paint-device 选定 **9 passed**，
3 组各 20 次、**60 次重复**全部通过，合计 **76 个测试进程**。tiled manager 从 §23 的 291 增至 333；其余完整套件总数不变。
Qt totals 含 init/cleanup；最终无 FAIL/SAFE ASSERT/QFATAL。源码及诊断 consumer 全部重建；未运行新的性能采样。
初版、缩锁前失败、修复后及增加等待/no-op 行后的中间完整回归分别保留，不用中间 binary 结果冒充最后源码。
verifier 核对完整 inventory、工作矩阵、negative、重复组、构建/loader、文档链接、架构/whitespace 与 source/binary/doc hashes，
D11/D12 仅 archive-only。structural_completion=false，performance_qualification=false；整体核心重构与 BR1-PERF 仍未结清。

## 25. 2026-09-21：完整输入直接初始化独立 backing

### 25.1 接口语义与实际生产调用

§24 保留的“整页 discard 仍默认初始化”在正常 packed 整页路径上进一步消除：新增同步 `overwritePage(key, KisCpuPagePayload)`，
由 `writeBytes` 的完整页块消费；不是普通 `beginWrite(DiscardContents)` 的语义变更。
输入包含 borrowed pointer、rowStride 与 available byteSize，覆盖整个 logical page extent；padding 不属于像素输入，
最后一行只需覆盖实际 row bytes。调用方保持输入稳定/可读直到同步返回，不得指向同段的 pending writable target。
owner 校验完整布局和溢出，provider 及 TileDataStore 各自再次检查自己的边界；没有借用输入的长生命周期缓存或 alias。

显式 `synchronousCpuPayload` 能力表示 provider 能在返回前用最终输入初始化**独立** CPU backing。
tiles3 使用 store-only row constructor，完成所有像素复制后才 register；pooler/swapper 从未看到未初始化页。
它仍使用主干 TileData allocator/store/swap 生命周期，不新增第二套 RAM allocator。provider-owned padding 若有也必须按其布局契约初始化；
当前 tiles3 支持的是完整 64×64 tight backing。最终输入覆盖默认初始化策略，不从 before-image 读取像素，也不填默认像素后再覆盖。

没有该能力时，owner 保留普通已初始化 allocation，再将完整输入复制进去；有能力但操作失败则取消，不偷偷退回/重复申请。
正常 `DiscardContents`、虚拟 default 的部分 preserve、删除后局部修改维持旧安全契约。
首次 full payload 后的 guard 重访仍复用同 generation/backing；同段再次 overwrite 只复制一次新输入，删除后完整重写不做多余 default reset。
没有 raw 未初始化 guard，也不依赖调用方“以后一定填满”的承诺。seal/commit、metadata-before-root 和取消语义不变，仍不是原位 permit。

### 25.2 工作量与相位口径

`payloadInitializedPages/Bytes` 是 provider 在新 backing 上执行的完整输入初始化，包含最终取消/被拒绝的已完成工作；
`pendingPayloadCopyBytes` 是已有 pending 或无能力 fallback 上的显式输入复制，按段 seal/cancel 汇总。
两者区分新建直接初始化与后续复制，不与 COW、default fill、alias/adoption 或硬件 migration 混算；计数是逻辑软件工作，不是 DRAM 总线流量。
正常 packed 整页 changed 页：一份最终输入初始化、零 source COW、零 default initialization；部分页仍必要 COW，no-op 不准备。

整页输入的 allocation+copy 在 `packed_write_prepare` → `write_provider_prepare` 内，不能再把旧版 `packed_write_copy` 当全部用户像素工作。
后者现在仅为 partial 行复制；已有 pending/fallback 的实际输入复制另用 `mutation_payload_copy`，不含此前 pin/materialization。
父子区间仍 inclusive；新的 whole-input 准备时间不是纯 memcpy K。成功后的派生 View、索引刷新、最终回收及后台工作不移出 E。

仍未消除：普通 discard 及不支持该能力的 provider 的默认填充；swapped pending 完整重写仍先恢复，尚未改为无需读回的 backing replacement；
其他 producer 的 full-cover 识别及准备/发布成本、原位许可、其余生产入口和总回收预算。当前不以结构计数宣布任何吞吐/延迟比例或 UMA/dGPU 资格。

### 25.3 安全与正确性证据

证据目录：[br1_full_payload_20260921](../../../evidence/br1_full_payload_20260921/README.md)。
新 owner 矩阵覆盖 1/4/8/16 BPP × default/resident/removed base × direct/fallback × commit/cancel，共 48 行：
带 padding、最后一行最小长度、输入随后修改不影响 backing、真实 swap/reload、同段同 generation、删除后再覆盖、旧 View 与零通用 request。
14 条无效布局/地址溢出分别经过 owner 与 store factory 边界；准备中 capture/独立页提交、禁止 abort/close、分配/binding 失败与 seal validate 失败另验。
冷 alias 的覆盖不读取 alias source。packed 生产矩阵现在同时断言 source COW=0、default fill=0 和恰好一次 payload initialization，
不只以 façade 的 copy 计数替代真实调用。旧 §24 证据完整保留，新的工作量与相位不能追认到旧二进制。

`checked-build` 完成 CPU/Vulkan 全部目标后，focused 72/52/21 passed；`final-*` 的 15 套完整测试 **1241 passed**，
paint-device 选定 **9 passed**，3 组各 20 次、**60 次重复**全过，合计 **76 个测试进程**。
CpuMutation 从 §24 的 358 增至 424，其余完整套件 totals 不变；Qt totals 含 init/cleanup，repeat 不混入完整套件总数。
最终无 FAIL/SAFE ASSERT/QFATAL；两个 benchmark consumer 按接口/统计变化重建，但没有运行新的性能采样。
verifier 检查完整 inventory、48/14 行输入矩阵、3 类 provider 故障、准备 claims、32 行 packed 生产矩阵、重复组与 loader，
并冻结源码/二进制/文档/日志 hashes，核验链接、架构、whitespace 和 D11/D12 archive-only。
structural_completion=false，performance_qualification=false；本轮关闭的是正常 packed 完整覆盖的冗余默认填充，不是整体核心重构或 BR1-PERF。

## 26. 2026-09-21：逻辑 root 准入与物理回收解耦

### 26.1 关闭退休 root 重新接入的缺口

此前 `beginTransaction(epoch)` / `retainSnapshot(epoch)` 只验证 root 仍在 registry 中。
后台预算回收使失去最后保护的旧 root 仍可暂存，因此“尚未销毁”错误地保留了重新取得历史能力的机会；
特别是 fused idle-history retirement 已移除旧像素 metadata 后，旧 epoch 仍可能被接纳为新事务 base。
不能靠更快 drain、瞬时无 reader 计数或提前把旧树全部销毁来建立原位许可。

当前以现有两个 counted protection index 定义准入：**current root，或仍有 snapshot retention，或仍是 active transaction base**。
`beginTransaction/retainSnapshot/root` 使用同一规则；检查与新保护登记、最后释放、事务终结和 root 切换都在同一 epoch gate 下完成。
先取得新保护则旧 root 延续存活；先失去最后保护则新接入失败。queued root、finished transaction 和裸 metadata copy 都不能复活旧 epoch。
current 无显式 token 时仍可正常捕获；仍受保护的历史可继续被合法借用，保留 undo/save/transaction-base 的既有语义。
不新增第二套可见性 authority、全图标记或普通逐页读的全局登记；已有 guard 在固定 View 内的热读路径不变。

`rootCount/immutableRoots` 继续统计物理 registry（不含 unpublished reserved slots），包含待回收树；
`root(epoch)` 返回可接入的结构 metadata，不是 pixel retention。此前已返回的 immutable metadata copy 仍可解析自己的树，
但不能授权稍后重新读取或修改已退休的像素。需要跨发布访问的调用方必须持有真实 token/View/active base。

### 26.2 按必要保留集合查询可达性

`reachablePageVersions` 不再遍历 registry 的所有 root，而从 current、snapshot-root counts、transaction-base counts 查询。
两类索引重叠及 current 去重，同 root 的重复 snapshot/transaction 不增加 root 查询次数，也不构造临时 dedup 集合。
固定查询 keys 时工作量随 distinct 合法 `R_live` 增长，不随物理退休积压或重复 token 数增长；每个 root 内仍承担稀疏索引查找。
§23 的 worker 每轮缓存继续成立：新可见 root 推进 head；同一 head 下新保护只可引用已经 admitted 的 root，不扩张逻辑集合。
最终保护释放只缩小集合，通过既有资格事件触发重扫；旧缓存至多多保留，不能误回收。reserved candidates 仍不可见。

这允许在物理 root 队列尚未清空时回收已不可达的历史像素，但不绕过精确版本的 captured token、lease/pin、provider operation 或 last-use。
native read guard 持有所属 View，因此 caller 释放 View facade 后 guard 仍保留 root；generic lease 只保留 exact replica，不授予整个旧 epoch。
新 `historyReachabilityRootsVisited` 累计 worker refresh 实际探查的 distinct roots，与 `historyReachabilityRefreshes` 配套；
不是树节点数、registry 大小、token 数、总回收工作或 wall time。合法长历史、动态保护列表、缓存/队列内存和完整 drain 成本仍独立计量。

真实积压回归进一步揭示了旧调度依赖：即使 reachability 已改，worker 仍等待 `epochs.hasCollectionWork()==false` 才处理像素历史。
现在删除这一全队列屏障，同轮分别推进 32 finished transactions、32 root 候选及最多 16 keys × 32 historical records；
判定采用逻辑保护，物理 registry 未清空不再阻塞已符合条件的像素退休。各预算仍独立，不声称形成完整时间/字节预算。
H=65/257 的回归明确要求 provider retirement 发生时仍有退休 root 积压，不能只在全部 drain 后检查最终大小。

### 26.3 边界与下一依赖

这是原位许可的必要准入条件，不是完整 permit。当前 root 仍允许新捕获；真实原位操作的 capture fence、物理已知 owner claim、
old identity/alias/cache 失效、recoverable-before 或首字节前完成全部可失败准备、不可失败发布等仍未贯通。
生产 mutation 继续安全的独立 backing/COW；不把“无旧 root 可复活”当作允许修改 Published bytes 的充分证明。
完整短发布、其余 producer 与总回收时间/内存预算继续开放，整体重构后才运行统一 M/K/X/E 资格测试。

### 26.4 正确性检查点与保留的反例

证据目录：[br1_epoch_admission_20260921](../../../evidence/br1_epoch_admission_20260921/README.md)。
reference 新增 8 行 commit/restore × snapshot/transaction 保护组合，4 行 H=0/7/127/1023 的积压与重复保护去重，
12 行最终 release/abort 与 retain/begin 的先后或并发（每行 32 次）。覆盖候选 metadata 拒绝、raw tree 可解析但不授予历史、
collector 尚未执行时即拒绝 stale epoch。真实 owner 新增 24 行 BPP × none/snapshot/base/View/native guard/generic lease，
另有 16 行 BPP × H=65/257 × 保留/释放最旧 View，证明 root 积压中即可退休且每次刷新只查询 1 或 2 个合法 root。
现有合法长历史矩阵同时验证必要 R_live 的查询计数，不把仍有保护的历史排除在工作量外。

`checked-build` 暴露测试误用 private capture API 与不可 move-assign lease，改为公开 capture 与直接构造，未运行失败构建后的旧二进制。
`confirmed-*` 的 16 行积压进度断言失败原样保留；原因是旧 worker 队列屏障，生产修复后同一断言通过，不削弱为只验最终 drain。
`progress-build` 完成 CPU/Vulkan 构建，`progress-*` focused **34/54/52 passed**；`final-*` 为最终完整矩阵：
**15 套 1305 passed、paint-device 选定 9 passed、3 组各 20 次共 60 次重复全过，76 个测试进程**。
Reference 261、CpuMutation 464，Qt totals 含 init/cleanup，重复不混入完整套件 totals；最终无 FAIL/SAFE ASSERT/QFATAL。
测试与链接不并行；两个 benchmark consumers 重建但未采样。verifier 冻结源码/二进制/文档/日志、检查矩阵与负例、loader、
链接、whitespace、架构 guard；structural_completion=false，performance_qualification=false。
本轮封存时发现 D11/D12 引用的原 `/tmp` runtime 已缺失，因此其完整 `--archive-only` 重验标记 unavailable，不声称通过。
独立核验仓库内 sealed artifacts 和仍存在的 frozen inputs，缺失路径及原失败输出存入 `final-checks.json`；
不修改旧封存脚本/数据，不用当前 binary 冒充历史运行库。本轮构建/正确性证据不依赖这些旧 `/tmp` binary。

## 27. 2026-09-21：发布后的退休排队使用已有记录

### 27.1 移除 metadata 安装后的队列扩展

§26 之后审阅 `installCommit` 的完整尾部发现：metadata 已接受安装、root 切换之后，`finishTransaction` 仍可能扩展终结 deque，
`queueRoot` 仍可能扩展去重 QSet 和 root deque。仅提前保留新 root 的 hash slot 并没有完成这部分发布准备。

当前 `EpochRootRecord` 与 `EpochTransactionRecord` 在已有 registry value 内保留 queue flag 与 next identity；
record 本身分别在初始化/候选 root slot 或 transaction begin 时创建。发布、事务终结及最后 snapshot 释放只连接已有记录，
不再为这三类排队动作分配 queue node 或 dedup entry。root 队列仍去重，事务终结仍一次入队，两个 FIFO 与预算互相独立。
链接使用单调 identity，而非 `QHash` value 的地址/iterator；registry rehash、reserved-slot 取消或收集时移动 value 不破坏链。
registry 不对外共享或复制，调试断言要求 mutation 时 hash 未共享，避免将来引入隐式 detach 分配。

reserved root 不进入退休队列，也不对捕获/可达性可见；candidate 拒绝/销毁只移除自己的 unpublished slot，不终结仍合法的事务。
历史 root 被预算检查但仍有保护时出队；最后保护释放可再次入队。队列耗尽时 head/tail 同时复位，current root 只被检查、不被删除。
`collectUnretainedRoots` 预算仍计检查数，而非成功移除数；`collectFinishedTransactions` 仍按终结记录数收集。
§26 的准入规则和双预算同轮推进保持不变，没有提前释放像素或改变 root/metadata 可见性。

### 27.2 范围与未完成依赖

消除的是 epoch 层 publication/final-release 的**额外排队分配**，不是整个 commit 无分配或无失败的证明。
metadata 中新增 default/history 索引、descriptor/root registry 准备、completion、owner 后续清理、真实树/事务析构、provider 退休与 worker 调度
仍可能有分配、锁等待或其他成本。record 增加固定链接字段，不能仅凭删除两个容器宣称 RSS 或完整 E 已降低。
普通 mutation 仍独立 backing/COW；capture fence、完整 owner permit、恢复/不可失败发布及总体回收预算继续开放。

### 27.3 正确性覆盖

证据目录：[br1_epoch_queue_20260921](../../../evidence/br1_epoch_queue_20260921/README.md)。
新增 1/33/513 epochs × 两类队列收集先后共 6 行，覆盖 repeated abort/root 去重、hash 增长、metadata callback 拒绝、
同事务多个 candidate 与稍后取消 reserved slot、终结事务 FIFO、零/1/32 预算、受保护 root 出队后倒序释放重入、current 及空尾重用。
每次被拒绝候选都确认事务仍 Prepared/current 未切换，rootCount 不包含候选；与既有 admission、释放竞态、真实积压进度矩阵共同验证。

初次 `checked-build` 因删除了树析构 batch 仍需的 `<deque>` include 而失败，已恢复；没有运行失败构建后的旧测试 binary。
`verified-*` 的新增 6 行被 `model.prepare` 拒绝：测试只增加 extent revision 而没改变 extent，违反原接口契约。
测试改为真实 extent 位移并显式断言 delta 合法，不修改生产校验或放宽队列断言；失败日志保留。

`final-build` 完成 CPU/Vulkan 构建后，`final-focus-*` **40/54/52 passed**；`final-*` 为最终完整矩阵：
**15 套 1311 passed、paint-device 选定 9 passed、60 次重复全过，76 个测试进程**；Reference 267，其余套件 totals 与 §26 相同。
Qt totals 含 init/cleanup，重复不混入完整 totals；最终无 FAIL/SAFE ASSERT/QFATAL。构建/链接与测试不并行，benchmark consumer 重建但未采样。
verifier 校验新队列矩阵、旧保护/积压/生产矩阵、runtime loader、源码/二进制/文档 hashes、链接/whitespace/架构；
D11/D12 历史完整重验仍因 `/tmp` runtime 缺失而 unavailable，现存封存文件独立验证，不以新运行库替代。
structural_completion=false，performance_qualification=false；下一依赖仍包括 metadata history/default 安装准备，不能以此切片结清 permit/BR1。

## 28. 2026-09-21：metadata 候选持有发布所需存储

### 28.1 已移动到准备期的工作

普通 commit、restore 和 mutation detach 中，**已有记录**首次变为 Historical 时所需的有序 history-index node，现由
`PreparedPublication` 在 shard gate 外构造；安装阶段在所有页 claim 与动态事实复验成功后，以 C++17 node handle 移交，
不再先改 live publication 再为 history index 分配。可选 fused idle-history 路径则在准备期构造完整 `VersionRecords` 及其
exact、slot、publication 索引；安装仅交换 record-set 所有权，旧 set 至少在对应 page shard gate 释放后才析构。

候选仍是 move-only、owner-bound、一次性能力。两页批量中的第二页晚冲突、取消、foreign coordinator、移动、owner 析构均不会
留下半批 history index 或 replacement set；mutation detach 继续按安装时的 exact Prepared/owner/no-writer 事实复验，不能用
准备时快照覆盖新 reader、pin、last-use 或 writer。普通发布继续要求 exact page revision，metadata 仍先于 root 可见。

新增计数只表示结构工作量：`publicationHistoryNodesPrepared/Transferred` 与
`publicationReplacementRecordsPrepared/Installed`。准备后失败或取消仍计 prepared work，只有成功安装才计 transferred/installed；
它们不是 allocator call、字节数、耗时或无锁证明，也不应混入 M/K/X 的硬件储存事实成本。

### 28.2 明确未完成的边界

本切片只关闭 existing-version history node 和 bounded fused record rebuild 的已知安装期分配。新合成 default record 的 list/hash
插入、PageStore descriptor 更新、completion、root/transaction 以外的 owner cleanup、worker 调度及 provider 回收仍可能在完整
E 中分配或等待。旧 fused record 的析构已离开 page shard gate，但当前仍可能发生在外层 PageStore owner gate 内，因此不能写成
“全部销毁已移出发布区”或“commit 已不可失败”。普通 local transition/GC 也仍使用其既有 insertion 路径。

这不是 owner-issued 原位 permit：没有新增 current-capture fence、recoverable-before journal、allocation retag、旧 binding 失效或
首字节后的不可失败 root publication。生产 mutation 继续使用独立 backing/COW。下一步应先处理新增 metadata/descriptor storage 与
retired payload 的 owner-gate 移交，再据完整失败面设计 permit；不得仅凭本轮 node transfer 调用底层 physical claim。

### 28.3 正确性证据

证据目录：[br1_metadata_storage_20260921](../../../evidence/br1_metadata_storage_20260921/README.md)。初次构建因同一新增测试被重复合入而在
编译期失败；合并为一套更严格矩阵后重新构建 CPU/Vulkan，两套均通过，且没有运行失败构建后的旧 binary。
新增 **3 类路径 × 6 类结局 = 18 行**；最终 focused 为 **98/74/52 passed**。完整矩阵为 **15 套 1329 passed**、
paint-device 选定 9 passed、60 次重复全过，共 76 个测试进程；Reference 285、CpuMutation 464，其余 totals 与 §27 相同。
本轮未采样 benchmark，`structural_completion=false`、`performance_qualification=false`，不能结清短发布、permit 或 BR1。

## 29. 2026-09-21：新增 default record 的候选存储与容量准备

### 29.1 不复制 H 的新增记录安装

§28 留下的普通 publication 新记录仅来自 `ReplaceDefaultPixel` 或 restore 缺失的 exact default。当前候选用 `std::list` 持有
完整 record node；状态机计算完成后，在准备阶段重新取得该页局部 shard gate，以同一个 exact revision 复验并为 live exact/slot
`QHash` 预留容量。安装仍先取得整个批次的 page claims；随后把候选 list node splice 到 ordered records，写入已预留索引，并断言
两个 hash 的 capacity 在安装前后不变。没有为了一个 default 重建或复制 H 个 retained records。

如果页在状态机计算与容量准备之间变化，prepare 立即失败；容量准备之后再变化，则安装的原 revision check 拒绝整个批次。
预留容量本身是非语义存储变化，不增加 page revision；它发生在 preparation 的局部 gate 内，可能阻塞该 shard，且被取消的候选可能
留下可复用的额外 capacity。不能将“capacity 不增长”外推为 Qt 内部绝无任何 allocator 行为；正式 allocator 结论仍需专用 hook。

新增 `publicationAdditionRecordsPrepared/Transferred` 按 record 数区分准备工作和成功安装。新增 default 与 existing-version history node
可同时出现；失败/取消只有 prepared，无 transferred。它仍不是硬件 M/K/X 时间、字节量或延迟指标。

### 29.2 仍未完成的发布面

PageStore 的 descriptor `QHash` 插入仍位于 metadata install 后、root 切换前的 owner callback；completion ticket、effects/discarded vectors、
旧 fused set 的最终析构、后处理与回收调度也有各自成本。普通非-root local transition/GC 仍使用直接插入。因而本轮只关闭 metadata
record node 与已知 hash growth，不声明整个 metadata install、owner critical section 或 commit 无分配/不可失败。

原位 permit 的捕获阻断、旧 View/active-base/alias 协调、allocation identity retag、旧 binding 失效、abort 恢复或首字节后的不可失败链仍
完全开放；生产写继续独立 backing/COW。下一步应处理 descriptor/retired payload 的准备与移交，并把完整 publish failure surface 逐项变为
预备或可恢复，再设计 permit，而不是直接消费 D12 physical claim。

### 29.3 正确性证据

证据目录：[br1_metadata_addition_20260921](../../../evidence/br1_metadata_addition_20260921/README.md)。初次两套构建通过；首次 focused 暴露
`entry.next` 尚未赋 key 就进行容量复验，以及新增测试 default header 未匹配其 version 的 fixture 错误。修正时序与 fixture 后重新构建，
focused **104/74/52 passed**。最终完整 **15 套 1335 passed**、paint-device 选定 9、60 次重复全过，共 76 个测试进程；
Reference 291、CpuMutation 464。失败日志保留，未通过削弱 revision/原子性断言解决。未采样性能，结构与性能资格仍为 false。

## 30. 2026-09-21：descriptor 容量准备与解锁期变更复验

### 30.1 owner descriptor revision

PageStore 中所有 descriptor 增删现统一经过 owner helper；只有实际新增、移除或值变化才推进 `descriptorRevision`。commit/restore 在
释放 owner gate 进入 metadata/root 构造前，按本候选可能新增的 default descriptor 数调用 `QHash::reserve`，记录 revision；重锁后如果
期间任何私有 generation 的 descriptor 增删改变 revision，则放弃 metadata/root 候选并重做。另一个候选仅扩大 capacity 而未改变语义
不会触发重做，也不会因旧 capacity 数值不同误拒绝。

最终 root callback 仍保持 metadata → descriptor → root 顺序；descriptor 新增只进入已预留表，并断言有新增时 capacity 在 callback
前后不变。fused discard 的 descriptor 删除不要求 capacity 相等。新增统计区分 capacity preparation、成功 descriptor installation 以及
commit/restore descriptor reprepare；重试是真实工作，不能从 E 隐去。

这一实现避免在 publication callback 中发现并执行 hash growth，但 reserve 本身仍在较早的 owner 临界段内，`QHash::insert` 也没有
allocator hook 证明“零调用”。取消/重试可留下非语义 capacity；全局 descriptor revision 对无关私有 generation 变化采取保守重做，
以换取简单可靠的容量证明，后续应通过真实并发工作量决定是否改成分片/页级 claim，不能先弱化复验。

### 30.2 仍开放的 failure/cleanup 面

completion ticket 在最终 owner 阶段生成；metadata candidate 和 fused swap 后的旧 `VersionRecords` 仍可能在外层 owner gate 内析构；
effects/discarded vectors、proof/transaction cleanup、worker scheduling 与 physical retirement 也尚未完成同一套准备/预算协议。
因此这里仍不是完整短发布或首字节后不可失败路径，也不能据此接通原位写。下一步先把 candidate/retired metadata payload 的析构所有权
移出 owner gate并量化预算，再审阅 completion 与其余 postwork。

### 30.3 正确性证据

证据目录：[br1_descriptor_storage_20260921](../../../evidence/br1_descriptor_storage_20260921/README.md)。CPU/Vulkan 构建、focused
**104/75/52 passed**；新增真实 default publication 用 disjoint private generation 的创建/取消改变 descriptor revision，确认首个候选重做、
第二次安装，directory revision 不变且旧像素不受污染。restore 缺失 default 断言每次成功候选恰有一次容量准备和一次安装。
完整 **15 套 1336 passed**、选定 9、60 次重复全过，共 76 个测试进程；Reference 291、CpuMutation 465。
无 benchmark/TSAN/permit/结构或性能资格结论。

## 31. 2026-09-21：publication cleanup 所有权移出 owner gate

### 31.1 move-only cleanup 交接

`PreparedPublication` 安装后不再在调用表达式末尾直接析构其候选存储。metadata coordinator 可把已消费的完整候选 `Data`
移交给 move-only `DeferredPublicationCleanup`；这同时涵盖成功安装后被 fused swap 换出的旧 `VersionRecords`、普通候选 vectors/maps，
以及动态事实复验失败后仍需销毁的候选内容。cleanup 不持有可解引用的 coordinator/shard 生命周期依赖，coordinator 销毁后仍可安全清空。

PageStore 的 commit/restore 在 metadata-before-root 的同一受控 callback 内完成安装，随后释放 owner gate，再清空 cleanup，最后重新取得
owner gate 处理剩余 bookkeeping。commit 成功时必须在第一次开锁前取得 `retainedAfter`：否则另一提交可在这个间隙把刚发布 epoch 变成
无保护历史并回收。`preparingCommits` 在整个间隙继续阻止同事务 abort/close 穿越；失败候选也在 owner 外释放，不把拒绝路径的析构藏回锁内。

### 31.2 已关闭与仍开放的边界

本切片关闭的是“候选/旧 fused record-set 的析构延长 PageStore owner publication 临界区”。它没有改变页 shard 安装原子性、
metadata-before-root、descriptor 顺序、root retention 或 provider last-use。`CommitCleanup` 诊断相位现在确实发生在 owner gate 外，测试中的
observer 可重新取得 owner 状态，从结构上证明不是仅改名。

cleanup 当前仍由提交线程同步 `clear()`：析构量会计入完整操作 E，只是不再阻塞其他 owner 使用者。它没有按记录数、字节或 wall-time
切片，也没有背压/积压统计，不能称为“后台有界回收”。普通 `installMutation` 的调用点尚未接出 deferred cleanup；effects/discarded、
proof/transaction 容器清理、completion ticket 生成、history/provider retirement 与 worker 调度仍有独立成本。下一步应把 mutation cleanup
和可分批 payload 纳入统一回收队列，再审阅 completion/final owner stage；在此之前仍不能接通原位 permit。

### 31.3 正确性证据

证据目录：[br1_metadata_cleanup_20260921](../../../evidence/br1_metadata_cleanup_20260921/README.md)。首次构建因测试使用不可见的局部
`findVersion` helper 失败，修为显式查找后 CPU/Vulkan 构建通过；第一次 focused 的 history=31 两行被既有 fused 32-record 上限正确拒绝，
测试改为边界内 history=30，没有放宽生产预算。最终 focused **108/76/52 passed**；完整 **15 套 1340 passed**、选定 9、
60 次重复全过，共 76 个测试进程。Reference 295、CpuMutation 465。未运行 benchmark/TSAN；
`structural_completion=false`、`performance_qualification=false`。

## 32. 2026-09-21：分批 metadata cleanup 与预完成 host evidence

### 32.1 小候选同步、大候选分批

`DeferredPublicationCleanup` 现公开给其授权调用方一个不泄露内部记录布局的协作预算：`pendingWorkUnits()` 与
`clearBatch(maximumWorkUnits)`。一个 unit 是一个 candidate page；零页候选有一个终结 unit。fused page 自身继续受 32-record 上限约束。
这不是字节预算，也不能把单个 page 析构称为硬实时上限。

PageStore 对最多 8 unit 的候选继续在 owner gate 外同步清空，避免 K1/K8 为微小析构支付线程调度；更大候选交给已有单线程 reclaimer。
每个 pass 最多 16 unit，并在每个 unit 后检查 1 ms 协作时间预算；超限后把 continuation 重新排到队尾，不在一个 job 中无界 drain。
mutation detach、commit 成功/拒绝和 restore 统一使用该入口。cleanup 只持有独立所有权，后台 job 不取 PageStore owner/shard gate，
PageStore facade/coordinator 可以先结束；显式 `waitForRetirementIdle()` 与 close 仍会等待本 store 已排 cleanup 归零。

统计分别给出 inline/deferred/completed candidates、pass、销毁 units、pending/peak candidate 与 unit、pass CPU-wall 近似时间和从入队到
完成的 queue sojourn。计时只发生在大候选后台路径；它不能与硬件 M/K/X 混算，也不包含同期 history/provider job 的独立工作。

### 32.2 host-logical completion 不再污染最终发布区

同步 CPU 工作需要的是“调用返回前工作已完成、没有异步 last-use”的终态证据，不需要每个操作都有不同时间线序号。PageStore 因而在
configure 阶段为 host-logical source 只分配并完成一个 `readyHostCompletion`；后续只有在同步工作真正成功后才把这张已终态 ticket 关联到
proof/request/commit。operation/request/version identity 仍各自独立，不能用共享 ticket 代替它们。

这消除了 commit/restore 最终 owner 阶段的 completion registry 锁、identity 增长，以及并发 allocate/complete 乱序时可能构造 terminal
range 的分配面。它不改变 GPU timeline、CPU job 或 I/O ticket；这些异步 producer 仍须逐次提供真实 completion。也不表示整个最终 owner
阶段已经无分配：PageStore 自己的 transition/default/removal/proof 容器及 post-publication 清理仍需继续移交或预算化。

### 32.3 正确性证据与边界

证据目录：[br1_budgeted_cleanup_20260921](../../../evidence/br1_budgeted_cleanup_20260921/README.md)。初次构建因自由函数签名点名 coordinator 私有
cleanup 类型失败；改为不暴露类型名的内部模板 executor，保持原 friend/API 边界。17 页旧 proof detachment 加 17 页 root commit 的阻塞
回归证明前台累计 2 candidate/34 units，后台至少 4 passes、每 pass 不超过 16、峰值与 queue time 可见且 drain 后归零。
host source 在多轮 fill/commit/default publication 前后始终为 1 allocated、1 terminal、0 pending、1 storage record。

最终 CPU/Vulkan 构建通过，focused **108/78/52 passed**；完整 **15 套 1342 passed**、选定 9、60 次重复全过，共 76 个测试进程；
Reference 295、CpuMutation 467。没有运行 benchmark/TSAN；unit/time 是结构预算与观测，不是延迟资格。
`structural_completion=false`、`performance_qualification=false`。

## 33. 2026-09-21：写侧方向收敛为有界 backing handoff

### 33.1 采用的最终口径

[68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 现为本清单的写侧权威设计。目标不是让每次 mutation 永久建立一份
独立 payload，也不是把公开 `InPlaceWritePermit` 分发给 painter/iterator/provider。PageStore 在拥有完整逻辑事实的位置由
store-scoped coordinator 生成内联 `KisPageWritePlan`，session 持有 write set，资源所有权放在 move-only claim/`KisPreparedMutationCommit`：同段优先
`ReusePending`；唯一且可安全转移的 current allocation 走 recoverable 或 commit-only handoff；旧精确值仍可观察、
事务仍可取消或发布仍可能失败时走 `FreshCow`；已有完整输入走 `FreshPayload`，由 writer 生成且不保留旧内容走
`FreshDiscard`；纯删除/alias/default 变化走 `SemanticOnly`。

这里的 handoff 是 backing 身份和可写权的受控状态迁移。逻辑 Published generation 在可见期间仍不可变；只有 capture/retention/active base、
alias、provider last-use、GPU/I/O in-flight 和恢复条件均满足时，物理 allocation 才能从旧 generation 移交给 Prepared generation。
不确定的情况必须保守进入 COW，但保守 fallback 同样受硬字节预算，不能靠无限后台 baking/retirement 吞吐维持正确性。

### 33.2 当前代码与目标的距离

截至 §32 的生产 mutation 仍要求目标 allocation 与 source allocation 不同；这保证旧 View 和取消安全，但普通首写仍可能同时承担整页复制、
新 payload 分配以及稍后 retirement。现有 physical claim、epoch admission、锁外候选、metadata-before-root 和 deferred cleanup 都是 handoff 的
前置材料，不构成已实现的 write-plan selector、allocation retag、capture fence、recoverable journal 或首字节后不可失败发布链。

因此 [68 §4](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md#4-统一能力封装类型边界与调用方式) 不再只是方向要求：它已冻结
store-scoped coordinator、value/move-only 类型划分、字段布局、对象状态迁移、析构顺序、provider friend 边界、managed commit-only batch
和文件归属；[68 §6.4](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md#64-状态机专用-transition) 冻结两个 handoff transition。
实现若要改变这些口径，必须先修订权威设计并重新评估堆管理、并发和失败边界。此设计冻结**不增加任何实现完成或性能资格**。当前事实仍为
`structural_completion=false`、`performance_qualification=false`；在 68 的 M0–M8 阶段和 §16 完成条件全部满足前，测试仍应把独立 backing/COW
视为安全 fallback，而不是最终性能结构。

### 33.3 实施与清理顺序

1. 先完成 compact authoritative records、shard slot arena/index 和 allocation-free publication；生产 handoff 不得越过该前置。
2. 引入内部 coordinator/inline plan，把现有 pending 复用、完整输入、COW、语义写统一到一个选择与完成协议；同时统一
   allocation owner ledger、精确字节分桶、硬上限和压力状态机，使所有 fallback 都可被约束和解释；旧入口只做适配。
3. 接通 `HandoffRecoverable`，只消费已经存在的 exact alternate before；再只为完全预检、首字节后不可失败的内部 kernel 接通
   `HandoffCommitOnly`，普通可回调 mutable API 不进入该模式。
4. 将 CPU、legacy tile、iterator/accessor、painter、generic lease、GPU/transfer 逐项迁入同一选择器；不得在调用点复制 handoff 判定。
5. 通过 tiny-budget、旧 View、undo/redo、alias、in-flight、取消/失败及并发 capture 矩阵后，删除公开 permit 草案、重复 refcount 猜测、
   `beginCpuMutation()/enableCpuWrites()` 兼容包装、永久独立-backing 快捷路由和无硬上限的退休兜底。
6. 最后冻结源码与协议，统一执行 M/K/X/E。性能报告必须分别给出 before-image copy、payload allocation、payload migration、计划模式/拒绝原因、
   峰值 backing bytes、背压时间和 drain 债务，不能用模糊“zero-copy”合并这些事实。
