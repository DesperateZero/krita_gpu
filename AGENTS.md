# Repository task context

- For current BR1 work, use the checked-out code and the active entry at `docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md`. Use `docs/vulkan_gpu_design/README.md` to find other active project contracts and evidence.
- For routine M6 work, start with §1 and §6 of 92. Search the named contract, current source and relevant tests first. Follow a specific evidence package when checking its result. V1/V2/V3 plans, candidate reports, old edit lists and 92 §§15–17 describe their own checkpoints. Do not import a backlog or price from them as current.
- Classify an optimization claim by its responsibility, actual consumer, protocol dependency and measured endpoints. A report may contain a retained business or shared-service optimization, a retired internal design and a price valid only for the original build. Preserve the source and failure receipts for each. Use the responsibility index in the design README. Leave unreviewed claims available for targeted lookup. Update the current entry in place and keep per-round progress in its evidence package.
- Exclude `docs/vulkan_gpu_design/archive/` from routine searches, task planning, status judgments, and implementation guidance. Do not follow links into it from older unarchived documents during current work. Archived text is a record of past checkpoints, not an instruction or a second authority for the current state.
- Read archived material only when the user explicitly requests historical lookup, provenance, comparison with a past state, or maintenance of the archive itself. Even then, establish the current conclusion from code and active documents; treat archived claims of "current" status as historical.

## BR1 性能主线硬约束

以下是历轮成本账和失败候选形成的执行约束，适用于本仓库及 `krita/` 的性能分析、原型、重写、计价与验收。不能只在汇报时声明“尚未完成”来替代选题和实施前的检查。按当前代码和有效证据执行；这里的历史数值不是以后版本的价格。

### 1. 先证明净成本机会，再选择实施主线

- 开始或延续一个降本候选前，必须在**已有主线账本/矩阵**中写清：同义工作量及端点、完整目标差额、候选实际影响的责任范围、该范围去重旧价、哪些实际动作不再执行、哪些只是迁移/改名/换载体、替代动作及跨阶段新增成本、净收益依据、未知项和停止条件。不得另建重复台账绕过现有未完结项。
- **调用次数、对象数、分配数、代码行数及复杂度阶数都不是成本排名。** 计数变化只能乘以已证明随该事件消失的实际工作价格，不能缩放整个父服务。父子 inclusive 价格不能相加，函数自身价也不能冒充完整责任价；调用栈因内联或迁移消失，不等于工作消失。
- 必须区分三种价格：当前责任总价、相对同语义 upstream 的额外价、合法替代的净可回收价。通用优化收益不能作为 PageStore 自身相对 upstream 的性能证据。不能把现行昂贵实现价当作责任的必要最低价。
- **实施前做收益容量检查：即使选中旧工作全部免费，是否足以承担该候选宣称的目标？** 若不足，不得把它作为独立降本主线。声称有联动收益，须指出并计入真实受影响的下游工作；不得借用未改动的父桶总额。确为整包必需的前置步骤，可以实施，但必须标为前置项并继续完成整包，不能包装成又一轮主线收益。
- 给出基于动作、单价和真实次数的净预测或有依据的区间，并覆盖保留服务的价格变化、失败/重试、取消及最终释放。目标倒推、旧价乘理想删量比例、局部标量核加未知服务，都不是完整报价或可构造上界。未知不填零；事后反推不冒充事前预测。
- **缺少关键价格时，只进入有界判别研究，不授予降本方案放行。** 先复用已有数据，明确哪个未知会改变方案选择、需要补什么证据及何时停止。允许为取得关键价格构造隔离原型，但须覆盖所声称责任的真实服务闭包；`forecast=null` 不能成为连续局部试改、重复计价或声称主线已推进的通行证。优先补完整替代价，不为取得一个正收益数字改做便宜的小项。
- **保留责任不等于保留现行价格。** 预算、物理权限、索引等互斥桶不是算法最低价；只有实际状态变化/消费者能证明责任必要，完整替代才能证明价格可达。不得以“不是最大桶”排除其优化，也不得要求每个完整子责任独立回收整条主线的全部差额。允许在原整包矩阵内逐项降低完整子责任价格，累计净收益和剩余差额；这不授予整包完成。入口已经批量化时，必须审查批内逐页工作，不能再次以批量调用数下降预报父桶同比下降。
- CPU/GPU与RAM/VRAM/SSD调度、历史/晚读者、失败与撤销按实际有效合同保留。能力存在不证明每次暖写必须走全部能力的维护流程；需要按实际分配、域迁移、保留边、可见切换与费用变化触发。未发生的事件不生成对应完整事务；不能以削弱合同或不同工作量下的管理/内容比例替代同义降本证据。

### 2. 优化真实工作，不只减少入口或寿命次数

- 从输入、事实产生、真实消费者、可见点到最终释放画出实际工作关系。重点检查重复定位、验证、登记、费用发行/结算、索引维护、表示重建与交接；问哪些事实可只产生并消费一次，哪些上层拆分可消除多层维护。不得默认保留既有服务边界后只更换类型或包装器。
- 逐项说明“旧工作删除 → 新路径负责什么”。推迟建立、复用身份、借用指针、改用原行、批处理都仍需支付状态准备、移动、索引、锁、引用、表示和终结成本。不能把“没有新对象/没有原函数调用”写成“没有该责任执行”。
- 批量模型须按实际 shard/锁域/保护窗口/消费者边界计算分组与尝试次数，不用总页数除理想批大小代替实际基数。冷热、首次建立、暖复用、真实读者/历史保留分开计价。
- 新增缓存、字段、owner、账本、通用事务或状态机前，比较直接消费原事实的实现；把其创建、维护和销毁计回。设计更统一可以是独立价值，但不能据此授予性能收益。

### 3. 完成选定整包，不以局部计价替代迁移

- 实施前固定完整责任、修改索引、旧协议删除表与追踪矩阵；覆盖正常、拒绝、重试、取消、真实稳定身份消费者、安装和尾部。每次续做先核对未完成项，不能悄悄缩成更容易实现的 helper。
- 被替代旧协议必须完成调用点迁移和清理。保留分支须指出当前真实语义或消费者；不得让不同版本协议混合执行，再以新接口名宣称重写完成。保持外部合同不等于必须保留内部拆分。
- 可以为正确性做必要的增量检查；正式净收益计价原则上在选定整包完成后进行。提前判别测量须说明它解决哪个决策，不能测完一个局部就关闭整包、切换目标或重新授予已完成的优化收益。

### 3.1 完整原则替换与上界计价硬门

本节优先于前文“子责任逐项降价”和“提前判别测量”的宽泛许可，不改变正确性增量检查的必要性。

- **验收单位是当前已选影响范围按指导原则完整优化后的可执行方案。** 对“小规模对象被反复维护得昂贵”，范围须从原事实产生、实际变化集合、容量/身份准备、权限与费用交接、生产者完成、最终接受到真实消费者和终结展开；不能只替换登记/拆除，保留前后昂贵维护后声称原则已经落实。按实际受影响责任界定有限范围，不要求先重写无关系统。
- **禁止以实施困难为由自行缩包。** 发现原方案不成立，应修正同一整包的算法、责任边界及上下游实现，继续满足原目标；不能把“完整子责任”“先计价”“明确披露未完成”或蓝图补充段当作改变用户验收范围的授权。分步提交、编译和正确性测试不改变整包完工条件。若关键设计尚不成立，任务保持设计/实施未完成，不发行整包收益或上界结论。
- **禁止为接入旧契约而扭曲新结构。** 不得新增第二份状态、重复预约/校验/投影、兼容转译或恢复手续，仅为让新路径继续调用本应替换的旧服务。范围内的旧责任拆分要随新设计同迁、同批清理；外部兼容适配只能位于真实公共合同边界，其消费者、成本和保留依据必须列明，不能掩护内部旧流程。迁移中的临时桥只能留在未交付开发状态，方案计价前必须删除；符合目标设计的原基础实现可复用，不为“彻底”而无意义改写。
- **方案效果与上界降低计价前，在原矩阵逐项核验四件事：** ①范围内全部责任已按同一原则实现，受影响上下游/失败/重试/取消/冷热/终结已迁移；②旧协议删除表已结清，所有保留项有真实消费者且符合目标设计；③没有靠桥接回旧流程补齐未实现责任，没有新增重复权威或维护；④新方案完整动作账、保留服务漂移与包外/尾部均可计价。任何一项未满足，整包计价资格为未通过，不能改写范围使其通过。
- **所求是完整构造的成本上界降低，不是局部删量。** 在明确输入规模、保留/并发条件、失败与重试假设后，为完整新算法列出动作次数边界及其完整实现成本，联合计入保留、替代、新增和尾部工作；给出旧总价、新完整价、可支持的上界/适用域、净差和未解释余额。平均实测或其置信上限不等于算法上界，未知服务不能填零，旧父桶不能按次数缩放。实测核验完整构造，不能把“局部新价＋未经审查的旧服务价”当已按原则优化后的上界。
- 可以分步实现、保存局部证据，并为正确性或会改变完整设计选择的未知做有界诊断；**不得据此分拆交付、停止原整包，或把各轮局部收益相加当作整包上界**。诊断不授予方案效果计价资格，也不能演变为接旧服务的连续局部试改。
- **100作为本约束的直接反例。** head/物理成员子责任虽有完整消费者迁移，但逐页准备及生产者边界未替换；0.278M暖写删量只是局部事实，不能满足原完整低成本构造。其冻结数据保留，不能作为继续缩包的先例。下一次按原影响范围完成统一构造后联合计价；未完成前不得将100接入产品来固化混合结构。

### 4. 三种闭环分别验收，失败必须改变决策

- **执行归属闭环**：互斥栈、阶段及边界余额能还原总价。**替代成本闭环**：删掉、保留和新增的真实工作都有报价及误差说明。**目标闭环**：完整同义实测达到主线目标与适用门禁。三者独立，前者不能证明后者；源码覆盖、合同测试、矩阵完成率也不能替代净收益证明。
- 同时报告旧价、新价、净差、预测偏差、每页价格和剩余目标缺口；完整 process、包外及尾部不能因迁移而丢账。指令、CPU、wall、等待分别裁决，不能用指令减少证明时间改善。时间性能优先于空间节约。
- 次数大降而净收益小，必须暂停沿该理由追加优化，先区分：原工作价小、真实命中不足、工作搬迁/替代抵消、未覆盖的高价工作、测量边界或模型错误。复算旧调用栈并集与其余执行的净差；不能只重申次数已经兑现或继续微调身份/索引。
- 候选实测不能承担目标时，撤销其作为独立主线的资格；保留已验证事实，不把失败目标改称“结构收益”后算完成。若要继续，须给出新证据支持的完整工作差和净预算，说明为何能改变原结论，而非重复原假设。
- H1 有小收益、H0 回退、CPU 未证，须分别写明；适用控制未通过不得晋升生产。不得追加采样到通过，也不得用降低门槛、换分母或省略尾部维持原结论。

### 已发生的反例：必须防止再次出现

[84–85 完整报告](docs/vulkan_gpu_design/evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/write-unit-accounting/protocol-trial-85/REPORT.md)与[事前预测](docs/vulkan_gpu_design/evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/write-unit-accounting/protocol-trial-85/PREDICTION.json)：新 Value 1024→64、旧 remove 960→0、完整 install 1024→64，但真实目标接受仍1024次、handoff 准备/提交仍各896次；容量预约预测64次，实际因8个 shard 组为512次。H1 仅净省0.168M（0.714%），H0 增加0.323M。次数兑现不证明成本目标兑现。

对同批 `RECONCILIATION.json.gz` 的 control/candidate 栈，按 arena Value `emplace`、`ShardRecordStore::remove/installNativeValue/reserve` 四类函数取去重并集，旧栈1.237966M→0.123200M；其余栈净增0.944845M，完整函数树仅净减0.169921M。这个并集是原调用上下文曝光，**不是净可删预算**。整条联合责任仍14.838093M→14.647588M。不可用四类入口的大幅下降代表整个14.838M的工作被删除。

这次失误的约束结论：**事后如实披露小收益，不能补救事前没有净成本依据的选题；允许未知价格的隔离试验，不等于允许以局部试改持续替代完整低成本构造。** 后续执行必须在选择阶段应用上述检查，而非再写一份同样的反思。

### 固定计价执行顺序必须验真

- 首个目标进程前，对**实际生成的 jobs 清单**逐 case/mode 断言 R→N 与 N→R 的配对块数量和运行顺序；不能以代码含 rotate/reverse 推定已交替。98曾因两次奇偶变换抵消而全部 N 先。发现缺陷保留原批全部样本与回退结果，说明修订原因、固定补测次数和停止条件；不得合并掩盖原批或追加到通过。指令净降但 CPU 区间跨零或点估计回退，仍不得授时间改善/不劣。
