# Vulkan 笔刷重构施工方案

> 本文是能力层施工计划，不再沿用旧 S0–S7 的“部分完成”标签。笔刷 production 集成必须位于全局 BR5；
> BR0–BR4 完成前，只允许收紧能力声明和建设独立测试资产，不允许继续加固旧
> render-thread/backend-pointer 路径。统一状态与 MVP 边界见
> [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md)，全局顺序见
> [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md)，执行基线见
> [10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md)。
> GPU stroke 内部施工见 [21_implementation_and_baseline_cutover.md](21_implementation_and_baseline_cutover.md)；
> 能力门禁细节见 [19_brush_resources_and_capability_gate.md](19_brush_resources_and_capability_gate.md)。

## 1. 目标

让 Vulkan paintbrush 成为统一页面系统的消费者，并做到：

- GPU 放行能力与真实实现一致；
- brush resource 有统一缓存、预算和生命周期；
- UMA/dGPU 使用相同 page lease API；
- CPU/GPU 输出可自动对照；
- 撤销、保存和压力迁移保持一致。

## 2. 当前状态

| 区域 | 当前事实 | 状态 |
|---|---|---|
| PaintOp/Factory/Router | 代码存在 | 未运行验证 |
| Round backend | shader/dispatch 代码存在 | 未做输出对照 |
| Stamp backend | 资源上传/采样代码存在 | 未做 GPU 端到端验证 |
| Preset analyzer | 有门禁 | 放行范围过宽 |
| Shared blend | enum/C++/GLSL 已抽取 | 只验证枚举，不代表像素正确 |
| Resource loader/cache | CPU cache 测试存在 | GPU residency 未验证 |
| Preupload | 有队列 | 会同步等待，预算/取消不足 |
| Wash | 近似 max-alpha | 未完成 |
| Color/Lightness | 部分解析/计算 | 最终语义未闭环 |

## 3. 立即施工项：不依赖新页面系统

### R0：修正能力声明

- `KisVulkanPresetAnalyzer` 拒绝非 plain ColorSource。
- `LightnessStrength` 在实际应用前拒绝。
- Wash V1 近似路径不再标记为完整支持。
- 为每个 fallback reason 增加单元测试。

### R1：冻结新生命周期协议

- 定义 `PreparedBrushProgramId`、resource generation、Ready ticket 和 immutable handle。
- PaintOp 只持有 program handle，并通过 `KisPaintExecutionContext` 获取文档 session；新路径不访问 UI canvas，
  不跨线程共享 backend 裸指针。
- 定义 prepare 请求合并、取消、预算和延迟回收协议。
- 设备或 pipeline 未就绪时在 begin stroke 前整笔 fallback/reject，不得静默丢弃请求。
- 不给旧 backend 指针/预上传队列增加长期兼容 wrapper；实现落在新模块并由新 executor 消费。

### R2：补充测试基建

- 保留 preset 解析测试，但标记为 CPU resource test。
- 建立可离屏运行的 Vulkan device/shader test harness。
- 输出可保存为固定格式图像并与 reference 比较。

## 4. 页面系统完成后的施工项

### R3：Writable page lease

- `PageWorkCompiler` 根据一批有序 dab 的页面覆盖获取目标 surface write lease；新树中不存在全局 PaintRouter，
  任何 paintop/router facade 都不能管理物理页。
- brush halo 进入预热与 pin。
- page-batched dispatch 完成后按 ticket 发布 page generation/dirty owner。
- 不允许 PaintOp 直接感知 sparse bind 或 staging buffer。

### R4：Brush resource surface

- tip、texture、mask 注册为 immutable resource surface。
- 资源 cache key 包含内容 generation、尺寸和采样语义。
- PageStore/ResidencyController 统一决定 UMA 共享页、dGPU VRAM cache 或 SSD/RAM replica；SSD 必须使用由
  Krita 现有 swap 演进出的唯一 unified store。

### R5：Auto Round

- Normal blend golden image。
- size/opacity/flow/spacing/rotation/mirror。
- tile 边界、超大 dab、快速轨迹和小预算迁移。

### R6：Predefined/Texture/Masking

- 验证真实 shader 采样和输出。
- 验证资源更新、失效、预热和回收。
- 禁止以“QImage 非空”作为端到端完成标准。

### R7：Airbrush/Wash/颜色

- Airbrush 时间模型与 CPU reference 对齐。
- Wash 使用独立 indirect surface 和由 commit ticket 串联的 stroke final composite stage，不在 host stroke end 中同步合成。
- ColorSource/Lightness 等逐项实现并解除门禁。

## 5. 提交边界

建议每次提交只覆盖一个可验证性质：

1. 门禁修正与测试；
2. PreparedBrushProgram/resource generation 生命周期；
3. Vulkan offscreen harness；
4. writable page lease；
5. round golden image；
6. resource surface/cache；
7. predefined golden image；
8. texture/masking；
9. airbrush；
10. wash indirect surface。

## 6. 禁止事项

- 不新增独立于统一 ResidencyController 的 brush GPU cache。
- 不把旧 backend pointer/preupload path 的局部修补作为新基线组成。
- 不以同步 `vkQueueWaitIdle` 作为生产热路径。
- 不因为 shader 有某字段就宣称功能已支持。
- 不把近似结果写成 CPU parity。
- 不在没有运行证据时写性能数字或“零阻塞”。
