# 中间版本消费者、直接回收净价及下一生命周期边界

**当前决策已由[全流程账本§19](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#full-flow-ledger-audit)接管。** 本文保留两次局部替代的冻结事实、否决与条件算法；其中“下一主线/优先”不是当前排期。先完成全流程数据，再比较完整设计，物理/身份复用与读侧均未预选，本轮不实施新优化原型。

产品仍为11c6895ddfeae074df727c76dcbf9e12988479ee。此次56个成功过程：r0安全6、r1安全6、数量4、真实metadata准备点故障2、完全无热路径观察器净价34、current/upstream payload数量4。另保留payload-r0构建锚点失败；r0直接回收原型虽通过5233/0/0，因静态发现遗漏bad_alloc接续而撤出，未测时间。r1 ARM64六组5233/0/0；这不是新一轮双架10466资格。产品/产品测试改动0，没有把原型写入生产。

**裁决：960个中间版本可在替换接受后直接通过原回收准入，但逐页前台执行这一合法替代净增CPU，否决生产化。额外物理对象周转仍存在；payload已大量复用，下一主线应围绕对象/身份完整生命周期，不能靠增加字节缓存或把GC搬上前台解决。** 整体机制净账尚未全部闭合，本次只闭合这一具体替代的净价。

## 1. 哪些值真要保留

`writeBytes → 捕获原overlay → 私有Fresh结果 → seal/proof → overlay接受 → 撤销被替换proof → Historical → 可达性/保护检查 → 原retirement record → provider retire → 实际free`。

这里有三个不同的旧值。undo起点保留到历史释放；上一成功operation的结果保留到本次接受，失败必须仍能读取它；exact capture、lease、pin、alias或last-use则可能在接受后继续保活。不能只保留undo起点就原地覆盖上次成功结果，也不能从一个短读已结束推断全部读者已结束。

此次找到的具体免扫描证明是**Prepared来源**，而非“H0无history”。`prepareMutation/installMutation`都确认版本由本事务Prepared；状态机只能将新 generation 变为Prepared，已发布版本不会退回Prepared。`tryAcceptLocked`在owner gate内安装新proof，旧proof随后撤销，所以旧版本未曾进入canonical root，也不能再由该事务提交。根扫描对这一精确来源不再增加信息；但metadata中的capturedReadViews、replica overflow、pin、activeOperation及债务准入仍必须逐项通过。`discardHistory`保留这些原检查，未删/拒绝/分配失败交回原collector。

静态索引（产品未改）：`KisPageStateMachine.cpp:376/469/928`新身份及Prepared/Detach规则；`KisPageMetadataCoordinator.cpp:2352/2508/2921/3433`准备、安装与保留保护；`KisPagePublicationCoordinator.cpp:392/457`原接受/退出；`KisPageHistoryCollector.cpp:104/185`原切片、根扫描及bad_alloc接续。原型只替换Publication TU中的`KisPreparedOverlayUpdate::finishUnlocked`，同一native/generic/removal入口共享此责任，没有新增持久字段、owner、队列或API。

## 2. 预测与实测必须分开

协议在运行前冻结于[DETACH_PROTOCOL](DETACH_PROTOCOL.md)，源码、修改前后差分、命令、身份和所有日志在[原始包](lifecycle-raw.tar.xz)。主净价为8独立镜像块、每侧块内两过程均值、100000次seed20261011 pointwise95% bootstrap。没有逐事件scope/count/Mach线程观察器；只保留双方相同的空边界hook和额外drain，原case和各业务阶段端点不变。

| 项目，K16/W16/H1，四manager寿命 | 事前判断 | r1实测 |
|---|---|---|
| 可免根扫描的superseded候选 | 最多960，依赖原保护/债务接受 | 两次均960；直接metadata删除960 |
| Fresh / provider retire / 实际free | 本候选不删物理生命周期 | 1088 / 1088 / 1092，原型前后完全相同 |
| metadata准备故障 | 不能撤销已接受overlay，必须回原collector | case7每过程960次真实reserve前bad_alloc；全部回原流程；全8case两过程共2040次注入，像素/历史/free闭合 |
| H1完整process净收益 | 单价未知；值得推进门δ=0.75ms，不能借1.736ms父桶作预测 | **节省−1.62125ms，95% [−2.793,−0.838]；失败** |
| H1完整前台CPU | 不得出现>0.75ms回退 | **节省−1.83310ms，[−2.60490,−1.27506]；失败** |
| H1其他线程CPU | 可能少扫描，但没有事前价格 | 节省0.26127ms，[0.16250,0.53485] |

以上中位数不能相加。可加的同批均值账（原型−原实现）是：**前台+1.520359ms，其他线程−0.504296ms，完整process+1.016063ms**。增广drain包含在内，额外tail process均值+0.005375ms；不是遗漏后台清理导致假回退。前台write阶段的配对中位回退2.09094ms，read节省0.32159ms；提前清理改变后续metadata规模和调度，但其总价仍为负。

H0实际命中0。它的process“节省”中位0.2525ms，区间[0.109,4.958]，均值2.571ms被几个大块偏移影响；baseline单块27.6995ms对prototype14.8305ms的原样本保留。**不能把未命中控制的差异当直接删除收益**，也不排除此块、不加样。H1八块中七块回退，按原固定分析被否决；无法据这批数据精确拆出每项锁、分配、批量和调度的单价。其他线程是process−foreground，不能重命名为这批单测的reclaimer。

原型把原本可在worker中按页历史切片处理的工作，变成每次接受时逐页effects/债务准备与metadata删除。免去根扫描并未免去退休主体，也新增了前台责任。当前证据证明**这一实现组合不值得**；不证明“所有免扫描算法都不值得”，不授权立即追加另一个队列/批量原型直到正结果。

## 3. 页面对象不是payload系统分配

独立数量协议见[PAYLOAD_COUNTS_PROTOCOL](PAYLOAD_COUNTS_PROTOCOL.md)。当前`KisTileData::allocateData`先查`m_cache`，4BPP的cache miss才进入Boost pool；`freeData`也先回cache。pool后备请求仍不等于系统malloc。两个过程按正反case顺序分别记录，缓存跨case状态和后台调度可能改变miss数量，报告原始值而非强行取一致值。

| K16/W16 | 当前payload请求 | 当前cache hit | 当前cache miss | upstream请求 / hit / miss |
|---|---:|---:|---:|---|
| H0，两过程 | 1092 / 1092 | 1092 / 869 | 0 / 223 | 132 / 132 / 0，两次相同 |
| H1，两过程 | 1092 / 1092 | 1076 / 1042 | 16 / 50 | 第一次132 / 99 / 33；第二次132 / 132 / 0 |

H1当前hit率**98.53% / 95.42%**；两侧所有payload归还都进入原cache，没有本窗口内的fallback释放。全8case当前2616次请求、cache miss49/273；upstream576次请求、miss33/33。数量满足`payload请求=cache hit+miss=对象free=rows或duplicate请求+默认alloc`。没有把case之前保留的payload缓存解释成泄漏，也没有将miss之间的差直接定价。

因此960额外`freeTileData`不能改写为960次系统free/malloc。字节缓存复用已经发生，仍持续发生的是TileData构造/注册、provider AllocationMap与resident binding准备、residency observer与physical identity登记、owner backing/预算与metadata generation/descriptor/proof的建立，再做反向退出。缓存pop/push、payload初始化和Boost后备也有成本，仍需真实定价；不能宣布全部差额都属于metadata或锁。

## 4. 对物理复用理想算法的精确修正

可构造方向有两类，责任不同：

1. 覆写**当前仍可见**的backing：必须有独立before，或满足M7全部首字节前准备及8页/256KiB/100µs约束。当前K16不能拆成两个不可逆半提交来绕过。此轮没有更改这些限制。
2. 重用**更旧、已证明无消费者**的backing作为下一Fresh私有目标，当前值保持不变直到接受：失败只丢弃私有目标，成功换逻辑身份，旧current在最后使用后成为下一可用目标。它不依赖覆盖当前值，因而逻辑上不等同M7；但要解决原provider内的身份代次、旧binding拒绝、完整预算/驻留/压力和最终释放。增加一个独立pool或生命周期账本并不是已有批准方案。

有限fixture、W=16、无外部持续capture/alias/异步last-use时，可用双工作目标构造数量上界：H0每manager每页2个物理对象；H1另保留undo origin，需要3个。于是四寿命K16是**128 / 192个非默认对象**，而现实现两者均1088；条件可少构造**960 / 896个对象**。H1不是直接减少960：保留每operation可恢复性时，这一构造比upstream的128个对象多64个。W=1时H1只需origin+一个结果，无需第三个。

这些是**待实现算法的条件构造数量上界**，不是已测删量、严格全局下界、生产资源峰值或毫秒预测。持续读者、alias、失败、背压、页面跨调用生命周期及释放调度会改变可用目标数；必须回退Fresh或明确拒绝，不能等待自己持有的保护。逻辑generation、必要接受点和metadata移交仍可能保持1088，单纯避免TileData重新分配不自动消除多层管理费用。真实新before副本也不能偷塞进此数量模型。

## 5. 原矩阵与下一有界责任

沿原T03.1/T04.2/T04.3/T07.2更新，不扩33行：本次确认旧Prepared在接受后能立即回收的命中；否决逐页前台直接discard；物理生命周期删量0；下一目标仍是同一页在多次操作中的**完整身份建立/解绑**。具体核对：`prepareTarget → provider::prepareAdoption/adopt/retainPhysical → owner::registerBacking → metadata::AdoptPreparedWrite → descriptor/proof → retirement::prepare/bind/verify/release → provider::releasePhysical → backing/budget退出`。`KisTiles3PageReplicaProvider.cpp:683/736/749/1276`与`KisPageOwnerLedger.cpp:1985/2004/2033/2052`是下一原位索引；先判定可复用原node/binding/charged storage和真实失效条件，不能先加cache。

优先做可以同时减少前台建立和后台拆除的完整责任判别；只折叠同步retirement四次终结检查是备选，不因它更易改就称榜首。T06一致读仍并列，no-op比较也是其consumer。新的净候选须把身份复用成本、预算高水位、失败和最终释放全部扣除后再报价，不用960或896乘未知单价。

技能流程在此轮成功阻止了“100%命中就产品化”的误判，并暴露接受后的可失败清理必须沿caller传递；它尚未获得本轮正向选项排名/收益预测验证。无需为了升级技能扩大实验。原业务控制、live-copy两个exact-view失败、M6/M7/M8 0/3和校准2/20保持。

<a id="synchronous-retirement-proof"></a>
## 6. 同步退休完成证明：删量兑现，净收益资格未取得

本节是下一次有限判别，产品仍11c689；没有把§1–5的负价候选重新测到通过。问题是创建和退休是否重复为一个同步事实付费，候选位于原T03.1/T07.2。它不是通用image优化，upstream不承担此PageStore completion协议；但其收益仍只能由同义完整窗口对照判定。

**必要事实与更直接表达。** Tiles3 `retire` 在provider mutex内验证operation replay、exact allocation、last-use、residency transition和binding pin，解绑并提取原节点，锁外deref后才返回。原每allocation私有Pending票据在这之前没有外部消费者；不是外部异步任务的可观察进度。原型让configure已准备的Succeeded票据在物理完成后随exact operation/replica返回，删除创建、保存、失败终结、析构取消与成功终结整条私有票据寿命。共享完成事实不替代operation身份，也不提前宣告释放。owner prepare/bind/verify/release、retirement debt和预算退出均保留；generic异步provider仍按原Pending结果接续。

**修改闭包和审核索引。** `KisTiles3PageReplicaProvider.cpp` 的`Tiles3Allocation/Private::adopt/allocate/prepareSynchronousSource/adoptInitialTile/retire`；`KisCpuResidentBinding_p.h` 的`Retirement/beginRetirement/revokeBindings`；同模板的测试CPU provider迁移，保留其独立allocation request票据。CPU mutation原位迁移完成记录满额和来源计数，补pin/last-use拒绝、同operation重试、重放与stale read反例。原型生产+15/−42，测试+50/−35；无新owner、字段、队列或缓存。**四文件候选全部撤回工作树**，完整补丁和派生源码保留于原始证据，产品/产品测试最终改动0。

### 6.1 预测与实测数量

| 项目，K16/W16四manager寿命 | 运行前预测 | 实测 |
|---|---:|---:|
| 删除每allocation Pending申请 | 1092 | **1088** |
| 全部Pending申请 | 原有configure保留，其余删除 | **1096→8**，两次数量过程一致 |
| Tiles3Allocation大小 | 删除一个ticket字段，字节待编译验证 | **56→24 B**，两架构DWARF一致 |
| Fresh / rows / provider retire | 保持1088 / 1088 / 1088 | 完全保持 |
| TileData free | 保持1092 | 完全保持 |
| 时间点预测 | **未知**；不是1088乘某个未测单价 | 见下表；未取得推进资格 |

初报把4个默认TileData也视为provider adoption，多算4（本case约0.37%）。实际manager构造把默认对象交给hash/memento；backend `configure`建立surface/default格式，不adopt默认物理对象；`configureClone`才对manifest逐页adopt，本fixture没有clone。8case实际删量均为`4K(W+1)`，少8/128/68/1088，两种history相同。数量后、时间前修正模型，保留原预测，不改变性能样本或门槛。**对象、provider allocation、逻辑generation必须按真实consumer分别计数。** 字段减少是每个记录32 B，不是全程驻留峰值减少1088×32 B。

### 6.2 完整净价与置信边界

34个plain过程＝双方各1 capability＋8个ABBA/BAAB块；无scope/count/Mach观察器。端点含前台、所有其他线程、teardown和额外drain。以下为配对节省`baseline−prototype`，ms/case；正数才是省时，pointwise95% bootstrap，不是联合正式门。

| 端点 | H1中位数 [95%区间] | H0中位数 [95%区间] |
|---|---:|---:|
| **process CPU** | **−0.01550 [−0.26500, 1.02850]** | 0.47875 [−0.02650, 1.57300] |
| 前台CPU | −0.11095 [−0.47260, 0.60977] | 0.08515 [−0.12211, 0.96710] |
| 其他线程CPU | 0.16424 [0.00106, 0.41873] | 0.37672 [0.00346, 0.60590] |
| wall | −0.29200 [−0.56150, 0.49950] | −0.01525 [−0.13700, 1.46950] |

H1均值的可加节省账：前台0.064356875＋其他线程0.145143125＝**process 0.209500ms**；其中额外drain节省−0.001000ms，已计入。阶段中位数不得相加。其他线程不是具名reclaimer观察，不能直接把0.164ms填回旧worker子桶。H0均值1.8573125ms被首块11.0825ms差主导，全部保留，不以此替换配对中位数或另算无异常样本。

主判据下界须≥0.75ms，实际−0.265ms，因此**不进入独立确认或产品化，不追加样本**。原型级非劣粗门通过，但不等于产品2%控制；安全通过也不等于性能资格。区间仍允许约1ms收益，不能说已证明零收益或上界小于0.75ms。当前只能说该设计冗余已合法删除并测价，未证实其值得作为本主线的性能落地项；这项数据不支持拿它解释约12ms主要差额。

### 6.3 失败保留、身份与下一选择

44成功过程：r2 ARM64六组**5233/0/0**、4数量、34时间。r0 `ar r`不接受fat archive，构建失败后改用Apple libtool；未跑测试。r1首组1746/1/0失败在新增测试：完成外部last-use正常释放80 B，却断言仍满额；r2补足这80 B后证明真正退休发生在hard cap。生产候选无安全修补，测试错误及全部日志保留，r1未跑性能。374个未替换plain对象与既有冻结哈希一致，原产品库未覆盖；两同步template consumer、六安全binary均隔离重编/重链。没有重跑原双架10466，不新增双架资格。

本轮净账加入一项**有价格区间但未合格**的合法替代，不将“结构冗余”自动排到可回收时间前列。原完整身份周转仍未定价：TileData/registration、provider node/binding/residency、owner backing/预算、metadata generation/descriptor/proof及其逆向退出仍全部发生。下一优先应验证§4的旧不可达backing能否在原owner内复用完整身份存储，并保留下一操作接受前的上一成功值；定价必须包含retag/失效、保护、压力和最终释放。不能只再折叠一个check、换容器或增加第二pool。T06一致读保持竞争解释，本轮没有据此裁决剩余差额都是必要管理或锁费用。

数量模型纠错和未合格候选退出说明技能有约束作用；它仍未取得本主线正向收益排名/时间预测的验证。整个机制净账、原业务控制、live-copy两个失败及M6/M7/M8仍开放。
