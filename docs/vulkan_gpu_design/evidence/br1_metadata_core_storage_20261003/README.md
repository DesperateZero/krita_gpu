# 原 metadata Private 配置准入及生产固定成本清理

产品提交`ec3cebba5b4652c04c856b262065dde092c938b4`，产品父`4c45738186bccf095b8cefd409e409c8accd637a`、文档父`2c534180589f7910dbe81daaf7a668544d535645`，见[Git身份](git-round-identity.json)。当前裁决归92 §16.69/§17。本批未读取archive、未push；继续原配置/收费/最后free责任，不重领已经收费的目录/authority。

## 最终责任与删除

冷facade保存原预算选择、配置锁及Debt接收事实，不分配Private。configure通过原retained allocator准备实际Private，authority/shards/目录/identity都放入这一局部候选；完整成功后一次release发布core指针。全部原shard、prepare/install、查询和诊断consumer acquire同一发布事实。拒绝和最终析构共用Private::destroy，保存原allocator直到实际free；晚Data/shard/read cleanup仍分别拥有原authority/accounting寿命，不新增尾owner。

同批删除未收费eager new Private、独立operational标志、原Private中的冷配置事实及始终存在的standalone controller值。原Store attached生产路径不创建standalone controller；实际未attach的reference入口在configure中创建原controller，保持可用性。保留不可重配、owner静止析构、foreign/claim、实际reservation/slot和detach后的真实拒绝；原block/hash手工fee继续。

直接constructor收费会违反Store的原shared/limits→configure顺序；后置估算补费增加第二收费权威。shared core会引入额外共享寿命和控制存储，当前Private没有跨coordinator存活的consumer；因此采用原配置候选中的独占core和原子裸指针发布，不增加RCU/共享寿命。内联全部Private会暴露shard/controller实现及依赖，冷facade只搬原必要配置事实。

原shardFor/sharedShardFor改为接受已acquire的core，旧签名删除；新的私有constructor/destroy分别用于配置构造和拒绝/析构，均有真实consumer。图API净增2（2023→2025），callback registration 21→22是同一候选deleter地址，不是新的业务通知协议。

## 保证成本与对象尺寸

生产两文件**+128/-94净+34**、测试一文件**+21/-2**、ownership**+1/-1**、生成物**+3935/-3719**分别见[统计](source-metrics.json)与[生产](production-incremental.diff)/[测试](tests-incremental.diff)。净增兑现Private实际收费、完整候选销毁及空core入口迁移，不算等价去重。

双架实际编译器布局见[修改前](layout-before.json)、[最终](layout-final.json)，原始stdout日志也保留。Private **1,488→104B**，facade **8→56B**；attached生产二者对象尺寸合计**1,496→160B，减少1,336B**。删除的内嵌controller本体1,352B，余下差额来自配置事实搬迁、去掉旧标志和保留实际free allocator。尺寸不含allocator开销，不是RSS、总峰值或正式性能结论。

实际配置请求收费双架1/4/64 shard为**1,416/5,016/77,016B**，均比父源码新增**104B**，恰为原Private实际allocator请求；已有authority/control64B保持。真正standalone仍创建1,352B controller，facade+core+controller合计1,512B，比旧形态多16B；controller体及含facade的Store根对象费用仍未完整qualified。不能把生产删除收益套到standalone，不能把新增收费记内存删除。[交付检查](delivery-checks.json)分列两者。

## 实际拒绝、并发和最后free

原配置六行覆盖1/4/64 shards×第一笔只余1B/完整候选少1B。夹具先暖原accounting owner/reservation slots；第一笔实际Private分配拒绝，authority/shards尚未分配。每行连续三次失败、无core/目录容量/费用残余，解除压力后同一facade重试和registerPage通过。新增冷facade先attach再configureShared/configureLimits的原顺序检查；未配置shard/pageKeys/snapshot/read binding/replica/metrics/count/footprint继续原空值。

原并发一次配置、foreign/claim、晚publication/detachment八行、仅read cleanup保活的controller后父硬满clear/析构四行继续通过，原parent弱引用在最终free后失效。未attach的standalone recoverable outcome9晚候选由原完整Reference数据行实际消费，行名保存在交付检查；没有用parent附加寿命替它遮蔽controller销毁。有限交错不授全局TSAN/完整两次序资格。

## 实际执行与身份

构建01的测试漏传configureLimits第二参数，exit1；修正后构建02 exit0。目标[50/0/0](core-targeted-arm64-result.json)。最终同源码双架七组十四进程**7584/0/0、全部exit0**：每架CPU1324、Physical393、Resident221、Reference783、完整manager1057、Freehand11、Matched3，见[完整记录](final-regressions.json)与[汇总](final-regression-totals.json)。原manager LIMIT_LONG_TESTS=1、stress/benchmark不变。

原六方法组合追加三对**66/0/0、六进程exit0**，原24/8MiB、输入、线程、慢reader/递归producer/undo-redo断言保持，见[压力记录](pressure-final-results.json)。首个冻结脚本在runner尚未完成时按六进程完整性断言拒绝，日志[保留](freeze-before-pressure-completion.log)；没有把打印Qt totals当退出，等实际六进程退出后最终冻结通过。

```sh
/Users/apple/krita_gpu/.venv/bin/ninja -C _build-br0-cpu KisPageStoreCpuMutationTest KisPageStorePhysicalClaimTest KisPageStoreResidentReadTest KisPageStoreReferenceTest kis_tiled_data_manager_test FreehandStrokeTest MatchedFreehandBaselineTest
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py
python3 docs/vulkan_gpu_design/evidence/br1_metadata_core_storage_20261003/capture_layout.py --phase final
python3 docs/vulkan_gpu_design/evidence/br1_metadata_core_storage_20261003/run_regressions.py --round 01
python3 docs/vulkan_gpu_design/evidence/br1_metadata_core_storage_20261003/reproduce_pressure.py --label pressure-final --count 3 --current-runtime --keep-going
python3 docs/vulkan_gpu_design/evidence/br1_metadata_core_storage_20261003/freeze_evidence.py --round 01
```

构建/graph命令从krita仓库运行，证据runner从外层根目录运行。修改前layout在父源码上实际运行并冻结，重放before必须先选择该父源码，不能对新源码改label伪造。当前[93源码](source-identity.json)、[109运行物](runtime-identity.json)、[四构建配置](build-identity.json)绑定产品commit，运行物测试前后逐项相同。图87TUs/2025APIs/25550edges/22callbacks；架构21manifest/25ownership/16census/19外部侵入及原ratchet保持。Matched字节/callback/原owner释放同父源码，没有新增upstream性能配对。

## 尚未关闭

runtime Private及生产无用controller已收口；真正standalone controller、Store/其他根对象和process bootstrap、Qt注册/link/cache、全部参与者总峰值/永久拒绝/停止/晚handle/自主drain仍欠。有限绿样本不授完整24MiB总峰值或8MiB完整准入后取消资格；历史8304B只属冻结旧源码，旧59123/70089/83020仍UE，见[进程记录](prior-failed-processes.txt)。

完整CP0/CP1、全局allocator/TSAN、公平/原job continuation及BR1-PERF开放，M6/M7/M8正式0/3、persistent默认关闭。活动差集已更新，不重领Private/authority/目录。交付检查见[文档检查](documentation-checks.json)，本批原始文件大小和SHA256见[清单](evidence-inventory.json)；清单不含自身，原日志/diff上下文不改写。
