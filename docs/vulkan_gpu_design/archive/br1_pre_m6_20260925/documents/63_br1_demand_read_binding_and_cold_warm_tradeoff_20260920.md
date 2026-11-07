> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D9：按需原生读缓存与冷暖成本对照（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

按需缓存消除了未使用 native read 的版本预建工作，**相对 D8，三个原生真实写桶吞吐提高约2.7%–3.8%**。
但直接对 D7 仍有约0.8%–1.7%负偏移；首次16页 read scope 变慢约70%–73%，部分暖读/rect也退化。
因此不能把 lazy cache 定为已经达标的最终设计，更不能用写收益抵消读回归。BR1-PERF继续，下一研究先拆开暖命中和冷发现路径。
完整原件、复算和封存入口见[D9证据](../../../evidence/br1_d9_20260920/README.md)；D8原件及反证保留在[62](62_br1_native_resident_read_and_write_cost_20260920.md)。

## 1. 单一生产处理变量与不变的安全边界

本轮只改变 native read binding cache 的建立时机，不更换 provider allocation record，不去掉 shared gate：

- `KisPageStore.cpp` 不再在 default materialization、adoption、generic read 或 commit 上预建 read candidate。
  只有 captured view 的首次 native read 发现缺缓存后才建立；纯写和 generic read 不代付未使用的 read cache 建立成本。
- `KisPageMetadataCoordinator.cpp` 在短 shard lock 下查询 exact Published/Historical version；优先 ready CPU authority，
  否则选择唯一 ready CPU-readable replica，不能仅因 authority 在其他域就要求物化。不导出/复制完整 page snapshot。
- 冷路径在 shard 锁外取得 ledger provider，重新核验 exact replica 仍 valid 后安装条目；provider record 的 once 解析仍在
  owner/shard锁外。同一版本的并发首次读只保留一个 cache entry。该 cache 不是新的authority或读取授权。
- 捕获root的retention保持版本不被当前CPU历史GC丢弃；pin和generic/native read/write、transfer、retire继续共用局部gate。
  existing guard仍先unpin后release root。原位写permit、future eviction和异步handoff安全仍须另行闭环，不能据此放行。
- 新增私有冷检查 `kisPageStoreCpuReadBindingCount()`，仅按shard统计现存条目，不增加逐访问原子计数，也不改变旧
  `SessionStats`返回布局。它不是并发全局原子快照或累计分配/RSS统计；正式配对fixture不调用这个新符号。

仍有待优化成本：每个provider allocation都创建stable record；纯写retire仍检查cache map；首次读需要metadata版本查找、
ledger lookup、cache allocation/安装及once解析。当前冷version查找沿该页的versions序列，未证明高H复杂度/成本合格。
scope内暖像素读不取PageStore owner gate，但仍有shard/page/swap锁；capture/release也仍有gate，不是严格lock-free。

## 2. 正确性与冻结版本

native suite从24增至**28 passed**（Qt totals含init/cleanup），新增CPU/tiles3两侧：

- 多次真实写/commit与generic读取后cache条目仍为0；
- 先捕获、后写入、再首次读取旧版本，仍返回历史bytes；
- 8个并发首次reader竞争同一版本，最终只保留一份条目；busy允许拒绝try，不允许返回错误bytes；
- 最后旧guard/root释放后历史cache删除，close后cache及committed payload归零；
- virgin default先报VirtualDefault；generic物化后同一captured view首次native读取成功，没有永久negative miss。

原D8历史/并发/abort/revoke、generic/native互斥、transfer/retire、swap-out与unsupported-provider测试继续通过。
read fixture新增12个cold-cycle正确性行，共**33**；Reference **59**、Foundation **24**、tiled-manager **88**、
原生共享fixture **34**、Vulkan contracts **13**，静态architecture guard通过。早期构建发现并修正了私有检查声明及新测试
调用接口问题；正式配对在修复、全部构建及功能回归结束后冻结。回归墙钟不作为性能数据；未重跑GUI、长压或sanitizer。

环境沿用D8：Mac16,10 / 24GiB / macOS15.7.3、Qt6.8、RelWithDebInfo，universal构建/arm64执行。
69个源码文件、三个版本runtime共407项hash；base仍是`f5fbbde618df6fb4e1068ace7381c339a70dd4c0`加归档dirty patch/source。
common binary只调用旧公共API；D8/D9不改变公共布局/虚表，D7只用于旧native fixture。12次loader检查核对实际加载的库。

## 3. 协议与计量范围

协议在性能采集前冻结：**48个配对桶 × 8对 = 384对、768次计时运行**，另12次loader检查；每次完成窗口至少200ms，
轮换桶顺序、交替两侧先后，无profiler，不与构建/功能测试并发。所有pair保留；区间是独立进程pair的探索性95% bootstrap，
没有预冻结不劣性容差，不授予正式Pass。吞吐是完成量，不是单次延迟倒数；process CPU/完成量是窗口均摊成本。

| 配对组 | 桶数 | before → after | 范围 |
|---|---:|---|---|
| integration | 18 | D8 → D9 | 原D8暖payload/binding session/accessor/rect；每次capture/cache/release计时 |
| native | 5 | D8 → D9 | 未迁移原生tiles3 cached guard/read/三个真实scanline写控制 |
| native_reference | 5 | D7 → D9 | 新采样直接对照，不连乘D8比值；不是upstream |
| cold | 12 | D8 → D9 | CPU/tiles3 × 4/16 BPP × K0/1/16，每周期重写发布N64页，再首次读K页并释放 |
| cold_profile | 4 | D8 → D9 | 额外启用prepare/publish与首次read scope区间时钟，仅作inclusive诊断 |
| cold_perturbation | 4 | D9 plain → profiled | 独立配对检查区间时钟扰动，不与实现收益混同 |

cold K0没有新read API，是完整写/发布/退休控制。每次publish产生新generation，所以payload已就绪但binding没有被预暖；
初始configure/fill与最终close分别计量，原字段`lifecycle_ns`实际是configure开始到close返回的窗口。
源码复核确认它尚不包含随后facade/provider容器析构，不能因字段名便称全部生命周期成本；旧版本GC在后续commit发生，
最终容器销毁及完整异步后台drain仍需补测。原日志/协议不改名或补造缺失时间。
Qt正确性检查及每周期两次冷stats读取均计入两侧；这不是隔离M。N64整页fill含真实像素/COW与发布，不等同于原生scanline写。
暖session/accessor每页仅触达一个字节；rect含输出buffer分配/清零及完整拷贝，不能把它直接标为K或纯管理。

## 4. 原生真实写：部分收回D8开销，但未恢复资格

以下为after/before完成吞吐比，大更好：

| 原生桶 | D9/D8配对中位比［探索区间］ | 本轮直接D9/D7［探索区间］ |
|---|---:|---:|
| cached guard N64 K1 4BPP | 0.999［0.992–1.002］ | 1.000［0.997–1.010］ |
| read N1024 K16 4BPP | 1.008［1.005–1.016］ | 1.003［0.986–1.027］ |
| write N64 K1 4BPP | 1.038［1.026–1.050］ | 0.992［0.956–1.000］ |
| write N64 K1 16BPP | 1.027［1.014–1.037］ | 0.988［0.971–1.009］ |
| write N4096 K1 4BPP | 1.032［1.024–1.048］ | 0.983［0.973–1.010］ |

D8/D9三个写桶窗口CPU/操作的两侧中位值约9,892→9,537ns、11,296→10,985ns、11,027→10,629ns。
pair ratio的中位数不等于两侧各自中位数之比，不能互换。独立D7/D9配对仍保留负偏移，不称“已与D7等速”。
移除eager cache维护支持“它是D8写回归的一个贡献项”，不证明stable record、shared gate或全部残余的self成本。
更不构成对D5主干巨大真实写差距的解决；P3 mutation/permit、P4布局与P5回收主线不变。

## 5. 反证一：暖读并未全部保持

| 新facade桶 | D9/D8完成吞吐比 | 探索区间 |
|---|---:|---:|
| session N16 K1 / 1BPP | 0.994 | 0.983–1.019 |
| session N256 K1 / 1BPP | 1.000 | 0.960–1.019 |
| session N256 K16 / 1BPP | 0.982 | 0.963–0.989 |
| session N256 K1 H1 / 1BPP | 1.004 | 0.975–1.011 |
| accessor N256 K16 / 1BPP | 0.982 | 0.958–0.988 |
| rect N256 K16 / CPU 4BPP | 0.927 | 0.891–0.983 |
| rect N256 K16 / CPU 8BPP | 0.970 | 0.950–0.986 |
| rect N256 K16 / CPU 16BPP | 0.951 | 0.926–0.973 |

其余暖桶及原件见`integration-analysis.json`。tiles3宽格式rect也有负偏移，但部分区间跨1；不能一律称噪声或一律称确定退化。
warm generic requests两侧都为0，说明零request结构门禁无法替代性能对照。

源码可检验的新假设：D9暖命中也构造一个完整`KisReplicaHandle coldReplica`，并让metadata输出参数再次初始化，即使不需要
冷发现；分支/调用布局与cache建立造成的内存布局变化也可能影响结果。当前没有self证据把约7.3%的rect差额全部分给该对象：
rect还有输出分配/清零、逐行accessor和memcpy，必须拆开guard与payload控制。不能因同域便把这些差额全部叫VT管理成本。

## 6. 反证二：冷读确实承担了工作转移

无phase时钟的完整cold周期，D9/D8配对吞吐如下。仅说明这些固定N/K桶的整体表现，不替代独立读成本或所有生命周期资格：

| provider / BPP | K0（无读） | K1（首次读一页） | K16（首次读16页） |
|---|---:|---:|---:|
| CPU / 4 | 1.019 | 0.997 | 1.006 |
| CPU / 16 | 1.013 | 0.995 | 1.010 |
| tiles3 / 4 | 1.016 | 1.016 | 1.017 |
| tiles3 / 16 | 1.010 | 1.021 | 1.006 |

完整探索区间、setup/close与configure→close窗口在`cold-analysis.json`。没有普遍大幅净收益；两个CPU K1中位负偏移也保留。
这组E由64页真实fill/write/publish主导，不允许用其正向吞吐豁免首次读M。

profiled运行的首次read scope墙钟窗口均摊中位值（不是单次延迟或binding self）：

| 桶 | D8 ns/cycle → D9 ns/cycle | D9/D8配对时间比［探索区间］ |
|---|---:|---:|
| CPU 4BPP K1 | 1,632 → 1,936 | 1.135［1.123–1.246］ |
| CPU 4BPP K16 | 5,475 → 9,192 | 1.703［1.652–1.738］ |
| tiles3 4BPP K1 | 1,550 → 1,880 | 1.190［1.135–1.235］ |
| tiles3 16BPP K16 | 5,463 → 9,493 | 1.730［1.673–1.775］ |

prepare/publish的配对时间比约0.984–0.992，与移除写侧维护、增加首次读发现/安装的方向一致；具体锁/allocator self仍未知。
cold_perturbation中profiled/plain吞吐为约0.988–1.006，其中CPU 4BPP K16为0.988［0.979–0.995］。
所以不声称时钟零扰动；短K1区间仍有时钟/边界成本，以上只支持inclusive工作转移判断，不能拿它计算精确锁等待或硬件下界。

## 7. 偏差存根、下一研究与资格

| 编号 | 观察/状态 | 下一证据 |
|---|---|---|
| D9-write-residual | 相对D8改善，直接D7/D9真实写仍约0.8%–1.7%负偏移；未关闭 | 保留record/gate，研究重复同步、record布局与真正mutation粒度；重新直接配对 |
| D9-warm-read-regression | 多页session/accessor约1.8%退化，CPU rect部分桶约3%–7.3%；未关闭 | 独立暖cache lookup与冷发现API，去掉暖命中不必要的cold handle；配对D9/D8控制，不凭源码宣布收益 |
| D9-cold-work-transfer | 首次16页read scope约70%–73%变慢 | 首次read、纯写及完整周期一起保留；不能把预热移出窗口关闭反证；高H的version查找另测 |
| D9-instrumentation | 一个phase profile桶约1.2%反向扰动 | 保留plain结果和扰动区间；细self需更长批次/抽样校准，不盲目提高采样频率 |
| D9-close-window | `lifecycle_ns`止于close返回，未覆盖随后facade/provider容器析构 | 下轮显式计时最终对象销毁及完整drain；本轮仅作为configure→close端点窗口，不授予全生命周期资格 |
| D9-unmeasured | upstream NI、固定-work/事件尾、高H/并发性能、完整drain、GPU/UMA仍未通过 | 沿39/20/52的独立冻结矩阵补齐，不用768次运行数量代替覆盖 |

下一切片先分离暖lookup与冷候选发现，让cold结构仅在真实miss时构造；该实验必须保留D9原始源码/runtime和全部负面结果，
同时对D8/D9直接重测暖读/rect、首次读和真实写，并补最终容器析构。若暖guard恢复而rect仍慢，再拆输出分配/清零、accessor和copy的同域控制；
不先归因于mutex等待，也不把软件残余改称物理跨域开销。provider record/gate仍不能仅为恢复比值被删除。

D9是正确性通过、性能未结清的候选，**不是优于D8/D7的全面资格结论**。BR1-PERF继续；BR2 production/GPU入口关闭。
CPU-only未发生CPU↔GPU交接，UMA零迁移项为NotApplicable，GPU/UMA产品性能NotMeasured。
