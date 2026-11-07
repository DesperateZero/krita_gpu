> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 CPU Access Session 与历史 Epoch 恢复（2026-09-19）

> 状态更新：本文是 BR1 中间切片记录；其中“尚未 cutover/尚未完成”只描述当时状态。51 已关闭功能/正确性
> cutover；page-scoped 通用 session 不能作为 resident CPU 最终热路径，BR1 已以 **BR1-PERF** 重开，见
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](52_br1_cpu_fast_path_optimization_plan_20260920.md)。

本文记录 BR1 C1/C2 当时的进行中切片，承接
[49_br1_transaction_lifecycle_tiles3_shadow_20260919.md](49_br1_transaction_lifecycle_tiles3_shadow_20260919.md)。本轮关闭
PageStore 锁内执行同步 provider 热操作的问题，并建立可供 iterator/accessor 迁移的 page-scoped CPU session；同时补齐
undo/redo 所需的 retained historical generation 原子恢复语义。该切片完成时 tiles3 iterator 尚未切换到该 session，
因此它在当时不是 C1、C2 或 BR1 完成声明；后续功能 cutover 见 51，当前整体状态见 52。

## 1. Provider 调用的两阶段锁边界

`KisPageStore` 的同步 CPU 路径现在遵循：

```text
PageStore lock: validate + reserve typed capability
    -> unlock
provider: prepareWrite / transfer / resolveAccess / releaseAccess / retire
    -> lock
PageStore: validate exact identity/completion + apply transition
```

- write allocation 先插入 provisional request；close/abort 在 provider 调用期间看到 capability 并 fail closed；
- allocation/transfer 返回后重新验证 request、writer、generation、provider epoch 和 layout；竞争失败的 allocation 在锁外
  retirement；
- request 增加 preparing/resolving 状态，阻止并发 resolve/cancel/abort 消费同一 capability；
- access release 期间 active lease 仍留在 owner map，防止 close 越过物理 access release；
- transition 产生的 retirement effect 在 PageStore 锁外执行，并由 `activeProviderCalls` 计数覆盖关闭窗口；
- reentrant probe provider 在上述五类调用中回调 `sessionStats()`，证明没有重入 PageStore 全局锁死锁。

provider capability 查询和 proof seal 的只读 validation 仍是短临界区调用；它们不得执行 allocation、I/O 或等待。异步
provider 仍需 C4 coordinator 路径，不能冒充 terminal-at-return provider。

## 2. CPU access session

新增 `KisPageStoreCpuAccessSession`：

- read session 按 `PageKey` 缓存 exact move-only read lease；
- write session 对每个触页同时持有 transaction-overlay base read lease 与 write lease，分别提供 `oldData` 和 writable
  data；
- 返回 span 是 session-scoped 非 owning view，不能越过 `finish()/cancel()/destructor`；
- `finish()` 通过 PageStore 内部 host completion 发布各页 generation，但不越权提交多页 transaction；
- session 析构会释放 read lease、取消未发布 write，调用者仍显式 commit 或 abort 外层 transaction。

这为 random/sequential iterator 提供了不暴露 provider 的 page-level ABI，但现有 `KisRandomAccessor2`、hline/vline iterator
仍使用 legacy tile lock，尚未完成 production accessor cutover。

## 3. Undo/redo 的 historical restore

新增 `RestoreCommittedVersion` transition 与 `restoreRetainedEpoch()`：

- retained token 必须由同一 PageStore owner 验证；裸 epoch 数字无恢复权限；
- restore 创建新的、单调递增的 ImageEpoch/commit sequence，但 manifest 可以重新选择较旧 generation；
- root switch 仍是多页可见性线性化点，所有 page cache transition 在 switch 前预检；
- historical/current generation 间切换不重写 bytes，`nextGeneration` 保持大于所有已存在 generation；
- active transaction、write/request、prepared proof、materialization 或 provider call 存在时 restore fail closed；
- graph/default/extent/property revision 随 retained root 一起恢复，为后续 memento/default/extent 接线保留原子语义。

测试覆盖 `generation 1 -> 2 -> undo(epoch 3, generation 1) -> redo(epoch 4, generation 2)` 的 exact bytes 与 session
lease 清理。

## 4. 当前证据与剩余门槛

```text
KisPageStoreFoundationTest: 20 passed
KisPageStoreReferenceTest: 13 passed
```

仍未关闭：

1. 将 tiles3 random/sequential/hline/vline accessor 真正切到 CPU access session，并跑上游 iterator 像素对照；
2. 把 `KisMementoManager` token、default/extent/clear/purge mutation 接到 retained epoch/revision；
3. 接入现有 swap exact-generation seam；
4. 完成 async completion/retire/shutdown、并发压力与 save/reopen gate。

上述门槛未完成前，tiles3 仍是 legacy authority，Vulkan replica 仍不得持有 canonical 文档像素。
