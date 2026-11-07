# P0：模块边界、CMake 依赖与代码归属

> 本文解决当前 `kritaui ↔ kritaimagevulkan` 双向依赖和 `image_vulkan` 同时承载存储、PaintOp、RenderThread、
> compositor、graphics/UI 类型的问题。总纲见
> [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)。基础 target、private/public
> 代码层、运行时所有权和构建模式的最终细化见
> [41_vulkan_foundation_build_architecture.md](41_vulkan_foundation_build_architecture.md)；本文保留 P0 边界口径。

## 1. 当前事实

当前 `libs/image_vulkan/CMakeLists.txt`：

- target 名为 `kritaimagevulkan`；
- `PUBLIC` 链接 `kritaimage`；
- `PRIVATE` 链接 `kritaui`；
- 同一 target 内含 TileManager、TransferQueue、BrushEngine、RenderThread、LayerCompositor、PaintRouter、
  PaintOpFactory、NodeSync、SyncStrokeStrategy 和 GraphicsPipeline。

当前 `kritaui` 在 `HAVE_VULKAN` 时又链接 `kritaimagevulkan`。这已经形成：

```text
kritaui -> kritaimagevulkan -> kritaui
```

此外 UI 代码直接 include `KisVulkanPaintRouter`，后端代码包含 paintop/UI 业务，导致：

- 无法单独测试/复用 backend；
- 核心页面状态会被 canvas 生命周期支配；
- PaintOp 只能通过当前 active canvas 找路由；
- CMake/link 顺序掩盖层级错误；
- 任意 UI 类型进入 image backend 都可能再次制造环。

## 2. 最终依赖方向

逻辑调用方向是 UI/PaintOp consumer 使用 backend-neutral session，由 concrete Vulkan backend 实现。但 CMake
链接采用下游组合，避免让 `kritaui` 直接成为 concrete backend 的 owner：

```text
application composition root
  -> kritavulkanuiadapter -> { kritaui, kritavulkanbackend }
  -> GPU paintop adapter  -> kritaimage session contracts

kritavulkanbackend -> kritaimage
kritavulkanoffscreen -> kritavulkanbackend
```

禁止：

```text
kritaimage -> kritavulkanbackend
kritavulkanbackend -> kritaui
kritaimage -> kritaui
kritaui -> kritavulkanuiadapter
kritavulkanbackend -> kritavulkanuiadapter
```

`kritaimage` 通过 backend-neutral interface 允许 backend 实现被附着，不需要链接 concrete backend。

## 3. `kritaimage` 归属

必须位于核心图像库：

- `SurfaceId`、`LogicalPageId`、`Generation`；
- `SurfaceFormat`；
- PageStore/PageStateMachine；
- read/write lease；
- canonical/derived surface metadata；
- COW/memento/undo generation；
- 统一 SSD store/index；
- backend-neutral `CompletionTicket`/operation handle；
- `PageReplicaProvider` interface；
- backend-neutral document acceleration session slot/interface；
- `KisPaintExecutionContext` 中不含 Vulkan 的会话/能力 handle；
- CPU/reference replica provider 和状态机测试。

这些类型可以被 CPU-only Krita 构建使用，不能 include Vulkan SDK。

## 4. `kritavulkanbackend` 归属

新 target 只包含 Vulkan 实现：

- instance/device/queue/capability probing；
- `BackendReadyToken` concrete factory；
- Vulkan `PageReplicaProvider`；
- UMA shared arena 和 direct/local binding table；
- dGPU VRAM buffer/atlas/sparse optimization；
- `SubmissionCoordinator`、timeline、command arena；
- shader/pipeline/descriptor/resource backend；
- StrokeExecutor/PageWork GPU packing；
- incremental composite GPU backend；
- `VulkanDocumentGpuSession`；
- offscreen harness、validation 和 fault injection。

禁止包含/链接：

- QWidget/QWindow canvas 实现；
- `KisCanvas2`/`KisAbstractCanvasWidget`；
- `KisPresetShadowUpdater`；
- `KisUpdateInfo` UI pixel payload；
- swapchain policy/UI settings；
- paintop factory registration；
- `kritaui` export headers。

Vulkan surface/swapchain 的低层对象可由 UI adapter 通过窄接口委托 backend service 创建，但窗口事件、canvas
替换和 decoration 仍归 UI。若实现需要 Vulkan surface 类型，接口位于 backend 的 WSI adapter 层，不反向 include UI。

## 5. `kritaui/vulkan` adapter 归属

- window/native surface descriptor adapter；
- Presenter intent/display snapshot 消费与 result 处理；
- canvas widget 生命周期；
- viewport/transform/visibility hint；
- outline、guide、selection、assistant overlay；
- 设置页、用户能力报告和安全回退；
- 多 canvas view attachment；
- display filter/output color management adapter。

UI 不管理：

- canonical page；
- COW/snapshot；
- residency/eviction；
- stroke journal；
- transfer command buffer；
- queue submission；
- swapchain image/timeline 的同步真相；
- document transaction。

实际 `VkSurfaceKHR`/swapchain generation/acquire/present packet 由 backend 的窄 WSI service 管理；UI adapter 不得
因此获得 raw queue 或 canonical page。

## 6. PaintOp/plugin 归属

GPU PaintOp adapter 应位于 paintop plugin 或独立 GPU paint plugin，而不是 `kritavulkanbackend` 核心 target：

- 从 `KisPaintExecutionContext` 获取当前 document session handle；
- analyzer/dynamics 生成 backend-neutral `ResolvedDab`；
- 调用 session stroke protocol；
- semantic capability 不足，或 CPU-relative performance profile 不具备 `AutoPreferred` 时，在 begin stroke 首次写入前选择
  成熟 CPU paintop；
- 不 include canvas/router/UI；
- 不调用 Vulkan API。

纯 brush 数学/解析若 CPU/GPU 共用，应放在 backend-neutral brush library；Vulkan pipeline glue 留在 backend。

## 7. Public header 规则

### `kritaimage` public

- 不出现 `Vk*`、VMA、SPIR-V、QWindow/QWidget。
- ticket/handle 使用不可伪造 opaque id/interface。
- Surface/Page/Format 类型可序列化/测试。

### `kritavulkanbackend` public

只暴露：

- device service factory/ready token；
- document session factory；
- view/presenter attachment interface；
- capability descriptor；
- offscreen test hooks（测试 build）。

不得暴露 mutable global singleton、raw queue、raw page allocation 或 backend object pointer 给 UI/PaintOp。

### `kritaui` public

Vulkan canvas 类型不被 `kritaimage` 或 backend include。UI update 类型不得携带 canonical raw pixels 给 backend。

## 8. CMake 目标

目标结构示意；`kritavulkanbase` 是 internal target，shader assets 是生成 target，UI adapter 是同时消费 UI 与
backend 的下游组合层：

```cmake
kis_add_library(kritaimage ...)

kis_add_library(kritavulkanbase STATIC ...)
target_link_libraries(kritavulkanbase
    PRIVATE Vulkan::Vulkan GPUOpen::VulkanMemoryAllocator Qt::Core)

add_custom_target(krita_vulkan_shader_assets ...)

kis_add_library(kritavulkanbackend ...)
target_link_libraries(kritavulkanbackend
    PUBLIC kritaimage
    PRIVATE kritavulkanbase)
add_dependencies(kritavulkanbackend krita_vulkan_shader_assets)

kis_add_library(kritavulkanuiadapter ...)
target_link_libraries(kritavulkanuiadapter
    PRIVATE kritaui kritavulkanbackend)

target_link_libraries(kritagpupaintop
    PRIVATE kritaimage kritalibpaintop)
```

application composition root 在 BR6 后才注册 `kritavulkanuiadapter` 产品入口。`kritaui` 和 backend 都不反向链接
adapter。PaintOp 只依赖 backend-neutral session；concrete backend factory/registration 由应用组装。

`kritavulkanbackend` 的 command arena、binding table、shader/pipeline repository、stroke/composite/display executor 与
WSI implementation 默认 private，不因骨架阶段方便而形成 installed public ABI。

## 9. Shader 与生成资源

- shader source/build target 归 `kritavulkanbackend`。
- UI 不通过 compile definition 指向 backend 私有 build 目录。
- backend 提供 shader asset locator/embedded resource，初始化时验证全部 required shader。
- shader 缺失使 ReadyToken 创建失败，不能由 UI 在运行时猜路径继续。
- pure shader math 可以保留并迁移，但 descriptor/layout ABI 由新 backend 重新定义。

## 10. 依赖守卫

CI/构建必须检查：

- `kritavulkanbackend` target link/interface 不含 `kritaui`。
- backend source 不 include `libs/ui` 路径或 `kritaui_export.h`。
- `kritaimage` 不 include/link Vulkan。
- UI update info 不再定义 raw Vulkan canonical tile payload。
- paintop 不 include `KisVulkanCanvas`/PaintRouter。
- 构建图无 target cycle。

可使用 CMake configure-time assertion、include-what-you-use/clang-tidy rule 和 source grep 多层守卫。

## 11. 迁移/删除路线

1. 在干净 BR0 基线上保留旧代码于 Git 历史，不编译旧 target。
2. 在 `kritaimage` 建 backend-neutral core，并保持 CPU/OpenGL 行为。
3. 新建空的 `kritavulkanbackend`，只链接 `kritaimage`。
4. 迁移 device probing/shader build 等可独立证明代码。
5. 实现 replica/submission/stroke/composite backend。
6. UI 建窄 adapter 并链接 backend。
7. PaintOp 通过 execution context/session 接入。
8. 不迁移旧 RenderThread/PaintRouter/SyncStrokeStrategy 高层类。
9. 删除 `kritaimagevulkan` target、双向 link 和旧 include path。

## 12. 验收门槛

- CMake target graph 单向且 CI 自动检查。
- `kritavulkanbackend` 可在不链接 `kritaui` 的 offscreen test 中初始化。
- `kritaimage` CPU-only 构建不需要 Vulkan SDK。
- PaintOp 和 UI 都不访问 global active router/backend pointer。
- canonical PageStore/undo/SSD 完全位于 `kritaimage`。
- swapchain/UI 代码完全位于 UI adapter。
- 旧混合 `image_vulkan` target 不再编译、不留兼容开关。
