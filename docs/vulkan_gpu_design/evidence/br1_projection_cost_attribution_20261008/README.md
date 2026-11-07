# 投影成本：业务分段、版本来源与维护代价

**投影额外CPU已经定位到clear和composite，并闭合132代际的完整来源。主要复杂度是每个独立写段都创建受保护的私有版本，再seal/发布/适配；重复memcpy只是其中很小一段。** 本包深化归因，未改生产、未实施融合或将fill实验升为主线。

产品`fb57b8b69be74a38602fb2f0cd1c6e4374b843e3`，源码树等同`2f22452e2d`；外层父`3e97333c79c22dbc5306233c288dc693fe0add69`；固定upstream仍`9a24ae0d8c070884fb013594191002e1a1b39a19`。输入沿[前包](../br1_upstream_cost_accounting_20261007/README.md)原ARM、同Qt、RGBA8真实freehand、4 workers和原像素/undo/redo/析构fixture。[初始协议](PLAN-initial.md)与[一次有界追加](PLAN.md)、[可复算数值](report.json)、[实际源码索引](../../br1_modification_guide/CODE_INDEX.md#projection-cost-attribution-code-index)分开保存。

## 1. 额外CPU的约四分之三在composite

粗模式只记录对称job及merger边界，固定四配对/八过程，每过程937 stroke jobs、19 merge jobs。两侧setup/clear/composite矩形多重集合完全相同，均19次投影更新、8输入与4更新callback。下面是该批四过程均值；各行是互斥CPU，setup/merge外框已扣其子操作。

| 投影责任 | 当前CPU | upstream CPU | 差额 |
|---|---:|---:|---:|
| clear | 1.200802ms | 0.049541ms | **1.151261ms** |
| composite | 3.933572ms | 0.349593ms | **3.583979ms** |
| writeProjection | 0.002949ms | 0.003311ms | −0.000362ms |
| setup其它 | 0.018290ms | 0.015460ms | 0.002830ms |
| merge其它 | 0.073887ms | 0.090418ms | −0.016531ms |
| job其它，含调度收尾 | 0.092563ms | 0.074648ms | 0.017915ms |
| 合计 | **5.322063ms** | **0.582970ms** | **4.739093ms** |

composite和clear分别占该诊断CPU差额的75.63%/24.29%，合计约99.92%；不是wall份额、可删比例或概率置信度。四个配对差额均正，范围4.330～5.238ms。与前包jobs-only约4.65ms在量级上相容，但不跨批相减宣布变化；本小样本没有新正式CI。

每过程实际调用95次composite，其中19次进入被观察到的像素写入，另76次未进入。首批详细模式中当前后76次合计仅0.044～0.054ms、upstream0.043～0.049ms；空层/空extent早返回不是主差距。真正19次写入的current composite自身剩余CPU约0.906～0.944ms，后面单独拆解，不能全称为kernel或adapter安装。

## 2. 132代际的来源完全闭合

原冷准备事件记录store/surface/page、base/source/target generation、transaction及mutation scope。按**同一页且source generation精确匹配先前target generation**连接，不靠时间相邻猜测。首批两个current及追加两个current均为下表；实际不同逻辑页56个。

| 来源 | 代际数 | 数据动作 | 首批详细模式整段冷准备CPU |
|---|---:|---|---:|
| 56个页的首次实体化 | 56 | 默认fill | 1.369～1.427ms |
| 整页default clear移除后，同merge再合成 | 4 | 默认fill | 0.060～0.063ms |
| 后续merge局部clear已有投影，源为上一merge的composite结果 | **36** | 完整页copy，保留clear区域外字节 | **0.4725～0.4730ms** |
| 同merge的composite，源正是上一步clear的新版本 | **36** | 再完整copy清除后的页 | **0.4686～0.4910ms** |
| 合计 | **132** | **60 fill + 72 copy** | **2.374～2.451ms** |

两个详细过程均62个clear页分支：22次default空操作、4次整页default移除、36次partial write。19次外层clear中只有13次进入backend fill，其余在外层空范围等路径结束。root共32个mutation batch，13个clear、19个composite；匿名transaction可由并发client共享，canonical commit数量不能直接等同32。

这修正了对“额外72代际”的含混理解：它不是72次同一种错误复制；其中36次是跨更新重写旧投影，36次才是同更新内clear→composite的第二次准备。60次fill也不是60个不同逻辑页，而是56首次页加4次default移除后的重新实体化。

对后36次同merge重复准备，**完整冷协议约0.47～0.49ms，memcpy体只有0.0223～0.0235ms**；前36次跨merge准备的memcpy约0.0255～0.0268ms。即使有合法方案取消第二次版本准备，主要删除对象也应该是整条claim/base/plan/backing/provider/登记/绑定/核验链，而非单独数据搬运。

这组0.47～0.49ms取代旧轮剩余36链约0.335ms的粗略规划价；两者观察方式/源码边界不同，不能解释为成本涨了。新价同样含时钟/记录扰动，仅是这一匹配分支的条件毛预算，不是已授可删CPU或wall。

## 3. 算法来源：共享transaction没有复用私有写段

当前路径如下：

```text
merge.setupProjection
  → parentOriginal.clear(rect)
  → fillRect：原范围准入、before快照、独立mutation batch
  → partial页复制旧投影并清除 → private seal → 原联合交付
  → 返回clear，原mutation终结

merge.compositeWithProjection
  → layer.apply → bitBlt → 源只读accessor/快照
  → writePageStoreOperation → 新mutation batch/execution
  → prepareWriteBase选刚才clear的版本，但原pending已终结
  → 新generation + Fresh复制 → 合成像素 → seal/commit/adapter
```

`beginMutationBatch`每次创建新mutation；`Private::finish`每次seal，而`writableTransaction/finishOwnedTransaction`只合并匿名transaction client。`prepareWriteBaseLocked`在没有pending时使用新的nextGeneration，`prepareWritePlanLocked`需要独立可恢复before等前提才可handoff。**共享transaction只减少部分commit，并不会让已经seal的clear页继续作为composite的暖pending。** 当前同session暖复用仍正确，不能据此说每次dab都重建provider。

追加标签使用原base查询已有的VersionInfo，没有添加metadata查询。两次观测的72个copy基准均只有1个replica、recoverableBefore全部无效；60个default基准为虚拟默认页、0 replica。后36次同merge源在一次观测全部Published，另一次30 Published/6 Prepared（sealed overlay），说明是否归并到同一匿名transaction受实际并发交错影响；生成链和删量仍相同。这个自然用例没有给handoff提供独立before机会，不能用已完成handoff微优化预测投影大收益。

所有上述base的`captured`标记为0，**这不等于没有旧读者**。该字段只投影`capturedReadViews`链；`captureReadViewImpl`还通过`retainSnapshot(root.epoch())`保护epoch root，只有overlay delta另外逐版本登记。clear本身持有before快照到循环完成。删掉capture、看到flag=0就原位改已发布backing，都会绕过原读选择/失败保证。

同merge的36链是明确可研究的边界重复，尚未证明当前合同下可直接删除。可构造方案必须将clear与后继composite的**准备、写入、失败和联合发布**移入同一个原投影更新owner，并证明外部reader、源读取、重叠范围和途中失败仍正确。仅跨函数保留裸指针、延长pin、跳过seal或依据引用数写回都不是合法实现。

## 4. 多层维护的绝对成本及剩余外框

后继v2两个current过程增加外框边界，全部原业务数量保持；本表是这个独立批次的互斥CPU，不能与§1差额或§2旧详细价相加。

| 当前投影机制 | v2 CPU范围 | 是否可整体删 |
|---|---:|---|
| 132冷准备，含fill/copy与所有子协议 | **2.253～2.408ms** | 否；包括必要首次页、版本与物理准备 |
| private seal + canonical commit | **1.153～1.176ms** | 否；需要按实际失败/可见性cut合并 |
| operation + batch外框 + adapter/presence | 0.563～0.736ms | 范围/权限/兼容输出有真实consumer |
| clear fill外框及逐页剩余 | 0.332～0.333ms | 含capture外的初始化、查验、lease/清除等，不全是重复 |
| manager geometry/交付析构外框 | 0.169～0.196ms | 不是仅sort价格，也不是完整adapter费用 |
| captureReadView + source accessor构造剩余 | 0.368～0.392ms | 需要当前/旧选择与释放合同审查 |
| bitBlt其它外框 | 0.357～0.439ms | 含裁剪、参数、桥接、局部变量析构及读侧释放；仍未进一步分价 |
| pixel-operation body | **0.227～0.276ms** | 包含实际合成与暖访问，不是纯kernel或可删管理 |
| 其它投影残差 | 0.282～0.372ms | 原merge/job等剩余，不能填为零 |
| 合计 | **5.703～6.326ms** | 当前实现成本，不是与upstream的差额 |

各范围端点不能逐行相加重造一条过程；原JSON保存每过程可相加账。图像合成body只占当前投影一小部分，但本包没有对称拆纯kernel，不能宣称像素kernel两侧精确同价。

新的外框观察把首批约1ms的composite residual具体分到了source/manager/bitBlt等责任。37次source捕获是18个TransactionOverlay、18个TransactionBaseEpoch及最终1个CurrentCommittedEpoch：overlay合计0.197～0.224ms、before合计仅0.0386～0.0399ms；另13次clear-before捕获0.057～0.078ms。不能看到“额外before捕获18次”又把它当主瓶颈，释放费用仍包含在其原外框中。source accessor构造自身0.048～0.072ms已扣capture，不再重复加价。

## 5. 理论空间的修订与下一责任

| 候选 | 已确定量/条件毛预算 | 合法性及净收益判断 |
|---|---|---|
| 取消同merge第二次准备 | 36条来源精确闭合；若保持其它工作，则root132→96、copy72→36、fill60不变；冷准备毛价约0.47～0.49ms CPU | 数量是条件公式，须先证明共同owner与失败/读者边界；净额还要扣新增准备/借用/释放 |
| 同一投影更新内交付合并 | 13个clear与19个composite各有私有终点，共32 batch | 不能直接承诺32→19的seal/commit净降幅；完整clear失败语义、joint adapter及并发client仍需闭合 |
| 首次页批量fill | 投影60次fill约0.54～0.56ms原详细观察CPU，已在总业务fill实验获得独立支持 | 沿03d A先解决undo/格式/原控制；不是新的本包收益，也不与旧整笔1.12ms重复计价 |
| 简化必要代际的同步CPU协议 | 首次56+重置4的冷准备仍约1.43～1.49ms，除payload外还存在显著维护 | 这部分不会随删除36重复页自动消失；需要原记录/消费者/寿命的整体替代，不能删除budget/ready/retire事实 |
| 只优化空composite、少量copy、before构造 | 分别约0.05ms、0.05ms、0.04ms量级 | 当前不足以解释或独立解决约4.74ms投影CPU差额，不排主优先 |

**更深的判断：重复写段边界已找到，但不是一个删36页就能解决全部差距的单点。** 在两条实际业务责任内部，新版本冷准备、seal/commit、原范围/adapter和读侧准备共同增加成本；“大量维护叠加”现在有互斥CPU账支撑，而不是残差猜测。首先用上述36链约0.48ms条件价格审查完整投影owner是否有足够净价值；若价值不足，应转向必要代际的记录/准备单价，而非继续零散删copy或sort。

下一实施前必须交付：原merge/callback/reader/失败consumer闭包；完整版本与交付cut的等价证明；被替代的重复对象及新增成本；未插桩parent/candidate与原控制固定协议。本包没有新的wall净收益预测或20%/30%保证；CPU删除映射到wall需要任务依赖和独立候选实验。

## 6. 置信边界、验证与复现

- **机制/数量证据较强**：首批2次和追加2次current的132/60/72、56不同页及36+36来源一致，实际generation身份对应，像素与矩形工作量一致。不是总体置信概率，也未覆盖别的笔刷/图像/更新频率。
- **CPU价格为诊断级**：粗模式四配对全正且量级稳定；细分只有两个重复，受观察与调度影响。mode0/current stroke CPU均值19.325ms、coarse19.236ms、初次detail21.739ms，不能机械扣固定观察成本；v2更细却未必更慢，说明顺序小样本不能当精确扰动校准。
- **合法删量/最终收益仍未验**：精确来源不证明无读者；captured=false不覆盖root retention。wall−thread CPU只是不执行时间，跨线程重叠，短区间wall可能量化为0而CPU>0，不把它们解释成锁耗时或加进整笔wall。

共21业务过程/63 QTest passed，全部正常退出并reap、runtime库哈希/像素/8输入/4 callbacks/undo/redo/析构核验通过，全部19更新。粗/详细有事件的17过程（含能力）setup/clear/composite矩形多重集合一致；mode0四过程没有事件，不能授逐矩形trace证明。观察无overflow/stack错误、阶段标签变化或未终结事件，逐条self+children=inclusive通过；所有Stroke事件均落在采样阶段时间内。追加能力过程有1个Undo释放事件，CPU291ns、wall量化为0，时间戳在Undo结束采样之后1µs；原fixture先采结束时间再清marker，故它仍带Undo标签。完整保留该边界例外，不计入投影、不改时间戳或丢样，不能宣称全部阶段时间戳严格包含。原观察器mode0/2/3与追加base事实归属方法检查通过。未跑Rosetta、产品安全大矩阵、正式M6或新优化性能比较。

两次构建准备脚本因匹配到两个源码片段而在编译前停下，收窄上下文后构建成功；v0/v1脚本/日志/派生文件保留。初版PLAN恢复时多一个末尾换行导致hash断言拒绝，随后按原hash恢复精确字节。报告生成一次迭代器被min消费导致max无输入，保存旧分析器/错误日志，修后分析原样本，粗差额与初始summary逐项相等。首次冻结检查因上述Undo时间边界例外停止，保留旧检查器/失败说明，改为显式报告非Stroke例外；随后源码快照列表遗漏两个内部头文件的`_p`后缀，修正为实际路径后继续打包。没有换样或追加到通过；上述均非产品运行失败。

复现：`build.py → selftest → run.py capability/measurement → analyze.py`；独立追加为`build_detail.py → run.py detail-capability/detail → analyze.py`。所有runner拒绝覆盖已有批次，重跑用新目录。源码、库、命令、原日志、逐事件与generation表、失败、分析器和身份见本包`raw-evidence.tar.xz`及`MANIFEST.json`；原fixture与借用对象按前包冻结身份复用。摘要与报告在本地原目录可直接读取，原始包保留完整复算输入。

**M6/M7/M8仍0/3，校准2/20，metadata分母和完整CP0未完成；persistent默认关闭。** 本次仅诊断，不把21过程当正式性能资格。
