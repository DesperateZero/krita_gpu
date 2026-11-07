# CP2 原 raw 写准入与拒绝清理

2026-10-04 产品本地提交 `4b108d316c360b2d752d788799a9fffbe07ea863`，父 `b51a7602c82bbee6bf2a0df79400dd943d6df5b6`；文档起点 `c1d7447effff26fa120ba02955eaecee8b9fbb14`。外层Git记录的旧`krita`指针为`0933ea04ddbe8bb58c04dc891d864be8cd95d778`，本轮开始时已经与产品HEAD不符；该既有差异不混入文档提交。本轮产品增量只比较实际父`b51a`，不把旧指针之后的累计实现计成本轮。当前裁决见 [92 §16.109](../../92_br1_m6_m8_execution_baseline.md#cp2-raw-access-delivery)。本轮 source/runtime 前后哈希和最终 Git blob 核对见 [机器结果](results.json)，增量见 [产品补丁](candidate.patch)及 [逐文件增删](diff-stat.json)。

真实 claim 冲突或 TileData payload 容量拒绝时，父版本 `tryWriteData` 返回空结果，另外三个 raw 入口在 SAFE ASSERT 后仍访问缓存 before-image。原私有 `markPageStoreWriteDirty` 改为返回准入事实，`data/tileData/setData` 消费同一结果，`tryWriteData` 删除重复 ensure 并保留 ABI。copy/purge 的嵌套锁用原局部 scope 统一归还；clear/extent/debug 和 codec 消费空结果，沿原回滚或 false 返回。legacy codec 的原 header buffer 改为局部 RAII，拒绝和正常解码均归还。

生产五文件 +70/-71（净-1），测试两文件 +180/-0。新增的是拒绝后的旧值保护；等价收敛是共用准入、删除重复 ensure 和散布的手工 unlock。无新增公共/受保护签名、字段、include、friend、锁、TLS、owner、队列或费用；行数不代表性能收益。原 memento `registerTileChange` 在 bridge 存在时不执行；iterator/wrapper 已有空结果处理，继续保留各自 scope/锁。原 raw COW 引用、batch Reserved pin、refs/users 排斥和 Fresh 政策保持。

| 运行 | 实际结果 | 证据 |
|---|---|---|
| 父版本 arm64，新增 raw 64行 | 18通过/48失败/0跳过，actual exit 48/reaped | [日志](parent-arm64/run.log)、[身份](parent-arm64/identity.json)、[当时测试源码](parent-test-source/kis_tiled_data_manager_test.cpp) |
| 候选 arm64，两个新方法 | 82/0/0，exit0/reaped；不重复计入最终总数 | [日志](candidate-target-arm64/run.log)、[身份](candidate-target-arm64/identity.json) |
| 完整已注册 DataManager，arm64/x86_64 | 每架1185/0/0，exit0/reaped | [arm64](candidate-manager-arm64/run.log)、[x86_64](candidate-manager-x86_64/run.log) |
| 完整 PhysicalClaim，arm64/x86_64 | 每架397/0/0，exit0/reaped | [arm64](candidate-physical-arm64/run.log)、[x86_64](candidate-physical-x86_64/run.log) |
| 完整 ResidentRead，arm64/x86_64 | 每架221/0/0，exit0/reaped | [arm64](candidate-resident-arm64/run.log)、[x86_64](candidate-resident-x86_64/run.log) |
| 生产 recoverable/fallback/concurrent-consumer handoff，arm64/x86_64 | 每架290/0/0，exit0/reaped | [arm64](candidate-cpu-arm64/run.log)、[x86_64](candidate-cpu-x86_64/run.log) |

最终八进程共4186/0/0，均未超时、实际加载 `_build-br0-cpu/bin` 的候选库，源码与库哈希运行前后不变。64个raw场景覆盖1/4/8/16 BPP、四入口、standalone/batch、真实同页foreign claim与8.5MiB payload耗尽；16个codec场景同时检查两种codec的嵌套编码/解码拒绝、原锁归还和后续解码恢复。原exact读在拒绝、取消foreign owner和后续新操作成功后字节不变；没有把后续新操作成功当成同一失败batch的自动continuation。

[runner](run_tests.py)保存各轮实际命令、环境、源/二进制/库/Qt哈希、dyld日志、actual exit/reaped和超时事实，每轮另存当时runner。父版本代码来自父Git blobs，新增测试源码已逐哈希复原保留。候选源码逐项与产品提交blob一致。配置是当前universal x86_64/arm64 CPU构建、Qt offscreen、seed12345、`LIMIT_LONG_TESTS=1`（stressTest为8线程/8worker/10000cycles），无失败退出替换或插桩库；[构建身份](build-identity.json)记录Apple clang17、macOS15.7.3及CMake/cache哈希。完整注册方法运行不表示未启用的100000cycles长测试或完整M6矩阵资格。

[parent build](parent-build-01.log)、[candidate build](candidate-build-02.log)、[最终测试重编译](candidate-build-03.log)均成功。`candidate-build-01.log`保留一次未注册旧compressor测试target的配置失败；该旧文件仍使用已删的unlock API且不在CMake注册，本轮实际codec覆盖加入现有manager测试，没有新测试target或生产测试入口。

[当前调用图](reverse-callgraph.json)基于实际compile database解析87 TU，2175 APIs、27663 edges、27 callback registrations、unresolved0；[生成日志](callgraph-01.log)。旧图的[首次checker失败](architecture-01.log)和使用当前图的[第二次checker失败](architecture-02.log)均保留。第二次只剩旧source checkpoint及既有`kis_memento_manager.cc` direct_includes 1>0的ratchet差异；本轮五生产文件没有新增include或扩大字段/API。没有刷新baseline或提高侵入上限，结构门未通过。

完整CP1仍按§16.108关闭，原8/24MiB长压力和默认abort崩溃探针未重跑。此轮关闭raw拒绝的有限缺口；完整CP2的原exact受保护选择、Reserved batch权限、epoch/ABA/晚completion和全部准备拒绝联动仍开放，接续见 [NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md)。完整ON/OFF、TSAN、M6资格与性能本轮未取得；M6/M7/M8正式0/3，persistent默认关闭。
