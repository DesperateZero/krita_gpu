# 原 metadata 配置目录的实际收费与残余回收

本批接续92 §16.65的CP1固定成本差集。产品父提交为`c8de106aacba42a9b4e5fbaafc6fa4d358bddbfa`，文档父提交为`ae9332c73304c660b432b684b4a94c71240ce573`；最终产品身份见[Git记录](git-round-identity.json)，完整改动见[生产差集](production-incremental.diff)和[统计](source-metrics.json)。当前结论来自检出代码和活动合同，没有读取archive。

原`configure`先估算shard对象和两指针控制块、三个arena目录及shard数组的总额，分配后再算容量、提交手工fee；失败时清空元素却留下数组capacity。现在原retained allocator直接承担shard对象/实际shared控制块、immutable shard指针数组、三个typed arena目录和publication identity的实际分配请求。原配置锁下只准备一个局部完整候选，全部成功后发布directory和identity，再release发布原operational事实；拒绝则同候选析构返还实际费用，同对象可重新配置。

删除`directoryCharge`、`shardObjectBytes`、`maximumDirectoryBytes`、`allocatedDirectoryBytes`、`directoryBytesForLimit`、`directoryReservation`及手工提交/释放、分配后超预留拒绝。原block/hash收费、arena hardceil、shard数量、slot generation、claim/cancel/分批cleanup政策保留。新identity仍只配置一次；prepare和install都先acquire operational再读取identity，未配置/foreign安装仍消费候选并按原责任清理。最终审查发现install原入口欠这次acquire，已补齐并重新构建、验证；不把前一轮运行物继承成最终资格。

`owningCapacityBytes`的实际consumer是原诊断/测试；其注释明确为shard对象payload和原hash/index容量费，不再添加两指针控制块估算。实际目录/control费用查原backing usage，不把该诊断字段升为准入、关闭或调度事实。生产3文件+36/-86净-50；测试1文件+128/-0；ownership及生成物分别列在统计。新增实际allocator成员有真实保留成本，未新增上层API、持久业务阶段、锁、TLS、队列或外部生产侵入文件。

## 实际边界和执行

新增7个数据行：1/4/64 shards真实共享父容量少一个字节，连续三次配置拒绝后operational、shard/page/owning capacity和reserved均不残留；释放原filler后同对象配置成功、第二次配置拒绝、真实registerPage仍可用。空配置实际请求费分别为25,824、103,152、1,649,712字节，双架构一致。另有1/64 shards × cancel/已安装cleanup四行：coordinator和child controller销毁后原candidate仍保留shard/parent和实际费用，最后取消或clearBatch(1)精确归费，最后parent引用退出。真实一字节压力不是状态开关；三个typed arena目录仍按原有限hardceil预留最大目录，未降低固定成本。

新增断言还覆盖原合法publication向未配置owner安装时的拒绝/候选消费，再确认该owner可配置。此行为测试不声称TSAN或并发两次序资格；identity同步依据是原一次发布的release/acquire合同。

实际命令（从相应仓库目录执行）如下；每次结果/原Qt输出保留，既有manager `LIMIT_LONG_TESTS=1`、stress/benchmark和业务六方法输入未变。

```sh
/Users/apple/krita_gpu/.venv/bin/ninja -C _build-br0-cpu KisPageStoreCpuMutationTest KisPageStorePhysicalClaimTest KisPageStoreResidentReadTest KisPageStoreReferenceTest kis_tiled_data_manager_test FreehandStrokeTest MatchedFreehandBaselineTest
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py
python3 docs/vulkan_gpu_design/evidence/br1_metadata_directory_storage_20261003/run_regressions.py --round 02
python3 docs/vulkan_gpu_design/evidence/br1_metadata_directory_storage_20261003/freeze_evidence.py --round 02
```

构建01使用最初实现和旧测试；构建02保留新测试的typed char allocator被传入void*导致的两个编译错误，修正测试指针后构建03成功。目标31/0/0及初始完整双架十四进程7560/0/0、六方法三对串行压力66/0/0均绑定构建03；其[初始结果](initial-regressions.json)、[压力身份](pressure-final-runtime.json)和全部日志保留。最终install同步修正后使用构建04，最终十四进程为**7559/1/0、均正常退出**，唯一失败是arm64 24MiB pressure的overlay surface准备拒绝，cancelCallbacks实际1、期望0，详见[原日志](FreehandStrokeTest-final-02-arm64.log)。本次未独立测定该拒绝请求的字节，不能继承§16.65的8304字节测量。[最终结果](final-regressions.json)和[总计](final-regression-totals.json)保留失败；`-final-02-`日志对应最终源码，`-final-01-`和`pressure-final-*`不继承新运行物资格。

最终[93源码](source-identity.json)、[109运行物](runtime-identity.json)、[构建配置](build-identity.json)、[删除/费用检查](delivery-checks.json)共同绑定；最终运行物测试前后逐项相同。原Matched像素、callback和owner释放与§16.65一致；没有新upstream独立配对性能结果。

## 保留边界

本批关闭原配置目录/control的实际收费、局部失败归费和晚candidate最后释放；不关闭完整CP1。64 shard空配置仍收取约1.65MB，eager全目录和其峰值继续同一固定成本审查。metadata Private/authority本体/control、standalone/bootstrap、Qt输入/注册/map、link本体/control及其他wrapper/cache仍未全量验证。

§16.65的后续surface准备8304字节拒绝和8MiB backend初始准入缺口仍开放；原压力输入/限额/断言未修改，有限绿样本不关闭反例或授予完整准入后cancel资格。此前59123/70089/83020仍UE，见[进程记录](prior-failed-processes.txt)，本批正常退出不证明全部尝试drain。完整CP0/CP1、全局allocator/TSAN、公平、原job continuation、BR1-PERF及M6/M7/M8正式0/3保持，persistent策略默认关闭。
