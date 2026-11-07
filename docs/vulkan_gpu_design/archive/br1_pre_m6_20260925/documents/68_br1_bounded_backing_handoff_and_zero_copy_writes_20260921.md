> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 有界 backing、条件 COW 与零冗余复制写入架构（2026-09-21）

当前执行（2026-09-25 最新复核）：**按 [90](90_br1_m5_baseline_freeze_review_20260925.md) 关闭默认更新/构造失败与 index install 分配三个反例，按 [91](91_br1_m6_to_completion_entry_plan_20260925.md) B1–B6 冻结合格前置后再进入 M6 → M7 → M8 → BR1-PERF。** M5-ready 尚未通过，本文安全和性能阈值继续生效。

## 历史实施补记

以下至第 1 节前为历次时点记录；“当前/已完成”不覆盖 90 的新反证。

2026-09-25 早期执行：按 [86 最终收敛方案](86_br1_m5_final_convergence_plan_20260925.md) 继续关闭 M5 缺口。
[85 审计](85_br1_m5_code_readiness_audit_20260924.md) 已重开 C4.2/C4.4，并要求复核完整 seal 编排；swap 前准入、compatibility 与正式性能仍开放。
[84 全性能优化链路收敛](84_br1_full_optimization_convergence_and_cleanup_20260923.md) 的批次记录保留为历史证据，其完成计数不再作为当前验收结论。
M1–M5 的历史实现/回归记录保留，但 M5 的协议统一、有限生产预算及调用图证据重新审查；不以原完成标签证明收敛。
范围追溯到 52 起全部性能优化；C0–C5 相关缺口闭合前不扩展 M6/M7，生产 handoff 仍未实现。

2026-09-23 第四批收敛调整：下文完整 handoff 类型是目标设计，不要求运行代码预埋未接线对象。
已移除空 `KisReplicaHandoffClaim`、binding handle、未消费的 context/plan 字段及 entry 中从未持有资源的 budget；
当前 selector 返回 kind 值，不持有 slot/context 占位状态；cold slot 用独立索引，不再冒充 descriptorIndex。
真实 claim/预算/绑定仍由 admission、owner ledger 和冷页资源对象持有；handoff 安全条件不变，未来接线时才引入对应 capability。
arm64/x86_64 实测 entry 280 → 104 B，详见 [84 第四批](84_br1_full_optimization_convergence_and_cleanup_20260923.md)。

2026-09-23 第五批：删除未接线的 `installCommitOnly()` 包装（原实现只是可失败 `tryInstall()` 加断言）。
下文不可失败收尾仍是 M6/M7 的目标契约，不因空包装存在而视为已实现；普通 prepared commit 的验证、取消和安装状态保留。

2026-09-23 第六批：当前 cancelable session 的 entry 成为 guard 生命周期的唯一表示；cold Page 不再长期保存完整
transition、像素指针和 guard/native 标志。entry 保留 operation/writer，target 只存非 default 的 generation（key 来自 intent），
调用状态机时临时组装 transition。别名输入改为 entry 内 16 B 的强引用，删除 `KisMutationSourceSet/sourceIndex`；
纯 alias/removal 不因此分配 cold slot，终结时在 owner 锁外清空输入，再释放 admission。
当前 entry 为 104 B、cold Page 为 688 B、session private 为 1048 B（arm64/x86_64）；没有增加共享对象分配。
未被生产使用的 freeze 和仅断言用的 Planned 阶段退出；可取消 guard 归还允许 `Exposed -> Prepared` 再取用。
下文完整 handoff 草图中的 source set、freeze 和单向 Exposed 图不再要求当前实现保留；未来 commit-only 仍须独立证明不可取消边界。

2026-09-23 第七批：generic overlay 替换与 native 共用旧版本 `Prepared -> Historical` 生命周期，
新 proof 验证成功后才 detach 旧版本；旧读者、captured view 和 last-use 继续保护 exact generation。
退出 superseded-Prepared 专用回收分支和 ReadCoordinator 回调，读请求取消/解析失败也触发统一历史回收。
这是现有 Fresh 路径的协议收敛，不实现 handoff，也不宣称 provider 准备、seal 原子候选和有限预算已全部统一。

2026-09-23 第八批：default、alias 与 generic 分配拒绝复用 Store 的锁外退休执行；generic 的预约丢失、
provider 结果无效和 metadata 准备失败共用一个终结出口。generic 先验证返回 replica 的 exact version、provider/
epoch 与非 source allocation，才准许进入 backing 账本；错误返回不能借本次写入退休另一页的当前 backing。
这是失败路径和物理身份边界的局部收敛，尚未替换各入口的 provider 准备算法或解决满 Debt 时的 native 析构退出。

2026-09-23 第九批：当前 Fresh provider 决策和私有版本 `BeginPublish -> PublishWrite` 转移由
`WriteCoordinator` 统一，native/generic 保留各自的 CPU pin、异步 transfer 和多页原子 seal 边界。
默认页物化及初始字节导入在登记/退休前也核对返回 replica 的目标 version 与 provider 身份。
从运行时 plan/input/exposure 枚举移除未接线的 `HandoffRecoverable/HandoffCommitOnly`、`ManagedKernel`、
`CancelableSession/ManagedCommitOnly` 值；下文 §4 的完整枚举仍是 M6/M7 目标草图，并非当前 ABI 承诺。
这些值仅在私有 `_p.h` 中、无持久化编码或跨库 ABI；删除不改变 entry/冷页布局与并发边界，
将来真正接线时须重新审查枚举数值和协议。
这不实现 handoff、有限 Debt 退出或零拷贝性能资格；本批证据见 [84 第九批](84_br1_full_optimization_convergence_and_cleanup_20260923.md)。

2026-09-23 持续收敛：运行时再次退出未承担决策的 `CompletePayload/AsyncProducer/NoPixelExposure` 值；
完整 payload 由 `InputBytesReady`、异步访问由 `AsyncLease`、语义写由 `Semantic` 分别表达，避免两份事实可不一致。
`SemanticOnly/ReusePending` 从当前 Fresh-only selector 退出：这两个结果此前只由单元测试直接构造，生产调用均传入空 pending，
语义及 pending 的真实处理仍在 session 而未统一，故不得借枚举声称已通过 C2 三入口策略门。
下文 §4 的完整目标枚举不改写为运行代码清单；未来接入时必须连同调用/状态迁移和旧分支删除证明。

2026-09-24 持续收敛：上述两个结果已随真实执行接线恢复，而非重新预埋。selector 读取同一 entry 的
prepared target，决定 `SemanticOnly/ReusePending`；semantic staging 据此更新已有 target，alias prepare 据此选择
`AdoptPreparedWrite/ReplacePrivatePreparedBacking`。Fresh payload/discard/COW 仍由该 selector 决定，当前运行范围不再有
session 以 cold Page 存在性独立猜 plan 的第二权威。Handoff 两种结果仍未接线、未恢复。

2026-09-24 后续收敛：tiles3 当前唯一具体 provider 始终提供 native CPU mutation，因此已删除该
provider 永不可达的 generic-write lease、完成/取消分支及 Store reservation 写入口。Store 的公开异步
generic provider 边界仍保留，本次删除不改变其契约，也不把 native 路径误称为 handoff。Metadata 所有生产
owner 转移同时已统一走有界 projection/prepared-publication，旧的公开全页 snapshot→state-machine→assign
转移实现已删除；完整 snapshot 只保留为注册导入边界和测试只读 oracle。

2026-09-24 proof 协议收口：native 多页 seal 与 generic finish 已共用同一 owner seal，且新/旧 overlay proof
的安装、撤销、removal 清理统一由 `KisPagePublicationCoordinator` 执行。page removal、transaction abort/commit
不再直接改 proof 侧表；多页仍先用 prepared metadata candidate 保证批次原子性，这是必要的批量差异，
不是第二套 proof 发布语义。

2026-09-24 compatibility 观测收敛：R0 使用的 backend `KisPageStoreCompatibilityCensus` 已完成路径盘点职责，
但只有一个测试读取，且为了计数在 tile lease、writer claim、iterator probe、refresh 等生产热路径重复加锁/写状态。
现删除该快照、记录回调和只为计数暴露的 waits/newly-claimed 参数；真实 reservation、transaction、lease、
iterator boundary 与 refresh 失败闭合不变。审计表对仍存 adapter 改为 source-bound/static 或复用 Store/Mutation 的
authoritative capability snapshot，行为测试保留成功、拒绝、取消和跨线程注销。provider payload/plan 等用于复制策略
裁决的专项指标保留，不把“删全部观测”当作收敛。

2026-09-24 canonical mutation factory 收口：生产和测试 caller 全部改用 `beginMutation()`，删除 Store 的两个
`beginCpuMutation()` 重载、session 的 `enableCpuWrites()` 以及 backend 的同义 `beginCpuMutationBatch()`。
session 创建只冻结 transaction；首次像素操作在任何 PageKey claim、provider allocation 或像素暴露之前选择唯一兼容的
native CPU provider，纯 removal/alias 因而不依赖 CPU capability。compat 测试 helper 只有在该 preflight 拒绝且 session
仍为空时才选择 generic route；provider 工作开始后的失败仍禁止重放。legacy 单页预占的两份 wait/reentry 循环也归为同一
Store-private gate，固定 read page 未被任何 caller 使用的 `byteSize()` 便利出口退出。这一批没有接入 handoff 或取消 escrow。

2026-09-24 backend batch 继续收口：tiles3 不再同时维护“裸 transaction batch + 每页临时 mutation”和 canonical
mutation batch；删除 `beginWriteBatch()`、`replaceFullTileInTransaction()` 及 Store 的 legacy removal claim-bypass，所有 full-tile
alias/removal 与像素写都进入同一 session/write set。单页 legacy lease 也直接由 session 在像素暴露前取得 claim，不再先创建
独立 reservation 再搬运。`WriteAdmission` 删除与 origin/claimId 重复的 `ClaimKind`、重复 write-set 计数，以及从未被 caller
选择的内部 `WaitPolicy::Wait`；一次性 claim 只作 try，真实等待留在能区分 same-thread/managed/legacy 的 adapter preflight。
tile lease wrapper 改为按值持有 read lease、write guard 和 mutation facade，消除每次 tile lock 的 1–2 个管理对象堆分配。
这些调整仍保留 generic read 冷页回退、legacy unlock visibility boundary 和 managed range 全取 reservation，不宣称 R4 已完成。

2026-09-24 类型截肢复核：当前运行时的 exposure 只有 cancelable guard 与 async lease 两种，且前者是默认语义；
删除独立 `KisPageWriteExposureKind`，只把非默认 `AsyncLease` 合入同寿命的 intent flags，避免 input/exposure 两个二值字段
表达同一执行差异。`PreparedRestore` 改用唯一 `PreparedRootReservation` 名称；CPU/tiles3 provider 配置统一为
`KisCpuResidentReplicaProviderConfig`；metadata 全局/分片快照不再通过空的 `KisPageMetadataGlobalMetrics` 中间类型拼接。
这些是当前 Fresh 实现的重复表示删除，不修改下文 M6/M7 handoff 草图；未来新增真正不同的暴露协议时须随 producer、
状态迁移和终结责任一起恢复类型，不能先预埋枚举。provider operation 防重放另改为固定 4096-bit 滑动窗口，
窗口外旧 ID fail-closed，不再用会话永久集合换取安全性。

2026-09-22 更新：M0 中由 69 定义的 R0 containment/audit 已完成且没有 D0，证据见
[70](70_br1_r0_containment_and_layout_gate_20260921.md)、
[71](71_br1_r0_runtime_census_and_test_binding_20260922.md) 与
[72](72_br1_r0_reverse_callgraph_and_closure_20260922.md)。R1 已按固定顺序完成
`DefaultStorage -> RetirementQueue -> HistoryCollector -> ReadCoordinator -> PublicationCoordinator` 五项按值提取；前两项证据见
[73](73_br1_r1_default_storage_extraction_20260922.md)、[74](74_br1_r1_retirement_queue_extraction_20260922.md)，完整收口证据见
[75](75_br1_r1_history_read_publication_extraction_20260922.md)。M1 compact authoritative record 与 snapshot 分离也已完成，见
[76](76_br1_r2_m1_compact_metadata_records_20260922.md)。M2A 已把权威 record 迁入三个 shard-owned typed arena，见
[77](77_br1_r2_m2a_shard_metadata_arenas_20260922.md)；M2B 锁外 growth、类型对照与 metadata-only 因果基线见
[78](78_br1_r2_m2b_lock_external_metadata_growth_20260922.md)。M3A shard index/intrusive record 证据见
[79](79_br1_r2_m3a_shard_indexes_and_intrusive_records_20260922.md)。M3B 已以 96 B compact page 与稀疏 activity 关闭 M3，见
[80](80_br1_r2_m3b_compact_page_activity_20260922.md)。M4 allocation-free publication install、prepared commit 与 side-map
收敛证据见 [81](81_br1_r2_m4_allocation_free_publication_20260922.md)。M5A 冻结 write schema、连续 write set、admission、budget
reservation 与 fresh-only selector，证据见 [82](82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md)；M5B 的 session/store、
Debt、物理 backing 与验证收口见 [83](83_br1_r3_m5b_store_session_write_migration_20260923.md)。M6–M7 尚未关闭。

本文承接 [52](52_br1_cpu_fast_path_optimization_plan_20260920.md)、
[67](67_br1_target_structure_reconstruction_20260920.md) 和
[25](../../../25_p0_canonical_pagestore_krita_tile_cow_swap.md)。历史 D4–D12 及 67 §8–32 的源码、失败样本和测试结论保持原版本边界；
本文改变后续实现方向，不把旧的“每次首写使用独立 backing”检查点追认为最终架构或新性能结果。
`KisPageStore` 系列类的拆分、重复状态清理、tiles3/iterator/painter 侵入面清单和删除门槛由
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) 冻结；实现顺序必须同时满足两份文档。

## 1. 结论与不可放宽的不变量

独立 backing 是保存同时可观察的不同像素值、支持取消和隔离在途执行的必要手段，但不得成为每个逻辑 generation 的永久默认成本。
最终模型恢复并提升 upstream tiles3 的条件 COW 原则：**唯一且可安全转交的 current backing 原位转交；只有确实需要旧值时才 COW。**

生产实现必须同时满足：

1. PageStore 仍是 generation、事务、历史、authority 和发布的唯一权威；引用计数、TileData 和 provider 不能自行签发写权限。
2. 逻辑 `PageVersion` 发布后不可被修改。允许复用的是物理 allocation，且必须通过一次原子的 ownership handoff 从旧版本解绑、
   绑定到新版本；不存在两个可读版本同时把同一可变字节当作自己的 exact replica。
3. 一个 mutation 的同一未发布版本可反复原位修改；中间结果一旦允许外部捕获，就必须重新取得写计划。
4. 无历史、无外部 View、无在途消费者且具备不可失败收尾的 resident CPU 常见写，目标是零 before-image copy、零新 payload
   allocation、零退休 payload；仍要发布新的逻辑 generation 和必要 metadata。
5. history/save/旧 View/可取消操作确实需要旧值时，每页每个业务 mutation 最多一次必要 COW；完整覆盖不得复制旧页。
6. backing、pending generation、history、in-flight 和 retirement debt 都有明确字节/数量预算及背压；不能依赖“后台最终会追上”。
7. 任一证明不完整、预算不足或物理 claim 竞争失败时走安全 COW/直接初始化，绝不删除校验或覆盖旧值来追求零复制。

目标物理存储上界为：

```text
B_physical <= B_current
            + B_retained_exact_history
            + B_active_pending
            + B_in_flight
            + B_bounded_retirement_slack
            + B_bounded_optional_cache
```

它不包含“进程启动以来创建的 generation 数”。合法 undo/history 可以增长，但必须受产品 undo policy、RAM/SSD residency
预算和 purge 生命周期管理；临时 pending、in-flight、retirement 与 preclone/cache 必须另有硬上界。
该式也不允许 current/history 永久占住 RAM/VRAM：每个 resident domain 另有硬上限，超出的仍需保留内容转入统一 SSD
或其他已验证 durable replica。文档/undo 的逻辑大小最终受产品策略和可用持久存储容量约束；容量不足必须背压或显式失败，
不能把 RAM 之外的增长改名为“可回收”后继续无界写入。

## 2. 与 upstream 的关系及当前偏差

固定 upstream `9a24ae0d8c` 的 `KisTile::lockForWrite()` 只在 `KisTileData::m_usersCount > 1` 时 COW；唯一 TileData
直接原位写。memento 在第一次变更时保留 before，新的 TileData 在同一 transaction 内继续原位修改；history purge 释放
旧 owner，内存压力可把历史 TileData 换出。这是成熟路径快的关键，不是单纯少一把锁。

当前 PageStore mutation 为保证固定 View、可取消、多页失败原子性和 provider 生命周期，强制 target allocation 与 source
allocation 不同。它已经做到同一未发布段复用 pending、完整 payload 不复制旧页、后台退休旧 generation；但无 history 的短写
仍持续分配、复制或初始化并产生退休债务。这个实现是正确性 fallback，不是最终 resident write 数据面。

不能直接把 upstream 的 `usersCount == 1` 搬成许可条件。PageStore 的旧值还可能由 retained root、captured View、transaction
base、exact lease、provider source、GPU/I/O last-use 或 legacy 裸指针保护；这些事实不必表现为 TileData 的用户计数。后续实现要
保留 upstream 的“共享才复制”结果，同时由 canonical owner 给出更完整的证明。

## 3. Published、Pending 与物理 allocation 的状态模型

逻辑与物理状态必须分开：

```text
Published G -> Replica A@G

first write plan:
  ReusePending          : Pending T 已拥有 B，继续写 B
  HandoffRecoverable    : A 从 G 转交 T；G 已有其他 exact recoverable replica
  HandoffCommitOnly     : A 从 G 转交 T；旧 G 不可再接入，首字节后只走不可失败发布
  FreshPayload          : 新 B 直接由完整最终输入初始化，不读取 A
  FreshDiscard          : 新 B 交给受控 writer 生成，不保留 A 的内容
  FreshCow              : 新 B 从 A 初始化，保留未修改内容
  SemanticOnly          : remove/default/alias/no-op，不准备 writable payload
```

物理 slot 的合法状态为：

```text
Bound(A, G)
  -> ClaimedForHandoff(A, G, T)
  -> Bound(A, T)
  -> Retiring(A, T)
```

`ClaimedForHandoff` 期间禁止新 alias、read pin、copy/transfer source、swap、retire 和 last-use；旧 binding/cache 必须失效。
handoff 完成后 provider 返回带新 `PageVersion`、相同 allocation identity 和新 logical replica identity 的 handle。metadata 的
physical-slot 索引在同一 transition 中移除 `A@G`、安装 `A@T`，不能短暂存在两个 valid owner。

逻辑 generation 仍单调且不复用；物理 allocation 的复用不等于 generation 复用，也不改变 metadata-before-root 的发布顺序。

## 4. 统一能力封装、类型边界与调用方式

生产调用方继续只使用 `KisPageMutationSession`、`KisCpuWriteGuard`、完整 payload 或语义操作。painter、iterator、provider
不得取得公共 `InPlaceWritePermit`，也不得传入“当前独占”、引用计数、handoff mode 或“不可失败”布尔值。
`KisPageWriteCoordinator` 是 `KisPageStore::Private` 内嵌的唯一策略服务；mutation session、CPU surface ops 和 backend
`acquireWrite()` adapter 都调用它，不能各自实现 selector。

### 4.1 冻结的类型规则与清单

类型规则固定为：

- `struct` 只承载可复制或可平凡移动的值，不拥有 claim、锁、预算、取消义务或 authority；
- 凡是拥有 admission、budget、physical claim、reserved metadata 或未完成提交义务的类型均为 move-only `class`；
- plan 是值，不是 capability；真正的权限只存在于 RAII claim/reservation 类中；
- store 级服务内嵌于 `KisPageStore::Private`，session 级状态内嵌于 `KisPageMutationSession::Private`；二者都不逐页分配管理对象。

| 最终类型 | class/struct | 所有者与职责 |
|---|---|---|
| `KisPageMutationSession` | public move-only `class` | canonical mutation facade；唯一 shared private lifetime，不暴露 plan/claim |
| `KisPageMutationSession::Private` | shared `class` | session context/write set/claims/prepared commit/counters；最后 guard 归还后终结 |
| `KisCpuWriteGuard` | public move-only `class` | session private ref + entry index + 当前 pixel view；不拥有 plan/binding control block |
| `KisPageWriteContext` | `struct` | session/operation 公共上下文：transaction、segment revision、provider policy；不逐页复制 |
| `KisPageWriteIntent` | `struct` | 单页业务事实：key、coverage、input/exposure kind、domain、priority、layout revision |
| `KisPageWritePlanKind` | `enum class` | 内部选择结果，不向调用方暴露 |
| `KisPageWritePlan` | `struct` | compact slot ids、revision、side-array indexes、fallback reason；不拥有资源 |
| `KisCpuResidentBindingHandle` | `struct` | stable physical binding slot + directory/allocation generation；跨锁不存裸指针 |
| `KisMutationPageEntry` | move-only `class` | 单页 intent/plan/target 状态及值型 claim/reservation；session write set 内存储 |
| `KisMutationWriteSet` | `class` | 单页内联、小集合线性查找、大集合可选 hash；统一 pixel/alias/remove 状态 |
| `KisMutationSourceSet` | move-only `class` | alias source 的单项内联/连续 owning storage；entry 只存 index |
| `KisPageWriteAdmission` | `class` | store 级 PageKey 写入冲突准入；coverage 只用于 dirty/kernel，不拆分 writer authority |
| `KisPageWriteAdmission::ClaimSet` | move-only `class` | 一批页全取或全不取的 RAII admission claim |
| `KisBackingBudgetController` | `class` | store 级 backing/metadata 硬预算、分类转移和背压 |
| `KisBackingBudgetReservation` | move-only `class` | 一次或一批字节预算的 RAII reservation |
| `KisReplicaHandoffClaim` | move-only `class` | provider 签发的小型物理 slot claim，按值返回 |
| `KisPreparedMutationCommit` | move-only `class` | 聚合 metadata slots/index capacity、descriptor/proof、epoch root 和 budget delta |
| `KisManagedCpuInputView/WriteTarget/WriteRequest` | `struct` | 同步 managed adapter 的 non-owning 调用栈输入；不逃逸、不复制 payload |
| `KisManagedCpuWriteBatch` | move-only `class` | 唯一可消费 `HandoffCommitOnly` 的同步受控 CPU batch |
| `KisPageWriteCoordinator` | `class` | store 级唯一 selector/prepare/install 服务，不拥有 session write set |
| `KisPageBackingLimits` | `struct` | 冻结配置值 |
| `KisPageBackingUsage` | `struct` | 冷路径用量快照 |
| `KisMutationSessionCounters` | `struct` | 单 session 非原子增量，终结时一次汇总 |
| `KisWritePlanStatistics` | `struct` | 冷路径 plan/fallback/copy/allocation/claim 统计快照 |

以下早期草案类型明确废弃，不能在实现中恢复：

- 独立 owning/move-only `KisPreparedWritePlan`：改为内联 `KisPageWritePlan + KisMutationPageEntry`；
- polymorphic `std::unique_ptr<KisPreparedReplicaHandoff>`：改为按值 `KisReplicaHandoffClaim`；
- 每 generation 新建 `QSharedPointer<KisCpuResidentBinding>`：改为物理 slot 稳定 binding + expected generation；
- 每页 `shared_ptr<Page>`：改为 `KisMutationWriteSet` 内的 move-only entry。

### 4.2 值类型的字段口径

```cpp
enum class KisPageWriteInputKind : quint8 {
    MutableGuard,
    CompletePayload,
    ManagedKernel,
    AsyncProducer,
    Semantic
};

enum class KisPageWriteExposureKind : quint8 {
    CancelableGuard,
    CancelableSession,
    ManagedCommitOnly,
    AsyncLease,
    NoPixelExposure
};

enum class KisPageWritePlanKind : quint8 {
    SemanticOnly,
    ReusePending,
    HandoffRecoverable,
    HandoffCommitOnly,
    FreshPayload,
    FreshDiscard,
    FreshCow,
    Count
};

enum class KisWritePlanFallbackReason : quint8 {
    None,
    RetainedRoot,
    ActiveTransactionBase,
    ExactReaderOrLease,
    PhysicalAlias,
    PendingLastUse,
    InFlightOperation,
    CancelableOrFallible,
    ClaimConflict,
    BudgetPressure,
    ProviderUnsupported,
    NonResident,
    LayoutMismatch,
    Count
};

enum class KisPageWriteIntentFlag : quint16 {
    CoverageKnown = 1u << 0,
    FullPageCoverage = 1u << 1,
    InputBytesReady = 1u << 2,
    MayWaitForAdmission = 1u << 3,
    SemanticRemoval = 1u << 4
};

enum class KisPageWritePlanFlag : quint16 {
    AlternateBeforeVerified = 1u << 0,
    TargetAllocationPreexisting = 1u << 1,
    RequiresCaptureFence = 1u << 2,
    RequiresProviderRetag = 1u << 3,
    RequiresBudgetReservation = 1u << 4
};

enum class KisMutationPageEntryState : quint8 {
    IntentOnly, Planned, Prepared, Exposed, Sealed, Consumed, Cancelled
};

enum class KisReplicaHandoffClaimState : quint8 {
    Empty, Prepared, Committed, Cancelled
};

enum class KisPreparedMutationCommitState : quint8 {
    Empty, Prepared, Installed, Cancelled
};

enum class KisManagedCpuWriteBatchState : quint8 {
    Empty, Prepared, Executing, Committed, Cancelled
};

enum class KisPageMutationSessionState : quint8 {
    Open, Sealing, Sealed, Cancelling, Cancelled
};
```

`ManagedCommitOnly` 只能由 `KisManagedCpuWriteBatch` 的私有 factory 写入，不能由 public 参数、provider capability bool 或调用方
flag 构造。`beginWrite()` 固定映射到 `CancelableGuard`，`overwritePage()` 固定映射到 `CancelableSession`，第一阶段 GPU 写固定映射到
`AsyncLease`。
`SemanticRemoval` 是同一 entry 上的暂存语义位：即使该页还有待取消的 private target，也不再另建按键 `removals` 集合；后继
alias/成功取得的 pixel guard 清除此位，seal 按 entry 遍历消费。它不表示 provider plan，也不授予 writer claim。

```cpp
struct KisPageWriteContext {
    KisPageTransaction transaction;
    quint64 segmentRevision;
    KisReplicaProviderId preferredCpuProvider;
    KisReplicaProviderEpoch expectedProviderEpoch;
};

struct KisPageWriteIntent {
    KisPageKey key;
    QRect localCoverage;
    quint64 expectedLayoutRevision;
    KisPageWriteMode mode;
    KisPageWriteInputKind inputKind;
    KisPageWriteExposureKind exposureKind;
    KisPageAccessDomain domain;
    KisPagePriority priority;
    quint16 flags;
};

struct KisCpuResidentBindingHandle {
    quint32 physicalBindingSlot;
    quint32 bindingDirectoryGeneration;
    quint64 expectedAllocationGeneration;
};
```

transaction、provider policy 和 segment revision 放在 context，不在每页 entry 重复。`localCoverage` 是调用方已经知道的页内范围；
未知范围使用明确 flag，不用空矩形同时表达 no-op。layout/descriptor 的完整值由 canonical surface state 解析，intent 只携带预期 revision。

```cpp
struct KisPageWritePlan {
    static constexpr quint32 InvalidSideIndex = std::numeric_limits<quint32>::max();
    KisPageWritePlanKind kind;
    KisWritePlanFallbackReason fallbackReason;
    quint16 flags;
    KisVersionSlotId baseVersion;
    KisVersionSlotId targetVersion;
    KisReplicaSlotId sourceReplica;
    KisReplicaSlotId recoveryReplica;
    KisReplicaSlotId targetReplica;
    quint64 expectedPageRevision;
    quint32 descriptorIndex;
    quint32 proofIndex;
};
```

无效 slot id 表示该模式不需要该角色；不允许同时内嵌三个 128 B `KisReplicaHandle`。需要调用 reference state machine/provider 时，
coordinator 在栈上按 slot record 构造完整 handle/transition。descriptor/proof 存在 `KisPreparedMutationCommit` 的连续 side arrays，
entry 只保存 index。

首版布局硬目标为：

| 类型 | 目标上限 | 约束 |
|---|---:|---|
| `KisPageWriteContext` | 96 B | session/operation 一份，不逐页复制 |
| `KisPageWriteIntent` | 64 B | 不含 owning container/string/shared pointer |
| `KisPageWritePlan` | 96 B | 只含 enum/flags/typed ids/indexes |
| `KisPageWriteAdmission::ClaimSet` | 40 B | 无 key 副本容器，引用 write set，move-only |
| `KisReplicaHandoffClaim` | 40 B | 无堆分配、无 type-erased payload，move-only |
| `KisBackingBudgetReservation` | 40 B | controller/cookie/total bytes/state，composite delta 留在 controller slot，move-only |
| `KisCpuWriteGuard` | 128 B | 一个 session shared ref + entry index + pixel view；不再持有 binding shared ref/full replica handle |
| `KisMutationPageEntry` | 512 B | 不内嵌完整 transition/descriptor/proof/snapshot |

当前 arm64/Qt6 基线为：`KisReplicaHandle` 128 B、`KisPageTransition` 440 B、`KisPageAllocationDescriptor` 216 B、
`KisPreparedPageProof` 176 B、`KisCpuWriteGuard` 200 B、mutation `Page` 904 B。以上上限是防止旧布局重新渗入热记录的门禁；
目标构建必须重新报告 `sizeof/alignof`，超限须在 review 中拆分冷字段，不能静默放宽。

### 4.3 `KisMutationPageEntry` 与统一 write set

以下保留完整 handoff 目标草图；当前运行字段及状态以本文第六批调整和 84 的收敛记录为准。
别名强引用不是 resident binding，也不授权原位写；用内联输入替代 source side set 后，页热记录上限收紧到 104 B。

```cpp
class KisMutationPageEntry final {
public:
    explicit KisMutationPageEntry(const KisPageWriteIntent &);
    KisMutationPageEntry(KisMutationPageEntry &&) noexcept;
    KisMutationPageEntry &operator=(KisMutationPageEntry &&) noexcept;
    KisMutationPageEntry(const KisMutationPageEntry &) = delete;
    KisMutationPageEntry &operator=(const KisMutationPageEntry &) = delete;

private:
    KisPageWriteIntent intent;
    KisPageWritePlan plan;
    KisPageVersion baseVersion;
    KisPageVersion targetVersion;
    KisCpuResidentBindingHandle binding;
    KisReplicaHandoffClaim handoff;
    KisBackingBudgetReservation budget;
    quint32 sourceIndex;
    QRect dirtyCoverage;
    KisMutationPageEntryState state;
};
```

`KisCpuResidentBindingHandle` 是 `{physicalBindingSlot, bindingDirectoryGeneration, expectedAllocationGeneration}` 的小型值，不是
`QSharedPointer`。完整 descriptor/proof 由 session 稀疏 cold side storage 保活，entry 的 `plan.descriptorIndex` 指向该 slot，
seal 时参与 prepared commit/publication；
alias source 由下面的 source set 保活；
`KisCpuPagePayload` 维持同步 borrowed rows 契约，必须在 `overwritePage()` 返回前被 provider 消耗，不能存进 session。entry 不保存完整
`KisPageTransition`，状态机调用前临时构造。非 alias entry 的 `sourceIndex` 固定为 `KisMutationSourceSet::InvalidSource`。

entry 状态只允许以下单向迁移：

```text
IntentOnly -> Planned -> Prepared -> Exposed -> Sealed -> Consumed
                           |           |
                           +-----------+-> Cancelled   // 普通 cancelable target，包括 ReusePending
IntentOnly/Planned/Prepared -> Cancelled
```

`HandoffCommitOnly` 在 `Prepared` 前可取消；进入 `Exposed` 即由 managed batch 同步推进到 `Sealed/Consumed`，不能转入
`Cancelled`。`KisMutationPageEntry` 的析构不隐式发布；未消费 entry 只能经 session/batch 的统一 cancel 路径归还 claim、预算和 slot
reservation。

```cpp
class KisMutationWriteSet final {
public:
    using EntryIndex = quint32;
    static constexpr EntryIndex InvalidEntry = std::numeric_limits<EntryIndex>::max();
    KisMutationWriteSet(KisMutationWriteSet &&) noexcept;
    KisMutationWriteSet &operator=(KisMutationWriteSet &&) noexcept;
    KisMutationWriteSet(const KisMutationWriteSet &) = delete;
    KisMutationWriteSet &operator=(const KisMutationWriteSet &) = delete;
    KisMutationPageEntry *find(const KisPageKey &);
    KisMutationPageEntry &getOrCreate(const KisPageWriteIntent &);
    void reserveKnownTargetCount(qsizetype);
    void freeze();
    bool isFrozen() const;

private:
    std::optional<KisMutationPageEntry> inlineEntry;
    std::vector<KisMutationPageEntry> overflow;
    std::optional<QHash<KisPageKey, EntryIndex>> index;
};

class KisMutationSourceSet final {
public:
    using SourceIndex = quint32;
    static constexpr SourceIndex InvalidSource = std::numeric_limits<SourceIndex>::max();
    KisMutationSourceSet(KisMutationSourceSet &&) noexcept;
    KisMutationSourceSet &operator=(KisMutationSourceSet &&) noexcept;
    KisMutationSourceSet(const KisMutationSourceSet &) = delete;
    KisMutationSourceSet &operator=(const KisMutationSourceSet &) = delete;
    SourceIndex add(QSharedPointer<const KisPageReplicaSource>);
    void replace(SourceIndex, QSharedPointer<const KisPageReplicaSource>);
    void clear(SourceIndex) noexcept;
    const KisPageReplicaSource &at(SourceIndex) const;
private:
    QSharedPointer<const KisPageReplicaSource> inlineSource;
    std::vector<QSharedPointer<const KisPageReplicaSource>> overflow;
};
```

行为固定为：

- 0–1 页只使用 session private 内联 entry，不产生 page heap allocation；
- `EntryIndex == 0` 永远映射 `inlineEntry`，`EntryIndex == n` 映射 `overflow[n - 1]`；加入第二页时不搬移第一项；
- 2–8 页线性查找，`overflow` 几何扩容，不创建 hash；
- 第 9 页前一次性创建并 reserve `PageKey -> EntryIndex`，以后只存 index，不存 owning page pointer；
- 已知 N 的 bulk/managed batch 在 prepare 时一次 `reserveKnownTargetCount(N)`；
- remove、alias、payload、discard 和 preserve 的 page membership 只存在于同一 entry，不再维护
  `pages/claimedKeys/removals/sources` 四套 keyed owning 容器；source set 仅按 index 保活稀有 alias 输入；
- source index 0 映射 `inlineSource`，n 映射 `overflow[n - 1]`；`add()` 先复用已 clear 的 slot，替换同一 key 的 alias 时复用/替换其
  slot，不增加平行 key map；
- guard 只保存 `EntryIndex`，不保存 entry 裸指针；vector relocation 不使 guard 失效；
- 普通 recoverable/fresh session 可在两个 guard acquisition 之间扩展；commit-only 在首字节前 `freeze()`，之后禁止扩容。

### 4.4 admission 与 backing budget

`KisPageWriteAdmission` 内嵌于 `KisPageStore::Private`，使用现有 owner mutex/condition，不增加一层全局锁。它只表达并发写入准入，
不是第二份 generation/replica ledger；metadata 仍是逻辑 authority。

```cpp
class KisPageWriteAdmission final {
public:
    enum class WaitPolicy : quint8 { NoWait, Wait };

    class ClaimSet final {
    public:
        ClaimSet();
        ~ClaimSet();                    // 未释放时归还全部 claim
        ClaimSet(ClaimSet &&) noexcept;
        ClaimSet &operator=(ClaimSet &&) noexcept;
        ClaimSet(const ClaimSet &) = delete;
        ClaimSet &operator=(const ClaimSet &) = delete;
        bool isValid() const;
        void release() noexcept;
    private:
        KisPageWriteAdmission *owner;
        const KisMutationWriteSet *writeSet;
        quint64 claimId;
        quint64 ownerToken;
        bool active;
    };

private:
    ClaimSet beginClaimSet(const KisMutationWriteSet &, quint64 ownerToken);
    bool claimOne(ClaimSet &, KisMutationWriteSet::EntryIndex,
                  WaitPolicy, QString *error);
    bool claimAll(ClaimSet &, WaitPolicy, QString *error);
    friend class KisPageWriteCoordinator;
};
```

普通 session 用同一 `ClaimSet` 按 entry 扩展；`claimOne()` 失败不改变既有 claim。managed batch 使用 `claimAll()`，它按稳定 PageKey
顺序全取或全不取，失败时不留下本次的部分 claim。`ClaimSet` 引用 session write set 而不复制 keys，因此 session/batch 成员析构
顺序固定为 prepared commit/claims 先于 write set。backend 的 `activeWritablePages`、
`operationWritablePages`、`cpuMutationPages` 迁入此类型；transaction claim、metadata writer 和 physical binding gate 仍是不同层次，
不能合并成一个 bool。

预算类型固定为：

```cpp
enum class KisBackingBudgetClass : quint8 {
    Current, RetainedHistory, ActivePending, InFlight,
    RetirementDebt, OptionalCache, MetadataArena, Count
};

struct KisPageDomainBytes {
    quint64 cpuRam;
    quint64 umaShared;
    quint64 discreteVram;
    quint64 ssd;
};

struct KisPageBackingLimits {
    quint64 logicalCurrentBytes;
    quint64 retainedHistoryBytes;
    KisPageDomainBytes residentCurrentBytes;
    KisPageDomainBytes residentHistoryBytes;
    quint64 activePendingBytes;
    quint64 inFlightReplicaBytes;
    quint64 retirementDebtBytes;
    quint64 optionalCacheBytes;
    quint64 metadataArenaBytes;
    quint64 durableStoreCapacity;
    quint32 maxTransientVersionsPerPage;
};

struct KisPageBackingUsageBucket {
    KisPageDomainBytes live;
    KisPageDomainBytes peak;
    KisPageDomainBytes reserved;
};

struct KisPageBackingUsage {
    std::array<KisPageBackingUsageBucket,
               static_cast<size_t>(KisBackingBudgetClass::Count)> buckets;
    quint64 backpressureCount;
    quint64 backpressureNanoseconds;
};

struct KisWritePlanStatistics {
    std::array<quint64,
               static_cast<size_t>(KisPageWritePlanKind::Count)> selections;
    std::array<quint64,
               static_cast<size_t>(KisWritePlanFallbackReason::Count)> fallbacks;
    quint64 handoffsPrepared;
    quint64 handoffsCommitted;
    quint64 handoffsCancelled;
    quint64 beforeImageCopyPages;
    quint64 beforeImageCopyBytes;
    quint64 payloadAllocations;
    quint64 payloadAllocationBytes;
};

struct KisMutationSessionCounters {
    std::array<quint32,
               static_cast<size_t>(KisPageWritePlanKind::Count)> selections;
    std::array<quint32,
               static_cast<size_t>(KisWritePlanFallbackReason::Count)> fallbacks;
    quint32 handoffsPrepared;
    quint32 handoffsCommitted;
    quint32 handoffsCancelled;
    quint32 payloadAllocations;
    quint32 beforeImageCopyPages;
    quint64 beforeImageCopyBytes;
    quint64 payloadAllocationBytes;
};

struct KisPageDomainByteDelta {
    qint64 cpuRam;
    qint64 umaShared;
    qint64 discreteVram;
    qint64 ssd;
};

struct KisBackingBudgetDelta {
    std::array<KisPageDomainByteDelta,
               static_cast<size_t>(KisBackingBudgetClass::Count)> buckets;
};
```

`KisBackingBudgetController` 内嵌于 `KisPageStore::Private`。`reserve()` 在首字节/新 payload/slab attach 前返回按值
`KisBackingBudgetReservation`；reservation 析构归还，publication 使用预构造 delta 将 Pending 原子重分类为 Current/History/Retirement。
预算不足返回 `MetadataPressure` 或 `ResourcePressure`，不能临时退回未计量 `new`。

```cpp
class KisBackingBudgetReservation;

class KisBackingBudgetController final {
public:
    KisBackingBudgetReservation reserve(const KisBackingBudgetDelta &,
                                        QString *error);
    KisPageBackingUsage usage() const;
private:
    void commit(quint64 cookie, const KisBackingBudgetDelta &) noexcept;
    void release(quint64 cookie) noexcept;
    friend class KisBackingBudgetReservation;
    friend class KisPreparedMutationCommit;
};

class KisBackingBudgetReservation final {
public:
    ~KisBackingBudgetReservation();
    KisBackingBudgetReservation(KisBackingBudgetReservation &&) noexcept;
    KisBackingBudgetReservation &operator=(KisBackingBudgetReservation &&) noexcept;
    KisBackingBudgetReservation(const KisBackingBudgetReservation &) = delete;
    KisBackingBudgetReservation &operator=(const KisBackingBudgetReservation &) = delete;
    bool isValid() const;
    quint64 bytes() const;
    void release() noexcept;
private:
    void commit(const KisBackingBudgetDelta &) noexcept;
    KisBackingBudgetController *owner;
    quint64 cookie;
    quint64 totalReservedBytes;
    bool active;
    friend class KisPreparedMutationCommit;
};
```

controller 用 store-owned generational reservation slot 保存 composite delta；cookie 是 slot id/generation 的压缩值，release/commit 后复用 slot，
不为每个 entry 建 `QHash` 节点或 heap record。一个 entry 只持有一个 reservation，即使 fresh COW 同时涉及 Pending、RetirementDebt 和
MetadataArena；`bytes()` 返回 delta 各正向分量之和。managed batch 可先合并所有 entry delta，再持有一个 batch reservation。

每个 session 只累加普通整数 counter，seal/cancel 时一次汇总到 store statistics，避免像素/guard 热路径原子递增。
`KisPageBackingUsage` 和 `KisWritePlanStatistics` 是冷路径快照，不持有 live container。

### 4.5 provider claim、stable binding 与 prepared commit

provider owner-only 接口按值返回 claim，不返回 `unique_ptr`。prepare/commit/cancel 都不进入 public provider capability surface：

```cpp
class KisPageReplicaProvider {
protected:
    KisReplicaHandoffClaim makeBackingHandoffClaim(
        quint64 cookie, quint64 expectedAllocationGeneration);
private:
    friend class KisPageWriteCoordinator;
    friend class KisReplicaHandoffClaim;
    virtual KisReplicaHandoffClaim prepareBackingHandoff(
        KisPageOperationId operation,
        const KisReplicaHandle &source,
        const KisPageVersion &targetVersion,
        const KisPageAllocationDescriptor &descriptor,
        QString *error) = 0;
    virtual void commitBackingHandoff(
        quint64 cookie, const KisReplicaHandle &target) noexcept = 0;
    virtual void cancelBackingHandoff(quint64 cookie) noexcept = 0;
};
```

```cpp
class KisReplicaHandoffClaim final {
public:
    KisReplicaHandoffClaim();
    ~KisReplicaHandoffClaim();          // active 时 cancel(cookie)
    KisReplicaHandoffClaim(KisReplicaHandoffClaim &&) noexcept;
    KisReplicaHandoffClaim &operator=(KisReplicaHandoffClaim &&) noexcept;
    KisReplicaHandoffClaim(const KisReplicaHandoffClaim &) = delete;
    KisReplicaHandoffClaim &operator=(const KisReplicaHandoffClaim &) = delete;
    bool isValid() const;
    KisReplicaHandoffClaimState state() const;
private:
    KisReplicaHandoffClaim(KisPageReplicaProvider *, quint64 cookie,
                           quint64 expectedAllocationGeneration);
    void commit(const KisReplicaHandle &target) noexcept;
    void cancel() noexcept;
    KisPageReplicaProvider *provider;
    quint64 cookie;
    quint64 expectedAllocationGeneration;
    KisReplicaHandoffClaimState claimState;
    friend class KisPageWriteCoordinator;
    friend class KisPageReplicaProvider;
};
```

claim 只允许 `Empty -> Prepared -> Committed` 或 `Empty/Prepared -> Cancelled`。move-from 对象立即回到 `Empty`；析构只对
`Prepared` 调用 provider cancel。`commit()` 和 `cancel()` 都是终态消费；重复消费是 invariant violation，不得再次调用 provider。

source/target/recovery handles 已由 entry/metadata slot 表达，claim 不重复保存。provider allocation record 只增加 claim cookie/state；
provider 自己判断 TileData/storage refs，PageStore 不传计数。handoff 保持同一 `(provider, epoch, slot)` 并递增
`allocation.generation`。`tryAcquireExclusiveWrite(counts)` 只可作为 provider 私有实现细节，不再是 PageStore capability。

`KisCpuResidentBinding` 按物理 slot 长期稳定，不为 generation 新建 control block。所有 read/write reservation 接受
`expectedAllocationGeneration`，在现有 binding mutex 内比较；旧 cached link 即使仍引用同一 binding，也只能得到 stale/retry。
真正 retire 物理 slot 时才 revoke/release binding。

```cpp
const void *KisCpuResidentBinding::acquireRead(
    quint64 expectedAllocationGeneration,
    bool residentOnly,
    KisCpuResidentReadStatus *status);

KisCpuWriteBindingReservation KisCpuResidentBinding::reserveWrite(
    quint64 expectedAllocationGeneration);

bool KisCpuResidentBinding::matchesGeneration(
    quint64 expectedAllocationGeneration) const;
```

现有返回内部 immutable handle 引用的 `replica()` 不再作为缓存资格；需要诊断时按值生成 snapshot。

`KisPreparedMutationCommit` 聚合而不复制现有 metadata/root 候选：

```cpp
class KisPreparedMutationCommit final {
public:
    ~KisPreparedMutationCommit();
    KisPreparedMutationCommit(KisPreparedMutationCommit &&) noexcept;
    KisPreparedMutationCommit &operator=(KisPreparedMutationCommit &&) noexcept;
    KisPreparedMutationCommit(const KisPreparedMutationCommit &) = delete;
    KisPreparedMutationCommit &operator=(const KisPreparedMutationCommit &) = delete;
    bool isValid() const;
    KisPreparedMutationCommitState state() const;
    bool tryInstall(QString *error);         // 普通 cancelable session，可失败并回滚 fresh/recoverable target
private:
    class Data;
    std::unique_ptr<Data> data;              // 一次 batch 级控制分配，不逐页分配
    void installCommitOnly() noexcept;      // 仅 ManagedCpuWriteBatch；首字节后唯一终点
    void cancel() noexcept;
    friend class KisPageWriteCoordinator;
    friend class KisManagedCpuWriteBatch;
};
```

其 private storage 包含：metadata `PreparedPublication` 的 reserved slot/capacity tokens、epoch `PreparedCommit`、descriptor/proof/
completion 连续 side arrays、root delta、budget reclassification delta 和 cleanup handles。普通 `tryInstall()` 保留现有冲突失败语义；
`installCommitOnly()` 只有在 capture fence、全部 admission/physical claims 和所有 capacity 已冻结后才可调用，内部不得 allocation、rehash、
等待 I/O/GPU 或返回普通失败。

prepared commit 只允许 `Empty -> Prepared -> Installed` 或 `Empty/Prepared -> Cancelled`。`Data` 持有唯一状态值，facade 不另存
shadow state。普通 `tryInstall()` 返回 `false` 时必须完成统一 `Cancelled`，不能保持可重试 `Prepared` 或留下部分 install；
commit-only 路径调用 `installCommitOnly()` 后必须同步到 `Installed`。

### 4.6 managed CPU batch 与唯一 selector

```cpp
enum class KisManagedCpuKernelKind : quint8 {
    PackedWrite, FillPixel, ClearToDefault, ResidentCopy
};

struct KisManagedCpuInputView {
    const std::byte *bytes;
    quint64 byteSize;
    quint32 rowStride;
};

struct KisManagedCpuWriteTarget {
    static constexpr quint32 InvalidInputView = std::numeric_limits<quint32>::max();
    KisPageKey key;
    QRect localCoverage;
    KisPageWriteMode mode;
    quint32 inputViewIndex;       // ClearToDefault 使用 InvalidInputView
    quint64 inputByteOffset;
};

struct KisManagedCpuWriteRequest {
    KisPageWriteContext context;
    KisManagedCpuKernelKind kernel;
    const KisManagedCpuWriteTarget *targets;
    qsizetype targetCount;
    const KisManagedCpuInputView *inputs;
    qsizetype inputCount;
};

struct KisManagedCpuWriteCommand {
    KisMutationWriteSet::EntryIndex entry;
    QRect localCoverage;
    quint32 inputViewIndex;
    quint64 inputByteOffset;
};

class KisManagedCpuWriteBatch final {
public:
    ~KisManagedCpuWriteBatch();
    KisManagedCpuWriteBatch(KisManagedCpuWriteBatch &&) noexcept;
    KisManagedCpuWriteBatch &operator=(KisManagedCpuWriteBatch &&) noexcept;
    KisManagedCpuWriteBatch(const KisManagedCpuWriteBatch &) = delete;
    KisManagedCpuWriteBatch &operator=(const KisManagedCpuWriteBatch &) = delete;
    bool isValid() const;
    void executeAndCommit() noexcept;
private:
    KisPageWriteContext context;
    KisMutationWriteSet writes;
    KisPageWriteAdmission::ClaimSet admission;
    KisBackingBudgetReservation batchBudget;
    KisPreparedMutationCommit commit;
    std::vector<KisManagedCpuWriteCommand> commands;
    std::vector<KisManagedCpuInputView> inputs;
    KisManagedCpuKernelKind kernel;
    KisManagedCpuWriteBatchState state;
    friend class KisPageWriteCoordinator;
};
```

它不接受 `std::function`、virtual callback 或调用方 supplied “no-fail” flag。factory 只存在于受审计的 packed `writeBytes`、fill、clear、
resident copy adapter；全部命令、目标、输入寿命、claim、预算和 commit 在返回 valid batch 前完成。首版仍受 8 页/256 KiB 上限。
batch 只允许 `Empty -> Prepared -> Executing -> Committed`；在 `Prepared` 析构可统一进入 `Cancelled`，进入 `Executing` 后只能由
`executeAndCommit() noexcept` 到达 `Committed`。首个 kernel store 是 `Prepared -> Executing` 的线性化点，所有可能失败的工作必须在它
之前结束。

`KisManagedCpuWriteRequest` 是同步调用栈 view，不拥有输入；coordinator 在返回前完成 prepare、kernel 和 install，batch 不得逃逸。
packed/fill 的调用方 buffer、resident-copy 的 source guard 必须覆盖整个调用；coordinator 把已校验 view 复制进连续 `inputs`，不复制
payload。`targets` 为空、非 clear target 没有有效 input、index/offset/stride/coverage 越界、source-target physical alias 未由计划允许、
超过 8 页或 256 KiB 时均在首字节前失败；全 clear request 可以没有 `inputs`。`InvalidInputView` 只有 `ClearToDefault` 可使用。

`KisPageWriteCoordinator` 内嵌于 store private，持有 metadata/epoch/admission/budget/owner ledger 的 non-owning 引用：

```cpp
class KisPageWriteCoordinator final {
public:
    KisPageWriteCoordinator(KisPageMetadataCoordinator &,
                            KisImageEpochReferenceModel &,
                            KisPageWriteAdmission &,
                            KisBackingBudgetController &,
                            KisPageOwnerLedger &);
    KisPageWritePlan select(const KisPageWriteContext &,
                            const KisPageWriteIntent &,
                            const KisMutationPageEntry *pending) const;
    bool prepareEntry(const KisPageWriteContext &, KisMutationPageEntry &, QString *);
    bool executeManagedCpuWrite(const KisManagedCpuWriteRequest &, QString *);
    bool prepareSeal(const KisPageWriteContext &,
                     KisMutationWriteSet &,
                     KisPageWriteAdmission::ClaimSet &,
                     KisPreparedMutationCommit *,
                     QString *);
private:
    KisManagedCpuWriteBatch prepareManagedBatch(const KisManagedCpuWriteRequest &, QString *);
    KisPageMetadataCoordinator *metadata;
    KisImageEpochReferenceModel *epoch;
    KisPageWriteAdmission *admission;
    KisBackingBudgetController *budget;
    KisPageOwnerLedger *ownerLedger;
};
```

`executeManagedCpuWrite()` 返回 `false` 只表示 preflight/claim/budget/capacity 失败且尚未写入任何像素；一旦开始 kernel，该函数通过
`noexcept` batch 内核和 commit 路径同步完成并返回 `true`。这是 `writeBytes/fill/clear/resident-copy` adapter 唯一可调用的 commit-only
入口，adapter 不接收 batch 对象。

选择顺序固定且唯一：

```text
SemanticOnly
-> ReusePending
-> HandoffRecoverable
-> HandoffCommitOnly       // 只有 ManagedCommitOnly exposure
-> FreshPayload
-> FreshDiscard
-> FreshCow
```

selector 先用 metadata/context 做 O(1) 逻辑拒绝，再进入 provider physical claim；低命中 workload 不得为每页先碰 allocation gate。
为制造 `HandoffRecoverable` 而额外复制 before 等价或劣于 `FreshCow`，禁止计为 handoff 命中。

### 4.7 对外统一用法与 capability 矩阵

`beginMutation()` 是 canonical CPU mutation factory：

```cpp
KisPageMutationSession KisPageStore::beginMutation(
    const KisPageTransaction &transaction,
    QString *error = nullptr);

class KisPageMutationSession {
public:
    KisPageMutationSession(KisPageMutationSession &&) noexcept;
    KisPageMutationSession &operator=(KisPageMutationSession &&) noexcept;
    KisPageMutationSession(const KisPageMutationSession &) = delete;
    KisPageMutationSession &operator=(const KisPageMutationSession &) = delete;
    bool isActive() const;
    KisCpuWriteGuard beginWrite(const KisPageKey &, KisPageWriteMode,
                                QString *error = nullptr);
    bool overwritePage(const KisPageKey &, const KisCpuPagePayload &,
                       QString *error = nullptr);
    bool removePage(const KisPageKey &, QString *error = nullptr);
    bool aliasPage(const KisPageKey &,
                   const QSharedPointer<const KisPageReplicaSource> &,
                   QString *error = nullptr);
    bool seal(QString *error = nullptr);
    bool cancel();
};
```

最终 public session 不接收 provider id/epoch、plan kind、handoff 开关、budget override 或不可失败声明。无 mode 的 `beginWrite(key)`
仅可保留为 `PreserveContents` 的 inline convenience overload；它不能形成第二条实现路径。

```cpp
auto mutation = store.beginMutation(transaction, &error);
auto guard = mutation.beginWrite(key, KisPageWriteMode::PreserveContents, &error);
// write guard.data()
mutation.overwritePage(otherKey, payload, &error);
mutation.removePage(emptyKey, &error);
mutation.aliasPage(aliasKey, source, &error);
mutation.seal(&error);
```

`beginCpuMutation()` 与 `enableCpuWrites()` 暂作兼容包装，内部只设置 context/provider policy 并转发，生产入口迁完后删除。
CPU provider 在首次像素准备时由 coordinator 按 base authority、resident capability 和 session policy 选择。backend 级
`acquireWrite()`/异步 lease 接口保留，但其 plan selection 必须调用同一 coordinator；不能另建宽松路径。

| 调用形式 | 允许的最优计划 |
|---|---|
| `KisPageMutationSession::beginWrite()` | pending / recoverable / fresh COW 或 discard；永不 commit-only |
| `overwritePage()` | pending / recoverable / fresh payload；普通 session 可取消，永不 commit-only |
| legacy `lockForWrite()` | 与普通 guard 相同 |
| 任意可失败 callback | 与普通 guard 相同 |
| 内建 packed `writeBytes/fill/clear/resident-copy` | 可由 private factory 建立 managed commit-only batch |
| 第一阶段 GPU async write | pending / recoverable / fresh；不使用 commit-only |
| remove/default/alias/no-op | semantic only |

普通 `beginWrite()` 返回生命周期由调用方控制的 mutable guard，因此永远不能证明首字节后不可失败。legacy 裸指针、任意 callback
和 async GPU 也不能借 provider capability 升级。普通调用者看不到 `plan.kind`，不会根据它分支。

### 4.8 session 生命周期、分配模型与文件边界

`KisPageMutationSession::Private` 保留一个 `QSharedPointer` lifetime，使 guard 可安全短暂超过 facade；它内嵌 context、write set 和
session counters，并引用 store coordinator。guard 只持有这一份 session shared ref、entry index 和 pixel view；binding 由 entry 的
stable handle 解析，不再产生第二对 shared-ref 原子操作。

成员声明和析构顺序冻结如下，不能用多个 pimpl/shared state 拆散：

```cpp
class KisPageMutationSession::Private final {
    KisPageStore::Private *owner;                // non-owning；store lifetime protocol 保证有效
    KisPageWriteCoordinator *coordinator;        // non-owning；store-scoped
    KisPageWriteContext context;
    KisMutationWriteSet writes;
    KisMutationColdPageSet coldPages;             // descriptorIndex 指向稀疏 slot；仅承载大 transition/descriptor/proof/binding
    KisMutationSourceSet sources;
    KisPageWriteAdmission::ClaimSet admission;
    KisPreparedMutationCommit preparedCommit;
    KisMutationSessionCounters counters;
    KisPageMutationSessionState state;
};
```

C++ 逆序析构保证 `preparedCommit`、`admission`、`sources` 和 `coldPages` 先于 `writes` 释放；coldPages 的 inline slot 不为首
页另行分配，只以 entry 的 side index 定位，不建立第二份 PageKey 索引或 membership/semantic authority；大量 semantic-only entry 不扩张
cold slots。显式 `seal()/cancel()` 仍是正常终结路径。最后一个 guard 延迟
private 销毁时也执行同一终结函数，不另建匿名事务注册对象。

session 只允许 `Open -> Sealing -> Sealed` 或 `Open -> Cancelling -> Cancelled`。`seal()`/`cancel()` 遇到未归还 guard 时返回
`false` 并保持 `Open`；seal prepare/复验失败进入统一 cancel，不能保留半 Prepared 的可重试 session。析构等最后一个 guard 归还后执行
同一 cancel transition。`Sealed/Cancelled` 是终态，重复终结不再触碰 provider/metadata。

guard 的目标布局冻结为：

```cpp
class KisCpuWriteGuard final {
public:
    KisCpuWriteGuard(KisCpuWriteGuard &&) noexcept;
    KisCpuWriteGuard &operator=(KisCpuWriteGuard &&) noexcept;
    KisCpuWriteGuard(const KisCpuWriteGuard &) = delete;
    KisCpuWriteGuard &operator=(const KisCpuWriteGuard &) = delete;
    bool isValid() const;
    void *data() const;
    KisPageVersion version() const;
    KisPageVersion baseVersion() const;
    quint32 rowStride() const;
    quint64 byteSize() const;
private:
    QSharedPointer<KisPageMutationSession::Private> scope;
    KisMutationWriteSet::EntryIndex entry;
    void *pixelData;
    quint32 pixelRowStride;
    quint64 pixelByteSize;
};
```

`reset()` 通过 `scope + entry` 归还 physical pin 并清空 `pixelData`；version getter 从 entry 的 compact version 取值。guard 不持有
`QSharedPointer<KisCpuResidentBinding>`、完整 `KisReplicaHandle`、claim 或 budget reservation。

修订后的 coordinator 分配口径固定为：

| 操作 | coordinator 管理对象分配 | payload 分配 |
|---|---:|---:|
| 创建 mutation session | 1 次 shared private | 0 |
| 首次单页 `SemanticOnly/ReusePending/HandoffRecoverable` | 0 | 0 |
| 单页 alias source | 0；只增加既有 source 的 shared ref | 0 |
| 重复取得同页 guard | 0 | 0 |
| 单页 `HandoffCommitOnly` | managed commit 的批量 side storage | 0 |
| `FreshPayload/FreshDiscard/FreshCow` | 无逐页 plan/claim/binding 分配 | 按模式 1 |
| N 页 managed batch | O(1) 次 vector/index/arena block 扩容 | 仅真正 fresh 的页 |

这里的 0 仅指 coordinator 不创建逐页堆对象；metadata slot、session aggregate capacity 和冷路径 index 仍按 §5 计量。

| 文件 | 允许包含的类型/职责 |
|---|---|
| `KisPageStore.h` | 现有 public session/guard/业务参数；不出现 plan/claim/arena |
| `KisPageWriteCoordinator_p.h/.cpp` | context、intent、plan、entry、write set、coordinator、admission、managed batch、prepared commit |
| `KisPageBackingBudget_p.h/.cpp` | limits/usage、budget controller/reservation；不依赖 painter/iterator |
| `KisPageMetadataArena_p.h` | typed slot id、slot arena、slot index/reservation；不依赖 provider/pixel 类型 |
| `KisPageMetadataCoordinator_p.h/.cpp` | compact records、shard、intrusive links/cursor、snapshot projection |
| `KisPageReplicaProvider.h` | backend-neutral prepare 签名及 `KisReplicaHandoffClaim` 前置声明；不暴露 claim 字段 |
| `KisPageReplicaHandoff_p.h` | claim 的固定值布局、cookie 状态和 provider 私有 commit/cancel bridge；仅 coordinator/provider 实现包含 |
| `KisCpuResidentBinding_p.h` | stable physical binding、generation retag/validation；不向 painter/iterator 暴露 |

`KisPageStore.cpp` 只保留 public facade 和 owner 生命周期，现有 mutation 大段逻辑迁入 coordinator。provider 只能实现物理契约，
不能包含第二份 selector。private template/record 不进入导出 ABI，public header 不因性能实现暴露 slab、slot index 或独占细节。

## 5. metadata 稳定 slot arena 是 handoff 前置条件

handoff 会显著增加 version/replica 的短生命周期 retag 和索引更新。如果继续使用每记录 `std::list/std::map/QHash` 节点及
`shared_ptr` owning container，payload 零分配只会把成本转移成 metadata 堆抖动。因此 arena 不是后续优化项；生产 handoff
不得先于本节完成。

### 5.1 authoritative record 与公开 snapshot 分离

状态机的公开/reference snapshot 保留完整值语义，生产 coordinator 改用紧凑 authoritative record：

```text
struct KisVersionRecord;
struct KisReplicaRecord;
struct KisMetadataOverflowNode;

template<class Tag>
struct KisGenerationalSlotId {
    quint32 index;
    quint32 generation;
};

template<class T, qsizetype BlockBytes>
class KisShardSlotArena;
```

`KisVersionRecord` 保存版本、publication、authority replica slot、intrusive version/history 链和少量计数；
`KisReplicaRecord` 保存 replica identity、validity、pin/last-use、physical slot 和 intrusive replica 链。常见的一版本、一 replica、
无 lease/额外 completion 情况不得创建 overflow 节点。只有额外 replica、lease、completion、captured view 等稀有状态进入
`KisMetadataOverflowNode`。

首版布局目标为 `KisGenerationalSlotId == 8 B`、`KisVersionRecord <= 128 B`、`KisReplicaRecord <= 128 B`、
`KisMetadataOverflowNode <= 64 B`、`MetadataPage <= 96 B`。record 保存 compact identity/slot id，不嵌入当前 128 B
`KisReplicaHandle` 或 200/224 B public snapshot；超限时先拆冷字段到 overflow，而不是扩大所有热记录。

生产 transition 只投影本次触及的 compact record 到 reference snapshot，运行既有纯状态机，再将接受后的 delta 写回 slot；
不得为修改一个 pin/writer 事实复制整页历史容器。诊断、测试和完整导出按需重建 snapshot，不让冷观察布局决定热存储。

### 5.2 shard-owned arena

每个 metadata shard 独占三个 typed arena：

```text
KisShardSlotArena<KisVersionRecord, 16_KiB> versionArena;
KisShardSlotArena<KisReplicaRecord, 32_KiB> replicaArena;
KisShardSlotArena<KisMetadataOverflowNode, 16_KiB> overflowArena;
```

block 按需分配，slot 固定地址，空闲 slot 使用 intrusive free list；释放时递增 generation，所有访问都验证
`{index,generation}`。空 block 进入 shard 的可回收列表，在 owner/shard 锁外整块归还；不得逐 slot 调用通用 allocator。
arena 操作使用现有 shard mutex，不增加每记录锁或全局 allocator mutex。若 block growth 需要系统分配，先在锁外取得候选 block，
进入 shard 后只 attach 或把多余候选退回 block pool。

arena directory 在 block payload 归还后仍保留小型 `{blockGeneration,state}` 条目；重新使用同一 directory index 时递增
block generation，先验证 directory 再解引用 slot memory。slot 或 block generation 达到最大值后永久 quarantine，不回绕复用。
因此整块归还不会让旧 `KisGenerationalSlotId` 在新 block 上重新有效。

64 个 shard 全部触及 version/replica 时，首块保留约 2–4 MiB；overflow 全部触及时再增加约 1 MiB。必须 lazy allocate、报告
`allocated/used/free/highWater/releasedBytes`，并允许长期空 block 归还，不能用永久预热掩盖小文档内存成本。

### 5.3 索引和顺序

shard 维护两个权威索引：

```text
KisShardSlotIndex<KisPageVersion, KisVersionSlotId> exactVersions;
KisShardSlotIndex<KisPhysicalSlot, KisReplicaSlotId> physicalSlots;
```

`KisShardSlotIndex` 首版可封装 `QHash`，但唯一 mutation API 是 `reserveInsertions(n)`、`insertReserved(token, key, slot)` 和
`eraseExact()`。reservation 在 shard mutex 下计入 `size + outstandingReservations`；扩容发生在首字节前的 prepare 阶段，install
只消费 token。任何绕开 wrapper 的直接 insert 都由 CI/私有 API 阻止，避免并发 prepare 抢走彼此预留容量后在 install rehash。

`MetadataPage` 只保存 version/history intrusive list 的 head、tail、count 和 page revision，不再拥有每页
`shared_ptr<VersionRecords>`、exact/slot/prepared/mutable/history 容器。历史遍历使用私有 cursor
`{after, nextHint, pageRevision}`；revision 不匹配时从 page history head 恢复，不保留 `std::map`。

prepared transaction 和 mutable version 的稀有多值关系优先存 compact inline slot；溢出后进入 overflow arena。禁止重新引入
每页小 `QHash/QSet`。shard-global index 的 reserve/rehash 必须发生在 prepare 阶段，install 阶段只能消费 capacity token。

### 5.4 publication 与 binding retag

`KisPreparedMutationCommit` 在首字节前预留 version、replica、overflow slots 及 exact/physical index capacity。install 只允许：

1. 复验 page/shard revision、capture fence、provider epoch 和 physical claim；
2. 将已构造 record 写入 reserved slot；
3. 以 node/slot handle 更新 intrusive list 和索引；
4. 切换 page head/authority 并提交 root；
5. 把旧 slot 送入延迟清理队列。

这一区间不得分配、释放大对象、重建完整 snapshot 或触发 hash rehash。全量 snapshot replacement 只切换 page 的 list heads；旧 slot
在锁外分批清理。

CPU resident binding 按物理 allocation slot 稳定存在，不为每个逻辑 generation 新建 `shared_ptr` binding。handoff 在现有 binding
mutex 下 retag `allocationGeneration` 和 expected replica identity；guard/cache 保存 expected generation。任一旧 guard、缓存或晚到操作
在 generation 不匹配时失败并重新 resolve，从而关闭 allocation ABA。binding slot 只有在 provider 已证明不存在 guard、cache、operation
和 last-use 后才能回收。

## 6. 两种 backing handoff

### 6.1 `HandoffRecoverable`

当 G 的 exact bytes 已由另一个有效、受 retention 保护的 replica、SSD record、immutable before backing 或完整 journal 保存，且 A
没有已有物理消费者时，A 可以转交给 T。旧 root/View 继续解析 G，但以后只能选择保留的 exact-before replica，不能再选 A。

此模式允许 transaction 后续取消：取消 T 只退休或重新分类 A，G 仍由 alternate before 恢复。为了取得许可临时完整复制 G
通常不优于 `FreshCow`，所以 recoverable handoff 只消费已经存在或由业务本来就需要的 before；额外建立 before 的成本必须计入 E。

第一阶段只接受已经 Ready、identity/layout 完整并可独立保活的 alternate before。仅有可能重放的命令、未完成 transfer 或未经校验
的远端内容不能冒充 recoverability。

### 6.2 `HandoffCommitOnly`

没有 before 时，只有满足以下全部条件才允许复用 A：

- 本次操作的范围、输入、provider、descriptor、metadata、completion、root delta、retirement record 和所有容量已经准备；
- 旧 current root 没有外部 snapshot/View/active-base 接入，或相关 G 已明确不可达；
- owner 在 epoch/capture gate 内关闭新的旧 root 捕获和 G read acquisition；gate 后的 `CurrentCommitted` reader 只能重试并取得新 root；
- 所有目标的逻辑 claim 与物理 claim 在首字节前取得，任何 claim 失败都尚未修改像素；
- 首字节后只执行受控、不分配、不等待 I/O/GPU、不返回普通失败的内存 kernel，以及已预构造的不可失败 `KisPreparedMutationCommit`；
- 进程级故障不要求业务 rollback；普通 cancel、后页准备失败和竞争重做均不得发生在首字节之后。

普通 `beginWrite()` 返回裸 mutable span、可失败 painter callback、长 session 和一般多页 Prepared transaction 默认不能消费此模式。
首批消费者只允许完整预检的内部 `writeBytes`/clear/fill/copy kernel，或语义本来就是 unlock 即提交的单页 legacy adapter。
多页操作只有在**全部页**先完成准备和 claim、之后整个执行/发布链不可失败时才可用；否则逐页 COW，不能制造半提交。

### 6.3 handoff 的线性化与失败边界

handoff 不能表现为先改裸指针、稍后修 metadata。统一顺序为：预构造 target identity/binding/capacity 和 publication inputs；
取得 epoch/page/allocation claims；复验 alternate before 或 commit-only gate；在 metadata 的 physical-slot transition 中移除 `A@G`
并保留/安装 G 的恢复来源；消费已准备的 provider retag；最后才向 kernel 暴露 T 的 writable view。claim 持有期间任何路径都不能
把 A 作为 G 的 source 或 T 的已发布 replica 使用。

`HandoffRecoverable` 在 A 暴露为 writable 前，旧 G 必须已经能只靠 alternate before 解析。provider retag 在首字节前失败时，
可以取消 claim；metadata 已切到 alternate 也仍正确，只是少一次可选 replica。retag 成功后取消 T 只退休/缓存 A，不需要把被修改的
bytes 倒写回 G。

`HandoffCommitOnly` 从关闭 old-current capture/read acquisition 到发布新 root 期间保持 fence；内部 current root 即使仍指向 G，
也不能被新 reader 用来取得 A。任何 preflight/claim/retag 失败都发生在首字节前并重开 fence；首字节后只有 kernel、预构造 publication
和 fence release，`postFirstByteFailures` 必须为零。多页模式在全部页都进入这一可执行状态前不得修改任一页。

### 6.4 状态机专用 transition

通用 `AcquireWrite` 的现有规则保持不变：target 与任何仍属于 source/recovery/其他可见版本的 replica 使用同一 physical slot 时拒绝。
不能给通用 transition 增加 `allowSameAllocation` 开关。handoff 只允许 coordinator 构造以下两个 private transition，public request、
provider capability 和测试 helper 都不能直接选择它们。

`AcquireWriteByBackingHandoff` 只服务 `HandoffRecoverable`，在 writable view 暴露前一次完成：

1. 复验 source 是 `baseVersion` 的 exact/current replica，target 是同一 transaction 的下一代 private version；
2. 复验 `recoveryReplica` Ready、exact、layout 相同并有独立 retention，且 source 无 reader/lease/pin/last-use/operation/alias；
3. 复验 logical admission、physical claim、provider epoch、page revision 和 allocation generation 都与 prepared input 相同；
4. 在同一 owner transition 中从 G 的 replica set 移除 source，以 recovery 保持 G 可解析，安装 target replica 的新 identity，并将
   stable binding retag 到递增后的 allocation generation；
5. 消费 `KisReplicaHandoffClaim`，建立 target writer reservation，返回 `Prepared` entry；任一复验失败时零状态变化并取消 claim。

`ReplacePublishedVersionByBackingHandoff` 只服务 `HandoffCommitOnly`，由 `KisPreparedMutationCommit::installCommitOnly()` 调用：

1. 要求 capture fence token、全批 admission/physical claims、frozen write set、全部 reserved slots/index tokens 和 `Executing` batch；
2. 复验旧 current 无外部可达性、target 正好是下一代、page/root/capture revision 未变化，且 provider claim 仍锁定同一 physical slot；
3. 消费预构造的 provider retag，把 A 从 G 的 identity 移除并以递增 allocation generation 安装为 T，同时安装 metadata delta 与新 root；
4. 将旧逻辑版本按预构造 cleanup delta 退休，提交 budget reclassification，entry 进入 `Sealed/Consumed`，最后释放 fence；
5. transition 本身无 allocation、等待、回调和普通失败出口；所有可拒绝条件必须已在首字节前由等价 prepare validation 冻结。

reference state machine 必须正式建模这两个 transition 及其负例，生产 coordinator 仍以它作为逻辑 oracle。provider retag 与 metadata
不能依赖跨对象“碰巧不失败”：provider claim 的 `Prepared` 状态必须一直保留可消费的 slot/cookie，commit 是 `noexcept` 的记录切换；
metadata/index/root 所需内存和 revision claim 由 `KisPreparedMutationCommit` 预留。两侧只有在上述 transition 中消费，不能先提交一侧再走
可能失败的另一侧。

## 7. 低成本 capture gate

第一版不在每次写入扫描全部历史 root，也不为 snapshot 捕获遍历所有页面。采用保守 O(1) 快速准入：

- 无 before 的 handoff 只在没有外部 retained snapshot、没有其他 active transaction base、没有旧 current capture，且 writer 是唯一
  mutation owner 时尝试；任何不确定性直接选择 COW。
- handoff 检查、旧 root 最后保护释放、新 root capture 和 current root publication 使用同一 epoch admission gate 线性化。
- page metadata 的 exact lease/pin/last-use/provider-operation 与物理 slot claim 在 page/replica gate 复验。
- capture 先完成则本次 handoff 失败；handoff fence 先建立则 capture 等待或重试到发布后的 root，不观察修改中的 A。

这比逐页维护所有 root 的反向引用保守，但不会给 resident pixel loop 增加 O(H) 工作。后续只有性能证据证明它阻止了重要常见路径时，
才引入按 root/page 的增量 reachability cache；不能为提高命中率恢复全图登记或每次 capture 的 O(N) 成本。

`HandoffRecoverable` 可以在旧 root 仍受保护时使用，但仍必须排除已经 pin 住 A 的读者；新的 G 读取在 metadata handoff 后选择 alternate before。

## 8. 业务事务、可见性段与 bounded multi-buffer

应复现 upstream 的 first-change 结果，而不是逐 API 调用复制：

- 无 undo/history 的立即写：满足准入时 handoff current allocation；不满足时安全 COW。
- 有 undo/history 的 transaction：每页第一次修改保留 before 并 COW 一次；后续 dab/span 复用同一 pending backing。
- 完整覆盖：旧值需要保留时直接初始化新 backing；旧值不需要时 handoff 后直接写最终输入。
- remove/default/alias/no-op：继续走语义 delta，不为获得“统一”而创建 payload。
- purge 最后 history 后，下一次无保护写应重新获得 handoff 资格；历史存在不应永久污染页面。

业务可见性边界不能为了少 generation 被吞并。若一笔 stroke 的中间结果需要给 display/save/exact reader 捕获，则被冻结的版本必须保持
稳定；后续写可以在其 last-use 完成后复用 allocation，或在预算内使用另一个 pending backing。不得为每个 display snapshot 无限增加
buffer：每页 transient generation 数、文档 pending bytes 和 in-flight bytes 都受预算；达到上限时合并/跳过可丢弃的派生展示、等待最早
last-use 的异步 continuation，或对上游施加 backpressure，不能继续无界分配。

canonical history 不得因 display cadence 增长；display 是 derived consumer，其临时保护与 undo retention 分开记账。

## 9. backing 预算与压力响应

每个 Document/PageStore 在 session 建立时冻结以下预算，测试可强制极小值：

```text
KisPageBackingLimits::logicalCurrentBytes
KisPageBackingLimits::retainedHistoryBytes
KisPageBackingLimits::residentCurrentBytes       // CpuRam/UmaShared/discreteVram/SSD
KisPageBackingLimits::residentHistoryBytes       // 同上
KisPageBackingLimits::activePendingBytes
KisPageBackingLimits::inFlightReplicaBytes
KisPageBackingLimits::retirementDebtBytes
KisPageBackingLimits::optionalCacheBytes         // 软上限，压力下首先清空
KisPageBackingLimits::metadataArenaBytes
KisPageBackingLimits::maxTransientVersionsPerPage
KisPageBackingLimits::durableStoreCapacity       // 耗尽时显式失败
```

达到高水位后的固定顺序：

1. 收割已经完成的 last-use/retirement，不在 owner gate 内析构大对象；
2. 清空 preclone、default cache 和其他可重建内容；
3. 尝试合法 backing handoff；
4. 将可换出的 retained history 转入统一 SSD store；
5. 对 mutation admission、journal 或 producer 施加有界 backpressure；
6. 达到硬上限仍无法取得必要 backing 时返回明确 `ResourcePressure`，不得越过上限、丢历史或覆盖旧值。

retirement worker 的批次数量不是字节预算。排队时预占 debt bytes，成功释放后归还；provider 拒绝释放时保持债务并降低新 allocation
准入。close/drain 必须报告未清债务，不能只等任务队列为空。

## 10. provider 与 TileData 契约

新增或重构的 provider 内部操作必须表达 allocation ownership transfer，而非“返回相同裸指针”。对 coordinator 只暴露 §4.5 的
一个 prepare 入口：

```text
KisReplicaHandoffClaim prepareBackingHandoff(operation, sourceReplica, targetVersion, descriptor, error)
KisReplicaHandoffClaim::commit(targetReplicaIdentity) noexcept   // coordinator friend-only
KisReplicaHandoffClaim::cancel() noexcept                        // coordinator/destructor
```

- `prepareBackingHandoff()` 在 provider 内部一次完成资格复验和 physical claim；PageStore 不传 `usersCount/refCount` 或伪造
  `knownOwnerLedger`。provider 必须根据自己串行保护的 allocation record 判断 TileData/storage refs、active reader/source operation 和 alias。
- future target identity、binding record 和必要容量由 coordinator 在调用前创建；claim 持有期间不得重新 ref/pin/clone 同一 TileData。
- legacy/native/generic reader、provider copy/transfer/source adoption、swap/pooler、retire 和 GPU/I/O last-use 必须汇入同一 allocation gate。
- stable target binding 在 handoff 中安全 retag；旧 generation 的缓存 tag 失配后必须重新 resolve，物理 slot 真正退休时才销毁 binding。
- preclone 只能作为受预算的可丢弃优化，不能作为正确性 before、不能绕过 source gate，也不能掩盖总复制工作。

D12 的 `tryBeginExclusiveAccess()` 可作为 tiles3 physical claim 的实现基础，但它的参数和调用顺序必须由上述 ledger/plan 产生；生产
代码不得直接从引用计数推断许可。

## 11. 零复制术语和可观测性

报告只允许使用以下限定词：

- **zero before-image copy**：本次写未复制旧页内容；不表示没有用户输入 memcpy、kernel store 或 cache traffic。
- **zero new payload allocation**：复用了同一物理 allocation；metadata、generation 和小对象仍可能有成本。
- **zero payload migration**：真实跨执行域交接中没有 payload copy；与 CPU 同域 handoff 是不同结论。
- **one necessary COW**：同一业务 mutation/页因旧值确实仍可观察而执行一次完整或等价 before 保存。

新增结构计数至少包括：

```text
writePlanSelections[mode]
writePlanFallbacks[reason]
backingHandoffsPrepared/Committed/Cancelled
handoffCaptureConflicts / handoffPhysicalConflicts / handoffBudgetConflicts
beforeImageCopyPages/Bytes
payloadInitializedPages/Bytes
allocationsCreated/Reused/Retired
liveBytes{current,history,pending,inflight,retirement,cache}
peakBytes{...}
transientVersionsPerPagePeak
budgetHighWaterEvents / backpressureCount/Nanoseconds
captureFenceWait/hold and preparedMutationCommitFailuresBeforeWrite
postFirstByteFailures   // 必须严格为零
metadataArena{blocks,slotsUsed,slotsFree,reservedBytes,usedBytes,slackBytes,highWater,releasedBytes}
metadataIndex{capacityReservations,reservationFailures,rehashesDuringPrepare,rehashesDuringInstall}
publicationInstallAllocatorCalls / publicationInstallLargeDestructors
```

`rehashesDuringInstall`、`publicationInstallAllocatorCalls` 和 `publicationInstallLargeDestructors` 在生产 handoff 开启前必须恒为零。

同一 operation 的 plan、像素工作、发布、退休和最终 drain 以 operation/transaction ID 关联。handoff 成功不能从 E 中删掉 capture fence、
metadata、cache invalidation 或最终回收；COW copy bytes 也不能被归为跨硬件域 X。

## 12. 性能模型、预测与验收预算

以下数字是基于 [D4 native COW fixture](58_br1_native_cow_initialization_and_payload_accounting_20260920.md#3-对照设计与实际-payload-工作)
和 [D11 mutation fixture](65_br1_native_cpu_mutation_segment_20260920.md#4-结果批量有收益单页退化主干差距未关闭)
的实施预测，用于决定切片和失败回退，不是当前代码的性能资格。D4 将普通 preserve 从 default fill + transfer 改成一次
native duplicate 后，4 BPP K1 从 19.810 降到 11.148 μs/op，K16 从 245.508 降到 107.220 μs/op；这证明冗余
payload 初始化是主要成本，同时 after 仍有一次整页 COW。D11 当前单页约 10.45–12.26 μs/op，K16/H0/B4 为
89.72 μs/op，finish/seal/publication 已占显著比例。因此本方案应删掉最后一次不必要 COW，但不能把全部 PageStore 管理
成本预测为零。

单 operation 的估算模型固定为：

```text
T_current = T_fixed + T_metadata + T_payloadAlloc + T_beforeCopy + T_retire
T_hit     = T_fixed' + T_arenaMetadata + T_claimRetag
T_miss    = T_fixed' + T_arenaMetadata + T_fastReject + T_fresh

savedPayloadBytes = uniqueEligiblePages * handoffHitRate * pageByteSize
```

同一 session 内对同一 pending page 的后续写已经走 `ReusePending`，不能重复计算 first-write 收益。64×64 页面在 4/8/16 BPP
下分别为 16/32/64 KiB；4096 个不同页面全部命中时，峰值 pending payload 预计分别减少约 64/128/256 MiB。这里是逻辑
payload/copy 工作量，不冒充实测 DRAM traffic。

| 场景 | 当前参考 | 实施预测 | 预计变化 |
|---|---:|---:|---:|
| 4 BPP K1、无 history、handoff 命中 | 10.45–12.26 μs/op | 7.5–10 μs/op | 延迟下降 15%–35% |
| 4 BPP K16、不同页、handoff 高命中 | 89.72 μs/op | 50–70 μs/op | 延迟下降 22%–44% |
| 4 BPP K16、history 需要 COW | 101.17 μs/op | 88–100 μs/op | 延迟下降 1%–13% |
| 完整覆盖且可复用 current backing | 待隔离 | — | 延迟下降 5%–20% |
| 同页在一个 mutation 内重复修改 | 已复用 pending | — | 完整 operation 通常下降 0%–10% |
| 混合 brush/replay | 取决于写占比和 unique-page 比例 | — | 完整 E 预计下降 5%–25% |

arena 单独预计使单页热路径改善 5%–15%、批量/高 H 操作改善 10%–25%；在 allocator contention 明显的多线程 metadata
workload 中，p95/p99 可能改善 20%–50%。这是待证伪假设。常见一版本、一 replica、无 overflow 的 metadata 驻留目标降低
25%–50%；小文档必须同时计入 §5.2 的 lazy slab 首块成本。4096 个 mutation page 按当前 904 B 正文约 3.53 MiB，
按 `KisMutationPageEntry <= 512 B` 目标不超过 2 MiB，并删除 4096 次 `make_shared<Page>`；commit side arrays、vector/hash capacity
和 arena slack 仍须单独报告，不能把它们藏出分母。

主干仍可在唯一 `TileData` 上直接写；PageStore 还要支付 generation、plan、proof、seal 和 root publication。预绑定 RAM copy
已接近主干，而现有 write-intent/cached-guard 控制仍约为主干吞吐的 86%/76%，所以 handoff 可以使像素数据面接近主干，不能单独
保证公开 operation 达到 parity。session 粒度和 publication batching 仍是最终 E 的决定因素。

首版 `HandoffCommitOnly` 限制为每个 fence 最多 8 页且总 payload 不超过 256 KiB；超过任一上限选择
`HandoffRecoverable/FreshPayload/FreshDiscard/FreshCow`。该限制只保护初始 reader tail，后续调整必须基于 `captureFenceHoldNs` 分布，不按
平均 memcpy 带宽放大。逻辑快速拒绝后的 handoff miss 回退预算为不超过 2%；若进入 physical claim 后高频失败使任一正式桶
退化超过 2%，应先改 eligibility/filter，不得删除 claim。

第一轮实现验收线为：

- K1/H0/B4 延迟至少下降 20%，K16/H0/B4 至少下降 30%；未达到时先按 plan/claim/arena/publication 分段归因；
- handoff 不可用的 history 和 forced-COW 控制桶吞吐回退不超过 2%；
- publication install 区间 allocator call、hash rehash 和大对象析构均为零；
- common metadata record 驻留量至少降低 25%，arena reserved/used/slack 分开报告；
- commit-only capture fence hold p99 不高于 100 μs，且 `postFirstByteFailures == 0`；
- 结构门禁通过后再冻结正式容差；以上预测不能替代 39 的 M/K/X/E、upstream 和产品 replay 资格。

## 13. 正确性与压力矩阵

实现必须覆盖：

- 1/4/8/16 BPP，full/partial/no-op/default/removed/alias；
- 无 history、named undo、save snapshot、旧 View、active transaction base；
- native/generic/legacy reader，raw pin，copy source，swap、preclone、retire、GPU/I/O last-use；
- capture-before-handoff 与 handoff-before-capture 两种确定性顺序；
- physical claim、metadata prepare、descriptor、completion、root candidate 和 publication 前的每个失败点；
- recoverable handoff cancel/abort 后旧 G 可读；commit-only handoff 首字节后没有普通失败路径；
- 多页第二页冲突不得留下第一页半提交；
- 同一 transaction 1/10/1000 次重写只产生一次 first-change 工作；中间 seal 后按真实捕获/last-use 决定 handoff 或 COW；
- tiny budget 下持续写、长 history、慢 reader、慢 retirement、swap pressure 和 close/drain；峰值不越硬上限且有进度；
- allocation ABA、旧 binding/cache、晚到 completion 和 provider epoch 变化全部拒绝。

TSAN/压力测试不能替代确定性的状态机顺序测试；引用计数为一的测试不能替代 retained root/capture 证明。

## 14. 实施顺序

### M0：冻结接口、布局预算与基线

状态：**已完成。** R0 产物、无 D0 裁决与验证见 70–72。

- 本文、52、67、25、17、20、39 的当前/前向口径统一为 `KisPageWriteCoordinator`、内联 plan、两种 handoff 和必要 COW；
  封存 evidence 保留历史名，不回写旧结果。
- 完成 [69 的 R0](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md#r0containmentaudit)：冻结 dirty-worktree
  source inventory、symbol/reverse-call graph、状态所有权矩阵、compatibility runtime counters 与 CI ratchet；R0 前不按文件长度删除路径。
- 以 §4 的字段、枚举、状态迁移、成员析构顺序、friend 边界和文件归属为实现 schema；变更必须先修改本文并说明 ABI/内存/并发影响，
  不允许实现阶段重新引入抽象 owning plan、polymorphic handoff 或每页 shared state。
- 增加 `sizeof/alignof` 静态或测试报告，冻结 §4.2 的首版上限及 D11 K1/K16/history 控制基线。
- CI 禁止上层直接用 `TileData::data/ref/usersCount/swapLock` 判断写许可，禁止新的页级 plan/shared binding 堆对象。

### M1：authoritative record 与 snapshot 分离

状态：**2026-09-22 已完成。** 完成证据见 [76](76_br1_r2_m1_compact_metadata_records_20260922.md)。当前权威容器已保存 compact
record，公开/reference snapshot 只在 touched-record state-machine 输入或边界导出时构造；M1 的 transitional list node 将由 M2 arena 替换。

- 定义 compact `KisVersionRecord/KisReplicaRecord/KisMetadataOverflowNode` 和 typed generational slot id。
- `applyOwnerSequence()` 继续复用 reference state machine，但只投影 touched records；补 snapshot round-trip、revision 和错误注入测试。
- 此阶段不改生产写选择，所有写仍走现有 fresh allocation/COW。

### M2：shard slot arena 与预算

状态：**M2 已完成。** M2A 已实现三个 typed arena、intrusive free list、slot/block generation 与 quarantine、硬预算、
锁外整块归还、完整计数和权威 record 迁移，并删除 `VersionRecordNode` owning node；证据见
[77](77_br1_r2_m2a_shard_metadata_arenas_20260922.md)。M2B 已把所有生产 arena block payload allocation 移到 shard lock 外，
relock 后按 page revision/claim 复验，publication 按 shard 聚合 candidate blocks，并加入 candidate/attach/conflict/failure 计数与
K1/K16/H metadata-only 基线；证据见 [78](78_br1_r2_m2b_lock_external_metadata_growth_20260922.md)。

- 实作三个 typed arena、intrusive free list、generation 验证、锁外 block growth/return 和完整计数。
- 强制 tiny block/budget 测试，覆盖 slot ABA、析构、空 block 归还、close/drain 和 shard 并发。
- arena 接入前后做 metadata-only 内存、allocation count、K1/K16/H 的因果对照。

### M3：shard 索引与 intrusive history

状态：**M3 已完成。** M3A 已接入两个 shard-global `KisShardSlotIndex`、capacity reservation、intrusive
version/history/mutable 链及 revision cursor，并删除 `VersionRecords` 和 page-local list/map/hash/set，证据见
[79](79_br1_r2_m3a_shard_indexes_and_intrusive_records_20260922.md)。M3B 已删除 public-snapshot header，将 `MetadataPage`
从 776 B 收敛为 96 B，并以稀疏 slot-referenced activity 保存 writer/handoff/materialization/claim，证据见
[80](80_br1_r2_m3b_compact_page_activity_20260922.md)。

- 将 exact version 和 physical slot 收敛到 shard-global index；`MetadataPage` 改为 head/tail/count/revision。
- 用 intrusive version/replica/history 链和 revision cursor 取代 `std::list/std::map` 及每页 prepared/mutable 容器。
- 保留完整 snapshot/diagnostic 导出，证明历史顺序、restore、GC continuation 和 reference oracle 一致。

### M4：allocation-free publication install

当前复核：该保证由 [90 M4-R1](90_br1_m5_baseline_freeze_review_20260925.md) 重开。`QHash::reserve()` 不能预备全部 span node storage，实际 reserved insert 仍分配；81 的完成记录只作历史。恢复资格须在真实 install 区间验证 allocator/rehash/大对象析构为零。

状态：**M4 已完成。** metadata `PreparedPublication` 现持有 arena slot、exact/physical index capacity 与 sparse activity reservation；
outer `KisPreparedMutationCommit` 聚合 metadata、commit/restore epoch candidate、proof/descriptor/completion side arrays 和 cleanup。
commit 与 restore install 均使用 raw callback，旧的四套 transaction publication side maps 已收敛为一个 state。证据见
[81](81_br1_r2_m4_allocation_free_publication_20260922.md)。backing budget delta 将在 M5 的真实 controller 接入，不以空 capability 冒充。

- `KisPreparedMutationCommit` 在首字节前预留 slots、index capacity token、descriptor/completion/root 输入；block memory 和
  大对象尽量在锁外准备，live index 的 reservation 在 shard mutex 下登记后立即离开。
- install 期间禁止 allocator、rehash、完整 snapshot 构造和大对象析构；故障注入覆盖每个 prepare 点和全部 revision conflict。
- 删除旧 `VersionRecords` owning container 后才允许继续 M5。**M1–M4 是生产 handoff 的硬前置，不可并行绕过。**

### M5：统一 coordinator 与现有 fresh 路径

状态：核心 Fresh 协议收敛保留，但 [90](90_br1_m5_baseline_freeze_review_20260925.md) 的默认像素更新、构造/clone 与 M4 install 分配反例使 M5 整体验收重开。关闭 [91 B1–B6](91_br1_m6_to_completion_entry_plan_20260925.md#1-先形成可冻结的-m5-基线) 后才评估 M6；86 的退出标准不变。
以下为历史迁移记录，不证明协议及有限生产预算已闭合。M5A 的类型、布局、write set、admission、budget reservation、fresh-only selector 与按值 composition
证据见 [82](82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md)；M5B 已删除 store/session/backend 旧 writer/keyed
容器，把 managed/legacy/native/generic claim 收敛到单一 admission，接入 fresh allocation、publication、default cache 与退役 Debt
预算，并按 provider physical token 去重 tiles3 alias。CPU/SSD residency 由 provider footprint 在 admission/publication/usage 冷边界
同步，swap-out/swap-in 与共享 alias 的 live 归属已有确定性断言；完整实现与验证见
[83](83_br1_r3_m5b_store_session_write_migration_20260923.md)。M5 仍不授权 handoff。

- 在 `KisPageStore::Private` 内实作唯一 `KisPageWriteCoordinator`、`KisPageWriteAdmission`、`KisBackingBudgetController`，并按
  §4 的字段布局实作 inline intent/plan、move-only entry/claim/reservation、session write set 与 stable binding handle；先只选择
  `SemanticOnly/ReusePending/FreshPayload/FreshDiscard/FreshCow`。
- 把 native/generic/legacy reader、provider source、swap、retire、GPU/I/O last-use 汇入同一个 allocation owner ledger/gate，
  并为 current/history/pending/in-flight/retirement/cache 建立 live/peak bytes、硬预算和背压；M6/M7 只消费该 ledger。
- 迁移 native mutation、packed/planar bulk 和 legacy adapter，删除 `shared_ptr<Page>` 与四套 session 页容器。
- 复测行为和性能；selector 本身在 forced-COW 桶的回退不得超过 2%。

2026-09-24 收敛补记：canonical mutation reservation 已直接下沉到 session，native/generic/remove 共用 proof
安装与撤销；backend generic read/clone 统一由 `KisPageStoreReadPage` 持有 exact view 和终结责任。epoch commit/restore
共用 move-only root reservation 与唯一 `installReservedRoot` 线性化原语，测试闭包适配层不再进入生产模型。
单值 transition-effect 标签、无消费者统计、admission/ledger 影子计数和若干纯转发 API 已退出。进一步删除了
上层 count-authorized physical exclusive、binding 完整 handle/内部引用出口和 Tiles3 access/writer 影子状态；provider
exact allocation、tile cache/lease、transaction delta、proof/snapshot 定位各自收敛为单一实现，metadata/commit 多处 K²
查找改为事务内临时索引。PageStore `.h/.cpp` 当前为 27,741 行；按收敛批基线 29,168 计净减 1,427 行。
仍未运行本轮构建/测试，且 generic async transfer、
增量 backing-domain 准入和有限 Debt escrow 未闭合，因此不改变 M5 未验收、M6 未授权的结论。

2026-09-24 后续状态（上段保留为历史 checkpoint）：generic FreshCow 的 bridge/request/terminal operation 已由
`KisPageWriteCoordinator::initializeFreshReplica` 独占，Store 只消费 readiness；provider/Tiles3 以可确认 sequence journal
增量报告 backing domain，OwnerLedger 同步复杂度由 N backing 全扫降为 P provider + K changes；真实 Store 的
Current/Pending/Debt/OptionalCache/SSD 有限失败矩阵已通过。七套 PageStore/Completion 在 arm64 与 x86_64 各
1,000/1,000；Vulkan foundation contract 在修复一处旧 completion-source API 侵入后双架构各 14/14。当前门表见
[84 第十批](84_br1_full_optimization_convergence_and_cleanup_20260923.md)：C2.8、C3.5、
C4.2、C4.6 已闭合，C3.4、C4.3、C5.5 仍为局部。特别是 swap 前准入和正式 BR1-PERF 尚未完成，故仍不授权 M6/M7。

2026-09-25 验收修正：上段是 85 独立审计之前的历史判断。C4.2 因可复现旧快照覆盖重开，C4.4 因真实 backend
有限预算和 MetadataArena 未接线重开；有限测试矩阵不证明产品配置或 swap 前准入完成。后续按 86 的批次及退出条件验收。

### M6：recoverable handoff

状态：尚未实施/放行；入口为 91 B1–B6 全通过，不沿用 89 的撤回关闭判断。

- 状态机和 provider 增加 physical-slot ownership transfer，消费已经存在的 exact alternate before。
- fake/reference/provider 覆盖 prepare/claim/retag/commit/cancel、旧 binding 失效、ABA、source copy/transfer/swap/retire 冲突。
- 对比 FreshCow，证明没有额外复制 before 来制造命中。

### M7：bounded commit-only handoff

状态：尚未实施/放行；依赖 M6 和真实 install 无分配保证，执行/验收表见 91。

- 接入 capture gate 和全部目标 preclaim；首批只开放 packed write/full clear/fill/copy 与单页 commit-on-release adapter。
- 强制 §12 的 8 页/256 KiB 上限、预构造 `KisPreparedMutationCommit` 和 `postFirstByteFailures == 0`。
- 一般 callback、异步 GPU、未证明的多页失败语义保持 fresh/COW；不得为了命中率扩大 capability。

### M8：业务 scope、资格与删除旧路径

状态：后续必需阶段；M6/M7 完成不替代本阶段及正式 BR1-PERF。

- 保证一笔 undo transaction 每页 first-change 一次并跨 dab 复用 pending；intermediate display/save 使用明确 frozen version/last-use。
- 迁移剩余 brush/iterator/alias/source producer，完成 bounded multi-buffer、backpressure 和 close/drain。
- 全部生产入口迁到 canonical `beginMutation()` 后删除 `beginCpuMutation()`/`enableCpuWrites()` 兼容包装；backend `acquireWrite()` 只保留
  异步执行适配，并必须调用同一个 coordinator selector。
- 冻结同义 upstream，运行 M/K/X/E、命中率、RSS/arena slack、峰值 backing、capture fence 和尾延迟；安全 FreshCow 永久保留。

## 15. 清理方案与待清理内容

以下清理随 M1–M8 完成，不先删除仍保护正确性的路径：

1. **术语/API**：公共设计不再以可被调用方消费的 `InPlaceWritePermit` 或独立 owning `PreparedWritePlan` 为中心，统一为
   PageStore 私有 `KisPageWriteCoordinator + inline KisPageWritePlan + KisReplicaHandoffClaim`；历史 evidence 保留旧名。
   生产迁移完成后删除 `beginCpuMutation()/enableCpuWrites()`，只保留 `beginMutation()`；public API 不暴露 plan kind、commit-only flag 或 claim。
2. **强制独立 allocation 假设**：移除 native mutation 对 `target.allocation != source.allocation` 的永久硬编码，改由 plan mode
   和 physical-slot transfer 校验；FreshCow/FreshPayload/FreshDiscard 仍要求独立 target。
3. **重复 owner 状态**：`activeWritablePages/operationWritablePages/cpuMutationPages` 全部迁入一个 store-scoped
   `KisPageWriteAdmission`；provider 的 generic/native source、binding writer、TileData alias/ref 与 activeWriter 汇入同一个 physical
   allocation gate。业务范围预约、逻辑 writer claim、物理 owner ledger 保持三层而不互相冒充。
4. **metadata owning 容器**：删除 `VersionRecords::ordered/exact/slots/preparedByTransaction/mutableVersions/historical`、候选
   `std::list/std::map/shared_ptr<VersionRecords>` 和逐记录节点分配；snapshot 只作为边界值类型存在。
5. **session 页对象**：删除逐页 `std::make_shared<Page>()`、`pages/claimedKeys/removals/sources` keyed 重复所有权和 generation 级
   `QSharedPointer<KisCpuResidentBinding>`；保留一个 session private lifetime、连续 entries 和无 key map 的 sparse source set。
6. **legacy bridge 状态**：所有 iterator/painter/bulk 迁移后，收缩 `KisTile` 中 PageStore lease/cache/write-intent 兼容字段；
   legacy lock 只剩清晰的 adapter，不再是独立可见性 owner。
7. **source 旁路**：provider duplicate/copy/adoption、preclone、swap 和 retire 全部消费 allocation gate，删除仅检查 generic
   `activeWriter` 或裸 TileData pin 的旁路；公开/owner 层删除 `tryAcquireExclusiveWrite(counts)`，若 tiles3 内部继续使用，它只能读取
   provider 自己锁保护的 owner record，不能接收 PageStore 传入计数。
8. **无界容器**：retirement/history continuation/default cache/preclone/pending mutation 容器全部接预算或可证明的外部 retention；
   删除“后台处理所以无需上限”的假设。
9. **统计**：合并同义累计 counter，保留 live/peak/bytes、plan/fallback reason、arena slack 与完整 drain；字段重命名提供一次迁移。
10. **候选与 cleanup**：完成 `KisPreparedMutationCommit` 后删除 owner 内剩余可失败分配、候选大对象析构和重复目录/descriptor 构造；
   不为追求“不可失败”隐藏失败或预分配无限容量。
11. **binding/cache**：删除 generation 级 `QSharedPointer<KisCpuResidentBinding>` 和以 `replica()` 内部引用作为 cache 资格的接口；cache
    只保存 stable binding slot、directory generation、expected allocation generation，失配统一重新 resolve。
12. **测试脚手架**：把只验证“始终 COW”的断言改为按 plan 条件断言；保留旧 D11/D12 封存结果，不用新 binary 重写历史。
13. **CI 架构守卫**：禁止新增 PageStore 外部 physical handoff、直接 refcount 授权、页级 plan/shared binding 堆对象、未计量
    metadata/backing 容器和无预算 payload cache。

## 16. 完成定义

只有同时满足以下条件才可称 BR1 写侧基本重构完成：

- 无 history 的 resident current write 在无竞争常见桶稳定选择 handoff，零 before copy、零新 payload allocation；
- history/旧 View/可取消路径按需要一次 COW，像素、undo/redo/save 与 upstream 一致；
- 所有生产入口经过同一个 write-plan selector，剩余 legacy 路径有明确 adapter 和清理期限；
- backing 各分类的 live/peak bytes 可观测，tiny-budget 压力下不越界、不死锁、不丢历史；
- authoritative metadata 已迁入 typed generational slot arena，common record 内存达到 §12 目标，publication install 的
  allocator/rehash/large-destructor 计数为零，slot/block 回收无 ABA；
- session 热路径只有一个共享 private lifetime，无页级 owning plan、`shared_ptr<Page>` 或 generation 级 shared binding；
- post-first-byte 普通失败为零，capture/reader/last-use/alias/ABA 矩阵通过；
- retirement debt、history 和 close/drain 有进度与硬预算；
- 与固定 upstream 的 resident write、lazy COW、完整 stress、M/K/E 吞吐和尾延迟通过 39 的冻结门禁。

本文冻结设计，不授予当前代码 handoff、zero-copy、bounded-memory 或性能资格。
