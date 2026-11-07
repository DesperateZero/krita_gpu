# 03j：CPU 全生命周期唯一追踪矩阵

本表是[03h算法](03h_cpu_lifecycle_ideal_blueprint.md)与[03i代码索引](03i_cpu_lifecycle_edit_index.md)的**唯一实施状态账**；92保留阶段资格权威。起点 `704d96e81cf29d16191bc3db8785859d79775e27`，tree `4e7fc164db46c02b968fdd04400b9e4402e289d0`。本包已实施并有限验收，当前候选/结果见§2与§6，默认及阶段资格另判。03g已完成22子项不重新打开。

<a id="rules"></a>
## 1. 状态、依赖和防漂移规则

`待实施`表示有具体目标算法与静态差异，**不表示并发等价/净收益已证明**；`待证明`有候选算法但尚缺删除许可或净复杂度判断；`有据保留`记录实际consumer，不能算已优化；`待核验`是完整交付责任。实施后经过`已改待核验`再到`验证通过`，必须分别填D（代码与删除）、S（语义/资源）、Q（数量）、P（未插桩性能）。没有独立时间价格写“未定价”，不能填0。

每行不能删除来求全绿；目标修改先写“旧目标→新证据→新目标→受影响ID”，同步03h/03i再更新本表。一个产品hunk对应至少一个ID；新增类型/字段/helper必须给原owner、消费者、替代/删除对象与失败/free终点。旧证据冻结不改写。

实施依赖：LP01–03共享语义策略；LP04分组依赖其最小候选表达；LP05依赖LP03/04但同步/失败路径也要迁移；LP06/07可独立开发，却不能代替主项完成；LP08闭包、LP09/10条件项同包裁决。完整候选统一性能验收，不能每项各跑一套完整矩阵或不断加样到正值。

<a id="tracking-matrix"></a>
## 2. 28项实施与删除矩阵

候选`d182a34bd0196079bc40d2ab7d00b8e326e4a58a`/tree`e03a63d2a33324a55c72b7eb8ec097deab96b171`，image SHA256 `da4304d429134da577087e15004b4d98d93b7fc5c97a1bf6d8da4f4a615d66d1`。22项结构/语义验证通过、5项有据保留、1项整包审查完成；所有行的P为整包因果对照，未逐项独立定价。分母未注明时为4个机制过程的projection Stroke范围。完整保护投影删除不等于必要标量值消失；[实施调整/失败记录](../evidence/br1_cpu_lifecycle_implementation_20261009/PLAN.md)与[原始数量](../evidence/br1_cpu_lifecycle_implementation_20261009/quantity-summary.json)保留偏离。

| 子项 | 必须达到的理想目标 | 关键依赖/反例 | 状态 | D / S / Q / P |
|---|---|---|---|---|
| [LP01.1](03i_cpu_lifecycle_edit_index.md#lp01.1) | Fresh/Adopt guards一份共享策略，无第二状态机 | T1；reference独立固定断言 | 验证通过 | 原policy唯一 / T1双架 / 32 kind路由审计 / 整包未独立定价 |
| [LP01.2](03i_cpu_lifecycle_edit_index.md#lp01.2) | 合格Fresh无旧保护镜像/未变base重装 | LP01.1；T1/T2，实际target容量先接纳 | 验证通过 | 直接target+pin / T1/T2 / 旧整记录重装396→0的一部分 / 同上 |
| [LP01.3](03i_cpu_lifecycle_edit_index.md#lp01.3) | Adopt同义迁移，全部其它sequence显式路由 | LP01.1；T3，alias/generic拒绝不漏 | 验证通过 | Adopt及finite路由 / T1/T3 / generic/异步未误迁 / 同上 |
| [LP02.1](03i_cpu_lifecycle_edit_index.md#lp02.1) | 同步private发布仅改实际字段 | T2/T3，before pin/CancelPending/effects | 验证通过 | 实际target字段+base pin / T2/T3 / 无旧record重装 / 同上 |
| [LP02.2](03i_cpu_lifecycle_edit_index.md#lp02.2) | 重试与首次发布同锁接纳，caller重复snapshot=0 | LP02.1；T3，foreign Prepared拒绝 | 验证通过 | 重试同锁接纳 / T3 / 132额外snapshot→0 / 同上 |
| [LP03.1](03i_cpu_lifecycle_edit_index.md#lp03.1) | Commit直接构造实际delta，无完整保护镜像（必要标量仍在） | T4，全Prepared链和最新代际 | 验证通过 | policy直接发delta / T4/T5 / full投影0；必要薄事实仍在 / 同上 |
| [LP03.2](03i_cpu_lifecycle_edit_index.md#lp03.2) | default/restore同一最小表达 | LP03.1；T4/T5，真实addition保持 | 验证通过 | Default/Restore同policy / T4/T5 / 实际addition保留 / 同上 |
| [LP03.3](03i_cpu_lifecycle_edit_index.md#lp03.3) | recoverable/authority/detachment不误删 | 真实retag/epoch消费者；T5需新候选复验 | 有据保留 | retag/authority原消费者 / T5双架 / 匹配fixture未触发retag / 不授删量 |
| [LP04.1](03i_cpu_lifecycle_edit_index.md#lp04.1) | 原entries分组、相邻去重/组范围 | T6，任意输入/字节收费/小N | 验证通过 | 原entries排序/邻接去重 / 新33页反例+16/17 / 比较706–848→119–136，新增sort413–501 / 整包 |
| [LP04.2](03i_cpu_lifecycle_edit_index.md#lp04.2) | 必要prepare pass按有限run共锁 | LP04.1；T5/T6，每真实unlock仍复验 | 验证通过 | 原candidate事实/demand分组 / T5/T6 / facts132–152→126–148（重试量不同） / 整包 |
| [LP04.3](03i_cpu_lifecycle_edit_index.md#lp04.3) | 全批claim/安装/失败回滚共用分组 | LP04.1；T5/T6，无多分片同锁 | 验证通过 | 全claim后安装；前缀回滚 / 新晚组冲突+T5/T6 / install132–136→122–126 / 整包 |
| [LP04.4](03i_cpu_lifecycle_edit_index.md#lp04.4) | 纯统计成功链额外锁退出 | T6，部分失败计数守恒 | 验证通过 | 成功统计并入原锁 / T6；失败已成功policy前缀结算 / 独立统计锁248–292→0 / 整包 |
| [LP05.1](03i_cpu_lifecycle_edit_index.md#lp05.1) | payload门外析构，activity按run归还 | LP03/04；T7，空/同步/失败全部caller | 验证通过 | 原Data反向run归还 / T7 / 全阶段活动锁408–428→221–239 / 整包 |
| [LP05.2](03i_cpu_lifecycle_edit_index.md#lp05.2) | 最终pass一次idle结算，原公平界保持 | T7/T8，不删计时界/指标 | 验证通过 | 最终idle一次结算 / T7/T8 / 全阶段36–38→26；16/1ms界保留 / 整包 |
| [LP05.3](03i_cpu_lifecycle_edit_index.md#lp05.3) | 失败与最终free仍在原Data单终点 | T7/T8，queue拒绝、late owner | 验证通过 | 原Data/根/收费单终点 / T7/T8及结构门 / 失败/同步/队列拒绝保留 / 整包 |
| [LP06.1](03i_cpu_lifecycle_edit_index.md#lp06.1) | job通知仅idle→work | T8/T9，stop/worker内追加 | 验证通过 | idle→work通知 / T8/T9 / 全阶段177–192→39–44 / 整包 |
| [LP06.2](03i_cpu_lifecycle_edit_index.md#lp06.2) | job结尾与下一取头共锁 | T8/T9，finished可销毁/self-requeue | 验证通过 | 完成/下一取头共锁 / T8/T9 / J次取头锁→启动1；实际invoke保持 / 整包 |
| [LP06.3](03i_cpu_lifecycle_edit_index.md#lp06.3) | 身份atomic按worker寿命写 | T8/T9，所有实际consumer及退出清零 | 验证通过 | ID线程寿命写 / T8/T9 / 观测346–371→1；退出清零静态核验 / 整包 |
| [LP07.1](03i_cpu_lifecycle_edit_index.md#lp07.1) | delay仅最早deadline变化notify | T9，cancel已取走/重arm/stop | 验证通过 | 最早deadline变化通知 / 原generation/cancel/rearm反例 / 观测空cancel通知196–207→0 / 整包 |
| [LP07.2](03i_cpu_lifecycle_edit_index.md#lp07.2) | ready仅空→非空notify | T9，fairness/临时ref/reset | 验证通过 | ready空→非空通知 / retainedWake等T9 / 匹配fixture ready调用0 / 未独立定价 |
| [LP08.1](03i_cpu_lifecycle_edit_index.md#lp08.1) | 仅同一有效执行保证覆盖的重复wake退出 | 原finished消费证明、T10；真实retry可解除 | 验证通过 | jobScheduled由finished同锁接续 / T10双架 / 匹配fixture notifyLastUse调用0 / 未独立定价 |
| [LP08.2](03i_cpu_lifecycle_edit_index.md#lp08.2) | history/retirement/budget事件与进度完整 | 原repeat/root世代/inFlight/dispatchAgain；T10/T11 | 有据保留 | 原root世代/retry/inFlight/dispatchAgain / T10/T11双架 / 七类executor消费者审查 / 不授删量 |
| [LP08.3](03i_cpu_lifecycle_edit_index.md#lp08.3) | epoch节点同原链有界摘取 | child尾追加/128界限/实际free，T11 | 验证通过 | 原链≤remaining128摘取 / epoch/late-owner/stop原反例 / 全阶段取头锁225–275→68–84；free数随调度变 / 整包 |
| [LP08.4](03i_cpu_lifecycle_edit_index.md#lp08.4) | 剩余effect/取消转换有逐kind处理结论 | 原Debt先接纳、复验、拒绝；T1/T11 | 有据保留 | effects先Debt/复验/原子安装 / T1/T11；PLAN具体逐kind / 匹配fixture generic0，不外推其它序列 / 不授删量 |
| [LP08.5](03i_cpu_lifecycle_edit_index.md#lp08.5) | 原root寿命覆盖最后物理free | 原lifetime/terminal job；T8/T10/T11 | 有据保留 | 原root覆至task/capture物理free / T8/T10/T11双架 / late owner/容量终点复验 / 不授删量 |
| [LP09.1](03i_cpu_lifecycle_edit_index.md#lp09.1) | exact共享descriptor命中免全历史搜索 | 值相等、原map owner、实际命中/净存储；T3/T5 | 验证通过 | 精确base借原共享值 / 完整相等新反例+T3/T5 / 命中132；比较187–191→55–59 / 整包 |
| [LP10.1](03i_cpu_lifecycle_edit_index.md#lp10.1) | 稳定scope中只借真实同义选择 | source/current/G0/oldData失效者；T12 | 有据保留 | 真实current/G0/oldData/source cut / T12与PLAN失效者 / 132代际/96bound保持；不重领旧pin / 不授删量 |
| [LP10.2](03i_cpu_lifecycle_edit_index.md#lp10.2) | 12路径、28项及所有hunk/删除闭合 | 下两节与完整候选，不复用旧通过 | 审查完成 | 14文件/109 hunk/32 kind / 双架9370+结构门+八桶控制 / 12路径结算 / Stroke与全生命周期收益未证；资格未过 |

<a id="path-coverage"></a>
## 3. 12条入口与终结路径覆盖

这是LP10.2的核验展开，不是第二份子项状态。实施后每行填候选、实际到达分支、反例结果或具体保留理由；当前12路径均完成源码/原测试落点审查，实际同候选安全组见下表；不宣称匹配性能fixture逐一触发全部路径。

| 路径 | 关联责任 | 必须保持/补证 | 本候选结果/边界 |
|---|---|---|---|
| 独立cursor + packed操作 | LP01–07/09/10 | preparation拒绝首字节前、partial/完整覆盖、越界锁存、changed集、adapter交付前claims | 双架manager/painter及CpuMutation packed/cursor反例通过；matched正常投影19更新 |
| 持续history借用/跨worker/checkpoint | LP01–05/10 | 同原transaction/execution，未发布不外泄、真实cut、拒绝保留旧段 | 双架CpuMutation execution/history/checkpoint拒绝与H4控制通过 |
| fill/clear/alias Adopt | LP01/02/03/04/09 | semantic removal、default hidden RGB、partial preserve、真实中间reader | 双架alias/default/hidden RGB/preserve反例通过；Adopt路由审查 |
| legacy iterator/copy/batch | LP01/02/04/10 | 原token与tile锁序、不可借用过期wrapper，非同步路径不误路由 | 双架manager/copy/iterator安全组及Fresh控制通过；原token锁序保留 |
| generic/异步/recoverable | LP01.3/02/03.3/08 | provider Ready/Pending/Failed、CancelPending、retag真实前后图 | 双架Reference/CpuMutation provider/retag/CancelPending反例通过；full fallback保留 |
| initial/default登记与物化 | LP01/03/09 | 原pin窗口保护、不同default revision、部分登记拒绝 | 双架default/registration/capacity反例通过；initial/default无hint原路 |
| canonical成功/失败/恢复 | LP03–05 | 所有claim后首改，disjoint rebase、冲突无partial、Undo/Redo exact root | 新晚组冲突无partial；原disjoint/default/Undo/Redo反例通过 |
| metadata candidate同步/后台清理 | LP04–07 | 0/8/9/16/17/1024/1025单位、pending硬界、失败/空输出、实际free | 0/1/2/16/17/33及原同步/后台/容量反例通过；未新增1024/1025专门枚举 |
| read/last-use/capture late release | LP06/07/08.1/08.5 | release/ack区分，terminal晚到、metadata容量、close重开、facade后guard | 双架automaticLastUse/boundedBurst/close/lifetime/capacity原组通过 |
| history/retirement/budget压力接续 | LP06/07/08.2/08.4 | 根变更重扫、retire拒绝不丢Debt、无新输入恢复、provider gate不倒置 | 双架root变更/revisit/拒绝债务/压力原组通过；原接续政策保留 |
| epoch tree/最后owner/队列停止 | LP06/08.3/08.5 | 非递归child追加、128/pass、finished销毁task、停止后同步drain | 双架epoch/late owner/runtimeStopsAtCapacity等原组通过；原128界保留 |
| pixel/merge/capture及端到端负控制 | LP10 | 同19updates及937/19job、像素与历史语义、Stroke/Undo/Redo/Teardown全费用 | 三组240性能过程与640控制过程；每性能过程19updates；未重跑937/19 job census |

<a id="verification"></a>
## 4. 语义、资源与统一实验

下列是实际已有测试落点，新增反例在原测试类中扩展，不为每个helper写镜像实现测试。实际双架16组9370 passed/0 failed/0 skipped，含新增16/17边界、33页乱序/重复/晚组冲突和descriptor值不等反例；T9/T10/T11复用原有屏障、容量、晚owner及stop断言，没有为每个交错另造测试。

| 反例ID | 现有落点 | 必须新增或加强的断言 |
|---|---|---|
| T1 | Reference `indexedMutationTransitions`、`indexedMutationConcurrentProtection`、`indexedRecordSlotReuse` | 逐允许/拒绝序列完整oracle；有/无保护列表、history长度、slot复用；不同writer/key/operation和generation/pin溢出；相同拒绝后全部权威状态未变 |
| T2 | Reference `indexedMutationBaseLookup`、`recoverableWriteGuards`；CpuMutation `sealPreservesReaderChanges` | Fresh只增加target/需要的pin；before为virtual后物化；reader/last-use在增长解锁窗口改变，旧指针不得写回；Failed/Retiring target拒绝 |
| T3 | CpuMutation `failedSealKeepsEarlierSegment`、`sealStorageRefusalKeepsFrozenOwner`、`sealPreparationClaimsAndSibling` | 首次/重复Prepared发布、foreign target/transaction、部分seal拒绝后不重复消费writer；alias、generic、单步和CancelPending路由 |
| T4 | Reference `preparedPublicationMatchesFullReferenceTransitions`、`indexedPublicationTransitions`、`indexedPublicationIgnoresRetainedHistory` | Commit/Replace/Restore逐字段与原值模型比对；较早/更晚同事务Prepared；长保护链仍原位保存；真正addition个数保持 |
| T5 | Reference `preparedMetadataRejectsReaderLastUseAbortAndCompletionChanges`、`preparedRecoverableWriteLifecycle`；CpuMutation `commitRebasesAfterDisjointPublication`、`commitRejectsConflictingPublicationAtomically`、`defaultPublicationRevalidatesDescriptorStorage` | 每个unlock窗口late变化；一组最后页冲突不能有第一组安装；recoverable/authority查询保持；default变更使descriptor hint失效 |
| T6 | Reference `preparedPublicationStorageIsBound`、`publicationStorageRefusalAndLateCleanup` | 0/1/16/17/跨分片、负坐标/相同hash不同key/乱序重复；小N排序净开销；原Data新增字节硬满拒绝；失败统计不漏，实际锁run数量 |
| T7 | Reference `deferredPublicationCleanupOwnsCandidate`；CpuMutation `publicationCleanupUsesBoundedBackgroundPasses` | 阈值上下边、部分reservation/claim失败、最后shard引用、payload析构在门外、activity恰一次归还；时间界/最大持锁，单位/候选守恒 |
| T8 | Reference `reclamationTaskStorageBeforeOwnerRelease`、`reclamationTaskRejectedPreparation`、`preparedReclamationRunsAtCapacity`；CpuMutation `terminalReclamationStorageAtCapacity` | invoke/非reusable dispose/finished顺序、finished销毁job、self-requeue、queue拒绝同步fallback、drain后物理存储与费用终点 |
| T9 | Reference `retainedWakeInFlightAfterController`及原reclamation测试 | 用同步屏障固定idle→enqueue、running追加、wait临界、cancel已取走、rearm代际、earliest移除/插入、reset在dispatch中、ready/timer公平、worker退出ID清零；不得靠sleep猜交错 |
| T10 | CpuMutation `automaticLastUse`、`lastUseBoundedBurst`、`lastUseCloseAndLifetime`、`lastUseAtMetadataCapacity` | 首次/重复terminal、执行中/finished前事件、retry已安排时新进度、无GUI/新输入、late capture/root不悬空 |
| T11 | CpuMutation `longHistoryUsesVersionBudget`、`multiPageHistorySharesRootBudget`、`historyRootSliceRevalidatesChangedKey`、`historySweepRevalidatesAndRevisits`、`rejectedRetirementsPreserveDebtAndBudget`；Reference `retirementQueuesPreserveBudgetAndIdentity` | 同根/变根与跨slice解保护、epoch child边取边入队、最后节点/最后owner、128公平、物理free才归费；效果接收拒绝页不丢、预算唤醒合并不丢真实进度 |
| T12 | tiles3 `testPageStorePixelOperation`及borrowed/concurrent/packed/copy/iterator原测试；ResidentRead `guardLifetimeAndHistory` | current/G0/oldData/source不同cut、false回调与越界锁存、真正19updates工作量；所有修改适用架构与非目标入口控制 |

Reference/CpuMutation源码分别在[ReferenceTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreReferenceTest.cpp)、[CpuMutationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp)。新增helper共享oracle之后仍保留独立预期字段/拒绝/像素断言；测试通过不自动证明算法已少做工作。

统一实验顺序：

1. **开发纠错**：逐责任编译并跑受影响T组，保留失败；源身份/新增存储/consumer核验同步做。没有产品改动时不跑历史安全大矩阵。
2. **机制资格**：完整候选用有限派生计数，按同义工作记录下节分母；foreground与七类后台责任分别计数，真实free落在Stroke后则在终结/drain补齐。实际计数不是估算malloc；无触发条件项明确记0。原则上不加逐单位clock，不重跑108过程覆盖实验。
3. **未插桩净收益**：实施完成前冻结父704、候选、同依赖upstream及原控制a918的用途，沿既有40配对/平衡顺序协议建立有限批；同像素/输入/19updates/实际job/undo/退出、加载库/79共享依赖匹配。记录全部慢值、样本和失败，不替换/加样到通过。若工作量不等先裁决，不用更新合并伪装优化。
4. **控制与资格**：父/候选量本包增量，上游量剩余差距，a918量原控制；Stroke CPU/wall、Undo/Redo/Teardown、完全drain、峰值/驻留metadata分开，Fresh/H4和适用ARM/x86按原资格覆盖。Teardown≤2%非劣和完整CP0/M6缺口不能用Stroke收益抵消；2/20校准、metadata≥25%同义分母仍需独立完成。
5. **有限裁决**：预测动作兑现但时间不显著则说明必要成本/新成本抵消/定价误差；安全或负控制失败保留候选，不默认晋升。只对未解释因果做预声明有限消融，不开启新一轮全覆盖采样。完整责任未关闭不能以一次正收益结束。

<a id="quantity-ledger"></a>
## 5. 预测与实际使用同一分母

计数定义与非加性规则见[03h §14](03h_cpu_lifecycle_ideal_blueprint.md#forecast)。下表只使用本候选8个机制过程；保留必要标量事实、真实free和未触发项，不从旧候选搬数。

| 责任 | 删除量预测/理想复杂度 | 新增/必要成本 | 实际/偏离原因 |
|---|---|---|---|
| LP01 | 合格事件Σ完整保护镜像→0，必要标量V不删，未变base重装→0 | 真正target A、pin/header、容量和复验；有inline不必有malloc | projection Stroke旧record整装396→0；完整保护投影628–672→0，必要薄投影640–672；不授全WorkingVersion删除 |
| LP02 | 合格private镜像/整记录重装→0；首次路径额外snapshot/锁进入→0 | 原base/target guard、proof和真实读cut | private publish132保持、额外snapshot132→0，重复caller metadata进入退出 |
| LP03 | 普通candidate完整保护镜像/旧publication整表比较→0 | 实际delta、addition、authority、revision/claim保持 | 普通候选保护镜像/差分退出；相关标量仍有；recoverable/detachment真实consumer保留 |
| LP04 | 最坏重复比较ΣN(N−1)/2→Σ[sort(N)+N−1]；growth筛选SN→N；每适用锁pass N→G | 原entries新增ordinal/组范围、排序、锁尾延迟 | 相邻比较119–136+sort413–501，对照706–848；growth1300–1652→112–140；stats248–292→0；小run仅约10锁下降 |
| LP05 | activity锁N→G_cleanup；最终pass idle锁每candidate至多2→1 | 全部实际payload/free/统计、原时间/单位界 | 全观测阶段活动锁408–428→221–239，idle36–38→26；真实payload/free仍做，时间/单位界不变 |
| LP06 | job notify J→B；worker队列锁约2J→J+1；身份写2J→2/线程寿命 | enqueue锁/每job真实invoke/dispose/finished保持 | 全观测阶段job通知177–192→39–44；取头锁173–185→启动1；完成锁仍每job一次；worker寿命身份写 |
| LP07 | notify全调用数→最早deadline变更+ready空到非空 | 原generation/clock gate/有效任务保持 | 空cancel通知196–207→0；arm与ready在匹配fixture调用0，不虚报这两项实际删量 |
| LP08 | 条件epoch锁按节点→按摘链批；其它未获许可不授量 | 真实history/last-use/retire/free与公平保持 | epoch取头锁225–275→68–84；销毁214–261对228–261，受后台调度影响不强配差值；条件last-use未触发 |
| LP09 | exact-value命中调用的历史比较ΣHᵢ→完整相等核验O(命中数) | 原map node、共享引用/owner寿命，无hint原路保持 | projection Stroke exact命中132次，历史比较187–191→55–59；真map node与原引用仍存在 |
| LP10 | 仅经稳定scope证明的重复选择/访问 | 像素、changed、真实cut和晚读者不减 | 19更新、96 bound页面量不改；五阶段总CPU降0.20%[−0.81%,1.29%]，净收益未证 |

成本桶不可简单相加成预测ms。最新detail的3.589741ms前台cold/seal/commit、另一配置的1.441125ms后台不是同一可删预算。完整候选记录“预测删量→实测删量→新增量→未插桩净CPU/wall→剩余upstream差额”，各阶段和全生命周期同时对账；尚未定价时不给乐观/保守百分比填充。

<a id="delivery"></a>
## 6. 交付栏与停止判据

本包本地产品提交`d182a34bd0196079bc40d2ab7d00b8e326e4a58a`，分支`codex/br1-cpu-lifecycle`；原704/a918分支保留、不push。生产代码+687/−338（净+349），测试+78/−1，CI+10/−3；新增有限直接安装路径与分组责任，不能宣称源码复杂度净减少。无新增业务保证/第二状态机/owner；[全hunk审计](../evidence/br1_cpu_lifecycle_implementation_20261009/implementation-audit.json)、[完整报告](../evidence/br1_cpu_lifecycle_implementation_20261009/README.md)记录失败和最终身份。

全部目标都有具体结果是责任交付条件；净收益/默认晋升/M6资格分别判定。当前M6/M7/M8仍0/3，校准2/20，persistent默认关闭；本蓝图不改变任何门限或资格。

父704对照20块/40配对：Stroke CPU下降3.88%[−0.28%,8.82%]、wall下降3.07%[−1.61%,8.62%]，均未证明收益；Undo/Redo/Teardown CPU下降11.45%/7.33%/9.08%。五阶段含Setup CPU下降0.20%[−0.81%,1.29%]。原a918的Teardown wall≤2%非劣在本pointwise批通过，但父对照上界1.0219未过，不能授正式family资格。Fresh/H4各四桶family通过；候选对upstream仍额外约7.64ms Stroke CPU/3.28ms wall（配对差中位），不是本包已经解决核心差额的证据。

预测动作已兑现，净收益证据弱：实际保护元素只0–13个（全观测阶段），396次旧record重装被删除而必要薄事实仍约640次/Stroke；小候选的N→G收益有限，后台真正任务/free未删除。不能给所有管理对象一个统一单价，也不能将剩余约7.64ms全部归因于保留锁或正常管理成本。下一归因须对必要标量构造/索引、owner/provider/proof与真实业务工作建立单位净价；没有此证据不再以通知删量预测大幅提速。
