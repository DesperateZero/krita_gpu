# CP1 后台退休分配拒绝与晚 capture 联合终点（2026-10-04）

本批绑定产品 `ee67754c0297e596f9a5b1d1cbe21166488df1e1`、父 `1177fa5ecab8318fe044b071342eb0ab51654e27`。范围只有原 retirement queue 已接纳记录在后台调用 provider 时抛出 `std::bad_alloc` 的责任：不新增 owner、队列、状态、锁、公共/保护 API 或通用 executor 异常策略。

## 原缺口与责任

`KisPageRetirementQueue::retireRecord` 已在 provider 调用前准备 operation，并用原 scope guard 负责未接受 operation 的取消；但 `provider->retire()` 的 `bad_alloc` 原来会越过 `retireBatch` 和 reclamation job。异常展开会执行 executor 的 finished cleanup，却先销毁本地 batch，未经过逐记录 `finishAttemptLocked`：原 record 没有重入队，active 计数没有归还，executor 的 post-invoke 线程状态也无法执行，随后异常越过 worker 入口触发 terminate。现有“provider 返回 invalid result”测试只覆盖正常返回，不能证明另一个线程上的异常退出和可恢复 close。

现在只在原 retirement owner 内捕获这一个分配拒绝。provider 没有返回 accepted result 时，原 guard 取消 prepared operation，`retireRecord` 返回拒绝；`retireBatch` 保留同一 record，沿已有 wait/1–100ms retry、Debt、close 和 owner-lifetime 规则继续。已经返回的 provider result、pending completion 和不可重放分支没有进入 catch，也没有由 executor 猜测业务恢复。

## 联合用例

`backgroundRetirementAllocationFailureRetries` 先发布 `0x31`，由 captured view 保留旧版本，再发布当前 `0x77`。确认晚 view 仍读取旧像素后，测试设置 provider 连续三次抛 `bad_alloc` 并释放该 view；从此不再发起 mutation、显式 retirement process 或第二次 close。原 history/retirement task 自动重试，随后断言：

- 三次拒绝全部消费，成功调用发生在同一原记录之后；
- pending retirement、provider operation 和 RetirementDebt 全部为零；
- 当前像素仍为 `0x77`，晚 capture 的旧像素未污染当前发布；
- close 成功，capability 和 provider backing 最终归零。

生产一文件 **+10/−2**，测试一文件 **+34/−0**。完整 diff、源码和实际二进制哈希见 `results.json`。

## 运行结果

- 定向 normal arm64、normal x86_64、TSAN arm64 各 **3/0/0**。
- `KisPageStoreCpuMutationTest` 完整 normal arm64 **1387/0/0、10431ms**，x86_64 **1387/0/0、11316ms**。
- 同目标完整 TSAN arm64 **1387/0/0、220423ms**，日志无 ThreadSanitizer 报告。
- 相邻 retirement/retry/close 组合在 normal 双架和 TSAN arm64 各 **23/0/0**；这些用例也包含在上述完整目标内，不另作总数累加。

构建使用现有 `_build-br0-cpu` 与 `_build-br1-tsan`，提交后产品 tracked tree clean；本批没有重跑已经完成的长 manager/pressure。首次完整 arm64 的三项测试失败来自编辑新断言时误改两处同形旧断言，定位后恢复原行并重新完整运行；原始中间日志被后续运行覆盖，保留的精确输出摘要见 `intermediate-assertion-edit-failure-summary.txt`，不计入最终通过。最终源码只有上述两文件差异。

## 边界

这是 provider 合同上的确定性 `bad_alloc`，关闭一个真实后台 task/晚 capture/history/retirement/close 联合责任，但不是跨线程 allocator interposition 的全部 site census。完整 CP1 仍欠：全部 owned/外部 native 总硬界及首次外部 span；其余 node/control/task 的真实 allocator fault 与 read/publication/晚 fence/caller 组合；非 Darwin 实现和平台运行；29 个历史 UE 与默认 abort 可回收资格。完整 CP1 与 M6/M7/M8 正式资格保持 0/3。
