# 03e：同步 CPU 管理管线——保留已接纳事实，按真实变化复验

本篇维护[92 §16.153](../92_br1_m6_m8_execution_baseline.md#cpu-management-pipeline-design)的算法模型。下文“当前/原实现”对照父`6644249a4c`；实施候选已为`704d96e81c`，结果见[92 §16.155](../92_br1_m6_m8_execution_baseline.md#cpu-management-cleanup-result)及[本包报告](../evidence/br1_cpu_management_cleanup_20261008/README.md)。原蓝图证据保留，后述“理想”只指有界可构造管线，不声称全局最优。

后继[92 §16.154](../92_br1_m6_m8_execution_baseline.md#cpu-management-cleanup-blueprint)将A–J固定映射为MP01–MP10。[03f代码改动索引](03f_cpu_management_cleanup_index.md)维护删除规格，[03g唯一实施追踪矩阵](03g_cpu_management_cleanup_tracker.md)维护逐项状态/验证/预测实际差额。实施中的模型补充见§8；旧条件预测不改写成事前已知。

## 1. 这次找到的共同问题

当前协议已经有唯一claim、稳定write-set entry、execution绑定、私有版本和活动session，却在层间又把这些对象当作未接纳的输入重新解释。由此产生重复集合扫描、成员检查、排序/COW以及没有受保护工作的锁交接。这里有几处能从实际控制流证明多余，不再只是“管理可能很贵”。

最具体的反例是`borrowExecution`注释称canonical数组无需另一次分配，但`auto pages = inputPages`后，`for (const auto &page : pages)`对非const容器调用可写begin，触发SnapshotArray的detach；元素是const引用并不能阻止它。此外，backend按(row,column)排序，execution按(column,row)检查，跨行跨列的范围还会被重新排序。当前模板的最小复现已经确认两条机制；尚未对它们单独定价。

## 2. 目标管线与必要的分界

```mermaid
flowchart LR
    A[规范目标集合<br/>一次排序去重] --> B[范围准入<br/>唯一 ClaimSet]
    B --> C[原 session 接收 claim<br/>直接绑定稳定 entry]
    C --> D[每个冷页<br/>预算与退休预备 → provider → 登记与 binding]
    D --> E[按真实变化复验<br/>接受私有版本 → 像素执行]
    E --> F[冻结原 segment<br/>seal 与 overlay 联合安装]
    F --> G[原 delta 进入 canonical 发布<br/>实际释放后归还预算]
```

管线保留当前32个真实写段和132个冷代际，不跨clear后的filter/selection读者强行合并。同步CPU专用的是事实传递和准备粒度，不新增另一套metadata状态机、预算账本或回收队列。独立的epoch/root、metadata、物理预算接受点仍然存在。

| 事实 | 原证明及有效区间 | 理想消费方式 | 必须重新判断的情形 |
|---|---|---|---|
| 操作目标的唯一性和顺序 | backend建立目标；本次同步operation内集合不变 | 一种操作域排序，const借用；BoundEntry沿相同顺序建立 | 任意公共输入仍需规范化；不能把可变外部vector当不可变范围 |
| 范围claim归属 | reserveManagedRange只在claimAll成功后返回；reservation的writes/admission为private，移动不释放token | 转交原ClaimSet，接收端核对owner/token；已有entry不再次申请同一claim | 外部/泛型新键、真正的growth解锁、取消/终结；generic路径不能凭`isValid()`假定所有键已接纳 |
| execution绑定及成员关系 | scope gate内绑定原稳定entry，linked execution阻止erase/reuse | 同一BoundEntry作为键是否属于execution的唯一查询入口 | worker、scope状态、重复暴露及晚guard仍检查；相邻execution必须排除重叠 |
| 冷目标的私有生命周期 | 原claim＋session activity；provider shared owner、退休预备先于物理分配 | reserve→provider→register/binding在一个锁外准备段内完成 | provider返回身份/状态、实际domain、budget接受、default源在解锁期间物化仍需核验 |
| seal时的claim集合 | scope mutex全程持有；Sealing禁止再写/借用；外部abort受session activity阻止 | 保留首次完整claim校验，后续只复验实际可变的owner/session状态 | reader/last-use、metadata/root revision、sibling发布、失败恢复仍走原接受协议 |
| 物理驻留和预算 | domain admission、真实footprint、实际capacity及退休Debt | 继续由原provider/ledger/controller共同接受 | CPU页仍可swap；“同步返回”不意味着驻留永不变化 |

关键区别：**解开owner mutex不自动使所有事实失效。** 原claim/session保护的归属可以继续有效；reader和驻留状态则可能变化。当前部分路径对前者重复做全集复验，却不能用这种复验替代后者的真实检查。

## 3. 当前实现与可删除工作

“确定”表示源代码/最小复现已证明存在重复工作，尚不表示候选已通过产品安全或性能验证。“条件”必须先收紧消费入口/证明有效期，不能直接删除公共校验。

| 项 | 当前路径与过度工作 | 更直接的表达 | 可观察预测与边界 |
|---|---|---|---|
| A：只读范围发生COW，确定 | [SnapshotArray](../../../krita/libs/image/pagestore/KisPageSnapshotArray_p.h:35)非const begin调用detach；[borrowExecution](../../../krita/libs/image/pagestore/KisPageStore.cpp:1367)以可写局部数组作只读range-for | 规范化之后用const视图遍历，保留任意输入真正需要的COW | 每次非空成功borrow少一次无意义数组克隆，即共享控制/Storage及vector两次分配请求；同路径19次投影operation预测少38请求，不是全进程malloc计数 |
| B：顺序反复转换及再排序，确定 | [backend](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2235)按row/column；borrow按column/row；BoundEntry按相同pages顺序填完后又sort | 统一本操作域的行优先序，同步迁移Private::order/less/find和borrow规范化；BoundEntry顺序由构造保证，删除第二次sort | 任意输入只在边界排一次；矩形packed输入天然行优先。不能只去COW却保留相反比较器；无需改变epoch/overlay自己的排序合同 |
| C：cursor双重成员检查，确定 | [BoundedCursor](../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2255)先`targets.contains(next)`线性查找，再由beginWriteImpl的execution->find二分查找 | execution作唯一成员权限入口；cursor继续在无效guard后锁存failed，后续move不得恢复成功 | 少M次线性扫描，已有二分查询保留。越界不得准备新页；不能顺便移除worker、scope状态、重复guard检查。callback的targets字段/参数失去consumer后共同删除 |
| D：已转交范围再次通用接纳，条件但证据强 | [adoptReservation](../../../krita/libs/image/pagestore/KisPageStore.cpp:1867)扫描全部claim；随后borrow再次getOrCreate/find并调用[claimRange](../../../krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2569)，后者对已拥有键仍执行required与install两轮遍历 | 用原reservation的消费入口直接接收已接纳write-set并绑定execution；私有字段及唯一producer证明成立，保留owner/token/状态校验。普通borrow仍处理新键与并发子范围 | 已接纳N键的claimRange可少2N个write-set查找＋2N个claim表查找；adopt全量N次claim查询可改常数身份核对。不是删除首次claimAll及冲突等待；不引入外部可传的trusted=true |
| E：entry反复按key找回，确定 | [borrow的绑定循环](../../../krita/libs/image/pagestore/KisPageStore.cpp:1418)依次find→getOrCreate→findIndex；已存在键getOrCreate内部仍查找 | 先取一次index/handle并直接at；只有缺键走建立/回滚路径 | 已存在N键至少少2N次write-set查找；保留slot incarnation及实际新键回滚。与D是不同调用位置，可计数量，时间不得按旧桶重复相加 |
| F：冷页重新申请execution已经持有的claim，条件 | [beginWriteImpl](../../../krita/libs/image/pagestore/KisPageStore.cpp:2048)对有bound entry的冷页仍调用claimEntryLocked→claimOne | 在原linked execution入口沿用已接纳claim；无execution的直接session/legacy新键仍走claimEntryLocked | 前批四过程均96条operation内冷链，可预测这96次claim重入消失；保留Active/linked/thread检查。不能给整个132冷页无条件跳过claim |
| G：预算与provider之间空锁交接，确定 | [冷准备](../../../krita/libs/image/pagestore/KisPageStore.cpp:2140)reserve结束relock/减activity，检验局部reservation，立刻加activity/unlock进入provider | 原scope和provider存活时，使用一个覆盖reserve→provider→register/binding的activity及锁外段；最终一次回锁核验安装 | 本用例132成功Fresh链可少132对relock/unlock（264次mutex操作），不是132次等待。拒绝/异常必须同一guard恢复锁和activity；物理分配后的失败仍保留退休Debt |
| H：空清理仍交接锁，确定的条件删除 | [beginMutation](../../../krita/libs/image/pagestore/KisPageStore.cpp:1745)成功已move candidate却在guard中unlock/reset空指针/relock；[descriptor guard](../../../krita/libs/image/pagestore/KisPageStore.cpp:2123)同样不检查是否有节点 | 空candidate不交接锁；空descriptor在原索引仍保有同一allocator owner时不作锁外清理；有实际节点的替换/拒绝保留原锁外free | 分别少B、E对锁交接，B为成功beginMutation数，E为当时实际空descriptor数；不凭32 seal或132冷页伪造实际B/E计数。retained allocator引用的最后释放条件必须核对 |
| I：seal对稳定claim反复全查，条件但证据强 | [claimsHeldLocked](../../../krita/libs/image/pagestore/KisPageStore.cpp:1102)在[seal](../../../krita/libs/image/pagestore/KisPageStore.cpp:2328)三个接受区间重复扫描全部write-set；其scope mutex从入口到结束一直持有，外部abort/close拒绝活动session | 首次完整核验或已封闭接纳证明；后续保持operational/session检查，将同一稳定claim集合的重复扫描移为调试不变量 | 保守方案3S→S，少2S个claim查询；不能删除晚reader合并、metadata/root revision及provider验证。seal容量拒绝仍保留Sealing、claim和已接受proof供重试 |
| J：legacy单页查询扫描全scope，条件 | [legacyMutationPageVersion](../../../krita/libs/image/pagestore/KisPageStore.cpp:1939)为一个已找到且未暴露的页调用ownsClaimSetLocked全扫N键 | 原scope gate内核对该页token，或消费该entry的有效归属；保留版本/状态约束 | M次单页查询的额外全集校验O(MN)可降为M次单页查询。当前投影该分支次数未测，不授本用例时间收益；iterator消费者单列迁移 |

D/F/I共享一个改动责任：让原ClaimSet的接受事实随原owner生命周期传递。不能给每行另建一份已验证集合、bool缓存或第二权限表。最稳妥的第一实现是消费唯一reservation的内部入口与原状态不变量；泛型接口保留其真实接纳责任。`rebindClaimSetLocked`的循环主要是Q_ASSERT，不将其静态行数当成Release版实际删量。

## 4. 不能因“看起来重复”删除的步骤

| 表面上相似的工作 | 真实变化或消费者 | 本轮裁决 |
|---|---|---|
| registerBacking两次footprint | 两次观察夹住domain registration；实际CPU swap可发生，第二次验证物理身份/驻留 | 保留；`ledgerBackingRegistrationExcludesDomainMovement`已有真实并发测试。若将binding/驻留稳定能力直接交付，也须替换整个接纳证明，不能只删一次查询 |
| provider返回身份、operation及completion验证 | 通用provider可返回旧allocation、错operation、未终结票据；同步能力不等于调用者可信 | 保留原边界；可研究让原已验证结果继续传递，但不得用硬编码tiles3或新trusted开关绕过 |
| seal重试的Prepared检查 | 前一次部分publish/proof可能已接受，后续容量拒绝须沿原记录重试 | 不直接删除。若并入原metadata一次接受调用，需保持幂等和局部拒绝；本轮未形成可实施替代 |
| source/default/reader复验 | provider锁外期间reader可物化默认before、保留旧版本或改变last-use | 保留；claim排除写者不排除reader。不能用旧snapshot覆盖新保护 |
| domain journal同步 | 不同provider可能在后台改变驻留，默认能力无廉价dirty标记 | 已有mayHaveChanges跳过干净journal快照，不重复领取已完成优化。当前所有provider遍历能否合并需独立协议证明 |
| canonical独立delta与联合安装 | root/metadata/预算有独立接受点，sibling与reader可改变状态 | 保留；公开proof输入检查约0.017ms，不以整个commit桶给内部直达入口定价 |
| batch registry、execution共享寿命与最终释放 | iterator冲突、OperationDelivery跨返回保留claim、晚guard及失败取消 | 不直接堆改栈或移除registry。当前preflight/登记的时间间隔可能含等待/回调，不能仿照无消费者的冷页空交接删除 |
| clear→composite不同版本 | 中间visitor/filter/selection实际读者和独立失败可见性 | 132→96仍未合法；本方案优化每个必要段的协议，不减少真实可见cut |

descriptor共享值目前还通过全index寻找相等布局；多种布局时存在历史规模相关搜索。优先让原已选descriptor引用随准备传递，避免另建intern cache。不过本用例target descriptor桶仅约0.054ms，未证实比较次数随历史异常增长，暂不把它列为主要收益项。

## 5. 数量模型、价格与实施顺序

令O为非空operation数，N为其目标键数之和，D为成功Fresh冷代际数，Dₑ为已有execution的冷代际数，S为所有seal输入键数之和，M为cursor换页次数；B/E是上述真实空清理次数。

- A/B联合：无意义克隆O→0，约2O个容器分配请求删除；一次边界规范化后不再转换顺序，不再对已按序绑定的entry排序。本用例O=19，预测38请求，所复制元素数仍按N报告。
- D/E联合：已接纳路径最多可删除5N个重复claimRange/adopt查询，再删除绑定循环2N次原write-set查询。首次冲突判定、claim安装及动态capacity准备保持；新增入口不得另建索引。
- F：Dₑ次冷页claim重入删除；冻结四过程Dₑ=96，直接/clear冷链36条仍按原入口接纳。
- G/H：锁交接删除D+B+E对；D=132已由真实分支数量约束，B/E待专用机制核验。不要将“锁调用数”当锁等待时间。
- I：保守完整校验3S→S，另保留常数次owner/session状态复验。J的O(MN)风险独立于当前M尚未计数的legacy路径。

净时间模型是上述实际删除工作的独占时间，减去新接收/分支及表示成本。约0.34ms operation准备、约0.568ms冷余项、约0.04ms seal输入等旧细桶都含混合工作和时钟扰动，不能全部授予本方案，也不能将它们与跨批中位数拼成精确预测。本轮没有证据承诺再降10%或追回1ms；确定性进展是找到了可证伪的删除集合，超出了单纯给混合成本命名。

实施顺序改为一个完整候选的内部次序：先A/B/C收束范围表示和唯一成员判断，再D/E/F/I使已接纳claim沿原owner传递，同时合并G/H空交接；J按实际legacy消费者纳入同一claim审查，未覆盖入口明确保留。不要每项都另跑一次完整性能矩阵。provider直接交付稳定binding/footprint是下一层方案，必须等真实domain接纳替代证明闭合后再进入候选。

## 6. consumer迁移与验证矩阵

| 迁移位置 | 必须共同处理 | 能证伪方案的检查 |
|---|---|---|
| SnapshotArray消费与操作排序 | writeOperation、packed writeBytes、borrow规范化、BoundEntry::order/less/find；只读range-for全部改const消费 | 2×2跨行列、单行/单列、负坐标、任意乱序/重复输入；实际模板COW数为0，原输入不变；不能改变像素与输出集合 |
| cursor | 删除线性contains及失去用途的targets引用；保留失败锁存与execution权限入口 | 越界→合法再次move仍失败；首次越界不分配/写新页；已有guard必须释放 |
| reservation→session→execution | 唯一producer reserveManagedRange、接收/重绑、通用borrow新键与重叠、冷bound入口 | foreign/空reservation拒绝；同页/同线程/其它线程/legacy冲突；growth解锁竞争；原操作拒绝不污染历史scope |
| scope与claim寿命 | cancel/finish/late guard、Sealing重试、checkpoint、adapter交付前保留claim | `executionBorrowExclusionAndFailure`、`executionBorrowLateGuard`、`sealStorageRefusalKeepsFrozenOwner`、`checkpointKeepsOriginalScope`；实际free后才归还预算 |
| 冷准备与空清理 | 一个activity覆盖锁外链；预算失败、provider异常、注册/绑定拒绝、真实非空descriptor释放 | 精确预算拒绝，无未收费物理尾；activity回到0；非空析构/collector不在owner gate；保留默认物化到AcquireRead的已有安全修复 |
| seal复验 | claim不变量与动态reader/metadata区别，所有三处validateClaims及alias/removal | `sealPreservesReaderChanges`、`blockedSealValidationAllowsParallelWork`、`sealPreparationClaimsAndSibling`；兄弟页可进展，活动session阻止abort/close |
| legacy单页 | acquireTile(ReadCache)→legacyMutationPageVersion→真实binding版本匹配 | 缓存只是identity hint，不得物化新页；过期wrapper拒绝，不因另一个无关键改变已有页的保护 |

表中反例已纳入实施候选的双架安全组；数量、未插桩父/候选/upstream及Fresh/H4的裁决只查03g和92 §16.155。本次另做独立a918对照支持旧Undo回退在诊断层恢复；Teardown CPU非劣及正式默认qualification仍未闭合，不拼接旧比值宣称默认资格；M6计量缺口保持。

## 7. 实施规格的补齐与一致性

[03f](03f_cpu_management_cleanup_index.md)扩展到22个可独立核销点：J还覆盖`reserveLegacyMutationPage`已有entry分支的全scope扫描；G覆盖alias同类中间交接并对generic provisional request单列证明；H补齐alias/generic/初始化空descriptor及terminal+retainAdmission的空write-set交接。packed body的只读消费与冷bound支的第二次entry定位也明确归入A/F。default物化中实际复验准备槽的中间锁、cancel尾退休pump、非空capacity清理均明确保留。

数量模型细化为`N_a + 4N_r + 2N_e`：N_a是全部范围转交键数，N_r是转交后绑定execution的键数，N_e是绑定时已有键数；同一独立operation三者相等才简写7N，fillRect只领取N_a项。六类空清理与alias/generic分母独立计数，不能套用19/132/96。完整定义、测试ID、预测/实测差额和偏离处理见[03g](03g_cpu_management_cleanup_tracker.md#quantity-ledger)。实施时必须逐项迁移与删除，同一模式的新漏点先入表；有证据保留可结束有限候选，但仍须明示未实现的理想目标。

## 8. 实施中闭合的算法条件（704d96e81c）

独立reservation是刚建立、无hole、未暴露的原write-set；两个私有producer均输入唯一行优先键。因此接收端可沿原slot枚举直接绑定，无须再按key定位。公共history借用仍一次定位已有键。原模型额外兑现`N_d`次查询删除（直接绑定键数），成为`N_a+4N_r+2N_e+N_d`；只在四者同为同一路径N时简写8N。没有增加永久index、权限集合、trusted参数或第二owner；可失败的execution容量先于原claim移交。

generic reserve/provider间隙的有效性由原`Preparing` request、preparation activity、page claim与provider shared寿命共同保证。cancel/resolve只接受Pending，abort/close拒绝准备活动；中间只消费本地reservation是否有效，不读取受owner锁保护的新事实。该证明不依赖CPU同步终态，故原同一窗口的异步/其它domain也可合并；provider之后的request状态、writer、domain/layout、operation/terminal、初始化和Retire接受全部保留。R09只关闭此窗口，不授GPU业务性能结论。

空descriptor由原publication owner统一裁决。prepare建立nodes前已使原m_descriptors保有相同retained allocator；节点全部extract后，空map的最终析构只减非最后owner引用。替换值/拒绝时仍有节点，仍门外free；default物化到AcquireRead之间原共享准备槽保护不迁移。retainAdmission只省terminal未移出writes时的空abandonedWrites交接，原claim直到adapter完成才归还。

计数证明19/32/132语义工作未减，重复工作已退出；未插桩Stroke CPU仅降3.08%，wall区间跨零，说明数量目标兑现不等于追回主要upstream差距。每项单价仍未知，不能用0.34/0.568ms混合旧桶承诺毫秒，也不能据此推断剩余成本全不可避免。
