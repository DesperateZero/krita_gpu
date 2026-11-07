# 虚拟纹理 UMA 指针旁路与一致性方案

> 2026-11-04 新版后端扩展设计：[105完整规范](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/UNIFIED_BACKEND_DESIGN.md)。shared backing与cache/order合同不变；同一provider的CPU同步/GPU异步能力、物理保护及费用共同归属新协议。 当前只完成设计，CPU产品0fd96保持；不据此声称GPU/完整能力已实装。旧实现名称不能覆盖105的目标责任，未迁消费者在原矩阵追踪。

> 本文定义 UMA shared replica 的物理与同步语义。PageStore 状态见
> [33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md)，GPU slot/binding ABI 见
> [34_virtual_texture_gpu_binding_and_arenas.md](34_virtual_texture_gpu_binding_and_arenas.md)。
> BR1 resident CPU 快路径冻结的局部 pin、mutation session 和 virtual default 原则也适用于 UMA，见
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)；条件 COW、shared backing
> handoff 和硬预算服从 [68](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md)。UMA 不能以共享
> allocation 为由恢复 per-access request/map/scan。

mapped memory 的 flush/invalidate 和 `nonCoherentAtomSize` 约束以
[Vulkan memory specification](https://docs.vulkan.org/spec/latest/chapters/memory.html) 为准。

## 1. 能力定义

UMA MVP 能力必须同时满足：

1. canonical PageVersion 的 exact bytes 位于 CPU 可映射且 GPU 可读写的同一物理 allocation。
2. CPU iterator 获取稳定 lease pointer/stride；GPU 获取 opaque handle/descriptor/address。
3. CPU/GPU 访问通过 lease、execution ordering 和 cache maintenance 串行化。
4. 同一已驻留、布局兼容的 shared backing 上，稳态 CPU↔GPU domain synchronization 的 canvas-pixel copy count/bytes 为零。
5. sampled atlas/display copy 单独计数，不能冒充 canonical 零复制。
6. shared allocation 上的 CPU 热路径和 GPU executor 分别通过同机成熟 CpuRam/CPU-only 的相对性能门禁；零拷贝本身
   不能使较慢路径获得产品资格。

CPU pointer 和 GPU address 不需要数值相同；“pointer bypass”指绕过像素上传/下载管线。
它不保证同步/cache maintenance、queue/ticket 或执行等待为零，也不消除 COW/undo、SSD 换入和 derived/display copy。
CPU-only 且无需 GPU 访问交接时不得额外执行 GPU binding/submit/ownership；真正交接的必要成本则必须计量，不能删掉。
CPU 同义管理以主干等价或更优为目标，独立通过 39 的 5.6 不劣性判据；下文 shared mapping 的退化上限不是 M 等价容差。
因此不能笼统宣称“UMA 硬件存储事实开销为零”：上述条件只排除 payload 搬运，不证明 CPU/GPU 读写等速或 E 差值为零。
映射访问性能由 K/同路径 resident E 配对，交接由 X/完整 E 验证，管理由 M 验证；未解释的软件成本不归给硬件免责。

报告统一写“同一兼容驻留 backing 的 CPU↔GPU payload migration copy count/bytes 为零”，不写无条件的“UMA 额外时间为零”。
零迁移证据须包含真实访问交接、allocation/exact generation 与布局/驻留证据及完整 copy 计数范围；CPU-only 没有发生
交接为 `NotApplicable`，缺少硬件/计量证据为 `NotMeasured`，均不构成 UMA Pass。零复制功能证明与 M/K/X/E 性能资格分开；
统一判词与 CPU/dGPU 对照边界见 [39 的 5.11](39_virtual_texture_performance_gates.md#511-统一口径速查与报告判词)。

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

若同一物理类型 GPU 性能不达门禁，该设备可使用 dGPU-style RAM+GPU replica 或 CPU route；必须如实报告该 bucket
未取得 UMA pointer bypass 性能资格。物理/语义支持与 AutoPreferred 分开，不能暗中复制仍宣称零复制。

同样地，若 mapped shared page 的 CPU resident read/write 因 cache policy、页属性或共享带宽稳定超过 native CpuRam
1.20×，或 P99/tail 超过 1.25×，该 `StorageClass` 不得作为 CPU hot canonical backing。它可以保留为 GPU replica，CPU
authority 使用 CpuRam；operation 根据 39 的 CPU-relative cost model 在首次写入前选择 CPU 或 GPU。

以上比较须按 [39 的 5.6–5.9](39_virtual_texture_performance_gates.md#56-四类证据与基线配对统一定义) 分离 M/K/X/E：
CPU shared/CpuRam 在相同 CPU 算子与管理实现下比较；GPU shared direct/VT 在同域比较；GPU shared 对 RAM Tile 是异构
驻留算子比值，不是管理开销。另测含管理/交接的 resident E 和完整产品 E，原有 shared 热访问阈值不能只用 isolated K 通过。
read/write/RMW、cache 属性和带宽争用独立分桶；GPU remote-host、CPU BAR-mapped 不得仅按可映射标志归类为 UMA。

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
- allocation 在全部 CPU lease/native guard、physical pin 和 GPU ticket 满足释放条件前不释放；
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
- pooler/swapper 不直接移动带 active lease/native guard pin 的 shared slot；
- iterator 结束释放 lease，而不是暗含指针永久有效；
- 需要跨调用保存像素地址的旧代码必须显式持有 access session。

Vulkan 类型不能进入 `kritaimage` 公共接口。arena backing 通过 provider token 和 CPU span adapter 暴露。

### 4.1 继承 resident CPU 快路径

已捕获 scope 内的 shared slot 暖 resident 命中，通过 `CachedPageHandle` 内的 provider/allocation generation 和 slot token O(1) 解析；
不得扫描 active lease、每次 map/unmap、建立 heap request 或取得全局 PageStore mutex。`blockSwapping()` 的对应语义是
page-local residency pin 加 last-use ticket：active guard/ticket 结束前 slot 不移动、不重用。
capture/release、首次 binding、局部锁及 scope cache 成本仍按 39 的 5.12 纳入 M/E；共享 payload 不使这些软件管理成本
自动为零，native try miss 也不证明需要 payload migration。此处是 UMA 目标协议；D8 CPU-only guard已接通并有回归/诊断
证据（[62](archive/br1_pre_m6_20260925/documents/62_br1_native_resident_read_and_write_cost_20260920.md)），D9按需缓存还有冷暖读/真实写反证
（[63](archive/br1_pre_m6_20260925/documents/63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md)）；D10冷热查询分离及held-view guard/局部析构计量
（[64](archive/br1_pre_m6_20260925/documents/64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md)）也只覆盖CPU-only，仍有冷读/宽格式/真写残余。
这些切片都不构成真实UMA交接、零迁移或性能验证；局部guard吞吐不含capture/release，容器析构不含全后台drain。
D11 的生产 CPU writeBytes 未发布段（[65](archive/br1_pre_m6_20260925/documents/65_br1_native_cpu_mutation_segment_20260920.md)）可供 UMA 继承
first-write/复用/段末 seal 的生命周期语义，但仍是安全 COW、段持有 physical pin；没有 GPU ownership handoff、内部 write-plan
或 UMA 性能证据。CPU 段的 K1 回归不能归为 UMA 硬件成本；跨域 payload migration 的零值条件不变。
D12的TileData physical claim（[66](archive/br1_pre_m6_20260925/documents/66_br1_physical_exclusivity_prerequisite_20260920.md)）也不是UMA ownership handoff：
GPU/I/O last-use、cache visibility及逻辑retention须另行接通。CPU引用gate测试不证明GPU reader已受保护，更不授予UMA零总成本。

未分配页面使用 shared read-only default binding。CPU 读取返回 virtual default span，GPU 读取可绑定一个 format/default
generation 匹配的共享 default slot；任一 reader 都不应为每个逻辑坐标分配 slot。第一次实际写才建立 private PageVersion。

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

若 PageStore 的 `HandoffRecoverable/HandoffCommitOnly` 条件成立，同一 shared allocation 可以重绑定到新 generation，
这计为 payload retag 而非 copy；旧值仍可观察或异步/失败链未闭合时仍必须 COW。所有 shared current/history/pending/in-flight/
retiring backing 进入同一 owner ledger 和硬预算，不能因 UMA 不发生 domain copy 就允许 slot 无界增长。

计数必须区分：

```text
DomainSyncCopyCount      // 仅下述同一兼容驻留 backing 的真实交接要求为 0
DomainSyncCopyBytes      // 同一计数范围；不是所有 copy bytes
CowCopyBytes
UndoSnapshotCopyBytes
DerivedAtlasCopyBytes
DisplayCopyBytes
```

上述是报告计数口径，不声明 recorder 已实现这些字段。零迁移要求仅用于同一已驻留、布局兼容 shared backing 的真实
CPU↔GPU 交接；同时记录交接次数/方向、exact generation 与 provider 计数覆盖。CPU-only 未交接为 `NotApplicable`，
计量缺失为 `NotMeasured`，两者都不能用零 counter 补成 Pass；无迁移执行区间不合成为 `0 ns`。必要 cache/order/queue/ticket
与像素访问继续按 X/K/E 测量，COW/undo/derived/display copy 分开，不把剩余差额直接认定为硬件下界。

COW 优先顺序：

1. 待覆盖slot无clone/shared物理别名、reader、in-flight GPU/I/O、materialization pin和pending last-use，且PageStore
   签发一次性permit时可物理复用、逻辑发布G+1。recoverable-before模式允许G的逻辑retention，但必须解析到受保护的
   exact-before而非被覆盖slot；无before模式必须没有需保留G的外部引用，并由old-root capture/read gate保护同步立即提交，
   不用于多页Prepared batch。legacy/native/generic物理读者须全部进入同一授权协议，详见52的3.3；
2. 否则保留旧 shared slot，为 G+1 分配新 slot并只在 first-write 执行一次 GPU/CPU page copy；
3. 内存压力下先把旧 generation 安全写 SSD，再决定是否复用。

同一 CPU/GPU mutation batch 的未发布段，后续写同页复用 pending G+1；不得 per iterator lock 或 per dab 重做 COW。
GPU stroke 按显式 batch 捕获 epoch、按 page 聚合该段 dabs，并在 batch 边界提交 root；需要中间可见性时分段，不能
跨已发布段沿用旧可写授权。新段重新取得 writer/COW 资格，物理原位复用仍须新的有效 permit，见 52 的 3.2–3.3。

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
- CPU pointer lease/native guard 未释放：document close 进入有界 drain/cancel，不提前 unmap。
- GPU ticket 未完成：arena 延迟退休；不能通过普通析构直接 free。
- capability 在 device recreation 后变化：创建新 ProviderEpoch，旧 handle 失效并从 RAM/SSD materialize。

## 12. 测试矩阵

必须覆盖：

- coherent 与 non-coherent fake/device path；
- atom 边界相邻页面并发访问；
- CPU write→GPU read、GPU write→CPU read、read/read；
- iterator、clone、COW、memento、save snapshot；
- 同一 mutation 的同一未发布段重复写同页只执行一次必要 COW；发布后新段重新取得 writer/permit，安全原位复用仍 reserve 新 generation；
- 32767+ virtual default 坐标 CPU/GPU read 不增长 page/slot 数量；
- BDA 与 descriptor+offset；
- 4/8/16 字节及更多 StorageClass；
- arena growth、slot ABA、device recreation；
- 强制小预算 shared→SSD→shared；
- 删除全部 sampled/display cache 后重建；
- 稳态绘画在同一兼容驻留 shared backing 上发生真实 CPU↔GPU 交接时，`DomainSyncCopyBytes == 0` 且 copy count 为零，
  适用条件与计数覆盖见 39 的 5.7。
- 三类报告负例：无 GPU 交接不能冒充零迁移实测；计数范围未覆盖实际 provider 不能记零；零 domain-copy 不能掩盖
  过慢 shared mapping、同步/queue 或后台 COW/preclone 工作。计量规则统一见 20 的 11.1、39 的 5.7。

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
- 同时提交 CPU shared/CpuRam、GPU shared direct/VT、主干 RAM Tile 的分项 M/K 及 X/E 关联报告，吞吐与延迟各自验收；
- 同时报告 CPU-only、forced UMA GPU 与 Auto route；覆盖 GPU 低功耗/热降频、CPU-fast、queue contention 和
  CPU/GPU 共享带宽争用；
- 只有完整 trace 达标的 StorageClass 才声明 UMA pointer bypass。

## 14. 完成门槛

- CPU/GPU exact page 使用同一物理 allocation；
- 同一兼容驻留 shared backing 的真实 CPU↔GPU 交接中 payload migration count/bytes 为零，覆盖证据符合 39 的 5.7；
- cache maintenance 范围和 execution order 经过 validation/golden；
- 上层不知道 Vulkan memory type/BDA；
- sampled image 丢失不影响 canonical 数据；
- COW/undo copy 与 domain synchronization copy 可区分；
- initial valid replica set 和交付 endpoint 明确，零 copy 不等于零 cache/order 成本，CPU-only BR1 不作为 UMA 实测证据；
- resident CPU/UMA hit 无 heap request、global request-map insert 或 active-lease scan；
- 产品 Auto 的 median/P95 ≤ CPU-only 1.10×、P99/最长停顿 ≤1.25×；只有预测留有至少 10% 收益余量的 bucket 才
  AutoPreferred，失败时在写入前整操作 CPU route；
- 不满足硬件/格式 correctness 门禁时 capability 如实返回 `Unsupported`；语义可运行但未通过性能门禁时返回
  `AutoPreferred=false`。不能静默复制/慢跑后继续宣称 UMA 加速。
