# Budgeted metadata cleanup and host-ready evidence（2026-09-21）

对应 [67 §32](../../67_br1_target_structure_reconstruction_20260920.md#32-2026-09-21分批-metadata-cleanup-与预完成-host-evidence)：
小 metadata candidate 在 owner 外同步清空；大候选按 candidate-page unit 进入单线程 reclaimer，每 pass 最多 16 units 并在 unit 间检查
1 ms 协作预算。mutation/commit/restore 共享该协议，wait/close 可 drain。同步 host work 复用 configure 时建立的一张已终态 ticket。

## 构建与保留反例

- `checked-build`：CPU 构建在生产编译期失败，因为自由函数签名点名了 coordinator 的私有 nested cleanup 类型。改为类型不泄露的内部
  模板 executor；没有把 cleanup 类型公开，也没有运行旧 binary。
- `fixed-*`、`verified-*`：修复封装后和补充 wait/close、queue telemetry 后的中间构建/聚焦均通过。
- `final-*`：分批 cleanup 版本完整 15 套 1341 passed；随后预完成 host evidence 落地。
- `completion-build/completion-focus/completion-full`：最终源码两套构建、focused **108/78/52 passed**；完整 **15 套 1342 passed**、
  paint-device 选定 9、三组各 20 次共 60 次重复全过，合计 76 个测试进程。Reference 295、CpuMutation 467。

```sh
node docs/vulkan_gpu_design/evidence/br1_budgeted_cleanup_20260921/verify-checkpoint.mjs
```

确定性回归先用 reclaimer barrier 阻塞 worker：17 页 mutation detachment 与 17 页 commit 分别只入队，观测 2 candidates、34 pending/peak
units、0 passes；释放后至少 4 passes、每 pass 1..16 units、completed=2、pending=0，并记录 pass/queue 时间。直接 cleanup 测试还覆盖零预算、
单 unit、coordinator 先销毁。host source 经多轮真实写、commit 与 default publication 后仍为 1 allocated/terminal/storage、0 pending。

unit 不是 record/byte；1 ms 只在 unit 间检查，不是硬实时保证。PageStore 其他候选/proof/postwork 仍未统一移交。没有 benchmark、TSAN、
原位 permit 或性能资格结论；`structural_completion=false`、`performance_qualification=false`。
