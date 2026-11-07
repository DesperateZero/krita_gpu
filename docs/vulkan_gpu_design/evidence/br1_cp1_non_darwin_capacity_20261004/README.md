# CP1 非 Darwin 实际容量与平台出口结算（2026-10-04）

产品提交为 `b51a7602c82bbee6bf2a0df79400dd943d6df5b6`，父提交为 `db7930797f4661e3a030b4004bca85c8a7011d4d`。本轮只关闭 §16.107 保留的两个平台出口；不重跑 §16.98 已绑定的 8/24 MiB 长压测，不改动 Darwin 已通过的小对象 native size class 与大对象精确 mapping 策略。

## 非 Darwin capacity/free

原 fallback 在分配前只记录 request+prefix，`operator new` 的真实 usable capacity 可能更大，不能证明硬界。当前把平台差异收进 `KisPagePlatformStorage_p.h`：

- Linux/Unix 先按 `sysconf(_SC_PAGESIZE)` 计算完整 payload、mapping record 和 alignment padding 的页取整容量，再用匿名 `mmap` 分配；释放使用原 mapping base/span 调用 `munmap`，失败保持 fail-fast。
- Windows 先按 `GetSystemInfo().dwPageSize` 做同一容量计算，再用 `VirtualAlloc(MEM_RESERVE | MEM_COMMIT)`；释放只用原 base 调用 `VirtualFree(..., 0, MEM_RELEASE)`，失败保持 fail-fast。
- mapping record 与 payload 位于同一笔已预留容量中；`kisPageStorageBytes`、live/peak 提交和最后 free 返回同一个容量事实。没有 size-class 猜测、第二收费表或第二释放权威。
- Darwin 产品分支未改变。其他没有 mmap/VirtualAlloc 合同的平台保留原 fallback，不能借本轮取得资格。

实现依据与系统合同相符：Windows `VirtualAlloc` 在空地址下把 size 向上取整到页，`VirtualFree(MEM_RELEASE)` 要求原 base 且 size 为 0；Linux `mmap(NULL, length, ...)` 返回页对齐区域，`munmap` 用原 base/span 删除 mapping。

## 真实平台运行

临时 CI workflow 只存在于远端 `codex/cp1-platform-exits-ci` 分支，不在产品提交中。最终运行 [37196520779](https://github.com/DesperateZero/krita/actions/runs/37196520779) 绑定 CI head `15e9e7c3f63c7f72b21efa7d3d54e7ab4480b868` 和产品父 `b51a7602c8`：

- Ubuntu 24.04：页大小 4096；48 个 size/alignment 边界和 8 线程 1024 次并发 allocate/write/bytes/free 全部通过。
- Windows Server 2025、VS 2026 image：页大小 4096；同一 48+1024 用例全部通过，另用 `VirtualQuery` 核对 allocation base 与 region size。
- 初次运行 37196382058 的 Linux job 已通过；Windows 在编译前因 runner 未初始化 `cl.exe` PATH 失败。只修 workflow 的 VS 环境初始化后，第二次运行双平台通过；失败未归因于产品，也未从证据中删除。

本地同一产品提交还通过：共享 Unix mapping 探针 48+1024；Android aarch64 API 28 交叉编译；Darwin arm64/x86_64 的 `processStorageReportsReservationSeparately` 各 3/0/0。后者验证平台无关的 reserved→live→physical-free 账本，不能替代 Linux/Windows 运行；两类结果在本轮联合。

活动 architecture checkpoint 仍是旧生成基线，当前检查同时报告既有 memento intrusion 差异和本轮新增私有头的 inventory 差异；本轮不刷新该基线来掩盖差异，也不把 architecture gate 记为通过。它不属于 §16.107 保留的两个平台出口。

## 默认 abort 合同处置

§16.93 已证明产品在 `munmap` 和 `mach_vm_deallocate` 都失败时到达不返回的 fail-fast，且诊断 handler 控制可由父进程回收。§16.107 的最小非 PageStore 默认 `SIGABRT` 控制仍在当前 macOS 15.7.3 宿主形成 UE，`SIGKILL` 无效；这说明默认 signal 后能否被 `waitpid` 回收由宿主负责，产品没有继续运行、伪报 physical free 或撤销 live charge 的安全修复点。

因此 CP1 产品资格保留“两个物理释放都失败时不返回且不伪退费”，把“当前宿主必须回收默认 abort”改为测试宿主健康前置。当前 UE PID 90016 和原失败证据继续保留，必须由宿主复位清除；不再用重复崩溃探针制造新 UE。该处置没有把 fail-fast 改为静默泄漏，也没有宣称当前宿主已经健康。

由此，§16.107 的两个平台出口均结算，完整 CP1 关闭。M6/M7/M8 正式资格仍为 0/3，下一工作包是 CP2。
