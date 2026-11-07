# 各轮优化汇总与中间基线 IB0

2026-10-17汇总输入阶段固定产品 `e238d170d30a505a92f209874826ead056841566`、累计研究源码 `handoff-lifecycle-r0/source` 和证据提交 `bcc8dabb424d36bf6a6a99db060c96f85179d2a2`；下文价格、66个祖先清单与补丁仍按该冻结身份解释。**后续正常工程已集成为 `ab1bf42e18`**，实际差异、构建与验收见[集成结果](../br1_pagestore_equivalent_pipeline_20261010/intermediate-baseline/integration/RESULT.md)。该集成没有新配对性能价，不回写旧各轮收益或将它们相加。

**结论：以 e238 加最新累计候选形成 IB0；不再把各轮小增量当成整包进展，也不回到旧版逐项重做。** [IB0 定义、当前价格和集成出口](../br1_pagestore_equivalent_pipeline_20261010/INTERMEDIATE_BASELINE.md)区分本汇总冻结的输入和后续已正常构建的产品提交；集成完成不将历史候选价格自动变成新产品的实测价格。

## 1. 汇总口径与覆盖

下面按责任演变汇总实施结果，另以[逐轮证据目录](ROUND_CATALOG.md)逐项保留早期 CP3/M6/业务优化、研究候选、前置验证、计价、反例与失败探针；[产品提交清单](PRODUCT_LINEAGE.md)覆盖 `500fd0702c` 至 e238 的全部 66 个提交，并核对指定关键提交均为 e238 祖先。报告轮、实验批和 Git 提交不是一一对应关系，不能将目录数叫作“有效优化次数”。早期 74.2% 引用链阶段已纳入，之前功能建设不重计为本次性能收益。

- **已在产品祖先中**：其最终保留实现随 e238 继承；历史上称“候选/未验收”不等于今天代码不在当前分支。性能资格仍看原实验。
- **累计候选中**：以实际源码、派生/合并输入和冻结哈希确定继承，不按“后一个目录”推断。
- **被替代/撤回**：保留负结果与原因，不重复应用旧补丁，不把旧收益加到新版。
- **诊断、计价、模型、门禁变更**：提供选点或约束，算法净收益记为“未产生”，不能与实施混算。

所有百万指令数写作 M。表中 `C−R` 是本轮候选减本轮重编父版本，负数表示减少；不是对 e238 的累计收益。8 块描述范围不是概率置信区间。早期不同 fixture、机器架构、M5/upstream 分母和 CPU/指令端点不拼接。通用融合优化与 PageStore 同能力基础优化分账。

## 2. 已进入 e238 的优化主线

| 轮次/责任 | 实际留下的实现与删除 | 本轮结果及限制 | 在 IB0 中的处理 |
|---|---|---|---|
| CP3 冷准备、工作值、存储准入、限额、epoch、backing/authority/claim、metadata 候选批量（500fd→6ffe） | 收费存储、连续批表示、原物理槽 claim、候选一次分配，删除多份临时索引和重复构造 | 各包取得结构/语义证据；原 Fresh/handoff 性能族仍未通过，不能按提交数推累计提升 | 随 e238 继承；后续有覆盖处以最终源码为准，逐包见目录 |
| [allocator 作用域保活](../br1_cp3_scoped_storage_20261006/README.md)，57e59 | 根保活＋内部借用，保留逃逸对象/实际分配寿命 | K16 三链归还 **4569→54**，总 **6157→1642–1645**；ARM K16 吞吐 **+5.04% [2.78%,7.44%]**。73% 次数删除不等于73%时间收益 | 继承；不再领取这一预算 |
| metadata 准入、handoff 槽复用（0a00、f0c） | 未变依赖事实复用、已收费准备存储复用 | 局部减费；[价值审查](../br1_cp3_handoff_value_20261006/README.md)不支持无条件 K16 优势30% | 原则和通用实现继承；IB0 native handoff 准备槽已进一步删除 |
| 新 M6 门、基线、提前拒绝、provider 借用（79e1、3883） | 已知忙状态提前拒绝；冷准备延后；原 provider 借用 | [provider 包](../br1_m6_provider_borrow_20261006/README.md)同库 hit4/4、miss16/16 数值过门；校准仅2/20，M6未过 | 继承；门禁变更本身不算加速，GPU价值仍待真实证据 |
| 稀疏 default clear，2f224 | 默认页不实体化 | [实测](../br1_projection_redundancy_20261007/README.md)root准备149→132、复制89→72；wall点估计−0.71%，区间跨零 | 继承；删量真实，不能解释大差额 |
| page-ordered fixed-source，f971→fb57 | 曾试图改变写入次序/准备 | 实验提交已由明确 Revert 撤回 | **不纳入**；不因祖先出现试验提交而重加 |
| native pin 最后 reader / 已持 barrier，751b、a918 | 将真实保护归回正确寿命，减少重复借还 | 后续投影生命周期以 a918 为父；见[CPU实施账](../br1_cpu_blueprint_implementation_20261008/README.md) | 随 e238 继承 |
| 完整投影生命周期，6644 | 五项联合准备/发布/资源责任清理，修复默认页读与配置拒绝接续 | [报告](../br1_projection_lifecycle_20261008/README.md)Stroke整包收益成立，Undo回退；当时仅保存候选 | 现已是 e238 祖先，继承；保留 Undo 欠账，不把当时限制抹掉 |
| CPU 管理管线，704d | 22项迁移；少克隆、重复排序/定位、重复 claim 和空对象锁交接 | [本轮](../br1_cpu_management_cleanup_20261008/README.md)投影 findIndex1218/1222→454；Stroke CPU约−3.08%，wall未确认。真实132代际保持 | 继承；大桶删量不等于大桶全价 |
| CPU 全生命周期，d182 | 22项实现、5项保留、1项整包审查；直接必要标量、分片批锁、退出调度 | [本轮](../br1_cpu_lifecycle_implementation_20261009/README.md)旧record整装396→0、额外snapshot132→0；Stroke及全生命周期净CPU未获95%支持 | 继承；不能将结构完整当收益完整 |
| 技能试行：读意图、free重复查询、空history任务、descriptor | 原型与候选筛选；c13c只补原空任务测试 | [排名复核](../br1_candidate_rank_audit_20261010/README.md)：高频可删未证明位于性能前列；未通过的TLS/清理实验不迁移 | 未交付的旧试验排除；后续真实读协议/历史事件实现按其提交继承 |
| 投影 clear/首层融合，8198 | 上层表达允许融合，减少冷准备和独立发布 | [生产包](../br1_projection_boundary_production_20261010/README.md)CPU省1.204ms，95%[0.922,1.781]；**通用业务优化，非PageStore同语义基础效率证据** | 保留已有代码；不计入本次PageStore基础净价 |
| 同语义整管线收敛，3f282→11c689 | operation交付、原D、稀疏presence、adapter/history/取消/恢复、捕获与回收责任统一 | [原追踪矩阵](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-change-index)保留唯一实施状态；结构完成不代表主差额消失 | 已在 e238，按最终consumer继承 |
| [operation拥有结果/容量](RESIDENT_OPERATION_RESULT.md)，02bcc | 稳定facts、H1 spare、H0直接canonical，避免过渡overlay | H1完整process指令179.230→149.221M，独立确认−16.74%；CPU省2.859ms；write却多8.443M，5个CPU控制未闭 | 继承后续版本；本轮揭示工作转移，不能只报process改善 |
| [private delta安装](READ_WRITE_PROTOCOL_RESULT.md)，d5f7 | 减少私有metadata准备/安装工作 | H1写少 **8.717M**；读基本未变、CPU未过，读写合计仍多约81M | 继承后续统一实现；不能将8.717M当读写问题已解 |
| [完成结果接纳/有限读范围](NATIVE_READ_WRITE_RESULT.md)，bb62 | 读写上移到operation；直接采用完成结果，保留有限读取范围 | 读写主路径实际改善；旧53.451M/3.374ms余额属于该冻结批，不是今天余额 | 继承，并由ed0/b756清理协议 |
| [统一私有结果和capture](unified-rw-r1/RESULT.md)，ed0 | 旧协议消费者迁移，统一读写寿命 | 同批仍多 **52.407M/3.535ms**；较bb62少约1.065M，未解释主差额 | 继承，并由b756继续最低路径 |
| [共同发布与最低capture路径](rw-minimum-pipeline-r1/RESULT.md)，b756 | 继续删除中间结果与冗余读路径，统一真实出口 | 指令局部改善；完整CPU/资源目标仍未闭，后来H1写差额约44M并未证明必要 | 作为后续研究公共祖先；经e238及IB0再覆盖 |
| 正确性前置，33132/0f526/0b116/e238 | signed父预算结算；真实debt；canonical带费所有权；有界close进度 | 前置修复不是免费：canonical detach等带来新费用，必须进入后续净账 | **全部保留**，不回到错误的低价版本 |

产品完整提交表还保留上述阶段内的取消、default、clone、restore、adapter等修复，不能因为没有独立速度报告就丢弃。

## 3. 研究原型及实施前置的归宿

| 轮 | 内容/已观察结果 | 最终处理 |
|---|---|---|
| h1-management-trial-r0 | facts→budget→activity空槽→清理阈值四累计变体；前三者H1写共少2.319M，第四仅条件进程价 | 不整包搬入；同锁/预算/活动思路由后版重新构造；**8→16清理政策不继承** |
| fact-window-r0 | 同锁事实、metadata准备合窗；控制读+2.622%未归因 | 纳入result-pipeline，旧单独补丁不叠加 |
| result-pipeline-r0 | 原结果layout/费用claim/proof/D；H1写−4.193M，process−4.423M；小读控制失败 | 由unified-native三方合并到e238，非另一个累计收益 |
| preconditions-r0 | signed结算、真实debt；预付未来debt反例 | 正确性提交进入产品；失败方案排除 |
| r1 | canonical带费脱离；H0 process改善同时write回退 | 0b116已入e238，费用进入基线 |
| r2 | D接受交接、空history清理候选 | 后续候选继承/改写，非独立再应用 |
| r3 | bounded close进度修复，先36失败后通过 | e238产品基点；不把正确性修复叫速度收益 |
| r4 | Optional借用 | 前置支线，经容量方案合并；不独立套用 |
| r5 | 同库测量控制 | 计量证据，无算法收益 |
| r6 | 全D容量接受与晚回退 | 前置支线，后由capacity-lifetime统一 |
| r7 | idle复用；Fresh下降，但Optional/Q仍有问题 | 被r8以后替代，不保留无界版本 |
| r8 | Idle分类、Q/T、退避和取消边界修复 | 由r10继续稳定记录；不是最终最低费 |
| r9 | r8完整计价：H0写−17.498M，H1 **+6.900M** | 回退证据保留，无新算法 |
| r10 | 稳定原准备record交接，候选7609；对r8 H0/H1写−2.143/−1.405M | **7609经三方合并进入capacity-lifetime，再修冲突和共同协议**；不等于最终源码逐字等同7609 |
| r11 / r12 / r13 | 暖/冷、费用/metadata、完整控制继续计价；r13 H1产品49.954M、7609 55.513M | 支线的失败与归因证据，不给IB0另计三轮收益 |
| cleanup-policy-r0 | 阈值8→16，H1write+1.177M、process−1.779M | 排除；IB0代码仍 `units <= 8` |
| native-activity-r0 | 原页活动事实，896暖节点消失；H1write−1.983M/process−4.343M | 并入下一联合候选，**不是与下一行相加的收益** |

[derive.py](unified-native-r0/derive.py)明确把 b756 上的 result-pipeline 与 e238 三方合并，再合并 native-activity；[derive_merge.py](capacity-lifetime-r0/derive_merge.py)明确以 e238 为共同祖先合并 canonical-compact 与7609，保留初次冲突及后续解决。最终选择以IB0全量补丁为准，避免“把所有看起来成功的补丁一起打上”。

## 4. 最新累计链：逐轮实现、收益和回退

以下各行都有真实替代实现。数字均是各自冻结批、相对各自父R的局部价格；**整列禁止求和**。主格为K16/W16/H0、H1；`≈0`代表未支持稳定变化，不是证明成本零。

| 轮 / 直接父 | 新实现与可核对删量 | H0写 ΔM | H1写 ΔM | H0/H1 process ΔM | 限制与归宿 |
|---|---|---:|---:|---:|---|
| [unified-native](unified-native-r0/RESULT.md) / e238＋两原型 | 原结果/费用claim/D与原页活动事实合在同一身份 | **−4.952** | **−5.917** | **−6.594 / −8.452** | 联合价已含native-activity/result；内部非内容仍为内容7.03倍，读控制失败；继承 |
| [accepted-identity](accepted-identity-r0/RESULT.md) / unified | 内部紧凑身份；native result344→312B、overlay304→216B | **+3.284** | **−3.144** | +3.603 / −2.720 | H0旧consumer重建投影造成新回退；下一轮修复，不能停在此版本 |
| [accepted-consumer-r1](accepted-consumer-r1/RESULT.md) / identity | 原result直接到真实consumer，H0完整投影/ledger查回4096→0 | **−3.231** | +0.008≈0 | −3.604 / −0.363 | 回收上一轮H0回退；H1暖零命中；未获整包CPU资格 |
| [native-acceptance](native-acceptance-r0/RESULT.md) / consumer | 暖原行直接接受；metadata prepare/install56→0，额外保活896→0 | +0.221≈0 | **−2.041** | +0.387 / **−3.265** | 全D claim/晚reader保留；上游多表示未消失；继承 |
| [operation-owner](operation-owner-r0/RESULT.md) / acceptance | 原scope拥有范围；删除独立reservation/adopt，原行槽号替节点索引；暖申请2752→1800 | **−3.294** | **−2.510** | **−4.136 / −2.710** | 952次删除不等于全部管理成本；继承 |
| [canonical-direct](canonical-direct-r0/RESULT.md) / owner | CommitTransaction原行规则，删除临时版本/replica模拟；旧oracle对照 | **−5.637** | −0.040≈0 | **−7.584 / −1.334** | H1暖canonical零命中；Publication一度1768→1888B，下一轮清空表示 |
| [canonical-compact](canonical-compact-r0/RESULT.md) / direct | Publication1888→160B；真实generic才存完整表示；K16实际准备容量少59,392B | −1.159 | +0.008≈0 | −1.397 / −0.069 | H0相对A写八块同向，相对R范围跨零；容量删量不能按字节推指令；继承 |
| [capacity-lifetime](capacity-lifetime-r0/RESULT.md) / compact＋7609 | 原容量/ledger登记跨cut，Q/T/原history接续；暖Fresh/register0，idle896次 | **−19.566** | **+3.948** | **−39.155 / +4.070** | H1八块真实回退；每次复用收费变贵，保留此欠账；旧transaction spare被共同寿命替代 |
| [budget-changes-r0](budget-changes-r0/RESULT.md) / capacity | 首次费用变化范围改法 | +0.375 | −0.431 | +0.481 / −0.266 | 全类扫描破坏metadata快路，**被r1替代，不叠补丁** |
| [budget-changes-r1](budget-changes-r1/RESULT.md) / capacity | 只在实际改变类上失效证明，恢复SSD aggregate | **−0.858** | **−1.029** | **−1.295 / −1.477** | oracle同义，CPU与其它控制未全闭；继承 |
| [core-acceptance](core-acceptance-r0/RESULT.md) / budget-r1 | 无保留Published/Prepared共同更新，H0每1024页三record新建/销毁归零 | **−1.006** | **−0.198** | −1.139 / −0.221 | H1全process范围跨零；剩余服务并未证明必要；继承 |
| [original-input](original-input-r0/RESULT.md) / core | 原D借到metadata，64个detachment申请/释放及1024行复制消失 | +0.018≈0 | −0.097≈0 | +0.142 / −0.149 | 写/进程范围跨零，不能宣称稳定加速；表示清理保留 |
| [handoff-lifecycle](handoff-lifecycle-r0/RESULT.md) / original | 句柄直接持原claim/许可；暖896个准备槽/目标登记/空publication，1008次空retained计算归零 | **−0.673** | **−0.717** | **−0.844 / −0.787** | 两主格八块同向；CPU未改善，4重编/6候选端点越线；**最终IB0** |

H1在capacity之前曾测到完整write约36.35M，最新约38.24M；这是**不同批的历史位置**，不是精确1.89M回退归因。capacity的同批+3.948M足以证明新增手续的负担；后版各轮局部回收有证据，但未经“完整旧产品/最终候选/同语义upstream”同批比较，不能宣布全数追回或给累计百分比。选择IB0是为统一完整责任并从固定中间状态继续开发，不是宣称它在所有端点构成Pareto最优。

## 5. 诊断轮带来了什么，哪些不能算优化

逐包链接见ROUND_CATALOG，下面保留影响基线选择的结论。

| 诊断序列 | 有效结论 | 对IB0的约束 |
|---|---|---|
| 早期metadata/管理采样→projection归因→CPU差额账 | 小memcpy与整页内核价格不同；投影cold/clear/composite与完整准备发布责任需要分开 | 不把CPU差额全部贴给metadata、锁或字节复制；不重复算嵌套责任 |
| read/write residual、boundary、最低路径系列 | 从52M读写差额追到activity/费用/descriptor/operation及退出；物理claim本身不是主价 | 留下全链账；理论最低金额仍未证明，不把未归因余项认作必要税 |
| instruction-account / causal / segment / object-envelope / state-fact等 | 指令数量、对象生成、控制频率比采样热点更可核对；有限K9外推有支持 | 定价是本实现条件价，不能由次数直接推出每操作都等价或全可删 |
| accepted/canonical/capacity/core冷热价格与失败r0→r1 | 观察器会改变被测对象；冷/暖、整写和process要同身份；重插桩失败不得用来排序 | 无效初次探针退出价格证据；保留失败，不把修正计价当代码加速 |
| whole-fact / fact-transfer-r1 | 父候选完整H0/H1非内容47.812/34.016M，内容比9.3509/6.6981；H1暖五项细责任仅约3.001M | 最新IB0无新内容分母，**当前管理比未知**；禁止跨批减0.717M得到新比例 |
| cost-necessity / commit-window | 提前整组预算会改变拒绝/peer/峰值；可取消结果和全D接受存在真实职责 | 不继承未经证明的896→56×G预算；不将K16拆两次不可逆半提交 |
| upstream-isolation | 有限upstream预备仅多约0.235M，不能解释PageStore全部数千万差额 | P不是完整PageStore等能力，不作新的正式分母；不把隔离义务当所有手续必要 |
| minimum-necessary / minimum-native-resource | 有限可执行核证明容量寿命可与值换代分离 | **不并入IB0**：缺稀疏/default/adapter/完整history/并发等能力；不增加另一个产品owner |

## 6. 得到的中间基线与下一次真正的进展

IB0是 e238 的完整后继源码选择：**19修改＋2新增私有头，净+710算法行；4测试净+763行**。最终21个算法变更都在PageStore目录，通用融合已在父代码中且不计入本次基础差额改善。完整补丁不依赖历轮派生器执行顺序，26文件回放已逐字节吻合。

最新同批K16/H0、H1完整写分别 **52.294M / 38.238M**，upstream **6.028M / 6.030M**，余额 **46.266M / 32.208M**；read余额2.881M/2.500M，完整process余额65.837M/52.897M。余额仍大，尚未证明必要；最新一次0.673M/0.717M只解释父候选差额的一小部分。

现在需要的是将固定IB0正常落源与验收，而非继续寻找一项更小的局部删量。集成期间只修真实include/CMake/consumer/合同问题并记录差异；必要行为断言不能为通过而删。冻结正常提交后做一次完整e238/集成版/U比较，报告累计净价与H1容量回退是否真正回收。当前小格控制失败、资源峰值/byte-time、压力/双架和正式M6欠项随基线携带，不能以失败未消失无限阻止默认关闭的中间开发集成。

本汇总不新增第二份实施状态矩阵；原33×6前五列未动。M6/M7/M8仍0/3、calibration2/20、默认关闭。累计优化不是零，但“每轮删量成立”尚未转化为可交付的完整低管理成本方案；IB0把分散成果固定到同一个可实施对象上。
