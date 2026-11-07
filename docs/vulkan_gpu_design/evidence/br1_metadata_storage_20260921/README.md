# Prepared metadata storage（2026-09-21）

对应 [67 §28](../../67_br1_target_structure_reconstruction_20260920.md#28-2026-09-21metadata-候选持有发布所需存储)：
普通 publication/mutation 为已有版本转 Historical 预构造有序索引 node；bounded fused path 预构造完整 record/index set。
安装在全部页 claim 与动态事实复验成功后才 transfer/swap，失败候选不改变 live index。

## 构建与回归

- `checked-build`：新增测试被重复合入，编译器报告重复声明/定义；未运行失败构建后的旧测试 binary。
- `verified-build-build-br0-cpu.log`：中断运行留下的非权威日志，没有配套结果文件，不用于通过声明。
- `fixed-build`：整理为单一更严格矩阵后，CPU 与 Vulkan 两套构建均通过。
- `fixed-focus`：索引/候选 98、真实 publication 74、packed 生产路径 52 passed。
- `fixed-full`：最终源码的 15 套完整回归、选定 paint-device，以及三组各 20 次重复。

最终 **15 套 1329 passed、选定 9 passed、60 次重复全过，共 76 个测试进程**；Reference 285、CpuMutation 464。
Qt totals 含 init/cleanup；完整套件与重复单独记账，无 FAIL/SAFE ASSERT/QFATAL，构建/链接与测试未并发。

```sh
node docs/vulkan_gpu_design/evidence/br1_metadata_storage_20260921/verify-checkpoint.mjs
```

## 覆盖与限制

新增 18 行覆盖普通 commit、fused discard、mutation detach 各自的成功、第二页晚冲突、取消、foreign owner、move 后成功、
owner 析构后拒绝。安装前 live 状态不变；成功时 history node/replacement record 数完整转移，失败时安装计数为零；生产 history
slice 也验证索引，而非只比较导出 snapshot。既有 54 行 publication oracle、fused budget、晚 reader/writer 保护、metadata-before-root、
真实 commit/restore 的 H=0/7/63 工作量，以及 packed/reader/swap/低内存/Vulkan 回归继续运行。

这些指标是逻辑 record 工作量，不是 allocator、字节或耗时。本切片没有消除新 default record/hash 与 PageStore descriptor 插入，
也没有证明旧 fused set 析构已离开外层 owner gate。没有 benchmark、TSAN、完整短发布、原位 permit 或 M/K/X/E 资格结论；
`structural_completion=false`、`performance_qualification=false`。D11/D12 原 `/tmp` runtime 仍缺失，历史完整重验标记 unavailable，
只独立核验 sealed artifacts 与仍存在的 frozen inputs，不以当前 binary 替代。
