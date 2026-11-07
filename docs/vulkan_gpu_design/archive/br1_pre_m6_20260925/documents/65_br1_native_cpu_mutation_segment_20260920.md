> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D11：生产 CPU 未发布写段与性能反证（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

**方向已从读缓存局部调参转回生产写生命周期，但目标结构仍未完成。** `writeBytes()` 已接通 native mutation 段，
同页重复访问复用 pending generation，段末统一 seal；这不是只给通用 request 换类名。不过单页写比 D10 慢约
**5%–6%**，16 页写快约 **8%**；直接固定主干，真实写吞吐仍仅其 **0.26%–0.45%**。不能宣布 P3 或 BR1-PERF 结清。

原件、冻结身份、复算与失败记录见 [D11 证据目录](../../../evidence/br1_d11_20260920/README.md)；执行入口为
[52 的 1.15/11/12 节](52_br1_cpu_fast_path_optimization_plan_20260920.md)。D6–D10 已封存原件不改写。

## 1. 实际迁移了什么

调用链为 `KisTiledDataManager::writeBytes` → `beginCpuMutationBatch` → owner `beginCpuMutation` → tile 首次
mutable exposure → `beginWrite` → `KisCpuWriteGuard` → tile unlock 归还访问权 → 段末 `seal` → 既有 extent/root commit。

| 环节 | D11 实装事实 | 仍缺什么 |
|---|---|---|
| 起点/base | 加入已捕获并保留 base 的 transaction；精确 provider id/epoch/capability 校验 | 无全局 gate 的起点不在本次范围 |
| 写授权 | tx/page claims，metadata writer token，精确目标 binding 独占 pin | page-local writer/紧凑生产记录；仍有 owner mutex 与 claims QHash |
| first-write | 沿用 D4 native duplicate；目标 discard 用 staged surface default | 原位 permit、virtual-default 直接 writable 初始化；当前仍每段整页 COW |
| 同页复用 | 本段 QHash 保存一个 pending generation；16 次 guard 只一次 reserve/COW/seal | legacy iterator/brush 的算法边界迁移；不能据此称所有生产入口已复用 |
| guard release | 只结束可写访问；scope 保留物理 writer pin 至 seal/cancel | 大 K pin 峰值/持续时间/压力预算；不能称 pin 成本已消除 |
| seal | 无 generic write request/access-lease map；统一 host completion，每 dirty page 一次 proof | metadata snapshot、逐页 proof/校验与 owner-held准备仍在；不是短发布 |
| root/retire | 沿用 canonical commit；claim 保留到物理收尾，退休锁外执行 | 短发布所需全部 claims/锁外准备、增量删除 extent、有界 drain |

源码入口：[owner API](../../../../../krita/libs/image/pagestore/KisPageStore.h)、
[mutation 实现](../../../../../krita/libs/image/pagestore/KisPageStore.cpp)、
[兼容层 batch/lease](../../../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp)、
[生产 writeBytes](../../../../../krita/libs/image/tiles3/kis_tiled_data_manager.cc)、
[mutable 访问失败检查](../../../../../krita/libs/image/tiles3/kis_tile.cc)。

只对支持 synchronous native write-copy 的 tiles3 CPU provider 启用；不支持 capability 时**开始前**走旧路径。
失败的半次 native 操作不得转到 generic 重放。`seal()` 不是 root commit；同一 history transaction 的前一 prepared
段必须可继续读取，后续操作新段重新授权，不能跨可见性边界复用已暴露的 writable generation。

## 2. 安全修复与验证范围

本轮验证先暴露并修复了 history clear→write：把 removal 后的逻辑 default 当 writer 的 before-version，状态机报
`write base is not visible to the transaction`。现在从受保护 epoch/较早 Prepared 解析 before，目标按 staged default
初始化，绝不复制已删除像素；取消则恢复 staged removal。原失败日志保留，不掩盖修复过程。

同时补齐：

- `tryWriteData()` 对写授权失败返回空，`writeBytesBody` 停止，batch 取消并刷新兼容索引；不能让 `memcpy` 写旧指针。
- native batch 销毁而 guard 仍在时，由 lease 保留控制块，最后 guard 延迟取消、释放 page/tx claim；backend registry
  为弱引用，避免永久占页/引用环。显式 finish 遇到活跃 guard 失败，不能提前 unpin。
- 失败 seal 的 `AbortPreparedVersion` 只撤销本段 exact Prepared version，保留较早 history proof；owner gate 内完成
  metadata/proof 回滚再放锁退休，防止失败的半个段被新 reader 捕获。generation 高水位不回退。
- scope 中途结束前，binding 拒绝另一 writer/read/retire；旧 captured root/guard 的字节保持原样。多个 alias backing
  不由单个 binding 的 reader 数授予原位写资格。

新 `KisPageStoreCpuMutationTest` **17** 项（含 init/cleanup），覆盖 1/4/8/16 BPP、同页16次复用、下一段新 generation、
intent不分配、取消、同页冲突/异页进展、线程误用、guard超出facade寿命、batch延迟取消、default revision/removal、
allocation失败、首个/第二个 proof 失败和较早 prepared 段保留。
既有 Reference **59**、Foundation **24**、ResidentRead **28**、read fixture **41**、tiled-manager **88**、
共用 native fixture **34**、Vulkan contracts **13** 与 architecture guard 通过。新 fixture 的实际计数包含 native
generation/seal，不能再用 generic request=0 推导没有写入。未运行 GUI、sanitizer、长期压力或完整新增并发矩阵。

## 3. 同源直接对照与 ABI 纠正

候选基点 `f5fbbde618df6fb4e1068ace7381c339a70dd4c0` 加冻结 dirty source/patch，不是只 checkout HEAD 即可复现。
固定主干为 `9a24ae0d8c`，未声称实时最新 upstream。环境仍为 Mac16,10 /24 GiB/macOS15.7.3、Qt6.8、
RelWithDebInfo universal 构建/arm64 执行。冻结 94 份源码和 D10/D11/upstream runtime，身份表共418项 hash。

D10/D11 共用兼容 executable；主干需用**同一 fixture 源码分别编译**的 executable。初次交叉装载在 loader 阶段因
主干 inline `commit()` 不提供候选引用的 out-of-line 符号而失败，未产生有效计时；原件及计时前纠正在
[measurement-decision](../../../evidence/br1_d11_20260920/measurement-decision.md)。不将源码相同等同 ABI 全同。

两组各11桶×8对，共 **352 次 rate 运行**；另6桶×4对 plain/sample，共 **48 次诊断运行**，总400次有效计时、
6次有效 loader，另保留1次失败 loader。每个rate进程独立至少200ms，轮换桶顺序与两侧先后，不与构建/回归/profiler并发。
区间为进程pair的10,000次探索性bootstrap，不是预注册正式不劣性判决；不删负面pair，不连乘旧倍率。
未采集实际随机hash seed、完整后台/热状态，不推断它们导致差异。

## 4. 结果：批量有收益，单页退化，主干差距未关闭

下表为完成吞吐比 candidate/baseline（大更好），方括号为探索性95%区间。不是单事件延迟/P95/P99。

| 真写桶 | D11 / D10 | 直接 D11 / upstream |
|---|---:|---:|
| N64 K1 4 BPP | 0.938 [0.933–0.947] | 0.00289 [0.00286–0.00296] |
| N64 K1 8 BPP | 0.950 [0.940–0.970] | 0.00304 [0.00301–0.00309] |
| N64 K1 16 BPP | 0.944 [0.923–0.964] | 0.00323 [0.00317–0.00329] |
| N1024 K16 4 BPP | 1.083 [1.074–1.089] | 0.00446 [0.00438–0.00457] |
| N4096 K1 4 BPP | 0.945 [0.910–0.978] | 0.00258 [0.00255–0.00259] |

同源 write fixture 是真实交替 scanline 修改，未改的63行必须保持正确；不是 alias/no-op。
在其无外部 reader/history 的稳态，主干可保持 exclusive TileData 原位写，而 D11 每次操作仍 COW/新 generation/seal/root。
所以**不是目标结构已经同构后只剩编译器/锁微调**。这里同时含软件管理、必要/非必要同域 copy 和兼容层，不能把整个差额
赋给管理 M，更不能记成跨 RAM/VRAM 的 X；双方本次都是 CPU/CpuRam。

| 分层控制桶 | D11 / D10 | 直接 D11 / upstream | 解释限制 |
|---|---:|---:|---|
| cached guard N64 K1 | 0.993 [0.982–0.997] | 0.755 [0.751–0.761] | 对应管理动作代理，不是全部M；分支内小负偏移保留 |
| write intent N64 K1 | 1.001 [0.990–1.003] | 0.858 [0.857–0.865] | 没暴露可写指针，不代表真实写 |
| readBytes N64 K1 | 1.001 [0.992–1.011] | 0.909 [0.887–0.918] | 完整该读入口，不是新facade所有读 |
| readBytes N1024 K16 | 1.003 [0.995–1.008] | 0.865 [0.854–0.870] | 读侧主干差距仍在 |
| prebound RAM copy K1 | 1.006 [0.997–1.031] | 1.001 [0.977–1.018] | pin在窗口外，只测K |
| prebound RAM copy K16 | 1.008 [0.997–1.008] | 0.996 [0.687–1.003] | 区间较宽，保留不确定性；不是正式不劣性 |

预持指针 copy 没有真实写的数量级差距，不支持“DRAM copy性能本身相差数百倍”的解释；它也不能单独证明其它阶段等价。
rate下 manager destruction 另记，不按不同完成量的析构/峰值比证明资源效率。完整 pool/worker drain、事件尾与GPU/UMA均未测。

## 5. 分段/工作量证据与局限

固定8192次操作，每16次采一个完整操作；每桶4个 plain/sample pair。样本 timer 是 inclusive，不是纯mutex self：

| 固定-work桶 | plain均摊µs/操作 | 采样内 batch begin | 采样内 body | 采样内 finish | sample/plain总时间比 |
|---|---:|---:|---:|---:|---:|
| N64 K1 H0 B4 | 10.45 | 1.06 | 3.17 | 10.86 | 1.041 |
| N4096 K1 H0 B4 | 12.26 | 1.07 | 3.82 | 12.64 | 1.033 |
| N1024 K16 H0 B4 | 89.72 | 1.06 | 49.61 | 55.81 | 1.004 |
| N1024 K16 H4 B4 | 101.17 | 1.08 | 50.26 | 67.37 | 1.009 |
| N1024 K16 H0 B16 | 108.06 | 1.07 | 67.53 | 55.16 | 1.004 |
| N1024 K16 H4 B16 | 120.90 | 1.08 | 69.65 | 66.61 | 0.996 |

后三个阶段列单位同为µs/**被采样操作**；阶段时钟及其子计时会放大被采样操作，不能相加后声称重建plain总耗时，
不能用约4%的整窗扰动推导每个短阶段只有4%扰动。body包含native beginWrite/COW/字节copy，finish包含seal、extent、
commit与部分回收。`write_acquire`、`write_provider_prepare` 是body的嵌套子区间，不再相加；native `write_publish_host`
每段一个interval/workItems=dirty页，位于finish内，不与旧per-lease publish直接同义比较。

例如N1024/K16/H0：B4→B16的采样provider prepare约15.86→33.25µs，而seal约15.53→15.42µs、
root publication约0.225→0.224µs。H0→H4时finish约55.81→67.37µs，不能因此将全部增量定名为某个锁或GC self。
原始wall/CPU/interval/workItems均保留；关闭态埋点代码本身的独立消融、锁wait/hold、allocator/control-block self仍缺测。

结构上：每次操作K页各一次 reserve、native duplicate、guard release、seal；generic write request=0、root commit=1。
K1/B4共8192次段仍逻辑复制128MiB整页数据；K16/B4为2GiB，K16/B16为8GiB；这不是硬件流量计数。
前台preclone hit=0，实际foreground copy字节随上述计数；旧63行因安全COW保留。**没有 reader 不自动消除这些copy**。

## 6. 反证存根与下一研究

| 存根 | 观察/缺口 | 下一步可证伪工作 |
|---|---|---|
| D11-K1Regression | 去掉generic request但K1吞吐下降5%–6% | 冻结K1起点/control-block/claim/收尾的粗粒度消融；保留完整E及D10对照，不能先把差额归给QHash或锁 |
| D11-WriteParity | 真写仅主干0.26%–0.45%；仍整页COW、逐段新root | 原位permit的安全纵向实现、紧凑writer/version生产记录及短发布；不是继续读缓存调参 |
| D11-PinBudget | dirty页physical writer pin保留整段 | 大K/长段pin数量/时间、内存压力、分段prepare与背压；不得仅为unpin而暴露半段或丢writer保护 |
| D11-Attribution | inclusive采样、K1整窗扰动约3%–4%；新段没有全部fine self | 粗粒度分组/关闭态消融，随后锁wait/hold；不从原子root赋值很短推断整个publish临界区很短 |
| D11-Compatibility | writeBytes覆盖，accessor/brush未统一；同源不等于同ABI | 列入口/布局/inline契约；legacy读pin与alias的并发保护矩阵先于permit |
| D11-ControlResidual | guard小幅负偏移、upstream K16 copy区间宽 | 独立环境/布局诊断，保留全部pair，不追求读微基准最优再推进写 |

下一主要研究必须先解决 **permit 的授权闭环**。`KisTile::lockForRead()` 的native-ready分支直接对TileData做swap pin，
不等于已进入新 `KisCpuResidentBinding` 的reader计数；多个record又可能共享一个TileData。
原位写前须统一这些真实物理读者/alias与capture/retention gate，不能按“binding readers==0”或瞬时usersCount放行。
随后将可失败prepare/root/retirement记录构造移出短发布区，并保留冲突复验。没有exact-before的exclusive-immediate分支
必须保证首字节之后不可普通失败/abort；本次多页可取消COW段不能直接删copy获得该资格。

如果这些结构真正落地后仍不满足同义M和产品E门禁，再按52第8节研究受控重构/回退。当前证据说明方向仍值得推进，
但也反证了“已有session就已实现主干成熟热路径”；不能无限以局部百分比代替最终结构、差分和资源预算。
