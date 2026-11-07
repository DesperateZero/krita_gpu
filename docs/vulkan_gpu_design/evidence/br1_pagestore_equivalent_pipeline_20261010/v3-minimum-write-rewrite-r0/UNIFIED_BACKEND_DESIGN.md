# 新结果协议的完整后端能力设计（105）

日期：2026-11-04。审查源码：0fd96f2fa3f24e70c1652ea17b8cc87192acf6d2。

本文件是原 [BLUEPRINT §105](BLUEPRINT.md#unified-backend-105) 的详细规范；进度、修改索引和验收状态只保存在原 [MATRIX.json](MATRIX.json) 的 unified_backend_extension_105，不另建进度账。CPU 生产集成已经完成；本文件完成后端扩展的设计，不声称 GPU/UMA、多副本或文档级统一提交已经实装、计价或通过门禁。

当前 CPU 价格、合同和失败证据以 [生产报告](write-unit-accounting/native-result-construction-104/production-integration/REPORT.md) 为准。0fd96 的 H1 暖写为10.447100M／1024页结果，完整用例40.415999M／2.7628ms；它不是以下能力扩展后的报价。不得把原21.526595→10.447100M的旧收益再次领取。

## 1. 范围与设计裁决

完整责任是：规范页面/格式 → 结果准备 → 真实物理权限与资金 → CPU/GPU/IO生产 → 共同可见切换 → 所有读者/历史/派生消费者 → 迁移、取消、恢复、末次释放。保持CPU/GPU、RAM/UMA/VRAM/SSD、后端切换、多文档、多画布、undo/save/clone/default和失败语义。

本包定义这些消费者所需的完整合同，不把全部笔刷kernel、所有图算子或所有设备的驱动实现列为已完成。每个实际后端在能力兑现前保持Unavailable/Unsupported；公共接口不能以占位成功代替真实服务。

选择以下形态：

1. 一份backend-neutral结果协议；现有native成为其CPU执行入口，generic成为其异步访问入口。两者共享事实、权限和终结，不能分别拥有页面真相。
2. 原Body/Row从意图到接受保持唯一待完成结果；只有真实异步、导出或保留事件增加相应寿命。
3. 逻辑结果、内容承载关系、物理allocation、执行后端四者分开。普通CPU单副本保留内嵌表示，禁止每次写增建独立Version/ReplicaSet对象。
4. 采用文档级epoch与按可见区间保留的页选择，配合持久化surface元数据目录，形成等价的不可变PageKey映射；不重新构造逐页publication manifest。
5. provider保留实际分配、访问、传输及终结责任；共享预算服务和SubmissionCoordinator保留；旧private/seal/publication核心不作为接入桥。
6. 对新增能力分别计价。CPU路径功能等价回归、GPU真实能力、完整性能和最坏上界分别验收。

第4项是对旧33 §6.1“每次提交逐页persistent map更新”实现选择的明确调整：保留不可变root/exact版本/跨Surface原子可见合同，采用版本区间表达同一个映射。它不是放宽为可变head读取。必须先通过§6及§16的反例验证，不能因为名称叫ImageEpoch就授予等价。

~~~mermaid
flowchart TD
  I[公开意图与冻结route] --> B[唯一原Body/Row及before]
  B --> P[原资源能力与正费用准入]
  P --> C[CPU同步生产]
  P --> G[GPU真实提交及依赖]
  G --> T[受信任ticket完成]
  C --> R[同一原结果Ready]
  T --> R
  R --> A[全批验证及可撤销预装入]
  A --> H[唯一文档root切换]
  H --> V[当前读 / 历史 / 保存 / exact访问]
  H --> D[原变化事件 / 图与显示]
  V --> M[按需物化同代副本]
  M --> V
  B --> X[取消意图]
  X --> F[实际在途完成与末次释放]
  V --> F
  D --> F
  F --> E[原资源终结 / 真实退款]
~~~

图中的物化只改变副本关系，不回到新内容发布链；取消已经提交的GPU工作必须经过真实完成，不能直接到退款。

## 2. 当前缺口和闭环目标

| ID | 当前事实/缺口 | 本设计的闭环 |
|---|---|---|
| UB01 | native组合根直接创建Tiles3 provider | 显式DocumentStore归属；CPU/GPU入口同一owner，独立PaintDevice使用同构单Surface owner |
| UB02 | provider全局同步标记；nativeCpuMutation要求CpuRam；后台退休要求同步provider | 按操作、storage domain与access kind声明能力；同provider可同时同步CPU访问、异步GPU生产/退休 |
| UB03 | Selection直接指向一个CPU Resource | 原Resource控制体演进为稳定内容承载控制体；首物理成员内嵌，真实多副本才展开 |
| UB04 | 一个DataManager内的epoch/all-D接受 | 文档级root、跨Surface原子可见、epoch capture/late reader与成本闭环 |
| UB05 | deferProducer只发行HostLogical票据 | 真实GpuTimeline/IO/CPU来源、提交接受点、可信完成和取消后在途寿命 |
| UB06 | layout、64×64紧密CPU stride、minimumByteSize直接进入访问/费用 | 逻辑64×64与物理layout/slot/arena/sparse粒度分离；实际容量计费 |
| UB07 | CpuResidentBinding的排他/读者事实 | 统一物理访问事实；UMA CPU/GPU pin、cache/order和retirement同一寿命 |
| UB08 | CPU RAM/SSD换入换出已有；GPU物化未接入 | exact materialization、去重、跨provider传输、预算峰值、失败和迁移完成 |
| UB09 | 本地/父级账与资源类别已有 | 多域、多副本、共享arena、alias的唯一收费与类别变更 |
| UB10 | CPU自动终结已有 | GPU last-use、IO、binding snapshot及关闭/设备失效共同终结 |
| UB11 | CPU快照/历史/恢复已有 | 统一文档root、prepared导出、跨Surface alias、undo/save/恢复 |
| UB12 | 实际GPU session仍不接收业务 | route冻结、切换/设备重建、可恢复journal和安全退回CPU |
| UB13 | graph/residency/composite接口独立存在 | 变化事件直接来自原批，derived发布/失效与canonical权威分开 |
| UB14 | generic Store核心仍独立服务公共合同 | 迁移所有实际消费者，删除双权威与旧内核；真实边界仅作薄适配 |
| UB15 | CPU三方净价有效，扩展价格未知 | CPU回归和新增能力分别联合计价；固定研究、明确停止，不移授旧收益 |
| UB16 | 旧文档仍引用private/proof和逐页root内部形态 | 接口映射、源码索引、能力/失败矩阵与主动文档路由一起校正 |

## 3. 权威事实与最少表示

以下是逻辑类型，不要求每一行对应堆对象或新增manager。

| 事实/表示 | 唯一写者、读者 | 寿命与表示要求 |
|---|---|---|
| DocumentId/SurfaceId/PageKey/格式修订 | SurfaceRegistry；所有消费者读 | 文档/Surface建立一次；格式、default、presence是root可见元数据 |
| ResultStamp = PageKey + logical generation + default/format revision | 原页代分配器；读/写/历史/图依赖消费 | 单调发行、不回滚、不因迁移发行；不是物理handle |
| ResultRef = ResultStamp + ContentRef或VirtualDefault | 原Row、当前Page选择、真实历史Edge | 作为原位置内的值；普通结果不增建独立Value对象 |
| ContentRef = 原Resource控制体 + content incarnation | 共同结果owner | 保持exact内容与物理成员的联系；alias的逻辑Stamp可不同但共享ContentRef |
| PhysicalMember = provider/device/slot generation + layout + storage domain +真实用量 | provider发行、共同资源责任认可 | 首成员内嵌；实际第二副本才分配扩展；provider不得决定当前逻辑版本 |
| Ready/last-use/访问权限 | 真实provider/registry产生，资源门统一消费 | 访问期间保存；逻辑引用、resident pin、GPU last-use不能互相替代 |
| Body/Row | 原操作owner | 已选源、目标、writer claim、生产完成及费用计划只存一份；Ready重试不重做producer |
| DocumentRoot(epoch, persistent SurfaceState directory) | 原ImageEpoch owner，演进而非外套另一个owner | immutable root；PageKey映射由root epoch与稳定页区间共同确定 |
| RootRetention/ExactCapability | root capture或真实导出发行 | 真正读者/undo/save/跨窗口依赖持有；数字epoch/裸stamp不授予读取 |
| BindingSnapshot | GPU编译批持有，provider解释 | 真实消费者需要的不可变最小投影；不能修改逻辑结果或成为第二目录权威 |
| 费用/退休债务 | 原预算与原Resource | 分配/类别/域变化时更新；通知队列只保存待推进节点 |

### 3.1 内容关系与物理寿命

当前Resource本来就跨多次写复用。扩展沿用这个受控控制体及池，不在它外面再套一份永久ContentOwner。

单副本CPU的ContentRef直接解析内嵌成员。存在实际第二副本时增加ReplicaMembers扩展；首副本物理释放后，原控制体仍可作为被引用内容的稳定锚点，内嵌成员可为空。物理字节退款不等于控制体元数据退款。最后逻辑引用/物化/访问全部结束才归还控制体。

同一内容被多个逻辑页alias时，物理容量只计一次；不能以某个PageKey的writer唯一证明物理独占。物理token只标识allocation与incarnation，不能继续把一个可变handle.version当作所有alias的共同逻辑身份。逻辑exact版本在owner签发访问授权时验证，provider验证其自身mint identity、物理incarnation、layout与访问权。

控制体仅在所有旧内容引用和使用边归零后才能改变content incarnation。recoverable handoff若同时保留旧逻辑内容，则旧锚点继续指向受保护的before成员，移动出的物理成员加入新结果的原目标控制体；这是两个真实可观察内容，不允许把旧锚点直接retag。普通空闲复用无旧观察者时继续复用原控制体，不因此新增每页版本对象。

### 3.2 不保存的重复事实

不保存第二份当前generation、第二份private完成标记、每层已验证完整descriptor、按每次写重建的provider登记、每CPU操作的空GPU票据、同一UMA存储的CPU和GPU两份payload费用。可推导的dirty/authority状态不允许由多个后端独立修改。

## 4. 对外接口与责任接受点

接口名称是目标语义草图；优先原位演进现有公开类型，不发布第二套并列API。返回类型必须区分Ready/Pending/Conflict/Rejected/Closed，原因中区分格式不支持、资源不足、真实冲突与设备失效。

~~~cpp
ProviderRegistration registerProvider(DocumentStore&, Provider&, OperationCapabilities);
RootLease captureCommitted(DocumentStore&);                    // O(1)取root，登记O(log V)
ResultBatch beginResult(DocumentStore&, MutationIntent, FrozenRoute);
PreparedAccess prepareInputs(ResultBatch&, ExactReadRequirements);
PreparedTargets prepareTargets(ResultBatch&, WriteRequirements);
CpuWriteAccess borrowCpuTarget(ResultBatch&, RowId);
GpuBatchInput compileGpuTargets(ResultBatch&, FrozenDependencies);
SubmitOutcome submit(GpuBatchInput&&);                         // 不可伪造的提交回执
void complete(OriginalOperation&, VerifiedCompletion);         // 不重新构造结果
AcceptOutcome accept(ResultBatch&);                           // Ready保留/共同root提交
CancelOutcome cancel(ResultBatch&);                           // 可异步，非强制free
AccessOutcome acquire(RootLease|ExactCapability, Key, AccessRequirement);
Materialization materialize(ExactCapability, DomainAndAccess);
void release(Access&&, LastUseEvidence);                       // host释放≠GPU结束
CommitHandle endStroke(Stroke&);                              // 不host wait/整图readback
CloseHandle close(DocumentStore&);                            // 拒新，存量能力仍合法
~~~

接口合同：

- beginResult只建立原批及真实范围责任，不发行通用逐页事务。输入bytes同步借用仅到prepare调用返回；异步输入必须携带真实拥有者。
- prepareInputs/Targets可返回pending；Pending状态持有同一原操作和continuation，不能靠重复调用再发行一套工作。已取得的前缀由原行负责取消。
- 同页追加未发布写复用原目标；已提交可见段不能沿用旧写权。普通packed CPU写不先捕获整文档历史root，只保留实际before行；需要跨窗口一致输入的消费者才持有RootLease。
- submit的接受点是coordinator已经持有完成记录、资源使用保护和不可变packet。返回拒绝意味着没有提交；发生部分提交时必须返回已接受前缀及对应ticket，不能报“全部未执行”。
- accept成功表示canonical结果已提交，不等于display完成、undo可恢复或文档保存落盘。返回ReadyRetry保留原结果及资金/权限的合法状态；重新准备只发生在取消或输入失效后。
- Legacy raw/iterator仍是CPU同步数据面。缺页/跨域等待由上层可续执行job在进入同步像素段前解决，不能在UI或持有owner锁时阻塞GPU；外部同步工具仅在合同允许的非交互边界等待。
- 旧同步callback若不能中途挂起，必须在进入前声明并准备完整访问region；数据依赖的未知访问须把真实调用者改成有恢复点的job。不能在部分像素副作用后抛出Pending并从头重放callback，也不能用隐藏host wait填补接口缺口。无法满足准备/恢复合同的执行路线在首次写前不授予能力。
- provider注册在对应session epoch内不可变；更换provider/device建立新epoch。注销先拒新，再等待原能力/操作终结，不能使活跃span悬空。
- 所有capability具有owner、document/session generation和范围；不可由裸ResultStamp、ticket数值或外部自行拼出的handle构造。

## 5. provider能力模型与物理接口

替换KisReplicaCapabilities中的全局组合限制。能力按以下键冷注册并验证：

~~~text
OperationKind: Allocate / Initialize / ResolveAccess / Transfer / Retire
SourceStorageDomain? / TargetStorageDomain
AccessKind + Read/Write mode
StorageClass / layout support
CompletionMode: TerminalAtReturn | AsyncTicket
Threading: caller / coordinator / background-safe
Guarantees: exact source, shared backing, initialization, native resident access
~~~

同一UMA provider可提供同步CPU resident resolve、异步GPU写和异步退休；不能因某操作异步禁止CPU直接span，也不能因CPU支持把GPU路径标成同步。capability集合大小不以当前四个domain常量作为未来语义限制；注册是冷路径，热路径消费已经选定的窄表项。

CPU fast entry使用已验证的provider-native能力及原binding直接入口；它与generic访问共用物理门，不通过通用请求堆分配绕一圈。不得以unchecked裸指针作为“快路径”。没有GPU交接的CPU操作不创建GpuTimeline/BindingSnapshot/transfer。

跨provider的transfer通过明确注册的bridge或coordinator执行；同provider不能接受外provider token。物化与写初始化必须区分：ExactMaterialization保持ResultStamp；WriteInitialization只准备原Row的新目标。bridge返回真实source/target身份、layout、完成及失败结果，不可只凭bool成功。

provider冷注册一次声明完整format/layout支持；分配出生验证一次descriptor兼容性。解锁后只复验可能变化的device/provider epoch、incarnation、权限、完成、域修订；真实descriptor改变则产生新修订并重验。不能删除外部不可信输入或真实失效边界的校验。

## 6. 文档级可见性与低成本root构造

### 6.1 不可变映射的构造

DocumentRoot保存全局commit epoch和持久化SurfaceState目录。每个稳定PageSlot保存当前选择及按可见区间索引的真实历史边；resolve(root,key)选择root.epoch对应的结果。surface存在性、格式/default、extent/索引根由root的SurfaceState确定，不能读取当前可变default。

对一个被保留root，以下关系必须不变：resolve(root,key)、surface枚举、absence/default及格式。页索引可增长，但root范围的枚举必须按epoch过滤；新页不能出现在旧root，删除后的旧页不能消失。快照枚举允许按实际需要扫描索引；每次写和capture禁止全图扫描。旧位置何时可回收取决于保留root及原Row/导出，而非仅current为空。

文档root持久目录只更新实际变动Surface的状态路径；页选择映射使用区间算法，不再同时更新一份逐页persistent map。旧root的可读性由RootRetention证明，裸旧root号不能在其退休后重新取得能力。长期undo/save保留一次root；对范围/explicit Prepared读只保留其实际选择，不能扩大为永久整图保留。

publication head自身不算外部历史观察者。否则每次写都会把旧head保留成历史，重新生成D份关系。RootLease的外部保留显式登记，不能采样shared_ptr::use_count推断。普通写的原before保护也不自动登记整文档历史观察者。

取得head及保留原root控制体可为O(1)，有序观察者登记/移除为O(log V)，另计真实控制存储成本；不能把整体capture说成无条件O(1)。全root观察者按epoch索引；SurfaceId不可重用，其出生/退出epoch限定有效观察区间。范围/Prepared导出消费原显式选择集合，按实际项数保留；不能为了支持范围过滤让每次普通页写扫描全部观察者，或把范围捕获伪报为O(1)。

### 6.2 跨Surface提交算法

1. 原批按稳定SurfaceId/PageKey排序取得真实writer claims，保留原before；不相交页可并行生产。跨文档不得作为单一原子写：应在公开边界明确是独立事务或显式跨文档协议，不能暗中扩大本包。
2. 生产全部完成后，锁外准备root持久目录节点、adapter容量、真实变化行和终结空间；以原预算取得正目的额度，保留源收费，禁止净额掩盖峰值。
3. 记录expected document head和retentionRevision；计算真实旧选择保留区间、资源变化及所需保留额度。capture/release会递增原文档retentionRevision。
4. 按稳定顺序取得涉及Surface gate与真实物理validation gate；检查writer、before、provider/device/incarnation、完成和资金计划。provider/IO/queue调用在这些门外执行。
5. 在Surface gate保护下，预装入可撤销的页选择/历史边/adapter引用变化；旧值保留在原Row。此时root仍旧，其他读者无法进入受影响Surface，未受影响Surface结果不变。此段不得free、退款、发通知或修改已提交GPU binding。
6. 最后取得原文档commit gate，O(1)比较expected head、retentionRevision和关闭/route修订。匹配后切换head一次；否则先释放commit gate，按原Row逆序撤销预装入，保留Ready并重算计划。不得重新执行producer。
7. head切换后不再存在业务拒绝点。释放commit gate，在Surface保护下完成预付费用的不可失败结算及原adapter最终发布，再释放Surface/物理门；通知、旧引用释放、实际退休在门外。费用结算在此之前始终保留足够reservation，不提前退款；内部不变量错误不能假装为可重试业务失败。

captureCommitted只短持commit gate，保留head并登记/更新原epoch观察者，随后释放；它从不在该门内取得Surface/provider门。跨Surface读通过同一个RootLease解析各页，而不是分别捕获当前页。

所有公开current选择、raw/iterator及adapter读必须遵循该保护边界。已有exact scope的cached binding可以继续局部pin直接读，因为scope已经固定版本；没有exact scope的缓存必须核对root/版本tag，不能绕过Surface门读取预装入状态。捕获登记所需内存提前准备，root最后释放先从观察者登记退出，再在commit gate外处理页区间和物理尾部。

晚capture若发生在步骤3和6之间，会改变retentionRevision，使提交重算；若发生在步骤6之后，只取得新root。这样无需在commit gate内扫描D行，也不会漏掉原计划之后出现的旧读者。release同样保守触发重算；是否优化单调释放另行计价，不影响正确性。

并发不相交提交若head变化，重建Surface目录增量并复验原before；不重做内容。重叠写由writer/版本冲突裁决，不以最后提交偶然覆盖。重试有明确每次调用上限，超限返回Pending/ReadyRetry由已有事件续跑，不在调用栈无限自旋；一般并发下无固定最坏重试次数承诺。

### 6.3 必须证明的反例

捕获发生于预装入之前/期间/之后；第二Surface最终拒绝；default与删除和写同时提交；旧root在新页创建后枚举；不相交批同时提交；close与commit竞争；最后old reader释放与预算计划并发；root切换后终结拒绝。所有结果只能是完整旧集、完整新集或显式失败，不能出现部分新集。

## 7. 真实异步、GPU binding与提交

原Body表示Preparing、Executing、Ready、Committed或Cancelled这些真实阶段；异步在途保护和用户取消意图分别保存，不能用一个Cancelled值推断物理已停止。CPU同步完成直接置原行Ready；真实异步才发行完成记录。

GpuBatchInput只含执行所需的exact输入/目标、layout/codec、区域与依赖。未提交时可借原Row；提交后packet引用的字段必须冻结，并保持原Body或最小BindingSnapshot活到last-use。生命周期选择须在代码索引中明确，禁止让GPU读取已归还/扩容的Row数组。

实际submit批按队列、provider/device epoch、格式/StorageClass、deadline、权限和依赖分组，不按D除理想批大小。一个submission的ticket可保护其多个成员，但资源使用集合仍必须逐真实成员建立/消费；不能把batch ticket数当作所有页保护成本。

SubmissionCoordinator是唯一queue owner。它在提交前保证completion记录和失败归属可保存；真实GpuTimeline completion由受信任设备源验证，不能调用公共finish(true)伪造。GPU可表达的依赖直接组成GPU DAG，不先host wait再submit。

BindingReady、ProducerComplete、CanonicalCommitted、DisplayVisible、Recoverable分别是不同事实。binding数据可读不证明像素已生成；producer完成不证明all-D提交；图预览若消费未提交结果，必须持显式Prepared capability，不能进入普通save/current读。

取消未提交批可直接归还权限；已提交批禁止复用目标，直到真实完成/设备失效终结证明。迟到成功只能完成该已取消操作的清理，不重新发布。旧device/provider/slot generation的回调不得改变新结果。

## 8. UMA与设备布局

逻辑tile仍为64×64；物理slot/row stride/plane/atom alignment来自StorageClass；sparse块来自设备。禁止恢复MAX_TILES_X/Y对应单张大image、固定8192 dense回退或逻辑tile直接生成sparse bind。buffer slab与软件binding是基线，sparse只是可选provider。

UMA共享slot的CPU span和GPU view是同一PhysicalMember的两种访问。CPU-only时GPU访问状态为空；实际交接才维护执行依赖及cache可见性。同一exact generation可在能力允许且无writer时并发CPU/GPU读；MVP若保守串行必须单列等待代价，不能变成接口永久限制。

统一物理访问门验证：allocation/device incarnation、writer、CPU/native/generic读者、GPU/IO pending-last-use、swap/迁移与retirement。不能以CPU读者为零推断GPU已结束。CPU写后非coherent flush、GPU写后CPU invalidate均按实际访问范围与atom对齐；coherent仍保留执行顺序。

TileData/shared span适配不拥有外部mapped指针的free权；pooler/swapper不移动活跃访问。所有现有硬编码stride和logical minimumByteSize收费点迁移至原PhysicalMember出生layout及实际容量；旧CPU tight layout仍可作为已证明能力的直接分支。

display atlas/gutter/LoD是独立实际消费者：只读exact核心可作辅助副本，派生转换带依赖向量，不替代canonical recoverability。GPU绑定与atlas分配不随每个CPU-only写自动发生。

## 9. 多副本、迁移与SSD

Exact materialization的去重键包含ContentRef/incarnation、目标provider/device epoch、StorageClass与所需访问能力。一个真实producer可有多个等待者；取消一个等待者不取消仍被他人需要的工作。最后等待者取消后，已提交工作仍须物理终结。

迁移步骤：选定可恢复源 → 固定其真实寿命 → 正目的预算及目标容量 → 真实transfer/IO → 验证完成与layout/exact内容 → 在原内容成员集合登记Valid → 按实际需求切authority → 无其他消费者后退休源。失败保留源，拒绝不能留下已退款的在途目标。

同代副本新增/删除不改变ResultStamp，不发行历史边、不通知像素内容变化。字节相同不代表可以跨格式alias；格式转换进入显式derived/new-result任务。

RAM/SSD现行服务继续复用，但目标SSD record必须具有exact内容/格式、校验、索引提交和崩溃/IO失败语义；CPU swap测试不自动证明全目标SSD合同。GPU不得另造L3。SSD写/索引完成前保留源，读取先取得真实RAM容量及费用；IO ticket只是实际请求，不为resident命中发行。

后端选择使用完整source→consumer关键路径估计。没有适用CPU副本时，CPU fallback也计真实readback；不能拿RAM-ready内核时间作为该状态的CPU价格。每笔结束不自动整图回传。

## 10. 费用、驻留和终结

收费按实际物理存储与管理容量，按角色及domain归类。UMA两种访问不是两份payload；多个逻辑alias不是多份物理申请；RAM与VRAM两份实际副本则必须分别付费。

arena在系统申请时全额进入物理容量账；slot从空闲容量转为Current/Retained/InFlight等角色属于这笔容量内部重分类，不能再向父级重复发行相同字节。未用slack、碎片、staging、binding/command元数据都列账，逻辑payload字节不是allocation价格。共享arena跨文档使用，物理owner付一次真实总量，文档配额按明确归属份额/保留政策约束；份额账不是第二次物理收费。

共享物理内容的默认payer保持原出生owner，跨文档alias只建立真实借用保留边；接收方的逻辑保留配额单独准入，但不重复上卷为process物理字节。出生文档关闭后，该物理payer和必要预算owner仍随借用尾存活。若要转移payer，先在接收方正准入，再原子转移原收费责任；失败保持原归属。若政策不允许借用则实际复制并正常付费，不以换owner名义免除成本。现行父/本地限额、metadata预算、transient版本上限、waiter公平性及动态收紧规则均须在共同预算服务中保留，不能因合并owner取消。

多域迁移保留源费用，先准入目的正额；类别净额不能消掉同时占用的峰值。reservation在物理副作用之前取得，取消后先证明物理释放再退款。retirement债务预付不证明物理可立即复用。

终结条件合取：逻辑current/retained/pending不再需要该内容或已有允许替代；所有真实访问/编译批/binding snapshot/IO/GPU last-use结束；没有迁移或独占claim；authority安全已满足。不同条件由原Resource/成员记录消费，不再建立通用终结事务。

原通知机制接入真实完成与最后保护释放。唤醒仅排队，不在provider回调栈重入owner或预算锁。每pass有界，仍有欠账时由事件/已付continuation保证进展，不依赖新笔迹或手工retry。

close先拒绝新root/写/provider登记，再取消未提交、跟踪已提交、等待实际外部能力结束。现有root/span/ticket不得悬空；可异步返回CloseHandle。device lost使旧device访问不可再发行，实际内存释放须依据设备资源销毁/失效确认，不能把逻辑Cancelled直接当物理完成。

## 11. 后端切换、历史、保存与恢复

FrozenRoute在operation首次写前保存执行后端、能力/格式/资源修订、device/session epoch及恢复策略。当前operation不因profile更新、资源miss或局部失败逐页/逐dab换后端。

正常CPU↔GPU切换先关闭旧epoch，以一致已提交root开启下一epoch；所需内容已有适用副本则直接访问，否则按§9物化。同一UMA内容仅发生访问交接，不换文档或复制像素。

设备失败：冻结该设备新业务 → 原操作区分已提交/已完成/已可见 → 保留CPU/SSD安全内容与before+journal → 在新恢复epoch重建失效内容 → 一致提交恢复结果 → 新ReadyToken允许重新附着provider。禁止清空CPU权威后才尝试回退；不可恢复能力在首次写前拒绝，不在失败后伪造成功。

恢复资格还包含语义可重放性：journal冻结输入、资源/程序版本、随机状态及所需运算语义。不能假定CPU与GPU浮点执行天然逐字节相同；没有满足该操作像素合同的恢复证据时，必须选择真实安全backing策略或在首次写前不授该路线。exact snapshot不能因设备失效被悄悄替换成另一种结果。

undo transaction可聚合多个已提交batch root，恢复是新commit选择被保留的旧结果，不回退generation高水位。undo-before-complete先取消/隔离原在途输出，再按恢复规则发布；不释放还在GPU使用的原目标。

save捕获一个RootLease及authoring/format一致快照，逐需取得exact内容，不追随current、不在GPU stroke结束时强制readback。DurableDocument以保存系统真正落盘裁决，与SSD临时工作集和GPU完成分开。

Prepared导出为真实消费者发行只读capability，跨accept/cancel继续保护其exact内容；它不是普通结果必经proof。clone/alias在同owner可共享ContentRef；跨owner通过真实immutable source import与共享物理收费归属，不能直接复制裸Resource指针。default/clear/trim/absence与历史使用同一提交算法。

显示后端切换只重建view attachment，文档root与内容owner不变。多画布共享document session；不同文档不共享可变页权威。独立PaintDevice接入文档时必须有显式冻结/导入边界，活跃外部快照保持原owner寿命，不能偷换其文档ID。

## 12. 图、驻留与后续完整能力接口

原批提交成功后发行唯一ChangedSet(event sequence, root, old/new ResultStamp, exact changed region)。事件借用原行时必须在行归还前消费；异步消费者需要的最小事件批预先受控付费。不能为了通知重新导出全图或扫描全部页。

提交前准备事件存储；提交后通知失败不能丢失更新。保留原未投递批并由既有scheduler续投，event sequence允许消费者去重；不另建第二份页面状态表。

EvaluationEpoch固定graph/property/context和输入RootLease；derived key包含实际输入版本、operation语义、格式/LoD/region。derived输出使用同一结果/生产完成协议，但发布到derived命名空间及依赖版本；不能改变canonical文档root或成为不可恢复canonical的唯一副本。真实需求的exact auxiliary replica与颜色转换/gutter等derived明确分开。

ResidencyController只提出合法候选及迁移意图；owner复核安全与预算，provider执行物理工作。温度/viewport/预测/CLOCK历史是策略信息，不是第二份authority或释放许可。无实际需求不预建所有域副本。任务图通过exact输入访问、output reservation、completion和ChangedSet连接，不直接操作TileData或Vulkan对象。

非Surface value继续由Value/Resource Store管理。格式codec和颜色语义是冷注册能力，不能只用bpp等价；unsupported格式整操作走合法CPU路径。kernel microtile/工作组大小不是逻辑tile，shader处理次数可按设备选择，不改变逐页COW/undo单位。

## 13. 锁、并发与失败矩阵

目标嵌套顺序：实际adapter/surface gate按稳定ID → 内容/物理metadata gate按稳定身份 → 短文档commit gate。capture仅取得commit gate，释放后才解析Surface。预算reserve、provider执行、queue/IO、回调与最终释放均不在commit gate内；不可失败的费用settlement在head切换后释放commit gate再完成。新顺序须与Tile swap barrier/现有binding及budget路径做真实调用图校验，不能凭本表授予无死锁。

| 失败/竞争点 | 保留事实 | 下一步与最终结果 |
|---|---|---|
| 冷分配/正预算拒绝 | 原before不变，成功前缀留原Row | 归还未执行目标/资金；报告真实拒绝 |
| 物理复用claim拒绝 | 该候选未取得写权 | 退对应份额后按已声明策略Fresh；不得双占未退预约 |
| submit前拒绝 | 原目标可未执行，旧current不变 | 取消或重新排队原操作；不重复发行已取得事实 |
| 分组部分submit | 已接受组/ticket精确记录 | 取消意图保留；接受前缀真实终结后退款 |
| producer失败 | 原结果未Ready/不可提交 | 旧current保留，失败贯穿公开stroke/raw终态 |
| late capture或root竞争 | 原Ready内容及原before | 撤销预装入，重算root/保留/费用；不重放内容 |
| 最后目标验证失败 | 尚无root切换 | 全D不安装，保留合法Ready或显式取消 |
| root切换后清理拒绝 | 已提交结果不能改报未执行 | 原退休债务续跑，用户结果仍成功 |
| IO校验/索引提交失败 | 源authority及在途费用 | 丢弃目标/续处理，禁止提前释放源 |
| cancelled后GPU成功 | 取消标记、同operation/device ticket | 只终结，不发布；防重复callback |
| device lost | 未发布/已发布与可恢复状态分开 | 源/backing/journal恢复；设备存储按真实终结处理 |
| close后晚读者归还 | 外部能力保活原owner | 原通知自动推进末次释放，标准drain可观察 |

## 14. 修改索引、清理与消费者迁移

完整机器索引在MATRIX.json的UB01–UB16，每项含当前路径、符号锚点、原MW映射、删除目标和验证条件。以下为阅读导航：

| 当前位置 | 最终责任/改动 | 必须一起退出的旧假设 |
|---|---|---|
| native/Protocol、State、Write、View | 原结果核心、稳定内容、文档root/区间保留、共同接受 | CPU-only Impl权威、每manager独立canonical epoch、重复root/区间目录 |
| native/Resource、CpuResidentBinding、Tiles3 provider | 真实资源访问/物化/费用/终结 | handle.version等于唯一逻辑身份、CPU读者为零即物理可复用 |
| native/Tiles3、Operations、IteratorReadScope | CPU公共facade消费同一owner | 另建CPU存储、GPU结果强制readback才能进入iterator |
| PageReplicaProvider、StoreTypes、SurfaceRegistry/Codec | capability、layout、物理身份与逻辑权限 | provider-wide同步限制、CpuRam-only native能力、硬编码stride/费用 |
| ImageEpochReferenceModel、PageStore、Metadata/Publication/Write/Read coordinator | 公共合同迁入同一结果协议；reference仅保留为oracle | private/proof/seal/manifest转译链和第二生产authority |
| VulkanPageReplicaProvider、Memory、BindingTable、SubmissionCoordinator、RetirementQueue | 真实设备服务、不可变packet、last-use | 假完成、单CPU completion代GPU、重复device账、按页host wait |
| DocumentGpuSession、StrokeCoordinator、PageWorkCompiler | 冻结route、真实接受与恢复、page批 | 逐dab后端切换、固定ring丢命令、stroke-end整图回读 |
| EvaluationPlanner/DerivedSurfaceCache、ResidencyController、Composite/Display消费者 | exact依赖、变化事件、策略与权限分离 | 独立dirty权威、全图重新投影、derived覆盖canonical |

清理顺序不是先删公共能力：先迁其真实consumer与失败尾部，再删除旧内部核心。原CPU backend/104选择等已完成删除项保持完成，不重新领取。测试也要迁移，不能保留旧测试调用旧生产核心而宣称全统一。

临时桥仅允许留在未交付开发分支；完整联合计价前必须为零。兼容public facade只翻译请求/结果一次，不生成第二事务/预算/发布。故意保留的reference oracle不进入产品调用图。

## 15. 成本预算、研究边界与停止条件

这是能力补齐与协议统一设计，不宣称又有11M可删额。当前CPU责任总价已知，GPU新增服务价未知；旧父桶不能当新能力预算。相对同语义upstream的额外价仍独立。

动作模型使用：D实际结果页、P实际页槽、W实际操作批、S触及Surface、F物理出生、A真实额外副本、R实际历史边、V被保留root/区间规模、X实际迁移及字节、B实际submission组、L实际资源使用边、Q真实重试、T真实终结。

| 工作 | 可审计次数/复杂度方向 | 不允许的放大 |
|---|---|---|
| 原行/页定位 | 当前有序索引O(D log P)，后续消费原位置 | 每层再次按key定位 |
| 共同接受 | D动态目标、至多2D资源变化；实际排序O(D log D) | 批量入口少了就宣称逐页工作为零 |
| 保留 | D次区间资格查询，约O(D log V)，只为R个真实关系安装 | 每个中间结果建立完整历史对象 |
| 文档root | 每次成功批一次head切换，实际S个surface目录路径更新 | 每次写导出全页manifest |
| 物理/副本 | F出生+A额外副本+真实类别/域变化 | 每逻辑写重新注册物理身份 |
| GPU | B真实提交与完成组、L真实使用关系及binding条目 | 无GPU事件时收费；B被理想批数替代 |
| 迁移与尾部 | X真实服务/字节，T末次终结，Q按其恢复阶段付费 | 取消后尾部移出端点、全重试乘完整父价 |

CPU指令报价必须对以上实际实现的互斥工作取得单价与漂移，再求完整总价；wall按依赖关键路径与等待测量，不能把并行阶段CPU价格相加当延迟。暂不发行未知GPU服务的数值上界，也不把次数模型称机器最低价。

有界研究先解决三个会改变设计的未知：

1. root区间构造在多Surface、late capture及adapter公开行为下是否成立，及其相对0fd96 CPU额外总价。
2. 原Resource扩展后的CPU单副本、alias与真实多副本完整寿命价；是否增加每页普遍的分配/查找/宽投影。
3. 真实UMA/GPU提交、权限、binding、取消/失败/终结的联合新增价，而非裸kernel或scalar模型。

先有限模型反例，再构造包含真实储存/预算/adapter/终结的完整候选；不允许完成一个helper就正式计价。选择实际硬件、冻结工作量/样本数/配对顺序/容差后才运行，未知硬件价格不能通过重复调小局部账得到“通过”。

停止并修正同包设计的条件：需桥接旧核心；CPU-only开始生成GPU事务或逐页新Version对象；root capture/保存不再exact；provider无法表达混合同步/异步；重复物理收费；低价依靠漏掉失败/尾部；真实CPU回归未通过适用门。不得将其改名为结构收益后晋升。

## 16. 能力、正确性与计价验收

每项验证要同时检查行为、实际服务命中、完整生命周期和对应计数。CPU M1–M5既有证据仍有效于0fd96；新结构需重新验证受影响合同。M6–M8、GPU/UMA及upstream价格不自动继承。

| 验收组 | 必须覆盖的反例/真实服务 | 放行要求 |
|---|---|---|
| A 文档/身份 | 多文档、跨Surface原子提交、close、格式/default/absence、旧root枚举、重叠/不相交写 | 等价root映射；无半批可见、无跨owner伪造 |
| B CPU等价 | 既有raw/iterator/fill/copy/clone/history、H0/H1、partial/no-op、压力、失败传播 | CPU消费者全迁；旧链删除；完整process/尾部计价 |
| C provider | UMA同步CPU+异步GPU同注册、外provider桥、epoch/ABA、unsupported、真实拒绝 | 能力精确，不能fake ready或失败后静默换路线 |
| D 多副本 | RAM/UMA/VRAM/SSD同代选择、去重、多等待者取消、alias、迁移失败 | 不新建逻辑代，源安全，物理收费一次 |
| E UMA | coherent/noncoherent，真实双向交接，CPU/GPU读写并发/取消，pin与swap竞争 | 同allocation证据，domain-copy计数完整，cache/order保留 |
| F GPU | 多真实提交组、binding未就绪、最后页失败、乱序/迟到完成、取消后在途 | 统一结果；无host wait/悬空binding/提前复用 |
| G 布局/容量 | 多格式/stride、不同atom/sparse粒度、负坐标、大逻辑坐标、无sparse设备 | 不依赖一张巨图或固定tile数；实际容量正确 |
| H 恢复/关闭 | device lost、before+journal、undo-before-complete、save并发、外部能力晚释放 | 可恢复策略真实；自动终结到预算/物理尾清零 |
| I 图/驻留 | derived过期输入、不同context/LoD、事件背压、强制换出、跨画布 | 不改canonical权威，不漏变化，不损坏输入 |
| J 结构/机器账 | 双架、TSAN、真实install分配审计、调用图、删除索引；CPU/GPU服务联合价 | 保持既有适用门；没有未知零价或迁移丢账 |

GPU不能运行的环境只可出具模型/接口/CPU结果，不标GPU能力完成。fake provider可验证状态机，不能证明真实设备同步、缓存维护或性能。

## 17. 实施依赖与完成定义

依赖顺序：UB01–04/06的共同身份、接口和root模型 → UB05/07–10的真实服务闭包 → UB11–13全部消费者 → UB14旧核心清理 → UB15联合计价与UB16文档/矩阵收口。允许增量编译与正确性验证，不允许以阶段结束更换原完整交付范围。

设计交付完成表示责任、接口、算法、失败、删除和验证已明确；模型验证、生产迁移、真实硬件能力与价格各自登记。完整实现验收要求UB01–UB16、所有保留消费者及失败尾部全部结清，且适用门通过；不能凭当前CPU完成率或本文件存在宣称完成。

最终实现必须同时回答：同一CPU工作是否保持低成本；真实新增能力实际增加了多少成本；切换是否保留同一文档和exact结果；所有旧内部生产权威是否退出。任何一项缺证，完整能力包保持未验收。

## 18. 本次设计核验

[可重放核验脚本](unified-backend-design-105/verify_design.py)校验原矩阵16项与MW01–12映射、59个源码锚点的源码哈希/位置、引用文件与未授实现/性能资格状态。

[有限模型回执](unified-backend-design-105/DESIGN_VALIDATION.json)枚举两Surface预装入、两读者capture/read与最终提交的420种合法事件交错，exact读取及完整提交/撤销无反例。删除retentionRevision检查、删除Surface保护两项负对照均得到反例，说明核验能够识别这两个关键错误。

该模型不含真实C++内存序、预算settlement、并发writer、root GC/default枚举、release交错、物理服务或设备失败，不授完整并发证明。其余反例在§16及原UB矩阵保持待验证；本次新增性能过程为0。
