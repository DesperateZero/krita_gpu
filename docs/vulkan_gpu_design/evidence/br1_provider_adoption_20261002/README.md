# CP1：原 provider adoption 节点准备、physical 记录与 lease 存储

产品本地提交 `2e39b9e760513ecab9c0aa7337a62308ddfd2c00`，父 `5942e1c0f6716c75a66d942f34ed1e4cf7461cd8`；文档父 `e1bbaf1197e4f67298ca3ff1397f40e17789d450`。44份源码blob和15个运行物见[Git身份](git-round-identity.json)、[源码哈希](source-sha256.txt)、[运行物哈希](runtime-sha256.txt)；构建配置/Qt/编译器实测身份见[环境](build-environment.json)。只暂存明确路径，不push。

## 目标形态、替代与成本

原physicalPayloads保存identity/refcount，observer Payload已保存同一identity及domain/revision，三个adoption入口各自创建binding、physical retain和插入allocation。逐个收费原Qt表会继续保留两套物理记录，因此将logicalReferences收回原Payload，删除第二physical表，并共用完整节点准备/安装/回滚政策。

| 原路径 | 最终责任与同批删除 |
|---|---|
| physicalPayloads/Tiles3PhysicalPayload | 原observer Payload唯一保存physical identity、logicalReferences、domain/revision及dirty link；第二Qt表/类型及其insert/remove/遍历删除，physical字节仍只计一次，最后逻辑ref才untrack |
| fresh/alias/initial各自拼binding→retain→allocation.insert | prepareAdoption准备真实allocation node及必要Payload/slot nodes，fresh全部前置到pixel创建/复制前；已有physical alias只准备一个逻辑node。adopt共用binding/physical/同node安装及回滚，三个直接插入点删除 |
| QHash allocation与无收费generic lease map | 共用稳定charged map，real Tiles3 allocation/lease nodes和buckets接§16.41原retained process allocator；reference CPU消费者迁移std接口，其默认预算接线没有扩大。actual lease拒绝先于pin，原leases/ID保留；retire提取原allocation node到provider门外free |
| physical表遍历统计 / observer锁下读tile锁的可能路径 | residentBytes等待原transition serial，再读唯一Payload domain；不持observer锁获取tile swap锁，不新增resident计数缓存；析构逐项撤销原payload登记，无整个列表复制 |

PreparedAdoption/PreparedPayload只是在本次cold调用中保留实际未安装nodes，目标handle未提前发布；没有新持久阶段、物理权威、结果队列或worker。节点安装前Qt binding构造仍可失败，TileDataStore register/initialize拒绝或异常由同一原scope撤销登记和tracking。外层Qt本体/control/bootstrap及TileDataStore内部登记容量仍欠，不将局部节点保证推广为全局bad_alloc资格。

生产2文件 **+211/-112，净+99**；测试/模型2文件 **+140/-3，净+137**；生成图/基线及ownership3文件 **+7203/-5900** 单列。见[metrics](source-metrics.json)、[生产差集](production-incremental.diff)、[测试差集](tests_and_model-incremental.diff)。净增表达实际收费、完整准备、拒绝原子性和统计锁序保证，不能记为纯去重；重复physical表和三处手拼安装/回滚确实删除。稳定map、cold三节点、lease buckets和等待成本未测性能；上层生产/public-protected API净增0。

## 同源结果与真实拒绝

最终同源universal build完成后，双架构各Registry87、CPU1289、Reference660、Physical379、Resident221、Foundation28、Freehand压力/取消4，合计 **5336 passed / 0 failed / 0 skipped**，包含init/cleanup。命令/退出码/时长见[qualified结果](qualified-results.json)、[汇总](run-qualified.log)。[最终聚焦](drain-boundary-results.json)双架构各22/0/0，不累计进全组通过数。

- 固定64KiB process Metadata，先用真实成功alias/fresh测量节点费用并确认退休返还基线；给0、仅allocation费用、fresh总费用少1B空间，分别拒绝actual allocation/Payload/slot节点。默认pixel初始化未发生，committed及原pending retirement不变，所有部分准备费用全退；解除压力后新合法operation成功并退休，没有重放已接受physical动作。
- 满额下已有physical alias和initial adoption拒绝，原source/tile/refcount/费用保留；释放后两入口共享同physical slot，不重复charge physical bytes，逐项retire保持原current physical。既有immutable/source/native alias、Fresh、before/handoff及prepared退休回归保留。
- actual generic lease node满额拒绝：原lease的0x31数据仍可读、旧pin仍阻止retire，拒绝未占新ID；释放原node后同ID成功。buckets容量允许收费存活到provider析构，不把仍有cache的root断言为零。
- 实际PausedObserver在real provider已准备serial、physical尚未移动时暂停；memoryUsage等待同serial，释放后swap和统计均完成，resident减一页、committed不变。整个路径不在observer门内获取tile锁。
- 现行Registry、domain journal/stale ack、read/capture/history/retirement、CPU/Reference/Physical/Resident/Fresh与真实brush压力/取消全部通过。这不是TSAN、全局allocator interposition、全部固定成本或完整永久压力/尾退出资格。

## 失败记录与修复边界

[初始构建](build-initial.log)完成生产/map迁移。[新增边界构建](build-boundaries.log)因测试把KisReplicaAccess.cpuReadData误写为data失败；[修复构建](build-repair.log)成功，[初始聚焦](initial-results.json)双架构各15/0/0通过。其后[初次全组](accepted-results.json)arm64通过，x86_64的lastUseAtMetadataCapacity(terminal-0-exit-1)出现引用数3/预期1，其余全组通过；原始日志和[汇总](run-accepted.log)保留，不作为最终资格。

该组合fixture的引用计数涵盖read/history/retirement及通知，而测试只等read/history语义idle就读取整体物理引用数。read finished先发布idle再门外归还root，原executor则在整个finished callback返回后才清running；retirement也有独立任务/通知。因此补齐原retirement.waitForIdle和kisDrainPageStoreReclamation再断言，原引用数必须为1、pending/read protection/pin/额度条件不变，没有放宽断言或手动重新发起业务。见[实际两行差集](tests_and_model-incremental.diff)、[最终构建](build-drain-boundary.log)，最终相关双架构22/0/0和完整qualified矩阵通过。

旧失败进程PID87095本包检查时仍为UE，属于[旧包](../br1_synchronous_operation_20261001/README.md)；其runner已停，不能声称子进程已退出或用于本包资格。当前新测试均禁用core dump，仍未取得完整永久退出保证。

## 结构与剩余

源码固定后[最终调用图](callgraph-final.log)1939 APIs/21485 edges/20 callbacks；[初次图](callgraph-generation.log)对应补drain之前的测试源码，不能作最终source身份。首次[结构检查](architecture-stale.log)只有4个实际source checkpoint过期，审阅后[刷新](architecture-refresh.log)与[独立门](architecture-final.log)21 manifest/25 ownership/16 census/19上层intrusion通过，manifest阈值不变。普通源码/文档使用显式apply_patch；Python只编排、分析、生成证据。活动文档与源码/运行物/环境身份校验见[结果](document-validation.json)。

下一是原Ledger provider/backing/physical/sharedMembers/sealedProof核心的注册→classification/claim→retirement/take，全部准备容量、有效provider结果拒绝后的责任保留、回滚及free必须共用原记录；不重建physical表或重放副作用。provider/binding/read-cache/source/observer/Transition/Admission/Reservation、Registry外层的Qt本体/control/bootstrap，TileDataStore observer登记内部Qt容量、generic metadata投影/capture辅助、tree/deferred/一次性task、close handles/seen/诊断及runtime/clock与永久压力最后handle仍在同一CP1清单。

**完整CP1未闭合，M6/M7/M8正式资格0/3、默认关闭。** CP0同依赖upstream、TSAN、公平/原job接续与BR1-PERF无新增资格。当前差集/剩余端点见[92 §16.42/§17](../../92_br1_m6_m8_execution_baseline.md#provider-adoption-delivery)、[NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)，不从旧冻结清点重复领取已交付节点。
