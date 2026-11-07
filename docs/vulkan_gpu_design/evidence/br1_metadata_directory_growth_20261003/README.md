# 原 metadata 目录按需增长与实际峰值

本批接续92 §16.66的固定目录差集，产品提交`453a5e9d1403da28aad85e51b68d1c995080ed6c`；产品父`3959672c4a2bb134adcb171dedb19dadcba37ad1`、文档父`737044ea4660a4315907b1004f09f265e4ea1f69`。实际身份见[Git记录](git-round-identity.json)、[生产差集](production-incremental.diff)及[分类统计](source-metrics.json)。未读取archive，未push。

原三个arena在configure时各预留256个目录条目，每shard固定24KiB，不论是否有block。现在空目录不分配；原MetadataArenaGrowth在shard gate内捕获所需块/目录几何，在门外准备同allocator的实际容量，门内移动DirectoryEntry并swap。Block和slot payload不移动，索引、block/slot generation及原4/8/4MiB hardceil保持；可重用Released条目先抵扣，quarantine不被重新使用。容量不足的attach直接拒绝，不再隐式触发vector增长。

目录候选和退下的旧数组由原growth carrier持有，实际fee随最后free返回；重新准备时在gate外先释放不再够用的候选，再分配新几何，避免叠加第三份无用数组。竞争使几何过时时，publication准备与generic增长共用原growMetadataArenasOutsideLock/revalidate入口，再完成原slot/index reservation；有效PreparedPublication的install不做目录增长。删除eager最大目录预留、fullMetadataArenaGrowthPlan重复规划及attach的隐式增长，失败沿原Exhausted/Stale/NeedsMore和候选清理，不新增终结阶段、队列或owner。

直接在attach里reserve会引入shard gate内实际分配；固定小预留不能兑现后续安装保证；分层目录需要改变原平坦查询和更多存储所有者。本批选择复用原growth及平坦目录，保留一次增长的线性条目移动和新旧数组共存成本，不声称整体复杂度净删。生产2文件+132/-44净+88，测试1文件+139/-9，ownership+1/-1、生成+8074/-6109单列。新增一个私有PreparedDirectory类型、每个原growth的三个目录carrier和三项局部几何；[编译器布局](selected-record-layouts.txt)确认每carrier40B，共增加120B，局部plan24→48B。实际目录数组请求另收费。上层API、持久业务阶段、锁/TLS/队列、外部侵入文件新增0，原19-file ratchet保持。

## 可证伪的边界

1/4/64 shard空配置请求费双架均为1,248/4,848/76,848B，相对父源码分别减少24,576/98,304/1,572,864B，严格等于24KiB×shards；64 shard降低约95.3%。这是原backing预算请求费，不是RSS、malloc header或全部bootstrap费用。原一字节不足的三次配置失败/同对象重试继续通过。

新arena测试先填满一个block，实际共享父额度只差一个字节拒绝目录增长，原slot值、payload地址和目录不变；解除压力后准备成功，再填满真实父额度，目录安装/第二block接受不分配或返还目录fee，旧地址仍有效。另一个候选在竞争者把目录扩到五项后确实不足，拒绝保留原数据；重新捕获几何后增长成功，最终目录费用精确回基线。这个leaf测试只裁决目录，原raw prepareBlock本身没有在该夹具中声明完整收费。

原晚candidate四行扩为八行：1/64 shards×cancel/已安装cleanup×detachment/default publication。新增四行将version arena恰填四个block，再通过真实ReplaceDefaultPixel新增version，确认directoryEntries确实增长；coordinator/controller退出后原Data保有旧目录和shard/parent费用，最后cancel或clearBatch(1)精确归费。源页与最后强/弱parent寿命断言保留。stale几何的leaf有序交错和原并发consumer通过，不授予TSAN或全并发两次序资格。

## 执行与失败保留

构建01验证最初实现/原消费者；构建02增加新夹具，首轮目标31/4/0。构建03把257代改为恰满四块后仍31/4/0：普通commit原位复用version slot，不会按夹具预期新增目录。两次失败均原样保留。构建04改用真实新增version的default publication，目标35/0/0；构建05补齐候选重准备的门外先释放，最终完整矩阵重新绑定，没有弱化目录增长断言。

最终源码双架七组十四进程**7570/0/0、全部exit0**：每架CPU1324、Physical393、Resident221、Reference776、完整manager1057、Freehand11、Matched3。manager保留LIMIT_LONG_TESTS=1及stress/benchmark；原六方法组合再串行三对为**66/0/0、六进程exit0**，原24/8MiB限额、输入、慢reader、递归producer、undo/redo和断言未变。运行物前后逐项相同，[93源码](source-identity.json)、[109运行物](runtime-identity.json)、[四项构建配置](build-identity.json)及[最终汇总](final-regression-totals.json)与产品提交一致。Matched像素/callback/原owner释放同父源码，无新upstream独立配对性能。

```sh
/Users/apple/krita_gpu/.venv/bin/ninja -C _build-br0-cpu KisPageStoreCpuMutationTest KisPageStorePhysicalClaimTest KisPageStoreResidentReadTest KisPageStoreReferenceTest kis_tiled_data_manager_test FreehandStrokeTest MatchedFreehandBaselineTest
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py
python3 docs/vulkan_gpu_design/evidence/br1_metadata_directory_growth_20261003/run_regressions.py --round 01
python3 docs/vulkan_gpu_design/evidence/br1_metadata_directory_growth_20261003/reproduce_pressure.py --label pressure-final --count 3 --current-runtime --keep-going
python3 docs/vulkan_gpu_design/evidence/br1_metadata_directory_growth_20261003/freeze_evidence.py --round 01
```

编译器使用实际compile_commands的两个架构参数，移除输出/依赖生成并加-fsyntax-only/-Xclang -fdump-record-layouts，原[布局日志](record-layouts.log)保留。首次结果摘要解析对空段访问越界，编译本身exit0；修正解析后只重读原日志，未重复编译或改源码。旧两个callgraph过程另存；最终图为87TUs/2025APIs/25510edges/21callbacks，架构21manifest/25ownership/16census/19intrusion通过。

## 未关闭条件

旧24MiB surface准备反例在本轮矩阵及三对组合中没有重现；已证明固定目录预留消失，有限绿样本不证明所有参与者永久压力/停止/晚handle/自主drain或真实总峰值。8MiB原cancel夹具仍未独立证明完整准入后取消，历史8304字节拒绝只属于其冻结源码。旧59123/70089/83020仍UE，见[进程记录](prior-failed-processes.txt)，本批全部退出不证明所有尝试drain。

下一继续原metadata Private/authority本体/control、standalone/bootstrap、其余Qt wrapper/注册/link/cache及全部参与者总峰值/永久尾出口，不重领已收费目录或eager预留。原block/hash手工费用仍在，不宣称所有allocator精确收费。完整CP0/CP1、全局allocator/TSAN、公平、原job continuation、BR1-PERF未结算，M6/M7/M8正式0/3、persistent默认关闭。

活动文档修改链接、93份源码与产品commit的逐项检查见[文档交付检查](documentation-checks.json)；全部本批文件的大小/SHA256见[证据清单](evidence-inventory.json)。清单不包含自身，不改写旧原始日志或diff上下文。
