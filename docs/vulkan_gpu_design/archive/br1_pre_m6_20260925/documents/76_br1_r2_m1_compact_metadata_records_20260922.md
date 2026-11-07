> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R2/M1 compact authoritative metadata records（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**M1 完成；后续 M2A 权威 arena 迁移已完成，见 [77](77_br1_r2_m2a_shard_metadata_arenas_20260922.md)。**

本文记录 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) M1 与
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R2 的第一切片。R1 完成证据见
[75](75_br1_r1_history_read_publication_extraction_20260922.md)。

## 1. 权威记录与 snapshot 已分离

新增私有 schema：

- `KisPageMetadataArena_p.h`：定义 8-byte `KisGenerationalSlotId<Tag>` 以及 version/replica/overflow 三类 typed id；
- `KisPageMetadataCoordinator_p.h`：定义 `KisVersionRecord`、`KisReplicaRecord`、`KisMetadataOverflowNode`；
- `KisPageMetadataCoordinator.cpp`：权威 `VersionRecords::ordered` 从完整 `KisPageVersionStateSnapshot` 改为 compact
  `VersionRecordNode`，node 内分别保存 version common record、replica records 与 rare overflow nodes。

公开/reference `KisPageStateSnapshot` 不再是权威版本容器。完整 snapshot 只在 diagnostic/checkpoint/兼容边界按值重建；
`applyOwnerSequence()` 继续只投影 writer/base/target、显式 transition versions 与 indexed collision witness，运行既有纯状态机后仅把 touched
records 写回。未触及 history 不会因 reader/pin/writer 改动被复制或覆盖。

## 2. compact schema

`KisVersionRecord` 保存 version identity、publication/prepared owner、typed version/replica/overflow links 与计数；
`KisReplicaRecord` 保存 provider/allocation/layout、validity、pin、operation 与 typed links，不内嵌 128-byte `KisReplicaHandle`；
handle 只在投影时于栈上重建。

captured views、read leases 与 pending last-use completion 进入 `KisMetadataOverflowNode` 链。常见的一 version、一 replica、无额外保护状态
不会在 compact record 中携带 `QVector` 或公开 snapshot。编译期门禁为：

| 类型 | 门禁 |
|---|---:|
| typed generational slot id | 8 B |
| `KisVersionRecord` | <= 128 B |
| `KisReplicaRecord` | <= 128 B |
| `KisMetadataOverflowNode` | <= 64 B |

M1 完成时仍以 `std::list<VersionRecordNode>` 提供稳定 owning node；这是 M2 前的过渡分配策略，不是最终 arena。publication addition 在 prepare
阶段构造 compact node并预留 live index capacity，install 继续只 splice/consume，不把大对象构造重新推入 publication 临界区。

## 3. 等价与失败验证

新增 `metadataCompactRecordsRoundTrip`，覆盖：

- 两个 provider/不同 allocation generation 的 replica；
- authority 重建；
- captured-view、read-lease、pin 与 pending-last-use overflow；
- snapshot -> compact records -> snapshot 全字段 round-trip；
- transition 写回后的第二次 round-trip；
- 重复 capture 错误注入拒绝且权威记录不变。

既有 indexed mutation/publication、prepared revision conflict、history slice、materialization 和并发 lease 测试继续作为 reference oracle。
生产 write selector 没有变化，所有写仍走现有 fresh allocation/COW。

## 4. machine-readable gate

审计里程碑升级为 `BR1-R2-M1`，manifest 增加 `metadata_status = r2-m1-complete` 与
`BR1-PS-METADATA-RECORDS-020`；ownership 增加 `BR1-OWN-METADATA-RECORDS`，runtime census 增加 compact-record 分组。
架构检查同时禁止：

- 权威 `ordered` 容器恢复保存 `KisPageVersionStateSnapshot`；
- compact record 内嵌公开 version/replica snapshot vector；
- record/overflow 超出冻结尺寸；
- typed slot 类型进入 `KisPageStore.h` 公共 ABI。

最终架构结果：20 manifest entries、16 ownership facts、15 runtime census groups、1,237 indexed APIs、11,712 reverse-call edges、
21 frozen external intrusion files，检查通过。调用图重复生成 SHA-256 均为
`57a7c4602af24fac27201eecd0469aae5b64b06b63e4f80af755001fb70a0741`。

## 5. 构建与测试

| 验证 | 结果 |
|---|---:|
| `kritaimage` 与 `KisPageStoreReferenceTest` build | 通过 |
| compact round-trip + indexed mutation/publication/revision 定向集 | 106/106 |
| PageStore/Completion 定向 CTest | 7/7 |
| tiles3 tiled data manager | 1/1 |
| 定向 CTest 合计 | 8/8（49.71 s） |
| PageStore architecture | 通过 |

## 6. 下一步边界

下一切片严格执行 M2：每个 metadata shard 建立 version 16 KiB、replica 32 KiB、overflow 16 KiB 三个 typed arena，加入 intrusive free
list、slot/block generation 验证、锁外 block growth/return、quarantine 与 `allocated/used/free/highWater/releasedBytes` 统计。
M1 的 transitional list node 只有在 arena 通过 slot ABA、tiny budget、close/drain 与 shard 并发门禁的同一切片才能删除。
该条件已由 [77](77_br1_r2_m2a_shard_metadata_arenas_20260922.md) 的 M2A 满足；本文保留完成时状态作为审计记录。
M3 索引/history intrusive 化、M4 allocation-free prepared commit、M5 write coordinator 与任何 backing handoff 均不得提前。
