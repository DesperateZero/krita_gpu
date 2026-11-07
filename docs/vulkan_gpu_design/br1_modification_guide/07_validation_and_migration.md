# 07：验证入口、迁移证据与阶段更新

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。设计依据：92 §6、§8.1、§13–§14，以及 README 所列的 39 正式性能契约。定位基线 `5173c807c87b`。本篇 V01 贯穿所有修改项，以下主体为应补证据；末节单独记录已执行的 freehand smoke 及其边界。

当前验证排期统一执行 [92 §17.4](../92_br1_m6_m8_execution_baseline.md#closure-testing-policy)：CP0提前准备required/同依赖对照和真实显示/drain测量；CP1/CP2及CP5–CP8以工作包目标结果为验证单位；CP3/CP4冻结M6/M7，CP9/CP10冻结完整M8/BR1。不对每个小hunk重复全矩阵，不为纯文档更新新增产品测试；目标失败与实际新风险仍须回修，当前代码不继承旧binary资格。

M6按[92 §6.1](../92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)验收，旧20%/30%失败不改写。[§16.139执行变异诊断](../92_br1_m6_m8_execution_baseline.md#m6-execution-variance-delivery)完成274测量过程/6188927操作，P1另计1通过/1上限失败并保留；生产未改。Rosetta thread CPU覆盖无效，process含后台；低扰动查询定位E/P关联执行变异，不伪造全局因果置信。就地ABBA同期192过程两策略均0/4满足±2%，候选否决，不续采或推广。12对/6块、两侧95%诊断界不授正式20桶99.75%资格；不删尾、扣偏差、CPU归一化或拼接新旧诊断。下一稳定并验证实际执行条件后独立匹配完整family，不继续同义runner调参或昂贵盲扩样。§16.137的64ms/128操作、40对原结果与当前11180/0/0安全、6资源、结构/工具及原Fresh/H4八桶继承核验，正式校准仍2/20、联合hit0/4和miss2/16。内循环不是独立统计单位，Store存活时close的metadata不能写已归零。下表端点/统计单位保持，metadata驻留及CP0完整required独立补证。

| 验证项 | 预注册/取证要求 |
|---|---|
| 同状态hit | 同源码/依赖、双Ready独立exact副本、相同输入/预算/旧读保护/端点；关闭态开关仅在准备前拒绝handoff走安全Fresh。K1/K16×两架4桶各40对，顺序平衡，单侧98.75%降幅下界>0 |
| miss与原控制 | 原Fresh/H4对固定M5保持各自family；新增单副本及资格冲突对同源码禁用handoff，吞吐下界≥0.98。miss原因/m桶及`1−0.05/m`界事前固定；实际资源拒绝另验等义终点，不填成功吞吐 |
| 容量/正确性 | 零额外before、新payload/migration/替换退休，真实每域live/reserved/peak；旧/新像素、取消、恢复、退出；正常/受限预算和单/双副本Fresh控制。必要退出退休单列 |
| 来源/业务 | 实际producer、候选/命中/拒绝、1/4次发布和同段多dab；额外before保留/维护、恢复与drain成本。原诊断只解释机制，完整默认启用按92 §6.2及39裁决 |
| GPU后继 | [39 §10.1.1](../39_virtual_texture_performance_gates.md#handoff-value-gates)的设备/副本/在途读者/写形状/预算/端点轴；合理池化Fresh、实际关键路径，不能用CPU或Rosetta百分比代测 |

身份、估计量、bootstrap/seed、样本/停止/失败规则和计时扰动校准均在新样本前冻结；保留全部失败，不追加到通过。结构/正确性计数与无插桩计时分开，诊断库与产品差异明确列出。metadata实际驻留≥25%分母、CP0 required、构建及安全资格继续独立闭合，不用统计正收益替代。

## V01：代码与观测落点

CP0最新有限结果见[92 §16.62](../92_br1_m6_m8_execution_baseline.md#cp0-matched-baseline-delivery)：[MatchedFreehandBaselineTest](/Users/apple/krita_gpu/krita/libs/ui/tests/matched_freehand_baseline_test.cpp)与fixed upstream共用同字节夹具、common依赖及五插件。普通Buildup真实jobs/update、projection、一次undo/redo和原owner释放可运行，首个12对/架代表性结果暴露stroke/undo/redo回退；完整DataManager失败与未退出尝试保留。现有FreehandStrokeBenchmark关闭普通updates，不用于display结论；新入口只有projection-ready，完整canvas-visible/M/K/E、足量CI及required矩阵仍待补。普通strategy的persistent opt-in关闭不等于manager adapter关闭。

随后[92 §16.63](../92_br1_m6_m8_execution_baseline.md#execution-preparation-reuse-delivery)修复原准备重复及负坐标指数增长，该批双架构完整manager/CPU及原reference/freehand控制6304/0/0、十进程退出0；此前失败尝试仍UE并单列，上一轮性能回退没有新的配对关闭证据。该批不授予完整CP0/CP1、TSAN/allocator或正式阶段/性能资格。

此前[92 §16.64](../92_br1_m6_m8_execution_baseline.md#resident-binding-storage-delivery)补齐原CPU binding/control实际收费及最后weak尾释放，双架七组十四进程7542/0/0、全部exit0，92源码及109运行物绑定。新增真实容量拒绝在像素前，12行晚handle/原pin/weak尾精确归费；33代metadata cache原清理验证通过，未增加生产GC。该批首轮7533/1/0中的24MiB组合pressure checkpoint metadata preparation拒绝当时未解释，单独/组合及最终通过不关闭反例。旧UE、完整CP0/CP1、全局allocator/TSAN及原配对性能回退仍开放，原19-file ratchet不放宽。

此前[92 §16.65](../92_br1_m6_m8_execution_baseline.md#checkpoint-preparation-pressure-delivery)复现并解释269568字节/324页的共享预算拒绝，原候选删除不用的发布载荷。真实父硬满后安装/取消及最后精确归费通过；同源码双架七组十四进程7546/0/0、均exit0，93源码/109运行物绑定。全部诊断尝试和候选surface8304字节拒绝保留；8MiB cancel曾在backend准入前被拒绝，不能授予完整准入后取消资格。最终通过仍不关闭完整24MiB压力、旧UE、CP1或性能回退，见[完整证据](../evidence/br1_checkpoint_pressure_20261003/README.md)。

此前[92 §16.66](../92_br1_m6_m8_execution_baseline.md#metadata-directory-storage-delivery)补齐原metadata配置目录/control及identity实际收费，删除旧估算/手工fee/失败capacity残留；真实少一字节三次拒绝、同对象重试和coordinator/controller后cancel/cleanup精确归费通过。install的identity读取补齐operational acquire后重新构建，该轮最终双架十四进程7559/1/0、均正常退出：arm64 24MiB pressure再次在overlay surface准备拒绝，该轮不继承旧请求字节。93源码/109运行物绑定；初始7560/0/0及压力66/0/0另存，不替代最终失败。[该轮证据](../evidence/br1_metadata_directory_storage_20261003/README.md)保持冻结，固定目录差集由下段更新。

此前[92 §16.67](../92_br1_m6_m8_execution_baseline.md#metadata-directory-growth-delivery)删除eager最大目录、重复规划和attach隐式增长；原growth门外准备/释放，stale几何复用原grow/revalidate。新增真实目录少一字节拒绝、准备后共享父硬满安装、确实不足候选重准备及晚Data default publication增长/取消/cleanup；raw block leaf范围和有序交错限制单列。两轮目标31/4/0夹具失败原样保留，普通commit不新增slot，改用ReplaceDefaultPixel后35/0/0。最终构建05双架七组十四进程**7570/0/0、全部exit0**，原六方法三对压力**66/0/0、六exit0**；原预算/输入/线程/断言、完整manager和stress/benchmark保持。93源码/109运行物/四构建配置与产品提交一致，运行物前后不变。64 shard空配置1,649,712→76,848B，不等于完整峰值或性能资格；24MiB反例未重现、8MiB准入后取消及旧UE仍未关闭，全局allocator/TSAN、完整CP0/CP1/BR1-PERF保持开放，见[全部证据](../evidence/br1_metadata_directory_growth_20261003/README.md)。

当前源码结果由[92 §16.71](../92_br1_m6_m8_execution_baseline.md#ledger-control-storage-delivery)更新：Ledger Private/admission/control沿同Store冷allocator收费，原Qt共享寿命与provider/transition consumer同批迁移；无操作receipt复用原authority删除独立分配及拒绝，真实claim仍先准备paid inactive receipt/control和claim节点。生产冷根5,104B新增584B、Private16B allocator及receipt接口8B单列；无操作新增0B、真实claim424B（node352B＋receipt/control72B），Store/Ledger facade8B保持。原冷拒绝/重试、父硬满无操作完成、真实claim候选少1B三次拒绝/原owner重试、source不变与取消、controller后仅receipt weak在满父额最后free精确归基线通过，最终目标14/0/0。首11/2/0为夹具finalize后注册provider，原日志保留；收费无操作receipt候选7596/0/0及其源码/运行物单列，删除分配后最终双架七组十四进程**7598/0/0、全部exit0**，原压力三对**66/0/0、六exit0**。四次构建均exit0，早freeze按压力六记录完整性拒绝、实际runner结束后成功。93源码/109运行物/四构建配置绑定产品commit且运行物前后相同，原预算/输入/manager LIMIT_LONG_TESTS=1、stress/benchmark及Matched字节/callback/释放保持。生产净+30为收费及弱尾保证成本，未授纯去重/性能资格；默认standalone/测试heap Ledger facade、其他Qt控制/root/process、完整总峰值/永久出口、8MiB准入后取消、旧UE与全阶段/性能仍开放，见[完整证据](../evidence/br1_ledger_control_storage_20261003/README.md)。

| 角色 | 现有代码段 | 修改/使用方式 |
|---|---|---|
| 主改 | [diagnostic phases](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreDiagnostics_p.h:22)，phase/metric/recorder；[timer](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreDiagnostics.cpp:100) | 把 stroke/job/segment、freeze/fallback 原因、重准备、root visits、wakeups 关联起来；局部累计、边界合并，关闭时无热时钟/跨 shard 原子 |
| 联动 | [stroke measurement](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/KisStrokeEfficiencyMeasurer.cpp)、[FreehandStrokeStrategy](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/freehand_stroke.cpp:130) | 保留首 dab、steady state、pen-up、实际显示与 drain 分段，不能用 average FPS 替代输入到可见尾延迟 |
| 注册核对 | [image tests CMake](/Users/apple/krita_gpu/krita/libs/image/tests/CMakeLists.txt:148)、[tiles3 tests CMake](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/CMakeLists.txt)、[UI tests CMake](/Users/apple/krita_gpu/krita/libs/ui/tests/CMakeLists.txt:137) | 新 case 接真实构建目标；先确认目标被启用、实际运行且符合同源码身份，再统计通过数 |
| 对照入口 | [M5 correctness 脚本](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_m5_repair_20260925/run_correctness.py)、[performance 脚本](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_m5_repair_20260925/run_performance.py)、[install probe](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_m5_repair_20260925/run_install_probe.py) | 阅读其参数/构建身份作为现有复现实务依据；新运行记录使用新的实际源码身份与独立证据位置，不覆盖已固定的 M5 证据 |

**当前测试注册限制：** `FreehandStrokeTest` 和 `FreehandStrokeBenchmark` 在 UI CMake 使用 `krita_add_broken_unit_test`。本目录把它们列为可扩展入口，不表示默认 ctest 会执行，也不表示当前目标已经具备正式 replay/尾延迟资格。实现时核对配置、可运行性和样例资源；修复/补齐后才能纳入 required buckets。现有 M5 测试总数不自动覆盖新增 stroke 契约。

`KisPainterStrokeCompletionTest` 已列入普通 `kis_add_tests`，执行真实 painter-based strategy 的事务/调度终结。其固定像素 fixture 不运行 brush kernel，不能替代上面的 freehand replay 或性能资格。

## 修改项与最小新增证据的对应

| 修改 ID | 不能省略的反例/场景 | 必须看到的结构证据 |
|---|---|---|
| S01 | callback 已写一页后失败、commit 失败、晚 guard、重复取消 | 无成功 undo 误登记、无失败后 replay、终结唯一 |
| S02/S03 | 1/10/1000 dab、worker 迁移、不相交/重叠 jobs、长 stroke | 无真实边界时 copy/allocation/generation/seal 不随同页 dab 数增长；并发未退回整笔全局锁 |
| S04 | display/save、完整 cut 屏幕外页、异步子 job、慢 reader、self-copy | 无 torn exact view；不隐藏更新等待，不丢输入/dirty |
| S05 | 新 capture 与提交两种顺序、旧 transaction 移除、反复 head 变化 | 端到端 gate wait/hold、重准备预算；install 实际 allocator/rehash/大析构为零 |
| S06 | recovery/source/raw pin/alias/swap、第二页冲突、ABA、cancel | M6 无人为 before copy；M7 首字节后失败零、fence 页数/字节/尾延迟合格 |
| S07 | no-change、登记前 journal、wrap、多个 backing owner | provider calls/临时分配下降，所有 domain 变化仍先准入 |
| S08 | 固定 K 放大 H、热点连续写、冷页与多文档 | 整个 pass root/version/destruction 有界，冷页持续进展 |
| S09 | 最后 pin 在登记前/后释放，无后续编辑，close/晚 completion | 无丢唤醒、无 busy loop，pending debt/预算自动收敛 |
| S10 | tiny budget、clone alias、慢 retirement、大 working set | 全局/局部 live+reserved 守界，真实 physical bytes 不重复/漏计 |
| U01/U02 | 固定 K 放大 N/H，default、稀疏边界、冷恢复 | 普通 undo 无 full export/sort/rebuild，缓存查询与 extent 正确 |
| C01/C02 | 热/冷切换、设置变化、旧异步结果、内容依赖改变 | 准确命中/失效、资源有界、不污染旧 stroke、不拖慢绘画 |

## 性能记录如何映射到设计

按 92 §14 预注册桶和统计方法，保留原始 samples、seed、输入 trace、源码/编译配置/库和 binary 哈希。修复基线与正式 upstream 比较分开，H0 handoff 桶不代替真实有 undo 的 stroke。

优先记录 stroke 的 completed throughput、固定-work latency、首 dab、P95/P99、pen-up、完全 drain 及峰值字节；再记录 undo 与 context。维持实际显示频率与 accepted input 量，不能靠减少工作或把未完成工作丢到测量区间外通过门禁。增量不劣性容差及正式 M/K/E 上限以 92/39 为准，本篇不复制另一套阈值。

## 合入与删除记录模板

```text
修改 ID：
对应 92 条款：
实际源码提交与符号：
主改 / 联动 caller 已迁移清单：
新增与复用 case；实际构建目标 / 运行命令：
语义、失败、并发与资源证据：
stroke 主桶和控制桶；undo/context（适用时）：
保留的 fallback / ABI adapter 及具体 caller：
删除证明（静态 caller + callback + runtime census）：
尚缺证据：
回写 92 的阶段裁决：
```

不得将“主文件修改完成”当作跨层闭环完成。S02/S03/S04/S05 启用同一业务入口时要共同通过；长 scope 的进度保证不能后补。删除旧线程注册、全量恢复或对账分支前核对所有 caller，`tests/pagestore` helpers 只作 reference，不迁回生产作为捷径。

## 指南维护规则

函数移动或签名变化后更新主题指南、[CHANGE_MAP](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/CHANGE_MAP.md) 与 [CODE_INDEX](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/CODE_INDEX.md) 的相应符号和链接。若新增测试目标，补实际 CMake 注册和执行方式。若目标行为变更，先修改 92 再同步指南。只在 92 记录 M6/M7/M8/BR1-PERF 资格，当前目录不另立进度权威。

文档定位校验与实现验收分开：检查目标文件和行号有效、符号及 override/caller 一致、每个主题源码文件有反向索引；这些只能证明指南可用。未编译的接口变更须明确标注，已有证据只覆盖其冻结源码，不能因测试入口存在或旧日志通过而授予新代码资格。

S09 的新增证据按 [04a §5](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md) 逐消费者取得：signal/registry 单测、真实 binding 状态、实际 queue 自主进度、close/晚通知寿命、无信号退避及 S10 资源上界分别核对。源码冻结须包含新建但尚未跟踪的 `KisPageReadiness_p.h/.cpp`；不能只导出 tracked diff，遗漏实际参与构建的源码。


## 并发测试夹具与新源码资格

[scheduler_utils.h::recordExecutedDab](/Users/apple/krita_gpu/krita/libs/image/tests/scheduler_utils.h:88)是原调度测试共享执行记录的写入口；worker 并发追加与主线程断言必须遵守同一同步边界，不能用串行化生产 jobs 或放松断言处理夹具问题。夹具代码也属于冻结源码，改后重新构建相关目标并运行完整矩阵，保留修复前失败与没有复现的隔离结果。

S10 的 [完整验证与中间失败记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s10_budget_waiters_20260927/README.md)分别保留初次矩阵失败、仅修正日志互斥后的隔离失败，以及最终夹具修正后的两架构各 100 次隔离和完整矩阵通过。[testMutatedJobs](/Users/apple/krita_gpu/krita/libs/image/tests/kis_strokes_queue_test.cpp:1242)用测试 strategy 的 semaphore 完成屏障保证两个真实 worker 在断言前同时占槽；不再依赖快速 job 恰好未完成的时序，原顺序/数量断言保留，生产调度不变。下一批修改的领取与交付格式见 [NEXT_EDITS / V01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/NEXT_EDITS.md#v01将修改闭环绑定到可复现证据)。

<a id="freehand-convergence-validation"></a>
## 收敛审查后：真实 freehand 与主干对照

2026-09-28 已显式构建 `FreehandStrokeTest`、`FreehandStrokeBenchmark`，所选 `testAutoBrushStroke` 在 arm64/x86_64 各 3 passed / 0 failed / 0 skipped（含 init/cleanup）。完整命令、环境、二进制 hash 与原始日志见 [收敛审查](../evidence/br1_convergence_review_20260928/README.md)。两个目标仍是 broken-test 注册；显式运行通过不等于默认 ctest 已纳入。该结果独立于 JP1 原矩阵，未证明默认持久 owner 已接入。

原 `StrokeTester::test()` 在所选 test 内包含正常/取消、更新和外部 layer 等变体，但没有断言新的持久 owner 模式。进一步核对 [testOneStroke](/Users/apple/krita_gpu/krita/sdk/tests/stroke_testing_utils.cpp:191) 发现：`indirectPainting` 已只参与测试命名，实际模式取自 preset；不能把命名变体当 direct/indirect 双模式覆盖。`benchmark()` 也不显式固定 indirect，且关闭普通更新；timer 只提供整体 stroke elapsed。前次 benchmark 仅构建未运行，不能报告 direct + 正常显示的收益或 input-to-visible P95/P99。首条回归必须断言实际模式、target 和 owner；此处纠正前轮依据旧注释作出的模式判断。

现在补 BC10 的真实入口验证：执行原 FreehandStrokeStrategy 与 brush/jobs，明确 runtime eligibility，断言原 transaction owner 跨 job 延续、正常 display cut、失败/finish/cancel 和 drain；保留相同 trace 的旧模式控制。资源与压力按完整 BC9/S08–S10 验收后才能默认启用。首条入口范围和停止条件见 [CONVERGENCE](CONVERGENCE.md#first-entry)。

比较身份使用固定 upstream `9a24ae0d8c070884fb013594191002e1a1b39a19`、JP1 冻结检查点和本批新源码三组，规则见 [比较协议](CONVERGENCE.md#comparison)。同依赖 upstream 可执行基线仍待搭建；不借旧 Qt 数据或只测改动组计算提升。先预注册 workload、分段指标和统计方法，再测量；92 §14 与 39 门限不变。
