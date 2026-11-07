# CP1 alias provider preparation 分配失败收敛（2026-10-04）

本批产品 `db7930797f4661e3a030b4004bca85c8a7011d4d`，父 `5b4c65ae4bd6ead34e910391472a007930bad372`。它沿 §16.105 后的第一组差集，只收回 native mutation alias seal 的 provider preparation 分配失败；没有新增 API、owner、线程、队列或恢复阶段。

## 父版本反例与当前终点

新增 `aliasProviderPreparationStorageFailureIsRecoverable` 先为原 mutation session 声明 immutable alias，再让 seal 阶段的 provider `prepareSynchronousSource()` 抛出 `std::bad_alloc`。[父版本日志](parent-red-arm64.txt)以 **2/1/0** 红在异常越过 `seal`。原作用域保护虽能恢复 owner gate 和 `activeProviderCalls`，业务 caller 不能取得普通失败结果并原位重试该 alias 输入。

当前 `prepareAliasLocked` 把 provider preparation 的 `bad_alloc` 折叠为原 storage-refused 结果和错误文本。第一次 seal 返回 `false`；`activeProviderCalls` 回到 0，原 transaction、page claim 和 alias 输入保留，committed 像素不变。解除故障后同一 mutation seal 成功，原 transaction commit 后读取 alias 像素并正常 close。

## 当前提交验证

[机器结果](results.json)绑定产品、父提交、两份源码和四份原始日志：

- 父版本定向反例：[arm64](parent-red-arm64.txt) **2/1/0**，确认异常越过 seal caller。
- CPU normal：[arm64](cpu-arm64.txt)与[x86_64](cpu-x86_64.txt)各 **1394/0/0**。
- 受影响方法的 [arm64 TSAN](tsan-arm64.txt) **3/0/0**，日志中无 ThreadSanitizer 报告。

本批没有重复运行 §16.98 已绑定的 8/24 MiB 长压测。活动 architecture checkpoint 仍早于最近多批已提交源码，本批未把旧生成基线记为通过，也未刷新它掩盖差异。

## 剩余

完整 CP1 仍未关闭。第一组现在排除 §16.99 read/capture、§16.100 import/archive read caller、§16.101 archive poll/cancel terminal、§16.102 initial validation、§16.103 implicit default materialization、§16.104 native mutation Fresh preparation、§16.105 commit validation 及本批 alias preparation；继续处理有实际分配反例的其他 node/control/task、线程、publication late-fence 与 close 端点。第二组为非 Darwin capacity/free 实现和平台运行；第三组为 29 个历史 UE/default abort 可回收资格。M6/M7/M8 正式资格仍为 0/3。
