# P0：SubmissionCoordinator、线程模型与“零阻塞”

> 本文是 Vulkan 全局提交/线程权威设计。GPU stroke 细节见
> [14_submission_tickets_and_queue_topology.md](14_submission_tickets_and_queue_topology.md)，本文进一步规定所有
> queue API（包括 present）只能由 SubmissionCoordinator 调用，以及可续执行 CPU job/关闭顺序。

## 1. 唯一 Queue Owner

进程内每个 Vulkan device generation 只有一个 `SubmissionCoordinator` 服务。只有它可以调用：

```text
vkQueueSubmit / vkQueueSubmit2
vkQueueBindSparse
vkQueuePresentKHR
```

其他模块提交不可变逻辑请求：

- TransferRequest；
- SparseBind/PageTablePublishRequest；
- ComputeRequest；
- GraphicsRequest；
- PresentRequest。

Presenter 不直接调用 `vkQueuePresentKHR`；它构建 PresentRequest。Transfer/brush/compositor 也不持有 raw queue。

## 2. Queue 拓扑

初始化生成不可变拓扑：

```text
QueueFamily/QueueIndex
Capabilities
PresentSupport
SparseSupport
TimestampBits
LogicalLaneAssignment
Priority
OwnershipTransferPolicy
```

逻辑 lane：

- Transfer；
- Sparse/PageTable；
- StrokeCompute；
- CompositeCompute；
- DisplayGraphics；
- Present。

StrokeCompute 与 Present 必须映射到不同 `VkQueue` 或平台等价独立 command queue。可以同 family。只有一个
串行 present+compute queue 的设备不满足低延迟 Vulkan基线，必须在能力路由前回退。

## 3. Timeline DAG

每个 operation：

```text
OperationId
Lane
WaitTickets[]
DeclaredResourceAccess[]
CommandBatch/HostContinuation
SignalTicket
FailurePolicy
```

依赖包括：

- replica materialization；
- sparse bind/direct-local binding publish；
- CPU flush/release；
- brush resource ready；
- page previous writer；
- COW snapshot；
- stroke compute；
- composite/display；
- swapchain image/present。

GPU可表达的依赖使用timeline/binary semaphore和barrier，不先让CPU wait再submit。

## 4. Command Arena

当前单transfer command buffer模型永久删除。每queue family/lane使用timeline管理arena：

```text
CommandPoolShard
CommandBufferSlot
LastSubmittedTimelineValue
RecordingOwner
TransientAllocationSet
DescriptorUseSet
```

规则：

- slot只有在对应timeline完成值达到后回到free list；
- async submit后不得立即reset；
- command pool由所属coordinator executor/thread使用；
- transient/staging/descriptor各自记录last-use ticket；
- 批量回收通过poll完成值，不逐operation host fence wait；
- shutdown只等待已知最高提交值，不对仍接受新工作device idle。

## 5. 线程角色

### UI/Input

- 提交input、viewport、immutable display snapshot request；
- 不调用Vulkan wait；
- 不materialize page；
- 不做SSD IO；
- 不进入PageStore内部锁。

### Krita Stroke Scheduler

- 执行/续跑CPU paint/filter/save job；
- 请求lease/ticket；
- 缺页时挂起operation并注册continuation；
- lease ready后重新排队，不占住worker线程同步等待。

### Compiler/Planner Workers

- 只处理immutable metadata/work；
- 不持queue；
- 不等待GPU。

### Residency/IO

- 执行压缩/SSD read/write等CPU IO；
- completion通过ticket/continuation发布；
- 不直接改PageStore published state。

### SubmissionCoordinator

- 独占queue API；
- 构建barrier/ownership；
- submit/present；
- poll timeline；
- publish completion event；
- deferred reclamation；
- 不等待CPU fence/condition完成业务输入。

## 6. 可续执行 CPU Job

同步旧算法需要页面时：

```text
job creates AccessPlan
-> acquire request returns pending ticket
-> job stores continuation state and yields worker
-> PageStore/IO completes ticket
-> scheduler requeues job
-> resolve lease
-> run synchronous pixel loop
-> release/publish
```

禁止：

- worker持锁阻塞数秒等SSD/GPU；
- UI线程调用同步 accessor触发materialization；
- 每个tile循环内wait；
- 用busy polling占用worker。

对于必须兼容的同步API，调度边界负责预先materialize区域；违反者在debug/CI中断言。

## 7. WSI/Presenter

- `vkAcquireNextImageKHR` 使用timeout=0或有界策略；无slot跳过帧。
- swapchain binary semaphore只进入Present/Display lane。
- PresentRequest只消费已完成DisplaySurface generation。
- resize创建新SwapchainGeneration；旧generation资源按last-use ticket退休。
- 不调用`vkDeviceWaitIdle()`重建。
- minimize/occlusion可停止present，stroke/session继续。

## 8. Host Wait 禁止与允许

### Runtime禁止

- UI/input wait；
- stroke admission/end wait；
- submission/render thread wait CPU fence；
- resource首次使用wait；
- resize/device-wide wait；
- save/export在UI wait；
- 无限`vkWaitForFences`；
- `vkQueueWaitIdle`/`vkDeviceWaitIdle`。

### 允许

- 独立测试明确验证blocking API；
- process退出最后阶段，在已拒绝新请求且提交集合冻结后等待已知timeline值；
- device lost后平台销毁API要求的受控处理；
- 不可续执行的第三方CPU算法在专用worker等待精确lease（应逐步消除，并有trace/timeout）。

允许路径不能成为正常绘制/显示/保存热路径。

## 9. Shutdown

固定顺序：

```text
1. Backend service state -> Draining，拒绝新session/request
2. Document sessions拒绝新stroke/view/save
3. 取消未提交operation；已提交operation完成或进入恢复策略
4. continuation/transaction达到可终结状态
5. 冻结SubmissionCoordinator输入
6. 等待每lane已知最高timeline value（有界诊断）
7. 回收command/descriptor/replica/WSI
8. 销毁device/service
```

禁止对仍可能被其他线程submit的device调用`vkDeviceWaitIdle()`。

## 10. 错误/超时

- submit/present/bind失败产生结构化operation failure；
- timeout不标记page clean/valid；
- generation mismatch completion只丢弃目标结果，不回退覆盖；
- device lost使该device generation所有pending ticket失效/indeterminate；
- canonical RAM/SSD/journal由document recovery处理；
- coordinator不调用业务层rollback，发布failure事件由PageStore/session决策。

## 11. 静态边界

CI扫描：

- 除coordinator implementation/测试mock外出现queue API即失败；
- runtime `vkQueueWaitIdle`/`vkDeviceWaitIdle`即失败；
- 无限fence wait即失败；
- UI source中page materialize/SSD/direct queue访问即失败；
- command buffer reset没有last-use guard的测试失败。

## 12. 实现路线

### ST0：Ticket/fake DAG

- backend-neutral ticket、operation、continuation。
- reorder/failure/cancel/late completion tests。

### ST1：Queue service

- topology、lane mapping、single owner。
- queue API全部集中。

### ST2：Command arena

- pool shard、timeline retirement、descriptor/staging use。
- 删除单buffer transfer。

### ST3：Replica/stroke/composite requests

- resource access declaration/barrier。
- transfer/sparse/compute/graphics DAG。

### ST4：Present request

- nonblocking acquire、coordinator present、swapchain generation。

### ST5：Continuation scheduler

- CPU lease pending/yield/resume。
- save/filter/page-fault tests。

### ST6：Shutdown/fault

- reject/drain/timeline/destroy。
- concurrent submit shutdown和device lost injection。

## 13. 验收门槛

- queue submit/bind/present只有一个源码owner。
- command/staging/descriptor不在in-flight时复用。
- UI/input/submission/stroke-end/resize无host wait。
- CPU缺页job挂起续跑，不占worker。
- swapchain无slot/resize/minimize不阻塞document session。
- shutdown在并发压力下不对active device调用waitIdle。
- 同family多queue、独立family两套矩阵通过。
- ticket DAG、barrier、ownership、failure都有trace和测试。
