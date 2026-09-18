# 可观测性、正确性测试与性能门禁

> 本文定义什么证据可以支持“正确、无阻塞、性能达标”的声明。不存在 GPU timestamp、sequence accounting
> 和压力/故障测试时，不允许用 CPU 录制时间或主观手感替代。
> 全局构建图、禁止 API、旧符号、唯一 SSD 和 capability 守卫以
> [30_p0_ci_architecture_guards.md](30_p0_ci_architecture_guards.md) 为准；本文不能用性能测试替代结构守卫。
> 虚拟纹理的 workload、成本模型、参数选择和 UMA/dGPU/SSD/温度专项门禁见
> [39_virtual_texture_performance_gates.md](39_virtual_texture_performance_gates.md)。

## 1. 验证顺序

固定顺序：

1. 协议与状态机正确；
2. 像素输出正确；
3. 同步与资源生命周期正确；
4. 迁移、取消和失败正确；
5. UI/host wait 审计；
6. 延迟与吞吐；
7. 功耗、内存带宽和长期稳定性。

任何性能结果都必须基于前四项通过的构建。缺少 barrier、丢 dab 或绕过回写得到的更高 FPS 无效。

## 2. Trace 数据模型

### 2.1 统一关联标识

每个事件尽可能携带：

```text
DocumentId
DocumentSessionId
EvaluationEpochId
StrokeId
BatchId
ChunkId
SequenceRange
OperationId
Ticket/Lane/TimelineValue
SurfaceId/PageId
Generation
ReplicaDomain
ThreadId
Timestamp
Result/Error
```

### 2.2 事件

```text
InputReceived
DabResolved
JournalAccepted/Sealed/Retired
BatchCompileBegin/End
LeaseRequested/Ready/Released
MigrationBegin/End
SubmissionQueued/Submitted/Signaled/Published
StrokePageWrite
CompositePageReady
DisplaySnapshotSelected
PresentSubmitted/Completed
SnapshotCreated
TransactionPublished
SavePageRead
BackpressureBegin/End
Failure/Recovery
```

trace 必须可在 release profiling build 以低开销 ring/stream 启用，并支持导出稳定格式。

## 3. 延迟定义

必须分别记录：

- input-to-resolved；
- resolved-to-accepted；
- accepted-to-compiled；
- residency wait；
- queue wait；
- GPU stroke duration；
- stroke-to-display-ready；
- display-ready-to-present-submit；
- input-to-visible；
- stroke-end-to-recoverable；
- transaction publication latency。

不能只报告平均值。至少报告 p50/p95/p99、最大值、样本数和分布；长笔迹、首笔、冷页、资源切换、
多层和内存压力分别统计。

## 4. GPU 时间

- StrokeCompute、Composite、DisplayGraphics 使用 GPU timestamp query。
- 记录 timestamp period、valid bits、queue/lane 和校准方法。
- CPU submit/record 时间单独记录，不能命名为 compute time。
- queue wait 可通过 submission/timeline correlation 推导，并与 kernel duration 分开。
- query pool slot 按 last-use ticket 回收，不因读 timestamp 阻塞热路径。

## 5. Command Accounting

每个 stroke 必须闭合：

```text
resolved count
accepted count
compiled logical dab count
PageJob reference count
executed/no-op/cancelled/failed count
last accepted sequence
last executed sequence per target/page
```

不变量：

- accepted 不会无终态消失；
- page duplication 只增加 ref count，不增加逻辑 dab count；
- ring/journal pressure 测试中 resolved-to-accepted 差异必须由明确 admission/backpressure/cancel 解释；
- transaction sequence range 与 End marker 前 accepted range 一致。

## 6. CPU Reference 与像素 Golden

### 6.1 Reference

- 消费同一 StrokeEpoch、ResolvedDab、PageJob 顺序。
- 明确浮点/rounding/color/blend 规范。
- 产生 page checksum 和完整图像。
- 无 GPU 环境可运行。

### 6.2 比较

- RGBA8 exact 或按明确 blend rounding 规范比较。
- 4/8/16 字节像素、浮点/高位深按每通道定义容差和统计，不使用肉眼相似。
- alpha、premultiplication、colorspace 分别检查。
- 输出差异附带 StrokeId、sequence、PageId、pixel coordinate 和前后值。

### 6.3 Golden 场景

- 单 dab、连续重叠 dab、低 opacity/flow；
- page/microtile 边界；
- 镜像、旋转、aspect、subpixel center；
- 超大 dab 和长 list；
- batch 任意切分；
- resource sampling；
- indirect/neighbor stage；
- undo/redo/replay。

## 7. Property/State-machine 测试

### 7.1 PageStateMachine

随机生成：

- CPU/GPU read/write lease；
- upload/download；
- SSD write/read；
- generation competition；
- cancel/timeout/failure；
- pin/evict；
- late completion。

检查：唯一 authority replica、最后安全副本、generation 单调、publish/cancel lease 终态、SSD checksum commit、
derived page 不接管 canonical authority、in-flight allocation 不复用。

### 7.2 Ticket DAG

- 随机 dependency graph；
- 环检测；
- queue/lane remapping；
- completion 重排；
- submit failure；
- device lost；
- deferred reclamation。

检查任何 consumer 不在 prerequisite publish 前运行。

### 7.3 Journal

- 随机 chunk 边界；
- 极小 budget；
- producer/compiler/executor 不同速度；
- end/cancel race；
- recovery/retirement。

检查 accepted sequence 全闭合。

## 8. Vulkan/Backend 验证

- validation layer 无同步、layout、descriptor、lifetime、sparse binding 错误。
- synchronization validation 必须开启的 CI/本地层级明确。
- shader 编译只是最低门槛，还需 offscreen execution/output test。
- command buffer reset、descriptor free、staging reuse 都有 in-flight 压力测试。
- queue family ownership 在 dedicated/shared queue 拓扑下分别测试。
- 同一/独立 family、独立 compute/transfer/present queue 拓扑分别测试；Presenter 不得直接调用 queue API。
- UMA coherent/non-coherent 和 dGPU/sparse/atlas 组合覆盖能力矩阵。

Validation layer 未报告不等于 shader read-modify-write 语义正确，因此 overlap golden test 仍是必需。

## 9. Host-wait 审计

### 9.1 静态检查

对交互模块扫描：

- `vkDeviceWaitIdle`；
- `vkQueueWaitIdle`；
- `vkWaitForFences`；
- blocking timeline wait；
- condition wait 包裹的 GPU completion；
- UI paint/resize 中 pixel download。

允许调用必须集中在明确 teardown/debug/background consumer 文件，并有注释/测试说明。

### 9.2 运行时检查

- 给 UI、input、stroke worker、presenter thread 注册 role。
- blocking GPU wait wrapper 在禁止 role 上断言/trace failure。
- 记录 wait ticket、时长、调用点。
- swapchain blocked test 验证 stroke sequence/generation 继续推进。

“零阻塞”只表示指定交互热路径无 host GPU wait，不表示系统没有依赖或 CPU consumer 永不等待数据。

## 10. 性能工作负载

### 10.1 Warm steady-state

- 单层 Auto Round；
- 小/中/大笔尖；
- 多种输入采样率和 spacing；
- working set 全驻留；
- 记录 input-to-visible 和 GPU duration。

### 10.2 Cold/resource

- 第一次选择 preset；
- predefined/texture/mask 冷资源；
- pipeline/resource prepare；
- 验证首个 dab 不 host wait，整笔 policy 可观察。

### 10.3 Residency pressure

- 极小 VRAM/RAM；
- 轨迹持续进入冷页；
- viewport pan 与绘画同时；
- SSD restore/writeback；
- non-target pages 和 derived cache 竞争。

### 10.4 Layer/composite

- lower checkpoint 命中/失效；
- upper overlay/operator/replay；
- 多目标；
- 大 viewport/高 DPI；
- decorations 开关。

### 10.5 Adversarial

- 500px+ 大 dab；
- 同一页数千重叠 dab；
- 超长笔迹；
- 快速 preset 切换；
- undo-before-complete；
- swapchain 阻塞/resize/minimize；
- device/transfer/SSD failure。

## 11. 性能指标

报告至少包括：

```text
input-to-visible p50/p95/p99/max
GPU stroke/composite/display duration
batch compile CPU time
queue/residency wait
PageJob/microtile/dab-ref count
bytes migrated among VRAM/RAM/SSD
journal/residency high-water marks
presented/stale/repeated frame count
backpressure duration
resolved dab loss（必须为 0）
CPU usage / memory bandwidth（可测设备）
power/thermal state（移动设备）
```

性能门槛按目标硬件 profile 定义，不写一个脱离设备的普遍 FPS。每个 profile 记录：CPU/GPU、内存架构、
驱动、屏幕刷新率、页面预算、文档、图层、笔刷和脚本版本。

## 12. 回归门禁

合入新基线前的硬门禁：

- `kritavulkanbackend` 不链接 `kritaui`，target graph 无环；
- queue submit/bind/present 只有 `SubmissionCoordinator` 一个源码/二进制 owner；
- global router、旧 stroke-end download、固定 fallback canvas 和第二套 Vulkan SSD store 不存在；
- resolved dab loss = 0；
- overlap/batch partition/page boundary golden 通过；
- 强制 VRAM/RAM/SSD 迁移 checksum 通过；
- UI/input/stroke-end/presenter 更新路径 host GPU wait = 0；
- swapchain blocked 时 stroke/transaction 推进；
- undo/save/cancel/device-loss 测试通过；
- 多文档、多 canvas、关闭其中一个 canvas 测试通过；
- 4/8/16 字节像素和不支持格式的前置 CPU 路由通过；
- EvalGraphIR 随机 DAG、Layer/Flow equivalent lowering 与 derived dependency generation 校验通过；
- validation/sync validation 通过；
- p95/p99 不超过目标 profile 已批准预算；
- 无未解释 latency spike 或 generation mismatch。

性能优化若破坏任一正确性门禁，不得以 feature flag 保留为可选路径。

## 13. CI 分层

### Tier 0：无 GPU

- dependency graph、public header、forbidden API/symbol 和唯一 SSD store 守卫；
- schema/journal/state-machine/property tests；
- PageWork compiler/reference；
- transaction/save generation tests；
- documentation/link checks。

### Tier 1：软件/基础 Vulkan

- shader compilation；
- offscreen Auto Round output；
- ticket/resource lifetime；
- validation layer。

### Tier 2：UMA

- shared canonical page；
- coherent/non-coherent cache；
- CPU pointer bypass；
- input-to-visible benchmark。

### Tier 3：dGPU

- transfer/sparse/atlas；
- dirty eviction；
- VRAM/RAM/SSD stress；
- queue topology。

### Tier 4：产品场景

- 完整 BR0–BR6 后的正常 Krita 入口；此前入口必须保持关闭；
- undo/save/reopen；
- 多文档/多 canvas/关闭、图层随机变化、viewport/decorations；
- color/display filter、SurfaceFormat 和 truthful LoD/capability；
- 长时间/功耗/热状态。

## 14. 实现路线

### OT0：事件与 trace schema

- 稳定 id/correlation。
- 低开销 recorder/exporter。
- current code facts 可先接入，但不得把旧指标当验收。

### OT1：Reference/golden harness

- CPU PageJob executor。
- offscreen Vulkan executor/readback。
- per-pixel/page diff。

### OT2：State/property/fault harness

- fake backend/ticket scheduler。
- completion reorder、failure、device-loss。

### OT3：GPU timing/latency

- query pool/timestamp。
- input-to-present correlation。
- p50/p95/p99 report。

### OT4：CI 与 profile gate

- UMA/dGPU device matrix。
- reproducible scripts/documents/presets。
- baseline storage 和 regression threshold。

## 15. 验收门槛

- 每个性能结论可追溯到构建、硬件、脚本和 trace。
- CPU recording 与 GPU execution 指标名称/数值分离。
- 每个 accepted sequence 有终态 accounting。
- 自动测试覆盖正确性、同步、迁移、transaction、present isolation 和故障。
- “零阻塞”由静态与运行时 wait audit 支持。
- 性能门禁在正确性全部通过后执行。
- 文档中的完成状态与 CI/运行证据一致。
