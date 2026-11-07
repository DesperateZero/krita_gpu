# PageStore 额外指令责任与下一完整优化边界

**最新交接补缺：** [原组件可接性探针](DONOR_LIFECYCLE_DESIGN.md)已证实旧proof撤销后backing仍为ActivePending、现有handoff可prepare；普通H1下一写旧目标全退出，因此需要提交退休前的有界保留。clone/native拒绝说明实际物理保护仍必要。它更新[§19.13](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#donor-lifecycle-capability)的构造算法和压力删量，不改变下列原库指令差、不定价净收益或授予榜首。

**2026-10-12后续完整性复审：** 本文冻结测量及条件设计保持；“首位/下一只领取复用”不代表净收益排序已成立。当前按[预算完整性报告](BUDGET_COMPLETENESS.md)及[唯一蓝图§19.12](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#budget-completeness-review)比较完整替代，先闭合原owner交接与联合净预算。该复审补全阶段指令、全部scope余项及两层窗口，没有新增性能样本。

2026-10-12，产品仍 `11c6895ddfeae074df727c76dcbf9e12988479ee`，upstream `9a24ae0d8c070884fb013594191002e1a1b39a19`。**本次完成归因及下一方案约束，生产/产品测试零改动，没有已兑现的指令或 CPU 收益。** 实施索引和状态只维护在 [PIPELINE_PLAN §13/§19.11](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#instruction-lifecycle-design)，不另建实施矩阵。

冻结批次结论（当前选型以[集中裁决](BUDGET_COMPLETENESS.md)为准）：正常执行条件的巨大指令差不能当作必要管理费。直接证据支持优先处理每页完整身份的建立/退出：它横跨前台准备和后台回收，不能只改一个 release、completion 或 malloc。现有测量不足以宣称每一项都能删除，亦不支持立即提交一个未经闭环验证的复用 cache。

## 1. 同批原库差额

Tier 1 为六 variant（两侧原库、派生 scope off/on）各一 capability，再四个旋转镜像块，共54过程；Tier 2为四个固定正反顺序的 current 细分过程。每过程沿原八case、四manager寿命、逐写readback、undo/redo与drain。全部58过程通过原自身语义、退出、加载身份和计数检查。准备期另有两个 r1 capability，其中 upstream 被错误的端点差门拒绝；以及一次协议文件哈希更新前的启动拒绝，均保留，未拼接到正式块。

线程边界通过 `thread_selfcounts`，角色通过 `PROC_PIDTHREADCOUNTS`，进程通过 `RUSAGE_INFO_V6`。这是诊断接口，未进入产品。两侧实际编译都是 `-O2 -g -DNDEBUG`、原生 arm64。同一fixture增加双方对称的外部 phase 指令读取；“原库”指内部产品未插桩，不把新fixture称为完全无观察器。

H1，K16/W16，四寿命，四块块内均值：

| 同批原库端点 | current | upstream | 增量 |
|---|---:|---:|---:|
| 进程指令，百万条 | 183.129688 | 29.882726 | **153.246962** |
| 前台指令，百万条 | 132.158188 | 29.833749 | **102.324439** |
| 进程减前台，百万条 | 50.971500 | 0.048977 | **50.922523** |
| 进程 CPU，ms | 14.700750 | 1.851375 | **12.849375** |

额外指令 pointwise 95% block bootstrap 为 **[151.456203,155.037721] 百万条**；CPU 为 [11.35925,14.971125] ms。固定100000次、seed20261012；只有四独立块，内部四寿命不是独立样本。此批约66.77%的额外指令在前台；“进程减前台”本身不是 reclaimer，但派生off的注册角色核对见前台131.5765M、reclaimer51.7690M，monitor/pooler/swapper分别0.0085/0.0164/0.0173M，支持主要后台责任为回收线程。

H1作为最后case时原库指令均值178.037877/26.581674M；作为首case时188.221499/33.183778M。初始化和外部边界均不同于上一自然批，不能把183.13/29.88的新比值与原6.84倍相除，宣称产品已改善。全部慢样保留；本批current原库平均P核CPU份额93.49%，没有筛选“只剩P核”的样本。

端点嵌套亦有价：当前线程边界包住两次process-rusage，upstream无后台时约多16574条；角色快照窗口比进程窗口更宽，Tier 1角色和比进程多23585～62395条。差额原样保留，不把小负残差解释为负成本。

## 2. 大责任先于小函数

下表是 Tier 1 **scope on 中互斥的 exclusive 指令**，不是原库净可删量。所有角色上的同名责任合并；job父桶已经扣除子scope。部分长符号按原job职责显示，原符号保存在JSON。

| H1责任 | 百万条，约数 | 解释 |
|---|---:|---|
| `prepareTarget` 新目标准备 | **53.95** | 1088次；准备/准入/provider/owner/metadata建立都在其中 |
| history pass，前台＋后台 | **25.19** | 可达性、metadata删除、退债准备等；并非25M全是扫描 |
| retirement task的exclusive主体 | **20.60** | provider退休、owner结算、记录实际析构等；普通history job中的子process另记 |
| seal | 18.58 | 68次；私有接受/投影/旧值交接仍存在 |
| read（fixture与backend同名嵌套按exclusive合并） | 16.41 | 含真实读、写前比较所走读取等，不能全部删读保护 |
| operation / pixels / write包装 | 5.71 / 5.55 / 4.53 | 各自exclusive，不重复加包含它们的write inclusive |
| capture / captured release / canonical commit | 5.19 / 2.94 / 3.71 | 保持为竞争责任，不把剩余全部归到身份周转 |

前三项合计约99.7M observed指令。**“身份建立与退出”是目前最大的成组责任，而不是已证明可省99.7M。** H0的canonical commit另有31.20M（68次），高于其provider子项；H1只有8次commit。不能把H1优化外推成所有入口/历史模式的榜首。

Tier 2只分解该生命周期，未加新样本追精度：

| H1子责任 | observed exclusive M | 真实调用 |
|---|---:|---:|
| provider Fresh准备 | 20.906 | 1088 |
| reserveBacking | 11.744 | 1088 |
| owner registerBacking | 5.653 | 1088 |
| metadata private write | 8.781 | 1088 |
| write base / plan | 5.498 / 1.735 | 各1088 |
| discardHistory，前台＋后台 | 22.645 | 平均1276（函数调用，不是删除成功数） |
| provider retire，前台＋后台 | 12.827 | 1088 |
| owner release backing，前台＋后台 | 6.142 | 1088 |
| retireRecord余体，前台＋后台 | 10.484 | 1088 |

prepareTarget余体在Tier 2仍为22.436M，包含新子scope入口/退出开销，不能当成又找到一个22M纯产品热点。细分总指令升到约232.4M；scope调用一次本身有系统调用成本。provider Fresh与discardHistory在不同细分深度下只足以列入前列，不能凭20.9与22.6的差严格授予第一、第二名。

## 3. 观察资格与置信判断

Tier 1 H1，current原库→派生off的额外指令均值0.143M，95% [−0.637,0.923]M；scope off→on又增7.128M [6.512,7.545]M。原库→派生off CPU区间[−3.720,0.363]ms，off→on [0.1345,1.1196]ms，都不满足沿用的±0.75ms粗门。因此：

- **高置信定位**：额外约1.5亿条指令是真实大差额；前台和回收链共同承担；1088次完整身份周转是实测事实，不是payload系统分配的误认。
- **有界责任排序**：新目标准备，以及历史删除/物理退出合起来，值得排在本次H1重构首位。scope价格属于受观察器影响的实现；不能把比例变成原库CPU价。
- **尚未证明**：这批没有干预减少生命周期次数；不能仅凭相关性证明重用将省多少，更不能给“省896对象＝省82.35% CPU”的预测。

“高置信”是以上证据边界的工程判断，不虚构一个主观概率。额外指令的统计区间与这些机制判断分开。M6/M7/M8 0/3、校准2/20、默认关闭及旧控制失败不因诊断晋升。

## 4. 需要改的是逻辑generation与物理寿命的耦合

业务需要每次完整输入被接受后可读、失败保留上一成功值、undo起点独立保留、真实外部读者继续看到其版本。这要求逻辑generation和接受点，不要求每次都重新建立并销毁TileData、physical registration、provider binding、owner backing节点。

当前路径：`上一成功值保留 → Fresh物理对象及各层身份 → metadata/proof接受 → 替换overlay → 旧Prepared变Historical → 扫描/退债 → provider拆除 → owner/预算/对象退出`。

拟验证路径：`上一成功值保留 → 从原责任取得已不可见且无人使用的旧目标 → 预备新generation/预算/安装 → 复用物理对象及可保留的身份存储 → 写入私有目标 → 同一接受点 → 原旧目标进入可复用/最终回收判断`。首次、无合格旧目标、读者/alias/last-use、布局不合或预算拒绝继续走Fresh/原拒绝。当前可见页不原地覆写，不绕M7，不新增before副本。

这里仍有决定生产合法性的设计缺口，完整列在唯一蓝图§19.11。特别是不能把公开provider `retire` 返回Succeeded偷换成“物理没释放而且没收费”；不得向普通retirement queue移交后又从另一owner取回同一record。只复用字节缓存不命中本问题，删一张completion票据也不构成完整替代。

H1无外部持续读者的条件构造：四寿命、K页、W次写，非默认物理对象建立上界 `4K × (1 + min(W,2))`，原为 `4K(W+1)`；K16/W16即 **192 vs1088，少896（82.35%）**。其中1是undo origin，另两个是交替工作目标；960是旧Prepared接受后免扫描的候选数，不是物理建立删量。最后释放仍必须发生，且会覆盖更长的保留时长。该数量沿用并深化已有合法消费者分析，尚未实现或实测；逻辑generation、必要payload写入、拒绝路径与有读者的Fresh并不会按同比减少。

## 5. 下一包的价值门和停止条件

不再为这一诊断追加scope样本。下一包只领取完整的H1 Prepared旧目标复用原型，先完成原索引中的所有权、预算与旧handle拒绝设计，再实现。首次有限目标是原库H1整过程指令减少至少15%（本批约27M，工程门而非收益预测），同时沿原项目门要求完整process CPU节省的95%下界≥0.75ms、前台不能增加>0.75ms；H0/K1/W1及读者/压力控制保持。更高门有实际理由：涉及多层身份/生命周期变化，几个百分点不能抵偿此复杂度。

先冻结实际实现的删量和新增retag/准入/持有成本。独立确认使用8镜像块、固定样本、不加到通过；两个版本均内部无观察器，使用同一外部计数边界，counter-off CPU另设同矩阵对照。先过安全与有限资源反例，后测数量，再测独立净收益；不把本次探索样本用作确认。

若无法复用原owner/node而需新增第二pool或重复恢复协议，若metadata/protection/退债仍逐页全跑使删量仅落到payload cache，或若实测指令/CPU门未达到，则撤回原型并保留否决。H0公开root历史寿命另有价格，不强行套入Prepared免扫描证明。下一方案的净收益目前为未知，不能宣称已经接近upstream。

复算入口：[协议](INSTRUCTION_PROTOCOL.md)、[Tier 1机器账](instruction-summary.json)、[Tier 2机器账](instruction-detail-summary.json)、[原始证据清单](INSTRUCTION_RAW.md)。
