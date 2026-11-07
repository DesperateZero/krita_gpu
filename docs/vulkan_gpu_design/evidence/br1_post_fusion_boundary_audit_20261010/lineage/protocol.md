# 融合后剩余责任与跨更新边界判别（事前冻结）

产品为8198c36ed722030edae715b7423554036bf1bcf7，正式对照仍为9a24ae0d8c070884fb013594191002e1a1b39a19。当前未插桩image库必须与上一包candidate-r1的SHA256 `77299ab0a112f338b0216eac38a52aa83b2fec3054fb6992a8a3b1417f15ec3d`一致；先冻结运行库，再从实际链接输入编译观察副本，不改产品源码/对象。复用20261007的matched freehand fixture、同Qt/插件/seed、ARM64、8段4显式更新、像素与生命周期断言。

本包回答：当前相对upstream额外CPU主要在哪个责任；投影96次冷准备中的跨更新重复属于同字节重算、页粒度放大还是交付版本边界；哪一项具备合法删量及净预算。19次内部更新不预设为不可改变，也不因最终像素相同就授权删除。真实canvas的同步updateCache读者与无canvas性能夹具分开审查。

## 有限实验

1. capability：original/off/jobs/lineage各current/upstream一次，共8进程。off=派生库观察关闭，jobs=worker职责及merge整体，lineage=进一步投影阶段、冷准备、capture、seal/commit/operation事件与身份。observer自测覆盖父子CPU守恒、重复finish、异常展开、关闭模式。
2. original：8个ABBA/BAAB交替块，共32进程；A=current，B=upstream。独立单位为顺序块，主端点Stroke CPU（process user+system），次端点wall及Undo/Redo/Teardown。每块两次各版本求均值再相减，块中位数及100000次固定seed percentile bootstrap点位95%区间。刷新差额，不作正式M6资格或2%非劣判断。
3. jobs：4个同样顺序块，共16进程。按job_stroke、job_merge、其余process CPU分账，投影merge inclusive不与job_merge相加。与original比较观察扰动；负残差或明显排序扰动则责任时间结论保持未知。
4. off：2个同样顺序块，共8进程。仅检验派生布局/关闭观察有无大于主差额20%的明显偏移；小样本不证明统计等价。
5. lineage：current固定4进程；仅判别数量、页/源/目标代际、merge矩形与事件先后，不将细粒度计时当净优化预算。连同capability共68进程，禁止扩样到通过。

样本顺序为capability→original→jobs→off→lineage。无构建或其他基准同时运行。每进程120秒超时后kill/reap；退出非零、像素/回调/析构断言失败、库身份错误、事件溢出/跨阶段/父子账不守恒立即停止，保留失败。各批验证输入前后哈希。调度导致内部更新数量变化记录为因变量，不按19剔样。

## 竞争解释、预算与停止

- 投影仍居新增CPU前列：由新jobs同分母对照证伪；旧7–9ms与旧1.204ms禁止相减。
- 同一页多次准备来自重叠字节重算：用每次merge矩形交集和页身份判别；不把整页保存成本当成被重算的像素。
- 跨通知/真实消费者前后的版本可合并：追到实际updateCache及源更新顺序；缺可见性/延迟/失败证明时不进入产品实现。
- 每次冷准备价格已接近必要成本：本包不预设；如边界删量不足，下一候选回到当前最重责任内的必要事实和冗余管理，而非重领clear融合。

本包没有事前产品收益点预测。数量上96与唯一页数之差只是候选重复上限；合法净删量待证。只有合同、命中、替代净预算齐备才另冻实施预测；否则交付明确判别及一个有限后续目标，不追加同义诊断。
