> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 Canonical PageStore 功能/正确性结清记录（2026-09-19）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

本文记录 2026-09-19 的 BR1 功能/正确性 cutover 证据，覆盖 46–50 文档中对应的“进行中/尚未 cutover”描述；
46–50 仍作为接口演进历史保留。它不再是 BR1 整体最终出口：2026-09-20 的 upstream 差分审计发现 resident CPU
热路径、稀疏 default 和 epoch 生产布局未达性能门禁，BR1 已以 **BR1-PERF** 重开。当前执行状态以
[31_p0_reset_and_execution_sequence.md](../../../31_p0_reset_and_execution_sequence.md) 为准，优化计划与最终门禁见
[52_br1_cpu_fast_path_optimization_plan_20260920.md](52_br1_cpu_fast_path_optimization_plan_20260920.md)。

## 1. 结论与边界

BR1 的功能/正确性 cutover 已结清：`KisTiledDataManager` 的 canonical 页面身份、generation、事务可见性、CPU
lease、COW/oldData、memento、default pixel、extent、clear/copy/clone/purge 与关闭审计统一由 `KisPageStore`
管理。legacy tiles3 类和 iterator ABI 继续作为兼容外壳，但不再维护第二套 canonical generation 或双写像素。

BR1 整体尚未结清。这里通过的测试证明像素与状态机语义，不证明当前每次 tile lock 采用的通用 lease 调用粒度、
default materialization 或 reference manifest 容器适合 production CPU 热路径。

本结论不提前完成后续阶段：

- Vulkan replica 仍不能持有 canonical 文档 authority；产品 Vulkan 入口继续关闭；
- queue submit/bind/present、timeline DAG 与 resource retirement owner 属于 BR2；
- UMA/dGPU 与 durable SSD segment/index/checksum recovery/cleaner 属于 BR3；
- EvalGraph、GPU stroke、compositor、display/WSI 分别按 BR4–BR6 推进。

## 2. C1–C5 出口对照

### C1：CPU accessor lease bridge

- `KisTile` 的 read/write lock 通过 `KisTilePageStoreBridge` 获取 move-only PageStore lease；random、sequential、hline、vline 继续使用既有 ABI，但裸指针只在匹配 lease 生命周期内成为 canonical access。
- 嵌套 read/write lock 复用同一 tile lease；read→write upgrade 保留必要 lease，并在最终 unlock 先释放 read、再发布 write，使已被替代的 prepared generation 可立即回收。
- 多 tile legacy 操作使用不透明 RAII write-batch token；匿名事务的 begin/finish/abort 客户端计数不再暴露给调用方。
- 同一数据管理器上的并发短写可加入同一匿名事务，最后一个 client 负责原子 commit；整设备 clear 是 capability barrier，会先撤销遗留匿名写 lease，再进入新的可见顺序；被 barrier 撤销的 lease 允许调用方幂等 finish，不产生伪失败。
- transaction read view 的选择与 read lease 获取处于同一发布互斥区；调用方不能取得一个可在锁外失效的临时 overlay 标识，最后 writer 也会在 publish 前停止暴露该 overlay。
- 同一 PageKey 的产品写由 backend reservation 串行化，不同 PageKey 仍可并发；隐式 default materialization 对相同 PageKey 合并等待，避免竞争写和重复 authority。

### C2：COW、memento 与产品语义

- `KisPageStoreMementoManager` 持有 before/after retained root；rollback/rollforward 创建单调新 epoch 并选择历史 generation，不复制或倒退 identity。
- `KisTiledDataManager` 的 default pixel、extent、clear、partial clear、trim、copy、oldData、clone、undo/redo 与 purge 已接到 PageStore authority。
- 同一事务允许 write→remove 和 remove/clear→write；后者强制从 surface default 初始化，禁止旧内容回流。history commit 会把全默认 prepared page 稀疏化，同时保留 legacy partial-clear 不立即收缩 tile extent 的行为。
- clone 直接从源 PageStore 的 committed/transaction-overlay 精确版本取 canonical tile，不再从可能惰性未刷新的 legacy hash cache 取种子。
- save/reopen checkpoint 覆盖宽像素格式、稀疏默认页和精确 manifest；跨色彩空间 frame copy、clone/COW 与 functional history 用例通过。

### C3：现有 swap seam

- `KisTiles3PageReplicaProvider` 复用 `KisTileDataStore` backing 和既有 swap 能力，replica handle 带 provider epoch、allocation generation、PageVersion 与 layout；retire/reuse 拒绝 stale/ABA capability。
- `KisSwappedDataStore`、chunk allocator 与 tile swap 路径保留在既有 tiles3 owner 内，没有建立平行 GPU/SSD tile store。
- BR1 只冻结 exact-generation provider/失败边界；durable append segment、原子索引、checksum recovery 与 cleaner 明确留在 BR3。

### C4：异步、取消与关闭

- completion registry、pending operation、archive poll/cancel、last-use acknowledgement、authority handoff 和 `Begin/Complete/FailRetire` 共享同一 typed identity/transition 语义。
- provider 热调用采用“锁内预留 capability → 锁外执行 → 锁内精确复验”；close/abort 由 preparing/resolving、active provider call、lease、snapshot、proof 与 archive 统计 fail closed。
- `sessionStats()` 暴露 transaction/request/lease/proof/archive、page version、replica 与 tracked metadata bytes；`closeSession()` 只有在 capability 清零并退休 replica 后成功。

### C5：cutover gate

- 分片 metadata 压力：256 pages、8 threads、每页 100 次 acquire/release；平均 decision 小于 250 µs、最大值小于 250 ms、墙钟小于 10 s、tracked metadata 不超过 1536 bytes/page。
- 产品并发写及发布期间的持续读、匿名事务重叠 lease、历史 64 次 commit/undo/redo/purge、异步 archive failure/cancel、provider failure/retry、stale completion/provider epoch/allocation ABA 均有自动测试。
- 历史 GC 在 retained root/lease 释放后通过 `DiscardHistoricalVersions` 退休不可达 replica；64 次历史循环后保持 1 page version、1 replica、0 outstanding capability。
- 同一事务反复覆盖同一 PageKey 时，旧 prepared proof 会被撤销，且仅在存在同事务更新 generation、没有 lease/pin/pending use 时由 `DiscardSupersededPreparedVersions` 回收；活跃 reader/last-use 暂缓的回收会在 capability 完成后重试。proof/removal 集、校验、epoch prepare 与关闭去重使用 identity 索引，避免大事务二次复杂度。
- `stressTestMemoryFragmentation` 在 `LIMIT_LONG_TESTS=ON` 下由超过 300 s 且第 0 轮无法完成恢复为 3 轮约 11.9 s；并发 clear/iterator 写无 SAFE ASSERT、BR1 诊断告警或失败。全量 paint-device、tiles3、iterator、transaction 与 save/reopen 门槛均通过。

这里的 metadata/latency 和单项恢复门槛是 2026-09-19 功能 cutover gate，不足以替代与 upstream 相同 workload 的
端到端差分。它没有覆盖 blank/default 稀疏性、每 tile 通用 request/lease 成本、重复 first-write COW、per-unlock commit
或 K/N epoch 复杂度，不能继续作为 BR1-PERF 结清证据。

## 3. API 冻结结果

BR1 对后续阶段提供的稳定边界是：

```text
PageKey = SurfaceId + LogicalPageId
PageVersion = PageKey + Generation + DefaultPixelRevision

acquireRead(ReadView, AccessRequirement) -> ReadRequest -> ReadLease
acquireWrite(PageTransaction, WriteMode) -> WriteRequest -> WriteLease
publish/cancel -> PreparedPageProof
resolvePageVersion(PageKey, ReadView) -> exact visible PageVersion
PreparedPageSet + surface metadata -> immutable ImageEpoch commit
retained root -> rollback/rollforward capability
```

关键约束：

- 一个 PageKey 只有一条 canonical generation history；legacy hash 只是 ABI/cache mirror；
- request、writer、lease、operation、transaction、snapshot、provider epoch 和 allocation generation 是不同 capability 空间；
- 多页原子性只由 transaction + immutable epoch root 提供，不由跨页裸指针或“大 lease”提供；
- provider allocation/handle 不暴露给 iterator、PaintDevice 或未来 authoring frontend；
- Layer 与未来 Flow/节点前端都只能通过 backend-neutral Surface/Page/EvalGraph 边界消费该能力，不能重建图层专属存储真相。

## 4. 2026-09-19 验证证据

CPU 构建目录：`krita/_build-br0-cpu`；Vulkan foundation 构建目录：`krita/_build`。

```text
KisPageStoreFoundationTest                 21 passed
KisPageStoreReferenceTest                  29 passed
kis_transaction_test                        9 passed
kis_iterator_test                           9 passed
kis_iterators_ng_test                      11 passed
kis_paint_device_test                      51 passed
kis_tiled_data_manager_test                23 passed

BR1 稳定七项 CTest                           7/7 passed
Vulkan foundation + offscreen CTest          2/2 passed
check-vulkan-architecture.sh                 passed
git diff --check                             passed
```

Vulkan offscreen 仍只证明 foundation device/VMA/shader/timeline smoke，没有改变“Vulkan 不持有 canonical 文档像素”的 BR1 边界。

## 5. 2026-09-20 性能复审与状态修正

同一机器、同类构建参数，对 `origin/master@9a24ae0d8c` 和优化开始前 BR1 的历史测量得到：

```text
stressTest             upstream 2.529 s   BR1 144.530 s   57.1x
stressTestLazyCopying  upstream 0.990 s   BR1  99.605 s  100.6x
32767 blank reads      upstream <1 ms     BR1 331 ms
max RSS                upstream 49.0 MiB  BR1 485.7 MiB
```

补充 tiled-manager suite 为 upstream 11.826 s / 21 cases、BR1 260.062 s / 23 cases；因 case 数不同，它只说明
整体放大，不作为精确倍率 gate。根因审计确认：default page 被逐坐标物化、resident read 重复 acquire/resolve、每次写锁
分配/COW、tile unlock 触发提交/extent 扫描、production commit 使用 reference `QHash/QVector/sort` 全量布局、全局锁及
provider lease 反查进入热路径。

因此 51 的结论限定为“functional/correctness closed”；BR1 总状态为 `BR1-PERF in progress`。最终结清必须增加
virtual default、native resident guard、显式 mutation session、条件原位写/每页一次 COW、persistent epoch root 与
增量 metadata，并通过 52 和 39 的结构及 upstream 差分门禁。

## 6. 下一阶段入口

当前 production 下一步不是 BR2，而是完成 BR1-PERF。BR2 的协议、fake workload 和隔离 reference 研究可以并行准备，
但 PageStore→SubmissionCoordinator production 接线必须等待 52 全部门禁通过。BR1-PERF 不改写 PageKey/PageVersion/
epoch/authority 语义；它调整 CPU data-plane API、调用粒度和 production root 布局。如确需改变冻结语义，必须先以兼容
迁移和 reference proof 更新本记录及权威执行文档。

## 7. 2026-09-20 优化实施检查点

本节保留第一次优化检查点，不改变本文“功能/正确性历史结清”的定位。当前已实现 virgin default read、resident native
read cache、two-stage write intent、whole-tile batch/adoption/alias、persistent balanced root、history changed-page
restore/release、metadata-only retained root 和若干内容相同 no-op。`stressTestLazyCopying` 单次复测为 Qt 0.892 s / real
1.02 s，单次低于历史 upstream 0.990 s 的 1.5× 阈值，但未完成正式配对验收；blank read 保持零 PageStore
page/version/replica allocation，RSS 约 49.7 MiB。

该检查点的主 `stressTest` 单次为 Qt 25.841 s / real 25.98 s，虽然相对初始 144.530 s 已下降约 82.1%，仍约为历史 upstream
2.529 s 的 10.2×，远高于 1.5× 出口。因此 BR1-PERF **仍未结清**。这组单次、非固定随机流的观察不构成独立优化归因。

后续 [53_br1_performance_attribution_review_20260920.md](53_br1_performance_attribution_review_20260920.md) 已撤回“主 stress
主要剩余成本是真实 mutable COW”的推论：诊断中 generic write request 为 0，delete/default 物化、commit/adoption/history
才是已测热点。底层 history delta 不代表 adapter 已增量化，virgin default read 通过不代表删除生命周期已无物化。
正式 mutation/guard API 仍必需，但由独立真实写 workload 验收；修订顺序与状态见 52 的 11，分段图和原始证据见 53。

后续 D1 已修正上述 delete/restore/default revision 路径，并有零新 payload/reader 安全性及 overlay 语义测试、混合 stress 前后诊断，见
[54_br1_optimization_execution_and_deviations_20260920.md](54_br1_optimization_execution_and_deviations_20260920.md)。
这不改写本节历史计时，也不构成同主干 M/K/E 性能验收通过；当前管线仍不能称完全同构主干，BR1-PERF 状态不变。
