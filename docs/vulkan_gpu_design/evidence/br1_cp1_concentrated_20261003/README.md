# CP1 当前CPU存储集中补齐：实际容量、同owner拒绝与最后free

产品提交 `b10b2913a69604d42b51cac83ba81214d30d43de`，父 `1d29ff82487bf6b936b1d187ec9816db0fe7c204`；外层父 `c5a829a958ce85a06461fe60de0eb341a6d3e32a`。实施依据为当前代码与 [92 §16.72](../../92_br1_m6_m8_execution_baseline.md#cp1-concentrated-storage-delivery)、cohesive-refactor 和原 MI1–MI8 合同；未读取 archive、push、增加原业务预算或引入新业务失败阶段。本包先集中实现，再统一编译/运行；新失败回原owner修复后重新冻结候选。

## 实现和清单边界

[allocation-contracts.json](allocation-contracts.json) 的16组覆盖 process/bootstrap、冷根、Registry、provider、observer登记、metadata core/indices、value/capture、epoch/tree、read/default、mutation、Ledger/publication、history/backend、extent、runtime/deferred、close。每组列实际对象、收费规则、接受/拒绝、最后free与真实测试。共享control、弱尾、实际容器capacity与旧/新数组重叠容量均随实际存储保留费用，physical free之后才归费。

[allocation-sites.json](allocation-sites.json) 从最终115个源码身份中筛出92个image参与者文件、1642个准备/分配/容器/释放/native runtime复核位置，生成器为 [collect_allocation_sites.py](collect_allocation_sites.py)。它用于对照真实调用点和上述owner合同，包含未改文件、别名和兼容边界；不宣称全局heap trace、每个C++表达式自动穷尽或每个位置都独立故障注入。当前原runtime-census仍是16组，不增一个没有独立owner的汇总组。

| 工作组 | 实际完成内容 | 同批回收 |
|---|---|---|
| provider／Registry／Ledger | 原冷allocator准备根/control/Private；bootstrap有限process parent，原live容量适配才采用产品policy；observer/Transition/source/receipt及强弱caller统一迁移 | 未收费Qt共享创建/control、无预算无限入口；不再给已live对象另挂第二parent |
| TileDataStore登记 | adoption先准备实际observer和registration节点，接受后转交原intrusive记录，资源存活至最后节点free | 像素后才尝试新登记分配的旧顺序 |
| metadata与capture辅助 | paid COW snapshot/format byte、扫描原输入验证；actual map/index/link节点和容量收费，原Entry释放活动 | MetadataOwnedHash/Capacity估算、重复验证集合、独立shared cleanup job、clear先pop导致丢活动 |
| backend／history／cache／extent | paid tracking/active/memento/thread/cache记录，client及输出容量前置，scope原abort；generic PMR extent两轴准备 | cache hash+order重复存储、匿名lease集合、clear复制列表、eager空extent和Qt行列投影 |
| deferred／runtime | 原Data就是cleanup job；statistics/control收费，原executor queue；Darwin显式stack及native region收费，永久stop join、晚handle归费 | Qt pool/runnable及普通clock/native隐性拥有存储；业务task与终结owner不另建 |
| close与原竞争复验 | 原Ledger terminal节点转交，原pending退休记录保留；同Growth recapture/build，实际free才归费 | shutdown handles数组、seenReplicas、动态诊断拼接、固定三次竞争业务拒绝、空free误退活费 |

调用者拥有的 Qt导出/输入、已有DataManager/Tile/pool/swap和undo载荷没有被再次收费；输入stream Qt临时值仍在外部兼容边界。Qt post-routine/global/TLS、malloc内部、其他进程分配和非Darwin native线程未取得全局allocator/RSS资格。Vulkan foundation/UI均OFF，其兼容签名同步迁移但未编译验收；原BR0/BR3 prototype和可选SSD persistence资源不混作CPU资格。

## 最终同源验证

构建 `_build-br0-cpu` 为 `RelWithDebInfo`、`x86_64;arm64`、`BUILD_TESTING=ON`、`LIMIT_LONG_TESTS=ON`，Vulkan两开关OFF；四配置与原始身份完全相同。最终 [compile-integration-21.log](compile-integration-21.log) 编译进程exit0。保留全部21份编译日志，不用compile失败/警告计运行资格。

[regressions-06.json](regressions-06.json) 是11组双架22个串行原进程，**8082 passed / 0 failed / 0 skipped，全部exit0**；每条有实际command、pid、Qt Totals、退出码和原日志。各架构数量相同：

| 原binary | 每架passed |
|---|---:|
| KisPageStoreCpuMutationTest | 1333 |
| KisPageStorePhysicalClaimTest | 393 |
| KisPageStoreResidentReadTest | 221 |
| KisPageStoreReferenceTest | 783 |
| FreehandStrokeTest（原六方法） | 11 |
| MatchedFreehandBaselineTest | 3 |
| kis_tiled_data_manager_test | 1057 |
| KisCompletionRegistryTest | 87 |
| KisPageStoreFoundationTest | 28 |
| KisPageStoreReadBaselineTest | 45 |
| kis_transaction_test | 80 |

[pressure-final-06-results.json](pressure-final-06-results.json) 保留三对原六方法，**66/0/0、六exit0**；[pressure runner](pressure-final-06-runner.log) 确认测试前后源码和运行物不变。普通freehand、persistent success/cancel、原四失败点、24MiB/swap0压力与8MiB取消输入/预算/像素断言保持；这仍不等于8MiB完整准入后取消和永久热点进度都已取得资格。

最终目标 `admissionStorageRevalidatesGrowth` **3/0/0、exit0**，见 [target result](growth-recapture-nullfree-final-arm64-result.json)。局部fixture在256KiB实际额度内先准备Growth，再填恰满，六轮revision变化只重用原数组，稳定后恰满安装；原1000 entries增长/复用检查保留，结束严格回312B controller baseline。新增 `processStorageRejectsAndRetains` 覆盖真实根/COW/provider/oracle/extent/close的连续拒绝、原值/费用保留、同owner恢复、永久retire拒绝保原记录及最后弱尾free；`runtimeStopsAtCapacity` 是最后方法，覆盖硬满下永久stop、无新callback、晚handle及实际线程费用回收。原Ledger/metadata/tree/capture/read/retirement目标同时包含在完整原矩阵中。

Matched普通业务的blank/painted SHA256、segment/update callback、strategy/image实际析构与父批原记录逐字段相同；不比较不同架构的时间，未取得正式性能资格。环境仍是offscreen、seed12345、相同依赖和原plugin目录；manager的LIMIT_LONG_TESTS=1保持，测试总数不作覆盖率。

[source-identity.json](source-identity.json) 119项＝115生产/测试/tool源码＋额外四audit合同/生成身份；[runtime-identity.json](runtime-identity.json) 113运行物、[build-identity.json](build-identity.json) 四配置、[git-round-identity.json](git-round-identity.json) 绑定产品commit。初始93源码和109运行物另存，四新增运行binary加入最终清单。[freeze-postcommit-06.log](freeze-postcommit-06.log) 验证所有最终源码/运行物/配置及完整22＋6记录，拒绝混合不同候选。

[architecture-final-06.log](architecture-final-06.log) 和 [tool-self-tests.log](tool-self-tests.log) 通过：87TUs、2158 APIs、27137edges、25callbacks；21manifest、25ownership、16census和19外部侵入文件。原ratchet无放宽：backend_duplicate_state两项收紧为零，manager identifier25→24，其他入口/字段/符号上限不扩张，见 [ratchet-comparison.json](ratchet-comparison.json)。初冻结错误要求所有ratchet值完全相等而拒绝，[失败日志](freeze-precommit-06.log) 保留；最终逐字段检查只允许相等或收紧，未扩张阈值。

## 失败与修复链完整保留

| 原尝试 | 实际结果及原责任修复 |
|---|---|
| regressions-01 | CPU三失败后stop移动clock仍解引用旧member，pid32658无正常Totals/退出；改为同local clock。原journal refill、登记顺序、process slot warm夹具也修正；focused repairs9/0/0。 |
| regressions-02 | 全22进程实际退出；Reference两架各五失败，x86 CPU一次引用断言竞争。真实clear先pop丢publication activity，修同Entry.releaseActivity；测试旧估算改按真实node，合法活动占用仍计费；CPU等待原executor结束再断言，保留refs==1。focused metadata19/0/0。 |
| regressions-03及pressure-final | 回归8082/0/0后原三对压力65/1/0、六正常退出；x86普通笔画像素失败伴随`mutation admission changed during storage preparation`。原固定三次竞争拒绝导致真实partial pixels，修为同Growth recapture。旧pressure收尾又因把会重新生成的audit graph当生产源码而拒绝，原记录保留，后续生产115与audit身份分列冻结。 |
| regressions-04 | 改后CPU/physical/resident通过；新growth fixture64KiB不能容纳后续原1000 entries，Reference uncaught bad_alloc、pid48549未正常退出。该局部fixture改256KiB，原业务预算保持。 |
| growth-recapture-final及regressions-05 | 目标2/1/0正常exit1：结束实际0B，严格期望312B。真实null free重复退活费；后续矩阵在已知失败后中止，已有manager等正常记录不混作最终资格。两个实际free owner统一非空检查后，精确断言通过。 |
| regressions-06／pressure-final-06 | 同最终commit内容8082/0/0＋66/0/0，28进程全exit0；没有删除以上失败或挑选跨候选绿记录。 |

上述JSON、各label原日志/runner日志、初始和各候选冻结文件全部保留；[production diff](production-incremental.diff)、[test diff](tests-incremental.diff)、[audit diff](audit-incremental.diff) 及所有有范围的机械迁移diff也保留。生成callgraph的大diff单独在产品commit，避免重复塞进生产diff。

[failed-process-state-final.txt](failed-process-state-final.txt)／[JSON](failed-process-state-final.json) 实际查询仍有本批32658/48549及此前43034/87095/59123/70089/83020处于UE。已对本批两个失败子进程发送kill并等待，但未reap；当前28个exit0不证明所有历史尝试drain，未把这些进程当通过或触碰旧进程。

## 改动成本及剩余资格

[source-metrics.json](source-metrics.json) 相对本批产品父提交，生产63文件 **+2274/-1327，净+947**；测试14文件 **+513/-358，净+155**；audit三文件 **+30/-17**；生成两文件 **+109825/-92211**。三新增头部共231行全部计入生产，关闭前后增量diff都有真实文件，不将生成/测试行数包装成重构净删。

原Store.cpp净-104、metadata净-30，说明旧close/验证/估算协议确实回收；WriteCoordinator净+232、backend净+136、runtime净+108和新COW数组/byte197行兑现新的容量/拒绝/保活保证，不能说这轮是纯等价封装或必然减少总行数。新增native starter同步属于资源准备，不新增业务phase/权威/queue。API图2033→2158并非API收缩承诺，真实构造/释放/value/native consumer列在[替代账本](../../br1_modification_guide/API_CONVERGENCE_MAP.md#cp1-concentrated-storage-api-delivery)。

两架Store factory子根实际fee **5104→5448B**，仅指测试测量的该子根，不是整个backend/provider/history或全process容量。bootstrap初始64MiB是有限root，产品policy只能沿同parent采用可容纳live/reserved/process实际容量的额度。Darwin worker/monitor各512KiB显式stack；创建前各预留64KiB native容量，再按VM实际region归差额，非malloc usable size或RSS。

最终CPU日志stop计数arm64 **1100296→2128B**、x86_64 **1067536→2136B**，晚delay handle已reset，留下固定executor/process anchor至static析构。测试断言实际stack与late control归费，未把stop写作全进程尾容量为零或完整static退出。

**当前CPU列明存储实现交付，完整CP1仍未结算。** 完整逐分配点故障注入及所有参与者同源硬满/永久拒绝/恢复/停止/最终释放矩阵、全局allocator/总峰值、Qt/OS外部容量、非Darwin与最终static退出、旧UE未drain和TSAN继续开放；持续公平与原job continuation按CP5，正式性能按CP10。M6/M7/M8正式0/3、persistent默认关闭，CP0 required及正式样本未结算，不根据行数/测试数推算工程人日。已收费对象和删除项不重新领取，下一只沿这些真实资格缺口回到原owner。
