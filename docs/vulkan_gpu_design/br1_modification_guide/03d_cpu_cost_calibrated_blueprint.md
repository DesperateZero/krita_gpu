# 03d：按实测成本修订的 CPU 写入理想路径

版本边界（2026-10-12）：本页算法/接口与LP或早期成本数字属于各自冻结批次。当前ed0f229821已完成CPU私有结果与captured保护统一；旧prepare/publishPrivateWrite、AdoptPreparedWrite、ReplacePrivatePreparedBacking不再是当前实施目标。后续只沿[新版流程及清理账单](../evidence/br1_pipeline_refactor_20261010/unified-rw-r1/RESULT.md)与[原33×6矩阵](../evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#unified-rw-implementation)推进；不重开本页已结算矩阵。

本篇§1–§5接续 [92 §16.147](../92_br1_m6_m8_execution_baseline.md#cpu-cost-calibrated-blueprint)，以[量化报告](../evidence/br1_upstream_cost_accounting_20261007/README.md)修订算法和收益预测。设计基准为 `fb57b8b69be74a38602fb2f0cd1c6e4374b843e3`（源码树等同 `2f22452e2d`），该次设计外层父 `732dfee416bd5fbc203c3f1a80a710763b1ede47`；当时只更新设计，未改产品或新增测量，[推导记录](../evidence/br1_cpu_cost_blueprint_20261008/README.md)保存输入哈希与可复算模型。[§6](#projection-quantified-refinement)按§16.148修订B的来源与条件价格；[§7](#bulk-fill-implementation-result)及§16.149记录A的完整实施、有限比较与不升默认的裁决，该时产品为只保留pin修复和oracle的 `a918e45e02`。以下旧价格保留各自分母，不冒充当前候选新测量。

**当前清理候选为704d96e81c，[03e管理管线](03e_cpu_management_pipeline.md)已按[03g唯一账本](03g_cpu_management_cleanup_tracker.md)完成22项迁移；最新同批CPU责任账见[§12](#current-upstream-cpu-ledger)，已将§11覆盖缺口推进到任务和线程归属。** [§9](#projection-lifecycle-result)和[§10](#projection-remaining-cost-priority)保留6644249的冻结结果，不再代表当前未实施状态；原a918新鲜对照已支持旧Undo回退诊断恢复，默认资格仍未闭合。§1–§4、§6–§8保留已有设计及冻结证据，§5记录完整方案的安排，不再把已完成删量列作新收益。原 [03c §1–§10](03c_cpu_write_execution_blueprint.md)是冻结的按页重排方案，§11已完整实施并回退；不再以其条件价格表预测当前收益。

## 1. 理想路径需要改变的判断

| 原关注点 | 新证据 | 修订后的决策 |
|---|---|---|
| pin 数量大，删掉大部分应显著变快 | 2420→152兑现，ARM/Rosetta整笔收益均未确认；计划生成也收费 | 不恢复重排候选，不把93.72%调用下降映射为时间下降 |
| 复制页多，优先再删几次复制 | 当前92次整页 memcpy 仅0.0635～0.0638ms CPU | 单独消除这段数据移动，直接CPU预算只有约0.064ms；连带协议另证另价 |
| 首次页与upstream写入同量字节，单价应近似 | 当前116页逐像素fill约1.062～1.127ms；upstream116页整页copy约0.051～0.054ms | 相同字节并不等价于相同执行成本，先消除细粒度调用放大 |
| 大差距可能均摊在所有模块 | jobs-only同批额外projection4.654ms、画笔3.856ms、未覆盖1.412ms CPU | 最大已定价业务责任是projection；按冷准备—seal—commit—adapter完整责任审查 |
| 208代际相对116，理想必能删92 | 两侧版本/读者/预算/释放合同不同 | 116是upstream工作量，不是当前合法下界；92中可删量未知 |

价格均带各自测量身份：jobs-only、完整生命周期和v2子相位是独立诊断批，有观察扰动；只有原库基线与fill独立对照提供无内部观察器的时延证据。不得将几个批次拼成一笔精确账，也不能把约7.02ms生命周期诊断CPU全作为删除目标。

## 2. 方案 A：同量字节，改成块级重复填充

### 2.1 当前与理想算法

实际链为 `KisTiles3PageReplicaProvider::allocate → createDefaultTileData → allocTileData → KisTileData构造 → fillWithPixel`。当前构造已经取得独立可写页；算法不需要新owner、默认页缓存或另一笔分配。

```text
当前：对4096个像素，分别 memcpy(dst + i*b, defaultPixel, b)
目标：memcpy(dst, defaultPixel, b)           // 先建立一个完整原像素
      filled = 1
      while filled < N:
          take = min(filled, N - filled)
          memcpy(dst + filled*b, dst, take*b)
          filled += take
      原构造返回 → 原provider登记/绑定 → 原ready交付
```

在既有有效尺寸与成功分配前提下，循环不变量是前 `filled` 个像素已逐字节等于原默认像素。`take≤filled`，因此源区间 `[0,take*b)` 与目标 `[filled*b,(filled+take)*b)` 不重叠；目标也不越过 `N*b`。每次扩展只读已初始化字节，最后完整初始化原页。外部defaultPixel只在第一步读取；当前真实caller由新分配页的构造调用，实施时仍要审查全部caller及源寿命，不扩大接口的别名/无效尺寸合同。

对 `N≥1`，调用数为 `1+ceil(log2 N)`，写入量仍为 `N*b`；算法仍为线性字节工作量，改善的是调用粒度及对应执行开销。这里“写入量”不等于内存总线流量：倍增算法会读已填块，cache/预取/实现分派均可能不同，不能据逻辑字节推出带宽收益。

| 固定RGBA8用例，64×64页 | 当前 | 目标 | 可确定变化 |
|---|---:|---:|---:|
| memcpy请求/页 | 4096 | 13 | −4083 |
| 116页请求 | 475136 | 1508 | **−473628（99.6826%）** |
| 默认初始化写入字节 | 1900544 B | 1900544 B | 0 |
| 冷代际/default fill/其它copy | 208 / 116 / 92 | 208 / 116 / 92 | 设计不改变；新候选仍须实测核定 |
| job/operation/显示cut/权限/物理释放 | 原合同 | 原合同 | 不领取这些层的删除 |

原库ARM汇编已确认外部 `_memcpy` 在4096次循环内；实验库确认为12次调用加一次尾调用。不能假设编译器已自动做了批量化。`memset`只适于所有字节相同的值，不能普遍替代任意多字节默认像素，尤其非零默认值和透明像素隐藏RGB。本方案先采用任意字节模式都成立的同一算法，不增加无证据的格式特化。

### 2.2 经实测校准的预测

| 端点/对象 | 原理论预算 | 独立实验结果 | 后续预测可以使用的范围 |
|---|---|---|---|
| stroke进程CPU | 减少约0.9～1.1ms，约当前CPU的5% | 配对省1.1225ms；减少5.2366%，95%[3.6723%,6.6436%] | 同ARM/同工作量可用约1ms作复现目标；旧区间不是下一批预测区间 |
| stroke wall | 约1.1ms串行可见预算，关键路径未知，不承诺全部兑现 | 配对省0.5965ms；减少6.5637%，95%[3.6335%,9.0815%] | 约0.6ms是本实验的校准量；不能从1ms CPU自动推出1ms wall |
| redo | 诊断有56次fill，预计受益但未预报比例 | wall减少33.0534%，95%[31.0372%,35.1379%] | 支持此用例机制；不外推所有undo/redo工作量 |
| undo负控制 | 原诊断0次fill，函数直接贡献应为0 | wall减少−6.3130%，95%[−12.5163%,−0.8490%]，配对多43µs | 真实回退信号未解释，阻止升为生产；不是拿stroke收益抵扣 |
| teardown | 原诊断0次fill | wall/CPU区间均跨零 | 收益未确认，继续保留控制 |

以上是24配对/12平衡块、20,000次块bootstrap、seed261021的pointwise双侧95%区间，没有family调整。请求下降99.68%是算法删量，**不表示CPU或整笔提速99.68%**。CPU实测略超过事前区间上端，支持约1ms量级而非精确命中；观察扰动、跨阶段/cache/调度效应尚未完全分离。约1.1ms串行预算也不是端到端严格上界。

主批保留全部48过程，其中fill过程38有18次projection更新，其余47个为19。事后排除其整个平衡块的22配对敏感性：stroke wall减少7.0612%[3.9279%,9.5994%]，CPU减少5.6103%[4.0698%,6.9366%]。这说明正向结果不依赖该例合并，不能据此抹去主批工作量例外、用更高点估计替换主结果或宣布undo无回退。两组均不是新的独立复验。

该改动落在当前与upstream共有的旧函数。上游本笔116次COW走已准备默认页的整页copy，因而不同调用路径使相同旧函数在当前stroke内变热；它在上游setup或其它用例也可能被调用。以后若比较“双方共同应用改进后的实现”，应另跑对称基线，不能把固定upstream结果自动搬过去。ARM结果也不授Rosetta/GPU资格。

## 3. 方案 B：投影冷准备到交付的条件理想路径

### 3.1 保留的事实与要核实的重复

```text
当前：merge的clear/composite等原operation
      → 原range/adapter准备 → 每个冷页claim/base/plan
      → backing预留 → provider准备ready和retirement身份
      → fill或copy → 登记/binding/pin/terminal复验/private安装
      → 原body → private seal → canonical commit/adapter联合交付
      → old/exact reader退出 → 原retirement与实际free

目标：原merge/operation owner接收输入
      → 按真实读者/冻结/失败cut确定必须独立的版本与交付
      → 每个合法版本只准备一次其必要事实和实际存储
      → 首次页用方案A；有旧读者的COW仍保留完整旧版本
      → 同一事实由原owner准备一次，各真实consumer借用/复验
      → 每个必要cut一次联合交付 → 原owner持债到最后实际free
```

这是责任层目标，**还不是已证明可把clear与composite合成一个operation的实现**。当前暖pending已经复用，不能重新建设pending cache；必要preflight仍覆盖全部目标，像素开始后不得新增准备失败或把失败操作重放。canonical与adapter的共同可见性、prepare后并发状态变化所需复验、旧exact选择、budget、ready和retirement两种完成事实都保留。

对每个观测到的projection新代际，记录原owner、page/generation、first-touch或复写、前一版最后写、reader/exact capture、seal/显示cut、operation失败终点及实际释放。132代际（60 fill+72 copy）逐项归因为：语义首次页；必要冻结后的新版本；独立失败/可见性边界；或已有证据证明可由同一原owner复用的重复。只最后一类授予删除。node的76代际另列，不能用projection结论推断它。

记录合并同样先找真实consumer：相同键不代表相同权限、锁域或寿命。若binding、OwnerLedger、budget、provider和retirement记录承载不同事实，应保留；只有同一事实在同一有效期内的重复构造/复制/查验才可借用或合并。新字段或缓存必须替换旧表示并计入容量与最终free，不建第二份CPU权威账本。completion分source仅在真实live interval峰值和独占成本证据成立时另立有限候选。

### 3.2 可计算的理论收益模型

分开维护两个台账：**业务actor差额账**用于排优先级；**实现机制互斥账**用于计算可删成本。projection额外4.654ms是两侧差额，其内部冷准备报价是当前一侧的成本；它们描述同一业务责任的不同分母，不能相加。约7.02ms是当前生命周期的诊断成本，既不是当前/upstream差额，也不是可删上界；与独立v2约1.1ms fill相减后称“确定可删5.9ms”也不成立。

对已证明合法的互斥机制类别r，记录实际被删事件集合 `D_r` 与其分支/资源状态匹配的原实现独占单价 `c_e`，新增成本单列后求净收益：

```text
ΔCPU_A = 同量旧fill成本 − 同量新fill成本 + 可验证的间接净效应
ΔCPU_B = Σ_r Σ_(e∈D_r) c_e − 新准备/表示/借用/复验/释放成本 A_B
ΔCPU_AB = ΔCPU_A + ΔCPU_B − overlap_AB + interaction_AB
Δwall  = 实际任务依赖与调度重放/未插桩测量的结果
```

`overlap_AB`包括B若删掉一页时已由A优化过的fill，不能按旧整页价格再扣一次；`interaction_AB`未测不得填零宣称严格可加。必要copy与版本协议分项定价，不能用 `4ms/208` 的所有冷页平均价乘“想删的92页”，也不能将projection额外4.654ms除以72得到每个多余代际价格。

| 待优化责任 | 已知观测预算 | 当前可承诺的理论净收益 |
|---|---|---|
| 方案A默认fill | 原循环约1.1ms CPU；独立实验校准约1.12ms净CPU | 固定用例的可构造请求删量已确定，净时间待完成产品资格后的复验 |
| 仅92次额外copy的memcpy体 | v2约0.064ms CPU | 即便假设全部可删，直接数据移动也仅此量级；合法删量尚未知 |
| 冷登记/binding/pin/核验/安装 | v2约1.00ms合并观察区间 | 尚无内部合法删量与匹配单价，不能承诺正收益 |
| base、backing预留、provider身份 | v2分别约0.45～0.48、0.32～0.38、0.35ms | 分别含必要合同，不以整区间或ticket数直接领取 |
| seal/commit/adapter及operation外框 | 完整诊断约3ms（不含冷准备） | 先证明必要cut和同一事实的重复，净收益未定 |
| 真实锁/依赖、未覆盖CPU | 完整关键路径未闭合；额外未覆盖CPU约1.412ms | 未归因不等于0，也不能先填成可删除收益 |

因此当前**没有足够证据承诺再降20%/30%或回到upstream**；这不是证明没有空间。对结构候选的下一硬产出是“有合同证明的事件删除集合 + 匹配净价格 + 原owner全部consumer迁移”，随后才登记有数值的收益预测。

### 3.3 整体目标的量级校准

新原库8配对的stroke wall比中位为2.028102，达到同一参考upstream用时的示意降幅为 `1−1/2.028102=50.69%`；它只是该比值的代数换算，不是正式门阈值、未来CI或每对收益中位。旧03c的2.258倍/55.7%属于旧批次，不能当本次分母。

用**整数化2倍起点**做规划敏感度，而不拼接新旧实验：若一项改动真的使全部当前stroke wall下降s且upstream不变，剩余比值为 `2×(1−s)`。s=5%/10%/20%时仍为1.90/1.80/1.60倍；到1.0需要50%。fill实验约6.6%的局部结果显然不足以单独关闭这一量级的差距，但不能据此计算候选的新实测upstream比值。CPU约1ms和wall约0.6ms也不能分别除以另一批9.233/4.208ms宣称精确贡献份额。

## 4. 真实改动与验证矩阵

以下A/B是本篇设计行，非新阶段编号；状态由92裁决。“审查”不表示已授权整文件重写。

| 行 | 真实位置/consumer | 实施或审查内容 | 保持合同与退出证据 | 当前结果 |
|---|---|---|---|---|
| A1 | `tiles3/kis_tile_data.cc:fillWithPixel`、构造caller | 原循环替换为seed+倍增；审查全部调用及实际编译汇编 | 字节模式/边界/源寿命；无新增分配或owner；4096→13核定 | §7候选725fe331af已实现；双架汇编确认13调用；未升默认 |
| A2 | `kis_tile_data_store.{h,cc}`、`KisTiles3PageReplicaProvider.cpp:allocate`及legacy构造consumer | 审查原分配、default/copy/rows分支，补真实使用覆盖 | 非零/隐藏RGB、项目支持BPP和对齐、原默认值变化、分配失败/swap/释放；copy与rows保持原义 | 九BPP×零/非零真实Store oracle、偏移源/复用/独立页通过；原构造consumer无需迁移 |
| A3 | 原tiles3/manager/CPU mutation/painter/Reference用例、原业务fixture | 补能证伪字节与边界的oracle，运行受影响原安全/资源；只诊断构建计数 | ARM/Rosetta分开；旧/新均保留原故障；新计数不可冒用v2原库数 | 候选及最终pin-only双架各8组/4610通过；发现并修复父库可复现的last-reader pin缺陷，全部失败保留 |
| A4 | 原低扰动fixture，stroke→undo→redo→teardown | 先定位undo43µs负控制，再固定完整增量及原控制协议 | 所有原始失败/更新数保留；不采到通过；原Fresh/H4与受影响M6控制独立复验 | 同布局6.30%、静态候选7.88% stroke wall收益，Fresh/H4八桶通过；Undo非劣仍未证，候选独立保存，不升默认 |
| B1 | `kis_async_merger.cpp`、backend `fillRect/runCpuMutationOperation` | 逐代际记录clear/composite、读者/冻结/失败与交付cut，形成合法删除集合 | 像素、更新、独立失败恢复与exact读者均保持；132不是待删数 | §6已闭合56首次+4重置+36跨merge+36同merge；合法删除集合仍未证 |
| B2 | `KisPageStore.cpp:prepareWrites/beginWriteImpl`、原write coordinator | 将被证明重复的base/plan/登记/安装事实归原owner一次准备 | 全目标准备失败/此前pending/必要复验；暖路径不得新建provider | 条件设计，尚无确定补丁 |
| B3 | provider、CPU binding、OwnerLedger、budget、completion、retirement | 清点B2真实借用者/锁域/晚尾；只合并同事实同有效期记录 | ready/retire分义、拒绝不漏债、最后free才归费；不新增第二权威 | §6核定copy基准单replica/无独立before；captured=false不覆盖root retention，合法删量仍待证 |
| B4 | 原seal/commit、`PreparedTileUpdates`和manager联合安装 | 仅在B1证明的cut内合并交付/重复表达 | canonical/adapter/extent共同可见；old view、undo/cancel/晚释放 | §7核定调整层/滤镜/selection为真实中间读者；clear无同一historyOwner入口，禁止直接跨operation合并 |
| B5 | 原计数诊断、无内部观察的parent/candidate/upstream | 实施前冻结D_r/c_e/A_B，完成caller迁移和旧路径删除后固定比较 | 同内部工作量、actor账与机制账不重计，负控制不回退；结构/资源/正式门各自裁决 | §6来源闭合，§7消费者准入审查完成；B实际删除0、净收益未授，不用A填数 |

## 5. 有限实施顺序与停止条件

1. **先覆盖完整差距**：以§8矩阵覆盖已有互斥成本账的全部责任。132代际来源已经闭合，不重做相同计数；先补会改变方案取舍的同事实/同有效期、失败点和真实读者证据。必要合同与现有实现机制分别审查，不能把“承载正确性”直接写成“现有流程不可简化”。
2. **形成完整目标与补丁清单**：同一原操作内的准备、记录、seal、交付与清理一起设计；跨clear/composite合并作为额外条件优化，不作为其它路径简化的前置。逐行列出旧表达、目标归属、删除/保留、新增成本和所有consumer。A的Undo待决只限制A启用，不阻塞结构方案。
3. **按清单连续实施**：已证明等价且属于该责任的优化合入同一候选，迁移全部调用者并删除被替代路径。开发中运行受影响编译和安全测试；不能以一处有收益作为本包结束条件，也不能为凑“全部优化”越过未证明的读者或失败边界。
4. **完整候选后统一测性能**：冻结最终源码/库及有限协议，比较候选与实际父版本、候选与同依赖upstream，重测投影actor与互斥机制账、整笔和Undo/Redo/Teardown及原控制。已有24配对/12块可作业务协议起点，具体端点、架构、样本量、失败/排除规则必须在运行前登记。局部消融只用于区分仍开放的机制或回退原因，不要求每个小改动各跑一轮全矩阵。
5. **按责任覆盖结算**：每个成本桶都交付已改、保持理由或具体未解决项；保留显著缺口时本包仍未完成。合法性未证不能领取收益，也不能悄悄将该行删出范围。整体候选的净时间、残差和负控制共同裁决；观察价、条件删量、局部收益、默认启用与M6资格分开。

本篇已有A的算法和复现量级；结构部分仍需完成§8的可实施设计和迁移，不能将本次范围修订当作优化实现。通用经验见 [CONVERGENCE §4.1–§4.2](CONVERGENCE.md#copy-granularity-lesson)。

<a id="projection-quantified-refinement"></a>
## 6. 投影责任的量化深化（2026-10-08）

[92 §16.148](../92_br1_m6_m8_execution_baseline.md#projection-cost-attribution)及[冻结报告](../evidence/br1_projection_cost_attribution_20261008/README.md)已完成B的来源归因。对称粗边界四配对，投影额外CPU约4.739ms，其中composite3.584ms、clear1.151ms；setup/write/调度等净差约0.004ms。份额只属于该诊断CPU差额，不是可删wall。

原132代际在两个详细及两个追加观测中闭合为：56个不同逻辑页首次fill，4次整页default移除后fill，36次后续merge局部clear复制旧投影，36次同merge composite再次复制clear的结果。只有最后36条是同一次merge内的第二次物理准备。其整段冷准备粗价**0.469～0.491ms CPU**，其中memcpy仅0.022～0.023ms。若共同owner方案能合法复用这些pending且其它工作不变，数量目标才是132→96、copy72→36、fill60保持；不是已实现或必然可达的删量，也不是wall预测。

其余成本不能忽略：当前投影132次冷准备约2.25～2.41ms，seal+commit约1.15～1.18ms；source快照、manager和bitBlt外框还有可量化费用。每个独立私有写段都支付冷协议与终结，是当前结构差距的核心表达。单删36条重复链不会消除必要首次页的协议或全部交付费用；下一方案须完整覆盖原投影owner的prepare/写入/失败/联合交付/最后释放，并扣新增成本。

追加base事实显示72个copy源均单replica、无独立recoverable-before，当前用例不自然满足handoff机会；页级captured标记全为0也不代表可写原backing，root snapshot另经epoch retention保护，clear自身还持before。不能凭一个引用/捕获标记跳过COW。旧0.335ms剩余36链估价改用上述匹配分支粗价，保留其旧批身份，不跨批解释涨跌。21过程全部同结果/19更新，未修改产品，未授净收益或M6资格。

<a id="bulk-fill-implementation-result"></a>
## 7. 蓝图实施后的理论/实际与取舍（2026-10-08）

[完整实施包](../evidence/br1_cpu_blueprint_implementation_20261008/README.md)将A完整落为本地候选 `725fe331af`，不是再次只计数。原Store/provider和legacy默认构造消费同一个private填充函数，copy/rows/预算/释放不变；实际汇编确认每页4096→13调用。同布局24配对单独隔离fill，stroke wall下降6.30% [4.10,8.34]、CPU5.53% [3.47,7.39]，配对节省中位0.514/1.111ms，兑现约1ms CPU量级预测。完整候选另24配对下降7.88% [5.87,9.87]/6.99% [5.04,9.08]，包括pin修复，不能全算fill。

完整候选一例18更新保留主结果；移除所在整个ABBA块的事后敏感性仍为wall7.63% [5.54,9.77]。两组控制的区间均为pointwise双侧95%，未授family或M6。Undo仍含可观回退区间，完整候选配对wall/CPU中位分别多17/11µs；Fresh/H4八桶通过不能代替该负控制。**按原有限停止规则保留候选，不升当前默认填充。** 旧43µs不能被一次区间跨0宣告消失，后继先固定可接受界和测量分辨率，不追加同类样本到通过。

安全批另发现真实旧缺陷：未暴露writer先退出、reader最后退出时，物理pin释放而拥有标记残留；新writer可能多归还活reader pin。父库和fill-only均被确定性实际swap反例证伪。第一版751bceff23收束最后native终结但引入重锁，独立批stroke wall多4.12%；当前产品 `a918e45e02` 将原私有终结完整替代为持锁函数，四个caller一起迁移，删除重复writer终结和read/write退出重锁。生产+12/−17、测试+97/−0，私有签名一增一删，无新owner/字段/上层API。双架各4610安全项、Fresh/H4八桶和结构通过；最终独立8配对stroke wall下降−0.93% [−6.97,3.85]，含一例更新合并，同更新敏感性也不确定。保留理由是必要安全保证，不称已证明业务非劣或领取填充收益。

完整候选直接对同依赖upstream仍为stroke wall2.055倍 [1.928,2.215]、CPU2.011倍 [1.911,2.121]，8配对/4块，仅ARM本用例。不能拼旧2.028倍与独立收益推算新比值，更不能称已关闭主差距。

B的[consumer清单](../evidence/br1_cpu_blueprint_implementation_20261008/IMPLEMENTATION.md)明确 `startMerge` 在clear/composite之间执行original visitor/recalculate；调整层读extent、复制中间projection、执行filter，selection还需要原中间选择。原batch每次新mutation并seal，clear无与composite同一historyOwner入口。因而36链约0.48ms仍是条件冷CPU预算，合法删除集合尚未成立；简单延长transaction或公开pending并非确定方案。后继必须给所有中间读者、全目标准备、独立失败和联合安装一个完整原owner方案，再扣新增代价；若不值得，转向必要代际的同事实重复单价。现有descriptor值已共享，不重新发明缓存，也不把未覆盖成本直接填为可删。

<a id="projection-complete-responsibility"></a>
## 8. 从局部候选改为完整投影责任（2026-10-08）

本节回应“尽可能完成已发现问题的优化，再验收完整结果”。代码复核基准是当前产品 `a918e45e028c426874d9aa13d8080f2d69170d9f`，文档修订父为 `7cd33c886552058f8b1ddd7668a122b2242ce5b3`。本次没有生产改动或新测量；既有价格仍属于各自冻结批次。

### 8.1 上次蓝图不够完整的具体位置

上次已识别整条维护链，但只有A形成了可执行算法，B主要列出约束和“待证”。实施顺序先收口A、再决定B，实际把容易验证的小项变成了交付范围。另一处收窄是围绕36条同merge准备讨论B，必要首次页的单位准备成本、seal/commit、adapter和读取准备没有形成同等深度的替代方案。因此，A的局部成功没有解决最初的upstream差距问题；这不是A的理论收益失效。

统计口径同时修正：投影当前总CPU **5.322ms**，upstream **0.583ms**，额外 **4.739ms**。本轮fill实测整笔净省 **1.111ms** 覆盖116页，其中投影60页、node56页；原投影fill体仅约 **0.54～0.56ms**。不能将1.111/5.322写成“投影额外成本已消除约20%”。完整候选尚无对称的投影分项重测，不能伪造其剩余差额。

**合同必须保留，不表示现有对象数量、调用顺序、检查次数和中间表示必须原样保留。** 例如，旧读者要求旧版本稳定，并不自动要求每个consumer再构造一份相同证明；失败可恢复要求保留已发生事实，也不自动要求多份临时数组和逐层重建。反过来，锁外provider调用期间base可能变化、默认页可能实体化，真实重新核验不能只凭“字段看起来一样”删除。

### 8.2 完整目标形态及边界

本包覆盖同一真实投影更新内的CPU准备→像素写入→seal→联合交付→清理，并审查共享CPU入口受到的影响。保持原merger、mutation、publication、物理预算各自权威；不另设总owner、影子账本或常驻CPU缓存。node共享路径随实现验证，约3.86ms画笔与1.41ms未覆盖CPU仍用各自账，不混成投影收益。

```text
原merge/operation接收范围和实际读写依赖
  → 原范围准入：确定目标集合、读选择及必须保留的可见性/失败边界
  → 原mutation准备：每个必要页版本建立一份可持续消费的事实
      选择base/plan → 预留真实存储 → 初始化 → 登记/复验 → 可写绑定
  → 原像素操作：复用已准备目标，不新增准备失败
  → 原seal/publication：消费原变化集合与证明，准备必要输出
      只复验跨锁外窗口会变化的事实 → 在原边界联合安装
  → 原owner移交/释放：成功与拒绝从已发生事实继续，实际free后归费
```

这要求减少同一边界内的重复表达，并不先假定一次merge只需要一次版本或发布。clear与composite之间存在真实中间consumer；跨操作合并必须另证其读到哪版、失败保留哪次成功结果。即使不能合并，单个合法写段内部的成本仍须完整优化。可前移的准备在首字节前完成；不能前移的真实seal/commit拒绝保留原冻结/接续责任，不能将其改成“不会失败”的断言。

### 8.3 全路径实施矩阵

下面是同一工作包的责任行，不是新阶段编号，也不表示所列每个文件都必须修改。每行实施前补具体旧→新差集；当前状态均为设计审查，只有填充已有独立候选。未展开路径的PageStore/backend/ledger/binding文件位于产品 `libs/image/pagestore/`，tiles3文件位于 `libs/image/tiles3/`。

| 责任与具体文件/函数 | 要形成的替代方案及联动消费者 | 必须证明的边界 / 完成证据 |
|---|---|---|
| 范围、写段与交付次数：`libs/image/kis_async_merger.cpp`；backend `fillRect/beginMutationBatch/Private::finish` | 在原merge调用链列出每个实际中间读取和独立失败结果；分清必须分段与可共同准备的范围，清理同范围重复收集；合并合法段时同时迁移clear与composite入口 | 32 batch不是32次canonical commit；36链不是自动可删。调整层/filter/selection、并发client、旧reader均有明确选择，不能只按preset开快路 |
| 冷页base/plan/descriptor：`KisPageStore.cpp:beginWriteImpl`；`KisPageWriteCoordinator.cpp:prepareWriteBaseLocked/prepareWritePlanLocked` | 由现有mutation entry/ColdPage保存本版本需持续消费的结果；查明同一有效期内可借用的解析、查找、descriptor引用与重复校验，合并其生产者和消费者 | claim、generation、source、权限及锁外变更复验保留；暖pending已复用、descriptor值已共享，不以重复造缓存领取收益 |
| 实体与provider登记：`KisTiles3PageReplicaProvider.cpp`；`KisPageOwnerLedger.cpp:registerBacking/verifyTerminalProviderResult`；`KisCpuResidentBinding*` | 沿一次allocate→预算登记→binding取得→ready核验追踪身份、布局、物理引用和临时存储；同事实同寿命由原记录一次提供，不在每层重建 | ready与retirement不同寿命；swap、provider epoch、拒绝后的真实回收与收费仍有唯一权威；不能仅合并结构体而保留全部旧记录 |
| 默认初始化：`tiles3/kis_tile_data.cc:fillWithPixel`及provider构造链 | 在完整候选中评估已验证的块填充；旧循环只有在启用资格成立时替代，同步保留copy/rows语义 | 投影预算只取60页；任意BPP/默认字节、资源、Undo控制；A待决不得冻结其它责任 |
| 私有seal：`KisPageStore.cpp:KisPageMutationSession::seal`；`KisPageWriteCoordinator.cpp:publishPrivateWrite`；OwnerLedger `sealPreparedPage` | 当前多遍write-set、逐页publish/proof、临时overlayChanges和候选输入共同审查；让原变化集合按稳定寿命供实际消费者使用，删除可被直接消费替代的重复扫描/构造 | 不是将所有遍历机械合一。alias/removal、proof接受点、容量拒绝后重复seal、claims和writable释放次序必须正确；新增保活及峰值容量单列 |
| overlay/canonical交付：`KisPagePublicationCoordinator.cpp:prepareOverlayUpdateLocked`及prepared commit；backend `Private::finish` | 从同一实际delta生成必要metadata、root、surface及adapter输出；核定哪些重验证因窗口成立、哪些只是重复投影；同批迁移准备/安装/清理 | canonical/adapter/extent原子可见、不同匿名client与旧快照不能弱化；不把32→19当现成承诺，不把私有seal和canonical费用重算 |
| adapter、presence、geometry：backend `runCpuMutationOperation`；`tiles3/kis_tiled_data_manager.cc:PreparedTileUpdates`及clear/write caller | 追踪targets、touched/changed、prepared tiles和extent的实际消费者；同一变化集合能原位借用或移交的只生产一次，清除失去consumer的中间输出和分支 | changed的失败清空、发布后不再增长、sparse default与联合安装仍成立；跨失败边界必须保留的集合不能只因键相同合并 |
| 读侧：backend accessor selection；`KisPageStore.cpp:captureReadViewImpl`；layer/painter bitBlt入口 | 区分实际所需current/old/overlay选择及稳定期间；沿消费接口审查可避免的未使用捕获、重复选择和相同快照的保活/释放 | 18 overlay与18 before不是18份相同数据；oldData真实消费者、alias/self-source、跨线程、root retention和晚reader必须覆盖 |
| 终结及残差：上面所有临时对象/捕获析构、retirement、job外框 | 将释放放回上述成本桶及原寿命，不把阶段外尾当作已省；bitBlt其它和job残差中不能解释的部分保持可追踪 | 对应实际物理free、压力恢复、取消/拒绝/晚释放；不为减少阶段时间把工作搬到Undo或drain，不以未采到当零 |

已发现的便宜调用、读侧和adapter不会因为不是第一热点而遗漏；是否值得改以这张表内的净成本和风险决定。每个保留项必须写出真实consumer、必要寿命/边界、已比较的更直接表达及不能采用的原因。“涉及正确性”“已有测试通过”“留待以后”均不足以关闭责任行。

### 8.4 预算要覆盖整条路径，不将候选成本冒充可删空间

以投影v2独立批次的互斥桶组织预测：冷准备2.253～2.408ms、seal+commit1.153～1.176ms、operation/batch/adapter 0.563～0.736ms、clear剩余0.332～0.333ms、manager/交付析构0.169～0.196ms、capture/accessor 0.368～0.392ms、bitBlt其它0.357～0.439ms、pixel body 0.227～0.276ms、其它0.282～0.372ms。每过程之和为其5.703～6.326ms总量，不能相加区间端点，也不能拼入粗批5.322ms或4.739ms差额。

投影fill体约0.55ms只是其它详细批的局部规划价，36条冷链约0.48ms是条件毛价；这两个候选不足以覆盖主要差距。实施预测应给各桶的**删除事件集合、保留必要工作、替代成本**，不是给所有桶套一个希望达到的折扣率。

```text
整包 ΔCPU_projection
  = 投影fill旧价−新价
  + 合法删除代际的完整成本（按优化后的payload价，避免重计）
  + 剩余必要代际内部删去的重复维护
  + 保留写段内seal/commit、adapter和读侧的净简化
  − 新准备、借用、复验、保活、失败接续及释放成本
  + 有证据支持的交互效应
```

剩余必要代际的单价优化不得再覆盖已整条删除的代际；删一次交付时不能再领取其每个子项。尚无删除集合的项标记未定，不能当零汇总成“完整方案只值约1ms”，也不能将整个桶领作理论上限。新的投影差额必须由最终候选与upstream的同边界测量取得；整笔1.111ms、投影局部预算及wall收益分别列账。

### 8.5 实施完成与测试安排

完成定义是本节责任表全部有可审查处置：实现并验证的替代；有具体证据必须保留且已比较较便宜表达的工作；或仍开放的明确缺口。第三类存在时不得宣布整包已完成。“尽可能优化”以这个有限闭包为界，不无限追逐所有热点，也不以找到第一个正收益结束。

开发中按改动运行必要的编译、语义与故障测试；它们用于尽早纠错，不是每个点一套最终性能验收。完整候选形成后再做一次固定的端到端性能包：

1. 当前父版本/完整候选/固定同依赖upstream绑定真实源码和运行库。候选必须包含当前pin修复，旧725分支不能未经整合直接代表最终候选。
2. 独立诊断构建核对各桶和事件删量；性能构建无内部观察器。保留输入、像素、19次更新等实际工作量、Undo/Redo及清理断言和全部例外。
3. 完整候选对父版本测净收益，对upstream测剩余差距；架构分列。原Fresh/H4、受影响M6控制、Undo/Redo/Teardown保持既有规则，不用总Stroke正收益抵扣回退。
4. 只有预测不兑现或负控制出现新问题时，按已登记假设做有限消融；不把每行都变成新一轮24配对，不逐项重复完整矩阵，不追加到通过。
5. 最终同表交付理论与实测的投影/整笔CPU、wall、实际删除/新增、峰值容量与残差。没有达到目标就明确整包失败或仍有缺口，不能将单项有效重命名为整体收敛。

本节记录实施前的范围修订。后继统一实现和验收见§9；保留本节事前预算，不将事后价格回填为预测。

<a id="projection-lifecycle-result"></a>
## 9. 完整责任候选的实际结果与蓝图修正（2026-10-08）

候选 `6644249a4c` 已在 `codex/br1-projection-lifecycle-candidate` 完成五项替代及全部受影响consumer迁移，九行责任的处置见[实施矩阵](../evidence/br1_projection_lifecycle_20261008/PLAN.md)。原分支仍为a918，当前检出候选，默认晋升因Undo回退失败。完整[理论/实测/容量/失败报告](../evidence/br1_projection_lifecycle_20261008/README.md)绑定最终库，不使用早期候选较好结果替代最终结果。

| §8责任 | 最终方案与处置 | 数量或边界 |
|---|---|---|
| 范围/写段 | 保留clear→original visitor/filter/selection→composite的可见与独立失败边界 | 132代际不减；未声称36链可删 |
| base/metadata | 原entry/ColdPage继续复用；prepare与publish的两步输入改栈借用 | 去528次SnapshotArray控制块/数组分配；跨provider解锁后source/domain复验保留 |
| provider/实体 | 配置一次同步Ready；Payload内嵌slot索引，登记/ack/dirty/释放共同迁移 | 去132个Ready、132个slot节点请求；retirement独立，实际record费160→144 B |
| 默认fill | 原pin修复上集成块填充，所有默认构造consumer共用 | 60页245760→780次memcpy；字节数不减，细诊断0.560→0.043ms |
| 私有seal | 原write-set直接生成overlay候选最终输入，部分proof接受与retry保持 | 去32个生产者数组及其复制/free；候选自有输入跨锁外准备 |
| canonical交付 | 保留公开输入与proof验证、跨锁descriptor保活、独立epoch delta | 改为借活动map不能承诺并发GC/重基安全；没有领取整个commit桶 |
| adapter/geometry | 原changed/target/missing/presence保持各自准入/实际结果/缺失准备/删除寿命 | 相同键不等于相同事实，暖wrapper已复用；无已失去consumer的集合遗留 |
| 读侧 | accessor建立时的old/current cut保留；修复默认物化到AcquireRead间的清理解锁窗口 | 外层read栈持原map至pin登记后，无常驻缓存或新owner |
| 终结/残差 | 同步借用不逃逸，slot/dirty先解绑，物理free后完成Retire；配置拒绝恢复原source | 原源接续不新增恢复域；不把工作移到Undo领取收益 |

合计投影核算删除824次分配请求，整笔1307次；真实cold、fill、overlay数量符合预测。结构项在事前没有可靠时间单价，不能用事后总收益声称逐项精确预测。五项共用源码与最终安全/性能包；配置拒绝发现真实问题后重开固定批，前批保存且不混样。

最终ARM无内部插桩20块/40对，Stroke wall降低**9.89% [8.43,11.31]**、CPU降低**8.28% [6.71,9.84]**，配对CPU省中位1.614ms；Redo也改善。**Undo wall增加5.06% [1.20,9.10]、CPU增加4.17% [0.86,7.60]**，未通过原≤2%控制。均为pointwise双侧95%，不授多端点family或M6；双架9222安全项及Fresh/H4通过不抵扣Undo。下一启用任务必须归因这一回退，不预先把它归到fill、不继续同样批次加样。

最终粗投影父/候选/upstream中位5.133/4.422/0.398ms，剩余额外约**4.024ms**。四对节省0.528/0.684/0.809/−1.821ms，有限且含慢值，15.0%只是按边际中位数描述的差距关闭比例。不能用整笔1.614ms除旧投影5.322ms，也不能把粗/细诊断中位数相加构造精确预算。独立完整Stroke对upstream仍约1.950倍wall/1.946倍CPU，原差距目标未完成。

据此修正下一理论模型：已删集合从模型中移除；继续保留132代际的物理准备、metadata准入/发布、proof与联合安装、真实读保护和最终释放。cold细诊断self约0.883ms、seal/commit/capture包围约0.575/0.555/0.359ms仍在，但桶价不等于可删空间。下一候选必须证明新的事实/寿命表达可以跨哪些原边界复用，并计入其接受、失效、失败与释放成本；尚未证明的方案既不能定价为0，也不能承诺追回剩余4ms。

容量测量只证明物理节点少16 B，整体MetadataArena峰值未稳定降低，原process/static尾仍存在。生产净增41行、测试净增63行，没有新owner/队列/缓存；保留完整候选便于针对实际回退作有限归因，不以净增或安全通过替代启用判断。当前阶段裁决统一见[92 §16.151](../92_br1_m6_m8_execution_baseline.md#projection-lifecycle-candidate-delivery)。

<a id="projection-remaining-cost-priority"></a>
## 10. 剩余成本分组深挖：修正价格与下一完整责任（2026-10-08）

固定§9产品，按事前协议完成33个诊断过程、99 QTest通过；[原始证据与详细归因](../evidence/br1_projection_remaining_cost_20261008/README.md)及[源码消费者](CODE_INDEX.md#projection-remaining-cost-code-index)冻结。本轮产品增删0，不复测原候选资格。首次细分使投影CPU中位增加33.8%；一次有限分组补证仍有16.4%～25.2%增量，停止采样。这些桶价是观察量级，不能与§9旧4.024ms差额拼成精确瀑布或直接作为删除预算。

最重要的假设修正：未打开metadata内部时钟时，132次prepare+132次publish合计每过程0.405/0.409/0.389/0.428ms，中位约0.407ms；打开后metadata_local自身达到0.755～0.803ms。四个分组过程均264次local sequence及每一相位，无局部重试放大；当前代码只投影相关版本，不是全历史复制。因此不按新插桩的约0.8ms启动第二套CPU状态机，先追完整冷链中的接收与交接。

| 优先 | 已确认的实际工作与诊断价 | 要形成的替代方案 | 不能提前领取的量 |
|---|---|---|---|
| 1 冷准备全链 | 132次；base0.209ms、reserve0.131ms、register0.077ms；private prepare0.246ms、provider0.372ms；cold余项0.568ms仍混有binding/写权、终态/descriptor、交接/清理与观察开销 | 让同一CPU准备结果随原reservation交付稳定的布局、物理与接收事实；核对source/domain真实变化后的必要重验及实际收费。空descriptor清理解锁作为相邻审查项，不单独定义主包 | 上述不是全可删；没有证明可回收1ms，冷余项不能全部标锁/析构。已复用write-set、idempotent退休节点准备不再宣称重复分配 |
| 2 operation建立与终结 | 19次composite：范围准入0.136ms，后续batch/transaction/adopt/execution/surface约0.200ms；adapter prepare0.032ms、changed export0.004ms | 沿原owner复用已接受target/claim，减少同一作用域的表示与重复接收；清点registry、wrapper、借用和失败终结的真实消费者 | 约0.34ms只是相邻桶量级；不能外推32次batch，不能绕过iterator冲突或跨中间filter/selection reader合并clear/composite |
| 3 seal/canonical整体 | seal主要在publish/proof与reservation释放/overlay存储；commit分散在metadata preflight0.144、cleanup0.091、completion及预算0.076、provider0.069、root0.066、联合安装0.056ms | 原delta贯穿metadata/root/预算/清理，保持各独立接受点和晚读者；先证明减少哪些表示与接收次数 | public proof输入核验仅0.017ms，不能拿整个commit0.65ms预测内部直达入口收益；组4未见重准备放大 |
| 4 读选择与merge余项 | capture约0.34～0.36ms，merge余项约1.1ms，本轮未进一步细分 | 按真实source/oldData cut、overlay delta重选及释放证明可复用范围，再决定方案 | 尚未完全归因，不称全部是必要维护，不把余项都归adapter |

此顺序按目前可研究的责任规模、删量可能性和改动风险排序，不是已验证的净收益排名。每行下一步均须产出“原事实的接受点→有效区间→消费者→失效/拒绝/释放”的闭包，以及可观测的Δ查询/接收/锁交接/容量/释放数量；尚无可靠单价时保留条件模型。相关项应形成一个完整候选后统一做父/候选/upstream、机制与原Undo控制，不能每遇一小桶便另做一个优化包。现有诊断已足以降低plan选择、changed数组、独立public proof反查和metadata算术重写的优先级，但不足以承诺新的净收益百分比。

剩余差距更像多层生命周期协议及尚未拆清的外框共同构成；这比“一个状态机大热点”更符合当前证据，但不证明现有多层表示均必要或已达算法理想。数量与消费者证据较强，时间单价证据受观察扰动限制。Undo回退仍是默认启用的独立阻塞；当前裁决见[92 §16.152](../92_br1_m6_m8_execution_baseline.md#projection-remaining-cost-diagnosis)。

后继[03e](03e_cpu_management_pipeline.md)已给出十项源码对照、事实有效期、consumer迁移和反例验证矩阵：沿原ClaimSet接受事实，联合去只读COW/顺序反转、双重成员查询、重复范围/冷页claim和空锁交接。19 clone/38分配请求、132对中间锁交接、96次冷claim重入是条件数量预测，四案例仅验证实际容器行为；本节旧桶价不转为新净收益。产品及原负控制裁决保持，最新状态见[92 §16.153](../92_br1_m6_m8_execution_baseline.md#cpu-management-pipeline-design)。

<a id="cpu-residual-ranking"></a>
## 11. 管理清理后的剩余来源排序（2026-10-09）

固定704d96e81c，只复算[§16.155清理数据](../evidence/br1_cpu_management_cleanup_20261008/README.md)，无新产品修改或采样。[完整排序、置信边界与复算](../evidence/br1_cpu_residual_ranking_20261009/README.md)取代§10的“下一项”顺序。当前/upstream未插桩Stroke仍多7.7685 ms CPU（配对中位数），比率1.8649、pointwise95% CI[1.7592,1.9704]；Redo/Undo/Teardown多0.7585/0.5125/0.4735 ms。四阶段配对均值额外成本中Stroke占81.60%，不含Setup/间隙，不将中位数相加。

第一梯队为**逐代际cold准备 → private seal → canonical联合发布及释放**。当前4个观察过程208冷代际耗2.581–2.836 ms；seal+commit逐过程合计1.512–1.637 ms；完整互斥链4.129–4.393 ms。继续审查同一base/layout/physical/delta事实跨provider、ledger、metadata、root及预算的重复表示和接收，保留真实动态接受点与失败/晚free。工作桶存在性高置信，额外差距归因中等，可删净预算未定；这些当前插桩桶不是upstream差额，不能与7.7685 ms拼成份额。

第二梯队**不强行互排**：operation扣除已记录子区间后3.231–3.372 ms，含真实pixel callback/暖访问/adapter/scope；capture+merge余项1.411–1.600 ms，含多种source消费者。二者需同批必要工作价格才能比额外成本。另有8.205–8.779 ms当前Stroke CPU未被这些事件覆盖，既不能填零，也不能全部当额外管理。旧3.856 ms画笔、1.412 ms未覆盖、4.024 ms投影差额仍属旧源码，不能移入当前账。

已删19 clone/96冷claim/328对空交接及findIndex重复工作降级，不重领。当前块fill约0.083 ms，不再是旧1.1 ms逐像素问题；private metadata计入cold/seal，不能独立加价。该冻结批次的R08 descriptor搜索当时未测；后继[92 §16.166](../92_br1_m6_m8_execution_baseline.md#descriptor-search-selection-trial)确认208个base hint命中、110–114次后备搜索均首项成功，已排除当前fixture的向后遍历放大，不再列为默认待改热点。版本索引全寿命、锁、allocator及混合余项仍未取得可删除净价，“正常维护”不能代替对账。

下一先以当前/upstream低扰动job边界补同批差额，再为第一梯队或实际更大的责任建立可删除集合；不重复本包矩阵或逐容器试改。新收益只写条件式 `原重复成本 − 替代表达的接受/失效/释放成本`，不以4.13–4.39 ms观察链承诺净收益。旧Undo已诊断恢复，Teardown原控制与正式门仍欠；阶段裁决见[92 §16.156](../92_br1_m6_m8_execution_baseline.md#cpu-residual-ranking)。

<a id="current-upstream-cpu-ledger"></a>
## 12. 同批差额账补齐：将后台终结纳入完整生命周期（2026-10-09）

产品仍704d96e81c，只补外部观察。[108过程的完整报告、源/运行身份与可复算数据](../evidence/br1_current_upstream_cpu_ledger_20261009/README.md)完成一次固定主批和一次预声明追加，无产品修改。首批detail同批额外CPU为projection jobs **3.697516ms**、stroke jobs **2.314388ms**、job外 **1.298971ms**，合计7.310875ms；各占50.58%/31.66%/17.77%，不是未插桩收益或正式置信度。两边937绘画/19合成任务，数量未放大。

原约8.4ms未覆盖总量已桥接为stroke job内6.573695、merge job外框0.074297、job外1.779033ms。一次主线程/线程边界追加确认：原reclaimer **1.265625ms**、delay/wake **0.175500ms**，主线程严格区间仅约0.09ms且两边近似；线程在Stroke前已存在，不是临时创建线程的解释。线程快照窗口略宽，保留差额0.029750ms后与同批进程CPU账闭合。尚未给各类后台任务单独分价，不能把其全归metadata/history或全称空唤醒。

据此修订完整设计边界：**原版本事实从冷准备/private/canonical交付，一直追到原后台cleanup/reader/history/retirement和实际free/通知。** 前台cold/seal/commit仍为第一梯队；原后台约1.4ms必须在同包审查，不能把前台费用转移到worker就算总CPU收益。第二梯队operation真实pixel/暖访问及read/merge余项继续保留。当前callback扣cold等后约2.286ms，operation其余约0.887ms，原混合桶不能全报wrapper。

下一源码审查复用报告§5的实际生产者：publication candidate的原Data任务、history collector、read last-use、retirement queue、epoch释放、budget waiter及Store最后owner释放。对每个真实节点核对前台事实/表示、排队次数、唤醒触发、原公平batch、晚reader与最终预算归还；task计数和可删量未证时不删原异步、公平界或失败进度，不新增第二owner。`净收益 = 前后台重复工作减少 − 替代表达全寿命成本`，本轮不给新的毫秒收益承诺。

责任层账已完成，停止扩大采样；不再领取“解释整个8–9ms”或重跑已删claim/空锁/旧fill。所有慢值保持，模式间漂移不支持固定扣clock、新CI或门资格；严格裁决见[92 §16.157](../92_br1_m6_m8_execution_baseline.md#current-upstream-cpu-ledger)。

上述责任已形成[03h全生命周期理想算法](03h_cpu_lifecycle_ideal_blueprint.md)、[03i代码/删除索引](03i_cpu_lifecycle_edit_index.md)、[03j唯一28项追踪矩阵](03j_cpu_lifecycle_tracking_matrix.md)，当前设计裁决见[92 §16.158](../92_br1_m6_m8_execution_baseline.md#cpu-lifecycle-blueprint)。本页继续保存成本校准与历史预测，不再新建第二份实施状态；下一按新蓝图实施、补实际删量与净价格。
