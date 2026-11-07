# CPU全生命周期优化：实施与有限验收

已按03j处理28项：**22项实现并通过结构/语义验证，5项有具体consumer而保留，1项完成整包审查**。本轮删量成立，Stroke和全生命周期CPU净收益尚未获得95%置信支持。保存在候选分支，不授默认晋升或M6通过。

产品父`704d96e81cf29d16191bc3db8785859d79775e27`，候选`d182a34bd0196079bc40d2ab7d00b8e326e4a58a`，tree`e03a63d2a33324a55c72b7eb8ec097deab96b171`，分支`codex/br1-cpu-lifecycle`。冻结image SHA256 `da4304d429134da577087e15004b4d98d93b7fc5c97a1bf6d8da4f4a615d66d1`。文档父e333942d9；原704和a918分支保留、本地提交、无push。

算法、改动位置和唯一状态账分别为[03h](../../br1_modification_guide/03h_cpu_lifecycle_ideal_blueprint.md)、[03i](../../br1_modification_guide/03i_cpu_lifecycle_edit_index.md#implemented-index)、[03j](../../br1_modification_guide/03j_cpu_lifecycle_tracking_matrix.md)。[事前协议](PROTOCOL.md)、[实施调整与失败](PLAN.md)、[14文件/109 hunk/32 kind审计](implementation-audit.json)、[交付身份](delivery-identity.json)可独立核对。

## 实际算法与范围

复用原唯一applyPolicy，限定Fresh/Adopt、Prepare/Begin和同步private组合消费不含保护链的必要标量事实，接纳真实容量后只安装target/base pin/header或实际发布字段；重试与首次发布同一metadata锁接纳。普通canonical由policy直接输出原candidate.deltas，退出保存旧字段再求差分。

原Data.entries按稳定分片/key排序，邻接去重；原installRecords暂存prepare事实，growth记录原数组范围。facts/demand/activity/claim/install按≤16页run共锁，所有claim仍先于首改、失败按前缀回滚。活动归还按同分片run进行，payload先门外析构；后台每页检查原1ms界、每轮≤16，最终一次idle结算。

原executor只在idle→work通知，完成与下一取头共锁、身份按线程寿命写；monitor仅等待条件变化通知。read事件由原job/finished同锁接续，真实retry仍cancel；epoch原链有界摘取、门外free。descriptor以精确base身份借原共享值，完整相等后免历史搜索，native/alias/generic/recoverable四类producer迁移，不新增layout cache。

recoverable真实retag、history/root世代与retirement/预算接续、effects任意序列及最终root寿命保留；current/G0/oldData/source的真实cut未获同义合并许可。保留理由、替代方案限制和最终free消费者见PLAN及03i。必要标量WorkingVersion仍存在，不能宣称相关版本值全删。生产+687/−338，测试+78/−1，CI+10/−3；生产净增349行，增加有限直接安装/分组路径，未证明源码复杂度净降低。

## 预测删量与实际

8个平衡机制过程（父/候选各4），均19投影更新。以下前三行是projection Stroke内的确定量；其它给范围且不把调度差误算固定删量。[完整分母](quantity-summary.json)包含五阶段与投影阶段分表。

| 项目 | 父→候选 | 判断 |
|---|---|---|
| 旧record整装 | 396→0 | 新target仍安装，不重装未变base及private target保护 |
| private发布前额外snapshot | 132→0 | publish132保持，幂等接纳并锁 |
| descriptor布局历史比较 | 187–191→55–59，精确命中132 | 真map node/共享引用保持 |
| 完整版本投影 / 必要薄事实 | 628–672→0 / 0→640–672 | 不是全部栈上WorkingVersion归零 |
| 独立准备统计锁 | 248–292→0 | 移入demand/activity原锁，失败前缀结算保持 |
| 重复key比较 | 706–848→119–136，新增sort413–501 | 必须扣新增排序；并非所有N很大 |
| growth全表筛选 | 1300–1652→112–140 | 改读原数组本分片范围 |
| facts/install锁 | facts132–152→126–148；install132–136→122–126 | 重试数不同；正常小batch每pass只约10次删量 |
| 全阶段job通知 | 177–192→39–44 | 不是实际OS唤醒数；实际invoke仍168–184量级 |
| 全阶段队列取头锁 | 173–185→启动1 | 完成锁仍每job一次，合于下一取头 |
| 全阶段活动/idle锁 | 408–428→221–239 / 36–38→26 | 真payload、free及公平界没有删除 |
| 空delay cancel通知 | 196–207→0 | arm/ready/lastUse producer在此fixture未触发，不授这些分支删量 |
| epoch取头锁 | 225–275→68–84 | 实际销毁214–261对228–261，后台调度不同；不强配总数差 |

全观测阶段原保护元素仅0–13个，说明“删保护链”在本例本来不是大字节预算。确定删除396次旧record整装，并不意味着获得396份高昂复制价格。标量构造/索引/原容量与owner/provider/proof、真实root/读cut仍在；新增排序与Entry/growth标量也有费用。没有逐项未插桩消融，不给这些项各自ms，不能相加预测大幅收益。

## 安全、结构与负控制

最终同image双架16组**9370 passed、0 failed、0 skipped**。包含Reference、CpuMutation、tile store、manager、painter、low memory、pooler、swapped store。新增16/17页边界、33页负坐标乱序/重复/晚组冲突、长保护链和descriptor值不等断言；其余并发/容量/取消/晚owner/stop复用原组。12路径完成源码与测试落点审查，不宣称性能fixture逐一触发全部路径，也未新增1024/1025每一阈值专门枚举。

结构门、callgraph和工具自测通过。开发build-04的测试字段拼写失败、structure-1索引时源码变化、structure-2旧逐页静态规则、主动中止的diagnostic-v2均保留；说明和修复见PLAN。结构规则现在限定install区域，禁止活动保护被提前消费；runtime库没有因规则修复改变。

Fresh/H4各双架K1/K16、40配对/桶，共640过程，全部正确且各自四桶family通过。固定M5吞吐比的单侧98.75%下界分别为：Fresh `1.5318/1.1936/1.5304/1.2231`，H4 `1.6405/1.5367/1.4957/1.6011`，均≥0.98。这些是受保护控制资格，不能作为本包增量或handoff优势。[Fresh](fresh-summary.json)、[H4](history-summary.json)。

## 未插桩净时间

父、upstream、原a918各20 ABBA块/40配对/80过程，共240过程。固定seed/输入、19updates、8segments/4callbacks、像素/历史/销毁/加载库/退出/reap均通过；**没有工作量偏差**。全部慢值保留。父/原控制100个同名共享依赖hash一致，upstream共享79个依赖hash一致；其余21个是各自构建的Krita库/插件，未冒称字节相同。

20,000次块bootstrap，seed261021，以下均pointwise双侧95%，不授正式多端点family资格。下降为正、回退为负。

| 相对本轮父704 | CPU下降% [95%区间] | wall下降% [95%区间] |
|---|---|---|
| Setup | −0.08 [−1.07,1.03] | −0.08 [−1.67,1.60] |
| Stroke | **3.88 [−0.28,8.82]** | **3.07 [−1.61,8.62]** |
| Undo | 11.45 [5.24,18.06] | 8.33 [1.35,15.46] |
| Redo | 7.33 [1.61,13.11] | 4.81 [−1.22,10.99] |
| Teardown | 9.08 [4.67,13.55] | 2.96 [−2.19,8.11] |
| 五阶段合计，含Setup | **0.20 [−0.81,1.29]** | **0.04 [−1.55,1.69]** |

Stroke CPU配对节省中位0.248ms，但两侧原始中位16.4085/16.3845ms；比值估计受全部配对/尾值影响，不能只选中位绝对差宣称稳定0.248ms收益。父批过程59的31.785ms、原控制批候选过程17的31.085ms均保留。此有限批未确认Stroke或五阶段总CPU净收益，较短后端阶段的正结果也不能抵消。

相对upstream，候选Stroke CPU比1.8558、wall比1.8637；配对额外CPU中位**7.643ms**、wall **3.283ms**。Undo/Redo/Teardown也仍明显慢。相对a918，Stroke CPU下降10.06%[6.55%,12.71%]、wall下降9.31%[5.40%,12.29%]，这是跨先前改动的累计结果，不能计作本包贡献。原控制Setup wall回退2.63%[0.36%,5.34%]，五阶段合计wall回退2.25%[0.04%,4.90%]；完整负结果同样保留。[父](parent-summary.json)、[上游](upstream-summary.json)、[原控制](original-summary.json)。

Teardown wall≤2%：a918对照在本pointwise批通过（候选比上界0.9952）；父对照上界**1.0219**未通过。原控制也没有取得正式family资格。机制阶段metadata峰值约4.5–4.9MB，终点reserved均0，但这些仅4样本，不能当≥25%同义resident分母或长期内存非劣证明。

结论是**数量证据强、Stroke/全生命周期净收益证据不足、主要upstream差额仍在**。本轮没有证明费用抵消的精确分项，也没有证明剩余7.64ms全部属于正常管理成本。下一归因应给必要标量构造/索引与owner/provider/proof、真实业务工作的单位净价，不能继续凭大量小动作删量预报大幅提速。M6/M7/M8仍0/3、正式校准2/20、metadata同义分母和完整CP0仍开放，persistent默认关闭。

## 可复算证据

[EVIDENCE](EVIDENCE.json)、[raw manifest](raw-manifest.json)、[压缩分片索引](raw-evidence-parts.json)保存所有运行库、测试可执行文件、派生源码/对象、命令、原始样本和失败。按分片索引拼接后解包即可复查；直接可读的脚本/摘要和矩阵与原始archive对应，不覆盖以前的证据包。本包停止继续加样，未重新运行108过程覆盖账。
