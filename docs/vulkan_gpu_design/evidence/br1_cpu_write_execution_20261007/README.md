# CPU写入蓝图：完整候选、实测与取舍

本包落实[03c](../../br1_modification_guide/03c_cpu_write_execution_blueprint.md) B1–B8、B11/B12。起点产品`2f22452e2dc76dca3e60c6231783534f44716ce4`，外层`fa18481b472f349cccd983fd06f68d6dfa8984c8`。候选及最终工作分支身份见`delivery-identity.json`；[事前协议](PLAN.md)、[真实前置核定与删除映射](IMPLEMENTATION_PLAN.md)、`candidate-product.diff`及包含新私有头的`source-freeze/`区分设计与实际实现。原始目录冻结到`raw-evidence.tar.xz`，成员/哈希见manifest。

完整候选提交`f9714b4d31`/分支`codex/br1-cpu-write-ordered-experiment`；回退`fb57b8b69be74a38602fb2f0cd1c6e4374b843e3`，Git tree与产品父完全一致。两次聚焦本地提交均保留，无push。外层原有krita gitlink修改不混入文档提交，当前产品身份由92与本包明确记录。

**裁决：完整算法候选已实施并验证，但本固定业务端点未确认收益；不让主线承担这批新增复杂度。** 试验代码保存在独立本地分支及冻结证据，工作分支回退该候选。数量大不等于独占成本大，更不等于位于关键路径。原M6/M7/M8仍0/3、persistent默认关闭；本包不改正式门。

## 1. 不良流程与已实现的理想流程

原固定源路径为：dab×clip求交→映射→QRegion页并集→QSet→QVector→backend SnapshotArray排序→borrow再次规范化/detach→全部冷页准备→按dab往返各页→changed/原联合交付。暖pending/provider复用本来已正确，不能再将它描述成每次pin重建provider。

候选在同一个原operation中：借用原dab/sourceOrdinal→一次映射/coverage/canonical范围→原execution借用→原prepareAdapter hook内计数/前缀和/稳定填充片段→全部冷准备→按页消费同形kernel矩形→原finish/交付/free。没有新owner、队列、锁、TLS、长期pin cache、job、patch、checkpoint或provider政策。

每像素仍按原dab/clip次序，重复clip不去重；kernel矩形、opacity/average/flow、源偏移、SIMD块形状保持。首版只接factory确认的真实scalar/SIMD RGBA8 OVER、无selection/wrap、独立固定源；第三方同名`over`不能取得重排资格。R=P时跳过片段buffer和第二遍填充，但第一次计数及offset存储仍有成本。

事务桥保持private，原target/mapping复验共用原实现。结构首轮把结果枚举带到transaction被拒后，已收回manager消费；同一个原适配结果类型集中声明，上层只收到bool。原ratchet阈值未提高，manager cc/header标识出现数25/12→24/11，类型集合与布局未扩张。

## 2. 事前预测与实测

前置普通/opt-in/opt-in/普通四过程，及后置parent/candidate/candidate/parent四过程均使用原8segments、4updates、4workers、同一笔像素/undo/redo/终点。每过程27个fixed multi-dab operation，ΣP=76、ΣF=5363、ΣC=76。

| 量 | 原实现 | 候选/目标 | 结论 |
|---|---:|---:|---|
| body页连续段R | 2344 | 76 | 精确兑现；不是把F或generation当R |
| node总pin C+R→C+P+E | 2420 | 152 | E=0，本用例删除2268对，93.72% |
| node代际/复制/初始化 | 76/20/56 | 76/20/56 | 全部保持 |
| node operation/session/canonical commit | 27/27/1 | 27/27/1 | 原边界保持 |
| root代际/复制/初始化/pin | 132/72/60/228 | 132/72/60/228 | 不领取root工作减少 |
| projection更新 | 19 | 19 | 原业务量保持 |
| 单operation最大F/P | 516/4 | 516/4 | 计划不是整笔5363片段常驻 |
| 同时pin | 原上限1 | 上限1 | 原CPU/manager/painter约束通过 |
| 候选最长单页body pin | 无同协议旧时长 | ordinary62.750µs、opt-in62.625µs | 仅诊断两过程，不是尾延迟或压力全域上界 |

片段24B、offset8B，按本序列最大单operation有效容量`516×24+4×8=12416B`；最大的四个operation有效容量合计45728B。这是输入推导的payload容量界，不是实测并存峰值/物理驻留或包含allocator头的总费用。真实存储经原store allocator收费；超8MiB元数据预算的524288片段计划确实拒绝，body零进入，先前pending保留并能重试。

root canonical commit受原并发client归并影响：本四过程parent12/13、candidate12/12，前置曾为11。初版分析器误把11作常量，断言失败后保留`analyze-v0.py`、原四过程和失败序列，修正解释并分析原样本；没有换样或领取commit删除。node commit1保持。

## 3. 未插桩时间结果

两架各24配对/12顺序平衡块，共96业务过程，另4能力过程。主端点stroke-to-projection-ready，20,000块bootstrap/seed261019，pointwise双侧95%；不是canvas-visible、P95/P99或正式M6。所有过程加载/语义检查通过，测量时无构建/其它基准竞争。

| 架构/端点 | 延迟减少点估计 | 95%区间 |
|---|---:|---:|
| ARM stroke | 0.276% | −2.150%～+5.859% |
| Rosetta stroke | 1.400% | −1.495%～+2.341% |
| ARM pen-up | 0.023% | −2.197%～+5.878% |
| Rosetta pen-up | 1.104% | −1.354%～+2.255% |
| ARM undo/redo/teardown | −1.051%/−0.964%/−1.609% | 均跨零，逐项见summary |
| Rosetta undo/redo/teardown | +0.338%/+2.040%/+0.245% | 均跨零，逐项见summary |

ARM边际stroke中位数8.096854→8.022479ms，配对中位省24.667µs；Rosetta13.801230→13.656501ms，配对中位省210.605µs。边际中位数之差、配对中位数和块比率是不同统计量，不能相互替换；重叠端点不相加。

低重用固定256次完整ordinary operation，ARM/Rosetta×同页/16独立页各12配对、6块，共96过程，seed261020、同pointwise95%。R=P、F=16，循环不是独立样本：ARM同页延迟减少−4.599%[−7.016%,+0.333%]、16页−0.121%[−1.101%,+3.763%]；Rosetta同页+4.783%[−4.114%,+7.881%]、16页+0.300%[−1.593%,+2.973%]。均未确认改善，ARM同页的潜在回退不能忽略。

低重用v0在两过程后因跨side像素hash不一致停止：独立main漏资源初始化，缺profile导致QColor转换输入不确定。v0源码/库/日志保留且不进入收益统计；修正沿原SIMPLE_MAIN资源初始化、要求profile存在、使用确定像素字节后另开完整96过程，不续采或挑样。

原固定M5保护两family×4桶×40对共640过程，两family各四桶单侧98.75%吞吐下界≥0.98，8/8过门。Fresh ARM K1/K16下界1.334526/1.095955、Rosetta1.296450/1.121744；H4 ARM1.484906/1.393880、Rosetta1.418140/1.447964。这包含前继全部优化，是原保护范围，不能算本候选相对parent的收益或新增正式M6资格。

## 4. 行为、资源与完整迁移

最终候选12过程：painter、manager、CPU mutation、PaintDevice其它全部方法、DabRenderingQueue、Reference，两架共9470/0/0。原kernel逐像素oracle覆盖隐藏RGB、opacity/flow、重复clip、负坐标/offset、同页/跨四页/稀疏16页、ordinary/持久commit/cancel和undo/redo；同名第三方op按A,A,B,B原顺序执行。manager覆盖BPP1/4/8/16、false/越界poison、真实计划容量拒绝及第二冷页压力后保留既有pending/重试。

首次完整PaintDevice组在原`stressTestMemoryFragmentation`崩溃：81像素patch跨64像素页，共享页writer拒绝后测试仍memcpy空指针。冻结parent单独同方法也SIGSEGV/shell139。保留两边日志与候选崩溃栈；本批不改这个独立入口。最终由-functions枚举其余全部方法，**不授该stress通过或完整PaintDevice组资格**，不能把9470/0/0说成所有原组无例外通过。

结构最终候选：21 manifest、25 ownership facts、16 census groups、2214 indexed APIs、29079 reverse-call edges、19 intrusion files；原阈值、Tile布局及backend重复状态约束保持，6工具自测通过。结构派生物在本包独立冻结，不修改仓库阈值或借生成物行数宣称优化。

| 蓝图行 | 实际迁移/同步删除 | 验证与状态 |
|---|---|---|
| B1 | fixed源借用原列表+sourceOrdinal；适用路径删filtered devices/opaque dab-major body | 像素/第三方op/真实R验证；候选完成 |
| B2–B3 | PaintDevice/strategy及原transaction私有桥，共用原映射/owner校验 | public上层净增长0；拒绝/负坐标/owner测试；候选完成 |
| B4–B5 | 原manager canonical范围，backend原prepareAdapter内收费计划；generic同框架 | QSet/values、native二次数组/排序删除；容量/压力/资源通过；候选完成 |
| B6–B7 | arbitrary公开输入仅边界规范化，内部const绑定；BoundEntry唯一范围查验 | 共享数组detach/BoundEntry重排/contains删除；poison/原集合语义通过；候选完成 |
| B8–B10 | 原extent/wrapper/changed/联合安装、job/provider/budget/retirement保留 | 27operation、76代际、原显示/undo/free保持；0额外owner/锁/队列/TLS；候选完成 |
| B11 | 新反例与原相关组两架 | 9470/0/0，有明确stress排除；候选完成 |
| B12 | 原普通业务、数量、低重用与原M5 Fresh/H4保护 | 机制兑现，业务收益未确认；原保护结果见summary；候选结算 |

生产19文件+390/−59、测试4文件+271/−27，新增私有geometry头完整计入。没有用净删行伪装复杂度下降。增长主要来自独立输入语义桥、稳定分组与真实factory eligibility，虽然每项有消费者，当前业务收益仍不足以证明整体值得保留。主线回退完整候选，不留下只有const/sort的局部补丁来领取B1–B8完成。

## 5. 为什么理论删量大，实际收益小

`Δwall≈α·((R−P−E)c−A)`中，R/P/C/E已核定；独占单价c、新准备成本A与关键路径映射α并未由计数给出。本次完整未插桩结果已把新增计划计入，但不能将近零净收益唯一分摊给c小、A大或α小。没有独占计价与依赖图，不声称已证明某一项占全部原因。

本实验否定的是“这项大量重复工作足以解释当前整笔大差距”的推断。它不否定算法等价，也不证明再无瓶颈。node76+root132=208个代际、92次复制、116次初始化及对应冷provider/metadata/预算/两completion/物理登记、原交付/退役全未减少；这些完整协议是下一优先诊断责任。旧sample差只能支持方向，不给可删比例。

下一次先对**每个新代际的prepare→provider→metadata/adapter→seal/最终free**建立同输入的独占CPU、等待及关键依赖账：同步ready与长寿命retirement分别计价，必要版本/读者/预算事实与重复表示分别计数；覆盖first-touch、warm、必要cut后复写。只有证实可删除净成本及原owner闭包后才形成新的实施蓝图，不能从208或两ticket数量直接开改。completion分source仍是独立未定价候选。本批结束，不追加样本到通过。

## 6. 复算与运行身份

解包raw证据后，`python3 analyze.py`读取冻结原始JSON，按原协议复算；`analyze_controls.py --round controls-fresh --output <新文件>`及history同式复算原保护。根目录summary是完整结果，raw内保留全部命令、实际exit/timeout/reap、加载库hash、source/compile/link身份及失败。

`candidate-runtime/bin`保存候选实际加载的31个本地库/插件/测试文件及必要soname symlink，Qt/安装依赖的原hash在各runtime与控制identity中。回退后再用冻结common库、parent/candidate image各运行一次原机制夹具，`frozen-replay-results.json`复核2420/152和同像素；两过程只证明冻结库可回放，不进入原4机制/96性能样本或估计。可按其中完整命令复验；不能直接把已回退的_build目录当候选库。

`freeze_evidence.py`核验候选源码副本、运行库副本和回退Git tree，记录raw成员hash并冻结。可再编译的`.o`中间文件不入tar，源码、库、可执行文件、compile/link命令和所有日志保留；它们仍可留在本地工作目录。最终回退相关组与结构检查单列在summary/`structure-rollback`，候选和回退的通过数不得相加。

回退后两架同一选定范围12过程**9402/0/0**，保持相同原stress排除；构建成功并实际Ninja no-op。结构恢复2211 APIs/29025 edges，原阈值及6工具自测通过。重新构建候选须使用试验commit或完整源码差异及原compile/link命令，不能将候选TU直接编译到已经回退的旧头文件上。
