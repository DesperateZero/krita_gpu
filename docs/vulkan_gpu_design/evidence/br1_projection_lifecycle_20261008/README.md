# 完整投影生命周期优化：统一候选验收

产品父 `a918e45e028c426874d9aa13d8080f2d69170d9f`，文档父 `506f60da750cb5ef7fe06a903b7f35c4868db088`。本包沿03d九行矩阵完成全路径审查，五项可构造替代共同形成候选，并修复默认页读回收交接及provider配置拒绝后的原源接续。最终整包Stroke收益成立，但Undo观察到回退，**只在 `codex/br1-projection-lifecycle-candidate` 保存候选，不晋升原分支、不宣布M6通过**。最终提交/树/运行库身份见[delivery](delivery-identity.json)。当前检出候选，原 `refactor/brush-s2-predefined-sanity` 仍在a918。

## 实施与保留

[PLAN](PLAN.md)逐行记录原owner、实际consumer、更直接表达的比较及保留原因；[协议](PROTOCOL.md)及[配置修复后的最终批协议](PROTOCOL-config-fix.md)在对应采样前固定样本量、分母、停止及负控制规则。较早read-fix库的11.17% Stroke结果保留在[中间报告](REPORT-read-fix.md)，不与最终批混合。

| 同一投影责任中的改动 | 已完成的生产者→消费者→释放迁移 | 机制核算 |
|---|---|---|
| 两步metadata转换 | preparePrivateWrite与publishPrivateWrite用栈上连续输入；coordinator同步借用，Reference全部调用迁移；原状态机及复验保留 | 132准备+132发布，各去shared-control/vector两次分配，共528次 |
| 同步provider完成事实 | 配置一次Ready；default/copy/payload/alias/transfer在真实操作成功后返回；每allocation的Pending retirement仍独立，实际free后完成 | 投影completion allocate264→132，去132次ready记录分配及完成；新增常量事实发生在provider配置 |
| overlay输入 | seal原write-set直接生成候选最终输入，删除生产者临时vector与复制/free；泛型单项入口同一个builder | 32次非空overlay输入，各去一个临时数组；候选拥有型最终值仍必要 |
| 物理slot索引 | 原Payload节点内嵌slot树hook；prepare/track/ack/untrack和dirty列表终结一起迁移 | 132个物理记录各少一个独立slot节点分配/free；hook增加原节点大小，不声称整个旧节点字节均删除 |
| 默认fill | 现有pin修复上替换公共fillWithPixel；任意BPP/default字节及copy/rows保持 | 投影60页，memcpy调用245,760→780；整笔116页单列 |
| 读回收交接修复 | 默认物化临时descriptor map由外层read栈持有，注册AcquireRead pin之后在owner锁外清理；竞争物化被回收时重新选择 | 无常驻缓存/新owner；不另领取性能收益，其开销包含于整包 |
| 配置拒绝接续 | 原completionSource/completions保留已接受的源登记；Ready存储拒绝后恢复仍用原源，拒绝换registry | 不增加重试状态或队列，不遗弃源记录；真实容量拒绝测试验证 |

前四项合计核算投影**824次**动态分配请求及其生命周期归还；这是源码表达×实际执行数量，不是全进程malloc计数，也不等于824次同价操作。整笔相应核算**1,307次**，不与投影相加。132代际和物理页数、60投影fill、32overlay没有减少；canonical commit与capture受匿名client时序影响有波动，不能将这些波动计成已删除责任。

保留项有具体边界：clear之后的调整层/filter/selection读者与独立失败结果；锁外provider准备后的source/domain/预算复验；公开commit输入与原proof一致性和epoch重基；target准入全集、实际changed、仅缺失wrapper及sparse presence的不同寿命；accessor建立时的oldData快照cut。详见PLAN各行；这些保留结论不等于已经证明当前算法是最低成本。

## 理论、实际与剩余差额

事前只有fill局部约0.55ms有独立价格，结构项有确定删量但没有同版本时间预测。最终投影粗诊断父/候选/upstream中位CPU为**5.133/4.422/0.398ms**；四对节省分别为**0.528、0.684、0.809、−1.821ms**，配对中位**0.606ms**。候选有一次6.986ms慢值，细诊断也有一次6.925ms，全部保留。按边际中位数描述，额外差距由4.735降至**4.024ms**，约关闭**15.0%**；这不是具有置信下界的投影收益率。四对不足以稳健定价，不取前三对、不用中间批的0.801ms覆盖最终结果，也不拼接旧5.322/4.739ms分母。

| 事前数量预测 | 实测细粒度包围CPU中位（父→候选） | 可作出的结论 |
|---|---|---|
| 60页fill，4096→13调用/页 | 0.560→0.043ms | 与原约0.55ms局部规划价相符 |
| 264个两步输入，删除528次分配 | prepare0.315→0.235，publish0.249→0.165ms | 删量兑现；保留的状态机/容量/复验仍占主要部分 |
| 132个ready记录消失 | allocate0.100→0.057，complete0.032→0ms | 剩余allocate对应逐allocation退休；配置常量票据不在Stroke内 |
| 132个slot独立节点消失 | physical record0.061→0.041ms | 全部physical record仍需建立，非删整条冷链 |
| 32个seal生产者数组消失 | overlay builder0.087→0.099ms；完整seal0.599→0.575ms | builder是保留的最终候选，临时生产者删除不保证该子函数降时；未单独授因果价 |

这些是同一细诊断中的包围成本，存在嵌套、observer成本和不同过程的中位数；**不能相加当整包收益**。cold包围CPU2.248→1.515ms，而cold self约0.882→0.883ms；剩余descriptor/backing/binding/metadata登记未被这五项消除。候选seal约0.575、commit约0.555、capture约0.359ms也仍在。提交数父11～14、候选10～15受anonymous client时序影响；不把其差当确定删除量。

因而可支持的结论是：整包能降低实际Stroke成本，fill之外的机制删量兑现，但本批没有把结构项逐一隔离成因果时间价格。当前证据仍不支持“已经达到upstream投影效率，只是其它负担抵消”。剩余约4.02ms分布在保留代际的准备、发布、读保护及外框，不能把每项称为不可避免，也不能把整桶称为理论空间。下一结构问题是这些owner/不可变发布保证是否能在同一合法段内用更少事实交接兑现；再次减少小容器不能冒充已找到全部核心。

未插桩完整候选对父版本（20个ABBA块/40对/80过程，区间为pointwise双侧95%）：

| 端点 | wall收益及区间 | CPU收益及区间 | 配对CPU节省中位 |
|---|---|---|---|
| Stroke | **9.89% [8.43,11.31]** | **8.28% [6.71,9.84]** | **1.614ms** |
| Undo | **−5.06% [−9.10,−1.20]** | **−4.17% [−7.60,−0.86]** | **−0.018ms** |
| Redo | 35.51% [33.89,37.12] | 32.44% [30.60,34.27] | 0.479ms |
| Teardown | 5.16% [2.27,8.73] | 4.43% [1.60,7.81] | 0.034ms |

Undo wall/CPU回退区间均未跨0，已观察到回退，且不能满足≤2%的负控制；不能只称“未证明非劣”。Undo边际中位wall0.542→0.560ms、CPU0.691→0.702ms，配对增加中位9.5/18µs；这些估计的单位和统计量不同，均保留。最终两组各80过程的工作量均满足19更新，没有排除样本。20块/20,000次bootstrap、seed261028，仅ARM本用例；不是多端点family或正式M6资格。

独立未插桩upstream比较同为20块：候选Stroke wall为upstream **1.950× [1.891,2.025]**，CPU **1.946× [1.887,2.023]**。这是实际新比较，不是旧upstream比值乘局部改善率。

固定M5受保护控制全部通过：Fresh四桶吞吐比下界（ARM K1/K16、Rosetta K1/K16）**1.357/1.198/1.422/1.225**；H4为**1.488/1.403/1.470/1.514**，均≥0.98。每桶40对/20块、50,000次bootstrap、单侧98.75%，各四桶family至少95%；这八桶不是八个新的正式M6格。

裁决：机制删除成立，整包Stroke/Redo收益成立，Fresh/H4通过；Undo回退阻止默认晋升。配置拒绝修复属于新源码，依事前补充协议开独立最终批；不把较好中间结果择优当最终结论，不追加样本追求越门。下一启用阻塞是Undo交付/读取/回收的实际新增成本归因，不预设它一定来自fill或本包某一个容器。

## 容量与代码成本

[容量协议](CAPACITY-PROTOCOL.md)及[六过程结果](capacity-v2-results.json)独立于计时批。实际preparePayload收费由**160→144 B/记录**，投影132记录少2,112 B的分配请求总量；物理record仍存在、同时驻留数不固定，不能当峰值减少2,112 B。能力过程后固定P/C/C/P，MetadataArena从setup开始的累计峰值为父4,583,412/4,519,444 B，候选4,507,684/4,553,764 B；一对降、一对升，不证明整体峰值下降或metadata≥25%通过。Stroke末live父4,515,108/4,448,404 B、候选4,440,676/4,440,164 B，后台回收时序会改变这一观察。

Stroke末process storage均1,160,612 B；Teardown末父1,149,988/1,150,084 B，候选1,149,860/1,150,276 B。存在原process/static寿命尾，不是零尾容量、RSS或全部payload峰值。容量观察库重新计时无效，未将这些过程加进性能样本。容量工具初次缺少头文件搜索路径的编译失败保留，v2只修派生工具后执行原样本数。

产品12文件合计+221/−117；生产10文件**+128/−87**，测试2文件**+93/−30**，无生成物进入产品。新增内部reader重载/共同builder用于同步消费原write-set，新增一个provider Ready字段和原Payload内嵌hook替代重复记录；没有新owner、恢复队列、缓存或主干public/protected API。净增不是复杂度下降的充分证据，收益与Undo代价按实际控制裁决。

## 安全及原始失败

- 最终候选库SHA256 `2442a100b543448c798e71ddfe6f9eb18625013aabc65f8e1d57f2e6e3aec9de`。双架八组，合计**9,222通过/0失败/0跳过**，均验证实际加载库；Reference946、CpuMutation1595每架均通过。覆盖字节oracle、预算拒绝、alias/旧视图、并发、swap、晚reader和最终释放。
- 最终结构检查通过；21 manifest、25 ownership facts、16 runtime census、2214 indexed APIs、29035 reverse edges，6项审计器测试通过。没有提高ratchet或以源码行数替代性能资格。
- dev-01的两项Ready容量/合并假设更新为新真实边界；旧失败日志保留。单节点余量现在可准备物理退休，零余量仍拒绝；最后一个Pending完成后终态区间合并，不能要求中间任意退休立即降低元数据live。
- dev-01与首次完整safety-arm64分别复现默认页读失败。根因窗口是物化后的空descriptor清理也会解锁；强制真实collector在旧窗口介入复现49通过/1失败，新清理点50通过，最终双架完整组通过。不是通过重跑忽略偶发错误。
- read修复两次编译失败及外部复现工具一次编译失败均保留；dev-read-fix误在失败构建后启动，实际使用旧库，明确以INVALID.md作废，不领取最终资格。修复后新命名批才有效。
- 配置失败复核补足原源接续；新增实际容量断言验证先登记成功、Ready分配拒绝、恢复后原源成功及更换registry拒绝。dev-config-fix曾只捕获unstaged两文件，SCOPE.md披露其身份不足；最终冻结改用git diff HEAD，12文件、运行库、完整安全及新计时批共同绑定。

## 复算与范围

`run_dev.py/run_safety.py`冻结安全库及源码；`build_diagnostic.py`从各自源码和实际对象生成观察库，后继build脚本只替换对应单元；`force_read_collection.py`是外部调度干预，不进入生产。`run_comparison.py`保留逐进程命令、环境、实际退出、timeout/reap、像素、阶段、事件和加载哈希；`analyze.py`只分析既定样本，最终分析选config-fix批。Fresh/H4沿用固定M5原runner及分析器。完整源/库/逐过程日志/原失败以四个≤64MiB分片保存：[00](raw-evidence.tar.xz.part00)、[01](raw-evidence.tar.xz.part01)、[02](raw-evidence.tar.xz.part02)、[03](raw-evidence.tar.xz.part03)。在本目录执行 `cat raw-evidence.tar.xz.part* > raw-evidence.tar.xz` 后解包；[分片清单](raw-evidence-parts.json)、[逐文件清单](raw-manifest.json)和[EVIDENCE](EVIDENCE.json)保存各级哈希。仓库中较早报告只说明其冻结源码。

完整候选的局部收益、受保护控制和正式M6分别裁决；M6/M7/M8的0/3、正式校准2/20、metadata同义分母和完整CP0缺口不因本包自动改变。
