# 优化技能纠错更新

**现在可以更新技能，不必等待又一个优化项成功；但这次只能称为纠错更新。** 新选择流程尚未证明能可靠选中前列可优化项并预测有价值的净收益，继续按新规则开展前瞻验证，不为完成“技能升级”重复追逐已否决候选。

按[skill-creator](/Users/apple/.codex/skills/.system/skill-creator/SKILL.md)修改已安装的[algorithm-cost-optimization](/Users/apple/.codex/skills/algorithm-cost-optimization/SKILL.md)，保留触发描述、UI配置及旧引用归还示例。正文只合入通用判断，新引用文件保存候选记录与少量冻结反例，不把整个03k复制进技能，也不固化BR1阈值。

## 更新依据与边界

| 纠错项 | 已有依据 | 本次改变 |
|---|---|---|
| 必要事实与候选准入 | [原试行回放](../br1_first_principles_selection_20261009/README.md)：结构删量和责任桶有权重未证明主端点价值 | 从消费者/变化/失效推导合法算法；关键净价未知先做有界判别，不能直接组成产品大包 |
| 排名口径 | [排名审计](../br1_candidate_rank_audit_20261010/README.md)：高频Work释放不等于前列CPU成本 | 区分当前、相对基线额外、合法净回收三榜；前列判断需同分母竞争责任 |
| 分支与数量净账 | [空历史试行](../br1_history_admission_trial_20261009/README.md)：跳过760次，前后净删656；非空控制增加查询却零删量 | 分开空/非空/复用/恢复价格，扣除新增和跨阶段成本，排程相关数量不能冒充稳定基数 |
| 调用上下文 | 同一试行首版在持shard锁的visitor中重入getter并死锁 | 原consumer矩阵增加caller持锁、锁内回调及重入条件 |
| 精度与预测 | [误差审计](../br1_candidate_rank_audit_20261010/README.md)：独立CPU节省0.4545ms [−0.028,1.404]，区间宽为δ的14.32倍 | 事前说明δ和可行精度；工程范围、探索参考、点预测与统计区间分开，不以落入宽范围宣称校准成功 |
| 方法状态 | 数量实施与否决闭环已完成，正向收益闭环尚未成立 | 允许据反例修正规则，同时保留效果验证欠项 |

这张表是已知证据到规则的人工审阅映射，**不是独立行为测试或流程成功率**。核心变化是把已有“次数不等于时间”的提醒落实到候选准入、排名和净预算决策，并把安全/精度反例纳入原流程。

## 保存与检查

- [before/SKILL.md](before/SKILL.md)和[after/SKILL.md](after/SKILL.md)：完整前后快照；其他技能文件同目录保存。
- [skill.diff](skill.diff)：全部实际变更，包含新增reference；UI配置及旧示例没有变化。
- [validation.json](validation.json)：已安装文件与快照SHA256、产品/外层起点、结构校验、技能相对链接检查及快照一致性结果。

结构校验使用系统skill-creator的`quick_validate.py`；相对链接检查只确认技能引用文件存在。人工核对没有新增统一δ、样本数、成功率或强制子代理要求，没有改写旧候选预测/确认结论。以上不能替代新候选的前瞻行为验证。

产品保持`c13c44249338bf10477b9b07c65726e5933e51f9`，生产源码与`d182a34bd0196079bc40d2ab7d00b8e326e4a58a`相同；外层起点`f00bf8a82`。本轮无产品/产品测试改动、新性能过程0。同步[03k](../../br1_modification_guide/03k_first_principles_candidate_selection.md)、[验证追踪](../br1_first_principles_selection_20261009/README.md)、[92 §16.165](../../92_br1_m6_m8_execution_baseline.md#optimization-skill-corrective-update)和导航，原冻结报告不改。

下一优化继续用于验证**候选价值及预测能力**：先在前台较大责任中证明合法净预算及可行精度，再选择完整责任实施；并非继续优化才能允许修正技能。M6资格和现有未通过项保持。
