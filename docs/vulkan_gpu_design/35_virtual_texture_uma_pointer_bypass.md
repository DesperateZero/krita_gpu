# 虚拟纹理 UMA 指针旁路与一致性方案

> 本文定义 UMA shared replica 的物理与同步语义。PageStore 状态见
> [33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md)，GPU slot/binding ABI 见
> [34_virtual_texture_gpu_binding_and_arenas.md](34_virtual_texture_gpu_binding_and_arenas.md)。

mapped memory 的 flush/invalidate 和 `nonCoherentAtomSize` 约束以
[Vulkan memory specification](https://docs.vulkan.org/spec/latest/chapters/memory.html) 为准。

## 1. 能力定义

UMA MVP 能力必须同时满足：

1. canonical PageVersion 的 exact bytes 位于 CPU 可映射且 GPU 可读写的同一物理 allocation。
2. CPU iterator 获取稳定 lease pointer/stride；GPU 获取 opaque handle/descriptor/address。
3. CPU/GPU 访问通过 lease、execution ordering 和 cache maintenance 串行化。
4. 稳态 CPU↔GPU domain synchronization 的 canvas-pixel copy bytes 为零。
5. sampled atlas/display copy 单独计数，不能冒充 canonical 零复制。

CPU pointer 和 GPU address 不需要数值相同；“pointer bypass”指绕过像素上传/下载管线。

## 2. Capability descriptor

```text
UmaPageCapability
  hostVisible
  deviceAccessible
  deviceAddressSupported
  hostCoherent
  hostCached
  atomSize
  minStorageBufferAlignment
  maxStorageBufferRange / descriptor strategy
  supported StorageClass set
  measured CPU read/write profile
  measured GPU read/write profile
```

只有满足格式、usage、同步和性能门禁的 StorageClass 才声明 `UmaShared`。检测到
`HOST_VISIBLE | DEVICE_LOCAL` 本身不构成能力完成。

若同一物理类型 GPU 性能不达门禁，该设备可使用 dGPU-style RAM+VRAM replica；必须如实报告 UMA pointer bypass
不支持，不能暗中复制仍宣称零复制。

## 3. Shared arena

每个 StorageClass 使用少量大 buffer allocation：

```text
UmaArena
  allocation/resource
  persistent mapped CPU base
  GPU descriptor/device address
  aligned fixed slots
  dirty atom tracker
  slot generation
  allocation last-use timeline
```

要求：

- 整个可用范围持久映射；
- slot 起点、row stride 和 size 覆盖 storage-buffer 与 non-coherent atom 对齐；
- 不在每页访问时 map/unmap；
- allocation 在全部 CPU lease 和 GPU ticket 完成前不释放；
- allocator 只返回 opaque token，Krita 上层不持有 arena 对象。

## 4. 与 `KisTileData` 的结合

BR1/BR3 迁移后，CPU tile view 可由 shared slot backing：

```text
KisTile/PageVersion facade
  -> CpuReadLease/CpuWriteLease
  -> pointer = mappedBase + slotOffset
  -> rowStride / validRect / SurfaceFormat codec
```

必须修改的生命周期假设：

- 旧 `KisTileData` 不能自行 `free()` shared pointer；
- duplicate/COW 通过 PageStore 分配新 PageVersion/slot；
- pooler/swapper 不直接移动带 active lease 的 shared slot；
- iterator 结束释放 lease，而不是暗含指针永久有效；
- 需要跨调用保存像素地址的旧代码必须显式持有 access session。

Vulkan 类型不能进入 `kritaimage` 公共接口。arena backing 通过 provider token 和 CPU span adapter 暴露。

## 5. 访问所有权状态

每个 shared replica 至少区分：

```text
Idle
CpuReaders(n)
CpuWriter
GpuReaders(in-flight tickets)
GpuWriter(in-flight ticket)
TransitionPending
```

这些是 lease/ticket 推导状态，不应再引入可绕过 PageStore 的独立 dirty owner。

### 5.1 CPU write -> GPU read/write

```text
CPU obtains exclusive write lease
-> CPU writes canonical bytes
-> release computes dirty atom ranges
-> flush ranges if non-coherent
-> publish host completion/order token
-> GPU submission waits host-release dependency
-> GPU memory dependency makes host writes visible
```

### 5.2 GPU write -> CPU read

```text
GPU obtains exclusive write lease
-> submission waits prior CPU/GPU users
-> compute writes shared page
-> writer timeline completes
-> PageStore publishes generation
-> CPU continuation observes completion
-> invalidate aligned ranges if non-coherent
-> resolve CPU read lease
```

### 5.3 Concurrent reads

CPU/GPU concurrent read 可以允许，但只有在：

- generation 相同；
- 没有 writer；
- host cache maintenance 已完成；
- provider/device memory model 支持对应 host/device access；
- lease 明确记录两个 reader。

MVP 可以先串行化 CPU/GPU read 以降低证明难度，但 API 不得假设物理复制。

## 6. Cache maintenance

non-coherent range 必须向下/向上对齐到 `nonCoherentAtomSize`。为避免两个页面共享同一 atom 造成 data race：

- slot 起点和 charged size 至少 atom-aligned；或
- allocator 为共享 atom 建立排他 ownership，不允许不同 page 并发 host/device 写。

优先采用 slot atom alignment，以空间换取简单、可证明的一致性。

host-coherent 只省略 flush/invalidate，不省略：

- CPU/GPU execution order；
- writer exclusivity；
- timeline/host continuation；
- publication validation。

## 7. BDA 与 descriptor

### 7.1 BDA 路径

- arena allocation 启用 device-address capability；
- binding entry 保存 provider 解析后的地址或 base+offset；
- shader 使用显式 alignment；
- address 不进入 PageStore/journal/undo/SSD；
- device loss/arena rebuild 后 ProviderEpoch 使旧地址全部失效。

### 7.2 Descriptor 路径

- 每个 arena 或 arena bank 使用稳定 storage-buffer descriptor；
- binding entry 保存 descriptor selector + offset；
- 超过 descriptor/range 限制时增加 bank，不改变 PageHandle API。

BDA 是性能和绑定简化优化，不是 UMA 同页语义的唯一实现。

## 8. COW、undo 与 snapshot

UMA 零 domain-copy 不表示永远不复制像素。以下 copy 属于语义 copy：

- first-write COW；
- undo before-image；
- immutable save snapshot 在无法继续共享时的复制；
- format conversion 产生 derived surface。

计数必须区分：

```text
DomainSyncCopyBytes      // UMA canonical steady state must be 0
CowCopyBytes
UndoSnapshotCopyBytes
DerivedAtlasCopyBytes
DisplayCopyBytes
```

COW 优先顺序：

1. 保留旧 shared slot，为 G+1 分配新 slot并用 GPU/CPU page copy；
2. 若 G 无任何 reader/memento/save ref，可复用物理 slot，但仍逻辑发布 G+1；
3. 内存压力下先把旧 generation 安全写 SSD，再决定是否复用。

## 9. Sample/display path

若显示或特定 compositor 需要 `VkImage`：

```text
UmaShared exact G
-> copy/convert to SampleAtlas/DisplaySurface G'
-> derived dependency records source G
-> display reads derived ticket
```

该 copy 不阻塞 canonical writer；derived 失效或丢弃不影响 canonical page。不能让显示 image 反向覆盖 shared page。

## 10. 预算与回收

UMA 上 CpuRam 和 UmaShared 可以物理折叠，只计一次 physical bytes。另计：

- COW/history slots；
- binding metadata；
- derived atlas/display；
- transient command/resource upload；
- allocator padding；
- OS/driver reported usage。

压力顺序：

1. 丢 derived；
2. 释放无引用 exact duplicate；
3. 把 CoveredCold/OffscreenCold generation 写入 SSD；
4. handoff 后释放 shared slot；
5. 保留 current target/emergency reserve。

## 11. 故障与关闭

- flush/invalidate 失败或 device loss：不发布目标 generation；保留 recoverable old generation/journal。
- CPU pointer lease 未释放：document close 进入有界 drain/cancel，不提前 unmap。
- GPU ticket 未完成：arena 延迟退休；不能通过普通析构直接 free。
- capability 在 device recreation 后变化：创建新 ProviderEpoch，旧 handle 失效并从 RAM/SSD materialize。

## 12. 测试矩阵

必须覆盖：

- coherent 与 non-coherent fake/device path；
- atom 边界相邻页面并发访问；
- CPU write→GPU read、GPU write→CPU read、read/read；
- iterator、clone、COW、memento、save snapshot；
- BDA 与 descriptor+offset；
- 4/8/16 字节及更多 StorageClass；
- arena growth、slot ABA、device recreation；
- 强制小预算 shared→SSD→shared；
- 删除全部 sampled/display cache 后重建；
- 稳态绘画 `DomainSyncCopyBytes == 0`。

## 13. 实施顺序

### UMA0：CPU-mapped fake arena

- slot/alignment/lifetime；
- `KisTileData` facade 和 iterator lease；
- COW/undo reference。

### UMA1：Vulkan descriptor path

- persistent mapping；
- host/device ordering；
- coherent/non-coherent tests。

### UMA2：BDA path

- address binding ABI；
- alignment validation；
- provider epoch/device loss。

### UMA3：Stroke/composite

- direct PageJob handle；
- operation-local binding window；
- derived sample/display path。

### UMA4：Performance gate

- CPU iterator、GPU brush、composite 和 mixed trace；
- 与 dGPU-style copy path 做端到端比较；
- 只有完整 trace 达标的 StorageClass 才声明 UMA pointer bypass。

## 14. 完成门槛

- CPU/GPU exact page 使用同一物理 allocation；
- steady-state domain copy 为零；
- cache maintenance 范围和 execution order 经过 validation/golden；
- 上层不知道 Vulkan memory type/BDA；
- sampled image 丢失不影响 canonical 数据；
- COW/undo copy 与 domain synchronization copy 可区分；
- 不满足硬件/格式门禁时能力如实返回 Unsupported，而不是静默退化后继续宣称 UMA。
