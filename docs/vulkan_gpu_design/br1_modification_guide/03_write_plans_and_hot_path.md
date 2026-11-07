# 03：首写决策、handoff 与对账热路径

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。设计依据：92 §2–§4、§10.1–10.2；比较基线 `5173c807c87b`，代码链接随当前工作树更新。覆盖 S06/S07，实施记录与剩余出口统一见 92 §15。M6 与 M7 必须分别验收。

## S06：共同决策、不同访问载体

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [WriteCoordinator](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1369)，`prepareWriteBaseLocked`；[select/prepareFreshReplica](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1645) | 当前按 intent 选 Fresh/semantic 等；集中加入 failure policy、恢复/保护事实和 handoff 证明，返回一次性准备结果及拒绝原因 |
| 主改 | [写计划类型](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator_p.h:45)，plan/intent/entry；[admission](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator_p.h:396) | 新字段随真实消费者进入，保留唯一 entry/claims 与 layout 上限；不得增加旁路 selector |
| 主改 | [native 写](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:1806)，`beginWriteImpl`；[generic 写](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3479)，`acquireWrite` | 消费共同计划，保留直接 guard 与 request/lease 两种载体；M6/M7 条件不在两边各写一份 |
| 主改 | [StateMachine](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine.cpp:250)，`AcquireWrite/AcquireRecoverableWrite`；[PublishWrite](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine.cpp:433)、[CancelWrite](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine.cpp:485)、[CommitTransaction](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine.cpp:669) | 工作树已有 recoverable 逻辑原语；生产接入须连同独立 before、物理 claim/retag 和统一终结消费，不能由逻辑成功直接授予可写字节 |
| 主改 | [physical handoff](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp:89)，`KisCpuBackingHandoff::prepare/tryClaim/commit`；[provider](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:789)，`prepareWrite` 及同步 payload/copy；[retire](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:1083) | 将已有 physical claim/retag 原语接入共同候选；保持 provider epoch、slot generation、alias/source/swap 等排斥条件，复用一次消费结果，不重复实现物理身份 owner |
| 联动 | [binding](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp:261)，`reserveWrite/pinReservedWrite`；[allocation index](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding_p.h:166) | 已有 parked writer reservation 继续使用；不能把它等同于对可见 backing 的 handoff 许可。旧 binding identity 失配须拒绝 |
| 联动 | [KisTile 读 cache](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:349)，`lockForRead/refreshPageStoreData` 与 `m_pageStoreNativeReadReady`；[tile bridge](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTilePageStoreBridge.h:17) | M6 启用前让 cache 读取按受保护版本与 expected allocation generation 复验，再取短 pin；retag 后的旧 cache 必须拒绝并重解析，不能仅凭 ready 标记返回复用后的字节。仍存活的 raw pin 必须排除 handoff；具体 adapter 随真实消费者进入，不另建 generation owner；函数级迁移与当前接口缺口见 [03b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03b_legacy_cache_migration.md) |
| 联动 | [provider 契约](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReplicaProvider.h:373)、[元数据发布](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2157)、[最终安装](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:423) | 先准备完整 proof/descriptor/root/预算和终结存储，再消费 claims；M7 首字节后不分配、不失败 |

**避免误映射：** StateMachine 已有 `BeginAuthorityHandoff/CommitAuthorityHandoff`，表示既有 replica authority 转移协议；它不自动提供 M6 的“旧 generation 解绑、physical allocation retag 后写新 generation”资格。不能仅复用名字就跳过物理排斥与恢复证明。

当前 Fresh 管线不复用可见 backing；工作树已有 binding expected identity 校验、physical claim/retag、`prepareRecoverableWrite/installRecoverableWrite` 和 ledger 预备计账/终结债务消费。captured read 已经通过 [discoverCpuReadBinding](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadCoordinator.cpp:303)在原受保护 exact version 上有界重解析；生产共同计划现已在驻留 CPU exact alternate 子集上联合 native/generic、旧 View 和原提交/取消链，具体关系见 [03a §11](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md:149)。legacy tile cache 的迁移和完整联合资格仍待完成；不得重做已经存在的 owner。验证须同时保留旧 View、已解锁但仍存活的旧 tile cache，以及 raw pointer 先到/claim 先到的两种顺序；只测 provider 里的 binding tag 不够。逐段改法、所需凭据、准备/安装/终结和测试关系见 [03a §6–§10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md:76)。

**M6 出口：** 只消费已有Ready exact独立before；没有临时before copy；取消后旧G经alternate可解析；ABA/provider epoch/reader/source/swap/retire两种次序通过，并满足[92 §6.1机会型能力门](../92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)。原20%/30%保留研究目标，不能继续作为当前硬出口，也不追认旧诊断为新门通过。代际消费、真实来源/命中与GPU预测按92 §6.2–§6.3；同段pending复用不重复记handoff，普通异步GPU不取得M7资格。

**M7 出口：** M6 先通过；仅指定受控 kernel，全部 claims 与安装资源在首字节前齐备；≤8 页、≤256 KiB、fence hold P99≤100 μs；普通 brush callback 不加入白名单。

**验证落点：** [ReferenceTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreReferenceTest.cpp)、[CpuMutationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp)、[PhysicalClaimTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStorePhysicalClaimTest.cpp)、[FoundationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreFoundationTest.cpp)。reference helpers 只作 oracle，不成为生产 owner。

## S07：先跳过不必要 reserve，再缩减真正分配的对账

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [reserveBacking](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1582)，`synchronizeBackingDomains` 调用 | 每次新 backing reservation 仍检查 domain 对账；空 journal 可跳过物化，pending 命中仍须消除重复 reserve，新分配可批量核对 |
| 主改 | [OwnerLedger](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:1028)，`synchronizeBackingDomains`，L1005–1088 | 隐式共享 provider 注册表快照，锁外查询 journal 非空提示；只有 dirty/不支持提示的 provider 物化 changes。保留原 revision、bytes、登记与 acknowledge 复验 |
| 联动 | [分类变更](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:1114)，`prepareBackingChanges`；[登记](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:749)，`registerBacking` | 继续使用实际 domain/revision 与 pre-admission；非空提示不缓存 owner 已见 sequence，尚未登记的观察不能提前确认丢弃 |
| 联动 | [provider journal](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:1160)，`mayHaveBackingDomainChanges/backingDomainChanges/acknowledgeBackingDomainChange/registerBackingDomainAdmission` | 原子非空提示随 journal 插入、精确 acknowledge、untrack 同步发布；false 仅代表本次观察为空，不替代 epoch/wrap/多 owner admission |
| 联动 | [TileDataStore residency](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_store.cc:438)，`prepareResidencyChange/commitResidencyChange` | physical domain 变更必须先准入再公开；不能让少读 journal 导致预算少记 |
| 联动 | [provider 默认契约](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReplicaProvider.h:412)、[保守默认实现](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReplicaProvider.cpp:53)，`mayHaveBackingDomainChanges` | 不支持提示的 provider 返回 true，继续原 journal 读取；接口不得等待、分配或回调 owner |

**验证落点：** [CpuMutationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp)、[tile_data_store_test](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tile_data_store_test.cpp)。无变化路径测 provider calls/临时分配；变化路径覆盖登记前观察、revision wrap、swap、多个 alias owners 和准备取消。此项收益独立报告，不以 handoff 命中率代替。
