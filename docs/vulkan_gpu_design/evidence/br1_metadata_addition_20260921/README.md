# Prepared default-record storage（2026-09-21）

对应 [67 §29](../../67_br1_target_structure_reconstruction_20260920.md#29-2026-09-21新增-default-record-的候选存储与容量准备)：
缺失 exact default 的 owning record node 由 publication candidate 构造；准备阶段按 exact page revision 为 live exact/slot hash
预留容量，安装在全批 claim/复验后 splice record，并断言 capacity 不变。没有为一个新增 default 复制 H 个历史 record。

## 构建与回归序列

- `checked-build`：CPU/Vulkan 两套构建通过。
- `checked-focus`：indexes 88 passed / 16 failed、publication 46 / 28 failed、packed 52 passed。失败暴露容量准备用尚未赋值的
  `entry.next.key` 回查页面；新增 kind3 fixture 也没有设置匹配 version 的 published-default header。
- `fixed-build/fixed-focus`：修正生产时序与 fixture 契约后重新构建，focused 104/74/52 passed；未放宽 revision、claim 或原子性。
- `fixed-full`：最终源码的完整 15 套、选定 paint-device，以及三组各 20 次重复。

最终 **15 套 1335 passed、选定 9 passed、60 次重复全过，共 76 个测试进程**；Reference 291、CpuMutation 464。
Qt totals 含 init/cleanup；完整套件与重复独立记账。最终无 FAIL/SAFE ASSERT/QFATAL，构建/链接与测试未并发。

```sh
node docs/vulkan_gpu_design/evidence/br1_metadata_addition_20260921/verify-checkpoint.mjs
```

## 覆盖与限制

候选矩阵扩为 4 类 × 6 结局：普通、fused、mutation detach、新 default，分别覆盖成功、第二页晚冲突、取消、foreign owner、move、
owner 析构。另有 54 行 transition oracle、4 行 fused budget，以及真实 restore 缺失 default 的 4 BPP × 首次 root 拒绝/直接成功。
失败候选只有 prepared 无 transferred；成功新增两页时完整 transfer，history index 与 record index 同时由生产查询验证。

`publicationAdditionRecords*` 是逻辑 record 数，不是 allocator、字节或延迟。hash capacity 不增长有断言，但没有 allocator hook；
准备会短持局部 shard gate，取消可能留下非语义 capacity。PageStore descriptor、completion、外层 owner 析构/postwork 仍开放。
没有 benchmark、TSAN、原位 permit、完整短发布或 M/K/X/E 资格结论；结构和性能资格均为 false。
