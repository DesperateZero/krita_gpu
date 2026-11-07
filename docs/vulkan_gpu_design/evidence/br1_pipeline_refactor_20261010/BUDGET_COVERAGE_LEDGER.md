# 沿预算图补数：plain慢态、资源寿命、入口及压力

2026-10-11；产品仍`11c6895ddf`，同依赖upstream仍`9a24ae0d8c`。原[预算图](PERFORMANCE_BUDGET_LEDGER.md)的11.962375ms主账保持，新批独列。生产/产品测试改动0；实施状态仍只有[原33项](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-change-index)。

**补到了资源数量和寿命证据，尚未关闭整套机制净账。** 真正plain仍有慢态；64格中60格同义，4格坏尾导入不等价；原库冷压力断言失败，事件与暖态控制支持首次运行时增费。H1资源观察门仍失败，以下峰值/时长属于观察运行，不能移授原库或CPU净收益。

后续[慢过程归因](SLOW_PROCESS_ATTRIBUTION.md)已用同过程内核计数捕获其他入口的自然慢态，并以H1对称干预验证执行条件放大；旧32.070ms仍是推断，未事后补造其内核记录。后续自然H1计数门通过不追认本批资源观察门，以下冻结数值保持。

![预算图补账：周转与峰值分开，标出已补证据和未闭缺口](budget-closure.png)

[可缩放图](budget-closure.svg) · [作图脚本](build_budget_closure_view.py)

## 1. 固定分母与失败

| 批次 | 分母及用途 | 裁决 |
|---|---|---|
| 公共矩阵r4 | 4能力＋4镜像块，共36过程；每过程64case，每case四manager寿命 | 自身断言、加载身份、退出和回放全通过；跨实现同义60/64 |
| 其中plain | 原始库，无派生钩子；fixture外层时钟及即时drain | 真正原库诊断；64case顺序与旧八case不同，不替换主图 |
| 其中resource | 12098796条事件，5557317个身份成对退出 | CPU观察门20/64通过；H0/H1均未通过 |
| System Trace | 一次基础能力、两次业务追踪；仅外部case signpost | current前台64case闭合；upstream缺前台线程，不授等待差额 |
| 压力 | 六组原有测试，每组plain/resource各一次，共12过程 | 682通过、2失败、0跳过；两次为同一冷基线断言 |
| 冷尾判别 | 隔离测试副本加marker一次；原库暖序控制一次 | cold 2/1/0、warm 5/0/0；不抹掉原失败 |

Qt数含初始化/清理和data行，不是独立样本。公共性能以四块为单位，100000次bootstrap、seed20261011、pointwise95%，不授联合多重比较资格。原始失败均保留：r1 protected `purge`未暴露导致编译拒绝；r2累计1048576事件触及容量后abort；r3环缓冲修正后current完整通过，但upstream缓存命中误记pool退出，身份回放拒绝。r4修观察锚点后另开固定批次，不拼前批样本。身份路径改为冻结副本的记录也保留。System Trace的dylib重叠警告保留，不使用栈/地址归因。

## 2. 真正plain慢态

`current−upstream`，ms/完整case/四寿命，含即时drain：

| 用例 | 四块均值 | 配对中位 [95%] | current观察on−off [95%] |
|---|---:|---:|---:|
| K16/W16/H0 | 16.116625 | 13.83650 [13.66650,23.12700] | −8.4090～0.6155 |
| K16/W16/H1 | 14.028875 | 11.93675 [11.43900,20.80300] | −8.1835～1.6310 |

H1八个plain current过程为12.220、32.070、13.306、13.795、12.898、12.769、13.281、13.342ms。index11慢态发生在**原始库**，不是资源钩子或此前mode0派生路径才能产生。64case按事前1.5倍规则标出20个side/case慢态，包含冷启动格，不能全部归为同一种异常。[机器账](budget-coverage-summary.json)保留原数据。

两次追踪的128个case signpost齐全。current 27262条目标线程状态可逐case无缺口拼回wall：H1前台15.078ms＝Running11.548761＋Interrupted0.733948＋Preempted0.758465＋Blocked1.780534＋Runnable0.256292ms；fixture前台CPU12.274625ms。不能把wall−CPU全部叫锁等待，也不能把Running当可删管理成本。

upstream只导出102条目标状态，前台tid未出现，H1整段1.519ms无前台覆盖；**不是upstream无等待或CPU为0**。current追踪H1进程CPU17.645ms，也不是plain index11的32.070ms。未把同一个慢过程的工作/内核状态连上，因果仍开放。本包按上限停止；下一B需更换并验证双侧完整、低扰动且能关联同一慢过程的方法，不续采本批等慢态。

## 3. 资源峰值：累计周转与重叠存活分开

范围来自八个正式resource过程，所有线程共同重叠；不是RSS，不包含观察器缓冲。

| K16/W16/H1资源 | current累计建立 | current峰值 | upstream / 退出 |
|---|---:|---:|---|
| 活跃payload，含4个默认对象 | 1092 | 49个＝802816 B | upstream132次、峰值33个＝540672 B；两侧case末0 |
| provider allocation / binding / owner backing | 每类1088 | 每类48 | case末0；无同名upstream实体 |
| sealed proof | 1088 | 32 | case末0 |
| metadata / 已安装descriptor | 每类1152 | 每类48 | case末0；含default及最终容器退出 |
| 实际CompletionInterval | 1096 | 49 | case末0；记录不等同于仍Pending的ticket数 |
| retirement record | 1088 | 48～49 | case末0 |
| epoch tree node | 128 | 32 | case末0；H0则1088建立、峰值32～64 |
| PageStore物理管理存储 | 28155～28171次 | 2049696～2122656 B | start/end均1115024 B、5个runtime存储 |

payload累计多960次，峰值多16个（262144 B），不能用960×16KiB估可省驻留。H0峰值current33～81、upstream33；held-clone/read的RGBA8格current49～86、upstream33，回收交错和保留合同均会改变峰值。

管理峰值含已有1115024 B进程runtime，相对case起点增量为934672～1007632 B。它与metadata/root/proof等逻辑行重叠，不能相加。容量含对齐/前缀；payload pool-slot只覆盖已取用槽位和缓存，不含Boost池未取用备用块，**完整allocator/RSS峰值仍未闭**。其他BPP留下的缓存跨case存活，不命名为本case泄漏。

| H1闭合寿命 | 每过程平均值范围 |
|---|---:|
| 活跃payload | current377.476～403.630µs；upstream310.675～364.274µs |
| binding / provider allocation / owner backing | 约368～394µs |
| proof | 142.856～153.047µs |
| retirement record | 387.011～413.220µs |
| epoch tree node | 1354.717～1463.132µs |
| metadata / 已安装descriptor | 约332～356µs；cohort存活积分/建立数 |

有身份项目逐birth/death匹配；metadata/descriptor只有总量事件，不伪造个体分位数。机器账另列closed p95/max、跨case退出、start/end及右截断。管理存储区间截至free入口，payload截至归还cache入口，**不是完整系统物理释放或物理驻留时长**。

H1观察器CPU/前台门失败，数量/寿命仅绑定resource模式。native guard、pending-read及adapter尚未全部获得独立类型标签；共同管理存储不替代类型级全寿命。原库峰值/保留时长移授和合法净预算仍开放。

## 4. 入口与压力合同

原八case＋14入口×1/4/8/16 BPP：full、partial、no-op、default、change-default、clear、purge、committed-source copy、clone、history、成功/坏尾导入、raw、held-clone/read。核对成功/拒绝、像素hash、presence、extent、default。copy只用已commit源，未绕过live-source exact-view缺口。

**60格同义。坏尾导入4格都返回false，但current清空内容，upstream保留已读16页。** 保留差异，不作为PageStore同义性能。成功导入与旧公共42点不能外推坏尾合同。

[64格逐项表](BUDGET_ENTRY_MATRIX.md)各自列完整端点；验证读/hash/presence均计入，不能横比不同family总时长当入口单价榜。新增普通family各做一次主要操作，held-clone做16次覆写；原八case按W。原始`writes`字段在新增family仅是夹具参数，实际次数以源代码和此处说明为准，不从该字段推算法倍率。

压力覆盖：预算上限与root保留；swap-in失败、partial取消/重试、导入拒绝；handoff准备满额/并发消费者；进程分配/read-capture拒绝；满额关闭；held reader/pin/retire/swap miss/provider revoke。除下一节冷基线断言外均通过。reader组还实际观测140条generic active-read、峰值14、最终0、最大寿命583.750µs；不能推定native guard同数同价。[压力机器账](budget-pressure-summary.json)保存每组峰值/寿命，当前独有合同不冒充upstream性能分母。

## 5. 573680 B冷尾账

原库和resource的`processStorageRejectsAndRetains`均在12474行失败：baseline581124 B，退出1154804 B，差573680 B。此前完整组通过不覆盖独立冷顺序。

隔离测试副本仅在原baseline/断言前加marker，保留失败。期间新增物理管理存储557056 B和240 B，没有旧块遗漏退出；两块均在进程退出时释放。源码`ReclamationExecutor::ensureClockLocked`首次建立全局deadline monitor，512KiB线程栈按对齐/前缀实际占557056 B，另有clock控制；原生pthread控制按页收费。

```text
573680 B = 557056 B（新增栈存储）+ 240 B（新增控制存储）
         + 16384 B（普通管理分配器钩子未覆盖的记账差）
```

后项与源码原生线程控制收费一致，尚未独立打类型事件，不冒称三项都直接测得。原库先执行`storeRootStorageRetained`再执行该测试得到5/0/0，支持baseline漏计首次monitor初始化。原失败仍保留；冷/暖测试基线需单独修正，本轮未改原测试或删除样本。

## 6. 回到预算图

| 缺口 | 本轮新增证据 | 尚未闭合 |
|---|---|---|
| plain慢态 | 原库32.070ms慢态保留；current追踪状态逐case闭合 | 同一慢过程因果、upstream前台追踪、全锁/等待 |
| 峰值/保留时长 | payload与多数管理实体的重叠数、寿命、进程尾、原预算历史峰值 | 观察扰动移授、池备用块/RSS、native/pending read/adapter类型、每类reservation独立峰值和时长 |
| 其他入口 | 64格固定矩阵，60同义；4坏尾差异明确 | 坏尾合同选择、旧live-copy缺口、多规模/稀疏/并发组合及独占机制价 |
| 压力 | 六组682/2/0；两种新条件支持具体573680 B初始化尾 | 原冷断言修正、长期压力/尾延迟分布及类型空格 |
| 全设计E | 复用模型可用真实重叠数量约束 | A/B/C/D仍有明确缺口；净可删ms仍null，不选最优方案 |

不因960次周转、48个live身份或2.8万次管理分配而直接预报CPU收益。M6/M7/M8 0/3、校准2/20、默认关闭及旧控制裁决保持。

复现：[事前协议/调整](RESOURCE_COVERAGE_PROTOCOL.md)、[构建](build_budget_coverage.py)、[环缓冲修订](revise_budget_coverage.py)、[upstream锚点修正](fix_budget_pool_anchor.py)、[公共runner](run_budget_coverage.py)、[分析](analyze_budget_coverage.py)、[压力](run_budget_pressure.py)、[冷尾](probe_budget_cold_tail.py)、[压力分析](analyze_budget_pressure.py)、[追踪](run_budget_trace.py)、[追踪分析](analyze_budget_trace.py)、[复核](budget-coverage-audit.json)、[原始包与重建](BUDGET_RAW_EVIDENCE.md)。
