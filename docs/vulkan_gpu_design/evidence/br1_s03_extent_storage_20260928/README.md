# S03 / OP5：原 extent 双轴容量写前准备

日期 2026-09-28。设计与阶段状态以 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)为准；待改内容、实际代码段、责任和验收关系见 [OP5 实施表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#extent-storage-implementation)。

## 原问题与当前实现

旧 `Data::unsafeMigrate` 在实际 new buffer 前就修改活动 capacity/offset，分配拒绝会让字段与旧 buffer 不一致，且 allocate/free 都在 migration gate 内。当前改为原 Data 的临时 Growth，仅持两个实际 buffer 和几何；使用 64 位临时量检查 span、capacity、offset 和字节乘法。原双轴 `prepareTileRange` 在两个分配均成功后复验并安装，安装时复制当前计数；分配期间的计数变化不会被早先快照覆盖。当前轴已覆盖所需范围时直接复用，其余候选须容纳当前几何。最多三次候选准备，最后只有一次当前容量检查，没有持锁循环分配。

原 manager 的 cursor、packed、clear、precise/rough copy 五条 native 路径以及显式持久 cursor 在执行像素前调用此能力。cursor 用原实际页并集的坐标边界确定**原稠密轴容量**，并不把范围内空白页加进 write footprint。packed 释放 manager gate 后才扩容。准备拒绝沿 Failed/原 void failure context 返回，原 canonical pixels、事务、索引及 visible extent 不变；本次实际分配候选释放后可以正常重试。

容量安装不改变 count/min/max/currentExtent；之后实际 tile 增删才改变它们。`notifyTileAdded` 也先确认两轴容量再改任一计数，已预备 native 范围不会在此分配；全量 `replaceTileStats` 先准备，再清原计数。结构替换 `takePrepared` 仍要求调用者排除并发 mutation，容量不代替其权限。成功安装但尚未使用的容量保留在原轴，后续 operation 失败不缩容。

## 验证与测量范围

- 新增每架构 **50 个测试**：几何/计数/极端坐标/候选失效 1 项，八 worker × 1,000 次准备增删 1 项，四 BPP × 正负远坐标 × 六条实际路径 48 项。真实入口检查写前容量且旧 extent 不变、完整页字节、旧 exact view、undo/redo、删除。定向 [focused-01](focused-01.log)为 149 passed、0 failed、0 skipped，另含原 96 个 presence cases、原 extent 并发测试与 init/cleanup。
- [实际 allocator/gate/failure 探针](extent-storage-probe.cpp)与[interposer](extent-storage-interposer.cpp)使用编译后的实际准备入口。基础冷扩容观测到 2 次分配、12,288 B、2 次旧 buffer 释放；1,000 次暖准备/新增/删除零分配、零释放。复制仍为 O(axis capacity)，此结果不包含 wrapper/hash、payload、canonical publication 或整个 stroke。
- 分配/释放 hook 让另一线程获取原 extent/migration gates；真实 native caller 还核对 manager gate 可取得。另一模式在分配期间增加原计数，或先扩到更大的几何，使旧候选失效；最终保留这些计数。该 hook 只观察本线程实际 allocator/free，未把辅助线程自身的扩容归入主线程分配数字。
- 对四 BPP、正负坐标、六入口逐个拒绝两轴实际分配，每架构 **96 次拒绝、48 个成功对照**。拒绝时无 callback body、无 generation/active transaction/原预算变化、旧 buffer/几何/extent 保持；随后正常重试及旧/新像素验证通过。第二轴失败前的第一轴候选被实际释放，未装入活动 owner。

## 失败记录

[probe-initial-01](probe-initial-01-driver.log)和[probe-initial-02](probe-initial-02-driver.log)是探针缺少实际 ReadPage 定义 header 导致的编译失败；补入 `KisPageStoreIteratorReadScope_p.h` 后编译通过。[initial-03](install-arm64-extent-storage-initial-03.log)的故障计数把拒绝后的 C++ exception runtime 分配也计入 extent，第一次拒绝报 3 次调用而非 1 次，整体失败。interposer 现一次拒绝后停止跟踪后续分配，保留已登记候选的 free 观察和正常 exception runtime；[initial-04](install-arm64-extent-storage-initial-04.log)全部通过。生产代码和失败断言未因此放宽。

## 最终同源码验证

最终 [checks-01 identity](checks-01/identity.json)、[矩阵清单](checks-01/manifest.json)、[probe 清单](probes-manifest-01.json)和 [evidence-scope](evidence-scope.json)绑定同一源码和实际二进制：

- **19 个 Qt 目标 × arm64/x86_64：8,854 passed、0 failed、0 skipped**。42 条矩阵记录另含实际构建、结构门、六项工具自测和最终 Ninja no-op；每架构增加 50 项。
- **48 个最终探针全部通过**：46 个继承入口和双架构 extent-storage。每架构 96 个实际拒绝、48 个成功对照及三种并发/暖容量模式；所有 extent 冷分配/已登记 buffer 的释放时，另一线程可取得原 extent gates。真实六路径还核对 manager gate 可取得。
- [结构门](baseline-01.log)与[调用图](graph-01.log)：86 TUs、1,794 APIs、18,659 edges、17 callbacks；21 manifest、25 ownership、16 census、19 intrusion，181 dirty source/build files。原侵入 ratchet 和布局门未放宽。
- HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含必要新文件的源码差异 SHA-256 **`a8c44c0b58d67b79be406ab4f0106a2e83c211fb7a56c6ab05b926c1aeaf7f03`**。全部矩阵库/插件/静态库/测试、probe 与 interposer 身份已经复验；[git diff 检查](diff-check.log)通过。只含本批五个文件的增量见 [extent-storage-code.patch](extent-storage-code.patch)。

[指南校验](validation.json)记录修改 ID、源码锚点、文件反向索引与链接；[指南增量](guide-update.patch)单独保留。文档校验不重跑运行测试，也不授予新阶段资格。

## 未闭合的责任

本批是 OP5 的必要容量前置。暖准备仍取得两个原 migration read gates；冷增长复制完整旧轴容量，边缘删除 updateMin/updateMax、clear/destructor 的扫描/销毁尚未有界化。现有 Data 析构仍有原 gate 内释放，不属于本批准备/交换旧 buffer 的锁外释放结论。完整 retained/peak/shared-parent budget 仍待 OP9，当前局部预算不变不能解释成 extent 已经收费。

OP4 的 wrapper、map migration、GC enqueue/回收，OP6/OP7 的最外层 publication/cut 与终结，OP8 raw/planar 和 MR4 exact 失败字节恢复继续。真实默认 brush 的持久 owner/current/source/producer 联合启用、M6/M7/M8、Fresh 2%、Vulkan、TSAN、BR1-PERF 仍开放；不以局部零分配或测试数量授予正式性能资格。优先级保持 stroke → undo → context。
