# 空源原执行顺序修正与独立确认

r0 已按固定16块停止：Stroke CPU节省1.23975ms [0.77775,1.786]，但Undo CPU回退0.027ms [0.010,0.064]、wall回退0.03225ms [0.0065,0.0605]。未因此宣布所有控制通过。64个原样本、源码差异和候选原库均保留，不与新批拼接。

量上Undo无融合可得，旧实现仍把空源的clear延后到plane无源出口，这是一条真实零收益的路由差异。r1仅在原setupProjection的既有eligible判断中确认源extent与updateRect相交：不相交或无源，按原顺序先clear；有源仍原生产候选。没有runtime开关、全局状态或另一个恢复owner。预期：Stroke36冷准备/13批次删量不变；Undo/Redo仍无新增operation，Undo的clear时序恢复。这个因果解释待测，不能先认定27μs全部来自延迟clear。

r1引入一次eligible source extent读取，时间包含在净收益内。保留最初0.5–1.5ms工程预测、δ=0.5ms，原r0只作已失败控制的诊断；不使用旧r0数值重估新收益范围。先四目标安全测试，再独立4过程数量能力，最后另16块64进程ABBA/BAAB。主CPU估计/pointwise区间/seed/timeout/全部样本保留规则完全沿原PROTOCOL。r1控制若仍有明确回退则如实保留，不追加无源码变更样本或据结果补非劣阈值。
