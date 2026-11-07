# BR1 prepared wake 状态收费与节点收敛，2026-09-29

本批交付 S09/S10 的一个 PageStore 内部收敛子范围：prepared wake state 本体通过既有 mutation-storage 路径计入所属 controller 与产品共享父 `MetadataArena`，dormant/ready 队列改为 state 内嵌双向链，删除每 wake 的 `std::list` 节点分配。阶段裁决见 [92 §16.24](../../92_br1_m6_m8_execution_baseline.md#budget-wake-state-storage)。本结果不授予完整 S09/S10、跨 store 公平、前台 continuation、BC9 或 M6–M8 资格。

## 实现与边界

- `KisPageReclamationWakeState` 在 PageStore 私有头中承载 dispatch、弱 self、dormant/ready 链接和短期 budget identity。现有 `kisPreparePageStoreReclamationWake` 只增加 private budget 参数；没有新建通知函数族或产品 API。
- `prepareWake` 用 `kisAllocateMutationStorage` 分配真实 state 本体；一个私有 `placeWake` 统一摘链和入链。producer `notify()` 只移动现有节点并 signal，不分配、不执行 callback。
- budget waiter 与 read last-use 的既有 consumer 都传入原 backing controller。waiter 的空载永久容量预检包含 context + request state + wake state。
- `reset` 在 controller 存活时摘链并归还 state charge。monitor 若已取得强引用，只留下不携带 budget identity 的 tombstone，稍后释放原始内存。process-global executor 不按 store 重复收费。
- 本批关闭 state 本体与 per-wake list node。context/wake 的 shared control block、可能越过 `std::function` 小对象缓冲的 capture、`QRunnable`/dispatch task、reservation slot/free-list 高水位、其他 retry/pass/terminal 存储仍开放。

## 目标验证

构建命令与结果见 [build.log](build.log)。arm64 运行一个目标程序中的十一组结果族：

```text
KisPageStoreCpuMutationTest
  budgetWaitersReserveInOrder
  budgetWaiterStateStorageIsChargedAndReleased
  budgetWaiterCancellationAndLifetime
  budgetWaiterQueuedCancellation
  budgetWaiterSignedDurableTransfer
  budgetWaiterCommitReleasesUnusedCapacity
  preparedReclamationWakeCancellation
  retirementBudgetWaitersProgress
  automaticLastUse
  lastUseBoundedBurst
  lastUseCloseAndLifetime
```

[测试日志](tests-arm64.log)为 **67 passed / 0 failed / 0 skipped**。`preparedReclamationWakeCancellation` 使用 4096 B metadata controller，证明创建 wake 后 live 增加、move 与重复通知不重复收费、reset 后归零。waiter 用例证明 1 B 容量会在分配前拒绝 context+state+wake，正常 take 后仅保留 controller 级 context+wake，Waiting→reset 只增减请求 state；读 last-use、退休重试、close 和 owner 寿命矩阵继续通过。

[结构门](architecture.log)通过：21 manifest entries、25 ownership facts、16 runtime census groups、1,829 indexed APIs、19,891 reverse-call edges、17 callback registrations、19 frozen external intrusion files。相对上一 checkpoint 的唯一 indexed API 增量是私有 `placeWake`，它合并两条队列节点维护路径；现有 exported prepare 函数只是 private 签名扩展。`git diff --check` 见 [diff-check.log]；HEAD 与目标源码 SHA-256 见 [head.txt](head.txt)和 [source-sha256.txt](source-sha256.txt)。[文档校验](document-validation.json)同时确认完成项和开放项没有互相覆盖。

## 后续领取

下一生产批只核对仍真实存在的 shared control block、callback capture、slot/free-list 与 dispatch task 分配，并为必要终结存储确定单一 owner。跨 store 公平必须与可取消的原请求及 scheduler ownership transfer 同批设计；没有该 owner 时继续沿现有 `Failed` 终点。不得为已闭合的 wake state 再建立并列函数、第二队列或上层 budget identity。

后续 [92 §16.25](../../92_br1_m6_m8_execution_baseline.md#wake-control-block-convergence) 已以内嵌 monitor 引用删除 wake shared control block；本目录仍保留 §16.24 的 state/list-node checkpoint，当前开放项以 §16.25 和 `br1_wake_control_convergence_20260929` 为准。

后续 context/free-list 和 slot 数组实际准入见 [92 §16.26–16.27](../../92_br1_m6_m8_execution_baseline.md#reservation-storage-admission)。本目录原日志及哈希只证明其冻结源码；当前源码验证不代替重新运行。
