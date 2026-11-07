# PageStore 性能预算图与成本账本

**2026-10-17当前清理净账：** [handoff-lifecycle-r0](handoff-lifecycle-r0/RESULT.md)真实研究库已删handoff槽/目标索引、空retained及native无用发布准备。H0/H1写净少0.673018M/0.717466M、进程少0.843521M/0.786764M，两对照八块同向；仅回收同批R−U写差额1.434%/2.179%。H1暖896次槽/索引/对象、1008次空retained归零，实际预算结算1008保持，不能计成收费服务全部删除。新C−U写46.265672M/32.207665M；CPU未取得收益，控制失败保留，新管理比未知。该项原预算核销，不从旧内容账跨批减去新净差。当前方案及剩余服务按[V2 §10.26](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN_V2.md#handoff-lifecycle-removal)，原数图均保留各冻结账期。

**当前条件预算按[§19.32](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-final-path-selection)：** 无alias指定seal遍历10240→2048；K16全驻留metadata入口3072→1024，持久ref仍16B、临时首窗2376B。原binding/scope多余复制各1024个引用对、warm adapter临时引用2048对是条件删量，未定价。它们替代§19.31的4K/2048等中间预测，不能叠加；固定初始化、提前持有384D原行和binding、cold/失败/尾部均须扣费。[新证据](rw-final-path-selection-r0/README.md)只有源码/模型/实际类型编译，净指令/ms仍null、产品及最新52.445M/3.259ms实测不变。

**完整性复审：** [§19.29](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-pipeline-minimum-audit)补齐管线每段的工作维度，不能将主要生命周期覆盖或plan内82.8%解释为全部52.445M已闭合。8轮seal全写集循环、D流/source清理、有序bound重复寻址、同锁exact重复查询和代际重键是新源码审计对象；entry访问、lookup和mutex次数只是条件模型，均未领取指令/CPU价格。失效集合、history长度、adapter、读ref/guard、后台调度、峰值和最终释放仍须计入完整候选。最新实测及下方冻结图不变，[本轮证据](rw-pipeline-lower-bound-audit-r0/README.md)无新性能运行。

**下一完整设计及费用边界：** [原蓝图§19.28](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-relational-pipeline-design)把原range/result贯穿收费、activity、D接受和读/退出。§19.27同窗plan内6.805M收费＋2.917M native准入＋1.364M descriptor约占该13.395M责任的82.8%，支持联合处理，但含真实保护，不能领作11.086M净预算。条件活动1024→容量增长G、cold768→64、内部owns3968→0、读metadata入口3072→1024均有前提；共享allocator/最后free与各父桶不重复加价。双架派生布局新增成本亦记账，候选未实现、没有新性能样本，必要费与净收益保持null。本文冻结图不换分母，[源码/布局证据](rw-pipeline-design-r0/README.md)不充当性能证明。

**当前ed0f补账（2026-10-13，产品未改）：** [物理续费/activity与交付退出](rw-boundary-cost-r0/RESULT.md)，[机器账](rw-boundary-cost-r0/overview.json)。普通库读写额外52.445M/3.259ms；同窗plan的收费准备/retag6.805M、native准入2.917M、descriptor往返1.364M、实际claim0.232M。physical908次申请＝896个activity节点＋12次账本存储，descriptor堆申请0；加Fresh共1024个activity最终全部后台释放。manager外部责任3.229M中最后delivery1.967M，对应配对1408次free；其CPU扰动超门，不能领取ms。r2管理allocator全69格窗口内配对通过，但必要费、合法替代净价、全进程资源和保留时长未闭。状态归[原矩阵§19.27](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-boundary-cost-audit)。前批[余项价格/数量](rw-residual-cost-r0/RESULT.md)、[最低路径/读保护](rw-minimum-cost-r0/RESULT.md)和以下旧图表各守账期，不跨批拼接。

**最新读写账期：** bb62f28b7a的[迁移净价与互斥预算图](NATIVE_READ_WRITE_RESULT.md)及[native-read-write-r1/account.json](native-read-write-r1/account.json)已按同批parent/candidate/upstream重算。主格净省2.543625ms/36.369050M，余5.695313ms/77.244153M，其中write余2.952988ms/50.217588M；4项CPU控制未通过，正式门不晋升。本文下面的图和机器数值保留原冻结账期，不能混算累计收益。此前d5f715的[读写局部价格](READ_WRITE_PROTOCOL_RESULT.md)仍为历史对照，新当前裁决归原蓝图§19.21。

**当前责任诊断与下一设计：** [192过程诊断](rw-protocol-audit-r0/README.md)否决全量观察器价格，稀疏估计将主要责任定位到final input/physical plan及seal；计数确认3968次proof归属查询和noop两类ID各1024次。当前责任暴露不是upstream额外成本或净可回收预算。统一事实流、必要分支、取消/读取/释放及同批删除目标归[蓝图§19.22](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-single-protocol-audit)，产品仍bb62，本轮未实施。旧§19.15及事件索引保留其当时预测，不再作为下一方案。

**必要性进一步拆分：** [新138过程](rw-protocol-audit-r0/NECESSITY_RESULT.md)核实768次零delta/128次补debt的spare交接、1024次无dirty域探查、1984次无Retiring版本访问。物理plan暴露12.707M/0.752ms，其中ledger准备/提交约6.050M/0.401ms；物理claim约0.241M/0.038ms，completion总验证约0.035ms。责任必要不代表当前表达必要，所有暴露均未领取为净收益。读写额外53.451M/3.374ms的A/B/C金额仍为未知；[机器分类账](rw-protocol-audit-r0/necessity-classification.json)保留null，不伪造比例闭合。修订约束归原蓝图§19.23，实施矩阵仍只有§13。

**闭环边界：** 冻结用例的支出加法已闭合；bb62的联合替代净价见首段，资源/合同与锁调度仍有范围缺口，剩余费用尚未证明必要。此前[集中裁决](BUDGET_COMPLETENESS.md#1-当前闭环裁决与明确关闭条件)、本文主图及§1–8属于原CPU账期，§9–13为各次证据增量；旧“retag未实现”和“下一步”不覆盖首段当前实现与§19.22目标，不要求先穷举全部平台和全部锁。

**整理日期：2026-10-11。产品：`11c6895ddf`；同依赖 upstream：`9a24ae0d8c`。** 主图固定原账期；后续plain/资源/入口/压力新采样独列于§9，不更换主图分母。产品改动0。当前裁决仍在[92](../../92_br1_m6_m8_execution_baseline.md#pagestore-pipeline-refactor-core)，实现状态仍只有[蓝图§13原33项矩阵](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-change-index)；本文是预算视图，不另建实施状态表。

主账能够回答：**额外 CPU 花在哪个阶段、哪个线程。** 目前不能完整回答：这些费用中哪些是必要成本、哪些可合法删除、替代后净省多少。最重要的量化结论是：K16/W16/H1 的额外 process CPU 均值 **11.962375ms**，其中 write 前台 **4.649351ms**、read 前台 **1.698595ms**、reclaimer **4.189938ms**，合计 **88.09%**。这是定位范围，不能领取为88.09%的可回收预算。

<a id="frozen-cpu-budget"></a>
## 1. 冻结CPU支出账：阶段/线程分解，不是当前闭环总图

![PageStore 同义性能预算图：当前及upstream完整CPU、额外成本分解、尚未知的净回收预算](performance-budget.png)

[可缩放SVG](performance-budget.svg) · [完整精度机器账](performance-budget.json) · [复算与作图脚本](build_performance_budget.py)

图中“预算”分三层：

| 层次 | 定义 | 当前能够填写的内容 |
|---|---|---|
| 当前支出 | 当前实现实际付出的完整 CPU | 主账H1 process均值13.8304375ms，upstream为1.8680625ms |
| 对齐差额 | `当前 − 同义upstream`，指出需要解释的支出 | 11.962375ms，按业务区间和线程可相加分解 |
| 合法可回收净预算 | `当前 − 完整合法替代`，扣完新增工作及所有线程/退出增费 | **未知（null）**；完整设计对象见§19.15，尚无实际替代净价，不填0，不按热点比例估算 |

upstream 是可运行对照，不是算法必要下界；对齐差额不是可删除上限。图中几乎全部费用已有阶段/线程归属，也不意味着机制净账几乎完成：**未定价部分存在于各个大桶内部**，不是仅剩右侧微小边界残差。

## 2. 固定分母与证据账期

主图固定采用 `net-ledger-r1` 的 **32个mode0计时过程、8个平衡块**；每块每侧2过程先取均值，再作current−upstream。ARM64，同一Qt/依赖，完整8case为K1/16 × W1/16 × H0/1。mode0关闭内部scope计时，但保留派生钩子及线程边界读取，**并非完全无插桩产品**；本图是诊断基线，不替代正式性能门。

每case包含四次manager寿命：初始完整写入/commit，W次交替完整写入且每次即时读，最终commit，H1另有undo/read/redo/read，purge/销毁，最后显式即时drain。K16为256×256 RGBA8，页64×64；每次完整写入256KiB。四寿命合计公共写入17MiB，H1显式读取18MiB，这是逻辑输入/输出量，内部比较、初始化、复制和真实内存流量另计。即时drain不证明一般压力下所有未来deadline已经结束。

| 证据账期 | 用途 | 可以进入主图吗？ |
|---|---|---|
| `net-ledger-r1` mode0；[全流程重算](flow-ledger-audit.json) | 同批前台阶段、具名后台、尾部及边界的加法账 | **唯一主时间来源** |
| `flow-census-r1`四过程 | payload、binding、owner、proof、metadata、descriptor建立/退出 | 只作数量旁证，不乘未知单价 |
| `execution-r2`36过程 | phase/job、队列交接、扫描/退休次数、CPU端点及有限gate获取 | 只补工作关联；主case观察门失败，不能换入主图的时间 |
| 完整调用树抽样68过程 | 约1/4树计时的能力试验 | H0/H1联合观察门失败；内部机制估计不纳入预算 |
| 同步票据44成功过程、直接前台回收56成功过程 | 各自完整候选相对当批baseline的净收益 | 分别结算，不与主图或彼此相加 |
| 整轮170过程中的存储/业务对照 | 相对重构前8198的已实现收益与业务控制 | 作为独立结果，不从本图再次扣除 |

主图与下节加法表用**算术均值**；配对中位数及95%区间用于评估差异，不参与逐桶加法。8块bootstrap为100000次、seed20261011、pointwise95%，不是同时覆盖所有桶的联合置信界。小数位供复算对账，不代表等量测量精度。

## 3. 主时间账：全部互斥项与尾部

单位：**ms / 完整case / 四manager寿命；current−upstream的均值**。负数保留，表示该项当前较低。小计和合计不再加入求和。

| 互斥成本项目 | H0：K16/W16 | H1：K16/W16 | 归属说明 |
|---|---:|---:|---|
| setup前台 | 0.667703 | 0.842932 | manager构造、初始写入/commit及H1 memento；含首次/暖态混合 |
| write前台 | 6.295622 | 4.649351 | 完整写操作区间；也含旧值选择/比较，不是纯复制价格 |
| read前台 | 1.729878 | 1.698595 | W次显式即时读；undo/redo附带读在其各自区间 |
| finish前台 | −0.011859 | 0.161552 | 最终commit |
| undo前台 | 0 | 0.133557 | rollback及验证读 |
| redo前台 | 0 | 0.102719 | rollforward及验证读 |
| teardown前台 | 0.194492 | 0.151222 | purge、memento/manager销毁的前台区间 |
| case frame前台 | 0.038991 | 0.030820 | 阶段以外的case框架与检查 |
| drain前台 | 0.001719 | 0.001448 | 显式即时drain的前台CPU |
| 观察边界前台 | 0.000323 | 0.000471 | 外层线程观测与原case/drain端点偏移 |
| **前台小计** | **8.916868** | **7.772667** | 以上十行合计 |
| reclaimer CPU | 4.895375 | 4.189938 | 后台历史、退休、临时对象及最后释放等责任 |
| monitor CPU | 0 | 0.0023125 | wake/deadline线程 |
| pooler CPU | 0 | 0 | 本账差额为0，不外推所有负载无成本 |
| swapper CPU | 0 | −0.002875 | 保留负差额 |
| 未登记线程/边界残差 | 0.000070 | 0.000333 | CPU边界余项，不命名为锁等待 |
| **完整process合计** | **13.812313** | **11.962375** | 前台＋具名后台＋残差 |

机器账保留完整精度，表中四舍五入会产生末位差；本次从归档原始32过程重算全部8case，逐过程/逐块共576项加法核对通过。

H1图中的“其余前台”是setup、finish、undo、redo、teardown、frame、drain、观察边界之和 **1.4247215625ms**；“其他线程与边界净修正”是monitor＋pooler＋swapper＋未登记边界，共 **−0.000229375ms**。因此：

```text
11.962375 = 4.6493506875 + 1.698594625 + 1.4247215625
          + 4.1899375 − 0.000229375
```

| 统计差额：配对中位数 [pointwise95%] | H0 | H1 |
|---|---:|---:|
| 完整process CPU | 13.70375 [13.1305,13.9570] | 11.87075 [11.3505,12.6195] |
| 前台CPU | 8.72780 [8.37667,9.06210] | 7.65266 [7.31723,8.34131] |
| reclaimer CPU | 4.92025 [4.7545,5.0055] | 4.21875 [4.0350,4.2780] |

drain已包含，原H1额外drain process均值0.02225ms不能再加一次。后台与前台可同时运行，完整CPU可按线程相加，wall和排队区间不能照此相加。H1当前与upstream的process均值只相差11.962375ms；不能再叠加旧170过程的13.126ms或业务Stroke差额。

同批规模旁证：K16/H1从W1增至W16，current−upstream的额外process增加均值 **10.0144375ms**，占W16差额83.72%；配对中位9.7475ms [9.4635,10.7875]。这是15次额外“写＋即时读＋诱发回收”的联合成本，不能除以960当每个Fresh的单价，也不能推断删除Fresh即可追回10ms。

## 4. 把预算桶接回真实管线

```text
公共输入与真实可见cut
  → operation归属 / capture与旧值比较
  → Fresh目标、payload、binding、provider / owner身份准备
  → metadata / descriptor / proof / overlay接受与发布
  → adapter交付 → 显式读取及读者最后归还
  → history可达性扫描 → metadata退出 → retirement
  → provider释放 → owner / budget退出 → 最后物理释放

拒绝/取消从各接受边界返回原owner；已交接记录继续由原队列收尾。
```

| 管线责任及源码入口 | 已有数量/工作证据：H1四寿命 | 与主预算的关系 | 仍不能定价的部分 |
|---|---|---|---|
| `Backend::runCpuMutationOperation`、`Store::captureReadView`、`ReadCoordinator` | operation/seal各68；capture/归还各140；独立read入口72（含undo/redo附带读） | 同时进入setup/write/read/history；不能只对应read的1.699ms | 视图选择、页查询、pin、锁和归还各自的同义额外成本 |
| `Store::prepareTarget`、`Tiles3Provider`、`OwnerLedger::registerBacking` | Fresh/rows/provider adoption/binding/owner physical/backing各1088，退出成对 | 写侧准备及后续退休共同构成完整寿命 | payload字节、对象/索引、准入、证明各自价格；复用失效/retag的新增成本 |
| `Metadata`、`Publication`、overlay/epoch安装 | 非默认metadata1088＋default64；descriptor准备/安装1152；proof1088 | write/setup/commit及后台清理互相联系 | 表示能否合并、发布粒度是否必要、失败闭包成本 |
| `HistoryCollector::collectSliceLocked/collectPassLocked` | 88 pass、1280版本访问、1408页访问、1600 root访问 | reclaimer及少量前台；不能把4.190ms全归history | 被保留候选与可删除版本的必要访问、重复扫描净价 |
| `RetirementQueue::retireRecord`、provider/owner终结 | 尝试/成功1088；retirement jobs60–64；全部reclaimer jobs236–240 | 后台及teardown等前台；线程间工作转移不等于删除 | 任务、同步完成协议、gate、清理及最终释放的互斥价格 |

前三行数量来自原scope/flow census，后两行来自`execution-r2`；它们解释同一冻结产品的行为，**不与其他批次时间相乘**。完整12条流程、原T索引及其它consumer见[蓝图§19.4](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#full-flow-ledger-audit)。当前主账不能给metadata、复制、锁、票据等机制排一个有合格净价支持的名次。

## 5. 数量与资源预算：累计周转、峰值和驻留分开

| 账目 | 已确认 | 缺口或边界 |
|---|---|---|
| payload对象周转 | 当前Fresh1088，upstream副本请求128；含4个默认对象后free为1092/132，多960次 | 是对象周转差；此前payload cache hit95.4–98.5%，不能写成960次系统malloc/free |
| provider / binding / owner / proof | 每类1088建立和退出；最终provider allocation、owner backing/proof为0 | 终态守恒不证明途中峰值或保留时长 |
| metadata / descriptor | 各1152建立；metadata显式退出1088＋最终arena64，descriptor显式移除1088＋最终map64 | 最终64条逻辑记录不是64块仍存活payload |
| completion | Pending发行1096；局部替代实测能少1088张 | 逐ticket全寿命未普查；56→24 B是记录大小变化，不是峰值下降1088×32 B |
| read / retirement record、root / adapter | 已有部分scope及交接关联 | 尚缺完整live/peak/reserved/保留时长及压力分布 |
| 条件工作目标复用 | H0两目标/页可构造128个非默认对象；H1再保留undo origin为192个，对1088条件少960/896 | 不是严格下界或已实现删量；逻辑generation未必减少，不能直接预测峰值内存或净ms |

资源预算需同时记录`live、reserved、peak、保留时长、最终残留`，按真实重叠寿命核算。复用方案必须支付代次/ABA、旧binding失效、预算重分类、压力回收和最终释放；不能只把累计少创建的字节量当常驻节省。1/4/8/16 BPP、partial/no-op/default、保留读者、swap/预算拒绝等覆盖保持开放。

## 6. 独立净收益账：已实现、未合格与回退

本节统一使用 **`节省 = 当批baseline − 当批候选`**，正数表示省CPU，负数表示增费。区间均沿原批pointwise95%；不从主图减去这里的数字，也不把不同候选收益相加。

| 独立比较与端点 | 机制/删量 | 净节省中位ms [95%] | 已有裁决 |
|---|---|---:|---|
| 整轮8198→11c689，H1完整case前台 | 原管线收敛的联合结果 | +2.17497 [1.22840,2.46796] | 已测局部收益；不表示原全部控制通过 |
| 同轮H1完整case process | 同上，计入其他线程 | +3.31800 [1.77300,3.64950] | 该批原case端点，不能与主图含额外drain的账混算 |
| 同轮业务Stroke CPU | 独立业务联合控制 | +0.60900 [0.37350,1.21950] | 单列；不能作为PageStore同义基础性能证据 |
| 私有Pending→原同步Succeeded证明 | 发行1096→8，实删1088，记录56→24 B | **−0.01550 [−0.26500,1.02850]** | 未过预定0.75ms收益下界；候选撤回，不等于证明零收益 |
| 旧Prepared逐页直接前台回收 | 960次直接删除命中，Fresh/free保持 | **−1.62125 [−2.79300,−0.83800]** | 完整process回退，候选否决；后台变少不能抵消前台增费 |

以上0.75ms是局部判别包的最小值得收益门；观察器±0.75ms是另一种粗精度门，**都不是M6正式门**。固定20%/30%已不是当前M6退出硬条件，机会型命中、miss/拒绝、原保护控制、资源、结构和业务预算仍按[92 §6](../../92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)独立取证。CPU账不给GPU百分比或容量资格。

尚未定价的完整方案继续比较：旧不可达backing/身份存储复用、原owner证明/准入收敛、真实可见cut下的operation/发布粒度、固定视图读协议、可达性/队列调度，以及clone/导入/稀疏交付。各自必要/新增/保留工作见[蓝图§19.5](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#full-flow-ledger-audit)，本预算图不预选赢家。

一个方案只有完成以下净账，才可报可回收预算：

```text
完整净节省 = 避免发生的完整寿命成本
           − 替代表示、证明/失效、准入、调度及最终退出的新增成本
```

所有项必须互斥并覆盖全部线程；前台移后台不算避免发生。少一个身份同时减少descriptor/proof/退休时，这些费用只能计一次；两个方案覆盖同一寿命不得分别领取同一预算。wall关键路径、峰值资源和失败/压力控制另行验收，不能用CPU收益抵消。

## 7. 最新证据如何改变账本解释

**首次setup单列，尚未分摊具体机制。** `execution-r2`中H1置于进程首case时，current首次setup约1.37–1.46ms，后续manager约0.19–0.27ms；upstream首次也约0.87–0.96ms。mode0的setup总和亦按首/末case分离。主图保留冻结顺序的混合分母，没有从旧账扣掉新批的首次差额；具体初始化器/cache/分配器占比仍未知。

**稳定计数只约束已观测区间。** H1八个观测过程退休1088次全成功，扫描量稳定，所测重启、rescan、blocked及retry arm/wakeup为0；但前台退休80–128、后台960–1008。另一个mode0慢过程无内部事件，不能拿这些零计数替它排除工作放大，更不能事后删掉它。

**排队和锁获取不是等待全价。** H1入队→出队平均11.38–12.33µs，其中与前序job重叠8.51–9.99µs；剩余包含observer、gate、唤醒和调度等，不能叫runnable时间。所测collector owner/retirement queue获取不覆盖全部Store/read/provider/owner caller、executor mutex、持锁及内核blocked；CPU编号端点也不证明驻留或频率。[完整范围](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#execution-work-correlation)保持。

**机制时间仍未取得资格。** 抽样68过程的H1 process on−off区间[−0.9475,0.4810]ms、事件36过程的[−2.4410,2.2425]ms，都未完全落入±0.75ms。两批均停止，未追加到通过。前者的cold/self、后者的job/lock区间不作为可删单价。后续12.6190ms等诊断差额点值不替换主图的11.962375ms均值，也不据此报告产品回退。

## 8. 预算资格与补账出口

| 需要作出的判断 | 现在的证据强度 | 预算处理 |
|---|---|---|
| 主批额外CPU及阶段/线程归属 | 可从原始数据确定性复算；总差异有原配对区间 | 可用于定位阶段/线程责任 |
| 已测实体数量守恒与任务关联 | 在冻结fixture和观测模式内重复成立 | 可约束算法删量；不换算时间或峰值 |
| 各机制为何增加、必要/冗余各占多少 | 目标观察精度失败，完整等待及资源证据不足 | 金额未知，不记“正常管理成本” |
| 完整替代净收益与最优方案 | 两个局部替代已有反证或未合格结果，全设计未定价 | 净预算null，不能排序为确定收益榜首 |
| 全生产覆盖及M6资格 | M6/M7/M8 0/3，正式校准2/20、默认关闭；live-copy和业务控制未闭 | 不由预算图晋升 |

后续已按[唯一流程账§19.9](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#budget-resource-entry-coverage)补C/D与plain，见§9；原表的冻结主账不随新批改写。A的合格机制价、B的同一慢过程/双侧完整追踪、C的原库移授及部分类型、D的失败合同与更多压力分布仍开放。对有限H1候选，只补会改变其合法性、净价和回退判断的A–D依赖，再比较E；全锁/全平台普查不是统一前置条件，未覆盖的结论仍开放。

更新本文时保持：主图一个账期、一个端点、一个估计量；新批独列；必要/避免/新增/未归属都有位置；涉及多个责任的同一费用只记一次；数量、CPU、wall、资源分开；保留失败、负项和未知。通用业务优化另记，不抵扣PageStore本体差额。

复算命令（只读冻结证据并生成JSON/SVG，不运行基准）：

```sh
python3 docs/vulkan_gpu_design/evidence/br1_pipeline_refactor_20261010/build_performance_budget.py
sips -s format png docs/vulkan_gpu_design/evidence/br1_pipeline_refactor_20261010/performance-budget.svg --out docs/vulkan_gpu_design/evidence/br1_pipeline_refactor_20261010/performance-budget.png
```

脚本直接读取已提交原始包中的32过程结果，核对成员SHA并重算8case加法；来源文件SHA与限制保存在[机器账](performance-budget.json)。PNG由SVG栅格化并目视核验。主图复算不运行新基准；后续补数不产生性能收益或技能排名/预测能力资格。

## 9. 沿图补数后的状态：新批独立结算

详见[闭环补数账本与图](BUDGET_COVERAGE_LEDGER.md)、[64格矩阵](BUDGET_ENTRY_MATRIX.md)。36个公共过程全部通过自身断言和回放，60/64同义；4格坏尾导入失败副作用不同，禁止性能比较。

- 真正plain H1再次出现32.070ms慢态；新批额外CPU中位11.93675ms [11.439,20.803]，不替换旧图均值。current外部追踪前台状态闭合，upstream缺前台tid，同一慢过程因果未闭。
- H1 payload周转1092/132，观测峰值49/33，累计多960与峰值多16分别记账。provider/binding/owner各1088建立、峰值48、最终0；root128建立、峰值32。管理存储峰值约2.05～2.12MB，其中1.115MB为已有runtime，不能与逻辑项相加。
- 压力12过程682/2/0：同一冷基线断言两模式失败，573680 B增量中557056 B及240 B有实体事件并在退出释放，16KiB差额与原生线程控制收费一致但未单独打点；原库暖序控制通过，原失败不撤销。
- H1观察器扰动门仍失败。原库资源峰值/寿命移授、pool备用块/RSS、部分read/adapter类型、完整reservation时长和压力分布仍缺。C/D补得更具体，但没有整体关闭；合法净预算保持null，M6不晋升。

## 10. 慢过程的执行条件账：不抵扣稳定本体差额

后续[同过程归因与完整限制](SLOW_PROCESS_ATTRIBUTION.md)独列68自然＋72QoS干预过程。3个自然慢态指令只增0.3～1.0%，P核CPU占比降到2～49%，CPI增大/有效速率下降共同解释67～122%的CPU增长。H1对称干预off组current 13.256→47.0585ms，upstream亦1.3405→6.114ms。旧32.070ms是同类执行条件变化的最有力推断，旧事件本身仍缺直接计数，不删样或重写原图。

正常P核条件下，新批H1额外CPU中位11.5975ms [11.112,11.808]、counter off均值11.4991ms，current指令约6.84倍；执行条件无法解释掉稳定差额。counter模式另有可加代数账11.5341ms＝数量项8.3409＋每指令成本项3.1932ms（以upstream每指令CPU作参考），不等于责任价格或可删除预算。自然H0/H1边界观察门通过，但QoS干预门失败，on的核类份额不精确移授off，亦不追认§9资源门。

预算裁决：B取得有限自然慢态机制及H1干预因果，历史单次仍推断、全锁/等待仍开放；产品主线仍找正常条件下额外指令的具体管线来源与合法替代。A/C/D/E缺项及M6保持，人工提高QoS不列优化收益。[可复算因子账](slow-cause-ledger.json)、[唯一流程账§19.10](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#slow-process-attribution)。

## 11. 指令责任账：定位完整身份周转，未兑换成净收益

[新批指令账](INSTRUCTION_LEDGER.md)独立于原CPU图：H1原库额外153.25M条 [151.46,155.04]M，前台102.32M、进程减前台50.92M；派生角色核对支持后台主要为reclaimer。scope on的cold53.95M、history25.19M、retirement task20.60M是成组的大责任。额外CPU12.8494ms [11.3593,14.9711]仍保留慢样，不替换原主图11.962375ms。

新观察器CPU粗门失败，99.7M observed不记为可删预算；provider建立、预算登记、metadata删除及物理退出没有单一支配函数。选择[原矩阵§19.11](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#instruction-lifecycle-design)的完整旧目标/身份复用设计门，明确必要generation与可复用物理寿命分离。H1条件1088→192、少896对象是构造数量，不是82.35% CPU预测；donor唯一持有、不可达凭证、retag、收费/压力和失败/drain尚未闭合，产品仍未改、净预算null。下一有界原型依赖这些实际合同，不再追加本包scope样本或把通用优化计入PageStore证据。

## 12. 完整性复审：支出闭合与方案定稿分开

[预算完整性报告](BUDGET_COMPLETENESS.md)从原始归档重算1393项：H1原库额外153.246962M中write73.659212M、显式read13.420408M、其余前台15.244819M、进程减前台50.922523M。scope on另有11.235415M当前角色内未命名指令及−0.114702M两层窗口修正，不能用主CPU微小残差宣称机制全明。

§11的完整身份复用降为有数量依据的比较候选，不以99.7M粗责任授予最大合法净预算。旧目标的metadata退出、唯一持有、budgetClass迁移与原退休队列交接尚需设计；证明/准入、读及H0发布仍为竞争方向。15%指令门是价值阈值，不是收益预测，只达门仍有125.777509M upstream差额。完整性足以做有限设计判别，但尚不足以给收益确切的生产方案；不再原样追加scope，不要求无关全锁/全平台穷举。产品/测试/新基准均0，原门禁不变。

## 13. 交接能力与条件删量：保留责任和写许可分开

[本轮8过程](DONOR_LIFECYCLE_DESIGN.md)没有新增CPU价格，却关闭了两个实现选择问题：普通H1旧proof撤销后960个目标均为ActivePending且原prepare/claim/cancel通过；下一写896个有来源目标均已退出。metadata Historical并不立即转Debt，直接等下一写再查历史页没有可靠可用量。须在原接受内完成旧逻辑退出与有收费备用容量移交，不回收后再注册，也不另建池/退出账。

clone/native分别使即时物理许可拒绝64/4次，保留其校验。仅保留容量无需先独占，实际checkout才申请；避免新增960次重复保留时claim，仍要扣除约896次实际handoff及所有保留/清退费用。这960次不是现有产品可删量。

四寿命K16/W16的源非默认physical条件建立量：普通1088→192（少896），一页持续holder→196（少892），16页持续clone→256（少832）；源每寿命峰值模型48/49/64。2616状态模型验证其建模域内的held字节、最后成功值和最后释放后排空；不包括clone侧其余分配、不移授plain资源峰值。逻辑generation、960个逻辑旧版本退出与逐写公共输入/输出仍是必要工作。

产品实际metadata删除/retag/代次拒绝及资源保留尚未实现，新净指令/毫秒继续null，旧支出图与独立失败候选价格不变。下一可定价对象已明确为“接受内逻辑退出＋原槽有收费保留＋下次原claim/retag＋所有出口原责任清退”的完整替代；不得拆小领取重复收益，也不能把本次能力通过当正式性能门。[唯一蓝图§19.13](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#donor-lifecycle-capability)承接，无新实施状态表。
