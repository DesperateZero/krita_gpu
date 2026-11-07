> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D8：原生驻留读接通与写侧成本反证（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

本轮把 D7 的 captured view 接到真实像素 native guard，消除新 CPU facade 暖驻留读的逐页 generic request/lease。
**读路径收益已测得，但原生真实写吞吐反向下降约 2.3%–4.8%。** 两项结论分别保留，不能相互抵消；BR1-PERF 不结清。
原始结果、冻结代码/运行库及复算入口见 [D8 证据](../../../evidence/br1_d8_20260920/README.md)。

## 1. 实装路径与安全边界

```text
beginRead：捕获一次 immutable root / surface metadata
  → scope cache miss：exact version → metadata shard 的 stable binding candidate
  → 首次 provider record 解析（锁外调用 provider；candidate 内 once）
  → allocation-local gate → first-reader residency/swap pin → CPU span
  → scope cache 命中：复用已持有 guard，不重复请求
finish：归还 native/generic pin → 释放 captured root → 按既有规则 GC
```

- `KisCpuReadGuard` move-only、内联持有 protected scope、stable allocation record 与只读 pointer/stride；无独立 guard heap node。
  root/owner 寿命与物理 pin 分别保留，guard 可晚于 public PageStore facade 销毁；CPU session 仍要求 facade 比 session 长寿。
- `KisCpuResidentBinding` 是 CPU/tiles3 provider 持有的稳定 allocation record，不缓存会因 `QHash` 移动失效的 value 地址。
  native/generic read/write、transfer 与 retire 共用局部 gate；最后一个 reader 才解除 physical pin，writer 与 retirement 拒绝活跃读者。
- tiles3 `tryBlockSwapping()` 只尝试 resident pin：锁忙和确已 swap-out 分开，不在 native try 内执行 swap-in。
  provider 销毁先 revoke 新访问，已有 pin 的 payload 仍保留到最后一次 release；成功 close 清除 candidate 缓存。
- captured root 保护当前/历史 exact version 不被现有历史 GC 丢弃，guard 先 unpin 再 release root；close 的 outstanding
  retention 检查涵盖 native guard。未增加“generic lease map 为空即可退休”的捷径。
- `KisCpuResidentReadStatus` 区分 Ready、InvalidView/InvalidIdentity、VirtualDefault、BindingUnavailable、UnsupportedProvider、
  Busy、NonResident、Retired；可选输出不增加全局热计数器。无效身份不是物理 fault，unsupported/busy 不是跨域迁移。
- CPU session/read accessor/`readRect` 与 `copyRect` 来源优先使用 native guard；mutable TransactionOverlay 保留 generic 路径。
  scope 的 read record 改为连续存储与 key→index 缓存，消除逐页 shared wrapper；vector/hash 的实际分配仍存在。

这是 CPU facade 的切片，不是所有 tiles3 traversal 已迁移。原生 `KisTile` 暖缓存及 legacy bridge 仍有自己的访问路径；
新 guard 不等于正式 mutation session/原位 permit。多个 allocation handle 可以 alias 同一 TileData；record-local 读者数
不能证明 payload 独占。未来 replica eviction/异步 handoff 必须在撤销 metadata 前接入等价寿命协议，不能沿用忽略 retire
失败的假设。本轮 CPU 历史 GC 依赖 retained root 排除这些 native version，不授予尚未接线的 GPU/UMA 回收资格。

免锁结论限定为已捕获 scope 内不取 PageStore owner mutex、不建 generic request/lease；metadata shard、page-local gate、
swap barrier 仍有锁，首次 provider lookup/once 也有成本。capture/release 仍持 owner/epoch gate，不能称严格 lock-free。
当前候选/record 在 allocation/adoption/commit 等处建立，读缓存维护还进入 generic read/retire；这是下面写侧反证的研究对象。

## 2. 正确性与旧测量断言

专门 native-read suite **24 passed**（含 init/cleanup），覆盖：

- CPU 与 tiles3 provider，1/4/8/16 BPP 布局、exact selector 错 key、历史像素/版本不变、move 与 facade 销毁；
- generic/native 多 reader 共存，writer/transfer target/retire 冲突，pending last-use，错误 ProviderEpoch 与 retired record 拒绝；
- 256 页 scope cache 扩容后旧 span 仍有效；暖读 generic request/lease 为零，manifest export 为零；native root 阻止提前 close；
- 并发多页 commit/read、并发 pin/retire、未提交写 abort 不改变 native before-image、provider revoke 不提前释放已有 pin；
- 真实 tiles3 swap-out 被 native pin 阻止；释放后 swap-out 成功；native try 报 NonResident 且不创建请求；generic swap-in 后恢复 native；
- 没有 native 能力的 provider 明确报 UnsupportedProvider，并由原 generic 路径读到正确 bytes；virtual default 过渡路径单列。

首次旧 read fixture 有 6 项失败：它把“每页必须创建 generic request”写进断言，新路径实际为零。除初始日志外，另以
**归档 D7 fixture executable + 冻结 D8 library** 重现 3 passed/6 failed，loader 身份已验证；原件为
`generic-counter-contract-counterexample.log/json`。不是像素失败，也不是可丢弃的性能样本。
新共用 fixture 为每侧显式冻结 expected requests/page：D7=1、D8=0，继续严格逐桶断言，不改为接受任意请求数。

## 3. 冻结测量协议

**23 桶 × 8 对 = 184 对、368 次独立进程计时运行**，另 4 次 loader 检查；每次完成窗口至少 200 ms，桶顺序轮换、两侧顺序交替，
无 profiler，不与构建/功能测试并行。环境与 D7 相同：Mac16,10 / 24 GiB / macOS 15.7.3、Qt 6.8、RelWithDebInfo，
universal 构建、arm64 执行。69 个源码文件另存快照，源码/运行库共 317 项 hash 绑定本切片。

- integration 18 桶：同一新 executable 只调用 D7 已有 API，交替装载 D7/D8 library。包括原 6 个 1 BPP CPU 桶，
  另加 CPU/tiles3 × 4/8/16 BPP 的单页 session 与 16 页 rect。payload/binding 已暖；每次 session 的 capture/cache/release 在计时内。
- session/accessor 每页触达一个实际字节，属于读管理生命周期，不能当作全页带宽；rect 包含完整矩形拷贝及输出 buffer 分配。
- native 5 桶：未修改的同源 tiles3 fixture，测 cached guard、readBytes 及三个真实 scanline write 桶，用来发现间接回归。
  两侧均是 PageStore 分支库，本轮没有重新比较 upstream。
- process CPU/完成量是窗口平均成本，不是单次延迟。区间为以独立进程 pair 重采样的探索性 95% bootstrap；未预冻结
  不劣性容差，不能据此授予 M/E Pass。history release/close 另计，不等同于全部后台 drain。

首次 binding self、锁 wait/hold、固定-work、单次 P95/P99、高 H/并发性能、产品 replay 与完整 drain 仍为 NotMeasured。
CPU-only 未发生 GPU 交接，UMA 零迁移项为 NotApplicable；GPU/UMA 产品性能仍为 NotMeasured。

## 4. 读收益：完整 scope 内的通用逐页工作确已消除

以下为 **D8 / D7 完成吞吐比**，大更好：

| CPU provider / 1 BPP 桶 | 配对中位比 | 探索区间 |
|---|---:|---:|
| session N16 K1 H0 | 3.170 | 3.127–3.180 |
| session N256 K1 H0 | 3.296 | 3.228–3.382 |
| session N256 K16 H0 | 12.178 | 11.895–12.298 |
| session N256 K1 H1 | 3.481 | 3.380–3.525 |
| accessor N256 K16 H0 | 11.567 | 11.429–11.903 |
| rect N256 K16 H0 | 2.193 | 2.069–2.291 |

N256/K1 的窗口 CPU/操作中位值为 **2,679 → 818 ns**；N256/K16 为 **31,336 → 2,585 ns**。计时区间的 D7 request
数为 completed operations × K，D8 为零。源码和结构计数支持“删除逐页通用协议/包装分配”的解释，但不能将全部差额
精确分给某一 mutex、allocator 或 cache line；没有分段 self 证据，不用吞吐倒数合成阶段延迟。

| provider | 4 BPP 单页 / rect | 8 BPP 单页 / rect | 16 BPP 单页 / rect |
|---|---:|---:|---:|
| CPU | 3.326 / 1.985 | 3.359 / 1.681 | 3.315 / 1.575 |
| tiles3 | 3.362 / 1.917 | 3.308 / 1.756 | 3.367 / 1.487 |

宽格式单页仍主要测 guard 生命周期；rect 含更多实际字节，收益较小与工作构成一致，但不由这组比值推导精确 memcpy 占比。
完整各桶区间、原始 pair 与 setup/close 时间保留在 `integration-analysis.json`。不得把 D8/D7 与 D7/D6 或 D5/upstream
比值相乘生成新的主干结论。D7 已记录的接入慢化有了对应的原生读修正及本切片正向证据，正式主干 M/E 资格仍未取得。

## 5. 反证：D8 中未使用新读 API 的真实写仍出现退化

| 原生 tiles3 控制桶 | D8 / D7 完成吞吐比 | 探索区间 |
|---|---:|---:|
| cached guard N64 K1 4 BPP | 0.997 | 0.995–1.013 |
| read N1024 K16 4 BPP | 0.997 | 0.987–0.999 |
| write N64 K1 4 BPP | 0.952 | 0.932–0.959 |
| write N64 K1 16 BPP | 0.977 | 0.951–0.998 |
| write N4096 K1 4 BPP | 0.968 | 0.944–0.980 |

最小写桶窗口 CPU/操作中位值约 **9,415 → 9,927 ns**。三个写桶配对均出现反向偏移；cached guard 未确认变化，原生 read
约 0.3% 的小幅负偏移也保留。不能将它们称为“噪声已排除”或“与新读提升相比可忽略”，更不能用新 read facade 的倍率抵消。

源码复核的可检验假设：本版为每个 allocation 建立独立 resident record，为每个提交/adoption 的版本预建 candidate；
generic read 也安装 candidate，retire 移除它。只写或只走原生 tiles3 暖缓存的 workload 也承担这些分配/索引/同步工作。
这解释了应优先研究哪条路径，**尚未证明约 512 ns 全部来自这些新增项**。

下一候选因果对照为“按首次 native read 建立 binding cache”，须另行冻结协议，保留 record 的 read/write/transfer/retire 保护；
比较 eager 与 lazy 的完整读/真实写，并另测首次 binding。不能仅将 setup 挪出窗口就宣布总成本消失，也不能删除安全 gate
来恢复写性能。若仍超预算，再评估 provider allocation 与稳定 record 的布局合并、generic 重复同步和真实写 session 粒度。

## 6. 偏差存根与结清边界

| 编号 | 观察 | 状态/后续证据 |
|---|---|---|
| D8-old-request-contract | 旧 fixture 强制 generic request 与 native 目标相反 | 已改为两侧显式路径断言；旧 executable 反例保留 |
| D8-eager-binding-write-regression | 读 facade 加速，但真实写慢约 2.3%–4.8% | 未关闭；eager/lazy 缓存与共享保护成本需独立因果对照 |
| D8-native-read-offset | 未迁移的原生 read 控制约 0.3% 负偏移 | 未关闭；不可用组件收益或未冻结容差宣告不劣性 |
| D8-cold-and-reclaim | 暖命中消除请求不覆盖首次 binding、最后旧 root、高 H/后台回收 | 未取得性能资格；补 cold/self/drain 与预算，不声称全 scope 零分配或全链 lock-free |

CPU build 与回归：ResidentRead **24**、ReadBaseline **21**、Reference **59**、Foundation **24**、tiled-manager **88**、
native shared fixture **34** passed；Vulkan foundation contracts **13** passed，静态 architecture guard 通过。Qt totals 含
init/cleanup，Reference 含 component 短检查；这些回归墙钟不作为性能结果。未重跑完整 GUI 产品、长压或 sanitizer。

P2 新 facade 的 native 像素读已落地；共享 default、legacy traversal/current-before fused scope、P3 mutation/permit、
P4 production owner/layout、P5 完整退休预算与正式 M/K/E 门禁仍未结清。不能把本切片称为整条 CPU 管线同构主干，
也不能因只读收益跳过真实写反证。BR1-PERF 继续，BR2 production 与 GPU/UMA 产品入口保持关闭。
