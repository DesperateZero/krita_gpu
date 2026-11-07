# T08.2：6f769的Setup/H0反面结果归因（诊断前冻结）

当前产品6f76902d4a、父cb942b6eff不变。本实验不增加上一批68过程样本，不重新计算其资格，不以新的阶段替换原总端点。原Setup/整进程回退信号、H0/Undo/尾控制未通过保持。原33项T08.2内完成责任判别，不新建迁移矩阵。

已有4观察过程的Setup所有collector/read-release计数均0。当前假设竞争：A. 新metadata通知直接在Setup付费；B. 成本发生在共有资源/brush初始化；C. 二进制布局、启动环境或调度影响，当前无法归因；D. H0通知前移改变工作合并/唤醒，净新增工作抵消收益。不得从零GC计数推断整阶段零PageStore工作，也不把共有Setup优化授予PageStore性能资格。

新增两个metadata入口的固定计数（applyReadProtection/applyCapturedProtection），沿原gc计数区分所有实际执行阶段。两側复用前批已绑定的observer objects，metadata仅加相同计数；父9-TU声明闭包保持，当前原源码未改。计数不用于单价。诊断business fixture保留原所有语义，仅用5个粗时刻将Setup拆成image创建、resource manager创建、preset/configure/wait、blank projection四段，输出在Setup之外。storage复用原完整case，限定每过程只运行case3或7，分别记setup/write/read/finish/undo/redo/teardown和stage0；原4寿命、输入和像素检查不变。stage是执行时段，不冒称工作发起者或完整物理drain。

固定12个ARM64观察过程：business parent/current/current/parent共4；storage case3和7各同一4过程。没有额外能力/性能样本；每个过程均验证像素/业务数量/退出/真实库与共享依赖，120秒超时并kill/reap，失败立即停止并保留。不与构建或其他基准并行。源码/头/链接对象/二进制/协议预先hash，运行后复核。

有限裁决：若Setup两个新增入口及原改动入口均0，否决“新增通知逻辑直接消耗Setup”的解释，但二进制间接效应/原统计信号仍未消除；将主要阶段的实测总量用于选择下一诊断，而非归因时间差。H0若节点/扫描/重复/唤醒增加，可支持D；若减少或不增加，则不能继续用其作已证回退来源。2次计数重复只给范围，不给概率区间；4粗时序只描述，不刷新原95%结果。若发现更高层重复必要性问题，回到原33项/共同管线的原owner推导，不凭短诊断直接扩成生产优化。
