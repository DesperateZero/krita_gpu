# 01：Stroke 失败、scope 与绘画入口

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。设计依据：92 §8.2–8.3、§9.1–9.3、§9.5；比较基线 `5173c807c87b`，代码行号跟随当前工作树。本篇覆盖 S01/S02/S03，实施记录与剩余出口统一见 92 §15。

## S01：先接通失败与唯一终结

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [KisPageStoreWriteOperation_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreWriteOperation_p.h:7)，`KisPageStoreWriteOperationResult` | 区分未执行、成功、失败；按 92 增补首字节前可重试压力，保留禁止失败后 replay 的语义 |
| 主改 | [PaintDevice strategy](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:280)，`applyPixelOperationImpl` | 保持 typed/bool 的 Operation rollback；由不能处理结果的 void 绘画边界向所属 job 上报。已失败 job 不再执行后续 callback；仅 Unavailable/Borrowed 在工作前 fallback |
| 主改 | [KisPainter](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:682)，`bitBltImpl`，尤其像素结果与 fast copy 分支 | 不得把目标写失败化为“少了一个 dab 但 stroke 成功”；普通 void ABI 向所属失败通道传播 |
| 主改 | [TransactionData](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp:155)，`endTransaction/tryEndTransaction/tryAbortTransaction` | 带结果提交成功后才置 Committed；直接取消恢复主像素与关联状态，拒绝后保持 Cancelling。继续把旧 void 包装的失败接到业务 sink，并处理析构与取消进度 |
| 联动 | [KisTransaction](/Users/apple/krita_gpu/krita/libs/image/kis_transaction.h:89)，`hasMemento/tryEnd`、`commit/tryCommit` 两个重载、`tryEndAndTake/endAndTake`、`revert/tryRevert` | 新 stroke 先检查 memento 准入；tryEnd/tryEndAndTake/tryRevert 失败保留所有权。旧 endAndTake、忽略 revert 结果的 caller 与析构 purge 继续迁移；主事务准入前不启动 interstroke；无 memento 时仅撤回自身 selection/flatten，不可取消其他 active history |
| 联动 | [DataManager](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:358)，`commit/tryCommit/tryAbort`；[backend](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1642)，`commitHistory/prepareHistoryAbort/abortHistory`；[memento](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_memento.h:72)，`saveNewDefaultPixel` | 向上传递 commitHistory 结果，提交失败不继续 restore；abort 预建兼容索引/extent，复验 memento 与 base epoch，再取消并交换已准备存储。当前 O(N) 准备和外层锁仍由 S03/S05/U01 接续 |
| 主改 | [stroke strategy](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:395)，`init/finish/cancelStrokeCallback` | direct 使用 tryEndAndTake，indirect 临时事务使用 tryEnd；失败保留 auto-key/事务。取消成功后才释放 painters/临时 target，最后撤销 auto-key；已交付的不可取消 merge 仍须补多设备结果链 |
| 联动 | [strategy worker 入口](/Users/apple/krita_gpu/krita/libs/image/kis_stroke_strategy.cpp:186)，`requestStrokeFailure/retryStrokeCancellation`；[queue](/Users/apple/krita_gpu/krita/libs/image/kis_strokes_queue.cpp:402)，`failStroke/retryStrokeCancellation`；[stroke](/Users/apple/krita_gpu/krita/libs/image/kis_stroke.cpp:246)，`failStroke/retryCancellation` | 丢弃故障后的新输入和可取消后继，保留已接纳的必需 jobs；输入 owner 尚未抬笔时保留句柄。LoD 只向仍在队列的 buddy 传播，不能给已经完成但仍被强引用的 buddy 填入无人执行的 cancel |
| 联动 | [scheduler](/Users/apple/krita_gpu/krita/libs/image/kis_update_scheduler.cpp:52)，`scheduleCancellationRetry`、`waitForDone/barrierLock` | 失败清理由现有 stroke queue 保活，重试退避 1→100 ms，单个合并 wakeup；异步无新输入仍能推进，显式阻塞 drain 不依赖 GUI timer。接续 S09 的 release/completion 通知和 S10 的压力终结；此退避不证明永久资源拒绝时可成功 |
| 联动 | [extent 存储交换](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTiledExtentManager.cpp:138)，`Data::takePrepared`、`KisTiledExtentManager::takePrepared`；[PaintDevice 缓存失效](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1161)，`invalidateTransactionCache` | 取消前准备实际索引/extent 存储，成功后交换；SuppressUpdates 仅抑制通知，仍须失效缓存。接续 delta 改造时保留此准备/安装边界 |

**实施边界：** job 故障桥仅对已选择整笔失败保证的 cancellable 绘画 job 生效；typed callback 的 false 仍由调用者处理。DataManager、painter 与 iterator 指针权限的详细代码关系、验证和剩余入口见 [01b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01b_pixel_failure_boundaries.md)。`KisPainter::endTransaction/revertTransaction` 在拒绝时保留事务，其他 void caller 的最终恢复责任仍需迁移。取消恢复 default/offset/frame/selection/interstroke；当前 stroke 重试保活不覆盖其他 owner 的拒绝后析构，也不代替 interstroke legacy void command、indirect 合并多设备结果及硬预算下的完整进度。普通 freehand 的跨 dab pending 复用只有错误链完整后才启用；未迁移 callback 继续单操作回退。不能改变 oldData=G0，不能在 callback 已写字节后静默切换路线。

**验证落点：** [KisPainterStrokeCompletionTest](/Users/apple/krita_gpu/krita/libs/ui/tests/KisPainterStrokeCompletionTest.cpp) 通过真实 strategy/scheduler 验证 direct/indirect 临时事务、auto-key、准入/完成拒绝与取消重试；[kis_stroke_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_stroke_test.cpp)、[kis_simple_stroke_strategy_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_simple_stroke_strategy_test.cpp) 验证队列终结和无新输入进度；[kis_transaction_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_transaction_test.cpp)、[kis_painter_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp)、[kis_strokes_queue_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_strokes_queue_test.cpp)、[CpuMutationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp)。新增验证第二页失败、callback 中途失败、finish 失败不入 undo、cancel 后旧 reader 可读、重复终结只发生一次。

## S02：持久 session 与短期 job borrow

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [TransactionData 起点](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp:97)，`init`；[事务声明](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.h) | 为已迁移 stroke 在既有 memento/history 成功后取得 scope token；默认 standalone transaction 不自动改变失败保证 |
| 主改 | [backend batch 生命周期](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:532)，`finishClient/Private::finish`，L505–555 | 最后 client seal 并清线程槽；stroke 路径改为归还 borrow，只有真实边界终结；standalone batch 保留显式 finish |
| 主改 | [backend 创建与选择](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:846)，`beginMutationBatch/beginIteratorMutationScope/writableTransaction`，L808–902 | 每 batch 新 session、线程表定义复用范围；改为已有 history/session 的显式 token 借用，线程表只可做过渡查找桥 |
| 主改 | [session 存储](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:741)，`KisPageMutationSession::Private`；[写入](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:1806)，`beginWriteImpl` | 分开 session 身份与 job 线程身份；同段命中不走 fresh 准备；失败状态与 late guard 仍有唯一 owner |
| 主改 | [write set/admission](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator_p.h:348)，`KisMutationWriteSet`、`KisPageWriteAdmission` | 在原 write set 内实现稳定 slots/incarnation、按需索引和局部并发；不能新建另一份 pending map |
| 联动 | [session 终结](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2069)，`cancel/seal/sealForLegacyUnlock/sealImpl` | 配合 Quiescing、job cut 和子集 seal；归还 guard 与 seal 解耦；S04 决定何时对外可见 |
| 联动 | [base iterator](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_base_iterator.h:25)，构造/析构中的 write/read scope | 析构不再决定 stroke 段结束；读意图、guard 释放和旧 standalone 行为必须分别保留 |
| 联动 | [backend 接口](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h:126)、[PageStore 接口](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.h) | 增补内部 borrow/result 接口；不把新复杂状态塞入每页热记录，维持 layout ceilings |

**启用条件：** S01 错误链、S04 可见性和 S08–S10 的必要进度/资源保证到位。cut 前的已接受 job 与必需子 jobs 可完成，cut 后排队；禁止拒绝旧 job 后又等待它结束，禁止 job 持有自己的 borrow 等 checkpoint。

**验证落点：** [CpuMutationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp)、[PhysicalClaimTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStorePhysicalClaimTest.cpp:659)、[iterators_ng_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_iterators_ng_test.cpp)。覆盖跨 worker 接续、不相交并行、重叠序列化、slot ABA、container 增长、late guard、1/10/1000 dab 无冻结重写的零重复 COW/分配/seal。

## S03：把真实调用者接到 scope，拆掉隐式写后 capture

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [stroke strategy](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:251)，`init/finish/cancel/suspend/resumeStrokeCallback` | scope 绑定实际 transaction/target；indirect 临时 target、mask devices、frame/LoD 不共用可变权限 |
| 主改 | [FreehandStrokeStrategy](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/freehand_stroke.cpp:143)，`doStrokeCallback` | 安装/归还执行 borrow，把 token 传给同步绘画及显式后继 jobs；保留 seed、输入顺序与 painter 亲和性 |
| 主改 | [pixel-operation batch](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1897)，`runCpuMutationOperation` | 默认路径仍建 batch/finish；显式原 memento 路径已借用同一 session 并传播 touched，见 [HS1–HS8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01f_history_owned_mutation_scope.md#history-scope-map)；继续接真实 painter/job 与 current/read footprint |
| 主改 | [manager 写入口](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1734)，`writePageStoreOperation`；[刷新](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1016)，`refreshPageStorePages/Page` | 成功 delta 已接元数据存在性与缓存失效，具体代码关系见 [MR1–MR3](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01d_metadata_refresh_and_pending_visibility.md)；继续接持久 scope 的未 sealed 变更、发布前索引资源准入，失败恢复仍须保留 raw 字节语义 |
| 联动 | [PaintDevice](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1884)，`applyPixelOperation`；[painter](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:526)，fixed-selection 与普通 blt | 内部上下文向下传递；保留同步查询所需 cache invalidation，source/mask/self-copy 的读语义由 S04 明确 |
| 联动 | [indirect merge](/Users/apple/krita_gpu/krita/libs/image/kis_indirect_painting_support.cpp:149)，`mergeToLayerThreaded`；[mask renderer](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/KisMaskingBrushRenderer.cpp) | 保留临时 target→layer 的正确终结、mask 合成 barrier；计入 pen-up 成本，不绕过独立 store scope |

**关键闭环：** 成功 `refreshPageStorePages` 已不再 capture/read；显式 cursor pending 适配及 checkpoint/终结失效已见 [HS1–HS8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01f_history_owned_mutation_scope.md#history-scope-map)。元数据查询只看原 sealed/current 选择；后续仍需将 scope 变更、真实 current 读、完整 checkpoint 与发布前适配准备一起接线。失败回滚保留 exact-view 缓存恢复；undo 仍以已恢复的 immutable view 为准。逐段责任与六组失败反例见 [MR1–MR7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01d_metadata_refresh_and_pending_visibility.md)。

**验证落点：** [freehand_stroke_test](/Users/apple/krita_gpu/krita/libs/ui/tests/freehand_stroke_test.cpp:127)、[FreehandStrokeBenchmark](/Users/apple/krita_gpu/krita/libs/ui/tests/FreehandStrokeBenchmark.cpp:156)、[paint_device_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_paint_device_test.cpp)。这两个 freehand 目标当前使用 broken-test 注册，执行方式和证据限制见 V01，不能默认常规 ctest 已覆盖。

S01 的直接 `endAndTake` 调用点、parent ownership 与命令包装迁移关系见[事务终结调用者清单](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01a_transaction_completion_callers.md)。

S02 的函数级实施关系见 [S02 / SS1–SS10：持久 session、稳定存储与 job 借用](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md)：先核对当前 thread-confined/session、冷热 vector 和原 admission，再按 SS1–SS10 处理 scope、稳定 slots、范围准入、借用、热路径、checkpoint、业务接线、取消和实际计账。该篇将能力实现与默认业务启用分开，列出不能只换容器、删除线程检查或移除 finish 的联动责任。

S02 第二批的稳定 slot、部分取消与容量归还记录见 [01c §10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#reusable-slot-implementation)；后续实际准入、范围借用与局部热访问现见 §12–§14。当前待改的是完整 job 冷资源准入、业务 scope/job/cut、subset/checkpoint 与真实 stroke 接线；范围借用已接 managed/packed 消费者，不能据此关闭 A/B 批、S02 或 M8。

S03 的默认笔刷 multi-dab 实施关系进一步见 [S03 / MD1–MD7：真实 multi-dab 与 painter scope](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01g_multi_dab_and_painter_scope.md#multi-dab-map)：两个异步生产 caller、坐标与页范围、painter 局部 kernel、source/mask 读取、producer cut、失败终结及必要存储分别映射到 MD1–MD7；已有 overload 与尚未接线的默认 stroke 路径分开审查。
