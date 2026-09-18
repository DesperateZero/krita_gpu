# P0：Canonical PageStore 与 Krita Tile/COW/Undo/Swap 吸收

> 本文定义唯一权威像素模型。PageStore 不是 Vulkan 新建的第二套 tile manager，而是把 Krita 现有逻辑 tile、
> COW、memento、tile data store 和 swap 语义提升为显式 Surface/Page/Generation/Lease/Replica 状态机。
> 状态布局、线性化点、分片并发、materialization 去重和多页 transaction 的可实施算法见
> [33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md)。

## 1. 现有语义必须保留

当前 `tiles3` 已提供大量成熟语义：

- `KisTiledDataManager` 维护逻辑 tile hash/extent/default pixel；
- `KisTile` 连接逻辑坐标与 `KisTileData`；
- `KisTileData` 通过共享/复制实现 COW；
- `KisMementoManager` 记录 tile change、revision、rollback/rollforward；
- `KisTileDataStore` 全局管理 tile data、内存统计、pooler 和 swapper；
- `KisSwappedDataStore` 把 tile data 压缩/换出并恢复；
- iterator/accessor 依赖 oldData/current memento 行为。

P0 不能绕过这些语义再造“GPU tile + 结束后回写”。目标是把这些已有身份和历史关系显式纳入 PageStore。

## 2. Canonical 身份

### 2.1 Surface

每个 canonical paint device/frame 对应稳定 surface：

```text
SurfaceId
DocumentId
NodeId
FrameId
SurfaceKind
SurfaceFormat
DefaultPixelGeneration
Extent/RegionRevision
PublishedRevision
CommittedImageEpochId
```

同一个 PaintDevice 的 projection、display image、GPU atlas 不能复用其 canonical SurfaceId；它们是不同 derived surface。

### 2.2 LogicalPageId

```text
LogicalPageId = (tileColumn, tileRow)
```

- 几何服从 Krita logical tile 大小和坐标规则；
- 与 Vulkan sparse granularity、atlas slot、buffer allocation 无关；
- 空白/default tile 可以没有物理 allocation，但仍有规范化 generation/value；
- wrap/LoD 是访问/derived 语义，不改变 base LogicalPageId。

### 2.3 PageGeneration

每次成功写入产生新 generation：

```text
PageKey = SurfaceId + LogicalPageId
PageVersion = PageKey + Generation
```

`KisTileData`/shared arena block/RAM allocation/VRAM slot/SSD record 都是某个 PageVersion 的 replica 或 backing，
不是独立 page identity。

## 3. Page record

```text
SurfaceId
LogicalPageId
SurfaceFormat
PublishedGeneration
PreparedGenerationsByTransaction
WriteGeneration(optional)
AuthorityReplica
ValidReplicas[ReplicaDomain -> Generation/State]
ReadLeaseSet
WriteLease(optional)
InFlightTicketSet
PinReasons
ResidencyPolicyHandle / SemanticClassSnapshot (non-authoritative)
SsdRecord(optional)
DependencyGenerations（derived only）
Default/Allocated state
Error state
```

`dirty`、`tier`、`layout` 不作为上层可直接修改的真相；它们从 generation/replica/ticket 状态推导或由 backend
私有保存。

## 4. 永久不变量

1. 每个 `PageKey` 只有一个 `PublishedGeneration`。
2. 同一 `PageKey` 同时最多一个 write lease/write generation。
3. write generation Prepared 且所属 ImageEpoch transaction commit 前，旧 PublishedGeneration 继续有效。
4. producer 失败/取消只丢弃 WriteGeneration，不修改旧 PublishedGeneration。
5. authority handoff 只有在目标 replica 完成、generation 匹配且校验通过后原子提交。
6. authority 被释放前，至少另一个同 generation replica 已 valid，或 page 是可重建 derived。
7. SSD write/index commit 前，源 authority 不能释放。
8. derived page 不能成为 canonical surface 的 authority。
9. CPU/GPU/IO 访问都持有 lease；in-flight allocation 不能复用。
10. 只有 PageStore completion/transaction-commit 路径能改变 PublishedGeneration/AuthorityReplica。
11. 迟到 ticket 完成不能覆盖更新 generation。
12. default/empty page 的 materialization 必须产生规范内容，不能读取未初始化内存。

Debug/CI build 始终检查这些不变量。

## 5. API

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

`publish()` 在 producer 完成后把页置为所属 transaction 的 Prepared generation；单页 operation 使用隐式单页
transaction。多页 batch 只有在 immutable ImageEpoch manifest 原子 commit 后才改变普通 document reader 所见的
PublishedGeneration 集合。
这里的 PageStore visibility transaction 可以是一批页面；完整 stroke 的 Krita undo transaction 可顺序聚合多个已
commit ImageEpoch，二者不得混为一个生命周期。

需要读取历史 generation 时，由 `PageRange`/read request descriptor 携带 exact-generation selector，不增加一套
旁路访问 API。这里的 `GpuTicket` 必须是定义在 `kritaimage` 的 backend-neutral completion value handle；名称不
允许意味着调用者可取得 Vulkan fence/semaphore，CPU/IO completion 也通过同一 ticket bridge 表达。
`ImageEpochCommitTicket` 同样是 backend-neutral host logical completion，不要求或允许 UI 直接等待 Vulkan primitive。

### 5.1 Request 与 Lease 分离

- `acquire*` 原子检查/预留逻辑状态并返回 request + readiness dependency。
- materialization、SSD read、VRAM upload 或旧 writer wait 可以异步发生。
- 只有 readiness 完成且 request 仍匹配 generation 才 `resolve()` lease。
- consumer 不通过轮询物理 tier 判断是否可访问。

### 5.2 Read lease

包含：

- exact PageVersion；
- CPU pointer/span 或 opaque GPU binding handle；
- valid rect/stride/format codec；
- replica domain；
- release operation。

read lease 期间对应 replica/page version 不能回收或被写入覆盖。

### 5.3 Write lease

包含：

- base PublishedGeneration；
- reserved WriteGeneration；
- exclusive writer token；
- writable CPU pointer 或 opaque GPU binding handle；
- before-image/COW snapshot dependency；
- producer/publish contract。

write lease 不能被复制成多个 writer。多页面 write request 返回每页独立 lease/token，但 operation 可批量管理。

## 6. 把 COW 映射到 Generation

现有 COW 的核心不是“复制 CPU tile”本身，而是旧内容引用必须在新写入后保持可用于 reader/undo。

目标流程：

```text
Published G points to PageVersion/TileData A
-> acquireWrite reserves G+1
-> first write captures/retains A as before generation
-> writable replica B prepared
-> producer writes B
-> page G+1 becomes Prepared
-> transaction/ImageEpoch manifest atomically publishes G+1
-> A remains referenced by memento/readers or becomes reclaimable
```

优化：

- 若现有 `KisTileData` usersCount 表明独占且无 reader/memento，CPU 写可原位使用物理 allocation，但逻辑上仍发布新 generation。
- UMA shared arena 可以 copy-on-write 到另一 shared page。
- dGPU 可以 VRAM copy、RAM existing base 或 journal replay建立 before-image。
- 优化不能让旧 generation 在 publish/undo 前失效。

## 7. 吸收 `KisMementoManager`

### 7.1 Memento 内容

PageStore-aware memento 记录：

```text
SurfaceId
Transaction/RevisionId
PageId -> BeforeGeneration
PageId -> AfterGeneration
DefaultPixel/Extent metadata generations
Snapshot/retention handles
Recoverability ticket
```

### 7.2 Rollback/Rollforward

- rollback 为每页发布一个指向 BeforeGeneration 内容的新逻辑恢复 generation，或原子切换 version head（取决于并发模型）。
- rollforward 恢复 AfterGeneration/after snapshot/journal replay。
- 操作通过 PageStore，不能直接替换 GPU/CPU 私有 tile 指针。
- 当前 iterator oldData 语义通过 memento snapshot lease 提供。

### 7.3 与现有测试兼容

BR1 首先在纯 CPU replica 上重现现有 memento、iterator、clone、copy、frame、default pixel、extent、purge 行为。
没有完整测试通过前不接 Vulkan replica。

## 8. 吸收 `KisTileDataStore`

`KisTileDataStore` 从“全局 CPU tile data 容器”演进为 PageStore 的 RAM/CPU replica allocator/store：

- `KisTileData` 获得稳定 PageVersion/replica metadata，或由新的 RAM page object取代；
- pooler/swapper 通过 Residency policy 申请 authority handoff，不直接换出正在 lease/in-flight 的数据；
- memory statistics 纳入 canonical、snapshot、replica、compressed/SSD 维度；
- `ensureTileDataLoaded()` 变为 CPU read lease/materialization，而不是调用者直接操作 swap lock；
- duplicate/free 服从 generation reference/lease/ticket。

不允许另建 `VulkanTileDataStore` 与其并行。

## 9. 吸收 `KisSwappedDataStore`

SSD/swap 详细设计见 [26_p0_replica_uma_dgpu_ssd.md](26_p0_replica_uma_dgpu_ssd.md)。核心要求：

- 由现有 swap 能力演进为统一 SSD replica provider；
- record key 从 tile pointer/allocator chunk 提升到 SurfaceId/PageId/Generation；
- append-only segment + checksum + atomic index commit；
- CPU和Vulkan页面使用同一 store/index/budget/GC；
- 不新建 Vulkan L3 文件或独立 SSD cache。

## 10. Default、Extent、Purge

### Default page

- default pixel 具有 format 和 metadata generation。
- 未分配 page 的内容由 default generation 定义。
- GPU materialization 使用 codec/clear kernel生成精确 default，不能固定 clear RGBA8 透明。

### Extent/Region

- extent/region 是 surface metadata revision。
- 驻留 replica 集合不能反向决定 extent。
- crop/extend 产生 page/version/ref 变化，并保持 memento/reader 可见性。

### Purge/Clear

- clear 是 write operation，产生 generation/COW。
- purge 只有在历史/lease/replica引用释放后才能回收。
- derived invalidation 与 canonical purge 分离。

## 11. SurfaceFormat

每个 PageVersion 绑定完整 `SurfaceFormat`，不是只有 pixelSize：

```text
KoColorSpace identity/revision
channel model/order
channel type/bit depth
pixel stride/alignment
alpha presence/type/premultiplication
endianness/packing
default pixel bytes
codec id/version
```

格式设计详见 [29_p0_surface_format_lod_capabilities.md](29_p0_surface_format_lod_capabilities.md)。

## 12. Derived Surface

derived surface 也使用 Surface/Page/Generation/Lease，但：

- 记录 dependency generation vector；
- 无文档 authority；
- 压力下可丢弃；
- rebuild/publish 不能改变 canonical source；
- SSD 缓存只有在策略认为重建昂贵时才可使用，且仍不是 canonical document record。

## 13. Lock 与状态提交

- PageStore 按稳定 PageKey hash 分片；单页 transition 只短持一个 shard lock。
- 多页 operation 按稳定 shard 顺序预留 intent，并通过 immutable transaction manifest 提交可见性，不长时间
  持有多 shard lock。
- acquire request 不持锁等待 IO/GPU。
- completion callback 先校验 operation/page generation，再短持锁 publish。
- 不能持有 image/node/UI lock 等待 lease ready。
- existing swap lock 逐步收口到 replica provider 内部，不暴露给上层 accessor。
- 相同 `(PageVersion, target domain, capability, provider epoch)` materialization 必须去重。
- physical slot 使用 allocation generation 防止退休/复用后的 ABA；旧 completion 不得命中新 allocation。

## 14. 实现路线

### PS0：事实与映射测试

- 记录现有 tile/COW/memento/swap 行为测试。
- 建立 SurfaceId/LogicalPageId 与现有 tile col/row 的映射。

### PS1：CPU-only generation core

- Page record/state machine/request/lease。
- 分片 metadata、transition completion queue 和 materialization dedup。
- transaction manifest、immutable image epoch 与随机完成乱序 reference test。
- 现有 `KisTileData` 作为 RAM replica。
- default/extent/clear/copy。

### PS2：COW/memento

- usersCount/oldData/memento revision 映射到 generation retention。
- rollback/rollforward 与现有像素一致。

### PS3：统一 tile store/swap

- `KisTileDataStore` 纳入 replica/lease。
- `KisSwappedDataStore` 使用 generation record/index。
- failure/checksum/GC。

### PS4：Async access

- request/resolve/continuation。
- CPU iterator session。
- 后续 GPU provider interface。

### PS5：Canonical cutover

- 所有 `KisPaintDevice` 操作通过 PageStore facade/core。
- 删除 parallel Vulkan tile authority。

## 15. 验收门槛

- 纯 CPU Krita tile/COW/memento/swap/iterator/save 测试全部保持。
- 一个 PageKey 只有一个 PublishedGeneration 和一个 writer。
- 写失败/取消不污染旧 generation。
- swap/SSD 失败不释放最后 authority。
- CPU/GPU/derived 都通过 lease，不直接改 dirty/tier。
- PageStore 使用现有 logical tile identity，不把 sparse block 当 page。
- production provider 与无 GPU reference model 使用同一 transition 语义。
- stale completion、provider epoch 和 allocation ABA 被稳定拒绝。
- undo/save 通过 transaction/image epoch 看不到多页半提交状态。
- 不存在第二套 Vulkan tile/SSD/undo store。
- 4/8/16 字节及更多格式 identity 不被压成 RGBA8。
