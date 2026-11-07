# 开发步骤与验收门槛

> 本文保留早期阶段摘要，其中“当前”和指向 47–91 的执行计划均为历史时点记录。当前 BR1 工作请以 [92](92_br1_m6_m8_execution_baseline.md) 和代码现实为准。

> 本文是便于阅读的阶段摘要。全局唯一执行计划、进入条件、删除清单和提交顺序以
> [31_p0_reset_and_execution_sequence.md](31_p0_reset_and_execution_sequence.md) 为准，机器门禁以
> [30_p0_ci_architecture_guards.md](30_p0_ci_architecture_guards.md) 为准。旧 `Phase*`、`G*` 标号只用于追溯，
> 不再构成可并行选择的项目路线。虚拟纹理的算法工作包映射见
> [32_virtual_texture_architecture_decisions.md](32_virtual_texture_architecture_decisions.md)。

## 当前总评

- 旧 Vulkan 原型：已归档并从当前 production tree 删除；不再有可运行 Vulkan 产品路径。
- canonical storage：BR1 功能/正确性 cutover 已完成，但整体以 `BR1-PERF` 重开；PageStore 已接管 tiles3
  identity/generation/transaction，当前补 resident CPU native guard、virtual default、mutation scope、统一 write-plan、
  条件 backing handoff、硬 backing 预算与 persistent epoch root，计划见 52/67，写侧最终设计见 68；69 R0 已完成且无 D0，
  R1–M5 已有实施记录，但全链路收敛尚未验收。当前按
  [84 全性能优化链路收敛方案](archive/br1_pre_m6_20260925/documents/84_br1_full_optimization_convergence_and_cleanup_20260923.md) 清理 52 起全部增量，暂不扩展 M6/M7。
- 新 Vulkan 子系统：backend/UI adapter 仍是保持产品入口关闭的 foundation；BR2 submission API 尚未接入产品。
- 正常应用入口与 readiness：旧假成功入口已删除，新入口保持关闭，尚无 ready device/session/view。
- 模块边界：旧 `kritaimagevulkan <-> kritaui` 构建环已切断；foundation target/private-public 边界已落位，
  native submission/WSI owner 仍按 BR2/BR6 推进。
- 虚拟纹理 MVP：未完成；当前 L3 没有真实 SSD，UMA 不是 canonical pointer bypass。
- queue/线程：新 coordinator 只有空壳，未形成 queue 唯一所有者和完整 ticket DAG，零阻塞不成立。
- GPU stroke、撤销/保存、多层合成：旧实验仅在 archive；新树没有可运行实现。
- device/shader/compositor/display/WSI：旧算法有提取价值，但新 foundation owner、ABI 和测试尚未落地。
- 格式/颜色/LoD：新能力保持关闭，尚无 codec/pipeline/golden 支持矩阵。

因此当前下一步是结清 BR1-PERF；BR2 `SubmissionCoordinator` 只允许隔离协议/reference 准备，production 接线不得
越过 BR1-PERF，也不得越过 BR2–BR5 直接接通产品入口。

## BR0：干净校正基线

目标：清除错误运行路径，使以后只能在正确边界上扩展。

- 归档当前原型，记录 upstream/submodule SHA、构建选项、trace 和测试资产。
- 从更新后的目标 Krita upstream 建新分支。
- 删除 TileManager+sparse canvas+global PaintRouter runtime、旧入口、stroke-end download 和双向 CMake 依赖。
- 建立 `kritavulkanbackend -> kritaimage`，以及下游
  `kritavulkanuiadapter -> {kritaui, kritavulkanbackend}` 单向 target；paintop 不链接 concrete backend。
- 冻结 foundation device/submission/resource/shader/composite/display/WSI owner 与 private/public 边界。
- 保持 Vulkan 用户功能不可用；CPU/OpenGL 回归必须完全通过。
- 安装依赖图、禁用符号、queue API 和 wait API 静态守卫。

验收：旧 runtime 不在生产构建中、依赖无环、foundation target/private-public 与旧能力提取清单冻结、CPU-only
和 Vulkan-foundation 构建有证据、用户无法进入半初始化 Vulkan、CPU/OpenGL 与 upstream 一致。

## BR1：Canonical PageStore

目标：让 Krita 逻辑 tile、COW、undo、swap 成为唯一 canonical page 身份。

- 在 `kritaimage` 内建立 `SurfaceId + LogicalPageId + Generation`。
- 吸收 `KisTileDataStore`、`KisMementoManager`、`KisSwappedDataStore`，不新建平行存储。
- 冻结 read/write request、lease、publish/cancel 与 backend-neutral completion ticket。
- iterator/accessor 通过 CPU access facade 保持现有语义，并以 native resident guard 保持 upstream 级热路径。
- virtual default 不物化空白 page；write mutation 由 PageStore 私有 `KisPageWriteCoordinator` 和内联 plan 选择 pending 复用、条件 backing
  handoff、完整 payload、必要 COW 或纯语义写；每页每个业务 mutation 至多一次必要 COW，epoch 使用 production persistent root。
- backing ledger 精确区分 current、retained history、pending、in-flight、retiring 与 optional cache；临时/退休类有硬上限、
  高低水位、背压和显式 `ResourcePressure`，不以无限后台 baking 作为稳态方案。
- 建立 reference state machine、随机迁移/取消/failure property test。

验收：纯 CPU 绘画、clone/COW、undo/redo、save/reopen 与 upstream 像素一致；同一 page 没有第二身份；普通无旧值保留的
resident write 达到零 before-image copy、零新 payload allocation、零 payload migration 且 backing 峰值不越硬上限；必要 COW、
tiny-budget/backpressure、blank/default 和 epoch commit 达到 52/68 的结构门槛与 39 的 upstream 差分性能门禁。

状态：2026-09-19 已通过功能/正确性 C1–C5；51 保留该历史证据。2026-09-20 upstream 差分发现 CPU 热路径和
production layout 未达出口，当前以 `BR1-PERF` 推进
[52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)，后续 write-side 实现服从
[68](archive/br1_pre_m6_20260925/documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md)。当前代码仍是独立 backing/COW fallback；不得恢复第二套
tile authority；R0 完成证据见 [72](archive/br1_pre_m6_20260925/documents/72_br1_r0_reverse_callgraph_and_closure_20260922.md)，R1 五项 service 提取已经完成，实施证据见
[73](archive/br1_pre_m6_20260925/documents/73_br1_r1_default_storage_extraction_20260922.md)、[74](archive/br1_pre_m6_20260925/documents/74_br1_r1_retirement_queue_extraction_20260922.md) 与
[75](archive/br1_pre_m6_20260925/documents/75_br1_r1_history_read_publication_extraction_20260922.md)；R2/M1 证据见
[76](archive/br1_pre_m6_20260925/documents/76_br1_r2_m1_compact_metadata_records_20260922.md)，M2A 证据见
[77](archive/br1_pre_m6_20260925/documents/77_br1_r2_m2a_shard_metadata_arenas_20260922.md)，M2B 证据见
[78](archive/br1_pre_m6_20260925/documents/78_br1_r2_m2b_lock_external_metadata_growth_20260922.md)，M3A shard index/intrusive record 证据见
[79](archive/br1_pre_m6_20260925/documents/79_br1_r2_m3a_shard_indexes_and_intrusive_records_20260922.md)，M3B compact page/activity 与 M3 收口证据见
[80](archive/br1_pre_m6_20260925/documents/80_br1_r2_m3b_compact_page_activity_20260922.md)，M4 allocation-free publication install、prepared commit 与 side-map 收口证据见
[81](archive/br1_pre_m6_20260925/documents/81_br1_r2_m4_allocation_free_publication_20260922.md)。M5A write schema、admission、budget reservation 与 fresh-only selector 证据见
[82](archive/br1_pre_m6_20260925/documents/82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md)，M5B 历史记录见
[83](archive/br1_pre_m6_20260925/documents/83_br1_r3_m5b_store_session_write_migration_20260923.md)。当前按
[84](archive/br1_pre_m6_20260925/documents/84_br1_full_optimization_convergence_and_cleanup_20260923.md) 执行全链路收敛；旧 gate 通过不代表当前源码已验收；
BR2 production 接线等待 BR1-PERF 结清。

## BR2：SubmissionCoordinator

目标：建立 Vulkan 工作的唯一提交、同步与资源退休系统。

- 一个 coordinator 独占所有 `VkQueue` 和 submit/bind/present API。
- transfer、sparse、compute、graphics、present 形成显式 timeline DAG。
- 每 queue family 使用按完成值回收的 command arena。
- descriptor、allocation、binding-table slot、swapchain generation 按 ticket 延迟退休。
- UI/input 无 Vulkan wait；CPU 缺页 job 使用 continuation，不占住 worker。

验收：源码和二进制只有 coordinator 调用 queue API；共享/独立 queue family 均无 validation 错误；无热路径
wait-idle 或无限 fence wait。

## BR3：UMA、dGPU、RAM 与 SSD replica

目标：在一个 PageStore 状态机下实现全自动透明转录。

- UMA canonical arena 持久映射、host-visible、device-addressable；CPU pointer/GPU address 访问同一物理页。
- dGPU 用 fixed-slot buffer 和 operation-scoped direct/local binding 映射逻辑页；atlas/sparse 只是可选优化。
- RAM 与 VRAM 是同 generation replica，authority 只在 producer 完成并校验后切换。
- SSD 只演进 Krita 当前 swap，使用 generation record、checksum、原子 index commit 和后台 GC。
- 统一预算、pin、in-flight、温度事件和 backpressure。

验收：同一兼容驻留 shared backing 的真实 CPU↔GPU 交接中，payload migration count/bytes 为零（条件及计数覆盖见
39 的 5.7；不等于零同步/总耗时），COW/undo/derived copy 单列；小预算下 VRAM→RAM→SSD→RAM→VRAM 强制循环不丢像素；
SSD 失败/取消/损坏不改变 authority。

## BR4：EvalGraphIR、EvaluationEpoch 与语义温度

目标：先建立不依赖 Layers/Vulkan 的通用求值图，再利用“stroke 只写目标图层”的事实做 layer-specific 剪枝。

- 固定 Authoring Graph → EvalGraphIR → Execution Task DAG 三层边界。
- 完成 Layer Tree reference lowerer、CPU evaluator、typed ports/edges、ROI/halo 与 exact cache key。
- EvaluationEpoch 的 `MutationRootSet` 可为空；每笔另行冻结非空 writable targets 并映射为 mutation roots。
- Layer lowerer 可令下层形成精确 LowerCheckpoint、上层按 overlay/operator/replay 分类；这些不是通用 IR 类型。
- backdrop-dependent blend、filter、mask 保留 replay bundle，不能在透明背景错误拍平。
- derived cache 持有 operation/input/property/context 的完整 dependency vector；authoring graph 变化创建新 epoch。
- `CoveredCold` 必须有 CoverageCertificate；温度按 safety、semantic class、cost/CLOCK history 决定，不另建 LRU 真相。
- canonical target、projection、derived composite、DisplaySurface 身份彻底分离。

验收：source/diamond/fan-out/multi-output/random DAG、空 MutationRootSet、随机图层属性/帧变化不能命中 stale
cache；Layer 与等价 Flow lowering 的 CPU reference 输出一致；剪枝前后像素一致；非目标页可以安全下沉。

## BR5：GPU stroke、undo 与保存

目标：让 GPU stroke 成为 PageStore 的普通 lease/ticket consumer。

- PaintOp 从 `KisPaintExecutionContext` 获取文档 session，不访问 canvas/global router。
- resolved dab 进入无丢失 journal，并按 page 稳定分桶；同页严格按 sequence 执行。
- page-batched kernel 取 write lease，first-write 消费与 CPU 相同的 PageStore write plan；合法 shared allocation handoff
  不新建 payload，仍需旧值/取消/失败隔离时创建 generation COW。
- stroke commit 依赖最后 publish ticket，不暂停 render thread、不下载整笔像素。
- undo 保存旧 generation 引用；save 获取 immutable image epoch，绘画可继续下一 generation。
- capability/format 先判定语义可执行性，再由 39 的 CPU-relative performance profile 在首次写入前决定整笔 GPU 或
  CPU route；`Supported` 但不具备 `AutoPreferred` 的 bucket 仍走 CPU。

验收：overlapping dab、selection、alpha lock、wash、undo/cancel/save/reopen 与 reference 一致；没有 per-dab
submit/wait，失败只丢弃新 write generation；CPU-only/forced GPU/UMA/Auto 在 39 的 GPU 劣势 profile 下满足 CPU-relative
median/P95/P99 门禁。

## BR6：Vulkan UI、DisplaySurface 与产品开放

目标：建立只消费 derived display 的 UI adapter，并在完整 MVP 后原子开放。

- 后端完整初始化后才产生不可伪造的 `BackendReadyToken`。
- `DocumentGpuSession` 归属 `KisImage`；同文档多 canvas 共享，不同文档隔离。
- canvas 必须同时拿到 token、swapchain 和 session 才能替换普通 canvas。
- Presenter 只构造 `PresentRequest`；queue present 仍由 coordinator 执行。
- resize/out-of-date/minimize 使用 swapchain generation 退休，不 wait-idle。
- 完成 SurfaceFormat、color conversion、proofing/display filter 和 truthful LoD/capability。

验收：多文档、多 canvas、关闭、resize、device loss、颜色与显示测试通过；Tier 0–4 全绿；此时才允许开放
Vulkan 用户选项。

## 首个 MVP 出口

首个 MVP 不是“Vulkan 画布能显示”，而是同时满足：

- 错误旧 runtime 已从源码树和构建图消失；
- canonical page/generation/lease/ticket 接口冻结并有 CI 守卫；
- UMA、VRAM、RAM、SSD、display 只能作为 replica、policy 或 consumer 扩展；
- UI/input 的零阻塞由计数和 trace 证明；
- page-batched GPU stroke、COW undo、immutable save 和 EvaluationEpoch 合成闭环；
- 4/8/16 字节像素格式及不支持格式的前置 CPU 路由有测试；
- 用户入口只在完整验收后打开。
