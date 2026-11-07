> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R2/M3A shard 索引与 intrusive record 链（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**M3A 完成。后续 M3B 已关闭 M3，见 [80](80_br1_r2_m3b_compact_page_activity_20260922.md)。**

本文记录 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) §5.3/M3 与
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R2 的第一切片。M2 锁外 arena growth 与冻结类型对照见
[78](78_br1_r2_m2b_lock_external_metadata_growth_20260922.md)。

## 1. 冻结类型对照

| 68 冻结设计 | M3A 实现 | 结论 |
|---|---|---|
| `KisShardSlotIndex<Key, SlotId>` | 私有二参数模板；底层 `QHash` 不暴露，插入只允许 `reserveInsertions()` 后以 move-only `Reservation` 调用 `insertReserved()`，删除只走 `eraseExact()` | 一致 |
| reservation 计入 `size + outstandingReservations` | reserve 前按 live entries、已有 outstanding 与本批数量统一扩容；consume/cancel 均扣减 outstanding | 一致 |
| shard-global exact index | 每个 `MetadataShard` 按值拥有一个 `KisShardSlotIndex<KisPageVersion, KisVersionSlotId>` | 一致 |
| shard-global physical index | 每个 shard 按值拥有一个 `KisShardSlotIndex<PhysicalSlot, KisReplicaSlotId>`；`KisReplicaRecord::ownerVersion` 反解逻辑 owner | 一致 |
| intrusive version/history 顺序 | `MetadataPage` 保存 version/history head/tail/count，`KisVersionRecord` 保存 previous/next links；history 以 generation/default revision 排序 | 一致 |
| prepared/mutable 不得保留每页 `QHash/QSet` | mutable record 以单向 intrusive chain 表示，prepared transaction 由 record 内 `preparedBy` 在链上过滤 | 一致 |
| revision cursor | 私有 `MetadataHistoryCursor { after, nextHint, pageRevision }`；hint 失效时从 history head 按 position 恢复 | 一致 |
| 删除 `VersionRecords` owning container | `VersionRecords`、`shared_ptr<VersionRecords>`、per-page `std::list/std::map/QHash/QSet` 已从 production coordinator 删除 | 一致 |
| `MetadataPage <= 96 B` 且只保留 compact page/list state | 当前 page 已不拥有容器，但仍内嵌 688 B public `KisPageStateSnapshot header`，实测 `MetadataPage == 776 B` | **M3B 待完成** |
| M4 prepared commit | publication install 仍在 claim 区间取得 index reservation；没有伪造 `KisPreparedMutationCommit` | 正确留给 M4 |

compact record 继续满足冻结上限：`KisVersionRecord == 128 B`、`KisReplicaRecord == 128 B`、
`KisMetadataOverflowNode == 64 B`。为保持 replica 上限，replica 不再保存冗余 self slot；遍历时的 typed slot id 即 self identity，
腾出的 8 B 用于 `ownerVersion`。

## 2. 权威所有权与原子更新

`ShardRecordStore` 是每个 shard 唯一的 record/index owner：

1. exact lookup 直接得到 generation-checked version slot；
2. physical lookup 得到 replica slot，再经 `ownerVersion` 得到 version identity；
3. 新增/替换批次先检查跨 version physical alias，再一次预留 exact/physical capacity；
4. capacity token 成功后才编辑 arena record 与 intrusive links；失败不产生部分 record/index 写入；
5. record retirement 先从 physical、history、mutable、version 链和 exact index 同步摘除，再递增 arena slot generation；
6. full replacement 先为全批 index capacity 建立 token，随后切换 record 链；M4 会继续把该 reservation 前移到 prepared commit。

physical index 现在拒绝同 shard 不同逻辑页复用相同 `{provider, providerEpoch, allocation.slot}`，即使 allocation generation 不同；
generation retag 必须经过 68 后续定义的显式 physical ownership transfer，不能以第二个普通 insert 绕开。

## 3. intrusive 顺序与导出

- full snapshot 按 version intrusive chain 重建，保持原始 record 顺序；
- history chain 按 `{generation, defaultPixelRevision}` 递增，常见“最新版本转 historical”直接从 tail O(1) 接入；
- history slice 优先消费 cursor hint；identity 已退休或不再 historical 时，从 head 恢复并寻找严格大于 `after` 的位置；
- mutable chain 只保留 slot link，prepared transaction identity 留在 compact record，不再产生 transaction -> set 的页级堆节点；
- preparation candidate 的 additions 从 `std::list` 改为连续 `std::vector`，history map node transfer 已删除。

## 4. 指标与因果基线

`KisPageMetadataFootprint` 新增 exact/physical 两组 `Index` 指标：entries、capacity、outstanding reservations、high-water、reservation
batches 与 rejected reservations。deterministic logical bytes 只按 live entries 计 payload，不把 QHash bucket capacity 冒充逻辑状态。

| 场景 | M2 logical bytes | M3A logical bytes | 变化 | arena bytes | candidates/attached |
|---|---:|---:|---:|---:|---:|
| K1/H0 | 1,168 | 1,104 | -64 | 49,152 | 2 / 2 |
| K16/H0 | 18,688 | 17,664 | -1,024 | 49,152 | 2 / 2 |
| K16/H4 | 43,776 | 38,656 | -5,120 | 49,152 | 2 / 2 |

三组场景 exact entries == versions、physical entries == replicas、outstanding reservations == 0。record 达到 128 B ceiling 后，
16 KiB version block 的 slack 相应由 M2 的 126/111/47 变为 119/104/40；这属于冻结布局的可解释容量变化，不是泄漏。

## 5. 测试与 machine-readable gate

- `KisPageStoreReferenceTest`：300 passed，0 failed；
- 新增 reservation move/consume/cancel、duplicate insert、expected-slot erase 测试；
- 新增跨页 physical alias 拒绝测试，并把旧并发 publication fixture 的伪共享 allocation 改为每页唯一 physical slot；
- architecture gate：21 manifest entries、18 ownership facts、16 runtime census groups、1,333 indexed APIs、12,402 reverse-call edges、
  21 frozen external intrusion files；
- `baseline-source.json` SHA-256：`adcc52eee68698401efcea6d5669086b11befafe967a95e187eb0b1cd6bdacaa`；
- `reverse-callgraph.json` SHA-256：`3a24dfe021a952fc7a1ab4d659bfbff7ff2438231080f425deb6e8b19383eeef`。

CI ratchet 现禁止 `VersionRecords`、`shared_ptr<VersionRecords>`、page-local `std::list/std::map` 与 prepared/mutable side containers
回流，并要求 shard index、reservation API、intrusive version/history/mutable links 与 revision cursor 同时存在。

## 6. M3B 边界

本切片结束时的剩余项已由 [80](80_br1_r2_m3b_compact_page_activity_20260922.md) 完成：public/reference
`KisPageStateSnapshot header` 已删除，published identity、writer/handoff 与 materialization/claim 已拆为 96 B `MetadataPage` 和
shard 级稀疏 compact activity，machine-readable milestone 已升为完整 M3。下一步是 M4 allocation-free publication install；
这不追改本文件记录的 M3A 当时基线。
