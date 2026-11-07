# 前台工作拆分与调度边界审查

**当前不能保证前台算法已足够优，也不能保证调度没有多余成本。** 已有实验定位了责任成本并排除若干局部解释，没有完成业务依赖图与当前执行图的对照。技能虽已有“必要事实、频率/粒度放大”，实际执行仍容易接受既有operation和版本边界，再在其内部选候选。本轮修正这个选择缺口，不宣称已找到新的主要损失或获得性能收益。

产品c13c442493、文档父d99677476；[身份与源码hash](identity.json)绑定本次静态审查。无生产/测试改动、无新运行或性能样本。以下旧数量仅属于各自冻结批次，不能当成当前新测量。M6/M7/M8仍0/3、校准2/20、persistent默认关闭。

## 1. 现有证据能保证到哪里

| 已有证据 | 能支持 | 不能支持 |
|---|---|---|
| [R08计数](../br1_descriptor_search_trial_20261010/README.md)：208次hint命中，其余110–114次搜索首项成功 | 该fixture的共享搜索无向后遍历放大 | 版本节点数量、前台协议或调度已合理 |
| [任务对账](../br1_current_upstream_cpu_ledger_20261009/README.md)：两侧937个stroke jobs、19个merge jobs | 该批差额不是多派发几倍job；投影任务内差额显著 | 每个job的operation/版本/发布次数必要；调度关键路径最优 |
| [排名审计](../br1_candidate_rank_audit_20261010/README.md)：前台准备/发布约4.043ms | 已观测较大责任，值得向上追溯其产生原因 | 4.043ms全部可删或全部是必要合同税 |
| 旧安全/资源测试与局部净收益 | 所覆盖实现的合同与局部结果 | 当前任务、owner、容器和发布边界就是算法下界 |

局部改动不必然让系统变差；真正的风险是把现有拆分写成新接口、不变量和多份长期状态，使后续替代需要迁移更多消费者。因而局部提速仍可保留，但不能作为上层拆分正确的证据。

## 2. 当前代码中需要往上解释的边界

```text
输入笔画/更新请求
 → 原scheduler与update queue选择、拆分/合并区域
 → merge walker执行层依赖
 → setupProjection(clear或临时projection) → 中间reader/recalculate → composite
 → manager几何/adapter准备 → backend operation/batch
 → 页范围接纳 → 每页private版本 → seal/交付 → 后台终结
```

这张图描述当前机制，不是必要算法。理想图先从真实中间消费者、显示/读cut、失败效果和最终释放推导，再决定哪些机制节点需要存在。

| 层与当前位置 | 静态事实 | 尚缺证明；本轮判断 |
|---|---|---|
| [updateProjection](../../../../krita/libs/image/kis_update_scheduler.cpp:163)、[queue合并](../../../../krita/libs/image/kis_simple_update_queue.cpp:320) | 入队后尝试调度；区域合并受patch界、节点/类型/LoD等匹配及面积比约束 | 新下层固定协议成本是否改变适宜粒度未知。合并有延迟/额外像素/取消/内存代价，不能凭面积启发式存在就判调度错误 |
| [isJobAllowed](../../../../krita/libs/image/kis_updater_context.cpp:123)、[walkerIntersectsJob](../../../../krita/libs/image/kis_updater_context.cpp:224) | 使用整块accessRect相交排斥，未按每层冲突细分 | 这是明确保守的实现结构；需要ready、dispatch、真实依赖、冲突和完成关联才能判断本fixture是否因此空转/串行。源码注释不构成实测证据 |
| [setupProjection](../../../../krita/libs/image/kis_async_merger.cpp:277)、[中间处理](../../../../krita/libs/image/kis_async_merger.cpp:193)、[composite](../../../../krita/libs/image/kis_async_merger.cpp:315) | 非临时路径先clear；其后可有original visitor/recalculate/依赖下层的读，再执行合成 | 单一“最终投影相同”不足以融合；必须区分真正需要独立状态的消费者与由当前API造成的切分，不能把独立函数存在当必要cut |
| [manager clear](../../../../krita/libs/image/tiles3/kis_tiled_data_manager.cc:824)、[write operation](../../../../krita/libs/image/tiles3/kis_tiled_data_manager.cc:1769) | clear与合成分别进入准备和adapter交付；write operation在本次调用内合并目标页 | 调用内已经去重不说明跨调用边界合理；公共单操作保证仍保持，但内部merge是否需要逐操作独立交付须另证 |
| [fillRect](../../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1963)、[runCpuMutationOperation](../../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2064)、[batch finish](../../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:611) | fill建立独立batch及before；普通无history operation建立batch，有history时借原scope；batch终结先seal再处理原transaction终点 | 相同transaction不等于相同private版本寿命；这种拆分产生多少合法可合并工作尚未确认。延长scope必须同时解决原失败、读选择、预算、取消和最终释放 |
| [prepareWrites](../../../../krita/libs/image/pagestore/KisPageStore.cpp:1530) | 已有range/execution，再逐页准备 | 对每页独立优化不能回答上层为什么建立这些range和generation。页级成本存在性与上层频率合理性必须分开 |

源码对照固定upstream9a24ae0：simple update queue、updater context、async merger、update job item四文件相同。scheduler有取消重试/唤醒等增量，但原processQueues和区域调度策略沿用。因此不能直接把原调度策略当新增CPU差额来源；也不能凭“沿用upstream”判新代价结构下仍适宜。实际关键路径与等待归因保持未知。

## 3. 不是第一次想到融合，而是没有完成边界裁决

[此前B项](../br1_cpu_blueprint_implementation_20261008/IMPLEMENTATION.md)已识别clear→composite同merge重复生命周期，并列出中间reader、失败、root retention等障碍；[投影归因](../br1_projection_cost_attribution_20261008/README.md)对当时36条重复冷准备给过约0.47–0.49ms的条件毛成本。不能说此前完全没看中层，也不能把这个旧毛价重领为新净收益。

缺少的是逐条回答：哪个消费者在什么时点必须观察哪一版？失败时哪些已经发生的效果必须保留？哪些约束来自用户/外部合同，哪些只是当前把merge拆成两个公共调用后产生的内部要求？真实约束不能删，但“当前实现要求”也不能自动成为不可改变的算法公理。存在一个不适合融合的复杂层不证明所有调用必须完全独立；简单路径可否使用原owner内的完整替代仍待论证，不能预先宣布可行。

这一分析允许结论是“当前边界确实必要”，但必须留下消费者与因果依据。之前停在“不能直接融合”后继续优化页内小项，尚不足以给出该结论。

## 4. 同义门也要区分语义和实现

原[fixture](../br1_upstream_cost_accounting_20261007/matched_freehand_baseline.h)固定8次输入、4次显式update callback、finish/undo/redo和最终像素，只要求`projectionUpdates > 0`；[R08 runner](../br1_descriptor_search_trial_20261010/run.py)为该局部判别额外固定了19次projection通知。

19是那一批的匹配控制，不自动是业务要求。若新候选调整任务合并、投影通知或版本数量，应另冻结构实验协议，以真实消费结果、必需顺序、input-to-visible/pen-up及取消/资源边界验收，把内部数量作为待解释的变化。四次update callback的消费者与语义须先审查，不能一起随意删掉；仅靠最终像素一致同样不足。全部旧样本和结论保持，不回改其验收条件。

## 5. 调整后的下一步与技能边界

下一主判别先围绕**一次投影更新的必要中间状态及失败/交付边界**，关联其原job、读cut、operation、page/generation和最终释放。以此比较：

1. 当前拆分确由真实消费者和失败效果要求，只能改善单次实现。
2. 同一原merge责任内存在无外部消费的中间交付，可通过完整准备/执行/发布替代同时减少多层工作。
3. 内部工作没有明显冗余，但调度粒度或冲突模型使可执行工作延迟。

这是调查顺序，不是新净收益排名。先复用旧生成链和当前源码找最小缺证边界，有限检查应产出一个具体消费者反例、合法替代原型或明确未知；不要求先证明全局最优，也不重跑整个旧成本账。没有证据时不承诺融合收益，不把所有owner/协议一并重写。若需要调度实测，必须关联ready/dispatch/run/finish和真实依赖；不能以总CPU或wall−CPU代替。

已按`skill-creator`对安装技能作有限修正：同义分母区分语义与机制；新增工作拆分/调度审查；候选记录要求解释干预层级；默认提示不再直接跳到一个痛点。保留原完整迁移和独立验证要求。[前后快照](after/SKILL.md)、[差异](skill.diff)、[结构校验](validation.json)随包保存。

以下只是基于已知材料的规则审查，不是盲测或正向性能验证：R08排除不能覆盖版本拓扑；相同job数不能覆盖每job工作与关键路径；19通知不能默认约束新调度；真实中间reader又不能被最终像素oracle略去。技能现在显式要求提出这些问题，但**尚未证明能可靠构造高价值跨层方案或预测其收益**，也不能保证发现所有架构问题。
