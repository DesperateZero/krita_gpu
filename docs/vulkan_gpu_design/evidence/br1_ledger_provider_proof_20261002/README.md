# BR1 Ledger provider/proof 准备与生命周期（2026-10-02）

本轮从产品父提交`64dd930babedfb71d9edabc7be97f11199cd5e6c`、文档父提交`48c279a1dcb3fa6b23b936ad65a20889c0547330`继续完整BR1目标。[Git身份](git-round-identity.json)绑定47份[源码blob](source-sha256.txt)、15份[运行物](runtime-sha256.txt)及5份[构建/依赖身份](build-environment.json)。普通源码、测试和活动文档用显式apply_patch，Python仅分析、运行编排和派生证据；本地两仓库聚焦提交，不push。

有限责任为原Ledger provider登记→accepted cut/route→sealed proof→revoke/析构。provider实际收费节点先于外部domain admission准备，原节点pending/accepted共用，拒绝unlink门外free；accepted查询共同排除pending。domain同步与route共用scalar accepted cut/cursor，删除pending QSet、Qt provider QHash snapshot/values/list。proof实际收费节点先于provider validation准备，安装无分配，接受后才推进stamp/输出；Qt proof表删除，revoke门外free。局部节点原语只有这两个实际consumer，原成员析构次序不变，无结果队列/公开API或上层生产改动。

每个节点记录原allocator预算来源，保留budgetless及挂接前bootstrap兼容；后续节点使用挂接预算。本批未追溯收费。单allocator整表map会在挂接时重新分配旧记录或改变兼容consumer，原节点provenance加原intrusive index避免该窗口和第二authority。paid节点/前置准备/共同cut是新增保证的成本：生产1文件 **+158/-67，净+91**；测试/模型4文件 **+153/-3，净+150**；生成审计/ownership3文件 **+8219/-7152**单列，不记作生产增长/简化。见[完整生产diff](production-incremental.diff)、[测试diff](tests_and_model-incremental.diff)、[统计](source-metrics.json)。raw diff保留Git空context行，初次build.log保留Ninja失败行末空格；外层whitespace检查只排除这三份原始证据，产品diff完整检查。

一次universal build writer：[初次构建](build.log)因C++17不支持construct_at失败，改为allocator_traits::construct后[构建](build-cxx17-fix.log)通过；加入实际provider validation边界压力后[最终构建](build-validation-pressure.log)退出0，随后运行[脚本](run_results.py)。环境offscreen、seed12345、原prefix/plugin路径，禁core及Qt crash handler；实际命令、退出码在[最终结果](qualified-results.json)。

| suite | arm64 | x86_64 |
|---|---:|---:|
| CompletionRegistry | 87 / 0 / 0 | 87 / 0 / 0 |
| CPU mutation | 1296 / 0 / 0 | 1296 / 0 / 0 |
| Reference | 660 / 0 / 0 | 660 / 0 / 0 |
| PhysicalClaim | 381 / 0 / 0 | 381 / 0 / 0 |
| ResidentRead | 221 / 0 / 0 | 221 / 0 / 0 |
| Foundation | 28 / 0 / 0 | 28 / 0 / 0 |
| Freehand压力/取消两个方法 | 4 / 0 / 0 | 4 / 0 / 0 |

合计 **5354 passed / 0 failed / 0 skipped**，含init/cleanup，14进程正常退出。新增一行ledgerProviderRegistrationPreparedBeforeAdmission（每架构1）实际填满64KiB MetadataArena，验证节点准备拒绝时provider callback零进入、pending隐藏/重入重复拒绝、provider拒绝/异常归费、准备后callback填满仍能登记及最后析构归费。扩展原domainProviderSnapshotSurvivesRegistration：capabilities/domain callback新登记者不进入旧cut，下一cut看见并拒绝route歧义/纳入domain同步。

原ownerLedgerSealsPreparedPageBeforeEpochCommit使用实际MetadataArena：proof准备拒绝保留prepared metadata/authority/transaction和caller输出stamp77，下一成功stamp1；测试模型在真实provider validation边界填满剩余额度，已准备proof仍能安装；两个proof实测收费，硬满validate/revoke精确归费，重复revoke拒绝，正常epoch commit后最终free。FakeCPU beforeValidate是测试模型hook，没有增加生产API。原History/Pending/retirement/close/manual/brush压力与取消断言保留。

加入validation边界压力前的[中间结果](pre-validation-pressure-qualified-results.json)也为5354/0/0；仅保留日志，没有在下一构建前冻结运行物身份，不作为最终源码资格、不与最终结果累加。callgraph.log同样只记录中间源码，最终使用callgraph-final.log。

[21项删除/替代检查](deletion-checks.json)通过，[检查脚本](check_deletions.py)复核旧表/集合/Qt复制退出、共同accepted lookup/cut、准备顺序/stamp/输出接受点及原budget来源/门外释放。静态检查不替代上面的实际资源边界行为。初次结构门只报告5份源码checkpoint过时，见[原日志](architecture-stale.log)；核对后阈值不变刷新[原baseline](architecture-refresh.log)，再独立[最终检查](architecture-final.log)：21 manifest/25 ownership/16 census/19 intrusion，图1953 APIs/21701 edges/20 callbacks，87 TUs；[最终生成日志](callgraph-final.log)及before/after baseline均保留。

native seal/generic finishWrite仍有proof准备与metadata/overlay Qt拒绝来源，原Failed/cancel消费者保留；Ledger保存prepared结果不等于scheduler自动继续。versionSnapshot、generic投影/capture辅助、Qt本体/control/bootstrap（含兼容节点）、TileDataStore登记、runtime固定成本和完整永久压力尾出口仍欠。旧失败native PID43034/87095本轮复核仍UE/parent1，完整永久尾退出、全局allocator、TSAN、公平/原job接续和性能资格未取得。当前唯一裁决见[92 §16.46](../../92_br1_m6_m8_execution_baseline.md#ledger-provider-proof-delivery)，[代码](../../br1_modification_guide/CODE_INDEX.md#ledger-provider-proof-code-index)与[API](../../br1_modification_guide/API_CONVERGENCE_MAP.md#ledger-provider-proof-api-delivery)同步；有限端点完成，**完整BR1目标继续、CP1开放、M6/M7/M8正式资格0/3、默认关闭**。
