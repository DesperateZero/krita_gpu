# 虚拟纹理 GPU 页绑定、Arena 与物理寻址方案

> 2026-11-04 新版后端扩展设计：[105完整规范](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/UNIFIED_BACKEND_DESIGN.md)。逻辑64×64、buffer slab/direct-local binding基线不变；物理slot/stride/收费和真实GPU输入接入新结果协议。 当前只完成设计，CPU产品0fd96保持；不据此声称GPU/完整能力已实装。旧实现名称不能覆盖105的目标责任，未迁消费者在原矩阵追踪。

> 本文定义 GPU replica 的物理布局和 shader 绑定 ABI。状态发布服从
> [33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md)，queue/ticket 服从
> [27_p0_submission_threading_zero_blocking.md](27_p0_submission_threading_zero_blocking.md)。

Vulkan sparse granularity/binding约束参考
[Khronos Sparse Resources](https://docs.vulkan.org/guide/latest/sparse_resources.html)，buffer device address能力与边界参考
[Khronos Buffer Device Address](https://docs.vulkan.org/guide/latest/buffer_device_address.html)。外部规范只约束 provider，
不改变本文的 canonical PageVersion。

## 1. 核心决策

- canonical logical page 固定为 Krita 64x64 tile。
- baseline GPU replica 使用少量大 buffer allocation 的 fixed-slot slab。
- shader 热路径消费 operation-scoped immutable binding table 或直接 PageHandle。
- 全局坐标查找只作为后备，不进入普通 stroke 页 job。
- image atlas 可以保存 exact sampled replica 或 derived view，但不拥有 canonical identity。
- native sparse resource 是可选 provider，缺失时所有上层语义不变。

## 2. Logical page 与 physical slot

### 2.1 StorageClass

物理 slot 由存储类别决定：

```text
StorageClassId
SurfaceFormatId / canonical codec
plane count
pixel stride
row stride
tile bytes
required CPU/GPU alignment
non-coherent atom alignment
usage/capability flags
```

不能只按 `pixelSize` 合并格式；通道顺序、packing、alpha 语义或 shader codec 不同就可能需要不同 StorageClass。

### 2.2 Slab/Arena

```text
Arena
  ProviderInstanceId
  StorageClassId
  VkBuffer/allocation or equivalent provider resource
  mapped base?            // UMA only
  device address?         // capability-dependent
  slot count
  free bitmap/runs
  arena generation
```

每个 slot 固定大小，slot 内保存一个 exact PageVersion。大 allocation 的大小由 benchmark/profile 决定，不进入 ABI。

不采用：

- 每页一个 `VkBuffer`/`VkDeviceMemory`；
- 通用 variable-size free list；
- 让 sparse block 大小决定 logical page；
- 把多个 logical page 合并成不可独立 COW/undo 的 superpage。

多个 slot 可以在 transfer 时连续合批，也可以在相同 allocation 内相邻放置，这只是物理优化。

## 3. Allocation token 与生命周期

```text
GpuPageHandle
  ProviderInstanceId
  StorageClassId
  ArenaId
  ArenaGeneration
  SlotIndex
  SlotGeneration
  byteOffset
  access flags
```

Public/backend-neutral lease 中只保存 opaque handle。Vulkan provider resolve 后才得到 descriptor、buffer、offset 或
device address。`SlotGeneration` 防止 slot 复用后的 ABA。

分配流程：

```text
reserve free slot
-> create Allocating replica/token
-> initialize exact base/default if required
-> publish mapping/binding table entry
-> signal ready ticket
-> PageStore validates and marks Valid
```

退休流程必须等待：

- 所有 read/write lease；
- 所有引用该 handle 的 compiled batch；
- binding snapshot retirement；
- last GPU use ticket。

## 4. 三种 GPU 访问形式

### 4.1 Direct PageHandle

普通 page-batched stroke 已知 input/output page：

```text
PageJob
  exact PageVersion ids
  input handles
  output handle
  row stride / format codec
  valid rect
  dab/ref ranges
```

shader 不执行 PageKey hash，直接使用 handle 中已解析的 arena/offset。descriptor 数量通过按 StorageClass 绑定少量
稳定 arena 或 descriptor indexing 控制。

### 4.2 Local dense binding window

composite、filter 或邻域操作在提交前声明 region/halo，compiler 创建：

```text
PageBindingTableSnapshot
  SnapshotId / ProviderEpoch
  origin page coordinate
  width/height
  entry stride/version
  exact PageVersion per entry
  opaque GpuPageHandle or DefaultSentinel
  publish ticket
  last-use ticket
```

这是 operation-scoped immutable snapshot。发布后不原地更新；新 generation 创建新 snapshot/entry set。

### 4.3 Sparse fallback directory

只有无法预先列出有限 region 的 GPU 算法才使用：

```text
sparse root: (SurfaceId, leafX, leafY) -> leaf slot
dense leaf: local page coordinate -> immutable entry
```

root 可使用 provider 内部 open-addressing 或排序目录，但必须满足：

- probe 有明确上限；
- miss 返回显式 invalid/default sentinel；
- entry 发布和退休有 ticket；
- 不把 root pointer/address 暴露给 journal 或 PageStore；
- 热路径是否启用由 benchmark gate 决定。

## 5. Binding entry ABI

版本化 entry 至少表达：

```text
BindingEntryVersion
StorageClassId
Arena/descriptor selector
slot/byte offset
row stride
format codec selector
valid rect/default sentinel
read/write capability
debug PageVersion tag
```

production shader 不能依赖 debug tag 保证正确性；正确性来自 immutable snapshot 和 submission dependency。debug/CI
shader 可以验证 tag，发现错误映射立即失败。

设备地址是 provider 实现细节：

- 支持 BDA 时，provider 可把地址写入 binding buffer；
- 不支持时使用 descriptor + byte offset；
- address 只在 allocation lifetime 内有效；
- journal、undo、SSD record 永不保存 GPU address。

## 6. Mapping publish

Binding table 是 GPU resource，更新必须通过 SubmissionCoordinator：

```text
allocate/initialize replica
-> build immutable binding data
-> upload or host-flush binding data
-> submit publish dependency
-> signal BindingReadyTicket
-> consumer waits BindingReadyTicket
```

不能在已经提交的 command buffer 读取期间原地覆写 entry。可采用 copy-on-write table chunk、double-buffer 或按 ticket
退休的 arena；具体方式是内部参数，但 immutable 可见性不可改变。

## 7. Buffer stroke 与 sampled atlas

### 7.1 Buffer baseline

适合：

- UMA CPU/GPU 同页访问；
- dGPU compute brush read-modify-write；
- 多 SurfaceFormat 的显式 codec；
- 精确 COW page copy；
- 不依赖 image tiling/sparse granularity。

画布采样若需要双线性/跨页邻域，由 local binding window 和显式 border/neighbor fetch 实现。

### 7.2 Sample atlas promotion

只有预测在 reuse horizon 内满足以下成本条件才创建 atlas：

```text
populateCost + expectedImageSamplingCost
    < expectedManualBufferSamplingCost
```

成本系数来自设备 trace。atlas 规则：

- 核心 64x64 内容必须对应 exact PageVersion；
- gutter/border 是 derived 数据，依赖相邻 generation；
- atlas entry 记录 dependency vector；
- canonical write 不就地覆盖仍被 reader 使用的 atlas；
- 可在压力下直接丢弃；
- 不允许仅剩 atlas 而丢失 canonical recoverability，除非 provider 明确把无 gutter 的核心区域注册为 exact
  replica 且通过同一 authority 规则。

### 7.3 Display surface

颜色转换、proofing、缩放和装饰后的 display tile 永远是 derived surface，不得注册为 canonical exact replica。

## 8. Native sparse provider

启用条件全部满足后才可注册：

- 目标格式和 usage 支持 sparse residency；
- runtime granularity 可正确覆盖 logical page；
- bind/unbind 由 SubmissionCoordinator 独占；
- 有完整 queue ownership/timeline 测试；
- 内存浪费和端到端 trace 优于 buffer/atlas baseline；
- no-sparse 路径保持同一功能和测试结果。

一个 logical page 可以覆盖多个 sparse block；多个 logical page 也可由一个更大 allocation 支持，但 mapping 必须保留
独立 generation/lease/retirement。禁止再次出现 `col*64,row*64` 直接构造 sparse bind 的假设。

## 9. Format codec

shader codec 按 `StorageClassId`/`SurfaceFormatId` 选择：

- load canonical bytes；
- 转换到计算表示；
- 执行 blend/composite；
- 按 alpha/channel/rounding 规则写回 canonical bytes。

GPU 不支持的格式在 operation 开始前路由 CPU。不能写入一部分页后因 codec 缺失再回退。

## 10. Budget accounting

GPU provider 分别报告：

- exact buffer replica bytes；
- sampled exact replica bytes；
- derived atlas/display bytes；
- binding table/root/leaf metadata；
- staging/transient bytes；
- reserved emergency bytes；
- in-flight but not reusable bytes；
- allocator fragmentation/internal padding。

逻辑 tile bytes 与 charged physical bytes 必须同时记录，才能识别 sparse/atlas/slab 的真实浪费。

## 11. 故障处理

- slot allocation 失败：operation Failed/Backpressured，不能返回空 handle；
- binding upload 失败：replica 保持非 Valid，source 不释放；
- device loss：provider epoch 递增，所有旧 GPU handle 失效；
- stale compiled batch：ProviderEpoch/SlotGeneration 不匹配，禁止提交或在 debug shader 中失败；
- atlas dependency 失效：拒绝采样并重新计划，不用旧颜色；
- sparse bind 失败：该 provider operation 失败，不改变 PageStore semantics。

## 12. 实施顺序

### GA0：CPU layout/reference

- StorageClass、slot layout 和 alignment 测试；
- fake arena/token/ABA 测试；
- binding ABI schema/version。

### GA1：Vulkan buffer slab

- descriptor+offset 基线；
- allocation/retirement ticket；
- direct PageJob handles。

### GA2：Local binding window

- composite/filter halo；
- immutable snapshot publish；
- generation/debug validation。

### GA3：Sample atlas

- exact core/gutter dependency；
- promotion cost trace；
- drop/rebuild。

### GA4：Sparse fallback/optional provider

- capability/granularity matrix；
- independent sparse queue；
- no-sparse differential test。

## 13. 完成门槛

- 逻辑 64x64 page 不依赖 sparse block；
- stroke shader 普通路径没有全局 PageKey hash lookup；
- binding snapshot 在使用期间不可变且按 ticket 退休；
- slot ABA 和 stale ProviderEpoch 可检测；
- 每个支持格式有 CPU/GPU codec golden；
- atlas 删除不会丢 canonical 内容；
- no-sparse 设备拥有相同 PageStore/lease/undo/save 语义；
- memory trace 区分 logical、charged、padding、metadata 和 transient bytes。
