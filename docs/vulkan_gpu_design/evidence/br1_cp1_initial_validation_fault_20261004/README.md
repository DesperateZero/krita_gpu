# CP1 initial replica validation 分配失败收敛（2026-10-04）

本批产品 `65e7d60aba9d4da5312764736157571a6b1648c5`，父 `65746168836602d1700eefac67b083dd9e80d696`。它沿 §16.101 后的第一组差集，只收回外部 initial replica adoption 的 provider validation 活动计数；没有新增 API、owner、线程、队列或恢复阶段。

## 父版本反例与当前终点

扩展后的 `pageStoreNativeCopyIsLockExternalRetainedAndFailClosed` 让已有 provider 包装器在 `validate()` 抛出 `std::bad_alloc`。函数末尾已有 caller 错误返回，但父版本的 provider 区间使用手工 relock/decrement；异常跨过这两步后，`activeProviderCalls` 永久为 1。[父版本日志](parent-red-arm64.txt)以 **2/1/0** 红在计数期望 0，同一 replica 的后续成功 adoption 也无法让初始化越过残留活动门。

当前 `adoptInitialPage` 用无分配作用域覆盖整段 provider validation。拒绝仍由原函数级 `bad_alloc` 终点返回 `false`，作用域先恢复 owner gate 并把活动计数归零；原外部 replica 未被 Store 接受或复制，紧接着同一 handle 重试成功并继续原初始化/native-copy/read/close 流程。

## 当前提交验证

[机器结果](results.json)绑定产品、父提交、两份源码和四份原始日志：

- 父版本定向反例：[arm64](parent-red-arm64.txt) **2/1/0**，确认 validation 拒绝留下活动计数。
- Reference normal：[arm64](reference-arm64.txt)与[x86_64](reference-x86_64.txt)各 **790/0/0**。
- 受影响方法的 [arm64 TSAN](reference-tsan-arm64.txt) **3/0/0**，日志中无 ThreadSanitizer 报告。

本批没有重复运行 §16.98 已绑定的 8/24 MiB 长压测。活动 architecture checkpoint 仍早于最近多批已提交源码，本批未把旧生成基线记为通过，也未刷新它掩盖差异。

## 剩余

完整 CP1 仍未关闭。第一组现在排除 §16.99 read/capture、§16.100 import/archive read caller、§16.101 archive poll/cancel terminal及本批 initial replica validation；继续处理有实际分配反例的其他 node/control/task、线程、publication、late-fence 与 close 端点。第二组为非 Darwin capacity/free 实现和平台运行；第三组为 29 个历史 UE/default abort 可回收资格。M6/M7/M8 正式资格仍为 0/3。
