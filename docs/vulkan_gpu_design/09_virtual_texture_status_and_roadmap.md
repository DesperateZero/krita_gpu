# 统一虚拟纹理现状、目标与施工路线

> 本文是虚拟纹理专题文档。MVP 边界和状态词服从 [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md)。
> Stroke 如何消费 lease、温度和三类 backend 见 [15_stroke_residency_and_memory_backends.md](15_stroke_residency_and_memory_backends.md)，Krita canonical store 接入见 [17_krita_pagestore_integration.md](17_krita_pagestore_integration.md)。
> Canonical PageStore 和 replica 权威设计分别见
> [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md) 与
> [26_p0_replica_uma_dgpu_ssd.md](26_p0_replica_uma_dgpu_ssd.md)；若本文内部 `VT*` 工作包与全局 BR0–BR6
> 冲突，以 [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md) 为准。
> 虚拟纹理最终算法、取舍评分和细化实施方案以
> [32_virtual_texture_architecture_decisions.md](32_virtual_texture_architecture_decisions.md) 及 33–39 专题为准；本文负责现状、
> 总体目标和路线，不再把原则性描述视为算法已经冻结。

## 1. 结论

当前实现是 sparse image、staging buffer、transfer queue 和简单 prefetch 的实验组合，尚未达到理想原型，更没有达到第一个 MVP。

首个 MVP 必须包含：

- VRAM / RAM / SSD 自动透明转录；
- UMA 共享权威页和 CPU 指针旁路；
- 独显 VRAM cache；
- dirty/generation/pin/in-flight 状态机；
- 绘画感知的自动温度管理；
- `MutationRootSet` 驱动的图层剪枝；
- lower checkpoint 与安全的 upper cache/replay；
- 强制迁移、撤销和保存正确性测试。

这些不是后期性能优化，而是决定存储模型、shader 访问方式和图层合成方式的大代价基础能力。

## 2. 当前代码的真实状态

### 2.1 Sparse canvas

`KisVulkanTileManager` 创建大型 sparse image，并维护逻辑 tile、物理内存页、bind/unbind 和 transfer。

问题：

- 逻辑 tile 固定为 64×64，但设备 sparse block granularity 是运行时属性。
- bind offset 仍按 `col * 64` / `row * 64` 计算，不能保证物理页对齐。
- 一个逻辑 tile 只分配一个 VRAM page，却允许代码生成多个 sparse bind。
- sparse bind 没有完整的 GPU-side 同步。
- image layout 在多个路径中被乐观假定。

因此它只能作为实验输入，不能作为最终页面模型。

### 2.2 RAM staging

已有 persistently mapped staging buffer，但它当前承担 upload/download 临时缓冲，并不是统一 RAM canonical backing。

问题：

- staging budget 超限只警告；
- backing、snapshot 和 transfer 临时缓冲没有统一生命周期；
- prefetch 重新 bind 后不保证把 staging 内容恢复到 GPU；
- dirty eviction 没有先完成下载；
- detach/free 与异步 job 依赖分散在多个类。

### 2.3 SSD

Krita 现有 `KisTileDataStore`/`KisSwappedDataStore` 已有 CPU tile swap 基础；但当前 Vulkan `L3_Cold` 没有
接入它，也没有 generation-aware unified SSD replica。因此不能把 `L3_Cold` 称为 SSD 层，更不能另建一套
Vulkan page store。

现有 swap 尚缺少目标模型需要的：

- 文件/pack 格式；
- page index；
- generation/checksum；
- 异步 I/O；
- 空间回收；
- 失败恢复。

### 2.4 UMA

当前代码会检测同时具备 device-local、host-visible、host-coherent 的 memory type，并在部分 buffer allocation 中使用它。

这不等于画布零拷贝：

- 画布权威数据仍围绕 optimal/sparse image；
- CPU 不能把 sparse image 内存视为线性像素数组；
- image upload/download 仍经过 transfer；
- 没有 CPU/GPU access lease、generation 和 cache maintenance 状态。

### 2.5 温度与 Prefetch

当前 `age()`、viewport 和 pan velocity 只构成简单启发式：

- 没有目标图层角色；
- 没有 brush trajectory/halo；
- 没有 dirty 和写回成本；
- 没有重建成本与依赖扇出；
- 没有派生缓存覆盖度；
- 没有迟滞和 backpressure；
- 没有 SSD 恢复成本。

因此不能称为全自动温度管理。

### 2.6 非活动图层与合成

非活动 paint layer 当前主要使用整画布 VkImage，合成目标也是独立整图 image。这导致：

- 显存随图层数线性增长；
- 不受 tile budget 控制；
- 内容更新和缓存失效不完整；
- 固定 RGBA8；
- compositor output 尚未可靠接入显示。

## 3. 目标页面模型

目标模型已作出以下不可逆算法决策：

- 页面驻留是真实的 replica set，不是互斥 `L1/L2/L3` tier；
- PageStore 使用分片 map 和短临界区 transition，所有 I/O/GPU 工作在锁外；
- GPU writable exact replica 使用 fixed-slot buffer slab；
- stroke/composite 热路径使用 operation-scoped resolved binding，不查询全局可变页哈希；
- UMA CPU pointer 与 GPU handle 访问同一物理页，但不要求地址数值相等；
- dGPU 按 byte/deadline 合批并保留 authority handoff emergency reserve；
- SSD 区分 SessionSpill 与 RecoveryCheckpoint，不做每页 fsync；
- 温度采用 safety eligibility、semantic class、cost/CLOCK history 三层算法。

完整决策及评分见 [32_virtual_texture_architecture_decisions.md](32_virtual_texture_architecture_decisions.md)。

### 3.1 Surface

`Surface` 表示有稳定像素语义的二维资源，不规定其物理存储。

建议类型：

- `CanonicalLayerSurface`
- `BrushResourceSurface`
- `LowerCheckpointSurface`
- `UpperOverlaySurface`
- `UpperOperatorSurface`
- `UpperReplayBundle`
- `DisplaySurface`
- `UndoSnapshotSurface`

每个 surface 至少记录：

- format/color space/pixel layout；
- logical tile geometry；
- revision/generation；
- canonical 或 derived；
- dependency set；
- rebuild cost；
- persistence policy。

### 3.2 Page

每个 page 维护：

```text
SurfaceId + LogicalPageId
SurfaceFormat
PublishedGeneration
PreparedGenerationsByTransaction
WriteGeneration
AuthorityReplica
ValidReplicas[domain, generation]
ReadLeases / WriteLease
InFlightTickets
PinReasons
ResidencyPolicyHandle / SemanticClassSnapshot (non-authoritative)
SsdRecord
DependencyGenerations
```

物理 backend 可以把一个逻辑页映射到一个或多个 GPU block，也可以让多个逻辑 tile 共享一个物理 block。映射不能泄漏到 brush/compositor 上层。

### 3.3 Derived page

checkpoint、display 和部分 upper cache 是 derived page：

- 可以在压力下丢弃；
- 不作为文档保存权威数据；
- 必须记录 dependency revision；
- rebuild 前检查 evaluation epoch 和 mutation roots/writable targets。

## 4. 后端设计

### 4.1 UMA backend

UMA 是主后端：

- 使用少量大块、持久映射的 buffer arena；
- 普通 stroke 由 operation-scoped binding table/direct handle 保存 exact page 到 slot 的映射；只有非局部访问使用
  稀疏后备目录；
- CPU 直接取得线性像素指针；
- GPU brush/compositor 通过 storage buffer 访问；
- coherent 内存只做 ordering，non-coherent 内存还需 flush/invalidate；
- sampled image/atlas 仅在显示或特定 shader 需要时作为 derived cache。

UMA 上逻辑 L1/L2 不代表两份数据：它们折叠为同一物理页的 GPU-hot/CPU-visible 访问状态。真正的容量下沉是 shared memory → SSD。

### 4.2 dGPU backend

- canonical 是逻辑 page generation，不等同于 RAM allocation。
- RAM 与 VRAM 都是 replica；GPU 写完成并 publish 后，VRAM 可成为 authority。
- upload/download 和 sparse bind 返回统一 batch ticket。
- graphics/compute submit 等待相关 batch。
- dirty VRAM page 在解绑前必须成功回写到 RAM 或另一个安全 backing。
- 无 sparse residency 时使用 paged buffer/atlas backend，不能退化成固定整图常驻。

具体 slab、批处理、staging、deadline 和 backpressure 算法见
[34_virtual_texture_gpu_binding_and_arenas.md](34_virtual_texture_gpu_binding_and_arenas.md) 与
[36_virtual_texture_dgpu_migration.md](36_virtual_texture_dgpu_migration.md)。

### 4.3 SSD backend

只允许把现有 `KisTileDataStore`/`KisSwappedDataStore` 演进为 unified SSD store；不得在 Vulkan backend
创建独立 page file、L3 或 swap。持久层采用 append-only segment + 原子 index commit，record 为：

```text
record header
  surface id
  page id
  generation
  format id
  codec
  checksum algorithm/version
  compressed size
  uncompressed size
  encoded payload checksum
  canonical content checksum
  header checksum
  commit sequence
payload
```

- RAM 写 SSD 完成前不能释放最后权威副本。
- 读取校验失败时不能发布页面。
- derived page 默认可丢弃，不必写 SSD；只有重建代价超过阈值时才允许缓存。
- 后台 GC 回收不可达 record；文档保存继续走 Krita 正式格式，不能把临时 store 当文档格式。

SSD 明确区分仅保证 live session 可读的 `SessionSpill` 与经过 data/manifest group durability 的
`RecoveryCheckpoint`。不得每页 fsync 或立即读回；完整提交、恢复和 GC 协议见
[37_virtual_texture_ssd_segment_store.md](37_virtual_texture_ssd_segment_store.md)。

## 5. Evaluation Graph、MutationRootSet 与图层剪枝

通用 EvalGraphIR 和 task DAG 服从 [28_p0_graph_epoch_projection_display.md](28_p0_graph_epoch_projection_display.md)。
本节 lower/upper 只描述 `KisLayerStackLowerer` 可识别的 layer-specific residency 优化。

### 5.1 Stroke epoch

开始笔画时冻结：

- `EvaluationEpoch`
- 非空 stroke writable targets，以及它们映射出的 `MutationRootSet`
- 目标 surface generation
- 相关 blend/group/mask 依赖

通常只有一个目标 paint layer。多目标操作必须显式声明目标集合，不能把整棵图层树视为可能写入。

### 5.2 单目标切分

```text
Lower read-only segment
        -> LowerCheckpoint
Writable target
Upper read-only segment
        -> Overlay / Operator / Replay
```

- LowerCheckpoint 在目标笔画期间稳定，保持 viewport 范围 hot 即可。
- 目标页和 brush halo 是最高优先级。
- 上层根据背景依赖分类。
- 被有效派生结果覆盖的非目标 canonical page 可以转冷并下沉。

### 5.3 多目标切分

```text
C0 -> T0 -> C1 -> T1 -> ... -> Tn -> Cn
```

- `T` 是 writable target。
- `C` 是当前 epoch 内 immutable segment。
- 目标变化只使相关下游组合结果失效，不使 segment 的 canonical source 自动失效。

### 5.4 Upper cache 分类

- `BackdropIndependentOverlay`：可以独立预合成，再覆盖任意下方结果。
- `BackdropOperator`：缓存可作用于 backdrop 的参数化算子。
- `BackdropDependentReplay`：保存准备后的 source/mask/filter 输入，目标变化后局部重放。

不能把任意 blend mode 的上层在透明背景上拍平后直接覆盖新目标结果。

## 6. 绘画感知温度

本节只列语义输入。最终选择算法固定为：先做不可覆盖的 safety eligibility，再按 semantic class 选择范围，最后在
同类内部使用成本/物理字节与 CLOCK-style ghost history 排序。`CoveredCold` 必须附带完整
`CoverageCertificate`，不能仅因“当前不是活动层”成立。详见
[38_virtual_texture_residency_temperature.md](38_virtual_texture_residency_temperature.md)。

策略输入：

```text
role priority
viewport visibility
distance to brush trajectory
predicted stroke halo
dirty writeback cost
rebuild cost
dependency fanout
surface class
cache coverage/substitutability
SSD restore cost
recent access with hysteresis
```

页面角色：

1. `CurrentWrite`：正在写的目标、output 与必要 before-image。
2. `PredictedWrite`：有 deadline/TTL 的预测 corridor。
3. `VisibleExact`：viewport 的 checkpoint/upper/display exact dependency。
4. `UndoOrSaveRetention`：transaction、undo、immutable save 引用页。
5. `ReplayOrCheckpoint`：即将参与 replay/rebuild 的 source/checkpoint page。
6. `CoveredCold`：有有效 CoverageCertificate 的非目标源页。
7. `OffscreenCold`：不可见且低依赖。
8. `DerivedDiscardable`：可重建的派生缓存。

迁移采用高低水位和最短驻留时间，避免频繁反向转录。

## 7. 访问 API

上层只应看到冻结的 request/lease 接口：

```cpp
ReadRequest  acquireRead(PageRange, AccessDomain, Priority);
WriteRequest acquireWrite(PageRange, AccessDomain, WriteMode, Priority);

ReadLease  resolve(ReadRequest, CompletionTicket);
WriteLease resolve(WriteRequest, CompletionTicket);

GpuTicket publish(WriteLease, GpuTicket producerCompletion);
void cancel(WriteLease);

PageTransaction beginTransaction(ImageEpochId base);
ImageEpochCommitTicket commit(PageTransaction, PreparedPageSet);
void abort(PageTransaction);
ImageEpochSnapshot captureCommittedEpoch();
```

`publish()` 先产生 transaction-private Prepared generation；多页 operation 通过 immutable ImageEpoch manifest
原子发布完整 page set。普通 reader/save 不逐页观察半提交 generation。

返回 ticket/page span 可以包含 CPU pointer 或 opaque GPU binding handle，但调用者不关心页面位于 VRAM、shared
memory、RAM 还是 SSD。

`KisPaintDevice` 必须通过 canonical PageStore access facade 消费这些接口。这个 facade 是现有 tiles3 的
generation/lease 化，不是与旧 tiled provider 并列的第二个 data manager，也不维护需要 stroke-end 回灌的
CPU 权威镜像。传统同步 iterator 应先取得区域 lease，再进入像素循环。

禁止上层直接：

- `bindTilePage()`；
- 分配 staging；
- 等待 transfer queue；
- 选择 SSD record；
- 修改 residency tier。

## 8. 同步状态机

最小状态转换示例：

```text
RAM_VALID -> UPLOAD_IN_FLIGHT -> VRAM_VALID
VRAM_DIRTY -> DOWNLOAD_IN_FLIGHT -> RAM_VALID
RAM_DIRTY -> SSD_WRITE_IN_FLIGHT -> SSD_VALID
SSD_VALID -> SSD_READ_IN_FLIGHT -> RAM_VALID
SHARED_CPU_WRITE -> SHARED_GPU_READY
SHARED_GPU_WRITE -> SHARED_CPU_READY
```

规则：

- generation 不匹配的完成事件不得覆盖新数据。
- in-flight 页面不能复用物理 allocation。
- transfer/sparse-bind ticket 必须可被 GPU submit wait。
- 错误路径保留最后权威副本。
- timeout 不能把页面错误标记为 clean。

## 9. 施工阶段

以下 `VT*` 只是虚拟纹理专题工作包，不是全局执行顺序。BR0 删除旧 runtime；BR1 完成 canonical
PageStore；BR2 完成 SubmissionCoordinator；只有进入 BR3 后才允许把 UMA/dGPU/SSD provider 接入 production。
BR4 才接入温度和图层剪枝。任何 `VT*` 都不得绕过这些进入条件。

### VT0：可观测基线

- 设备能力与 sparse granularity 报告。
- page transition trace。
- VRAM/RAM/SSD budget 和使用量。
- validation layer 启动基线。

### VT1：页面几何与 reference state machine

- 从 Krita 现有 tile/COW/undo/swap identity 演进，不创建 Vulkan PageStore。
- SurfaceId/PageId。
- logical-to-physical mapping。
- authoritative/generation/dirty/pin/in-flight。
- 无 GPU 随机迁移模型测试。
- 分片 PageStore、materialization dedup、transaction manifest 和 stale completion/ABA 测试，详见
  [33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md)。

### VT2：UMA backend

- mapped buffer arena。
- CPU/GPU lease。
- direct PageHandle、operation-scoped local binding 与稀疏后备目录访问。
- flush/invalidate 和 timeline。
- shared canonical page checksum 测试。
- BDA 与 descriptor+offset 两种 binding，domain-copy/COW/derived-copy 分项计数。

### VT3：dGPU backend

- RAM backing 与 VRAM cache。
- upload/download/sparse-bind batch。
- GPU-side wait。
- dirty safe eviction。
- atlas/no-sparse backend。
- deadline-aware byte batch、staging retirement、emergency reserve 和 backpressure。

### VT4：SSD backend

- 演进 `KisTileDataStore`/`KisSwappedDataStore` 为唯一 generation-aware segment/index/checksum store。
- async read/write/cancel。
- budget、空间回收和失败恢复。
- RAM↔SSD 强制抖动测试。
- SessionSpill/RecoveryCheckpoint、partial write、manifest/GC interruption 恢复。

### VT5：ResidencyController

- 统一预算。
- 语义温度。
- 高低水位、迟滞和 backpressure。
- 多 surface 竞争测试。
- safety/semantic/CLOCK-cost 三层策略、CoverageCertificate、bounded trajectory corridor 和多文档公平性。

### VT6：EvaluationPlanner 与 Layer lowering optimization

- typed EvalGraphIR、requested outputs、通用 task DAG 与空 MutationRootSet。
- stroke writable targets 到 mutation roots 的映射。
- lower checkpoint。
- upper overlay/operator/replay 分类。
- evaluation epoch、operation/context revision 和局部 invalidation。

### VT7：绘画消费者

- Auto Round Brush。
- 独立 StrokeCompute lane、不可变 journal 和有序 page job。
- page-batched kernel，不逐 dab dispatch/barrier。
- dirty display tile。
- page-level undo snapshot。
- save/reopen。
- UMA/dGPU/SSD 同一测试矩阵。

具体执行契约见 [10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md)。

## 10. 建议提交序列

具体提交必须嵌入 [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md) 的顺序：

1. BR1：冻结来自 tiles3/COW/swap 的 Surface/Page/State 与 reference tests。
2. BR2：引入统一 ticket、GPU-side wait、queue 独占和资源退休。
3. BR3：依次接入 UMA arena、dGPU fixed-slot/binding replica、unified SSD store 和 safe authority handoff。
4. BR4：引入 EvalGraphIR/reference lowerer/EvaluationPlanner、ResidencyController、MutationRootSet、Layer
   checkpoint 和 upper replay optimization。
5. BR5：接入 brush/undo/save consumer。
6. BR6：接入 DisplaySurface UI，并在全部压力、性能、格式和故障测试通过后开放入口。

每个提交必须包含对应测试或 trace；不得只提交接口和文档后标记完成。

## 11. MVP 验收矩阵

### 正确性

- VRAM→RAM→SSD→RAM→VRAM 后 checksum 一致。
- dirty page 不在未保存时解绑。
- generation 竞争不会提交旧数据。
- CPU/GPU 并发访问受 lease 约束。
- 设备不支持 sparse 时仍使用同一页面系统。

### UMA

- canonical canvas page 是共享 mapped page。
- brush 和 compositor 直接访问该页。
- CPU 读取不经过 image→staging copy。
- non-coherent 路径正确 flush/invalidate。

### 绘画

- 当前目标页和预测 halo 保持 hot/pinned。
- lower checkpoint 有效时，下层源页可以自动降温。
- upper cache 对安全 blend 正确复用，对背景依赖 blend 正确 replay。
- stroke end 不整图回读。

### 压力

- 人为限制 VRAM/RAM，持续绘画和平移不丢数据。
- 多 surface 竞争不会饿死当前目标。
- SSD 写失败、取消和超时保持最后权威副本。
- derived cache 被丢弃后可以重建。

### 集成

- 只有完整 BR0–BR6 和 MVP 门禁通过后，正常 Krita 入口才启用。
- undo/redo/save/reopen 一致。
- validation layer 无资源状态相关错误。
- 所有性能结果记录硬件、预算、文档规模和测试脚本。

## 12. 当前代码处理原则

只可迁移独立正确的纯算法和测试资产：

- transfer/timeline 的概念、trace 与测试；当前单 command-buffer `TransferQueue` 删除；
- tile/page 标识和 debug 统计；
- resolved dab 的字段与 CPU dynamics 边界；固定覆盖式 brush ring 不保留；
- graphics/compute shader 实验成果；
- Krita transaction 的业务测试；旧 sync stroke 下载 runtime 删除。

不应继续扩展为目标架构：

- 固定 64×64 直接 sparse bind；
- `L1/L2/L3` 枚举直接代表真实 backing；
- 非活动层整图 VkImage；
- 8192×8192 dense fallback；
- 上层直接管理 staging/bind/wait；
- 只按 age 的 prefetch；
- stroke-end 下载作为 UMA 主路径。

## 13. 最终判断

虚拟纹理、UMA 指针旁路、SSD backing、自动温度和图层剪枝必须作为一个整体进入首个 MVP。允许分提交验证，但不允许用不同的数据模型先做“简化版本”再推迟重构。后续功能应当只扩展 backend、策略和消费者，不再改变 canonical surface/page 语义。
