# 原 detachment 候选收敛与压力反例

当前裁决见[92 §16.65](../../92_br1_m6_m8_execution_baseline.md#checkpoint-preparation-pressure-delivery)。产品提交`c8de106aacba42a9b4e5fbaafc6fa4d358bddbfa`，产品父提交`50304c3da6881c535e790b3b64dd0f02a812469c`、文档父提交`99c2b7223f13b07fcae1d7819c037447770c5f03`，见[Git身份](git-round-identity.json)。未读取archive、未push；完整CP1及BR1继续开放。

## 原责任与同步替换

原PreparedPublication::Data统一持有候选、shard与活动预约，原prepare/install/cancel/DeferredPublicationCleanup共同负责生命周期。Detachment只改publication/preparedBy，reader/pin/last-use仍须读取安装时原记录；旧Entry却无条件容纳完整发布快照、deltas/installRecords和arena需求。

| 旧内容 | 当前归属与删除 | 实际consumer |
|---|---|---|
| 所有Entry的完整发布载荷 | 共同Entry只保留version/shard/revision/activity；同Data的Publication数组仅普通publication/recoverable候选准备 | preparePublicationImpl、installPublicationImpl、clearBatch |
| detachedVersion和条件key选择 | 共同version提供唯一key，旧字段与所有旧Entry载荷访问删除 | detach准备/复验/全部claim/实际安装/取消 |
| 每页整体Entry析构 | 原cleanup单位分别释放该页发布载荷和共同Entry，payload先于shard owner，原收费owner保持到实际free | DeferredPublicationCleanup::clearBatch，最后Data销毁 |
| 测试改变共享配置前未完成排队终结 | TinyTileBudget在配置切换/恢复的静止边界调用原drain | 原Freehand测试夹具；笔触中没有新增drain |

原PreparationKind、claim、取消、slot reservation和清理调度政策保持，没有新的持久阶段、队列或上层生产API。inline optional/variant仍需要最大Entry布局；逐页heap新增分配。因此采用一个同owner批量数组，代价是一个TU内载荷类型、一个数组和准备/安装/清理三处配对关系，不能声称整体复杂度净删。

## 所有尝试与结论边界

原六方法、输入/额度/断言不变，进程串行；[重复脚本](reproduce_pressure.py)保存每个实际PID、命令、退出、日志和源码/运行物身份，异常退出停止启动后续进程。

| 尝试 | 实际结果 | 意义 |
|---|---|---|
| [旧运行物15进程](baseline-results.json) | 164/1/0，均正常退出 | [第15个arm64](baseline-07-arm64.log)进入压力场景时缺PageStore；不是checkpoint内拒绝 |
| [首次诊断](diagnostic-results.json) | 10/1/0，正常退出 | [原日志](diagnostic-00-arm64.log)确认旧Store仍活跃时改变共享配置遭拒绝 |
| [诊断8进程](diagnostic-more-results.json) | 86/2/0，均正常退出 | [x86_64 checkpoint](diagnostic-more-02-x86_64.log)真实拒绝269568字节/324页；[arm64配置](diagnostic-more-03-arm64.log)再次拒绝 |
| [重构诊断候选3进程](candidate-results.json) | 32/1/0，均正常退出 | [第3个arm64](candidate-01-arm64.log)后续surface extent准备又拒绝8304字节，完整24MiB场景未闭环 |
| [目标候选测试](candidate-targeted-arm64-result.json) | 42/0/0，exit0 | 安装/取消/准备拒绝/晚cleanup/reader churn的有限测试；当时仍含临时诊断，不代替最终验证 |
| [最终原消费者14进程](final-regressions.json) | **7546/0/0，均exit0** | 原CPU/Physical/Resident/Reference/完整manager/Freehand/Matched两架构；见[汇总](final-regression-totals.json) |

旧checkpoint拒绝是共享非payload预算，不是全局malloc失败：kind=Detachment、count=324、请求269568，子控制器live11721288/reserved0/peak11827464；未记录精确父usage，不用子usage推定整个24MiB峰值。原832字节Entry的数组容量正好269568，其中768字节/页的publication载荷不会被detachment使用。本批去掉这份载荷，仍保留真实容量拒绝和原Failed/cancel语义。

旧15进程记录先于source快照脚本补充；baseline Git/runtime已记录且源码当时未改。补充[提交源码身份](baseline-source-reference.json)是事后将原父提交与上一批92份冻结源码逐项匹配，明确不是伪造的运行前source快照。临时[诊断补丁](diagnostic-instrumentation.diff)只用于定位；首次[诊断build](diagnostic-build.log)漏QDebug完整include而失败，[修复build](diagnostic-build-02.log)成功。全部三处生产诊断最终删除，manager/write coordinator最终相对父提交无diff。[最终build](build-final.log)及[删除检查](delivery-checks.json)绑定当前实现。

诊断候选仍有8304字节surface容量拒绝；8MiB取消日志另显示backend初始化容量拒绝，旧cancel断言并不能证明成功准入后取消。最终两次Freehand组合通过不关闭这些反例，不提高额度/缩输入/降低断言或在笔触中强制GC。继续沿原CP1固定成本、bootstrap、候选峰值、接受和最后释放查完整参与者，不新增失败子阶段。

## 实际容量、成本与身份

新Reference两行给真实共享父额度仅留64KiB，准备324页候选后填满剩余全部额度，再分别安装/取消。每页Published/nextGeneration和原身份保持、Prepared/Historical及事务正确；原17页清理单位与活动归零、子费用精确返还通过。双架四行候选实际live增量均**20976字节**，见[arm64](KisPageStoreReferenceTest-final-01-arm64.log)、[x86_64](KisPageStoreReferenceTest-final-01-x86_64.log)。原布局要求的Entry数组269568字节已超过64KiB，这一反例不靠测试开关模拟拒绝。

[同目标编译布局](candidate-record-layouts.json)/[命令和退出](record-layout-results.json)：Data200→240、Entry832→64、Publication768字节。普通publication两数组合计仍832字节/页，但多40字节Data和一次数组分配；detachment实际候选为240+324×64=20976。布局是编译器sizeof证据，不是malloc实际总开销或全局性能资格。[复现脚本](measure_candidate_layouts.py)从原父提交重建before源、只做syntax/layout编译；完整原始布局dump和before源是可再生分析材料，未纳入提交清单。

[生产](production-incremental.diff)1文件**+50/-43净+7**，[测试](tests-incremental.diff)2文件**+70/-0**，[ownership](ownership-incremental.diff)**+1/-1**，[生成](generated-incremental.diff)**+5279/-5035**，见[逐文件统计](source-metrics.json)。容量改善和真实硬满完成证明单列，不记等价去重收益。上层生产API/持久阶段/锁/TLS/队列新增0，mainline生产侵入文件新增0；测试新增private drain依赖只位于测试夹具。

[最终图](callgraph-final.log)87TUs/2020APIs/25285edges/21callbacks，[架构门](architecture-final.log)21manifest/25ownership/16census/原19intrusion；[原ratchet](baseline-before.json)未放宽。93份[源码](source-identity.json)、109个[运行物起点](runtime-before-tests.json)/[结束身份](runtime-identity.json)、[构建](build-identity.json)、[检查器](freeze_evidence.py)绑定同一本地提交。最初冻结脚本误将runner日志纳入费用提取，[失败](freeze-first-failed.log)保留；收窄至两个真实Qt日志后[最终检查](freeze-committed.log)通过，没有重跑产品矩阵来掩盖此脚本错误。

原manager保留LIMIT_LONG_TESTS=1、stress/benchmark与线程配置。Matched共用原五插件/fixture，blank/painted、callback、strategy/image释放同前；无新upstream独立配对，原stroke/undo/redo回退未关闭。图索引与前部低层测试共时，索引已结束才执行两次业务Freehand；不将共时当作先前失败原因或正式性能证据。

[此前三个失败进程](prior-failed-processes.txt)59123/70089/83020仍UE，当前14个exit0不证明全部尝试drain。完整CP0/CP1、provider/observer/Transition/Reservation及其他控制本体、metadata link/source/read cache、bootstrap/固定成本、全部参与者永久尾出口、公平/原job continuation、全局allocator/TSAN、M6/M7/M8正式0/3与BR1-PERF仍开放，默认persistent策略资格不改变。
