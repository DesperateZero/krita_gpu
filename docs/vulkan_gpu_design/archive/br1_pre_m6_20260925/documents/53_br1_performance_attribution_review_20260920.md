> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 性能归因复审与分段证据（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

本次复审修订 52 的瓶颈判断和实施优先级，不改变 canonical PageStore 方向、正确性要求或 CPU/GPU/UMA 出口。
**此前“主 stress 的剩余 10× 主要说明真实 mutable CPU 写仍走整页 COW”没有足够证据，现撤回这一归因。**
本轮只增加测试端 opt-in 诊断、保存证据和校正文档，没有实施新的 production 性能修复。

后续验收口径已统一为 [39 的 M/K/X/E](../../../39_virtual_texture_performance_gates.md#56-四类证据与基线配对统一定义)：M 管理对
主干 tile，K 同域驻留算子及单列异构比值，X 跨域，E 同终点产品吞吐/延迟。本文是 CPU-only 混合 stress 的管理热点和
操作计时证据，不是隔离 M 的完整配对证明、真实改写像素 K 或吞吐门禁；更不是 UmaShared/DiscreteVram 的读写性能。
原始数值保持历史范围，新配对 harness、真实写与硬件证据按 52 的 P1/P6 及后续 GPU/UMA 阶段补齐。

版本边界：下文的“当前/仍/本轮”均指第 3 节 hash 对应的采样检查点，不自动描述最新工作树。
后续 D1 已消除删除/restore/default revision 切换时的新 default payload，并完成正确性复验、五次前后计时和新采样，见
[54_br1_optimization_execution_and_deviations_20260920.md](54_br1_optimization_execution_and_deviations_20260920.md)。
本报告耗时、热点比例、源码行号和同构对照不作为 D1 后证据；新结果只引用 54，不能据旧采样宣称热点仍占相同比例。
D1 的诊断收益不替代同主干 M 不劣性、真实写 K/resident E、尾延迟或 GPU/UMA 验收。

## 1. 结论与证据等级

- 已测事实：8 worker × 10000 cycles、固定 seed 的主 stress 中，generic write request 为 **0**，default
  materialization 为 **1,260,800** 次，同步整页 adoption 为 **1,499,968** 次。
- 操作计时：history、clear-all、setExtent 的互斥执行体共 **20.644 s**，占该次 Qt 总时长 **26.280 s** 的约 **78.6%**。
- 调用结构：同 seed、全程 1/5 ms 采样均将 default 物化排在首位，约占非等待 worker 栈的 **28.5–29.8%**；
  其后是其他 commit 约 20.6–21.2%、整页 adoption 约 12.2–12.5%、history GC/release 约 10.8–11.4%。
- 源码事实：删除时仍为 default generation 申请物理页；canonical history delta 后仍全量重建 tiles3 index；
  transaction start 仍为取得 epoch id 导出完整 snapshot；删除 extent 仍全量扫描。
- 尚未证明：真实像素修改成本、各个修复能独立消除多少耗时、最终能达到 upstream 几倍，以及 GPU/UMA 产品性能。
  这些不能从 no-op/整页结构型 stress 外推。

数据原件、统计脚本和图表位于 [evidence/br1_perf_20260920](../../../evidence/br1_perf_20260920)。
`analysis.json` 保存互斥分类计数、API 分布、copy 祖先链和操作/阶段 wall、thread CPU 结果。

## 2. 原始测试实际覆盖了什么

`KisStressJob` 源码位于 `krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp`。保留其 12 个分支和原有锁语义，
仅在测试端加计时及固定 seed 的可选入口。

| 分支 | 实际工作 | 不能据此证明 |
|---|---|---|
| 0 | 设置相同 default pixel | default revision 真实变化性能 |
| 1/2 | read lock、write lock/unlock、old read；未访问 writable data | mutable pointer、真实 first-write/COW 吞吐 |
| 3/9 | extent/hasMemento 查询 | epoch commit 或边界删除复杂度 |
| 4 | 512×512、1 BPP、页对齐 uniform fill | 4/8/16 BPP brush、SIMD 混合、partial-page 写 |
| 5 | readBytes 后原样 writeBytes | 内容发生变化的 writeBytes 性能 |
| 6 | 构造 1 BPP 源 manager，并整页 bitBlt | 非对齐 copy、混合 kernel；该分支还包含源构造/析构 |
| 7/8 | begin → 整页 fill → commit → undo → redo → purge | 任意画笔 transaction 的性能 |
| 10/11 | clear-all、按页对齐 setExtent，频繁删除其他 worker 页 | 纯并行独立像素写的扩展性 |

`stressTestLazyCopying` 重复同一 uniform clear、未暴露 writable pointer 的锁，以及 current/old read。
当前的 no-op suppression 和 alias 对该 workload 很有效，达标证明的是这些路径；不能把名称里的 copying 当成
“持续修改数据的 COW”证据。其 `isWriter` 特殊分支还被 `&& 0` 禁用，不能据名称推断读写比例。

两个原始 stress 都使用 1 BPP，与产品常见 4/8/16 BPP pool、色彩格式、SIMD brush 不同。原始随机 seed 来自毫秒时间，
不同 worker 还可能拿到同 seed。因此旧的单次 144.530→25.841 秒只是性能趋势，不能分解为各次提交的因果收益。
此前还并发执行过 stress/lazy 的计时，且部分比较混用 Qt 与进程 real；这些不能用作正式配对验收。

## 3. 本轮测量设计与结果

环境：Mac16,10 / arm64、10 physical cores、24 GiB RAM、macOS 15.7.3；Qt 6.8.0；RelWithDebInfo `-O2 -g -DNDEBUG`，
universal x86_64/arm64 binary 实际运行 arm64，`LIMIT_LONG_TESTS=ON`，Vulkan foundation/UI adapter 均关闭。
工作树 base 为 `f5fbbde618df6fb4e1068ace7381c339a70dd4c0` 加现有未提交改动；upstream 对照源码为
`9a24ae0d8c070884fb013594191002e1a1b39a19`。最终诊断二进制和库 hash 见本节末。

### 3.1 分开采集的三种量

1. 原测试总墙钟：Qt test elapsed；进程 real/user/sys 单独保存，不交叉取比。
2. 测试端计时：外层 stress lock 等待、每个 operation body wall/当前线程 CPU、history 内部 API 阶段。
   时钟/统计只在 `KIS_BR1_PROFILE=1` 开启，无 production 埋点。统计在 worker 本地累积，结束后才输出 JSON。
3. macOS `sample`：分离 test-level lock wait、product API 内等待和非等待 worker 栈；排除主线程 waitForDone、
   watchdog、swapper 空闲线程。解析器用 `self = inclusive - sum(children)` 做叶归因，检查节点和总数守恒。

**stack occupancy 不等于 CPU time；thread CPU 和并发 body wall 的和也不等于进程 wall。** 所有图明确标注分母。
结构分类按祖先路径互斥分配，default materialization、GC、prune、rebuild 等已经从 commit 等父路径扣除。
分类依赖可见调用栈和符号，内联/展开质量会影响细分归属；它定位路径，不证明该路径全部可以消除。
短阶段的两个时钟读取端点不同，读时钟本身也有成本；微小阶段出现 CPU 略高于 wall 不应解释为物理上的加速。

### 3.2 原测试固定 seed 的重复与扰动检查

固定 base seed `12345`，worker seed 为 `base + workerIndex * 0x9e3779b9`。只固定每 worker 事件流，不固定交错。
所有性能进程顺序运行，没有相互并发竞争；没有为本轮诊断宣称稳定 P95/P99 或通过最终 5-run 门禁。

| 配置 | Qt elapsed | 说明 |
|---|---:|---|
| 无计时埋点 plain-01 / plain-02 | 26.219 / 26.408 s | 固定 seed，8 worker / 8 thread |
| 埋点 timed-01 / timed-02 / timed-03 | 25.883 / 26.276 / 26.280 s | 波动区间重叠，未检出明显大扰动；不等于证明零开销 |
| 全程 5 ms sample | 27.783 s | profiler 数据不用于性能 pass/fail |
| 全程同 seed 1 ms sample | 27.549 s | profiler 数据不用于性能 pass/fail |
| 8 worker / 1 thread，埋点 | 13.235 s | 调度改变实际 page work，不能据此声称 2× 锁优化空间 |

上游 2.529 s 是此前单次历史结果，本轮未重建/重跑上游二进制。正式差距必须在上游移植相同 diagnostic harness 后
配对重测；stress 完整操作的 1.5× relative gate 保留，3.794 s 仅是旧基线的示意上限。该阶段上限不能证明管理等价，
后续还须通过 39 的 5.6/52 第 7 节新增的 CPU 同义管理不劣性判据；本报告旧采样不构成该项通过证据。

### 3.3 操作与 history 分段

以下来自 `timed-03-counters.log`，body 不包含外层测试锁等待，包含 product 内部等待；单位为秒，跨 worker 累加。

| operation | 次数 | body wall | thread CPU |
|---|---:|---:|---:|
| history（7/8 合并） | 13371 | 8.216 | 8.204 |
| clear-all | 6547 | 6.895 | 6.877 |
| bitBlt + 源生命周期 | 6631 | 6.739 | 4.117 |
| uniform clear | 6535 | 5.717 | 3.269 |
| setExtent | 6744 | 5.533 | 5.525 |
| read→identical write | 6754 | 1.929 | 0.792 |
| set same default | 6600 | 0.705 | 0.115 |
| tile locks（1/2 合并） | 13300 | 0.113 | 0.067 |

![操作执行体 wall 与 thread CPU](../../../evidence/br1_perf_20260920/operations.svg.png)

history 阶段：commit 2.864 s、clear 1.687 s、rollback 1.252 s、rollforward 1.196 s、purge 1.178 s、begin 0.010 s。
这些 API 计时已经包含子调用，不能再与 operation history 的 8.216 s 相加。

![history 分阶段耗时](../../../evidence/br1_perf_20260920/history.svg.png)

全部 operation 的 thread CPU 累计约 28.971 s；外层 stress lock wait 累计约 172.585 worker-seconds。
后者由多个被阻塞 worker 重叠贡献，不是 172 秒可回收的进程耗时。history/clear-all/setExtent 在测试中互斥，
这三类 body 的 20.644 s 可以作为进程关键路径的保守组成部分，其余并发 body 不可直接加到墙钟上。

### 3.4 采样结构与粒度复核

同 seed 全程 1 ms：186312 worker 样本；5 ms：33392 worker 样本。两轮均包含约 82.4–82.6% test scheduling/lock wait、
约 4.0–4.1% product API 内等待、约 13.0% 非等待执行栈。未固定 seed 的第一轮 10 秒采样只作探索，不作为同粒度 A/B。

| 互斥结构分类（只以非等待 worker 栈为分母） | 1 ms | 5 ms |
|---|---:|---:|
| default-page materialization | 28.52% | 29.81% |
| 其他 canonical commit | 21.24% | 20.56% |
| synchronous whole-tile adoption | 12.24% | 12.52% |
| history GC / snapshot release | 10.76% | 11.41% |
| canonical history restore | 4.47% | 4.06% |
| history default-page prune | 4.42% | 4.13% |
| adapter index rebuild（含子工作） | 3.69% | 3.43% |
| generic read/native refresh | 2.65% | 2.54% |
| derive extent | 1.16% | 1.24% |
| 其他 | 10.86% | 10.30% |

![非等待调用结构](../../../evidence/br1_perf_20260920/sample-seeded-1ms-structure.svg.png)

这两轮的主要排序稳定，支持先用 5 ms 长窗口定位宏观热点；当前没有依据把全程采样加密到微秒。
极短的 pin、lookup、no-op 需在固定批次中重复计时并用 counter 验证；对已锁定的 commit/delete 子路径，再加有限 scope
计时或使用 Time Profiler/线程调度 trace。采样里的 `_platform_memmove` 只有追溯祖先才能区分 default fill、COW、
metadata 容器 detach 和实际像素 copy，不能统一标为 COW。

### 3.5 结构计数及单线程反例

| Counter（目标 dm，不含临时 bitBlt source manager） | 8 threads | 1 thread |
|---|---:|---:|
| generic write request | 0 | 0 |
| default materialization | 1,260,800 | 333,120 |
| synchronous adoption | 1,499,968 | 1,189,440 |
| generic read request | 1,052,201 | 1,298,505 |
| committed transaction | 23,965 | 23,780 |
| 最终 registered pages / versions / replicas | 512 / 512 / 512 | 512 / 512 / 512 |

相同 80000 操作类型流，1 thread 时 setExtent 执行体只有约 3.36 ms，8 threads 却为 5.53 s：并发 worker 让共享文档
同时存在其他矩形的页面，trim 删除量完全不同。正确的 scaling 实验需要固定页集与 K/N，分开测无全局破坏操作的独立页
并发，不能把这个混合 stress 的 1→8 thread 比值直接归因为锁。

最终测试二进制 SHA256：`0a6d8795e8f0504d3ce695b23a99898fe0e7f4d86f0f783bde4319e850cc3b7c`。
product `libkritaimage` SHA256：`9a068ab0530ed8e44115f0726c03bf977e6eb019a63f9e00760a61067596d81f`。
本轮 production 库仅重编译此前的注释变动，性能实现没有新增修改；timed-01/02 在加入结束时 counter 输出前采集。

## 4. 采样检查点实现是否与主干同构

**物理存储复用了主干，完整执行路径没有同构。** 当前是 CPU-only 的 PageStore/tiles3 混合接入，没有 GPU 仿真参与。

| 层/操作 | 主干 | 当前 BR1 | 判断 |
|---|---|---|---|
| payload/pool/swap | KisTileData / Store / pooler | 同一套 native CPU 对象，经 provider 持有 | 底层复用 |
| resident read | tile-local nested pin + swap block | native read cache + 桥接失配时 generic request | 部分同构 |
| 真正可写 pointer | usersCount 条件 COW，局部写 | PageStore reserve/allocate/transfer/publish/commit | 另一执行路径，尚待真实写基准 |
| full-tile fill/clone | 共享 backing、后写再 COW | 共享 backing + adoption/proof/epoch，额外内容比较 | 算法部分复用，控制成本不同 |
| default clear/remove | 删除稀疏映射；历史保留旧 backing | stage removal → ensureDefaultPageLocked → allocation/fill → restore/commit/retire | 明显不同构 |
| undo/redo | changed-tile 历史链更新索引；主干仍会 recalculateExtent | canonical retained root/delta + adapter clear/rebuild 全部 wrapper | 底层 delta 未贯通适配层 |
| epoch root | 无同等跨域 immutable epoch 层 | persistent tree + owning snapshot 导出调用残留 | 新增实现/协议层，不能宣称与主干完全相同；不自动取得 additional semantics 成本豁免 |

上表的结构差异不能作为性能成本分类的捷径：实现共同操作所需的 root/generation/proof/adapter 仍按 M 与完整 E
验收；只有确实新增的对外契约才按 39 的 5.6 单列语义预算。此为口径校正，不更新本节历史版本的计时或源码行号。

关键代码（路径相对 `krita/`）：

- `libs/image/pagestore/KisPageStore.cpp:2754`：removedPages 仍调用 `ensureDefaultPageLocked()`；同文件 393 开始执行物化。
- `libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:119`：无 seed 时 `createDefaultTileData()`。
- `libs/image/tiles3/kis_tile_data.cc:109`：每 tile 4096 个 pixel fill；采样中的大量 copy 落于此处。
- `libs/image/tiles3/kis_tiled_data_manager.cc:243,266,726`：undo/redo 后全量 rebuild；不仅更新 changed pages。
- `libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:623`：只为 epoch id 导出 snapshot；760/1429：删除 extent 与 allocatedPages 导出/遍历。

所以在该采样检查点，“QVector 已退出生产热路径”“history 已端到端 O(K)”“default 生命周期已零物化”均不成立。
独立 production owner 的重命名本身不会提速；必须同时移除 owning export、冗余每页 transition/拷贝和 adapter 全量工作。

## 5. 优化空间及修订顺序

当前仍有明确可优化空间，但不能把统计占比直接许诺为墙钟收益：仅将约 30% 的路径消除，在理想串行 Amdahl 模型里
也只有约 `1/(1-0.30)=1.43×`，不足以填补 10× 差距。实际还含锁竞争/任务变化，必须逐项配对测量。
若暂用历史 gate 3.794 s，从当前约 26.3 s 到该线需要约 85.6% 的总成本下降；不能靠一次 memset 优化或 root 改名结清。

1. **删除/default 生命周期**：让删除直接提交 virtual default/sparse absence；retained old version 只保留真实必要的旧
   identity/backing。禁止为每次删除重新分配填充 default payload；同时核对重复删除/trim、default revision 与 undo。
   provider 共享 immutable default 可作为受约束过渡，但不能掩盖每坐标 metadata 的长期累积。
2. **每页 commit/adoption/history 成本**：测量 prepare、proof 验证、preflight、apply、retire 的次数/字节与 self 时间；
   用 owner-held page record、批量 transition 或 compact metadata 降低重复 snapshot/vector detach。保留全部安全不变量，
   不以关闭校验达标。history 中的 default prune 也应利用可信 dirtiness/uniform metadata 避免重复 generic read。
3. **索引与 root 边界**：delta 贯穿 rollback/redo 的 adapter；transaction 起点只取 root/id；删除 extent 用轴/空间增量
   索引；snapshot export 仅显式 cold consumer。K 固定、N 扩大要测完整产品操作，不只 tree commit。
4. **真实写单独推进**：补 4/8/16 BPP 实际修改、partial/full page、同页重复写、no history/reader/memento/save、
   1/2/4/8 threads 的固定 page work；再按数据实现 `CpuMutationSession`、pending generation 复用、原位 permit 与 guard。
   同时补 identical/changed write 分桶，确认目前额外 memcmp 在高变化率 workload 中不会适得其反。
5. **全量产品和 GPU/UMA**：真实 iterator/brush/transaction/save 与 W0–W8 端到端验收。CPU 先恢复成熟产品性能；GPU/UMA
   继续以相同 workload 的实际 CPU 为分母，弱 GPU 自动路由约束见 39，不能用此 no-op stress 给 GPU 授予加速资格。

每项完成后重新采样、重排优先级；计划中的 API 是语义与安全要求，瓶颈顺序必须由当前 workload 证据决定。
切片后的证据更新、采样粒度选择与成本转移检查统一遵循 39 的 5.10；实施/偏差状态以 54 为准。

## 6. 复现与后续验收纪律

从仓库根目录执行（所有性能进程依次运行）：

```sh
.venv/bin/cmake --build krita/_build-br0-cpu --target kis_tiled_data_manager_test -j8
KIS_BR1_SEED=12345 krita/_build-br0-cpu/bin/kis_tiled_data_manager_test stressTest
KIS_BR1_SEED=12345 KIS_BR1_PROFILE=1 krita/_build-br0-cpu/bin/kis_tiled_data_manager_test stressTest
KIS_BR1_SEED=12345 KIS_BR1_PROFILE=1 KIS_BR1_THREADS=1 krita/_build-br0-cpu/bin/kis_tiled_data_manager_test stressTest
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_perf_20260920/analyze.py docs/vulkan_gpu_design/evidence/br1_perf_20260920
```

采样在另一次同 seed 测试进程启动时执行 `/usr/bin/sample <pid> 30 1 -mayDie -file <output>`，5 ms 对照只替换 interval。
对运行时间较短的进程先读取符号（`-mayDie`），确保保存的 binary/source hash 与采样地址一致。最初探索用 10 秒/未固定 seed
的 `sample-1ms.txt` 保留为原始证据，正式同 seed 对照是 `sample-seeded-1ms.txt` 与 `sample-5ms.txt`。

- 原始 stress、同 seed 诊断、真实写补充测试和固定 page-work scaling 各自标识，不能相互替代。
- 正式结果至少 5 个独立 run，报告 median/range/方差；尾分位数使用足量事件和 replay，记录样本量/置信范围。
- 冷/热分开，固定 build/ISA/格式/页尺寸/seed/操作端点；UI 与业务负载不得和 benchmark 并发。
- profiling 结果只用于归因；最终门禁以关闭 profiler 的配对计时与像素/extent/history 等价为准。
- 本轮 stress 各诊断运行均 3/3 通过；诊断解析器检查每次 80000 个操作及采样树计数守恒。未声称新的全量 CPU/OpenGL
  或 BR1-PERF 结清，既有正确性证据保持其原始适用范围。
