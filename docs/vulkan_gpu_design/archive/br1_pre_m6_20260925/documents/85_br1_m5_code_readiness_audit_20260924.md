> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1/M5 当前工作树代码审计（2026-09-24）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

结论：M5 已完成明显的结构收敛，CPU Fresh 管线可以继续迭代；但仍不满足“足够干净、足够稳定，可关闭 M5 并进入 M6/M7”的条件。本次发现一项可确定性复现的并发记账错误，以及两项预算契约未兑现问题。不能沿用 84 的“21 已闭合 / 3 局部 / 0 未闭合”作为独立验收结论。

审计对象是当前脏工作树，不是 BR0 的 Git HEAD，也不是 82/83 的历史快照。未修改生产代码；仅补充本审计、复现程序与验证证据。证据位于 [本次审计目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_m5_readiness_audit_20260924)。

## 四项判断

| 问题 | 判断 | 依据 |
|---|---|---|
| 重构管线是否正确清晰 | 主干职责与可见性边界清晰，不能宣称整体正确性闭合 | admission → 准备/预算 → 私有写 → overlay seal → root commit → retirement 已能对应明确 owner；domain 同步仍有真实并发错误。 |
| 实现是否精练可靠、是否多份权威 | 核心权威已明显减少，但尚未完全收敛 | 页 writer admission、metadata 转移、root 安装有共同实现；native/generic 的 seal 编排仍分别存在，业务 compatibility 仍持有额外生命周期状态。预算接口和实际 allocator 还存在脱节。 |
| 是否存在大量死代码和不必要分支 | 没有证据支持“核心仍堆积大量可直接删除死代码”；也不能认定已彻底清理 | 旧 keyed writer 容器、shadow 和 source-set 已退出。CPU 调用图仍有测试专用、间接调用及不可达候选，必须区分模板/虚调用、其他构建配置和 BR3 骨架。 |
| 其他冗余 | 仍存在可落实的清理点 | 热路径无条件计时、生产库中的测试专用 provider、兼容状态与回调、未接线预算项，以及文档计数与验收口径偏乐观。 |

## 阻止验收的发现

### 1. P1：domain journal 的旧快照能够覆盖新状态，且不会自行恢复

[KisPageOwnerLedger.cpp:568](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:568) 在 ledger 锁外读取 provider changes，随后在锁内按 domain 差异更新账本；[PhysicalBackingRecord:93](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:93) 未保存最后安装的 sequence。[更新处:612](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:612) 也没有拒绝较旧 sequence。

确定性调度如下：

1. 页 swap-out；同步 A 取得 Ssd 观察后暂停。
2. 页 swap-in；同步 B 取得更新的 CpuRam 观察，安装/确认并清空 journal。
3. 同步 A 恢复，把账本退回 Ssd；确认旧 sequence 时 journal 已空。
4. 再同步一次，由于没有未确认事件，错误账本保持不变。

复现使用实际 `KisTiles3PageReplicaProvider`、实际 swap-out/swap-in 和实际 `KisPageOwnerLedger`；仅在测试 provider 转发层读取快照后加 semaphore，控制两个调用的先后次序，未修改生产实现。输出为：

```text
actual_domain=1 CpuRam=1 ledger_cpu=0 ledger_ssd=16384 pending_journal=0
after_extra_sync: cpu=0 ssd=16384
stale_snapshot_reproduced=1
```

[复现源码](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_m5_readiness_audit_20260924/domain_journal_repro.cpp)、[输出](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_m5_readiness_audit_20260924/domain_journal_repro.log)。这是 ledger 层确定性并发复现；未声称已在交互画笔操作中复现。生产路径也没有统一的外层串行保证：`processRetirements()` 在 Store 锁外运行 queue，失败 Debt 重试会进入相同同步入口，可与前台 backing admission 交叉。

后果包括 RAM/SSD 分类失真、错误预算拒绝或漏限额，以及后续 alias 注册的 footprint mismatch。需要在权威记录安装时校验每个 physical slot 的观察版本，或提供覆盖“取快照—安装—确认”全过程的等价串行协议；只在 provider ack 阶段比较 sequence 不足以修复。

因此 C4.2 的复杂度改善成立，但“可靠增量同步已闭合”应重开。此外，通知序号目前在 [ResidencyObserver::residencyChanged:123](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:123) 才生成；修复时还需验证 storage 解锁后的通知乱序。后者是静态检查提示，本次未另做确定性复现。

### 2. P1：有限预算能力已实现，但没有接入真实 backend 配置

[KisPageBackingLimits:90](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator_p.h:90) 各上限默认是整数最大值；[backend prepareStore:197](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:197) 也把 provider budget 设为 `max()/4`，只执行 provider configure、Store configure 和 register，没有配置 Store backing limits。

源码全局检索和当前调用图均表明 `configureBackingLimits()` 的调用方只有测试；[Store 方法:1889](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:1889) 只是设置控制器，并不会被初始化自动调用。因此“可在测试注入有限预算”和“产品已经运行于有限预算”是两种状态。后者尚未完成，C4.4 不能整体记为闭合。

需要在真实 backend 初始化前接入配置来源，并运行真实业务路径的拒绝、取消、退出和重试矩阵。已有 tiles3 全局 swap 限制不能替代 Current/History/Pending/Debt 等文档级预算契约。

### 3. P2：MetadataArena 是未接线的预算类别

`metadataArenaBytes` 出现在 backing limits，controller 也会检查此类别，但实际 metadata 分配走 [MetadataArenas:53](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:53) 的每 shard 4/8/4 MiB 常量上限，没有向该 bucket 申请或归还预算。

在实际 Store 上设置 `metadataArenaBytes = 0` 后，初始化与两页写入/提交仍成功：

```text
metadata_limit=0 registered_pages=2 page_versions=2 accounted_metadata=0
```

[复现输出](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_m5_readiness_audit_20260924/metadata_budget_repro.log)。这不表示 arena 本身无边界；问题是对外配置与统计不控制真实资源，形成两套不一致的预算表述。应让统一配置进入实际 allocator，或明确删掉/拒绝尚不支持的配置项，不能把空 bucket 计入已覆盖预算。

### 4. P1 验收缺口：swap 在准入之前改变资源，低 SSD 限额会阻塞后续无关工作

[trySwapTileData:346](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_store.cc:346) 先写 swap、改变驻留状态，再通知 provider；ledger 同步时才向预算申请 SSD 分类。[同步拒绝处:608](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:608) 会保留未确认变化，之后其他 allocation/publication 同样可能因它失败。

现有 [finiteBackingLimitMatrix:4225](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:4225) 明确演示：durable capacity 为 0，swap-out 仍成功，后续写入失败，手动 swap-in 才恢复。这是已知 C4.3 未完成项，而不是预算正确拒绝了资源变化的证明。

应在物理域改变前取得可兑现的预约，并对拒绝提供保留原状态或可恢复回退。该问题与发现 1 不同：修好 sequence 并不能补足事前准入。

## 已经收敛的部分，以及仍需压缩的部分

- 唯一页准入：native、generic、managed、legacy 均汇入 `KisPageWriteAdmission`；旧 `controlWritePages`、`mutationPages`、`activeWritablePages`、`operationWritablePages`、`cpuMutationPages` 已不在当前生产 PageStore 源码中。
- 唯一 metadata 转移语义：[StateMachine:132](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine.cpp:132) 的公开与 known-valid 入口共用 `applyImpl`；[compact coordinator:2590](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2590) 调用这份语义。compact records 和 snapshot 投影不应简单判为两份权威状态机。
- Root 发布由 [installReservedRoot:977](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:977) 收口。`KisImageEpochReferenceModel` 虽带 ReferenceModel 名称，实际承担生产 epoch/root 职责，不能当测试死代码移走。
- 读的 native/fallback 持有已共用 [KisPageStoreReadPage](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreIteratorReadScope.cpp:6)。Busy/Invalid 等失败不任意触发物化 fallback，是应该保留的可靠性边界。
- 写策略已共用 base preparation、Fresh provider prepare、private publish/cancel；但 [native seal:1634](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:1634) 和 [generic finish:3373](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3373) 仍各编排 proof 创建、旧 proof detach/revoke、新 proof install 和失败恢复。多页原子 seal 与单 lease 可见性不同，保留两条入口合理；仅共享几个 primitive 也不足以称整个 prepare/seal/cleanup 协议已完全合一。
- 兼容层仍然较重：[backend 私有状态:220](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:220) 包含 anonymous transaction/clients/failure、lease registry、thread batch registry 和 iterator boundaries；[tile:191](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.h:191) 仍维护 native-read-ready、write intent/native pin、bridge 和 leases。它们有真实消费者，应通过业务调用点迁移后一起删除，不能只换名称或搬入新 coordinator。
- owner、metadata、provider 的多层检查不能按“检查重复”批量删：它们分别保护 admission、逻辑版本、真实 allocation/pin。重复数据投影与同一事实被两方独立修改必须区别对待。目前 ownership 清单仍有 5/18 项标为 split；其中也包括为后续 physical handoff 保留的边界，不等同于五个已证实的当前正确性错误。

## 死代码、不必要分支与其他冗余

当前 CPU 调用图为 1,381 APIs，分类为 950 production-boundary、249 indirect-review、139 test-only-review、43 unreached-review。后三类是复核候选，不是 431 个死函数。例：`isOrderedWith()` 在当前 CPU 图中未达，但 Vulkan command/retirement 实际调用；`backingAuthority()` 经模板使用，不能按零直接调用删除。

仍有具体可清理对象：

1. [metadata transition 计时:2576](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2576) 在每次局部转移中无条件读取时钟、更新跨 shard 共享原子总量/最大值。其直接数据消费者目前只有 ReferenceTest 的时间门；与已有 opt-in diagnostic recorder 不一致。应接入既有可关闭采样机制。可以确定额外工作存在，本次未测其吞吐影响，不能给出回退百分比。
2. `KisCpuPageReplicaProvider` 的创建/配置只有测试调用，仍列在生产 [CMakeLists.txt:35](/Users/apple/krita_gpu/krita/libs/image/CMakeLists.txt:35)。它和 Tiles3 provider 的物理存储不同，不应粗暴合并，但应明确属于产品后端还是参考测试支持；若保持现状，就不能声称测试专用实现已全部移出生产。
3. 未接线的 MetadataArena bucket；当前 BR1 无实际入口的 InFlight 等前向类别，应注明适用阶段，避免把枚举存在当作资源协议已实现。
4. 文档中“目录下降”与“删除收益”容易混淆：PageStore 当前确为 33,551 → 26,759，目录减少 6,792 行；其中 1,663 行迁到 tests，排除已记录搬迁后为 5,129 行（约 15.3%）的目录内净减口径。不是全仓净删除统计，也不证明稳定性或性能改善。

没有发现理由把必要 COW/default/Busy/retirement 重试分支列为“无用分支”。这些分支有故障矩阵和寿命语义。更有价值的清理是缩减仍在运行的重复状态和控制工作。

## 本次验证与范围

- 当前源码的 architecture gate 通过：21 manifest entries、18 ownership facts、16 runtime census groups、19 external intrusion files。通过 gate 不代表它能发现本次 sequence 与预算接线问题。
- 本次运行 7 套 PageStore/Completion，7/7 通过；QtTest totals 合计 1,000，无失败。使用当前 CPU 构建的 arm64 路径。
- 检查增量构建后发现 Painter/tiles3 两个测试源还需重编，已完成它们的 universal 编译并重新执行；最终 Painter 99/99、tiles3 334/334（seed 12345）通过，无 FAIL/SAFE ASSERT，日志在证据目录。最终 Ninja dry-run 无待构建工作。
- 初次通过 ctest 启动 Painter 未提供测试资源前缀，停在资源初始化 fatal；补齐现有证据要求的 `KIS_TEST_PREFIX_PATH`、`KIS_TEST_PLUGIN_PATH` 后执行。该环境问题没有记为 PageStore 缺陷。
- 两项新验证均链接当前真实生产库：并发 journal 旧快照覆盖复现、metadata budget=0 不生效复现。未做完整交互产品压测、TSAN 或当前版本 BR1-PERF 配对测量。
- 本次未重新运行 x86_64/Vulkan；84 中的双架构结果属于已有证据。BR1 的 CPU scope 与 BR3 活跃 Vulkan provider 应分开验收，不能为了关闭 CPU M5 把启用 BR3 变为额外前置条件。

## M5 退出顺序

1. 修复并发 journal 安装与通知顺序，加入确定性交错和 ack 回归；C4.2 重开至此通过。
2. 真实 backend 接入有限预算，处理 metadata 配置与 allocator 脱节，并完成 swap 前准入；C4.4 重开，C4.3 保持未完成。
3. 针对实际业务入口压缩 compatibility 状态和重复 seal 编排，保留各自可见性/原子性/线程边界；关闭有范围的 C3.4，不新增平行 authority。
4. 用同源码构建完成 core、Painter、tiles3、有限预算/退出/并发矩阵，再按 39/68 进行 CPU 正式配对性能验收。M5 selector 的 forced-COW 控制桶回退 ≤2% 尚不能由 100 ms read 控制样本或 QtTest 总耗时替代。

建议状态：**M5 结构收敛已有实质进展；正确性与预算验收仍开放；可以继续收口，不宜冻结为 M6/M7 的稳定前置。**
