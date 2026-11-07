# BR1 API 收敛方案与代码修改映射

当前接口推进至 **b7565f0f6f**：[原33项最低路径实施](../evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-minimum-pipeline-implementation)。原publication新增接收原changes向量的共同prepare，generic输入构造同一向量后汇合；full/range retain/release共同消费16B ref链与原record游标，packed私有capture提供最多16项binding输出，私有同步visitor借原view；公共外逃guard仍保活原scope。原budget新增严格零费用准入而不创建空slot；slot本身仍用原generation与occupied生命周期。两hash只在原claim/manager排斥内提供prepared-update短借，generic模板保持原next合同。没有第二读/恢复协议、新owner或新队列；[真实caller与17个退役符号复查](../evidence/br1_pipeline_refactor_20261010/rw-minimum-pipeline-r1/consumer-census.json)。完整性能/压力资格按92当前入口，以下旧“最新/下一”不覆盖本条。

<a id="cpu-lifecycle-api"></a>
## 最新：最小metadata变化与原回收owner（92 §16.158）

[03h §3](03h_cpu_lifecycle_ideal_blueprint.md#shared-policy)规定下一包的接口形态，[03i](03i_cpu_lifecycle_edit_index.md)列每个caller/旧实现删除边界，[03j](03j_cpu_lifecycle_tracking_matrix.md)唯一维护状态。拟在原StateMachine私有实现内提取Fresh/Adopt、private publish、canonical三类共享策略，由原reference值模型与metadata arena消费；替代同义guards和临时镜像，不建立第二状态机/owner/权限表。原Data内部排序分组、cleanup与executor/monitor原位收束；任何新增私有helper必须吸收真实政策并使旧链退出。产品尚无接口改动，recoverable/effects/真实revision与最终free保持；公共trusted参数、新layout cache和常驻fast-path状态不在蓝图中。

最新检出为[92 §16.155](../92_br1_m6_m8_execution_baseline.md#cpu-management-cleanup-result)管理管线清理候选`704d96e81c`，分支`codex/br1-cpu-management-cleanup`，父6644249，原产品分支保持a918。22项迁移与安全验证完成，默认不晋升；性能/原控制只查92，本篇下方旧交付保留各自身份。正式校准2/20、metadata分母/完整CP0和M6仍未完成。

<a id="cpu-management-cleanup-api"></a>
## 管理管线清理的接口结算（92 §16.155）

[03f](03f_cpu_management_cleanup_index.md)固定API及caller责任，[03g](03g_cpu_management_cleanup_tracker.md)维护唯一状态。MP03删除cursor的冗余targets字段/参数；MP02删除无consumer的排序helper；MP04以原session私有reservation接收/绑定替代独立operation的adopt→generic borrow，fillRect仍只接收范围，history仍真实准入；MP10由原WriteAdmission承担单键owner/token/origin核验。新增内部函数必须有实际consumer且替代旧工作，禁止公共trusted flag、第二权限表或新owner。

实际接口：Store私有adoptReservation增加可选execution输出；原WriteAdmission新增adoptReservationLocked/ownsClaimLocked并删除rebindClaimSetLocked；原Publication新增discardDescriptorAdditionsLocked供四consumer使用；原Execution的link统一两个挂接consumer。backend两个范围consumer、全部legacy caller和旧测试同步迁移。没有public trusted flag、永久状态或另一owner；主干public/protected净增长零。生产+158/−106、测试+66/−28，原generic claimRange/初次claimAll/EntryHandle及实际失败/free保持。每个新增接口的消费者、代替对象和最小形态比较见[PLAN](../evidence/br1_cpu_management_cleanup_20261008/PLAN.md)。

<a id="projection-lifecycle-api"></a>
## 完整投影责任的候选替代与保留（92 §16.151）

| 原入口/消费者 | 最终原责任表达 | 同批删除与寿命 |
|---|---|---|
| WriteCoordinator prepare/publish→MetadataCoordinator、全部Reference caller | `applyOwnerSequence(key, pointer, count)`同步借用，生产两步栈数组 | 删除拥有型SnapshotArray签名及生产临时control/vector；原状态机/拒绝/跨锁复验不变 |
| provider配置→default/copy/payload/alias及CPU transfer | 原state新增一份终态Ready；transfer参数改为该事实 | 删除逐operation Ready allocate/complete；原completionSource在配置Ready拒绝后复用，禁止换registry；每allocation Retire仍独立Pending到实际free |
| native seal、generic overlay输入→PublicationCoordinator | 新内部reader重载及唯一 `prepareOverlayInputLocked`，直接构造候选最终输入 | 删除seal生产者vector/复制/free；同步reader不逃逸，最终owned输入跨锁保活，proof/alias/removal/retry保持 |
| ResidencyObserver prepare/track/ack/untrack | Payload自有记录内嵌slot tree hook，slot查询借原节点 | 删除独立SlotMap节点及PreparedPayload.slot；slot/dirty先解绑再析构，不新增第二owner |
| 所有默认TileData构造 | 原private fillWithPixel用seed+倍增块 | 删除逐像素循环；字节/BPP/布局/copy/独立页不变，原pin安全修复保留 |
| acquireRead→ensureDefaultPageLocked | 外层read栈持原descriptor临时map，注册pin后锁外清理 | 删除内部无条件解锁scope guard；合法竞争物化回收后重新选择，没有常驻pin/cache |

新内部模板只表达同步读取输入，不引入策略owner或额外候选事实；泛型和native共用一个builder。Ready字段与hook有明确消费者和寿命，用已有source状态承接配置重试，不加恢复队列。生产10文件+128/−87、测试2文件+93/−30；没有主干public/protected API净增长、owner、缓存、队列或锁实例增量。原公共commit、防过期proof、epoch delta、oldData cut与adapter不同集合有实际消费者，逐项更直接表达及不采用原因见[九行审查](../evidence/br1_projection_lifecycle_20261008/PLAN.md)。这些保留不证明成本已经最小；最终安全/容量/实际收益与Undo失败见[报告](../evidence/br1_projection_lifecycle_20261008/README.md)。

<a id="bulk-fill-pin-terminal-api"></a>
## 原Tile唯一native pin终结与填充候选（92 §16.149）

| 原责任/caller | 当前唯一表达或候选 | 同批删除/保持合同 |
|---|---|---|
| 原read/write最后native unlock及两个COW失败caller | 原私有函数替代为`unblockSwappingLocked`，四caller在同一barrier内归还物理pin并清原write-intent拥有标记 | 删除writer重复native终结及正常read/write退出后的重锁；原lease终结保持，两个失败caller显式持锁 |
| 默认构造→private fillWithPixel | §16.149时独立候选在同一已分配页seed+倍增，4096→13；a918原分支保持原循环，最新检出候选见上节 | 所有Store/provider/legacy caller不改签名；copy/rows、预算、源寿命/独立页不变，未加共享可写默认页 |
| 原Store/manager QTest | 18字节数据行和一项实际swap寿命反例，测试slot有原qExec消费者 | 无测试专用生产API；父库反例和首次夹具顺序失败均冻结 |
| 投影clear→original visitor→composite | 调整层filter/selection是真实中间读者；B共同owner尚无闭包 | 不新增跨层owner/setter/许可flag；读选择、准备失败、canonical/adapter/extent联合安装继续原合同 |

当前生产两文件+12/−17、测试四文件+97/−0；完整填充候选比父库生产两文件+11/−14。私有helper改名1、旧签名删除1，没有净增函数/状态/上层类型/队列/TLS；fill候选仅多algorithm include。第一版pin修复751bceff23真实stroke回退4.12%仍保留，最终消除重复锁工作后独立结算。全部caller、关闭状态成本、原owner与MI1–MI8见[实施责任账](../evidence/br1_cpu_blueprint_implementation_20261008/IMPLEMENTATION.md)，实际结构和双架安全/控制见[证据](../evidence/br1_cpu_blueprint_implementation_20261008/README.md)。

<a id="cpu-write-experiment-api"></a>
## CPU写入蓝图的候选闭包与回退（92 §16.145）

完整试验代码在`codex/br1-cpu-write-ordered-experiment`/`f9714b4d31`及[冻结源码、caller图和逐文件账本](../evidence/br1_cpu_write_execution_20261007/README.md)。主工作分支`fb57b8b69b`已完整撤回，不留下只改sort/const的半包领取B1–B8；以下是**已试验的迁移映射，不是当前主线新增接口**。

| 原责任/实际caller | 候选表达与同批删除 | 保持合同与当前裁决 |
|---|---|---|
| painter fixed multi-dab→PaintDevice strategy | 一条private ordered geometry/sourceOrdinal桥，替换适用路径的filtered列表及opaque dab-major body | 真实factory OVER32、原kernel矩形/clip次序，未知op原序；上层public/protected净增0 |
| 原KisTransaction/TransactionData→manager | 私有ordered转接与原generic共用target/mapping复验；manager消费结果，上层只取bool | 原owner唯一，无第二事务/恢复域；未把PageStore枚举扩散到transaction |
| manager→原backend operation | 唯一canonical SnapshotArray；原prepareAdapter内收费的稳定片段计划 | 删QSet/values/native重建与二次排序；原extent/wrapper/changed联合安装保持 |
| backend→原execution/cursor | private canonical const绑定；BoundEntry唯一范围校验 | 删非const detach、BoundEntry重排、targets.contains；single guard/poison/预算/free保持 |
| pigment实际factory→painter资格 | 私有动态类型query留在原factory，覆盖已编译scalar/SIMD类型 | 不是同id字符串授权；无对象布局/长期cache/公共composite接口增量 |

候选生产19文件+390/−59、测试4文件+271/−27；无新owner、队列、锁、TLS、长期字段、job/patch/cut或provider政策。原ratchet未提高，manager PageStore类型集合不增，标识次数cc/header25/12→24/11；2214 indexed APIs/29079 edges及原结构规则通过。新增桥虽均有真实consumer，当前整笔收益未确认，不能据此认定复杂度值得保留。原unsupported/selection/wrap/generic callback仍有合法消费者，候选也没有强行删除；回退后全部原路径保持。行为/资源/负控制/原保护和原stress失败的精确范围见实施证据。

**当前完整执行 [92 §17 CP0–CP10](../92_br1_m6_m8_execution_baseline.md#br1-closure-schedule)及本篇 [§21 API行动账本](#closure-api-actions)。** 按文件反查 [CODE_INDEX CP索引](CODE_INDEX.md#closure-code-index)，按包勾选 [清点 §21](CONVERGENCE_CHECKLIST.md#closure-package-checklist)。§2/§12及各交付节保留2026-09-29局部行动和冻结事实，不把旧“下一项”再当当前排期；状态与资格统一查92 §16.28。沿用S/JP/BC/U/C/V责任编号，CP只表示工作包，不新增项目阶段。

核对日期为 2026-09-29，产品 HEAD 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`，含未提交实现。copy bounds 已按 §13 绑定最终源码与回归；完整身份、125 文件清点与增量见[本批证据](../evidence/br1_copy_bounds_convergence_20260929/README.md)。此前[行动映射记录](../evidence/br1_convergence_action_map_20260929/README.md)只属于当时的文档检查点。文档映射不代表全部适用配置的 caller 审计，后续签名变化仍须补 callback/override、测试及配置消费者清单。

<a id="m6-provider-borrow-api"></a>
## M6 原 plan 冷准备与 provider 寿命（92 §16.137）

| 原实现 | 当前唯一责任与消费者 | 同批删除与合同 |
|---|---|---|
| 所有可尝试路径立即构造整组Prepared | 原plan的physical局部值先观察，合格后才构造其余冷Prepared | native pin拒绝的冷构造K→0；所有可失败存储仍在claim前，锁外销毁与异常gate恢复保持 |
| same-provider before重复ledger查询/强引用 | 原native Mutation::Private::provider、generic acquireWrite局部provider已保活，plan借用该参数 | 同provider lookup K→0；foreign仍由原ledger取得strong reference到before pin及冷存储析构，未新建owner/API/字段 |
| 原handoff安全fixture只含同provider | 原productionRecoverableHandoff增加32个foreign before边界 | exact旧读、四终结与两provider最后payload归零保持；资源/结构与性能分别裁决，见[源码证明](../evidence/br1_m6_provider_borrow_20261006/source-review.json) |

<a id="cp3-candidate-storage-api"></a>
## CP3 原 metadata 候选同一收费生命周期（92 §16.125）

| 旧实现 | 最终归属 | 同批删除与验证 |
|---|---|---|
| 原Data三套独立vector的容量/费用/free | 同一原Data的检查对齐尾部有界存储；page、publication和shard容量按真实基数保留 | 三套reserve/growth/free删除，原public prepared能力及共同prepare/install/cancel/clearBatch/invoke消费者一起迁移；detachment无额外publication/growth |
| 原夹具固定两页四分片且复用物理slot | 原生命周期夹具0/1/2/33页与1/4分片，每页独立物理身份 | 六终结、full oracle、容量/late-free原断言保持；初次54注册拒绝独立保留，当前/父修正后282通过 |
| 下一性能审查 | 原provider冷adoption/物理tracking/注册/binding/retire完整责任 | 按实际写栈审logical/physical基数、稳定保活与收费，尚未选表示，不新增owner、许可开关或恢复域 |

[证据](../evidence/br1_cp3_candidate_storage_20261006/README.md)绑定原双架11112/0/0与原三个40对四桶协议。Fresh K1/H4通过，Fresh K16/handoff仍失败；common metadata25%同义驻留分母与CP0 required继续开放，完整M6未授予资格。

<a id="cp3-metadata-batch-api"></a>
## CP3 已接受 metadata batch 替代账本（92 §16.124）

| 旧责任/表示 | 当前唯一实现与消费者 | 删除/保持证明 |
|---|---|---|
| generic putBatch(snapshots,storage) | 原ShardRecordStore::putAcceptedBatch(page,accepted working result)，唯一applyProjectedSequence caller | 接受结果是原状态机的同一事实，不建proof wrapper或绕过开关；canonical/per-version碰撞和真实预留保留 |
| batchPhysicalSlots hash/桶/逐replica节点 | 原canonical输入及各identity引入/转移的状态机guard负责唯一性，原record store负责全canonical碰撞/安装 | 临时索引完整构造/free删除，没有替代数组/排序器/第二owner；原revision/Debt/输入顺序/拒绝/安装保持 |
| 依赖临时分配或恒满时序的两个压力fixture | 真实spare replica slots占满后Debt注入；每次seal前实际恰满原4MiB、拒绝后真实free和reserved0 | 原2MiB/4MiB限额及语义/原子/成功重试断言保持，实际free栈、父控制与全部失败分别保留 |

[完整责任/源码结果](../evidence/br1_cp3_metadata_batch_20261005/README.md)绑定24行为rows及双架原矩阵。Fresh K16/handoff、metadata驻留及CP0门仍开放；[下一原recoverable候选审查](../evidence/br1_cp3_metadata_batch_20261005/next-recoverable-candidate-audit.json)尚未实现，不新增owner、扩大恢复域或放宽collision/limiter。

<a id="cp3-claim-ownership-api"></a>
## CP3 登记源 claim 替代账本（92 §16.123）

| 旧责任/表示 | 当前唯一实现与消费者 | 删除/保持证明 |
|---|---|---|
| 每个registered source的prepared键节点 | 原Private physical cookie/generation与slot.changes；reclassify、watch、class projection、handoff source与退休/commit断言同批迁移 | 源键reserve/insert/erase/extract及桶增长删除；空闲用原free-slot计数，busy O(K)，选中/未选中no-op差异保持 |
| 未登记handoff目标与两个安装尾节点 | 原preparedHandoffTargets仅保护future target；同一个冷slot保留唯一detached target node | register/handoff target guards保持；第二尾节点删除，安装不free，冷复用/析构才free |
| 外部projection helper与三个owner索引参数 | 原Private::buildPhysicalBackingDelta拥有自己的canonical索引及selected predicate | 原物理计费/别名/输入顺序/credit优先和全部limiter不变，无新公开API、owner或队列 |

[完整责任/源码结果](../evidence/br1_cp3_claim_ownership_20261005/README.md)绑定12并存groups/24aliases行为与双架原矩阵。Fresh K16/handoff、metadata驻留及CP0门仍开放；[下一metadata batch审查](../evidence/br1_cp3_claim_ownership_20261005/next-metadata-batch-audit.json)尚未实现，不增加第二snapshot authority或放宽collision/limiter。

<a id="cp3-publication-authority-api"></a>
## CP3 authority 快照替代账本（92 §16.122）

| 删除的表达 | 原位替代 | 保留的边界 |
|---|---|---|
| VersionHash、unordered_map节点/桶、insert-or-assign | Data-owned paid vector真实首批reserve、标准增长、一次既有identity排序和二分查询 | 原唯一页/版本事实，所有authority、recoverable派生与严格revision |
| 每version独立node生命周期 | 原Data数组容量统一实际收费和最终free | 原移动/取消/安装/deferred cleanup owner，不增加常驻字段或公开API |

[最终源码/结果](../evidence/br1_cp3_publication_authority_20261005/README.md)绑定独立64身份测试和原完整矩阵。下一claim消费者清点只记录原source键、physical cookie/slot changes与future target的区别；same-class no-op拒绝语义保留，不直接删除保护或增加claim owner。Fresh K16/handoff、metadata及CP0门仍开放。

<a id="cp3-backing-batch-api"></a>
## CP3 backing 批量准备替代账本（92 §16.121）

| 删除的表达 | 原位替代 | 仍由原责任保持 |
|---|---|---|
| targetClasses hash map | paid numeric index 排序/merge，caller效果次序追加 | 原retirement record、竞争目标与budget affinity |
| projected/availableCredits maps与classified set | 一组paid pointer array逻辑去重、physical分组与栈内投影 | 原物理priority/references/首个credit/checked delta |
| 逐backing线性physical查找 | 原prepared physicals数组排序去重 | 原排他claim、slot/key节点rollback、取消与handoff转交/free |

全部原native/snapshot准备入口共用同一Ledger gate；未新增公共接口或常驻owner。独立flat模型、实际父库分配差分和最终源码绑定见[本批结果](../evidence/br1_cp3_backing_batch_20261005/README.md)。剩余Fresh K16/handoff与metadata/CP0门不由删除数量授予资格。

<a id="cp3-working-policy-api"></a>
## CP3 原工作结果生命周期替代账本（92 §16.120）

| 原实现 | 替换与真实consumer | 保留责任 |
|---|---|---|
| applyPolicy(state by value)与两种transitionResult | 共同政策按引用推进原result；公共oracle及私有applyKnownValid全部迁移，旧helper删除 | 原transition-local语义、public前后验证及拒绝恢复 |
| applyKnownValid(state)返回working result及逐步接回 | coordinator直接创建一个原结果，publication的两个调用点及projection序列原位推进 | paid allocator/实际容量/退出free；拒绝丢弃、effects逐步累计、revision与安装边界 |

<a id="cp3-epoch-batch-api"></a>
## CP3 原工作值与sparse root替代账本（92 §16.119）

| 原实现 | 替换与真实consumer | 保留责任 |
|---|---|---|
| sparse per-page insert/remove/minimum | 原prepareCommit一次消费accepted sorted/disjoint change/removal数组，三个旧helper删除 | immutable共享、AVL任意height delta、原dense threshold、paid node/control与冷释放 |
| versions/replicas/removal witness独立常见小数组 | 原working alias接受inline capacity，全部projection/publication consumer共同迁移 | paid carrier全容量及原spill allocator，保护数组动态硬预算；不授权canonical可见性 |
| allocator隐式破坏性move | 原copy ctor/assignment显式默认，moved-from reuse保持同一收费关联 | 原owner/费用/实际free及controller detach，不另建恢复域 |

<a id="cp3-budget-limits-api"></a>
## CP3 原限额替代账本（92 §16.118）

| 原实现 | 同批消费者 / 替换 | 保留理由与责任 |
|---|---|---|
| domainLimit(limits,class,domain) | fitsLocked和priorWaiterConflictsLocked每类取一次domainLimits值 | Current/History四域限额，其余五类UINT64MAX，全部域检查保持；无cache/新owner |
| aggregateLimit(limits,class) | 两原consumer每调用取一次aggregateLimits七类值 | enum顺序与原限额对应，Count无真实caller；原signed净aggregate/SSD准备及保留slot政策不改 |
| ed0f229821：CPU私有结果、真实lease producer及共同seal/publication | 旧prepare/install/publish/cancelPrivateWrite退出；CPU统一reserve/complete/replacePrivateWrite及cancelPrivateResult，lease明确*LeaseWrite；共同D/不同观察点保留 | CPU不再落入generic writer fallback；17退役符号及所有caller见[清理账单](../evidence/br1_pipeline_refactor_20261010/unified-rw-r1/RESULT.md)，下一在新版优化费用而不恢复旧协议 |

没有新公共API或收费/终结协议；完整控制结果和编排失败见[本包](../evidence/br1_cp3_budget_limits_20261005/README.md)。

<a id="cp3-storage-admission-api"></a>
## CP3 同步存储准入替代账本（92 §16.117）

| 原实现 | 最终原归属 / consumer | 删除及保留理由 |
|---|---|---|
| kisAllocateMutationStorage每次reserve generic delta→取得local/parent transferable slot→通用commit | 同一个入口的stack capacity/准备事实、controller domain/aggregate reserved及shared child；physical allocation与成功/拒绝共用settle | 普通分配的slot/cookie/数组growth/通用commit搬运删除；全部ordinary/retained/pmr caller自动迁移，无新public接口；同预算limiter和先前waiter检查保持 |
| raw free与retained controller后尾 | 原kisFreeMutationStorage、MutationStorageOwner stop/detach/release/deref及parent child register | 继续原物理free先于退费；最后weak/control仍收费到真实free，不新增cleanup owner/队列 |
| payload/class-change、cold arena/slot-array及异步waiter reservation | 原reserve/reserveChange/slot/grant consumer | 仍需可转交cookie、signed class/durable变化或grant，不能跟普通同步分配一起删除；下一全限额/physical delta政策先审真实caller/转换 |

两架H4 K1通过仅结算该scope两桶；Fresh、H4 K16与handoff门仍失败。新代码成本、原测试更强零尾费断言及全部失败见[证据](../evidence/br1_cp3_storage_admission_20261005/README.md)。

<a id="cp3-transition-values-api"></a>
## CP3 原工作值替代账本（92 §16.116）

| 旧实现 | 最终原归属 / consumer | 同批删除及保留理由 |
|---|---|---|
| 普通publication完整before深复制、第二additions数组及重复authority插入 | 原deltas暂存原版本比较字段并原位压缩；原working array转交新增immutable installRecords | 完整副本及冗余容器/插入删除；三种普通转换维持输入顺序，只追加记录，oracle已覆盖；seal与canonical commit独立可见/取消边界保持 |
| applyProjectedSequence完整input→next深复制 | 原paid version identity数组保留removed/retry事实，next消费原working value | 嵌套状态复制删除；guard/revision、grow/debt unlock竞争和部分拒绝取消继续原owner承担 |

准入/实际fees/free共同成本先审查原controller/slots/shared child/MutationStorageOwner全部consumer，再决定整体收敛；不预先新增接口或将budget关闭。固定M5实际控制失败及完整剩余门见[证据](../evidence/br1_cp3_transition_values_20261005/README.md)。

<a id="cp3-cold-preparation-api"></a>
## CP3 共同准备与终结替代账本（92 §16.115）

| 旧实现 | 最终原归属 / consumer | 同批删除及保留理由 |
|---|---|---|
| recoverable before深复制、第二install数组、base/target authority hash副本 | preparePublicationImpl消费原paid work array；backingAuthority读取同一安装记录 | 全部删除；普通publication的before字段比较仍有consumer，下一按共同责任审查 |
| full-demand arena预分配及第二attach/growth循环 | 原growMetadataArenasOutsideLock补未预留缺口，锁内原records.reserve取得全部tokens | fullDemand参数/分支及重复循环删除；竞争复验、预算拒绝和Data取消保持 |
| 冷slot动态node handle vector/reserve | 原收费slot内联固定两handle；claim立即撤销，费用至冷复用/析构 | 动态holder删除，无新node owner/cleanup queue |
| consumePublicationActivity与安装期清除Entry标记 | 原setPublicationClaim只管理瞬时claim；原Entry releaseActivity管理已有reservation终点 | 私有函数/唯一caller替换删除；installed/cancelled/destructor/clearBatch共用终结，无新字段 |

最终28 index/root/restore及31080 handoff区间/架均alloc/free0，父restore free129保留。checker将删除函数名要求迁到实际claim/release责任，禁止恢复旧消费，不提高原尺寸/侵入门。完整资格及性能/固定Fresh/驻留门只由92裁决。

<a id="target"></a>
## 1. 最终 API 责任与本轮出口

CP2 [§16.113](../92_br1_m6_m8_execution_baseline.md#cp2-epoch-preparation-delivery)结算完整代码/安全范围。原native beginWriteImpl将共同plan实际bad_alloc接回原fail/discardUnprepared及cancel/abort，generic保留原catch，execution外层catch仍承担其他冷准备。logical、physical、accounting、metadata、descriptor与cleanup各保留原唯一owner，没有新签名、字段、类型、队列或结果框架；生产+10/-4净+6为拒绝保证成本。真实epoch/晚completion及五有限准备点与原三终结的consumer见[代码](CODE_INDEX.md#cp2-epoch-preparation-code-index)，完整[审查](../evidence/br1_cp2_epoch_completion_20261004/cp2-audit.json)绑定当前结果。下方各交付保留冻结时点；当前下一包为CP3，正式M6与结构门未验收，业务idle/raw兼容删除仍随CP6–CP9消费者迁移。

CP2 [§16.112](../92_br1_m6_m8_execution_baseline.md#cp2-clone-refusal-delivery)没有新增生产签名。三个Tile复制构造共用原init拒绝空TileData；manager沿已有std::bad_alloc构造终点消费canonical clone拒绝，legacy源继续legacy。删除两个空backend fallback、chained重复array/default/manager/count初始化及未安装局部链；原link/count/析构与原recalculateExtent承担完整准备和清理。bridge在native hash复制前接入，不再登记旧memento索引。生产+17/-35、无新生产类型/字段/owner；初轮manager引用超限已用原工厂返回类型消除，既有ratchet未提高。[源码与consumer](CODE_INDEX.md#cp2-clone-refusal-code-index)、[有限差集](../evidence/br1_cp2_clone_refusal_20261004/cp2-audit.json)保持完整CP2开放。

CP2 [§16.111](../92_br1_m6_m8_execution_baseline.md#cp2-tile-selection-delivery)删除 `attachPageStoreTile` 与 bridge `oldData` 参数/分支，声明/唯一override/全部caller同步改为四参数，无旧overload。G0由原capture/ReadPage→TileData转换交接COW存储，不再复制current、另查presence、保留backend或分配读cache。只读权限使用原标记，拒绝由原write lock承担，旧ensure检查删除；current getter沿原job failure context返回空值。生产六文件+44/-31（净+13），测试四文件+160/-31；无新类型/字段/owner/队列/上层API。新增保证、普通lock检查成本及未通过结构门见[证据](../evidence/br1_cp2_tile_selection_20261004/README.md)，不领取整体性能或完整CP2资格。

CP2 [§16.110](../92_br1_m6_m8_execution_baseline.md#cp2-batch-read-delivery)把内部bridge的原writable bool替换为ReadSelection/ReadCache/Write，全部consumer同批迁移，旧overload删除。一个私有原target查询由原session事实派生；cache意图不能准备新页或改选current。原batch lease复用既有readCache字段，读后/写后共用expected移交与原failed/finish/cancel；nested写复用已有guard。上层公共API、字段、include、friend、owner/queue/mutex新增为零；内部枚举/查询及构造参数增加对应真实wrapper consumer，consumer迁走时随legacy路径退出。生产+96/-54（净+42）是权限/拒绝保证成本，不算去重收益；kis_tile.cc bridge标识引用13>旧上限9仍需结构审阅，不提高ratchet。

CP2 的有限 raw 准入交付见 [92 §16.109](../92_br1_m6_m8_execution_baseline.md#cp2-raw-access-delivery)。原私有 `markPageStoreWriteDirty` 改为返回准入结果，三个 raw 入口消费它；`tryWriteData` 保留 ABI，删除其重复 `ensure`。copy/purge 删除散布的手工解锁分支，codec 消费空结果并归还原锁，旧 codec 的 header buffer 归原局部 RAII。公共/受保护签名、字段、include、friend、锁、TLS、owner 和队列新增均为零；生产五文件 +70/-71，测试两文件 +180/-0。新增拒绝保证与等价清理分列，不据净行数领取性能或完整 CP2 资格。

**目标：调用者只声明读写意图，原 owner 管理能力寿命，每种选择和适配政策只有一处实现。** 保留语义不同的入口；相同政策不因 packed/cursor、fresh/captured 的入口差异复制。局部合并和等价旧实现删除随行为修复交付，不再整体推迟到真实 stroke 之后。

| 责任 | 最终唯一归属 | 调用者不再承担什么 | 必须保留的区别 |
|---|---|---|---|
| 选择读取来源 | backend 原 Private 中的受锁选择逻辑 | 各入口自行判断 history、anonymous、committed | current、transaction base、captured、合法 live legacy 的寿命和能力不同 |
| 逻辑版本与物理 pin | Store 原 owner 查询；provider/binding 原身份和 pin | 由“cache 可 pin”推断“版本仍是 current” | 元数据提示不能充当精确读取能力；分配身份不等同版本 |
| 写入后适配交付 | manager 原 operation 局部准备与安装流程 | packed/cursor 分别维护同一套 cache/extent 更新政策 | standalone seal 与 history pending；新增、删除、default 变化 |
| 保活与归还 | 原 batch 或原 execution 的单次交付边界 | 自行组合两种输出、猜测 finish/析构顺序 | 不新增事务、session、write set 或常驻 current 表 |
| 业务 owner | 原 strategy/transaction；painter 同步借用 | 各 overload 重新决定运行模式或拥有事务 | eligibility、source/target、异步 job 保活及未迁移模式 |
| 错误与终结 | 内层显式结果，legacy void 边界接原 job 失败桥 | 内层重复转成 TLS 后再查询、忽略失败继续发布成功 | 可恢复准备拒绝、执行失败、取消和成功发布后清理不同 |

当前API出口是：CP1–CP8每包迁移实际caller并同步删除等价旧责任；CP9汇总剩余ABI/模式/配置保留理由，CP10按实际收益裁决默认策略。读取选择、packed/cursor联合窗口和首条direct已交付，不重做。完整预算、OFF、同依赖主干性能、Fresh及M6–M8仍按92，不以函数总数或净删行数代替这些门。

**冻结交付：** 六处读取选择见 [§10](#read-selection-delivery)，共同安装/旧输出删除见 [§11](#adapter-delivery)，copy见 [§13](#copy-bounds-delivery)，packed/cursor联合窗口见 [§14](#joint-adapter-window-delivery)，direct及联合fixture见§15/§17。完整剩余范围由92 §16.28/§17和本篇§21定位，不重领已关闭重构，也不把剩余JP族拆成无限底层能力库存。

<a id="sequence"></a>
## 2. 执行顺序、依赖与停止点

以下保留2026-09-29局部收敛单元；当前不顺序重领，整体排期改用92 §17及本篇§21。一个工作包可以包含多个必要单元，分别记录结构变化和行为结果，不要求另开版本。

| 先后 | 领取范围 | 本次必须合并/删除 | 完成后停止在哪里 |
|---|---|---|---|
| 已交付，见 [§10](#read-selection-delivery) | [JP5/S04 读取选择](#read-selection) | 将六处已定位的选择分支归到同一受锁政策，删除各入口等价副本；保留各自 capture/pin/旧读控制 | 原 fresh/old/default/关闭/进度行为不变，政策只有一处；不得顺带重做 read capability 框架 |
| 结构子项已交付，联合行为仍开放 | [JP2/JP6 adapter 与 bounds](#adapter-bounds) + [JP2/JP3/JP7 交付协议](#delivery-contract) | 共同安装及旧输出删除见 §11；接下来闭合真实 bounds caller 与 page/adapter 的共同观察窗口 | 整体 reader-window 精确通过，pending/intent/旧读保持；成功与拒绝各有唯一终点 |
| 现在准备，联合窗口闭合后接线 | [BC1–BC7 owner 与 painter](#painter-owner) + [S01 错误边界](#failure-boundary) | 复用既有私有实现，已相同的 owner/结果分支在接线时删除；保留有消费者的兼容薄包装 | 首条有限 direct 模式的真实 jobs、正常显示、finish/cancel/drain 通过 |
| 具体模式迁移完成后 | [条件删除](#conditional-removal) | 按消费者证明收缩 raw bridge/friend、旧包装、普通 restore 的全量调用 | 只删已被替代的具体路径；不把全模式迁移变成当前 JP6 的前置 |

V01/BC10 harness 与 caller 清点现在开展。不要为等所有旧入口可删而延迟真实验证；也不要为等真实验证而保留已经证明等价的重复政策。

<a id="read-selection"></a>
## 3. JP5/S04：收敛读取选择，不合并读取寿命

| 主改位置与实际 caller | JP5 基线问题 | 替代关系（本项已按 §10 实施） | 验收 |
|---|---|---|---|
| [captureIteratorReadScope](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1148)、[captureReadView](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1205)、[resolveCurrentPagePresenceInto](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1262)、[selectCurrentReadTile](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1352)、[acquireTile](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1459)、[pageAllocated](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2527)（由 manager `getOldTile` 查询存在性） | 六处包含同源的 history/anonymous/committed 分支；局部修复容易漏改其他入口 | 在原 backend Private 内集中受锁的选择值计算，六处调用者删除等价分支。若提取一个私有 helper，必须同批删副本；不创建新的持久 selector、公开参数族或隐式取锁层。iterator 的 current/base 与 capture 条件、writable/oldData 拒绝仍由对应入口保留 | 按入口比较 current/base、无 history、健康/失败 anonymous、关闭及 iterator live legacy；原受锁区间和事务 ID 保活不能缩短 |
| [manager getTile/getReadOnlyTileLazy/getOldTile](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:285) → [Tile::refreshPageStoreData](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:143) / [lockForRead](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:349) | fresh current 和 retained TileSP 已分离，不能因压缩接口恢复旧缓存错误 | 保留 `getTile(false)` 到 `getReadOnlyTileLazy` 的单一路由；`selectCurrentReadTile` 作为兼容适配入口暂留，内部复用统一选择。只删已不再消费的重复刷新段，不删除整个 Tile refresh/lock 协议 | 新 getter 读新值；旧 raw/captured、嵌套读、manager 析构后的 detached Tile 保持；失败返回空的 caller 继续安全 |
| [Store::resolveTileReadIdentity](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3301) → 原 publication coordinator | 联合 version/default 查询是新函数，但承担原分开查询无法保证的同锁选择 | 保留私有原子查询，不拆回两个分别加锁的 public getter；统一选择不要求每次 capture/freeze | default A→B→A、关闭、分配拒绝与暖读取成本保持；不额外 materialize canonical default |
| [provider::readCacheMatchesVersion](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:895) → [Tiles3TileReadCache::matchesVersion](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:153) → [binding::matchesReadIdentity](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp:30) | 三层转接需要给出封装理由，不能只因短而算重复 | 当前保留：provider 隔离具体 cache 类型，cache 持 expected 身份，binding 在原 mutex 下比较身份与版本。不得与 `matchesAllocation`/`matchesHandle` 混成含糊的可选参数查询；迁移 raw cache 后再核对零消费者删除 | 命中只作提示，读取仍须 pin；版本变化/身份复用/retire 不能误命中；不新增 public virtual 来取代这三个小函数 |

**锁与成本约束：** 保持 publication → backend mutex → Store 查询的原选择保护；取得 tile barrier 前释放 publication read，冷路径仍沿 tile barrier → publication read。禁止 publication write → tile barrier，也不让无副作用的选择 helper 隐式 capture、分配或等待。新增函数可作为删除重复分支的手段；评价记录要同时列出被删的具体副本。

最新 JP5 新增五个具名成员函数的处置已逐个列在上表：`selectCurrentReadTile`、`resolveTileReadIdentity`、`readCacheMatchesVersion`、`matchesVersion`、`matchesReadIdentity`。它们不全是公共 API；本方案也不预先断言五个都能删除。

<a id="adapter-bounds"></a>
## 4. JP2/JP6：共用适配交付，并关闭 bounds 窗口

| 主改位置与 caller | 当前问题 | 必须修改/删除的对象 | 不可丢失的语义 |
|---|---|---|---|
| [PreparedTileUpdates::prepare/install](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:57)、[manager::writeBytes](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1555)、[writePageStoreOperation](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1734) | 原两条写入口的重复循环已按 §11 合并；联合 bounds 窗口尚在 | 已沿原 operation 局部对象共用安装政策并删除两个调用点重复循环体；保持实际入口和像素执行差异。下一步只联动联合可见性，准备仍只覆盖缺失 wrapper | history pending 用成功 touched 集；standalone 使用对应发布结果；不能误用最新全局查询来代替本次交付身份 |
| [manager::extent/region](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1519)、[KisTiledExtentManager](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTiledExtentManager.h)；联动 [clear](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:809)、[purge](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:726)、[checkpointStrokeMutation](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1711) | 已发布页可见而 manager bounds 仍旧；简单 union 只能掩盖新增，不能处理删除 | 先按下表确定 caller 需要的 bounds，再将相应查询接到同一选择/交付。保留 manager 公共接口的兼容语义；精确读取使用已有 captured surface 能力。不得只给接口换名或再造一份 bounds 注册表 | 新增、删除、清空、default 更新、checkpoint/cancel/restore；旧 view 固定；working bounds 中纯写意图和 pending 不能丢 |

### 必须迁移或明确保留的 bounds caller

以下列出审查落点和目标，不声称 caller 分类已经由运行证明。实施者先记录实际调用时点与读意图，再决定是否改调用；所有“保留”也须写理由。

| 代码入口 | 审查/修改内容 | 交付要求 |
|---|---|---|
| [PaintDeviceStrategy::extent/region](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:99)、[PaintDevice::extent/exactBounds](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1263) | working extent 与内容精确 bounds/cache 分开；不能把 public `exactBounds()` 等同于 PageStore 的 fixed surface metadata | 更新/失效与读取对应选择一致，旧模式和 wrapped strategy 的边界不变 |
| [frameBounds](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:351) | 确认 frame 的 data manager 与返回边界是否和后续读取绑定；需要固定结果时复用原 captured surface | 不以当前 frame/global current 代替指定 frame；default bounds 处理保留 |
| [estimateDataSize](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:438) | 估算用途与像素 exact 读取分开记录，不能把它升级为第二份资源账本 | 估算无需新建每次 capture，但其范围口径明确 |
| [LoD/copy bounds 消费者](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:850)、[clone 范围裁剪](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1136) | 源范围和源像素使用同一选择，避免旧 extent 裁掉新内容 | 对 source/target、offset、LoD 分别核对；没有覆盖的复杂模式不默认迁移 |
| [purgeDefaultPixels](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1513) | 这是修改扫描，不是纯元数据查询；复用原 writer/manager 协议 | 不能用局部 viewport 或无删除能力的 union bounds 漏掉应清理的页 |

**该单元的硬出口：** 原整体 reader-window 探针以共同选择/固定窗口通过；新增、删除和默认值路径均有断言；pending/intent 对照保持。只有 raw 子范围通过、只把 canonical extent 返回给所有 caller，或把所有差异改称兼容行为，均不能验收。若联合安装需要重排，先给出原 admission → prepare → install → release 的锁序及拒绝路径，再改实现；不得以持大锁包住 pixel kernel 消除窗口。

<a id="delivery-contract"></a>
## 5. JP2/JP3/JP7：收束交付参数与终点

主改 [backend 声明](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h:155)、[runCpuMutationOperation](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1897)、[writeOperation](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2034)、[writeBytes](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2106)；生产交付 caller 是上一节两条 manager 写入口。无交付 caller、测试和其他 backend 消费者也须在修改签名前清点。

**已实现的接口目标：** caller 不再同时提供可独立组合的 `completedBatch*` 和 `completedExecution*`。最初的互斥 `OperationDelivery` 已完成过渡，§14 又移除 history execution 分支与 `finish()`；现在它只移动 standalone 已完成 batch 以延长原 admission。history execution 留在 backend 原 worker，`AdapterCompletion` 在其仍存活时安装 pending adapter。不另开 session、不复制 changed 集，也不新增全局状态。

| 原调用情形 | 交付必须表达的状态/责任 | 退出条件 |
|---|---|---|
| standalone 成功 | 原 batch 已 seal，原 admission 保活至 adapter 安装及局部准备对象清理完毕 | 释放顺序明确，cleanup 不把已经发布成功改报未发布；保留 JP3 成功后解锁成果 |
| history 非空成功 | 原 execution 借用在 backend worker 内继续保护 pending 与重叠写；completion 不取得所有权 | adapter 安装成功后由 worker 调原 `execution.finish`；completion 失败沿原 mutation failure/cancel 责任，不输出可遗弃的 execution |
| 空目标成功 | 无可写能力、无 adapter 工作 | 结果允许“成功且无交付”；不能因没有 execution 而误报失败 |
| 首字节前准备拒绝 | 无部分交付，归还 untouched borrow | 既有 pending 不被毒化；可恢复拒绝与真正执行失败分开 |
| 中途失败/取消/遗弃 | 原 owner 的既有失败与取消责任 | 不 replay、不发布成功 undo；不能等待自己尚持有的 borrow |
| Unavailable/Borrowed | 首字节前决定旧实现是否可用 | 保留实际 fallback 消费者，不能在已经写入后重跑 |

`prepareAdapter` 是在原 admission 内、像素前准备的实际边界；`AdapterCompletion` 只在 changed delta 固定后包围原 publish 与 prepared install。两个 callback 都不能保留 writable pointer，pixel kernel 不在 manager/publication gate 内。旧内部 out-param、history delivery 状态和重复转换均已删除；`OperationDelivery` 暂留的唯一消费者是 standalone admission 延寿。

<a id="painter-owner"></a>
## 6. BC1–BC7/S03：业务接线同时压缩 owner 分支

| 主改符号与 caller | 改法与要移除的重复内容 | 保留与验收 |
|---|---|---|
| [KisPainter::bitBltImpl](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:682)、[scalar bltFixed](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:998)、[multi-dab bltFixed](/Users/apple/krita_gpu/krita/libs/image/kis_painter_blt_multi_fixed.cpp:164)、[painter 声明](/Users/apple/krita_gpu/krita/libs/image/kis_painter.h:182) | 已有 overload 已有部分委托，不重复重构它们。逐个核对后，将同一操作的模式选择/owner 借用收进已有私有实现；旧无 owner API 只作兼容薄包装，不继续为每个入口复制运行模式分支 | 不把 source/target、oldData、selection、mirror 强并为同一算法；实际同步 caller 与未迁移模式继续运行 |
| [PaintDeviceStrategy::applyPixelOperationImpl](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:280)、[Transaction::applyStrokePixelOperation](/Users/apple/krita_gpu/krita/libs/image/kis_transaction.h:73) | 沿现有事务校验/借用收口 owner，保持 WriteContext 为映射值；删除迁移后重复的 owner→result 转换段 | painter 不拥有事务，不把可写权限藏进长期缓存或 TLS |
| [brush addDabJobs 调用点](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:184)、[Freehand init/finish/jobs](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/freehand_stroke.cpp:130)、[PainterBased init/finish/cancel](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:251) | 用原 strategy/transaction 的真实寿命接替首条合格 direct 模式的空 owner；选择在首字节前完成。跨 worker job 由原 owner 保活，不能仅把 `nullptr` 换成裸指针 | BC5/BC6 读意图、producer/cut、正常显示和 BC7 finish/cancel/drain 一起验收；原不合格模式保持旧路径 |

本单元与 [BC1–BC10](01j_real_stroke_integration.md#stroke-integration-map)共用首条 RGBA8/OVER/普通 autobrush 的有限入口，不借“API 统一”扩大模式。内部等价分支现在即可删；公共签名的删除等真实消费者和适用 ABI/插件边界核对完成后执行。

<a id="failure-boundary"></a>
## 7. S01：把结果转换留在实际兼容边界

主改/联动 [KisStrokeJobFailureContext](/Users/apple/krita_gpu/krita/libs/image/KisStrokeJobFailureContext.h:8)、[SimpleStrokeJobStrategy::run](/Users/apple/krita_gpu/krita/libs/image/kis_simple_stroke_strategy.cpp:25)、[tryEndTransaction/tryAbortTransaction](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp:225)、[nullable Tile wrapper](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_wrapper.h:41)、[base iterator](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_base_iterator.h:53)。

可返回结果的本次内层改动直接传递原结果；legacy void/painter/job 边界保留短栈失败桥。删除迁移后不再需要的“写 TLS → 立即读 TLS → 转 result”重复段，前提是逐 caller 确实发现这类段，不能假定所有 TLS 调用都冗余。报告点与消费点写入清点；第二页失败、准备拒绝、空 getter、晚 guard、重复 cancel 都须到达原唯一终点。**不删除整个失败桥，也不为本次 API 整理新增一种跨 job 错误 owner。**

<a id="conditional-removal"></a>
## 8. 删除账本：确定删除与条件删除分开

| 对象 | 本方案要求的处置 | 删除的时间与证据 |
|---|---|---|
| 六个读取入口中等价的 selector 分支副本 | **本批已删除副本**，集中政策，入口本身按语义保留 | §3 同批，原六处调用覆盖与锁序不变 |
| packed/cursor 两处 adapter 共同循环体 | **§11 已合并并删除重复 body**，联合 bounds 验收继续 | §4 同批；不同 pending/standalone 分类在外层显式保留 |
| 独立 `completedBatch/completedExecution` 内部输出组合与旧签名 | **§11 已迁移并删除旧签名**，无交付 caller 保持默认空输出 | §5 同批；只有明确外部消费者可保留薄包装，不保留第二实现 |
| `stageDerivedExtent` | **JP4 已删除**，禁止重新引入后补发布 | 既有证据见 [清点 §9](CONVERGENCE_CHECKLIST.md#jp4-delivery) |
| 新增 `selectCurrentReadTile` 与两处 backend friend | **暂留适配债务**，不新增同类 friend | raw 消费者迁到原 read capability、cache 操作不再跨此边界后，删除 helper/两处 friend 并降低侵入上限；不是本次先验可删项 |
| cache/version 三层查询与 Store 联合查询 | **保留独立责任**；重复转接如有等价替代再删 | 不得把物理 pin、逻辑版本、allocation 身份合成布尔“ready” |
| owner/无 owner painter 包装、legacy/Unavailable/Borrowed | **有消费者暂留**；内部重复 body 在各次接线中删 | 具体模式完成迁移且静态/运行时/插件边界消费者证明后，才删除对应外部包装 |
| [restoreHistory](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:465) 中 `rebuildPageStoreIndex` 调用 | **U01/U02 后续条件删除** | changed delta 贯穿且固定 K 证据成立；其他构造/恢复 caller 的 helper 不随之删除 |

不要求“新增一个函数必须删除一个函数”。要求每项新增说明独立责任和调用者，并在存在替代关系时同批迁移、删除旧实现；不能只写“未来清理”。暂留项必须有上述具体触发条件，不能因暂留而判为收敛完成。

<a id="verification"></a>
## 9. 验证、交付清点与防止再次发散

| 修改范围 | 复用的验证落点 | 必须新增/保持的断言 |
|---|---|---|
| 读取选择 | [FreshReadSelection/WarmPath/OutlivesManager/DefaultRevision/Failure/DefaultPressure](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:4311)、原 iterator/cache/history 测试 | 相同读意图与观察窗口下六个入口遵循同一选择政策，old/base/captured 语义保留；暖命中不无条件 capture/分配，失败不返回旧值 |
| adapter/bounds/交付 | [AdapterPreparationRefusal/AfterAbort/Barrier/Delivery/Lifetime/LegacyConflict](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:2370)、[OverlayExtent](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:981)、[当前整体窗口证据](../evidence/br1_s05_fresh_read_20260928/README.md) | 原整体窗口由非零退出变为精确通过；补删除/default/working bounds；空目标、准备拒绝、失败/成功终结顺序及持续 reader 写进度 |
| owner/错误/真实业务 | [painter 测试](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp)、[事务测试](/Users/apple/krita_gpu/krita/libs/image/tests/kis_transaction_test.cpp)、[FreehandStrokeTest::testAutoBrushStroke](/Users/apple/krita_gpu/krita/libs/ui/tests/freehand_stroke_test.cpp:127)、[完成测试](/Users/apple/krita_gpu/krita/libs/ui/tests/KisPainterStrokeCompletionTest.cpp) | 断言进入持久模式、同一原 owner 跨 jobs、正常显示、成功仅一次 undo、取消恢复与最终 drain；保留旧模式控制 |
| 结构删除 | 实际 caller 搜索、生成调用图、架构/ownership/census/intrusion 检查 | 删除的符号/签名/分支无未迁移生产消费者；callback/override 不能漏查。不能只刷新架构上限换通过 |

生产实现改变后，按受影响范围运行检查和正式所需矩阵，重新冻结源码/二进制身份；原方案的文档校验与 §10/§11 的真实实现证据分开，不复用旧测试数宣称新设计通过。API 统计按公共/私有、具名函数/局部 lambda、包装/政策实现分列；净增行数只作趋势。

每个实施单元填写：

```text
原 JP/BC/S ID；本篇条目：
修改前函数 → 修改后职责与 owner：
实际调用者：生产 / 测试 / callback-override / 适用 ABI 与配置：
新增函数或参数及不可复用的原因：
迁移的调用点；删除的具体签名/重复 body：
保留对象、消费者与退出触发条件：
成功 / 无工作 / 准备拒绝 / 执行失败 / 取消 / 析构：
锁序、分配/pin/capture/回收成本是否改变：
结构检查、行为断言及冻结源码证据：
剩余问题与停止条件；92 当前裁决：
```

没有可证明重复责任或本次契约缺口的重命名、泛化容器、第二套上下文不进入当前批。达到该单元出口后冻结，继续下一实际交付；不能因为全项目仍有条件删除项而不断延长底层整理。

<a id="read-selection-delivery"></a>
## 10. 已交付：六处读取选择合并

主改 [Private::selectReadViewLocked](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:315)。§3 六个入口已经删除各自的等价选择分支，改用这个内部函数；iterator 的 before 捕获条件、各入口的 operational/模式判断、live legacy 和原锁范围继续保留。

新增一个私有实现函数，替代六份重复政策；未增加公共接口、状态或所有权。生产单文件 +24/-38，净减 14 行。不能以 helper 数量增加否定这次去重，也不能以行数减少宣布整体 API 已收敛。编译数据库生成的[调用者证据](../evidence/br1_read_selection_convergence_20260929/selector-callgraph.json)确认六个入口/七个调用点。

七目标双架构行为回归及剩余窗口统一见 [92 §16.10](../92_br1_m6_m8_execution_baseline.md#read-selection-convergence)和[本批记录](../evidence/br1_read_selection_convergence_20260929/README.md)。该冻结点之后的共同安装/单次交付见 §11；实际 bounds 联合窗口与 §6/§7 业务接线仍待完成。


<a id="adapter-delivery"></a>
## 11. 交付协议的实际改动与下一必交付结果

| 文件 / 原符号 | 已实施的替代与删除 | 保留的能力及成本 |
|---|---|---|
| [backend 头](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h:94)：两个独立 out-param | `OperationDelivery` 最初以互斥值保存原 batch 或 execution，旧 `completedBatch/completedExecution` 签名已删除；§14 又删除 history 分支与 `finish()`，现在只保存已完成 standalone batch | 导出头保留一个 move-only admission holder：默认/移动构造、移动赋值、`isEmpty`；不加 owner、session、write set 或每次交付 heap 分配 |
| [runCpuMutationOperation](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1897) → completion | 原分散输出已改为一次移动；§14 将原 publish closure 交给 caller 的短 completion，history 在 completion 内保留 execution borrow、返回后由原 worker归还，不再输出 execution | standalone 已完成 batch 的 admission 仍到局部 prepared 存储销毁后释放；析构不被解释为新成功边界 |
| [PreparedTileUpdates::install](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:89) → 两条 manager 生产 caller | 两份 tile 安装、bridge、cache 失效、extent 通知循环收成一份；删除两条路径的 presence 准备和事后查询 | changed 是本操作实际写入集，不含删除；clear/copy/remove 查询不随之删。缺失 wrapper 在像素前准备，暖页不建记录 |
| [交付生命周期测试](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:2681)及原 adapter/presence 测试 | 覆盖空目标、占用输出、move、异线程 finish 拒绝、遗弃取消、原 claim 等待者；presence 测试要求两条写路径查询为零 | 保留原像素、旧 view、pending、legacy 冲突及 clear/copy 的查询断言；不以删掉原断言换通过 |

本节表格先记录 §16.11 的结构批；其生产增量为三个文件 **+92/-77，净增 15 行**。§14 在其上继续收束 delivery，并完成 packed/cursor 短 gate：相对 copy 冻结点生产 +95/-67、测试 +31/-76，indexed APIs 由 1,815 降为 1,814。两个冻结点分别由[交付协议证据](../evidence/br1_adapter_delivery_convergence_20260929/README.md)与[联合窗口证据](../evidence/br1_joint_adapter_window_20260929/README.md)约束，不能混用早期源码的测试数。

### JP6 后续发布族具体改什么

以下保留 §16.11 冻结点的逐入口静态核对；后续 copy 交付见 [§13](#copy-bounds-delivery)，当前执行顺序以 [§12](#convergence-action-map)为准，尚未声称联合迁移完成：

| 入口 | 当前实际用途 | 下一改动及删除对象 |
|---|---|---|
| `PaintDeviceStrategy::extent/region`、`frameBounds` | 原 manager working bounds，加 device/frame offset；不透明默认值另合入 default bounds；region 经原 cache | 保留这些公开语义；将需要固定内容的显示/读取 caller 接到与像素相同的已有 captured surface。联动原 cache 失效，删除迁移 caller 中独立读取变化中全局边界的组合 |
| `estimateDataSize` | bbox 面积 × pixelSize 的估算，不是精确资源账本 | 保留估算接口并明确口径，不增加 capture 或另一张常驻 bounds 表 |
| LoD 上传、`transferFromData`、frame copy、`makeCloneFrom/Rough` | 先取源 extent 作裁剪，再另一次读取/复制；是联合选择的具体审查点 | 对合格路径让源边界与源像素消费同一选择；迁移后删除独立获取 current extent 的裁剪段。保留 source/target、offset、frame/LoD、默认值差异；未覆盖模式保持原路径 |
| `purgeDefaultPixels` → `purge(dm->extent())` | writer 扫描全 working 范围，可能删除页 | 保留完整扫描语义；随 clear/remove/default/checkpoint/cancel/restore 核验 adapter 更新，不能用只增不减的 union 或 viewport 替代 |

packed/cursor add 已在 §14 以原 admission/prepare/completion/release 协议关闭对应 reader-window；其余发布族仍须确定页与对应 bounds 的共同可见边界、锁序和拒绝终点。已能独立关闭反例的固定选择 caller 可逐项修复并验收，但删除/default/copy/restore/purge 及 pending/intent 控制不能被 add 结果替代。保留原旧读和已完成的 JP3 成功后解锁；不得在 Store owner gate 内回调 manager，不得引入 publication write → tile barrier，也不能将 working bounds 全部替换成 canonical extent。

**停止条件：** 已通过的 packed/cursor 探针不再重开；剩余发布族只在反例或首条 direct 依赖下领取。若 direct RGBA8/OVER 路径不经过未闭合发布族，立即转 BC1–BC7/BC10，不追加无反例的 session/slot/hash 泛化。具体模式完成迁移后按 §8 删除其兼容包装；其余 BR1/M6–M8 门继续保留。

<a id="convergence-action-map"></a>
## 12. 当前可执行的收敛改动清单

**目标状态：每项读写政策只有一份实现，能力寿命仍由原 owner 管理；固定读取的 bounds 与像素消费同一次选择；第一条真实 direct stroke 能显示、完成、取消并释放资源。** API 数量可以因表达独立责任增加，但等价政策和已被替代的签名必须减少。公共兼容入口不以净删行数为理由强行合并。

下面按执行顺序列出有限工作。序号只是表格顺序，不是新增阶段。每一行的出口成立就结束该项；下一行只有表中列出的直接依赖，不能继续追加没有反例的底层优化。

| 顺序 / 原 ID / 当前状态 | 具体修改位置 | 改动与必须同时删除的内容 | 验收及进入下一项的条件 |
|---|---|---|---|
| 1 · JP6 copy · **本项已验收，见 §13** | [copyPageStore / 两条 bitBlt 实现](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1122)、[backend::copyFrom](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2222)、[makeCloneFrom/Rough](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1130) | source/target 各固定一次选择，bounds、准备与像素共用；两条 native 分支已收进一个私有实现；旧内部 `oldSource` 签名和非 wrapped clone 的独立 extent 预裁剪已删。不重新领取 copy 重构 | §13 的固定源、目标清除、不同 default、history-before、legacy backend 关闭对照及失败回归通过；完整 OFF 构建资格仍开放。只关闭 copy 子项 |
| 2 · JP6 / JP2 / JP7 · **packed/cursor add 已验收；其余发布族待依赖审计** | [PreparedTileUpdates::install](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:89)、[extent/region](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1525)、[writeBytes/writePageStoreOperation](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1557)、[runCpuMutationOperation](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1897)；剩余联动 clear/purge/restore/default/copy | 两条实际 add 入口现用原 manager gate 包围原 publish 与 prepared install，旧 history delivery/finish 已删；详见 §14。下一步只审查未覆盖发布族，修复首条 direct 实际依赖并删除相应事后修补；保留有独立语义的 working/pending 适配 | packed/cursor 的 44 场景/172 观察精确通过，旧读、pending/intent、legacy 冲突和进度控制保留。delete/default/copy/restore/purge 不由此自动完成；无 direct 依赖或新反例就转真实链 |
| 3 · JP6 caller · **已定位，待逐路径迁移** | [uploadLodDataStruct](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:839)、[transferFromData](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:853)、[uploadFrameData](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:890)；[frameBounds](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:351)、[strategy extent/region](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:99) | 对需要固定内容的 copy caller，将范围与读取接到已有 read view；删相应“先取变化中 extent、再另取像素”的组合。公开 working/frame bounds、估算、purge 各保留原用途，不能一律改成 canonical getter | 每个 caller 记录迁移或保留原因以及测试；offset/frame/LoD/default/wrap 单列。不在首条 direct 路径内的模式可留原实现并登记到 BC8，不得宣称全模式完成 |
| 4 · BC1–BC7 / S01–S04 · **首条显式开发入口与 BC10 联合正确性已交付** | [addDabJobs](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:169)、[multi-dab bltFixed](/Users/apple/krita_gpu/krita/libs/image/kis_painter_blt_multi_fixed.cpp:175)、[issueSetDirtySignals](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/freehand_stroke.cpp:282)、[init/finish/cancel](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:273) | 原 strategy/transaction 已在有限资格内签发非拥有 painter 绑定，真实 async/1px 写入口消费它；dirty 前 checkpoint，终结先解绑 painter 再释放 owner。正式工具不调用 protected opt-in setter，`FreehandStrokeStrategy::Flags` 保持主干接口 | direct Buildup fixture 已证明实际 brush owner/checkpoint/像素、显示/finish/cancel、多 update 的一个 undo 单元、递归 drain 和四类失败唯一终点；BC9 首个资源子范围也未要求扩大这里。完整 BC10/默认启用仍按后续门 |
| 5 · BC9 / V01 / S05 / S08–S10 · **共享总额、注册/state/context/wake 本体收费和 wake 隐式分配收敛已交付；继续管线内资源收敛** | [资源与回收指南](04_reclamation_and_budgets.md)、[waiter 实施表](04b_budget_waiter_implementation_map.md)、[业务联合表 BC9/BC10](01j_real_stroke_integration.md#stroke-integration-map)、[continuation 所有权 §19](#stroke-continuation-ownership-audit) | 24 MiB/pool=0 长 stroke 已在共享父层下通过；metadata/cache、child registry、每请求 waiter state、每 controller 冷 context 与 prepared wake state 本体受父额约束。wake 队列和 monitor 引用都内嵌在 state，删除每 wake list node 与 shared control block；既有 prepare 函数只扩展 private budget 参数，没有新增产品函数族。waiter handle 是 intrusive inert context+sequence；context/wake 控制块、wake list node 和独立 free-list 已删除。固定请求数组收费且退出释放；slot 数组经原内嵌 reservation 和父 token 收费，冷增长分配与 free 在 gate 外、原需求重新复验；析构先退数组/state/wake/slot，再注销 child。产品方法集合不变；父 controller 自身存活时 slot cache 仍收费。现有 scheduler 尚无安全 continuation owner；下一完整存储段处理 callback/task/retry/pass/terminal 和墓碑实际内存后，再把跨 store 公平与原请求所有权同批设计，继续返回 `Failed` | 自动恢复须等原未执行工作单元能一次性转交，并与 typed result、旧失败分支合并同批实现；禁止按注册 backend 数静态分额、UI 重放 dab 或保存 budget 身份。OFF/Fresh/主干比较仍按 92、39 |
| 6 · BC8 / U01–U02 / S06 · **达到具体迁移条件后删除** | [§8 条件删除账本](#conditional-removal)、[restoreHistory](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:465)、[raw cache 迁移表](03b_legacy_cache_migration.md) | 逐对象删零消费者的外部包装、raw friend/helper、普通 restore 全量调用；迁移前保留实际消费者。已证明等价的内部重复体不能借“后续条件删除”拖延 | 静态 + callback/override + 实际模式证明；适用配置/ABI 验证；删除后降低相应侵入上限。M6→M7→M8 和 stroke→undo→context 顺序不变 |

已交付且不再领取：六处 selector 副本、packed/cursor 两份安装 body、`completedBatch/completedExecution` 旧签名和 JP4 `stageDerivedExtent`。若新反例确实触及这些位置，先登记失败契约，再有范围地修改。

<a id="copy-bounds-pending"></a>
### 12.1 第一项实施前的代码清点与验收缺口

本节保留 §16.12 规划时点的候选记录；下列验收缺口现已按 [§13](#copy-bounds-delivery)处理，不能作为当前任务重复领取。

| 文件与符号 | 工作树中已经发生的变化 | 本次结论与尚需完成 |
|---|---|---|
| [manager 私有声明](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.h:376) / `copyPageStore` | 新增一个私有 helper；precise/rough 两个 native 分支改为委托；公开四个 bitBlt 入口保留 | 新函数有明确去重对象，但尚不能记已交付。声明增加一处 PageStore 类型引用；实施验收前必须审查侵入、owner、锁序及移除条件，不能直接放宽 ratchet |
| [backend 头 copyFrom](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h:218) / 定义 | 旧 `(source, rect, oldSource, rough, …)` 改为 `(source, sourceView, targetView, rect, rough, …)`；内部不再捕获第二组视图，直接测试 caller 同步迁移 | 两个 view 各绑定所属 store/surface，分别固定 source/target；不承诺跨 store 原子快照。检查能力保活延长到 manager 返回的释放、关闭和拒绝行为 |
| `makeCloneFrom/Rough` | 非 wrapped 请求交给复制层按固定视图裁剪；wrapped 保留原 extent 裁剪 | clone 反例日志中 32 个场景已通过，但后续测试中断，且测试源码随后又改动；这些记录不能为当时工作树提供最终通过资格 |
| [CopyBoundsSelection](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:4158)、[ClonePublishedBounds](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:4248) | 已加入 current/history-before、相同/不同 default、空源清目标、source 在准备后改变、offset、precise/rough 和发布窗口 case | 测试中栈上 manager 被隐式转为智能指针造成非法释放，调用已改为显式基类入口，仍须重新构建、运行；保留失败记录，不删断言换通过 |

与 copy 开始前保存的源码相比，当时候选的生产五文件 **+96/-64（净增 32）**，测试两文件 **+147/-1**；仅是改动清点，不是正确性或质量评分。该次文档任务未改产品、未运行新的产品测试；[核对记录](../evidence/br1_convergence_action_map_20260929/README.md)保存本次读取的源码身份。

这一项验收必须包含：固定视图前后变化仍读取原值；目标独有页被空源清除；default 不同不漏掉请求范围；history-before 不被 current bounds 裁剪；large requested rect 的工作量按实际固定范围约束；live legacy、wrapped、非 PageStore 路径的兼容结果明确。复用已有 copy/presence/failure/clone 测试，补当前断言缺口，完成受影响配置回归后再冻结源码、库和调用图。无新产品变化时不因文档改动重跑全项目测试。

<a id="joint-window-design"></a>
### 12.2 联合窗口必须先完成的设计决策

copy 的固定选择本身不解决 manager working extent 的联合发布。§14 已把下表决策落实到 packed/cursor add，并通过原整体探针；表中规则继续约束尚未覆盖的 delete/default/copy/restore/purge，不能把 add completion 无条件套到不同语义，也不能先增加一组新 API 再寻找消费者。

| 决策 | 确定的目标与禁止替代 | 需要提交的具体设计结果 |
|---|---|---|
| bounds 含义 | fixed content 使用原 `KisCapturedReadView` 的 surface state；working extent 保留纯写意图、pending、offset/default 语义 | 每个调用点标出使用何种选择、谁保活、何时失效；不能给所有调用者返回 canonical，也不能用只增不减的 union 掩盖删除 |
| 准备与安装 | packed/cursor 已沿原 operation/admission 预备资源，并由原 manager gate 执行 publish→adapter；其他发布族复用原则而不强套只增页实现 | 每条剩余路径写清 admission→prepare→seal/publish→adapter→release 的实际锁与时点；逐条证明 commit 拒绝时不会留下已生效的 hash/extent |
| 失败与取消 | 首字节前准备拒绝、执行失败、已成功发布后的清理必须分别处理 | clear/remove/default/checkpoint/restore 各列旧状态保留或原取消终点；禁止事后失败后 replay 像素，禁止将已发布成功改报未发布 |
| 并发与寿命 | 保留 JP3 解锁后的 reader 进度、旧 raw/captured 读、同页原 admission 排斥 | 不在 Store owner gate 内回调 manager；不引入 publication write→tile barrier；不得持 publication 大锁覆盖 kernel 或等待旧 reader 退出 |

packed/cursor 的实现满足新增页与拒绝回退后已冻结，不再扩大其接口。剩余路径只有在能同时满足自己的删除/default/restore 语义和拒绝回退时才允许扩展原 completion；若原协议确需扩展，在 §9 模板中记录新增责任与被替代的旧段。现有 add 探针保持绿色，同时为实际领取的发布族增加对应观察，不能用重新命名窗口结案。

<a id="api-removal-accounting"></a>
### 12.3 API 增删账本与停止规则

每次实现回填同一行：**旧符号/重复段 → 唯一目标职责 → 所有 caller → 新增符号 → 同批删除 → 保留原因与退出条件 → 精确测试 → 冻结身份**。公共 API、私有 helper、局部 lambda、薄包装、政策实现分别统计，调用图的 indexed API 数不能直接当公共 API 数。

结构收敛满足三条才记完成：同一政策只有一份实现；所有受影响 caller 已迁移且旧等价 body/签名已删除；保留分支存在可指认的语义或消费者。只增 helper、只移动代码、只更新侵入上限、只累计测试数都不满足。不存在真实替代关系时允许保留独立函数，不能为函数总数强并 current/base、pin/version 或 successful/abandoned 语义。

对“仍不断增加函数”的验收回答必须具体到上面的替代账本。第一项结束后只有新的失败证据才可继续改 copy；联合窗口结束后转真实 stroke；真实链结束后转资源/性能和条件删除。所有扩大范围的工作须说明阻断哪条既定出口，不能因为发现一个可优化 helper 就再开一轮底层版本。


<a id="copy-bounds-delivery"></a>
## 13. 已交付：copy 的范围与像素共用固定选择

| 处置 | 实际代码变化 | 验收与保留责任 |
|---|---|---|
| 合并 | manager 私有 `copyPageStore` 接替 precise/rough 两条 native 选择、准备、复制分支 | 四个公开 bitBlt 入口及有消费者的 legacy 算法保留；不增加 owner、session、常驻字段或锁 |
| 替代并删除 | backend `copyFrom` 改为消费 caller 的 sourceView/targetView；旧 oldSource 签名及内部重捕获删除 | 当前生成图只有一个生产 caller，来自共同 helper；直接测试同步迁移。两个 store 分别固定选择，不是跨 store 原子快照 |
| 修复 | 非 wrapped `makeCloneFrom/Rough` 删除独立 working extent 预裁剪；相同 default 使用 source/target 固定内容范围的并集，不同 default 保留请求范围 | 新发布页不被旧 manager extent 丢掉；空源清除目标独有内容；wrapped、LoD/transfer/frame copy 的其余迁移继续按 §12 第 3 项 |
| 验证 | 每架构新增 32 个真实 clone 窗口场景、32 个 native 固定 bounds 场景和 32 个两端 backend 关闭的 legacy 对照 | 保留原失败/oldData/live legacy/copy/presence 断言；native 在准备后改变源，仍复制原选择。1/4/6 页为具体 fixture 工作量，不是所有稀疏布局的性能上界 |
| 测试所有权修正 | `syncLodCache` 用局部 unique_ptr 释放原 `LodDataStruct` | 原 helper 在 HEAD 也漏释放；隔离前只有 LoD 用例报泄漏，修正后最终双架构无该警告；没有修改生产回收策略以隐藏警告 |
| 侵入及规模 | manager 私有声明增加既有结果枚举的一处引用，头部 11→12；include、布局、friend 不变。生产五文件 +96/-64，净增 32；测试三文件 +167/-6 | 审查与移除触发条件见 92 §16.13；仅调整这一已审上限，其他上限不变。新增函数与旧 body 的替代关系明确，不称接口总数下降 |

最终同源矩阵为 20 个完整目标加 14 个选定 PaintDevice 方法，每架构执行一次，共 **9,560 passed / 0 failed / 0 skipped**；架构、工具自测与实际 Ninja no-op 通过。PaintDevice 未运行其压力/benchmark 全集，不把选择性方法说成完整目标通过。完整命令、二进制/源码身份、失败诊断与剩余窗口见[本批记录](../evidence/br1_copy_bounds_convergence_20260929/README.md)。

**停止与下一项：** copy 子项已关闭。下一步按 §12.2 明确原联合安装的锁序和拒绝回退，关闭 manager page/bounds/adapter 的整体窗口；其后按既定顺序接真实 owner/显示/finish/cancel/drain。完整 OFF、真实压力/成本、默认启用和 M6–M8 均不由本批取得资格；不再因没有新反例而扩展 copy 的 API 或容器。


<a id="joint-adapter-window-delivery"></a>
## 14. 已交付：packed/cursor canonical 与 adapter 的共同完成边界

| 旧符号 / 重复段 | 唯一目标职责与 caller | 本批新增 | 同批删除与保留原因 | 精确验收 |
|---|---|---|---|---|
| backend 在内部 finish/publish，manager 返回后另取 `m_lock` 安装 prepared tiles/extent | [runCpuMutationOperation](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1897)把原 publish closure交给 caller；[writeBytes](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1557)与 [writePageStoreOperation](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1742)只在短 manager gate 内 publish + install | 两个既有 public 写方法及内部模板各增加一个 `AdapterCompletion` 参数；一个导出 callback 类型别名。没有新增具名函数 | 删除 manager 两段返回后安装；保留两条写入口，因为 packed buffer 与 cursor callback 的像素 ABI 不同。保留 `PreparedTileUpdates::install` 作为已合并的唯一只增页安装政策 | 独立 reader 在 canonical 已新、adapter 尚旧时阻塞于 `extent()`，gate 后同时见新值；每架构 44 场景/172 观察，三类违例为零 |
| `OperationDelivery` 保存 batch 或 history execution，并暴露 `finish()` | delivery 现在只让 standalone 的原 admission 活到 prepared 存储销毁；history execution 不离开原 backend worker | 无新 member function；状态缩成一个 `unique_ptr<WriteBatch>` | 删除 `finish()`、execution variant/monostate、`<variant>` 和两个 history delivery 测试项。保留默认/移动构造、移动赋值、`isEmpty`，供输出占用检查和单次移动 | standalone close/同页 waiter、异线程销毁、legacy conflict、history checkpoint/commit/abort 回归保持 |
| manager `extent()` / `region()` 无 manager read gate，可能独立观察到安装中间态 | working adapter 的独立 reader 与 write completion 使用同一原 `m_lock` | 两个既有 getter 各增加 read locker，无新 API | `setExtent()` 在已持 write lock 时直接调用 `m_extentManager.extent()`，删除递归进入 getter 的可能；公开 working bounds 语义保留 | 完整 manager 双架构各 1,054 项通过；旧 pending/intent 和 retained reader 控制不改 |

失败顺序固定为：首字节前 `prepareAdapter` 拒绝时不执行 pixels；operation/execution 失败走原 mutation 失败责任；standalone completion 先调用原 publish，失败时不安装 adapter；成功 publish 后只做预备结构的无分配安装。history completion 不发布 root，但在 execution borrow 仍存活时安装 pending adapter，随后原 worker 归还 execution。诊断 phase 在 manager gate 释放后发出，避免 callback 重入非递归锁。

结构账本相对 copy 冻结点为：生产三文件 +95/-67，测试两文件 +31/-76；具名函数净减 1，生成图为 **1,814 APIs / 19,634 edges / 17 callbacks**。没有新增 owner/session/write set、manager/Tile 字段、TLS、friend 或 intrusion file。完整证据见 [本批记录](../evidence/br1_joint_adapter_window_20260929/README.md)，唯一状态裁决见 [92 §16.14](../92_br1_m6_m8_execution_baseline.md#joint-adapter-window-delivery)。

**保留对象和退出条件：** `OperationDelivery` 仍服务 standalone admission 生命周期，直到 prepared storage 不再需要原范围排斥；等所有 adapter 安装都能在原 transaction completion 内安全销毁局部存储时才能删除。`AdapterCompletion` 仍只服务 manager/backend 过渡边界；当 tiles3 adapter 不再是 canonical 发布的外部消费者时随两个参数一起删除。delete/default/copy/restore/purge 继续按 §12.2 审查，不能因为 add 探针为零就标记完成。

**停止规则：** 本表三行不再无反例重构。下一批只做剩余发布族对首条 direct 链的依赖审计；有依赖就关闭该一条并同步删除旧事后修补，无依赖就进入行动表第 4 项。函数数、测试数或可选泛化不构成继续修改本边界的理由。

<a id="direct-stroke-pilot-delivery"></a>
## 15. 已交付：首条 direct stroke 的非拥有 owner 与显示 cut

| 旧入口或缺口 | 最终职责与实际 consumer | 本批新增 | 同批合并、删除或保留 | 退出条件 |
|---|---|---|---|---|
| `KisBrushOp::addDabJobs` 对 vector `bltFixed` 显式传 `nullptr`，strategy transaction 无法到达真实 jobs | 原 `KisTransaction` 仍是唯一 session/commit/cancel owner；`KisPainter` 仅在 jobs 存续期保存非拥有绑定 | 一个 public `setStrokeMutationOwner(KisTransaction *)` 和一个 private pointer 字段 | 删除真实 async caller 的空 owner 实参；无 owner 入口改为消费绑定。后续调用图确认显式 owner overload 只有测试外部 consumer，已按 §20 删除并转为 private impl | 保留单一绑定桥；所有实际模式改用稳定执行上下文后再删该 setter，不增加并列 owner 入口 |
| base strategy 只有一次性 transaction，没有 opt-in 的跨 update checkpoint | 原 strategy 负责准入、checkpoint 与 finish/cancel 次序 | protected opt-in setter、protected dirty-publication checkpoint；`FreehandStrokeStrategy::Flags` 不变 | 没有增加第二个 transaction/session；测试派生 strategy 调用 setter，默认 Freehand 只增加必要的 dirty 发布切点调用。base 的 failure reporting 属于 S01 的可失败写正确性，不由 pilot 开关控制 | BC10 联合正确性已完成；BC9 资源/进度与正式配置完成后，由稳定策略配置调用 setter；若可由既有配置直接推导，则删除临时 setter，不并存两套政策 |
| fixed/bitBlt/mirror 与 multi-dab 分别要求 caller 显式传 owner，真实 1px/brush 没有统一桥 | public 入口统一从同一 painter 字段解析；owner 参数只保留在 private implementation helper 中执行原同步借用 | 早期 vector `bltFixed` owner 参数已由一个无 owner public 入口替代，不再作为默认参数 | 1px、mirror、async job 和测试共用同一绑定政策；删除 public 显式 owner 变体，保留 source-dependent 的独立拒绝规则 | current、G0、独立 source 语义仍在 private 实现分流；不为测试恢复 public owner overload |
| dirty 在持久 pending 尚未发布时可交给 projection | 原 update 序列在取走 dirty 前完成完整 transaction checkpoint | 无新公共 API；`issueSetDirtySignals` 调用上述 protected checkpoint | 不增加第二个 dirty 队列；checkpoint 失败前 dirty 仍留在原 painter，原 failure context 请求取消 | 递归 producer/no-input drain 和 checkpoint 失败已完成；补齐 save 与 BC9 压力下 continuation 后关闭 BC6 |

**数量解释：** 该交付当时增加三个具名函数（一个 public、两个 protected），没有增加 Freehand 公共 flag。它们分别承载跨 image/ui 的非拥有绑定、strategy opt-in 与原 transaction checkpoint；生产 caller 的硬编码空 owner已删除，四类 painter 写入口收进一个绑定政策。后续 §20 删除了只被测试外部调用的 public 显式 owner 变体；生成图的 PageStore 可达计数另由最终源码门给出，不能据此声称公共 API 没增加。

本节原目标验证为 `KisDabRenderingQueueTest` 双架构各 50/0/0 和 `FreehandStrokeTest` 双架构各 4/0/0；完整记录见[证据](../evidence/br1_direct_stroke_pilot_20260929/README.md)。其中 Freehand 所用预设实际为 Wash/indirect，不能单独证明 direct persistent 命中；修正后的 Buildup 联合证据和双架构各 8/0/0 见 [§17](#direct-stroke-joint-fixture)。本节只结算首条显式开发入口，不结算 BC9、完整 BC10、默认启用或 M6–M8。

<a id="stroke-mainline-intrusion-audit"></a>
## 16. `tool/strokes` 主干侵入裁决

本次对照使用仓库记录的 `origin/master` `cdf0a1c4a37ca3a928c37d44465e7e52b4b9bae9`，而不是较旧的本地 `master` `3cba915362726d6c8391f4497fdc0605de9d2465`。据此，`kis_color_sampler_stroke_strategy.*` 与 `move_stroke_strategy.*` 没有 BR1 差异；本地旧分支显示的差异来自 BR0 的 upstream replay，不能计入本轮 stroke 管线侵入。当前生产 `tool/strokes` 差异集中在三个文件：`freehand_stroke.cpp` +2/-0、painter-based strategy header +5/-0、implementation +104/-31。

| 主干表面 | 当前处置 | 必要性裁决 | 继续保留或删除条件 |
|---|---|---|---|
| `FreehandStrokeStrategy::Flags` | 已删除测试专用 bit，header 相对 `origin/master` 零差异 | 公开 flag 只服务 pilot 测试，没有产品语义，属于不必要侵入 | 禁止重新加入；测试派生 strategy 直接调用 protected opt-in |
| `FreehandStrokeStrategy::issueSetDirtySignals` | 只保留一次 `checkpointStrokeMutationBeforeDirtyPublish()` 调用 | 必要：这是 painter dirty 被 projection/display 消费前的真实观察边界；放到 PageStore 或 brush kernel 都无法保证外部观察顺序 | 若原 scheduler 提供等价的 transaction-aware dirty cut，则迁移后删除此调用 |
| `KisPainterBasedStrokeStrategy` 的 begin/bind/unbind | 保留在原 transaction owner 中 | 必要：这里唯一同时拥有 target/selection/indirect 资格、transaction、painters 和 finish/cancel 生命周期；下沉会迫使 image 层依赖 UI 模式，放到 brushop 会产生第二 owner | 不把 page 分区、预算策略或 paint kernel 搬进 strategy；稳定配置可直接推导资格时删除临时 opt-in setter |
| `hasMemento`、`tryEnd/tryEndAndTake/tryRevert`、cancel retry 与 job failure reporting | 保留此前 S01 改动 | 必要的失败正确性：PageStore admission/commit/abort 已允许可恢复拒绝，主干 void painter API 若不向 scheduler 上送会把部分写入登记为成功 stroke；这部分不提供性能收益 | 只有存储恢复为“这些边界绝不失败”并删除相应 failure API 后才能回退。双架构 `testPixelFailure` 各 22/0/0 证明当前消费者 |
| `KisPainter::setStrokeMutationOwner` | 保留一个 public 非拥有桥，四类写入口共用 | 当前最小跨层桥：不暴露 PageStore session/token，也不改变 painter 自持 transaction | 所有 painter 写入口改用既有内部 execution context 后删除；此前不再增加并列 setter/owner wrapper |
| eligibility 中的 Pixel Brush/RGBA8/OVER/单 painter 限制 | 保留为开发入口的安全门 | 临时必要，尚不是优越的最终产品 API；它防止未定义的 current/source/selection/mask 语义进入长 session | BC5/BC8/BC9/BC10 完成时迁入稳定策略配置或由已有 preset 能力推导；不能继续堆叠模式布尔值 |

**硬边界：** `tool/strokes` 只协调既有 transaction 的准入、外部可见 cut 和唯一终结。页归属、COW、缓存、预算、PageStore 状态和 brush kernel 不进入该目录。后续若为了性能在此新增独立 owner、公开 flag、page/token 类型或第二套 finish/cancel 路径，应直接拒绝；只有同一真实 fixture 暴露的生命周期缺口才能修改这里。

本节的逐文件裁决受 [MI1–MI8 主干低耦合合同](MAINLINE_INTRUSION_POLICY.md)约束。后续不只审查 `tool/strokes`：任何 UI、paintop、PaintDevice/DataManager 或其他主干接点都必须提交同一份侵入账本，并保持 PageStore 内部类型不越过语义桥。

<a id="direct-stroke-joint-fixture"></a>
## 17. BC10 联合 fixture：无生产 API 增量

本批先用真实业务行为关闭 owner 连续性、策略 undo、drain 和结构化失败缺口，没有为观察测试状态增加 getter。原 autobrush 是 Wash/indirect；fixture 在资源快照前显式设为 Buildup 并断言 incremental，修正此前未能证明 direct persistent 分支命中的证据。API 处置如下：

| 原缺口 | 同一 fixture 的实现与断言 | API 处置 | 仍开放的改动 |
|---|---|---|---|
| 两个 update 是否仍属于一个原 transaction 只能从分散测试推断 | direct Buildup 下两段实际 autobrush 写入、两次强制 update；一次 image strategy undo 同时清除两段并使 surrogate store 回到空位置，一次 redo 精确恢复完整图像 | **新增生产 API 为 0。** 用原 owner 代码路径和一个 undo 单元证明连续性；禁止增加 transaction 指针、session token 或 incarnation getter | 联合正确性已关闭；BC9 压力仍沿原 owner 验证，不增加观察接口 |
| 外部输入结束后，递归必要后继是否会在 finish 前排空 | 测试派生 strategy 通过既有 `KisRunnableStrokeJobsInterface` 追加三步 sequential successor；finish 记录三步已全部完成 | **新增 scheduler/strategy API 为 0。** 复用原 runnable-job 边界；没有第二队列或测试 public flag | 24 MiB 慢 reader/长 stroke 下已保持 drain；剩余可等待压力接续仍由原 scheduler owner承担，不增加生产 queue 控制面 |
| 策略 undo/redo 的观察时点不明确 | undo/redo 后使用既有 `image->waitForDone()`，再检查设备、命令位置与完整图像 | **新增同步 API 为 0。** 保留 image scheduler 作为唯一执行/排空责任 | 失败矩阵断言无成功 undo、唯一 cancel；不在 worker 内新增同步等待 |
| admission/像素/checkpoint/finish 失败此前只在分散 fixture | 同一 direct persistent strategy 分别触发实际 admission 拒绝、真实写入后的 pixel-failure signal、真实 checkpoint 拒绝和 finish 拒绝；均一次 cancel、无 undo、回滚为空、释放 memento | **新增失败 API 为 0。** 复用原 job failure context、scheduler fail/cancel 与 transaction abort；低层像素 swap-in 故障继续由 completion test 证明 | 正确性子范围已关闭；BC9 只增加压力条件和计账断言，不复制失败状态 |

本批生产文件 +0/-0；新增生产函数、字段、include、friend、锁和 TLS 均为 0，关闭状态成本不变。只修改 [freehand_stroke_test.cpp](/Users/apple/krita_gpu/krita/libs/ui/tests/freehand_stroke_test.cpp)及测试声明，复用原 undo store、image scheduler、failure context 和 runnable jobs。双架构目标各 8/0/0，源码与二进制身份见[证据](../evidence/br1_direct_stroke_joint_20260929/README.md)，状态裁决见 [92 §16.17](../92_br1_m6_m8_execution_baseline.md#direct-stroke-joint-fixture)。

**下一 API 决策：** 四类失败已经证明现有 failure sink、scheduler cancel 和 transaction abort 给出唯一终点，生产 API 保持不变。BC9 首个资源 fixture 又证明正常受限预算、慢 reader、长 stroke、取消/close 不需要新生产接口；8 MiB 反例只证明永久容量拒绝、可等待压力与取消仍被折叠。§18 已先在 PageStore/DataManager 内建立普通 direct cursor 的 callback 零进入/同 owner 重试边界，没有增加公开结果。随后 §19 复核发现原 scheduler 在 job 返回后销毁 job/data，且一次 update 有并发兄弟 job，当前没有可直接消费 deferred 结果的安全 ownership transfer。因此不先增加 typed result；下一生产改动转向 PageStore 内完整收费、公平和释放进度。当前不新增身份 getter、模式布尔值或 PageStore 到 UI 的类型通道。

<a id="operation-pressure-boundary"></a>
## 18. BC9 / OP9：backing 原子准备的 API 增删账本

| 修改前缺口 | 最终职责与 caller | 本批新增 | 同批合并、删除或保留 | 下一 API 触发条件 |
|---|---|---|---|---|
| 普通 `writeOperation` 在 callback 中首次触页时才可能因 backing/metadata 容量失败 | `KisPageMutationExecution` 在 callback 前为声明范围准备普通 mutable backing；唯一生产 consumer 是 backend 私有 `runCpuMutationOperation` 的 cursor 分支 | execution 私有 `prepareWrites`；session 私有 `preparationOnly` 参数；backend 私有模板 `prepareWrites` 策略参数 | `writeOperation` 启用，packed `writeBytes` 保留完整 payload 优化；removal/alias 保留原语义路径。没有新增 public/protected 符号或上层 wrapper | 只有底层能可靠判定 permanent/waitable/cancel 且原 scheduler consumer 同批接入，才扩展 operation result |
| 准备成功但 callback 未触碰的页会留下 Prepared 版本风险 | 原 execution 用第二组按 BoundEntry 位置的位记录本次准备归属；`finishPreparedWrites` 在 changed 导出前取消 untouched preparation | 原 touched overflow 扩为同一预算 allocation 内两组 word；`finishPreparedWrites` 同时负责 cleanup 与 export | 原 `collectChangedPages` 的单一 export 职责并入 terminal cleanup/export，避免再加一个独立 discard helper；不复制 page key | 参数化 changed-storage 必须保持 `pagesSealed == changed.size()`，否则不能接 continuation |
| metadata 取消后 entry 仍保存 Prepared transition 身份，持久 scope 无法安全重试 | `KisPageWriteCoordinator::recordCancelled` 作为原状态机内部逆转，由 `cancelPageLocked` 在 metadata cancel 成功后调用 | 一个 coordinator internal helper | 复用原 entry、claim、retirement 与 storage release；没有第二 cancel owner 或公开状态 | 同一 history owner 的压力拒绝后重试必须通过，entry 身份不能越过 backend |

本批生产范围为 PageStore、write coordinator 与 DataManager backend 六个内部文件；测试为 tiled data manager 两个文件。`tool/strokes`、paintop、painter、PaintDevice、DataManager 公开接口和 scheduler 均未修改。新增 public/protected API、字段、include、friend、锁和 TLS 为零；execution 的第二组 bits 由原 allocator/controller 收费并随同一 execution 终结。

这里出现的新函数有独立责任且替代了原 lazy-failure 缺口：`prepareWrites` 只完成全范围物理准备；`finishPreparedWrites` 合并“清理未触碰准备页”和原 changed 导出；`recordCancelled` 恢复原 entry 状态机以支持重试。它们不能与 page publication、scheduler continuation 或 adapter install 合并，因为 owner、锁和终结点不同；也不能为减少函数数把这些责任送到 UI 或 DataManager public API。

验证与状态见 [92 §16.19](../92_br1_m6_m8_execution_baseline.md#direct-operation-pressure-boundary)和[本批证据](../evidence/br1_operation_pressure_boundary_20260929/README.md)。当前结果仍是既有 `Failed`。§19 已确认现有 scheduler 不能安全重排已出队并将在返回后销毁的通用 job；typed pressure result 必须与原未执行工作单元的 ownership transfer、实际 caller 和旧模糊失败分支合并同批交付，否则不新增该枚举值。

<a id="stroke-continuation-ownership-audit"></a>
## 19. BC9 continuation：所有权先于结果类型

| 当前事实 | API 裁决 | 允许重新打开的条件 |
|---|---|---|
| `KisStroke::popOneJob()` 将 job 移出队列，`KisUpdateJobItem::setDone()` 在返回后删除 job/data | 不给 `KisStrokeJobStrategy::run()`、failure TLS 或 queue interface 先加 deferred/retry 状态 | 同批给出原 job/data 的一次性 ownership transfer，并证明 cancel、finish、析构和队列位置 |
| 通用 `KisStrokeJobData` 无失败重试克隆；runnable data 独占 closure | 不复制或重建整个 job，不把 closure 藏入新的 PageStore waiter | 原未执行工作单元能原样转交，且唤醒后仍由原 scheduler 调度 |
| brush update 有多个并发页 job，后接 dirty/checkpoint/递归 producer | 不重放整个 dab/update，不让一个页的压力越过已执行兄弟或后继 cut | callback 零进入、兄弟 job 不重复、后继不越序的联合 fixture |
| failure context 只拥有首个错误文本 | 保持它为 cancel/error bridge，不扩成第二 scheduler 或 budget owner | scheduler-neutral 的 `continue/defer/fail` 由原 job owner消费，且 page/budget/waiter 不上移 |

当前 public/protected 增量预算为 **0**：UI、tool、paintop、painter、PaintDevice 和 stroke scheduler 不新增压力 API。当前顺序按92 §17：CP1先完成控制存储，CP2–CP4关闭M6/M7，CP5再联合真实多文档公平、释放进度和原job接续；这些工作不得为了未来 continuation 增加未消费参数。若后续能在一个有限批次满足上表，新增结果必须替代原 `bool/Failed + 文本` 的对应分支并删除并列路径；不能形成闭环就继续明确拒绝。

<a id="painter-owner-api-convergence"></a>
## 20. Painter owner 公共接口收缩

| 收缩对象 | 最终边界 | caller 迁移 | 保留与删除规则 |
|---|---|---|---|
| `bitBlt`、标量 `bltFixed`、vector/QRect multi-dab `bltFixed`、PaintDevice-source `renderMirrorMask` 的 public 显式 owner 变体 | public 写入口只表达原 painter 操作；单一 `setStrokeMutationOwner` 在 strategy 已经拥有的生命期中绑定非拥有 transaction | 原目标测试改为先绑定 painter，再调用与生产 brush 相同的 public 入口；生产 caller 本就不需要显式 overload | owner 参数仅保留在 private `bltFixedImpl` / `renderMirrorMaskImpl` / `bitBltImpl`，用于同步借用与 mirror 内部传递；禁止为测试重新暴露 |
| 测试直接选择 owner 参数变体 | 测试覆盖真实的单绑定政策，包括错 owner、取消、snapshot、并行与 mirror | `kis_painter_test` 的相关 case 在 worker 启动前设置绑定，不在并发回调中改变它 | 测试无权要求生产 public API；后续若原 execution context 可承载同一语义，再迁移 caller 并删除 setter |

这一收缩不改变 PageStore 语义、transaction owner、source 独立性、checkpoint 或失败终点。它只去掉了第二种对外 owner 传入方式，把同步实现参数收回 private 边界。相对本批前工作树删除 5 个 public 显式 owner 变体，以 1 个无 owner 的 vector multi-dab 入口承接原业务形状，public 声明净减 4；private helper 继续承担同步参数传递。目标构建通过，Painter 目标矩阵 **520/0/0**、brush 生产入口 **50/0/0**，动态 brush 插件重建后加载不再引用旧符号；架构索引由 1,824 APIs / 19,890 edges 降至 **1,818 APIs / 19,722 edges**，19 个 frozen external intrusion files 未增加。完整命令与范围见 [92 §16.21](../92_br1_m6_m8_execution_baseline.md#painter-owner-api-convergence)和[本批证据](../evidence/br1_painter_owner_api_convergence_20260929/README.md)。

<a id="closure-api-actions"></a>
## 21. CP0–CP10 的API替代、合并与删除行动

以下是计划动作，尚无新的API增删通过结论。顺序/工时以 [92 §17](../92_br1_m6_m8_execution_baseline.md#br1-closure-schedule)为唯一来源；实际文件/函数查 [CODE_INDEX](CODE_INDEX.md#closure-code-index)，结算查 [包清点](CONVERGENCE_CHECKLIST.md#closure-package-checklist)。不能把表中职责名先实现成未消费方法。

| 包 | 最终唯一责任与允许改动 | 同包必须合并/删除或说明保留理由 | 跨层接口门 |
|---|---|---|---|
| CP0/CP3/CP10 | 测量、required、身份和资格复用真实fixture及原diagnostics | 删除失效的当前导航/重复测量口径；冻结日志本身保留，不将旧binary标成当前通过 | 不加生产测试flag、owner getter、未使用指标/热原子 |
| CP1 | 原budget/reclamation/read/retirement owner承担实际控制存储、必要尾内存和终结收费 | 无收费owner的实际分配迁入既有准入；所有重复通知候选列实际consumer，等价者合并；已删control block/free-list不重建 | 产品上层API不增长；不用新的通用allocator/executor框架代替完整结果 |
| CP2 | logical权限由metadata/selector，physical身份与pin由provider/binding；原exact读选择单一 | caller迁走后删除同义cache桥/ready旁路；未迁移raw/batch保留实际保护理由与CP7退出条件 | 不以refs=1或allowSameAllocation新增绕过权限，不向iterator传第二generation权威 |
| CP4 | 在原plan/epoch/publication链加入M7实际同步消费，claims与预构造安装共用原owner | 合并实际重复的准备/安装/分类body；保留Fresh、recoverable和普通可取消路径的语义差别 | 禁止独立commit-only事务/ledger；普通painter callback不取得不可失败资格 |
| CP5 | 原scheduler拥有未执行job的输入、队列位置、取消/析构和后继排序；PageStore只管准入/预算/唤醒 | 选定一条真实ownership路线后同批加入consumer和结果，并替代对应模糊Failed分支；不得留下两套retry/终结队列 | 仍默认上层public/protected净增长0；必要例外须给真实caller、不可复用原因、替代对象及退出条件；page/budget/waiter不外泄 |
| CP6 | 一个原read selection、一个按真实语义准备/安装/cleanup的适配交付 | 等价packed/cursor/restore安装循环或out-param随迁移合并；add/remove/default/alias区别不能为压API抹掉 | 保持最窄manager/backend桥，无长期current表或第二write set |
| CP7 | 原transaction持有scope，原painter一个非拥有绑定，job只借用 | 各模式迁走后删除可选owner重复分支、过时overload/注册/回调；仍服务ABI/未迁移模式的入口逐项列consumer，不新增模式布尔值库存 | `tool/strokes`仅负责原生命周期/语义cut，不能加入页、预算、缓存或重放政策；测试用真实绑定路径 |
| CP8 | 原成功恢复delta贯穿adapter；配置准备缓存只持不可变资源、预算与准确依赖key | 删除普通undo的全量rebuild caller；其他clone/default/序列化的全量函数保留真实理由；合并过时preset完成/当前only政策 | 不增加每dab全图/全history扫描；cache不持writer/token，不以UI缓存取代interstroke/undo语义 |
| CP9 | 唯一owner/consumer/配置清单汇总；默认策略只覆盖合格入口 | 无consumer的包装/字段/兼容开关必须删除；临时setter/friend/overload有最终去向；必要ABI写明稳定理由，不伪造净删除配额 | 对照MI1–MI8和实际ON/OFF成本；索引API数不等于public数，不提高ratchet掩盖扩张 |

每包交付填写“新增职责/签名 → 实际caller → 替代对象 → 同批删除 → 保留consumer/触发条件 → 失败终点 → 目标证据”。API与状态只是手段，不能把一种通知收费或增加几个探针当完整工作包完成。CP9负责汇总遗漏，不能成为将全部删除推迟到最后的理由。

<a id="immediate-task-api-delivery"></a>
### CP1 当前实施：即时任务 API 替代账本

| 实际 consumer | 内部实现 / 同批删除 | 失败与尚未结算 |
|---|---|---|
| 所有原即时回收 caller | 原 `kisSchedulePageStoreReclamation` 改为 typed capture 准备；原 executor 的 `kisEnqueuePageStoreReclamation` 消费 prepared node。删除导出 std::function 包装和每任务 QRunnable 创建；prepared 边界由 terminal node 实际消费 | 分配/构造失败不转交节点；sizeof/align 进入原 allocator。未传 budget 的 caller 仍为收费缺口 |
| last-use/退休通知/退休 pass/history pass | finished 统一在 capture/实际 task 释放后归还 root；删除四类 callback 内提前归还的出口，不另建 owner | 保留原记录，投递失败撤销额外计数/引用；pass 内其他分配失败恢复仍在 CP1 |
| `PrivateReleaser::cleanup` | 原 root 冷准备独立 TerminalCleanupJob；删除 terminal 时的新任务分配，node 在 root 析构后自行释放 | 冷 node 的实际收费及 controller 后寿命仍待结算 |
| runtime / drain | 原单 worker 使用常驻 runnable/FIFO；删除反复 pool.start 和旧 drain；pool.waitForDone 只用于 shutdown | 一次性 runtime 成本单列；deadline 独立；不替代 pressure/fairness 资格 |

UI/tool/paintop/painter/PaintDevice/scheduler 的 public/protected API 本轮净增长 **0**。新 private task/操作有本轮 consumer，替换原包装、投递和释放职责；没有增加压力结果或第二 semantic authority。CP1 未勾选，见 [92 §16.29](../92_br1_m6_m8_execution_baseline.md#immediate-task-convergence)和 [CODE_INDEX](CODE_INDEX.md#immediate-task-code-index)。

<a id="retained-storage-api-delivery"></a>
### CP1 当前实施：收费寿命 API 替代账本

| 原职责 / 已删内容 | 当前必要操作与本批消费者 | 保留边界 / 后续删除要求 |
|---|---|---|
| raw budget 只适用于 controller 内存活存储；原wake/context提前releaseLive及raw storageBudget字段已删除 | 原MutationStorageAllocator::retained，私有KisMutationStorageOwner allocate/deallocate/ref/deref/stop/detach；实际wake、typed task、read与retirement弱控制存储已消费 | 这是收费寿命，不是新预算/调度/语义权限。普通raw模式保留真实scope消费者；不能自动迁移所有容器或增加每block header。费用含allocator对象/owner本体 |
| 原make_shared/QShared create不能给实际控制块分配指定收费allocator；ensureWakeContextLocked已删除 | 原read/retirement context/record/wait/grant改allocate_shared；read准备函数被arm/close实际消费，retirement冷准备内联原prepareWait | 上层provider/public QShared ABI不变。两个context服务不同原owner/取消身份，不因名字相似强合并；外置capture/node/pass要按真实分配处理 |
| 原RetirementQueue ctor没有预算参数；原scheduleAfter没有真实DelayState收费 | 原composition传budget引用给原queue；既有scheduleAfter增加private storageBudget参数，retry真实消费 | 不新增新的scheduleAfter族、future压力参数或未消费getter；default nullptr兼容caller仍是欠收费清单，不能视作完成 |
| 原reset只取消引用却立刻返还wake费用；controller dtor立刻注销child | 物理dispose后退费；原child身份保留到最后retained存储和收费owner释放，stop后拒绝新分配 | 不pin PageStore/payload，不替换原parent池，不授予设备/写入权限；最后释放不需要重新申请terminal容量 |

本批新增操作都接实际consumer并替代原分配/释放责任，删去提前退费与无收费的包装；UI/tool/paintop/painter/PaintDevice/scheduler public/protected API净增仍 **0**。尚欠存储与必要冷预留见 [CODE_INDEX](CODE_INDEX.md#retained-storage-code-index)，不能以当前内部函数增加量直接推导工程能力完成。完整CP1与正式M6/M7/M8未结算。

<a id="prepared-reclamation-api-delivery"></a>
### CP1 当前实施：冷任务替代与合并（92 §16.31）

| 原分配/分支 | 当前实际替代与consumer | 保留条件 / 下一差集 |
|---|---|---|
| schedule内部局部Job构造；重复的一次性与拟议复用存储实现 | 原KisPageReclamationTask类型和prepare模板统一实际inline存储、allocator与dispose；schedule复用该实现；原executor只根据reusable选择最后free | 一次性schedule有tree/deferred cleanup等真实消费者，不能强删；这些未收费消费者另结算，不新建executor/权限owner |
| history/退休每pass新task及投递bad_alloc撤销；旧独立TerminalCleanupJob/make_unique | 两个原owner的prepareTask被store configure冷区间实际消费；原schedule方法仅排原node。terminal采用同一一次性node、原retained收费寿命 | 两个prepareTask服务不同语义owner，不能因同名合并状态。失败配置不得进入adoption，已存活cache继续收费；pass scratch仍欠 |
| budget/read每dispatch新task、强capture与投递bad_alloc分支 | 原context冷prepare；budget临时context pin/dispatchAgain，read原root pin/jobScheduled；producer消费已有node | runtime已在coldprepare启动；删除的只是任务分配失败分支。callback/process/必要冷准备仍可拒绝，不能删其保债处理 |
| 退休每notification新task/weak捕获与bad_alloc回滚 | prepareWaitState被真实provider/budget/retry两类准备消费；每wait有原任务，inFlight合并重复通知并持活动self/root pin | 不增加第二ready队列/record；晚通知仍验证原context与queued/retry身份。每次retry的Wait/Delay冷准备和deadline node/capture仍待收敛 |

本批上层UI/tool/paintop/painter/PaintDevice/scheduler public/protected API净增 **0**。新增内部准备操作已有同批caller并替代重复分配，调度/权限/物理释放仍由原owner裁决；不因内部函数增加量宣告能力完成。精确源码映射见 [CODE_INDEX](CODE_INDEX.md#prepared-reclamation-code-index)，CP1尚欠条件见 [92 §16.31](../92_br1_m6_m8_execution_baseline.md#prepared-reclamation-tasks)。

<a id="callback-storage-api-delivery"></a>
## CP1 API 替代：一个实际通知捕获和原订阅/deadline协议（2026-10-01）

本轮先发现原std::function隐式分配/复制无法覆盖真实费用，选择替换原协议的存储；没有新增观察服务、上层压力参数或M7/continuation接口。以下private实现必须与实际caller同批，不能单独登记成未来能力。

| 新/改实际符号及consumer | 替代 / 同批删除 | 保留理由与边界 |
|---|---|---|
| KisPageReadinessCallback；read/retirement/budget/wake/deadline原callback参数和字段统一使用 | 替换这些std::function及其隐式capture分配/dispatch复制，复制改为retain已冷准备的实际typed body | 原retained allocator管实际bytes/free，不持page/root权限；typed body为实际caller弱身份。budget外来callback只在冷准入fund，失败保留原capture |
| Subscription(callback)、Signal::subscribeRetained(prepared)；Registry和CPU binding真实caller | 删除signal门内try_emplace/捕获搬移、QP state控制包装，改为门外实际节点准备、原门内链接/重验 | cold prepared构造有真实消费者；subscribe便利包装仍服务直接signal consumer并共用同一准备/安装，非第二通知服务。原ID/取消/在途资格保留 |
| Registry实际ReadinessRecord/侵入树与releaseEmptyReadiness；sourceStatistics | 删除readiness unordered map节点/buckets和空表交换释放；actual record持自己的收费owner | 原ticket status仍唯一；核心terminal/source maps尚欠收费，不能删除失败分支或误授终态。失去原record的竞争使用同一signal的预备replacement |
| DelayState embedded hook/queuedPin、原Clock::Tasks与reset/pop/shutdown | 删除独立deadline multimap node；实际callback/state冷收费，O(log N)排序和原monitor保留 | queuedPin只持原DelayState，callback继续弱消费者；每次retry identity新建仍是真实欠项，不能为复用擅自删除取消身份 |
| W3捕获大小判定和read/binding/ledger门外准备 | 删除对未收费capture的固定slot大小假设，永久拒绝不先准备收费cache；失败候选门外释放 | 修改原准入/生命周期责任，没有新的wrapper状态权威或上层ABI |

上层UI/tool/strokes/paintop/painter/PaintDevice/scheduler生产改动和public/protected API净增均0。源文件增减与静态API计数只作为审查信息；真正结果是旧分配域同步替换和原consumer完整消费。本表冻结于 [92 §16.32](../92_br1_m6_m8_execution_baseline.md#callback-storage-convergence)；其record及retry欠项由§16.33–16.34更新，当前领取用 [最新代码差集](CODE_INDEX.md#prepared-retirement-retry-code-index)。不重建本表协议；完整CP1、M6–M8和默认开启仍未结算。

<a id="retirement-record-api-delivery"></a>
## CP1 API 替代：原 backing consumer 冷准备及唯一节点转交（2026-10-01）

本轮明确选择必要terminal存储，并同步删除旧的后补record/重复容器/包装；没有新业务模式、压力参数或第二退休权威。

| 新/改实际符号及consumer | 替代 / 同批删除 | 保留理由与边界 |
|---|---|---|
| `KisPageBackingPreparation`；原 `reserveBacking`、Store六个调用与rejected-result路径 | 同一个冷方法返回reservation+实际terminal节点，替代裸reservation及失败后补record；initial传已准备node，不新建等价reserve API | carrier没有语义权限，原quota/layout/provider/identity消费者不变；provider之前收费拒绝。仅PageStore私有层签名变化 |
| `kisPreparePageRetirementRecord` / unique deleter / owning intrusive records | 替代queue std::list节点、record值搬移、pass/close QVector reserve及另一个容器堆节点 | factory被write cold准备、initial整体准备和直接ledger注册使用；deleter是实际free汇合点，不是额外回收service。完整body与薄storage forward分开减少层间依赖 |
| 原 `registerBacking(..., preparedRetirement)` 与 `takeRetirementRecord` | 成功才接收node；原BackingRecord、retag/handoff及退休/close消费者复用唯一node，避免从原physical ownership脱离后再造节点 | take仅真实queue/close/initial失败回滚消费，原完整handle校验；初始失败回滚保持原Store门内，body free门外。旧register便利签名用于实际外部caller，复用同一factory |
| `retireOrDefer`、`defer`、`enqueuePendingLocked`、`finishAttemptLocked`、`takeForClose` | 入参/返回改为转交原node/list；三种orphan/admission/wait-grant shared reservation box删除，reservation内嵌 | 原provider、last-use和预算重验不变；splice不改变权限，不因节点复用消除取消generation。retry实际Wait/Delay/capture仍欠 |
| 原 `process` / `stopAutomaticWakeups` | 没有新增函数；只增加PRIVATE header中的KRITAIMAGE_EXPORT，让原外部test binary链接真实消费者 | 恰满目标显式停auto并调用真实process；没有friend/probe/getter/模拟pipeline。public/protected产品API与上层接口净增0；可见性事实不隐藏 |
| architecture `takeForClose` 合同与原ownership三事实 | 旧QVector具体断言改为已收费节点转交类型；注册/retire/debt字段更新对应真实代码 | manifest与19上层侵入文件限制原值不变，未放宽；source checkpoint在审查/重建图后刷新 |

源码真实增删、最终统一结果与身份见 [证据](../evidence/br1_retirement_record_20261001/README.md)。本表冻结于§16.33，必要retry/wait由§16.34更新；下一改动只从 [当前差集](CODE_INDEX.md#prepared-retirement-retry-code-index)领取，不能重建本表协议；其他scratch/core与固定成本、完整硬满进度尚欠，完整CP1及M6–M8未结算。

<a id="prepared-retirement-retry-api-delivery"></a>
## CP1 API 收口：原 Delay 统一协议与固定 queue retry（92 §16.34）

本轮先裁决每retry重建及无生产consumer的旧便利API，选择实现必要自主恢复并同步删除旧路径。以下新操作均由原queue或实际目标同批消费，无stroke模式、pressure/continuation或第二通知权威。

| 当前实际符号及consumer | 同批合并 / 替代 / 删除 | 保留理由与边界 |
|---|---|---|
| `KisPageReclamationDelay(callback,budget)`，原Queue::prepareTask | 原Executor::scheduleAfter改为prepareDelay；一次准备实际state/capture/hook，删除每retry Wait/task/capture/Delay分配及bad_alloc清空分支 | 原冷配置在physical前消费，全部成功才安装；同一收费owner/root责任，dormant实际bytes继续收费 |
| 原Delay::arm / cancel / takeReady；Queue::scheduleRetryLocked / cancelRetryLocked及retry任务 | monitor发布generation，消费者取一次；cancel清资格，下一arm不接受旧ready；排序node与callback存储复用。旧 `kisSchedulePageStoreReclamationAfter` 导出便利函数、friend及one-shot变体删除，六处测试迁移 | 三个private操作服务三种实际状态转换，不能用一个含糊bool函数合并权限。原isValid看存储、m_retryScheduled看活动资格，idle/drained不再把常驻cache当活动 |
| 原prepareWaitState / finished，原dispatchReady | 原完成点coalesce在途通知，重排同一task/pin；删除prepareWait懒建context，统一由冷prepareTask安装 | 每record订阅保留独立弱身份，拒绝转预付retry；不重用不同record取消身份，不增加ready队列/worker/物理权限 |
| 原prepareWait候选拒绝、原retireRecord/process/close | 保留同一node/debt及provider/budget复验，替代仅可手动process/close兜底的说明 | 有自主retry不等于provider操作必成功；实际effect/core索引与其他terminal/scratch容量仍未全部闭合 |

生产上层改动/public-protected API净增 **0**；新增内部方法与删除旧函数逐项列明，不用API计数作完成率。本表冻结§16.34的retry交付；当前下一工作只从 [最新CODE_INDEX](CODE_INDEX.md#read-terminal-storage-code-index)领取，证据和Git边界见 [92 §16.34](../92_br1_m6_m8_execution_baseline.md#prepared-retirement-retry)。

<a id="read-terminal-storage-api-delivery"></a>
## CP1 API 收口：原 read request/lease 终结与固定重试（92 §16.35）

本轮新增两个必要private操作，实际caller和旧路径同批替代；其他原方法改签名或扩大private测试可见性，不算新业务能力。不为减函数数目合并冷准备与GC终结两种责任。

| 实际符号 / consumer | 同批替代、合并或删除 | 保留理由与可见性 |
|---|---|---|
| `KisPageReadCleanup::prepareRequestLocked`；Store acquireReadImpl及原owner组合测试 | **新增1个private冷操作**。原request map节点门外准备先于读选择，原register填值/转节点并AcquireRead；旧register选择后解锁准备删除 | 真实失败证明必须在选择前准备。复用原cleanup的预算map，不建第二request表或token；新增方法private头导出供实际组合测试 |
| 原 `prepareTask`；Store configure | 改名/替代 `prepareLastUseContextLocked`，从last-use懒建改冷configure一次完成context/task/wake/Delay；旧dispatchFailed停摆及手动恢复兜底删除 | 原状态/worker不换；失败在physical adoption前拒绝。冷准备方法不是额外prepare包装 |
| `finishHistoryReadLocked`；release/retry/ack/close/worker | **新增1个private终结操作**，合并五类consumer的key→GC→节点终结；拒绝保持原historyPending/key，成功原节点交cleanup | GC接受与metadata ack是不同终态，不能把ack成功视为可删除记录。方法不导出；没有新增外部GC或release权限 |
| 原 releaseLocked/retryReleasedReadsLocked/acknowledgeCompletedLastUsesLocked/acknowledgeLastUseLocked | 返回void/只保留matched/accepted，删除releasedKeys/QVector结果及Store聚合；原cancel/release retry deques和ack matching/pending数组删除 | 原read owner统一终结，完整不同失败语义保留。Store不再二次维护GC清单，无兼容overload |
| 原History collectUnreachableLocked/collectBatchLocked；Publication三个调用点、Read各终结/captured消费者 | 单pointer/count签名替代QVector参数，全部caller迁移；单key终结不再建QVector，无新增重载 | 同期调用只读；原history内部容器仍开放，不把签名收缩当容量闭环 |
| 原private组合边界 | Read 13个原方法、Cleanup ctor/dtor、History ctor/dtor/prepareTask/waitForIdleLocked，共**19个既有方法**增加测试导出可见性；新增prepareRequestLocked亦导出 | 无friend probe/owner state getter/预算修改旁路。是private链接可见性增加，公开账本记录；上层public/protected和Store facade API净增0 |

完整CP1/全局失败原子性仍欠；当前实际差集及测试边界见 [CODE_INDEX](CODE_INDEX.md#read-terminal-storage-code-index)、[92 §16.35](../92_br1_m6_m8_execution_baseline.md#read-terminal-storage)和 [证据](../evidence/br1_read_terminal_storage_20261001/README.md)。

<a id="captured-release-api-delivery"></a>
<a id="history-handoff-api-delivery"></a>
<a id="metadata-retirement-api-delivery"></a>
<a id="synchronous-provider-result-api-delivery"></a>
<a id="registry-terminal-preparation-api-delivery"></a>
<a id="domain-journal-api-delivery"></a>
<a id="provider-adoption-api-delivery"></a>
## CP1 API 收口：capture→history→retirement与准备/结果接受（92 §16.36–16.43）

| 原接口/状态 | 最终归属与同批删除 | 实际consumer及保留理由 |
|---|---|---|
| Private::sealedPages + releaseCapturedView(token, QHash, capturedScope) | 一份 `KisPageCapturedRelease::versions` 用于查询和释放；releaseCapturedView接原unique node；旧QHash、析构复制和旧签名删除，无兼容重载 | Store capture、Private destructor及部分准入回滚；排序数组只读，retained前缀由原owner保护，后页拒绝可精确回滚 |
| PendingCapturedRelease/deque/releaseCapturedVersionsLocked | 原节点内嵌link与完成事实，新增私有finishCapturedReleaseLocked替代release/retry两份阶段序列；failed/released临时数组删除 | 原release/retry/worker/close共用一处推进，保留key直至history接受；processing只排除锁外交接的重复进入 |
| 原request cancel notification与captured retry | 原context的cancelPending收口为cleanupPending，复用原task/Delay/stop/cancelClose出口；不增加调度框架 | 位只表示原记录需要继续，版本和token事实仍在原节点；同任务至多32条，scan/版本公平另按CP5 |
| releaseSnapshotLocked的capturedScope参数/分支 | capture已由原记录保存事实，legacy retained snapshot只保留token/changedPages入口；无consumer的参数/计数/分支同批删除 | Store legacy releaseSnapshot不改变外部签名；没有第二capture snapshot终结模型 |
| 新节点prepare/构造/deleter，原releaseCapturedView/retryCapturedReleasesLocked | prepare与deleter在private头导出，构造内联；两个既有read方法增加测试链接可见性。没有新facade getter、friend probe或预算冻结旁路 | 原Store冷准备及原owner组合fixture。节点/版本容量实际收费到free；新增snapshot内部pendingCapturedReleases由close和测试消费 |
| History五组容器、collectBatchLocked / queueContinuationLocked / deferredKeysLocked | 一份WorkIndex保存原key、fixed candidates/cursor和effects，intrusive link只排队；旧容器和三方法删除，无兼容overload。collectUnreachableLocked返回void，全部Read/Publication/Store caller同批删除效果复制/累加，overlay retirement不再接输出指针 | 前台/后台共用collectPassLocked/collectSliceLocked/finishEffectsLocked/endScanLocked；内部snapshot新pendingEffects供close/目标测试观察。原collect/snapshot增加private头测试链接可见性 |
| History task / Delay / stopAutomaticWakeups | 原任务接一个冷准备Delay/context，复用既有通知机制；新增stop消费在Store facade销毁和组合fixture。idle等待在途task/通知的真实root pin归还，future retry不等于drain；close先冻结future wake并推进原Work | context的活动计数只配对实际临时pin，不增加新的业务阶段；原记录拒绝无新输入继续。永久压力尾退出仍是欠项，不增加新executor或错误阶段队列 |
| Queue acceptEffect、Ledger prepare/cancelRetirementOperation与原retireRecord | 一处无provider调用、无新增存储的效果接受；两项ledger私有friend操作转移/取回record预付map node。bindRetirementOperation填已有completion；有效result只保存/轮询，不重放物理副作用 | 新增方法只服务原History/Queue；同步write/transfer/foreign临时登记已按下方§16.39删除，显式pending/reference binding仍有独立计数/释放consumer；不推广为全部provider准备资格 |
| Metadata测试组合入口 | 增加现有KisPageStoreCpuMutationTest friend，冷构造时接真实budget/debt owner；没有新getter或修改private事实 | 256KiB固定额度从fixture构造前建立；实际allocator和Debt额度占满，不修改活跃Store配置 |
| 原HistorySlice/historySlice、collectSliceLocked、重扫pageKeys | HistorySlice改固定32 identity/count，无完整version Qt投影。新增metadata私有discardHistory取代history eligibility helper、逐版本snapshot和discard Qt数组；visitPageKeys流式枚举用于原rescan及public pageKeys结果，删除后者中间shard数组 | metadata唯一决定compact eligibility与revision；原Work持有root proof和效果packet。Reference bounded oracle同批迁移；generic discard/reference snapshots有实际消费者继续保留，无兼容HistorySlice overload |
| 原PrepareRetirementDebt callback、Ledger prepareRetirementDebt和prepareBackingChanges | callback和Debt入口改pointer/count，Store及4组测试consumer全迁移，不复制effects。新增一个Ledger私有prepareBackingChangesImpl合并generic Qt输入和history charged输入；原prepareBackingChanges public语义保留。Queue已接管的单record复用原atomic reclassify，删除effect/cookie/batch准备绕路 | 不是新的准备owner或结果记录；原cookie/slot/commit/cancel唯一权威。原slot实收容量并统一异常回滚，未增加失败阶段、队列、通知或上层API；队列仍在原record中保留拒绝债务 |
| 原consumeTerminalProviderOperation及7个生产consumer | **同批替代为一个const内部Ledger操作verifyTerminalProviderResult**；原owner保留result/activity，直接核对身份和registry终态。5个Store点、transfer和foreign同步retire全部迁移；旧符号及临时map node生命周期删除，无兼容overload | 同步provider/bridge是现行选择合同；不保留Pending，不增加预备token、结果队列或失败阶段。显式bind接口继续服务reference/组合模型的pending合同，异步业务接线仍未取得资格 |
| Ledger Private::acceptsProviderResultLocked；直接结果验证与显式bind | **新增一个私有共同身份政策**，合并两条接受路径的operation/provider/epoch/重复绑定判断；不增加权威事实 | 两个实际consumer需要相同身份拒绝；registry仍唯一铸造terminal evidence，原caller负责活动/结果寿命。transfer改核对原request.operation，错误返回ID不能自证 |
| Registry原构造、registerSource/allocatePending/complete/status/sourceStatistics | 构造接原process预算，Private实际std共享控制块/source节点收费。一个预备intrusive区间索引替代terminalRanges/nonSuccess；markTerminal/terminalStatus和终结时分配回滚删除。没有新facade方法、ticket类型或终结API | backend同批传sharedNonPayloadBudget；既有reference默认构造保留。区间节点/deleter/comparator/锁外释放仅服务原source生命周期；Pending实际成本进入storageRecords，不能拿记录数变多当活动增加。外层Qt包装/bootstrap仍欠 |
| 原allocation/alias/initial adoption；共用beginRetirement/revokeBindings及真实/测试provider retire | 原allocation保存一张private retirementCompletion，前移到物理副作用前；retire现场铸造和拒绝后的completeFailed删除，成功free原ticket，teardown取消。全部实际allocation插入点和reference provider迁移 | 这张ticket保留退休容量，原binding/physical key仍是物理权威；失败重试沿同一allocation，无新队列/失败阶段/调度器。每backing准备成本增加，索引/journal实际容量仍待关闭 |
| 原kisTransferCpuBinding和UnifiedSsd storeExact | 原scope收口失败ticket/source pin，archive preparation前移到payload/physical write前，删除重复失败终结/归还 | 没有新增helper/API或archive before恢复域；全局物理索引异常/永久退出尚未验收。真实硬满准备及退休验证见[本轮证据](../evidence/br1_registry_completion_20261002/README.md) |
| 原ResidencyObserver Payload/m_changes及track/untrack/commitTransition/acknowledge | 原Payload唯一domain/revision加dirty link，删除第二Qt journal；charged稳定payload节点和slot→Payload索引只服务原物理身份。physical commit不申请journal存储，exact ack只unlink同revision，untrack门外实际free | 真实provider物理tracking/迁移与Ledger ack，没有新结果记录/状态阶段；slot索引不拥有domain/revision。外层Qt observer/Transition/bootstrap和physicalPayloads核心仍欠 |
| 原backingDomainChanges() virtual与生产/测试override；synchronizeBackingDomains | 一个charged Changes类型及budget参数替代Qt输出，全部caller迁移，无兼容overload。原同步consumer使用原预算，默认诊断snapshot保留原accounting寿命；Probe内ack flag删除第二acknowledged数组 | 保留原provider registry共享cut和整个cut通过才ack的合同。实际snapshot/probe拒绝保留原journal，未增重试队列或physical动作；两个快照容量仍有实际成本 |
| 原configure/prepareResidencyChange/registerAdmission；DomainAdmission prepare/cancel/commit/detach | configure接原process root；charged admission snapshot/reservation数组、weak index及claim节点，删除live弱数组；registration标记现按下方§16.43收回同步调用栈。内部attachBackingBudget接原Ledger预算；返回对象及claim节点齐全后才发布原domainClaim，异常撤销同serial/claims | 原backend/physical producer/Ledger直接消费；无新的admission权威。Qt Transition/Admission/Reservation本体/控制块及完整尾出口继续CP1 |
| physicalPayloads/Tiles3PhysicalPayload与三个provider adoption入口 | 原Payload增加唯一logicalReferences，第二Qt physical表删除；新增内部prepareAdoption/adopt承接共用准备/安装政策，临时PreparedAdoption/PreparedPayload持有实际未安装node，无新持久阶段。fresh前置三nodes，existing alias一个node，三处直接allocation插入与手拼回滚删除 | allocate/payload/write-copy、immutable alias、initial native tile全迁移。binding仍唯一allocation handle/generation权威，原Payload唯一physical/domain/refcount；wrapper和TileDataStore内部登记容量保留欠项 |
| 原AllocationIndex/findExactAllocation/revoke/resolve/release/transfer/retire；lease map | charged stable map替代QHash，所有real/reference消费者迁移std接口；真实allocation/lease nodes和buckets复用原observer retained root；retire取同node到门外free，无兼容Qt索引包装 | 新内部observer prepare/retain/release/first节点操作只服务cold安装、physical计费和析构，原serial/dirty/slot合同不变；lease实际拒绝先于pin，同ID未占用，不增加lease权限或业务observer getter |
| 原memoryUsage/physical表遍历 | observer内原serial等待+domain求和替代，删除物理Qt表计数与锁内tile读，无第二resident计数状态 | 唯一physical record供原诊断consumer；实际交错验证保持resident/committed语义。收费/准备的保证成本单列，未取得性能收益 |

上层UI/tool/paintop/painter/PaintDevice/scheduler生产改动与public/protected API净增0。内部新节点是一项真实捕获/释放责任，不能用净API数替代保债、收费或完整CP1验收；当前结果、源代码差集及尚存consumer见 [CODE_INDEX](CODE_INDEX.md#captured-release-code-index)和 [证据](../evidence/br1_captured_release_20261001/README.md)。

<a id="ledger-backing-api-delivery"></a>
## CP1 API 收口：Ledger backing 安装、共享成员与退场（92 §16.43）

| 原接口/状态 | 最终归属与同批删除 | 实际consumer及保留理由 |
|---|---|---|
| 原BackingIndex/PhysicalBackingRecord与registerBacking的insert/emplace | actual charged stable map替代uncharged backing hash和Qt physical map；类型移到原retirement private头，两个实际node handles并入原record。prepareBackingStorage服务cold构造与消费后refill，安装只转交同nodes，无public overload/token/占位身份 | 全部fresh/initial/direct registration、原class/domain/retirement消费者同批迁移。initial rollback取回原record，reserveBacking先补齐缺失node，再交回caller；有效provider结果不重放 |
| 原sharedPhysicalMembers及每physical QSet | backing记录内嵌member links、原physical成员头替代；link/unlink只由原Ledger gate使用，旧表及其grow/终结/代表选择分支删除 | 三alias、handoff/reclassify、domain admission、releaseRetiredBacking。handoff只rekey同node，不复制成员身份或权威；投影只读原link |
| DomainAdmission原RegistrationIndex及begin/endRegistration(key) | 删除allocated set/buckets，参数改为同步registerBacking栈上marker引用，原authority gate管理link；scope出口移除同marker，detach只断开link | 原两次footprint观察需要排除同physical登记及domain移动；无异步consumer/持久phase，拒绝与成功共用scope；真实并发窗口和硬满已测 |
| attachBackingBudget与registerBacking allocator检查 | 挂接仍构造空map且不分配；首次安装锁内绑定actual prepared allocator，再检查原budget/allocator身份；删除挂接时提前创建accounting owner的候选实现 | 已存在cold limits/shared-parent配置及无预算Ledger兼容消费者要求此顺序；不增加bootstrap状态或controller。实际cold配置回归及笔刷压力全通过 |
| takeRetirementRecord / releaseRetiredBacking | 公开签名不变；唯一record交原queue，实际backing/last physical nodes先unlink/extract，再于Ledger门外free；旧移动value后锁内erase及shared-member终结容器删除 | hard-full registered/orphan retry、Debt无输入释放、close和late record。node/record释放时间不同按actual allocator fee分别断言；缓存寿命不混作已退休逻辑活动 |

生产3文件+271/-176、净+95；测试2文件+256/-8、净+248，生成审计单列。新增成本用于真实收费、准备及原子安装/最后free保证，不能计为纯去重；共享member表与allocated domain registration index实际删除。上层生产/API净增0，完整CP1仍开放；当前[代码映射](CODE_INDEX.md#ledger-backing-code-index)与[同源证据](../evidence/br1_ledger_backing_20261002/README.md)列明剩余provider/proof及固定成本消费者。

<a id="retired-policy-api-delivery"></a>
## CP1 API 收口：准备保证传播与过时政策回收（92 §16.44）

上方§16.37–16.43行记录各批冻结形态；History Work效果、Registry终结入口及退休分类以本表和当前源码为准。

| 原接口/状态 | 最终归属与同批删除 | 实际consumer及保留理由 |
|---|---|---|
| 原complete的producer业务失败/忽略bool两种政策 | 新增内部completePrepared noexcept统一独占已铸造Pending终结；allocate/retire/transfer/archive成功后Failed/rollback删除，alias/initial/scope/teardown/host-ready和reference CPU producer全迁移 | 准备已消除capacity拒绝；内部错ticket/重复终结按不变量处理。公开complete仍服务合法身份/参数拒绝，未删除；源/ticket准备及物理动作前真实失败guard保留 |
| beginRetirement的private ticket缺失→旧现场分配失败 | 原allocation准备合同要求有效ticket，缺失为不变量；旧业务失败文本/分支删除 | pin/last-use/transition拒绝有实际来源，保留同ticket重试。无新退休token、状态或provider API |
| History Work.effects/nextEffect、finishEffectsLocked、snapshot.pendingEffects、close guard/诊断 | 原slice局部charged effects packet替代持久packet；detach前检查原Debt owner、精确backing及record，成功只转交原intrusive queue，同批删除后置effect重试及全部读者 | 原owner gate覆盖detach→acceptEffect；Queue acceptEffect改void noexcept，无分配/provider调用。packet/Debt/root/revision拒绝仍在detach前，由原Work/task/Delay接续；普通queue真实拒绝不混入此保证 |
| bindRetirementOperation缺node的generic fallback；ProviderOperationRecord.detachedRetirement；bindProviderOperationImpl bool wrapper | 退休只填原record预装node，fallback删除；原record指针表达分类，第二bool删除。generic bind原body直接归原方法 | reference退休模型改actual provider Pending→原Queue→同node回收，未准备结果拒绝。generic bind仍有Pending/reference消费者、活动计数/释放和真实分配来源；不外推异步生产业务资格 |
| metadata indexedHistorySlices旧无owner夹具 | 原attachRetirementDebtOwner在cold configure前接模型接收者，逐项核对准备/commit/取消数量 | 合成replica只验证compact索引与责任接收合同；缺owner/backing/record及hard-full原record交接分别由真实CPU fixture覆盖，无新friend/public probe |

生产16文件+79/-119、净-40；测试/模型4文件+88/-33、净+55，生成审计单列。新增前置检查是缺口修复，其成本包含在生产差集；prepared方法承接完整共享政策，没有新持久阶段/队列，上层生产/API净增0。该批5352/0/0及原失败样本见[证据](../evidence/br1_retired_policy_20261002/README.md)，后续残余及保留依据由下方§16.45更新。完整CP1、默认启用及M6–M8正式资格不变。

<a id="protocol-residue-api-delivery"></a>
## CP1 API 收口：效果接受、后台许可与废弃查询（92 §16.45）

| 原接口/状态 | 最终归属与同批删除 | 实际consumer及保留理由 |
|---|---|---|
| batch effects的缺Debt补准入、缺record跳过；History独立原record检查 | 私有takeEffectRecord noexcept吸收共同接受不变量，两个入口消费已提交Debt和原record；旧fallback/continue删除 | generic metadata及publication原reservation先验证/提交；batch/foreground和History门内转交的调度差异仍实际需要。未登记结果retireOrDefer保留真实准入/物理拒绝 |
| wakeEligible、retry provider重查与record.backgroundRetirement两套事实 | 原record.backgroundRetirement唯一：registered取登记许可、orphan准入固定一次；prepareWait、初次/效果退休、retry/close全迁移 | 原容量行验证至少3次retry和最终free后的query次数0/1；许可无需新cache/API。Pending、subscriber拒绝及Delay真实进度机制继续 |
| Read retireEffectsUnlocked(QVector, lock)及5个空参数consumer | 改为processRetirementsUnlocked(lock)，直接foreground process(max)，删除effects参数和旧Read符号 | 保留后台短路、锁外窗口及activeProviderCalls配对；通用Queue/Publication effects接口仍有真实batch消费者 |
| Store preparedPageExtent及private preparedPageExtentLocked；backend resolveCurrentPagePresence公开输出包装 | 全部无consumer，删除声明/完整body；底层extent算法和manager预备scratch实际接口保留，MR2索引同步修改 | 当前联合prepareSurfaceLocked和resolveCurrentPagePresenceInto承担原责任；无callback/override/配置引用，不保留空兼容包装 |

生产14文件+38/-117、净-79，测试1文件+6/-0；生成审计单列，上层生产/API净增0。最终双架构5352/0/0及19项删除检查见[证据](../evidence/br1_protocol_residue_20261002/README.md)，实际端点见[CODE_INDEX](CODE_INDEX.md#protocol-residue-code-index)。[92退出审计](../92_br1_m6_m8_execution_baseline.md#protocol-residue-delivery)说明真实失败/旧模式的保留与删除条件；本次清理目标完成，完整CP1和M6–M8资格不变。

<a id="ledger-provider-proof-api-delivery"></a>
## CP1 API 收口：provider 原节点接纳、共同切点与 proof 前置准备（92 §16.46）

| 原接口/状态 | 最终归属与同批删除 | 真实消费者及保留依据 |
|---|---|---|
| ProviderIndex QHash、pendingProviderRegistrations QSet及后置accepted insert | 一个原paid节点贯穿pending/accepted/rollback，acceptedRevision表达外部接受事实；旧pending集合和后置分配删除 | registerProvider、provider/result/backing/retirement查询共用accepted lookup；合法重复/ID/配置/admission拒绝保留，实际硬满和异常在接受前归还同节点 |
| providerFor values/list、synchronizeBackingDomains隐式共享provider snapshot | 同一scalar cut/cursor遍历原accepted节点，门内iterator不跨callback；旧Qt复制/分配全部删除 | route、domain同步及精确ack消费者迁移，callback登记不改变已捕获cut；pending不能因后来接受进入旧cut。没有新route API或第二索引 |
| sealedProofs QHash、seal在索引插入前消耗stamp | 原paid proof节点先准备、provider验证后无分配链接，接受后推进stamp/输出；旧Qt proof表删除 | native seal、generic finishWrite、validate/owns/revoke及reference消费者原签名不变。实际容量拒绝保留prepared/output，既有Failed/cancel仍有准备/Qt失败来源，不能删除或误称自动resume |
| 各节点准备/释放与预算挂接兼容 | 两个真实consumer共用局部LedgerNode/LedgerIndex；原budget来源随节点保留，unlink后门外free及原成员析构次序 | budgetless/reference及先登记后attach实际消费者继续；post-attach节点收费。单allocator整表替换会在挂接时重分配旧节点或改兼容合同，因此不引入该后置窗口；bootstrap总收费仍欠 |

生产1文件+158/-67、净+91，测试/模型4文件+153/-3、净+150；生成审计单列，上层生产/API净增0。保证成本单独解释，不宣称净简化或性能收益。[最终证据](../evidence/br1_ledger_provider_proof_20261002/README.md)为双架构5354/0/0、21项检查；[代码索引](CODE_INDEX.md#ledger-provider-proof-code-index)与[92裁决](../92_br1_m6_m8_execution_baseline.md#ledger-provider-proof-delivery)记录该批欠项，exact/capture后续由下方§16.47更新。完整BR1目标继续，本有限交付未关闭CP1或正式M6–M8。

<a id="capture-metadata-api-delivery"></a>
## CP1 API 收口：最小 exact 查询与同 capture 记录（92 §16.47）

| 原接口/状态 | 最终归属与同步删除 | 真实consumer及保留依据 |
|---|---|---|
| versionSnapshot的KisPageStateSnapshot输出、projectVersionPair/countMutationInput | 原私有exact查询改scalar VersionInfo；generic read可选paid ReplicaCandidates，锁外准备后重选cut。seal/validate/write/default/adoption/read全迁移；projectVersionPair仅余mutationBase，body归原函数、包装/开关删除 | page存在/exact不存在保留不同语义；generic候选硬满返回原Failed，未发布读保护。mutationBaseSnapshot、generic applyProjectedSequence及publication Qt准备仍实际可拒绝，Failed/cancel不删除 |
| capture transactionDelta Qt exporter、Private removed QSet/staged QHash | 原内部captureDeltaLocked直接填同release记录的paid version/removal/surface容量；Private查询同份immutable sorted cut，旧导出调用和第二容器删除 | preparedPages及其他消费者仍用transactionDeltaLocked，保留该函数；original root/transaction/token归属不变，无第二scope registry |
| Private Qt共享控制块/default QHash/提前Store cleanup | retained allocate_shared支付真实Private+control，paid default map slot先于buffer；最后Store ref由首声明的原deleter成员持有，成员销毁后释放 | CpuReadGuard/外部view仍真实共享scope；map保留旧default buffer跨global cache eviction，不删除。一个测试friend验证原private shared-budget配置，public产品方法没有增长 |
| singleton capture retain/release的通用Qt投影、native CPU exact discovery快照 | 原private applyCapturedProtection借原slot；retain准备/revision复验，release unlink并把空block/charge归同record cleanup。native discovery只借门内records | identity/foreign/duplicate/stale/pub/publication-claim拒绝仍真实；mixed sequence/oracle保留StateMachine分支。versionReleased/snapshotReleased/next记住已完成事实，后续history/key/epoch拒绝不得重放 |

生产10文件+363/-147、净+216；测试2文件+137/-10、净+127；生成审计单列、上层生产/API净增0。新增收费/准备/slot生命周期保证有成本，旧投影/容器删除不等于整体净删。[最终证据](../evidence/br1_capture_metadata_20261002/README.md)、[代码](CODE_INDEX.md#capture-metadata-code-index)与[92裁决](../92_br1_m6_m8_execution_baseline.md#capture-metadata-delivery)对应双架构5358/0/0和18项检查；通用metadata/overlay实际容量及固定/永久尾出口继续CP1。

<a id="publication-residue-api-delivery"></a>
## CP1 API 收口：空 publication 效果协议和 detach 快照（92 §16.48）

| 原对象 | 最终归属与删除 | 保留的实际责任 |
|---|---|---|
| PreparedPublication.effects / retirementEffects() / installPublication effects输出 | 全部删除；commit/default replacement/restore保留replicas为history，recoverable write转交backing，detach只改publication字段；StateMachine及原oracle证明这些种类不产生效果 | generic StateMachine effects、abort/cancel/discard/GC仍产生真实退休；Ledger的batch effects合同继续服务这些consumer |
| PreparedMutationCommit.publicationRetirements与commit historyRetirements搬运 | 字段与空packet删除；commit/restore的backing reservation只准备真实class changes，history collect后继续原foreground queue pump | 未删history key交接、queue调度、publication冲突重准备和DeferredPublicationCleanup；成功发布不改成退休失败 |
| detach准备与activity复验完整version snapshot | 与安装共用原record isPreparedBy，旧replica/lease/pin/last-use/capture复制删除；无需新增接口 | writer、版本身份、publication claim及批量拒绝继续；晚保护读取原记录，不覆盖旧快照 |

生产+14/-33、净-19；测试+31/-44、净-13，生成审计单列。无新增业务保证/持久状态/队列/上层API。全部原caller迁移、双架构5358/0/0及12项删除/保留检查见[证据](../evidence/br1_publication_residue_20261002/README.md)。[代码](CODE_INDEX.md#publication-residue-code-index)和[92裁决](../92_br1_m6_m8_execution_baseline.md#publication-residue-delivery)保留真实失败来源与完整CP1差集。

<a id="publication-storage-api-delivery"></a>
## CP1 原 publication 候选的实际容量与清理寿命（92 §16.49）

| 原对象/假设 | 最终归属与删除 | 保留的真实消费者 |
|---|---|---|
| Data make_unique、普通entries/growth vector、Qt deltas/authority及嵌套安装快照 | 同一PreparedPublication的独占容量由原allocator实际支付；私有安装值保留原字段，原assign/putReserved模板共享政策；header版本容量重置，旧持有容器删除 | commit/default/restore/detach/recoverable全消费同一候选；StateMachine临时Qt投影/集合仍准备可拒绝，不另建业务权威 |
| MetadataArenaGrowth默认无预算holder、安装局部QSet重复检测 | 所有实际构造绑定原收费owner；未挂接payload先于reservation释放；单记录physical重复检测用无分配前缀扫描 | register/captured/projected与candidate共用原helper；generic batch QSet仍承担真实跨记录检查，性能未测 |
| MetadataBudgetAuthority detach后release依赖原controller、空unique_ptr deleter保留owner | 已支付arena/directory费用仅记入原accounting owner保活字节，不重复reserve；controller退场后同shared-child费用延续；最后clear替换完整DataPointer | 原reject/cancel/Deferred cleanup及晚shard引用仍真实；合法身份/revision/claim拒绝不转为断言或新重试阶段 |

生产4文件净+112用于收费/所有权/晚释放缺口修复，测试2文件净+163，生成/ownership单列；上层生产/API净增0，无新持久状态或队列。最终5390/0/0与17项删除/保留检查见[证据](../evidence/br1_publication_storage_20261002/README.md)；[代码](CODE_INDEX.md#publication-storage-code-index)与[92](../92_br1_m6_m8_execution_baseline.md#publication-storage-delivery)保留generic临时Qt、mutationBase/overlay及bootstrap/完整尾出口的有限下一责任，CP1和M6–M8资格不变。

<a id="mutation-base-query-api-delivery"></a>
## 原首写查询的最小事实（92 §16.50）

| 替代对象 | 最终归属与同步删除 | 真实保留责任 |
|---|---|---|
| mutationBaseSnapshot及两版本/replica/protection Qt输出 | 私有queryMutationBase返回stack标量MutationBaseInfo；root/selected、writer、generation及候选来自同一原shard cut；旧接口与所有调用删除，无兼容重载 | 普通versionSnapshot仍服务exact读和paid候选消费者；generic StateMachine转换/exporters仍使用Qt，未迁移 |
| prepareWriteBaseLocked里的快照findVersion及before循环 | 原记录按既有顺序/validity/operation/domain/layout/physical条件返回一个观察候选；native/generic/semantic共用原入口，无上层API改动 | pending/removal/default发现控制、default/descriptor拒绝及joint physical资格复验继续；没有新authority、持久阶段或结果队列 |

[代码映射](CODE_INDEX.md#mutation-base-query-code-index)、[同源证据](../evidence/br1_mutation_base_query_20261002/README.md)和[92裁决](../92_br1_m6_m8_execution_baseline.md#mutation-base-query-delivery)记录有限交付与净增成本。消除查询分配来源不等于首写所有准备都不可失败，Failed/cancel合同与完整CP1差集保留。

<a id="read-failure-residue-api-delivery"></a>
## 原 read 终结的分配失败归属（92 §16.51）

cancel/release/ack直接消费原metadata保护节点；取消状态、last-use与history事实仍由原记录持有。删除旧投影时期的三处外层bad_alloc捕获及后台对应捕获/失败标记；订阅前同锁验证去重，锁外watch复验保持。无签名变化、兼容桥接或新失败阶段。

真正的subscription和history容量拒绝分别由armLastUseLocked、cancel/finishHistory/finishCaptured入口承接；claim/身份拒绝、Pending/Debt和公开ticket拒绝继续其原合同。生产净-11、测试源码零改动，[代码](CODE_INDEX.md#read-failure-residue-code-index)、[同源证据](../evidence/br1_read_failure_residue_20261002/README.md)和[92](../92_br1_m6_m8_execution_baseline.md#read-failure-residue-delivery)记录删除依据及剩余条件；完整CP1未结算。

<a id="metadata-working-storage-api-delivery"></a>
## 原 metadata 转换值与安装的统一政策（92 §16.52）

| 替代对象 | 最终归属与同步删除 | 真实保留责任 |
|---|---|---|
| 公开applyKnownValid(Qt snapshot)、applyImpl包装 | known-valid能力收为MetadataCoordinator友元private paid入口，三个原生产调用全部迁移；Qt apply与paid入口共享applyPolicy的一段switch/guard。后续step按值接收并move，未接受值无安装consumer | 外部Qt apply保留完整current/next验证和拒绝原快照；省略boundary扫描仅限原indexed state，不省略transition局部保护 |
| PreparedPublication::Data的独立Replica/Version复制构造、Qt临时生产投影 | 原付费Version/Replica移为私有工作值，从原record直接构造；state/result只拥有局部工作容量。成功move同Version进installRecords，不再第二次复制lease/last-use/capture | 原record/claim是唯一authority；before/input仍用于delta、authority、removal见证，晚保护和revision复验保持 |
| seen/included/previous/retained/discard临时集合与未收费batch QSet | 原entries/before/next及transition输入见证重复/移除，集合删除；真实physical batch唯一性改为原allocator的paid set，全部节点准备先于record install | prefix/membership和单record重复检查仍有扫描成本；paid数组/set、arena/index/activity准备拒绝仍真实，不授予短gate或性能资格 |
| 私有拒绝值复制恢复与逐step深拷贝 | 生产失败直接丢弃未安装值，公开oracle仍恢复原快照；只保留第一份实际before/input见证，后续转换和安装转交同值。无consumer的const state lookup删除 | producer公共Qt effects/reason在Debt/install前生成；Store/publication后续聚合仍有cancel/abort等消费者及收费缺口，不能删除packet或声称全链不可失败 |

[23项删除/保留检查](../evidence/br1_metadata_working_storage_20261002/deletion-checks.json)列明原Debt cookie取消、合法identity/revision/claim、paid proof/overlay拒绝和Failed/cancel的真实依据；没有新恢复阶段、队列或上层API。生产净+156用于实际收费工作值，共享一段政策不等于整体净删。[代码](CODE_INDEX.md#metadata-working-storage-code-index)、[证据](../evidence/br1_metadata_working_storage_20261002/README.md)与[92](../92_br1_m6_m8_execution_baseline.md#metadata-working-storage-delivery)绑定产品`8896ac1dab5364e403048d9069703c4ed9dd0978`；完整CP1仍开放。

<a id="effect-acceptance-api-delivery"></a>
## 原 effects 接受点与过时调用侧协议回收（92 §16.53）

| 旧实现 | 最终归属与同批删除 | 真实保留责任 |
|---|---|---|
| metadata 返回KisPageTransitionResult的Qt effects/空next、Store/publication聚合和append/copy | 原paid span经commit receiver直接转交原record，metadata改为accepted/reason；cancelPage/prepareAlias/PrepareAbort输出参数与所有caller效果数组删除 | 公共Qt StateMachine oracle仍完整返回next/effects；Ledger显式effects输入还有reference consumer，不混同生产输出 |
| HistoryEffects类型、collector局部packet与二次acceptEffect | discardHistory在同一owner-gated调用中完成原Debt commit及record转交，只返回removedMask；collector只更新原扫描和descriptor | 历史reachability、root/cursor、真实paid准备/Debt拒绝与原冷retry保持，不新设恢复阶段 |
| queue retireEffects旧batch接受与独立执行循环 | acceptEffect独占原record转交，同一ready list按原许可调度首次尝试；processAcceptedEffects替代旧入口，worker/manual/pump复用一个私有retireBatch | worker≤32、manual总额度、foreground首次尝试及原pending/subscription/retry/operation/close保持；无新持久事实或队列 |
| operation回滚后页拒绝时跳过退出pump | 原finishPreparedWrites的退出guard吸收releaseStorage和pump，前页接受不可丢失/重放 | 原两页borrow逻辑claims仍保留到取消；Failed/cancel对真实准备拒绝必要，CP5未实现原job转交 |

compact result只表达原metadata调用结果，不是CP5 scheduler continuation。API图净+1来自原queue私有retireBatch的三个真实入口，改签名及pump替换删除原入口；acceptEffect原集成端点导出供actual record测试，Store.h一行test friend未新增public/protected方法。上层生产改动/API净增0，manifest仅迁移旧服务符号，所有门限不变。生产净-12包括这项接受保证的成本，[23项检查及保留依据](../evidence/br1_effect_acceptance_20261002/deletion-checks.json)、[代码](CODE_INDEX.md#effect-acceptance-code-index)和[证据](../evidence/br1_effect_acceptance_20261002/README.md)绑定产品`7c90a4f07d9486391df22eb2cc7aed6bf8a5e171`；完整CP1与M6–M8正式资格保持开放。

<a id="overlay-storage-api-delivery"></a>
## 原 overlay 的最小输入与清理拒绝归属（92 §16.54）

| 旧实现 | 最终归属与同批删除 | 真实保留责任 |
|---|---|---|
| Qt overlay producer输入、candidate/state数组和未收费nodes/control | 一个pointer/count overlay入口，原paid Data/state/control/index与maps/buckets；producer拷贝于metadata准备前释放 | 实际budget/identity/source-change拒绝在安装前保留；所有在途insertions参与容量准备 |
| keys set、historical数组、derived extent完整Qt delta及临时RemovalSet | 已排序changes负责去重/lookup，paid key scratch读取原state/base bounds；只给epoch原语一份最小keys输入 | 正确默认像素/derived extent语义和范围/修订拒绝；公开Qt oracle/commit/restore仍有consumer |
| 完整detachment Transition数组及kind/operation/epoch旧分支 | prepareMutation只接受版本身份+原交易；共用原metadata准备/安装政策 | 无writer、exact Prepared transaction、重复version和全页claim拒绝；protections保持当前值 |
| Qt surface detach/后置容量拒绝、foreground History throw和后台独立rescan | surface actual容量在安装前准备；metadata+原collector rescanRequested保留清理责任，一份collectPassLocked覆盖foreground/worker；candidate History节点整套删除 | 节点/GC/Debt真正拒绝沿原ready/cold retry继续，已发布结果不回报未执行；CP5 Failed/job ownership仍开放 |

图API净+6为原paid Data/state构造/deleter、排序lookup/comparator及私有extent投影；改签名迁移全部consumer，无上层生产改动、新阶段或新恢复队列。原内部端点导出/test friend仅供实际容量集成测试，不新增上层可见状态权威。checker的旧QHash合同同批更新为原paid TransactionMap，门限不变。[22项删除/保留检查](../evidence/br1_overlay_storage_20261002/deletion-checks.json)、[代码](CODE_INDEX.md#overlay-storage-code-index)与[证据](../evidence/br1_overlay_storage_20261002/README.md)绑定产品`5188f8d9c5c2a2e0e726a3ef667890e49b630585`。下一原commit facade/descriptor/configuration实际存储、外部Qt输入/输出/注册/诊断、bootstrap/控制本体/固定成本及完整永久尾handle继续CP1；完整CP1与M6–M8资格未结算。

<a id="commit-descriptor-storage-api-delivery"></a>
## 原 descriptor 与 commit 准备政策的传播和旧协议删除（92 §16.55）

| 原对象 | 最终归属与同步删除 | 保留合同 |
|---|---|---|
| putDescriptorLocked / DescriptorHash / bucket reserve | 原 prepareDescriptorLocked / pointer-count batch 准备实际 paid ordered nodes；install 只转交或交换，全部 post-success 插入删除 | 原版本索引唯一决定可见描述；实际准备拒绝在副作用前，semantic revision 仍复验 |
| 每版本及 native Page 描述副本 | 原索引共同持有相同布局的 immutable value/control；原 descriptorLocked 同时提供受保护 borrow，Page value 删除 | native claim/session 覆盖使用期；外部 Store bool/copy 输出保持，晚 semantic 操作仍要求原 owner |
| unpaid commit Data / Qt descriptor changes / History key packet | 原 Data/deleter 与 paid 数组/节点同 accounting 寿命；History 直接消费已有 proof/change/restore target，旧 packet 删除 | 真实 metadata/root/backing 拒绝保留；已成功发布与后续清理继续分责，原 rescan/retry 不变 |
| allocated QSet commit/abort claim | 原同步调用栈 intrusive record 覆盖全部解锁；原 owner-gated 查询和退出 unlink，旧分配来源删除 | 不扩大活动含义或增加第二队列；close/abort/mutation admission 继续读取同一事实 |
| importDefaultRevisionLocked 的逐项后置导入 | 原完整 paid high-water 冷准备，原子交换先于 owner/metadata/epoch 初始化；旧入口及 loop 删除 | 合法 surface/revision/重复拒绝保持；其他 bootstrap 失败不被包装为已验收全局原子配置 |

图API净+4为原私有 Data/deleter、stack claim、ordered comparator 与准备签名替代合计，无上层新生产API、持久业务阶段或恢复队列。实际收费/冷拒绝保证有成本；冷相等扫描和 ordered lookup 未取得性能裁决。checker 同步迁移 unique_ptr 形态、补 descriptor/high-water/claim 检查并收紧 Page ceiling 688→512，baseline ratchet 不变。产品`7141769304ae83437db17339383e6f43e464963c`，[18项删除/保留检查](../evidence/br1_commit_descriptor_storage_20261002/deletion-checks.json)、[代码](CODE_INDEX.md#commit-descriptor-storage-code-index)和[证据](../evidence/br1_commit_descriptor_storage_20261002/README.md)绑定最终 5412/0/0 双架构结果。原 commit/restore 的 Qt 工作输入/投影、epoch/core、其他 wrapper/bootstrap/固定成本与完整永久尾出口继续 CP1；M6–M8 正式资格仍未结算。

<a id="prepared-fact-residue-api-delivery"></a>
## 已准备事实的旧失败政策与副本删除（92 §16.56）

| 原对象 | 最终归属与同步删除 | 合法剩余 consumer |
|---|---|---|
| seal private/proof、commit、restore 的 host 缺票假拒绝 | 原 configure 准备成功 terminal ticket 后才开放入口；全部上述 consumer 共用不变票，旧业务失败/候选回滚删除 | 冷 configure source/ticket 容量拒绝，公共 completion 身份验证仍保留 |
| bool revokePreparedProofLocked / owned epoch abort false 重试 | 私有 void noexcept 撤销原 claim 保护的唯一 owned proof；只 unlink/free。同一 claim 内的有效交易保持 active 到 epoch exit；两个假退出删除，身份破坏按不变量处理 | 公开 Ledger revoke/epoch abort 仍拒绝非法/foreign/重复输入；原 metadata/Debt 准备与 abort 拒绝保留 |
| commit surfaceChanges QHash / preparedKeys QSet | 原 state vector/hash 直接回答相同查询；两份副本及 include 删除，原输入完整验证保持 | 公共 isValid 去重、Qt proof/directory/transition/backing 和 restore/epoch 仍有实际消费者，未宣称完整收费 |

生产3文件+49/-67净-18，覆盖本包两个提交；无新增生产 API、持久阶段、队列或业务保证，原 surface 线性查找成本未测。图2000 APIs，私有 revoke 返回合同迁移 commit/abort 全部 consumer。最终产品`1427f464d57e54e9a16245ef4dfd7163d47cdb06`、5414/0/0 与[14项检查](../evidence/br1_prepared_fact_residue_20261002/deletion-checks.json)见[证据](../evidence/br1_prepared_fact_residue_20261002/README.md)和[代码](CODE_INDEX.md#prepared-fact-residue-code-index)。完整CP1、默认启用和M6–M8仍未结算。

<a id="publication-input-storage-api-delivery"></a>
## 原 publication 工作输入与候选释放（92 §16.57）

| 旧对象 | 最终归属与同步删除 | 保留的 consumer / 删除条件 |
|---|---|---|
| publicationHeaders / publicationSnapshot | private paid version directory + 同shard cut current/target标量；旧函数及Reference唯一oracle consumer迁移删除 | 实际公开pageSnapshot/serializer/Qt oracle仍存在；不把directory当coherent epoch view |
| publicationTransitions / restoreTransitions、restore changedDefaults/seen/targeted及manifest中间副本 | 原Data的compact change/target数组；原immutable surfaces推导变化、排序唯一prefix二分查目录，metadata复用单一转换政策 | Qt Transition消费者覆盖oracle/generic/recoverable等不同语义，不能因production compact迁移而删掉 |
| proofDescriptors完整值复制、backingChanges生产Qt→paid复制 | 原immutable描述的paid shared_ptr数组保留批量门外验证；paid backing数组移动到Ledger原slot/cookie，native seam为private friend | Ledger Qt wrapper仍服务Reference、CPU与PhysicalClaim测试，生产caller仅用native；slot缓存实际收费直至替换/析构，不按clear虚报free |
| 局部metadata/epoch候选、discardPreparedCandidates及四处手动discard | 原Data从准备起保有两候选，原门外discardCommit覆盖全部拒绝/复验/安装后释放，后置move删除 | 不新增候选owner/状态/结果队列；真实metadata/root/descriptor/backing准备与revision拒绝继续 |
| 生产完整delta被再次当增量prepare | private epoch preparePublication消费完整owner-validated write set，与公开incremental prepare共享prepareImpl | 原epoch记录是唯一权威；完整集拒绝后可重试或继续写入。公开增量同generation拒绝保留 |

图API从2000到2005，净+5为内部准备签名与必要查询/输入类型的差集，UI/tool/paintop/painter/PaintDevice/scheduler生产新增0。生产7文件+336/-237净+99；其中实际收费、冷拒绝与完整write set接续是保证增量，不能计为纯去重收益。测试2文件+202/-9，生成2文件单列；产品`36189cb3b1bc91d77ea565894bb1fd51f9b6056a`、5534/0/0与[16项检查](../evidence/br1_publication_input_storage_20261002/deletion-checks.json)见[证据](../evidence/br1_publication_input_storage_20261002/README.md)、[代码](CODE_INDEX.md#publication-input-storage-code-index)和[92裁决](../92_br1_m6_m8_execution_baseline.md#publication-input-storage-delivery)。原epoch工作/core/root/control、Qt输入验证/注册/oracle、bootstrap/固定成本及完整永久尾出口仍归CP1，完整阶段及默认策略不变。

<a id="epoch-protocol-residue-api-delivery"></a>
## epoch 保护与不可变 restore 的旧政策回收（92 §16.58）

| 旧对象 | 原责任与删除 | 保留依据 |
|---|---|---|
| prepare/prepareCommit 的base丢失失败、capture缺root、默认空root查询 | Private::protectedRoot统一同锁下已准入root查找；旧业务恢复出口删除，公共准入仍先验证身份 | 原active交易/retention计数与collector同gate；未保护/非法/foreign/stale身份仍拒绝 |
| release缺count静默成功、登记完成前发布事实 | 直接消耗原正计数；initialize先插入root，transaction/retention先准备count并在异常时撤销空槽 | 原Qt登记分配仍可失败，异常安全修补不授予收费或硬满资格 |
| restore逐字段内容重建、重复QSet验证和validation假拒绝 | 继承已验证root，只更新检查后的发布身份 | 外部retained输入/metadata、active交易、exhaustion、晚复验/metadata拒绝保持 |

新增一个Private方法，无上层生产API/状态/队列净增。生产+51/-64净-13，测试+28/-1，生成单列；产品`9e0534018d9db0e1376272fb5889ae0d46deb639`及5534/0/0见[证据](../evidence/br1_epoch_protocol_residue_20261003/README.md)、[12项检查](../evidence/br1_epoch_protocol_residue_20261003/deletion-checks.json)和[代码](CODE_INDEX.md#epoch-protocol-residue-code-index)。epoch/core实际存储仍欠，完整CP1及正式阶段不变。

<a id="epoch-transaction-storage-api-delivery"></a>
## 原 epoch 写集与生产查询协议回收（92 §16.59）

| 旧对象 / 旧政策 | 最终归属与同步删除 | 保留 consumer / 真实拒绝 |
|---|---|---|
| record内Qt transaction snapshot及changeIndexes/surfaceChangeIndexes/removedPageSet | 原交易一个immutable delta，值/实际shared控制块和三数组使用retained allocator；辅助容器及旧record snapshot删除 | 公共isValid Qt输入验证与冷transaction oracle仍有实际consumer，嵌套format字节/Qt本体不宣称收费 |
| under-gate三字段扩容、complete相同事实仍重建/增加revision | 同锁捕获原base/delta/revision，门外构造后重新查record/复验；相同complete直接复用原值/revision | 真实control/array容量与晚revision拒绝保留原记录；public incremental仍要求generation推进，拒绝后仍由原prepare入口继续 |
| public incremental先remove后write接受、反向拒绝 | 合并后的唯一delta统一检查，两个相反顺序都原子拒绝 | private complete是整个write set替换，合法的remove↔write替换仍接受；此项是行为修复 |
| prepareCommit Qt snapshot复制及dense replacement/removal/current.manifest投影 | 同一个immutable delta被root准备共享，dense原收费vector按已排序事实merge | 原sparse AVL/dense阈值、metadata/root构造与晚current/revision拒绝仍存在，root树/surfaces/registry收费尚欠 |
| Store/Publication共7处transaction导出 | 私有activeTransaction仅返回原active identity，全部native consumer迁移 | 公开transaction保留冷Qt oracle导出；私有budget attachment只接原controller，standalone初始化才准备兼容controller |
| collection持gate析构paid delta | 原finished链摘record并移出同一delta，门外reset后回锁重新查下一record | 无新retirement队列/状态；controller退场后的实际tail由原retained accounting owner收费，完整tree/永久尾退出未结算 |

图API从2006到2011，私有查询/原数据方法及内部类型由真实consumer使用；上层生产API/持久阶段/队列新增0。生产+229/-130净+99，实际收费、原子保留/门外释放和政策修复不能算纯等价去重；测试+199/-0、生成单列。产品`1bc171aefe59b5931fead205155311292f3534ca`及5562/0/0见[证据](../evidence/br1_epoch_transaction_storage_20261003/README.md)、[15项检查](../evidence/br1_epoch_transaction_storage_20261003/deletion-checks.json)和[代码](CODE_INDEX.md#epoch-transaction-storage-code-index)。root/core/control/Qt registry及tree/deferred仍归CP1，正式M6–M8与默认关闭不变。

<a id="epoch-root-storage-api-delivery"></a>
## 原 epoch root/core 与最后释放协议回收（92 §16.60）

| 旧对象 / 政策 | 最终原责任与同步删除 | 保留 consumer / 真实拒绝 |
|---|---|---|
| 出生即QShared Private、Qt三registry及两个count表 | private prepareInitialization/installInitialization冷准备paid core/control；三ordered actual node；两种counts归原root | 公共initialize及Store同一实现，门外窗口复验；standalone controller/facade/bootstrap仍欠 |
| 门内registry growth/Qt detach协议、cancel/release/collector门内实际free | prepareEpochNode门外实际准入，原身份/准入复验后无增长insert；extract同node门外free | 参数/foreign/exhaustion与晚保护/revision/token拒绝真实可达，容量拒绝保留原责任 |
| Qt root surfaces生产导出、重复root验证/validation失败与替换找不到base | paid surfaces值/control/数组；private surfaceCount/At服务restore；原验证输入和immutable root继承构造权威 | 公开Qt surfaces/snapshot/retention/oracle实际消费者、格式/metadata校验继续；surface变化才复制原付费数组 |
| TreeReleaseBatch/deque/TLS、最后引用释放时申请task、前台析构节点 | 同一原tree owner冷准备paid reusable task；intrusive原raw node与taskPin，最多128实际free/pass | 最后shared control与原Node实际free分别归费；raw引用不提供逻辑admission。全参与者永久尾退出未授予 |
| 冷configure局部准备成功后不可接续、source接受后首ticket拒绝时重新register | epoch候选准备前移到发布之前；default/metadata原事实复用；原Store用registry/source两个字段保留不可重复receipt | 外部Registry source/ticket实际预算仍可拒绝；同入口续allocatePending、foreign registry拒绝。源accepted记录保留到原Registry寿命，完整bootstrap/close未结算 |

图2011→2019 API，增长为实际存储/冷安装/原surfaces遍历及内部释放机制，不新增上层生产API/业务stage/恢复队列。源接受不可通过局部顺序变成Registry原子事务；本批选择两个原receipt事实，扩大Registry为source+ticket bundle不属本责任的必要API。复用原Tree owner/task与allocator避免每次析构另立失败协议，Qt估算额度也不能约束actual node/control容量。

生产+553/-356净+197，测试+328/-14，ownership合同和生成物单列；新增保证成本不能记作等价净简化。ordered lookup O(logH)、冷default核对O(S²)，正式性能未测。产品`e0fc83ab79a2d761bd61cdae64226a569330d3bb`及5594/0/0见[证据](../evidence/br1_epoch_root_storage_20261003/README.md)、[22项检查](../evidence/br1_epoch_root_storage_20261003/deletion-checks.json)和[代码](CODE_INDEX.md#epoch-root-storage-code-index)。原epoch root/core/registry/tree已交付，外部Qt/嵌套format、其余wrapper/bootstrap/固定成本和全部参与者永久拒绝最后handle仍归CP1，正式M6–M8与默认关闭不变。

<a id="residency-protocol-cleanup-api-delivery"></a>
## 驻留协议残余清理（92 §16.61）

| 旧假设 / 分支 | 最终原责任 / 删除 | 实际保留 |
|---|---|---|
| Transition创建后局部guard仍取消serial | 原Transition接受后独占取消，立即dismiss局部guard | 接受前Qt创建失败仍由guard负责 |
| physical commit的payload/serial/revision异常直接return | untrack等待原serial，物理移动后不能拒绝原提交；内部违例终止 | source/registration/reader/active transition在物理移动前的拒绝 |
| releaseReference丢失原slot/count返回false | live allocation唯一持有准确引用，删除非最后释放假结果 | 正常多alias的非最后引用仍返回false |
| 只以数值revision复验登记身份 | 原准备Qt数组保留存储，constData核对同一身份 | 未来登记表收费替换须保留此ABA保证 |
| alias直接完成但allocate/retire保留结果时completion拒绝 | 起点已经统一completePrepared，本批静态核对并回归保持 | source/ticket冷准备及retire前真实忙拒绝，不重复计作本批删除 |

无新类型/状态/容器/接口。主干仅TileDataStore.cc+3/-0，新增字段/include/friend/锁/TLS为0；provider内部新增exception include。生产+14/-10净+4包含ABA保证及必要说明，测试+44/-0、ownership+3/-2、生成物单列。收费候选扩大本次清理责任且未通过原24 MiB场景，已撤回；Qt登记/observer/Transition真实consumer及收费欠项继续原CP1。产品`69a01e929abce246bfeed0603dbf0825088e28a1`、5614/0/0及17项检查见[证据](../evidence/br1_residency_protocol_cleanup_20261003/README.md)、[代码及MI账本](CODE_INDEX.md#residency-protocol-cleanup-code-index)和[92](../92_br1_m6_m8_execution_baseline.md#residency-protocol-cleanup-delivery)。

<a id="cp0-matched-baseline-api-delivery"></a>
## CP0 基线与原 memento 消费合同补齐（92 §16.62）

| 旧假设 / 对象 | 最终责任 / 同批删除 | 实际边界 |
|---|---|---|
| PageStore memento不填extent，undo像素正确即表示projection正确 | 原commitHistory从canonical完整delta填入原memento，原TransactionData读取extent并setDirty；无需另建显示终结协议 | 低层setExtent(QRect)一个consumer，上层API新增0；真实Qt准备/commit拒绝和收费继续CP1 |
| FreehandStrokeBenchmark无普通update却可代表显示/drain | 独立双方同字节真实job/update夹具，分开setup、stroke、pen-up、undo/redo及owner teardown | benchmark原API仍有用户，不删除；新入口只有projection-ready、普通strategy；不授予canvas/M/K/E或正式非劣 |
| 原testui全字体启动作为该无外部资源auto brush的前置 | 双方相同lazy原plugin registry、匹配五插件；临时旧slot、调试图片输出和destroyed探针删除 | 全字体启动失败保留；最后image引用由原weak失效判断，不增加生产测试flag |

生产+25/-1是语义缺口修复，不能记作封装净删；低层setter真实消费者和原四字段形成同一handoff。原Qt delta查询在普通history终结增加，仍需CP1收费/拒绝与CP10成本验证。双架构目标4210/0/0、12对/架同像素，仅资格于[冻结源码/运行物](../evidence/br1_cp0_matched_baseline_20261003/README.md)；完整manager25失败及两个UE尝试保留，正式M6/M7/M8、全局allocator、TSAN、公平、continuation及性能不结算。

<a id="execution-preparation-reuse-api-delivery"></a>
## 已接受准备事实的复用（92 §16.63）

| 旧假设/路径 | 原责任及替换 | 必须保留 |
|---|---|---|
| 每次preflight重新pin已有pending | linked BoundEntry/原Page已持有backing reservation，删除暖页prepare guard/pin/materialize | 冷准备保证及实际callback重pin/swap-in；原真实pin拒绝不改成不变量 |
| 负坐标新容量都留在右侧 | 原Data::Growth在扩展侧保留slack，消除小范围指数增长 | 原两轴原子准备、并发复验及真实容量拒绝 |
| callback页数等于全部准备工作 | 原统计继续计cold pin和未写generation，consumer分别验证取消/不seal | 不为了旧期望跳过冷前置、减少声明目标或隐藏工作量 |

无新增public/protected/private方法、类型、字段、状态、锁/TLS或队列。生产+14/-4包含extent缺口修复及真实热路径工作减少，不报等价净删；主干只改原ExtentManager增长政策。当前6304/0/0、源/库身份及剩余实际失败见[证据](../evidence/br1_execution_preflight_20261003/README.md)、[代码](CODE_INDEX.md#execution-preparation-reuse-code-index)和[92](../92_br1_m6_m8_execution_baseline.md#execution-preparation-reuse-delivery)，未授予全部收费/退出、M6–M8或正式性能资格。

<a id="resident-binding-storage-api-delivery"></a>
## 原 binding 实际收费与共享表示迁移（92 §16.64）

| 旧路径/表示 | 原责任及替换 | 保留依据 |
|---|---|---|
| adopt阶段Qt构造binding，实际对象/control未收费 | prepareAdoption在原allocation node中先allocate_shared，adopt只接原tile引用；同observer retained allocator覆盖实际控制块 | 放在原adopt后收费会把拒绝移到像素初始化后；附加估算额度不能限制Qt实际控制容量 |
| QShared binding及Qt cast | 现有cpuResidentBinding低层返回/参数、原guard/reservation/handoff/link/cache全部std共享同一记录，生产provider和三个实际派生/测试override同步迁移 | 现有C++消费者需共同重建，不宣称旧二进制ABI兼容；没有Qt↔std桥接控制块或第二权威 |
| 退休/退出即认为存储全归还 | 原强引用终结对象，弱控制块继续保有实际allocation及原accounting owner；最后free才归费 | provider/controller后晚pin仍可读原字节，新pin拒绝；不增加最后释放容量申请或terminal阶段 |

生产+53/-43为实际收费与准备顺序保证增量，不计等价净删。上层public/protected API、持久字段/状态/队列新增0；TU内新增adoptTile一个真实consumer，现有低层seam表示改变但没有新增外部方法。真实身份、pin/readiness、物理引用与terminal completion拒绝政策保持。原retirement已清除read cache，不增加重复GC；33代测试验证该旧消费者在新收费后继续正确。完整结果、压力反例和其余wrapper/bootstrap差集见[证据](../evidence/br1_resident_binding_storage_20261003/README.md)、[代码](CODE_INDEX.md#resident-binding-storage-code-index)及[92](../92_br1_m6_m8_execution_baseline.md#resident-binding-storage-delivery)。

<a id="checkpoint-pressure-api-delivery"></a>
## 原 detachment 候选存储（92 §16.65）

原prepareMutation/preparePublication/prepareRecoverableWrite、install及DeferredPublicationCleanup接口保持；仅同Data的共同Entry与可选Publication载荷分离，prepare/install/clearBatch全部consumer同步迁移。旧detachedVersion与Entry发布载荷访问删除，原kind/claim/cancel/slot预约及最后收费owner保持。TU内新增一个Publication类型/数组，由三处实际消费者维护配对；无新上层生产API或持久阶段。

真实共享父硬满后的安装/取消与精确释放通过，普通publication实际增加40字节头部/一次数组分配，生产净+7不算复杂度净删。真实surface/8MiB准入拒绝仍保留原Failed/cancel，不能凭候选缩小删除这些业务出口。详见[证据](../evidence/br1_checkpoint_pressure_20261003/README.md)、[代码](CODE_INDEX.md#checkpoint-pressure-code-index)与[92](../92_br1_m6_m8_execution_baseline.md#checkpoint-preparation-pressure-delivery)。

<a id="metadata-directory-storage-api-delivery"></a>
## 原 metadata 配置目录/control（92 §16.66）

原configure/prepare/install/cleanup公共入口保持。私有arena constructor增加原allocator输入，由三个真实typed arena消费；默认无预算形式继续供原bootstrap测试。原shard/control、目录数组和identity不再同时维护估算fee与实际分配，删除directoryBytesForLimit/allocatedDirectoryBytes/maximumDirectoryBytes、directoryCharge及分配后超预留分支。配置拒绝只销毁原局部候选，同owner可以重试；publication identity仍唯一，prepare/install先acquire原operational再读，foreign安装仍消费原候选。

生产净-50来自原估算/提交/释放协议退出，实际收费保证增加retained allocator成员成本；没有上层API、业务阶段或锁/队列增量。原footprint诊断去掉两指针控制估算，原backing usage承担实际费；block/hash费用继续，eager最大目录由下一节删除。真实少一字节/晚引用验证和该轮surface压力失败见[证据](../evidence/br1_metadata_directory_storage_20261003/README.md)、[源码](CODE_INDEX.md#metadata-directory-storage-code-index)与[92](../92_br1_m6_m8_execution_baseline.md#metadata-directory-storage-delivery)，不删仍可达的surface准备/Failed或bootstrap边界。

<a id="metadata-directory-growth-api-delivery"></a>
## 原 metadata 目录按需增长与原失败归属（92 §16.67）

| 旧实现 | 最终归属与同批删除 | 真实consumer/保留依据 |
|---|---|---|
| arena constructor最大directory reserve | 原MetadataArenaGrowth先门外准备同allocator目录，门内安装；空arena零目录分配，eager预留删除 | 三种typed arena和原generic/publication增长；flat lookup、slot/block generation及hardceil保持 |
| fullMetadataArenaGrowthPlan独立规划 | 原metadataArenaGrowthPlan接受fullDemand局部模式，共同计算block需求及目录几何 | publication仍在候选交付前保证完整batch容量；generic按当前free slots准备，没有第二规划政策 |
| attach允许隐式vector增长 | attach只能消费已准备容量，NeedsMore经原growMetadataArenasOutsideLock/revalidate | 原Locker、claim/slot/index预约、Exhausted/Stale和候选清理继续；真实存储拒绝不能改成成功/断言 |
| 固定最大目录只随arena整体释放 | 按需目录替换时，三个原growth carrier保有退下数组，门外free；不足候选重准备先释放 | 原Data取消/安装后的cleanup保活shard/parent，实际allocator费用不提前返还；不新增尾回收阶段 |

新增私有PreparedDirectory的构造/移动/prepare只由原growth和直接arena夹具消费，directoryCapacityForBlocks/installPreparedDirectory由原规划/attach消费；上层公共接口不变。图的API总数2017→2025，本批新增接口局限私有实现，不等同新增八个上层业务API。生产净+88、三carrier共120B、局部plan+24B及线性搬移/新旧数组峰值为保证成本，不能记纯去重。block/hash原手工fee、surface真实准备/Failed、身份/参数拒绝和bootstrap仍有真实来源；目录保证不授权删除它们。完整实际验证与未结压力条件见[证据](../evidence/br1_metadata_directory_growth_20261003/README.md)、[代码](CODE_INDEX.md#metadata-directory-growth-code-index)及[92](../92_br1_m6_m8_execution_baseline.md#metadata-directory-growth-delivery)。

<a id="metadata-authority-storage-api-delivery"></a>
## 原 metadata authority 配置收费（92 §16.68）

| 旧实现 | 原责任及替代/删除 | 保留依据 |
|---|---|---|
| Private构造make_shared未收费authority，attach重置budget/owner | 原configurationMutex只保存配置前预算选择，configure以同retained allocator准备authority/control及原全部候选后发布；旧构造/authority::attach删除 | standalone和Store预算选择仍按原公共入口；不能在预算冻结前增加live费或放宽controller挂接合同 |
| 首次reserve补建accounting owner并catch拒绝 | 完整配置候选保证authority发布前已有原owner；后置补建及该拒绝分支删除 | 实际reservation/slot准备及detach后的budget不可用仍可能拒绝；不将reserve整体改为无失败 |
| read/captured cleanup在shard acquire前读d->authority | 原shardFor先acquire配置发布，再核对同shard authority；旧提前比较删除 | foreign cleanup拒绝保持，未配置入口返回拒绝；没有新增锁或第二可见性权威 |
| 退出即认为authority已无实际费用 | 原shard/Data/read cleanup最后持有同一收费authority/control；最后free再归原parent | 只剩detached read cleanup的controller后硬满clear/析构已验证；不新增回收阶段 |

上层公共API不变，原Private多一个8B预算选择指针，没有新增业务事实/类型/锁/TLS/队列。生产净-12伴随实际收费保证：1/4/64 shard均新增原authority/control64B请求，不能记内存净删。Private本体/standalone controller及其余bootstrap仍有真实依赖，表中的authority有限收口不关闭它们；见[源码](CODE_INDEX.md#metadata-authority-storage-code-index)、[证据](../evidence/br1_metadata_authority_storage_20261003/README.md)和[92裁决](../92_br1_m6_m8_execution_baseline.md#metadata-authority-storage-delivery)。

<a id="metadata-core-storage-api-delivery"></a>
## 原 metadata Private 配置准入（92 §16.69）

| 旧实现 | 最终归属与同批删除 | 原consumer与保留依据 |
|---|---|---|
| constructor未收费new Private和总是内嵌standalone controller | constructor只建原配置壳；configure通过原retained allocator准备实际Private；attached生产不创建standalone | Store保持原shared/limits/configure顺序；未attach的公开reference入口仍需真正standalone，controller本体收费资格仍欠 |
| Private::operational独立发布目录可见性 | 完整core指针release/acquire作为唯一配置事实，全部shard/prepare/install/query/诊断消费者迁移，旧标志删除 | 已配置不可重配和析构静止合同保持；没有新的业务阶段、锁、队列或TLS |
| 配置失败只清局部数组，eager Private始终保留 | 原完整Private候选承担全部付费配置存储；拒绝与最终析构用同一Private::destroy按实际free归费 | 私有constructor/destroy有真实configure及析构consumer；晚Data/read cleanup独立保有原shard/authority，无新增尾owner |
| 冷配置事实保存在堆中Private | 原预算选择、配置锁和Debt接收指针移到facade，发布前设置、发布后不修改 | facade尺寸8→56B，含它的Store根对象费用仍待闭合，未新增第二份事实 |

上层公共API新增0；图2023→2025 APIs是私有构造/销毁，callback registrations 21→22含原候选deleter地址。生产净+34是实际Private收费、完整候选清理及未配置空core消费者迁移成本，不记纯去重。双架Private104B请求收费与生产对象尺寸减少1,336B分列；共享control仍按实际请求，raw core不增加控制块或延长owner寿命。表中结构收口不授完整CP1/全局TSAN/永久出口/性能资格，见[代码](CODE_INDEX.md#metadata-core-storage-code-index)、[证据](../evidence/br1_metadata_core_storage_20261003/README.md)及[92](../92_br1_m6_m8_execution_baseline.md#metadata-core-storage-delivery)。

<a id="store-root-storage-api-delivery"></a>
## 生产 Store 根存储冷准入（92 §16.70）

| 旧入口/协议 | 最终归属与同批删除 | consumer及暂留条件 |
|---|---|---|
| backend new KisPageStore、Store new Private | 原prepareStore调用私有prepareStorage；同retained allocator实际准入facade/Private，旧new删除 | configure及configureClone共用唯一组合入口；private allocator constructor实际构造原Private |
| 同步与terminal lambda各自delete owner | 原Private::destroy保存allocator直至实际free，两处旧delete删除 | 原PrivateReleaser和原terminal task共用，captured/mutation最后引用仍走原lifetime |
| 默认unique_ptr facade delete | 原StoragePointer保存同destroyStorage地址，facade实际析构/free独立归费 | factory与backend handle是两个真实deleter登记，原Private可以晚于facade退出，无新增尾owner |
| 直接向内部controller收费或后置补费方案 | 冷栈child复用原共享登记/accounting；返回前controller退出，原accounting持父到最后free | 原内部shared/limits冻结保持；此allocator只供free，禁止在退出controller上新准入；默认reference及其他根/嵌套control仍待迁移 |

图2025→2029 APIs净增4：Store allocator constructor、prepareStorage、destroyStorage、Private::destroy新增，Private constructor改签名一增一删。上层API新增0；callback 22→24为同facade deleter两个地址登记。生产净+59和Private16B、backend deleter8B、原accounting/child120B是新增收费保证成本；实际冷fee4,520B与facade ABI8B分列，不算等价去重。冷真实拒绝/重试与cold/late captured父硬满实际free通过，但完整CP1/永久出口/全局TSAN/性能门仍开放。见[代码](CODE_INDEX.md#store-root-storage-code-index)、[证据](../evidence/br1_store_root_storage_20261003/README.md)及[92](../92_br1_m6_m8_execution_baseline.md#store-root-storage-delivery)。

<a id="ledger-control-storage-api-delivery"></a>
## 原 Ledger／domain 控制存储（92 §16.71）

| 旧入口/协议 | 最终归属与同批删除 | consumer及暂留条件 |
|---|---|---|
| Ledger new Private与Qt create admission | 私有allocator constructor从原Store冷allocator准备实际Private及allocate_shared admission/control，旧创建删除 | Store::Private和原default委托；cleanup保存allocator至实际free；默认null allocator仍是未qualified兼容入口 |
| admission的Qt sharedFromThis、provider QWeak与transition QShared receipt | 原std strong/weak和allocator-backed control；相关provider签名/override/数组/准备返回同批替换，旧类型删除 | provider weak、真实transition、两测试override均已迁移；原锁序、identity/Busy、singleOwner保守政策及detach保持 |
| 无record时new no-op Reservation及可分配拒绝 | 原admission实现已有receipt接口，共享同控制返回，原独立创建删除 | 原transition commit后清空同vector；原强authority寿命保留，无操作不作新的预算准入 |
| 有record时未收费Qt Reservation/control | 同原预算retained allocator准备inactive std receipt/control，原ClaimMap发布仍最后进行 | 真实资源拒绝仍由原prepare/catch回滚，不能在此删除；cancel/commit及晚weak存储沿原accounting释放 |

上层新增API/业务队列/阶段0；索引2029→2033净增4为私有Ledger/Private构造、cleanup与原receipt接口的无操作commit实现，四个原签名一增一删。callback24保持。生产净+30兑现实际收费及弱尾归费；冷根新增584B、Private allocator16B和receipt接口8B单列，不称纯去重或性能收益。没有新分配的无操作分支在父满额下完成；真实claim仍先准备424B候选，72B receipt/control可晚于controller存在，实际弱尾free通过。完整CP1/TSAN/永久出口/性能门仍开放，见[代码](CODE_INDEX.md#ledger-control-storage-code-index)、[证据](../evidence/br1_ledger_control_storage_20261003/README.md)及[92](../92_br1_m6_m8_execution_baseline.md#ledger-control-storage-delivery)。

<a id="cp1-concentrated-storage-api-delivery"></a>
## CP1 集中实际容量与同owner失败／退出（92 §16.72）

| 旧入口／协议 | 最终责任及同步删除 | 实际consumer与保证成本 |
|---|---|---|
| Qt共享根/control、null allocator无费bootstrap | 冷实际allocator与同一有界process parent；std strong/weak签名/override/cast/持有全部迁移，弱尾到实际free | Registry/provider/observer/Transition/source、Store/history/backend及controller；不重挂live对象到第二parent。 |
| oracle/嵌套format Qt拥有数组与重复验证集合 | KisPageSnapshotArray/KisPageByteArray共享真实paid COW vector/control；扫描原输入，旧生产投影/集合删除 | StateMachine/Epoch/capture/Transition与checkpoint值；公开borrow/export边界保留，COW detach可拒绝并返回原值。 |
| MetadataOwnedHash/Capacity及每slot估算 | actual MetadataMap rebind请求、actual vector容量与原authority/accounting | page/activity/link/index prepare/install/clear；真实节点收费，不以估算重贴费用。 |
| pop Entry后独立取消、shared cleanup job | Entry.releaseActivity用于cancel/clear；原publication Data实现ReclamationJob，原statistics收费 | 实际修复136B活动泄漏；Data/Entry最后owner不增加失败阶段/队列。 |
| observer接受后分配登记 | 原adoption前置prepare两登记节点，原intrusive记录transfer | TileDataStore真实caller；实际node/PMR收费和保活，不向stroke暴露预算业务。 |
| QHash/order重复缓存、匿名lease集合、clear复制两列表 | paid list/set/map原记录和匿名lease intrusive链；memento复用原active map node | default/cache/history/backend原scope；输出容量先准备，事务接受后拒绝由同scope abort。 |
| extent eager空数组/Qt行列投影 | generic PMR两轴准备、原输入minmax扫描、原buffer持有resource | DataManager内部冷绑定；公开extent只有通用memory_resource，与预算类隔离。 |
| close shutdown handles数组、seenReplicas及QStringList拼接 | private takeShutdownRetirementRecords转交原terminal节点；原pending/统计/常量原因 | Store close独占Ledger记录一次；永久拒绝保留相同record，不重放provider动作。 |
| 三次竞争后拒绝原mutation | 同Growth原数组capture/build，原请求每轮复验；旧人为次数失败删除 | claim/activity原准入consumer，六次revision变化硬满无新分配后安装；永久热点有界进度仍归完整压力资格。 |
| 空free同时退费用 | 同free helper先检测实际指针，physical free后原归费 | retained/raw两个owner路径统一；精确controller baseline断言保持。 |
| Qt pool/runnable及普通clock/线程分配 | 原intrusive executor、paid clock/control/statistics；Darwin原ReclamationThread显式stack/native region | 两native runner共一原queue，永久stop原端点join、晚handle最后free；其他平台native/global框架未qualified。 |

新私有value/storage/native helper都有上述真实consumer；std签名替换同步迁移兼容caller和disabled Vulkan声明，但未授Vulkan runtime资格。iterator上层只替换原opaque寿命类型；MI1–MI8仍要求预算/页业务留在PageStore/DataManager内，外部19文件集合未扩张，manager引用减少一处，backend_duplicate_state从两项收紧为零。API图2033→2158、callback24→25包含新实际分配/释放/COW和线程入口，不能称API数量减少。生产净+947、测试净+155、audit和生成物单列；具体尺寸、peak/重试成本及未验收边界见[证据](../evidence/br1_cp1_concentrated_20261003/README.md)。没有新增持久业务失败阶段或平行业务队列；新的thread starter同步原mutex/condition只保证已收费native资源在callback前发布，不替代业务状态权威。完整CP1/M6–M8/TSAN/正式性能仍未结算。

<a id="cp1-qualification-api-delivery"></a>
## CP1 实际分配拒绝与锁内终结责任（92 §16.73）

| 原接口/责任 | 最终替代 | 净增/删除 |
|---|---|---|
| execution prepareWrites／原history owner | 捕获准备`bad_alloc`后原finishPreparedWrites负责rollback，原Failed返回、同owner重试 | 删除冷分配异常逃逸造成的owner失效；不新增返回类型、持久状态或恢复入口 |
| metadata projected sequence／activity | 原installHeader成功时在gate内结束activity回滚；原guard只在未安装路径执行 | 成功路径解锁后的map访问删除，无新guard或锁 |
| retirement prepare callback／shard统计 | callback仍在gate外，返回后先恢复原gate，成功和拒绝共享此顺序 | 删除解锁的rejectedTransitions写入；原prepare/commit/cancel签名和接受语义不变 |
| 原Freehand 8MiB取消方法 | 原数据行扩展至queued/admitted-visible两行，复用tester取消及原memento/producer/checkpoint | 测试增加data方法，生产API/consumer无改动 |

audit-only malloc工具/同源runner均保存在证据目录，不作为生产恢复协议。生产+43/-29、测试+97/-2，图API2158和callback25保持，上层生产/API、业务类型、锁/TLS/队列净增0。实际保证改动不能称纯去重；完整CP1资格及外部平台/总硬界/static/TSAN/旧UE差集见[证据](../evidence/br1_cp1_qualification_20261003/README.md)与[92](../92_br1_m6_m8_execution_baseline.md#cp1-qualification-attempt)。

<a id="cp1-reconciliation-api-delivery"></a>
## CP1 原seal活动与已接受捕获输出（92 §16.74）

原seal三段手工活动计数改为一次scope guard，正常拒绝/异常共享恢复gate及归还；已安装overlay后只读输出拒绝不取消原session，原checkpoint入口恢复不重放。关闭diagnostic的TLS隐性分配改成一个4B fixed presence counter和一次relaxed读取，disabled对象无需查TLS；旧“无atomic”注释按实际成本修正。生产上层API、业务owner/阶段、队列净增0，私有registered字段服务disabled实例生命周期。新的保证增量+29/-13与测试+49/-0单列。

当前图2158APIs/25callbacks，ratchet保持；真实总heap、已辨认static最后free及487拒绝目标的122失败均绑定[同源证据](../evidence/br1_cp1_reconciliation_20261003/README.md)。owned QWaitCondition私有块仍漏费，不能归到caller Qt例外；完整CP1未通过。

<a id="cp1-wait-storage-api-delivery"></a>
## CP1 原等待存储与caller迁移（92 §16.75）

九类原owner的QWaitCondition成员及其120B私有heap删除，原wait/wake调用使用内嵌[KisPageWaitCondition](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWaitCondition_p.h)。原WriteAdmission构造和借用指针由Qt条件改成同一私有条件类型，五处测试caller迁移；无公共生产API增量。新增wait/wake两个私有图入口服务原owner通知窗口，无新业务阶段/恢复队列；原gate、谓词与close/drain沿原消费者完成。生产+74/-22、测试+14/-7，原body sizeof承担费用，最后引用析构承担free。

图2160APIs/25callbacks、原ratchet保持；[当前证据](../evidence/br1_cp1_wait_storage_20261003/README.md)关闭列明owned等待漏费及read fixture竞态。原seal/commit的122实际拒绝失败仍须利用原metadata/proof/history接受事实接续；完整CP1未通过。

<a id="cp1-commit-retention-api-delivery"></a>
## CP1 原候选retention与删除（92 §16.76）

私有`prepareCommit`按原sink要求准备registry node和snapshot；`installCommit`及`KisPreparedMutationCommit::tryInstall`转移已付费输出，普通commit/restore caller沿默认无retention要求。新增`describeRetainedRoot`由原独立retention和候选共用，无公共生产API增量。候选新增存储字段，收费与取消/最后free沿原allocator；原lock/revalidate/metadata callback保持，无新owner/队列/业务阶段。

删除`commitLocked`接受后`retainSnapshot`、memento after-root失败返回、`orphanedAfter`及其释放分支，原history capability在preparation拒绝后保留。生产+73/-42净+31是保证增量；图2161APIs/25callbacks、原ratchet保持。真实六故障关闭；108 seal取消/8重放及完整CP1仍欠。[当前证据](../evidence/br1_cp1_commit_retention_20261003/README.md)。

<a id="cp1-seal-retry-api-delivery"></a>
## CP1 原seal接受事实与失败责任（92 §16.77）

原metadata transition/candidate、Ledger seal及overlay prepare沿原结果传storage拒绝分类，替代resource拒绝时cancel原scope；不解析QString，也不增加上层API。原session state增加Sealing值，保持claim和输入冻结，`isActive`表示可retry/cancel寿命。private publish从原metadata接受事实接续，proof复用原Ledger记录；overlay借用至install接受，删除提前清空及cancel撤销，generic lease caller同批迁移。checkpoint接受恢复Active，语义失败仍cancel本segment。

生产+114/-58净+56为frozen/retry保证成本，无新owner/队列/锁；图2162APIs/25callbacks、原ratchet保持，新增`wasStorageRefused`由原overlay prepare消费。原116失败关闭，487生命周期实拒及首次父增长实际通过；完整alias/provider拒绝、联合无输入清理和整包CP1仍欠。[当前证据](../evidence/br1_cp1_seal_retry_20261003/README.md)。

<a id="cp1-orphan-progress-api-delivery"></a>
## CP1 原 scope 取消与既有 collector 接续（92 §16.78）

原`retryOrphans → cancelLocked`仍唯一执行scope终结，所有显式abort/close caller保留同一流程。`retainOrphanLocked`调用既有`historyCollector.scheduleLocked`；collector新增两内部composition callbacks，分别在owner gate查询原链、在锁外推进原取消，替换schedule对原orphan工作的遗漏，不复制取消政策或节点。真实consumer是Store的原scope链；不持有scope副本，job的原owner pin覆盖锁外窗口。两个指针16B纳入原Private实际收费，无新task/timer/队列/业务阶段或上层API。

后台只在operational、允许background、未close/stop时接续；关闭仍冻结现有调度，最后facade退出沿原stop规则。16新增行关闭本scope两类实际拒绝解除后的无输入清理，caller transaction自动终结与全部晚引用恢复未验。生产+46/-7是保证增量；图2164APIs/27callbacks、原ratchet保持。普通Matched claim/像素失败在父/候选均复现，须继续原adapter准入及失败交接；完整CP1保持开放。[当前证据](../evidence/br1_cp1_orphan_progress_20261003/README.md)。

<a id="cp1-legacy-admission-api-delivery"></a>
## CP1 原clear准入、adapter安装与实际增长竞争（92 §16.79）

`fillRect`内部signature接收原OperationDelivery/prepareAdapter/completeAdapter，原DataManager clear迁移；测试/其他caller默认无delivery仍沿同一batch终结。原batch在像素前adopt完整range，delivery在adapter install后才释放claim。`PreparedTileUpdates::install`共同承接clear/packed/cursor，删除三处重复诊断/安装/解锁；clear presence沿原完整claim解析，无第二选择权威。`claimAll`原bool替换为临时Acquired/Contended/Failed，原唯一生产consumer reserveManagedRange及十个reference断言同步迁移；实际growth竞争复验/等待，不把allocator失败包装成竞争。没有新持久字段、queue/task/owner或上层生产API。

生产+105/-59净+46是完整范围及真实竞争恢复保证增量，实际targets/candidates均沿原allocator/last free。双架8236/0/0、真实增长body各一次、702 clear实拒、原压力72/0/0；中间失败保留。图2164APIs/27callbacks、ratchet不放宽。原void enqueue仍不能拒绝stop后的晚job，现已证实晚close死等；这项原接受交接及TileSwapper新SEGV未修复，不宣称stop/最终尾责任闭合，完整CP1开放。[同源证据及八项结算](../evidence/br1_cp1_legacy_claim_20261003/README.md)。

<a id="cp1-terminal-convergence-api-delivery"></a>
## CP1 原enqueue接受与停止后的终结（92 §16.80）

private `kisEnqueuePageStoreReclamation`由void改bool：true才转交原node责任，false保留原owner。prepare/schedule冷入口以原bad_alloc传播拒绝；history/read/retirement/waiter全部生产caller撤回本次临时scheduled/pin/activity，Store/tree/Data最终owner完成拒绝后的free。删除停止后盲排、debug-only接受断言及ghost记账，没有新公开PageStore API、owner、queue、lock、callback或持久业务失败阶段。停止后的同步最终遍历是明确成本，正常worker仍沿原bounded pass。

新增TileData `tryRef`只由原map遍历消费，替换可复活零计数的普通ref；cold首个owner保留原ref。age及pooler配置用原body内atomic标量，无新存储包装。tree foreground统计新增8B，四个静态统计实际32B统一收费（补齐原24B），不能记纯去重收益。CPU abort测试改观察真实Debt释放，没有改变原硬预算或生产拒绝政策。所有源码成本、生成物、通过及失败单列于[本轮证据](../evidence/br1_cp1_terminal_convergence_20261003/README.md)，完整CP1资格保持开放。

<a id="cp1-owned-qualification-api-delivery"></a>
## CP1 原arena计费单位与依赖可观测性（92 §16.81）

原 `KisShardSlotArena::blockByteSize` 改实际allocation request；原capacity/attach/live/detached/release及Growth reservation共同迁移，删除名义BlockBytes在计费路径中的使用。slot几何/稳定地址和所有真实consumer保持，Reference统计断言同步调整；没有新增API、helper、owner、持久字段、锁/TLS/队列。生产+11/-9与测试+6/-2是计费保证修正，未改变对象尺寸，不记性能或等价去重收益。

独立固定表、pthread debug hook及匹配QtCore插桩都只用于审计，不构成新的生产准备/恢复协议。原provider/operation/lifecycle/线程入口body及失败策略保持，本轮只取得明确实际请求/拒绝/最后free和七组TSAN结果。原native区域合并重收费、全owned硬界、联合永久拒绝/晚fence、外部/nonDarwin、完整manager及十二UE退出仍开放，[完整边界与失败](../evidence/br1_cp1_owned_qualification_20261003/README.md)统一由92裁决。

<a id="cp1-native-span-api-delivery"></a>
## CP1 原native启动容量与唯一join归费（92 §16.82）

TU内原start增加非拥有alreadyPaid参数，唯一consumer为原monitor的ensureClockLocked；原worker仍默认首次准备，存储查询span供后继消费。扣除已付交集后才接受monitor，worker原收费保留至最后join；没有新准备/重试函数族、carrier、owner或上层API。两个区域字段共使executor+32B，沿原sizeof付费，是容量去重保证成本，不是等价净删。生产+26/-5、测试修改0，图/ratchet保持；所有实际证据及外部/完整退出欠项见[本轮结算](../evidence/br1_cp1_native_span_20261004/README.md)，完整CP1未通过。

<a id="cp1-orphan-terminal-api-delivery"></a>
## CP1 原scope终结及metadata单值/序列统一接受（92 §16.83）

原cancelLocked/retryOrphans扩展仅由原façade退出与拒绝后复验消费；原声明/guard/execution/provider责任保持，删除façade之后的orphan自保重挂，活façade的原重试继续。唯一新增façadeGone事实受原gate保护且填原padding，Private两架actual4960B保持；没有新owner/queue/lock/公共API。原单transition不再用临时SnapshotArray包装，原私有applyProjectedSequence改const pointer/count，单值与序列共用local校验和project/install/拒绝，未添另一份接受或失败政策。生产+51/-23净+28是最后owner保证成本，测试+120/-2及派生单列，不计纯去重/性能收益。[结算](../evidence/br1_cp1_orphan_terminal_20261004/README.md)保留全owned/其他联合fence/平台/完整manager与十三UE出口，完整CP1仍开放。

<a id="cp1-unclassified-storage-api-candidate"></a>
## CP1 调用内Prepared候选与容量规则待结（92 §16.86）

仅将原私有prepareWritePlanLocked的make_unique<Prepared>改为调用栈optional，原qScopeGuard在同一unlock/reset/relock边界释放原pin及metadata/accounting/descriptor；没有新API/owner/gate/队列，删除该堆分配和拒绝来源。Prepared416B、optional424B两架相同，原堆416B及栈上8B句柄改调用内值，不称总容量或性能收益。候选384父780，生产+3/-1、测试/派生0，主树0；双架各296次原请求消失，四原body5544/0/0、目标TSAN290/0/0 actual0。

以上是§16.86冻结时的隔离候选事实；后继§16.87已合入并生成主树清点。原观察96,463/96,471B属于780请求费反例，不再作为共同容量规则的当前待实现；完整独立总账仍欠。[原冻结证据](../evidence/br1_cp1_unclassified_owned_20261004/README.md)。

<a id="cp1-tile-lifetime-api-delivery"></a>
## CP1 TileData分配失败生命周期（92 §16.91）

生产公共/保护签名、字段、状态、队列和测试hook净增均0。`KisTileData::allocateData`仍返回原像素所有权，但native null统一抛出`std::bad_alloc`；Store的原四个nullable入口在reservation/源pin责任内把异常收回为`nullptr`。Pooler、Swapper和swap store继续使用原`tryGetTileData`、iterator、bool及计量合同，以作用域owner保证候选、pin、gate、chunk和临时像素在拒绝时回滚。`releaseInternalPools`不再复制并移动活backing，只清理可选clone/cache并释放完全空闲Boost block；含活chunk的block由最后原owner释放。产品1177fa5ecab8318fe044b071342eb0ab51654e27，五生产文件+198/−202、测试0；API迁移与新增均0。[同源故障矩阵、manager及保留边界](../evidence/br1_cp1_tile_lifetime_20261004/README.md)。

§16.91保留的低内存SIGSEGV经§16.92确认来自陈旧测试对象232B布局与当前288B动态库对象的ABI失配；当前布局双架原body各3/0/0。产品API、签名、字段和源码改动均0，该项不产生新的迁移或兼容接口。[ABI裁决](../evidence/br1_cp1_low_memory_20261004/README.md)。

§16.93对现有`kisFreePageStorage`签名和调用者保持零改动；双OS释放都失败时仍由原void deleter执行fail-fast，不新增错误返回、owner或泄漏表。双架实际路径已确认，默认macOS abort回收仍是宿主出口差集。[退出裁决](../evidence/br1_cp1_default_exit_20261004/README.md)。

<a id="cp1-qt-temporary-api-delivery"></a>
## CP1 失败原因传播及原付费格式值（92 §16.90）

beginWriteImpl/sealImpl公共签名与拒绝状态保持；删除错误原因外层动态前缀，原QString原因直接共享，空原因使用静态通用文本，原cancel/retire责任不变。configure删除QByteArray::number的中间对象，以栈上to_chars结果直接构造原KisPageByteArray；没有新增转换API或长期状态。生产+8/−3、测试0/0；调用者输出、异常/TLS和共享Qt外部存储仍有各自真实消费者，不因这三处删除获得总预算资格。[产品87a及原完整body对照](../evidence/br1_cp1_qt_temporaries_20261004/README.md)。

<a id="cp1-config-initialization-api-delivery"></a>
## CP1 KConfig测试模式前置（92 §16.89）

产品2e471d5efb生产接口及owner增删0，只有原manager fixture的initTestCase：在并发worker启动之前完成KConfig 6.7的全局测试模式转换。新增QTest slot是测试生命周期入口，有实际qExec消费者；没有生产helper、锁、cache、参数或退出guard。原完整压力body/预算保持，测试两文件+11/−0、派生单列。负例及控制来自同版本插桩依赖，不把当前完整manager Pending计为通过。[同源记录](../evidence/br1_cp1_config_tsan_20261004/README.md)。

<a id="cp1-physical-release-reset-api-delivery"></a>
## CP1 原free及语义默认值owner补漏（92 §16.88）

kisFreePageStorage签名及所有原consumer保持；Darwin VM分支删除munmap失败返回0导致owner丢地址的路径，同地址native deallocate成功后返回原capacity。无新失败队列、异步重试状态或owner，双native失败的fail-fast及宿主出口未获资格。Mutation::Private::Page::resetPixel直接复用原KisPageByteArray，删除stageSemantic对QByteArray的生产隐式复制；转换运算符仍有原测试/边界消费者，未扩大删除范围。beginWriteImpl和原析构共享同一付费值的引用寿命。

两次产品提交分别8f84cc8461和3c22a0226a，生产+12/−3及+1/−1、测试改动0、派生两JSON单列。无上层API、类型、gate或队列新增；实际保证成本及消失的172次请求不外推性能收益。原owner分类、完整CPU/TSAN、真实native故障及manager资格边界见[本批证据](../evidence/br1_cp1_physical_fault_20261004/README.md)。

<a id="cp1-actual-capacity-api-delivery"></a>
## CP1 原分配入口、retained fee与physical free统一（92 §16.87）

四个私有物理存储函数分别承担完整capacity计划、已预留后的物理分配、存活费查询、最后free；原process/Mutation allocator、owner、slot、arena、readiness、map/index和默认buffer共同消费，不建立第二收费权威。中间raw capacity函数删除，默认buffer共用同一分配入口；原ProcessStorageObject独立header政策及reservation allocation的无效bytes副本删除。retained owner按实际费记账，controller消失后原parent/child登记保持到真实free，原锁序及callback退出协议保持。

Darwin普通小对象复用native size class，小型超对齐对象在原分配内保存base/capacity，超过64KiB raw容量按页预付映射；对齐与free事实不创建外部表或owner。默认read byteSize保持逻辑span，新增内部allocationBytes仅供费用/cache/释放。调用内Prepared改optional并在原unlock/reset/relock边界清理。生产+270/−95、测试+360/−206和两派生文件分列；新增容量保证成本不计性能或全局内存收益。[最终身份、实际反例和四组出口](../evidence/br1_cp1_actual_capacity_20261004/README.md)。

<a id="cp1-static-root-extent-api-delivery"></a>
## CP1 固定费统一及原extent getter同步（92 §16.85）

原固定费初始值和释放下限共用ProcessStorageState::fixedStorageBytes；私有initializationGuardBytes仅推导当前Itanium ABI guard类型，MSVC分支不授运行资格。原tree-only常量被完整reclamation固定存储常量替代，原executor/Resource handle静态断言约束实际类型；capabilities公共值/签名保持，原静态返回值与guard删除。原两个process gate内嵌std::mutex，字段名/锁序/consumer保持，无新增lock/owner/queue/公共API。

原Data::isEmpty/min/max同既有extent读gate同步；已持gate的updateExtent迁移为直接读原字段，删除递归获取的可能。两个私有constexpr函数对应真实固定费消费者，生产+50/-15是补齐计费与竞态保证的成本；原命名存储实际220/292→332/332B、费用92→332B，不计净节省。原测试body没有新变体。actual0的范围、旧完整manager actual66和新Pending、四组CP1差集统一见[本轮证据](../evidence/br1_cp1_static_root_20261004/README.md)。

<a id="cp1-finite-default-api-delivery"></a>
## CP1 原API不变的有限容量与默认拒绝退出冻结资格（92 §16.84）

沿用产品61a0e28b全部签名、owner、接受和失败政策，生产/测试/派生改动0；审计main/qExec和观察器不进入生产API。原captured release/history rescan/epoch node extraction/close原caller复核没有建立新的allocator自保环，独立oracle不能借用Store gate序列化结论。两架原Freehand两个完整body14/0/0，以及1041 handled真实拒绝/52控制默认正常退出，见[当前证据](../evidence/br1_cp1_final_qualification_20261004/README.md)。这些有限资格不覆盖全owned/Qt/OS/TLS总硬界、其余联合fence/caller、非Darwin、完整manager实际终点与十三UE/宿主默认abort出口；不增加一组适配或恢复API来代替未获得的运行证据。
