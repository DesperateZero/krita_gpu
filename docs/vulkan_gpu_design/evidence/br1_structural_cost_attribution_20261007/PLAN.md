# 从upstream差距追溯复杂度来源

用户纠正优先级：目标是解释普通freehand约2.3倍差距的核心新增责任，不能以17页局部浪费作为主解。本包只做结构归因与下一责任设计，不先实施共享scope/cache，也不追加性能样本。

1. 固定当前产品2f22452e2d、外层5da3a9adf；对照同依赖upstream9a24ae0d8c的既有源码/构建。历史profile仍属于128fb32a71前的生产同38834c4e26，不能改写为新产品采样。
2. 重读business-cost-localization四次固定64 replay的selected-stacks及原冻结SHA。原actor分组保持；对双方一致纠正KoStreamedMath/OverCompositor内层kernel被外层adapter遮蔽的类别。只重分析原样本，不重跑/删尾/调整时延区间。
3. 分离像素、明确管理类别、physical heap与未归类；用互斥样本差核对“哪类新增工作”的方向。样本不变成wall微秒、可删比例或因果置信区间。保留19/18更新分布与后续replay暖cache限制。
4. 按upstream→当前真实调用链审查三层：每operation的目标集合/准入/adapter；每generation的provider/预算/metadata/completion；每span/page revisit的guard/read与终结。区分必要合同和当前昂贵表达。
5. 冻结结构证据、现有反证及完整责任优先表。下一应验证结构候选能解释主要残差、预报完整变化，之后才实施；不自动领取局部排序/const循环修复或继续36条copy链。
