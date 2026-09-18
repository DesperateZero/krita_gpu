# 难点与关键约束

> 本文描述必须解决的问题。当前完成状态见 [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md)，
> 全局 P0 永久方案见 [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)，虚拟纹理
> 算法决策见 [32_virtual_texture_architecture_decisions.md](32_virtual_texture_architecture_decisions.md)。

## 0. 先解决 canonical 身份与模块咬合

最大的风险不是某个 shader 缺功能，而是当前 Vulkan runtime 同时拥有第二套 tile/residency 真相，并通过
`kritaimagevulkan <-> kritaui` 构建环、global PaintRouter 和 canvas/backend 裸指针侵入 Krita。

永久边界是：Krita 现有 tile/COW/undo/swap 演进为唯一 canonical PageStore；Vulkan 只提供 replica 和
consumer；构建依赖通过下游 `kritavulkanuiadapter -> {kritaui, kritavulkanbackend}` 组装，backend 只向下依赖
`kritaimage`，paintop 只消费 backend-neutral session。具体见
[23_p0_module_boundaries_and_build_graph.md](23_p0_module_boundaries_and_build_graph.md)、
[24_p0_backend_lifecycle_and_document_sessions.md](24_p0_backend_lifecycle_and_document_sessions.md) 与
[25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md)。

## 1. 页面几何不等价

Krita 逻辑 tile、Vulkan sparse block、RAM page 和 SSD record 不是天然一一对应。设备报告的 sparse granularity 必须参与映射，不能把固定 64×64 逻辑 tile 直接当作物理 sparse page。

## 2. UMA 共享内存不等于可直接映射 image texel

`HOST_VISIBLE | DEVICE_LOCAL` 只说明内存可被双方访问，不保证 optimal/sparse image 的 texel 具有 CPU 可解释的线性布局。UMA 指针旁路必须建立在共享 buffer page 或其他明确的线性权威表示上。

## 3. 三层转录必须保证唯一权威副本

每个页面都要明确：

- 哪一份数据是 authoritative；
- 哪些副本是派生或过期副本；
- dirty 数据何时可以转录或淘汰；
- CPU/GPU/SSD 操作的 generation 和完成时间线；
- 失败、取消和设备丢失时如何恢复。

SSD 不能由 Vulkan 另建。现有 `KisTileDataStore`/`KisSwappedDataStore` 必须升级为唯一 unified store，
否则 CPU undo/save 与 GPU residency 会长期拥有两套 page identity。

## 4. 温度是绘画语义问题

普通 LRU 无法表达：

- 当前目标页必须保持可写；
- 笔迹预测区域需要提前 pin；
- 有效 lower checkpoint 覆盖的下层源页可以快速降温；
- backdrop-dependent upper node 仍可能需要局部重放；
- derived cache 可丢弃，而 canonical dirty page 不可丢弃。

最终不是给 LRU 继续加权，而是先执行安全资格，再按绘画语义类和 cost/CLOCK history 选择 replica；详见
[38_virtual_texture_residency_temperature.md](38_virtual_texture_residency_temperature.md)。

## 5. 图层合成具有背景依赖

目标层以下通常可以形成精确 checkpoint；目标层以上只有一部分 blend/group 语义可以预合成为独立 overlay。其余必须保存 operator 或 replay bundle。错误地把所有上层都拍平成透明 RGBA 会改变结果。

## 6. 多队列同步与布局状态

Transfer、compute、graphics 和 sparse bind 之间必须有显式依赖。仅在 CPU 侧等待 timeline，或每次假定 image 从 `UNDEFINED` 开始，都不足以保证正确性。

笔刷还存在同页重叠写的顺序约束：同一 submission 中连续 `vkCmdDispatch` 不自动建立 shader
read-modify-write 的内存依赖。逐 dab 加 barrier 会把当前模型串行化，因此目标必须是稳定页面分桶和
page-batched kernel；同页 invocation 按 sequence 混合，不同页并行。

详细设计见 [13_page_work_compiler_and_gpu_kernel.md](13_page_work_compiler_and_gpu_kernel.md) 与
[14_submission_tickets_and_queue_topology.md](14_submission_tickets_and_queue_topology.md)。

## 7. 撤销、保存与 CPU 操作

UMA 应允许 CPU 在等待 GPU 完成后直接读取共享页；独显需要页级异步回传。两者都不能依赖 stroke-end 整图下载。撤销应以目标页的 copy-on-write/snapshot 为基础。

Krita 存储接入和 transaction 时序分别见
[17_krita_pagestore_integration.md](17_krita_pagestore_integration.md) 与
[18_undo_save_cancel_and_recovery.md](18_undo_save_cancel_and_recovery.md)。

## 8. 设备能力差异

需要能力矩阵，而不是单一 fallback 大图：

- UMA shared-buffer backend；
- dGPU VRAM-cache backend；
- sparse image 或 atlas/display cache；
- coherent 与 non-coherent 映射；
- 不同 queue-family、格式、位深和 sparse granularity。

能力声明必须绑定完整 `SurfaceFormat`、codec 和 GPU golden；没有 mip/page pyramid 时不得报告 LoD 支持，
display RGBA8 也不能倒推出 canonical paint format 支持。见
[29_p0_surface_format_lod_capabilities.md](29_p0_surface_format_lod_capabilities.md)。

## 9. 可验证性

首要测试不是帧率，而是强制小预算下随机迁移和 checksum：dirty eviction、VRAM↔RAM↔SSD、CPU↔GPU ownership、多 surface 竞争、取消与错误恢复。正确性通过后，才讨论延迟和吞吐。

GPU stroke 还必须验证 batch partition invariance、重叠 dab 顺序、零 resolved-dab 丢失、swapchain
隔离、undo-before-complete 和真实 GPU timestamp。具体门槛见
[10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md)。
测试和性能证据格式见 [20_observability_testing_and_performance.md](20_observability_testing_and_performance.md)。

## 10. 生命周期和产品入口

构造对象或检测到 Vulkan loader 不代表后端可用。必须由完整初始化产生不可伪造的 `BackendReadyToken`，
canvas 还需同时获得 swapchain 和文档 session。多个 canvas 共享文档 session，不得用“当前活动 canvas”决定
PaintOp 目标。Vulkan 用户入口在 BR0–BR6 全部验收前保持关闭。
