# 03h：CPU 版本管理全生命周期理想算法蓝图

版本边界（2026-10-12）：本页算法/接口与LP或早期成本数字属于各自冻结批次。当前ed0f229821已完成CPU私有结果与captured保护统一；旧prepare/publishPrivateWrite、AdoptPreparedWrite、ReplacePrivatePreparedBacking不再是当前实施目标。后续只沿[新版流程及清理账单](../evidence/br1_pipeline_refactor_20261010/unified-rw-r1/RESULT.md)与[原33×6矩阵](../evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#unified-rw-implementation)推进；不重开本页已结算矩阵。

本蓝图从[差额账](../evidence/br1_current_upstream_cpu_ledger_20261009/README.md)和源码704/tree4e7fc164起步，现已按实际实施调整最小事实表达。候选`d182a34bd0196079bc40d2ab7d00b8e326e4a58a`，完整结果见[03j](03j_cpu_lifecycle_tracking_matrix.md)与[实施报告](../evidence/br1_cpu_lifecycle_implementation_20261009/README.md)。下文“当前差异”指704起点；设计删量不等于净时间收益。[03i](03i_cpu_lifecycle_edit_index.md)维护改动/删除位置，03j是唯一实施状态账，[92](../92_br1_m6_m8_execution_baseline.md#cpu-lifecycle-implementation)裁决资格。

LP01–LP10仅为本包责任ID，不新增项目阶段。之前03e–03g的MP01–MP10、22子项已经结算，保持关闭；本包不重复领取原19 clone、96 claim、328对锁、824分配请求和小memcpy改进。本方案覆盖明确的责任闭包，不声称静态检索能穷尽全仓库所有未来瓶颈。

后续优化项先按[03k候选筛选](03k_first_principles_candidate_selection.md)审查合法删量、实际命中和净时间预算。本包“结构已见/责任有权重但未定价即可待实施”的选择方式不继续沿用；原实施结果保持冻结，不以新规则改写旧预测或重开03j。

<a id="cost-boundary"></a>
## 1. 目标、证据和预测边界

目标是减少**同一真实绘画任务中，必要版本事实被重新投影、复制、安装、清理和通知的总成本**。前台交付与后台最终free共同验收；把工作移到worker不是CPU删量。必要像素、真实读cut、首次写权、provider接纳、全批原子发布、旧读者与实际预算归还保持。

| 最新证据 | 可支持的判断 | 不可领取的预算 |
|---|---|---|
| detail同批额外CPU：projection 3.697516、stroke jobs 2.314388、job外1.298971 ms，共7.310875 ms | 投影管理链优先；两边937/19任务，非任务数放大 | 三项都不是可全删成本；不能与其它批次相加 |
| 同批current独占cold/seal/commit为2.142911/0.792826/0.654004 ms，共3.589741 ms | LP01–LP04的覆盖责任有足够权重 | 包含必要provider/内存/协议；不能承诺省3.59 ms |
| census原reclaim 1.265625、monitor 0.175500 ms；主线程近似相等 | LP05–LP08必须跟前台一起审查 | 尚无任务类型单价，不能全算metadata、空唤醒或净删量 |
| 当前源码有完整WorkingVersion投影、按页锁、重复通知 | 可设计减少表示和遍历的算法 | 静态存在不证明该分支频率、耗时或预期百分比 |

证据强度：责任层定位高；下文标为“结构已见”的冗余有源码依据；直接改写的语义等价要经共享策略和oracle反例证明；实际净收益未测。这里不提供伪造的统计置信度。108过程的责任对账已经停止，不再以扩大覆盖采样代替实施。

<a id="ideal-flow"></a>
## 2. 不良路径与理想路径

当前常见路径：

```text
原reservation/execution已接纳
 → exact base/provider/cold分配/实际backing登记
 → applyProjectedSequence：找少量相关版本，却复制它们的replica/lease/last-use/capture
 → 在WorkingState上运行Acquire/Prepare，再把相关整记录写回
 → 像素工作
 → seal：一次versionSnapshot检查重试，再投影BeginPublish/Publish并整记录写回
 → canonical候选：投影完整相关版本 → 保存旧publication字段 → 状态机 → 比差分
 → 每页多次分片锁/统计锁，按分片再遍历全部entries
 → 全批claim后安装delta，释放claim，activity仍留给cleanup
 → cleanup逐页锁/销毁；后台job逐个排队、通知、完成再重新取队列锁
 → reader/history/retirement/epoch等原消费者推进，真正free后归还费用
```

理想路径（不合并真实业务cut）：

```text
原owner/索引中读取本次转换必需字段
 → 共享语义策略先验证并产生最小改写；实际新增存储先接纳
 → 若因容量/provider解锁：复验原revision/identity，失效则重算，不复用旧指针
 → 在原分片锁内一次安装新增记录及实际变化字段，未变保护链保持原位
 → 像素工作
 → seal同一原metadata调用内核对已完成事实或原子执行private发布
 → canonical按(分片,key)一次组织：只保存字段delta/真正addition/authority
 → 全批claim成功后才安装；prepare/install不能同持多把分片锁
 → 候选原存储在门外按有界同分片run清理，不再析构根本不需要的状态镜像
 → 原队列只有有效的状态变化才唤醒；每个实际任务仍有唯一finished/free
 → 原reader/history/retirement/epoch消费者满足条件后释放原资源
```

原子性分两层：单页局部转换在该分片锁内接纳；canonical保留publication/root协议与全批claim。分组只减少锁往返和遍历，不能把“先验证全部”改为“边验证边发布”。所有准备、外部调用、物理析构仍遵守原锁序。

<a id="shared-policy"></a>
## 3. 实现形态：一个语义政策，两种存储消费

实施审查确认原`applyPolicy/applyKnownValid`已经是reference和production共享的唯一政策。因此以更小表达替代原拟议三个delta helper：限定序列用`records.project<false>`构造必要版本/replica标量事实，原状态机决定接受与新值，metadata只安装真实字段；ordinary publication由原policy在实际publication/preparedBy变化处直接写原candidate.deltas。没有复制guards或第二状态机。recoverable与任意effects序列继续完整投影。

优先用栈值/原Data字段和内部函数；不增加虚接口、公共trusted参数、永久fast-path标志、第二版本表、缓存或通用策略框架。单页delta至多保存原header变化、base pin变化、新target/目标字段；canonical原Publication持实际delta和真正addition。delta不是权限，其安装权来自原锁、identity、revision、capacity reservation和publication claim。

reference对新增路径仍须比较完整可观察状态/拒绝/效果，另用固定反例断言策略本身；仅让两种存储调用同一错误helper并互相比对不够。generic、多步任意sequence、recoverable retag和产生retirement effects的路径未被证明等价时继续原实现，不能静默把失败变成成功或在直接安装了一半后fallback。

<a id="lp01"></a>
## 4. LP01：Fresh/Adopt冷准备的最小改写

**当前差异。** `preparePrivateWrite → applyOwnerSequence → applyProjectedSequence`已只选择相关版本，但`records.snapshot/project`仍复制这些版本的replicas、readLeases、pendingLastUses、capturedReadViews；随后`putAcceptedBatch`替换相关记录。选了少量版本不等于只处理变化字段。Fresh只需校验base/target、给实际base authority加一个pin、增加target并设置writer/nextGeneration；旧base保护列表不应随每次冷写复制/重装。

**理想算法。**

1. 仅对单独AcquireWrite、实际生产的AcquireWrite+PrepareWrite、AdoptPreparedWrite接入共享策略；不凭count=2跳过kind/同一writer/operation/key检查。
2. 原分片锁下读header、exact base、实际authority、目标generation和physical slot索引。验证transaction可见、Valid authority/合法virtual default、key/provider句柄、pin/generation溢出、target未存在/物理不碰撞；Adopt保持Discard、直接Prepared且不新增writer pin。virtual before在provider窗口物化的事实继续由现有WriteCoordinator重新选择。
3. 计算**真正新target**的一份version/replica、必要activity和索引容量，沿原arena/budget准备。需要解锁增长时只保存值身份和revision，回锁重新查索引/复验；变化则整次重算。任何拒绝不改base pin/nextGeneration/writer。
4. 全部可失败检查和容量接纳完成后无失败地安装：插入target，增加需要的base pin，写writer及nextGeneration；两步生产序列直接得到Writable，但逻辑计数仍记录两次接纳。不重写base replica/overflow链。
5. provider失败、初始化未完成、后续cancel保持原收尾；是否将Cancel/Fail也改成delta属于LP08.4条件责任，不能绕过实际retirement debt。

**删除目标。** 符合入口中的完整保护镜像、inputVersions数组、对未变base的`putAcceptedBatch`和对应保护临时析构归零；必要标量WorkingVersion仍存在，多replica可spill并实际收费，不能记“旧版本值=0”；新增target及物理容量保持。原单页索引查询、copy/default fill、backing登记/retire准备不在删量内。结构与语义验收见03j，净时间不能由删量直接判定。

<a id="lp02"></a>
## 5. LP02：private seal的局部发布与重试同次接纳

当前`publishPrivateWrite`先`versionSnapshot`判断以前是否已发布，再进入BeginPublish+PublishWrite的完整相关记录投影；第一次路径两次进入metadata，重试事实与真正接纳分离。

理想由原metadata的一次私有入口承担完整责任：锁下先匹配version/transaction/target是否已经Prepared；匹配则幂等成功，否则在同锁下执行共享private策略。验证Writable、writer/operation/target、`canPublishWriteReplica`和exact before-image保护；先检查合法logical default或真实base pin>0，再修改target validity/authority/publication/preparedBy、base pin及清空writer。无新增记录的成功路径不复制任何保护列表，不新申请arena，不先改writer.phase再遇到失败。

单独PrepareWrite/BeginPublish经原共享guards后只改header；异步PublishWrite、CancelPending、FailWrite及有effects分支仍遵循原通用协议；不能用“CPU”忽略延迟取消。同步两步中Publishing没有锁外观察者，可省中间存储写入；真实final状态和两次逻辑接纳不变。已有Prepared的识别也不能接受foreign owner/transaction/target。

seal中的proof创建/验证、可写binding归还、overlay交付和canonical之后真正读cut继续存在。32写段和132代际不能因为此优化降为96；旧reader/capture有真实消费者。删除第一次路径重复snapshot/分片进入与整个private镜像重装，不能把proof/private/canonical三层合成一个未定义终态。

<a id="lp03"></a>
## 6. LP03：canonical直接构造语义delta

当前普通`preparePublicationImpl`先取相关版本的完整工作值，保存旧publication/preparedBy，再执行状态机并比差异。其实CommitTransaction、ReplaceDefaultPixel、RestoreCommittedVersion通常只改变header、publication/preparedBy及可选默认addition。

| 转换 | 理想读取/修改 | 不可省的反例 |
|---|---|---|
| CommitTransaction | 当前published、目标Prepared及同transaction Prepared链；检查最新代际，输出old→Historical、其它Prepared→Historical并清preparedBy、target→Published、header | 不能只改old/target而遗漏同事务较早Prepared；另一更晚Prepared必须拒绝 |
| ReplaceDefaultPixel | published/default目标身份、writer/mutable事实、existingReplacement、target物理归属；输出两处字段或真实新default记录 | 存在writer/mutable、authority不符、物理别名均拒绝；已有Historical复用 |
| RestoreCommittedVersion | published、exact历史/默认target、writer/mutable和authority；必要时新增virtual default，保持nextGeneration高水位 | 当前target同published可只改epoch；不能恢复到新填充的其它default或覆盖晚reader |

共享策略决定delta；原record索引提供最小事实，原Publication的`deltas/installRecords/backingAuthorities`提供跨解锁收费存储。原installRecords暂存必要标量输入，锁外policy后只保留真正addition；只为真正addition保留完整WorkingVersion；现存record的replica、lease、pin、last-use、capture保持原位。authority从已读取的exact record保存，保留原排序/版本精确查询；不能删掉还有epoch/预算消费者的authority表。

普通路径完整保护镜像、“复制全部旧publication再压缩”的中间数组及差分循环退出；必要标量值不计入删除。recoverable仍要真实搬移物理归属，不能借普通字段delta删掉它的base/target替换和strict revision；detachment已直接做语义变更，不重领既有优化。

prepare与install之间仍以原revision检查所有动态变化，继续全批claim、原root/canonical/adapter一致性交付。**本包不引入第二个semantic revision以忽略reader变化**：它会新增失效政策，未被计价也不是删除镜像的必要条件。claim成功后字段安装不会覆盖现存保护链；仍按原规则拒绝已过期候选。

<a id="lp04"></a>
## 7. LP04：候选按分片组织，一次遍历负责同一批事实

结构已见：重复key用`any_of(entries)`造成最坏N(N−1)/2比较；growth定位线性扫分片集合，按分片revalidate又遍历全entries；activity预留、统计和claim/install各自按页拿锁。它们与跨锁动态复验不同，前者可改变表示，后者有真实失效者。

理想先在**原Data.entries**记录输入身份及暂存的inputOrdinal，按`(stableShardIndex, fullPageKey)`排序；相同key必在同分片并相邻，做一次重复检查。inputOrdinal仅用于prepare内部回读同步借用输入，之后原Entry保留该标量但不再消费；没有新的输入owner。现有Entry中的shardOwner保活不再复制到新表；非detachment的原ShardArenaGrowth保存本组begin/count以代替全表筛选。detachment从相邻entries直接取组。不得按裸指针关系排序或只比hash认定key相同。

按组执行：收集最小输入→锁外策略/容量准备→本组动态复验及activity接纳→下一组。每个必须解锁的增长窗口重新复验本组全部依赖；不能仅验证第一个页。安装仍分为**所有组claim完成 → 所有组安装**，只持一把分片锁；失败按已claimed前缀逐组解除。以≤16页的连续run作为持锁上界起点，跨run释放锁仍由已接纳claim/原revision承担保护，不能无界扩大锁驻留。

两个独立统计循环移入demand/activity原锁；拒绝时仅结算尚未记录的已成功policy前缀，回滚本次预记的prepared页数。拒绝policy中途的临时partial delta不再计为已准备工作；完整成功与后来容量/复验拒绝的工作量保持，不能为了少锁漏报失败计数。prepare/installed/rejected计数是不同事件，不能并为一个数。

数量模型：重复检查从最坏N(N−1)/2到排序O(N log N)+N−1；若内部输入已证明满足该新顺序才可免sort，旧(surface,row,column)并不等于分片顺序。growth全表筛选S×N到N；每一个适用按页锁pass由N到G，G为实际分片run数且N≥G≥S。增加排序、inputOrdinal/组边界字节及可能延长持锁时间，要从净收益扣除；小N可能没有收益，不能给132页总量直接套一次大batch。

<a id="lp05"></a>
## 8. LP05：原候选按有界分片run清理

`Data`本身已是收费reclamation job，不能再领取“删除任务分配”。当前每单位先销毁publication，再`Entry::releaseActivity`逐页锁；后台`invoke`每次`clearBatch(1)`，最多16单位/约1ms；≤8同步、pending≤1024以及超过界限的同步fallback均存在。

理想与LP03/04共同交付：不生成的镜像无需清理；其余沿原Data反向连续run处理。先在锁外销毁本run的publication payload，逐单位检查原时间/单位界；随后一次分片锁归还这些entries的activity，再在锁外弹出entries/释放shardOwner。用原payload索引和栈上已处理数量，不新增owner/heap临时队列。不得在分片锁内析构payload、释放最终budget owner或清空整个Data。

同步`clearBatch(maxUnits)`、异步invoke、准备失败`cancel`共用“activity在原锁内恰好归还一次”的原责任；`releaseActivityLocked`若引入，必须同时替代原逐页锁实现，并保留无reservation/已归还的幂等检查。失败候选的growth reservations和releasedBlocks仍按原Data终点释放。异步最后pass将pendingUnits/pendingCandidates的结算合于一次idleMutex区间；保留统计原子可观察性、maxima、idle判定和executor finished之后的实际对象free。

本包保持8/16/1024阈值、每单位deadline检查和公平yield；没有单价前不延长batch、不删除时间界、不把所有候选同步销毁。16单位和1ms都不是任意析构的硬实时保证：一次析构可能越界，仍需记录最大pass和持锁尾延迟。run活动归还由N把锁降到G_cleanup把；最终pass每候选至多少一次idleMutex进入。LP03删除的payload与LP05清理少量只记一次寿命节省。

<a id="lp06"></a>
## 9. LP06：原回收队列的通知、锁和线程身份

三个结构已见的局部替代，均留在现有ReclamationExecutor：

1. `enqueue`只有“队列原为空且worker不在执行”才需jobChanged通知；非空追加/运行中追加不唤醒。检查与链表挂接在原m_jobMutex内，worker在同锁下决定wait，避免丢醒；stopJobs的唤醒保留。
2. `runJobs`在上个任务invoke/dispose/finished全部完成后，一次m_jobMutex区间完成旧任务终结、决定drain、取下一节点或wait，替代现有“结尾锁→下一轮头锁”。只取一个job，不摘走整队列；原finished回调自重排仍入队尾，顺序与公平不变。
3. `reclaimerThread`只表达worker身份，原生产consumer均与currentThreadId比较。可在worker开始/退出各写一次，替代每job置入/清零；不用新TLS，也不改变主线程/其它线程判断。线程退出先清零，stop/join保持，不能留下已退出ID被系统复用。

J个实际job、B次从idle启动：job通知J→B（0≤B≤J），worker队列锁约2J→J+1，身份原子写2J→2/worker lifetime。enqueue锁本身保留；`nullptr`能力检查、外部stop拒绝、worker内最后释放继续enqueue、reusable job及final context保活全部原样承接。数量可证明，J/B未测、时间未定；不能据此领取1.265625ms全部后台CPU。

<a id="lp07"></a>
## 10. LP07：monitor只对可改变等待条件的事件通知

`Delay::cancel`目前即使未queued仍notify；arm每次notify；wake对同节点已有ready会去重，但不同节点仍逐次notify。

理想保持原clock mutex、intrusive任务/ready表及generation：cancel始终失效armed/readyGeneration，只有改变最早deadline才通知；arm在原锁内对比旧/新最早deadline，只有等待条件改变才notify；wake在原锁内只有ready队列由空变非空才notify。移除最早任务后即使deadline延后也通知以免旧超时；相同deadline换节点不要求再次唤醒。clock外的queuedPin/dispatch析构保持。无需另设“monitorSleeping”镜像状态。

任何已被monitor取走的任务，cancel仍必须使takeReady失败；相同对象rearm递增generation保持。真实ready到达不得被未来retry阻挡，preferWake与due timer交替公平保持。stopDelays仍强制唤醒并清理。数量：notify次数从全部cancel/arm/首个节点ready降至“最早deadline变更+ready空到非空”；实际减少次数须分类计数，不能假设全部cancel为空或全部monitor CPU是无效唤醒。

<a id="lp08"></a>
## 11. LP08：全部后台消费者及失败路径的闭包

本项既包含待证明替代，也明确保留已经较直接的实现。不能从约1.4ms推断下面各项均值得改。

| 原责任 | 理想算法/本包判定 | 删除条件与禁止遗漏 |
|---|---|---|
| read last-use | 原ready链去重、最多32，finished负责再次调度；producer只交接原节点 | 条件项：仅证明`jobScheduled && !retryScheduled`时finished必消费ready/cleanup后，才合并producer重复wake；新terminal可能解除retry，不能仅readyQueued就return。未证明不改 |
| history | 原Work/32候选/根预算、repeat与原reachability cookie；只扫描已请求key | 保留现有有界算法。只有证明同一key、同一有效root扫描世代且无reader/retained变化，才能去重repeat；不新增reachability cache，不删因释放产生的rescan |
| retirement + budget waiter | 原notified/inFlight与scheduled/dispatchAgain保存执行中到达事件；实际free后归费 | 保留原接续。两次通知可能夹着capacity/terminal变化，不能按次数合并；provider gate内不可直调owner。队列拒绝/晚close仍由原owner终结 |
| epoch tree free | 原非递归释放链，最多128节点/pass；child析构可追加同链 | 条件项：先在原mutex摘下最多剩余budget的连续节点，锁外逐个free；child仍入原链，下批继续。不新分配队列、不超128、不提前returnLive；实际节点数未知 |
| metadata Cancel/Fail/Abort/retire等 | 已有read/capture/history局部更新保留；有effects的通用路径先Debt后接纳 | 条件项：LP01–03完成后用相同字段依赖法检查剩余镜像；必须列出原效果、容量拒绝、复验及退费，不能借“相似”直接修改通用fallback |
| Store/owner最终释放 | 原lifetimeReferences和terminalCleanup，最后物理存储/回调free之后释放root | 保留。不能减少root引用来伪造refcount收益；queued/finished/late guard/stop拒绝都要核验 |

epoch摘链算法在原mutex内切断local尾的nextReleased并更新first/last，沿本地原节点指针销毁；真正child回调重新入原链。在一个pass内可补取剩余预算，但不能为了再取而递归；finished原taskPin及拒绝同步drain仍是唯一owner。减少的是每节点mutex往返，节点free/递归子释放数量保持。

LP08.4的剩余转换不留成一个无边界的“优化metadata”任务。逐类理想表达如下，生产路由全表在03i；这是可替代表示设计，仍需命中和等价证据才启用：

| 转换责任 | 最小算法与实际变化 | 必须先获得的删除许可 |
|---|---|---|
| AcquireRead | 原lease索引检查同页唯一性、exact version/replica可读性；预留一个真实lease overflow节点后只追加该节点/必要字段 | 不能因只读目标就漏跨版本lease碰撞；增长解锁后复验；任意多步sequence不能分次接纳 |
| 单步PrepareWrite/BeginPublish | 校验writer与目标replica，原锁内只改writer.phase | 多步原子合同、异步phase真实消费者均保持；不能顺便删除phase |
| CancelWrite/FailWrite、CancelPending的PublishWrite | Publishing取消仅改CancelPending；真正终结先校验所有目标使用者与before pin，列出实际retire handles，接纳原Debt，再复验并移除目标/减pin/清writer | 有effects时必须锁外Debt准备；复验失败取消同cookie，不复用旧指针或提前移除记录 |
| AbortPreparedVersion/AbortTransaction | 沿原transaction链；有captured view的版本仅转Historical，其余验证idle并准备全部effects，全部可接纳后再变更 | 同事务writer仍拒绝；不能逐版本先删成功部分再因后页失败；保留captured历史和原原子结果 |
| ReplacePrivatePreparedBacking | exact单replica/Prepared/transaction及全部保护为空检查；原Debt和新物理索引容量预备后换真实一条replica/authority | physical碰撞、late capture/reader、旧backing真实退休不能免除 |
| AttachHistoricalDefault/MaterializeDefault | 物理归属核验后只增加真正默认version/replica与authority；writer/header未变部分不复制 | 同一exact default、已物化拒绝、原provider/reader pin窗口保持；新增arena/索引必须收费 |
| 单步DetachPreparedVersion | no writer及exact Prepared/transaction成立后只改publication/preparedBy | ordinary prepared detachment已经更直接，不重复领取；任意sequence仍保持整体原子 |
| Begin/Commit/FailAuthorityHandoff | exact双端点及handoff identity检查；只改两端pin、handoff字段及成功authority | 实际materialize/retag/domain、pin溢出与晚completion保持；不把CPU条件授GPU |
| ReleaseRead/AcknowledgeLastUse、capture release、history discard | 继续原局部索引修改/原有界扫描与Debt，不恢复成完整镜像 | 这些已经有直接实现；只有原generic兼容caller实测触发并有同义证明，才另记新增迁移 |

上述无effects固定字段分支适合原分片内直接改写；有effects分支需要“原收费handle packet→Debt接纳→revision复验→无失败安装→门外效果交付”，不能为了追求一个统一helper而强迫两者都建完整WorkingState。若多个转换在一条任意sequence内互相依赖，当前通用工作值仍是回滚边界；未设计完整合成delta前保留它，并记录调用次数/必要大小，不开新的通用解释器。真正provider materialize/retire状态亦有外部完成者，作为闭包控制保留，不能仅从局部owner转换套用。

<a id="lp09"></a>
## 12. LP09：descriptor已有不可变值的直接传递

`prepareDescriptorAdditionsLocked`为共享布局而线性查m_descriptors及临时nodes。已有exact base描述符时，理想从原descriptor索引传递同一个`shared_ptr<const Descriptor>`，经完整值相等核验后直接构造目标map node，避免全历史布局搜索。它是原值保活，不是新layout缓存/权限；surface/default变化、initial/generic输入或不相等时仍走原构造/去重路径。

拟议内部参数是可核验的不可变值，不能公共trusted bool；WriteCoordinator/Publication共同持有直到原map安装或门外释放。只有实际命中且搜索长度已计数的调用才授删量。现有索引节点/容量/immutable共享仍必要；不能用每version重新分配替换全扫后宣称优化。此项是条件候选，尚无频率/单价，优先级低于LP01–05。

<a id="lp10"></a>
## 13. LP10：第二梯队和不可借走的保证

operation剩余0.887282ms、pixel callback独占2.286166ms、capture0.373214ms、merge residual1.049696ms是当前责任桶，不是净回退。理想仍为每真实cut一次选择、在原execution/guard寿命内复用稳定binding、实际像素只执行一次；source/current/G0/oldData不能共用不相同的cut。原pin2420→152试验未确认整笔收益，不能再次当确定项目。

本包保持入口/终点核验：独立cursor、packed、history借用、fill/alias、legacy、generic/异步、初始化/default、capture、Undo/Redo、cancel/close。只有证明某一相邻调用没有新reader/epoch/domain/失效者且复用原owner比新增cache便宜，才将LP10条件行转入实现；否则以具体consumer保留。**这些开放项仍留在03j，不因主项完成而消失。**

<a id="forecast"></a>
## 14. 统一数量与性能模型

LP01/02每个合格事件i记录：被选择旧版本数Vᵢ、复制保护元素Pᵢ、旧记录安装数Iᵢ、实际新增记录Aᵢ。实施目标为完整保护镜像Pᵢ→0、未变记录重装→0；必要标量版本Vᵢ保持并实际计数，Aᵢ和真实改变字段保持。不能把132冷页直接当V/P/I，也不能把省一个WorkingVersion等同省一次malloc（small_vector有内联存储）。LP03记录输入版本/实际delta/addition/authority数，不因不复制保护链就减少逻辑读者数量。

锁、通知、比较和物理存储分别记账：LP04的N/S/G按每候选统计；LP05按cleanup run与成功/失败分开；LP06记录J/B及队列深度；LP07区分空cancel、非首deadline变化、有效ready；LP08按消费者记录pass/units，条件分支未触发填0而不是套全部线程时间。全部计数用派生低扰动观察，不在产品常驻细时钟。

```text
净CPU节省 = 删除的镜像构造/重装/最终析构
          + 删除的比较/锁/通知/原子写
          - 新delta策略/输入排序/组边界/复验/分支/存储成本
          - 因更晚回收或更长持锁引入的全寿命成本
```

同一对象“未构造”与“未析构”可分别记录实际动作，但时间由该寿命的互斥区间结算；LP03与LP05不得重复领取同一析构。CPU与wall分别报告，关键路径、并行度和尾延迟可改变wall；新源码不开观察的父/候选/upstream对照才确认收益。尚无单位净价格，**目前可靠预测是可删动作公式，不是新的毫秒或百分比承诺**。

完整包顺序：先LP01–03共享政策和小改写，再LP04/05前后台共同表示，然后LP06/07；LP08/09/10在同次责任审查内给出实施或具体保留证据。不能以通知去重先见到正值就宣称主蓝图完成。统一验收和有限停止见[03j](03j_cpu_lifecycle_tracking_matrix.md#verification)。
