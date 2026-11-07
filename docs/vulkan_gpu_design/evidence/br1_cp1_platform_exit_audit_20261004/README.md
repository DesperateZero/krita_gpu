# CP1 实际 fault 停止规则与平台出口审计（2026-10-04）

产品保持 `db7930797f4661e3a030b4004bca85c8a7011d4d`，生产和测试改动 0。本轮从 §16.106 的差集继续反查 PageStore、publication、read、retirement 和 archive 的真实分配边界，不把测试 provider 可以主动抛异常等同于生产分配。

## 受控 fault 清点

- provider 的 `requestReplica`、同步 source/payload/write-copy、transfer、resolve、validate 和 owned retirement 已分别由原 caller 或 owner 捕获；retirement wait/task 的实际分配由函数级 `bad_alloc` 终点保留同一 record。
- archive 的 store/read、poll 和 cancel 已有 caller 联合终点；生产 `contains()` 只是锁内 `QHash::contains()`，不分配。publication/restore 的候选容量使用付费 allocator，准备失败返回无效候选，原 transaction/root 不安装。
- `releaseAccess()`、静态 capabilities 和只读 presence 查询在当前生产实现中不分配。foreign/no-record retirement 分支没有生产 caller；现有三个 caller 都传递 owner record 或原 preparation。为这些测试缝新增 throw hook 不构成产品修复。

五个主要实现文件的 SHA-256 记录在 `results.json`。本轮没有找到 §16.99–§16.106 以外的新生产 allocator 反例，因此 fault 清点在这里停止。以后只有同时具备生产 allocator 栈、父版本红例和原 owner 恢复终点的反例才重新进入 CP1；不再用开放式搜索维持 CP1。

## 当前宿主默认 abort

复验前 `ps` 中 UE/E 数为 0，历史 29 个 UE 已不在当前宿主进程表；这只说明宿主已在外部复位，不能倒推原失败已被父进程回收。随后运行一个与 PageStore 无关的最小控制：子进程关闭 core、保持默认 `SIGABRT` handler 并调用 `abort()`。父进程轮询 30 秒仍不能 `waitpid`，子 PID 90016 变为 `UE`，`SIGKILL` 后状态不变；采样停在 `abort → pthread_kill → __pthread_kill`。当前宿主因此仍不能取得默认 abort 可回收资格，并新增一个只能由宿主复位清除的 UE。

这证明退出缺口属于当前 macOS 15.7.3（24G419）宿主行为，而不是 PageStore fail-fast 是否到达；§16.93 的产品双 native 释放路径和带诊断 handler 的双架回收结果保持。为避免继续制造残留，不再重复默认崩溃探针。

## 非 Darwin 出口

当前机器没有 Docker、Podman、Colima、Lima、QEMU、Multipass、Orb、Nerdctl 或已配置 SSH 目标。非 Darwin fallback 仍按 request+prefix 计费，缺目标 allocator 的实际 usable-size 上界和匹配 free 运行资格。这个合同不能在 Darwin 上用假定的 glibc/Windows size class 实现并宣告通过。

完整 CP1 现在只保留两个平台出口：

1. 在真实 Linux/Windows runner 上实现并验证 capacity 预留、实际 usable/live、并存 peak 和 matching physical free；
2. 在能正常回收默认 `SIGABRT` 的 macOS 宿主上复验，或把该宿主能力明确移出产品资格合同。

本轮没有重跑已由 §16.98 绑定的 8/24 MiB 压测，也没有改写已通过的功能/TSAN资格。完整 CP1 与 M6/M7/M8 正式资格仍未通过。

源码身份、证据哈希、当前文档锚点与停止规则一致性见 [`document-check.json`](document-check.json)。
