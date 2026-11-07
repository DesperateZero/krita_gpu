# 第一性候选前瞻判别：metadata降级，H2拆价与未准入结论

按[03k试行流程](../../br1_modification_guide/03k_first_principles_candidate_selection.md)完成D1及唯一一次D2补充，**本轮没有候选取得主优化实施资格，没有产品改动或新提速声明**。这不是把负结果当结束目标，而是执行“先定价再进入蓝图”：当前证据不支持再次大改临时状态，也不支持把某个backing/proof检查当多毫秒瓶颈。下一责任仍须从较大且未拆清的外层中建立合法删除预算。

产品`d182a34bd0196079bc40d2ab7d00b8e326e4a58a`保持；原库SHA256 `da4304d429134da577087e15004b4d98d93b7fc5c97a1bf6d8da4f4a615d66d1`，文档父e5a529aab。仅派生观察源码、观察库、实验脚本与证据。协议先于运行保存：[D1](PROTOCOL.md)、[D2新增问题与停止条件](SUPPLEMENT.md)。本轮δ=0.5ms Stroke CPU只是再次调整metadata政策表示是否值得的参考，约为当前16ms的3%；它不替代M6门，也不是其它项目通用阈值。

## 1. D1：完整metadata责任约0.85ms，不能领取多ms临时构造预算

D1为原库/raw、同派生库off、outer、facts，各1能力+4个平衡主过程，共20过程。outer只记录完整责任；facts增加局部写事实/策略及每批canonical事实/策略边界。没有逐replica或逐字段时钟。

| D1指标 | 结果 | 含义 |
|---|---|---|
| Stroke CPU中位 raw / off / outer / facts | 16.360 / 16.527 / 16.5305 / 18.499 ms | off含布局与空调用影响；不可将观察变慢算成产品成本 |
| outer全部Stroke的metadata write+prepare+install | **0.85148ms**，范围0.83986–0.86312 | 每过程先合计互不包含的调用再取中位；含必要策略、容量/索引、安装和清理 |
| facts的write_facts+publication_facts | **0.24940ms**，范围0.24326–0.29492 | 仍含事实查找、原锁和观察；不包含全部临时对象生命周期，更不是可删除净价 |
| outer→facts投影CPU中位比 | **1.18093** | 超过事前15%扰动线 |
| outer→facts Stroke CPU中位增加 | **1.9685ms** | 超过事前0.25ms扰动线；细分价格按协议降为粗价 |

原库→off和off→outer在四样本中较近，仅是描述性结果，不能证明观察器完全无成本。facts过程10为25.251ms，全保留。不能统一扣一个时钟常数，不能拿详细观察中变大的metadata桶重新宣称高价值；原旧细时钟的16%–34%扰动教训在前瞻试验再次触发了明确限制。

实际命中得到进一步限定：projection Fresh为132调用/132个输入版本，private为132调用/264个输入版本；其它Stroke为76/76、76/152。每个版本对象`sizeof=488B`，相关版本数最高2，版本数组capacity最高2，与源码内联2的表达相容。**sizeof×次数不是实际memcpy字节，也不是heap分配次数。** replica总量是每调用所有版本之和；没有逐replica数组地址/容量观察，因此不宣称所有嵌套数组已证明零spill。普通canonical输入随合法重试为244–284版本，不能全归到applyWriteSequence。

这使H1的主优化地位下降：完整metadata才约0.85ms，要净省0.5ms就需删除其大部分成本，而真正还要执行的策略/容量/索引/安装明显未得到删除许可。事实粗价并未给出这种预算。它不是严格不可能性证明，也不证明H1零收益；只是**没有足以承担新政策表示重构的证据**。

## 2. D2：H2四个具体责任有价，单独优化均未准入

D1冷准备扣除已观察provider/private后的外框仍较大，按事前允许追加一次D2。D2在同一新派生库中比较coarse/h2，2能力+4个ABBA块/16主过程，共18过程。只新增四个完整函数边界，旧metadata细时钟关闭；h2保留少量事实计数。实际工作/原语句和锁序不变。

D2 coarse/h2 Stroke CPU中位17.2645/17.3665ms，相差0.102ms；投影CPU比1.03745，未触发本协议扰动限制。**这不等于四函数价格无偏或获得概率置信度。** h2过程14为32.789ms，多个责任同步变慢，未删除该过程或重采。

以下均为每过程先合并投影及其它Stroke，再取8过程中位，不能把分组中位数相加：

| 完整责任 | 全Stroke CPU中位 | 全样本范围 | 第一性保留与选择结论 |
|---|---:|---:|---|
| prepareWriteBaseLocked | **0.43671ms** | 0.40004–0.87758 | 根/overlay选择、真实缺页补建、metadata base/代际和layout查询均在内；全桶也不能支持直接删除0.5ms，先证明可复用事实 |
| reserveBacking | **0.22374ms** | 0.20467–0.42568 | 真实payload与失败Debt接纳、原retirement存储准备；不为少一个检查新增预留协议 |
| registerBacking | **0.14050ms** | 0.13442–0.29054 | 物理身份/域登记/收费接纳；二次footprint观察存在真实变化窗口，不能删整个登记 |
| sealPreparedPage | **0.13891ms** | 0.12617–0.26863 | completion/metadata/provider验证、proof存储与原owner登记；不能把整个seal责任价归给proof |

四函数在投影均132次，其它Stroke均76次。它们与208次实际冷代际/发布相容，未观察到这些入口调用次数相对代际的重复放大；这不代表函数内没有重复工作，也不证明208是合法最小代际数。不同函数共同改造必须证明共享事实及寿命窗口，不能直接把四个桶相加当可删量。

## 3. 剩余责任与下一次应改变的选择

D2同批事件按父子关系分配自时间后，下列互斥责任仍未拆清；表内给每过程合计的中位，**这些中位数不相加作为一个差额总量**：

| 剩余独占责任 | 当前CPU中位 | 已排除的误读 / 下一证据 |
|---|---:|---|
| cold外框 | **0.88158ms** | 已扣本批base/reserve/register/provider/private子责任；仍有Page冷存储、descriptor、binding/校验、锁与临时清理，需要沿真正接收/失效边界审查 |
| operation外框 | **0.96918ms** | 扣pixel、cold、seal等已观察子责任；范围/batch/execution与接线开销，不是可全删wrapper |
| startMerge外框 | **1.07971ms** | 扣已观察子责任后仍含read/merge业务；要建立同义消费与原upstream工作对照，不能全称新增管理费 |
| seal外框 | 0.53646ms | 已扣private/proof；overlay准备、writer释放和原终结仍在 |
| commit外框 | 0.48369ms | 已扣metadata准备/安装；root、预算、proof清理与发布仍在 |
| capture完整责任 | 0.38233ms | 真实读cut有消费者，不能以scope相邻为由合并 |

前三者是接下来审查的责任集合，不是新“待实施”项目。先沿冷准备的Page/descriptor/binding交接与operation原scope，比较单页反复接收和原batch内必要事实寿命；merge需要同义消费对照。新方案只有建立合法可删量和净价才能入蓝图，不能把当前约0.88/0.97/1.08ms责任桶直接转成收益预测。

**当前证据没有支持单一高价值小动作，也尚未把剩余差额证明为不可避免的分摊成本。** 本批未重新运行upstream，因此不与上一批7.643ms配对差硬相减，不给新的差额解释百分比。此前直接把H1当下一核心的倾向被本轮证据纠正；H2也取得了有限的排除/降级依据，而非又一份未定价的产品修改清单。

## 4. 正确性、复现与方法验证状态

总计38个真实过程，**114 QTest passed / 0 failed / 0 skipped**。全部19updates、8segments/4callbacks、像素/历史/销毁、实际加载库、正常退出/reap通过。观察器mode0/2/3的关闭、嵌套、异常展开、重复finish及计数上下文自检通过；Stroke事件CPU/wall父子等式、线程归属和覆盖账复核通过，无栈错/overflow/活跃尾。这里验证观察实验，没有新增产品安全大矩阵或性能资格。

脚本入口：[build.py](build.py)、[run.py](run.py)、[analyze.py](analyze.py)、[D2构建](build_h2.py)、[D2运行](run_h2.py)、[D2分析](analyze_h2.py)、[同过程聚合](decision.py)。[D1摘要](summary.json)、[D2摘要](h2-summary.json)、[决策数值](decision-summary.json)保持全部慢值、分布与输入hash。D2生成的runner/analyzer与原脚本均保留；重跑必须新目录，不覆盖已冻结证据。

原始日志、派生源码/差异、编译/链接命令、观察库、selftest、身份清单及协议随[原始包索引](raw-parts.json)保存。复用未修改链接对象和fixture按hash记录，不伪称本包包含整个构建环境。产品源码保持原commit及干净tracked状态。

方法状态：已取得**事前规则能够限制观察失真、阻止无预算重构**的前瞻行为证据；未取得新优化的净收益预测、完整实施与独立确认。`algorithm-cost-optimization`继续保持原版，不能把否决能力当完整正向流程已验证。M6/M7/M8仍0/3、校准2/20、persistent默认关闭。本包按协议结束D1+D2，不继续添加第三组细时钟。
