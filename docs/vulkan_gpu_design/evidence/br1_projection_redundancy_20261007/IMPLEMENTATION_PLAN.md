# 稀疏默认页局部clear：修改前预测与有限验证

v3恢复原19次更新、root149代际/89复制/32session，node76代际；两个诊断过程均观测到53条clear→composite直接source链，页并集96。全merge共享责任的条件上限是53准备/复制、13session，但当前仍需独立发布/失败，不作为已可删除产品工作。

其中17条链的clear首次准备没有native source：逻辑默认页在局部default clear时实体化，随后composite又复制它。`fillRect`现仅对整页default clear检查before.isDefaultPixel，部分页没有相同检查。已有managed range覆盖所有targets，before为固定视图；把相同default判定扩到部分页，是合法空操作消除，不需要新owner/API/锁/队列。保持原准入与adapter交付，任何查询拒绝仍返回失败；非default fill及native部分页按原路径。

## 事前数量与收益预测

同一普通8段/4update/4worker例，若更新工作量保持19：root代际149→132，native复制89→72，默认初始化60不变；node76/20不变；合计代际225→208、复制109→92，逻辑复制减少278,528 B。session32没有领取下降目标，canonical commit受原client并发分组影响，不做固定数量预报。

v3被删的17次clear准备及其17次后继复制准备合计原生线程CPU为0.322833/0.312337ms，约0.318ms。它是重插桩定价，包含两个时钟查询与原准备链；不是候选实测加速。按本批原库stroke约8.196ms，若其它成本/等待不变、没有新增开销，被删CPU有25%/50%/100%落在关键路径，单项wall降幅约0.97%/1.94%/3.87%。额外default判断/resolve、回收减少、并发/调度变化尚未计价，预测可失效；不把它写成95%区间或保证。全53条链的0.406/0.431ms也不是整个projection 28%的可删预算。

## 完整迁移矩阵

| consumer/位置 | 原责任、变更与保留 | 数量/行为证据 | 状态 |
|---|---|---|---|
| backend fillRect逐页分支 | 原before固定视图+managed range下，对整页/部分页共用default判定；跳过逻辑默认页实体化 | 默认页不新增generation/provider工作；native部分页仍COW | 待实施 |
| manager clear与projection caller | 沿原extent/adapter/delivery/dirty流程，不增加入口与隐式作用域 | 原像素/更新/退出；不改变callback工作 | 待验证 |
| 失败/重试与并发范围 | reserve、before查询失败、取消及晚delivery仍原终结；无操作页也保留原范围准入 | 原ClearRangeAdmission、CancelledPrivateClient等完整manager覆盖 | 待验证 |
| 稀疏/历史/旧读/格式 | BPP1/4/8/16、history开/关；部分clear稀疏洞不分配、非default fill仍写、old view不变、undo/redo | 一个数据化资源/语义反例；在parent库应失败，在候选应通过 | 待验证 |
| 其它fill调用 | uniform非default/fullpage删除、trim/copy、ordinary stroke原逻辑保持 | 完整manager、merger与Reference双架 | 待验证 |

## 固定验证顺序

1. 先冻结原image库、实际输入和源码。产品仅修改backend及新增稀疏洞回归。先用新测试二进制+parent库跑新增8行反例（预期失败）；候选运行完整manager、merger、PageStore Reference两架。测试失败保留，修复后另批，不能挑行当完整通过。
2. 通过后机制固定四过程（parent/candidate/candidate/parent），原计数夹具各一笔，检查数量预测、全部像素/更新/退出和加载身份；120s/kill+5s reap；不插入额外诊断库。
3. 未插桩固定ARM/x86各24配对、12顺序平衡块，共96过程，使用同一个原MatchedFreehandBaselineTest、同Qt/插件、parent/candidate image库。沿CP0块log latency ratio几何均值，20,000 bootstrap，seed261018，pointwise双侧95%诊断区间，主端点stroke-to-projection-ready，pen-up/undo/redo/teardown为次端点。每过程120s/kill+5s reap；原始失败保留、身份/语义失败停止，不删尾、不延长到通过。无同时间构建/采样。

固定完成即停止。机制兑现、局部收益、原控制与完整M6分别裁决；旧正式校准/metadata分母/CP0/GPU缺项不因本包消失。

安全环境修正：parent新增反例8/8预期失败，candidate ARM完整manager1319/0/0。随后merger在testMerger初始化blur filter处SIGSEGV：runner误用仅五个brush插件的普通freehand目录，blur未加载。保留退出/IPS，改为既有完整build/bin插件集合；仅继续固定剩余五过程（ARM merger/Reference、x86 manager/merger/Reference），不重复已通过manager、不改变产品或性能样本协议。完整结果分别记录原批及修正批；若仍失败，先定位产品反例，不能当环境忽略。

原控制补证（启动前登记）：未插桩增量比较结束后，串行重跑§16.137原固定M5 Fresh/H4两个family，各四桶/每桶40对，沿原250ms、20顺序块、50,000 bootstrap/seed260926、单侧98.75%与throughput lower≥0.98。复用原runner源码，仅以证据副本的__file__重定向输出目录；不修改工作、参考库、顺序或停止规则。它裁决当前累计产品对固定M5的不劣性，不能归因本次17页增量或充当正式M6校准。
