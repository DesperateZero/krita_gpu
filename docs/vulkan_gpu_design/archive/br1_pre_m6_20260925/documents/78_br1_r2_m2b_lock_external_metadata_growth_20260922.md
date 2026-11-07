> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R2/M2B 锁外 metadata arena growth 与类型对照（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**M2B 完成，M2 关闭；下一步只进入 M3 shard-global index/intrusive history，不授权 M4 或 backing handoff。**

本文记录 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) §5.2/M2 与
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R2 的第二个 arena 切片。M2A 的 stable slot、generation、budget 与
lock-external return 证据见 [77](77_br1_r2_m2a_shard_metadata_arenas_20260922.md)。

## 1. 与 68 冻结类型逐项对照

| 68 冻结设计 | 当前实现 | 结论 |
|---|---|---|
| `KisGenerationalSlotId { quint32 index; quint32 generation; }` | `KisPageMetadataArena_p.h` 的 typed `KisGenerationalSlotId<Tag>`，三个 id 均为 8 B、trivially copyable | 一致 |
| `KisShardSlotArena<T, BlockBytes>` | 同名二参数模板；16 KiB version、32 KiB replica、16 KiB overflow | 一致 |
| lazy block、stable slot、intrusive free list | `PreparedBlock` 延迟构造 payload；slot 地址在 active block 生命周期内固定；slot 内保存 free link | 一致 |
| block payload 锁外取得，锁内只 attach | `MetadataArenaGrowth::prepareBlocks()` 是 production `Arena::prepareBlock()` 的唯一调用点；`growMetadataArenasOutsideLock()` 明确以 `unlock -> prepare -> relock -> revision validation -> attach` 执行 | 一致 |
| 多余 candidate 锁外归还 | immediate path 的 growth batch 声明早于 locker；publication candidate 随 batch 在无 shard lock 时析构 | 一致 |
| directory 保留 block generation/state，generation 到顶 quarantine | M2A directory 与 slot generation/quarantine 保持不变 | 一致 |
| `KisShardSlotIndex<Key, SlotId>` | 尚未实现；当前 exact/physical/history 仍是 `VersionRecords` 的过渡容器 | 正确留给 M3 |
| `MetadataPage` 只含 intrusive head/tail/count/revision | 当前仍含 `shared_ptr<VersionRecords>` 与过渡索引 | 正确留给 M3 |
| `KisPreparedMutationCommit` 聚合 slots/index/root/budget | 未新建同义类型；本轮私有 `MetadataArenaGrowth` 只运输未绑定 slot 的 block payload，不含 index token、semantic delta、root 或 install 权利 | 正确留给 M4/M5 |

本轮没有把 block candidate 冒充 slot reservation。`MetadataArenaDemand` 只是锁内计算出的数量；真正的 slot id 仍只在 mutation
critical section 内由 arena `emplace()` 产生。因此 M2B 不提前冻结 M3 index token 或 M4 prepared-commit ABI。

## 2. production growth 协议

immediate register/transition/last-use/materialization 路径统一为：

1. 持有单个 shard mutex，投影状态机输入并计算 version/replica/overflow slot demand，同时记录 page revision 或 materialization identity；
2. 先用 `canAttachBlocks()` 对 hard budget 做锁内 fail-fast；仅在预算可容纳且容量不足时解锁，按 block size 构造
   `PreparedBlock` candidate；
3. relock 后重新查找 QHash iterator，复验 page revision、publication claim 与 materialization completion sequence；
4. 复验成功才 attach；同 shard 其他页在窗口内消费容量时继续锁外补候选，hard budget 或 allocation failure 则在任何 page metadata 改动前拒绝；
5. 写回完成后 detach 空 block，`ReleasedBlocks` 与未消费 candidate 均在 locker 之后析构。

同页并发 owner transition 在首次 slab 准备期间遇到 revision 变化时，会在最新 revision 上透明重投；arena growth 的实现窗口不会冒充业务拒绝，
`localTransitionSequences`/`localVersionInputs` 也只记录最终语义尝试。该路径以 4 worker × 200 次 retain/release 的用例连续重复 20 轮校验。

publication 不按页各准备一个 slab。`PreparedPublication::Data` 以 `ShardArenaGrowth` 聚合同 shard 全批 demand，一次准备足以覆盖该 shard
全部 candidate 的 blocks；claim pass 按 cumulative demand attach。所有 page claim 成功前不写权威 record。成功 install 完整批次后才允许
empty-block reclaim，避免前一页把后续已 claim 的空 block 提前 detach；后页冲突时则清除全部 claim、detach 本轮空 block并在锁外销毁。

## 3. 可观测性与因果基线

`KisPageMetadataMetrics` 新增：

- `metadataArenaGrowthBatches`；
- `metadataArenaBlockCandidatesPrepared`；
- `metadataArenaBlocksAttached`；
- `metadataArenaGrowthConflicts`；
- `metadataArenaGrowthFailures`。

`KisPageMetadataFootprint::Arena` 新增 cumulative `attachedBlocks`，并继续报告 active/directory/allocated/used/free/high-water/released/
quarantine/rejected-attach。candidate 是一次成功的锁外 block payload allocation；attached 是进入 shard budget 的子集，二者不混算。

`metadataArenaGrowthCausalBaseline` 固定 K1/H0、K16/H0、K16/H4 三个 metadata-only 场景，验证 record 数、logical tracked bytes、arena
allocated bytes、slack、candidate allocation count 与 attach count。设置 `KIS_BR1_METADATA_BASELINE=1` 时输出单个
`BR1_METADATA_ARENA` JSON，供后续 M3/M4 与真实 K1/K16/H fixture 做 paired comparison；这组 deterministic counter 不冒充 RSS 或
完整 write-pipeline latency。

2026-09-22 的 M2B 重构版本基线如下：

| 场景 | logical tracked bytes | arena allocated bytes | prepared candidates | attached blocks | version slack | replica slack | overflow slack |
|---|---:|---:|---:|---:|---:|---:|---:|
| K1/H0 | 1,168 | 49,152 | 2 | 2 | 126 | 239 | 0 |
| K16/H0 | 18,688 | 49,152 | 2 | 2 | 111 | 224 | 0 |
| K16/H4 | 43,776 | 49,152 | 2 | 2 | 47 | 160 | 0 |

三个串行情形均为 candidate = attached，growth conflict/failure = 0；K 从 1 增至 16、H 从 0 增至 4 时没有新增 block allocation，证明本轮
记录增长由 arena block 的摊销容量承担，而非恢复成 per-page/per-record backing allocation。该表只锁定本测试的因果计数，不将 49,152 B
解释为进程 RSS。

## 4. 失败原子性

- allocation failure、hard-budget attach rejection 与 relock revision conflict 均发生在 record 写回前；
- apply/sequence/last-use/materialization conflict 清空待返回 effects 或重排 completion，调用者从新 snapshot 重试；
- publication attach 失败发生在全批 claim pass，已 claim page 统一释放，已 attach 的空 block 统一 detach；
- `VersionRecords::put/replaceAll` 不再触发 block allocation，只验证 admission 已附着的容量；因此 mutation 开始后不存在普通 arena growth
  failure。

## 5. machine-readable gate

审计里程碑升级为 `BR1-R2-M2`，metadata status 为 `r2-m2-arena-authority-complete`。架构检查新增以下 ratchet：

- coordinator 中不得恢复 `ensureArenaCapacity`；
- production `Arena::prepareBlock()` 只能出现在单一 growth carrier；
- growth carrier 必须存在可见的 `unlock -> prepare -> relock` 顺序；
- candidate/attach/conflict/failure counters 与 causal baseline test 必须保留；
- M2 typed arena 不得进入 `KisPageStore.h` public ABI，M3/M4 类型不得提前伪实现。

## 6. 最终校验

- `KisPageStoreReferenceTest`：298 passed，0 failed；
- metadata/publication/index/并发定向集合：176 passed，0 failed；
- `indexedMutationConcurrentProtection`：连续 20 轮均为 3 passed，0 failed；
- architecture gate：21 manifest entries、17 ownership facts、16 runtime census groups、1,307 indexed APIs、12,076 reverse-call edges、
  21 frozen external intrusion files；
- `baseline-source.json` SHA-256：`b70932d0a4f52a731cd6ea407e6f2d5225e77fe97ab275e99b45671b345490b4`；
- `reverse-callgraph.json` SHA-256：`60a5f0c470e1e74f1d456ffe9357c87ed8d3e4a976162243febbe56612257ec6`。

## 7. 后续边界

后续 M3A 已删除 `VersionRecords` 的 per-page `std::list/QHash/QSet/std::map`，实现两个 shard-global `KisShardSlotIndex` 与
intrusive version/history/mutable 链，见 [79](79_br1_r2_m3a_shard_indexes_and_intrusive_records_20260922.md)。M3B compact page/activity
已关闭 M3，见 [80](80_br1_r2_m3b_compact_page_activity_20260922.md)；下一步才进入 M4 allocation-free publication install。
`MetadataArenaGrowth` 不升级为、也不替代 `KisPreparedMutationCommit`。
