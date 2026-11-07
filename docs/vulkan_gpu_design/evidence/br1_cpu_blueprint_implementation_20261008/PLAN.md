# 03d实现：填充产品资格与投影结构边界

起点：外层`88662bce446ae3ece7078b03652b80237dea542d`，产品`fb57b8b69be74a38602fb2f0cd1c6e4374b843e3`，产品tracked工作树干净。沿92 §16.148、03d A1–A4/B1–B5推进，不恢复已回退pin重排，不改变M6门。前轮已完成投影来源量化；本轮必须产生实现、对应安全与性能证据，不能用再次计数替代实现。

## 责任及替代关系

| 责任 | 当前表达 | 目标/保持边界 | 退出证据 |
|---|---|---|---|
| A：独立新页的默认字节初始化 | 原构造函数内4096次小memcpy | 同一独立页内seed+不重叠倍增，删除逐像素调用；原分配、预算、copy/rows、失败及释放不变；无新生产API/owner/状态 | 多BPP、非零/透明隐藏字节、实际allocator/cache复用与源寿命；原受影响安全测试；独立真实业务增量及负控制 |
| B：投影clear→composite | 13 clear+19 composite独立mutation；中间还有original visitor/recalculate及下层依赖消费者 | 不把transaction共享等同pending复用；合并必须同时表达中间读选择、完整prepare、失败与joint publication。先核定全部consumer与净预算；没有合法闭包不增加跨层wrapper | 36链约0.48ms只是条件冷预算；完整合并若不成立，保持该边界并转向必要代际单价，不声称已删 |

A的函数是private、只在完成独立内存分配后的默认构造调用；源像素由caller持有，copy构造与strided构造独立。实现前核对所有caller。所有产品编辑通过显式补丁；测试oracle检查逐字节最终值而非实现内部循环。

## Undo有限判别（实施前冻结）

旧24配对fill实验的Undo wall约+43µs、CPU约+40µs保留。Undo原观察没有fill调用；不能拿stroke收益抵扣。只判别：语义/工作量或释放工作是否变、同一二进制布局下是否仍有回退、最终实际产品候选是否保持原控制。

1. 冻结当前源、父库、实际fixture与依赖哈希；复用前包ARM同Qt真实RGBA8、4 workers、8输入/4更新callback、painted/blank/undo/redo/析构断言。
2. 在证据目录构建同一个可选legacy/block二进制，选择只在进程初始化读环境变量，保持双方相同链接布局。一份有前包详细观察，一份无内部观察；生产代码不保留选择开关。派生库不覆盖原库/前包。
3. 详细观察各一个能力过程，然后固定legacy/block/block/legacy四过程。按Undo真实事件/调用/CPU及所有阶段数量解释；不得按短区间wall推锁价。工作量差异保留，不混成同量均值。
4. 同二进制无内部观察各一个能力过程，然后固定24配对、12个ABBA平衡块。记录原端点Stroke/Undo/Redo/Teardown wall及CPU、实际19更新等数量。所有样本保留，不扩样到通过。20,000次block bootstrap、seed261028，pointwise双侧95%；该判别不是正式M6，也不替代最终候选比较。
5. 在产品实现和受影响安全检查后，最终直接候选与冻结父库独立各一个能力过程+24配对/12块，协议及端点相同。主要stroke需正向区间；Undo/Teardown保留原控制，若回退原因/非劣性仍不能判定则保持候选资格未通过，不能只凭不显著称等价。另对固定同依赖upstream做有限直接对照，不拼旧比值。
6. 未知调度变化、输入哈希/像素/回调错误、退出/timeout/reap或库身份不符全部保留；能力失败停止对应批。计数/分析器实现错误可修后分析原样本，保留旧版；真实候选修复后另冻结身份，不能默默换样。所有性能过程串行、不与编译/分析负载竞争。

## 实施矩阵与剩余目标

本协议不将A的约6%局部收益替代upstream总差距或B的结构目标。后续按A真实结果和B合法闭包继续原目标，所有未验收项保持开放。产品/测试/派生物分列，原Fresh/H4及受影响M6控制使用项目现行规则；ARM与Rosetta独立裁决。最终更新原03d矩阵、92和证据，分别提交产品与外层文档，不push，不暂存已有外层gitlink变化。

## 候选比较开始前的执行明细

上述同布局判别已完成，不追加样本；初始协议原字节保存在PLAN-initial.md并由initial-identity核对。产品候选只将fillWithPixel改为同一倍增算法，新增18行数据驱动字节用例。第一次把新测试排在旧clock-iterator之前，父库的旧迭代顺序断言失败并遗留iterator锁，识别该失败进程后终止；日志/退出保留。新用例移到已有用例之后，保持旧组顺序；同一新测试二进制在冻结父库ARM/Rosetta均27/0/0，不将失败当成优化回归或抹去。

正式候选必须先通过两个架构的8个受影响原组（TileDataStore、TiledDataManager、CPU mutation、Reference、Painter、low-memory、pooler、swapped store），然后执行原定24配对增量。候选对固定同依赖upstream直接比较固定8配对/4块（ARM），仅给局部差距，不授完整CP0。每个批次先各一个能力过程，测量顺序仍ABBA；48/16测量过程分别核对19更新，不按结果扩样。Undo/Teardown若区间不足以支持非劣性，明确保留未通过，不能将“未显著”改称等价。

原Fresh/H4控制沿既有runner固定40配对/20块、250ms、loops4、两架构K1/K16共8桶，固定M5 5173对照、单侧98.75%每4桶family≥95%、吞吐下界≥0.98；不因填充作用于setup/首触而免除原控制。后续native M6机会/安全/资源资格和完整CP0仍分开，不凭A的正向业务收益授予。

## 安全检查发现的必要修复

首个fill-only候选在ARM low-memory组的bitBltRough memcmp中读到空backing；首个父库压力过程通过，不能据此判成fill回归或旧故障。固定反例随后在父库和fill-only候选均2/1/0失败：未暴露writer先解锁、reader最后解锁后，旧write-intent native-pin标记未清；下一轮read→write错误归还仍由旧reader持有的pin，trySwapTileData在活跃读者期间成功。

本包因此增加与A安全资格直接相关的原Tile终结修复：读/写的native最后unlock统一经过unblockSwapping，物理unpin与原ownership标记同时终结；删除writer分支的重复终结，不增owner/计数/公共API。新反例检查实际swap能力和旧字节，不只检查标记。新版本保存为fixed-candidate，fill-only源/库/失败保留；必须先通过反例、原完整受影响矩阵及低内存并发，再开始尚未执行的最终候选性能批。它是正确性修复，不能算作fill算法净收益；同布局switch批仍只隔离fill。

## 有限实验后的交付选择与最终源码复核

原定24配对最终候选和8配对upstream对照已结束；候选有一例18更新，主结果保留，另对所属整个ABBA块做事后同更新敏感性，不补样。stroke正向，但Undo/Teardown区间不能证明原控制不回退，按先前停止规则A不升当前默认实现。候选的Fresh/H4两组原控制均通过，不能代替真实业务负控制。

将完整填充候选保存为本地 `codex/br1-bulk-fill-candidate`；原工作分支仅保留已由父库反例证明必要的pin终结修复及字节/寿命oracle。这不是撤回正确性修复，也不是把A记作已交付优化。保存候选源、库、完整diff、提交及全部实验，不push。

最后源码变为原fill＋pin修复后，独立冻结 `retained-fix` 库和源；重跑相同16个安全组和原Fresh/H4各40配对控制。另固定父库对retained-fix各一个能力过程＋8配对/4块真实业务，只核定正确性修复成本，使用原端点/语义/加载检查及20,000次bootstrap；它不补A样本、不领取优化或M6资格，区间不确定如实保留。所有新性能过程仍串行且无编译/分析竞争；重复失败/超时均保留并停止相应批。B按IMPLEMENTATION消费者矩阵保持条件方案，不引入未经合法性证明的跨层owner。

## pin终结第一次独立价格触发的实现修正

上述retained-fix全部安全/原保护通过，但8配对真实stroke wall增加4.12% [2.26,6.28]、CPU增加4.92% [3.79,6.06]。这不是填充负控制追加；第一版正确性修复在未暴露writer终结确实多解锁/重锁原swap barrier。不能凭安全通过忽略新增热路径工作。

在原Tile内将唯一native终结改为明确的持锁私有函数，read/write退出直接在已有锁域消费它；另外两个legacy COW失败caller显式持同一锁调用。原函数完整替代/改名，无新owner/字段/锁/API，避免重新复制writer终结分支。候选725fe331af和第一版751bceff23的全部证据保留，最终源码另标single-lock-fix。

新源码重跑原16安全组、结构规则，再固定父库对single-lock-fix各一个能力过程＋8配对/4块业务，以及Fresh/H4各40配对控制；同端点/统计/停止规则，不因结果扩样。新增私有改名的所有静态caller一起迁移。该有限修正只结算原安全修复的成本，既不替填充A追加到通过，也不领取B结构资格。

single-lock-fix业务批index6也出现18更新，主结果保留；事后仅以移除所在整个ABBA块的3块同更新敏感性限制解释，不新增过程、不替换主结果，尤其不把仅3块的区间当正式资格。
