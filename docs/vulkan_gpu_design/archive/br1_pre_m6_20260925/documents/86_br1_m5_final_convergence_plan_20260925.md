> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1/M5 最终收敛方案（2026-09-25）

> 文档角色更新：本文保留为 M5 收敛与退出标准，后文“尚未实施/下一次”均为方案冻结时点。批次实施与修复历史已归档至 87/89；最新 [90](90_br1_m5_baseline_freeze_review_20260925.md) 撤回整体关闭并新增三个确定性前置问题。当前实施从 [91 B1–B6](91_br1_m6_to_completion_entry_plan_20260925.md#1-先形成可冻结的-m5-基线) 开始，M6 尚未放行；本文标准不因归档降低。

**目标：让当前 Fresh 管线成为可继续实施 BR1 优化的稳定基础，关闭已证实的正确性与预算缺口，并删除已被替代的状态和协议。**
当前 M5 未验收，M6/M7 不扩展，BR1-PERF 未通过。本文是下一轮实施方案，不是已完成记录。
审计结论以 [85](85_br1_m5_code_readiness_audit_20260924.md) 为依据；
[68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 的安全条件、
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) 的删除证明和
[39](../../../39_virtual_texture_performance_gates.md) 的性能口径继续生效。

## 1. 已提交的检查点与验收修正

本轮先保存一个逻辑检查点。由于外层仓库以 gitlink 引用 Krita，实际包含两个提交：

| 仓库 | 提交 | 内容 |
|---|---|---|
| `krita` | `0db343467871cb169a288964ad03c995d9e4047f` | 当前 BR1/M5 生产实现、测试、架构门与源码绑定清单 |
| 外层 `krita_gpu` | `9c867b83c7dcf33dfd13b2f076592f5a8e8a4822` | 对应 gitlink、设计/执行记录、85 审计及归档证据 |

该检查点保留已发现的缺陷，便于修复前后复现；提交不改变验收状态。构建目录、临时测试图像和系统缓存不纳入提交。
提交后 architecture gate 再次通过，九个受影响 CPU 测试目标 Ninja dry-run 无待构建工作；未据此新增运行测试或性能结论。

[84](84_br1_full_optimization_convergence_and_cleanup_20260923.md) 的“21 已闭合 / 3 局部 / 0 未闭合”保留为历史判断，不能作为当前验收表。
不重算表面完成率，改为按以下具体缺口逐项关闭：

| 门 | 当前状态 | 本方案的关闭条件 |
|---|---|---|
| C4.2 增量 domain 同步 | 重开：确定性复现旧快照覆盖，journal 清空后不能恢复 | 批次 1：物理转移版本、安装版本与确认协议一致 |
| C4.4 有限生产预算 | 重开：只有测试配置限额，MetadataArena 未接线 | 批次 2–3：实际 backend、实际 allocator 和所有终结路径兑现有限预算 |
| C4.3 swap 前准入 | 仍为局部 | 批次 3：RAM/SSD 变化之前取得预约，拒绝时保留有效原状态 |
| C2.7 overlay seal/替换 | 共同 primitive 已存在；整个编排仍须复核 | 批次 4：共同准备/替换/失败协议只有一份，保留单页/多页边界 |
| C3.4 compatibility | 仍为局部，十组边界有真实消费者 | 批次 5：逐调用组迁移；剩余适配器有明确必要性且不再自行维护 canonical 状态 |
| C5.5 最终证据 | 当前 CPU 正确性有通过记录，当前正式性能未测 | 批次 7：同源码结构、正确性、并发和 CPU 性能证据齐备 |

## 2. “足够干净”的可检验定义

不以零适配器、最少类数或目录缩小百分比验收。以下条件必须同时成立：

1. **事实只有一个修改权威。** 页 writer 由 Admission 管，私有写由 session entry 管，metadata 转移由 StateMachine 管，
   overlay proof 由 PublicationCoordinator 管，committed root 由 epoch 模型安装，physical domain/identity 由真实 storage 管。
   读投影、定位索引、非 owning 指针 cache 可以保留，但不能独立推进同一事实。
2. **成功和失败共用资源协议。** 暴露可写字节前具备所需 backing、metadata 与退出资源；失败后保留终结 owner，
   有界重试可完成 cancel/drain/close。不能靠丢失 owner、无限重试容器或预算外分配“保证成功”。
3. **预算控制实际资源。** 正常 backend 使用有限配置；已声明支持的 bucket 有真实 reserve/commit/release，
   usage 为无副作用观察。零预算有可解释的拒绝行为，多文档与 alias 不绕过进程物理上限。
4. **适配器只承接既有调用契约。** 可以保留 ABI、线程交接、raw pointer pin、最后 unlock 等责任；
   不另存一份 generation、writer 页集、budget、seal/cancel 状态机。已有必要状态须逐项证明，不能整体搬家后宣布删除。
5. **热路径只做必要工作。** 诊断关闭时没有诊断时钟/共享原子累加；固定变化页 K 的管理工作不随无关总页 N、历史 H 扫描。
   必要 COW/default、Busy 拒绝、retirement 重试不作为“多余分支”删除。
6. **删除与验收可追溯。** 生产删除、测试搬迁、新增必要协议分别统计；调用图候选经构建配置、模板/虚调用和真实行为验证。
   当前 CPU 测试通过不外推 BR3 活跃 Vulkan，也不代替 BR1-PERF。

目标数据流保持：输入适配 → Admission → base/策略/资源预约 → provider 执行 → 私有写 → overlay seal → root commit → retirement。
批次只收敛这条链，不增加平行的 PipelineManager、BudgetManager 或 compatibility coordinator。

## 3. 批次 1：修复 domain 版本协议

**涉及：** `KisPageOwnerLedger`、`KisTiles3PageReplicaProvider`、`KisTileDataStore` 的 residency 通知与 physical identity。

实施顺序：

1. 将 85 的旧快照复现迁入现有 CPU Mutation 测试，用 semaphore 固定交错；先保留修复前失败证据。
2. 在真实 storage 的驻留转移线性化点生成每个 physical identity 的单调 revision，并在受同一物理锁保护的观察中取得 domain/revision。
   observer 传递这个 revision，退出“按回调到达次序制造物理顺序”的本地 sequence 权威。
3. ledger physical record 保存最后安装的 revision。比较版本、计算 class/domain delta、安装 domain/revision 在同一 ledger 临界区完成。
   旧 revision 不得覆盖；domain 相同但 revision 更新也必须推进版本；同 revision 对应矛盾 domain 要显式拒绝。
4. journal 按 physical slot 保留物理 revision 最大的变化，丢弃晚到的旧通知，不能用最后到达者覆盖新事件；不增长为永久事件日志。
   ack 只能确认精确事件；确认旧事件不能清掉新事件。
   无对应 backing、注册中、退休中的事件分别规定消费规则，不能靠“暂未找到”丢失注册所需的新状态。
5. 初次注册以一致的 domain/revision 建立 ledger；slot/provider epoch 复用必须隔离旧通知，关闭 ABA。
   处理 revision 溢出与 observer 注销寿命，不能把数值回绕当作更新。

这里的 revision 是 storage 状态版本；journal 确认游标若仍有独立用途，须明确两者含义，不能继续用通知到达序号推断物理新旧。
不能只在 ack 加比较，也不能每次扫全部 backing 修补最终状态。

**必要验证：** 旧快照晚安装；swap-out/in 通知倒序；相同 domain 的更新；旧 ack 晚到；多个 observer；
注册与转移交叉；注销/retire 后晚到；slot 复用；domain 同步与 Debt 重试并发。每项核对实际驻留、ledger bytes、pending journal 和最终 drain。

**退出：** 原复现变绿且再同步不改变正确结果；工作量保持受 provider 数与变化项约束；旧通知序号权威同批退出。
本批只修复观察顺序，仍不能宣称 swap 已具备事前预算准入。

## 4. 批次 2：把有限预算接到产品和实际 allocator

**涉及：** `KisTiledDataManagerPageStoreBackend::Private::prepareStore`、现有 `KisBackingBudgetController`、
OwnerLedger、`KisPageMetadataCoordinator::MetadataArenas` 和 `KisImageConfig`。

### 2A. 冻结预算来源、粒度和生效时机

- 复用 `KisImageConfig::tilesHardLimit()`、`poolLimit()`、`maxSwapSize()` 的产品配置来源。
  MiB 转 bytes 用检查过的整数运算；负值、零值、溢出及初始化所需最小量的行为明确，不能静默回退 `max()`。
- 将配置推导集中在一处现有 backend 初始化流程，形成不可变的 Store limits，在资源注册/分配前生效。
  provider 的 `max()/4` 占位退出；测试通过同一入口注入很小的配置，不另建只供测试使用的预算决策路径。
- **进程物理容量与 Store 分类预算分工。** 全局 RAM/SSD 库存由既有 tiles3/storage/swap 分配入口控制；Store controller
  管 Current/History/Pending/Debt 等分类和事务预约。多文档不能各自获得一份可累加兑现的全进程物理额度；
  跨 Store alias 可分别受文档策略约束，但进程物理字节只按真实 allocation 计一次。
- 接线前交付一张配置推导表：每个限额的单位、来源/公式、计费粒度、硬拒绝或回收策略、最小可工作规模。
  现代码不足以证明合理的 Pending/Debt/metadata 比例，本文不伪造已验证常数；实现时先冻结该表，再执行测试和性能测量，禁止测后放宽。
  依赖模式是“产品配置 → 一份推导 → 已有控制器/allocator”，不是各层自行挑默认值。

### 2B. 接通 MetadataArena 的真实申请和释放

把当前每 shard 的 Version/Replica/Overflow 4/8/4 MiB 常量约束与 Store 总预算协调为一份配置。
block、slot directory/index 等实际 owning 分配要有明确计费范围；不能只计逻辑 record 字节而漏掉预分配目录或锁外候选。
元数据与其管理的像素 backing 分别计费，不重复计同一内存。

沿已有“锁外准备 block → revision 复验 → 安装”流程接入 reservation：分配前 reserve，安装后转 live，
冲突/异常/取消释放候选预约，真实析构后释放 live。shard 不能各自解释为可用一整份 Store 上限。
metadata budget=0 时，有实际内存需求的初始化或首次操作必须在分配之前失败；不能成功创建页后仍上报 0。

prepare/root install/读 lease 释放/取消/退休都要纳入检查。必须预留的 metadata 和 Debt 退出资源在像素暴露前准备；
不能把当前有限 Debt escrow 扩展成另一套退出账本，也不能在不可失败安装阶段追加普通可失败申请。

### 2C. 从真实入口验证后启用

覆盖真实 tiled data manager/backend 创建、多文档同时分配、共享 alias、clone、history 保留/释放、
Current/Pending/Metadata/Debt/cache 紧预算，以及初始化中途失败和 close。检查 live/reserved/peak 与真实资源相符。
BR1 尚不支持的 GPU 域和 in-flight 工作必须明确为未接线/拒绝，不能用空 bucket 冒充已完成覆盖。

**退出：** 有限配置实际生效；所有支持的 bucket 可由真实路径触发拒绝及释放；MetadataArena 原复现变绿；
取消不丢失 owner，不泄漏 reservation，不要求先提高预算才能退出。
生产默认值的最终启用依赖批次 3；不能把“接上有限数值但仍先 swap 后记账”作为可发布中间状态。

## 5. 批次 3：在物理域变化之前完成预约

**涉及：** tiles3 swap-in/out、现有物理 claim、observer/OwnerLedger 的 domain 变更预约。
依赖批次 1 的物理 revision 和批次 2 的配置/计费契约。

两阶段协议必须覆盖 RAM→SSD 和 SSD→RAM，而不只在 swap-out 后追加一个检查：

1. 取得稳定 physical identity、源 domain/revision、相关 observer 集合版本及必要寿命持有。
2. 在不持有 tile swap/list/iterator 锁的边界申请目标资源与所有受影响 owner 的预算预约；任一失败，归还已取得预约并保持源状态。
3. 重新进入物理 gate，复验 identity、源 revision、pin/claim 和 observer 集合版本。变化则取消/有界重试，不能拿旧预约转换新 backing。
4. 独占转移期间执行存储变化；I/O 失败须保留或恢复有效源。实际成功时在物理线性化点推进 revision。
5. 转换期间 reservation 持续覆盖新增资源；成功后的记账兑现与通知确认不再进行普通容量准入。
   取消与成功均恰好消费一次 token；后续 `usage()` 不承担纠偏或拒绝资源的职责。

现有 `trySwapTileData()` 的调用者持有遍历/列表相关锁，swap-in 也有既定重锁顺序。
实施前必须逐调用点调整准备/执行边界并画出锁序；仅把回调移出 `m_swapLock` 仍可能反向进入 owner 造成死锁。
不允许持有 storage 锁逐个调用 Store；新增值类型 token 只能代表这次实际预约，不得引入常驻的第二份 physical 状态机。

共享 payload 的多个 observer 必须全有或全无预约；注册/注销过程中不能漏过一个仍持有 backing 的 owner。
源资源在转移成功前不可提前释放计费，目标空间不足时不能反复抖动驻留。swap-in 拒绝需沿真实调用链返回可处理状态，
旧的 raw-pointer API 如不能表达失败，必须先准备其所需资源或改造调用边界，禁止伪造成功/返回失效指针。

**必要验证：** SSD=0 时 swap-out 拒绝、原 resident 页仍可读；RAM 紧预算时 swap-in 不改变有效原状态；
I/O 失败；reader/native pin；多 observer 与多 Store alias；并发 unregister/close；foreground 写与后台 swap/retirement；
预算拒绝后无关页面仍能完成其合法操作；drain 不靠手动 swap-in 解锁全局进度。

**退出：** 更新现有 `finiteBackingLimitMatrix`，删除把“swap 已成功、下一次写才失败”视为准入闭合的断言口径。
进程 allocator 仍是物理库存权威，Store ledger 仍是分类权威；journal 用于增量通知/核对，不再事后批准已经发生的资源增长。

## 6. 批次 4：收敛 overlay seal/替换/取消编排

**涉及：** `KisPageStore.cpp` 的 native seal 与 generic finish，现有 WriteCoordinator、PublicationCoordinator。

共同算法置于既有 owner 内：验证新结果 → 准备旧 proof 的 detach 和新 proof 候选 → 预备 metadata/分类资源 →
复验 → 一次安装/撤销 → 终结旧资源。失败时保留旧 overlay，并由同一取消/退休出口处理新私有资源。
单页输入可以作为一项输入借用共同算法，native 多页仍先准备全批 candidate 后原子 seal。

必须在同批删除两入口原来的共同分支，不能仅提取 helper 后保留第二套“异常时自己拼装 proof”逻辑。
优先使用现有 entry、prepared metadata、reservation；若需要短寿命候选，只保存准备结果，不能复制 transaction/page 生命周期。
沿用现有 `KisPreparedMutationCommit` 的 root commit 责任，overlay seal 不为复用而变成 committed-root 发布。

**保留的差异：** native CPU pin 与 generic 异步 completion；多页 seal 原子性与单 lease 可见性；
entry 私有取消与事务 abort；exact old reader/captured view/last-use 保护。必要差异不通过统一接口隐去。

**必要验证：** 新 proof/metadata/预算任一步失败保留旧 overlay；中间页失败整批不发布；重复 seal/cancel；
default/alias/removal 替换；generic late completion；旧读者跨替换；abort 与 retirement 交叉。

**退出：** 有一张“原分支 → 共同实现 → 删除位置 → 行为测试”的对照表；共同协议的修改不再要求在 native/generic 两处同步改算法。
同步 CPU 不因此多建 generic request、lease 或共享堆对象。C2.7 只在该证据成立后闭合。

## 7. 批次 5：按调用组收缩 compatibility

十组边界是迁移清单，不是十组死代码。每波先画“谁创建、谁借用、谁终结”，迁移真实消费者，再删失去职责的状态。
禁止先造一层统一 wrapper，再让旧 wrapper 和新 wrapper 长期共存。

| 波次 | 真实入口与目标 | 随迁移清理的对象 | 必须保持的行为 |
|---|---|---|---|
| 5A 操作范围 | painter、packed/planar bulk、clear/copy/alias/removal 使用既有 operation/mutation/cursor | 已有 canonical write set 后的重复 target/source 列表；本入口独立终结路径 | 整操作成败、overlap/source 保活、完整 payload、借用 history 事务 |
| 5B 迭代范围 | H/V iterator、random accessor 的写入借用同一 mutation 与 guard；读复用已有 ReadPage/ReadCursor | 重复 exact 解析/cache 权威；可由显式 scope 替代的 thread lookup 和 iterator boundary 回调 | 跨页指针有效期、current/before、嵌套调用、跨线程最后 unlock |
| 5C tile/事务范围 | 剩余 legacy tile 调用只经必要 lease/bridge 适配 canonical scope | `nativeReadReady`、write intent/native pin 状态中可由实际持有推导的副本；无消费者的 lease registry/boundary；匿名 client/failure 的重复生命周期 | 最后 client 结束才提交、失败传播、barrier、reader 不能撤销 active writer |

判定规则：

- `anonymousTransaction/anonymousClients/anonymousFailed` 不能看到三个字段就直接删除。
  先区分“多 legacy client 共享一个事务”这一真实责任与 session 内部状态；若还需要共享寿命，保留一个既有 owner，
  wrapper 只持有它。迁移完成后删除旧引用计数/失败传播实现，不能再开第三份匿名事务协议。
- `cpuMutationBatches` 的线程注册与显式 scope 二选一承担发现职责；有 ABI 必要的借用查询可以留，不能再独立管理页准入。
  `iteratorWriteBoundaries` 若仍因可见性边界存在，必须指出不能由 guard/scope 生命周期替代的 caller，并保留对应反例测试。
- tile 的旧数据视图、nested lock count 与实际 pin 不一定是同一事实；可推导字段要删除，不能推导的持有责任保留。
  无 history 时 before 可能别名 live write，有 captured history 时必须固定 exact view，不能统一成错误的快照规则。
- 非 owning 热指针与 owning pin 责任不同。不能为减少 cache 数量，在 caller 仍可持有 raw pointer 时跨页释放 pin。
- `Unavailable` 仅在未开始工作时允许 fallback；`Failed` 可能已写字节，禁止重放另一条管线。
  Busy/Invalid 不能伪装“不支持”而物化或复制重试。

**退出：** 十组各列“已迁移并删除 / 保留最小 ABI 边界”及源码/测试理由，不能留“以后再清理”的双权威。
残留适配器有活调用不自动合格；必须证明它只承担不同寿命或调用契约。C3.4 闭合不要求删除 Krita 全部 tile API。

## 8. 批次 6：删除验证后的冗余，修正文档口径

| 对象 | 动作与门槛 |
|---|---|
| metadata transition 无条件计时/共享 atomics | 使用现有 opt-in diagnostics 或删除仅测试需要的常驻计时；关闭态不读诊断时钟、不写跨 shard 原子；行为测试不依赖机器速度阈值 |
| `KisCpuPageReplicaProvider` | 核对生产工厂、构建选项、Vulkan foundation 与外部引用；若仍只有测试构造，移入已有 tests support target，并退出 production CMake；物理存储不同，不能为“唯一 provider”硬合并 |
| 249 indirect / 139 test-only / 43 unreached 候选 | 逐项裁决模板、虚调用、取地址、隐式析构与其他配置；确认死实现才删，测试专用则迁移；不把 431 个候选全部统计为死代码 |
| default revision/surface 责任 | 复核 `defaultRevisionHighWaterLocked()` 暴露可写引用的多处修改；收口到既有 owner 的分配/导入操作，外部不直接改 high-water；undo 恢复旧 root 后 revision 仍须单调 |
| 其余 ownership split | 对 transaction、physical allocation、last-use、binding/cache 分别说明谁决策谁执行；当期双权威要收口，BR3/handoff 目标边界明确标注，不能为凑“零 split”把真实物理锁职责搬到上层 |
| 状态文档和结构指标 | 当前判断统一指向 85/86；保留历史证据，不把目录搬迁计作删除、不把 foundation 构建计作活跃 GPU 验收 |

每一项生产重写报告被删除的旧算法/状态和净变化；新增 revision、预算预约等必要正确性成本单列。
不以总行数下降抵销某处新增双实现，也不为达到行数指标压缩清晰的失败处理。
`KisImageEpochReferenceModel` 当前是生产 root authority，不能因名字移入测试；snapshot/oracle 也不能和第二套可写权威混为一谈。

## 9. 批次 7：形成足以关闭 M5 的证据

前六批每批先跑直接受影响行为测试与 architecture gate，改动稳定后再统一验收；不在每次微调后重复整套性能跑分。
最终测试必须来自相同源码提交/构建，记录命令、配置、source hash、binary 与原始结果。

### 正确性与资源边界

- 重新生成源码绑定调用图并运行 architecture gate、图工具自测；不放宽 intrusion ratchet 来掩盖迁移。
- 重编并运行 7 套 PageStore/Completion、Painter、tiles3，保留 QtTest totals、seed 和环境。
  arm64 与 x86_64 重新运行，不沿用 84 的历史数字；维护现有 Vulkan foundation 的构建/契约兼容。
- 跑批次 1–5 的确定性交错与失败矩阵，增加有界并发压力，覆盖 swap、foreground write、retirement、history release、close。
  TSAN 作为并发补充；若环境不支持，明确记录缺口，不能把普通压力测试写成 race 检测通过。
- 长时间循环后无单调增长的 pending journal、live reservation、orphan、匿名 client 或终结队列；
  退出稳定，预算峰值与实际资源吻合。含多文档、极小预算和真实取消，不只验证正常 FreshCow。

现有本机命令入口见 [85 证据 README](../../../evidence/br1_m5_readiness_audit_20260924/README.md)。
实施期间源码已变化后，必须用当前测试替换 scratch 复现，不把旧 source hash 的日志当新结论。

### 性能与控制工作

- 比较基线分开：本检查点用于判断本轮收敛收益/回退；冻结 upstream 同义操作用于正式 CPU 不劣性；
  selector forced-COW 还须有隔离 selector 成本的匹配控制，不能用整个实现相对旧检查点的加速掩盖该项回退。
- 按 39 预先冻结 required buckets、容差、至少 95% 的单侧置信口径、独立配对运行与停止规则。
  M/K/X/E 分列，吞吐与尾延迟分别验收；控制 N/K/H、字节格式、线程与诊断状态，保留完整 drain/析构成本。
- 必测固定 K 增长 N/H、冷/暖 read、native/generic、真实写/COW/default/alias、有限预算压力和回收。
  selector 的 forced-COW 控制桶回退不超过 68 规定的 2%；这是既有门槛，不能以 QtTest 总耗时或短 read 样本替代。
- 结构零工作（零额外 request、无全表扫描、诊断关闭无计时）和实际性能分别报告；
  `Inconclusive`/`NotMeasured` 保持开放，不用均值掩盖单桶退化。

### 两个不同出口

**M5 可以关闭：** 批次 1–6 的当期缺口关闭，剩余适配器均有必要性证明，当前 CPU 正确性/预算/并发矩阵通过，
且 M5 已规定的 selector 性能门通过。届时才评估 M6/M7，不能在收口过程中扩展 handoff 增加变量。

**BR1 优化版本可以宣称完成：** 在相应优化实现之后，通过 39 的正式 CPU BR1-PERF 和完整生命周期验收。
M5 关闭只是可靠前置，不能代替最终性能资格；M6/M7 的收益目标留在相应实施阶段验证。
BR3 活跃 Vulkan/GPU/UMA 的产品与性能资格独立，不作为关闭 CPU M5 的新增条件。

## 10. 执行纪律与下一步

顺序为 **1 → 2（契约/allocator）→ 3（事前准入并启用有限默认值）→ 4 → 5A/5B/5C → 6 → 7**。
每批独立可 review：列出修复对象、唯一 owner、被删旧状态、测试和未解决项；保存修复前后证据，不把多个缺口合成一个乐观完成标签。

下一次代码实施从批次 1 的确定性失败测试开始。若某批必须保留兼容行为，记录它的实际消费者和寿命反例，再决定最小表示；
不因为实现麻烦就以改名、搬文件或新建 coordinator 代替收敛。
本文尚未实施任何修复；两个已提交检查点与本方案之间的差异仅为规划/状态文档。
