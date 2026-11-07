# CP3 全路径算法预算与工作量放大（2026-10-06）

**同一用例的合理算法工作量，已经可以按字节、页、版本输入、根路径和发布次数建立完整责任账；不能只拿 4 KiB memcpy 或一个热点函数估算。当前主要问题是同阶算法工作的实现常数和生命周期开销，以及分支选择造成的工作量放大。尚未校准全部必要动作的时间下界，不能宣布“理想应为某个精确 μs”或“所有瓶颈已关闭”。**

产品仍为 `6ffe097909e23adf3afd229a2a14e93986fae00b`，固定 M5 仍为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`。本轮没有产品或门槛变更。原 Fresh K16/native handoff 正式失败保持，本机 arm64 诊断不授予 M6 通过，不替代 upstream/真实 stroke。

## 1. 三层预算必须分开

1. **API 语义下界**：16 个受影响页、4 KiB 新输入、一次完整可见发布；要保证并发观察/失败恢复。API 本身不规定必须复制整页，也不规定每个临时值有独立 malloc。改成行级 COW、delta 表示或改变发布边界属于设计变更，不能拿这种下界直接裁决冻结 Fresh 用例。
2. **当前 Fresh 合同和页表示的必要工作**：64×64/B4，保留部分写的 before 内容和不可变观察，每页新物理副本。因而复制 16×16 KiB=256 KiB，再写 4 KiB；16 generation/seal、1 session/commit。不重复 default-fill。这层是本轮公平比较的下界，M5/current 两版一致。
3. **实现实际工作**：上述事实被表现为哪些节点、数组、保护、分配器、账本和反复查询；这里才有可删除重复工作的空间。计数不是“算法必须这样”，O(K) 也不代表常数合理。

复制逻辑目标合计 260 KiB；若按 source read 与 destination write 计数，是 520 KiB 逻辑读写，另加实际比较/索引访问。它不是 DRAM 实测流量。对交替常量输入，memcmp 第一次差异就返回，4 KiB 是比较上限，不能当实际完整扫描量。

## 2. 同一操作的完整工作账

令 P 为输入字节，S 为完整触及页字节，K 为触及页数，N 为已登记页数，V/R 为相关版本/replica 数，U 为受影响 immutable root 路径的并集节点数，A 为实际容量分配请求，G 为可证明安全的一组准入容量，D 为异步回收债务/容量状态。

在冻结的 hot first-K-page/H0 场景，页数据下界为 Θ(S+P)，管理应围绕 K 个事实及相关 V/R 处理；root/索引有路径查询、排序和有序容器成本，不能把它们称作零成本。一般安全目标是：

```text
W_target = Θ(S+P)
         + O(K log N + K log K + U log K + K·(V+R))
         + 原容量分组的预算/生命周期工作
```

这是有界工作量目标，不是运行时间等式。当前 tree 对已有键的替换没有旋转/新键插入，原根形状保持；连续前缀的稀疏 U 很小。固定库的后台 D、reader protection、实际 arena/allocator capacity 也必须纳入时间与存储模型。

| 原责任/完整路径 | K16/N1024/B4/h1 合同或源码工作 | 实测/定位 | 理论判断 |
|---|---|---|---|
| 输入/范围/transaction | 16 key、一次范围、一事务；execution lookup 二分 | 1 session/commit；`Private::find` 为 lower_bound | O(K log K) 或批量遍历；无理由复制 N 个页数据 |
| before-read/输入比较 | 每页解析一次 before 数据，读 binding/pin，比较到首差异 | read 整段 CPU 略优于 M5 | 包含 O(K log N)/索引/保活；非当前净回退主因 |
| Fresh payload | 16 副本、256 KiB before-copy+4 KiB 输入 | 98 进程全部计数吻合；原 CPU pixel copy 约7–10 μs | 64倍输入放大是页粒度设计成本，两版同量，非新增回退 |
| native provider/物理账本 | K 个新 payload/binding、logical/physical 身份和晚 observer/retire | 排除收费/heap后的 provider 约19 μs，owner ledger约11–13 μs | 不同实际 lifetime 不能随意合并；索引与注册遍数需有原 consumer |
| 局部 metadata/working state | 两局部序列/页，3K 局部版本输入，K mutation-base输入 | 两版均32/48/16；完整 snapshot导出0 | 没有观测到额外全页历史扫描；同样状态动作的表示成本仍可过大 |
| seal/proof/发布准备 | K seal/proof，提交约2K publication版本输入 | 32 publication输入、16 publication页，微量revision retry另保留 | O(K·相关V/R)+索引；多次 guard若保护不同 unlocked interval并非同义重复 |
| epoch root | 连续前16页只需22个 union-path节点；M5逐键复制150节点 | 当前 sparse源码模型22节点/44存储请求 | 当前 sparse算法已改善；dense规则另见下节 |
| 容量/预算/收费 | 实际容量、两级账本、失败回滚、公平及最后free | 原 steady约524请求、988 full fits、446套两级prepare/settle | 准入按实际容量不可删；逐节点反复完整政策不是语义下界 |
| allocator/reference propagation | 原尾需要 accounting owner 保活；短命值由原外层owner保护 | 原约6157 deref、仅48 retained deallocate | 引用周转与物理free分开；应审查短命对象图，而非仅一个map |
| root/version/payload退休 | K superseded代及U旧root节点，原 pin/last-use/预算尾处理 | 有主线程约3 μs及并发后台CPU；最终drain未测 | 延迟释放会改变D和临时容量；不能把后台工作移走当删除 |
| 调度/锁/宿主 | 需要的同步/公平，以及实际阻塞/抢占 | wall与thread/process CPU分列 | wall−thread不等于锁等待，process−thread不等于最终drain |

表覆盖全部原操作责任，但时间不是简单把独立小测试相加。old/new、publish/rollback、foreground/background、parent/child 必须按同一完整语义记账。

## 3. 一次固定矩阵，而非逐点试实现

[事前协议](protocol.json)：N64/N1024，K1/2/4/8/16/32，B4/h1；另两个 B16/h1、B4/h64 点。3 个顺序平衡 current/M5 时间块（84进程）及1个完整 current调用数量块（14进程），共98顺序进程；没有自适应补点、并行 benchmark/profiler/build 或改门。复制 helper 只扩CLI K验证、在时钟外读取已有metadata计数；原公有 writeBytes、setup/warm、交替数据和验证逻辑保持。[分析源](analyze.py)、[全部结果](results.json)、[模型与所有残差](algorithm-budget.json)可复核。

每进程均像素/extent/工作量正确、正常退出/reaped、实际库加载及前后源/库身份通过。计数复用上轮同源独立 budget TU 库，无每入口时钟；有计数的时间不纳入未插桩时间拟合。两版原 TU/fixture 实际均为 `-O2 -g -DNDEBUG`，没有用 Debug 对 Release。三块只作描述，不提供原40对统计资格。

**像素量、generation、seal、session、commit 的预测误差均为0；局部metadata在全部98进程均精确是2K序列、3K版本输入、K mutation-base输入，snapshot导出0。** publication约2K/K页，真实重验/竞争引起的少量额外输入保持，未强制抹成整数。

未插桩每 op 主线程CPU三块中位（μs）：

| K | N1024 M5 | N1024 current | N64 M5 | N64 current |
|---:|---:|---:|---:|---:|
| 1 | 31.29 | 30.82 | 29.61 | 27.99 |
| 2 | 44.87 | 46.12 | 42.24 | 40.15 |
| 4 | 71.15 | 67.14 | 69.31 | 62.42 |
| 8 | 120.89 | 122.77 | 113.82 | 112.47 |
| 16 | 207.15 | 238.38 | 191.40 | 245.16 |
| 32 | 412.51 | 467.66 | 354.56 | 454.54 |

描述性 `a+bK` 拟合：current斜率约14.0–14.1 μs/页，M5约10.4–12.2；current截距较低。N1024 current最大CPU残差约4.06 μs，N64约11.21 μs。R²高不证明每个分支都线性、不是理想时间，也不授予精确cross-over页数；K8残差及所有噪声/范围保留。结果支持“每页实现成本增加”而非一次固定分配解释所有回退。

## 4. 源码算法模型解释了 dense 分支突变

[当前 prepareCommit](../../../../krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:1204) 沿用 `K >= ceil(N/4)` 的 dense 规则；dense遍历/重建N页，sparse已经改为批量 union path。M5 sparse还是逐key path-copy，沿用旧密度启发式对新批量算法不保证成本最小。

从初始化 balanced tree 和已有键替换直接算 root 构造量：

| N / K | 可用 sparse union-path节点 | 当前实际选择/节点 | M5选择/节点 |
|---|---:|---:|---:|
| 64 / 8 | 11 | sparse 11 | sparse 45 |
| 64 / 16 | 18 | **dense 64** | dense 64 |
| 64 / 32 | 33 | dense 64 | dense 64 |
| 1024 / 16 | 22 | sparse 22 | sparse 150 |
| 1024 / 32 | 37 | sparse 37 | sparse 295 |

该用例dense仍满足N≤4K，并不违反O(K)上界；但N64/K16把18个受影响节点变成64个，构造量约3.56倍。它是由选择策略导致的可明确建模的放大，不是发现一个热函数后猜原因。对native N=K，dense N节点与union K节点相同，本例不能据此判所有dense均有问题。

当前 [makePageRoot](../../../../krita/libs/image/pagestore/KisImageEpochReferenceModel.cpp:190) 分开准入node和shared control（每节点2次），dense另有1个manifest buffer。根部分理论 control请求为 `2R+I_dense`，对应两级 fits 为 `4R+2I_dense`。

**跨N数量验证**：从N1024首次写入减去上述根请求，得到该K的非root参考量；再按N64根模型预测。6个K点的control allocation与fits差额共12项，误差全部0。K16：N1024首次492请求/924检查，N64首次577/1094，差额85/170正好由64节点、22节点和dense buffer解释。此为运行后源码推导并在已冻结矩阵中的跨N验证，不冒充事前整体绝对成本预测；非root参考量仍来自实测。

原来纯 `a+bK` 调用模型在N64的K8/K32留出点错约14%–17%；加入真实dense/sparse分支后首次跨N差额闭合。steady差额仍有容量/清理/重验残差，最大每op约2.62个请求/5.23次检查，模型明确保留。**不能再用一个每页平均malloc/fits成本乘到所有N/K场景。**

## 5. 还有哪些算法与表示放大

- [preparePublicationImpl](../../../../krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:2421) 对每个唯一输入扫描已有entries检查重复，恰有K(K−1)/2次key相等比较：K16为120，K32为496。排序/有序批次唯一性可有不同算法，但实际 CPU 权重尚未单独测定；它是明确的复杂度缺点，不自动是K16主瓶颈。
- 原完整预算检查对每次MetadataArena/CpuRam容量遍历7类×4域及aggregate/durable。约446套逐对象双级prepare导致约892次完整检查；算法只要求安全地准入实际容量，没有要求每个临时节点重复所有不变政策。可合并的G须按原真实lifetime/失败/公平/限额证明，不能拍脑袋规定“应只有两次检查”。
- 两版局部状态/发布版本数量相同，current却有数千allocator owner原子引用归还。这是表示和生命周期传播层的放大；working replica/result、projection、publication、root/node/control均在同一对象图中。只优化一个容器不覆盖这条链。
- per-generation读link、physical/logical索引、completion、prepared proof、retire及晚weak/control是不同consumer。应按唯一事实与真实寿命统计重建次数，统一消除重叠表示；不能为少malloc删除stable pin、别名基数、独立保护或晚费用。
- H0不等于“没有旧版本/后台”：操作内部before/transaction根和异步D仍在。跨状态/容量分支没有闭合的steady残差，不能当随机噪声删掉，也不能直接判成某一个锁。

## 6. 时间预算与可删除上界

从[原库互斥CPU采样](../br1_cp3_management_attribution_20261006/cpu-attribution.json)把整次K16主线程CPU拆成同一张账（2s份额×6s CPU/op的量级投影，非精确阶段wall）：

| 互斥机制 | current约μs/op | 判定 |
|---|---:|---|
| pixel copy | 7–9 | 冻结Fresh的必要字节量；无新增放大 |
| budget政策/账本 + storage owner/charge glue | 64–66 | 集中管理成本；包含真实保证，非全可删除 |
| physical heap | 30–36 | 已明显小于M5约65；包括payload与control，不能再加inclusive malloc |
| metadata/working state | 32–37 | 逻辑工作量相同，表示/临时对象仍有优化空间 |
| write protocol/claims | 44–49 | 必要guard与重复事实尚需分解，不统称冗余 |
| provider/native lifecycle + owner ledger | 30–33 | 实际身份/注册/索引责任，排除了上述收费和heap |
| epoch root | 约3 | N1024 sparse算法已改善；N64 dense另属不同形状 |
| read view、foreground退休、adapter及其他 | 约20–27 | 全部留在账内，不能忽略小桶或移后台宣称删除 |

该分区总和按每份样本算术闭合到原主线程CPU；unsymbolicated leaf约2.5%–3.1%按caller保留。它覆盖“时间花在哪”，不等于已知每桶的必要/冗余比例。

完整时间模型需要：

```text
T_cpu = c_copy·(S+P) + c_lookup·L + c_state·M + c_root·R
      + c_alloc·A + c_budget·B + c_ref·F + c_lifecycle·E + ε_state
T_wall = 主线程工作 + 真实依赖的阻塞/调度（后台可并行）
T_lifecycle = 整体工作、尾债务与最终drain，另定义联合端点
```

固定B时S与K成正比，各管理计数也大体随K，**一个漂亮K拟合无法辨识全部c系数**。本轮B增4倍，currentCPU238.38→262.06 μs（约+9.9%）；full input h64时237.19 μs，因256 KiB直接初始化替代before-copy，不是内部字节增64倍。支持管理主导，但不是已测DRAM带宽或精确像素系数。纯4 KiB/256 KiB copy控制只校准像素量级，不能从完整Fresh直接相减成纯管理。

因此合理算法预算可给出“256KiB before-copy、4KiB输入、16页事实、48局部/32发布版本输入、22root节点、一次发布”，而理想总μs还不能凭算法理论编造。必要索引、同步、原尾责任的系数/下界仍须在完整候选内校准；当前实现CPU约238 μs不是它的理论下界。

## 7. 下一实施必须领取完整模型中的责任

1. 把原 operation→provider/metadata→seal/commit→retire 的对象/容量/lifetime图作为一个设计输入；原逻辑输入数量已吻合，优先消除重复控制表示、逐对象完整收费及短命引用传播。候选须一次给出覆盖哪些A/B/F/E、哪些原consumer保持、哪些完整对象移除；不按sample热点领取一个map或一个allocator。
2. 以真实root工作量比较批量path-copy与dense重建，重审旧密度启发式；K16/N64的46个额外root节点是可验证局部缺点，但不冒充N1024主门的全部修复。不能重领已经关闭的batch root实现，只审查选择策略与剩余实际容量责任。
3. 对K²输入去重、相关版本/保护查询和必要重复guard给复杂度与成本上界。上界小于缺口的点只列次要项，不把几个轻微改进当主性能包。
4. 每个完整候选都报 `ΔA/ΔB/ΔF/ΔR/Δbytes` 和保守收益预算、剩余模型残差，随后一次因果验证。只在预测工作下降且未插桩CPU/wall跟随时继续正式原协议；不自适应补样本直到通过。
5. 等待/后台/实际capacity仍有残差时，补的是统一账本的缺失状态变量/联合端点，不开启一串盲猜实现。全部必要下界+剩余可优化上界无法承担缺口时，才讨论改设计或事前重校门槛。当前没有证明只能积累零散优化，也没有证明原门槛必然可达。

**本轮交付是全路径算法预算、实际工作量闭合、分支模型及可复核剩余项。** native handoff共同成本分母、Rosetta、实际stroke和完整drain未由该矩阵授予结论。CP3/M6仍未通过，persistent默认关闭。

## 复核

`analyze.py`可复现所有工作断言、每个cell分布、预注册affine训练/留出误差及后续源码root模型；没有丢掉M5 K1/K32时间离群结果。`raw-evidence.tar.gz`含98份stdout和每进程结果，按`raw-manifest.json`逐member核验。最终`evidence-manifest.json`绑定协议、源、数据、构建命令/身份、源模型文件以及引用的原库CPU/成本证据；对象/库/probe不入Git。两个初次未加入metadata读数的构建未执行进程、未用于该结果，最终两份grid2 helper绑定实际源码。
