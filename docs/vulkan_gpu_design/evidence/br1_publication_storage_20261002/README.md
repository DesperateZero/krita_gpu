# BR1 原 publication 候选的存储与晚释放（2026-10-02）

产品`d9f15aa3ae0e29857873c1f3c7492a18694eb4e5`，父提交`31dabb9789400c697851f553342f9051e4664c99`；文档父提交`e5e892c91187c419b145537b6f9d6f3fa0decd68`。[Git身份](git-round-identity.json)、[47份源码](source-sha256.txt)、[15份运行物](runtime-sha256.txt)及[5份依赖](build-environment.json)绑定最终结果；未读archive、未push，普通编辑使用显式apply_patch，上层生产/API零变化。

原PreparedPublication继续唯一持有candidate和原activity/arena/index reservations。Data、entries/deltas/growth、authority hash节点/buckets与嵌套version/replica/lease/last-use/capture安装容量使用原allocator，删除未收费make_unique、普通vector与Qt持有副本；header的versions重置释放保留容量。原assign/putReserved/install共用政策，单记录physical重复检查的局部QSet删除，改为无分配前缀扫描；generic batch QSet保留。全部MetadataArenaGrowth实际consumer迁移，默认无预算构造删除，未挂接payload先free再release reservation。

原MetadataBudgetAuthority对已支付directory/block费用仅登记相同accounting owner的保活字节，不重复收费。controller销毁后，该owner继续持有原shared parent/child，deferred shard/arena和candidate实际free才减费，最后owner free后才unregister。删除detach后晚release直接忽略费用的旧假设；clearBatch终点替换完整DataPointer，同时释放空deleter里的allocator引用。成功、revision拒绝、取消、晚cleanup仍同一候选，无新队列、持久阶段或预算权威。既有shared shard/owner控制块bootstrap未由本批改写。

[生产差集](production-incremental.diff)4文件 **+168/-56，净+112**；[测试差集](tests_and_model-incremental.diff)2文件 **+186/-23，净+163**；生成/ownership3文件+8560/-6534单列。[统计](source-metrics.json)从本轮实际父提交计算。净增是实际容量与物理释放缺口修复的成本，不作为等价去重；深复制只在原准备入口，使用实际allocator约束收费与free。前缀检查为O(replica²)，性能、锁时长和短gate资格未测。

只有一个build writer，最终[universal构建](build-cache-fix.log)完成后运行[编排](run_results.py)，offscreen、seed12345、原prefix/plugin，core为0，Qt crash handler关闭。[最终矩阵](qualified-results.json) **5390 passed / 0 failed / 0 skipped**，14进程正常退出；每架Registry87、CPU1297、Reference677、Physical381、Resident221、Foundation28、Freehand压力/取消两方法4（含init/cleanup）。新增Reference16行覆盖commit/recoverable/default restore/detach的成功、取消、读churn和coordinator/controller销毁后clear：实际parent恰满准备拒绝不变state/activity，释放压力后正控制可准备，再恰满仍安装；完整StateMachine与晚保护oracle、reservation退出、parent精确baseline均断言。read churn合法新增的overflow arena仍收费到页面退出，不能误算成candidate泄漏。

中间失败完整保留：[初次构建](build-initial.log)为迭代器遮蔽replica成员导致编译失败，[修复构建](build-fix.log)成功；[初次定向](focused-results.json)与[寿命修正定向](focused-lifetime-fix-results.json)揭示空deleter保留owner、未暖root cache和真实reader overflow增费；实现释放完整空DataPointer，断言保留原reservation直到cleanup。全部holder收费后，[第一完整矩阵](matrix-before-fixture-fix-results.json)暴露旧夹具以稳态容量限制冷注册，[第二矩阵](matrix-before-cache-fix-results.json)仅余honorsBudget缓存基线。夹具在冷准备后以实际filler恰满，先暖可复用原cache；退出精确费用断言保留，没有放松被测压力。最终日志与失败日志分开，无新增hang/crash。

最终图在完成构建后生成，[日志](callgraph-qualified.log)为87 TUs、1967 APIs、22024 edges、21 callbacks。[过时检查](architecture-stale.log)报告已改源码/图checkpoint，[刷新](architecture-refresh.log)不改变门限，[独立检查](architecture-final.log)通过21 manifest/25 ownership/16 census/19 intrusion。原25事实仅补候选与arena寿命说明，不新增权威；[前](baseline-before.json)/[后](baseline-after.json)快照保留。[17项删除/保留检查](deletion-checks.json)只证明静态替代，行为证据以最终矩阵为准。

当前裁决见[92 §16.49](../../92_br1_m6_m8_execution_baseline.md#publication-storage-delivery)，[代码](../../br1_modification_guide/CODE_INDEX.md#publication-storage-code-index)和[API](../../br1_modification_guide/API_CONVERGENCE_MAP.md#publication-storage-api-delivery)同步。原candidate独占容量和晚释放责任已交付；generic临时StateMachine Qt投影/集合、mutationBase/overlay、其余wrapper/shared核心/bootstrap/固定成本及完整永久压力尾出口继续CP1。合法identity/revision/claim拒绝、read/capture进度、Pending/subscription/Delay/Debt和Failed/cancel仍有真实消费者。**完整CP1仍开放，M6/M7/M8正式资格0/3、默认关闭**；未取得TSAN、公平/CP5接续或BR1-PERF资格。
