# Epoch admission 与独立预算回收（2026-09-21）

对应 [67 §26](../../67_br1_target_structure_reconstruction_20260920.md)：root 的逻辑接入资格与物理注册/待销毁状态解耦，
只遍历 current 与 distinct 受保护 roots，worker 同轮推进 root/finished-transaction 及历史像素的各自预算。
不再允许凭未销毁 root 的 epoch ID 复活历史，也不再等待整个 root 队列清空才能开始像素退休。

## 证据序列

- `checked-build`：测试误用 private `captureRetainedEpochRoot` 及 deleted lease assignment，编译失败；没有用旧 binary 接着测试。
- `verified-build/focused-*`：修正测试 API 使用后的构建与首轮准入/物理保护回归，34/38/52 passed。
- `final-build`：加入真实退休积压矩阵后构建，没有基于此中间版本测试。
- `confirmed-build/confirmed-*`：补齐测试早退 cleanup 寿命，focused 的 epoch/packed 通过；retention **38 passed / 16 failed**。
  16 行均因 `reclaimedWithRootBacklog` 不成立，揭示 worker 仍先清空 root 记账才处理像素历史的旧屏障，负例原样保留。
- `progress-build/progress-*`：删除生产队列屏障，两套构建后 focused **34/54/52 passed**，未放宽上述进度断言。
- `final-*`：最终源码的 **15 套 1305 passed、选定 paint-device 9 passed、60 次重复全过，76 个测试进程**。
  Reference 261、CpuMutation 464；Qt totals 含 init/cleanup，重复不混入完整套件总数。

最终无 FAIL/SAFE ASSERT/QFATAL；所有测试均在 CPU/Vulkan 构建结束后执行。两个 benchmark consumers 已重建但未做性能采样。
历史阶段日志保留，最终 manifest 固定最后源码/运行库/文档身份，不把中间日志冒充当前 binary 的结果。

D11/D12 的原始 `/tmp` runtime 已不在当前环境，完整 `--archive-only` 重验为 **unavailable**，不是 pass。
本 checkpoint 独立校验仓库内 sealed artifacts 与仍存在的 frozen inputs，保存原失败输出与缺失路径；不修改历史脚本/数据，
不以当前 build 重建或替代过去的 identity。这不影响本轮 `_build` / `_build-br0-cpu` 的独立正确性结果；历史性能的完整重验能力仍缺失。

```sh
node docs/vulkan_gpu_design/evidence/br1_epoch_admission_20260921/verify-checkpoint.mjs
```

## 覆盖和限制

24 行新 reference：8 行 release/commit/restore 保护组合，4 行 H=0/7/127/1023 加重复 snapshot/transaction-root 去重，
12 行最终 release/abort 与 retain/begin 的明确先后和竞争（每行 32 次）；物理 collector 尚未运行时验证不可复活。
40 行新 owner：BPP=1/4/8/16 × 六种保护，及 × H=65/257 × 保留/释放最旧 View。
root 队列仍有积压时观察真实 provider retirement；每次 refresh 只查询 1/2 个合法 root，合法长历史另验必要 R_live。
native guard 保留自己的 View；generic lease 只保护 exact replica，不授权旧 epoch，最后保护消失后两者均正确回收。
完整 suite 和重复组覆盖候选拒绝/restore、history sweep 失效/续扫、真实 packed/no-op/history/失败/并发及 loader 路径。

`historyReachabilityRootsVisited` 是 worker refresh 的 distinct root 查询数，不是 token/registry/tree-node 数或时间。
此改动收紧原位许可的必要前提，但当前 root 仍可被新捕获。owner permit、capture fence、恢复/不可失败提交、其余 producer、
完整短发布和回收总时间/内存预算仍未结清。没有整体结构完成、TSAN、全局无锁、M/K/X/E、CPU 主干不劣性或 RAM/VRAM/UMA 资格声明。
