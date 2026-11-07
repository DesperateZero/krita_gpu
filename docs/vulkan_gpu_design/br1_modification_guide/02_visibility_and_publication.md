# 02：读取、checkpoint 与完整发布路径

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。设计依据：92 §9.4–9.5、§10.3；定位基线 `5173c807c87b`。覆盖 S04/S05，部分能力已实现；当前缺口以 92 §16 和 02a 的实现记录为准。

## S04：把读取意图接到真实可见性边界

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [backend 捕获](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1148)，`captureIteratorReadScope/captureReadView`，L1178–1261 | 显式区分 job current、operation-start source、G0 oldData、外部 exact；继续校验 store/access mode；不把 live legacy writer 包装成 immutable view |
| 主改 | [核心 capture](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2684)，`captureReadView` | 原 capture 保留 immutable/retention 保证；在其调用前落实拟新增 checkpoint，不让它直接读取可变 pending |
| 主改 | [段 seal](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2105)，`sealImpl` | 将准备/安装责任复用给完整 checkpoint 与内部 sealSubset；子集存储 seal 不独自推进对外 read selection |
| 主改 | [更新入口](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/freehand_stroke.cpp:228)，`tryDoUpdate/issueSetDirtySignals` | 由实际 projection update 安排 cut、收回相关 borrows、准备完整 delta 后发 dirty；同 revision 可共用 checkpoint |
| 联动 | [read scope/cursor](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreIteratorReadScope.cpp)、[base iterator](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_base_iterator.h:25) | token/read selection 传递与释放时机；旧 exact reader 继续保活，短 pin 不变长期裸指针 |
| 联动 | [projection 调度](/Users/apple/krita_gpu/krita/libs/image/kis_update_scheduler.cpp:163)，`updateProjection`；[merger](/Users/apple/krita_gpu/krita/libs/image/kis_async_merger.cpp:172)，`startMerge` | 核对 checkpoint 的 producer/consumer 生命周期；实际读取结束释放 canonical snapshot，不等到画面消失；必要接口联动，不整套重写 compositor |

**实施次序：** 先定义 cut 与 job 完成条件，再连接 producer/consumer，最后启用跨 dab scope。capture/save 需要完整 cut，必须包含 cut 前 job 的屏幕外页；projection 仅消费某区域不能让完整 view 混入多页半提交。自拷贝/smudge/source snapshot 必须保留算法原来的输入语义。

**禁止捷径：** 不每 dab seal；不把刷新频率降低当优化；不在持有自身 borrow 时等待 checkpoint；不引入 BR2 的未实现显示能力；不取消 save 或明确的 exact capture。

**验证落点：** [ResidentReadTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreResidentReadTest.cpp)、[CpuMutationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp)、[async_merger_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_async_merger_test.cpp)、[update_scheduler_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_update_scheduler_test.cpp)。新增 cut 前/后 job、异步子 job、save+display、跨屏幕边界多页写、慢 reader 与 scope cancel 的交叉验证。

## S05：准备与短安装必须贯穿 backend

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [匿名终结](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:947)，`finishOwnedTransaction`；[history 终结](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1642)，`commitHistory` | 匿名 root 成功后的 cleanup 已移出 publication gate；准备及原 selector 规则保留，history/checkpoint 等外层锁及完整联合交付仍开放，见 02a §4 |
| 主改 | [PublicationCoordinator](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:834)，`commitLocked`，原重试循环；[restore](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1152)，`restoreRetainedEpochLocked` | 保留失效复验；有界重试必须配合 scheduler/原 owner 接续。本批固定三次拒绝破坏并发写保证，已撤回。restore 同样审议 |
| 联动 | [原子安装](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:423)，`KisPreparedMutationCommit::tryInstall` | metadata→descriptor→root 安装顺序及 allocator/rehash/大析构零门不变；准备好 backend/index/history 安装所需存储 |
| 联动 | [metadata 候选](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2157)，`preparePublication`；[root 候选](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:891)，`prepareCommit` | 复用候选准备与 claims；不得因缩锁删除 revision/epoch 校验 |
| 联动 | [manager commit](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:358)、[TransactionData](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp:155) | 检查更外层 manager/history 锁是否覆盖准备；S01 的返回结果与候选失败保持一致 |

**必须共同维护的事实：** commit 会移除 transaction，backend 不能在中间窗口继续返回未保活的旧 transaction id。旧读选择应是有效 immutable handle；root 与选择切换处线性化。M7 在首字节后既不能让出重准备，也不能进入普通失败路径。

**验证落点：** [CpuMutationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp)、[FoundationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreFoundationTest.cpp)与 V01 install allocator probe。新增新 capture 等待、旧 overlay 消失、head 竞争、restore 重试、准备失败及 end-to-end gate hold 分布；仅核心锁缩短不计完成。

原 session 的完整 checkpoint 能力、保留 activity 后再开放、可拒绝边界与测试见 [01c §15 / CP1–CP5](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#checkpoint-implementation)。S04 的业务 job cut/current/exact 读接线、跨 store 协调和 S05 完整准备/短 gate 尚未由这项底层能力关闭。

完整 checkpoint 的原调度切点、已接纳输入/必要子任务/后续输入/finish 的次序见 [S02 / SC1–SC6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01e_scheduler_cut_and_job_admission.md#scheduler-cut-map)；业务持久 scope、producer 与 current/G0/source 仍需联合接线。


**S05 / OP6 当前跨项入口：** [JP1–JP8：联合发布的观察边界与逐段改法](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/02a_joint_publication_boundaries.md#joint-publication-map)。JP1 对应原 overlay 的真实节点/并发桶容量、native/generic/条件删除与 cleanup；JP3 匿名 root 成功清理的读进度子范围见 [02a §4](02a_joint_publication_boundaries.md#commit-preparation-implementation)；JP2–JP8 仍保留 session、surface extent、raw/current 读取、manager gate、其他 history 终结及完整预算。reader-window 已实际复现，候选准备或局部零分配都不能将外层窗口判为已关闭。
