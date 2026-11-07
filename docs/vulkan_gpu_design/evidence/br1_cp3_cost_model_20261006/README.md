# CP3 实际工作量、成本模型与门槛可达性审查（2026-10-06）

当前产品 `6ffe097909e23adf3afd229a2a14e93986fae00b`，固定 M5 `5173c807c87bb1619325249a07a8b4f4f8f09f09`。本轮没有修改产品、门槛或阶段资格；按用户要求先诊断工作量与可达性，停止直接从采样热点选择下一容器优化。当前裁决见 [92 §16.126](../../92_br1_m6_m8_execution_baseline.md#cp3-cost-model-review)。

**结论：现有数据支持优先排查逐页写前准备和共同发布协议，尚未形成完整的回退因果账。不能认定没有瓶颈、只能靠零散优化；也不能认定 20%/30% 门槛已经被证明不可能。此前 allocator 请求减少、全线程采样栈与局部通过，不能替代这两项证明。**

[有限协议](protocol.json)在运行前冻结。[源码](public-work.cpp)仅使用原 manager 测试 friendship、生产 writeBytes 与现有计数器，不增加产品接口；[native 粗分](native-cuts.cpp)保留原 fixture 的 exact before、实际地址、物理增量和退出检查。沿用实际 target 编译参数，current/M5 分别按各自头文件和库链接。144 个顺序进程、2128 个结果均正确、正常退出/reaped，源码/运行库前后身份一致；[全部结果](runs/results.json)、[派生分析](cost-model.json)、[分析脚本](analyze.py)保留失败停止规则与全部样本。四个独立诊断块只报告描述性分布，不追加到原 40 对正式样本或授予通过资格。x86_64 在此 Mac 通过 Rosetta 运行（`arch -x86_64 sysctl -n sysctl.proc_translated` 返回 1），不是另一台 x86 硬件。

[原始输出附件](raw-logs.tar.gz)按[逐 member SHA](raw-log-manifest.json)完整核验，[分析身份](analysis-identity.json)绑定本报告、派生脚本、数据及编译命令。

## 实际工作量与算法预测

页面固定 64×64，B 表示 BPP，K 为本次触及页数，N 为总页数。部分页高度 h 的输入字节为 `P=K×64×h×B`，完整页集为 `S=K×4096×B`。

| 用例 | 有用输入 / K16 B4 | 实际路径与端点 |
|---|---:|---|
| 原 public Fresh H0 | 4 KiB，一行 | 保留旧页的部分写；每次隐式 seal/commit；循环没有显式 dm.commit，不代表没有发布 |
| 原 public H4 | 256 KiB，整页 | full-payload 初始化，history commit、逐页 sentinel 读和有界 purge 在计时内；undo/redo 检查在外 |
| 原 native Fresh/handoff | 256 KiB，整页 memset | MutableGuard PreserveContents 首次准备 → seal → canonical commit；exact before reader 两组都保留 |
| 原 public kernel | 256 KiB，整页 memcpy | 预先持有 read pin 的直接复制；不能从只写 4 KiB 的 Fresh 中直接扣作纯 M |

public Fresh 初始 N 页在计时前写满、commit、逐页 warm；循环固定重写前 K 页，N1024/B4 的初始 payload 为 16 MiB，热改写页集仅 256 KiB。不是每次处理 16 MiB，也不是随机全图写。

源码的部分页分支选择 PreserveContents，provider 原生 duplicate 64×64 页。**first 与 steady 所有已采集区间，当前/M5 均与下列预测完全相符：每次 K 次 duplicate、K 次 generation、K 次 seal、1 次 session、1 次 commit；preclone hit=0，foreground copy=S，default 初始化=0。** K16/B4 因而每次复制 256 KiB before，再写 4 KiB 输入：额外 before-copy 是输入的 64 倍，复制的逻辑目标字节合计 260 KiB、是输入的 65 倍。计数器覆盖的工作量预测误差为零。

该放大两版相同，不能解释当前相对 M5 回退。它是现有部分写/不可变观察端点的行为，不凭本用例判为错误；减少重复段 COW 必须沿 M7/M8 的安全语义，不跳过旧 View 或把每次公共发布改成未发布写。若实际 stroke 无新的冻结边界却随每个 dab 重做，则按每页每段至多一次必要 COW 的原合同另行定位。

数量相符只覆盖列出的计数，不包含全部 tree/hash 查询、allocator 或锁次数。此前没有建立经过校准的理论时间预测，因而不能诚实地给出“理论耗时与实测差多少百分比”；仍需给成本系数、缓存/并发条件和误差范围。不能用数量账相符冒充性能模型已闭合。

这些是 provider 逻辑复制量，不是 DRAM 实测流量。cache 命中、write allocate、分配缺页和后台工作仍未知。交替常量数据还会让 memcmp 在首次差异处提前退出，不能把整块比较字节上限当实际扫描量。

## 控制变量后的结果

arm64、无诊断时钟，每格四个顺序进程；以下为每完成操作 wall 的中位值（μs），不是原正式门禁的替代数据。

| N / K / B / h | M5 | 当前 | 用途 |
|---|---:|---:|---|
| 64 / 1 / 4 / 1 | 37.31 | 34.02 | 固定小 N 的 K1 |
| 1024 / 1 / 4 / 1 | 39.77 | 37.99 | 独立增加 N |
| 64 / 16 / 4 / 1 | 232.16 | 270.77 | 小 N 也观察到 K16 回退 |
| 1024 / 16 / 4 / 1 | 257.00 | 271.91 | 原 K16 形状 |
| 1024 / 16 / 4 / 64 | 253.51 | 268.89 | full-payload 初始化，before-copy=0 |
| 1024 / 16 / 16 / 1 | 276.02 | 297.06 | COW 实际字节从 256 KiB 增到 1 MiB |

原两桶同时改变 N/K，不能从它们单独认定 K 或 N 因果。交叉后，当前 K16 在 N64/N1024 都慢；N 增 16 倍时当前 K16 中位 wall 仅变约 1.14 μs，不能把这次回退主要归到全画布扫描。只有两个 N 点且有噪声，**不据此证明整个实现没有 O(N) 路径**。M5 N64/K16 的四次范围为 220.74–361.15 μs，全部保留；不对两个 K 点拟合直线并宣称已验证复杂度。

当前 B 增四倍时实际 COW 字节也增四倍，wall 仅增加约 25.16 μs/9.3%，thread CPU 约增加 9.6%。支持“本场景不是单纯像素字节吞吐主导”，不能拟合为已校准的 DRAM 带宽。h1→h64 会从 COW 切到 full-payload，内部完整页初始化量并未增 64 倍；不能用输入量增 64 倍而耗时相近直接推导所有额外时间都是管理。

同输入字节、相同 K 个预绑定目的页的复制控制：4 KiB 约 0.28 μs，整页 256 KiB 的按行复制约 6.50 μs。前者相对 public 271.91 μs 相差约三个数量级，说明“只按最终输入复制时间估算”的预算漏掉绝大部分操作。但该控制没有 COW、allocator、PageStore 观察语义或退休，**不是同义管理对照，也不能相减后把差值全部称为纯 M**。

当前原形状 K16 的主线程 CPU 约 229.55 μs、process CPU 约 345.82 μs、wall 约 271.91 μs；M5 为 200.85/324.76/257.00 μs。像素计数一样而当前主线程工作增加，管理路径是优先调查对象。`wall-thread` 包含调度、抢占和阻塞，不直接命名为 mutex wait；process/thread 差含其他线程，尚未测完整 drain，不授予生命周期资格。

## 能定位到什么程度

无产品埋点改动的 native exclusive cuts 对每个 instrumented 样本算术闭合；中位阶段不要求相加等于中位 total。K16 handoff：

| 区间 | arm64（μs） | x86_64/Rosetta（μs） |
|---|---:|---:|
| transaction/session 起点 | 0.67 | 0.92 |
| 逐页 beginWrite，含候选/claim/retag/准入 | 60.62 | 93.81 |
| 实际 memset 及紧邻有效性检查 | 2.65 | 5.64 |
| seal | 36.81 | 52.40 |
| canonical commit，含 preparedPages 导出 | 44.54 | 66.75 |

按逐样本比例统计，beginWrite + seal + commit 占 instrumented handoff wall 中位约 **96.5%**；seal+commit 约 **55%/54%**。这已把调查范围压到两个大责任区间，而不是证明某一个收费函数占同样百分比。

cuts 开/关中位总时间在 ARM K16 handoff 上相差约 **10.3%**，Rosetta 上约 **5.5%**；ARM K1 Fresh 甚至出现负差，说明排序/状态/噪声也在影响。以上只能作粗定位，不能替代原 40 对延迟、计作无扰动因果占比或收益。诊断层剩余的算术 closure 也不代表已经建立理论下界。

现有 opt-in recorder 在 public K16 内提示 packed write prepare、compare、range admission；prepare inclusive 中还有 provider。current 的 profiled prepare 约112 μs、provider 子区间约39 μs、compare约17 μs，而 publication/finish 总区间有所改善。**parent/child 有重叠，且 current/M5 时钟密度不同；不把这些值相加，不以它们相减声称已经解释约22 μs正式回退缺口。** 下一 provider 候选仍只是待验证假设，不能继续由全线程 sample 计数认领一个实现。

## 门槛的理论依据与实际缺口

[92 §6](../../92_br1_m6_m8_execution_baseline.md#6-验证性能与删除门)的 handoff 20%/30%、Fresh 吞吐不劣于 M5 的 98%、metadata 驻留25%是现行工程要求。活跃入口没有给出 handoff 20%/30% 的已校准成本推导；39 则明确要求 micro 校准系数、端到端 trace 裁决和事前冻结 M 容差依据。

比较口径与统计执行是可复核的；收益目标值的可达性论证仍缺失。2% 是允许回退多少的工程容差，不能把它当物理定律；当前 Fresh gate 保护的是 M5，不是成熟 upstream。同域完整操作的 upstream 1.3× 上限也不是纯 M 容差。

第一性模型必须至少写成：

```
T_Fresh = C + F
T_handoff = C + H
收益 r = (F-H)/(C+F)
```

C 是匹配后的共同工作；F 是 Fresh 独有 allocation/copy/管理；H 是 handoff 独有候选/proof/claim/retag/恢复管理。变体共同阶段中的差异也必须归账，不能假定公共函数同名就等耗时。**消除 before-copy 和新 payload 不代表消除 F 全部，更不代表 H=0。** 达到30%须净省 `F-H >= 0.3×T_Fresh`；只证明“零复制”不足以证明30%可达。当前观测支持共同管理很大，但没有实测安全下界，不能宣判目标不可能。

从原冻结40对结果计算的描述性预算（不替换配对 estimator/置信下界）：

| 目标 | ARM | Rosetta |
|---|---:|---:|
| Fresh K16 的配对块绝对缺口中位，达到98%边界 | 约21.79 μs/op | 约0.42 μs/op |
| handoff K1，Fresh 中位固定时还需减 | 约2.32 μs/op | 约3.65 μs/op |
| handoff K16，Fresh 中位固定时还需减 | 约27.65 μs/op | 约39.56 μs/op |

Rosetta Fresh 点估计接近边界，原单侧下界0.9648仍失败；不能只省0.42 μs便承诺正式过门。handoff K16 缺口约为现有 handoff 的20.2%/19.0%，而不是再削几个请求就默认补齐。

**共同路径优化会同时改变 Fresh 分母。** ARM 原中位 Fresh155.59/handoff136.56 μs，净差约19.03 μs；若只让两边等量减少且净差不变，要使比值达到30%，需共同减少约92.16 μs，而不是27.65 μs。后者只在 Fresh 不变、handoff 单独降低时成立。30% 比值不能单独成为每次公共路径优化是否有价值的裁判：同时大幅加快两组也可能仍不达到比例目标。保留原失败，先补可达性和实际产品预算，再讨论是否需要正式重设预注册门禁；不得因本轮未达标直接降低门槛。

## 后续排查和退出规则

1. **先锁痛点和基线。** 当前 primary pain 是 protected Fresh K16 与固定M5的回退；native handoff 收益是另一个独立问题。原40对失败冻结，不以本轮4块结果替代；upstream/stroke/input-to-visible、完整drain、metadata驻留分母继续单列欠项。
2. **形成数量账与互斥时间账。** 当前数量账已经核实；时间账沿真实 operation → range/read/prepare → provider/metadata/claim → seal/commit → inline/async retirement 划分。每项写明次数、字节、CPU/wall、包含子项及新增/共同责任；parent和child不能重复收费。先验证时钟扰动、锁等待和后台归属，不能从全线程栈比例或malloc次数估毫秒。
3. **再验证机制。** 对逐页准备的候选，固定 N，在额外独立诊断中用至少三个 K 点检验固定/每页成本；必要时固定 K 改 B/输入覆盖率。检查重复准入、相同事实多次解析、收费/保护/注册生命周期是否重复，沿当前源码与M5同义分支比较，不先选容器。provider、metadata和publication仍是原责任，不增加owner或扩大恢复域。
4. **实施前必须报预算。** 一个安全等价候选需给出实际被删除的工作、现有独占成本、可节省上界和保守预期，并与约22 μs Fresh缺口/变动分母下handoff目标比较。上界明显小于缺口时，不能作为主性能修复包；其独立价值另列。不能将三次malloc的减少乘以未经测量的“单次allocator成本”。
5. **一次因果验证后再正式验收。** 冻结父/候选身份、同场景顺序平衡，以关闭 profiler 的结果检验预测差额；收益远低于预测时修正模型和归属，停止继续猜下一个容器。只有明确修复覆盖缺口及余量，才跑原阶段正式协议；不重跑CP1长矩阵或扩样直到通过。
6. **用下界决定改设计或改门槛。** 若匹配后的必要管理/像素/同步下界加上最优候选仍越目标，才能判定局部优化不足，转向原业务段复用/批量责任，或提出有产品预算依据的新预注册门槛。只有剩余可优化上界小于剩余缺口且没有结构重复，才有证据讨论“只能积累小优化”；目前没有这项证明。

本轮成本模型仍有未校准系数和粗区间，完整 causal closure 未完成；它已经否定“输入只有4 KiB所以很便宜”“零COW自然等于30%收益”“sample热点或请求数足以解释回退”三种推法。下一步的约束是**先证明可删除工作能承担预算，再决定实现**。
