# CP3 控制容量、保活引用与实际寿命追踪（2026-10-06）

**本轮把上一批的管理热点落实到实际调用来源与寿命，并补上 native Fresh/handoff 的同口径调用数量。优先方向仍是原控制容量准入/结算和 working→projection→publication 对象传播的整包收敛；仅减少 provider 分配或只消除几次 allocator 参数复制，均不足以获得主门收益承诺。没有修改产品，也没有新的优化速度结果。**

产品保持 `6ffe097909e23adf3afd229a2a14e93986fae00b`，固定M5及现行性能门不变。当前裁决接续92 §16.129；CP3/M6未通过，persistent默认关闭。

## 1. 固定范围与实际执行

[事前协议](protocol.json)冻结7种负载、2个顺序平衡块、每格原库control/追踪库两侧，共 **28个顺序进程**：public N64/K1、N1024/K16、N64/K16；native Fresh/handoff各K1/K16。全部actual exit0/reaped、指定image实际加载、像素/extent或旧新exact/物理增量/close、public复制与generation/seal/session/commit检查通过，源码/库输入前后SHA相等。

只机械插桩一个budget TU，复用原374个image对象；原库、产品源、预算判断、收费、引用增减和失败政策保持。固定数组记录调用栈、线程、阶段、对象地址和实际capacity，没有逐调用时钟。[生成器](prepare.py)、三个精确helper/TU补丁、[构建身份](diagnostic-image-01/identity.json)和[执行结果](results.json)可核对。首次分析误读`atos -inlineFrames -d`的地址分隔符，保留`analysis.log`；修正解析后分析同一批原始事件，没有重跑/补样/删除进程。

14个追踪进程共 **358,815事件**。这是重插桩数量实验，所有时间均排除，不和上一批未插桩CPU或正式40对吞吐混合。public分别追踪首写及64次未追踪预热后的单次写入；后者不是旧250ms循环平均。native保持原N=K/H0/B4、一份相同exact验证view和完整first-write→seal→canonical commit。两块native主要计数完全一致；public N1024/K16主要计数也一致。K1及N64/K16的状态/后台差异保留。

## 2. public K16：优先链条与对象分布

N1024/K16后次写入，两块均为 **524控制请求、446套local/parent prepare与settle、988次fits、6157次deref**，与上一轮稳态数量一致。524中78次经`budget==nullptr`进入原process storage，仍有原process收费；本次地址寿命匹配只覆盖另外446次controller-backed成功分配，不能把78次写成未收费。

| 原责任中的引用周转 | 每op deref |
|---|---:|
| working replica/version/state/result | 2640 |
| projection及其局部准备 | 1296 |
| metadata publication及其局部准备 | 633 |
| 三者合计 | **4569 / 6157 = 74.21%** |

直接callsite包括working replica析构800、working version析构480、working version构造432、`kisPageReplicaValue`288、`kisPageVersionValue(version)`240次。`MetadataArenaGrowth`的构造/析构也在原projection/publication链中。保留16个物理frame及解析出的inline frame；本次被测主线程control request/success和deref全部可归属。public N1024/K16仍有36个fits及各2个prepare/settle、native每次2个raw free未归到具体责任，原栈和数量保留；总事件/数量不因分类缺口被丢弃。摘要首次要求所有事件均可归属的断言失败，随后明确报告覆盖边界，未把未分类项强行归桶。

这说明仅盯实际malloc会遗漏大量临时allocator保活。原working value允许嵌套数组移动和moved-from复用，实际晚free仍依赖retained owner；计数不证明可以把所有allocator换成裸指针。下一对象设计须区分原owner始终保活的短命scratch、移入prepared publication的值，以及真正逃逸的保护/尾对象。

带controller的446次成功分配按近端原责任分布为：provider96、publication/descriptor61、write protocol51、epoch49、retirement48、metadata publication38、read link32、completion32、owner ledger17、projection16、store/adapter6。这些是分配所在责任，不能把阶段父子重复相加，也不意味着同一类的所有对象寿命相同。

## 3. 寿命约束排除了“整操作统一释放”的捷径

对public N1024/K16后次写入，地址顺序匹配两块结果一致：446次controller-backed成功分配中，**144次在该操作阶段内释放，257次在后续验证/manager销毁阶段释放，45次到捕获结束仍未闭合**。操作内释放144包含37次worker释放；操作内释放只是观察到的时序，不能据此推定同一锁域或统一owner。provider的96次全部跨过操作终点；retirement48、completion32也有原尾责任。不能把整批446个对象塞入一个在commit立即释放的scratch arena。

45个未闭合主要是epoch根/控制尾，本轮没有联合final drain端点，不能判为泄漏。native捕获截止原close调用之后、局部Store/其它对象的C++析构之前，未闭合尾同样明确保留。全线程phase是时间窗口，不是所属事务；worker释放可与主线程并发。public首写后追踪关闭的64次warm区间不做跨gap地址匹配，首写剩余标为unobserved gap；后次写入连续追踪到manager销毁。没有发现连续捕获区间的歧义地址复用。

因此预算优化需要以**原owner下可证明共同准备、实际容量和兼容寿命的一组对象**为单位。必须保持parent/child总账、prior waiter公平、限额改变、任一步分配失败的归还、最后物理free再退费。不能通过跳过无变化预算类、总票后不追踪实际容量，或把尾对象提前free制造收益。

## 4. native K16：handoff已经减少分配，共同保活链仍大

下表是完整begin transaction→首写→seal→canonical commit的主线程数量；两块各自完全一致，不是CPU或wall占比。

| 事件 | Fresh | handoff | 数量降幅 |
|---|---:|---:|---:|
| 控制请求 | 471 | 313 | 33.55% |
| fits完整检查 | 893 | 624 | 30.12% |
| local/parent prepare各自 | 405 | 279 | 31.11% |
| retained owner deref | 5830 | 5286 | **9.33%** |

handoff主要把acquire区间从294控制请求/572 fits/2704 deref，降到138/304/2160。**seal两侧均74请求、116 fits、1629 deref；commit两侧均1489 deref**（Fresh100请求/199 fits，handoff98/198）。因此seal+commit共3118次deref，占handoff **58.99%**；其314次fits占handoff **50.32%**。这补强共同管理的定位，但没有得到native互斥CPU时间或可删除比例。

handoff中的working/projection/publication三类deref合计4829/5286（91.35%）；recoverable publication的独立claim、revision复验和取消保证仍有真实consumer。它们不能因为计数多就合并可见性边界，也不能把public的64–66μs投影搬到native证明30%可达。共同优化会同时缩小Fresh分母，现有性能失败原样保持。

## 5. dense和状态残差

N64/K16后次写入仍构造64个root节点及64个shared control，N1024/K16为22+22；加dense manifest，root来源恰多85个请求。两块N64总请求分别609/601、fits1158/1142，而N1024均524/988：第二块少8个`MetadataPageActivity`节点申请，来自projection准备的既有容量/清理状态，deref仍为6328。该差异有实际callsite，不能抹为随机噪声，也不能用平均每页malloc乘全部N/K。

旧dense选择仍是可独立证实的局部缺点；N1024主门没有它，native N=K时dense与union节点量相同。保持次优先级，不以修dense代替共同管理主包。

## 6. 下一方向、收益边界与有限退出

| 顺序 | 完整候选责任 | 本轮新增依据 | 实施前必须给出的证据 |
|---|---|---|---|
| 1 | 原控制容量准入/结算与working→projection→publication的表示、交接一起收敛 | public 74.21%、handoff91.35%的deref落在该链；handoff共同seal/commit计数大体不减 | 原consumer/容量/lifetime图；哪些临时表示和重复准入实际删除；逐组预测ΔA/Δfits/Δref及保守成本，保留原失败/晚尾 |
| 2 | 在原prepared owner内合并兼容寿命的控制容量准备 | 446个成功对象只有144个观测到操作内释放，257有可见晚释放 | 每组原owner、收费域、准备与释放边界；不得按总数盲合成operation arena；保留分配失败和公平边界 |
| 3 | root的dense/sparse选择、K²去重 | 原root85请求放大再被callsite证实；不是所有场景主因 | 独立有界工作预测；不得重领已经交付的sparse批量算法 |

第一、二项是同一完整存储责任的两个视角，不应变成各自新增owner/缓存/队列。可先消除实证重复表示，随后评估合法分组；尚未证明具体分组方案可行，本轮不启动容器重写。

上一批原库CPU中`deref` leaf仅约8–9μs/op，整个budget+owner链约64–66μs/op；这两个口径是包含关系。只减少构造参数的引用，不能据此承诺承担原Fresh ARM约21.8μs wall缺口，更不能把64–66全部当收益。provider `prepareAdoption` inclusive约13–15μs且包含必要工作，单独改其几个节点也没有覆盖缺口的证据。数量少33%并不推出延迟少33%。

下一完整候选先预注册预测调用减少量，在原同义输入下作有限因果验证；预测不兑现或未插桩CPU/wall不跟随则停止该候选，不追加样本直到过门。无需重新跑未改动产品的完整安全矩阵；真正产品候选再按受影响责任验证。

**置信边界：** 调用来源、shared阶段和本次观测寿命的证据较强；安全可删除比例、锁等待、最终drain、Rosetta和真实stroke的收益仍不足。该轮没有生成新的正式置信区间，也没有优化前后速度比较。原Fresh K16/handoff门、metadata驻留同义分母及CP0 required欠项不变。

## 7. 复核

[数量与不变量摘要](summary.json)、[分析器](analyze.py)与[summarize.py](summarize.py)保留全部行。[原始归档](raw-evidence.tar.gz)包含完整`attribution.json`及各进程归因、28份fixture日志、14份事件与地址映射、完整符号表、分配/free匹配、原始栈、分析失败及最终日志；`raw-manifest.json`逐member绑定。大体积逐调用归因只在压缩归档保留，避免重复提交相同派生表。符号表是对实际运行image地址的解析缓存，重放分析无需重新运行业务。原始事件、调用栈中的本机代码地址只用于该诊断，不加入产品。

`evidence-manifest.json`绑定源/补丁/helper、实际构建和运行身份、分析与原始归档；不提交对象或dylib。活动文档更新只记录当前裁决，未变更门槛或阶段资格。
