# 虚拟纹理 PageStore 状态机、线性化与并发方案

> Canonical 身份与 Krita COW/undo 关系见
> [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md)。本文把其中的
> 不变量落实为可实现的记录布局、transition、锁顺序和 reference model。

## 1. 目标与非目标

本文解决：

- exact generation 读写；
- 单 writer、旧 generation 保留和 publish/cancel；
- 多域 materialization 去重；
- authority handoff；
- 多页 operation 的一致可见性；
- 完成乱序、取消、OOM、I/O 错误和 device loss；
- PageStore 元数据并发与物理对象退休。

PageStore 不负责 Vulkan queue submit、SSD 系统调用、压缩或温度打分。它只拥有逻辑状态并验证 provider 的完成事件。
除 read/write/publish/cancel 外，公共模型还必须提供 `beginTransaction(baseEpoch)`、`commit(preparedPages)`、
`abort(transaction)` 与 `captureCommittedEpoch()`；具体类型定义在 `kritaimage`，不暴露 backend 对象。

## 2. 身份和记录拆分

### 2.1 不可变身份

```text
PageKey       = SurfaceId + LogicalPageId
PageVersionId = PageKey + Generation
ReplicaId     = PageVersionId + ReplicaDomain + ProviderInstance + AllocationToken
OperationId   = SessionId + monotonic sequence
```

Generation 在同一 PageKey 内单调递增，不因物理迁移改变。默认/空白内容也有规范 generation，不要求立刻实例化记录。

### 2.2 Page head

每个已实例化 PageKey 保存紧凑 head：

```text
PublishedGenerationView          // 从 committed ImageEpoch root 解析；cache 必须带 ImageEpochId
PreparedVersionsByTransaction?
ReservedWriteGeneration?
WriterToken?
VersionChainHandle
SurfaceFormatId
MetadataRevision
PageFlags
```

`ResidencyPolicyHandle/SemanticClassSnapshot` 不是 correctness truth；策略状态引用 PageKey/ReplicaId，PageStore 只保存
安全所需 pin、lease 和 operation 状态。任何快照过期只影响策略质量，不能改变页面有效性。

### 2.3 PageVersion record

```text
PageVersionId
PublicationState = Unpublished | Prepared | Published | Historical | Retiring
ReplicaSet
ReadLeaseCount / readers by domain
PinReasons
InFlightOperationIds
TransactionRefs / UndoRefs / SaveRefs
DependencyVectorHandle   // derived only
ErrorSummary
```

### 2.4 Replica record

```text
ReplicaId
State = Allocating | Materializing | Valid | Retiring | Failed
Capabilities = CpuRead | CpuWrite | GpuRead | GpuWrite | Persistent
PhysicalHandle           // provider-private opaque token
ReadyTicket
LastUseTicket
BytesCharged
ValidationStamp
```

PageStore 不保存裸 CPU pointer、`VkBuffer`、`VkDeviceAddress` 或文件描述符；这些只在 resolved lease/provider 内短期存在。

## 3. 状态不变量

1. 每个 PageKey 只有一个 published head。
2. 每个 PageKey 同时最多一个 reserved writer。
3. Unpublished generation 只对其 writer 可见；Prepared generation 只对所属 transaction/显式 progressive view 可见。
4. 普通 document read 默认解析调用时捕获的 committed ImageEpoch，不逐页追随 prepared/之后的新 head。
5. 任一 Valid replica 必须精确匹配 PageVersion/format/validation stamp。
6. `Materializing` 不能被 consumer 当作 Valid；consumer 只能等待其 ReadyTicket。
7. canonical PublishedGeneration 必须至少有一个 authority/recoverability 路径。
8. derived generation 可以没有 durable authority，但必须有完整 dependency vector 和 rebuild route。
9. operation completion 必须同时匹配 OperationId、PageVersion、ReplicaId 和 provider epoch。
10. Retiring replica 在 LastUseTicket 完成前保持 allocation 和 mapping。
11. Failed/Cancelled operation 不能改变 published head。
12. PageStore lock 内禁止等待 GPU、I/O、condition variable 或其他 subsystem future。

## 4. 分片所有权

### 4.1 Shard

```text
shard = stableHash(PageKey) % ShardCount
```

每个 shard 包含：

- page head map；
- PageVersion/Replica metadata；
- in-flight materialization dedup map；
- 短临界区 mutex 或等价 owner；
- completion event queue；
- 可增量扫描的 residency candidate hooks。

ShardCount 是内部策略参数。PageKey 到 shard 的映射在 session 生命周期内稳定。

### 4.2 锁顺序

单页 transition 只持一个 shard lock。多页逻辑 operation 采用：

1. 对 PageKey 排序并计算唯一 shard 序列；
2. 在短临界区内依次预留 logical intent；
3. 任何冲突都释放已预留 intent 并返回 dependency/retry token；
4. 不持多 shard 锁执行物理工作；
5. 最终可见性通过 transaction manifest 提交，而不是长时间锁住所有页。

禁止持有 PageStore shard lock 再取得 image/node/UI/provider allocator lock。provider completion 先生成事件，再由
PageStore owner 应用 transition。

## 5. Request 与 lease 算法

### 5.1 Read request

`acquireRead()` 在线性化点捕获：

```text
PageVersionId
ReadView = CommittedImageEpoch | TransactionOverlay | ExactGeneration
required AccessDomain/capability
deadline/priority
request token
```

处理：

1. 先从 ReadView 冻结的 manifest/selector 解析 exact generation；不得在 materialization 期间追随 head。
2. 若 exact generation 已有合适 Valid replica，增加逻辑 reservation 并返回 ready request。
3. 若存在相同 `(PageVersion, target domain, access mode)` 的 Materializing operation，附着其 ticket。
4. 否则预留 target replica intent，生成 materialization operation，锁外执行。
5. `resolve()` 再次验证 request token、generation 和 completion result，随后增加 read lease。
6. lease release 记录 consumer last-use ticket；只有 CPU 同步消费者可在完成访问后直接 release。

不得在 `resolve()` 时静默改为更新 generation；需要新内容的调用者必须重新 request。

### 5.2 Write request

`acquireWrite()`：

1. 验证没有现存 writer；
2. 从调用者的 WriteView 捕获 exact base：同一 transaction chain 的最新 Prepared generation 优先，否则使用
   committed ImageEpoch 的 PublishedGeneration；
3. 分配严格更大的 WriteGeneration；
4. 创建不可伪造 WriterToken；
5. 增加 base generation 的 before-image/transaction retention；
6. 预留 target replica intent；
7. 返回 base materialization、target allocation 和 previous-writer dependencies。

`resolve()` 只在 target replica 可写且 base 内容已按 WriteMode 准备后产生 WriteLease。

### 5.3 Publish

publish 不是立即写 metadata：

```text
publish(writeLease, producerTicket)
-> register PublishPending operation
-> producer completes
-> completion validates writer token/generation/provider epoch
-> mark output replica Valid
-> mark page generation Prepared in its TransactionId
-> release writer reservation
-> emit PagePrepared event
-> transaction commit atomically publishes a new ImageEpoch manifest
```

单页独立 operation 可以使用只含一页的 implicit transaction。迟到、重复或错误 generation 的 completion 只终结对应
operation，不得修改 committed image epoch。

### 5.4 Cancel

- producer 尚未提交：取消 allocation/materialization，释放 writer reservation。
- producer 已提交但未完成：标记 CancelRequested，等待 completion 后丢弃输出或交给恢复事务。
- transaction 已 commit：不能用 `cancel(WriteLease)` 回滚；必须执行显式 undo/restore transaction。

## 6. 多页 transaction 和 image epoch

逐页 generation publish 与用户可见的 stroke/save 一致性是两个层次。
本节 `TransactionId` 指 PageStore 的多页可见性事务，可以对应一个 page batch；它不等同于 Krita undo stack 中的
整笔 `StrokeTransactionId`。后者可以按顺序引用多个已提交 ImageEpoch。

### 6.1 Transaction manifest

```text
TransactionId
BaseImageEpoch
PageKey -> BeforeGeneration
PageKey -> AfterGeneration
RequiredPreparedTickets
State = Open | Prepared | Committed | Aborted
```

Committed document view 使用不可变 root：

```text
ImageEpochRoot
  ImageEpochId
  PreviousEpochId
  SurfaceId -> immutable SurfacePageMapRoot
  graph/default/extent/property revisions
  commit sequence

DocumentImageEpochHead -> ImageEpochRoot
```

实现采用 copy-on-write persistent map/radix tree 或等价不可变映射：transaction 只复制发生变化的路径，把
`PageKey -> AfterGeneration` 写入新 root。每个 document 有一个只负责短时间排序 commit sequence 的 commit
sequencer；线性化点是 `DocumentImageEpochHead` 从旧 root 原子切换到新 root。它不持 shard lock等待 producer，也不
执行 materialization。

Page record 中可缓存 `(ImageEpochId, PublishedGeneration)`，但它不是可见性线性化点；tag 不是当前 root 时必须忽略并
按 root 懒刷新。普通 reader 先捕获 ImageEpochRoot，再从该 root 解析 generation，不能逐页读取正在变化的 head
cache。多目标跨 Surface operation 也通过同一个 document root switch 提交。

- 单页可以在 GPU 完成后进入 Prepared generation，但不能进入普通 document view；
- 同一 page-batch/StrokeBatch 所需页面全部 Prepared 后，构造新的 immutable ImageEpoch manifest并原子切换；
- display/composite 可消费最后 committed batch epoch；若使用 TransactionOverlay 预览，必须明确标记为可丢弃预览，不能
  被 save/undo/canonical reader 观察；
- undo/save 的 committed image view 只通过原子 manifest/head 发布看到完整集合；
- abort 保留/重新发布 BeforeGeneration，不让半笔内容进入 committed image epoch。

stroke 可以按多个已完成 batch 连续发布多个 ImageEpoch；stroke transaction 在 undo 层把这些 batch epoch 组成一个用户
操作。任何单次 epoch switch 都不能包含半个 batch。

两个基于同一 BaseImageEpoch 的并发 commit 若修改重叠 PageKey，后到者必须按 scheduler/transaction order rebase 或
返回 conflict；不得用最后写入 map entry 的偶然顺序静默覆盖。修改不相交 PageKey 时也必须生成有序的新 root，确保
save/undo 可重放。

### 6.2 Immutable save epoch

保存捕获：

```text
ImageEpochId
Surface graph revision
PageKey -> exact PublishedGeneration
metadata/default/extent revisions
```

之后的新写生成新 generation。serializer 只申请 snapshot 中的 exact generation read lease。

## 7. Materialization 去重与来源选择

Dedup key：

```text
(PageVersionId, TargetDomain, RequiredCapability, ProviderEpoch)
```

多个 consumer 共享 producer ticket，但各自得到独立 lease。来源选择由策略提供候选和 ETA，PageStore 验证：

- source 必须 Valid 且 generation 精确匹配；
- source lease/pin 覆盖整个 transfer；
- target allocation 不得与仍被引用的旧 replica alias；
- conversion 只有在 SurfaceFormat 明确允许且仍产生同一 canonical bytes 时才算 replica；否则是 derived surface。

失败会清除 dedup entry 并唤醒所有附着 request，以显式 Failed 或重新选择其他 source 结束，不能返回 default page。

## 8. Authority 与 recoverability

`AuthorityReplica` 是责任位置，不意味着只有一份数据。handoff：

```text
Valid source G + source pin
-> target Materializing G
-> target completion/validation
-> add target to ValidReplicas
-> commit authority/recoverability policy
-> release source pin
-> optional retire source
```

以下情形禁止 handoff：

- target 仅有 allocation，没有完成 ticket；
- checksum/format/provider epoch 不匹配；
- target durability 不满足调用者要求；
- source 是唯一 recoverable before-image 且 transaction 尚未提交；
- device loss 后仍引用失效 VRAM handle。

## 9. 内存回收

PageStore 只发布 `RetireIntent`，provider 根据 LastUseTicket 延迟物理回收：

```text
remove replica from new lease selection
-> mark Retiring
-> wait existing lease releases
-> wait LastUseTicket
-> provider unpublish mapping/free slot
-> provider completion
-> erase Replica record
```

ABA 防护使用 `AllocationToken = slot index + allocation generation`。slot 重新使用后，旧 completion 和旧 PageHandle
必须因 generation 不匹配而失败。

## 10. Reference model

BR1 必须先实现无 GPU 的确定性 reference state machine：

- fake RAM/UMA/VRAM/SSD domain；
- 手动推进 completion；
- 任意重排 operation 完成顺序；
- 可注入 allocate/copy/validate/index/retire 失败；
- 每一步检查不变量；
- 输出可缩减、可重放 seed。

状态空间事件至少包含：

```text
AcquireRead / ResolveRead / ReleaseRead
AcquireWrite / ResolveWrite / Publish / Cancel
BeginMaterialize / CompleteMaterialize / FailMaterialize
BeginHandoff / CommitHandoff
BeginRetire / CompleteRetire
CommitTransaction / AbortTransaction
CaptureSaveEpoch / ReleaseSnapshot
Undo / Redo / DeviceLost / CloseSession
```

production provider 必须复用同一 transition 函数，不能另写“更快”的宽松状态机。

## 11. 可观测性

每个 transition 记录：

```text
timestamp
DocumentSessionId / SurfaceId / PageId / Generation
OperationId / TransactionId
old state -> new state
source/target domain
ticket/value
reason/deadline
bytes charged/freed
error code
```

强制计数：materialization dedup hit、stale completion rejection、writer conflict、lease wait duration、authority handoff
失败、retirement lag、metadata bytes/page、default sentinel hit。

## 12. 实施顺序

### PS-SM0：类型与 reference transition

- 定义 ID/token/state/event；
- 建立单线程模型和 exhaustive/random tests；
- 固化所有不变量。

### PS-SM1：分片 metadata

- shard map、锁顺序、completion queue；
- materialization dedup；
- 无 I/O 的 fake provider 压力测试。

### PS-SM2：Krita COW/memento

- PageVersion retention；
- transaction manifest；
- iterator oldData、undo/redo/save epoch。

### PS-SM3：Provider bridge

- backend-neutral ticket；
- provider epoch/device loss；
- last-use retirement。

### PS-SM4：Cutover

- 所有 PaintDevice access 通过 facade；
- 删除第二套 GPU authority/dirty/tier；
- reference 与 production trace 差分测试。

## 13. 完成门槛

- 任意完成乱序、取消和 OOM 下不变量成立；
- 相同 materialization 只有一个物理 producer；
- shard lock 内没有 wait/I/O/queue 调用；
- stale completion 和 ABA handle 被稳定拒绝；
- 多页 undo/save 不看到未提交 transaction 的混合 generation；
- default、extent、COW、clone、animation frame 与现有 CPU 测试一致；
- PageStore metadata 不包含 Vulkan/SSD 私有对象；
- production 和 reference 使用同一 transition 语义。
