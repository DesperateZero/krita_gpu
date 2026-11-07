# CP2 clone 拒绝与构造清理收敛

产品 `39700f0d53f249eed4ea189fe7d0ed98635a9ee0`，父 `5a3767cc6f9af6e3885c3eb634822798ed99553e`，文档父 `6c88743c8320127df477aa708228ce77473d185d`。当前裁决见[92 §16.112](../../92_br1_m6_m8_execution_baseline.md#cp2-clone-refusal-delivery)。产品身份、最终同源结果和实际退出见[results.json](results.json)；完整CP2剩余核验见[cp2-audit.json](cp2-audit.json)。外层旧krita gitlink不混入文档提交。

有效父红为[parent-final-arm64](parent-final-arm64/run.log)：四BPP各一个已暴露字节的anonymous write拒绝被manager吞掉、各一个legacy源克隆读成默认值，共8失败，actual exit8/reaped。未暴露字节的intent与native普通clone共8行通过，另有init/cleanup两行。[父源码](parent-source/libs/image/tiles3/kis_tiled_data_manager.cc)和[最后测试补丁](parent-final-test.patch)保留。没有在父版本执行已知会消费空TileData的直接复制，也没有故意崩溃探针。

最初active-write夹具误要求未暴露字节的intent也拒绝，[初始8失败](parent-active-write-arm64/run.log)不算8个有效缺陷；修正后[parent-corrected-arm64](parent-corrected-arm64/run.log)只有4个exposed失败。初轮候选还暴露单参数表达式被解析为声明，以及成功hash复制多持一个默认backing用户引用，[21失败](candidate-target-arm64/run.log)和对应编译日志原样保留。修正后的目标集合[candidate-target-corrected-arm64](candidate-target-corrected-arm64/run.log)80/0/0，包括构造/default旧控制；它早于新增legacy控制，不累加为最终资格。

manager先准备canonical clone，再建立兼容hash；已有canonical源拒绝时抛已有std::bad_alloc，legacy源保持legacy，无空backend回退。memento bridge在hash复制前接入，native复制不再登记旧memento索引。extent在局部RAII资源交出前准备，原recalculateExtent政策复用。三个Tile复制构造共用原init，空TileData在acquire/register前抛同一构造失败。

chained hash复制委托原空表构造，成功的每个tile立即走原link/count；部分失败由正常析构归还已复制tile、默认backing和数组。删除重复array/default/manager/count初始化以及局部未安装chain。lock-free已有同一委托/析构政策，保留。测试直接实例化两种模板，前两tile复制后拒绝第三个，观察原detach和users归还再正常重试；这不是完整OFF或另一hash配置构建资格。

新增81个场景：active intent/exposed8、三Tile构造及manager在真实claim/physical预算拒绝下的standalone/batch64、两hash模板的部分构造清理1、native/legacy源8。最后解锁/取消后原exact bytes保持、活动write为零，解除拒绝后的clone读取成功。未取消调用者尚未交出的写责任，不放宽pin、refs/users、Reserved或Fresh条件。

[完整差集](candidate.patch)、[分列统计](diff-stat.json)与[删除检查](deletion-check.json)区分新增拒绝保证与等价清理；生产三文件+17/-35（净-18），测试两文件+217/-0。无新生产类型、公共API、字段、owner、队列、线程或锁；原工厂返回类型承接局部backend候选，未提高结构ratchet。

最终运行使用[runner](run_tests.py)，universal arm64/x86_64、offscreen、seed12345、LIMIT_LONG_TESTS=1。每进程source/runtime/Qt前后hash、dyld实际加载、exit/reaped/timeout存于各目录。早先final运行在局部backend类型收缩前，保留但不累加；最终以final-02及results.json为准。构建失败、修正和[配置身份](build-identity.json)保留，不重跑CP1长压测/默认abort，也不领取性能资格。

最终每架：DataManager1311、CPU Mutation1394、Reference790、PhysicalClaim397、ResidentRead221，全部0失败/0跳过；十进程8226/0/0，actual0/reaped、未超时。171份source和95份runtime并集一致，source与提交Git blobs匹配，见results.json。两个manager日志为[arm64](final-02-manager-arm64/run.log)/[x86_64](final-02-manager-x86_64/run.log)，其他进程命令和结果逐项列于机器汇总。

当前完整调用图87 TU、2176 APIs/27925 edges/27 callbacks、unresolved0；结构结果见[summary](callgraph-summary.json)、[无损gzip](reverse-callgraph-final.json.gz)、[generator](callgraph-final.log)和[checker](architecture-final.log)。初轮新增的manager类型引用越过旧上限1项，已改用原工厂返回类型；原图与[初轮结构失败](architecture.log)保留。26旧source checkpoint及inventory变化、memento include1>0和此前tile bridge引用13>9不冒充通过，正式结构冻结仍归CP3。

完整CP2继续开放。下一核对生产provider epoch/allocation ABA/晚completion联合时序，以及共同plan的before pin、physical、accounting、metadata、descriptor和install全部实际准备拒绝；原语/局部测试和总数不能替代缺失的生产联合证明。CP1保持关闭，M6/M7/M8正式0/3，persistent默认关闭。
