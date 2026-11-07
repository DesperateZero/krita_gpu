# required 清单发现后的有限安全补证

原性能批次已经完成，PLAN.md 和 100 个过程的样本不再变更。产品起点仍为 38834c4e2612c819f9d088dfd59c59889f295a49。

当前 exactGenerationArchivePreservesPublishedAuthorityOnFailure 在 1 MiB ample budget 下只使用注入写失败，不能证明实际 archive byteBudget 耗尽。扩展同一测试，保留原 ample 行，增加 1/4/8/16 BPP 的一页容量：第二个 exact generation 因预算拒绝，原 archive/current/retained old bytes 保持；forget 旧记录后同一 store/archive 重试成功，旧 retained View 仍可读，最后原 capability/record 清理完成。

只修改测试，不改生产容量/策略、不新增 SSD handoff producer，不声称物理磁盘满或全部压力组合覆盖。构建并运行两架完整 ReferenceTest，记录源码/实际加载/退出/失败。如测试实现出错，保留失败并修复有限责任。未改生产库的原安全/性能保持各自冻结身份；新测试与原 11180 通过数不相加成重跑全矩阵。清单 R03 只增加有限覆盖，完整 CP0 和其他压力要求仍独立。
