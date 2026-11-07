# CPU管理管线：实现、证明与差集归属

父6644249a4c，候选704d96e81cf29d16191bc3db8785859d79775e27。状态只查03g，本文件解释实现依据；PROTOCOL是事前协议，OBSERVATION_NOTES保留失败和观察器修正。

| MP / 实际位置 | 原owner内的最终表达 | 同批删除及必须保留 |
|---|---|---|
| 01/02：Store.cpp:1367 borrow；backend.cpp:2344 packed | borrow两处as_const；比较器和execution order都为(surface,row,column)；packed消费原const targets | 删除只读可写begin和末尾BoundEntry sort/less；公共乱序/重复输入真实规范化保留 |
| 03：backend.cpp:2242 BoundedCursor | execution.find唯一判定成员，归还旧guard后再取得新guard | 删除targets字段、构造参数/传参、线性contains；failed/rawData/layout/worker检查保持 |
| 04：Store.cpp:1787 reserve、1873 adopt；WriteCoordinator.cpp:2623；backend.cpp:1994/2138 | 原唯一reservation只在claimAll成功后返回；原admission原子移动完整writes/claim。可失败execution存储在移动前准备，直接遍历原slot绑定；fill只移交 | 删除adopt的N键全验及独立路径generic borrow/claimRange；删除旧rebind API及旧测试consumer。history仍真实borrow，初次claimAll/growth复验不变 |
| 05：Store.cpp:1420公共绑定 | 已有key一次findIndex，直接at；缺键才getOrCreate和重新取得index | 删除已有键find/getOrCreate/findIndex三连；原created位图、失败erase/incarnation保持。独立移交沿slot绑定为0查询，比预报再少N_d |
| 06：Store.cpp:2049/2097 bound冷支 | linked execution的原entry/claim已接纳，沿用当前scope gate内entryIndex | 删除bound的claimEntryLocked和claim后findIndex；直接、semantic、legacy新键继续真实准入 |
| 07：Store.cpp:1160 alias、2164 native、4118 generic | 同一原activity/guard覆盖reserve与provider；实际接受点回锁 | 删除reserve/provider间空relock/unlock；拒绝/异常先恢复锁，原request/entry继续失败或恢复，实际分配后仍退休Debt |
| 08：Store.cpp:834/1743及四个descriptor consumer；PublicationCoordinator.cpp:1756 | 原publication集中空map/非空释放政策；空candidate不作reset交接；terminal retainAdmission未移出writes不清理空abandonedWrites | 删四份无条件descriptor清理、成功空candidate和空write-set交接；非空节点/capacity/最后实际free、cancel尾pump、default读物化原窗口保留 |
| 09：Store.cpp:2355 sealImpl | scope gate持有且Sealing禁止写/借用；首次完整claim核验一次，后两次只复验owner operational/session | 删后两次稳定集合全扫；reader、metadata/root、provider proof及Prepared/重试仍独立验收 |
| 10：Store.cpp:1923 reserveLegacyMutationPage、1970 legacyMutationPageVersion；WriteCoordinator.cpp:2616 | 找到原entry后，只查该key在原claim表的owner/token/合法origin | 删除单页访问中的全scope ownsClaimSet；缺键仍claim，ReadCache仍须匹配binding版本；全部原copy/fill/iterator caller不新增分支 |

`Execution::Private::link()`的两个consumer是公共borrow和原reservation接收；它只统一原intrusive挂接，没有新状态。`adoptReservation(..., execution*)`的可选输出表达实际是否需要绑定，不是trusted/alreadyClaimed开关。3个新增内部owner方法分别承担完整claim移交、单键归属和descriptor清理，均替代旧工作，原public/protected主干接口不增长。

生产7文件+158/−106，测试3文件+66/−28。净增长52生产行用于可失败存储前置、原接受的直接绑定、原子移交和共同异常/清理政策；没有新增永久字段、owner、集合、锁实例、队列、缓存、生产计数器或恢复域。不能靠净删行裁决复杂度：实际少了一次独立operation通用准入、第二成员表、排序、重复全集检查及空锁交接。

## 权限与并发证明

reservation构造器虽公开，writes/admission为private；只有Store::reserveManagedRange可填充，且仅在claimAll成功后返回unique_ptr。它无公开增长或releaseOne入口。接收要求原admission.owner=this、token有效、writeSet正是range.writes、非空、目标set为空且无有效claim、owner operational。session再要求Active、fresh、正确worker、无execution，并在scope→owner原锁序内消费；失败由原range RAII释放。move后仅目标ClaimSet有效，其writeSet改指向原session。Debug完整断言不计Release扫描收益。

原fresh write-set按唯一row-major目标插入，未erase，slot枚举顺序就是搜索顺序。两个私有backend producer均满足该合同，Debug断言明示。公共borrow没有这个私有保证，保留输入规范化、新键、真实冲突/growth复验、活跃execution重叠以及回滚位图。linked execution和晚guard共同保有原scope，禁止稳定entry erase/reuse；免claim仅发生在已经找到合法bound的入口。

scope mutex覆盖seal及其锁外provider/proof窗口；Sealing阻止新写/borrow。其它ClaimSet不可按本token释放native键，generic releaseDirect只处理自己的origin/token。外部abort/close因原session activity拒绝；alias/removal改变准备结果，不撤销该scope claim。因而首次核验后归属不变，但owner operational、reader、metadata/root revision等仍可能改变，各原owner继续复验。checkpoint/容量拒绝保留已接受proof和原claims，重试不重做。

generic的中间间隙由原Preparing request、preparation activity、page claim和provider shared owner保护。cancel/resolve只接受Pending；abort/close不能跨准备活动。reserve结束与provider调用之间只判断本地reservation，无新的owner事实读取。异步/其它domain也有相同保护，证明不依赖同步scope或CPU终态。合并只涵盖此窗口；provider之后request是否仍Preparing、writer/generation、layout/domain、operation/terminal、初始化、Retire和失败记录原样保留。R09没有独立锁窗残留。

四类descriptor的prepare先让原m_descriptors保有同一retained allocator，再创建nodes。空临时map没有节点，最后析构不是最后accounting owner；非空替换或拒绝仍门外清理。初始化terminals vector即使元素都空也有capacity，保留实际释放。default物化有awaitPreparation/isMaterialized/beginPreparation共享消费者，保留其真实回锁及AcquireRead前保护。

## R01–R09与真实反例

R01首次权限/新键/growth/重叠、R02 provider/domain/两次footprint、R03 reader/default/last-use、R04 proof重试/预算/退休Debt、R05 registry/shared寿命/delivery、R06真实clear/filter/composite cut、R07已有快路径及真实capacity、R08 descriptor历史相等搜索均保留。R09按上面的request独立证明仅删除该空窗口；其它domain/异步动态接受保留。

同源八安全组各ARM64/x86_64一次，9224/0/0；结构调用图、architecture检查及工具自测通过。具体反例包括原executionBorrowWorkers（65键跨worker/index增长）、ExclusionAndFailure、LateGuard，checkpoint/容量拒绝保留FrozenOwner，sealPreservesReaderChanges、blockedSealValidationAllowsParallelWork、sealPreparationClaimsAndSibling及ledgerBackingRegistrationExcludesDomainMovement。完整Reference/manager原generic、init、alias、wrong provider/domain、取消和拒绝终点在同源组内执行，不授未运行的TSAN/其它平台资格。

新增manager CanonicalRange覆盖72页、负坐标、跨行列、重复/逆序rect、反向搜索全部页、失败后下次成功、首次越界→有效仍锁存。合法页在callback前已预备，因此断言越界相对callback前不新增代际，不能要求整个operation预备为0。Reference补空reservation拒绝、foreign admission/token、GenericWrite及IntentOnly不获单键权限；有效foreign reservation无公开producer，拒绝依据为上述私有闭包/owner检查，不伪称动态伪造过它。

## 数量与有限收口

counts-summary按Projection/Stroke其它/all phases分别给出每个实际计数的calls/hits/amount，8过程全部保留。19/32/132及96 bound冷链稳定；clear范围使父N_a/S在154、158间波动，commit10–14也非固定。只按实际分母比较，不删除波动过程或从跨批值推断因果。

投影19 clone/96元素/768B、19次第二sort、96 contains、96冷claim重入、96冷支二次定位均归零；132 Fresh中间锁＋32 candidate＋132 descriptor＋32 retainAdmission空锁共328对消除。write-set findIndex1218/1222→454；40次已有legacy预留从284/316个claim查询变40个单键查询。alias/generic、legacy read及初始页无Stroke投影命中，不授此处净删量；代码条件式及安全覆盖单列。38分配请求来自实际模板结构推导，不是全进程malloc计数。

原模型N_a+4N_r+2N_e保持作事前预测；直接slot实现额外删除N_d=96，实际可删除逻辑查询模型N_a+4N_r+2N_e+N_d。全体独立路径相等才简写8N，fillRect只有N_a。不要将这个不同表/调用位置的逻辑数与findIndex实测差再次相加。

时间只取固定未插桩父/候选及upstream比较，pointwise区间不授正式family。即使22项清理结束，剩余upstream差距、原默认qualification、metadata同义驻留分母、CP0 required、M6校准仍开放。下一优先应为未对账的canonical发布/allocator联合责任及read/merge余项建立必要成本下界和可删预算；不重领这些已退出的扫描/空锁，也不在没有预算时开启新容器重写。
