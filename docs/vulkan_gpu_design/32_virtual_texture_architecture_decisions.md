# 虚拟纹理架构决策总纲

> 本文冻结虚拟纹理的算法族、接口边界与文档路由。项目状态和 MVP 边界服从
> [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md)，全局 P0 架构服从
> [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)，唯一实施顺序服从
> [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md)。本文不表示相关代码已经实现。

## 1. 决策结论

虚拟纹理基线固定为：

```text
Krita 64x64 logical PageVersion
        |
        v
sharded canonical PageStore
        |
        +-- CpuRam replica
        +-- UmaShared buffer-slab replica
        +-- DiscreteVram buffer-slab replica
        +-- Ssd segment-record replica
        +-- optional exact sampled-atlas replica
        `-- derived checkpoint/display page

GPU consumer
        <- immutable operation-scoped PageBindingTable
        <- exact-generation lease/ticket

ResidencyController
        <- safety eligibility
        <- semantic class
        <- cost/byte + CLOCK-style history
        <- budget/deadline/backpressure
```

永久决策：

1. canonical identity 是 `SurfaceId + LogicalPageId + Generation`，不是 Vulkan image、allocation 或 SSD chunk。
2. VRAM、RAM、UMA、SSD 不是互斥 `Tier`；同一 generation 可以同时拥有多个 valid replica。
3. logical page 永久服从 Krita 64x64 tile；物理 slot、transfer batch 和 sparse block 可以有不同粒度。
4. writable/exact page 的基线表示是固定槽位 buffer slab；sampled atlas 是辅助 exact replica 或 derived view。
5. stroke 和已规划 composite 使用作业级已解析句柄，不在 shader 热路径查询全局可变 hash page table。
6. UMA 指针旁路表示 CPU pointer 与 GPU handle 访问同一物理页，不要求两种地址数值相等。
7. SSD 使用 `kritaimage` 中唯一的 append-only segmented store；Vulkan backend 不拥有第二套 swap/L3。
8. 淘汰先经过安全资格，再经过绘画语义分级，最后才使用成本与访问历史排序。
9. native sparse resource 只能是可选 provider 优化，不得成为功能正确性、页面身份或 MVP 的前提。
10. 所有阈值都来自 trace/benchmark；阈值不得进入 PageStore 公共 ABI。

## 2. 方案评分和取舍

评分用于架构排序，不代表当前代码性能。权重为：语义正确性 25、热路径延迟 20、带宽/容量 15、Krita
集成 15、可移植性 10、故障可测性 10、维护成本 5。

### 2.1 物理表示

| 方案 | 分数 | 决策 |
|---|---:|---|
| 完整 `VkImage` per surface | 44 | 删除，不满足大画布/多图层预算 |
| native sparse image 作为 canonical | 58 | 删除，设备粒度和格式反向污染逻辑页 |
| image atlas 作为唯一 page store | 74 | 只作辅助读取/显示副本 |
| storage-buffer slab + software mapping | 90 | 基础实现 |
| provider-specific buffer + optional sampled atlas | **94** | 主路径 |

### 2.2 GPU 寻址

| 方案 | 分数 | 决策 |
|---|---:|---|
| 全 surface 稠密页表 | 58 | 不适合稀疏大图层 |
| 全局 GPU hash table | 72 | 只允许慢路径/实验 |
| 两级稀疏目录 | 84 | 非局部访问后备 |
| operation-scoped resolved handles | 91 | stroke/composite 热路径 |
| direct handles + local table + sparse fallback | **95** | 主路径 |

### 2.3 状态并发

| 方案 | 分数 | 决策 |
|---|---:|---|
| 全局 PageStore 大锁 | 48 | 删除 |
| 每页独立 mutex | 75 | 不作为最终模型 |
| 全 lock-free 状态机 | 60 | 证明和恢复复杂度不值得 |
| 单 actor 串行所有页面事件 | 78 | 可作 reference，不作 production |
| 分片 map + 短临界区 transition | **93** | 主路径 |

### 2.4 外存与温度

| 子系统 | 被拒绝方案 | 选定方案 | 评分 |
|---|---|---|---:|
| SSD | mmap window + 可变 chunk | append-only segment + generation index | 92 |
| dGPU migration | per-fault submit/固定页数 batch | deadline-aware byte batch + reserve | 94 |
| temperature | age/LRU 或单全局分数 | safety + semantic class + cost/CLOCK | 95 |
| prefetch | viewport 或无限线性外推 | 有界轨迹 corridor + deadline/expiry | 91 |

## 3. 端到端访问模型

### 3.1 Read

```text
consumer requests exact PageVersion + AccessDomain + deadline
-> PageStore checks valid replicas and existing in-flight materialization
-> select source by measured completion ETA
-> deduplicate or create migration DAG
-> target provider publishes ValidReplica after completion validation
-> resolve immutable ReadLease
-> consumer submits work with readiness ticket
-> release lease after last-use ticket
```

读取不能根据 `Tier` 猜测数据是否存在，也不能把缺页当透明像素。

### 3.2 Write

```text
acquireWrite(PageKey)
-> reserve single writer and WriteGeneration G+1
-> retain exact base/before generation G
-> prepare writable replica in requested domain
-> producer waits materialization/binding/previous-writer dependencies
-> producer completes
-> PageStore validates token/generation and marks G+1 Prepared
-> transaction/ImageEpoch manifest atomically publishes the complete page set
-> old generation remains for readers/undo or is retired safely
```

producer 失败或取消只终结 `G+1`，不得污染 `G`。

### 3.3 Evict

```text
budget crosses high water
-> cancel/expire speculative work
-> enumerate safety-eligible replicas
-> select semantic class
-> choose lowest retention value per byte
-> drop derived OR handoff canonical authority
-> unpublish mapping after users complete
-> retire physical slot after last-use ticket
-> stop after low water is restored
```

淘汰的是 replica，不是抽象 PageVersion。最后 authority 不能直接淘汰。

## 4. 冻结与可调边界

### 4.1 现在冻结

- Page/Generation/Replica/Lease/Ticket 身份；
- PageStore transition 与线性化点；
- provider capability 和失败契约；
- operation-scoped `PageBindingTable`；
- fixed-slot storage class slab；
- SSD record key、commit sequence 和 durability class；
- residency safety eligibility 和 semantic event/schema；
- `CoverageCertificate`/dependency vector；
- UMA 零 domain-copy 的计数口径；
- 所有资源按 last-use ticket 退休。

### 4.2 只允许测量后调整

- arena chunk/slot group 大小；
- local binding window/稀疏目录 leaf 大小；
- transfer batch byte threshold 和 deadline margin；
- atlas promotion/demotion 阈值；
- codec 选择和 raw escape 阈值；
- high/low water、minimum residence 和 cooldown；
- prediction horizon 和 soft-pin TTL；
- CLOCK hot/cold 比例与 ghost history 上限。

这些参数必须通过 capability/profile 或策略对象注入，禁止散落为 magic constant。

## 5. 专题文档路由

| 文档 | 权威范围 |
|---|---|
| [33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md) | 状态、线性化、分片并发、lease、事务可见性 |
| [34_virtual_texture_gpu_binding_and_arenas.md](34_virtual_texture_gpu_binding_and_arenas.md) | slot/slab、PageHandle、作业级绑定、atlas/sparse |
| [35_virtual_texture_uma_pointer_bypass.md](35_virtual_texture_uma_pointer_bypass.md) | UMA allocation、CPU/GPU ownership、cache maintenance、COW |
| [36_virtual_texture_dgpu_migration.md](36_virtual_texture_dgpu_migration.md) | VRAM/RAM 迁移、聚合、staging、eviction、backpressure |
| [37_virtual_texture_ssd_segment_store.md](37_virtual_texture_ssd_segment_store.md) | record、index、durability、codec、GC、恢复 |
| [38_virtual_texture_residency_temperature.md](38_virtual_texture_residency_temperature.md) | 安全资格、语义温度、CoveredCold、预测和公平性 |
| [39_virtual_texture_performance_gates.md](39_virtual_texture_performance_gates.md) | trace、成本模型、硬件矩阵、参数选择和验收门禁 |

[09_virtual_texture_status_and_roadmap.md](09_virtual_texture_status_and_roadmap.md) 继续记录现状与总体路线；本文和
33–39 负责目标算法。若旧专题中的抽象与 32–39 冲突，必须修订旧专题，不能实现两套模型。

## 6. BR 阶段归属

| 阶段 | 虚拟纹理交付物 |
|---|---|
| BR0 | 删除旧 runtime/Tier/LRU/direct sparse bind；加入静态守卫 |
| BR1 | 33 的 CPU reference、PageStore、COW、RAM/SSD identity |
| BR2 | ticket DAG、completion bridge、binding/allocation retirement |
| BR3 | 34–37 的 UMA/dGPU/SSD provider 和强制迁移闭环 |
| BR4 | 38 的语义温度、预测、CoverageCertificate 和公平性 |
| BR5 | stroke/undo/save 作为 lease/ticket consumer，验证热路径 |
| BR6 | display/WSI consumer 和完整产品性能门禁 |

BR1 可以实现 SSD reference store，但 Vulkan provider 只能在 BR2 coordinator 完成后进入 production。BR4
策略不得直接修改 provider 状态，仍通过 PageStore operation/ticket 执行。

## 7. 明确拒绝的长期方向

- `L1/L2/L3` 单枚举描述页面真相；
- 以 dirty bool 代替 generation/authority；
- 每个 dab 或每次缺页单独 queue submit；
- 通过 UI canvas/global router 查找当前文档 backend；
- 让 shader 在热路径探测可变全局哈希页表；
- 把 host-visible staging 宣称为 UMA canonical；
- 每页一个 `VkBuffer`/`VkDeviceMemory`；
- SSD 每页 fsync 或立即读回校验；
- generic LRU 直接决定 dirty canonical page 淘汰；
- 用 native sparse 不支持作为关闭虚拟纹理功能的理由；
- 通过保留旧 runtime 形成“双轨过渡”。

## 8. 架构完成定义

只有同时满足以下条件，才能称虚拟纹理架构闭环：

- 33–38 的 reference model、故障注入和 production provider 共用相同 transition 语义；
- UMA 稳态 canvas-pixel domain-copy 为零；
- dGPU 小预算下自动完成 VRAM/RAM/SSD 往返且 generation/checksum 不变；
- 默认页、COW、undo、save、cancel 与旧 Krita CPU 语义一致；
- 当前目标、预测 corridor、非目标 CoverageCertificate 真实驱动 residency；
- 任何缺页、I/O、queue 或预算压力都不在 UI/input thread 形成无界等待；
- 所有性能结论通过 39 定义的完整 trace，而不是单个 copy/shader microbenchmark；
- 旧 TileManager/TileCache/Prefetcher/Tier runtime 已从 production tree 消失。
