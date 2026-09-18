# GPU Stroke 重建施工与 BR5 接入计划

> 本文只细化 GPU stroke 新实现的代码组织、提交边界和验收。它不是全局基线切换计划。
> 旧 Vulkan runtime 在 BR0 就从新树删除，而不是等本文的新 stroke 能显示后再删除。全局唯一顺序见
> [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md)，全局 P0 边界见
> [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)。

## 1. 最终基线定义

GPU stroke 完成时，数据链只有一条：

```text
Krita input / PaintOp
  -> KisPaintExecutionContext
  -> DocumentGpuSession
  -> StrokeEpoch + immutable StrokeJournal
  -> PageWorkCompiler
  -> canonical PageStore write leases
  -> SubmissionCoordinator ticket DAG
  -> page-batched StrokeCompute
  -> publish page generations
  -> EvaluationPlanner incremental task DAG/composite
  -> Derived DisplaySurface
  -> Presenter builds PresentRequest
  -> SubmissionCoordinator presents
```

Undo/save/CPU consumer 从同一个 canonical PageStore 读取 generation；不存在：

```text
GPU canvas authority
  -> stroke-end download
  -> writeBytes into a second CPU tile truth
```

GPU stroke 是 PageStore 的 consumer，不拥有 tile identity、COW、swap、queue、document session 或 display authority。

## 2. 全局前置条件

Production stroke 接入必须等待：

- **BR0**：旧 runtime、global router、factory wrap、双向 CMake 依赖、旧入口已删除；
- **BR1**：Krita tiles3/COW/undo/swap 已演进为唯一 canonical PageStore；
- **BR2**：SubmissionCoordinator 独占 submit/bind/present，command/resource retirement 已验证；
- **BR3**：UMA/dGPU/RAM/SSD replica 与 authority handoff 已通过强制迁移；
- **BR4**：authoring lowerer、typed EvalGraphIR、EvaluationPlanner task DAG、EvaluationEpoch、Layer lower/upper
  optimization cache 和 DisplaySurface identity 已冻结。

在这些条件完成前，只允许开发纯协议、reference executor、shader 数学和 offscreen test asset；不得把它们接到
用户 canvas，也不得保留旧 runtime 供“过渡验证”。

## 3. 目标模块和依赖方向

```text
application -> kritavulkanuiadapter -> { kritaui, kritavulkanbackend }
kritavulkanbackend -> kritaimage
paintop/save/undo/cpu consumers -> kritaimage
```

### 3.1 `kritaimage`

必须提供 backend-neutral：

- `SurfaceId`、`LogicalPageId`、`SurfaceFormat`；
- `PublishedGeneration`、`WriteGeneration`、dependency generation；
- read/write request、lease、publish/cancel；
- completion ticket value handle；
- `KisPixelAccessPlan`/session/TileView facade；
- generation-aware dirty event；
- memento/snapshot/immutable image epoch；
- `KisPaintExecutionContext` 和 document acceleration session slot；
- `KisEvaluationGraphTypes`、authoring lowerer、EvaluationEpoch、MutationRootSet 与 task planner contracts。

这里不包含 Vulkan、descriptor、queue、swapchain 或 device memory 类型。

### 3.2 `kritavulkanbackend`

实现：

- `VulkanDocumentGpuSession`；
- Vulkan `PageReplicaProvider`；
- UMA shared arena、dGPU fixed-slot direct/local binding、atlas/sparse optional path；
- `SubmissionCoordinator` 与 command/descriptor/allocation arena；
- `StrokeJournal` GPU upload view、`PageWorkCompiler` GPU encoding；
- page-batched stroke kernels；
- brush resource/pipeline preparation；
- incremental composite backend；
- DisplaySurface replica 和 `PresentRequest` 执行。

它不能链接 `kritaui`，不能实现第二套 SSD store，不能暴露 raw `VkQueue` 或 backend pointer 给 PaintOp。

### 3.3 `kritaui/vulkan` adapter

只实现：

- window/native surface descriptor adapter；
- DisplaySnapshot 选择；
- canvas transform、display intent、outline/decorations scene；
- `PresentRequest` 构造和 result 处理；
- resize/out-of-date/minimize 的 view event；backend WSI service 管理实际 swapchain generation、bounded acquire
  和 present packet。

它不读取 journal，不管理 target residency，不提交 undo/save，不直接调用任何 queue API。

## 4. BR0 中已经删除的旧文件/语义

下列代码不作为本文施工的前置依赖，也不留 compile flag：

- `KisVulkanPaintRouter::activeInstance`；
- `KisVulkanPaintOpFactory` 全局 wrap；
- `KisVulkanSyncStrokeStrategy` stroke-end download/writeBytes；
- `KisVulkanUpdateInfo` raw projection pixel payload；
- `KisVulkanTileData::Tier`；
- 旧 `TileCache`/`Prefetcher`/单 command-buffer `TransferQueue`；
- fixed 8192×8192 fallback image；
- projection、active layer、display image alias；
- `flushAndPause` 与同步 resize；
- fixed overwrite ring 和 CPU 每 dab 一 dispatch；
- render thread 同时消费 brush、composite、graphics、present 的 frame loop。

需要对照旧行为时从 archive branch 读取，不把旧源码复制回新树。

## 5. 可迁移内容的证明门槛

以下只是候选，必须先脱离旧对象图并通过独立测试：

- round/stamp/blend shader 数学函数；
- resolved dab 字段与 CPU dynamics 求值；
- preset analyzer 的纯解析；
- brush resource decoder、normalization 与 content key；
- device capability 查询；
- canvas transform、outline/decorations 算法；
- shader 构建基础设施；
- CPU reference 图像、golden 和 trace schema。

迁移单元必须满足：纯数据输入输出、无 global canvas/backend、无 queue API、无 canonical pixel ownership、
有明确 semantic version 和测试。原类“基本能用”不是迁移理由。

## 6. SB0：协议与 CPU reference

`SB*` 只表示 stroke build 工作包，不是全局 BR 阶段。

### 工作

- 冻结 `StrokeEpochDesc`、`ResolvedDab`、End/Cancel marker；
- 实现分块 immutable `StrokeJournal`；
- 定义 Accepted/Sealed/Compiled/Submitted/Executed/Visible/Recoverable 终态；
- 实现稳定 page/microtile 分桶；
- 实现 CPU page-batched reference executor；
- 建立 sequence accounting、batch partition invariance 和 overlap golden；
- 定义 journal/residency backpressure，队列满不丢已接受 dab。

### 出口

- accepted sequence 无缺口且全部有终态；
- 任意 batch/chunk 切分不改变输出；
- 同页重叠严格遵守 `(sequence, subSequence)`；
- page boundary、超大 dab、长 stroke 可以产生有界工作包；
- 无 Vulkan 环境可复现实验结果。

## 7. SB1：PageStore access plan

### 工作

- `PageWorkCompiler` 只使用 PageStore 公布的 logical page geometry；
- 生成 `StrokeAccessPlan` 的 read/write/resource/halo set；
- write request 预留 `WriteGeneration` 并声明 first-write snapshot；
- 同页 batch 依赖 previous-writer ticket；
- 编译输出只持 stable opaque GpuPageHandle/lease，不持物理 allocation；
- cancel/compile failure 归还 request，不能发布 generation。

### 出口

- compiler 中没有 bind/upload/download/SSD 调用；
- logical 64×64 tile 不被等同于 sparse granularity；
- 空白页由 PageStore 的 default generation 表示，不读取未初始化 allocation；
- lease 失败产生显式 batch failure，不画透明假数据。

## 8. SB2：Submission request 与资源退休

### 工作

- stroke 只构造 immutable `ComputeRequest`；
- request 显式列出 residency、binding publish、resource ready、snapshot、previous writer tickets；
- coordinator 生成 barrier、ownership transfer 和 timeline wait；
- command buffer、descriptor、transient dab buffer 持有 last-use ticket；
- completion 先校验 session/surface/page/write generation，再请求 PageStore publish；
- submit/device failure 触发 cancel/restore，不修改旧 published generation。

### 出口

- stroke 代码不调用 `vkQueueSubmit`/`vkQueueBindSparse`/`vkQueuePresentKHR`；
- async submit 后 command/descriptor/allocation 不提前 reset/reuse；
- 同/异 queue family validation 都通过；
- UI/input/stroke-end host wait 计数为零。

## 9. SB3：Page-batched GPU kernel

### 数据布局

```text
PageJobHeader[]
PageDabRef[]
ResolvedDab[]
MicrotileRange[]
ResourceHandleTable
```

每个目标像素只能由一个 invocation 写入。invocation 按稳定 dab ref 顺序执行 load/blend/store；不同页面和
无重叠 microtile 可并行。超大工作负载按 cost limit 切 micro-batch，相邻同页 micro-batch 由 ticket/barrier 排序。

### 首条 golden path

- Auto Round；
- Normal blend；
- pressure size/opacity/flow；
- spacing、rotation/aspect、mirror；
- 明确测试的 eraser/alpha 语义；
- RGBA8 可以是第一个 kernel variant。

RGBA8 只是第一条 golden，不是底层格式假设。MVP 必须通过 4/8/16 字节像素 `SurfaceFormat` 矩阵，并把没有
codec/kernel 的组合在 begin stroke 前整笔路由 CPU。

### 出口

- 同页数千 overlapping dabs 与 CPU reference 一致；
- CPU 不逐 dab 录制 dispatch/push constants；
- dispatch 数随 page/micro-batch 而不是 dab 数增长；
- GPU timestamp 与 CPU compile time 分离；
- 没有依赖缺失带来的“虚假高性能”。

## 10. SB4：UMA 与 dGPU 执行

### UMA

- write lease 返回 shared arena opaque GpuPageHandle；
- CPU pointer 与 GPU address 指向同一 physical page；
- coherent 仍执行 timeline ordering，non-coherent 执行 flush/invalidate；
- stroke end 不生成画布 download；
- 稳态 canvas-pixel copy counter 为零。

### dGPU

- write lease 返回 VRAM replica handle；
- restore/upload/binding publish tickets 成为 compute waits；
- compute publish 后 VRAM 可成为 authority；
- CPU/save/eviction 只 materialize 所需页面；
- authority handoff 失败时保留旧 replica；
- SSD 只使用 `kritaimage` 的 unified store。

### 出口

- 同一 journal/reference 在 UMA 和 dGPU 产生一致像素；
- VRAM→RAM→SSD→RAM→VRAM 强制迁移后 generation/checksum 一致；
- SSD fail/cancel/corruption 不丢失最后 authority；
- swapchain 阻塞时 stroke generation 继续推进。

## 11. SB5：EvaluationEpoch、任务图、合成与可见状态

### 工作

- stroke begin 捕获 immutable `EvaluationEpoch`/非空 writable targets，并把对应 value 映射为 mutation roots；
- EvaluationPlanner 只重建 requested output 的相交 task/pages；Layer lower/upper 是可选优化而非通用 ABI；
- target publish 只使相交 dependency pages 失效；
- lower checkpoint、upper operator/overlay/replay 按完整 generation vector 读取；
- composite completion 发布 derived DisplaySurface generation；
- Visible 与 Executed/Recoverable 分离；
- Presenter 选择最近完成 snapshot，构造 `PresentRequest`，不 host-wait。

### 出口

- backdrop-dependent upper 不在透明背景错误 flatten；
- display descriptor 精确绑定声明的 surface generation；
- target、projection、composite、display 不 alias；
- resize/minimize/out-of-date 不暂停 stroke；
- non-target `CoveredCold` 下沉不影响像素。

## 12. SB6：Undo、save、cancel 与 recovery

### 工作

- 第一次写页创建 generation COW before-image；
- End marker seal journal，commit 依赖最后 publish/recoverability ticket；
- 现有 `KisMementoManager`/oldData 演进为 generation snapshot reference；
- undo-before-complete 等待可能 writer 后发布 restore generation；
- cancel 对已执行 batch 做 snapshot restore；
- save 捕获 immutable image epoch/generation map；
- 缺页 save job 通过 continuation 挂起，ready 后续跑，不占 worker；
- device loss 用 durable replica 或 before-image+journal 恢复。

### 出口

- stroke end 不暂停 executor、不回读像素；
- undo/redo/cancel/save/reopen 与 CPU reference 一致；
- 保存期间新 stroke 写下一 generation，不污染快照；
- 失败只丢弃新 write generation，不污染旧 published generation；
- journal 只在 after generation 有安全恢复来源且 undo/redo 不再需要时退休。

## 13. SB7：Brush resource 与 capability

### 工作

- PaintOp 只持 immutable `PreparedBrushProgramHandle`；
- program identity 包含 semantic、resource、pipeline、format 和 recovery generation；
- preset 选中时异步 prepare，不在首 dab 上传/编译；
- begin stroke 前求 manifest、device、format、kernel、golden 的交集；
- `Supported` 才进入 GPU，其他整笔走同一 PageStore 的 CPU execution；
- texture/mask/predefined/airbrush/wash/neighbor-read 逐项增加 CPU/GPU golden；
- resource cache 受统一预算控制，不另建 canvas SSD/cache。

### 出口

- capability 的每个 `true` 对应 GPU golden 和 undo/save/pressure test；
- epoch 中不切 backend/resource generation；
- PaintOp 不持 raw backend/canvas pointer；
- 近似 Wash、未消费 ColorSource/Lightness 不宣称支持；
- device loss 所需 resource/journal 在 recoverability 前不会退休。

## 14. SB8：BR6 UI 接入

本文只规定 stroke 侧交付物；UI 接入由 BR6 执行：

- 后端完整初始化产生不可伪造的 `BackendReadyToken`；
- `KisImage` 的 backend-neutral slot 绑定 `VulkanDocumentGpuSession`；
- 同文档多 canvas 共享 session，不同文档隔离；
- canvas 只在 token、swapchain、session 都有效时启用；
- Presenter 只消费 DisplaySurface；
- CPU/OpenGL 是唯一产品 fallback；
- Tier 0–4 全通过后才开放 Vulkan 用户选项。

GPU stroke 不能自己打开隐藏设置，也不能因 Auto Round golden 通过就宣称产品入口可用。

## 15. 建议提交序列

以下提交可以独立审查，但必须嵌入全局 BR0–BR6：

1. `stroke: add immutable protocol and cpu reference`
2. `stroke: add chunked journal and sequence accounting`
3. `stroke: add stable page work compiler`
4. `stroke: bind access plans to canonical page leases`
5. `backend: add stroke compute request encoding`
6. `backend: add ordered page kernel rgba8 golden`
7. `backend: add format codecs and 4/8/16 matrix`
8. `backend: add uma pointer-bypass stroke path`
9. `backend: add dgpu replica stroke path`
10. `image: bind first-write cow and commit generations`
11. `image: add immutable save epoch and continuation jobs`
12. `backend: add evaluation-epoch incremental task/composite path`
13. `backend: add prepared brush resources and capability gate`
14. `ui: consume completed display surface only`

每个提交保持 CPU/OpenGL 可用、Vulkan 产品入口关闭，且不得暂时恢复旧 Vulkan runtime。

## 16. 禁止的过渡设计

- 给旧 `TileManager` 政名为 PageStore，同时保留 `64×64 == sparse block`。
- 建立 CPU tiled provider 与 GPU PageStore provider，然后 stroke-end 双写同步。
- 在 Vulkan backend 新建 SSD pack/index。
- 为了截图保留 global PaintRouter/factory wrap。
- 让 PaintOp 从 UI canvas 找 backend。
- 让 Presenter 直接 `vkQueuePresentKHR`。
- 用每 dab barrier 修补每 dab dispatch。
- 用更大的固定 ring 掩盖命令丢失。
- 用 `vkDeviceWaitIdle` 修复 resize、resource upload 或 shutdown race。
- 只支持固定 RGBA8 却让 `SurfaceFormat`/LoD capability 返回通用支持。
- 新路径失败后回落旧 Vulkan runtime。
- 以 compile flag 在源码树保留第二套 GPU stroke 状态机。

## 17. 验收清单

### 数据与集成

- Krita tile/COW/undo/swap 是唯一 canonical page identity；
- PaintOp 通过 `KisPaintExecutionContext` 获取正确文档 session；
- 多文档、多 canvas、关闭其中一个 canvas 不串扰；
- CPU/GPU stroke、filter、save、undo 消费同一 generation ledger。

### Stroke

- resolved/accepted/executed accounting 闭合，dab loss 为零；
- 同页 overlap、page boundary、batch partition golden 通过；
- command/dispatch 粒度是 page/micro-batch，不是 dab；
- stroke compute 不依赖 swapchain semaphore/image；
- backpressure 可观察且不冻结 UI。

### 同步与资源

- coordinator 独占 submit/bind/present；
- command/descriptor/allocation 按 ticket 退休；
- UI/input/stroke-end presenter wait count 为零；
- UMA canvas copy bytes 为零；
- dGPU/SSD authority handoff failure 保留旧 replica。

### Transaction

- first-write generation COW；
- undo-before-complete、cancel-after-submit、redo 正确；
- immutable save epoch 与并发新 stroke 隔离；
- device loss 对已放行能力可恢复或显式失败。

### Graph、格式与显示

- lower/upper dependency generation 精确；
- backdrop-dependent replay 正确；
- display descriptor 绑定正确 generation；
- 4/8/16 字节格式与不支持格式前置 CPU 路由通过；
- 未实现 mip/page pyramid 时 LoD 报告不支持；
- resize/minimize/present backpressure 不停止 stroke。

### 清洁度

- production tree 不含旧 runtime、兼容开关或第二套状态源；
- `kritavulkanbackend` 不链接 `kritaui`；
- Vulkan 用户入口只在完整 BR6/Tier 0–4 后开放；
- 所有完成声明可追溯到源码调用链、构建、validation、golden 和 trace。
