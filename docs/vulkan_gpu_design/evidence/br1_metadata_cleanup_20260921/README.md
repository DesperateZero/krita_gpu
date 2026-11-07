# Publication metadata cleanup ownership（2026-09-21）

对应 [67 §31](../../67_br1_target_structure_reconstruction_20260920.md#31-2026-09-21publication-cleanup-所有权移出-owner-gate)：
已消费的 publication candidate、失败候选与 fused swap 换出的旧 record-set 可由 move-only cleanup 持有；PageStore commit/restore 在
owner gate 外清空。成功 commit 在该开锁点之前取得新 epoch retention，metadata-before-root 与动态事实复验不变。

## 构建、反例与最终矩阵

- `checked-build`：生产库编译完成，新增测试因误用不可见的 `findVersion` helper 编译失败；未运行旧 binary。
- `fixed-build`：CPU/Vulkan 两套构建通过。`fixed-focus` 保留 **106 passed / 2 failed**：history=31 再加 current 与 prepared target 共
  33 records，按既有 fused 32-record 上限应当拒绝；fixture 改为边界内 history=30，没有修改生产预算。
- `verified-build/verified-focus`：两套构建及 **108/76/52 passed**。
- `verified-full`：完整 15 套 **1340 passed**，选定 paint-device **9 passed**，3 组各 20 次共 **60 次重复**全过，合计
  **76 个测试进程**。Reference 295、CpuMutation 465；Qt totals 含 init/cleanup，重复不混入完整套件总数。

```sh
node docs/vulkan_gpu_design/evidence/br1_metadata_cleanup_20260921/verify-checkpoint.mjs
```

新增四行覆盖 history=0/30 × 成功/晚期 read 冲突拒绝；两类结果都产生非空 cleanup，并在 coordinator 销毁后清空，证明没有可解引用的
shard/coordinator 生命周期依赖。生产测试在 `CommitCleanup` observer 中重新取得 owner 状态，证明相位确实位于 owner gate 外。

当前 `clear()` 仍由提交线程同步执行，未按时间/字节预算，也未接入 mutation install；它仍计入完整 E。没有 benchmark、TSAN、后台
cleanup 吞吐/积压、原位 permit 或性能资格结论。`structural_completion=false`、`performance_qualification=false`。
