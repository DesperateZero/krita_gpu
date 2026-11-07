# BR1 budget waiter state/context 唯一所有权与实际收费，2026-09-29

本批交付 S10 的一个内部收敛子范围：每个预算等待请求的 state 由 context 唯一拥有，state 与每 controller 的冷 context 本体通过现有 mutation-storage 路径计入本地及产品共享父 `MetadataArena`；外部 waiter handle 只保留弱 context 与 sequence。阶段裁决见 [92 §16.23](../../92_br1_m6_m8_execution_baseline.md#budget-waiter-state-storage)。本结果不授予完整 S10、跨 store 公平、前台 continuation 或 M6–M8 资格。

## 实现与边界

- 删除 `KisBackingBudgetWaitState` 的 `QSharedPointer` 共同所有权和反向 weak context。context 的固定 32 项数组改为 allocator-backed `unique_ptr` 唯一 owner。
- `KisBackingBudgetWaiter` 的公开方法不变；内部只保存弱 context+sequence。isValid/take/reset 继续遵守 context→controller 锁序，并在 controller 表中复验 sequence。
- 空载容量预检同时计入一次等待不可约的 context+state 字节，32 项已满也先无分配拒绝。context/state 都在 controller gate 外实际分配/收费，竞态后安装前复验；take、取消和 controller 析构把 state 移出数组后在 gate 外析构退费。
- context 的 charge 在 controller 寿命内复用；controller 析构先释放所有 state，再退 context charge，最后注销共享父 child。晚 waiter/callback 可短暂持有 tombstone control block，但不持有 controller 或预算 charge。
- context/state 的 `MetadataArena` charge 自动经过 §16.22 的共享父 reservation，因此局部和父层同额变化。没有新增第二账本、公开 getter、pressure 枚举或 stroke/scheduler 状态。
- 本批覆盖 state 与 context 对象本体。`QSharedPointer` control block、prepared wake/monitor 节点、reservation slot/free-list 高水位、可能外置的 callback capture 和 worker dispatch task仍开放。

## 目标验证

构建命令与结果见 [build.log](build.log)。arm64 运行一个目标程序中的八个结果族：

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
```

[测试日志](tests-arm64.log)为 **26 passed / 0 failed / 0 skipped**。新增用例证明 1 B metadata 在分配前拒绝不可约 context+state 并保持账本归零；共享父额下首次 Ready 同时收费 context+state，take 后只保留 context，Waiting→reset 仅增减 state，child 析构后注册节点与 context 一并归零。dormant waiter 跨 controller 析构后失效，父 live 仍归零。原 FIFO、独立资源越过、32 项上限、move/lifetime、回调竞争、SSD 净移动、unused grant、wake 取消和 4 BPP × 20/40 页 × close/normal 的退休恢复继续通过。

[结构门](architecture.log)通过：21 manifest entries、25 ownership facts、16 runtime census groups、1,828 indexed APIs、19,880 reverse-call edges、17 callback registrations、19 frozen external intrusion files。单调用点的 `detachStorageCharge()` 已内联回 controller 析构，不保留无独立协议的函数库存。`git diff --check` 见 [diff-check.log]；HEAD 与目标源码 SHA-256 见 [head.txt](head.txt)和[source-sha256.txt](source-sha256.txt)。[文档校验](document-validation.json)同时确认完成项与开放项没有互相覆盖。

## 后续领取

下一段优先处理 prepared wake/monitor 与 `QSharedPointer` control block 的实际所有权/收费边界：process-global executor 只能收费一次，每 controller 的 wake/list/control storage 才进入 store/父额。随后处理 reservation slot/free-list 高水位、callback/dispatch task、必要终结存储。跨 store 公平仍须由可取消且能回到原 scheduler job 的请求身份承载；没有该 owner 前继续返回 `Failed`，不增加上层 API。

后续 [92 §16.24](../../92_br1_m6_m8_execution_baseline.md#budget-wake-state-storage) 已关闭 prepared wake state 本体收费和每 wake list node 子范围；本目录仍保留 §16.23 源码时点的 26 项 checkpoint，当前剩余边界以 §16.24 和 `br1_wake_state_budget_20260929` 为准。

再后续 [92 §16.25](../../92_br1_m6_m8_execution_baseline.md#wake-control-block-convergence) 已删除 wake shared control block；当前未闭合的是 context control block、slot/free-list 与 callback/dispatch 等其他存储。

后续 context/free-list 和 slot 数组实际准入见 [92 §16.26–16.27](../../92_br1_m6_m8_execution_baseline.md#reservation-storage-admission)。本目录原日志及哈希只证明其冻结源码；当前源码验证不代替重新运行。
