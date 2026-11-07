# 03f：CPU 管理管线清理——代码改动位置索引

本篇把[03e理想算法](03e_cpu_management_pipeline.md)落实为固定改动索引；**逐项状态只维护在[03g](03g_cpu_management_cleanup_tracker.md)**，资格以[92 §16.155](../92_br1_m6_m8_execution_baseline.md#cpu-management-cleanup-result)为准。父基线`6644249a4c`，实施候选`704d96e81cf29d16191bc3db8785859d79775e27`、tree `4e7fc164db46c02b968fdd04400b9e4402e289d0`。以下旧表达是删除规格；当前函数导航及完整hunk归属见[本包PLAN](../evidence/br1_cpu_management_cleanup_20261008/PLAN.md)，函数名和源码身份优先于行号。

MP01–MP10分别对应03e的A–J，不重编号、不删除失败项；本篇拆成22个独立核销点。新增的alias、generic、初始化及legacy重复预留入口是同一冗余模式的消费者补齐，不给它们套用19/132/96的投影计数。这里的“删保证”只指删除重复证明的工作，业务保证保持。

<a id="pipeline-contract"></a>
## 1. 固定算法和责任边界

| 管线步 | 唯一责任/原对象 | 允许做的工作 | 不应再次做的工作 | 索引 |
|---|---|---|---|---|
| P1 目标规范化 | backend目标数组；公共borrow边界 | 操作域统一(row,column)排序去重；任意输入最多规范化一次；规范结果只读借用 | 只读detach、相反序重排、已按序绑定后再sort | MP01、MP02 |
| P2 范围接纳 | reserveManagedRange / 原ClaimSet | 第一次冲突判定、实际容量准备、growth解锁后的真实冲突复验；成功返回私有reservation | 已接受完整范围转交后再按N键重新准入 | MP04 |
| P3 原entry绑定执行 | session write-set / 原BoundEntry | 已存在entry一次定位；通用新键建立/回滚；排除活跃execution重叠 | 同键find→getOrCreate→findIndex；cursor第二成员表/线性扫描 | MP03、MP05 |
| P4 冷准备 | 原scope、provider和backing/retirement reservation | 一个连续activity覆盖预算→provider锁外准备；按真实可变状态回锁验收 | bound entry重新claim；无事实消费者的中间锁交接 | MP06、MP07 |
| P5 写入/单页借用 | execution权限或legacy原scope | 单guard、worker、Active/linked、layout/版本身份；真实新键准入 | legacy单页操作遍历全部已拥有claims | MP10 |
| P6 冻结并发布 | 原Sealing segment / overlay与canonical delta | 保留首次完整claim核验，后续校验动态owner/session、reader、revision与proof | 稳定claim集合反复全查；空值释放仍强制交接锁 | MP08、MP09 |
| P7 交付/释放 | 原OperationDelivery、ClaimSet、budget/retirement owner | adapter安装后释放原claim；实际物理free后归费；必要析构移出owner gate | 为已move/空且非最后owner的对象制造一次锁外清理 | MP08 |

三条入口必须同时有结论：独立operation走P2→P3；持续history scope直接走公共borrow的增量准入；fillRect取得P2后消费原session的semantic/直接写入口，不强迫构造execution。legacy iterator/copy/读缓存是P5的真实消费者。任何实现都不能因只测投影而省略这些分支。

实施形态：原session私有adoptReservation消费唯一reservation，可选execution输出替换独立operation的adopt→generic borrow；fillRect只消费reservation。直接slot绑定不再按key查找，公共borrow仍一次定位已有键并处理真实新键/重叠。ClaimSet的owner/token/writeSet身份由原WriteAdmission的adoptReservationLocked判定；不向公共API传trusted/canonical/alreadyClaimed开关，不新增权限集合、缓存、常驻布尔事实或owner。

<a id="source-index"></a>
## 2. 固定改动索引

各行都包含源码定位、需要一起迁移的consumer以及删除边界；验收ID在03g定义。源位置未列为“主改”的联动文件只审查受影响责任，不整文件重写。

<a id="mp01"></a>
### MP01 / A：规范数组只读消费

| 子项 | 源码及consumer | 实施目标、旧表达退出及保留条件 | 验收 |
|---|---|---|---|
| MP01.1 | [Store::borrowExecution](../../../krita/libs/image/pagestore/KisPageStore.cpp:1367)：活跃execution重叠循环1402及绑定循环1421；[SnapshotArray::data/begin/detach](../../../krita/libs/image/pagestore/KisPageSnapshotArray_p.h:35) | 规范化以后统一const消费；删除两个非const range表达引发的detach。保留模板可写COW语义和真正乱序输入的必要复制；修正“canonical无需分配”的注释使之可验证 | V1、V3a、V4a |
| MP01.2 | [backend::writeBytes](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2351)：lambda按页遍历局部pages；同函数已有const targets别名 | 改为消费原const规范范围，防止新的借用方式让body重新触发可写detach。当前不单独授一次克隆删量。核对changed/target用途，不把结果数组误作声明范围 | V1、V3a、V4a |

<a id="mp02"></a>
### MP02 / B：一个操作域排序

| 子项 | 源码及consumer | 实施目标、旧表达退出及保留条件 | 验收 |
|---|---|---|---|
| MP02.1 | [backend::writeOperation](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2235)、[writeBytes自然行序](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2327)、[borrow比较器](../../../krita/libs/image/pagestore/KisPageStore.cpp:1378)、[Execution::Private::order/find](../../../krita/libs/image/pagestore/KisPageStore.cpp:1320) | 统一(surface,row,column)，单surface输入用(row,column)；二分查找与构造相同。公共乱序/重复输入仍规范化，adapter规范输入不重排。epoch/root/overlay的其它排序不变 | V2、V3a、V4a |
| MP02.2 | [borrow末尾BoundEntry sort](../../../krita/libs/image/pagestore/KisPageStore.cpp:1444)、Private::less | entry按规范pages顺序构造后直接使用；删末尾sort。检索less全部consumer，归零则同批删除；debug有序断言可以留，不能在Release重新扫一遍作“保险” | V2、V3a、V4a |

<a id="mp03"></a>
### MP03 / C：唯一成员权限判断

| 子项 | 源码及consumer | 实施目标、旧表达退出及保留条件 | 验收 |
|---|---|---|---|
| MP03.1 | [BoundedCursor ctor/moveTo/字段/构造点](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2244)、[execution beginWriteImpl权限入口](../../../krita/libs/image/pagestore/KisPageStore.cpp:2003) | 删`targets.contains(next)`、cursor的targets字段与参数、构造传参；由execution->find唯一判定成员。旧guard先释放、failed锁存、rawData空、布局检查保留；不得失败后换合法坐标恢复成功 | V2、V3b、V4b |

<a id="mp04"></a>
### MP04 / D：完整reservation一次接纳

| 子项 | 源码及consumer | 实施目标、旧表达退出及保留条件 | 验收 |
|---|---|---|---|
| MP04.1 | [唯一producer reserveManagedRange](../../../krita/libs/image/pagestore/KisPageStore.cpp:1787)、[adoptReservation](../../../krita/libs/image/pagestore/KisPageStore.cpp:1867)、[私有reservation字段](../../../krita/libs/image/pagestore/KisPageWriteCoordinator_p.h:576)、[ClaimSet身份/移动](../../../krita/libs/image/pagestore/KisPageWriteCoordinator_p.h:506) | 先证明唯一有效producer与token不被外部释放，再以原admission身份核对替代接收端N键全查。保持同owner/非空有效token/对应writeSet、fresh scope/worker/operational检查；foreign、空、伪造未接纳范围均拒绝。fillRect及operation两个接收consumer共同迁移 | V2、V3c、V4c |
| MP04.2 | [runCpuMutationOperation两支](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2119)、[Store.h私有接收接口](../../../krita/libs/image/pagestore/KisPageStore.h:226)、[claimRange](../../../krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2569) | 独立operation只从原reservation接收并绑定，消除其generic claimRange两遍required/install；history分支仍走原generic borrow，新键、容量和活跃重叠判断保留。候选存储先准备，失败由原range/session RAII释放，无部分execution挂接。claimRange有真实generic consumer，函数不全删 | V2、V3c、V4c |

移交前后仅一个有效ClaimSet；move后原range析构不释放已转交token。旧rebindClaimSetLocked及两个测试consumer已删除；原adopt函数中的Release全扫和新方法Debug断言分别核对，不从断言行数领取Release收益。新增身份查询仅由原WriteAdmission拥有其语义。

<a id="mp05"></a>
### MP05 / E：稳定entry一次定位

| 子项 | 源码及consumer | 实施目标、旧表达退出及保留条件 | 验收 |
|---|---|---|---|
| MP05.1 | [borrow绑定/回滚](../../../krita/libs/image/pagestore/KisPageStore.cpp:1409)、[findIndex/getOrCreate/handleAt](../../../krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2211) | 已存在键一次findIndex→handle/at，避免find→getOrCreate内部find→findIndex三连。新键保留原容量准备、incarnation、创建位图与失败erase；无必要不改通用write-set API或增加键索引。回滚查找只有确有已保存安全handle时再删，不凭entry地址猜index | V2、V3c、V4c |

<a id="mp06"></a>
### MP06 / F：bound冷页沿用原claim和定位

| 子项 | 源码及consumer | 实施目标、旧表达退出及保留条件 | 验收 |
|---|---|---|---|
| MP06.1 | [beginWriteImpl bound/冷支](../../../krita/libs/image/pagestore/KisPageStore.cpp:1996)、[claimEntryLocked](../../../krita/libs/image/pagestore/KisPageStore.cpp:1000)、Execution::prepareWrites/beginWrite | 只有原linked execution合法bound entry免除claimEntryLocked/claimOne；直接beginWrite、semantic、legacy新键继续准入。保留scope状态/worker/重叠/已暴露guard校验及prepared-but-untouched撤销 | V3c、V3d、V4d |
| MP06.2 | [冷支取得entryIndex](../../../krita/libs/image/pagestore/KisPageStore.cpp:2022)、[claim后再findIndex](../../../krita/libs/image/pagestore/KisPageStore.cpp:2072) | bound冷支已有scope保护和有效entryIndex，沿用该定位，省第二次同键查找；普通新增entry必须取新handle。不要新增每entry永久index缓存或复用已erase的incarnation | V3c、V3d、V4d |

<a id="mp07"></a>
### MP07 / G：冷准备的必要锁边界

| 子项 | 源码及consumer | 实施目标、旧表达退出及保留条件 | 验收 |
|---|---|---|---|
| MP07.1 | [beginWriteImpl reserve→provider](../../../krita/libs/image/pagestore/KisPageStore.cpp:2133)、register/binding与最终接受 | 一个activity/guard覆盖锁外reserve→provider→register/binding；有效reservation只读局部值，不制造中间回锁。拒绝/异常先回锁再改scope，所有出口activity平衡；已物理分配失败沿原retirement Debt | V3d、V4e |
| MP07.2 | [prepareAliasLocked reserve/provider](../../../krita/libs/image/pagestore/KisPageStore.cpp:1164) | 同样合并reserve与prepareSynchronousSource之间的空交接。provider之后原回锁接受点保留：旧pending slot重用判定、metadata替换、proof及取消有独立责任；不能照搬native路径把整个alias安装搬到锁外 | V3d、V3e、V4e |
| MP07.3 | [acquireWrite provisional request/reserve](../../../krita/libs/image/pagestore/KisPageStore.cpp:4082) | 这是相邻同类窗口，须证明CPU分支的request尚未交付、不能被取消/关闭并发改写、provider存活及所有失败erase顺序，再删除空交接。异步/其它domain没有该证明则明确保留分支；不得无依据套用scope gate证明 | V2、V3d、V4e |

MP07.3已按原Preparing request/preparation activity闭合CPU、异步及其它domain的同一空窗口证明，见03e §8；没有将provider后的动态接受外移。反例：[default物化reserve后的窗口](../../../krita/libs/image/pagestore/KisPageStore.cpp:498)仍执行awaitPreparation/isMaterialized及beginPreparation，是实际共享状态消费者，**保留这次中间回锁**。

<a id="mp08"></a>
### MP08 / H：有实际释放才交接锁

| 子项 | 源码及consumer | 实施目标、旧表达退出及保留条件 | 验收 |
|---|---|---|---|
| MP08.1 | [beginMutation preparation guard](../../../krita/libs/image/pagestore/KisPageStore.cpp:1745) | candidate成功move为空时不unlock/reset/relock；仍在持锁状态减activity。构造失败、真实非空候选拒绝析构仍锁外，guard必须处理当前锁状态 | V3d、V4e |
| MP08.2 | [native冷支discardDescriptors](../../../krita/libs/image/pagestore/KisPageStore.cpp:2124)、[descriptor准备/安装](../../../krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1714) | map节点全部转移后，证明原索引仍保有同一allocator owner才省空清理交接；替换值时旧节点留在prepared内，必须锁外释放 | V3d、V4e |
| MP08.3 | [alias discardDescriptors](../../../krita/libs/image/pagestore/KisPageStore.cpp:1151) | 未创建map和新节点已转移两种空状态分别处理；复用pending、alias替换与失败非空清理保留。与MP08.2采用同一空/最后owner判据 | V3d、V3e、V4e |
| MP08.4 | [finishSegmentLocked](../../../krita/libs/image/pagestore/KisPageStore.cpp:823)：terminal且retainAdmission的adapter交付 | writes未移出，abandonedWrites为空且不重建checkpoint容器，可省空清理交接；保留原claim到OperationDelivery完成后，endSessionActivity在原owner锁下执行。非terminal重建/真实容量释放继续原窗口 | V3c、V3e、V4e |
| MP08.5 | [acquireWrite discardDescriptors](../../../krita/libs/image/pagestore/KisPageStore.cpp:4083) | generic消费同一descriptor索引，按MP08.2相同allocator/节点判据清理；不能只改native helper遗漏此处。失败request清除与实际Retire次序保留 | V3d、V4e |
| MP08.6 | [adoptInitialPage discardDescriptors](../../../krita/libs/image/pagestore/KisPageStore.cpp:3511) | 初始化consumer同步迁移同一空map政策；provider验证/部分登记回滚/未finalize限制保留，不授stroke收益。相邻terminals vector即使元素都空也可能拥有capacity，不能按元素空删除实际free | V3d、V4e |

已有[releaseStorageLocked](../../../krita/libs/image/pagestore/KisPageStore.cpp:883)先判断hot/cold/source皆空，属于已完成快路径，不重领。`cancelLocked`释放空coldPages后还可能pump退休队列，也不是无工作窗口。所有DescriptorMap清理必须检查**节点、capacity/allocator保活、最后owner及析构回调**，不能统一按`empty()`猜无成本。

<a id="mp09"></a>
### MP09 / I：冻结claim不反复全扫

| 子项 | 源码及consumer | 实施目标、旧表达退出及保留条件 | 验收 |
|---|---|---|---|
| MP09.1 | [claimsHeldLocked](../../../krita/libs/image/pagestore/KisPageStore.cpp:1102)、[sealImpl三处validateClaims](../../../krita/libs/image/pagestore/KisPageStore.cpp:2328)、[外部abort拒绝活动session](../../../krita/libs/image/pagestore/KisPageStore.cpp:284) | 保守目标：保留第一次完整claim核验，后两处只查owner operational/session等真正动态事实。scope mutex跨整个seal持有、Sealing禁止新写；逐一证明alias/removal不改变被核验的claim归属。首次失败、partial proof、容量拒绝、checkpoint重试和retainAdmission都走原终结 | V3e、V4f |

不能把`claimsHeldLocked`整体改成true；全量与动态核验的消费者须分清，调试不变量不能重新引入Release全扫。reader/last-use、metadata/root revision和provider proof仍独立接受。

<a id="mp10"></a>
### MP10 / J：legacy单页检查只访问该页

| 子项 | 源码及consumer | 实施目标、旧表达退出及保留条件 | 验收 |
|---|---|---|---|
| MP10.1 | [legacyMutationPageVersion](../../../krita/libs/image/pagestore/KisPageStore.cpp:1939)、[acquireTile ReadCache](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1594) | 已找到的单页只核对原token归属或消费封闭entry证明，去N键全查。原worker/Active/无execution/未exposed及binding版本匹配不变；read cache不能创建新代际 | V3f、V4g |
| MP10.2 | [reserveLegacyMutationPage已有entry分支](../../../krita/libs/image/pagestore/KisPageStore.cpp:1892)；backend [batch beginWrite](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:658)、[acquireTile写](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1623)、[fillRect partial](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2032)、[copy两个source分支](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2475) | 同样将已有键N范围校验收为单页归属；覆盖第二copy caller2497。缺键的冲突/legacy origin/claimEntryLocked原逻辑保留；不在持tile/manager gate时等待managed writer。与MP10.1共用原admission单键责任，不另造已验证页表 | V2、V3f、V4g |

单键校验必须校验**token与合法origin**，不能以pageClaimedLocked只判断“有人持有”代替“本scope持有”。包括IntentOnly/claim拒绝后遗留entry在内，存在entry本身不是完整权限证明。

<a id="retain-register"></a>
## 3. 保留与相邻问题登记：不得悄悄省略或冒领

| ID | 保留/待后继责任 | 依据与本包退出约束 |
|---|---|---|
| R01 | 初次claimAll、generic claimRange/new entry、growth复验、活跃execution重叠 | 真实新权限和竞争；MP04仅使已接纳内部路径不再重入它们，不能删公共合同 |
| R02 | provider结果身份、terminal、layout、operation、domain两次footprint | CPU页会swap；登记前后有实际变化。保留[registerBacking](../../../krita/libs/image/pagestore/KisPageOwnerLedger.cpp:968)与对应并发反例 |
| R03 | reader/default/last-use与metadata/root接受 | claim只排除写者。default物化的准备槽复验、AcquireRead前的清理保护和晚reader合并保留 |
| R04 | Prepared/proof重试、retirement Debt、预算容量/物理free顺序 | 已接受部分结果不能重做/丢失；不是检查名字相似即可省略 |
| R05 | registry、execution shared寿命、OperationDelivery、晚guard | 防iterator交错、跨返回的adapter交付、悬空entry。不得用栈指针/第二成功标志替代 |
| R06 | clear→filter/selection→composite真实cut | 32段/132代际保留；不能为实现本蓝图减少必要可见性边界 |
| R07 | domain journal、releaseStorageLocked及已有const消费 | 已有dirty/空集合跳过不重领；backend historyChangedPages/allocatedPages的pages已是const，不是新COW目标；cancel尾pump和terminals实际capacity仍有工作 |
| R08 | descriptor相等布局的历史规模搜索 | 在[准备函数](../../../krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1739)仍存在；本包只清其空清理，搜索替代尚无同义布局来源/失效证明和可靠价格。明确作为后继开放项，不标算法最优，不建intern cache绕过 |
| R09 | generic非CPU/异步准备的中间锁审查 | 已由原Preparing request/preparation activity证明此间隙与domain/同步终态无关，见03e §8及PLAN。原provider后动态验收、异步终结和domain保护仍保留；不能外推其它锁窗口 |

这些保留项没有新的性能通过资格。发现某个“保留”已无consumer，需建立新的子项、删除条件和反例，然后在本包统一改；不允许只改说明、留下无consumer旧API。

基线[consumer清单](../evidence/br1_cpu_management_blueprint_20261008/consumer-census.json)为每个命中指定MP/R及理由，包括声明和检索误命中。`KisPaintExecutionContext::hasReadyAccelerationSession`的contains验证capability输入的目标唯一性，没有已绑定execution可消费，归R01保留；不能按同名contains全删。清单是固定源码的词法覆盖，不替代动态调用或候选语义验证。

<a id="implementation-order"></a>
## 4. 一次完整候选的实施顺序

1. 按P1–P3闭合MP01/02/03/05，同时确定MP04内部接收形态；先跑必要的范围/权限反例。
2. 在同一候选里实现MP04/06/09/10的原claim事实传递，核对全部claim释放、checkpoint和admission移交。
3. 合并MP07/08的准备与清理锁窗口；把22个子项逐一更新到03g，不能把alias/legacy/generic/初始化项藏在“以后”。相邻项若无法合法删除，交付具体反例、较便宜替代的比较和残余数量，仍标设计差额。
4. 一次统一安全/机制/未插桩性能验收；所有实际产品hunk映射到MP或必要的R反例修复，所有失去consumer的字段/参数/helper/分支同批删除。更名、合helper或净删行不是算法达成证明。

本蓝图不改UI/tool/painter/PaintDevice/scheduler公共API，不新建全局缓存、锁、owner或预算权威。若确需跨越这些边界，先补具体consumer、等价替代不足之处及MI1–MI8账本，再形成同一可审阅方案；不预埋功能。跟踪状态、算法数量恒等式、测试落点及偏离处理均见03g。
