# 产品实施前冻结预测与独立确认协议

父产品d182a34bd0196079bc40d2ab7d00b8e326e4a58a，tree e03a63d2a33324a55c72b7eb8ec097deab96b171；父库SHA256 da4304d429134da577087e15004b4d98d93b7fc5c97a1bf6d8da4f4a615d66d1。固定父库取自br1_cpu_lifecycle_implementation_20261009/candidate，不以将被重建的build/bin充当父库。本记录在产品修改和确认样本之前写入。

选择依据：重复malloc_size的条件Stroke价仅约0.02–0.04ms，排除主优化。释放栈的26条history路径/21条Work节点erase只产生候选，不构成CPU比例。合法空历史替代的独立计数与8块探索支持进入产品：Stroke新Work734→212，非空候选均212；CPU块中位节省0.66025ms，探索95%区间[0.2315,1.696]。探索数据不得进入下述确认。

## 算法与数量、时间预测

原算法为每个新key分配Work→收费→入ready→扫描history→空则出队/free。理想算法在原owner锁内先查Work；已有任务沿原repeat/ready路径；不存在时查询现有historySlice(key,{},1).total，零则返回，非零按原hint插入、扫描和退休。仍使用测过的getter，不顺带增加新API、cache、owner或字段。

净模型：被避免Work的构造/分配/收费/入出队/扫描/free − 每个新候选新增的metadata锁/查找/HistorySlice值构造及最多一条历史读取 ± 调度与cache变化。空任务不再合并后续请求，因此B的694次skip不能视为694个净删除；能力过程实际观察为522个节点减少。条件数量预测：同fixture新Work约700–750→200–250，保留全部非空回收，字节/像素/19updates与终点不变；这是调度相关范围，不是固定计数合同。

条件工程预测：Stroke CPU节省约0.2–1.0ms，以探索结果作有误差的定价；不是严格算法下界或统计置信区间。δ=0.1ms适用于本次无新owner、仅一处准入的小改动。wall探索未确认，不保证加速；Setup不命中，不计入候选收益。Undo/Redo/Teardown需另看，不按Stroke比例外推。

## 有限实现索引与追踪矩阵

| ID | 位置/consumer | 处置与保持的合同 | 验证 | 事前状态 |
|---|---|---|---|---|
| H01 | KisPageHistoryCollector::requestKeyLocked | lower_bound后只对新任务预检；空不分配，其余原try_emplace(hint)、repeat、ready及bad_alloc/rescan保留 | 源码diff、能力计数、未插桩确认 | 待实施 |
| H02 | MetadataCoordinator::historySlice及historyCount维护 | 保留原shard锁/现存精确计数；不返回借用iterator、不改变history生命周期 | metadata/状态机源码审查、Reference测试 | 保留 |
| H03 | PublicationCoordinator overlay collectRetirements、commit及restoreRetainedEpoch | Historical创建/选择变化后原requestKey保留；恢复行1364是restore而非abort | consumer索引审查、完整Mutation测试 | 保留 |
| H04 | ReadCoordinator release/finishCaptured/releaseSnapshot | pin/捕获/epoch保护消失后原key/scanAll请求保留；历史默认材质晚创建后也由释放请求接续 | late reader、last use、read terminal测试 | 保留 |
| H05 | Collector collectSlice/collectUnreachable/background/close/clear | 已有scanning repeat、root/revision/protection复验、退休拒绝与有界预算及最终free不变 | historySweepRevalidatesAndRevisits、historyRefusalPreservesOriginalWork、close/drain等 | 保留 |
| H06 | CpuMutationTest::retainedHistoryReclaimsInBackground | 在历史出现前显式经历当前读/释放并drain，再创建受保护历史、拒绝close、晚释放并无新输入回收到终点 | 原真实96页测试扩展，两架构 | 待实施 |
| H07 | 所有consumer/旧路径删除/表示 | 原空Work准入被替代；无新头文件、字段、API、恢复域；无其它owner改写 | diff与requestKey/collectUnreachable全caller索引 | 待核验 |
| H08 | 实际库、端点及控制 | 安全先行、真实加载库与同依赖确认；Fresh/H4与局部增量分开 | 以下固定实验 | 待验证 |

## 独立确认与退出

先build与双架构8组安全通过。再用非插桩正式父库A/候选B，原matched fixture，16个ABBA/BAAB交替块、64个新过程，固定序列ABBABAAB重复8次。所有像素、19projection updates、Undo/Redo、销毁、timeout/reap和加载身份沿用探索校验；每过程120秒，错误即停止并保留。不与构建或另一基准并发。

主端点为Stroke process CPU。每块取两次A/B均值之差，再取16块中位；bootstrap50000次、seed20261010，双侧95% pointwise区间。准入要求点估计≥0.1ms且下界>0；预测准确性另核0.2–1.0ms，不以门通过自动宣称预测准确。所有阶段CPU/wall保留为描述性区间，不授多端点family资格。慢值全部保留，不删尾、不扣Setup、不追加样本。

原Fresh/H4控制按已有驱动分别执行ARM64/x86_64 × N64K1/N1024K16四桶，对固定M5基线，每桶40配对、20平衡块；250ms完成率、2%非劣、50000bootstrap seed260926，一侧98.75%/桶控制各自四桶95%family。两family分开报告，不宣称八桶联合95%。不重跑未修改的20桶正式校准，不借本包授M6。

独立CPU未确认、控制失败或新合同反例时保留全部数据，停止本候选；有合同反例先修复后另冻批次，性能未决不追加同包样本。技能仍需分别反测：选项排除、合法删量、净预测与独立确认、控制/终点。正向闭环不足即保留试行；不得靠缩小目标制造成功。
