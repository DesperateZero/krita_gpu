# Submission Ticket、Queue 拓扑与线程所有权

> 本文定义所有 GPU/IO 工作如何形成显式依赖，如何避免 host wait，以及 Vulkan queue、command resource
> 和对象生命周期由谁拥有。全局线程硬边界见
> [27_p0_submission_threading_zero_blocking.md](27_p0_submission_threading_zero_blocking.md)，页面状态见
> [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md)。

## 1. 目标

同步模型必须让系统能回答：

- 某个 page generation 的前置 bind/upload/snapshot 是否完成；
- 哪个 queue/lane 是最后 writer；
- 下一个 GPU consumer 应等待什么；
- CPU read lease 应等待哪个精确 generation；
- command buffer、descriptor、staging 和 allocation 何时可回收；
- 失败/取消后哪些 completion 已过期；
- swapchain 阻塞时为什么 stroke 仍可继续。

任何依赖都不能通过“通常在同一个队列”“CPU 刚刚 wait 过”或“上一帧应该完成了”隐式推断。

## 2. 逻辑执行域

至少定义：

```text
HostAdmission
ResidencyIO
Transfer
SparseBind/PageTablePublish
StrokeCompute
CompositeCompute
DisplayGraphics
Present
CpuConsumer
```

`HostAdmission` 和 `CpuConsumer` 不是 Vulkan queue，但也用 operation/ticket 进入统一 trace。

逻辑域与物理 queue 不是一一对应：

- UMA 可能不需要独立 transfer queue；
- dGPU 可以有 dedicated transfer；
- sparse bind 可能需要支持 sparse 的 graphics queue；
- StrokeCompute 与 CompositeCompute 可以共用 compute queue；
- Present 必须与 StrokeCompute 使用不同 `VkQueue` 或后端等价独立 command queue；同一串行 queue 上的不同 command buffer 不构成隔离。

## 3. 设备 Queue 选择

### 3.1 必需能力

初始化时生成 `QueueTopologyReport`：

```text
queue family/index
flags
queue count
present support
sparse support
timestamp valid bits
requested/global priority
logical lane mapping
ownership transfer requirements
```

低延迟 GPU stroke capability 至少要求：

- 一个不执行 WSI present 的 StrokeCompute queue；
- 一个 Present queue；
- 所有 target format/kernel feature 支持；
- timeline semaphore 或等价可组合异步 primitive；
- 可用 GPU timestamp。

若设备只有一个必须同时承担 present 与 compute 的串行 queue，则它可以运行实验路径，但不能标记满足本基线
的 presentation isolation。正常应用必须选择 CPU/其他成熟 backend，而不是静默降低硬边界。

### 3.2 Queue family ownership

- shared buffer page 优先使用 concurrent sharing 或稳定 owning family，避免高频 ownership transfer。
- 若 transfer/compute/graphics family 不同，ticket operation 必须携带 release/acquire barrier。
- image layout 与 queue family owner 是 page/view 状态的一部分，不能由每个调用点自行假定。
- WSI image 只属于 presenter；canonical target page 不直接成为 swapchain image。

## 4. `SubmissionTicket`

建议字段：

```text
OperationId
LaneId
TimelineId
TimelineValue
OperationKind
AffectedObjectGenerations[]
ResultState
ErrorCode
TraceCorrelationId
```

ticket 是值对象/稳定 handle，不暴露 `VkFence*`、command buffer 或 queue 指针。

### 4.1 状态

```text
Allocated -> Submitted -> Signaled -> Published -> Retired
                  \-> Failed
Allocated/Submitted -> CancelRequested
```

- `Signaled`：底层执行 primitive 完成。
- `Published`：completion 已通过 generation 检查并更新 PageStore/Resource 状态。
- `Retired`：没有依赖者且相关临时资源已回收。
- 迟到 signal 仍必须经过 publish 检查，不能直接修改对象状态。

### 4.2 Ticket 组合

`SubmissionCoordinator` 支持：

```text
join(ticket[])
submit(lane, waits[], commandBatch) -> ticket
poll(ticket) -> state
registerCompletion(ticket, callback)
deferRelease(resource, lastUseTicket)
```

`join` 可以是纯逻辑 dependency set，不必创建一个空 GPU submission。重复 ticket 去重，但不能丢失不同
generation 的检查。

## 5. Stroke submission DAG

一个典型 PageJob batch：

```text
SSD read -> RAM valid
             -> upload -> VRAM valid
sparse bind/direct-local binding publish ---------+
brush resource ready -------------------+
before-image snapshot ------------------+
previous page writer -------------------+
                                        -> StrokeCompute
                                             -> page generation publish
                                             -> IncrementalComposite
                                                  -> DisplayReady
```

规则：

- compiler 只声明依赖；coordinator 把依赖翻译为 semaphore waits/barriers。
- GPU 能等待的工作必须使用 GPU-side wait，不能先让 CPU wait 再提交。
- SSD/CPU IO completion 通过 host signal timeline 或后续 upload submission 接入 DAG。
- 每个 page generation 记录 last-writer ticket。
- composition 读取的是明确 generation，而不是“当前 image 内容”。

## 6. SubmissionCoordinator

### 6.1 单一职责

coordinator 是所有 Vulkan queue submit/bind-sparse/present 调用的唯一 host owner：

- 分配 timeline value；
- 验证 dependency DAG 无环；
- 合并同 lane 小 submission；
- 生成 queue ownership/layout barrier；
- 提交 command buffer；
- 执行 `PresentRequest`；
- 收集 completion；
- 发布 generation/resource state；
- 延迟回收临时对象；
- 记录 trace。

其他模块提交逻辑 command batch/request，不直接调用 `vkQueueSubmit`、`vkQueueBindSparse`、
`vkQueuePresentKHR` 或 `vkQueueWaitIdle`。

### 6.2 外部同步

Vulkan 要求对同一 `VkQueue` host access 外部同步。实现可采用：

- 单 coordinator thread；或
- 每 queue 一个由 coordinator 管理的串行 executor。

不能让 render thread、transfer helper、brush uploader 各自持有同一 queue 并仅靠局部 mutex 猜测全局顺序。

### 6.3 公平性

调度优先级：

1. 当前目标页前置 residency/snapshot；
2. latency-critical StrokeCompute；
3. visible dirty composite；
4. present-ready graphics；
5. predictive prefetch；
6. background writeback/SSD/derived rebuild。

优先级不能违反依赖，也不能饿死 dirty writeback 直到预算耗尽。ResidencyController 提供 deadline、pin 和
高低水位，coordinator 负责可运行 operation 的顺序。

## 7. Host wait 规则

### 7.1 热路径禁止

以下线程/操作禁止等待 GPU：

- UI/input event loop；
- `paintAt()`/dab admission；
- stroke end；
- PageWorkCompiler；
- Presenter 为等待“更新一帧”而阻塞；
- preset 切换/首个 dab resource upload；
- swapchain resize 对全设备 idle。

禁止调用：

- `vkDeviceWaitIdle()`；
- `vkQueueWaitIdle()`；
- 无限期 `vkWaitForFences()`；
- 用 condition variable 把上述 GPU wait 转移成间接 UI wait。

### 7.2 允许的等待

- 应用关闭或 device teardown；
- device-loss recovery 的受控停止；
- 明确标记 blocking 的调试/测试 API；
- 后台 CPU consumer 为读取指定 generation 等待 read lease；
- 旧同步 CPU 算法在 Krita stroke worker 上等待其事先声明区域的 CPU lease。

即使允许，也必须：

- 等待精确 ticket/generation；
- 有取消和错误传播；
- 不使用全局 device idle 代替局部依赖；
- 进入 trace 和超时诊断。

## 8. Presenter 与 WSI 同步

- swapchain binary semaphore/fence 只存在于 Present lane。
- Presenter 非阻塞/有界 acquire；无 image 时跳过该次 present。
- Presenter 查询最新已完成 `DisplayReady` generation，不等待未完成 generation。
- Presenter 只构造 immutable `PresentRequest`；实际 `vkQueuePresentKHR` 由 `SubmissionCoordinator` 执行。
- 可以重复显示上一完成 generation。
- swapchain recreate 只回收 WSI resources，依赖其自身 last-use ticket。
- StrokeCompute/Composite 不等待 imageAvailable semaphore。
- resize/minimize/surface lost 不改变 canonical page generation。

## 9. Command 与资源生命周期

### 9.1 Command pool/buffer

- command pool 按 queue/lane 和 owning thread 划分。
- command buffer 在 last submission ticket Signaled 前不能 reset/re-record。
- 不能只有一个 transfer command buffer，在 async submit 后立即 reset。
- pool retirement 通过 timeline value 批量完成，不逐提交 host wait fence。

### 9.2 Descriptor

- descriptor arena 的 slot 记录 last-use ticket。
- immutable ResourceSet 在所有引用 batch 退休前保持有效。
- direct/local binding table 或 descriptor 更新需要 publish ticket；consumer 显式等待。
- 不允许每帧/每 dab 分配后无限不回收。

### 9.3 Staging/transient allocation

- allocation 与 operation id/generation 绑定。
- upload/download completion 后才能进入 allocator free list。
- CPU job 仍持有 mapped pointer 时不能回收。
- cancel 只撤销逻辑 consumer，不自动释放 in-flight backing。

## 10. Barrier 生成

coordinator/backend 根据 resource access declaration 生成 synchronization2 barrier：

```text
previous stage/access/layout/owner
next stage/access/layout/owner
subresource/page range
```

典型依赖：

- transfer write -> compute read；
- sparse/direct-local binding publish -> compute read/write；
- compute page write -> compute page read/write；
- stroke compute write -> composite compute read；
- composite write -> display graphics read；
- CPU write flush/release -> GPU compute read；
- GPU write signal -> CPU invalidate/read。

不能只使用一个宽泛 memory barrier 掩盖未声明 resource range。debug build 应输出 barrier trace 并检查
old layout/owner/generation。

## 11. Completion、错误和超时

- timeline signaled 不等于业务 publish；先验证 operation result 和 generation。
- submit 失败时 ticket 进入 Failed，所有依赖 operation 取消或走恢复分支。
- CPU wait 超时不能把页面标为 clean/valid。
- device lost 使相关 GPU lane ticket 进入 indeterminate/failed，由恢复系统依据 journal 和 committed generation 决定。
- 错误必须携带 OperationId、page/resource generation 和依赖链，不能只打印 VkResult。

## 12. 实现路线

### SQ0：抽象 ticket 与 fake executor

- 不依赖 Vulkan 的 ticket/DAG/publish 状态机。
- generation mismatch、取消、迟到 completion 和环检测测试。

### SQ1：Queue topology

- 设备 capability report。
- lane 到不同 `VkQueue` 的映射。
- 不满足 present isolation 的设备明确拒绝能力。

### SQ2：Timeline submission

- per-lane timeline 或统一 timeline namespace。
- GPU-side waits/signals。
- command pool 和 transient allocation 延迟回收。

### SQ3：Transfer/sparse/direct-local binding 接入

- 删除 helper 自主 queue submit。
- bind/upload/download 全部返回 ticket。
- queue family ownership/layout 状态集中化。

### SQ4：Stroke/composite/present DAG

- PageJob dependency translation。
- DisplayReady 非阻塞选择。
- swapchain destroy/recreate isolation test。

### SQ5：故障和诊断

- submit failure、timeline delay、device lost 注入。
- dependency graph/operation trace 导出。
- 禁止 host-wait API 的静态/运行时断言。

## 13. 验收门槛

- 所有 GPU 工作都有 OperationId、ticket、declared resource access 和 completion state。
- graphics/compute 正确等待 transfer/sparse/resource/snapshot/previous-writer。
- 同一 `VkQueue` 没有多个未协调 host owner。
- command buffer、descriptor、staging 不在 in-flight 时复用。
- UI、input、stroke end 和 presenter 更新路径没有 host GPU wait。
- swapchain acquire/recreate 阻塞或失败时 StrokeCompute 继续执行。
- generation mismatch/迟到 completion 不能覆盖新状态。
- device/queue 能力不足时显式回退，而不是降低同步硬边界。
