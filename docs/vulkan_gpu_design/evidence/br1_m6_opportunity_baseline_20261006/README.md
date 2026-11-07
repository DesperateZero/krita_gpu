# M6新门首轮基线实测（2026-10-06）

按[92 §6.1](../../92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)事前冻结协议后，完成 **62个preflight + 2,880个性能进程，共2,942个运行进程**。本包只建立新基线和下一修改责任，生产代码改动0；产品仍为 `f0c40a5d195f1c20a0f915faaef18b1f3ee5b575`，文档起点为 `1be6fd7623c06da12474dc9c6cfa535e46702b4a`。

**M6仍未通过。** 同一开关库内命中4/4桶正收益；miss只有3/16桶通过，12桶明确回退、1桶证据不足。开关库对原产品库的等价校准仅1/8桶成立，故同库命中结果暂不授予生产性能资格。原生产库相对固定M5的Fresh和history八桶全部通过。metadata实际驻留≥25%的同义分母、CP0完整required及适用构建资格仍欠。旧20%/30%协议失败保留，没有改旧报告或改标签追认。

## 实验身份与计时

- [protocol.json](protocol.json)、[freeze.json](freeze.json)在正式样本前冻结样本量、顺序、估计量、bootstrap/seed、失败和停止条件。每桶40对进程，顺序平衡且串行，无profiler和阶段计时；没有排除慢样本、追加到通过或阈值修订。
- [selection-control.patch](selection-control.patch)只在一份复制的WriteCoordinator TU加入证据专用TLS开关，在`queryMutationBase`前禁用`discoverBefore`，其余374个生产对象复用。off走原安全Fresh；on正常选择。源代码和原生产库均未改动。差异、命令和对象哈希在原始包的`selection-image/identity.json`，构建工具见[prepare.py](prepare.py)。没有将控制开关提交到产品。
- [baseline.cpp](baseline.cpp)：64×64、B4、N=K、H0 history roots，同时保留一个exact旧View；Preserve后写满输入。从`beginCurrentTransaction`到mutation/seal/canonical commit计wall。每进程8次warmup、64次测量。setup、独立before创建、全像素验证、blocker completion、close与drain分别在主计时外记录；完整fixture生命周期不等于真实stroke E。
- 命中与三类blocker两边都预先持有两个**分别初始化**的exact G0副本；single两边都只有一副本。记录实际pointer identity命中、provider payload、copy/allocation工作量以及每预算类live/reserved/peak；吞吐按真实完成操作数/测量区间之和计算，不取中位延迟倒数，也不宣称饱和吞吐。
- arm64为本机原生，x86_64为**Rosetta**，不是原生Intel。所有结果只对该CPU/依赖/工作量成立；没有GPU测试。
- 固定M5为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`，沿用原同依赖二进制、公共Fresh/H4 fixture与各自250ms完成率规则，**本包重新采样**。[reused-tools.json](reused-tools.json)记录继承脚本的哈希及路径改动；未用本包native微基准替代原控制。

## 命中：同库4/4桶成立，生产资格待校准

40对/桶，配对log延迟比的中位数，20,000次bootstrap，seed 261006；单侧98.75%下界，每个family按Bonferroni名义覆盖至少95%。下表为同开关库的off Fresh与on handoff，边际延迟中位数与配对节省不是同一个统计量。

| 架构 | K | Fresh / handoff μs | 延迟降幅 | 单侧下界 | 配对节省 μs |
|---|---:|---:|---:|---:|---:|
| arm64 | 1 | 12.677 / 11.552 | 8.93% | 7.94% | 1.114 |
| arm64 | 16 | 123.969 / 100.437 | 18.80% | 17.26% | 23.677 |
| Rosetta | 1 | 20.229 / 18.427 | 7.82% | 5.63% | 1.531 |
| Rosetta | 16 | 201.906 / 162.854 | 18.90% | 18.36% | 38.177 |

结论是“同状态下的局部机会有可重复收益”，不是默认业务收益，也不是本轮产品优化了18.8%。产品未改；新旧fixture、控制和观察开销不同，不能直接用本表减旧报告百分比作为增量改善。

## Miss：12个真实blocker桶明确回退

每桶40对，按事前顺序合成20个平衡双对block，50,000次bootstrap、seed 261006；16桶用单侧99.6875%下界，门为on/off完成吞吐≥0.98。下表完整保留16桶，`native-pin`为真实CPU读guard，`generic-lease`为真实read lease，`last-use`为已释放lease但HostLogical completion尚未完成。

| 架构 | K | 拒绝形状 | 吞吐比 | 下界 | 结果 |
|---|---:|---|---:|---:|---|
| arm64 | 1 | single | 1.01083 | 0.99810 | 通过 |
| arm64 | 1 | native-pin | 0.84110 | 0.82362 | 回退 |
| arm64 | 1 | generic-lease | 0.89839 | 0.86391 | 回退 |
| arm64 | 1 | last-use | 0.90426 | 0.87883 | 回退 |
| arm64 | 16 | single | 1.00179 | 0.98569 | 通过 |
| arm64 | 16 | native-pin | 0.81372 | 0.78175 | 回退 |
| arm64 | 16 | generic-lease | 0.88186 | 0.86825 | 回退 |
| arm64 | 16 | last-use | 0.88783 | 0.85439 | 回退 |
| Rosetta | 1 | single | 1.00082 | 0.97266 | 证据不足 |
| Rosetta | 1 | native-pin | 0.87322 | 0.84639 | 回退 |
| Rosetta | 1 | generic-lease | 0.88705 | 0.86287 | 回退 |
| Rosetta | 1 | last-use | 0.88206 | 0.85282 | 回退 |
| Rosetta | 16 | single | 1.01051 | 0.99425 | 通过 |
| Rosetta | 16 | native-pin | 0.82860 | 0.79648 | 回退 |
| Rosetta | 16 | generic-lease | 0.86739 | 0.83661 | 回退 |
| Rosetta | 16 | last-use | 0.88437 | 0.86933 | 回退 |

三类blocker的点估计吞吐损失9.57%～18.63%；对应同置信级别的单侧上界也均低于0.98。Rosetta K1 single区间覆盖1，不能写成已证明回退。K16的配对中位新增wall成本分别为：arm64 native-pin/lease/last-use **28.063 / 18.438 / 16.875μs**，Rosetta **44.739 / 31.990 / 28.979μs**。这是同库完整操作的净差，尚未分解为某一阶段独占成本，也不保证全部可删；校准未成立，不直接当原生产库的精确损失。

## 校准：7/8桶未建立±2%等价

同一fixture/state比较“开关库正常选择”与“未改产品库”。每桶40对、20个平衡block、50,000次bootstrap，双侧99.375%区间，8桶family名义覆盖95%；事前等价范围[0.98,1.02]。

| 架构 | K | 形状 | 开关库/产品吞吐 | 区间 | 等价 |
|---|---:|---|---:|---|---|
| arm64 | 1 | hit | 1.00275 | [0.98412,1.02173] | 未建立 |
| arm64 | 1 | single | 0.99453 | [0.98329,1.00887] | 成立 |
| arm64 | 16 | hit | 0.99687 | [0.96530,1.03067] | 未建立 |
| arm64 | 16 | single | 1.00220 | [0.97098,1.02547] | 未建立 |
| Rosetta | 1 | hit | 0.99697 | [0.96808,1.01571] | 未建立 |
| Rosetta | 1 | single | 1.00326 | [0.97181,1.02624] | 未建立 |
| Rosetta | 16 | hit | 0.97887 | [0.92386,1.00865] | 未建立 |
| Rosetta | 16 | single | 0.98647 | [0.92875,1.00952] | 未建立 |

七桶未建立等价不等于七桶证明开关变慢；主要表现为区间未包含于等价范围，本轮不能归因于某个宿主噪声或编译因素。按预注册规则保留全部结果，不减去校准均值、不放宽2%、不续采。本次校准覆盖hit和single；将来扩大生产资格前也应事前审查真实blocker是否需要独立校准。下一独立协议优先改善固定进程内的有效测量时长/批量计时设计，同时保持独立同状态初始fixture及完整端点，不修改本轮样本。

## 未改产品的固定M5控制：8/8通过

两组原公共fixture各四桶、每桶40对；50,000次bootstrap、seed 260926，每桶单侧98.75%下界≥0.98。它们使用原产品库，资格不依赖开关库等价；每个family独立裁决，没有合并为更高的整体置信度。

| 架构 | K | Fresh比 / 下界 | H4 history比 / 下界 |
|---|---:|---:|---:|
| arm64 | 1 | 1.32697 / 1.31265 | 1.47918 / 1.46618 |
| arm64 | 16 | 1.11577 / 1.10157 | 1.41207 / 1.39701 |
| Rosetta | 1 | 1.37799 / 1.35299 | 1.42361 / 1.39787 |
| Rosetta | 16 | 1.14210 / 1.12099 | 1.40780 / 1.39814 |

Fresh使用公共scanline；H4包含写入、commit、sentinel读取与四memento保留/purge，undo/redo在吞吐计时外。不是BR1真实stroke/显示/undo/context性能资格。

## 正确性、容量、代际与实际驻留边界

preflight运行原产品/开关库×两架的五个既有`productionHandoff`相关函数：共 **1,832 passed、0 failed、0 skipped**。另外58个fixture进程各两次样本覆盖两种库、开关、blocker、容量和代际；性能进程也逐次验证完整旧/新像素、命中数、复制/分配工作量、预算reservation归零、completion处理、provider close后payload归零及显式reclamation drain。全部2,942个运行进程正常退出并回收，源/运行输入前后哈希一致；不是一次新的完整产品/配置/TSAN矩阵。

受限provider payload预算为512KiB，K16逻辑payload S=256KiB，两架各两次结果一致：

| 初始状态与分支 | payload起止 | 完成 | 新复制 |
|---|---|---|---|
| 单副本Fresh | 256→512KiB | 成功 | 256KiB |
| 双副本Fresh | 512→512KiB | 安全拒绝、旧值保留 | 0 |
| 双副本handoff | 512→512KiB | 成功，16次命中 | 0 |

普通双副本Fresh被拒绝不证明“先驱逐alternate再Fresh”等所有合法策略都不可行。容量上限只针对provider payload，并非进程RAM总界。各Store预算类live/reserved/peak保存于样本；类峰值发生时刻不同，不能相加为同一时刻总峰值。示例双副本handoff的MetadataArena：初始296,448B，两架首次样本操作后arm64 live384,096/peak386,576B、Rosetta live344,336/peak373,488B，reserved均0。close快照时Store仍存活，元数据尚有驻留；随后销毁Store再drain。不能用payload close归零宣称所有metadata或全进程归零，也不能用本表代替重构前common-record同义used/reserved/slack分母。

连续四次发布且保留旧View的诊断，两架on命中均为 **[16,0,0,0]**，off为[0,0,0,0]：`G0:{A,B}→G0:{B},G1:{A′}`后没有自动生成G1的alternate。不是同pending段的多dab复用，也没有测量实际笔刷命中率。

## 从基线推进：下一完整修改责任

[source-audit.json](source-audit.json)绑定当前源码和生产caller检索；[required-matrix.json](required-matrix.json)区分本包已测子集与未闭合的CP0/阶段要求。

| 优先项 | 代码位置与当前事实 | 下一交付与边界 |
|---|---|---|
| M1：metadata已知拒绝 | `queryMutationBase`发现alternate时未先排除旧authority的pin/readLeases/pendingLastUses；`AcquireRecoverableWrite`在准备工作状态后才拒绝 | 从既有shard事实提前排除明确不合格候选；保留最终revision、identity和安装检查，不引入第二owner或缓存排他位 |
| M2：native已知拒绝 | `prepareHandoff`已有mutex但不检查reader/write state；最终`tryClaimHandoff`才拒绝 | 原binding下提前拒绝明显busy；最终nonblocking claim继续负责竞争复核，不能把预检当权限 |
| M3：完整回退与联动 | `prepareWritePlanLocked`先pin before，再准备physical/accounting/metadata/descriptor，最后claim | 审核两种提前拒绝都回原Fresh，已获资源沿原cleanup退出，全部可失败准备仍在claim前；没有必要就不改coordinator |
| V1：安全验证 | 原reader/concurrent/epoch/preparation/cancel函数 | 真实blocker及释放后可命中、晚到reader、两种交错、ABA、零复制/安装/close；验证早拒绝没有改变原成功或失败语义 |
| V2：性能取证 | 当前父基线与开关校准 | 另行预注册稳定测量；修复后比较父/子、hit/miss/原控制，保留本次失败，不能扩当前样本到通过 |

理论目标是把**已知无资格**的尝试从完整冷准备缩为对现有状态的有限判断，随后直接走Fresh。晚到的竞争仍可能触发原完整准备与回滚，不能承诺所有miss都零成本。本包观察到的K16额外16.9～44.7μs给出优先级和待解释规模，并非已证明的算法可删下界。

生产caller清点仍只发现普通byte import及tiles3 clone提供单authority，没有发现传入非空readyAlternates的生产caller；自然正例与业务p未建立。新门暴露的真实问题是无收益尝试的成本，支持优先改善拒绝路径；不支持继续按30%差值逐容器猜改，也不支持默认启用。GPU native provider未接通，没有新增BR3范围。完整M6/M7/M8仍0/3，persistent默认关闭。

## 证据和失败保留

入口：[summary.json](summary.json)、[verification.json](verification.json)、[固定Fresh](fixed-m5-fresh-summary.json)、[固定history](fixed-m5-history-summary.json)。运行编排为[run.py](run.py)/[run_matrix.py](run_matrix.py)，统计为[analyze.py](analyze.py)，核对归档为[verify.py](verify.py)。[prior-identity.json](prior-identity.json)验证继承的2,315个源码及163个运行文件；本轮fixture共161,396个原始样本（含warmup和preflight），不是161,396个统计独立单位。

正式运行前首次fixture编译调用了不存在的`mutation.isValid()`，未收集样本；改用既有beginWrite guard有效性后重建。失败源码/命令/日志保存在`failed-build-arm64-01`及[execution-issues.json](execution-issues.json)。所有统计失败与不确定结果原样保留。

[raw-evidence.tar.gz](raw-evidence.tar.gz)保存全部原始日志、进程记录、输入快照、host状态、编译命令/失败、源哈希及生成的复制TU；[raw-evidence-manifest.json](raw-evidence-manifest.json)含逐文件和归档SHA-256。二进制/对象仍保留本地，不进Git；复现实验需对应产品、原构建依赖和包内命令。归档只冻结本轮证据，旧包不改写。[documentation-verification.json](documentation-verification.json)另记录活动文档链接/锚点、差异与暂存范围核对，不授予性能资格。
