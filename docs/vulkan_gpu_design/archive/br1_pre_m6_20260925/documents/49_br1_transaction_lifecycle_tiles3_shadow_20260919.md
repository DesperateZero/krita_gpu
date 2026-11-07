> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 事务链、会话生命周期与 tiles3 影子映射（2026-09-19）

> 状态更新：本文是 BR1 中间切片记录；其中 C1–C5 待办只描述当时状态。51 已关闭功能/正确性 cutover；resident
> CPU 生产路径和布局未达出口，BR1 已以 **BR1-PERF** 重开，见
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](52_br1_cpu_fast_path_optimization_plan_20260920.md)。

本文记录 BR1 审核后完成的 C0 校正切片。它延续
[48_br1_cpu_owner_api_correction_20260919.md](48_br1_cpu_owner_api_correction_20260919.md) 的 CPU owner baseline，
关闭同一事务重复写、会话关闭边界和 tiles3 identity 对照三个前置缺口。该切片在当时仍不是 accessor authority
cutover、PS1 关闭或 BR1 完成声明；后续功能 cutover 见 51，当前整体状态见 52。

## 1. 本轮关闭的问题

### 1.1 同一事务内的重复写

同一 `PageTransaction` 对同一 `PageKey` 连续执行 `PreserveContents` 时，后一次写必须以前一次已 Prepared 的最新
generation 为 base，而不是重新从 transaction base epoch 取旧 generation。对应契约现在固定为：

- `TransactionOverlay` read 解析到该事务该页的最新 Prepared generation；
- write acquire 从相同 generation 继续 COW，generation 严格单调；
- `PreparedPageSet` 对每个 `PageKey` 只保留最终 generation 的一个 owner proof；
- 被覆盖 proof 的 seal 立即撤销，commit/abort 后不残留 prepared seal；
- epoch commit 仍只有一次 immutable root switch，事务中间 generation 不对 committed reader 可见。

回归覆盖 `generation 1 -> 2 -> 3`、第二次写保留第一次写入的 bytes、proof 去重、原子 commit，以及 abort/close 后
owner 记录清理。

### 1.2 会话关闭与资源可观测性

`KisPageStore` 新增 `sessionStats()` 与幂等 `closeSession()`：

- stats 显式报告 retained roots、active transactions、pending requests、active leases、pending last-use、prepared proofs、
  materializations 和 provider operations；
- close 在任一外部 capability 仍存活时 fail closed，不伪造“已经安全关闭”；
- 成功 commit/abort 后回收 finished transaction，snapshot release 后回收不再被引用的 immutable root；
- terminal-at-return provider operation 在完成验证后从 owner ledger 移除，避免同步 facade 的 operation record 无界增长；
- resolved lease 自身保留 provider access record 的共享生命周期，即使 `KisPageStore` owner 先析构，最终 lease
  析构仍能执行精确 `releaseAccess()`。

这只是同步 CPU facade 的确定性关闭边界。异步 provider drain、deadline/cancel、device-lost 和分阶段 shutdown 仍属于
后续门槛。

### 1.3 tiles3 只读影子 adapter

新增 `KisTiledDataManagerPageStoreShadow`，用于在不改变 legacy authority 的前提下建立对照证据：

```text
registered canonical SurfaceDescriptor + SurfaceId
    + tiles3 (column, row)
    -> PageKey
    -> observed Generation + SHA-256 content digest
    -> allocation/default/extent/COW diagnostic snapshot
```

配置必须提供规范化 canonical `KisSurfaceDescriptor`、64x64 logical page extent、layout revision 和幂次
row alignment，并验证 tiles3 pixel stride/default pixel。capture 记录 default-pixel revision、data extent revision、
物理 allocation 是否存在、users/memento 状态，以及用于验证 clone/COW sharing 的进程内 backing token。

影子 adapter 有意不做以下事情：

- 不持有、复制、发布或双写 canonical bytes；
- 不把指针值当成可持久化 Page/Replica identity；backing token 只用于测试期诊断；
- 不注册 authority replica，也不让 PageStore 与 tiles3 同时成为 owner；
- 不替代 iterator/accessor lock、memento、purge、swap 或 save/reopen 路径。

因此它关闭的是 PS1 的 identity/default/extent/COW 对照前置项，而不是 `KisTileData` provider 或 accessor cutover。

## 2. 本轮验证证据

```text
_build-br0-cpu/bin/KisPageStoreFoundationTest -maxwarnings 0
Totals: 20 passed, 0 failed

_build-br0-cpu/bin/KisPageStoreReferenceTest -maxwarnings 0
Totals: 13 passed, 0 failed

ctest --test-dir _build-br0-cpu --output-on-failure \
  -R '^(libs-image-kis_transaction_test|libs-image-kis_stroke_test|libs-image-kis_strokes_queue_test|libs-image-KisPageStoreFoundationTest|libs-image-KisPageStoreReferenceTest|libs-image-tiles3-kis_tiled_data_manager_test|libs-ui-KisFrameCacheStoreTest)$'
100% tests passed, 0 tests failed out of 7

_build/bin/KisVulkanFoundationContractsTest -maxwarnings 0
Totals: 13 passed, 0 failed

_build/bin/kritavulkanoffscreen.app/Contents/MacOS/kritavulkanoffscreen
checksum=32896
```

Vulkan target 在原 `_build` cache 上以 `MACOSX_DEPLOYMENT_TARGET=12` 重新生成并编译通过；shader asset target 同步
构建通过。以上证据只说明新 backend-neutral 类型没有破坏既有 CPU/tiles3/UI 与 Vulkan foundation 边界。

## 3. BR1 后续顺序与关闭条件

1. **C1 accessor lease bridge**：同步 provider allocate/transfer/resolve/release/retire 和通用 CPU page session 已由后续
   切片完成；仍需把现有 tile/random/sequential iterator 真正切到该 session，不能保留绕过 lease 的产品路径。
2. **C2 COW/memento retention**：把 `usersCount/duplicate/oldData/memento` 映射到 generation retention，完成
   undo/redo/clone/frame、clear/purge 和 default/extent mutation 对照。
3. **C3 swap seam**：让现有 swap identity 通过同一 exact-generation provider seam；BR1 只固定失败与 authority
   安全，durable segment/index/checksum recovery/cleaner 仍由 BR3 完成。
4. **C4 async 与关闭**：接通 reserve/bind/completion queue、`Begin/Complete/FailRetire`、timeout/cancel/device-lost，
   使 `closeSession()` 能 drain 或明确拒绝全部异步 capability。
5. **C5 cutover gate**：通过多线程 shard stress、fault matrix、metadata bytes/page、transition latency、CPU golden 和
   save/reopen 后，才允许逐步切换 accessor authority；切换期间仍禁止双写。

本切片完成时 C1–C5 尚未全部完成，BR1 当时保持“进行中”；Vulkan replica 不得拥有 canonical 文档像素，
Layer/Flow frontend 也只能
通过共同的 EvalGraphIR、retained ImageEpoch 与 PageStore publication 边界消费数据。
