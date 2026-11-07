# BR1 原首写 base 查询退出 Qt 投影（2026-10-02）

产品`276c675f6af1a80321aca7be4087fc05a086223a`，父提交`d9f15aa3ae0e29857873c1f3c7492a18694eb4e5`；文档父提交`35e0f16661f5d660952234f962e833edbc62aee9`。[Git身份](git-round-identity.json)、[47份源码](source-sha256.txt)、[15份运行物](runtime-sha256.txt)和[5份依赖](build-environment.json)绑定最终结果。未读archive、未push，普通编辑使用显式apply_patch，上层生产/API零改动。

原prepareWriteBaseLocked由native首写、generic acquireWrite及semantic alias/private replacement共同消费。原mutationBaseSnapshot复制root/sealed两个版本及全部replica/protection列表，caller只需存在性、writer、nextGeneration、exact authority和一个before候选。改为原shard cut的私有queryMutationBase与stack MutationBaseInfo，删除旧接口/全部调用/嵌套Qt复制及caller循环；原versionSnapshot共用record VersionInfo描述。候选次序与validity/operation/CPU/layout/physical条件不变，pending/removal/default控制保留；缺页/foreign/writer/缺selected authority/default或descriptor准备仍可拒绝。输出没有write/claim授权，原联合准备继续复验并取得物理资格，无新owner、持久阶段、重试或结果队列。

[生产差集](production-incremental.diff)3文件 **+79/-52，净+27**；[测试差集](tests_and_model-incremental.diff)1文件 **+75/-9，净+66**；生成审计2文件+4150/-3801单列，ownership未变。[统计](source-metrics.json)按本轮实际父提交计算。必要标量结果和原record描述有成本；两个独立exact查询不能维持同一shard cut，保留Qt投影并收费仍复制不用的保护容量，故直接读原记录。没有宣称整体净删、内存峰值/性能收益或完整generic metadata收口。

一个universal build writer完成[构建](build.log)后运行[编排](run_results.py)：offscreen、seed12345、原prefix/plugin，core为0，Qt crash handler关闭。[最终矩阵](qualified-results.json) **5390 passed / 0 failed / 0 skipped**，14进程退出0；每架Registry87、CPU1297、Reference677、Physical381、Resident221、Foundation28、Freehand压力/取消两方法4（含init/cleanup）。本次产品构建/测试无失败，无新增QtTest数据行。原indexedMutationBaseLookup的0/255/4095 history行改验证标量事实：wrong domain/layout/Allocated候选跳过、带lease/pin/last-use/capture的有效before按原序选择；实际MetadataArena filler恰满下writer/nextGeneration、root/selected分别缺失、候选发现关闭、foreign输出保留和virtual default均断言，live/backpressure不变，完整StateMachine oracle与原记录对照保持。

原CPU生产handoff/Fresh回退和native/generic首写、semantic/default/private replacement、publication/cancel及真实Freehand压力取消均在最终矩阵内。实际恰满只证明此观察无需metadata容量，不能推定后续first-write/overlay/proof准备必成功；没有当前源码global malloc计数、性能或完整永久压力最后handle资格。

图在构建完成后生成：[callgraph](callgraph.log)为87 TUs、1968 APIs、22059 edges、21 callbacks。[初次结构检查](architecture-stale.log)只报告4份已改源码checkpoint，[刷新](architecture-refresh.log)不改门限，[独立检查](architecture-final.log)通过21 manifest/25 ownership/16 census/19 intrusion；[前](baseline-before.json)/[后](baseline-after.json)快照保留。[12项删除/保留检查](deletion-checks.json)核对全部consumer和剩余实际拒绝，静态检查不替代运行证据。

裁决见[92 §16.50](../../92_br1_m6_m8_execution_baseline.md#mutation-base-query-delivery)，[代码](../../br1_modification_guide/CODE_INDEX.md#mutation-base-query-code-index)和[API](../../br1_modification_guide/API_CONVERGENCE_MAP.md#mutation-base-query-api-delivery)同步。首写观察投影已替代；generic StateMachine临时Qt容量、overlay准备/安装/清理、其他wrapper/shared核心/bootstrap/固定成本及完整永久压力尾退出继续CP1。**完整BR1目标保持，CP1开放，M6/M7/M8正式资格0/3、默认关闭**；TSAN、公平/CP5接续及BR1-PERF未取得。
