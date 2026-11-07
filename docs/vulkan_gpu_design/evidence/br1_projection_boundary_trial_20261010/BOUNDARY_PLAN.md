# 清零/首层合成边界：算法、代码索引与唯一追踪矩阵

当前生产实现为 **8198c36ed7**，本表已按[生产证据](../br1_projection_boundary_production_20261010/README.md)结算；早先c13派生原型的冻结版仍保存在本目录raw归档及60b1bb8fc文档提交中。B01–B11沿用，不另立第二套责任表。生产语义/资源验证与局部净收益已交付，严格阶段时间非劣及正式M6仍分别开放。

## 原路径与生产理想路径

```text
原：同 merge owner → clear完整生命周期 → visitor/recalculate → first composite完整生命周期 → 后续层/原write/reset/完成
生产：原 merge owner判断真实中间消费者
  → 复杂/派生类型、额外源投影、temp、不可见、空源：原路径
  → 独立具体首层：本leaf局部clearRect → 原源更新 → plane原参数
     → 不支持 / clear-only域超出实际paintRect：原clear + bitBlt
     → 旧清除域为空：原bitBlt
     → 支持：一次准备实际paintRect → cursor初始化旧清除域 → 原over → 一次原交付
        准备拒绝且未进入callback：原两操作一次
        callback已进入后失败：原撤销 → clear效果 → 原失败报告，不重放合成
  → 后续层、write/reset、通知、原scheduler终结
```

融合守卫：具体`KisPaintLayer` / `KisLayerProjectionPlane`、无下层依赖/mask/style/needProjection，源与updateRect相交；painter无selection/stroke owner/wrap，over、等format、零default、独立data manager。`initializeRect = clearRect ∩ target extent`必须包含于实际裁剪paintRect。只删不被业务要求的中间clear cut；不把所有operation、版本或调度边界默认当必要，也不把观察不到cut当不需要。

旧extent不是存在页集合，故不再用原型union扩大准备范围。新增准备页集合为0，实际内存峰值仍受原预算准入；全页clear先释放的优势由未进入callback时回原路径保留。没有实验pending TLS、跨leaf设备保活、第二队列/owner；原failure context错误桥接保留，其内部既有TLS不是原型状态。

## 代码位置与唯一状态

| ID / 当前代码 | 原责任、清理结果与保留保证 | 验证与状态 |
|---|---|---|
| B01 [startMerge](../../../../krita/libs/image/kis_async_merger.cpp:172) | 每次leaf只有局部clearRect，不跨层排队；原job、取消、原visitor、scheduler完成保持 | 已实施；原merger/projection及自定义中间reader通过 |
| B02 [setupProjection](../../../../krita/libs/image/kis_async_merger.cpp:278) | 只具体独立首层可延迟；空源在setup阶段先clear，非空支持路径删除独立生命周期 | 已实施；13次融合、fill13→0、冷准备132→96、batch/seal32→19 |
| B03 [plane::applyWithClear](../../../../krita/libs/image/kis_layer_projection_plane.cpp:90)、[compositeWithProjection](../../../../krita/libs/image/kis_async_merger.cpp:334) | 原参数和源裁剪；无设备/空needRect仍完成clear；普通apply未改语义 | 已实施；调用闭包merger→plane→painter，无旁路消费者 |
| B04 [bitBltAfterClear](../../../../krita/libs/image/kis_painter.cc:686)、[bitBltImpl](../../../../krita/libs/image/kis_painter.cc:760) | 原kernel、source reader、cursor；受约束初始化与paint共享原prepare/finish | 已实施；30等价数据行、快照/历史，以及完整painter双架构通过 |
| B05 [write/reset](../../../../krita/libs/image/kis_async_merger.cpp:273) | 不增加pending收尾字段；scope没有延期任务，temp/write/reset原责任保留 | 已实施；Undo/Redo原操作数量不变；r0空源延迟已在r1恢复原顺序，严格时间非劣未授 |
| B06 [复杂visitor](../../../../krita/libs/image/kis_async_merger.cpp:59)、[中间reader反例](../../../../krita/libs/image/tests/kis_async_merger_test.cpp:40) | 派生类型、额外源投影、mask/style/真实依赖保持clear cut；普通native当前/固定旧view保留 | 本生产范围关闭；初始化前及写完未publish当前view仍旧，完成后新view、固定旧view稳定；不外推所有类型 |
| B07 [native-only私有入口](../../../../krita/libs/image/kis_paint_device.cc:1905)、[失败反例](../../../../krita/libs/image/tests/kis_painter_test.cpp:1431) | 现有stack错误桥接先隔离attempt；未进callback才允许fallback，已进callback失败不重放；原clear先于向调用者报告 | 本范围关闭；prepare/kernel-write/prepublish finish/already-failed实测；原adapter预备、abort、barrier、delivery、life/conflict全部复验，不制造发布后恢复合同 |
| B08 [资源反例](../../../../krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:2502)、[支持域与fallback](../../../../krita/libs/image/kis_painter.cc:686) | clear域限于paint集合；sparse/default/小空源等保留原路径；原额度、收费、claim与释放不变 | 本范围关闭；真实硬满两臂相同拒绝/效果、reserved及活跃写归零、释放后重试；不宣称物理峰值零增加 |
| B09 原job取消/重入/target/source lifetime | 无新持久状态、owner或延期引用；stack intent只在当前leaf同步消费；stroke owner不融合 | 本范围关闭；history revert与完整painter原并发/取消控制、manager取消/abort及fixture销毁通过 |
| B10 Store/backend观察 | 生产未加入计数或改下层policy；观察版只记录成功冷准备/batch/seal等，commit不固定 | 已结算；新两父/两候选计数完整兑现，不领计数时间收益 |
| B11 fixture / 双架构测试 / 独立性能 | r0控制失败保留；r1先1760测试/4能力过程，再另16块64进程；实际库与源码分别冻结 | 局部主价值通过：CPU1.204ms [0.922,1.781]；控制点仍稍慢且CI跨0，严格非劣、M6与全局排名不授 |

## 成本预算与结算

模型为`C(clear)+C(paint)−C(同一paint准备+必要初始化)`，额外计入guard/source extent、错误桥接及失败fallback，而非把所有clear内部CPU相加为收益。新增准备页集合0；删除36次成功冷准备和13套batch/seal，原19次合成与必要kernel保留。566464B为初始化字节，不是新分配容量。

事前0.5–1.5ms宽工程预测，r1主点1.20375ms；旧原型1.05775ms与本生产结果不属同批估计，不能断言新增安全检查反而“提升0.146ms”。r0 Undo CPU明确回退27μs；r1恢复空源原时序后点回退18.25μs，区间跨零，不能宣称严格非劣或证明全部原因。两个固定批次均停止，不追加样本、不事后改门。

本矩阵关闭的是这套有限生产实现、安全/资源反例和可证净收益；全局算法/调度充分性、其它模式、完整upstream差额、正式M6及阶段非劣仍按92维护。安装skill取得从边界选择到生产收益的正向实例，不宣称精确预测或全局榜首已验证。
