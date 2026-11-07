# CP3 metadata准入的依赖范围缓存（已交付）

产品起点`57e59e6b0e53c625b0e4853985a242b5433ca618`。按新建[algorithm-cost-optimization skill](skill/SKILL.md)从当前实际成本选择一个完整责任，当前阶段资格仍由92维护。本包的技能快照及安装位置/hash在[start-identity.json](start-identity.json)，个人技能位于`/Users/apple/.codex/skills/algorithm-cost-optimization/`。

最终产品`0a00bd3fe3fe71e44c04b987f9558bcd37f00dc6`，[提交与资格](delivery.json)、[责任及增删](closure-review.json)、[Git blobs/运行库/样本核对](final-verification.json)均绑定同一实现。机制和父版本增量已确认，原Fresh/H4四桶均通过；native20%/30%门仍失败，完整M6未通过。

## 问题、必要工作与候选选择

父版本public N1024/K16/B4/h1/H0后次写入约988次完整`fitsLocked`，每次7类×4域及class aggregate/全局durable检查；单leaf约28.55–30.65μs，预算+owner互斥约57–58μs。本包不是继续减少已闭合的allocator引用。524控制请求中446个controller对象各做parent/local准入（892次），请求只增加MetadataArena/CpuRam，其他六类状态经常未变。实际容量、准入次数、两级收费/settle、失败归还及最后free是必要工作，本包不预报下降。

理想表达为：依赖未变的六类基线约束只判断一次；每次metadata请求仍检查四域溢出、metadata aggregate、实时process storage以及全局SSD。缓存不是“未涉及类别就默认通过”，必须保存失败结果；基线非法时不允许metadata请求绕过。原通用/signed/empty-usage路径继续完整判断，不把净额预留等同于物理正域预留。

选择原controller内一个派生缓存：六类零增量的可行性与其饱和live SSD和，由同一`m_mutex`保护。没有新owner/账本/队列/费用/许可，m_usage/m_limits仍是唯一权威。相比全域headroom增量缓存，这只需约16B并保守失效，不要求每种结算维护第二套各域余额；相比只做metadata sparse scan，它继续拒绝未变化但已超限的其他类。metadata与durable实时检查使用同一bucket政策函数，避免两份限额政策。

## 失效与消费者闭包

| ID | 位置/consumer | 修改及必须保持的合同 | 退出证据 | 状态 |
|---|---|---|---|---|
| B1 | `fitsLocked`的domain/class政策、signed/empty/process/durable | 提取共用bucket判断；通用路径完整语义不变 | 每架父/新库各800000判断的digest/accepted完全一致 | 完成 |
| B2 | `fitsMetadataStorageLocked`及原controller字段 | 缓存六类零增量可行性/SSD和；metadata/process/global SSD实时检查 | 每架1200000组full/cold/warm比较一致，布局1360→1376B | 完成 |
| B3 | activateReservation/commitRetaining/configureLimits/moveRetirementHeadroom | 在同一gate内保守失效；包含净额预留、保留预留和退休换域 | 每架14状态序列判断及原waiter/physical claim矩阵；全部写者静态闭合 | 完成 |
| B4 | releaseLive/shared release、allocator prepare/settle、process publish | 非metadata release失效；metadata变化不污染六类缓存；process snapshot不缓存 | 释放后恢复、SSD过期反例、退休换域溢出、真实process变化通过 | 完成 |
| B5 | kisAllocateMutationStorage、process reserve、reservation-slot准备 | 仅已知metadata CPU正容量迁入专用判断；prior waiter、公平/拒绝、原收费及回滚保持 | 原安装0alloc/free、storage与压力测试 | 完成 |
| V1 | 完整受影响安全/结构/ABI | 原测试断言与ratchet；controller增长如实收费 | 双架38个QTest进程及6个原探针正常退出；结构/工具检查通过 | 完成 |
| V2 | 原public/native数量端点 | logical fits总数、请求/free/工作量保持；量化bucket检查与缓存刷新 | 原28进程全部通过；14 trace的逐行数量模型一致 | 完成 |
| V3 | 冻结父库、M5/H4/native、CPU采样 | 预注册固定配对与原门；不加样到通过 | 1280未插桩进程+4诊断；增量/Fresh/H4通过，native资格单列失败 | 完成 |

只有本TU写controller的m_usage/限额/预留总额。activate与commit覆盖waiter授予/取消、reserveChange、shared child和slot array；release/retainOnly均收敛到commitRetaining。releaseLive只有非metadata类使缓存失效；shared release、allocator local/parent prepare/settle、process storage及bootstrap政策采纳只改metadata，因此实时metadata检查覆盖，不缓存process快照。moveRetirementHeadroom即便aggregate不变也改变reserved域，必须失效；configureLimits在成功后失效。每个正常/失败/重试/清理边界仍沿原owner继续。

## 事前数量与时间模型

记Q为同义逻辑准入次数、G为通用检查次数、M为metadata专用次数、R为六类缓存刷新次数。在被测成功准入上，原bucket检查约`7Q`，候选约`7G + M + 6R`（拒绝可提前返回，原始事件另报）。只按892个已确认两级metadata准入估算，Q=988、G≤96、M≥892，原6916个bucket判断对应候选≤`1564 + 6R`；process/slot迁移可进一步减少G。工程退出目标为本用例bucket检查至少减少50%，R需由实测解释；不改变Q或费用来达标。

忽略缓存刷新和新增分支的乐观上界，六个重复bucket占完整扫描约6/7，对父28.6–30.7μs成本仅给约24.5–26.3μs的条件上界，不能当作保证收益。实际还保留metadata、process snapshot、SSD、负值/溢出及冷刷新；不为总预算57–58μs整项宣称可删。未插桩父/候选固定配对检验方向与区间，CPU采样只解释机制。正式Fresh/native与metadata驻留/CP0资格独立，不能用本包局部收益替代。

## 有限验证

先固定源/父库，再完成整个B1–B5迁移。既有单次完整policy差分和新依赖失效差分各有限执行；状态注入仅用于证据程序，不进入产品API。安全通过后顺序运行原28数量进程、父版本40对四桶、原M5 Fresh/H4/native40对及4个CPU诊断，性能不与构建/其他基准并发。失败保留，真实回归修复另开批次；分析器问题只修分析并使用原样本，不改门/删样/扩样。原TSAN/CP0/长压测等欠项不由本包推定通过。

## 数量实测与预测核对

[策略差分](policy-differential-summary.json)调用真实父/新库私有政策函数，8进程全部退出0；每架父/新通用各800000判断一致，每架1200000组metadata依赖比较及14个定向状态序列通过。边界注入证明政策等价及失效正确，不宣称所有注入状态都能由合法业务产生；原安全矩阵验证真实consumer。每controller真实布局增加16B，原分配路径按容量收费。

[数量对照](quantity-comparison.json)保持原单操作窗口、全部顺序块与晚free，不使用插桩时间。父bucket次数由已通过准入的`7Q`推导，候选为实际事件计数；表中没有政策拒绝导致的提前返回差额。

| 同义用例 | Q | G / M | R | 父7Q → 实际bucket | 减少 |
|---|---:|---:|---:|---:|---:|
| public N1024/K16 | 988 | 17 / 971 | 63、61 | 6916 → 1468、1456 | 78.77%、78.95% |
| public N64/K1 | 137 | 2 / 135 | 6、5 | 959 → 185、179 | 80.71%、81.33% |
| public N64/K16 | 1158 | 17 / 1141 | 60 | 8106 → 1620 | 80.01% |
| native Fresh K16 | 893 | 17 / 876 | 50 | 6251 → 1295 | 79.28% |
| native handoff K16 | 624 | 27 / 597 | 38 | 4368 → 1014 | 76.79% |

K16得到`7×17 + 971 + 6×R`，两块均无模型残差。工程目标≥50%已通过；若忽略必要刷新，当前consumer划分的乐观数量界为1090，而实际额外366～378次来自刷新，约占候选检查25%。这是本设计的条件数量界，不是所有合法算法的严格下界。524请求、446 controller成功、78 process路由、339 retained请求、两级prepare/settle及各角色收费容量保持；所有14行准入数量保持。63/61刷新差异来自释放/后台时序，保留两块原值，不将它当作workload差异或删样理由。

## 未插桩增量与正式控制

[改动前57e59父库配对](parent-comparison-summary.json)每桶40对、20个预定顺序平衡块，双侧95% bootstrap区间；这是本轮增量解释，不是四桶family阶段门。全部320进程身份、语义、退出通过。

| 架构 / 桶 | 吞吐增益及95%区间 | 配对CPU节省μs | 配对wall节省μs |
|---|---:|---:|---:|
| ARM K1 | 13.42% [12.88%,14.23%] | 3.77 [3.64,3.90] | 3.95 [3.81,4.13] |
| ARM K16 | 17.29% [12.39%,20.53%] | 35.14 [29.44,39.16] | 42.07 [30.86,47.81] |
| Rosetta K1 | 11.73% [10.88%,12.12%] | 不解释未校准线程时钟 | 4.88 [4.48,5.01] |
| Rosetta K16 | 12.86% [12.19%,13.61%] | 不解释未校准线程时钟 | 47.81 [44.87,50.29] |

CPU与wall分开；配对中位估计不等于两组边际中位数之差。事前24.5～26.3μs仅估计六类扫描的条件空间，不能约束包括临时构造、政策特化及编译布局在内的整个补丁收益；实测35.14μs超过这个窄模型，保留差额，不能全部归因于缓存。后续Running样本用于检查方向，不取代上述配对区间。

原[Fresh M5控制](fixed-m5-fresh-summary.json)四桶全部通过。K16 current/M5为ARM1.0986、Rosetta1.1397，单侧98.75%下界分别1.0621、1.1214，均高于原0.98；K1为1.3248/1.4043，下界1.3061/1.3897。此次关闭此前Fresh K16的置信下界缺口，不能据此提前通过native或整个M6。

原[H4控制](fixed-m5-history-summary.json)四桶也均通过：ARM K1/K16为1.4875/1.4133（下界1.4733/1.3953），Rosetta为1.4744/1.4627（1.4450/1.4429）。原[native handoff门](latency-paired-summary.json)保持每桶40对和单侧98.75%下界：

| 架构 / 桶 | handoff延迟减少 | 下界 | 原要求 | 裁决 |
|---|---:|---:|---:|---|
| ARM K1 | 3.68% | 2.81% | ≥20% | 失败 |
| ARM K16 | 11.99% | 10.90% | ≥30% | 失败 |
| Rosetta K1 | 2.90% | 0.84% | ≥20% | 失败 |
| Rosetta K16 | 12.60% | 11.38% | ≥30% | 失败 |

四组共1280进程全部正常、库/语义/前后身份核对通过。失败的正式门不补样；旧14.3%/14.9%与本批11.99%/12.60%的差值不是本补丁增量回归估计，因为Fresh分母也受优化影响，且原生两版本的增量配对未在本包运行。

## CPU解释、残差和下一优先责任

[4份Running CPU诊断](cpu-comparison.json)中，父完整准入上下文约28.88～30.70μs，候选general+metadata两个互不嵌套的上下文合计约1.61～2.06μs。独占预算政策/账本32.72～33.58→5.36～5.55μs，独占owner/收费胶水19.89～22.80μs仍存在，两者合计约54.94～56.22→25.25～28.34μs。扫描数量减少78.8%并不要求时间也减少相同比例，常量metadata政策特化、临时构造和代码生成均可能影响单价；短样本不能精确分摊35.14μs总CPU收益的全部原因。

每份1985～2080个内部循环主线程样本，约3.2%～4.0% leaf未符号化；2秒Running份额乘6秒夹具CPU/op只给近似定位，无分阶段置信区间。初版分析器错误要求外层样本为零；三份各1个外层`testSharedBaseline`样本被断言拦下。现保留原分析器、失败日志及这3个样本，独立列出后重析同一4份XML，见[回修与原始身份](analysis-repair.json)、[执行问题](execution-issues.json)。没有改采样规则、重跑或丢弃整份profile，产品测试也没有失败。

本责任B1–B5/V1–V3全部完成并停止扩样。原安全矩阵11114/0/0，另6探针（每架31080/28安装区间零alloc/free、24 storage边界）及8策略差分进程分开计数。87 TU/2211 APIs/28880逆边/27 callbacks和原结构/6工具检查通过；生产2文件+81/-25、ownership+1/-1，派生物+1195/-1018，没有新增产品测试flag或公共接口。

下一优先责任应转向native差异准备与必要收费/settle，而不是继续按旧28～31μs领取已删除的完整扫描。当前public独占write protocol/claims约45.2～48.7μs、heap35.9～37.9μs、metadata26.3～30.0μs、owner19.9～22.8μs是可定位范围，尚不等于可删预算；需要先在native原完整事务/选择/seal/commit上分开共同与handoff特有工作，证明可删空间能承担正式门缺口。

以本批边际中位数作**条件规划**：ARM K16 Fresh125.17μs、handoff110.10μs，若Fresh不变，达到30%需handoff另减约22.49μs；Rosetta对应198.32/172.32μs，另减33.50μs。若只从两边删除完全相同的成本C，则需`C ≥ [H−0.7F]/0.3`，即约74.96/111.66μs，说明继续削小额公共扫描不能自动关闭30%差距。这不是配对置信结果，也不证明这些成本可删；真实门仍须原下界通过。metadata同义实际驻留≥25%分母、CP0 required及其余M6/M7/M8欠项保持，persistent默认关闭。

## 复核入口

技能结构已由skill-creator校验通过，[实际应用复核](skill-application-review.json)确认个人安装与版本快照相同。后续可用`$algorithm-cost-optimization`启动相同工作流；具体项目合同、阈值与样本量不从本个案照搬。

复现从[start-identity](start-identity.json)、[事前协议](validation-protocol.json)、[源码补丁](product.patch)及[构建/运行工具来源](reused-tools.json)开始。`run_package.py`保存每条命令的退出/超时/reap；`run_policy_differential.py`核对实际父/新策略。数量分析用`analyze_trace.py`、`summarize_trace.py`、`compare_quantities.py`，时间分析用原paired分析器和修正后的`analyze_cpu.py`/`compare_cpu.py`。最终运行`verify_final.py`绑定Git blobs和真实库；[完整原始证据包](raw-evidence.tar.gz)及[逐文件hash清单](raw-evidence-manifest.json)保留全部成功、分析失败、XML、事件/映射/符号和源码工具，二进制构建产物留本机。
