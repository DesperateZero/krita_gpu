> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R1 History、Read 与 Publication 无语义职责拆分收口（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**R1 五项 service 提取完成；后续 M1 亦已完成，当前下一步为 M2，不授权 backing handoff。**

本文记录 [69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R1 固定顺序中最后三项实现，并汇总 R1 的完成门禁。
前两项独立证据见 [73](73_br1_r1_default_storage_extraction_20260922.md) 与
[74](74_br1_r1_retirement_queue_extraction_20260922.md)。本轮保持现有结果、锁序、完成票据、统计与 failure contract；没有把
[68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 的 metadata replacement 或 backing handoff 混入职责搬迁。

## 1. 完成的 owner 搬迁

### 1.1 `KisPageHistoryCollector`

新增 `KisPageHistoryCollector_p.h/.cpp`，由 `KisPageStore::Private` 按值持有。它成为以下状态和算法的唯一 owner：

- deferred/pending/ready/queued history work；
- 每页增量 scan cursor 与 retained-root reachability cache；
- 16 页 admission budget、32 version scan budget、worker continuation 与 idle drain；
- history visit、foreground visit、reachability refresh/root visit 统计。

collector 只判定不可达版本并产出 transition effect；物理 retirement 继续交给 `KisPageRetirementQueue`，epoch root 发布仍由
publication/epoch model 负责，避免重新制造 history/retirement 双 owner。

### 1.2 `KisPageReadCoordinator`

新增 `KisPageReadCoordinator_p.h/.cpp`，按值持有并统一：

- generic read request 注册、resolve 与 cancel；
- active read lease、consumer last-use 延迟确认；
- captured view/snapshot release 与相应计数；
- prepared transaction 的读保护查询和 abort 前 request 清理。

`KisPageStore` 的公共 read API 保留为 facade，只在 owner lock 下委托。provider access 的实际释放仍保持原有解锁边界，
不会在 owner mutex 内引入 provider 回调或等待。

### 1.3 `KisPagePublicationCoordinator`

新增 `KisPagePublicationCoordinator_p.h/.cpp`，按值持有并接管：

- preparing commit、prepared proof、同步 host completion；
- staged surface/default/removal 输入；
- commit、retained epoch restore、abort 的完整编排；
- default revision high-water、interim descriptor side table 与 publication 统计。

这里的 descriptor/default high-water 仍是 R1 的原表示搬迁，不被追认为最终 authority。R2/M1–M4 必须以
authoritative record、snapshot、stable-slot arena 和 `KisPreparedMutationCommit` 替换这些临时表示，再按同里程碑删除旧 side map。

## 2. composition root 与规模

R1 完成后 `KisPageStore::Private` 按值组合五个 final、非 `QObject` service：

```cpp
KisPageDefaultStorage defaultStorage;
KisPageRetirementQueue retirementQueue;
KisPageHistoryCollector historyCollector;
KisPagePublicationCoordinator publicationCoordinator;
KisPageReadCoordinator readCoordinator;
```

没有 `new`、shared/scoped/unique ownership，也没有逐页 manager。`KisPageStore.cpp` 从 69 冻结时的 5,522 行降为 3,979 行；
新实现分别为 History 321 行、Read 395 行、Publication 1,259 行。行数只说明 facade 收缩，不是删除资格或性能资格。

## 3. machine-readable audit 收口

审计里程碑统一升级为 `BR1-R1`，manifest 顶层 `restructuring_status` 为 `r1-complete`。新增/更新内容包括：

- history/read/publication 三个 canonical/delegated manifest owner；
- `BR1-OWN-HISTORY`、`BR1-OWN-READ-COORDINATION`、`BR1-OWN-PREPARED-PUBLICATION` ownership facts；
- read/publication runtime census 分组；
- 三个 service 的 final、非 `QObject`、按值嵌入、禁止 heap owner 与禁止旧容器回流 ratchet；
- 重新冻结当前 dirty source union 与 compilation-database-backed reverse call graph。

最终架构检查结果：

| 项目 | 结果 |
|---|---:|
| manifest entries | 19 |
| ownership facts | 15 |
| runtime census groups | 14 |
| indexed APIs | 1,227 |
| reverse-call edges | 11,582 |
| callback registrations | 11 |
| physical gate production/test callers | 0/20 |
| frozen external intrusion files | 21 |
| repeated graph SHA-256 | `70a630e37adc16ec12f54d7bd9e9967d1eca21ede8a466dae136aec58d270ec9`（两次一致） |

## 4. 构建与正确性验证

完成结构迁移后，在 `_build-br0-cpu` 上重新构建 `kritaimage` 与相关测试。一次 default publication 回归暴露了迁移候选中
`ReplaceDefaultPixel` transition 重复追加；删除重复追加后重新执行失败套件及完整定向集。

最终结果：

| 验证 | 结果 |
|---|---:|
| `kritaimage` build | 通过 |
| PageStore Foundation / Completion / Reference / ReadBaseline / ResidentRead / CpuMutation / PhysicalClaim | 7/7 |
| tiles3 tiled data manager | 1/1 |
| 定向 CTest 合计 | 8/8（46.56 s） |
| PageStore architecture | 通过 |

本轮只证明 R1 结构与现有行为等价。它不授予 zero-copy、bounded-memory、BR1-PERF、GPU/UMA 或删除 compatibility path 的资格。

## 5. 下一步边界

下一切片严格进入 68/69 R2/M1：先建立 authoritative metadata record 与 snapshot 分离，并定义 stable-slot arena 的唯一 owner、
索引和失败原子性。不得在 M1 尚未闭合时提前开放 recoverable/commit-only backing handoff，也不得以 R1 已搬迁的 descriptor side table
冒充最终 metadata authority。write unification 仍等待 M1–M4 完成。

2026-09-22 后续：M1 已完成，见 [76](76_br1_r2_m1_compact_metadata_records_20260922.md)；当前顺序位置为 M2 shard slot arena 与预算。
