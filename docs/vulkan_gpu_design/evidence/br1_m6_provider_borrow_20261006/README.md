# M6冷准备延后、已有provider借用与固定窗口验证

产品父`79e1c8d1eff509e683c120df25861eb21512fb5f`，最终`38834c4e26`，文档起点`2614383c1`。[事前设计](PLAN.md)先于产品修改，[协议](protocol.json)和[冻结身份](freeze.json)先于新样本。B1–B3/V1–V2有限包完成：冗余查找/冷构造数量全部兑现，当前安全/资源/结构通过；同库hit4/4、miss16/16数值过门，原控制8/8。**校准仅2/20等价，其余18桶证据不足，完整性能资格及M6仍未通过。** 原库父子仅ARM K1 native pin确认小额增益，K16时间增益未确认。

## 算法必要成本与当前差距

source必须保持exact身份与原物理排斥，independent before必须保活且可读，所有可失败accounting/metadata/descriptor准备仍须在最终claim前完成。实际有两处额外工作：已知native pin拒绝时仍构造/销毁整组冷Prepared；before与source来自同一provider时，逐页从ledger重新取得调用方已经保活的provider，并附加一组shared retain/release。

原native consumer在Mutation::Private::provider持有强引用，原generic consumer在acquireWrite局部provider持有强引用，均跨整个共同plan与cleanup。原registry按id/epoch唯一接纳，不存在此调用中可替换同身份live provider的第二权威。physical token也继续保活source provider；因此相同id/epoch的before可直接借用参数，不需要重复ledger查找。不同provider仍沿原ledger取得强引用，到before read pin释放及全部prepared析构后才释放。

| ID | 当前改动与consumer闭包 | 保留责任 | 状态 |
|---|---|---|---|
| B1 | 原plan中的physical调用栈值移出冷Prepared，后者只在physical observation合格后emplace | cleanup在owner gate外先reset physical，再释放before pin/其余冷状态；异常恢复原gate | 完成 |
| B2 | before id/epoch与已验证source相同就借用传入provider；foreign才查原ledger | 参数强引用与原native/generic admission跨解锁工作；所有identity、epoch/revision和最终claim保留 | 完成 |
| B3 | 原productionRecoverableHandoff增加32个跨provider数据行，含四BPP、generic Preserve/Discard和四终结 | Fresh准备被拒时必须成功handoff；旧读、像素、取消/abort/restore及两provider close payload归零 | 完成 |
| V1 | 原16完整CPU/manager/业务目标、Freehand/read/foundation及6个安装/存储探针 | 原预算、安装零分配、epoch/晚读/失败/close；原ratchet未放宽 | 38个QTest进程11180/0/0，资源/结构/6工具自测通过 |
| V2 | 原库父子、开关校准、同进程配对hit/miss和固定M5控制 | 64ms有效操作窗口、40独立配对、固定family与停止规则 | 固定矩阵完成；hit4/4、miss16/16、原控制8/8，校准2/20；不追加样本 |

生产1文件**+19/−13，净+6**，测试1文件**+28/−4**，另有两个派生审计文件。不增加公共API、持久字段或owner；原beforeProvider字段仅在确有foreign provider寿命时持有引用，未创建平行账本。必要physical局部值和冷Prepared仍归同一调用栈，不延长恢复域。

## 事前数量预测与实测机制

另行40个机制进程，父/子两架、K1/K16及五形状，每进程两个独立完整样本。只在复制的一份coordinator TU加两个TLS调用点计数，正式原库/开关性能镜像没有这些计数；原phase observer仅机制scope启用。

| K16形状 | 父[before ledger lookup,cold Prepared construction] | 候选 | 原recoverable阶段 |
|---|---|---|---|
| hit | [16,16] | [0,16] | Prepare/Prepared/Install/Installed/Cleanup仍[16,16,16,16,16] |
| native pin | [16,16] | [0,0] | 仍[16,0,0,0,16]；必要source观察与cleanup不是零 |
| single | [0,0] | [0,0] | 仍零尝试 |
| generic lease | [0,0] | [0,0] | 上一包已提前拒绝，仍零尝试 |
| pending last-use | [0,0] | [0,0] | 上一包已提前拒绝，仍零尝试 |

K1按K缩放，两架预测全部兑现。这里统计的是具体调用点执行次数与局部对象构造，不是allocator请求或独占CPU比例。减少的附加shared retain/release由被删除的shared返回值寿命推导，未冒称独立ref计数器观测。foreign实际安全consumer通过原新数据行验证，其强引用不能删除。

未给未测单价赋值，上一包native pin的1.927/4.771μs同库净差不作为本包全部可删预算；原库父子未插桩实测负责确认增量，新的同义on/off残差负责门项判断。不同批次、不同统计窗口的点估计不能相减充当本包因果收益。

## 计时分辨率与固定实验

上一包K1每进程128个内部测量仅约1～3ms有效计时，K16约十几至几十ms；setup/检查/close占进程生命周期多数，小额差异的区间跨界不能直接归因成产品回退。新协议在采样前固定每arm累计至少64ms操作wall及至少128个完成操作，不按置信区间追加时间。

每个内部样本仍重新初始化一/两份独立exact副本，保持N=K、H0且一个exact旧View、64×64 B4 Preserve完整首写，计begin transaction→mutation/full memset→seal→canonical commit。完整旧/新字节、实际copy/payload/budget、保护释放、Store close/析构及drain每样本检查；setup、校验/close、drain单列。原始每操作wall向量保留，另列首/末budget与逐类观测max，类max不能相加为同时峰值。

| family | 固定规模/独立单位 | 估计与判据 |
|---|---|---|
| 原产品父子增量 | hit/native-pin×两架×K1/K16共8桶，40对，各arm独立进程且满足64ms | 20平衡双对log完成率块，50k bootstrap/seed261008，双侧99.375%，family名义95%；lower>1确认增益 |
| 开关等价校准 | 全20桶40对，原候选库/正常on开关库分进程 | 20块/50k/261008、双侧99.75%；区间完全落在[0.98,1.02] |
| 同库hit | 4桶40独立配对进程，进程内两arm逐样本交替，初始顺序跨进程反转；两arm各≥64ms | 40个进程配对log中位延迟比，20k/261008、单侧98.75%下界>0 |
| 同库miss | 16桶40独立配对进程；相同完成数，两arm逐样本交替、完整退出后才开始下一样本 | 20个预注册平衡进程块/50k/261008，单侧99.6875%完成吞吐下界≥0.98 |
| 固定M5 Fresh/H4 | 原public fixture，每family4桶40对、原250ms完成率 | 原50k/seed260926/单侧98.75%，lower≥0.98 |

窗口内部循环不作为独立统计重复；同库配对的一个进程是一个独立pair，原库父子与校准仍以两个进程形成pair。pair/顺序块和family纠正均在新样本前固定；与上一包的两个独立进程设计分别保留。开关只在复制TU的discoverBefore前禁用发现以走原安全Fresh，其余374对象复用；诊断parent/current镜像另行，不用于性能裁决。arm64原生，x86_64为Rosetta。

## 安全、身份与剩余资格

当前38个QTest进程**11180 passed、0 failed、0 skipped**，比父源码原完整范围新增每架32个cross-provider数据行。每架安装/publication/storage原资源探针各1个，实际加载本轮候选，全部通过；二进制与源码继承原资源包，未声称重编未改fixture。结构87 TUs、2211 APIs、28983 edges、27 callbacks，原21 manifest/25 ownership/16 census/19 intrusion及6工具自测通过。

计时结束后，新CPU测试二进制加载冻结父库，原productionRecoverableHandoff全部112数据行及init/cleanup在两架各114通过，合计**228/0/0**；这两个合同控制进程单列，不计性能family。它证明foreign路由合同优化前后保持，不能用其通过证明时间收益。[源码寿命证明](source-review.json)与[最终身份核验](verification.json)绑定本包。

## 无插桩增量、当前残差与裁决

[全部统计](summary.json)保留原始估计量和完成数。下表原库父子使用双侧99.375%区间，8桶family名义95%；只有下界>1才确认增益，跨1不证明等价。四个正常hit控制均跨1，没有确认增益或清晰回退，不把其中位点写成实际改善。

| 原库父子native pin | 当前/父完成吞吐 | 区间 | 配对中位延迟节省μs（辅助） | 裁决 |
|---|---:|---|---:|---|
| ARM K1 | 1.017628 | [1.005179,1.029219] | 0.11475 | 增益确认，点估计+1.76% |
| ARM K16 | 0.986012 | [0.962196,1.034246] | 0.63600 | 时间增益未确认，也不能证明2%等价 |
| Rosetta K1 | 1.002026 | [0.985088,1.008416] | 0.03075 | 时间增益未确认 |
| Rosetta K16 | 1.019786 | [0.997210,1.031245] | 2.52025 | 时间增益未确认 |

吞吐由全部实际操作wall和完成数计算；中位延迟节省是另一辅助估计量，不能用其正值覆盖吞吐区间。例如ARM K16配对中位延迟略降，但完成吞吐点略降且区间宽，不能只报有利指标。

| 同库合格hit | 延迟减少点估计 | 单侧98.75%下界 | 配对中位节省μs |
|---|---:|---:|---:|
| ARM K1 | 6.233% | 6.176% | 0.709 |
| ARM K16 | 17.451% | 17.244% | 21.208 |
| Rosetta K1 | 6.453% | 6.322% | 1.208 |
| Rosetta K16 | 19.283% | 19.188% | 38.521 |

同库miss **16/16**达到单侧99.6875%吞吐下界≥0.98，family名义95%。native pin K1/K16下界为ARM **0.987168/0.983279**、Rosetta **0.988718/0.980792**；K16相对关闭handoff的配对中位额外wall仍为**1.8335/2.58325μs**，不宣称拒绝零成本。必要source观察、binding排斥及gate往返继续存在，其他single/lease/last-use保持原早拒绝。

开关校准用原候选产品/正常on镜像分进程比较，20桶各双侧99.75%区间须完全落在[0.98,1.02]。仅**ARM K1 single、last-use**满足，其他18桶全部跨边界且全部包含1，没有清晰非等价证据，也没有等价证明。结合对应校准，hit **0/4**、miss **2/16**同时满足数值和校准；其余不授予正式资格。summary中的same_image_hit/miss布尔仅是数值判据，[门项差集](required-matrix.json)记录联合校准限制。

固定M5 Fresh/H4各4/4通过。Fresh K1/K16下界为ARM **1.291933/1.091681**、Rosetta **1.365179/1.112009**；H4为ARM **1.486474/1.356007**、Rosetta **1.412692/1.457472**。这是当前累计产品对固定5173的受保护控制，不能归因成本包增量或替代开关校准。

理论方面，K16成功的16次重复lookup与附加引用、native pin的16次lookup及冷构造均已删除，成功仍保留16次必要冷准备。这是明确的实现差距收束，未给未测单价赋值。实际方面，只在ARM K1确认+1.76%吞吐增益，其约0.115μs配对中位延迟节省是辅助点估计；K16收益未确认。新协议同时改变有效窗口与配对设计，miss由上一包6/16变成数值16/16不能全部归因这次代码修改，也不能将跨批百分比相减作优化收益。

## 固定完成范围与下一主项

预注册流程共**3824实验运行进程**（preflight104、独立机制40、正式性能3680），全部正常退出/回收及身份通过；另有上述父库合同控制2个。正式窗口3840个arm、**9424983个完成操作**，每arm至少64ms，实际最少190个完成操作；这些内部操作不算独立统计重复。21项冻结文件、2504项候选输入、复制TU/镜像及各自374个复用对象均核验；提交后完整产品diff仍与冻结patch一致。正式样本无profiler、阶段时钟或诊断计数，所有失败/命令/原始ns向量保留，不扩样。

64ms与同进程配对已让同库小额残差更清楚，分进程校准仍宽；目前不能区分镜像扰动与进程间环境变异，也不能仅靠“窗口更长”宣布已解决测量问题。下一先为校准建立独立可证伪诊断，固定相同fixture的无改动同镜像控制、进程次序/慢变因素与完整wall分布，并先验证控制是否能分辨±2%；正式新协议仍须采样前冻结。不要给本包追加样本、扣除校准偏差或继续无已确认K16预算的provider/容器重写。metadata同义驻留分母与CP0完整required并行取证，资格完整后再更新92阶段表。

本包不是新的完整TSAN/平台/CP0资格，也没有自然业务正例或GPU实测。metadata实际驻留≥25%重构前同义分母、CP0完整required、自然producer/业务分布与M7/M8/GPU/默认策略分别开放。有限候选完成后冻结本包，不用无改动重复矩阵或可选扩样延长收口。

全部原始命令、日志、每操作ns向量、诊断源码及身份收入[原始证据包](raw-evidence.tar.xz)，[逐成员清单](raw-evidence-manifest.json)核验**7231项、展开470737848B、压缩26710248B**，已逐成员读回校验。产品提交及Git blob身份见[交付记录](delivery.json)；活动92/指南的新链接、暂存范围和文档核验另列，不改冻结实验输入。二进制/dylib/object/dSYM留本机并记录哈希，不作为源码证据提交。
