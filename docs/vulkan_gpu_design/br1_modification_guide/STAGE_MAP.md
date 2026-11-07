# BR1 阶段与修改项对照

原 history/memento 显式持有同一个 session、跨 worker cursor 操作与 checkpoint/终结的代码关系见 [HS1–HS8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01f_history_owned_mutation_scope.md#history-scope-map)；该入口要求静止初始化，通用 painter/current 读、job 读写依赖、producer 与资源准备仍待联合启用。

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。本篇把 [92 的阶段出口](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:30)和 §13 的实施单元对应到修改 ID，供拆分实现与审查使用。源码定位基线为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`；实际进度、通过资格及证据入口仍只在 92 维护。

## 当前批次与正式阶段的关系

当前完整主线只见 [92 §17](../92_br1_m6_m8_execution_baseline.md#br1-closure-schedule)，完成情况见 [§16.28](../92_br1_m6_m8_execution_baseline.md#m6-m8-completion-matrix)。CP1/CP2已关闭，CP0/CP3按[92 §6.1](../92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)验收M6，再由CP4执行M7、CP5–CP9收口M8、CP10裁决BR1-PERF。[§16.139执行变异诊断](../92_br1_m6_m8_execution_baseline.md#m6-execution-variance-delivery)完成，生产未改；CPU覆盖与E/P查询关联已定位，就地ABBA候选被同期结果否决，完整计量未闭合。下一稳定实际执行条件后独立正式family，不继续无预算微优化；旧校准2/20、联合hit0/4和miss2/16及原控制8/8保持，metadata驻留/CP0 required独立补证，M6未通过。旧20%/30%仍是原协议失败和研究目标。M6参与对象的安全/预算/退出为前置，M8全模式/多文档及未实现GPU不是M6的无限前置。阶段顺序不变，默认启用仍需真实业务资格。

本轮具体目标、领取边界和条件删除见 [收敛清点](CONVERGENCE_CHECKLIST.md#targets)。

下表说明全量职责和阶段依赖，不要求在第一次真实业务验证前完成所有可选微优化。按 [API 收敛映射](API_CONVERGENCE_MAP.md#sequence)，读取选择的重复政策已按 [92 §16.10](../92_br1_m6_m8_execution_baseline.md#read-selection-convergence)合并，adapter/交付与 JP6 修复同步收束，owner/结果分支随真实接线删除；只有依赖模式迁移的外部 API 删除后置。每项必须给出具体 caller 迁移与保留理由。

## M1–M5 基线中要调整的现有职责

这里按当前代码职责列调整范围，不重新定义历史 M1/M2/M3/M4/M5 的边界。M5 基线已通过与后续仍需调整可以同时成立：必须保护已有语义与 Fresh 控制桶，新增能力单独取证。

| 当前职责与调整原因 | 修改 ID / 指南 | 从哪段代码开始 | 本轮交付边界 |
|---|---|---|---|
| 底层 commit 返回失败，上层仍可能先结束事务或登记 undo | [S01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01_stroke_scope_and_failure.md:5) | `KisTiledDataManager::commit` → `KisTransactionData::endTransaction` → `KisTransaction::commit/endAndTake/revert`；另接 painter/job 故障链 | 结果贯穿业务终结；失败保留终结责任。只有部分接口返回 bool 不算 S01 完成 |
| 唯一 selector 保留 Fresh/semantic，CPU recoverable 子集已联合接线；尚无 M6/M7 完整证明 | [S06/S07](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03_write_plans_and_hot_path.md) | `prepareWriteBaseLocked/prepareWritePlanLocked/select/reserveBacking`，provider domain journal | 先保护现有 selector/预算一致性；M6 与 M7 的新增出口分别验收 |
| prepare 已有锁外工作，backend/manager 外层锁仍覆盖准备 | [S05](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/02_visibility_and_publication.md:22) | `finishOwnedTransaction/commitHistory` → publication prepare/install → backend read selection | 端到端短 gate、旧选择保活、有限立即重准备；实际 install 零分配仍成立 |
| 原 history 可显式持有 session，默认业务仍以 batch/iterator 为主 | [S02/S03/S04](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01_stroke_scope_and_failure.md:24) | `beginMutationBatch/finishClient`、`beginWriteImpl/sealImpl`、`writePageStoreOperation/refreshPageStorePages` | 显式 cursor 的原 owner/终结已按 [HS1–HS8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01f_history_owned_mutation_scope.md#history-scope-map) 接线；默认启用须与 current 读、真实 job/producer、checkpoint 和资源准备共同闭合 |
| 已接整轮 root 限额与 CPU 退休事件/退避；完整进度/资源仍未闭合 | [S08/S09](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04_reclamation_and_budgets.md) | `collectSliceLocked/beginReachabilityScan/advanceReachabilityScan`，`finishAttemptLocked`，binding/completion | 整个 pass 有界；无后续编辑仍能退休；这些是长 scope 的启用前提 |
| 各 store 已有预算准入，需要统一实际物理收费与工作窗口 | [S10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04_reclamation_and_budgets.md:46) | `deriveProductBackingPolicy/reserveImpl`、TileDataStore 实际分配/释放 | 全局/局部 reservation 闭合、alias 不重复收费、pending/必要元数据都有预算 |
| 核心 history 已有 delta，上层普通恢复仍重建全量索引 | [U01/U02](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/05_undo_delta.md) | MementoManager `restore` → backend `restoreHistory` → manager `rebuildPageStoreIndex` | delta 贯穿适配层；放在 stroke 闭环之后验收，不借机增加每 dab 工作 |

所有上述行都由 [V01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/07_validation_and_migration.md)绑定当前源码、构建身份及回归证据。前置修复可以先合入；不能仅因修改发生在旧基线文件里就计作 M6/M7/M8 已完成。

## M6–M8 的交付范围

| 阶段 | 必须落实的修改关系 | 独立出口与禁止替代 |
|---|---|---|
| M6：可恢复 handoff | S06 的 selector → logical transition → provider physical claim/retag → 统一 seal/commit/cancel；联动 S05/S07/S10 的准备、准入和计账 | 已有 Ready exact 独立 before；无临时 before copy；cancel 后旧 G 可读；epoch/ABA/pin/source/swap/retire 双顺序验证。已有 authority transfer 不能替代 backing handoff |
| M7：commit-only handoff | M6 通过后，S06 接 epoch admission gate、全部页 claims、完整输入与预构造安装；V01 记录 fence 分布及首字节后失败数 | 仅受控同步 kernel；≤8 页且≤256 KiB；hold P99≤100 μs；首字节后失败为零。普通 brush callback 不取得该资格 |
| M8：stroke 迁移 | S01 的结果/取消 + S02 的 persistent session/borrow + S03 的真实入口 + S04 的可见性 + S05 的发布；S08/S09/S10 先提供必要进度/资源保证 | direct → indirect/mask/source-dependent → wrapped/LoD/async，按入口闭环验收。同页重复 dab 消除无语义必要的 COW/seal，同时保持显示/exact reader/单操作回退语义 |
| M8：undo 与 context | stroke 后推进 U01/U02，再推进 C01/C02；共享已落实的索引失效和预算能力 | 普通 undo 固定 K 无全量 export/sort/rebuild；缓存有界且依赖准确。undo/context 收益不能抵消 stroke 回退 |
| BR1 总出口 | V01 汇总 92 §6、§7、§14 与 39 的全部 required buckets、生命周期、删除及构建身份 | 正式 BR1-PERF 单独裁决；接口合入、局部微基准、测试总数、M6/M7 通过均不能替代 |

## 建议的可审查修改批次

1. **CP0/CP1：V01与S09/S10。** 预备同依赖对照，完整控制存储统一收费/失败/退出；不重做已交付S01/direct，也不增加通知变体。
2. **CP2/CP3：S06联合S05/S07/S09/S10。** 关闭M6的剩余安全/消费者与参与资源资格，然后冻结M6。
3. **CP4：S06的M7。** 在M6正式通过后接epoch admission、全部claims和实际同步consumer，证明首字节后不可失败及fence分布。
4. **CP5–CP7：S01–S05/S08–S10/BC1–BC10。** 原job接续与真实多文档压力，读/发布/operation族和复杂模式联合迁移；每族同时关闭生命周期并删旧责任。
5. **CP8：U01/U02，再C01/C02。** 保持stroke控制，完成普通undo delta与有界准备/准确失效；不把第三优先级提前变成stroke前置。
6. **CP9/CP10：全责任与V01。** 汇总API/配置/删除、完整M8出口与正式性能；默认策略受最终收益和资源门约束。

上面的批次是实现依赖，不是额外的阶段状态表。对同一源码文件的不同批次，按 [CODE_INDEX](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/CODE_INDEX.md)查出全部关联 ID，避免只修局部函数后破坏另一条契约。

S06 内部按 [03a](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md)进一步拆分：身份与 cache 消费者 → 恢复凭据及物理排斥 → metadata/descriptor/预算准备 → selector/transition 与统一终结 → M6 全出口 → M7 admission/fence。身份比较、parked writer 或已有 authority transfer 中任何一项单独完成，都不能越过这条依赖链。

真实 stroke 的 D/E 联合实施单元见 [BC1–BC10：真实 stroke 联合接线](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01j_real_stroke_integration.md#stroke-integration-map)。BC1–BC7 必须一起审查生命周期、读选择、显示与终结；BC8 扩展到多设备/LoD，BC9 保持资源前置，BC10 取得真实 scheduler 证据。能力层可分批交付，但不能只传 owner 后直接默认启用。

## 审查一段代码时怎样使用本目录

从 CODE_INDEX 定位文件对应的 ID，打开主题指南核对函数及调用者，再回到 92 的条款确认行为。修改记录应写清“输入/失败保证 → 本段状态变化 → 下游消费者 → 验证 case”；涉及多个 ID 时逐项列出，不能仅填文件清单。源码行号用于定位，符号及当前调用链才是修改依据。

实现记录模板和具体测试注册限制见 [V01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/07_validation_and_migration.md)。本篇不新增测试通过结论，也不把指南中拟议接口当成现存能力。

S06.3 的最小接线单元见 [03b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03b_legacy_cache_migration.md)：L1–L4 同步接口与冷路径，L5–L9 迁移缓存/借用/终结，L10 才处理解除 idle 强引用。前两批仍保留原物理保护，不作为 legacy-cache handoff 已开放的证明。

S09 的最小接线单元见 [04a](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md)：R1–R4 接生产者与原 operation；R5–R8 接唯一 queue、去重、寿命与退出；R6 已接有界退避，R3 的空 signal/空表取消清理已接原 registry；上游 last-use 正常终态已接原读记录；R9/R10 继续补 metadata 释放/通知冷失败、完整共享预算与前台等待者、准入原因和实际计量；具体代码单元按 [04a §11 / T1–T6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#terminal-cleanup)推进，单次局部终结及局部空块归还已有 [04a §12](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#metadata-terminal-implementation)的 CPU 证据，外层析构预算、拒绝后继续及必要资源准入仍分别验收。接口、CPU 事件或延迟重试子集均不能替代完整 S09；它们是 S06.3 L10、S02 长 scope 与 S01 压力取消的联动前置，不改变 M6 → M7 → M8 的阶段出口顺序。

S08 的源码与验收按 [04 / G1–G7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04_reclamation_and_budgets.md)对应：有界候选、原 root owner 游标、保护释放、按 key 失效、整轮限额、detach 复验与退出。G1–G6 的枚举子集不能替代 G7 持续热点进度、销毁成本/预算和跨 store 压力；这些未闭合前不以本批结果启用长 scope。

S10 的局部 grant 链见 [04b / W1–W8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04b_budget_waiter_implementation_map.md)。CPU 退休的授额/复验/取消已进入原 owner 链；共享物理预算、所有元数据实际计量、前台 admission continuation 和完整压力/故障仍是长 scope 的启用前置。

实际领取每批工作时使用 [NEXT_EDITS](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/NEXT_EDITS.md) 的 15 项入口和交付格式。该篇区分已有代码与剩余改动，防止把当前实现重新列作从零开发，或把局部接线当成完整阶段通过。

S09 / T4 的外层空块释放、原预算与 close/idle/abort 责任映射见 [04a §13](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#outer-read-cleanup)；当前仍待修改的是整轮节点/字节/时间上限、其他临时对象、T5 拒绝接续及 T6/S10 必要存储准入。本项不关闭 S09 或 M6–M8。

S09 / T5–T6 的实际安装 gate 核对、completion 存储拒绝原子性与后续必要准入责任见 [04a §14](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#completion-failure-atomicity)；本批不建立基于未证实交错的轮询队列，也不把保留 Pending 当作自动接续完成。

读请求/lease/provider 准备与保护、pin、取消和退出的代码关系见 [04a §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#read-storage-admission)；T6/S10 的必要通知、派发、retry/pass 存储及全局计账继续开放。

通用写必要记录准入按 [04c：通用写准入 GW1–GW7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04c_generic_write_admission.md) 拆批；GW1–GW3 的记录前移与 GW5 的终结消费者已同步接线，GW4 的三个准备调用边界已补异常恢复；内部故障与 GW6 实际硬预算继续独立验收。它属于现有写路径的安全/资源前置，不替代 S02–S05 的 stroke 热路径优化，也不授予 handoff 或 M8 资格。

S02 的最小实施批次见 [S02 / SS1–SS10：持久 session、稳定存储与 job 借用](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md)：A 为冷热稳定 slots、原 claim/index 与真实存储准入；B 为业务 scope、job borrow、局部命中与取消；C 为完整 checkpoint、subset 和资源窗口；D 为真实 stroke 与 iterator/cache 接线。A/B 可先提供受测能力，D 的默认启用必须满足既有联合前置；本拆分不增加阶段资格，也不改变 stroke → undo → context 的顺序。

S02 第二批的稳定 slot、部分取消与容量归还记录见 [01c §10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#reusable-slot-implementation)；后续实际准入、范围借用与局部热访问现见 §12–§14。当前待改的是完整 job 冷资源准入、业务 scope/job/cut、subset/checkpoint 与真实 stroke 接线；范围借用已接 managed/packed 消费者，不能据此关闭 A/B 批、S02 或 M8。

上述 A 批原表准入的完整要求保留在 [01c §11 / J1–J8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-implementation-map)，实际第三批交付和证据见 [01c §12](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-implementation)。原 claim/activity、三类 caller、scope/range/control block 和原 orphan 链已接线；整个 job 冷资源、必要终结存储和压力策略仍须在 B/C/D 业务启用前闭合。它属于 M1–M5 现有写路径的必要调整及 M8 前置，不提前开放 M7 首字节后不可失败区间。

S03 的本批前置能力见 [MR1–MR3](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01d_metadata_refresh_and_pending_visibility.md)：普通成功刷新只消费元数据并失效 cache。MR4 保留失败 raw 字节恢复；MR5 发布前准备与 MR6 持久 pending/current/checkpoint 继续作为 D/E 联合启用出口，不据此提前完成 M8。

C 批已有原 session 完整 checkpoint/再开放的受测能力，见 [CP1–CP5](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#checkpoint-implementation)；subset、真实 scheduler cut、压力 continuation 和完整必要准入仍未闭合，D 批业务默认启用继续等待这些出口。

C 批的原 scheduler 切点现见 [S02 / SC1–SC6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01e_scheduler_cut_and_job_admission.md#scheduler-cut-map)，已与真实 worker/原 session checkpoint 联合验证。剩余为 job 身份/footprint、业务 scope/current/read、异步 producer 及压力/必要容量；完整 B/C/D 和 M8 不因本批通过而关闭。

S03 真实 multi-dab 的领取入口见 [S03 / MD1–MD7：真实 multi-dab 与 painter scope](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01g_multi_dab_and_painter_scope.md#multi-dab-map)。MD2–MD3 的实际声明范围已按 [S03 / SR1–SR7：稀疏写范围](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01h_sparse_write_footprints.md#sparse-range-map) 消除包围框假依赖；默认不可变 dab compositor 的共页分区已按 [S03 / PG1–PG8：页归属与真实 brush jobs](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01i_page_owned_brush_jobs.md#page-partition-map) 接线。首条显式 direct 开发入口已接持久 owner、dirty 前 checkpoint 和 finish/cancel；Buildup direct fixture 又完成多 update 的一个策略 undo 单元、递归无输入 drain，以及 admission/像素失败信号/checkpoint/finish 的唯一 cancel 终点，正式工具默认仍关闭。完整 current/source 读 footprint 与资源责任仍未完成。下一批直接做 BC9 与 S05/S08–S10 的 tiny budget、慢 reader、长 stroke、多文档、资源收费及 cancel/close 进度，完成后才评估默认启用与扩大入口覆盖。该顺序不提前授予 M6/M7/M8，也不把局部目标测试当正式 stroke 性能。

S03 的 BC4/BC5 同步消费者子批见 [FC1–FC8：固定源与 sharpness](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01k_fixed_source_and_sharpness.md#fixed-cursor-map)：scalar fixed 的读/合成/拷回已改原 cursor，真实 1px producer 和绑定 owner 镜像各有验证，public 显式 owner overload 已收缩为 private impl；仍未完成 BC 的默认上下文、读意图和整 job 资源联合启用。此子批属于 D/E 的能力准备，M6 → M7 → M8 和 stroke → undo → context 次序不变。

BC3 的 target/mapping 复验子批见 [WC1–WC8：目标映射复验](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01l_write_context.md#write-context-map)。原事务和真实 brush jobs 均消费同一值契约；BC1/BC2 的业务 owner 与异步寿命、BC5–BC9 的读/cut/终结/资源仍未闭合，不能据此提前默认启用。

MR5/BC9 可按 [OP1–OP10：operation 资源准备](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#operation-storage-map) 的 A–D 批次审查。A 中触页/changed 子范围已按 [OP2 实施与剩余边界](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#operation-storage-implementation) 实施；B 准备 adapter 存储；C 协调发布、cut 和旁路；D 接完整压力与真实 stroke 证据。四批不新增阶段，也不改变 M6→M7 依赖或默认长 scope 的联合启用条件。

各局部批次的冻结记录在 92 §15，当前资格在 §16；本页不追加不同批次的动态计数。JP、HX、BC 的函数级责任以各主题指南为准。
