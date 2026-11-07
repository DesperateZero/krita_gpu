# Vulkan GPU 项目状态与 MVP 口径

本文定义项目状态词和 MVP 产品边界。全局 P0 数据模型与模块边界以
[22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md) 为准，唯一执行顺序以
[31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md) 为准。其他设计、阶段、专题文档
必须同时与三者一致；当源码、测试证据与文档冲突时，以可复现的源码调用链、构建结果和测试结果为准。

## 1. 状态词定义

- **代码存在**：仓库中有类、接口、shader 或调用框架；不代表可以编译或运行。
- **已接线**：存在从 Krita 正常入口到该模块的调用链；不代表结果正确。
- **已验证**：有可复现的构建、运行或自动测试证据。
- **已完成**：已接线、已验证，并满足本阶段全部验收标准。
- **实验实现**：代码可供继续验证，但不能作为用户可用能力或性能结论。

禁止以提交数量、文件数量、枚举值、TODO 被删除或单元测试只覆盖 CPU 解析为“已完成”的依据。

## 2. 当前事实基线（2026-09-25）

BR1 的唯一当前执行入口为 [92](92_br1_m6_m8_execution_baseline.md)，生产修复检查点为 `5173c807c8`。默认像素更新与历史恢复的准备顺序、manager 构造预算拒绝，以及 metadata/index/descriptor/root 安装的资源准备已修复；以 [本轮证据](evidence/br1_m5_repair_20260925/README.md) 的同源码验证授予阶段资格。

| 范围 | 当前状态 |
|---|---|
| BR0 | 已完成，生产 Vulkan 路径保持关闭 |
| M5 修复基线 | 已通过，可进入 M6；双架构 CPU/业务 2,964 passed、Vulkan foundation 28 passed，真实 install 零分配及两桶性能回归通过 |
| M6 | 下一实施阶段：recoverable backing handoff；尚未实现 |
| M7 | M6 通过后：bounded commit-only handoff；尚未实现 |
| M8 | 业务 scope、剩余迁移、资源/退出、清理与正式资格待完成 |
| BR1 / BR1-PERF | 尚未完成；必须通过 39 的正式 upstream M/K/E、尾延迟、容量及生命周期门 |
| BR2–BR6 production | 尚未开放；foundation 兼容不代表产品接线 |

当前生产仍为 Fresh allocation/COW，不宣称已经实现 recoverable/commit-only handoff。TSAN 保持 Inconclusive，确定性交错、预算、失败与退出测试单独验收。

47–91 共 45 篇文档已 [移入归档目录](archive/br1_pre_m6_20260925/README.md)。原始版本可从来源提交恢复，失败记录和证据保留；它们退出当前状态及执行口径，仍有效的 BR1 约束已归并到 92。旧关闭/重开判断只属于相应历史提交，不与本节并列维护。

## 3. 第一个 MVP 的不可裁剪目标

第一个 MVP 不是“能显示画布”或“能画一笔”，而是同时满足以下能力：

1. **统一页面模型**
   - 逻辑 Krita tile、GPU 物理页、RAM backing 和 SSD record 有明确映射。
   - 页大小和绑定粒度来自设备能力，不能假设固定 64×64 逻辑 tile 等于 sparse block。

2. **VRAM / RAM / SSD 自动透明转录**
   - 上层通过 surface/page 访问接口请求读写，不直接执行 bind、upload、download 或 SSD I/O。
   - dirty、authoritative copy、generation、pin、in-flight、timeline 和失败状态由统一状态机维护。
   - 在强制小预算和频繁迁移下不能丢失像素。

3. **UMA-first 指针旁路**
   - UMA 是一等后端，不是独显 staging 方案的兼容分支。
   - 权威页优先使用可持久映射、CPU/GPU 共享的 buffer page arena。
   - CPU/GPU 所有权切换通过 barrier、timeline 和 flush/invalidate 完成；零复制不等于零同步。
   - sampled image/atlas 可以作为派生显示缓存，但不能成为 UMA 权威副本。

4. **独显后端**
   - 使用同一页面状态机，在 VRAM cache 与 RAM backing 之间异步转录。
   - GPU 提交必须显式等待相关 transfer/sparse-bind 完成。

5. **SSD backing store**
   - 直接演进 Krita 现有 `KisTileDataStore`/`KisSwappedDataStore`，提供页索引、generation、校验、空间回收和异步读写。
   - 全项目只保留这一套 SSD page store；Vulkan backend 不得另建 L3/cache/swap。
   - SSD 层是临时工作集的外存，不代替 Krita 文档保存格式。

6. **绘画感知的自动温度管理**
   - 温度不能只是普通 LRU/age。
   - 必须考虑目标图层、viewport、笔迹预测、dirty 写回代价、重建代价、依赖扇出和替代缓存覆盖度。

7. **通用求值图、目标图层剪枝与派生缓存**
   - Layer Tree 与未来 Flow authoring model 必须 lower 到同一个 immutable、typed `EvalGraphIR`。
   - `EvaluationEpoch` 的 `MutationRootSet` 可为空；每个 stroke 另行冻结非空 `writableTargets` 并映射为 mutation roots。
   - Layer frontend 可把非目标节点识别为只读，形成下层 checkpoint、上层 overlay/operator/replay cache；该分类不是通用图 ABI。
   - 被有效派生缓存覆盖的非目标源页可以快速降温并转录到 RAM/SSD。

8. **GPU 原生笔迹执行**
   - resolved dab 进入不可变、可恢复的 stroke journal，固定队列满时不得丢弃。
   - dab 按目标页面稳定分桶；同页严格保持笔迹顺序，不同页并行。
   - stroke compute 使用独立 submission lane，不能位于 swapchain acquire/present 的前置或同一帧生命周期中。
   - 驻留、资源、前序写入、计算与合成都使用 GPU timeline ticket 串联；交互热路径禁止 host GPU wait。
   - stroke end 关闭 epoch 并返回 commit ticket，不暂停 render thread，也不触发整笔像素回读。

9. **可验证的绘画闭环**
   - 后端只有在产生不可伪造的 `BackendReadyToken`、建立 swapchain 和文档 session 后才可替换普通 canvas。
   - Vulkan 用户入口在 BR0–BR6 和整个 MVP 验收全部通过前保持不可用；校正期间使用 CPU/OpenGL。
   - 单层笔刷、显示、撤销/重做、保存/重开有像素一致性测试。
   - 不允许用固定大图 fallback、手工迁移或 stroke-end 整图回读冒充虚拟纹理 MVP。

10. **CPU 相对的自动执行路由**
   - GPU/UMA 的产品性能基线是同机、同质量、启用实际 SIMD/线程/COW/PageStore 的 CPU 产品路径，不是 scalar reference。
   - correctness capability 与 `AutoPreferred` 分离；设备可用、共享映射或零拷贝都不能单独触发 GPU route。
   - stroke/evaluation 在首次写入前按完整端到端 ETA 冻结 CPU 或 accelerator route，不允许逐 dab/逐页混跑来掩盖选择错误。
   - GPU 劣势、低功耗/温控、queue contention、UMA 共享带宽竞争下，Auto 必须满足
     [39_virtual_texture_performance_gates.md](39_virtual_texture_performance_gates.md) 的 CPU-relative 上限，否则前置选择 CPU。

## 4. 统一对象模型

唯一 canonical 身份来自 Krita 逻辑 tile、COW、undo 和 swap；UMA、RAM、VRAM、SSD 与显示资源只是同一
generation 的 replica 或 derived consumer。目标模块边界如下：

- `SurfaceRegistry`：注册 canonical surface 与 derived surface。
- `PageStore`：位于 `kritaimage`，吸收并演进现有 tile data、COW/memento 和 swap，管理唯一逻辑页 identity、
  generation、lease、authority、RAM/UMA 与 SSD record。
- `KisPixelAccessSession`/iterator facade：向 `KisPaintDevice` 暴露既有 tile/iterator 行为；它是 canonical
  PageStore 的访问门面，不是第二个 provider 或并行存储。
- `PageStateMachine`：维护权威副本、dirty、generation、pin、in-flight 与错误状态。
- `ResidencyController`：根据预算、温度与依赖决定驻留和转录。
- `UmaPageBackend`：提供共享 mapped page 和访问权切换。
- `DiscreteGpuPageBackend`：提供 VRAM cache、transfer 与 sparse/atlas 后端。
- unified SSD provider：由现有 `KisTileDataStore`/`KisSwappedDataStore` 演进，只存在于 `kritaimage`。
- `DocumentGpuSession`：归属 `KisImage` 的 backend-neutral session slot；同文档多 canvas 共享，不同文档隔离。
- `KisEvaluationGraphLowerer`：把 versioned authoring snapshot 转为统一、不可变的 `EvalGraphIR`。
- `KisLayerStackLowerer`：现有 Layer Tree 的兼容 frontend，并可附加 lower/target/upper 优化提示。
- `KisEvaluationPlanner`：从 requested outputs 生成 ROI/依赖明确的 backend-neutral execution task DAG。
- `KisDerivedSurfaceCache`：按 operation/input/property/context generations 保存可丢弃、可重建的图像输出。
- Value/Resource Store：保存 scalar/text/tensor/model/external artifact 等非 surface value；不得并入 PageStore。
- `StrokeJournal`：保存不可变 resolved dab chunk 和恢复所需命令历史。
- `PageWorkCompiler`：将连续 dab 序列稳定编译为有序 page job。
- `StrokeExecutor`：执行 page-batched kernel，不逐 dab 提交。
- `SubmissionCoordinator`：统一 queue submission、timeline ticket 和延迟资源回收。
- `IncrementalEvaluationScheduler`：把目标页 generation 变化传播到局部 DisplaySurface。
- `Presenter`：只为最近已完成的 DisplaySurface 构造 `PresentRequest`；实际 `vkQueuePresentKHR` 仍由
  `SubmissionCoordinator` 独占。

构建依赖永久固定为 `application -> kritavulkanuiadapter -> {kritaui, kritavulkanbackend}`、
`kritavulkanbackend -> kritaimage`；paintop 只依赖 `kritaimage` 的 backend-neutral session contract。
`kritavulkanbackend` 不得链接 `kritaui`，paintop 通过 `KisPaintExecutionContext` 获取文档 session，不访问 UI canvas。

旧 `KisVulkanTileManager`、`KisVulkanTileCache`、`KisVulkanTransferQueue`、`KisVulkanTilePrefetcher` 只存在于
归档分支，是历史实验输入，不是当前源码树模块，也不得被重新接入新边界。

GPU stroke 的执行与同步细节以 [10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md) 为准。
当前旧路径的问题证据见 [11_current_path_failure_inventory.md](11_current_path_failure_inventory.md)。GPU stroke
内部施工见 [21_implementation_and_baseline_cutover.md](21_implementation_and_baseline_cutover.md)；全局 P0
删除边界和 BR0–BR6 顺序见 [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md)。

## 5. 通用求值与图层剪枝口径

Authoring Graph、EvalGraphIR 和 Execution Task DAG 必须分离。通用 IR 用 typed ports/edges 表达 source、diamond、
fan-out 和多输出，不出现 lower/upper 或 Vulkan 类型；纯生成/显示图允许空 `MutationRootSet`。

仅当 Layer Tree lower 后识别出线性绘画结构时，单目标图层栈至少拆为：

```text
只读下层 -> LowerCheckpoint
当前目标 -> WritableTarget
只读上层 -> UpperCache / UpperReplay
```

- 下层 checkpoint 是独立于目标层的精确输入。
- 上层只有在 blend/group 语义允许时才能预合成为 overlay。
- 对 backdrop 有非线性依赖的上层必须保存 replay bundle 或按脏区重算，不能把透明背景上的 RGBA 快照当成普遍正确结果。
- 多目标操作把图层图切成 `C0 -> T0 -> C1 -> ... -> Tn -> Cn`，其中 `C` 是只读 segment，`T` 是可写目标。
- “当前 stroke 不可写”不等于节点永远不可变；图层属性、滤镜、动画、Flow 连接或外部编辑会创建新的
  evaluation/stroke epoch 并使相关缓存失效。

## 6. 温度与回收口径

页面角色至少包括：

- `CurrentWrite`：当前正在写的目标、output 和必要 before-image；active lease/in-flight 由安全层硬保护。
- `PredictedWrite`：笔尖预测 corridor，使用有期限 soft pin。
- `VisibleExact`：当前 viewport 所需 checkpoint、upper cache 和 display dependency。
- `ReplayOrCheckpoint`：下一次局部重算会读取的源页/checkpoint。
- `UndoOrSaveRetention`：transaction、undo 或 immutable save 引用页。
- `CoveredCold`：已被有效派生缓存覆盖的非目标源页，优先下沉。
- `OffscreenCold`：不可见且短期无依赖。
- `DerivedDiscardable`：可由 canonical page 重建，压力下可直接丢弃。

回收必须遵守：

- dirty page 在安全写回前不可解绑或复用；
- pinned/in-flight page 不可回收；
- derived cache 可以丢弃，但 canonical data 必须至少有一个权威副本；
- 迁移决策需要迟滞，避免 VRAM/RAM/SSD 之间反复抖动。
- `CoveredCold` 必须由 EvaluationEpoch/dependency generations 完整的 `CoverageCertificate` 证明。

## 7. 路线顺序

全局只采用 BR0–BR6；本目录内其他 `G*`、`VT*`、`GS*`、`SQ*` 等编号均为专题工作包，不能覆盖此顺序：

1. **BR0**：归档原型，从更新后的目标 upstream 建干净分支；删除旧 Vulkan runtime、入口和双向依赖，
   保持 Vulkan 不可用并证明 CPU/OpenGL 回归。
2. **BR1**：把现有 tile/COW/undo/swap 吸收到 canonical PageStore；先证明纯 CPU 像素一致。
3. **BR2**：建立独占全部 queue API 的 `SubmissionCoordinator`、timeline DAG、command arena 与资源退休。
4. **BR3**：接入 UMA、dGPU、RAM、SSD replica；通过 pointer bypass 与强制迁移校验。
5. **BR4**：建立 EvalGraphIR/reference lowerer、EvaluationEpoch、通用 task DAG、derived cache、图层剪枝和语义温度。
6. **BR5**：GPU stroke 消费 page lease/ticket，完成 generation COW undo 与 immutable save epoch。
7. **BR6**：UI 只消费 derived DisplaySurface；完成多 canvas、WSI、颜色/显示过滤和安全回退后才开放用户选项。

## 8. 文档维护规则

- 每项能力分别记录“代码存在、已接线、已验证、已完成”。
- 没有构建与运行证据时，不写“可运行”“零阻塞”“完全兼容”或具体性能数字。
- 没有 SSD 文件格式和读写实现时，不把 `L3` 称为 SSD 层。
- 没有共享权威像素页时，不把 host-visible staging/ring buffer 称为 UMA 画布零拷贝。
- 没有端到端 GPU 输出对照时，不把 preset 解析或资源加载测试称为笔刷端到端测试。
- 没有与真实 CPU 产品路径对照的 CPU-only/forced accelerator/Auto 结果时，不以 GPU timestamp、零拷贝或 capability
  supported 声明 GPU/UMA 性能完成。
- 设计目标与当前实现必须分段书写，不能混在同一完成清单中。

## 9. 专题文档路由

- 全局 P0 总纲：[22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)
- 模块/CMake：[23_p0_module_boundaries_and_build_graph.md](23_p0_module_boundaries_and_build_graph.md)
- 后端入口/文档 session：[24_p0_backend_lifecycle_and_document_sessions.md](24_p0_backend_lifecycle_and_document_sessions.md)
- Canonical PageStore/Krita tile/COW/swap：[25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md)
- BR1 条件 COW/backing handoff/硬预算：[68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md)
- BR1 PageStore 拆分/冗余/侵入审计：[69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md](archive/br1_pre_m6_20260925/documents/69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md)
- UMA/dGPU/RAM/SSD replica：[26_p0_replica_uma_dgpu_ssd.md](26_p0_replica_uma_dgpu_ssd.md)
- 虚拟纹理算法决策总纲：[32_virtual_texture_architecture_decisions.md](32_virtual_texture_architecture_decisions.md)
- PageStore 状态机与并发：[33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md)
- GPU binding/slab/atlas/sparse：[34_virtual_texture_gpu_binding_and_arenas.md](34_virtual_texture_gpu_binding_and_arenas.md)
- UMA 指针旁路：[35_virtual_texture_uma_pointer_bypass.md](35_virtual_texture_uma_pointer_bypass.md)
- dGPU 迁移与 backpressure：[36_virtual_texture_dgpu_migration.md](36_virtual_texture_dgpu_migration.md)
- SSD segment store：[37_virtual_texture_ssd_segment_store.md](37_virtual_texture_ssd_segment_store.md)
- 语义温度与预测：[38_virtual_texture_residency_temperature.md](38_virtual_texture_residency_temperature.md)
- 虚拟纹理性能决策门禁：[39_virtual_texture_performance_gates.md](39_virtual_texture_performance_gates.md)
- Submission/线程/零阻塞：[27_p0_submission_threading_zero_blocking.md](27_p0_submission_threading_zero_blocking.md)
- Evaluation Graph/Projection/Display：[28_p0_graph_epoch_projection_display.md](28_p0_graph_epoch_projection_display.md)
- SurfaceFormat/LoD/capability：[29_p0_surface_format_lod_capabilities.md](29_p0_surface_format_lod_capabilities.md)
- CI 架构守卫：[30_p0_ci_architecture_guards.md](30_p0_ci_architecture_guards.md)
- 受控重置与唯一全局执行顺序：[31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md)
- 新基线基础结构与 target/运行时所有权：[41_vulkan_foundation_build_architecture.md](41_vulkan_foundation_build_architecture.md)
- 旧 Vulkan 能力、缺口与逐项提取判定：[42_legacy_vulkan_capability_extraction_matrix.md](42_legacy_vulkan_capability_extraction_matrix.md)
- Foundation 施工与 BR0 构建门禁：[43_foundation_construction_sequence_and_gates.md](43_foundation_construction_sequence_and_gates.md)
- Shader/compositor/canvas 重建：[44_shader_compositor_canvas_reconstruction.md](44_shader_compositor_canvas_reconstruction.md)
- BR0 构建、测试与 upstream 对照证据：[45_br0_build_and_regression_evidence_20260918.md](45_br0_build_and_regression_evidence_20260918.md)
- 虚拟纹理现状/旧代码证据：[09_virtual_texture_status_and_roadmap.md](09_virtual_texture_status_and_roadmap.md)
- Stroke 如何消费 residency：[15_stroke_residency_and_memory_backends.md](15_stroke_residency_and_memory_backends.md)
- GPU stroke 总纲：[10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md)
- 当前路径问题与删除边界：[11_current_path_failure_inventory.md](11_current_path_failure_inventory.md)
- 命令协议与无丢失日志：[12_stroke_protocol_and_journal.md](12_stroke_protocol_and_journal.md)
- 页级 compiler/kernel：[13_page_work_compiler_and_gpu_kernel.md](13_page_work_compiler_and_gpu_kernel.md)
- Queue/ticket/线程同步：[14_submission_tickets_and_queue_topology.md](14_submission_tickets_and_queue_topology.md)
- 合成/DisplaySurface/Presenter：[16_incremental_composite_and_presenter.md](16_incremental_composite_and_presenter.md)
- Krita PixelStore/PageStore 集成：[17_krita_pagestore_integration.md](17_krita_pagestore_integration.md)
- Undo/保存/取消/恢复：[18_undo_save_cancel_and_recovery.md](18_undo_save_cancel_and_recovery.md)
- Brush resource/能力门禁：[19_brush_resources_and_capability_gate.md](19_brush_resources_and_capability_gate.md)
- 验证/性能门禁：[20_observability_testing_and_performance.md](20_observability_testing_and_performance.md)
- GPU stroke 代码施工与 BR5 接入：[21_implementation_and_baseline_cutover.md](21_implementation_and_baseline_cutover.md)
