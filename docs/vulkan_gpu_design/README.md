# Vulkan / BR1 文档入口

继续 M6 时，先读 [92 §1 当前产品](92_br1_m6_m8_execution_baseline.md#native-cpu-baseline)和 [§6.1 机会型能力门](92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)。只有任务涉及某个子系统时，再按下表取对应材料。更新当前状态时替换对应条目；逐轮过程留在该次证据包。

| 要判断的事 | 当前依据及适用范围 |
|---|---|
| 产品、阶段与公开合同 | [00 状态词与 MVP](00_status_and_mvp_contract.md)、[22 P0 架构](22_p0_vulkan_baseline_reconstruction.md)、[31 阶段依赖](31_p0_reset_and_execution_sequence.md)、[25 存储语义](25_p0_canonical_pagestore_krita_tile_cow_swap.md)、[33 状态机](33_virtual_texture_pagestore_state_machine.md)。阶段状态以 92 §1 为准 |
| BR0、Vulkan foundation 和显示 | [41 构建边界](41_vulkan_foundation_build_architecture.md)、[42 能力提取](42_legacy_vulkan_capability_extraction_matrix.md)、[43 建设顺序](43_foundation_construction_sequence_and_gates.md)、[44 合成与画布](44_shader_compositor_canvas_reconstruction.md)。按各模块自己的合同和证据追踪 |
| 提交实验材料、查原始证据或准备远端归档 | 从[双仓检出、复算与冷存索引](evidence/README.md)核对 CPU 基线、独立优化回执和历史材料的取回路径 |
| CPU native 产品实际提供什么 | 读 [0fd96 生产交付](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/write-unit-accounting/native-result-construction-104/production-integration/REPORT.md)。拆分后的六个单元、公共消费者、故障、终结与同义三方价格均有绑定。P 为上一个产品，U 为完整原型，N 为当前产品 |
| M6 如何验收 | [39 性能规则](39_virtual_texture_performance_gates.md)、[92 §6.1](92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)、[业务价值](92_br1_m6_m8_execution_baseline.md#m6-business-value)。固定 M5 对照、同义 upstream、P/U/N 分别回答不同问题 |
| GPU、UMA、SSD、切换和公共消费者迁移 | [32 架构决策](32_virtual_texture_architecture_decisions.md)、[34 GPU binding](34_virtual_texture_gpu_binding_and_arenas.md)、[35 UMA](35_virtual_texture_uma_pointer_bypass.md)、[36 dGPU](36_virtual_texture_dgpu_migration.md)、[37 SSD](37_virtual_texture_ssd_segment_store.md)、[38 驻留](38_virtual_texture_residency_temperature.md)。[105 完整设计](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/UNIFIED_BACKEND_DESIGN.md) 与原矩阵 `unified_backend_extension_105` 描述待实现的 UB01–UB16 |
| 笔刷、stroke、undo、上下文 | 按问题进入[业务修改指南](br1_modification_guide/README.md)的对应专题。核对当前实现与测试，沿用仍有消费者的行为约束。早期领取顺序、实现名和阶段进度只对应原批 |

<a id="evidence-scope"></a>
## 哪些优化结论继续适用

同一份报告可以有下表中的多种用途。先确定结论所指的责任及读者，再核对它依赖的实现、实测提交和端点。仅查到符号时只能确认代码存在。实现或端点变更后的收益需要同义复测。

| 设计或优化 | 继续使用的部分 | 只在什么条件下引用原记录 |
|---|---|---|
| 首层投影 clear 与合成融合 | 在 `8198c36ed7` 与 `0fd96f2fa3` 之间，merger、layer projection plane、painter 三个实现文件的 blob 均相同。`applyWithClear → bitBltAfterClear` 的适用域、已进入回调后的失败处理，以及正常/失败测试，仍供投影修改使用。[生产记录](evidence/br1_projection_boundary_production_20261010/README.md) | 原 ARM64 业务对照的 Stroke CPU 节省 1.20375 ms。该数只归当时的融合前后；原 prepare/seal 次数只归当时后端。当前 PageStore 相对 upstream 的差额独立取证。[比较口径](evidence/br1_pagestore_comparison_scope_20261010/README.md) |
| 固定源笔刷、Alpha Darken 分块 | FC6 的 U16/F32、mask 和分块一致性继续有实际消费者。当前 scalar/SIMD 使用 `calculateAlpha`，回归入口为 `testAlphaDarkenSpanInvariant`；sharpness 真实笔刷另有 `testSharpnessLine`。[原专题 FC6–FC7](br1_modification_guide/01k_fixed_source_and_sharpness.md) | 当时 provider prepare/seal 计数、原 owner 接线进度和整笔收益各自绑定原路径。调整像素内核时仍须保留整数精度与浮点容差的区分 |
| 真实预算、RAM/SSD、末次释放 | 公共 generic Store、Memento、provider 仍有消费者；native 直接使用共享预算、物理 binding 与 Tiles3 RAM/SSD。当前生产包有 1 MiB payload 压力下 1000 页真实换出/换入、读回及尾账证据。[生产交付](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/write-unit-accounting/native-result-construction-104/production-integration/REPORT.md) | 旧 private/seal/publication 的逐页单价仅可用于重放旧产品。公共接口仍存在，只能证明该责任有消费者，无法证明 native 每页支付旧价格 |
| 容量寿命、费用、Value、安装与 seal 的各代候选 | V1/V2/V3 原包可用于查原假设、已否决方向、代价如何转移及失败用例。85 的“入口减少仍需核对真实逐页工作与包外抵消”继续约束选题。[仓库成本约束](../../AGENTS.md) | 旧方案的“下一步”、旧责任占比和目标单价留在对应提交。若要在 0fd96 推进同一问题，先给出仍执行的具体消费者与同义端点。跨层的小 memcpy / 整页复制同理，保留比较方法，按当前分块与调用重新计价 |
| 104 产品化与 105 后续设计 | 104 的完整原型是 U 比较对象，正式 CPU 行为和价格取生产集成子包；105 的接口与失败矩阵供扩展设计使用。[104 生产回执](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/write-unit-accounting/native-result-construction-104/production-integration/REPORT.md) · [105 设计](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/UNIFIED_BACKEND_DESIGN.md) | 同一 V3 证据目录同时容纳退役候选、有效生产收据和后续设计。原型冻结价、当前产品价、未来能力分别引用；105 实施 0/16 |

对尚未逐条核对的专题，保留原文件、提交、测试和失败收据，按需查证。当一项结论仍适用时，在所属责任的入口留下来源、当前消费者、适用条件和需要重新测量的部分。原文中的“当前”“下一步”按其写作时点解释。

切换前的完整文档导航可在外层仓库用 `git show d6062041a5f1:docs/vulkan_gpu_design/README.md` 还原。92 §15–§17 留有逐批出处；常规 M6 工作从上面的合同和具体责任进入。
