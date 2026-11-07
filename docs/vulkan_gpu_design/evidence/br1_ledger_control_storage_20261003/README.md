# 原 Ledger／domain 控制及无操作 receipt 收敛

产品提交`1d29ff82487bf6b936b1d187ec9816db0fe7c204`，产品父`edd8eb815e99f4b845c659a5f1957d6cfa051c53`、文档父`ac5f667112332aa7c5399c34fe6da4b29f7fd839`，见[Git身份](git-round-identity.json)。当前裁决归92 §16.71/§17；继续原Store冷准备／Ledger准入／实际最后free责任，未读取archive。

## 最终责任与删除

Store原Private以同冷allocator构造Ledger，实际收费Ledger Private及allocate_shared admission/control；内部shared→limits→configure冻结顺序保持。Ledger Private cleanup保存原allocator到实际free，拒绝完整回滚。直接向未配置内部controller收费会阻断配置，后置补费另立权威；复用上一轮的冷child/accounting无需再增加登记、强parent pin或业务恢复owner。

原admission强/弱引用、provider weak登记/数组、transition receipt vector及相关注册/override同批迁移到std shared存储，旧Qt类型/create/sharedFromThis和Ledger new Private删除。真实claim沿原runtime预算retained allocator准备inactive receipt/control，再准备原ClaimMap节点，最后发布domainClaim与receipt cookie；cancel/commit/detach、source identity/Busy、同步registration marker、保守singleOwner和锁序保持。真实拒绝由原prepare/catch返回并回滚，没有新重试队列或阶段。

无physical record时原receipt只需保活authority并作无操作commit。最终admission实现原reservation接口，直接共享同控制返回receipt，删除独立Reservation创建及其分配拒绝；原transition commit后清空同vector，取消走原vector析构。仅给旧无操作receipt补费的候选仍保留一次分配、增加实际预算拒绝；全局空singleton会丢掉原强authority寿命。因此复用已收费root，不为无操作额外准备控制块，也不把这一保证泛化到真实claim。

原default Ledger委托null allocator保留兼容性，仍未qualified。其他provider/observer/Transition与statistics等Qt根/控制不由本批推定收费完成。新增私有构造/cleanup及原receipt无操作commit有实际consumer；四个旧签名一增一删，API净增4（2029→2033），callback24保持。没有新增上层API或外部主干侵入。

## 成本与实际请求

生产七文件**+58/-28净+30**、测试二文件**+171/-2**、ownership**+2/-2**、生成物**+8937/-8275**见[统计](source-metrics.json)、[生产差异](production-incremental.diff)与[测试差异](tests-incremental.diff)。净增用于实际收费、弱尾归费及完整caller迁移，不能记纯去重收益。

双架编译器布局见[修改前](layout-before.json)、[最终](layout-final.json)，原stdout保留。Ledger Private **424→440B**保存16B allocator，admission **96→104B**新增8B原receipt接口；reservation对象32B保持。Store和Ledger facade均8B、Store Private4,392B保持。

生产Store冷请求费双架**4,520→5,104B，新增584B**＝Ledger Private440B＋admission/control144B。144B含104B实际对象与40B allocator-backed共享控制；原Store accounting/child120B复用，不能再加一份。独立Ledger constructor测试的冷费**704B**＝440＋144＋它自己独立冷child/accounting120B；测试heap facade不在此收费资格内。实际生产Ledger facade已嵌入上一轮收费的Store Private。

真实claim候选费**424B**＝原claim节点352B＋receipt/control72B（对象32B＋控制40B）。无操作receipt新增存储费**0B**。新增费用与增加的对象字节分列，不称总峰值/RSS/正式性能收益；不能把被弃候选中的72B当作修改前Qt分配尺寸。[交付检查](delivery-checks.json)记录实际请求及资格边界。

## 实际拒绝与最后释放

原冷root四行继续验证第一笔父只余1B、完整冷候选少1B、各三次拒绝/同父重试及cold/late captured精确归费。当前候选少1B在最后admission/control分配拒绝，构造中已付费的Ledger/Store存储完整回滚；首行仍为冷child登记拒绝。

新增两行通过真实provider注册取得admission（provider实际保存weak）：原parent填满后，无physical record的receipt连续三次成功、费用不变；Store退出detach后再填满父额，强admission或原receipt保活，最后strong退出后provider/test weak仍保留收费，直到实际last weak free才归baseline，原parent weak最终失效。

新增真实claim行使用原imported provider handle及原paid Ledger constructor；真实physical record/source domain/revision存在，暖好原accounting后将完整424B候选额度减少1B，各三次拒绝无费用/SSD reservation残余，source保持，同owner重试。取消原claim后只剩72B receipt弱控制，释放backing，Ledger/controller和原fixture退出；原parent仍被accounting保活，再填满真实父额，last weak free精确回baseline＋filler，释放filler回baseline，parent weak失效。该测试heap Ledger facade及独立controller本体未qualified；只裁决同生产constructor的paid Private/control和真实runtime receipt tail。真实commit/swap/journal由原目标方法及完整矩阵消费，没有伪造物理动作来提交claim。

## 执行记录

四次构建均exit0。首目标**11/2/0**的新夹具在finalize后注册provider，被既有合同拒绝；改为原configure→register→finalize后候选目标13/0/0。收费无操作receipt的候选双架七组十四进程**7596/0/0、全exit0**保留在[candidate记录](candidate-regressions.json)，其[源码](candidate-sources.json)/[运行物](candidate-runtime-before-tests.json)单列。最终复用authority、删除无操作分配后重新构建并验证目标[14/0/0](ledger-targeted-final-02-arm64-result.json)。

最终同源码双架七组十四进程**7598/0/0、全部exit0**：每架CPU1331、Physical393、Resident221、Reference783、完整manager1057、Freehand11、Matched3，见[完整记录](final-regressions.json)和[汇总](final-regression-totals.json)。原manager LIMIT_LONG_TESTS=1、stress/benchmark、输入和断言保持。

原六方法组合三对**66/0/0、六exit0**，原24/8MiB、线程、慢reader/递归producer/undo-redo断言保持，见[压力记录](pressure-final-results.json)。首freeze在压力runner仍活跃时按六记录完整性拒绝，[日志](freeze-before-pressure-runner-exit.log)保留；等实际runner退出后最终冻结通过。所有本批构建/布局/graph/测试句柄均已核对终态，没有用Qt totals代替进程退出。

## 重放与身份

```sh
/Users/apple/krita_gpu/.venv/bin/ninja -C _build-br0-cpu KisPageStoreCpuMutationTest KisPageStorePhysicalClaimTest KisPageStoreResidentReadTest KisPageStoreReferenceTest kis_tiled_data_manager_test FreehandStrokeTest MatchedFreehandBaselineTest
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py
python3 docs/vulkan_gpu_design/evidence/br1_ledger_control_storage_20261003/capture_layout.py --phase final
python3 docs/vulkan_gpu_design/evidence/br1_ledger_control_storage_20261003/run_regressions.py --round 02
python3 docs/vulkan_gpu_design/evidence/br1_ledger_control_storage_20261003/reproduce_pressure.py --label pressure-final --count 3 --current-runtime --keep-going
python3 docs/vulkan_gpu_design/evidence/br1_ledger_control_storage_20261003/freeze_evidence.py --round 02
python3 docs/vulkan_gpu_design/evidence/br1_ledger_control_storage_20261003/finalize_delivery.py
```

构建/graph从krita仓运行，证据runner从外层根运行。before布局在产品父源码实际执行，重放须选择该父源码；candidate/before-noop布局不冒充最终。当前[93源码](source-identity.json)、[109运行物](runtime-identity.json)及[四构建配置](build-identity.json)绑定产品commit，最终测试前后运行物逐项相同。图87TUs/2033APIs/25660edges/24callbacks，原21manifest/25ownership/16census/19-file ratchet保持。Matched字节/callback/原owner释放同父，没有新增upstream性能配对。

## 尚未关闭

生产Store/Ledger Private/admission/control、attached真实domain receipt及无操作分配不重领。默认/reference/真正standalone根、其他Qt heap/control、backend/provider/history/observer/Transition/process根、其余wrapper/登记/link/cache和全部参与者总峰值/永久拒绝/停止/晚handle/自主drain仍欠。有限绿样本不授完整24MiB总峰值或8MiB完整准入后取消资格；旧59123/70089/83020仍UE，见[实际进程记录](prior-failed-processes.txt)。

完整CP0/CP1、全局allocator/TSAN、公平/原job continuation与BR1-PERF开放，M6/M7/M8正式0/3、persistent默认关闭。[文档检查](documentation-checks.json)核对本批新链接及源码身份；[清单](evidence-inventory.json)记录原文件大小/SHA256、不含自身，原日志和diff上下文不改写。
