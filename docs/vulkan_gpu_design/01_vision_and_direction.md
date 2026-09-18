# 最终愿景与开发方向

> 状态与 MVP 定义以 [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md) 为准，全局 P0 数据模型与
> 模块硬边界以 [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md) 为准。
> 虚拟纹理的已决算法以 [32_virtual_texture_architecture_decisions.md](32_virtual_texture_architecture_decisions.md)
> 及 33–39 专题为准。本文只描述长期方向，不声明当前实现已经具备这些能力。

## 最终愿景

建立面向数字绘画的 GPU 原生图像系统，对标 Procreate 所体现的产品效果：低输入延迟、超大画布、快速图层操作，以及在内存压力下平滑而可预测的退化。

目标不是简单地把 OpenGL 显示替换为 Vulkan，而是重构像素存储、绘画、合成和缓存调度，使它们共同围绕统一页面系统工作。

## 核心方向

### 1. UMA-first，而不是独显-first 加兼容层

- UMA 上使用 CPU/GPU 共享的 mapped buffer page 作为权威像素存储。
- CPU 通过指针访问；GPU 热路径通过 storage buffer direct handle/operation-scoped binding 访问，稀疏目录只作后备。
- 访问域切换依赖 timeline、barrier 和 flush/invalidate，不复制像素。
- 独显使用相同逻辑页面模型，通过 VRAM cache 与 RAM backing 转录。

### 2. VRAM / RAM / SSD 统一虚拟纹理

- Krita 逻辑 tile、COW、undo、swap 定义唯一 canonical page identity；不为 Vulkan 平行重建 tile store。
- 页面位置对上层透明。
- Residency、dirty owner、generation、pin 和 in-flight 状态集中管理。
- SSD 直接演进现有 `KisTileDataStore`/`KisSwappedDataStore`，全项目只保留一套；它是临时工作集 backing，
  不是文档保存格式。
- sparse image、atlas 或 sampled image 都是设备后端或派生缓存，不能决定上层对象模型。

### 3. 以绘画目标集驱动调度

- 一个 stroke epoch 内只有 `ActiveTargetSet` 可写，通常只有当前图层。
- 非目标图层只读，可由 lower checkpoint、upper overlay/operator/replay cache 替代。
- 温度管理综合 viewport、笔迹预测、重建成本和替代缓存覆盖度，而不是只看最近访问时间。

### 4. GPU 原生绘画与局部合成

- CPU 将输入解析为不可变、单调有序的 resolved dab journal；已接受命令不会因固定 ring 满而丢失。
- dab 按目标页面稳定分桶，同页在一个 page job 内按序混合，不使用逐 dab dispatch/barrier。
- stroke compute、局部合成和 present 是三个票据化阶段；swapchain 不能阻塞笔迹执行。
- stroke end 不等待 GPU 或做整图 GPU→CPU 回读；撤销使用页级 copy-on-write、journal 和异步 commit ticket。

具体执行模型见 [10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md)。
具体的 journal、页级执行、同步、呈现和 Krita 存储边界分别见
[12_stroke_protocol_and_journal.md](12_stroke_protocol_and_journal.md)、
[13_page_work_compiler_and_gpu_kernel.md](13_page_work_compiler_and_gpu_kernel.md)、
[14_submission_tickets_and_queue_topology.md](14_submission_tickets_and_queue_topology.md)、
[16_incremental_composite_and_presenter.md](16_incremental_composite_and_presenter.md) 与
[17_krita_pagestore_integration.md](17_krita_pagestore_integration.md)。

### 5. 正确性优先于功能数量

- 位深、颜色空间、blend、mask、group 和非破坏节点必须有对照测试。
- 不支持的能力要明确门禁和回退，不能以近似结果冒充支持。
- 所有性能结论必须建立在像素一致性和内存安全通过之后。

### 6. 与 Krita 渐进集成

- 保留 CPU/OpenGL 路径作为对照和安全回退。
- 通过受控重置删除旧 Vulkan runtime，不以兼容开关保留错误数据模型；Vulkan 在 BR0–BR6 与整个 MVP
  验收前不可对用户启用。
- 先把 Krita 现有 tile/COW/undo/swap 演进为统一页面系统，再接入 replica、图层图、单层笔刷、撤销/保存和显示。
- 节点图、滤镜和高级笔刷共享同一 surface/page/residency 基础设施，避免继续增加特例资源路径。

### 7. 单向模块与文档会话

- 依赖由下游 `kritavulkanuiadapter -> {kritaui, kritavulkanbackend}` 组装；backend 只依赖 `kritaimage`，
  paintop 只依赖 backend-neutral session。
- `DocumentGpuSession` 归属 `KisImage` 的 backend-neutral slot；同文档多 canvas 共享，不同文档隔离。
- PaintOp 从 `KisPaintExecutionContext` 获取 session，不能访问 UI canvas 或全局 current router。
- `SubmissionCoordinator` 独占 submit、sparse bind 和 present；Presenter 只产生请求。

## 当前定位

仓库已有大范围 Vulkan 实验代码，但正常应用入口、虚拟纹理三层转录、UMA 权威共享页、自动温度管理、图层合成正确性和 GPU 端到端测试均未闭环。因此当前仍是架构实验分支，而不是已完成的 GPU 画布后端。
