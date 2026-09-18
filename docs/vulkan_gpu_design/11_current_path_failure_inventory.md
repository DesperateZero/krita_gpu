# 当前 GPU Stroke 路径问题清单与退出边界

> 本文只记录当前源码事实、结构性风险和旧路径退出条件。目标架构见
> [10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md)，全局 P0 清除边界见
> [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)。本文不得被用来证明
> 当前能力已经完成，也不得把旧 runtime 延后到新路径启用时才删除。

## 1. 结论

当前实现不是可以通过补几个 barrier、增加 ring 大小或把下载改成异步就能成为长期基线的路径。
它把输入消费、brush compute、图层合成、全屏显示和 present 放进同一个 swapchain frame 生命周期，
同时以固定覆盖式 ring、逐 dab dispatch、render-thread 资源上传和 stroke-end pause/download 连接 Krita。

这套结构有四类不可局部消除的问题：

1. **正确性不闭合**：同页重叠 dab、transfer/sparse bind、pending generation 与新笔迹之间缺少可证明依赖。
2. **交互时序错误**：笔迹计算受 acquire/present、资源上传和 render frame fence 支配。
3. **数据模型错误**：GPU canvas 与 `KisPaintDevice` 通过 stroke-end 回灌维持两份状态，UMA 也没有共享权威页。
4. **退化行为错误**：容量不足时丢 dab，资源未准备时阻塞，页面不足时在首触达帧分配，失败时缺少恢复日志。
5. **模块所有权错误**：`kritaimagevulkan <-> kritaui` 构建环、global router 和 canvas/backend 裸指针使
   文档、UI 和后端生命周期不可隔离。
6. **格式/能力错误**：固定 RGBA8、raw projection bytes 和无条件 LoD 声明没有真实 capability 依据。

因此，新基线必须替换旧执行链，而不是在旧链上形成长期兼容层。

## 2. 当前调用链

```text
KisVulkanPaintOp::paintAt
  -> CPU dynamics -> StrokePoint
  -> KisVulkanPaintRouter::strokeTo
  -> fixed KisVulkanRingBuffer
  -> wake KisVulkanRenderThread

KisVulkanRenderThread::processFrame
  -> brush resource prepare/upload
  -> vkAcquireNextImageKHR
  -> wait frame fence
  -> BrushEngine::recordDabs
       -> ensureTilesForRegion
       -> one vkCmdDispatch per dab
  -> one compute-to-fragment barrier
  -> optional whole-stack compositor
  -> canvas/decorations graphics pass
  -> submit graphics queue
  -> present

KisVulkanPaintRouter::strokeEnd
  -> flushAndPause render thread
  -> dirty tile GPU-to-CPU download
  -> KisVulkanSyncStrokeStrategy::writeBytes
  -> transaction commit
  -> resume render thread
```

相关入口：

- [`KisVulkanPaintOp.cpp`](../../krita/libs/image_vulkan/KisVulkanPaintOp.cpp)
- [`KisVulkanPaintRouter.cpp`](../../krita/libs/image_vulkan/KisVulkanPaintRouter.cpp)
- [`KisVulkanRingBuffer.h`](../../krita/libs/image_vulkan/KisVulkanRingBuffer.h)
- [`KisVulkanBrushEngine.cpp`](../../krita/libs/image_vulkan/KisVulkanBrushEngine.cpp)
- [`KisVulkanRenderThread.cpp`](../../krita/libs/image_vulkan/KisVulkanRenderThread.cpp)
- [`KisVulkanSyncStrokeStrategy.cpp`](../../krita/libs/image_vulkan/KisVulkanSyncStrokeStrategy.cpp)

### 2.1 正常应用入口尚未闭环

- 正常启动路径没有可复现的 `KisVulkan::initialize()` 调用链；
- `useVulkanCanvas` 默认关闭，缺少完整用户设置、能力检查与成功/失败状态闭环；
- 因此当前代码级风险分析是“强制进入该路径后”的预测，不能把默认不可达状态当成稳定性证明；
- 新基线接入口必须在所有数据/transaction/回退门槛通过之后完成，不能仅把隐藏配置打开。

### 2.2 全局 Router 与双向依赖

- `KisVulkanPaintRouter::activeInstance()` 以全局当前 canvas/backend 决定 PaintOp 目标，多文档和多 canvas 会串扰；
- `kritaimagevulkan` 混合 PaintOp、RenderThread、Compositor 与 UI 类型，并反向链接 `kritaui`；
- `kritaui` 同时链接 `kritaimagevulkan`，形成必须在 BR0 拆除的构建环；
- 新路径必须由 `KisImage` 的 backend-neutral session slot 持有文档 session，PaintOp 通过
  `KisPaintExecutionContext` 获取它。

### 2.3 固定格式与能力虚报

- canvas、NodeSync、compositor 的多处路径固定 RGBA8/`pixelSize=4`；
- raw `readBytes()` 没有 `SurfaceFormat`/codec 就进入 GPU；
- canvas 没有 mip/page pyramid 仍报告 LoD 支持；
- 新路径必须在 BR0 删除这些运行路径，并按 format/capability golden 逐项重开。

## 3. P0 正确性问题

### 3.1 固定 ring 满后丢失已解析 dab

`KisVulkanPaintRouter::strokeTo()` 在 `push()` 失败时直接返回。已完成压力、间距、镜像、颜色等
CPU 语义计算的命令会永久消失。

实际后果：

- GPU 停顿首先表现为缺段，而不一定表现为 UI 阻塞；
- ring 被 resource upload、present 或 fence wait 堵住时更容易溢出；
- stroke end 无法证明所有已接受输入已经执行；
- 设备失败后没有可重放命令源。

不能接受的局部修复：

- 只把 2048 改成更大的常数；
- 在输入线程自旋等待 ring；
- 覆盖最旧命令；
- 只记录丢失计数但仍继续提交 transaction。

目标替代：分块不可变 `StrokeJournal`、明确 Accepted 状态和受预算 backpressure，见
[12_stroke_protocol_and_journal.md](12_stroke_protocol_and_journal.md)。

### 3.2 重叠 dab 缺少 read-modify-write 顺序

round/stamp shader 对同一 storage image 像素执行 `imageLoad -> blend -> imageStore`。当前 CPU 循环连续
记录多个 dispatch，但 dab 之间没有 compute-to-compute memory dependency。命令顺序本身不提供所需的
shader memory visibility。

实际后果：

- 相邻半透明 dab 可能读取旧目标值；
- apparent performance 可能来自缺少正确同步；
- 结果依赖驱动、设备和工作组调度；
- 最后一次 compute-to-fragment barrier 只能保证显示读取，不修复 dab 之间的竞争。

不能接受的局部修复：每个 dab 后插入 barrier。该方案虽然可以建立顺序，却把执行结构退化为严格串行，
保留了 per-dab CPU 录制和提交开销，也无法形成可扩展的超大笔尖路径。

目标替代：稳定页面/microtile 分桶，一个 invocation 独占一个目标像素并按序遍历 dab list，见
[13_page_work_compiler_and_gpu_kernel.md](13_page_work_compiler_and_gpu_kernel.md)。

### 3.3 Transfer、sparse bind 与 compute 依赖不闭合

当前 transfer queue 可以 signal timeline，但 graphics/compute submission 只显式等待 swapchain image
semaphore。`vkQueueBindSparse` 也没有形成可由目标 compute 等待的统一 ticket。

实际后果：

- 页面可能尚未 bind/restore 就被 brush 访问；
- brush resource 可能尚未上传完成就被采样；
- 新写入可能与旧 download 并发；
- command buffer 或 staging allocation 可能在 in-flight 时被 reset/reuse。

目标替代：所有 residency、bind、upload、snapshot、writer 和 composite 操作返回统一
`SubmissionTicket`，由 GPU-side wait 构成 DAG，见
[14_submission_tickets_and_queue_topology.md](14_submission_tickets_and_queue_topology.md)。

### 3.4 `flushAndPause()` 没有形成可靠 flush

当前调用同时设置 paused 和 flushRequested；render loop 尝试多处理一帧，但 `processFrame()` 开头看到
paused 后立即返回。这使 pause acknowledgment 与“pending dab 已完成”不是同一事实。

实际后果：

- stroke-end download 可能读取旧内容；
- render thread 若卡在 acquire/fence/upload，调用者可能等待到超时；
- timeout 后没有 generation 级失败状态；
- 新笔迹恢复后可能与旧回传重叠。

目标替代：End marker、final batch、`StrokeCommitTicket` 和 page last-writer dependency，见
[18_undo_save_cancel_and_recovery.md](18_undo_save_cancel_and_recovery.md)。

### 3.5 GPU canvas 与 CPU paint device 双权威

当前以 GPU tile dirty、stroke-end download、`writeBytes()` 回灌 `KisPaintDevice`。两个存储系统分别拥有
内容和生命周期，只有特定结束路径尝试同步。

实际后果：

- 保存、撤销、CPU filter 和新笔迹之间难以定义观察 generation；
- UMA 仍执行 staging copy；
- partial CPU update 需要 read-modify-write GPU tile；
- 任一路径遗漏同步就产生静默陈旧数据。

目标替代：把 Krita 现有 tile/COW/undo/swap 演进为 canonical PageStore，由 `KisPaintDevice` access facade
让同一 canonical surface 同时服务 CPU/GPU，而不是增加并列 data manager/provider，见
[17_krita_pagestore_integration.md](17_krita_pagestore_integration.md)。

### 3.6 当前 mapped ring 不是 GPU-driven command stream

ring 虽然分配为 host-visible mapped buffer，但消费端仍由 CPU render thread 读取每个 `StrokePoint`，转换 descriptor、
设置 push constants 并录制 dispatch。GPU shader 没有自主消费 ring/head/tail。

后果：

- 每 dab CPU 录制成本仍线性增长；
- UMA 的 command mapping 只省略小命令复制，不等于画布零拷贝；
- render thread 停顿就停止消费；
- 扩大 ring 不能改变提交结构。

目标不是让 shader 直接追逐可变 ring head，而是把 immutable journal batch 编译成稳定 PageJob/DabRef buffer。

### 3.7 Async transfer command resource 复用风险

当前 transfer 封装围绕少量 command buffer 和共享 recording 状态工作。异步 submit 后如果没有等待相应 ticket 就
reset/re-record command buffer，或把 detached staging 提前放回 cache，会违反 in-flight 生命周期。

目标替代：每个 command/transient allocation 记录 last-use ticket，由 SubmissionCoordinator 延迟回收；见
[14_submission_tickets_and_queue_topology.md](14_submission_tickets_and_queue_topology.md)。

### 3.8 Dirty eviction 不能证明数据安全

当前 tier/age 驱动的释放没有统一 authoritative generation、writeback ticket 和失败状态。dirty page 在解绑/复用前
未必已经成功回写，prefetch 恢复也未必上传正确 backing。

这不是 eviction policy 参数问题，而是缺少 PageStateMachine。目标处理见
[15_stroke_residency_and_memory_backends.md](15_stroke_residency_and_memory_backends.md)。

## 4. P0/P1 延迟问题

### 4.1 Stroke compute 被 swapchain 阻塞

render thread 在读取 dab 前先 acquire swapchain image，并等待 frame fence。笔迹计算、合成和显示共用一个
command buffer 与 graphics queue submission。

可能触发：

- vsync/present backpressure；
- 窗口遮挡、最小化或 surface out-of-date；
- resize/recreate；
- 显示帧中其他 graphics 工作过重。

目标替代：独立 StrokeCompute queue/command lane、DisplaySurface 和 Presenter，见
[16_incremental_composite_and_presenter.md](16_incremental_composite_and_presenter.md)。

### 4.2 Brush resource 首次上传同步等待

当前 texture upload 在 render thread 上提交 fence 并等待完成。新 preset、大 tip、texture 或 mask 会让
render thread 停止消费 dab。

目标替代：preset 选择阶段建立不可变 `PreparedBrushProgram`，resource ready ticket 成为 batch dependency，
整个 stroke epoch 一次决定 GPU 或 CPU backend，见
[19_brush_resources_and_capability_gate.md](19_brush_resources_and_capability_gate.md)。

### 4.3 冷页分配和 bind 位于首触达帧

`recordDabs()` 在提交前扫描所有 dab 并 `ensureTilesForRegion()`。若预取没有正确接线，页分配、稀疏绑定
和恢复集中到用户第一次画入区域的帧。

目标替代：trajectory/halo 预热、异步 residency ticket、页温度和 deadline，见
[15_stroke_residency_and_memory_backends.md](15_stroke_residency_and_memory_backends.md)。

### 4.4 UI 线程存在全设备/同步下载等待

resize 路径调用 `vkDeviceWaitIdle()`；partial tile update 可能同步下载 GPU 内容。它们会直接冻结 GUI，
而不是只降低绘制帧率。

目标替代：Presenter 独立重建；所有 CPU 像素访问先通过后台 operation 取得区域 lease；UI 不直接访问
transfer/page backend。

### 4.5 全窗口 decoration QImage 每帧生成和上传

当前 paint event 创建物理窗口尺寸 QImage、QPainter 重画 decorations，再把整块像素上传 GPU。高 DPI/4K
下该路径可以消耗大量 CPU、内存带宽和 transfer 带宽，并把抖动注入显示帧。

目标替代：独立 overlay surface、dirty region、稳定 GPU/CPU resource；brush outline 与 canvas content
保持独立，见 [16_incremental_composite_and_presenter.md](16_incremental_composite_and_presenter.md)。

### 4.6 Frame pacing 直接增加输入延迟

当前 render thread 以固定目标间隔休眠，并在空闲时使用更长 wait。即使 GPU 工作提前完成，输入也可能等待下一轮
frame loop；compute 与 present 共用 loop 后，这个 sleep 同时限制笔迹消费。

目标替代：StrokeCoordinator 以 batch deadline/命令压力唤醒独立 compute lane；Presenter 按显示机会工作，二者
不共享固定 `msleep` 节拍。

### 4.7 Layer compositor 默认工作粒度和接线不可靠

当前 compositor 可以在每个显示 frame 进入多层合成，现有输出 descriptor、target 清零、layout、descriptor 生命周期
和 NodeSync invalidation 均未形成端到端证明。非活动层整图 image 还绕过页面预算。

后果不是单纯“图层多时慢”，而是结果、内存规模和失效范围都无法证明。目标替代为 ActiveTargetSet segment、
page-level dirty propagation 和 DisplaySurface，见
[16_incremental_composite_and_presenter.md](16_incremental_composite_and_presenter.md)。

### 4.8 Prefetch 没有形成真实输入闭环

已有 prefetch/age 类和调用点不等于工作策略已经生效。viewport、brush trajectory、halo、dirty cost、cache coverage、
deadline 与 restore ticket 没有作为统一输入闭环到 ResidencyController。

目标不是继续给 `age()` 增加权重，而是以 StrokeAccessPlan 和语义温度驱动，见
[15_stroke_residency_and_memory_backends.md](15_stroke_residency_and_memory_backends.md) 和
[38_virtual_texture_residency_temperature.md](38_virtual_texture_residency_temperature.md)。

## 5. 当前性能数据为什么不可作为验收

当前 `computeMs` 主要覆盖 CPU command recording 时间，在 GPU 执行前结束。它不能回答：

- GPU brush 实际耗时；
- queue wait 和 residency stall；
- input-to-visible latency；
- page fault、upload、composite 与 present 各自占比；
- p95/p99 尖峰；
- 丢失 dab 是否让工作量看似更低。

新基线必须使用 GPU timestamp、ticket trace 和 sequence accounting，见
[20_observability_testing_and_performance.md](20_observability_testing_and_performance.md)。

## 6. 可保留的输入与必须退出的实现

### 6.1 可提取并重新验证

- `KisVulkanPaintOp` 与 Krita paintop/preset 的接入位置；
- resolved dab 已有字段与部分 CPU dynamics；
- round/stamp shader 的数学公式；
- blend enum 和共享映射；
- transfer timeline 封装经验；
- `KisStrokeJob`/transaction 的业务接入位置；
- canvas transform、outline 和 display shader 的实验结果。

“可提取”不等于原类直接成为目标模块。所有内容都需要在新不变量和测试下重新验收。

### 6.2 新基线必须删除

- 固定容量、满后丢命令的 GPU stroke ring；
- render thread CPU 读取 ring 后逐 dab push constants/dispatch；
- brush compute 与 swapchain command buffer 的绑定；
- render thread 同步 brush resource upload；
- `flushAndPause()` 作为完成协议；
- stroke-end tile download 作为 CPU/Krita 一致性主路径；
- Vulkan canvas 直接管理 target residency/transfer；
- 全帧 decoration QImage upload；
- 同一页面同时由 GPU canvas 和 CPU paint device 维护权威版本；
- 新旧 GPU stroke 状态机并存的长期配置开关。
- `KisVulkanPaintRouter::activeInstance` 与全局 factory wrap；
- `kritaimagevulkan` 对 `kritaui` 的反向依赖；
- fixed RGBA8/raw projection upload 与无实现的 LoD 声明。

## 7. 退出判定

旧路径不等待替代实现完成，而是在 BR0 归档后从新校正分支直接删除。校正期间 Vulkan 不可用，CPU/OpenGL
承担产品路径。这样新模块从第一天起就无法依赖错误对象模型，也不需要维护双写和兼容适配。

BR0 的退出判定：

1. 归档分支/tag 可复现旧原型，Git 历史保存研究价值；
2. 上述旧 runtime、配置、注释和构建边已经从新树删除；
3. Vulkan 用户入口关闭，不能靠隐藏配置进入半实现；
4. CPU/OpenGL 与更新后的 upstream 回归一致；
5. CI 能拒绝旧符号、双向依赖、queue API 旁路和 wait-idle 回归。

全局删除和重建顺序见 [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md)。
GPU stroke 内部新实现工作包见 [21_implementation_and_baseline_cutover.md](21_implementation_and_baseline_cutover.md)。
