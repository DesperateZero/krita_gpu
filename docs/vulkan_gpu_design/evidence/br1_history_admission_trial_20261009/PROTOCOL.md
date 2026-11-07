# 空历史任务准入：新候选事前协议

起点仍为产品d182a34bd0，无产品改动。来源是storage release试行唯一栈普查：185个Stroke释放样本中26条经过history collectSlice，21条直接释放Work map节点。这是每32次释放一次的系统抽样，不是CPU比例或精确全量。重复malloc_size仅约0.03ms，已排除；本包考察完整空任务分配/调度/释放。

必要合同：只要页上有Historical版本，必须保留有界reachability/discard、失败重试、late保护和最终退休；只有事件产生/解除保护后才能判断可释放。当前requestKeyLocked即使metadata历史数为0也先分配含32版本槽的Work、入ready，再由worker发现空并删除。理想在**原owner gate、首次Work准入前**查询现存history事实；为空不创建任务。已有Work的scanning/repeat/ready保持；非空新Work沿原路径。历史后续创建必须由原publication或read-release再次请求，不用空Work作为未来事件订阅。

原型只改collector一个TU，使用现有historySlice(key,{},1).total判断，无新API/缓存/字段。lower_bound复用原map查找，再try_emplace(hint)；对原有Work不加metadata查询。额外成本为新Work候选的metadata锁/查询/小slice值构造；收益为被拒绝空Work的原节点分配、收费、排队、worker遍历和free。不能把collector全部CPU或采样份额当可删。

先构建同库A/B开关，计数A/B各1过程，复用原matched fixture所有像素/19updates/8segments/4callback/UndoRedo/销毁/退出/实际库核验。计数request、新候选、空候选、分配完成和工作slice，分阶段。A也查询一次以取得空候选分布，所以能力计数仅用于机制；时间模式关闭计数，A严格走原try_emplace，B才进入预检路径。若空候选为0或语义失败则停止，不跑时间。

命中后固定8个ABBA/BAAB交替块、32个关闭计数的探索fixture。主端点Stroke CPU；每块A/B均值差，保留全值，用8块bootstrap10000次seed20261009给探索95% pointwise区间，不能视为独立产品确认或M6资格。结构较小且无新owner，参考δ=0.1ms；只有CPU节省中位≥δ且探索CI下界>0、原控制没有明确回退时，才允许另存事前PREDICTION与产品索引并实施。否则为未决/不准入，不能追加样本到通过。

通过后产品候选与未修改父库独立确认另定协议、样本不混用；完整安全需覆盖零历史→后续产生历史、已有扫描repeat、保护晚释放、准备失败重试、close/drain和真实free。当前唯一额外getter不是退休许可；不得改变discard的原root/revision/protection复验。安装技能仍试行，只有03k原条件兑现才能升级。
