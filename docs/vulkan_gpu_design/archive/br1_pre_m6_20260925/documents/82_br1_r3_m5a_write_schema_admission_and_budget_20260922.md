> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R3/M5A write schema、admission 与 backing budget（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**M5A 已完成；M5 尚未关闭。下一步为 M5B，把现有 native/generic/legacy fresh 路径迁入唯一 coordinator，并在同一迁移中删除旧 writer/session keyed 容器。本文不授权 backing handoff。**

本文记录 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) §4.1–§4.4、§4.6、M5 与
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R3 的第一段实现。M5A 只建立最终类型、所有权和可验证的
fresh-only selector，不把“类型已存在”误报为生产路径已经迁移。

## 1. 与文档 68 冻结类型的逐项对照

新增私有实现边界 `KisPageWriteCoordinator_p.h/.cpp`，包含：

- 值类型 `KisPageWriteContext`、`KisPageWriteIntent`、`KisPageWritePlan` 与冻结的 input/exposure/plan/fallback enum；
- move-only `KisMutationPageEntry`、`KisMutationWriteSet`、`KisMutationSourceSet`；
- move-only `KisPageWriteAdmission::ClaimSet` 与 `KisBackingBudgetReservation`；
- store-scoped `KisPageWriteAdmission`、`KisBackingBudgetController`、`KisPageWriteCoordinator`；
- M6 才会接 provider 的 `KisReplicaHandoffClaim` 空状态壳。M5 selector 不产生两种 handoff plan。

布局门禁直接冻结在私有头中：context 96 B、intent 64 B、plan 96 B、claim/reservation/handoff 40 B、entry 512 B。
`KisMutationPageEntry` 不允许重新内嵌 `KisPageTransition`、allocation descriptor、proof、resident binding shared pointer 或
per-page shared state。

当前 arm64/Qt6 目标构建的实际 `sizeof/alignof` 为：context 40/8、intent 48/8、plan 64/8、ClaimSet 40/8、handoff 32/8、
budget reservation 32/8、entry 280/8；均低于 68 的首版硬上限。

## 2. write set 与 source set

`KisMutationWriteSet` 已按 68 的索引规则实现：

- 第 1 页存于 `optional` inline entry；加入后续页不会搬移第 1 页；
- 2–8 页线性查找；
- 第 9 页建立并 reserve `PageKey -> EntryIndex` 稀疏索引；
- 已知 bulk 数量可以在 prepare 时一次 reserve，freeze 后禁止加入新 entry；
- guard/claim 的长期引用单位是 `EntryIndex`，不是 entry 裸指针。

`KisMutationSourceSet` 使用单项内联加连续 overflow，并复用 clear slot；entry 只需保存 source index。现有
`KisPageMutationSession::Private::pages/claimedKeys/removals/sources` 仍承担生产语义，必须在 M5B 迁移后同批删除，不能长期双写。

## 3. admission 与预算

`KisPageWriteAdmission` 引用现有 store owner mutex/condition，不新增第二把全局 writer 锁。`claimAll()` 按稳定 PageKey 顺序预检，
冲突时不留下本轮部分 claim；`ClaimSet` 只引用 write set，release 通过 claim id/owner token 清除其页。

`KisBackingBudgetController` 以 generational slot 保存 composite delta，reservation 本体只保存 controller/cookie/总字节/active。
prepare delta 禁止负数，按 Current/History domain 上限、各 class 总上限和 durable SSD 总容量执行硬拒绝；析构或显式 release
归还全部 reserved bytes。M5B 必须把 fresh allocation 前的真实 payload delta 接入该 controller，并由 M4 prepared commit 消费最终
reclassification delta；当前尚未把“未接线的 controller”计作生产预算覆盖。

## 4. 唯一 selector 的当前边界

`KisPageWriteCoordinator::select()` 当前只产生：

```text
SemanticOnly -> ReusePending -> FreshPayload -> FreshDiscard -> FreshCow
```

`ManagedCommitOnly` exposure 也不会使 M5A 选择 handoff。架构门禁显式禁止 selector 对
`HandoffRecoverable/HandoffCommitOnly` 赋值；M6/M7 的 eligibility、physical claim、capture fence 和首字节后不可失败协议均未开放。

三个服务已经在 `KisPageStore::Private` 中按值持有。现有 native/generic/legacy 入口尚未全部转发到 coordinator，因此 M5 仍为进行中。
原先并列的 `mutationTransactions/mutationPreparations/genericWriteTransactions` 已合并为 coordinator 内每 transaction 一个 compact
activity record；页级 `controlWritePages/mutationPages` 必须等 session write set 迁移时一起删除，避免出现半迁移 claim owner。

## 5. 验证与门禁

- `mutationWriteSetUsesInlineAndSparseIndexStorage` 覆盖 1 页内联、9 页索引、已知数量 reserve、重复 key 与 freeze；
- `writeAdmissionClaimsWholeSetsAtomically` 覆盖相交 write set 的无部分 claim 拒绝、release 与重新获取；
- `freshWriteSelectorAndBackingBudgetAreBounded` 覆盖五种允许 plan、handoff 不可达、硬预算拒绝和 reservation 归还；
- architecture milestone 升为 `BR1-R3-M5A`，并冻结类型、布局、按值 composition 和 handoff 禁入门禁；
- `KisPageStoreReferenceTest`：303 passed，0 failed；
- 最终 reverse-call graph：1498 APIs、12931 edges、11 callback registrations，physical gate production/test callers 为 0/20；
- source baseline SHA-256：`abbfd035ec719d4133a8c4b25df0b0c50c375ec24b3ea2edfeb297cf6898879c`；reverse-call graph
  SHA-256：`2eb1b9bf813c57f0f62a594168d3e097e8de1beea95c6fce8c28a8053508285f`。

## 6. M5B 删除门槛

下一步必须以生产迁移和旧表示删除为同一个闭环：

1. native mutation、generic request/lease、legacy backend adapter 全部调用唯一 selector/admission；
2. session 改为连续 entry + sparse source set，删除逐页 `shared_ptr<Page>` 和 `pages/claimedKeys/removals/sources` 四套 keyed 容器；
3. 删除 store 侧 `controlWritePages/mutationPages` 分裂表示，再迁移 backend 的三套 writable-page map；
4. fresh payload/COW/discard allocation 前持有真实 budget reservation，seal/commit/cancel/retire 完成分类转移；
5. forced-COW 行为与性能桶通过后才关闭 M5；M6 前仍不得调用 provider handoff。
