> **归档历史：** 本索引记录上一轮 35 篇归档动作；当时的状态判断及“原位归档”叙述只属于该检查点。这些文件现已移入 [47–91 共 45 篇的实体归档](../br1_pre_m6_20260925/README.md)，唯一当前执行入口是 [92](../../92_br1_m6_m8_execution_baseline.md)。

# BR1 调优与收敛历史归档（2026-09-25）

**历史检查点：当时 M5-ready 基线尚未通过。** 当时裁决见 [90](../br1_pre_m6_20260925/documents/90_br1_m5_baseline_freeze_review_20260925.md)，当时的 B1–B6 → M6 → M7 → M8 → BR1-PERF 条件路线见 [91](../br1_pre_m6_20260925/documents/91_br1_m6_to_completion_entry_plan_20260925.md)。

本索引最初采用原位归档；现在下列文件已实际移动，表中链接指向新位置。旧路径可从来源提交恢复，失败样本继续可查。归档不表示这些版本都曾通过验收。

当时引用的 52/68/69/86 已归档；其中仍有效的 BR1 约束汇入 [92](../../92_br1_m6_m8_execution_baseline.md)。全局 00/22/31、语义 25/33 和性能 39 仍按当前入口使用。

[00 原第 2 节快照](00_status_section2_before_review.md) 保存旧状态长时间线；[manifest.json](manifest.json) 记录每篇归档前 SHA-256。本轮开始已存在的 00/68/69/84 修改保存为 [原始补丁](../../evidence/br1_m5_baseline_review_20260925/pre-review-worktree.json)。

| 编号 | 历史资料 | 角色 |
|---|---|---|
| 51 | [51_br1_canonical_pagestore_closure_20260919.md](../br1_pre_m6_20260925/documents/51_br1_canonical_pagestore_closure_20260919.md) | 功能切换历史 |
| 53 | [53_br1_performance_attribution_review_20260920.md](../br1_pre_m6_20260925/documents/53_br1_performance_attribution_review_20260920.md) | 性能切片/归因 |
| 54 | [54_br1_optimization_execution_and_deviations_20260920.md](../br1_pre_m6_20260925/documents/54_br1_optimization_execution_and_deviations_20260920.md) | 性能切片/归因 |
| 55 | [55_br1_d2_phase_measurement_and_atomic_transaction_begin_20260920.md](../br1_pre_m6_20260925/documents/55_br1_d2_phase_measurement_and_atomic_transaction_begin_20260920.md) | 性能切片/归因 |
| 56 | [56_br1_prepared_metadata_publication_20260920.md](../br1_pre_m6_20260925/documents/56_br1_prepared_metadata_publication_20260920.md) | 性能切片/归因 |
| 57 | [57_br1_sampled_write_pipeline_and_immutable_directory_20260920.md](../br1_pre_m6_20260925/documents/57_br1_sampled_write_pipeline_and_immutable_directory_20260920.md) | 性能切片/归因 |
| 58 | [58_br1_native_cow_initialization_and_payload_accounting_20260920.md](../br1_pre_m6_20260925/documents/58_br1_native_cow_initialization_and_payload_accounting_20260920.md) | 性能切片/归因 |
| 59 | [59_br1_shared_upstream_cpu_baseline_20260920.md](../br1_pre_m6_20260925/documents/59_br1_shared_upstream_cpu_baseline_20260920.md) | 性能切片/归因 |
| 60 | [60_br1_completion_coverage_and_sparse_terminal_status_20260920.md](../br1_pre_m6_20260925/documents/60_br1_completion_coverage_and_sparse_terminal_status_20260920.md) | 性能切片/归因 |
| 61 | [61_br1_captured_read_scope_and_integration_cost_20260920.md](../br1_pre_m6_20260925/documents/61_br1_captured_read_scope_and_integration_cost_20260920.md) | 性能切片/归因 |
| 62 | [62_br1_native_resident_read_and_write_cost_20260920.md](../br1_pre_m6_20260925/documents/62_br1_native_resident_read_and_write_cost_20260920.md) | 性能切片/归因 |
| 63 | [63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md](../br1_pre_m6_20260925/documents/63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md) | 性能切片/归因 |
| 64 | [64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md](../br1_pre_m6_20260925/documents/64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md) | 性能切片/归因 |
| 65 | [65_br1_native_cpu_mutation_segment_20260920.md](../br1_pre_m6_20260925/documents/65_br1_native_cpu_mutation_segment_20260920.md) | 性能切片/归因 |
| 66 | [66_br1_physical_exclusivity_prerequisite_20260920.md](../br1_pre_m6_20260925/documents/66_br1_physical_exclusivity_prerequisite_20260920.md) | 性能切片/归因 |
| 67 | [67_br1_target_structure_reconstruction_20260920.md](../br1_pre_m6_20260925/documents/67_br1_target_structure_reconstruction_20260920.md) | 整体重构执行记录 |
| 70 | [70_br1_r0_containment_and_layout_gate_20260921.md](../br1_pre_m6_20260925/documents/70_br1_r0_containment_and_layout_gate_20260921.md) | R0–M5 阶段记录 |
| 71 | [71_br1_r0_runtime_census_and_test_binding_20260922.md](../br1_pre_m6_20260925/documents/71_br1_r0_runtime_census_and_test_binding_20260922.md) | R0–M5 阶段记录 |
| 72 | [72_br1_r0_reverse_callgraph_and_closure_20260922.md](../br1_pre_m6_20260925/documents/72_br1_r0_reverse_callgraph_and_closure_20260922.md) | R0–M5 阶段记录 |
| 73 | [73_br1_r1_default_storage_extraction_20260922.md](../br1_pre_m6_20260925/documents/73_br1_r1_default_storage_extraction_20260922.md) | R0–M5 阶段记录 |
| 74 | [74_br1_r1_retirement_queue_extraction_20260922.md](../br1_pre_m6_20260925/documents/74_br1_r1_retirement_queue_extraction_20260922.md) | R0–M5 阶段记录 |
| 75 | [75_br1_r1_history_read_publication_extraction_20260922.md](../br1_pre_m6_20260925/documents/75_br1_r1_history_read_publication_extraction_20260922.md) | R0–M5 阶段记录 |
| 76 | [76_br1_r2_m1_compact_metadata_records_20260922.md](../br1_pre_m6_20260925/documents/76_br1_r2_m1_compact_metadata_records_20260922.md) | R0–M5 阶段记录 |
| 77 | [77_br1_r2_m2a_shard_metadata_arenas_20260922.md](../br1_pre_m6_20260925/documents/77_br1_r2_m2a_shard_metadata_arenas_20260922.md) | R0–M5 阶段记录 |
| 78 | [78_br1_r2_m2b_lock_external_metadata_growth_20260922.md](../br1_pre_m6_20260925/documents/78_br1_r2_m2b_lock_external_metadata_growth_20260922.md) | R0–M5 阶段记录 |
| 79 | [79_br1_r2_m3a_shard_indexes_and_intrusive_records_20260922.md](../br1_pre_m6_20260925/documents/79_br1_r2_m3a_shard_indexes_and_intrusive_records_20260922.md) | R0–M5 阶段记录 |
| 80 | [80_br1_r2_m3b_compact_page_activity_20260922.md](../br1_pre_m6_20260925/documents/80_br1_r2_m3b_compact_page_activity_20260922.md) | R0–M5 阶段记录 |
| 81 | [81_br1_r2_m4_allocation_free_publication_20260922.md](../br1_pre_m6_20260925/documents/81_br1_r2_m4_allocation_free_publication_20260922.md) | R0–M5 阶段记录 |
| 82 | [82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md](../br1_pre_m6_20260925/documents/82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md) | R0–M5 阶段记录 |
| 83 | [83_br1_r3_m5b_store_session_write_migration_20260923.md](../br1_pre_m6_20260925/documents/83_br1_r3_m5b_store_session_write_migration_20260923.md) | R0–M5 阶段记录 |
| 84 | [84_br1_full_optimization_convergence_and_cleanup_20260923.md](../br1_pre_m6_20260925/documents/84_br1_full_optimization_convergence_and_cleanup_20260923.md) | 收敛、审计、方案或修复历史 |
| 85 | [85_br1_m5_code_readiness_audit_20260924.md](../br1_pre_m6_20260925/documents/85_br1_m5_code_readiness_audit_20260924.md) | 收敛、审计、方案或修复历史 |
| 87 | [87_br1_m5_batches_1_3_execution_20260925.md](../br1_pre_m6_20260925/documents/87_br1_m5_batches_1_3_execution_20260925.md) | 收敛、审计、方案或修复历史 |
| 88 | [88_br1_m5_post_convergence_reaudit_20260925.md](../br1_pre_m6_20260925/documents/88_br1_m5_post_convergence_reaudit_20260925.md) | 收敛、审计、方案或修复历史 |
| 89 | [89_br1_m5_reaudit_findings_resolution_20260925.md](../br1_pre_m6_20260925/documents/89_br1_m5_reaudit_findings_resolution_20260925.md) | 收敛、审计、方案或修复历史 |

禁止把旧样本重标为新源码结果；正式 baseline 必须由 91 B1–B6 形成新的 source/binary/配置身份后再登记。
