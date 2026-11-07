# PageStore 同义基础成本：版本周转仍按每次操作重新发生

**最新成本选择：** [seal实测](v3-seal-service-r0/RESULT.md)及[下一责任蓝图](v3-seal-service-r0/BLUEPRINT.md)。产品0473保持，48诊断过程，无新生产收益；下一包尚未实施。

**当前入口：** [V3计划](PIPELINE_PLAN_V3.md#original-handoff-fee)与[本轮收费责任结果](v3-target-service-r0/RESULT.md)。产品0473；H1净省1.134M指令、CPU收益未证，双架11852控制通过。下文是最初8198同义比较的冻结来源，不代表当前仍逐页Fresh。


**主线已从通用优化回到存储替代管线。** 同一份公共data manager夹具、相同输入/当前读取/Undo/Redo，在不经过画笔、区域队列或compositor的情况下，确认了显著基础差额。最有解释力的机制是：upstream首轮COW后复用当前tile，PageStore在每次覆写仍选择Fresh并完成新版本准备、seal和退出。下一责任是这条完整周转管线，不能继续拿通用减少工作量证明PageStore更高效。

产品保持`8198c36ed722030edae715b7423554036bf1bcf7`，upstream固定`9a24ae0d8c070884fb013594191002e1a1b39a19`；**生产修改0、产品测试修改0**。本轮87个诊断进程全部成功：46个存储进程×8行=368行公共语义矩阵、1472次manager寿命；41个freehand进程为123 QTest passed / 0 failed / 0 skipped。两次构建/分析准备错误也保留，未换样或追样。

## 1. 公共能力对照

[事前协议](PROTOCOL.md)固定K1/K16页、1/16次覆写、H0/H1历史、每行4次独立manager寿命。每次覆写后立刻读回并校验；H1最终Undo恢复初值、Redo恢复终值，再purgeHistory/销毁。采用双方原始未插桩image库，8个ABBA/BAAB块/32进程；下表是**每行合计4次寿命、64次公共write**的配对差额，不是单笔stroke时间。

| K / history，均16次覆写 | write额外CPU ms，pointwise95% | write时间倍数（块内比值中位） | 全case额外CPU ms，含setup/读/历史/销毁 |
|---|---:|---:|---:|
| K1 / H0 | 1.279 [1.265,1.424] | 54.36× | 1.801 |
| K16 / H0 | **8.256 [8.052,8.442]** | **24.77×** | **14.239** |
| K1 / H1 | 0.862 [0.845,0.925] | 32.96× | 2.037 |
| K16 / H1 | **6.976 [6.924,7.257]** | **20.48×** | **14.282** |

完整8行、逐块值、wall与所有控制阶段见[summary.json](summary.json)，可用[analyze.py](analyze.py)重算。倍数仅描述这些短小公共操作，不是整应用变慢20倍；K1绝对时间短，需注意计时粒度。区间是预定端点的pointwise区间，不授8行联合性能门。process CPU含同时发生的后台工作，阶段名不能直接代替线程归因。

双方的成功写入、每次current可见、history/Undo/Redo行为逐次匹配；额外exact reader、operation rollback和预算等合同不能因本次没有失败/并发就宣称全部等价。本结果证明共同正常存储能力存在明显差额，不证明差额全部可以删除，也不把额外保证现有实现的价格当作必要下界。

## 2. 可重复的算法差异

两次/侧机制过程一致，以下只统计覆写阶段，不含setup初次写：

| K16、4次manager寿命 | PageStore冷页准备 | upstream实际COW | PageStore seal | PageStore canonical commit |
|---|---:|---:|---:|---:|
| 1次覆写，H0 | 64 | 64 | 4 | 4 |
| 16次覆写，H0 | **1024** | **64** | **64** | **64** |
| 1次覆写，H1 | 64 | 64 | 4 | 4 |
| 16次覆写，H1 | **1024** | **64** | **64** | **4** |

H1把canonical commit压到history终点，但没有消除逐operation的冷准备/seal。读一次并完成，不等于旧值被后续消费者持续保留。两点规模不是渐近复杂度证明，但已直接证明这个用例中“实际同一当前页”与“每次操作重新周转”的差异。

为避免把冷准备误当物理COW，又另冻[计划判别协议](PLAN_PROTOCOL.md)，运行4个current诊断过程：公共矩阵所有冷准备实际选择**FreshPayload**，`recoverableBefore`全部无效；真实freehand未融合控制的208次准备为**116 FreshDiscard+92 FreshCow**，同样全部没有recoverableBefore。共同selector已接通；它在缺独立恢复副本的首个条件就返回Fresh，不能归咎于后续锁检查过于保守。结果见[followup-summary.json](followup-summary.json)。

这也限制了M6的价值外推：本用例没有自然可恢复handoff机会；调整hit路径不直接消除这里的基础成本。history起点A不是本次覆写前B的恢复副本。完整输入FreshPayload已经直接初始化新backing，不是先复制旧页再覆盖；不能把1024次准备说成1024次多余旧页memcpy。

## 3. 读取区间有大量其它线程CPU

初测K16/N16的read区间额外process CPU约4.95ms，不能据此把read函数列为5ms优化预算。另冻[前后台判别](FOREGROUND_PROTOCOL.md)，原库current/upstream/upstream/current4进程，只给描述性分界：

| K16/N16 | read区间额外process CPU | 当前调用线程额外CPU | 其它线程额外CPU |
|---|---:|---:|---:|
| H0 | 4.896ms | 1.725ms | 3.171ms |
| H1 | 5.012ms | 1.803ms | 3.209ms |

“其它线程”尚未分配到具体collector/retirement任务，也可能含其它全局工作；不能自动全部算本次read或前一次write。它证明只调read循环会漏掉大部分区间差额。write本身的调用线程额外CPU仍显著更大，和新版本周转候选一致；不由两个过程/侧宣称全业务净可回收榜首。

## 4. 业务控制与对照边界

派生当前库仅恢复原clear→composite拆分，保留其它PageStore实现。8块/32进程的Stroke额外CPU为**7.439ms，pointwise95% [7.0835,7.823]ms**；Undo/Redo/Teardown为0.4435/0.6525/0.36975ms。各32过程均19次projection update，8段4显式callback、像素和销毁一致；机制两侧各937个stroke job、19 merge。

这条整链仍含[源码审查](SOURCE_AUDIT.md)列出的页分区/失败接线、通用参数外提及OVER透明像素正确性修复差异，因此只作业务旁证。7.439ms不能与上包6.390ms直接相减估计融合效果；双方样本/实验策略不同。共同存储矩阵才是本包排除这些绘画差异后的基础证据。

## 5. 下一完整责任与理论空间

[理想算法、代码位置和T01–T08追踪](PIPELINE_PLAN.md)已收敛到**同步操作的新目标准备→可见性交付→旧资源退出**。已确认的960次Fresh目标周转差，不能直接写成可删除960次或93.75%提速：逻辑版本、实际claim、retag、metadata安装和历史保留仍有必要成本。

对受控同步完整输入，条件理想是将全部可失败准备放到首字节之前，再在无真实保留者时复用物理backing。当前仍有后页准备、seal/overlay及canonical安装的可失败动作；不先移动并证明这些责任，原地写会破坏operation rollback。无alternate的路径属于现行M7 commit-only范围，阶段尚未开放，且8页fence不自动覆盖K16。本轮不改门、不关闭保证，也不新增CPU影子owner。

P01/P02已完成本次对照构造/差异分账；P03完成固定测量；P04确认主责任与真实Fresh原因，**合法净删量和净时间报价仍待完整替代证明**；P05生产实施未开始。下一沿已清点的五处首字节后拒绝点，形成原发布管线可前移准备的有限方案；不能再次由一个可删容器直接跳到产品优化。

## 6. 身份、复现与限制

当前原image SHA256 `77299ab0a112f338b0216eac38a52aa83b2fec3054fb6992a8a3b1417f15ec3d`，upstream `a288ac214124c80c4d3961112c3b4ca8c13ee922e8208a63b204dd597f441908`。每批输入前后核验，保存实际dyld库、命令、原日志和退出/reap。所有观察scope父子CPU守恒、无溢出、无活动尾；全局pool/runtime和跨case最终free归属不授完全闭合。

最初新夹具链接缺SDK搜索路径，给链接显式传原compile的同一`-isysroot`后成功；失败命令/日志在`build-attempt-r0`。首次分析依赖未安装的numpy，保留`analyze-r0.py`/日志，改为标准库固定seed重算原样本；没有重新采样。追加两批分别由已出现的归因歧义触发，协议先冻结，不混入原32进程统计。

原始包及成员哈希见[EVIDENCE.json](EVIDENCE.json)，实际核验见[verification.json](verification.json)。解包`raw.tar.xz`到本目录后，运行`analyze.py`和`analyze_followup.py`可重算；冻结构建/运行目录不可覆盖重跑，新实验须新目录。M6/M7/M8仍0/3，校准2/20，persistent默认关闭；本包未授新生产收益、正式门或技能预测资格。
