# CP1：原 Payload journal 与 domain admission→Ledger 精确确认

本包从产品父提交 `7708613905a183dfb1d1424bc961ee70300ee438`、文档父提交 `4eecdd0efe90cc2efb1139fd7de667896ed854bb` 继续原physical准备→提交→确认责任。产品本地提交 `5942e1c0f6716c75a66d942f34ed1e4cf7461cd8` 及44份源码blob、15个运行物绑定见[Git身份](git-round-identity.json)、[源码哈希](source-sha256.txt)、[运行物哈希](runtime-sha256.txt)，构建配置/Qt/编译器实测身份见[环境](build-environment.json)。只暂存明确路径，不push。

## 目标形态、替换与成本

原Payload已保存domain/revision，m_changes又复制同一事实，而且noexcept commit在physical移动后申请journal节点。逐个给这两套记录收费仍留下重复状态和终结分配，因此将dirty link放回原Payload，整个准备→physical commit→exact ack使用同一事实。Ledger和原admission负责自己的准入与确认，没有新的结果队列、失败阶段或worker。

| 原路径 | 最终归属与同批删除 |
|---|---|
| observer Payload QHash + m_changes QHash | 原process root上的独立retained child收费稳定Payload/slot map节点，原Payload保存domain/revision和dirty link；slot→Payload只是lookup。m_changes删除，physical commit只写原事实并链接，exact ack仅unlink同revision，untrack在门外free原节点 |
| prepareResidencyChange发布serial后复制live/admissions和追加reservation | charged admission快照先于serial，charged reservation容量先于owner claim；expired weak原位删除，live数组删除。cold拒绝统一cancel原serial与已准备reservation；没有替代原payload或重放physical动作 |
| DomainAdmission先写domainClaim再分配claim/返回对象 | charged claim/registration节点，inactive返回对象与claim齐全后才发布原domainClaim；cancel/commit提取原node，detach清原事实并转交整容器到门外free。保持authority→Ledger→budget锁序 |
| backingDomainChanges Qt输出；Ledger changes/probes/acknowledged Qt数组 | 一个charged Changes类型/参数替代原virtual签名，生产和测试override全迁移。Ledger保留原provider registry不可变共享cut，准备charged Changes和一份Probe，ack flag存Probe；整cut通过前不ack，第二acknowledged数组删除 |

默认诊断snapshot保留原accounting寿命，实际容量可晚于provider facade销毁；Ledger局部snapshot使用原Ledger预算。原stable map、slot lookup、weak admission容量、准备快照与transition reservation数组有实际成本；同步仍有Changes和Probe两类copy，未宣称零分配。外层observer/Transition/DomainAdmission/Reservation的Qt本体和控制块/bootstrap仍未收费。

生产6文件 **+218/-127，净+91**；测试2文件 **+162/-13，净+149**；生成图/基线及ownership3文件 **+7285/-6257** 单列。见[metrics](source-metrics.json)、[生产差集](production-incremental.diff)、[测试差集](tests_and_model-incremental.diff)。生产净增用于实际收费、准备失败原子性和寿命保证，不记为纯行数去重；第二journal事实、live数组和ack数组确实删除。上层生产/public-protected API净增0，原签名替代无兼容overload；未取得性能收益资格。

## 同源行为与失败记录

最终universal构建完成后才运行双架构：各Registry87、CPU1284、Reference660、Physical379、Resident221、Foundation28、Freehand压力/取消4，合计 **5326 passed / 0 failed / 0 skipped**，包含init/cleanup。原始命令、退出码、时长见[accepted结果](accepted-results.json)、[汇总](run-accepted.log)。[初始聚焦结果](initial-results.json)双架构各16/0/0是当时源码范围；其后删除无用Payload字段并把slot索引直接指向原Payload，再完成[最终构建](build-final.log)和上述全组，不能将两次通过数累计。

- 固定64KiB原Ledger Metadata实际allocator硬满，分别没有snapshot容量、仅容得下实测snapshot但没有Probe容量。snapshot成功钩子区分两个真实拒绝点；两者均不ack，保留原cold physical revision/dirty，压力解除后同journal成功确认，再swap-in/确认/退出。没有放宽quota或重放swap。
- claim准备实际拒绝发生在physical移动前，原resident/revision保留、journal不脏、各bucket SSD reserved=0。解除压力后同payload迁移/同步成功，证明没有遗留原transition或domainClaim。
- 真实provider使用固定64KiB共享process root；测试ResidencyObserver在real provider完成准备后填满真实Metadata，后续commit观察仍恰满且真实physical已到SSD、原journal已脏。later Ledger登记时actual weak-admission vector增长拒绝，释放后同Ledger登记成功，原pending登记退出。
- 取cold snapshot后load产生较新revision；旧ack不清较新dirty。原Store/provider/accounting facade销毁后snapshot仍持有实际容量，最后释放后process live实降；没有把仍存在的cache费用断言为零。
- 原snapshot/registration并发cut、clean hint、unregistered dirty保留、stale snapshot及swap-in失败回归，以及read/capture/history/retirement/Fresh和真实brush压力/取消全部通过。不是全局allocator interposition、TSAN、全产品尾退出或完整永久压力资格。

[初始构建](build-initial.log)记录签名迁移后漏改局部swapChanges.isEmpty的编译失败；改为empty后[修复构建](build-repair.log)成功。[边界构建](build-boundaries.log)及[晚snapshot构建](build-tail-test.log)保留准备测试的实际顺序。最终矩阵无异常退出、timeout、skip或行为/像素/额度断言放宽。

旧环境失败进程PID87095本包检查时仍处于UE；其runner已经停止，属于[旧包记录](../br1_synchronous_operation_20261001/README.md)，不能写为子进程已退出或用于当前源码资格。本包新测试禁用core dump，未取得永久退出保证。

源码/ownership固定后完成[调用图](callgraph-generation.log)：1930 APIs/21371 edges/20 callbacks。首次[结构检查](architecture-stale.log)仅报告8个实际改动source checkpoint过期；审阅后[刷新](architecture-refresh.log)，[独立结构门](architecture-final.log)21 manifest/25 ownership/16 census/19上层intrusion通过，manifest阈值不变。普通源码/文档使用显式apply_patch，Python用于运行、分析、派生证据；本包不增加ownership事实或阶段权威。

活动文档链接、已删除状态、源码/运行物/环境身份校验见[结果](document-validation.json)。本包生成数据、原始日志和增量差集分别保存，不用生成图行数解释生产净增。

## 当前剩余与资格

| 相邻实际端点 | 唯一原权威与尚欠保证 |
|---|---|
| provider allocation/physicalPayloads和Ledger provider/backing/physical/sharedMembers/sealedProof核心 | 原binding/physical key、原BackingRecord继续权威；需要完整容量前置、实际安装拒绝回滚及free，尤其physical adoption后Qt插入的异常窗口，不能重放副作用 |
| observer/Transition/DomainAdmission/Reservation及Registry外层 | 本包关闭列明节点/数组，Qt本体/control/bootstrap固定成本仍欠；provider registry共享read cut不等于write-detach已收费 |
| generic metadata投影、capture辅助、tree/deferred/一次性task、close handles/seen/诊断及runtime/clock | 继续原owner/原任务的CP1实际分配清单；永久拒绝、停止、晚handle与自主drain全出口仍开放 |

**完整CP1未闭合，M6/M7/M8正式资格0/3、默认关闭。** CP0同依赖upstream、TSAN、公平/原job接续与BR1-PERF无新增资格。当前差集及下一端点在[92 §16.41/§17](../../92_br1_m6_m8_execution_baseline.md#domain-journal-delivery)、[NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)原位维护，不重复领取已删除journal或增加新的终结阶段。
