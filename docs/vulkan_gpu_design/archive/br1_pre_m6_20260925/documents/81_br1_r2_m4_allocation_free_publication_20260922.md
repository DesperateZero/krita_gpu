> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R2/M4 allocation-free publication install（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。 M4 install 零分配结论已由 90 的 M4-R1 重开。

状态：**M4 已完成，R2 已关闭；后续 M5A 已完成，见 [82](82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md)。本文不授权 backing handoff。**

本文记录 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) §4.5、§5.4、M4 与
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R2 的实施结果。M1–M3 的 compact record、arena、index、intrusive
ordering 与 compact page/activity 前置条件分别见 [76](76_br1_r2_m1_compact_metadata_records_20260922.md)–
[80](80_br1_r2_m3b_compact_page_activity_20260922.md)。

## 1. 与 68 冻结类型的边界比对

文档 68 明确要求 `KisPreparedMutationCommit` **聚合而不替代** metadata `PreparedPublication` 和 epoch candidate。实现据此保持三层：

| 冻结职责 | 实现 owner | 结果 |
|---|---|---|
| metadata semantic delta 与 slot/index capacity | `KisPageMetadataCoordinator::PreparedPublication::Data` | prepare 持有，install 只消费 |
| commit root candidate | `KisImageEpochReferenceModel::PreparedCommit` | prepare 预构造 root 并预插入不可见 root slot |
| restore root candidate | `KisImageEpochReferenceModel::PreparedRestore` | undo/redo 同样预构造 root 并预插入不可见 root slot |
| batch 聚合与唯一状态 | `KisPagePublicationCoordinator::KisPreparedMutationCommit::Data` | 单一 `unique_ptr<Data>`；`Empty/Prepared/Installed/Cancelled` |
| proof/descriptor/completion/root 输入 | `Data` 内连续 `QVector`/value 字段 | install 前完成构造或移动 |
| 大对象与旧 metadata 清理 | outer candidate 锁外析构 + `DeferredPublicationCleanup` | 不在 owner/shard install gate 析构 |

`KisBackingBudgetReservation` 尚不存在，因为它属于 M5 的 `KisBackingBudgetController`。M4 candidate 不伪造空预算 capability；M5 接入
backing ledger 时必须把真实 reclassification delta 加入同一个 `Data`。`installCommitOnly()` 仍为 private 且没有生产 caller，M7 门禁不因此开放。

## 2. prepare 阶段冻结的 capacity

### 2.1 arena slot reservation

三个 `KisShardSlotArena` 新增 move-only `Reservation`：

- `reserveSlots()` 只在 shard mutex 下登记 batch slot 数；
- `availableSlots()` 从 free slots 中扣除全部 outstanding reservation，普通 mutation 不得偷用 prepared capacity；
- `emplaceReserved()` 是 prepared install 唯一消费入口；
- `cancelReservation()` 在 conflict、foreign candidate、显式丢弃和析构路径归还未消费 slot；
- outstanding reservation 存在时 `takeEmptyBlocks()` 不得拆走其 backing block。

publication prepare 先在锁外构造最坏需求的 16/32 KiB block candidates，relock 后复验 page revision/claim，attach 所需 block，再一次登记
version/replica/overflow slot reservation。install 不再 attach block。

### 2.2 index 与 activity reservation

- 每个 shard candidate 同时持有 exact-version 和 physical-slot `KisShardSlotIndex::Reservation`；
- full replacement 与 partial additions 都调用 `replaceAllReserved()` / `installPreparedAdditionsReserved()`，不在 install 内调用
  `reserveInsertions()`；
- prepare 为每个目标页预建 sparse `MetadataPageActivity` 并增加 `preparedPublications`；install 通过
  `consumePublicationActivity()` 原位换成 claim；
- header install 使用 `installReservedHeader()`，只修改已有 activity entry，不走通用 QHash upsert；
- mutation claim 使用 compact `KisVersionRecord` predicate，不再投影含 QVector 的完整 version snapshot。

footprint 同步公开三个 arena 的 `outstandingReservations/reservationBatches/rejectedReservations`；测试在 prepare 后观察非零 token，在
install、conflict、foreign owner、candidate destruction 后要求 arena/index token 全部归零。

## 3. outer prepared commit 与 side-map 收敛

`KisPreparedMutationCommit::Data` 聚合：

- metadata `PreparedPublication`；
- commit `PreparedCommit` 或 restore `PreparedRestore`，两者恰有一个有效；
- page proofs、proof descriptors、publication transitions、default/removal/restore descriptor delta；
- ready completion、fused history effects、discarded versions和 deferred metadata cleanup。

`tryInstall()` 使用 raw `void * + function pointer` epoch callback，不在 install 边界构造 `std::function`。metadata 拒绝或 epoch conflict
统一进入 `Cancelled`；成功同步进入 `Installed`；move-from facade 为 `Empty`。成功和失败 candidate 的连续数组均在 owner gate 外销毁。

原来的 `preparedProofs/synchronousHostCompletions/preparedSurfaceChanges/stagedPageRemovals` 四套 transaction-keyed side maps 已删除，改为
一个 `QHash<transaction, PreparedTransactionState>`；proof、completion、surface delta 与 removal 因此只有一个 transaction lifetime owner。

## 4. install 区间不变量

metadata install 的静态门禁禁止重新出现：

- `reserveSlots()` / `reserveInsertions()`；
- `MetadataArenaGrowth::attach()`；
- 通用 `replaceAll()` / `installPreparedAdditions()`；
- mutation `records.snapshot()`；
- 通用 `installHeader()`。

epoch commit/restore 在 metadata install 前已拥有不可见 root slot，descriptor QHash capacity 在 owner gate 解锁准备前完成 reserve，并在 relock
后以 descriptor revision/capacity 复验。root install 的 raw callback、intrusive retirement link 和 prepared metadata token 消费均不等待 provider、
I/O 或 GPU。

## 5. 验证与门禁

- `KisPageStoreReferenceTest`：300 passed，0 failed；
- 新增 arena reservation consume/cancel/empty-block guard、prepared activity lifetime、arena/index outstanding token 和 aggregate
  prepare/install/cancel counters；
- commit、metadata rejection、foreign owner、candidate destruction、root conflict、restore/default change 和 retained-root 顺序测试保持通过；
- machine-readable milestone 升为 `BR1-R2-M4`，metadata status 为 `r2-m4-allocation-free-publication`；
- architecture gate 禁止四套旧 side map 和上述 install-time reserve/attach/snapshot/upsert 回流；
- reverse-call graph 与 source baseline 在最终代码上重新生成。

## 6. 下一步边界

R2/M1–M4 至此关闭。后续 M5A 已建立唯一 `KisPageWriteCoordinator`、`KisPageWriteAdmission` 与
`KisBackingBudgetController`，先统一现有 `SemanticOnly/ReusePending/FreshPayload/FreshDiscard/FreshCow`，并把真实 backing budget delta
的类型和门禁落地；M5B 仍须完成生产迁移并接入本轮 prepared commit。M6 前不得实现 recoverable handoff，M7 前不得给
`installCommitOnly()` 增加生产 caller。见 [82](82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md)。
