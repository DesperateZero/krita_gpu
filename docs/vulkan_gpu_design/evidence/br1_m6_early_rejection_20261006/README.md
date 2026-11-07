# M6已知拒绝提前：实现、机制与固定性能验证

父产品 `f0c40a5d195f1c20a0f915faaef18b1f3ee5b575`，文档起点 `b86bde1cda8de014e3d9d431803f80a7efdac5b5`。本包按 algorithm-cost-optimization skill 解决上一基线中稳定pin/lease/last-use仍进入冷准备的成本。[事前设计](PLAN.md)、[起点身份](start-identity.json)先于产品修改；[性能协议](protocol.json)、[冻结文件](freeze.json)先于新性能样本。

已完成并提交产品 `79e1c8d1ef`：已知拒绝的多余准备被删除，三类blocker的 **12/12桶确认改善，完成吞吐增加10.68%～22.16%**。预注册20桶父子family采用双侧99.75%区间，family名义覆盖至少95%。正常命中同库4/4正收益、原Fresh/H4八桶保护通过；miss仅6/16通过，校准仅4/20等价，**完整M6仍未通过**。

[汇总数据](summary.json)、[最终核验](verification.json)、[源码闭包](source-review.json)、[门项差集](required-matrix.json)和[原始归档](raw-evidence.tar.xz)共同绑定结论。5572个实验运行进程（其中5440正式性能进程）、550660条原始fixture样本全部退出/回收且通过工作量、像素、实际库及身份检查；内部样本不是独立统计重复。24项事前冻结文件与2500项候选输入哈希复核一致。

## 算法差距与完整责任

同义工作仍为Preserve首写、完整新输入、旧exact View可读、seal/canonical commit以及原退出终点。Fresh必须准备新payload并保留旧值；handoff必须有独立exact before、独占物理source及完整预算/安装保证。发现旧source已有稳定读者时，准备一份注定不能安装的handoff候选不属于语义必要工作。

当前修改使用已有锁内事实提前拒绝：metadata authority的`pinCount/activeOperation/overflow`、binding的`m_readers/m_writeState`。replica overflow只承载read lease和pending last-use；version上的captured View仍允许handoff，独立before自身有读者也不被误排除。没有缓存布尔值、第二owner、新字段、API或等待策略。

| ID | 实际改动/consumer | 必须保留的合同 | 验证与状态 |
|---|---|---|---|
| M1 | `queryMutationBase`在原shard cut中排除已有writer或被保护的authority，再选择独立before | 不扫描/导出额外版本；同一返回中的base/sealed/nextGeneration保持；StateMachine及最终revision复核保留 | 原indexedMutationBaseLookup补lease→last-use→ack与已有writer；captured version/受保护before仍可被选择。完成 |
| M2 | `KisCpuResidentBinding::prepareHandoff`在原mutex下拒绝已有reader或非Idle writer | 预检不占有权限；`tryClaimHandoff`继续检查identity、reader/write state及底层storage排斥 | 原physical guards覆盖先准备后到reader与先reader后准备、释放后重试。完成 |
| M3 | `prepareWritePlanLocked`把非占有physical prepare放在独立before pin之前，明确失败即走原Fresh | before provider仍沿原ledger保活；所有provider访问与cleanup在owner gate外；成功路径仍先保活before、准备accounting/metadata/descriptor，最后claim/install | 原native/generic fallback、并发双次序、epoch、准备拒绝和三终结；共同安装零分配。完成 |
| C1 | 原tileReadCacheLifetime测试原来重试busy时创建的候选；改为pin释放后重新prepare | 被拒绝的候选不保留未来写权限；idle候选自身仍不pin RAM，缓存stale/retired行为不变 | 首轮完整矩阵四行失败保留；同步迁移后完整双架全过。完成 |
| V1 | 原生产、reference、physical、业务与资源消费者 | 不放松raw/ref/alias/swap/foreign owner、限额、取消、epoch或close | 38个QTest进程11116/0/0，6个资源探针与结构检查。完成 |
| V2 | 原库父/子增量、候选同库hit/miss、开关校准、固定M5保护 | 同义工作/实际库、固定样本、独立family，不追加到通过 | 固定矩阵完成；blocker12/12改善，hit4/4、miss6/16、校准4/20、原控制8/8。资格限制见下 |

提前拒绝是机会型策略的保守观察：如果保护在预检之后解除，本次仍可选择Fresh；下一次准备重新读取原状态。晚到的竞争仍可能造成完整准备后回滚，本包没有消除其必要复核成本，也不承诺所有miss为零。

生产4文件 **+30/−15，净+15**（包含私有header合同注释），测试3文件 **+48/−1**；新增代码行不等于新增运行工作。重用原责任表达，没有增加产品计数器或持久存储。派生callgraph/source inventory另列，不作为算法复杂度或收益指标。

## 理论预测与实际机制

独立的40个机制进程，arm64/Rosetta×K1/K16×五形状×父/子，每进程两个样本，全部工作/像素/退出检查通过。仅该scope启用原diagnostic phase observer；其时间不计性能资格。顺序为Prepare入口、Prepared结束、Install尝试、Installed成功、Cleanup。

| K16形状 | 父计数 | 候选计数 | 预测兑现 |
|---|---|---|---|
| hit | [16,16,16,16,16] | [16,16,16,16,16] | 必要成功责任不变 |
| single | [0,0,0,0,0] | [0,0,0,0,0] | 不新增尝试 |
| native pin | [16,16,16,0,16] | [16,0,0,0,16] | 后续accounting/metadata/descriptor和claim尝试16→0；观察与局部cleanup仍有成本 |
| generic lease | [16,16,0,0,16] | [0,0,0,0,0] | 整段候选准备16→0 |
| pending last-use | [16,16,0,0,16] | [0,0,0,0,0] | 整段候选准备16→0 |

两架结果一致，K1对应16→1缩放。这里是实际阶段次数与代码顺序的联合证据，不是allocator请求数、独占CPU占比或全部管理工作减少比例。其余Fresh写入、共同seal/commit、旧值保护、预算和最后释放仍然必要。

事前未给未测单价赋值；上一基线K16多出的16.9～44.7μs仅是待解释净差，不作为本包保证可删下界。理想目标为`TFresh + 有限已知状态判断`，不是零成本miss；最终用父/子原库验证实际增量，再用同库on/off残差判断门项。

## 实际收益与剩余门项

原产品库父/子比较不依赖证据开关等价。K16结果如下；μs为40个配对的进程中位延迟差之中位数，吞吐是实际完成数/总计时wall，二者不是相互倒数。

| 架构 | blocker | 完成吞吐提升 | 双侧99.75%区间 | 配对中位wall节省 |
|---|---|---:|---:|---:|
| arm64原生 | native pin | 22.16% | [18.34%,25.82%] | 28.906μs |
| arm64原生 | generic lease | 13.33% | [11.28%,16.16%] | 17.698μs |
| arm64原生 | pending last-use | 14.32% | [9.46%,17.65%] | 18.771μs |
| Rosetta x86_64 | native pin | 20.21% | [17.83%,22.06%] | 41.979μs |
| Rosetta x86_64 | generic lease | 14.82% | [13.20%,19.33%] | 29.073μs |
| Rosetta x86_64 | pending last-use | 15.13% | [11.59%,17.51%] | 31.677μs |

K1六个blocker桶增加10.68%～15.97%，各下界均>0；12个blocker全部达到事前增益判断。其余八个hit/single父子桶区间均包含1，不能从“没有显著变化”推定±2%等价；它们也不是要求继续优化到显著正收益的目标。

| 门项 | arm64 K1 / K16 | Rosetta K1 / K16 | 裁决 |
|---|---|---|---|
| 同库hit延迟降低（单侧98.75%下界） | 8.09%（6.99%）/17.92%（17.17%） | 10.04%（7.76%）/19.85%（19.03%） | 同库4/4正收益；校准限制仍适用 |
| miss single吞吐比下界 | 0.98393 / 0.94714 | 0.97618 / 0.97299 | 1/4≥0.98 |
| miss native-pin吞吐比下界 | 0.96971 / 0.96241 | 0.97440 / 0.96469 | 0/4≥0.98 |
| miss generic-lease吞吐比下界 | 0.98606 / 0.99050 | 0.98940 / 0.97535 | 3/4≥0.98 |
| miss last-use吞吐比下界 | 0.98551 / 0.97741 | 0.98501 / 0.97397 | 2/4≥0.98 |
| 原库相对固定M5 Fresh下界 | 1.31349 / 1.08867 | 1.39037 / 1.13221 | 4/4保护通过 |
| 原库相对固定M5 H4下界 | 1.48052 / 1.40056 | 1.44869 / 1.48063 | 4/4保护通过 |

miss用事前单侧99.6875%下界、16桶family名义至少95%；**6通过、10证据不足、0桶明确证明回退超过2%**。旧基线的12桶明确回退已不再出现，但不同批次的桶通过数量不能替代本轮原库父子因果比较。当前native pin仍最值得关注：K16吞吐比点估计arm64为0.98079、Rosetta为0.97369；Rosetta上界0.98356仍跨过0.98门，因此不能说已经证明超过2%。对应同库配对中位额外wall为1.927/4.771μs，不能把它全部当可删量。

开关校准扩为20桶，仅arm64 K1的hit/single/native-pin/last-use四桶区间完全落入[0.98,1.02]；其余16桶是**等价证据不足**，没有一桶区间完全落在容许带外。全部点估计在0.98797～1.01411，仍不能用接近1替代等价检验，也不做减法校正。增加进程内循环到128并没有关闭校准；未定位的调度/计时变异和证据库布局差异不能先验归因成某一原因。所有同库结果保留此限制，不能跨桶借用四个已过校准的资格。

本包兑现了已知不必要工作的删除与实际增益，停止于此。下一性能工作先区分**测量分辨率不足**和**native pin剩余准备成本**：在独立预注册协议中核对无改动控制的进程间变异、有效计时窗口与库布局影响，同时只审查原source检查、beforeProvider引用和gate往返是否还存在合法可删工作。须先给必要成本/绝对收益预算再改代码；不放宽2%、追加本批样本或凭剩余μs重写容器。metadata实际驻留分母及CP0完整required继续独立推进。

## 固定性能协议与可比性

使用同一[fixture](baseline.cpp)，K1/K16、N=K、64×64 B4、H0 history roots且一个exact旧View。hit与三个blocker两边都是分别初始化的两个exact副本，single两边是一副本。事务begin→mutation/完整memset→seal→canonical commit计wall；setup、独立before创建、全像素/工作检查、completion、close与Store析构/drain在外另报。

| Family | 事前规模与估计量 | 判据 |
|---|---|---|
| 原库父/子增量 | 20桶×40对，8warmup+64测量；20个平衡双对log完成吞吐块，50k bootstrap/seed261007，双侧99.75% | 全family名义95%区间；下界>1才确认吞吐改善，控制桶不显著不等于等价 |
| 开关等价校准 | 全20桶×40对，8warmup+128测量；20块，50k/261007，双侧99.75% | 正常选择开关库/原候选库区间须完全落在[0.98,1.02]；包含真实blocker，失败不作减法校正 |
| 同状态hit | 4桶×40对，8+128；40个配对log中位延迟比，20k/261007，单侧98.75% | 延迟减少下界>0 |
| miss | 16桶×40对，8+128；20个完成率块，50k/261007，单侧99.6875% | on/off真实完成吞吐下界≥0.98 |
| 固定M5 Fresh/H4 | 原公共fixture各4桶×40对、250ms完成率；原50k/seed260926/单侧98.75% | 各自吞吐下界≥0.98，不与新native family合并 |

比上一批，新门/校准预先固定为每进程128次测量，校准覆盖也扩为全部20桶；父/子沿64次测量。每个进程只写有界结果文件，scope结束才汇总，避免反复重写全部历史记录。所有正式性能都关闭phase observer、profiler和阶段时钟，串行执行且不与构建/测试并行。独立统计单位是进程配对或预注册双对块，内部数百次循环不算独立重复。

证据开关只在复制的WriteCoordinator TU加入TLS选择控制，`queryMutationBase`前禁用发现以走安全Fresh。其他374个对象复用，原父库与原候选库均没有该开关。实际加载路径和源/运行哈希逐scope核对。arm64原生、x86_64为Rosetta；不解释为Intel原生、独占CPU或GPU结果。即使开关校准未成立，原产品库父/子增量仍可独立裁决；同库gate结果须保留其资格限制。

## 安全、调用点迁移与失败记录

最终38个原QTest进程 **11116 passed、0 failed、0 skipped**；每架另有joint/publication/storage三个原资源探针，全通过并核对实际新库。这些原probe的二进制/源码身份继承原包，运行库是本轮候选，未声称重新编译未变fixture。无新TSAN/平台或完整CP0资格。

结构检查通过：87 TUs、2211 APIs、28968 call edges、27 callbacks；21 manifest、25 ownership、16 census、19 intrusion及6项工具自测，原ratchet未放宽。产品提交包含七个手工修改文件和两个派生审计文件；派生图的大量行移动不是生产复杂度增长。

最终测试二进制链接原父库的6个负控制进程，reference每架3行、physical每架24行、production fallback每架24行失败，均为预期的新提前拒绝断言；同一最终测试在候选完整矩阵全部通过。首次定向12进程另存于`focused-01`，不合并作最终源码资格。

保留两次修复前记录：[execution-issues.json](execution-issues.json)。其一为证据fixture漏include原diagnostic header，发生于采样前；补header后重新编译。其二为首轮完整arm64的tileReadCacheLifetime四行仍重试旧busy候选；迁移其重试点、明确私有prepare合同后重新构建和运行完整矩阵。旧源码补丁与证据库保存在`pre-fixture-repair`，旧失败日志未覆盖，没有性能样本因上述修复被替换。

92 §6.1的metadata驻留≥25%重构前同义分母、CP0完整required、实际自然producer/业务分布及M7/M8/GPU仍独立开放。减少失败候选的临时准备不能替代common record实际驻留分母；局部吞吐改善不授予persistent或真实业务默认启用。

原始日志、逐进程结果、源/运行身份、事前脚本/协议、修复前失败与完整产品补丁共10775个成员，按[逐成员SHA-256清单](raw-evidence-manifest.json)归档并回读验证；展开908468470B，压缩23174560B。本地可执行文件和库不重复纳入Git，实际哈希与加载路径保存在原身份文件中。普通源码/文档用显式补丁，Python仅用于实验、统计、派生审计、归档及核验。产品与文档分别聚焦本地提交，外层原有`krita` gitlink差异不纳入文档提交。
