# CP1：Registry 与原 provider 退休终结准备

本包从产品父提交 `a561ca7b0ba920872fd2d8e0420016967a354985`、文档父提交 `20c68559f7001c190a91958eb2cfbc9b42405a16` 继续原producer→owner→terminal责任。产品本地提交 `7708613905a183dfb1d1424bc961ee70300ee438` 及41份源码blob、15个运行物绑定见[Git身份](git-round-identity.json)、[源码哈希](source-sha256.txt)、[运行物哈希](runtime-sha256.txt)，构建配置/Qt/编译器实测身份另见[环境](build-environment.json)。只暂存明确路径，不push。

## 目标、替换与实际成本

已定位的真实缺口是allocatePending只发行ID，terminalRanges/nonSuccess仍在物理动作之后申请存储。单独给两表预备节点会保留两套索引/回滚政策，因此采用原source的一个intrusive区间，Pending实际节点在发行前准备。完成只写状态/合并和推进明确coverage，不再做存储准入；物理动作后的确认不依赖新的可用额度。

| 原路径 | 最终归属及同批删除 |
|---|---|
| Private QSharedPointer、无收费sources和terminalRanges/nonSuccess | 原Registry建立独立retained accounting child，真实backend接原process root；Private/std共享控制块、source map及实际区间节点收费。两个终态索引、terminalStatus/markTerminal和终结时分配/回滚删除 |
| ticket发行 → physical动作 → complete申请节点 | allocatePending先收费实际Pending节点才铸造ID，拒绝不消耗身份。complete复用原节点，成功prefix无需节点，相邻同类Failed/Cancelled区间合并；实际free在registry门外且先于notify |
| provider retire现场allocatePending、拒绝后completeFailed | 原allocation记录在cold allocate/immutable alias/initial adoption前持有private retirementCompletion；拒绝保留同一Pending，物理detach/free后完成，teardown取消未消费ticket。真实Tiles3全部插入点和reference CPU consumer迁移 |
| transfer手写失败/归还、archive在物理store后取得ticket | 原scope统一失败终结和source pin归还；archive准备前移到payload/copy/storeRawRecord前，不增加结果记录/队列/失败阶段 |

每Pending持有实际区间，每活跃backing增加一张预备退休ticket。storageRecords现在包括Pending准备，100000 Pending即100000实际记录；原Pending gap、状态、重复终结和readiness上限断言保持。实际consumer只有诊断/测试，不参与Store关闭或业务调度；private退休Pending表示预留容量，不是活跃业务operation。

生产7文件 **+161/-119，净+42**；测试/模型3文件 **+202/-4，净+198**；生成图/基线及ownership3文件 **+7745/-6172** 单列。见[metrics](source-metrics.json)、[生产差集](production-incremental.diff)、[测试/模型差集](tests_and_model-incremental.diff)。净增是实际收费、准备和producer保证的表达成本，不是纯行数去重。没有新增上层生产/public-protected API、通知权威或调度器；source有序map、Pending准备、查询/合并和cold retirement成本未做性能测量。

## 同源行为与失败记录

完成universal构建后才测试。最终双架构各CompletionRegistry87、CPU1280、Reference660、PhysicalClaim379、ResidentRead221、Foundation28、Freehand压力/取消4，合计 **5318 passed / 0 failed / 0 skipped**。原始命令、退出码与结果见[accepted结果](accepted-results.json)、[完整汇总](run-accepted.log)。[prepared聚焦结果](prepared-results.json)不是另一份累计通过数；[initial聚焦](initial-results.json)没有后来补充的双节点准入拒绝行，只保留其当时范围。

- 固定64KiB真实process Metadata硬满，新增source/ticket实际allocator拒绝且不消耗身份。5 tickets先孤立终结、桥接再关闭gap，三种终态均完成；callback看到原终态，duplicate不能改状态/计数。释放后下个ticket/source值连续。
- 真实Tiles3冷准备分别拒绝operation节点和retirement节点。实际测量同source节点费用，保留固定额度而非估算sizeof；没有新增default payload工作或committed bytes，先取得的ticket结束而非遗留Pending。释放额度后新合法operation成功，原已消费operation语义不变。
- 两个真实backings已持有退休ticket，later backing被read pin拒绝时ticket仍Pending；释放pin后共享Metadata仍满，用原ticket完成out-of-order物理退休，不新增ticket。两个physical free后payload归零；拒绝一次加实际退休两次共3次provider调用。
- Registry销毁释放实际body/source/区间，最后弱订阅reset后回到同workload实测预热process cache基线，reserved归零。原registry析构/取消竞争、随机状态oracle、Pending gap、重复终结、并发allocation/readiness和source存储compact全组通过。
- 全部现行CPU/Reference/Physical/Resident/Fresh与真实brush压力/取消回归通过；这不是全局allocator interposition、M6 archive before、完整永久压力或全产品退出证明。

[build-initial](build-initial.log)记录Boost intrusive disposer不能继承noexcept函数指针的编译失败；改为lambda，见[build-repair](build-repair.log)。补充准入测试最终构建见[build-capacity-tests](build-capacity-tests.log)。新测试没有异常退出、timeout、skip或放宽像素/行为/固定额度。

当前包之外的旧环境失败进程PID87095仍是上包初始夹具留下的UE进程；其runner已停止，不能写为子进程已退出，也不计当前源码资格。历史诊断保留于[原证据](../br1_synchronous_operation_20261001/README.md)，本包没有据此取得永久退出保证。

源码/ownership固定后完成[调用图](callgraph-final.log)：1928 APIs/21265 edges/20 callbacks。首次[结构检查](architecture-stale.log)仅报告10个已改source checkpoint过期；审阅实际增量后[刷新](architecture-refresh.log)，[独立结构门](architecture-final.log)21 manifest/25 ownership/16 census/19上层intrusion文件通过，原manifest阈值不变。普通源码/文档使用显式apply_patch；Python仅运行、分析和生成证据。

活动链接与身份校验见[结果](document-validation.json)。[初始文档校验](document-validation-initial.log)将verifyTerminal中的局部变量terminalStatus误当已删除的同名方法；正则改为检查旧方法/调用，产品源码与行为断言未变。

## 相邻责任与尚欠资格

| 实际剩余端点 | 原权威及拒绝后承接 |
|---|---|
| provider allocation/physical/domain journal/admissions；Ledger provider/backing/physical索引 | 原binding/physical key、原revision/admission和BackingRecord保持权威；实际索引容量仍需收费/前置，物理副作用后不能靠重新执行operation恢复。准备区间不关闭这些Qt索引异常窗口 |
| backingDomainChanges → synchronizeBackingDomains changes/probes/acknowledged | 原provider journal保留到精确revision ack；需收费准备并复验原domain/revision，拒绝由原journal/owner保留事实，不新建结果队列 |
| Registry外层Qt facade/child controller包装及bootstrap | 本包实际收费的是内层Private/shared控制块、source和区间；外层固定成本仍欠，不能把局部owner释放推广为全部对象预算关闭 |

generic metadata投影、capture辅助存储、tree/deferred/一次性task、close handles/seen/诊断、Store/provider/Ledger本体及runtime/clock和完整永久压力最后handle继续CP1。**完整CP1未闭合，M6/M7/M8正式资格0/3、默认关闭。** CP0同依赖upstream、TSAN、公平/原job接续与BR1-PERF没有新增资格。当前差集/下一端点在[92 §16.40/§17](../../92_br1_m6_m8_execution_baseline.md#registry-terminal-preparation)、[NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)原位维护，不重复领取已删除两索引或建立新的终结阶段。
