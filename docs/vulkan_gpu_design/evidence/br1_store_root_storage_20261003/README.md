# 生产 Store 根存储冷准入与最后释放

产品提交`edd8eb815e99f4b845c659a5f1957d6cfa051c53`，产品父`ec3cebba5b4652c04c856b262065dde092c938b4`、文档父`4d62c749a5c926ac266bc4403c87f71186ec2327`，见[Git身份](git-round-identity.json)。当前裁决归92 §16.70/§17。本批未读取archive；沿原backend prepareStore、内部配置及原lifetime最后free收口。

## 最终责任与删除

生产唯一动态Store创建点prepareStore已经先取得process共享父预算，原configure与configureClone共用它。私有prepareStorage在原冷入口创建临时栈child controller，复用原共享登记及retained allocator，实际分配Store facade和原Private。返回前临时controller停止准入并退出，原accounting继续持有原parent/child登记，直到实际最后free；保存的根allocator仅用于deallocate，不在退出后的controller上作新准入。

Store内部controller仍接受原shared→limits→configure配置顺序；没有放宽非零live/reserved冻结。直接用该内部controller支付它自身存储会阻断配置，后置估算补费会另立收费权威。直接向process controller分配不能自行保活晚free所需controller；每个尾对象另存强pin或转移费用又增加维护协议。因此复用原child/accounting寿命，不增加业务阶段、恢复owner、队列或TLS。

原backend `new KisPageStore`、Store `new Private`、原同步/terminal task两处`delete owner`已删除。构造局部候选失败原位回滚，PrivateReleaser和原退休线程共享Private::destroy，原captured/mutation lifetime承接最后引用；facade destroyStorage独立归还自己的实际存储。原default/reference构造继续使用null allocator，仍未qualified；真实foreign/claim、内部配置、其他准备及reservation拒绝保持。

新增Store allocator constructor、prepareStorage、destroyStorage、Private::destroy有真实consumer；Private constructor改签名一增一删，图API净增4（2025→2029）。callback registrations 22→24是同facade deleter在factory/backend handle的两个登记，不是新的业务通知协议。

## 保证成本

生产三文件**+66/-7净+59**、测试一文件**+117/-0**、ownership**+1/-1**、生成物**+9135/-8416**分别见[统计](source-metrics.json)、[生产](production-incremental.diff)和[测试](tests-incremental.diff)。净增兑现实际根存储收费与最后free，不记等价去重收益。

双架实际编译器布局见[修改前](layout-before.json)、[最终](layout-final.json)及[其他对象布局](bootstrap-layout-checks.json)，原始stdout保留：Store facade **8→8B**保持一指针ABI，Private **4,376→4,392B**新增16B allocator。实际冷根收费双架均**4,520B**＝8B facade＋4,392B Private＋120B原accounting/child登记。accounting对象64B，登记剩余请求费56B；此120B保留到真实最后free。backend handle另存8B deleter函数指针；临时栈controller对象sizeof1,352B，不是整个栈帧/stack peak测量。没有测量整个backend新旧布局或总RSS。

原metadata配置费1/4/64 shard **1,416/5,016/77,016B**保持；冷根费是另一个真实分配边界。原Private嵌入的service/controller字节随本体收费；其nested Ledger/domainAdmission/statistics等实际heap/control仍欠，不能把本体收费推成全部嵌套存储关闭。default/reference和其他backend/provider/history/process根仍未qualified，见[交付检查](delivery-checks.json)。

## 实际边界

新增四数据行。父accounting和reservation slots先暖好，再实测冷root请求费：父仅余1B时冷child登记真实拒绝；完整冷候选少1B时最后Private分配不能接受，局部对象与登记完整回滚。每行连续三次无live/reserved残余，解除压力后同一原parent可重试且收费恰为实测值，reset精确归基线。首行没有到达Private分配，不以它声称首Private失败。

cold facade和已配置late captured两行释放外部parent；原根accounting保活原parent，captured还持原Store内部accounting。重新取得原parent并将真实额度填满，cold reset或最后captured退出及原kisDrainPageStoreReclamation之后，归费精确为baseline＋filler；释放filler再回baseline，外部parent退出后weak失效。冷行不依靠配置后的内部controller遮蔽根寿命。原terminal task、reclaimer和lifetime保持，没有新增尾清理。

目标[7/0/0](root-targeted-arm64-result.json)。构建01、最终测试断言补齐后的构建02均exit0。最终同源码双架七组十四进程**7592/0/0、全部exit0**：每架CPU1328、Physical393、Resident221、Reference783、完整manager1057、Freehand11、Matched3，见[完整记录](final-regressions.json)和[汇总](final-regression-totals.json)。原manager LIMIT_LONG_TESTS=1、stress/benchmark保持。

原六方法组合三对**66/0/0、六进程exit0**，原24/8MiB、输入、线程、慢reader/递归producer/undo-redo断言保持，见[压力记录](pressure-final-results.json)。等实际runner退出后冻结；首freeze的宽泛substring把`new KisPageStoreMementoManager`误判为旧Store创建，修正精确类型检查后通过，[失败检查日志](freeze-initial-symbol-check.log)原样保留。这是证据检查修正，没有由此改动已验证产品源码。

## 重放与身份

```sh
/Users/apple/krita_gpu/.venv/bin/ninja -C _build-br0-cpu KisPageStoreCpuMutationTest KisPageStorePhysicalClaimTest KisPageStoreResidentReadTest KisPageStoreReferenceTest kis_tiled_data_manager_test FreehandStrokeTest MatchedFreehandBaselineTest
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py
python3 docs/vulkan_gpu_design/evidence/br1_store_root_storage_20261003/capture_layout.py --phase final
python3 docs/vulkan_gpu_design/evidence/br1_store_root_storage_20261003/run_regressions.py --round 01
python3 docs/vulkan_gpu_design/evidence/br1_store_root_storage_20261003/reproduce_pressure.py --label pressure-final --count 3 --current-runtime --keep-going
python3 docs/vulkan_gpu_design/evidence/br1_store_root_storage_20261003/freeze_evidence.py --round 01
python3 docs/vulkan_gpu_design/evidence/br1_store_root_storage_20261003/finalize_delivery.py
```

构建/graph命令从krita仓库运行，证据runner从外层根运行。before layout在产品父源码实际运行，重放before先选择父源码；不能对当前源码改label。当前[93源码](source-identity.json)、[109运行物](runtime-identity.json)与[四构建配置](build-identity.json)绑定产品commit，运行物测试前后逐项相同。图87TUs/2029APIs/25603edges/24callbacks；架构21manifest/25ownership/16census/19-file ratchet保持。Matched字节/callback/原owner释放同父，没有新增upstream性能配对。

## 尚未关闭

生产Store facade/Private本体不再领取。默认/reference/真正standalone根、其他嵌套heap/control、backend/provider/history/process根、其他wrapper/注册/link/cache及全部参与者总峰值/永久拒绝/停止/晚handle/自主drain仍属原CP1。有限绿样本不授完整24MiB总峰值或8MiB完整准入后取消资格。旧59123/70089/83020仍UE，见[实际进程记录](prior-failed-processes.txt)，没有用当前进程正常退出推成所有历史尝试drain。

完整CP0/CP1、全局allocator/TSAN、公平/原job continuation与BR1-PERF开放，M6/M7/M8正式0/3、persistent默认关闭。活动差集已更新，见[文档检查](documentation-checks.json)；原文件大小/SHA256见[清单](evidence-inventory.json)，清单不含自身，原日志和diff上下文不改写。
