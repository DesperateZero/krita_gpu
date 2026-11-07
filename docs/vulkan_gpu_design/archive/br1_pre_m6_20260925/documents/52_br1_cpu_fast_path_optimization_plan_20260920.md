> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 Resident CPU 快路径与生产布局优化计划（2026-09-20）

> 当前入口（2026-09-25）：状态以 [90](90_br1_m5_baseline_freeze_review_20260925.md) 为准，实施顺序为 [91](91_br1_m6_to_completion_entry_plan_20260925.md) 的 M5 修复/冻结 → M6 → M7 → M8 → BR1-PERF。M5-ready 未通过。本篇的性能目标、同义 upstream 与退出约束继续生效；各 Dx 的“当前/下一步”及后续执行补记均为历史时点，53–67 已按 [索引](../../br1_tuning_20260925/README.md) 归档，不再独立驱动下一阶段。

本文是 BR1 在功能/正确性 cutover 之后的生产性能结清计划。2026-09-19 的
[51_br1_canonical_pagestore_closure_20260919.md](51_br1_canonical_pagestore_closure_20260919.md)
仍是功能语义、状态机和测试通过的历史证据；但 2026-09-20 与 `origin/master@9a24ae0d8c` 的同机差分审计证明，
resident CPU 热路径、稀疏 default 页面和 epoch 生产布局尚未达到 BR1 出口。因此 BR1 总状态改为
**BR1-PERF 进行中**，在本文门禁关闭前不得声明 BR1 整体结清，也不得进入 BR2 production 接线。

权威语义仍由
[25_p0_canonical_pagestore_krita_tile_cow_swap.md](../../../25_p0_canonical_pagestore_krita_tile_cow_swap.md) 和
[33_virtual_texture_pagestore_state_machine.md](../../../33_virtual_texture_pagestore_state_machine.md) 定义；写侧选择、backing handoff 与硬预算由
[68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 收敛；本文把这些语义落实为
CPU 产品路径、生产数据结构、迁移顺序和可量化出口。

本次口径补强把“VT/PageStore 管理对比主干 tile 管理”与“VT 吞吐/延迟对比 RAM Tile”分为独立证据，再作整合。
M（管理）、K（驻留算子）、X（跨域/执行交接）、E（端到端）的权威定义、配对矩阵与比值方向统一在
[39 的 5.6–5.9](../../../39_virtual_texture_performance_gates.md#56-四类证据与基线配对统一定义)；20 规定埋点，30 规定 CI 拒绝条件。
新增要求目前是实施与验收计划，不是新的实测通过声明；53/54 的 CPU-only stress 均不能证明 UMA/显存性能。

## 0. 性能目标与零开销边界

2026-09-23 执行更新：[84 全性能优化链路收敛](84_br1_full_optimization_convergence_and_cleanup_20260923.md)
复审本文开始后的全部优化实现和兼容分支，先消除重复协议与预算缺口，再继续 handoff 和最终性能验收。
历史切片结果保留，不代表当前工作树；清理范围不以 68 M1 为起点。

**当前执行顺序更新：先整体结构重构，再统一性能验收。** 以
[67 的六项约束及生产入口清单](67_br1_target_structure_reconstruction_20260920.md) 为当前工作清单，并以
[68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 作为写侧最终结构。当前独立 backing/COW 是正确性 fallback；
生产目标是由 PageStore 内部按可见性和恢复条件选择 backing handoff 或必要 COW，并以硬字节预算约束 fallback 和退休积压。
重构期间持续运行正确性、并发、失败原子性和生命周期测试；不再以每个 Dx 的局部吞吐 A/B
作为继续结构迁移的前置条件。本文后续 P1–P6/第 12 节中的逐切片计时顺序据此调整；
历史结果、反证和最终 M/K/X/E 门槛不变。结构尚未完整通过时，不启动“整体重构后”的性能资格运行。

- CPU/CpuRam、相同管理语义下，PageStore 管理成本以主干 Tile 等价或更优为目标（`M_time_ratio <= 1`），不因虚拟纹理
  抽象而预留固定额外管理开销。工程验收采用 39 的 5.6 所定义的预冻结容差及配对不劣性判据，不要求每次计时逐周期相等。
- 无真实 materialization/交接需求时，不进入通用跨域控制路径。读侧按所需 exact generation 是否已有就绪、可合法 pin
  的 CPU 可读副本判断，不按 authority 所在域、历史读取标签或 cached handle miss 判断。
- UMA 同一已驻留、布局兼容的 shared backing 上，CPU↔GPU payload migration copy count/bytes 应为零；这不是整个
  X/E、缓存流量、同步、queue/ticket 或执行等待为零。CPU-only 且无需 GPU 交接时不为可共享 backing 额外执行 GPU 协议。
- 消除多余工作是首要目标；必要硬件/执行依赖、实际新增对外语义和软件冗余分别归因。内部 generation/proof/adapter
  记账若服务于同义操作，仍计入 M；真正新增语义单列绝对预算且保留在产品 E，不能把所有剩余差值称为硬件必然开销。
- 1.2×/1.3×/1.5× 是完整操作的阶段上限，不是管理等价容差。BR1-PERF 结清须同时通过 CPU 同义管理不劣性、结构硬门槛
  和完整操作吞吐/延迟门禁；当前配对证据和新增 harness 尚未齐全，不因此改变“进行中”状态。

“VT 只增加真实跨域开销”在本计划中表示消除不必要软件工作的目标，不表示已经证明端到端差值仅来自硬件。
尤其 UMA 的零值只约束上述 payload migration；同域访存/cache policy、执行交接、必要新增语义和软件冗余不能合并记零。
管理等价、底层复用、整条管线同构、性能实测通过是四种不同结论，分别按 39 的 5.6–5.10 给证据。

本次校准统一使用以下表述，后文实施项和验收项不得放宽它们：

- **设计目标**：CPU 同义管理不预留 VT 抽象税；消除冗余后，再由实测解释必要的存储访问、执行交接和新增对外语义成本。
  不预设 `E_VT - E_Tile == X`，也不承诺在 UMA 上该差值必然为零。
- **通过结论**：写明“在冻结容差内通过同义管理不劣性”，不简写成“耗时完全相同”或“软件零开销”；未冻结容差的探索性
  A/B 只给诊断结论。同域 K、完整 E 以及结构硬门槛仍须独立通过。
- **当前实现**：native TileData/pool/swap 复用 + PageStore 控制/epoch/adapter 管线；不是整条 CPU 管线同构主干。
  D4 已消除支持条件下 preserve 的 default-fill 再 source-copy，D8 已接通新 CPU facade 的 native read guard；
  legacy traversal 的统一接入、mutation session/原位 permit 及完整回收预算仍未结清，不能把读侧切片外推为整条管线完成。
  D11 已把生产 writeBytes 的安全 COW 段接到 native mutation/guard，仍未完成 permit/短发布/全部入口，见1.15/65。
  67 §24 进一步让正常 packed write 退出 legacy wrapper：固定 View/no-op 比较、直接 guard、整页 discard、范围/取消/提交与像素操作共用，
  写体不持 DataManager 锁。§25 以同步完整输入直接初始化新 backing，正常 packed 整页不再 default-fill；普通 discard/无能力 fallback 保留初始化。
  同段 overwrite 复用 pending，仍可取消；这不是原位 permit，也不意味着全部 producer 已迁移。
  §26 区分逻辑 root 接入资格与物理退休队列：旧 root 最后保护释放后不能凭 epoch ID 复活；reachability 只遍历 current/受保护 root。
  这收紧了原位许可的一个必要前提，不是操作期间禁止新 current 捕获的 fence，也不是完整 owner-issued permit。
  67 §31 后仍未接通统一 write-plan selector、allocation handoff 或硬 backing budget；68 已废弃把公开 permit 作为最终 API 的方向，
  但保留其 capture/alias/history/in-flight/abort 安全条件并收进 PageStore 私有 `KisPageWriteCoordinator`、内联 plan 与 claim。
- **已归档证据**：58 的 native COW 分支内收益已由 59 的同源 upstream 诊断补充：D5 所测版本真实写完成吞吐仅为主干约
  0.27%–0.39%，暖管理约 74%–86%；不是全局性能恢复。D3 目录去锁未确认加速，D2-B-small-K 反证未关闭。
  CPU 同主干已测部分 M/K/resident E 的窗口吞吐，但正式资格仍未取得；GPU/UMA 产品性能为 `NotMeasured`。
- **D6 归档切片**：60 已将逐 ticket 终态存储改为完成覆盖与稀疏非成功状态；原区间候选的碎片时间/RSS反证促成了布局修正。
  D6 所测版本分支内真实写吞吐仅改善约2.9%–5.5%，不按组件约90%的长桶降耗推导整条 CPU 管线收益；主线仍是 native guard/session/permit。
- **D7 归档切片**：61 已落实 captured identity/surface view 及 CPU facade 一致性，该版本像素仍走 generic lease。
  identity lookup 吞吐改善约1.8–2.5倍，但单页 generic session 吞吐下降约23%–25%；历史反证保留，不改写成新路径结果。
- **D8 归档切片**：[62](62_br1_native_resident_read_and_write_cost_20260920.md) 已接通 stable binding/native read guard，
  暖驻留读的逐页 generic request 为零。相对 D7，新 facade 单页 session 吞吐约为3.17–3.48倍，16页 session/accessor
  约11.6–12.2倍；但未迁移的原生真实写吞吐下降约2.3%–4.8%。生命周期/并发回归通过不等于正式 M/E Pass；
  写侧反证、冷 binding/完整 drain 及同主干配对仍未关闭。不能用读收益抵消写回归，也不能连乘历史比值重算主干性能。
- **D9 归档切片**：[63](63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md) 将读缓存改为首次native读建立，
  保留stable record/共享gate。相对D8真写吞吐提高约2.7%–3.8%，但直接D7/D9仍有约0.8%–1.7%负偏移；首次16页read scope
  变慢约70%–73%，部分暖session/accessor/rect也退化。该检查点提出分离暖lookup与冷发现，后续D10见下；不能把成本转移称为消除。
- **读侧归档切片 D10**：[64](64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md) 已分离暖lookup与冷发现，
  相对D9，16页held-view guard吞吐提高约5%–7%、完整session/accessor约4%；直接对D8，部分宽格式读仍有负偏移，
  首次16页read scope仍慢约63%–73%。真实写直接D7控制仍有约1.1%–1.6%负偏移；未授予不劣性。
  固定256周期已补facade/provider容器析构，不是全后台drain。当前候选仍需冷热/真实写及环境归因，BR1-PERF不结清。
- **最新写侧切片 D11**：[65](65_br1_native_cpu_mutation_segment_20260920.md) 已接通 writeBytes 未发布写段。
  400次有效计时保留K1约5%–6%回归与K16约8%收益；直接固定主干真实写吞吐仅0.26%–0.45%。结构计数、粗分段和
  RAM copy控制不等于全部M/K/E达标。下一研究必须继续permit/生产写记录/短发布，不能退回连续读缓存调参。

跨文档判词统一引用 [39 的 5.11](../../../39_virtual_texture_performance_gates.md#511-统一口径速查与报告判词)，不能将上述目标
降格为“允许固定 VT 管理附加税”，也不能升级为已经证明“UMA 总额外时间为零”。管理 self 与包含像素准备的
lifecycle-inclusive 分开标识；M/K/X/E 是归因视角，不是三个可相加子项与一个总项。

落实时还须遵守三条校准规则：

1. CPU-only、相同 CpuRam 驻留条件下的管理差额不能归因于跨域硬件；UMA 零迁移也不能豁免软件差额。
   “必要”须由相同任务的副本、访问与交付依赖证明，不由 PageStore 当前恰好执行了该工作反推。
2. 免全局锁声明须区分 operation 的 capture/release 与 scope 内逐页访问；短 capture/publication 临界区的真实成本仍计入 M/E。
   仅 identity/root lookup 免锁不等于像素路径免锁，亦不等于严格 lock-free；root retention、backing pin、异步 last-use
   三类寿命保护和原位写 capture gate/permit 不能为了满足零计数而删除。
3. 52 的目标、39 的判据和 20 的计量可以更新，53–64 与 evidence 中的历史样本不能改写成新版本结果。
   后续实现重新绑定源码/二进制与测试证据；残余或反向结果按 39 的 5.10–5.11 登记，不用术语调整宣布优化完成。

## 1. 审计结论

同一机器、同类构建参数下，优化开始前的 BR1 与 upstream 基线代表性结果为：

| 用例 | 历史 upstream | 优化前 BR1 | 历史观察差距 |
|---|---:|---:|---:|
| `stressTest` | 2.529 s | 144.530 s | 57.1× |
| `stressTestLazyCopying` | 0.990 s | 99.605 s | 100.6× |
| tiled manager QtTest 总时长 | 11.826 s / 21 cases | 260.062 s / 23 cases | 约 22×，仅作补充观察 |
| 32767 个空白坐标只读 | <1 ms，49.0 MiB RSS | 331 ms，485.7 MiB RSS | 至少 331×；RSS 9.9× |

这些数字说明当前问题是执行路径和数据布局问题，不是调小锁粒度、对象池化或编译选项即可消除的常数项问题。
PageStore 的 canonical identity、generation、transaction 和 replica 方向保留；需要重构的是 resident CPU data plane，
不能让通用异步 materialization control plane 介入每次本地 tile lock。

优化开始时定位的主要放大项：

1. `getTile()` 预刷新后，正常 `lockForRead()` 再次执行 acquire/resolve/release，单次逻辑访问重复走完整协议；
2. 空白/default 只读为每个 `PageKey` 创建并长期保存 Published page/replica，破坏 upstream 的共享 default tile 与稀疏性；
3. 每次 write lock 都分配新 replica 并复制整页，同一事务重复写同页也不断产生 generation/allocation；
4. tile unlock 隐含 publish、proof、extent 扫描和 epoch commit，提交粒度退化为 tile-lock 粒度；
5. extent 通过全 manifest 扫描派生，而不是 changed-page 增量维护；
6. 当时的 `KisImageEpochReferenceModel::commit()` 重建 `QHash`、导出 `QVector` 并排序，生产 commit 为 `O(N log N)`；
7. PageStore 全局 mutex、heap request/lease 记录和 provider 的 active-lease 线性反查进入 resident CPU 热路径；
8. 当前接口只表达“通用 request/resolve”，不能表达已驻留页面的无分配、局部 pin 快路径。

### 1.1 重新审阅 upstream 后必须保留的完整性能模型

`origin/master@9a24ae0d8c` 的优势不是单一 COW 判断，而是一组协同机制；BR1-PERF 不能只实现其中一半：

- `KisTile::lockForRead/Write()` 用 tile-local counter 合并嵌套访问，只在 first lock/last unlock 操作 swap pin；
- random accessor 保留小型 hot-tile cache，line iterator 预取并在整行/整段访问期间持有 tile；逐像素不重复 lookup/pin；
- `getTilesPair()` 把 current/oldData 获取合并，避免 memento 开启时双倍 hash/锁压力；
- `KisTileHashTableTraits2` 使用并发稀疏 map、raw-pointer access guard 和 deferred reclamation；普通 lookup 不经过
  data-manager/PageStore 全局 mutex；
- default miss 只创建短期 wrapper并共享一个 `KisTileData` 像素 backing，不把坐标插入 hash/extent；新实现可以进一步
  使用栈上 virtual view，但不得退化为坐标级 canonical record；
- 4/8 BPP tile payload 使用固定尺寸 pool/cache，其他格式保持连续整页 allocation；COW clone 可由后台 pooler 预制，
  避免交互线程频繁 allocator/memcpy 抖动；
- full-tile clone/bitBlt 在格式/default 兼容时共享 `KisTileData`，只在后续 first write COW；default full clear 删除映射，
  相同 non-default fill 也可以共享只读 backing；
- memento 以 changed-tile index 提交并按需提供 oldData，不扫描未变化 tile；
- extent 用 row/column occupancy 增量更新，仅边界删除时扫描相应轴结构，不逐 commit 遍历 page manifest。

对应 PageStore 设计应保留这些**复杂度和局部性性质**，不要求照搬具体 mutex/容器。cached handle 数量和 pin 生命周期
由 traversal 决定；current/old view 使用 fused resolve；read-mostly sparse index 采用 RCU/epoch/hazard/deferred
reclamation 或继续复用已验证的 tiles3 map；payload arena/pool 与 metadata persistent root 分开；full-page clone/clear
优先 alias/sentinel/delta，而不是无条件复制像素。

本轮主干复核以 `origin/master@9a24ae0d8c` 为固定对象，源码事实和落实门禁如下；后续 upstream 漂移时必须重跑此表，
不能只沿用结论：

| upstream 源码事实 | 必须保留的性质 | 本文落实点 |
|---|---|---|
| `tiles3/kis_tile.cc::blockSwapping()`、`lockForWrite()` | first/last nested pin；仅 shared users 触发一次 COW；旧 backing 延迟释放 | 3.1–3.3、P2/P3、resident/accessor 门禁 |
| `tiles3/kis_tile_data.h::blockSwapping()` | resident pointer 直接返回；只有 backing 已 swap-out 才进入 materialize | 3.1、P2/P5、resident fast-path 零放大计数 |
| `tiles3/kis_random_accessor.cc`、`kis_hline_iterator.cpp` | hot tile set/整行预取并持 pin；逐像素仅 pointer arithmetic | 1.1、P2、accessor locality 门禁 |
| `tiles3/kis_tiled_data_manager.h::getTilesPair()` | current/old 一次协调获取，避免双倍 lookup/lock | P2、fused current/before resolve |
| `tiles3/kis_tile_hash_table2.h` | 稀疏并发 lookup、raw access guard、deferred reclaim；default read 不插入坐标 | P2/P5、virtual default 和 sparse-index 门禁 |
| `tiles3/kis_tile_data.cc`、`kis_tile_data_pooler.cc` | 连续整页数据；常见 BPP pool/cache；有界异步 preclone | P3/P5、payload arena 与 COW reserve |
| `tiles3/kis_tiled_data_manager.cc::{clear,bitBltImpl}` | full tile 删除/共享 backing，partial tile 才逐像素写 | P3、clone/clear 门禁 |
| `tiles3/kis_memento_manager.cc::{registerTileChange,commit}` | first-change changed-tile index；提交只遍历 delta；提交后唤醒预克隆 | 3.4、P3/P4、changed-page history |
| `tiles3/KisTiledExtentManager.cpp` | row/column occupancy 增量维护；边界删除只扫描对应轴 | 4、P4、K/N complexity 门禁 |

### 1.2 2026-09-20 实装检查点

以下是本计划启动后的历史单次诊断结果，用于观察优化趋势，不替代第 7 节要求的重复计时与独立尾延迟报告。
2026-09-20 二次归因及分段/分结构图见 [53_br1_performance_attribution_review_20260920.md](53_br1_performance_attribution_review_20260920.md)；
该复审校正了本节原先把剩余 stress 成本主要归因于 mutable COW 的推论。

| 用例 | 优化前 BR1 | 首次优化检查点 | 历史 upstream / 阈值示意 | 状态 |
|---|---:|---:|---:|---|
| 32767 blank coordinate read | 331 ms；485.7 MiB RSS | Qt 1 ms；49.7 MiB RSS；0 PageKey/version/replica allocation | upstream <1 ms；结构门禁为零实例化 | 结构门禁通过；计时仍需扩展重复次数 |
| `stressTestLazyCopying` | 99.605 s | Qt 0.892 s；real 1.02 s；51.1 MiB RSS | upstream 0.990 s；上限 1.485 s | 单次低于历史阈值，未完成配对验收 |
| `stressTest` | 144.530 s | Qt 25.841 s；real 25.98 s；约 355 MiB RSS | upstream 2.529 s；上限 3.794 s | **历史观察显著超限（约 10.2×）；正式倍率待配对重测** |

主 stress 的历史阶段性观察为 `144.530 -> 70.760 -> 45.55 -> 37.42 -> 27.29 -> 25.841 s`。这些单次结果混有不同
随机流和 Qt/进程计时端点，不能用于计算各项优化的独立贡献；必须以固定 workload 的配对测量重新验收。
这期间已实现以下生产路径修正，正确性仍由相应测试独立约束：

- 从未分配坐标的 tiles3 default read miss 不再创建坐标级 metadata/replica；该检查点的删除/历史 default 路径仍会物化，见 53；
- bridge/old-view/native-ready 使用稳定原子快判，provider lease id 使用 O(1) 定位；
- write lock 先取得 intent，只有真正暴露 mutable data 才 reserve/复制；
- whole-tile fill/clone 使用显式 batch、同步 backing adoption、共享 immutable uniform backing 和相同内容 no-op；
- 相同 `writeBytes` 先在受保护的 tile read view 中比较，内容未变不创建 generation/transaction commit；
- state coordinator 对 owner-held 已验证状态使用 trusted transition，外部/reference `apply()` 仍执行完整前后 invariant；
- commit 可在无 retention/reader 时原子融合 idle history retirement；
- epoch root 已改为结构共享的平衡 persistent tree，sparse delta 为 `O(K log N)`，dense delta 才执行有界 rebuild；
- memento 记录 changed-page delta；canonical restore/purge 按 delta 处理，但 tiles3 rollback/rollforward 仍全量重建索引；
- history retention 使用不含 owning manifest 的 root capability；事务起点、删除 extent、allocatedPages 仍导出完整 manifest；
- 增量 restore/release 只能由 `KisPageStoreMementoManager` 调用，普通 PageStore 调用方不能伪造“不完整 delta”。

不能据此宣称 P2–P5 完成。53 的固定 seed 计数证明该版本主 stress 的 `writeRequestsCreated == 0`，当时主要成本是
删除时 default 物化、canonical commit/adoption/history，以及适配层索引维护。它不能验证真实 mutable CPU 写性能。
正式 `CapturedReadView/CpuReadGuard/KisPageMutationSession`、PageStore 私有 coordinator/inline plan、同 session 同页 pending generation 复用、
page-local metadata 和 accessor traversal scope 仍未整体接通；这些需求保留，但必须由实际改写像素的 workload 排序和验收。
**BR1-PERF 保持进行中。**

### 1.3 D1 切片后状态：结构与性能结论分开

随后 D1 已将 `commit(removal)`、restore-to-default 和 default metadata revision 切换改为 virtual default 语义，
同步 full-tile adoption 不再先填充即将被覆写的 default base；事务 prepared read 优先于 base materialization。
定向生命周期测试（1/4/8/16 BPP）、旧 reader/default revision 与状态机负例已有通过记录；随后统一了 TransactionOverlay
的 identity/read/default 初始化语义，并验证 history clear 后再写及 undo/redo。最终 Foundation 24、Reference 31、完整
tiled-manager suite 36 项通过（Qt totals 含 init/cleanup），见
[54](54_br1_optimization_execution_and_deviations_20260920.md)。这不是全部 BR1 产品回归或性能门禁通过。

通用 exact default read/write 仍可能按需物化；共享 native default guard、坐标 metadata 长期有界性、完整 P2/P5 均未结清。
D1 前/最终后各 5 次独立 plain 诊断的 Qt median 为 **26.556 → 16.212 s**（约下降 39.0%）；同 seed、8 workers、1 BPP，
非交替运行且实际 page work 不完全相同，不是主干配对。最终独立 profile 的目标 manager default materializations 为 0，
generic write requests 仍为 0；不据此外推所有 manager 或真实像素写。首轮 1/5 ms、最终 5 ms 新采样将 commit/adoption/GC
列为主要残余路径；样本占比不是精确 CPU 时间。新数据只引用 54，不将 53 的旧热点套用到修复后。
同主干 M 不劣性、真实写 K/resident E 全矩阵、尾延迟、长期 drain 与 GPU/UMA 仍未取得资格；缺测项保持 `NotMeasured`。

### 1.4 D2-A 检查点：定向阶段与无清单事务起点

新证据见 [55](55_br1_d2_phase_measurement_and_atomic_transaction_begin_20260920.md)。已加入 owner-filtered opt-in phase
诊断和 52 桶固定 N/K/H/格式/工作类型 fixture；`beginCurrentTransaction()` 在同一 owner gate 内捕获并保留当前 root，
匿名事务不再导出全 manifest 只取 epoch。显式历史 base 继续用 `beginTransaction(baseEpoch)`，两者不混用。

N=4096、K=1、4 BPP 的真实 scanline 写 median 约 36.5→20.4 μs，alias 约 33.0→17.8 μs；原混合 stress 的
5-run median 16.177→16.286 s，区间重叠，未确认整体收益。前者是复杂度修正的切片诊断，不能冒充普遍提升或同主干资格。
Reference/Foundation/完整 tiled-manager 为 33/24/88 passed；细阶段 profile 开启后 stress 有约 15%–17% 扰动，只用于定位。
same-fill no-op 仅在已知 uniform backing 命中时成立，cold identical 仍有额外 adoption；精确内容属性未结清。
D2-A 当时的 metadata batch 尚未实装；后续实施状态见下节，不能把该历史检查点当作当前缺口清单。

### 1.5 D2-B 检查点：同步 prepared metadata publication

[56](56_br1_prepared_metadata_publication_20260920.md) 已实现 owner-held move-only candidate batch，覆盖 write proof 与
default/removal transition；逐页 revision/短 claim 先整批复验，再安装 metadata/descriptor，最后发布 root。
删除不再为预演补写 live default metadata。保留 proof/provider 校验与所有 transition-local lifetime guards；仅对 coordinator
已验证内部状态复用既有 trusted invariant 边界，外部 state 校验及 reference 对照不变。

这仍是同步 owner-gated 切片：没有生产 record/cursor、锁外 prepare 的 provider/retention claim，也没有免全局锁 native read。
初版候选曾在 H=0 alias 桶慢约 6%–8%，已保留原件并据此消除新增 invariant 扫描/第三遍 shard 交接；最新实测见 56，
不得只报告缩短后的 install 阶段或把通过负例当作性能合格。restoreRetainedEpoch 入口尚未迁移到新 seam。
最终 plain stress median 16.037→15.118 s（约下降 5.7%，非主干配对），但小 K/H=0 的 alias/真实写仍慢约 6%–10%。
该反证未解决；后续同时研究 transaction 固定成本与真实写外壳，不能以 stress 通过代替小桶或 M/K/E 门禁。

### 1.6 D3 检查点：长区间/操作级抽样与只读目录发布

[57](57_br1_sampled_write_pipeline_and_immutable_directory_20260920.md) 加入 ≥100ms 长桶、六对交替 library 对照及 1/127
完整操作抽样。plain/sample ratio 中位约 0.998–1.005，但不证明零扰动；recorded 单次仍有时钟成本。关闭 recorder 的新旧
binary 也有 real K1 偏移，不能把它归给目录优化。代码将一次配置 shard directory 改为 release/acquire 发布，不再每页取
configurationMutex；页面锁与 PageStore owner gate 仍在。六个 paired 桶均未确认性能收益，Reference/Foundation/tiled 为39/24/88。
完整管线定位支持下一主线推进 P3/P5 resident write/native guard：acquireWrite 仍承担通用 request、prepare/transfer、ticket
与多次状态转移。不得继续只盯 commit，也不得把其中 RAM copy 误算为管理 M 或跨域 X。D2-B-small-K 历史反证仍保留。
源码确认 generic preserve 还先逐像素 default-fill 新 backing，再整页 source-copy；语义 default request=0 不覆盖这项
provider 初始化。优先消除该冗余 payload pass 并吸收主干 duplicate/preclone，补齐对应工作量计数，不先假定其 wall 占比。

### 1.7 D4 检查点：native COW 初始化与实际 payload 工作

[58](58_br1_native_cow_initialization_and_payload_accounting_20260920.md) 已接入同 provider/epoch/CPU 域的同步 exact-source
初始化能力，tiles3 直接 duplicate，不再先默认填充或再做第二次 transfer。source/reader/abort、writer、operation/completion
及目标 version/layout 校验保留；新增实际 payload 计数和 provider 子区间。Reference/Foundation/tiled 为42/24/88。
同脚手架十桶六对交替：七个真实写桶时间比0.436–0.593，三个 alias 控制桶未确认变化。不是主干 M/K/E 资格。
预克隆命中全为0；不把收益归给预克隆，不以 logical copy 字节推导 DRAM 流量。部分 sampled 桶仍有约1%及反向偏移。
after 定位中 K1 finish 超过 body，K16 访问/发布与 finish 均显著；下一步分桶研究 native guard/session 和批量发布，
不能继续把已消除的 default fill 当当前主瓶颈，也不能仅盯 commit。后台 preclone/长期 drain 等完整计量仍待完成。

本次口径复核补充两项源码边界，不新增计时结论：固定 fixture 的 `alias` 使用交替颜色的 `clear()`，计时内仍会创建
uniform source backing；目标 provider 的零 default-fill 计数不覆盖它，故该桶是操作级控制组，不是纯 M。`writeBytesBody`
已在一个 tile wrapper 内处理连续多行，不是每行一次 COW；后续重复写优化应先按真实 session/页/发布边界计数，不能据
scanline fixture 推断多行写存在逐行放大。对应源码范围及证据限制见 58 的第 3 节。

### 1.8 D5 检查点：同源 upstream 管线对照

[59](59_br1_shared_upstream_cpu_baseline_20260920.md) 固定 upstream `9a24ae0d8c`，在两侧直接运行同一份 tiles3 fixture，
不向主干套 PageStore 协议。双方各 34 项正确性通过；十个主协议桶及一个补充 read 桶分别冻结后，各 12 对独立进程，
共 264 次配对运行。独立 ≥200 ms 窗口按实际完成量测吞吐；不是固定工作量延迟或单次尾分位。

- 暖 cached guard、lookup、blank、未升级 intent 的生命周期吞吐为主干约 74%–86%，不是隔离管理 self。
- 预备 source 的 alias 为约 2.57%；真实 scanline 写为约 0.27%–0.39%；readBytes 为约 86.2%。这些属于操作级 E。
- 预绑定 memcpy 控制没有数量级差距，但保留反向偏移 pair；不能外推为普遍内核加速或 GPU/UMA 性能。
- 已确认 completion ticket 终态 QHash 和 provider replay QSet 的累计留存；尚未量化各自占比。固定-work 长桶尚未跑，
  先完成限时 rate，不能把潜在累计增长写成已发生 OOM，也不能以不同完成量下的 RSS 比证明每操作内存效率。

该结果支持继续重构 native CPU 访问/写入/提交，不支持仅调 memcpy 或把全部差值归给锁等待/某个 registry。
终态/防重放布局的长期有界研究加入 P5，不能替代 guard/session/permit 主线；压缩须保留 pending gap、乱序和失败终态、
identity 及拒绝重复操作。D4 分段仅解释 D4 对应 fixture，不乘 D5 吞吐比生成伪精确子阶段时间。
固定-work、尾延迟、M 不劣性、H/并发/压力、产品 replay 和完整 drain 仍待测，不授予 BR1-PERF Pass。

### 1.9 D6 检查点：累计完成记录压缩及反证驱动修正

[60](60_br1_completion_coverage_and_sparse_terminal_status_20260920.md) 在相同安全/统计脚手架下比较三种布局。
初版相邻同状态区间在交替终态桶慢2.807倍；尾部快路径仍有约1.47倍RSS。当前改为逐项完成的覆盖范围与稀疏失败/取消
记录，保留所有精确终态及pending gap。四个长桶各8对，当前时间比约0.094–0.420；记录数和同操作数RSS独立验证。
真实tiles3五桶各8对，写吞吐仅改善约2.9%–5.5%，cached guard未确认变化。组件/原生操作差异不能互相缩放。

已落地冷统计API与非法终态枚举拒绝；没有消除registry/PageStore全局锁。大量pending碎片/非成功状态、provider replay
QSet、root/history及完整drain仍需预算；不是普遍常量空间，也不是同主干资格。主线回到正式CPU访问与写发布路径，
不以继续微调registry替代P2/P3/P5。历史D5主干对照仍保留其版本边界，不把D6分支内比值相乘伪造新的主干结果。

### 1.10 D7 检查点：捕获一致性与完整读路径慢化

实现及反例见 [61](61_br1_captured_read_scope_and_integration_cost_20260920.md)：`KisCapturedReadView` 固定 root/page/default
metadata，CPU session/accessor/readRect/copyRect 来源使用同一 view；scope 内 identity lookup 无 owner 锁，但 pixel access
仍创建 generic request/lease。D6 混合 epoch 的回归反例已修正；D7 首版短 scope 重扫长期 retained history 也已修正，最后一个
旧 scope 的回收预算仍未证明。PageStore 单指针与旧 SessionStats ABI 保持。

15 桶各8对共240次配对：identity lookup 吞吐为 legacy selector 的1.8–2.5倍；包含 owning manifest/full-scan 的旧 scope
API 对照收益更大，但不代表原 session 已做过那些工作。真正 generic read session 的单页吞吐反而下降23%–25%、16页约3%–4%，
native adapter read 无材料级变化、真实写出现约0.9%反向偏移。保留这些未关闭偏差；不能以捕获语义或组件收益免除 M/E 回归。
下一步须接通 stable exact backing binding + page-local native pixel guard，并使 retire/eviction 看见同一 ownership gate；
不能只让 root 查表免锁，或通过删去 retention/pin/last-use 消除捕获成本。

### 1.11 后续 native read 草稿：源码存在与验证完成分开

本节保留 D8 归档前的静态复核检查点；下表描述**当时**的候选与待证项，不代表当前仍未构建/测试。
其后落实与实际证据见 1.12；两者均不改写 61 的 D7 二进制行为或测试结果：

| 源码位置 | 已可见的草稿路径 | 尚不能据此宣布 |
|---|---|---|
| `KisPageStore.{h,cpp}` | `KisCapturedReadView::tryReadResidentPage()` 与 move-only `KisCpuReadGuard`，释放顺序为 physical unpin 后 root release | 整个 operation 免全局锁、生命周期安全已验证或 P2 完成 |
| `KisPageMetadataCoordinator.cpp`、`KisCpuResidentBinding_p.h` | exact-version candidate 经 metadata shard 查找；首次 `call_once` 解析 provider record | 严格 lock-free、所有命中均无 provider 锁、冷 binding 零成本 |
| `KisCpuResidentBinding.cpp`、CPU/tiles3 providers | native/generic 访问、transfer 与 retire 尝试共用 allocation-local gate；tiles3 尝试 resident-only swap pin | 全部发布/退休/关闭入口已安全闭环，或共享 payload 已具备原位写资格 |
| `KisPageStoreCpuAccessSession.cpp` | 优先 native guard，失败回 generic；连续 read record 与 key→index 缓存 | 整个 scope 零分配、fallback 都是缺页，或旧 generic-request 断言仍适用 |

源码路径相对 `krita/libs/image/pagestore/`。验收需重新冻结源码、实际装载库、兼容 harness 与计量口径，先做生命周期/并发
和结构测试，再跑无 profiler 配对；不直接执行依赖旧 generic-request 数量的 fixture 后把其结论沿用给新路径。
首次 binding、暖 guard、完整 scope、真实写控制和最后旧 root 回收按 39 的 5.12 / 20 的 11.2 独立测量。
当时的空 guard 回退不能证明失败原因；须区分 unsupported provider、binding miss、busy、未驻留/未就绪与非法身份，
过渡 generic 路径计入软件缺口，不包装成真实硬件跨域成本。共享 default、mutation session/permit、完整回收预算仍未结清。

### 1.12 D8 检查点：原生像素读已接通，写侧反证未关闭

[62](62_br1_native_resident_read_and_write_cost_20260920.md) 与其证据目录绑定独立源码/运行库：captured view 经 exact-version
candidate、stable allocation record 和 page-local pin 返回只读 guard；CPU session/accessor/rect 来源优先 native，失败保留
同一视图的 generic 路径。native/generic read/write、transfer、retire 共用局部保护，guard 先 unpin 再 release root；
close/revoke、历史、并发、abort、swap-out 和 unsupported provider 等 native suite 共24项通过。失败原因已有显式 status，
但完整逻辑读/重试/锁 wait-hold 分段计量尚未全部落实，不能把接口存在写成全部观测项已测。

23 桶各8对，共184对/368次计时运行（另4次 loader 检查），均为 D8 对 D7 的分支内探索性吞吐诊断：
新 facade 单页 session 约3.17–3.48倍、16页 session/accessor 约11.6–12.2倍；包含实际拷贝的 rect 约1.49–2.19倍。
计时内含 scope capture/release，payload/binding 已暖，逐页 generic request 为零；不证明整个 scope 零分配或严格 lock-free。
原生控制组三个真实写桶慢约2.3%–4.8%，原生 read 另有约0.3%负偏移。写侧新增 record/candidate 分配、索引维护与共享 gate
是可检验假设，不是已测 self 归因；不从 CPU/操作差额直接给 mutex 或 allocator 分摊百分比。

下一候选因果对照为按首次 native read 建 binding cache：先冻结协议，再与 eager 版配对，保留读写/退休保护。
同时测首次 binding、暖读、只写/legacy 控制及完整生命周期，防止把成本从写侧移到窗口外；若仍超预算，再拆解 record
布局和重复同步。D8 未重测 upstream，未取得 M 不劣性、固定-work/单次尾延迟、高 H/并发性能或完整 drain 资格。
完整测试通过数及偏差存根以62为准；P2/P5仍部分完成，BR1-PERF与GPU/UMA资格状态不变。

### 1.13 D9 检查点：按需缓存收回部分写成本，但冷暖读均有反证

[63](63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md) 已完成1.12提出的eager/lazy对照。write/adoption/default/
generic read不再预建candidate；冷native读在captured root保护下查找ready exact CPU replica，锁外取provider，复验后装缓存。
provider record与read/write/transfer/retire gate不变。新增冷检查/测试证明纯写、generic读零cache条目，历史首次读、并发首次
reader、晚物化default和回收正确；ResidentRead28/read fixture33/Reference59/Foundation24/tiled88/native34/Vulkan13及架构检查通过。

48个配对桶各8对，共384对/768次计时运行，另12次loader；包括暖读、D8/D9和直接D7/D9原生控制、写发布→首次读周期、
inclusive区间诊断和埋点扰动。真写D9/D8吞吐约1.027–1.038，直接D9/D7约0.983–0.992，不授予写侧不劣性。
暖16页session/accessor约1.8%退化，CPU rect部分桶约3%–7.3%退化；首次16页read scope的配对时间比约1.70–1.73。
完整N64写/首次读周期变化较小，不能用它豁免冷读成本；phase时钟有反向扰动，不能把inclusive差额全归给binding/锁self。

D9检查点提出的下一候选：将暖cache lookup与冷候选发现分离，避免暖命中也构造/重置完整coldReplica；直接对D8/D9复测，不预定收益。
若guard恢复而rect仍慢，再拆输出buffer分配/清零、accessor与实际copy；高H冷版本查找、真实写残余、完整drain仍需研究。
D9原`lifecycle_ns`实际止于close返回，最终facade/provider容器析构未覆盖；下轮显式补齐，不把该字段名当成全生命周期证明。
不取消安全gate，不把首次成本移出窗口；D8/D9原件及负面结果均保留。BR1-PERF不结清，GPU/UMA未取得资格。

### 1.14 D10 检查点：暖路径部分恢复，首次读与写主线仍开放

[64](64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md) 已完成1.13的冷热分离对照：暖cache命中不再构造/
重置完整cold handle，冷miss增加一次shard查询后在锁外取provider并复验安装；root/pin/last-use及共享访问/retire gate不变。
14组111个配对桶各8对，共888对/1776次计时运行，另28次loader。新增held-view guard与固定256周期的容器析构端点，
同时保留完整session/accessor/rect、冷首次读、plain/profile扰动、直接D8及独立D7原生控制；不连乘历史比值。

相对D9，16页held-view guard吞吐改善约5%–7%，完整session/accessor约4%；这支持减少暖命中多余工作的方向。
但D8-relative宽格式rect仍有约2.8%–6.1%负中位偏移且区间较宽，tiles3 8BPP单页session约0.973［0.957–0.998］；
不能宣布全部恢复。首次16页read scope时间比D8约1.63–1.73，冷成本转移未关闭；它是inclusive区间，不是binding/锁self。
真实写D10/D9未确认变化，直接D10/D8约1.021–1.050、直接D10/D7约0.984–0.989；不授予写侧或主干性能资格。

新fixture的`lifecycle_ns`已覆盖configure到实际facade/provider容器析构，旧端点另存`configure_to_close_ns`；
固定工作量与rate窗口分开，D9原日志不补造时间。全局tiles3 pool/worker drain、长reader/高H/并发性能仍未测。
ResidentRead28/read fixture41/Reference59/Foundation24/tiled88/native34/Vulkan13及架构检查通过；Qt totals含init/cleanup。

下一研究同时保留两条线：校准暖读负偏移的环境/输出准备/accessor/copy归因；推进真实写的mutation/permit、
紧凑metadata与回收预算，不让读微基准代替P3/P4主线。当前协议没有记录每进程实际hash seed，不能把残差归因为它；
新诊断先冻结记录项和控制方案，固定seed只限benchmark子进程，并与生产默认环境独立复验。锁self、布局、后台活动
和rect初始化均是待验证变量。完整M/K/E及BR1-PERF仍未通过，GPU/UMA产品性能为NotMeasured。

### 1.15 D11 检查点：生产写段已接线，性能反证未关闭

[65](65_br1_native_cpu_mutation_segment_20260920.md) 将 `writeBytes()` 接到 owner-issued `KisCpuMutationSession` /
`KisCpuWriteGuard`：同一未发布段缓存 pending generation，不创建 generic write request/access lease；tile unlock
归还访问权，段结束统一 seal/proof，之后沿用 extent/root commit。history transaction 内每次操作仍是独立段，不吞并中间可见性。
provider 仍是同步 tiles3 CPU；不支持该 capability 时在开始前选择既有 generic 路径，不在失败后回放半次操作。

这是 P3 的**安全 COW 过渡子步骤**，不是原位 permit、page-local writer 全面落地、短发布或有界回收完成。
新页仍可能先物化 default before；每段真实修改仍做一次整页 COW；owner gate、claims QHash、metadata snapshot/proof
和兼容 lease/control block 仍存在。当时段持有每个 dirty page 的 binding 写排他与 RAM pin 至 seal/cancel；
当前 67 §13 已分离预约和 guard pin，本段历史性能结果不覆盖该变化，大 K 总工作集/尾延迟仍待最终验收。
17 项新生命周期测试和既有回归通过；history clear/default revision、失败 seal 只撤销本段、guard/batch 延迟取消均有覆盖。
分支内直接对照出现单页写吞吐约 **5%–6% 下降**、16 页写约 **8% 提升**，不能用零 request 覆盖反证；全部比对/缺测见65。
当前状态以第11/12节为准；不得继续把“写侧仅有 generic 接口”作为当前源码事实，也不得把此段原生化外推全部 iterator/brush。

### 1.16 D12 检查点：物理独占基础，不是原位 permit 完成

[66](66_br1_physical_exclusivity_prerequisite_20260920.md) 补充 TileData allocation 级 physical claim：已有 legacy/native/generic
像素 pin 通过同一 swap 锁排除，未知 provider alias/seed/lifetime ref 阻止 claim，新 ref 与 claim 线性化并等待其释放。
resident binding 接入该能力，但 PageStore 生产写仍走 D11 的新 allocation 安全 COW，未消费原位授权。
物理 gate 不替代 root/capture/retention、exact-before、不可失败提交或 alias 语义复验；不能以低层测试通过宣布 P3 完成。
正常 ref 热路径的变化必须用分别编译、匹配各自 runtime 的共同 fixture 复测，不允许旧 inline ref 与新 claim 协议混用。
实测、边界与剩余工作以66为准；BR1-PERF、GPU/UMA 产品资格仍不结清。

### 1.17 当前整体重构（未完成）

执行细目及缺口集中在 [67](67_br1_target_structure_reconstruction_20260920.md)。当前已推进源复制统一 writer gate、
owner-bound prepared epoch candidate、native virtual-default/discard 写准备、legacy tile 写与 CPU session 接入 native mutation，
删除 extent 的 persistent subtree bounds、root/transaction 的事件驱动回收候选索引。
2026-09-21 已建立事务 claim，并将 provider proof 验证、事务 delta、metadata 候选评估与 root 构造移出外层 owner gate；
发布时复验 head、retention、页面 revision 及默认页目录。候选 root 的内部 hash slot 不对读者/retention 暴露。
legacy tile 路径保留原 unlock 可见性边界；CPU session 按显式段 seal；二者不能混称所有 iterator 已有统一 operation scope。
retained restore 已统一 metadata-before-root；CPU session 已消费共享 default 并区分局部 gate/能力/物理驻留原因。
后续已将显式 opt-in 的 tiles3 CPU 配置接入后台历史/首次退休与分批树引用释放，并补齐 drain/close 协调，见 67 §9。
再后续已冻结 captured overlay 的 sealed delta、独立保留私有版本，并将生产 packed `readBytes` 与提交前默认页裁剪
接入原生驻留读，见 67 §10。随后独立 H/V/random 只读遍历、wrapped/repeat peers 和 planar read 接入固定 View，见 67 §11。
每个只读 cursor 最多缓存 4 对 current/before 页，exact version 相同只持一个 pin；packed/planar 每次至多一个页 pin。
同线程仍持有 legacy writer 的重叠读显式保留旧语义，不能自动 unlock/seal 并撤销业务裸指针，也不能声称是 immutable View。
该兼容分支、真实 brush/dab mutation 生命周期、直接 tile 写借用者以及全部生产入口贯通仍是未完成项；不能按新增 facade 数量结清。
默认 identity 跨 abort/undo 不复用；语义裁剪在应用删除前复验实际检查过的 exact version。
67 §12 将 generic/adoption 的按页 claim 前移至首次 provider 准备前，并贯穿 request/lease/terminal release，
native 首写/删除不再扫描全局 request/active-write map。未终结写/准备冻结本事务 surface/default 契约；
删除后复活仅与成功 proof 安装同时可见，generic exact default 读取不因其他版本 writer 存在而被错误拒绝。
这些是安全语义和冲突索引修正，不是物理 permit、完整 mutation O(1) 或无 owner gate 的证明。
67 §13 进一步拆分未发布 writer reservation 与 RAM pin：guard 归还后停放 pending backing，保持排他和版本，
再访重新 pin，真实 NonResident 才经 owner gate 外的同步 tiles3 swap control 恢复。生产 writeBytes 的目标 writable
pin 峰值在 2/32/256 dirty 页测试中为 1，但全 span session/legacy cache 仍按实际借用保活；不外推所有 pin 或总内存上界。
67 §14 将 RandomAccessor/SurfaceOps 接到显式 CursorPage：native 当前 target/before-image 各至多一个 guard，
页块遍历避免逐行跨页重复 pin；默认 OperationSpans 不缩短旧指针寿命，generic 未发布 write leases 仍保留。
这只关闭有移动边界的访问 pin 生命周期，copy 临时 buffer、全 dirty backing、所有 brush/dab 边界与性能资格仍开放。
67 §15 继续接通生产 planar 写及 trim 的部分页：一次业务操作共用 native 段，同页多个裁剪带不重复首写/seal。
删除和已确认空/全缺失通道不做像素准备；现有 alias/no-op/adoption 路径不退回像素循环。
嵌套拒绝、guard 尚存时失败及 compatibility index 范围在实际入口验证；语义 delta 的私有暂存/全段撤销尚未实现，
不能把 native pending 的取消外推到 caller history 已 sealed/staged 的修改。
batch 放弃由最后强引用终结，弱注册表槽位保留到匿名 client 结束；跨线程最后 unlock 与原线程重入有压力回归，
不把它等同于 TSAN 或整条管线无锁。私有语义 delta 的下一切片契约和混合故障验收见 67 §15.5。
67 §16 已落实删除/像素的私有 delta：canonical mutation 允许纯语义段不选择 CPU provider，旧 CPU session 为 source alias；
trim/clearAll/removePages 接入，旧 prepared 版本安全转 Historical，mutation metadata 候选全批复验再安装且不改 committed epoch tag。
混合失败保留旧 history，删除后重写复用 pending version/backing。67 §17 进一步接入 immutable source capability，
完整 clear/fillRect 和 PageStore → PageStore copy 的 alias/removal/部分像素共用私有段；实际 changed keys 才刷新索引。
输入引用不等于 RAM pin，alias 首写才必要 COW；整页替换不为 no-op 判定物化/扫描旧目标。混合 legacy-source 与已有 live
write intent 的复制保留兼容分流（67 §17.2），不能静默读 sealed 旧值，也不能将 live 分流计为 immutable copy 已迁移。
`operationSessionsCreated`、语义 removal、软件 default reset bytes 与 CPU pin/初始化、root publication 各自计量（20/67 §16.4），
不以重命名或新增 counter 代替真实入口/复杂度/性能验收。
67 §16.5 修正回收与历史恢复的控制边界：owner 分类后的 detached retirement 不再随机拒绝 undo；
close 可以轮询已保存的异步退休 operation，但仍须全部成功才完成。总 operation/debt 计数不删除，普通 provider
operation、source retention、冲突/metadata 复验保持原约束。此项有修复前确定性负样本，不以重跑绿替代归因。
mutable preparation 不再消费可能共享的 adoption seed；§17 的 native alias 使用显式私有 source，seal 时 adoption，
alias 后真实修改则独立 writable backing（已有 pending 可重初始化复用），不是将 aliased input 直接暴露为可写。
数量批次不等于完整时间/内存预算：单页长历史、root reachability、总队列背压和非 opt-in/GPU/I/O 进度仍须继续。
原位 permit、完整生产 read scope 与交接路径，以及仍在 owner 内的默认/删除输入组装、安装、后台分批历史评估须继续；
乐观重做需要记录实际工作量与尾延迟，不能据“准备外移”宣布短发布性能已达标。
67 §18 已将 mutation seal 的私有 metadata/completion、provider proof 与 detach 候选准备移出 owner，
transaction/PageKey claims 连续保留；同事务兄弟段按本段 key 合并。detach 使用紧凑语义 delta，不复制完整 page snapshot；
全部 exact Prepared/transaction/无 writer 检查与 claim 成功后，只修改当前 publication/preparedBy，保留最新 View/lease/pin/last-use。
读者变化不重做候选；成功后的 private page/source 销毁与退休移出 owner。首轮全 snapshot + 8 次重试实验造成正常并发失败，
已淘汰并保留反证（67 §18.3）。不同于 root commit 的严格 revision 重做，不授予固定延迟；输入、安装、单页历史与 map 合并仍须减量。
新增相位和两个 seal 候选计数见 20/67 §18，不把 inclusive 区间相加或把测试时间当性能证明。
67 §19 修复真实 painter bitBlt 的 source/mask 入口：不再将 const accessor 下转 mutable 后调用 rawData，
而使用公开 rawDataConst/明确 oldRawData，mask 始终选 captured current。修复前原 testSimpleBlt 的 SIGSEGV 已保留。
新增 72 个产品场景覆盖复制中途更新、history/default/wrap、外部 live writer 和重叠 self-copy；每个输入各自固定 View，
不宣称跨 owner 原子快照。§19 当时的目标端仍为 legacy writable accessor，操作级 writer 归属、同页首写复用与失败原子性没有因此完成。
已有 wrapper 可能复用外部 lease，不能靠外套 batch 悄悄合并其可见性；后续迁移必须先解决该归属并覆盖真实 producer。
新 painter 相位是 inclusive 业务段，composite 非纯 K、finish 非最终 drain；诊断日志不用于性能结论。
67 §20 现将正常 bitBlt 目标接入 `applyPixelOperation` 的显式私有段：目标专用 `KisPixelWriteCursor` 不含 oldRawData，
直接消费 mutation guard，避免不必要的目标 before-image View/pin；输入仍独立捕获。同页重访复用 pending，guard 换页归还，
完整操作后一次 seal；超范围/后页失败取消且不 replay。所有目标先分类/预约，native 争用等待整组、无部分持有；
已有 legacy 借用在 callback 前走兼容分支，同线程重入/嵌套 batch 先拒绝，范围预约不替代 owner 授权。
同时修复新操作和既有 CPU batch 私有取消污染共享匿名事务的实际丢数据：canonical cancel 确认私有段撤销后正常归还 client，
保留此前 sealed 页和外部 writer；操作仍失败，无法证明私有取消的失败仍事务级 abort。两例修复前失败已保留。
新增 range prepare/wait/body/finish 是 backend 业务相位；DataManager 先行扫描/探测/锁等待和后续索引锁等待仍须计入 M/E。
§20 的 15 套 951 passed、选定 9 passed、240 次重放检查点保留其历史版本，不改写旧样本。
全部 multi-dab/fill/line producer、legacy 归属最终迁移、owner-issued permit、完整短发布/历史布局/回收预算仍开放。
67 §21 将 metadata 的 page header 与独立 exact-version 记录分开：native 首写、私有 seal/cancel、capture token 和
proof 只读取/安装相关版本；physical-slot 全页索引提供冲突见证，不能遗漏旧历史中的同 slot。局部输入仍执行同一状态机，
§21 时未知转换/commit/restore/GC 保留完整路径；§22 继续迁移普通 root 候选，严格 revision/root 冲突协议不变。部分投影缺少历史不能作为原位 permit 证明。
真实 1/4/8/16 BPP × 0/7/63 个 retained overlay 的首写+重访+seal，局部输入 3、安装 4，前台完整 snapshot 导出 0；
这是子链工作量证据，不是整操作/后台 GC 与 H 无关或主干性能等价。完整 snapshot 与后台子集另计，索引内存和 fallback 成本仍纳入 M/E。
本轮还以负例修正 reference 与既有 optimistic 事务的矛盾：活动 writer 唯一，但独立 Prepared 版本可分别属于不同事务；
foreign read、物理 slot 唯一性及 root 冲突拒绝保留。§21 的 15 套 1017 passed、选定 9 passed、280 次重放作为历史检查点保留；
§20 live hashes 不再代表当前源码，不将新布局的正确性耗时当性能样本。
重构完成前不启动最终整体性能测试；旧反证全部保留。
67 §22 将普通 root commit/restore 改成 indexed candidate + publication delta：当前/目标/own Prepared 与必要冲突见证，
不复制无关 H；严格逐页 revision、多页 claim、metadata-before-root 协议不变。生产默认目录只读 header，删除/恢复取精确记录；
缺失默认版本及 descriptor 在候选成功安装时一起生效，不在预检修改 live history。同步 fused retirement 最多取 32 条记录/changed page，
超预算重试普通 commit + 后台收集；这不是全局回收预算。1/4/8/16 BPP × H=0/7/63 的真实提交输入/安装 2/2，恢复 3/2，
所测前台完整导出为零；这是工作量而非吞吐证据。当前正确性结果见 §22 的独立证据目录，旧 manifest 不覆盖。
未分类控制/GC、单版本动态列表、目录 N、root/descriptor 安装与重做/销毁成本仍计入完整 M/E；新 default/hash 仍可能在发布区分配。
67 §23 接着改造生产 history worker：ordered Historical index + identity cursor，每 key 32 条、每 pass 16 keys，
FIFO continuation 与外部事件后的完整重扫；只对选中的记录执行共享 discard guards，不导出/重装整页历史。
reachability 在同一轮跨切片复用，head 改变刷新，保护释放保守延迟到下一轮；完成/替换缓存在 owner 外销毁。
H=65/257 × 1/4/8/16 BPP 的保留、pin 释放与实际回收，以及跨 pass 恢复旧 generation 再写均验证。
GC 现在贡献 local transition，前台首写计数必须 total−background；退休移除与缓存 debt 单列，后台工作仍属于 E/drain。
root 集合刷新、单版本动态列表、非 background 兼容路径、索引分配与总队列预算仍开放，不能把 32×16 当硬时间/字节上限。
67 §26 的 root 资格与回收分离后，reachability 不再遍历所有物理注册 root：只查询 current、snapshot 保留和活动事务 base，
同一 root 去重，不随退休积压或重复 token 数量放大。最后保护释放、事务终结及新接入在同一 epoch gate 下决定；
旧 metadata copy 不授予保留权。合法长历史仍形成真实 R_live 成本，物理队列内存/背压、动态列表及全阶段时间预算仍须验收。
worker 同轮推进 root/finished-transaction 与 history 的独立预算，不再等前两类队列清空后才允许像素退休；积压中必须验证真实释放进度。
67 §27 将 root/finished-transaction FIFO 链接放进预先存在的 registry record，发布/最后保护释放只连 identity 链，
不扩展 dedup set/deque。hash relocation、候选取消与受保护 root 重新入队必须保持队列完整。消除的是 epoch 排队分配，
不是 metadata/default/history 插入、completion/后处理、worker 调度或真实析构全部无分配；不能据此签发原位许可。

## 2. 冻结方向：单一 canonical 模型，双执行路径

“双执行路径”不等于双权威：

```text
                  canonical PageStore semantics
            PageKey / PageVersion / epoch / authority
                              |
              +---------------+----------------+
              |                                |
    resident CPU native fast path     generic async control path
    cached handle + page-local pin    materialize / cross-domain /
    conditional COW + mutation scope  not-ready exact read / SSD / GPU
              |                                |
              +----------- same transition/proof --------+
```

- `KisTileData` 是 PageStore 的 native CPU replica，BR1 CPU-only 路径由其承载 authority；读侧可使用非 authority 的
  ready exact CPU 副本，不建立第二套像素真相；
- tiles3 hash 是稀疏 current-head cache/index，不是独立 generation ledger；
- PageStore 仍唯一拥有 PageVersion、epoch、writer exclusivity、history retention、authority 和跨域转换；
- resident CPU 命中可以通过等价的内联 transition/guard 完成，不要求创建通用 request 对象；
- 缺少可用 exact CPU 副本、需等待异步 producer/访问交接或需 swap-in/跨域/I/O 时使用通用 request/resolve；
  已驻留且就绪的历史版本读取与当前版本使用相同 native read 判据，不因历史身份绕行；
- reference model 保持 oracle，不得作为生产容器或热路径实现。

## 3. 必须落地的 CPU API

### 3.1 读路径

内部 API 需要明确区分快路径与 materialization：

```cpp
CapturedReadView captureReadView(ImageEpochSelector selector);

CpuReadGuard tryAcquireResidentCpuRead(
    CachedPageHandle &handle,
    const CapturedReadView &view,
    CpuReadOptions options = {});

MaterializationRequest acquireNonResidentRead(
    PageKey key,
    const CapturedReadView &view,
    AccessRequirement requirement,
    Priority priority);
```

`CapturedReadView` 是持有 immutable root retention 的 move-only capability，不是未计数 raw root pointer；它必须参与
内部 `KisPageWriteCoordinator` 的 handoff eligibility/gate 协议，确保“检查后新捕获的旧 root”不能形成 TOCTOU。

`CpuReadGuard` 必须是 move-only、栈上/内联友好的短期对象，持有 exact `PageVersion`、CPU span/stride、page-local
pin 和必要的 swap-block token。成功 resident 命中不得：

- 分配 request/lease heap node；
- 插入全局 request/lease map；
- 获取 PageStore 全局 mutex；
- 通过 provider 扫描 active leases 反查 pointer；
- 创建 default page record 或物理 allocation；
- 逐 tile 捕获新的 ImageEpoch。

推荐读取时序：

```text
operation/accessor 开始时捕获一次 read view/root
-> 查 CachedPageHandle 或稀疏 tiles3 hash
-> 未分配坐标直接返回 shared/virtual default view
-> resident CPU page：page-local pin + blockSwapping
-> 校验 cached generation/epoch tag；失配时从 root 刷新一次
-> 返回 CpuReadGuard
-> guard 析构时 unblock/unpin
```

快路径资格为：受保护视图中的所需 exact generation 已有 CPU 可读的 valid replica，所需访问顺序/可见性已满足，且能
安全取得局部 pin。它可以是 CpuRam 或 UmaShared，也可以是非 authority 副本或 retained 历史版本。
cached handle miss/tag 失配先在该视图中重新 resolve；virtual-default miss 返回匹配该视图 format/default revision 的共享
只读 view，都不等于需要 materialization。只有缺少上述可用副本、待完成 producer/访问交接，或确需 swap-in/跨域/I/O
才进入通用路径；失效 capability/version 是错误，不应以迁移掩盖。局部竞争按有界重试/延后策略处理，不伪造物理缺页。
降级完成后可以填充 `CachedPageHandle`，但 cache 不能成为可见性线性化点。这是读侧判据，不放宽写侧 authority handoff、
writer exclusivity、COW 或 3.3 的 write-plan 证明。

这里的“resident 命中零请求/免全局锁”限定于已捕获 scope 内的像素访问，不把 capture/release 或首次 binding 的成本
删出操作 M/E。payload 驻留与 binding/cache 冷暖必须分别描述；短 shard/page 锁和首次 provider lookup 如实计量。
原生 try 未成功不自动等于物理缺页；过渡能力不足、binding 未接通与局部 busy 单列为软件原因，不能让未分类 fallback
绕过 P2/P5 出口。具体结果分类与计量按 39 的 5.12、20 的 11.2，不强制把诊断字段加入公共 ABI。

guard 的 root retention 只保护逻辑版本，physical pin 防止 backing swap/复用，异步 last-use 保护尚未完成的 GPU/I/O。
generic/native 访问、transfer、retire/eviction 和 close 必须共享可验证的寿命协调，先复验回收资格再撤销 metadata，
不能忽略 provider 拒绝退休造成隐藏 pin/泄漏。allocation-local record 也不证明被多个 handle alias 的 payload 独占；
读 guard 的接通不授予 3.3 的原位写 permit。

### 3.2 写路径与 mutation scope

```cpp
KisPageMutationSession KisPageStore::beginMutation(
    const KisPageTransaction &transaction,
    QString *error);

KisCpuWriteGuard KisPageMutationSession::beginWrite(
    const KisPageKey &key,
    KisPageWriteMode mode,
    QString *error);

bool KisPageMutationSession::seal(QString *error);
bool KisPageMutationSession::cancel();
```

`KisPageMutationSession` 是明确的 RAII transaction facade。其 store-scoped coordinator、entry/write-set、claim、prepared commit 和
managed batch 的最终字段及状态迁移冻结在 [68 §4](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md#4-统一能力封装类型边界与调用方式)，
本节不再定义平行抽象类型。iterator/accessor、区域 copy/clear、paint operation 和 stroke batch必须在算法边界创建 session；不得依赖
定时器或“相邻短写自动合并”猜测业务事务。write intent 是 session 内部值，不暴露 writable pointer；`beginWrite()` 才执行
first-write transition 并返回可写 span。暂未迁移的 legacy
单页写可以创建立即提交的 single-page session，但 `lockForWrite()` 一旦暴露裸可写指针就必须等价于调用
`beginWrite()`，不能事后猜测调用者是否写入。该兼容路径不得成为 paint/iterator/bulk operation 的生产热路径。

同一 session 内每个 PageKey 只允许一次 first-write transition：

```text
首次可变访问：G -> reserve G+1 -> retain before G -> 选择原位或一次 COW
后续访问同页：复用 pending G+1 和同一 writable replica
每次 guard release：归还 RAM pin、清除裸指针、合并 dirty；scope 保留未发布 writer reservation
session commit：每个 dirty page seal 一次，增量更新 extent，一次 root commit
```

访问权与 physical pin 不能混为一项：如果段在 guard 间仍保留可用 writable pointer，必须保留等价的 backing pin 保护。
D11 当时持有 pin 至 seal/cancel；当前 67 §13 清除 pointer、保留局部预约，允许 parked backing 换出而拒绝外部 read/write/transfer/retire。
再访同一 generation 重新 pin，不以换出为由再次 COW。只有真实 NonResident 进入现有同步 CPU 恢复控制路径，
不是零 pin 成本、完整异步控制或全部大 K 场景已合格。全 span session/legacy 借用保活、总 dirty 记账与尾延迟仍需验收。
只生成内部 `KisPageWriteIntent` 而未升级为 writable guard 的页面不得分配新 generation、复制 allocation 或产生 proof；已经
暴露 writable pointer 的 guard 按 dirty 处理。`unlock()` 不是 epoch commit 的同义词。

“每 session/页一次”限定于同一**未发布的可写版本**。如果业务需要中途发布或允许外部 exact reader 捕获结果，必须先
seal/发布并结束该段 mutation；后续写进入新段并重新取得 writer/COW 资格。不能为减少 generation/COW 而覆写已可见
版本、吞并原有中间可见性，或把同一 history transaction 内全部访问默认当成一个可复用 writable session。
新段仍可在 owner 重新选择 3.3 的有效 handoff plan 后复用物理 allocation；这里禁止的是沿用旧可写授权，而非禁止安全原位写。

#### 3.2.1 Exact source 直接初始化 native COW backing

设计出发点是 57 确认的 preserve 两遍 payload 工作。58 已消除 `createDefaultTileData → default fill → source transfer`
的冗余初始化并测到 provider 子路径与完整操作收益；尚未把 allocator/填充/协议的独立 self 成本完全分离。继续推进
通用请求外壳与 session 复用，不从本切片承诺后续倍数；已选定接口及下面各项契约必须同时成立：

- 为就绪且布局兼容的同 provider/epoch、同 CPU 存储域 exact source 提供显式 native 初始化能力；以主干
  `duplicateTileData` 的预克隆/直接复制为对照，目标新 backing 直接由 source 初始化，不先填一遍将被全部覆写的 default。
  partial write 仍须保留未改区域；virtual default、discard 和真正跨域 materialization 各按自己的语义处理，不能一并删掉必要初始化。
- 这是独立新 backing 的安全 COW，不是原位写 permit。provider 调用前保护 source 版本/寿命与 residency，拒绝正在
  可变写入的 source；旧 reader/history 可继续访问旧内容，abort 不破坏旧 root。不可只凭裸指针或引用计数判断安全。
- provider 能力、source handle、operation、目标 generation/layout 及终态须明确验证；锁外执行后仍复验 transaction、
  writer、provider epoch 和 lifetime。成功返回已经初始化的目标时不得再 transfer；失败或竞态丢弃目标须完整清理，不得
  把已执行的失败操作静默重放为另一条初始化路径。未具备能力时在执行前选择既有安全路径。
- 复用一个同步 native 初始化原语不等于正式 `KisCpuWriteGuard/KisPageMutationSession` 完成；request map、owner gate、
  completion、重复 first-write 等剩余工作继续按各自 counter 和 M/E 门禁审计。
- 先补 provider 实际 default-initialized、explicit-copy、native-duplicate、adopted 页数/逻辑字节；预克隆命中、后台补充、
  reserve 占用及最终 drain 另报。native duplicate 的逻辑字节不是前台 memcpy 或 DRAM 流量，预克隆命中也不等于总复制为零。

验收覆盖 4/8/16 BPP、partial write、保留 reader/history、同页重复写、abort、provider 失效/过期 completion、预算失败和
clone 后首次写。初始化结构计数、像素/生命周期正确性、同 harness before/after 与 upstream 资格分别记录；切片 before/after
不能替代主干配对。完整计量规则见 20 的 11.1、39 的 5.10，最终 P3 出口仍包含 3.3 的内部 write-plan/handoff 和每 session 同一未发布段内每页一次 first-write。

D4 已落实 `synchronousWriteCopy/prepareSynchronousWriteCopy`、tiles3 native duplicate、失败清理、实际 provider 计数和
本节主要负例（58）。这仅完成初始化切片；后台 preclone 工作/峰值 reserve、更多失效并发组合及原位/session 全部出口仍未结清。

### 3.3 backing handoff 安全矩阵（取代公共原位 permit）

本节早期版本使用 `InPlaceWritePermit` 描述安全边界；[68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md)
现已将其收敛为 PageStore 私有、store-scoped 的 `KisPageWriteCoordinator`。它生成内联 `KisPageWritePlan`；session 持有 write set，
只有 physical claim 和 `KisPreparedMutationCommit` 承担一次消费的资源所有权。painter、iterator、provider 和其他调用方不得持有或自签公共 permit。
PageStore 原子地把 allocation A 从 G 转交给 pending G+1，并选择以下一种可证明模式：

1. **`HandoffRecoverable`**：G 的 exact bytes 已由 immutable before backing、delta/journal 或其他 valid replica 保留；
   G 的旧 root/read 仍可 materialize，G+1 可以复用 A；
2. **`HandoffCommitOnly`**：仅用于完全预检、首字节写入后不可普通 abort 的受控内部 kernel。
   write plan 在检查与 publish 之间阻止新的 old-root capture、retained snapshot 和 G read acquisition；
   `CurrentCommitted` reader 在 gate 后重新捕获 root。多页 Prepared transaction、长生命周期 session 和可失败 producer
   不得使用这种无 before backing 的模式。

选择任一 handoff plan 的共同条件针对**将被覆盖的 physical allocation A**，不能把 G 的逻辑引用与 A 的物理访问混同：

- CPU replica 是 G 的 authority 且 allocation 可写；
- `KisTileData`/replica 的像素所有权独占，没有 clone/shared users；
- A 没有 active/pending-last-use reader，也没有 GPU/I/O in-flight consumer、materialization source pin 或 retirement ticket；
- 当前 writer 是该 PageKey 唯一 writer，不能覆盖任何仍作为 immutable before-image 对外暴露的 A；
- PageStore 能在同一线性化边界内 reserve writer、复验 root/snapshot/read retention、锁定 allocation，并建立上述
  recoverability 或 capture gate；检查后不得留下新消费者插入的 TOCTOU 窗口；计划还必须预占对应 backing/retirement 字节预算。

逻辑 retention 分模式处理：exclusive-immediate 必须没有需保留 G 的外部 memento/undo/save/retained epoch/exact-version/
transaction-before 引用；recoverable-before 可以保留这些 G 引用，但它们之后只能解析到受保护的 exact-before backing，
不能再读已用于 G+1 的 A，且已有 raw reader/pin 不能靠改 metadata 强制搬走。建立副本/保存 delta 的成本全部计入 E。
这澄清了“有可恢复 before”和“一律不准存在 G 的逻辑 retention”的旧措辞冲突，不放宽物理独占或旧像素恢复要求。

D11 实审发现的必要入口检查：legacy `KisTile::lockForRead()` 的 native-ready 路径直接 pin TileData，未必经过新的
binding reader 计数；多个 provider record 还可 alias 同一 payload。write-plan selector 必须先让 legacy/native/generic 的实际 reader、
alias 创建、swap pin、capture/retention 同属可线性化保护；单个 binding 的 readers==0 不证明 A 独占。禁止先开原位写
再补这些门禁，具体研究边界见65第6节。

D12 的 `tryAcquireExclusiveWrite(ownedStorageReferences, ownedStorageUsers)` 仅是内部 physical claim。参数必须来自调用者
持有并串行保护的已知 owner/record，不得读取实际 refcount 后原样传入。已有合法 ref/pin 与正在创建的新 alias 均需协调；
不能把防换出 shared pin、binding 内 writer 排他与跨 alias 的 physical exclusivity 当作同一事实。claim 本身保活 allocation，
释放前不准在本线程重新 ref/acquire/pin 它。先准备未来的 identity/ownership record，再尝试 claim；现有 write intent 的
自身 shared pin 需在受保护边界内移交，竞争失败回 COW，不能直接升级锁。物理 claim 释放后，等待的 alias 仍须由上层
重新证明其 exact version；“等到了指针”不是旧 G 内容仍有效的证明。首字节前的 owner write-plan/handoff 协议尚待实现。
后续接线前还需统一provider native duplicate的source访问与binding writer gate；D12收尾发现的generic `activeWriter`
与native writer覆盖差异、provider锁顺序风险列在66的`D12-ProviderSourceGate`，不得略过这类旁路入口审计。

任一条件不满足时只在首次写入执行一次物理 COW。判断必须由 PageStore/CPU replica metadata 给出，不允许调用者只看
`usersCount == 1` 自行覆盖；后者只是安全判定的一部分。guard 只引用 session entry，physical claim/prepared mutation commit 一次消费。
首字节被修改后，若没有
recoverable-before，流程只能成功 publish 或以不可失败的内存内恢复终结，不能再执行可能失败的 allocation/I/O/provider
操作。原位写后仍必须生成新的 `PageVersion`、dirty delta 和 commit proof，不能把“复用 allocation”误写成“复用
generation”。

### 3.4 Memento 和 history

吸收 upstream 成熟的“first change only”算法：一个 mutation/undo transaction 对同一页只记录一次 before reference，
commit 后记录 after reference。记录内容是 before/after `PageVersion` retention，不是复制第二份 tiles3 真相。

- 无 history reader 时仍须取得 `HandoffRecoverable` 或 `HandoffCommitOnly` 计划，不能只按瞬时引用计数原位覆盖；
- 有 history retention 时 first-write COW 保留旧 allocation 或先建立可恢复 exact backing；
- rollback/rollforward 发布单调的新 ImageEpoch/commit sequence，root 可重新选择被 retention 保护的旧 exact PageVersion；
  新写的 generation 分配高水位不回退、不复用，不能误要求每次历史 head 切换都重造一份像素 generation；
- history GC 按 root/version 可达性回收，不扫描每次访问产生的临时 lease 表。

## 4. 生产 epoch 与索引布局

生产 root 必须采用 persistent radix tree、HAMT、B-tree 或复杂度等价的结构共享映射。当前过渡实现已在
`KisImageEpochReferenceModel` 内把 root 替换为结构共享平衡树，并让 sparse commit 和 history restore 直接使用该 root；
但 owner 名称/职责仍是 reference model，公共 `KisImageEpochSnapshot` 仍携带 owning `QVector`，因此还不是 P4 的最终
production API 边界：

```text
commit K changed pages into N-page manifest: O(K log N) time
new root memory:                           O(K log N)
read exact page:                           O(log N) or bounded radix depth
unchanged page payload/reference copy:     0
full manifest export/sort:                 only explicit serialization/debug
```

生产 API 不返回 owning `QVector<PageEntry>` 作为日常 epoch snapshot。允许：

- immutable root handle；
- cursor/range iterator；
- changed-page delta；
- 按需 lookup；
- 显式、标注为 cold-path 的序列化导出。

extent/default metadata 与 root 同 epoch 提交，但 extent 由 changed-page delta 和空间索引增量维护；普通 commit 不得扫描完整
manifest。default/empty page 使用 surface-level sentinel 和共享只读数据，读取任意空白坐标不得实例化 PageKey/page version/
replica。

## 5. 与 GPU/UMA 共用的成熟设计

CPU 快路径不是特殊旁路，而是后续 backend 应复用的局部性原则：

| Krita 成熟 CPU 机制 | PageStore/GPU/UMA 对应设计 |
|---|---|
| shared default tile | virtual default generation；GPU shared read-only default binding |
| `usersCount` 条件 COW | generation retention/pin 决定 first-write COW |
| `blockSwapping()` | residency pin + last-use ticket，防止 in-flight backing 移动 |
| tile-local lock | page-local writer token / shard，不用全局串行热访问 |
| memento first-change delta | before/after generation delta journal |
| 增量 extent | changed-page spatial index，不扫 manifest |
| tile pool/preclone | page arena、预分配与预测驻留 |
| 延迟释放旧 tile data | ticket-qualified retirement |
| accessor/session | 一次 capture epoch、批量 access plan、immutable binding snapshot |
| accessor hot-tile cache/line preload | scope-owned cached handles + pin set；像素循环零 lookup/pin |
| fused current/old `getTilesPair()` | current/before PageVersion pair 一次 root/cache resolve |
| lock-free sparse hash + deferred GC | read-mostly sparse head index + epoch/hazard/ticket retirement |
| full-tile shared clone/default clear removal | immutable backing alias/virtual sentinel，first-write 才私有化 |
| fixed-size tile pools + background preclone | per-StorageClass page arena、reserve watermark、异步 COW preparation |

UMA 同一已驻留、布局兼容的 PageVersion shared backing，其 CPU mapped pointer 与 GPU binding 指向同一物理页；
交接执行必要的 ordering、cache maintenance 和 ticket handoff，不做 CPU↔GPU payload migration。GPU stroke 按显式
mutation/publication batch 捕获 epoch、按 page 聚合 dabs；同一未发布段每页 reserve 一次 G+1、执行该段 dabs、产生
completion，并以 batch 一次 commit；禁止 per-dab request/submit/wait，不能跨已发布段复用可写版本。
这里的零复制只排除满足上述条件的 payload migration；不把必要同步或执行等待记零，
也不把 COW/undo、SSD 换入或 derived copy 隐去。CPU-only 且没有 GPU 访问交接时，不执行无用 binding/submit/ownership 工作。

这些结构优化只消除不必要开销，不保证所有 GPU 都快。后续 GPU/UMA 的性能基线必须是同机启用 SIMD/线程优化的实际
CPU product path，而不是 scalar reference。零拷贝、GPU timestamp 和 capability 可用都不能单独触发产品 route；完整
compile/residency/queue/cache-maintenance/commit/visibility ETA 留有收益余量时才在首次写前整操作选择 accelerator，
否则保持 CPU。定量门禁、GPU 劣势 profile 和迟滞/降级规则统一见 39。

### 5.1 同域管理对照与跨域产品对照

- BR1 先以相同 CPU/CpuRam、共同管理语义做 M 配对，另测真实像素 K 与包含原生 iterator/管理生命周期的 resident E。
  不把 K 预先获取指针后得到的吞吐当作整个 tile/PageStore API 吞吐。
- GPU 阶段补同域 direct/VT 控制组：GPU/VRAM 对 GPU/VRAM，GPU/shared 对 GPU/shared；与主干 CPU/RAM 的比值另标
  异构驻留算子性能，不能据此证明管理开销。direct 仅作隔离测试，不新增生产 authority。
- GPU/UMA provider 的实际 host-side 管理另作 M 测量；共同生命周期对主干，实际异构执行新增 binding/proof/ticket 等
  工作给绝对预算；不能把同义操作的内部记账重分类免责，也不能以 CPU bridge 的 M 通过代替 GPU 管理证据。shader 寻址属于 K。
- CPU/shared 对 CPU/CpuRam 使用相同 CPU 算子，read/write/RMW 分桶；GPU remote-host 与 CPU BAR-mapped 不合入 UMA。
  共享物理页、可映射和 host coherent 都不证明访问延迟/带宽与原生 RAM 相同。
- X 记录跨域上传/读回及 cache/ownership；同域 COW/default fill 等准备列入 E 子阶段，copy reason 独立标记且不重复计时。
  E 根据 CpuReadable/GpuConsumable/Visible 等相同端点付真实交付成本，不强制无用读回，也不漏必要上传；条件 route
  使用已有 exact valid replicas，不只看 authority。
- M 与 E 两道独立门禁都要通过；显存/执行器优势不能掩盖 CPU 管理回归，管理层优化也不能替代整条 VT 吞吐和尾延迟。

## 6. 实施阶段

### P1：测量冻结与防回归测试

- 固化 upstream/current 的 commit、构建参数、测试命令、墙钟、CPU、RSS、allocation/page/request/commit 计数；
- 冻结 M/K/X/E paired baseline、共同语义/新增语义、访问域及 InitialState→RequiredEndpoint；BR1 先落实 CPU/CpuRam，
  GPU/UMA 项标 NotMeasured 并留在后续对应阶段，不能用 CPU-only 或 fake 结果替代；
- 按 39 的 5.6 冻结 M 不劣性容差、近零基线绝对容差、required bucket、置信水平和配对采样/停止规则；单列
  Pass/Fail/Inconclusive/NotMeasured。差异不显著或只通过完整操作阶段上限，均不构成管理等价；
- M fixture 按实际调用链核查 setup、source backing 初始化和 drain；alias 类隔离管理配对使用双方同样预备的 immutable
  backing，被移出计时的必要数据准备仍另测并保留在完整生命周期 E，必要 allocation 的管理部分仍计入 M。
  已有 clear/alias 桶不直接改名为纯 M；
- M 测共同管理 API 的 self/生命周期总成本与 N/K/H；K 测已驻留真实像素，E 测原 iterator/operation 总吞吐和延迟；
  trace 中每项复制、setup/commit/retire 有归属，无 profiler 的产品计时独立保留；
- 增加 32767+ blank coordinate read，断言 page/version/replica allocation 为 0；
- 增加 cached-handle miss 但 exact RAM resident、retained 历史已驻留、非 CPU authority 但有 ready exact CPU 副本的
  读路径测试，断言无通用 request/迁移；与真正 non-resident、pending producer、stale generation/provider 的负例配对。
  非 CPU authority 用状态机/fake provider 证明路由正确性即可，不能据此声称真实 GPU/UMA 性能已测；
- 增加同一未发布 mutation/session 段重复写同页，断言最多一次 generation reserve、一次物理 COW、一次 seal；
  中途发布后新段须重新取得 writer/permit，不把整段 history transaction 混为一次可写授权。增加 intent 未升级测试，
  断言 generation/allocation/proof 为 0；
- 增加 K 固定、N 扩大的 epoch commit benchmark，证明成本不随 N 线性增长；
- 在任何重构前建立像素、COW、undo、save、并发和故障差分基线。
- 固定到达时间、线程/in-flight 和 batch，分别做交互延迟与持续完成吞吐；不能扩大 batch 后用倒数代替单操作延迟。

出口：性能放大项能由 counter 逐项定位，测试可在 CI 稳定复现。

### P2：virtual default 与 resident read fast path

- default page 改为 surface sentinel/shared immutable view；
- 覆盖 virgin read、write→default clear、trim/remove、undo/redo-to-default、retention purge 的完整生命周期；删除映射不得
  为每个坐标重新 allocation/fill 一个 default tile，retained 历史按需保存 exact identity，不能制造新 default payload；
- default/alias/已知 uniform 操作带精确内容属性，避免 commit prune 再走 generic read/逐像素比较；裸 mutable pointer
  暴露后属性必须失效，不能用未验证的 hash 或旧 default revision 当作内容等价证明；
- 引入 `CapturedReadView`、`CachedPageHandle`、`CpuReadGuard`；
- resident 命中只做局部 pin/校验，去掉 request map、heap lease 和 provider 反查；
- D8 已为新 CPU facade 接通 native 像素读与共享 gate；D9按需cache、D10冷热分离已有1.13–1.14/63–64的对照。
  宽格式/首次读及真实写残余继续登记，不定为最优布局；只写/旧traversal不应代付未使用的读缓存，冷读成本仍计入M/E。
  D10诊断收尾不等待所有读微基准最优，D11已按第12节转向生产写段，后续继续其结构硬项；
- accessor/iterator 在操作级捕获一次 view，并缓存当前/相邻 page handle；
- accessor 按 traversal 持有 hot-page pin set，nested guard 只在 first/last access 改 pin；current/old view fused resolve；
- 保留 read-mostly sparse index 与 deferred reclamation，不能换成全局锁 `QHash`；
- cache miss 先受保护地 resolve；default miss 返回共享 view。仅真实副本/就绪性缺失需要通用 materialization/异步交接，
  完成后回填 cache；resident 历史或非 authority 的合法 CPU 副本不得仅因标签不同走慢路径。

出口：空白读取零页面实例化；同义 resident-read 管理通过预冻结不劣性判据；swap/retained exact read 语义不回退。

### P3：mutation session、条件 backing handoff 与 first-write COW

- 3.2.1 的 exact-source native 初始化与 provider payload 计数已在 D4 落实；继续补后台 preclone/峰值 reserve/drain，
  不得把本切片单独写成 native write 管线完成；
- 收敛到 public `KisPageMutationSession/KisCpuWriteGuard` 与内部 `KisPageWriteIntent` 两阶段 API；
- 把 dirty、proof、extent 和 commit 从 tile unlock 移到 session finish；
- 实作 PageStore 私有 `KisPageWriteCoordinator`、inline plan/claim 与完整 handoff 安全矩阵；否则首写一次 COW，并仅在同一未发布
  mutation/session 段重用 pending G+1；seal/发布后新段重新选择 write plan，满足 handoff 时仍可复用物理 allocation；
- memento 只登记 first-change before/after PageVersion；
- full-tile clone/copy 共享 immutable backing，default full clear 移除 mapping，相同 fill 可共享只读 backing；partial tile 才复制；
- 为常用 StorageClass 保留 payload arena/cache 和受预算约束的 COW reserve，避免在交互线程冷分配；
- 未升级 write intent 零 generation/allocation；legacy writable-pointer exposure 明确计为 dirty。

出口：重复写放大消失；无旧值保留且满足 handoff 的普通 resident write 稳定实现零 before-image copy、零新 payload allocation、
零退休 payload；必要 COW/undo/reader 并发 property test 与 tiny-budget 背压矩阵全绿，峰值 backing bytes 不越硬上限。

### P4：production persistent epoch root 与增量 metadata

- 将 reference `QVector/QHash` 退出 production commit/read path（persistent balanced root 已接入；独立 production owner 和
  非 owning cursor ABI 未完成）；
- 接入 persistent root、changed-page delta 和 cursor API；
- extent/region/default metadata 增量提交；
- delta 必须贯穿 tiles3 adapter/index；`rollback/rollforward` 不得以 `rebuildPageStoreIndex()` 把底层 O(K) 变回 O(N)；
- begin transaction 只取 root/epoch handle，不能为取得 epoch id 调用完整 `captureCommittedEpoch()`；D2-A 已以
  `beginCurrentTransaction()` 接入匿名事务起点，capture 和 base retention 在同一 owner gate 内完成（55）；
- 将 per-page current-head cache 明确为 epoch-tagged cache，而非 authority；
- 为 root/history/GC 加复杂度、占用和并发读门禁。
- owner-held prepared batch 尽量一次生成/验证提交记录，发布时复验冲突及生命周期变化；metadata 紧凑记录与完整 diagnostic
  snapshot 分离。能力绑定、一次消费和 reader/last-use/abort/reset 失效边界按 33 的 6.1；不得靠关闭验证达标，也不得在
  root 已可见后补齐 reader 所需版本/authority 数据。D2-B 已实装同步 owner-held 切片并做 reference/并发负例核对（56）；
  仍需将生产候选布局、全部发布入口和锁外准备/动态复验推进到完整目标，不能把同步缓存视为 P4 结清。

出口：K-page commit 的时延和分配量只随 K/树深变化；普通提交无全 manifest export/sort/scan。

### P5：安全免全局锁读路径、provider 与分配清理

- 已捕获 scope 内的 resident CPU 像素热访问不持 PageStore 全局 mutex；capture/release 的短 gate 单独计入操作成本；
  不同页并行准备，同页 writer 独占，root 发布允许短临界区串行化；
  不要求全系统严格 lock-free，不以自旋/CAS 替换 mutex 的名称变化作为成果；
- page/shard 锁只保护短 transition，provider 调用始终锁外；
- 发布前准备完整 immutable version/root 和必要退休记录；读者在解引用前取得经过验证的 lifetime protection，再建立
  retention/pin。generation 校验不能单独防 UAF，RCU/hazard 也不能保护被原位覆盖的旧像素；原位写仍服从 3.3；
- D3 已冻结并一次发布 shard directory、移除热 lookup 配置锁，但没有确认性能收益，也未消除页面锁/owner gate；
  不再把此已完成的结构改动列为待办。计时/计数器分线程或采样化须有扰动证据，不能删掉关键安全校验；分别量化
  锁等待、持锁执行、自旋/重试与统计本身成本；
- CPU provider 通过 guard 内保存的 opaque token O(1) resolve，不扫描 active leases；
- fast guard 使用 slab/inline storage 或纯栈对象；通用异步 request 才进入 owner map；
- D8 scope 内原生读已避开 owner/request map，但 capture/release、metadata shard、局部 gate 与首次 provider/once 仍有成本。
  CPU 历史 GC 的安全证明依赖 retained root；未来 replica eviction/异步 handoff 必须先接入等价协调，不照搬忽略 retire 失败的假设；
- lookup/pin、payload allocation、root allocation 和 retire 四类内存路径分别计数，防止 root 优化掩盖 payload 抖动；
- 保留 operation id、provider epoch、allocation generation 和 stale completion 校验。
- D5 定位的逐 ticket completion 留存已在D6改为完成覆盖与稀疏非成功状态，并补冷统计/同累计操作数测量；provider
  `consumedOperations`仍未改。完成覆盖只合并已逐项确认的相邻值，允许跨终态合并覆盖但必须独立保留每个值的真实状态；
  不能跨pending gap或以大host ticket推断小ticket完成。乱序、失败/取消、重复操作及身份负例必须保留。
  补大量pending碎片、非成功记录、replay、root/history和drain的字节/CPU/峰值预算；压缩不自动证明最坏空间有界，
  所有replay/retire结构须各自给安全回收证明。60保留同状态区间方案的性能/RSS反证，不能沿用该原候选作为当前布局。
- retire 同时等待 root/history retention、CPU backing pin 与 GPU/I/O last-use，设置积压预算/有界 drain；报告操作 E 及
  drained CPU/wall/峰值占用，禁止通过无界推迟回收或强制复用未结束对象获得表面低延迟。

出口：多页并行访问可按 shard/page 扩展，resident hit 无 heap/global-map/provider-scan 放大。

### P6：全量差分、文档与 BR1-PERF 结清

- 运行 tiles3、iterator、paint device、transaction、save/reopen、PageStore property/fault 全套；
- 复跑本文审计 workload 和长时内存压力；
- 交付 CPU 阶段 M/K/resident E 的独立结论及整合表，包含吞吐/延迟、管理预算、初末状态、采样扰动、回收积压；
- M 按预冻结容差与配对置信界证明同义管理不劣于主干；所有 required bucket 和完整 E 均通过，不能以证据不足或
  额外语义单列代替结清；
- 验证 CPU/OpenGL 产品路径，Vulkan 产品入口保持关闭；
- 新增最终双维度结清证据（functional/correctness + performance/layout），51 只追加导航，不改写其历史结果；
- 只有全部门禁达成后，31 才能把下一 production 阶段切为 BR2。

### 6.1 代码落位与禁止混放

下表路径均相对 `krita/libs/image/`：

| 位置 | 必须落实的职责 | 不得继续承担 |
|---|---|---|
| `pagestore/KisPageStoreTypes.h`、owner API header `KisPageStore.h` | backend-neutral identity/契约；owner-issued RAII capability 可在 owner header 声明（D7 `KisCapturedReadView`、D8 `KisCpuReadGuard`）；write-plan 对调用方保持私有 | Vulkan 类型、裸 provider pointer、owning manifest vector、公共 `InPlaceWritePermit`；公开 reference root 内部布局 |
| `pagestore/KisPageStore.{h,cpp}` | 通用异步路径；共享 transition validator；内部 write-plan selector、backing ledger/handoff 与 root/read capture gate；fast-path fallback | resident hit 的 heap request/global-map 必经路径；调用方自签 physical exclusivity |
| 新 production epoch owner（不得继续塞入 `KisImageEpochReferenceModel`） | persistent root、lookup/cursor、changed-page commit、root retention/GC | reference `QHash/QVector/sort` adapter |
| `pagestore/KisImageEpochReferenceModel.*` | property/fault oracle、trace comparison | tiles3 accessor、production commit、extent 计算 |
| `pagestore/KisTiledDataManagerPageStoreBackend.*` | operation-level read view/mutation session、epoch-tagged handle cache、一次性 seal/root commit | per-tile transaction commit、完整 manifest extent scan |
| `tiles3/KisTilePageStoreBridge.h`、`tiles3/kis_tile.*` | page-local/nested guard 生命周期；只在 first/last access pin；移除 `getTile()`/lock 的重复 refresh | 直接创建通用 request、业务事务聚合 |
| `pagestore/KisTiles3PageReplicaProvider.*` | allocation token 到 `KisTileData` 的 O(1) resolve、pin/last-use | `tileDataForLeasedPointer()` 的 active-lease 线性反查 |
| `tiles3/kis_tile_hash_table2.h` | 保留 shared default、并发稀疏 lookup 与 deferred reclamation，cache entry 带 canonical tag | 自建 generation/history authority或全局锁 lookup |
| `tiles3/kis_tile_data.*`、`kis_tile_data_pooler.*`、`kis_tile_data_store.*` | 保留连续页、StorageClass pool/cache、受预算 COW reserve；逐步收口为 CPU replica arena | 与 PageStore root 共用一个大锁/allocator，或无界预克隆 |
| `tiles3/KisTiledExtentManager.*` | 消费 changed-page delta、增量维护空间边界 | 从完整 PageStore manifest 重算每次 commit |
| `pagestore/KisPageStoreMementoManager.*`、`tiles3/kis_memento_manager.*` | first-change before/after PageVersion retention | 每次 write lock 重复复制/登记同页 |
| `pagestore/KisPageStoreCpuAccessSession.*`、`KisPageStoreRandomAccessor.*`、`KisPageStoreLineIterator.*` 与现有 tiles3 iterator | 在算法边界持有 view/session/hot pin set，fused resolve current/before，跨 tile 复用 cached handle | 每次坐标/像素捕获 root、pin 或等待 materialization |

测试落位：

- `libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp`：blank/default、stress、lazy-copying 和 extent scaling；
- `libs/image/tiles3/tests/kis_tiles3_cpu_baseline_test.cpp`：D5 同源 upstream/current 的 guard/lookup/intent、预备 source alias、
  真实 read/write 和预绑定 memcpy；当前只有 H=0 暖路径诊断，不替代 retained reader/并发或完整产品验收；
- `libs/image/tests/KisPageStoreReferenceTest.cpp`：fast/slow trace 等价、permit TOCTOU、retention、K/N complexity；
- `libs/image/tests/KisPageStoreFoundationTest.cpp`：move-only 类型、非法 capability、reference/production 边界；
- `libs/image/tests/KisPageStoreResidentReadTest.cpp`：D8 native/generic 交互、root/backing寿命、并发/retire/abort/revoke/swap负例；
- `libs/image/tests/KisPageStoreReadBaselineTest.cpp`：同捕获语义下的session/accessor/rect配对，双方明确expected requests/page；
  D8仅有暖binding吞吐，不冒充冷self、固定-work/尾延迟或完整drain；
- `libs/image/tests/KisCompletionRegistryTest.cpp`：完成覆盖/真实终态、pending gap、乱序oracle、并发/重放拒绝与记录增长；
  组件计时不替代tiles3的M/K/E，实际字节与全生命周期另测；
- iterator、transaction、paint-device、save/reopen 现有测试继续承担产品语义差分，不能只新增 isolated microbench。
- performance harness/报告器落实 20 的 run header 与 39 的 M/K/X/E：上游同义管理 fixture、CPU 同域 K、resident E，
  以及后续 Vulkan 同域 direct/VT、X 与 W0–W8。不能为让上游适配新协议而改变其原生 tile 算法；额外语义单列绝对成本。

文件名可以在实现时按 Krita 命名规范调整，但上述 owner 边界不可合并回“一个 PageStore mutex + 一个 reference
manifest + 一个通用 lease map”。

## 7. 性能与结构出口

以下是 BR1-PERF 的最低门槛，均使用同机同构建 profile 的 upstream 基线；原始数据和方差必须保存：

小于计时分辨率/噪声下限的用例先以固定重复次数扩展到 upstream 中位数至少 100 ms，再比较单位操作成本；不能把
审计表中的“<1 ms”直接乘以阈值。计时样本预热后至少重复 5 次，报告 median、range/方差、RSS 和结构 counter；
5 个 run 不能支撑稳定 P95/P99。尾延迟另以足量操作事件/独立 replay 统计，报告样本量、事件单位和不确定性。
固定 seed 只固定每 worker 的操作流，不固定线程交错及删除的实际页数；scaling 必须同时固定/报告实际 page work。
profiler 和正式计时分开，竞争 workload 不并发运行；wall、thread CPU、锁等待与采样栈占用不得混作同一分母。详见 53。

下表的数值上限约束相应**完整 CPU 操作**，不是隔离像素 K 的上限，也不是 GPU/VRAM 对 CPU/RAM 的管理倍率。M 的
共同语义管理须另按 39 的 5.6 证明不劣于主干，管理预算/容差须在配对基线冻结时预先分配，并与结构 counter 独立验收；
真正无主干同义项的对外语义给绝对预算并保留在 E，内部记账不能借此排除。吞吐按固定资源和
endpoint 事前冻结，不把延迟倍率取倒数当作吞吐门禁。K 比较有益但不单独结清，最终须由原产品路径的 resident E 验证。

| 类别 | 门槛 |
|---|---|
| blank/default read | 任意空白坐标零 PageKey/version/replica allocation；像素 backing 为 O(1)；墙钟不高于 upstream 1.2× |
| resident read | 代表性 iterator/accessor benchmark 不高于 upstream 1.2× |
| resident write，无 history | 不高于 upstream 1.3×；满足条件的常见桶由内部 plan 选择 backing handoff，并达到零 before copy/新 payload allocation/migration/retirement payload |
| first-write COW/undo | 不高于 upstream 1.5×；每页每 mutation 的同一未发布段至多一次 COW |
| `stressTest` / `stressTestLazyCopying` | 两项均不高于 upstream 1.5×，且像素/extent/history 等价 |
| epoch commit | K 固定、N 扩大时不存在 O(N) rebuild/sort/scan；符合 `O(K log N)` 设计 |
| resident fast path | 0 heap request/lease、0 global request-map insert、0 provider active-lease scan、0 implicit epoch commit per tile unlock |
| accessor locality | 像素循环 0 root lookup/0 pin；page transition 至多一次 fused current/before resolve，pin 按 scope first/last 计数 |
| clone/clear | compatible full-page clone 零像素 copy；default full clear 删除 mapping；COW reserve 不产生不可控交互尾延迟 |
| correctness | BR1 既有 property/fault/CPU tests 全绿，无双 authority、stale acceptance 或历史破坏 |
| 管理独立证明 M | CPU/CpuRam 同义 tile 管理逐 required bucket 通过 39 的预冻结不劣性容差/置信界；新增语义预算及 N/K/H/锁/分配/回收证据齐全，K/E 加速不能抵消其回归 |
| 吞吐与延迟整合 K/E | 同域 K 与含管理的 resident E 分开；完成量、端点、并发/到达率一致，吞吐与尾延迟均通过预先冻结 profile |

1.2×/1.3×/1.5× 是完整操作阶段上限，不是长期性能目标或 M 等价容差；不能单凭满足这些倍率声明管理等价/BR1-PERF 结清。
同义管理不劣性与完整 E 同时验收；更快且语义相同的实现允许通过。只降低总耗时但违反结构门禁，或只通过 microbenchmark
而产品 stress 仍超限，都不得结清。M 容差/采样未冻结或置信证据不足时保持未通过，不用“无显著差异”代替等价。

## 8. 回退与决策点

如果 P2–P5 证明当前 tiles3 PageStore bridge 无法在不扩大 ABI 风险的情况下表达 native fast path，应采用可恢复回退：

1. 关闭当前 PageStore-backed tiles3 产品桥；
2. 恢复 upstream 成熟 CPU 产品路径作为唯一启用路径；
3. PageStore core/reference/provider 在隔离测试中继续演进；
4. 完成 fast API、persistent root 和差分门禁后再一次性 cutover；
5. GPU/UMA 仍不得启用、不得建立另一 authority、不得用 stroke-end 双写弥补。

回退的是尚未达标的接入粒度，不是 canonical PageStore 设计。禁止为了保留现有代码形状而接受数量级退化，也禁止通过
双写或将 tiles3 降为事后镜像来换取表面性能。

## 9. 变更纪律

- 每个实现提交同时注明消除的放大项、保持的不变量、相关 counter 和 before/after 数据；
- 按 39 的 5.10 保存版本化证据链及偏差登记（54）；结构通过但性能未测时明确标注，不复用旧采样作为当前热点结论；
- API 如不能表达零分配 resident fast path，应先调整 API，不能把错误抽象用缓存层掩盖；
- reference model 的便利容器不得通过 typedef、adapter 或 snapshot export 重新进入生产热路径；
- 性能修复不得删除 operation/provider/ABA 校验，只能把校验下沉为 O(1) cached token 或局部 transition；
- 任何“BR1 完成”声明必须同时引用 51 的功能证据和本文最终性能证据。

## 10. 原始审核判断的文档落地对照与校正

本表只回答“判断是否已经转化为规范、代码落位和门禁”，不代表对应代码已经全部完成；实际实现完成度唯一以第 11 节为准。

| 审核判断 | 规范落点 | 结论 |
|---|---|---|
| PageStore 方向正确、CPU 接入层次错误 | 本文 1–2；25 的 5.4；32 的永久决策 | 已冻结为 control plane + resident data plane |
| default 物化、重复 acquire、lease 反查是直接问题 | 本文 1、P2/P5；30 的 6.4 | 规范已明确代码落位、counter 和负向守卫 |
| per-lock request/COW/commit 是粒度问题 | 本文 3/P3；17 的 access session；33 的 5.5 | 规范已冻结 two-stage write + mutation scope；代码仅部分完成，见 11 |
| reference manifest/extent 是生产结构缺失 | 本文 4/P4；33 的 2.5/6；46–47 校正 | persistent root/changed delta 为必选，不再是建议 |
| mainline read/default/COW/memento/extent 应吸收 | 本文 1.1/5；25、35 | 规范已补齐 accessor cache、fused old/current、稀疏索引、pool/preclone、full-page alias |
| 只优化通用 request 无法达标 | 本文 7–8 | 保留 upstream CPU 产品路径作为未达标时的受控回退 |
| GPU/UMA 复用 first-write、pin、batch、retirement | 本文 5；15、32、35 | 设计已同步到 GPU/UMA 权威文档 |
| GPU 劣势时不得严重慢于 CPU | 39 的 8.1/10.2；10、30、32、35 | 规范已增加实际 CPU product baseline、前置 route、迟滞和 1.10×/1.25× 硬门禁 |
| VT 管理与 RAM Tile 吞吐/延迟须分别证明再整合 | 39 的 5.6–5.9/10；20 的 2.3/11；本文 P1/P6/7 | 已定义同域/异构配对、初末状态、比值和 M/K/X/E；59 已测部分 CPU 窗口吞吐，完整资格仍未取得 |
| CPU 管理不劣于主干，UMA 仅物理迁移复制为零 | 本文 0/3.1/5/7；25/33 的 resident 边界；39 的 5.6/5.7 | 已定义独立不劣性判据及副本就绪性快路径；不把软件残余或必要同步伪装为零/硬件必然成本，测量尚待完成 |

两处原判断不能按字面直接实现，已在规范中收紧：

1. upstream default miss 共享的是像素 `KisTileData`，仍可能创建短期 tile wrapper；目标实现允许更优的栈上 virtual view，
   但硬要求是零 PageKey/version/replica 和 O(1) pixel backing，而不是误称主干“完全零对象”；
2. 暴露裸 writable pointer 后无法可靠判断 no-op，且“当前无 reader/memento”不足以保护 immutable old root。因此写侧采用
   内部 `KisPageWriteIntent -> beginWrite()`，由 PageStore 内部 coordinator/inline plan 选择条件 handoff 或必要 COW；普通多页 Prepared
   transaction 在没有 exact-before、完整预检和首字节后不可失败发布链时禁止无 before handoff。

## 11. P1–P6 当前完成度与下一实施顺序

“已落地”列只列已验证切片及其限定范围；D10–D12 为历史阶段，当前结构切片与正确性证据以 1.17/67 为准。
旧检查点不沿用为当前状态；物理claim未被owner消费，不把它记成原位写已完成。
正式 M/K/E 资格仍未取得；“待结清”不等于源码中完全没有候选实现。

| 阶段 | 当前完成度 | 已落地 | 未结清硬项 |
|---|---|---|---|
| P1 | 部分完成 | 历史upstream及53–64诊断；D11共400次（65）；D12直接D11/固定upstream各11桶×8对，共352次（66） | M不劣性容差/采样冻结、隔离self、完整固定-work主干差分/事件尾统计、K/N/H/并发sweep、产品真写replay；D12负偏移/控制桶变动、后台drain及环境校准 |
| P2 | 部分完成 | D1/D7–D10 读布局；67 的 frozen sealed overlay、revision-qualified shared default、独立 H/V/random/wrapped/repeat 与 packed/planar 固定 View/有界 pin cache；§19 painter source/mask 的公开 const 契约及真实交错回归 | live-writer 重叠读及完整 brush 写边界、通用 default/冷 binding 与坐标 metadata 有界性；current/before 更细的 fused resolve；历史负偏移、独立 M/产品验收 |
| P3 | 部分完成 | two-stage intent/batch/adoption/no-op；D4 native COW、D11 段内复用、D12 physical claim；67 按页 claim、parked writer；§14–17 私有语义 delta；§20 bitBlt 目标段；§24 packed 固定 View/缩锁；§25 完整输入直接初始化与 pending 复用 | metadata stable-slot arena；legacy-source copy/冷源准备；统一 coordinator/inline-plan selector、recoverable/commit-only handoff；普通 discard/fallback 填充、swapped pending 完整覆盖重载；其余 multi-dab/fill/line 与重叠读迁移；D11 K1/D12 负偏移、全 span/legacy 借用、generic write leases、总 dirty/backing 预算、preclone 及主干差分资格 |
| P4 | 部分完成 | persistent root/extent；锁外候选与 metadata-before-root；§18 detach；§21 独立记录；§22 root delta/精确预检/default 候选；§23 Historical index/local discard；§26 root admission；§27 预存 epoch 退休链接 | root/descriptor/目录输入、安装/销毁/重做；未分类控制/同步兼容 GC、adapter、合法 R_live reachability 刷新和总预算；完整 K/N/H 证据 |
| P5 | 部分完成 | CPU opt-in 后台历史/退休、分批树释放及 drain/close；§23 单页 32 记录续扫、FIFO、事件重扫及每轮可达性缓存；§26 只遍历 distinct 受保护 roots；§32 metadata cleanup 按 unit/time 分批且可 drain | 合法 R_live 刷新、单记录动态列表；current/retained/pending/in-flight/retiring backing 精确字节 ledger、硬上限、高低水位、背压与 `ResourcePressure`；candidate unit 预算不得冒充 payload 字节预算；同步 K-token 归还；非 opt-in/GPU/I/O 进度与完整尾统计 |
| P6 | 未开始结清 | §21–25 检查点保留；§26/27 补 root 准入、释放竞争、退休积压进度、identity 链接及预算边界；correctness 时间不是性能 | 产品全量/CPU/OpenGL长压、新 native/write-plan/handoff 并发矩阵、tiny-budget 压力/恢复、读残差/D11 K1回归/D12负偏移、M不劣性及配对K/E吞吐/尾统计、最终结清；GPU/UMA待实测 |

下一实施顺序由59/65的直接主干差距、58/60的收益及61–65的接入/成本转移反证共同校准，各报告保留版本边界。
D10已完成冷热查询分离与直接D8/D9复测；按1.14/64保留宽格式/单页负偏移、冷首次读和直接D7真写残余。
读侧补测先冻结环境/布局记录及控制诊断，再分buffer准备/accessor/copy；不把未记录的hash seed或后台活动写成原因。
这不是生产写迁移的前置阻塞项：D11 已按第12节接通 writeBytes 的安全 COW 段，record/重复同步与 K1 回归随该生产路径一起归因。
固定256周期已补局部析构，完整后台drain另测。不得删安全gate或移出窗口关闭反证。
并继续推进同一未发布session段的first-write复用、mutation/permit及K1 finish / K16访问与批量发布的分桶研究。
D7不得退回追逐current head的旧session，D8也不代表所有legacy traversal已接入；39的5.12冷热/完整操作门禁继续有效。
各切片源码/运行库/采样协议分别冻结；D9/D10直接D7对照不等于upstream，不连乘历史比值重算D5主干差距。
D6已压缩completion成功历史，真实写只改善约2.9%–5.5%；provider replay与全生命周期预算仍待研究，不以此替代原生路径重构；
不再把配置锁或 commit 单段当作主要真实写瓶颈。D1 的零新 default payload 不替代长期/全产品成本转移验收；
D2-A 已消除事务起点 O(N)，D2-B 已实现同步 owner-held prepared metadata batch；继续研究 adoption/proof、GC/retire、
candidate 生产布局与动态保护。prepare/发布/GC/retire 总工作全部计入，不能靠关闭必要校验达标。
精确 uniform/alias 属性、history/index delta 与 production root/cursor 随切片证据推进；真实写 workload 单独驱动
`KisPageMutationSession + KisPageWriteCoordinator/inline-plan/BackingHandoff`
及 iterator/accessor guard 重构。每个切片必须重新测量后排序，不能用既定 API 名称代替瓶颈证据。
3.794 秒只是历史 upstream 2.529 秒乘以 1.5 的示意上限；stress 完整操作单项按新同机配对 upstream 的 1.5× 验收，
不能替代新增 M 不劣性与其余出口。
lazy-copy 单项通过不替代整体出口；GPU/UMA route 仍只能以最终成熟 CPU product path 为分母。

## 12. 按目标结构推进，防止 Dx 退化为局部调参

### 12.1 当前源码对照：部分落地，不是目标全链路完成

D7/D8 是 captured view/native read 的结构迁移；D9/D10 是该迁移引入成本的必要修复和计量补全。它们不能代替
真实写、短发布和有界回收。D11 已转向生产写路径的首个子步骤，读缓存残差作为独立研究项保留，不要求先把每个读桶调到最优。
此排序不豁免任何最终读性能门禁，也不允许已知数据损坏/寿命错误带病迁移。

| 目标节点 | 当前源码事实 | 尚缺的结构，不以类名或局部倍率替代 |
|---|---|---|
| 操作级受保护 view | committed/base/frozen sealed overlay；独立 H/V/random、wrapped/repeat、packed/planar 已接入；§19 真实 painter source/mask 消费公开 const View | 活跃 writer 的重叠读仍是显式 legacy 观察；brush/dab mutation 边界与直接 tile 借用者迁移；不隐式撤销裸写指针、不宣称跨 owner 联合快照 |
| 稀疏索引/缓存、驻留局部pin | D8/D10 native binding；tiles3 只读 cursor 4 对 hot pins，packed/planar 单页 pin；67 §13 parked writer 保留排他；§14 PageStore accessor 当前 target/before guard、同页 span 复用与区域页块遍历 | 完整 handle/traversal 融合及所有生产入口；默认全 span/legacy 借用、generic write leases、copy 临时 buffer、总 dirty set 无相同上界；capture/release、重复 pin 与冷恢复计成本 |
| 空白共享view、慢路径materialization | CPU session/oldData 已消费 revision-qualified 共享 default，局部 gate 等待与真正 nonresident 分流 | 全生产入口贯通、完整冷 binding/执行交接；try失败不能一律当硬件缺页 |
| 显式mutation与同页复用 | packed/planar、trim、legacy tile 与 CPU session；§16–17 私有语义 delta；§20 bitBlt 直接 guard；§24 packed 固定 View/缩锁；§25 完整输入初始化/同段复用；确认私有取消才健康归还共享 client | 统一 write-plan/handoff、普通 discard/fallback 及其余 producer 完整覆盖消费、swapped pending 重载、混合 legacy-source/外部 live writer 最终归属、其余 multi-dab/fill/line 及整段失败协议；不能外推全部画笔贯通 |
| 局部writer与条件COW | backend同页reservation、D11段内复用；67 §12 将 native/control 首写冲突改为按页索引并覆盖锁外准备/terminal release；D4直接初始化COW；D12 physical claim | 仍有 owner gate，不等于完整 page-local 热路径；其余入口段内复用；PageStore 私有 selector 与 recoverable/commit-only handoff；不把每次真实修改固定为整页COW |
| 删除/整页别名语义delta | 私有 removal/alias/像素一次 seal，immutable source 首写才必要 COW；实际 changed keys 刷新缓存；删除 extent 沿 persistent subtree bounds/delta 计算（67 §16–17） | default prune 精确内容属性、剩余入口的 history/adapter 增量化仍未齐 |
| 批量prepare与短root发布 | claim、锁外候选与多维复验、metadata-before-root；§18 紧凑 detach；§21 独立记录；§22 indexed root delta、精确生产预检、默认恢复候选与单页 fused 预算 | 未分类控制/GC 仍有全历史工作，目录 N、root/descriptor/新增记录安装及销毁仍有 owner 成本；不是原位许可或 root 陈旧合并，完整临界区/重做仍待测 |
| 延迟回收与全部寿命满足 | CPU opt-in 的历史/首次退休/树引用在后台分批处理；root retention、CPU pin/last-use 独立，显式 drain/close 协调（67 §9） | 单页长历史/可达性评估、同步 overlay token 释放、总积压/背压及完整 drain 的成本证据；非 opt-in/GPU/I/O 产品路径未验证 |

关键源码：
历史读写 session（`KisPageStoreCpuAccessSession.cpp:182` 已迁移，后续见 [67](67_br1_target_structure_reconstruction_20260920.md)）、
[生产writeBytes与batch](../../../../../krita/libs/image/tiles3/kis_tiled_data_manager.cc:1095)、
[tile lease finish](../../../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:192)、
[最后batch客户端提交](../../../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:348)、
[删除extent准备](../../../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp)、
[owner commit与scope释放回收](../../../../../krita/libs/image/pagestore/KisPageStore.cpp)。历史行号只对应当时版本；当前以符号与 67 工作检查点为准。

两条必须避免的过度归纳：

1. `writeBytes()` 的batch会把root commit延后到最后客户端，不能写“所有tile unlock都独立commit root”。旧 generic tile lease
   finish仍执行publish/proof；D11 native段则在guard结束时归还访问权，段末统一seal，同页复用已被计数验证。
   不能把旧路径行为覆盖到新路径，也不能外推全部入口已迁移；新段仍重新授权，当前仍每段COW。
2. production owner仍持`KisImageEpochReferenceModel`，但其root已经结构共享，sparse commit按路径更新，history restore复用root。
   不能凭ReferenceModel名称宣布这些优化不存在，也不能改名即视为P4完成；实际缺口是owner/oracle职责分离、紧凑page/version
   记录、cursor、剩余snapshot复制/扫描、临界区及复杂度。dense rebuild有K/N触发条件，不能把它外推为每次稀疏commit全量重建。

### 12.2 D10 的收尾边界

D10的**实现/诊断切片**以64的源码、回归、冷热/真实写对照、局部析构端点和证据封存完成为界；不以全部读性能最优为界。
D10-WarmResidual、ColdTradeoff、WriteResidual、Endpoint、Environment五项存根继续开放，不能写成性能关闭。
已有正确性/生命周期错误必须先修；没有新证据不得把宽区间负偏移直接判为噪声。读残差的定向实验可继续，但不再作为
下一主要架构切片；BR1-PERF整体与任何正式M/K/E资格仍不结清。

### 12.3 真实生产写路径纵向贯通（D11 已完成安全 COW 子步骤，整体未完成）

优先选择已有共同fixture能覆盖的`KisTiledDataManager::writeBytes()`，不是再建一个只在新facade里更快的演示API。
实现前先冻结当前候选与固定upstream基线，审阅实际访问/中间可见性/abort语义；源码与二进制固定到各自证据中，
需要更新upstream时显式重新冻结，不能把`9a24ae0d8c`称为未验证的“最新主干”。

交付链条必须贯通：

`生产入口 → mutation起点/base保护 → 局部writer/写意图 → 首次beginWrite → pending复用 → seal/proof → extent/root发布 → retirement`

- 首次 beginWrite 由 owner coordinator 选择 `ReusePending/HandoffRecoverable/HandoffCommitOnly/FreshPayload/FreshDiscard/FreshCow/SemanticOnly`，
  不默认每次都复制整页；同一未发布段复用 pending，guard release
  归还可写访问权并累计dirty；scope保留或移交独占backing保护，不能让未发布可写页在guard间被移动/回收。
  段结束每页seal一次。中途发布或暴露exact observer后新段重新授权，不能暗中吞并可见性。
- handoff 模式按 3.3/68 先完成 API/安全审阅：区分 allocation 上的直接 reader/pin、逻辑 root retention、alias 及可恢复 before。
  瞬时`usersCount==1`或“没有reader”不足以授权。普通可abort多页事务无exact-before时继续COW；exclusive-immediate
  的capture gate、首字节后的不可失败提交/恢复必须闭环。不能先删COW再补安全协议。
- 可先分子步骤落地安全 COW+pending 复用、再接内部 handoff，但前者仅是过渡成果；**write-plan、handoff 和硬 backing
  budget 未落实时不得宣布 P3 或 CPU 写性能目标完成**。
  不能将通用request包进名为MutationSession的类就算原生数据路径完成。
- 短发布是纵向切片的显式依赖：prepared batch绑定transaction/provider epoch、writer和root-retention claims，锁外完成
  可失败准备/分配/完整校验，发布区仅复验会变化的冲突/寿命事实并安装已就绪metadata/root。未有等价保护时保留安全锁，
  将该段列为未完成；不能为降低hold time而先发布、后补metadata，或把重试重建成本移出E。
- 明确标出本切片覆盖的入口和保留的legacy/generic fallback；后续实际accessor/iterator/brush迁移另列，不以一个入口
  证明所有生产路径已完成。shared default/current-before及fallback分类继续作为P2未结清项跟踪。

最小证据必须同时包含结构和完整操作：

- 同页重复访问、K1/K16、partial/scanline、4/8/16 BPP、reader/history/alias、intent未升级、abort/失败以及中途发布后新段。
  每个真实段记录generation reserve、allocation、实际copy reason/bytes、generic request、proof/seal、root commit和retire数量。
- 固定K扩大N及H，计量prepare/发布/adapter/最后释放的wall、CPU、wait/hold、分配与处理页数；有观测缺口标缺测，
  不能只凭结构预言E改善。新增计量先校准关闭态/开启态，不在所有短函数无条件加时钟。
- 同源生产入口直接配对候选与upstream，管理M、驻留算子K、完整E分别判定；另保留当前分支前后配对以区分收益来源。
  D5旧比值不与D6–D10连乘，read facade提速不抵消真写回归；正式不劣性容差/样本/停止规则在采样前冻结。
- 必要 COW、history 与 abort 语义同主干/既有 contract 差分；write-plan/handoff 的并发 capture、alias、in-flight、失败与
  tiny-budget 负例单独验证。通过正确性不等于性能 Pass。

### 12.4 后续顺序与方向纠偏门槛

在纵向写路径基础上推进短发布的全部入口、删除extent空间索引、history delta贯通adapter和有界回收；这些是同一目标结构
的剩余阶段，不是写优化失败后的可选补丁。回收必须有每批数量/时间预算、积压峰值/持续时间、长reader及GPU/I/O未完成时
的保留/背压策略；绝不能为有界而强制复用仍在用的backing，也不能只把前台成本藏到后台。

后续每个Dx必须回答：迁移了哪个真实生产入口？消除了哪个结构放大？哪些必要工作仍存在？最新直接M/K/E和完整生命周期
是否符合预期？若结构计数已下降而完整E不改善，记录反证、校准工作量/端点并重排剩余成本；不得仅增加更多读缓存微基准。
若充分实现native session/permit/布局后仍无法达到主干目标，再按第8节评估受控回退/重构，不提前把未完成实现判成PageStore
方向失败，也不无限延期性能结清。

### 12.5 发布存储准备检查点（67 §28）

已有 record 转 Historical 的 ordered-index node 和 bounded fused replacement record-set 已由 move-only publication candidate 持有，
在全页 claim/复验通过后才 transfer/swap；失败候选不改 live index。该变化落实了“可失败分配先准备、发布时只安装已就绪结构”的
一部分，并以 prepared/transferred、prepared/installed 成对计数验证，而不是用 root 赋值耗时替代完整发布成本。

此检查点没有关闭新增 default record/descriptor 插入、旧 record-set 在外层 owner gate 内析构、completion/postwork，也没有把 commit
变成不可失败。因而 owner-issued in-place permit 仍不得接入：capture fence、recoverable-before 或 exclusive-immediate 协议、allocation
retag/旧 binding 失效和首字节后的完整无失败路径仍须共同完成。证据见
[67 §28](67_br1_target_structure_reconstruction_20260920.md#28-2026-09-21metadata-候选持有发布所需存储)。

### 12.6 新增 default record 的后续关闭（67 §29）

普通 root publication 的新增 default record 现由候选持有 owning list node，并在准备阶段按 exact page revision 为 live exact/slot hash
预留容量；安装 splice 节点且断言 capacity 不变，不复制 H。新增 record 的 prepared/transferred 计数与 history/fused 计数分离。

这把 §12.5 所列“新增 metadata record”从开放项移除，但 descriptor 插入、completion、旧 set 外层 owner 析构与回收 postwork 仍开放。
容量预留持有局部 shard gate，取消可留下非语义 capacity，且未用 allocator hook 证明 Qt insert 零调用；因此仍不能声称完整短发布或 permit。
实现边界与证据见 [67 §29](67_br1_target_structure_reconstruction_20260920.md#29-2026-09-21新增-default-record-的候选存储与容量准备)。

### 12.7 descriptor 发布容量（67 §30）

所有 owner descriptor 语义增删已有统一 revision；default commit/restore 在解锁构造 metadata/root 之前预留候选新增容量，重锁后复验
revision，callback 安装断言 capacity 不增长。无关私有 generation 的 descriptor churn 当前保守触发重做，并计入 E。

reserve 仍短持较早 owner gate，Qt insert 未经 allocator hook；completion、candidate/旧 record 析构与 postwork 仍在后续发布面。
所以 §12.6 的 descriptor **扩容**缺口关闭，但完整 descriptor 成本、短发布和 permit 不关闭。见
[67 §30](67_br1_target_structure_reconstruction_20260920.md#30-2026-09-21descriptor-容量准备与解锁期变更复验)。

### 12.8 publication cleanup ownership（67 §31）

commit/restore 的 metadata candidate、失败候选和 fused swap 换出的旧 record-set 现通过 move-only cleanup 交接，并在 PageStore owner gate
外同步销毁；成功 commit 在开锁前先 retain 新 epoch，保证 cleanup 间隙仍有合法 root 保护。由此关闭“隐式候选析构延长最终 owner
临界区”的已知缺口。

这不是总回收预算完成：同步 clear 仍计入 E，mutation install 尚未接出 cleanup，effects/proof/container/provider retirement 也未统一。
下一阶段应以真实队列记录数/字节/时间预算和背压验证，而不是只观察 owner hold 缩短。completion、capture fence、retag/rollback 与
不可失败发布仍是原位 permit 前置条件。见
[67 §31](67_br1_target_structure_reconstruction_20260920.md#31-2026-09-21publication-cleanup-所有权移出-owner-gate)。

### 12.9 分批 cleanup 与 host-ready evidence（67 §32）

超过 8 candidate-page units 的 metadata cleanup 现进入单线程 reclaimer，每 pass 至多 16 units，并在 unit 间检查 1 ms；mutation 与 root
publication 都接入，pending/peak/pass/queue time 可观测，wait/close 可 drain。小候选继续 owner 外同步，避免把 K1 热路径变成线程调度。

同步 host work 使用 configure 时一次建立的已完成 evidence，commit/restore 最终 owner 阶段不再分配 completion identity 或修改 registry。
这关闭 §12.8 指出的 mutation cleanup 与 completion 两项，但 PageStore 候选 vectors/maps、proof/transaction postwork 仍可能在 owner 内析构；
capture fence、retag/rollback、不可失败完整发布仍未关闭。详见
[67 §32](67_br1_target_structure_reconstruction_20260920.md#32-2026-09-21分批-metadata-cleanup-与预完成-host-evidence)。
