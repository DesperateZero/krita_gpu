> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1/M5 基线冻结复核与历史归档裁决（2026-09-25）

**结论：当前 M5 尚不足以冻结为 M6 前置基线。历史调优记录可以归档；M5 关闭、M6 放行及完整 BR1 完成均不能由归档动作授予。** 本次在 89 所验收的同一生产提交上复现了默认像素状态分裂和构造后 clone 崩溃，并确认 index capacity reservation 不保证 install 零分配。因此撤回 89 的整体关闭判断，重开具体失败契约及 M4 分配保证，保留其已通过实验与已完成结构收敛。

生产代码为 `krita@095193d11a1041c31ba92f218ccaea4a8d4f396f`；前轮外层证据提交为 `d44c732`。复现时 tracked source 干净，CPU 库、测试二进制、编译数据库及源码清单哈希均与 89 的 `correctness-final/identity.json` 相符。本轮只新增审计探针、证据与文档；没有修复以下生产缺陷。当前状态入口为本文；后续条件顺序见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)，文档角色见 [目录](../../../README.md)。

内层后续文档提交 `875c3854d6` 只更新 `pagestore-audit/README.md`；相对上述生产检查点没有 C++、测试、清单或构建规则变化，不能将该提交写成问题已修复。

## 1. 四项判断

| 问题 | 判断 | 已成立与未成立的边界 |
|---|---|---|
| 管线逻辑是否正确清晰 | 主责任链清晰，失败闭环仍不完整 | Admission → private write → overlay → root → retirement 仍能对应唯一 owner；但真实 manager 在内存压力下出现部分更新和无效构造。不能把核心 backend 测试覆盖外推为全部业务入口可靠。 |
| 是否精练可靠、是否有重复轮子或复数权威 | 核心决策已经收敛，兼容投影仍有一致性缺口 | selector、metadata 状态转移、overlay 编排和 root 安装没有发现第二份独立决策；`m_defaultPixel`/默认 TileData 是有消费者的兼容表示，但失败时与 canonical default 分裂。只写“canonical”标签不足以证明投影同步。 |
| 是否存在大量死代码和不必要分支 | 没有证据支持大量存在，也未完成零死代码证明 | 当前 1,461 个 indexed API：1,003 production-boundary、282 indirect-review、133 test-only-review、43 unreached-review。后三类不得相加为死函数数；其他配置、模板/虚调用和必要失败/回收分支仍须逐项判断。 |
| 其他冗余与脆弱点 | 热路径的已知历史槽位扫描/共享诊断原子已修复；仍有契约与验收资料问题 | QHash capacity token 被当成零分配能力；历史文档中的多份“当前状态”互相覆盖；audit README 仍描述已删除的 compatibility census、旧 split 和 R0/R1 顺序。 |

可以继续作为修复检查点；**不能以“足够纯净”冻结为新能力的可信前置**。这里不要求零适配器、零分支或所有静态候选全部删除。

## 2. 阻塞发现

### M5-R1 / P1：默认像素先发布，compatibility 分配失败后不回滚

[setDefaultPixel](../../../../../krita/libs/image/tiles3/kis_tiled_data_manager.cc:302) 先调用 backend 更新 canonical surface default，再调用 `setDefaultPixelImpl()`。后者在 [315 行](../../../../../krita/libs/image/tiles3/kis_tiled_data_manager.cc:315) 分配默认 tile；本轮硬准入使它可以正常返回 null，此时直接退出，`m_defaultPixel`、hash table default 和 memento default 均保留旧值。canonical 更新已生效。

独立 Qt test-mode 配置：8 MiB resident、swap=0、pool=0。一个真实 `KisTiledDataManager` 加 511 个真实 storage allocation 填满 8 MiB。调用 `manager.setDefaultPixel({0x31,0x42,0x53,0x64})`，随后释放填充资源以允许正常读取：

```text
limit=8388608 resident=8388608 filler_count=511
manager_default_retains_old=1
canonical_read_has_new_default=1 default_read_diverged=1 bytes=49,66,83,100
```

该复现只调用公开 manager/storage API，没有改写其 private 状态。结果说明同一对象的 `defaultPixel()` 与 `readBytes()` 已不一致；后续 history 接口还把 `m_defaultPixel` 传入 begin/commit。undo/redo 在先 restore canonical 再调用同一 helper 时也有相同静态失败边界，本次未另行声称已复现 undo 数据损坏。

修复条件：默认值、必要 default backing/compatibility 索引和 canonical publication 共用一次可失败准备、一次一致安装；prepare 拒绝应完整保留旧值。测试必须覆盖 setDefault、undo/redo、clone、clear/default 消费及释放资源后的重试，不能只在 void helper 中吞掉 null。

### M5-R2 / P1：满预算构造返回无效 manager，随后 clone 崩溃

[构造函数](../../../../../krita/libs/image/tiles3/kis_tiled_data_manager.cc:86) 分配未初始化的 `m_defaultPixel` 后调用 void `setDefaultPixel()`，无法察觉默认 tile 初始化失败，仍继续 configure backend 并返回。hash table 的 default tile 因此为空。

相同 8 MiB 满预算条件下，再构造一个 manager，构造函数成功返回；调用它的复制构造函数时，`refAndFetchDefaultTileData()` 对空 default tile 执行 `ref()`：

```text
limit=8388608 resident=8388608 filler_count=511
saturated_constructor_returned=1
process returncode=-11
```

LLDB 确认 EXC_BAD_ACCESS，地址 `0x44`，位于空 TileData 的 atomic ref 操作。证据包含原始进程日志与调试栈。这是受预算拒绝触发的真实无效对象，不是操作系统物理 OOM。

修复条件：明确 manager 构造失败契约，不能返回默认指针为空、默认字节未初始化但看似可用的对象。覆盖满限额、多 manager、0/不足一页配置、复制与销毁；若使用可失败 factory、已有错误边界或受预算的共享 default，必须审计实际调用者并保持全生命周期一致，不能通过预算外兜底绕过原硬上限。

### M4-R1 / P1：QHash reserve 不能保证 reserved install 无堆分配

[prepareCapacity](../../../../../krita/libs/image/pagestore/KisPageMetadataIndex_p.h:49) 只调用 `QHash::reserve()`；[insertReserved](../../../../../krita/libs/image/pagestore/KisPageMetadataIndex_p.h:81) 仍调用 `QHash::insert()`。本机已绑定的 Qt 6.8 实现采用 span，`reserve()` 预留 bucket；span 的 node storage 在 `Span::insert()` → `addStorage()` 才按需 `new Entry[]`。

对生产 `KisShardSlotIndex<KisPageVersion, KisVersionSlotId>` 模板直接实例化，成功 prepare 64 容量和 64 个 token 后，仅在 `insertReserved()` 区间统计 `operator new/new[]`：

```text
reserved_insertions=64 capacity_before=64 capacity_after=64 successful=1
insert_heap_allocations=2 insert_heap_bytes=5120
```

capacity 没增长仍发生分配。生产 [metadata install](../../../../../krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2495) 经 `installPreparedAdditionsReserved()` → `putReserved()` 调用相同 index 插入；`putReserved()` 在插入前已经编辑 arena record/链。这与 [68 §12](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md#12-性能模型预测与验收预算) 的 install allocator=0 及 [81](81_br1_r2_m4_allocation_free_publication_20260922.md) 的 M4 完成结论矛盾。

证据范围：这是精确生产模板的动态反例，加真实 install 调用链的静态核对；不是完整 publication 的全 allocator trace，也未注入并宣称已经观察到生产 OOM 半提交。它足以否定 capacity token 本身具备 no-allocation 保证，不能据此进入首字节后不可失败的 M7。

修复条件：在现有 shard index owner 内把实际 node/slot 存储准备完成，install 只消费已经存在的物理存储；或使用与已冻结 slot-arena/index 设计一致的真正无分配索引。验证普通插入、span/tier 边界、prepare 并存、cancel/retry、publication additions/restore，并在真实 install 区间统计 allocator/rehash/大对象析构及注入 prepare 失败。只测 `capacity()` 不够。

## 3. 保留的通过结论及验证范围

- 89 的进程 resident 硬拒绝、metadata owning 容量计费、预约 O(1)、诊断 shard-local 化及失败 mutation 终结修复保留。本次未发现理由恢复旧算法。
- 7 套 PageStore/Completion、Painter、tile data store、tiled manager 双架构合计 2,952 passed，以及 Vulkan foundation 双架构各 14 passed，继续作为该提交的已有证据；本次没有将它们计为新运行。
- 前轮 416 个证据 artifact 哈希全部匹配，CPU 构建身份无漂移；本轮新执行 architecture gate 与六项工具自测通过，Reference/manager Ninja dry-run 无待构建工作。门禁通过仍未发现上面三个反例，说明需要行为/allocator 覆盖补强。
- 本轮新探针在 arm64 上运行：默认 update 分裂、默认构造/clone 崩溃、slot index 插入分配。探针源、完整编译/链接参数、库/二进制哈希及原始输出见 [证据目录](../../../evidence/br1_m5_baseline_review_20260925/README.md)。index 探针第一次编译缺少 arena id 头，补 include 后成功；不计为生产编译失败。
- selector 两次失败 candidate 与最终采用 control 的机器码比较保留。它只覆盖 selector 差异，不能覆盖默认页压力失败、index install allocation 或正式 BR1-PERF。
- TSAN 仍为 Inconclusive；不替代确定性交错，不把混合插桩直接解释成没有竞态。本次 M5 重开的依据是确定性反例，并非把 TSAN 增设为退出条件。

## 4. 归档裁决与状态更新

历史文档按 [归档索引](../../br1_tuning_20260925/README.md) 原位归档：保留路径、原正文及证据链接，新增明确的历史标识，退出“当前执行入口”。失败数据、85/88 的反例、89 的修复和被撤回结论全部保留。

仍生效的规则是 00/22/31 的全局边界、25/33 的语义、39/52 的性能门、68 的写侧设计、69 的清理规则、86 的 M5 退出定义。归档不能删除或降低这些要求。00 的冗长调优时序移入归档快照，当前状态压缩为可核验表；68/69、31/52、86 和 audit README 统一指向本文。

| 事项 | 当前状态 |
|---|---|
| 调优历史与中间审计文档 | 已原位归档，证据保留 |
| 核心 Fresh 管线的结构收敛 | 保留已完成范围 |
| M4 install 零分配保证 | 重开：M4-R1 |
| M5 资源失败语义/业务兼容 | 重开：M5-R1、M5-R2 |
| M5 作为 M6 前置基线 | **未通过，不能标为 ready** |
| M6 → M7 → M8 → BR1-PERF 路线 | 已整理，条件计划，尚未开始新能力实施 |
| BR1 整体 | BR1-PERF 未通过；BR2 production 接线仍不开放 |

关闭顺序为：三个反例修复 → 对应回归/真实 allocator 证据 → 同源码双架构矩阵与受影响性能门 → 新基线身份冻结 → M6。详细检查表在 91；本次不创建暗示验收通过的 M5-ready 标签。
