# 前台 descriptor 共享搜索：先判实际复杂度

产品c13c442493，生产同d182a34bd0；外层父ac8806805。使用原matched CPU fixture和当前原库ba5876d6，不重跑旧D1/D2细时钟、空history候选或upstream矩阵。本轮是候选判别，未授产品改造资格。

前台调查中，base/provider/binding/metadata/proof各有不同可变事实与寿命，不能把4.043ms全部删除。已有R08 descriptor搜索仍为开放结构候选：prepareDescriptorAdditionsLocked可能逐项扫描已有索引，但prepareDescriptorLocked已传入精确base layout hint。新问题是这个O(D)后备路径在实际Stroke是否存在显著放大，而非再次测整个metadata/proof桶。

竞争解释：D-A，hint覆盖正常冷代际，后备扫描量小，不能承担主目标；D-B，hint失配/缺席造成大量跨代际搜索，存在表示放大；D-C，主要成本为必要节点/容量而非共享搜索，减少比较可能增加分配和驻留。数量记录须同时保留命中、比较、真实新增值/节点和当时索引大小，不能将共享命中视作免费。

必要合同：每个版本取得完整相等的immutable descriptor；晚读者及已接受proof可继续引用原值；原owner/索引/预算/拒绝/锁外释放保持。共享相等值是表示选择，不能为跳过扫描新增第二持久owner或未计费缓存，也不能隐藏多分配造成的拒绝/驻留变化。

只对原publication TU派生计数，原产品不改。每次prepareDescriptorAdditionsLocked在栈上累加数量，退出时写固定预分配记录；无逐比较时钟、无热路径日志、无新增getter或业务锁。记录入口stage与嵌套single-descriptor来源，scope跨阶段不用于时间归因。Stage0另列，记录overflow必须为0。原hint及比较条件执行顺序不变。

固定四个能力过程：raw、count、count、raw；ARM64、原seed12345，正常19updates/8segments/4callbacks、像素hash、Undo/Redo、真实销毁、实际加载库/依赖、退出与reap逐一核验。每过程120秒超时kill/reap，失败保留后停止，不择样。本批计数只支持机制，CPU/wall仅作运行记录，不授增量收益或观察扰动置信度。

若Stroke后备比较为0，直接排除本端点的搜索优化。若非零，先计算欲节省0.5ms需每比较/扫描承担的价格（本次跨层表示改造的工程参考，非M6/通用门），必要时最多追加一次隔离扫描校准；必须标为条件价格，不由次数阈值直接晋升。真实共享/新增分配必须进入后续净模型。只有取得足够净预算才另冻合法替代与独立确认协议；无依据则结束本候选，不临时追逐另一个小改动。

同时记录技能欠缺：审查层间事实生产/接收/失效的方法是否足够具体；旧开放候选是否因后继优化已改变热路径；判别结果属于结构、净价还是性能资格。新经验先保留证据，不因本轮有否决结果宣称技能整体有效。
