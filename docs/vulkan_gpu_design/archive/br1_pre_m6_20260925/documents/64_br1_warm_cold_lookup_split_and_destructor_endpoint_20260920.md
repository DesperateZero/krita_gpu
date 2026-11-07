> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D10：冷热查询分离与析构端点校准（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

D10 将暖 binding 查询与冷副本发现分离。相对 D9，16 页 held-view guard 完成吞吐提高约 **5%–7%**，完整
session/accessor 提高约 **4%**；但直接对 D8，部分宽格式读仍有负偏移，首次 16 页 read scope 仍慢约 **63%–73%**。
这是局部冗余工作减少的证据，不是 CPU 主干等价、整条管线同构或按需缓存已经最优的证明。BR1-PERF 继续。

本报告校准已有实现和测量结果，不启动新的生产修改。原件及复算入口见 [D10 证据](../../../evidence/br1_d10_20260920/README.md)。
[63 的 D9](63_br1_demand_read_binding_and_cold_warm_tradeoff_20260920.md) 与更早报告保留各自版本、端点和反证，不反向改写。

## 1. 实现事实与安全边界

生产处理变量限定在 `KisPageMetadataCoordinator` 和 `KisCapturedReadView` 的冷热查询：

- `cpuReadBinding(version)` 只在原有短 shard lock 内查暖缓存，不再为命中路径构造/重置完整 `coldReplica` 输出。
- 缺缓存后才调用 `Q_NEVER_INLINE discoverCpuReadBinding()`：冷 `cpuReadReplica()` 查 exact Published/Historical version，
  优先 ready CPU authority，否则要求唯一 ready CPU-readable replica；锁外取得 provider，再在安装时复验 exact replica。
- 冷 miss 因此比 D9 **多一次 metadata shard 查询/加锁**；不能称冷热两侧都已零成本。这里是源码事实，不是锁 self 耗时测定。
- D9 的按需建缓存保留；写/adoption/default/generic read 不重新预建。provider stable record、generic/native
  read/write/transfer/retire gate、root retention、backing pin 和 last-use 不变，未修改公共布局或虚表。
- 暖像素 scope 内不取 PageStore owner gate，但仍有 shard/page/swap 局部同步；capture/release 的 gate 仍在完整操作中。
  这不是严格 lock-free，也不授予原位写 permit、future eviction 或异步 handoff 资格。

当前仍是 native TileData/pool/swap 复用加 PageStore 控制/epoch/adapter 管线；新 facade 的读切片不能代表未迁移的 legacy
traversal、真实写、提交、历史及回收都已经与主干同构。源码入口：
[metadata](../../../../../krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp)、
[captured view](../../../../../krita/libs/image/pagestore/KisPageStore.cpp)、
[共用读 fixture](../../../../../krita/libs/image/tests/KisPageStoreReadBaselineTest.cpp)。

## 2. 版本、构建与回归证据

环境为 Mac16,10 / 24 GiB / macOS 15.7.3、Qt 6.8、RelWithDebInfo `-O2 -g -DNDEBUG`，universal 构建/arm64 执行。
源码基点为 `f5fbbde618df6fb4e1068ace7381c339a70dd4c0` 加冻结 dirty patch/source；不能只凭 HEAD 复现候选。
identity 共 497 项：69 个当前源码、69 个冻结源码，以及 D7/D8/D9/D10 四套 runtime。

| 冻结角色 | 版本与目录 | 用途 |
|---|---|---|
| before | D9 `/tmp/br1-d9-runtime.IcwSzu` | 主因果对照 |
| reference | D8 `/tmp/br1-d8-runtime.DEnywg` | 直接检查是否恢复 eager 版表现 |
| original | D7 `/tmp/br1-d7-runtime.othEAo` | 仅旧 native fixture 控制；不是 upstream |
| after | D10 `/tmp/br1-d10-runtime.f0fE3p` | 候选 |

新读 fixture 仅适用于 **D8+ guard/view ABI**，不装载 D7。D7 只用独立的旧 `kis_tiles3_cpu_baseline_test`。
28 次 loader 检查验证实际装载库；未用多轮性能比值连乘生成“直接对照”。

最终回归：ResidentRead **28**、read fixture **41**、Reference **59**、Foundation **24**、tiled-manager **88**、
native baseline **34**、Vulkan contracts **13**，静态 architecture guard 通过；Qt totals 含 init/cleanup。
read fixture 新增 8 个 held-view guard 行；原冷首次读、并发/历史、安全 gate 回归保留。最终日志以 `final-*.log` 为准，
早期 `read-initial.log` 不替代最终端点修正后的回归。套件墙钟不是性能数据；未重跑 GUI/长压/sanitizer。

## 3. 冻结协议与计时结构

14 组共 **111 个配对桶 × 8 对 = 888 对、1,776 次计时运行**，另 28 次 loader 检查。独立进程、轮换桶顺序、
交替两侧先后；rate 窗口至少 200 ms，fixed-work 为 256 个 cycle、窗口至少 100 ms。性能循环不与构建、回归或 profiler 并发。
下列区间为进程 pair 的探索性 95% bootstrap（10,000 次重采样）；未预冻结正式不劣性容差，不授予 Pass。
表中吞吐比为 candidate/baseline，大更好；时间比小更好。pair 比值中位数不等于两侧中位数之比。

| 组 | 桶数 | 对照 | 端点/范围 |
|---|---:|---|---|
| integration / integration_reference | 各 18 | D9/D10、D8/D10 | 暖 session/accessor/rect，每操作 capture/cache/release 在内 |
| guard / guard_reference | 各 8 | D9/D10、D8/D10 | 预持 captured view，计时 pin/触达/unpin，capture/release 在外 |
| native / native_reference / native_original | 各 5 | D9/D10、D8/D10、D7/D10 | 未迁移的 native guard/read/三个真实 scanline 写控制 |
| cold / cold_reference | 各 12 | D9/D10、D8/D10 | N64 写/发布新 generation → 首读 K0/1/16 → release |
| cold_profile / cold_profile_reference | 各 4 | D9/D10、D8/D10 | 上述周期的 inclusive prepare/publish、first-read 区间 |
| cold_perturbation | 4 | D10 plain/profile | 单独校准分段时钟扰动 |
| cold_fixed / cold_fixed_reference | 各 4 | D9/D10、D8/D10 | 相同 256 cycle，补 configure 到最终容器析构 |

必须保留以下范围区别，不能机械相加为一条流水线：

| 观测 | 窗口实际包含什么 | 不证明什么 |
|---|---|---|
| held-view guard | 暖 root resolve/cache lookup、native pin、每页触达 1 byte、unpin | 完整 session M/E、全页 RAM 带宽或纯 mutex self |
| session/accessor | 每操作 capture、访问、cache 和 release；每页仅触达 1 byte | 实际全页像素吞吐 |
| rect | 完整输出 buffer 分配/清零、accessor 和像素 memcpy | 隔离 K、纯 M 或整个差额都是 binding 成本 |
| cold cycle | fill64/COW、发布、首次读及 release，双方包含计数/Qt 检查 | 纯管理、单次延迟或孤立 cold binding self |
| first-read profile | session 建立、首次 binding、访问及释放的 inclusive 区间 | 锁等待/持有或 allocator 的独立成本 |
| fixed lifecycle | configure/setup、相同 256 cycle、close、facade/provider 容器最终析构 | 全局 tiles3 pool/worker 完整 drain、长期资源有界 |

D9 的 `lifecycle_ns` 实际止于 close 返回；本轮共用 fixture 保留 `configure_to_close_ns`，另计 `destroy_ns`，
新的 `lifecycle_ns` 止于 `storeOwner.reset()` 完成，明确 endpoint 为 `Facade-and-provider-containers-destroyed`。
`lifecycle_process_cpu_ns` 在实际端点采集。两侧用同一新 fixture，不把 D9 旧日志补造为含析构结果。
固定工作量总时间不是持续吞吐或事件 P95/P99；rate-window 的 lifecycle/完成量也不是固定-work 延迟。

## 4. 暖路径：局部改善成立，全部恢复不成立

以下均为完成吞吐配对比［探索性 95% 区间］；完整 18+8 桶见对应 analysis JSON，不丢弃未列出的桶。

| 暖桶 | D10/D9 | 直接 D10/D8 |
|---|---:|---:|
| guard N256 K16，CPU 1 BPP | 1.057［1.014–1.069］ | 0.989［0.985–1.093］ |
| guard N256 K16，CPU 4 BPP | 1.065［1.036–1.077］ | 0.998［0.993–1.013］ |
| guard N256 K16，CPU 16 BPP | 1.054［1.023–1.065］ | 1.011［0.990–1.018］ |
| guard N256 K16，tiles3 4 BPP | 1.054［1.027–1.085］ | 0.995［0.982–1.042］ |
| guard N256 K16，tiles3 16 BPP | 1.067［1.050–1.074］ | 0.996［0.982–1.019］ |
| session N256 K16，CPU 1 BPP | 1.043［1.016–1.061］ | 1.018［0.978–1.035］ |
| accessor N256 K16，CPU 1 BPP | 1.038［1.026–1.051］ | 1.000［0.998–1.002］ |
| session N256 K1，tiles3 8 BPP | 1.005［0.998–1.012］ | 0.973［0.957–0.998］ |
| rect N256 K16，CPU 8 BPP | 1.049［0.943–1.084］ | 0.939［0.910–1.066］ |
| rect N256 K16，CPU 16 BPP | 1.023［0.993–1.107］ | 0.959［0.925–1.048］ |
| rect N256 K16，tiles3 8 BPP | 1.066［0.996–1.089］ | 0.963［0.928–1.008］ |
| rect N256 K16，tiles3 16 BPP | 1.036［0.947–1.088］ | 0.972［0.921–1.001］ |

结果支持“暖命中不应付冷 handle 初始化成本”的方向；但不能分配整个收益给某条指令、锁或 cache effect。
单页 guard 部分区间较宽；宽格式 rect 有约 2.8%–6.1% 负中位偏移，多数区间跨 1，而 tiles3 8 BPP 单页 session
区间略低于 1。负向结果全部保留，区间跨 1 不证明不劣性，也不能宣布宽格式全部恢复。

## 5. 真实写控制：没有因暖查询分离而解决写主线

| 原生桶 | D10/D9 吞吐比 | 直接 D10/D8 | 直接 D10/D7 |
|---|---:|---:|---:|
| guard N64 K1 4 BPP | 1.000［0.995–1.002］ | 1.001［0.996–1.004］ | 1.000［1.000–1.007］ |
| read N1024 K16 4 BPP | 0.999［0.991–1.004］ | 1.003［0.990–1.009］ | 0.998［0.992–1.012］ |
| write N64 K1 4 BPP | 1.003［0.957–1.014］ | 1.050［1.032–1.059］ | 0.984［0.976–1.002］ |
| write N64 K1 16 BPP | 0.993［0.981–1.009］ | 1.023［1.016–1.058］ | 0.989［0.974–1.010］ |
| write N4096 K1 4 BPP | 1.008［0.995–1.025］ | 1.021［1.006–1.059］ | 0.987［0.964–1.003］ |

D9/D10 未确认变化；D8/D10 保留约 2.1%–5.0% 真写收益。直接 D7/D10 仍有约 1.1%–1.6% 负偏移，区间跨 1
不等于恢复资格。D7 不是 upstream；不能把这些数字乘入 [59](59_br1_shared_upstream_cpu_baseline_20260920.md) 的历史主干比值。

源码仍可见匿名写 batch 最后一个客户端需完成 extent staging、prepared set 与 root commit；这是现存工作，不是新测得
的 self 占比。P3 同一未发布段 first-write 复用、mutation/原位 permit，P4 紧凑生产 metadata/短发布，以及 P5 回收预算
继续是主线，不能用新 facade 的暖读收益代替真实写重构。不得跨已发布版本沿用可写授权或删去 capture gate。

## 6. 首次读与固定工作量：端点补齐，成本转移未关闭

12 个完整 cold rate 桶的 D10/D9 吞吐中位比为 0.983–1.035，区间全部跨 1。D10/D8 多数接近 1；它包含 N64 填充和
发布，不能稀释或豁免独立首次读退化。以下为 **first-read inclusive 时间比**，不是吞吐比：

| 首次读桶 | D10/D9 时间比 | 直接 D10/D8 时间比 |
|---|---:|---:|
| CPU 4 BPP K1 | 1.053［0.954–1.179］ | 1.163［1.159–1.325］ |
| CPU 4 BPP K16 | 1.051［0.994–1.071］ | 1.726［1.573–1.822］ |
| tiles3 4 BPP K1 | 1.062［0.962–1.165］ | 0.995［0.891–1.264］ |
| tiles3 16 BPP K16 | 0.994［0.897–1.040］ | 1.629［1.544–1.716］ |

D10/D9 未确认 cold 变化，不能说新增 shard 查询免费；D8/D10 的 K16 成本转移仍明确存在。
四个 D10 profiled/plain 吞吐比中位数为 0.995、1.001、1.009、1.008；tiles3 4 BPP K1 区间为［1.005–1.037］，
其余跨 1。正向扰动也是扰动，不解释为时钟能加速代码；不以 phase 和重建精确 E。

固定 256 cycle、configure→实际容器析构总墙钟时间比为：

| 桶 | D10/D9 | 直接 D10/D8 |
|---|---:|---:|
| CPU 4 BPP K0 | 1.001［0.970–1.019］ | 0.991［0.985–0.996］ |
| CPU 4 BPP K16 | 0.993［0.976–1.012］ | 0.992［0.983–1.001］ |
| tiles3 16 BPP K0 | 0.992［0.984–1.003］ | 0.980［0.973–0.999］ |
| tiles3 16 BPP K16 | 1.003［0.981–1.034］ | 0.984［0.968–0.997］ |

上述固定-work 对照的各侧析构中位数约 0.051–0.078 ms，D9/D10 析构时间比区间均跨 1；未确认析构回归，但不授予不劣性。
本轮只关闭“遗漏 facade/provider 容器析构”这个端点缺口；全局 tiles3 pool/worker drain、最后长 reader、高 H 和
累计 retired/replay 资源有界性仍 `NotMeasured`。process CPU/墙钟分别在原始结果中保留，不与后台忙时间混加。

## 7. 偏差存根与下一研究，不预写原因

| 存根 | 预期与实际 | 下一证据/关闭条件 |
|---|---|---|
| D10-WarmResidual | 暖冗余减少应恢复 D9 损失；K16 guard/session 改善，但 D8-relative 宽格式/单页仍有负偏移 | 直接 D8/D10 重复配对，记录布局/环境；拆 rect 输出准备、accessor 与 copy，保留原始 E |
| D10-ColdTradeoff | 暖冷分离不能隐去冷 miss 额外查询；K16 首读仍比 D8 慢约 63%–73% | exact-version 高 H、查找/缓存建立与局部锁 opt-in 计量；完整首次读及生命周期并行验收 |
| D10-WriteResidual | 真写不应由读缓存付固定税；D8收益保留，但直接D7仍有负偏移 | record/retire 成本定向对照；推进 P3/P4，不用读收益抵消 |
| D10-Endpoint | D9 close 端点不完整；本轮补容器析构 | 局部端点已测；后台完整 drain、积压峰值/持续时间和长 reader 继续开放 |
| D10-Environment | 部分暖区间宽，现有数据不能区分布局/调度等变异来源 | 记录每进程实际 hash seed、配置、warmup、后台活动；控制诊断与生产默认环境分开复验 |

`KisPageKey/KisPageVersion::qHash` 会传递 seed，但本轮 driver 继承环境，未冻结/记录每进程实际 `QHashSeed`。
因此不能从 workload seed、当前 shell 环境或 bootstrap seed 反推已测进程的 hash seed，更不能断言它造成了回归。
后续可在**独立 benchmark 子进程**使用固定 hash seed 作定向诊断，同时保留生产默认配置的独立重复；不得为跑分改变
生产 hash 策略、事后筛掉不利 seed 或把单个确定性布局当资格证据。分配器/代码布局和 pooler 活动同样是待验证变量。

`readCapturedRect()` 的输出先清零再拷贝，确有可研究的冗余准备；它存在于对照两侧，不是 D10 偏移的已证原因。
如优化完全覆写区域的初始化，须保留 padding/error/publication 语义，并以 payload/direct 控制和完整 E 证明净收益。
不因读微基准容易量化而无限推迟真实写的 mutation/permit、生产 metadata 与回收主线。

D10以本切片实现/诊断、局部析构端点及证据封存收尾，上述五项性能存根仍开放；不要求所有读桶先最优才推进写侧。
结构逐节点核对和下一主要切片边界见 [52 第12节](52_br1_cpu_fast_path_optimization_plan_20260920.md#12-按目标结构推进防止-dx-退化为局部调参)：
优先贯通生产 `writeBytes` 的 mutation/writer/条件COW或permit、发布和回收，保留现有操作batch/persistent root成果，
不把新facade提速或ReferenceModel改名当完整生产路径迁移。该下一切片尚未实装，不继承D10回归/性能证据。

## 8. 统一判词与资格状态

- **目标**：CPU/CpuRam 同义管理对主干等价或更优，不预留 VT 管理附加税；正式结论只能按 39 的预冻结不劣性取得。
- **实现**：新 facade 的冷热查询切片，安全 gate 保留；不是全链路同构，也不是所有 legacy/native write 接入完成。
- **已测**：分支内暖/冷、原生控制、inclusive 分段和固定-work 局部析构；结构/正确性与计时诊断分别成立。
- **未取得资格**：最新候选的直接 upstream M/K/E、required 全桶不劣性、单事件尾延迟、高 H/并发性能、产品 replay、
  全后台 drain。GPU/UMA 产品性能仍 `NotMeasured`；CPU-only 未发生交接，UMA 零迁移项为 `NotApplicable`，不能记 Pass。

UMA 的零只约束同一兼容驻留 shared backing 的真实交接中的 payload migration count/bytes，不约束同域访存、
cache/order、queue/ticket 或整个 E。CPU-only 本轮冷热差额属于软件路径研究，不能重分类成硬件跨域事实。
管理 M、同域驻留 K、跨域/执行交接 X 与完整 E 分别报告再关联，不能机械相加或互相抵消；权威口径见
[39 的 5.11](../../../39_virtual_texture_performance_gates.md#511-统一口径速查与报告判词)。BR1-PERF 保持进行中，BR2 production 不开放。
