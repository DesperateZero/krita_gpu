# 第一个 MVP 大纲

> 本文已按当前架构决策重写。旧版“单图层 sparse image 能画即可算 MVP”的定义已废止。权威口径见
> [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md)，全局 P0 总纲和唯一执行顺序见
> [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md) 与
> [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md)。笔迹执行见
> [10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md)。

## 目标

验证一个面向真实绘画的统一页面系统，而不是只验证 Vulkan API 能否显示和 dispatch。

## 必须包含

1. 受控重置、旧 runtime 删除和下游 UI adapter 组装的单向 target 图；backend 只依赖 `kritaimage`，paintop
   只依赖 backend-neutral session。
2. Krita 现有 tile/COW/undo/swap 演进出的唯一 canonical PageStore。
3. 逻辑 tile 与设备物理页正确解耦；fixed-slot slab 与 direct/operation-scoped binding 为基线，sparse 仅为可选 provider。
4. UMA 共享 mapped page 与 CPU/GPU 所有权切换。
5. dGPU VRAM cache 与 RAM backing 自动转录。
6. 唯一 unified SSD store 的写出、恢复、校验和空间回收。
7. generation、lease、authority、pin、in-flight 和失败状态机。
8. `SubmissionCoordinator` 的 queue 独占、timeline DAG、command arena 和零阻塞线程边界。
9. 基于 `GraphEpoch`/`ActiveTargetSet` 的 lower/target/upper 图层剪枝。
10. 绘画感知温度、预算和迟滞。
11. 独立于 swapchain 的 page-batched GPU stroke lane。
12. generation COW undo、immutable save epoch 和 cancel/recovery。
13. `SurfaceFormat`、codec、4/8/16 字节格式与 truthful capability/LoD。
14. 文档级 session、多 canvas 隔离和只消费 DisplaySurface 的 UI adapter。
15. BackendReadyToken、设备能力探测和完整验收后的产品入口。

## 可以限制但不能绕开

- 可以先以单目标图层和 Auto Round Brush 建立第一条 stroke golden path，但 PageStore/codec 和 capability
  必须从第一天支持完整 `SurfaceFormat` 身份，并覆盖 4/8/16 字节像素及不支持格式的前置 CPU 路由。
- 可以让 CPU reference backend 立即完成 ticket，但消费者从第一天就只能使用异步 ticket API；不得先暴露同步 transfer/wait 接口再改造。
- 可以先只对安全 blend 生成 upper overlay，其余走 replay。
- 不可以用固定大图、手工 bind/upload、只有 VRAM/RAM、逐 dab dispatch、stroke-end 整图回读或仅 CPU 测试替代目标架构。

## 当前状态

仓库中已有 device/swapchain、sparse image、staging、transfer、brush compute、render thread 和同步框架，但三层自动转录、UMA 权威共享页、温度策略、图层剪枝和端到端验证尚未实现。因此本 MVP 未完成。

## 成功标准

- 小预算压力测试覆盖 VRAM↔RAM↔SSD 并保持 checksum 一致。
- UMA 路径没有画布像素复制，只有显式同步和 cache maintenance。
- 当前目标页在快速绘画中保持 pinned/hot；有效 checkpoint 覆盖的非目标源页可下沉。
- 只有 BR0–BR6 和 Tier 0–4 全通过后，Krita 正常入口才开放 Vulkan；启用后可画、可撤销、可保存并重开一致。
- validation layer 无相关错误，所有性能数字都有测试环境和可复现脚本。
