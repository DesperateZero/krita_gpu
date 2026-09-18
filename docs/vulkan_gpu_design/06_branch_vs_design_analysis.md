# Vulkan 分支现状与目标架构差距

> 本文记录源码审查结论，不把计划代码当成已完成能力。统一状态见 [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md)。
> 当前 GPU stroke 路径的逐项证据、风险与退出边界见 [11_current_path_failure_inventory.md](11_current_path_failure_inventory.md)。
> 全局 P0 结论和受控重置方案见 [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)
> 与 [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md)。

## 1. 归档原型中曾存在的代码

以下事实来自 `archive/vulkan-prototype-pre-br0-20260918` / `7207640968`。这些文件已从当前 production tree
删除；本节是 legacy capability 审计，不表示当前树仍可运行这些能力。

- Vulkan instance/device/queue/swapchain/memory pool。
- `KisVulkanCanvas`、graphics pipeline、render thread、outline/decorations。
- sparse canvas、tile/cache/transfer/prefetch 实验模块。
- round/stamp brush compute、ring buffer、preset analyzer、brush runtime/resource cache。
- layer compositor、NodeSync、paint router、sync stroke strategy。
- blend 映射、少量 CPU 侧单元测试。

这些内容证明方向已有较大代码投入，但不能证明正常应用可进入该路径或像素结果正确。

## 2. 归档路径的关键断点

### 2.0 模块边界与文档会话

- `kritaimagevulkan` 私有链接 `kritaui`，`kritaui` 又私有链接 `kritaimagevulkan`，形成构建层双向依赖。
- `KisVulkanPaintRouter::activeInstance()` 和 factory wrap 把 PaintOp 目标绑定到全局当前 canvas，无法保证多文档隔离。
- canvas、render thread、PaintOp 之间传播裸 backend 指针，生命周期与线程所有权不闭合。
- 当前 Vulkan 库混合 device、tile、PaintOp、RenderThread、Compositor 与 UI 类型，不能成为长期模块边界。

### 2.1 入口

- `KisVulkan::initialize()` 没有正常应用调用者。
- `useVulkanCanvas` 缺少完整设置路径。
- `VULKAN_STARTED` 在真实 surface/swapchain 成功前写入。

### 2.2 页面系统

- 固定 64×64 逻辑 tile 与设备 sparse granularity 没有正确解耦。
- dirty eviction 没有先保存权威数据。
- transfer timeline 没有进入 graphics/compute 的 GPU wait。
- prefetch bind 后没有保证把 backing 内容恢复到 GPU。
- staging 预算超限没有回收策略。
- `L3_Cold` 没有 SSD backing。
- fallback 是固定 8192×8192 dense image，不代表虚拟纹理兼容后端。

### 2.3 UMA

- 当前 UMA 检测只影响部分 allocation flag。
- ring buffer 的 host-visible 映射不等于画布像素零拷贝。
- sparse/optimal image 不能被当作可移植的线性 CPU 像素指针。
- 尚无共享权威 buffer page、access lease 或 cache maintenance 状态机。

### 2.4 图层合成

- compositor image 没有绑定到实际 canvas descriptor。
- composite target 未建立可靠的清零与 layout 状态。
- descriptor set 每次 dispatch 分配，缺少生命周期回收。
- NodeSync 只遍历根节点直接 paint layer。
- 非活动层内容变化不能可靠触发像素重新上传。
- image projection 与 active-layer sparse surface 的语义互相冲突。

### 2.5 笔刷

- preset/resource CPU 侧解析已有基础。
- analyzer 放行了一些运行时没有真实消费的能力。
- Wash 是近似实现，不是独立 indirect painting。
- brush resource 预上传仍会同步等待，且缺少统一 residency 预算。
- backend 指针生命周期和线程访问需要收口。
- 固定 ring 满后直接丢 dab，无法形成可靠命令日志或设备失败恢复。
- render thread 在 swapchain frame 中逐 dab dispatch，笔迹计算被 acquire/present 节奏绑定。
- 重叠 dab 的 storage-image read-modify-write 缺少逐阶段可见性；直接补逐 dab barrier 又会结构性串行。

### 2.6 撤销与保存

- stroke-end 下载、`writeBytes()` 和 transaction commit 框架存在。
- transfer 与恢复绘制之间缺少完整跨队列依赖。
- 没有 undo/save/reopen 端到端测试。
- UMA 目标路径不应依赖 stroke-end 像素下载。

### 2.7 格式、LoD 与能力

- 多处固定 `VK_FORMAT_R8G8B8A8_UNORM`/`pixelSize=4`，raw projection bytes 被直接解释为 RGBA8。
- canvas 仅因选择 Vulkan 路径就报告 LoD 支持，没有 mip/page pyramid 能力证据。
- display/composite format 与 canonical paint format 没有显式 codec 边界。

### 2.8 Krita 既有存储未被吸收

- `KisTileDataStore` 已管理 tile data pool/swapper 和 memory stats；`KisSwappedDataStore` 已提供当前 swap 基础。
- `KisMementoManager` 已承载 COW/memento/oldData 语义。
- 当前 Vulkan TileManager/L3 没有把这些 identity 演进为同一 generation/lease 模型，反而形成第二套 residency 真相。

## 3. 需要保留的成果

- paintop/preset 接口适配思路。
- resolved dab 的字段设计和 CPU dynamics/compute brush 的模块边界；固定 ring 的容量与消费模型不保留。
- transfer/timeline 中可独立证明正确的算法、测试和 trace schema；当前单 command-buffer queue wrapper 不迁移。
- layer compositor shader 和 blend 共享表，作为后续正确实现输入。
- sync stroke 所暴露的 Krita transaction 业务需求；旧 stroke-end 下载实现不迁移。
- graphics/display/outline/decorations 的实验实现。

## 4. 需要重新定义的核心

### 4.1 从 TileManager 转向 Surface/Page 系统

当前 tile/cache/prefetch 以 sparse image 为中心。目标不是平行创建下列新 store，而是在 `kritaimage` 内把现有
tile/COW/swap 演进为唯一 PageStore，并让 Vulkan 只提供 replica：

```text
SurfaceRegistry
  -> Canonical PageStore (absorbs tiles3/COW/swap)
  -> PageStateMachine
  -> ResidencyController
       -> UMA backend
       -> dGPU backend
       -> Unified SSD provider in kritaimage
```

Sparse image、atlas、buffer 或 display image 都是 backend 选择或派生缓存。

### 4.2 从“活动层特殊路径”转向 ActiveTargetSet

每个 stroke epoch 明确可写目标集合。其余节点只读，并切成可缓存 segment：

```text
C0 -> T0 -> C1 -> ... -> Tn -> Cn
```

`C` 可以生成 checkpoint、overlay/operator 或 replay bundle。目标变化只重算必要依赖，而不是让所有非目标层保持 GPU-hot。

### 4.3 从 age 转向语义温度

Residency 评分必须包含目标角色、可见性、笔迹预测、dirty 成本、重建成本、依赖扇出和派生缓存覆盖度。
具体算法不是单分数：先做 safety eligibility，再做 semantic class，最后用 cost/CLOCK history 排序；见
[38_virtual_texture_residency_temperature.md](38_virtual_texture_residency_temperature.md)。

## 5. 正确的数据流

### UMA 绘画

```text
CPU input -> immutable StrokeJournal
PageWorkCompiler -> ordered PageJob
GPU StrokeCompute -> shared canonical target page
GPU incremental composite -> DisplaySurface
Presenter -> latest completed DisplaySurface -> swapchain
CPU consumer -> wait/invalidate -> mapped pointer
```

没有画布像素 upload/download，但存在显式 ticket、barrier 和 cache maintenance。stroke compute 不等待
swapchain。完整模型见 [10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md)。

### dGPU 绘画

```text
same logical generation
RAM replica <-> VRAM replica <-> unified SSD replica
GPU brush writes a leased VRAM generation
producer 完成并校验后才可切换 authority
dirty authority 在安全 handoff 前不可释放
```

### 图层合成

```text
LowerCheckpoint + WritableTarget + UpperCache/Replay -> DisplaySurface
```

## 6. 结论

归档原型不是“只差几个功能”的完成后端，而是曾具备多个实验部件、但核心数据模型、模块边界和线程所有权
均需校正的架构原型。当前树已经归档并删除该 runtime，下一步从 Krita tile/COW/undo/swap 出发建立唯一
PageStore，并按 41–44 完成 foundation 和算法提取；不得恢复 sparse-image-centric 对象图继续增加功能。

全局重建必须按 [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md) 的 BR0–BR6
执行。GPU stroke 的内部工作包才由 [21_implementation_and_baseline_cutover.md](21_implementation_and_baseline_cutover.md)
细化；两者不得倒置。
