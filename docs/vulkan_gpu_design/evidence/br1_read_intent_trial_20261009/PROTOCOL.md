# 显式 source 读意图：有界因果原型（事前协议）

产品起点 d182a34bd0196079bc40d2ab7d00b8e326e4a58a，文档父 2c1a93ad4；原库 SHA256 da4304d429134da577087e15004b4d98d93b7fc5c97a1bf6d8da4f4a615d66d1。这是03k的新责任判别，不续采已结束的D1/D2，不改产品或安装技能。

## 必要事实与构造算法

bitBltImpl<false>的source及mask只消费rawDataConst；bitBltImpl<true>的source消费oldRawData，先保留原行为。两种通用accessor目前均承诺current/before，并在构造时capture；cursor按页检查beforeMatches，若不同则另取before页。理想的**受限业务读者**只选择被消费的current，捕获时点、publication读锁、原current view与页guard寿命不变。既有通用accessor两种数据的公共合同不变，不能在全局禁用before。

本原型仅在bitBltImpl内source(false)及mask的构造调用上设置短暂线程局部实验意图；backend在同一同步构造栈、非writable、非existing、非live legacy条件下跳过before capture。不修改类布局；保留原current scope与cursor，before为空时已有alias规则使current仍为原current。该原型的oldRawData并非通用合同，所以这些受限局部对象不得逃逸且调用者不能消费oldRawData。产品实现若获准须采用显式类型/参数贯穿factory，删除实验TLS与环境开关，覆盖wrap/legacy/失败等完整索引。

竞争解释：R1未消费before造成重复capture/页解析/保护和最终释放；R2该workload无activeHistory，或current/before常相同，删量很小；R3主要成本仍在写生命周期，读者替代没有值得的净收益。cold的Page/descriptor/binding以及operation scope仍有真实owner、预算和解锁变化窗口；目前没有合法整桶删除算法，不能因各近1ms而优先重写。

## 数量预测与选择标准

设E为受限读者中原本有activeHistory的构造数，D为它们实际访问的current/before不同的cache miss数：capture减少E，未消费before页获取减少D，其原最后释放随相同对象寿命消失；真实current cut、写代际、像素及projection工作不减少。D和单价未知，不能预报净ms。先申请合法局部原型定价，不称已进入产品蓝图。复杂度跨factory/strategy/iterator/backend，业务参考δ=0.3ms Stroke CPU（约16ms的2%）；不是M6门或通用阈值。

## 有限实验

同一派生库 BR1_READ_SELECT=0/1，计数可单独 BR1_READ_COUNT=1；无逐页时钟。计数含分阶段构造意图、eligible/history/跳过capture、readPage current/before调用；后两项为整个程序聚合，不能直接把差额归为某个具体读者的D。先原库1过程及计数0/1各1能力过程；若任一语义/加载/退出失败则停止调查，若E=0则以未命中结束，不运行时间矩阵。

命中时，关闭计数，固定4个顺序块ABBA/BAAB/ABBA/BAAB共16过程；A原型关闭、B开启。复用ARM64同一fixture、4workers、RGBA8、8segments/4callbacks、19updates，全部像素/UndoRedo/销毁/实际加载hash/退出reap必须通过。保留所有慢值和失败，不续样。逐过程五阶段CPU/wall；按块内均值A−B报绝对节省、块均值和范围；4块仅用于探索定价，不给确认CI。若4块方向一致、节省中位≥δ、控制无明显反向代价，才支持另立产品蓝图及独立确认协议；否则有限结束为未决/不准入。含Setup总量单列，不能代替Stroke目标。绝不将本探索样本并入独立确认。

共享库、重编译源码/机械差异、链接对象与依赖hash、协议和runner身份冻结。原始失败与全过程保留。没有未经测量的置信百分比、upstream差额抵扣或M6晋升。
