# Vulkan Foundation 施工顺序、构建门禁与 BR0 修订

> 状态更新：本文记录 BR0 Foundation 施工边界；51 记录了 2026-09-19 的 BR1 功能/正确性 cutover，2026-09-20
> resident CPU 性能审计后 BR1 以 `BR1-PERF` 重开，见
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)。文中的
> “current skeleton/BR1–BR6”判断按历史时点理解；当前 production 执行阶段仍是 BR1-PERF。

> `F*` 是 BR0 内部的基础结构工作包，不是新的全局阶段编号。全局仍只有 BR0–BR6。`F*` 可以准备 isolated
> code/test，但不得绕过相应 BR 出口接入 production document、PaintOp 或 canvas。

## 1. 为什么需要 Foundation 工作包

当前树已经完成旧 runtime 删除和单向 target 占位，但存在三个风险：

1. **骨架过早公开**：command buffer、binding table、stroke executor 等实现细节已经以 shared-library export 形式出现；
2. **基础能力无 owner**：device、allocator、shader、pipeline、composite、display、WSI 尚无新类/目录/构建计划；
3. **能力资产被隔离但未提取**：旧 blend/brush/display shader、device query 和 swapchain helper 只在 archive 中，
   尚未进入 isolated test/asset 流程。

因此当前 BR0 不能按“补完七个空壳”继续。先完成 F0–F6，再冻结 BR1/BR2 接口。

当前执行快照（2026-09-18）：

- F0：target/owner/public-private 设计和 legacy 判定已完成；
- F1：`kritavulkanbase`、显式 shader asset target、backend、internal UI adapter target 已落 CMake，CPU-only 与
  foundation 配置/构建均已验证；
- F2：legacy extraction matrix 已完成，算法/fixture 尚未复制进入新树；
- F3：device evidence、shader catalog/ABI、memory/pipeline contract 已落位；build-generated SPIR-V、reflection/ABI
  校验、native Vulkan/VMA compute offscreen smoke 已实现并通过；
- F4：完整 submission packet、completion source 和 resource retirement contract 已落位，native queue executor 尚未实现；
- F5：SurfaceVersion/access view、private executor、composite/display/WSI skeleton 已完成第一轮重排；
- F6：工具链、未修改 upstream baseline、重放后 CPU-only/foundation 构建、architecture guard、真实
  offscreen smoke 和稳定核心回归均有证据；BR0 净变更已位于目标 upstream 之上，BR0 已关闭。

## 2. F0：结构冻结

### 工作

- 以 [41_vulkan_foundation_build_architecture.md](41_vulkan_foundation_build_architecture.md) 冻结 target DAG；
- 逐个 current skeleton 标记 public、private、provisional；
- 为 device/submission/memory/shader/page/stroke/composite/display/WSI/diagnostics 指定唯一 owner；
- 建立 legacy extraction manifest；
- 确认 CPU-only、foundation developer、product 三种状态不是同一个开关；
- 将新文档纳入总纲和 BR0 出口。

### 出口

- 不存在“某项旧能力已删但新架构无 owner”；
- 不存在两个模块都可 submit、publish、present 或销毁 device resource；
- public header 白名单明确；
- current skeleton 明确不是冻结 ABI。

## 3. F1：CMake target 图和配置模式

### 3.1 首先构建空 target 图

建议顺序：

```text
kritaimage
kritavulkanbase (internal)
krita_vulkan_shader_assets (generated)
kritavulkanbackend
kritavulkanoffscreen/test support
kritaui
kritavulkanuiadapter (internal, not product-registered)
application composition root (no Vulkan activation)
```

示意 CMake：

```cmake
if(BUILD_VULKAN_FOUNDATION)
    add_subdirectory(vulkanbackend/base)
    add_subdirectory(vulkanbackend/shaders)
    add_subdirectory(vulkanbackend)
endif()

if(BUILD_TESTING AND BUILD_VULKAN_FOUNDATION)
    add_subdirectory(vulkanbackend/tests)
endif()

if(BUILD_VULKAN_FOUNDATION)
    add_subdirectory(ui/vulkan) # target exists, product registration remains absent
endif()
```

名称只是示意，最终以 Krita 已有 option 规范落地；关键是状态分离：

- `Vulkan SDK found` 是工具链事实；
- `foundation target built` 是构建事实；
- `backend runtime Ready` 是运行时事实；
- `product Vulkan canvas enabled` 是 BR6 产品门禁事实。

### 3.2 public/private 规则

- `kritavulkanbase` 不 install、不导出 public header；
- `kritavulkanbackend` 只安装确有外部消费者的 factory/interface；
- command arena、binding table、shader catalog、pipeline repository、executors 和 WSI implementation 全部 private；
- `kritavulkanuiadapter` 在 MVP 完成前不作为稳定安装 ABI；
- offscreen test hooks 只在 test build 暴露，不能进入普通 application public interface。

### 3.3 配置矩阵

至少验证：

| 配置 | Vulkan SDK | shader tool/assets | backend | UI adapter | 产品入口 |
|---|---:|---:|---:|---:|---:|
| CPU-only | 不要求 | 不要求 | 不构建 | 不构建 | 关闭 |
| foundation compile | 要求 | 必须完整 | 构建 | 可构建未注册 | 关闭 |
| offscreen CI | 要求 | 必须完整 | 构建并运行测试 | 不要求 | 关闭 |
| WSI CI | 要求 | 必须完整 | 构建 | 构建测试 | 关闭 |
| product | 要求 | 必须完整 | Ready | 连接 | 仅 BR6+MVP gate 后开放 |

### 出口

- CMake configure graph 无环；
- CPU-only 不查找 shader compiler/VMA；
- foundation target 不链接 `kritaui`；
- UI adapter 不被 `kritaui` 或 backend 反向链接；
- shader 缺失不会得到一个伪 Ready backend。

## 4. F2：legacy extraction lab

### 工作

从 archive 按内容、不是按旧类迁移：

1. 复制纯 shader math 到隔离目录；
2. 提取 device capability/queue topology 的纯查询和评分测试 fixture；
3. 提取 preset/resource/dynamics 的纯数据测试；
4. 提取 display transform/bicubic/checker/grid/outline 算法；
5. 提取 surface format/present mode/extent 选择 helper；
6. 保存旧 benchmark scene、trace 字段、failure reproduction；
7. 为每项建立 provenance：archive path、commit、修改说明、semantic contract、测试。

候选在通过证明前只能进入：

```text
tests/reference/
tests/fixtures/
shaders/math/
tools/offscreen/
```

不能进入 product source list 或 capability advertisement。

### 出口

- [42_legacy_vulkan_capability_extraction_matrix.md](42_legacy_vulkan_capability_extraction_matrix.md) 每项有实际去向；
- blend/brush/display 候选至少能独立编译；
- 纯算法不 include UI、旧 TileManager、旧 global Vulkan singleton；
- 没有把旧 descriptor/push constant ABI 搬入新树。

## 5. F3：device service 与 shader foundation

### 5.1 device service

实现顺序：

```text
instance probe
 -> capability dump
 -> queue topology solver
 -> device selection
 -> logical device generation
 -> allocator creation
 -> debug/fault reporting
```

先使用 offscreen harness，不连接 document/session/canvas。必须验证：

- 无适配 device、缺 extension/feature、allocator failure 的结构化失败；
- unified queue family 和独立 queue family 两套拓扑；
- device generation 失效；
- raw queue 不离开 base→coordinator 构造路径；
- teardown 不依赖未知工作的 `vkDeviceWaitIdle`。

最后一条在 foundation smoke 阶段可以通过“所有测试 work ticket 已知且完成”关闭；真正多消费者 drain 在 BR2 完成。

### 5.2 shader assets

实现：

- 显式 source manifest；
- include dependency；
- deterministic flags；
- SPIR-V validation；
- reflection/生成 C++ ABI 描述；
- content hash/semantic ABI；
- embedded or installed resource 的统一 locator；
- missing/mismatch negative tests。

先迁移最小 foundation shader：buffer fill/copy/checksum 和一个无业务含义的 graphics/offscreen pass。旧 brush/
composite shader 不作为 device ready 的必需资产，直到对应 BR 能力被正式支持。

### 出口

- offscreen device + allocator + required foundation shader 初始化可复现；
- 不产生 product ready token，或 token capability 明确仅为 foundation/test；
- shader path 不依赖 build directory compile definition；
- reflection mismatch 在构建或初始化时硬失败。

## 6. F4：submission/resource 协议预研

F4 只建立 BR2 所需的 private protocol、fake model 和最小 offscreen smoke；BR2 才冻结并完成 production coordinator。

### 工作

- 定义 immutable submission packet；
- 实现 fake coordinator/reference DAG；
- 定义 queue lane、timeline source、ticket completion；
- 定义 command/descriptor/transient resource last-use record；
- 定义 sparse bind、compute、graphics、present packet 的同一依赖表示；
- 定义 cancellation、submit failure、device loss continuation；
- 用最小 Vulkan buffer fill/copy/checksum 验证 timeline 与 resource retirement。

### 禁止

- 将当前三字段 `KisVulkanSubmissionRequest` 冻结为 public ABI；
- 暴露 command buffer lease 给 executor/UI；
- 让 offscreen test 之外的模块自行调用 queue；
- 以 `waitIdle` 代替 retirement；
- 在 PageStore 尚未完成时创造新的 GPU page authority。

### 出口

- fake 与 Vulkan smoke 使用同一 packet 语义；
- command/resource 在 completion 前无法回收；
- 静态检查确认 coordinator 之外没有 queue API；
- 尚不宣称 BR2 完成。

## 7. F5：骨架重排与缺失类占位

只有完成 F0–F4 设计后才调整 class skeleton。建议动作：

### 保留并继续演进

- `KisBackendServiceRegistry`、`KisCompletionRegistry` 的原则；
- `KisPageStore`、`KisPageStateMachine`、`KisPageReplicaProvider`；
- `KisDocumentGpuSession`、`KisPaintExecutionContext`；
- `KisEvaluationGraphTypes`、`KisEvaluationGraphLowerer`、`KisLayerStackLowerer`、`KisEvaluationPlanner`、
  `KisDerivedSurfaceCache`；
- `KisStrokeCoordinator`、`KisPageWorkCompiler`；
- `KisVulkanBackendBootstrap`、`KisVulkanSubmissionCoordinator`、`KisVulkanPageReplicaProvider` 的责任名称。

### 改为 backend private

- `KisVulkanCommandArena`；
- `KisVulkanPageBindingTable`；
- `KisVulkanStrokeExecutor`；
- 未来 shader/pipeline/allocator/composite/display/WSI executor。

### 新增占位

- base：device service、capability snapshot、queue topology、allocator；
- submission：packet、arena set、resource reclaimer；
- shaders：manifest/catalog/pipeline repository；
- evaluation/composite：authoring lowerer、EvalGraphIR、task planner、access plan adapter、specialized composite executor；
- display：DisplaySurface snapshot、display executor；
- WSI：native surface descriptor、swapchain session、present result；
- diagnostics：trace ids/counters/failure report。

### 需要修正的现有类型

- 增加 `SurfaceVersion`/derived surface snapshot，不能用一个 page version 表示整 surface；
- lease 返回 typed CPU view 或 operation-scoped GPU access view；
- capabilities 从 bool 集合演进为按 operation/version/port ValueType/format/feature 的 immutable descriptor；
- ticket 明确 source generation、completion/failure/cancel；
- view id、document id、service id 使用不同强类型；
- UI presenter 不产生虚构 completion ticket，实际 WSI operation 由 backend service 返回。

所有 TODO 方法继续显式失败，直到对应 BR 工作包有测试驱动实现；不得用空成功值打通演示。

## 8. F6：BR0 构建和回归关闭

### 必须执行的构建

1. 目标 upstream 的未修改 CPU/OpenGL baseline；
2. 当前树 CPU-only configure/build；
3. 当前树 foundation configure/build；
4. `kritaimage` 和 PageStore reference tests；
5. vulkan base/shader/offscreen smoke；
6. architecture guard；
7. Krita CPU/OpenGL core regression。

### 必须记录

- upstream/base SHA、编译器、Qt、Vulkan loader/SDK、shader compiler；
- CMake options；
- GPU/driver/capability dump；
- 测试命令、结果和 validation output；
- 失败环境与 unsupported reason。

### BR0 修订出口

BR0 只有在下列全部满足后关闭：

- 旧错误 runtime 与入口已删除；
- archive 可复现；
- foundation target 图和 public/private 边界已冻结；
- legacy extraction manifest 完整；
- CPU/OpenGL 回归通过；
- CPU-only 与 Vulkan-foundation 构建通过；
- foundation shader/device/offscreen smoke 通过；
- 产品 Vulkan 入口仍关闭；
- current skeleton 未被虚假声明为 BR1–BR6 implementation。

如果当前环境缺工具链，只能记录“F0/F2 文档和静态门禁完成”，不能关闭 F1/F3/F6。

2026-09-18 的实际执行记录见
[45_br0_build_and_regression_evidence_20260918.md](45_br0_build_and_regression_evidence_20260918.md)。净变更已重放到
目标 upstream，并在重放后的树上复验全部门禁；BR0 已正式关闭，BR1 可以按既定顺序开始。

## 9. Foundation 之后的全局顺序

F0–F6 不替代后续阶段：

| 全局阶段 | 允许使用的 foundation 成果 | 该阶段仍必须完成的核心 |
|---|---|---|
| BR1 | contracts/reference/fakes | Krita tile/COW/undo/swap 的唯一 canonical PageStore |
| BR2 | device/shader base、submission packet/fake | production coordinator、timeline DAG、retirement、fault closure |
| BR3 | allocator/page binding skeleton | UMA/dGPU/RAM/SSD replica 与强制迁移 |
| BR4 | evaluation/composite skeleton | EvalGraphIR/reference lowerer/task DAG、EvaluationEpoch、layer optimization、derived cache、温度和 composite correctness |
| BR5 | brush math/parser/resource fixtures | journal/page work/kernel/undo/save 的 GPU stroke 闭环 |
| BR6 | display math/WSI skeleton | 多 view、swapchain generation、color/display、fallback 和产品门禁 |

任何 foundation smoke 都不能提前宣称对应 BR 完成。

## 10. 推荐提交切分

每个提交保持 CPU/OpenGL 可用和产品 Vulkan 入口关闭：

1. `docs: freeze vulkan foundation target and ownership graph`
2. `build: separate cpu-only, vulkan foundation and product gates`
3. `build: add private vulkan base and generated shader asset targets`
4. `tests: add archived capability and shader extraction fixtures`
5. `vulkan: add offscreen device capability service skeleton`
6. `vulkan: add shader manifest reflection and ABI validation skeleton`
7. `vulkan: add private submission packet and fake coordinator model`
8. `vulkan: add command/resource retirement skeleton`
9. `refactor: reduce public backend ABI and relocate internal skeletons`
10. `tests: record BR0 cpu and foundation build evidence`

不应在同一提交同时做 upstream rebase、删除旧 runtime、重排所有 skeleton 和迁移 shader；那会使失败无法归因。

## 11. 停止条件

遇到以下任一情况停止实现并回到设计：

- 新类需要 include `kritaui` 才能初始化 device/page/submission；
- executor 需要 raw queue 或自行 publish PageStore；
- UI adapter 需要 canonical page pointer；
- shader ABI 只能靠手写重复 layout 且无法校验；
- 旧行为无法在 owner 图中找到位置；
- 为显示首帧需要恢复 sparse canvas authority、projection upload 或全局 active router；
- 为清理资源需要无界 `vkDeviceWaitIdle`；
- 缺 shader/compiler 时仍准备发放 ready token。

这些不是“先跑起来再修”的小问题，而是说明 foundation 边界仍未闭合。
