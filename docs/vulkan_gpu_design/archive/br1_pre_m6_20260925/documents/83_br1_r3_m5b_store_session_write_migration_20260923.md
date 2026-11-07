> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R3/M5B 检查点：store/session write owner 收敛（2026-09-23）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：M5B 历史实施检查点，当前不能据此直接进入 M6。后续审计发现调用图/源码 checkpoint 陈旧、写协议与预算仍有缺口，现按
[84 全性能优化链路收敛方案](84_br1_full_optimization_convergence_and_cleanup_20260923.md) 执行；以下保留当时的实现及验证记录，不代表当前版本的重新验收。

## 已迁移

- `KisPageStore::Private` 的 `controlWritePages/mutationPages` 已删除。generic request 与 native session 的页冲突都经 store 内按值的 `KisPageWriteAdmission`；generic claim 跨 request → lease → publish/cancel，native session 用 `ClaimSet` 按 entry 扩展并在 detach 统一归还。既有 session 统计从 admission 计数生成。
- session 的 `pages/claimedKeys/removals/sources` 四套按键容器已删除。`KisMutationWriteSet` 是唯一 PageKey membership；语义移除存在 entry intent flag，alias source 用 entry source index 指向 `KisMutationSourceSet`，大 transition/descriptor/proof/binding 用 `plan.descriptorIndex` 指向稀疏 cold slot。首个 cold slot 内联，semantic-only entry 不扩张 cold slots。
- `KisCpuWriteGuard` 不再持有 binding shared ref 或完整 replica handle；只保留 session shared ref、entry index、pixel pointer/stride/size。target/base version 从 entry 的 compact version 读取，并加入 128 B 布局断言。
- cold Page 不再重复持有 `QSharedPointer<KisCpuResidentBinding>`；有效 writable reservation 是该 binding 的唯一 session 内持有者。tiles3 provider 从 guard 的 entry/cold slot 临时解析 replica 与 binding，并在 provider allocation 表内校验 identity。managed range 直接消费原有 logical target set 构造 write set，不再复制 PageKey 向量。
- backend managed operation 在创建 native session 前由 store-scoped `KisPageStoreManagedRange` 对完整目标做 all-or-none preclaim。该 adapter RAII 将同一份 `KisMutationWriteSet` 与 move-only `ClaimSet` 移入 session，owner token 在同一 store owner gate 下重绑；不释放/重取 PageKey，也不再有 session 第二次 store claim。backend 的 `activeWritablePages/operationWritablePages/cpuMutationPages` 三表现已删除：admission 明确区分 managed range、legacy adapter 与普通 native/generic writer，store 负责借用、同线程硬失败和 managed-other-thread 等待；单页 legacy RAII 向 native session 或 generic request 在同一 owner gate 下交接，语义移除持续持有 claim 到结束。
- native 首次 fresh 分配按 coordinator plan 选择 `FreshPayload/FreshDiscard/FreshCow`；generic `acquireWrite` 也使用 fresh selector 确定 discard/copy 路径。`HandoffRecoverable/HandoffCommitOnly` 仍不可选。
- backend 的整 tile 替换已改用 immutable `KisPageReplicaSource` + 单页 legacy claim 原子移交给 mutation session 的 alias/seal；生产调用不再先往 tiles3 provider 的 PageKey seed mailbox 塞入可变输入。旧 mailbox API/测试暂留为兼容面，属后续 R4 删除项，不能重新接回生产写路径。
- budget free-slot 容量在可失败的 reserve 阶段预留，`noexcept` commit/release 不因回收 slot 再扩容。
- 真实 backing 预留已集中进 `KisPageWriteCoordinator::reserveBacking`，native fresh、alias、generic fresh、默认页物化、初始页 bytes 导入与同步 adoption 在 provider 调用前通过同一入口；owner ledger 按 provider/epoch/allocation slot/generation 登记，并校验返回 replica 的 class/domain/bytes 确实被预留。未登记但需要退役的 provider 返回值会把原 reservation 带进 retirement queue，直到 terminal retire。
- `KisPreparedMutationCommit` 预构造跨 Current/ActivePending/RetainedHistory/RetirementDebt 的净额 delta，commit/restore root 安装成功时按值一次重分类，冲突/取消归还预留。历史 default 物化按 exact committed root 选择 Current 或 RetainedHistory；每页 transient generation 上限在新 pending allocation 前检查。default read buffer 已接入 OptionalCache 预算，先驱逐后重试，视图钉住时不越账；retirement queue 正常准入 Debt 并在 terminal retire 扣减 live。
- metadata coordinator 已在 authoritative detach 前执行两阶段 Debt prepare/revalidate/install/commit，stale/reject 路径 cancel；publication 把 history cleanup 的 retirement effects 与 class delta 合并为一次原子 reservation。fresh provider allocation 同时保留可转为 Debt 的 fallback reservation，因此 provider 已产出而尚未登记的失败结果也不会越过退役预算。
- owner ledger 新增 provider/epoch/physical-token 级记录、按预算类的逻辑引用计数和确定性 charged-class 优先级。tiles3 provider 为每个唯一 `KisTileData` 签发稳定 physical token，immutable alias 只增加引用，不重复增加 committed/live bytes；最后一个逻辑引用退役时才释放物理计账。provider footprint 在 backing admission、publication 与 usage 冷边界同步 resident CPU/SSD domain，换出、换入和 alias 去重均有断言。

## M5B 删除门槛结果

1. page writer admission 的 authoritative owner 只有 `KisPageWriteAdmission`；backend 只保留按线程定位 RAII batch 的兼容 registry，不保存 PageKey writer 集合。M5B ratchet 已把 `page writer admission` 从 split 改为 canonical。
2. session 的唯一 membership 是 `KisMutationWriteSet`，source/cold data 只由 entry side index 定位；guard、entry、reservation 与 prepared terminal path 均按文档 68 的值型/move-only 边界实现。
3. backing budget 覆盖 fresh allocation、commit/restore class transfer、default cache、Debt 事前准入及 tiles3 唯一物理 payload；退役队列只接收已属于 Debt 或持有 Debt fallback 的记录。M6/M7 handoff capability、physical retag 和 commit-only 状态仍保持不可选。

文档 68 的类型对照：entry 本体仍内联 intent/plan、compact versions、stable binding handle、值型 handoff/budget，完整 transition/descriptor/proof 不进入 512 B entry；guard 目标 128 B；source 与 cold storage 均以 entry 的 side index 定位。此次在 68 中明确了 `SemanticRemoval` intent bit 和稀疏 cold side storage，避免用新 keyed 容器复现旧状态。

## 最终版本验证

- 定向目标 `KisPageStoreReferenceTest`、`KisPageStoreCpuMutationTest`、`KisPageStorePhysicalClaimTest` 编译通过；Debt prepare/cancel/commit、physical alias 去重和 CPU/SSD swap 归属新增断言通过。
- 六项 PageStore 串行 ctest（Foundation、Reference、ReadBaseline、ResidentRead、CpuMutation、PhysicalClaim）全部通过；`KisPageStoreCpuMutationTest` 连续 20 轮通过，并发退役代表句柄窗口没有复现失败。
- tiles3 `kis_tiled_data_manager_test` 全量通过；首次回归暴露的 56 个 failure/competing-writer 用例已由 claim-origin 分类、range-wait 诊断和 reservation error propagation 修复，相关 82 个数据用例定向通过后全量复跑通过。
- `kis_tiles3_cpu_baseline_test` 通过。`check-pagestore-architecture.py --build-dir _build-br0-cpu` 通过：21 manifest entries、18 ownership facts、16 runtime census groups、1498 indexed APIs、12931 reverse-call edges。

后续顺序已调整为 84 的收敛清理，覆盖性能优化起点以来的全部链路。M6/M7 暂不扩展；下列旧状态不再适用于当前代码：
seed/host adoption 协议已删除，managed/legacy reservation 共享一个值型载体和移交实现。详见 84 执行记录。
