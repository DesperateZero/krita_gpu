# CP3：handoff 成本、30% 可达性与实际价值

本包完成的是下一步的可达性和价值诊断。产品保持 `f0c40a5d195f1c20a0f915faaef18b1f3ee5b575`，生产改动 **0**。结论：**现有 CPU recoverable handoff 有条件性局部收益和容量价值，但没有证据支持把 K16 固定下降30%作为其价值的唯一判据。当前普通 tiles3 业务的自然 alternate 来源和持续命中尚未建立，继续只为该微基准做小额管理优化不是当前最有依据的投入。** 原门保持失败，不据诊断结果宣布 M6 通过，也不自动修改阶段顺序。

## 有限问题、变更与证据

使用 algorithm-cost-optimization skill，先冻结[协议](protocol.json)，完成以下矩阵。计时前有50个语义/时钟检查进程，随后534个固定诊断进程；因逐段CPU时钟扰动过大，事前另定[CPU采样协议](profile-protocol.json)，运行6个短时CPU采样进程。所有进程正常退出、reap、语义和加载库通过。没有重新采样失败数据或扩充原正式40对门。

| 问题/位置 | 理想或必要工作 | 本包动作 | 裁决 |
|---|---|---|---|
| 原 fixture 同时改变 alternate 数量与 selector | 从同一初始 exact replica set 比较合法方案 | 两侧均2副本；诊断副本中在 handoff 准备前拒绝候选，完整走原 Fresh | 同状态局部优势成立，不能与上一包比值相减作补丁收益 |
| native prepare → seal → commit 成本 | 独占阶段和机制计一次，父子不相加 | fixture分段、两TU诊断scope；CPU时钟扰动对照；另用Running CPU采样 | 主要为CPU管理；metadata单项没有承担主缺口的预算 |
| Preserve 后整页覆盖 | full input应直接初始化；partial仍保留未改字节 | 原Preserve、partial一行、原overwritePage三桶 | full input下仍有收益，但不能把收益全归为before-copy |
| alternate 是否可跨generation复用 | before必须是当前被改写generation的exact副本 | 同一Store连续4次发布，保留各操作前exact View | 第一轮16次命中，随后0/0/0；不能摊销成每轮命中 |
| 资源是否改善 | 同状态、同容量、同输出/恢复端点 | provider预算固定2S，对照安全拒绝 | handoff完成，现有双副本Fresh拒绝；不证明所有Fresh驱逐策略都拒绝 |
| 业务是否自然产生资格 | 存在真实producer提供同generation独立CPU副本 | 当前caller和状态机审查 | 普通导入/clone仅authority；尚无实际stroke命中证据 |
| 是否实施下一容器/metadata改动 | 合法可删预算应承担缺口 | 对照候选整个上下文与原20.01/29.37μs缺口 | 不启动没有预算支持的生产改写；诊断问题已关闭，必要下界未伪造 |

诊断仅机械复制 `KisPageWriteCoordinator.cpp` 与 `KisTiles3PageReplicaProvider.cpp` 两个TU，分别保存[协调器差异](KisPageWriteCoordinator.patch)、[provider差异](KisTiles3PageReplicaProvider.patch)。另373个真实对象复用原构建；force-Fresh只提前选择已有安全fallback，不取消安全检查或修改像素/生命周期。诊断开关不进入产品。重建见[生成/构建](prepare_diagnostic.py)、[夹具](value-probe.cpp)、[运行器](run_experiment.py)和[CPU夹具提取](prepare_profile.py)。

产品2315个先前冻结源码hash及109个原运行输入复核一致；当前产品跟踪树干净。[身份核对](product-identity-verification.json)与[源码审查](source-audit.json)绑定同一产品，既有安全资格继承原批；本轮没有重跑无变更的完整QTest或声称新增安全阶段资格。

## 时间比较：同状态后仍未达到30%

[完整统计](summary.json)的主矩阵为双架、6种形状、3种variant、12个顺序平衡块，共432进程；每进程8次warmup+32次测量，进程中位数进入配对。下表是**两边都有2个初始独立exact副本**时，handoff相对当前原Fresh路径的延迟减少，双侧95%描述性区间；不是多桶family资格。x86_64在Rosetta运行，不外推原生Intel机器。

| 用例 | ARM | Rosetta |
|---|---:|---:|
| K1/B4，Preserve首写 | 7.27% [5.95%,8.89%] | 7.64% [3.89%,10.05%] |
| K16/B4，Preserve首写 | **16.93% [14.81%,18.77%]** | **16.23% [10.67%,21.03%]** |
| K16/B4，部分写一行 | 19.60% [16.16%,22.89%] | 20.23% [15.40%,21.89%] |
| K16/B4，完整输入overwritePage | 13.01% [11.73%,18.94%] | 15.44% [13.85%,18.12%] |
| K16/B16，Preserve首写 | 24.66% [23.00%,25.13%] | 24.93% [22.62%,27.12%] |
| K16/B4，连续4次发布的累计操作时间 | **3.64% [0.89%,6.01%]** | **5.20% [4.00%,7.07%]** |

K16/B4同状态首写边际Fresh/handoff为127.40/106.10μs（ARM）、201.87/169.10μs（Rosetta）；配对节省21.58/32.77μs。与原“一副本Fresh、两副本handoff”相比，双副本Fresh需要管理/保留更多旧副本，代价更高，因此同状态优势比原形状大；这是初始状态效应，不是产品加速。

同批一副本Fresh对两副本handoff的K16/B4点估计10.65%/10.47%；原正式40对13.55%/14.50%结果保持原义。此次新夹具有完整字节验证、CPU总时钟和显式drain，诊断库也不同，不能替代原门。B增至16使复制负担更大、优势上升，仍未达到30%；两个B点不构成可靠外推或复杂度证明，不能换B冒充B4通过。

## alternate 会被消费，制造副本不构成算法节省

每次成功M6转换是：`G0:{A,B} → G0:{B}, G1:{A'}`。A被retag并改写为G1；B仍只恢复G0。下一次写G1时不存在G1的第二exact副本。当前[状态机](../../../../krita/libs/image/pagestore/KisPageStateMachine.cpp:319)明确移除旧authority、为新generation只追加一个target。[发现条件](../../../../krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:3138)要求所选generation自身有第二Valid CpuRam副本，不能拿旧G0、derived display或SSD记录代替。

连续4次的全部测量均为`[16,0,0,0]`命中；Fresh两组为`[0,0,0,0]`。该控制保留4个操作前exact View，避免后台释放干扰物理增量，属于冻结边界诊断而非实际freehand trace。同一未发布段内继续写应走已有pending复用，本来就不应反复走M6；新的冻结/发布边界后，必须重新证明alternate资格。

若把专为handoff创建第二副本的setup、完整字节验证、close与显式reclamation barrier也计入，K16/B4首写相对一副本Fresh的完整sample **ARM慢25.92% [24.35%,28.70%]，Rosetta慢26.71% [23.98%,33.30%]**。四次发布后仍慢9.61%/9.16%。这不是产品E或纯setup的因果价格，但足以拒绝“在本夹具中额外制造alternate就能赚取整体收益”。它也符合现行合同禁止临时整页复制来制造handoff命中的规定。

两边都有已存在alternate时，完整sample首写ARM减少3.85% [3.33%,5.57%]，Rosetta4.36% [−0.41%,6.93%]；共同初始化/验证/清理会稀释操作内优势。真实业务应计入实际alternate来源、保留和重建成本，不能把这里的synthetic setup摊到一个未经证明的无限复用次数。

## CPU归因与剩余预算

CPU busy-loop校准：ARM线程CPU覆盖wall约99.97%，Rosetta仅2.40%，因此不解释Rosetta线程CPU。fixture粗阶段按样本精确闭合；nested scope的独占值扣除子scope，父inclusive上下文另列。

但逐段CPU时钟自身有显著扰动：handoff mode1（内部只测wall、fixture粗段测CPU）约慢7.33%，区间含零；mode2内部同时读CPU约慢32.53%，其他两variant也有约20%–23%开销。因此mode2绝不是理想成本或精确单价。mode1的handoff metadata约12.34μs、accounting5.91μs、joint install8.26μs、cleanup2.27μs、plan整个上下文34.58μs，只作粗定位。

随后6个固定CPU采样进程使用关闭分段时钟的同源诊断库，Time Profiler只取Running，按夹具精确操作的noinline函数/唯一lambda划界。累计3127个操作内样本；setup、validation、输出、close/drain和后台另计。3秒采样份额乘15秒循环实际CPU/op，只提供两次独立观察范围，不是置信区间或可删除量。[CPU统计](cpu-summary.json)：

| ARM K16/B4，μs/op | Fresh，一副本 | Fresh，已有双副本 | handoff |
|---|---:|---:|---:|
| 实测操作线程CPU | 117.57–118.66 | 126.07–126.86 | 101.64–104.82 |
| beginWrite归因 | 58.89–61.66 | 60.33–61.15 | 40.57–46.59 |
| seal+commit归因 | 53.46–54.96 | 60.67–62.92 | **49.08–59.09** |
| before-copy机器叶子归因 | 2.42–3.72 | 4.08–4.46 | 0样本；另有结构计数证明0复制 |
| handoff plan inclusive | — | 0–0.24 | 27.44–34.88 |
| 其中metadata prepare inclusive | — | — | **9.85–14.20** |
| 其中accounting prepare inclusive | — | — | 5.16–5.98 |

机器机制独占分类也显示handoff metadata/working约26.90–28.84μs、write protocol25.16–26.97、physical heap17.94–18.06。该机制表与阶段表是两种视角，不能相加；27–35μs plan已经包含metadata/accounting，不重复收费。各操作wall比CPU均值多约0.4–1.2μs，当前暖单线程诊断没有“大额睡眠等待”证据；这个差值不是已定位mutex等待，也不能代表竞争负载。未符号化leaf约1.2%–4.2%，尽可能按已知caller归属，少量fixture/clock/unclassified保留。

这次账否定了“消除剩余metadata临时分配就足以过门”的预算假设。原正式形状仍需handoff单方再省20.01/29.37μs；即便粗暴将观测到的整个metadata准备变成零，ARM观测量级也不足20.01μs，实际还必须保留revision、两个generation、恢复、容量和joint install。这里只能否定该单项作为主解法的合理性，不能把有扰动的测量或短采样当严格优化上界。

整个handoff plan还有约27–35μs，但要从中省20μs相当于删去约57%–73%的整个准备/安装上下文；当前没有保持合同且能实现该幅度的构造证明。seal/commit近一半CPU是共同责任，优化会同时改变Fresh分母。按原正式中位数，若Fresh节省x、handoff节省y，须`y−0.7x≥20.01/29.37μs`；等量共同优化需要约66.70/97.91μs。不能把约50μs共同发布全部算作handoff独享空间。

完整观测分类可以闭合，但“共同必要C/Fresh专属A/handoff专属R”的安全下界仍未建立：同名阶段受副本数、释放与状态影响，不当然等时；没有因果干预覆盖的差额继续保留。结论是**没有已证实能承担主门的下一生产改动**，不是证明所有合法算法不可能达到30%。

## 容量价值与真实consumer

S=K16×64×64×4=256KiB。

| 初始/路径 | 写前payload | 写后payload | provider预算512KiB时 |
|---|---:|---:|---|
| 一副本 → Fresh | 256KiB | 512KiB | 成功 |
| 已有双副本 → Fresh | 512KiB | 通常768KiB | 安全拒绝，旧值保持 |
| 已有双副本 → handoff | 512KiB | 512KiB | 成功，旧/新值保持 |

这证明现有路径在**同状态**下避免新增256KiB，有明确容量价值；并不证明对“一副本Fresh”降低最终payload，也不证明“先合法丢弃冗余alternate再Fresh”的所有策略都无法进展。后者未测，不能由本次拒绝宣称handoff不可替代。

[当前源码审查](source-audit.json)发现普通byte import与tiles3 clone均调用单authority的初始导入；backend只配置一个native CPU provider。生产caller审查未发现提供`readyAlternates`集合的调用者，测试/证据夹具显式提供。这个结果支持“普通tiles3业务的自然正例尚未建立”，不等于对所有将来provider/外部调用证明永不命中。真实命中率p、资格错失原因、fallback成本与业务收益仍需原真实stroke trace，不能填100%。

## 对门禁与投入的判断

30%成立的条件为`TF=C+A, TH=C+R`且`0.7A≥0.3C+R`。算法正确或O(K)并不保证常数满足该式。真实混合负载还需扣除alternate维护与拒绝尝试成本；若命中净节省d、未命中新增开销e、alternate增量成本q，则每次尝试净收益为`p*d−(1−p)*e−q`。p来自真实generation/consumer轨迹，不来自预装双副本的fixture。

**建议判断：**

1. 当前30%适合保留为指定形状的性能目标；在缺少业务预算与可达性校准时，不适合作为handoff是否值得、乃至整条BR1路线是否继续的唯一代理。它没有反映同状态比较、实际命中率和容量/进度价值。也不能用完成了很多优化来证明目标错误。
2. 保留已验证的recoverable handoff作为“消费已有合格资源”的能力有依据：同状态首写约16%–20%的局部收益和256KiB的新增payload避免都存在。它目前不具备“持续CPU绘画核心加速手段”的证据；不值得为专门造alternate或仅追赶该微基准继续扩展协议。
3. 下一决策先回答真实producer/命中分布以及miss路径代价，再关联完整业务绝对延迟、资源峰值和进度。没有自然alternate时，应优先已有合同中的pending跨dab复用、真实冻结边界和共同发布管理；这些仍按原阶段与安全要求实施，不能借诊断自动取得M7/M8资格。
4. 若正式调整门禁，应另行预注册：安全/零额外copy/资源硬门保持；机会型handoff用同状态的净收益与失败路径不劣性；业务价值用真实trace含来源维护/退出和容量控制。阈值由产品预算和噪声校准，**本包不把30%偷换成10%/15%，也不追认任何通过。**

置信边界：generation消费、字节/容量结果和所查生产caller具有直接证据；固定诊断下的局部收益有上述区间；实际stroke总体收益和所有合法算法的性能极限仍未证明。现有原40对K1/K16门、metadata实际驻留、CP0 required及M6–M8出口保持原状态。

## 扰动、失败保留与复现

- 原production与关闭时钟的诊断库做48进程校准。ARM两条production运行出现约360.9/407.6μs中位数，全部保留；6对区间很宽，不能证明诊断库严格等价。三variant主要比较使用同一诊断库；新结果只作条件诊断，不替代原product门。
- 一个process的drain中位数为0ns，首次log-ratio分析失败。保留旧分析器和日志，零值用绝对差、不算比值；同一批数据重析。
- xctrace把noinline模板内地址归为其唯一lambda，首次函数名筛选得到0样本。通过nm/atos和所有匹配frame地址范围核对，修正识别后重析同6条记录，无重录。
- 上述记录、原脚本hash和理由见[执行问题](execution-issues.json)。所有原始日志、XML、源差异、命令、退出和身份放入[原始证据包](raw-evidence.tar.gz)，校验见[清单](raw-evidence-manifest.json)。二进制、对象与原生trace bundle留本机；原product commit加两TU补丁可重建诊断库。
- 主统计运行`python3 analyze.py`；CPU分类运行`python3 analyze_cpu.py`；身份/文档/归档复核见`verify_and_freeze.py`。固定样本运行目录禁止覆盖。无需修改生产代码或重跑原全矩阵来复现此诊断。
