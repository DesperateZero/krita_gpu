# 完整投影生命周期优化：统一候选验收

产品父 `a918e45e028c426874d9aa13d8080f2d69170d9f`，文档父 `506f60da750cb5ef7fe06a903b7f35c4868db088`。本包沿03d九行矩阵完成全路径审查，五项可构造替代共同形成候选，并修复验收暴露的默认页读取与回收交接缺陷。不是以第一个局部正结果结束，也不声称全部相对upstream成本都已证明必要或可删。

## 实施与保留

[PLAN](PLAN.md)逐行记录原owner、实际consumer、更直接表达的比较及保留原因；[协议](PROTOCOL.md)在性能采样前固定样本量、分母、停止及负控制规则。

| 同一投影责任中的改动 | 已完成的生产者→消费者→释放迁移 | 机制核算 |
|---|---|---|
| 两步metadata转换 | preparePrivateWrite与publishPrivateWrite用栈上连续输入；coordinator同步借用，Reference全部调用迁移；原状态机及复验保留 | 132准备+132发布，各去shared-control/vector两次分配，共528次 |
| 同步provider完成事实 | 配置一次Ready；default/copy/payload/alias/transfer在真实操作成功后返回；每allocation的Pending retirement仍独立，实际free后完成 | 投影completion allocate264→132，去132次ready记录分配及完成；新增常量事实发生在provider配置 |
| overlay输入 | seal原write-set直接生成候选最终输入，删除生产者临时vector与复制/free；泛型单项入口同一个builder | 32次非空overlay输入，各去一个临时数组；候选拥有型最终值仍必要 |
| 物理slot索引 | 原Payload节点内嵌slot树hook；prepare/track/ack/untrack和dirty列表终结一起迁移 | 132个物理记录各少一个独立slot节点分配/free；hook增加原节点大小，不声称整个旧节点字节均删除 |
| 默认fill | 现有pin修复上替换公共fillWithPixel；任意BPP/default字节及copy/rows保持 | 投影60页，memcpy调用245,760→780；整笔116页单列 |
| 读回收交接修复 | 默认物化临时descriptor map由外层read栈持有，注册AcquireRead pin之后在owner锁外清理；竞争物化被回收时重新选择 | 无常驻缓存/新owner；不另领取性能收益，其开销包含于整包 |

前四项合计核算投影**824次**动态分配请求及其生命周期归还；这是源码表达×实际执行数量，不是全进程malloc计数，也不等于824次同价操作。整笔相应核算**1,307次**，不与投影相加。132代际和物理页数、60投影fill、32overlay没有减少；canonical commit与capture受匿名client时序影响有波动，不能将这些波动计成已删除责任。

保留项有具体边界：clear之后的调整层/filter/selection读者与独立失败结果；锁外provider准备后的source/domain/预算复验；公开commit输入与原proof一致性和epoch重基；target准入全集、实际changed、仅缺失wrapper及sparse presence的不同寿命；accessor建立时的oldData快照cut。详见PLAN各行；这些保留结论不等于已经证明当前算法是最低成本。

## 理论、实际与剩余差额

事前只有fill局部约0.55ms有独立价格，结构项有确定删量但没有同版本时间预测。本次投影粗诊断的父/候选/upstream中位CPU为**5.167/4.329/0.431ms**，配对节省中位**0.801ms**（四对范围0.765～1.103ms）；按本批边际中位数描述，额外差距由4.736降至**3.898ms**，约关闭**17.7%**。这是有限机制诊断，没有给投影收益概率区间；不拼接旧5.322/4.739ms分母。

| 事前数量预测 | 实测细粒度包围CPU中位（父→候选） | 可作出的结论 |
|---|---|---|
| 60页fill，4096→13调用/页 | 0.559→0.050ms | 与原约0.55ms局部规划价相符 |
| 264个两步输入，删除528次分配 | prepare0.321→0.257，publish0.247→0.179ms | 删量兑现；保留的状态机/容量/复验仍占主要部分 |
| 132个ready记录消失 | allocate0.105→0.054，complete0.034→0ms | 剩余allocate对应逐allocation退休；配置常量票据不在Stroke内 |
| 132个slot独立节点消失 | physical record0.058→0.038ms | 全部physical record仍需建立，非删整条冷链 |
| 32个seal生产者数组消失 | overlay builder0.089→0.098ms；完整seal0.621→0.591ms | builder是保留的最终候选，临时生产者删除不保证该子函数降时；未单独授因果价 |

这些是同一细诊断中的包围成本，存在嵌套、observer成本和不同过程的中位数；**不能相加当整包收益**。cold包围CPU2.306→1.573ms，而cold self约0.905→0.913ms；剩余descriptor/backing/binding/metadata登记未被这五项消除。候选seal约0.591、commit约0.582、capture约0.370ms也仍在。提交数父12～14、候选11～12受anonymous client时序影响；不把其差当确定删除量。

因而更强结论是：fill之外的重复维护删除有增量价值，但当前证据仍不支持“已经达到upstream投影效率，只是其它负担抵消”。剩余约3.90ms分布在保留代际的准备、发布、读保护及外框，不能把每项称为不可避免，也不能把整桶称为理论空间。下一结构问题是这些owner/不可变发布保证是否能在同一合法段内用更少事实交接兑现；再次减少小容器不能冒充已找到全部核心。

未插桩完整候选对父版本（20个ABBA块/40对/80过程，区间为pointwise双侧95%）：

| 端点 | wall收益及区间 | CPU收益及区间 | 配对CPU节省中位 |
|---|---|---|---|
| Stroke | **11.17% [7.97,15.90]** | **9.28% [7.21,12.20]** | **1.516ms** |
| Undo | 0.61% [−3.97,5.05] | −0.05% [−4.16,3.90] | 0.001ms |
| Redo | 33.27% [30.55,35.68] | 29.82% [27.14,32.25] | 0.427ms |
| Teardown | 2.98% [0.03,5.95] | 1.44% [−1.83,4.49] | 0.005ms |

Undo wall/CPU退化上界分别3.97%/4.16%，未证明≤2%；点估计接近零不等于非劣。边际中位Undo wall0.533→0.5445ms、CPU0.673→0.679ms；这些边际差与配对估计不同，均保留。父组有一次projection_updates18，upstream组有一次20，其余19，全部保留未筛样，不扩样到通过。

独立未插桩upstream比较同为20块：候选Stroke wall为upstream **1.947× [1.905,1.990]**，CPU **1.918× [1.877,1.965]**。这是实际新比较，不是旧upstream比值乘局部改善率。

固定M5受保护控制全部通过：Fresh四桶吞吐比下界（ARM K1/K16、Rosetta K1/K16）**1.373/1.198/1.404/1.205**；H4为**1.481/1.444/1.478/1.506**，均≥0.98。每组40对/20块，各四桶family至少95%；这八桶不是八个新的正式M6格。

裁决：机制删除成立，整包Stroke/Redo收益成立，Fresh/H4通过；Undo非劣仍未闭合，完整优化保留候选资格，不升为原分支默认实现，M6不通过。没有重复相同样本批追求越门。

## 安全及原始失败

- 最终候选库SHA256 `3f6248c2f6ac8cda8842d7cefe8989bbc66089cec0ed306a40f9c6f24eda2539`。双架八组，合计**9,220通过/0失败/0跳过**，均验证实际加载库；Reference946、CpuMutation1594每架均通过。覆盖字节oracle、预算拒绝、alias/旧视图、并发、swap、晚reader和最终释放。
- 两轮结构审计均通过；最终21 manifest、25 ownership facts、16 runtime census、2214 indexed APIs、29013 reverse edges，6项审计器测试通过。没有以源码行数替代性能资格。
- dev-01的两项Ready容量/合并假设更新为新真实边界；旧失败日志保留。单节点余量现在可准备物理退休，零余量仍拒绝；最后一个Pending完成后终态区间合并，不能要求中间任意退休立即降低元数据live。
- dev-01与首次完整safety-arm64分别复现默认页读失败。根因窗口是物化后的空descriptor清理也会解锁；强制真实collector在旧窗口介入复现49通过/1失败，新清理点50通过，最终双架完整组通过。不是通过重跑忽略偶发错误。
- read修复两次编译失败及外部复现工具一次编译失败均保留；dev-read-fix误在失败构建后启动，实际使用旧库，明确以INVALID.md作废，不领取最终资格。修复后新命名批才有效。

## 复算与范围

`run_dev.py/run_safety.py`冻结安全库及源码；`build_diagnostic.py`从各自源码和实际对象生成观察库，后续两个build脚本只替换对应单元；`force_read_collection.py`是外部调度干预，不进入生产。`run_comparison.py`保留逐进程命令、环境、实际退出、timeout/reap、像素、阶段、事件和加载哈希；`analyze.py`只分析既定样本。Fresh/H4沿用固定M5原runner及分析器。最终清单、原始压缩包与提交身份在验收结束后冻结。

完整候选的局部收益、受保护控制和正式M6分别裁决；M6/M7/M8的0/3、正式校准2/20、metadata同义分母和完整CP0缺口不因本包自动改变。
