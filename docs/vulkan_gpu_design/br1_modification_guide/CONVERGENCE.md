# BR1 收敛与统一验收指南

本篇规定如何选择、停止和交付后续批次；当前事实、阻塞项与阶段资格统一由 [92 §16](../92_br1_m6_m8_execution_baseline.md#br1-convergence)裁决。函数入口沿用 BC、JP、HX 和原 15 项修改 ID，不再增加一组全局阶段编号。2026-09-28 的已执行审查见[冻结记录](../evidence/br1_convergence_review_20260928/README.md)。

执行时直接使用 [收敛目标与改动清点](CONVERGENCE_CHECKLIST.md)：目标出口、可领取改动、精确断言、接口合并与条件删除均已逐项列出，并附 124 文件的冻结清点。本篇维护通用规则，清点文档落实具体对象，当前裁决仍只回写 92。API 的函数级替代、合并删除与 caller 迁移按 [API_CONVERGENCE_MAP §12](API_CONVERGENCE_MAP.md#convergence-action-map)执行；任何主干改动还必须通过 [MI1–MI8 主干低耦合合同](MAINLINE_INTRUSION_POLICY.md)，完成情况勾选 [清点 §20](CONVERGENCE_CHECKLIST.md#mainline-intrusion-contract)。已冻结交付、工作树候选和待实现项必须分开；候选代码存在和局部日志通过不构成当前源码的验收。

## 1. 收敛目标与边界

下一轮的交付单位是一条可观察、可取消、可比较的真实绘画链：**初始化 → 接纳输入 → 实际 brush jobs → 正常显示 cut → finish / cancel → drain**。新增 helper、单点零分配和扩大测试总数只证明各自局部能力，不能代替这条链。

区分四种结果：

| 结果 | 能说明什么 | 不能据此宣布什么 |
|---|---|---|
| 局部能力通过 | 被测接口及失败边界在冻结源码上成立 | 默认 brush 已消费、整体预算或性能通过 |
| 开发/测试入口闭环 | 指定 eligibility 内真实 owner、jobs、读选择、显示和终结共同工作 | 未迁移模式安全、默认启用或 M8 完成 |
| 指定入口默认启用 | 该入口的语义、资源、进度、同输入回归与控制桶全部闭合 | 全模式、全部 M6–M8 或 BR1-PERF 通过 |
| 正式阶段/总出口 | 92 和 39 所需证据均满足 | 用其他入口收益抵消 stroke 回退 |

M6 → M7 → M8 的正式出口顺序、stroke → undo → context 的优先级不变。真实 freehand harness 和受控集成测试现在就做；它们属于 92 §13 的能力准备，不必等全部阶段完成才暴露业务接线问题。普通 brush 仍采用其可恢复失败保证，不因受控接线取得 M7 commit-only 资格。

<a id="next-batch"></a>
## 2. 下一工作包只领取可关闭的目标

**当前主线按 [92 §17 CP0–CP10](../92_br1_m6_m8_execution_baseline.md#br1-closure-schedule)执行。** 已交付的读选择、copy bounds、packed/cursor add窗口和真实direct联合fixture不再列当前待实现。剩余JP族进入CP6，控制存储进入CP1，M6资格进入CP2/CP3，M7进入CP4，公平/continuation进入CP5；不是一个无限补前置的任务。先核对 [完成矩阵](../92_br1_m6_m8_execution_baseline.md#m6-m8-completion-matrix)，再从 [NEXT_EDITS](NEXT_EDITS.md#closure-next-work)领取明确差集。

每个工作包交付必须满足：

1. 新取得的 current 读、canonical page + extent/default、adapter 对同一逻辑发布一致；旧 captured view 保持原选择。多个独立读取调用跨过发布点可以处于不同版本，测试必须固定观察窗口或共同 read selection，不能要求未承诺的跨调用原子快照。
2. 将现有窗口复现改为确定性契约断言，保留失败样本；覆盖冷缺页、暖缓存、旧 retained/raw reader、并发独立页与准备失败。原探针的通过表示“复现成功”，不能原样当修复通过。
3. 交付原 owner 的 prepare/revalidate/install/cleanup 生命周期和实际锁序；不在 publication write gate 内等待 tile swap barrier，不把完整 pixel kernel 串行化。当前锁内准备、清理成本必须单列；若本批只关闭一致性，S05 短 gate 资格仍保持开放。
4. finish/cancel/晚 guard 有唯一终点，已发布结果不能因后续清理失败改报未发布。未覆盖的其他入口逐项保留，不推定已经共用安全协议。

**验证准备从CP0开始：** 首条direct联合正确性已有冻结证据，不重新搭建harness。准备当前同依赖upstream、实际显示/drain的workload和缺测清单；CP5–CP7扩展资源/复杂模式时复用真实strategy的target、owner、producer、显示与终结断言。旧fixture的通过只对应其冻结源码。

新增前置项必须附上“违反的 92 条款或可复现失败 → 实际 caller → 为什么阻塞本次入口 → 有限完成判据”。只有潜在收益、更多零分配区间或类型美化的工作进入后续清单。已修复的边界没有新反例时，不再以增加探针数量延长同一批。

验证频次按 [92 §17.4](../92_br1_m6_m8_execution_baseline.md#closure-testing-policy)：小改动组合成一个可验收工作包后测目标结果，阶段冻结才跑完整所需矩阵。连续两次小交付未关闭主要断言时重估缺失协议和工时，不再增加同义通知/helper。工时和关键路径只在92更新，不在本指南复制日程。

<a id="round-edit-and-commit"></a>
### 每轮编辑与 Git 审阅边界（2026-10-01）

普通源码、头文件、测试和活动文档编辑使用显式 `apply_patch`，让修改路径、上下文与删除内容可审阅。Python用于分析、测试编排、证据与派生文件生成；只有明确的批量机械迁移才可用脚本写源码，且必须列明全部受影响文件、保存本轮前后差异并审查实际diff。不能用节省输出tokens作为绕过可审阅补丁的理由。

每轮实施包在统一目标检查后形成一个聚焦的本地Git提交，并报告commit、实际增删、验证范围与欠项；不为每个hunk提交或重跑测试。提交前核对暂存diff，仅纳入该轮已确认的改动，不使用全目录暂存混入原有未归属修改。产品代码在`krita`仓库，设计文档在外层仓库，两者分别提交并互相记录对应身份；本地提交不自动授权push或历史改写。

已有大量跨轮未提交状态时，先明确累积基线范围，再从基线之后记录逐轮提交。不能将相对旧HEAD的累计diff标成某一轮增量，也不能凭文件时间伪造历史提交。缺少完整起点的测试或文档要明确披露；现存源码增量证据可补充审阅，不能替代完整Git边界。基线中的归属不明文件须由用户确定范围，确认前保留原工作树与暂存区。

<a id="first-entry"></a>
## 3. 首条真实入口的资格与验收

首条受控入口选择单目标设备、direct、普通 default brush/composite、无 wrap、无 LoD、无 indirect/mask、无依赖可变目标的 source；先保留未迁移同步旁路和复杂模式的旧行为。范围由运行时实际 strategy/painter/target/composite 分支证明，不能只检查 preset 名字。异步 dab producer 和真实 scheduler 仍须参加，不能为缩小范围而换成手写像素 fixture。

在 stroke 初始化、任何写入之前选定旧模式或受控持久模式；未迁移输入/设置要有明确拒绝或既有整笔取消语义，不能半笔切回旧模式，也不能重复执行已经写入的 dab。测试必须断言确实进入目标模式、同一原事务 owner 跨 job 延续及最终释放，防止“实际跑旧路径但新测试通过”。

| 验收面 | 首条入口必需证据 |
|---|---|
| 写入与复用 | 同页重复 1/10/1000 dab、跨 worker、同页顺序与独立页并行；无真实冻结时 preparation/COW/seal 不随 dab 次数线性增长 |
| 读取与显示 | current、G0、算法需要时的 operation-start、immutable exact 各有独立断言；正常更新期间排空 cut 前 producer 和必要子任务；完整 checkpoint 不限 viewport；dirty 拒绝不丢更新 |
| 终结 | 正常 finish、第一页写后失败、准备拒绝、显式 cancel、重复 cancel、晚 guard；成功才交付一个 undo，取消恢复原结果，不能等待自身 borrow |
| 隔离与资源 | eligibility 外保留路径有控制组；测试场景中分配/失败/清理安全。默认启用前另须完整 S08–S10/BC9 的预算、压力、subset 与自主 drain 证明 |
| 实际工作量 | 同 input trace/seed/preset、accepted input、显示节奏与完全 drain；像素和 undo/cancel 结果同义，新增已修复像素差异单独说明 |

JP、BC 各项共用同一 owner 和选择协议，不为了测试另建私有 PageStore 事务。已证明等价的内部政策和转接随当前修复合并删除，owner 分支随业务接线收束；首条入口通过后只继续依赖模式迁移的外部 API 删除和全量复核，再逐项扩大到 indirect/mask/source-dependent、wrapped/LoD 等。全量目标没有因首批范围缩小而删除。

<a id="comparison"></a>
## 4. 与主干比较必须先固定工作和身份

固定正式源码对照为 `9a24ae0d8c070884fb013594191002e1a1b39a19`；每批实现前冻结当时工作树和运行库身份，包含参与构建的未跟踪源码。当前产品身份由 92 的最新实现记录维护。JP1、JP3、JP4 各自只代表冻结检查点，后续不能继续把 JP1 自动当成本批改动前代码。主干、实际改动前检查点、新改动分别用于“上游差距”和“本批增量”判断，不能混为同一个基线。

两组必须使用相同 Qt、工具链、构建选项、架构、线程数、输入 trace、preset/selection/composite、显示条件与样本规则。当前 QtCore 身份见冻结记录；旧 Qt 性能比值不能迁用。[92 §16.62](../92_br1_m6_m8_execution_baseline.md#cp0-matched-baseline-delivery)已建立固定upstream同依赖可运行对照及普通freehand代表性基线；后续复用该构建/夹具，按实际源码与运行库身份复验。完整required、canvas-visible/M/K/E与正式样本仍待补，不能填入估算收益。

现有 FreehandStrokeBenchmark 的 helper 关闭普通更新，实际 direct/indirect 模式由 preset 决定；`StrokeTester::testOneStroke` 的 `indirectPainting` 参数已不控制运行路径，不能从测试名或 benchmark 的旧注释推定模式。其总耗时只能代表经实际模式核验的 workload，不能代替本指南 direct + 正常显示入口。需先补齐相同业务输入和分段计时，再运行两组。首 dab、steady、input-to-visible P95/P99、pen-up、完全 drain、峰值实际字节与 Fresh 控制桶均保留，统计方法和门限复用 92 §14/39。

主干原本就有整笔 transaction/memento、共享 tile 的首写 COW 和重复 dab 原位写、异步 dab batching 与区域并行。评价新增代码时，分别写清“新增 PageStore 保证”“恢复原有热路径效率”“真正减少原有工作量”。不能把主干已有能力计作新收益，也不能用行数或测试数直接推导质量分数。

<a id="copy-granularity-lesson"></a>
### 4.1 性能经验：整页复制与大量小 memcpy 必须分价

后续从差额账生成优化蓝图，先用[03k第一性候选筛选](03k_first_principles_candidate_selection.md)：责任归属、结构冗余、合法删量与可回收净时间分别取得证据。未定价候选可进入有界判别实验，不能只因覆盖大责任桶就进入大包产品实施。[试行回放与技能升级条件](../evidence/br1_first_principles_selection_20261009/README.md)保留方法尚未经前瞻验证的边界。

本项目已经出现“字节量相同、执行成本相差很大”的真实反例：[冻结量化报告](../evidence/br1_upstream_cost_accounting_20261007/README.md)中，同为116个64×64 RGBA8页、1,900,544 B默认初始化，当前执行475,136次4 B memcpy，循环约1.062～1.127ms CPU；upstream从准备好的默认页做116次整页memcpy，约0.051～0.054ms。当前另外92次整页memcpy仅约0.064ms。价格是带观察扰动的固定ARM用例，不是通用memcpy延迟常数。

今后的复制、初始化和COW成本报告同时列出：

| 必须记录 | 用途 |
|---|---|
| 逻辑初始化/复制字节、实际调用次数、单次大小分布 | 识别逐像素小调用，不能仅凭MB或复制页数选瓶颈 |
| 源类型、对齐、访问/复用方式、cache与驻留状态 | 默认模式填充、已有整页copy、预克隆命中和GPU传输不是同一单价 |
| 原始数据操作体与外层分配/版本/登记/交付 | 数据搬运省0.064ms不等于删除代际只省0.064ms；反之也不能全部领取代际费用 |
| 实际编译库及关键汇编 | 动态pixelSize的小memcpy未必被编译器内联/向量化；源代码短不代表执行便宜 |
| 调用路径与阶段频率 | 未修改的旧函数也可能因新路径从setup/缓存复用转为每页调用，形成主要新增成本 |
| CPU、wall、未覆盖/等待及观察扰动 | 请求删量不是时间份额；fine-grained计时只给粗价，无内部观察的因果对照验证收益 |

本例seed+倍增块填充保持全部默认字节，每页4096→13次请求，116页少473,628次（99.6826%）；独立实验stroke CPU却只减少5.24%、wall减少6.56%。改进仍需写完同样的页，不能把调用删量当提速。任意多字节默认值、非零透明隐藏RGB必须逐字节保持，不可直接改成通用memset；不得靠共享可写默认页绕过COW、预算或晚读者合同。

经验的验证边界也要保留：该实验含一例projection更新合并，事后同更新量敏感性仍正向；undo主结果变慢、原因未定，未升生产。后续估价必须检查原控制、所有受影响格式和阶段，不能只保存正向stroke结果。项目预测和实施清单见 [03d](03d_cpu_cost_calibrated_blueprint.md)，该经验不改变正式门槛，也不将CPU小调用优势外推为GPU收益。

[§16.149实施复验](../evidence/br1_cpu_blueprint_implementation_20261008/README.md)进一步在同一二进制布局中隔离fill，stroke wall下降6.30%、CPU节省中位1.111ms；双架实际汇编确认13调用，格式/资源及Fresh/H4通过。完整静态候选约7.88% wall收益仍未取得Undo非劣资格，独立分支保存、当前只保留新发现的pin安全修复。报告必须同时保存负控制的配对绝对差、区间及中位数；区间跨0不等于证明等价，端点较短也不是删除控制的理由。独立批次的upstream比值不能与局部收益相乘后标成实测。

<a id="complete-cost-responsibility"></a>
### 4.2 性能方案以完整责任交付，不以第一个正收益结束

[03d §8](03d_cpu_cost_calibrated_blueprint.md#projection-complete-responsibility)修正了本轮实际暴露的范围问题：已经定位多层维护成本，却只将容易构造的fill做成确定方案，其余停留在条件清单。单项收益兑现不能代替最初的upstream差距目标。

选定一条业务责任后，先把已知互斥成本桶全部映射到真实consumer、必要事实、可替代表示和失败/释放边界；在同一方案中完成有依据的相邻优化及调用者迁移。保留合同不意味着保留现有对象、遍历、查询和中间表示。对主要成本只写“正确性需要”“暂不处理”，不能算覆盖；要给出更直接方案的比较、保留理由或明确未完成项。尚未证明的收益保持未定，不按零计算后得出没有空间。

测试分为开发纠错和最终性能验收。编译、受影响安全/资源测试随实现进行；完整候选形成后统一比较父版本和upstream、工作量与分项CPU、端到端wall和负控制。局部消融用于未解决的因果问题，不默认每个点单独跑完整矩阵。一个候选的启用阻塞不自动成为其它结构优化的前置；完整方案的测试也不能掩盖该候选自身的回退。

有限退出以责任表为准：已实现并验证，或有证据保留且比较过更便宜的表达；存在显著未解决项就继续标明方案未完成。用户要求尽可能优化时，不能将第一次正收益、一次局部测试通过或一个子项提交当作整个目标完成。

完整实施已形成[§16.151候选](../evidence/br1_projection_lifecycle_20261008/README.md)：五项替代一起降低Stroke，Undo却观察到回退。九行审查有处置、代码已实现、机制删量兑现、候选允许默认晋升及upstream差距关闭是五个不同结论。保存未通过候选和负结果，不用较早源码更好的结果替代最终批，也不重复加样取得资格。有限责任审查结束不意味着全部剩余成本已经证明必要。

本包还留下两个实际生命周期经验。空临时容器的析构准备也可能通过scope guard释放owner锁；materialize到注册AcquireRead pin之间的这一窗口会允许真实collector移除刚准备的历史默认页。优先移动原临时值的清理边界，不增加常驻pin/cache。配置中的源登记先于Ready存储接受，后者拒绝时必须由原source承担接续，不能重试就注册新源；应以实际容量拒绝验证已接受事实没有遗弃。安全修复增加的保证与成本计入整包，不冒充去重收益。

<a id="observation-boundary-lesson"></a>
### 4.3 细分前先给观察器定价，阶段名称不是函数单价

[剩余投影诊断](../evidence/br1_projection_remaining_cost_20261008/README.md)中，全分项时钟使同一产品投影CPU中位增加33.8%；将冷链、metadata、发布/operation分组后仍增加16.4%～25.2%。未开内部时钟时prepare+publish外层约0.407ms，内部phase开启后仅metadata_local即约0.78ms。不得将细分后的大桶视作新发现的产品成本，也不能按统一比例扣clock后制造精确价格。先用无内部时钟外层、稳定工作数量和源码消费者限制候选，再用未插桩因果对照验证净收益。

阶段标记的费用属于两个标记之间的实际区间。CommitCompletion还包含backingChanges/预算变更预备，CommitMetadataApply调用联合安装，MutationSealProofPrepare还包含writer reservation释放；标签不是完成票据、metadata或proof函数的独占单价。计数也必须与计时上下文一致，不能将全projection的188次descriptor调用配给冷链内132次调用的时间。未知余项保留未知，不统一叫锁、析构或adapter。观察器修订和分析器错误保留原始日志，只复算同批，不借机换样。

<a id="accepted-facts-lesson"></a>
### 4.4 原接受事实应随owner传递，重复检查要按失效条件判断

[管理管线审查](03e_cpu_management_pipeline.md)确认了容易漏掉的实际成本：range-for的元素为const引用，不保证容器采用const begin；当前SnapshotArray会因此detach。所谓“canonical输入共享、无额外分配”的注释必须对照实际模板行为；相邻层的排序比较器也必须一致。最小探针证明隐藏复制，但其结果不能代替产品测试或端到端收益。

重复校验是否可删应按“原接受者→事实有效区间→真正失效事件→后续消费者”判断。owner mutex暂时解锁并不撤销仍由scope/session保护的claim；可以沿原ClaimSet传递接受事实，不另建trusted标志或第二权限表。reader、last-use、驻留及metadata revision却能真实变化，不能一并跳过。空容器清理是否可不交接锁，还要核对其allocator保活及最后释放者。逐项列出可观测Δ查询/复制/锁操作，再以完整候选验证；不把混合桶全价或锁操作数当作可节省时间。

<a id="callback-copy-codegen-lesson"></a>
### 4.5 同步借用也要核对内层复制的机器码

[最低读写管线实施](../evidence/br1_pipeline_refactor_20261010/rw-minimum-pipeline-r1/READ_COPY_CORRECTION.md)把binding选择并入capture并删除重复引用后，首次未插桩确认仍见读指令增加4.11%。反汇编表明：type-erased同步回调按引用捕获复制参数，memcpy可能别名修改capture，编译器把尺寸与地址读取留在每行循环内，ARM循环由8条变25条。将请求参数在回调入口固定为局部值后恢复8条；复制量、pin和可见性不变。这是PageStore新增实现引入的费用，不能归给upstream共有memcpy，也不能以少锁/少引用宣称净收益。数量模型与最终独立批次分别记录，首次失败不可覆盖。

<a id="complexity"></a>
## 5. 何时整理代码，何时停止细化

现在完成责任与依赖审查，把并发容器的静止关闭前提、等待和回收边界写清。没有可复现缺陷时，不顺便重写第三方 map；其是否满足长 stroke 预算与尾延迟，必须由实际调用路径和测量决定。QSBR 的强制等待/整批回收在上游就存在，不能误记为本批新引入的 bug；新增 prepared-key 自旋也不能宣称 wait-free 或有界延迟。

现在审查散布的可选 owner/参数、重复 caller 分支和转换层，沿原 transaction、execution、read selection 合并责任。读取选择副本、packed/cursor 重复安装及独立交付输出已按 [实际清点](API_CONVERGENCE_MAP.md#adapter-delivery)收束；packed/cursor add窗口已闭合，其余发布族进入CP6，owner重复分支随CP7真实模式迁移删除；明确函数与迁移关系见 [API 映射 §3–§8](API_CONVERGENCE_MAP.md#read-selection)。每个新增状态/包装都必须指出实际生产消费者、独立生命周期及替代对象；无法指出的不得作为通用前置继续添加。只有依赖未迁移模式的公共签名删除留到对应模式验证后，不把全部接口压缩推迟到首条链之后。

删除旧路径必须有静态 caller、callback/override 和运行时消费者清单；仍承载未迁移模式或故障恢复的路径继续保留并注明原因。生产行数、分支与包装数量只作复杂度趋势，不设“净删多少行即通过”的伪指标。

同一批达到已登记行为和检查后冻结结果，更新剩余项并结束。新失败先判断是本批回归还是下一入口的范围；前者修复，后者只有符合 §2 的阻塞规则才扩大本批。不要把每次 review 都转成继续开发一个新子层的任务。

<a id="delivery"></a>
## 6. 统一结果与文档维护

每批只在 92 更新当前裁决；主题指南保留函数责任，入口索引链接 92；证据目录按源码身份冻结，不覆盖旧日志、不把旧的“下一步”再次当作当前任务。文档导航维护不算实现收益。

```text
范围：原修改 ID / 92 条款 / 本批要关闭的可观察问题
身份：HEAD + 包含新源码的 diff；Qt/配置/库/插件/测试哈希
对照：upstream / 前检查点 / 本批；相同与不同的 workload 条件
已交付：真实 caller → owner → 写入/读取/显示/finish/cancel/drain
证据：实际命令、case、原始日志；失败样本与通过样本的区别
成本：复制/分配/准备/锁等待/回收/峰值；真实 stroke 分段指标
复杂度：原函数→最终职责；新增函数理由；已迁移 caller；删除的签名/重复 body；保留对象的消费者及退出触发条件
剩余：阻塞哪个入口或阶段、实际代码端点、完成判据
裁决：局部能力 / 开发入口 / 默认启用 / 正式资格，逐项写明
```

未运行、未测量、未闭合分别写清；不得把“无新失败”写成全面正确，也不得把文档检查、smoke、局部 probe 和正式矩阵相加制造总通过数。

本次 JP3 匿名 root 提交的有限交付与撤回项见 [清点 §8](CONVERGENCE_CHECKLIST.md#jp3-delivery)。硬性重试次数不能代替原 owner 接续；局部读进度通过不能改写发布一致性、完整 gate 或 M8 的剩余门。

JP4 本批把页与派生 extent 收敛到原 overlay 候选，并删除事后补 extent；具体处置见 [清点 §9](CONVERGENCE_CHECKLIST.md#jp4-delivery)。后续 fresh raw 子范围已按 [清点 §11](CONVERGENCE_CHECKLIST.md#fresh-read-delivery)关闭，继续 manager extent 的联合窗口，保持原 claims、读意图和锁序；不要因本批通过而提前给真实 brush 默认传入持久 owner。
