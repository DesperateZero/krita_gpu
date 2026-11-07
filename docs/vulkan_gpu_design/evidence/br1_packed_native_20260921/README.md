# Packed native production checkpoint（2026-09-21）

本轮对应 [67 §24](../../67_br1_target_structure_reconstruction_20260920.md)：真实 `writeBytes` 直接 native guard，
完整范围保留之后一次捕获比较 View、no-op、full discard/partial preserve，和像素操作共用 private cancel/事务生命周期。
DataManager 锁缩到入口与派生索引刷新；不是原位 permit、完整无锁架构或最终性能资格。

## 证据阶段

- `initial-build/initial-*`：首版原生入口，focused 45/47/13 passed。
- `lock-check-build/lock-check-*`：新增真实 DataManager 读者回归，packed **45 passed / 1 failed**，只失败于写体持有 DataManager 锁。
  该反例保留，不计入最终通过。另两组 47/13 passed。
- `unlocked-build/unlocked-*`：收窄 DataManager 锁后 46/47/13 passed。
- `final-*`：上述生产实现首轮完整回归 15 套 **1173 passed**、paint-device 选定 9 passed、60 次重复；是补充最后两条等待/no-op行之前的测试源。
- `verified-build/verified-*`：追加等待后比较的发布/取消边界后，重新构建全部 CPU/Vulkan consumer 并重跑完整矩阵。
  15 套 1175 passed、选定 9 passed、60 次重复通过。
- `confirmed-build/confirmed-*`：最终复查消除共用生命周期中重复构造目标 QSet，重建后再跑相同完整矩阵。
  **15 套 1175 passed、选定 9 passed、60 次重复全部通过，76 个测试进程**；tiled manager 333，最终无 FAIL/SAFE ASSERT/QFATAL。
  这是当前源码的权威正确性结果；`final-manifest.json` 冻结源码/二进制/文档/证据 hashes。

Qt totals 含 init/cleanup；repeat 不加入完整套件总数。构建结束才测试，两个 benchmark consumer 也重建，未执行性能采样。
首次交互构建还修正了新增测试误用 `KisDataManager::clear(QRect,…)` 的编译错误（该派生接口需要五参数）；未用旧二进制测试它。

## 验证

```sh
node docs/vulkan_gpu_design/evidence/br1_packed_native_20260921/verify-checkpoint.mjs
```

首次冻结用 `--capture`；禁止覆盖已有清单/日志。verifier 检查 32 条 packed 工作矩阵、6 条竞争/等待/no-op 行、后页失败/借用/并发旧读，
完整套件与 3 组各 20 次重复、negative、构建顺序、动态库/插件加载路径、架构、whitespace、文档链接及 hash。
D11/D12 仅 archive-only；不重写 §23 或更早的证据，不把旧 live checkpoint 当作当前源码结果。

## 必须保留的限制

整页覆盖零源复制，但 discard 分配仍默认初始化。部分修改仍 COW；段可失败、历史/共享匿名事务仍可 abort。
物理 claim 尚未由 owner-issued permit 消费。业务体不走 compatibility wrapper，但完成后仍有派生 wrapper/cache 更新；live borrower 显式 fallback。
body 新分段包含完整 mutation 生命周期和 commit，finish 包括重新取 DataManager 锁与索引刷新；不能混用旧 timing 定义。
无吞吐、延迟、CPU 主干管理等价、UMA/VRAM、TSAN 或整体结构完成声明；剩余生产入口、短发布与回收总预算继续开放。
