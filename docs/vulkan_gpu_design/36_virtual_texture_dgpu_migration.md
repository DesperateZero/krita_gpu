# 虚拟纹理 dGPU Replica 迁移、批处理与 Backpressure

> 本文定义 DiscreteVram 与 CpuRam/SSD 之间的迁移算法。PageStore transition 见
> [33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md)，GPU handle/arena 见
> [34_virtual_texture_gpu_binding_and_arenas.md](34_virtual_texture_gpu_binding_and_arenas.md)，提交所有权见
> [27_p0_submission_threading_zero_blocking.md](27_p0_submission_threading_zero_blocking.md)。

timeline completion 语义参考 [Khronos Timeline Semaphores](https://docs.vulkan.org/tutorial/latest/Advanced_Vulkan_Compute/08_Asynchronous_Compute/03_timeline_semaphores.html)；动态 heap budget
只作为控制输入，参考 [VK_EXT_memory_budget](https://docs.vulkan.org/refpages/latest/refpages/source/VK_EXT_memory_budget.html)。

## 1. 目标

- GPU write 后 VRAM 可以成为最新 generation 的 authority。
- CPU、save、undo、SSD 和 GPU consumer 只 materialize 所需 exact pages。
- transfer、binding、compute 和 graphics 组成一个可验证 ticket DAG。
- 缺页按 deadline/bytes 合批，不逐页 submit。
- 预算压力不能丢失 accepted stroke，也不能在 UI/input thread 同步等待。
- 不支持 sparse 的设备具有完整功能。

## 2. dGPU replica 布局

基线：

- device-local storage-buffer slab 保存 exact writable page；
- RAM replica 保存 CPU 可访问、安全写回内容；
- sampled atlas 是按收益创建的辅助 exact/derived replica；
- sparse buffer/image 只作可选 provider；
- transfer staging 使用独立、可按 timeline 回收的 ring/slab；
- binding table 使用 immutable snapshot/publish ticket。

VRAM replica 不要求始终有 RAM 镜像。GPU 写完成后 VRAM 可以是唯一最新 authority，但必须保留使该 generation 可恢复的
before-image/journal，直到 RAM/SSD backing 建立或 transaction durability policy 允许释放。

## 3. Materialization 请求

```text
MigrationRequest
  OperationId
  PageVersionId
  source candidates
  target domain/capability
  StorageClassId
  bytes
  priority class
  deadline
  cancellation policy
  dependent consumer ids
```

相同 dedup key 的请求共享物理 producer。聚合器只处理 PageStore 已预留的 operation，不自行改变 replica state。

来源选择使用当前实际副本和完成端点的条件估计，计时/性能归因统一见
[39 的 5.6–5.9 与 8](39_virtual_texture_performance_gates.md#56-四类证据与基线配对统一定义)：

```text
SourceETA = calibratedCriticalPath(source -> target, {
    sourceReady, queueDelay, codec,
    bytes / effectiveBandwidth, bindingPublish, contention
})
```

同 generation 有 RAM 和 SSD 时通常选择 RAM，但不能把固定域优先级写死；拥塞或 codec 成本必须进入 ETA。
各项是模型特征，不是可直接相加的阶段 P95；来源完成分布由真实依赖关键路径校准。X 报告迁移本身，E 包含 consumer
交付成本；GPU remote-host 的内核访存不能冒充 resident VRAM，也不能在 K 已包含后再叠加估算传输耗时。CPU fallback
若无适用 RAM replica 同样承担必要读回，不能以 RAM-ready 内核时间替代该状态下的 CPU route 成本。

## 4. Deadline-aware batcher

### 4.1 分组键

请求优先按以下兼容性分组：

```text
direction (upload/download/device copy)
source/target provider epoch
StorageClass/codec
required queue family/ownership transfer
priority/deadline class
```

逻辑 PageId 不连续不妨碍合批。连续 physical ranges 可合并 copy region，但不能改变逐页完成与错误归属。

### 4.2 Flush 条件

满足任一条件提交：

```text
queuedBytes >= calibratedByteTarget
earliestDeadline - estimatedBatchDuration <= safetyMargin
high-priority CurrentWrite arrives
staging span would wrap/exhaust
explicit transaction/save flush boundary
```

不使用固定“每批 N 页”作为主决策。页数可以作为 command region 上限，值由设备 profile 决定。

### 4.3 优先级

从高到低：

1. 当前已接受 stroke 的 target/base/before-image；
2. 即将到期的 PredictedWrite；
3. 当前 viewport 的 exact composite/display dependency；
4. CPU/save/undo 显式 demand；
5. authority safety writeback；
6. speculative prefetch；
7. background derived promotion/compaction。

安全 writeback 在接近硬预算时提升到 current-demand 级，防止因长期不写回耗尽可回收 VRAM。

## 5. Staging 管理

```text
StagingSpan
  arena id / offset / size
  direction
  PageVersion list
  producer/consumer tickets
  last-use ticket
```

- upload/download 使用不同逻辑 lane，可共享 allocation 但不能覆盖未完成 span；
- ring wrap 前检查 timeline，不 host wait；无空闲 span时触发 backpressure 或增加有预算的 block；
- 每页拷贝结果拥有独立 validation metadata；
- non-coherent staging 按 atom 对齐 flush/invalidate；
- staging bytes 计入 transient/in-flight 预算，不能藏在 VRAM/RAM 统计之外。

对于小页，CPU packing 可以把多个页连续放入 span；GPU copy regions 再分发到各 slot。大格式页或连续 slot 可直接使用
多个 region，不强求重新打包。

## 6. 迁移 DAG

### 6.1 SSD cold page -> GPU write

```text
SSD exact G
  -> async read/decompress/checksum
  -> RAM exact G valid
  -> upload staging/copy
  -> VRAM exact G valid
  -> binding snapshot publish
  -> wait previous writer/resource tickets
  -> GPU writes reserved G+1
  -> writer ticket
  -> PageStore publish G+1
```

若页面是规范 default，PageStore/provider 使用 clear/init kernel 生成 exact base，不进行虚假 SSD read。

### 6.2 GPU write -> CPU/save

```text
VRAM exact G writer ticket
  -> reserve RAM target
  -> download batch
  -> invalidate staging/RAM mapping when required
  -> validate PageVersion/format
  -> RAM exact G valid
  -> resolve CPU/save lease
```

stroke end 不触发整笔回读。只有显式 CPU consumer、save、recoverability 或 eviction 发起 materialization。

### 6.3 VRAM eviction

```text
select safety-eligible replica
-> if another exact backing exists: skip writeback
-> else pin source and materialize RAM/SSD exact G
-> PageStore commits handoff/recoverability
-> remove handle from future binding snapshots
-> wait old snapshots/consumers
-> retire slot after last-use ticket
```

unbind/mapping removal和物理 free 是不同操作，均需 ticket。

## 7. Queue 与 ownership

所有 Vulkan queue API 由 SubmissionCoordinator 独占。一个 migration batch 描述逻辑依赖，不直接持有跨线程 queue。

需要表达：

- transfer write -> compute read/write；
- compute write -> transfer read；
- transfer/compute -> sampled graphics；
- queue-family ownership release/acquire；
- binding/sparse publish -> consumer；
- resource retirement -> last use。

同 queue family 和独立 transfer/compute family 必须运行同一语义测试。不能依赖 queue submission 偶然顺序或
`vkQueueWaitIdle`。

## 8. Emergency reserve

为了避免“释放内存需要先分配写回目标”形成死锁，每个 domain 预留：

- current target/COW output slots；
- 至少一个 authority handoff batch 的 staging/RAM/VRAM 空间；
- binding/descriptor/command metadata；
- SSD write pipeline 所需最小缓冲。

reserve 大小由最大支持 StorageClass、最大并发 current page set 和测量的 batch 决定。reserve 不供 speculative
prefetch、atlas promotion 或 background rebuild 使用。

## 9. Backpressure 顺序

当预算或 staging 不足：

1. 取消尚未提交的 speculative prefetch；
2. 过期 soft pin，停止新的 atlas promotion；
3. 丢弃安全的 DerivedDiscardable；
4. 提升 CoveredCold/OffscreenCold authority writeback；
5. 缩小未来 batch admission window；
6. 暂停 scheduler 接纳新的 GPU page batch，但 UI/input 只写入有界 journal，不 host-wait GPU；
7. journal 接近硬上限时由 stroke protocol 进入显式 pressure 状态，不能覆盖旧命令或漏 dab。

已经接受并 journal 化的 stroke command 必须最终执行、显式失败或通过恢复事务取消。不能因 residency pressure 静默丢弃。

## 10. Budget controller

分别跟踪：

```text
device-local exact replicas
sampled atlas/display
staging/transient
binding/descriptor metadata
in-flight retired-but-not-free
emergency reserve
driver-reported heap usage/budget
```

预算使用高低水位：越过 high water 启动回收，回到 low water 才停止。外部 heap budget 变化触发目标水位调整，但不能
直接同步驱逐当前 target。

公平性由 ResidencyController 分配 document/session share；SubmissionCoordinator 仍可按 deadline 跨文档调度。

## 11. 可选 direct paths

以下只能是 provider 优化：

- BAR/Resizable BAR 上 host-visible device-local replica；
- peer/device copy；
- native sparse bind；
- 平台特有 direct-storage/GPU decompression。

它们必须实现相同 operation/ticket/validation，并有基线 RAM staging fallback。任何 direct path 不能把 SSD record 或
GPU address 暴露给上层。

## 12. 故障矩阵

- VRAM allocation OOM：保持 source，触发回收/backpressure。
- staging allocation 失败：batch 不提交，request 保持等待或显式失败。
- transfer submission 失败：target 非 Valid，source authority 不变。
- device loss：ProviderEpoch 失效所有 VRAM/mapping ticket，从 RAM/SSD/journal 恢复。
- download 后 generation 已过期：该 exact historical replica可在仍有引用时保留，但不能覆盖当前 head。
- binding publish 失败：已复制 slot仍不能被 consumer使用，可安全退休。
- document close：拒绝新 request，取消未提交 batch，等待已知 ticket后释放。

## 13. 指标

- page faults by source/target/reason；
- dedup ratio；
- batch bytes/pages/regions；
- batch queue delay、copy time、binding time；
- deadline miss；
- bytes uploaded/downloaded per painted byte；
- staging stalls/growth；
- emergency reserve use；
- writeback debt；
- VRAM churn/reverse migration；
- last-use retirement lag；
- avoidable SSD read after recent eviction。

## 14. 实施顺序

### DG0：Fake migration scheduler

- ETA、dedup、deadline batch 和 failure tests；
- 无 Vulkan 的 deterministic trace simulator。

### DG1：RAM <-> device buffer

- staging ring/slab；
- upload/download ticket；
- same-family queue。

### DG2：Queue topology

- dedicated transfer/compute；
- ownership transfer；
- binding publish/retirement。

### DG3：Eviction/recoverability

- authority handoff；
- emergency reserve；
- high/low water/backpressure。

### DG4：Optional provider

- sampled atlas；
- sparse/direct paths；
- end-to-end benchmark gate。

## 15. 完成门槛

- per-fault/per-page queue submit 为零；
- current stroke target 不因普通预算回收被逐出；
- dirty VRAM 在安全 handoff 前不解绑/复用；
- 同/异 queue family 结果一致且 validation clean；
- 小预算随机迁移不丢 generation/checksum；
- CPU/save 只回读 exact demand pages；
- device loss 后旧 GPU handle 不可被复用；
- backpressure 不阻塞 UI/input thread，不丢 accepted dab。
