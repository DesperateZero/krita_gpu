> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D7：捕获读视图、一致性修正与接入成本反证（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

本轮推进 52/P2 的 operation-held view，并补 P5 的寿命/回收边界。**已完成 identity/surface 捕获与只读 facade 接线，
尚未完成 native pixel guard。** 单独查表更快不代表整条读管线更快：稳定 head 下，通用单页 read session 完成吞吐比
D6 下降约 23%–25%；该反证必须继续优化，不能用新增内部 retention 记账作为管理开销豁免。BR1-PERF 不结清。
原件、冻结代码及复算入口见 [D7 证据](../../../evidence/br1_d7_20260920/README.md)。

## 1. 实装范围与安全边界

- `KisCapturedReadView` 是 move-only、owner-issued 的 immutable root capability；在一次 owner 临界区内选定并 retain
  current/retained/transaction-base root。ExactVersion 限定 exact key/version；拒绝失效 token、跨 owner 使用和 mutable overlay。
- scope 内 `resolvePageVersion/resolveSurfaceState` 直接读 persistent root，不再进入 PageStore/epoch mutex，也不导出 owning manifest。
  capture/release 仍有 owner/epoch 锁及分配，完整成本保留；不宣称严格 lock-free 或整条像素路径免全局锁。
- `CpuAccessSession::beginRead`、random accessor、`readRect/copyRect` 的来源页面与 format/default revision 绑定同一捕获视图。
  `TransactionOverlay` 继续使用显式 live-overlay 语义，不伪装成 immutable view；写侧/原位 permit 未在本轮落实。
- `acquireReadInView` 仍转换为合法 retained selector，进入现有 request/lease/provider 协议；每个实际读页仍产生 generic request。
  root retention 不等于 backing residency pin，更不等于 GPU/I/O last-use。未绕过 swap pin、provider 校验或安全释放。
- captured identity view 持有 private owner 生命周期，可晚于 public PageStore facade 销毁；CPU access session 仍要求 facade
  比 session 长寿。PageStore 保留单指针 ABI、不可复制/移动；新增冷统计单独返回，不扩大旧 `SessionStats` 布局。
- captured scope 释放只考察已登记的 deferred historical keys，不扫描所有 registered pages；没有 root 真正被移除时不重扫
  deferred history。generic lease release、last-use acknowledgement 保留各自 eligibility/GC 路径。

这不是完整的有界回收：`collectUnretainedRoots()` 仍检查 root/transaction 集合；最后一个旧 scope 可能同步处理大量 deferred
pages，reachability 也受 retained roots 数影响。当前 epoch owner 仍是 `KisImageEpochReferenceModel`，production owner/cursor、
page-local native pin、批量回收预算与高 H 压力尚未结清。

## 2. 两个可复现反例

| 反例 | 观察 | 修正/复验 |
|---|---|---|
| D6 read session 追逐 current head | 同一 fixture/executable 加载归档 D6 library：第一页为 `0x21`；中间 commit 后第二页变成 `0x45`，违背 operation immutable view | session 起点持有 root；新库同用例通过，另验证旧 default revision、accessor 和并发双页 commit |
| D7 首版短 scope 重扫旧 reader 的历史 | N=16、旧 root 保留，64 次当前 scope 释放使 GC 页访问从 48 增至 1072，即重复 1024 次无效检查 | 只有释放实际移除 root 时才尝试 deferred GC；N=16/256 下当前 scope、非最后一个旧 scope 释放均零新增访问，最后一个旧 scope 释放回收全部旧 payload |

前者 loader 日志验证了 D6 `libkritaimage` 身份，失败原件为 `d6-coherence-counterexample.log`；后者为
`history-release-counterexample.log`，最终通过见 `reference-final.log`。两者不是性能样本，不能混入吞吐统计。
旧 session 不满足捕获不变式，不是可回退的合格实现；下面 D6 性能对照仅限稳定 head、双方输出正确的诊断 workload。

## 3. 测量协议

共 **15 桶、每桶 8 对、240 次独立进程配对**，另有 6 次 loader 短检查。桶顺序轮换、两侧顺序交替；每次独立计时
至少 200 ms，统计到相同完成端点的操作数；不启用 phase profiler，不与构建/功能测试并发。环境继续为
Mac16,10 / 24 GiB / macOS 15.7.3、Qt 6.8、RelWithDebInfo、universal 构建/arm64 执行。

1. component：同一个新 binary/library 内，旧 retained-selector API 对新 captured API。lookup 排除双方 capture/release；
   scope 包含 capture/lookup/release，旧公共 `captureRetainedEpoch()` 的 owning manifest 导出和 full-scan release **包含在内**。
   这是 identity API 对照，不是“原 D6 session 已经做了这些工作”，更不是 upstream tile 对照。
2. integration：只用 D6 既有公开 API/ABI 的同一新 fixture，交替加载 D6/new library；稳定 head、1 BPP、CpuRam、单线程，
   K=1/16、N=16/256、H=0/1。session/accessor 包含 generic lease 和读值检查；rect 还包含实际像素拷贝及输出分配。
3. native：未改的 shared tiles3 fixture，D6/new library；检查已缓存 native guard、readBytes 与真实 scanline 写。
   这条 adapter 路径没有接上新的 captured pixel guard，不能用它的暖读结果授予新 facade 性能资格。

报告的区间是以进程 pair 为单位的探索性 95% bootstrap；没有预冻结 M 不劣性容差，不作正式 Pass。完成吞吐不能当单次
延迟，process CPU/完成量只是窗口平均成本。未测 P95/P99、完整 drain、宽格式新 facade 或 GPU/UMA；CPU-only 未交接的
UMA 零迁移项为 `NotApplicable`，不是 UMA Pass。源码/ABI/library/driver/protocol 身份随 manifest 保存。

## 4. Identity 对照：收益存在，但边界很窄

以下均为 candidate / baseline **完成吞吐比**，大更好：

| 桶 | 配对中位比 | 探索区间 | 解释 |
|---|---:|---:|---|
| lookup N16 K1 H0 | 1.812 | 1.749–1.855 | 仅 retained identity lookup |
| lookup N256 K64 H0 | 2.490 | 2.454–2.503 | 同一 scope 中 64 个 identity lookup |
| scope N16 K1 H0 | 4.154 | 3.998–4.375 | 包含捕获/释放，旧 API 有 manifest/全扫 |
| scope N256 K1 H0 | 51.297 | 50.791–52.346 | 去掉 N 级冗余工作的定向收益，不是像素加速 |
| scope N256 K64 H0 | 29.122 | 28.367–29.671 | 同上，64 页 identity |
| scope N256 K1 H1 | 80.995 | 77.317–81.963 | 长旧 reader 仍保留；当前短 scope 不触发无效历史扫描 |

captured 各桶计时区间 generic read request 为零；lookup 没有 capture，scope 每操作恰一次 capture；当前 scope release
GC 页访问为零。旧 scope 的 GC 页访问为 completed scopes × N。N=16/256 的结果支持消除该 N 级扫描，不能据此宣称
所有 H/N/K、root reclamation 或 native pixel 路径均已具备完整复杂度/预算证明。

## 5. 完整接入：明确慢化，不能被 component 收益抵消

| 稳定 head 桶 | D7 / D6 完成吞吐比 | 探索区间 |
|---|---:|---:|
| session N16 K1 H0 | 0.752 | 0.747–0.755 |
| session N256 K1 H0 | 0.756 | 0.743–0.761 |
| session N256 K16 H0 | 0.962 | 0.946–0.977 |
| session N256 K1 H1 | 0.766 | 0.752–0.784 |
| accessor N256 K16 H0 | 0.972 | 0.951–0.987 |
| rect N256 K16 H0 | 0.969 | 0.952–0.999 |

N16/K1 的 process CPU/操作中位值为 1,919→2,550 ns，N256/K1 为 2,033→2,691 ns；这是实测窗口平均 CPU 成本，
不是从吞吐倒数推导的延迟。每侧每桶均验证 `readRequests == completedOperations × K`，证明通用逐页协议没有被消除。
capture 加在原通用像素路径外，单页成本未充分摊薄；这与完整管线加速目标不一致，不能把 identity 的最高 81× 作为本轮结论。
上述结构事实支持继续消除双层协议，但没有精确子阶段计时证明约 0.6 µs 全属于某个 allocator/锁，不作过度归因。

原生 adapter 三桶的吞吐比为 guard **1.004**（1.003–1.009）、read **1.001**（0.995–1.008）、write **0.991**
（0.985–0.997）。暖读无材料级收益；真实写有约 0.9% 的小幅反向偏移，保留为待定位项，不自动解释为 GC 记账或噪声。
它们不抵消新 facade 的明显慢化，也不替代新的 upstream 配对或正式不劣性。

## 6. 偏差存根与下一实施约束

| 编号 | 预期/实测差异 | 状态与后续动作 |
|---|---|---|
| D7-view-consistency | 旧 session 未真正持有 immutable view | 已修正，D6 反例与新回归保留；不得性能回退到追逐 head |
| D7-history-rescan | 首版 deferred keys 仍被每个短 scope 重扫 | 已修正此条件；高 H 与最终旧 scope 的有界 drain 仍未证明 |
| D7-generic-read-regression | identity 优化没有转化成整体读加速，单页吞吐下降约 23%–25% | **未关闭**；native pixel guard、scope 内 cached binding/pin 与 generic fallback 接通后重测 |
| D7-native-write-offset | 本切片不以改进写管线为目标，却出现约 0.9% 反向偏移 | **未关闭**；后续对齐代码/计数布局、同固定 work 与重复 paired，不能删掉这批样本 |

下一步必须落到真正像素管线，而不是继续把新 captured 名称套在旧 lease 外：

1. 在 immutable view/owner 内建立 exact version → stable CPU backing binding 的合法路径，持有 provider/owner 寿命。
   不能缓存 `QHash` value 地址或未经 pin 的 `KisTileData*`；版本、ProviderEpoch、allocation generation 和布局必须匹配。
2. move-only native read guard 做 page-local first/last pin 与 swap barrier；驻留命中不创建 generic request/active-lease map entry。
   view retention 仅保护逻辑版本，不能替代 replica retirement/eviction、writer 和 backing pin 的原子安全协调。
3. provider 的 generic/native 访问和 retire 必须共享同一局部 ownership gate；避免 metadata 已丢弃而 provider 因隐藏 pin
   拒绝 retire 后无重试。root 发布前 binding 完整可读；retire 拒绝须保持可恢复状态或有界重试记录，不能静默泄漏。
4. 接入 session/accessor 与 tiles3 traversal 的同一 captured root、hot pin set、current/before fused resolve；真正缺页、未完成
   producer 或访问交接才进入通用路径。capture/release 成本仍测，不得为省约 0.6 µs 删除 old-root capture gate。
5. 重跑本轮全部三组、BPP4/8/16/partial read/retained history/并发，补固定-work、尾延迟及 N/K/H/drain；native 写仍按
   session/first-write permit 主线推进。安全前置与结构计数通过后，最终回到 39 的同义 M 和产品 E，而非止于新 fixture。

## 7. 回归与未完成项

最终 CPU build：Reference **59 passed**（包含 12 个 component 短检查行）、新 read fixture **9 passed**、Foundation
**24 passed**、tiled-manager **88 passed**、原生 shared fixture **34 passed**；Vulkan foundation contracts **13 passed**，
静态 architecture guard 通过。日志总数含 init/cleanup；功能回归墙钟不参与性能分析。未重跑完整 GUI 产品/长压。

本轮推进了 P2 的 captured identity 与一致性、P5 的特定回收放大消除；P2 native pixel guard、P3 mutation/permit、P4 production
owner、P5 有界 retire 和 P1/P6 完整性能资格仍未完成。保持 BR1-PERF 进行中，BR2 production 与 GPU/UMA 产品接线不开放。
