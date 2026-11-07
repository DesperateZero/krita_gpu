> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R2/M2A shard-owned metadata arenas（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**M2A 完成时记录；后续 M2B 已完成并关闭 M2，见 [78](78_br1_r2_m2b_lock_external_metadata_growth_20260922.md)。**

本文记录 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) M2 的结构迁移切片，以及
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R2 的当前边界。M1 schema 与 snapshot 分离证据见
[76](76_br1_r2_m1_compact_metadata_records_20260922.md)。

## 1. allocator 核心

`KisPageMetadataArena_p.h` 新增通用 `KisShardSlotArena<T, BlockBytes>`：

- block payload lazy allocate，slot 地址在 block 存活期固定；
- 空闲 slot 使用 record 外壳内的 intrusive free link，不逐 slot 调通用 allocator；
- 8-byte typed id 的 generation 组合 block generation 与 slot generation，所有 `get/erase` 先验证 directory state 与 generation；
- slot 或 directory generation 到达上限前即 quarantine，不允许回绕；
- payload 归还后 directory 保留 `{blockGeneration,state}`，同 index 重用递增 block generation，因此旧 id 不会在新 block 上复活；
- `PreparedBlock` 把 block payload 分配与 attach 分开；有限 hard budget 在 arena 构造时同时固定 directory capacity；
- 空 block 通过 block 内嵌的 intrusive `ReleasedBlocks` 链移出 arena，detach 不分配，批次在 shard unlock 后析构；
- `close/drain`、owner-quiescent destructor 与 `allocated/used/free/highWater/releasedBytes/quarantine/rejection` 计数齐全。

arena 本身不含 mutex。所有 record 操作复用现有 metadata shard mutex，没有新增 per-record 或 global allocator mutex。

## 2. 生产权威 owner 已迁移

每个 `MetadataShard` 按值拥有：

```text
KisShardSlotArena<KisVersionRecord, 16 KiB>
KisShardSlotArena<KisReplicaRecord, 32 KiB>
KisShardSlotArena<KisMetadataOverflowNode, 16 KiB>
```

当前每 shard hard ceiling 分别为 4/8/4 MiB；它们是拒绝上限，不是预留 payload。首个 record 到来前不会分配 block。
M2B 的 metadata-only 基线会决定这些 ceiling 是否需要在冻结前调整。

`VersionRecords` 不再拥有 record node：

- `ordered` 仅暂存 `KisVersionSlotId` 顺序索引；
- exact/physical/history/prepared/mutable 容器只保存 identity 或 slot id；
- version、replica、captured view、lease 与 pending last-use 均由 shard arena 独占；
- snapshot/project/assign/remove 全部通过 generation-checked slot 解引用；
- `VersionRecordNode` 与其中的三个 owning list 已删除。

publication candidate 继续保存值快照，不持有 live arena 指针。install 后的权威记录只存在于 shard arena；完整 replacement 也写回同一组
arena，不再交换 candidate-owned record container。这保持 candidate 可取消、可延迟析构且不越过 coordinator/shard 生命周期。

## 3. 回收与观测

版本删除、完整 transition 写回和 publication replacement 后都会在 shard mutex 下 detach 超过首块保留量的空 block，然后显式 unlock，
最后析构 `ReleasedBlocks`。4095-history 门禁证明 version/replica 多余 block 被归还且各保留一个 active block。

`KisPageMetadataFootprint` 新增 version/replica/overflow 三组 arena 统计：directory entries、active blocks、allocated bytes、used/free slots、
high-water、released bytes、quarantined slots/blocks 与 rejected attaches。原 logical `trackedPayloadBytes` 继续保持 ABI-independent 口径，
不把 allocator slack 混入逻辑 payload。

## 4. 验证

新增 `metadataSlotArenaGenerationAndRelease` 覆盖 tiny block、固定地址、slot ABA、block-directory 重用 ABA、hard budget reject、close/drain、
owner-quiescent destructor 与八线程外部 shard 锁并发。既有 `metadataCompactRecordsRoundTrip` 现在实际经过三个生产 arena；
`metadataShardsSurviveConcurrentLeaseStressWithinBudget` 同时验证 live/allocated/free/high-water 统计。

当前结果：

- `kritaimage` 与 `KisPageStoreReferenceTest` 构建通过；
- 完整 `KisPageStoreReferenceTest` 297/297 通过；
- compact/arena/concurrent footprint 定向集 5/5 通过；
- 4095-history 空 block 归还门禁通过。
- PageStore/Completion/tiles3 定向 CTest 8/8 通过（46.64 s）。

machine-readable audit 已升级为 `BR1-R2-M2A`：21 manifest entries、17 ownership facts、16 runtime census groups、1,293 indexed
APIs、11,983 reverse-call edges 与 21 frozen external intrusion files，检查通过。reverse graph SHA-256 为
`eee1d8acb4c72aa990096b5a25952e827b245de83a0247145ffa19455378469a`，source baseline SHA-256 为
`6358c59d8b85349298e70a38bc0994ee47860dd581179c4a49ecac14c80435ec`。

## 5. M2B 完成后的历史边界

以下是 M2A 完成时尚未满足的门槛；现已由 [78](78_br1_r2_m2b_lock_external_metadata_growth_20260922.md) 全部收口：

1. 在 mutation/publication admission 阶段计算 version/replica/overflow slot 需求；
2. 在 shard lock 外准备不足的 block，锁内只验证 revision、attach 或拒绝，多余候选回到锁外；
3. 证明 concurrent reservation 不会过量承诺 hard budget，也不会出现 post-mutation capacity failure；
4. 冻结接入前后 metadata-only RSS、allocation count、arena slack 与 K1/K16/H 因果对照；
5. 将 machine-readable milestone 从 `BR1-R2-M2A` 升为完整 M2 后，才允许进入 M3 intrusive index/history。

本文仍只记录 M2A 当时状态；M3、M4、M5–M7 与任何 backing handoff 的状态不由本文改变。
