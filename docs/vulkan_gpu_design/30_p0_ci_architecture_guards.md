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
- 稳态绘画画布像素 copy counter 严格为零；
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

硬门槛：UI/input wait count 为零；UMA 稳态 canvas-pixel copy bytes 为零；每 dab dispatch 路径计数为零；
validation error 为零。帧率均值不能替代交互延迟分位数、最长停顿和背压行为。

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
- 性能基线和交互延迟。

Vulkan 用户选项启用前全部必跑。

## 14. BR 阶段对应门禁

| 阶段 | 不能缺少的机器证据 |
|---|---|
| BR0 | 旧符号为零、依赖无环、Vulkan 用户入口关闭、CPU/OpenGL 回归通过 |
| BR1 | CPU canonical PageStore 与原 Krita tile/COW/undo/save 像素一致，分片/dedup/transaction 状态机 property test 通过 |
| BR2 | queue API 唯一所有者、timeline/command retirement、validation/fault injection 通过 |
| BR3 | UMA domain-copy=0、direct/local binding、dGPU deadline batch、SSD durability/GC、强制迁移与 handoff fault test 通过 |
| BR4 | Layer/Flow equivalent lowering、random EvalGraphIR/EvaluationEpoch、mixed executor stale publish、CoverageCertificate、semantic CLOCK/cost、bounded prediction 和图层剪枝通过 |
| BR5 | stroke golden、COW undo、immutable save、cancel/recovery、格式矩阵通过 |
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
- Vulkan backend 新建独立 swap；
- capability 没有 golden 却返回支持；
- 旧 global router 或 stroke-end download 重新出现。

只有这些失败样例都能被自动拒绝，P0 的“绝对硬边界”才真正建立。
