# 04：回收进度、后台公平性与预算

**当前差集按 [92 §16.36](../92_br1_m6_m8_execution_baseline.md#captured-release-lifecycle)更新：** capture查询与释放共用收费排序版本数组，原释放节点/容量在保护前准备，销毁和部分准入回滚转交同节点；已完成解保护与未接受history交接分事实记住，原read task/Delay继续，锁外实际free后归还原pin。原read ID deques、ack快照和Store聚合也已替代。下一沿同一接受后交接目标整合history/key/scan/pass、detach效果和provider前operation登记；Private/Qt辅助存储、core、本体/runtime及完整退出仍开放。完整CP1未结算；按 [CODE_INDEX](CODE_INDEX.md#captured-release-code-index)与 [API账本](API_CONVERGENCE_MAP.md#captured-release-api-delivery)领取，下方早期专题“下一”按此取差集。

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。设计依据：92 §9.5、§10.4–10.6；比较基线 `5173c807c87b`。覆盖 S08/S09/S10，完整出口均未闭合；S09 已接 CPU pin/completion 事件、无信号有界退避及取消后空通知存储清理；局部预算等待者已接原 CPU 退休队列，前台等待者/全局计账与资源资格仍待闭合，逐段关系见 [04a / R1–R10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md)。必要进度能力是长寿命 stroke scope 的前置条件。

## S08：root 与 version 的共同工作预算

S08 的有界枚举子集已接入原 collector；完整 S08 仍需下表的进度、销毁成本和预算出口。实现身份与测试结论只由 [92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:477)和[本批证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s08_root_slices_20260927/README.md)给出。

| 改动单元 | 实际代码段及联动 | 已落实行为 → 后续修改约束 |
|---|---|---|
| G1：候选集合 | [collectSliceLocked](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp:159)；[Scan](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector_p.h:89) | 每页最多 32 个完整 `KisPageVersion` 身份和 32-bit live mask，替代历史长度的 reachable set；同 generation 不同 default revision 不得合并。继续为候选/队列的实际分配接 S10 计账 |
| G2：root 枚举身份 | [begin / advance / endReachabilityScan](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:1372)；[私有枚举接口](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.h:178)、原 `EpochRootRecord` | 最多 16 个固定游标 slots，cookie 防晚取消；先计入 current，再续扫原有限边界。仅复制版本身份，不复制/保活全部 roots。保护事实仍来自 current、retained count、transaction base count |
| G3：保护释放 | [unlinkUnprotected](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:573)；`releaseSnapshot/finishTransaction` | 原 root 节点保存前后身份；最后保护消失时在 epoch gate 内调整游标，再允许延后销毁。不得跨锁存 QHash iterator，不能因记录尚未析构允许旧 root 复活 |
| G4：publication/restore | [installReservedRoot](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:1080) → `invalidateChangedScans/linkProtected` | 只比较最多 16 个活跃 scan key 的前后完整版本身份；改变的 key 失效，无关 key 继续。安装不分配；新增能引入保护的入口必须并入这一证明，不另建保护登记表 |
| G5：整轮工作上限 | [scheduleLocked](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp:252)；`PageAdmissionBudget/VersionScanBudget/RootVisitBudget`、[冷统计](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.h:276)与[快照出口](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2790) | 最多 16 页、每页最多 32 个历史候选，**整个 pass 共 32 次 root 访问**，含每组起始 current 的一次。就绪 key 分享额度，未完成则续排；仍须补销毁 bytes/nodes 限额、锁占用及多 store 进度证据 |
| G6：detach 前复验 | [collectSliceLocked](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp:159) → `versionSnapshot/applyOwner` | 只在完整且未失效的枚举后，持原 store owner gate 重新取候选的 publication/pin/last-use 状态，再走原 owner transition；不缓存过去的物理可退事实。失效重扫，不完整不 detach |
| G7：取消和继续实施 | [clearLocked / destructor](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp:346)；后续联动 [processQueue](/Users/apple/krita_gpu/krita/libs/image/kis_strokes_queue.cpp:647)、[beginMutationBatch](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:846)与 S02 job borrow | 清理每个原 epoch cursor 后再清扫描状态。后续随 S02 引入 job borrow 后，在持续热点的 job admission 安全点暂缓新写，完成有效扫描后恢复；不持 owner/image 锁等待、不重放像素 callback |

**复杂度边界：** 本批限制一次 pass 的枚举数量及 scan 暂存量，未证明总回收时间或 stroke 尾延迟。每组最多 32 个候选仍可能重走 H 个 roots，总工作随候选组数增长；tree resolve、replica 列表、root/metadata 销毁及 provider 调用有独立成本。持续同页发布可以反复使扫描失效；必须补 G7 的进度控制，不能用已有 32 次上限宣称公平性或硬时间上限。

| 验证内容 | 具体入口 | 对应单元 |
|---|---|---|
| 删除 next/last/all root、真实擦除、异页发布保持游标安全 | [boundedReachabilitySurvivesRootRemoval](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreReferenceTest.cpp:2455) | G2/G3；H=0/1/33/97，完整 oracle 对照 |
| 同页改变和 restore 失效，异页不失效，slots 复用拒绝旧 cookie | [boundedReachabilityInvalidatesOnlyChangedKeys](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreReferenceTest.cpp:2511)、`boundedReachabilitySlotsAndCancellation` | G2/G4/G7 |
| 同 generation 的 default revision 保持独立，旧扫描失效 | [boundedReachabilityPreservesDefaultRevision](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreReferenceTest.cpp:2567) | G1/G4；真实 surface metadata change，无伪造 replica proof |
| 8 页同时分享整个 pass 的 root 限额，保护释放后 payload 收敛 | [multiPageHistorySharesRootBudget](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:1331) | G1/G5/G6；四种 BPP |
| 实际 worker 扫描一半时发布同页/异页，旧 View 字节保持正确 | [historyRootSliceRevalidatesChangedKey](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:1368) | G4/G6；四种 BPP × 两种变更关系 |
| 长历史版本预算、退役 root backlog 不参与可达性 | [longHistoryUsesVersionBudget](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:1270)、`historyReachabilityIgnoresRetiredRootBacklog` | G1/G5；refresh 计候选组，不能沿用一次整页全量扫描的计数含义 |

继续修改必须补持续热点/冷页与两 store 的进度压力、销毁成本和计账故障，并与 S09 就绪债务、S10 可等待准入接线；这些仍是长寿命 stroke scope 的启用前提。

## S09：阻碍解除后主动归还债务与预算

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [retirement record/queue](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue_p.h:28)；[失败与调度](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp:340)，`finishAttemptLocked/schedulePassLocked` | CPU 事件已按独立等待身份把稳定 pending 节点去重移入 ready；无信号记录已由同一 queue 的 retry 分区和单 deadline 调度；已消费局部 budget grant；继续补完整等待原因、前台 S10 waiter 和元数据上界 |
| 主改 | [binding](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp:181)，`releaseRead/releaseWriter` | 最后 pin/writer 解除时提供就绪事件；在物理锁外通知，不重入 owner 形成锁反转 |
| 主改 | [completion](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCompletionRegistry.cpp:213)，`complete/watchTerminal` | 已接 ledger 原 operation 和 queue 消费；terminal 返回 Ready、Pending 登记调度订阅。取消后的空存储已回收，上游已成功 ReleaseRead 的 last-use 已接自动 acknowledge；单次 metadata 终结已按 [04a §12](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#metadata-terminal-implementation)复用原 slot；继续补其他拒绝接续/通知冷失败、外层销毁预算、完整生命周期及存活存储硬预算 |
| 联动 | [queue process/close](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp:436)，`process/retireEffects/waitForIdle/isDrained`；[store close](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2839) | 保留显式兼容 process，关闭通知准入并取消 waiter/deadline，使晚通知失效；idle、drained、closed 不能混同 |
| 联动 | [provider retire](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:1083)、[budget](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:587) | 真实退休与预算归还后唤醒可准入工作；provider 无信号时有界退避，不能依赖下一次编辑 |

**必须实现的交错：** 读状态序列→登记 waiter→复验，解决释放发生在登记前的丢唤醒；record incarnation 解决注销后的晚事件；重复通知只保留一个 ready item。等待不持 payload pin、不占 worker 忙等。

**验证落点：** [现有物理 pin 退休测试](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:3732)、[CompletionRegistryTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisCompletionRegistryTest.cpp)。现有 pin 用例已改为不再编辑、不手动 process 的自主收敛验证，并新增登记前释放、延迟 completion、close 拒绝与直接析构；另有无信号 pin、129 页退避/跨 store、orphan 延迟终态和 timer close/析构场景，逐段见 04a §8；完整交错/资源出口仍继续补齐。

## S10：实际分配点计量，局部与全局不重复收费

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [budget controller](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:650)，`waitForChange/reserveImpl/configureSharedNonPayloadBudget/registerSharedNonPayloadChild/releaseLive`；[预算类型](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator_p.h:98) | 局部 FIFO waiter、真实 grant 与 CPU 退休消费已接；每请求 state 由 context 唯一拥有，state、冷 context 与 prepared wake state 本体实际计入本地/共享父 `MetadataArena`，空载预检含三者。wake 的 dormant/ready 链接与 monitor 引用内嵌，已删除每 wake list node 和 shared control block；析构先释放这些控制存储再注销 child。产品 store 的 metadata/default-cache 与父子注册节点同样受共享总额约束，空闲注册项不静态分额；context/wake 控制块和独立 free-list 已删除；slot 数组通过内嵌冷 reservation 和父 token 实际收费，锁外分配/free、安装后复验。继续补 callback/task/retry/pass/terminal、墓碑实际内存及有原请求 owner 的跨 store 等待 |
| 主改 | [backend policy](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:68)，`deriveProductBackingPolicy/acquireProductNonPayloadBudget`；[prepareStore](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:310) | live product store 复用一个按当前 RAM+pool 配置建立的弱持有父预算；配置在 live store 存在时改变会拒绝，不再把同一非载荷配置按 store 重复。局部上限仍用于单 store 诊断和保护；backend 注册数明确不作为公平需求 |
| 主改 | [TileDataStore](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_store.cc:192)，`reserveResidentMemory/releaseResidentMemoryReservation`；L318 `freeTileData` | 在真实 payload 分配/释放生命周期接全局 charge；registry entry 并不等于一次新物理分配 |
| 联动 | [residency/swap](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_store.cc:438)，residency change、load/swap；[SSD 实物](/Users/apple/krita_gpu/krita/libs/image/tiles3/swap/kis_swapped_data_store.cpp:58) | 准入后才公开 domain 变化；继承当前 swap 路径，不提前假设统一 SSD/GPU production 已开放 |
| 联动 | [OwnerLedger](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:749)、[metadata arena](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataArena_p.h)、[default storage](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageDefaultStorage.cpp) | charge 放真实 allocation/control block；跨 store alias 只全局收费一次，局部 current/history 分类保留 |
| 联动 | [session](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:741)与 S02/S04 | W 窗口和内部 sealSubset 归还活跃 slots/writer；已 staged K-page 必要元数据仍计账，不用清指针伪装释放 |

**实施边界：** 首先固定 RAM/pool/swap 配置的父子包含公式；不能持两层 budget gate 等待；局部失败归还全局 token；保留必要终结记录空间。C01 的缓存接同一受控可选容量，LRU 删除但仍被 snapshot 引用的 bytes 继续计账。

**2026-09-29 已实施的父额度子范围：** `KisBackingBudgetReservation` 在原本地 reservation 内部组合一个父 reservation；`MetadataArena` 与 `OptionalCache` 在父层合并为同一 CPU 非载荷桶，本地仍分别报告。reserve 顺序固定为父→本地，失败由 RAII 归还；commit/release 分步执行，不持两层 mutex。父子注册表使用父 controller 的 budget allocator，节点创建在父 gate 外、安装不再分配，注销在 gate 外析构；1 B 反例证明失败候选不会漏账。真实 tile payload 仍只由 `KisTileDataStore` 的既有进程级上限负责。

父层采用 work-conserving 准入：所有 live/reserved 与注册控制字节共同受总额限制，空闲注册项不分走容量。1024 B 用例验证第二 store 只能取得实际剩余值、额外 1 B 拒绝、第一 store 释放 600 B 后第二 store 可借满 600 B、子项析构归还注册节点且最终父 live 归零。曾尝试的注册数静态 (1/N) 分额已删除，因为一个图像的投影/辅助 backend 会被误当成竞争文档；保持原 24 MiB、pool/swap 为零的真实长 stroke 已重新通过，证明没有用提高预算掩盖该问题。证据见 [本批记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_shared_nonpayload_budget_20260929/README.md)。

这关闭“非载荷共享总额、注册控制存储、空闲 store 不限流与释放返还”子范围。其后 [92 §16.23](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md#budget-waiter-state-storage)关闭每请求 waiter state 和每 controller 冷 context 本体的实际父子收费、唯一所有权与退费，[92 §16.24](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md#budget-wake-state-storage)把 prepared wake state 本体接入同一预算、删除每 wake list node并扩大空载预检，[92 §16.25](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md#wake-control-block-convergence)进一步以内嵌 monitor 引用删除每 wake shared control block；budget waiter 和 read last-use 复用同一个既有入口。[92 §16.27](../92_br1_m6_m8_execution_baseline.md#reservation-storage-admission) 将普通/父 reserve 与 waiter 的 slot 存储统一冷准入；实际数组和增长时新旧共存字节都收费。controller 仍存活时保留的 slot cache 继续收费；不能用请求归零冒充 controller 原始存储已释放。无饥饿公平、等待者跨 store 唤醒、真实多文档并发长笔，以及 callback/task/retry/pass/必要终结存储和 inert anchor 实际内存继续开放。公平必须拥有可取消的原请求身份；禁止以永久 child 标志、注册 backend 数或 stroke 轮询替代。不得据此授予完整 S10、BC9、M6–M8 或自动 continuation 资格。

**验证落点：** [store_limits_test](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_store_limits_test.cpp)、[tile_data_store_test](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tile_data_store_test.cpp)、[swapped_data_store_test](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_swapped_data_store_test.cpp)、[CpuMutationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp)。覆盖 tiny budget、长 stroke、共享 alias、构造/分类失败、慢退休、多文档与 RSS/账本差额；后台未 drain 不能算完整释放。

S09 的具体修改目录见 [04a](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md)：R1–R4 定位通知原语、binding、completion 和 ledger；R5–R8 定位 queue、调度、owner 寿命与 close；R9–R10 连接真实预算归还、资源计量和验证。现有 `watchTerminal` 不代表上述链已经闭合，也不授予 M6/M8 资源资格。

S10 局部等待者的具体接线见 [04b / W1–W8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04b_budget_waiter_implementation_map.md)；仅限制 pending/granted 数量不等于实际元数据硬计账，完整出口按其末节继续。

S09 / T4 的外层空块释放、原预算与 close/idle/abort 责任映射见 [04a §13](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#outer-read-cleanup)；当前仍待修改的是整轮节点/字节/时间上限、其他临时对象、T5 拒绝接续及 T6/S10 必要存储准入。本项不关闭 S09 或 M6–M8。

S09 / T5–T6 的实际安装 gate 核对、completion 存储拒绝原子性与后续必要准入责任见 [04a §14](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#completion-failure-atomicity)；本批不建立基于未证实交错的轮询队列，也不把保留 Pending 当作自动接续完成。

读请求/lease/provider 准备与保护、pin、取消和退出的代码关系见 [04a §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#read-storage-admission)；T6/S10 的必要通知、派发、retry/pass 存储及全局计账继续开放。

<a id="retained-storage-budget-delivery"></a>
## CP1 当前收费寿命交付与下一差集

[92 §16.30](../92_br1_m6_m8_execution_baseline.md#retained-storage-owner)已把实际wake/context、已预算typed task与read/retirement弱控制块接到原allocator的retained收费寿命。controller后存储保留原共享父/child身份和全局费用，最后physical free才退费/注销；不pin PageStore/payload、不授予mutation权限。read冷准备不持原store owner gate，失败保留request/debt并在原gate外释放候选。普通raw存储继续由原scope保证controller寿命。

本项不代表所有callback/control/pass已收费。下一段按 [实际清点](CODE_INDEX.md#retained-storage-code-index)关闭外置capture、deadline节点、record/orphan容器、其余task、pass scratch、terminal/runtime的真实bytes、必需冷预留、硬满失败/自主恢复与最后释放。不得在最后引用归还时申请新容量，也不以32个waiter上限替代真实全局字节界。当前CP1和正式阶段仍未结算。

[92 §16.64](../92_br1_m6_m8_execution_baseline.md#resident-binding-storage-delivery)进一步把原CPU binding对象及实际shared控制块接同observer retained allocator。prepareAdoption先于像素准备，所有guard/reservation/handoff/cache/link共用一份原记录；晚native pin、provider/controller退出及weak-control最后free精确归费。binding的Qt构造/持有已删除，不重领；metadata link本体/Qt控制块、read cache、provider/observer/Transition、bootstrap及完整永久尾出口仍欠。首轮24MiB组合freehand出现checkpoint metadata容量拒绝，单独/组合复验通过仍不关闭该反例，实际证据见[本批记录](../evidence/br1_resident_binding_storage_20261003/README.md)。

[92 §16.65](../92_br1_m6_m8_execution_baseline.md#checkpoint-preparation-pressure-delivery)确认该324页detachment为无用发布载荷申请269568字节；同候选仅保留共同事实后实测20976字节。父预算硬满后的安装/取消及原分批释放通过，普通publication多40字节头部/一次数组分配。配置夹具只在静止边界drain；后续surface8304字节拒绝及8MiB backend初始准入仍欠，完整Store/bootstrap峰值和最后释放按同一CP1继续，见[证据](../evidence/br1_checkpoint_pressure_20261003/README.md)。

当前task/terminal事实按 [92 §16.31](../92_br1_m6_m8_execution_baseline.md#prepared-reclamation-tasks)更新：原history/退休pass、budget/read context和退休wait已冷准备实际收费node，terminal在任何physical adoption前准备且收费到controller后free；重复投递分配已经删除，不再领取。剩余callback/deadline/record/pass scratch、tree/deferred cleanup任务和runtime/clock仍按 [当前差集](CODE_INDEX.md#prepared-reclamation-code-index)关闭准入、保债、进度与最后free。prepared enqueue不能证明整个pass零分配或完整CP1通过。

当前§16.31表中的capture/subscription/deadline节点欠项已由 [92 §16.32](../92_br1_m6_m8_execution_baseline.md#callback-storage-convergence) 更新：一个实际typed捕获冷收费，copy只retain；subscription/signal/registry readiness真实节点与控制块沿原付款owner收费，deadline节点嵌入原state。W3含实际notify/wake捕获大小，永久不可满足判定先于cache准备；producer链接/通知预备节点，不重建外置function。cancel/in-flight/弱尾到physical free才退费；read/binding/registry/backing门外准备，原身份重验。不会再领取已删除的std::function/map额外节点/QP包装或prepared task投递分配。

唯一retirement record和原queue冷retry已由§16.33–16.34交付，read/capture原终结已由§16.35–16.36交付，不再领取旧容器、task或通知框架。当前 [92 §16.37](../92_br1_m6_m8_execution_baseline.md#history-handoff-lifecycle)把history的key/扫描/未接受效果放入同一收费Work，前台/后台共用有界pass；原退休record在物理准入前准备operation node，效果交接消费注册时固定的线程许可，有效provider result只绑定/轮询。实际key/Debt拒绝复用原任务和冷Delay自主继续，原效果和operation恰满交接通过。

下一沿同一metadata/ledger准备边界处理historySlice/versionSnapshot/pageKeys及discard/effects/Debt的Qt容量，不另建效果队列。泛型provider operation、tree/deferred、close handles/seen、capture辅助存储、Store/registry/provider本体及runtime固定成本、永久压力退出继续开放。实际映射维护 [CODE_INDEX](CODE_INDEX.md#history-handoff-code-index)、[API](API_CONVERGENCE_MAP.md#history-handoff-api-delivery)，完整CP1未结算；恰满目标不证明全部pass零分配或全局bad_alloc原子性。
