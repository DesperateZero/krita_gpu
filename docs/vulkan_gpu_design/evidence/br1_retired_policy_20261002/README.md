# CP1 旧完成、History 交接及退休 binding 政策回收

本轮从产品父提交 `5771e65f819e5f4b7a70cbe465078e17e73a327a`、文档父提交 `1d7ae9f31342a042dd539a54553fa3b208c3601c` 继续。聚焦产品提交及44份源码blob、15份运行物身份见[Git记录](git-round-identity.json)、[源码](source-sha256.txt)、[运行物](runtime-sha256.txt)；编译器、双架构配置及5份构建/依赖身份见[环境](build-environment.json)。普通源码、测试和活动文档均使用显式apply_patch；Python仅分析、编排及生成证据。本地两仓库分别提交，不push，不混入原有未归属文件。

用户本轮要求回收前几轮审视出的过时分支。目标是传播已经成立的准备保证，同批移除旧恢复及附属状态；没有增加下一段provider/proof容量工作或新持久阶段。

| 原残余 | 最终责任及删除 | 真实仍可失败的部分 |
|---|---|---|
| allocate/retire/transfer/archive在物理成功后将completion拒绝改报Failed或回滚；alias忽略结果 | Registry内部`completePrepared noexcept`统一所有实际producer、reference CPU provider、host-ready、scope及teardown；prepared终结无容量拒绝，非法/重复终结属于不变量。旧成功后业务失败/rollback全部删除 | public bool complete保留非法/foreign/重复ticket拒绝；source/ticket准入、pin/last-use、物理创建/准备前拒绝保留。不是archive Qt记录安装等所有成本都不可失败的保证 |
| beginRetirement缺少private ticket仍报现场分配失败 | 原allocation必须拥有已准备ticket；缺失按不变量处理，旧错误解释删除 | pin/last-use/transition拒绝沿同ticket继续，不在retire现场再铸造 |
| History detach后Work.effects/nextEffect及finishEffectsLocked重试、pendingEffects快照/close guard | detach前必须配置Debt owner，验证精确registered backing及原record；成功提交Debt后，原owner gate内只转交同record到原intrusive queue。effects收回slice局部charged packet，旧持久效果状态和全部读者删除 | key/root/revision、packet及Debt准备拒绝继续原Work/task/Delay；普通queue Pending/pin/Debt拒绝仍有来源，不是所有pass零分配 |
| bindRetirementOperation缺预付node转generic分配；detachedRetirement缓存及bool转接wrapper | 只填原record预装node，fallback、第二bool和私有wrapper删除；publication分类直接读原record指针 | generic bind有实际reference/Pending消费者及容量拒绝，保留其独立计数/释放合同；身份失配仍拒绝并保留实际result，不重放retire |

生产16文件 **+79/-119，净-40**；测试/模型4文件 **+88/-33，净+55**。生成审计/ownership3文件+11279/-11177单列，调用图索引变化不计作生产复杂度增长或收益；上层生产改动及public/protected API净增0。新增History前置验证修复缺接收者时可能detach后失去责任的缺口，成本已计入生产差集。参见[生产差集](production-incremental.diff)、[测试差集](tests_and_model-incremental.diff)、[统计](source-metrics.json)、[实际删除检查](deletion-checks.json)。没有靠压行或删除说明取得净减行。

最终构建先完成再跑测试，一次universal构建writer，见[构建](build.log)、[reference夹具迁移后增量构建](build-reference-fix.log)。测试环境offscreen、seed12345、原prefix/plugin路径，禁core并关闭Qt crash handler。最终同源资格来自[运行脚本](run_results.py)和[14进程结果](qualified-results.json)，各架构如下：

| 组 | arm64 | x86_64 |
|---|---|---|
| CompletionRegistry | 87/0/0 | 87/0/0 |
| CPU mutation | 1295/0/0 | 1295/0/0 |
| Reference | 660/0/0 | 660/0/0 |
| PhysicalClaim | 381/0/0 | 381/0/0 |
| ResidentRead | 221/0/0 | 221/0/0 |
| Foundation | 28/0/0 | 28/0/0 |
| Freehand正常压力/取消 | 4/0/0 | 4/0/0 |

合计 **5352 passed / 0 failed / 0 skipped**，包含init/cleanup；14进程全部正常退出。三个新History负例实际移除Debt owner、已登记backing或原retirement record，保留原metadata，至少三次原retry且provider退休0次；原硬满行直接验证准备完成后的交接和一次退休。Registry硬满三终态直接消费共同政策，同时保留public身份/重复拒绝测试。reference退休模型改用实际FakeCpu provider Pending→原Queue→同预付operation node回收，验证未准备结果拒绝、generic Pending共存、计数归零且无重放。

中间[聚焦运行](focused-results.json)240/0/0发生于metadata oracle最终迁移之前，其reference运行物已被后续构建替换，仅作中间行为记录，不授予最终源码身份，也不与5352累加。首次[完整运行](pre-reference-migration-results.json)在两个架构各出现5个`indexedHistorySlices`失败：合成replica夹具直接discard且未配置Debt owner。已在cold configure前接显式模型责任接收者，并核对prepare/commit数量及cancel=0；合成索引oracle不冒充真实物理交接证据。失败日志与[首次完整输出](run-pre-reference-migration.log)保留，迁移后重新运行全部7组，不降低业务/预算断言。

[最终调用图](callgraph-final.log)为1943 APIs/21642 edges/20 callbacks。初次[结构检查](architecture-stale.log)只报告20份实际改动source checkpoint过期；审阅后[刷新](architecture-refresh.log)及[独立门](architecture-final.log)通过21 manifest/25 ownership/16 census/19上层intrusion，既有阈值未变。源/库/活动文档核验见[结果](document-validation.json)及[核验脚本](verify_documents.py)，commit冻结由[脚本](freeze_evidence.py)检查父身份、实际Git blob和运行物；归档未参与当前裁决。

既有失败native PID43034/87095在本轮检查时仍为UE/parent1；本轮最终测试没有新native崩溃，不能由正常进程退出推定完整永久压力最后handle已取得资格。未运行全局allocator interposition、TSAN或性能矩阵；其他metadata投影/包装本体、固定成本、TileDataStore登记及完整尾出口仍开放。

**本轮过时政策回收完成；完整CP1未结算，M6/M7/M8正式资格0/3，默认关闭。** 下一仍是Ledger provider/pending登记、route cut及proof接纳/撤销生命周期，见[92 §16.44/§17](../../92_br1_m6_m8_execution_baseline.md#retired-policy-delivery)、[代码索引](../../br1_modification_guide/CODE_INDEX.md#retired-policy-code-index)、[下一领取](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)。不重新领取本轮已删除失败分支或状态。
