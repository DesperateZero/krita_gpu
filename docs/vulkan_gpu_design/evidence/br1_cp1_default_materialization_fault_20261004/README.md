# CP1 implicit default materialization 分配失败收敛（2026-10-04）

本批产品 `c19c6d83016423f4cdd7c8894e0ee7305caa6ebe`，父 `65e7d60aba9d4da5312764736157571a6b1648c5`。它沿 §16.102 后的第一组差集，只收回稀疏默认页首次物化的 provider request 分配失败；没有新增 API、owner、线程、队列或恢复阶段。

## 父版本反例与当前终点

扩展后的 `sparseDefaultPageFirstWriteAndUndoStayVersioned` 让已有provider包装器在隐式默认页的 `requestReplica()` 抛出 `std::bad_alloc`。父版本没有 caller catch，异常越过 `acquireRead`，同时跳过 `activeProviderCalls` 递减和 `finishPreparationLocked`；[父版本日志](parent-red-arm64.txt)以 **2/1/0** 红在异常越界。留下的active计数会阻塞关闭，留下的default preparation会让同一页后续读取永久等待。

当前 `ensureDefaultPageLocked` 用无分配作用域覆盖provider调用，并在同一 `bad_alloc` 终点完成default preparation、写入原错误并返回 `false`。拒绝后 `activeProviderCalls == 0`、`activeDefaultPreparations == 0`；同一稀疏页立即重试，继续原默认像素读取、首次写入、undo/redo与close流程。

## 当前提交验证

[机器结果](results.json)绑定产品、父提交、两份源码和四份原始日志：

- 父版本定向反例：[arm64](parent-red-arm64.txt) **2/1/0**，确认异常越过caller。
- Reference normal：[arm64](reference-arm64.txt)与[x86_64](reference-x86_64.txt)各 **790/0/0**。
- 受影响方法的 [arm64 TSAN](reference-tsan-arm64.txt) **3/0/0**，日志中无 ThreadSanitizer 报告。

本批没有重复运行 §16.98 已绑定的 8/24 MiB 长压测。活动 architecture checkpoint 仍早于最近多批已提交源码，本批未把旧生成基线记为通过，也未刷新它掩盖差异。

## 剩余

完整 CP1 仍未关闭。第一组现在排除 §16.99 read/capture、§16.100 import/archive read caller、§16.101 archive poll/cancel terminal、§16.102 initial validation及本批implicit default materialization；继续处理有实际分配反例的其他 node/control/task、线程、publication、late-fence 与 close 端点。第二组为非 Darwin capacity/free 实现和平台运行；第三组为 29 个历史 UE/default abort 可回收资格。M6/M7/M8 正式资格仍为 0/3。
