# GPU Stroke 与 UMA/dGPU/SSD Residency 连接

> 本文不重新定义统一页面系统；Surface/Page/Residency 的上位定义见
> [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md)，replica
> provider 见 [26_p0_replica_uma_dgpu_ssd.md](26_p0_replica_uma_dgpu_ssd.md)。本文只细化 stroke 如何通过
> lease、温度、预取和 ticket 使用三类后端，且不感知物理驻留位置。
> 虚拟纹理算法已经在 [32_virtual_texture_architecture_decisions.md](32_virtual_texture_architecture_decisions.md)
> 冻结；PageStore、binding、UMA、dGPU、SSD、温度的具体实现分别服从 33–38，本文不定义另一套策略。

## 1. 边界

Stroke 子系统可以声明：

- 哪些 target page 将写；
- 哪些 source/resource page 将读；
- 预计首次使用 deadline；
- 当前笔迹轨迹和 halo；
- 页面角色、重建成本和完成 ticket。

Stroke 子系统不能：

- 直接 bind/unbind sparse page；
- 自行分配 VRAM/RAM/SSD backing；
- 选择 staging buffer；
- 等待 transfer queue；
- 修改 residency tier；
- 在 page fault 时丢弃 PageJob；
- 把后端物理 page 大小泄漏到 brush shader 语义。

ResidencyController 决定物理位置和迁移；PageStateMachine 决定 generation/authoritative 状态；
SubmissionCoordinator 决定执行依赖。

## 2. Stroke 访问计划

### 2.1 `StrokeAccessPlan`

PageWorkCompiler 在提交前产生：

```text
StrokeId / BatchId
ReadSet
WriteSet
ReadHaloSet
ImmutableResourceSet
Deadline
PriorityClass
ExpectedReuse
PredictedNextRegion
```

每个 entry 包含：

```text
SurfaceId / PageId
requiredGeneration
access mode
domain（CPU/GPU）
role
deadline
estimated hold duration
```

### 2.2 Lease 获取

- `acquireRead()` 返回精确 generation 的 read lease 或 future ticket。
- `acquireWrite()` 预留 pending generation，并返回 write lease、previous writer 和 before-image requirement。
- lease 请求本身不要求页面已经驻留。
- compiler 可以继续编译其他 batch；submission 等待 lease/residency ticket。
- lease 失败必须让 batch 显式 Failed，不能降级成透明空页，除非 PageStore 确认该页本来就是规范化空白页。

### 2.3 Pin

- 当前 batch target page 在 write lease 生效到 writer ticket 完成期间强 pin。
- 笔迹预测 halo 使用有期限 soft pin，错误预测可撤销。
- before-image、in-flight transfer 和 CPU mapped lease 有独立 pin reason。
- pin 是引用计数/原因集合，不能用一个 bool 被另一模块错误清除。

## 3. 页面版本与权威状态

推荐每页维护：

```text
PublishedGeneration
WriteGeneration
AuthorityReplica
ValidReplicas[domain, generation]
LastWriterTicket
InFlightTickets[]
ReadLeases / WriteLease
PinReasons
ResidencyPolicyHandle / SemanticClassSnapshot (non-authoritative)
SsdRecord
DependencyGenerations
```

典型 GPU stroke：

```text
Published G
  -> reserve Pending G+1
  -> ensure write location and before-image
  -> submit writer waiting on LastWriterTicket
  -> signal StrokeTicket
  -> validate operation/generation
  -> mark page G+1 Prepared
  -> atomically commit batch ImageEpoch manifest
  -> later establish Recoverable G+1 or retain journal+before-image
```

“GPU 已写”与“CPU 可读”“可淘汰”“可恢复”是不同状态，不能由一个 dirty bool 表示。

## 4. 绘画感知温度

最终温度算法见 [38_virtual_texture_residency_temperature.md](38_virtual_texture_residency_temperature.md)。以下角色和输入是
Stroke 侧产生的语义事件，不是可独立修改 PageStore 的打分器。淘汰必须先通过 safety eligibility，再进入语义类和
cost/CLOCK history 排序。

### 4.1 角色优先级

Stroke 相关页面至少分：

1. `CurrentWrite`：当前 target、正在执行的 output 和必要 before-image。
2. `PredictedWrite`：轨迹/速度/方向/半径推导的近期 halo。
3. `VisibleExact`：viewport 所需 lower/upper/display exact dependency。
4. `ReplayOrCheckpoint`：即将参与 composite/replay 的 source/checkpoint page。
5. `UndoOrSaveRetention`：未提交 transaction、undo 或 immutable save 引用。
6. `CoveredCold`：有有效 checkpoint/cache 覆盖的非目标 canonical page。
7. `OffscreenCold`：不可见、非目标、低依赖。
8. `DerivedDiscardable`：可由 canonical generation 重建。

### 4.2 策略输入

```text
role priority
deadline
viewport visibility
distance to predicted trajectory
brush radius / spacing / speed
dirty writeback cost
SSD restore latency
rebuild cost
dependency fanout
cache coverage
last use with hysteresis
pin/in-flight state
```

温度只决定候选顺序，不覆盖安全规则。dirty、pinned、in-flight 或最后权威副本不能因分数低被直接回收。
`CoveredCold` 只有在 GraphEpoch、ActiveTargetSet、property/source generations 和 replay route 组成的
`CoverageCertificate` 有效时成立。

### 4.3 轨迹预测

- 根据最近输入方向、速度、笔刷 conservative bounds 和 spacing 产生有限 horizon。
- horizon 以 materialization/scheduler P95 和 safety margin 推导；corridor由有界速度/曲率轨迹与 brush/filter halo
  做 Minkowski sum。
- 只提交 prefetch hint，不提前创建文档 generation。
- predictor miss 不影响正确性，只增加 residency wait。
- predictor 不能无限 pin 沿整条延长线的页面。
- 笔刷停止或方向突变时撤销过期 soft pin。

## 5. UMA 后端

### 5.1 Canonical page

- 页面位于少量大块、持久映射的 shared buffer arena。
- CPU pointer 和 GPU buffer offset 指向同一物理像素数据。
- PageStore 维护 canonical generation/lease/authority；UMA replica provider 维护 fixed-slot suballocation 和
  direct/local binding；BDA 不是唯一实现。
- sampled image/atlas 只作为 derived display/resource cache。

### 5.2 GPU 写

```text
CPU leases released
-> flush CPU dirty range（non-coherent）
-> GPU acquire/order dependency
-> StrokeCompute writes shared page
-> signal writer ticket
-> publish generation
```

### 5.3 CPU 读写

GPU 写后 CPU read：

```text
request generation G read lease
-> wait G writer ticket on background consumer
-> invalidate mapped range（non-coherent）
-> return pointer/span
```

CPU write 后 GPU read/write：

```text
CPU write lease
-> update pixels
-> flush mapped range（non-coherent）
-> release lease + publish generation
-> GPU submission waits CPU-release ticket/order
```

host-coherent 不取消 execution ordering；它只减少显式 cache maintenance。

### 5.4 UMA 禁止项

- 不把 host-visible command ring 称为画布零拷贝。
- 不尝试把 optimal/sparse image memory 当线性 CPU 像素。
- stroke end 不创建 image-to-buffer download。
- 同一 canonical page 不维护独立 CPU tile 镜像。
- display image 失效不影响 canonical page。

## 6. dGPU 后端

### 6.1 存储角色

- canonical identity 是逻辑 page generation，不绑定 RAM allocation。
- RAM 与 VRAM 是同一 generation 的 replica；GPU 写 publish 后 VRAM 可成为 authority。
- SSD record 是带显式 `SessionSpill`/`RecoveryCheckpoint` durability class 的同 generation backing replica，不是
  Vulkan backend 私有 L3。
- 页面状态记录哪一个 generation 在何处有效，不能用 L1/L2/L3 枚举隐含推断。

### 6.2 写入冷页

```text
SSD G -> async read -> RAM G
RAM G -> upload -> VRAM G
sparse bind/atlas/direct-local binding publish
before-image for G
previous-writer dependency
StrokeCompute -> VRAM G+1
```

所有箭头产生 ticket；host 不串行等待。若页面从未有内容，PageStore 提供规范化 clear generation，省略恢复。
迁移聚合按 byte/deadline/StorageClass 执行，不使用固定页数或 per-fault queue submit；详见
[36_virtual_texture_dgpu_migration.md](36_virtual_texture_dgpu_migration.md)。

### 6.3 Dirty writeback

- VRAM G+1 在 writer 完成前不能下载。
- download 目标 RAM allocation 在 completion/publish 前不能成为 valid G+1。
- generation mismatch 的迟到 download 被丢弃，不覆盖 RAM 更新版本。
- writeback 失败时 VRAM allocation 与 journal/before-image 保留，禁止 unbind/reuse。
- stroke end 不自动回写所有 dirty page；由 CPU consumer、eviction、recoverability policy 或后台水位触发。

### 6.4 Eviction

候选页必须同时满足：

- 无 active lease；
- 无 pin；
- 无未完成 writer/reader；
- 最新 generation 已有安全 backing，或 derived/discardable；
- binding/sparse unbind 有后续 consumer 可等待的 publish ticket。

顺序：

```text
select candidate
-> if dirty: download G + validate
-> publish RAM G / recoverable G
-> remove GPU mapping with sparse/direct-local binding ticket
-> after last-use ticket release VRAM allocation
```

## 7. SSD 后端

### 7.1 Record

该 record 属于 `kritaimage` 中由 `KisTileDataStore`/`KisSwappedDataStore` 演进的唯一 unified SSD store。
Vulkan backend 不创建 page pack/index。

```text
SurfaceId
PageId
Generation
FormatId
Codec
CompressedSize
UncompressedSize
Checksum
CommitSequence
```

### 7.2 写入

- 只有 RAM/UMA 中存在可由 CPU 安全读取且验证过的 exact generation，或先从 VRAM materialize出该 replica，才能
  发起 SSD write。
- RAM allocation 在 SSD completion/checksum publish 前保持有效。
- 同页新 generation 不取消旧 write 的物理完成，但迟到 completion 不能把旧 generation 设为当前。
- 空间回收/compaction 也使用 record generation 和引用计数。

### 7.3 读取

- index 查找必须匹配 requested generation。
- read、decompress、checksum 完成后才发布 RAM valid。
- checksum 失败进入 Failed/恢复路径，不返回透明数据。
- brush deadline 可以提高 read 优先级，但不能跳过校验。

### 7.4 SSD 与文档保存

Unified SSD segment 只服务运行时工作集和恢复，不替代 Krita 文件格式。保存捕获 canonical generation map，
serializer 通过 read lease 取得内容；不能直接把 SSD record 当文档正文。

运行时换出使用 `SessionSpill`；需要 crash recovery 的记录使用分组提交的 `RecoveryCheckpoint`。禁止每页 fsync；
完整协议见 [37_virtual_texture_ssd_segment_store.md](37_virtual_texture_ssd_segment_store.md)。

## 8. Residency Backpressure

资源不足时不能让各 allocator 独立超预算：

- ResidencyController 统一核算 canonical、snapshot、derived、brush resource、staging 和 in-flight allocation。
- 达到高水位先丢 DerivedDiscardable，再降温 CoveredCold/OffscreenCold。
- dirty writeback 达不到回收速度时，减少预测 prefetch、延迟新的 stroke batch admission，并报告压力。
- 当前 in-flight target page 不能被赶出；如果连必需 target lease 都无法满足，batch 明确等待/失败，不能漏画。
- journal backpressure 与 residency backpressure 使用不同指标，但由 StrokeCoordinator 汇总为可观测 latency。

## 9. Brush Resource 与画布竞争

tip/texture/mask 作为 immutable resource surface 进入统一预算：

- 当前 PreparedBrushProgram 的资源 pinned/read-hot。
- 最近 preset 可以 warm，但不能挤出当前 target/undo safety pages。
- resource 可从源文件/CPU image 重建时记录 rebuild cost，可作为 derived cache 回收。
- resource generation 在 journal 退休前不能不可恢复地删除。
- 独立 brush cache 不得绕过 ResidencyController 另设无限 VRAM 预算。

## 10. 实现路线

以下 `SR*` 是全局 BR3/BR4 内部工作包：BR1 canonical PageStore 与 BR2 coordinator 未通过前不得接入
production；SSD 工作必须演进现有 Krita swap，不得建立 reference 成真后的第二套 store。

### SR0：AccessPlan/Lease 接口

- StrokeAccessPlan、read/write lease、pin reason、deadline。
- CPU reference backend 模拟 async ready/failure。

### SR1：UMA

- shared buffer arena、direct/local binding、CPU pointer lease。
- coherent/non-coherent ordering 和 cache tests。
- Auto Round 直接写 canonical shared page。

### SR2：dGPU

- RAM/VRAM generation ledger。
- upload/download/sparse/direct-local binding ticket。
- dirty safe eviction 与极小 VRAM 测试。

### SR3：SSD

- unified segment/index/checksum/async I/O，对现有 `KisSwappedDataStore` 做 generation-aware 演进。
- RAM 极小预算、写失败和迟到 completion 测试。

### SR4：Temperature/Prediction

- role/deadline/hysteresis。
- trajectory halo 与 target pin。
- lower/upper cache coverage 输入。

### SR5：统一压力控制

- brush resource、snapshot、canvas、derived 和 staging 统一预算。
- journal/residency backlog trace。
- 持续绘画、平移、图层切换和 SSD 抖动测试。

## 11. 验收门槛

- Stroke compiler/executor 不出现 bind/upload/download/SSD 具体调用。
- UMA target canonical page 为共享映射页，stroke end 无像素 copy。
- dGPU target 在 VRAM/RAM/SSD 间迁移后 checksum/generation 一致。
- transfer/sparse/direct-local binding ticket 被 StrokeCompute 显式等待。
- dirty/pinned/in-flight/最后权威 page 永不错误回收。
- 当前目标与预测 halo 优先于非目标源页和可丢 derived cache。
- 资源不足时表现为有记录的 wait/backpressure，而不是漏画或数据丢失。
- SSD failure、checksum failure 和迟到 completion 保留最后安全 generation。
