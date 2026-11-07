# r1：保留空清除分支，独立验证原型价值

写入于r1构建和任何r1过程之前。r0探索固定四块结束：Stroke CPU块收益1.413/1.6055/1.6955/1.1195ms，中位1.50925ms；Redo四块回退0.2095–0.230ms。r0不进入生产。机制显示Redo没有冷准备删量（56→56），却新增917504B初始化；这是明确新增工作，回退因果份额尚未单独测价。

r1在原merge准备处把待清除区域裁剪到当时parentOriginal的extent；交集为空则走原clear，不激活融合。非空时仅初始化该交集，原pixel operation范围使用该交集与实际paintRect的并集。保持原kernel/source读和复杂路径的clear先行。extent仍是保守边界，不能按bounding rect假定全部页存在；该查询及扩大并集的成本在新样本计入。

预测：Stroke仍删除原13个非空独立clear batch/seal和同merge36次冷准备（条件方向，必须用r1返回计数核验）；原6次空clear不融合。Redo没有融合及额外初始化，56个实际合成页保持；Undo原独立清除保持。若数量不兑现，先更新模型，不拿旧预测领收益。

对相同matched fixture的条件工程预测：r1 Stroke CPU节省约1.0–2.0ms，以r0量级及减少无效初始化推导；并非精确点预测或统计区间。最小值得收益δ保持0.5ms。wall不按CPU外推。Redo额外初始化预测0，不保证机器时间严格零；其它阶段需独立观察，Setup不领取收益。

先固定四个能力过程control-count/fusion-count/fusion-count/control-count，并以相同完整测试插件运行merger/projection各control/fusion一次。任何语义、实际加载或数量失败停止保留。

能力/现有测试通过后，独立16个平衡ABBA/BAAB块、64个未计数过程；主端点为逐块两次control/fusion的Stroke CPU均值差，再取16块中位。bootstrap50000、seed20261010、pointwise双侧95%区间；原型价值要求点估计≥0.5ms且下界>0。所有阶段及wall分别保留点与区间，未作family，不能把其它区间当正式非劣门。顺序、慢值、19通知变化及全部退出保留，不追加样本到通过。

这仅验证受限原型的机制与性能价值。生产应由原merge/painter明确传递初始化语义，移除实验TLS；中间current/exact读、拒绝时原clear效果、实际费用/峰值和取消的消费者闭包仍需目标反例。本批不会据性能通过自动授M6/正式安全资格或宣称技能所有层级已可靠。
