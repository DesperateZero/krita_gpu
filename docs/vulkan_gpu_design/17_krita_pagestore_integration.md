# Krita `KisPaintDevice` 与 PageStore 集成

> 本文定义统一页面系统如何进入 Krita 核心图像模型，避免 Vulkan canvas 与 CPU tile manager 长期双权威。
> 该改造是架构基础，不是 UI plugin 内部优化。Canonical 权威设计以
> [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md) 为准：
> PageStore 必须吸收并演进现有 tiles3/COW/memento/swap，不能与 `KisTiledDataManager` 并列为第二个 provider。
> 2026-09-20 的 CPU 差分审计证明“所有访问都走通用异步 lease”不是可接受的集成粒度；BR1-PERF 的 native
> resident CPU 接线与门禁见
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)；条件 COW、backing
> handoff、metadata stable-slot arena、统一 coordinator 与硬预算的写侧实施设计见
> [68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md)。

## 1. 当前咬合事实

当前 `KisDataManager` 不是可直接替换的抽象接口，而是继承具体 `KisTiledDataManager`：

- [`kis_datamanager.h`](../../krita/libs/image/kis_datamanager.h) 通过 `ACTUAL_DATAMGR` 绑定具体实现；
- `KisPaintDevice`、iterator、memento、frame data manager 和大量 CPU 算法直接依赖现有 tile 行为；
- `KisTransactionData` 从 data manager 获取 `KisMemento`；
- 许多算法在像素内循环中使用 random/sequential accessor；
- UI/projection 和 plugin 可能假定 CPU tile 可以同步取得。

因此，“新增一个 Vulkan data manager 子类”或“同时维护 CPU tiled provider 与 GPU PageStore provider”都不是
长期方案。需要为现有 `KisTiledDataManager`/tiles3 建立清晰访问门面，再在其内部逐步加入
surface/page/generation/lease/replica 语义。迁移完成前后，逻辑 tile identity、COW history 和 swap record 始终
只有一套；Vulkan 只实现 `PageReplicaProvider`。

## 2. 长期模块边界

```text
libs/image
  SurfaceRegistry + Canonical PageStore
  EvaluationGraph types/lowerers/planner + DerivedSurfaceCache
  non-surface Value/Resource Store contract
  KisPixelAccessPlan / Session / TileView
  KisPixelSnapshot / Transaction integration
  Surface/Page ids and backend-neutral ticket handle
  KisDataManager facade
  evolved tiles3/COW/unified SSD implementation

kritavulkanbackend
  Vulkan PageReplicaProvider
  Stroke compiler/executor
  Vulkan submission/timeline implementation
  operation-specific GPU executors, including composite

libs/ui/vulkan
  Presenter / swapchain / input-facing canvas adapter
```

硬边界：

- `libs/image` 头文件不出现 `VkDevice`、`VkImage`、`VkBuffer`、descriptor 或 queue。
- `libs/ui` 不拥有 canonical target residency、stroke journal 或 transfer queue。
- 一个 `KisPaintDevice` 永久只有一个 canonical PageStore identity；CPU tile access 是其 facade，不是 provider 选择。
- `kritavulkanbackend` 不链接 `kritaui`；下游 UI adapter 同时消费两者，paintop 只依赖 backend-neutral session，
  backend 只依赖 `kritaimage`。
- RAM/UMA、VRAM、SSD 只是同 generation 的 replica domain，不可成为平行 pixel store。

## 3. Canonical PageStore 访问契约

建议从 `KisDataManager` 外观下抽出 backend-neutral access facade。`KisPixelStore` 若保留该命名，只表示
canonical PageStore 的门面，而不表示可插拔的两套存储实现：

```text
KisPixelStore
  format()/pixelSize()/defaultPixel()
  extent()/region()/setExtent()
  beginAccess(KisPixelAccessPlan) -> KisPixelAccessSession
  snapshot(KisSnapshotPlan) -> KisPixelSnapshot
  restore(KisPixelSnapshot) -> OperationTicket
  purge()/clear()/copy()
  serialize()/deserialize()
  generation()/revision()
```

### 3.1 `KisDataManager` 的角色

`KisDataManager` 保持上层稳定外观，目标是 facade/pimpl：

- 现有 CPU tiled store 就地演进为 canonical PageStore core；
- 现有 API 逐步委托 access/session 层；
- GPU 文档/图层不切换 pixel-store provider，只为同一 PageStore 注册 Vulkan replica provider；
- public/ABI 约束通过 pimpl、factory 和适配层处理；
- 不能通过 `#define ACTUAL_DATAMGR` 在构建时全局替换整个 Krita 存储模型。

### 3.2 访问与 replica 能力

canonical store/session 报告访问能力：

```text
CpuDirectRead
CpuDirectWrite
GpuDirectRead
GpuDirectWrite
AsyncAccess
Snapshots
SparseExtent
AnimationFrames
Serialization
```

调用者不得通过 dynamic_cast 到 Vulkan provider 获取句柄。GPU 消费者通过 backend-neutral
`PageReplicaProvider`/document session 将 paint device identity 映射到 backend handle；PageStore 本身仍拥有
generation、lease、authority 和 publish。

### 3.3 CPU data plane 与 control plane

`KisDataManager` facade 内部必须提供两条共享同一 canonical 状态机的执行路径：

- resident CPU native path：`CapturedReadView + CachedPageHandle + CpuReadGuard/CpuWriteGuard`，只做 page-local
  pin、swap block、generation/allocation validation 和 dirty delta；写侧使用 `CpuWriteIntent -> beginWrite()`，只在
  暴露 writable span 时执行 first-write transition；
- generic materialization path：保留 request/resolve/operation ledger，用于缺少适用 exact 就绪副本、swap-in、跨域或待完成
  producer/访问交接；历史标签、非 CPU authority 或 cached handle miss 本身不触发 materialization。

这不是 provider 切换。`KisTileData` 是 PageStore 的 native CPU replica，在 BR1 CPU-only 路径承载 authority；读侧并不要求
每个 ready exact CPU 副本都是 authority。tiles3 hash 是稀疏 current-head cache；
PageStore 仍拥有 version/epoch/history/authority。已捕获 scope 内的 resident 命中不得创建 heap request/lease、插入全局 map、
取得 PageStore 全局 mutex 或由 provider 线性扫描 active lease。capture/release、首次 binding 与局部同步成本仍计入
完整操作；按 39 的 5.12 区分冷暖与 fallback 原因，不宣称整个 session 严格 lock-free。快慢路径必须调用相同 transition/invariant validator。

## 4. 区域访问协议

### 4.1 `KisPixelAccessPlan`

```text
device/surface identity
region
mode: Read / Write / ReadWrite
domain: CPU / GPU
required generation or LatestCommitted
expected traversal
deadline/priority
allow blocking on worker
```

访问必须在进入像素内循环前声明范围。目的：

- 一次性取得 page lease；
- dGPU 批量下载/上传；
- UMA 一次 cache invalidate/flush；
- 建立 memento/before-image；
- 防止 iterator 每跨一个 tile 就隐式等待 GPU。

### 4.2 `KisPixelAccessSession`

session 持有：

- 精确 generation；
- page lease set；
- CPU pointer/tile view 或 opaque GPU binding handle；
- completion/readiness ticket；
- dirty region accumulator；
- release policy。

CPU accessor 只能在 session Ready 后创建。session release：

- 对 write region 发布新 generation；
- 执行必要 flush；
- 发送 generation-aware dirty event；
- 释放 lease/pin；
- 返回 operation ticket。

对纯 resident CPU session，Ready 可以同步成立，但 session 仍必须在操作边界捕获一次 epoch root。write session 对每个
page 只在 `CpuWriteIntent` 升级为 writable guard 时 reserve G+1；PageStore 私有 `KisPageWriteCoordinator` 生成内联 plan，统一选择 pending 复用、
recoverable/commit-only backing handoff、完整 payload、必要 COW 或纯语义写。tile view/guard 的逐次
release 只合并 dirty range，
不能逐 tile publish、扫描 extent 或 commit epoch。session release 对每个 dirty page seal 一次并只提交一次 root。
这里的 session 是显式未发布 mutation 段，不等于整个 undo/history transaction；中间结果需要可见时按原有语义
seal/发布并开启新段，重新取得 write plan，不跨段沿用可写授权。物理 allocation handoff 服从 25/52/68 的 canonical-owner
证明与 backing budget；调用方不能签发 permit 或依据瞬时 refcount 自行选择。

### 4.3 传统同步 API

大量现有 Krita 算法是同步函数。长期兼容规则：

- 调度层先在 `KisStrokeStrategy`/worker job 中建立 access plan；
- worker 可以等待所需 CPU session ready；
- UI thread 不得直接触发可能等待 GPU/SSD 的 accessor；
- session ready 后，传统 iterator 的内循环仍可以同步读取连续 tile view；
- 未声明区域的 legacy API 需要明确 fallback access plan；resident CPU 页面仍走 native guard，只有真实 miss/域转换可
  等待。不得通过为每个 tile 构造通用 request 来模拟 session。

这不是“所有 CPU API 立即异步化”，而是把异步域切换放在算法边界，而不是像素循环内部。

## 5. Iterator 与 TileView

### 5.1 TileView

backend-neutral view 至少包含：

```text
page/tile logical coordinates
valid rect
row stride
pixel size
read pointer / write pointer（仅 CPU session）
generation
dirty callback/session owner
```

UMA replica 可以让 access session 直接返回 shared mapped page span。dGPU 路径在 CPU session ready 前已经把
请求 generation materialize 为 RAM/CPU-visible replica。CPU iterator 不感知 staging 或 Vulkan，也不自行更改 authority。

### 5.2 Random/Sequential accessor

- accessor 创建时绑定 access session。
- tile 切换先查 session 的 epoch-tagged cached handle/view table；resident 命中 O(1)，失配才回到 root/materialization。
- 写 accessor 在暴露首个 writable span 前确保 snapshot/before-image 已建立；只取得 write intent 不得触发
  COW/generation。legacy API 暴露可写 pointer 后按 dirty 处理。
- 同一 mutation session 的同一未发布段重复触达同一 page 必须复用 pending generation 和 writable allocation；
  中途 seal/发布后新段重新取得 writer/permit，不沿用旧可写授权。
- accessor 销毁不执行 GPU wait；它只把 dirty ranges 交给 session release。
- 无 session 的旧创建函数由调度安全检查保护，在 GPU-backed device 上不能从 UI 隐式进入阻塞路径。

### 5.3 Extent/default pixel

- 空白 page 使用 PageStore 的规范 default-pixel generation，不必物理分配。
- 空白坐标读取返回 surface-level virtual/shared default view，不得因为坐标不同实例化 PageKey/version/replica。
- extent/region 是逻辑元数据，不由当前驻留页集合推断。
- extent/region 由 session changed-page delta 增量更新，不在 tile unlock 或普通 commit 扫描完整 manifest。
- clear/purge 生成页面映射/generation 操作；不能在 GPU backing 未同步时直接删除 CPU tile 并假设完成。

## 6. GPU Stroke 接入

### 6.1 PaintOp

`KisVulkanPaintOp` 或后续 GPU paintop 只负责：

- 读取 Krita brush/input 语义；
- 创建 `StrokeEpochDesc`；
- 生成 `ResolvedDab`；
- append journal；
- 向 `KisPainter` 报告逻辑 dirty region；
- end/cancel epoch。

它不保存 backend pointer、不管理 tile/residency、不调用 render thread、不下载像素。

### 6.2 Target identity

paint device/PageStore 注册 canonical surface identity：

```text
DocumentId
NodeId
FrameId
SurfaceId
StoreGeneration
Format/ColorSpace
```

frame 切换、图层替换或 colorspace conversion 创建新 identity/revision；旧 in-flight work 不能写入新 generation。

### 6.3 CPU fallback

整笔 CPU fallback 仍通过同一个 canonical PageStore：

- RAM 路径：现有 paintop/iterator 通过 CPU write session 修改新 generation；
- UMA 路径：CPU write session 直接写 shared canonical page；
- dGPU 路径：stroke begin 前按读写需求检查 exact CPU-visible valid replica；已有 ready 副本直接使用，否则完成必要
  materialization/访问交接，full overwrite 不强加旧像素读回。CPU publish 后 GPU consumer 按 generation 获取所需 replica。

resident read 的快慢路径判据同 25/33：authority 在其他域、历史读取或 cached handle miss 均不能单独触发迁移；已有
ready exact CPU 副本时受保护地 resolve/pin 即可。这不放宽写侧 authority handoff、唯一 writer、write-plan 证明或必要 COW。

禁止 CPU fallback 写旧 `KisTiledDataManager` 身份、GPU stroke 写另一套 PageStore 身份再合并。

fallback 不只处理“不支持/未 ready”，也处理性能不合格：begin mutation 前以 39 的同机成熟 CPU product profile 比较
完整 GPU/UMA ETA；收益余量不足、profile 过期、queue 拥塞、shared bandwidth/thermal 状态越界时整笔 CPU route。
correctness capability 与 `AutoPreferred` 分开，不能因 Vulkan/UMA 可用或 copy bytes 为零而强制加速路径。

## 7. Dirty、Projection 与 Node 更新

### 7.1 Generation-aware dirty event

```text
Device/SurfaceId
Region/PageSet
OldGeneration
NewGeneration
WriterDomain
WriterTicket
EvaluationEpoch
```

消费者根据 generation 决定：

- projection/composite invalidation；
- thumbnail/outline cache 失效；
- save snapshot visibility；
- CPU/GPU domain transition。

普通 QRect dirty signal 可以保留为 UI/调度外观，但内部不能丢失 generation/ticket。

### 7.2 Projection

- EvalGraphIR 的 surface operation（包括 GPU composite）消费 canonical surfaces 的 read lease。
- CPU projection consumer 先在 worker 取得 CPU read session。
- UI 不通过 `updateCanvasProjection()` 临时同步下载 GPU tile。
- writable target 与 image projection 的语义由 EvalGraphIR/EvaluationPlanner 决定；Layer segment 只作为 lowerer
  optimization，不再让两套 image 谁是 canvas source 相互覆盖。

## 8. Transaction 与 Snapshot 接口

`KisMementoManager` 的现有 COW/oldData 语义必须演进为 PageStore generation reference，而不是与新的 GPU
memento 并存。`KisTransactionData` 通过统一 snapshot handle 使用：

- first-write before-image；
- rollback/rollforward；
- frame identity；
- transaction lifetime；
-异步 recoverability ticket；
- purge/history retention。

详细 transaction 时序见
[18_undo_save_cancel_and_recovery.md](18_undo_save_cancel_and_recovery.md)。

## 9. UI 边界

`KisVulkanCanvas`/Presenter 可以：

- 获取 DisplaySurface snapshot；
- 提交 viewport/transform/visibility hint；
- 发送 input 到 Krita tool/paintop；
- 绘制 outline/overlay；
- 管理 swapchain。

不能：

- 直接操作 target PageStore residency；
- 在 paint event 下载/upload canonical tile；
- 暂停 stroke executor；
- 决定 transaction commit；
- 持有 `KisPaintDevice` 的第二份 GPU authority。

## 10. 线程和锁

- `KisPixelStore` metadata 有明确 owner/锁层级，不能在持有 image/node 锁时等待 GPU/SSD。
- access plan 建立与 lease ready 分成两个阶段。
- CPU worker wait 可取消，并在 wait 前释放不必要的 graph/UI locks。
- dirty event 发布不回调到持有 PageStore 内部锁的任意 Krita consumer。
- document session/PageStore destruction 先禁止新 request，再通过 ticket/deferred reclamation 清理；不在 GUI destructor 中 device idle。

## 11. 实现路线

以下 `KI*` 是全局 BR1/BR5 内部工作包，不得被解释为先建立“CPU provider”，再替换为“GPU provider”。
整个迁移只有一个 canonical store。

### KI0：依赖审计与契约冻结

- 枚举 `KisDataManager`/iterator/memento/frame API 使用点。
- 区分存储契约与 `KisTiledDataManager` 实现细节。
- 冻结 `KisPixelStore`、AccessPlan/Session/TileView/Snapshot 接口。

### KI1：现有 tiles3 facade 与 identity 冻结

- 让现有 `KisTiledDataManager` 通过 facade 实现新访问契约。
- 明确 tile data、memento oldData、default pixel、extent、frame 和 swap 的稳定 identity。
- 现有 Krita image/iterator/transaction 测试必须保持通过。
- 此阶段不引入 Vulkan。

### KI2：调度边界

- CPU 算法在 worker 上预先建立区域 session。
- 检测 UI thread 隐式 blocking accessor。
- iterator 绑定 session，不逐 tile 触发域转换。

### KI3：Canonical PageStore core

- 在现有 tiles3/COW/swap 内加入 generation、lease、authority 和 replica ledger。
- UMA CPU pointer TileView。
- dGPU CPU session 的批量 page materialization ticket。
- extent/default/clear/copy/serialize 基础语义。
- CPU native resident guard、virtual default、mutation session、条件 backing handoff/必要 COW、硬 backing 预算和
  production persistent epoch root；
  reference `QHash/QVector` 不得成为 production layout。

### KI4：GPU stroke/projection

- PaintOp 输出 journal，不接触 Vulkan page。
- generation-aware dirty event。
- GPU composite 读取同一 canonical surfaces。
- 删除 `writeBytes()` 回灌主路径。

### KI5：Memento/frame/save

- 现有 memento/COW 演进为 PageStore generation snapshot，不保留并列实现。
- frame data manager identity。
- rollback/rollforward/save/reopen。

### KI6：UI 清理与基线切换

- Canvas 只保留 Presenter/DisplaySurface。
- 删除同步 partial tile download、GPU canvas authority 和双状态更新。

## 12. 验收门槛

- `libs/image` 无 Vulkan 类型依赖。
- 一个 paint device 只有一个 canonical PageStore identity；不存在 CPU tiled/GPU PageStore provider 切换。
- CPU/GPU brush、filter、save、undo 消费同一 surface generation。
- GPU-backed device 的 iterator 不在像素循环中隐式等待/迁移单个 tile。
- UI thread 无可能触发 GPU/SSD wait 的 pixel accessor。
- 演进后的 tiles3/PageStore 保持现有 CPU 核心测试和语义。
- blank/default read 保持稀疏，任意坐标数量不增长 page/version/replica 数量。
- resident iterator/accessor 内循环不建立 heap request/lease、不进入全局 request map、不扫描 provider active lease。
- PageStore 内部 selector 只有在 recoverable-before 或完整预检的 commit-only 条件成立时才移交 CPU allocation，并逻辑发布
  新 generation；无 before backing 且仍可取消/失败的多页 Prepared transaction 不允许 handoff。否则同一 mutation 的同一
  未发布段每页只执行一次 first-write COW。
- 普通无旧值保留的 resident write 在 handoff 命中时零 before-image copy、零新 payload allocation、零退休 payload；
  current/history/pending/in-flight/retiring backing 精确计量并受硬上限、背压和 `ResourcePressure` 约束。
- session 结束前 tile unlock 不 commit epoch；production root commit 和 extent 更新只随 changed pages 扩展。
- CPU 性能满足 52 的 upstream 差分门禁后，BR1 才可整体结清。
- GPU/UMA 产品 Auto 满足 39 的 CPU-relative 门禁；GPU 劣势环境下在首次写前 CPU route，无同 epoch 混写。
- UMA CPU access 返回共享 canonical page pointer，无像素镜像回灌。
- dGPU CPU access 在 worker 按区域批量转换，不逐 tile 同步。
- `KisTransactionData` 能持有 PageStore snapshot/memento。
- Vulkan canvas 不再拥有第二份 target authority。
