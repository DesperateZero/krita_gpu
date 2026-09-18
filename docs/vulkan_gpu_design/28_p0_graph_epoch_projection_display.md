# P0：GraphEpoch、Projection、Derived Cache 与 Display

> 本文解决 projection、活动层和显示共用一张 image、非目标整图常驻、compositor 输出未实际绑定、
> NodeSync/失效不完整和多 canvas 显示耦合。

## 1. Surface 角色绝对分离

### Canonical

每个 `KisPaintDevice`/frame 有独立 canonical surface：

- paint layer content；
- mask/selection canonical data；
- filter/clone等节点自身参数或源数据（按节点语义）。

canonical surface 由 PageStore 管理，不是 VkImage，也不由 canvas 拥有。

### Derived

```text
LowerCheckpointSurface
UpperOverlaySurface
UpperOperatorSurface
UpperReplayBundle
ProjectionSurface
DisplaySurface
LodPyramidSurface
UiOverlaySurface
```

derived surface：

- 带 dependency generation vector；
- 可丢弃重建；
- 不能覆盖/替代 canonical authority；
- 每页单独 publish；
- 不进入文档 undo（除非节点语义明确将其变成canonical结果）。

## 2. `GraphEpoch`

```text
GraphEpochId
DocumentId
LayerGraphVersion
ActiveTargetSet
NodeTopologySnapshot
PropertyGenerations
AnimationFrame/Time
SurfaceGenerationInputs
LowerSegments
TargetSegments
UpperSegments
DisplayPolicyVersion
```

epoch不可变。以下事件创建新epoch：

- target set变化；
- 节点添加/删除/重排；
- blend/opacity/visibility/property变化；
- mask/filter/group配置变化；
- animation frame/time语义变化；
- color/format转换改变图求值；
- 无法局部表达的外部CPU编辑。

旧epoch in-flight工作可以完成物理执行，但completion只有在epoch/generation匹配时才能publish。

## 3. LayerSegmentPlanner

### 单目标

```text
LowerReadOnlySegment
  -> LowerCheckpoint
WritableTarget
UpperReadOnlySegment
  -> Overlay / Operator / Replay
-> Projection/Display
```

### 多目标

```text
C0 -> T0 -> C1 -> T1 -> ... -> Tn -> Cn
```

- `T`只包含ActiveTargetSet声明的可写surface。
- `C`在epoch内不可写，可缓存/replay。
- Planner输出精确dependency和dirty propagation graph。
- 节点不支持GPU求值时，整个相关segment在CPU通过canonical lease求值，再发布derived generation；不能偷用陈旧projection。

## 4. Lower/Upper 语义

### LowerCheckpoint

- 表示目标输入之前所有下层的精确合成结果；
- target stroke期间保持稳定；
- viewport/halo页hot，其余可冷；
- dependency包含所有参与source/property generation。

### UpperOverlay

仅用于数学上backdrop-independent的结果。普通source-over可按定义缓存source/coverage，但仍需明确opacity、
premultiplication、mask和color semantics。

### UpperOperator

保存可应用到任意backdrop的参数化操作，不把结果错误拍平为透明RGBA。

### UpperReplay

backdrop-dependent blend、filter、mask、group保存prepared source/参数/dependency，在target改变的dirty region重放。

未知/未证明语义默认Replay或CPU route，不能默认Overlay。

## 5. Dependency Generation Vector

每个derived page记录：

```text
GraphEpochId
Output Surface/Page/Generation
Input Surface/Page/Generation[]
PropertyGeneration[]
Kernel/Codec/ColorTransform Version
ValidRegion
ProducerTicket
```

cache hit必须逐项匹配。只比较“节点最近修改时间”或全局dirty bool不足以证明有效。

## 6. Dirty propagation

canonical page publish事件：

```text
SurfaceId/PageId
Old/New Generation
GraphEpochId
WriterTicket
ChangedRegion
```

planner/scheduler：

1. 找到依赖该page/property的derived nodes；
2. 将region转换到各节点坐标/halo；
3. 只使相交derived page失效；
4. 保留仍匹配的Lower/Upper cache；
5. 请求source read lease/output write lease；
6. 提交CPU/GPU operation；
7. generation/epoch匹配后publish。

全画布重算只能由明确无法界定的节点/变换触发，不是普通stroke默认。

## 7. Projection

`KisImage::projection()` 语义对应一个derived ProjectionSurface/view，而不是向活动层sparse image上传CPU flattened pixels。

永久规则：

- projection从canonical node surfaces和graph epoch求值；
- active target仍是自己的canonical surface；
- projection不能alias writable target；
- Canvas不把CPU projection raw bytes覆盖target GPU replica；
- CPU projection consumer通过derived/canonical leases；
- GPU projection/composite由LayerSegmentPlanner产生exact output generation。

删除 `KisVulkanUpdateInfo` 中按64×64携带 raw projection pixel copy 的模型。

## 8. DisplaySurface

DisplaySurface是面向视图的derived输出：

```text
Document/GraphEpoch
Projection dependency generation
Display Color Transform/Filter generation
View LOD/scale policy
Page generations
Ready tickets
```

- Display descriptor必须绑定该DisplaySurface exact generation/view，不使用局部变量“选择composite image”后仍保留旧descriptor。
- 每页完整producer完成后publish。
- Presenter可复用上一完整snapshot。
- 多canvas可有不同DisplaySurface/view transform，但共享canonical/Projection cache。
- display失效/重建不改变canonical page。

## 9. Compositor Pipeline

输入：

- explicit source surface/page/generation；
- destination derived write lease；
- blend/node/property descriptor；
- dirty/halo rect；
- previous derived dependency（如需）。

输出：

- output generation；
- dependency vector；
- producer ticket；
- validity region。

禁止：

- 每dispatch临时descriptor无限分配；
- target未clear/未初始化；
- layout假定`UNDEFINED`；
- full-canvas image绕过PageStore预算；
- compositor输出没有更新display binding；
- active layer与projection共享image。

## 10. 温度与非目标剪枝

GraphEpoch提供语义事件给ResidencyController：

- active target/output: `CurrentWrite`；
- trajectory corridor: `PredictedWrite`；
- visible lower/display/upper exact dependency: `VisibleExact`；
- replay source/checkpoint: `ReplayOrCheckpoint`；
- transaction/undo/save retained: `UndoOrSaveRetention`；
- 被有效derived覆盖的canonical: `CoveredCold`；
- offscreen low-dependency: `OffscreenCold`；
- derived rebuildable: `DerivedDiscardable`。

`CoveredCold` 必须有包含 GraphEpoch、target、property/source generations 和 replay route 的
`CoverageCertificate`。温度策略按 safety、semantic class、cost/CLOCK history 分层，不维护脱离
generation/dependency 的独立 age 真相。完整算法见
[38_virtual_texture_residency_temperature.md](38_virtual_texture_residency_temperature.md)。

## 11. 多 Canvas

- 一个DocumentGpuSession维护GraphEpoch/Projection/共享derived cache。
- 每view attachment维护viewport、transform、DisplaySurface variant、swapchain generation。
- 一个view关闭不清理共享canonical/composite仍被其他view使用的page。
- 不同display filter/color profile形成不同DisplaySurface dependency generation。
- view不可见时可降低其display cache温度，不停止document stroke/undo/save。

## 12. UI Overlay

- outline、guide、selection、assistant不写Document ProjectionSurface。
- GPU primitive或UiOverlaySurface带独立generation/dirty region。
- selection canonical mask变化可以同时使document graph和UI outline依赖失效。
- 禁止每帧全窗口QImage生成/复制/上传。

## 13. 实现路线

### GD0：Graph snapshot/reference

- GraphEpoch/PropertyGeneration/ActiveTargetSet。
- CPU reference LayerSegmentPlanner和dependency tests。

### GD1：Derived surface core

- dependency vector、invalid/publish/rebuild。
- LowerCheckpoint/ProjectionSurface reference。

### GD2：GPU composite

- page-batched source/output leases。
- descriptor/view exact generation。
- output clear/layout/ticket。

### GD3：DisplaySurface

- color/display dependency、per-page publish。
- Presenter exact snapshot。

### GD4：Upper分类

- overlay/operator/replay golden tests。
- CPU fallback segment。

### GD5：多canvas/overlay

- shareddocument cache、per-view display。
- dirty UiOverlay，删除全窗口upload。

### GD6：旧projection path删除

- 删除raw `KisVulkanUpdateInfo`、active alias、full layer VkImage和NodeSync旧假设。

## 14. 验收门槛

- 每PaintDevice canonical surface独立，projection/display全为derived。
- active target不alias projection/display image。
- derived page持有完整dependency vector并拒绝stale completion。
- LowerCheckpoint与Upper分类像素正确。
- compositor output exact generation实际绑定到display descriptor。
- 普通stroke只局部重算必要page。
- CoveredCold非目标canonical可安全下沉。
- 多canvas共享document内容且独立display/WSI。
- UI overlay不再每帧全窗口上传。
- 旧raw projection upload/NodeSync整图路径从基线删除。
