# 00 状态页归档快照（2026-09-25 复核前）

> 历史快照；下文“当前/最新”均指原记录时点。现状见 [90](../br1_pre_m6_20260925/documents/90_br1_m5_baseline_freeze_review_20260925.md)。正文保存本轮修改前的第 2 节，包括既有未提交状态补记；仅调整相对链接以保持可访问。

## 2. 当前事实基线

2026-09-25 最新状态：当前代码已保存为 Krita `0db3434678` / 外层 `9c867b8` 检查点。
[85 代码审计](../br1_pre_m6_20260925/documents/85_br1_m5_code_readiness_audit_20260924.md) 已复现 domain journal 旧快照覆盖和 metadata 预算未接线，
并确认真实 backend 尚未启用有限分类预算。当前执行方案改为
[86 最终收敛方案](../br1_pre_m6_20260925/documents/86_br1_m5_final_convergence_plan_20260925.md)：先修复版本/预算/事前准入，再收口 seal 与真实 compatibility 调用链，
最后完成同源码验收。84 的“21 已闭合 / 3 局部 / 0 未闭合”是审计前历史判断，不能作为当前验收结论。
M5 未关闭，M6/M7 不扩展，BR1-PERF 未通过；86 仅为方案，尚未实施其中修复。

2026-09-23 当前执行转入 [84 全性能优化链路收敛](../br1_pre_m6_20260925/documents/84_br1_full_optimization_convergence_and_cleanup_20260923.md)，
覆盖 52 起全部性能优化、67 结构调整及 M1–M5。下文各阶段完成数字是历史切片事实；M5B 的旧源码基线/调用图
已确认过期，当前协议统一与生产有限预算仍需闭合。C0–C5 未验收，M6/M7 不扩展，BR1-PERF 未结清。

截至 2026-09-22 的 BR1-PERF 复审状态：

当前执行已切换为 [67 的整体目标结构重构](../br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md)：
先接通并验收结构，再统一做性能测试；过程持续运行正确性/并发/生命周期回归。
下列 D1–D12 数字仍是各自归档版本事实，不能用作当前工作树性能。整体重构尚未完成，不授予新的 BR1-PERF 资格。
2026-09-21 继续推进提交核心：事务 claim 保护下，provider proof 验证、metadata 候选与 persistent root 构造已移出 owner gate；
发布复验 head、retention、页面 revision 及默认页目录变化。undo/redo 的 metadata 准备也已外移。
默认/删除输入组装、安装及历史评估仍有 owner 临界区；后续已将 tiles3 CPU 历史/首次退休与树析构接入后台分批、drain/close，见 67 §9。
截至 67 §32，生产 mutation 仍强制 source/target 使用不同 allocation；这是安全 COW fallback，尚未实现普通 resident write 的
条件 allocation handoff，也没有覆盖 current/history/pending/in-flight/retiring backing 的硬字节预算。
[68](../br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) 已冻结后续方向：PageStore 私有
`KisPageWriteCoordinator` 生成内联 `KisPageWritePlan`，统一选择 pending 复用、recoverable/commit-only handoff、完整 payload、
必要 COW 与纯语义写；metadata stable-slot arena 是 handoff 前置，公开原位 permit 不再是目标 API。
[69](../br1_pre_m6_20260925/documents/69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) 进一步冻结重构前 R0 审计、store-private 服务拆分、
tiles3/iterator/painter 侵入 manifest、CI ratchet 与删除门槛；R1 完成后 `KisPageStore.cpp` 已从 5,522 行收缩到 3,979 行，
但剩余代码仍不能直接解释为可删冗余。
R0 已按 [70](../br1_pre_m6_20260925/documents/70_br1_r0_containment_and_layout_gate_20260921.md)、
[71](../br1_pre_m6_20260925/documents/71_br1_r0_runtime_census_and_test_binding_20260922.md) 和
[72](../br1_pre_m6_20260925/documents/72_br1_r0_reverse_callgraph_and_closure_20260922.md) 完成：17 项 manifest、R0 的 12 类 ownership fact、11 个 runtime group 与
Clang reverse-call graph 已冻结；没有项目满足 D0。R0 之后只按 69 R1 顺序推进无语义职责拆分。
R1 五项 service 已全部完成按值提取，default admission、physical retirement、history scan、read lease/last-use 与 publication staging
均已有 owner 和防回退门禁，证据见 [73](../br1_pre_m6_20260925/documents/73_br1_r1_default_storage_extraction_20260922.md)、
[74](../br1_pre_m6_20260925/documents/74_br1_r1_retirement_queue_extraction_20260922.md)、[75](../br1_pre_m6_20260925/documents/75_br1_r1_history_read_publication_extraction_20260922.md)；
R2/M1 compact authoritative records 与 snapshot 分离已完成，证据见
[76](../br1_pre_m6_20260925/documents/76_br1_r2_m1_compact_metadata_records_20260922.md)；M2A 已把权威 record 迁入 shard slot arena，证据见
[77](../br1_pre_m6_20260925/documents/77_br1_r2_m2a_shard_metadata_arenas_20260922.md)，M2B 已完成锁外 block growth、revision revalidation 与 metadata-only
因果基线，证据见 [78](../br1_pre_m6_20260925/documents/78_br1_r2_m2b_lock_external_metadata_growth_20260922.md)。M3A 已删除 `VersionRecords` 及 per-page
list/map/hash/set，接入 shard-global exact/physical index、reservation token 与 intrusive version/history/mutable 链，证据见
[79](../br1_pre_m6_20260925/documents/79_br1_r2_m3a_shard_indexes_and_intrusive_records_20260922.md)；M3B 已删除 776 B public snapshot header，以 96 B
`MetadataPage` 和稀疏 slot-referenced activity 完成 M3，证据见
[80](../br1_pre_m6_20260925/documents/80_br1_r2_m3b_compact_page_activity_20260922.md)；M4 allocation-free publication install、prepared commit 与 publication
side-map 收口已完成，证据见 [81](../br1_pre_m6_20260925/documents/81_br1_r2_m4_allocation_free_publication_20260922.md)。R2 已关闭；M5A 已完成 write schema、
inline/sparse write set、admission、budget reservation 与 fresh-only selector，证据见
[82](../br1_pre_m6_20260925/documents/82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md)。当前下一项为 M5B 生产 fresh 路径迁移与旧 writer/session 容器删除；
M6 前不授权 recoverable backing handoff。
完整生产 read scope、write-plan/handoff、单页历史与总队列背压等边界仍开放。

- 旧 `libs/image_vulkan`、`libs/ui/vulkan` runtime 与其旧测试已从当前 production tree 删除；删除前的原型和
  35 个工作区修改保存在内层 Krita 仓库的 `archive/vulkan-prototype-pre-br0-20260918` 分支，归档提交为
  `7207640968`。
- `kritaimagevulkan` target、UI 反向链接、`useVulkanCanvas`/`VULKAN_STARTED` 入口、全局
  `KisVulkanPaintRouter`、factory wrap 接线和 raw `KisVulkanUpdateInfo` 已从当前树删除。
- 新 target 是单向依赖的 `kritavulkanbackend -> kritaimage`；当前 `kritaui` 不链接该 target，也不编译 Vulkan
  canvas。产品只保留既有 CPU/OpenGL/QPainter 路径。
- `kritaimage` 已加入 PageStore/Surface/generation/lease/ticket、state machine、document session/context、format
  codec、unified SSD、residency、`EvalGraphIR`/lowerer/planner、derived surface cache、stroke protocol/compiler
  的接口骨架；`kritavulkanbackend` 已加入
  bootstrap、submission、command arena、binding table、replica provider、document session 和 stroke executor
  骨架；独立且未接入产品的 `kritavulkanuiadapter` target 已加入 view/presenter/canvas gate 骨架。
- 第一版空壳已升级为 Foundation 契约：Surface/Completion/BackendService registry 具备线程安全 identity、单调
  ticket、终态和 generation 注销行为；backend 具备 device evidence、shader catalog/ABI、内存预算、pipeline、
  submission packet、resource retirement、page binding、stroke/composite/display preparation 和 WSI view intent
  状态机。涉及 native Vulkan allocation/command/queue/swapchain 的方法仍显式失败，不代表 BR2–BR6 已实现。
- `KisTiledDataManager` 已通过 PageStore backend/bridge 把 tile identity、generation、事务可见性、CPU access lease、
  COW/oldData、memento、default/extent、clear/copy/clone/purge 统一到 canonical PageStore；legacy tiles3 与 iterator
  ABI 仅保留为兼容外壳，不再维护第二套 canonical generation 或双写像素。
- 上述 cutover 已通过功能/正确性测试，但尚未通过 production CPU 性能出口。优化开始前的历史 upstream 差分显示
  `stressTest` 57.1×、`stressTestLazyCopying` 100.6× 退化，当时 blank/default 读取还破坏稀疏性；BR1 已以
  `BR1-PERF` 重开，执行见
  [52_br1_cpu_fast_path_optimization_plan_20260920.md](../br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)。
- 后续已有 virgin default/native read/alias/root 等局部优化；D1 最终 Foundation/Reference/tiled-manager 回归为 24/31/36 项通过。
  D1 混合 stress 前/后各 5 次诊断的 Qt median 为 26.556 → 16.212 s（约下降 39.0%），不是同主干 M/K/E 配对验收。
  当前不能沿用初始倍率或旧采样热点作为最新结果；历史归因见 53，版本化实施/偏差记录见
  [54_br1_optimization_execution_and_deviations_20260920.md](../br1_pre_m6_20260925/documents/54_br1_optimization_execution_and_deviations_20260920.md)。
- D2-A 已接入无 manifest 导出的原子 current-root 事务起点，新增 52 桶固定工作量/真实写和阶段诊断；当前 Foundation/
  Reference/tiled-manager 在该版本为 24/33/88 项通过。大 N 小 K 有定向收益，原混合 stress 没有可确认整体收益，细阶段计时有明显
  扰动；仍未取得主干 M/K/E 资格，见 [55](../br1_pre_m6_20260925/documents/55_br1_d2_phase_measurement_and_atomic_transaction_begin_20260920.md)。
- D2-B 已接入同步 owner-held prepared metadata publication、逐页 revision/短 claim 与 metadata 先安装后发布 root；
  该版本 Foundation/Reference/tiled-manager 为 24/38/88 项通过。初版局部性能偏差和再优化实测见
  [56](../br1_pre_m6_20260925/documents/56_br1_prepared_metadata_publication_20260920.md)；全局 PageStore mutex、生产布局/全部发布入口与同主干 M/K/E 仍未结清。
- D3 加入操作级抽样、完整 writeBytes 分段、长区间交替 library 对照；metadata shard 目录一次发布后不再逐页取配置锁。
  该版本 Foundation/Reference/tiled-manager 为 24/39/88 项通过；六桶未确认目录优化收益，主线转向 resident write/native guard，
  见 [57](../br1_pre_m6_20260925/documents/57_br1_sampled_write_pipeline_and_immutable_directory_20260920.md)。不是 PageStore 整体免全局锁或主干性能合格。
- D4 已接入 native COW 初始化，消除支持条件下 preserve 的冗余 default-fill 和第二次 transfer，补 actual payload 计数与
  安全负例。D4 所测版本 Foundation/Reference/tiled-manager 为24/42/88；十桶六对中七个真实写桶耗时下降约41%–56%，alias 控制桶
  未确认变化，见 [58](../br1_pre_m6_20260925/documents/58_br1_native_cow_initialization_and_payload_accounting_20260920.md)。仍是 TileData 复用加 PageStore
  控制/epoch/adapter 的混合管线，正式 guard/session/permit 和主干 M/K/E 资格未完成。预克隆命中全0，后台成本尚未完整计量。
  CPU 同义管理目标与容差内不劣性验收分开；UMA 零值仅指满足条件的 payload migration copy count/bytes，不指全部耗时。
  GPU/UMA 产品性能仍为 NotMeasured。
- D5 新增两侧同源 tiles3 fixture；固定 upstream 与 D4 实现的 11 桶各 12 对、264 次独立窗口吞吐运行显示：
  暖管理生命周期约为主干 74%–86%，真实 scanline 写仅约 0.27%–0.39%；预绑定 memcpy 控制无数量级差距，见
  [59](../br1_pre_m6_20260925/documents/59_br1_shared_upstream_cpu_baseline_20260920.md)。双方 fixture 各34项、D5 所测版本 Foundation/Reference 24/42及架构检查通过。
  这不是固定-work 延迟、M 不劣性或完整产品资格；D5 定位的累计 completion 留存由 D6 继续处理，provider replay 仍未结清。
  原生 guard/session/permit、短发布和有界回收仍是主线，BR1-PERF 不结清，GPU/UMA 不开放。
- D6 已将 completion 逐ticket留存改为完成覆盖与稀疏失败/取消状态，保留pending gap/精确终态/拒绝重放；初版碎片
  耗时与RSS反证促成布局修正，见 [60](../br1_pre_m6_20260925/documents/60_br1_completion_coverage_and_sparse_terminal_status_20260920.md)。D6 所测版本真写吞吐
  分支内改善约2.9%–5.5%，暖guard未确认变化，不把组件长桶收益外推整条管线。provider replay/完整drain仍未结清。
- D7 已接入 captured identity/surface view，修正 CPU session 跨 commit 混合 epoch，短 scope 不再重扫仍可达历史。
  identity lookup改善不等于像素加速：单页generic session吞吐反而下降23%–25%，native真实写另有约0.9%反向偏移，见
  [61](../br1_pre_m6_20260925/documents/61_br1_captured_read_scope_and_integration_cost_20260920.md)。D7 尚未接通 native pixel guard/retire；相关回归与240次
  配对只证明该切片范围，不授予M/E性能资格，BR1-PERF不结清。
- D8 已把 stable binding/native read guard 接到新 CPU facade，暖读逐页 generic request 为零，见
  [62](../br1_pre_m6_20260925/documents/62_br1_native_resident_read_and_write_cost_20260920.md)。相对 D7，单页 session 吞吐约3.17–3.48倍，16页 session/accessor
  约11.6–12.2倍，rect约1.49–2.19倍；原生真实写却下降约2.3%–4.8%，必须独立保留反证。184对/368次计时运行及4次loader
  检查不构成upstream不劣性、冷binding/单次尾延迟或完整drain资格。ResidentRead24/read fixture21/Reference59/
  Foundation24/tiled88/native34/Vulkan13及静态架构检查通过；Qt totals含init/cleanup。分段self/锁wait-hold尚未完整测得，
  eager缓存维护是该检查点的假设，后续对照见D9。
- D9已改为首次native读建立cache，保留provider record/共享gate，见
  [63](../br1_pre_m6_20260925/documents/63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md)。768次计时运行显示相对D8真写提高约2.7%–3.8%，
  但直接D7/D9仍有约0.8%–1.7%负偏移，首次16页read scope约慢70%–73%，部分暖读/rect也退化。
  ResidentRead28/read fixture33及其余D8同范围回归通过，不能写成全面优于D8/D7或M/E达标。
  D9提出的暖lookup/冷发现分离与rect/真实写控制已由D10继续验证，历史反证不改写。
- D10已分离暖lookup与冷发现，见[64](../br1_pre_m6_20260925/documents/64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md)。
  1776次计时运行、28次loader显示相对D9，16页held-view guard吞吐提高约5%–7%，完整session/accessor约4%；
  直接D8仍有宽格式/单页负偏移，首次16页read scope仍慢约63%–73%，直接D7真实写仍有约1.1%–1.6%负偏移。
  固定256周期已补facade/provider容器析构，不是全后台drain。ResidentRead28/read fixture41/Reference59/Foundation24/
  tiled88/native34/Vulkan13及架构检查通过（Qt totals含init/cleanup）；不授予upstream不劣性或产品资格。
  D10按52第12节收尾诊断，保留读残差，不以所有读微基准最优为下一步前提。
- D11已接通生产writeBytes的native未发布写段、同页pending复用与段末seal，见
  [65](../br1_pre_m6_20260925/documents/65_br1_native_cpu_mutation_segment_20260920.md)。generic write request已去除，但仍安全整页COW、owner-held准备与兼容层；
  直接D10对照单页写吞吐下降约5%–6%、16页写提高约8%，必须保留反证。新增17项写生命周期测试及既有回归通过。
  直接固定主干真写吞吐仍仅0.26%–0.45%；400次有效计时与分段计数不授予正式不劣性，亦不支持归因为硬件跨域。
  此为D11版本事实；原位permit、短发布、全部生产入口和有界回收未完成，BR1-PERF不结清，GPU/UMA无产品性能资格。
- D12落实TileData/binding的物理独占前置保护，16项定向测试及既有回归通过，见
  [66](../br1_pre_m6_20260925/documents/66_br1_physical_exclusivity_prerequisite_20260920.md)。生产owner尚未消费claim，不能作为原位permit完成。
  352次直接D11/固定upstream配对保留K1/B8写约-1.9%、K16读约-1.6%及copy控制桶变动；不声称零成本。
  真写仍仅固定主干约0.25%–0.43%，不授予M/K/E资格；当前状态以52的1.16/11为准。
- 静态架构门禁已接入 GitLab CI；BR0 归档版本的 CPU-only 与 Vulkan-foundation 双架构配置/构建均通过，
  `kritaimage`、`kritaui`、backend、offscreen smoke 和未接产品入口的 UI adapter 均有可复现构建证据。
- Foundation 已有构建期生成并校验的 SPIR-V checksum asset、reflection/ABI manifest、真实 Vulkan 1.2 device、
  VMA buffer、compute dispatch 和有界 timeline wait smoke；该 smoke 不链接 UI，产品 Vulkan 入口仍关闭。
- 当前树仍没有可运行 Vulkan 产品功能，也没有跨域页面迁移、UMA pointer bypass、业务合成、GPU stroke 或
  swapchain 的端到端验证证据；这些仍分别属于 BR2–BR6，不能由 foundation smoke 或 BR1 CPU closure 代替。
- BR0 当时未修改 `origin/master` 的 CPU/OpenGL baseline 与候选树稳定核心回归分别通过 5/5 和 6/6；额外 4 个
  测试在两棵树上以相同方式因未安装 bundle 资源或既有 scheduler/checksum 崩溃失败，已作为 upstream parity
  限制记录，不计为本次回归。
- BR0 净变更已重放到目标 upstream `origin/master` `9a24ae0d8c` 之上；重放前状态保存在
  `archive/br0-pre-upstream-replay-20260918`。BR0 归档树已重新完成 CPU-only、Vulkan foundation、真实 offscreen、
  稳定核心回归和依赖边界验证，BR0 正式关闭。

因此，当前项目应描述为：

> BR0 已完成；BR1 的 canonical 功能/正确性 cutover 已完成，但 BR1 整体处于 `BR1-PERF`。Canonical PageStore
> 已成为 tiles3 的唯一 generation/transaction authority；新 CPU facade 原生读及部分 production mutation 已接通，当前写侧仍是
> 独立 backing/COW fallback。还须完成全部 legacy/brush 入口、统一 write-plan、条件 backing handoff、硬 backing 预算、
> production owner/layout、有界回收和 upstream 性能门禁。51 是历史功能证据，52/67 是执行入口，68 是写侧最终设计。
> BR2 只允许隔离协议/reference 准备，production 接线与 Vulkan canonical replica、GPU 产品路径仍保持关闭。

性能口径统一引用 [39 的 5.11](../../39_virtual_texture_performance_gates.md#511-统一口径速查与报告判词)：CPU 同义管理等价是
目标，冻结容差内不劣性是验收结论；UMA 零 payload migration 不是零总开销。D4 alias 桶包含 caller 的 uniform backing
初始化，不是纯管理 M；源码复核限定见 58。D5 改为计时前预备 source，仍含原生内容判断与提交，归为操作级 E，
不直接改称纯 M。文档按 53–64 的版本化结果与 52 的当前状态更新，不改写历史证据，也不改变 BR1-PERF 未结清状态。
60/62/63/64 的分支内改善不乘入59的主干比值；后续工作树接线须另补源码/二进制和回归/性能证据。零迁移结论须说明真实交接与
计数覆盖，CPU-only 未交接为 `NotApplicable`；未解释的软件差额继续登记研究，不作为“硬件事实”豁免。
