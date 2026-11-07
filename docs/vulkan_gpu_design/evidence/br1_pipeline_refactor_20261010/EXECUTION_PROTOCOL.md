# 补数 B：执行条件与实际工作关联（事前协议）

产品基线11c6895ddfeae074df727c76dcbf9e12988479ee、同依赖upstream 9a24ae0d8c070884fb013594191002e1a1b39a19不变。只生成隔离诊断库/fixture，不优化产品，不重领A的机制定价。当前问题是：相同输入的慢过程是否同时出现工作放大、不同执行条件、队列积压或特定gate获取延迟？本包不会证明完整管线最优。

## 有限范围与停止条件

- ARM64，复用原K1/16 × W1/16 × H0/1，RGBA8、四manager寿命、全部即时读/undo/redo、销毁、显式即时drain。业务操作和像素断言保持。
- 固定36过程：current0/upstream0/current5/upstream5四个capability，随后4块；四侧按块旋转并镜像，每块8过程，奇块反转case顺序。0关闭事件及计数；5同时记录计数和事件。没有采样率、核绑定、QoS或调度策略改变。每过程120秒，超时kill并reap；任何语义/身份/事件关联失败停止，保存失败，修观察器另开版本；不追加样本等慢态或过精度门。
- 输出全部样本，包括慢态；独立统计单位为块。4块只作执行证据能力判别。on−off完整foreground/process用原±0.75ms、pointwise95%、100000 bootstrap、seed20261011报告，不通过则事件时间仅是受观察器影响的描述，不授予原始产品单价。即使通过也不授予合法可删净预算。

## 隔离派生位置与因果含义

复用flow-census-r1当前的生命周期计数对象及net-ledger-r3 upstream对象。观察器替换，另派生Reclamation/HistoryCollector/RetirementQueue三个TU。scope只计调用，不再热scope读CPU时钟。两侧fixture的phase事件与原计时端点相邻，仍保留原计时；每事件记录CPU编号、pthread QoS、monotonic和当前线程CPU。CPU编号只是瞬时观测；同起止编号不证明全区间驻留，不以0–5/6–9先验直接声称实际核类或频率。

| 观测 | 精确锚点/关联 | 可证伪内容和限制 |
|---|---|---|
| 前台操作 | measure入口/出口，phase、四寿命内次序；本线程计数delta | 同一阶段慢态是否多做Fresh/登记/销毁/内部scope；包含原外层时钟费用，不能当原阶段函数单价 |
| 成功enqueue→dequeue | 原executor queue gate内，以job地址和按FIFO成功enqueue序号关联；dequeue前记录，完成后不解引用可能已释放job | 队列等待包含前序job、唤醒和调度；不是单纯runnable等待。可复用job必须按每次enqueue关联，不能仅凭地址 |
| job起止 | unlock后到invoke/dispose/finished结束，独立本线程计数delta | 工作是否转移/放大、job大小、与前台时间重叠；完成回调可能再次enqueue，原顺序保持 |
| history工作 | 实际slice版本数、root访问、pages访问、scan重启、rescan、blocked pass、实际retry arm/wakeup | 工作不等于job数；zero只覆盖此次无压力输入，不推断一般无重试 |
| retirement工作 | retireRecord入口、成功返回、实际retry arm/wakeup、background pass | 尝试与成功差为未成功尝试；不是所有失败原因细分 |
| 有界锁获取 | HistoryCollector中明确的ownerMutex获取，RetirementQueue中的自身queue mutex获取；locker之前/之后读数 | 只测acquire区间；不冒充锁持有时间，不覆盖owner/provider其他caller，不包含QWaitCondition内部重获取，不从wall−CPU推算阻塞。executor只记交接事件，未测其mutex竞争 |

计数全记；phase/job记本role计数delta。按role预分配有限事件/计数快照，热路径不写日志、不分配、不新加互斥锁；容量溢出、未闭合事件、CPU查询失败、FIFO不匹配都拒绝该包。输出在case原端点及drain后。观察器自己的共享原子和时间读取仍可能改变工作交错，明确保留扰动。

## 事前竞争解释与判断

1. **同工作执行条件差异**：逐phase相同计数签名，CPU/QoS起止观测不同，CPU耗时同步变化。只能获得关联；无全区间调度/频率信息不宣称外因已证实。
2. **实际工作放大/分配到不同线程**：比较同case全部role总量、前台/后台分量、history版本/root访问和退休尝试。相同Fresh总数不排除更多扫描或任务；相同总量不排除排队差异。
3. **队列/有限gate延迟**：匹配每个成功入队、出队和job，查看前序job覆盖与获取区间，保持独占CPU和elapsed不同分母。不把并行任务elapsed相加为端到端关键路径。

描述慢操作事前定义：同side/case/phase的mode5过程内phase线程CPU均值，高于全部8个观测过程对应中位数1.5倍。只用于列表，不删样或改变总账；没有命中则报告本次未捕获，不能说波动已解决。操作级同计数/CPU编号比较至少各20操作、分布于各3过程才报告聚合，仍不把操作当独立统计样本或给因果置信度。

预期交付：完整36过程、身份与原始事件、计数/FIFO/phase闭合复核、同批on−off能力、已支持/未支持解释。缺内核running/runnable/blocked轨迹、全部锁、资源峰值/驻留、其它入口/压力仍明确开放。B只完成其可观测子集，C/D/E继续开放；不以本次观察点值选优化。

构建准备纠错：r0在任何编译/运行前因`m_rescanRequested = false`有多个源码位置而拒绝；r1收窄到`if (m_rescanRequested)`分支的唯一锚点。r0生成文件保留，没有性能样本或丢弃样本，协议与36过程上限不变。

r1的三个产品派生TU已编译，观察器编译因CPU编号输出须为`size_t*`、QoS查询须三个参数而失败。r2按实际SDK声明修正，r1源码/编译失败日志保留；尚未运行任何fixture，不影响固定样本计划。
