# 虚拟纹理 PageStore 状态机、线性化与并发方案

> 2026-11-04 新版后端扩展设计：[105完整规范](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/UNIFIED_BACKEND_DESIGN.md)。第6.1节逐页persistent-map实现选择在新版候选中由持久Surface目录+epoch区间映射替代；immutable root、exact读和跨Surface原子可见不变。该算法仍须反例与实现验收。 当前只完成设计，CPU产品0fd96保持；不据此声称GPU/完整能力已实装。旧实现名称不能覆盖105的目标责任，未迁消费者在原矩阵追踪。

> Canonical 身份与 Krita COW/undo 关系见
> [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md)。本文把其中的
> 不变量落实为可实现的记录布局、transition、锁顺序和 reference model。
>
> 2026-09-20 状态：PS-SM0–PS-SM4 的功能/正确性证据见
> [51_br1_canonical_pagestore_closure_20260919.md](archive/br1_pre_m6_20260925/documents/51_br1_canonical_pagestore_closure_20260919.md)；resident CPU
> 快路径、virtual default 和 persistent epoch 生产布局仍在 **BR1-PERF**，见
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)。写侧 first-write
> 选择、backing handoff 与硬预算以 [68](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 为准。异步 Vulkan
> submission 与跨域 replica 分别留在 BR2/BR3，不能用于绕过这项 CPU 出口。

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
`abort(transaction)`、`captureCommittedEpoch()`、`captureRetainedEpoch()` 与 `releaseSnapshot(token)`；具体类型定义在
`kritaimage`，不暴露 backend 对象。graph/planner 消费 retained snapshot 前还必须调用 owner 的
`validateRetainedEpoch()`；`abort()` 返回成功/失败，active writer 和未独立保留的 Prepared read/last-use 阻止 abort；
captured sealed version 可在 abort 后转为独立保留的 Historical，不能撤销仍活跃的读 capability，见 5.4。
只需要查询可见 identity 的 cache/index adapter 使用 `resolvePageVersion(PageKey, ReadView)`；该接口必须覆盖
transaction prepared write 与 staged removal，但不得 materialize page 或授予访问 capability。
正常 current-base mutation 使用 `beginCurrentTransaction()`：同一 owner gate 内捕获当前 immutable root 并建立 transaction
retention，不导出 owning manifest，也不分成先返回裸 epoch、稍后建立 retention 的两次公开调用。显式历史 base 仍用
`beginTransaction(baseEpoch)`；D2-A 已接入匿名 tiles3 起点，尚不代表免全局锁或完整 production epoch owner 已完成（55）。

BR1 基线采用单页 acquire/resolve 原语：`acquireRead(PageKey, ReadView, AccessRequirement, ...)` 与
`acquireWrite(PageTransaction, PageKey, AccessRequirement, ...)`。区域 facade 可以批量组织 request，但不得制造跨多个
generation 的单一 lease。`AccessRequirement` 显式拆分 domain 与 CPU pointer/GPU binding capability；多页一致性只由
共同捕获的 ImageEpoch/transaction manifest 提供。

## 2. 身份和记录拆分

### 2.1 不可变身份

```text
PageKey       = SurfaceId + LogicalPageId
PageVersionId = PageKey + Generation + DefaultPixelRevision
ReplicaId     = PageVersionId + ReplicaDomain + ProviderId + ProviderEpoch
                + AllocationToken(slot + allocation generation)
OperationId   = SessionId + monotonic sequence
CompletionId  = RegistryId + Domain + SourceId + Value
```

新写的 Generation 分配高水位在同一 PageKey 内单调且不复用，不因物理迁移或删除/重建而重置。
undo/redo 的新 ImageEpoch 可重新选择被 retention 保护的旧 exact generation，published head 的数值不要求逐次增大。
默认/空白内容还绑定精确 DefaultPixelRevision，不要求立刻实例化记录；不同 revision 不能互换。

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
CapturedReadViewTokens // sealed private version retention, independent of physical pins
DependencyVectorHandle   // derived only
ErrorSummary
```

`Published/Historical` 的 virtual default 可以具有空 ReplicaSet 和空物理 authority，但必须能通过捕获/保留的 surface
format/default revision/descriptor 恢复 exact bytes；不能用这个分支表示普通 non-default 丢失、Unpublished/Prepared
像素或未完成 producer。D1 的 `MaterializeDefault` 只为已有 virtual default 附加匹配的 valid backing，保留 version 和
publication，不创建新写 generation；必须拒绝错误版本、重复物化与跨版本物理槽别名。

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

PageStore canonical metadata 不保存裸 CPU pointer、`VkBuffer`、`VkDeviceAddress` 或文件描述符。CPU span 只在有寿命
保护的 resolved lease/native guard/provider 内使用，backend 私有句柄留在 provider 内，不进入公共 metadata ABI。
native guard 虽不进入 generic lease map，仍须遵守相同的 reader/writer、abort/close、pin/retire 不变量；空 map 不是无消费者证明。
每个 replica 另带 provider 返回的 `ReplicaLayout(layoutRevision, formatId, extent, validRect, rowStride, byteSize)`；它必须
匹配 PageStore 保存的完整 allocation descriptor，不能只比较 generation 或 pixel size。

### 2.5 生产布局与 reference 布局

以上是逻辑记录，不要求生产实现为每个 default page、request 或 lease 分配独立 QObject/heap node。生产布局必须按访问
频率拆分：

- surface-level default sentinel 和 immutable root 不随空白坐标数量增长；
- page head/current-version cache 使用紧凑结构，resident CPU guard 保存直接 opaque token；
- request/operation maps 只保存真正异步、跨域或待完成的 capability；
- historical/version/replica 冷记录可单独分配，不放大 current resident access 的 cache footprint；
- `KisImageEpochReferenceModel` 使用的 `QHash`、owning `QVector`、全量排序仅是 oracle 表示，不是 production ABI。

production epoch root 必须采用 persistent radix tree/HAMT/B-tree 或复杂度等价的结构共享映射。commit K 个 changed pages
进入 N-page manifest 的时间和新增内存目标为 `O(K log N)`；ordinary lookup 为 `O(log N)` 或 bounded radix depth。
全量 export/sort 只允许显式 serialization/debug cold path。

## 3. 状态不变量

1. 每个 PageKey 只有一个 published head。
2. 每个 PageKey 同时最多一个 reserved writer。
3. Unpublished generation 只对其 writer 可见；Prepared generation 只对所属 transaction/显式 progressive view 可见。
   Prepared 归属按版本隔离，不同事务可持有同页独立 sealed 版本；不等于多个活动 writer，最终 root 仍须复验 base/head 冲突。
4. 普通 document read 默认解析调用时捕获的 committed ImageEpoch，不逐页追随 prepared/之后的新 head。
5. 任一 Valid replica 必须精确匹配 PageVersion/format/validation stamp。
6. `Materializing` 不能被 consumer 当作 Valid；consumer 只能等待其 ReadyTicket。
7. canonical PublishedGeneration 必须至少有一个 authority/recoverability 路径；virtual default 使用上述精确内容描述，
   其余像素版本不得仅凭“无 replica”当作可恢复。
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

`acquireRead(PageKey, ReadView, ...)` 在线性化点捕获：

```text
PageVersionId
ReadView = CurrentCommittedEpoch | RetainedCommittedEpoch | TransactionOverlay | RetainedExactVersion
required AccessDomain/capability
deadline/priority
request token
```

处理：

1. 先从 ReadView 冻结的 manifest/selector 解析 exact generation；不得在 materialization 期间追随 head。
2. 若 exact generation 已有合适 Valid replica，增加逻辑 reservation 并返回 ready request。
3. 若存在相同 `(PageVersion, target domain, access mode)` 的 Materializing operation，附着其 ticket。
4. 否则预留 target replica intent，生成 materialization operation，锁外执行。
5. `resolve()` 再次验证 request token、generation 和 completion result，把 acquire 时已有的 reservation 转成 provider
   access；不能在此时才第一次 pin replica。
6. lease release 记录 consumer last-use ticket；只有 CPU 同步消费者可在完成访问后直接 release。
7. 放弃未 resolve request 时显式 `cancel(request)`，释放同一 reservation；重复/伪造 cancel 不改变状态。

不得在 `resolve()` 时静默改为更新 generation；需要新内容的调用者必须重新 request。

### 5.2 Write request

`acquireWrite(PageTransaction, PageKey, ...)`：

1. 验证没有现存 writer；
2. 从调用者的 WriteView 捕获 exact base：同一 transaction chain 的最新 Prepared generation 优先，否则使用
   committed ImageEpoch 的 PublishedGeneration；
3. 分配严格更大的 WriteGeneration；
4. 创建不可伪造 WriterToken；
5. 增加 base generation 的 before-image/transaction retention；
6. 预留 target replica intent；
7. 返回 base materialization、target allocation 和 previous-writer dependencies。

`PreserveContents` 的 base→write 初始化不是同 generation replica materialization。provider transfer kind 必须显式区分
`ExactVersionMaterialization` 与 `WriteGenerationInitialization`；前者要求 PageVersion 完全相同，后者要求 PageKey
相同且 target generation 严格更大。

request id、writer token、lease id、operation id 均由 PageStore 单调分配。provider 接口接收 PageStore 分配的
operation id，并回显同一 identity；provider id/epoch 由注册实例暴露。provider 重建、device loss 或 slot 复用后，
旧 epoch/allocation generation 的 completion 必须失败。

`resolve()` 只在 target replica 可写且 base 内容已按 WriteMode 准备后产生 WriteLease。

native virtual-default 首写允许无物理源的 writer：base 必须是当前事务可见的 exact virtual default，
default revision 匹配，source 为空且目标采用 discard/default 初始化。保留的是逻辑 before-image，
不是虚构的 source replica/pin。普通版本没有合法 source 仍然拒绝；`PreserveContents` 不能凭空 source
通过。Publish/Fail/Cancel 对虚拟源不递减不存在的物理 pin，但仍复验 base、writer、transaction 和 target。
期间允许独立 reader 物化同一 immutable default；是否属于逻辑 before-image 由取得授权时的 exact default、空 source 和 discard 模式决定，
不能在完成时仅凭 `isVirtualDefault()`（副本是否仍为空）重新推断，也不能消耗后来 reader 的 pin。
这与通用路径遵守同一状态机，不是跳过 authority 检查的快捷入口；实际代码及测试进度见
[67](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md)。

### 5.3 Publish

publish 不是立即写 metadata：

```text
publish(writeLease, producerTicket)
-> BeginPublish: register Publishing operation
-> producer completes
-> completion validates writer token/generation/provider epoch
-> mark output replica Valid
-> mark page generation Prepared in its TransactionId
-> release writer reservation
-> emit PagePrepared event
-> transaction commit atomically publishes a new ImageEpoch manifest
```

单页独立 operation 也使用只含一页的 core transaction；facade 可提供 convenience，但不得绕过 transaction identity。
producer 失败通过 `FailWrite` 释放 before-image pin 并丢弃 WriteGeneration。迟到、重复或错误 generation 的
completion 只终结对应 operation，不得修改 committed image epoch。

### 5.4 Cancel

- producer 尚未提交：取消 allocation/materialization，释放 writer reservation。
- producer 已提交但未完成：从 `Publishing` 标记为 `CancelPending`，等待 `PublishWrite`/`FailWrite` completion
  后释放 pin 并丢弃输出；不得提前复用 allocation。
- transaction 已 commit：不能用 `cancel(WriteLease)` 回滚；必须执行显式 undo/restore transaction。
- transaction abort 遇到 active writer/写 segment 或未独立保留的 Prepared generation 的 active/pending-last-use read lease 时返回失败；
  持有者先 release/cancel 后继续。未 resolve 的普通 request 可以由 abort 安全取消。
- captured overlay 的 sealed Prepared 持有独立逻辑 token；abort/删除把它转为 Historical 并清除 preparedBy，不释放其仍在用的 replica。
  supersede、历史丢弃及 fused idle retirement 必须拒绝仍有 captured token 的目标。释放 token 不等于释放 CPU pin 或完成 GPU/I/O last-use。
  capture/release token 也推进 metadata revision；锁外 commit 候选不能覆盖晚到捕获/释放，详见 [67 §10](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#10-2026-09-21冻结-sealed-overlay-与生产-packed-读取)。

D11 新增 owner 内部 `AbortPreparedVersion`：仅用于尚未暴露给 overlay 的 native seal 批次失败，按 exact version +
transaction 撤销本段已经 Prepared 的版本，保留同 history transaction 的较早 prepared/proof；generation 高水位不回退。
拒绝 active writer、read lease、pin、pending last-use/operation；metadata 回滚和 proof 撤销在同一 owner gate 内完成，
不能放锁后让外部 reader 捕获半个失败段。它不是公开 undo、任意删除 Prepared 页或全事务 abort 的替代品。
物理退休在 metadata 撤销后锁外执行；claim 保留至收尾。负例与失败位置覆盖见 [65](archive/br1_pre_m6_20260925/documents/65_br1_native_cpu_mutation_segment_20260920.md)。

### 5.5 Resident CPU 快路径

67 §12 将按页准备 claim 扩展到 generic/adoption：首次 provider unlock 前登记，request → lease → terminal
release 连续保留，native 首写/删除不扫描全局 request map；失败/cancel/seal 归还。它是 owner-gated 预约，不是原位写授权。
未终结写/准备期间拒绝本事务 surface metadata/default 变更，commit/abort/close 仍遵守已有 claim 约束。
删除页只有成功 proof 安装才解除 removal；准备/失败/取消均保持 absence，已捕获 View 不跟随复活。
`AttachHistoricalDefault` 可以与其他 exact version 的 writer/Prepared 共存，但不得改变 head/writer、重复 identity
或复用任何已有物理 slot。后续 default materialization/read lease 也不得改变原写授权；其他转换的写排他约束不放宽。

生产只读迁移的当前边界见 [67 §11](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#11-2026-09-21生产-iterator-与-planar-读作用域)：
独立 H/V/random/包裹遍历与 packed/planar 使用固定选择，跨页不追逐 head；同一 exact current/before 复用物理读 pin。
旧 writable iterator 仍暴露生命周期内可用的裸指针，新读不得擅自结束它的写段。当前同线程重叠读标识为 legacy compatibility，
不是通用 materialization fallback，也不是已完成的 immutable View。后续迁移必须明确业务 mutation 边界并消除该分支，
不能靠改变指针有效期或把未 sealed backing 放进独立 View 来通过验收。

D11 首先将生产 `writeBytes` 接入 `beginCpuMutation(tx, providerId, providerEpoch)` → `beginWrite(key)` → `seal()`；
随后 legacy tile/CPU session 共用该实现。seal 只准备页，不提交 root。tx/page claims 阻止冲突 write/removal/metadata/commit/abort。
67 §13 已将 physical RAM pin 从段寿命改为 guard 寿命：归还 guard 后保留 move-only writer reservation，不保留裸指针；
parked backing 允许 swap，但仍拒绝其他 binding 消费者/退休；再访同一 generation，确实 NonResident 才走显式恢复。
guard 存活时拒绝显式结束；facade/compatibility batch 被销毁时由最后 guard 延迟取消。
compatibility batch 的终结由最后强引用负责，不依靠异线程 unlock 读取放弃标志；弱注册表槽位直到匿名事务 client
终结才移除，避免下一段误加入正在取消的事务。复用既有 lifetime，不为每页增加全局锁；见 67 §15。
67 §14 的显式 CursorPage 将 accessor 换页接到 guard 归还，不增加 canonical 状态转换或 seal：
native pending 仍受段预约保护，默认 OperationSpans 的旧指针继续保活至结束；generic write leases 不提前释放。
换页失败先失效旧缓存；native 分配失败后的段必须失败回滚，不得从缓存取回已停放指针或自动改走 generic。
read/base pin 淘汰不改变固定 View，矩形页块遍历与指针寿命配套；全业务生命周期/预算仍单独验收。
67 §15 将 planar write 与 trim 的实际部分页接入同一 operation segment。trim 的多个带不再重复首写/seal；
全部缺失 channel/空操作不申请 writer，整页删除不申请 pixel backing。`markFailed` 不提前撤销借出的指针，
最终取消 native pending，已有 caller-history delta 保留；混合语义 delta 的全段撤销尚未完成。
67 §16 更新此状态：canonical `KisPageMutationSession` 支持 provider-independent 私有 removal，CPU 为可选执行能力；
删除与原生像素统一 seal，trim/clearAll/removePages 消费它。新 `DetachPreparedVersion` 只把旧 prepared 版本移出 overlay、
转为 Historical，不撤销现有 View/read lease/pin/last-use。coordinator 的 mutation candidate 全部 revision 复验后安装，
不改变 committed epoch tag，不能与 root publication candidate 混用。失败只取消本段候选、保留旧 history。
删除后重写复用 pending generation/backing，按当时 surface default 必要初始化。
67 §17 将 alias/fill 和 PageStore copy 纳入该段：aliasPage 私有保留 provider-issued source，不立即 generation/adopt/proof。
当时的`ReplacePrivatePreparedBacking`已于ed0f229821删除。当前CPU alias由原scope的`KisPagePrivateWrite`与
`replacePrivateWrite`替换同一未暴露结果，保留generation：必须为本activity借用的reserved/completed结果、
没有proof或publication claim、target generation相同、新physical slot不同且未被可见版本占用；旧target交原paid retirement，不修改root。
原source/read者的物理保护不因私有结果可替换而失效。完整新流程与异步lease边界见[统一协议报告](evidence/br1_pipeline_refactor_20261010/unified-rw-r1/RESULT.md)。
它不是可覆盖旧 reader 的原位 permit。alias → write 独立 COW，write → alias → write 复用同 pending allocation，最后一次 alias
在 seal 才 adoption，所有候选成功后一起安装。混合 legacy-source 和 raw live write intent 的旧观察路径仍独立，
不能据此声明所有 copy 入口完成或把可变 producer 授权为 immutable source；history old-source 仍使用固定 base View。
private batch 拒绝非法 alias 后必须整段失败，不能在析构时安装先前私有删除；此前 caller history 不因此回滚。
67 §18 不新增状态机特权：native 私有 Publish 与 proof/detach 候选改在 owner 外准备，但 transaction/PageKey claims
仍保护本段 target/base/provider，旧读者可继续变更自己的 revision。候选改为紧凑 detach delta，全批复验 exact Prepared/
transaction/无 writer 并取得 claim 后，仅更新当前 publication/preparedBy、推进 revision，其余动态保护保留。
不复制或覆盖旧 snapshot，不因合法读者变化重做；真实语义冲突整批拒绝，保留旧 history 与兄弟段。
未进入 sealed proof map 的 Prepared 不对新 View 可见；最终按 key 合并完整 overlay，绝不安装准备前复制的旧 map。
成功收尾在 owner 外销毁输入/私有页并退休，仍保留 claims 至结束；root commit/restore 的严格 page revision 协议不变（§22 改变候选布局，不放宽复验）。
67 §19 的 painter source/mask 修复不新增状态机特权：只读 accessor 只能通过 rawDataConst/oldRawData 消费已保护输入，
不能下转具体 writable 类型绕过其契约；source old-data 选择不改变 mask 的 current View。各 owner 捕获不构成联合快照。
live legacy writer 仍走明确兼容观察；§19 目标 writer 的 tile 解锁边界不因读消费者迁移而被合并为整操作 mutation，
已有借出 pointer/lease 不可由外围 batch 撤销，整操作失败回滚和同页首写复用必须另验。
67 §20 的目标操作只组合已有 canonical mutation 状态转换，不新增写权限。backend 全范围预约防止目标路由中途变化，
但不替代 transaction/PageKey claim、exact-version/COW 与 owner 复验；直接目标 guard 无需额外 before-image read pin，
仍需 mutation base 保护。所有目标仅在 seal 后对新 View 可见，当前 guard 归还不逐页 publish；失败取消只移除本私有段。
现存 legacy 借用在执行前分流，不能在 native 失败后 replay；同线程重入/嵌套 batch 在加入事务前拒绝。
共享匿名事务 client 的完成不能与操作成功混同：canonical cancel 已确认私有段彻底撤销时正常归还 client，
本操作结果仍失败，先前 sealed delta 和外部 writer 保留；没有取消证明或可能已发布的失败继续走事务级 abort。
新操作与既有 CPU batch 的双路径丢数据反例及修复回归见 §20；不把 healthy client release 当成丢弃错误或强制 root commit。
owner-issued permit、所有 producer 的统一入口、短发布及总回收预算不由此自动满足。
67 §21 将 owning reference snapshot 退出 native metadata 的存储/局部更新路径：header 与独立 exact-version 记录分离，
本事务 sealed proof 指定首写候选，physical-slot 索引保留整个页面的冲突见证，不因旧版本未投影而放过 slot 复用。
白名单转换在同一 shard gate 内取输入、执行共享状态机、整序列成功后安装相关记录；失败不安装前缀，未涉及历史保护不变。
§21 阶段 root/restore 与未分类控制转换继续完整候选；§22 将普通 root 候选改成 indexed projection，原 revision 复验保留。
局部输入不是有效全页 snapshot，也不能证明物理或逻辑独占。
reference 误将 Prepared 当作 page-wide 事务锁的旧不变量已由真实负例定位并修正，见 67 §21.2；活动 writer、allocation slot、
foreign read、producer completion 与 root 冲突保护均未豁免。完整 reference 与已存在的生产 optimistic 流程必须共同回归。
§22 的 preparedByTransaction/mutableVersions 索引仅提供全页 guards 的输入见证：commit 必须包括全部 own Prepared，
restore/default 必须拒绝任意 mutable state，slot 唯一性仍覆盖未投影历史。共享状态机的接受/拒绝语义不变。
候选安装只改 publication/preparedBy 与完整 header，必要时加一个 default；先 claim 全批、严格 revision 匹配，再安装 metadata/descriptor，
最后 root 对新读者可见。晚到动态保护不能被 stale delta 覆盖；旧 View 继续受原版本保护。
同步 fused 退休超过单页 32 记录预算是捷径拒绝，不是状态机语义拒绝；owner 必须回退普通 commit + 排队历史收集。
缺失 default 的恢复不再在准备阶段 attach live history；成功才安装其 exact descriptor。新节点/hash/descriptor 仍可能分配，
仍需完整 owner/shard 临界区、冲突重做、回收预算与 M/K/X/E 实测，不以最后 root 赋值代表整个发布。
§23 为 production Historical 记录维护有序索引与值游标，`DiscardHistoricalVersions/DiscardSupersededPreparedVersions` 改用局部
输入执行原 guards；unknown/foreign/重复、capture、lease、pin、last-use、operation 等拒绝行为保持，整个批次成功才移除。
退休效果顺序不是安全契约，identity/effect 集合及最终完整状态必须与 oracle 一致。局部转换本身不证明 root 已不可达。
后台每 key 32 历史记录、每 pass 16 keys，FIFO continuation 与外部事件后的 repeat；跨切片 reachability 缓存必须因新可见 root 失效，
旧 root 删除只能保守延迟回收并由 rescan 收敛。值游标不等于 immutable View，旧 generation 再次 Historical 插到游标之前必须重扫。
metadata 枚举/转换、逻辑 root 引用、物理 pin 与异步 last-use 四者不得合并成一个 reader count；总回收预算及 root 刷新成本仍开放。
67 §16.5 的 ledger 显式分类不改变 page 状态机：已 detached 的退休确认不影响 retained 历史恢复；
source retention、head/transaction 与 metadata revision 检查仍负责保护恢复候选。普通 provider operation 不被豁免。
关闭的 pre-drain 检查允许进入保存的 retirement operation 轮询，但只有全部 terminal success 才能关闭；
公开 operation/debt 计数仍包含退休，失败保留记录且不得重复发 retire。后台回收与可见性控制不得混为同一种阻塞条件。
拒绝嵌套必须发生在加入外层匿名事务之前，否则错误的失败 client 会污染外层事务；不可只检查新 session 没有创建。
仍有 owner mutex、通用 metadata transition/snapshot、逐页 proof 和安全 COW；不宣称所有数据路径无全局锁或原位 permit 已落地。
binding 预约、TileData 防换出 pin 与所有 alias 共用的写授权不得混称。D12 physical claim 使用 allocation
级 pin/ref 协调，但不新增 canonical 状态转换或绕过 generation/retention；上层 permit 尚未消费它，见
[66](archive/br1_pre_m6_20260925/documents/66_br1_physical_exclusivity_prerequisite_20260920.md)。尤其不得在仍有 old G reader/root 可解析 A 时仅凭低层 claim 覆写 A。
before-version 与清除后的语义默认内容须分开：保留真实 base 事务保护，目标按 staged surface default 初始化，不从已删除像素复制。
67 §25 的完整输入覆盖是显式内容来源：仍通过相同 AcquireWrite/PrepareWrite/私有 seal 转换，mode 为 discard，before-version 保护不变；
provider 在返回前完成独立 backing 初始化，没有新增“未初始化但可发布”状态。其输入覆盖整个 page extent，可省掉默认填充和旧页复制；
无能力 fallback 仍初始化后复制。已有 pending 重写保留 writer/generation，private removal 的 default reset 被完整输入取代；
任何失败不得泄漏半段到 overlay，也不能把物理完整输入误当不可 abort 或原位许可。
67 §26 把 epoch 逻辑存活与物理 registry 回收分开：非 current root 只有 snapshot/active transaction base 仍保护时才允许
`beginTransaction/retainSnapshot/root` 接入；最后保护释放即失去资格，不等后台析构。终结事务记录或 raw metadata copy 不恢复资格。
准入检查与新保护登记、最终释放及发布使用同一 epoch gate；不新增采样式 refcount 推断或第二套根权威。
可达性集合只查询 current 与两类 counted protection index，重复 root 只解析一次；没有新 head 时只能缩小，旧缓存可保守延迟回收。
这不代替版本级 captured token、lease/pin、provider operation、last-use 检查，也不等于原位写期间的新 capture fence。
逻辑资格同步更新后，预算 worker 可同轮收集 root/finished-transaction 与历史版本；不再等待物理 root 记账队列清空。
67 §27 将 root/terminal-transaction 的排队链接放入已创建记录；candidate install 之后只连接已存在身份，不再增长 dedup/deque。
候选拒绝不终结事务，reserved root 不入队；protected/current 候选被检查出队后可由后续资格事件重新入队，预算仍计检查数。
普通 native/generic mutable preparation 始终产生独立 backing，不消费 whole-payload adoption seed；只有明确的 sealed
adoption 允许复用合法别名。新 allocation handle 本身不是物理独占证据。

resident CPU 访问允许把通用 request/resolve 状态机折叠为同步 guard，但不能改变其线性化语义：

```text
read: captured root + cached PageHandle
   -> page-local pin/block-swap
   -> validate epoch/version/allocation generation
   -> CpuReadGuard

write: KisPageMutationSession + cached PageHandle -> internal KisPageWriteIntent
   -> beginWrite / expose writable span
   -> unique writer + reserve G+1 once
   -> KisPageWriteCoordinator emits inline plan: pending reuse / conditional backing handoff / fresh payload / necessary COW / semantic-only
   -> CpuWriteGuard
   -> dirty delta
   -> seal once + one root commit at session end
```

快路径不得进入 global request/lease map、heap allocate capability、扫描 active leases 或逐 tile 捕获 root。virtual default
read 返回该 captured view 的 format/default revision 对应的共享只读 view，不创建 page/version/replica。
cached handle miss/tag 失配先在受保护视图中 resolve；所需 exact generation 若已有 ready、CPU 可读且可合法 pin 的 valid
replica，就使用 native read，包括 retained 历史和非 authority CPU 副本。只有缺少适用副本、需要异步 producer/访问交接
或 swap-in/跨域/I/O 才建立 5.1/5.2 的通用 request；局部竞争有界重试/延后，无效 capability/version 显式失败，不能
一律冒充 materialization。读侧选择不放宽写侧 authority handoff、writer exclusivity、COW 或下述 write plan。

allocation A 的 handoff 需要 owner coordinator 原子准备一次性 inline plan、move-only physical claim 和 `KisPreparedMutationCommit`：
A 无 clone/shared 物理别名、reader、in-flight
consumer、materialization pin 和 pending last-use。`HandoffRecoverable` 要求已有 exact before，G 的逻辑 history/save/memento
retention 必须改由受保护的 before backing 解析，不能读被重用于 G+1 的 A；已有 raw reader 不能强制搬走。
`HandoffCommitOnly` 要求无需保留 G 的外部引用、由 old-root capture/read gate 保护、所有可失败工作已预构造，首字节后只能运行
不可失败 kernel 与 prepared mutation commit。无 before 的普通多页 Prepared transaction、长 session 或可失败 producer 禁止 handoff。
计划选择、writer reservation、allocation claim、预算预占与防止新 G consumer 插入必须处于同一线性化协议；它仍产生逻辑 G+1。
通用 `AcquireWrite` 保持同 physical slot 冲突拒绝；只有 coordinator 可构造
`AcquireWriteByBackingHandoff`（recoverable，暴露 writable view 前切换到 exact recovery）和
`ReplacePublishedVersionByBackingHandoff`（commit-only，在 capture fence 内安装预构造 metadata/root）。两者的字段、前置条件、
消费顺序和失败边界以 [68 §6.4](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md#64-状态机专用-transition) 为准，
不得以 public `allowSameAllocation` flag 旁路状态机。
其余情况首次写执行一次 COW，同一 transaction 的后续写复用 pending G+1。guard release 不等于 publish/commit；未升级的
内部 `KisPageWriteIntent` 没有 writable pointer，也不生成 generation；legacy API 一旦暴露 writable pointer
就必须按 dirty 处理，不能通过 pointer 内容比较或事后猜测恢复 no-op。`CapturedReadView` 持有计数的 root retention，
并参与 write-plan 选择，不能留下 snapshot-capture TOCTOU。所有模式同时服从 68 的 backing ledger 和硬预算。

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

`RequiredPreparedTickets` 在接口中表现为 owner-sealed `PreparedPageProof`，包含 transaction/version、完整 authority
provider epoch/allocation/layout、成功 producer completion 与 validation stamp。epoch model 不接受裸 PageVersion；commit
前重新验证 seal、metadata 与 provider，commit/abort 后撤销 seal。

上述 proof 约束真实 prepared 像素写；删除/default revision 变更使用 owner 验证的语义 delta/metadata staging，
不为凑出像素 proof 而新建 default allocation。restore 从有效 retained root 选择 exact 版本，在新 ImageEpoch 发布；
generation 分配高水位保持不变。GC 识别无 payload 的 virtual default 元数据与有 backing 的历史版本，前者无需发出
虚假的 provider retirement，后者仍等待全部 retention/pin/last-use 条件。当前切片证据与未结清项见 54。

prepared metadata batch 是 **owner 内部能力协议**，不是调用者提供的“已验证”布尔值，也不撤销上述 proof。
D2-B 已实装现有 owner gate 内的同步切片（[56](archive/br1_pre_m6_20260925/documents/56_br1_prepared_metadata_publication_20260920.md)）：逐页 revision/短 claim、
move-only 一次消费、整批拒绝、metadata 先于 root 发布；生产 owner/layout、锁外 prepare 与 provider/retention 等价保护仍未结清。
以下完整契约不因该切片缩小：

- move-only、不可伪造、一次消费，绑定 owner/transaction/base epoch、逐页 metadata revision 或等价冲突 token，以及
  涉及的 provider epoch/allocation generation。仅缓存确定未变的验证结果，禁止凭旧完整 snapshot 覆盖新的活跃计数。
- prepare 生成精确 delta 并完成必要完整校验；发布前复验可变化的 writer、generation、retention/pin、last-use 和 provider
  状态。prepare 后的新 reader、last-use、同页修改、abort/reset 若使前提失效，须在发布前拒绝或重新准备；不能拿 root
  pointer 未变作为这些事实未变的证明，也不因无关页变化无条件重做全部工作。
- 新 root 引用的版本与 backing 在 root 可见前已完整可读；失败/取消仍保留旧 root 的 exact 内容。reader 所需 metadata
  不能先 publish 后补齐。不同页锁外准备、同页局部独占、短发布协调；不以跨整个 batch 长持全部 shard 锁达标。
- 复用 transition/invariant 语义与 reference 对照，测试重复消费、foreign owner、并发 reader/last-use、abort、reset 和
  同页冲突。计量 prepare/复验/发布/retire 的总工作与尾延迟，不仅测缩短后的 publish 区间。实施顺序见 52 的 P4、54 的 D2。

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

**新版105的实现分歧：** 以下逐页persistent-map构造是旧实现选择；[105 §6](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/UNIFIED_BACKEND_DESIGN.md#6-文档级可见性与低成本root构造)选择持久Surface目录与受保留的epoch区间页映射，保持同一个不可变PageKey映射合同，避免同时维护两份目录。该设计尚未生产验收，不能把原CPU测试当作跨Surface证明；105实施不得再执行下面的旧逐页manifest构造后转译成新Selection。

旧构造采用 copy-on-write persistent map/radix tree 或等价不可变映射：transaction 只复制发生变化的路径，把
`PageKey -> AfterGeneration` 写入新 root。每个 document 有一个只负责短时间排序 commit sequence 的 commit
sequencer；线性化点是 `DocumentImageEpochHead` 从旧 root 原子切换到新 root。它不持 shard lock等待 producer，也不
执行 materialization。

这里的 persistent map 是 production 必选项而非未来优化。reference model 可以用 `QHash/QVector` 方便检查，但
production `commit()` 不得复制完整 manifest、导出 owning vector、全量排序或通过全 manifest 扫描计算 extent；extent、
region 和 default metadata 由 changed-page delta/空间索引增量更新。

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

之后的新写生成新 generation。serializer 只申请 snapshot 中的 exact generation read lease。历史 read 必须携带 owner
发放且尚未 release 的 snapshot token；裸 `ImageEpochId/PageVersion` 不是 retention capability。

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

materialization 采用两阶段 owner 协议：先在 shard 内 reserve dedup/request/operation identity；锁外只分配 target；再把
target 与一个 PageStore-owned pending logical completion 绑定到 `BeginMaterialize`，由此 pin source 后才允许启动实际
copy/I/O。provider completion 经 registry 验证后终结 logical completion，再入队 `Complete/FailMaterialize`。禁止在
source 尚未被逻辑 pin 时先启动 transfer，也禁止在 shard lock 内调用 provider。单 provider `transfer()` 只处理相同
provider id/epoch；跨 CPU/UMA/VRAM/SSD 必须走显式 transfer bridge。

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

handoff completion 失败时必须走显式 failure transition，释放 source/target pin 并保持旧 authority；不得把记录留在
永久 in-flight 状态。retirement 同样必须回显 PageStore 分配的 operation id，并以 Complete/Fail 两个终态结束；失败
只把非 authority replica 标记为可重试的 Failed，不得影响 published generation。

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
AcquireWrite / ResolveWrite / BeginPublish / CompletePublish / FailWrite / Cancel
BeginMaterialize / CompleteMaterialize / FailMaterialize
BeginHandoff / CommitHandoff / FailHandoff
BeginRetire / CompleteRetire / FailRetire
CommitTransaction / AbortTransaction
AbortPreparedVersion // owner-only rollback of an unexposed failed native seal segment
RetainCapturedVersion / ReleaseCapturedVersion // owner-bound sealed overlay lifetime
CaptureSaveEpoch / ReleaseSnapshot
Undo / Redo / DeviceLost / CloseSession
```

production provider 必须复用同一 transition 函数，不能另写“更快”的宽松状态机。

复用 transition 语义不等于复用 reference 容器和调用粒度。reference model 可以逐事件保存易检查的完整集合；production
可以使用内联 guard、紧凑 record、persistent root 和 batch transition，只要线性化点、capability 校验和 observable trace
与 reference 等价。禁止把 reference 的 owning manifest snapshot、`QVector` 输出或全量排序接入 iterator、tile unlock、
commit、extent 或普通 read 热路径。

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

2026-09-19 已完成 typed identity、deterministic/random transition、统一 invariant validator、固定 seed 序列与
production 对照；演进记录见 46，功能/正确性关闭证据见 51，production 布局出口见 52。

### PS-SM1：分片 metadata

- shard map、锁顺序、completion queue；
- materialization dedup；
- 无 I/O 的 fake provider 压力测试。

2026-09-19 已完成 immutable ImageEpoch、sharded transition owner、materialization dedup/completion drain、
production CPU provider、owner ledger/proof、retained snapshot、last-use retirement、锁外 provider 调用与
fail-closed close；真实 tiles3 accessor/memento authority cutover、多线程压力、fault matrix 与 metadata/latency budget
均已进入验证矩阵。阶段演进见 47–50，功能/正确性关闭证据见 51，production 快路径出口见 52。

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

PS-SM0–PS-SM4 的 BR1 功能/正确性范围于 2026-09-19 形成证据；production resident CPU fast path、virtual default、
persistent root 和增量 metadata 在 BR1-PERF 关闭后才算整体完成。native asynchronous Vulkan provider 仍由 BR2/BR3
接续，不得先接入 production 路径掩盖 CPU 缺口。

## 13. 完成门槛

- 任意完成乱序、取消和 OOM 下不变量成立；
- 相同 materialization 只有一个物理 producer；
- shard lock 内没有 wait/I/O/queue 调用；
- stale completion 和 ABA handle 被稳定拒绝；
- 多页 undo/save 不看到未提交 transaction 的混合 generation；
- default、extent、COW、clone、animation frame 与现有 CPU 测试一致；
- PageStore metadata 不包含 Vulkan/SSD 私有对象；
- production 和 reference 使用同一 transition 语义。
- default read 不实例化 page/version/replica，resident CPU hit 无 heap/global-map/provider-scan；
- 同一 mutation 的同一未发布段每页只 reserve、必要 COW 和 seal 各一次；发布后新段重新取得 writer/permit，tile unlock 不隐式提交 epoch；
- production commit 随 changed-page 数扩展，不存在 ordinary `O(N)` manifest rebuild/sort/extent scan；
- CPU 差分性能达到 52 的 upstream 门禁。

### 13.1 Prepared publication 的存储边界（2026-09-21）

`PreparedPublication` 除语义 delta 外，现持有已有版本转 Historical 所需的 map node；fused 小历史路径持有完整 replacement record-set。
所有页 claim 和 revision/semantic revalidation 成功后才移交，保持 metadata-before-root 与全批原子性。准备失败、晚冲突、取消、foreign
owner 和 owner 析构的候选不得改变 live index。详见 [67 §28](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#28-2026-09-21metadata-候选持有发布所需存储)。

新增 default record、descriptor、completion 和回收调度仍是独立可失败/分配面；普通 local transition 也未改成 prepared publication。
因此状态机正确性覆盖不等于短发布完成，更不授权复用 Published backing。

后续 [67 §29](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#29-2026-09-21新增-default-record-的候选存储与容量准备)
使缺失 exact default 的 record node 也由候选持有，并在准备阶段按 revision 预留 live exact/slot capacity；安装期 capacity 不变。
这不改变 transition 语义，也不覆盖 PageStore descriptor 与 owner postwork；取消候选可能保留非语义 capacity，不能误写成 live metadata
完全零变化或全 commit 无分配。

随后 [67 §30](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#30-2026-09-21descriptor-容量准备与解锁期变更复验)
为 PageStore descriptor 建立语义 revision 和发布前 capacity 准备；metadata 安装成功后 descriptor 先完整可用，再切 root。该 revision
是 owner 存储复验，不取代页 revision、directory revision 或 epoch root rebase，四者保护的事实不同。

[67 §31](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#31-2026-09-21publication-cleanup-所有权移出-owner-gate)
进一步规定已消费 publication candidate 的销毁属于显式 cleanup ownership：安装返回不应在外层 owner gate 内隐式析构旧 fused record-set。
成功与拒绝都可移交，且 cleanup 不依赖 coordinator 存活。当前 PageStore commit/restore 已消费该接口；mutation 调用点及预算化销毁仍开放。
这不改变 transition 接受条件、page revision 复验或 metadata-before-root 的原子性。

[67 §32](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#32-2026-09-21分批-metadata-cleanup-与预完成-host-evidence)
给 deferred cleanup 增加 candidate-page unit 分批协议，mutation/commit/restore 使用同一 disposal policy；后台 continuation 不接触 live metadata。
同步 host completion 改为预完成、可复用的终态证据，因为状态机只需要确认无 pending last-use，不依赖它承载操作序号。异步 domain 的 ticket
仍不得复用；version/operation/request identity 也不受该优化影响。
