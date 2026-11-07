# 清理后相对 upstream 的回退来源重新排序

本轮只复算既有新数据和核对当前代码，没有修改产品或新增性能样本。产品固定为 `704d96e81cf29d16191bc3db8785859d79775e27`，tree `4e7fc164db46c02b968fdd04400b9e4402e289d0`；文档父为 `36fb72baf25412fd5f7f7f6c71c487ff93162019`。输入来自[管理管线清理冻结包](../br1_cpu_management_cleanup_20261008/README.md)，未改写该包。

结论：**优先保留“逐代际冷准备 → private seal → canonical 发布”的整条生命周期责任；已删的重复 claim、扫描、隐藏复制和空锁交接退出前排。operation 中的像素／暖访问与读选择／merge 外框是第二梯队，现有数据不足以确定两者谁贡献更多 upstream 差额。** 不能把未覆盖部分或这些混合区间统一解释为不可避免的管理成本。

## 1. 按同批绝对额外 CPU 排业务阶段

采用当前/upstream固定20平衡块、40配对、80个未内部插桩过程。比率及95%区间沿用原块bootstrap，是pointwise双侧区间，没有新授family资格。

| 顺序 | 阶段 | 当前/upstream CPU比率 [95% CI] | 配对额外CPU中位数 | 配对额外CPU均值 |
|---|---|---|---:|---:|
| 1 | Stroke | 1.8649 [1.7592, 1.9704] | **7.7685 ms** | 7.7979 ms |
| 2 | Redo | 4.8036 [4.4986, 5.0967] | 0.7585 ms | 0.7540 ms |
| 3 | Undo | 6.1895 [5.7052, 6.7669] | 0.5125 ms | 0.5279 ms |
| 4 | Teardown | 2.4644 [2.3494, 2.5622] | 0.4735 ms | 0.4761 ms |

四阶段配对均值可相加，合计9.55595 ms，Stroke占**81.60%**；这是该批四个端点的描述性份额，排除Setup和端点之间的间隙，不是完整fixture占比、可删除比例或置信度。各中位数不相加。Stroke优先的证据强；后三个阶段只是本批绝对点估计排序，未检验彼此差额的显著性。Undo倍数最大也不改变Stroke优先级。

所有慢值保留，包括Stroke一对CPU差为负和一对额外22.820 ms。upstream过程11有20次projection updates，其余19次；原像素、8 segment、4 callbacks和销毁检查通过，沿冻结规则保留，不按此次排序删样。

## 2. 当前源码的互斥工作桶与观察边界

复用清理包8个计数／嵌套观察过程中的4个候选过程。逐事件核验父子CPU账、无跨Stroke事件、祖先上下文；下面逐过程互斥汇总，不把inclusive父项与子项相加。每过程仍为208次冷准备（投影132、其它Stroke76）、59次seal（32+27）、46次operation（19+27）。这次观察未同时取得upstream对应分桶，也没有给该计数观察器单独校准价格。

| 互斥责任 | 当前4过程CPU范围 | 中位数 | 解释 |
|---|---:|---:|---|
| cold完整准备 | **2.581–2.836 ms** | 2.704 ms | 包含provider、默认填充、private metadata prepare、base/budget/register/binding等；不是全部管理指令或可删除量 |
| private seal完整区间 | 0.846–0.929 ms | 0.876 ms | 包含private publish、proof、overlay、writer释放及终结；private publish不能另加 |
| canonical commit完整区间 | 0.627–0.760 ms | 0.658 ms | 11–14次，含metadata/root/预算联合接受、安装、清理；不是一个输入核验循环的价格 |
| operation扣除上述子区间的余项 | **3.231–3.372 ms** | 3.330 ms | 包含真实pixel callback、暖访问、adapter、scope准备/交付和观察费用；不能全叫wrapper成本 |
| capture完整区间 | 0.325–0.361 ms | 0.357 ms | 51次，其中投影50次；尚无相同合同的upstream独占差额 |
| merge扣除已记录子区间的余项 | 1.086–1.246 ms | 1.129 ms | source读取、未包围调用、合成调度等混合外框；不等于纯read或等待 |
| 其余已覆盖区间 | 0.037–0.041 ms | 0.039 ms | 本批独立completion_complete区间，不能据此给所有票据定价 |

按**每过程先相加**，cold+seal+commit共**4.129–4.393 ms**；其中seal+commit为**1.512–1.637 ms**。capture+merge为**1.411–1.600 ms**。这些是同一观察条件下的当前工作桶，**不是相对upstream的额外成本，不能除以未插桩7.7685 ms计算归因占比，也不能领取为理论收益**。

当前计时事件共覆盖8.880–9.402 ms，而同过程Stroke进程CPU为17.085–18.181 ms，尚有**8.205–8.779 ms**未被这些事件覆盖。它包含必要画笔计算、其它线程/调度及观察器边界费用等，既不是已证明的额外成本，也不是纯后台管理。旧jobs-only曾覆盖更大范围，但其产品是fb57；旧画笔额外3.856 ms、未覆盖1.412 ms，以及664投影额外4.024 ms均不能移植填入704的账。

## 3. 归因与后续审查顺序

| 优先级 | 当前责任与代码入口 | 排序理由、置信与待证事项 |
|---|---|---|
| **第一梯队 A：逐代际冷准备及接收链** | `KisPageStore.cpp:2019 beginWriteImpl`；`KisPageOwnerLedger.cpp:968 registerBacking`；`KisPageMetadataCoordinator.cpp:3703 applyProjectedSequence` | 208条实际链仍在，当前桶2.58–2.84 ms；省几个查找未改变链数及多层接受事实。大桶存在性高置信，作为额外差距主要来源为中等置信；可删净量未建立。检查同一base/layout/physical结果在原reservation、provider、ledger和metadata之间是否重新表示、接纳和收费，保留真正独立的接受点。 |
| **第一梯队 B：seal到canonical的联合发布与释放** | `KisPageStore.cpp:2355 sealImpl`；`KisPagePublicationCoordinator.cpp:866 commitLocked` | 1.51–1.64 ms连续责任仍在，独立预算、metadata、root及真实释放均在此范围。与A共同审查原版本事实／delta从准备到交付的寿命；不要只改public proof反查或一个allocator。工作存在性高，差额归因中等，可删预算未定。A、B分桶互斥，设计共用一条完整生命周期。 |
| **第二梯队，暂不互排：operation内pixel／暖访问／adapter余项** | `KisTiledDataManagerPageStoreBackend.cpp:2064 runCpuMutationOperation`及`:2243 BoundedCursor` | 当前3.23–3.37 ms是混合桶；投影部分0.645–0.704 ms，其它Stroke部分2.556–2.686 ms。原“range+scope约0.34 ms”已含本轮删除对象，不重领。必须先扣清真实kernel，再判断暖访问和交付是否过重。当前额外差额和净删量置信低，不把桶大直接等同排名第一。 |
| **第二梯队，暂不互排：读选择与merge外框** | `KisPageStore.cpp:3038 captureReadViewImpl`；`kis_async_merger.cpp:172 startMerge` | 当前合计1.41–1.60 ms，capture约0.36 ms，剩余混有其它消费者。审查相同source/oldData/cut的选择及原reader寿命能否直接消费，不能缓存越过真实发布。存在性高，具体超额归因低至中等。 |
| **单独列为对账缺口，不排成瓶颈** | 当前未覆盖的Stroke进程CPU | 8.21–8.78 ms只是当前总量的覆盖缺口；必要工作及额外部分各占多少均未知。不得填零，也不能反过来宣布它比cold更值得优化。 |

“高／中／低”是证据强度，不是凭空估算80%或95%的归因概率。现有95%区间只支持阶段比率和整包增量结论；不能转成某个函数承担多少差额的概率。第一梯队内部顺序按现有工作桶规模和责任闭包暂定，第二梯队无可靠超额成本先后。

## 4. 明确降级和保留的候选

清理包投影19次隐藏clone、96次冷claim重入、96次二次定位、328对中间／空锁交接已退出，findIndex从1218/1222降到454。整包未插桩Stroke CPU只降低**3.08% [0.33%, 6.86%]**，配对节省中位数0.182 ms；wall改善区间跨零。它证明整包有净收益，但不支持继续把这些已删工作当主要缺口。不能把0.182 ms与另一upstream批相除作精确追回份额，也不能单独归因给锁。

private prepare+publish仍处理208个冷代际，当前观察self合计每过程0.689–0.781 ms，其中投影约0.378–0.455 ms；它分别已计入A/B，不另排成第三个独立大项。旧无内部时钟约0.407 ms与该投影量级相容，但不是精确同批验证。没有新证据表明全历史metadata复制或重试放大主导本例，不优先另造CPU状态机。

默认fill已变为块填充，当前116次fill观察区间合计约0.083 ms；旧约1.1 ms逐像素小memcpy问题已不再存在。额外整页copy的旧约0.064 ms只说明旧版本payload本体便宜，不直接定价当前copy或整条代际协议。真实读cut没有新等价性证明，132→96仍不合法。R08 descriptor相等布局的历史搜索仍开放，但本轮未测扫描长度/单价；保留候选，不由代码存在全表搜索便升级为当前主瓶颈。

被删328对锁是空交接，不是已测等待时间；剩余owner/publication/domain交接可有真实CPU和等待成本。当前没有锁等待的独占价格或关键路径证据，不能用“正常锁成本”封账。allocator同理，实际容量、原owner及晚free合同仍在，不代表当前每一临时表示都必要。

原a918独立对照中Undo回退已在诊断层恢复，它仍比upstream贵，但不再排作“上一轮引入且未修复”的回退。Teardown绝对差距较小，却仍欠原≤2%非劣资格；业务优化排序与默认启用控制分别保留。

## 5. 下一最小诊断与收益预测边界

下一诊断先在**当前704／固定upstream同一批**仅包围实际stroke jobs与merge jobs，恢复可相减的进程CPU账，明确观察开销和未覆盖部分；然后只对仍占主要差额的责任区分pixel kernel、暖访问与生命周期接收。复用原fixture、像素／回调／析构检查和有限配对规则，另存事前协议，不启动每个小项各一套全矩阵。本轮没有执行该诊断。

若生命周期仍为主要差额，沿同一原owner追踪 `base → provider结果 → ledger/metadata接受 → private版本 → proof/delta → canonical安装 → 真实释放`，列每个事实的生产次数、表示/接收次数、稳定区间和动态失效点；把有证明的相邻删除做成完整候选。不能先挑容器改完再追认理论预算。operation和read/merge先补独占差额，保留真实kernel、reader、预算和失败费用。

当前只给条件模型：`净可省CPU = 原重复工作价格 − 替代表达的接受/失效/释放成本`。4.13–4.39 ms整条观察链不是可达到的节省上界；缺少必要成本同批价格和可删除集合，**本轮不承诺新的毫秒数或提速百分比**。证据更倾向多层生命周期和混合路径共同形成差距，尚不足以证明它们全是不可避免的正常维护。

## 6. 复算与交付范围

[analyze.py](analyze.py)读取原80个未插桩过程和8个诊断过程，验证所有通过状态、预定顺序、同阶段父子CPU账、208冷代际/46operation、原汇总中位数，以及完整事件覆盖闭合；[summary.json](summary.json)保存输入SHA256、逐过程互斥桶、同批阶段均值份额和原pointwise区间。运行 `python3 docs/vulkan_gpu_design/evidence/br1_cpu_residual_ranking_20261009/analyze.py` 可复算；原输入在前包原始分片及本地同名目录，无需另复制运行库。没有删除样本、调整原门或新增CI。

本轮生产/产品测试增删0，不重跑安全或性能矩阵。首次文档补丁因旧段落定位不匹配被拒绝，核对文件后重施；未改变输入数据或样本。当前仍默认不晋升，M6/M7/M8 0/3、正式校准2/20、metadata同义驻留分母和完整CP0 required开放；唯一阶段裁决见[92 §16.156](../../92_br1_m6_m8_execution_baseline.md#cpu-residual-ranking)。
