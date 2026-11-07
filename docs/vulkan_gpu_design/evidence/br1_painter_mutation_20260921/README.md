# BR1 painter 生产 const 读取契约检查点

本目录记录实际 `KisPainter::bitBltImpl` source/mask 接通公开 const accessor 契约的修复与正确性回归。
目录名不代表 painter 已迁移为操作级 mutation；目标端仍走 legacy writable accessor。
设计、相位口径及剩余写侧归属问题见 [67 §19](../../67_br1_target_structure_reconstruction_20260920.md#19-2026-09-21真实-painter-sourcemask-消费者的-const-契约贯通)。

## 保留的失败

`baseline-*`：修复前原有 testSimpleBlt 触发 SIGSEGV（地址 0x1）。source/mask 从 const 接口强转具体 mutable
accessor 后调用 rawData 得到空指针。修复调用方，不恢复只读 guard 的可写权限。

`focused-*`：加入 72 个产品场景后的首次测试为 67 passed / 8 failed，失败均为带 mask 的 F32 exact-byte 比较。
`float-diagnostic-*` 保留相同 8 个失败并记录最大绝对误差：2.98023e-08 或 5.96046e-08。
最终只对 F32 使用有限性检查及逐分量 float epsilon × max(1, abs(expected)) 误差界；整数仍逐字节一致。
oracle 是连续 buffer 上同一色彩合成；测试真实产品的 tile 分块调用，未修改生产色彩 kernel。

## 覆盖与重放

新增 64 个格式/场景/old-current/mask 组合，在实际第二块之前更新 source/default 和 mask；断言旧 View 输出与新 accessor 输出。
另有 4 个持有外部 writer 的 current/old 兼容场景及 4 个重叠 self-copy。不是多 owner 联合快照、并发吞吐或 TSAN 证明。

`run-checkpoint.mjs build <新标签>` 构建 CPU 相关测试（含 painter）、selection-tools 和 Vulkan contracts。
所有构建结束后执行 `focused <新标签>` 或 `full <新标签>`；full 含 15 套完整测试、7 个 paint-device 选定槽，
再执行 11 组各 20 次重复。标签和日志不可覆盖。instrumented/并发运行的 wall time 不是性能样本。

## 最终正确性检查点

`final-build-*` 的 CPU/Vulkan 相关目标和 selection-tools 全部完成重建后，才启动 `final-*`。
15 套完整回归 **905 passed**、paint-device 选定槽 **9 passed**；11 组各 20 次、共 **220 次重复**全部通过，
合计 **236 个测试进程**。完整 painter 套件 90 项含新增 72 个场景；Qt totals 包含 init/cleanup。
所有最终日志无 FAIL!/SAFE ASSERT/QFATAL，不将重复进程数量混算进完整套件 totals。

`verify-checkpoint.mjs --capture` 一次性绑定当前 source、binary、插件、日志及设计文档 hashes，并核验 inventory、
负样本、加载路径、架构/whitespace 和文档链接；之后不带参数复验。旧 manifest 不覆盖，后续修改会使 live 检查点失效。
D11/D12 仅 archive-only 验证，不重跑或改写原性能证据。修复前的失败不归入最终通过资格。

## 未授予的资格

painter 目标写的操作级段归属、同页首写复用和失败原子性仍需迁移；不能只套 batch 便吞并已有 live tile lease。
owner-issued 原位 permit、全部 brush/dab 入口、owner 安装/单页历史成本及回收总预算仍开放。
相位是 inclusive 业务区间；painter_composite 不是纯 K，bitblt_finish 不是最终 drain。
GPU/UMA 及显存/RAM 配对 M/K/X/E 未测，未宣告结构完成或性能通过。
