# BR1 prepared wake control block 收敛，2026-09-29

本批继续交付 S09/S10 的 PageStore 内部控制存储收敛：删除每个 prepared wake 的 `std::shared_ptr<KisPageReclamationWakeState>` control block，以已收费 state 内的原子引用承载 handle 和 monitor/shutdown 的临时所有权。阶段裁决见 [92 §16.25](../../92_br1_m6_m8_execution_baseline.md#wake-control-block-convergence)。本结果不授予完整 S09/S10、跨 store 公平、前台 continuation、BC9 或 M6–M8 资格。

## 实现与边界

- `KisPageReclamationWake` 只保存 state 原始指针；move constructor/assignment 用 exchange 转移唯一 handle 引用，不复制所有权。
- `KisPageReclamationWakeState::references` 位于 §16.24 已实际收费的 state 本体。monitor/shutdown 只在 clock mutex 下看见已登记节点时增加临时引用，离锁完成 callback/清理后由唯一 `releaseWake` 释放。
- reset 先摘链，再在 controller 存活期分离 budget identity 并归还 state charge，最后释放 handle 引用。运行中的 callback 可保留 tombstone state 和 capture，但不保留 controller 或预算身份。
- 每 wake 的动态控制存储从 state + list node + shared control block 收敛为一块已收费 state。既有 prepare/notify/reset 产品边界不变；新增的 `releaseWake` 是 PageStore 私有释放汇合点，没有上层函数族。
- context 的 `QSharedPointer` control block、可能外置的 `std::function` capture、`QRunnable`/worker dispatch task、reservation slot/free-list 高水位和其他 retry/pass/terminal 存储仍开放。

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

[测试日志](tests-arm64.log)为 **67 passed / 0 failed / 0 skipped**。`preparedReclamationWakeCancellation` 除 move/reuse/reset 计账外，新增 in-flight 交错：monitor callback 停在执行区间时，主线程 reset 立即使 metadata live 归零；capture 在放行前保持存活，callback 结束后释放，证明内嵌引用替代 control block 后仍满足取消和寿命协议。

[结构门](architecture.log)通过：21 manifest entries、25 ownership facts、16 runtime census groups、1,830 indexed APIs、19,897 reverse-call edges、17 callback registrations、19 frozen external intrusion files。相对 §16.24 唯一 indexed API 增量是私有 `releaseWake`，用于合并 monitor、shutdown 和 handle 的最后引用释放；external intrusion 数不变。`git diff --check` 见 [diff-check.log]；HEAD 与目标源码 SHA-256 见 [head.txt](head.txt)和 [source-sha256.txt](source-sha256.txt)。[文档校验](document-validation.json)确认当前源码不存在 `shared_ptr<WakeState>` 或 self weak control path，并保持开放项为未完成。

## 后续领取

下一生产批先处理 context control block 或 reservation slot/free-list 中能形成单一 owner、实际字节和退出退费闭环的一项。callback capture 与 worker task 必须按是否越过小对象缓冲和实际调度寿命核对，不能用估算 charge 冒充实际分配。跨 store 公平继续等待可取消的原请求和 scheduler ownership transfer；没有该 owner 时沿现有 `Failed` 终点。

后续 context/free-list 和 slot 数组实际准入见 [92 §16.26–16.27](../../92_br1_m6_m8_execution_baseline.md#reservation-storage-admission)。本目录原日志及哈希只证明其冻结源码；当前源码验证不代替重新运行。
