# Undo、保存、取消与失败恢复

> 本文定义 stroke 从 Accepted 到 Recoverable 的业务闭环，以及 Krita transaction、保存、取消和设备失败
> 如何在没有 stroke-end 全量回读的前提下工作。现有 `KisMementoManager`/oldData 的 COW 语义必须演进为
> canonical generation reference；不得平行新增一套 GPU undo。PageStore 权威设计见
> [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md)。

## 1. 完成层次

一个 stroke 不是单一“完成/未完成”状态：

1. **Accepted**：所有 resolved command 已进入不可变 journal。
2. **Submitted**：相关 PageJob 已提交并有 execution ticket。
3. **Executed**：target pending generation 的写入已完成。
4. **Visible**：依赖该 target 的 DisplaySurface generation 已完成。
5. **Recoverable**：新结果有安全 backing，或 base/before-image + journal 足以确定性重建。
6. **TransactionPublished**：Krita undo adapter 中存在可执行的 undo/redo command。
7. **DurableDocument**：用户保存的文件已经持久化相应 snapshot；这不是普通 stroke commit 的必要条件。

UI 可以在 Visible 后显示；undo transaction 只能在 Recoverable 后发布。不能因画面已经显示就提前释放 journal
或 before-image。

## 2. First-write Snapshot

### 2.1 页面级 COW

一次 stroke 第一次写某 canonical target page 前：

- 捕获 `baseGeneration`；
- 创建 before-image snapshot handle；
- snapshot 完成 ticket 成为 PageJob 前置依赖；
- 同一 stroke 后续写该页复用同一 before-image；
- snapshot 与 target pending generation 分开管理。

### 2.2 后端

UMA：

- 在 shared arena/冷 backing 创建 snapshot page；
- 可以 GPU/CPU copy，但必须在 writer 前完成；
- 压力下 snapshot 可异步下沉 SSD。

dGPU：

- 可 VRAM-to-VRAM copy、VRAM-to-RAM download 或利用已存在 RAM base generation；
- backend 选择最低代价方案；
- snapshot 安全前不能覆盖唯一 base generation。

### 2.3 Snapshot set

transaction 记录：

```text
StrokeId
TargetSurfaceId
EvaluationEpoch
PageId -> BeforeGeneration/SnapshotHandle
PageId -> AfterGeneration
SnapshotReadyTicket
RecoverabilityTicket
```

只记录 canonical target pages。DisplaySurface、checkpoint、overlay 等 derived page 不进入文档 undo。

## 3. Stroke end 与 transaction 发布

### 3.1 `endStroke()`

- append End marker；
- seal 最后 chunk；
- 返回 `StrokeCommitHandle`；
- 不等待 GPU；
- 不暂停 render/presenter；
- 不下载 dirty pixels；
- 不直接调用 `KisTransaction::commit()` 假装完成。

### 3.2 `StrokeCommitHandle`

```text
StrokeId
acceptedSequenceRange
executionTicketSet
visibleTicketSet
recoverabilityTicket
transactionState
failure/cancel state
```

### 3.3 异步 transaction job

后台 `KisStrokeStrategy`/transaction bridge 采用 continuation：

1. 等待 recoverability ticket，而不是全局 GPU idle。
2. 校验 target identity、after generations 和 snapshot set。
3. 构造 PageStore-aware memento/undo command。
4. 发布到 post-execution undo adapter。
5. 更新 journal/snapshot retention。

依赖未完成时 job 保存 continuation state 并让出 worker，ticket ready 后重新排队；不允许占住 Krita worker
同步等待。UI 和新 stroke admission 不等待。

尚未达到 Recoverable 的 stroke 进入 `PendingTransactionRegistry`。它保持 Krita stroke scheduler 中的逻辑顺序，
并参与 undo/save barrier；不能因为 undo command 尚未进入公开 undo stack，就让用户的下一次 undo 越过它。

## 4. 新笔迹与未完成旧笔迹

允许新 stroke 在旧 transaction 尚未发布时开始，但必须满足：

- 同一 page 的新 writer 等待旧 `LastWriterTicket`；
- 新 stroke before-image 捕获的是它开始时逻辑基准 generation；
- undo publication 顺序与 Krita stroke order 一致；
- transaction bridge 不能让后一个 stroke 先成为 undo stack 中较早项；
- 若旧 stroke 失败，所有依赖其 generation 的新 operation 进入恢复/失败传播。

不同 target/page 可以并行执行，但用户可观察的 transaction 顺序仍由 stroke scheduler 保证。

## 5. Undo

### 5.1 正常 Undo

undo operation：

1. 捕获当前 after generation，验证没有不允许的外部覆盖。
2. 为目标 page 预留新的 restore generation。
3. 等待目标 page last-writer。
4. 从 before-image snapshot 恢复。
5. 发布 restored generation。
6. 发送 dirty/composite event。

undo 自身也是 page operation/ticket，不是 CPU `writeBytes()` 循环。

### 5.2 Undo-before-complete

用户可能在 GPU stroke 尚未完成时撤销：

- undo 调度先检查最新 `PendingTransactionRegistry` 项，再检查已发布 undo stack；
- 对未提交 batch 请求取消；
- 已提交 batch 不能假定 queue 可撤回；
- restore operation 等待所有可能 writer ticket；
- writer completion 先发布或被标记 superseded；
- restore generation 最后发布并成为新 last writer；
- DisplaySurface 只显示完整 generation，不短暂重新出现已撤销结果。

### 5.3 Redo

redo 可以：

- 恢复保存的 after-image snapshot；或
- 在 semantic/resource version 匹配时重放 journal。

选择由 snapshot/replay 成本策略决定，但 undo command 必须保证至少一种路径在其生命周期内可用。不能在释放
journal 后仍假设可以 redo replay。

## 6. Cancel

### 6.1 未提交

- 标记 open/sealed chunk Cancelled；
- 释放未使用 lease/resource pin；
- 若尚未产生页面写入，不需要 restore。

### 6.2 已提交/已执行

- 等待或依赖所有相关 writer ticket；
- 使用 before-image 恢复受影响 page；
- 取消 pending composite，或让其结果因 generation mismatch 不发布；
- 生成新的 DisplaySurface restore generation；
- 只有 restore 完成后 cancel handle 才完成。

### 6.3 不能做的事

- 清空 ring 并认为取消完成；
- 删除 transaction 对象但保留 GPU 修改；
- 把 dirty 标志清除；
- 复用 in-flight page allocation；
- 让新 stroke 在不知道旧 writer 结果时直接覆盖。

## 7. 保存

### 7.1 Snapshot isolation

保存请求作为 image/stroke scheduler 中的有序 operation，先依赖逻辑上位于它之前的 accepted stroke commit，
再捕获：

```text
Document/EvaluationEpoch
Node/Frame topology revision
Canonical SurfaceId set
每页 requested generation map
metadata/default pixel/colorspace
```

后续笔迹创建新 generation，不改变已捕获保存快照。

这保证“用户松笔后立即保存”包含该笔，即使像素仍在 GPU 执行；等待发生在保存 worker 对精确 commit/read ticket
的依赖上，而不是 UI 或全局 device idle。

### 7.2 页面读取

- serializer 在后台逐区域申请 exact-generation CPU read lease。
- UMA 等待对应 writer 后 invalidate 并直接读共享页。
- dGPU 对所需 generation 批量 download；若 RAM/SSD 已有该 generation 则直接读。
- 可以流式写文件，不需要先把全画布复制到一块 CPU buffer。
- 页面读取失败使保存明确失败，不能写透明替代数据。

### 7.3 保存与临时 SSD

- 由 `KisTileDataStore`/`KisSwappedDataStore` 演进的 unified SSD segment 不是文档格式；Vulkan 不另建 page pack。
- serializer 可以从 PageStore/SSD record 读取验证过 generation，但仍按 Krita 文件格式编码。
- 保存成功不自动删除运行时 snapshot/journal；它们由 undo/recovery retention 决定。

## 8. Recoverability

### 8.1 定义

generation `G` 可恢复，当且仅当至少一个条件成立：

- G 已存在验证过的 UMA/RAM/SSD replica，并由 PageStore ledger 记录；
- 有安全 base/before generation，加完整、版本匹配的 journal/resource 可以确定性重放到 G；
- 有验证过的 after-image snapshot。

仅存在于 dGPU VRAM 且无重放材料的 G 不可标记 Recoverable。

### 8.2 Journal retirement

只有满足全部条件才能退休相关 journal：

- after generation 有其他安全恢复来源；
- undo/redo 不再需要 replay，或已有 snapshot；
- 没有 device recovery 引用；
- 所有 batch completion 已发布/失败终结；
- resource semantic generation 可以释放。

## 9. 设备丢失

### 9.1 状态冻结

- 停止新 GPU submission；
- 标记所有未 signal GPU ticket 为 indeterminate/failed；
- 禁止其迟到 callback 发布 page generation；
- 保留 journal、before-image、RAM/SSD backing 和 transaction order；
- Presenter 独立失效。

### 9.2 页面分类

对每个受影响 page：

1. `Committed+Recoverable`：直接从安全 backing 恢复。
2. `Pending with base+journal`：回退 base，再重放 accepted sequence。
3. `Pending with after snapshot`：恢复 after snapshot。
4. `VRAM-only unrecoverable`：transaction 失败，必须显式报告，不能伪造 clean page。

成熟 capability gate 不允许第 4 类出现在用户已接受的 stroke 中。

### 9.3 重建

- 可选择 CPU reference executor 立即恢复，或新 Vulkan device 重放。
- 重放使用 journal 中冻结的 semantic/resource version。
- 恢复 generation 与旧 GPU physical handle 无关。
- 恢复后重新生成 derived composite/display，不保存旧 derived cache。

## 10. 其他失败

### 10.1 SSD 写失败

- RAM/VRAM 最后权威 generation 保留；
- page 不得被回收；
- ResidencyController 施加 backpressure；
- recoverability 不前进到 SSD-valid。

### 10.2 Download/upload 失败

- 目标 copy 不标 valid；
- source authoritative allocation 保留；
- 依赖 batch Failed 或重试；
- 超时不清 dirty。

### 10.3 Brush resource 失败

- begin 前失败：整笔选择 CPU/reject。
- epoch 中 pinned resource 失效属于 backend fault，停止后续 batch并走 restore；
- 不切换到新 resource generation 继续旧 stroke。

### 10.4 Graph/target identity 变化

- 关闭或取消旧 epoch；
- 已提交 writer 依据旧 target identity 完成/恢复；
- 新 evaluation epoch 不能复用旧 pending generation；
- stale completion 被 identity/generation check 拒绝。

## 11. 应用关闭与文档关闭

- 禁止新 stroke/session；
- 等待或取消业务 transaction，而不是直接 device idle 丢弃状态；
- 确保用户要求保存的 document snapshot 已完成；
- 未提交笔迹按产品策略完成或取消恢复；
- journal/snapshot 在不再需要恢复后释放；
- 最后再销毁 GPU device/backend。

## 12. 实现路线

### UR0：Snapshot/reference transaction

- Page snapshot handle/generation set。
- 将现有 `KisMementoManager` COW/oldData 映射到 PageStore generation rollback/rollforward。
- first-write once-per-page 测试。

### UR1：Commit states

- Accepted/Executed/Visible/Recoverable/Published 状态机。
- `StrokeCommitHandle` 和异步 transaction bridge。

### UR2：GPU snapshot/restore

- UMA shared copy。
- dGPU VRAM/RAM snapshot policy。
- undo-before-complete dependency。

### UR3：Save snapshot

- generation map capture。
- background read lease/stream serialization。
- save 与新 stroke 并发测试。

### UR4：Cancel/Redo

- 未提交取消、已执行恢复。
- after snapshot/journal redo policy。

### UR5：Fault recovery

- SSD/transfer/resource failure injection。
- device-loss ledger、CPU/GPU replay。
- unrecoverable state 显式报告。

## 13. 验收门槛

- stroke end 无 host GPU wait 和像素回读。
- transaction 只在 Recoverable 后发布。
- 同页新 stroke 通过 last-writer 排序，undo stack 顺序稳定。
- undo-before-complete、cancel-after-submit 和 redo 输出正确。
- 保存得到捕获 generation，而不是混入后续笔迹。
- UMA 保存/undo 不经过画布 staging copy。
- dGPU VRAM-only pending generation 始终有 journal/before-image 恢复路径。
- SSD/transfer/resource 失败不清 dirty、不释放最后权威 backing。
- device lost 后支持的 brush 可以确定性恢复；不能恢复时明确失败而非静默丢像素。
