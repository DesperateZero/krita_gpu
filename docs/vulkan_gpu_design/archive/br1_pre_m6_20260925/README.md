# BR1 M6 前的历史资料归档

47–91 共 **45 篇**文档已移入 [`documents/`](documents/)；旧主目录文件不再存在。归档保留失败样本、证据和归档正文之间的可浏览链接；它们不再是当前执行计划、状态判据或 API 模板。当前只维护 [92：M6–M8 与 BR1 收口](../../92_br1_m6_m8_execution_baseline.md)。

原 52 的性能约束、68 的 handoff/预算/安全条件、69 的唯一权威和删除门、86 的验证纪律已汇入 92；全局 00/22/31、语义 25/33 和正式性能 39 仍有效。归档没有降低验收门槛，也不把旧失败改成通过。

- 47–51：早期 owner、cutover 和功能切片。
- 52–67：旧调优计划、归因实验与迭代方案。
- 68–86：原重构目标、阶段计划、清理规则与 M5 审计；活动规则转入 92，旧类型草图不再照抄实施。
- 87–91：M5 收敛、重审、修复和修复前条件计划；包含被撤回判断及确定性反例。

## 文档索引

- [47_br1_ps_sm1_epoch_metadata_evidence_20260919.md](documents/47_br1_ps_sm1_epoch_metadata_evidence_20260919.md)
- [48_br1_cpu_owner_api_correction_20260919.md](documents/48_br1_cpu_owner_api_correction_20260919.md)
- [49_br1_transaction_lifecycle_tiles3_shadow_20260919.md](documents/49_br1_transaction_lifecycle_tiles3_shadow_20260919.md)
- [50_br1_cpu_access_and_history_restore_20260919.md](documents/50_br1_cpu_access_and_history_restore_20260919.md)
- [51_br1_canonical_pagestore_closure_20260919.md](documents/51_br1_canonical_pagestore_closure_20260919.md)
- [52_br1_cpu_fast_path_optimization_plan_20260920.md](documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)
- [53_br1_performance_attribution_review_20260920.md](documents/53_br1_performance_attribution_review_20260920.md)
- [54_br1_optimization_execution_and_deviations_20260920.md](documents/54_br1_optimization_execution_and_deviations_20260920.md)
- [55_br1_d2_phase_measurement_and_atomic_transaction_begin_20260920.md](documents/55_br1_d2_phase_measurement_and_atomic_transaction_begin_20260920.md)
- [56_br1_prepared_metadata_publication_20260920.md](documents/56_br1_prepared_metadata_publication_20260920.md)
- [57_br1_sampled_write_pipeline_and_immutable_directory_20260920.md](documents/57_br1_sampled_write_pipeline_and_immutable_directory_20260920.md)
- [58_br1_native_cow_initialization_and_payload_accounting_20260920.md](documents/58_br1_native_cow_initialization_and_payload_accounting_20260920.md)
- [59_br1_shared_upstream_cpu_baseline_20260920.md](documents/59_br1_shared_upstream_cpu_baseline_20260920.md)
- [60_br1_completion_coverage_and_sparse_terminal_status_20260920.md](documents/60_br1_completion_coverage_and_sparse_terminal_status_20260920.md)
- [61_br1_captured_read_scope_and_integration_cost_20260920.md](documents/61_br1_captured_read_scope_and_integration_cost_20260920.md)
- [62_br1_native_resident_read_and_write_cost_20260920.md](documents/62_br1_native_resident_read_and_write_cost_20260920.md)
- [63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md](documents/63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md)
- [64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md](documents/64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md)
- [65_br1_native_cpu_mutation_segment_20260920.md](documents/65_br1_native_cpu_mutation_segment_20260920.md)
- [66_br1_physical_exclusivity_prerequisite_20260920.md](documents/66_br1_physical_exclusivity_prerequisite_20260920.md)
- [67_br1_target_structure_reconstruction_20260920.md](documents/67_br1_target_structure_reconstruction_20260920.md)
- [68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md](documents/68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md)
- [69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md](documents/69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md)
- [70_br1_r0_containment_and_layout_gate_20260921.md](documents/70_br1_r0_containment_and_layout_gate_20260921.md)
- [71_br1_r0_runtime_census_and_test_binding_20260922.md](documents/71_br1_r0_runtime_census_and_test_binding_20260922.md)
- [72_br1_r0_reverse_callgraph_and_closure_20260922.md](documents/72_br1_r0_reverse_callgraph_and_closure_20260922.md)
- [73_br1_r1_default_storage_extraction_20260922.md](documents/73_br1_r1_default_storage_extraction_20260922.md)
- [74_br1_r1_retirement_queue_extraction_20260922.md](documents/74_br1_r1_retirement_queue_extraction_20260922.md)
- [75_br1_r1_history_read_publication_extraction_20260922.md](documents/75_br1_r1_history_read_publication_extraction_20260922.md)
- [76_br1_r2_m1_compact_metadata_records_20260922.md](documents/76_br1_r2_m1_compact_metadata_records_20260922.md)
- [77_br1_r2_m2a_shard_metadata_arenas_20260922.md](documents/77_br1_r2_m2a_shard_metadata_arenas_20260922.md)
- [78_br1_r2_m2b_lock_external_metadata_growth_20260922.md](documents/78_br1_r2_m2b_lock_external_metadata_growth_20260922.md)
- [79_br1_r2_m3a_shard_indexes_and_intrusive_records_20260922.md](documents/79_br1_r2_m3a_shard_indexes_and_intrusive_records_20260922.md)
- [80_br1_r2_m3b_compact_page_activity_20260922.md](documents/80_br1_r2_m3b_compact_page_activity_20260922.md)
- [81_br1_r2_m4_allocation_free_publication_20260922.md](documents/81_br1_r2_m4_allocation_free_publication_20260922.md)
- [82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md](documents/82_br1_r3_m5a_write_schema_admission_and_budget_20260922.md)
- [83_br1_r3_m5b_store_session_write_migration_20260923.md](documents/83_br1_r3_m5b_store_session_write_migration_20260923.md)
- [84_br1_full_optimization_convergence_and_cleanup_20260923.md](documents/84_br1_full_optimization_convergence_and_cleanup_20260923.md)
- [85_br1_m5_code_readiness_audit_20260924.md](documents/85_br1_m5_code_readiness_audit_20260924.md)
- [86_br1_m5_final_convergence_plan_20260925.md](documents/86_br1_m5_final_convergence_plan_20260925.md)
- [87_br1_m5_batches_1_3_execution_20260925.md](documents/87_br1_m5_batches_1_3_execution_20260925.md)
- [88_br1_m5_post_convergence_reaudit_20260925.md](documents/88_br1_m5_post_convergence_reaudit_20260925.md)
- [89_br1_m5_reaudit_findings_resolution_20260925.md](documents/89_br1_m5_reaudit_findings_resolution_20260925.md)
- [90_br1_m5_baseline_freeze_review_20260925.md](documents/90_br1_m5_baseline_freeze_review_20260925.md)
- [91_br1_m6_to_completion_entry_plan_20260925.md](documents/91_br1_m6_to_completion_entry_plan_20260925.md)

[`manifest.json`](manifest.json) 同时保存旧路径、归档路径、迁移前后 SHA256 和来源提交 `20adec2ac0438e27a8ced7d6087dee6f696373f8`。因相对链接随位置重写，当前归档文件与迁移前文件的字节不同；可从该提交的旧路径逐字节恢复原件，并用原始文件/正文哈希核对。[`verify_archive.py`](verify_archive.py) 验证路径、来源和链接。`previous-entry-snapshots.json` 保存归并前 00/31/README 的全文和哈希；不把旧状态继续留在活动入口里。冻结的 `evidence/` README 与哈希清单保持原始字节，因此其中指向 47–91 旧路径的 48 个链接需按 `manifest.json` 映射到本索引；未改写证据或重新绑定历史哈希。

此前 [35 篇调优记录的归档](../br1_tuning_20260925/README.md) 保留为归档历史，本次覆盖范围扩展到 47–91。生产修复与新验证见 [本轮证据](../../evidence/br1_m5_repair_20260925/README.md)。
