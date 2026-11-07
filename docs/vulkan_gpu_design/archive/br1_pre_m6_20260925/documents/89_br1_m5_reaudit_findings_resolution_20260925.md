> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1/M5 复审问题修复与最终代码判断（2026-09-25）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。 **本文 M5 整体关闭判断已撤回；既有通过实验保留。**

**结论：以 85 为基线、按 86 的退出条件并纳入 88 的复审反例后，当前 M5 已足够干净，可以作为继续完成 BR1 优化的稳定基础。完整 BR1 优化版本仍未完成；M6/M7、正式 BR1-PERF、生命周期与尾延迟资格继续开放。**

本结论以 Krita 最终源码 `095193d11a1041c31ba92f218ccaea4a8d4f396f` 为准。修复分为 `6ac53223efcb152253786b69ac4a92224151a12a`（进程物理预算、metadata owning 容量、预约统计与诊断收口）和 `095193d11a1041c31ba92f218ccaea4a8d4f396f`（forced-COW selector 采用已测 control 分支）两个提交。85、87、88 保留各自时点的事实，不用后来的结果改写原始反例或实验。

## 四项最终判断

| 问题 | 当前判断 | 代码现实 |
|---|---|---|
| 1. 重构后的管线逻辑是否正确清晰 | **是，达到 M5 范围的关闭条件** | admission、private write、overlay publication、root commit、retirement 的责任边界保持单向；资源增长也改为分配前准入，失败沿现有返回路径回滚。双架构完整矩阵未发现可见性、预算或寿命回归。 |
| 2. 实现是否精练可靠，是否重复造轮子或存在复数权威 | **核心权威已收敛，没有发现同一逻辑主体的复数可写权威** | tile store 负责进程物理驻留，Store controller 负责逻辑 class/domain，MetadataCoordinator 在同一 controller 中计费 owning 容量；预算预约合计由 controller 自身 O(1) 维护。native/generic、current/before、pin/completion 是不同原子性或寿命契约，不是第二份决策实现。 |
| 3. 是否存在大量死代码和不必要分支 | **没有证据支持“大量”存在** | 最终图的 43 个 `unreached-review` 仍只是其他配置、模板/虚调用或待人工复核候选；已有模板调用反例证明不能按静态零边批量删除。COW/default/Busy、失败回滚、单页/多页分支均有行为契约。 |
| 4. 其他冗余 | **M5 阻塞性冗余已清除，剩余为有边界的适配层或后续阶段骨架** | 历史预约槽位扫描、metadata 热路径共享诊断原子、失效 census 字段已经收口；compatibility 状态仍有调用者和寿命反例，不宜为减少类型/分支数量而合并。 |

## 88 中新问题的关闭情况

| 发现 | 最终实现 | 关闭证据 |
|---|---|---|
| P1-A 多 Store 可共同突破进程 RAM 上限 | `KisTileDataStore` 在真实 allocation 与 swap-in 增长前，以实际 `memoryMetric()` 加 pending reservation 对 `tilesHardLimit` 做进程级硬准入；空间不足时先同步请求既有 swapper 回收，不能回收才拒绝 | 8 MiB、swap/pool 为 0：第一个真实 backend 的 6 MiB 写入成功，第二个 6 MiB 写入被拒绝；全局驻留始终为 6 MiB，close 后归零 |
| P1-B metadata owning index/页目录漏计费 | MetadataCoordinator 在 shard 建立及 QHash reserve/insert 之前，按稳定上界向既有 `MetadataArena` bucket 预约；charge 随 retained capacity 存活并随 shard 释放 | 110,616 B 有限预算容纳首个 64-capacity tier；64 页成功，第 65 页在扩容前拒绝，reserved 保持 0，析构后 live=0 |
| P2-A 预约成本扫描历史槽位 | BackingBudgetController 在同一 mutex/invariant 内维护 aggregate 与 durable reserved totals；槽位只保留 token 身份和复用信息 | 历史高水位 16/512/4096 后单次 reserve/release 中位数分别为 91.6665/89.9165/90.5 ns，不再随退休槽位线性增长 |
| P2-B 关闭态仍写共享诊断原子 | 诊断计数下沉到 shard，在已有 shard 锁下更新；冷 `metrics()` 查询时折叠。协议所需 `registeredPages` 保留 | 双架构 Reference/Mutation 与完整矩阵通过；未增加 opt-in 之外的计时路径 |
| P2-C census 失效字段 | architecture gate 增加生产 identifier 绑定检查并重新生成 census、source baseline 与 reverse callgraph | 最终 gate：21 manifest、21 ownership facts、16 census groups、1461 APIs、13725 reverse-call edges、19 external intrusion files；工具自测 6/6 |
| 失败 mutation 清理遗漏 | backend 在 mutation 已进入 `Failed` 时取消 private segment 并终结 anonymous transaction | 资源紧限额、失败、取消、退出相关测试包含在最终双架构矩阵，退出后资源归零 |

这些修复没有增加第二份容量决策：进程物理库存继续由 tile store 决定，PageStore 的逻辑分类继续由 backing controller 决定，metadata 只通过同一 controller 取得容量。两层限制保护不同资源，不能互相替代，也不构成重复权威。

## Selector 的最终处理

在父提交 `6ac53223ef` 上，原冻结 matched-control 实验的 K=1 中位比为 0.997664、单侧 97.5% 下界为 0.976220，未达到 0.98；K=16 通过。随后冻结的 order-balanced 实验中 K=1 中位比为 0.988278、下界为 0.973512，仍未通过；K=16 通过。两组失败样本完整保留，不改口径、不重标为通过。

最终提交直接采用这两次实验中的 control 实现：MutableGuard、无 InputBytesReady、PreserveContents 立即选择 FreshCow。对最终生产库与父提交测得 control 库做完整 `__TEXT,__text` 反汇编比较，arm64 与 x86_64 各自完全一致；对应 SHA-256 分别为 `6c8ee790...faa98` 和 `762de07b...d590`。因此最终生产实现就是已经测量的 control，而不是继续接受失败 candidate 或用第三种选择器形成新权威。

## 最终验证

- 最终提交、tracked source 干净状态下，10 个测试进程在 arm64 与 x86_64 各运行一次：每架构 1,476 passed，总计 **2,952 passed、0 failed、0 skipped**。范围包括 7 套 PageStore/Completion、Painter、tile data store 与 tiled data manager。
- Vulkan foundation compatibility 在同一最终源码构建：arm64 与 x86_64 均 **14 passed、0 failed、0 skipped**。这是构建与合约兼容结论，不是 Vulkan 设备或 GPU 性能资格。
- 产品双 Store 与 metadata/历史高水位探针均绑定 `095193d11a`，tracked status 为空，返回码为 0。
- architecture gate 与 6 个 reachability 工具自测通过；最终 Ninja dry-run 无待构建工作。
- TSAN 仍为 **Inconclusive**。普通压力测试不能代替完整插桩的 race-free 证明；按 86，它是补充资格，不阻止已具备确定性交错和双架构回归的 M5 关闭。

完整证据见 [br1_m5_convergence_20260925](../../../evidence/br1_m5_convergence_20260925/README.md)。

## M5 与完整 BR1 的边界

M5 现在可以冻结：主管线权威、有限资源失败语义、退出归零、结构清单和 forced-COW selector 都有同源码证据。继续删除剩余适配器或把必要分支压成一条路径，反而会模糊 native 多页原子性、generic 单页 completion、current/before 可见性及同步 pin 的不同寿命。

后续工作进入 M6/M7 与正式 BR1-PERF：按 39/68 的预注册矩阵评估 CPU 吞吐、尾延迟、容量和生命周期，并完成 TSAN/toolchain 能力闭环。此前可以说“**M5 足够干净且稳定，可承载 BR1 后续优化**”，不能说“完整 BR1 优化版本已经完成”。
