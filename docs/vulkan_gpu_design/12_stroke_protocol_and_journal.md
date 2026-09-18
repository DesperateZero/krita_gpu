# Stroke 协议、命令日志与无丢失接入

> 本文细化 `StrokeEpoch`、`ResolvedDab`、`StrokeJournal`、容量控制和 begin/end/cancel 协议。
> 跨专题硬边界见 [10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md)。
> 本协议不能定义第二套 tile/session 真相：document target/session 来自 `KisPaintExecutionContext`，页面写入
> 只通过 canonical PageStore lease。全局边界见
> [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)。

## 1. 目标

输入侧必须在不等待 GPU 的前提下，把 Krita 笔刷语义转换为可排序、可批处理、可恢复的命令流。
协议需要同时满足：

- 已解析命令不丢失；
- 同一输入在相同资源 generation 下可确定性重放；
- backend、目标集合和图层图在一次 epoch 内冻结；
- journal 有界且不会通过覆盖旧数据控制容量；
- end/cancel 是显式记录，不依赖对象析构时猜测 GPU 状态；
- GPU、CPU fallback、undo 和设备恢复消费同一逻辑命令格式。

## 2. 数据层次

### 2.1 `InputSample`

来自 Krita 输入系统的原始或规范化样本，可包含：

```text
position
pressure
tilt / rotation
timestamp
speed / distance context
button/modifier state
```

`InputSample` 不是持久 GPU 协议。Krita 可以在进入 paintop 语义前按自己的规则合并设备事件；一旦样本被
解析成 `ResolvedDab`，后续系统不得再为性能原因丢弃或改变它。

### 2.2 `StrokeEpochDesc`

```text
StrokeId
GraphEpoch
ActiveTargetSet
TargetSurfaceId[]
TargetBaseGeneration[]
PreparedBrushProgramId
BrushSemanticVersion
ResourceGenerationSet
PixelFormat / ColorSpace
CanvasTransformSnapshot
CompositePolicy
UndoPolicy
ExecutionBackend
```

规则：

- `StrokeId` 全进程单调唯一，不能复用。
- `GraphEpoch` 标识图层图、mask、group、blend 属性的稳定视图。
- `ActiveTargetSet` 显式列出可写 surface；未列入的节点在该 epoch 内只读。
- `ExecutionBackend` 在 begin 时选择，不能在 epoch 中从 GPU 切到 CPU 或反向切换。
- brush/resource generation 必须在 journal 退休前保持可访问或可恢复。

### 2.3 `ResolvedDab`

建议协议字段：

```text
StrokeId
sequence
subSequence
targetIndex
timestamp / duration
center
conservativeBounds
radius / aspect / rotation
opacity / flow
color / blend mode
shape flags
resource slot references
algorithm-specific payload offset
```

约束：

- `(sequence, subSequence)` 在一个 epoch 内严格递增。
- 主 dab、水平/垂直镜像等共享 source sequence，但用固定规则分配 subSequence。
- bounds 必须保守包含 shader 可能读写的全部像素，包括 filter halo、texture footprint 和 anti-alias fringe。
- payload 只引用 `PreparedBrushProgram` 中的稳定 slot，不保存裸 C++/Vulkan 指针。
- 浮点规范、随机种子、颜色转换版本和曲线版本必须属于可重放语义。

### 2.4 控制记录

journal 不只存 dab，还需要：

- `BeginEpoch`；
- `DabChunk`；
- `TimeAdvance`，用于 airbrush/restamp 等时间语义；
- `BarrierMarker`，只用于算法 stage，不对应 host wait；
- `EndEpoch`；
- `CancelEpoch`；
- `ResourceFailure`/`ExecutionFailure` 终态记录。

控制记录也有 sequence，不能依赖析构顺序或跨线程 flag 猜测。

## 3. `StrokeJournal` 存储模型

### 3.1 Chunk

journal 由固定上限但可动态增加数量的 chunk 组成。每个 chunk 包含：

```text
ChunkId
StrokeId
firstSequence / lastSequence
recordCount
byteSize
checksum
state
referenceCount
records[]
```

chunk 大小是 allocator 策略，不是协议容量。禁止出现“全系统只能容纳 N 个 dab”的固定覆盖窗口。

### 3.2 状态机

```text
Open
  -> Sealed
  -> Compiled
  -> Submitted
  -> Executed
  -> Recoverable
  -> Retired
```

错误分支：

```text
Open/Sealed/Compiled -> Cancelled
Submitted/Executed   -> RestoreRequired -> Recoverable/Failed
Any                  -> Failed
```

状态含义：

- `Open`：唯一 producer 可追加。
- `Sealed`：内容、sequence range 和 checksum 不再改变。
- `Compiled`：所有记录已经映射到 PageJob，但仍保留原命令。
- `Submitted`：存在执行 ticket，物理 command buffer 可能尚未运行。
- `Executed`：GPU/CPU executor 完成新 generation，但不一定有安全恢复来源。
- `Recoverable`：新数据有安全 backing，或 before-image + journal 足以重放。
- `Retired`：undo、恢复和所有 consumer 都不再需要，内存可回收。

只有 owning coordinator 能推进状态，迟到 completion 必须验证 ChunkId、StrokeId 和 generation。

### 3.3 内存位置

- CPU 端 chunk 使用普通 RAM/slab pool，保证快速 append 和设备失败后可用。
- GPU 消费的打包数据使用独立 command upload arena；UMA 可映射，dGPU 可通过 transfer ticket 上传。
- GPU command arena 不是 journal 的唯一副本。
- chunk 与 GPU upload slice 分离回收，二者分别等待 journal retention 和 GPU completion。

## 4. Producer 与并发

每个 stroke epoch 只有一个逻辑 producer。若 Krita 可能从多个 worker 产生目标命令，必须在进入 journal 前按
Krita stroke job 顺序归并，不能依赖多个线程竞争 atomic sequence。

建议接口：

```text
StrokeHandle beginStroke(StrokeEpochDesc)
AppendResult appendDabs(StrokeHandle, Span<ResolvedDab>)
AppendResult appendTimeAdvance(StrokeHandle, TimeRecord)
StrokeCommitHandle endStroke(StrokeHandle)
CancelHandle cancelStroke(StrokeHandle, Reason)
```

`appendDabs()`：

- 不调用 Vulkan；
- 不查询 swapchain；
- 不等待 fence/timeline/SSD；
- 只分配或追加 CPU chunk，并唤醒 compiler；
- 返回 accepted sequence range 和 journal pressure，而不是“GPU 已画完”。

## 5. Sequence 与确定性

### 5.1 Sequence 分配

- `sequence` 在 dynamics 完成后、journal append 前分配。
- 一个 source sample 产生多个 dab 时，按语义固定顺序生成 subSequence。
- 不能在 page binning 后重新编号。
- compiler 可以把一个 sequence 引用到多个页面，但不能复制成新的逻辑 dab。

### 5.2 随机与时间

- scatter、texture randomization 等使用 `(StrokeId, sequence, semanticSeed)` 派生随机数。
- 不能读取执行线程当前时间、全局 RNG 或 GPU 调度顺序作为像素语义。
- airbrush 使用显式 `TimeAdvance` 或已解析 restamp dab；设备重放时结果不依赖真实等待时间。

### 5.3 协议版本

`BrushSemanticVersion` 和 command schema version 必须进入 journal/replay metadata。shader 或 CPU dynamics 语义变化后，
旧 journal 只能由匹配版本执行；不能用新 shader 静默重放旧命令。

## 6. Backend 选择

begin stroke 前检查：

- capability manifest 是否覆盖 preset；
- `PreparedBrushProgram` 是否 ready 或有可等待的 resource ticket；
- target format/color space 是否支持；
- canonical PageStore 与目标 replica/execution capability 是否可用；
- queue isolation 和必要 shader feature 是否满足；
- recovery policy 是否可满足。

结果只能是：

1. `GPU`：整笔 journal 交给 GPU executor。
2. `CPU_EXECUTION`：整笔 journal 或原 CPU paintop 写同一 canonical PageStore surface。
3. `REJECTED`：无法保证语义时不开始该 backend，并由上层选择成熟路径。

禁止：GPU 画到一半因资源 miss 切换 CPU，或 CPU 画到一半把剩余 dab 接到 GPU。跨 backend 切换必须关闭
旧 epoch，并以已完成 canonical generation 作为新 epoch 基准。

## 7. 容量、Backpressure 与零丢失

### 7.1 水位

journal 至少公开：

```text
softByteLimit
hardByteLimit
openBytes
sealedBytes
submittedBytes
oldestOutstandingSequence
compilerLag
executorLag
```

- 低于 soft limit：正常分块。
- 超过 soft limit：提高 compiler 调度优先级、缩短 batch deadline、减少非必要预测工作。
- 接近 hard limit：在 Krita stroke worker 的 admission 点施加 backpressure。
- UI/input event loop 不等待；上游仍能收集设备状态，但不得谎报 dab 已 accepted。

### 7.2 Hard limit 行为

hard limit 不能通过以下方式解决：

- 覆盖最旧 chunk；
- 丢弃中间 dab；
- 自动降低 opacity/spacing 改变语义；
- 提前把 transaction 标记完成；
- 在 UI 线程等待 GPU。

如果持续过载，允许：

- stroke worker admission 暂停，形成可测量绘制延迟；
- 在尚未开始的下一笔选择 CPU backend；
- 向性能/UI诊断报告 overload；
- 由用户显式取消当前笔迹，再按取消协议恢复。

### 7.3 防止内存失控

- chunk pool 有预算，不能无限 heap grow。
- journal 只有在 Recoverable 且 undo/recovery 不再引用后退休。
- 长笔迹可以分段形成 recovery checkpoint，但不能改变一个 epoch 内的逻辑顺序。
- recovery checkpoint 必须先确保所有相关页面有安全 generation，再释放更早 journal。

## 8. Begin、End 与 Cancel

### 8.1 Begin

`beginStroke()` 原子捕获 epoch desc，并完成：

- target set 和 graph epoch 校验；
- backend 选择；
- brush program/resource generation pin；
- undo transaction/snapshot policy 初始化；
- journal first chunk 分配；
- trajectory predictor 和 residency hint 初始化。

它不等待所有目标页驻留。页恢复由后续 batch ticket 表达。

### 8.2 End

`endStroke()`：

1. append `EndEpoch`；
2. seal open chunk；
3. 禁止新 append；
4. 请求 compiler 处理尾 batch；
5. 返回包含 accepted、execution、visible、recoverable 状态的 commit handle。

它不调用 pause、fence wait、device idle 或像素下载。

### 8.3 Cancel

- 尚未提交的 chunk 可以标记 Cancelled 并释放资源。
- 已提交但 GPU 尚未开始的工作可在调度允许时跳过；不能假设一定可撤回 queue submission。
- 已经或可能写入页面的工作必须等待/依赖 writer ticket 后从 before-image 恢复。
- cancel 完成也返回 ticket，只有恢复 generation 发布后才对上层完成。

## 9. Journal 与恢复

设备失败或 dGPU 未回写时，需要：

- stroke epoch desc；
- 完整未退休 command chunk；
- matching brush semantic/resource generation；
- 每页 before-image 或安全 base generation；
- 已知最后成功执行 sequence/page generation。

恢复可以选择 CPU reference executor 或重建 GPU executor。不能从“最后提交的 command buffer”推断完成范围；
必须使用 page generation 和 completion ledger。

## 10. 实现路线

### SJ0：协议冻结

- 定义 POD/serializable schema，不含 Vulkan handle。
- 明确浮点、颜色、随机和时间语义。
- 建立 schema version 和 round-trip serialization test。

### SJ1：CPU journal

- chunk allocator、状态机、checksum 和引用计数。
- 单 producer append、seal、retire。
- 强制小预算与并发状态测试。

### SJ2：Admission 与 backpressure

- soft/hard 水位和统计。
- 与 Krita stroke worker 集成，证明 UI 线程不等待。
- 移除 ring-full drop 行为。

### SJ3：Compiler handoff

- sealed chunk 只读视图。
- sequence range 到 PageJob 的 accounting。
- 每个 accepted dab 必须能追踪到 executed/cancelled 终态。

### SJ4：恢复与 retirement

- journal 与 before-image/recoverable generation 联动。
- device-loss replay 测试。
- transaction/undo 释放后正确退休。

## 11. 验收门槛

- 100% accepted `ResolvedDab` 最终进入 Executed 或显式 Cancelled/Failed，不能失踪。
- 任意 chunk 边界和 batch 边界不改变输出。
- ring/queue 极小预算压力下不丢命令、不冻结 UI。
- begin 后 backend、target set、resource generation 不发生隐式切换。
- End marker 前的所有 sequence 都包含在 commit handle 中。
- cancel 对已写页执行可证明恢复。
- journal 在 recoverability 前不会退休。
- 设备失败后能从 base generation + journal 恢复受支持笔刷结果。
