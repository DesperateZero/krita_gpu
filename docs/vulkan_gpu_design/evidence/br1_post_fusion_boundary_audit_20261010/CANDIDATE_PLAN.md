# 下一有限候选：同批投影区域精确合并

**当前状态（2026-10-10）：退出PageStore基础性能主线，作为通用候选暂缓实施。** 以下保留§16.170形成的算法、索引和矩阵，Q02–Q07未因此获实施优先级。当前裁决为[92 §16.171](../../92_br1_m6_m8_execution_baseline.md#pagestore-equivalent-performance-scope)，下一主线入口为[同语义替代比较/P01–P05](../br1_pagestore_comparison_scope_20261010/README.md)。未来若恢复本候选，业务净收益单列；要主张PageStore相对收益，须另测upstream匹配策略。

本表是新候选的唯一索引和追踪矩阵。状态是**几何与来源成立，合法实现/净收益待原型判别**，不是生产实施已获验收。当前产品8198c36ed7保持。事前输入和原库差额见[报告](README.md)。

## 理想算法与当前放大

必要输入是一次addJob已提交的同node/type/LoD/crop/flags脏区域集合，不是现有walker数。保持集合覆盖、依赖扩张、取消和最终通知；消费者不能获得未准备的像素。当前27个不重叠区域直接建立walker，局部collect通过包围矩形减少任务，却把已派发的区域再次纳入工作。

构造性候选：

1. 原addJob在建立walker前，使用局部值对输入做同x/width、纵向相邻区域的精确合并；保持patch边界及原区域覆盖，避免新持久owner/队列。生产算法需证明有界复杂度，不能为本fixture引入任意O(N²)扫描或固定坐标特判。
2. 原joinRects保留node/type/flags/LoD/crop/patch约束；仅当矩形包围盒面积等于实际并集面积时允许合并。用64位面积并扣交集，保留空/负坐标/边界语义。这样不需跟踪已完成矩形，也不会因本次collect补洞覆盖它们。
3. 不跨addJob延迟，不跳过源变化，不复用已发布可写字节，不绕过M6/M7保活或失败合同。原worker、merger、通知、终结owner继续工作。

这不是全局最优调度器；同批精确表示是否比允许有限过绘更快须实测。禁用所有带空隙合并可能使碎片任务增加；这一负例是主控制之一。不同producer分批后的同页复访仍保留。

## 数量与时间预测

固定本包四批7/4/8/8区域，可回放得到4/4/4/4个纵向合并区域，78次64×64页访问、164128像素；实际基线19任务、96次冷准备、207840像素。**条件预测**少3任务、18页访问、43712像素，并保持每批请求并集不变。真实调度不保证固定4批，需记录输入和输出两个分母，不为凑预测筛掉不同分批。

时间预测目前是公式，不给伪精确毫秒：减少的页准备/后续管理、作用域和像素成本，减去局部排序/合并/面积判定与跨阶段净增。重观察下16次重叠cold仅0.074–0.093ms，不代表完整生命周期预算。下一原型可将Stroke CPU **δ=0.3ms**作为低复杂度方案的探索价值阈值（约当前额外6.39ms的4.7%）；这不是M6新门。必须同时检查wall、显示延迟及短阶段控制，实际精度不足则保持未决，禁止扩样到通过。

## 代码位置与唯一矩阵

| ID/位置 | 原owner、寿命和上下文 | 删除或保留 | 验证/完成判据 | 状态 |
|---|---|---|---|---|
| Q01 `libs/ui/tool/strokes/freehand_stroke.cpp::issueSetDirtySignals`；`KisPainter::takeDirtyRegion` | 原painter dirty列表，checkpoint后向node提交；不能合并未来请求 | 保留四批源更新与dirty来源；本轮不改producer | 当前/upstream四次来源追踪均输入27个不重叠矩形 | 来源已证；不改 |
| Q02 `libs/image/kis_simple_update_queue.cpp::addJob` | 原局部rects/walkers，尚未派发本批；现有m_lock仅保护队列 | 同批纵向精确合并，减少被后续包围矩形重新覆盖的碎片；不增加全局记录 | 精确覆盖、负坐标、稀疏/大量区域、不同flags/LoD；确认不在长持锁段排序 | 原型待实施 |
| Q03 `collectJobs/tryMergeJob/joinRects` | 原queue及m_lock；只改待执行walker | 约束合并不补洞；保留所有语义/patch限制及原walker重收集 | L形/环形/已派发中间块不被补回；相邻整矩形仍合并；碎片任务负控制 | 放大已证；替代待验证 |
| Q04 `kis_update_job_item.h::runMergeJob`；`kis_async_merger.cpp` | 原worker/merger，更新后同步通知 | 保持原调度和clear融合，不再领取已删36准备 | 独立source更新、复杂层依赖、wrap/LoD、失败/取消；页计数随新分母解释 | 保持；合同待联合验证 |
| Q05 `kis_canvas2.cpp::startUpdateCanvasProjection`；`KisOpenGLUpdateInfoBuilder::buildUpdateInfo`；`kis_texture_tile_update_info.h::retrieveData` | 真实DirectConnection消费者，先readBytes再压缩 | 不以19次通知为合同；保留被要求的可见性与完整覆盖 | callback内真实读取的对照、渐进显示/首次可见/pen-up、取消后无晚错误更新 | 消费链已证；运行控制待做 |
| Q06 `libs/image/tests/kis_simple_update_queue_test.cpp`、scheduler/merger测试 | 现有测试owner；复用原测试 | 加能证伪补洞和覆盖丢失的边界，不镜像实现 | 同批正常/空/相交/稀疏/负坐标、不同节点/type/LoD、并发与取消 | 待实施 |
| Q07 原matched fixture与M6控制 | 同依赖原库/候选、独立顺序块 | 机制计数与未插桩收益分开；两个版本都受益时重算upstream差额 | 先固定原型协议和样本量；CPU价值、wall/其它阶段不回退；安全后再生产独立确认 | 净收益未知 |

停止规则：本包72次诊断不继续扩样。新原型若只有计数改善而净收益不足、任务碎片或显示延迟回退，则否决/保留冻结候选，下一主线转绘画job额外责任；不得继续同一候选的小幅调参直到显著。任何生产实施都需先补Q02–Q07，不能凭几何回放直接提交scheduler优化。
