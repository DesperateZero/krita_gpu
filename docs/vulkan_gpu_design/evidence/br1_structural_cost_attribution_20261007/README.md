# upstream 大差距的结构归因

先前选择过于局部：17页的稀疏clear消除解释了一个真实冗余，不能解释普通freehand约2.3倍的差距。核心候选是**普通同步CPU写入，被表达为逐操作准备、逐代际资源登记、逐访问借还保护、再逐操作交付的通用协议；原owner的持续性没有充分传递到这些下层责任**。本包完成源码对照、原采样重分类和下一责任清单，没有产品修改、新性能样本或新M6通过。

当前产品`2f22452e2dc76dca3e60c6231783534f44716ce4`，外层父`5da3a9adf`；upstream `9a24ae0d8c070884fb013594191002e1a1b39a19`。当前状态见[92 §16.143](../../92_br1_m6_m8_execution_baseline.md#structural-cost-attribution)。[事前范围](PLAN.md)、[固定身份](identity.json)、[分析器](analyze.py)和[结果](summary.json)绑定本次诊断。

## 差距落在哪类工作

普通未插桩业务的冻结比值为ARM **2.258 [2.107,2.426]**、Rosetta **2.318 [2.180,2.448]**，来自[独立CP0批次](../br1_cp0_current_applicability_20261007/README.md)。它们不是本包重测的时延。以下是[原business profile](../br1_business_cost_localization_20261007/README.md)固定四过程、各64次replay的Stroke内所有线程Running样本，采用双方一致的互斥机制规则：

| 类别 | 当前0 | upstream1 | upstream2 | 当前3 |
|---|---:|---:|---:|---:|
| 像素/画笔上下文，含内层混合kernel | 347 | 277 | 303 | 342 |
| 管理协议上下文合计 | **507** | **10** | **11** | **524** |
| physical heap | 144 | 77 | 77 | 131 |
| 其余 | 86 | 104 | 121 | 100 |
| 合计 | 1084 | 468 | 512 | 1097 |

管理合计含mutation/publication、provider/ledger/completion、budget/storage、adapter/manager、metadata、retirement、read binding及epoch。两次当前对应细分为：mutation132/123，provider108/124，budget83/78，adapter82/74，metadata42/51，retirement41/52，read15/14，epoch4/8。physical heap单列，不能不分来源全算作PageStore可删成本。

该上下文仍包含协议下面的数据复制/初始化及同步原语，并非纯控制指令；继续按最内层符号拆分，避免再次把外层函数当成全部成本：

| 管理协议内的叶符号类别 | 当前0 | upstream1 | upstream2 | 当前3 |
|---|---:|---:|---:|---:|
| memcpy/memmove/memset/fillWithPixel | 76 | 2 | 4 | 92 |
| ulock/psynch/Qt mutex与wait原语 | **150** | **3** | **1** | **161** |
| 其它协议叶符号 | **281** | **5** | **6** | **271** |

其它协议叶符号可见budget树查找、metadata/admission索引、storage owner引用等；当前同时出现大量同步原语，与逐层逐次进入资源协议的源码相符。**同步原语即使被采样器标为Running，也不等于已测得锁CPU或等待时长**；其它协议叶符号也不等于全可删。复制叶既可能搬像素，也可能搬管理容器，不能仅凭memmove区分。叶分类只在上述管理上下文内分区，upstream位于其它类别的copy/COW成本没有被改记为0。

两边过程均值之差600.5个样本中，管理协议上下文差505个，描述性占84.1%；像素类别差54.5、heap差60.5、其余差−19.5。**84.1%只是样本差的账面分布，不是wall差距归因比例、可删比例或置信区间**。所有线程样本不能直接换算关键路径时间。相同输入/结果也不证明内部像素访存和操作次数完全同义；仍缺upstream完整工作量账。

这比“projection占28%”更有解释力：额外上下文散布在画笔、projection和终结尾的共同管理路径，不会因单独少复制17页而整体消失。原actor划分未改：当前画笔626/619、projection299/308，upstream画笔363/382、projection25/46；history/retirement/reclamation当前分别39/44、23/22、34/34，upstream在此窗口均无样本。后台样本不证明全部由这一笔产生，零样本也不等于零成本。

## 纠正一项会误导选点的证据

原机制分类漏认`void KoStreamedMath<…>`、`OverCompositor32<…>`等内层混合kernel，随后遇到外层adapter便标为管理。当前0/3的**117/106**个原adapter样本实际落在这些像素kernel；upstream1/2也分别对称纠正6/5个。原actor、Running总量、时延区间和全部样本不变，旧输出保留。

本次只在遇到首个实际管理frame前识别这些内层kernel；不能凭栈中出现过混合函数就把内层管理调用算成像素。每过程保留纠正样例。原“adapter199/180”的机制量不再作为纯管理预算，§16.141的旧机制分类由本包接续；该包actor和数量反证仍有效。本次先纠正分类再判断结构，不能把一次重分类当新的独立性能重复。

## 增加复杂度的核心责任

### 1. 原业务写入被拆为多次独立准备与交付

upstream的fixed dab通过random accessor取得tile，检查必要COW后直接进入原bitBlt/composite kernel。当前相同kernel外，`writePageStoreOperation`每次从矩形建QRegion、查legacy tile intent、建QSet，再导出QVector；backend转为SnapshotArray、排序去重，borrowExecution重新规范化并准备执行范围；随后adapter准备、全范围prepareWrites、像素操作、changed导出、execution finish、发布/adapter安装及清理。

这些动作并非全无意义：声明目标范围、像素开始前准备失败不破坏既有工作、并发writer排斥、原manager gate内联合交付都是现有合同。问题在于**同一目标事实跨层重建、权限和可见性边界没有形成可直接消费的一次性表达**，而非某个set特别慢。

两个具体例子说明这一点，但不单独领取微修复：

- backend按`(row,column)`排序，borrowExecution按`(column,row)`规范化。[原v3范围复核](range-order-audit.json)两过程各19次root composite、96次声明页访问，其中11个范围排序不同。额外转换是源码事实，未定价。
- borrowExecution的`auto pages=inputPages`本应共享canonical数组，但后续对非const局部`pages`作range-for，调用非const`begin()`→`data()`→`detach()`。非空canonical输入仍会复制；非canonical输入已在排序时detach。共享注释与实际行为不符。这说明只设计了“可共享容器”，没有让消费者真正只读借用，不证明它单独能解释2.3倍。

普通node原来已共用history transaction，canonical commit是1次；root匿名client也已合并部分canonical commit。不能把当前机制夸大成“每dab全局commit”。已有persistent分支仍逐operation构造execution、准备adapter/页、导出变化和交付，它没有消除以上管线。

### 2. 每个新代际都承担完整通用资源协议

upstream `KisTile::lockForWrite`先blockSwapping，仅在TileData共享时经COW mutex复验、clone及登记memento变化；独占暖tile不会重新建立一套通用replica对象。

当前`beginWriteImpl`的冷页分支要建立write plan/source/before、descriptor、metadata/admission/backing reservation，调用provider准备新replica，再登记OwnerLedger、验证terminal结果、准备/安装private状态。CPU provider即使同步完成，仍为allocate准备**readiness与retirement两个completion ticket**，逻辑allocation节点、physical payload/slot索引、residency observer登记和shared binding控制块，然后分配/复制TileData、关联物理身份、完成readiness。以后还有对应metadata发布与最终退役。

新设计确实要求版本隔离、实际容量、物理身份、swap一致性和晚释放证明；upstream不承担完全相同的统一CPU/GPU合同，因此不能把所有差额称为算法浪费。待验证的是：**原同步CPU owner能否直接持有唯一必要记录，在真实版本/读者转折前持续使用，让通用协议的动态准备只发生在确有转折处**。不能靠删除计账、伪造同步零尾或绕过claim证明收益，也不能另加一个CPU影子owner/账本。

页代际数和单代际管理单价相乘。root149→132只少11.4%的root代际，node76个不动，合计225→208仅少7.6%；大量通用协议仍存在。复制109→92合计少15.6%，但必要初始化116页没有减少。少量字节消除没有触及整条管理链，业务收益小与模型一致。

### 3. 准备寿命与实际字节访问寿命不一致

upstream random accessor保留4个tile的锁及指针，缓存命中直接算offset，不重新lockForWrite；淘汰或析构才归还。当前BoundedCursor只保留当前页guard，切页便归还；再访问通过目标集合contains、beginWrite、pin和exposure登记，guard销毁再unpin及更新状态。预备entry持续存在，并不代表可写指针或驻留保护持续存在。

原固定数量反证尤其重要：persistent把node session **27→1**，但**76个代际、20次复制、56次初始化、2420次pin**全部不变。它表明仅延长会话没有覆盖下层资源和使用期，而非证明这些2420次都可删到76。驻留可变、慢读者、实际峰值、同时exposure、拒绝与归还终点约束还在；upstream的实际pin次数也尚未测得。

### 4. canonical与兼容表示的同步以及终结尾

当前PageStore是唯一canonical权威，但仍须在旧tile索引中准备wrapper、更新extent、交付changed pages并失效派生读缓存。这是**两个表示的维护成本**，不是两个所有者。history/retirement/reclamation还维护跨操作的真实寿命。只减少session或只少copy，不能消除这些交付和退役责任。

目标是把派生更新接到原权威的实际delta，在真正交付边界消费一次；必要中间显示、exact reader和独立失败边界仍需更新，不能延迟到任意笔尾。物理free前的责任不可被“逻辑完成”吞掉。

## 理想设计与当前差距的模型

设`O`为原pixel operation数，`P_o`为每次声明页集合，`G`为合法写入段，`D_g`为该段真实首次写页，`C`为必要capture/发布/回退边界，`V`为实际页访问，`R`为驻留/权限失效导致的必要重新获取。

当前额外成本形状是：`Σ_o(集合重建/规范化 + 范围准入/执行准备 + adapter准备/交付) + Σ_代际(完整replica/metadata/预算协议) + Σ_V(guard/pin借还) + 真实终结尾`。这些项包含必要工作，不能整项删除。

可达到的理想表达要求：不变事实只规范化一次；同一`G`内首次写按`D_g`准备；有效保护覆盖其真实使用期，在`R`或必要边界处重取；派生表示消费实际delta；完整费用仍持续到物理free。只能合并没有独立失败/读者/并发边界的工作。**合法G与R尚未全量核定，单价及关键路径也未闭合，所以目前有结构模型，没有可兑现的总收益百分数。**

从2.258倍回到upstream量级，在其它因素不变的代数条件下需减少当前stroke约55.7%。这是目标缺口，不是已经证明的优化空间。17页净条件预算约0.083ms、剩余36链条件准备预算约0.335ms，均不足以支撑“解决主差距”的承诺；后者还未扣共享scope新增成本和必要边界。

## 下一有限责任与排查清单

优先级从“找到一个可删点”改为“原同步CPU写入的完整准备—使用—交付责任”。必须整体比较以下耦合成本；表中是诊断闭包和设计约束，不是未经实现便打勾的改动清单。

| 优先/位置 | 当前放大机制 | 可构造目标及保留合同 | 本包结论/下一证据 |
|---|---|---|---|
| P0 `kis_painter_blt_multi_fixed.cpp`、manager `writePageStoreOperation`、backend `writeOperation/runCpuMutationOperation` | 目标范围跨表示重建，逐operation preflight/adapter/export | 原owner一次规范化和直接消费；真实operation失败、legacy intent及联合交付保持 | 源码链确认；先分first-touch/warm-reuse/cut，不单独修sort/const作为主解 |
| P0 `KisPageStore` borrowExecution/prepareWrites/beginWriteImpl/finish、WriteCoordinator | 同一业务owner下面仍反复执行完整准备；必要与多余代际混合 | 按真实G复用原entry/plan/admission与资源，遇必要冻结/拒绝重新准备 | persistent数量反证确认；逐页核定代际原因和净协议删量 |
| P0 Tiles3 provider、原Ledger/completion/metadata/budget | 同步CPU代际承受通用动态资源协议及多层计账 | 唯一原记录、原终结及实际容量；区分同步立即ready与真实pending/retirement | 协议存在性确认；独占单价和结构替代表达未因果验证，不能直接删ticket |
| P0 cursor/guard与原驻留binding | 逐访问归还后再解析/借还 | 原execution内有限持续保护；驻留峰值、排他exposure、pressure及最终归还保持 | 2420次数确认；必要R及其代价未闭合，不凭次数加缓存 |
| P0 PreparedTileUpdates、manager gate、原publication/retirement | 持续准备派生表示和寿命结算 | 消费原delta，保留真正显示/reader/失败cut，晚释放持续收费 | actor差异和源码确认；不把后台全部归因本笔 |
| P1 merger clear→composite余36链 | 局部重复准备，有共享scope前提 | 纳入上述原责任能共享的部分 | 暂不独立领取；0.335ms只是条件准备预算 |
| P2 单个const循环/排序/容器 | 表示不一致的局部症状 | 随完整责任迁移同步删除 | 不据静态可删性预报显著业务收益 |

下一设计验证以同义first-touch、同页暖复写、必要capture后复写三种路径区分：记录`O/Σ|P_o|/D_g/C/V/R`，以及原plan/admission、实际allocation/control/ticket、pin/lock、changed交付、seal/退役的数量和独占CPU；等待与后台另列。原业务像素、更新数、旧读、失败、预算/pressure及最终free必须相同。用完整合同下的结构替代形成因果对照，不能禁用accounting/锁/COW来模拟“理想实现”。之后再固定未插桩parent及upstream比较；未取得这些预算前，不先开新产品微改或泛化cache。

## 置信度与收口

- **新增共同管理协议是主要额外执行上下文：较强证据。** 两次当前与两次upstream重算方向一致，源码链及persistent计数反证相互支持；不是概率95%的因果结论。
- **责任粒度/表示和寿命不匹配是优先结构问题：源码证据强。** 涉及operation、代际、访问及交付多层，不等于每层都可合并。
- **能删多少、能追回55.7%中的多少：尚不能给可靠区间。** 缺合法G/R全账、upstream必要工作计数、独占单价及结构替代因果样本；不可用84.1%样本差填补。

原profile产品为128fb32a71，生产同38834c4e26，先于当前2f22452e2d的17页clear改动；本包没有把旧采样冒称新源码实测。四过程均64 replay，其中current0为63×19+1×18次projection更新，其余均64×19，全部保留；它们后续replay暖全局cache，与CP0一过程一笔不同。原选栈SHA和profile-results先对旧raw manifest验证，再冻结本包副本。源快照保留当前及upstream差异；重算只证明类别归因修正。

新bench过程0、产品改动0、新正式通过0；M6校准2/20、联合hit0/4/miss2/16、metadata实际驻留分母/完整CP0缺项及M6/M7/M8=0/3保持。已有4554/0/0和Fresh/H4 8/8属于前包冻结源码，不宣称本包重跑。

原始选栈、数量输入及14个源码快照打包于`raw-evidence.tar.xz`；[manifest](raw-manifest.json)、[核验](verification.json)与[input指纹](input-fingerprints.json)单列。解包至本目录后运行`python3 analyze.py --frozen`，只重算summary和range-order-audit，先验证所有冻结输入，保持身份与源快照不变。原完整trace和加载/运行证据继续由前包SHA归档引用。
