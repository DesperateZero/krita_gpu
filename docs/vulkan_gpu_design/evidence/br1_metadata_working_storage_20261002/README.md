# BR1 原 metadata 工作值、转换与安装（2026-10-02）

产品`8896ac1dab5364e403048d9069703c4ed9dd0978`，父提交`e8a9f1f34a19b1e65bf2d2bcde3698da9d4e7d2f`；文档父提交`603a936e19e083af1922a8ce622e678508189af5`。[Git身份](git-round-identity.json)、[50源码blob](source-sha256.txt)、[15运行物](runtime-sha256.txt)和[5构建依赖](build-environment.json)绑定本批。未读archive、未push。产品tracked树干净，外层活动文档单独提交。

本批责任是原generic metadata和publication的临时投影→转换→安装/拒绝→实际free。权威仍在原record/shard/revision/claim，四种私有工作值只拥有临时或原candidate容量；没有新owner、持久阶段、队列或上层生产API。原paid Version/Replica直接投影并参与共享StateMachine政策，后续step消费原值，publication move同Version进入installRecords。Qt public oracle和外部snapshot合同继续。相比另写一套paid转换，单段政策减少需要同步维护的生命周期判断；相比原record直接修改再补回滚，付费局部值让sequence及effect准备拒绝继续发生在权威修改之前。第一份before/input仍承担实际authority/delta/removal见证，不把它误删为无用副本。

seen/included/previous/retained/discard临时集合、旧Qt→paid安装复制、公开Qt known-valid入口与applyImpl包装删除；无consumer的新增const工作state查询也删除。batch physical set仍有实际跨record唯一性责任，用原allocator收费其节点/buckets；原single record前缀检查仍为O(replica²)，去集合后其他membership扫描也有查找成本。全部batch插入及reservation先于record改变，Debt准备后的真实容量拒绝沿原guard取消同cookie；没另建恢复阶段。

公共Qt effects/reason和Store/publication下游聚合有真实cancel/abort/private-replacement消费者。本批先准备producer输出再Debt/install，但未迁移其全部Qt容量、后续搬运或原接受责任；不宣称完整generic CP1。read/capture进度、Pending/subscription/Delay/Debt、合法identity/claim/revision/physical冲突、paid proof/overlay和原Failed/cancel仍有真实来源。[23项删除/保留检查](deletion-checks.json)及[已知valid入口消费者](known-valid-consumers.txt)记录具体条件，不用静态消失代替行为验证。

[生产差集](production-incremental.diff)4文件 **+422/-266，净+156**；[测试差集](tests_and_model-incremental.diff)1文件 **+123/-0**；生成审计/ownership3文件 **+33655/-13528**单列，图重索引不计作实现增长或去重收益。[统计](source-metrics.json)相对本轮实际父提交。净增来自原预算下的实际工作值及共享容器操作，是收费保证成本；没有纯净删、分配速度或短gate结论。

普通源码/头文件/测试/活动文档均使用显式apply_patch。单文件StateMachine的机械容器迁移保存[一次性配方](migrate_policy.py)和[机械diff](state-machine-mechanical.diff)，工具只从当时工作树生成可审阅补丁，没有脚本直接写产品源码；该中间配方不代表最终结果，也不应在已迁移源码上再次应用。后续discard、iterator、消费工作值及无consumer删除均为显式补丁，完整结果以Git增量为准。

每次构建只有一个写者；测试和图都在对应构建完成后启动。[初次构建](build-01.log)有vector signed循环warning，改iterator后[build-02](build-02.log)通过；新write测试的nextGeneration初值在运行前修正，只有private-replacement已Prepared初值才前进。[working-02结果](working-02-results.json)为5396/0/0，源/运行物身份及增量保存为working-02-*。按值move简化后[build-03](build-03.log)及[working-03结果](working-03-results.json)同样5396/0/0，身份和差集独立保存为working-03-*。初次调用图因我在索引时修改ownership说明被同源保护拒绝，保留[日志](callgraph-input-change.log)；稳定输入后重新生成。两份中间成功不与最终数相加。

移除无consumer的const lookup后完成[最终build-04](build-04.log)，[最终双架构结果](qualified-results.json) **5396 passed / 0 failed / 0 skipped**，14进程退出0；每架Registry87、CPU1297、Reference680、Physical381、Resident221、Foundation28及Freehand压力/取消4（含init/cleanup）。原完整oracle、Recoverable/Fresh、publication/capture/read/retirement/close、真实Freehand压力与取消继续覆盖。新增3行实际MetadataArena压力分别验证read/release、private replacement、write/prepare/cancel：headroom从0到65536，拒绝不安装records；Debt准备回调实际压满剩余额度，后续拒绝全部取消原cookie且保持完整metadata；实际free后live精确恢复baseline，解除压力后同输入成功并与Qt oracle全部records/effects对照。Debt receiver明确为synthetic metadata oracle，真实provider/backing/queue交接由原矩阵验证，不把替身当永久压力尾退出证据。

[最终图](callgraph-qualified.log)87 TUs、1989 APIs、24221 edges、21 callbacks。[API差集复核](callgraph-delta-review.json)确认37新增/16移除中多数是模板化签名和私有值访问；零直接入边的pure值方法仍由共享template policy消费，无consumer的const state查询已删。[初次检查](architecture-stale.log)只报告最后header checkpoint过期；审阅后[刷新](architecture-refresh.log)，[独立检查](architecture-final.log)通过21 manifest/25 ownership/16 census/19 intrusion，阈值未改。[冻结脚本](freeze_evidence.py)核对产品commit父关系、全部源码blob、运行物及实际依赖配置。

[92 §16.52](../../92_br1_m6_m8_execution_baseline.md#metadata-working-storage-delivery)、[代码](../../br1_modification_guide/CODE_INDEX.md#metadata-working-storage-code-index)、[API](../../br1_modification_guide/API_CONVERGENCE_MAP.md#metadata-working-storage-api-delivery)和NEXT已同步。本有限责任完成；公共effects到queue的接受/取消、overlay、外部Qt oracle/注册/诊断、Transition输入、bootstrap/shared核心/固定成本与完整永久压力最后handle仍属CP1。完整CP1及BR1继续，M6/M7/M8正式资格0/3、默认关闭；未新增全局allocator、TSAN、公平/CP5接续、CP0同依赖对照或BR1-PERF资格。
