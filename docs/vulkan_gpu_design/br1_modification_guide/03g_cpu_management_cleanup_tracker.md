# 03g：CPU 管理管线清理追踪矩阵

本文件是[03f代码索引](03f_cpu_management_cleanup_index.md)22个子项的**唯一实施状态账**；[03e](03e_cpu_management_pipeline.md)解释算法，92维护资格。实施候选`704d96e81cf29d16191bc3db8785859d79775e27`，父`6644249a4c`，分支`codex/br1-cpu-management-cleanup`。[本包报告](../evidence/br1_cpu_management_cleanup_20261008/README.md)、[证明及hunk归属](../evidence/br1_cpu_management_cleanup_20261008/PLAN.md)限定结论。22项代码迁移和适用安全验证完成；数量、净收益、原控制、晋升和M6分别裁决。

<a id="tracking-rules"></a>
## 1. 一致性规则和状态

- 固定MP01–MP10↔03e A–J映射；子项只增不删，拆分须保留父映射。每个产品hunk和新增/删除符号必须归属某一子项或R反例修复，不得以“顺手优化”游离。
- 正常状态为`待证明 → 待实施 → 已改待核验 → 验证通过`。`待实施`只表示设计已有依据，绝不等于安全已证明。`有证据保留`和`撤回`必须给出反例/消费者、较便宜替代的比较、仍剩工作量及下一责任；不能把它们涂成理想目标已达成。
- 每行关闭必须填同一候选commit、差集、删除检索、适用分支、行为结果与数量证据；未测净时间写“未独立定价”。新API若只是把全扫/复制/锁转到别处，该行仍未关闭。
- 目标变化要先改03e算法/03f删除条件，记录旧目标→新证据→新目标→受影响ID，再更新本表和92；不通过修改预测来掩盖实际未兑现。旧证据包不改写。
- 实施过程中发现同模式漏点，先补本表与索引、再改代码；全部22项核销前不能宣称完整清理。数量、安全、净收益、默认晋升、M6五类结论分开。

<a id="cleanup-tracking-matrix"></a>
## 2. 实施矩阵

D统一为704d96e81c及PLAN/删除核验；S为双架16组9224/0/0及定向55/0/0；Q为外部派生库8过程counts-summary。投影未触发项以原协议及源码闭包证明删除条件，不授该fixture删量或独立时间。所有22项属于同一候选。

| 子项 | 理想机制目标 | 依赖/尚需闭合条件 | 状态 | D / S / Q |
|---|---|---|---|---|
| [MP01.1](03f_cpu_management_cleanup_index.md#mp01) | canonical借用只读clone=0 | 两处as_const；模板可写COW保留 | 验证通过 | D/S；Q：联合MP04：19 clone→0，公共借用保持 |
| [MP01.2](03f_cpu_management_cleanup_index.md#mp01) | packed只读不调用可写begin | 原const targets寿命覆盖lambda | 验证通过 | D/S；Q：不重复领取clone |
| [MP02.1](03f_cpu_management_cleanup_index.md#mp02) | 构造与查询一致排序 | (surface,row,column)；任意输入仍规范化 | 验证通过 | D/S；Q：11次反向重排→0；72页负坐标反例 |
| [MP02.2](03f_cpu_management_cleanup_index.md#mp02) | BoundEntry第二sort=0 | less删除；仅Debug断言 | 验证通过 | D/S；Q：19次/96元素→0 |
| [MP03.1](03f_cpu_management_cleanup_index.md#mp03) | cursor线性扫描/targets字段=0 | 唯一execution判断；失败锁存 | 验证通过 | D/S；Q：96次contains→0；比较元素数未知 |
| [MP04.1](03f_cpu_management_cleanup_index.md#mp04) | reservation移交全扫=0 | 原admission核对owner/token/set，原子move | 验证通过 | D/S；Q：32次、154/158键→0 |
| [MP04.2](03f_cpu_management_cleanup_index.md#mp04) | 独立operation不重入claimRange | 存储准备先于移交；history保留通用准入 | 验证通过 | D/S；Q：19次/96键→0 |
| [MP05.1](03f_cpu_management_cleanup_index.md#mp05) | 公共已有键3定位→1 | 新键/回滚/incarnation保持；独立直接slot绑定 | 验证通过 | D/S；Q：独立96键3→0，较原模型多删96查询 |
| [MP06.1](03f_cpu_management_cleanup_index.md#mp06) | bound冷页claim重入=0 | linked execution原claim；无execution仍准入 | 验证通过 | D/S；Q：96→0；claimOne总136→40 |
| [MP06.2](03f_cpu_management_cleanup_index.md#mp06) | bound冷支二次findIndex=0 | 沿用scope保护的entryIndex | 验证通过 | D/S；Q：96→0；不重复领取helper内查询 |
| [MP07.1](03f_cpu_management_cleanup_index.md#mp07) | native中间锁对=0 | 一个原activity；异常回锁和退休保持 | 验证通过 | D/S；Q：132→0 |
| [MP07.2](03f_cpu_management_cleanup_index.md#mp07) | alias中间锁对=0 | provider后接受/旧slot判断仍在gate | 验证通过 | D/S；Q：投影未触发，不授132删量 |
| [MP07.3](03f_cpu_management_cleanup_index.md#mp07) | generic中间锁对=0 | Preparing/preparation activity证明与domain/同步终态无关 | 验证通过 | D/S；Q：投影未触发；R09证明见PLAN |
| [MP08.1](03f_cpu_management_cleanup_index.md#mp08) | 空candidate清理锁对=0 | 非空失败仍锁外析构，出口恢复锁/减activity | 验证通过 | D/S；Q：32→0 |
| [MP08.2](03f_cpu_management_cleanup_index.md#mp08) | native空descriptor锁对=0 | 原publication共同cleanup；原索引持allocator owner | 验证通过 | D/S；Q：132→0 |
| [MP08.3](03f_cpu_management_cleanup_index.md#mp08) | alias空descriptor锁对=0 | 同共同cleanup；非空替换/拒绝仍锁外free | 验证通过 | D/S；Q：投影未触发，不外推 |
| [MP08.4](03f_cpu_management_cleanup_index.md#mp08) | retainAdmission空write-set锁对=0 | terminal未移出writes；交付后才放claim | 验证通过 | D/S；Q：32→0 |
| [MP08.5](03f_cpu_management_cleanup_index.md#mp08) | generic空descriptor锁对=0 | 原request终结及非空free保持 | 验证通过 | D/S；Q：投影未触发，不外推 |
| [MP08.6](03f_cpu_management_cleanup_index.md#mp08) | 初始化空descriptor锁对=0 | 原验证/回滚；terminals capacity仍释放 | 验证通过 | D/S；Q：投影未触发，不授stroke收益 |
| [MP09.1](03f_cpu_management_cleanup_index.md#mp09) | seal全查3S→S | gate/Sealing保持claims，两次动态复验 | 验证通过 | D/S；Q：父96轮462/474查询；候选32轮158＋64动态判断 |
| [MP10.1](03f_cpu_management_cleanup_index.md#mp10) | 单页版本查询全scope扫=0 | 原单键owner/token/非GenericWrite归属 | 验证通过 | D/S；Q：投影读分支0，不外推 |
| [MP10.2](03f_cpu_management_cleanup_index.md#mp10) | 重复预留已有页全scope扫=0 | 全部原caller；IntentOnly/foreign拒绝 | 验证通过 | D/S；Q：40调用284/316查询→40单键查询 |

<a id="path-coverage"></a>
## 3. 入口与终结覆盖矩阵

每条路径必须留下“已迁移＋反例结果”或具体保留原因；表中“保持”也是需要核验的consumer，不是可略过的空格。

| 路径 | 必须覆盖的MP | 必须保持的退出事实 | 当前 |
|---|---|---|---|
| 独立cursor operation | 01–09适用项 | 首字节前prepare拒绝无像素；回调失败不交付；adapter完成前原claim仍在 | 验证通过（S；保留项见PLAN） |
| packed writeBytes | 01.2/02/04/05/06/07/08/09 | 全页覆盖、partial、no-op、before cut、changed只含实际触页 | 验证通过（S；保留项见PLAN） |
| 持续history operation/公共borrow | 01/02/03/05/06/07/08/09；04保留generic分支 | 多execution重叠拒绝、跨worker合法借用、准备失败不污染旧段、checkpoint | 验证通过（S；保留项见PLAN） |
| fillRect clear/partial | 04.1/07/08/09/10.2；无需execution | semantic removal、uniform alias、partial copy、真实中间reader | 验证通过（S；保留项见PLAN） |
| legacy iterator/batch/copy | 07/08/09/10 | 原token归属、tile锁顺序、无等待重入、cache仅identity hint | 验证通过（S；保留项见PLAN） |
| alias seal/替换pending | 07.2/08.3/09 | 不退休被拒的旧slot；partial proof接受后retry不重做 | 验证通过（S；保留项见PLAN） |
| generic acquireWrite | 07.3/08.5；公共claim保持 | CPU/异步/其它domain分别核销、原request/pending/retire/取消寿命 | 验证通过（S；保留项见PLAN） |
| 初始页登记 | 08.6 | provider验证、部分登记回滚、finalize限制、非空free | 验证通过（S；保留项见PLAN） |
| retainAdmission交付、late guard、析构/cancel | 04/06/08.4/09与R04/R05 | 原owner最终释放、no dangling entry、物理free后归费 | 验证通过（S；保留项见PLAN） |
| default读物化与domain变化 | R02/R03/R07 | 有真实消费者的中间锁及AcquireRead前保护继续存在 | 验证通过（S；保留项见PLAN） |

<a id="verification-matrix"></a>
## 4. 算法验收与测试落点

以下反例均纳入同源安全组；新增72页负坐标/跨行列/重复rect及首次越界不新增代际测试。Reference迁移旧rebind测试，补空reservation、单键foreign owner/token/IntentOnly拒绝。foreign有效reservation无公开构造入口，其拒绝由私有producer闭包及原owner检查证明，不能伪称已动态伪造。

| ID | 验收内容 | 现有落点与必要补证 |
|---|---|---|
| V0 | 固定产品父、候选tree、实际库/依赖、upstream、全路径清单；22个ID双向覆盖 | 本轮[源码索引核验](../evidence/br1_cpu_management_blueprint_20261008/README.md)作为起点；实现后重扫，不把旧行号/四案例当新库身份 |
| V1 | canonical只读无复制、跨层顺序一致；泛型保持COW隔离 | SnapshotArray实际模板微探针＋产品借用反例。2×2、单行/列、负坐标、乱序重复、空、>64位图边界；输入字节/元素不变 |
| V2 | 原caller迁移，旧成员/参数/helper/重入路径退出 | 03f固定符号检索；所有新增函数实际caller非零；generic claimRange/初次claimAll保留；源代码数量与Release实际行为区别；MI1–MI8账本 |
| V3a | 规范范围到真实像素/changed输出 | `executionLocalCountersAndCancellation`、`executionBorrowStorageRejection`、`testPageStorePixelOperation`及packed/copy/clear原测试；补跨行列/负坐标查询，核对>8索引和>64范围 |
| V3b | cursor越界锁存、无新页准备、旧guard释放 | [testPageStorePixelOperation](../../../krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:2397)已有越界→合法仍失败；补首次越界相对callback前预备完毕的代际不增长及失败锁存 |
| V3c | 原权限与entry寿命 | [executionBorrowExclusionAndFailure](../../../krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:7801)、`executionBorrowWorkers`、`executionBorrowLateGuard`、`checkpointKeepsOriginalScope`、`testPageStorePixelOperationBorrowed/Concurrent`；补foreign/空/未接纳reservation及growth后竞争、接收中容量拒绝，保持历史旧段 |
| V3d | 锁/活动计数/预算/实际free | [mutationScopeAdmissionBudgetRejection](../../../krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:7899)、`executionPreparationReusesParkedBacking`、`executionWarmDuringColdPreparation`、`ledgerBackingRegistrationExcludesDomainMovement`及Reference实际登记/准备失败测试；补空/非空/替换descriptor、最后allocator owner、alias/provider异常、generic取消、初始化部分失败 |
| V3e | seal/cancel/checkpoint/adapter真实交错 | [sealPreservesReaderChanges](../../../krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:1514)、`blockedSealValidationAllowsParallelWork`、`sealPreparationClaimsAndSibling`、`sealStorageRefusalKeepsFrozenOwner`、`failedSealKeepsEarlierSegment`、`checkpointFailurePreservesFrozenViews`；验证三窗口晚reader、原claim与retry、retainAdmission交付之前拒绝新writer |
| V3f | legacy单键归属、cache不造新页 | [testIteratorWriteScope](../../../krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:6048)、`testIteratorNestedWriteScope`、read-cache与copy原测试；补大scope中重复同页预留、foreign token/IntentOnly、过期wrapper，无关页数量增加不放大全scope检查 |
| V4 | 下节逐项机制计数与守恒 | 低扰动计数/实际分配与锁分支，区分初始化/投影/画笔/Undo、正常/失败；不得不断添加细时钟。计数诊断不与正式性能样本混用 |
| V5 | 完整候选未插桩净收益与原控制 | 按原固定协议预注册父/候选/upstream及需要的默认基线，Stroke/Undo/Redo/teardown、Fresh/H4及适用架构，真实工作量/退出/加载库一致；不逐MP各跑一套矩阵、不加样到通过 |
| V6 | 统一交付及偏离裁决 | 保存全部失败、预测/实际/残差、源码/库hash和删除账；92更新资格。原冻结Undo +5.06%不改写，本批独立a918对照支持诊断恢复；完整默认qualification与M6仍开放 |

<a id="quantity-ledger"></a>
## 5. 数量账：实现前后使用同一分母

设O为非空成功borrow数；N_a为全部reservation转交的目标键数之和，N_r为转交后绑定execution的键数之和，N_e为本次绑定中已有键数之和；D_e为bound execution冷代际；D_f/D_a/D_g为native Fresh/alias/证明成立的generic锁交接次数；S为走完三次claim核验的seal输入键数之和。M_c为cursor实际换页查询，L为legacy单页查询/已有页重复预留次数。所有符号是实验计数，不以cold/seal数量冒充未知分母。

| ID | 当前→理想 | 原同路径用例的条件预测 | 实施后必须填 |
|---|---|---|---|
| V4a / MP01–02 | 冗余clone O→0，分配请求约2O→0；反向重排与BoundEntry第二sort→0 | O=19时19 clone、38请求；N元素复制量待计。任意输入首次规范化复制保留 | 19 clone/96元素/768B→0；38请求为模板两分配推导，非malloc实测。11次反向重排和19次BoundEntry排序归零；联合MP04不重复定价 |
| V4b / MP03 | M_c次线性contains→0，execution二分查询保持 | M_c未知，不以pin数替代 | 96次contains→0；范围长度和952不是提前命中前的比较次数。原execution查询保持；72页反例通过 |
| V4c / MP04–05 | adopt全查N_a＋claimRange两轮各两次查询4N_r删除；已有entry少2N_e查询 | 合计N_a+4N_r+2N_e；同一独立operation三者相等才简写7N。fillRect只有adopt项，不授borrow项 | N_a=154/158，N_r=N_e=96。原预测为N_a+4N_r+2N_e；直接slot绑定实际另少N_e查询，未另建索引。fillRect不授borrow项 |
| V4d / MP06 | D_e次claim重入及D_e次冷支重复findIndex→0 | 冻结用例D_e=96；另36非execution冷链不免首次claim | 96次bound重入及96次二次定位→0；claimOne136→40。整体findIndex1218/1222→454，与4键输入波动分别报告，不混同claim表查询 |
| V4e / MP07 | 中间锁对D_f+D_a+D_g→0 | 仅D_f=132已知；alias/generic未知，不按132外推 | Fresh132中间锁对→0；alias/generic投影0，条件代码已迁移，不外推132。原活动计数/最终接受及拒绝恢复保持 |
| V4e / MP08 | 实际空且安全的清理锁对ΣEᵢ→0 | 六类Eᵢ未知；不以19/32/132填入 | candidate32、native descriptor132、retainAdmission32空清理锁对→0；加Fresh共328对。alias/generic/初始页不授投影收益；非空free保留 |
| V4f / MP09 | 同一冻结集合claim查询3S→S | 只计三处均到达的成功链；重试/失败按实际到达点单列 | 父3S=462/474；候选S=158且另64次动态判断。父S154/158随实际clear范围波动，不能把跨过程差当净删量 |
| V4g / MP10 | 每次单页操作扫描Nscope→单键或原entry有效证明 | L及各次Nscope未知，成本为ΣNscope→O(L)次查询 | 投影read=0；已有页重复预留L=40，父ΣNscope=284/316→40单键查询。无关scope扩大不再增加此检查 |

必要工作守恒：原投影19 operation、32真实写段、132冷代际、真实像素/changed/读cut、首次权限获取及最后free不以本方案减少；实际新批须复核同义工作量，变化则说明原因。原5N/7N模型是不同调用点的逻辑查询数，不表示所有查询等价或都是hash；small write-set可能线性。

直接slot绑定另省N_d=96，实际逻辑模型N_a+4N_r+2N_e+N_d；同一独立路径均相等才简写8N。原预测不改写，公共已有键仍3→1，fillRect仅adopt。净CPU模型＝被删除工作独占成本−新增接收/分支/表示成本；wall还受关键路径影响。旧0.34/0.568ms混合桶不授预算，各项单价仍未知。

未插桩40对相对父：Stroke CPU降低3.08%，95% CI[0.33,6.86]，配对节省中位数0.182ms；wall CI[−0.07,7.35]跨零。Undo wall/CPU降低9.31%/7.83%，Redo降低5.95%/5.39%；Teardown未证明2%非劣。独立upstream40对仍为Stroke CPU1.8649倍，CI[1.7592,1.9704]。另按采样前协议独立a91840对，Undo wall/CPU降低8.35%/6.60%，诊断层恢复；Teardown CPU上界约+2.10%，完整默认资格保持开放。Fresh/H4双架8桶保护fixture非劣通过；完整时间/控制分母见本包报告，不能累计这些百分比或授M6资格。

<a id="completion-contract"></a>
## 6. 包完成与防漂移检查

| 检查 | 完成必须满足 | 当前 |
|---|---|---|
| 覆盖 | 22项与03f一一对应，10父项与A–J一一对应；入口矩阵10行全部有结论；R01–R09复核 | 22子项/10路径/R01–R09已核对 |
| 实现 | 每项有实际差集/consumer/旧路径检索；已替代字段、参数、全扫和空交接退出；无另一层同义补偿 | 704d96e81c；完整hunk/删除账 |
| 安全 | V3适用反例、资源与失败终点通过；未覆盖项明确，实际free/归费和动态复验保持 | 双架9224/0/0，定向55/0/0 |
| 机制 | V4逐行实测与预测比较，归零失败保留为未达成；未独立定价不编造毫秒 | 8过程计数；未触发项不外推 |
| 收益 | 完整候选V5固定实验结束、负结果保留；与原Undo控制分别结算 | 40对父/候选及40对upstream已结束；Fresh/H4见最终报告 |
| 交付 | V6冻结身份与失败、92更新；局部完成不覆盖M6/metadata/CP0缺口 | 报告/冻结身份/92 §16.155；不晋升 |

“有证据保留”可以结束一次有限候选，但**不能据此宣称整个理想管线已经实现**；必须列仍未实现的目标、残余工作及具体阻塞。不得为了全绿把待证明项移出矩阵，或把“没有测到收益”改写成“本来不需要清理”。全部可实现目标闭合后统一比较理论与实际，再决定后继责任。
