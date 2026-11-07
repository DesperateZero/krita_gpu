# CP1 native mutation provider preparation 分配失败收敛（2026-10-04）

本批产品 `f0246c95c4ecb7fd2abce8f689b63d52878087f9`，父 `c19c6d83016423f4cdd7c8894e0ee7305caa6ebe`。它沿 §16.103 后的第一组差集，只收回 native mutation Fresh 写准备的 provider 分配失败；没有新增 API、owner、线程、队列或恢复阶段。

## 父版本反例与当前终点

扩展后的 `pageStoreCallsProviderOutsideGlobalLock` 用原 mutation session 在稀疏默认页触发 Fresh/Discard 准备，并让 provider `prepareWrite()` 抛出 `std::bad_alloc`。父版本没有 caller catch，[父版本日志](parent-red-arm64.txt)以 **2/1/0** 红在异常越过 `beginWrite`；同一异常还会跳过 owner gate 恢复和 `activeProviderCalls` 递减，使原 session、transaction 与 close 不能沿正常终点收敛。

当前 `beginWriteImpl` 用无分配作用域覆盖该 provider preparation 窗口。`bad_alloc` 先恢复 owner gate、归还 `activeProviderCalls`，再写入原 mutation 错误并返回无效 guard。拒绝后活动计数为 0，原 session 可取消、transaction 可 abort；同一 fixture 随后继续原 generic 写、读、retirement 与能力归零流程。

## 当前提交验证

[机器结果](results.json)绑定产品、父提交、两份源码和四份原始日志：

- 父版本定向反例：[arm64](parent-red-arm64.txt) **2/1/0**，确认异常越过 caller。
- Reference normal：[arm64](reference-arm64.txt)与[x86_64](reference-x86_64.txt)各 **790/0/0**。
- 受影响方法的 [arm64 TSAN](reference-tsan-arm64.txt) **3/0/0**，日志中无 ThreadSanitizer 报告。

本批没有重复运行 §16.98 已绑定的 8/24 MiB 长压测。活动 architecture checkpoint 仍早于最近多批已提交源码，本批未把旧生成基线记为通过，也未刷新它掩盖差异。

## 剩余

完整 CP1 仍未关闭。第一组现在排除 §16.99 read/capture、§16.100 import/archive read caller、§16.101 archive poll/cancel terminal、§16.102 initial validation、§16.103 implicit default materialization及本批native mutation preparation；继续处理有实际分配反例的其他 node/control/task、线程、publication、late-fence 与 close 端点。第二组为非 Darwin capacity/free 实现和平台运行；第三组为 29 个历史 UE/default abort 可回收资格。M6/M7/M8 正式资格仍为 0/3。
