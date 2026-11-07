# 06：笔刷准备缓存与内容上下文切换

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。设计依据：92 §12；定位基线 `5173c807c87b`。覆盖 C01/C02，均待实施。性能优先级第三；不以后台抢占或无界预热换切换成绩。

## C01：扩展现有 preset 准备缓存

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [PresetShadowUpdater](/Users/apple/krita_gpu/krita/libs/ui/KisPresetShadowUpdater.cpp:78)，`Private`、L107 `slotCanvasResourceChanged`、L135 `slotPresetChanged` | current-only cache、统一延迟重建改为按版本 key 的有界复用；区分 preset 切换与连续编辑设置 |
| 主改 | [后台准备/完成](/Users/apple/krita_gpu/krita/libs/ui/KisPresetShadowUpdater.cpp:146)，`slotStartPresetPreparation/slotCacheGenerationFinished`；L28 `ShadowUpdatePresetJob` | 热命中直接使用，冷 miss 尽快低优先准备，设置拖动继续合并；完成按 key+sequence 校验，不装入错误当前 preset |
| 联动 | [资源 snapshot](/Users/apple/krita_gpu/krita/libs/ui/tool/kis_resources_snapshot.cpp:66)，构造、L200 `setupPainter` | stroke 固定 snapshot；把合法 immutable cache 附着到它，不能让旧 stroke 被新 UI 设置修改 |
| 联动 | [preset snapshot](/Users/apple/krita_gpu/krita/libs/image/brushengine/kis_paintop_preset.cpp:510)，`cloneWithResourcesSnapshot`；L625 `regenerateResourceCache/sanityCheckResourceCacheIsValid` | key 含 settings cookie、实际依赖资源版本/canvas 值；保留 sanity check，不以指针/名称替代内容身份 |
| 联动 | [settings cache](/Users/apple/krita_gpu/krita/libs/image/brushengine/kis_paintop_settings.cpp:204)，`setResourceCacheInterface/regenerateResourceCache` | masking 子 preset 依赖及 prepared 资源的实际 bytes 一起计量；共享引用仍持有 charge |
| 核对 | [UI 切换](/Users/apple/krita_gpu/krita/libs/ui/kis_paintop_box.cc:659)，`setCurrentPaintop`；[painter 创建](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:2813)，`setPaintOpPreset` | 已按 engine 复用 option widgets；先测设置/信号成本。每笔可变 paintop 状态仍独立，不缓存 writer、随机源、spacing accumulator |

**依赖：** S10 提供共享可选额度和真实资源计量，C02 决定失效 key。纯配置 cache 不绑定 whole-image epoch；没有可靠大小/上界的对象不能记成零字节常驻。LRU 逐出只去索引，仍被 snapshot 引用的资源继续计账。

**验证落点：** [KisPaintOpPresetTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPaintOpPresetTest.cpp)、[freehand_stroke_test](/Users/apple/krita_gpu/krita/libs/ui/tests/freehand_stroke_test.cpp)、[FreehandStrokeBenchmark](/Users/apple/krita_gpu/krita/libs/ui/tests/FreehandStrokeBenchmark.cpp)。ShadowUpdater 还需在 [UI test 注册处](/Users/apple/krita_gpu/krita/libs/ui/tests/CMakeLists.txt)新增针对性测试目标或 fixture，名称待实现确定，不宣称已有对应完整测试。覆盖 A→B→A、冷 miss、设置拖动、旧完成、依赖变化、缓存超额、正在绘画时预热。

## C02：内容变化只失效真正依赖者

| 角色 | 现有代码段 | 当前行为 → 必须修改的关系 |
|---|---|---|
| 主改 | [ResourcesSnapshot](/Users/apple/krita_gpu/krita/libs/ui/tool/kis_resources_snapshot.cpp:66)，固定资源选择与 `setupPainter` | 区分配置依赖、目标/device/frame/LoD 和显示依赖；切换后新 job 不借旧目标 token |
| 主改 | [interstroke factory](/Users/apple/krita_gpu/krita/libs/image/KisInterstrokeDataTransactionWrapperFactory.cpp:110)，`createBeginTransactionCommand/createEndTransactionCommand` | 继续使用 continued-data、`isStillCompatible` 和 factory compatibility；内容相关状态按实际依赖复验，并保留 undo 命令语义 |
| 联动 | [TransactionData](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp:97)，`init` 的 frame/dataManager 与 interstroke 命令；L362 `redo/undo` | frame/offset/default/interstroke 与恢复顺序相容；配置缓存不得取代有业务语义的 interstroke 状态 |
| 联动 | [PaintDevice strategy 映射](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:280)，`applyPixelOperationImpl`；[scope 初始化/恢复](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:251) | 实际 manager/offset/wrap 发生变化就换或复验 scope incarnation；不能只凭 preset 一致复用 |
| 核对 | [stroke compatibility](/Users/apple/krita_gpu/krita/libs/ui/tool/KisStrokeCompatibilityInfo.cpp) | 这是既有 undo timed-merge 兼容信息；可参考字段，但不能把它直接当作准备缓存或物理权限 key |

**必须采用 92 §12.3 的完整矩阵：** preset/颜色参数、selection、layer/device、frame/LoD/offset/wrap、format/profile 转换、undo/外部内容改变、zoom/display。真实内容转换仍是显式写操作；轻量 preset 切换不触发全层搬迁、PageStore 重建或 history 清空。

**验证落点：** [transaction_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_transaction_test.cpp)、[paint_device_test](/Users/apple/krita_gpu/krita/libs/image/tests/kis_paint_device_test.cpp)、[freehand smudge/LoD 用例](/Users/apple/krita_gpu/krita/libs/ui/tests/freehand_stroke_test.cpp:139)。对矩阵每行分别验证保留与失效两侧；区分 UI 响应、准备、首 dab、可见结果，后台预热同时满足 stroke 防回退要求。
