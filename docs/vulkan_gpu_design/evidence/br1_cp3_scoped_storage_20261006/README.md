# CP3 metadata 作用域保活与内部借用

产品起点 `6ffe097909e23adf3afd229a2a14e93986fae00b`，交付 `57e59e6b0e53c625b0e4853985a242b5433ca618`。本包接续92 §16.129，按用户要求完成设计、全调用点清单、矩阵实施与理论/实际对比。**本轮优化完成并取得实际收益，完整M6仍未过门。** 阶段资格由[92 §16.130](../../92_br1_m6_m8_execution_baseline.md#cp3-scoped-storage-delivery)裁决。

## 设计与预测

原 `KisMutationStorageAllocator` 的每份复制都独立保活；working 嵌套数组、allocator rebind、移动临时对象把同一保活责任重复传播。本包在原allocator中区分拥有与借用两种编译期类型，分配/实际capacity/parent-child收费/拒绝/free政策共用原实现。只有拥有类型的左值能显式产生借用类型；借用不能隐式转换为拥有，也不能从即将析构的拥有临时值取得。

局部操作的一个根引用覆盖完整prepare/revalidate/install/失败/重试迭代。PreparedPublication的原Data持有根引用；其工作值、deltas、authority和growth借用Data，覆盖移交、cancel、批量清理、worker及controller detach之后的释放。每个实际allocation原本自带的owner引用仍保留。目录数组会swap进入持久arena，因此把arena原目录allocator内的根引用移到arena成员，声明在借用目录之前；准备目录依赖外部根，swap之后由arena根接续。原shard maps只在shard内部，借用先声明且后析构的budgetAuthority所保留的原owner。索引本身及独立provider/retirement/completion等保留原所有权。

本包不合并预算准入，不新增owner/队列/恢复域，不变更canonical事实、claims、revision复验或晚free收费边界。借用类型是对已存在保活责任的表达，不提供新的写权限。较简单的“全部allocator裸指针”无法覆盖逃逸尾；只改参数引用不能消除嵌套容器复制；运行时owning开关会扩散状态，因此采用同一allocator的编译期模式。

同一public N1024/K16/B4/H0后次写入，原总deref6157，working2640+projection1296+publication633=4569；原链主线程实际free20。事前模型为32局部作用域+1发布准备作用域+20实际释放+E必要交接，即53+E；设计目标链约100次以内、全操作约1690次以内（约98%/73%减少），不是已证明下界。原未插桩CPU可明确归到本链的deref约5.9–6.0μs/op（约2.4%主线程CPU），不是73%时间收益；ref/构造的附带收益待测。原A=524请求、446成功、988fits不预报下降；actual capacity可能随布局变化，逐项报告。

## 改动与验证矩阵

| ID | 必须排查/迁移的位置 | 根与释放边界 | 旧实现删除/保留 | 退出证据 | 状态 |
|---|---|---|---|---|---|
| S1 | KisMutationStorage_p.h allocator/rebind/allocate/free/equality | 拥有类型保活；借用复制不碰引用；每块actual allocation仍保活 | 原默认拥有路径保留；目标容器不再复制强引用 | 编译期转换约束、跨controller晚free与拒绝 | 完成 |
| S2 | KisPageStateMachine_p.h replica/version/state/result及value工厂；StateMachine.cpp模板consumer | 局部根或Data根；移动后对象仍能在同一根寿命内复用 | working所有嵌套数组的独立强引用删除 | reference oracle、溢出容量/拒绝/移动复用；StateMachine.cpp规则无需改动 | 完成 |
| S3 | MetadataArenaGrowth及registerPage/discardHistory/applyCapturedProtection/applyProjectedSequence | 每个完整迭代根先于scratch构造，后于scratch析构；锁外窗口/重试保留 | 从临时强allocator构造scratch删除 | 原CpuMutation/Reference/Read完整组通过，准入与revision规则保持 | 完成 |
| S4 | PreparedPublication::Data/create/deleter/Publication/ShardArenaGrowth；preparePublicationImpl全部kind | Data强根先于嵌套值；deleter覆盖Data析构到物理free | 内部deltas/authority/installRecords/growth强引用传播删除 | 原普通/restore/default/recoverable/detach及成功/冲突/cancel/晚cleanup测试通过 | 完成 |
| S5 | KisPageMetadataArena_p.h Directory/PreparedDirectory/arena ctor/installPreparedDirectory | arena原根保活移至成员；prepare外部根；swap无分配/free | 目录临时allocator强引用删除；每arena原保活保留 | 原directory增长/恰满/竞争测试通过；实际install零分配/free | 完成 |
| S6 | MetadataMapAllocator及MetadataShard pages/activities/cpuBindings | 原budgetAuthority先声明、后析构并保留原storageOwner | map allocator临时独立强引用删除；原map容量计数保持 | 原准入/claim/close/observer测试与结构门通过 | 完成 |
| S7 | 全部剩余consumer及allocator派生类：Store::MutationAllocator、ShardRecordStore/index、retirement/completion/provider、Qt reference | MutationAllocator显式rebind保留原MutationLifetime；其他独立寿命保持拥有 | 删除继承基类rebind导致的控制块保活丢失；不把独立尾对象误改为借用 | 编译期family断言、原runtimeStopsAtCapacity、静态搜索/完整diff/结构门 | 完成，含真实回归修复 |
| V1 | 原reference/cpu/claim/read/registry与参与业务、Vulkan | 同源码双架构；x86为Rosetta | 失败全部保留 | 38进程11114/0/0，另6探针通过 | 完成 |
| V2 | 原public/native容量引用追踪矩阵 | 同端点、2顺序块；全线程尾分开 | 重插桩时间不算性能 | 28进程、277699事件；K16目标链54，预算工作保持 | 完成 |
| V3 | 未插桩父版本/候选性能；固定M5/H4及native门 | 独立顺序平衡配对、事前固定样本 | 不加样到通过、不改阈值 | 1280性能进程+4个CPU诊断；增量收益成立，原门的失败保留 | 完成 |

## 有限验证与停止

先冻结原库/fixture/源码身份，再完成全部生产迁移和行为测试。复用原测试、allocator探针和trace工具，所有原失败保留；仅真实回归或构建错误允许修复后另建批次。安全完成后顺序执行数量追踪和未插桩性能，不与构建并发。正式性能仍使用既定40对、四桶单侧98.75%界/至少95%family门，不把局部计数达标当作M6通过。原CP0、驻留分母、TSAN等欠项不由本包覆盖。

最终按本矩阵逐项记录已改位置、实际测试、删除/保留原因和理论偏差；若计数预测未兑现或时间不跟随，报告原因，不继续同义微调和扩样。

## 实施与安全结果

[责任关闭审查](closure-review.json)分别列出生产、测试和派生物：生产5文件+72/-38（净+34），测试+68/-5（净+63），结构/所有权+4/-2，调用图与基线派生物另列。净增用于表达拥有/借用类型、完整根寿命和派生allocator的rebind；没有新增owner、队列、公开业务API或失败恢复政策。目录allocator之外保留原根使每arena布局增加16B、每shard三arena合计48B（分配器取整前）；本包不声称内存减少。所有被测后次操作的controller准入容量总量保持。

[安全摘要](validation-summary.json)：双架构原16参与组、5个persistent freehand业务方法、ReadBaseline和Vulkan，共38个QTest进程11114 passed/0 failed/0 skipped。另6个探针通过；每架31080个joint install及28个publication install区间alloc/free均为0，24个实际storage生命周期边界通过、registration实际64B。新增一个生命周期测试覆盖嵌套小数组spill、整体move后复用、controller销毁后分配拒绝、worker最终释放及parent归零。结构门87 TU/2209 indexed APIs/28868 reverse edges/27 callbacks，21 manifest/25 ownership/16 runtime census/19 intrusion及6项工具测试通过，ratchet未放宽。

初版在原`runtimeStopsAtCapacity`断言留下512B；LLDB与39131事件诊断追到4个Store的64B MutationSession控制块及64B registration。新基类rebind被派生MutationAllocator继承后丢失原MutationLifetime，现已显式rebind回本族并增加编译期断言。原终点断言未放宽，修复后完整双架矩阵通过。构建显式默认构造、旧文本结构匹配、首次debugger表达式及数量摘要断言的问题也全部保留在[尝试清单](execution-issues.json)。不把这些失败计入最终通过批次。

## 理论与实际工作量

[逐块数量比较](quantity-comparison.json)和[完整当前摘要](summary.json)使用同一public N1024/K16/B4/h1/H0后次写入。原用例只写一行4KiB，仍完成16页COW（256KiB），copy/generation/session/seal/commit等实际工作及像素/extent保持。它不是完整笔画或全页payload吞吐模型。

| 工作量 | 原实现 | 事前预测 | 当前实测（两个块） |
|---|---:|---:|---:|
| working值引用归还 | 2640 | 消除内部复制保活 | 0 / 0 |
| projection引用归还 | 1296 | 32局部根+真实free | 48 / 48 |
| metadata publication引用归还 | 633 | 1准备根+真实free+E | 6 / 6 |
| 三条链合计 | 4569 | 53+E；目标≤约100 | **54 / 54，E=1，减少98.82%** |
| 整次操作引用归还 | 6157 | 目标≤约1690 | **1645 / 1642，减少73.28% / 73.33%** |
| controller/process控制请求 | 446 / 78 | 保持 | 446 / 78 |
| retained-owner分配请求 / 完整fits检查 | 339 / 988 | 保持 | 339 / 988 |
| 目标链实际free | 20 | 保持 | 20 / 20 |

54次分解为32局部作用域+16实际free，以及publication的2次根/工厂交接+4实际free；可见算法表达已接近本轮提出的53+E模型。53不是所有合法算法的严格下界，不能用本轮结果证明全局最优。目标链仍占当前总deref约3.28%，继续削这54次的数量上限已经很小。

全量1645/1642的3次差异来自publication descriptor的清理落点（1次retained free伴随引用销毁），不是控制请求增加。14个trace进程277699事件；28个control/trace均正常退出/reap且语义、实际库与前后身份通过。首轮摘要要求所有块的释放时刻完全相同而失败，现用**同一批数据**分别报告寿命和总量，不补跑、不删样；原分析输入的hash由[快照映射](trace-input-snapshots.json)保留。45个跨epoch尾到捕获结束仍未闭合，不能据追踪窗口宣称全量drain。

其他原端点也兑现数量下降：public N64/K1链304→10，N64/K16链4569→54；native Fresh K1链304→10、K16链4365→54；native handoff K1链333→14、K16链4829→118。K16 native共同seal/commit引用归还3118→279。provider/retirement/completion/epoch等独立寿命保留，未把跨操作对象统一塞入operation arena。

## 未插桩实际收益与置信度

[父版本增量对照](parent-comparison-summary.json)每桶40对、20个顺序平衡块，固定50000次bootstrap，无删样/补样。以下为配对块估计及双侧95%区间，属于每桶描述性置信度，不是四桶family正式门。父版本使用修改前冻结的实际原库；所有fixture和语义工作不变。

| 端点 | 当前/父吞吐提升 | 每次wall节省 |
|---|---:|---:|
| ARM K1 | 2.63% [1.91%, 3.50%] | 0.88μs [0.64, 1.17] |
| **ARM K16** | **5.04% [2.78%, 7.44%]** | **14.81μs [7.65, 21.08]** |
| Rosetta K1 | 2.17% [1.74%, 2.93%] | 1.00μs [0.80, 1.37] |
| Rosetta K16 | 3.63% [3.13%, 4.97%] | 14.83μs [12.83, 20.38] |

ARM K16主线程CPU减少**15.06μs/次 [7.53, 19.35]**；配对CPU比下降5.98% [3.15%, 7.68%]。各版本边际中位数的差不等于配对块差，本包采用事前配对口径。Rosetta原`CLOCK_THREAD_CPUTIME_ID`读数仅约wall的2%，未校准其对翻译执行的覆盖，因此保留原计数但不将其μs外推为物理CPU总成本；Rosetta收益按完成工作量的wall吞吐比较。

[四次CPU诊断](cpu-comparison.json)保持parent/current、current/parent顺序，每进程原6秒fixture取2秒Time Profiler **Running** 行，主线程每次约1984–2120个样本。目标链deref从父6.03–6.38μs降到0–0.12μs的采样估计，全部owner deref从8.59–9.26μs降到1.69–1.79μs。它复核了原“直接deref约5.9–6.0μs”的成本模型：引用工作确实消失；总15.06μs收益还包含配对ref、构造/移动与编译器简化等可能因素，现有数据不能精确分摊。没有把“直接成本估计”误作全优化收益上限。

采样份额乘全6秒CPU/op假定工作混合稳定，仅为诊断近似；未符号化leaf约3.15%–3.96%，0样本不表示成本严格为0。计数的可重复性和本轮正收益证据较强；对收益逐项因果分配、其他机器/完整笔画的外推置信度较低，不编造概率。

## 原性能门复验与剩余方向

原M5/H4/native各自每桶40对，正式四桶单侧98.75%下界（至少95% family），仍按预注册阈值。全部1280个性能进程正常退出、reap，原像素/工作量及库/源码身份通过。

| 检查 | ARM K1 / K16 | Rosetta K1 / K16 | 裁决 |
|---|---|---|---|
| [Fresh current/M5](fixed-m5-fresh-summary.json)，下界≥0.98 | 1.1805 / 0.9464；下界1.1630 / 0.9261 | 1.2696 / 1.0169；下界1.2565 / 0.9308 | K1通过，K16两桶仍失败 |
| [H4 current/M5](fixed-m5-history-summary.json)，下界≥0.98 | 1.3314 / 1.2454；下界1.3029 / 1.2095 | 1.2614 / 1.3320；下界1.2443 / 1.2955 | 四桶通过 |
| [native handoff延迟减少](latency-paired-summary.json)，下界≥20% / 30% | 5.58% / 14.29%；下界4.57% / 13.89% | 4.29% / 14.91%；下界3.48% / 13.42% | 四桶仍失败 |

Rosetta Fresh K16点估计已高于M5，但区间不足以通过；不能按点估计宣布过门。native表比较本次Fresh与handoff，不能与父版本的比值差当成本轮精确因果收益；共同成本和Fresh分母同时改变。原失败与宽区间全部保留，没有加样到通过。

当前public K16完整`fitsLocked`仍约28.55–30.65μs/次，是最大单leaf，次数仍988；预算政策与owner收费互斥合计约57.13–58.31μs，占当前CPU约24%。这不是全部可删空间。下一优先分析原controller两级准入/settle的重复政策扫描与批次边界，逐项推导可删除的检查/锁/临时结算，不重做已收敛的allocator引用。任何候选须保持actual capacity、parent-child总硬界、公平/拒绝归还与晚free，并以预测`Δfits/Δprepare/Δsettle`和未插桩因果结果验收。provider物理tracking/binding/retire只有在完整生命周期下能证明可承担剩余缺口时再实施。

本包没有增加metadata同义驻留≥25%的证据、CP0 required、TSAN、完整long/OFF或完整stroke资格；persistent默认仍关闭，M6/M7/M8仍未完成。该优化S1–S7与V1–V3已关闭，不因整体门未过而继续同义微调或扩样。

## 交付与复核

[交付身份](delivery.json)、[完整产品补丁](product.patch)、[源码Git blobs与运行库复核](final-verification.json)绑定产品提交及固定M5/父库；[原始包清单](raw-evidence-manifest.json)给出`raw-evidence.tar.gz`逐文件hash，包含所有成功、失败、追踪事件/maps/符号、CPU Running XML、原始性能样本和分析输入。dylib、object及原生`.trace`包只保留本地，导出的可复核数据均冻结。脚本和协议直接保留可审阅文本；raw包解压至本目录可恢复其相对布局。重建trace使用产品提交、`prepare_trace.py`生成的预算TU补丁与原工具链/依赖，不把诊断库当性能库。
