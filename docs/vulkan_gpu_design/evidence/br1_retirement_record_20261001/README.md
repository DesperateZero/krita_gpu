# CP1 backing 前退休节点准入及同一节点转交

2026-10-01 同源冻结，当前入口为 [92 §16.33](../../92_br1_m6_m8_execution_baseline.md#retirement-record-preparation)。本轮先审查原caller与已收敛API：继续使用typed通知、prepared task及原executor；真正欠项是丢弃physical ownership之后才补record，分区/pass/close重复容器节点，以及三类reservation shared box。选择补齐必要terminal存储并同批替换旧路径，没有提前扩展M7或stroke模式。

## 实际责任与删除对象

| 原消费者 | 已实现 / 原门 / 最后释放 | 替代及限制 |
|---|---|---|
| reserveBacking / Fresh/default/native/generic/import | 原方法返回payload/debt reservation与真实收费terminal record，provider前冷准入；沿原activeProviderCalls出Store门准备/释放，原身份重验后接收 | 裸reservation和physical失败后临时造record路径替换；新carrier不取得page/root/payload权限；原quota/layout/domain/transient和复合Debt预留保持 |
| initial adoption | 第一笔ledger registration前准备所有真实nodes及收费指针数组；回原Store门重验；注册/失败rollback保持同一原门内，nodes回到预备数组后门外free | 不在部分注册期间冷分配或为free临时开门，避免并发adoption接受将被rollback的注册；其他replicas/providers/registered/metadata scratch仍欠 |
| OwnerLedger backing / retag/handoff / take | 成功注册才接收node，BackingRecord持有唯一terminal；retag/handoff保留同body，退休/close/初始rollback按原完整handle取走一次；未转交body在ledger门外free | direct注册先冷准备真实node；拒绝时外部physical仍归caller。backings/physical/shared-members/claims的索引、本体与全部分配失败回滚未获资格 |
| rejected-unregistered provider result | 持冷准备的同一node和原composite reservation，实际provider与budget重验保留 | orphan/admission reservation内嵌，wait budgetGrant也内嵌；三个shared box删除；不因已付存储费授予retire许可 |
| pending/retry/ready / worker batch/process / close / failed-close | owning intrusive list只splice原node；真实provider拒绝保留同一physical debt/地址；成功retire后仍收费，门外实际body free后才退费 | 原std::list节点、record值搬移、close QVector reserve/copy与重复pass容器分配删除；32项pass上界和原provider/last-use重验不变。其余wait/retry/效果/core/close scratch未关闭 |

薄RetirementStorage forward header让ledger/write无需依赖Queue/Store；完整body只供实际消费者。不同alias各自真实terminal node收费，payload仍按原physical-once分类，不用payload去重掩盖实际metadata容量。retained allocator保持原parent/child付款身份直到物理free，controller退出后的存储尾不取得语义权限。

## 最终统一结果

| 实际目标 | arm64 | x86_64 |
|---|---|---|
| Reference全组 | 657/0/0 | 657/0/0 |
| CPU mutation全组，含冷拒绝及两条恰满node转交目标 | 1250/0/0 | 1250/0/0 |
| PhysicalClaim全组：handoff/共享alias/retag/index-growth | 379/0/0 | 379/0/0 |
| 原Freehand压力成功与取消 | 4/0/0 | 4/0/0 |

合计 **4580 passed / 0 failed / 0 skipped**。实际argv/退出码/totals见 [results.json](results.json)，环境见 [run_results.py](run_results.py)：offscreen、KIS_BR1_SEED=12345、原_install与_build/bin夹具路径。原UI 24 MiB成功/8 MiB取消预算未改。本批没有重跑Completion全组，不累加上一批的83/架构成当前资格。

新增CPU目标用真实WriteCoordinator准备：metadata余量小于一个实际record时拒绝，provider尚未进入，payload/debt reservation全退；容量释放后同方法成功并收费实际sizeof(record)。registered和rejected-unregistered两条原consumer在metadata恰满、provider连续拒绝下，经prepared pass/process/close保留同一node地址；physical retire与node free分开检查，节点费用仅在真实free后返还。**恰满node目标显式停用自动wake**，只关闭record转交/失败保债，不能外推为所有wait/retry在硬满下自主恢复、全pass零分配、全分配interposition或TSAN。

原四族PhysicalClaim断言不再要求仍活跃controller的所有bucket都零：每个实际node free准确返还sizeof(record)，共享alias和index-growth逐node检查；所有payload/live CPU SSD/reserved归零断言保留，metadata cache存活继续收费。没有跳过MetadataArena或放宽quota。

## 初始失败与最后审查

整包完成后运行目标，没有每个hunk重复测试。保留 [首轮PhysicalClaim失败](initial-failures/results.json)：两架构各81个失败集中四族旧“所有bucket归零”断言，已按真实metadata node与仍存活cache修正，保留payload/reservation零保证。初始构建的carrier完整类型/调用迁移及private链接可见性错误分别见 [build.log](build.log)、[build-final.log](build-final.log)、[build-qualified.log](build-qualified.log)、[build-freeze.log](build-freeze.log)；没有用失败构建后的旧binary授予最终资格。

第一次完整通过见 [最后回滚审查前结果](before-final-rollback-review/results.json)，它不代表最后源码。最后代码审查发现initial rollback为free节点开Store门的并发缺口：改为同一预备数组保留节点，在原门内撤销注册，之后门外free。最终源码构建见 [build-rollback-final.log](build-rollback-final.log)，最终结果是上表八个进程。构建期间调用图扫描遇到暂时缺失的generated moc，失败保留在 [callgraph-during-rebuild.log](callgraph-during-rebuild.log)；构建结束后重新扫描的 [callgraph.log](callgraph.log)才绑定最终源码。测试与最终身份之后没有再no-op重建binary。

## 结构、代码密度与未关闭条件

[architecture.log](architecture.log)通过：21 manifest条目、25 ownership事实、16 census组、1902 indexed APIs、20605 call edges；callgraph登记20 callbacks。审查前的旧QVector具体contract与source失配见 [architecture-initial.log](architecture-initial.log)；只将takeForClose检查更新为同一已收费节点的转交类型，原三条backing/admission/retirement ownership事实同步，未增加第二状态权威。先审查/生成图，再刷新 [前](baseline-before.json)/[后](baseline-after.json)checkpoint，最终正常gate独立执行。intrusion manifest与上一批逐字节相同，19个既有主干侵入文件限制未放宽。

本批仅PageStore内部及原测试，上层UI/tool/strokes/paintop/painter/PaintDevice/scheduler生产改动和public/protected API净增均 **0**。9个生产文件相对本批起点 **381 added / 176 removed**，包含两个新的private storage/body headers。增量主要是冷准入、原node ownership转交及原gate内rollback，不声称总行数或所有private API数下降。既有private process/stopAutomaticWakeups增加KRITAIMAGE_EXPORT仅为外部test binary链接原消费者，没有新函数、friend/probe/getter；完整替代/删除见 [API账本](../../br1_modification_guide/API_CONVERGENCE_MAP.md#retirement-record-api-delivery)。

[before-code.json](before-code.json)记录7个原生产文件及2个新文件的空起点；[source-incremental.diff](source-incremental.diff)只对应这9个生产文件，原测试没有完整起点快照，不纳入本轮行数。[source-union.diff](source-union.diff)为所列9个生产及3个测试相对HEAD累计差异，包含此前改动，不能当本轮增量。[source-metrics.json](source-metrics.json)、[source-sha256.txt](source-sha256.txt)冻结32个相关源码/测试/结构文件，[runtime-sha256.txt](runtime-sha256.txt)冻结4个实际目标binary及8个运行库/插件。[HEAD](head.txt)只是checkout提交，实际实现仍在未提交工作树。检查脚本和实际结果见 [validate_documents.py](validate_documents.py)、[document-validation.json](document-validation.json)。

**完整CP1仍未结算，M6/M7/M8正式资格0/3，默认关闭。** 下一主目标为必要Wait/订阅/Delay/capture与generation-qualified retry重臂：拒绝保留同一physical debt，容量释放后无新输入能自动继续；原晚取消/在途身份必须保持，同包审计余下pass/core效果。history/read scratch、tree batch/deferred对象及一次性task、Store Private/统计/内嵌服务、registry/provider本体/core索引、runtime/clock/线程固定成本及完整硬满终结仍欠。清点只在 [最新CODE_INDEX](../../br1_modification_guide/CODE_INDEX.md#retirement-record-code-index)，领取只在 [NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)维护；不重复构造已收费record、typed通知或worker。
