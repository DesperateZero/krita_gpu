> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 全性能优化链路收敛与清理（2026-09-23）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

2026-09-25 验收修正：本篇批次记录及下方“21 已闭合 / 3 局部 / 0 未闭合”是审计前历史判断。
[85 代码审计](85_br1_m5_code_readiness_audit_20260924.md) 已复现并发 domain 记账错误、metadata 预算未接线，
并确认有限预算尚未进入真实 backend；C4.2/C4.4 重开，C2.7 的共同编排仍须复核，C3.4/C4.3/C5.5 保持开放。
当前后续实施与退出标准以 [86 最终收敛方案](86_br1_m5_final_convergence_plan_20260925.md) 为准。
M5 未验收，M6/M7 不扩展；以下不改写历史构建和测试证据。

状态：实施中（量化及最终源码校验更新至 2026-09-24）。第九批后继续逐门收敛；selector、语义 staging、
读 cursor、终结持有和预算 escrow 已进一步清理，不把正确性通过当作 C2–C5 或性能资格全部完成。
当前连续修改已在同一源码上完成九个受影响目标的 x86_64/arm64 通用架构编译；arm64 运行
PageStore/Completion 7/7 套共 **995** 项、Painter **99** 项、tiles3 **334** 项全部通过。
fresh 调用图、源码 checkpoint、architecture gate 与 6 项 reachability 工具自测也在当前源码上通过。
本轮类型截肢删除纯别名、重复二值 exposure、无读取 surface role 和无消费者的 backpressure 计时；同时以固定
4096-bit replay window 替换 provider 会话永久 `consumedOperations` 集合，并把带 reachability cache 的并发 history scan 限为 16。
本文落实用户要求：范围从性能优化开始，不能把 M1 以前的实现视为不再审查的基础。
68 的 handoff 安全条件、39 的性能出口不变；本轮写入协议与预算闭合前不扩展 M6/M7。

## 1. 范围和证据

- 审查 52–64 的 D1–D10、65–66 的 mutation/physical claim、67 的结构调整，以及 68–83 的 M1–M5。
- 生产范围包括 pagestore、tiles3/storage/swap、iterator/accessor、paint device/painter、Vulkan provider/retirement。
  兼容层、统计和诊断同样在范围内；生产、测试、脚本、文档分别计数。
- BR0 `f5fbbde618` 是完整增量覆盖用的 Git 锚点，不是性能优化前的精确源码快照。
  D1–D12 按原证据的源码 hash/二进制/命令关联；无完整快照的阶段明确为无法重建净行数，不改写历史性能结论。
- 本轮起点 pagestore `.h/.cpp` 共 33,551 物理行（含注释/空行，不含 tests），69 历史记录为 24,742。
  两者不是 M5 单独增量。每个批次保存操作前源码，报告真实净变化，搬文件不计删除收益。

M5 的 admission owner 已集中，但 native/generic/adoption 的 prepare/seal/cleanup 仍分别存在。
entry state 与 cold Page 布尔状态并存；selector 未接管 pending/semantic；backing 准入全局扫描，swap 后补账，
生产有限限额配置未闭合。compact/snapshot 往返、descriptor 侧表、长期 identity 集合与兼容回调均须复审。
本轮起点的 M5B 标签调用图仍含 M5A 数据；旧 gate 通过不能证明现有管线收敛或认证死代码。

目标数据流：输入适配 → 页准入 → base/layout/初始化计划 → backing 准入及 provider 执行 → 私有写入 →
overlay seal → 原子 root commit → completion-qualified retirement。私有写入、overlay、root 的可见性边界不合并。
StateMachine、epoch、物理 gate 各保护不同事实，不能按锁或容器名字相似直接删除。

## 2. 跨阶段责任清单

| 来源 | 审查对象 | 保留不变量与清理方向 |
|---|---|---|
| D1/default/adoption | 虚拟默认页、seed mailbox、host adoption | 保留稀疏性/exact default revision；显式 source/alias 接管后删除旧协议 |
| D2–D5/publication/COW | prepared metadata、proof、descriptor、copy/payload | 原子 root、oldData、失败可恢复；共用 seal/cleanup，provider 只执行计划 |
| D6/completion | 覆盖区间、稀疏终态、owner operation 表 | 保留 terminal/last-use；消除重复历史记录，不回退逐 ticket 永久表 |
| D7–D10/read | captured view、binding/cache、generic fallback、read scope | 保留 exact generation/pin；复用验证，退出多层相同 cache/fallback |
| D11/65–67/write | CPU session、mutation、legacy lease、managed batch | 保留线程/取消/unlock 边界；共享准备和终结，适配器只描述调用范围 |
| 66/physical claim | source/pool/swap/alias gate | 保留 ABA、独占、reader/last-use 冲突；禁止由上层猜计数授予权限 |
| 67/history/GC | root reachability、队列、deferred cleanup | 保留 retained root 和退休寿命；增量工作、有界队列和总预算 |
| M1–M4/metadata | arena/index/snapshot/descriptor/commit | 保留 stable slot/generation/无分配安装；单一语义，减少投影和重复状态 |
| M5/admission/budget | entry/cold/source、writer、class/domain ledger | 页准入唯一、物理去重、失败归还；单一生命周期、增量预算事务 |
| 全阶段/诊断 | timers、census、compat stats、测试 wrapper | 保留可复现证据；随旧路径删除专属计数，不用测试数认证架构 |

## 3. 执行计划

### C0：可信证据

调用图绑定完整源码选择集合、编译数据库、manifest/ownership/census 和生成器的 hash。
生成前后复验输入不变；源文件/头文件/新增文件变化必须拒绝旧图。当前 source checkpoint 比对文件集合和内容。
保留历史比较点，刷新 checkpoint 不能自动提高侵入上限。
退出条件：旧图被拒绝，当前图由 Clang 重新生成；删除还须核对 virtual/address-taken、独占 ownership 和等价测试。

### C1：已替代的早期优化协议退出

首项 seed mailbox/host adoption：将 removal 可见性、并发竞争、独立 mutable payload、alias 和失败预算测试
迁到 `KisPageReplicaSource + aliasPage + seal`。删除 Store API/实现、provider 虚接口/实现、mailbox/析构清理及专属诊断。
未发布工作树采用删除前真实静态 gate、迁移后完整 gate/回归的连续证明；保留的语义测试不再依赖旧协议。
同样检查早于 M1 的其他优化路径；有真实生产调用的兼容接口留在 C2/C3 迁移，不直接删调用者。

### C2：写入协议和终结收敛

现有 WriteCoordinator 统一 base/descriptor/default/removal/provider 的决策和准备/取消协议。
同步 CPU 不强制生成 generic request/lease；异步访问差异只留在 provider access/completion 层。
entry 成为私有写生命周期唯一表示；cold slots 只保存必要资源，transition 尽量为临时输入。
统一 proof seal/替换/superseded 清理，root publication 仍属于 PublicationCoordinator。
修正先删除唯一重试持有者再执行可失败取消的顺序；claim/preparation/budget 覆盖所有失败出口。
退出条件：pending/semantic/fresh 共用策略，prepare/cancel/overlay seal 各有一份共同协议，旧分支同批删除。
未接线的 M6/M7 schema 不算收益；68 字段若需调整，记录原因，不能为守住字段名维护空状态。

### C3：读侧、业务 scope 和兼容层

追溯 D7–D10/67 的 view/scope/cursor/cache、iterator/accessor、backend batch 和 tile lease。
统一重复 exact-version 验证与 fallback；删除相同范围的重复 cache/target 集合。
适配器只保留 ABI/线程/unlock/operation 可见性范围；canonical 覆盖后删除包装与对应统计。
退出条件：native fast path 不增加 generic 控制工作，无多份 cache 权威、被改名保留的旧终结协议。

### C4：预算、退休和维护工作

allocation/residency/class 按受影响 backing 增量准入和更新，替代逐次全局 probes/observations。
provider 管物理库存、owner 管事务分类；swap 在资源变化前准入，usage 无副作用、不吞同步失败。
生产配置有限预算；写入暴露前取得取消/rollback 必需的退出资源，Debt 满不能丢失终结持有者。
publication/retirement 共用 class delta 计算/消费；预构造后安装不重新走另一套策略。
审查 default/history/deferred cleanup/seen-ID 集合总寿命；防重放义务有替代前不直接删除 identity 集合。
退出条件：固定 K 不扫描无关 N，批量 class change 无 K² 去重；有限预算覆盖真实 Store，失败可取消/重试/drain/close。

### C5：metadata 表示和全量验收

复审 D2 起 snapshot 投影、全页/局部转移、prepared candidate、descriptor/cleanup。
共用一份转移语义；compact record 权威，snapshot 用作边界/诊断。新生产实现接管时同时删除旧投影路径，保留测试 oracle。
退出条件：每个重写范围生产代码净减少，必要新增功能独立说明；测试增长不抵扣生产膨胀。
全部 ownership/源码/调用图/回归一致后才恢复 M6/M7；此时仍不自动授予 BR1-PERF Pass。

### C2–C5 历史检查点（2026-09-24；当前验收修正见篇首及 85/86）

以下把本节的退出条件拆成 **24 个可分别核查的门**，计数口径固定为“已闭合 / 局部 / 未闭合”。
局部不折算成完成百分比；正确性测试通过、调用图边数下降和累计删行都不能自动关闭架构门。

| 阶段 | 门数 | 已闭合 | 局部 | 未闭合 | 当前证据与最大缺口 |
|---|---:|---:|---:|---:|---|
| C2 写入 | 8 | 8 | 0 | 0 | base/descriptor、entry 寿命、Fresh 准备、同步 CPU 不经 generic lease 已落地；selector 真实决定 semantic-only/pending-reuse 及 Fresh 三策略；native/generic/remove/abort/commit 共用 proof 撤销与安装权威；generic transfer 的选择、请求和终态消费也已由 WriteCoordinator 独占。 |
| C3 读侧 | 5 | 4 | 1 | 0 | 获取/释放、exact/fallback、cache/target 的源码责任已闭合；固定 K 增长 N/H 的控制工作量曲线已加入并以内部计数器约束。tiles3 不可达 generic-write adapter 已退出，真实 generic read/tile lease/iterator ABI 兼容层仍须继续压缩。 |
| C4 预算/退休 | 6 | 5 | 1 | 0 | class delta 共用、批量 K² 去重、长期集合上限、有限 Debt 和真实 Store 的 Current/Pending/cache/SSD 拒绝矩阵均已闭合；backing domain 改为 O(P+K) 序列 journal。swap 已可靠增量同步，但仍发生在 Store 准入之前，所以 C4.3 保持局部。 |
| C5 表示/总验收 | 5 | 4 | 1 | 0 | compact record、单一转移语义、descriptor/cleanup 和逐范围净减均闭合；七套 PageStore/Completion 在 arm64 与 x86_64 各 1,000/1,000、Vulkan foundation contract 各 14/14 通过，fresh graph/gate 一致；活跃 Vulkan provider 路径与完整性能资格尚未闭合。 |
| 合计 | 24 | 21 | 3 | 0 | 已无“未闭合”门；三个局部门仅为 C3.4、C4.3、C5.5，局部不折算完成。正确性、双架构运行与静态门已刷新到当前源码。 |

门的定义：C2 为 **base/descriptor 单一准备、entry 唯一私有寿命、Fresh provider 单一策略、同步 CPU 不建 generic lease、
取消/失败后仍有可达终结所有者、pending/semantic/fresh 全输入策略、overlay proof seal/替换单一协议、
异步差异仅留 provider access/completion**；C3 为 **获取释放持有、exact-version/fallback、cache/target 权威、
adapter/compat 旧包装退出、native fast-path 控制成本**；C4 为 **class delta/K²、增量 domain 准入、swap 前准入与纯 usage、
有限生产预算和 Debt 退出、长期集合寿命、真实 Store 的有限限额失败矩阵**；C5 为 **compact 权威、
单一转移语义且旧投影退出、descriptor/cleanup、逐重写范围生产净减、全配置证据一致**。
其中 C2 的“取消/失败终结”和 C4 的“有限生产预算/Debt”由同一复合 escrow/重试机制同时闭合；
表中仍按写入生命周期与预算生命周期分别计门，但不能解释成两份独立实现收益。

量化基线：PageStore `.h/.cpp` **33,551 → 26,759 行（-6,792，约 -20.2%）**；其中四个测试专属实现
迁移到 tests 的部分继续单列，不计删除收益。本批相对上一份 26,584 行记录是 **+175 行**：它来自可靠的多观察者
backing-domain journal、死锁隔离与 transfer owner 收口，明确记为协议成本，不冒充收敛删行。当前 CPU 配置 correctness
在 arm64 与 x86_64 均为 PageStore/Completion **1,000/1,000**；Clang 图
**1,381 APIs / 13,355 edges / 15 callbacks / 82 TUs** 且 gate 通过。新增的 API/边对应上述可达协议与新增控制/失败矩阵，
不能按删行收益解释。固定 K 曲线及 Vulkan foundation 双架构契约已建立，但活跃 Vulkan provider、完整吞吐和时延资格
仍不构成 BR1-PERF Pass。

第九批后、最终校验前的连续修改 checkpoint：生产 PageStore 目录 `.h/.cpp` 31,097 → 26,550（-4,547 行），
其中 `CpuSurfaceOps` 324 行、`Checkpoint` 473 行、`RandomAccessor` 374 行、`CpuAccessSession` 492 行
迁到测试支持库，**1,663 行是移动而非删除收益**；其余 2,884 行是生产目录内的真实净减。
合计起点 33,551 → 26,550（目录 -7,001 行，约 -20.9%，不等于全仓净减）。
语义 remove/alias 共用一次 staging、三个未决策输入/暴露枚举值退出；
Fresh-only selector 删除未生产调用的 semantic/pending 结果及参数，相关虚构断言从测试退出，真实 entry 寿命测试保留。
`CursorPage` 读复用已有 inline record，免除该路径的 vector/hash 分配与查找；不新增 session 对象字段。
captured generic 读直接把既有 view 传入统一获取流程，不再复制成第二份 Committed/Exact selector；
foreign owner 与 exact key 的拒绝改由共同流程和 captured resolver 保证。
Memento manager 的测试专属 `stats()`/`KisPageStoreHistoryStats` 退出；测试仍检查 retained snapshot 数量和
memento 恢复/清理行为，audit manifest 不再把该类型计入生产 runtime counter。
`WriteAdmission::m_conflicts/conflictsLocked()` 也只有一处测试读取、无生产诊断消费者；
删除计数状态与三条热冲突路径的写计数，测试保留实际 claim 拒绝/释放/再获取断言。
`cpuMutationStatistics()` 只是 `mutationStatistics()` 的 public 转发，返回值类型也只是同一统计结构的 alias；
测试调用迁到后者，删转发 API/类型别名，并把 store 内部计数器统一名为 `mutationStats`。
另查出 `KisPageStoreCpuSurfaceOps` 生产 `.h/.cpp` 合计 324 行，四个公开操作只有五个测试源文件直接调用；
backend 只留下一个未使用的 include，已删除。该类承载参考用例的矩形读写/填充/复制语义，现原样迁到
测试支持库，生产不再导出此未使用 adapter，五个测试目标继续链接该实现。
`KisPageStoreCheckpointCodec` 的 473 行同样只有 ReferenceTest 调用，也迁到同一测试支持库；其
capture/encode/decode/restore 参考覆盖保持。沿引用链确认 `KisPageStoreRandomAccessor` 374 行及其底层
`KisPageStoreCpuAccessSession` 492 行也只服务这些测试，没有真实生产调用；两者一并迁移，测试支持库
总计 1,661 行（源头 1,663 行，注释少两行），四项搬迁不计全仓删行。
真实 tiles3 路径仍使用生产 `KisPageStoreReadPage`/backend，未改其可见性和 writer unlock 边界；
C3.4 的其他兼容包装与回归尚未收口。
复核 C4.5 后没有直接删除防重放事实：两个 resident provider 共用的 `consumedOperations` 从会话永久 `QSet`
改为固定 4096-bit 滑动窗口和 high-water。窗口内允许跨线程/跨 provider 造成的乱序，已消费 ID 拒绝重放；
早于窗口的 ID fail-closed，跨度超过窗口时一次清空位图，不再随 session operation 总数增长。default read cache 仍受
64 entry/8 MiB 双上限约束，default preparations 受 64 entry 上限约束；HistoryCollector 的 pending/deferred key
集合至多每个已注册页一项，而持有 root reachability 副本的 active scan 现只填充 16 个 work slot，不再每轮为长历史
继续增加 scan cache。连同已有 1,024-unit metadata cleanup 上限和 memento 逐 token 终结，C4.5 源码责任闭合。
同批把 Store 私有的 `bind → verify terminal → release` 包装迁入唯一 operation owner `KisPageOwnerLedger`；
tile compatibility lease 的 `ownsTransaction/writeLeaseReady` 影子布尔也删除，分别由有效 transaction capability 和实际
writable lease 推导。在该 checkpoint，generic FreshCow transfer 仍在 Store 生命周期控制段，故 C2.8 当时保持未闭合，
不以方法搬家冒充收口；其后续闭合见本文第十批。
复核 C4 时发现 publication class-change 合并和 `prepareRetirementDebt` 仍按已累积 changes 线性去重，
与旧表的“K² 已退出”表述不符；现改为 backing key 索引，重复 effect 在两个入口各只分类一次。
operation-scope 写记录也由 `QHash<key, shared_ptr<record>>` 改为连续记录加 key→index，消除每页独立的
`shared_ptr` 分配；native cursor 仍不查索引，额外页触发容器搬移后，已返回的 provider byte span/oldData 仍有效。
metadata 的 verified last-use 原来单独导出全页 snapshot 再整页 assign，现复用局部投影/安装；
`AcquireRead/ReleaseRead/AttachHistoricalDefault/MaterializeDefault` 的 owner 路径也走相同安装语义。
AcquireRead 的跨历史 lease 冲突由 compact overflow 扫描提供 exact witness，最终拒绝仍由同一 StateMachine 判定；
历史占用 ID 的回归和 read/release/ack 的 `fullSnapshotExports` 不增长断言已加。
读释放时若 consumer last-use 已终态，但即刻 metadata acknowledge 未接受，现保留待确认记录供后续重试；
只有确认成功才删除，避免把失败当成终结。继续处理 generic release：provider access 只释放一次，
metadata `ReleaseRead` 若拒绝则由读服务保留 active record 与 completion，并在后续 release、last-use acknowledge、
close 的 owner gate 重试；close 不得将未终结记录视为空闲。request 留在 pending 计数、released lease 留在 active
计数、captured release 继续持有 retained root 和 owner lifetime，因而三者都不能被 close 误判为空闲；C3.1 的源码
持有/释放责任闭合。当时尚未执行的 arena 拒绝回归统一归入 C5.5，不再保留第二套读实现等待测试。
此更改不替代有限 Debt 失败矩阵。
native mutation 最后一个句柄析构时，取消失败的 Private 现交给 Store 的稀疏 orphan 表保留，原 transaction/page claim
及 owner 寿命不丢失；commit/abort/close 尝试重新取消，只有成功才销毁会话。捕获 overlay 的版本释放若部分拒绝，
读服务只记录失败版本并继续持有根快照与 Store 寿命；后续视图/snapshot 释放和 close 推进，成功终结后才释放根。
overlay 捕获失败的 rollback 也复用该终结路径。两处仅完成失败所有者接线，尚未做故障注入及完整回归，
不能将 C2.5 或有限 Debt 门标记闭合；C3.2 的 exact/captured/fallback 源码终结责任已经闭合，最终故障验证归 C5.5。
fallback 读 resolve 失败后再取消若被 metadata 拒绝，`KisReadRequest` 的取消意图也留在读服务内；
后续 acquire/close 重试，显式取消成功或 transaction abort 会清除稀疏重试 ID。调用方句柄消失不再是终结前提。
close 的 replica 枚举也改为从 compact metadata record 直接输出 handle，Store 保留原物理身份去重和退休规则；
不再为关闭构造含历史租约、last-use、view 等字段的全页 snapshot。此为源码接线，尚未验证关闭故障矩阵。
Debt 准入失败且即时 provider 退休未终态时，退休队列不再丢掉 record/operation：已登记 backing 保持原预算类别，
未登记但有预留凭据的 replica 保留凭据，二者进入由 process/close 等同步推进点处理的待重试队列；
未取得 Debt 的记录不进入后台 ready 队列。这修补终结持有者，不等于暴露前 escrow 已完成。
复核发现同步重试/close 仍可直接退休未获 Debt 的已登记 backing，可能在共享物理别名存活时留下错误类别 charge；
现把 Debt 准入设为 provider 退休的执行前提，失败只轮转同步队列。若首次重分类失败时携带预留凭据，
队列保留并优先复用该凭据；若共享 alias 实际需要别的 class delta，则再尝试正常准入，两者都失败才继续保留。
新共享 alias 抢占更高优先级类别时也用其预留完成物理
charge 转账；类别不变仍释放重复预留。在该 checkpoint 尚未验证有限预算及并发故障矩阵，C4.4 当时仍只局部。
首次退休和同步重试现在共用一个已登记 backing 的 Debt 准入动作；仅测试调用的第二个 backing-change
准备重载已删除，测试改用生产发布入口传空 retirement effects，不再维护复数 physical class delta 接口。
读侧 captured release 与 native 取消的可选 owner 锁也改为栈内持锁，避免两处控制对象堆分配。
Store 初始化剩余两处只需页存在/页头的 `pageSnapshot` 已改为单版本投影；当前生产 PageStore 不再直接调用全页
`pageSnapshot`，测试 oracle 保留，publication candidate/转移语义仍须单独收敛。
普通 commit 曾在历史版本数不超过 32 时另走 fused idle-history 转移，准备整页候选并替换所有版本记录；
超过 32 又退回局部 commit，形成两套提交/退休权威。现 Store 只选择普通 commit，退休交由同一 HistoryCollector；
元数据层的 fused 枚举、整页候选、替换式安装、`discardedVersions` 回传和专属计数已退出。
测试改为对照普通 commit 在 0/30/31/511 个历史版本下的局部输入与相同结果，并保留独立历史退休转移用例。
owner API 的非局部转移 fallback 原来直接调用整页 `applySequence`；参考用例已迁到 prepared publication，owner API
现在拒绝非局部类型，零引用的 `applySequence` 实现删除。测试独用的批量 `pageSnapshots` 也改由现有
`pageKeys`+单页 oracle 组合后退出，生产不再为该便利入口保留一次全量投影实现。
`activeMutationPages` 与 `activeCpuWritePages` 始终同值，前者只被测试读取；测试和 census 改用后者，退出重复统计字段。
`KisCpuMutationSession` 仅为 `KisPageMutationSession` 的旧同型别名；backend、CPU access 与测试统一使用后者，
删除该别名，不改变 native/generic 会话选择或生命周期。
prepared commit 的 `proofDescriptors` 校验后未再读取，整份 publication transition 在候选中只用于一次诊断计数，
候选内的 proof 副本又与调用者受保护的 `preparedPages.proofs` 同值；现删除这三份候选侧表，转移计数留在局部，
转移输入在元数据候选准备后于 owner 锁外释放。removal/restore-default 的平行 version/descriptor 向量合为成对记录，
default/removal/restore 最终共用候选中的一份 descriptor 安装表，安装计数直接取其长度；
仅用于生成 ReplaceDefaultPixel 转移的 replica 不再保存在 descriptor 候选里。
输入预检改为在 owner 锁内借用既有 transaction state，不再复制三个容器并持有到函数结束；
proof descriptor 暂存也在 provider 校验后释放。
prepared commit 中另删除与 commit/restore 两个互斥 epoch capability 重复的 `restoration` 布尔值；
有效性现要求恰好一个 capability 有效，安装分支直接由有效 capability 决定，避免状态和实际资源分叉。
候选中仅供弱容量断言使用的 `descriptorCapacity` 也已删除：它不拥有 QHash 预留且不能证明剩余槽位，
真实约束仍是准备期 reserve、descriptor revision 复验和 owner 锁内安装。metadata 安装拒绝直接由 epoch
install 的 `Rejected/Conflict/Committed` 结果区分，不再另写 `metadataRejected` 影子布尔值。
commit preparation claim 在 owner 锁内冻结 transaction proof/removal/surface 输入；解锁准备后的 metadata revision、
page directory、descriptor revision 和 epoch root 均在安装前复验，安装仍在 owner 锁内消费已预留容量。
deferred metadata cleanup 的后台待处理量新增固定 **1,024 page-unit** 上限，单 unit 内部记录受 metadata arena
预算约束；超限候选在 owner 锁外同步销毁，不创建额外失败出口或无限排队。由此 C5.3 的 descriptor/cleanup
源码责任闭合；按用户要求未运行的并发/故障回归归入最终 C5.5 一致性验证，不倒退为第二套实现。
Memento manager 的 `completing/restoring` 只在持有同一 mutex 的方法内部读写，无法成为其他调用可观察的
并发状态，已退出；`operational/sharedRetention` 分别由 store 指针和相同 token 判断，不再长期双写。
`purge/close` 共用逐 token 的释放并在每次成功后撤销记录中的 token；`abort/close` 共用 active transaction
终结清理，若 abort 已成功但 retention 释放失败，重试不会再 abort，同理第二份 retention 失败不会重放第一份释放。
commit 已发布但 after-root 留存失败时，active 记录标记事务已终结并保留可能取得的 after token 供 abort/close 清理；
这只修补失败后的持有者与幂等重试，不证明留存失败时 undo 语义可恢复或整个 C4/C5 生命周期闭合。
当前 selector 已重新接入 `SemanticOnly/ReusePending`，但不恢复空占位：同一 entry 是否已有 prepared target
直接决定两者，stage semantic 据此处理 pending reset，alias prepare 据此唯一选择 Adopt/Replace transition；
MutableGuard 的 payload/discard/COW 仍由同一 selector 决定。两处原先各自以 cold Page 是否存在猜策略的判断退出，
故 C2.6 按当前 Fresh 范围闭合；未来 M6 handoff 必须再扩展同一 selector，不能建立第二权威。
仅测试使用的 `KisCpuWriteGuard::baseVersion()` 及 entry 转发 accessor 已删除；测试 helper 从其已经持有的 exact
before read 取得 base identity，不减少 before/oldData 语义覆盖。
截至该段尚未运行构建/测试/源码门；旧 reverse-callgraph 与当时源码不匹配，
须待允许校验时重新生成，因而不把旧图当作 C5.1/C5.2 证据；两门随后由当前源码 caller 全量核对和旧实现物理删除闭合。
继续沿真实 tiles3 写入口核对到一个不可达旧协议：`KisTiles3PageReplicaProvider` 的 capability 固定声明
`nativeCpuMutation=true`，但 backend 的单 tile 写仍在条件分支后保留 generic `KisWriteLease` 回退。现已删除该
constructor/字段/finish/cancel 分支、`GenericWrite` census 类别和 adapter-only `acquireWriteFromLegacy`；普通
`KisPageStore::acquireWrite` 直接拥有通用异步写实现，不再经带 reservation 可选参数的第二入口。
backend 的 CPU batch 和 range operation 也不再重复查询固定 capability。此项净删 127 行，真实 tiles3 写只剩
native mutation 终结权威；generic read 冷页回退和其余 tile ABI 包装仍存在，所以 C3.4 仍为局部。
继续沿测试根审计发现完整 `KisPageStoreCompatibilityCensus` 只有一个 tiles3 测试读取，却在 lease 构造/终结、
anonymous transaction、writer claim/wait、iterator probe 和 tile refresh 的生产路径反复锁 backend mutex 写计数。
这不是 owner 状态，也不参与 close/失败恢复；真实事实已有 WriteAdmission、Mutation/Store capability snapshot、
RAII lease/transaction/registry 持有。现删除 census 类型/API/字段/记录回调，连同只为计数穿透的 waits/newly-claimed
输出和两个纯计数 release guard；测试保留实际读、写、拒绝和跨线程 boundary 行为并改名为
`testPageStoreCompatibilityBehavior`。intrusion manifest/runtime census 对仍存 adapter 如实改为 static-only 或映射
canonical Store/Mutation 统计，不能把这次计数退出误写成 R4 adapter 已删除。固定 read cursor 的 `cachedPages()`
也只有测试读取；容量由 `std::array<Entry,4>` 本身保证，200 页轮转和 peer 独立读取仍保留，因此该测试 accessor 同批退出。
ReadCoordinator 的三处 `ReleaseRead` 和两处 captured-version release 构造归到各自一个内部入口，失败重试 owner/队列不删；
RetirementQueue 仅转发到四参数实现的公开重载也退出。本段使 PageStore 目录再净减 309 行，仍未运行构建或测试。
继续按 68 的最终类型/API 对照，Store 两个 `beginCpuMutation()`、session `enableCpuWrites()` 与 backend
`beginCpuMutationBatch()` 均已删除；生产、tiles3 和测试 caller 只创建 canonical `beginMutation()`。
唯一 CPU provider 在首次像素操作的 claim/allocation 之前选择，纯语义 delta 不依赖该 capability；测试 adapter 仅允许
这种零副作用 preflight 拒绝选择 generic route，真实 native 失败不重放。固定 read page 的未调用 `byteSize()` 出口删除。
随后 tiles3 删除裸 transaction batch、逐页 replacement mutation 和 legacy removal bypass，full-tile alias/removal 与像素写统一进入
canonical mutation batch；单页 lease 直接取得 session claim，不再经独立 reservation 搬运。Admission 删除重复 `ClaimKind`、
write-set 影子计数和零 caller 的内部等待分支，真实冲突等待只保留在 adapter preflight。tile lease wrapper 按值持有 move-only
capability，不再为每次读写额外分配 1–2 个管理对象。本段把本批净减扩大为 638 行；仍未运行构建、测试或重新生成调用图。
随后按 production caller 复查 metadata 转移，确认公开 `KisPageMetadataCoordinator::apply()` 仅被 ReferenceTest
调用，却仍执行完整 page snapshot、StateMachine 和整页 assign，是 compact record 之外真实存在的第二套写回实现。
现将本地 read/write/capture/abort/handoff 测试改走 coordinator 内已有的 projected owner 路径；非局部 commit 测试改走
prepared publication。旧 `apply()` 及其全页写回实现删除，测试的全页 `pageSnapshot` 只保留为只读 reference oracle。
生产转移现只有两类：局部/已验证 completion 使用 `applyProjectedSequence`，commit/restore/mutation batch 使用同一
prepared publication prepare/install；两者共享 `KisPageStateMachine` 语义而不共享错误的生命周期边界。
继续追到 Store 读请求和默认页准备的入口：原本合计五处 `pageSnapshot` 只用于判断一个 exact version，
已换成 `versionSnapshot` 的页头+单版本投影。共用投影函数把 mutation-base 计量仅留给真正的 mutation，
默认/历史读的获取与物化回归确认不导出全页 snapshot、也不污染 mutation-base 输入数。
同步 `HistoryCollector::collectBatchLocked` 已从全页 snapshot 改为只枚举页键、按页每次最多 32 个
Historical 版本的切片扫描与安装；同步与后台路径共用一次退休资格判断，root 可达性仍由 epoch 模型统一计算。
默认/历史读回归增加释放后的断言：前台全页 snapshot 不增长、切片最大输入不超过 32。
受限 transient backing 准入也已从整页 snapshot 改为页内 mutable 计数、exact target lookup 和 Retiring 记录扫描；
已注册页的上限拒绝、已有 Prepared target 例外回归验证均没有增加 full-snapshot 导出。不过同步一批的总历史遍历、reachability 集合与
retirement effects 仍未总量限额化，受限准入的 Retiring 检查仍可扫描 H，故 C3/C5 不闭合。
owner ledger 的共享物理 backing 在代表副本退休时原来遍历所有逻辑 backing 找替代者；
现只为真正共享的物理 backing 建成员索引，单成员时移除索引，代表替换只访问同物理成员。
这是有界于存活 alias 数的定位索引，换取退休时不扫描无关 N；不替代每次 reserve 的全域 domain 同步。
原有 alias 回归扩为三个共享逻辑 backing，再依次覆盖/退休两个成员，四种像素宽度下仍确认剩余别名和物理用量正确。
此扫描仍随 H 增长，**没有**关闭 C3.5 的固定 K/H 工作量门，也没有把测试用 full-snapshot oracle 删除。
上述变更不关闭 C2 三入口策略门，也不证明 C3 全链路性能。完整验证与证据仍在形成中。

上一个已校验源码节点的边界（不覆盖随后未验证的读释放重试修改）：受影响的 9 个构建目标成功，七套 PageStore/Completion ctest、Painter **99**、
tiles3 **334**（seed 12345）通过；
Clang 图更新为 **1,517 APIs / 13,516 edges / 13 callbacks / 83 TUs**，物理 gate **0/20**、
源码 checkpoint/architecture gate 与 6 个 reachability 自测通过。全仓构建未完成，
不能把目标构建称为“universal build”；最终 manifest 与性能资格仍待闭合。

继续按字段/函数引用图清理后，测试便利的 epoch `std::function` 安装重载、无消费者观察器、累计后无人读取的
history-version 统计、write admission/owner ledger 影子计数及若干纯转发 reservation/release 接口退出；generic read
获取已统一由 `KisPageStoreReadPage` 持有 exact view 与唯一释放协议。commit/restore 不再各自维护 root 槽取消和安装逻辑，
共用 move-only root reservation 与 `installReservedRoot`；单值 `KisPageTransitionEffectKind` 及三个永真消费者分支也已删除。
iterator write boundary 改为 context/function-pointer，backend 内部 CPU operation 改为模板，不再叠加第二层类型擦除。
继续按 68 的 physical owner/binding 设计核对后，上层按引用计数授权 exclusive 的整条链、binding 内完整
`KisReplicaHandle`/内部引用出口、Tiles3 的 `activeAccesses/activeWriter` 影子状态均已退出；真实 binding
read/write pin 和 provider allocation gate 保留。两个 provider 各自的 exact allocation 身份判断收敛为一处，tile
bridge 选择、读 cache 替换、lease 终结及 data-manager index refresh 也分别只剩一个实现。native seal/cancel 在原遍历中
汇总 page/source/removal 数量并合并互斥 detach，删除多次 K 扫描；这不实现或授权 M6/M7 retag/handoff。
PublicationCoordinator 的 proofs/surface/removal 三次查表复制改为单次 transaction delta snapshot；proof 九字段相等语义
归回值类型，PageState/Version 的 exact version/replica/published 定位归回 snapshot 值类型，删除四个文件中的重复 helper。
StateMachine 的 version/operation/lease 去重和 metadata batch physical-slot 去重从 K² 改为临时集合；commit 的
surface-change/proof key 索引在一次事务内复用，删除 registered page 与 change/proof 的嵌套扫描。retirement 对 backing
存在/类别的两次 ledger 查询合成单一类别查询，close 直接移动退休记录而不复制整批 capability。
随后继续清理活路径复数权威：arena/index 的相同 reservation 合为一份内部 move-only 模板；CPU/tiles3
generic CPU access 的 binding pin 与 access 投影共用同一实现；completion source 删除无人读取的名称及四布尔 one-hot
descriptor，直接以 `KisCompletionDomain` 注册；provider 的失败 operation 构造也收为类型上的单一工厂。
写请求、archive 请求、resident binding writer 与 metadata slot 的互斥布尔组合分别改为单一状态枚举；memento active
record 以 transaction capability 有效性替代 `transactionClosed` 影子状态。上述改动不关闭 C2.8/C4.2/C4.5，
只减少重复状态和实现。
后续引用图继续收敛长寿命状态：iterator cache 有效性由当前 pin 推导，history reachability 总数改为冷快照求和；
write batch/lease 的终态由资源 owner 指针表达，mutation session 的互斥布尔改为单一状态；CPU/tiles3 provider
活动 lease 只保留 allocation token，并由 allocation 表复验完整外部 capability。Tiles3 物理字节数由唯一 tile
payload 推导，SSD operational 由 swap store 推导，OwnerLedger/EpochModel/PageStore 的 configured/operational
影子位分别由其唯一资源/root 推导。iterator scope 的 same-view、before-alias、live-writer 三个位改由成功持有的
view 拓扑表达，捕获失败先清空 owner 标记以保持 fail-closed；active generic write 只保存 finish/abort 所需 closure，
不再复制 pending-only 的 access/readiness 状态。PageStore 也不再整份保留 EpochModel 已持有的 initial snapshot，
finalize 冷路径从唯一 root 导出 manifest；完成区间的单项状态 cache 与匿名 transaction 已清空后的重复清理退出。
校验前的收敛 checkpoint 为 29,168 → 26,550，净减 2,618 行（约 -9.0%）；该节点尚未运行构建、测试或调用图生成。
相对上次 26,543 行记录净增 7 行：类型/字段截肢被 C4.5 必需的固定 replay window、history scan 硬上限和
OwnerLedger 唯一 terminal-operation 消费原语抵消；该 7 行不计作删行收益，也不影响各归档重写范围仍为净减。

### 当前编译、回归、调用图与门重评估（2026-09-24）

- 当前源码的九个受影响目标在同一 `_build-br0-cpu` 配置完成 universal 构建；七套 PageStore/Completion
  已分别以 arm64 与 `arch -x86_64` 实际运行，不再以 fat binary 代替跨架构运行证据。
- 两个架构的 PageStore/Completion 都是 **7/7、1,000/1,000**：Foundation 28、Completion 11、Reference 297、
  ReadBaseline 45、ResidentRead 33、CpuMutation 572、PhysicalClaim 14。新增 5 项来自固定 K 控制曲线四行和真实
  Store 有限失败矩阵一行；没有删除旧行来改善结果。
- 校验实际发现并修正三类偏差：旧测试仍期待被截肢前的 writer/diagnostic 文案；byte-identical packed write 的
  no-op 不应创建 session；一页 Debt 上限时，close 原先先枚举当前 live replica、后处理已占 Debt 的旧退休记录，
  会让当前退休被无谓拒绝。close 现先消费已排队 Debt，再处理本轮 live replica，定向竞争用例连续复验通过。
- fresh Clang 图为 **1,381 APIs / 13,355 call edges / 15 callback registrations / 82 TUs**，无 unresolved edge；
  reachability 分类为 production-boundary 950、indirect-review 249、test-only-review 139、unreached-review 43。
  后两类仍只是人工裁决候选，图明确不授权自动删除。物理写 reservation 的真实调用者为 production/test **1/6**，
  取代已失真的旧 `0/20` 统计。
- architecture gate 在刷新源码 checkpoint 前只报告 12 个预期修改文件的 stale hash、没有侵入或 ownership 违规；
  经人工复核后刷新，并再次通过：21 项 manifest、18 项 ownership fact、16 组 runtime census、19 个冻结的外部侵入文件。
  三处主干 PageStore 标识计数相对旧 checkpoint 增加：`kis_tile.h` 3→6、`kis_tiled_data_manager.cc` 19→21、
  `kis_tiled_data_manager.h` 7→10；direct include 未增长。它们分别对应按值 move-only lease capability、固定 read-view
  和 canonical operation value type，不增加 PageStore owner/生命周期状态。该例外已在 manifest 登记路径、精确上限和理由，
  新 baseline 从现值继续禁止增长，不能用刷新 checkpoint 静默抹去。
- `reserveBacking()` 现在在 provider 物理分配前一次预留目标 class 与同尺寸 `RetirementDebt`，
  `registerBacking()` 安装目标 charge 后继续持有 Debt fallback，直至退休/取消终结。有限一页 Debt 的 generic 三终态、
  native/generic/sealed-proof 部分取消、拒绝退休、drain/close 均通过，因此 C2.5 与 C4.4 闭合。
  当前矩阵又覆盖 Current/Pending/OptionalCache/SSD 拒绝与重试，结合既有 Debt/drain/close 后 C4.6 闭合。
  双架构 CPU 正确性已一致；Vulkan foundation 配置随后也完成双架构构建/运行，但 provider 按 BR1 设计仍 fail-closed，
  完整非 CPU 执行和性能资格仍使 C5.5 保持局部。

代码量收敛与架构门采用两套计数，避免把删行误报为协议闭合，也避免把未变化的门数误解为没有进展：

| 口径 | 起点 | 当前 | 变化 | 判定 |
|---|---:|---:|---:|---|
| PageStore 全收敛范围 | 33,551 | 26,759 | -6,792 | 生产目录体积下降约 20.2%；本批协议补全 +175 行单列，不记作删行收益 |
| 第九批后连续修改 | 31,097 | 26,759 | -4,338 | 扣除 1,663 行迁移后，原位净减 2,675 |
| 当前强化收敛批 | 29,168 | 26,759 | -2,409 | 目录体积下降约 8.3% |
| C2–C5 架构门 | 24 | 21 闭合 / 3 局部 / 0 未闭合 | C2.8、C3.5、C4.2、C4.6 闭合 | 仅 C3.4、C4.3、C5.5 保持局部；不存在未闭合门 |

归档范围净减不是用门数倒推，而是用第九批归档的
[`before-source.tar.gz`](../../../evidence/br1_convergence_c9_20260923/before-source.tar.gz) 与当前生产目录执行
`git diff --no-index --no-renames --numstat`，再按互斥文件责任归组。下表保留校验前 checkpoint 的
31,093 → 26,550（-4,543）结果；当前为 26,759，比该 checkpoint 增 209 行，但即使保守地全部计入净减最小的
provider/budget/retirement 范围，也不足以反转任何互斥范围的净减结论。
其中四个迁移文件在该基线占 1,633 行并单列，不冒充删除收益。其余生产源码净减 2,910 行，分组如下：

| 互斥生产范围 | 新增 | 删除 | 净变化 | 覆盖责任 |
|---|---:|---:|---:|---|
| Store/read/write 协议核心 | 1,463 | 2,001 | -538 | Store、读写协调器、iterator read scope、公共 types/write operation |
| Metadata/publication | 1,477 | 2,642 | -1,165 | metadata/index/reservation、state machine、publication、epoch/history/memento/completion |
| Provider/budget/retirement | 980 | 1,477 | -497 | owner ledger、CPU/Tiles3/SSD provider、resident binding、retirement/default storage |
| Backend/integration | 352 | 1,062 | -710 | tiled backend、service/registry、diagnostics/reclamation |
| 迁到 tests（不计删除收益） | 0 | 1,633 | -1,633 | CpuSurfaceOps、Checkpoint、RandomAccessor、CpuAccessSession |

四个生产重写范围均为净减，且和迁移项无重叠，故 C5.4 由“局部”改为“闭合”。这只关闭源码净减门；
当前 CPU 双架构回归和 Vulkan foundation 双架构契约虽已通过，活跃 Vulkan provider 路径与性能资格仍归 C5.5，
不由该表推导。

逐门状态（`闭合` 只表示对应门，不表示所在阶段完成）：

| 门 | 状态 | 当前判据/下一证据 |
|---|---|---|
| C2.1 base/descriptor 单一准备 | 闭合 | native/generic 共用 `prepareWriteBaseLocked`；默认及 removal 复验在同一处。 |
| C2.2 entry 唯一私有寿命 | 闭合 | guard/alias/removal 共用 entry；cold Page 仅存资源。 |
| C2.3 Fresh provider 策略 | 闭合 | 两入口调用 `prepareFreshReplica`；当前 selector 明确只处理 Fresh。 |
| C2.4 同步 CPU 无 generic lease | 闭合 | native session 不创建 generic write request/lease。 |
| C2.5 失败后终结所有者 | 闭合 | generic request/lease、native orphan、captured release 各由唯一 owner 保留到真实终态；一页有限 Debt 下三种 generic 终态和 native/generic/sealed-proof 部分取消均可 drain 后重试，close 先消费旧 Debt 再处理 live replica。 |
| C2.6 pending/semantic/fresh 策略 | 闭合 | selector 由 entry prepared target 决定 `SemanticOnly/ReusePending`，并驱动 staging 与 Adopt/Replace；payload/discard/COW 继续走同一 selector，不保留第二套 page-presence 策略。 |
| C2.7 overlay seal/替换 | 闭合 | native/generic 共用 `sealPreparedPage`和旧 proof Historical 寿命；native 多页、generic finish、page removal、abort/commit 的 map-owned proof 撤销/安装统一由 PublicationCoordinator 执行，多页仅保留必要的 metadata 原子批次差异。 |
| C2.8 异步仅在 provider access/completion | 闭合 | `WriteCoordinator::initializeFreshReplica` 独占 FreshCow 判定、source provider 解析、bridge 选择、transfer request 以及 terminal provider operation 的校验/消费；Store 只接收 allocation readiness 并保留生命周期复验/安装，不再含 FreshCow 分支或 transfer 终态语义。 |
| C3.1 读获取/释放持有 | 闭合 | `KisPageStoreReadPage` 共用 native/fallback；provider access 只释放一次，metadata release 拒绝后 active record 保留 completion 并由 release/ack/close 推进，失败记录继续进入 close 能力计数。 |
| C3.2 exact-version/fallback | 闭合 | 已删 captured→selector 重编码；Store exact read 与默认物化改单版本投影；捕获版本部分释放及 fallback cancel 拒绝均由读协调器保留 exact 身份、root/owner lifetime 并重试。 |
| C3.3 cache/target 权威 | 闭合 | hline/vline/random 的 PageStore 只读路径只构造固定 4-slot cursor，不分配 legacy tile cache；可写路径不构造 cursor，tile cache 的 mutable target 与 exact before 分责；operation-scope 写记录也已消除每页 shared_ptr。 |
| C3.4 adapter/compat 退出 | 局部 | 四个测试专属 wrapper 共 1,663 行已迁出生产；tiles3 不可达 generic-write 分支、旧 mutation factory、裸 transaction batch、逐页 replacement/removal 旁路均已退出，tile lease capability 已改为零额外管理对象分配；generic read 与真实 tile lease/iterator ABI 包装仍保留。 |
| C3.5 native 控制成本 | 闭合 | CPU guard 控制曲线覆盖 N16/N1024、K1/K16、H0/H32；每轮 page resolution 严格等于 completed×K，generic request/default materialization/metadata transition 均为 0，binding、snapshot export、version input 不随 N/H 增长。100 ms 样本中 N1024/K1/H0、H32 分别完成 2,101,184、2,061,008 次，N1024/K16/H32 完成 115,504 轮（1,848,064 页解析）。该门约束控制工作量，不代替吞吐资格。 |
| C4.1 class delta/K² | 闭合 | 共用 physical class delta；retirement effect、StateMachine identity/lease 与 metadata batch physical-slot 去重均使用临时索引，commit 的 surface/proof 查找不再按 registered page 嵌套扫描。 |
| C4.2 增量 domain 准入 | 闭合 | provider 暴露按序号确认的 coalesced physical-slot domain journal；Tiles3 只为 PageStore-owned payload 登记稀疏多观察者，首次物理 retain 登记、最后一次 release 注销。`synchronizeBackingDomains` 只遍历 P 个 provider 与 K 个变更并按精确 sequence ack，不再扫描 N 个 physical backing。 |
| C4.3 swap 前准入/纯 usage | 局部 | `backingUsage()` 保持纯观察器；swap-out/swap-in 在 tile storage 锁释放后可靠发布 Ssd/CpuRam 序列变更，别名、多 provider 与回调锁顺序已覆盖。但域实际变更仍先发生、后由 Store admission 同步，尚未形成 swap 前预留/拒绝协议。 |
| C4.4 有限生产预算/Debt 退出 | 闭合 | 真实 Store 可配置有限限额；fresh backing 在 provider 暴露前复合预留目标 class 与同尺寸 Debt，登记后保留 Debt fallback 到终结。有限 Debt 的取消、拒绝退休、重试、drain/close 回归通过。 |
| C4.5 长期集合寿命 | 闭合 | provider 防重放改为固定 4096-bit 滑动窗口，窗口外旧 ID fail-closed；default cache/preparation 分别受 64 entry、8 MiB/64 entry 限制；history pending/deferred 按 PageKey 去重，持有 reachability 副本的 active scan 只填满 16 个 work slot；metadata cleanup 仍有 1,024 unit 上限。 |
| C4.6 真实 Store 失败矩阵 | 闭合 | 新增真实 Store 有限矩阵：Current 两页原子拒绝、Pending 第二请求拒绝、OptionalCache 分配拒绝、Tiles3 Ssd/durable 零上限拒绝及 swap-in 后重试；结合既有 Debt、部分取消、拒绝退休、drain/close 用例覆盖五类预算与终结。 |
| C5.1 compact 权威 | 闭合 | 生产 Store 无 `pageSnapshot` caller；read/default/transient/GC/shutdown/publication 均读取 compact record 的有界投影或 header，完整 snapshot 只作注册边界与只读 reference oracle。 |
| C5.2 转移语义与旧投影退出 | 闭合 | 所有生产 owner 转移走 `applyProjectedSequence`，commit/restore/mutation batch 走 prepared publication；二者共用 StateMachine，旧公开全页 `apply`/整页 assign 转移实现已删，fused commit 双权威也已退出。 |
| C5.3 descriptor/cleanup | 闭合 | 候选重复侧表/影子状态已删，三种 descriptor 安装共用单表；commit claim 与 revision/root 复验覆盖解锁准备，后台 cleanup 固定上限 1,024 unit，溢出在 owner 锁外同步销毁。 |
| C5.4 逐重写范围生产净减 | 闭合 | 当前连续修改 PageStore 目录 -4,338，其中 1,663 行仅迁到 tests，实际原位净减 2,675；强化收敛批净减 2,409 行。第九批归档到校验前 checkpoint 的四个互斥生产范围分别净减 538/1,165/497/710 行；当前相对 checkpoint 的 +209 行不足以反转任一范围，本批 +175 行协议成本未冒充净减。 |
| C5.5 全配置一致 | 局部 | fresh graph/checkpoint/gate 一致；七套 PageStore/Completion 在 arm64 与 x86_64 均为 1,000/1,000，Vulkan foundation contract 双架构各 14/14。构建发现的旧 `isKnownSource` 侵入已改为 canonical ticket `status != Unknown` 校验而未恢复兼容 API。活跃 Vulkan provider 仍按 BR1 fail-closed，且缺完整性能资格，不能闭合。 |

## 4. 验证

先完成所选范围，再验证最终版本，不逐小改动做整轮吞吐实验。
覆盖 remove→write、alias→write、default revision、captured before、cancel/retry、线程竞争、last-use/close；
在 provider/proof/metadata 拒绝及有限 Current/Pending/Debt/cache/SSD 限额下检查终结。
K1/K16/大 K、固定 K 增长 N/H，记录 allocation/copy/scan/claim/terminal 工作；QtTest 耗时不作性能资格。
每次新增抽象明确同时退出的状态/分支/API。用户未提交修改保留，未完成项如实登记。

## 5. 执行记录

### 2026-09-23：首批实际删除与合并

- C0：源码集合/内容、编译数据库和审计输入指纹已接线。旧 M5B 证据被拒绝；删除前重新生成的图为
  1,614 APIs / 13,683 edges / 14 callbacks / 85 TUs，gate 通过。刷新 source checkpoint 前必须先通过旧侵入上限，
  不能借 `--write-baseline` 自动抬高上限。固定起点另存 `pagestore-audit/convergence-start-source.json`。
  删除相关的原始 caller/override 子集及完整旧图摘要保存在 `convergence-retired-protocol-proof.json`，不充当当前 gate 图。
- C1：删除完整 seed/host adoption 协议，包括 Store public/private 入口、provider virtual/实现、PageKey mailbox、
  析构清理和六个专属诊断 phase。旧链仅有测试外部调用；production 边只在旧 wrapper/impl 之间。
  removal/default revision、并发排他、mutable 独立字节、预算失败后重试、physical alias 引用测试迁到显式 source/alias。
  五组定向测试（含数据行）通过，没有以删除测试换取删除代码。
- C1 补充：删除没有调用者的 backend 独立 `replaceFullTile` 包装、provider `tileDataForLeasedReplica`，
  以及 session `pageFor` 的未用 const 重载。batch 的实际整页替换、source/alias、lease 查找路径保留。
- C2 局部：`KisPageStoreManagedRange` / `KisPageStoreLegacyPage` 合并为 `KisPageStoreWriteReservation`；
  两份相同的 mutation adopt 实现合并为 `adoptReservation`。managed/legacy 的不同等待、origin 与 generic 转交语义不合并。
- C4 局部：publication/retirement 的物理分类安装共用一份实现；class delta 重复项检查从 K² 扫描改为临时哈希集合，
  预检平均 O(K)，不新增长期权威容器。增加重复项拒绝且预算不变的断言。

本批生产 `.h/.cpp` 新增 69 / 删除 592，净减 **523 行**，pagestore 合计 33,551 → **33,028**。
Store.cpp 4,654 → 4,381，Store.h 613 → 573。三个测试文件新增 57 / 删除 45，净增 12；
两个审计脚本新增 68 / 删除 2，净增 66。文档和生成证据单列，不抵扣生产净减少；没有新增生产文件。

验证见 [本批证据](../../../evidence/br1_convergence_c1_20260923/README.md)：

- 当前构建成功；六项 PageStore + Completion 共七个 ctest 通过（912 QtTest totals），无 SAFE ASSERT。
- Painter 完整套件配置正确资源/插件目录后 99 passed、无 SAFE ASSERT；未配置时在正文之前发生 bundle 路径启动失败。
- tiles3 完整套件报告 334 passed，但日志有 1,984 条 SAFE ASSERT，**不算验收通过**。
  独立 stress 重跑也复现 history commit 拒绝，超过 2,000 条 warning 上限；完整运行还出现 exact-generation 无有效 replica。
  根因及是否本批引入尚未确认，不因 QtTest exit 0 抹去此问题，也不回退压力用例。
- 当前重新生成的图：1,604 APIs / 13,559 edges / 14 callbacks / 85 TUs；physical gate 仍为 production/test 0/20。
  源码 checkpoint 与 architecture gate 一致。旧源码 hash、源码集合变化、旧 generator hash、缺失输入指纹、
  旧 source checkpoint、超旧侵入上限六种负例均被拒绝。

以上不声称 C2/C4 已完成或获得吞吐提升。首批实际删改保留；全量回归缺口与后续协议收敛一起跟进。

### 2026-09-23：第二批共享终结与失败出口收敛

- generic `publish/cancel(lease)` 共用 `finishWrite`，删除重复的 completion、transition、proof 替换与退休分支。
  begin/publish 使用原子的 metadata sequence；provider 验证放在 owner gate 外，页 admission 与 preparation claim
  保持到终结。失败取消不再先删唯一 active record；已消费 access 的记录由事务 abort 重试，仍暴露的 lease 拒绝 abort。
- native、generic request 和失败 lease 的私有取消共用 `WriteCoordinator::cancelPrivateWrite`。
  从 metadata 的真实 publication 状态选择 CancelWrite/AbortPreparedVersion，删除 cold Page 的 `published` 布尔权威。
  generic prepare 三个失败出口共用清理，detach 被 Debt 预算拒绝时保留 abort 可到达的 request/claim。
- native 批量取消逐个退出已成功的 cold slot；部分失败也执行已产生的退休 effects，重试不再二次取消已删除版本。
  transaction abort 同样在全部退出路径归还已接受的 effects，并在解锁清理期间保留 preparation claim。
- 新有限 Debt 用例暴露了旧整事务 abort 绕过局部预算准入的问题：`AbortTransaction` 现接入已有 indexed prepared
  选择与 `applyOwnerSequence`，不再回落到全页 `applySequence`。取消/无效 completion/proof 拒绝后三类 consumed lease，
  以及 native/request/sealed proof 三类部分取消，均覆盖预算拒绝→drain→abort/cancel 重试→close。
- 首批 stress 告警定位为 `preparePublication` 的 revision 冲突：后台回收或读保护变更可在准备存储/容量时使候选失效，
  旧循环仅在安装阶段重试。候选现明确返回 retryable 冲突，commit/restore 共用既有重准备循环；预算耗尽、身份错误
  不改为盲重试。新增 16 页、64 轮并发 captured reader/commit/restore 回归，stress 的 SAFE ASSERT 改为真正测试失败。
  定位用临时日志已移除；保留 DataManager history commit 失败原因输出。此修复不声称覆盖所有并发交错。

本批生产 `.h/.cpp` 新增 189 / 删除 265，净减 **76 行**（pagestore 净减 78，业务错误信息净增 2）；
两个测试文件净增 134 行，新增 7 个数据行/用例；没有新增生产文件。pagestore 33,028 → **32,950**，
Store.cpp 4,381 → 4,266。两批生产累计净减 **599 行**；不把测试、文档、生成证据计为生产收益。

验证见 [第二批证据](../../../evidence/br1_convergence_c2_20260923/README.md)：

- 最终构建成功；七个 PageStore/Completion ctest 全过，QtTest totals 919；Painter 99；tiles3 完整套件 334。
  全部上述日志均无 FAIL/SAFE ASSERT。独立 seed 12345 / 8 线程 stress 也通过；非吞吐配对实验。
- 新定向回归 7 行/用例通过（含 init/cleanup totals 9）。有限 Debt 的首次失败是测试发现预算路径分叉，不是放宽断言。
- 当前图重新生成：1,610 APIs / 13,662 edges / 14 callbacks / 85 TUs；physical gate production/test 仍为 0/20。
  source checkpoint 通过旧侵入上限后刷新；architecture gate 通过。固定 convergence 起点及首批证据未刷新。

### 2026-09-23：第三批写入基准与默认页准备收敛

- native、generic 和 alias 三条入口共用现有 `WriteCoordinator::prepareWriteBaseLocked`，集中 exact base、sealed proof、
  removal/default descriptor、generation 和 operation/writer 身份的准备。删除三份对应分支和 `latestPreparedVersion`。
  resolver 只认 publication 中已 seal 的 proof 或正在替换的精确 private base，不把任意 Prepared 版本当作可见 overlay。
- generic 从全页 snapshot/历史遍历迁到现有 `mutationBaseSnapshot(base, sealed)`；正常已登记页只投影最多两个版本。
  在保留 H=0/7/63、bpp=1/4/8/16 的用例中增加 generic prepare：exact version 输入增量 ≤2、无前台全页导出，
  且写入确实延续已 seal 的像素；不是仅检查查询次数而忽略可见性。
- generic 写虚拟默认页不再调用 `ensureDefaultPageLocked` 先分配 before-image；与 native 一样只初始化目标页。
  native/generic 共享 `preparePrivateWrite` 的默认源复验：provider 解锁执行期间若读者物化默认页，取得实际 authority pin。
  同步 native 仍原子 Acquire/Prepare，generic 保留异步 transfer/completion 边界，没有强迫 native 生成 request/lease。
- 虚拟默认版本登记移到已有 PublicationCoordinator，并改用单版本查询。首次访问来自旧事务时先按当前 root 登记
  Published head，再附加旧 Historical default，防止把旧 revision 误标为当前 head 而绕过写冲突。
  native/generic/alias 三条新回归确认旧写拒绝、无残留 target/claim、abort 后当前默认像素不变；没有放宽 StateMachine。
- 类型对照：沿用 68 的 store 内嵌非拥有 coordinator、intent 和临时 transition，未添加持久 map、owner、entry 字段或新类型。
  本批不是完整 `prepareEntry/prepareSeal` 落地；provider allocation/access 及 pending/semantic 策略后续仍需合并。
  普通已有版本继续从精确 descriptor 查询，不能要求所有历史显式 manifest 都有新 surface 元数据。
- 测试迁移保留全部旧语义断言；两处并发注入从已删除的 default-before `requestReplica` 移至实际 `prepareWrite`，
  对应检查已存在的 provisional request。扩展 native/generic 默认页和读者并发物化覆盖，不删除失败用例换取通过。

本批生产 `.h/.cpp` 新增 208 / 删除 286，净减 **78 行**；测试新增 92 / 删除 18，净增 74 行，新增 8 个数据行。
没有新增生产文件；pagestore 32,950 → **32,872**，Store.cpp 4,266 → **4,047**。三批生产累计净减 **677 行**。

验证见 [第三批证据](../../../evidence/br1_convergence_c3_20260923/README.md)（目录 c3 表示第三批，不表示 C3 读侧已完成）：

- 当前构建成功；七个 PageStore/Completion ctest 全过，QtTest totals 927；Painter 99；tiles3 完整套件 334。
  全部上述日志无 FAIL/SAFE ASSERT；定向回归 totals 34，包含新增断言和迁移后的并发注入。
- 当前图：1,611 APIs / 13,680 edges / 14 callbacks / 85 TUs；physical gate production/test 仍为 0/20。
  source checkpoint 按旧侵入上限刷新，architecture gate 通过；固定起点和前两批证据保持不变。
- 去掉默认 before 分配与历史导出是已验证的结构性工作减少；没有运行 upstream 配对吞吐实验，不授予 BR1-PERF Pass。

### 2026-09-23：第四批扩大整层删除与读协议收敛

- D7–D10 的独立 `KisPageStoreHLineIterator/VLineIterator` 原型整文件退出（380 行），移除构建项。
  删除前当前 Clang 图确认没有原型文件外的生产调用；构造/调用/override 子图包含在本批证据中，不能仅凭文本搜索。
  唯一调用它们的负坐标/跨页测试迁到真实 `KisHLineIterator2/KisVLineIterator2` 和 captured PageStore scope，
  保留像素、步进、连续范围、换行/列断言并补充 reset 验证。实际业务 iterator 没有被删成测试替身。
- 删除没有资源签发/消费路径的 `KisReplicaHandoffClaim` 全部实现，以及 entry 的空 binding/handoff/budget/dirtyCoverage。
  删除完全被忽略的 `KisPageWriteContext`、无消费者的 `KisPageWritePlan` slot/revision/proof 字段和只写不读的 flags；
  selector 返回 kind 值，coldPageIndex 独立命名，不再挪用 descriptorIndex。没有删除真实预算 reservation、物理 gate、
  metadata 身份验证或 admission；handoff 仍关闭。设计目标留在 68，不能为尚未实施的功能预埋每页运行成本。
- arm64 与 x86_64 使用同一真实编译数据库测量，`KisPageWriteIntent` **48 → 24 B**，
  `KisMutationPageEntry` **280 → 104 B**；静态上限分别从 64/512 收紧到 32/128。
  移除 schema 对 metadata arena 的无用头文件依赖及三个没有调用者的 entry 观察 API。
- CPU session 的读页和写前 before-image 共用现有 `KisPageStoreReadPage`，删除 `ReadRecord`、两套 fallback acquire/resolve、
  `mayUseGenericRead` 和手工 base lease 释放协议。真实业务 iterator/backend 已用此持有对象，不引入新 manager。
  priority 和 generic writer 的预选控制路径保留；Busy/Invalid/ResourceUnavailable 不触发物化 fallback。
  operation 与 cursor 的缓存寿命不同，仍由各自 scope 控制，不为删代码合并可见性边界。
- 新失败注入覆盖 generic resolve 拒绝后的 request 清理和重试、CursorPage 失效时释放旧 pin、OperationSpans 保留旧 pin，
  以及当前 root 更新后的 cache miss 仍读取捕获版本。既有 native 默认零 before 分配、Busy、captured overlay、移动持有者回归保持通过。
- 审计脚本原先硬编码旧 schema 名称，首次 gate 按预期拒绝本次删除；现要求更紧的实际尺寸、禁止空资源字段回流，
  selector 提取改为新签名，并禁止任何 handoff kind 出现在当前 selector。三个内存负例确认：放宽 entry 上限、恢复空 budget、
  提前返回 handoff 均被拒绝；未提高外部侵入上限，也未刷新固定 convergence 起点。

本批生产 `.h/.cpp` 新增 63 / 删除 710，净减 **647 行**，另外 CMake 删除 1 行；测试新增 61 / 删除 19，净增 42。
删除两个生产文件、没有新增生产文件；pagestore **32,872 → 32,225**，Store.cpp 4,047 → 4,034。
四批生产累计净减 **1,324 行**（不含构建脚本/测试/文档/生成证据）。不是以空行或搬文件制造净减少。

验证见 [第四批证据](../../../evidence/br1_convergence_c4_20260923/README.md)（c4 表示批次，不表示 C4 预算阶段完成）：

- 七个 PageStore/Completion ctest 全过，QtTest totals **929**；Painter **99**；tiles3 **334**（seed 12345）。
  最终日志均无 FAIL/SAFE ASSERT；两组定向 totals 4/7，包含真实业务 iterator 和新失败注入。
- 当前图 **1,560 APIs / 13,587 edges / 14 callbacks / 84 TUs**；physical gate production/test **0/20**。
  构建/source checkpoint/architecture gate 一致；没有把旧 schema 删除误称为已实现 handoff 或统一所有写入策略。

### 2026-09-23：第五批可达性驱动的整层退出

- 在原 Clang/IndexStore 生成器中增加生产边界、测试、间接调用三类独立遍历，记录逐函数前驱和非生产强连通分量。
  生产文件内互相调用不再自动成为生产根；测试根不保活生产孤岛。回调/override、非调用引用、模板和 RAII 保守标记，
  不输出自动删除许可；六组工具回归覆盖环、测试根、外部边界、析构、回调/override 和非调用引用。
- 删除 metadata 独立 `reserve/bind/reject/queue/drain` 调度链及其 shard map/queue、两个永久身份集合、identity mutex、
  activity 计数、专属指标和 Store 中永远为零的 close/session 投影。其所有状态生产者只有旧测试调用；生产读取这些
  恒零状态的 guard/统计一并删除，不能把这些读取边误写成“零调用”。真实 owner 的 ID、default admission、请求、
  lease、provider operation、verified completion 和关闭条件保持。状态机仍定义异步语义，不声称新增异步生产支持。
- 旧 queued-completion 测试迁为状态机成功/失败/陈旧操作/ABA 及 compact metadata 的 fused-retirement 防护验证；
  public metadata 未验证 completion 的拒绝保持。生产默认准备用例新增 65 请求同页去重，验证唯一分配、唯一 request ID、
  late request、伪造身份/重放拒绝、取消、关闭背压和归零；原 65 页/64 并发限额用例保留。
- 删除早期 `KisTiledDataManagerPageStoreShadow.{h,cpp}` 及构建项。原身份/default/extent/clone COW 测试迁到真实 backend、
  captured view 和 provider：检查真实 shared backing、写后分离、源像素不变、旧默认视图与负坐标，而非摘要模拟 generation。
- 清理无消费者接口、旧包装及 reservation 自分配旧入口；小候选 inline cleanup 改为消费既有 `clearBatch(units)`，
  并删除第二个 clear 入口。`installCommitOnly()` 原来的 tryInstall+assert 空包装退出，不代表已实施不可失败 handoff。
  `backingAuthority` 的模板调用、captured view 析构释放及 prepared publication cancel 明确保留，零直接调用不等于死代码。

生产 `.h/.cpp` **+14/-895，净减 881**，CMake -1；无新生产文件，删除两个原型文件。
测试 **+170/-224，净减 54**；两个审计脚本及新工具回归合计 **+193/-2，净增 191**，分别计数。
pagestore **32,225 → 31,344**，五批生产累计净减 **2,205**。测试、脚本及证据另计，不把搬文件当作删除。
当前图 **1,523 APIs / 13,430 调用点 / 14 callbacks / 83 TUs**，退出 37 个索引符号，无新生产 API。
图中 987 个生产边界可达、314 个间接调用待复核、167 个测试可达待裁决、55 个无已知入口待复核；
这些是自动筛选分类，不是剩余死函数数量或全量人工审计完成声明。跨构建 GPU/BR0 契约没有据此误删。

证据见 [第五批](../../../evidence/br1_convergence_c5_20260923/README.md)。PageStore/Completion 七套全过（QtTest totals **930**），
Painter **99**，tiles3 **334**（seed 12345）；最终日志无 FAIL/SAFE ASSERT，当前 build/source checkpoint/architecture 一致。
首轮迁移测试误走 public metadata completion 入口被正确拒绝，已转为 reference oracle 与真实生产请求验证，未放宽 gate。
本批完成的是上述孤立层及接口清理，不代表 C2–C5 全部关闭，也不授予 BR1-PERF Pass。

### 第六批：活路径状态与资源收敛（2026-09-23）

本批不是继续把零引用等同死代码，而是审查仍有调用的字段、构造/移动/析构与实际消费者；
`SourceSet` 和 `planEntry` 的旧调用全部迁移，freeze 则确认从未在生产启用。14 个退出的旧 API/声明条目及其
原始调用记录保存在 [逐项替代证明](../../../evidence/br1_convergence_c6_20260923/state-dispositions.json)，不能把 14 当作死函数数量。

- entry 的 `Prepared/Exposed` 现在真正约束 guard、remove/alias、seal/cancel，guard 归还恢复 Prepared；
  删除仅断言用的 Planned、cold `guardActive/nativePrepared`，不再维护两套私有页状态。
- cold Page 删除完整 `KisPageTransition` 和像素指针。entry 保存实际需要的 operation/writer；
  target 只存 generation（固定沿用 intent key，非 default target），完整 base 保留 default revision。
  source/target 物理句柄仍是 cold 资源，transaction 仍为 session 共有，状态机输入按需组装。
- 删除 `KisMutationSourceSet`、sourceIndex、独立 source 容器的移动/替换/销毁链；16 B immutable source 引用直接归 entry。
  来源只是输入，不授权原位写；显式终结在 owner 锁外清空输入，再释放 admission。纯 alias/removal 不预建 cold slot。
  过程中否决了“alias 输入放 cold Page”的中间方案，因为它会放大纯 alias 的 staging 内存，而不是只比较代码行数。
- cold slot 的 reserve/create 两段仅剩同一调用点，合并为一次 create；删除未启用的 write-set freeze 状态。

双架构 Clang 布局：entry **104 → 104 B**，cold Page **888 → 688 B**，write set **160 → 152 B**，
session private **1296 → 1048 B**；每个实际 prepared 页的 entry + cold 对象 **992 → 792 B（约 -20.2%）**。
这是静态对象布局，不含 vector capacity、allocator、共享控制块及 payload，也不等同 RSS/吞吐测量。
entry/cold 编译期上限收紧为 104/688 B；纯 alias 不创建大 cold 记录，且不再另付 source vector 槽位。

生产 **+152 / -247，净 -95 行**；测试 **+58 / -9，净 +49**；审计脚本 **+13 / -4，净 +9**。
PageStore `.h/.cpp` 共 **31,249 行**；六批生产累计净减 **2,300 行**，不混入测试、审计 JSON、证据或文档。
证据位于 [第六批目录](../../../evidence/br1_convergence_c6_20260923/README.md)，含删除前完整源码与 audit 备份，可恢复旧实现。

最终 universal build、fresh Clang graph（1,514 APIs / 13,463 edges / 83 TUs）、源码 checkpoint 和 architecture gate 通过；
四个 cold 旧字段与两个旧协议 token 的负向夹具均被拒绝。PageStore/Completion **932**（CPU mutation **486**），
Painter **99**、tiles3 **334**（seed 12345），均无 FAIL/SAFE ASSERT。新增 64 页 alias/source 寿命、guard 移动/扩容与
重复取指针排他检查；源引用在最后一次初始化后释放。首轮新增 alias 用例把初始化的 pins 算进了当前操作，已改为准确的差量，
未放宽正确性断言。函数图仍只覆盖当前 CPU 编译配置，结构缩减不授予 BR1-PERF Pass。

### 第七批：被替换 overlay 的单一历史寿命（2026-09-23）

本批继续处理仍有生产调用的旧协议：generic 替换旧 proof 后，原先保留旧 Prepared，分别在写终结、读释放、
last-use 和 captured-view 回调中尝试清理；native 已使用 `DetachPreparedVersion -> Historical`。
旧清理函数有 4 处直接调用，读服务另有一处回调注册，不能归类为死代码。

- generic 新 proof 验证成功后才 detach 旧版本，再替换 overlay proof；新 proof 失败保留旧 overlay。
  detach 失败则撤销新 proof 并走已有取消/abort 重试，不丢失 active write 的清理所有者。
- 两种入口共用 HistoryCollector 的 root/read/capture/pin/last-use 资格判断；删除 superseded-Prepared
  状态机分支、metadata 特例、Store 清理函数、读服务反向回调、重复 releasedVersions 容器。
  被替换版本的 generic reader 不再阻止新 overlay 的 abort；它与 native reader 一样独立存活至释放。
- 待解析请求取消、provider 解析失败都触发历史回收；失败解析复用 cancel，不再忽略 ReleaseRead 结果后丢掉请求。
  native seal、generic 终结和读释放复用已有的 owner 锁外 retirement helper，没有新增清理协调器。
- 状态机枚举保留退役值 25 的空位，后续值不漂移；最新 Prepared 仍不能按 Historical 丢弃。
  新增 **84** 组交叉测试：4 种 native/generic 前后组合 × 7 种 reader/请求寿命 × commit/abort/新 proof 失败。
  原状态机/indexed 测试迁到 detach + historical discard；保留拒绝条件、精确回收和不导出全量 snapshot 的检查。

相对第六批后的实际脏工作树，生产 **+38 / -173，净 -135 行**；测试 **+123 / -15，净 +108**；
checker **+2 / -1**。PageStore `.h/.cpp` 共 **31,114 行**，七批生产累计净减 **2,435 行**。
没有删测试来凑净值；测试/审计 JSON/文档不混入生产数。删除前源码、旧调用子图和最终 hash 见
[第七批证据](../../../evidence/br1_convergence_c7_20260923/README.md)。

最终 universal build、架构 gate、源码 checkpoint 和 fresh Clang graph 通过：**1,512 APIs / 13,525 edges /
13 callbacks / 83 TUs**。四个退役协议 token 和旧源码图均被负向门禁拒绝，固定 convergence-start 未改写。
PageStore/Completion **1,016**（CPU mutation **570**）、Painter **99**、tiles3 **334**（seed 12345），
均无 FAIL/SAFE ASSERT；运行测试为 arm64。这关闭旧 overlay 的第二套回收语义，不代表全部 provider 执行、
native 多页原子 seal、有限 Debt 析构退出或性能资格已完成，也不将正确性通过解释为吞吐提升。

### 第八批：provider 拒绝后的单一退休出口（2026-09-23）

前七批退出重复活协议后，generic 分配在预约丢失、provider 结果无效、metadata 准备失败时仍分别执行
锁外退休和请求失败清理；default/alias 也各自重复一段锁外 `retireOrDefer` 调用。本批保留入口不同的
准备方式，把相同的退休执行收回 Store 的一处 helper，generic 三种失败共用一处终结出口。

generic 分配现在先判定返回 replica 是否属于本次目标 version、选中的 provider/epoch、且不与 source
共用 allocation，才将它登记到 backing 账本；同一个判断决定失败后能否退休它。故障注入让 provider
为第 0 页写入返回第 1 页现存 replica，验证拒绝请求、原页像素与 provider committed bytes 保留、
没有多一次退休调用。保留 native writable guard 必须在 owner 锁外归还的独立清理时序。

相对第七批后的实际脏工作树，生产 **+33 / -54，净 -21 行**；测试 **+36 / -0**。
PageStore `.h/.cpp` 共 **31,093 行**，八批生产累计净减 **2,456 行**。
源码快照、三处分支的前后替代及最终 hash 位于 [第八批证据](../../../evidence/br1_convergence_c8_20260923/README.md)。
最终 universal build、fresh Clang graph、架构 gate 与固定起点检查通过；
PageStore/Completion **1,017**（CPU mutation **571**）、Painter **99**、tiles3 **334**（seed 12345）通过。
调用图为 **1,513 APIs / 13,529 edges / 13 callbacks / 83 TUs**。本批收敛的是失败协议，不把
正常 provider 准备、batch seal、满 Debt 退出或 BR1-PERF 当作已完成。

### 第九批：Fresh 准备、发布转移和异常返回身份（2026-09-23）

第八批之后的实际脏工作树作为本批基线，操作前完整 PageStore 源码与所改测试、审计输入只留一份快照，
最终构建/测试/图/文档在同一 [第九批证据目录](../../../evidence/br1_convergence_c9_20260923/README.md) 绑定，
不为每个小修改创建阶段档案。

- native 与 generic 的 FreshPayload/FreshDiscard/FreshCow provider 准备由 `WriteCoordinator::prepareFreshReplica`
  选择和执行；native source-copy、generic 条件同步复制与异步 transfer 的差异仍保持在各自可见性边界。
  私有版本的 `BeginPublish -> PublishWrite` 两步转移也只由 `publishPrivateWrite` 组装；native 多页 seal 的候选安装
  仍必须保持原子，不被误并成逐页 root commit。
- default materialization、alias、native、generic 和初始字节导入都在 backing 登记前核对返回 replica 的目标
  exact version、provider/epoch，Fresh 写入另排除 source allocation；错误返回不得借本次拒绝退休其他页实体。
  故障注入覆盖 generic 写、虚拟默认页 read、checkpoint 初始字节导入：provider 三次返回第 1 页存活实体，
  三次均拒绝且保留原页像素、内存账与退休次数，关闭注入后默认页和初始导入可重试。
- 退出未接线的五个 input/exposure/plan 枚举值及三个 `_p.h` 内部未用访问器。
  一度按图上零调用尝试移除 `PreparedPublication::backingAuthority`，完整构建发现模板实例化仍调用它，
  已恢复；这是本批给 C0 新增的人工复核约束，不把图上零调用当作整程序死代码证明。

相对第八批基线，生产 **+88 / -84，净增 4 行**；PageStore `.h/.cpp` **31,093 → 31,097 行**，
九批累计净减 **2,452 行**。测试 **+46 / -4**，新增行为纳入既有故障用例而不增加 QtTest 用例数。
这不是满足 C5“每个重写范围生产净减少”的一批：新增的共同执行点和身份保护带来小幅净增长，
后续必须继续删除旧执行/状态权威，不能把仅合并入口当作写入协议已完全收敛。

最终 universal build、PageStore/Completion **1,017**（CPU mutation **571**）、Painter **99**、
tiles3 **334**（seed 12345）均通过且无 FAIL/SAFE ASSERT。fresh Clang 图 **1,513 APIs / 13,531 edges /
13 callbacks / 83 TUs**，physical gate production/test **0/20**；源码 checkpoint 与架构 gate 通过，
旧图被 7 项源码指纹变化拒绝，固定 convergence-start 未改写。仍未证明 handoff、满 Debt 析构退出、
全配置可达性或 BR1-PERF Pass。

### 第十批：剩余七项集中收口（2026-09-24）

本批不再以拆分类型或迁移代码作为进展，直接按七个未完成门补足退出条件；证据集中在
[第十批证据](../../../evidence/br1_convergence_c10_20260924/README.md)。结果是四个未闭合门全部闭合，三个局部门中
C4.3、C5.5 获得实质推进，C3.4 经引用图复核后保持局部；总表从 17/3/4 更新为 **21/3/0**。

- C2.8：generic FreshCow 的 provider 解析、bridge 选择、request 构造、终态校验/消费全部进入 WriteCoordinator。
  Store 不再识别 FreshCow 或 transfer operation，只保留分配 readiness、生命周期复验和安装。
- C3.5：ReadBaseline 新增 N16/N1024、K1/K16、H0/H32 控制行，准备历史不计入测量；内部计数器证明每轮只解析 K 页，
  generic request/default materialization/metadata transition 恒为零。该证据关闭控制成本门，不声称性能资格通过。
- C4.2/C4.3：provider/Tiles3 增加按 physical slot 合并、按 sequence 确认的 domain journal；tile store 支持同一 payload
  的多观察者，并在 storage 锁外通知。OwnerLedger 从逐次 N backing 扫描改为 P provider + K changes。
  这关闭 C4.2；由于 swap 仍先于 Store admission 发生，C4.3 只从“缺可靠通知”推进到“可靠事后增量同步”。
- C4.6：真实 Store 的一页限额矩阵覆盖 Current 原子拒绝、Pending 竞争、OptionalCache 拒绝、SSD/durable 拒绝和
  swap-in 后重试；与已有 Debt、部分取消、拒绝退休及 drain/close 用例共同关闭该门。
- C3.4：重新核对 manifest 和新调用图；tile state/bridge/lease、DM routing、backend admission/anonymous/iterator、
  iterator base、random accessor、painter operation 十组 CPU/tiles3 兼容边界仍有生产调用和行为契约。
  本批没有把“可达但不喜欢”的 adapter 当作死代码删除，也没有为门数伪造替代层，因此保持局部。
- C5.5：七套 PageStore/Completion 在 arm64、x86_64 各 **1,000/1,000** 通过；fresh graph 为
  **1,381 APIs / 13,355 edges / 15 callbacks / 82 TUs**，architecture gate 在原侵入上限下通过后才刷新源码 hash。
  Vulkan foundation universal build 首次暴露旧 `isKnownSource` 调用；该侵入改用完整 ticket 的 canonical `status` 校验后，
  arm64、x86_64 各 **14/14** 通过。活跃 Vulkan provider 按 BR1 仍 fail-closed，完整吞吐/时延资格也未完成，所以保持局部。

生产 PageStore 目录从上一记录 26,584 增至 26,759（**+175**）。新增量承担可靠 domain journal、多观察者生命周期、
回调锁隔离和 transfer owner 收口；它有明确协议用途，但不是删行收益。全收敛范围相对 33,551 仍净减 6,792 行。

### 后续仅剩局部项

1. C3.4：十组 CPU/tiles3 兼容边界仍有真实生产调用。若继续收敛，应以 canonical cursor/operation scope 直接替换
   tile/iterator/painter 调用点，并在同一修改中删除旧 bridge/anonymous/boundary 状态；仅搬 wrapper 不得闭合。
2. C4.3：domain journal 已可靠且 O(P+K)，但要闭合仍须把 swap-out 改成 Store 先预留 Ssd class、失败可拒绝或回退，
   而不是域改变后再同步账本。
3. C5.5：CPU 与 Vulkan foundation 双架构正确性、静态门已一致；仍需启用活跃 Vulkan provider 路径并完成正式
   BR1-PERF 吞吐/时延/内存资格。
   不以删行数、QtTest 耗时或一次控制样本替代性能结论。
