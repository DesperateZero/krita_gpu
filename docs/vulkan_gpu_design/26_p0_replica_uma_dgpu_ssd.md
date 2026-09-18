# P0：统一 Replica 模型——UMA、dGPU、RAM 与 SSD

> 本文定义同一 canonical PageVersion 在不同物理域的 replica。Canonical identity 和不变量见
> [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md)。
> 物理 binding、UMA、dGPU、SSD 和温度的实施算法分别见
> [34_virtual_texture_gpu_binding_and_arenas.md](34_virtual_texture_gpu_binding_and_arenas.md)–
> [38_virtual_texture_residency_temperature.md](38_virtual_texture_residency_temperature.md)。

## 1. Replica 不是 Page

```text
PageVersion = SurfaceId + LogicalPageId + Generation

Replica
  domain
  PageVersion
  physical allocation/record
  valid/in-flight/error state
  access capabilities
  last-use ticket
```

可能域：

```text
CpuRam
UmaShared
DiscreteVram
Ssd
GpuSampledExact
DerivedGpu
```

- 同一 generation 可以有多个 valid replica。
- AuthorityReplica 表示当前最新内容的责任位置，不改变 PageVersion identity。
- sampled atlas 的无变换核心可以是可丢弃 exact auxiliary replica；gutter、颜色转换和 display output 是 derived。
  二者默认都不能成为 canonical authority。
- sparse/atlas/buffer 是 `DiscreteVram` 的物理策略，不是上层 tier。

## 2. `PageReplicaProvider`

定义在 `kritaimage` 的 backend-neutral interface：

```text
capabilities()
requestReplica(PageVersion, Domain, AccessMode, Priority)
prepareWrite(PageKey, WriteGeneration, Domain)
transfer(SourceReplica, TargetReplica)
validate(Replica, Generation)
retire(Replica, CompletionTicket)
memoryUsage()/budgetSignals()
```

实现：

- CPU/RAM/SSD provider 位于 `kritaimage`；
- Vulkan UMA/dGPU provider 位于 `kritavulkanbackend`；
- PageStore 选择 provider/迁移并提交 authority handoff；
- consumer 只获得 lease，不直接调用 provider。

## 3. Authority handoff transaction

任何域切换遵循：

```text
Source replica G remains valid/authoritative
-> allocate Target replica for G
-> copy/materialize
-> producer completion
-> validate generation/format/checksum
-> PageStore atomically adds Target valid replica
-> optionally switch AuthorityReplica
-> only then retire Source when leases/pins allow
```

失败：

- Target 标记 Failed/丢弃；
- Source authority 不变；
- page generation 不变；
- dirty/valid 不被伪造；
- budget/backpressure 得到通知。

不存在“先 unbind/释放源，再希望 staging/SSD 有数据”的路径。

## 4. UMA Shared Replica

### 4.1 Arena

- 少量大块持久映射 buffer allocation；
- host-visible、device-addressable，满足目标设备内存类型；
- PageVersion 映射到 arena allocation id + byte offset；
- CPU tile view 与 GPU opaque handle/device address 访问同一物理像素；两种地址数值不要求相等；
- allocator 遵守 format alignment/non-coherent atom size；
- allocation 直到全部 lease/ticket/reference释放后回收。

### 4.2 与现有 tile/COW 集成

- `KisTileData`/CPU tile view 可以由 shared arena backing 提供 data pointer；
- COW 分配新 shared page，旧 PageVersion 指针继续有效；
- iterator 不知道 Vulkan，只使用 CPU lease pointer/stride；
- GPU direct/local binding snapshot 由 Vulkan provider建立并发布 ticket；
- PageStore 保持 generation/authority，Vulkan provider不改 tile history。

### 4.3 同步

CPU 写后 GPU：

```text
CPU write lease release
-> flush mapped range if non-coherent
-> publish CPU completion/order ticket
-> GPU submission acquire/order
```

GPU 写后 CPU：

```text
GPU producer timeline
-> PageStore publish generation
-> CPU read request continuation
-> invalidate mapped range if non-coherent
-> CPU lease ready
```

host-coherent 只省略 flush/invalidate，不省略 execution ownership/order。

### 4.4 零像素复制定义

UMA canonical path 的画布像素 copy count 必须为零：

- 不做 image→staging→KisTileData；
- 不做 KisTileData→staging→canonical image；
- COW/undo snapshot 是语义需要的 version copy，不计作 domain synchronization copy，但必须单独统计；
- display/sample atlas 是 derived copy，单独统计，不能伪装 canonical zero-copy。

## 5. dGPU VRAM Replica

### 5.1 物理布局

首选 software binding：

- logical PageId -> VRAM buffer/atlas fixed slot；
- stroke PageJob 直接携带已解析 PageHandle；composite/filter 使用 operation-scoped immutable local binding table；
- 只有事前无法列举有限 region 的访问才使用两级稀疏后备目录；
- logical page 不直接绑定为 Vulkan sparse block；
- physical granularity/format alignment 由 provider内部处理。

后端策略：

- storage buffer page arena；
- image atlas；
- sparse image 仅在设备能力和映射验证后作为可选优化。

任何策略使用同一 PageReplicaProvider/lease/ticket 契约。

### 5.2 GPU 写

- prepareWrite 为 WriteGeneration 分配 VRAM replica/slot；
- 恢复 base generation 或规范 default；
- 等待 binding publish、resource 和 previous writer；
- GPU producer 完成后 PageStore publish；
- VRAM 可成为新 AuthorityReplica；
- journal/before generation 保留到新 generation recoverable。

### 5.3 CPU materialization

CPU/save/filter 请求 exact generation：

- 若 RAM/SSD 同 generation 已 valid，直接选择；
- 否则从 VRAM 批量 download 到 RAM replica；
- download/validate 完成后 resolve CPU lease；
- 不因 stroke end 自动回传全部页面。

### 5.4 Sparse 可选优化

- query runtime sparse granularity/format support；
- 一个 logical page 可映射多个 physical blocks，多个 logical page 也可打包一个 allocation；
- bind/unbind由 SubmissionCoordinator提交 ticket；
- provider binding/映射记录吸收几何差异；
- 无 sparse 时功能/语义不变。

删除固定 `col*64,row*64` 直接生成 `VkSparseImageMemoryBind` 的假设。

## 6. RAM Replica

RAM provider 演进自 `KisTileDataStore`：

- 为 PageVersion 提供 CPU-visible replica；
- 支持 existing tile data pool/COW/default pixel；
- 参与统一 lease/pin/in-flight；
- 作为 dGPU 安全 backing 和 CPU algorithm materialization；
- memory metric按format/replica/snapshot精确核算；
- pooler/swapper 只通过 PageStore eviction transaction 行动。

UMA 设备上 `CpuRam` 与 `UmaShared` 可以物理折叠；状态仍记录 CPU/GPU access ordering，而不是制造两份数据。

## 7. 统一 SSD Replica

### 7.1 唯一实现

直接演进：

- [`KisTileDataStore`](../../krita/libs/image/tiles3/kis_tile_data_store.h)
- [`KisSwappedDataStore`](../../krita/libs/image/tiles3/swap/kis_swapped_data_store.h)

禁止在 Vulkan backend 增加独立 L3 file/cache/index。

### 7.2 Record

```text
RecordVersion
SurfaceId
LogicalPageId
Generation
SurfaceFormatId
CodecId/Version
ChecksumAlgorithmId/Version
CompressedSize
UncompressedSize
EncodedPayloadChecksum
CanonicalContentChecksum
HeaderChecksum
CommitSequence
PayloadOffset
```

### 7.3 Segment/index

- append-only segment 写 payload；
- `SessionSpill` 在 I/O completion 和进程内 index commit 后可成为 live-session backing；
- `RecoveryCheckpoint` 才执行 data/manifest 分组 durability barrier；禁止每页 fsync；
- 原子提交 index/commit sequence；
- PageStore 只有在 index commit 成功后添加 Valid Ssd replica；
- 后台 GC复制仍被引用 record 后原子切换 segment；
- crash/取消恢复扫描 commit sequence，不接受半写 record。
- 正常写入不立即读回整页；写前生成 checksum，读取 materialization 时验证 payload。

### 7.4 Codec

- codec 由 SurfaceFormat/数据特性选择，不能固定认为 RGBA8；
- 解压后验证 uncompressed size 和 checksum；
- codec/version不支持时不能发布页面；
- default/zero page可用规范 special record，但必须保留format/default semantics。

### 7.5 写入/读取

写入：

```text
Valid RAM/UMA replica G
-> pin source
-> compress/write segment
-> checksum/index commit
-> publish Ssd replica G
-> release source pin
```

读取：

```text
find exact PageVersion record
-> async read/decompress
-> size/checksum/format validate
-> publish RAM/UMA replica G
```

失败/取消不改变 authority。SSD 不直接成为 GPU shader source；先materialize到 RAM/UMA/VRAM。

## 8. Migration DAG

典型 dGPU cold write：

```text
SSD G -> RAM G -> VRAM G -> GPU write G+1
             before-image/undo -----^
```

典型保存：

```text
VRAM G -> RAM G -> serializer
SSD G ------------^（若已有验证 replica）
UMA G -> direct CPU lease
```

每步是 operation/ticket；PageStore publish 逐步增加 valid replica。consumer等待精确 ready ticket，不阻塞提交线程。

## 9. Residency/温度

策略固定分为 safety eligibility、semantic class、cost/CLOCK history 三层；不能以单个全局分数覆盖安全规则。

统一策略输入：

- canonical/derived；
- MutationRootSet/trajectory halo；
- viewport/display；
- dirty/authority writeback成本；
- before-image/undo retention；
- dependency fanout/rebuild cost；
- SSD restore cost；
- format/replica size；
- minimum residency/hysteresis；
- document/session budget/fairness。

策略输出只选择：保留、预取、materialize、handoff、retire候选。它不能直接修改 page state 或绕过安全检查。
`CoveredCold` 必须由带 EvaluationEpoch、MutationRootSet、property/source generation 和 replay route 的
`CoverageCertificate` 证明。

## 10. 预算

统一核算：

- RAM canonical/COW/snapshot；
- UMA shared arena；
- dGPU VRAM page/resource/display；
- staging/transient/in-flight；
- SSD records/segments；
- immutable brush resources；
- derived caches。

优先回收：

1. 无引用 DerivedDiscardable；
2. covered/offscreen derived；
3. 已有安全 backing 的 cold replica；
4. canonical authority handoff 后源 replica。

绝不直接回收 active write、lease、pin、in-flight、未安全写回 authority。

## 11. 实现路线

### RP0：Interface/CPU reference

- Replica/Provider/authority handoff状态机。
- fake domains和failure tests。

### RP1：RAM/现有 swap吸收

- `KisTileDataStore` lease/replica化。
- `KisSwappedDataStore` generation record/index/校验。
- 保持CPU Krita行为。

### RP2：UMA

- shared fixed-slot arena、tile view、BDA 或 descriptor+offset binding。
- coherent/non-coherent tests；canonical copy count 0。

### RP3：dGPU

- VRAM fixed-slot buffer、operation-scoped binding、optional atlas；deadline-aware upload/download batch。
- dirty writeback/authority handoff。

### RP4：Sparse optimization

- runtime mapping/capability；可选启用。
- no-sparse同语义测试。

### RP5：Residency/budget

- safety/semantic/CLOCK-cost temperature、bounded trajectory、CoverageCertificate、document fairness、pressure backpressure。
- 三域随机迁移。

## 12. 验收门槛

- logical PageVersion 与 physical replica完全分离。
- UMA canonical CPU/GPU同一物理页，像素同步copy=0。
- dGPU VRAM/RAM authority handoff失败保留旧authority。
- SSD只使用升级后的Krita统一store，无Vulkan独立L3。
- 64×64 logical tile不再等同sparse block。
- sparse/no-sparse设备使用同一上层状态机。
- VRAM→RAM→SSD→RAM→VRAM checksum/generation一致。
- 所有迁移、sparse bind、direct/local binding publish通过ticket DAG。
- lease/pin/in-flight/authority安全规则在压力和故障下成立。
