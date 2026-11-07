# 原型到生产的完整重构任务矩阵

> 生成视图。唯一任务状态在 [PIPELINE_REVIEW_INDEX.json](PIPELINE_REVIEW_INDEX.json) 的 `refactor_execution_matrix`。用 `refactor_tracking.py --render` 更新，勿独立修改本表。

复核日期：2026-10-27；冻结起点 `b0fb5acb04` / 普通库 `698b7d553fd2`。当前工作区身份另见最新实施回执；冻结起点不代表当前量价。

**验收单元是全部22项。** 原33行映射保留；技术分批、局部提交、构建或安全验证均不缩减范围。RF00–RF19全部就绪并冻结完整候选/预测/协议后，才允许RF20联合计价。RF21分别裁决落实与目标，未达目标明确失败，不能称最优。

[填写规范与放行门](REFACTOR_CHECKLIST.md) · [冻结量价差异](prototype-current-reconciliation-r0/RESULT.md) · [当前总方案 V3](PIPELINE_PLAN_V3.md)

**本表保留原型迁移的原22项证据。** 已定原型迁移阶段完成；RF20观察和RF21总体目标仍开放。新主线及其有限工作包由 [V3](PIPELINE_PLAN_V3.md#next-package) 与原索引的 `pipeline_plan_v3` 承接，不用本表20/22表示V3进度。

当前状态由下表给出；“待”表示缺对应完成证据。当前已有17项有限consumer闭包；种子位置描述冻结起点，迁移/删除以同候选重审为准，旧PASS不移授。

## 实际交付与剩余范围

截至2026-10-27：已有 **29批实施回执**；**22/22项已启动**；**20/22项整项验收通过**。未启动：无。

**尚不能给出可信的总完成百分比。** 原型迁移阶段完成；20/22原任务证据维度完成，RF20观察/RF21总体成本证据开放。V3新研究包另记，不以旧矩阵比例表示新主线进度。

**原型优化迁移阶段已验收，可切换主线。** [逐项生产化落实与有意保留差异](refactor-prepricing-settlement-r0/finalization-r1/joint-pricing/PROTOTYPE_MIGRATION_ACCEPTANCE.json)。RF20观察资格、RF21总体成本目标及M6保持独立，不再作为该迁移阶段未完成的依据。

最新回执源摘要 `2d5d1aaf9f27`：[实施报告](refactor-implementation-closure-r0/IMPLEMENTATION.md) · [源/库及验证清单](refactor-implementation-closure-r0/IMPLEMENTATION_MANIFEST.json)。本表的“已落地”指限定子责任，不能替代整项验收或净收益证据。

**2026-10-27回填复核：** 19个限定子责任已完结，1个子责任或汇总组未完结；17项有限consumer闭包（RF01, RF02, RF03, RF04, RF05, RF06, RF07, RF08, RF09, RF10, RF11, RF12, RF13, RF14, RF15, RF16, RF17）保持。上述范围相互交叉，不能换算总完成百分比。

已定原型优化全部迁移并验收；V3以当前C/U写入与setup差额选择下一完整责任，次数、寿命、单价共同定价。

| 待处理前沿 | 类型 | 完成所需证据 |
|---|---|---|
| RF20观察资格与RF21最低成本证据 | 采样已完成；不重复本轮直到通过 | 另有依据的有限观察能力方案；写入/setup责任最小工作及排他服务/内容价格。正式门独立。 |

[本次回填的身份与核验回执](refactor-prepricing-settlement-r0/finalization-r1/joint-pricing/RESULT.md)；本次新增实施批次0，性能样本192。

### 原任务各验收维度

按原状态直接汇总；“进行中”包含已有子责任交付，不表示整项已通过。合同/账本任务的不适用项不计为实施完成。

| 维度 | 已验证 | 进行中 | 待开始 | 不适用 |
|---|---:|---:|---:|---:|
| 设计 | 22 | 0 | 0 | 0 |
| 消费者迁移 | 17 | 0 | 0 | 5 |
| 旧内容删除 | 17 | 0 | 0 | 5 |
| 整项行为合同 | 20 | 2 | 0 | 0 |
| 同版联合计价 | 22 | 0 | 0 | 0 |

**本次方向复核：** 已定原型优化全部迁移并验收；V3以当前C/U写入与setup差额选择下一完整责任，次数、寿命、单价共同定价。 [完整账本与纠偏顺序](PIPELINE_PLAN_V3.md#next-package)。

### 现行子责任完结情况

以下是原任务内部责任的当前投影，仍以原22项状态为权威。有限闭包可涉及相同原任务，不能相加为整项完成率；实现欠账与整包验收欠账分列。

| 子责任 | 原任务 | 当前状态 | 已交付 | 剩余边界 |
|---|---|---|---|---|
| [原记录operation消费与初始接管撤销](refactor-terminal-consumption-r0/IMPLEMENTATION.md) | RF11, RF15, RF16, RF17, RF19 | 限定责任已完结 | 原operation节点观察与一次verified消费/退款、同记录watch、同步入口与接管撤销完整收敛；Failed/Cancelled/Pending/close/orphan同迁。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [Idle期限通知与有界回收](refactor-idle-scheduling-r0/IMPLEMENTATION.md) | RF11, RF12, RF13, RF15 | 限定责任已完结 | 单目标/纯查询/唯一任务准入/仅通知timer/独立退避/有界执行/close恢复同迁；旧混合回调与重复状态删除。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [原记录类别准入、等待与物理终结](refactor-record-retirement-r0/IMPLEMENTATION.md) | RF11, RF15 | 限定责任已完结 | 原record终结从handover到admission/wait/provider/close/实际退款全部接线；栈上尝试结果直达等待，provider accepted不重放，未知handle保留边界。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [普通费用父子事实传递与接受/退款](refactor-fee-facts-r0/IMPLEMENTATION.md) | RF11, RF15 | 限定责任已完结 | 普通父子费用窄事实、parent原slot exact接受、真实partial/retained、取消与一次多域退款14类消费者完成；单一结算政策，旧宽载体/多次退款门删除。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [独立读精确选择与guard/view完整退出](refactor-read-selection-r0/IMPLEMENTATION.md) | RF14, RF15 | 限定责任已完结 | 完整overlay直接用原slot，range/window传cold source；stale同锁一次选，provider锁外/真实install重验和guard/view/lease/最后payer独立退出全部裁决。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [前台descriptor/binding/locator与准确候选失效](refactor-descriptor-facts-r0/IMPLEMENTATION.md) | RF01, RF03, RF08 | 限定责任已完结 | 原descriptor/binding/locator/真实revision消费者有限审查闭合；global过宽失效删除，原稳定location和物理登记复用保持。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [history Work索引与切片退休准备](refactor-history-work-protocol-r0/IMPLEMENTATION.md) | RF13, RF15 | 限定责任已完结 | Work唯一key/有序索引/ready、直接片后轮转与scanAll共用政策，统一dispose；metadata首查slot经原重验复用，inline8效果替代短命付费。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [不可变epoch delta统一存储责任](refactor-epoch-delta-storage-r0/IMPLEMENTATION.md) | RF12 | 限定责任已完结 | 同epoch冲突、dense直接建树/窄解析及不可变delta存储三个有限责任已闭合；三个producer、增量/完整/retry与最终原payer释放同迁，无旧shared/vector协议。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [dense root直接构造及窄事实解析](refactor-dense-root-stream-r0/IMPLEMENTATION.md) | RF12, RF14 | 限定责任已完结 | dense删除内部manifest申请/复制/退款，直接从原不可变输入建最终F节点；成员事实一次取得，true rebase复用原查询校准，所有producer/增量/重试同迁。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [history有界可达性完整查询与cursor寿命](refactor-reachability-window-r0/IMPLEMENTATION.md) | RF12, RF13, RF15 | 限定责任已完结 | 原Work候选→有界epoch遍历→跨片/取消→metadata接受完整同迁；旧三段接口删除，一窗门/core快照3→1、cursor1→0，只有current时注册表定位省1。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [epoch冲突验证与base保活](refactor-epoch-conflict-r0/IMPLEMENTATION.md) | RF12 | 限定责任已完结 | 输入prepareImpl为唯一delta写入者；同一不可变epoch不取base副本、不运行三类冲突自比。真实rebase、derived extent、最终current/revision/state/保护重验保持，所有producer同迁。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [终态facade与原workspace分寿命](refactor-terminal-scope-r0/IMPLEMENTATION.md) | RF02, RF15 | 限定责任已完结 | 已知/未知范围、跨段/跨操作、普通/legacy终态和adapter最后交付迁完；原链提前持registry pin，稳定facade与workspace分寿命。scalable execution不嵌入控制；父压无需销毁facade即可回收，有限consumer闭合。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [来源选择完整有限消费者](refactor-write-selection-r0/IMPLEMENTATION.md) | RF04 | 限定责任已完结 | 四生产入口及直接测试迁完；原delta一次定位、metadata直接填唯一结果，旧投影/getter/转交删除，census 7类闭合。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [原D mutation准备、接受与退出](refactor-original-d-closure-r0/IMPLEMENTATION.md) | RF06, RF07, RF15 | 限定责任已完结 | native/外部/remove/混合D共用原行、真实shard pin、全D接受和锁外终结；旧Detachment/Data/Entry/activity及独立清理删除。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [原D晚容量冲突与局部修复](refactor-mutation-capacity-repair-r0/IMPLEMENTATION.md) | RF06, RF07, RF15 | 限定责任已完结 | 保留顺序/原位置/旧预约，只为真实新槽补容量；成功、拒绝、取消、错误owner/type及晚读者出口有证据，整D重备删除。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [ledger物理节点完整寿命](refactor-backing-storage-lifetime-r0/IMPLEMENTATION.md) | RF01, RF05, RF09, RF15 | 限定责任已完结 | 原physical节点承担唯一identity/索引和最后释放；临时map及逻辑key副本删除。独立退款保留，合并取块原型因额外尾撤下。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [唯一native目标准备→private接受](refactor-private-target-r0/IMPLEMENTATION.md) | RF05 | 限定责任已完结 | 原prepareTarget统一Fresh/reuse/首次及替换alias，准备/登记/验证/接受与拒绝同迁；旧独立编排删除，有限consumer闭合。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [父子预算/storage owner单次付费服务](refactor-storage-service-r0/IMPLEMENTATION.md) | RF09, RF10, RF11 | 限定责任已完结 | 原父子实际容量服务、全allocator/rebind/borrowed、owner detach及最后退款已迁完；slot数组改用同一服务，成功settle/bootstrap预约/特殊cookie删除。正常parent预算门6→4，controller−360B，有限consumer闭合。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [root/history/独立读与退出](refactor-implementation-closure-r0/CONSUMERS.md) | RF12, RF13, RF14, RF15 | 限定责任已完结 | immutable delta/dense与sparse/root服务沿原责任保持；最终current/base/token退出统一原位置解除保护并入队，投机候选路径删除，有限消费者闭合。 history有则建一个Work、重复同记录、拒绝恢复、原cursor/最终销毁完整核对；只有最后root保护解除才全Work复查。虚假root候选不再扩大回收队列。有限消费者闭合。 | 本有限责任计价前的实施/迁移/删除/资源验收均已结清；保留项及未知单价按RF18_ACCOUNT纳入RF20联合价，不重列实现欠项。 |
| [整包联合计价与目标裁决](refactor-prepricing-settlement-r0/finalization-r1/joint-pricing/RESULT.md) | RF00, RF16, RF17, RF18, RF19, RF20, RF21 | 测量完成，资格未闭 | 192过程与11520用例通过；普通CPU和开启态指令整包价已取得。 | RF20观察控制未证；RF21 paid/内容/最低实现证据未闭，正式门保持。 |

### 29批实施的成本回填

各行对应原实施回执；条件数量不等于当前测值。各批净指令收益和差额回收均未计价（null），不填0、不累计旧价。

| 原批次 | 成本关系 | 已替换内容 | 条件数量 | 新增/保留成本 |
|---|---|---|---|---|
| [refactor-implementation-r0](refactor-implementation-r0/IMPLEMENTATION.md) | 直接差额与共同服务 | entry/准入/base/private/overlay位置直接消费；页树控制合入节点并直接构造最终旋转。 | 相同128次页树节点构造时，256→128申请；旋转事件删量另计，不能再套旧节点数重复领取。 | ordinal/位置核验、原node atomic及真实失效fallback；root剩余语义保持。 |
| [refactor-capacity-lifetime-r0](refactor-capacity-lifetime-r0/IMPLEMENTATION.md) | 直接差额 | 原scope/热目录/冷块/execution容量跨段复用；取消慢尾只保留原admission token。 | 串行同规模、≤64KiB、最后引用及时退出且无压力增长时，RF02 348→28、RF03 136→8；合计484→36，少448。 | 值reset/free links、checkout/登记门、空容量收费、压力重建；sealed facade依赖未清。 |
| [refactor-sparse-facts-r0](refactor-sparse-facts-r0/IMPLEMENTATION.md) | 直接差额与共同服务 | 变化类别惰性delta、既有descriptor传递、原Page直接借原D、无历史不造Work。 | 相同surface且原descriptor仍可消费时，descriptor来源128→64；delta构造/复制按0/1/多类，Work删量随实际空事件。 | delta声明+8B、Work控制+16B、mask/copy分支及未知新key查询；无当前净价。 |
| [refactor-history-pipeline-r0](refactor-history-pipeline-r0/IMPLEMENTATION.md) | 直接差额 | metadata直接填Work、epoch版本直接消费；三个read入口复用同窗口history事实。 | 删除两个32版本中间表达及实际V/R转抄；未认领新的paid删量。 | 每root consumer间接调用；小V二分可能更贵；Work/根扫描/尾仍付费。 |
| [refactor-acceptance-pipeline-r0](refactor-acceptance-pipeline-r0/IMPLEMENTATION.md) | 直接差额 | 原基页位置贯穿三种native接受；实际shard分组、共同有界验证/安装及持锁容量终结。 | 相关成功native锁2B+G→2B−S；S仅整D同shard且≤16页为1，跨shard仍claim。 | WriteInput/Selection/BaseInfo各+24B；新增位置传递/核验与持锁长度；外部独立准备待收口。 |
| [refactor-capacity-services-r0](refactor-capacity-services-r0/IMPLEMENTATION.md) | 共同来源，事件时序可能形成差额 | 原CompletionSource内嵌/8槽容量；保留历史后暖槽复用；仅真实新physical组备登记节点。 | 无既存碎片、N个同时存活区间的新source批：N→ceil(max(N−1,0)/8)次overflow申请；48→6。四批48时条件少168，未证实P/K相同区间时序。 | source120→208B；N=2声明合计280→776B，N=48为3960→3616B；碎片/byte-time/压力需裁决。 |
| [refactor-provider-record-r0](refactor-provider-record-r0/IMPLEMENTATION.md) | 共同来源 | 唯一binding直接承接slot索引、physical和retirement ticket；删除独立AllocationMap与两个Allocation类型。 | 成功N次逻辑准备2N→N；若两侧Fresh仍192，各少192次，P−K差不因此减少。 | binding200→288B、strong/weak尾多88B；失败准备顺序/树访问局部性须计回，物理Payload和全局登记未迁。 |
| [refactor-target-protocol-r0](refactor-target-protocol-r0/IMPLEMENTATION.md) | 直接前台协议差额；未获净价 | 目标仅属原结果；删整reuse输入candidate/回写与旧plan契约；native alias原布局，只有实际接受使global revision失效。 | WriteInput384→256B、selection720→592B、原private344B不变；删A/S次整输入复制；首次成功alias少4个metadata入口；拒绝重备反例通过。 | 明确目标引用、成功后的原revision通知、未接受原冷槽清理；generic真实transition/原physical、pin、费用保持。无新owner/状态；输入字节不是malloc或指令价格。 |
| [refactor-physical-record-r0](refactor-physical-record-r0/IMPLEMENTATION.md) | 共同provider物理服务及其前台原事实消费，非同义upstream收益证据 | 原physical记录承担global pin；删map/node_type与第二登记准备；binding同8B借原记录，五类已得对象重定位删除。 | F次同义成功新物理准备2F→F；有parent无reclaim时少6F预算门获取；声明280→288B，observer1912/binding288保持；已知共享alias不重领。 | 原索引pin原子维护、虚销毁/侵入索引、global/multiple observer/snapshot尾；新纯global尾288B实收费且最后pin归零，旧global声明104B，新增184B声明驻留/真实byte-time待裁决。真实锁/serial/像素保持。 |
| [refactor-disposition-ledger-r0](refactor-disposition-ledger-r0/IMPLEMENTATION.md) | 前台metadata/费用接受与终结事实收敛；通用服务影响两侧，未获净价或upstream资格 | 删逐页class门、混合字段和终结预查；原D按真实类筛选，投影消费同锁原位置；detached仅收funded record，effect同锁验证Debt。 | 删除D次提前查询和T次终结预查询；A=E且ΔI=0时条件少D+T入口/门/查找。内部输入144→24B；row320/prepared72/native344/ledger536不变；外部输入每流初始化一次。 | resolver/24B传递及必要输出分支；A实际idle查找/ΔI接受尝试和journal准入，非Active无读者的history→原queue等待转移与资源峰值/byte-time均计回。旧640预算不变。 |
| [refactor-original-d-closure-r0](refactor-original-d-closure-r0/IMPLEMENTATION.md) | 原D mutation准备到终结旧协议完整替换；真正root/lease协议保留，未授最低价或upstream资格 | 删除Detachment generic fallback、生产versions重载、第二Data/Entry、逐页activity、影子失效清单和mutation deferred job；所有输入同一原D接受。 | E外部行第二Entry/activity→0，J旧mutation清理job→0；实际324页同硬限额附加候选65536→96B，原D320/native344/prepared88保持。纯native暖reuse原本无此fallback，不核销13.107M。 | 容量头48→80B，C真实native组616B、S独立外部pin16B、R请求撤下上界32B；原D输入另计，真实key/reader检查、prepare排序及晚重备容量重叠保留。root/lease Entry168→152B；无指令价。 |
| [refactor-mutation-capacity-repair-r0](refactor-mutation-capacity-repair-r0/IMPLEMENTATION.md) | 前台原D准备寿命和局部容量修复；数量/有限硬额证据，无整包净价或upstream资格 | 删整prepare重试、重复retry状态及两套增长政策；同次D保留位置/排序/旧预约，只补真实新槽。初次有序跳过sort。 | retry初始化D、排序及external定位E→0；旧C条预约不重复，新预约只R。实际C1/R1准备2，旧模型3非旧库实测；纯外部满额整prepare拒绝、原repair零分配成功。 | 初次D有序性比较，无序仍sort；修复需求扫描/真正全D验证保留。原C与新R共存，补块80+616*S_R为真实成本，同shard组数可不变；carrier80/row320/native344/prepared88与324页96B不变；生产净+89。 |
| [refactor-backing-storage-lifetime-r0](refactor-backing-storage-lifetime-r0/IMPLEMENTATION.md) | 原ledger物理节点完整寿命与资源反例；有限布局/数量证据，不是前台主差额净价 | 逻辑physical key副本/临时map node准备提取重绑/最后按key重定位删除；原物理记录负责唯一identity/索引和独立退款。 | 2→1取块预报撤下，最终仍2；shared alias物理准备仍0；逻辑key24B/成员→0，最后key查找1→0。原表示同服务1216→1168B，尾272保持，两架均准确退款。 | 生产净+11行；typed allocator/显式deleter替代原map node寿命，裸physical声明208→272已包含原map外部key/hook/allocator。跨provider/registration真实观察、domain/class claims保持。合并块1536B/额外尾1264B方案撤下。 |
| [refactor-write-selection-r0](refactor-write-selection-r0/IMPLEMENTATION.md) | 前台来源选择完整有限责任；同锁重复事实/中间表示删除，非净指令报价 | 原publication owner一次选择delta，metadata填唯一fresh input；删376B投影/三个helper及跨carrier转交/二次清零；四生产和直接硬额consumer迁移。 | publication delta定位1+!显式Removal+需要surface→1；缺省root surface2→1，真实metadata前后观察保持。正常metadata观察1→1，测试3→2不抵生产成本。 | 原selection592/input256及D/private/physical声明不变，1168B/272B付费尾实际保持；0新持久owner/队列，原root/metadata权威和解锁后动态接受仍付费；生产8文件净减33。 |
| [refactor-private-target-r0](refactor-private-target-r0/IMPLEMENTATION.md) | 原native目标准备/接受与拒绝责任整体统一；不授主差额或upstream收益 | 删除独立prepareAliasLocked，原prepareTarget与prepareFreshReplica覆盖Fresh/reuse/首次与替换alias，统一funded拒绝；首次alias在原metadata接受时complete。 | 完整编排2→1，真实首次alias接受/完成metadata门2→1；native checkout source整值复制1→0。物理申请数保持；未将sizeof/门次数换算指令。 | 0新持久owner/队列/字段/付费申请；原声明、1168B/272B物理控制保持。semantic分支、原目标可选快照及末尾费用锁外清理计回，后者可增加Store unlock/relock，不宣称总锁2→1。reuse无新busy条件；父子服务仍待。生产净减89，累计净+831。 |
| [refactor-storage-service-r0](refactor-storage-service-r0/IMPLEMENTATION.md) | 完整实际存储服务替换及slot bootstrap基础删除，不授paid<1M/upstream净价 | 父本地各准入一次，成功atomic live发布；物理free后同源退款，generic普通费用独立；slot同一原payer服务，旧嵌入预约及特殊cookie全删。 | 无拒绝/reclaim的父子实际申请—释放预算门6→4，无parent3→2；成功2次atomic发布、free2次atomic减，每次usage1次atomic读须计回。 | controller1600→1240B，child16/owner72/slot384不变；实际224→144→0，physical1168/272保持。原owner锁/引用、系统申请、slot重叠、公平/跨类/进程约束保留；不凭数量折指令。 |
| [refactor-terminal-scope-r0](refactor-terminal-scope-r0/IMPLEMENTATION.md) | 完整RF02终态容量及稳定facade协议，不授整包最低或净价 | 原预算链提前持scope的一份registry引用；unique时复用whole scope，有公开facade时新操作保留新control并迁原workspace。unlink/handback同门，owned/adapter真实责任保留；公开d不清空。 | 16页实费14960=720控制+14240工作容量；16个完成facade新增15×720=10800，不按14960×16虚构旧实测删量。execution终结结构门2→1，终态offer新加1结构门。 | 0新owner/队列/持久字段；registry pin、offer/转移/回收门与新control计回；多页cold execution由原coalloc1取块改独立2，暖容量可直接复用。当前720B控制不声称最低。64KiB/每Store一spare、physical1168/272保持。 |
| [refactor-epoch-conflict-r0](refactor-epoch-conflict-r0/IMPLEMENTATION.md) | 完整epoch冲突子责任；不授整个RF12最低或净价 | 同锁捕获current与原delta；只有真实rebase取得protected base并运行原三类冲突比较。唯一prepareImpl输入验证、解锁后current/revision/state及install重验保持。 | 相同epoch：base定位/副本1→0，冲突resolve 2C→0、surface S→0、contains 2R→0；真实rebase原检查保持。 | 每candidate一次epoch标量比较；0新owner/队列/持久字段/申请。初始输入验证、不可变快照、输出树和真实失效边界保留。 |
| [refactor-reachability-window-r0](refactor-reachability-window-r0/IMPLEMENTATION.md) | 完整有界可达性时间协议；不是整个RF13或旧6.110M核销 | 同一原epoch门消费current/旧根；仅未完frontier进入原固定槽，完成/失效同门清除，真正取消独立。生产及私有测试无旧兼容分支。 | 一窗epoch门/core快照3→1、cursor建立清理1→0；S窗门S+2→S；只有current根时注册表定位1→0。 | 局部scan值/分流计回；满槽/身份耗尽可能先访问预算内current再拒绝真实continuation，尝试不计零；Work申请次数/候选容量/真根访问不降。0新owner/队列/持久字段/申请。 |
| [refactor-dense-root-stream-r0](refactor-dense-root-stream-r0/IMPLEMENTATION.md) | 完整dense构造/成员计数与窄事实解析；不是整个root最低实现或旧9.538M核销 | 原resolve一次提供Missing/Default/Explicit，原delta持新增摘要；rebase同原两次查询校准。原树与changes/removals直接流式建F个最终节点，不经内部manifest；default解析只借用revision。 | 每dense候选临时寿命1→0、F次中间版本复制→0；只读入口格式调用点4→0、静态函数行148→66/179→103，不是每次退休指令数。 | delta字段+8B、C16实费672→688（+16B沿原寿命）；cursor1048B有界栈/构造递归和计数检查计回。节点128/Root88、真实rebase/输入/保护保持。0新owner/队列/动态申请。 |
| [refactor-epoch-delta-storage-r0](refactor-epoch-delta-storage-r0/IMPLEMENTATION.md) | 完整不可变delta存储责任；不是root节点最低实现或原指令父桶核销 | 原值内嵌strong与一份original payer，三个绑定数组在32KiB内合配，大区段原请求独立extent；全部原值消费者/部分拒绝/最后释放同迁。 | 原1+非空数组数→1+独立extent数；C16 2→1，small全三数组4→1，large可4→4；相同complete重试0→0。 | 原值104B含引用/3位mask；有界布局/extent分支与部分退款计回，C16实际688→624，真实内容/旧新值重叠/冲突保持。盲目合配的32/64KiB跃迁初稿已否决。 |
| [refactor-history-work-protocol-r0](refactor-history-work-protocol-r0/IMPLEMENTATION.md) | 完整history Work索引/切片退休准备；非Work生命周期数量下降或6.109835M核销 | 原Work承担唯一key/index/ready；原slice事实经真revision重验消费，inline8避免小效果付费，large原payer spill。 | S个处理片删S次末find（包括完成格）、T个完成key删T次erase定位、A个scanAll key删A次lower_bound；V selected最多少2V次版本查找；1–8效果寿命1→0。 | Work申请寿命不变，请求1224→1208/实际1536→1536；collector+16B，32槽256B/inline数组1320B，局部栈0x610→0xc30与0x5f8→0xc18。inline32新增chkstk被否决；保护/large spill保持。 |
| [refactor-descriptor-facts-r0](refactor-descriptor-facts-r0/IMPLEMENTATION.md) | 前台原事实/候选相关性责任；非单价最低或旧主差额核销 | global revision与全部写/取消/history通知删除；原C/P覆盖、S跳过事实同锁重验，shared/borrow/matches/exchange同一exact/native解析。 | U次无关相交的额外整包重备U→0，global通知/R个history marker删除；prepare C个临时descriptor shared引用对→0；当前U/S/R未采。 | partial新增C行zip+S个exact/shard检查；P=C含C0调用点直接跳过。Store声明−16B但root实际6304不变；所有保活/权限/真实根目录metadata重验保持，无新owner/付费寿命。 |
| [refactor-read-selection-r0](refactor-read-selection-r0/IMPLEMENTATION.md) | RF14独立读完整有限消费者与已确认同窗重选删除；非每原语机器最低成本 | 原retained slot与cold replica直接传递；同锁stale撤销/选择、共同provider continuation，物理pin/逻辑保护/last-use/最后payer分寿命保持。 | 完整root/overlay冷选择锁3→1，overlay findVersion→原slot；range无窗口冷选择3→1，窗口已选cold source消费端额外三次重选删除；stale3→1。真实provider install重验两边保留。 | warm逻辑锁/refs与paid寿命不增，helper/branch/carrier机器成本仍未知；原capture376/guard104/window2304等布局保持，static函数迁入cold工作不折算动态指令。 |
| [refactor-fee-facts-r0](refactor-fee-facts-r0/IMPLEMENTATION.md) | RF11共享费用传递/接受/取消/退款有限子责任；不是完整事件次数或最低单价 | 共享费用32B域事实；parent原slot保存signed接受，exact/partial/retained共用同一结算政策；多域退款一次门，root跳过child初始化。 | 两optional完整delta声明544→64B；k个负域纯退款parent锁/通知k→1，k=0保持0；正预约/接受次数不变，controller1240/reservation32/slot384保持。 | 模板两个机器函数体新增代码体积计回；真实parent/local门、原slot增长/限额/公平性保持。arm64帧912→128B、x86显式824→72B不折退休指令；无新paid寿命。 |
| [refactor-record-retirement-r0](refactor-record-retirement-r0/IMPLEMENTATION.md) | 原RF11/RF15原记录类别准入与退休完整有限责任 | 原记录贯穿交接/准入/等待/物理退款；旧queue准入编排删除，全部真实转类共用ledger政策，等待直接消费尝试结果。 | 无grant的非Debt准入查找2→0/ledger门2→1；Debt重试1→0且门仍1；已知Idle交接1→0、预算等待2→0、最终释放1→0；handle-only入口保持1。生产record888/queue416/physical272B不变。 | 生产5文件+176/−89净+87；私有入口/栈上结果分支/原身份检查、动态claim与投影/预算/provider/回调成本保留，无新持续字段或paid寿命。条件Idle剪枝尚未生产迁移。 |
| [refactor-idle-scheduling-r0](refactor-idle-scheduling-r0/IMPLEMENTATION.md) | 原RF11/12/13/15 Idle期限观察、通知与执行完整有限责任 | 单目标/纯查询/原task有界执行及明确完整退出；timer仅通知，唯一准入、完成重判与close同迁，删除重复状态及第二wait条件。 | 目标/schedule/monitor他页业务移交E→0但worker仍处理E；timer Store门1→0，已有job时timer独立root保活1对→0；每pass最多16。 | Idle-only增加原History task、schedule统一通知门、worker重判及可能空pass；真实费用/queue/provider及排队尾保留。生产+170/−117净+53；声明Store+context减120B，实际root6304保持，净价未知。 |
| [refactor-terminal-consumption-r0](refactor-terminal-consumption-r0/IMPLEMENTATION.md) | 原RF11/15 operation终态责任及初始接管撤销 | 原record同窗准入与准备；原节点观察、一次verified消费与最终结算；所有writer/rollback/wait/close同迁。 | 正常已登记立即成功attempt ledger窗口7→3、返回后operation查找4→0、registry验证2→1；非动态全进程价格。 | 移交/prepared、普通writer所有权及证据判定计回；orphan预约释放不结束托管。生产+209/−173净+36；record888/queue416/root实际6304保持，动态claim/budget/provider/queue/最终free仍在。 |
| [refactor-implementation-closure-r0](refactor-implementation-closure-r0/IMPLEMENTATION.md) | RF12/13/15最后逻辑保护解除与实际回收事件 | 三保护出口共用原iterator卸保护/入队；root drain只消费真正退役记录，Work/读/退出有限消费者核完。 | 仍为current或有snapshot/base保护的root入队/后续空查变零；实际最终释放数不变。Work申请量不变；实际命中和净价未知。 | 生产2文件+41/−50净−9；无新增字段/付费寿命/门/owner。原真实保护读取/cursor/tree drain保留；相同B内可回收更多死root，实际后台时间/保留时长仍须计回。 |

### 四个互斥来源的条件预算

| 旧来源 | 责任 | 冻结P次数 | 条件P次数 | 条件删量 |
|---|---|---:|---:|---:|
| `operation_scope_execution_entries_directories` | RF02 | 348 | 28 | 320 |
| `operation_cold_page_blocks` | RF03 | 136 | 8 | 128 |
| `epoch_page_roots` | RF12 | 256 | 128 | 128 |
| `descriptors` | RF08 | 128 | 64 | 64 |
| **小计** | 互斥来源 | **868** | **228** | **640** |

**640/1260=50.8%只表示旧申请差额的条件来源预算，不是完成率或指令收益。** 620只等于1260−640的条件局部算式，不是当前残差、下界、或指令收益。不能据此更新P2976/K1716；新增/其它变化及真实次数尚未核验。

前提：仅核对四个互斥的旧P来源组；不把旧栈当当前实测；沿用4个Store、16页/16cuts/68段；像素/cut/权限与旧比较工作量不变；RF02/RF03容量≤64KiB、串行最后引用及时退出、无增长/额外活借用/压力重建；root仍128次节点构造；descriptor仍有64次可以消费相同surface布局的原对象；本小计仅替换列出的来源；其它变动、新成本、旋转与实际completion时序另账。

共同provider在两侧Fresh仍192时各少192次；不改变相对差额。completion四批48仅条件少168，P/K实际并发/历史碎片尚未证明相同，不能一起代入当前paid总数。

### 当前处理优先级

| 原任务 | 执行前沿 | 证据及边界 | 退出条件 |
|---|---|---|---|
| RF21 | V3-01：公开写入工作生成与保留服务责任账 | 写入+setup占arm64 H0/H1 CPU差额75.90%/65.69%；机制排行和净删量未知。 | 同义必要工作、实际事件、完整服务及竞争解释足以选择一个有限替代责任。 |
| RF20 | V3-02：按选择需要补有界计价能力 | 旧12控制未证观察等价；不因此阻止不依赖leaf价格的合法整责任A/B。 | 事前冻结新判别，得到结论或明确未决；不扩旧样本至通过。 |

资源裁决：

- RF16, RF17, RF19：六资源有限裁决已结清。同候选资源见finalization-r1/RESOURCE_DECISIONS.json。 本轮复用，未发现新违约，不重开为计价前置。 未来出现具体新反例才回原owner修复。

原责任分组的当前退出状态如下；每项恰好归属一组，已结清范围也保留，未缩减原22项。

| 责任组 | 任务 | 退出状态与条件 |
|---|---|---|
| 已结清的原责任范围 | RF00, RF01, RF02, RF03, RF04, RF05, RF06, RF07, RF08, RF09, RF10, RF11, RF12, RF13, RF14, RF15, RF16, RF17, RF18, RF19 | RF00–19实施/合同与同候选整包价已接；不代表各项必要最低价或总目标通过。 |
| 观察校准未证 | RF20 | 当前192过程已结案，不扩样求通过；能力不足与普通净价分别保留。 |
| paid/内容/最低实现证据不足 | RF21 | 以写入/setup的最小必要工作和完整排他价格解释剩余C/U差额；正式门独立。 |

| 项 | 累计已落地的子责任 | 仍须完成 |
|---|---|---|
| [RF00](#rf00) | 29批/19限定责任/11有限闭包；原实现未完结聚合组收口，剩余资源/全包验收组。原22项/33行保持。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF01](#rf01) | 原descriptor/binding/locator/真实revision消费者有限审查闭合；global过宽失效删除，原稳定location和物理登记复用保持。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF02](#rf02) | 已知/未知范围、跨段/跨操作、普通/legacy终态和adapter最后交付迁完；原链提前持registry pin，稳定facade与workspace分寿命。scalable execution不嵌入控制；父压无需销毁facade即可回收，有限consumer闭合。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF03](#rf03) | 原ColdPage只保存真实本代值；稳定D容量与终态facade分寿命保持；descriptor/binding/locator逐consumer完成保留/替换裁决。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF04](#rf04) | 唯一来源选择有限consumer保持闭合；alias入口随独立编排删除归原prepareTarget，四种业务入口仍消费同一原publication/metadata selection。旧376B投影/getter/转交保持删除。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF05](#rf05) | 当前native目标准备→provider/物理/费用→private接受与拒绝完整编排统一；Fresh/reuse/首次与替换alias共用原prepareTarget，旧独立alias方法/拒绝政策删除。首次alias原子complete，有限consumer闭合。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF06](#rf06) | 原D为唯一mutation输入，按真实shard分组并保留原page位置；旧Detachment、versions入口、Data/Entry和独立activity删除。初次有序跳过排序，晚容量冲突不重建整D。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF07](#rf07) | native/外部/remove/混合D共用all-D claim、安装、取消和锁外终结；同shard≤16页共享有界窗口。容量拒绝保留原准备，只为真实新增槽补预约。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF08](#rf08) | 内部原identity/stamp与真正外部proof边界保持；descriptor准确相关失效替换global marker，provider锁外/真实解锁重验保留。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF09](#rf09) | 已闭合actual存储服务保持；ordinary父子费用同义合同与实际storage独立收费再次同验，无新owner/paid寿命。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF10](#rf10) | 原completion/provider/physical有限迁移保持；其原allocator全部消费新实际容量协议，child/owner尾无字段增长，actual224→144→0。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF11](#rf11) | 普通类别、共用投影/直接Idle及handoff排除已移交logical；物理alias动态变化保留，准入与operation同窗。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF12](#rf12) | immutable delta/dense与sparse/root服务沿原责任保持；最终current/base/token退出统一原位置解除保护并入队，投机候选路径删除，有限消费者闭合。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF13](#rf13) | history有则建一个Work、重复同记录、拒绝恢复、原cursor/最终销毁完整核对；只有最后root保护解除才全Work复查。虚假root候选不再扩大回收队列。有限消费者闭合。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF14](#rf14) | 完整overlay直接用原slot，range/window传cold source；stale同锁一次选，provider锁外/真实install重验和guard/view/lease/最后payer独立退出全部裁决。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF15](#rf15) | 前批终态/接管撤销和原独立尾保持；三类root保护退出与最终drain统一。root/Work/读/退出无本组已知未迁旧路，有限消费者闭合。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF16](#rf16) | root三出口、history producer/worker/read/close、独立树与最终provider消费者核完；固定449检查通过。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF17](#rf17) | 旧queueRoot/unlinkUnprotected和drain中的受保护候选跳过删除；此前436旧协议接线检查保持。 当前候选消费者/删除登记重核完成（计价前结清回执）。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF18](#rf18) | 仍为current或有snapshot/base保护的root入队/后续空查变零；实际最终释放数不变。Work申请量不变；实际命中和净价未知。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF19](#rf19) | 两架各4431，共8862/0/0；四种root退出次序、旧库真实反例与原全部固定合同通过。 2026-10-27：原计价前三组欠账有限验收结清，详见finalization-r1/PREPRICING_ACCEPTANCE.json。 | 本项实施/同源合同和整包联合价已验收；无独立子责任因果价，不能宣称最优。RF20/21开放证据另列。 |
| [RF20](#rf20) | 完整P/C/U及实际测量binary、22项条件预算、192过程固定协议和强制严格门启动器已冻结；未开始确认样本。 | 见本项观察控制/成本目标未证结论；不重复已迁完消费者。 |
| [RF21](#rf21) | 未启动；实施、成本目标、同语义upstream及M6资格分开，有限行为总数不升格。 | 见本项观察控制/成本目标未证结论；不重复已迁完消费者。 |

## 整项验收状态

| 项 | 责任 | 原节点 | 依赖 | 设计 | 迁移 | 删除 | 行为 | 联合计价 |
|---|---|---|---|---|---|---|---|---|
| [RF00](#rf00) | 冻结生产语义、原型差异和完整实施边界 | A/B/C/D/E/F/G/H/I | — | 已证 | 不适用 | 不适用 | 已证 | 已证 |
| [RF01](#rf01) | 稳定页位置与物理登记归回原owner | B/C/D | RF00 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF02](#rf02) | 操作控制与热entry/目录跨段容量寿命 | A/B | RF00, RF01 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF03](#rf03) | 私有Page与ColdPageSet只按真实变化构造 | B/H | RF01, RF02 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF04](#rf04) | 来源选择、布局和原entry位置一次取得后传递 | A/B | RF01, RF02 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF05](#rf05) | 目标checkout、计划与private接受合为一次事实交接 | B/C/D | RF01, RF03, RF04 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF06](#rf06) | 原D直接承担publication准备与实际shard分组 | D/E | RF04, RF05 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF07](#rf07) | 全D原子接受消费稳定位置和一次claim结果 | D | RF01, RF06 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF08](#rf08) | provider验证、内部identity和真实外部proof分界 | D/E | RF00, RF05, RF07 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF09](#rf09) | 付费存储的申请、收费、退款统一最小粒度 | C/H | RF01, RF02, RF03 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF10](#rf10) | Fresh物理容量与稳定登记的整个寿命 | B/C/D/H | RF01, RF05, RF09 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF11](#rf11) | 费用投影与handoff只处理实际状态变化 | C/E | RF05, RF07, RF09, RF10 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF12](#rf12) | canonical root与历史可见性按真实变化更新 | F | RF01, RF06, RF07, RF08 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF13](#rf13) | history调度与H0后台差额按实际失效事件收敛 | F/H | RF12 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF14](#rf14) | capture/read一次选择与独立保活最小表示 | G | RF01, RF07, RF12 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF15](#rf15) | cancel/close/retirement/弱尾使用唯一终结政策 | H | RF03, RF05, RF07, RF09, RF10, RF13, RF14 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF16](#rf16) | 所有公共入口与adapter消费同一核心协议 | A/E | RF02, RF04, RF05, RF06, RF07, RF08, RF12, RF14, RF15 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF17](#rf17) | 旧实现、旧恢复与多代协议全量删除审计 | I | RF01, RF02, RF03, RF04, RF05, RF06, RF07, RF08, RF09, RF10, RF11, RF12, RF13, RF14, RF15, RF16 | 已证 | 已证 | 已证 | 已证 | 已证 |
| [RF18](#rf18) | 完整净预算、分配来源与指令桥对账预案 | I | RF00 | 已证 | 不适用 | 不适用 | 已证 | 已证 |
| [RF19](#rf19) | 整包消费者与失败/资源合同验证 | I | RF00, RF01, RF02, RF03, RF04, RF05, RF06, RF07, RF08, RF09, RF10, RF11, RF12, RF13, RF14, RF15, RF16, RF17, RF18 | 已证 | 不适用 | 不适用 | 已证 | 已证 |
| [RF20](#rf20) | 完整候选的机制账与未插桩联合计价 | I | RF00, RF01, RF02, RF03, RF04, RF05, RF06, RF07, RF08, RF09, RF10, RF11, RF12, RF13, RF14, RF15, RF16, RF17, RF18, RF19 | 已证 | 不适用 | 不适用 | 进行中 | 已证 |
| [RF21](#rf21) | 整包落实、目标达成和M6资格分别裁决 | I | RF20 | 已证 | 不适用 | 不适用 | 进行中 | 已证 |

## 量价账的唯一归属

以下P/K为冻结起点生产与同资源服务适配原型，均非最新C价格；K不是upstream，也缺完整生产语义。H1申请2976/1716、差1260是原来源账；来源合法不证明数量或单价最优。当前净价见本表联合结果，不把旧差额写成当前。

| 来源组 | P次数 | K次数 | 差 | 主责任务 |
|---|---:|---:|---:|---|
| `capture` | 64 | 64 | +0 | RF14 |
| `descriptors` | 128 | 0 | +128 | RF08 |
| `epoch_model_other` | 64 | 0 | +64 | RF12 |
| `epoch_page_roots` | 256 | 0 | +256 | RF12 |
| `fresh_provider_5` | 960 | 960 | +0 | RF10 |
| `fresh_retirement_and_physical_2` | 384 | 384 | +0 | RF10 |
| `history_setup` | 16 | 0 | +16 | RF13 |
| `history_work` | 128 | 0 | +128 | RF13 |
| `kernel_fixed_arrays` | 0 | 28 | -28 | RF18 |
| `kernel_stable_records` | 0 | 192 | -192 | RF18 |
| `metadata_registration_capacity_and_setup` | 288 | 0 | +288 | RF01 |
| `operation_cold_page_blocks` | 136 | 0 | +136 | RF03 |
| `operation_scope_execution_entries_directories` | 348 | 0 | +348 | RF02 |
| `publication_other` | 36 | 0 | +36 | RF12 |
| `read_setup` | 24 | 0 | +24 | RF14 |
| `root_prepared_proof_vector_growth` | 44 | 0 | +44 | RF12 |
| `shared_services_and_store_setup` | 100 | 88 | +12 | RF09 |
| **总计** | **2976** | **1716** | **+1260** | 单一归属，相关任务协作 |

冻结起点P/K指令桥（M）：`21.130214 观察前台差 − 0.518070 模型偏差 − 0.271907 其它线程差 = 20.340236 普通全进程差`。stage/seal差6.539/6.568M，paid差2.679M。模型偏差不能摊平；旧H0其它线程差6.109835M不是当前C/U后台价，也不据此重开已验收消费者。

相同stage/seal桶可对应多个任务，但总账只计一次。P内部细分价与另一批粗分净差不能混加。原型20.340M不是可兑现收益预测；K paid2.051M也没有达到完整paid<1M目标。

## 原33行反向覆盖

| 原节点 | 原行 | 本包任务 |
|---|---|---|
| A | T01.1, T01.2, T01.3, T01.4, T02.1 | RF00, RF02, RF04, RF16 |
| B | T02.2, T02.4, T03.1, T03.2, T03.3, T04.1 | RF00, RF01, RF02, RF03, RF04, RF05, RF10 |
| C | T05.1, T05.2 | RF00, RF01, RF05, RF09, RF10, RF11 |
| D | T04.2, T04.3, T04.4, T04.5, T04.6 | RF00, RF01, RF05, RF06, RF07, RF08, RF10 |
| E | T04.7, T04.10, T04.11, T06.3 | RF00, RF06, RF08, RF11, RF16 |
| F | T02.3, T04.8, T04.9, T06.2 | RF00, RF12, RF13 |
| G | T04.12, T06.1 | RF00, RF14 |
| H | T07.1, T07.2, T07.3 | RF00, RF03, RF09, RF10, RF13, RF15 |
| I | T08.1, T08.2 | RF00, RF17, RF18, RF19, RF20, RF21 |

## 逐项排查卡

各卡都要沿入口→唯一事实/owner→接受→失败/取消→最后使用者填写证据。种子位置是冻结起点，不要求重构后保留旧符号。

<a id="rf00"></a>
### RF00 · 冻结生产语义、原型差异和完整实施边界

**原行：** T01.1, T01.2, T01.3, T01.4, T02.1, T02.2, T02.4, T03.1, T03.2, T03.3, T04.1, T05.1, T05.2, T04.2, T04.3, T04.4, T04.5, T04.6, T04.7, T04.10, T04.11, T06.3, T02.3, T04.8, T04.9, T06.2, T04.12, T06.1, T07.1, T07.2, T07.3, T08.1, T08.2。**差异：** operation, write_base, private_target, seal_acceptance, storage, fees, root, read, exit。

**代码起点：** [KisPageStore.cpp:1725](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:1725) `KisPageMutationSession::borrowExecution`；[KisPageStore.cpp:2005](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2005) `KisPageMutationExecution::writeFinalRect`；[KisPageStore.cpp:694](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:694) `struct ColdPageSet`；[KisPageStore.cpp:906](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:906) `void finishSegmentLocked`；[KisPageWriteCoordinator.cpp:2149](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2149) `KisMutationStorageOwner::allocate`；[KisPageWriteCoordinator.cpp:2177](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2177) `KisMutationStorageOwner::releaseLiveCharge`；[KisPagePublicationCoordinator.cpp:207](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:207) `class KisPagePublicationCoordinator::KisPreparedMutationCommit`；[KisPagePublicationCoordinator.cpp:636](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:636) `KisPreparedMutationCommit::tryInstall`；[KisTiledDataManagerPageStoreBackend.cpp:967](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:967) `KisTiledDataManagerPageStoreBackend::prepareMutationBatch`；[KisTiledDataManagerPageStoreBackend.cpp:1340](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1340) `KisTiledDataManagerPageStoreBackend::readBytes`；[KisImageEpochReferenceModel.cpp:190](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:190) `PageRoot makePageRoot`；[KisImageEpochReferenceModel.cpp:1309](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:1309) `KisImageEpochReferenceModel::prepareCommit`；[KisPageStore.cpp:3347](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3347) `KisCapturedReadView::readResidentPageImpl`；[KisPageStore.cpp:3559](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3559) `KisPageStore::captureReadRange`；[KisPageRetirementQueue.cpp:594](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp:594) `KisPageRetirementQueue::process`；[KisPageRetirementQueue.cpp:479](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp:479) `KisPageRetirementQueue::prepareTask`；[KisPageStoreCpuMutationTest.cpp:8359](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8359) `KisPageStoreCpuMutationTest::sharedIdleWarmQuantities()`；[KisPageStoreCpuMutationTest.cpp:8409](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8409) `KisPageStoreCpuMutationTest::nativeFinalSlotReplacement()`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | K提前知道固定页集；P公共入口unknown-range。K缺完整root/外部proof/独立尾，整Kernel busy会使provider回调读旧cut自等待，拒绝重试语义亦不等价。 |
| 目标形态 | 以原operation/result/D和原资源owner为共同协议；公开cut、exact读、原子接受和独立寿命不变。借鉴稳定事实与工作生成率，逐条列出必须保留的生产增量，不照搬Kernel全局互斥或固定数组假设。 |
| 权威/寿命/锁 | 每个事实保留原权威；列出owner锁、scope/execution门、metadata shard锁、provider锁外窗口及回调的真实锁序。锁/寿命地图须在实施前审定。 |
| 真实消费者种子 | beginMutation已知/未知范围及追加borrow；native/generic/adapter与外部proof；provider callback、retirement worker、close后escaped guard |
| 失败/取消/退出 | 区分接受前可取消、容量变化可重备、provider终态拒绝、已接受后的退出欠账；不得把所有拒绝改成重试。 |
| 旧→新→同批删除 | 列出K-only假设→生产替代；禁止引入整Store busy作为统一协议；原33行和本22项组成固定范围，技术分批不得删除或降为可选 |
| 数量与计价约束 | 冻结4 Store、16页、16cuts及2页/8cuts、H0/H1、1088写/68seal/64capture/1024读的各自端点；内部次数是结果，不硬锁为原型计数。 |
| 验收反例/证据 | 合同/可见点/失败分类逐项有源码消费者；原33行、9类差异和全部22项无遗漏；回调重入与独立尾不能依赖Kernel整体存活 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-27）：** 29批/19限定责任/11有限闭包；原实现未完结聚合组收口，剩余资源/全包验收组。原22项/33行保持。 [本批证据](refactor-implementation-closure-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=不适用；旧实现删除=不适用；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf01"></a>
### RF01 · 稳定页位置与物理登记归回原owner

**原行：** T02.2, T02.4, T03.1, T03.2, T03.3, T04.1, T05.1, T05.2, T04.2, T04.3, T04.4, T04.5, T04.6。**差异：** private_target, seal_acceptance。

**代码起点：** [KisPageMetadataCoordinator.cpp:4477](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:4477) `KisPageMetadataCoordinator::acceptPrivateTarget(`；[KisPageMetadataCoordinator.cpp:1890](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:1890) `void acceptNativeResult`；[KisPageStore.cpp:1402](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:1402) `KisPageMutationSession::Private::prepareTarget(`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 物理backing/binding已复用，metadata登记、私有接纳和页位置事实仍在多个阶段重新建立；P metadata登记/容量/初始化288次。 |
| 目标形态 | 在原metadata/physical记录内维持稳定位置；稳定容量身份与每代写权限/transaction stamp分离。原编辑行携带位置和失效条件，真实变化才重建，不新设影子Record目录。 |
| 权威/寿命/锁 | metadata shard拥有位置与记录；physical owner拥有实际容量；只在各自锁保护且代次匹配时消费事实。最后外部reader/alias退出前不得复用身份。 |
| 真实消费者种子 | prepareTarget/acceptPrivateTarget；prepareMutation/installMutation；capture/read、cancelPrivateResult、retirement |
| 失败/取消/退出 | 晚reader/ABA、页remove/default、并发transaction和关闭使哪些事实失效必须列全；纯容量复用不授写权限。 |
| 旧→新→同批删除 | 删除原owner间仅用于重新定位/复制同一登记事实的状态；每个残留登记点说明真实首次建立或失效事件及消费者 |
| 数量与计价约束 | logical physical key24B/成员→0；最后成员key查找1→0；准备临时map/提取/重绑删除。两架实际原表示1216→当前1168B，物理尾272保持；288旧登记组不是可删288次。 |
| 验收反例/证据 | 稳定地址与authority代次独立验证；新增/移除/重用页与晚reader失败反例；同一物理寿命只登记/最终退款一次 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-26）：** 原descriptor/binding/locator/真实revision消费者有限审查闭合；global过宽失效删除，原稳定location和物理登记复用保持。 [本批证据](refactor-read-selection-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf02"></a>
### RF02 · 操作控制与热entry/目录跨段容量寿命

**原行：** T01.1, T01.2, T01.3, T01.4, T02.1, T02.2, T02.4, T03.1, T03.2, T03.3, T04.1。**差异：** operation。

**代码起点：** [KisPageStore.cpp:1725](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:1725) `KisPageMutationSession::borrowExecution(`；[KisPageStore.cpp:906](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:906) `void finishSegmentLocked`；[KisPageWriteCoordinator.cpp:2574](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2574) `KisMutationWriteSet::reserveKnownTargetCount(`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 主格每段scope/execution/entry/两目录各分配一次，共68×5+8=348；known-range coalloc不覆盖本unknown-range公共主入口。 |
| 目标形态 | 原operation负责真实活动与准入，已收费的热行/目录容量按可复用寿命保留；scope/execution只持各自必要权利。未知范围增量增长和并发借用共享同一规则，不能只优化已知范围。 |
| 权威/寿命/锁 | 沿原Store/operation权威复用；scope取消不等于容量销毁；execution权限独立，禁止把可逃逸guard嵌入可能先死的对象。检查scope→owner锁序。 |
| 真实消费者种子 | beginMutation/borrowExecution追加与并发借用；writeBytes、fill/copy范围入口；adapter retainAdmission、scope析构 |
| 失败/取消/退出 | 失败准入不发布半个entry；seal/cancel释放逻辑权利，close或真实容量回收才退款；保留并发scope隔离。 |
| 旧→新→同批删除 | 替换finishSegmentLocked中无条件丢弃已收费writes容量的生命周期；清理只为段内重新建目录服务的分配/恢复分支；已知/未知范围不得保留两套核心协议 |
| 数量与计价约束 | 通常无公开终态facade时whole scope原址复用；有facade则新control保持稳定身份并迁W，资源从M份workspace收敛为ΣC+Wspare（active另计）。当前C720/W14240；E个execution少E结构门，T个terminal新增T门。cold多页execution1→2次申请须计回，640旧条件来源不重算。 |
| 验收反例/证据 | 已知/未知范围及多个borrow均迁移；无写/空range不造私有目标；跨段复用不增加无界驻留或修改公开cut |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-26）：** 已知/未知范围、跨段/跨操作、普通/legacy终态和adapter最后交付迁完；原链提前持registry pin，稳定facade与workspace分寿命。scalable execution不嵌入控制；父压无需销毁facade即可回收，有限consumer闭合。 [本批证据](refactor-read-selection-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf03"></a>
### RF03 · 私有Page与ColdPageSet只按真实变化构造

**原行：** T02.2, T02.4, T03.1, T03.2, T03.3, T04.1, T07.1, T07.2, T07.3。**差异：** private_target, exit。

**代码起点：** [KisPageStore.cpp:694](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:694) `struct ColdPageSet`；[KisPageStore.cpp:1048](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:1048) `Page *ensurePage`；[KisPageStore.cpp:964](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:964) `void releaseStorageLocked`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 冻结r6每段2个ColdPage块、共136次；当前容量已复用。Page仍构造当代事实及稳定对象引用；仅凭clear/reconstruct不足证明基础重建，对引用/定位维护的可回收净价仍待。 |
| 目标形态 | 原D只保存本代必需的变化与接受事实；可复用管理容量由原受控owner持有，稳定物理事实不放入每代Page重建。无变化的claim不构造Page，最后实际使用后才析构临时成员。 |
| 权威/寿命/锁 | scope gate保护逻辑行；provider/binding析构仍在owner锁外，活动保护持续到实际free/退款。可逃逸尾不得借用短命workspace。 |
| 真实消费者种子 | ensurePage/prepareTarget；sealImpl/finishSegmentLocked；releaseStorageLocked/cancelLocked/adapter delivery |
| 失败/取消/退出 | 中途失败回滚已构造行且不重复退休；取消后允许合法下一操作，压力回收实际容量一次。 |
| 旧→新→同批删除 | 删掉按seal无条件重建的Page块/计划路径；原Page字段逐一分类稳定事实、当代变化、可推导值；后者消除；删除被新寿命消除的局部恢复/备用缓存 |
| 数量与计价约束 | 条件H1冷块2S=136→2L=8，少128；实际Page值仍逐代构造，稳定字段仍须原owner收敛。不能把容量删量当整个Page责任的指令节省。 |
| 验收反例/证据 | 稀疏、no-op、空claim无额外构造；所有失败/析构锁外安全；增长与最后释放相等且压力有界 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-26）：** 原ColdPage只保存真实本代值；稳定D容量与终态facade分寿命保持；descriptor/binding/locator逐consumer完成保留/替换裁决。 [本批证据](refactor-read-selection-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf04"></a>
### RF04 · 来源选择、布局和原entry位置一次取得后传递

**原行：** T01.1, T01.2, T01.3, T01.4, T02.1, T02.2, T02.4, T03.1, T03.2, T03.3, T04.1。**差异：** write_base, operation。

**代码起点：** [KisPageStore.cpp:2005](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2005) `KisPageMutationExecution::writeFinalRect(`；[KisPageWriteCoordinator.cpp:2894](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2894) `KisPageWriteCoordinator::prepareWriteBaseLocked(`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | P write_base内部约2.378M；当前选择、source/layout与transaction解析仍比K直接Record关系更重，但并非全部可删。 |
| 目标形态 | 真实入口完成key→原entry定位，向后携带ordinal、原source与layout。相同保护窗口消费原事实；跨真正的版本/锁外失效边界才检查必要stamp，不按key重走整条解析。 |
| 权威/寿命/锁 | 选择由publication/transaction原权威决定；owner锁内事实与锁外像素比较分开。保留来源被更新、外部proof或布局变化的失效条件。 |
| 真实消费者种子 | borrowExecution/writeFinalRect；prepareWriteBaseLocked/prepareTarget；generic读比较与native pin失败路径 |
| 失败/取消/退出 | 失效只重新取得受影响事实，不把单页变化升级成整scope事务；真实读失败和参数拒绝保留。 |
| 旧→新→同批删除 | 检索并删除已持entry/slot后再按key解析的调用链；同锁事实不再层层get/validate/register；只保留真实失效边界的重新定位 |
| 数量与计价约束 | 原publication delta定位1+!显式Removal+需要surface→1（不包含真实epoch/root/metadata不同权威）；缺省首次登记root surface2→1，metadata前后观察保留。376B中间投影及其转交/清零删除，selection592/input256不变。正常生产metadata观察原本1，不领取旧诊断3→2。 |
| 验收反例/证据 | 同锁事实复用有代码证明；解锁后source变化/默认页/部分写保持；copy/no-op像素工作量不偷减 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-26）：** 唯一来源选择有限consumer保持闭合；alias入口随独立编排删除归原prepareTarget，四种业务入口仍消费同一原publication/metadata selection。旧376B投影/getter/转交保持删除。 [本批证据](refactor-read-selection-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf05"></a>
### RF05 · 目标checkout、计划与private接受合为一次事实交接

**原行：** T02.2, T02.4, T03.1, T03.2, T03.3, T04.1, T05.1, T05.2, T04.2, T04.3, T04.4, T04.5, T04.6。**差异：** private_target, write_base。

**代码起点：** [KisPageStore.cpp:1402](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:1402) `KisPageMutationSession::Private::prepareTarget(`；[KisPageMetadataCoordinator.cpp:4477](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:4477) `KisPageMetadataCoordinator::acceptPrivateTarget(`；[KisPageOwnerLedger.cpp:1800](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:1800) `KisPageOwnerLedger::prepareBackingHandoff(`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | prepareTarget内部约7.419M、private metadata接纳0.904M；含真实资源工作，不能整体按可删价认领。 |
| 目标形态 | 原记录checkout直接产生本代可写结果和最小接受事实，Fresh与复用只是真实容量来源差异，后续原D协议相同；布局/归属已知值直接消费。 |
| 权威/寿命/锁 | physical独占与metadata权限分开，在原handoff/claim接受点建立资格；无全Store busy，provider验证保持锁外。 |
| 真实消费者种子 | prepareTarget/acceptPrivateTarget；Fresh provider、idle checkout与handoff；write completion、seal/cancel |
| 失败/取消/退出 | 晚reader/last-use/共享拒绝在写入前安全选Fresh或拒绝；不得先修改再回退。取消只结算实际发生的容量/权限。 |
| 旧→新→同批删除 | 删除目标已被接纳后下游再次建通用计划/登记的路径；Fresh/复用不再复制一整套后续发布协议；旧计划失效后的恢复对象随失败源删除 |
| 数量与计价约束 | 原完整native编排2→1；真实首次alias的metadata接受/完成门2→1；native checkout source整值复制1→0。实际物理工作/申请保持；末尾费用锁外清理可增加Store窗口，净指令未测，不能领取旧7.419M或0.904M父桶。 |
| 验收反例/证据 | native/generic/late-reader/Fresh拒绝端点一致；成功替换无额外payload/copy/retirement；阶段新增成本纳入stage/paid/handoff各自互斥桶 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-26）：** 当前native目标准备→provider/物理/费用→private接受与拒绝完整编排统一；Fresh/reuse/首次与替换alias共用原prepareTarget，旧独立alias方法/拒绝政策删除。首次alias原子complete，有限consumer闭合。 [本批证据](refactor-read-selection-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf06"></a>
### RF06 · 原D直接承担publication准备与实际shard分组

**原行：** T04.2, T04.3, T04.4, T04.5, T04.6, T04.7, T04.10, T04.11, T06.3。**差异：** seal_acceptance。

**代码起点：** [KisPagePublicationCoordinator.cpp:1818](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1818) `KisPagePublicationCoordinator::preparePagePublicationLocked(`；[KisPageMetadataCoordinator.cpp:2794](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2794) `KisPageMetadataCoordinator::prepareMutation(`；[KisPageStore.cpp:2800](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2800) `KisPageMutationSession::sealImpl(`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 统一了D表示仍逐代重填acceptance、分组排序、superseded/authority/disposition。publication prepare/accept各约0.750/0.755M为P内部价。 |
| 目标形态 | 原D携带已知选择和原位置；只为真实失效项准备新容量。相同成员/顺序不反复排序，动态成员时只维护必要分组；adapter消费同一已接受变化。 |
| 权威/寿命/锁 | publication持当前选择权威，metadata持shard位置。分组是遍历视图，不能成为第二份业务状态或另造完整D。 |
| 真实消费者种子 | sealImpl/preparePagePublicationLocked；prepareMutation/publicationRows；adapter prepare/acceptSelection |
| 失败/取消/退出 | 接受前所有可能分配先完成，失败不改变已可见cut；成员/权限真变化才使相应准备失效。 |
| 旧→新→同批删除 | 删掉原D已具有事实的再次投影/复制/宽初始化；删掉固定成员情况下重复排序/重建容器；清理仅由被删prepare失败产生的重试状态 |
| 数量与计价约束 | 同次capacity retry初始化/排序/external定位=0；初次有序输入跳过sort，无序增加一次有序性判断后仍sort。原carrier80/row320/native344/prepared88不变；原324页候选96B保持。 |
| 验收反例/证据 | 原D identity/ordinal始终唯一；不遗漏remove/default/generic行；空变化不建通用准备事务 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-25）：** 初次有序D直接消费；容量冲突不重新初始化、排序或定位external page，已有预约、pins和引用容量留在原carrier。 [本批证据](refactor-mutation-capacity-repair-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf07"></a>
### RF07 · 全D原子接受消费稳定位置和一次claim结果

**原行：** T04.2, T04.3, T04.4, T04.5, T04.6。**差异：** seal_acceptance。

**代码起点：** [KisPageMetadataCoordinator.cpp:2935](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2935) `bool KisPageMetadataCoordinator::installMutation(`；[KisPageMetadataCoordinator.cpp:1890](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:1890) `void acceptNativeResult`；[KisPageMetadataCoordinator.cpp:3075](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:3075) `KisPageMetadataCoordinator::finishMutation(`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | metadata install约2.126M、prepare约0.792M；必须保留all-D检查，但当前价格未证明是最小实现。 |
| 目标形态 | 第一阶段按真实触及shard验证并claim，第二阶段直接消费保存的page/slot/disposition安装；只有晚读者造成的容量失效才重备该部分。保留两阶段原子语义，不重复key定位或再解释输入。 |
| 权威/寿命/锁 | shard锁与publicationClaim保留跨阶段稳定性；原prepared/current行保存一次接受结果，不另造通用事务。 |
| 真实消费者种子 | installMutation native/generic混合D；acceptNativeResult/replacementSlot；finishMutation/DeferredPublicationCleanup |
| 失败/取消/退出 | claim中途失败全部释放；只有实际capacity变化可重备；参数/identity失败不变可重试。成功安装后不允许报成未执行。 |
| 旧→新→同批删除 | 删除claim成功后重复定位/验证同一未失效事实；删除native再生成通用Entry的残余及仅服务旧失败的cleanup；保留外部lease确有生命周期的准备，不强删真实消费者 |
| 数量与计价约束 | C条原预约保持，只补R条新native预约；新增组S_R及80+616*S_R补块，外部R=0时零分配。C=1/R=1旧模型3而当前断言2；同shard可能不减少组字节，真实全D重验保持。 |
| 验收反例/证据 | 全D原子性/晚reader容量重备/混合输入；安装阶段零分配；拒绝无半安装且claim清理仅一次 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-25）：** 全D容量拒绝保留原准备，只有实际新native槽追加预约；初次/修复共用Group::prepare。错owner/type/未修复安装终态消耗，一次修复再冲突按原退出。 [本批证据](refactor-mutation-capacity-repair-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf08"></a>
### RF08 · provider验证、内部identity和真实外部proof分界

**原行：** T04.2, T04.3, T04.4, T04.5, T04.6, T04.7, T04.10, T04.11, T06.3。**差异：** seal_acceptance。

**代码起点：** [KisPageOwnerLedger.cpp:2465](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:2465) `KisPageOwnerLedger::validatePrivateWrite(`；[KisPageOwnerLedger.cpp:2576](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:2576) `KisPageOwnerLedger::validatePreparedPage(`；[KisPageMetadataCoordinator.cpp:4715](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:4715) `KisPageMetadataCoordinator::ownsCpuProof(`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | provider/private验证P约1.119M，原型也有provider验证；删除旧proof契约不证明所有验证必要或所有可删。 |
| 目标形态 | 内部直接消费原private identity与真实动态变化；外部proof仅在实际信任边界解析/验证一次。provider仍锁外调用且可回调读取旧cut，验证失败保持生产原分类。 |
| 权威/寿命/锁 | provider唯一决定资源有效性；metadata/publication唯一决定版本可接受性。两种权威不可混同，也不层层重复验证相同事实。 |
| 真实消费者种子 | validatePrivateWrite/validatePreparedPage；ownsCpuProof/revokeCpuProof；provider callback、native/generic seal |
| 失败/取消/退出 | provider终态拒绝取消原D；回调不等自身busy；真实异步状态变化仍须再验，不用版本缓存绕过。 |
| 旧→新→同批删除 | 删除内部路径转external proof再查回的包装；逐一列出保留验证的真实失效事件；旧retry/descriptor附属状态无消费者即删 |
| 数量与计价约束 | 首次成功native alias删4个通用metadata descriptor入口，不默认少4个分配；private layout本地拒绝不推进global revision，成功接受仍通知。若无并发default/restore候选，不预支整套重备收益。 |
| 验收反例/证据 | 回调读旧cut不会自等待；provider拒绝副作用与返回值保持；proof伪造/过期/revoke/外部lease语义保持 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-26）：** 内部原identity/stamp与真正外部proof边界保持；descriptor准确相关失效替换global marker，provider锁外/真实解锁重验保留。 [本批证据](refactor-read-selection-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf09"></a>
### RF09 · 付费存储的申请、收费、退款统一最小粒度

**原行：** T05.1, T05.2, T07.1, T07.2, T07.3。**差异：** storage, exit。

**代码起点：** [KisPageWriteCoordinator.cpp:2238](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2238) `KisBackingBudgetController::allocateStorage(`；[KisPageWriteCoordinator.cpp:2316](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2316) `void kisFreeMutationStorage(`；[KisMutationStorage_p.h:124](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisMutationStorage_p.h:124) `class KisMutationStorageAllocator`；[KisPageWriteCoordinator.cpp:2196](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2196) `KisMutationStorageOwner::detach`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | P前台paid4.730M，K2.051M，两者均高于完整服务<1M目标；合法申请源不证明父子准入/结算/退款的现行单价必要。 |
| 目标形态 | 原容量owner传递实际layout/物理大小/付费责任；同一真实变化由原预算权威一次接受，复用已受控容量不重新申请/结算。模板rebind、process账和最后payer使用相同协议，不加影子账本。 |
| 权威/寿命/锁 | 父/本地预算原锁域、shared child和process容量仍是权威；明确原子准入/回滚顺序与动态限额失效。不同锁不凭猜测合并。 |
| 真实消费者种子 | KisMutationStorageAllocator所有rebind/派生实例；allocateStorage/kisFreeMutationStorage；owner detach/weak tail、budget usage/configureLimits与waiter |
| 失败/取消/退出 | 分配失败退款、父准入成功本地失败、限额收紧、溢出、跨类变化、detached owner最终free完整保留；不向close后台转嫁收费。 |
| 旧→新→同批删除 | 删除已携带大小/owner后的重复layout/native-size/process查询；删除同一容量被多层重复登记/结算的实现；保留必要全局约束，纯减少用量不无条件使成功事实失效 |
| 数量与计价约束 | 无拒绝/reclaim的成功parent存储寿命预算门6→4，无parent3→2；成功原子发布/free原子减/usage读计回，controller1600→1240B。child/owner及actual224B尾不增；完整paid<1M未证。 |
| 验收反例/证据 | 账与真实分配/释放一致、无未收费常驻缓存；父子/动态限额/压力拒绝/最后weak退款；含后台与final drain后的完整服务净价 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-26）：** 已闭合actual存储服务保持；ordinary父子费用同义合同与实际storage独立收费再次同验，无新owner/paid寿命。 [本批证据](refactor-fee-facts-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf10"></a>
### RF10 · Fresh物理容量与稳定登记的整个寿命

**原行：** T02.2, T02.4, T03.1, T03.2, T03.3, T04.1, T05.1, T05.2, T04.2, T04.3, T04.4, T04.5, T04.6, T07.1, T07.2, T07.3。**差异：** storage, private_target, exit。

**代码起点：** [KisPageStore.cpp:694](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:694) `struct ColdPageSet`；[KisPageStore.cpp:906](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:906) `void finishSegmentLocked`；[KisPageWriteCoordinator.cpp:2149](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2149) `KisMutationStorageOwner::allocate`；[KisPageWriteCoordinator.cpp:2177](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2177) `KisMutationStorageOwner::releaseLiveCharge`；[KisPagePublicationCoordinator.cpp:207](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:207) `class KisPagePublicationCoordinator::KisPreparedMutationCommit`；[KisPagePublicationCoordinator.cpp:636](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:636) `KisPreparedMutationCommit::tryInstall`；[KisPageRetirementQueue.cpp:594](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp:594) `KisPageRetirementQueue::process`；[KisPageRetirementQueue.cpp:479](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp:479) `KisPageRetirementQueue::prepareTask`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 两侧192 Fresh各5 provider+2 retirement/physical申请，共1344；相同数量不是最少必要次数证明。 |
| 目标形态 | 按同生共死且同预算域的原容量责任安排管理表示，允许合并实际可合的记录；独立尾或不同退款点保持分离。真实payload数量由语义决定，不用合并计数隐藏成本。 |
| 权威/寿命/锁 | provider、physical node、retirement record各原owner和最后使用者逐项列出；存储合并不能延长payload收费或破坏owner销毁顺序。 |
| 真实消费者种子 | Fresh创建/registration/binding；metadata交接、handoff/idle保留；retirement queue/provider observer/weak tail |
| 失败/取消/退出 | 任一构造失败只回滚已发生部分；退休拒绝由原退休责任推进；不为普通写新增无条件等待。 |
| 旧→新→同批删除 | 每个5+2组成项映射最小事实、同生共死条件及原位最终归属；清理可合寿命的重复owner/ref/申请；不能合的项必须保留真实消费者和代价证据 |
| 数量与计价约束 | F次同义成功新物理准备，原Payload node/global record 2F→F；真实共享已知tile alias保持。新原pin索引、虚销毁计回；两架声明280→288B、新纯global尾288B实收费/最后pin退款，旧global声明104B，新增尾驻留仍待。P/K同F共同下降，不抵1260或20.340M。 |
| 验收反例/证据 | 同义物理峰值与压力进度；每项独立尾和最终退款；改变申请粒度后实际字节/碎片/保留时长入账 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-25）：** 原completion/provider/physical有限迁移保持；其原allocator全部消费新实际容量协议，child/owner尾无字段增长，actual224→144→0。 [本批证据](refactor-storage-service-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf11"></a>
### RF11 · 费用投影与handoff只处理实际状态变化

**原行：** T05.1, T05.2, T04.7, T04.10, T04.11, T06.3。**差异：** fees。

**代码起点：** [KisPageOwnerLedger.cpp:553](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:553) `bool prepareProjectedChanges`；[KisPageOwnerLedger.cpp:1614](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:1614) `KisPageOwnerLedger::prepareBackingChanges(`；[KisPageOwnerLedger.cpp:1876](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:1876) `KisPageOwnerLedger::commitBackingHandoff(`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 真实替换选择的执行删量已测，但N对当前R的整体结构净简化未证明；不能拿B中被删除而R不存在的预检/续期作生产结构收益。结构原则采纳、生产暂留R，按原全管线事件/资源/净预算推进。 |
| 目标形态 | 从真实类别/域变化导出最小delta；原D直接提交给原ledger。handoff独占/预算责任保留，不因中间表示重造而反复投影；改变状态的失效与纯退款单调性分开。 |
| 权威/寿命/锁 | 原ledger/budget权威决定分类与费用；投影缓存仅由真实变化失效，动态限额/总额/跨域不能略。 |
| 真实消费者种子 | prepare/finish/commitProjectedChanges；prepareBackingChanges/prepareBackingHandoff/commitBackingHandoff；cancel/retire/idle与小规模输入 |
| 失败/取消/退出 | 费用预留失败无副作用、接受后只结算一次，取消按实际状态退回；空delta不得触发通用准备。 |
| 旧→新→同批删除 | 全量检索由表示变化误触发的投影/空delta事务；宽费用结构/遍历按实际变化粒度收敛；保留真实handoff准备与独占，不能降保护冒充删量 |
| 数量与计价约束 | 无grant的非Debt准入查找2→0/ledger门2→1；Debt重试1→0且门仍1；已知Idle交接1→0、预算等待2→0、最终释放1→0；handle-only入口保持1。生产record888/queue416/physical272B不变。 净价未知；原两页额外8投影未核销。 |
| 验收反例/证据 | 合同、当前生产结构净简化、运行影响独立裁决；结构价值不要求正CPU收益。准确区分B→N与R→N以及入库年龄和候选选择；保留真实费用、独占与进度，不以计数或CPU跨零代替证明。；空/负delta、限额变化和跨域总额；同义handoff成功/拒绝/取消费用完整 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-27）：** 普通类别、共用投影/直接Idle及handoff排除已移交logical；物理alias动态变化保留，准入与operation同窗。 [本批证据](refactor-terminal-consumption-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf12"></a>
### RF12 · canonical root与历史可见性按真实变化更新

**原行：** T02.3, T04.8, T04.9, T06.2。**差异：** root。

**代码起点：** [KisPagePublicationCoordinator.cpp:1152](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1152) `KisPagePublicationCoordinator::commitInputLocked(`；[KisImageEpochReferenceModel.cpp:1309](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:1309) `KisImageEpochReferenceModel::prepareCommit(`；[KisImageEpochReferenceModel.cpp:190](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:190) `PageRoot makePageRoot`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | H1 root/history/publication组528次；commit差0.940M，H0差9.538M。K缺完整生产root义务，不能以其0作下界。 |
| 目标形态 | 原root事务直接消费已接受D和原位置；只更新真正变化的持久节点/选择，保留历史cut、remove/default/rebase和多transaction。避免从原D重新组全量proof/manifest。 |
| 权威/寿命/锁 | epoch/reference model是历史权威，publication是当前选择权威；快照strong/weak和异步析构寿命保持，不为速度合成一把全局锁。 |
| 真实消费者种子 | commitInputLocked/prepareCommit/applyPageRootDelta；resolve/abort、root retain/weak；history collector与generic外部commit |
| 失败/取消/退出 | 提交冲突不改变旧root；成功后清理失败不能重报未提交；abort只释放该事务责任。 |
| 旧→新→同批删除 | 删除已接受D后再建等价proof/manifest/选择的路径；清理真实不再发生的root准备失败与恢复对象；保留结构共享所需节点并说明最少重建边界 |
| 数量与计价约束 | 此前冲突/dense/窄事实删量保持；delta 1+非空数组→1+独立extent，C16 2→1/688→624B，small三数组4→1；large最多仍4。原值104B/原payer/mask与布局费用计回，内容/旧新并存/持久节点保持。 |
| 验收反例/证据 | 多transaction/rebase/remove/default/history/undo可见性；H0与H1同义工作均覆盖；root节点/引用/析构增减和峰值全账 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-27）：** immutable delta/dense与sparse/root服务沿原责任保持；最终current/base/token退出统一原位置解除保护并入队，投机候选路径删除，有限消费者闭合。 [本批证据](refactor-implementation-closure-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf13"></a>
### RF13 · history调度与H0后台差额按实际失效事件收敛

**原行：** T02.3, T04.8, T04.9, T06.2, T07.1, T07.2, T07.3。**差异：** root, exit。

**代码起点：** [KisPageHistoryCollector.cpp:74](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp:74) `KisPageHistoryCollector::requestKeyLocked(`；[KisPageHistoryCollector.cpp:108](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp:108) `KisPageHistoryCollector::collectSliceLocked(`；[KisPageHistoryCollector.cpp:319](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp:319) `KisPageHistoryCollector::scheduleLocked(`；[KisPageHistoryCollector.cpp:384](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp:384) `KisPageHistoryCollector::waitForIdleLocked(`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | history work H1 128/H0 1088次；H0进程减前台的参照差额约6.110M尚未独立归因。 |
| 目标形态 | 原collector按真实失效key/epoch推进，已排队的同一责任不重复建Work或扫描。必要后台工作保留，完成端点含最终drain；不把前台工作搬到尾部换局部收益。 |
| 权威/寿命/锁 | 原collector/retirement拥有各自欠账，队列只表达待推进事实；owner锁与worker退出顺序显式列明。 |
| 真实消费者种子 | requestKeyLocked/collectAfterEpochChangeLocked；collectSlice/collectPass/scheduleLocked；stopAutomaticWakeups/waitForIdle/clear/drain |
| 失败/取消/退出 | 拒绝时从已完成阶段继续；若合同需要无新输入进度，现有worker保证；close后不能丢失仍有holder的责任。 |
| 旧→新→同批删除 | 删除重复排队、重复初始化Work和同事实全量扫描；删除被统一阶段消除的重复终结序列；真正保留的任务记录最终消费者 |
| 数量与计价约束 | S个处理片删S次末find（包括完成格）、T个完成key删T次erase定位、A个scanAll key删A次lower_bound；V selected最多少2V次版本查找；1–8效果寿命1→0。 原一窗可达性预算保持；Work申请次数未降、collector+16B/栈及large spill计回。 |
| 验收反例/证据 | 事件→排队→处理→真实释放可追溯；无新输入时必要进度和close竞争；H0/H1后台CPU/指令与尾部资源单列 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-27）：** history有则建一个Work、重复同记录、拒绝恢复、原cursor/最终销毁完整核对；只有最后root保护解除才全Work复查。虚假root候选不再扩大回收队列。有限消费者闭合。 [本批证据](refactor-implementation-closure-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf14"></a>
### RF14 · capture/read一次选择与独立保活最小表示

**原行：** T04.12, T06.1。**差异：** read。

**代码起点：** [KisPageStore.cpp:3559](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3559) `KisPageStore::captureReadRange(`；[KisPageStore.cpp:3347](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3347) `KisCapturedReadView::readResidentPageImpl(`；[KisPageReadCoordinator.cpp:1024](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadCoordinator.cpp:1024) `KisPageReadCoordinator::releaseCapturedView`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 两侧capture申请均64，但capture差0.661M、read/unpin差0.431M；单分配已完成不代表读协议最优。 |
| 目标形态 | capture保存exact选择和必要独立保活，后续原视图直接定位并取得读guard；只有真实miss/外部来源走通用解析，不重复构建选择或扩大保护集合。 |
| 权威/寿命/锁 | read view可独立于Store，guard可独立于view；原read/metadata owner维持必要pin，不能用Kernel整体保活替代。 |
| 真实消费者种子 | captureReadRange/readResidentPageImpl；groupNativeRefs/releaseCapturedView；readBytes/generic/raw lease/escaped guard |
| 失败/取消/退出 | 部分capture失败仅回滚本次retains；close后读与最后guard释放合法，取消/alias不复用被保护页。 |
| 旧→新→同批删除 | 删除已有exact selection后再次遍历选择/定位；合并确实同寿命的释放表示，保留独立guard尾；已完成单capture合配不重复计功 |
| 数量与计价约束 | 完整root/overlay冷选择锁3→1，overlay findVersion→原slot；range无窗口冷选择3→1，窗口已选cold source消费端额外三次重选删除；stale3→1。真实provider install重验两边保留。 warm机器单价仍未知；布局与paid寿命不增，真实物理pin/保护规模不减少。 |
| 验收反例/证据 | 旧cut、并发capture、generic miss与partial failure；view/guard/Store任意合法销毁顺序；资源峰值及最后payer无转嫁 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-26）：** 完整overlay直接用原slot，range/window传cold source；stale同锁一次选，provider锁外/真实install重验和guard/view/lease/最后payer独立退出全部裁决。 [本批证据](refactor-read-selection-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf15"></a>
### RF15 · cancel/close/retirement/弱尾使用唯一终结政策

**原行：** T07.1, T07.2, T07.3。**差异：** exit, storage。

**代码起点：** [KisPageStore.cpp:3836](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3836) `KisPageStore::closeSession(`；[KisPageRetirementQueue.cpp:594](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp:594) `KisPageRetirementQueue::process`；[KisPageWriteCoordinator.cpp:2207](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2207) `KisMutationStorageOwner::stopAllocations`；[KisPageWriteCoordinator.cpp:2213](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2213) `KisMutationStorageOwner::deref`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | H1 close差1.186M；独立尾不能照抄整Kernel保活，新增复用容量又可能延长收费。 |
| 目标形态 | 原记录保存已发生事实，cancel/worker/close/晚通知推进同一终结规则；准入停止与最后实际free分离，最后payer只退款一次。没有消费者的容量在合法边界释放。 §10.100原record直接推进内嵌operation，一次verified消费和原成员结算；接管撤销/正常退休/最终析构分别保留授权，不新增总状态机。 |
| 权威/寿命/锁 | Store活动、provider activity、retirement、storage owner weak尾各有真实寿命，不能为新用途扩大旧计数含义。析构/回调不带错误锁。 |
| 真实消费者种子 | cancelLocked/finishSegmentLocked/closeSession；retirement process/provider observer callbacks；owner stopAllocations/detach/deref、root drain/escaped view |
| 失败/取消/退出 | 真实退休拒绝由原记录续推，不重放发布或handoff；停止后拒绝新申请，已有最后尾仍可退款；唤醒仅在有真实等待者时必要。 |
| 旧→新→同批删除 | 删除多入口复制的整套终结/重排/结算；删除仅为已消失prepare失败存在的recovery状态；清理可复用容量的销毁点，不能留无界持有 |
| 数量与计价约束 | 每次实际effect/detached原record接受，原2次ledger门/定位→1次take；effect只同锁取必要Debt类别，detached用funded record事实。等待/拒绝后的真实再观察保留；非Active场景等待转移须计回，不报CPU。 §10.100第28批已落实源码预算：正常已登记、无拒绝/claim等待且立即Succeeded时ledger窗口7→3，返回后operation查找4→0、终态验证2→1；非动态实测，其他锁/退款与失败另计。 |
| 验收反例/证据 | 拒绝→重试→close→晚通知完整链；weak/read/provider晚释放与并发teardown；完整drain后应释放项归零，合法保留项有最后消费者；已移交logical不能被普通class/handoff writer复活；generic operation释放不能消费退休node；初始接管回滚不调用provider、不转Debt，原record可重新准备；其退账不冒充物理free；同步/worker/显式process/effect/close/orphan全部消费同一终结实现，accepted Pending不再准入或重发 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-27）：** 前批终态/接管撤销和原独立尾保持；三类root保护退出与最终drain统一。root/Work/读/退出无本组已知未迁旧路，有限消费者闭合。 [本批证据](refactor-implementation-closure-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf16"></a>
### RF16 · 所有公共入口与adapter消费同一核心协议

**原行：** T01.1, T01.2, T01.3, T01.4, T02.1, T04.7, T04.10, T04.11, T06.3。**差异：** operation, seal_acceptance, read。

**代码起点：** [KisPageStore.cpp:1725](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:1725) `KisPageMutationSession::borrowExecution`；[KisPageStore.cpp:2005](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2005) `KisPageMutationExecution::writeFinalRect`；[KisTiledDataManagerPageStoreBackend.cpp:967](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:967) `KisTiledDataManagerPageStoreBackend::prepareMutationBatch`；[KisTiledDataManagerPageStoreBackend.cpp:1340](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1340) `KisTiledDataManagerPageStoreBackend::readBytes`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 主格公共unknown-range不同于已有known-range优化；只在夹具或native路径迁移会继续保留旧管线。 |
| 目标形态 | write/fill/copy/iterator/raw/generic等真实入口表达意图，原核心完成相同选择→目标→D→接受→退出；adapter只准备真实交付并安装一次，不再拼第二事务。 |
| 权威/寿命/锁 | manager/adapter原gate覆盖真实可见性，业务责任不下放为新持久状态；consumer清单包含override/callback/template和配置分支。 |
| 真实消费者种子 | KisTiledDataManagerPageStoreBackend全部mutation/read入口；sealForAdapterDelivery/sealedAdapterChanges；tiles3 manager、iterator/raw访问、copy/fill及external proof |
| 失败/取消/退出 | adapter准备失败不安装，接受后交付失败不重放已接受D；真实兼容入口允许保留边界转换，不保留整套旧协议。 |
| 旧→新→同批删除 | 按旧协议关键字和实际callgraph全量搜索生产消费者；迁完每个入口同时删其旧拼装/桥接/回滚；代码标记只表示待迁，不能算消费者已迁移 |
| 数量与计价约束 | 入口覆盖率分母为实际caller清单；暂无全量完成证据，不能用当前4个seed冒充全部入口。 |
| 验收反例/证据 | 已知/未知、追加borrow、native/generic/adapter均使用目标协议；零未解释旧caller/旧字段写者；像素/中间可见点/失败语义逐类保持 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-27）：** root三出口、history producer/worker/read/close、独立树与最终provider消费者核完；固定449检查通过。 [本批证据](refactor-implementation-closure-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf17"></a>
### RF17 · 旧实现、旧恢复与多代协议全量删除审计

**原行：** T08.1, T08.2。**差异：** operation, write_base, private_target, seal_acceptance, storage, fees, root, read, exit。

**代码起点：** [KisPageStoreCpuMutationTest.cpp:8359](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8359) `KisPageStoreCpuMutationTest::sharedIdleWarmQuantities()`；[KisPageStoreCpuMutationTest.cpp:8409](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8409) `KisPageStoreCpuMutationTest::nativeFinalSlotReplacement()`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | r6八项旧契约删除已有证据，但每段重建等算法差距仍在；不能继承旧PASS作为本轮完成。 |
| 目标形态 | 对RF01–16逐项形成旧符号/字段/状态/分支→最终归属→实际删除或必要保留的闭包。逐路径而非仅名称搜索，确认无改名包装和并存旧协议。 |
| 权威/寿命/锁 | 业务权威仍唯一；迁移标记随实际完成删除。临时桥只有真实尚存consumer且有明确删除条件才能存在，整包放行前必须处理。 |
| 真实消费者种子 | 全部生产声明/定义/调用、测试支持与派生allocator；callback/worker/close后的consumer；结构门/callgraph脚本及旧断言 |
| 失败/取消/退出 | 被删失败来源对应恢复也须删；保留业务拒绝要指出实际来源，内部不变量破坏不得包装成业务重试。 |
| 旧→新→同批删除 | 每条删除登记必须给零命中查询或语义替换diff；每项保留必须给合同、真实消费者、成本与限制；旧r6证据仅作基线，不填本轮完成证据 |
| 数量与计价约束 | 生产/测试/生成物增删分列；净减行数不代替协议/工作减少，净增长须说明真实保证和更直接替代比较。 |
| 验收反例/证据 | 33行全覆盖、9差异类闭包；无临时桥/未迁caller/无理由保留；源码身份一致的删除证明 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-27）：** 旧queueRoot/unlinkUnprotected和drain中的受保护候选跳过删除；此前436旧协议接线检查保持。 [本批证据](refactor-implementation-closure-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=已证；旧实现删除=已证；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf18"></a>
### RF18 · 完整净预算、分配来源与指令桥对账预案

**原行：** T08.1, T08.2。**差异：** operation, write_base, private_target, seal_acceptance, storage, fees, root, read, exit。

**代码起点：** [KisPageStoreCpuMutationTest.cpp:8359](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8359) `KisPageStoreCpuMutationTest::sharedIdleWarmQuantities()`；[KisPageStoreCpuMutationTest.cpp:8409](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8409) `KisPageStoreCpuMutationTest::nativeFinalSlotReplacement()`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 申请来源1260差额已100%核对，不等于指令必要性100%；前台模型偏差−0.518070M，H0后台差约6.110M未解释。 |
| 目标形态 | 每项先给语义最小事实→可实现数量模型→新增/删去动作→条件净预算，统一互斥桶，合上普通前台/后台/全进程桥。当前价、参照差、可回收净价分列。 |
| 权威/寿命/锁 | 本JSON为任务状态权威，原ACCOUNT/COUNT_ACCOUNT为历史测量权威；新预算仅引用，不重造第二套实测来源。 |
| 真实消费者种子 | RF01–16数量模型与RF09服务转嫁；普通P/K与后续parent/candidate；same-semantics upstream、内容分母与正式门 |
| 失败/取消/退出 | 未知价保留null；实现删量变小须在新样本前修订预测并保留旧值。不得强制均摊残差或扣掉失败样本。 |
| 旧→新→同批删除 | 删除重复认领父子桶的预算；保留原型缺语义所需的新增责任预算；冻结整包预测后才开始最终确认 |
| 数量与计价约束 | 条件模型P=7F+7N+R+1092，K=8F+R+116仅用于16页特定阶梯；2页另列。候选模型必须事前给出，不能照搬K1716为硬下界。 2026-10-24仅列四组条件P申请868→228/少640；1260−640=620是局部预算式，不是当前残差；两侧共同provider少192不核销差额，completion实际并发另计。 |
| 验收反例/证据 | 所有分配组有且仅有一个负责项；exclusive桶、观察偏差、后台桥完整列出；paid<1M/管理内容比/upstream差额各自分母与未证项清楚 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-27）：** 仍为current或有snapshot/base保护的root入队/后续空查变零；实际最终释放数不变。Work申请量不变；实际命中和净价未知。 [本批证据](refactor-implementation-closure-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=不适用；旧实现删除=不适用；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf19"></a>
### RF19 · 整包消费者与失败/资源合同验证

**原行：** T08.1, T08.2。**差异：** operation, write_base, private_target, seal_acceptance, storage, fees, root, read, exit。

**代码起点：** [KisPageStoreCpuMutationTest.cpp:8359](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8359) `KisPageStoreCpuMutationTest::sharedIdleWarmQuantities()`；[KisPageStoreCpuMutationTest.cpp:8409](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8409) `KisPageStoreCpuMutationTest::nativeFinalSlotReplacement()`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 旧11764项等结果只覆盖原冻结源码；新寿命/权限/原D改动不能沿用其PASS。 |
| 目标形态 | 整包结构完成后，对本次受影响的实际合同闭包做验证；中途构建和安全验证允许，但不产生整体实施/性能通过资格。 |
| 权威/寿命/锁 | 按原安全/结构门与当前92§6.1，记录源码树、实际库、工具链、架构和失败进程；保持真实预算与安装零分配要求。 |
| 真实消费者种子 | CpuMutation/Reference/PhysicalClaim及实际受影响业务测试；allocator rebind/provider callback/worker；H0/H1、小页/大页、冷暖、压力/限额/独立尾 |
| 失败/取消/退出 | 构造真实拒绝或说明替代边界为何同义；所有未通过、hang/UE和未退出进程保留，不以总通过数掩盖。 |
| 旧→新→同批删除 | 验证旧测试中的过期实现断言已按真实合同修正；结构门删旧符号要求而不恢复旧路径；新增测试检验真实反例，不镜像新helper |
| 数量与计价约束 | 不在本项采普通性能价格；资源含峰值、容量slack、保留时长/最后释放，未测维度保持欠账。 |
| 验收反例/证据 | 消费者迁移/旧实现删除证据完备；回调/晚reader/冲突/失败/close/drain全部覆盖；最终候选树与加载库一致、环境无未处理异常 |
| 待定设计/停止条件 | 实施和当前同源合同已验收，整包净价已接；未知的单项因果单价不填0或宣称最优。 |

**实施进度（2026-10-27）：** 两架各4431，共8862/0/0；四种root退出次序、旧库真实反例与原全部固定合同通过。 [本批证据](refactor-implementation-closure-r0/IMPLEMENTATION.md)

**本项状态：** 设计=已证；消费者迁移=不适用；旧实现删除=不适用；行为验证=已证；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf20"></a>
### RF20 · 完整候选的机制账与未插桩联合计价

**原行：** T08.1, T08.2。**差异：** operation, write_base, private_target, seal_acceptance, storage, fees, root, read, exit。

**代码起点：** [KisPageStoreCpuMutationTest.cpp:8359](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8359) `KisPageStoreCpuMutationTest::sharedIdleWarmQuantities()`；[KisPageStoreCpuMutationTest.cpp:8409](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8409) `KisPageStoreCpuMutationTest::nativeFinalSlotReplacement()`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 既有原型距离是受限参照，不能替代新候选对冻结parent的因果收益。 |
| 目标形态 | 只在RF00–19全部达到放行条件后冻结整包运行；先机制/资源，再未插桩parent/candidate，P/K用于解释，upstream只用于同语义对照。 |
| 权威/寿命/锁 | 独立冻结输入、库、端点、顺序块、样本量、排除/失败/停止规则和区间；与build/其它benchmark串行。 |
| 真实消费者种子 | H0/H1主格及事前规模检查；前台/后台/setup/close/final drain；内容、paid全寿命、root与真实业务端点 |
| 失败/取消/退出 | 安全回归先修复，再冻结新批次；不追加样本到过门、不事后换端点、无计数/时间混算。 |
| 旧→新→同批删除 | 撤销将局部下降称整体落实的报告模板；输出每项预测/实际/新增/残差及未兑现原因；同一候选所有失败与原始数据保留 |
| 数量与计价约束 | 验证每cut重建项、实际付费源、stage/seal和后台桥；需覆盖全部责任，不能只复测已改善的bucket。 |
| 验收反例/证据 | RF00–19联合门通过且候选冻结；观察器校准与普通净价各自成立；每项联合实测引用同一候选及完整端点 |
| 待定设计/停止条件 | 确认过程完成；12主格±2%观察控制未证，不能标校准成立。 |

**本项状态：** 设计=已证；消费者迁移=不适用；旧实现删除=不适用；行为验证=进行中；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。

<a id="rf21"></a>
### RF21 · 整包落实、目标达成和M6资格分别裁决

**原行：** T08.1, T08.2。**差异：** operation, write_base, private_target, seal_acceptance, storage, fees, root, read, exit。

**代码起点：** [KisPageStoreCpuMutationTest.cpp:8359](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8359) `KisPageStoreCpuMutationTest::sharedIdleWarmQuantities()`；[KisPageStoreCpuMutationTest.cpp:8409](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:8409) `KisPageStoreCpuMutationTest::nativeFinalSlotReplacement()`

| 排查字段 | 要完成的内容 |
|---|---|
| 当前差距 | 过去技术批次完成易被误读为原型全部落实；paid、upstream及正式M6未获通过。 |
| 目标形态 | 分别裁决结构迁移、行为正确、预测兑现、成本目标、原控制与M6资格。所有本包任务处理且联合验证完成后才称本包落实；目标失败必须明确失败，不能缩范围。 |
| 权威/寿命/锁 | 当前92§6.1是正式门权威；旧20%/30%不是硬门。M6/M7/M8仍按真实证据，任务表不修改资格。 |
| 真实消费者种子 | RF00–20全部证据；固定M5 Fresh/H4、同状态hit/miss与校准family；同语义upstream与管理/内容分母 |
| 失败/取消/退出 | 任何待迁、临时桥、未解释保留或缺证据均不能全完成；负结果可形成完整评估，但不得称达标或最低成本。 |
| 旧→新→同批删除 | 逐条清空原定待改而非用“开放研究”遮住未做实施；合法保留必须由实际合同与最小表达论证；新发现属于本包既定合同则补入本表，不能另立主线绕开 |
| 数量与计价约束 | paid完整服务<1M为工程目标；原型20.340M差额不是收益承诺；upstream同语义证据与通用优化分开。 |
| 验收反例/证据 | 整包22项逐项有结论，缺证据项仍未完成；predicted/actual/net/new/residual和不确定性完整；M6受保护控制/命中/拒绝/资源与环境资格独立报告 |
| 待定设计/停止条件 | 实施/价格/目标分开裁决已完成；paid排他价格、内容分母及最低实现仍缺证据。 |

**本项状态：** 设计=已证；消费者迁移=不适用；旧实现删除=不适用；行为验证=进行中；联合计价=已证。
**可回收净指令预测：** 未核定（null）；先完成数量/新增责任预算，不把原桶全额认领。
