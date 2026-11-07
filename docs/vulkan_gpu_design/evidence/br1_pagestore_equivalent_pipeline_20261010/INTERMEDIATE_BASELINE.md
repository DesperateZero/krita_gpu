# IB0：累计优化中间源码基线

**IB0之后的最新开发候选为 `1f3d4fd25e`。** [触发责任收敛及条件普通净价](intermediate-baseline/full-flow-trigger-audit/convergence/RESULT.md)已完成三个原owner内的清理；局部晚保护/已有通知有收益，H0/H1净改善未分辨，旧H1操作欠账保持。以下IB0定义不随开发提交改写。

2026-10-17。**IB0 已正常落源为产品 `ab1bf42e184d3a210a525a78605585b51067f22a`**，分支 `codex/br1-ib0-integration`。它由 e238＋handoff-lifecycle-r0 累计算法及匹配测试形成，另恢复原合同、修正正常集成细节。双架构正常构建、核心/调用者验证和结构检查已完成，具体边界见[集成结果](intermediate-baseline/integration/RESULT.md)。已有并行写压力崩溃仍未解决；本轮没有新性能计价，不改变默认关闭与 M6 资格。以下第1节保留冻结输入身份，第3节价格仍属于旧研究库。

[各轮优化汇总](../br1_pipeline_refactor_20261010/OPTIMIZATION_ROLLUP.md)解释每轮继承、替代、回退和价格；[逐轮目录](../br1_pipeline_refactor_20261010/ROUND_CATALOG.md)保留完整证据入口；[产品提交清单](../br1_pipeline_refactor_20261010/PRODUCT_LINEAGE.md)区分“历史候选”与今天已纳入的产品祖先。当前裁决仍以[92](../../92_br1_m6_m8_execution_baseline.md)为准，原33项状态矩阵不另建副本。

## 1. 精确身份与可交付输入

| 项目 | 冻结值 |
|---|---|
| 名称 | IB0，累计优化的中间源码选择 |
| 产品基点 | `e238d170d30a505a92f209874826ead056841566` |
| 累计候选证据提交 | `bcc8dabb424d36bf6a6a99db060c96f85179d2a2` |
| 最终算法源码 | `../br1_pipeline_refactor_20261010/handoff-lifecycle-r0/source/` |
| 原普通候选库 SHA256 | `6b2ed8420945a3b48e5692d3057b5049bd694cdea6036864c710b6daf59a4b9b` |
| 算法差集 | 19已有文件修改、2新增私有头，+1891/−1181，净+710行；另1个相同上下文头 |
| 测试差集 | 4已有文件修改，+915/−152，净+763行 |
| 完整可应用补丁 | [algorithm.patch](intermediate-baseline/algorithm.patch)、[test.patch](intermediate-baseline/test.patch)，目标路径相对 `krita/` |
| 文件、哈希和同批价格 | [manifest.json](intermediate-baseline/manifest.json) |
| 回放验证 | [verification.json](intermediate-baseline/verification.json)：26文件一致，两补丁可应用且结果逐字节一致 |
| 本轮性能过程 | **0**；全部价格来自已冻结批次 |

正常集成身份另见[identity.json](intermediate-baseline/integration/identity.json)，不覆盖上表研究输入：生产最终21文件 +1892/−1184，测试5文件 +936/−87；四套核心每架4017通过，含恢复的12条原合同。全部限定验收合12192条Qt测试行，PaintDevice明确排除既有并行压力崩溃方法。结构/派生物单列，不计生产删量。

复核命令（仓库根目录）：

```sh
python3 docs/vulkan_gpu_design/evidence/br1_pagestore_equivalent_pipeline_20261010/intermediate-baseline/assemble.py
```

该命令只核对冻结输入、旧库身份和临时目录补丁回放，不修改产品、不构建、不跑性能。行数采用Git diff口径。完整补丁已经包含累积差异，**不要再逐轮叠加source.diff，也不要再额外套7609或budget-changes-r0**。源码快照在旧原始归档中，已提交的ordinary-identity绑定本次全部26个输入；本次补丁使它们可从e238直接还原。

## 2. 固定纳入与排除

纳入原operation/scope范围、原行槽号写集、原native活动事实、内部紧凑身份、原结果直达consumer、暖metadata直接接受、canonical共同规则与紧凑表示、原容量/ledger跨代寿命、真实Q/T及退出接续、变化范围预算检查、共同record接纳、原D借用、直接handoff句柄和空终结表示清理。e238已有的signed父预算、带费所有权及close修复全部继承。

排除旧独立reservation/adopt、旧transaction spare与新寿命并存、r0费用宽扫描、未通过的8→16清理政策、早期撤回的page-ordered固定源/直接中间版本回收/同步退休原型、诊断探针、TLS读意图原型、有限minimum-native-resource Kernel及upstream-isolation替代库。旧实验的数量与负结果保留为证据，不携带为新的生产分支。

共同融合8198已在e238中，属于上层业务优化；本次21个算法变更全部在PageStore目录。对称业务策略和同语义工作量仍是正式比较前提，不能将此前融合1.204ms加到本次基础收益里。

## 3. 当前性能坐标：只使用最终同一批

来源：[handoff-lifecycle-r0/ACCOUNT](../br1_pipeline_refactor_20261010/handoff-lifecycle-r0/ACCOUNT.json)。arm64、K16/W16、四寿命，case3为H0、case7为H1；每格完整写1024页次，暖写896页次。65普通过程/845格、8旋转镜像块；以下是普通C/U均值，非新测量、非置信区间。

| 同批端点 | H0 IB0候选 | H0 upstream | H0差额 | H1 IB0候选 | H1 upstream | H1差额 |
|---|---:|---:|---:|---:|---:|---:|
| 完整write M | 52.294 | 6.028 | **46.266** | 38.238 | 6.030 | **32.208** |
| 暖write M | 44.475 | 4.915 | 39.560 | 31.058 | 4.912 | 26.146 |
| read M | 8.869 | 5.988 | 2.881 | 8.488 | 5.987 | 2.500 |
| 完整process M | 89.634 | 23.797 | **65.837** | 79.468 | 26.571 | **52.897** |
| write CPU ms | 3.727 | 0.413 | 3.314 | 2.440 | 0.357 | 2.084 |
| process CPU ms | 6.984 | 1.420 | 5.563 | 5.589 | 1.405 | 4.185 |

完整write指令为U约 **8.675倍 / 6.341倍**；每完成写页次约 **51,068 / 37,341条**，U约5,887/5,889条。这是包含该写阶段摊销的平均成本，**不是单页独占管理指令**。process已经包含write/read等阶段，禁止再与它们相加。

最终一轮相对父候选的净改善为H0/H1 write **0.673M/0.717M**、process **0.844M/0.787M**，八块同向；它只描述最后一轮。**IB0相对e238的累计净收益目前没有最终同批直接价，不能将历轮差值相加替代。**

最后一轮C−R write CPU反而+0.503/+0.111ms，process+0.852/+0.318ms，块范围跨零；不声称CPU收益。主格指令方向有重复块支持，但其余控制、跨架构和完整业务资格仍欠缺，不能赋一个虚构的“整体置信度百分数”。

## 4. 回退和未闭项随基线携带

| 问题 | 已有事实 | 集成后的处理 |
|---|---|---|
| 容量寿命对H1反增费用 | capacity同批write+3.948M、process+4.070M，八块同向；H0同时大幅减少 | 整包对照核算最终回收程度，保留共同寿命的同时审查实际费用；不盲目退回错误/无界版本 |
| 最后批其它控制 | 重编teardown失败case5/64/66/67；候选6个正向超线端点（case2、4、5、65、66，case4含两个端点） | 保留原样本和信号；只在正常集成身份固定后一次完整比较，不按旧小格反复扩样 |
| 当前内容/管理比 | 旧core候选完整非内容H0/H1 47.812/34.016M、比例9.3509/6.6981属于whole-fact批 | **IB0新比例未知**。不能跨批扣后续收益；更不能把C−U余额直接认作必要管理费 |
| 原四套测试匹配 | 研究R/C各4005；正常集成恢复原合同后每架4017，通过8034；原失败保留 | 已完成正常重跑与预期审核，详见集成结果；不替代未过压力入口 |
| 正常工程闭包 | 研究库依赖强制include；现已用正常CMake/Ninja构建11目标，两架测试加载正常库 | 工程集成完成；源/库身份与相对冻结输入差异已保存 |
| 资源和覆盖 | 全Store峰值/byte-time、完整压力/双架/业务与实际GPU并未由最新包全部证明 | 按真实改动补必要安全验证；最终资格继续开放 |

不能将“旧方案比当前轻”简单等价为“旧方案正确”，也不能将“新方案承担正确责任”当作新增费用已是最低。IB0是统一后的可继续开发对象，不是理论最小管理协议或最终达标方案。

## 5. 落源顺序与完成判据

<a id="h1-capacity-operation-price"></a>
**持续保留的主问题（2026-10-17用户补充）：** 容量寿命复用令H1写增加3.948M指令，而算法动作数量没有同量级膨胀。后续总成本回落不等于已解释这些操作如何降价，更不证明它们必要或已达到最小必要成本。工程集成已完成；继续串起“新增/保留操作及次数 → 同身份操作现价 → 后继实际删除或降价 → 真实合同下的必要动作与可达到最低实现价”，分别核算次数、单价、跨层放大、阶段转移和全寿命净价；未知项保持未知，不用整包回收冲销。

**管理路径续查：** [借还服务账与当前索引](intermediate-baseline/h1-operation-debt/RESULT.md)将旧合格定价批暖回退3.724662M逐块合回：轻量准入升级+1.687296M、归还已测子账+1.596446M、Idle取出+0.325696M，另有存储、原路径降价及残差。56次归还内部有896行投影/接纳；当前15个抽查操作中8个函数体仍与C1相同，部分预算与handoff实现已变。该证据支持“容量复用仍触发完整用途转换服务”的具体路径解释，不授现价或净删量。按[V2 §10.30](PIPELINE_PLAN_V2.md#h1-operation-service-debt)先完成既定正常整包对照，再在IB0一次补齐保留服务价；本轮无新性能过程或产品改动。

**集成中确认的计数边界：** `nativeDuplicatePages`只记录provider新副本；复用容量的PreserveContents复制在coordinator进行。provider计数减少不能当总复制量减少，更不能据此证明单次写已便宜；后续操作账必须覆盖这种入口迁移。本轮没有给它虚填指令单价。

1. 从e238建立可回退开发提交，将两份完整补丁落入正常目录。只解决集成/合同问题；任何与冻结候选的差异进入实际提交说明，不新增优化支线。
2. 通过正常工程构建及受影响的读写、晚reader、全D失败、取消/重试、预算与退出测试。测试计数不代替正确性，旧预期的调整逐处审核。
3. 冻结正常构建的中间提交；一次固定比较e238、集成版、同语义U，给出累计write/read/cold/warm/process/退出的指令与CPU净账，并核对外置候选是否可复现。保留全部失败。
4. 此后所有定位/预测/改动从该提交出发，既有删量不重复领取预算。优先处理完整责任的已知回退和主差额。

上述第1–2步的有限集成已按[结果与限制](intermediate-baseline/integration/RESULT.md)完成，第3步整包比较尚未执行。继承[V2 §10.27](PIPELINE_PLAN_V2.md#integrated-development-baseline)，中间开发资格与M6正式通过分别判断；已知压力缺陷不因集成变为通过。当前仍 **M6/M7/M8 0/3、calibration2/20**，原33×6矩阵前五列未变。

## 6. 文件级落点

完整逐文件哈希、来源与行数见manifest；便于审阅的表见[FILES.md](intermediate-baseline/FILES.md)。四测试来源固定为capacity-lifetime的tests-adjusted/Reference、tests/PhysicalClaim和ResidentRead，以及handoff-lifecycle/tests/CpuMutation。CpuMutation对应最终clients-r1验收，不能误取旧clients内的父测试。
