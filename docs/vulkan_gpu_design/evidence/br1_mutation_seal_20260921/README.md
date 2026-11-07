# BR1 mutation seal：锁外准备与紧凑 detach delta

本目录是正确性检查点，不是性能资格或核心重构整体完成声明。设计与口径见 [67 §18](../../67_br1_target_structure_reconstruction_20260920.md#18-2026-09-21mutation-seal-的锁外准备与紧凑语义安装)。

连续 transaction/PageKey claims 保护私有 metadata/proof 准备，正常准备与私有容器收尾不持全局 owner。
mutation detach 只携带 exact identity，在全部页面短 claim/语义复验成功后，只改变当前 publication/preparedBy，保留最新读者、pin 和 last-use。
root publication/restore 的严格 snapshot revision 检查不变，不能推广为通用陈旧快照合并。

## 保留的失败

第一版锁外完整 snapshot 候选设置最多 8 次重试。`focused-*` 165 passed，`full-*` 的 14 套完整测试 799 passed，
但 200 次重复中 4 次失败：`full-concurrent-{3,5,14}.log` 的 capturedOverlayConcurrentSegments，
`full-semantic-13.log` 的 concurrentMixedSemanticCapture。合法 capture/release 使 snapshot 陈旧，重试耗尽导致正常操作失败。
`full-results.json` 保留全部 215 个进程，其中 211 成功、4 失败；它不是最终通过证据。
修复采用紧凑语义 delta，未放宽测试断言，也未用增加重试次数规避问题。

中间的 `verified-*` 标签同样不是最终通过证据：oracle 结果字段正确，但测试清理直接调用裸 AcknowledgeLastUse，
被 completion 能力门正确拒绝。1 个完整 Reference 套件及 20 个 metadata 重复进程各失败 8 个组合。
随后测试改用 registry `complete/verifyTerminal` 与 `acknowledgeLastUse`，生产能力门未放宽；这 21 份失败记录保留。

## 重放

`run-checkpoint.mjs build <新标签>` 顺序构建 CPU 相关测试/selection-tools 和 Vulkan contracts。
构建全部结束后，使用 `focused <新标签>` 或 `full <新标签>`；full 是 14 套完整测试、7 个 paint-device 选定槽，
再执行 10 组各 20 次重复。脚本拒绝覆盖既有标签/日志。运行的 wall time 含并发和诊断干扰，不是性能样本。

新增 41 个 CPU 场景和 16 个状态机 oracle 场景；另更新 capability 整批拒绝测试，以第二页真实 writer 冲突验证原子性，
合法 reader 变化应保留而非拒绝。CPU pin、logical retention、async last-use 各自验证；不授予 TSAN、wait-free 或硬延迟资格。

## 最终检查点

`final-build-*`：CPU 全部相关目标、selection-tools 插件及 Vulkan contracts 均完成重建后，才启动 `final-*`。
最终 14 套完整测试 **815 passed**，paint-device 选定测试 **9 passed**；10 组各 20 次，共 **200 次重复**全部通过，
合计 **215 个测试进程**。Qt totals 包含 init/cleanup；最终日志无 FAIL!/SAFE ASSERT/QFATAL。
CPU mutation 314、Reference 99，其余 12 套合计 402；新增场景不是将 200 次进程重放混算进完整套件 totals。

`verify-checkpoint.mjs --capture` 创建一次性 live manifest；随后不带参数核验源码/构建/插件/日志/文档 hashes、
测试 inventory、运行时加载路径、架构检查、diff whitespace 与本地链接。D11/D12 只做 archive-only 检查，不重跑或改写性能样本。
旧检查点和性能原件不覆盖，后续源码变更会使本 live manifest 失效。

原位 permit、完整生产入口迁移、
owner 输入/安装及单页历史成本、回收总预算与最终 M/K/X/E/GPU/UMA 性能验收仍开放。
