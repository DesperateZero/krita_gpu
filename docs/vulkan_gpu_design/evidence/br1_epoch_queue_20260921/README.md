# Epoch retirement links（2026-09-21）

对应 [67 §27](../../67_br1_target_structure_reconstruction_20260920.md)：root 与 terminal-transaction FIFO 链接内嵌于已有 registry record，
metadata 安装后的 epoch 排队不再扩展独立 deque/dedup set。identity 链接跨 hash relocation 保持有效；准入与预算语义不变。

## 构建和回归序列

- `checked-build`：移除 `<deque>` include 时遗漏独立树析构 batch 的依赖，编译失败；未运行旧二进制测试。
- `verified-build/verified-*`：恢复 include 后两套构建通过；新增队列测试的非法 extent-revision-only 样本被原契约拒绝，epoch 34 passed / 6 failed；retention 54、packed 52 passed。
- `final-build/final-focus-*`：测试改为真实 extent 变化，生产校验不变；两套构建及 focused 40/54/52 passed。
- `final-*`：最终源码的完整 15 套、选定 paint-device，以及 3 组各 20 次重复。完整套件与重复单独记账，Qt totals 含 init/cleanup。

最终 **15 套 1311 passed、选定 9 passed、60 次重复全过，共 76 个测试进程**；Reference 267，其余套件与 §26 相同。
最终无 FAIL/SAFE ASSERT/QFATAL；构建/链接和测试没有并发。

```sh
node docs/vulkan_gpu_design/evidence/br1_epoch_queue_20260921/verify-checkpoint.mjs
```

## 覆盖和限制

新增六行：1/33/513 epochs × root/transaction 先后收集。覆盖 hash 增长和 reserved-slot erase、重复事件去重、事务 FIFO、
零/小/批量预算、candidate 拒绝/取消、current 与 protected root 检查出队、最后保护释放后重新入队及空 head/tail 再利用。
§26 的准入/释放竞争、物理读者安全、真实退休积压进度及 packed 生产矩阵继续完整运行。

“无额外排队分配”仅指 root/terminal transaction 的链接动作；record 固定字段、registry 准备、metadata/history/default 插入、
completion、owner 后处理、worker 调度、实际树和事务析构仍有独立成本，不能外推整次 commit 或 E 无分配。
两个 benchmark consumers 重建但不采样；没有 owner 原位 permit、完整短发布、总回收预算、TSAN、全局无锁或 M/K/X/E 资格声明。
旧 D11/D12 `/tmp` runtime 缺失，完整历史重验仍为 unavailable；独立核验 sealed artifacts/现存 frozen inputs，不以新 binary 替代过去。
