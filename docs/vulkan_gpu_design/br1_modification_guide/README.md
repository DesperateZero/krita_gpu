# BR1 修改指南目录

本目录按 stroke、undo/redo 和上下文切换提供责任、原实现与回归入口。当前 M6 任务从 [92 §1](../92_br1_m6_m8_execution_baseline.md#native-cpu-baseline)和[机会型门禁](../92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)领取。查已有优化时按[证据适用范围](../README.md#evidence-scope)核对实际消费者。下列表格中的轮次、代码位置、领取表与进度均对应各专题原批，按所需责任读取。

## 从这里开始

| 要做的事 | 入口 | 文档给出的关系 |
|---|---|---|
| 从第一性成本选择值得进入蓝图的优化项 | [03k试行流程](03k_first_principles_candidate_selection.md)、[回放与前瞻追踪](../evidence/br1_first_principles_selection_20261009/README.md)、[92 §16.160](../92_br1_m6_m8_execution_baseline.md#first-principles-selection-trial) | 必要事实/保证 → 合法差异 → 竞争解释 → 可删除净时间 → 蓝图准入；前瞻闭环后才升级技能 |
| 按理想管线实施全部管理协议清理并防止目标漂移 | [03f代码改动索引](03f_cpu_management_cleanup_index.md)、[03g唯一追踪矩阵](03g_cpu_management_cleanup_tracker.md)、[92 §16.154](../92_br1_m6_m8_execution_baseline.md#cpu-management-cleanup-blueprint) | MP01–MP10/22子项与10条路径；逐项绑定删除目标、原owner、失败/释放和V0–V6验收。先证明再删，同一完整候选统一测试；文档完成不是产品完成 |
| 按量化证据设计CPU管理协议理想管线 | [03e十项蓝图](03e_cpu_management_pipeline.md)、[92 §16.153](../92_br1_m6_m8_execution_baseline.md#cpu-management-pipeline-design)、[执行经验](CONVERGENCE.md#accepted-facts-lesson)、[代码位置](CODE_INDEX.md#cpu-management-pipeline-code-index) | 当前模板只读COW已复现；统一范围/claim事实，删除重复接纳和空交接。数量预测与条件明确，净时间尚未测定；原候选Undo阻塞保持。旧价格限制见[03d §10](03d_cpu_cost_calibrated_blueprint.md#projection-remaining-cost-priority) |
| 验收M6、评估handoff业务/GPU价值 | [92 §6.1–§6.3](../92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)、[最新执行变异诊断](../evidence/br1_m6_slow_operation_attribution_20261007/README.md)、[实际位置](CODE_INDEX.md#m6-execution-variance-code-index)、[V01](07_validation_and_migration.md) | CPU覆盖/E/P查询关联定位完成、就地ABBA候选否决；正式校准仍2/20、完整M6开放，诊断不授业务/GPU资格 |
| 按完整排期收口BR1 | [92 §17](../92_br1_m6_m8_execution_baseline.md#br1-closure-schedule)、[CP代码索引](CODE_INDEX.md#closure-code-index)、[CP清点](CONVERGENCE_CHECKLIST.md#closure-package-checklist) | CP0–CP10 → 原责任/函数 → 同批合并删除 → 有限交付 → 阶段冻结；工时只在92维护 |
| 决定何时接线、何时默认启用、何时停止细化 | [收敛与统一验收](CONVERGENCE.md) | 有限阻塞 → 首条真实链 → 资源启用门 → 主干对照与交付模板 |
| 按明确目标领取和清点收敛改动 | [收敛目标与改动清点](CONVERGENCE_CHECKLIST.md) | 目标出口 → 代码端点 → 精确断言 → 保留/合并/条件删除；附全文件清点 |
| 规划 API 的替代、合并与删除 | [API_CONVERGENCE_MAP](API_CONVERGENCE_MAP.md) | 当前函数 → 最终职责 → caller 迁移 → 删除对象 → 锁/寿命与验收 |
| 从优化问题定位改动 | [设计与代码关系总表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/CHANGE_MAP.md) | 原问题 → 92 条款 → 15 个修改 ID → 代码与联动终点 |
| 领取下一批实现 | [待改代码段与实施入口](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/NEXT_EDITS.md) | 当前已有 → 尚需修改 → 主改函数 → 完成判据 |
| 对接写权限寿命、adapter 交付与下一批候选 | [AD1–AD6：原能力交付](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#adapter-delivery-implementation) | 已改函数 → 锁序与失败终点 → HX7/OP6/OP7 的下一段代码 |
| 接 BC9 首字节前 backing 准备与资源收敛 | [OP9 原子准备边界](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#operation-pressure-boundary) | 全目标准备 → 本 execution 回滚 → 同 owner 重试 → 完整收费、多 store/多文档公平与释放进度；结果分类等待安全 consumer 同批出现 |
| 修改 wrapper、hash 与 GC | [HX1–HX10：hash 存储与回收](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#hash-storage-map) | 原函数 → 实際节点/引用归属 → prepare/install/cleanup → 故障与并发验收 |
| 接通真实绘画链 | [BC1–BC10 联合接线表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01j_real_stroke_integration.md#stroke-integration-map) | 原事务 → painter/job → 同步/异步入口 → 读选择 → 显示 cut → finish/cancel |
| 从正在编辑的文件反查 | [源码反向索引](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/CODE_INDEX.md) | 文件 → 全部相关修改项与主题指南 |
| 安排依赖与阶段交付 | [M1–M5 调整及 M6–M8 对照](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/STAGE_MAP.md) | 前置改动 → 可审查批次 → 默认启用条件 → 阶段出口 |

当前完整路线按92 §17：先CP1完整控制存储，再CP2/CP3关闭M6、CP4实现M7，随后CP5压力/原job接续、CP6读发布族、CP7复杂stroke、CP8 undo/context、CP9/CP10最终资格与性能。首条direct及联合fixture已有冻结证据，正式默认仍关闭；缺口见92 §16.28。主干public/protected API保持默认净增长零，typed continuation只与唯一原owner、实际consumer和旧失败分支合并同包交付。资格矩阵、工时不在本目录复制维护。

## 15 项修改目录

每个 ID 沿同一契约实施；“主改”是必须改变的行为，“联动”是必须审查的责任，不表示整份文件重写。表中详细主题给出函数入口、失败路径与验证落点。

| ID | 待改内容 | 92 的约束来源 | 指南与主要落点 | 92 §13 单元 |
|---|---|---|---|---|
| S01 | 失败传播、成功才结束事务、整笔/单操作取消 | §9.3 | [01：失败与 scope](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01_stroke_scope_and_failure.md)；TransactionData、strategy、painter、scheduler、backend | A |
| S02 | 跨 dab session、跨 worker borrow、稳定 entries | §8.2–8.3、§9.1–9.2 | [01c：SS1–SS10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md)；MutationSession、MutationWriteSet、admission、iterator | C |
| S03 | brush/direct/indirect/mask/LoD 接线及写后索引刷新 | §9.1、§9.5 | [01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01_stroke_scope_and_failure.md)；stroke jobs、PaintDevice、DataManager | D |
| S04 | 读取意图、checkpoint、显示与完整 exact cut | §9.4–9.5 | [02：可见性与发布](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/02_visibility_and_publication.md)；seal/capture、dirty/update、read scope | E |
| S05 | 外层短 publication gate、候选准备和有限立即重试 | §10.3 | [02](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/02_visibility_and_publication.md)；backend、PublicationCoordinator、root/metadata | E |
| S06 | 唯一 selector、M6/M7 claims 与一次性准备 | §2–§4、§10.1 | [03：首写与 handoff](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03_write_plans_and_hot_path.md)；WriteCoordinator、StateMachine、provider/binding | B |
| S07 | provider domain 对账无变化快路径 | §10.2 | [03](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03_write_plans_and_hot_path.md)；reserveBacking、OwnerLedger、domain journal | B/F |
| S08 | root/version 有界扫描、跨 store 公平回收 | §10.4 | [04：回收与预算](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04_reclamation_and_budgets.md)；HistoryCollector、epoch owner、reclaimer | F |
| S09 | 最后 pin/completion 唤醒退休与等待者 | §10.5 | [04](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04_reclamation_and_budgets.md)；RetirementQueue、binding、completion | F |
| S10 | 局部/全局配额、长 stroke 窗口与计账 | §9.5、§10.5–10.6 | [04](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04_reclamation_and_budgets.md)；budget、TileDataStore、真实 allocator | F/C |
| U01 | undo delta 贯穿兼容索引，移除普通恢复全量重建 | §11.1 | [05：undo 与缓存](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/05_undo_delta.md)；MementoManager、backend restore、DataManager | G |
| U02 | extent、像素边界缓存、history purge 分责 | §11.2–11.3 | [05](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/05_undo_delta.md)；TiledExtentManager、PaintDeviceCache、purge | G/F |
| C01 | 有界 preset 准备缓存、热切/冷准备/设置 debounce | §12.1–12.2 | [06：上下文切换](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/06_context_switching.md)；PresetShadowUpdater、ResourcesSnapshot、preset/settings | H |
| C02 | 内容上下文失效与 interstroke 兼容性 | §12.3–12.4 | [06](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/06_context_switching.md)；目标/frame/LoD、资源依赖、interstroke commands | H/D |
| V01 | 因果计数、产品 replay、正式门与删除证据 | §6、§8.1、§13–§14 | [07：验证与迁移](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/07_validation_and_migration.md)；diagnostics、现有测试、证据脚本 | A–H |

## 函数级细分指南

以下编号细分原 15 个 ID，不另立状态权威。优先阅读该文件的当前边界与剩余项；实施记录中的历史通过只覆盖其冻结源码和测试范围。

| 细分指南 | 关联 ID | 要修改的具体边界 |
|---|---|---|
| [01a](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01a_transaction_completion_callers.md) | S01 | 事务终结 caller、void 包装与失败责任 |
| [01b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01b_pixel_failure_boundaries.md) | S01/S03 | 像素结果、错误上送与单操作/整笔回退 |
| [01c](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md) | S02 | SS/A/J/CP：稳定 slots、实际准入、job borrow、checkpoint |
| [01d](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01d_metadata_refresh_and_pending_visibility.md) | S03/S04 | MR：成功元数据刷新、失败字节恢复与发布前准备 |
| [01e](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01e_scheduler_cut_and_job_admission.md) | S02/S04 | SC：原 scheduler cut、必要子任务与后续输入 |
| [01f](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01f_history_owned_mutation_scope.md) | S02 | HS：原 history/memento 持有 session 与终结 |
| [01g](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01g_multi_dab_and_painter_scope.md) | S03 | MD：真实 multi-dab 消费者、owner、读写与验证 |
| [01h](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01h_sparse_write_footprints.md) | S03 | SR：实际 dab 交集的页并集与范围拒绝 |
| [01i](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01i_page_owned_brush_jobs.md) | S03 | PG：映射后同页归一个 job，独立页并行 |
| [01j](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01j_real_stroke_integration.md) | S01–S05/S10/C02/V01 | BC：真实 stroke 联合接线；初始化到显示、结束与取消 |
| [01k](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01k_fixed_source_and_sharpness.md) | S01/S03/S04/V01 | FC：固定源 cursor、同步 sharpness 镜像、wrap 与分块合成一致性 |
| [01l](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01l_write_context.md) | S03/C02/V01 | WC：原事务与真实 jobs 的 target/offset/wrap 复验，拒绝后的取消与完成上报 |
| [01m](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md) | S01/S03/S05/S09/S10 | OP：首字节前实际存储、适配安装、失败/回收与旁路 |
| [01n](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md) | S03/S05/S09/S10/V01 | HX：QSBR 记录准备、迁移回收、竞争插入、clear/析构与真实 map 安装凭据；逐段区分局部准备和 operation 写前准入 |
| [JP1–JP8：联合发布的观察边界与逐段改法](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/02a_joint_publication_boundaries.md#joint-publication-map) | S04/S05、OP6/OP7、U01 | overlay/root 准备、surface delta、真实读取边界、manager 锁序及终结/预算 |
| [03a](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md) | S06 | 访问身份、CPU recoverable 共同计划、M6/M7 准备/安装 |
| [03b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03b_legacy_cache_migration.md) | S06.3 | L：canonical cache、局部 pin、batch borrow 与 idle 引用 |
| [03c](03c_cpu_write_execution_blueprint.md) | S02/S03、OP1/OP9、S06/S07、V01 | CPU写入算法蓝图：同一operation按页稳定消费、范围只读借用、B1–B12迁移与条件收益 |
| [04a](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md) | S09 | R/T：退休通知、last-use、终结存储、取消/退出 |
| [04b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04b_budget_waiter_implementation_map.md) | S10 | W：预算等待、实际授额、原消费者与归还 |
| [04c](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04c_generic_write_admission.md) | S09/S10 | GW：通用写 request/lease 的准备、异常与终结 |

## 从流程全图定位修改项

[管线全图](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_pipeline_map_20260925.md)解释冻结源码的职责与调用关系；[设计审视](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_pipeline_design_review_20260925.md)提供问题来源。实施目标和当前资格统一回到 92，不能将全图中的旧源码状态当成工作树现状。

| 管线段 | 对应修改项 | 修改后的责任边界 / 详细指南 |
|---|---|---|
| stroke 初始化、job 调度、结束/取消 | S01、S03 | 结果传到唯一事务 owner；成功才登记 undo，未处理像素失败进入既有取消链；[01 / 01a / 01b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01_stroke_scope_and_failure.md) |
| dab / iterator 借用可写页 | S02、S03 | 业务持有 session，job 借用执行权，guard 释放只解除短 pin；稳定 entry 复用；[01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01_stroke_scope_and_failure.md) |
| 首写选择、物理 backing 与预算准入 | S06、S07、S10 | 唯一 selector 选择 Fresh / 合法 handoff，provider 负责物理排斥，预算 owner 负责实际收费；[03](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03_write_plans_and_hot_path.md)、[03a](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md)、[04](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04_reclamation_and_budgets.md) |
| 精确读、显示、save 与写后兼容索引 | S03、S04 | 区分读取意图和完整 exact cut，按实际 freeze 决定下一次 COW；更新展示不能暗中冻结每个 dab；[02](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/02_visibility_and_publication.md) |
| seal / root publication / 旧选择释放 | S05、S01 | 锁外准备实际存储，短 gate 复验安装；失败保留终结责任，旧选择保护跨越事务移除；[02](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/02_visibility_and_publication.md) |
| history GC、retirement、压力与关闭 | S08、S09、S10 | 整个维护 pass 有界，最后 pin/completion 唤醒，局部与全局资源都能收敛；[04](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04_reclamation_and_budgets.md) |
| undo / redo / extent 与内容缓存 | U01、U02 | changed delta 贯穿外层适配，不以全量重建恢复固定 K；[05](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/05_undo_delta.md) |
| 切笔刷、切层、frame / LoD | C01、C02 | 既有 owner 中维护有界不可变准备缓存，依赖失效准确，不缓存绘画执行权限；[06](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/06_context_switching.md) |
| 全链路观测、比较与删除 | V01 | 每个改动绑定源码、二进制、语义/失败证据和 stroke 控制桶；[07](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/07_validation_and_migration.md) |

## 修改依赖与启用顺序

1. V01 冻结源码/测试身份及 stroke replay；S01 明确并接通结果与终结链。
2. S06 依照 92 的 **M6 → M7** 顺序验收，保留 Fresh。S07 的对账优化单独证明，不借 handoff 成绩掩盖预算问题。
3. 为长寿命 scope 建立 S08/S09/S10 的必要资源与进度保证；S02 可先实现受测能力。
4. **S02 + S03 + S04 + S05 是 stroke 启用闭环。** 不能只延长 pending，留下旧的写后 capture、projection 或结束逻辑。
5. 按 direct/common composite → indirect/mask/source-dependent → wrapped/LoD/异步入口迁移，每批保留同输入语义和性能证据。
6. 再推进 U01/U02，然后 C01/C02；独立准备可先进行，不能让后两类收益抵消 stroke 回退。
7. V01 汇总正式 BR1-PERF、生命周期和删除证据，只有 92 更新阶段状态。

## 每批修改的交付要求

每批记录：**修改 ID/92 条款 → 实际函数与 caller → 唯一 owner → 准备/成功/失败/取消/析构 → 测试与源码/二进制身份 → stroke 主桶和控制桶 → 剩余项**。领取模板见 [NEXT_EDITS](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/NEXT_EDITS.md)，验证与迁移规则见 [V01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/07_validation_and_migration.md)。

修改一个文件前，从 CODE_INDEX 核对它涉及的全部 ID；实现后同步主题指南、NEXT_EDITS 和反向索引。行号是检索入口，符号及当前代码才是修改依据。改变业务契约或阶段资格必须回到 92，不在子指南中暗改失败保证、可见性或硬预算。

本次目录整理和 BC1–BC10 符号核对见[文档检查记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_guide_stroke_chain_20260928/README.md)；已有[目录初次核对](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_guide_directory_20260928/README.md)、[multi-dab 映射核对](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_guide_code_map_20260928/README.md)保留各自范围。文档检查不代替生产构建、行为测试或性能资格；各批冻结证据查 92 §15，当前裁决查 92 §16。
