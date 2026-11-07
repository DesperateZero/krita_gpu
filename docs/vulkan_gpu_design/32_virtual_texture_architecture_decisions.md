# 虚拟纹理架构决策总纲

> 本文冻结虚拟纹理的算法族、接口边界与文档路由。项目状态和 MVP 边界服从
> [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md)，全局 P0 架构服从
> [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)，唯一实施顺序服从
> [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md)。本文不表示相关代码已经实现。
> 2026-09-20 补充：resident CPU 快路径和 production epoch layout 属于冻结架构，不是事后 micro-optimization；
> 执行与门禁见
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)；2026-09-21 起写侧条件
> COW、backing handoff、硬预算和零冗余复制定义服从
> [68](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md)。

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
11. 单一 canonical 模型允许 resident native data plane 与 generic async control plane 两种执行粒度；这不是双 authority。
12. virtual default 不按逻辑坐标物化页面；CPU/GPU 读共享 format/default-generation 匹配的只读 backing。
13. 每个显式 mutation/batch 的同一未发布段，对同一页只做一次 first-write transition/COW/seal；per tile lock 或 per dab
    提交被拒绝。需要中间可见性时显式分段，不能跨已发布段沿用旧可写授权，也不能把 history transaction 自动当成单一段。
14. production epoch 使用 persistent root/changed-page delta；reference `QHash/QVector/sort` 不得成为产品布局。
15. GPU/UMA 是可按 operation 选择的 executor，不是“硬件存在即优先”的 storage mode。Auto route 以同机成熟 CPU
    product path 为性能基线，在首次写入前冻结，并服从 39 的 CPU-relative gate 和迟滞。
16. 零拷贝只证明迁移字节，不证明加速；shared-memory 带宽、GPU kernel、queue 或 cache maintenance 不利时必须走 CPU。
17. VT 管理对主干 tile 的 M 证据与 VT/RAM Tile 吞吐、延迟的 K/E 证据分别验收，再以同 workload 的 X/E 关键路径整合。
    GPU direct/VT 必须同 executor/domain；GPU/VRAM 对 CPU/RAM 只给异构性能比，不能归因为管理成本。定义统一见 39 的 5.6–5.9。
18. route 比较以当前 exact valid replicas 和相同交付 endpoint 为条件，产品比较以完整外部任务为边界；CPU 可用性不等于
    RAM 已就绪。不得遗漏 fallback 读回或为 GPU 强加无用读回，也不得以阶段时长/P95 求和代替端到端实测。
19. CPU/CpuRam 同义管理以主干 Tile 等价或更优为目标；M 独立通过 39 的预冻结容差/配对不劣性判据，不能用完整操作
    1.2×/1.3×/1.5× 阶段上限替代。服务于同义操作的内部记账仍计入 M，真正新增语义单列预算且保留在 E。
20. resident read 依据所需 exact generation 的 CPU-readable valid replica 是否 ready 且可安全 pin；cache miss、历史
    标签、非 CPU authority 不单独触发通用 materialization。读侧快路径不放宽写侧 handoff/COW/permit。
21. UMA 同一已驻留、布局兼容 backing 的 CPU↔GPU payload migration 为零，不是全部硬件/同步成本为零；无 GPU
    交接需求的 CPU-only 路径不执行无用 GPU 协议。必要执行依赖、实际新增语义与可消除软件冗余分别计量，不互相免责。

这些是设计目标与约束，不是性能通过声明；跨文档摘要和报告判词以
[39 的 5.11](39_virtual_texture_performance_gates.md#511-统一口径速查与报告判词) 为准。M/K/X/E 不构成可相加的时间恒等式。

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

resident CPU 是同一模型的缩短路径：operation 先捕获一次 retained root，随后以 epoch-tagged cached handle 做
page-local pin/version validation；virtual default 返回匹配 captured view 的 format/default revision 的共享 view。
cached handle miss 先在受保护 root 中 resolve；retained 历史或非 authority 的 ready exact CPU 副本同样可 native pin。
只有缺少适用就绪副本、需要异步 producer/访问交接、swap-in/跨域/I/O 时才建立上面的通用 request/materialization DAG。
无效 capability/version 显式失败，不能伪装成迁移；resident hit 不分配 heap request、不插入 global map、不扫描 provider leases。

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

CPU/UMA/GPU mutation 都遵守 first-write 规则：同一 page/batch 的未发布段只 reserve G+1 一次并复用 writable replica。
中途发布后开启新段并重新选择 write plan，不沿用旧授权。物理 allocation 复用由 PageStore 私有 `KisPageWriteCoordinator` 的内联 plan
选择 `HandoffRecoverable` 或 `HandoffCommitOnly`：前者证明旧 G 有 exact recoverable backing，后者要求 old-root
capture/read gate、完整预检和首字节后不可失败发布链。调用方/provider 不持有公共 permit；多页 Prepared batch 不能仅因
当前无 reader 就覆盖旧 G。production metadata 先使用 shard-owned generational slot arena 和 allocation-free publication；
handoff 不得以每 generation plan/binding 堆对象换取 payload 零分配。算法边界一次 commit，
tile unlock/per dab completion 不是 epoch 边界。

executor route 发生在 acquire write/begin mutation 前。成本模型同时估计实际 CPU product path 与完整 accelerator
end-to-end cost；只有带风险余量仍有收益的 bucket 才 `AutoPreferred`。route 冻结后同一 stroke/operation 不按 dab/page
混用 executor；故障通过 abort/replay 恢复。GPU 劣势设备或状态保持 CPU route，不影响 PageStore 仍拥有同一 authority。

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
- virtual default、native resident guard、two-stage write intent/guard、PageStore 私有 write-plan 与条件 backing handoff；
- current/history/pending/in-flight/retiring/optional backing 的 owner ledger、硬预算、压力状态机与背压；
- persistent epoch root、changed-page delta 与增量 extent；
- CPU-relative execution profile、operation-level route freeze、risk margin/hysteresis 和 regret demotion；

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
| [68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) | BR1 write-plan、条件 COW、allocation handoff、硬 backing 预算与清理顺序 |
| [69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md](archive/br1_pre_m6_20260925/documents/69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) | BR1 PageStore 类拆分、重复 owner 清理、外部侵入审计与删除门槛 |
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
| BR1 | 33/52/68 的 CPU reference + production persistent root、PageStore、virtual default、resident guard、条件 backing handoff/必要 COW、硬 backing 预算、RAM/SSD identity |
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
- resident CPU 每次 tile lock 走 generic request/resolve/global map；
- production commit 重建/排序完整 reference manifest，或由 tile unlock 触发提交；
- 仅凭 Vulkan/UMA capability 或零拷贝计数强制 GPU route，忽略同机 CPU 实际性能；

## 8. 架构完成定义

只有同时满足以下条件，才能称虚拟纹理架构闭环：

- 33–38 的 reference model、故障注入和 production provider 共用相同 transition 语义；
- UMA 同一兼容驻留 shared backing 的真实 CPU↔GPU 交接中 payload migration count/bytes 为零，证据与例外见 39 的 5.7；
  不能由此推出必要同步/总耗时为零或授予 M/K/E Pass；
- dGPU 小预算下自动完成 VRAM/RAM/SSD 往返且 generation/checksum 不变；
- 默认页、COW、undo、save、cancel 与旧 Krita CPU 语义一致；
- 当前目标、预测 corridor、非目标 CoverageCertificate 真实驱动 residency；
- 任何缺页、I/O、queue 或预算压力都不在 UI/input thread 形成无界等待；
- 所有性能结论通过 39 定义的完整 trace，而不是单个 copy/shader microbenchmark；
- 旧 TileManager/TileCache/Prefetcher/Tier runtime 已从 production tree 消失。
