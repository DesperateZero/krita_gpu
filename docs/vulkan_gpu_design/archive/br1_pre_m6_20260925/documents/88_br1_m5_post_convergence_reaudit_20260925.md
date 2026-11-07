> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1/M5 收敛后复审（2026-09-25）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

> 后续修复：本文发现已由 `6ac53223ef`、`095193d11a` 关闭；最终代码现实、验证和 M5 裁决见 [89](89_br1_m5_reaudit_findings_resolution_20260925.md)。本文保留发现发生时的反例与重开判断，不作为当前状态。

**结论：主写入管线已经实质收敛，但目前 M5 仍不足以按 86 的标准称为“足够干净”。应重开资源验收和少量实现清理，撤回 87 的整体关闭判断。**

本次以当前 Krita 源码 `a0400cf0f7484004dd520e5c03dbc71cbe6827b4` 为准，复核 [85](85_br1_m5_code_readiness_audit_20260924.md) 的问题及 [86](86_br1_m5_final_convergence_plan_20260925.md) 的退出条件。
没有修改生产源码。87 中的既有测试结果仍有效，但不足以推出其较强的资源与清洁度结论。本文是后续复审结论，不抹除原始实验记录。

## 1. 四个问题的当前答案

| 问题 | 当前判断 | 依据与限制 |
|---|---|---|
| 重构后的管线是否正确、清晰 | 写入、overlay、root、退休的主责任链基本清楚；资源闭环仍不正确 | 本轮未复现新的像素可见性或 overlay 发布错误；复现了全局 RAM 超限和元数据漏计费 |
| 实现是否精练、可靠，是否重复造轮子或存在复数权威 | 比 85 明显收敛；关键发布算法已合并，但尚未精练到可关闭 M5 | 未确认 selector、overlay 发布、物理 revision 又出现同一事实的双修改权威；预算管理仍有历史槽位全扫描及无条件诊断原子 |
| 是否存在大量死代码和不必要分支 | 当前证据不支持“大量死代码” | 静态未达不等于死代码；native/generic、current/before、pin/completion 的差异仍有真实契约。没有依据做大面积删除 |
| 其他冗余 | 有局部运行成本和验收资料漂移 | 跨 shard 诊断计数、已释放预约槽位的重复扫描、清单中的失效字段，以及 87 对资源门的过度关闭 |

问题集中在有限资源与尾部管理成本，不需要推翻已经统一的 Fresh 管线，也不应再包一层总控制器。

## 2. 本次确认的问题

### P1-A：每个 Store 的有限额度没有兑现进程 RAM 硬上限

`KisTiledDataManagerPageStoreBackend.cpp:66–103` 为每个 Store 独立推导同一份产品 RAM 限额；provider 与分类 controller 都按各自 Store 管理。
真正分配 tile 的 `kis_tile_data.cc:53–79` 先调用 `checkFreeMemory()`，随后继续 `allocateData()`；
`kis_tile_data_swapper.cpp:94–100` 的检查只是必要时执行一次回收，不能返回准入失败。
`doJob()` 回收不到足够内存后仍可返回，调用者继续分配。这里保留的是历史回收阈值语义，不能直接用来证明 86 所要求的进程硬库存。

通过真实 `KisTiledDataManagerPageStoreBackend::configure/writeBytes` 复现，使用独立应用名和 Qt test-mode 配置：

| 项目 | 结果 |
|---|---:|
| 产品 `tilesHardLimit` | 8,388,608 B（8 MiB） |
| 产品 swap / pool | 0 / 0 |
| Store 1 成功写入后 Current RAM | 6,291,456 B（6 MiB） |
| Store 2 成功写入后 Current RAM | 6,291,456 B（6 MiB） |
| 全局真实 tile payload RAM | 12,582,912 B（12 MiB） |
| 两个 Store close 后 tile payload RAM | 0 |

每个 Store 均低于其上限，但总驻留超过产品 RAM 上限 50%。探针读取的是 `KisTileDataStore::memoryMetric() × 64 × 64`，没有用逻辑页数推算，也没有把调用者输入缓冲或 metadata 加入结果。
不同页使用不同内容；最初的统一颜色 fill 被正确合并为共享 payload，只占两个物理页，其未复现结果也保留。

这不是泄漏反例，而是**容量准入缺失**。86 批次 2A/2C 的多文档实际入口条件应重开；87 不能再把 tiles3 “物理库存权威”这一职责声明当作硬准入已实现的证据。

修复应位于已有进程 allocator/storage 入口，覆盖新增物理 payload 和 swap-in 等真实增长，先预约再分配、失败保留原状态。Store 分类 controller 继续承担自己的职责；同一物理 allocation 不因跨 Store alias 被重复计入进程库存。

证据：[product-probe.cpp](../../../evidence/br1_m5_reaudit_20260925/product-probe.cpp)、[运行输出](../../../evidence/br1_m5_reaudit_20260925/product-probe.log)、[源码与动态库身份](../../../evidence/br1_m5_reaudit_20260925/product-probe-identity.json)。

### P1-B：MetadataArena 仍漏计 owning index 与页目录分配

当前修复确实覆盖了 arena directory、锁外候选 block、安装和析构；但计费边界没有覆盖全部计划要求的 owning 分配：

- `KisPageMetadataIndex_p.h:39–57` 中 `reserveInsertions()` 直接 `QHash::reserve(required)`，其 token 预约的是插入数量，没有向 backing controller 预约实际字节。
- `KisPageMetadataCoordinator.cpp:1432` 附近的 `pages/activities/cpuBindings` 是独立 owning 容器；`registerPage():2556` 的页目录插入没有计费。
- `configure():2488–2511` 的 `actualBytes` 只累计 shard 指针数组和 arena directories，没有包括 shard 对象及上述容器。
- `footprint()` 明确是逻辑 payload 统计、排除 allocator/hash 实现开销，不能作为实际 owning 总预算的替代。

探针通过既有 reference-test friendship 连接真实 MetadataCoordinator 和真实 BudgetController，未修改生产状态或另写计费实现。
将限额固定为单 shard 目录及首个 version/replica block 正好占用的 **73,744 B**：

| 注册页数 | 账本 live / limit | exact / physical index capacity | 额外页头 payload |
|---:|---:|---:|---:|
| 1 | 73,744 / 73,744 B | 64 / 64 | 96 B |
| 64 | 73,744 / 73,744 B | 64 / 64 | 6,144 B |
| 65 | 73,744 / 73,744 B | 128 / 128 | 6,240 B |
| 96 | 73,744 / 73,744 B | 128 / 128 | 9,216 B |

arena 始终只有两个 block。第 65 页扩容两个 owning index，但预算仍显示已占满且 reserved=0；直到第 121 页需要新 arena block 才拒绝。析构后已计费部分归零。
这些页头和 index 不在 arena block 中，因此不能用“已有 block 的余量”解释。这里没有声称已经精确测得 QHash allocator 的总开销；现象足以证明现有账本漏项。

86 批次 2B 明确要求 slot directory/index 实际 owning 分配的计费范围。现有 `metadataArenaBudgetTracksAllocator()` 只验证零预算、directory-only 拒绝首个 block 和成功 block 转 live，未覆盖本反例。
应沿现有容器/allocator 的增长边界补全计费、取消及析构；避免再造独立 metadata 账本。

证据：[probe.cpp](../../../evidence/br1_m5_reaudit_20260925/probe.cpp)、[运行输出](../../../evidence/br1_m5_reaudit_20260925/probe.log)。

### P2-A：每次预算预约重复扫描历史高水位槽位

`KisPageWriteCoordinator.cpp:228–300` 的 `reserveImpl()` 在 budget mutex 下，按每个 budget class 扫描全部 `m_slots`，然后为 durable 再扫一次。
`commitRetaining/release` 只是把已释放槽位放回 free list；`m_slots.size()` 不缩回当前 active 数量。
因此同一个 Store 经历过大批量预约后，即使全部释放，小操作仍为过去高水位付扫描成本。

同一生产 controller、相同 1-byte reserve/release、当前 live/reserved 均为 0，arm64 局部探针结果为：

| 历史同时预约高水位 | reserve/release 每对中位耗时 |
|---:|---:|
| 16 | 133.854 ns |
| 512 | 1,891.44 ns |
| 4096 | 16,555.9 ns |

每组 3 次、每次 2000 对。这里是定位复杂度的探索性微测量，不是预注册 BR1-PERF、产品吞吐或正式回归验收；约 124 倍差异与源码中的全扫描一致。
准确说，它依赖**历史同时预约高水位**，不能未经证明改称当前 N/H 线性增长。

建议在同一 controller 内维护预约 aggregate/durable 合计，所有 reserve、commit、retain、cancel 更新同一统计不变量；槽位继续只承担 token 身份与回收职责。
这是现有权威内部的管理算法收敛，不需要另加一个预算决策者。

### P2-B：诊断关闭态仍写共享原子

87 确实删除了 transition 的无条件 `QElapsedTimer` 和总/最大耗时两个 atomics；但其表格声称“metadata transition 关闭态不再……更新共享原子”过于宽泛。

`KisPageMetadataCoordinator.cpp:1717–1726` 仍定义跨 shard 的 accepted/rejected、prepared/installed 等 metrics；
`:2956` 每次成功 owner transition 无条件 `acceptedTransitions.fetchAndAddRelaxed()`，`:2182`、`:2330` 的准备/安装统计也没有 opt-in gate。
这些指标经 `metrics()` 输出，仓内消费者是测试/诊断，不承担 publication 或 admission 决策。

应区分真正的协议原子，例如用于目录失效判断的 `registeredPages`，与诊断计数。前者保留；后者可在既有 shard 锁下局部累计后冷查询合并，或复用 opt-in recorder。
本次未测得这些 atomics 的产品级性能损失，不给出虚构比例，但 86 批次 6 的关闭态约束尚未完全兑现。

### P2-C：结构门和验收清单不能替代行为证明

当前 architecture gate 通过，但 `runtime-census.json` 的 `backend-writer-admission` 仍引用已不存在的
`KisPageStoreSessionStats.writePageClaimChecks`、`writePageClaimConflicts`。
源码全搜无这两个字段；该 gate 尚未验证清单中的 metric 成员确实存在。审计目录 README 也仍描述已删除的 mutex-protected compatibility census 和早期 R0/R1 状态。

这属于验收资料漂移，不证明生产又有两个 canonical owner。应清除失效条目并补上字段绑定验证，然后再用清单支持关闭判断。

## 3. 已经成立的收敛，不应重复推翻

1. **Selector**：`KisPageWriteCoordinator::select():955` 将 mutable 分为 FreshPayload/FreshDiscard/FreshCow；semantic 输入只判断 ReusePending/SemanticOnly。没有重新引入多套优化选择器。
2. **Overlay**：native `sealImpl():1807/1839` 和 generic `finishWrite():3422/3437` 都调用 PublicationCoordinator 的同一 overlay candidate 准备/安装协议。多页原子 seal 和单 lease completion 的边界差异合理；root commit 另有职责。
3. **Domain**：storage revision、provider journal、owner 分类 ledger 的职责已分离；85 的旧快照覆盖修复有确定性交错测试。该结论不自动包含全局物理容量硬准入。
4. **Compatibility**：tile capability 使用固定槽位，iterator boundary registry 已删除，共享 scope 借用既有 native mutation。anonymous client lifetime、嵌套锁计数、before/current 视图与 pin 的寿命差异仍有实际消费者，不能机械合并。
5. **测试 provider 与 revision**：CPU reference provider 已移入 test support；default revision high-water 已收口到 owner import/reserve，外部不再写可变引用。

在上述核心边界中，本轮没有确认“同一逻辑事实由两个实现独立决策”的新反例。多层 capability、镜像、预算分类并不自动构成双权威；应检查修改权和生命周期，而不是按类名数量判断。

## 4. 死代码与分支裁决

当前冻结图的 1452 个 API 分为：997 production-boundary-reachable、279 indirect-review、133 test-only-review、43 unreached-review。
后三类是候选，不是已证实死代码数量。

具体反例：图把 `PreparedPublication::backingAuthority` 列为 unreached-review，源码 `KisPagePublicationCoordinator.cpp:38–39` 却在模板 helper 中实际调用它。
这说明模板可达性的人工复核仍必要，不能按 43 或 455 批量删除。

因此本轮结论是：**没有证据支持仍存在大量死代码；也没有完成零死代码证明。**
保留的 native/generic、同步 pin/异步 completion、成功/失败/尚未开始的 fallback、current/before 以及单页/多页分支大部分有明确契约。
真正应优先删除的是上文已定位的重复扫描、诊断热成本和失效资料，不是再压缩有行为差异的边界。

## 5. 验证范围与 M5 裁决

本轮在生产 tracked source 干净的同一提交上执行：

- Ninja dry-run：CPU Mutation / Reference 两目标无待构建工作。
- arm64 CPU Mutation：577 passed，0 failed，0 skipped。
- arm64 Reference：297 passed，0 failed，0 skipped。
- architecture gate：21 manifest entries、21 ownership facts、16 census groups、1452 APIs、13654 reverse-call edges、19 frozen external files，通过。
- reachability 工具自测：6/6。
- 两个独立源码探针：元数据漏项/历史槽位扫描；真实 backend 多 Store 物理超限。

原最终双架构矩阵及 selector v2 gate 没有被本轮推翻，也没有被重复计作本轮新执行。selector 两桶通过不能覆盖 budget controller 的历史高水位场景。
TSAN 仍为 Inconclusive：既有报告有告警，混合插桩可能存在同步建模缺口，但本轮没有完成 Qt 同步最小复现或全工具链 race-free 证明。
不把“Qt 未插桩”直接当作全部告警已经解释，也不把该日志单独认定为已证实生产竞态。

| 86 批次/门 | 本轮状态 |
|---|---|
| 1：domain 版本协议 | 保留已完成结论 |
| 2A/2C：产品有限预算、多 Store 实际路径 | 重开：进程物理 RAM 上限有实际反例 |
| 2B：MetadataArena owning 分配 | 重开：index、页目录等漏计费 |
| 3：物理域转换事前准入 | Store 分类转换已有实现；不能再外推为全部进程物理增长已受控 |
| 4：overlay 编排 | 保留共同实现已收敛结论 |
| 5：compatibility | 保留本轮检查到的必要边界；未发现需要重建第二套协议 |
| 6：冗余与口径 | 部分：共享诊断原子、槽位全扫描和失效审计字段待收口 |
| 7：M5 整体验收 | 重开；已有通过实验保留 |

后续顺序：先关闭两个 P1 的实际资源反例；再收敛同一 controller 的预约统计与诊断热成本；修复清单绑定；最后在同一源码上补多 Store/紧预算/高水位后小操作及退出测试并重做受影响的性能门。
不能只通过修改 86 的措辞把硬容量降格为软回收阈值。若要改变产品契约，应作为独立、明确的设计变更，而不是计作原计划已完成。

**当前可作为继续修复和收敛的基础；尚不能作为“足够干净、M5 已关闭”的稳定前置。**

完整记录位于 [本轮证据目录](../../../evidence/br1_m5_reaudit_20260925/README.md)。
