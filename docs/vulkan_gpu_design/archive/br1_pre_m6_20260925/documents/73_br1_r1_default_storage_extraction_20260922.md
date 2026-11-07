> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R1 `KisPageDefaultStorage` 无语义职责拆分（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**R1 第一项完成；`DefaultStorage` 已成为按值嵌入的唯一 owner。R1 后续四项亦已完成，当前下一步为 R2/M1。**

本文按 [69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R1 顺序，在
[72](72_br1_r0_reverse_callgraph_and_closure_20260922.md) 关闭 R0 后提取第一个 leaf service。它不实现
[68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) M1–M7，不改变 epoch publication、provider authority、
write selection、backing handoff 或像素结果。

## 1. 提取边界

新增：

```text
krita/libs/image/pagestore/KisPageDefaultStorage_p.h
krita/libs/image/pagestore/KisPageDefaultStorage.cpp
```

`KisPageStore::Private` 现在按值保存：

```cpp
KisPageDefaultStorage defaultStorage;
```

新 service 是 `final class`，不继承 `QObject`，禁止 copy/move，也不通过 `shared_ptr`/`unique_ptr` 单独分配。它只拥有：

- exact default revision 对应的 immutable CPU read buffer；
- cross-scope default buffer cache、插入顺序和 bytes accounting；
- generic default materialization 的同 key 去重集合；
- preparation entry admission、wait condition 与 request/live/peak/wait 统计。

下列事实没有迁入 service：

- surface/default revision 与 epoch root；
- `defaultRevisionHighWater` 的逻辑 identity 分配；
- provider 选择、operation/completion 验证和 replica retirement；
- metadata transition、page registration 与写许可。

因此这是职责迁移，不是把 `KisPageStore::Private` 改名，也没有形成第二套 publication/authority。

## 2. 预算与锁序

冻结的 service 预算为：

| 资源 | 硬门槛 | 行为 |
|---|---:|---|
| cached default read buffer | 64 entries | FIFO eviction；scope/guard 强引用继续保证旧 revision 可读 |
| cached default read bytes | 8 MiB | 插入前逐项 eviction；单 buffer 超预算时只返回、不缓存 |
| concurrent default preparations | 64 entries | 第 65 个不同 key 在 owner condition 上等待，不创建额外 provider operation |

cache 使用 service-private mutex。preparation set 继续由 PageStore owner mutex 保护；wait 只临时释放并重新取得同一 owner mutex。
这保持原来的 `owner -> cache` 锁序，且 provider call 仍在 owner mutex 外执行。

同 key caller 和容量 waiter 被唤醒后重新读取 authoritative metadata：前一个 caller 已完成时直接复用结果，失败时才重新准备。
active preparation 被加入 `hasOutstandingCapabilities()`，所以 close 在 preparation 未排空时 fail closed；成功 close 断言 service 已 drain，
再清空 cache。

## 3. 可观测性

既有 `KisPageStoreSessionStats` default 指标改由 service snapshot 聚合，并新增：

- `defaultReadCacheEvictions`；
- `defaultReadCacheOversizeBypasses`；
- `activeDefaultPreparations`；
- `peakDefaultPreparations`；
- `defaultPreparationWaits`。

`defaultMaterializationRequests` 也已从 `KisPageStore::Private` 的独立 counter 迁入 service。统计不参与写许可；只有
`activeDefaultPreparations` 参与 close eligibility。

## 4. ownership、manifest 与静态门禁

R0 的复合 ownership fact 被拆为两个可验证事实：

| fact | 当前 owner | 状态 |
|---|---|---|
| default byte cache and materialization admission | `KisPageDefaultStorage` | `canonical` |
| default revision and surface association | `KisPageStore::Private` high-water + `KisImageEpochReferenceModel` | `split` |

第二项仍是后续 publication/epoch 职责债务，不能因本轮 cache 提取而宣称 default 全部 canonical。

`BR1-PS-STORE-DEFAULT-010` 已指向新 service，category 为 `canonical`、status 为 `delegated`；manifest 顶层
`restructuring_status` 为 `r1-default-storage-complete`。runtime census 绑定 cache/live/peak/wait/terminal 指标和新并发测试。

architecture checker 新增 ratchet：

1. 强制 `_p.h/.cpp`、`final`、三个硬预算和按值成员存在；
2. 禁止旧 `defaultBuffers/defaultPreparations/defaultBufferMutex` 等容器返回 `KisPageStore.cpp`；
3. 禁止 `KisPageDefaultStorage` 变成 heap/shared service；
4. manifest、ownership、runtime map 与 reverse-call graph 继续同时校验。

更新后的 Clang graph 覆盖 80 个 TU、535 个 repository record、1,135 个 API USR 和 11,471 条 call edge；callback registration
和 unresolved edge 仍为 0。`BR1-PS-STORE-DEFAULT-010` 已绑定新 service 的 14 个 API USR，并解析到 captured-read 与
generic materialization 两个 caller 边界。physical gate 仍保持 production caller 0/test caller 20，未受本轮影响。

## 5. 测试证据

`KisPageStoreResidentReadTest::sharedDefaultIsExactAndBounded` 现在额外验证 70 个 default revision 下：

- cache 保持 64 entries、8 MiB 上限；
- 发生 6 次确定性 eviction；
- guard 持有的旧 revision 在 eviction 后仍可读；
- close 后 cached/live bytes 归零；
- 没有错误 materialization、oversize bypass 或 preparation 泄漏。

新增 `defaultMaterializationAdmissionIsBounded`：65 个不同 default page 并发请求由 blocking provider 固定顺序，验证：

- provider 同时只收到 64 个 request；
- 第 65 个 caller 进入 admission wait；
- saturation snapshot 为 active/peak 64、requests 64；
- 此时 close fail closed；
- release 后 65 个请求全部完成，active 归零、总 requests 为 65，最终 close/drain 成功且 provider bytes 为 0。

本轮验证：

| 测试 | 结果 |
|---|---:|
| `KisPageStoreResidentReadTest` 完整集 | 32/32 |
| `virtualDefaultOnlyAllocatesTarget` | 6/6 |
| default removal/revision reference 定向集 | 4/4 |
| tiled data manager default lifecycle | 6/6 |
| PageStore/Completion CTest 完整集 | 7/7 |
| tiled data manager CTest 完整集 | 1/1（41.52 s） |
| PageStore architecture | 通过：17 manifest、13 ownership、11 runtime、1,135 API、11,471 edges |
| Vulkan architecture | 通过 |

测试环境仍报告既有 swap 路径不可写并使用系统临时目录；断言和结果不受影响。

## 6. 下一步

严格按 69 R1 顺序继续提取 `KisPageRetirementQueue`。下一切片只迁移 pending/ready retirement queue、completion-qualified defer、
worker batch、drain/close 和相应统计；不得同时改 history reachability，也不得提前进入 metadata arena 或 backing handoff。

2026-09-22 后续：`RetirementQueue` 切片见
[74](74_br1_r1_retirement_queue_extraction_20260922.md)；R1 其余三项与整体收口见
[75](75_br1_r1_history_read_publication_extraction_20260922.md)。当前顺序位置为 R2/M1 authoritative metadata records。
