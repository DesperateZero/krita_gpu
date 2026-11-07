# 投影首层生产化：事前协议

父产品c13c442493，文档60b1bb8fc；原库ba5876d6已复制到parent-lib，本包不覆盖旧试行样本。沿旧B01–B11结算，不新增第二责任表。目标是把受限原型实现为原merge/plane/painter内的同步初始化语义，无TLS、env生产开关、强引用延期队列或新预算owner。

生产范围先收窄到具体KisPaintLayer及具体KisLayerProjectionPlane、无mask/style/下层依赖、非temp首层；clear意图只跨本leaf的独立源更新，不跨其它leaf。painter只在零default、相同format、独立源/目标manager、无selection/stroke owner/wrap的over路径尝试融合；旧clear域为空不融合，旧clear域必须完全落在实际paintRect中，否则原clear+合成。这样新增准备页集合为0，清除域之外的旧像素仍按原路径处理，稀疏default的clear-only页不被错误实体化。

用原native operation做完整准备/执行/交付，禁用该次尝试的legacy fallback。原源读/over kernel保持。尝试的错误用原stack failure context隔离；未进入像素回调时退回原clear+bitBlt；进入后失败不重放合成，先执行原clear效果，再报告失败。既有失败context已failed时不开始；真实native拒绝/回调失败/交付失败必须验证效果和无回放。成功完成后不再存在pending clear。正常读者保持操作前固定视图或完成后的新视图；需要clear cut的复杂中间消费者保持旧路由。

必要验证：正常dense/partial/透明RGB/opacity/channel/offset；空源、旧extent超源、sparse/full-page default、selection/wrap/alias等fallback；current/exact读固定；准备拒绝与写后失败；原history undo/cancel与新调用无跨scope存储；原预算准入/物理释放保持。先做目标测试及原merger/projection、painter相关控制；失败保留、修复后新批次，安全未通过不测最终性能。检查所有新增接口实际caller及原型状态未进入生产。

条件数量预测：若真实首层paintRect包含旧clear域，保留原型13套batch/seal和36冷准备的删除；收窄guard可能减少命中，必须实测而非沿用旧计数。时间先以旧独立1.058ms为参考，生产预期约0.5–1.5ms Stroke CPU，属于宽工程范围，δ=0.5ms。若数量缩减在确认前登记修订预算；不凭数量授时间。

最终性能固定原ARM64 seed12345 matched fixture，parent/candidate ABBA/BAAB共16块64进程；块内各2进程均值差、块间中位，bootstrap50000 seed20261010，主Stroke CPU pointwise95% CI。工程价值需点≥0.5ms且下界>0；所有阶段/wall保留描述性pointwise区间，Undo/Redo/Teardown控制不因主项通过自动合格，正式M6和upstream差额另判。无计数性能进程不与build/分析竞争，timeout120秒kill/reap。保留所有慢值、实际库/hash、8segment/4显式callback、像素/undo/redo/销毁结果，更新通知只要求有输出并记录数量。数量验证用独立诊断，不增加生产计数器。固定批次结束不追显著性；本包交付当前产品与测试、实际删量、净收益、B01–B11处置和剩余正式资格。
