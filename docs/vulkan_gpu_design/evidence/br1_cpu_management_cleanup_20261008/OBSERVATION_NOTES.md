# 观察器修正与失败留存

- build-01：产品TU已编译；两个Reference旧测试仍调用已删rebind接口。迁移到原完整reservation协议及单键归属反例后build-02通过。
- dev-01：新增首次越界测试错误假定callback前没有预备。实际公开operation先预备合法72页；修正为越界不新增代际且失败锁存，dev-02为55/0/0。产品保持原首字节前预备合同。
- 首次diagnostic父TU从未改的中间header读到当前私有声明，编译失败。diagnostic-v2冻结整个pagestore本地header依赖闭包，父源仍来自6644249，候选来自本次源；旧派生源、命令和失败原样保留。
- 首个runs-diagnostic父过程像素/退出/加载/栈均正确，但观察器错误要求Stroke结束metadata reserved=0，测到16B临时预留而拒。Stroke结束早于后台drain，原合同允许；最终Teardown reserved=0才是本包此观察的终点。保留run_comparison-01.py及失败全样本；修正后另开countfix能力2过程及固定ABBA×2的8过程，不用于性能授时。
- 所有quantity计数属于外部派生库；产品无计数器。计数按phase和proj_merge祖先拆分。amount为整型工作量，hits仅非零次数；cursor contains的amount是声明范围长度总和（952），不是提前命中前的实际比较次数，不领952次元素比较删量。
- clones是borrow接纳后input/局部constData地址差观察，成功非空且源存活，地址差证明一次COW；完整候选的独立operation直接绑定而不再调用borrow。因此19次克隆删除是MP01–04联合结果，不能分别重复领价。38个请求由真实SnapshotArray的shared Storage/control与vector两分配推导，非全进程malloc实测；元素96，共768B。
- 声明协议、统计样本量和未插桩性能规则未改变。计数上的重复复制/查询/锁删量不替代净时间证据。phase5仍有进程全局bootstrap/cache等收费，process bytes不要求0，不能将该全局快照解释为单store泄漏或完整metadata门分母。
- 首次差集删除核验把Private::less子串误匹配到无关CapturedReadView::Private::lessKey而拒；保留audit_cleanup-01.py，修正为Execution/BoundEntry精确符号后重做删除账，不删真实capture排序。首轮analyze仍带旧10过程diagnostic尾而在输出有效父结果后拒，保留analyze-01.py，新的数量分析独立于未插桩统计。首次控制分析调用缺少必需CLI参数，随后按原固定--round/--output复算同一640过程，没有换样。
