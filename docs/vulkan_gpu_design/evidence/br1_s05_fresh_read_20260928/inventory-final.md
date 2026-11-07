# 本批最终代码清点

HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含未跟踪源码的差异 SHA-256 `73c04adf447603eaad0cfd272f0d055136a6c8c833cd8f73bc00ee9b3a0f84a3`。

本表是未提交改动相对 HEAD 的规模；不是整个 BR1 相对 upstream 的差异，也不是质量分数。本批相对 JP4 的实际生产/测试增量见 [final-increment.patch](final-increment.patch)。

| 类别 | 文件 | 增加 | 删除 | 净增 |
|---|---:|---:|---:|---:|
| other | 3 | 22 | 3 | 19 |
| generated_audit | 6 | 108859 | 42010 | 66849 |
| production_source | 90 | 10345 | 2243 | 8102 |
| test_source | 25 | 11684 | 181 | 11503 |

## 本批改变的文件

| 文件 | 类型 | 相对 HEAD 增加 / 删除 |
|---|---|---|
| [build-tools/ci-scripts/pagestore-audit/baseline-source.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/baseline-source.json) | generated_audit | 1703 / 294 |
| [build-tools/ci-scripts/pagestore-audit/intrusion-manifest.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/intrusion-manifest.json) | generated_audit | 16 / 10 |
| [build-tools/ci-scripts/pagestore-audit/reverse-callgraph.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/reverse-callgraph.json) | generated_audit | 106936 / 41662 |
| [libs/image/pagestore/KisCpuResidentBinding.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp) | production_source | 184 / 23 |
| [libs/image/pagestore/KisCpuResidentBinding_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding_p.h) | production_source | 87 / 16 |
| [libs/image/pagestore/KisPageStore.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp) | production_source | 1065 / 333 |
| [libs/image/pagestore/KisPageStore.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.h) | production_source | 106 / 8 |
| [libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp) | production_source | 664 / 150 |
| [libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h) | production_source | 60 / 8 |
| [libs/image/pagestore/KisTiles3PageReplicaProvider.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp) | production_source | 195 / 15 |
| [libs/image/pagestore/KisTiles3PageReplicaProvider.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.h) | production_source | 8 / 0 |
| [libs/image/tiles3/kis_base_iterator.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_base_iterator.h) | production_source | 15 / 3 |
| [libs/image/tiles3/kis_tile.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.h) | production_source | 11 / 7 |
| [libs/image/tiles3/kis_tile_data_wrapper.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_wrapper.h) | production_source | 8 / 2 |
| [libs/image/tiles3/kis_tiled_data_manager.cc](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc) | production_source | 506 / 72 |
| [libs/image/tiles3/kis_tiled_data_manager.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.h) | production_source | 26 / 1 |
| [libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp) | test_source | 1983 / 44 |
| [libs/image/tiles3/tests/kis_tiled_data_manager_test.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.h) | test_source | 64 / 0 |

## 完整文件级清点

| 文件 | 责任路由 | 增加 / 删除 | 本批变更 |
|---|---|---|---|
| [build-tools/ci-scripts/check-pagestore-architecture.py](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/check-pagestore-architecture.py) | 构建与架构规则 | 12 / 3 | 原 JP4 检查点改动 |
| [build-tools/ci-scripts/pagestore-audit/README.md](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/README.md) | 生成审计与 manifest | 6 / 6 | 原 JP4 检查点改动 |
| [build-tools/ci-scripts/pagestore-audit/baseline-source.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/baseline-source.json) | 生成审计与 manifest | 1703 / 294 | 是 |
| [build-tools/ci-scripts/pagestore-audit/intrusion-manifest.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/intrusion-manifest.json) | 生成审计与 manifest | 16 / 10 | 是 |
| [build-tools/ci-scripts/pagestore-audit/reverse-callgraph.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/reverse-callgraph.json) | 生成审计与 manifest | 106936 / 41662 | 是 |
| [build-tools/ci-scripts/pagestore-audit/runtime-census.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/runtime-census.json) | 生成审计与 manifest | 3 / 3 | 原 JP4 检查点改动 |
| [build-tools/ci-scripts/pagestore-audit/state-ownership.json](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/state-ownership.json) | 生成审计与 manifest | 195 / 35 | 原 JP4 检查点改动 |
| [libs/image/3rdparty/lock_free_map/concurrent_map.h](/Users/apple/krita_gpu/krita/libs/image/3rdparty/lock_free_map/concurrent_map.h) | 并发 map/QSBR | 443 / 87 | 原 JP4 检查点改动 |
| [libs/image/3rdparty/lock_free_map/leapfrog.h](/Users/apple/krita_gpu/krita/libs/image/3rdparty/lock_free_map/leapfrog.h) | 并发 map/QSBR | 108 / 62 | 原 JP4 检查点改动 |
| [libs/image/3rdparty/lock_free_map/qsbr.h](/Users/apple/krita_gpu/krita/libs/image/3rdparty/lock_free_map/qsbr.h) | 并发 map/QSBR | 143 / 71 | 原 JP4 检查点改动 |
| [libs/image/3rdparty/lock_free_map/simple_job_coordinator.h](/Users/apple/krita_gpu/krita/libs/image/3rdparty/lock_free_map/simple_job_coordinator.h) | 并发 map/QSBR | 19 / 3 | 原 JP4 检查点改动 |
| [libs/image/CMakeLists.txt](/Users/apple/krita_gpu/krita/libs/image/CMakeLists.txt) | 构建与架构规则 | 2 / 0 | 原 JP4 检查点改动 |
| [libs/image/KisStrokeJobFailureContext.cpp](/Users/apple/krita_gpu/krita/libs/image/KisStrokeJobFailureContext.cpp) | 事务与失败传播 | 31 / 0 | 原 JP4 检查点改动 |
| [libs/image/KisStrokeJobFailureContext.h](/Users/apple/krita_gpu/krita/libs/image/KisStrokeJobFailureContext.h) | 事务与失败传播 | 32 / 0 | 原 JP4 检查点改动 |
| [libs/image/KisStrokesQueueMutatedJobInterface.h](/Users/apple/krita_gpu/krita/libs/image/KisStrokesQueueMutatedJobInterface.h) | 调度与 cut | 5 / 0 | 原 JP4 检查点改动 |
| [libs/image/brushengine/kis_paintop_utils.cpp](/Users/apple/krita_gpu/krita/libs/image/brushengine/kis_paintop_utils.cpp) | Painter/设备写接口 | 7 / 0 | 原 JP4 检查点改动 |
| [libs/image/brushengine/kis_paintop_utils.h](/Users/apple/krita_gpu/krita/libs/image/brushengine/kis_paintop_utils.h) | Painter/设备写接口 | 4 / 0 | 原 JP4 检查点改动 |
| [libs/image/kis_paint_device.cc](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc) | Painter/设备写接口 | 74 / 2 | 原 JP4 检查点改动 |
| [libs/image/kis_paint_device.h](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.h) | Painter/设备写接口 | 49 / 0 | 原 JP4 检查点改动 |
| [libs/image/kis_paint_device_strategies.h](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h) | Painter/设备写接口 | 96 / 13 | 原 JP4 检查点改动 |
| [libs/image/kis_painter.cc](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc) | Painter/设备写接口 | 153 / 106 | 原 JP4 检查点改动 |
| [libs/image/kis_painter.h](/Users/apple/krita_gpu/krita/libs/image/kis_painter.h) | Painter/设备写接口 | 30 / 2 | 原 JP4 检查点改动 |
| [libs/image/kis_painter_blt_multi_fixed.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_painter_blt_multi_fixed.cpp) | Painter/设备写接口 | 92 / 57 | 原 JP4 检查点改动 |
| [libs/image/kis_painter_p.h](/Users/apple/krita_gpu/krita/libs/image/kis_painter_p.h) | Painter/设备写接口 | 12 / 6 | 原 JP4 检查点改动 |
| [libs/image/kis_simple_stroke_strategy.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_simple_stroke_strategy.cpp) | 事务与失败传播 | 8 / 1 | 原 JP4 检查点改动 |
| [libs/image/kis_simple_stroke_strategy.h](/Users/apple/krita_gpu/krita/libs/image/kis_simple_stroke_strategy.h) | 事务与失败传播 | 7 / 0 | 原 JP4 检查点改动 |
| [libs/image/kis_stroke.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_stroke.cpp) | 调度与 cut | 89 / 2 | 原 JP4 检查点改动 |
| [libs/image/kis_stroke.h](/Users/apple/krita_gpu/krita/libs/image/kis_stroke.h) | 调度与 cut | 14 / 1 | 原 JP4 检查点改动 |
| [libs/image/kis_stroke_strategy.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_stroke_strategy.cpp) | 事务与失败传播 | 21 / 0 | 原 JP4 检查点改动 |
| [libs/image/kis_stroke_strategy.h](/Users/apple/krita_gpu/krita/libs/image/kis_stroke_strategy.h) | 事务与失败传播 | 25 / 0 | 原 JP4 检查点改动 |
| [libs/image/kis_strokes_queue.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_strokes_queue.cpp) | 调度与 cut | 60 / 1 | 原 JP4 检查点改动 |
| [libs/image/kis_strokes_queue.h](/Users/apple/krita_gpu/krita/libs/image/kis_strokes_queue.h) | 调度与 cut | 5 / 0 | 原 JP4 检查点改动 |
| [libs/image/kis_transaction.h](/Users/apple/krita_gpu/krita/libs/image/kis_transaction.h) | 事务与失败传播 | 67 / 8 | 原 JP4 检查点改动 |
| [libs/image/kis_transaction_data.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp) | 事务与失败传播 | 188 / 14 | 原 JP4 检查点改动 |
| [libs/image/kis_transaction_data.h](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.h) | 事务与失败传播 | 29 / 1 | 原 JP4 检查点改动 |
| [libs/image/kis_update_scheduler.cpp](/Users/apple/krita_gpu/krita/libs/image/kis_update_scheduler.cpp) | 调度与 cut | 27 / 1 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisCompletionRegistry.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCompletionRegistry.cpp) | 预算、退休与维护 | 163 / 55 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisCompletionRegistry.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCompletionRegistry.h) | 预算、退休与维护 | 16 / 2 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisCpuResidentBinding.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp) | 读保护/驻留/readiness | 184 / 23 | 是 |
| [libs/image/pagestore/KisCpuResidentBinding_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding_p.h) | 读保护/驻留/readiness | 87 / 16 | 是 |
| [libs/image/pagestore/KisImageEpochReferenceModel.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp) | 预算、退休与维护 | 164 / 6 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisImageEpochReferenceModel.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.h) | 预算、退休与维护 | 21 / 0 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisMutationStorage_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisMutationStorage_p.h) | Session/稳定存储/backend | 497 / 0 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageHistoryCollector.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp) | 预算、退休与维护 | 86 / 32 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageHistoryCollector_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector_p.h) | 预算、退休与维护 | 11 / 4 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageMetadataArena_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataArena_p.h) | 预算、退休与维护 | 40 / 1 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageMetadataCoordinator.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp) | Publication/metadata | 374 / 73 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageMetadataCoordinator.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.h) | Publication/metadata | 42 / 4 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageMetadataCoordinator_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator_p.h) | Publication/metadata | 26 / 0 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageOwnerLedger.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp) | 写计划/provider/ledger | 301 / 47 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageOwnerLedger.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.h) | 写计划/provider/ledger | 39 / 0 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPagePublicationCoordinator.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp) | Publication/metadata | 370 / 169 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPagePublicationCoordinator_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator_p.h) | Publication/metadata | 44 / 19 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageReadCoordinator.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadCoordinator.cpp) | 读保护/驻留/readiness | 444 / 87 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageReadCoordinator_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadCoordinator_p.h) | 读保护/驻留/readiness | 90 / 20 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageReadiness.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadiness.cpp) | 读保护/驻留/readiness | 106 / 0 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageReadiness_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadiness_p.h) | 读保护/驻留/readiness | 57 / 0 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageReplicaProvider.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReplicaProvider.cpp) | 写计划/provider/ledger | 5 / 0 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageReplicaProvider.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReplicaProvider.h) | 写计划/provider/ledger | 6 / 0 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageRetirementQueue.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp) | 预算、退休与维护 | 298 / 26 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageRetirementQueue_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue_p.h) | 预算、退休与维护 | 47 / 12 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageStateMachine.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine.cpp) | 写计划/provider/ledger | 31 / 2 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageStateMachine.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine.h) | 写计划/provider/ledger | 6 / 1 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageStore.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp) | Session/稳定存储/backend | 1065 / 333 | 是 |
| [libs/image/pagestore/KisPageStore.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.h) | Session/稳定存储/backend | 106 / 8 | 是 |
| [libs/image/pagestore/KisPageStoreDiagnostics.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreDiagnostics.cpp) | 诊断与因果指标 | 9 / 4 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageStoreDiagnostics_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreDiagnostics_p.h) | 诊断与因果指标 | 43 / 0 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageStoreReclamation.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreReclamation.cpp) | 预算、退休与维护 | 267 / 13 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageStoreReclamation_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreReclamation_p.h) | 预算、退休与维护 | 49 / 0 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageStoreTypes.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreTypes.h) | Session/稳定存储/backend | 12 / 1 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageWriteCoordinator.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp) | 写计划/provider/ledger | 965 / 253 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisPageWriteCoordinator_p.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator_p.h) | 写计划/provider/ledger | 138 / 20 | 原 JP4 检查点改动 |
| [libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp) | Session/稳定存储/backend | 664 / 150 | 是 |
| [libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h) | Session/稳定存储/backend | 60 / 8 | 是 |
| [libs/image/pagestore/KisTiles3PageReplicaProvider.cpp](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp) | 写计划/provider/ledger | 195 / 15 | 是 |
| [libs/image/pagestore/KisTiles3PageReplicaProvider.h](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.h) | 写计划/provider/ledger | 8 / 0 | 是 |
| [libs/image/tests/KisCompletionRegistryTest.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/KisCompletionRegistryTest.cpp) | 测试与测试注册 | 361 / 0 | 原 JP4 检查点改动 |
| [libs/image/tests/KisPageStoreCpuMutationTest.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp) | 测试与测试注册 | 2675 / 62 | 原 JP4 检查点改动 |
| [libs/image/tests/KisPageStorePhysicalClaimTest.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStorePhysicalClaimTest.cpp) | 测试与测试注册 | 863 / 18 | 原 JP4 检查点改动 |
| [libs/image/tests/KisPageStoreReferenceTest.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreReferenceTest.cpp) | 测试与测试注册 | 1486 / 13 | 原 JP4 检查点改动 |
| [libs/image/tests/KisPageStoreResidentReadTest.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreResidentReadTest.cpp) | 测试与测试注册 | 459 / 14 | 原 JP4 检查点改动 |
| [libs/image/tests/kis_painter_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp) | 测试与测试注册 | 1032 / 1 | 原 JP4 检查点改动 |
| [libs/image/tests/kis_painter_test.h](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.h) | 测试与测试注册 | 35 / 0 | 原 JP4 检查点改动 |
| [libs/image/tests/kis_simple_stroke_strategy_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/kis_simple_stroke_strategy_test.cpp) | 测试与测试注册 | 152 / 0 | 原 JP4 检查点改动 |
| [libs/image/tests/kis_simple_stroke_strategy_test.h](/Users/apple/krita_gpu/krita/libs/image/tests/kis_simple_stroke_strategy_test.h) | 测试与测试注册 | 5 / 0 | 原 JP4 检查点改动 |
| [libs/image/tests/kis_stroke_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/kis_stroke_test.cpp) | 测试与测试注册 | 154 / 0 | 原 JP4 检查点改动 |
| [libs/image/tests/kis_stroke_test.h](/Users/apple/krita_gpu/krita/libs/image/tests/kis_stroke_test.h) | 测试与测试注册 | 8 / 0 | 原 JP4 检查点改动 |
| [libs/image/tests/kis_strokes_queue_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/kis_strokes_queue_test.cpp) | 测试与测试注册 | 298 / 7 | 原 JP4 检查点改动 |
| [libs/image/tests/kis_strokes_queue_test.h](/Users/apple/krita_gpu/krita/libs/image/tests/kis_strokes_queue_test.h) | 测试与测试注册 | 9 / 0 | 原 JP4 检查点改动 |
| [libs/image/tests/kis_transaction_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/kis_transaction_test.cpp) | 测试与测试注册 | 568 / 7 | 原 JP4 检查点改动 |
| [libs/image/tests/kis_transaction_test.h](/Users/apple/krita_gpu/krita/libs/image/tests/kis_transaction_test.h) | 测试与测试注册 | 21 / 2 | 原 JP4 检查点改动 |
| [libs/image/tests/pagestore/KisCpuPageReplicaProvider.cpp](/Users/apple/krita_gpu/krita/libs/image/tests/pagestore/KisCpuPageReplicaProvider.cpp) | 测试与测试注册 | 6 / 7 | 原 JP4 检查点改动 |
| [libs/image/tests/scheduler_utils.h](/Users/apple/krita_gpu/krita/libs/image/tests/scheduler_utils.h) | 测试与测试注册 | 16 / 4 | 原 JP4 检查点改动 |
| [libs/image/tiles3/KisTilePageStoreBridge.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTilePageStoreBridge.h) | Tiles3 adapter/extent/hash | 11 / 2 | 原 JP4 检查点改动 |
| [libs/image/tiles3/KisTiledExtentManager.cpp](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTiledExtentManager.cpp) | Tiles3 adapter/extent/hash | 147 / 33 | 原 JP4 检查点改动 |
| [libs/image/tiles3/KisTiledExtentManager.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTiledExtentManager.h) | Tiles3 adapter/extent/hash | 24 / 2 | 原 JP4 检查点改动 |
| [libs/image/tiles3/kis_base_iterator.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_base_iterator.h) | Tiles3 adapter/extent/hash | 15 / 3 | 是 |
| [libs/image/tiles3/kis_memento.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_memento.h) | Tiles3 adapter/extent/hash | 6 / 2 | 原 JP4 检查点改动 |
| [libs/image/tiles3/kis_tile.cc](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc) | Tiles3 adapter/extent/hash | 74 / 18 | 原 JP4 检查点改动 |
| [libs/image/tiles3/kis_tile.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.h) | Tiles3 adapter/extent/hash | 11 / 7 | 是 |
| [libs/image/tiles3/kis_tile_data_store.cc](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_store.cc) | Tiles3 adapter/extent/hash | 90 / 35 | 原 JP4 检查点改动 |
| [libs/image/tiles3/kis_tile_data_store.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_store.h) | Tiles3 adapter/extent/hash | 11 / 0 | 原 JP4 检查点改动 |
| [libs/image/tiles3/kis_tile_data_wrapper.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_wrapper.h) | Tiles3 adapter/extent/hash | 8 / 2 | 是 |
| [libs/image/tiles3/kis_tile_hash_table.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_hash_table.h) | Tiles3 adapter/extent/hash | 28 / 0 | 原 JP4 检查点改动 |
| [libs/image/tiles3/kis_tile_hash_table2.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_hash_table2.h) | Tiles3 adapter/extent/hash | 228 / 124 | 原 JP4 检查点改动 |
| [libs/image/tiles3/kis_tile_hash_table_p.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_hash_table_p.h) | Tiles3 adapter/extent/hash | 40 / 0 | 原 JP4 检查点改动 |
| [libs/image/tiles3/kis_tiled_data_manager.cc](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc) | Tiles3 adapter/extent/hash | 506 / 72 | 是 |
| [libs/image/tiles3/kis_tiled_data_manager.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.h) | Tiles3 adapter/extent/hash | 26 / 1 | 是 |
| [libs/image/tiles3/kis_tiled_data_manager_p.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager_p.h) | Tiles3 adapter/extent/hash | 6 / 1 | 原 JP4 检查点改动 |
| [libs/image/tiles3/tests/kis_lockless_stack_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_lockless_stack_test.cpp) | 测试与测试注册 | 784 / 1 | 原 JP4 检查点改动 |
| [libs/image/tiles3/tests/kis_lockless_stack_test.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_lockless_stack_test.h) | 测试与测试注册 | 24 / 1 | 原 JP4 检查点改动 |
| [libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp) | 测试与测试注册 | 1983 / 44 | 是 |
| [libs/image/tiles3/tests/kis_tiled_data_manager_test.h](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.h) | 测试与测试注册 | 64 / 0 | 是 |
| [libs/pigment/CMakeLists.txt](/Users/apple/krita_gpu/krita/libs/pigment/CMakeLists.txt) | 构建与架构规则 | 8 / 0 | 原 JP4 检查点改动 |
| [libs/pigment/compositeops/KoOptimizedCompositeOpAlphaDarken128.h](/Users/apple/krita_gpu/krita/libs/pigment/compositeops/KoOptimizedCompositeOpAlphaDarken128.h) | 像素 kernel 修正 | 35 / 48 | 原 JP4 检查点改动 |
| [libs/pigment/compositeops/KoOptimizedCompositeOpOver128.h](/Users/apple/krita_gpu/krita/libs/pigment/compositeops/KoOptimizedCompositeOpOver128.h) | 像素 kernel 修正 | 3 / 1 | 原 JP4 检查点改动 |
| [libs/pigment/compositeops/KoOptimizedCompositeOpOver32.h](/Users/apple/krita_gpu/krita/libs/pigment/compositeops/KoOptimizedCompositeOpOver32.h) | 像素 kernel 修正 | 7 / 5 | 原 JP4 检查点改动 |
| [libs/ui/tests/CMakeLists.txt](/Users/apple/krita_gpu/krita/libs/ui/tests/CMakeLists.txt) | 测试与测试注册 | 1 / 0 | 原 JP4 检查点改动 |
| [libs/ui/tests/KisPainterStrokeCompletionTest.cpp](/Users/apple/krita_gpu/krita/libs/ui/tests/KisPainterStrokeCompletionTest.cpp) | 测试与测试注册 | 368 / 0 | 原 JP4 检查点改动 |
| [libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp) | 事务与失败传播 | 47 / 28 | 原 JP4 检查点改动 |
| [plugins/paintops/defaultpaintops/brush/kis_brushop.cpp](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp) | 实际 brush producer | 44 / 17 | 原 JP4 检查点改动 |
| [plugins/paintops/defaultpaintops/brush/kis_brushop.h](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.h) | 实际 brush producer | 4 / 0 | 原 JP4 检查点改动 |
| [plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.cpp](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.cpp) | 测试与测试注册 | 306 / 0 | 原 JP4 检查点改动 |
| [plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.h](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.h) | 测试与测试注册 | 6 / 0 | 原 JP4 检查点改动 |
