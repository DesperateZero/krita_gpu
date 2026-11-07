# CPU管理管线清理：数量兑现，主性能差距仍开放

实施候选`704d96e81cf29d16191bc3db8785859d79775e27`，tree `4e7fc164db46c02b968fdd04400b9e4402e289d0`；父`6644249a4c`，文档父`1dc64c25`。当前分支`codex/br1-cpu-management-cleanup`，原a918产品分支及6644249候选分支不动，不push、不晋升默认。[03g唯一状态账](../../br1_modification_guide/03g_cpu_management_cleanup_tracker.md)的22项全部迁移和适用安全验证完成，[PLAN](PLAN.md)给出原owner证明、每个hunk归属及保留责任；[cleanup-audit](cleanup-audit.json)核对59个hunk及22个ID。

原session直接接收完整reservation并按原slot绑定execution，公共history仍处理真实新键与重叠；规范范围只读，排序一致，cursor只查execution。bound冷页沿用原claim/entry定位，native/alias/generic连续锁外准备，原publication统一空descriptor清理，seal稳定claim只全查一次，legacy单页只查该页token。没有第二权限表、永久字段、owner、队列、锁实例或生产计数器。生产7文件+158/−106，测试3文件+66/−28；新增行用于直接绑定、原子移交、失败前置及共同清理，不把净行数当复杂度结论。

## 事前预测与实际删除

[事前协议](PROTOCOL.md)与[原蓝图](../../br1_modification_guide/03f_cpu_management_cleanup_index.md)不改写旧预测。8个固定派生观察过程按proj_merge祖先核对数量，[完整计数](counts-summary.json)同时分Stroke其它及all phases；计数不用于授时。

| 工作 | 事前 | 同义投影实测 |
|---|---|---|
| 真实operation/写段/冷代际 | 保留19/32/132，bound冷96 | 各过程保持；private prepare/publish也132 |
| 数组克隆 | 19 clone、约38请求 | 19 clone/96元素/768B→0；38请求由模板两分配推导，非malloc实测 |
| 排序及成员 | 反向重排/第二sort/contains删除，次数未知 | 11次反向重排、19次BoundEntry sort、96次contains→0 |
| reservation及通用再准入 | N_a+4N_r+2N_e逻辑查询 | N_a父154/158，N_r=N_e=96；独立直接slot绑定另省N_d=96；history仍真实准入 |
| bound冷重入 | claim96次及第二findIndex96次→0 | 均兑现；claimOne总136→40，保留直接/semantic/legacy真实准入 |
| 准备/空清理锁 | Fresh132；空对象未知 | Fresh132＋candidate32＋native descriptor132＋retainAdmission32，共328对退出 |
| seal全量claim查询 | 3S→S | 父96轮462/474查询；候选32轮158查询＋64动态判断 |
| legacy已有页重复预留 | ΣNscope→L，分母未知 | L=40，父284/316查询→40单键查询 |
| 总write-set定位 | 未单列此合计 | findIndex1218/1222→454；不与上述含helper的逻辑数重复相加 |

别把952个声明范围长度和当contains真实元素比较数，也别把96 bound链误改为132全部免claim。父clear目标范围有4键波动，commit10–14不固定；全部过程保留，不用跨过程差伪造净删量。alias/generic、legacy read和初始化没有Stroke投影命中，不授此处数量或时间收益；它们的原协议证明和安全覆盖单列。完整候选绕过独立borrow，所以克隆消除是MP01–04联合结果，不能分项重复领价。

直接slot构造比原“一次定位”更便宜，模型补为`N_a+4N_r+2N_e+N_d`。仅各变量同为同一路径N时简写8N；fillRect只有N_a。原预测保留作对照，额外96次删除另列。

## 未插桩净收益

相同matched fixture、依赖和像素hash；每批固定20个ABBA块/40对、20,000次块bootstrap，seed261021，pointwise双侧95%，没有正式family资格。CPU为进程user+system。完整命令、运行库hash、原始慢值、退出、析构及reap均保存；未与构建/另一基准/分析器竞争。父、upstream分别80过程，能力3过程。[统计结果](parent-summary.json)、[upstream结果](upstream-summary.json)可复算。

| 候选相对6644249，降低为正 | 点估计 | 95%区间 | 配对节省中位数 |
|---|---:|---:|---:|
| Stroke wall | 3.08% | −0.07%～7.35% | 0.076ms |
| Stroke CPU | 3.08% | 0.33%～6.86% | 0.182ms |
| Undo wall / CPU | 9.31% / 7.83% | 5.52%～13.85% / 3.98%～12.42% | 0.047 / 0.044ms |
| Redo wall / CPU | 5.95% / 5.39% | 1.66%～11.43% / 1.06%～10.85% | 0.035 / 0.045ms |
| Teardown wall / CPU | −1.38% / −1.42% | −6.75%～3.21% / −6.35%～2.94% | 0.007 / −0.001ms |

机制兑现；Stroke CPU有弱的正向净证据，wall尚未显著；Teardown未证明≤2%非劣，不能用“不显著”当通过。该批只定价整个清理包，单个MP仍未独立定价。没有事前可信的毫秒预报，旧0.34/0.568ms混合观察桶不能充当承诺或与结果相加。

新候选仍为upstream Stroke wall的**1.8795倍**，CI[1.7492,2.0099]，CPU的**1.8649倍**，CI[1.7592,1.9704]；此批CPU配对额外成本中位数7.769ms。该批upstream第11过程projection updates=20，其余19，像素/8 segment/4 callback/析构均同义，按协议保留，不删尾；不能与旧“额外5.3ms”等独立分母拼成已追回比例。

因此本轮清理值得保留为候选，但不足以解释主要upstream差距。理论数量达到目标不意味着这些重复工作的单价足够大；也未证明余下全是必要管理成本。下一优先为canonical发布/allocator联合责任和read/merge余项建立必要下界与可删除预算，不能重领本包的扫描/空交接或无预算重写容器。

## 原控制与资格

为单独核对旧Undo回退，完成[预注册原a918对照](PROTOCOL-original.md)，另2能力＋80过程，不扩充父/候选旧批。[结果](original-summary.json)：Stroke wall/CPU降低11.34%/9.90%；Undo wall降低8.35%（CI[1.96,14.25]），CPU降低6.60%（CI[0.35,12.43]）；Redo wall/CPU降低37.38%/33.84%。这批诊断层支持旧Undo回退恢复，无须拼接旧比值。Teardown CPU CI仍容许约+2.10%，未过2%非劣诊断上界；原默认完整qualification仍不授予。

Fresh/H4各双架K1/K16、每桶40对，合计640个顺序过程，50,000次块bootstrap/seed260926，单侧98.75%每桶、各4桶family≥95%；8桶保护fixture非劣均通过。Fresh相对固定M5吞吐ratio/lower为ARM K1 1.4234/1.3983、K16 1.2117/1.2019；x86 K1 1.3876/1.3566、K16 1.2190/1.2136。H4分别1.4929/1.4628、1.4484/1.3923、1.5040/1.4595、1.5148/1.4946。[Fresh](fresh-summary.json)、[H4](history-summary.json)仅是各自原保护范围的累计对照，不算本包增量或handoff优势资格。

同源八安全组×双架为**9224/0/0**；定向范围/并发/legacy为55/0/0。架构核验通过：2216 indexed APIs、29062 reverse-call edges，工具自测6/6。容量快照随实际phase记录，终点metadata reserved均0；Stroke结束允许后台临时预留，process全局bootstrap/cache收费不等于单store泄漏。没有新的metadata同义驻留门分母或TSAN/其它平台资格。

**本有限清理包结算，默认不晋升；M6/M7/M8仍0/3，正式校准2/20，metadata分母及CP0 required开放，persistent默认关闭。** R01–R08实际消费者保持，R09仅此generic空窗口证明闭合；不声称所有CPU管理成本达到全局理想下界。

## 复现与证据

候选实际image SHA256 `9f138c80f6b9c66223f3411684069f3a082f6a39d5ed58d7bd2c4c0cf92daed6`；父`2442a100b543448c798e71ddfe6f9eb18625013aabc65f8e1d57f2e6e3aec9de`。源/运行身份见[delivery-identity](delivery-identity.json)，完整diff、成功与失败源/对象/库/命令/原日志在分卷raw-evidence中，[manifest](raw-manifest.json)、[冻结核验](EVIDENCE.json)、[分卷索引](raw-evidence-parts.json)绑定字节。旧证据包不改写；[OBSERVATION_NOTES](OBSERVATION_NOTES.md)解释编译旧consumer、测试预备假设、父header闭包、Stroke临时reservation及审计/分析器拒绝。

拼接分卷恢复raw-evidence.tar.xz并核对索引SHA后解包。在本目录用run_dev/run_safety、run_comparison各独立批、analyze.py、analyze_counts.py、analyze_controls.py复算；当前源码必须匹配704d96e81c及冻结依赖。旧增量runner版本按原SHA保留，原baseline控制的新增dispatch不改写先前脚本身份。重新运行使用新输出目录，不覆盖本包。
