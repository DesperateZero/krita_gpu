> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R2/M3B compact page/activity layout（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**M3B 完成，M3 已关闭；后续 M4 已完成，见 [81](81_br1_r2_m4_allocation_free_publication_20260922.md)。本文不授权 backing handoff。**

本文记录 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) §5.1/§5.3/M3 与
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R2 的 M3B 实施。M3A shard index、reservation 与 intrusive
record 链见 [79](79_br1_r2_m3a_shard_indexes_and_intrusive_records_20260922.md)。

## 1. 与 68 冻结类型逐项比对

| 68 冻结设计 | M3B 实现 | 结论 |
|---|---|---|
| `KisGenerationalSlotId == 8 B` | version/replica/overflow 三类 slot id 均为 8 B | 一致 |
| `KisVersionRecord <= 128 B` | 128 B | 一致 |
| `KisReplicaRecord <= 128 B` | 128 B | 一致 |
| `KisMetadataOverflowNode <= 64 B` | 64 B | 一致 |
| `MetadataPage <= 96 B` | 96 B，并由编译期 `static_assert` 和 runtime footprint 固定 | 一致 |
| page 只保存 compact identity/list state | 保存 version/history/mutable intrusive head/tail、published version slot、epoch、next generation、revision 与三个 count | 一致 |
| 不嵌入 public snapshot/replica handle | `KisPageStateSnapshot header` 已删除；page/activity 均不保存 `KisReplicaHandle` | 一致 |
| writer/handoff 稀有状态使用 compact identity | shard 级稀疏 `MetadataPageActivity` 只保存 version/replica slot、token/id、mode/phase | 一致 |
| snapshot 仅在边界重建 | state-machine、publication、checkpoint/diagnostic 边界按 page key、published slot 和 activity slot 投影 | 一致 |

`MetadataPageActivity` 同样不超过 96 B。没有 writer、handoff、materialization 或 publication claim 的页面不创建 activity 条目；
因此稳态 page 只承担固定 96 B directory payload。materialization count 与短 publication claim 也进入该稀疏表，不再扩大每页热布局。

## 2. authoritative layout 与投影

- published generation/default revision 不重复存储，统一由 `publishedVersion` slot 指向的 `KisVersionRecord::version` 反解；
- writer 的 base/write version 和 base-authority/target replica 均保存 typed slot，公开 `KisPageWriterStateSnapshot` 只在边界重建；
- authority handoff 保存 operation 与 source/target replica slot，完整 handle 从 replica record 和 owner version 投影；
- activity 更新保留 materialization/claim 控制事实；writer/handoff 归零后，若无其他活动即同步删除稀疏条目；
- full replacement 与 partial publication 在 record/index 安装后更新 compact header，不再把 `entry.next.versions` 或 public QVector 留在 page 中；
- page key 继续由 shard `pages` 索引拥有，不在 `MetadataPage` value 中重复保存。

M3B 不声称 M4：activity `QHash`、publication capacity reservation 与完整 transition snapshot 仍可能在 install/owner 临界区分配。
这些必须由 `KisPreparedMutationCommit` 的预留和不可失败 install 协议另行收敛。

## 3. 内存因果基线

arena block 数与 record slack 未变化；下降全部来自每页 776 B public-snapshot header 被 96 B compact page 替换，即每页固定减少
680 B。

| 场景 | M3A logical bytes | M3B logical bytes | 变化 | arena bytes | idle activity entries |
|---|---:|---:|---:|---:|---:|
| K1/H0 | 1,104 | 424 | -680 | 49,152 | 0 |
| K16/H0 | 17,664 | 6,784 | -10,880 | 49,152 | 0 |
| K16/H4 | 38,656 | 27,776 | -10,880 | 49,152 | 0 |

活动 writer 的 round-trip 会创建一个不超过 96 B 的 activity entry；`CancelWrite` 后该 entry 立即回到 0。历史深度只增加 arena
record，不复制 page header 或 activity。

## 4. 验证与门禁

- `KisPageStoreReferenceTest`：300 passed，0 failed；
- compact record round-trip 新增 page 96 B、idle activity 0、writer slot projection 与 cancel 后回收检查；
- 48 组 indexed mutation（H0/H17/H257）与完整 reference suite 保持 oracle 一致；
- machine-readable milestone 升为 `BR1-R2-M3`，metadata status 为 `r2-m3-compact-page-intrusive-authority`；
- CI 要求 compact page/activity、slot projection、footprint 字段同时存在，并禁止 `KisPageStateSnapshot header` 回流；
- architecture gate：21 manifest entries、18 ownership facts、16 runtime census groups、1,349 indexed APIs、12,485
  reverse-call edges、21 frozen external intrusion files；
- `baseline-source.json` SHA-256：`243d523f41f42eb58b7e72d29036f84f1e5a90c636b29823cc74fe7cb5c351d2`；
- `reverse-callgraph.json` SHA-256：`ba833e4edd2277b178cdaffa630eb7f11c458a562c1e452192757736e86805e8`。

## 5. 下一步边界

M3 的 index、intrusive ordering 与 compact page/activity 三项已全部关闭。本文列出的 M4 剩余项已由
[81](81_br1_r2_m4_allocation_free_publication_20260922.md) 完成：真正的 `KisPreparedMutationCommit` 聚合、arena/index/activity
reservation、descriptor/completion/commit+restore root 输入、side-map 收敛和 install 静态门禁。下一步是 M5；M6 前仍不开放
recoverable backing handoff。
