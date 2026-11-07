# BR1 metadata 精确版本记录

本轮将生产 metadata 从整页 owning snapshot 改为 header、稳定版本记录和 exact/physical-slot 索引，
把 native 首写、私有 seal/cancel、capture token 与 proof 的输入收窄到实际涉及版本。
白名单局部转换仍运行同一状态机；完整 commit/restore、通用控制和 GC 成本不因此消失。
实现与归因边界见 [67 §21](../../67_br1_target_structure_reconstruction_20260920.md#21-2026-09-21生产-metadata-的精确版本记录与局部更新)。

## 阶段记录

- `initial-*`：布局初版保留原套件，Reference 99、CpuMutation 314 通过；不是最终检查点。
- `indexed-build/indexed-*`：新增局部差分、并发与长历史用例后，Reference 151、CpuMutation 326 通过。
- `invariant-negative-build/invariant-negative-*`：完整 reference 不变量与既有生产乐观事务行为的矛盾被实际复现。
  Reference 152 passed / 1 failed，失败发生于第二个独立 Prepared 版本 PublishWrite；CpuMutation 326 passed。
  负例不删除，也不忽略原失败。修正为活动 writer 唯一、Prepared 归属按版本隔离，foreign read 与 root 冲突仍受保护。
- `final-build/final-*`：CPU/Vulkan 构建结束后，15 套完整测试 **1017 passed**、paint-device 选定 **9 passed**，
  14 组各 20 次、**280 次重复**全部通过，合计 **296 个测试进程**。最终无 FAIL/SAFE ASSERT/QFATAL。

`run-checkpoint.mjs` 拒绝覆盖旧标签。所有构建完成后才运行测试，不把链接中的库用于回归。
full 运行 15 套完整测试、paint-device 7 个选定槽及 14 组各 20 次重复。
完整 Reference 为 153、CpuMutation 为 326、painter 99、tiled manager 291；共新增 66 个场景。
Qt totals 含 init/cleanup，重复进程不混算完整套件总数。

`verify-checkpoint.mjs --capture` 一次性记录 source/binary/doc 和本轮日志 hashes，之后不带参数复核；拒绝覆盖旧 manifest。
除全部测试清单外，还检查负例、12 个真实 native 工作量输出、构建先于测试、painter/iterator 实际库与插件、
architecture guard、whitespace、本地文档链接和 D11/D12 archive-only 证据。旧检查点不覆盖。
structural_completion=false，performance_qualification=false。

## 结构证据与限制

真实 native 单页首写+重访+seal 在 1/4/8/16 BPP × 0/7/63 个 retained overlay 下，
局部输入为 3 条、安装为 4 条，exact snapshot 输入为 3/5/5，前台整页 snapshot 导出为零。
其旧 View、abort 后可读性、generation、close/provider 内存归零均有断言。
独立 reference exact lookup 覆盖 0/255/4095 历史记录，局部转换按完整状态机逐字段/效果比较。
physical-slot 见证覆盖旧历史冲突、不同 allocation generation/domain 及安全回收后的 slot 重用。

新结构计数在 shard 内累加，冷查询汇总。全 snapshot 工作另计，background 是总数子集，不能重复相加。
前台局部工作量稳定不等于 root/GC/E 已与 H 无关；单版本 replica/lease/token 列表和索引分配仍有成本。
Qt correctness 耗时、observer 注入及并发回归不是性能数据。未运行 TSAN，没有原位 permit 或 GPU/UMA 性能资格。
原位 permit、其他 producer/legacy 边界、完整短发布/历史布局及总回收预算仍未结清。
