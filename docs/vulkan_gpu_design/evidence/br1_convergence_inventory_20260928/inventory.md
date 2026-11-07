# BR1 当前改动文件清点（冻结）

源码身份和方法见 [inventory.json](inventory.json)。当前执行目标见 [收敛目标与改动清点](../../br1_modification_guide/CONVERGENCE_CHECKLIST.md)。

范围为相对当前产品 HEAD 的未提交改动，包含未跟踪 C/C++，排除构建目录和测试输出图片。分组用于分配审查责任，不表示每个 diff hunk 都完成了语义审查；同文件跨项关系仍按 CODE_INDEX。

| 分类 | 文件 | 增加 | 删除 | 净增 |
|---|---:|---:|---:|---:|
| other | 3 | 22 | 3 | 19 |
| generated_audit | 6 | 105750 | 41326 | 64424 |
| production_source | 90 | 9954 | 2145 | 7809 |
| test_source | 25 | 11153 | 152 | 11001 |

## 事务与失败传播

对应 S01/BC1/BC7。处置：保留；补齐业务 caller，终结协议收敛。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/KisStrokeJobFailureContext.cpp](/Users/apple/krita_gpu/krita/libs/image/KisStrokeJobFailureContext.cpp) | 31 | 0 | 新增未跟踪源码 |
| [libs/image/KisStrokeJobFailureContext.h](/Users/apple/krita_gpu/krita/libs/image/KisStrokeJobFailureContext.h) | 32 | 0 | 新增未跟踪源码 |
| [libs/image/kis_simple_stroke_strategy.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_simple_stroke_strategy.cpp) | 8 | 1 | tracked diff |
| [libs/image/kis_simple_stroke_strategy.h](/Users/apple/krita_gpu/krita/libs/image/kis_simple_stroke_strategy.h) | 7 | 0 | tracked diff |
| [libs/image/kis_stroke_strategy.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_stroke_strategy.cpp) | 21 | 0 | tracked diff |
| [libs/image/kis_stroke_strategy.h](/Users/apple/krita_gpu/krita/libs/image/kis_stroke_strategy.h) | 25 | 0 | tracked diff |
| [libs/image/kis_transaction.h](/Users/apple/krita_gpu/krita/libs/image/kis_transaction.h) | 67 | 8 | tracked diff |
| [libs/image/kis_transaction_data.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp) | 188 | 14 | tracked diff |
| [libs/image/kis_transaction_data.h](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.h) | 29 | 1 | tracked diff |
| [libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp) | 47 | 28 | tracked diff |

## 调度与 cut

对应 S01/S02/S04/BC6。处置：保留；接真实 producer，不重建调度器。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/KisStrokesQueueMutatedJobInterface.h](/Users/apple/krita_gpu/krita/libs/image/KisStrokesQueueMutatedJobInterface.h) | 5 | 0 | tracked diff |
| [libs/image/kis_stroke.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_stroke.cpp) | 89 | 2 | tracked diff |
| [libs/image/kis_stroke.h](/Users/apple/krita_gpu/krita/libs/image/kis_stroke.h) | 14 | 1 | tracked diff |
| [libs/image/kis_strokes_queue.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_strokes_queue.cpp) | 60 | 1 | tracked diff |
| [libs/image/kis_strokes_queue.h](/Users/apple/krita_gpu/krita/libs/image/kis_strokes_queue.h) | 5 | 0 | tracked diff |
| [libs/image/kis_update_scheduler.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_update_scheduler.cpp) | 27 | 1 | tracked diff |

## Painter/设备写接口

对应 S03/S04/BC2–BC5。处置：接通后合并重复分支；保留未迁移消费者。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/brushengine/kis_paintop_utils.cpp](/Users/apple/krita_gpu/krita/libs/image/brushengine/kis_paintop_utils.cpp) | 7 | 0 | tracked diff |
| [libs/image/brushengine/kis_paintop_utils.h](/Users/apple/krita_gpu/krita/libs/image/brushengine/kis_paintop_utils.h) | 4 | 0 | tracked diff |
| [libs/image/kis_paint_device.cc](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc) | 74 | 2 | tracked diff |
| [libs/image/kis_paint_device.h](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.h) | 49 | 0 | tracked diff |
| [libs/image/kis_paint_device_strategies.h](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h) | 96 | 13 | tracked diff |
| [libs/image/kis_painter.cc](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc) | 153 | 106 | tracked diff |
| [libs/image/kis_painter.h](/Users/apple/krita_gpu/krita/libs/image/kis_painter.h) | 30 | 2 | tracked diff |
| [libs/image/kis_painter_blt_multi_fixed.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_painter_blt_multi_fixed.cpp) | 92 | 57 | tracked diff |
| [libs/image/kis_painter_p.h](/Users/apple/krita_gpu/krita/libs/image/kis_painter_p.h) | 12 | 6 | tracked diff |

## 实际 brush producer

对应 S03/BC2/BC3/BC6。处置：首条链接入；保留页分区及并行。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [plugins/paintops/defaultpaintops/brush/kis_brushop.cpp](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp) | 44 | 17 | tracked diff |
| [plugins/paintops/defaultpaintops/brush/kis_brushop.h](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.h) | 4 | 0 | tracked diff |

## Tiles3 adapter/extent/hash

对应 S03/S04/S05/U01/HX7。处置：关闭联合可见性；删除全量恢复另需消费者证据。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/tiles3/KisTilePageStoreBridge.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTilePageStoreBridge.h) | 11 | 2 | tracked diff |
| [libs/image/tiles3/KisTiledExtentManager.cpp](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTiledExtentManager.cpp) | 147 | 33 | tracked diff |
| [libs/image/tiles3/KisTiledExtentManager.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTiledExtentManager.h) | 24 | 2 | tracked diff |
| [libs/image/tiles3/kis_base_iterator.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_base_iterator.h) | 13 | 1 | tracked diff |
| [libs/image/tiles3/kis_memento.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_memento.h) | 6 | 2 | tracked diff |
| [libs/image/tiles3/kis_tile.cc](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc) | 74 | 18 | tracked diff |
| [libs/image/tiles3/kis_tile.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.h) | 10 | 7 | tracked diff |
| [libs/image/tiles3/kis_tile_data_store.cc](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_store.cc) | 90 | 35 | tracked diff |
| [libs/image/tiles3/kis_tile_data_store.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_store.h) | 11 | 0 | tracked diff |
| [libs/image/tiles3/kis_tile_data_wrapper.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_wrapper.h) | 5 | 1 | tracked diff |
| [libs/image/tiles3/kis_tile_hash_table.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_hash_table.h) | 28 | 0 | tracked diff |
| [libs/image/tiles3/kis_tile_hash_table2.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_hash_table2.h) | 228 | 124 | tracked diff |
| [libs/image/tiles3/kis_tile_hash_table_p.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_hash_table_p.h) | 40 | 0 | tracked diff |
| [libs/image/tiles3/kis_tiled_data_manager.cc](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc) | 480 | 64 | tracked diff |
| [libs/image/tiles3/kis_tiled_data_manager.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.h) | 23 | 1 | tracked diff |
| [libs/image/tiles3/kis_tiled_data_manager_p.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager_p.h) | 6 | 1 | tracked diff |

## 并发 map/QSBR

对应 HX1–HX10/JP8/S09/S10。处置：保留已测存储能力；测关闭/等待/维护，暂停无反例重写。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/3rdparty/lock_free_map/concurrent_map.h](/Users/apple/krita_gpu/krita/libs/image/3rdparty/lock_free_map/concurrent_map.h) | 443 | 87 | tracked diff |
| [libs/image/3rdparty/lock_free_map/leapfrog.h](/Users/apple/krita_gpu/krita/libs/image/3rdparty/lock_free_map/leapfrog.h) | 108 | 62 | tracked diff |
| [libs/image/3rdparty/lock_free_map/qsbr.h](/Users/apple/krita_gpu/krita/libs/image/3rdparty/lock_free_map/qsbr.h) | 143 | 71 | tracked diff |
| [libs/image/3rdparty/lock_free_map/simple_job_coordinator.h](/Users/apple/krita_gpu/krita/libs/image/3rdparty/lock_free_map/simple_job_coordinator.h) | 19 | 3 | tracked diff |

## Session/稳定存储/backend

对应 S02/S03/S04/S05/BC/JP。处置：同一原 owner 联合交付；压缩接口在整链通过后。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/pagestore/KisMutationStorage_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisMutationStorage_p.h) | 497 | 0 | 新增未跟踪源码 |
| [libs/image/pagestore/KisPageStore.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp) | 1035 | 332 | tracked diff |
| [libs/image/pagestore/KisPageStore.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.h) | 93 | 8 | tracked diff |
| [libs/image/pagestore/KisPageStoreTypes.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreTypes.h) | 9 | 0 | tracked diff |
| [libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp) | 551 | 75 | tracked diff |
| [libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h) | 54 | 6 | tracked diff |

## Publication/metadata

对应 S04/S05/JP1–JP7。处置：联合 page/surface/adapter 发布；保留原唯一选择器。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/pagestore/KisPageMetadataCoordinator.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp) | 374 | 73 | tracked diff |
| [libs/image/pagestore/KisPageMetadataCoordinator.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.h) | 42 | 4 | tracked diff |
| [libs/image/pagestore/KisPageMetadataCoordinator_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator_p.h) | 26 | 0 | tracked diff |
| [libs/image/pagestore/KisPagePublicationCoordinator.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp) | 246 | 169 | tracked diff |
| [libs/image/pagestore/KisPagePublicationCoordinator_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator_p.h) | 36 | 18 | tracked diff |

## 写计划/provider/ledger

对应 S06/S07/S10。处置：保护 Fresh 与已有能力；M6/M7 独立验收。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/pagestore/KisPageOwnerLedger.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp) | 301 | 47 | tracked diff |
| [libs/image/pagestore/KisPageOwnerLedger.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.h) | 39 | 0 | tracked diff |
| [libs/image/pagestore/KisPageReplicaProvider.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReplicaProvider.cpp) | 5 | 0 | tracked diff |
| [libs/image/pagestore/KisPageReplicaProvider.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReplicaProvider.h) | 6 | 0 | tracked diff |
| [libs/image/pagestore/KisPageStateMachine.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine.cpp) | 31 | 2 | tracked diff |
| [libs/image/pagestore/KisPageStateMachine.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine.h) | 6 | 1 | tracked diff |
| [libs/image/pagestore/KisPageWriteCoordinator.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp) | 965 | 253 | tracked diff |
| [libs/image/pagestore/KisPageWriteCoordinator_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator_p.h) | 138 | 20 | tracked diff |
| [libs/image/pagestore/KisTiles3PageReplicaProvider.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp) | 186 | 15 | tracked diff |
| [libs/image/pagestore/KisTiles3PageReplicaProvider.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.h) | 7 | 0 | tracked diff |

## 读保护/驻留/readiness

对应 S06/S09/S10/JP5。处置：保留读保护与唤醒职责；不并入 job 错误状态。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/pagestore/KisCpuResidentBinding.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp) | 177 | 23 | tracked diff |
| [libs/image/pagestore/KisCpuResidentBinding_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding_p.h) | 84 | 16 | tracked diff |
| [libs/image/pagestore/KisPageReadCoordinator.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadCoordinator.cpp) | 444 | 87 | tracked diff |
| [libs/image/pagestore/KisPageReadCoordinator_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadCoordinator_p.h) | 90 | 20 | tracked diff |
| [libs/image/pagestore/KisPageReadiness.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadiness.cpp) | 106 | 0 | 新增未跟踪源码 |
| [libs/image/pagestore/KisPageReadiness_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadiness_p.h) | 57 | 0 | 新增未跟踪源码 |

## 预算、退休与维护

对应 S08/S09/S10/JP8。处置：补全默认启用所需收费/进度边界。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/pagestore/KisCompletionRegistry.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCompletionRegistry.cpp) | 163 | 55 | tracked diff |
| [libs/image/pagestore/KisCompletionRegistry.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCompletionRegistry.h) | 16 | 2 | tracked diff |
| [libs/image/pagestore/KisImageEpochReferenceModel.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp) | 127 | 0 | tracked diff |
| [libs/image/pagestore/KisImageEpochReferenceModel.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.h) | 21 | 0 | tracked diff |
| [libs/image/pagestore/KisPageHistoryCollector.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp) | 86 | 32 | tracked diff |
| [libs/image/pagestore/KisPageHistoryCollector_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector_p.h) | 11 | 4 | tracked diff |
| [libs/image/pagestore/KisPageMetadataArena_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataArena_p.h) | 40 | 1 | tracked diff |
| [libs/image/pagestore/KisPageRetirementQueue.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp) | 298 | 26 | tracked diff |
| [libs/image/pagestore/KisPageRetirementQueue_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue_p.h) | 47 | 12 | tracked diff |
| [libs/image/pagestore/KisPageStoreReclamation.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreReclamation.cpp) | 267 | 13 | tracked diff |
| [libs/image/pagestore/KisPageStoreReclamation_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreReclamation_p.h) | 49 | 0 | tracked diff |

## 诊断与因果指标

对应 V01。处置：补真实链分段；关闭时保持无热时钟/跨 shard 原子。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/pagestore/KisPageStoreDiagnostics.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreDiagnostics.cpp) | 8 | 3 | tracked diff |
| [libs/image/pagestore/KisPageStoreDiagnostics_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreDiagnostics_p.h) | 42 | 0 | tracked diff |

## 像素 kernel 修正

对应 S03/V01。处置：保留语义回归；独立解释与 upstream 的预期差异。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/pigment/compositeops/KoOptimizedCompositeOpAlphaDarken128.h](/Users/apple/krita_gpu/krita/libs/pigment/compositeops/KoOptimizedCompositeOpAlphaDarken128.h) | 35 | 48 | tracked diff |
| [libs/pigment/compositeops/KoOptimizedCompositeOpOver128.h](/Users/apple/krita_gpu/krita/libs/pigment/compositeops/KoOptimizedCompositeOpOver128.h) | 3 | 1 | tracked diff |
| [libs/pigment/compositeops/KoOptimizedCompositeOpOver32.h](/Users/apple/krita_gpu/krita/libs/pigment/compositeops/KoOptimizedCompositeOpOver32.h) | 7 | 5 | tracked diff |

## 测试与测试注册

对应 V01及对应被测 ID。处置：保留独立反例；补整链，重复计数不作新增能力。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [libs/image/tests/KisCompletionRegistryTest.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/KisCompletionRegistryTest.cpp) | 361 | 0 | tracked diff |
| [libs/image/tests/KisPageStoreCpuMutationTest.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp) | 2675 | 62 | tracked diff |
| [libs/image/tests/KisPageStorePhysicalClaimTest.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStorePhysicalClaimTest.cpp) | 863 | 18 | tracked diff |
| [libs/image/tests/KisPageStoreReferenceTest.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreReferenceTest.cpp) | 1429 | 12 | tracked diff |
| [libs/image/tests/KisPageStoreResidentReadTest.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreResidentReadTest.cpp) | 459 | 14 | tracked diff |
| [libs/image/tests/kis_painter_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp) | 1032 | 1 | tracked diff |
| [libs/image/tests/kis_painter_test.h](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.h) | 35 | 0 | tracked diff |
| [libs/image/tests/kis_simple_stroke_strategy_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/kis_simple_stroke_strategy_test.cpp) | 152 | 0 | tracked diff |
| [libs/image/tests/kis_simple_stroke_strategy_test.h](/Users/apple/krita_gpu/krita/libs/image/tests/kis_simple_stroke_strategy_test.h) | 5 | 0 | tracked diff |
| [libs/image/tests/kis_stroke_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/kis_stroke_test.cpp) | 154 | 0 | tracked diff |
| [libs/image/tests/kis_stroke_test.h](/Users/apple/krita_gpu/krita/libs/image/tests/kis_stroke_test.h) | 8 | 0 | tracked diff |
| [libs/image/tests/kis_strokes_queue_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/kis_strokes_queue_test.cpp) | 298 | 7 | tracked diff |
| [libs/image/tests/kis_strokes_queue_test.h](/Users/apple/krita_gpu/krita/libs/image/tests/kis_strokes_queue_test.h) | 9 | 0 | tracked diff |
| [libs/image/tests/kis_transaction_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/kis_transaction_test.cpp) | 568 | 7 | tracked diff |
| [libs/image/tests/kis_transaction_test.h](/Users/apple/krita_gpu/krita/libs/image/tests/kis_transaction_test.h) | 21 | 2 | tracked diff |
| [libs/image/tests/pagestore/KisCpuPageReplicaProvider.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/pagestore/KisCpuPageReplicaProvider.cpp) | 6 | 7 | tracked diff |
| [libs/image/tests/scheduler_utils.h](/Users/apple/krita_gpu/krita/libs/image/tests/scheduler_utils.h) | 16 | 4 | tracked diff |
| [libs/image/tiles3/tests/kis_lockless_stack_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_lockless_stack_test.cpp) | 784 | 1 | tracked diff |
| [libs/image/tiles3/tests/kis_lockless_stack_test.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_lockless_stack_test.h) | 24 | 1 | tracked diff |
| [libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp) | 1525 | 16 | tracked diff |
| [libs/image/tiles3/tests/kis_tiled_data_manager_test.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.h) | 48 | 0 | tracked diff |
| [libs/ui/tests/CMakeLists.txt](/Users/apple/krita_gpu/krita/libs/ui/tests/CMakeLists.txt) | 1 | 0 | tracked diff |
| [libs/ui/tests/KisPainterStrokeCompletionTest.cpp](/Users/apple/krita_gpu/krita/libs/ui/tests/KisPainterStrokeCompletionTest.cpp) | 368 | 0 | 新增未跟踪源码 |
| [plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.cpp](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.cpp) | 306 | 0 | tracked diff |
| [plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.h](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.h) | 6 | 0 | tracked diff |

## 构建与架构规则

对应 V01。处置：随实际源码更新；不放宽约束换通过。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [build-tools/ci-scripts/check-pagestore-architecture.py](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/check-pagestore-architecture.py) | 12 | 3 | tracked diff |
| [libs/image/CMakeLists.txt](/Users/apple/krita_gpu/krita/libs/image/CMakeLists.txt) | 2 | 0 | tracked diff |
| [libs/pigment/CMakeLists.txt](/Users/apple/krita_gpu/krita/libs/pigment/CMakeLists.txt) | 8 | 0 | tracked diff |

## 生成审计与 manifest

对应 V01。处置：机械刷新且保留可复现来源；不计生产复杂度。

| 文件 | 增加 | 删除 | 来源 |
|---|---:|---:|---|
| [build-tools/ci-scripts/pagestore-audit/README.md](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/README.md) | 6 | 6 | tracked diff |
| [build-tools/ci-scripts/pagestore-audit/baseline-source.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/baseline-source.json) | 1694 | 298 | tracked diff |
| [build-tools/ci-scripts/pagestore-audit/intrusion-manifest.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/intrusion-manifest.json) | 2 | 2 | tracked diff |
| [build-tools/ci-scripts/pagestore-audit/reverse-callgraph.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/reverse-callgraph.json) | 103850 | 40982 | tracked diff |
| [build-tools/ci-scripts/pagestore-audit/runtime-census.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/runtime-census.json) | 3 | 3 | tracked diff |
| [build-tools/ci-scripts/pagestore-audit/state-ownership.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/state-ownership.json) | 195 | 35 | tracked diff |
