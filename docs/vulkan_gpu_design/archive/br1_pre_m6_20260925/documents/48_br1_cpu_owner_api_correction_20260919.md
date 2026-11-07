> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 CPU Owner 基线与 API 校正记录（2026-09-19）

> 状态更新：本文是 BR1 中间切片记录；其中“尚未完成”只描述当时状态。51 已关闭功能/正确性 cutover；resident
> CPU 生产路径和布局未达出口，BR1 已以 **BR1-PERF** 重开，见
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](52_br1_cpu_fast_path_optimization_plan_20260920.md)。

本文记录对 BR1 reference baseline 的第二轮设计审核、必要接口校正，以及独立 CPU PageStore owner/provider 的首个
可执行切片。它在当时不构成 tiles3 cutover、PS1 关闭或 BR1 完成声明；后续功能 cutover 见 51，当前整体状态见
52。权威语义仍以
[25_p0_canonical_pagestore_krita_tile_cow_swap.md](../../../25_p0_canonical_pagestore_krita_tile_cow_swap.md) 和
[33_virtual_texture_pagestore_state_machine.md](../../../33_virtual_texture_pagestore_state_machine.md) 为准。

## 1. 审核结论

原有方向——单页 lease、immutable ImageEpoch、provider replica、未来 Layer/Flow 共用 EvalGraphIR——无需推翻，但
reference API 仍缺少足以支撑 production cutover 的证明边界。本轮修正后形成以下闭环：

```text
full allocation descriptor
-> provider-owned exact replica/layout
-> PageStore-owned request/operation/lease/writer identity
-> terminal completion verified by its issuing registry
-> metadata Prepared generation
-> owner-sealed PreparedPageProof
-> immutable ImageEpoch root switch
-> retained token for historical/evaluation reads
```

当前可运行的是显式 `configure -> registerReplicaProvider -> adoptInitialPage* -> finalizeInitialization` 的隔离 CPU
facade。legacy tiles3 尚未调用这条路径，因此“facade operational”不等于“文档像素已切换为 PageStore authority”。
该 facade 当前只注册声明 `synchronousOperations` 的 provider 和 transfer bridge；async provider/bridge 仍走
reserve/bind/completion queue 的后续接线，不能被同步代码把 Pending 误报为 Failed 后遗失 allocation。

## 2. 已校正的公共契约

### 2.1 Format、allocation 与 replica layout

- `KisPageAllocationDescriptor` 携带 layout revision、完整 `KisSurfaceFormat`、default pixel bytes、page extent、valid
  rect、row alignment 与初始化策略；尺寸、alignment 和乘法 overflow 均 fail closed。
- `KisReplicaLayout` 回显 format/layout revision、extent、valid rect、row stride 与 byte size；lease 和 provider
  validation 必须与 descriptor 匹配。
- production CPU provider 使用对齐 allocation，支持 nonzero default pixel、多行 stride、PreserveContents copy、预算、
  lease 和 retirement；不把 RGBA8/透明零当作隐式通用格式。
- provider 内 `transfer()` 只允许同 provider id/epoch。CPU↔UMA↔VRAM↔SSD 必须经显式
  `KisPageReplicaTransferBridge`，并在 facade finalization 前通过 `registerTransferBridge()` 注册；零个或多个匹配 bridge
  都 fail closed，不能依赖注册/容器顺序或伪装成普通 memcpy；当前 CPU facade 还要求 bridge 显式声明同步完成。

### 2.2 Completion 的来源与顺序

- `KisCompletionTicket` identity 为 `registry + domain + source + value`；不同 registry 从相同 source/value 起步也不会
  互认。
- terminal evidence 只能由 `KisCompletionRegistry::verifyTerminal()` 产生，metadata last-use/materialization 路径不接受
  调用者传入的裸 bool。
- 只有同 registry、同 source 的 `GpuTimeline` ticket 允许 timeline ordering；CPU job、I/O operation 和 host logical
  ticket 必须 exact-match，不能使用“更大的 value 已完成”推断。
- Vulkan command arena 与 retirement queue 已按该 typed domain 收紧，CPU/host ticket 不能进入 GPU timeline retire。

### 2.3 Request、lease 与 abort

本节记录 2026-09-19 基线契约。后续 [67 §10](67_br1_target_structure_reconstruction_20260920.md#10-2026-09-21冻结-sealed-overlay-与生产-packed-读取)
增加独立 captured-version retention：被捕获的 sealed Prepared 可在 abort 后转 Historical，继续保护已发出的读能力；
下述 abort 拒绝规则仍适用于 active writer 和未独立保留的 Prepared read/last-use。历史测试结果不据此改写。

- allocation/transfer operation 与 resolved access operation 使用不同的、进程内单调唯一 PageStore owner identity；GPU
  binding 不复用 allocation operation id，多个 document/session ledger 共享 provider 时也不会碰撞 lease/operation id。
- transaction id 与 retained snapshot token 同样在进程内单调唯一；两个独立 ImageEpoch/PageStore 实例即使从相同
  epoch/manifest 启动，也不能把另一实例的 transaction 或 retention capability 误认为自己的句柄。
- read 选择优先 exact authority；若没有 authority 且存在多个同能力 replica，在 route policy 落地前 fail closed，避免
  依赖容器迭代顺序。
- `acquireRead()` 在返回 request 前预留 lease identity 并 pin exact replica；`resolve()` 只建立 provider access。新增
  `cancel(ReadRequest/WriteRequest)` 释放未 resolve reservation，避免 request/resolve 窗口被 retirement 穿透。
- consumer last-use ticket 记录在 replica state，只有 verified terminal completion 才能解除 retirement 阻塞。
- `abort(PageTransaction)` 返回 `bool`。尚未 resolve 的 write request 可安全取消；active write lease 或 Prepared
  generation 的 active/pending-last-use read lease 存在时 abort 失败，调用者必须先消费 capability。禁止强制释放后留下
  悬空 CPU pointer/GPU binding。

### 2.4 Prepared proof 与 epoch commit

- `PreparedPageSet` 每页携带 owner-sealed `KisPreparedPageProof`，包含 transaction/version、完整 authority
  provider/epoch/allocation/domain/layout、成功 producer completion 与 validation stamp。
- `KisPageOwnerLedger` 保存 seal 记录；非零但未由该 owner 发放的 stamp 仍被拒绝。commit 前重新核对 metadata、provider
  layout/bytes ownership 与 completion，commit/abort 后撤销 seal。
- immutable root switch 是多页可见性的唯一线性化点；page record 的 `(publishedEpoch, generation)` 只是带 epoch tag 的
  cache。
- root switch 前先用同一 `KisPageStateMachine` 对全部 per-page cache transition 做无副作用预检，并预分配 terminal host
  completion；root 一旦切换，后续 cache apply 不再存在可预见的公开失败出口，避免“实际已 commit 但返回无效 ticket”。

### 2.5 Retention 与 EvaluationGraph

- `captureRetainedEpoch()` 返回 snapshot + token，`releaseSnapshot()` 精确消费 token；GC 保留 current root、显式 retained
  root，以及 open/prepared transaction 的 base root。
- graph/planner 在开始工作前通过 `validateRetainedEpoch()` 校验 token 与 snapshot 全量内容；类型自身的 `isValid()` 只做
  结构检查，不能替代 owner 验证。
- `CommittedEpoch` 与 `ExactVersion` read view 必须携带 retention token；epoch owner 验证 token→root→version。裸数字
  不再构成历史读权限。
- `KisEvaluationGraphSnapshot` 绑定 `KisRetainedImageEpochSnapshot`，并要求其 graph revision 与 EvalGraphIR revision
  相同；这为未来 Layer Tree 与 Flow frontend 共用同一 exact surface snapshot，非 Surface value 仍由独立
  Value/Resource Store 管理。

### 2.6 Materialization 两阶段边界

`KisPageMetadataCoordinator` 的合法顺序为：

1. shard 内 reserve dedup、request identity 与 proposed operation identity；
2. 锁外只分配 target；
3. shard 内 bind target、logical readiness，并通过 `BeginMaterialize` pin source；
4. source 已 pin 后，锁外启动 transfer/I/O；
5. provider completion 先经 registry 验证，再入队并由 shard owner应用 Complete/Fail transition。

公共 `apply()` 拒绝绕过该路径的 materialization 与 last-use completion。重复 request 共享一个 producer，但每次尝试提交
的 proposed operation id 都被消费，不能在另一 reservation 中复用。

## 3. 当前代码证据

本切片新增或实质接通：

- `KisCpuPageReplicaProvider`：真实 CPU bytes、alignment/default/COW/lease/budget/retire；
- `KisPageOwnerLedger`：provider registry、全局 typed identity、operation binding、completion verification 与 proof seal；
- `KisPageStore`：显式 initial manifest adopt/finalize、exact read、COW write、publish/proof/commit、retained historical read、
  read request pin/cancel、pending/active write abort 边界与 commit-before-root preflight；
- `KisImageEpochReferenceModel`：四类 revision、retained root/token、conflict/rebase 与 root GC；
- `KisPageMetadataCoordinator/KisPageStateMachine`：two-stage materialization、last-use acknowledge、retire effects 与
  epoch-tagged published cache；
- Vulkan provider/binding/retirement contract 对新 descriptor/layout/completion 类型的编译兼容。

2026-09-19 最终复跑证据：

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

cmake --build _build --target krita_vulkan_shader_assets -j6
ninja: no work to do.

build-tools/ci-scripts/check-vulkan-architecture.sh
Vulkan architecture checks passed.
```

以上证明隔离 CPU baseline、既有 tiles3/UI 路径和 Vulkan foundation 同时通过；不构成 tiles3 authority cutover、PS1
关闭或 BR1 完成声明；这是当时的阶段边界。后续功能关闭证据见 51，production 性能出口见 52。

## 4. 仍未完成：下一步按这个顺序推进

1. 已建立 `KisTileDataManager`/logical tile 到 `PageKey + allocation descriptor` 的只读影子 adapter，覆盖 identity、
   default pixel、extent 与 clone/COW 对照，不双写 canonical bytes；它不是 authority replica 或 accessor cutover。
2. 接 CPU accessor/iterator session，把 pointer 生命周期映射为 read/write lease，补并发 reader、abort、last-use 和
   purge/clear 测试。
3. 把 usersCount/duplicate/oldData/memento 映射为 generation retention，完成 undo/redo/clone/frame 的像素与 lifetime
   对照。
4. BR1 只把现有 swap identity 和 fail-closed provider seam 接到同一个 PageStore；append segment、durable index、
   checksum recovery、cleaner/GC 和跨域 residency 压力仍按 BR3/SSD0–SSD4 落地，避免 BR1 与 BR3 重复实现。
5. 完成多线程 shard stress、fault matrix、metadata bytes/page、transition latency、save/reopen 与现有 CPU golden 后，才
   允许逐步切 accessor authority 并评估 PS1/BR1 gate。

在以上 cutover 完成前，Vulkan replica 仍不能持有 canonical 文档 authority，Layer/Flow authoring 也不能绕过
EvalGraphIR、retained ImageEpoch 与 PageStore publication。

同一事务重复写、会话关闭/统计及 tiles3 影子映射的后续校正与最新证据见
[49_br1_transaction_lifecycle_tiles3_shadow_20260919.md](49_br1_transaction_lifecycle_tiles3_shadow_20260919.md)。
