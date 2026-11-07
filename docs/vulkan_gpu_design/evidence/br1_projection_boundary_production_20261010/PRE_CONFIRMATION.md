# 最终确认前登记

生产守卫已补 `!KisPaintLayer::needProjection()`，临时绘画目标和动画洋葱皮仍先 clear 再更新源；具体 paint layer 的剩余 recalculate 只释放旧 safe projection，不读父目标。自定义 subclass 的 visitor 中间读取反例通过。所有实际 payload/预算/锁/adapter/取消责任仍交给原 native operation，不新增 owner 或协议队列。事前“无 TLS”精确指删除原型自建的 pending/target TLS；仍使用现有 `KisStrokeJobFailureContext` 的栈式错误桥接，该框架内部使用既有 TLS，不能声称零 TLS 访问。

观察库只增加统计，不替换生产算法。父计数使用上一包同 c13 基础的派生库且 `FUSE=0`（原清零/合成顺序）；候选计数由本次已编译产品派生。两个父、两个候选均实测：Stroke merge/composite 为19；fill 13→0、成功冷准备132→96、new batch / successful seal 32→19；候选13次成功融合、失败0、初始化566464B。Undo / Redo 的填充、operation、冷准备、batch / seal 均保持。commit 随调度变化，不作为固定删量。计数模式的 CPU 不用于定价。

收窄条件后删量完整兑现；保留原工程范围0.5–1.5ms、δ=0.5ms、16块64进程及同一估计规则，不按当前数据改预测。最后补足“像素回调完成但尚未发布”的 current reader 检查后，重新运行受影响测试批；通过才启动最终未插桩性能批。

故障注入覆盖准备时 bad_alloc、实际 kernel 已改首块后 bad_alloc，以及 finish / publication 之前拒绝；这几条合法失败都由原 native RAII 撤销。适配安装本身要求预备完整、原 manager 锁下完成；本次保留并复验现有 adapter preparation/abort/barrier/delivery/lifetime/conflict 测试，不在已 publish 后抛诊断异常冒充合法可恢复失败。真实硬满的原路径与候选均拒绝，效果相同、reservation与活跃写归零，释放压力后可重试；这个反例不证明原路径在所有满额条件下都能成功。

最终统计主端点是本机 ARM64 的 projection-ready 增量 CPU，不能授 M6、上游差额或 GPU 资格。生产常规 CPU 优化与 persistent/handoff 默认策略分开。
