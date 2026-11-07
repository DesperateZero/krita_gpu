# CP2 原 parked batch wrapper 的读取权限

产品 `7d425255e2364339cc5f9cedf4472e1377f44053`，父 `4b108d316c360b2d752d788799a9fffbe07ea863`，文档父 `6871f8cb832735a930ff7f5c97323b115e99f1fc`。最终十进程逐项source/runtime前后哈希与产品Git blobs已核对，见 [机器结果](results.json)。外层既有旧 `krita` gitlink 差异不混入文档提交。当前裁决见 [92 §16.110](../../92_br1_m6_m8_execution_baseline.md#cp2-batch-read-delivery)。

父实现的 batch lease 没有未来读缓存。write unlock 归还 native guard 后仍留下 ready 标记，wrapper 直接 blockSwapping，不经过仍为 Reserved 的 binding。真实同页 foreign reader 因而取得 unpublished target；四 BPP × anonymous/history 共8行全部失败，actual exit8/reaped：[父日志](parent-parked-batch-arm64/run.log)、[身份](parent-parked-batch-arm64/identity.json)、[当时源码](parent-manager.cpp)、[测试补丁](parent-tests.patch)。

独立与 batch 写现在共用有效 guard 下的 expected cache准备和失败归还。bridge 的原 writable 布尔替换为 ReadSelection/ReadCache/Write 意图，全部声明/override/生产和测试 caller 同批迁移，没有保留旧 overload。ReadCache 先从原 session 查询已有 parked target，再核对原 hint，beginWrite 重新借用后再次复验同一 version；它不能准备新页、选择最新 current 或借另一线程的 batch。读取结束归还原 guard并留下 dormant hint；nested read→write 移交同一活跃 guard，不再二次 beginWrite。hint继续只保留 binding/expected，不持batch、root、RAM pin或TileData所有权。

已取得 target guard 后，缓存或 lease交接拒绝由原 batch 的 failed/finish/cancel承接；写failed时依原 leaseMutex→backend mutex顺序保护既有查询。standalone沿原session析构取消和原transaction归还。原诊断消息保留，raw COW refs/users、Reserved writer排斥、retired wrapper独立存储和Fresh政策不放宽；bulk无缓存consumer仍不强制分配hint。

新增权限保证与等价合并分列：保证是foreign拒绝、原mutation借用、拒绝后不得静默发布；合并是standalone/batch guard/缓存准备及局部失败归还。生产六文件 +96/-54（净+42），测试四文件 +178/-28（净+150）。新增一个内部意图枚举、一个私有原target查询，修改现有batch lease构造参数；没有新增字段、include、friend、TLS、owner、queue或mutex。failure路径多取得一次原lease gate，不能将净增计为去重或性能收益。bridge意图和私有legacy查询在相应旧wrapper consumer迁走时随兼容路径删除，不向上层暴露PageStore身份。

新读取用例同时检查同owner live读取、nested写复用、一代/一次seal、pin归还、captured exact保持、named undo/redo，以及无额外capture/generic request。另一个真实硬满用例先准备pending target，再用process allocator填满metadata budget，拒绝缓存/lease交接；释放容量后原scope仍拒绝finish并取消，current/exact保持before，后续新owner可成功。这是原owner失败终结，不能当作同一失败操作的自动continuation。

运行命令、source/runtime/Qt前后哈希、dyld实际加载、actual exit/reaped及超时事实由 [runner](run_tests.py)逐轮保留。最终运行清单见 [results.json](results.json)；不同候选源码、目标子集和重跑结果不累加成资格。配置继续为universal arm64/x86_64、Qt offscreen、seed12345、LIMIT_LONG_TESTS=1。完整注册manager不表示未启用的100000cycles长测试或完整M6矩阵。

| 最终当前源码运行 | 每架结果 | arm64 / x86_64 |
|---|---|---|
| 完整注册DataManager | 1194/0/0 | [arm64](final-03-manager-arm64/run.log) / [x86_64](final-03-manager-x86_64/run.log) |
| 完整CPU Mutation | 1394/0/0 | [arm64](final-03-cpu-arm64/run.log) / [x86_64](final-03-cpu-x86_64/run.log) |
| 完整Reference | 790/0/0 | [arm64](final-03-reference-arm64/run.log) / [x86_64](final-03-reference-x86_64/run.log) |
| 完整PhysicalClaim | 397/0/0 | [arm64](final-03-physical-arm64/run.log) / [x86_64](final-03-physical-x86_64/run.log) |
| 完整ResidentRead | 221/0/0 | [arm64](final-03-resident-arm64/run.log) / [x86_64](final-03-resident-x86_64/run.log) |

十进程共7992/0/0，均actual0/reaped、未超时、实际加载候选库；上述最终源码的hash逐项与产品commit blobs一致。其他运行不重复计入总数。87 TU调用图为2176 APIs、27700 edges、27 callbacks、unresolved0，结构门差异仍保持为未通过。

两次无效方法名调用原样保留于candidate-parked-batch-arm64及candidate-parked-batch-02-arm64；它们在执行前失败，不记行为覆盖。candidate-build-02.log保留新增测试把原backend裸指针误作smart pointer的编译错误，build03修复。首次完整manager的18个失败都是合并时漏掉原batch拒绝诊断，final-manager-arm64保留actual18/reaped；build04恢复原诊断，定向49/0/0和双架完整相关矩阵均通过。最后补齐原failed查询的锁域后，build05和最终运行另行绑定，早先矩阵不充当最终源码资格。

当前实际compile database的87 TU调用图另行重建，unresolved0；源和调用闭包见reverse-callgraph-03.json。checker仍未通过：旧source checkpoint及继承的memento include差异之外，本轮kis_tile.cc的bridge意图使identifier_occurrences由上限9增至13。这四处是同一个内部bridge类型的实际读/写意图caller，仍须CP3结构审阅结算；没有刷新baseline、提高ratchet或靠alias隐藏计数。原raw/batch桥是暂留consumer，不宣称核心已成为独立library。

CP1保持关闭，8/24MiB长压测和宿主默认abort探针没有重跑。本轮只关闭原parked batch wrapper再次读取与该交接拒绝的有限缺口；原受保护exact重解析、其余raw/batch生命周期、epoch/ABA/晚completion及所有其他实际准备拒绝仍属完整CP2。ON/OFF、TSAN、完整M6与性能资格未取得，M6/M7/M8正式0/3、persistent默认关闭。
