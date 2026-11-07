# 投影成本深化：固定诊断协议

产品起点 `fb57b8b69be74a38602fb2f0cd1c6e4374b843e3`（tree等同2f224），外层父 `3e97333c79c22dbc5306233c288dc693fe0add69`。复用前包同Qt/原ARM真实RGBA8 fixture与stage边界；不修改生产，不恢复已回退pin候选，不推广fill实验。

问题：projection额外约4.65ms CPU分别落在哪些业务操作和维护机制？132代际中的60默认填充/72复制由哪些clear/composite边界触发？同一次merge内部、跨merge及必要冻结的区别是否能闭合？合法删量必须有原owner/失败/可见性合同证明，不能单靠版本相邻。

1. 先复算前包原始事件的projection互斥账。它只有job与机制，没有完整clear/composite标签，不能据时间邻近猜业务来源。
2. 独立派生两侧观察库，复用前包v2对象/源及嵌套wall/thread CPU观察器。新增对称merger start/setup/clear/composite/write边界；详细模式为当前冷准备事件记录page/base/source/target/transaction/scope及原有状态，不增加查询或改变决策。记录原fill的skip/default-removal/partial-write分支以及batch/capture边界，保持原pixel、job和同步行为。
3. 模式0关闭事件；模式2仅jobs与对称merger粗边界；模式3包含原v2机制及本轮标签。标签不单独读时钟，不在热路径打印/分配，不记录逐像素/span/pin。固定容量/栈错误/溢出/未终结事件必须检查。详细价格只作有扰动粗价，coarse用于双方责任差额，二者不混成精确原库账。
4. 两侧各一个mode3能力过程。通过后固定mode0四过程current/upstream/upstream/current；mode2四配对八过程AB/BA交替；mode3四过程current/upstream/upstream/current。合计18个业务过程，全部保留，不追加到某个结论出现，不计算小样本正式CI。若能力或观察实现有缺陷，保留失败并另标修订后重开固定批次，不能默默换样。
5. 原painted/blank像素、8 segment/4 callback、undo/redo/析构、runtime实际库哈希和退出/reap均核对。projection更新期望19，但调度合并例外原样保留并单列，不丢样伪造同量对照。不同工作量不能合并机制均值；变化足以破坏解释时停止外推。
6. 分析按每个job→merge phase→冷页→payload/协议的实际父子ID构建。核对self+children=inclusive、所有完整阶段、同线程嵌套。按page+generation匹配source到先前target；区分同一clear→composite链和其它来源。边界相邻只证明来源，不证明无reader或可合并失败域。CPU可在线程间加，wall区间重叠不得相加或叫锁等待。
7. 不与构建/其它benchmark竞争。先完成所有构建和方法校验，再串行18过程。只授本用例的诊断、数量归因和条件成本，不授产品安全/收益/M6资格。最终交付完整来源、绝对CPU/非执行时间/残差、合法性判断、下一可实施责任与有限证据缺口。

## 首批完成后的有限判别追加

首18过程已完成且全部19更新。详细两个current均闭合56首次fill+4整页default移除后fill+36跨merge复制+36同merge clear→composite复制。粗粒度差额主要在composite；其中原机制之外的composite residual约0.95～1.00ms。下一只判别两个问题，不补首批样本：

- 在原`prepareWriteBaseLocked`已经得到的VersionInfo上记录captured、publication、replicaCount、recoverableBefore、sealed/pending/removed；不加查询，不把采样时无capture当作允许原位写的授权。
- 把当前composite residual划入原bitBlt外框、source accessor构造、manager geometry/交付析构，以及原captureReadView准备；保留其它残差，避免把所有residual误称兼容安装。

仅派生current v2库，原观察库/全部首批数据保留。一个能力过程，然后固定两个mode3过程；共3个追加过程，无新upstream对照/CI或优化实验。量/结果若变单列，所有事件互斥等式/标签与实际库复核；完成后停止本包，不继续细分到每个container。
