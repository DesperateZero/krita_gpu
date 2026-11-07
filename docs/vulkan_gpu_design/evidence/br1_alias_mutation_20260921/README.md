# Private alias and production region mutation checkpoint

范围见 [67 §17](../../67_br1_target_structure_reconstruction_20260920.md#17-2026-09-21私有-alias-source-与生产-fillcopy-贯通)。
本轮接通 immutable source capability、alias/像素/删除混合私有段、生产 fill/clear 与 PageStore → PageStore copy，
并按实际 changed keys 更新 compatibility index。不是核心重构整体结清，也不是性能资格。

最终 `verified-*` 的 695 个测试进程全部通过：14 套完整回归 **758 passed**、paint-device 选定 **9 passed**、
17 组各 40 次共 **680 次重放**；无 FAIL/SAFE ASSERT/QFATAL。CPU/Vulkan 目标及 selection-tools 重建后执行，
当前运行库/插件路径、架构和 diff whitespace 检查通过。D11/D12 封存证据只做 archive-only 验证，不修改旧性能原件。

## 正确性范围

- alias/write/remove 的 8 种序列 × 4 BPP × seal/cancel/proof failure：96 个 Qt 场景。
- 多页 alias/native 混合的 provider/第一或第二 proof 失败 × 4 BPP：12 个。
- source mint identity、exact guard、非驻留暂存/seal、独立 COW、discard 不复制输入：4 个。
- private backing replacement 的 13 个状态机正/负例，包含旧 View/read lease/pin/last-use/writer 和 allocation token 复用。
- 生产部分像素 → alias/removal → 后页 writer 冲突，owned/history × fill/copy × 4 BPP：32 个。
- copy current/before × exact/rough × 4 BPP，复制中途更新源内容/default，全部读取原 View：16 个。
- raw source 的 live intent/已暴露指针 × history/current/before × exact/rough 兼容分流：16 个；原 low-memory hangingTilesTest 不放宽。
- 已有 invalid-alias batch 失败、重复 uniform no-op、无 generic request 的索引刷新、undo/redo 和并发回归保持。

新增 189 个 Qt 场景；Qt totals 含 init/cleanup，内部子循环不另计。

## 开发失败记录

`production-cpu-test.log` 的 6 个失败来自关闭 native 能力的 fixture 未关闭新能力依赖；
`production-tiled-test.log` 的 7 个失败包含独立写 View 计数口径及整片索引刷新新增 generic read request。
已改为实际 changed keys 原生刷新，并将被测读操作与注入写操作的 View 分开断言。
`index-*` 保留漏扣最后一个空 planar 调用断言中的写 View；数据一致性检查没有放宽。

`contracts-build.log` 保留测试调用错误 clear 重载的编译拒绝。
`contracts-kis_tiled_data_manager_test.log`、`copy-failure-*.log` 保留 SIGABRT 及 LLDB 回溯：
测试把栈 source 隐式转成 shared pointer，临时对象释放栈内存；改为显式调用不转移所有权的 base API，未改产品所有权协议。
`rechecked-*` 保留 16 个未触发注入的失败：diagnostic observer 仅由 timer.next 调用，非 timer 构造；
复制现有明确的 prepare/page/finish 分段，固定 View 回归仍要求确实发生 source 更新，不能无注入就宣告通过。

首轮 `checkpoint-*` 的 655 个测试进程中，654 个通过，但 low-memory 的 hangingTilesTest 失败，因此整轮不具通过资格。
原因是源 raw tile 仍有 write intent 时，新固定 View 复制读 sealed 版本，改变了既有 live backing 共享语义。
断言提前返回又留下原测试借出的锁，故记录失败后仅终止该挂起测试进程（SIGTERM），没有终止或修改产品会话。
修复按源范围已有 wrapper 的局部 intent 分流，普通 immutable copy 与旧 live 观察分开验证；history old-source 不被误分流。
这项兼容路径仍是未迁移边界，不构成捕获可变 producer 为 immutable source 的许可。

## 重放

```sh
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_alias_mutation_20260921/run-checkpoint.mjs verified
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_alias_mutation_20260921/verify-checkpoint.mjs
```

构建及链接全部结束后运行；runner 拒绝覆盖既有结果，每个测试进程 180 秒上限。14 套完整测试、paint-device 选定槽、17 组各 40 次重放。
源码、运行库、插件、日志和文档 live hash 在全部通过后才 capture；未来编辑使该 checkpoint 失效，不改写历史 manifest。
时长含并发、诊断及故障注入，不是性能测量；无 TSAN、GPU/UMA、CPU 主干不劣性或最终 M/K/X/E 资格。
