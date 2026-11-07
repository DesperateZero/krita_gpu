# 正常执行条件下的额外指令责任判别（2026-10-12）

本包承接 SLOW_PROCESS_ATTRIBUTION，不把 6.84 倍指令、8.34 ms 代数数量项直接当可删预算。用户授权继续减少指令差，允许有界诊断及有证据的完整优化；此前暂停产品优化的结论不能替代这次判别。

产品冻结 11c689，upstream 冻结 9a24ae0；原八 case、每格四寿命、逐写可见及 H1 undo/redo/drain 保持。原库和派生库分账，实际 dyld 身份检查。全部构建结束后串行运行，120 s 超时 kill/reap，保留所有失败和慢样，不追加到通过。

能力接口：Apple XNU `thread_selfcounts(THSC_TIME_CPI=3)` 测当前线程，`proc_pidinfo(PROC_PIDTHREADCOUNTS=34)` 测注册角色，`proc_pid_rusage(V6)` 测进程；仅用于隔离诊断，不成为产品依赖。官方源码 URL/哈希随证据保存。先前本地能力固定一百万次循环约 500 万指令；空边界稳定约 1508 条，逐 scope 不免费。不得把插桩结果直接当原库净收益。

Tier 1：使用原 net 根责任 scope，增加 fixture 七个 phase scope，以 inclusive/child subtraction 得 exclusive 账；registered role 总数和进程残差分开。六 variant：原库 current/upstream、派生 counter scope off current/upstream、派生 scope on current/upstream。每 variant 一 capability，再固定四个旋转镜像块（每块各 variant 两次），共 54 个过程；块内先求均值，再比较。正反 case 顺序交替。所有过程外部边界计数开启。H1/H0 检验原库→派生 off 的身份布局扰动，以及派生 off→on 的指令和 CPU 扰动；pointwise 95% block bootstrap，100000 次，seed 20261012。±0.75 ms 为沿用的粗观察门，不是优化验收。

scope 调用自身、桶查找和两次系统调用在父桶/残差留下成本；总 observed exclusive 必须闭合到 role。微基准空 scope 只给解释边界，禁止逐桶减常数后冒充原库精确价。排序看大责任及跨块稳定性，结合原库 phase/role 端点和源码，以能否改变完整责任选择为目标。

Tier 2 仅在 Tier 1 存在至少 2000 万条 observed 指令的大责任、而内部合法干预点不明确时领取：只细分该责任，固定两对正反顺序 current diagnostic 过程；保留 Tier 1 原样，不能合并估计。另记录指令观测成本，不作时间资格。若仍不能确定可删机制，停止本包归因，明确未知，不能用小项充榜首。

能力纠错：r1 在第二个 capability upstream 触发外部端点误差门。线程端点包住两次 process-rusage，upstream 无后台时固定多约 16574 条，原 10000 条边界不足；改为 30000 条并保留实差，不修正业务桶。r1 两过程保留在 `instruction-r1/runs`；正式四块尚未开始。r2 按相同 54 过程重新执行能力及冻结矩阵，无样本拼接。

候选须证明业务观察点、失败回滚、并发 reader/epoch、有限预算/父子收费、退出及重用失效。选定后在唯一 PIPELINE_PLAN 原矩阵责任内列有限代码索引、事前数量预测和独立确认规则，再改产品或隔离原型。禁止重复已否决的前台同步回收和完成票据删除；payload cache 已高命中，不能将 960 次对象周转视为 960 次 payload 系统分配。
