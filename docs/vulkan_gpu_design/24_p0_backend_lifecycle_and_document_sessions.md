# P0：Backend 生命周期、DocumentGpuSession 与多文档隔离

> 本文解决 Vulkan 入口不可达/假成功、全局 active Router、factory wrap、多 canvas 串扰和 backend 裸指针生命周期。

## 1. 当前问题

- `KisVulkanCanvas` 构造期间写入 `VULKAN_STARTED`，并不能证明 device、shader、swapchain、document session 全部可用。
- `useVulkanCanvas` 是隐藏/default-off 配置，缺少完整产品设置与失败闭环。
- 正常应用没有可复现的 `KisVulkan::initialize()` 生命周期调用证据。
- `KisVulkanPaintRouter::activeInstance()` 是进程全局 mutable pointer。
- PaintOpFactory、PresetShadowUpdater 和 Canvas 通过该全局指针找到“当前”路由。
- 多文档、多窗口或关闭一个 canvas 时，active instance 与实际 paint device/session 可以错配。

## 2. 设备服务状态机

```text
Unavailable
  -> Probing
  -> Initializing
  -> Ready(BackendReadyToken)
  -> Draining
  -> Shutdown

Probing/Initializing -> Failed(BackendFailureReport)
Ready -> DeviceLost -> Recovering/Failed
```

### 2.1 `BackendReadyToken`

token 必须：

- 构造函数私有，只能由成功完成全部初始化的 service factory 创建；
- 绑定 device generation、queue topology、shader ABI、capability descriptor；
- 引用计数/所有权明确，backend draining 后不能用于新 session；
- 不可由 bool、config string 或静态 `isAvailable()` 伪造；
- device lost 后失效，新 device 产生新 generation/token。

Ready 前必须完成：

- instance/device/allocator；
- required queue 隔离；
- timeline/timestamp/format feature；
- required shader/pipeline layout asset 验证；
- SubmissionCoordinator；
- PageReplicaProvider registration；
- validation/failure report setup。

## 3. 不可变设备服务注册表

允许的全局状态只有设备服务发现/注册表：

- entry 是不可变 service descriptor/factory；
- 不包含 current document/canvas/paint device；
- 不暴露 raw device/queue mutable singleton；
- application composition root 在启动/设置时选择 service；
- tests 可以创建 isolated service instance。

禁止：

- `activeInstance()`；
- `currentRouter()`；
- “最近创建 canvas”覆盖全局指针；
- plugin factory 静态替换全局原 factory；
- UI 对 backend singleton 改 target paint device。

## 4. DocumentGpuSession 所有权

### 4.1 核心 slot

`KisImage` 拥有 backend-neutral session slot/registry，定义在 `kritaimage`。它记录：

```text
DocumentId
Image/Graph generation
Canonical Surface registry
AccelerationSession interface handle
Session state
Attached view ids
Pending transaction/session tickets
```

### 4.2 Vulkan concrete session

`kritavulkanbackend` 创建 `VulkanDocumentGpuSession`，实现 backend-neutral interface：

- 绑定一个 BackendReadyToken/device generation；
- 注册该文档 canonical surfaces 的 Vulkan replica provider；
- 持有 StrokeCoordinator、EvaluationGraph lowerer/planner、derived cache/composite backend、document operation ledger；
- 不持有 QWidget/QWindow；
- 不由任一 canvas 独占。

### 4.3 多 canvas

同一 `KisImage` 的多个 canvas：

- 共享一个 document session 和 canonical/derived generation；
- 每个 canvas 有独立 ViewAttachment、viewport、display transform、swapchain generation；
- 关闭一个 canvas 只 detach 对应 view；
- 最后一个 canvas 关闭不必销毁 document session，文档可能仍需 save/undo/background jobs；
- 文档关闭才进入 session draining。

不同 `KisImage`：

- 不共享 session、StrokeId namespace、SurfaceRegistry 或 transaction ledger；
- 可以共享不可变 device service、pipeline cache 和 deduplicated immutable brush resources；
- page budget由 ResidencyController 按 document/session 隔离和仲裁。

## 5. `KisPaintExecutionContext`

PaintOp/StrokeStrategy 创建时获得显式 context：

```text
DocumentId
Image/Graph handle
Non-empty unique WritableTarget PaintDevice/Surface identities
DocumentGpuSession handle（可空）
Backend capability snapshot
Stroke scheduler/transaction context
```

规则：

- context 从实际 `KisImage`/writable targets 构建，不从 active canvas 查找；
- headless、无 canvas、多个 canvas 都可工作；
- context 中 session handle 使用 generation/weak ownership 防止文档关闭后悬空；
- GPU 不可用时 session 为空，factory 正常选择 CPU paintop；
- PaintOp 不持有 Canvas/Router/Vulkan backend 裸指针。

## 6. Canvas 激活协议

Vulkan canvas 替换成熟 canvas 前必须同时具备：

1. 有效 `BackendReadyToken`；
2. 对应 `KisImage` 的 Ready `DocumentGpuSession`；
3. 成功创建的 view attachment；
4. 成功创建的 surface/swapchain generation；
5. 支持当前 SurfaceFormat/display/filter/LoD 请求的 capability；
6. 初始 DisplaySurface snapshot 或明确 loading/fallback 状态；
7. 安全回退 canvas 尚可恢复。

只有状态机完成后才更新用户配置/运行状态。构造函数开始执行不能写 `VULKAN_STARTED`。

失败：

- 销毁部分 view/WSI resources；
- document session/canonical data不受污染；
- 保持/恢复 CPU/OpenGL canvas；
- 记录结构化 failure report；
- 不反复崩溃式重试。

## 7. 用户开关与可用性

BR0–BR5：

- Vulkan 用户选项不展示或强制不可用；
- 仅 offscreen/CI/developer harness 使用；
- 不通过隐藏配置让错误 runtime 可进入正常绘画。

BR6 完整验收后：

- 设置页读取 backend capability descriptor；
- 展示精确 unsupported reason；
- 切换需要安全重建 view attachment，不改变 canonical document store；
- 失败自动回退成熟 canvas；
- `isAvailable()` 只可作为静态编译/平台提示，不能替代 ReadyToken/session/view handshake。

## 8. Session 生命周期

### 创建

```text
KisImage ready
-> request acceleration session
-> bind BackendReadyToken
-> register canonical surfaces
-> create document ledgers/controllers
-> Ready
```

### 文档关闭

```text
reject new stroke/view attach
-> detach all views
-> cancel/complete pending stroke and save policy
-> wait known session tickets through continuation/drain operation
-> unregister replicas/resources
-> release concrete session
```

不允许 canvas destructor 直接 shutdown 全局 backend 或清空 active router。

### Device lost

- 所有绑定旧 device generation 的 sessions 进入 Recovering；
- canonical PageStore、RAM/SSD/COW 保持在 `kritaimage`；
- journal/transaction 按恢复文档处理；
- 新 BackendReadyToken 成功后 sessions 可重新附着 replica provider；
- canvas 等待新 view attachment 或回退，不控制数据恢复。

## 9. Capability snapshot

session begin stroke/view operation 时获取不可变 capability descriptor：

- format/codec；
- queue topology；
- stroke program；
- composite/display；
- LoD/page pyramid；
- recovery；
- device limits。

operation 期间 capability 不原地改变。device/pipeline generation 变化创建新 descriptor/session epoch。

## 10. 实现路线

### DS0：Core interface

- backend-neutral session slot/interface、DocumentId/ViewId。
- `KisPaintExecutionContext` 注入。
- CPU-only tests 证明无 canvas/global router 也可创建 paintop。

### DS1：Device service/token

- 初始化状态机、failure report、不可伪造 token。
- queue/shader/capability 验证。

### DS2：Document session

- Vulkan concrete session factory。
- SurfaceRegistry/operation ledger attachment。
- 多文档隔离测试。

### DS3：View attachment

- 一个文档多个 swapchain/view。
- 关闭/重建单一 canvas 不影响 session。

### DS4：PaintOp/transaction context

- 删除 factory global wrap/active router。
- 显式 target/session/backend selection。

### DS5：Normal entry

- BR6 后设置/activation handshake。
- failure fallback 和状态报告。

## 11. 必须删除

- `KisVulkanPaintRouter::activeInstance/setActiveInstance`；
- Canvas 内 document-global PaintRouter 所有权；
- PaintOpFactory 从 global router 判断支持；
- PresetShadowUpdater 访问 active router；
- 构造函数写 `VULKAN_STARTED`；
- hidden `useVulkanCanvas` 作为唯一入口；
- 跨线程裸 brush backend pointer。

## 12. 验收门槛

- backend ReadyToken 无法由配置/构造半程伪造。
- 无 canvas/headless PaintOp 能通过 context 正确选择 CPU/GPU session。
- 两文档并发绘制完全隔离。
- 同文档两 canvas 共享内容但拥有独立 WSI 生命周期。
- 关闭任一 canvas 不取消另一 canvas 或文档 stroke/save。
- device lost 不销毁 canonical document data。
- 正常入口只有 BR0–BR6 完成后开放，失败可靠回退。
- 源码不存在 active router/factory wrap/runtime global document pointer。
