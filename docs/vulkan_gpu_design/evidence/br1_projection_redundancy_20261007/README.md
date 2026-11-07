# Projection重复准备：确定删除量与收益预测复核

本包将上一包的热点定位推进到数量证明和产品修改：**局部default clear不再把逻辑默认的稀疏页实体化**。同一普通freehand的root准备149→132、复制89→72、pin245→228，减少17代际、17复制和278,528 B逻辑复制。node工作不变。未插桩ARM stroke点估计下降0.71%，95%区间跨零，**尚未确认真实时延收益**；M6未通过。当前阶段权威仍为[92](../../92_br1_m6_m8_execution_baseline.md#projection-redundancy-delivery)。

起点产品`128fb32a71fef69f462da2c2dfa8d187ed94db52`（生产同`38834c4e26`），外层父`2a94f65dd`。产品最终提交和实际源码/库身份见[source-identity.json](source-identity.json)，改动前库见[parent-identity.json](parent-identity.json)。同一个未插桩MatchedFreehandBaselineTest用于增量比较，Qt、libui和插件保持；不借upstream差距宣称本次加速。

## 从全链条件上限到合法删除

[事前诊断协议](PLAN.md)从原merger/backend/PageStore三个TU派生独立诊断库。最终v3采用固定8192项POD buffer，在业务/清理结束后dump；两过程各643项，无溢出。恢复原19次projection更新，累计计数验证stroke149代际、undo0、redo56，无temp projection。诊断覆盖本例仍活着的root，不能推广到所有模式。

每个merge按实际成功准备的页分组，clear准备页是composite准备页的子集，合计并集96，存在**53条直接source链**：clear的新generation成为随后composite的source，观察区间未见另一merge在同页开始新准备。若能合法共享整个merge的原写入作用域，条件上限为149→96代际、89→36复制，少868,352 B复制、13个clear session。当前独立可见性、失败和并发合同尚未联合证明，53不是已获准删除量；原transaction也已合并部分canonical commit，不能按session数许诺发布下降。

其中17条clear没有native source：逻辑默认页被局部清为同一个默认值，本来就是空操作。原fillRect只对整页检查default；把判定扩至部分页，可在既有managed range与固定before视图下直接跳过，保留原准入、adapter交付、拒绝和取消边界。没有新增owner、API、锁或缓存。其余36条链留作有界候选，不为它们立即引入跨merge事务。

## 实施与验证矩阵

| 位置/consumer | 实际修改或保留 | 证据和结算 |
|---|---|---|
| backend fillRect逐页分支 | 整页/部分页共用default判定，逻辑默认页跳过实体化；非default/native部分页仍原COW | 唯一生产修改：8增/3删；固定机制4过程数量兑现 |
| manager clear唯一fillRect caller；projection调用链 | 沿原clearRect、extent、range、adapter/delivery与dirty流程；不增加入口或共享scope | 同像素、8 segment/4 update callback、owner销毁；merger两架24项通过 |
| 失败/取消/重叠准入 | range先于before取得；resolve拒绝仍失败；无操作页保留range直到原batch终结 | 完整manager覆盖ClearRangeAdmission、CancelledPrivateClient、ClearBarrier等原反例，两架2638项通过 |
| 稀疏/格式/历史/旧读 | 新增BPP1/4/8/16×history开关8行，非零默认值、extent中间稀疏洞；default clear不分配，非default fill必须写，边缘/旧读/undo/redo保持 | 新测试加载parent库8/8按预期失败；candidate完整manager通过；Reference两架1892项通过 |
| 原底层机制与其它consumer | prepare/seal/provider/claims/selector、handoff及其它fill路径无新策略 | 原protected Fresh/H4两family重测8/8通过；结构门另见[verification](verification.json) |

[修改前清单与预测](IMPLEMENTATION_PLAN.md)保留原文本；本表结算其全部有限位置。产品3文件64增/3删，其中测试56增、生产8增/3删。未实现全merge共享责任，也未修改默认persistent策略。

## 理论预测与实际结果

| 项目 | 修改前预测 | 实测/最终判断 |
|---|---|---|
| root准备/复制/default初始化 | 149→132 / 89→72 / 60不变 | 两次parent及两次candidate完全兑现；session32不变 |
| node准备/复制/pin | 76 / 20 / 2420保持 | 完全兑现；node普通session27、canonical commit1保持 |
| 两manager合计准备/复制 | 225→208 / 109→92 | 兑现，复制−278,528 B；初始化116页保持，不是DRAM流量测量 |
| 原时间估价 | 17条clear及后继composite准备合计0.322833/0.312337 ms；条件wall约0.97%/1.94%/3.87% | **净删除估价偏高**：必要default初始化从clear移到composite，不能把两段准备全删；事后修正与原输出均保留 |
| 修正条件模型 | 原17个composite重复准备0.085166/0.081504 ms，均值0.083335 ms | 假定必要初始化单价相同，关键路径25%/50%/100%时约0.254%/0.508%/1.017%；另扣新增resolve，seal/回收/等待变化未定价。不是CI或实测CPU收益 |
| 全53共享scope候选 | 重复composite准备0.406041/0.430626 ms | 均值0.418334 ms；条件关键路径100%约5.10%，剩余36条约0.335 ms/4.09%。没有合法共享合同或关键路径证明，不能领取为最终收益 |

正确的净准备模型是：before有clear allocation+default-init及composite allocation+copy；after仍需composite allocation+default-init。初始化成本相同的条件下，只剩一个原duplicate preparation可删。新partial-default查询会增加成本；未定价seal/retirement减少和调度变化可改变净额。**数量可准确预测，最终wall不能只用页比例推出。** v3线程CPU含时钟查询、allocation/copy/metadata，嵌套在operation CPU内，不能相加；全projection的28% Running样本仍不是可删预算。

未插桩[固定比较](run_comparison.py)先四能力过程，再两架各24对/12顺序块，共100过程，全部像素、callback、owner和加载身份通过。主端点为stroke-to-projection-ready；20,000块bootstrap/seed261018，pointwise双侧95%诊断区间，固定结束，无删尾或扩样。

| 架构/端点 | candidate/parent延迟比 | 延迟降幅及95%区间 | 裁决 |
|---|---:|---:|---|
| ARM stroke主端点 | 0.992888 [0.974041,1.013705] | 0.71% [−1.37%,2.60%] | 未确认正收益；48过程均19次更新 |
| Rosetta stroke主端点 | 0.988387 [0.958566,1.026803] | 1.16% [−2.68%,4.14%] | 未确认；parent有3次18更新，candidate有5次，保留全部样本，不作纯数量消融归因 |
| ARM setup诊断端点 | 1.013348 [1.000124,1.033665] | 变慢1.33% | 保留回归信号；7端点未作family校正，不能断言原因是新增resolve |
| ARM total fixture | 1.011825 [0.999354,1.030471] | 变慢1.18%，区间跨零 | 不用setup主导的total抵消或宣称stroke改善 |

pen-up/undo/redo/teardown以及Rosetta setup/total区间均跨1；详见[comparison-summary.json](comparison-summary.json)。原预测修正在结果之后完成，只是解释与下一模型，不重新定门、不改变timing统计或追加样本。实现保留为低风险的稀疏页工作消除，不能包装成显著业务加速或M6收敛主解。

## 安全、原控制、失败与复现

candidate完整manager/merger/Reference各两架，共**4554/0/0**；新增parent反例为2 pass/8 expected fail单列。安全首批merger因runner误用仅brush插件目录，blur filter为空而SIGSEGV；保留原log/IPS/退出，修正为既有完整build/bin插件，仅继续余下五过程。没有用失败批充当完整通过。

原固定M5 Fresh和H4保持原40对/桶、20块、50,000 bootstrap/seed260926、单侧98.75%/lower≥0.98；两个family640过程完成，**8/8桶通过**。Fresh lower ARM K1/K16=1.276289/1.093756、Rosetta=1.295699/1.084088；H4为1.422321/1.374346及1.422363/1.401804。它们是当前累计产品对固定M5控制，不是本次增量收益，也不补正式M6校准。

诊断失败全部保留：两个observer编译修复；首轮两过程诊断缺请求的dylib alias，加载原库/零事件，停止；v2四过程热JSON/recorder改变调度为17更新/143代际，不能混入原19更新估价；v3四过程低扰动恢复原数量后停止。产品新测试首次编译因clear重载隐藏失败，改用已有五参数入口后通过。原成本估价的事后修正保留[旧输出](analysis-revision-0/comparison-summary.json)于原始归档。所有测量过程实际退出和reap保留。

复现顺序：parent冻结→build_diagnostic/run_diagnostic各修订批→analyze→按IMPLEMENTATION_PLAN修改/构建→run_safety两环境批→run_comparison mechanism/performance→run_controls fresh/history→analyze_comparison/analyze_controls→run_structure→freeze_evidence。证据目录排他创建，不覆盖本包重跑；归档包含库、夹具、源码、命令、原日志、失败和身份，见[raw-manifest](raw-manifest.json)。

有限包已停止。剩余36条链需要原读者/范围/失败语义下的可构造共享设计，再判断约0.335 ms的条件准备预算是否足以覆盖成本；若不成立则转向画笔准备与其它projection结算的独占成本，不以2420次pin或28%样本猜改缓存。正式校准仍2/20、联合hit0/4、miss2/16；metadata实际驻留分母、完整CP0/业务/GPU证据独立开放。原全安全11180/0/0与6资源探针属于旧冻结版本，本包不声称重跑该完整矩阵。**M6/M7/M8仍0/3，persistent默认关闭。**
