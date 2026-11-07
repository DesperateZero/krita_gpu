> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 PageStore 拆分、冗余清理与侵入面审计（2026-09-21）

当前执行：**[90 基线冻结复核](90_br1_m5_baseline_freeze_review_20260925.md) / [91 条件实施计划](91_br1_m6_to_completion_entry_plan_20260925.md)。** M5-ready 未通过；三个反例修复并验证前不扩展 M6/M7。当前结构清单为 21 manifest、21 ownership facts、16 census groups、1461 APIs、13725 reverse-call edges、19 external files；43 unreached 仍是候选，不能当作死代码删除清单。清单通过不证明 failure atomicity 或 install 无分配。

以下开篇补记是历史复核顺序，本文的唯一权威、删除证据和 ratchet 规则继续生效。2026-09-25 早期执行为 [86 最终收敛方案](86_br1_m5_final_convergence_plan_20260925.md)。
[85 审计](85_br1_m5_code_readiness_audit_20260924.md) 重开并发 domain/生产预算验收；下文及
[84](84_br1_full_optimization_convergence_and_cleanup_20260923.md) 的批次完成标签是历史记录，不覆盖本次反证。
R0–M5 的局部实现与历史回归不等于整条管线已收敛。旧 M5B 标签调用图已确认过期，删除须使用重新生成的源码绑定证据。
审查包括 52 起 D1–D12/67 的旧优化，不局限 M1 以后；未发布旧协议按 84 的前后 gate 与迁移测试连续证明退出。

2026-09-23 第四批：无生产调用的独立 PageStore H/V LineIterator 原型整文件退出，原边界测试迁到真实 tiles3 入口；
CPU session 的 native/fallback 读获取与释放复用现有 `KisPageStoreReadPage`。未接线 schema 不再占据生产 entry，
删除前的构造/调用/override 子图和最终源码绑定 gate 见 [84 第四批](84_br1_full_optimization_convergence_and_cleanup_20260923.md)。

2026-09-23 第五批：调用图新增生产/测试/间接调用分开的可达路径和非生产强连通分量；
此图仍是当前编译配置的 PageStore 边界图，不是全程序、全配置死代码认证。模板依赖调用及隐式析构必须人工补证。
旧 Shadow 观察器和仅测试驱动的 metadata materialization 调度层退出；实际 default admission、request/lease、
verified completion 与状态机语义保留。逐函数裁决、迁移测试和删除前源码见 [84 第五批](84_br1_full_optimization_convergence_and_cleanup_20260923.md)。

2026-09-23 第六批：审查从零引用扩展到仍有调用的状态/资源读写链。entry 接管真实 guard 生命周期和别名输入，
删除 SourceSet/index、重复像素指针、cold 状态和长期 transition；源引用终结仍在 owner 锁外、admission 释放之前。
不把这些旧活代码称为死代码；替代关系、双架构布局和回归见 [84 第六批](84_br1_full_optimization_convergence_and_cleanup_20260923.md)。

2026-09-23 第七批：退出 Store 的 superseded-Prepared 清理函数、ReadCoordinator 反向回调与状态机专用分支；
native/generic 均 detach 到 Historical，由 HistoryCollector 判断回收资格。新 proof 失败保留旧 overlay，
读请求取消/解析失败补齐回收触发；旧调用图、逐项迁移证明与交叉寿命测试见 [84 第七批](84_br1_full_optimization_convergence_and_cleanup_20260923.md)。

2026-09-23 第八批：合并 Store 中三处 provider 拒绝后的锁外 `retireOrDefer` 执行；generic 分配的
预约丢失、校验失败和 metadata 拒绝不再维护三套退休/请求清理代码。新故障注入验证 provider 返还另一页
已存活 replica 时，拒绝此次写入且不误退休该页。源码净变化和仍需处理的 provider 入口见 [84 第八批](84_br1_full_optimization_convergence_and_cleanup_20260923.md)。

2026-09-23 第九批：native/generic Fresh provider 选择及私有发布转移复用 WriteCoordinator，
default/初始导入的异常 replica 身份也先核对再记账或退休；三条故障路径共用一个现存第 1 页
replica 的 provider 注入，证明没有误退休。删除未接线的写入枚举值和三个内部零引用访问器。
Clang 图漏掉模板实例化对 `PreparedPublication::backingAuthority` 的调用，构建捕获并恢复该方法；
零调用仍须全仓搜索、模板审查和完整构建三重确认。本批证据见 [84 第九批](84_br1_full_optimization_convergence_and_cleanup_20260923.md)。

2026-09-24 第十批：剩余四个未闭合门已按各自退出条件闭合。generic transfer 的全部异步语义进入
WriteCoordinator；fixed-K 控制曲线证明 CPU guard 的控制工作不随 N/H 放大；backing-domain 同步改为可确认的
P+K 增量 journal；真实 Store 有限失败矩阵补齐 Current/Pending/Debt/OptionalCache/SSD 与 drain/close。
双架构 CPU 正确性和 fresh graph/gate 一致；Vulkan foundation 构建还捕获并移除了对旧 `isKnownSource` API 的侵入，
改用 canonical whole-ticket status 校验后双架构契约各 14/14。R4/C3.4 仍保持局部：十组 CPU/tiles3 compatibility boundary 均有
生产调用和行为契约，不能按零引用或偏好性重写删除；C4.3 swap 前准入和 C5.5 正式性能/非 CPU 资格也仍为局部。
当前量化表与证据见 [84 第十批](84_br1_full_optimization_convergence_and_cleanup_20260923.md)。

2026-09-23 持续收敛：`CursorPage` 读复用 session 原有内联 cursor record，不再进入 operation-scope 的
`vector + QHash` 缓存；同页命中和跨页失败后释放旧 pin 由 CPU Mutation 测试复验。
RandomAccessor 的非 owning 热指针缓存与 session 的 owning pin 是不同责任，不能以名字相似直接删除。
`acquireReadInView` 不再把已捕获的 view 重新编码成一份 Committed/Exact selector；
Store 的共同 `acquireReadImpl` 直接验证 captured owner，并由 captured view 唯一解析 exact key/version 与 surface。
这只收掉重复 selector 表示，尚未证明整个 read fallback 层没有重复解析或控制成本。
本次图筛出的 `KisPageStoreRandomAccessor::oldRawData/x/y` 零直接生产调用是抽象 accessor 的 override；
`KisPageStoreReadCursor` 构造还被 tiles3 模板 header 中的 `make_unique` 使用。
二者均不能仅按 `.cpp` 直接调用计数认定为死代码。
另有一项经全仓引用确认的测试专属诊断：`KisPageStoreMementoManager::stats()` 及其
`KisPageStoreHistoryStats` 类型没有生产调用。保留 memento 行为/retained root 断言，删除这份重复统计出口，
并将 intrusion manifest 的 runtime-counter 映射改为现存 `KisPageStoreSessionStats`。
`WriteAdmission` 的 conflict 累计量同样只有测试读取且没有生产观测出口；删除其字段、三次冲突热路径写入与访问器，
保留 claim 冲突/重试的行为断言，不将丢失的测试专用计数伪装成性能收益。
同一规则继续应用到 R0 backend compatibility census：该快照及其 lease/anonymous/writer/iterator/refresh 字段只有
`testPageStoreCompatibilityCensus` 读取，却在真实热路径加锁写入；路径本身仍由 source-bound caller、RAII owner、
Store/Mutation authoritative snapshot 和成功/拒绝/取消/跨线程行为测试覆盖。因此删除 census、三个记录回调、
只为计数保留的 waits/newly-claimed 输出和 cursor `cachedPages()` 测试 accessor，并将测试改名为
`testPageStoreCompatibilityBehavior`。intrusion manifest/runtime census 对相关项明确标为 static-only 或映射到
`KisPageStoreSessionStats`/`KisPageMutationStatistics`，不再引用已删除的影子账本；真实 adapter 尚存，R4 不因此闭合。
Store 的 `cpuMutationStatistics()` 仅转发同类型的 `mutationStatistics()`，且实际计数已覆盖语义 remove/alias；
保留唯一 public 读口、删除旧别名，测试机械迁移到 canonical 名字。
随后按 68 §4.7 的最终 public surface 收掉 mutation factory 兼容层：`beginCpuMutation()`、`enableCpuWrites()` 和 backend
`beginCpuMutationBatch()` 已无源码定义或 caller，所有入口只创建 `beginMutation()` session。CPU provider policy 在首次像素
preflight 选择，semantic-only session 保持 provider-independent；两处 legacy wait/reentry 实现共用一个 Store-private gate。
这关闭的是旧 factory 包装，不代表 tile lease、iterator boundary 或 generic read adapter 已退出，R4/C3.4 仍为局部。
随后 operation-scope 写缓存退出每页 `shared_ptr<WriteRecord>`：连续 record 持有实际 guard/lease，
`QHash<key,index>` 只做定位；native cursor 仍只用内联 record，跨页容器搬移不移动 provider byte span。
metadata owner 路径的 read、default attach/materialize、verified last-use 共用局部投影安装；
跨历史的读 lease 冲突从 compact overflow 找见证，再由原 StateMachine 拒绝。
已终态 consumer last-use 的即刻 metadata acknowledge 若未接受，读服务保留 pending 记录供重试，
不再无条件移除。
另有未闭合的失败出口：generic `releaseLocked` 先向 provider 归还 access，再做 metadata `ReleaseRead`；
后者若因紧预算或状态失败，void Store API 已消费 lease。现由读服务保留已释放 provider access 的
active record/completion，只重试 metadata 终结，release/ack/close 入口会推进；这段按用户要求未做编译或故障注入，
因此共同 read scope 不等于释放终结协议已闭合，见 84 的 C3.1 降级。
随后 native mutation 析构失败由 Store orphan 表接管重试，captured view 部分释放失败由读服务继续持有版本、根快照和 Store 寿命；
abort/close 与后续快照释放接入推进。两处当前只有源码接线、尚未按用户要求运行编译或故障注入，不能把 C2.5/C3.2 记为闭合。
fallback 读的 resolve→cancel 失败也在读服务内保留取消意图，后续 acquire/close 推进；transaction abort 或显式重试成功会删除对应队列 ID。
关闭阶段不再调用全页 `pageSnapshots()` 枚举 replica，而从 compact record 只输出 handle；Store 仍按原物理身份去重并退休，
但此修改尚未运行用户当前禁止的编译/测试，不据此关闭 C5.1。
Debt 准入失败且同步退休未终态时，退休队列现在保留原 backing 类别或孤儿预留凭据与 provider operation，
在 process/close 等同步推进点重试；不会自行进入后台 ready 队列。暴露前 escrow 与有限限额故障矩阵仍未闭合。
后续补齐同步重试/close 的执行前 Debt 准入，避免共享 alias 尚存时按旧类别直接释放；首次失败的预留凭据
随 record 保留并优先复用；票据不能覆盖共享 alias 所需类别时再尝试正常准入。共享物理 backing 新 alias 若提升类别，
登记时完成 charge 转账。均未经过本轮编译/测试，
不能据此关闭有限预算门。
Store 的 exact read 和默认页准备另有五处只消费一个 version 的全页 `pageSnapshot`，现改成单版本投影；
`versionSnapshot` 不再把普通读计入 mutation-base 工作量。获取/物化回归在释放 lease 前断言
`fullSnapshotExports` 不增长。同步 HistoryCollector 后续也退出全页 snapshot：只枚举页键，
按页用最多 32 个 Historical 版本的切片，并以同样粒度分别安装 discard；与后台路径共用退休资格函数，
释放后回归确认前台全页导出不增长。受限 transient 准入也已改为 exact target、页内 mutable 计数及
Retiring 紧凑记录扫描，不再导出整页版本。
随后移除 metadata publication 的 fused idle-history 快捷路径：Store 不再选用它，StateMachine 的复合转移、
整页候选/替换安装及 discarded-version 回传均退出；普通 commit 的历史退休统一交给 HistoryCollector。
保留测试 full-snapshot oracle，并增加普通 commit 在长历史下只输入相关版本的对照。此修改尚未编译/测试，
不能据此宣布 C5 闭合。
owner API 随后禁止非局部转移默默落回整页 `applySequence`；参考 commit 测试改走 prepared publication，
零引用的批量整页接口与测试独用的 `pageSnapshots` 便利函数均退出。单页诊断 snapshot 仍作为 oracle 保留。
prepared commit 候选再退出未被安装读取的 proof descriptor 列表、只供诊断的 transition 向量和调用者已有的 proof 副本；
removal 与 restore-default 的 descriptor/version 平行向量改为成对记录，再与 default replacement 共用一份候选安装表。
输入预检借用 owner-gated transaction state，不再复制三种容器；元数据候选准备后在 owner 锁外释放转移输入，
descriptor 安装的容量断言允许其他候选并发扩容；并发 proof/descriptor 和 deferred cleanup 的预算门仍待核验。
另将仅测试引用的 `KisPageStoreCpuSurfaceOps`、`KisPageStoreCheckpointCodec`、
`KisPageStoreRandomAccessor` 及其底层 `KisPageStoreCpuAccessSession` 从生产编译目标迁到测试支持库，
保留原测试语义；1,663 行属于源码搬迁，不能充作全仓净删。真实 tiles3 adapter/compat 仍未完成闭合。
这移除了上述转移及读获取入口的全页 snapshot/assign，但 lease 见证仍线性扫描历史，
同步 GC 一批的总历史遍历、reachability 集合与 effects 仍未总量限额化；C3 固定 K/H 成本及 C5 全路径 compact
权威未验收，详见 [84 逐门表](84_br1_full_optimization_convergence_and_cleanup_20260923.md)。
owner ledger 的另一处无关 N 扫描位于共享物理 backing 的代表退休：原来扫描全部逻辑 backing 寻找替代者，
现仅为存活 alias 数大于 1 的物理 backing 建成员索引，退回单成员即释放。此索引不承担预算分类权威，
也不解决 reserve 时的全物理 backing domain 扫描。
随后按类型截肢门删除 `PreparedRestore`、provider-specific config alias、`KisPageMetadataGlobalMetrics`、
`KisPageWriteExposureKind` 与无读取的 `KisSurfaceRole`；保留的低引用 snapshot/DTO 均能追到唯一统计、生命周期或
fail-closed 事实，不改写成 `pair/out-param`。C4.5 的长期集合也完成替代后删除：resident provider 防重放使用固定
4096-bit 滑动窗口；default cache/preparation 保持 64 entry、8 MiB/64 entry 上限；HistoryCollector 只允许 16 个
持有 reachability 副本的 active work slot，pending/deferred 继续按已注册 PageKey 去重。详见 84 的逐门表。

2026-09-22 完成证据见 [70](70_br1_r0_containment_and_layout_gate_20260921.md)、
[71](71_br1_r0_runtime_census_and_test_binding_20260922.md) 与
[72](72_br1_r0_reverse_callgraph_and_closure_20260922.md)。R0 完成不改变本文 §9 的删除门槛，也不授权 68 M1–M7。
R1 前两项实现与验证见 [73](73_br1_r1_default_storage_extraction_20260922.md) 和
[74](74_br1_r1_retirement_queue_extraction_20260922.md)；`HistoryCollector`、`ReadCoordinator`、`PublicationCoordinator` 与 R1
整体收口证据见 [75](75_br1_r1_history_read_publication_extraction_20260922.md)。R2/M1 compact record 证据见
[76](76_br1_r2_m1_compact_metadata_records_20260922.md)。
R2/M2A shard arena 迁移证据见 [77](77_br1_r2_m2a_shard_metadata_arenas_20260922.md)，M2B 锁外 growth 与类型对照见
[78](78_br1_r2_m2b_lock_external_metadata_growth_20260922.md)，M3A shard index/intrusive record 证据见
[79](79_br1_r2_m3a_shard_indexes_and_intrusive_records_20260922.md)，M3B compact page/activity 与 M3 收口证据见
[80](80_br1_r2_m3b_compact_page_activity_20260922.md)，M4 allocation-free publication、prepared commit 与 side-map 收口证据见
[81](81_br1_r2_m4_allocation_free_publication_20260922.md)。R3/M5A write schema、admission 与 backing budget 证据见
[82](82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md)。
M5B store/session 迁移检查点见 [83](83_br1_r3_m5b_store_session_write_migration_20260923.md)。

本文补充 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 的实现边界。
68 冻结 write plan、metadata arena、backing handoff 与预算；本文冻结 `KisPageStore` 系列类如何拆分、
PageStore 对 tiles3/iterator/painter 的侵入如何登记和退出，以及旧路径何时才允许删除。

## 1. 结论

1. 本次结构重构前需要一个独立的 **R0 containment/audit** 阶段，但不进行“大扫除式”语义改写。
2. 先删除目前看起来重复的 map、lease、锁或 tile 字段不安全。这些结构中有些确实重复，有些仍是唯一承载
   transaction claim、old-data view、nested lock、cancel、last-use 或 retire 义务的地方。
3. R0 只允许删除已经同时满足静态、动态和所有权证明的死代码；其余内容先登记 owner、替代类型和退出门槛。
4. `KisPageStore.cpp` 应收缩为公共 facade 与 composition root。read、write、publication、default、history GC 和 retirement
   分别由 store-private、非虚、非 `QObject` 的服务类承载；服务对象按值嵌入 `KisPageStore::Private`，不得逐页创建 manager。
5. `KisTiledDataManagerPageStoreBackend` 最终只做 tiles3 语义适配，不再保存第二套 writer/admission/publication 状态。
6. `KisTile`、iterator 和 painter 中的 PageStore 代码现在要登记为 compatibility intrusion；在 canonical coordinator 接管前保留，
   接管后按清单逐项删除。不要用散落 TODO 代替清单。
7. 可靠排查不能只靠 `rg`。必须组合 frozen diff、编译数据库上的 symbol/reverse-call graph、状态所有权矩阵、运行时路径计数、
   failure injection 和差分 oracle。

## 2. 当前量化基线

本轮以 Krita 内层仓库 `f5fbbde618`（`vulkan: establish BR0 foundation on current upstream`）为冻结比较点。
当前 BR1 工作树尚未形成单一提交，因此审计工具必须同时纳入 `git diff HEAD` 和 `git ls-files --others --exclude-standard`；
只看 tracked diff 会漏掉新建的 PageStore 实现。

### 2.1 规模

| 范围 | 当前有效行数 | BR0 对照 | 结论 |
|---|---:|---:|---|
| `libs/image/pagestore/*.{h,cpp}` | 24,742 | 2,787 | BR1 净增约 21,955 行，绝大多数仍未提交 |
| `KisPageStore.cpp` | 5,522 | 114 | 已同时承担 facade、读写协议、事务发布、GC、retire、default 和统计 |
| `KisPageStore.h` | 558 | 55 | public API、兼容 API、RAII guard 和多类统计混在同一头文件 |
| `KisTiledDataManagerPageStoreBackend.{h,cpp}` | 2,510 | 不存在 | adapter 内又形成 transaction/write admission/lifetime coordinator |
| `KisPageMetadataCoordinator.{h,cpp}` | 2,132 | 不存在 | canonical metadata 与 snapshot/prepared container 表示混合 |
| `KisImageEpochReferenceModel.{h,cpp}` | 1,829 | 不存在 | 事务 root、retention、restore 的真实语义，不应按文件长度直接删除 |
| `KisPageStateMachine.{h,cpp}` | 1,674 | 134 | reference transition 与 production snapshot 投影均在此增长 |
| `KisTiles3PageReplicaProvider.{h,cpp}` | 1,190 | 不存在 | provider 域 allocation/lease 状态，需与 store owner ledger 对齐 |

BR0 之后，`libs/image/pagestore` 之外的 `libs/image` 生产文件有 **35 个**被修改，累计新增 1,948 行、删除 342 行。
按侵入区域分组的 tracked 增量为：

| 区域 | 新增 | 删除 | 主要风险 |
|---|---:|---:|---|
| `KisTiledDataManager*` | 813 | 153 | 第二套 transaction/batch/default/history 路由 |
| `KisTile` | 346 | 3 | PageStore lease/cache/write-intent 进入底层 lock/unlock 生命周期 |
| iterator/accessor | 215 | 61 | read scope、cursor 和 write-boundary callback 分散到每种遍历器 |
| tile storage/swap/hash | 293 | 25 | physical owner、swap 和 backing 生命周期出现旁路 |
| painter/paint-device 等调用方 | 246 | 97 | 上层开始感知 PageStore operation/diagnostic 类型 |
| memento | 18 | 3 | history bridge 与 canonical epoch 的适配 |

上述数字是改动面，不是冗余行数。它们用于确保审计不遗漏侵入文件。

### 2.2 `KisPageStore.cpp` 当前责任分布

以下区间来自当前源文件，是拆分输入，不是永久行号 ABI：

| 当前区间 | 约行数 | 内容 | 处理方式 |
|---|---:|---|---|
| 1–383 | 383 | request/lease/default/retire/deferred-cleanup 记录 | 搬入对应服务；合并重复记录 |
| 384–1379 | 996 | `KisPageStore::Private` helper、default、retire、history GC、descriptor | 拆成五个 store-private 服务 |
| 1380–2230 | 851 | mutation session、write guard、native write 准备/封口 | 由 68 的 write coordinator/write set 替换 |
| 2231–2459 | 229 | 统计、captured view、read guard | 搬入 read coordinator；公开 guard 保留 |
| 2460–3071 | 612 | configure/close/provider/adopt/resolve | facade 与 composition root 保留，细节下沉 |
| 3072–4479 | 1,408 | generic acquire/resolve/cancel/release/archive/publish | 读写分别归一到 read/write coordinator |
| 4480–5522 | 1,043 | transaction、surface/default/remove/commit/restore/abort | 搬入 publication coordinator |

目标不是把 5,522 行机械切成多个同样耦合的文件。每个迁移步骤必须同时消除重复 owner 或建立单一 delegation，
否则只算移动代码，不算结构改善。

## 3. “冗余”必须分四类

### 3.1 D0：已证明死代码

只有零 production caller、零运行命中、无独占 ownership fact、无序列化/ABI 义务且已有等价测试的代码属于 D0。
**当前审计尚未对任何生产块完成全部证明，所以当前可认证直接删除量是 0。** R0 完成后预计只会得到低数百行量级，
不能把它当作主要收益来源。

### 3.2 D1：重复表示，必须随替代类型原子删除

已经确认的结构重复包括：

- store 内 `mutationPreparations/genericWriteTransactions/controlWritePages/mutationTransactions/mutationPages` 与 backend 内
  `activeWritablePages/operationWritablePages/cpuMutationBatches/cpuMutationPages` 分别表达相交的 transaction/page writer 事实；
- `preparedProofs/synchronousHostCompletions/preparedSurfaceChanges/stagedPageRemovals/descriptors` 与 metadata publication candidate
  分开保存一次提交的侧表；
- `VersionRecords` 同时持有 `ordered/exact/slots/preparedByTransaction/mutableVersions/historical`，prepared publication 又复制
  snapshot、addition 和 replacement records；
- tiles3 lease 同时支持 native borrowed mutation、native owned mutation、generic read 和 generic write 四套终结协议；
- mutation session 用 `pages/claimedKeys/removals/sources` 多个 keyed 容器表达同一 write set。

这些结构不能先删。68 的 `KisPageWriteAdmission`、`KisMutationWriteSet`、`KisPreparedMutationCommit`、metadata slot arena 和统一
coordinator 生效并通过等价验证时，旧表示必须在同一里程碑删除，不能长期双写。

### 3.3 D2：真实职责位于错误 owner

retirement、history reachability/GC、default buffer/materialization、captured read、generic request 和 transaction publication 都是
真实功能。它们导致 `KisPageStore` 膨胀，但搬出后总行数不会等比例减少。D2 的目标是缩短锁域、明确生命周期和可单独测试，
不能按“删行”评价。

### 3.4 D3：兼容与侵入代码

`KisTile` 中的 PageStore read-ready/old-data/write-lock/lease 状态、iterator write-boundary registry、data manager 的 anonymous
transaction/batch、painter 的 PageStore-aware operation 都属于 D3。部分最终会消失，部分会收敛成窄 adapter。

基于当前结构，重构资源规划可暂按 **2,500–4,500 行现有代码最终净删除**、**6,000–9,000 行职责迁移或重写**估算；
前者约占当前 `pagestore/` 的 10%–18%。这只是规划区间，不是已经证明可删的行数，也不允许作为验收指标。
最终数字由 §8 的 manifest 和删除门槛产生。

## 4. 目标类与唯一职责

下列类名、所有权和边界作为实施口径锁定。除公开 RAII facade 外，它们全部位于 `pagestore/*_p.h/.cpp`，为 `final class`，
不继承 `QObject`，不可复制，不使用 virtual dispatch，不按页分配 service 实例。

| 最终类型 | 存储方式 | 唯一职责 | 明确禁止 |
|---|---|---|---|
| `KisPageStore` | public facade | 稳定 API、参数校验、转发与 session 生命周期入口 | 保存 page/transaction 容器或实现 provider 算法 |
| `KisPageStore::Private` | `KisPageStore` 唯一 heap pimpl | composition root、configure/close 状态与服务析构顺序 | 重新吸收 read/write/GC helper |
| `KisPageReadCoordinator` | `Private` 内按值 | captured view、resident exact read、generic read request/lease、release | 写计划、root publication、history GC |
| `KisPageWriteCoordinator` | `Private` 内按值 | 68 定义的 selector、admission、write set、prepare/install delegation | 公开 permit、第二套 provider owner ledger |
| `KisPagePublicationCoordinator` | `Private` 内按值 | stage surface/default/remove、commit/restore/abort、prepared commit 安装 | 像素写入、provider allocation、后台 GC |
| `KisPageDefaultStorage` | `Private` 内按值 | virtual default buffer cache、default materialization 去重与预算 | 修改 epoch root 或决定写许可 |
| `KisPageRetirementQueue` | `Private` 内按值 | completion-qualified retire/defer、批量 worker、drain/close | history reachability、发布新版本 |
| `KisPageHistoryCollector` | `Private` 内按值 | retained-root reachability、增量 scan cursor、历史版本回收候选 | 自行 retire replica 或发布 root |
| `KisPageMetadataCoordinator` | `Private` 内按值 | authoritative version/replica records、stable-slot arena、索引和 transition | transaction policy、tiles3 类型、业务 callback |
| `KisImageEpochReferenceModel` | `Private` 内按值 | epoch root、transaction base/delta、retention/restore 的 reference truth | provider/binding/physical allocation |
| `KisPageOwnerLedger` | `Private` 内按值 | provider 注册、operation token、completion/proof authority | 保存第二份 page state 或 writer admission |
| `KisTiledDataManagerPageStoreBackend` | data manager 独占 | tiles3 identity/default/history 与 PageStore API 的窄适配 | active page writer 集合、独立 selector、独立 publication protocol |

内部服务通过构造函数引用 `metadata/epochs/owner/completions`，引用对象先构造、后析构。服务不得拥有彼此的 `shared_ptr`，
不得通过 callback 形成生命周期环。公开 guard/session 只共享其明确需要跨调用栈存活的 control block；page record、plan、binding 和
maintenance job 不因为拆分类而获得新的逐项 heap 对象。

### 4.1 `KisPageStore::Private` 最终保留内容

`Private` 只保留下列内容：

- lifecycle/configuration state 与一次配置后只读的 provider directory；
- `KisCompletionRegistry` 及上述服务对象；
- store 级 monotonic id/source；
- close/drain 的拓扑顺序；
- 各服务统计 snapshot 的无副作用聚合。

`requests/activeReads/activeWrites`、history 四队列、default cache、retirement 双队列、prepared side maps 和 mutation page maps
不得继续直接出现在 `KisPageStore::Private`。

### 4.2 公开头文件边界

`KisPageStore.h` 最终只声明 `KisPageStore`、`KisPageMutationSession`、`KisCapturedReadView`、CPU read/write guard 和必要的公开统计值。
private helper、legacy unlock、provider-specific friend 和内部统计结构移入私有头。兼容 API 在 manifest 中登记删除里程碑；
不能为了减少当前 diff 永久留在 public header。

## 5. 当前代码的拆分归属

| 当前状态/代码 | 新 owner | 处置 |
|---|---|---|
| `requests/activeReads`、read resolve/release | `KisPageReadCoordinator` | 机械迁移后与 resident read 共用 exact-version 验证 |
| `activeWrites/genericWriteTransactions/controlWritePages` | `KisPageWriteCoordinator` + `KisPageWriteAdmission` | transaction activity 与页级 claim 已迁；`activeWrites` 仍是 lease 生命周期而非第二份页准入 |
| `mutationTransactions/mutationPages` | `KisPageWriteAdmission::ClaimSet` | store 侧已退役；backend 三套 writable-page map 仍待迁移 |
| prepared proof/completion/surface/removal side maps | `KisPreparedMutationCommit` + `KisPagePublicationCoordinator` | M4 install 完成后原子替换 |
| default buffer/order/preparation | `KisPageDefaultStorage` | 增加硬 bytes/entry budget 和关闭 drain |
| pending/ready retirement queues | `KisPageRetirementQueue` | 保留 completion 和 provider epoch 校验 |
| deferred/pending/ready/queued history GC + scans | `KisPageHistoryCollector` | 合为有明确状态的 work item/cursor，不丢进度 |
| descriptor map | metadata authoritative record / prepared commit | arena 接管后删除 store 侧表 |
| session `shared_ptr<Page>` 与四容器 | `KisMutationWriteSet` | 已替换为连续 entry、稀疏 cold/source side slot 与 ClaimSet；待完整回归 |
| backend anonymous transaction/lease | adapter RAII handle | 只描述 legacy 调用范围，不再授予 page writer |
| backend iterator boundary callbacks | operation-scoped write batch | 调用方迁移后删除 registry |
| tile PageStore flags/lease vector | compatibility intrusion | 先登记；canonical cursor/guard 覆盖所有生产入口后缩为单一窄 bridge 或删除 |
| painter/strategy PageStore 类型 | generic pixel operation facade | 保持上层不感知 generation/claim/provider |

## 6. 重构前允许和禁止的清理

### 6.1 R0 可以做

- 删除满足 §9 全部条件的 D0；
- 合并完全同义且已有全调用方迁移的 alias/overload；
- 将大函数机械搬到已冻结 owner，并保持调用顺序、锁顺序和错误结果不变；
- 为兼容路径增加可归零的运行计数和 failure-injection 点；
- 建立外部侵入 allowlist/ratchet，禁止范围继续增长；
- 补齐行为 characterization test，不为当前实现细节写同义测试。

### 6.2 R0 禁止做

- 因为两个容器 key 相同就删除其中一个；
- 同时改变 owner、锁域、错误回滚和物理 backing 策略；
- 先删 tile/iterator bridge，再用裸 `TileData` 引用计数猜写许可；
- 保留新旧状态双写跨越多个里程碑；
- 用代码内大量 `TODO`/`legacy` 注释代替外部 manifest；
- 为拆分类引入 `QObject`、virtual interface、逐页 `shared_ptr` 或 sidecar heap manager。

## 7. 侵入面如何标记

不在每个分支前散布标签。维护一个机器可读 manifest，每项至少包含：

```text
id
path
symbol
category = canonical | misplaced | duplicate | compatibility-intrusion | test-only
facts-owned = [transaction-claim, page-writer, read-pin, old-view, last-use, ...]
current-owner
target-owner
replacement-type
static-callers
runtime-counter
failure-tests
remove-after
status = inventoried | delegated | callers-migrated | quarantined | removable
```

只有 compatibility boundary 本身允许一条统一格式的源码注释，写明 manifest `id` 和退出里程碑；内部每个 if/map 不重复标记。
manifest 的路径和 symbol 必须由工具验证仍存在，已删除项保留 tombstone 一轮，以避免同一兼容路径换名字后重新进入。

首版 manifest 至少覆盖：

- `KisTile` 的全部 `m_pageStore*` 字段及 lock/unlock 分支；
- `KisTiledDataManager` 的 configure/clone/history/default/clear/copy/read/write/iterator 接入；
- backend 的 anonymous transaction、四种 lease mode 和 writable-page maps；
- iterator/accessor 的 read scope、cursor、write-boundary callback；
- painter/paint-device strategy 的 operation 和 diagnostic 接入；
- TileData/store/swap 中新增的 owner、pin、swap 与 exclusivity 分支；
- Vulkan/provider 对 PageStore generation、last-use 和 retirement 的直接引用。

## 8. 可靠排查流程

### 8.1 Frozen source inventory

生成 `baseline-source.json`，记录：

- baseline commit、dirty worktree source hashes、编译配置和 `compile_commands.json` hash；
- tracked diff 与 untracked source 的并集；
- 每文件行数、公开类型、成员字段、容器、mutex/condition 和 include edge；
- PageStore 标识符出现在允许目录外的全部 symbol，而不只是文件名。

每个里程碑重新生成并与 baseline 做 set difference。CI 先采用 ratchet：现有侵入可暂存，但文件、symbol、field、direct include 数不得增加；
每清掉一项就降低基线，不能回升。

### 8.2 Symbol 与 reverse-call graph

`rg` 只用于发现候选。删除判断使用编译数据库上的 Clang AST/index，覆盖 overload、template、function pointer、virtual override 和宏展开；
输出每个 public/private PageStore API 的 production caller 与 test-only caller。无法由静态图解析的 callback 必须在 manifest 中显式登记注册点。

### 8.3 State ownership matrix

为下列事实逐项列出唯一 authoritative owner、只读 observer、写入点、锁/claim、创建与全部 terminal path：

```text
transaction lifetime
page writer admission
pending generation
physical allocation owner
read pin / writable pin
captured/retained exact version
provider operation
GPU/I/O last-use
retirement debt
history reachability
default source/materialization
binding/cache validity
```

同一事实存在两个 writer 时必须先统一 owner；只有一个结构保存额外且仍被读取的事实时，它不是冗余。

### 8.4 Runtime path census

为 generic/native/legacy lease、anonymous transaction、iterator boundary、tile refresh、fallback COW、default materialization、
history scan 和 deferred retirement 建立 operation-level 计数。代表性测试和 trace 必须报告：

- path hit/operation/page 数；
- live/peak entry 与 bytes；
- terminal success/cancel/failure/drain 数；
- fallback reason；
- 理论应归零的 compatibility counter。

计数用于证明路径是否仍在使用，不能单独证明可删；零命中还需静态 caller 和 ownership matrix 同时通过。

### 8.5 Differential 与故障验证

- PageStore disabled/upstream、当前实现和重构实现运行同义 M/K/X/E workload；
- reference state machine 比较 page/version/root/history/default；
- 在 allocation、claim、metadata prepare、provider completion、root install、cancel、retire、close 每个失败点注入错误；
- tiny metadata/backing budget 与慢 reader/retirement 验证无界队列和隐藏 owner；
- TSAN/ASAN/UBSAN 只作补充，不能代替确定性顺序测试。

### 8.6 Architecture guards

R0 增加独立 PageStore 架构检查，并从 audit-only 转为 CI ratchet：

- 禁止 allowlist 外新增 PageStore direct include/type；
- 禁止在 `KisTile` 新增 `m_pageStore*` 字段或 owning lease container；
- 禁止在 adapter/provider 新增 page-writer/admission map；
- 禁止用 TileData ref/usersCount/swapLock 直接授权 PageStore write；
- 禁止页级 owning plan、generation 级 shared binding 和未计量 payload/metadata 容器；
- 强制 manifest 中的 path/symbol 存在性、状态单调和删除里程碑。

## 9. 删除门槛

一个旧 symbol/field/container/path 只有同时满足下列条件才可删除：

1. production reverse caller 为零，或所有 caller 已显式委托给 replacement；
2. state ownership matrix 中没有它独占的事实；
3. reference/differential/failure tests 覆盖原成功、取消、失败和 close 路径；
4. 对应 runtime counter 在冻结 workload 中为零，且 counter 自身覆盖入口而非抽样；
5. 新 owner 已有 live/peak/budget/drain 可观测性；
6. 静态 architecture guard 已禁止旧模式重新出现；
7. 先进入一个里程碑的 `quarantined` 状态，再物理删除；若该里程碑不发布，可用连续两次完整 gate 代替。

删除提交必须同时移除旧状态写入、旧状态读取、兼容 fallback、统计和测试期望。只断 caller 而留下双写容器不算完成。

## 10. 实施顺序

### R0：containment/audit

冻结 source inventory、manifest、reverse-call graph、ownership matrix、运行计数和架构 ratchet；只删 D0。
这是 68 M0 的组成部分，完成前不开始 handoff 或 metadata 表示替换。

状态：**2026-09-22 已完成。** 全部产物已冻结；物理写门虽无 production caller，但 ownership 仍为 `split`，因此本轮没有 D0。

### R1：无语义改变的职责拆分

按 `DefaultStorage -> RetirementQueue -> HistoryCollector -> ReadCoordinator -> PublicationCoordinator` 顺序搬出 leaf/service；
每次只改变一个 owner，保持结果、锁序和统计等价。`KisPageStore::Private` 在每一步减少直接容器。

状态：**2026-09-22 已完成。** 五个 service 均为 final、非 `QObject`、由 `KisPageStore::Private` 按值嵌入；
history/read/publication 的直接容器与算法已从 facade 移出，架构 ratchet 禁止回流。R1 不改变 publication 语义。

### R2：metadata M1–M4

执行 68 的 authoritative record/snapshot 分离、stable-slot arena、intrusive index 和 allocation-free publication。
旧 `VersionRecords` 与 publication side maps 在 replacement 通过 gate 的同一里程碑删除。

状态：M1–M2 已完成；`KisVersionRecord/KisReplicaRecord/KisMetadataOverflowNode` 已成为三个 shard-owned typed arena 中的权威
record，typed slot/block generation、hard budget、empty-block return、footprint 与 snapshot round-trip 门禁已建立，旧
`VersionRecordNode` owning node 已删除。生产 block growth 已改为锁内 demand、锁外 candidate allocation、relock revision/claim
复验与锁内 attach；allocation-count/memory/K1/K16/H 基线已冻结。M3A 已删除 `VersionRecords` 及 page-local
list/map/hash/set，两个 shard-global slot index、reservation token、intrusive version/history/mutable 链和 revision cursor 已接入。
M3B 已删除 public snapshot header，`MetadataPage` 收敛为 96 B，writer/handoff/materialization/claim 进入 shard 级稀疏 compact
activity。M4 已把 arena/index/activity capacity 前移到 metadata prepare，以 outer `KisPreparedMutationCommit` 聚合 metadata、
commit/restore root、proof/descriptor/completion 和 cleanup，删除四套平行 transaction publication side maps，并冻结无 reserve/attach/
snapshot/upsert 的 install 门禁；历史证据见 [81](81_br1_r2_m4_allocation_free_publication_20260922.md)。R2/R3 的局部实施不代表全链路收敛，
当前先按 [84](84_br1_full_optimization_convergence_and_cleanup_20260923.md) 清理与验收，不直接进入 M6。

### R3：write M5–M7

统一 native/generic/legacy 写入到 `KisPageWriteCoordinator + KisPageWriteAdmission + KisBackingBudgetController`；
先保持 Fresh 路径，再开放 recoverable/commit-only handoff。backend writable maps 与 session keyed 重复容器在此退出。

状态：M5 的全链路验收已重开，以下保留历史实施记录；当前完成门槛与未闭合问题见 84。
后续连续清理又去掉 prepared commit 的 `restoration` 重复状态，并把 Memento 的 active/retained-root
释放改为逐 token 成功后撤销的可重试持有记录；这是局部生命周期收敛，不改变 M5 未验收或 M6 未实现的判断。
M5A 已把 68 冻结的值类型、move-only entry/claim/reservation、inline/sparse write set、全取或全不取
admission、generational budget slot 和 fresh-only selector 作为 `Private` 的按值服务落地；证据见
[82](82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md)。M5B 进一步把 store/session/backend writer owner 收敛为单一
`KisPageWriteAdmission + KisMutationWriteSet`，删除 `controlWritePages/mutationPages`、session 四容器与 backend
`activeWritablePages/operationWritablePages/cpuMutationPages`；退役在 metadata detach 前预占 Debt，owner ledger 以 provider physical token
对共享 alias 去重并同步 CPU/SSD domain。迁移后的 failure/competing-writer/semantic-ordering、PageStore、tiles3、CPU baseline 与架构
ratchet 均通过，证据见 [83](83_br1_r3_m5b_store_session_write_migration_20260923.md)。M6 handoff 仍未实现。

### R4：侵入清理与 M8

按 backend -> data manager -> iterator/accessor -> tile -> painter 的 caller 方向收缩兼容层。每移除一项即降低 CI ratchet；
最后删除 `beginCpuMutation/enableCpuWrites/sealForLegacyUnlock` 等兼容 API，并把 `KisPageStore.h` 收回稳定 facade。

当前连续收敛已先完成一个可静态证明的 R4 子项：tiles3 backend 只构造 capability 固定为
`nativeCpuMutation=true` 的 `KisTiles3PageReplicaProvider`，所以其 legacy single-tile 写中的 generic
`KisWriteLease` fallback 永不可达。该 constructor、finish/cancel 协议、census 类别及 Store 的
`acquireWriteFromLegacy` reservation 入口已一起退出；通用 `KisPageStore::acquireWrite` 异步 API 保留为独立
provider 边界。generic read 冷页回退与其他真实 adapter 尚未退出，因此 R4 仍在进行中。

随后 batch facade 也只剩 canonical mutation 入口：删除裸 `beginWriteBatch()`、逐页
`replaceFullTileInTransaction()` 以及 Store 的 legacy removal 旁路；full-tile alias/removal、partial write、packed/planar operation
现在共享一个 mutation/write-set owner。单页 lease 不再经独立 reservation 中转，lease wrapper 也不再为 move-only capability
分别分配 `unique_ptr`。Admission 的等待只存在于能分类冲突的 adapter preflight，内部从未使用的 `Wait` 分支与重复 claim kind/count
退出。generic read、iterator scope、legacy unlock 和 tile ABI wrapper 仍是真实兼容责任，因此本项只推进而不关闭 R4/C3.4。

R2 的后续收敛也已删除一个被旧调用图掩盖的第二权威：公开 `KisPageMetadataCoordinator::apply()` 没有
production caller，却仍执行完整 snapshot→StateMachine→整页 assign。reference tests 现改走同一个 projected
owner 路径，commit 改走 prepared publication；完整 snapshot 只作只读 oracle。CI 架构检查新增禁止该全页
transition writer 回流的规则。由此 compact arena record 是唯一存储权威，局部转移与原子 batch 只按生命周期
边界分流，不再各自维护一份全页写回语义。

继续逐函数/字段引用审计后，backend 的 generic read 与 clone 已改走同一个 `KisPageStoreReadPage`，不再手写第二套
request/resolve/cancel/release；iterator write boundary 和 backend 内部 CPU operation 也不再叠加动态类型擦除。
epoch commit/restore 的 root 槽取消及安装协议合并为一个 move-only reservation/installation owner；只有一个取值的
transition-effect kind 及其三个永真消费者分支退出。零调用观察器、无消费者累计字段、shadow count 和纯 forwarding
implementation 同批删除。后续又删除了上层 count-authorized physical exclusive、binding 完整 handle/内部引用出口和
Tiles3 access/writer 影子状态；provider exact allocation、tile cache/lease、transaction delta、proof/snapshot 定位各自只留
一处权威实现，metadata/commit 的 identity/physical-slot/surface-proof 多处 K² 查找改为事务内临时索引。当前 PageStore
`.h/.cpp` 为 27,741 行；本轮尚未运行构建、测试或重新生成 reverse graph，
R4 仍不把真实 generic read/tile/iterator ABI adapter 误标为已删除。

## 11. 完成定义

- `KisPageStore.cpp` 只包含 facade/composition/lifecycle，不再直接拥有 §4.1 禁止的容器；
- 每个状态事实只有一个 authoritative writer，adapter 只持 RAII handle 或不可变 identity；
- `KisTiledDataManagerPageStoreBackend` 不保存 page writer 集合或独立 write selector；
- allowlist 外没有新增 PageStore 类型侵入，已有 manifest 项全部为 canonical、quarantined 或已删除；
- 无逐页 manager/plan/shared binding heap allocation，metadata/backing/maintenance queue 都受预算；
- 所有删除项满足 §9，并通过 68 与 39 的正确性、压力、性能和内存门禁。

文件变短只是结果。验收看 owner 是否唯一、兼容路径是否可证明退出、预算是否封闭，以及生产入口是否统一。
