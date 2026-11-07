# 03i：CPU 全生命周期改动位置与删除索引

版本边界（2026-10-12）：本页算法/接口与LP或早期成本数字属于各自冻结批次。当前ed0f229821已完成CPU私有结果与captured保护统一；旧prepare/publishPrivateWrite、AdoptPreparedWrite、ReplacePrivatePreparedBacking不再是当前实施目标。后续只沿[新版流程及清理账单](../evidence/br1_pipeline_refactor_20261010/unified-rw-r1/RESULT.md)与[原33×6矩阵](../evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#unified-rw-implementation)推进；不重开本页已结算矩阵。

算法唯一入口为[03h](03h_cpu_lifecycle_ideal_blueprint.md)，实施状态唯一入口为[03j](03j_cpu_lifecycle_tracking_matrix.md)。§1保留704起点定位；当前实施位置见§6，完整差集绑定[实施审计](../evidence/br1_cpu_lifecycle_implementation_20261009/implementation-audit.json)。原索引固定产品 `704d96e81cf29d16191bc3db8785859d79775e27`；所有行号只对应该源码，实施时以符号和caller重定位。[核验包](../evidence/br1_cpu_lifecycle_blueprint_20261009/README.md)保存源位置/hash及检索结果。28个子项须与03j双向一致；以下规格已按实施证据调整，资格/数量/净收益以03j为准。

<a id="source-map"></a>
## 1. 按原责任反查代码

| 原owner / 文件 | 真实入口与消费者 | 本包ID及处理性质 |
|---|---|---|
| [StateMachine](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine.cpp:273)、[原working类型](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine_p.h:13) | reference apply、metadata applyKnownValid | LP01/02/03：共享有限语义策略；原通用转换保留 |
| [Metadata投影](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:1104)、[整记录安装](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:1482)、[局部sequence](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:3703) | WriteCoordinator、通用owner transitions | LP01/02/08.4：适用链替代；非适用链保留 |
| [Metadata候选Data](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:1954)、[prepare](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2349)、[install](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2731) | canonical commit、restore、detachment、recoverable | LP03/04/05：原Data内部表示和完整释放 |
| [WriteCoordinator](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2668) | native/generic prepare base/private publish、alias Adopt | LP01/02/09：caller和参数迁移；provider失败边界保持 |
| [Store冷页](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2019)、[seal](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2355) | native、legacy、execution、checkpoint/cancel | LP01/02/10：消费原事实，proof/读cut不改 |
| [Publication commit](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:866)、[descriptor准备](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1724) | prepared overlay、canonical、initial/alias/default | LP03/09：最小candidate/不可变值；跨owner验证保留 |
| [OwnerLedger登记](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:968)、[proof](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:2129) | backing登记、sealPreparedPage、validatePreparedPage | LP01/02/08.5：闭包复验，非已证明可删 |
| [executor](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreReclamation.cpp:250)、[job协议](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreReclamation_p.h:65) | 下表七类真实后台责任 | LP06/07：原队列/时钟实现，不改公共job ownership |
| [read last-use](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadCoordinator.cpp:207) | notify/dispatch/process/finished、capture release | LP08.1：条件去重；LP06/07必测消费者 |
| [history](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp:71) | requestKey/collectSlice/collectPass/schedule | LP08.2：保留有界算法；LP06/07迁移验证 |
| [retirement](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp:91)、[budget waiter](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:606) | dispatchReady/inFlight、wakeDispatch/dispatchAgain | LP08.2：保持执行中事件、拒绝与实际free |
| [epoch释放](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:374)、[Store末引用](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3020) | tree drain/finished、terminalCleanup | LP08.3/08.5：原节点有界摘链/最终owner |
| [backend operation](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2064)、[cursor](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2243)、[merger](/Users/apple/krita_gpu/krita/libs/image/kis_async_merger.cpp:172)、[painter](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:687)、[capture](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3038) | 独立/borrowed/packed/clear、current/G0/oldData | LP10：完整入口与第二梯队，不修改像素语义 |

需要声明迁移时一并检查原`KisPageMetadataCoordinator.h`、`KisPageWriteCoordinator_p.h`、`KisPagePublicationCoordinator_p.h`及原测试类声明；不先新建一组公共接口文件。新私有helper须有生产consumer、替代旧实现、列明预算和销毁端；找不到这三者则不引入。

<a id="edit-specs"></a>
## 2. 子项改动与删除规格

<a id="lp01.1"></a>
### LP01.1 — 共享Fresh/Adopt语义策略

位置：StateMachine `AcquireWrite/AcquireRecoverableWrite`、`AdoptPreparedWrite/PrepareWrite`分支及其原私有声明。复用原applyKnownValid政策与编译期薄事实投影，不再新抽三组helper；recoverable额外的retag/independent-before条件继续原分支，不随提取被跳过。值模型调用共享策略后应用变化，metadata从原索引提供同义事实。原guards仍唯一，canonical增加私有delta emitter；不并存两套判断。输出不得拥有旧保护链/新缓存；失败在任何权威修改前返回。反例T1/T2。

<a id="lp01.2"></a>
### LP01.2 — Fresh实际consumer直接安装

位置：Metadata `applyOwner/applyOwnerSequence/applyProjectedSequence`、records/arena安装原语；WriteCoordinator `preparePrivateWrite`、Store `beginWriteImpl`。识别真实允许的完整序列；用原arena/index/capacity接纳target，仅改变base pin/header。适用分支删除完整保护snapshot/inputVersions/旧record重装；保留必要标量WorkingState；不删除通用函数本身，所有其它caller仍可用。空、foreign、非同writer序列在第一修改前拒绝/选原算法；进入直接安装后不得fallback。增长后按revision重算，统计/Storage拒绝保持。反例T1/T2/T3。

<a id="lp01.3"></a>
### LP01.3 — alias Adopt与generic边界

位置：Metadata同入口、StateMachine Adopt、Store `prepareAliasLocked`及WriteCoordinator所有`applyOwnerSequence`caller。Adopt新target直接Prepared，保持source可见性/physical碰撞/generation，不能增加不存在的base pin。单步Prepare/Begin已迁入header直接路径；未initialized、异步、recoverable逐一保持原合法路由。退出条件是所有kind/sequence路由表有去向，不能只优化native主分支而遗漏同义Adopt；无fixture命中时不授删量。反例T1/T3。

<a id="lp02.1"></a>
### LP02.1 — private publish字段改写

位置：StateMachine BeginPublish/PublishWrite、`releaseWriterBeforeImage/canPublishWriteReplica`；Metadata sequence派发/原record定位。共享策略先验证全部base/target/phase事实；普通同步两步一次写最终字段，旧replica/overflow链不重装。真实CancelPending/effects仍走原路径；不得提前pin--再发现target失败。适用路径无完整保护临时镜像，必要标量WorkingVersion仍存在、无无关arena增长。反例T2/T3。

<a id="lp02.2"></a>
### LP02.2 — 已完成事实与首次发布合于原接纳点

位置：WriteCoordinator `publishPrivateWrite`、Metadata原私有发布入口/声明、Store seal caller。把原versionSnapshot重试判断并入同一分片锁的发布操作；删除caller两段metadata访问。新私有入口承担判断和安装完整责任，不是返回另一个bool让caller再重做。相同Prepared三元身份可重试，foreign/过期不接受；proof/writable reset/overlay边界保持。反例T3。

<a id="lp03.1"></a>
### LP03.1 — CommitTransaction直接delta

位置：StateMachine Commit分支、Metadata `preparePublicationImpl`的include/snapshot/旧publication复制/比差分、原`Publication`。沿原published/Prepared transaction索引读必要字段；所有较早Prepared及最新目标仍检查，直接产生实际deltas和authority。删除适用分支旧完整版本投影及复制再压缩循环；不新建第二Prepared目录。install沿原delta/claim，无旧保护链覆盖。反例T4。

<a id="lp03.2"></a>
### LP03.2 — default/restore同一表示

位置：StateMachine ReplaceDefaultPixel/RestoreCommittedVersion、Metadata prepareRestoration/preparePublicationImpl、Publication restore/commit。用同共享策略输出fields及真正default addition；mutable/physical归属/exact default revision/nextGeneration保持。完整候选所有支持的普通publication kind都退出旧镜像，不能只留下Commit快分支。新addition仍走原收费installRecords。反例T4/T5。

<a id="lp03.3"></a>
### LP03.3 — recoverable/detachment与authority保留

位置：Metadata `PreparationKind`、`backingAuthority`、`prepare/ installRecoverableWrite`与detachment调用。recoverable确有base/target物理所有权变更，继续严格revision及两记录替换；detachment已避免镜像，维持原语义delta。backingAuthorities有版本精确消费者，排序/原allocator保活保持。不能从普通路径删除公共字段后破坏这些caller。反例T5；仅记录保留，不计新收益。

<a id="lp04.1"></a>
### LP04.1 — 原entries唯一分组表示

位置：Data::Entry/ShardArenaGrowth/create、prepare输入重复检查、growth find_if。原entries带短寿命inputOrdinal，按stableShardIndex/fullKey排序后相邻去重，原growth记录begin/count。替换any_of全前缀比较、growth线性匹配/全表筛选；新增字节纳入原Data allocationUnits。输入只同步借用，不新增排序副本、常驻hash表或shard owner。detachment无growth仍有合法分组。反例T6。

<a id="lp04.2"></a>
### LP04.2 — 分片准备与动态复验

位置：prepare中的输入读取、batchDemand、growth revalidate及activity预留。按≤16页run共锁，解锁前完成该run事实提取；原growth窗口后复验对应组全部依赖，失效则Conflict/原重试。删除同一稳定组的重复全表过滤和可合并锁，保留每个真正unlock后的动态检查；不能保留arena/raw page指针跨失效窗口。反例T5/T6。

<a id="lp04.3"></a>
### LP04.3 — 全批claim/安装/回滚分组

位置：installPublicationImpl claimed循环、失败前缀清claim、每页安装、growth回收。先所有组claim成功再首个安装，≤16页run、每次仅一把分片锁；原claim在跨run解锁时继续保护未安装部分。释放claim仍在页最终写入的同锁内；不能提早回收后页预留arena。旧按页锁循环被真正替代，失败清理走同分组。反例T5/T6。

<a id="lp04.4"></a>
### LP04.4 — 统计合于已需锁区间

位置：recordEntryPreparationWork析构scope、preparedMutationPages/preparedPublicationPages末循环、安装/拒绝计数。把本地累积统计在下一既有分片锁内结算；无下一锁的失败出口仍须一次结算。删除纯统计成功链的额外N次/两组锁循环；失败和不同事件计数不合并。须计数实际成功/拒绝到达次数，不能声称固定每候选少2N。反例T6，原metrics对账。

<a id="lp05.1"></a>
### LP05.1 — Data payload与activity共同有界清理

位置：Entry::releaseActivity、Data::clearBatch/cancel、DeferredPublicationCleanup::clearBatch。沿LP04相邻run先门外销毁publication，再一把分片锁归还同run activity，门外销毁entries。原data索引/局部数量代替新数组；releaseActivityLocked若新增须吸收原检查/更新政策，逐页旧实现退出适用链。所有maxUnits、空候选和部分entries的同步caller也迁移。反例T7。

<a id="lp05.2"></a>
### LP05.2 — invoke最终统计一次结算

位置：Data::invoke、DeferredPublicationCleanup::dispose、原statistics。保留每单位时间检查和8/16/1024界限，最终pass的pendingUnits/pendingCandidates在一次idleMutex下结算；其它原子计数和maxima保持。删除最终pass额外idle锁；无新增计时、任务分配或worker pool。反例T7/T8。

<a id="lp05.3"></a>
### LP05.3 — 拒绝、cancel、最后free同一终点

位置：Data::~Data/cancel/DataDeleter、install transferCleanup scope、enqueue拒绝invoke及finished。partial prepare、foreign/stale/非空deferred输出拒绝都清完原reservation/activity；原allocator通过Data物理free存活。不能把未入队失败候选遗留给不存在的finished；现有同步fallback一直清到完。拆除无consumer旧cleanup分支，不能另建terminal wrapper。反例T7/T8。

<a id="lp06.1"></a>
### LP06.1 — 回收队列有效唤醒

位置：ReclamationExecutor::enqueue/stopJobs。用原m_firstJob/m_jobRunning在原mutex下决定idle→work通知；删除运行中/已有排队job的无效notify_one。stop和nullptr能力检查保持，所有后台producer见§3。反例T8/T9。

<a id="lp06.2"></a>
### LP06.2 — 任务完成与下一次取队列共锁

位置：runJobs。invoke/dispose/finished保持门外，后面同一lock做end→next/wait；原独立尾锁循环退出。不批量偷队列、不改变FIFO/自重排公平；原finished/context/reusable在invoke前快照，finished可能销毁job，之后禁止再访问job。drain判定必须在实际任务终结后。反例T8/T9。

<a id="lp06.3"></a>
### LP06.3 — worker身份按线程寿命发布

位置：runJobs、kisOnPageStoreReclamationThread及全部检索consumer。启动/退出各一次原atomic store；删除每job两写。所有consumer目前比对当前线程；测试main/外部线程/析构/finished/worker内部enqueue、退出后ID清零。不得换动态TLS或扩大owner存活。反例T8/T9。

<a id="lp07.1"></a>
### LP07.1 — delay等待条件变更通知

位置：Delay::cancel/arm/takeReady、monitor due分支。原gate内对比最早deadline变化，只在变化时notify；未queued取消仍失效generation。移出的queuedPin和dispatch门外free。删除无等待条件变化的通知，不删rearm/cancel逻辑。反例T9。

<a id="lp07.2"></a>
### LP07.2 — ready队列空到非空通知

位置：Wake::notify/placeWake、monitor preferWake。只由原ready队列空→非空通知，保留节点registered/ready/stopping检查及dispatch临时ref。reset与正执行callback交错保持；stop强制唤醒。反例T9。

<a id="lp08.1"></a>
### LP08.1 — read producer重复调度的条件清理

位置：ReadCoordinator notifyLastUse/dispatchLastUses/processLastUses/prepareTask finished、close/retry。LP06/07修改后全量消费验证必做；只有证明jobScheduled且无retry的最终检查覆盖当前ready事件才删producer再次wake。readyQueued本身不构成删除许可，异步完成能解除已安排retry。已按jobScheduled/finished同锁保证迁移，retryScheduled仍cancel；不在provider通知中运行metadata。反例T10。

<a id="lp08.2"></a>
### LP08.2 — history/retirement/budget原接续保持

位置：HistoryCollector schedule/collectSlice、RetirementQueue dispatchReady/finished/schedulePassLocked/retireOrDefer、BackingBudgetController notifyWaitersLocked/wakeDispatch/finished。保持根世代失效、repeat/ready、公平预算、notified/inFlight/dispatchAgain、capacity retry。没有同事实重复调度证据前不改consumer政策；仍须验证LP06/07没有丢醒/自旋。反例T10/T11。

<a id="lp08.3"></a>
### LP08.3 — epoch原释放链有界摘取

位置：KisImageEpochTreeStorage::enqueue/drain/finished。原链mutex下摘最多remaining(128)个节点，断开本地尾；锁外迭代free，child只追加原链，下次取剩余额度。删除每free一个节点一次取头锁；不修改实际free/归费/原taskPin和shutdown同步drain。已实施原链摘取，原128界和child追加不变。反例T11。

<a id="lp08.4"></a>
### LP08.4 — 有effects/取消的剩余镜像审查

位置：Metadata applyProjectedSequence、StateMachine Fail/Cancel/Abort、m_prepare/commit/cancelRetirementDebt。逐kind记录读取、修改、效果和consumer；可用LP01–03共享策略扩展时必须先准备原Debt，再复验再安装，拒绝保留原页。无确定更便宜表示时具体保留，不能删除通用fallback或把所有后台时间授此项。反例T1/T11。

<a id="lp08.5"></a>
### LP08.5 — root/owner最后释放保持

位置：Store PrivateReleaser::cleanup/terminalCleanup、原job Task::dispose/finished、retirement和read生命周期引用。物理task、captures、arena、provider/backing实际free及预算归还先于原root最终释放；晚guard/facadeGone/stop拒绝都有原终点。不拟新增生产代码，作为不可缺少consumer反证。反例T8/T10/T11。

<a id="lp09.1"></a>
### LP09.1 — exact descriptor复用条件项

位置：WriteCoordinator prepareWriteBaseLocked、Publication descriptorLocked/prepareDescriptorAdditionsLocked/prepareDescriptorLocked及initial/default/alias/generic四类producer。传精确base身份，在原owner锁下索引借用共享值，经完整相等判断后跳过布局全扫；无hint/不等保留原正确路径。删除仅命中分支的历史搜索，不删除必需map node、不新layout cache。新增内部参数须替代真正搜索且有caller，测额外shared引用/存储成本。反例T3/T5。

<a id="lp10.1"></a>
### LP10.1 — operation/读选择相邻重复条件项

位置：Backend runCpuMutationOperation/BoundedCursor、Store captureReadViewImpl、Painter bitBltImpl、AsyncMerger startMerge。记录真实current/G0/oldData/changed选择和跨cut失效者；只在原scope证明稳定时借原binding/read selection，不新cache。没有同义差额证据前保留原算法，不重领旧pin试验。反例T12。

<a id="lp10.2"></a>
### LP10.2 — 全入口、删除检索及整包验收

位置：上述所有caller、原Reference/CpuMutation/ResidentRead/PhysicalClaim及tiles3测试。每个产品hunk归属28子项之一；新字段/helper/签名同步列入删除/保留账。末次统一检查所有入口，判定未触发/保留/已迁移，记录数量、安全、净时间及负控制。不得用已有9224次旧安全结果认证新实现。具体路径与验收见03j。

<a id="background-consumers"></a>
## 3. 后台七类责任不允许遗漏

| producer→执行/结束 | 原节点与失效者 | 本包责任 |
|---|---|---|
| Metadata dispose→Data invoke→finished/dispose | 原Data；部分prepare/claim冲突/队列拒绝 | LP03–07、LP05.3 |
| History schedule→collectPass→原finished/retry | 原task/Work；根变化、reader/retained释放、容量 | LP06/07/08.2 |
| Read notify→monitor dispatch→processLastUses→finished | 原ActiveReadRecord/ready/task；terminal、close、cleanupPending | LP06/07/08.1/08.5 |
| Retirement dispatchReady/schedulePass→原task→finished | 原wait/debt/task；provider完成、pin、stop、inFlight通知 | LP06/07/08.2/08.5 |
| Budget notifyWaiters→monitor→dispatchWaiters→finished | 原waitContext/requests/task；capacity、cancel、dispatchAgain | LP06/07/08.2 |
| Epoch enqueue→drain→finished | 原tree storage/taskPin/释放链；child追加、last owner、stop | LP06/08.3/08.5 |
| Store PrivateReleaser→terminalCleanup→destroy | 原owner terminal job；晚guard、facadeGone、worker内最后引用 | LP06/08.5 |

这七类是源码生产责任清单，不表示108过程均触发、均已定价或存在七个可删任务。声明/通用task模板是共用支撑，不另算一种业务责任。执行器优化须覆盖所有消费者，即使本次投影样本某类次数为0。

<a id="deletion-rules"></a>
## 4. 删除验收与范围纪律

检索`records.snapshot/project`、`putAcceptedBatch`只要求从LP01/02/03合格分支退出；其它路径有真实consumer，不能追求全仓库零命中。`versionSnapshot`仅删LP02 caller重复调用；真实read/base消费保持。`notify_one`只删没有等待条件变化的调用；stop通知保留。统计从重复锁迁走不等于删除指标，费用从临时镜像消失才可称实际字节/请求删量。

每项交付必须填：原位置/新位置、调用者差集、删除/保留检索、并发反例、成功和拒绝实际分母、净新增存储/锁/owner。全部28行都有处置才可报告责任审查完成；只有已实现且验证的行才可称优化落地。条件项转保留须写具体consumer与较便宜替代为何未获证明，不能只填“正确性需要”。实现中发现漏点先扩展同一行或新增子项并同步03h/03j，不把未解决项迁出账本。

<a id="transition-coverage"></a>
## 5. 原状态机转换全集与实际路由边界

此表用于防止“只写Fresh却删除共享fallback”或把其它metadata转换遗漏为零成本。核验器对当前StateMachine全部case逐一比对；表是03j子项的责任展开，不新增状态权威。具体最小算法见03h LP01–03及LP08，未命中/保留不授删量。

| 当前转换kind | 本包归属与理想/保留路由 |
|---|---|
| `AcquireWrite`、`AdoptPreparedWrite` | LP01：合格单步/生产序列最小delta，任意sequence保留原原子边界 |
| `PrepareWrite`、`BeginPublish`、`PublishWrite` | LP01/02及LP08.4：同步组合主项；单步/CancelPending/异步有实际phase或effects，逐条件保留/迁移 |
| `AcquireRecoverableWrite` | LP03.3：原prepared recoverable真实retag，两记录和strict revision保持 |
| `CommitTransaction`、`ReplaceDefaultPixel`、`RestoreCommittedVersion` | LP03：原candidate直接构造实际delta/addition；公共值模型同一语义策略 |
| `FailWrite`、`CancelWrite`、`AbortPreparedVersion`、`AbortTransaction`、`ReplacePrivatePreparedBacking` | LP08.4：有effects先原Debt/复验；captured历史/CancelPending特殊字段分支；未获许可保持generic |
| `AcquireRead`、`AttachHistoricalDefault`、`MaterializeDefault` | LP08.4/LP10：真实新增lease/version/replica节点不免收费，条件改写不动未变保护链 |
| `DetachPreparedVersion` | LP03.3/LP08.4：prepared detachment已直接；generic单步可条件delta，任意sequence不拆原子性 |
| `BeginAuthorityHandoff`、`CommitAuthorityHandoff`、`FailAuthorityHandoff` | LP08.4：双端pin/header/authority最小变化候选；外部动作和完成identity必须保持 |
| `RetainCapturedVersion`、`ReleaseCapturedVersion`、`ReleaseRead`、`AcknowledgeLastUse`、`DiscardHistoricalVersions` | LP08.1/08.2/08.4：已有原位保护修改/有界history路径不重领；原值模型/兼容序列仍作正确性控制 |
| `BeginMaterialize`、`CompleteMaterialize`、`FailMaterialize`、`BeginRetire`、`CompleteRetire`、`FailRetire` | LP08.2/08.5：provider/retirement外部完成合同；不在owner localTransition允许集内，不误送新增Fresh/private入口 |

<a id="implemented-index"></a>
## 6. 当前实施位置与完整差集

实际14文件/109 hunk逐块归属见[implementation-audit.json](../evidence/br1_cpu_lifecycle_implementation_20261009/implementation-audit.json)，包含32个当前case与每个源hash；[PLAN](../evidence/br1_cpu_lifecycle_implementation_20261009/PLAN.md)记录新增字段/consumer/失败与free终点及条件项保留证据。下列为实施符号位置，§1行号仅作704起点参照。

| 当前实现 | 子项与删除对象 |
|---|---|
| [共享policy](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStateMachine.cpp:170)、[薄事实project](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:1104)、[直接write](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:3665) | LP01/02/03：唯一guard；删除保护镜像和旧record重装，必要标量保留 |
| [分组prepare](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2386) | LP03/04：原installRecords暂存；原entries排序/邻接去重；原growth范围与统计并锁 |
| [同步清理](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2216)、[后台清理](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2269) | LP05：同分片活动归还、payload门外析构、最终idle结算一次 |
| [worker](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreReclamation.cpp:367)、[read通知](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadCoordinator.cpp:207)、[epoch摘链](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:390) | LP06/07/08.1/08.3：原队列/链，无新调度状态 |
| [精确base descriptor](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1706) | LP09：native/alias/generic/recoverable迁移；原两参数ABI与initial/default保持 |
| [新分组反例](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreReferenceTest.cpp:6983)、[结构规则](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/check-pagestore-architecture.py:1368) | LP04/05/10.2：33页乱序/重复/晚组拒绝/保护链；install范围禁止释放活动保护 |
