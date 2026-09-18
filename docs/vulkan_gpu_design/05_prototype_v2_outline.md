# 第二阶段能力扩展：在 P0 MVP 基线上扩大多层与笔刷覆盖

> 前置条件是 [04_prototype_v1_outline.md](04_prototype_v1_outline.md) 的完整 P0 MVP 已验收。typed EvalGraphIR、
> EvaluationEpoch、MutationRootSet、Layer lower/upper 优化、derived DisplaySurface 和基本多层正确性已经属于第一个 MVP；本文不能
> 被用来把这些高代价基础推迟到后续。当前尚未进入本阶段。
> 多层增量合成服从 [16_incremental_composite_and_presenter.md](16_incremental_composite_and_presenter.md)，笔刷能力解除门禁服从 [19_brush_resources_and_capability_gate.md](19_brush_resources_and_capability_gate.md)。

## 目标

在不增加第二套存储模型、不修改冻结的 page/generation/lease/ticket 边界前提下，扩大复杂图层语义、笔刷
能力和色彩功能覆盖。

## 范围

### 多层合成

- 在 MVP 已有通用 EvalGraphIR、`MutationRootSet`、Layer LowerCheckpoint、UpperOperator/Replay 和 generation invalidation 上扩展更多
  blend、group、mask、filter 与 animation 组合。
- 增加复杂多 target 操作和更广的 dependency graph 优化，但不改变 EvaluationEpoch 语义。

### 笔刷能力

- predefined tip、texture、masking 和 airbrush。
- 每项能力有 CPU/GPU golden image。
- Wash、ColorSource、LightnessStrength 等未闭环语义继续回退。

### 交互与显示

- pan/zoom/rotation。
- brush outline 和 decorations。
- wrap-around、channel selection。
- swapchain/display pipeline 的稳定性。

### 正确性

- 常用 blend/group/mask。
- undo/redo/save/reopen。
- 多 target 操作。
- 内存压力下 derived cache 丢弃和恢复。

## 不在本阶段默认完成

- 完整 OCIO/HDR/所有位深；
- 所有 Krita paintop；
- 全部滤镜与非破坏节点；
- 通用节点图编辑器。

这些能力属于后续扩展，但必须复用同一页面、依赖和缓存框架。

## 成功标准

- 多层文档在目标页持续写入时只局部重算必要 segment。
- 被有效 checkpoint/cache 覆盖的非目标源页能够自动下沉。
- compositor 输出、显示结果和 CPU reference 在定义容差内一致。
- 不因增加图层功能重新引入整层常驻 VkImage 或独立预算体系。
