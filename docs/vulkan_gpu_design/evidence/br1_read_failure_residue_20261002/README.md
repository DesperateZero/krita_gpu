# BR1 read 过时失败分支回收（2026-10-02）

产品`e8a9f1f34a19b1e65bf2d2bcde3698da9d4e7d2f`，父提交`276c675f6af1a80321aca7be4087fc05a086223a`；文档父提交`c1745dcb4509f5f256d676cf30c8548ecbf32a7c`。[Git身份](git-round-identity.json)、[47源码](source-sha256.txt)、[15运行物](runtime-sha256.txt)及[5依赖](build-environment.json)绑定本轮。未读archive、未push，源码及活动文档使用显式apply_patch。

目标是传播已经成立的原保护节点合同。release将ReadLease原slot改为PendingLastUse或unlink；ack移除同ticket的原slot；ReleasedBlocks::append只拼intrusive链，cleanup只保留原费用/活动。registry订阅reset的emptied callback只移除原readiness记录。订阅冷分配仍可能拒绝，armLastUseLocked已经把它接到原retry；history key与queue交接的实际拒绝由cancel/finishHistory入口保留原记录。因此删除cancel的metadata捕获、finishReleasedReadLocked/acknowledgeRecordLocked外层捕获，以及processLastUses对取消重试的重复捕获、allocationFailed和重复失败计数。订阅前同一owner锁内重复验证删除，锁外watch后的完整复验保留。

本次没有新增保证、类型、状态、队列或API。[生产差集](production-incremental.diff)1文件 **+6/-17，净-11**；测试源码及数据行零改动；生成审计2文件 **+218/-227，净-9**单列，ownership不变。[统计](source-metrics.json)相对本轮实际父提交，未用压行或删除不同语义的阶段达成净减。

一个universal写者完成[构建](build.log)后执行[双架构编排](run_results.py)。[最终结果](qualified-results.json) **5390 passed / 0 failed / 0 skipped**，14进程退出0；每架Registry87、CPU1297、Reference677、Physical381、Resident221、Foundation28及Freehand压力/取消4（含init/cleanup）。复用lastUseAtMetadataCapacity的实际满额、subscriber拒绝和Succeeded/Failed/Cancelled终态，以及cancel/close/stop、capture晚guard和原Freehand压力取消；本轮没有构建或测试失败，也没有新增全局malloc计数或完整永久尾退出证明。

构建后生成[调用图](callgraph.log)：87 TUs、1968 APIs、22058 edges、21 callbacks。[初次结构检查](architecture-stale.log)仅报告本轮read源checkpoint过期；审查差集后[刷新](architecture-refresh.log)，[独立检查](architecture-final.log)通过21 manifest/25 ownership/16 census/19 intrusion，门限未改。[16项删除/保留检查](deletion-checks.json)核对旧分支、全部相关入口和剩余失败来源，静态检查不替代运行证据。

示例中的provider completion政策、空publication效果和首写投影在本轮起点已经删除，未重复实施。read/capture进度、真实subscription/history拒绝、publication claim/身份拒绝、retirementResult/Pending/Debt及generic StateMachine/overlay/proof的准备失败仍有实际consumer；检查文件逐项记录删除条件。不会把新的付费候选保证扩张为所有prepare都不可失败，也不会把捕获减少当作CP5 job接续完成。

[92 §16.51](../../92_br1_m6_m8_execution_baseline.md#read-failure-residue-delivery)、[代码](../../br1_modification_guide/CODE_INDEX.md#read-failure-residue-code-index)及[API](../../br1_modification_guide/API_CONVERGENCE_MAP.md#read-failure-residue-api-delivery)同步。本次有限清理完成；完整CP1与BR1排期继续，M6/M7/M8正式资格0/3、默认关闭，性能、TSAN、公平及CP5接续资格不变。
