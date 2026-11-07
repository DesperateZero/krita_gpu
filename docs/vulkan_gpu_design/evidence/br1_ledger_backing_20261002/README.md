# CP1：Ledger backing 安装准备、共享成员与同节点退场

产品提交 `5771e65f819e5f4b7a70cbe465078e17e73a327a`，父 `2e39b9e760513ecab9c0aa7337a62308ddfd2c00`；文档父 `1a834667c1181dbc55592eb2053ad6dc9b96e7c9`，见[Git身份](git-round-identity.json)。44份源码blob、15个运行物及5份构建/依赖身份分别见[源码](source-sha256.txt)、[运行物](runtime-sha256.txt)、[环境](build-environment.json)。普通代码、测试和活动文档用显式apply_patch，Python只分析/编排/生成证据；只提交本轮明确路径，不push。

## 目标形态与同步删除

原registerBacking先改变physical引用或插入physical，再分配logical backing/sharedMembers；实际拒绝可留下部分状态。只给旧容器收费仍保留这个窗口。因此选择前移实际安装存储，复用原retirement record，完整迁移注册、class/domain claim、handoff、退休和take消费者。

| 原路径 | 最终归属及同批删除 |
|---|---|
| uncharged BackingIndex / Qt physicalBackings | 两个actual charged稳定map nodes并入原retirement record，在fresh provider前准备；安装只转移同nodes。预算投影、domain admission、classification、handoff和terminal消费者全部迁移 |
| sharedPhysicalMembers + 每physical QSet | 原backing节点内嵌双向member links、原physical成员头；第二成员表和grow/终结分支删除。projection只读link，handoff rekey同node，原headroom/class/revision政策不变 |
| DomainAdmission allocated RegistrationIndex | 同步调用栈拥有原登记marker，原authority gate维护link，scope结束移除；没有异步结果/责任复制，不需要节点/buckets或持久phase |
| rollback后已消费的原retirement record | reserveBacking在下一cold准备补齐缺失的实际nodes，失败仍由caller持有原Record/physical结果/reservation；恢复只继续登记，不重放provider副作用 |
| releaseRetiredBacking移动value再锁内erase | unlink并extract实际backing/last physical nodes到门外free；take移交唯一退休Record，原queue保留拒绝债务。alias成功不用的physical预备node门外返还 |
| 挂接时创建retained accounting owner的候选实现 | 删除候选提前分配，attach空map保持零分配；首次安装锁内绑定已准备node的allocator，再检查身份。保持冷limits和shared-parent配置，不新增bootstrap状态 |

生产3文件 **+271/-176，净+95**，包含CPP到private头的完整迁移；Ledger cpp净+10，不能以单文件搬移声称减行。测试2文件 **+256/-8，净+248**；生成审计3文件 **+8229/-6796** 单列。见[metrics](source-metrics.json)、[生产差集](production-incremental.diff)、[测试差集](tests_and_model-incremental.diff)。增长用于真实收费、完整准备/原子安装和最后free保证，不能记作纯去重；成员表和allocated registration index实际删除。稳定map、每fresh两节点及record增大未测性能；上层生产/public-protected API净增0。

## 同源结果与实际边界

最终完成同一universal build后，双架构各Registry87、CPU1292、Reference660、Physical381、Resident221、Foundation28、Freehand两个压力/取消方法4，合计 **5346 passed / 0 failed / 0 skipped**，包含init/cleanup。全部14进程正常退出；命令、耗时、退出码见[qualified结果](qualified-results.json)、[汇总](run-qualified.log)。[修复后聚焦](repaired-results.json)对应冷配置修复前的中间源码，双架构各CPU19/Physical85，不累加为最终资格。

- 固定64KiB，先预热原reservation/accounting缓存，再实际测量backing/physical node费用；分别给只够原record+operation node和完整费用少1B的空间，触发两个真实allocator拒绝。fresh物理入口0次，部分准备费全退，reserved=0。
- 直接adoption已有有效physical结果：拒绝保留同handle、provider验证/committed bytes、caller reservation和未登记Ledger事实；解除压力后仅登记，provider创建0次。初始adoption rollback的原Record回到caller，硬满补齐失败仍是同地址，解除后同Record补齐/安装，最终实际free回基线。
- 原registered/orphan queue组合把Metadata压力提前到registerBacking之前。硬满登记只转移actual nodes，queue拒绝retire、automatic retry、Debt额度释放后无新输入继续和close均用原Record；已安装core节点在physical退休时free，inert Record到最终dispose才free，分开按实测费用严格断言。
- 真正的第二footprint窗口中，登记线程保留scoped marker，主线程swap和同physical alias登记被拒；后者仍有原Record/reservation。原登记在硬满下完成，marker归还后同alias结果接受；释放压力后同physical成功迁SSD，physical字节只计一次。
- 三alias每次准入前都占满64KiB，成功时无安装分配，额外预备physical node返还；移除middle/head、原代表、最后physical，逐次按实测logical/physical node费用断言。原共享Debt/SSD、claim取消、handoff generation及跨索引增长回归保留。
- 冷配置、Registry/journal/read/capture/history/retirement/Fresh、Reference和真实brush压力/取消最终全部通过。没有取得全局allocator interposition、TSAN、所有固定成本或完整永久压力/最后handle退出资格。

## 失败记录与修复

[首次构建调用](build-initial.log)因当前PATH没有cmake未启动；改用CMakeCache中的绝对命令，[实际构建](build-absolute.log)通过。首轮[focused结果](focused-results.json)的新测试费用差312/936B来自未预热的原reservation缓存，两个实际节点并未泄漏；补齐真实缓存基线，额度与free断言不放宽。

同轮x86_64 lastUseAtMetadataCapacity在terminal-0-exit-0观察到root=2/预期1。原history idle合同明确排除未来retry，Metadata硬满仍有future history工作，可再次临时持root；原executor drain不冻结monitor未来生产。现先观察自动last-use终态完成，再停止future history/retirement dispatch，等待原idle和回调尾部，仍严格断言root=1，不手动重新发起业务。

[下一聚焦CPU原始日志](boundaries-cpu-arm64.log)在新测试访问空initialReplicas时SIGSEGV；[LLDB定位](debug-nodes.log)到测试4533行。修复为显式一页的Fixture::init(4, 1)，[修复构建](build-fixture-repair.log)和[修复后聚焦](repaired-results.json)通过。该轮runner已停止，失败native PID43034收到SIGKILL后仍观察为UE，不能声称已退出；旧PID87095也仍UE。记录见[失败元数据](failed-boundary-run.json)。后续禁core并使用QtTest -nocrashhandler，最终14进程均正常退出；仍不构成永久退出资格。

[首次完整矩阵](pre-cold-fix-results.json)每架构CPU152、Reference8、Freehand1失败，暴露了挂接提前分配破坏冷limits/shared-parent配置的实际回退。将空索引allocator绑定移到首次安装，直接取已准备allocator，保留零分配安装；[最终构建](build-cold-configuration.log)后完整qualified矩阵全通过。原失败与[汇总](run-pre-cold-fix.log)保留，不能当最终资格。

## 结构、身份与剩余范围

[最终调用图](callgraph-final.log)1944 APIs/21627 edges/20 callbacks；[中间调用图](callgraph-pre-cold-fix.log)对应冷配置修复前源码，不能作当前身份。初次[结构检查](architecture-stale.log)只报告5份实际source checkpoint过期；审阅后[刷新](architecture-refresh.log)和[独立门](architecture-final.log)通过21 manifest/25 ownership/16 census/19上层intrusion，阈值不变。源/库与活动文档核验见[结果](document-validation.json)；[首次文档校验](document-validation-first.json)只因自身输出文件尚未生成而缺一个链接，保留后复核通过。

下一是原Ledger provider/pending registry、provider cut/route选择、sealedProofs的实际存储及接受/撤销。保留budgetless/先登记后挂接的真实consumer和冷配置；provider接受admission后不能再因索引分配丢失责任，seal拒绝不能消耗stamp或丢失原prepared结果。generic metadata投影、capture辅助、TileDataStore登记、tree/deferred/一次性task、close handles/seen/诊断、Qt本体/control/bootstrap、Store/provider/Ledger及runtime/clock和完整永久压力尾退出仍欠。

**完整CP1未闭合，M6/M7/M8正式资格0/3、默认关闭。** CP0同依赖upstream、TSAN、公平/原job接续及BR1-PERF无新增资格。当前差集和排期见[92 §16.43/§17](../../92_br1_m6_m8_execution_baseline.md#ledger-backing-delivery)、[NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)，不重新领取本轮已交付节点和已删索引。
