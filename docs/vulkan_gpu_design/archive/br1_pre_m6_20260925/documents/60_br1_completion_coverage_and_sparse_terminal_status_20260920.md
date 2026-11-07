> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D6：完成覆盖压缩、终态差异与性能反证（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

本轮落实 52/P5 与 59 的累计 completion 记录研究。**当前实现采用“已逐项完成的覆盖范围 + 稀疏失败/取消状态”，
不是只记录最大已完成 ticket，也不是移除完成校验。** 原件、三版候选、脚手架和复算入口见
[D6 证据](../../../evidence/br1_d6_20260920/README.md)。这是分支内切片，不是主干管理不劣性或 BR1-PERF 结清。

## 1. 代码与安全契约

- `KisCompletionRegistry` 不再为每个 pending/succeeded ticket 永久保留一个 QHash entry。`nextValue` 定义已分配区间；
  未被证明完成的值仍为 Pending。显式完成后才加入连续 terminal prefix 或不相邻的完成区间。
- 完成覆盖可跨不同终态合并，但 Failed/Cancelled 另以 exact value 存储；只有**已证明 terminal 且没有非成功记录**
  才返回 Succeeded。补上一个 pending gap 时只能吸收已经逐项完成的相邻区间；大 host ticket 完成不推导小 ticket 完成。
- 全部状态仍在原 registry mutex 内更新；最近一次 completion 的值/状态缓存也在该锁下，旧值不可变。没有新增 CAS
  状态机，没有声称 PageStore reader 已免全局锁。registry/source/domain/value identity 和重复 complete 拒绝保持。
- 新增冷路径 `sourceStatistics()`，报告 allocated/pending/terminal 的逻辑 ticket 数与实际存储记录数。记录数包括
  inline terminal prefix（非空时计1）、完成区间和非成功条目；**不是分配次数、字节或 RSS**。统计不在操作循环内。
- 修复原接口接受非法枚举终态的漏洞，仅允许 Succeeded/Failed/Cancelled，`KisVerifiedCompletion::isValid()` 同步收紧。
  该修正及统计 API 在 before/全部 after 中相同，布局对照不把它们算作压缩收益。

保留已分配 ticket 的精确终态查询，没有 ticket 过期或隐式撤销。存储为 `O(完成区间数 + 非成功数)`，不是所有状态序列
常量空间；大量长期 pending 缺口与失败/取消仍须独立预算。provider `consumedOperations`、root/history 与 retire 队列
未在本轮优化，不把 completion 的缩减称为全系统有界回收。

## 2. 两次反证改变了实现

| 候选 | 观察 | 处理 |
|---|---|---|
| 相邻同状态终态区间 `after` | success 的长桶耗时约降至12.5%，但交替成功/失败耗时变为2.807倍 | 保留64次配对原件；补单调尾部完成/查询，不接受只报成功桶 |
| 尾部快路径 `after-tail` | 交替桶仍约1.011倍；全进程峰值 RSS 约543 MiB，对照约368–371 MiB | 记录实际空间退化；不把树节点计数当节省字节，重新分离完成覆盖与终态状态 |
| 完成覆盖 + 稀疏状态 `after-sparse`（当前） | 四个长桶耗时均降低；交替桶记录降为约一半，RSS 诊断亦下降 | 采用当前布局，继续完整管线测量；未解除其他 P5 缺口 |

首轮4,194,304次的 after success 仅92.324 ms，触发既定100 ms计时下限；原件保留，双方同步翻倍到8,388,608次后重新
跑完整矩阵。没有删除不利结果或降低门槛。完整过程见 evidence 中 `measurement-decision.md`。

## 3. 当前 registry 切片结果

同一 before 测试 executable，交替装载 ABI 兼容的 before/after-sparse image library；冻结源码/库 hash、实际 loader、
相同编译 profile。四桶各8对独立进程，单线程单 source，固定8,388,608个 allocate→complete→status 操作；无逐事件时钟。
下表是固定工作量墙钟/完成量的**摊销成本**，不是 P50/P95 或完整生命周期延迟。统计、正确性检查、析构在区间外。

| 分布 | before ns/op | 当前 ns/op | 当前/before时间比（探索性95%区间） | before记录 → 当前记录 |
|---|---:|---:|---|---:|
| 连续成功 | 177.43 | 18.22 | 0.1030（0.1002–0.1044） | 8,388,608 → 1 |
| 首个ticket保持pending，其后成功 | 190.34 | 17.91 | 0.0941（0.0930–0.0964） | 8,388,609 → 1 |
| 每1024次一次失败 | 176.27 | 18.15 | 0.1032（0.1013–0.1048） | 8,388,608 → 8,193 |
| 交替成功/失败 | 176.74 | 74.87 | 0.4201（0.4170–0.4319） | 8,388,608 → 4,194,305 |

比值为 pair 比中位数，不是两列中位数相除；按进程 pair bootstrap，seed606137、20000 resamples，未冻结正式 M 容差。
永久 pending 没有被补成成功，失败终态也没有丢弃。稀疏状态结构、最近完成缓存和完成覆盖共同构成当前候选，不能将全部
收益分配给某一单行代码。此处是 registry 组件的长历史状态，不是 tiles3 管理 M 的完整替代品。

补充两对相同操作数的 `/usr/bin/time -l` 诊断，包含进程 setup、检查、registry 析构和 allocator：连续成功 before峰值
349.77/362.66 MiB，当前23.27/23.14 MiB；交替终态 before357.80/350.50 MiB，当前205.11/204.58 MiB。各自实际装载库
均核验。只有两对，且是整个进程峰值，不给 per-record bytes 或普遍内存不劣性资格；也不是 PageStore/provider 的完整 drain。

## 4. 回到真实 tiles3 操作

使用59的同源 fixture，在 before/当前两库间做5桶各8对、独立200 ms完成吞吐。预备 source alias归操作级 E，cached guard
归管理生命周期；setup/像素校验在计时外。仍是H=0、单线程、固定端点，未重跑新的 upstream 资格或尾分位。

| fixture N/K/BPP | before ops/s | 当前 ops/s | 当前/before吞吐比（探索性95%区间） |
|---|---:|---:|---|
| cached guard 1024/16/4 | 4,579,481 | 4,505,751 | 0.9888（0.9592–1.0255），未确认变化 |
| prebuilt-source alias 1024/16/4 | 10,809 | 11,106 | 1.0274（1.0210–1.0327） |
| real write 4096/1/4 | 90,452 | 94,854 | 1.0467（1.0041–1.0867） |
| real write 1024/16/4 | 9,997 | 10,556 | 1.0552（1.0323–1.0797） |
| real write 64/1/16 | 93,680 | 95,480 | 1.0287（1.0025–1.0496） |

真实写吞吐只改善约2.9%–5.5%，没有随成功主导组件长桶的约90%降耗而同比改善。该结果校准了归因：**累计记账是实际问题，
但在所测200ms写窗口里，其压缩没有消除主干差距。** 两种实验的累计状态规模不同，不能据此给registry在全部产品负载的
固定占比；不把组件成本比乘到59的历史主干比值，也不从吞吐倒数反算延迟/子阶段时间。
尾部区间候选也做过5桶80次对照，原件保留；与当前区间重叠的差异不单独解释为再次加速。

## 5. 验证、未结清项与下一主线

新增 registry 测试覆盖非法终态/foreign registry、永久 pending gap、左右合并、混合终态、重复完成拒绝、固定随机乱序
对照 oracle、四线程共享 source、10万次成功和10万个 pending 的记录计数。当前 registry **11 passed**、Foundation
**24 passed**、Reference **42 passed**、完整 tiled-manager **88 passed**、共享 fixture **34 passed**、Vulkan foundation
contracts **13 passed**，静态架构检查通过（Qt totals含init/cleanup）。这是相关回归，不是全部产品/长压或真实GPU性能资格。

| 偏差/缺测存根 | 当前结论与后续要求 |
|---|---|
| D6-status-fragmentation | 初版2.807倍时间、尾部版约1.47倍RSS已由当前布局在所测桶修正；全部原件保留，不声称所有异步分布已通过 |
| D6-component-vs-pipeline | 组件长桶约90%降耗只对应真写吞吐约2.9%–5.5%改善；不能继续按 registry 微基准收益排序整条 CPU 管线 |
| D6-pending-fragmentation | 大量分散且长期不完成的 pending、随机历史查询、异步并发尾分位/内存仍待测；完成区间与非成功记录没有全局常量空间承诺 |
| D6-replay-and-drain | provider 防重放 QSet 未改，真实写的同累计操作数长桶、root/history/后台回收预算仍未完成；固定-work 主干配对不能因本组件通过就自动放行 |

下一主线仍是 P2/P3/P5 的正式 captured view/stack guard、mutation session、owner-issued原位permit与短发布，结合53–59的
版本化证据重新测量访问/准备/发布/提交/回收。版本可见性、abort、reader/history以及唯一authority不放宽。同步完成的CPU
路径应减少通用 request/proof/ticket 的实际调用次数，而不是仅靠更快的 registry 保留逐页完整通用协议。
GPU/UMA仍为NotMeasured，BR1-PERF不结清，不开放BR2产品接线。
