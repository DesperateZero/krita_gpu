# 读写前台：删量成立，CPU未通过，主线需上移到操作协议

**后续研究：** 用户已将读写核心重写设为最高优先级；[原蓝图§19.20](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#read-write-converged-protocol)进一步选定私有输出到接受时直接安装版本、合法旧槽代换、64B facts的范围exact读能力及失败/预算协议。双架有限检查702/0/0属于设计依据，生产重写未实施。本报告仍冻结为d5f715实测，不把新设计或预算算术当作已实现收益。

2026-10-12。候选d5f71573bb21c78ecb38756802c2129f5a60d68d，比较起点02bccf1d12、固定upstream9a24ae，原13格公共fixture、arm64。候选只改变PrivateWrite metadata准备/安装，保持读写次数、像素、逻辑generation、物理claim和最终drain。它是**未验收实验候选**；读写主线没有完成，正式M6/M7/M8仍0/3、校准2/20、默认关闭。唯一实施矩阵仍为[蓝图§13](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-change-index)。

## 1. 独立确认与upstream残差

先固定4镜像块探索，再用独立8镜像块确认，每块三侧各两过程，四manager寿命与内部循环不作独立样本。估计为块均值之差或块比值均值，10000次bootstrap/seed12345，区间逐端点95%，不是联合family保证。数据与复算见[confirmation](read-write-r0/confirm/analysis.json)、[分析器](read_write_price.py)。没有删样或追加样本。

| H1 K16/W16端点 | 02bcc | 候选 | upstream | 本轮节省及双侧95%区间 |
|---|---:|---:|---:|---:|
| write指令，M | 87.9299 | 79.2130 | 6.0282 | **8.7169 [8.6161,8.8100]** |
| read指令，M | 17.6956 | 17.6980 | 5.9879 | −0.0025 [−0.0980,0.1139] |
| write CPU，ms | 5.3690 | 5.3678 | 0.3516 | 0.0012 [−1.0328,0.6904] |
| read CPU，ms | 1.4909 | 1.6399 | 0.3774 | **−0.1489 [−0.3352,−0.0180]** |
| 完整process指令，M | 148.7330 | 140.0389 | 26.5682 | **8.6941 [8.4596,9.0208]** |
| 完整process CPU，ms | 10.1648 | 10.6516 | 1.3944 | −0.4869 [−2.3095,0.7040] |

write配对指令下降**9.9134% [9.8019%,10.0131%]**；读写合计下降**8.2503% [8.1974%,8.2995%]**。write剩余额外指令73.1848M、read11.7101M；候选write仍约upstream **13.14倍指令、15.27倍CPU**，read约2.96倍指令、4.34倍CPU。比值为同批边际均值，不冒充配对节省率。不能把8.72M跨批减去上轮8.44M，就宣布已回到11c689价格。

探索write指令省8.6614M、CPU点省0.3230ms，通过事前5%指令且CPU点改善的筛选；确认只兑现了指令删量。write CPU正收益、read CPU 2%非劣、整包CPU至少0.75ms下界均未过。12个存储控制的指令非劣通过，CPU未闭case2/3/4/5/6/64/67；完整端点保留在机器账。没有因指令显著就授予产品加速资格。

本批有一个具体慢过程：confirmation index22 candidate，H1 process21.234ms，非P类指令占65.30%、非P类CPU17.3546ms；同块original两过程9.908/9.708ms、非P指令占0。它证明本批执行组成发生变化，不能仅归因锁、算法工作增加或随机噪声；也**不能由process级计数认定read增费全部由它造成**。该过程与其他样本一样计入全部结果，不作筛除、归一化或替代门。

## 2. 改动及理论/实际闭环

原普通PrivateWrite只需要新增target、增加base authority pin并安装writer，却与RecoverableWrite一样导出完整base保护、准备替换容量，再putReserved重装base。候选复用即时write delta的政策边界：compact快照只供AcquireWrite→PrepareWrite读取scalar事实；准备输出只留target；在原严格revision claim下安装target并原位增base pin。RecoverableWrite需要解绑/迁移authority，仍保留完整保护镜像。没有新增状态字段、owner、队列、缓存或第二写集。

| 预测 | 验证 | 尚不能据此认领 |
|---|---|---|
| H1主格896次复用不再重装base | [隔离数量](read-write-r0/quantity/result.json)：896次private_pin_delta；原PrivateWrite→putReserved分支静态退出 | 896次全部metadata准备或所有保护成本消失 |
| 原保护链原地保留，准备后变化拒绝 | 新增8格与完整状态机比较，覆盖20个capture token、两个replica、read lease、last-use、已有pin、晚reader冲突/重试、取消及发布 | 删除真实读者保护或放宽revision |
| 目标新增/物理claim及接受保持 | K1复用56、主格896、full clone832、单页holder892、partial224；其余格无命中 | 合并generation、公开结果或M6 alternate-before命中 |
| 指令净节省未知，探索要求write≥5% | 探索后独立确认9.91%；无合法事前指令/毫秒点预测 | “预测完全准确”或已找到全局最大可删项 |
| CPU/read/原控制应独立验收 | 本次未通过 | 用后台、总指令或安全测试替代CPU门 |

产品差集：metadata **+35/−12行**，测试+94行；共同准备对象、逐页调度和每次读视图仍存在。不是整条前台协议已经最优，也不是生产复杂度整体下降。

[源码身份/改动索引](read-write-r0/source-index.json)与[101过程、语义和原33×6复核](read-write-r0/verification.json)绑定本地提交d5f71573bb；[351文件原始包](read-write-raw.tar.xz)及[逐文件SHA清单](read-write-manifest.json)保存构建、所有样本、初始失败、数量和安装日志。归档不含二进制，原/候选库在本机分别保留并在机器账记录哈希；不宣称仅凭归档可跨机器重现相同二进制。

## 3. 诊断能力与验证边界

[前台指令观察](read-write-r0/diagnosis/results.json)固定25过程：1计数＋4镜像块×6。H1普通write约87.838M、派生off88.413M、观察on140.119M；read17.754/17.877/35.616M。观察明显增费，内部exclusive桶只定位责任，**不作为原库单价或可删预算**。前台观察器线程局部，其他线程不记入该桶。

同一计数用例write阶段64次capture，1920次capture保护转换；read阶段64次capture，2048次保护转换、1024次binding冷发现。这里读写各1024页访问；write前比较并不等于真实外部reader。源码还显示每次PrivateWrite以单页通用候选完成，而owner、transaction和operation共有事实反复经过准备边界。先问为什么这些工作被生成，再优化每次调用。

本轮101个公共fixture过程正常完成：诊断25、三方capability3、探索24、确认48、数量1。candidate与02bcc的69格能力结果相同；upstream的坏尾导入52–55沿原差异单列，13个价格格同义。没有新业务价格、真实峰值/保留时长或多文档压力资格。

两架六组最终有效结果**10642 passed、0 failed、0 skipped**；其中5组每架沿同产品库一次完整运行，ReferenceTest修正测试输入后各重跑一次。最初编译失败是新增测试少传两个参数；初测每架一项失败是Prepared base晚reader缺transaction，完整状态机在操作前拒绝了测试输入；修正测试后1027/0/0，两次失败与日志保留。产品实现未因这些测试输入修正改变。

[真实安装探针](read-write-r0/install.json)每架32格、544窗口，canonical80/reuse272/adapter128/overlay64，分配和释放均0，分配正控制3。它只证明实际安装窗口，不证明整个读写无分配。结构/调用图按本候选刷新，不放宽布局或侵入上限。

## 4. 后续主线的完整责任

下一项不是继续给metadata容器抠常数，而是原operation范围内的**输入选择→必要页准备→一次接受→读者交付与最后释放**。原T01/T02/T03/T04/T06共同承担，详细设计约束见蓝图§19.18。当前候选可作为局部指令删量原型，但未取得CPU性能验收；后续比较必须保留02bcc及本原型两个身份，不能静默以未通过候选作为已验收基线。

## 5. 目标校正：局部删量尚未越过原有写成本

2026-10-12用户复核指出，8.72M删量与上一包的前台回退相当，不能用它代表原有基础差额的解决。这个量级判断成立。计数名称须同时校正：旧报告的**81.8543M是write前台相对upstream差额**，独立read是11.8158M；写内部的capture、比较读取、准备和接受包含在write端点中，没有证据将81.85M全部归给其中的读路径。

| 冻结批次与身份 | write相对同批upstream的额外指令，M | 能支持的判断 |
|---|---:|---|
| resident-operation确认：11c689 | 73.4117 | 由同批81.854298−8.442598重建，上一包之前已经存在巨大写差额 |
| 同批02bcc | 81.8543 | 上一包向写前台增加8.4426M，后台净收益不能掩盖它 |
| read-write确认：d5f715 | 73.1848 | 删去8.7169M后，剩余量级仍接近上述原有差额 |

两个确认批次不同，**不能把8.7169−8.4426=0.2743M称作相对11c689的实测净收益**，也不能将73.4117与73.1848的差宣称显著改善或等价。需要同批11c689、02bcc、d5f715与新候选/固定upstream的相关对照才可授予相应增量结论。本轮应报告为局部冗余删除、量级近似抵消上一包写增费；没有证据宣称突破原有写协议成本。

当前write 79.2130M/upstream 6.0282M，1024个页写入，描述性均摊为约77.36k/5.89k条指令每页，额外约71.47k。均摊不是单页机制价格。公共fixture的`measure(1)`只包`writeBytes`，`measure(2)`另包随后`readBytes`；输入是整页覆盖，初值0x19、后续0x53/0x6d交替，旧值比较首个memcmp即不等。因此重复旧值扫描不能解释主格的全部管理差额，写内部读取也不能与独立read桶相加后重领预算。

当前源码的结构证据为：`Backend::writeBytes`先在已准入范围内capture并逐页读出比较；改变页随后经`prepareTarget→prepareWriteBaseLocked`再次解析overlay/base/authority/descriptor；复用容量仍逐页执行`prepareWritePlanLocked→preparePrivateWrite(count=1)`的物理准备、预算handoff、通用metadata候选、descriptor准备、claim/安装和清理，最终经过operation接受。**backing复用已成立，不代表管理协议已经复用。** 这些事实支持将完整写操作的重复选择/准备作为根因候选；未受控定价前，不能认定capture、锁、metadata中的任何一项独自解释73.18M，也不能把整个差额都授予可删预算。

后续必须同时回答“是否修复02bcc新增的写成本”和“是否减少11c689就已有的基础差额”，并单列当前对upstream残差。先证实原scope可承载一次选择、一次共有准备和一次接受，再领取实现；真实逐页状态变化、物理权限、并发读者、操作失败回退仍逐项证明。下一候选不能仅以相对最近未验收原型的局部百分比通过，就宣布命中主瓶颈。此次为已有原始数据及源码的解释修正，没有运行新价格样本或改变既有门槛。

<a id="remaining-cost-audit"></a>
## 6. 仍然很大的原因与未解决成本

2026-10-12继续复核。**核心重写尚未实施；73.1848M是局部base重装优化后的写差额，不是§19.19完整重写后的残差。** 该节“回收50%仍7.07倍、达到2倍需回收91.76%”只是由当前大差额推导的预算算术，不是已预测或实测的重写效果。

下表全部由本报告同一确认批的case7重算，单位为每个完整case（含四manager寿命），不混入11c689或02bcc旧批价格。每行互斥，CPU和指令分别计算，均为候选减upstream的块均值差：

| 端点 | 额外指令 M | 额外CPU ms | 指令差额占比 |
|---|---:|---:|---:|
| setup：创建、初始写入/commit、history准备 | 8.636038 | 0.712094 | 7.61% |
| write | **73.184785** | **5.016220** | **64.50%** |
| read | **11.710149** | **1.262464** | **10.32%** |
| finish | 1.966898 | 0.187734 | 1.73% |
| undo | 1.361447 | 0.189563 | 1.20% |
| redo | 0.999229 | 0.122727 | 0.88% |
| teardown | 1.843157 | 0.173607 | 1.62% |
| 前台阶段外余项 | 0.014487 | 0.062426 | 0.01% |
| 进程减前台 | **13.754525** | **1.530414** | **12.12%** |
| **进程合计** | **113.470714** | **9.257250** | **100%** |

未四舍五入值逐块闭合；[研究机器账](read-write-design-source-index.json)的`remaining_cost_audit`记录来源、九行、汇总与检查。`进程减前台`是带符号的计量窗口差，不能把它全部改名为reclaimer/锁成本；upstream该项−0.016653M/−0.000115ms反映窗口不完全重合，不是负工作，也不截零。前台阶段外余项没有单独的frame/drain/观察边界拆分。setup含实际初始写入，不能全部当成构造费。

**读写占额外指令74.82%、额外CPU67.82%；其余仍有28.575781M/2.978565ms。** 其中其他前台14.821256M/1.448151ms，进程减前台13.754525M/1.530414ms。端点位置已经入账，不等于各自算法机制已经定价。假设仅将read/write两个端点完全降到同批upstream、其他端点不动，进程仍为55.144006M/4.372940ms，约upstream的2.08/3.14倍。这是条件算术，不是下界或预测：核心改写也可能改变setup和后台，但只能按实际净变化认领。

**写内部还没有解决的工作不止capture。** 当前源码支持以下责任链；下列条目可能嵌套，不能各领一个父桶再相加：

- 输入/操作：`runCpuMutationOperation`建立范围、write set、execution和adapter准备；`writeBytes`再建立完整capture，逐页resident比较；`prepareTarget→prepareWriteBaseLocked`又选择base、authority和descriptor。当前主格第一次memcmp即不同，不能将这些管理工作解释为必要旧像素扫描。
- 物理复用/收费：`prepareWritePlanLocked`虽不重新分配896个backing，仍逐页准备physical handoff、budget reservation、metadata、descriptor；claim后再提交各层。`OwnerLedger::prepareBackingHandoff/commitBackingHandoff`还检查物理归属、记录prepared change、按allocation generation对backings索引extract/reinsert并结算。保留ABA/并发读者校验，不等于必须保留这套逐次容器与交接表示。
- metadata生成与发布：`preparePrivateWrite`仍进入`preparePublicationImpl(count=1)`，创建Data/Entry/Publication、取shard、构造工作值并预备安装。d5f只删除其中base重装；`publishPrivateWrite→applyWriteSequence`仍另做private完成。当前代码是“目标准备后再完成”，不能只看安装区间alloc/free为零就当整次操作廉价。
- 接受与逻辑退出：`sealImpl`仍多次访问D集合，创建/核对proof，准备publication与metadata detachment，再接受overlay/adapter并销毁冷状态。`finishUnlocked`释放候选、处理尚未直接退出的旧proof和history；即使旧物理页作为spare保留，旧逻辑记录/descriptor/proof的周转也不会因此全部消失。必要接受点必须保留；中间表示、重复验证和重复遍历是否必要要按原entry的已知事实重审，不能一律删掉或一律合理化。
- 独立读：完整cut的H项保护、K次版本查找和新逻辑版本的binding冷发现/关联仍存在。主格read的1024次冷关联与write里的resident比较属于不同端点；把关联提前到写端不构成净优化。

这些路径已列入§19.19修改索引，但**尚缺未插桩条件下的机制净价，以及重写后它们确实退出的证据**。重插桩曾将write从约88M抬到140M，不能据其内部桶给73.18M分配可信百分比。全write差额的逐端点95%区间为[73.1365,73.2628]M，存在性很稳；某个机制的可删比例没有相应区间。不能用必要版本/预算/锁的存在，推导13.14倍写指令是正常代价。

**对蓝图的修正是扩大核销口径，不另开小优化主线。** 原生读写候选要共同核销输入选择、目标/物理身份准备、metadata转换、接受/adapter、旧逻辑退出及新读者保活；物理复用数不再重复领收益。setup、finish/history、teardown及后台保留独立差额，不能因为不在read/write计时内而移出验收；H0无history的canonical发布、真实holder、partial/no-op和压力路径沿原控制保留。进一步解释见[原蓝图§19.19.9](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#read-write-residual-obligations)。本次只复算既有样本并核对源码，没有新性能样本或产品修改。
