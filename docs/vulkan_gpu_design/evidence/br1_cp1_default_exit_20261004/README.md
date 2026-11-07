# CP1 双 native 释放失败与默认宿主退出（2026-10-04）

本目录复核 `kisFreePageStorage` 在 `munmap` 和同地址 `mach_vm_deallocate` 都失败时的最后出口。产品保持 `1177fa5ecab8318fe044b071342eb0ab51654e27`，生产、产品测试及派生审计改动0。诊断interposer只对探针明确传入的映射base/span各拒绝一次，不影响其他映射；探针使用最终候选 `libkritaimage` 的原导出分配/释放函数。

## 默认退出尝试

arm64首轮不安装信号处理器。子进程实际分配1MiB、32字节对齐的1,064,960B映射，interposer先令 `munmap` 返回EINVAL，再令 `mach_vm_deallocate` 返回KERN_FAILURE。日志到达 `libc++abi: terminating`，只读采样确认主线程位于 `kisFreePageProcessStorage` → `std::terminate` → `abort` → `pthread_kill`，即产品确实执行预定fail-fast。

macOS宿主在SIGABRT处把子进程保留为UE，父进程60秒内无法`waitpid`，外层PID 5900超时后被runner回收，子PID 5915由launchd接管并保持UE。该轮不计通过，`default-dual-release-arm64/`保留运行身份、日志、结果和采样；未继续x86默认退出，避免重复增加宿主残留。只读清点由28增至29个UE，未清理宿主。

## 双失败实际路径

后继探针只在子进程安装async-signal-safe SIGABRT处理器：处理器写单字节标记并 `_exit(134)`，不修改产品库和两项OS释放调用。父进程通过管道分别收到 `U`（munmap拒绝）、`V`（mach_vm拒绝）和`A`（abort到达），再实际回收子进程。最终结果：

- arm64：`munmap=1 mach_vm=1 abort=1 child_exit=134`，父进程actual0/reaped，1.674秒；
- x86_64：相同三端点，父进程actual0/reaped，0.506秒。

两架均确认最终候选镜像和interposer加载，运行输入在退出后复核未变。由此关闭“双native释放失败是否真实到达fail-fast”的差集；守护结果不授予macOS默认SIGABRT可回收资格，也不把首轮UE改计为通过。

## 裁决

当前void deleter在两个OS释放都失败后无法安全归还地址或撤销费用，保持`std::terminate`策略；本轮没有依据把它改成静默泄漏、伪报free或继续运行。剩余宿主出口缩为 **29个历史UE和默认abort可回收资格**。CP1的三组产品责任不变：完整owned/外部native总硬界和首次span合并、其他真实故障及联合终点、非Darwin实际实现和平台运行。M6/M7/M8正式0/3，persistent默认关闭。
