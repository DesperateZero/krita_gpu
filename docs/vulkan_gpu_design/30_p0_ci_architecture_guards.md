# P0 CI 架构守卫、故障注入与验收矩阵

> 本文定义 Vulkan 校正基线的机器可执行边界。它不是一般测试建议，而是
> [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md) 的强制执行层。
> 任何合并请求只要违反这里的结构规则，即使演示画面正确、性能更高，也不得合入。

## 1. 目标

P0 校正不能依赖 code review 记忆来维持方向。以下事实必须由 CI 自动证明：

1. 依赖图保持单向，Vulkan backend 不反向依赖 UI。
2. Krita tile/COW/undo/swap 只存在一个 canonical PageStore 语义。
3. 所有 Vulkan queue 操作只有一个所有者。
4. UI/input 热路径不出现无界等待、缺页 materialization 或 SSD I/O。
5. PageStore 的 generation、lease、authority handoff 不变量不可旁路。
6. capability 的每个 `true` 都有对应实现和 golden test。
7. 旧 runtime、全局 router 和第二套 swap/cache 不会以“临时兼容”名义返回。
8. Layer/Flow 只能经 versioned lowerer 进入 typed EvalGraphIR；Layer 专用 planner、封闭值类型枚举和
   composite-only cache 不得重新成为全局求值接口。
9. resident CPU/default 热路径保持稀疏、局部和批量提交；reference 容器、通用异步 request 粒度或全 manifest 扫描
   不能进入 production iterator/tile lock。
10. GPU/UMA Auto route 以同机成熟 CPU product path 为基线；在 GPU 劣势环境下前置回退，不能用 capability、零拷贝或
    device timestamp 掩盖端到端退化。

CI 只认可可复现证据：构建图、AST/符号扫描、状态机测试、Vulkan validation、像素 golden、fault
injection 和性能 trace。文档声明或手工演示不能替代其中任何一项。

## 2. 守卫分层

```text
source policy
    -> build/link graph
        -> unit/property/fault tests
            -> Vulkan validation and GPU golden
                -> product scenarios and performance gates
```

前一层失败时不运行后一层。这样既缩短反馈时间，也确保产品测试不会掩盖结构错误。

## 3. 构建和依赖图守卫

### 3.1 允许的 target 边

允许的高层 target 方向是：

```text
application -> kritavulkanuiadapter -> { kritaui, kritavulkanbackend }
kritavulkanbackend -> kritaimage
paintop/save/undo/cpu consumers -> kritaimage
kritavulkanoffscreen -> kritavulkanbackend
```

构建时生成 target dependency graph，并执行以下断言：

- `kritavulkanbackend` 的直接和传递链接闭包中不得出现 `kritaui`；
- `kritaimage` 的链接闭包中不得出现 Vulkan、WSI、Qt window/canvas 类型；
- `kritavulkanuiadapter` 可以依赖 `kritaui` 和 backend，但二者不得反向链接 adapter；adapter 不得导出
  canonical pixel storage 类型；
- paintop 可以依赖 backend-neutral execution context，不能 include UI canvas 私有头；
- paintop 不应链接 concrete Vulkan backend；
- PageStore、SurfaceRegistry、generation、lease、SSD store 的实现只属于 `kritaimage`；
- Vulkan replica、direct/local binding、可选稀疏目录、shader 和 submission 的实现只属于 `kritavulkanbackend`。

建议由 CMake 导出 JSON/DOT target graph，再由仓库脚本检查 target 闭包。只对文件名做 grep 不足以证明传递依赖。

### 3.2 公共头依赖

单独编译每个公共头，检查：

- `kritaimage` 公共头不需要 Vulkan SDK；
- backend-neutral ticket 不暴露 `VkFence`、`VkSemaphore` 或 timeline handle；
- PageStore lease 不暴露 Vulkan allocation；
- UI 公共头不成为 backend 公共 API 的前置依赖；
- concrete `VulkanDocumentGpuSession` 不出现在 `kritaimage` 类型定义中。

### 3.3 循环依赖

CI 对 target 图执行强连通分量检查。包含两个或更多产品 target 的强连通分量一律失败，不接受 link order、
弱符号或 platform conditional 作为例外。

## 4. Queue API 所有权守卫

只有 `SubmissionCoordinator` 的 allowlist translation unit 可以调用：

```text
vkQueueSubmit
vkQueueSubmit2
vkQueueBindSparse
vkQueuePresentKHR
```

检查必须覆盖：

- 源码 token/AST；
- 最终 backend 二进制的符号引用；
- wrapper、function pointer 和 dispatch table 的间接调用；
- 测试 fake 与 production 路径的区分。

业务模块只能生成 immutable submission request：

```text
TransferRequest
SparseBindRequest
ComputeRequest
GraphicsRequest
PresentRequest
```

Presenter 可以构造 `PresentRequest`，但不能持有或调用 `VkQueue`。发现新的 queue mutex、模块私有
timeline semaphore 或自行递增的 completion counter，同样判定为架构失败。

## 5. Wait 与线程守卫

### 5.1 静态禁止项

production runtime 中禁止：

- `vkQueueWaitIdle`；
- 对仍可能接收提交的 device 调用 `vkDeviceWaitIdle`；
- `UINT64_MAX` 或等价无限值的 fence/semaphore wait；
- UI/input callback 中的 blocking future、condition variable wait、page materialization；
- render/submission thread 等待 CPU worker 完成；
- resize 先 wait-idle 再重建；
- save/export 在 UI thread 逐页下载。

`vkDeviceWaitIdle` 若仅用于已停止接收工作、已等待所有已知 timeline 的最终故障清理路径，必须位于单独
allowlist 文件并由测试证明调用前 coordinator 已进入 `Stopped`。

### 5.2 运行时断言

线程角色注册为稳定 ID：

```text
UiInput
StrokeFrontend
CpuContinuationWorker
Submission
PresentationFrontend
IoWorker
```

PageStore materialization、SSD I/O、host wait 和 Vulkan wait 记录调用线程。debug/CI 中，只要从禁止线程
进入这些路径立即 abort 测试，并输出 session、surface、page、generation 和 ticket。

### 5.3 有界 WSI

`vkAcquireNextImageKHR` 只能采用非阻塞或明确有界策略。没有 frame slot 时允许跳帧；不允许用无界 acquire
保持“每次都显示”。测试注入长期 occlusion、minimize 和 out-of-date，UI 输入延迟仍须稳定。

## 6. Canonical PageStore 守卫

BR1 当前已有的 tiles3/iterator/painter 侵入先以 allowlist ratchet 封存，再随统一 owner 迁移逐项降低；source inventory、
symbol/reverse-call graph、状态所有权矩阵、runtime census 和单项删除门槛见
[69](archive/br1_pre_m6_20260925/documents/69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md)。本节定义永久不变量，69 定义当前污染面如何证明退出。

### 6.1 状态机断言

debug 和所有 CI profile 中永久开启：

1. 同一 page generation 最多一个 writer。
2. Unpublished/Prepared generation 不可被普通 committed ImageEpoch reader 看见。
3. transaction commit/cancel 后 write lease 不能再次使用。
4. authority handoff 前目标 replica 必须完成且通过校验。
5. 释放 authority 前必须存在同 generation 的另一有效 replica。
6. 未提交或 checksum 失败的 SSD record 不能进入有效 replica 集。
7. derived page 不能成为 canonical authority。
8. ticket 未完成时相关 command、descriptor、allocation、binding-table slot 不能回收。
9. dependency generation 不匹配的 derived page 不能被显示或保存。
10. 所有状态转移只能通过 PageStore transition API。
11. operation completion 必须匹配 OperationId、PageVersion、ReplicaId 与 ProviderEpoch。
12. slot/allocation generation 不匹配的 stale handle/completion 必须被拒绝。
13. 相同 materialization dedup key 不能同时存在多个 producer。
14. 多页 transaction/save epoch 不能暴露 Prepared 但未 Committed 的 generation 混合。
15. `DocumentImageEpochHead` 是多页可见性的唯一线性化点；tag 过期的 per-page published cache 不得用于普通 read。
16. 基于同一 BaseImageEpoch 的并发重叠 commit 必须有确定 rebase/conflict 结果，不能静默 last-writer-wins。

### 6.2 状态空间探索

使用 reference state machine 生成随机序列：

```text
acquire read/write
resolve
produce
publish/cancel
copy replica
write/read SSD
evict
undo/redo
save epoch
device loss
document close
```

每一步比较 reference model 与实现，并在失败时输出可缩减、可重放的 seed。测试不能只覆盖正常顺序；必须
系统注入完成乱序、取消、OOM、I/O 错误和校验失败。

reference model 与 production provider 必须调用同一组 transition 验证函数；禁止测试一套简化状态机、运行另一套
宽松逻辑。随机测试额外覆盖 shard 竞争、materialization dedup、transaction abort、ProviderEpoch 变化和 slot ABA。

### 6.3 唯一 SSD 后端

架构扫描禁止在 `kritavulkanbackend` 或 UI 中出现独立 page file、swap index、compression store、L3 cache。
唯一 SSD page backing/durability path 是 `kritaimage` 中由 `KisTileDataStore`/`KisSwappedDataStore` 演进出的
unified store。

Vulkan staging、transient upload ring、pipeline cache 不属于 SSD page store，但必须以类型和目录明确其生命周期，
不得把画布 canonical page 写成 backend 私有持久文件。

### 6.4 Resident CPU 与 production layout 守卫

Tier 0/4 必须以计数器、allocation hook 和复杂度 sweep 主动拒绝：

- default/blank read 为每个坐标创建 PageKey、PageVersion、replica、request 或物理 tile；
- 已捕获 scope 内的 ready resident CPU read/write 建立 heap request/lease、插入全局 request map、取得 PageStore 全局 mutex；
- CPU provider 通过遍历 active leases 把 pointer/handle 反查为 tile；
- 同一 mutation 的同一未发布段对同一 PageKey 重复 reserve generation、重复 COW 或重复 seal；
- tile/accessor unlock 隐式执行 epoch commit、全 extent 或完整 manifest 扫描；
- 未升级的 write intent 创建 generation、allocation 或 proof，或在 writable pointer 已暴露后仍声称 no-op；
- production epoch commit/read 依赖 reference `QHash` 重建、owning `QVector` manifest 或全量 sort；
- 每页创建 owning write-plan、`shared_ptr<Page>` 或 generation 级 shared binding；
- publication install 触发 metadata slot allocation、index rehash 或大对象析构；
- 为 handoff 绕过 shard-owned generational slot arena，或在 slot/block generation 回绕后复用 identity；
- K 固定、N 扩大时 commit allocation/latency 随 N 线性增长。

必须有正向测试证明：

1. 32767+ 不同 blank coordinates 读取后 page/version/replica allocation 为 0，default pixel backing 为 O(1)；
2. resident read guard 只产生 page-local pin/unpin，cache tag 失配会回到 immutable root 校验；
3. CPU allocation 只有经 PageStore 私有 `KisPageWriteCoordinator` 选择 `HandoffRecoverable`（已有 exact before）或
   `HandoffCommitOnly`（capture gate + 完整预检 + 首字节后不可失败）才可移交，observed PageVersion 仍单调推进；
   并证明可取消/可失败的多页 Prepared transaction 不会无 before 覆盖旧 G；
4. 旧值仍可观察且没有 alternate before 时 first-write COW；同一未发布段后续写复用 pending G+1，发布后新段重新选择 write plan；
5. persistent root commit K 个 changed pages，只复制 changed paths，extent 按 delta 更新；
6. fast path 与通用 request path 对同一事件序列输出相同 transition trace/invariant 结果。
7. 无旧值保留的 resident handoff 桶中 before-image copy、新 payload allocation、payload migration 和 retirement payload 均为 0；
8. current/history/pending/in-flight/retiring/optional backing 的精确字节 ledger 在 tiny-budget、旧 View、undo、last-use 与
   retire 拒绝压力下不越硬上限，并出现预期背压或 `ResourcePressure`，最终 drain 债务可解释。
9. production metadata 使用 typed generational slot arena；install allocator/rehash/large-destructor 计数为零，旧 slot/block id
   在释放、整块归还、重新附着和 generation 极限下均不能 ABA；common record 内存至少降低 25%。

补充 resident-read 路由矩阵：cached handle miss 但 exact CPU 副本 ready、retained 历史已驻留、authority 在其他域但已有
ready CPU 副本，都应在受保护视图内 resolve/pin，通用 request/迁移计数为零；virtual default 绑定视图的 format/default
revision。真正 non-resident、pending producer/访问交接才走对应慢路径；stale capability/version/provider 被拒绝，局部
竞争不得伪装为物理缺页。非 CPU authority 可由状态机/fake provider 覆盖正确性，但不作为 GPU/UMA 性能证据。
上述读侧规则不能放宽 writer handoff、COW 或 write-plan 证明；CPU-only 无 GPU 交接时 GPU binding/submit/ownership 计数应为零。

免全局锁与零分配断言的路径范围按 39 的 5.12 冻结，capture/release、首次 binding、scope cache 分配仍计入完整 M/E。
generic fallback 必须有可核验原因；unsupported provider/binding miss/busy 是软件路径或竞争，不等于 swap/跨域，
不得用扩大“缺页”分类规避 ready resident 门禁。原生与通用读写/transfer/retire/close 的协调必须有生命周期负例：
不能仅断言 generic lease map 为空便宣布无 reader，不能在 metadata 撤销后忽略 provider 的退休失败。
多个 allocation alias 同一 payload 时，record-local 零 reader 不授予原位写；scope/root 保护也不替代 physical pin。

详细门禁和迁移顺序见
[52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)。

当前整体重构的执行门槛见 [67](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md)：先完成六项结构约束及真实入口回归，
再统一运行性能资格。新增结构测试必须覆盖候选 owner/revision/单次消费/取消与不可见性、virtual-default writer 的逻辑
before-image、native source copy 与 writer 互斥、extent 索引相对独立 manifest oracle、root 多重 retention/transaction 引用。
补测 pending default writer 与后续旧版本物化、共享 default 跨 key/revision/cache 淘汰/guard 寿命及真实 session 零源物化；
局部 gate 竞争须复验/恢复，不建 generic request 掩盖竞争；commit 与 retained restore 都验证 metadata 完整安装后 root 才可见。
退休拒绝须保留 exact 身份及 last-use，预算重试、物理 pin 解除后恢复、关闭失败后再试均须通过；失败重试有界不等于整个回收已预算化。
`synchronousWriteCopy` 仅声明复制能力，不能推导支持 native mutation；后者须显式 `nativeCpuMutation` 能力并接受相同安全测试。
保留 legacy unlock 边界接入 native 不等于整个 iterator 已具备 operation-wide View/MutationSession。
共享 legacy wrapper 的最终 unlock 跨线程必须单独回归；terminal seal 不得放松普通 session 的线程归属或活跃 guard 检查。
日志中的 `SAFE ASSERT` 属于失败证据，即使 QtTest 总结和进程 exit code 为通过，也不能计入通过清单。
应用级测试若在资源初始化崩溃，记录原始失败及堆栈；直接 iterator 实现回归不能替代完整 PaintDevice/画笔资格。

## 7. 全局状态和生命周期守卫

静态检查拒绝：

- `KisVulkanPaintRouter::activeInstance` 或语义等价的 current canvas/current backend 单例；
- PaintOp factory 全局 wrap；
- 跨线程捕获裸 `DocumentGpuSession*`、backend 指针或 canvas 指针；
- canvas 构造函数写成功标记；
- 仅凭配置键或静态 `isAvailable()` 就替换正常 canvas；
- 文档 A 的 job 引用文档 B 的 surface/page identity。

测试必须覆盖两个文档、同文档两个 canvas、关闭任一 canvas、关闭文档、设备丢失和重新建立 UI adapter。
session 生命周期由 `KisImage` 的 backend-neutral slot 决定，canvas 数量不能改变 canonical 数据所有权。

## 8. 旧路径负向清单

BR0 后，production source tree 中以下符号或语义不得存在：

- `KisVulkanPaintRouter::activeInstance`；
- `KisVulkanPaintOpFactory` 全局替换；
- stroke-end 全量/逐 dirty tile CPU download transaction；
- `KisVulkanUpdateInfo` 携带原始 projection 像素副本；
- `KisVulkanTileData::Tier` 作为第二套 residency 真相；
- 旧 `TileCache`、`Prefetcher`、单 command-buffer `TransferQueue`；
- shader 热路径中的全局可变 PageKey hash lookup；
- 每页/每次 fault 独立 queue submit；
- production SSD 的每页 fsync、立即整页读回和 mmap window/chunk authority；
- 以单个 temperature score 绕过 lease/pin/authority safety；
- fixed 8192×8192 fallback canvas；
- active layer 与 projection/display image alias；
- `flushAndPause`；
- CPU 循环“一 dab 一 dispatch”。

检查脚本应同时维护符号清单和允许迁移的纯算法清单，避免因重命名躲过守卫。

## 9. SurfaceFormat、LoD 与 capability 守卫

每项 capability descriptor 必须关联：

```text
CapabilityId
OperationId / SemanticVersion
Input/Output ValueType(typeId/version/storage class)
Supported SurfaceFormat set
Required device features
Required shader/kernel variant
CPU reference
GPU golden test ids
FallbackRoute
```

规则：

- capability 没有关联通过的 GPU golden 时只能返回 `Unsupported`；
- fixed `pixelSize=4` 和无 codec 的 raw `readBytes()` 上传在 production 路径中失败；
- 未实现 mip/page pyramid 时 LoD 返回不支持；
- display format 支持不能推导 canonical paint format 支持；
- 不支持格式在 stroke 开始前路由 CPU，不能在部分 GPU 写入后回退。

最低格式矩阵覆盖 4/8/16 字节像素、不同通道布局和 alpha 语义；每个已声明支持的 blend/selection/
alpha-lock/wash 组合都有 CPU reference comparison。

## 10. Vulkan validation 与同步矩阵

### 10.1 Validation 零容忍

启用 validation、sync validation、best practices 和 GPU-assisted validation（平台支持时）。任何 error 或未在
有期限 issue 中说明的 warning 都使测试失败。不得维护长期 suppression 来通过基线。

### 10.2 Queue topology

同一测试套件至少运行：

1. graphics/compute/transfer/present 共用 queue family；
2. compute 独立；
3. transfer 独立；
4. present 与 graphics 不同 `VkQueue`；
5. sparse queue 独立或不支持 sparse 的 direct/local software-binding 路径。

测试比较结果和 resource ownership transfer；queue topology 不得改变 PageStore 可见语义。

## 11. 必须具备的测试矩阵

### 11.1 存储和迁移

- 极小 VRAM/RAM 预算下执行 VRAM → RAM → SSD → RAM → VRAM 随机迁移；
- 每个阶段核对 generation、checksum、authority 和有效 replica 集；
- SSD write fail、partial write、cancel、checksum corruption、index 恢复、GC 中断；
- authority handoff 前后注入 device loss/OOM；
- default pixel、extent 收缩、purge、clone/COW 和 animation frame identity。
- deadline-aware byte batch、materialization dedup、emergency reserve 和 staging wrap/retirement；
- `SessionSpill` 与 `RecoveryCheckpoint` 分级、manifest durable 边界和 GC 任意中断；
- disk full/硬预算下保留旧 authority 并形成显式 backpressure。

### 11.2 UMA

- canonical arena 的 CPU pointer 与 GPU address 访问同一 generation；
- 稳态绘画画布像素 domain-sync copy counter 严格为零，COW/undo/derived copy 单列；
- coherent/non-coherent memory 的 flush/invalidate 范围正确；
- CPU iterator 与 GPU writer 的 ownership/timeline 不出现 data race；
- sampled display cache 可删除并从 canonical page 重建。
- BDA 与 descriptor+offset 两条 binding 路径；
- domain-sync、COW、undo snapshot、derived/display copy 分项计数；
- non-coherent atom 相邻 slot 并发和 slot ABA。

### 11.3 Stroke、undo 和保存

- overlapping dab 严格顺序 golden；
- 跨页 dab、长线、高频输入、journal/backpressure；
- selection、alpha lock、wash、first-write COW；
- stroke 进行中立即 undo、cancel、save、关闭文档；
- 保存 immutable image epoch，同时新 stroke 写下一 generation；
- 保存后重开逐像素一致；
- CPU fallback 在开始前决策且不产生混合半成品。

### 11.4 Graph 和显示

- EvalGraphIR topology/ports、Layer/Flow equivalent graph、属性、mask、filter、animation frame 随机变化；
- lower checkpoint 和 upper operator/replay dependency vector 校验；
- backdrop-dependent upper 不能在透明背景错误拍平；
- display descriptor 精确绑定所声明的 DisplaySurface generation；
- 多文档、多 canvas、关闭一个 canvas 不影响另一 canvas 或文档；
- resize/out-of-date/minimize 通过 generation retirement，不 wait-idle。
- `CoveredCold` 必须带有效 CoverageCertificate；graph/property/target变化后 stale certificate 接受数为零；
- 有界 trajectory corridor 的 soft pin/expiry/predictor miss 不改变最终像素。

### 11.5 格式和能力

- 4/8/16 字节像素格式；
- 支持与不支持的 KoColorSpace/channel/alpha 组合；
- 不支持项前置 CPU 路由；
- color conversion、proofing/display filter 与 canonical 数据隔离；
- LoD/mip 缺失时不宣称支持。

## 12. 可观测性和性能门禁

每次测试 trace 至少关联：

```text
DocumentSessionId
SurfaceId
LogicalPageId
Generation
EvaluationEpochId
StrokeId
SubmissionId
GpuTicket
QueueId
ReplicaDomain
```

强制计数器：

- UI/input host waits；
- page materialization by thread；
- canvas-pixel copy bytes by path；
- dispatches、page jobs、dabs per page job；
- replica migrations 和失败次数；
- SSD bytes/checksum/recovery；
- command/descriptor/allocation retirement lag；
- stale derived cache rejection；
- skipped/dropped present frames。
- materialization dedup/stale completion/slot ABA rejection；
- batch bytes/pages/regions、deadline miss和staging pressure；
- domain-sync/COW/undo/derived/display copy bytes分项；
- semantic class、CoverageCertificate、ghost hit和reverse migration；
- SSD durability class、GC write amplification和disk-pressure backpressure。
- virtual-default hit、PageKey/version/replica allocations by reason；
- resident CPU fast/fallback hit、heap request/lease、global-map insert、provider active-lease scan；
- generation reserves、physical COW、in-place allocation reuse、page seals 和 epoch commits per mutation/page；
- epoch changed pages K、manifest pages N、root nodes copied、full-manifest export/sort/scan；
- tile unlock triggered commits 和 full extent scans（硬门槛为 0）。
- CPU-only/forced accelerator/Auto 的 end-to-end P50/P95/P99、最长停顿；
- predicted CPU/accelerator ETA、route reason、profile freshness、risk margin、regret 与 demotion；
- performance profile state-envelope exit、circuit-breaker trip、bucket quarantine 和 whole-operation abort/replay；
- GPU low-power/thermal、queue contention、UMA shared-bandwidth contention 的 bucket 结果。
- 39 的 M/K/X/E classification、paired baseline、semantic scope/additional semantics；
- 每项指标的 MetricScope、CPU/wall 与计时边界/排除项，管理 self 和 lifecycle-inclusive 不混为一个倍率；
- executor、physical backing/access path、memory/cache 属性、InitialState→RequiredEndpoint 和 exact valid replica set；
- 固定资源/到达率的完成吞吐、单操作及负载尾延迟、M self 与 wait/hold、同域 direct/VT 和 RAM Tile 异构 K 比值；
- setup/cold/warm、X 方向/字节、关键路径重叠、drained CPU/wall 与 retired backlog。
- M required buckets、预冻结相对/绝对容差、置信水平/方法、独立配对采样/停止规则、时间及吞吐置信界与验收状态。
- provider default-initialized、explicit source-copy、native-duplicate、adopted 页数/逻辑字节及其计量范围；
  preclone 前后台工作、reserve 峰值与 drain 按 20 的 11.1 单列，不把 native duplicate/adoption 当作物理带宽。
- native read 的 capture/release、首次 binding、暖 guard、完整 operation 计量边界，逻辑读结果、fallback 原因与重试次数；
  allocation/lock 范围及最后旧 scope 回收按 20 的 11.2 保存，尚不可观测的字段标缺测。

硬门槛：UI/input wait count 为零；同一兼容驻留 shared backing 的真实 CPU↔GPU 交接中 payload migration count/bytes 为零
（适用条件与证据范围见 39 的 5.7；非所有 copy）；每 dab dispatch 路径计数为零；
validation error 为零。产品 Auto 相对 CPU-only 的 median/P95 不超过 1.10×，P99/最长交互停顿不超过 1.25×；route/
fallback 开销不使直接 CPU 路径超过 1.05×，该开销配对必须从相同 valid replica set 到相同 endpoint（必要读回双方均计）。
帧率均值不能替代交互延迟分位数、最长停顿和背压行为。
GPU/UMA 性能资格还必须依赖 BR1-PERF upstream CPU 差分已通过；禁止以退化的 CPU 实现作分母“洗快”accelerator。
CPU/CpuRam 同义管理必须按 39 的 5.6 独立证明不劣于主干；阶段完整操作倍率通过不代替 M 通过，证据不足不得结清。

性能报告/harness 必须按 [39 的 5.6–5.9](39_virtual_texture_performance_gates.md#56-四类证据与基线配对统一定义) 校验；
以下任一项出现，不能接受为性能结清或 AutoPreferred 证据：

- 把 GPU/VRAM 对 CPU/RAM 的 K 比值称为虚拟纹理管理倍率，或缺少同域 GPU direct/VT 对照却声称已隔离寻址开销；
- 用 K/E 加速抵消 M 的结构/CPU 主干回归，或只提供 M/no-op stress 而缺少真实像素吞吐和端到端延迟；
- 用 CPU bridge 的 M 结果替代实际 GPU/UMA provider 管理证据，或把 shader 寻址混为 host-side 管理 self；
- executor/domain/access path/endpoint 或共同语义不匹配，却仍计算配对倍率；新增语义用虚构零分母比较；
- 用提交量代替完成量、logical alias bytes 代替物理带宽、1/P95 代替吞吐，或隐藏 setup/readback/GC/队列积压；
- M/K/X/E 双计数、P95/并发时长直接相加、缺失项填零、用 UMA/fake/CPU-only 结果代替真实 dGPU 性能；
- 未在验收前冻结管理/吞吐预算，或在看到结果后放宽 profile 以取得通过。
- 以“无显著差异”或 1.2×/1.3×/1.5× 阶段操作上限代替 M 不劣性，required bucket 缺测或置信界不足却标 Pass；
- 把同义操作所需内部 generation/proof/adapter 记账改称 additional semantics 后排除，或把真实新增语义从 E 扣除；
- 由 UMA 零迁移复制推导整个 X/同步/queue/ticket 为零，或把未解释的软件残余直接归为不可优化的硬件成本。
- 把旧源码/库版本的采样热点写成修复后实测，结构/正确性通过但未有 after 配对仍标性能 Pass，或删去失败原件掩盖成本转移。
- 把单 manager 的零 counter 外推为全进程/全 trace 零开销，把存活终值当累计工作量或长期有界证明，或以切片诊断代替正式配对资格。
- 以 defaultMaterializationRequests=0 证明 provider 没有默认填充，或把未拆开的 acquireWrite/provider 时间全算 M、K 或 X；
- 预克隆只记录前台收益、不记录后台补充/占用/回收，或以复制调用数/逻辑字节推定硬件流量；
- 新增诊断接口后不冻结兼容 harness/ABI 和两侧版本，或忽略关闭态偏移、抽样周期混叠及 sampled 单次时钟成本；
- 未发生实际 CPU↔GPU 交接或缺少 shared backing/计数覆盖证据，却把 UMA 零迁移标为 Pass；
- 用容差内不劣性通过宣称严格耗时相同、整条管线同构或全部软件额外成本已消失。
- 把无迁移执行区间合成为 `0 ns`、低于分辨率记作零耗时，或仅凭 UMA/必要同步标签豁免未归因、超预算差额；
- 仅 identity lookup 免锁便声明像素热路径免全局锁，排除 capture/release 的真实成本，或删除 retention/pin/last-use 保护换取零计数；
- 将不同切片的性能倍率相乘生成未实测结果，或让后续工作树接线直接继承旧二进制的 Pass。
- 仅凭 alias/adoption/commit 名称将混有 source 初始化/像素复制的操作授予纯 M 资格，或只排除候选一侧的数据准备；
- 以“每 session/页一次 COW”为由跨已发布段沿用旧可写授权、改变中间可见性，或不记录真实 session/发布边界却声称重复工作已消除。
- 将 payload 已驻留等同于 binding/cache 已暖，隐藏每次操作必经的 capture/setup/release，或用暖 guard 零请求宣称整个 scope 零分配；
- 用 `tryLock`/原子计数/`call_once` 名称宣称严格 lock-free，或将未分类 native miss 一律记为硬件缺页/跨域迁移；
- 修改 provider/guard ABI 后未经兼容性与 loader 核验即复用旧二进制，或以源码存在替代新版本构建、生命周期和性能证据。
- 用新read facade的收益抵消未迁移legacy路径或真实写的回归，或把eager→lazy仅移出窗口的缓存建立成本写成已消除；
  冷binding、暖读、只写/legacy控制及完整生命周期须分别保留，D8–D10反证与实际计量覆盖见62–64、20的11.2。
- 把held-view guard的组件吞吐当含capture/release的完整session结果；或将固定cycle总时间倒数称为持续吞吐/事件尾分位。
- 仅凭`lifecycle`/`destroy`字段名或close返回宣称全部回收完成；混用旧close端点与新容器析构端点，或以局部析构替代
  pool/worker全后台drain、退休积压与长期有界证明。
- 把workload/统计seed当每进程实际hash seed，用事后环境推断代替缺失记录；未经控制证据把负偏移归给噪声/布局/后台活动。
- 为跑分改变生产hash策略、筛除不利seed，或只用固定seed/layout诊断授予生产默认配置的不劣性；测量记录变更未校准
  关闭态偏移，或改写旧协议以制造已记录的假象。后续记录与环境对照按20的11.3落实，历史缺失明确保留。
- 只有新facade或类名变化而没有真实生产入口迁移，仍声称native mutation/production owner完成；或将tile publish/proof、
  操作batch和root commit混计，以原子root赋值存在证明整个发布临界区已短。结构核对及后续切片门槛见52第12节。
- native 写段中放掉独占 backing 保护却继续复用裸可写指针，或将整段 dirty-page pin 当零成本、无大 K 预算也宣布有界；
  失败 seal 清除较早 history 段、guard/batch 销毁遗留永久 claim，或写授权失败仍向 memcpy 返回 before-image。
  D11 的定向测试/反证见65；零 generic request 不授予性能 Pass，尤其不能抵消已测 K1 回归。
- 将binding局部writer或swap shared pin误当所有alias的物理写排他；用采样总refcount自签发physical claim，或将physical claim
  当成root/capture/retention permit。D12负例覆盖见66，生产未消费claim不得宣称原位写已接通；inline引用协议变化须重编所有
  参与路径并使用匹配runtime，不能只替换动态库后假定旧inline代码会遵守新gate。

报告还须满足 39 的 5.10 证据更新规则、5.11 统一判词与 5.12 native read 分层验收；default/remove 优化检查后续 read/first-write/history/drain，
归因残余不能隐去。

上述为新增测试标准，报告器/CI 实装仍须按 52 的 P1/P6 落地；文档存在不代表自动守卫已实现。BR1 先要求 CPU 阶段
适用证据，GPU/UMA 的 NotMeasured 不阻止隔离研究，但阻止对应硬件 profile 获得产品性能资格。

## 13. CI 分层

### Tier 0：结构与无 GPU reference

- dependency graph、public header self-compile、forbidden symbol/API；
- PageStore reference state machine/property tests；
- shard/dedup/transaction/ProviderEpoch/ABA state-space tests；
- CPU pixel reference、codec、EvaluationEpoch dependency；
- authoring snapshot/lowerer、open ValueType、typed EvalGraphIR、source/diamond/fan-out/multi-output 与空 MutationRootSet；
- SSD fake store/fault injection；
- 文档链接与架构关键词一致性。

每次提交必跑。

### Tier 1：软件或基础 Vulkan

- SubmissionCoordinator DAG；
- command arena retirement；
- validation/sync validation；
- direct/local binding 和基础 compute golden；
- direct PageHandle/local binding snapshot与retirement；
- shared/separate queue family matrix 中可模拟部分。

每次合并请求必跑。

### Tier 2：真实 UMA

- pointer bypass；
- coherent/non-coherent cache maintenance；
- copy counter；
- CPU/GPU concurrent ownership；
- 长时间内存压力。

至少每日和 release candidate 必跑。

### Tier 3：真实 dGPU

- VRAM/RAM/SSD 强制迁移；
- discrete queue family；
- OOM/device-loss/fault handling；
- 大画布和长 stroke。

至少每日和 release candidate 必跑。

### Tier 4：Krita 产品闭环

- undo/redo/save/reopen；
- EvalGraphIR/Layer/Flow、mask/filter/color/display；
- 多文档、多 canvas、WSI 生命周期；
- CPU-only/forced GPU/forced UMA/Auto 性能基线、GPU 劣势 profile 和交互延迟。

Vulkan 用户选项启用前全部必跑。

## 14. BR 阶段对应门禁

| 阶段 | 不能缺少的机器证据 |
|---|---|
| BR0 | 旧符号为零、依赖无环、Vulkan 用户入口关闭、CPU/OpenGL 回归通过 |
| BR1 | CPU canonical PageStore 与原 Krita tile/COW/undo/save 像素一致；分片/dedup/transaction property test 通过；virtual default、resident guard、write-plan/条件 handoff/必要 COW、硬 backing 预算、mutation scope、persistent root 达到 52/68 的结构和 39 的 upstream 差分性能门禁 |
| BR2 | queue API 唯一所有者、timeline/command retirement、validation/fault injection 通过 |
| BR3 | UMA 真实交接在同一兼容驻留 backing 上零 payload migration（39 的 5.7），且 shared CPU access 通过 39 的相对门限；direct/local binding、dGPU deadline batch、SSD durability/GC、强制迁移与 handoff fault test 通过 |
| BR4 | Layer/Flow equivalent lowering、random EvalGraphIR/EvaluationEpoch、mixed executor stale publish、CoverageCertificate、semantic CLOCK/cost、bounded prediction 和图层剪枝通过 |
| BR5 | stroke golden、COW undo、immutable save、cancel/recovery、格式矩阵及 39 的 CPU-relative Auto route/GPU 劣势门禁通过 |
| BR6 | 多 canvas、WSI、display/color/filter、完整产品回归和性能门禁通过 |

阶段门禁不可用“后续补测试”豁免。未通过即不进入下一阶段。

## 15. 例外策略

P0 结构规则没有永久例外。短期测试基础设施限制只能：

1. 明确说明缺失的平台/硬件；
2. 保持 capability 关闭；
3. 不开放用户入口；
4. 记录带到期日和负责人 issue；
5. 不改变 canonical 数据模型或放宽静态守卫。

禁止通过 suppression、隐藏配置键、只在 release 关闭断言、将旧路径放进 compile flag 等方式制造“通过”。

## 16. 验收定义

本文完成不以脚本文件存在为准，而以 CI 能主动阻止以下回归为准：

- backend 链接 UI；
- 第二个模块调用 queue API；
- UI thread 新增 host wait；
- 未校验 replica 接管 authority；
- default read 物化页面、resident CPU 热路径创建通用 request，或 production commit 全量重建 reference manifest；
- Vulkan backend 新建独立 swap；
- capability 没有 golden 却返回支持；
- 旧 global router 或 stroke-end download 重新出现。

只有这些失败样例都能被自动拒绝，P0 的“绝对硬边界”才真正建立。
