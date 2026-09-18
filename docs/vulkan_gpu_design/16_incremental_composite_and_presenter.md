# 增量合成、DisplaySurface 与 Presenter 隔离

> 本文定义 stroke 输出如何形成可显示结果，以及 WSI/swapchain 为什么不能成为笔迹执行的前置依赖。
> 全局 GraphEpoch/projection/display 权威设计见
> [28_p0_graph_epoch_projection_display.md](28_p0_graph_epoch_projection_display.md)，queue API 所有权见
> [27_p0_submission_threading_zero_blocking.md](27_p0_submission_threading_zero_blocking.md)。

## 1. 目标

- StrokeCompute 只写 canonical target/indirect surface，不直接写 swapchain。
- 图层合成只重算受 page generation 变化影响的区域。
- Presenter 只读取已经完成的 DisplaySurface generation。
- acquire、present、resize、遮挡、最小化和 surface lost 不阻塞 stroke。
- 非目标图层利用 ActiveTargetSet 形成 lower/upper 派生缓存，不保持全栈 GPU-hot。
- decorations/outline 不通过每帧全窗口 CPU bitmap upload 污染 stroke/display 时序。

## 2. Surface 分工

```text
CanonicalLayerSurface     文档权威图层像素
LowerCheckpointSurface   目标以下只读 segment 的派生结果
UpperOverlaySurface      与 backdrop 无关的上层覆盖
UpperOperatorSurface     可作用于 backdrop 的缓存算子
UpperReplayBundle        背景依赖节点的准备数据/重放描述
StrokeIndirectSurface    wash 等笔刷的 stroke-local 内容
DisplaySurface           可直接被 presenter 采样的派生页面
UiOverlaySurface         grid/guide/selection 等非文档内容
```

只有 CanonicalLayerSurface 进入文档保存权威数据。其他 surface 记录 dependency generation，可丢弃重建。

## 3. Stroke epoch 图层切分

### 3.1 单目标

```text
ReadOnlyLowerSegment -> LowerCheckpoint
WritableTarget       -> changed target pages
ReadOnlyUpperSegment -> Overlay / Operator / Replay
```

epoch begin 冻结：

- GraphEpoch；
- ActiveTargetSet；
- segment 边界；
- node/blend/mask revision；
- lower/upper dependency set。

目标页写入不会使 lower checkpoint 失效。upper 只对相交下游 DisplaySurface page 失效。

### 3.2 多目标

```text
C0 -> T0 -> C1 -> T1 -> ... -> Tn -> Cn
```

- `T` 是 writable target。
- `C` 在 epoch 内只读。
- 每个 target generation 变化只传播到依赖它的后续 segment。
- target 之间有算法依赖时使用 stage ticket；否则可并行。

## 4. Upper 分类

### 4.1 BackdropIndependentOverlay

在透明或独立语义下预合成，之后可覆盖任意下方结果。只有数学上与 backdrop 无关的 blend/node 才允许。

### 4.2 BackdropOperator

缓存对 backdrop 的参数化作用，而不是拍平后的 RGBA。执行时将 operator 应用于新 target/lower 结果。

### 4.3 BackdropDependentReplay

保存 source page、mask、filter 输入和 node parameters。target 变化后对脏区重放。

任何未分类语义默认进入 replay，不能为了性能假设 overlay 安全。

## 5. Dirty propagation

### 5.1 事件

PageStateMachine 在 target generation 发布后发出：

```text
SurfaceId
PageId / Region
OldGeneration
NewGeneration
WriterTicket
GraphEpoch
```

### 5.2 传播

`IncrementalCompositeScheduler`：

1. 校验 GraphEpoch 和 dependency revision。
2. 找到相交 lower/target/upper/display pages。
3. 保留仍有效 lower checkpoint。
4. 选择 overlay/operator/replay stage。
5. 获取 source read lease 和 derived write lease。
6. 提交等待 writer ticket 的 composite batch。
7. 发布新的 DisplaySurface generation 和 `DisplayReadyTicket`。

失效传播以 page/region 为单位。全画布 invalidate 必须有明确原因，例如无法界定范围的 graph mutation，不能作为
普通 dab 更新默认路径。

## 6. DisplaySurface

### 6.1 内容

DisplaySurface 是指定 display transform 前或后的派生页面集合，必须明确：

- source graph epoch；
- target/lower/upper dependency generations；
- color/display transform version；
- viewport/LOD；
- completion ticket；
- valid region。

### 6.2 版本

- 正在构建的 generation 与 presenter 正在读取的 generation 分离。
- 一个 DisplaySurface page 只有在完整 composite stage 完成后发布。
- Presenter 可以混合读取不同 page 的最新完整 generation，但每页不能读取半完成写入。
- graph epoch 变化时旧 display page 可以继续显示到新页完成，不能误标为新 epoch。

### 6.3 存储

- UMA canonical target 仍是 buffer page；DisplaySurface 可以是 sampled atlas/image 派生缓存。
- dGPU DisplaySurface 由 ResidencyController 管理，可丢弃重建。
- 不允许把 swapchain image 作为 DisplaySurface canonical backing。

## 7. Presenter

### 7.1 职责

Presenter 只负责：

- 非阻塞/有界 acquire swapchain image；
- 选择最新已经完成的 DisplaySurface generation；
- 记录 canvas transform/display pass/overlay；
- 构造 immutable graphics/present request 交给 `SubmissionCoordinator`；
- 处理 present result 和 WSI resource lifetime。

Presenter 不持有 `VkQueue`，也不直接调用 `vkQueueSubmit` 或 `vkQueuePresentKHR`。只有
`SubmissionCoordinator` 执行所有 queue API。

它不负责：

- 消费 stroke journal；
- 触发 target page bind/upload；
- 等待未完成 stroke/composite；
- 提交 undo/save；
- 暂停 StrokeCompute。

### 7.2 帧选择

每次机会：

1. poll 已完成 DisplayReady tickets；
2. 捕获可用的 DisplaySnapshot；
3. acquire 成功则提交 `PresentRequest`；
4. acquire not-ready/timeout 则跳过；
5. 没有新 DisplaySnapshot 时重复显示上一版本。

不能为了“显示最新一笔”在 presenter host 线程等待 compute timeline。

### 7.3 Queue 隔离

- Present 与 StrokeCompute 使用不同 `VkQueue` 或后端等价独立 command queue。
- 可位于同一 queue family，避免不必要 ownership transfer。
- 如果硬件底层仍竞争执行单元，性能测试记录 queue contention；逻辑依赖仍不能把 present 放到 stroke 前面。

## 8. Swapchain 生命周期

### 8.1 Resize/out-of-date

- 标记 Presenter surface epoch 失效。
- 停止新 WSI submission，不停止 StrokeCoordinator。
- 等待/回收旧 swapchain 自己的 last-use ticket，不 `vkDeviceWaitIdle()`。
- 建立新 swapchain/Presenter epoch。
- 重新显示最新有效 DisplaySurface。

### 8.2 Minimize/occlusion

- Presenter 可以完全停止 acquire/present。
- StrokeCompute、PageStore、undo/save 继续工作。
- DisplaySurface 预算可根据不可见状态降温，但 canonical target generation 不受影响。

### 8.3 Surface lost/device lost

- surface lost 只重建 WSI；
- device lost 进入全 GPU backend 恢复，见
  [18_undo_save_cancel_and_recovery.md](18_undo_save_cancel_and_recovery.md)；
- 二者不能混为“调用 device wait idle 后重来”。

## 9. Canvas transform 与 LOD

- pan/zoom/rotation 是 Presenter/DisplaySurface sampling 状态，不修改 canonical target coordinates。
- 高缩放或远距离视图可以选择 derived LOD page，但写入仍发生在 canonical page。
- 没有实现并通过测试的 mip/page pyramid 时，capability 必须返回不支持 LoD，不能由 canvas 类型推断。
- transform version 变化只使相关 DisplaySurface 派生状态失效，不使 layer page generation 变化。
- viewport 变化向 ResidencyController 提交 visible/anticipated page hint。

## 10. Decorations 与 Outline

### 10.1 Brush outline

- 使用小型动态 vertex/parameter buffer 或直接 graphics primitive。
- 与 DisplaySurface 独立，可按输入频率更新。
- 不要求重新合成文档页面。

### 10.2 Grid/guide/selection/assistant

优先方案：

- GPU-native overlay primitive；或
- 有 dirty region 和稳定 allocation 的 `UiOverlaySurface`。

禁止普通帧路径：

- 每次 paint event 新建全窗口 QImage；
- 全图 clear/QPainter redraw；
- 全尺寸像素复制到 render state；
- 每帧全图上传。

只有不支持 GPU primitive 的 decoration 才进入 CPU overlay，并且必须按 dirty region 更新。

## 11. 延迟与渐进显示

系统区分：

- Accepted：journal 已接受；
- Executed：target generation 完成；
- Visible：相应 DisplaySurface page 完成；
- Presented：某一帧实际使用该 snapshot。

长笔迹/大 dab 可以按完整页面渐进 Visible。禁止：

- 展示半完成 page generation；
- 为等待一个冷页阻塞所有已经完成的其他 display page；
- 让 presentation deadline 改变 blend 顺序；
- 因窗口不可见而不执行 transaction。

## 12. 实现路线

### CP0：Segment planner reference

- 单目标 lower/target/upper 切分。
- upper 分类和 CPU reference composite。
- dependency revision/invalid region 测试。

### CP1：DisplaySurface

- page/revision/ticket 数据模型。
- dirty page composite 和完整页 publish。
- target writer -> composite GPU dependency。

### CP2：Presenter 分离

- 从 render thread 移除 brush journal 消费。
- 构造 `PresentRequest`、非阻塞 acquire、旧帧复用；实际 queue submit/present 由 coordinator 独占。
- swapchain blocked isolation test。

### CP3：WSI 生命周期

- resize/out-of-date/surface lost 不使用 device idle。
- WSI resource 按 last-use ticket 回收。

### CP4：Overlay

- outline 独立绘制。
- decorations GPU primitive/dirty overlay。
- 删除每帧全窗口 QImage 上传路径。

### CP5：多层与特殊 upper

- overlay/operator/replay GPU stages。
- 多 target segment DAG。
- 图层属性、mask、group revision 局部失效。

## 13. 验收门槛

- StrokeCompute command/submission 不引用 swapchain image/semaphore。
- acquire/present/resize/minimize/surface lost 不阻塞 stroke execution/commit。
- Presenter 从不 host-wait 一个未完成 DisplayReady ticket。
- target dirty page 只使必要 derived/display page 重算。
- lower checkpoint 在单目标 epoch 内稳定复用。
- backdrop-dependent upper 不被错误拍平成透明 overlay。
- DisplaySurface 每页只发布完整 generation。
- decorations 不再每帧全窗口生成、复制、上传 QImage。
- 阻塞 swapchain 的测试中，journal sequence、target generation 和 undo 仍完整推进。
