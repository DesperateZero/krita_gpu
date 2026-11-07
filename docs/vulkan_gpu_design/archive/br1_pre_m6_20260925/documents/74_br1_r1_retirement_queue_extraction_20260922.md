> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R1 `KisPageRetirementQueue` 无语义职责拆分（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**R1 第二项完成；detached physical retirement debt 已有唯一 owner。R1 后续三项亦已完成，当前下一步为 R2/M1。**

本文按 [69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R1 的固定顺序，在
[73](73_br1_r1_default_storage_extraction_20260922.md) 之后提取第二个 leaf service。本轮不改变 history reachability、epoch root、
publication、provider allocation authority 或 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) M1–M7。

## 1. 提取边界

新增：

```text
krita/libs/image/pagestore/KisPageRetirementQueue_p.h
krita/libs/image/pagestore/KisPageRetirementQueue.cpp
```

`KisPageStore::Private` 现在按值保存：

```cpp
KisPageRetirementQueue retirementQueue;
```

新 service 是 `final class`，不继承 `QObject`、不可 copy/move，也不通过 `shared_ptr`/`unique_ptr` 独立分配。原先直接位于
`KisPageStore::Private` 的以下状态已删除：

- `retirementMutex` 与 `retirementIdle`；
- `pendingRetiredReplicas` / `readyRetiredReplicas`；
- scheduled/closing/active worker 状态；
- pending bytes、pass 和 batch peak 统计。

service 现在唯一拥有：

- completion-qualified `retire` operation 的首次提交与后续 terminal polling；
- pending/ready detached replica debt；
- foreground bounded retry 和 background worker batching；
- close freeze、worker idle wait、queue take/drain；
- retirement live/peak/retry/drain 统计。

`pendingShutdownReplicas` 仍是 facade close 的 session 清单：它还包括从 authoritative metadata 枚举出的当前 replica，不等同于
detached retirement queue。history candidate 选择、root reachability 和新版本发布也没有迁入该 service。

## 2. completion、provider epoch 与锁序

每个 `KisPageRetirementRecord` 保存 exact replica、exact provider/epoch 对应的 provider 强引用、`lastUse` 和已绑定的
`retirementOperation`。第一次尝试调用 provider 并通过 `KisPageOwnerLedger::bindRetirementOperation` 分类为 detached retirement；
若 completion 尚未 terminal，记录保留同一 operation，后续只 poll，绝不再次发出第二个 retire。

冻结的 worker budget 为每 pass 最多 32 个 replica。queue mutex 只保护 debt、bytes 和 worker 状态；provider callback、completion
verification 和物理销毁均在 PageStore owner mutex 与 queue mutex 之外运行。拒绝或尚未完成的记录轮转到 pending 队尾，避免一个
blocked replica 饿死同批其他记录。

worker 通过 composition root 的 intrusive lifetime reference 保持按值 service 存活。图中唯一新增 callback registration 是
`Private::releaseRetirementLifetime` 的静态函数指针，已被 Clang graph 完整解析；它不持有 `shared_ptr`，不形成 service 生命周期环。

## 3. close/drain 拓扑

`closeSession` 保持原顺序：

1. 在 owner gate 下设置 facade closing，并调用 `retirementQueue.beginClose()` 冻结新 pass；
2. 释放 owner gate，等待当前 worker idle；
3. 等 metadata cleanup 与 history worker 完成；history worker 此时只能入队，不能启动新 retirement pass；
4. 若仍有其他 capability，取消 freeze 并恢复调度；
5. 否则 `takeForClose()` 原子移走 pending/ready debt，再与 metadata shutdown replica 清单合并；
6. close 在锁外逐项调用 `retireForClose()`，失败记录保留原 operation 并进入 `pendingShutdownReplicas`，供下一次 close 继续 poll；
7. 成功 close 断言 retirement service 已完全 drain。

因此 close 不会漏掉 detached-but-not-yet-started replica，也不会在 provider callback 中持有 owner/queue gate。

## 4. 可观测性与静态门禁

既有 pending bytes、pending replicas、background pass 和 maximum batch 指标改由 service snapshot 聚合，并新增：

- `activeRetirementReplicas`；
- `peakRetiredReplicas` / `peakRetiredBytes`；
- `retirementRetryRequeues`；
- `retirementCloseDrainedReplicas`；
- `retirementIdleWaits`。

`BR1-OWN-RETIREMENT` 已从 `misplaced` 改为 `canonical`，唯一 writer 是 `KisPageRetirementQueue`。
`BR1-PS-STORE-RETIREMENT-017` 已指向新 service，manifest 顶层状态为 `r1-retirement-queue-complete`。history 与 retirement runtime
census 已拆成独立 group，避免物理债务指标掩盖仍未提取的 history owner。

architecture checker 新增 ratchet：

1. 强制 `_p.h/.cpp`、`final`、32 项 worker budget、close/drain API 和按值成员存在；
2. 禁止旧 retirement mutex/双队列/worker state 回到 `KisPageStore.cpp`；
3. 禁止 service 变为 heap/shared owner；
4. manifest、ownership、runtime map 和 reverse-call graph 继续联合校验。

更新后的 Clang graph 覆盖 81 个 PageStore-reachable TU、538 个 repository record、1,150 个 API USR 和 11,483 条 call edge；
1 个 callback registration 已解析，unresolved edge 为 0。physical gate 仍保持 production caller 0/test caller 20。

## 5. 测试证据

既有 retirement failure-path 测试已扩展为直接验证 service snapshot：

- provider 阻塞时 publication 返回，active/live/bytes/peak debt 保持准确；
- 20 个被拒绝 replica 保持 debt 和 bytes，budget 0/负值不尝试，budget 3 只处理 3 个；
- retry 成功后 active/pending bytes 归零，历史 peak 保留；
- close 把 detached queue 债务计入 `retirementCloseDrainedReplicas`，失败记录保留到下一次 close；
- delayed completion 的同一 retirement operation 只 poll、不重发；
- first retirement 仍在 reclamation thread 执行，provider callback 可安全查询 session stats。

本轮验证：

| 测试 | 结果 |
|---|---:|
| retirement 定向 failure/close/concurrency 集 | 9/9 |
| PageStore/Completion CTest 完整集 | 7/7 |
| tiled data manager CTest 完整集 | 1/1 |
| PageStore architecture | 通过：17 manifest、13 ownership、12 runtime、1,150 API、11,483 edges |
| Vulkan architecture | 通过 |

测试环境仍报告既有 swap 路径不可写并使用系统临时目录；断言和结果不受影响。

## 6. 下一步

严格按 69 R1 顺序继续提取 `KisPageHistoryCollector`。下一切片只迁移 retained-root reachability、pending/ready/deferred history queue、
incremental scan cursor、worker continuation/drain 和对应统计；不得把 physical retirement 再并回 history，也不得提前进入 metadata M1、
write coordinator 或 backing handoff。

2026-09-22 后续：`HistoryCollector`、`ReadCoordinator`、`PublicationCoordinator` 已依序完成，R1 收口证据见
[75](75_br1_r1_history_read_publication_extraction_20260922.md)。当前顺序位置为 R2/M1 authoritative metadata records。
