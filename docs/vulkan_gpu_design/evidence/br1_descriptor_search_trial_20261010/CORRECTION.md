# 节点数量探针修订，保留首版

首版四过程及所有源/库/日志不改。审阅发现values[10]在每次nodes.emplace之后加一，测的是调用次数而未读取returned pair的inserted。首版分析器用“existing + new_nodes == inputs”验证的等式实际可以只验证尝试数，不能独立证明成功节点数。114 comparisons = 114 hits及208 hint等搜索数据不受此问题影响。

在correction独立目录生成修订观察库，只新增values[11]作为emplace尝试数，values[10]按emplace返回的second记录实际成功插入。继续分开exact-existing、共享选择、实际新建值和成功节点；不删除或覆盖旧数据。重新编译观察器自检后，只固定追加两个count过程，沿相同像素/19updates/8segments/4callbacks/退出/销毁/实际依赖检查；不增加raw时间样本，不授性能收益。

正式报告中首版[10]按emplace_attempts解释，成功节点仅引用修订过程。新增分析验证：existing+attempts=inputs；hint+global/local hits+new_values=attempts；successful_nodes≤attempts。若两者不同，逐调用披露，不能再假定相等。原两次计数一致不是系统性探针错误不存在的证明。

技能反测记录：必须从操作结果或真实对象身份验证关键数量语义，不能只用互相依赖、可自洽的计数等式。此修订只补观察准确性，不是候选算法或实验门槛改变。
