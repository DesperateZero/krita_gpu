# Complete CPU payload initialization（2026-09-21）

对应 [67 §25](../../67_br1_target_structure_reconstruction_20260920.md)：真实 packed 整页输入同步初始化独立 TileData，
在注册前复制完成，省 default-fill 与 source COW；部分/default preserve 和普通 discard 的语义不变。
同段覆盖复用 pending；没有 raw 未初始化 guard、长期 caller-memory alias 或原位 permit。

## 证据与运行

- `initial-build`：CPU/Vulkan consumer 初次完整构建。
- `checked-build/checked-*`：补 factory 地址范围检查，并将验证失败测试放到实际 seal 边界后重新构建；focused 72/52/21 passed。
- `final-*`：以上最后生产/测试源码的完整矩阵。构建完成才测试；完整套件、选定 paint-device 和 3 组各 20 次重复分别记账。
  **15 套 1241 passed、选定 9 passed、60 次重复全过，76 个测试进程**；CpuMutation 424，最终无 FAIL/SAFE ASSERT/QFATAL。

Qt totals 包含 init/cleanup；重复不相加为完整套件 totals。两个 benchmark consumer 重建但不运行新性能采样。
验证脚本冻结源码、运行库、测试日志与文档身份，不修改 §24 或更早证据。

```sh
node docs/vulkan_gpu_design/evidence/br1_full_payload_20260921/verify-checkpoint.mjs
```

## 范围与限制

48 行 owner 矩阵：BPP 1/4/8/16 × default/resident/removed × direct/fallback × commit/cancel；覆盖 padding、末行最小长度、
调用后输入改变、真实 swap/reload、相同 generation、删除后覆盖与旧 View。14 行非法 buffer/地址分别测试 owner 和 store factory，
另测锁外准备与 capture/独立提交、abort/close 拒绝、分配/binding 拒绝及 seal validation 失败。cold alias 覆盖不复制旧 source。
生产 packed 矩阵核对 full page 零 default fill/零 source copy/一次 payload 初始化，partial/no-op、history/undo/失败及并发旧读保留。

`payloadInitializedPages/Bytes` 是新 backing 初始化，`pendingPayloadCopyBytes` 是 pending/fallback 显式复制，均不是硬件流量或 X。
整页 copy 移到 `packed_write_prepare/write_provider_prepare`，不是消失；`packed_write_copy` 仅是 partial 行复制。
普通 discard/fallback 初始化、swapped pending 完整覆盖的重载、原位许可、其他 producer、完整短发布和回收预算仍开放。
没有整体结构完成、CPU 主干管理不劣性、RAM/VRAM/UMA、TSAN 或最终性能资格声明。
