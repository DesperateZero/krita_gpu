# D2：一次有界H2判别

D1全部20过程语义通过、19updates。outer中全部Stroke metadata write/prepare/install合计0.840–0.863ms，投影其中约0.51ms；facts的投影CPU比outer高18.09%、Stroke中位高1.9685ms，触发事前粗价限制。H1的局部写事实/普通发布事实并非已定价为新的多ms瓶颈。不对它先做大规模政策重写，也不称其收益严格为零。

D1的cold扣除provider/private已观察子责任后，投影与其它线程约0.726/0.666ms；该1.4ms是整个冷准备残差，不能领取为某个动作。D2仅添加四个已有责任的完整函数边界：prepareWriteBaseLocked、reserveBacking、OwnerLedger.registerBacking、OwnerLedger.sealPreparedPage。前二与登记区分基础事实解析、真实资源接纳；proof定位seal余项。它们保持原代码/锁/语义，旧metadata细时钟在D2不启用。

同一新派生库coarse(mode2)/h2(mode3)，每个1能力过程后固定四个coarse/h2/h2/coarse块，共18过程。沿原fixture、输入、退出/加载/语义核验；只报告描述性范围及同批互斥责任，全部原始值保留。h2相对coarse若投影CPU中位增加>15%或Stroke增加>0.25ms，仍限制为粗价，不统一扣钟。D2不拿D1与D2不同布局的分项差算产品收益。

目标δ仍为0.5ms Stroke CPU的值得改造参考。预测是条件判别而非提速承诺：若某完整H2函数覆盖接近/超过δ，则查明其必要动作与可删除动作，只有合法可删除预算才准入；若四责任分别小而残差仍大，保留未归因部分，不再追加第三组细时钟。没有合法候选就停止本包、更新排序与技能试行状态，不能为制造正例仓促改产品。
