# 空历史任务准入试行：删量兑现，独立净收益未通过

本包从[物理释放单价排除](../br1_storage_release_trial_20261009/README.md)转向完整Work寿命，完成事前探索、蓝图/索引、产品实现、安全修复、真实数量复核和独立确认。**生产优化回退，保留新增边界测试；没有获得技能正向闭环，不追加样本。** M6/M7/M8资格、2/20校准及默认关闭保持。最终处置见[DECISION](DECISION.md)。

事前材料：[探索协议](PROTOCOL.md)、[产品预测/唯一实施矩阵](PREDICTION.md)、[安全反例及修订](REVISION-1.md)、[产品计数复核协议](PRODUCT-COUNTS.md)。起点产品d182a34bd0/tree e03a63d2、image da4304d4；修订候选image 55f09a6d。开始于2026-10-09，最终收口跨到10日。初步栈统计26条history路径更正为40/185，Work erase仍21条；详见释放包勘误，不改写事前协议。

## 理想算法、原路径与边界

必要事实是“此key现在是否有历史”，原metadata已维护historyCount。普通新任务原路径为分配含32版本候选槽的Work、收费、入队、worker查询、空则erase/free。候选在原owner内先查Work；已有Work保留repeat/ready，只有新Work用现存historySlice(key,{},1).total预检，零则返回。非空版本的reachability、root/revision/protection复验、预算拒绝重试、最终退休/free全部保留。

这不是未来事件订阅：overlay supersede、canonical commit、restore安装后的请求，以及read/captured/snapshot释放后的key/scanAll请求继续存在。已有扫描的repeat不能删。普通路径新增每个新候选的metadata锁、索引查询及最多一条历史读取；空任务不再合并重复请求，因此新的查询数量可能增大。未增加第二owner、cache或持久字段。

第一次产品实施遗漏了callback锁上下文：metadata.visitPageKeys持shard锁调用requestKey，新增historySlice递归取非递归锁，完整overlayStorageAtCapacity测试挂起。sample定位后人工SIGTERM并reap，保留候选5d157894及失败日志。修订仅让该visitor传inspectHistory=false，沿原准入/重试；压力rescan仍可能创建空Work，不能声称全环境删除。修订双架构8组共16过程、9370 QTest/0失败/0跳过通过。此前失败记录单列，不计作clean首次通过。

## 事前预测与实际

| 项目 | 事前预测/探索 | 修订产品数量复核或独立确认 | 裁决 |
|---|---|---|---|
| Stroke新Work | 探索734→212；条件预计约700–750→200–250 | 868→212，减少656（75.58%）；非空候选两边均212 | 候选终点命中，父任务量范围低估，调度影响未充分建模 |
| 空准入/新增查询 | 每新候选多一次查询；空不分配 | B新候选972，空skip760；不能将760当净删除656；visitor bypass次数0 | 保留了替代成本，skip与净删量分开 |
| Stroke worker slice | 空任务原会再被消费 | 868→209，非空回收/19updates/像素不变 | 数量兑现，不等于这些动作的独占时间 |
| Undo/Redo | 不承诺收益，控制另判 | 两阶段各56新任务全部非空，各新增56次查询且没有空Work删除；Redo slices216→216 | 原预测没有充分定价的必付新增成本 |
| Stroke CPU | 条件0.2–1.0ms；δ0.1ms；探索0.660ms [0.232,1.696] | **0.4545ms [−0.028,1.404]** | 点估计落预测范围，独立正收益未确认，未通过事前门 |
| Stroke wall | 不保证加速 | 0.18575ms [−0.303,0.5815] | 未确认 |
| Undo CPU / wall | 不外推Stroke | 0.0605 [−0.018,0.143] / 0.04025 [−0.023,0.1245] ms | 未确认 |
| Redo CPU / wall | 控制另判 | −0.05875 [−0.113,−0.018] / −0.04125 [−0.108,−0.007] ms | pointwise回退信号，与非空路径额外查询方向一致；尚无独立分摊证明 |
| Teardown CPU / wall | 保持最终free | −0.018 [−0.0425,0.0085] / −0.0075 [−0.032,0.009] ms | 未确认差异，终点通过 |
| Setup CPU / wall | 未命中、不得领收益 | 0.51575 [−0.9795,2.3085] / 0.36875 [−1.002,2.278] ms | 负控制，不能从Stroke扣除它 |

节省为A−B，正数才是加速。数量复核2过程不提供时间收益。独立确认固定16个ABBA/BAAB块/64过程，主Stroke CPU的95%区间为block bootstrap、50000次seed20261010；其它端点仅描述性pointwise，不能宣称全端点family显著。所有64过程通过像素/19updates、UndoRedo/销毁、实际库/共同依赖和退出检查。探索32过程和产品确认64过程不混用。

独立Stroke有5/16块CPU反向，父库慢值30.675ms与两个大正差块8.531/7.377ms全部保留；候选范围14.981–18.088ms。既不删尾“净化”结论，也不将这些尾解释为已确认的尾延迟收益。原算法也有很快样本，整体分布仍影响可分辨精度。区间跨零不是证明没有收益，点估计落宽预测范围也不足以证明预测准确。

## 原控制与实施矩阵结算

原Fresh/H4固定M5控制各320过程完成，各四桶40对/20平衡块，50000bootstrap seed260926，单桶一侧98.75%下界；各四桶family至少95%，不宣称八桶联合95%。以下下界全部≥0.98，但不能改变主增量未确认的裁决；比例中的既有优化不能归本候选。

| 控制 | ARM K1 | ARM K16 | x86 K1 | x86 K16 |
|---|---:|---:|---:|---:|
| Fresh候选/M5吞吐比 | 1.58079 | 1.22530 | 1.52815 | 1.24950 |
| Fresh一侧下界 | 1.56769 | 1.22260 | 1.52347 | 1.24225 |
| H4候选/M5吞吐比 | 1.69028 | 1.54711 | 1.54505 | 1.61359 |
| H4一侧下界 | 1.68173 | 1.54031 | 1.51838 | 1.59882 |

主端点未通过且存在Redo回退信号，按固定规则恢复两个生产文件为父内容；保留测试13行，本地提交c13c442493。恢复后构建成功，新image SHA256 ba5876d6（不声称与冻结父库da4304d4二进制逐字节相同）；两架构定向retainedHistoryReclaimsInBackground及overlayStorageAtCapacity共12 QTest/0失败/0跳过通过。证据单独记录为restored-*，不冒充候选性能验证。不将本次候选收益填入最终产品或旧upstream账。

| ID | 最终实现/证据 | 状态 |
|---|---|---|
| H01 | Collector lower_bound及新任务预检；candidate-r1/product.diff | 已实现并测试；收益未准入，生产回退 |
| H02 | 保留metadata原计数及原getter；修复visitor已持锁上下文 | 保留原合同 |
| H03 | Publication overlay/commit/restore全部原请求保留 | caller闭包已核对 |
| H04 | Read取消、lease、captured、snapshot释放原请求及最后root扫描保留 | 完整Mutation/Reference通过 |
| H05 | 原rescan callback禁止重入metadata；已有Work repeat、拒绝债务、close/drain不变 | 首版反例已修复，完整双架构通过 |
| H06 | retainedHistoryReclaimsInBackground在第一次supersede前增加96页当前读/释放/drain | 候选下两架构通过；测试保留 |
| H07 | 候选三文件28新增/4删除，无新owner/字段/恢复域；最终仅保留测试13行 | 索引闭合，生产算法恢复父版本 |
| H08 | 2探索机制+32探索时间+2产品机制+64独立确认；新100过程共300 QTest通过 | 主端点未通过；Fresh/H4各四桶通过 |

## 技能反测与下一责任

筛选正确排除了约0.03ms的高频free重复查询；选中了有真实大删量的完整任务，且工程净收益点估计量级比该微项大。但还没有证明稳定、有价值的产品净收益。因此**03k继续试行，已安装skill保持不变**，不能因为完成了矩阵就宣布升级。

两处实际缺口：一是索引记录了caller但没有记录调用时已持锁，导致安全反例；二是按总体空任务量选项，却没有给Undo/Redo这种零过滤收益、必加查询的路径单独定价。独立确认阻止了将探索正数直接当产品结果，这属于流程的否决能力证据，不是正向预测成功率。

下一有界候选应考察：能否在本来就进入metadata的状态迁移/保护释放事件中传递现存的历史事实，避免统一准入getter重复查；同时证明旧root/晚读者/恢复及metadata持锁visitor仍会请求原回收器。不得把它直接标成可实施方案：需先有实际producer/consumer、失效窗口、合法删量及非空路径净价。也不重开本包或既有LP/读意图批次加样。

复现：先查看冻结身份与原协议，数量及timing原始结果分别在product-capability/results.json、confirmation/results.json；[analyze_confirmation.py](analyze_confirmation.py)只分析原64过程。全部失败、源码差异、runner派生差异、构建/加载身份随raw.tar.xz及manifest保存。未重新测upstream，不能从旧7.643ms差额机械减去本次0.4545ms。
