# BR1 extent 锁等待：QtCore 因果排查与依赖修复

当前结论：QtCore 负 reader 计数已通过独立复现、原版／修复版源码对照、保留 Krita 扩展的依赖重建关闭。最终库下 **20 目标 × 两架构 8,896 passed、0 failed、0 skipped，54 个故障／分配探针全部通过**。产品源码与产品二进制相对失败矩阵保持不变，仅 QtCore 依赖变化。M6/M7/M8 与 BR1-PERF 仍未完成。

本证据接续 [HX6/HX8 的真实失败](../br1_s03_map_migration_storage_20260928/README.md#未解决的-extent-锁等待)，不删除或覆盖该失败。产品源码仍为 [source-before.json](source-before.json) 记录的工作树：HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`，diff SHA-256 `e809ed039190e4bbc0a6b653653b67325d2761de666bb580a2dbd3e347b73830`。

## 已确认的因果证据

| 对象 | 结果 | 证据 |
|---|---|---|
| 当前安装 QtCore | ARM64 读、写慢路径在 private mutex 后执行普通 `ldr` 复验；没有 acquire 发布同步 | [原二进制身份](qt-original-identity.json)、[两条完整锁函数反汇编](qt-original-lock-disassembly.txt) |
| 当前产品二进制 / 原 QtCore | 第 212 次 `stressTestExtentsColumn` 停滞，8 个 worker 等待；reader=-1、writer=0、waitingReaders=5、waitingWriters=3 | [运行记录](installed-extent-1000-01-identity.json)、[线程栈和锁内存](installed-extent-1000-01-lldb.log) |
| 独立 QtCore 程序 / 原安装 QtCore | 完成 158 轮后停滞，reader=-1、writer=0、waitingReaders=6、waitingWriters=2 | [程序源码](qt-grouped-counter-probe.cpp)、[运行身份](installed-qt-counter-1000-01-identity.json)、[现场](installed-qt-counter-1000-01-lldb.log) |
| 独立 QtCore 程序 / 原版 v6.8.0 源码构建 | 完成 76 轮后停滞，reader=-2、writer=0、waitingReaders=6、waitingWriters=2 | [运行身份](baseline-qt-counter-1000-01-identity.json)、[现场](baseline-qt-counter-1000-01-lldb.log) |
| 同一独立程序 / 同构建参数加两项上游补丁 | 1,000 轮、每轮 32 jobs × 5,000 次 add/remove，完成且最终计数归零 | [运行身份](patched-qt-counter-1000-01-identity.json)、[日志及实际加载库](patched-qt-counter-1000-01.log) |

独立程序只链接 QtCore 和系统运行库，不链接 Krita、PageStore、并发 map 或 allocator hook。它保留原压力测试的 32 jobs / 8 workers / 三个相邻计数器，以及 read → release → write 顺序。上面的重复实验用于定位并发错误，不是性能比较，也不以有限轮数证明所有调度安全。停滞后由 runner 采集 LLDB 现场再终止其自有进程；`-15` 是诊断终止，不是普通测试退出。

## 根因与修复位置

Qt 6.8.0 的 `QReadWriteLockPrivate` 来自 freelist。同一地址释放后可被复用；线程取得该对象内部 mutex 并不必然与新 owner 发布 private 指针同步。仅比较指针地址相同，无法排除复用后的 ABA，也不保证看见新 reader/writer 计数。上游 [80d01c4](https://github.com/qt/qtbase/commit/80d01c4ccb697b9d390cc0da49c2f111b19b4c5b) 在首次访问 private 对象前补 acquire 重载；[4fd8801 / QTBUG-142321](https://github.com/qt/qtbase/commit/4fd88011fa7975ce64d5648698a234f85bac359c) 在内部 mutex 后的复验处补 acquire。后者明确描述了 readerCount 变负后所有 worker 等待的结果。

[最小回植补丁](qt-6.8-qreadwritelock-acquire.patch)同时修改 `contendedTryLockForRead`、`contendedTryLockForWrite` 的上述两处。它不改变 Krita extent 的并行访问协议，也没有增加整笔 stroke 的串行锁。源码和库的对照身份见 [qt-comparison-source.json](qt-comparison-source.json)，配置见 [baseline-config.summary](baseline-config.summary) 和 [baseline-CMakeCache.txt](baseline-CMakeCache.txt)。

## 无效对照与兼容性边界

- 最初两个所谓 source-baseline / patched extent 对照经 `/usr/bin/arch` 启动，DYLD override 未生效。LLDB 证实加载的是原安装库；它们是原库再次复现，**不能用于比较补丁效果**。[无效记录](invalid-arch-comparisons.json)保留名称和原因。后续直接启动 ARM64 进程，并核对实际加载路径。
- 直接加载普通 Qt 6.8.0 Core 的产品测试在 dyld 阶段失败：已有 QtWidgets 需要 Krita 专用 `QFrameRateCompressor`。详见 [原版启动失败](source-baseline-extent-1000-02.log)、[修复版启动失败](patched-extent-1000-02.log)。这些失败没有进入测试，不能计作 extent 通过。
- 已有库比普通源码构建多出的 22 个导出都属于该 compressor，见 [导出差异](installed-only-symbols.txt)。导出集合一致也不足以证明所有 Krita 补丁兼容；需要沿正式依赖仓库定位完整源码后再重建。

## 最终验收与剩余工作

| 最终运行库下的验证 | 结果 | 证据 |
|---|---|---|
| Qt 自身 QReadWriteLock 测试 | 每架构 24 passed / 0 failed | [两架构记录](qt-upstream-test-manifest.json) |
| 真实 extent 重复测试 | arm64、x86_64 各 1,000 次通过，实际加载库已核对 | [arm64](final-arm64-extent-1000-01-identity.json)、[x86_64](final-x86_64-extent-1000-01-identity.json) |
| 原完整矩阵 | 44 条记录、40 个 Qt target/arch；8,896 passed / 0 failed / 0 skipped；结构门和最终 no-op 通过 | [manifest](checks-01/manifest.json)、[源码／二进制／QtCore 身份](checks-01/identity.json) |
| 原 54 个故障／分配探针 | 全部通过，保留 map 每架构 44 拒绝及 store 45 拒绝等实际故障覆盖 | [manifest](probes-manifest-01.json)、[源与运行库身份](probes-source-01.json) |
| 一致性收口 | 原产品源码和二进制未变；本批全部记录使用同一最终 QtCore | [汇总及边界](evidence-scope.json)、[校验程序](finalize_evidence.py) |

最终库 SHA-256 为 `cd0a48d2948af55889625ae0750a7d08895068deae9b6e85bdc3e1fac6dc9434`。[构建与恢复指南](qt-build-recipe.md)明确源码、Krita 扩展、配置差异排除、实际依赖及原库备份；[安装记录](qt-installation.json)确认只原子替换 Core 二进制，其他 Qt 模块和头文件未改。原失败矩阵和无效对照均保留。

两架构通过的是当前开发回归。新旧 Qt 编译器不同，**后续性能控制组与改动组必须使用同一运行库**；本次不继承旧库性能比值，也不授予正式 BR1-PERF。下一步仍是 HX6 跨 job 结构安装能力、HX7 候选寿命、OP6/OP7 联合发布与 HX9/S10 预算，以及 M6 → M7 → M8 的原出口。

[修改指南校验](validation.json)只验证导航、源行、映射和文档身份，不替代运行测试。[指南修改差异](guide-update.patch)相对本次依赖排查前的文档快照生成。
