# CP1 commit provider validation 分配失败收敛（2026-10-04）

本批产品 `5b4c65ae4bd6ead34e910391472a007930bad372`，父 `f0246c95c4ecb7fd2abce8f689b63d52878087f9`。它沿 §16.104 后的第一组差集，只收回 commit proof provider validation 的分配失败；没有新增 API、owner、线程、队列或恢复阶段。

## 父版本反例与当前终点

新增 `commitProviderValidationStorageFailureIsRecoverable` 先用原 mutation session seal 一页 private write，再让 commit 阶段的 provider `validate()` 抛出 `std::bad_alloc`。父版本的 `validatePreparedPage` 没有 caller catch，[父版本日志](parent-red-arm64.txt)以 **2/1/0** 红在异常越过 `commit`。原 `commitClaim` 虽能在栈展开时恢复 owner gate并释放 preparing 标记，但业务 caller 不能得到原失败结果，也不能沿普通重试终点处理该次拒绝。

当前 `validatePreparedPage` 把 provider validation 的 `bad_alloc` 折叠为原 `false` 结果和错误文本。第一次 commit 返回无效 ticket；`activeCommitPreparations` 回到 0，原 transaction 与 sealed proof 各保留一份，当前 committed 像素不变。解除故障后用同一 prepared input 重试成功并正常 close。

## 当前提交验证

[机器结果](results.json)绑定产品、父提交、两份源码和四份原始日志：

- 父版本定向反例：[arm64](parent-red-arm64.txt) **2/1/0**，确认异常越过 commit caller。
- CPU normal：[arm64](cpu-arm64.txt)与[x86_64](cpu-x86_64.txt)各 **1393/0/0**。
- 受影响方法的 [arm64 TSAN](tsan-arm64.txt) **3/0/0**，日志中无 ThreadSanitizer 报告。

本批没有重复运行 §16.98 已绑定的 8/24 MiB 长压测。活动 architecture checkpoint 仍早于最近多批已提交源码，本批未把旧生成基线记为通过，也未刷新它掩盖差异。

## 剩余

完整 CP1 仍未关闭。第一组现在排除 §16.99 read/capture、§16.100 import/archive read caller、§16.101 archive poll/cancel terminal、§16.102 initial validation、§16.103 implicit default materialization、§16.104 native mutation preparation及本批commit provider validation；继续处理有实际分配反例的其他 node/control/task、线程、publication late-fence 与 close 端点。第二组为非 Darwin capacity/free 实现和平台运行；第三组为 29 个历史 UE/default abort 可回收资格。M6/M7/M8 正式资格仍为 0/3。
