> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D2-B：prepared metadata 发布与偏差校准（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

本切片沿 55 的分段证据消除重复 transition，并修正 metadata/root 发布顺序。
**这是现有 owner gate 内的同步批处理切片，不是 P4/P5 或 BR1-PERF 结清。**

本文保留 D2-B 当时的源码/测量边界。2026-09-21 的事务 claim、锁外准备及发布复验进展见
[67](67_br1_target_structure_reconstruction_20260920.md)；不以新实现改写下列旧性能结果。
版本、原件与复算见 [实验目录](../../../evidence/br1_d2_batch_20260920/README.md)；55 的数据继续只描述 D2-A。
本文“current/最终”冻结在 D2-B；后续长区间交替、操作级抽样和完整写路径研究见
[57](57_br1_sampled_write_pipeline_and_immutable_directory_20260920.md)，不回填本文短桶数据。

## 1. 管线实际变化

```text
before: proof/provider validation
        → removal/default 解析 + transition 预演
        → write transition 预演 → epoch prepare → root 构造并发布
        → 重做 write/removal/default transition → metadata apply → GC/retire

current: proof/provider validation
         → removal/default 语义解析（不提前补写 live default metadata）
         → 一次生成候选状态 → epoch prepare → root 构造并完成冲突校验
         → 全批逐页 revision 复验/claim → 安装候选 metadata/descriptor
         → root 发布 → GC/retire
```

- `KisPageMetadataCoordinator` 生成不可伪造、move-only、一次消费的私有 publication capability，绑定 coordinator
  lifetime identity、transaction/base、minimum epoch、逐页 revision 和精确候选状态。仅 PageStore 与契约测试可调用。
- prepare 在一个 shard 内捕获已验证 owner state/revision，锁外运行 shared transition。install 先验证并 claim 全批页面；
  任一失败则释放已取得的 claim，**不安装任何候选状态**。成功后每页安装与 release 使用同一次 shard lock，绝不同时
  长持全部 shard mutex。失败和成功都会消费 capability；不允许用旧 token 重试。
- 所有 coordinator page-state 写入推进 revision；reader acquire/release、last-use ack、writer/abort、materialization
  reserve/bind/queue/drain 均纳入冲突处理。claim 期间状态修改拒绝，completion drain 保留事件待后续处理。
  未绑定的 materialization reservation 也禁止 fused idle retirement；不能只看 snapshot 中尚未出现的 activeOperation。
- root model 新增 **私有** `commitWithMetadata` owner seam：冲突检查、root 构造与校验全部通过后，才能安装 metadata；
  安装失败不发布 root、不完成 transaction。安装成功后没有可恢复的协议拒绝点，再切换 root。不是开放的业务 callback，
  不允许重入 epoch model、provider 调用或等待。
- root allocation 失败可烧掉 epoch identity，所以 candidate 使用严格更新的 minimum epoch，安装时采用实际分配的 epoch；
  不能假设 `current+1` 永远等于实际 commit epoch。只有此批次允许的 publication transitions 使用该单一 epoch tag。
- proof seal、producer completion、authority/provider epoch/allocation/layout 验证保留；PageStore owner gate 从这些验证到
  安装期间一直持有，没有锁外异步 prepare 或可外传的 capability。provider/transaction/root-retention 的失效约束仍依赖
  该 gate；**逐页 revision 不能代替 provider lifecycle claim 或 root-retention pin**。

物理 provider retirement 仍在 root 发布后、PageStore 锁外执行；旧 retained/read/last-use 版本不被 fused retirement 清除。
claim 仅防止候选 snapshot 覆盖后来的状态，不提供独立的多页可见性；公开读取仍通过 immutable root 和现有 owner gate。
`restoreRetainedEpochImpl()` 尚未迁移到此批处理 seam，仍受旧 owner-gated 预演/发布路径保护，不泛化为“全部发布入口已改完”。

## 2. 第一次实现的反证与修正

初版保留在 `after-*` 原件/源码归档，不覆盖掉不理想的结果：

- plain stress 五次 median **16.037 → 16.201 s**，区间重叠，没有确认整体收益。
- H=0 alias 在部分固定桶慢约 **6%–8%**；N4096/K1 为 **18.114 → 19.498 μs/操作**。
- 新 `commit_transition_preflight` 已含 write + default/removal 全部候选构造，不能直接与旧 write-only 同名阶段相减。
  历史 D2-A 的 default/removal + preflight + metadata apply 合计约 **2.275 s worker-wall**；初版约 **2.113 s**。
  工作量略不同、profile 明显扰动且非新鲜配对，这只是方向诊断，不能据此声称 E 降低了 0.162 s。

发现新增成本后做两项可核查修正，而不是只缩短 publish 计时区间：

1. prepare 的输入只能来自 coordinator 已验证且按 revision 捕获的 owner state，复用既有 `applyKnownValid()` 内部边界，
   避免在原本 trusted/fused 路径上新增整页 invariant 分配扫描；所有 transition-local generation/writer/lease/pin/last-use
   guards 不变。外来 register state 仍完整校验，debug 构建保留前后 invariant assert，测试把四类 publication 与完整
   reference `apply()` 作 32 种状态组合对照。不是面向调用者的 skip-validation flag。
2. 全批 claim 成功之后，每页最后一次安装就可在同锁内 release，后续步骤不再覆写该页；移除独立的第三遍 lock/hash pass。
   没有取消全批复验，也没有将准备、回收或 release 从总操作成本中隐藏。

## 3. 最终证据与资格

最终 `refined-*`：Reference **38**、Foundation **24**、完整 tiled-manager **88** passed（含 init/cleanup）。新增五个
Reference 用例覆盖 foreign owner/transaction/base、move/重复消费、晚到 reader/last-use/materialization/abort、整批拒绝、
旧 root 不变、失败后 epoch 跳号、4 reader × 1000 次并发 acquire/release，以及四类 transition × 8 种状态的完整 reference
对照。既有功能用例继续覆盖 retained/default/restore/宽格式 bytes；没有因此证明 native lock-free reader 或设备 reset 并发协议。

### 3.1 无 profiler 的完整操作区间

同 fixture，before/初版/refined 各五次，依次运行而非交替/同主干配对。固定桶 256 操作；短桶未达正式微基准最小时长，
保持 diagnostic 状态。全 52 桶 range/stddev/工作量/release 耗时见 `analysis.json`，不只展示收益桶。

| stress 版本 | Qt elapsed 五次（s） | median（s） |
|---|---|---:|
| before D2-A | 15.934 / 15.922 / 16.037 / 16.203 / 16.307 | 16.037 |
| 初版 batch | 15.781 / 16.008 / 16.306 / 16.262 / 16.201 | 16.201 |
| refined batch | 14.803 / 15.118 / 15.059 / 15.205 / 15.408 | 15.118 |

refined/before 中位耗时比 **0.9427**，约降低 **5.7%**，本组范围不重叠；支持“重复控制工作减少有整体诊断收益”，
但没有消除顺序漂移、调度/page-work 差异，**不是同主干不劣性通过，也不是各桶普遍加速**。

| 操作 | N/K/H/BPP | before（μs/op） | refined（μs/op） | 耗时比 |
|---|---|---:|---:|---:|
| alias | 64/1/0/4 | 15.172 | 16.112 | 1.062 |
| alias | 4096/1/0/4 | 18.114 | 19.183 | 1.059 |
| alias | 4096/16/0/4 | 77.924 | 75.885 | 0.974 |
| alias retained | 4096/16/4/4 | 99.297 | 86.129 | 0.867 |
| real scanline | 64/1/0/4 | 18.440 | 20.054 | 1.087 |
| real scanline | 4096/1/0/4 | 20.915 | 23.018 | 1.101 |
| real scanline | 4096/16/0/4 | 248.319 | 260.033 | 1.047 |
| real retained | 4096/16/4/4 | 270.054 | 271.379 | 1.005 |
| real wide | 1024/16/4/8 | 244.717 | 241.114 | 0.985 |
| real wide | 1024/16/4/16 | 267.589 | 259.898 | 0.971 |

[固定工作量图](../../../evidence/br1_d2_batch_20260920/fixed-work-comparison.svg) 使用独立 before/refined 两条柱，避免叠加隐藏慢化。
**小 K/H=0、尤其真实部分页写仍慢约 6%–10%，没有结清。** 原 stress 主要 alias/removal，不能用其下降覆盖真实写反证。

### 3.2 分段结果与扰动

refined profile 的 Qt 时长 **17.474 s**，比其 plain median 高约 **15.6%**，仍仅定位、不作 Pass/Fail。以下为目标 manager
跨 worker 累计 wall/CPU；短阶段 CPU 大于 wall 是计时端点成本，不是负等待。

| 阶段 | wall（s） | thread CPU（s） |
|---|---:|---:|
| commit proof/provider validation | 0.559 | 0.560 |
| default/removal 解析 | 0.202 | 0.204 |
| write/default/removal candidate prepare | 0.651 | 0.652 |
| epoch prepare | 0.314 | 0.315 |
| root 构造/冲突检查 | 0.386 | 0.387 |
| revision/claim/install + descriptor | 0.335 | 0.337 |
| root 最终发布/return | 0.007 | 0.009 |
| history collection | 1.048 | 1.048 |
| provider retirement + tail | 1.188 | 1.186 |

图：[commit](../../../evidence/br1_d2_batch_20260920/refined-commit_phases.svg)、
[adoption](../../../evidence/br1_d2_batch_20260920/refined-adoption_phases.svg)。default/removal + candidate + install 合计约
**1.188 s worker-wall**，初版为 2.113 s，历史 D2-A 为 2.275 s；这验证了该组合阶段工作减少的方向，但不把其差值机械
归因给进程 E。adoption entry/provider 仍约 2.321/2.375 s wall，而 CPU 约 0.637/0.980 s；provider 区间含 owner
锁重取，不是纯 provider kernel 时间。

目标 manager：commits **24,105**、adoptions **1,500,672**、read requests **1,049,673**、default materializations **0**、
generic write requests **0**；最终 pages/versions/replicas 为 **512/512/64**，不是累计/峰值/全进程统计。candidate/install
覆盖 **2,760,832 page transitions**，其中 removal **1,261,568**；固定 fixture 的显式事务起点 manifest export 仍为 0。

### 3.3 新偏差存根：总 stress 下降不等于小 K/真实写改善

`D2-B-small-K` 保留为未解决项：候选 capability/transitions/去重容器等增加按 transaction 的固定成本，可能使小 K 无法
摊销；目前只有代码结构支持这一**假设**，不能直接把全部 6%–10% 归给分配。refined 的 real N4096/K1/H0 plain 区间
为 **5.709–5.966 ms/256 op**，before 为 **5.081–5.436 ms**，仍需更长、交替版本的同 workload 复验。

相同桶的初版/refined profile 中 candidate prepare 为约 **1.076→0.604 μs/op**，但完整 plain real 操作没有随之改善。
因此下一研究必须同时覆盖 operation 外壳、临时分配、pin/adoption、清理与 CPU 热/调度漂移；不得再只看 commit 内部子段。
新增计时需优先有界抽样/批次校准，并将桶延长到标准规定时长，而不是继续叠加每页时钟。优先减少确证的固定分配/多余
lookup，保留一套 capability/claim 语义，不以不安全的 K=1 旁路取消发布协议。

## 4. 尚未结清与后续研究

这不是与主干完全同构的 CPU 管线：native tile backing + PageStore/epoch/metadata 控制层仍混合执行；per-page
`QVector` snapshot/reference owner、全局 PageStore mutex、provider adoption/proof 成本、历史回收与适配器扫描仍在。
本轮先解决重复工作和发布安全，尚未取得独立 M 管理不劣性、isolated K、产品 E/tail 或 GPU/UMA 性能资格。

后续不能凭“批处理已存在”跳过以下工作：

1. 分离 root 构造、provider/transaction/retention 动态复验与短 sequencer；native reader 不能依赖当前 owner mutex。
   长期退出该 gate 前，必须给所有可变事实等价的 pin/claim 协议；不能只把 prepare 搬到锁外。
2. 优化候选 production record/delta 布局，避免长期以 reference snapshot/vector 作为热路径布局；以 M 分项计数和
   固定 K/N/H 工作量检验是否真的减少分配、lookup、transition 与回收工作。
3. 继续实测 adoption/provider/proof、history collect/retire 与 adapter delta，确认是否为下一主导项；更新粒度之前先控制
   scope 扰动。cold identical、真实写 COW/permit、native guard、production root/cursor 仍是 52 的原始出口。
4. GPU/UMA 沿用同域 M、resident K、跨域 X 与产品 E 分离口径；本 CPU 切片不证明 VRAM/RAM K 等价，也不证明 UMA
   同步成本为零。GPU 劣势桶仍必须以成熟 CPU 产品路径作回退和成本上限参照。
