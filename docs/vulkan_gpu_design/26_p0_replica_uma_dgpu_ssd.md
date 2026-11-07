# P0：统一 Replica 模型——UMA、dGPU、RAM 与 SSD

> 2026-11-04 新版后端扩展设计：[105完整规范](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/UNIFIED_BACKEND_DESIGN.md)。多副本、真实跨域传输与唯一SSD保留；改用按操作能力和同一内容/物理寿命。 当前只完成设计，CPU产品0fd96保持；不据此声称GPU/完整能力已实装。旧实现名称不能覆盖105的目标责任，未迁消费者在原矩阵追踪。

> 本文定义同一 canonical PageVersion 在不同物理域的 replica。Canonical identity 和不变量见
> [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md)。
> 物理 binding、UMA、dGPU、SSD 和温度的实施算法分别见
> [34_virtual_texture_gpu_binding_and_arenas.md](34_virtual_texture_gpu_binding_and_arenas.md)–
> [38_virtual_texture_residency_temperature.md](38_virtual_texture_residency_temperature.md)。allocation ownership transfer、条件 COW 与
> backing硬预算见[92当前合同](92_br1_m6_m8_execution_baseline.md)；M6机会型能力与GPU预测按其§6及[39 §10.1.1](39_virtual_texture_performance_gates.md#handoff-value-gates)分别验收。

## 1. Replica 不是 Page

```text
PageVersion = SurfaceId + LogicalPageId + Generation + DefaultPixelRevision

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

性能记录须把 executor、逻辑 ReplicaDomain、physical backing/access path 分开：CPU/CpuRam、CPU/shared、GPU/shared、
GPU/local-VRAM、GPU/remote-host 与 CPU/BAR-mapped 分桶。UMA 共享 allocation、host-visible/device-local 标志均不证明
与原生 RAM 的吞吐/延迟相同。管理对主干 tile、同域算子、跨域交付及产品对照统一按
[39 的 M/K/X/E 标准](39_virtual_texture_performance_gates.md#56-四类证据与基线配对统一定义)，不能用异构内核倍率证明管理效率。

## 2. `PageReplicaProvider`

定义在 `kritaimage` 的 backend-neutral interface：

```text
capabilities()
requestReplica(PageVersion, Domain, AccessMode, Priority)
prepareWrite(PageKey, WriteGeneration, Domain)
prepareSynchronousWriteCopy(Operation, ExactSource, TargetVersion, Descriptor, Priority) // optional
transfer(SourceReplica, TargetReplica)
validate(Replica, Generation)
retire(Replica, CompletionTicket)
memoryUsage()/budgetSignals()
```

实现：

- CPU/RAM/SSD provider 位于 `kritaimage`；
- Vulkan UMA/dGPU provider 位于 `kritavulkanbackend`；
- PageStore 选择 provider/迁移并提交 authority handoff；
- consumer 获得 PageStore 授权的 lease 或 resident native guard，不直接调用 provider；native record 不向调用方授予独立 authority。

两类访问须共用可验证的 read/write/transfer/retire 寿命协调；generic lease map 为空不证明 native pin 已释放。
root retention、physical pin 与异步 last-use 分别保护不同寿命，alias 同一 payload 的多个 allocation record 不可各自
宣称物理独占。D8 CPU guard落实与回归/写侧反证见[62](archive/br1_pre_m6_20260925/documents/62_br1_native_resident_read_and_write_cost_20260920.md)，
后续按需cache及冷热/真写反证见[63](archive/br1_pre_m6_20260925/documents/63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md)。D10分离暖查询/冷发现，
保留shared gate且冷miss多一次shard查询；局部暖读改善和未关闭的冷读/真写残余见
[64](archive/br1_pre_m6_20260925/documents/64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md)。当前状态见52的1.14/11，验证/成本边界见39的5.12；
容器析构已测不等于provider异步工作全部drain，更不据此授予UMA/dGPU实现或性能资格。

BR1 D4 已为 tiles3 接入可选 `synchronousWriteCopy` 能力：同 provider/epoch、同 CPU 域 preserve 直接从 exact immutable
source 初始化独立新 allocation，避免 default-fill 后再 transfer。未具备能力时在执行前选择旧路径；已执行失败不静默
重试。Ready/terminal completion、source lifetime/pin、active writer 拒绝、目标 generation/layout 与锁外调用后的复验
不省略。它不是原位写权限或 authority handoff，也不自动授予 UMA/dGPU 能力；默认实现 Unsupported，详见
[58](archive/br1_pre_m6_20260925/documents/58_br1_native_cow_initialization_and_payload_accounting_20260920.md)。

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

<a id="recoverable-backing-handoff"></a>
### 3.1 M6可恢复backing复用与副本来源

§3的同generation副本物化/authority转移与M6不是同一个转换。M6把物理A从G0解绑、retag后写G1，同时用已Ready、内容/layout匹配且物理独立保活的B恢复G0：`G0:{A,B} → G0:{B}, G1:{A′}`。B不自动升级为G1的before；新发布边界后再次复用须重新证明资格，同一未发布段则使用pending。

CPU上传GPU后，若业务本来就保留CPU exact G0，且GPU exact G0已Ready、旧last-use完成，可能自然提供一次GPU backing复用机会。这是后继设计条件，不是当前实现：当前M6发现/写入只接resident CpuRam，Vulkan native分配、传输和写入仍待BR3。不能为制造命中额外整页复制或逐代读回；需要额外保留的容量、迁移、恢复及退出成本须计入业务净收益。

同一UMA allocation的CPU pointer与GPU handle、两个alias记录均不算两个独立before。derived display、不同generation和in-flight transfer也不能授予资格。A仍有实际reader/pin/source/last-use时不能覆盖；已有GPU命令不会因metadata retag自动改为读取B。B自己的读者保护继续保留，取消后旧G经B可解析。算子若要求独立旧输入，不因复用物理页而获得原地执行资格。

显存压力下避免新增payload可能有价值，但不会自动节省PCIe传输、驱动分配或池的reserved容量；旧页在途读取时还可能失去Fresh的并行机会。能力、容量与真实业务延迟分别按[92 §6.1–§6.3](92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)和39验收，不外推CPU收益率，也不扩大同步commit-only白名单。

## 4. UMA Shared Replica

### 4.1 Arena

- 少量大块持久映射 buffer allocation；
- host-visible、device-addressable，满足目标设备内存类型；
- PageVersion 映射到 arena allocation id + byte offset；
- CPU tile view 与 GPU opaque handle/device address 访问同一物理像素；两种地址数值不要求相等；
- allocator 遵守 format alignment/non-coherent atom size；
- allocation 直到全部 lease/native guard、physical pin、ticket/reference 满足释放条件后回收。

### 4.2 与现有 tile/COW 集成

- `KisTileData`/CPU tile view 可以由 shared arena backing 提供 data pointer；
- 旧 PageVersion 仍可观察或 mutation 可取消/失败时，COW 分配新 shared page，旧指针继续有效；PageStore 证明
  recoverable/commit-only handoff 条件时，同一 allocation 可原子重绑定到新 generation；
- iterator 不知道 Vulkan，只使用 CPU lease pointer/stride；
- GPU direct/local binding snapshot 由 Vulkan provider建立并发布 ticket；
- PageStore 保持 generation/authority，Vulkan provider不改 tile history。

shared arena 只定义物理可共享性，不保证性能资格。resident CPU view 必须复用 52 的 cached handle + page-local pin 快路径；
GPU/UMA executor 只有通过 39 的同机真实 CPU-relative `AutoPreferred` 门禁才进入产品 route。若 shared mapping 的 CPU hot
access 退化，则 CpuRam 继续作为 CPU authority、UmaShared 只作 GPU replica；零像素 copy 不能覆盖 cache/bandwidth/queue
劣势。

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

所需 exact bytes 已位于同一已驻留、布局兼容的 shared backing 时，UMA canonical path 的稳态 CPU↔GPU domain
synchronization 画布像素 copy count/bytes 必须为零：

- 不做 image→staging→KisTileData；
- 不做 KisTileData→staging→canonical image；
- COW/undo snapshot 是语义需要的 version copy，不计作 domain synchronization copy，但必须单独统计；合法 backing handoff
  计 payload retag，不计 copy，也不能隐去必要 cache/order 和 metadata 工作；
- display/sample atlas 是 derived copy，单独统计，不能伪装 canonical zero-copy。

零迁移不等于零同步、零 DRAM/cache 流量或零 queue/ticket 等待，也不包含 SSD 换入。CPU-only 且没有 GPU 访问交接时，
不能仅因 backing 可共享而执行 GPU binding/submit/ownership 协议；有真实交接时必须保留必要 ordering/cache maintenance。
CPU/CpuRam 同义管理仍按 39 的 5.6 证明不劣于主干；实际新增语义、硬件/执行依赖和软件冗余分别归因，不能以 UMA 标签
把开销记零，也不能把所有软件残余归为硬件必然开销。
按 [39 的 5.11](39_virtual_texture_performance_gates.md#511-统一口径速查与报告判词)，零迁移证据必须覆盖真实交接及
同一 allocation/exact generation/布局/驻留；CPU-only 未交接为 `NotApplicable`，覆盖缺失为 `NotMeasured`。
CPU/RAM 与 CPU/shared、GPU/shared 与 GPU/local-VRAM 的访问成本分别测，不因共享物理内存而宣称读写等速。

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
- UMA canonical CPU/GPU 使用同一兼容驻留物理页，真实交接的 payload migration count/bytes 为零；按 4.4 与 39 的 5.7
  提供适用条件和计数覆盖，不代表必要同步或总耗时为零，CPU-only 未交接不构成 UMA Pass。
- shared CPU access 对 native CpuRam/upstream 达到 39 的门限；CPU-only/forced UMA/forced dGPU/Auto 在劣势 profile 完成
  同质量端到端对照，未达标 bucket 在首写前路由 CPU。
- dGPU VRAM/RAM authority handoff失败保留旧authority。
- SSD只使用升级后的Krita统一store，无Vulkan独立L3。
- 64×64 logical tile不再等同sparse block。
- sparse/no-sparse设备使用同一上层状态机。
- VRAM→RAM→SSD→RAM→VRAM checksum/generation一致。
- 所有迁移、sparse bind、direct/local binding publish通过ticket DAG。
- lease/pin/in-flight/authority安全规则在压力和故障下成立。
