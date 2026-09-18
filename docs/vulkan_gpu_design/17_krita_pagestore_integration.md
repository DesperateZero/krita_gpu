# Krita `KisPaintDevice` 与 PageStore 集成

> 本文定义统一页面系统如何进入 Krita 核心图像模型，避免 Vulkan canvas 与 CPU tile manager 长期双权威。
> 该改造是架构基础，不是 UI plugin 内部优化。Canonical 权威设计以
> [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md) 为准：
> PageStore 必须吸收并演进现有 tiles3/COW/memento/swap，不能与 `KisTiledDataManager` 并列为第二个 provider。

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

### 4.3 传统同步 API

大量现有 Krita 算法是同步函数。长期兼容规则：

- 调度层先在 `KisStrokeStrategy`/worker job 中建立 access plan；
- worker 可以等待所需 CPU session ready；
- UI thread 不得直接触发可能等待 GPU/SSD 的 accessor；
- session ready 后，传统 iterator 的内循环仍可以同步读取连续 tile view；
- 未声明区域的 legacy API 需要明确 fallback access plan，最坏可以请求整个相关 surface，但不能逐 tile wait。

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
- tile 切换只查 session 已准备的 view table。
- 写 accessor 第一次触达 page 时确保 snapshot/before-image 已建立。
- accessor 销毁不执行 GPU wait；它只把 dirty ranges 交给 session release。
- 无 session 的旧创建函数由调度安全检查保护，在 GPU-backed device 上不能从 UI 隐式进入阻塞路径。

### 5.3 Extent/default pixel

- 空白 page 使用 PageStore 的规范 default-pixel generation，不必物理分配。
- extent/region 是逻辑元数据，不由当前驻留页集合推断。
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
- dGPU 路径：stroke begin 前为目标区域 materialize CPU-visible replica，CPU publish 后 GPU consumer 按
  generation 获取 VRAM replica。

禁止 CPU fallback 写旧 `KisTiledDataManager` 身份、GPU stroke 写另一套 PageStore 身份再合并。

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
- UMA CPU access 返回共享 canonical page pointer，无像素镜像回灌。
- dGPU CPU access 在 worker 按区域批量转换，不逐 tile 同步。
- `KisTransactionData` 能持有 PageStore snapshot/memento。
- Vulkan canvas 不再拥有第二份 target authority。
