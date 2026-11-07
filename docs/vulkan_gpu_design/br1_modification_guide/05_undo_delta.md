# 05：Undo delta、兼容索引与缓存

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。设计依据：92 §11；定位基线 `5173c807c87b`。覆盖 U01/U02，均待实施。性能优先级第二；与 S03 共用适配层失效机制时，不增加 stroke 每 dab 的工作。

## U01：让恢复 delta 穿透全部适配层

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [MementoManager](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreMementoManager.cpp:259)，`restore`；[commit](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreMementoManager.cpp:166) | 已保存 changedPages 并增量恢复；将 changed keys/存在性/default 标记随成功结果上送，不再导出全图求 diff |
| 主改 | [backend restore](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1773)，`rollback/rollforward/restoreHistory` | 传递受保护的目标 view 与 delta；失败不给上层成功结果；兼容 default 准备仍在可见安装前 |
| 主改 | [manager restore](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:465)，`restoreHistory` 中成功后的 `rebuildPageStoreIndex` 调用 | 成功后无条件 rebuild 改为 delta 安装/失效；普通恢复不得调用 allocatedPages/export/sort |
| 主改 | [manager 索引](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1000)，`rebuildPageStoreIndex/refreshPageStorePages/refreshPageStorePage` | 拆分存在性维护、缓存失效和实际 payload 读取；现有 refresh 会读取像素，不能简单替换 rebuild 后声称全链路完成 |
| 联动 | [全量枚举](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2478)，`allocatedPages`；[核心恢复](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:4266)，`restoreRetainedEpoch/Delta` | 全量 API 保留确有需求的消费者，普通 undo caller 迁出；default/format 等全量分支单独标记 |
| 联动 | [恢复发布](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1101)，`restoreRetainedEpochLocked` | 和 S05 共用短安装/复验；root 已变后不能因 adapter 分配失败留下一半状态 |

**索引变更规则：** 有→无删除坐标，无→有预备节点，两边都有只失效变化缓存，未变 key 不动。准备可能失败的索引/default/extent 存储后才安装。保持旧 tile capability 生命周期；不能对仍被使用的 wrapper 原地释放 payload。

**删除边界：** 移除普通 undo 对 rebuild 的调用，不无条件删除 `allocatedPages` 或 rebuild 函数本身；先查 clone/序列化/诊断/default 等真实 caller。

**验证落点：** [tiled_data_manager_test](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp)、[transaction_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_transaction_test.cpp)、[CpuMutationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp)。固定 K=1/16 放大 N/H，普通恢复 export/sort/hash clear 为零；验证 clone、空白、default、redo、边缘页、adapter 准备失败与 retained reader。

## U02：extent、像素边界和 history 清理分责

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [extent](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTiledExtentManager.cpp:270)，`Data::updateMin/updateMax`；[notifyTileAdded/Removed](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTiledExtentManager.cpp:344) | 先消费 U01 的增删 delta；稀疏坐标边界扫描按实测决定改有序计数/分块摘要，不能宣称现有删除严格 O(K) |
| 联动 | [PaintDeviceCache](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_cache.h:56)，`invalidate`；[PaintDevice 写入口](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1884) | 内容 revision/区域化失效需保持中途同步查询正确；不能把全部 cache invalidation 延至抬笔 |
| 联动 | [TransactionData](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp:423)，`redo/undo` 与更新路径 | offset/frame/default/interstroke 与像素恢复次序保留；只脏变更及真实滤镜依赖区域 |
| 联动 | [history purge](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreMementoManager.cpp:284)，`purge`；[releaseSnapshotDelta](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:4332) | 保护释放交给 S08/S09 的有界队列，不把 H 扫描或大析构压到下一笔首 dab |

**验证落点：** 同 U01，补 [paint_device_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_paint_device_test.cpp) 的 exact bounds/region、删除最外层 tile、巨大稀疏坐标、冷 undo、滤镜 halo 和 purge+stroke。区分 root 安装、用户可见、后台 drain 三个端点。
