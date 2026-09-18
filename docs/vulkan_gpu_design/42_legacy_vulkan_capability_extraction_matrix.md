# 旧 Vulkan 基础能力、缺口与提取判定

> 本文以归档分支 `archive/vulkan-prototype-pre-br0-20260918`、归档提交 `7207640968` 为事实来源。
> 评分只表示“对新基线的可复用程度”，不表示旧功能完成度，也不授权把旧 runtime 整体复制回当前树。

## 1. 判定标尺

### 实现成熟度

- **M0**：只有声明/占位；
- **M1**：局部实验路径存在；
- **M2**：可组成原型链路，但语义或生命周期不闭合；
- **M3**：有较完整实现和自动测试；
- **M4**：达到新基线正确性、故障和产品门禁。

### 提取价值

- **E0**：不迁移，仅保留失败证据；
- **E1**：只参考行为/调用需求；
- **E2**：可提取局部纯算法，需重写接口和测试；
- **E3**：大部分纯实现可迁移，仍需接入新 ABI；
- **E4**：可直接迁移且已有充分证明。

本次审计没有任何项达到 E4。旧实现有实际研究价值，但没有足够的像素 golden、并发不变量或产品生命周期
证据可直接进入新 runtime。

## 2. 总体比较

| 能力域 | 旧原型事实 | 成熟度 | 提取价值 | 新基线结论 |
|---|---|---:|---:|---|
| instance/device/capability | 有 DeviceManager、queue family 查询、设备评分、logical device | M2 | E2 | 提取查询/评分规则；重写所有权和 ready 证据 |
| allocator/VMA | 有 MemoryPool、device/staging/UMA allocation helper | M2 | E1–E2 | 参考 allocation flags；重写 arena、budget、last-use 与错误传播 |
| queue/submission | 多模块直接持 queue；transfer/frame/brush 各自提交或等待 | M1 | E0–E1 | 整体重写为唯一 coordinator |
| shader build | 有 glslc/glslang CMake、SPIR-V 输出和 install | M2 | E2 | 保留编译探测思路；改为显式 manifest、reflection、hash、embedded asset |
| compute pipeline | 固定枚举加载 round/stamp/composite shader | M1 | E1 | 不迁移对象；按 pass ABI/pipeline repository 重建 |
| blend GLSL | 14 个 mode 纯函数和共享 apply/constants | M2 | E2–E3 | 最高价值候选；先补 alpha/color/CPU-GPU golden |
| round brush shader | SDF、rotation/aspect/softness、blend 数学 | M2 | E2 | 提取数学；丢弃 fixed rgba8 canvas 与 per-dab ABI |
| stamp brush shader | tip sampling、texture/mask 与 blend 实验 | M2 | E2 | 提取采样数学；资源/codec/page ABI 重写 |
| subgroup brush | 有 subgroup variant | M1 | E0–E1 | 暂不迁移；先证明普通 page-batched kernel，再由 benchmark 决定 |
| brush parser/dynamics | preset analyzer、dynamics、resource loader/cache/runtime | M2 | E2–E3 | 纯解析/求值/内容 key 单独迁移；Vulkan/cache ownership 重写 |
| sparse tile/cache | TileManager/TileData/TileCache/Prefetcher | M2 原型 | E0–E1 | 不迁移 runtime；只保留设备限制、trace 和失败用例 |
| UMA | 有 host-visible/VMA helper，但不是 canonical shared page | M1 | E1 | allocator flags 可参考；pointer bypass 全新实现 |
| SSD | `L3_Cold` 枚举，无 durable store 闭环 | M0–M1 | E0 | 不迁移；演进 Krita swap |
| layer compositor | fixed RGBA8 compute 和直接 layer dispatch | M1 | E2 数学 / E0 runtime | blend 研究可用；planner、generation、mask/filter/display 全重写 |
| NodeSync | CPU projection/layer 上传桥 | M1 | E1 | 只记录业务事件需求；上传/双权威路径删除 |
| display shader | fullscreen transform、bicubic、checker、pixel grid | M2 | E2–E3 | 提取纯采样/几何；DisplaySurface、color/output ABI 重写 |
| outline/decorations | vertex/fragment 与 bitmap overlay | M2 | E2–E3 | 提取算法和测试资产；资源/command 生命周期重写 |
| swapchain | format/mode/extent 选择、acquire/present、frame sync | M2 | E2 helpers / E0 owner | 提取纯选择函数；generation、bounded acquire、retirement 重写 |
| Canvas | 平台 surface、输入、显示、paint routing 的集成原型 | M2 | E1 | 只参考事件和 transform；类与所有权整体不迁移 |
| RenderThread | paint/composite/graphics/present 串在 frame loop | M1–M2 | E0–E1 | 记录工作类型；frame-coupled runtime 删除 |
| PaintRouter/factory | 可把 PaintOp 接到 Vulkan 原型 | M2 | E0 | global/current-canvas 模型永久删除 |
| sync stroke | stroke-end GPU→CPU writeback | M2 | E1 | 保留 transaction 业务需求；实现删除 |
| benchmark/trace | 有时间/内存统计基础 | M1 | E2 | 提取指标名称和场景；按新 ticket/page/session identity 重写 |
| tests | brush cache 与 blend enum/alias 为主 | M1 | E2 | 测试数据可迁移；不能证明像素、同步、合成或产品正确性 |

## 3. 基础平台能力

### 3.1 DeviceManager

旧能力：

- 创建 instance/device；
- 枚举 physical devices；
- 查找 graphics/compute/transfer/present queue families；
- 设备评分与部分 feature/limit 查询；
- 对外提供 raw device/queue。

真实不足：

- 生命周期与 UI `KisVulkan`/canvas 耦合；
- raw queue 可被任意模块使用，无法建立提交单写者；
- destructor/清理依赖 `vkDeviceWaitIdle`；
- 没有 device generation、device-lost 恢复和不可变 capability digest；
- 没有把 shader ABI、allocator、coordinator、provider smoke test 纳入 readiness。

提取：

- 将 physical-device 枚举、feature/limit 读取、queue topology 求解和纯评分规则提取为无 UI 的函数；
- 为同一 capability dump 建 fixture，比较新旧选择结果；
- raw handle 只进入 `KisVulkanDeviceService::Private` 与 coordinator 构造过程。

### 3.2 MemoryPool

旧能力：VMA buffer/image allocation、staging/host-visible/UMA flag 选择。

真实不足：

- “host visible”被混同为“UMA canonical zero-copy”；
- 没有 page generation、lease、authority 或 cache-maintenance 协议；
- allocation 不携带 last-use ticket；
- canvas、staging、brush resource、derived image 不在统一预算中；
- 没有 device-address/descriptor/atlas binding 的可移植能力矩阵。

提取：只保留内存类型探测、VMA 调用参数和设备兼容经验；新实现拆为 persistent page arena、transient arena、
staging lane、image/atlas resource 与 retirement record。

## 4. 提交和资源生命周期

旧 `TransferQueue`、`FrameResources`、`BrushEngine`、`Swapchain` 分别拥有 command buffer、fence 或 queue 调用；
还有同步 submit-and-wait、frame wait/reset 和 cleanup idle。

这组代码不能按类迁移，因为错误不是某个 wait，而是提交所有权分散：

- transfer completion 没有成为 compute/graphics 的统一 GPU dependency；
- 单 command buffer/固定 frame resource 在完成前有复用风险；
- sparse bind、compute、graphics、present 没有同一 DAG；
- destructor 用 device idle 掩盖 last-use 不明确；
- 失败/取消不会回到 PageStore publication transaction。

新实现只提取：

- queue family/ownership transfer 所需的设备事实；
- 旧调用链暴露的 workload 种类；
- 可转成 fault case 的时序；
- 计时与 debug label 需求。

任何旧 command/queue owner 都不得包入新 coordinator。

## 5. shader 与笔刷

### 5.1 blend 数学

旧树中的 add、burn、dodge、darken、difference、divide、exclusion、hard-light、lighten、multiply、overlay、screen、
soft-light、subtract 具有较好的纯函数边界，是最值得保留的成果。

未证明项：

- CPU `KoCompositeOp` 与 GPU 函数逐像素一致性；
- straight/premultiplied alpha 定义；
- linear/perceptual working space；
- 8/16-bit integer、half/float 与 rounding；
- NaN、denormal、zero divisor、out-of-range 处理；
- source/destination alpha 为 0/1 的边界；
- 不同 GPU/driver 编译结果。

迁移方式：提取到 `shaders/math/blend/`，为每个 mode 建 reference vector 和 image golden；只有有明确 semantic
contract 的 mode 才进入 pipeline manifest。

### 5.2 round/stamp

可提取：

- round SDF、rotation/aspect、hardness/softness；
- tip coordinate、mirror/rotation、mask/texture sampling；
- 与 `ResolvedDab` 对应的纯参数求值。

必须删除：

- `layout(rgba8) image2D canvas`；
- 一 dab 一 push/dispatch；
- shader 自行假定整张 canvas 坐标和边界；
- 固定 RGBA8/通道/alpha；
- 旧 ring buffer、raw resource index 和 canvas descriptor ABI。

这些数学进入 page-batched kernel 前，先在 CPU reference 与离线 shader test 中证明。

### 5.3 preset/resource/dynamics

应优先审计并迁移纯部分，因为它们比 Vulkan runtime 更接近业务语义：

- preset feature analyzer；
- dynamics 曲线/pressure/rotation/spacing 解析；
- brush tip 解码和归一化；
- resource content hash/cache key；
- begin-stroke capability gate 所需 feature vector。

不能迁移：backend pointer、预上传同步等待、Vulkan allocation cache、全局 factory wrap 和“parser 识别即代表 GPU
实现支持”的 capability 结论。

## 6. compositor

旧 `KisVulkanLayerCompositor`/`layer_composite.comp` 的有效成果是：验证 compute blend pass 的基本可行性，
并提供 blend GLSL 的实际调用场景。

不足是结构性的：

- fixed `rgba8 image2D`；
- full image/dirty rect 上逐 layer dispatch；
- 直接持 device/queue/image/memory/pipeline；
- descriptor 生命周期与清零/layout 不闭合；
- 只覆盖简单 visible paint layer；
- 不表达 group、mask、filter、pass-through、inherit alpha、clipping、backdrop dependency；
- 没有 GraphEpoch/dependency vector/cache invalidation；
- 输出 image 未可靠成为 canvas 实际采样源；
- resize/shutdown 使用 device idle。

因此：

- blend 函数 E2–E3；
- shader dispatch/descriptor ABI E0；
- compositor class E0；
- dirty region 与 layer metadata 输入只能作为 E1 行为参考。

新 compositor 从 `LayerSegmentPlanner -> CompositeAccessPlan -> page executor -> derived surface publication` 重建。

## 7. display、outline 与 canvas

### 7.1 display shader

可提取：fullscreen triangle、widget/image transform、Catmull-Rom bicubic、checkerboard、pixel grid。它们是 view
算法，不拥有 canonical page。

缺失：DisplaySurface page/atlas sampling、颜色管理、soft proof/display filter、HDR/output transform、surface
generation、resource lifetime 和 capability fallback。

### 7.2 outline/decorations

可提取几何和 fragment 算法，也可复用演示输入。但旧 graphics pipeline 的 descriptor、buffer upload、command
record 和 frame ownership 必须重写。

### 7.3 Swapchain

`chooseSurfaceFormat`、`choosePresentMode`、`chooseExtent` 是纯函数候选，应提取为带输入 fixture 的测试。其余
Swapchain 类不迁移：它自己 acquire/present、持 frame command/sync，并在 destroy 调用 device idle。

### 7.4 Canvas

旧 Canvas 的价值是平台集成清单：surface 创建、resize、input、viewport transform、outline、decoration、屏幕和
device pixel ratio。它不能迁移，因为同时拥有 TileManager、RenderThread、PaintRouter、Compositor、GraphicsPipeline
并写全局成功状态。

新 UI adapter 可逐项核对旧事件覆盖，但不得复用类或对象图。

## 8. 虚拟纹理与存储

旧 TileManager/sparse canvas 证明了 sparse bind、tile upload/download 和 viewport prefetch 的探索价值，但不能成为
新虚拟纹理底座：

- logical tile 被近似等同 sparse granularity；
- dirty eviction 可在 durable handoff 前解绑；
- `Tier/L3_Cold` 没有 SSD record；
- prefetch age/LRU 不理解 ActiveTargetSet/GraphEpoch/CoverageCertificate；
- fallback dense 8192×8192 不是可扩展后端；
- GPU canvas 与 Krita tiles3/COW/swap 形成双权威；
- UMA 只是 allocation/staging 变体。

可保留：设备 sparse property dump、测试场景、trace 字段、bind failure case。实现 E0。

## 9. 测试资产

旧测试实际覆盖以 enum/alias、resource cache/preset 为主。它们不证明：

- blend 像素数学；
- overlapping dab memory ordering；
- transfer/compute/graphics/present dependency；
- layer graph 语义；
- format/color/alpha；
- resize/device loss；
- undo/save/reopen；
- VRAM/RAM/SSD 迁移；
- 多文档/多 canvas。

处理：保留输入数据和业务断言，测试代码按新 target 重定位。所有 capability 必须新增对应的 CPU/GPU golden、
failure 和 lifecycle test，旧测试数量不能作为迁移完成证据。

## 10. 逐文件族处理表

| 旧文件族 | 处理 | 新归属 | 最早进入 production 的阶段 |
|---|---|---|---|
| `KisVulkanDeviceManager` | 提取 query/selection；owner 重写 | `kritavulkanbase` | BR0 foundation/BR2 readiness |
| `KisVulkanMemoryPool` | 参考 VMA flags；类不迁移 | backend `memory/` | BR3 |
| `KisVulkanTransferQueue` | 删除 | coordinator transfer packet | BR2 |
| `KisVulkanFrameResources` | 删除 | arena/reclaimer | BR2 |
| `KisVulkanComputePipeline` | 删除 | shader catalog/pipeline repository | BR0 foundation/BR2 |
| blend `.glsl` | 提纯 + golden | shader math | foundation test，BR4/BR5 使用 |
| dab shaders | 提取数学；pass 重写 | shader math + `stroke/` | BR5 |
| `KisVulkanPresetAnalyzer/Dynamics` | 提取纯解析/求值 | backend-neutral brush/paintop | BR5 gate |
| resource loader/cache/runtime | decoder/key 可迁移；GPU cache 重写 | brush core + backend resources | BR5 |
| TileManager/Data/Cache/Prefetcher | runtime 删除 | PageStore/provider/residency | BR1/BR3/BR4 |
| `KisVulkanLayerCompositor` | 删除；blend/fixtures 提取 | planner + composite executor | BR4 |
| `KisVulkanNodeSync` | 删除；事件需求进入 graph invalidation | `kritaimage` graph/page bridge | BR4 |
| display shaders | 提取纯 view math；pass 重写 | backend `display/` | BR6 |
| GraphicsPipeline | 删除 | pass-specific executors/repository | BR4/BR6 |
| Swapchain | helpers 提取；owner 重写 | backend `wsi/` | BR6 |
| Canvas/macOS surface code | 事件/平台事实参考 | UI adapter + native descriptor | BR6 |
| RenderThread | 删除 | scheduler + coordinator + view ticks | BR2–BR6 |
| PaintRouter/Factory wrap | 永久删除 | explicit execution context | BR5 |
| SyncStrokeStrategy | 业务需求参考 | generation transaction | BR5 |
| Benchmark | schema/scene 提取 | diagnostics | foundation 起持续扩展 |

## 11. 防止再次过度清理的规则

- 归档分支在每个 foundation/BR work package 开始时都必须做相关文件族审计；
- “不迁移类”不等于“不迁移算法、fixture、平台限制和故障场景”；
- 每个删除项在本矩阵中必须有 replacement owner 或明确“不再需要”的理由；
- 可提取内容先进入 isolated test/asset target，不可为了保留成果而接回产品 runtime；
- 若新设计发现旧能力无对应 owner，先修正文档/target 图，再写实现；
- 若旧实现比新方案多覆盖一个真实产品行为，必须补入需求/验收，不允许因删除代码而删除需求。

## 12. 最终判定

BR0 删除旧运行路径是正确的；将所有 shader、device/display 算法同时从当前可见源码树移出则是过度清理，
但修正方式不是恢复旧目录。正确方式是：

1. 从归档逐项提取纯算法与测试资产；
2. 在新 target 边界内建立新的 ABI 和所有权；
3. 先用 offscreen/golden 证明，再进入 BR1–BR6 production 集成；
4. 永久拒绝恢复 global router、sparse canvas authority、frame-coupled render thread 和双向 CMake。
