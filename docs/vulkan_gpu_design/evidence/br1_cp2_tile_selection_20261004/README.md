# CP2 原 G0 选择与只读 wrapper 寿命

产品 `5a3767cc6f9af6e3885c3eb634822798ed99553e`，父 `7d425255e2364339cc5f9cedf4472e1377f44053`，文档父 `c7b0d06ee5e880ff4e15d044f0c919ee7418d17b`。当前裁决见[92 §16.111](../../92_br1_m6_m8_execution_baseline.md#cp2-tile-selection-delivery)，完整差集见[cp2-audit.json](cp2-audit.json)。原外层旧krita gitlink不混入文档提交。

父版本在真实process metadata硬满下32行全部失败，actual exit32/reaped；8个commit/old场景在首次准备失败后仍返回wrapper，下次冷读改选current `0x72`，而原G0是 `0x31`。有效父红见[parent-selection-02](parent-selection-02-arm64/run.log)、[源码](parent-kis_tiled_data_manager.cc)和[测试补丁](parent-tests.patch)。第一次夹具把同默认值写入误当allocated，其16行presence断言不成立；[初始运行](parent-selection-arm64/run.log)及[parent-tests-01.patch](parent-tests-01.patch)原样保留，不用它领取32行覆盖。

先capture G0，再从有效ReadPage取得原TileData，在原pin释放前构造COW wrapper；presence与bytes使用同一read。getter拒绝返回空值并报告原job failure context。old wrapper在manager hash/detach生命周期之外，因此只保留原存储及既有只读标记，不保留backend/root/cache。write lock在原barrier拒绝，删除旧ensure后置检查。外层寿命[负例](readonly-parent-arm64/run.log)基于中间候选，四BPP均仍授予write intent、actual4/reaped；当时源码见[readonly-parent.patch](readonly-parent.patch)，没有执行悬空backend的数据访问或crash探针。

删除attach helper、复制current后刷新G0、独立presence查询、临时read-cache分配及bridge oldData参数/分支；全部声明/override/生产和测试caller迁移，没有旧overload。原生captured read的原version重解析继续用既有保护；独立旧wrapper只代表其原物理存储，不伪造新的逻辑重解析权限。raw refs/users、pin、Reserved与Fresh控制保持。

[生产/测试完整差集](candidate.patch)及[分列统计](diff-stat.json)：生产六文件+44/-31（净+13），测试四文件+160/-31（净+129）。新增拒绝/原版本/manager外层寿命保证与等价删除分列，净增不算去重收益；无新类型、状态字段、owner、queue、thread、mutex或上层API。原lock中新增只读标记检查的性能仍待正式比较。[静态删除核验](deletion-check.json)确认旧helper无caller、旧桥选择参数消失、G0无backend/cache及二次presence。

最终运行使用[runner](run_tests.py)，补齐`.cc`源码哈希；universal arm64/x86_64、Qt offscreen、seed12345、LIMIT_LONG_TESTS=1。完整注册manager不等于未启用的100000cycles长测试。每进程命令、source/runtime/Qt前后哈希、dyld实际加载、exit/reaped/timeout均存于对应目录；[机器汇总](results.json)逐项核对最终source与产品Git blobs，共8064/0/0。

| 最终源码 | 每架结果 | arm64 / x86_64 |
|---|---|---|
| DataManager | 1230/0/0 | [arm64](final-05-manager-arm64/run.log) / [x86_64](final-05-manager-x86_64/run.log) |
| CPU Mutation | 1394/0/0 | [arm64](final-05-cpu-arm64/run.log) / [x86_64](final-05-cpu-x86_64/run.log) |
| Reference | 790/0/0 | [arm64](final-05-reference-arm64/run.log) / [x86_64](final-05-reference-x86_64/run.log) |
| PhysicalClaim | 397/0/0 | [arm64](final-05-physical-arm64/run.log) / [x86_64](final-05-physical-x86_64/run.log) |
| ResidentRead | 221/0/0 | [arm64](final-05-resident-arm64/run.log) / [x86_64](final-05-resident-x86_64/run.log) |

早先candidate、final-manager、final-02/03运行对应不同候选，保留但不累加成上述资格。build05遗漏两处测试旧实参，原编译失败见[candidate-build-05.log](candidate-build-05.log)，build06同批修正。构建配置见[build-identity](build-identity.json)。

当前87 TU调用图2176 APIs/27715 edges/27 callbacks、unresolved0，完整原图无损保存为[reverse-callgraph-05.json.gz](reverse-callgraph-05.json.gz)，解压字节及两种SHA见[summary](callgraph-summary.json)。generator实际读取compile database、checker使用未压缩原图；原命令/结果见[生成日志](callgraph-05.log)、[结构日志](architecture-05.log)。结构门未通过：26个旧source checkpoint及memento include、此前bridge引用13>9差异保留；没有改baseline或提高ratchet。

完整CP2保持开放，下一轮先核验clone/hash raw拒绝接续，再核验生产epoch/ABA/晚completion与共同plan全部准备失败的有限清单。CP1不重开、8/24MiB长压测与默认abort不重跑；CP3、M6/M7/M8正式资格及ON/OFF/性能不由本批领取，persistent默认关闭。
