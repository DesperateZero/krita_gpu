# CP1 archive terminal callback 分配失败收敛（2026-10-04）

本批产品 `65746168836602d1700eefac67b083dd9e80d696`，父 `caaafcf58d21f5d5470dc28fa80ef146fbdb59f2`。它沿 §16.100 后的第一组差集，收回 exact-generation archive 完成轮询与取消回调两个终点；没有新增 API、owner、线程、队列或恢复阶段。

## 父版本反例与当前终点

扩展后的 `asyncArchiveCompletionCancellationAndShutdownAreFailClosed` 先让异步 archive 成功完成，再令最终 `contains()` 检查抛出 `std::bad_alloc`。父版本虽然把异常折叠为空事件，但已经领取的 pending record 永久停在 `busy`，第二次轮询仍取不到事件；[父版本日志](parent-red-arm64.txt)以 **2/1/0** 红在 `firstEvents.size() == 0`。

当前 `pollArchiveCompletions` 在领取 terminal candidates 后安装无分配作用域回滚：成功记录仍由原 erase 终结，任何分配失败则只把身份仍匹配的 surviving record 解除 `busy`。第一次轮询返回原空事件，pending 数保持 1；第二次轮询收割同一成功事件，版本与 completion 身份不变。

同一用例再令 `cancelStoreExact()` 抛出 `std::bad_alloc`。`cancelArchive` 现在以同一无分配作用域归还 `activeProviderCalls` 并解除原 pending record 的 `busy`，把分配拒绝折叠为原 `false`；紧接着对同一 completion 重试取消成功，后续 poll 仍产生原 Cancelled 事件。两条路径都不重放 archive 写入，也不新建第二份 pending 状态。

## 当前提交验证

[机器结果](results.json)绑定产品、父提交、两份源码和四份原始日志：

- 父版本定向反例：[arm64](parent-red-arm64.txt) **2/1/0**，确认 terminal record 被永久留在 `busy`。
- Reference normal：[arm64](reference-arm64.txt)与[x86_64](reference-x86_64.txt)各 **790/0/0**。
- 受影响方法的 [arm64 TSAN](reference-tsan-arm64.txt) **3/0/0**，日志中无 ThreadSanitizer 报告。

本批没有重复运行 §16.98 已绑定的 8/24 MiB 长压测。活动 architecture checkpoint 仍早于最近多批已提交源码，本批未把旧生成基线记为通过，也未刷新它掩盖差异。

## 剩余

完整 CP1 仍未关闭。第一组现在排除 §16.99 read/capture、§16.100 import/archive read caller，以及本批 archive poll/cancel terminal；继续处理有实际分配反例的其他 node/control/task、线程、publication、late-fence 与 close 端点。第二组为非 Darwin capacity/free 实现和平台运行；第三组为 29 个历史 UE/default abort 可回收资格。M6/M7/M8 正式资格仍为 0/3。
