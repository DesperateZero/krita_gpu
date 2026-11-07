# 原物理释放事实复用：事前试行协议

起点：产品d182a34bd0196079bc40d2ab7d00b8e326e4a58a、文档5ac0154c3；原image da4304d429134da577087e15004b4d98d93b7fc5c97a1bf6d8da4f4a615d66d1。旧D1/D2与读意图均结束，不重采。本轮目标是实际跟踪一个有界优化并反测03k的预测/选择；正向结果不是预设结论。

必要事实：每块物理存储只能释放一次，预算必须在真实free后归还实际capacity；Darwin低对齐普通分配的capacity来自malloc_size，带前缀分配的base/bytes已存于原块。分配函数固定以capacity>65536选择mmap，否则operator new。释放没有改变这一事实的合法写者。

现状：普通块free先由kisPageStorageBytes查询malloc_size(data)，再为分支重复查询；低对齐映射还查询malloc_size(base)；高对齐前缀块的分配方式也经malloc_size(base)重新发现。理想：普通块仅查一次并直接释放；前缀块读取原mapping，按原capacity阈值决定delete/munmap。保留munmap失败时mach_vm_deallocate及双失败terminate；其它平台不变。不加字段/owner/缓存、不前移预算归还、不绕过实际释放。

数量模型：普通块N、低对齐mapping M、高对齐前缀A，malloc_size查询删除N+2M+A；真实free、capacity、驻留寿命和收费次数不变。竞争项：未消费before已证明可删但跨层改造净价未决；resetPixel小memcpy在已有匹配机制账中未命中，不能凭旧fill成功再领取收益。当前候选单函数、没有API/布局迁移，值得度由实测单价与真实次数决定，不能沿用跨层读API的0.3ms阈值。

阶段1：先构建单TU派生库，原/新free同库开关；独立计数模式按阶段和普通/低对齐映射/高对齐前缀汇总。匹配fixture原库1、计数A/B各1，核验19updates/8segments/4callbacks/像素历史/销毁/实际库/退出。计数含所有线程，非逐动作时钟。

隔离单价实验在同一派生库中，固定代表布局：普通64/512/4096/16384/65536B、低对齐映射65537B、高对齐32B对齐的512B和4096对齐的65537B。每种布局8个ABBA/BAAB交替块，每配置每块16轮，每轮先分配64块并触碰首尾，随后只计时释放；归还容量求和必须等于分配时实际capacity。所有布局、所有块保留。微基准是条件价格，不能直接宣布整笔收益；同一过程内部块不冒充独立进程CI。数量和单价取齐后，在产品改动前另存PREDICTION.md，给有来源的条件范围和是否值得进入单函数实施的裁决。

阶段2仅在净单价支持正删除且维护复杂度下降时进行：以显式补丁落实原函数，追踪普通/映射/高对齐/空指针/失败fallback/非Darwin/预算最终归还。复用实际storage、CPU mutation/reference、low memory/TileData测试；必要边界反例先补。产品候选冻结后独立真实fixture：父/候选16个平衡ABBA/BAAB块共64过程，非计数生产库；主端点Stroke CPU，wall及Setup/Undo/Redo/Teardown分别报告，块为重采样单位，固定10000次bootstrap、seed20261009、95% pointwise CI。预估若低于全笔可分辨量，则如实分开局部兑现和整笔未决，不改端点或增加样本。没有显著结果也不自动证明本项零收益。

本轮总量预先封顶：阶段1的3个fixture和1个单价过程；阶段2最多64个fixture及必要语义测试。编译/分析不与性能过程并行。失败先停查因、保留全部原始结果；不追显著性。旧upstream差额不跨批扣减，M6/正式family独立；技能只有达到原03k正向闭环条件才晋升，单元提速不自动等于M6主目标命中。
