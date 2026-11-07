# M6：CPU计量覆盖、执行条件变异与就地配对

本包完成有界诊断与修复候选实测：**异构核执行条件是校准变异的实证来源之一，就地ABBA候选被否决；没有取得新的产品加速，完整M6仍未通过。** 不再将少见极慢尾或重复调用次数单独当作下一产品热点。

产品保持`38834c4e2612c819f9d088dfd59c59889f295a49`，文档父`a5bff4ea5bbbba58d453a01683b1e7fdfb56f828`。应用algorithm-cost-optimization技能。生产/产品测试改动0，新增业务开关/API/字段/owner0；本包不猜改provider、容器或产品调度。

| 责任 | 事前范围/实际动作 | 证据/裁决 |
|---|---|---|
| C1 CPU时钟覆盖 | 两架各3×busy、3×sleep、3×empty；仅通过覆盖判据才解释相应时钟 | ARM thread/process均通过；Rosetta thread约2.4%无效、process约100%有效。process包括后台，不能冒充main |
| D1 ≥1ms操作归因 | 32过程、每桶4、128ms/min512/8warmup | 161087有效操作无≥1ms事件；有限诊断完成，不加样到出现尾或宣称尾已修复 |
| 旧D4分解 | 校验768过程/769输入，吞吐log精确拆为median与mean/median形状因子 | 极慢尾只是少量时间，不能解释所有残差；协方差保持，不换成median门 |
| D2 固定算术/CPU编号旁证 | 16过程、K1两架hit/native、512ms，操作前后32768步固定reference | 601409操作；全量Pearson判据仅4/16，不能宣布完整同步解释成立；CPU编号分组有差异 |
| D3 低扰动复核 | 32过程、K1/K16两架hit/native，移除CPU/rusage/reference，只在原wall外查询编号 | 654950操作；30个有两组样本的过程全部观察到0–5同编号组中位比6–9慢3.11–5.33倍；2过程无0–5组。现象重复，不冒充核类型/因果置信区间 |
| I1/V1 就地ABBA | 同期global/local各96过程，四个D4残留组合，每组12pair/6块、512ms；原未插桩probe直接复用 | 两策略均0/4区间满足±2%；local在3/4组合增大SD。候选否决，不推广、不续采；[完整位置矩阵](local-block-PLAN.md)、[结果](local-block-summary.json) |
| P1 核标签/当前上下文 | 原库两个固定3s ARM trace，K1 native、K16 hit；不与测量并行 | K1触发原100000次上限exit3，保留、不重录；已登记K16正常退出，49177操作、493个明确API上下文Running样本。有效K16 trace标签给出0–5 E、6–9 P |
| V2 身份/工作/退出 | 全部冻结输入、timed body、输出、copy/handoff、budget及销毁drain | [核验](verification.json)通过2527新冻结输入及769旧D4输入；274/274测量过程、6188927有效操作。P1另计2尝试、1通过/1失败。旧完整安全11180/0/0、6资源及结构仅继承同一输入，不计作新增 |

[初始计划](PLAN.md)、[reference计划](reference-PLAN.md)、[低扰动计划](cpu-query-PLAN.md)、[理论成本账](cost-model.md)区分工作、计量和环境。C1/D1增加CPU/rusage，D2还增加reference，会扰动短操作，不能作为正式速度；D3查询也非零扰动。I1/V1完全复用原未插桩夹具。

CPU编号仅表示查询瞬间，同起止编号不能证明中间未迁移。IORegistry未给出映射；后继有效当前K16 [trace分析](profile-summary.json)实际将0–5标E Core、6–9标P Core。K1的16个过程两组均存在，E查询组有16–771操作，中位比3.14–5.33；K16部分E组仅1–2操作，证据较弱。关联现象重复，不由30/30给虚构全局95%因果置信或精确频率/缓存/外部竞争分摊。

一次独立helper的[公开affinity能力检查](affinity-capability.json)返回46/service not supported；SDK该接口本来也是尽可能共享cache的hint，不保证指定CPU。没有修改产品或全局调度。有效K16的493个明确API上下文样本中seal125、commit144、beginWrite223，仍有共同管理成本；未覆盖的像素/guard等不算零，样本不转换为精确μs或可删预算。失败K1 trace只允许读取硬件标签，不授操作成本；分析器把1879个仅source行匹配的歧义样本单列，保留原分析，不重录。

| 四个诊断组合 | global两侧95%区间 | local两侧95%区间 | local paired log吞吐SD变化 |
|---|---|---|---:|
| ARM K1 native A/A | [0.99814,1.03299] | [0.95271,1.01117] | +14.27% |
| ARM K16 hit异镜像 | [0.98690,1.03487] | [0.97844,1.05671] | +149.16% |
| Rosetta K1 native A/A | [0.94232,1.00998] | [0.98730,1.04313] | +24.95% |
| Rosetta K1 native异镜像 | [0.97420,1.02189] | [0.96336,1.00670] | −0.77% |

均为未经family调整的有限诊断界，不是正式性能资格。相反顺序pair的中位间隔从global约15–27s降至local约0.004–0.012s，编排机制兑现；精度预测没有兑现，说明只消除局部线性漂移不足。不能把本轮4组与旧12组拼成16/16，不启动昂贵盲正式扩样。全部[执行/分析问题](execution-issues.json)、原始向量、命令、退出、实际加载库和trace保留在[原始归档](raw-evidence.tar.xz)与[成员/SHA](artifact-manifest.json)，未替换失败。

下一责任是稳定并验证实际执行条件，再独立完整20桶校准及匹配hit/miss；当前host未证明具备该分辨率，不能据此判产品回退或降低门槛。没有可删时间预算时停止同义runner调参和微路径猜改；metadata分母/CP0 required独立补证。此次完成的是更准确的定位与候选否决，不是产品优化成功或完整计量关闭。

有限包与正式M6分开：旧校准2/20、联合hit0/4和miss2/16、原Fresh/H4八桶保持；旧20%/30%失败不改写。metadata同义重构前used/reserved/slack驻留≥25%分母、CP0完整required、自然来源/业务分布及GPU/M7/M8/default资格独立开放。M6/M7/M8仍0/3，persistent默认关闭。

分析复现：在隔离目录展开本包归档，依次运行`analyze_diagnostic.py`、`analyze_reference.py`、`analyze_cpu_query.py`、`analyze_local_block.py`、`analyze_profile.py`；均分析既有样本，不重启实验。旧D4分解需另将上一包归档展开到相邻同名目录，再运行`decompose_previous.py`。`verify_evidence.py`还需要冻结清单中原源码/库路径存在且字节匹配；移机分析与重新获得运行资格分开。原始实验runner以新建目录保护禁止覆盖，已结包不再续采。
