# 原 metadata authority 配置准入与最后释放

产品提交`4c45738186bccf095b8cefd409e409c8accd637a`，产品父`453a5e9d1403da28aad85e51b68d1c995080ed6c`、文档父`413b7e03454b68f52b889fd32826e2d071a3a6ff`，见[Git身份](git-round-identity.json)。本批接续92 §16.67的同一配置/实际收费/最后free责任，未读archive、未push；不重领已收费目录或eager预留。

## 原责任与同批删除

原Private构造make_shared的authority对象/control未收费，attach重设budget并reset accounting owner，第一次reserve才补建owner且可能拒绝。现在预算选择仍在原configurationMutex下、配置前不分配authority；configure以原retained allocator准备authority实际对象/control、shards、immutable目录和identity，局部候选全部成功后一起发布原operational。authority在发布前已经持有原accounting owner，后续reserve不再有补建owner分支；实际reservation/slot准入和budget不可用仍有真实来源，不能删除。

原shard、PreparedPublication Data和KisPageMetadataReadCleanup继续持有同一authority。coordinator退出detach新准入；实际authority/control与block/hash费用都沿原accounting寿命，晚controller退场也不能提前归费。read/captured cleanup身份比较改为先经原shardFor acquire配置发布，再核对原shard authority；原foreign拒绝保持，没有另加锁或第二可见性事实。

删除authority::attach、构造期make_shared和reserve的后置owner准备/catch。生产1文件**+17/-29净-12**，测试1文件**+99/-2**、ownership**+1/-1**、生成**+6063/-5901**分别见[统计](source-metrics.json)与[生产](production-incremental.diff)/[测试](tests-incremental.diff)差集。新增原Private预算选择指针8B，表示配置前已有的attach事实；没有新type/业务阶段/锁/TLS/队列/上层API/外部侵入。

直接在constructor收费会使现有configureLimits/shared挂接被非零live合同拒绝；只对make_shared补估算无法覆盖实际control请求和最后free。选择把authority移进原完整候选，未放宽controller配置合同。Private本体及内嵌standalone controller仍需随root bootstrap准备/配置责任闭合，不将本批收费迁移记为它们已经完成。

## 实际拒绝与晚释放

双架1/4/64 shard空配置实际请求费为**1,312/4,912/76,912B**，相对父源码均增加**64B**，覆盖原authority本体及实际共享control的一次allocator请求；不是RSS或完整bootstrap费用。旧对象终于收费是保证成本，不能记内存净删。数据见[交付检查](delivery-checks.json)。

原配置数据扩为1/4/64 shards×只余1B/完整候选少1B六行。夹具先暖原accounting owner和reservation slots；只余1B时第一个实际authority/control分配被拒绝，没有shard或候选残余。各行连续三次失败、预算选择不分配、未配置heads为空、解除压力后原对象重试/真实registerPage均通过。原目录并发consumer包含authority可见性访问，但不授予完整TSAN/两次序资格。

原publication/detachment八行晚Data继续通过。新增read-release/last-use ack×显式clear/析构四行：coordinator/controller退出后只剩detached read cleanup，没有shard/Data替它保活。parent最后外部强引用退出时仍被原accounting尾保留；重取parent并填满真实额度，最后clear或析构无需分配，原authority/control、blocks、accounting owner及child登记费用精确回原基线，最后parent弱引用失效。clear重复、原foreign cleanup/跨shard拼接/移动赋值消费者保持。

## 实际执行

构建01使用原七个目标，exit0；首个目标命令含两个未核对的方法名，QtTest在执行前拒绝（0/2/0、runner exit1），原[结果](authority-targeted-arm64-result.json)和日志保留。修正为实际名称后[目标02](authority-targeted-02-arm64-result.json) **50/0/0、exit0**，没有改源码或削弱断言。

最终同源码双架七组十四进程**7584/0/0、全部exit0**：每架CPU1324、Physical393、Resident221、Reference783、完整manager1057、Freehand11、Matched3。原manager LIMIT_LONG_TESTS=1、stress/benchmark保留；原六方法压力组合另跑三对**66/0/0、六进程exit0**，原24/8MiB/输入/线程/慢reader/递归producer/undo-redo断言保持。[完整矩阵](final-regressions.json)、[汇总](final-regression-totals.json)和[压力](pressure-final-results.json)分别保留。

```sh
/Users/apple/krita_gpu/.venv/bin/ninja -C _build-br0-cpu KisPageStoreCpuMutationTest KisPageStorePhysicalClaimTest KisPageStoreResidentReadTest KisPageStoreReferenceTest kis_tiled_data_manager_test FreehandStrokeTest MatchedFreehandBaselineTest
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py
python3 docs/vulkan_gpu_design/evidence/br1_metadata_authority_storage_20261003/run_regressions.py --round 01
python3 docs/vulkan_gpu_design/evidence/br1_metadata_authority_storage_20261003/reproduce_pressure.py --label pressure-final --count 3 --current-runtime --keep-going
python3 docs/vulkan_gpu_design/evidence/br1_metadata_authority_storage_20261003/freeze_evidence.py --round 01
```

[93源码](source-identity.json)、[109运行物](runtime-identity.json)、[四项构建配置](build-identity.json)与产品commit绑定；最终测试前后运行物逐项相同。图87TUs/2023APIs/25535edges/21callbacks；架构21manifest/25ownership/16census/19外部侵入及原ratchet不变。Matched字节/callback/原owner释放与父源码相同，没有新增upstream配对性能。

## 未关闭条件

Private本体、内嵌standalone controller、其他bootstrap/Qt注册/link/cache、全部参与者总峰值/永久拒绝/停止/晚handle/自主drain仍欠。有限绿矩阵和压力三对不授完整24MiB总峰值资格；8MiB原取消夹具未独立证明完整准入后取消，历史8304B只属其冻结源码。旧59123/70089/83020仍UE，见[当前进程记录](prior-failed-processes.txt)，不能称所有尝试drain。

原block/hash手工fee保持。完整CP0/CP1、全局allocator/TSAN、公平、原job continuation与BR1-PERF开放，M6/M7/M8正式0/3、persistent默认关闭，不据提交/测试数或行数扣人日。文档/源码交付检查见[检查记录](documentation-checks.json)，本批原始文件大小/SHA256见[清单](evidence-inventory.json)；清单不含自身，原日志和diff上下文不改写。
