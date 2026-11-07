# 完整管线重构的实施证据

**2026-10-17累计基线入口：** [各轮优化汇总](OPTIMIZATION_ROLLUP.md)、[逐轮目录](ROUND_CATALOG.md)、[66个历史产品祖先](PRODUCT_LINEAGE.md)及[IB0基线](../br1_pagestore_equivalent_pipeline_20261010/INTERMEDIATE_BASELINE.md)。累计实现已正常集成为 **`ab1bf42e18`**，构建/限定验收、恢复的原合同和已有压力失败见[集成结果](../br1_pagestore_equivalent_pipeline_20261010/intermediate-baseline/integration/RESULT.md)。本次没有新配对性能价，H1近4M操作单价欠账仍开放；下方各批的“最新/下一步”按各自冻结身份解释，历史增量不相加。

**最新计价资格验证（2026-10-15）：** 80普通进程/1040格语义加载通过；原KIS_BR1_SEED不固定Qt布局，同库A/A也出现小格读越线，zero仍有其它变动。H0/H1同库与夹具控制最大约0.60%，约83M/44M额外write未被解释掉。[本批判别和完整净账](implementation-preconditions-r5/RESULT.md)只完善成本可辨识前置，未迁r4候选、不授产品收益；完整暖内核/Optional/Q/T/动作价格及留出继续。产品仍e238，原矩阵和阶段资格保持。

**最新Optional借用验证（2026-10-15）：** 原版24格拒绝来源，仅接线来源仍24格Debt准入失败；候选84a105a2f8按原prepared来源消费真实费用后，24格各16代循环及56格新增防护通过，双架7646通过。固定24普通进程312格语义加载通过，case4写+2.386%超观察线，不迁产品、不补样；产品恢复e238d170d3后双架7486通过。完整暖内核、Optional闲置索引/Q/T、动作价格及留出预测仍未过；不授性能收益。[完整账与原始失败](implementation-preconditions-r4/RESULT.md)，[原33行§19.51](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-management-contract-index)。以下是冻结检查点。

**最新关闭进度验证（2026-10-15）：** 产品e238d170d3，原退休owner在本次释放额度后有界接续准入拒绝记录；删除Store复制终结及旧8次close补救。公开轮转构造的36个原版失败全部修复，双架7486通过。固定24普通进程/312格及39项指令观察控制通过，整进程变化跨零，不领取读写收益。新暖协议/Optional/Q/T/动作定价与留出预测仍未过；原异步失败没有现场轨迹，不授所有间歇close资格。[本批完整账与失败](implementation-preconditions-r3/RESULT.md)回填[原33行§19.51](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-management-contract-index)。以下为各批冻结身份。

**最新接受结果交接验证（2026-10-15）：** 候选63c07f0e5d在原owner内贯通D、原ledger/退休record及真实history通知；双架7462安全通过。固定24普通进程H0 write省2.290M/process省3.678M，H1无明确收益；两个小格写超+2%观察线，CPU未授收益，未扩样。候选冻结在本地独立分支，当前产品恢复0b116b04e8。[完整报告、失败和净账](implementation-preconditions-r2/RESULT.md)回填原33行成本列；完整暖内核/Q/T/价格预测继续开放，不授M6。下文按各批身份解释。

**最新共同接受验证（2026-10-15）：** 产品0b116b04e8完成原epoch/metadata全D接受与原费用退休交接，旧Pending出口统一；双架7414测试通过。固定24普通进程H0完整process省14.061M，但write增加1.724M，H1无指令收益；[本批报告](implementation-preconditions-r1/RESULT.md)同时记录前台增费、后台减少、表示容量、旧失败及剩余条件。完整暖内核、Optional/Q/T和可预测单页价格未过，不授全入口迁移/M6。原33行仅更新成本证据；以下为冻结批次。

**最新实施前实际证据（2026-10-15）：** 产品0f526aea1d含33132de1ec父费修复，双架7364测试通过；[报告](implementation-preconditions-r0/RESULT.md)保存44个原预算反例、被否决的81个预占Debt回归、24格原收费接续以及24普通控制过程。原型不再假定所有Fresh有发布credit；Q/T与完整动作价格尚未过关，不授管理比例/整包收益/M6资格。以下旧“当前”仅描述各自冻结批次。

**当前读写主线（2026-10-12）：实验候选d5f71573bb，未验收。** [101过程读写诊断/计价](READ_WRITE_PROTOCOL_RESULT.md)：896次复用写改为base pin增量，write指令独立确认省9.91%，仍为upstream约13.14倍；write CPU未确认、read CPU本批增0.149ms。完整慢样本保留，不授CPU/M6资格；下一沿[原矩阵与operation设计§19.17–18](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#read-write-protocol)审查输入选择→批次准备→接受→读者退出。以下02bcc及更早结果均按各自冻结版本解释，不作本候选的CPU或资源通过证明。

**当前候选计价（2026-10-12）：02bccf1d12。** [126过程净价与剩余账](RESIDENT_OPERATION_PRICE.md)确认H1指令省16.74%、CPU省2.86ms；其余线程减少37.16M而前台增加7.16M，write增8.44M。5个存储CPU控制、业务Stroke收益和Undo/Teardown非劣未闭，整包/M6不验收；下一审查原T02/T04复用写准备/接受。原[实现/数量/安全](RESIDENT_OPERATION_RESULT.md)、生产净+625行和完整资源未知保持；[原33项](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#resident-operation-implementation)为唯一实施状态。[完整439文件原始包](resident-operation-price-raw.tar.xz)与[哈希清单](resident-operation-price-manifest.json)保留全部新样本和复算输入，旧失败仍在原包。下方“下一/最新”均是各冻结批次。

**下一完整设计（2026-10-12）：** [唯一蓝图§19.15](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#resident-operation-pipeline)从合同重新选择操作级准备/接受、原版本事实合并、H1有界物理容量循环与合格H0直接canonical，旧donor方案纳入整包。明确表示规格、失败/锁/退出、原T项删除闭包及可证伪事件目标；[机器索引与条件模型](resident-operation-design.json)、[生成器](build_resident_operation_design.py)。这是下一完整验证对象，非已测净收益或全局最优；无新基准/产品改动，原33行实施状态不变。

**当前预算裁决入口：** [集中闭环审查与更新图](BUDGET_COMPLETENESS.md)统一支出、机制、交接、净价、资源、调度及覆盖七层证据与关闭条件。只有冻结用例内的支出加法已闭合；donor即时能力及数量模型不补授净价/资源资格。原CPU图明确为保留钩子的冻结诊断账。当前执行限定见[蓝图§19.14](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#budget-closure-recheck)；下方各“最新”仅指各自冻结批次，不构成多份当前裁决。此次无新基准或产品改动。

**最新交接补缺（2026-10-12）：** [实际窗口与最小保留设计](DONOR_LIFECYCLE_DESIGN.md)完成8个隔离过程、512个公共case记录。普通H1即时960个旧目标仍为ActivePending，原handoff准备/独占/取消全部通过；下一写896个已记录目标均已退出。纠正下述“收费类边界意味着即时不可接”的过宽推断：缺的是提交退休前的跨操作保留。clone/native分别拒绝64/4次，物理保护不可删；保留阶段无需重复取得写许可。原transaction/page槽最多1个备用、原owner收费/退出；2616状态模型给源physical条件建立量192/196/256。实际metadata移交/retag、资源压力及净定价仍待完整替代验证，产品未改、M6不晋升。[唯一蓝图§19.13](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#donor-lifecycle-capability)、[7900项复核](donor-summary.json)、[源码索引](donor-source-index.json)、[原始包](donor-raw.tar.xz)。下方“最新”为各次冻结记录。

**最新预算完整性审查（2026-10-12）：** [报告与图](BUDGET_COMPLETENESS.md)完成1393项原始包/源码/加法与原33行核验，无新基准或产品改动。H1额外153.25M指令全部回到同义阶段及前后台，scope外11.235M和两层窗口修正独列。支出图已闭合；99.7M当前责任不授净收益榜首，旧目标复用仍须与共同准入、读、发布及回收联合比较。源码明确旧metadata退出到RetirementDebt与现有handoff可接类之间缺完整交接；合法净预算未闭，不能冻结最优生产方案。[唯一蓝图§19.12](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#budget-completeness-review)给有限定稿条件；[机器账/复算](budget-completeness.json)。以下“最新”为各次冻结记录。

**最新指令责任定位（2026-10-12）：** [完整指令账](INSTRUCTION_LEDGER.md)完成54＋4个诊断过程，H1原库额外153.25M条 [151.46,155.04]M，约2/3在前台、其余主要在reclaimer。新目标准备、history和retirement合计约99.7M observed指令；scope CPU粗门失败，不授原库可删价。下一候选收敛为旧不可见Prepared目标及身份复用，条件非默认对象1088→192、少896；[唯一蓝图§19.11](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#instruction-lifecycle-design)列原位索引、五项设计门和独立验证约束。生产/产品测试零改动、尚无收益、M6不晋升。[协议](INSTRUCTION_PROTOCOL.md)、[原始证据](INSTRUCTION_RAW.md)。

**最新慢过程归因（2026-10-12）：** [同过程指令/P-E/执行速率账](SLOW_PROCESS_ATTRIBUTION.md)完成68自然＋72对称QoS干预过程，42760项复核。直接捕获3个自然慢态：指令仅多0.3～1.0%，P核CPU份额降到2～49%，CPU增加67～122%；H1干预off组13.256→47.0585ms，upstream亦变慢。旧32.070ms当前最有力解释为同类执行条件变化，仍是中等置信推断，未直接重捕自然H1。正常P核H1额外CPU仍11.5975ms [11.112,11.808]、指令约6.84倍，不能把稳定差额归给异常。自然H0/H1观察门通过，干预门失败分账；产品/测试0改动、M6不晋升。[协议](SLOW_PROCESS_PROTOCOL.md)、[唯一流程账§19.10](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#slow-process-attribution)、[原始证据](SLOW_PROCESS_RAW.md)。

**最新沿图补数：** [plain慢态、资源寿命、入口与压力账](BUDGET_COVERAGE_LEDGER.md)独列36过程/64格，60格同义；H1观测payload周转1092/132、峰值49/33，主要实体末端0。真正plain仍有32.070ms慢态；current系统追踪前台闭合，upstream缺前台。12压力过程682/2/0，冷基线573680 B增费有资源/暖序旁证；4格坏尾导入副作用不等价。H1观察门未过，原库资源移授及机制净预算仍开放，不晋升M6。产品/产品测试零改动；[逐格](BUDGET_ENTRY_MATRIX.md)、[复核](budget-coverage-audit.json)、[原始包](BUDGET_RAW_EVIDENCE.md)、[唯一流程账§19.9](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#budget-resource-entry-coverage)。以下各批保留原冻结分母，“下一”以最新裁决为准。

[性能预算图与完整账本](PERFORMANCE_BUDGET_LEDGER.md)汇总同批阶段/线程支出、数量周转、独立候选净价和未知项；[机器账](performance-budget.json)与[复算脚本](build_performance_budget.py)从冻结原始数据核对全部8case。原主图复算没有新采样或产品改动，本轮新增采样独列于其§9，不将成本占比当作可回收收益。

本目录对应[唯一蓝图与33子项](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-change-index)。最新产品仍为**11c6895ddf**，本轮产品/产品测试最终改动0，原双架10466/0/0安全库身份保持。最新**36个基线过程**完成操作/任务/计数关联，主case仍未取得合格机制价格；此前68过程抽样能力、全流程审计及4个数量过程保留。先补全面数据，再比较完整设计；下文旧批“下一/优先”不再是当前排期。44过程同步票据候选、56过程直接回收、106过程线程账与170过程整包价保持各自身份，不跨批相加。整体机制净预算、性能和M6仍未通过，live-source两个exact-view失败保持。

<a id="execution-work-correlation"></a>
## 最新补数B：操作/任务数量关联闭合，完整等待因果仍开放

固定36过程全部成功，产品仍11c689、原库不变，产品/产品测试零改动。12096个phase、9084次成功入队/出队/job、72965个有限gate获取形成112313事件；288个case/role前台与job计数分配精确闭合，1656项生命周期数量恒等通过。原33行六列仍是唯一实施状态矩阵，详见[同一流程账§19.8](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#execution-work-correlation)。

- K16/W16/H1八个观测过程：退休尝试/成功均1088，history版本1280、页1408、root1600访问保持；所测重启、rescan、blocked、重试arm/wakeup均为0。总量稳定但前台退休80–128、后台960–1008，retirement jobs60–64；不得以任务数或单线程差异虚领收益。
- 新分母：H1为进程首case时，首次setup线程CPU1372.54–1455.04µs，后续manager189.67–265.00µs；upstream首次也为868.00–958.54µs，其后约25–27µs。这是首次/顺序关联，不能全归PageStore稳态维护；具体初始化器、cache和分配器各占多少尚未知。
- H1入队到出队均值11.38–12.33µs，前序job覆盖8.51–9.99µs；其余不能称内核runnable等待。所测两个gate不能替代整管线锁账：只测获取，没有全部锁、持锁或内核blocked轨迹。
- H1 current process观察扰动1.9545ms [−2.4410,2.2425]未过±0.75ms，H0亦未过，事件时间不授予原产品单价或净可删预算。本批mode0仍有36.995ms的H0慢过程，保留且不猜核类/外因；其它过程的稳定计数不能替它证明没有放大工作。

复核860项新身份、旧878＋498项、12项独立bootstrap与原矩阵通过。36过程无运行/语义/身份失败；r0唯一锚点准备拒绝、r1观察器SDK参数编译失败，以及分析器重复关键字语法拒绝均保存，修正后只分析同批原始样本。M6/M7/M8 0/3、正式校准2/20、默认关闭、两个live-copy失败与业务控制保持。B只取得部分因果链，A/C/D尚有空格、E未选定；不实施优化、不追加同类观察样本。

复现：[事前协议](EXECUTION_PROTOCOL.md)、[隔离构建](build_execution.py)、[事件接口](execution_observer.h)、[观察实现](execution_events.inc)、[固定36过程](run_execution.py)、[分析](analyze_execution.py)、[独立审计](audit_execution.py)、[机器账](execution-summary.json)、[复核](execution-audit.json)、[原始包](execution-raw.tar.xz)、[成员SHA](execution-raw-manifest.json)。r0/r1失败准备、r2派生源码/准确diff、命令、加载身份、全部原始日志/事件均归档；不含二进制，复算依赖本机冻结构建。构建与runner为一次性目录，不覆盖重跑原样本。

mode0仍有派生钩子、终态census遍历和线程边界读取，不是完全plain产品性能；其时间只作本布局的诊断基线。r0与首次分析器拒绝只保存了源码及本次工具返回，未另存原始stderr文件；r1编译失败有实际`build-3.log`，不补造日志。

下文为前批冻结结果，不与本批时间拼接。

<a id="sampled-cost-capability"></a>
## 补数A：内部时钟降至四分之一，目标联合精度仍未通过

沿[全流程账本§19.7](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#sampled-cost-capability)，本轮只替换隔离观察器TU，不改任何产品算法。最外层调用树按1/4概率抽取，后代继承抽样决定，完整计数与入选计时分开；每角色exclusive之和等于入选根时间。四侧各1能力检查＋8块镜像，共68过程，均通过语义/身份/退出断言。未发生运行或构建失败；精度失败是本次结论的一部分，样本全部保留。

K16/W16/H1实际读时钟比例24.98%；current on−off前台中位0.0792ms、pointwise95% [−0.5546,0.2889]，process中位0.0667ms、[−0.9475,0.4810]。前台虽在±0.75ms内，process未通过，按事前联合门**不给H1机制价格**。H0也未通过（process [−1.9705,0.8105]）。原八case中0/2/4/5/6通过观察粗门、1/3/7失败；控制格不代替主case，每个桶另有样本数和精度要求。

查账发现不开scope时钟也有显著慢过程：最后一块current-off index61/66的H1 CPU为14.968/34.149ms，H0为14.208/32.486ms；H1 write前台5.161/14.494ms、read2.108/4.052ms，多阶段与后台共同增大，额外drain仅0.023/0.046ms。没有剔除index66，也没有把它断言成E-core、频率或锁问题；本轮未观测这些因果维度。单纯继续缩减时钟或调样本顺序缺乏依据，92 §16.139旧执行条件限制仍适用。

同批off的H1额外process中位12.2805ms [11.4280,13.4755]，均值13.357688ms；原11.962375ms是另一个冻结批次，不能用两批之差报告产品回退。H1 on的cold1088、operation/seal各68、commit8、capture/release各140、read72次在16过程保持；可用于数量账，不能把它们乘未合格单价。合法净预算仍未知；本轮停止，不追加样本或实施候选。

复核：824项当前身份、878项旧身份、1360次随机序列/根树加法检查、12项独立字面bootstrap和原33行六列检查；原产品库SHA仍`91e962c2c43379697b13f37a2ee388d408440c67f3e21458e75c70dab4b21b38`。M6/M7/M8 0/3、正式校准2/20、默认关闭和两个live-copy失败不变。下一补执行条件/等待、资源及入口数据，完整设计仍未选定。

复现与证据：[事前协议](SAMPLED_COST_PROTOCOL.md)、[观察器](sampled_observer.cpp)、[隔离构建](build_sampled_cost.py)、[68过程编排](run_sampled_cost.py)、[分析](analyze_sampled_cost.py)、[审计](audit_sampled_cost.py)、[完整机器账](sampled-cost-summary.json)、[复核结果](sampled-cost-audit.json)、[原始包](sampled-cost-raw.tar.xz)、[成员SHA](sampled-cost-raw-manifest.json)。构建/运行目录为一次性冻结目录，复算使用`analyze_sampled_cost.py`及`audit_sampled_cost.py`，不要覆盖重跑原样本；二进制按本机冻结路径/哈希绑定，原始包保存源码、命令、原始日志与结果。

<a id="full-flow-ledger-audit"></a>
## 全流程审计：总账与有限数量闭合，完整设计尚不能选定

用户要求先得到全面真实数据再按最优设计实施。本包把原33项映射到12条完整流程，同时比较所有当前设计方向；**没有选择物理复用、读侧或另一个小机制作为下一优化**。[唯一流程账本§19](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#full-flow-ledger-audit)记录必要consumer、算法、保留/新增工作、失败/资源边界、覆盖缺口及有限补数门。实施状态仍只有原33行六列。

时间来自原`net-ledger-r1`八case、八平衡块中的32个mode0过程，逐块拆出七阶段、frame、drain前台、具名后台和边界残差，未重新采价。K16/W16/H1额外process CPU均值 **11.962375ms**，其中write **4.649351**、read **1.698595**、其余前台 **1.424722**、reclaimer **4.189938**、monitor **0.002313**、swapper **−0.002875**、未登记/边界 **0.000333**；pooler为0。均值可相加；原配对中位数11.87075ms [11.3505,12.6195]用于统计结果。旧170过程阶段数不混入本账。H1内部scope扰动失败的原裁决不变，这些阶段/线程仍不是可删除机制价格。

唯一新增运行是基线C/U/U/C四个数量过程，覆盖原八case×四manager寿命。使用已有mode3计数框架、六个隔离派生TU和一个私有头，不新增热路径时钟。所有像素/历史/销毁、实际库与同依赖检查通过；120s超时kill/reap保护，实际无超时，全部进程退出。K16/W16：Fresh/provider allocation/physical、binding、owner backing/physical、proof各1088次建立和退出；metadata与descriptor各1152次建立，含64个虚拟default；各有64条最终记录随容器销毁。物理free1092对upstream132，最后记录不等于尚有64个物理页。Pending1096只计发行，没有伪报逐ticket全寿命闭合。两次总数全一致，但H1前台退休分别96/64、后台992/1024；这种工作转移不能从线程局部改进推断净收益。

仍缺：H1合格独占机制增量、锁/ready/dispatch因果等待、所有相关实体峰值/驻留时长、其他入口及压力/失败的同义性能覆盖、合法完整替代的联合净价。CPU算术、部分对象守恒、完整机制净账是不同层次；当前只完成前两者的有限范围。安全通过不填性能空格，未知不记零。M6/M7/M8 0/3、校准2/20、默认关闭、原业务控制与两个live-copy失败保持。产品未变，无需把此前安全结果重复包装为本轮新测试。

证据与复算：

- [事前冻结协议及纠错](FLOW_AUDIT_PROTOCOL.md)、[构建/运行脚本](flow_census.py)、[独立账本审计与打包](audit_flow_ledger.py)。`python3 audit_flow_ledger.py`核验原库/源码、旧878项和新498项身份，按原始日志复算计数，并校验33项覆盖；依赖本机冻结构建产物，原始文本包不包含二进制。
- [八case逐块时间/数量/角色账](flow-ledger-audit.json)、[原始文本包](flow-ledger-raw.tar.xz)、[成员大小与SHA256](flow-ledger-raw-manifest.json)。旧完整68过程原始日志仍在[前批原始包](net-ledger-raw.tar.xz)；新包保存其结果和原协议，另包含实际进入时间重算的32个mode0原始日志、命令和运行库身份。
- 旧身份表中两项活动入口已被后续诊断更新；本次分别解析到原观察目录冻结的`NET_PROTOCOL.md/run_net_ledger.py`，验证字节哈希相同，没有跳过。所有新热路径bucket的`cpu_ns/self_ns`为0，不使用新运行的秒数给机制定价。
- r0在编译前因单行binding析构与预期锚点不同而拒绝；r1修正，顺便在metadata记录erase前读取default标记，避免观察器读取已销毁记录。失败版源码和协议保留在包中；该准备失败没有运行样本，最初工具报错未另存为日志，不伪造一份原始stderr。

原产品库SHA256仍`91e962c2c43379697b13f37a2ee388d408440c67f3e21458e75c70dab4b21b38`。下面各段为前批冻结结论；其待研究算法现在统一经过§19的完整数据与设计比较门。

<a id="completion-net-decision"></a>
## 同步退休票据：完整删除成立，收益未取得资格

原allocation私有Pending票据没有退休返回前的外部consumer。隔离原型让同步CPU provider在真实释放后返回configure已准备的Succeeded证据，保留原operation/replica身份、pin/last-use/replay、owner验证及异步接续。实际删除1088张（初报1092多算4个manager默认对象），`Tiles3Allocation`两架构56→24 B；Fresh/rows/retire/free不变。ARM64六组5233/0/0通过，包含硬满、last-use与pin拒绝后重试、stale与重放。

8块完整生命周期净节省：H1 process **−0.01550ms [−0.26500,1.02850]**；foreground −0.11095ms、other threads +0.16424ms。可加均值分别+0.064357、+0.145143、合计+0.209500ms；drain已包含。H0 process +0.47875ms [−0.02650,1.57300]，首块大变异保留。区间是pointwise95%，不能用均值或其他线程局部正值代替主判据；也没有证明零收益。预定0.75ms下界门未过，原型全部撤回，不追加样本、不升级M6。

本轮44成功过程、1失败安全过程、1构建失败。原型生产+15/−42、测试+50/−35，最终产品改动0。完整[理想路径/消费者闭包/预测纠错/净账/下一边界](LIFECYCLE_DECISION.md#synchronous-retirement-proof)、[协议与纠错](COMPLETION_PROTOCOL.md)、[数据](completion-summary.json)、[原始包](completion-raw.tar.xz)、[成员哈希](completion-raw-manifest.json)、[复核](completion-audit.json)。下一仍聚焦完整backing/binding/owner身份建立和退出，不能把本次大量小机制删除当作已命中性能榜首。

交付复核：2025项身份核验、374个未替换plain对象、33行六列原矩阵、8张可加均值账、独立字面bootstrap及plain无热路径观察器通过；376个原始成员逐项哈希核对。原产品库SHA256保持`91e962c2c43379697b13f37a2ee388d408440c67f3e21458e75c70dab4b21b38`。

<a id="lifecycle-net-decision"></a>
## 已定价替代被否决：960次命中仍净增CPU

被替换的Prepared从未进canonical root，可在接受后直接消费这一来源事实，再由原metadata检查capture/pin/last-use/activeOperation和债务。但隔离原型将其放入逐页前台执行，完整process反而增加**1.62125ms [0.838,2.793]**，前台增加**1.83310ms [1.27506,2.60490]**，其他线程仅省0.26127ms [0.16250,0.53485]。同批均值可加账是前台+1.520359、其他线程−0.504296、process+1.016063ms，含额外drain；不是将遗漏后台移出端点造成的表象。区间均为8块pointwise95%。本候选不进入产品，不追加样本。

r1 ARM64六组5233/0/0，4数量过程确认H1两次均960直接metadata删除，Fresh/retire/free仍1088/1088/1092；2故障过程在metadata真实reserve前共注入2040次bad_alloc，原collector接续和全部像素/历史/实际free通过。r0同样5233/0/0但静态发现漏catch，保留并撤出，未测净价。34个时间过程不链接scope/count/Mach线程观察器；H0零命中控制的大块变异和全部原样本保留，不能把其差异算作本项收益。

另4个current/upstream数量过程证实H1当前1092次payload请求中**1076/1042次命中原cache，miss仅16/50次**；所有payload归还进入cache。cache miss还可能由Boost pool满足，系统malloc次数未知。因此下一责任应着眼provider/binding/metadata身份建立和退出；单纯加字节cache缺少依据。条件双工作目标构造在H1还要保留undo origin，四寿命K16可从1088降至192非默认对象，即条件少896而非直接宣称960；代次、预算、压力、ABA及净价仍待证，未批准新pool。

完整[消费者/算法/代码索引/预测比对/下一边界](LIFECYCLE_DECISION.md)、[冻结协议](DETACH_PROTOCOL.md)、[净价数据](detach-summary.json)、[payload数量](payload-counts-summary.json)、[原始包](lifecycle-raw.tar.xz)、[成员哈希](lifecycle-raw-manifest.json)、[复核](lifecycle-audit.json)。本次56成功过程、1构建准备失败；产品零改动，细机制净账只对这一具体替代闭合为负，其余保持未知。M6/M7/M8 0/3、校准2/20、默认关闭和原业务/live-copy欠项不变。

<a id="mechanism-net-ledger"></a>
## 机制净账：后台来源与物理周转已落实，可回收净价仍未取得

这次共**106成功过程＋1个保留的失败capability**，产品没有改变。r1四侧on/off共68过程；r2仅后台34过程；r3两侧数量核对4过程。沿原K1/16×W1/16×H0/1、四manager寿命，全部像素、undo/redo和销毁断言通过。r0首个off capability因正常退出的pooler线程端口失效而被观察器拒绝；r1用线程退出RAII保存CPU，失败源/库/日志保留。协议见[NET_PROTOCOL](NET_PROTOCOL.md)，重算入口见[总账](analyze_net_ledger.py)、[后台](analyze_net_background.py)、[数量](analyze_net_counts.py)。

### 1. 先闭合未定位的线程差额和尾账

r1 mode0没有scope时钟，但仍有派生入口检查、线程边界读数及额外drain；**不是新的完全无插桩产品收益试验**，不能用其较旧批的点值变化宣称优化。原case端点保留，另记drain；以下均是同批8块的差额算术均值，可相加。单位ms/完整case（四寿命）。

| 当前减upstream | H0 | H1 |
|---|---:|---:|
| 前台thread CPU | 8.916868 | 7.772667 |
| PageStore reclaimer | 4.895375 | 4.189938 |
| wake/deadline monitor | 0 | 0.002313 |
| tiles3 pooler | 0 | 0 |
| tiles3 swapper | 0 | −0.002875 |
| 未登记线程＋边界读数偏移 | 0.000070 | 0.000333 |
| **完整process CPU差额** | **13.812313** | **11.962375** |

H1配对中位数：完整process额外**11.87075ms [11.3505,12.6195]**；reclaimer额外**4.21875ms [4.035,4.278]**；前台额外7.65266ms [7.31723,8.34131]。均为pointwise95% bootstrap，非联合门。reclaimer约占H1均值差额35.0%；旧“其他线程4.610ms未知”在这批同义工作下已找到执行者，不能继续写成无归属管理成本，也不能把旧4.610和新4.190混加。

drain尾相对upstream均值H0 **0.02175ms process / 0.00172ms foreground**，H1 **0.02225 / 0.00145ms**。H1原case process差额11.94019ms，增广窗口11.96238ms，故数毫秒差额主要发生在原case内，不是遗漏到case之后。drain只排即时任务，仍不证明未来deadline或一般资源压力下全部物理债务已结束。线程CPU读取有微秒量化及端点位移，显式残差保留；CPU不能解释锁等待时间。

### 2. 物理对象从生成到释放的数量账闭合

r3完全关闭scope时钟，直接计成功Fresh、`createTileDataFromRows`、provider `retire`及两侧`freeTileData`。以下每项两个独立过程重复一致；H0/H1相同。`duplicateTileData`是副本请求次数，不默认等于malloc或preclone miss。

| K / W（每case四寿命） | PageStore成功Fresh＝rows创建＝provider retire | upstream副本请求 | PageStore / upstream实际free | 额外free |
|---|---:|---:|---:|---:|
| 1 / 1 | 8 | 8 | 12 / 12 | 0 |
| 1 / 16 | 68 | 8 | 72 / 12 | 60 |
| 16 / 1 | 128 | 128 | 132 / 132 | 0 |
| 16 / 16 | **1088** | **128** | **1092 / 132** | **960** |

每侧另有4个默认tile，均已释放。当前满足`rows+alloc=free`、`Fresh=provider retire=rows`；upstream满足`duplicate请求+alloc=free`。因此上轮1088 cold现在有了真实物理consumer的闭包，**额外960次对象释放是实测差额，不再只是cold调用数猜测**。有限矩阵符合`当前Fresh=4K(W+1)`、`upstream副本请求=8K`、`额外free=4K(W−1)`；不由两个规模点外推所有负载复杂度。

原8case的事后探索对比进一步区分固定成本与重复周期：固定K16/H1，W16比W1多出的“current−upstream”process差额均值**10.01444ms**（中位9.7475，[9.4635,10.7875]），其中前台6.35010ms、其他线程3.66434ms。它占W16完整额外成本均值83.7%。这是**15次额外write＋read周期的联合成本**，包括读保护、版本/发布及回收；不能除以960当Fresh单价，也不证明只删除Fresh便能兑现10ms。H0同一对比为11.91319ms。结果见[数量及探索对比](net-counts-summary.json)。

### 3. 后台内部线索已获得，但精度门不允许把它们变成净预算

r1 H0前台粗门通过；H1 foreground on−off0.591ms [0.112,1.987]、process0.838ms [−0.007,2.735]失败。r2去掉所有前台scope时钟后，H1 foreground−0.172ms [−0.811,0.337]、process−0.096ms [−1.105,0.832]仍未完全落在事前±0.75ms内；H0 process上界0.910ms也失败。**不追加样本、不删离群点、不放宽门**。r1/r2线程off总账可用；内部定价本轮停止。

仅作描述，r2 H1观察worker的互斥均值账为：retirement job **1.874ms**、history pass **1.736ms**、metadata prepared publication释放 **0.425ms**、history job其余0.134ms、Store最终cleanup0.132ms、tree释放0.033ms、retirement process0.017ms、worker未包scope部分0.218ms，合计4.568ms。这不是upstream增量的逐项因果分配，也没有±0.75ms资格。r1 H1为76次metadata cleanup task、8次tree task、4次Store终结，history/retirement任务数随调度变化；不能给每次job套平均单价。普通read last-use task未出现在本用例的worker记录中，不能推广为一般read清理免费。

### 4. 当前判断与下一责任

**目前最强解释是逐次写入生成新页面生命周期，前台准备与后台回收共同放大；不是单个小函数，也不能概括为相同工作量下的普通锁开销。** 证据强度分别为：额外960次free及Fresh/retire闭合——有限fixture内直接重复验证；约4.2ms的worker归属——无scope时钟的同批95%区间；后台内部份额——观察线索、精度未过；合法净删量及毫秒收益——未知。

理想设计仍从三个不同旧值消费者出发：undo起点、上一成功operation的失败恢复点、exact reader/alias/last-use的冻结版本。upstream的低周转是同义公开操作下的算法参照，不能直接证明其具备当前全部新增失败/并发保证，也不能证明这些保证必须用当前Fresh协议实现。额外960不等于可合法删960；“保留undo即可原地覆盖上一成功值”仍不成立，K16不能绕过M7有界首字节合同。

原T03.1/T04.2/T07.2下一包应联合审查：`prepareTarget → seal/overlay接受 → historySlice/可达性 → discardHistory → removeDescriptor → retirement record → provider retire → owner/budget释放`。先确定哪些代际有真实消费者、每个消费者的最后使用事件及可构造的恢复替代，再计算`少发生的完整生命周期成本 − 新增证明/保活/恢复/尾账`。若代际不能删，则另审同步CPU退休的prepare/bind/verify/release是否重复表达同一已终结事实，保持异步、失败、last-use和债务接续。**不要只按两个最大观察桶直接重写collector/queue，也不恢复已被反例否决的H0“无history就可直接free”捷径。**

三本账的状态明确分开：①线程/总差额已闭合到显式微小边界残差；②物理生命周期数量已闭合；③同义替代的细机制增量与合法可回收净预算未闭合，故本轮不实施产品优化、不声称找到已定价收益榜首。原33项更新，M6、业务控制和live-copy欠项保持。完整[总账JSON](net-ledger-summary.json)、[后台JSON](net-background-summary.json)、[原始源/命令/失败/输出](net-ledger-raw.tar.xz)、[成员哈希](net-ledger-raw-manifest.json)、[独立复核](net-ledger-audit.json)。

交付复核通过：106成功过程、1保留失败capability、5065项身份校验、516个原始包成员、原33项/六列结构、16张加法账及4个独立字面bootstrap区间。脚本语法和`git diff --check`通过；原产品库SHA256仍为`91e962c2c43379697b13f37a2ee388d408440c67f3e21458e75c70dab4b21b38`。10466安全测试本轮未重跑，不新增安全或性能阶段资格。

<a id="current-cost-ledger"></a>
## 当前成本账：阶段差额闭合，逐页周转优先于小额终结清理

当前11c689 / 重构前8198 / upstream9a24，ARM64，存储与业务各51过程；当前两个观察诊断各34过程，共**170过程**。产品代码/测试改动0，实际库与上一轮最终安全库相同。当前ABI夹具及取消共有clear融合的business控制重编；像素、8段/4callback/19 projection、存储8case、undo/redo/销毁、退出及运行库核验全部通过。每块内各侧先取均值，8块为独立单位；100000次固定seed bootstrap，以下为配对中位数及pointwise95%，不授联合正式门。

### 整轮净价与当前upstream分母

| 完整端点 | 当前较8198节省ms [95%] | 节省% [95%] | 当前较upstream额外ms [95%] |
|---|---:|---:|---:|
| K16/W16/H1完整前台CPU | **2.175 [1.228,2.468]** | **17.08 [11.48,19.88]** | **8.330 [7.659,9.399]** |
| K16/W16/H1完整case进程CPU | 3.318 [1.773,3.649] | 见完整结果 | 12.803 [11.956,14.324] |
| K16/W16/H0完整前台CPU | 1.120 [0.463,1.717] | 9.70 [4.37,15.13] | 9.058 [8.400,9.358] |
| 业务Stroke CPU | **0.609 [0.373,1.219]** | **3.77 [2.32,7.17]** | **6.992 [6.764,7.102]** |

这说明整轮存储收益已经超过1ms，且当前Stroke相对整轮起点有正收益；不把16a4的0.723ms回退改写成不存在，也不将不同版本点估计相减来分配修复贡献。没有整轮事前总时间点预测，仍不能宣称预测模型已经验证。业务Undo/Redo及teardown等2%控制未全闭；teardown节省−0.017ms [−0.028,+0.002]。业务整进程节省−1.103ms [−10.190,+7.781]，不能宣称全生命周期非劣。旧Setup反面结果保留其冻结身份，本批Setup也未建立严格非劣性。

### 可相加的阶段总账

下表是**8块差额的算术均值**，不是上表中位数；单位均ms/完整case（四个manager寿命）。前台七阶段加外框残差，逐块与完整case前台CPU严格相等。残差是计时窗口外的真实工作及测量边界，不命名为某个机制。

| 当前−upstream前台成本 | H0 | H1 |
|---|---:|---:|
| setup | 0.672 | 0.937 |
| write | **6.318** | **4.936** |
| read | **1.830** | **1.951** |
| finish | −0.013 | 0.181 |
| undo | 0 | 0.161 |
| redo | 0 | 0.120 |
| teardown | 0.110 | 0.165 |
| case外框残差 | 0.050 | 0.064 |
| **前台合计** | **8.967** | **8.517** |
| 同期其他线程CPU差额 | 5.100 | 4.610 |
| **完整case进程CPU差额** | **14.068** | **13.126** |

H1 write+read占额外前台CPU均值的**80.9%**，H0为90.9%。这是可靠的阶段优先级，不是可删除比例。其他线程4.610/5.100ms仍未归到具体worker/退休任务，不能直接称为正常管理成本或等待。read窗口进程CPU包含后台执行，不能全部算给read函数。共17张账（8case×前台/进程＋业务整进程）、两种对照、逐块加和误差均小于1e−9ms；这证明算术闭合，不证明机制归因闭合。

业务同批均值账中Stroke多6.950ms，但公共Setup少11.425ms、进程外框少3.752ms，因此整进程差额均值−6.705ms；该均值与整进程中位数/宽区间也不矛盾。**共有启动工作不能抵扣PageStore本身的读写差额。** 原始块值全部保留，不能由整进程偶然更快宣布存储成本已抵消。

### 独立发布新增工作的价格边界

保留上一冻结前后数量：同32个投影producer，由父11–14个事务变为32个，总commit12–15→33。旧匿名cohort在失败下会撤销已返回成功的兄弟操作，不能恢复它作为合法优化。当前17个mode2过程（含capability）均33次非空成功commit、188 proof、4 removal；原commit循环实际**34–35次尝试**，root/directory/descriptor重准备均0，metadata预检重准备1–2次。实际多出的尝试也可能发生于install拒绝，因此预检计数不冒充全部重试原因。

| 当前业务直接责任 | 观察CPU中位数ms [95%] | 保留边界 |
|---|---:|---|
| owned seal中间处理32次 | 0.149 [0.143,0.153] | 包含必要adapter/清理，不是可全删overlay预算 |
| borrowed seal中间处理27次 | 0.144 [0.142,0.166] | history有真实overlay消费者 |
| 完整canonical commit33次 | **1.038 [0.963,1.062]** | 含必要验证、root、同步回收入口；后台后果和其他caller中的等待未全覆盖 |

observer on−off为0.044ms [−0.358,+0.418]，通过本次事前用于判断数毫秒责任规模的±0.75ms粗精度，**没有通过或替代旧±0.2ms小额预算门**。不能把on/off整体区间当单scope严格误差上界。当前证据不支持把约7ms业务差额主要认领给这两个直接段，也不排除独立发布在其外诱发的保留、回收、竞争成本。没有将1.038/33当额外18–21次的实际单价：当前全部commit价、相对父新增价、合法净可删价是三种不同问题。

### 写入/读取分解与失败保留

同当前库增加9个粗scope，按线程树核验`inclusive=self+children`，只相加exclusive；所有scope在前台，case外未归属部分显式保留。H0完整前台on−off为0.176ms [−0.086,+0.504]，通过预定±0.75ms粗精度；write为0.193 [0.037,0.470]，read为−0.034 [−0.095,+0.039]。H1完整前台为**0.737ms [0.367,1.812]**，write为0.553 [0.380,1.010]，未通过，**H1的细分时间不给选项净预算资格**。block6较大扰动完整保留，无删样或扩样。

H0完整case的当前观察责任中位数：cold prepareTarget **3.297ms [3.198,3.335]**，commit **1.825ms [1.770,1.875]**，read exclusive（不含其capture/归还子scope）**1.748ms [1.696,1.787]**。其余各scope及未归属前台1.274ms见完整结果。它们包括setup/最终退出的实际命中，不能直接除以仅write阶段差额；中位数桶也不能相加闭合。独占均值账在JSON内另行守恒。H1观察值只作带扰动原始资料，不用于榜首或收益承诺。

数量则两种模式都稳定：**1088 cold准备、68 operation、68 seal/intermediate**；H0 **68 commit**，H1 **8 commit**。1088=`4寿命×(16 setup页+16次写×16页)`，H1显式history减少canonical频率，但没有减少这批逐页冷准备。H0 capture/release各132次，H1各140次；读回和packed write比较都有真实capture，不能只算其中一边。cold次数不自动等于Fresh allocation或before memcpy数量，本批未补测这两个物理分母。

据此，下一有界主线回到**T03.1/T04/T07的逐页目标准备→私有完成→保留/退休管线**，读侧T06.1/原readPage并列为第二责任。先区分同一次cold内可合并的证明/预算/descriptor工作与跨操作必需的新版本，再判断减少每次费用还是减少周转次数；H0短暂Historical删除仍是竞争候选，不再仅凭空节点数优先。T02.4直接canonical中间表示不具备多毫秒直接预算证据。

理想跨操作复用必须证明：旧值已无实际exact读者/alias/last-use，当前调用失败可恢复上一成功状态，所有可能拒绝的准备先完成，并保持整次多页操作及资源上限。一次短暂读回结束不等于仍有永久冻结，也不自动授予原地改写权限；K16不能通过擅拆为两个8页不可回滚段绕过M7边界。原先“可少960次周转”的数量只能保留为满足这些条件后的候选，不是当前已授权删量或时间预测。本轮没有据未通过H1定价启动新产品重构。

原33项新增成本列，明确必要保留、真实删除、保证增量及合并计价关系；T02.3/T04.4的同一导出删除、T04.8/T04.10的同一history投影等不得重复领取。**总阶段账已补齐；机制额外成本、合法可回收成本和其他线程归因仍有明确缺口。**

[事前协议](PROTOCOL.md)、[存储三方](cost-ledger-storage-summary.json)、[业务三方](cost-ledger-business-summary.json)、[互斥总账](cost-ledger-reconciliation.json)、[发布数量/时间](cost-ledger-terminal-summary.json)、[存储粗责任/扰动](cost-ledger-storage-work-summary.json)、[完整身份与复核](cost-ledger-audit.json)、[全部原始尝试](cost-ledger-raw.tar.xz)/[成员校验](cost-ledger-raw-manifest.json)。1582项身份、632原始成员、4个主端点字面bootstrap复核；两次r0构建器锚点拒绝发生在编译/采样前，r1修正后完整运行。可复现入口为[run_cost_ledger.py](run_cost_ledger.py)、[reconcile_cost_ledger.py](reconcile_cost_ledger.py)、[audit_cost_ledger.py](audit_cost_ledger.py)。没有新正式M6、GPU或所有控制非劣资格。

<a id="read-terminal-deletion"></a>
## T07读终结删除闭包：接受后移交，拒绝留在原责任

产品提交`11c6895ddf`，父`6f76902d4a`。生产**+71/−127（净−56）**，测试+112/−5，人工ownership清单+3/−2，派生inventory/callgraph +8038/−7695；不把派生行数当复杂度收益。

本轮按[事前协议](READ_TERMINAL_PROTOCOL.md)复审6f769后的完整读终结责任。发现的问题不是少一个helper，而是GC已经接受通知后，读记录仍重复维护“等待GC结束”的恢复阶段。目标顺序为：`metadata解除保护 → 原collector接受通知 → 原活动容器提取记录 → GC/退休继续处理 → 原cleanup在锁外销毁`。真实last-use尚未完成时仍由原read记录保留，不能提前提取。

先在未改生产代码的父库上反测：`orphanRetirementFootprintRefusal`报告2 passed/1 failed，异常确实逃出`retainRetirementDebtReservation`；反例保留原reservation/record，完成物理清理后才报告失败。修复在原ledger准入边界把footprint分配异常表达为拒绝，初次handoff和queued retry共用，未新建恢复队列。此为外部虚拟接口的异常注入；当前tiles3 footprint查询不分配，不能冒称实际tiles3 OOM或已经实测队列泄漏。

| 原位置与全部调用闭包 | 最终责任与删除 | 必须保留的保证 |
|---|---|---|
| ReadCoordinator `cancelLocked/retryCancelledRequestsLocked/cancelPreparedRequestsLocked` | 保护解除成功后原map node直接交cleanup；删Released/Collecting及pump后的重新查找/异常恢复 | Resolving排斥、metadata真实拒绝和原cancel队列；cleanup活动覆盖物理销毁 |
| `releaseLocked/finishReleasedReadLocked/acknowledgeRecordLocked`及worker、手工ack、completed、retry、cancelClose | 原`finishReadLocked`先提取node再解锁pump；删historyPending/historyProcessing、m_pendingHistoryReads及六处阶段分派 | last-use ticket、metadataReleased、原release重试/通知；共享ticket不重复ack，晚通知见原map缺项后结束 |
| `finishCapturedReleaseLocked/retryCapturedReleasesLocked/releaseCapturedView` | 已接受版本只推进原next；snapshot接受后提取原记录；删versionReleased/snapshotReleased/historyPending及对应异常树 | next/retained、逐版本解锁的processing排斥、snapshot真实拒绝及原retry/lifetime；不删root最后保护判断 |
| OwnerLedger `retainRetirementDebtReservation` → RetirementQueue初次交接/retireRecord/worker/process/close | footprint观察拒绝返回false；原reservation/paid record继续接续 | 不重复已接受provider operation；budget/debt、物理pin、readiness与原延迟重试都保留 |

删除共5个布尔字段、1个计数器、2个枚举阶段及3处读侧异常恢复树，没有新增持久状态或owner。bool减少不直接换算对象字节，padding未定价。captured release与last-use释放实际使用不分配的metadata摘链；collector在原work/rescan内接收分配/债务拒绝，retirement原记录保留未接受尝试或已接受operation。正是这些已有接受保证允许删除上层阶段；不是用catch删掉来宣称失败消失。

定向31/0/0通过，包含真实MetadataArena硬满下初次footprint拒绝、同node显式重试、无新输入自动清零、cancel/release/last-use三条真实退休回调重入，以及captured暂停/恢复。最终ARM64/x86_64六组各5233/0/0，总**10466/0/0**；结构门21 manifest/26 owner/16 census、87 TU/2253 API/30668边/26 callback及6工具测试通过。903项身份校验、86个原始包成员核验，双架冻结runtime/test diff与最终提交一致；结构派生物随后生成，未改已测运行源码。首版测试链接到未导出的手工ack失败，已改为已有completed入口，未增加导出API；原构建日志保留。

[完整结果与身份](read-terminal-summary.json)、[全部源码/运行/构建失败](read-terminal-raw.tar.xz)、[成员校验](read-terminal-raw-manifest.json)、[复核脚本](audit_read_terminal.py)。该读终结责任完成，原33项继续承载更大的管线范围。

该责任属于健全性和净简化，不虚领1088次物理退休、像素复制或全部GC成本；本轮没有新性能时间结论。T02.4净预算、H0/Setup原反面结果、全包当前/upstream、两个live-copy exact-view失败和M6/M7/M8仍开放。

<a id="setup-h0-attribution"></a>
## 反面结果归因：Setup未执行新增通知，H0没有新增回收工作

产品保持6f76902d4a，生产/测试改动0。按独立[诊断协议](SETUP_H0_PROTOCOL.md)运行12个ARM64观察过程：business四个，storage的case3/H0与case7/H1各四个，均parent/current/current/parent。全部同义结果、退出、真实库及共享依赖通过；525项身份和79个原始包成员核验。没有追加上一批68过程、没有新置信区间、没有改变原回退或门禁裁决。

Setup进一步覆盖了两个metadata保护入口；四过程24项计数全部为0，包括applyReadProtection/applyCapturedProtection。粗分段中，image创建占**89.36–92.15%**：父341.649/338.613ms，当前352.316/339.935ms；resource manager为父40.068/28.581ms、当前29.567/28.643ms；configure/wait及blank projection各小于0.323ms。此处的image创建包含`KoColorSpaceRegistry::rgb8`、KisImage构造、五个paint layer及节点安装，不是已细分到颜色引擎的独占成本。不能从两个重复估计新回退量。

所以，新通知的三个实际保护释放入口没有在Setup直接付费。共有初始化占主导，优化它必须同样作用于upstream，不能用作PageStore基础性能证据。二进制布局/同头重编、通用transition result构造及环境波动仍未定价；“没有新增GC调用”不等于严格证明整个产品改动不影响Setup。原Setup/整进程回退信号仍开放。

| 完整case内实际工作（4寿命） | H0父/当前，每侧两次 | H1父，两次 | H1当前，两次 |
|---|---:|---:|---:|
| epoch退出 | 均68 | 均16 | 均16 |
| requestKey | 均1088 | 均3328 | 均1344 |
| 新work | 均1088 | 3072、3056 | 均1088 |
| history slice查询 | 均1088 | 3264、3248 | 均1280 |
| 实际历史版本扫描 | 均1088 | 均1280 | 均1280 |
| 保护root访问 | 均0 | 均320 | 均320 |
| 历史版本移除 | 均1088 | 均1088 | 均1088 |
| worker pass / schedule | 均68/68 | 212/212、211/211 | 88/88、87/88 |
| captured版本释放 | 均0 | 均1984 | 均1984 |

H0两侧全部24项观察计数相等，两个metadata保护入口也都是0。因此当前数据不支持“通知前移造成H0多分配、重扫、重复或唤醒”的解释。H1直接定位到1984次没有历史的captured归还；实际净删节点1968–1984，非空扫描/可达性检查/移除均保持，不能把1984跳过次数机械当净删量。少一个worker尚可能跨出末尾dump；计数按执行阶段，未声称完整物理drain或通知发起阶段。全部计数不用于单价。

### 原T07/T08的下一责任边界

1. **H0旧版本的短暂历史阶段值得判别，尚未准入实施。** 1088=`4寿命×(初始化+16次写)×16页`，不是1984空通知的余项；它们是真正旧版本，物理退休仍必要。当前Publication `commitOwnedLocked`登记D，Metadata `preparePublication/installPrepared`把旧Published变Historical，再经work/当前root解析/历史丢弃交RetirementQueue。理想候选是在接受点已有“没有其他逻辑保护”的证明、逐版本保护及退休能力均成立时，由原发布候选向原退休记录交接，省掉不必要的历史索引/任务/再判定；不能删除1088次实际物理回收或复制，也不是M7原地写入。
2. **不要把后来的0 root访问倒推为安装时无保护。** `installCommit`持epoch mutex调用metadata安装，不能在metadata callback里再查询epoch；prepare后的unlock允许新capture。任何可用证明必须来自原epoch接受点并覆盖active sibling transaction、旧retained root、captured版本、read/last-use及当前incarnation。metadata现有准备明确要求`step.effects.empty()`；直接改枚举不是实现。需要先给出原metadata/ledger/debt准备、晚保护出现、可选准备失败回原Historical路径、无分配install和唯一释放责任的完整设计与净预算，禁止另建退休队列或第二保护表。下一成本判别须同分母比较cold/commit/history/physical责任，不能按1088次数授榜首。
3. **诊断时提出的读终结删除闭包已由11c6895ddf完成。** 当时源码发现footprint查询位于provider->retire的bad_alloc捕获范围外，因此不能直接删除上层重试。后续父库反例验证准入异常逃逸，并在原ledger修复；读记录在解锁前移交原cleanup，普通/captured/last-use阶段与所有caller一并收敛。详细失败范围、保留责任与验证见[读终结交付](#read-terminal-deletion)，不再将这些旧阶段列为下一待办。

[诊断全结果](setup-h0-summary.json)、[全部源/命令/输出](setup-h0-raw.tar.xz)、[成员校验](setup-h0-raw-manifest.json)。原33项继续承载T07.2/T07.3/T08.2；同义存储局部收益保留，整体M6与live-copy语义缺口未关闭。

<a id="history-release-event-delivery"></a>
## T07健全性复审：从保护释放事实直接交接回收责任

产品提交`6f76902d4a`，父cb942b6eff。ARM64/x86_64六组各**5227/0/0**，总**10454/0/0**；结构门21 manifest/26 owner/16 census、87 TU/2253 API/30630边/26 callback及6工具测试通过。生产**+27/−22**，测试**+43/−7**，派生inventory/callgraph **+7480/−7325**。无新增持久字段、owner或队列；唯一新增值是短寿命metadata结果中的通知bit。collector原requestKey为手工Historical测试导出，未新增方法或第二状态权威。

### 为什么原备选不够健全

“缺work意味着无历史”不成立：虚拟/物理历史默认页、captured Prepared的abort/cancel会产生Historical而不预先登记work。commit接受后的cleanup解锁还早于D登记；restore实际上在解锁前登记。强制read只唤醒已有work会漏首次通知，补齐每个生产者又会复制维护协议。

另一备选是缺work时再查historyCount。r1 ARM安全组通过，但复核92 §16.163已否决的getter候选后，在任何计数/性能样本前撤回；新增锁/查询的费用没有消失。r2改为消费释放操作本来就知道的事实：metadata持shard锁移除保护后，若该页存在历史，返回historyNeedsRevisit；ReadCoordinator仍持原Store gate，把通知交给原requestKey。回收仍须重新证明完整可达性与物理保护，通知不是退休权限。

| 实际入口与寿命 | 最终表达 | 被替代/保留 |
|---|---|---|
| ReleaseRead无last-use | 原接受结果携带历史事实，当场交接key | 删除稍后无条件key通知；释放尚未接受时flag为false |
| ReleaseRead有last-use / AcknowledgeLastUse | 等真实ack移除保护后交接；一票清除多lease时其余record只完成自身收尾 | 不提前发任务，不为已由首个ack清完的同票重复入队；原订阅/晚ack/close保留 |
| ReleaseCapturedVersion | 在同一Store gate内从metadata接受交给collector，随后原versionReleased记录承担清理接续 | 历史默认及captured abort即使从未有work也能登记；重试不二次释放token |
| Collector / Store / Publication全部caller | collectUnreachable只泵已有工作或扫描原H；首次key由原接受点登记 | 删除candidateKeys/count、候选循环、临时getter和分散重新查历史；测试六处手工Historical改显式登记再pump |
| 真实登记拒绝 | requestKey的noexcept接受点保留m_rescanRequested，由原任务恢复全N登记 | 不删除bad_alloc恢复、真实历史repeat、债务/退休队列、物理清理和close；这些仍有实际消费者 |

这次调整的是通知发生的位置，没有扩大metadata锁域，没有从shard内调用collector，也没有新增查找、getter、缓存或回收框架。晚产生的历史仍由原发布D或后续保护释放通知，不能把一次false当永久无历史。原read清理记录仍保留自己的metadata/物理终结事实；其跨入口接续不被一个GC通知bit取代。

### 反测、机制与净价

父版本两个真实读终结反例均失败：无历史的pending cancel/resolved release，在硬满MetadataArena时仍触发无用回收准入背压（resolved行0→2）。r2两行通过，原真实非空history存储拒绝、无新输入恢复、default/captured abort、重验和close矩阵继续通过。r1 getter安全通过不计入r2总数。观察构建r0因旧脚本保留16a4方法名而在派生阶段失败，未运行样本；r1修正后按ninja依赖重建父9个受metadata/collector头影响的TU，当前只对原collector/read插固定计数，无逐事件clock。

4观察过程按parent/current/current/parent全部通过。Stroke退出均33次；新work父698、804→当前208、212；slice查询754、873→272、270；worker pass80、90→48、48。全阶段实际历史移除均324，必要回收没有通过少做工作来取快值。数量属于观察运行，不作概率区间，也不等于物理释放数量。该业务观察未命中generic ReleaseRead/last-use的新增通知；主要是captured保护归还时页上已无history。captured释放计数父636、当前692并不相等，所以不把skip数等同前后净删数，也不声称整个内部执行图固定；真实像素、8段/4callback/19 projection、undo/redo与销毁端点相同。

随后68个未插桩过程：storage/business分别2能力＋8块×4，块内ABBA/BAAB，8块为独立单位。两侧同一fixture binary、同一未融合merger与共享依赖；父用完整cb942冻结库，候选是已安全验证的当前对象重链接。下表为配对中位数和pointwise95%区间，正数为节省。

| 端点 | 净省CPU ms [95%区间] | 净省% [95%区间] | 裁决 |
|---|---|---|---|
| 存储K16/W16/H1 write前台 | 0.5105 [0.4136,0.6148] | 8.966 [7.283,10.738] | 局部改善确认 |
| 同case完整前台 | **0.9030 [0.5328,1.0214]** | **8.429 [4.643,9.905]** | 同义存储增量成立 |
| 同case完整process | 1.650 [1.0125,1.8945] | 10.394 [6.094,12.109] | 此case未被后台抵消 |
| 存储K16/W16/H0完整前台 | −0.2454 [−0.3635,+0.1535] | −2.420 [−3.636,+1.480] | 未排除2%回退 |
| 业务Stroke | **0.6295 [0.1720,0.9550]** | **3.887 [1.073,5.694]** | 正收益成立，绝对下界未达到0.2ms排序参考 |
| Undo | 0.0083 [−0.0130,+0.0340] | 1.570 [−2.416,+5.812] | 2%非劣未证 |
| Redo | 0.0345 [−0.0040,+0.0655] | 4.019 [−0.466,+7.376] | 本pointwise控制排除2%回退，不授联合资格 |
| Teardown | −0.0093 [−0.0400,+0.0035] | −1.408 [−5.993,+0.503] | 2%非劣未证 |
| 业务Setup | −2.7845 [−12.0315,−0.3385] | −0.747 [−3.221,−0.090] | 出现回退信号，来源未归因 |
| 业务整进程 | −1.5063 [−11.3910,−0.4035] | −0.317 [−2.400,−0.085] | 出现回退信号，不能宣称整体变快 |

Stroke wall净省0.0878ms [−0.0725,+0.3595]，未确认改善。Setup是业务fixture初始化全责任，不自动算作PageStore管理成本；也不能忽略它或把它解释成后台抵消。所有慢值保留，不加样到通过。没有新upstream过程，不把与cb942的收益当作最终upstream比值，也不与上一批0.401ms直接相加。

**裁决：保留事件传递实现，局部必要工作/删量/净收益成立；整体门禁、精确预测和榜首判断仍未完成。** 事前只有结构数量条件而无毫秒点预测，本次不能反称预测准确。下一优先核对本批H0和Setup回退的责任及同一公共管线成本，而非继续细削已降到208–212节点的GC；当前/相对upstream/可回收成本排名仍须分开。live-copy语义选择及两条exact-view失败独立保留。

[完整价格](history-admission-price-summary.json)、[实际计数](history-admission-work-summary.json)、[1697身份/10端点字面bootstrap及删除核验](history-admission-audit.json)、[全部源码/构建/失败/原始样本](history-admission-raw.tar.xz)、[成员校验](history-admission-raw-manifest.json)。构建与采样脚本为build/run/analyze/audit_history_admission系列，派生脚本转换及差异也收入原包。最终提交差异必须与采样前source.diff逐字节一致；ARM测试早于仅派生图更新，运行时代码与两架实际库一致。

<a id="epoch-exit-net-price"></a>
## T07实际效果：过大的回收范围确实付出了业务成本

本轮产品/产品测试改动均为0，沿用cb942b6eff双架10450/0/0的安全身份。与父16a4各自冻结库比较，双方采用同一未融合merger；存储不调用该层，业务上层工作没有减少。ARM64两矩阵各2个capability＋8块×4进程，合计**68个成功过程**；实际库/共享依赖、源码、全部像素及退出身份核验，未插桩。每块两次先取均值，8块是统计单位，下表均为配对中位数和pointwise95%区间，正值为节省。

| 端点 | 较16a4净省ms，95%区间 | 净省%，95%区间 | 裁决 |
|---|---:|---:|---|
| 业务Stroke CPU | **0.401 [0.2405,0.7145]** | **2.420 [1.426,4.169]** | 局部正收益成立；绝对下界超过事前0.2ms排序参考 |
| 业务Stroke wall | 0.1403 [0.0065,0.3065] | 1.918 [0.088,4.170] | 此端点改善，不归因某种锁等待 |
| 存储K16/W16/H1 write前台CPU | 0.1640 [−0.2504,1.7857] | 2.949 [−4.526,24.553] | 未确认改善，也未排除2%回退 |
| 存储K16/W16/H1完整前台CPU | 0.3246 [−0.4234,3.0078] | 3.297 [−3.841,23.272] | 基础端点资格仍不足 |
| 同case完整process CPU | 0.530 [−0.678,3.6085] | 3.587 [−4.248,19.376] | 不能认定后台抵消或尾已收口 |
| 存储K16/W16/H0完整前台CPU | 0.0983 [−0.9166,0.7582] | 0.960 [−9.371,6.973] | 不确定 |
| 业务Teardown CPU | −0.0188 [−0.0300,0.0175] | −2.733 [−4.566,2.616] | 未排除2%回退 |
| 业务整个进程CPU | 1.7678 [−6.780,9.143] | 0.365 [−1.437,1.935] | 未确认整进程正收益 |

Undo/Redo CPU分别净省−0.01175ms [−0.045,0.064]、−0.01725ms [−0.0555,0.0385]，两者均未排除2%回退。Setup和完整进程受初始化等成本影响，不能将其归给PageStore。所有8个存储case/互斥阶段和业务阶段保留在summary，不删波动样本、没有追加到通过。**基础性能仍须由同义存储和当前/upstream比较证明；业务局部正结果不能代替它。** 原0.723ms回退与本批0.401ms不是同一组配对样本，不能称已严格对账55%或剩余恰为0.322ms。

身份边界补记：本批事前绑定主fixture、二进制、产品HEAD/库和链接对象；两个沿用的业务fixture头`matched_freehand_baseline.h/stage_probe.h`在审计时补核对，与16a4既有冻结hash一致。audit单列此次事后核验，不回写成采样前已单列冻结的输入。

### 同一改动的实际工作删量

净价结束后用最终r2的4个count-only过程parent/current/current/parent复核。父按ninja真实依赖清单，将引用collector头的全部6个生产TU（Store/Epoch/Write/Collector/Read/Publication）按16a4源码和声明重建，其他未变源码对象与当前一致；两侧计数点相同，无逐事件clock。四过程均满足8段/4callback/19 projection、原像素/undo/redo/销毁合同。后台合并受调度影响，两个重复不构成概率区间；阶段指实际执行时段，包含stage0，不等同于工作发起者。

| Stroke实际责任 | 父16a4，两次 | 当前cb942，两次 | 解释 |
|---|---:|---:|---|
| epoch提交/退出收尾 | 33、33 | 33、33 | 未少做独立发布责任 |
| 请求旧base历史重扫 | 20、19 | 9、8 | 新条件只在最后保护消失时成立；不等于实际worker次数 |
| 全metadata扫描pass/key | 20/648、18/580 | 0/0、0/0 | 直接删除无关页的全表登记来源 |
| 已知H重排pass/key | 0/0、0/0 | 9/90、8/82 | 新增替代工作照常付费，不能只报删除N |
| 请求key | 1496、1484 | 994、986 | 包括原D、读者释放和历史失效，不能全删 |
| 新建work节点 | 1200、1230 | 706、818 | 不必要访问会继续放大为分配、登记和销毁 |
| historySlice查询 | 1298、1314 | 801、871 | 不以此差值推定每次查询的净时间 |
| 已启动后台pass | 111、114 | 85、90 | 原预算不变，实际排程量下降 |
| 所有阶段移除的历史版本 | 324、324 | 324、324 | 没有通过少做历史移除获得上述收益；这不是物理free计数 |

这组结果把此前“正常管理费用”的一部分具体化为**过大的维护范围产生无关key，再放大为work节点、worker和扫描**。当前补齐前台漏回收、收窄最后保护条件、N→H替代是同一包，净0.401ms不能按上表计数比例分摊给某一个hunk；但整包实际收益与机制删量方向一致，不再只是静态判断。

### 下一责任与预测边界

优先继续原T07的work准入：当前仍新建706–818个节点，而历史查询和实际版本访问不是同一件事。先查节点是否在没有历史可回收时就被创建，不能把这些节点全当冗余或宣布它们是剩余CPU榜首。完整consumer是Publication的superseded proof/commit descriptor/restore目标，以及ReadCoordinator的cancel、history-read终结和captured-version释放；共同点是`HistoryCollector::requestKeyLocked`，metadata的原page.historyCount是权威事实。

继续源码审核已排除直接给`requestKeyLocked`加metadata getter的做法：缺key恢复经`visitPageKeys`在configuration和shard锁内回调，`historySlice`会再锁同一非递归shard，构成重入死锁。普通caller只有Store gate；方法名相同不代表锁上下文相同。

更直接的候选是按事件区分责任：发布/superseded proof可以产生新历史，由原`requestKeyLocked`登记；Read的cancel、history-read终结和captured-version释放只降低保护，尝试只重排已有H；缺key分配失败仍由原rescan记录在锁内恢复登记。生产代码给`collectUnreachableLocked`传非空key的恰是这三个读者出口，其他生产caller只pump或请求全H；测试还有直接初始化Historical数据/制造工作容量拒绝的用法，不能将它们混为普通读释放或删除反测。

这还不是已成立的产品方案：须证明每个历史产生点和初始注册都已承担登记，尤其commit/restore接受后先解锁做adapter/cleanup、稍后才登记D的窗口。此时“m_work中没有key”不能直接等同于“metadata没有history”；缺失责任可能仍在正在结束的发布者或rescan中。需要验证读者先退出、发布者随后登记、真实登记失败及无新输入/close接续，再用有限原型定价空工作、真实工作和已有任务复用。优先消除无用通知，不新增查询、第二history表/owner/队列；若这些前提不成立，则保留原登记并重新选择有据的表达。原T02.4 direct-canonical仍缺可靠可删预算，live-copy语义和整包控制独立保留。

本轮没有事前毫秒点预测，因此只确认原数量假设与局部增量收益，不能宣布预测技能升级闭环或整个算法最优。[净价全结果](exit-price-summary.json)、[独立字面bootstrap/943身份核验](exit-price-audit.json)、[净价原始包](exit-price-raw.tar.xz)/[校验](exit-price-raw-manifest.json)、[实际计数](exit-work-summary.json)、[511身份及头依赖闭包核验](exit-work-audit.json)、[计数原始包](exit-work-raw.tar.xz)/[校验](exit-work-raw-manifest.json)。复现脚本为build/run/analyze/audit_exit_price及build/run/audit_exit_work；r0头选择编译失败、r1四个探索过程和未完整重建声明依赖的限制全部保留，最终计数资格来自r2的6-TU父重建与4过程。未插桩净价一直使用完整冻结父库，不受观察器重建修正影响。

<a id="epoch-exit-closure"></a>
## T07：按最后逻辑保护统一历史回收范围

产品提交 **cb942b6eff6d2afe19f87311e1febf2ccb98c655**。最终ARM64/x86_64六组各**5225/0/0**，合计**10450/0/0**；新增18行/架以及原历史预算、重验、晚释放和close均实际执行。结构门21条manifest/26项owner/16组census、87 TU/2253 API/30613边/26 callback及6项工具自测通过。原33项和此前删除承诺复核通过，未提高侵入上限。

生产代码**+22/−16**（含注释，净+6）；测试**+100/−0**；人工manifest仅方法名**+1/−1**；派生inventory/callgraph **+7811/−7379**。新增代码用于补齐真实回收和精确触发，不以代码净删量代替责任收敛。当前公共upstream42点未重跑，前置结果仅属于16a4；本包没有改变copy语义，也没有关闭其两个已知exact-view失败。

本包从16a4ff59eb出发，只修改原publication、history collector和snapshot释放责任。旧实现同时存在缺失与过度保证：前台旧事务退出只回收epoch记录，漏掉写集外历史页；后台把普通root失效当成缺失key登记而走全metadata扫描；事务或快照仍有同base保护时又重复扫描已知历史。不能只删除扫描，因为前台确实还缺必要回收。

### 理想算法、当前差距与改动索引

令D为本次变化页，H为原history work索引中仍带历史的页，N为全部metadata页。新根相对原current的差异只在D；释放另一个旧base则可能影响D外任意H。触发事件应是**非current根失去最后一个snapshot/transaction保护**，而不是“某个事务结束”或“base不等于current”。

这里的H扫描是复用当前权威数据可构造的实现上界，不是理论最少访问量。若A为此次真正失去可达性的历史页，理论目标更接近受影响集合A；精确产生A可能需要额外版本—root反向登记或比较多个根，其维护费用尚未定价。本包不新建这类索引，也不声称整条GC已达到算法最优。已经可确定删除的是保护未变化时的扫描，以及普通根失效对无历史N页的补扫。

| 原位置/真实consumer | 最终表达及同批删除 | 保留的合同与成本 |
|---|---|---|
| Publication `commitOwnedLocked` | 先登记proof/descriptor的D，再用原epoch root准入判断旧base是否失去最后保护；进入共同收尾 | base即前current只访问D；旧base须保留一次epoch查询，不新设root计数 |
| Publication `abortLocked` | 同一准入判断接共同收尾，补上前台D外回收；不等下次写入或close | 无自己的D也能释放旧base保护的历史；原overlay锁外销毁和物理退休继续 |
| Publication `restoreRetainedEpochLocked` | 原目标D已登记后进入同一收尾，删除独立的第二次collection调用 | 恢复源仍映射到新current；adapter准备/重验、真实拒绝和旧读者保护不删 |
| HistoryCollector `collectAfterEpochChangeLocked` | 替换并删除`collectEpochBookkeepingLocked`；普通保护变化只重排原m_work中的H | 前台先清epoch再执行历史工作，后台沿原有预算/worker；缺失登记的bad_alloc才保留全N补扫 |
| ReadCoordinator `releaseSnapshot` | 前后台均消费原epoch返回的becameUnretained；删前台无条件H扫描/同步处理 | 不增加查询或状态；最后保护释放仍访问H并实际归还backing |
| ReadCoordinator `finishCapturedReleaseLocked` | 核验已有同一last-protection条件，保留 | captured版本token逐项释放还有独立metadata事实，不能仅凭root仍保留就删除；拒绝由原pending记录接续 |

两种收尾owner复用原history索引、epoch权威和物理退休队列。快照出口没有为了统一函数外观加入finished-transaction的额外锁查询；原前后台执行差异、32-version/root预算、晚completion、实际存储拒绝/重试/close均有真实consumer。无新增持久字段、owner、队列或公共API。全N恢复仍必须保留：requestKey在分配失败时可能尚未登记key，H不能覆盖这种情况。

### 预测、反例与兑现范围

| 责任 | 原始反例/事前数量预测 | 最终要求与费用边界 |
|---|---|---|
| 旧事务前台commit/abort，写集外旧页 | 原r0两行实占49152B，期望32768B，多留16384B | 退出后仅等待已启动回收，必须归还1页；这是补足必要工作，不能算CPU收益 |
| 另有同base事务/快照，事务退出 | 首版r1四个protected abort仍多扫1页；旧base不等于current不充分 | 保护未失效时abort新增页扫描0；commit只扫描自身1个D，不额外访问H |
| 另有同base事务/快照，快照退出 | snapshot r0前台两行pagesVisited为4，期望3 | 非最后保护释放新增页扫描0；最后释放仍回收1页，close真实容量0 |
| 后台旧base真正失效 | 从普通事件触发全N登记，改为已知H | 删除一类全metadata遍历触发；实际业务命中、N/H分布与净时间未知，不能假定所有N访问都可省 |

前台必要扫描增量、旧base准入查询、实际free均必须计费。实施包冻结时已量化16KiB遗漏和受保护行1→0的扫描，尚未量化时间；随后[增量净价及真实命中](#epoch-exit-net-price)确认业务局部收益，存储和全包资格仍不足。原0.723ms回退不因此被判定消除，机制计数可重复不等于概率置信区间或时间预测闭环。

[双架与源码身份](transaction-exit-audit.json)、[原删除承诺/反例/实际数据行复核](transaction-exit-contract-audit.json)、[可复现审计](audit_transaction_exit.py)、[全部原始尝试](transaction-exit-raw.tar.xz)、[成员校验](transaction-exit-raw-manifest.json)。原失败r0为4/2/0、首版受保护事务反测10/4/0、快照反测6/2/0；getter/目标名构建失败和结构检查点更新前拒绝均保留。最终资格来自最终源码两架六组，不由中间19/0/0定向结果替代。

<a id="owned-terminal-budget"></a>
## owned终态候选定价：扰动门未通过

16a4的34个ARM64过程使用同一派生库，mode0/2各一次capability，随后8块×4个镜像顺序过程；只有seal中间处理与完整commit两个不嵌套scope。像素、8段/4callback/19 projection、undo/redo/销毁及观察器完整性全部通过。统计单位是块，100000次固定seed bootstrap给pointwise95%区间。

| Stroke粗责任 | 观察CPU ms，95%区间 | 解释限制 |
|---|---:|---|
| 32次owned seal中间处理 | 0.1663 [0.1574,0.1774] | 含必须保留的adapter和清理工作，不是可删预算 |
| 27次borrowed seal中间处理 | 0.1491 [0.1417,0.1534] | 显式history实际consumer仍需overlay |
| 33次完整canonical commit | 1.0272 [0.9721,1.0411] | 含必要publication、动态验证与回收，不能全领 |
| 完整Stroke observer on−off | −0.3083 [−0.5855,+0.2995] | 未落入事前±0.2ms精度/扰动界，候选预算资格失败 |

因此不能把0.1663ms当严格上界，也不能用commit桶给0.723ms差额分摊比例；负on−off不是产品优化。没有追加样本到通过，也没有借这个结果批准direct-canonical重构或否定其所有可能价值。原T02.4继续保留条件设计；当前T07实施来自独立可复现的回收反例。下一有限责任仍需定价真实发布/回收工作，分开必要保证与可删除成本。

[固定协议](PROTOCOL.md)、[结果](business-terminal-summary.json)、[身份审计](business-terminal-audit.json)、[原始包](business-terminal-raw.tar.xz)、[校验](business-terminal-raw-manifest.json)、[构建](build_terminal_cost.py)、[运行](run_terminal_cost.py)、[分析](analyze_terminal_cost.py)、[审计器](audit_terminal_cost.py)。897项身份绑定、129归档成员核验在修改产品前完成；归档中的16a4身份不随当前构建更新。

<a id="business-work-attribution"></a>
## 业务回退：独立发布增加，尚未完成时间因果分摊（2026-10-11）

产品仍16a4ff59eb，本批生产/产品测试均0改动。补充两轮各4个ARM64观察进程，顺序parent/current/current/parent；复用净价原夹具、8段输入、4显式callback、19 projection、原像素/undo/redo/销毁断言。父观察库仍8198、当前是只加观察器并取消共有clear融合的派生库，实际依赖与各自ABI核验。8过程均通过，观察器父子线程/阶段、CPU嵌套守恒、无溢出/活动尾成立；不增加未插桩性能样本，不授概率置信区间。

| Stroke实际工作 | 父8198，四次观察 | 当前16a4，四次观察 | 本轮能排除或确认什么 |
|---|---|---|---|
| stroke / merge jobs | 937 / 19 | 937 / 19 | 未观察到job数增加；不能据此证明调度等待最优 |
| operation / cold / seal | 46 / 208 / 59 | 46 / 208 / 59 | 此用例没有上述次数放大；不代表每次内容和价格相同 |
| projection中的冷准备及producer边界 | 132 / 32 | 132 / 32 | producer取实际operation或setup事件ID，不用可复用的scope地址当寿命身份 |
| 这32个producer进入的事务 | 12、12、14、11 | 32、32、32、32 | 父在同一匿名事务合入多个producer；当前每个producer独立事务 |
| canonical commit入口 | 13、13、15、12 | 33、33、33、33 | 包括一次stroke history提交；父合并量随调度变化，多出的次数是18～21，不是固定20 |
| 当前writable_presence | 未单独插此scope | 0 | 排除本夹具直接调用新增ensureWritablePage的解释，不排除其他初始化成本 |
| 当前adapter页准备 / 安装 | 无同名计数，不补零 | 234 / 212 | 有实际成本，但没有父同口径计数，不能叫作新增量或可删量 |

r2进一步标记当前commit原输入及成功点：两次均为33次真实成功发布，均有非零proof，累计188个proof、4个removal，surface变化为11/10个（并发顺序影响extent是否变化）。没有空提交可直接剪枝。capture次数随实际读时序小幅变化，完整值保留在summary，不强制相等或据此删读保护。

### 机制归因与健全性裁决

父`Backend::writableTransaction`以`anonymousTransaction/anonymousClients`合并不同worker，只有最后client才调用commit；当前`writableTransaction`每次建立原owned事务，并由原mutation在终点提交。这与事件里的共享事务直接对应。原[owner反测](#cancel-owner-review)已证明父设计在8个root拒绝行撤销已返回Succeeded的兄弟操作；恢复匿名合并会恢复这个缺陷。**独立失败/成功责任应保留；“每个独立责任现在付出的所有费用均不可删”不成立。** 当前33次发布不是无效分支，旧cohort及其假成功/整群abort不得回流。

这解释了为什么存储H1改善而绘画回退可以同时发生：公共存储H1原本就有显式history owner，写入不会像并发投影那样从11～14个匿名事务扩展成32个独立事务。两条端点测试不同的发布形态，不能互相代替。原蓝图漏记了所有权修复引起的发布数量增量；仅核对cold/seal、删行和同19次projection不够。

时间模型修订为`ΔStroke = 新增独立发布的固定及逐页/重基/回收成本 + 其他保证增量 − 已删维护成本 + 测量残差`。同132次冷准备不保证各root只访问相同D：父同事务还能覆盖先前同key的变化，当前独立可见版本须各自结算。观察CPU有额外scope扰动，不能把父/新commit桶相减解释为0.723ms中已对账的比例。

对“新增发布足以独自解释0.723ms”的条件反算是每个额外发布平均34.4～40.2µs；这只是0.72325ms除以18～21的**待证门槛，不是实测单价或收益预测**。若仅优化32个投影发布，要消除该点估计回退，平均净省需22.6µs/次，且不能向history、取消、后台或最终释放转移成本。现有数据尚不能证明该目标可达；也不证明0.723ms全部来自发布。

### 理想管线与允许清理的边界

下一责任仍属原T02.4/T04.3–5/T07/T08.2，不增设进度矩阵。最小目标是`原entry私有结果 → 共同准备/校验 → 原canonical接受 → 原adapter交付 → 原责任释放`。owned终态若无overlay消费者，审查中间`候选D → 原transaction map → epoch不可变delta`及两次derived extent表达是否确有必要；history/checkpoint的overlay有真实读者，不能统一删除。

候选代码闭包为Store `sealImpl`/`Private::finishOwnedTransaction`、Publication `prepareOverlayUpdateLocked`/`prepareSurfaceLocked`/`commitOwnedLocked`、Epoch `prepareImpl`/`prepareCommit`及Backend `Private::finish`/manager `PreparedTileUpdates`。实施前须证明原scope已quiescent、独立事务无外部overlay读者/其他producer、原D/claim能覆盖root准备和adapter最终交付。现有ownsTransaction只说明终结归属，不单独授予省略所有中间保证的权限。

优先比较原位消费原entry/原候选的表达，不加第二写集、持久owner、等待队列或成功标志。若直接路径成立，同批删去该路径专用的overlay插入/移交/销毁、无读者的派生surface准备，以及只由这些已消失失败点产生的恢复；共用history路径、真正资源拒绝、same-key/default冲突、proof/provider动态校验、最后guard/orphan与close仍保留。不能为净删量删公共validator，不能以所有fallback有caller为由保留已失效的恢复。

明确排除两种捷径：恢复先返回成功后群体提交；把clear/composite通用融合收益作为PageStore基础收益。集中排队合并独立commit可能减少root次数，但会引入等待、联合拒绝拆分、延迟和峰值责任，当前无价格证据，不建立新协调框架。此处是下一有限候选的责任设计，**尚非已定价的产品方案或预测闭环**；应先验证删量与净预算，再实施完整迁移。

### 证据和失败保留

[工作量及事务分组](business-work-summary.json)、[审计](business-work-audit.json)、[构建器](build_business_work.py)、[运行器](run_business_work.py)、[分析器](analyze_business_work.py)、[复核器](audit_business_work.py)、[全部原始文本/派生源码](business-work-raw.tar.xz)、[成员校验](business-work-raw-manifest.json)。1840项身份绑定和143个归档成员已复核。r0生成器因installPage返回类型锚点写错，在编译前停止，原失败保留；r1/r2分别冻结自身源码/协议/命令。库与对象未放入文本压缩包，其哈希及本地输入路径完整保留。最新安全10414/0/0属于前置16a4验证，本批未重复运行或增加安全资格；live-copy两个exact-view失败、整体净价和正式M6仍开放。

<a id="whole-package-net-price"></a>
## 整包净价：存储改善未兑现为业务收益（2026-10-11）

本次**产品与产品测试改动均为0**，延用16a4ff59eb最终安全库。父8198c36ed7与upstream9a24ae0d8c的原夹具/库哈希核验通过；当前按相同夹具源码、当前ABI重编译。两矩阵各3个capability＋8块×6个镜像顺序进程，合计**102个成功进程**；存储408行/1632个manager寿命，业务153 QTest passed。所有运行实际库、各侧原共享依赖、退出/reap及末尾hash通过。块是统计单位，不把循环或寿命数充当样本；下述均为配对块中位数、pointwise95%区间，不是联合正式门。

### 同义存储主端点

同一公共data manager源码，K16、16次非默认完整覆写、每次立即读回，H1最后commit/undo/redo/purge/销毁；每行合计四次manager寿命、64次write。无画笔、compositor或融合差异。正“节省”表示当前比父更快，额外成本为当前减upstream。

| 端点 | 较父节省 ms | 较父节省%，95%区间 | 相对upstream额外 ms，95%区间 |
|---|---:|---:|---:|
| H1 write前台thread CPU | 1.188 | **17.90 [11.59,24.85]** | 5.232 [4.751,5.628] |
| H1完整case前台thread CPU | 1.342 | **11.70 [4.78,20.33]** | **8.798 [7.718,9.714]** |
| H1完整case process CPU | 1.790 | **10.51 [2.54,19.50]** | **13.901 [12.298,15.160]** |
| H0 write前台thread CPU | 0.671 | 9.00 [7.23,34.09] | 6.264 [6.077,6.435] |
| H0完整case前台thread CPU | 0.562 | 5.09 [3.85,31.46] | 8.945 [8.588,9.107] |
| H0完整case process CPU | 0.386 | 2.41 [−0.64,27.94] | 13.865 [13.432,14.371] |

H1的前台和进程CPU均下降，排除了“本端点所有收益都被后台抵消”；H0进程CPU及整进程收益仍不确定。整个8-case进程含启动/退出仅节省**2.194ms，95% [−2.753,17.336]ms**。K1/H1/16次写完整前台点估计回退0.58%，区间跨较大正负；短操作及teardown控制也未全部排除2%回退，不能把大K正结果变成所有模式非劣。H1完整前台区间下界4.78%未达到事前5%工程参考；这不是改门或续采理由。

剩余前台差额仍以write为主：H1配对算术均值按互斥阶段对账为write **5.224ms**、read **1.980ms**、setup **0.883ms**、finish **0.169ms**、undo **0.148ms**、redo **0.123ms**、teardown **0.147ms**，另有case外框/校验。此处均值仅作可加账，不能与上表中位数混加；read区间process CPU也不能直接归给read线程。当前每次Fresh周转及真实发布/回收仍在，前台5.23ms不是已证明可全部删除的预算。没有新增机制样本，不把旧1024→0 pin等计数冒充此次重测。

### 实际业务控制反例

三方执行原8段、4显式callback、同seed/像素/undo/redo/销毁。父和当前都使用只恢复独立clear的派生image，当前merger产品源码相对8198没有差异，仅重编译同一派生对象；其他当前链接对象保持已测产品。三方每侧17过程均**19次projection update**。原SOURCE_AUDIT中的页分区、失败接线、参数外提、透明RGB修复差异仍披露，所以业务不能代替上述存储本体证据；相同projection次数也不证明内部job、页访问与交付次数相同。

| 业务端点 | 当前较父增加 ms，95%区间 | 相对父变化 | 当前相对upstream额外 ms，95%区间 |
|---|---:|---:|---:|
| Stroke CPU | **0.723 [0.503,0.976]** | **回退4.50% [3.07%,6.18%]** | **7.939 [7.409,8.160]** |
| Stroke wall | 0.247 [0.108,0.576] | 回退3.47% [1.52%,8.48%] | 3.633 [3.331,3.685] |
| Setup CPU | 7.852 [2.399,12.288] | 回退2.15% [0.65%,3.35%] | −3.824 [−11.422,4.171] |
| 整进程CPU | 8.747 [4.063,11.224] | 回退1.87% [0.86%,2.38%] | 6.557 [−6.392,8.089] |

Undo/Redo/Teardown的增量区间均跨零，Teardown CPU节省0.022ms、区间[−0.053,0.093]ms，不能宣称尾已改善。五阶段CPU合计回退2.47%、区间[0.77%,3.33%]；Setup含资源/插件首次工作，不将7.85ms无依据全归PageStore。存储主端点改善与业务回退同时成立，故**本重构的整体性能验收保持未通过**，更不授M6、默认启用或全局最优资格。

### 对蓝图及下一动作的约束

原T08.2现在有整包实际价格，但不关闭：先定位**业务Stroke新增约0.72ms**的真实责任，再处理其他未决控制。竞争解释应覆盖公共writable显式presence/default语义修复的额外工作、prepared adapter及原gate覆盖的实际命中、任务/操作拆分变化和原清理尾。它们目前只是需要区分的解释，不按函数看起来保守就领取CPU预算。下次机制观测须区分新增保证与同义替换、前台与后台，核对同一真实业务输入的job/operation/page/commit计数；之后才选择完整责任实施及独立确认，禁止为净价正向结论回退已证明必要的语义。

没有事前总时间点预测，因此本轮只能确认数量模型的一部分兑现和净结果，不能声称预测准确或技能已完成下一次闭环。live-copy的两个exact-view失败仍是独立语义缺口，不因本夹具没有触发而豁免。原T矩阵仍33项，产品HEAD、结构门及安全资格未变。

[存储全8行/阶段/块值](net-price-summary.json)、[业务阶段/块值](net-business-summary.json)、[身份和独立bootstrap核验](net-price-audit.json)、[运行器](run_net_price.py)、[可复现分析](analyze_net_price.py)、[审计脚本](audit_net_price.py)。原始包：[存储](net-price-raw.tar.xz)/[校验](net-price-raw-manifest.json)、[业务](net-business-raw.tar.xz)/[校验](net-business-raw-manifest.json)。r0依赖分类错误及首版分析对近零other-thread残差错误计算比例均保留；后者仅删除无意义比率，原样本和绝对CPU分析不变，无追加样本。

<a id="deletion-closure-review"></a>
## 删除闭包与保留责任复核（2026-10-11）

父2eb9f4236ff3cf28550716717ec43c676336cd9d → 当前**16a4ff59eb01e87dc435afb81a305413d32223bb**。最后copy恢复caller迁走后，`KisTile::installPageStoreReadCache/takeIdleReadCache`只剩定义声明；本包全部删除。`readCacheForPage`仍被Backend的`selectCurrentReadTile/acquireTile`调用，收回private并删除无人使用的默认参数。`tileDataForReadPage`仍供clone和manager默认backing使用；正常cache失效/选择、动态pin、provider proof验证、scope orphan和collector接续均有真实职责，保留。

| 审查面 | 最终事实及限制 |
|---|---|
| 当前删除闭包 | 全仓tracked C++和编译调用图共同核对；上述两接口无定义/声明/调用。此前各包记录的删除表达式及core/overlay/owned-publication的定域删除要求再次在最终提交验证；不把无直接caller的callback/virtual API自动判死 |
| 权威与生命周期 | 审计清单从已删除anonymous事务组改认原batch的客户端/lease登记，与原mutation scope的owned事务终结分别记账；新增的是审计事实记录，生产不增加owner、状态、队列或调度分支 |
| surface/proof保留 | `surfaceDefaultAndExtentMutateAtomicallyWithEpoch`验证默认值随current/retained/undo/redo选择，以及extent与root共同提交；`ownerLedgerVerifiesTerminalProviderIdentity`验证错误operation、provider epoch及completion拒绝；`ownerLedgerSealsPreparedPageBeforeEpochCommit`验证真实metadata满额拒绝、输出不变及准备后满额安装。不能用entry状态替代这些动态事实 |
| 物理与最终释放保留 | `physicalBackingHandoffGuards`覆盖14类reader/writer/reservation/raw pin/引用/alias/foreign provider/swap/iteration阻碍，拒绝不retag；`lastUseCloseAndLifetime`及`firstRetirementRunsOffThreadAndCloseDrains`验证晚completion、facade析构、后台provider工作和close归零。这不是M7生产handoff资格或全局最优证明 |
| 当前结构门 | 修正旧refresh、anonymous组、iteratorScope、PreparedTransactionState及旧测试名字的要求；重新生成87 TU、2,253 API、30,565调用边、26 callback登记。21项manifest、26项ownership、16组runtime census及6项工具自测通过；runtime census的static-only项仍保持static-only |
| 侵入代价 | manager实计60标识/4 include：32诊断timer/phase，28实际backend/operation/能力引用。仅该文件旧25/3上限按92逐责任复审为60/4；其他上限不变，convergence-start和retired-protocol证明不刷新。局部B/R候选、manager gate、claim、free均继续收费，不把更新检查点当作性能许可 |

最终六组双架构各**5,207/0/0**，合计**10,414/0/0**；公共当前/upstream探针**42观察点逐项相同**。源diff、实际加载库、进程退出/reap和末尾hash均绑定最终提交。未新增或改写产品测试；没有因本包删除死接口而重复分配探针或性能采样。此前两个live-copy exact-view失败仍开放，不能被本次六组全绿覆盖。

| 文件类别 | 本包实际增删 |
|---|---:|
| 运行时生产代码（3文件） | +1 / −28，净−27 |
| 架构检查器（1文件） | +2 / −2 |
| 人工审查清单（3文件） | +72 / −40 |
| 派生调用图及源码检查点（2文件） | +49,286 / −33,288 |
| 测试 | 0 / 0 |

**理论与实际：** 被删接口已无consumer，预期动态调用删量为0，本包不预报可测CPU收益；实际确认的是生产冗余删除及结构身份恢复。巨大JSON差异主要是整条既有重构后的图/源码位置更新，不能计作运行时代码增长或删除。两copy此前的W个warm替换和失败A页恢复、clone归并、导入retention等机制结果仍按各冻结包解释，不能把它们的删量直接累加为总时间收益。

结论：原owner上“准备→接受→交付→最后释放”的方向有现行代码和行为证据支持；目前不足以宣布整条管线健全且高效。原T06.3仍欠live-source与immutable exact-view的合同收敛；T08.2仍欠同义父/新/upstream完整净价、普通路径控制及最终释放端点，M6/M7/M8保持0/3、校准2/20、默认关闭。不得为这两项缺口再建平行发布/恢复管线，亦不得把snapshot新增复制隐入同义PageStore基础性能。

[源码/双架/公共探针审计](delete-closure-audit.json)、[删除/保留/分类审计](delete-closure-contract-audit.json)、[复现脚本](audit_delete_closure.py)、[全部原始记录](delete-closure-raw.tar.xz)、[成员校验](delete-closure-raw-manifest.json)。初次结构门137条过期/侵入错误保留，修正后只读门禁通过；旧失败不删除、不改写。

<a id="copy-prepared-delivery"></a>
## 普通与 rough copy 的准备、发布、安装收敛（2026-10-11）

父 `e1a26e14d91f26db4e4f03b470842105fda00165` 的两个兼容copy循环在root接受前删除/替换目标wrapper，失败后再capture并扫描整个矩形恢复。四BPP×ordinary/rough的真实MetadataArena root拒绝反测均观察到**接受前索引已改变**，八项失败；这些行在该断言处停止，不能外推成后续canonical/索引一定恢复失败。静态legacy source让此反例独立于待选择的live-source语义。

产品 `2eb9f4236ff3cf28550716717ec43c676336cd9d` 把最小完整责任改成：原像素/alias写集 → seal原overlay候选借出有序D → 原manager gate内准备缺wrapper、删除能力与extent容量 → 原root（或借用history overlay）接受 → 原保留write set借出实际D安装 → gate外销毁局部候选 → 释放原scope/claim。两次借用共用`AdapterChanges`，不复制D、不保留第二份overlay、不增加owner、队列或持久阶段；prepare输入有序，最终install只要求unique，不为原write顺序再排序。所有栈回调在原调用内结束。

成功交付的claim覆盖候选退出；拒绝时未安装候选只作局部析构，raw working缓存失效、B插入撤销和可能被预算拒绝的物理取消仍由原batch/scope/orphan处理。真实读必须成功`lockForRead`后取得数据，不能把未加锁的旧TileData缓存当current能力。原自动重试在解除压力后完成取消；一次`kisDrainPageStoreReclamation`仅等待已排队任务，不包含未来retry wake，因此测试按既有5s合同观察归零，不主动abort或新建操作代偿取消。

| 删除/保留 | 本包结果与成本边界 |
|---|---|
| 两套普通/rough循环 | 合为`bitBltImpl<oldSource, rough>`；legacy-only目标保留原hash语义，这部分循环去重是通用维护简化，不能计PageStore性能证据 |
| PageStore整页提前删/建warm wrapper | 接受后失效原warm wrapper；只为实际冷缺项准备新wrapper。必要source捕获、alias、default删除仍存在 |
| 两个失败恢复scope及整矩形refresh | 随producer交付迁移删除，`refreshPageStoreIndex/refreshPageStorePage`定义、声明及无用forward declaration一起退出；四个原raw恢复caller至此全部迁完 |
| 最终结果的第二份D目录 | 不建立；prepare借原overlay，install借原retained write set。新增函数指针借用视图和栈回调仍有执行成本 |
| 拒绝/取消、legacy目标、source live alias | 均有真实consumer，保留原语义；没有用删错误检查、失败分支或选择另一copy语义换取通过 |

可删量按真实工作计：令A为请求内页数、D为实际变化数、B为新增wrapper数、W为整页变更中已有且仍存在的wrapper数。成功路径删除W次warm wrapper重建和对应detach/retirement；冷B准备、R个真实删除、D准备与安装仍收费。失败删除一次额外capture及A页resolve/cache重建；原raw取消仍可能遍历其实际entry并失效缓存。原像素循环、source/target取值及整页memcmp不消失，也不声称O(A)成为O(D)。新增准备和manager gate覆盖费用尚未定价，净毫秒收益未知。

定向r4 **80/0/0**，包含八个root拒绝及16个四BPP×ordinary/rough×standalone/history的混合边缘页/整页/warm/cold/default删除、真实overlay预算拒绝、先前history保留、自动取消、重试及undo/redo。r1为61/3（未加锁缓存旧断言），r2与r3各64/16（立即/单次drain归零假设），全部失败和原始输入保存。两架构安装探针各64行：48实际窗口无分配、16空copy无事件；ARM/x86窗口内free共578/577、单窗口最多32，**不授零free保证**。峰值、最终释放及净价继续收费。

最终r4双架六组 **10414/0/0**，每架manager1817、Reference1019、CpuMutation1721、Physical398、Resident221、lockless31。公共history/presence探针42点与upstream一致；live-copy专用探针24点与upstream及此前冻结观察均相同，实际加载库与完整测试绑定。生产六文件 **+101/−189，净−88**；测试两文件 **+152/−3**。新增的是原能力借用和有序准备，未以删注释或压行替代政策简化。

[源码/双架/删除/分配审计](copy-delivery-audit.json)、[反例与合同审计](copy-delivery-contract-audit.json)、[全部原始尝试](copy-delivery-raw.tar.xz)、[成员校验](copy-delivery-raw-manifest.json)、[安装探针](copy_allocation_probe.cpp)、[附加审计脚本](audit_copy_delivery.py)。已知live-copy目标exact view两个失败仍未修复，不能用本包通过覆盖；原公共live alias及clone/redo未来变化的语义选择仍待定。本包关闭两copy交付和raw恢复删除责任，不代表T06.3整体或M6完成。M6/M7/M8仍0/3、正式校准2/20、默认关闭。

<a id="import-owned-lifecycle"></a>
## 当前实施：导入复用原owned生命周期，删除私有history（2026-10-11）

产品`e1a26e14d91f26db4e4f03b470842105fda00165`，父`667c8d65162017f872352b19a8c4a8e3e5815521`。实际`KisPaintDevice::read/readFrame`只传回bool；KRA读取失败会断开设备，剪贴板导入失败会丢弃，尺寸探测读取结果范围。没有caller接收导入局部`nothing`作为undo结果。先前四轮读入/清空/排空留下`2/4/6/8`个retained root token的[冻结反例](#import-history-retention-counterexample)得到修复。

目标流程落实为：原`clear`恢复点 → 解析头 → 原batch在idle-store条件下拥有整次解码 → 每页guard归还RAM pin → 最后统一接受/交付，或由同一batch取消D/B并通过原scope/orphan退出。没有新import owner、队列、持久阶段或回滚表。原`beginMutationBatch → prepareMutationBatch → writableTransaction`传递`requireIdle`，在原transaction/backend锁域核对活动事务；默认调用仍保留原借用政策。有效空文件同样准入，已有history或外部事务时拒绝。

本次删除的完整闭包是PageStore导入的`getMementoLocked/commitHistory`接线、默认backing保活、before/after输出及其memento索引、history脏区求值，以及失败时`PreparedHistoryAbort/abortPageStoreHistoryLocked`全量准备。后两helper、默认色保活及history本体仍服务真实公共undo/abort，继续保留；legacy导入仍沿自己的memento/commit。原失败测试通过QIODevice回调加入独立native operation，从而保留私有history供后续tryCommit；现在嵌套native写在原batch入口拒绝，这条无人消费的实现接续随私有history一起删除。新测试同时验证拒绝、无history、像素/索引恢复及真实raw guard跨read返回后的最终释放，没有只撤去旧失败断言。

| 事前模型 | 实际证据与保留成本 |
|---|---|
| 每次导入不输出undo结果，删两份持久root token | 四BPP各四次真实read/clear/drain由`2/4/6/8`变为`0/0/0/0`；两架均复验。必要current root仍存在，不能称删除所有root |
| 私有history及逐页小scope改由原文件batch表达 | 三个生产文件+31/−29，净+2；导入生命周期减少一套结果/取消政策，新增显式idle准入和bad_alloc返回false。正常history及legacy消费者保留；未为净删行数压缩代码 |
| 解码完成即归还页驻留，不能要求整文件同时在RAM | N17/257×BPP1/4/8/16，每页后真实swap-out，分别16/256次成功；最终像素一致，单个顺序session最大pin=1。D个private条目、B个逆安装token、metadata容量及最终交付仍计费，不把此pin证据扩张为全进程峰值下降 |
| 保持当前清空后失败语义，消除无消费者输出 | null/空流/坏头/坏尾、嵌套写拒绝、跨返回raw guard、stream抛bad_alloc、已有history/外部事务，以及实际MetadataArena满额导致的最终root拒绝/释放/重试通过。异常注入仅证明展开，真实资源证据来自root拒绝 |

成功输入仍为文件解码与N页必要输出；大batch保留更长的变化/逆安装集合，旧双root保活消失不自动抵消这项峰值。尚未测相对upstream实际retained bytes、进程峰值或净时间；不把本次token清零或通用legacy行为作为PageStore基础性能通过。

最终r2六组双架各**5183/0/0**，合计**10366/0/0**：manager1793、Reference1019、CpuMutation1721、Physical398、Resident221、lockless31；x86_64为Rosetta。测试两文件+216/−16。r0定向43/0/0，r1补流式换出后51/0/0；r2补异常展开后执行最终全组。全部构建、源码diff、实际加载库、退出及reap已核验；父反例和之前探针失败仍保留。

最终相同[公共探针](import_semantics_probe.cpp)在ARM64新/父的42个观察点逐项相同；当前/upstream仍为32相同、10不同。成功四类24点完全同义，坏尾部分内容和空流返回值的10点差异原样保留，未暗改为upstream失败合同。generic `audit_package.py`仍要求传入的upstream probe全同义，本包不放宽该通用断言，而以[导入合同审计](audit_import_owned.py)独立核对父观察、成功输入同义、保留差异、retention、swap及删除闭包。

[源/库与双架审计](import-owned-audit.json)、[合同及数量审计](import-owned-contract-audit.json)、[全部实施原始数据](import-owned-raw.tar.xz)、[成员校验](import-owned-raw-manifest.json)。这关闭原T04.12导入结果寿命责任；两copy语义/交付和完整性能仍未完成，M6/M7/M8保持0/3。

<a id="import-history-retention-counterexample"></a>
## 冻结父版本反例：导入留下无人消费的历史保活（2026-10-11）

冻结父667c8d6516时仅增加反测，未修改导入实现。真实压缩流在四种BPP下各执行四次`read → clear → kisDrainPageStoreReclamation`，像素正确、无current memento、活动事务为0，但retained snapshots从0依次变成**2、4、6、8**，四行均失败（init/cleanup通过）。源码对应`read`局部`nothing`不返回undo消费者，`commitHistory`仍生成before/after保活及两个memento索引；`KisMemento`析构只释放默认色，没有purge。该失败反测原样冻结，修复与新证据见[上方交付](#import-owned-lifecycle)，不能用clone的冻结10302通过覆盖父反例。

这证实该父实现每次成功导入残留两份root token，尚未测它对应的实际payload/metadata驻留、后续CPU时间，也没有测upstream的保活字节；不能把token数直接当作相对upstream的成本差。upstream同样有历史结构，`purgeHistory`还有裁剪旧revision的政策，须沿实际consumer进一步核对，不能仅凭局部`nothing`名称宣称两边价格。

同一[共同public/protected API探针](import_semantics_probe.cpp)分别编译链接当前/upstream，各42点、均正常退出且实际库正确；**32点相同、10点不同**。成功输入四类（空图、单页、多页、显式默认页）的24点相同。坏尾流在首个真实页解码后返回false：当前清空已读页，upstream保留该页，差异延续到clone及后续edit/undo/redo的5点。空流当前返回false、upstream返回true，另5点返回值不同；坏header这组观察点相同。不能将失败回滚的额外语义隐入普通管理成本，亦不自动恢复upstream的空流接受。

该判别时原T04.12要求先追`read`真实caller的失败内容/取消接续需求，比较原owned mutation能否承接导入及原B/D交付；其transaction base本已保护失败前状态，不应默认再生成可撤销before/after输出。若仍需history，必须明确结果是否有undo消费者，并让成功及取消拒绝后的`tryCommit`遵守同一保活政策。只在read成功尾补purge会遗漏后一条，也仍先生成再销毁无用after/default/dirty输出，未作为理想方案采用。暂不新增导入队列、第二owner或临时bool旁路，未据此暗改失败语义。

r0共同探针未编译（read/write为protected，改用两边相同的公开派生适配）；r1当前运行日志因缓冲JSON与坏header诊断交错而解析失败，未到upstream；r2显式行缓冲后完成，两次旧失败原样保留。[反例与身份审计](import-history-diagnosis.json)、[原始记录及完整测试补丁](import-history-diagnosis-raw.tar.xz)、[成员校验](import-history-diagnosis-manifest.json)、[复现审计](audit_import_diagnosis.py)。这是父版本反例，不授予功能/资源/性能门；后续修复不改写这批失败。

<a id="clone-fixed-view-delivery"></a>
## 当前实施：clone固定视图贯穿初始化、像素与索引（2026-10-11）

产品`667c8d65162017f872352b19a8c4a8e3e5815521`，父`a24062b966c05236c171e43b90b35fd3b86931a8`。父实现先导出current manifest，再导出完整history prepared-set逐项搜索/删除/替换，最后另取history base+overlay读像素。独立Store producer推进current而history仍保留base时，四种BPP的clone均失败；该夹具是跨层防御性反例，不冒称普通manager业务已命中。另一个实际错位是manager复制源working hash，会把尚未sealed的新页带入目标索引，而目标canonical仅有sealed页。

现在`configureClone`先取得一次受保护的读视图，随后`Store::snapshotForClone`从它的原root和已冻结有序delta生成manifest；同一视图用于descriptor对应的像素采用。初始化完成后把原manifest移动给manager构造懒wrapper，不再复制源hash或调用源`tileData()`。输出不逃逸构造作用域，未新增owner、队列、持久状态或第二份页目录。单surface的tiles3配置、源transaction准入/manager锁、实际capture保活、每页adoption及构造失败RAII保持。

下游`prepareInitialization`对有序输入直接建立owned树节点，删除第二份N-entry临时数组及排序；真正无序的外部输入仍复制/排序，没有新增trusted标志绕过公共验证。canonical manager使用原`getTileLazy`建立缺项，避免源缓存复制；没有改用通用`addTile/insert`，后者会为根本不存在的旧值准备retirement。legacy-only manager和直接Tile copy仍有真实working-data消费者，保留原路径及其拒绝。

| 工作 | 父实现 | 最终实现与保留成本 |
|---|---|---|
| clone取样 | current快照与history读视图两个不同cut | 一个captured cut；retained capture次数本来就是1，不能称2→1次capture |
| base N、delta D、输出M | 全prepared-set导出，逐项find/erase/append：最坏O(ND+D²) | 从原capture的有序D直接归并；D>0先计数再写出，两次O(N+D)访问，只复制M条最终输出；D=0沿原一次导出 |
| 导出容量 | N起步并可能扩容，另有完整prepared-set | manifest按M预留；原capture的D排序/保护仍收费，不称整次零分配 |
| 派生范围/验证 | clone再扫manifest重算extent；乱序追加可触发平方去重回退 | 删除`updateSnapshotDerivedExtent`；复用已维护surface事实，有序输入仍执行公共验证 |
| 初始化 | 另复制M条再排序、建树 | 加一次有序性检查，直接建树；无序外部输入保留原排序，必要节点分配不删除 |
| 兼容索引 | 复制源W个working wrapper/cache，可能物化未暴露写意图 | 消费同一M条manifest建目标wrapper；不带入private pending页、不产生源写申请；必要wrapper/锁/引用/extent构造仍收费 |

这把**clone投影子责任**从可能的平方工作收敛为线性归并，并删除有序初始化的一份M-entry数组和一次排序；不是整次clone严格O(N)，逐页metadata/adoption、节点分配与最终释放仍有各自成本。两遍归并以2N访问换取精确输出容量，没有再建N目录；不把输入量当时间占比。相对upstream的净耗时、收益幅度和置信区间均未测，留在原全包固定对照，不能用普通初始化清理单独授予PageStore性能资格。

新增52个数据行覆盖N0/1/17/257、D0/1/N、四BPP、混合增删改/负坐标/default、persistent未sealed页、history base与current分离、真实metadata预算拒绝/重试。原64行Tile copy拒绝组中，4行原来因manager clone误物化写意图而拒绝；现在要求预算满时clone仍成功、source写页数为0且像素正确，再用真正`tryWriteData`确认预算仍拒绝。原foreign/anonymous batch准入及直接Tile copy拒绝保持。Reference的独立map oracle增加逆序初始化，并继续原96轮delta。

全部失败保留：r0为测试API拼写构建失败；父r1为4个manifest/读cut不一致失败；r2为71/32，其中20条由Qt的emit宏吞掉局部回调、4条是working索引错位、4条是本来应拒绝的base-changed abort清理期望、4条故障注入未进入显式next边界。r3命令两个selector错误（0/2），修正命令的r3b为103/0/0；r3完整ARM为5147/4/0，四条正是上述旧物化拒绝断言。r4定向167/0/0；r5仅构建。最终r6双架六组各**5151/0/0**，共**10302/0/0**：manager1761、Reference1019、CpuMutation1721、Physical398、Resident221、lockless31。最终相同[公共clone探针](clone_semantics_probe.cpp)在ARM64当前/upstream的42个观察点相同，覆盖页存在、像素hash、default、extent、undo及源后续修改。此探针没有选择或修复已知live-copy语义冲突。

生产8文件**+119/−107，净+12**；测试3文件**+178/−1，净+177**。净增用于把原固定视图贯穿完整consumer，未以删注释、压行或隐藏必要成本追求净减。[源码/库/删除审计](clone-view-audit.json)、[全部原始尝试](clone-view-raw.tar.xz)、[成员校验](clone-view-raw-manifest.json)。该冻结点原T06.2与T08.1更新；当时T04.12 import history、T06.3两copy及完整性能仍开放。M6/M7/M8 **0/3**、正式校准**2/20**、默认关闭。

<a id="history-segment-delivery"></a>
## 当前实施：history直接交付原overlay变化，删除无消费者投影（2026-10-11）

产品 `a24062b966c05236c171e43b90b35fd3b86931a8`，父c1f。原persistent history在每次checkpoint先seal，再创建一个无人消费的captured view、导出累计history的proof/removal/surface数组和D-key数组、逐页重解及晚刷新；commit也为adapter和脏区导出累计变化。现在原seal在overlay接受前准备实际段变化需要的兼容能力，接受后直接安装，最后才清理候选和结束原claim。已有working wrapper仍须失效旧cut缓存；独立backend producer的缺wrapper也在接受前准备，不能仅凭前者已存在便省略交付。

`AdapterChanges`仅借原`KisPreparedOverlayUpdate::changes`，没有新变化数组、持久字段、队列或第二owner。该集合已唯一、有序，过滤后的候选仍有序，因此也删除本入口的重复sort。准备/安装在Store主锁外，原scope/manager/publication锁上下文保持；候选在manager锁外销毁。内部checkpoint只返回成功/失败，直接删除无consumer的capture及其拒绝分支；公开`KisPageMutationSession::checkpointForRead`仍提供exact view和原capture拒绝/重试合同。root拒绝保留已经sealed并交付的结果，再次commit不重放该段。

同批删除`historyChangedPages`、`refreshPageStorePages`、bool-presence `refreshPageStorePage`及全部调用。完整history变化只剩提交脏区这个consumer，由原publication owner直接访问proof/removal求边界，保留坐标/矩形溢出拒绝；不导出数组。copy专用exact-view refresh仍有两处实际caller，未误删。生产9文件 **+200/−110，净+90**；测试2文件 **+139/−2，净+137**。净增主要是前置准备/不可拒绝交付的同步接口与脏区直接访问，不意味着整条管线代码已净减少。

| 责任 | 父实现 | 最终实现及成本边界 |
|---|---|---|
| 第i段变化D_i，累计历史H_i | checkpoint导出并交付H_i，commit再导出/刷新累计集 | 借原候选两次访问D_i并安装D_i；未触碰声明不重访；空段不交付 |
| 内部checkpoint读快照 | 每次成功checkpoint产生一个随后丢弃的capture | 0；真实后续读者仍各自capture，不吞掉其必要成本 |
| history提交脏区 | 完整prepared-set和key投影后遍历H | 原owner一次访问H；必要扫描仍收费，未宣称脏区计算消失 |
| 兼容资源与释放 | 接受后可能创建wrapper/准备删除 | 接受前准备实际缺项/删除能力；候选存储、两次遍历、锁域及最终释放收费，时间未知 |

若r次checkpoint每次新增d个不重叠页，仅checkpoint的adapter访问从`d·r(r+1)/2`降为`d·r`，另删r次无用capture及相应完整导出；最终空段commit不再刷新H。重复修改同一组页时不享有这项三角形删量，但capture/导出仍删除。原型r3还需两次扫描S个声明项再过滤D；最终r5改借已有候选后为2D，没有为获得这个数量增加D目录。以上是条件工作量模型，不是实测耗时、概率置信区间或upstream差额回收承诺。

新增28行覆盖四BPP、working/缺wrapper两producer、checkpoint/final、未触碰声明、连续/空checkpoint、dirty extent、undo/redo、受控adapter拒绝、实际metadata硬满下空内部checkpoint成功而真正capture失败，以及真实root预算拒绝后不重放。受控prepare拒绝不冒充hash allocator耗尽。r2首轮 **27 passed / 48 failed** 暴露安装放在coldPages释放后导致实际遍历为空，阶段D计数不能证明完成；已修正时序，随后进一步去掉对coldPages的借用。r0/r1构建失败、r3中间通过和r4仅构建身份都保留，不转授最终资格。

最终r5定向75/0/0，六组双架各 **5099/0/0**，共 **10198/0/0**（manager1709、Reference1019、CpuMutation1721、Physical398、Resident221、lockless31）。相同[公共history探针](history_semantics_probe.cpp)的42观察点与冻结upstream一致；它验证普通公共历史能力，persistent扩展由上述产品测试覆盖。真实allocator双架各64场景，BPP1/4/8/16×N0/1/17/129×checkpoint/final×warm/direct；warm页在安装前全部建立旧cut缓存。各48个实际安装窗口alloc/free均0，各16个空段无安装事件，所有内部capture增量0；构造正控制确有分配。这只限定冻结窗口，不能撤销purge已证实的cache/binding释放，也不代表最终回收免费或全局零free。

[源码/库绑定审计](history-segment-audit.json)、[所有构建、失败、中间及最终原始记录](history-segment-raw.tar.xz)、[成员校验](history-segment-raw-manifest.json)、[安装探针](history_segment_allocation_probe.cpp)、[复现入口](run_clear_allocation.py)。原T04.8/T04.10/T06.1/T06.2原位更新；clone导出仍有consumer，导入history与copy完整交付继续审查。两个live-copy exact-view失败未修复；全包父/新、同义upstream及业务控制未运行，M6/M7/M8仍0/3、正式校准2/20、默认关闭。

<a id="purge-prepared-delivery"></a>
## 当前实施：purge准备后交付与删除能力清理（2026-10-11）

产品 `c1f4efcf07c44577454302e0a5c708325cff9826`，父e9d。`purge(area)`保留H个索引遍历、相交K页的默认backing pin与整页比较；仅对命中的D页借原removePages/batch准备map-key及GC动作，再统一接受和安装。D=0直接返回，不创建事务/session；D个claim至原候选释放。内容判定到删除之间仍依赖调用方已结束迭代器、排序设备写入：clearSelection和设备去重清理是实际依据，不新增并发purge/default变更保证，也不声称删除时的claim能追认此前观察版本。未增加覆盖K页的claim或包住比较的大锁。

删除原待删TileSP列表、其到keys的复制循环和PageStore接受后的deleteTile；legacy仍按原hash删除。无锁hash的纯Absent候选仅使用原key/retirement，故同时删除无消费者的旧tile查找与强引用保活，影响clear/restore/trim/purge的该准备分支；Present/MayRemove仍保留实际tile，链式hash保留防止同步unlink在锁内销毁旧tile的引用。没有新增owner、队列或恢复状态。生产3文件 **+45/−12，净+33**，测试2文件 **+115/−0**。预备token容量/key/GC与延长claim仍收费；选择容器清理同时影响legacy，是通用清理，不能单算PageStore基础性能收益。

新增36行：BPP1/4/8/16、history、D0/1/17、部分相交仍比较整页、页尾非默认不删、范围外默认页保留、旧raw/exact读、表身份、D个实际claim、undo/redo及改默认色；另在准备后/owned root发布处耗尽真实进程metadata预算，确认不安装、canonical/index不变，释放压力后同范围重试成功。它们不是hash allocator本身耗尽的反例。定向55/0/0；首版ARM5071/0/0后追加Absent清理，最终r1六组双架各 **5071/0/0**，共 **10142/0/0**（Reference1019、CpuMutation1721、manager1681、Physical398、Resident221、lockless31）。独立[公共purge探针](purge_semantics_probe.cpp)的42个观察点与冻结upstream相同。

**零free假设被真实反例推翻。** allocator r1首个D1安装为alloc0/free1；r2的实际栈定位到notifyDetachedFromDataManager删除闲置Tiles3TileReadCache。purge的比较建立缓存，前一clear探针没有覆盖该状态，因此不能把其冻结128个零free场景外推为普遍保证。r3仍检查零晚分配、真实事件与业务结果，明确只报告free，不赋予零free资格：双架各64场景中48个实际安装窗口均alloc0，16个零命中没有安装事件；各删除1776页，ARM/x86前台free分别 **1832/1835**，最大单窗口138/136。r4 ARM保留每类free的实际栈，无溢出；除缓存对象，还有最后持有的Tiles3ResidentBinding控制块，数量受背景回收交错影响。此诊断重插桩只用于机制归因，不是时间样本，也不能把r4次数回填到r3。

这些释放没有产生可拒绝的晚准备，但仍是实际管理成本、也仍发生在原detach锁上下文；本包未将其迁到锁外。为追求零free额外保活D份cache或新增延迟队列并非当前接受边界所必需，未引入。此前“候选/旧map引用在安装后释放”不代表整个安装没有free。成本模型修订为保留H遍历与K次内容判定，减少选择列表/复制及每个无锁Absent的一次旧tile lookup/保活，增加预备能力与claim寿命，另保留实际cache/binding清理；未测净毫秒、峰值或相对upstream收益。

[同源审计](purge-delivery-audit.json)、[所有构建/定向/首版/最终/失败allocator与归因尝试](purge-delivery-raw.tar.xz)、[成员校验](purge-delivery-raw-manifest.json)、[allocator探针](purge_allocation_probe.cpp)、[复现入口](run_clear_allocation.py)。原33项仅结算purge准备/接受/交付与纯Absent无用保活；history、两copy及完整性能仍开放，live-copy两个exact-view失败未修复，M6/M7/M8保持0/3、正式校准2/20。

<a id="clear-prepared-delivery"></a>
## 当前实施：全量clear在接受前准备索引删除（2026-10-11）

产品 `e9d2048b4ca202c3c60d97ea53c855991735c997`，父f25d。manager全量clear复用原PreparedTileUpdates/PreparedTile，先准备实际索引的map key及QSBR删除动作，再经原remove batch接受并安装。原OperationDelivery保持非空canonical的claim到候选锁外释放；空canonical但有wrapper残留时仍准备并交付，不创建空事务。原表身份保留；restore/trim与clear共用原removal准备，clear无需对候选排序或额外导出变化集。

删除PageStore clear成功后的hash clear晚分配/重试路径；legacy-only hash clear仍有真实consumer而保留。原same-thread raw barrier及外部排序要求保持，不新增并发clear保证，也不承诺恢复已被barrier取消的未发布raw写。候选/旧引用不在manager安装锁内释放，没有第二索引、队列或owner。生产3文件 **+97/−30，净+67**，测试2文件 **+73/−0**；这是接受边界修复，原N个GC动作前移，额外map-key/候选容量及claim延长均收费，峰值和净时间未定价。

12个新增行覆盖N0/1/17、history、独立backend造成的空canonical/非空wrapper、受控adapter拒绝后canonical/index不变、旧raw/exact读、表身份、安装时原claim仍在及undo。定向57/0/0；最终六组双架各 **5035/0/0**，合计 **10070/0/0**：Reference1019、CpuMutation1721、manager1645、Physical398、Resident221、lockless31。当前/upstream公共探针42点相同。

真实malloc/calloc/realloc/aligned/free拦截，双架各64场景（BPP1/4/8/16、N0/1/17/129、history、wrapper残留）在安装线程的Install→Installed区间均 **alloc/free=0**，开始/结束事件各1，真实manager构造正控制有分配。它不代表整次clear零分配或业务性能通过。受控prepare回调拒绝不是实际allocator耗尽反例；r0正控制无分配和r1缺开始事件的无效探针均完整保留，未当作产品分配缺陷或通过。

[源码、两架运行及探针审计](clear-delivery-audit.json)、[所有原始尝试](clear-delivery-raw.tar.xz)、[成员校验](clear-delivery-raw-manifest.json)、[可复现探针](run_clear_allocation.py)。两copy的已知exact-view失败、purge内容判定/删除交付、history commit/checkpoint和最终同义性能仍开放，M6/M7/M8维持0/3。

<a id="raw-write-recovery-deletion"></a>
## 前置实施：packed/planar取消复用原写集（2026-10-11）

产品 `f25d3085d0201fd0585daeb9c645e1dbc405e752`，父11ad。删除两个失败caller的`refreshPageStoreIndex`；原batch在claim释放前失效实际D缓存并撤销实际cold插入B，外部已持有的裸指针保持原owner及归还边界。没有增加owner、状态、容器或恢复分支。planar原失败警告仍保留，copy的两处refresh及其exact-view helper仍有真实用途，未误删。

新增12个实际Mapping/Allocation/Decompression swap-in拒绝行：先写外部raw页、已有页和空页，后续页拒绝；本次warm/cold结果撤销，canonical保持before，原raw pointer不被撤销，归还后同范围重试及history undo正确。父版本14/0/0（含init/cleanup），删除后定向37/0/0；完整r2曾因顺带删除planar诊断得到manager1631/2/0，恢复原警告后独立r3双架六组各 **5023/0/0**，合计 **10046/0/0**。Reference1019、CpuMutation1721、manager1633、Physical398、Resident221、lockless31；当前/upstream公共探针42点同义。

生产1文件 **+4/−10，净−6**，测试2文件 **+74/−0**。删除量为每次失败的一次capture和至多A个矩形页的resolve/缓存安装尝试；实际工作集D及必要取消仍存在，正常路径没有独立可领取收益。未做本包计数插桩或时间定价，不能将数量上界写成实测节省，不能据此宣称M6性能改善。[源码与双架审计](raw-write-audit.json)、[全部尝试](raw-write-raw.tar.xz)、[成员校验](raw-write-raw-manifest.json)。

该批通过范围不包含下面的live-copy反例，后者仍未修复。M6/M7/M8保持0/3，正式校准2/20；下一实施仍沿原33项完成copy输入能力/延迟交付、history commit/checkpoint、purge/clearAll和最终同义性能。

<a id="live-copy-contract-conflict"></a>
## 健全性反例：live alias 不能当作 immutable source（2026-10-11）

冻结父产品 `11adac3e3a66a25bca54de0e4a12583269f8f955`，只增加判别测试。源端持有原始 write pointer，整页普通/rough copy 到目标后取得目标 exact view，再经原 pointer 将首字节 `0x71→0x72`，两个 exact view 均随之改变，结果 **2 passed / 2 failed**（init/cleanup通过）。`captureCompletedTileSource` 在这个入口只保活 TileData，无法冻结已暴露的裸指针；原同地址断言没有覆盖未来修改。

同一份公共 API 探针分别编译、链接当前和冻结 upstream；普通/rough×有无目标history×六个观察点，**24点逐项相同**：源后续修改改变目标，也改变 copy 后建立的 clone；history undo回到0、redo仍是被源修改后的0x72。因此不能把修复描述成完全同义的“延迟安装”或把upstream比较中的差别隐藏成普通管理成本。公共live-alias行为与本分支的exact-view不变保证在当前表达下冲突。

待确认的直接方案是复制完成即冻结live source：同步消费源行到独立最终payload，之后统一交付；真正immutable的source继续alias。逐live页复制的可构造费用上界是 `K_live×4096×BPP`（RGBA8每页16KiB），不是严格下界：多个目标若消费同一实际mutable backing，只需冻结一次，再共享这个已冻结source。理想量取决于需要独立冻结的不同payload数量U及其真实版本/布局/观察时点，不能因整段copy进入fallback便复制全部K页；原sources去重可否表达该事实需核验，不新增第二份source目录。源命中数、驻留、分配/最终回收及复制单价仍须测量。它同时改变上述upstream公共行为，未获语义选择前不实施，也不从相对upstream基础性能样本中隐去这项增量。

若必须保持live alias，则必须另证可变共享内容的发布和exact capture隔离：一个持久引用不能代替内容冻结；仅在clone处COW、只延迟目标wrapper安装或在源最终unlock时补处理，都挡不住此前exact view已被修改。不能为此默认新增跨Store owner、别名目录或第二恢复队列。该方向尚无已验证的精简实现及净成本。

此反例属于原T06.3/T06.1/T08.1，未新建矩阵。诊断补丁从活动产品候选移出，完整保存在归档中的 `raw-copy-retained-repro-r0-arm64/source.diff`，**不是修复或转为通过**；其他入口全组通过不能覆盖这个已知缺口。[验证脚本](audit_live_copy.py)、[身份与结论](raw-copy-audit.json)、[完整原始数据及诊断补丁](raw-copy-raw.tar.xz)、[成员校验](raw-copy-raw-manifest.json)。

<a id="owned-terminal-delivery"></a>
## 当前实施：owned事务随原mutation完成退出（2026-10-11）

产品 `11adac3e3a66a25bca54de0e4a12583269f8f955`。先在父e6fc真实生产provider填满进程MetadataArena：8个BPP/raw/iterator组合全部在解除压力后页claim归零、事务仍为1，得到 **2/8/0**（含init/cleanup）。原orphan只负责取消页、没有承接owned transaction，是实际生命周期缺口。

最终将batch的owned事实移入原mutation，最后release和原orphan retry共用私有cancel→owned abort；成功终结解除责任，拒绝保留原scope。manager交付仍先完成，不进入orphan。普通finish/cancel归还无消费者facade的shared引用；真实lease仍保有原batch及其线程槽，最后锁外释放后退出。物理取消拒绝后不遗留expired弱槽；公开finished facade仍存活也能自动恢复并重新准入。显式OperationDelivery因仍有真实交付消费者保留原引用。

删除batch的owned副本、Backend独立abort wrapper、忽略abort返回的政策、default三个重复退出分支和无消费者facade保活。default-only及scope准备失败的新空事务不产生像素proof/lease/prepared-reader债务，采用原局部同步退出，不为形式统一分配空mutation。default实际拒绝/重试验证operationSessionsCreated不增加。成功owned提交直接进入原publication核心，不再从公共Store入口扫描同事务orphan；公共入口保留其真实多scope消费者。事务身份复查只在abort拒绝后执行，不给成功路径增加重复查询。

最终r6双架六组各 **5011/0/0**，合计 **10022/0/0**：Reference1019、CpuMutation1721、manager1621、Physical398、Resident221、lockless31。覆盖压力下raw最终归还/iterator放弃/失败finish保留facade、root预算拒绝、default-only拒绝/重试、持live native lease时阻止新batch及最后归还后自动退出，原取消/兄弟owner/foreign锁窗继续通过。独立当前/upstream公共探针42点相同。生产5文件 **+128/−53，净+75**；测试2文件 **+124/−0**。owned字段移动与scope布局变化、必要失败终结费用未定价，无新队列/owner目录；这是保证增量，不能称为纯去重或时间收益。

证据边界：16个压力业务行中12个私有cancel行在压力观察点仍为页/事务1，解除后无新输入归零；4个seal后root拒绝行当场已abort为0，**不冒充持续abort拒绝的直接证据**。r5 ARM5010通过后又修正真实lease/finished facade责任，以r6身份作为最终资格。初次命令缺cmake、两次私有接口访问编译失败、最初8个真实失败及全部中间通过均保留。[源码/两架库/upstream与删除审计](owned-terminal-audit.json)、[全部原始尝试](owned-terminal-raw.tar.xz)、[成员校验](owned-terminal-raw-manifest.json)。

四raw producer的提前warm替换、history交付和完整同义性能仍按原T矩阵推进；M6/M7/M8仍0/3。

<a id="local-adapter-delivery"></a>
## 前置实施：原写集交付 working adapter（2026-10-11）

产品 `e6fc6d687c` 保留原 mutation 的 D/claim 到 root 结果和 adapter 完成；失败先冻结借用，锁外失效实际 D 缓存，撤销 B 个实际新插入，再尝试物理取消。B 复用冷准备的原 PreparedTile/key/GC 能力，两种 hash 明确区分 prepared/inserted/consumed；没有第二份 D、全量恢复或逐 warm presence 查询。成功的匹配 cache 保持 ready；`finish()` 返回即释放其准入，即使公开 facade 仍存活。manager 组合指针不进入 Store orphan。

删除 getTile 冷 miss 的 OperationDelivery、两层回调编排和无 consumer 的单页 installLocked；原 claim 与 hash/extent 自身锁覆盖交付，不在共同 helper 重取 manager gate。生产8文件 **+173/−68，净+105**；测试2文件 **+37/−8**。这是取消保证补齐，B 实际容量、GC 准备、D lookup/barrier/version 判断及 claim 延长都收费，净时间未知，不宣称净简化或 PageStore 性能提升。

双架六组各 **4993/0/0**，合计 **9986/0/0**：Reference1019、CpuMutation1721、manager1603、Physical398、Resident221、lockless31。父67ae的28个取消失败已关闭；真实 scoped cancel 与 raw publish 的8个最后归还锁窗、foreign unlock、两 hash 的winner/未安装/重复撤销/表地址复用，以及已finish但facade仍存活的再次同页准入均通过。独立当前/upstream公共探针42点相同。r0构建失败、r1诊断observer未收到事件导致的4个失败及后续全部尝试保留。[源码/运行库审计](local-adapter-audit.json)、[原始归档](local-adapter-raw.tar.xz)、[成员校验](local-adapter-raw-manifest.json)。

原T06.3/T07.1仍未全关：真实物理取消/abort拒绝后的owned transaction责任待证；四个raw refresh caller仍保留，其中旧copy会在root前删除/替换已有warm wrapper，不能由B新插入逆操作覆盖。必须继续迁移实际producer，才可删除旧恢复。commit/checkpoint/purge/clearAll及最终同义性能仍属于完整范围，M6/M7/M8仍0/3。

<a id="owned-publication-migration"></a>
## 当前实施：独立 owner、派生 extent 与普通读发布点（2026-10-11）

产品 `67ae4a8caa2d95d3184032dd841c82b3ffcc6353` 实施下方竞争实验所选方向。普通读选canonical，显式history保留overlay；无history的独立operation提交自己的transaction，不再因别的owner拒绝而撤销。原合并页树决定configured derived extent，保留真实元数据冲突及extentRevision。raw借用共用原batch，最终引用在Tile barrier外释放。

删除匿名三状态、匿名overlay选择/stale-selector政策、raw独立mutation/transaction/dirty/终结序列，以及owned commit/abort的publication写锁、Store→Publication锁参数和条件解锁分支。Store activeTransactions直接承担冷准入事实；没有新owned计数/目录。transactionMutex仍保护history切换，不能一起删除。

原读/clone断言迁到实际seal旧current、root接受新current及adapter完成后新current；旧exact view、独立线程和clone两观察点仍检查。16个真实root预算拒绝控制全部通过；最后raw unlock的4个真实root锁窗通过。依赖旧匿名cohort的4个scoped root锁窗退出，实际本地取消锁窗尚待新交付实施后验证。

同源六组双架各 **4961/28/0**：Reference1019、CpuMutation1721、manager1571/28、Physical398、Resident221、lockless31。所有失败仅在local adapter取消32业务组合中的28项；这不是完整候选合格。另有213项定向检查通过；同一公共探针分别编译、链接当前及冻结upstream，七类42观察点逐项一致，运行库和源码已绑定。

生产12文件 **+200/−254，净−54**；测试3文件 **+420/−25**。增加raw控制块和独立提交的费用仍待完整同义测量，不声明PageStore速度提升，M6/M7/M8仍0/3。新轮明确不继承旧批通过总数；r0构建、r1构建/定向/全manager、六组r1错误可执行名（未启动任何测试）、六组r2双架及公共探针全部保留。[可复算审计](audit_owned_publication.py)、[结果及源码身份](owned-publication.json)、[101成员原始归档](owned-publication-raw.tar.xz)、[成员校验](owned-publication-raw-manifest.json)。

剩余D/B恢复能力、原PreparedTile复用、内部seal取消、caller不同锁域、manager不逃入Store orphan及abort(false)责任，已原位落到[蓝图§17.6](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#owned-publication-migration)。四个raw refresh caller在实际取消缺口关闭前保留；不能先删恢复，再把失败当作预期行为。

<a id="cancel-owner-review"></a>
## 冻结竞争复审：隐式共享扩大失败范围，不能只加回滚（2026-10-11）

该轮按`algorithm-cost-optimization`和`cohesive-refactor`检查完整终结责任，并实际比较两种上层划分。**下一实现选择显式operation/iterator/history决定事务分组，普通读以canonical root接受为发布点。** 该轮结束时竞争原型冻结并撤回，生产工作差集保留raw终结统一候选，产品HEAD为75dc8fca5f。之后的实施见上方当前批次；冻结失败不改写为全包通过。

已保留的清理：`KisTiledDataManagerPageStoreLease`不再自持transaction、ownedMutation、dirty和独立seal/cancel/commit序列，统一到原`WriteBatch::Private`。原shared control block由Tile最后unlock交到栈上，在swap barrier释放后终结；实际guard归还/cache移交仍在原锁域，直接lease.finish仍同步。没有新增延迟队列；unscoped raw新增一个原batch控制块分配，必须收费。生产6文件 **+125/−140，净−15**，未提交、未作时间收益声明。针对性53/0/0；同一生产候选完整manager双架各 **1531/28/0**，28失败全部属于尚未关闭的local adapter取消。扩充真实返回Tile的lock/read后，已有页也会读出已取消的0x71私有缓存；此前r2只读canonical所称已有页通过不能外推。

上层竞争实验使用同一24行业务用例（4种BPP × cold/warm × 成功/私有放弃/真实root预算拒绝），测试不改预期来迁就算法：

| 算法 | 业务结果（不含init/cleanup） | 归因 |
|---|---|---|
| 原隐式共享 | 16通过、8失败 | 本操作最终root准备拒绝，把此前返回Succeeded的兄弟operation一起撤销；补回两边hash也无法修复丢失的成功业务结果 |
| 每个原owner独立事务 | 20通过、4失败 | 兄弟效果保住；cold本操作本应成功，却因兄弟已扩大extent而触发surface整字段假冲突 |
| 独立owner + 原root bounds派生extent | 24通过、0失败 | 最终页树直接给出合并extent；无新页集合或全量导出。额外4个控制覆盖原本无surfaceChanges、交错增删、双删除和default真实冲突 |

原型第一版还暴露history extentRevision从4退到3，已按原overlay/current revision修正，失败保留。完整r3双架各manager **1441/146/0**、Reference **1018/1/0**：manager失败分为实际local取消28、seal读可见16、seal处clone16、fresh read锁窗80、旧共享最后client触发root4、合并提交次数2；Reference剩余1为匿名lease合并后的manifest时点。除次数断言外，这些都要重新验证旧/新一致视图及交付锁序，不能一概称作“测试过时”后删除。尤其未成功root提交的overlay不应自动等于普通current，但迁移发布点必须同时迁移read/clone和工作adapter，不能只删selector。

预测仅限机制：真正独立且时间重叠的r个操作，root提交可能1→r（已观测控制1→2），显式iterator/history分组内不因此逐页提交；原树bounds单surface为O(1)，不代表整笔提交O(1)；原surface存储、冷adapter退出能力、局部D缓存恢复和raw控制块均计入最终费用。**尚无净毫秒或相对upstream收益，M6/M7/M8仍0/3。**

[原33项及本次修改/删除次序](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#cancellation-terminal-review)、[结果/运行身份审计](cancel-owner-review.json)、[审计脚本](audit_cancel_owner_review.py)、[全部尝试及竞争补丁](cancel-owner-review-raw.tar.xz)、[成员校验](cancel-owner-review-raw-manifest.json)。首个错误selector调用、原共享反例、独立原型失败和撤回后的验证均保留；旧cancel-diagnosis归档未覆盖。取消/clear/commit/checkpoint/import、真正失效分支删除和最终同义性能继续属于原重构闭包。

## 首次取消反证：冻结75dc检查点（2026-10-11）

产品仍为75dc8fca5f，只有反测试验新增测试代码，尚未修改生产实现。`cancel-full-repro-r2`在ARM/x86各执行32业务组合：缺页的16项全部失败，已有页的16项通过；连同init/cleanup为每架 **18 passed / 16 failed / 0 skipped**。实际覆盖主动放弃、metadata硬预算耗尽后的cache交付拒绝、overlay已接受后的root准备预算拒绝。末两类使用真实分配拒绝，root类只由原诊断observer确定耗尽预算的时点，并未替换commit结果。

取消后canonical已回到0x13，但hash/extent残留。再次公开getTile(writable)没有建立显式presence，随后改变默认色会得到0x29。该结果既说明当前warm存在假设不完整，也说明仅在私有cancel后补回调不够：root拒绝时原session已经sealed/detached、writes已清，已接受事实归原transaction。兄弟operation和foreign最后unlock的风险来自源码推导，本批尚未执行验证；不把这些推导计作已复现问题。

[原蓝图§17.5及代码责任索引](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#cancellation-terminal-review)已修订；T04.10/T06.3/T07.1保留未完成状态，继续检查匿名共享是否语义必要和最小完整终结责任。成功路径的42点同义证据与本次32组合分别报告，不能互相覆盖。[诊断身份与所有观察](cancel-diagnosis.json)、[审计脚本](audit_cancel_diagnosis.py)、[全部尝试及测试补丁](cancel-diagnosis-raw.tar.xz)、[37成员校验](cancel-diagnosis-raw-manifest.json)。r0与r1分别冻结最初8项失败及增加cache拒绝后的12项失败，不混为修复后通过；没有统计性能或M6资格。

## 最新清理：legacy clear 的无效接线（2026-10-11）

最新清理 `75dc8fca5f006b546f5774d5b2aa4a3b99318e46`（父73a9）删除 legacy clear 中恒空的 PageStore batch、无效 replace/finish 及 bridge/read-ready 接线。operational native 分支已经返回；构造失败后的真实 legacy fallback 和默认 backing 缓存仍保留。空 batch 析构原有的失败报告责任改由函数内 scope guard 承担，真实预算耗尽拒绝及释放后重试通过。生产 **+9/−16（净−7）**，测试 **+26/−0**；没有新增持久状态或恢复协议，不计 PageStore 性能收益。

`clear-cleanup-full-r1` 的受影响 manager 测试双架各1503、合计 **3006/0/0**，独立 upstream 七类 **42观察点相同**。该包不声称重新运行六组9784；那是父73a9的冻结验证。源diff/运行库和删除审计见[身份](clear-cleanup-audit.json)、[全部原始记录](clear-cleanup-raw.tar.xz)、[成员校验](clear-cleanup-raw-manifest.json)。构建r0仅为初版，加入失败职责与反测后的r1才是最终候选；完整管线余项保持开放。

## 冷准备、真实借用和私有完成

产品提交 `3f2826d4647b75a49488ad88b8f499d214af62f3`，父版本 `8198c36ed722030edae715b7423554036bf1bcf7`。原20fd候选未合入。实际测试时为父HEAD加未提交补丁；[可复算审计](audit_core.py)证明双架测试保存的完整diff与该提交逐字节相同，结果见[core-audit.json](core-audit.json)。

原entry仍为唯一阶段记录：`MutableReady → Exposed → PrivatePrepared → AliasAccepted`按实际动作前进，最后两步分别接受。preflight直接使用共同冷准备，不再临时构造公共guard或伪装Exposed。完整最终Fresh输入直接初始化受保护backing并AdoptPreparedWrite；普通overwrite仍允许再借用，真实handoff仍持必要writer/pin。新增结果类型只在栈上，无第二owner、队列或持久布尔字段。

删除 `preparationOnly`、`recordPrepared`、旧`Prepared`阶段和完整final的无消费者guard；alias重试不再从writable有效性猜测阶段。生产5文件 **+383/−220**，测试2文件 **+188/−9**。生产净增163行来自将原全体beginWrite混合策略拆成共同冷准备、原热借用和独立最终输入，以及两次真实接受的表达；没有通过新增全函数模板扩大热路径分派。完整管线尚有待删责任，不将此净增描述成全局复杂度已下降。

双架构最终运行均为CpuMutation 1694、manager 1322、PhysicalClaim 398、ResidentRead 221，通过合计 **7270，失败0，跳过0**。实际image及依赖身份逐进程保存，末尾再次验hash。新增反例覆盖最终输入的五种终结、预算真实拒绝/重试、alias前后两个接受点、强制真实handoff、旧视图及最终资源；preflight保留真实驻留pin而不计guard。通过的安全测试不授予时间收益或M6资格。

首轮测试的DYLD身份未回报，因macOS保护的arch入口清理环境；修复为arch后显式env再运行。首轮manager另有14个旧pin计数断言失败，按新完整/部分页语义更新，保留全部日志；缺类型前置声明的一次构建失败亦保留。原始失败未删除，不将这些初次过程计入7270通过。

固定parent/new/new/parent机制观察为8用例、各4个完整生命周期，四进程结果及库身份全部通过；两个重复的整数工作量逐项相同。K16/N16如下，H0/H1除注明外一致：

| 机制 | 父版本 | 核心包 | 解释 |
|---|---:|---:|---|
| Fresh / sealed pages | 1024 | 1024 | 必要私有代际未改变 |
| write pins / unpins | 1024 | 0 | 完整最终Fresh，无外部可写借用 |
| foreground version inputs | 3072 | 1024 | 每页少两次mutable输入 |
| foreground installs | 1024 | 1024 | 发布次数未减 |
| foreground sequences H0 | 2048 | 1024 | 少每页一轮 |
| foreground sequences H1 | 6016 | 4992 | 相同删量，历史工作保留 |

机制原始计时仅作诊断，不作为未插桩收益。F/P计数的预测兑现；必要preflight物理pin仍保留。旧20fd的1.186/1.360ms只属其冻结版本，不给新实现授予相同收益。完整候选之后按既定协议完成父/新、upstream及业务控制。

原始核心运行、失败构建、运行命令、runtime哈希和补丁保存在 `core-raw.tar.xz`，成员校验见 `core-raw-manifest.json`；解包后原runner和审计脚本可直接复核。外层文档不阶段化重复复制T矩阵。

## 共同overlay接受与清理

产品`4dc89bada34d746364a5eb3ed04c40f962d1c274`相对核心包迁移native seal、generic finish、conditional removal三caller。`tryAcceptLocked`仍在同一owner gate中安装；surface可失败存储准备与安装分开，保留原诊断及零分配安装验证。接受后producer先归还proof责任，`finishUnlocked`统一处置metadata候选、取得owner交接旧proof到原HistoryCollector、锁外释放整个候选与allocator retention。拒绝分支不消费producer proof。没有新字段/owner/队列，删除旧`collectRetirementsLocked`和`collected`状态、三caller清理变体；旧`tryInstallLocked`仅改名明确接受含义，不领取独立收益。

native锁窗口/顺序保持；generic/removal从“先collect再释放候选”改为“先处置候选再collect”。这两个入口增加一次短owner重取，但候选activity不必阻塞同步清理；净时间未知，不声称锁数全局下降。conditional removal缺少独占页claim，解锁后的observed版本复查完整保留；generic provider releaseAccess不重放，取消拒绝仍由activeWrites承接。三种caller的外层失败范围和诊断回调锁域不合成新策略参数。

双架四组再次**7270/0/0**，实际库/source diff均绑定提交，[审计脚本](audit_overlay.py)与[结果](overlay-audit.json)可复算。现有容量测试改由真实deferred cleanup callback保留已接受候选，覆盖满额安装、callback无owner锁、History拒绝接续和候选/控制器尾寿命。首轮1691/3/0发现空unique_ptr仍在deleter持有128B控制器尾，修正为连同deleter保活一起释放后重验通过；全部首轮失败保留在[原始archive](overlay-raw.tar.xz)，[成员校验](overlay-raw-manifest.json)。

生产3文件**+56/−51（净+5）**，测试1文件**+35/−12**。净增主要为显式完整清理合同及无锁调用说明；替代的政策只有一份，实际退出旧收尾状态。此包没有新增性能样本；整个33项范围、未插桩时间、upstream差额和业务控制继续开放。

## Operation交付和batch终结

产品`7c36dceb858b06b0dbb3ed66adc7ef21a1c34a58`：四种seal入口以局部SealMode表达终点，删除legacyFinalUnlock和retainAdmission参数的组合。checkpoint继续try-lock并允许worker迁移，普通终态继续原线程校验；adapter保留原admission直到联合交付之后，不新增持久状态。

fill/普通operation由finishOperationBatch统一选择封段、联合adapter completion及已接受batch的交付；history仍按其真实合同先安装pending adapter再归还execution，不虚构一个共同发布阶段。changed失败输出集中清空，重复execution.finish分支退出。batch与clear barrier共用原登记槽的最终撤离，保留不同取消/晚finish语义；过期weak slot仍阻止新batch进入直到原匿名client终结。source存储保留原锁外析构位置，没有把大的释放移进manager交付锁。

原`failed && !privateCancelled`分支不可达：seal失败后只有mutation.cancel确认成功才能继续；已接受seal时failed为false。因此删除privateCancelled记录及这条abort候选，真实cancel拒绝仍早退保留原owner，generic及barrier的独立abort入口仍有consumer。此推导由现有failedProductionBatchCancelsUnpublished、invalidAlias、嵌套batch、128轮foreign abandonment、clear晚unlock、checkpoint和adapter窗口测试反证。

双架四组**7270/0/0**，未新增镜像测试；生产4文件**+52/−58（净−6）**、测试0。构建前静态复核保持source析构原位置后再测，全部构建和运行证据见[审计](operation-audit.json)、[原始记录](operation-raw.tar.xz)和[成员校验](operation-raw-manifest.json)。[通用审计器](audit_package.py)的参数亦保存在audit JSON，可重算提交/source/库绑定。结构迁移不冒充净时间收益；copy交付、adapter晚失败、内部commit以及history/restore等余项仍按原矩阵推进。

## Prepared adapter与clear最终presence

产品`ccbf0bcb0db6f13bab5c87ca03936439f25ee04d`完整迁移PreparedTileUpdates的packed、cursor、clear三caller。安装改为消费已准备能力，删除晚业务拒绝、error输出和隐式locker.unlock；三个caller在原manager gate中安装、显式unlock，再发原AdapterInstalled观察。clear复用原临时presence缓冲，由fill在记录changed时同步写最终remove/replace事实，发布之前已完整；不再取publication/backend/Store锁重新解析同一组页。成功后缓冲长度与changed相同，失败两者均空。普通packed/cursor无新增presence输出或全量验证扫描。

安装不可拒绝的依据是当前完整caller闭包，而非“改成断言就算安全”：

1. packed支持坐标校验、cursor的QRegion/QSet去重、clear规则矩形与backend targets形成相同coverage；每个changed只出现一次且来自该范围。
2. 原range admission在prepareAdapter前取得，standalone由OperationDelivery保到安装后，history由execution保到pending adapter安装后。因此warm wrapper不能被同key写/删除取走；当前clear/restore/abort/trim整表屏障拒绝活动claim。tryAbort是构造外唯一换表处，原活动检查仍保留。
3. cold节点只从同一张表准备，未被别处消费；额外冷插入只产生可接受winner。chained identity不变；lock-free PreparedKey的replace在有entry/owner时无分配拒绝，migration不撤销owner，只有close或消费使其失效。原manager寿命和claim排除了这些条件。
4. 因而这里只移除manager将内部不变量破坏伪装为可重试业务失败的分支。两种hash公共接口仍对foreign、closed、consumed capability拒绝，独立测试consumer存在，不能全删。未来T04.10若改变全局屏障，必须重新证明表/节点寿命，不能沿用本条而直接删准入。

双架各CpuMutation1694、manager1322、Physical398、Resident221，以及8个hash边界函数加init/cleanup 10，共**7290/0/0**。[审计](adapter-audit.json)绑定全部实际库和source diff；hash包含migration/partial migration/close/同key竞争/address reuse及两种PreparedTile，manager包含已有联合可见窗口、屏障、存储拒绝、旧视图和K=1/64/65/257、BPP=1/4/8/16。原presence测试确认clear查询由每次1次降为0，copy仍1次；FreshReadSelection同时验证读取/旧pointer与零查询。

首轮manager有101失败：77个来自将诊断next误改为构造而丢观察通知，8个来自presence准备被提前到extent前，16个是clear旧查询次数断言。已恢复原单timer的next/锁域与extent先备顺序，更新明确被删除的查询断言后重验；没有增加第二计时器的常态代价。所有进程自然结束，无timeout/强杀；[原始记录](adapter-raw.tar.xz)和[成员校验](adapter-raw-manifest.json)保留首轮错误和全部构建。

生产3文件**+62/−32（净+30）**、测试1文件**+6/−2**。新增的是producer输出事实及完整失败输出处理、显式锁/诊断边界；原presence容器复用，无新owner/cache/登记表或逐页再验证。零changed仍沿原scratch预备合同，fill多了可选输出的局部分支；净价待最终候选。此机制不在纯K16 packed热路中命中，不拿其计数领取K16时间；copy的专有refresh和history/restore三rebuild仍开放。

## Copy的准入、固定源与共同交付

产品`081afa7072adeb6035c80dcfa211ca0d8603e097`将copy接入原managed range、finishOperationBatch及PreparedTileUpdates。准入只覆盖原稀疏裁剪选中的K页，贯穿资源准备、像素、publish、adapter安装及局部storage析构。完整alias/remove和partial写直接报告changed及最终presence；copy不再发布后调用refreshPageStorePages，不再取presence查询或晚建wrapper。连同无consumer的pageStoreRefreshCapacity、三参数refresh重载一起删除；单参数refresh仍有tryCommit消费者，不冒称已删除整个history尾路。

源和目标不是相同选择责任。第一实现沿用两份提前固定view，在双架原安全组通过后，新增真实range-wait反例却得到错误像素：copy源/旧目标同为0x31，先行writer发布0x71，copy等待结束后仍按旧alias判no-op，最终0x71。`copy-full-wait-repro-arm64`保留3通过/1失败。这是本包引入等待后暴露的设计缺口，不能靠更多原测试通过覆盖。最终源仍一次固定；目标预先只读surface几何，原范围准入成功后、beginMutationBatch之前才捕获唯一target view，按当时版本判断no-op。总target capture仍1次，无K次逐页再锁，也不为新建匿名事务生成空overlay capture。

目标边界只核对**原请求在新target view下的实际裁剪矩形**：选中范围变化在像素前拒绝，避免遗漏新页；请求外extent或无关revision变化不拒绝。该局部拒绝不fallback、不重放、不无界扩范围。先按整个surface几何比较的草案也已收窄，避免不必要的全局一致保证。新增一个surface查询、一次矩形重算和K页准入/预备成本，净价未知；它们是必要交付/并发保证增量，不是纯删量。

最终双架各manager1369、CpuMutation1694、Physical398、Resident221，共**7364/0/0**，source diff与实际库绑定见[审计](copy-audit.json)。复用BPP1/4/8/16、K1/64/65/257、source并发变化、oldData、self-copy、负坐标、不同默认值、alias寿命和回滚测试；新增47行数据/架构包括原reader可见窗口中的partial/rough copy、五种adapter barrier、准备拒绝及六种等待/取消/内外边界反例。presence测试copy查询从1降至0；固定source和原稀疏选中页数/总capture数保持。hist persistent无显式owner的copy继续按原合同拒绝。

首轮4个失败是旧“先写再取消”计数及不具显式owner时应提前拒绝的测试预期；首次构建另有测试使用错误clear重载的编译失败，均保留。第一版双架通过与随后真实并发反例、最终修复双架通过分开归属。[全部原始记录](copy-raw.tar.xz)、[成员校验](copy-raw-manifest.json)涵盖中间通过、失败和构建。

生产4文件**+113/−48（净+65）**，测试2文件**+138/−44**。净增主要用于补齐原copy缺失的完整范围交付、并发选择和生产presence输出；复用原owner/claim/容器，没有新持久状态、队列或第二权威。此包不能领取K16 packed write收益；原33项中的内部commit、history/restore/trim/read失败尾与最终同义性能仍未完成。

## 内部提交：直接借用原 publication delta（2026-10-11）

产品 `ce903fe3e91dd4826d5d2e14374771da8dd2e9ac` 完成 T02.3/T04.4–5/T04.8：原 PreparedTransactionState 更名并暴露为私有 KisPagePublicationDelta，容器和预算 ownership 不变；原 CommitPreparation 贯穿锁外 provider、epoch 准备和 rebase。内部 backend/memento 不再导出三容器、调用重复 isValid 或逐 proof 与自身回比。公共 commit 输入保留独立 validator，随后进入同一 commitOwnedLocked。epoch 仍生成必要不可变投影，history 直接准备原 record 的 changedPages/default/retained 输出。

空事务通过原 abort 接受，不生成空 root；活动写或无效/已结束身份仍拒绝。memento 的空/非空成功路径合一，旧 commitAndReleasePublicationLock 和 PreparedTransactionState 定义删除。已接受 commit 的 proof map 保留到 history 取得 key 后锁外释放；abort 逐项撤销并在拒绝后可续的差异有真实语义，予以保留。clone/prune/historyChangedPages/allocatedPages 仍有独立导出 consumer，不领取其成本。

双架五组 **9410/0/0**，每架 Reference 1019、CpuMutation 1698、manager 1369、PhysicalClaim 398、ResidentRead 221，源码与实际运行库绑定均通过。新增内部/外部提交的重入、锁外 provider 拒绝、rebase 及空事务身份反例；Reference 完整构建发现两个较早包遗漏的 recordPrepared 测试 caller，已迁到 recordTarget，并迁移五处私有 epoch 输入测试，未恢复旧生产签名。构建失败和修复一并保存在[审计](commit-audit.json)、[原始记录](commit-raw.tar.xz)、[成员校验](commit-raw-manifest.json)。

生产8文件 **+214/−166（净+48）**，测试2文件 **+89/−13**。可删除的是内部中间表示及回比；descriptor 保活、provider 检查、最终 epoch 投影、必要 history 输出与短门控仍计费。没有本包未插桩净价，不能用安全通过宣称 upstream 差距收敛；restore 实际差量、manager 三类 rebuild、allocatedPages 和最终全包性能继续开放。

## 恢复与最终释放：实际 root 差量（2026-10-11）

产品 `2363d824b73f34a1508c80b5e2b595ae61bba65c` 完成 T04.9 底层恢复，并修正 T04.8/T07 的历史释放前提。不是仅有旧命名问题，两条独立反例均在修复前实际失败：

- `restore-full-repro-arm64`：M1 改 A、M2 改 B，直接 rollback(M1) 后 B 的像素读正确，继续写 B 被拒绝。旧路径恢复整个 root，却只更新 M1 的 metadata 差量。
- `restore-full-purge-repro-arm64`：先 purge M2 再 purge M1，前台回收后仍占 49152 bytes，必要 current 为 32768 bytes，关闭前遗留一页 16 KiB；后台通过。M1 虽未写 B，其 before/after root 仍可能是旧 B 的最后持有者，write delta 不能限定释放范围。

恢复现在直接比较原 current/retained 两棵不可变树，按序游标跳过相同指针的完整子树，输出到原 preparedCommit.restoreTargets；不构造中间 manifest 或第二 delta。版本相同的页不进入 metadata candidate，重复恢复同内容的新 epoch 也得到零页差量。默认值变更仍处理原 directory 中相关虚拟默认页、重试 registration revision，并保留原 head/activity/provider/retained 拒绝及共同原子安装。一般最坏树遍历 O(N+M)，删除键解析另计 O(D_remove log M)，共享结构可减访问；未宣称所有旋转都达到 O(D log N)。动态存储按实际差量 capacity 和增长暂峰收费，固定游标栈也计入执行成本。

释放统一到原公共 releaseSnapshot 的 history work index 扫描及重试政策。后台原本同时请求 all 和 delta 的重复通知退出；前台可能需要访问更多真正的历史工作，是修复成本。before/after 独立 token、同 token 一次释放、部分拒绝续接不变。删除 `restoreRetainedEpochDelta`、`copyPageVersions`、`releaseSnapshotDelta`、`releaseSnapshotLocked`，以及 memento 的 changedPages/default 标记、commit 对应输出和 purge/close 两份 lambda。此前 commit 包判为“必要输出”的字段经真实 consumer 反测后被证伪，现已完整删除；backend 的 prune/dirty 输出属于另一责任，仍保留。

最终双架五组 **9438/0/0**：每架 Reference1019、CpuMutation1712、manager1369、PhysicalClaim398、ResidentRead221。新增跨节点后续写、BPP1/4/8/16×K1/17/65 的增删改/旋转/重复恢复，以及前后台非自身 delta 页回收；保留 late reader、head 变化、active transaction、默认注册重试、预算拒绝等原测试。首轮及第二轮的各12条旧计数断言失败全部保留，最终计数对账为 restore 版本输入 **3→2**、目录枚举 **2→0**、实际安装仍 **2**。源码/运行库双架绑定、全部失败和原始过程见[审计](restore-audit.json)、[原始记录](restore-raw.tar.xz)、[成员校验](restore-raw-manifest.json)。

生产10文件 **+98/−136（净−38）**，测试 **+132/−25**。确定删除每个 memento 的一个持久 key 列表和标记、提交时 D 个 key 的复制/容量准备及上述重复分支；树差量生成与前台完整回收净价未知。manager 稀疏交付、trim/read 失败尾、枚举及最终父/新/upstream 性能尚未关闭，M6 不晋升。
## 读入失败的共同取消与前置拒绝（2026-10-11）

产品 `ee8a165fc7` 将 `read` 的真实解码/提交失败接回 `tryAbort` 原协议：先准备基线索引、接受取消后安装；失败保留原 history/default backing/index，仍可由原提交或关闭推进。两个原局部候选合并为同作用域存储，仍在 manager gate 外析构，不增持久 owner 或队列。空流、空头和坏头改在创建 history 前拒绝，直接删除其历史创建/取消工作；不改变 clear 后恢复点。删除 read 的三份提前取消及不检查取消结果便 rebuild 的尾路，rebuild 当前只剩 trim consumer。

双架六组 **9628/0/0**，每架 Reference1019、CpuMutation1721、manager1424、Physical398、Resident221、lockless31；新增 BPP1/4/8/16 × 五种失败。实际压缩页先解码成功再坏尾，取消成功后基线为空；真实 OperationDelivery 仍持范围准入时取消拒绝，原 wrapper/history 保留，释放准入后原提交继续。首轮4条拒绝断言失败来自夹具错误：legacy raw writer 的原语义允许取消，并非必须拒绝；改用真实准入，不改变产品拒绝政策。全部失败、定向和完整回归均归档，[身份审计](import-audit.json)、[原始记录](import-raw.tar.xz)、[成员校验](import-raw-manifest.json)。

生产 **+75/−69（净+6）**，测试 **+77/−0**；新增存储类型只包原两个候选，公共/导入两入口共用开始与取消责任。失败恢复仍需基线 N 页全表准备，没有 CPU 净价或纯 D 声明。导入私有 history 的替代、提交 prune 后交付归原 T04.10 后续审查；本包不启用匿名替代、不授 M6 资格。

## 枚举：同一事务基根与有序归并（2026-10-11）

产品 `0e55a60932c2d50c099e566f08f514b5f113244c` 完成 T04.11。Store 原 owner 一次验证事务身份、固定真实 base root 并投影本 surface 的 D 个 proof/removal key；解锁后直接遍历原不可变树，归并到最终全量输出。删除 N-version manifest、N-key 中间表、完整 prepared-set 导出和逐项 find/erase；只排序 D 个输入，复杂度由 O(ND+N log N) 收敛为 O(N+D log D)。树访问、D-key 存储及输出 reserve 上界仍收费，不把机制删量换算成未测毫秒。

首版只改归并、保留 current root，被 `enumeration-full-base-repro-arm64` 证伪：独立 Store 事务推进 current 后，单页查询仍不包含该页，枚举却包含。最终两者同用原事务 base。测试继续到 rebase 时，又发现夹具两笔事务同时扩 extent，应按合同冲突；预先建立 bounds 后才构成真正不冲突的 rebase，产品规则未改变。所有中间通过与两次失败保留。

最终双架五组 **9456/0/0**，每架 Reference1019、CpuMutation1721、manager1369、Physical398、Resident221。新增 N1/17/257、D0/1/N、增删改/撤销、commit/undo/redo、选基/rebase，并确认零 manifest 导出。生产7文件 **+72/−37（净+35）**，测试 **+103/−0**；没有新 owner、队列或持久状态。[源码/运行身份](enumeration-audit.json)、[完整原始记录](enumeration-raw.tar.xz)、[成员校验](enumeration-raw-manifest.json)。manager 交付和最终同语义性能仍开放。
## 恢复交付及语义删除的准备闭包（2026-10-11）

产品 `faffef592cff360f4b7baa0ae53fd129f97e3bd1` 将 manager restore 从接受后的全量销毁/重建迁到接受前的完整准备，保留未变化的 wrapper。全组通过后仍追出了三条影响设计的反例，均保留失败记录：

- `restore-delivery-full-r0-arm64`：已有 `testUndoingNewTiles` 失败。writable intent 可以扩大兼容 extent 而从未改变 root，因此仅用实际 root D 会漏删 wrapper。
- `restore-delivery-full-presence-repro-arm64`：backend 已发布 page5、manager 缺 wrapper，再创建多余 page9；两边数量相等而集合不同，恢复后实际1页、应为2页。仅扫 hash 删多项仍不足。
- `restore-delivery-full-lock-repro-arm64`：已有 Tile 在 swap barrier 内等待真实 backend read selection，恢复持 backend/publication 锁进入 adapter 后环等；12秒 watchdog 仅终止本批记录的子进程，exit−15、无Totals，不算通过。修正后单测及双架全组通过。

最终管线借用原 retained root 和原 preparedCommit 的实际版本差量，不增加持久索引或第二 delta。manager gate 内、canonical 接受前，遍历原 hash 对目标 root 查多项，再直接遍历 root 查缺项；只有实际多项/缺项进入原 PreparedTileUpdates 候选数组，hash iterator 结束后才获取准备锁。原 root visitor 不导出 manifest。cold wrapper、extent、删除用 map key/GC action 和 default backing 均先备；拒绝不交付。成功后先释放 backend mutex/publication gate，再在原 manager gate 消费删除/缺项，并只对实际版本 D 失效缓存。已消费 token 不再安装，旧候选/default 在 manager 锁外释放。默认目录重试不重做这份固定目标准备。

完整集合核对是当前兼容语义的必要成本：准备最坏 **O(H log M + M + S log S)**，H为原hash页数、M取目标整棵root节点上界、S为实际多项/缺项候选数；另付原root差量生成及D交付。确定删除的是原全量枚举输出、H个旧wrapper的无差别清除及M个wrapper的重建，保留项不再分配重建；不是删除所有N规模遍历。没有证据证明 manager restore 已为纯D，也没有本包CPU净价。

静态锁/分配审计还发现此前 adapter 的删除仍调用 `deleteTile → QSBR::prepare/map.erase`，会晚分配并可能参加迁移。两种hash的原 PreparedTile 现在表达 Present/MayRemove/Absent；发布前准备原 key/action，交付用原 PreparedKey 交换并交给原GC队列。没有新回收owner/队列。旧 `prepareMissingTile` 定义及caller同包迁走；clear/copy 同步使用准备删除。producer传递准入后原view的default比较事实，非默认fill、不同default的copy及partial页不准备删除。相同default的完整copy仍按可能删除上界收费；候选字段/容量、GC动作和少量门控增量不能填零。

最终 `restore-delivery-full-r4` 双架六组 **9588/0/0**：每架 Reference1019、CpuMutation1721、manager1404、Physical398、Resident221、lockless31。覆盖BPP1/4/8/16×N17/257×default/intent、跨历史节点、同内容新epoch、晚默认注册、保留旧读者、拒绝不安装、独立backend页补齐、两hash迁移/同地址重建/重复消费/晚插入。源diff和运行库身份双架一致；所有编译失败、中间通过、语义失败及有界环等见[审计](restore-delivery-audit.json)、[原始归档](restore-delivery-raw.tar.xz)、[成员校验](restore-delivery-raw-manifest.json)。

生产14文件 **+309/−83（净+226）**，测试3文件 **+186/−8**。净增用于补齐完整集合、删除准备和锁序保证，不能声称总代码复杂度已降低。该包时 restore 已不调用 rebuild；其余迁移见后续 import/trim 包，不能将该冻结检查点当作当前 consumer 状态。

## trim 与索引集合核对收敛（2026-10-11）

产品 `e03742b0ef30667d88ed955dad525cd6d6616eb1` 完成最后一个 rebuild caller。trim 复用原 allocatedPages 的有序集合准备 adapter，原 TrimPage D 项直接借给安装；原 OperationDelivery 持 batch 到候选锁外释放。未变 wrapper 保留，只对实际 partial D 失效缓存，消费预备删除和实际缺项。删 `rebuildPageStoreIndex` 定义/声明/全部调用、重复线程 batch 检查及有序过滤后重复 sort；全局活动写入屏障仍保护完整集合交付，不因删 rebuild 而撤销。

restore/trim 共用集合准备：先穷举唯一目标集合 N，逐项确认已有 wrapper 或准备缺项 M。此后 H = N−M 才证明没有多项，可省去反向扫描；不相等则遍历原 hash 查目标集合并准备删除。原“数量相等、集合不同”反例继续通过，包括 trim 的 canonical D=0、但需删除 intent 并补 backend 页的情况。普通一致集合只做目标遍历及 N 次 hash 查找；最坏仍有 H log N + N + S log S，restore 的树遍历用完整 root 上界。没有 N-key 新副本或持久第二索引。

双架六组 **9694/0/0**：每架 Reference1019、CpuMutation1721、manager1457、Physical398、Resident221、lockless31。新增 BPP1/4/8/16×N17/257×history×实际变化、冷缺项/多项、未变 wrapper 身份及持有旧读者；实际超出兼容坐标的 canonical 页在准备时拒绝，验证 head、generation、索引均未改变，移除阻碍后可继续。原嵌套 batch、foreign admission、失败及 restore 反例保持。构建 r0 的新测试 API 拼写错误已修，全部定向/完整记录保留。[审计及删除检查](trim-audit.json)、[原始记录](trim-raw.tar.xz)、[成员校验](trim-raw-manifest.json)。

生产 **+138/−80（净+58）**，测试 **+84/−1**。增加的是接受前完整准备和共用集合政策；确定删除全量销毁/重建及重复检查/排序，不将 N 遍历说成已消失，也不以净删某个 helper 代替总复杂度报告。commit/checkpoint 的历史差量与 prune 交付、最终父/新/upstream 性能和全矩阵审计仍开放，M6 不晋升。

## 删除不合法的自动默认页裁剪（2026-10-11）

产品 `1249396fa8203570df42ee031eb9c946a45394d9` 修正了上一版蓝图的前提：不能因为prune有consumer就保留其责任。同一份[公共API探针](history_semantics_probe.cpp)分别编译链接冻结upstream和当前库，证实显式默认写必须建立页，并跨redo及后续默认色变更保留原字节。旧实现对空页packed写错误no-op，已存在页则在commit自动裁剪；随后把原来显式写入的0x13变为新的默认色0x29。显式clear(default)才应移除页。

本包删除`pruneDefaultPreparedPages`定义/声明/调用及整个扫描责任；packed no-op同时要求页已存在。fallback也修正同一错误，并复用原read selection返回presence，无第二查找。fallback修复是通用语义修复，不计PageStore性能。没有新增alias API、存在账本或恢复框架。生产 **+17/−77（净−60）**，测试 **+84/−5**。

最终双架六组 **9750/0/0**，每架Reference1019、CpuMutation1721、manager1485、Physical398、Resident221、lockless31。BPP1/4/8/16×部分/整页/覆盖/显式clear×普通/persistent验证写入、commit、undo、redo、改默认色，并断言commit不再增加capture。独立公共探针r3的四类写入/clear **20个观察点均与upstream相同**。新增的第五类“只getTile(writable)、不借像素”仍有redo extent和改默认色两处差异，明确保持开放；本包不声称全入口同义。

所有失败保留：targeted-r0的16条揭示本分支fallback不能直接当upstream oracle；full-r1的40条来自旧测试把显式默认packed写当无工作，按独立upstream事实修正，native cursor未访问目标仍为空；build-r2为新测试QStringBuilder不能直接toHex，r3已修。见[精确源码/运行身份](history-audit.json)、[所有探针、失败及最终通过](history-raw.tar.xz)、[成员校验](history-raw-manifest.json)。公共探针采用相同源码和各自真实头文件/运行库，后续可用[运行脚本](run_history_semantics.py)复现；原始comparison.json保留两处尚未修复的差异。

可删除量：每次进入旧prune的commit省一份prepared-set导出；proof非空时再省一次overlay capture、本surface D个proof的descriptor/ReadPage以及实际比较字节。非默认页可能首像素即退出，不能按全页扫描领取收益。修复此前被错误跳过的显式默认写会增加必要metadata/页成本，净时间未知。公开purge(area)的显式裁剪继续保留并审计交付；不为无效自动裁剪建设新adapter框架。M6不晋升，完整候选父/新、同语义upstream和业务控制仍待实测。

## writable缺页的显式presence（2026-10-11）

产品 `73a9fde6b3dfe7a76724d6797b1470233b7de4a1` 删除“公开writable miss只建wrapper”的错误分支。冷getTile在原session取得legacy key准入后，直接从原entry/transaction判断presence，先准备原wrapper/key/extent，再以原manager默认backing建立alias；已有显式页/私有结果不覆盖。已有iterator/batch借用原session，不新增client、不提前seal；独立调用沿原finishOperationBatch与OperationDelivery交付。没有新持久字段、存在账本、可写guard或全表补偿。原replaceFullTile的源缓存/alias政策移到原batch共享控制块，两入口共用，未复制第二source目录。

最终双架六组 **9784/0/0**，每架Reference1019、CpuMutation1721、manager1502、Physical398、Resident221、lockless31。新增BPP×独立/批次/批次实际写、立即改默认色与clone、重复取得、原准入阻挡时不建wrapper、释放准入后从已存在彩色canonical页重试、冷准备坐标拒绝仍保留同批先前工作。未借像素时零writable pin；同批后续真实写复用原entry，只准备一个CPU target。alias仍有真实metadata版本，CPU generationsReserved不含alias，不能将此计数为零解释成零版本成本。

公共探针r1扩大到七类 **42个观察点全部与冻结upstream一致**：默认packed/覆盖/clear、公开writable无借用、无history、commit前改default及clone；运行库SHA与最终双架库一致。原r0的25点也全部相同。所有失败保留：trim旧夹具改成明确friend故障注入；旧错误presence/no-allocation/提交数期望按独立语义修正；新CPU计数分母、编译误插入及误调用旧可执行的失败资格明确标注；x86即时pageVersions受排队回收影响，移至既有drain后的实测点再完成双架验证。[源码/库及通过审计](intent-audit.json)、[全部原始记录](intent-raw.tar.xz)、[成员校验](intent-raw-manifest.json)。

生产 **+139/−32（净+107）**，测试 **+117/−16**。这是补齐同语义能力的增量，不是等价去重净简化；冷缺页的alias、原source捕获/缓存、索引准备及无scope时独立提交均须计价。显式presence是必要事实，当前发布粒度仍只是可构造方案，不是已证明的算法下界。没有本包净时间收益结论。修复源头后继续按T04.10/T06.3审查batch取消、旧raw恢复与完整集合扫描的真实依据；不能单凭friend人为不一致要求所有正常路径永久付N扫描。父8198含已发现语义缺陷，最终父/新需逐fixture证明同义或另冻仅修语义的父对照，不能只比最终像素checksum；新/upstream仍是基础性能主证据。
