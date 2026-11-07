# BR0 代码切换与骨架清单

本文只记录代码落位事实，不把类存在、TODO 或 target 可配置等同于功能完成。全局设计以
[22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md) 为准，阶段出口以
[31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md) 为准。

> 二次结构审计后的 Foundation skeleton 已落位，但仍不是 BR1–BR6 完成声明。device/shader/memory/pipeline、
> submission/resource、composite/display 和 backend WSI 已有结构性 API 与状态校验；native Vulkan 实现仍显式
> 不可用。部分 internal 类已取消 export，最终 installed ABI 仍需随阶段冻结。修订方案见
> [41_vulkan_foundation_build_architecture.md](41_vulkan_foundation_build_architecture.md) 与
> [43_foundation_construction_sequence_and_gates.md](43_foundation_construction_sequence_and_gates.md)。
>
> 2026-09-20 状态更新：本文的 BR0 inventory 仍用于追溯 foundation 落位；PageStore/tiles3 的功能 cutover 以 51
> 为历史证据，resident CPU production path 和布局以
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md) 为当前状态。

## 1. 归档与删除

- 仓库：内层 `krita` Git 仓库。
- 归档分支：`archive/vulkan-prototype-pre-br0-20260918`。
- 归档提交：`7207640968`。
- 归档范围：完整父提交中的旧 Vulkan tree，加上删除前 `libs/image_vulkan` 与 `libs/ui/vulkan` 的 35 个
  工作区修改。
- 当前树删除：完整旧 `libs/image_vulkan` runtime、旧 `libs/ui/vulkan` 实现与旧 Vulkan UI/image 测试；
  `libs/ui/vulkan` 路径随后只放入未接产品的全新 adapter skeleton。
- 当前树删除语义：`kritaimagevulkan`、UI 双向依赖、global active router、factory wrap 入口、stroke-end
  writeback runtime、raw projection tile payload、旧 Canvas 配置成功标记。

恢复旧实现只能显式读取归档分支。禁止把归档目录整体复制回当前树；纯算法迁移仍需满足
[21_implementation_and_baseline_cutover.md](21_implementation_and_baseline_cutover.md) 的证明门槛。

## 2. `kritaimage` PageStore 与文档边界

目录：`krita/libs/image/pagestore`。

| 骨架 | 固定责任 | 当前方法体状态 | 首次实现阶段 |
|---|---|---|---|
| `KisPageStoreTypes` | Surface/Page/Generation、format、request、lease、transaction、epoch、opaque ticket | 通用 request/lease 功能已接线；resident CPU guard/mutation session API 仍按 52 调整 | BR1（功能完成；PERF 进行中） |
| `KisSurfaceRegistry` | 文档内 canonical/derived surface identity | 已实现线程安全 identity/register/query/remove；外部引用门禁仍由 PageStore 承担 | Foundation/BR1 |
| `KisPageStateMachine` | 唯一 production/reference transition 与不变量 | transition/invariant 功能已实现；production fast guard 必须复用语义但退出 reference 容器/调用粒度 | BR1（功能完成；PERF 进行中） |
| `KisImageEpochReferenceModel` | immutable 多页 committed view、transaction overlay、conflict/rebase | persistent root/delta 已落地；owner/cursor 未冻结，transaction start/删除 extent/allocatedPages 仍导出 owning snapshot（53） | BR1（P4 部分完成） |
| `KisPageMetadataCoordinator` | stable shard、page-state owner、completion queue、materialization dedup | correctness/dedup、virgin default read、trusted transition 已实现；D1 virtual default 状态/回收定向通过（54），generic 消费仍可能物化，正式 guard/page-local pin 与 K/N 门禁未关闭 | BR1（功能完成；PERF 进行中） |
| `KisPageStore` | read/write request、lease、publish/cancel、epoch commit | canonical authority、同步 host adoption、exclusive fused commit/history retirement、history delta restore/release 已接通；通用 mutable CPU 写仍经过完整协议 | BR1（功能完成；PERF 进行中） |
| `KisPageReplicaProvider` | backend-neutral replica 契约 | 已要求 provider id/epoch、PageStore operation id、lease-scoped resolve/release access 及 exact-materialize/write-init transfer kind；production CPU provider 已接通，SSD/Vulkan 仍非 canonical provider | BR1/BR3 |
| `KisTiledDataManagerPageStoreBackend` / `Shadow` | tiles3 到 Surface/Page/generation 的 authority bridge 与迁移对照 | native read、batch/adoption/no-op 已接通；history adapter 全量 index rebuild、删除 extent 扫描及 mutation/permit 均待落实（53） | BR1（功能完成；PERF 进行中） |
| `KisCompletionRegistry` | GPU timeline、CPU job、I/O 的统一 opaque ticket bridge | 已实现线程安全 source、单调 ticket、终态冲突拒绝 | Foundation；native bridge 在 BR2 |
| `KisSurfaceCodecRegistry` | exact `SurfaceFormat` codec 选择 | 已实现 codec identity/version 注册、重复拒绝、ambiguous claim fail-closed | Foundation/BR1 |
| `KisBackendServiceRegistry` | 不可变 device service 证据与唯一 ready-token 构造边界 | 已验证完整 report、精确 generation、revoke；当前无真实 report producer | Foundation/BR2 |
| `KisDocumentGpuSession` | 文档归属的 backend-neutral acceleration session；按 operation/version/input-output ValueType/format 查询能力 | 纯接口与精确 capability contract | BR2/BR3/BR4 |
| `KisPaintExecutionContext` | PaintOp 显式 document/writable-target-set/session/capability snapshot | 只接受显式构造数据 | BR5 接线 |
| `KisUnifiedSsdPageStore` | 演进现有 swap 的唯一 SSD provider | 不声明 durable/Ssd capability | BR3 |
| `KisResidencyController` | safety 后的语义温度、预算和迁移计划 | 不产生迁移 | BR4 |
| `KisEvaluationGraphTypes` | immutable typed EvalGraphIR、EvaluationEpoch、value/port/edge/context contract | 开放 ValueType、逐端口 format 和 fail-closed validation 已落位 | BR4 |
| `KisEvaluationGraphLowerer` / `KisLayerStackLowerer` | versioned authoring snapshot → EvalGraphIR；Layer 仅是兼容 frontend | schema gate 已落位，lower 恒失败 | BR4 |
| `KisEvaluationPlanner` | EvalGraphIR requested outputs → backend-neutral execution task DAG | 不产生 plan | BR4 |
| `KisDerivedSurfaceCache` | operation/input/property/context-qualified surface cache 与 CoverageCertificate | 查询恒 miss、publish 拒绝 | BR4 |
| `KisCompositeTypes` | 一种 surface operation access plan、DisplaySurface snapshot | extensible operation identity 与 validation contract 已落位 | BR4/BR6 |

这些 public header 禁止出现 Vulkan、VMA、window/canvas 类型。`KisBackendReadyToken` 构造私有，当前只有
`KisBackendServiceRegistry` 是 friend；默认 token 永远 invalid。

## 3. Backend-neutral stroke 协议占位

目录：`krita/libs/image/gpustroke`。

| 骨架 | 固定责任 | 当前方法体状态 | 首次实现阶段 |
|---|---|---|---|
| `KisGpuStrokeTypes` | StrokeEpoch、ResolvedDab、sealed batch、ordered page/microtile work | 只有不可变协议字段与 validity 检查 | BR5 |
| `KisStrokeCoordinator` | journal、backpressure、batch、end/cancel | 不接受 stroke/dab，不产生 commit | BR5 |
| `KisPageWorkCompiler` | 按 logical page 稳定分桶并保持 sequence/subSequence | 返回 unsupported plan | BR5 |

这些类位于 `kritaimage`，允许 CPU reference test 和 PaintOp 使用；它们不得包含 Vulkan API、canvas 或 raw queue。

## 4. `kritavulkanbackend` 占位

目录：`krita/libs/vulkanbackend`。该 target 只 `PUBLIC` 链接 `kritaimage`，不链接 `kritaui`。

| 骨架 | 固定责任 | 当前方法体状态 | 首次实现阶段 |
|---|---|---|---|
| `KisVulkanFoundationTypes/DeviceService` | device/queue capability 与完整 readiness evidence | capability/evidence/state/revoke 校验已实现；无 native probe | Foundation/BR2 |
| `KisVulkanShaderCatalog` | shader identity/hash/reflection/ABI manifest | register/seal/digest/失败闭环已实现；manifest 明确不可 seal | Foundation |
| `KisVulkanMemoryBudgetLedger` | native allocation 前的统一预算 reservation | hard/high/low budget 与 reservation/release 已实现 | Foundation/BR3 |
| `KisVulkanPipelineRepository` | generation-qualified pipeline identity/state | declare→prepare→prepared/failed/retired 状态机已实现 | Foundation/BR2+ |
| `KisVulkanResourceRetirementQueue` | last-use ticket 后资源回收 | 多 completion source 的有界收集契约已实现 | Foundation/BR2 |
| `KisVulkanBackendBootstrap` | device service 初始化证据、失败报告和 session factory | 可验证完整 evidence/report/token；普通 initialize 明确报告缺 probe | BR2/BR3 |
| `KisVulkanSubmissionCoordinator` | 唯一 queue submit/bind/present owner与timeline DAG | 完整 packet/config/dependency 校验；native submit 仍关闭 | BR2 |
| `KisVulkanCommandArena` | timeline 后 command buffer 回收 | config/capacity/retirement 校验；native pool 未安装 | BR2 |
| `KisVulkanPageBindingTable` | operation-scoped、generation-qualified 映射 | completed snapshot 原子发布、精确 lookup、invalidate 已实现 | BR3 |
| `KisVulkanPageReplicaProvider` | UMA/dGPU 物理 replica 和迁移 | dependency/domain/budget 契约可配置；native allocation/transfer 明确失败 | BR3 |
| `KisVulkanDocumentGpuSession` | 文档隔离的 concrete session | 有强 generation identity，停在 Initializing，不接受工作 | BR3–BR5 |
| `KisVulkanStrokeExecutor` | page-batched compute preparation | 验证精确 writable generation 和 dab order；native encode 未实现 | BR5 |
| `KisVulkanCompositeExecutor` | exact composite pass preparation | 验证 dependency/output binding/pipeline；native encode 未实现 | BR4 |
| `KisVulkanDisplayExecutor` | exact DisplaySurface pass preparation | 验证 snapshot/binding/format/pipeline；native encode 未实现 | BR6 |
| `KisVulkanWsiService` | backend-owned surface/swapchain generations | view intent/update/retire 状态机已实现；swapchain 保持 Awaiting | BR6 |

这些占位不能按当前 public 形状直接补实现：`CommandArena`、`PageBindingTable`、`StrokeExecutor` 应成为 backend
private；`SubmissionRequest` 需要补齐 command/resource/ownership/failure packet 语义。新 target 还必须先补齐
device、allocator、shader catalog/pipeline repository、resource retirement、composite、display 和 WSI owner。

## 5. `kritavulkanuiadapter` 占位

目录：`krita/libs/ui/vulkan`。它是独立 downstream target，同时消费 `kritaui` 与 `kritavulkanbackend`；两者都不
反向链接它，`KisCanvas2` 和应用也不接入它。

| 骨架 | 固定责任 | 当前方法体状态 | 首次实现阶段 |
|---|---|---|---|
| `KisVulkanViewAttachment` | 同文档多 view、session/token generation 校验 | 可登记/更新/退休 WSI intent；当前 session 不会 Ready | BR6 |
| `KisVulkanPresenter` | 构造 immutable display/view present intent | validation contract 已实现，不拥有 acquire/present | Foundation/BR6 |
| `KisVulkanCanvasAdapter` | token/session/swapchain/display/MVP 产品原子门禁 | 返回结构化拒绝原因；当前无证据可通过 | BR6 |

UI 只在拿到真实 ready token、matching document session、display surface 和 swapchain generation，并且完整 MVP
门禁通过后，才允许把 adapter 接入正常 canvas。

## 6. 当前静态门禁

`krita/build-tools/ci-scripts/check-vulkan-architecture.sh` 当前检查：

- 旧 runtime 目录和旧 target/symbol 不得回到当前树；
- `kritavulkanbackend` target 必须存在且不得链接 `kritaui`；
- disabled `kritavulkanuiadapter` target 必须存在，但不得进入 `KisCanvas2` 产品路径；
- backend 不得包含 UI/window/canvas 类型；
- 除 `SubmissionCoordinator` 外不得出现 queue submit/bind/present API；
- 新 backend 与 UI adapter 不得出现 device/queue idle、无限等待；UI adapter 不得调用 queue API。

当前脚本通过只证明结构负向条件；C++ 编译、Vulkan 初始化和 CPU/OpenGL 回归证据独立记录在
[45_br0_build_and_regression_evidence_20260918.md](45_br0_build_and_regression_evidence_20260918.md)，仍不构成像素端到端或性能结论。

`libs/vulkanbackend/tests/KisVulkanFoundationContractsTest.cpp` 已加入 registry、shader catalog、memory budget、
pipeline state、binding provider epoch、coordinator/WSI generation 的 contract tests；BR1 复验结果为 13/13
通过（BR0 冻结证据为 11/11）。backend-neutral Foundation 为 21/21，PageStore production/reference、CPU access、
history/GC/fault/stress 与 tiles3 产品回归的最终矩阵见 51。真实 Vulkan/VMA compute offscreen smoke 继续通过；这些结果
构成 BR1 边界复验，但不构成 BR2 submission、BR3 Vulkan replica 或产品 Vulkan 入口完成声明。

## 7. BR0 关闭状态

1. 目标 revision 已固定为 `origin/master` `9a24ae0d8c`；未修改 baseline 的 CPU/OpenGL 构建与稳定核心
   回归 5/5 通过。
2. BR0 净变更已重放到该基线，并重新通过 CPU-only、Vulkan foundation、shader ABI/offscreen、PageStore、
   architecture guard 和 CPU/OpenGL 6/6 对照套件；产品入口、target DAG 与 public/private 边界未回退。
3. BR0 已正式关闭。51 只关闭 BR1 功能/正确性 cutover；BR1-PERF 仍按 52 推进，结清前不得进入 BR2 production
   接线。不得把 foundation smoke 或 BR1 功能证据扩写为性能或后续阶段完成证据。
