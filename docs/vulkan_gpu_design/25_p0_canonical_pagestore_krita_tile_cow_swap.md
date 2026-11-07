# P0：Canonical PageStore 与 Krita Tile/COW/Undo/Swap 吸收

> 2026-11-04 新版后端扩展设计：[105完整规范](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/UNIFIED_BACKEND_DESIGN.md)。逻辑版本、公共访问与provider合同保留；内部private/proof不再是所有写的必经结构。 当前只完成设计，CPU产品0fd96保持；不据此声称GPU/完整能力已实装。旧实现名称不能覆盖105的目标责任，未迁消费者在原矩阵追踪。

> 本文定义唯一权威像素模型。PageStore 不是 Vulkan 新建的第二套 tile manager，而是把 Krita 现有逻辑 tile、
> COW、memento、tile data store 和 swap 语义提升为显式 Surface/Page/Generation/Lease/Replica 状态机。
> 状态布局、线性化点、分片并发、materialization 去重和多页 transaction 的可实施算法见
> [33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md)。
>
> 2026-09-20 状态：2026-09-19 已完成 BR1 功能/正确性 cutover，证据见
> [51_br1_canonical_pagestore_closure_20260919.md](archive/br1_pre_m6_20260925/documents/51_br1_canonical_pagestore_closure_20260919.md)；同机 upstream
> 差分随后发现 resident CPU 热路径、稀疏 default 和 epoch 生产布局未达到出口，BR1 已以 **BR1-PERF** 重开。
> 实施顺序和性能门禁以
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md) 为准。
> 写侧的条件 COW、backing handoff、零冗余复制定义与硬预算以
> [68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 为准；
> 本文旧 `InPlaceWritePermit` 表述只保留为安全需求来源，不再是目标公共 API。
> durable SSD 与跨域 replica 仍属于 BR3，不能用于绕过 BR1-PERF。

## 1. 现有语义必须保留

当前 `tiles3` 已提供大量成熟语义：

- `KisTiledDataManager` 维护逻辑 tile hash/extent/default pixel；
- `KisTile` 连接逻辑坐标与 `KisTileData`；
- `KisTileData` 通过共享/复制实现 COW；
- `KisMementoManager` 记录 tile change、revision、rollback/rollforward；
- `KisTileDataStore` 全局管理 tile data、内存统计、pooler 和 swapper；
- `KisSwappedDataStore` 把 tile data 压缩/换出并恢复；
- iterator/accessor 依赖 oldData/current memento 行为。

P0 不能绕过这些语义再造“GPU tile + 结束后回写”。目标是把这些已有身份和历史关系显式纳入 PageStore。

## 2. Canonical 身份

### 2.1 Surface

每个 canonical paint device/frame 对应稳定 surface：

```text
SurfaceId
DocumentId
NodeId
FrameId
SurfaceKind
SurfaceFormat
DefaultPixelGeneration
Extent/RegionRevision
PublishedRevision
CommittedImageEpochId
```

同一个 PaintDevice 的 projection、display image、GPU atlas 不能复用其 canonical SurfaceId；它们是不同 derived surface。

### 2.2 LogicalPageId

```text
LogicalPageId = (tileColumn, tileRow)
```

- 几何服从 Krita logical tile 大小和坐标规则；
- 与 Vulkan sparse granularity、atlas slot、buffer allocation 无关；
- 空白/default tile 可以没有物理 allocation，但仍有规范化 generation/value；
- wrap/LoD 是访问/derived 语义，不改变 base LogicalPageId。

### 2.3 PageGeneration

每次成功写入产生新 generation：

```text
PageKey = SurfaceId + LogicalPageId
PageVersion = PageKey + Generation + DefaultPixelRevision
```

普通像素版本的 `DefaultPixelRevision == 0`；default sentinel 使用非零精确 revision，避免不同历史 default 被混为同一内容。
新写 reservation 的 generation 高水位单调且不复用；undo/redo 在新 ImageEpoch 中可以重新选择较旧的 exact PageVersion，
不表示分配器倒退，也不要求为了恢复旧内容重新分配/复制像素。

`KisTileData`/shared arena block/RAM allocation/VRAM slot/SSD record 都是某个 PageVersion 的 replica 或 backing，
不是独立 page identity。

## 3. Page record

```text
SurfaceId
LogicalPageId
SurfaceFormat
PublishedGeneration
PreparedGenerationsByTransaction
WriteGeneration(optional)
AuthorityReplica
ValidReplicas[ReplicaDomain -> Generation/State]
ReadLeaseSet
WriteLease(optional)
InFlightTicketSet
PinReasons
ResidencyPolicyHandle / SemanticClassSnapshot (non-authoritative)
SsdRecord(optional)
DependencyGenerations（derived only）
Default/Allocated state
Error state
```

`dirty`、`tier`、`layout` 不作为上层可直接修改的真相；它们从 generation/replica/ticket 状态推导或由 backend
私有保存。

## 4. 永久不变量

1. 每个 `PageKey` 只有一个 `PublishedGeneration`。
2. 同一 `PageKey` 同时最多一个 write lease/write generation。
3. write generation Prepared 且所属 ImageEpoch transaction commit 前，旧 PublishedGeneration 继续有效。
4. producer 失败/取消只丢弃 WriteGeneration，不修改旧 PublishedGeneration。
5. authority handoff 只有在目标 replica 完成、generation 匹配且校验通过后原子提交。
6. authority 被释放前，至少另一个同 generation replica 已 valid，或 page 是可重建 derived。
7. SSD write/index commit 前，源 authority 不能释放。
8. derived page 不能成为 canonical surface 的 authority。
9. CPU/GPU/IO 访问都持有 lease；in-flight allocation 不能复用。
10. 只有 PageStore completion/transaction-commit 路径能改变 PublishedGeneration/AuthorityReplica。
11. 迟到 ticket 完成不能覆盖更新 generation。
12. default/empty page 的 materialization 必须产生规范内容，不能读取未初始化内存。

virtual default 的 recoverability 来自 exact surface format/default revision/descriptor，可以没有物理 authority 或 replica；
这不是释放普通像素 authority 的豁免，也不是把丢失/未就绪内容冒充 default。所有新 root 可见前须已有完整的恢复描述。

Debug/CI build 始终检查这些不变量。

## 5. API

```cpp
ReadRequest  acquireRead(PageKey, ReadView, AccessRequirement, Priority);
WriteRequest acquireWrite(PageTransaction, PageKey, AccessRequirement, WriteMode, Priority);
bool resolvePageVersion(PageKey, ReadView, PageVersion *out);

ReadLease  resolve(ReadRequest, CompletionTicket);
WriteLease resolve(WriteRequest, CompletionTicket);
bool cancel(ReadRequest);
bool cancel(WriteRequest);
void release(ReadLease, CompletionTicket consumerLastUse = {});

CompletionTicket publish(WriteLease, CompletionTicket producerCompletion);
void cancel(WriteLease);

PageTransaction beginTransaction(ImageEpochId base);
PageTransaction beginCurrentTransaction(); // atomic current-root capture + base retention; no manifest export
ImageEpochCommitTicket commit(PageTransaction, PreparedPageSet);
bool abort(PageTransaction);
ImageEpochSnapshot captureCommittedEpoch();
RetainedImageEpochSnapshot captureRetainedEpoch();
bool validateRetainedEpoch(RetainedImageEpochSnapshot);
bool releaseSnapshot(ImageEpochSnapshotToken);
```

底层 acquire/resolve 是**单页控制原语**。`ReadView` 明确选择 `CurrentCommittedEpoch`、指定 `CommittedEpoch`、
`TransactionBaseEpoch`、`TransactionOverlay` 或 `ExactVersion`；`acquireRead()` 在线性化点解析成单一 exact
`PageVersion`。多页读取必须先捕获受保护的 `KisCapturedReadView`，驻留页走 native guard，确需控制路径时用
`acquireReadInView()`。重复使用动态 current/overlay selector **不能**保证跨页一致性，也不应强制每页创建 request/lease。
overlay 捕获固定当时 sealed delta、删除集合和 staged surface metadata，独立保留其 Prepared 版本；后续 seal、commit、abort
不改变该视图。未 sealed writable backing 不可见，`epoch()` 表示受保护 base，不是伪造的新 committed epoch。
直接单页 `acquireRead(TransactionOverlay)` 仍是当次动态解析；不要把它与捕获后的 overlay 混称同一访问契约。
共享 `PageTransaction` 加 `PreparedPageSet` 保证原子发布。禁止返回一个只有单一 `version()` 却覆盖多个 generation
的含混 lease。`resolvePageVersion()` 只解析 selector 对应的 identity（包括 transaction prepared write 与 staged
removal 的 default sentinel），不 materialize 像素、不给出裸指针，也不替代 acquire/lease 或受保护的 native guard。

被捕获的 sealed 私有版本在 abort/删除后转为 detached Historical，而不是强制退休；逻辑 view token、物理 pin、
异步 last-use 分别满足后才可回收。默认值 revision 在同一 owner/surface 生命周期不复用：`stageSurfaceDefaultPixel()`
由 owner 分配高水位后的新 identity，abort/undo 不降低高水位；显式 `stageSurfaceMetadata()` 不可用旧 revision 表示新 bytes。
同事务 A→B→A 仍采用新 revision，不能与仍被读者持有的旧 A/B identity 冲突。按检查过的 bytes 删除时使用
`stagePageRemovalIfUnchanged()` 在 owner 内复验 exact version，不得删掉检查后被替换的新内容。

request、writer、lease、operation 都使用 PageStore 分配的不可伪造单调 ID；transaction id 与 retained snapshot token
同样必须跨 PageStore/ImageEpoch 实例保持进程内唯一，不能让另一 document 的同号 capability 通过结构校验。read/write lease 都是 move-only，
不得用复制增加未计数引用；read lease 由 `release()` 消费并携带可选 consumer last-use ticket。replica identity 必须
同时包含 provider id、provider epoch、allocation slot 和 allocation generation，任一不匹配都按 stale/ABA
completion 拒绝。

`KisPageAllocationDescriptor` 是 provider 分配的完整输入，必须包含 layout revision、完整 `SurfaceFormat`（含
default pixel bytes）、logical extent、valid rect、row alignment 与初始化策略；provider 返回的 `ReplicaLayout`
必须与 descriptor 精确兼容。不能从 generation 或全局 image 状态猜 pixel stride/default/layout。跨 provider copy
必须经显式、在 initialization finalization 前注册的 `KisPageReplicaTransferBridge`；单个 provider 的 `transfer()` 只接受
同一 provider id/epoch 的 allocation。零个或多个 bridge 匹配都 fail closed；同步 CPU facade 只接受声明
terminal-at-return 的 bridge，async bridge 必须接 coordinator logical readiness 后才能注册。

`AccessRequirement = AccessDomain + AccessKind`，其中 `AccessKind` 至少区分 `CpuPointer` 与 `GpuBinding`。
这对 UMA 是必要的：同一个 shared domain 可同时支持两种访问，不能用 domain 猜测调用者需要指针还是 operation-scoped
binding。SSD 不是可直接 resolve 的 consumer access；必须先 materialize 到可访问 replica。provider 通过
`resolveAccess(lease, operation, replica, requirement, mode)` 返回短期 view，并在 `releaseAccess()` 消费同一 lease
identity/last-use ticket。provider capability 必须枚举精确 `(domain, access kind)`，不得用 domain 列表乘以全局
CPU/GPU bool 推导并不存在的组合；同时提供 UMA CPU/GPU view 时必须明确保证 shared backing。

provider transfer 必须带显式 kind：`ExactVersionMaterialization` 只允许 source/target 为同一 PageVersion；
`WriteGenerationInitialization` 只允许同一 PageKey 从 base generation 到更大的 reserved write generation。
`prepareWrite()` 同时接收 `WriteMode`。禁止为了复用一个 copy API 而取消 exact-generation 校验。
所有异步 provider action 包括 retirement 都接收并回显 PageStore 分配的 operation id，返回 completion；每个 begin
必须存在 success/failure 终态，使失败可重试且 stale callback 不会永久占用 pin。

`publish()` 在 producer 完成后把页置为所属 transaction 的 Prepared generation；单页 operation 也使用只含一页的
显式 core transaction，facade 可以提供创建/提交该 transaction 的 convenience，但不能绕过它。多页 batch 只有在
immutable ImageEpoch manifest 原子 commit 后才改变普通 document reader 所见的 PublishedGeneration 集合。
这里的 PageStore visibility transaction 可以是一批页面；完整 stroke 的 Krita undo transaction 可顺序聚合多个已
commit ImageEpoch，二者不得混为一个生命周期。

`abort()` 可取消尚未 resolve 的 write request；active writer/写 segment 仍阻止 abort。未被独立 captured View 保护的
Prepared generation 若有 active/pending-last-use read lease，必须返回 `false`，调用者先消费 lease 再重试。
有独立 captured-version token 的 sealed Prepared 可从事务脱离为 Historical，即使读 lease/last-use 尚在；
其 bytes 和能力继续有效，最后 token/lease/pin/last-use 满足释放资格后才退休，不强制回收。
禁止为了“强制 abort”释放 provider access 后让调用者手中的 CPU pointer/GPU binding 悬空。

需要读取历史 generation 时，由 `ReadView::CommittedEpoch/ExactVersion` 同时携带 retention token 与 exact selector，
并由 epoch owner 验证 token→root→version；仅有 epoch/version 数字不构成历史 retention。这里的
`CompletionTicket` 必须是定义在 `kritaimage` 的 backend-neutral completion value handle；
名称不允许意味着调用者可取得 Vulkan fence/semaphore，CPU/IO completion 也通过同一 ticket bridge 表达。
ticket identity 包含 registry、typed domain、source 和 value；不同 registry 的相同 source/value 也必须拒绝。只有同一
registry、同一 source 的 `GpuTimeline` ticket 可以使用 timeline 顺序，CPU/IO/host logical ticket 只能精确匹配并由
registry 产生 terminal verification。
`ImageEpochCommitTicket` 同样是 backend-neutral host logical completion，不要求或允许 UI 直接等待 Vulkan primitive。

`PreparedPageSet` 不接受裸 `PageVersion`。每页必须携带由 PageStore owner seal 的 proof：transaction/version、完整
authority identity/layout、成功 producer completion 与 owner validation stamp；commit 重新核对 metadata、provider 和
owner seal，成功 commit/abort 后撤销 proof。

### 5.1 Request 与 Lease 分离

- `acquire*` 原子检查/预留逻辑状态并返回 request + readiness dependency；read request 在返回前已 pin exact replica，
  不能把 pin 延迟到 `resolve()`。
- materialization、SSD read、VRAM upload 或旧 writer wait 可以异步发生。
- 只有 readiness 完成且 request 仍匹配 generation 才 `resolve()` lease。
- 不再需要 request 时必须显式 `cancel(request)`，释放 read pin 或 write reservation；重复/伪造 cancel 被拒绝。
- consumer 不通过轮询物理 tier 判断是否可访问。

### 5.2 Read lease

包含：

- exact PageVersion；
- CPU pointer/span 或 opaque GPU binding handle；
- valid rect/stride/format codec；
- replica domain；
- release operation。

read lease 期间对应 replica/page version 不能回收或被写入覆盖。

### 5.3 Write lease

包含：

- base PublishedGeneration；
- reserved WriteGeneration；
- exclusive writer token；
- writable CPU pointer 或 opaque GPU binding handle；
- before-image/COW snapshot dependency；
- producer/publish contract。

write lease 不能被复制成多个 writer。多页面 write request 返回每页独立 lease/token，但 operation 可批量管理。

### 5.4 Resident CPU 原语与通用异步原语的边界

上述 `acquire/resolve` 是跨域、缺页、I/O、GPU 和 exact historical materialization 的通用原语，不要求 resident CPU
命中为每次 tile lock 建立 heap request、全局 ledger entry 或 provider reverse lookup。生产实现必须额外提供语义等价的
native CPU 原语：

```cpp
CapturedReadView captureReadView(ImageEpochSelector);
CpuReadGuard tryAcquireResidentCpuRead(CachedPageHandle &, const CapturedReadView &);

KisPageMutationSession beginMutation(const KisPageTransaction &, QString *error);
KisCpuWriteGuard KisPageMutationSession::beginWrite(
    const KisPageKey &, KisPageWriteMode, QString *error);
bool KisPageMutationSession::seal(QString *error);
bool KisPageMutationSession::cancel();

MaterializationRequest acquireNonResidentRead(...);
```

这些是 PageStore 的 CPU data plane，不是第二套 authority。guard 仍执行 exact-version 校验、pin、writer exclusivity 和
release transition；暖 cached binding 命中压缩为 O(1) 局部操作，cache miss 的 root lookup 仍按生产索引复杂度计量。
写侧内部类型、字段布局、状态迁移和析构顺序以 [68 §4](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md#4-统一能力封装类型边界与调用方式)
为唯一口径；`beginCpuMutation()/enableCpuWrites()` 只是在生产迁移期转发到 `beginMutation()` 的兼容包装，不是长期 API。
以下约束针对已捕获 scope 内的 resident 像素访问；capture/release、首次 binding、局部锁及完整操作成本按 39 的 5.12
分别验收，不宣称整个调用链严格 lock-free 或零分配。resident fast path 必须满足：

- guard move-only，优先栈上/内联保存，不建立 heap lease node；
- 不进入全局 request/lease map，不扫描 active lease，不取得 PageStore 全局 mutex；
- accessor/session 在操作边界捕获一次 `CapturedReadView`，tile 切换复用 epoch root 和 `CachedPageHandle`；
- cache 带 PageKey、PageVersion、epoch tag、provider/allocation generation，只是加速索引，不是可见性线性化点；
- cached handle miss/tag 失配先在受保护视图中 resolve；virtual-default miss 返回该视图 format/default revision 的共享 view；
- 当前或 retained 历史的所需 exact generation，只要已有 ready、CPU 可读且能合法 pin 的 valid replica，就可走 native read；
  authority 在其他域、或副本是 UmaShared，不单独构成降级理由；
- 缺少适用 CPU 副本、需等待 producer/访问交接或 swap-in/跨域/I/O 时才走通用 request/resolve；无效 capability/version
  显式失败，局部竞争有界重试/延后，不能将 cache miss 或标签差异伪装为物理缺页；
- 快慢路径调用同一 transition/invariant 验证，不能形成宽松 CPU 状态机。

以上是读侧副本选择，不放宽 writer exclusivity、authority handoff 或原位写 permit。CPU/CpuRam 同义管理以主干 Tile
等价或更优为目标，按 39 的 5.6 独立不劣性验收；不因 PageStore 内部记账而获得额外预算豁免，完整操作阶段上限不证明等价。
本文 lease 的读取、互斥、关闭与退休寿命约束同样覆盖 native guard；不进入 generic lease map 不代表没有活跃消费者。
受保护 guard 可短期携带 CPU span，canonical metadata 不因此保存裸 pointer 或成为第二套物理权威。

实现补强（当前推进见 [67](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md)）：虚拟 default 的 exact before-image
可以由逻辑版本及 surface default revision 表达，writer reservation 保留该逻辑版本；没有物理源时不伪造 authority/pin，
只初始化独立目标 backing。状态机仅在实际 virtual default 且 discard 初始化时接受空 source，普通物理版本仍要求合法 source。
取得授权后，即使另一个读者物化该 exact default，writer 的逻辑 before-image 仍有效，不能改以新 replica 的物理 pin 作为原授权依据。
CPU read/oldData 应使用 View 对应的共享不可变 default bytes，保留逐 key 的逻辑版本；不伪造 provider replica 或借用 current default。
共享 buffer cache 必须有容量上限，淘汰不得破坏 guard 持有的旧内容；初始化工作与合法存活 bytes 进入独立统计。
初始化导入也必须维护这一内容事实：payload manifest/adoption 仅接受普通 content version，默认内容由 surface metadata 表达。
不得把任意像素导入标记为 `defaultPixelRevision != 0` 的语义版本，否则 native default 与 provider payload 会给出不同内容。
source copy、generic/native reader/writer 和 retire 必须经过同一 binding/物理互斥；不能只查询 generic activeWriter 字段。
`nativeCpuMutation` 是比同步复制更强的独立能力声明，不自动授予 in-place permit。

写侧准备落实补充见 67 §12：native 与 control 在 owner 内按 PageKey 协调，generic/adoption 在首次锁外 provider
准备前就登记；request/lease/terminal release 结束前保持同页预约，失败必须归还。该索引不替代 writer/physical permit。
本事务有未终结写或准备时冻结 surface/default 契约，变更须位于段边界。删除后的复活只与成功 prepared proof 安装同时发生，
不能在申请 backing 时先撤销 removal。partial 目标以 staged default 初始化；整页 adoption 使用当前 surface 描述符。
旧 removed/default View 在其他版本写入期间仍可独立物化 exact default，不能借此更改 head/writer 或别名到 mutable allocation。

锁外提交准备的实现约束：先以 owner claim 冻结本事务 delta，排除尚存的 native segment、generic write request/lease、
provider 准备和 terminal publish/cancel；该 claim 不是物理写权限。Prepared 版本及事务 base 保护候选依赖的逻辑对象，
provider 注册在 operational 期间不变。只构造元数据不需要假造 CPU resident pin，但不能据此访问可交换的像素。
重新进入 owner 后复验 current head；若计划合并回收，还须重新检查 retention/其他事务，native reader 不产生 metadata lease 也不能漏掉。
metadata 的全批 revision claim 防止覆盖新 lease/last-use；涉及默认值的全目录计划另验页注册变化，避免漏掉准备期间新增的空白坐标。
undo/redo 独立保留恢复源 root，metadata 准备后拒绝已变化的 head/新事务，再执行同样的完整安装。
这些是当前 [67](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md) 已消费的协议，不代表原位 permit、历史清理预算或短发布性能已经结清。

回收落实补充见 67 §9：tiles3 CPU provider 显式声明后台退休能力，历史候选和首次物理退休进入有数量批次的生产队列，
persistent tree 子引用后台迭代释放；pin/retention/last-use 仍分别复验。旧 View 释放不执行全量历史 sweep，关闭必须等待在途任务并汇总队列债务。
单页版本扫描、总积压和内存压力反馈尚未有完整上界；不能把“搬到后台”记为工作消失或全链路预算完成。

`CapturedReadView` 必须持有计数的 immutable-root retention，并参与 backing handoff gate。`KisPageMutationSession` 是显式 RAII
transaction facade；内部 `KisPageWriteIntent` 不暴露 writable pointer，`beginWrite()` 才在 first-write reserve G+1、建立 before
retention 并选择原位写或一次 COW。同一 session 的同一未发布段后续写复用该 pending G+1；seal/发布后新段重新取得
writer/permit，不跨已可见版本沿用旧授权。当前 native 实现（67 §13）在 guard release 时归还实际 RAM pin、清除裸指针，
scope 保留局部 writer reservation 至 seal/cancel；再次访问同一 pending backing 重新 pin，不重复首写/COW。
parked 期间允许受控 swap，不允许其他消费者 read/write/copy/transfer/retire。真实 NonResident 才走 owner gate 外的
tiles3 同步恢复控制路径；不是异步物化已完成。仍借出裸指针的 session/legacy cache 必须继续保留 guard/pin，其工作集另验收。
67 §14 显式区分默认 `OperationSpans`（全部 span 保活到 finish/cancel）与 `CursorPage`（尝试换页即失效）。
RandomAccessor/SurfaceOps 使用后者：native 当前 target/before-image 各至多一个 guard，固定 View 和 parked pending 版本不变；
generic 仅释放离开页的 before/read pin，未发布 write leases 仍保留，不允许以换页作为 seal。
矩形读写按页块处理所有相交行，避免单页 pin 配合逐行跨页放大重复工作；copy 临时 buffer 和总 dirty 记账另计。
67 §15 的生产 planar 写和 trim 部分页现共用操作级 native 段；同页多个裁剪带只取得一次 writable backing。
整页删除仍是语义 delta，不做像素工作。batch 失败在所有 guard 归还后取消未发布像素，不能撤销调用方此前已 sealed/staged 的历史修改；
混合删除/alias/像素的私有 delta 与整段撤销仍须补齐。compatibility hash 的坐标能力与 canonical identity 范围分别校验。
上述是 §15 的检查点边界。67 §16 已把删除与像素纳入同一 `KisPageMutationSession` 私有 delta：`beginMutation/removePage`
不要求 CPU provider；`enableCpuWrites` 仅选执行能力，旧 CPU session 是 source alias。trim/clearAll/removePages 已接入。
seal 完成全部新 proof 与 metadata revision 复验后，在同一可见性切面安装 removal/revival/proof；失败保留 prior history。
旧 prepared 版本转为 Historical 而非强行释放，capture/read lease/pin/last-use 继续保护；删除后重写可复用同段 pending generation/backing。
67 §17 已继续接通完整 fill/clear 与 PageStore → PageStore copy 的 alias/removal/像素私有 delta，成功后只刷新 changed keys。
source 能力保持 immutable backing 与 COW-user 引用而非 RAM pin；首次真实修改才独立准备，已有 pending 页可初始化复用。
最终 alias 换 backing 只作用于本段未暴露的 Prepared 版本，不能覆盖旧 View 或作为原位 permit。
混合 legacy-source copy、live source write intent 分流、全部 brush 边界、原位 permit 与完整短发布/回收预算仍未结清。
live source 范围探测只读已有 wrapper 的局部状态，不新增全局 lock/unlock 记账；额外访问页扫描成本仍归 M/E。
private batch 拒绝非法 alias 必须整段失败，不能在析构时提交此前私有删除。后台回收与可见性操作也必须分开。
67 §18 进一步以连续 transaction/PageKey claims 保护 seal：私有 metadata、completion、proof 与旧版本 detach 候选在 owner 外准备，
安装前复验全批 exact Prepared/transaction/无 writer 并取得 claim，按本段 key 合并而不覆盖兄弟段。紧凑 detach delta
只改变当前 publication/preparedBy，保留最新读者/pin/last-use，不因读者 churn 重做；真实拒绝取消本段，不回滚此前 history。
root publication 仍严格复验 page revision（§22 普通候选不再携带完整 snapshot）。writable reservation 在目标仍私有时归还，完整 overlay 安装后于 owner 外销毁
private page/source 容器并退休；claims 保留至收尾。输入/安装/历史分类仍有全局临界区，不能据此宣布原位 permit 或短发布完成。
67 §19 将真实 painter bitBlt 的 source/mask 改为公开 const accessor 消费者，修复下转 mutable accessor 导致的生产崩溃。
current source/mask 与明确 old-source 各选正确 View，保持 wrap/offset、live writer 兼容和 self-copy；不授予跨 owner 联合快照。
§19 当时的目标端仍按 legacy writable accessor 的 tile 生命周期写入。操作级 batch 不能接管已借给外部的 wrapper/lease，
后续必须明确 writer 归属及失败边界，不能把只读消费者接通记为全画笔 mutation 或原位 permit 完成。
67 §20 现将正常 bitBlt 目标接入显式 `applyPixelOperation`：目标专用 cursor 直接使用 mutation guard，不提供 oldRawData，
不额外取得未消费的目标 before-image View/pin，base 仍由 mutation 保护。范围准入先检查已有 writer/intent；legacy 借用
只在 callback 前选择兼容边界，native 争用等待全范围，不持部分页、不以 generic 降级。同线程重入及外层 batch 先拒绝。
段内同页重访复用 pending backing，换页只归还 guard；非法移动/后页失败毒化并取消，成功后才按 touched keys 更新索引。
范围预约是 backend 协调，不是 canonical writer permit；直接目标路径仍采用安全 COW，不宣称独占即可物理原位覆写。
取消私有段与 abort 共享匿名事务必须分开：只有 canonical cancel 确认全部私有工作撤销，才健康归还本 client，
保留已 sealed 兄弟段/外部 writer；本操作仍失败。generic/可能已发布或无法证明私有取消的失败仍事务级 abort。
新操作和既有 CPU batch 均按此处理；一段 seal 不等于一次 root commit。其余 multi-dab/fill/line、legacy 归属最终迁移、
owner-issued permit、短发布/历史布局与回收总预算仍未完成，见 67 §20 的生产与失败回归。
67 §21 的 metadata 生产布局进一步拆出 header、独立版本记录及 exact/physical-slot 索引。native 首写从受保护 base 与本事务
sealed proof 读取指定版本，私有 writer/capture/cancel 转换只投影相关记录及全页 slot 冲突见证，仍执行同一状态机保护。
snapshot 不共享 owning version 容器，单版本更新不再复制整页历史；§21 时诊断/控制/commit/restore/GC 的完整导出显式保留并计数，root 后续迁移见 §22。
未投影的历史不是无 reader/retention/alias 的证明，不能凭这些局部输入签发原位 permit；现有安全 COW 仍只是过渡。
Prepared 归属是逐版本的，独立 optimistic 事务可持有同页不同 sealed 版本；活动 writer 唯一、foreign read 拒绝及 root 冲突
检查继续生效。本节缩减实际写侧 metadata 工作，不宣称全部 CPU 模式已与主干等价或整个生产布局/回收已完成。
67 §22 普通 commit/restore 用 current/target/own Prepared 与必要冲突见证构造候选，claim 全批并严格复验 revision 后，
仅安装 publication/preparedBy delta 与必要 default 新记录。未变 replica、pin/lease/last-use/captured 列表不重写；
不以省略 H 证明原位写许可。恢复缺失 default 版本与其 descriptor 改成候选成功后、root 前安装，拒绝不留下预检 history。
default/full restore 目录只导出 header，删除/恢复精确 lookup；同步 fused 退休限制为 32 records/page，超出回退普通提交+后台收集。
这减少 H 放大，但目录 N、控制/GC、插入分配和完整 owner 协调仍有成本；不是总回收预算或无锁/零分配发布的结清。
67 §23 将 opt-in 生产 GC 接到有序 Historical 索引：值游标分批选版本，局部 discard 保留 root、captured token、lease/pin/last-use
与 provider operation 的独立安全检查。每 key 32 条、每 pass 16 keys；长页 FIFO 续扫，语义/资格事件要求完成本轮后重扫。
同轮逻辑可达 root 集合跨切片复用，head 改变失效；保护释放保守延迟到事件重扫，缓存完成/替换后在 owner 外销毁。
不改变 TileData 的 backing/COW/swap 权威边界，也不从“未投影历史”或缓存命中推导原位写许可。
单记录动态列表、root 刷新、索引分配和总队列预算仍未结清；同步兼容 GC/cold close 不冒充已完全增量化。
67 §26 明确 root 接入资格不取决于物理 registry 是否尚未删除：只有 current、snapshot 保留或 active transaction base 可接入。
最后保护释放后，旧 epoch ID、finished transaction 和裸 metadata snapshot 都不能重新取得其历史能力；判定和加保护与发布/释放同 gate。
`rootCount/immutableRoots` 仍计物理 registry（含退休积压），不是可访问历史数。reachability 只遍历 distinct 合法 roots，
不把退休树当像素存活依据；CPU pin、generic lease、captured overlay token 和 GPU/I/O last-use 的精确版本保护仍须独立检查。
native guard 继续持有所属 View，故 guard 未释放时仍有 root retention；通用 lease 本身不授权重开整个旧 epoch。
worker 不再把清空 root/finished-transaction 队列作为像素回收前置条件；逻辑资格既已同步更新，各预算可同轮推进。
67 §27 的 root/事务退休链接内嵌于已有 registry record，发布和最后保护释放无需扩展额外队列或去重集合；
用 identity 而非 value 地址连接，避免 hash relocation 破坏退休链。物理析构与 worker 调度成本仍另计，不是整个提交免分配。
这一接入约束不禁止新 current 读者，不签发原位许可；exclusive-immediate 的 capture fence/不可失败提交或 recoverable-before 仍必需。
67 §24 的正常 packed write 直接消费 native mutation guard，共用 §20 的完整范围保留、事务/私有取消协议。
一次 View 作 no-op 比较，部分 preserve、整页 discard；比较读 pin 不跨 writable acquisition。写体/范围等待退出 DataManager 锁，
成功后只刷新 changed keys；live legacy borrower 在开始前选兼容路径。§24 阶段 discard 仍有默认初始化，不是零准备成本。
67 §25 的正常 packed 整页块改用同步完整输入 `overwritePage`：借用输入仅在调用内有效，provider 在注册之前直接初始化独立 TileData，
不先 default-fill，也不复制旧页；不是暴露未初始化 guard 或共享 caller memory。普通 discard/default-preserve 保持原契约。
同段 pending 重用及失败取消仍由 canonical owner 决定；没有能力的 provider 采用已初始化 fallback，有能力但失败不得重试其他路线。
该入口依旧可取消、可属于 history 或共享匿名事务；不因没有现成 reader 就发原位 permit，全部 fallible 发布工作尚未提前完成。
67 §16.5 的 owner ledger 将已 detached retirement 从恢复阻塞项中排除，但继续保存全部退休债务并要求 close drain 成功；
不能让无关回收随机拒绝 undo，也不能丢弃未确认释放的记录。
mutable preparation 不可消费可能共享的 legacy payload seed；§17 通过显式 source 区分 immutable alias 与 independent writable copy，
不以 generic key mailbox 暂存新段输入；source 初次取得仍可能需要真实冷源控制路径，不能宣称产品复制一律无 fault-in。
session commit 才对各 dirty page seal 一次并切换一次 epoch root。未升级 intent 不产生 generation/allocation/proof；
legacy API 一旦暴露可写 pointer 就按 dirty 处理，不能事后推断 no-op。

> 2026-09-20 版本化落实状态：virgin default read、tiles3 native resident-read cache、two-stage write intent、显式 multi-tile batch、
> whole-tile backing adoption/alias、persistent root 与 history changed-page delta 已进入代码；`CapturedReadView` 在 D7 落实，
> D8已将native pixel guard接入新CPU facade并有独立回归/诊断证据（62）；legacy traversal的统一接入、
> `CpuMutationSession`和owner-issued `InPlaceWritePermit`仍未完成闭环。局部回归不授予完整性能资格。现有同步 adoption 只优化已经
> 完成的 full-tile backing，不能被解释为“任意 resident write 已可原位覆盖”。在 permit 的 capture gate、reader/root
> retention 复验和不可失败 publish 闭环落地前，普通 mutable pointer 仍必须走 COW 安全路径。53 的旧采样发现 delete/trim
> 物化 default backing；随后 D1 已消除删除/restore/revision 切换的新 default payload，并通过结构/正确性复验及前后混合
> stress 诊断（54）。同主干 M/K/E 资格仍未取得，通用 exact default 消费仍可能物化。rollback/rollforward 的 tiles3 index
> 仍全量重建；不能称端到端同构主干。
> D2-A 的 `beginCurrentTransaction()` 已消除匿名事务起点的 owning manifest 导出，捕获和 base retention 同属一个 owner gate（55）。
> D2-B 已接入 owner-held prepared metadata publication 与先安装 metadata 后发布 root（56），不是免全局锁读或生产布局结清。
> D3 的目录一次发布只移除配置锁，六桶未确认收益；该切片 preserve 仍先填默认 backing、再整页 source-copy（57）。
> D4 已将支持条件下的 preserve 改为 exact-source native duplicate，并补实际 payload 计数、安全负例及分支内配对（58）；
> D4当时尚无正式native pixel guard；D8读侧进展见下，mutation session/permit仍未完成。deletion/default sentinel必须覆盖完整生命周期，history delta必须贯通adapter。
> D5 同源 upstream 窗口吞吐确认暖管理与真实写仍有差距（59），不把底层复用等同于整条管线同构或正式资格。
> D6已压缩completion完成覆盖/非成功状态，保留精确查询和pending gap；真实写只见局部收益（60），不是原位/guard完成。
> D7 归档版本已实现 captured identity/surface view 及CPU只读facade一致性，其pixel仍走generic lease；单页吞吐慢化23%–25%（61）。
> D8新facade的native guard与generic访问/transfer/retire已共享allocation-local gate，guard先unpin再release root；
> CPU历史GC依赖retained root避免提前丢弃版本，future eviction/异步handoff仍须另补等价协调。多个record alias同一payload不产生独占permit。
> D8暖读收益与真实写慢化2.3%–4.8%分别保留；根因尚无分段self证明，不能用零request或读倍率抵消写侧反证。
> D9已把candidate建立移到首次native读，写/generic入口不再预建，exact replica在安装前复验；共享gate不变。
> 相对D8收回部分写成本，但冷读成本转移、暖读/rect负偏移和直接D7真写残余仍未关闭；不授予按需cache最优布局资格。
> D9证据见[63](archive/br1_pre_m6_20260925/documents/63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md)；D10已分离暖cache查询与冷副本发现，保留上述gate，
> 冷miss增加一次shard查询。暖K16 guard/session部分改善，直接D8的宽格式/冷读及直接D7真写残余仍未关闭；局部析构不等于后台drain。
> 读侧证据见[64](archive/br1_pre_m6_20260925/documents/64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md)。D11 已接通生产 writeBytes 的安全 COW 原生写段，
> 同页复用、段末 seal，无 generic write request；但仍非原位 permit/短发布，有单页写性能反证，见
> [65](archive/br1_pre_m6_20260925/documents/65_br1_native_cpu_mutation_segment_20260920.md)。当前状态见52的1.15/11；旧报告保留各自版本边界。

> D12增加内部 allocation physical claim，见[66](archive/br1_pre_m6_20260925/documents/66_br1_physical_exclusivity_prerequisite_20260920.md)。D11段内保持的是
> binding writer 排他与 TileData 防换出 pin，不据此证明跨全部 alias 的物理独占。D12不自动授予原位写：已知refs/users的
> owner保护、legacy write-intent pin移交、old-root/capture gate与首字节后的恢复/发布协议仍须一并接通，生产暂保持安全COW。

## 6. 把 COW 映射到 Generation

现有 COW 的核心不是“复制 CPU tile”本身，而是旧内容引用必须在新写入后保持可用于 reader/undo。

目标流程：

```text
Published G points to PageVersion/TileData A
-> acquireWrite reserves G+1
-> first write captures/retains A as before generation
-> writable replica B prepared
-> producer writes B
-> page G+1 becomes Prepared
-> transaction/ImageEpoch manifest atomically publishes G+1
-> A remains referenced by memento/readers or becomes reclaimable
```

优化：

- PageStore 的 store-scoped `KisPageWriteCoordinator` 为每次 first-write 生成内联 `KisPageWritePlan`；session 持有 write set，
  资源所有权由 move-only `KisReplicaHandoffClaim`/`KisPreparedMutationCommit` 承担。若 CPU replica 是 authority、allocation 可写且
  物理所有权可安全转移，选择 `HandoffRecoverable` 或 `HandoffCommitOnly`，把 allocation 从 G 原子解绑并绑定到 G+1；
  逻辑上仍发布新 generation。旧 G 仍可观察、操作可取消或发布仍可能失败时选择 `FreshCow`；完整最终输入选择
  `FreshPayload`；删除/default/alias/no-op 选择 `SemanticOnly`。调用方和 provider 不持有公共原位许可。
- `HandoffRecoverable` 必须已有独立 exact before；`HandoffCommitOnly` 必须关闭旧 root capture/read acquisition，并只允许
  全部预检后首字节起不可失败的受控内部 kernel。无 before 的普通多页 Prepared transaction、长 session、裸 mutable
  callback 和可失败 producer 不得 handoff。`usersCount == 1` 只是物理证明的一项，不能代替 canonical owner 判断。
- 同一 `KisPageMutationSession` 第一次写 PageKey 时最多执行一次物理 COW；后续 tile lock 复用相同 pending generation 和
  writable replica。tile `unlock()` 只释放局部 guard，不得隐式 commit epoch。
  复用限定在同一未发布段；需要中间可见性或外部 exact reader 捕获结果时显式 seal/发布并分段，后续重新取得
  writer/COW 资格。history transaction 可包含多个这样的段，不能借 first-change memento 合并来沿用已发布段的可写授权；
  新段重新选择 write plan，符合上述 handoff 条件时仍可安全复用物理 allocation，详见 52 的 3.2–3.3 和 68。
- 只取得 write intent 且未暴露 writable pointer 的 page 不分配 generation、不复制页面、不生成 proof；已暴露 pointer
  的 legacy write lock 按 dirty 处理。
- UMA shared arena 可以 copy-on-write 到另一 shared page。
- dGPU 可以 VRAM copy、RAM existing base 或 journal replay建立 before-image。
- 优化不能让旧 generation 在 publish/undo 前失效。
- current、retained exact history、active pending、in-flight、retirement slack 与 optional cache 分桶计量；后五类受明确
  hard/soft budget 和压力状态机约束。后台退休不能作为越过 backing 硬上限的理由。

D4 native 初始化已按 [52 的 3.2.1](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md#321-exact-source-直接初始化-native-cow-backing)
接入：兼容且就绪的 exact source 直接初始化独立新 backing，不先 default-fill 再覆盖；provider 能力/epoch、source pin、
writer/transaction 复验、失败清理与旧版本保持仍是硬约束。复用 `duplicateTileData` 不授予原位写权限，也不代表通用
request/owner gate 已退出热路径。预克隆的后台复制、reserve 与回收必须可计量，不能将前台少一次 memcpy 写成整个生命周期零复制。

## 7. 吸收 `KisMementoManager`

### 7.1 Memento 内容

PageStore-aware memento 记录：

```text
SurfaceId
Transaction/RevisionId
PageId -> BeforeGeneration
PageId -> AfterGeneration
DefaultPixel/Extent metadata generations
Snapshot/retention handles
Recoverability ticket
```

同一个 mutation/undo transaction 对同一 PageKey 只记录第一次变更的 BeforeGeneration，并在结束时记录最终
AfterGeneration；这吸收现有 memento 的 first-change delta 优势。memento 保存 PageVersion retention，不复制一套平行
tiles3 authority，也不要求每次 write lock 复制整页。

### 7.2 Rollback/Rollforward

- rollback/rollforward 创建单调的新 ImageEpoch/commit sequence，原子切换到 before/after retained root 的 exact PageVersion；
  可以重新选择旧 generation，但新写 reservation 的 generation 高水位不回退，旧 handle/retention 校验不得绕过。
- 需要重新执行像素的 journal replay 走正常 mutation/new-generation 协议，不与纯历史 root restore 混为一个成本桶。
- 操作通过 PageStore，不能直接替换 GPU/CPU 私有 tile 指针。
- iterator oldData 必须选择操作所捕获的事务 base；无 memento 的 writable oldData 保留 current backing 别名语义。
  已迁移独立只读 H/V/random 与 wrapped peers 使用固定 current/before View 和有界 pin cache，不强制走 generic snapshot lease。
  缓存淘汰/reset 不刷新可见性。活跃同线程 legacy writer 的重叠读仍为兼容观察，不是 immutable snapshot；
  不得以新读构造为由隐式 seal/unlock 并撤销调用方裸写指针。此缺口与后续 mutation 迁移见 [67 §11](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#11-2026-09-21生产-iterator-与-planar-读作用域)。

### 7.3 与现有测试兼容

BR1 首先在纯 CPU replica 上重现现有 memento、iterator、clone、copy、frame、default pixel、extent、purge 行为。
没有完整测试通过前不接 Vulkan replica。

## 8. 吸收 `KisTileDataStore`

`KisTileDataStore` 从“全局 CPU tile data 容器”演进为 PageStore 的 RAM/CPU replica allocator/store：

- `KisTileData` 获得稳定 PageVersion/replica metadata，或由新的 RAM page object取代；
- pooler/swapper 通过 Residency policy 申请 authority handoff，不直接换出正在 lease/in-flight 的数据；
- memory statistics 纳入 canonical、snapshot、replica、compressed/SSD 维度；
- `ensureTileDataLoaded()` 变为 CPU read lease/materialization，而不是调用者直接操作 swap lock；
- duplicate/free 服从 generation reference/lease/ticket。

不允许另建 `VulkanTileDataStore` 与其并行。

## 9. 吸收 `KisSwappedDataStore`

SSD/swap 详细设计见 [26_p0_replica_uma_dgpu_ssd.md](26_p0_replica_uma_dgpu_ssd.md)。核心要求：

- 由现有 swap 能力演进为统一 SSD replica provider；
- record key 从 tile pointer/allocator chunk 提升到 SurfaceId/PageId/Generation；
- append-only segment + checksum + atomic index commit；
- CPU和Vulkan页面使用同一 store/index/budget/GC；
- 不新建 Vulkan L3 文件或独立 SSD cache。

## 10. Default、Extent、Purge

### Default page

- default pixel 具有 format 和 metadata generation。
- 未分配 page 的内容由 default generation 定义。
- 任意数量的空白坐标读取共享 surface-level virtual/default sentinel；不得为只读 default 命中创建 PageKey、
  PageVersion、replica、request ledger 或物理 allocation。
- 第一次实际 dirty 写才把 default sentinel 实例化为页面；未修改的 write guard 仍保持稀疏。
- full-page default clear、trim/remove 和 restore-to-default 提交 absence/default 语义 delta，不为删除新建像素 allocation/fill。
  default 内容绑定捕获 root 的 format/default revision，不能用最新 default 替代历史内容；必要历史 identity/高水位 metadata
  与像素 backing 分开，virgin read 的零坐标记录要求不因历史保留而放宽。
- 当前 D1 允许 Published/Historical default 以空 replica set、无物理 authority 存在；通用消费可以按需附加 exact backing。
  这是过渡实现，不替代目标 native shared-default read 的零页面实例化与长期 metadata 有界门禁（52/54）。
- GPU materialization 使用 codec/clear kernel生成精确 default，不能固定 clear RGBA8 透明。

### Extent/Region

- extent/region 是 surface metadata revision。
- 驻留 replica 集合不能反向决定 extent。
- production extent/region 由 changed-page delta 与空间索引增量维护；普通 commit 不得扫描完整 epoch manifest。
- crop/extend 产生 page/version/ref 变化，并保持 memento/reader 可见性。

### Purge/Clear

- clear 是逻辑 mutation，但不等于无条件物理写：整页 default clear 删除映射并保留必要历史；相同内容可 no-op，已知
  non-default 整页 uniform fill 可共享 immutable backing。partial/真实像素修改才按写协议处理，必要时 first-write COW。
- purge 只有在历史、lease/native guard、physical pin、异步 last-use 与相关 replica 引用满足释放条件后才能回收。
- derived invalidation 与 canonical purge 分离。

## 11. SurfaceFormat

每个 PageVersion 绑定完整 `SurfaceFormat`，不是只有 pixelSize：

```text
KoColorSpace identity/revision
channel model/order
channel type/bit depth
pixel stride/alignment
alpha presence/type/premultiplication
endianness/packing
default pixel bytes
codec id/version
```

格式设计详见 [29_p0_surface_format_lod_capabilities.md](29_p0_surface_format_lod_capabilities.md)。

## 12. Derived Surface

derived surface 也使用 Surface/Page/Generation/Lease，但：

- 记录 dependency generation vector；
- 无文档 authority；
- 压力下可丢弃；
- rebuild/publish 不能改变 canonical source；
- SSD 缓存只有在策略认为重建昂贵时才可使用，且仍不是 canonical document record。

## 13. Lock 与状态提交

- PageStore 按稳定 PageKey hash 分片；单页 transition 只短持一个 shard lock。
- scope 内 resident CPU 命中使用 page-local pin/lock 与 epoch-tagged cached handle，不取得 PageStore 全局 mutex；
  operation 的 root capture/release 与 root 发布允许短 gate，provider/session registry 等冷路径另计，不能扩成逐 tile
  全局串行访问。首次 binding/shard 查找与暖命中按 39 的 5.12 分开记录，不因锁短或局部化而免除 M/E 成本。
- 多页 operation 按稳定 shard 顺序预留 intent，并通过 immutable transaction manifest 提交可见性，不长时间
  持有多 shard lock。
- acquire request 不持锁等待 IO/GPU。
- completion callback 先校验 operation/page generation，再短持锁 publish。
- 不能持有 image/node/UI lock 等待 lease ready。
- existing swap lock 逐步收口到 replica provider 内部，不暴露给上层 accessor。
- 相同 `(PageVersion, target domain, capability, provider epoch)` materialization 必须去重。
- physical slot 使用 allocation generation 防止退休/复用后的 ABA；旧 completion 不得命中新 allocation。
- provider access 必须可由 guard 内 opaque token O(1) 解析；禁止按 active lease 数量线性扫描来把 pointer 映射回 tile。
- epoch production root 采用 persistent radix tree/HAMT/B-tree 或等价结构共享映射；reference 使用的
  `QHash/QVector/sort` 不能进入 commit/read 热路径。K 个 changed pages 的 commit 应为 `O(K log N)`，而不是重建、
  导出或扫描 N-page manifest。

## 14. 实现路线

### PS0：事实与映射测试

- 记录现有 tile/COW/memento/swap 行为测试。
- 建立 SurfaceId/LogicalPageId 与现有 tile col/row 的映射。

### PS1：CPU-only generation core

- Page record/state machine/request/lease。
- 分片 metadata、transition completion queue 和 materialization dedup。
- transaction manifest、immutable image epoch 与随机完成乱序 reference test。
- 现有 `KisTileData` 作为 RAM replica。
- default/extent/clear/copy。

2026-09-19 已完成功能/正确性 cutover；但 2026-09-20 差分审计发现通用 lease/control path 被用于每次 resident
CPU tile access，导致数量级性能和稀疏性退化。PS1 的语义子项保留关闭，生产布局/快路径子项并入 BR1-PERF，执行见
[52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)。

### PS2：COW/memento

- usersCount/oldData/memento revision 映射到 generation retention。
- rollback/rollforward 与现有像素一致。

### PS3：统一 tile store/swap

- `KisTileDataStore` 纳入 replica/lease。
- `KisSwappedDataStore` 先接入 exact-generation provider seam，并用 in-memory/reference record 固定失败语义。
- BR1 不重复实现完整 durable segment/index；append segment、checksum recovery、cleaner/GC 与跨域压力在 BR3 的
  SSD0–SSD4 关闭。

### PS4：Async access

- request/resolve/continuation。
- CPU iterator session。
- 后续 GPU provider interface。

### PS5：Canonical cutover

- 所有 `KisPaintDevice` 操作通过 PageStore facade/core。
- 删除 parallel Vulkan tile authority。

PS1–PS5 的功能/正确性范围于 2026-09-19 形成证据；resident CPU 快路径、virtual default、mutation scope 和
persistent epoch root 必须在 BR1-PERF 关闭后，BR1 才整体结清。BR3 才实现 durable SSD
segment/index/checksum/cleaner 与跨域 replica。

## 15. 验收门槛

- 纯 CPU Krita tile/COW/memento/swap/iterator/save 测试全部保持。
- 一个 PageKey 只有一个 PublishedGeneration 和一个 writer。
- 写失败/取消不污染旧 generation。
- swap/SSD 失败不释放最后 authority。
- CPU/GPU/derived 都通过 lease，不直接改 dirty/tier。
- PageStore 使用现有 logical tile identity，不把 sparse block 当 page。
- production provider 与无 GPU reference model 使用同一 transition 语义。
- 空白/default 读取不实例化 PageKey/PageVersion/replica，物理像素 backing 为 O(1)。
- resident CPU read/write 命中不建立 heap request/lease、不进入全局 request map、不扫描 provider active lease。
- 同一 mutation 的同一未发布段对同页最多一次 generation reserve、一次必要 COW、一次 seal；tile unlock 不隐式 commit epoch。
- PageStore 私有 write-plan selector 在 recoverable/commit-only 条件成立时允许移交物理 allocation，同时必须发布新的逻辑
  generation；普通多页 Prepared transaction 在没有 exact before 与不可失败发布链时仍须保留旧 G。
- 普通无旧值保留的 resident write 应实现零 before-image copy、零新 payload allocation、零退休 payload；这些指标分别
  计量，不用笼统“zero-copy”替代。必要 COW 每页每个业务 mutation 至多一次。
- current、retained history、pending、in-flight、retiring backing 有精确字节 ledger；压力下按固定顺序回收/降缓存/换出/
  背压，达到硬上限返回 `ResourcePressure`，不无界新增 backing。
- production epoch root 不使用 reference `QVector/QHash` 全量 rebuild/sort；commit 随 changed pages 而非 manifest 总量扩展。
- CPU stress/iterator/accessor 性能达到 52 的 upstream 差分门禁。
- stale completion、provider epoch 和 allocation ABA 被稳定拒绝。
- undo/save 通过 transaction/image epoch 看不到多页半提交状态。
- 不存在第二套 Vulkan tile/SSD/undo store。
- 4/8/16 字节及更多格式 identity 不被压成 RGBA8。

### 15.1 BR1 发布候选存储落实（2026-09-21）

生产 metadata 的普通发布已为 existing-version Historical 变化预构造可移交的 ordered-index node；bounded fused path 预构造完整
record/index set 后交换。安装仍先完成全批 claim 与动态事实复验，失败不暴露部分 metadata。实现与证据口径见
[67 §28](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#28-2026-09-21metadata-候选持有发布所需存储)。

这只减少发布区的已知工作，不改变本节原位写门槛：新 default/descriptor storage、capture gate、旧 View/alias、abort 恢复、allocation
identity 移交和不可失败 root publication 尚未闭环。CPU 路径继续 COW，不能把“candidate 预构造”表述成“已获物理原位许可”。

后续 [67 §29](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#29-2026-09-21新增-default-record-的候选存储与容量准备)
已补齐新 default 的 owning record node 与 exact/slot hash capacity 准备，不再把该 record node 列为安装期已知增长点；descriptor、
capture/rollback、allocation retag/binding 失效及完整不可失败发布仍保持开放，原位许可结论不变。

[67 §30](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#30-2026-09-21descriptor-容量准备与解锁期变更复验)
又将 default descriptor 的 hash growth 提前到候选准备，并以 owner revision 防止解锁期间容量被语义变化消耗。reserve 仍持 owner gate，
completion/cleanup/capture/rollback/retag 仍开放，故不改变本节原位 permit 门槛。

[67 §31](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#31-2026-09-21publication-cleanup-所有权移出-owner-gate)
已把 publication candidate 与 fused 旧 record-set 的最终析构所有权移到 owner gate 外，并在 commit 开锁前先保留新 epoch，避免 cleanup
间隙让刚发布 root 失去保护。该析构仍同步计入 E，mutation 路径与预算队列尚未统一；capture fence、可恢复 before/不可失败提交、
allocation retag 和旧 binding 失效仍开放，因此 physical claim 仍不能成为生产原位写授权。

[67 §32](archive/br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md#32-2026-09-21分批-metadata-cleanup-与预完成-host-evidence)
把大 publication/mutation cleanup 接入页单元/时间协作预算，并让 wait/close 可显式 drain；小候选仍锁外同步。同步 CPU producer 共用 configure
时已终态的 host evidence，最终发布不再分配 completion ticket。PageStore 其余候选容器、capture/rollback/retag 仍开放，故原位 permit
门槛不变；共享 host ticket 只证明“无异步工作”，绝不授予物理 backing 写权限。

### 15.2 写侧最终结构（2026-09-21）

[68](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 已冻结 metadata stable-slot arena、store-scoped coordinator、
内联 plan/claim、两类 handoff、低成本 capture gate、provider transfer 契约、硬 backing 预算、压力响应、测试矩阵和 M0–M8
清理顺序。arena 与 allocation-free publication 是 handoff 前置。当前代码仍使用独立 backing/COW；§15 新增门槛
是后续完成条件，不是实现或性能通过声明。只有 write-plan/handoff、所有生产入口、tiny-budget 压力测试和 M/K/X/E 均通过后，
才能删除旧公开 permit 草案与永久独立-backing 快捷路径。
