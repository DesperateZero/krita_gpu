# 完整管线重构：实施身份与验证约束

## 当前整包成本账（11c689，cost-ledger-r0，采样前冻结）

本轮补齐原T08.2的当前分母与互斥阶段账，并复核T02.4发布责任预算；不增加第二进度矩阵。产品固定11c6895ddfeae074df727c76dcbf9e12988479ee，原重构前8198c36ed722030edae715b7423554036bf1bcf7与同义upstream9a24ae0d8c070884fb013594191002e1a1b39a19保持原库/夹具。当前库先核验与read-terminal-six-r2-arm64最终安全库一致。只重编当前ABI夹具和原取消共有clear融合的business派生merger；产品源码、对象与测试不修改。

整包存储/业务各3个capability＋8块×6个三方镜像顺序过程，共102过程。沿原run_net_price的seed、输入、四manager寿命、8存储case、8段/4callback/19 projection、像素/undo/redo/销毁断言、120秒超时、kill/reap与加载库核验。任一语义或身份失败停止该批，不删除失败或追加样本。构建、采样、分析串行，不与另一基准同时运行。记录主机背景负载旁证，不据其删样。

统计单位仍为配对块，各侧块内两过程均值；收益与upstream差额用配对块中位数、100000次seed20261011 bootstrap pointwise95%区间。预先保留全部8case及五业务阶段，不挑正端点。另对成本账使用块差额的算术均值：存储setup/write/read/finish/undo/redo/teardown加显式case外框残差，业务五阶段加进程外框残差，逐块核对加和误差小于1e-9ms。前台thread CPU与同期其他线程CPU分别入账；后者不得归给某个worker。中位数收益不能加到均值账，跨批局部收益不能累加。新增账是对当前总差额的阶段归属，不将其自动称为可删除机制预算。

发布责任另用当前库的两个原粗scope（seal中间处理、完整commitOwnedLocked）作有限诊断。当前派生库mode0/2各capability＋8块×4镜像过程共34过程，复用原观察器、标签及33次非空成功发布断言。目的仅判断该两个直接责任能否解释当前业务数毫秒级差额，不为小额优化发放净预算；预定区分精度为0.75ms，on−off的95%区间须完全落在±0.75ms，方可报告该精度下的责任规模。即使通过，也不等价于旧±0.2ms门通过；新结果不得补授旧候选资格。报告观察CPU及误差敏感性，不能将observer on/off区间当单个scope的严格误差界；间接GC、锁竞争及调度影响仍需单列，不能由commit内部成本排除整个发布管线。没有足够精度则保留未知并停止，不扩样到通过。

交付回填原33项：必要工作/被删机制/新增保证及其实现工作/真实命中/已测时间/剩余未知，公共优化与PageStore基础成本分账。独立所有权正确性必要不证明逐producer独立发布是最优；旧共享匿名事务有失败反例，不能恢复作为合法基线。整包、局部责任与正式M6分别裁决；本批仅ARM64诊断，不授联合门、默认启用或GPU资格。

发布观察同时计数每次原commit循环的真实尝试、root/directory/descriptor/metadata重准备及非空proof/removal/surface输入；只增加局部计数并随原scope输出，不增加每次尝试的时钟采样。标签在原owned map销毁前固定，避免观察器读取已释放记录。重准备次数是工作放大证据，不凭次数推断等待或可删除时间。

## 当前存储写/读责任分解（cost-ledger-storage-work-r0，采样前冻结）

三方总账和发布观察完成后，有限延伸到原T03/T04/T06/T07的存储责任：同当前11c689派生库、原公共存储夹具，增加operation、pixel callback、cold prepareTarget、seal、capture、readBytes、captured release粗scope，沿用commit及intermediate。实际语义、case数量、四寿命和所有断言不改；按线程父子关系只加exclusive CPU，原case前台CPU减去所有scope的exclusive和为显式未归属残差。读取scope中的capture/归还不能再与read inclusive相加；写入操作所包scope与外部finish/undo/teardown按原调用树区分。该观察没有upstream同名机制价格，不把当前责任时间直接当额外或可删时间。

mode0/2各capability后8块×4镜像过程，共34过程；偶块0/2/2/0，奇块2/0/0/2，块奇偶反转8case执行顺序。每个case后仅dump并reset观察器，reset要求全部frame结束；容量与事件数校验，scope跨phase、嵌套不守恒、跨thread错误或任何像素/库/退出失败即停止。唯一新增观察器reset在case计时之外。原33项及产品不改。K16/H0和H1完整前台on−off各报告pointwise95%（100000次seed20261011），仅当各自区间均落在±0.75ms时，才按这一粗精度解释责任规模；分别也报告write/read扰动，不把合计抵消视作局部无扰动。没有通过则保留该端点未知，不补采。本诊断不授小额净收益、严格下界或M6资格。

## T07无历史通知：有界候选（cb942，实施/采样前登记）

**r1查询原型撤回，尚未采性能或计数。** 复核92 §16.163的既有否决后，重复getter不是足够新的候选；r1仅完成ARM64 5227/0/0安全组，两条父版本真实背压反例保留。下一r2直接消费原metadata ReleaseRead/AcknowledgeLastUse/ReleaseCapturedVersion接受时已持shard锁可知的historyCount，短寿命transition result携带historyNeedsRevisit；不保存第二事实，不再查shard。ReadCoordinator在原Store gate内立即requestKey（noexcept，分配失败由原rescan可靠接受），之后只泵原collector。last-use尚未结束不发通知；同一completion已由首个ack清完的其他record不重复通知。发布之后产生的历史仍由原D或后续保护释放通知，历史默认/captured abort的首次实际释放能直接观测，不依赖事先有work。

修改/删除索引收敛为MetadataCoordinator原两个保护转换及短寿命result→ReadCoordinator原release/ack/captured三个接受点→HistoryCollector原requestKey。删除r1 hasHistoricalVersions及其查询分支，删除collectUnreachable的candidateKeys/count参数与无条件候选循环，全部生产caller改为仅pump/scanAll。测试手工初始化Historical的六处改为显式requestKey后pump，原真实存储拒绝、补扫及退休断言不变。结果flag只在接受的保护移除并有history时置位，不作为回收权限；不在metadata内部回调collector。原release token/versionReleased和物理清理失败继续由原record接续。

本轮最终机制/净价只对r2事件传递候选采样，沿下方固定4观察＋68净价规则，不对r1重复取样。理论新增为原锁内计数读和结果bit；没有新增锁/查找/数组/持久状态。价格仍须实际检验，不能沿用此前getter探索收益。下方r1文字保留为已撤回的事前备选。

代码复核否决“所有生产者已登记，因此read只能requeue”的前提：ensureVirtualDefaultLocked/ensureDefaultPageLocked的AttachHistoricalDefault，以及abortLocked/cancelPrivateWrite保留captured Prepared的分支均会产生Historical而没有登记work。commitOwned的接受后cleanup解锁窗口也早于登记；restore则实际在解锁前登记。不能用work缺key证明无历史，也不为本候选增设逐生产者通知协议。

比较更直接的表达：collectUnreachable的candidate循环在原Store gate内，先查询原work；已有work保持原重排，缺work才锁metadata shard读取既有historyCount。无历史时不分配work、不入ready；有历史保持requestKey原登记/失败rescan。新私有hasHistoricalVersions仅用于此入口，不在visitPageKeys持shard锁的callback/requestKey里调用。无新字段、返回状态、owner、队列；原publication/default/abort责任不变。query与后续动作同在原Store gate内；晚发布者仍按原D登记，不把新查询当永久缓存或回收授权。

此为原T07/T08.2下的有限候选，不是已经定价的产品优化。预计每次候选多一次work查找，缺key多一次shard锁/页查找/计数读；只删除当时无历史的节点创建、入队和空slice，不预报删除全部706–818剩余节点。新查询净价未知，无毫秒点预测。保留真实历史的首次通知、已有work/repeat、bad_alloc全N恢复、metadata拒绝、物理退休和close；这些不是无效分支。

先用真实读cancel/release、硬满metadata与原真实history拒绝/重验/默认页/captured/close测试验证；再以相同计数点的4过程观察净删量，最后ARM64未插桩storage/business各2 capability＋8块×4，交替ABBA/BAAB，共68过程。父是exit-price-r0的cb942 plain-current，新侧保持同一unfused merger；两侧使用同一原fixture binary，全部相关头/源码/对象/库在采样前冻结。统计沿用8块均值后配对中位数、100000 bootstrap、seed20261013、pointwise95%；固定120s、失败停止/reap，不排样、不加样。独立构建/测试/观察/性能顺序执行。

原0.2ms Stroke CPU仅作值得继续的排序参考，存储基础端点与Undo/Redo/Teardown 2%控制分别裁决；若本候选业务及存储均无可靠正收益，则撤回候选，不以减少节点或绿色安全组授予产品性能资格。无正式M6/upstream晋升。该轮验证不重开T02.4或live-copy语义选择。

## T07实际回收工作量判别（净价结束后）

r1四观察过程通过但源闭包复核发现旧collector声明还进入Store/Epoch/Write三个未变化cpp。其类声明也必须与旧源码一致；不能只按有调用的方法来定头依赖闭包。r2用ninja的实际依赖清单定位6个生产TU，全部按16a4源码和先包含的原collector头重建；当前侧保持当前声明。新开同一4观察过程，r1原记录保留但不作最终源码资格。此前未插桩父库本来就是完整16a4冻结库，68过程净价不受此观察重建问题影响。

观察构建r0在parent publication编译失败：未变化的coordinator头按自身目录先包含当前collector头，旧方法声明未生效。r1在父派生cpp最先包含该版本collector头，沿原include guard保持一致；不改产品/计数点，原源码diff、构建命令和错误日志保留。此失败发生在任何观察运行之前。

68过程净价已完整结束、未追加样本；业务Stroke净省0.401ms [0.2405,0.7145]，存储主端点区间跨零。现在只用4个parent/current/current/parent观察过程检查来源，不重测性能资格。两侧派生库在原HistoryCollector相同操作点增加固定原子计数，无逐事件clock/日志或产品状态；记录请求key、实际新work节点、全metadata pass/key、已知H重排、historySlice及版本、root访问、重复/重启、实际移除和worker运行/排程。保留原stage marker，阶段代表计数发生时段，不把后台计数归给发起它的前台责任；stage0也输出。

父由16a4的collector/publication/read原源码及原collector头、当前其余未改源码对象和同一unfused merger重链接；新侧只替换collector加计数对象。先核对16a4→cb942 runtime差集恰为这三个cpp和collector头，无其他产品变更被错误带入父。原业务fixture/依赖/像素/undo/redo/销毁保持，120s超时并reap、失败停止。四过程只观察计数可重复性，不能给统计置信区间，原子计数可能改变后台合并时序；实际工作删量与已冻结未插桩价格并列，不由计数比例反推时间份额。

## T07净价判别（cb942b6eff对16a4，采样前冻结）

本轮是原T08.2的增量验证，不重复授予upstream资格。父16a4采用net-business-r0冻结的plain-current image；新cb942b6eff仅用同一冻结merger对象替换产品merger后重链接，使业务两侧保持相同clear/composite拆分。存储不调用merger，复用同一双库；其余产品对象与最终安全构建绑定。新侧按当前头重编译原存储及业务fixture，父侧用16a4冻结二进制；记录全部命令、输入与实际库，不改产品对象/源码。旧upstream价格仍按冻结身份解释，不将不同时段比值拼接成当前资格。

ARM64，两矩阵各2个capability＋8块×4过程；偶块parent/current/current/parent，奇块current/parent/parent/current，共68过程。存储保持原K1/16×覆写1/16×H0/1共8行、每行4寿命，奇块反转case次序；业务保持8段/4callback/19 projection及原像素、undo/redo/销毁。每过程120s超时，失败立即停止、kill/reap，保留全部失败；两矩阵顺序执行，产品/夹具/协议/共享依赖在前后核验，不与构建/其他采样竞争。

主端点为存储K16/16写/H1完整case前台thread CPU及业务Stroke process CPU；同时报告全8行/互斥阶段、CPU/wall和整进程。每块每侧两过程先均值，8块为独立单位；100000次seed20261013 bootstrap、配对中位数和pointwise95%区间。沿用2%回退界观察原控制；仅下界大于0才确认局部正收益。业务绝对净省0.2ms作为是否足以改变剩余0.723ms主线排序的参考，非正式门；先前8块变异不能保证辨别0.2ms，区间不确定时保留未知，不加样到通过。

事前数量模型是发布/D不变、非最后保护退出不再访问H、后台最后保护普通事件从N补扫转为H重排；前台补足D外必要回收必须付费。当前真实业务触发量未知，因此不预报毫秒点值。此正确性修复不依赖正收益才保留；若性能回退则诊断替代实现，不恢复漏回收。实际增量价与上轮机制计数分开，不将通用融合、旧粗桶或少扫次数当PageStore基础性能证据。

## 原T07事务base释放闭包反测（terminal计时结束后）

最终冻结cb942b6eff6d2afe19f87311e1febf2ccb98c655：六组ARM64/x86_64各5225/0/0，源diff/库/运行依赖及退出身份一致。结构图最后r5、source inventory及原manifest方法名匹配，结构门/6自测通过。生产+22/−16、测试+100；不改owner/census、侵入上限、原收敛起点和删除证明。不重跑公共42点或授其跨版本资格，本包未插桩时间尚未测。

相邻snapshot出口复核：epoch.releaseSnapshot的becameUnretained已精确表示非current根的最后snapshot且无transactionBases；前台releaseSnapshot却无条件scanAll。增加6行前后台×无其他保护/同base事务/第二快照反测，先冻结原实现的多余扫描，再将原前台collector/物理处理条件收窄到该既有事实。captured release已有同一条件，不添加第二终结器或为统一外观增加一次finished-transaction锁查询；两种owner继续调用同一history索引政策。

snapshot反测r0为6/2/0，两个前台受保护行pagesVisited均4对期望3；r4只将原前台扫描和同步物理处理纳入becameUnretained条件。结构检查首两次因旧符号/源码检查点拒绝，更新原manifest中的方法名并刷新source inventory；第一次graph早于manifest更新，随后再次生成graph，全部拒绝日志保留。原intrusion ceilings、owner/census、收敛起点和删除证明不调整。

首版r1的4行及旧相邻责任定向11/0/0后，扩大同一失效事实反测：追加仍有同base事务/retained snapshot两种保护，共12行；4个protected abort行仍多扫1个历史页（5对4），证明“base旧于current”不是失效事件。r2复用epoch.root(base)现有逻辑准入查询，仅最后保护消失才遍历H；commit的base即前current时只需既有D，避免多余查询/全H扫描。该查询在原Store gate下，未添加root计数/持久标志；代价是一条旧base路径的既有epoch查询，不能把删H直接当毫秒收益。重复历史/元数据恢复分支不得保留。旧构建命令误用不存在目标、测试统计getter误写及全部失败日志保留。

反测r0：4 passed/2 failed（含init/cleanup），前台commit及abort均为49152B而期望32768B，后台两行通过。候选r1在原collector把epoch记录和历史回收合为collectAfterEpochChangeLocked；commit先登记D再调用，restore删第二次collect调用，abort共用同一终点。rescanHistory复用原m_work已知历史索引；m_rescanRequested只承担实际登记失败后的缺key补扫，不增加新状态/队列。静态删去根失效直接触发全metadata遍历的赋值，但未测其业务命中和净时间，前台补足必要回收成本须计费。验证原4行、旧memento跨delta释放、并发不同页、预算拒绝/晚释放/close及两架六组；所有输入冻结到测试结束。

源码复核发现collectEpochBookkeepingLocked的rescanHistory只在后台模式设置全metadata重扫，前台只回收epoch记录；commit随后仅显式请求本次D，abort直接返回。先以4行foreground/background×commit/abort验证：旧事务base保活页1，新事务改页1后旧事务仅改页0提交或空abort；结束后不释放snapshot、不发新写，只等已有retirement空闲，要求旧页1物理backing归还。失败前不改collector；该反测属于原T07.2/3，不能拿close最终清零掩盖普通事务出口遗留。若成立，优先复用原history work索引统一已知历史失效，区分真实缺key存储拒绝的全metadata补扫，不新增回收队列或常驻表。产品改动须另行验证，不把计时粗桶转成因果价格。

## owned终态中间处理预算与观察扰动（16a4，business-terminal-r0，采样前冻结）

原T02.4在直接canonical设计前定价：从seal的overlay候选准备开始，到seal返回的整段中间处理（包含adapter准备/交付、原cold/source清理、session终结）按ownsTransaction区分；另观察完整commitOwnedLocked，两者不嵌套。该粗桶包含必须保留的工作，只给候选当前责任预算，不能全额当可删价格。相同当前派生库仅开/关两处scope，移除旧job/cold/operation细分观察；保留相同取消共有融合及原业务fixture，禁止改产品对象或协议。

ARM64，mode0/2各1个能力过程，之后8块，每块4过程，偶块0/2/2/0、奇块2/0/0/2，总34过程。样本单位为块，各mode每块先均值；报告完整Stroke process CPU的on−off配对中位数和100000次seed20261012 bootstrap pointwise95%区间，阶段桶只统计mode2块值。每过程120s超时、kill/reap，像素/8段/4callback/19 projection/undo/redo/销毁、运行库/共享依赖及scope完整性任一失败立即停止，保留全部失败，不追加求精度。构建/分析与采样顺序执行。

事前判据：仅当on−off绝对区间落在±0.2ms内，才把这组粗桶用于0.723ms回退量级的候选筛选；否则明确扰动或精度未闭，不按比例扣时钟。该容差是有限判别精度，不改正式门。直接路径若连所涉及owned粗桶都明显低于0.723ms，只能解释/回收部分回退；无论大小均不能把删除整个粗桶当成合法实现。固定两处source diff、所有链接对象及实验前后身份；不增加新性能优化资格。

## 业务回退的工作量判别 r0（净价两矩阵之后，产品仍16a4ff59eb）

r0生成器在编译前被错误的installPage返回类型锚点拒绝，保留目录与driver；修正为真实KisTileSP后r1构建和4过程通过。r1共同Stroke计数为937 stroke job、19 merge、46 operation、208 cold、59 seal；commit入口父13、当前33，current writable_presence为0。r2仅加commit原输入proof/removal/surface数量、transaction/base/surface身份及实际成功位，重复同一4过程来解释多出的20次提交是否真实发布及内容；不增加净价样本。其余scope不变，CPU不得跨观察深度充当净价格。

原T08.2实测Stroke增加0.723ms后，先用4个观察过程parent/current/current/parent检查是否多产生了job、operation、冷页目标、seal、capture或canonical提交；不扩大未插桩计时样本，不将观察CPU差当净价格。父采用原8198 observed-current冻结库（已取消clear融合）；当前仅在派生库复制同一observer、job/merger入口及对应实际冷准备/内部commit入口，并额外观察真实writable-presence、batch准备、adapter页准备与交付。旧cold已拆到Private::prepareTarget，新commit使用commitOwnedLocked；这是同一逻辑责任的观测映射，旧entry模式flags不跨版本等同。

复用净价的同一业务夹具及各自ABI、相同8段/4 callback/19 projection、像素/undo/redo/析构要求，ARM64、120s超时、失败立即停止且reap。模式2的事件父子thread/stage、exclusive CPU守恒、无溢出及dump无活动尾必须成立；记录全部派生源码/命令/链接对象/库身份。编译与运行顺序执行，产品不修改。两个重复只检验计数可重复性，无概率置信区间。

竞争解释：新增writable显式presence/default保证实际命中；adapter在相同工作上重复准备；operation/版本/发布或调度拆分增长；数量没有增长而相同责任单价/锁域/尾增加。观察先决定哪项有资格进入下一有界定价，不能由一个inclusive桶直接授权优化，也不为取快值删除已证明正确的语义。

## 整包净价有限判别 r0（16a4ff59eb，采样前冻结）

原T08.2领取一次共同存储三方比较，不替代未完成的live-source合同选择或正式M6。当前16a4ff59eb与重构前8198c36ed7、upstream9a24ae0d8c分别记账。父版本使用原`br1_pagestore_equivalent_pipeline_20261010/plain-current`冻结库：唯一派生修改为merger取消clear融合，共同storage夹具不调用该路径；其image及旧foreground夹具哈希与当时身份一致，70项工作区依赖中仅原current image路径已被新构建替换，其他依赖仍匹配。新夹具仅按当前头重编译原同一foreground_fixture.cpp；父/upstream使用各自原ABI夹具，禁止把旧夹具硬连新布局。

输入保持原8行K1/16×覆写1/16×history0/1，每行4次manager寿命；每次非默认完整写后立即read并比较全部像素，H1 commit后undo/redo再purge/销毁。此矩阵无live-copy、getTile仅声明、显式default写或坏流导入，不拿这些新增/不同合同掩盖净价。固定ARM64；无产品插桩、无观察库。三个clock沿同一原边界：thread CPU、process CPU、wall，七阶段与整case分别输出；另用wait/reap后的RUSAGE_CHILDREN量整进程CPU，包含启动/全局析构但不能将尾准确分派到单case。case内四寿命和循环不是独立样本。

先各侧一次capability，共3进程，核对全部32寿命、正确image加载、runtime依赖与无observer输出；任一失败停止。通过后固定8块，每块6进程：从current/parent/upstream的6种排列按块号循环选前三侧，再逆序运行后三侧，使各侧两次位置关于块中心对称；奇偶块反转case顺序。总48计时进程，禁止追加至显著。每进程120s；错误像素/库/依赖变化/超时立即停止，kill后reap并保留记录。产品源码/库/夹具在批次前后核验；构建、分析器及其他基准不得竞争运行。

主端点为K16/16覆写/H1（case7）的write和全case前台thread CPU；同时报告全部8行的process CPU/wall、七阶段、全case以及整进程。统计单位是顺序块，每侧两次先均值，再形成配对差与比值；沿用100000次固定seed bootstrap中位数pointwise95%区间，区分当前较父节省与当前较upstream额外成本。其余各行是竞争解释/控制，不给跨端点联合资格。工程解释以全case前台≥5%为值得维持复杂重构的参考、沿用2%回退边界观察普通控制；这是诊断判别，不变更正式门或把精度不足算通过。

事前只作数量预期：原F/pin及内部投影删除应命中这条管线，但D/B准备、成功交付、scope寿命及真实free可能抵消；无合法单价，**不报总时间点预测**。主要竞争解释为：前台兑现但后台/退出抵消、真实管理工作仍占多数、只改善history而普通operation回退，或执行噪声不足以辨别。不得加和旧局部CPU桶推导整包收益。最终按实际差额更新原T08.2，未覆盖的freehand、live exact-view及完整正式family仍保留，不能用这个矩阵宣称重构全部完成。

净价r0在第一个current capability后按规则停止：8行像素完成，依赖校验误把dyld列出的主可执行文件`storage`也当成必须与旧夹具逐字节相同的共享库。实际依赖名称集相同，除各自独立冻结的image和新编译storage外，全部共享依赖hash一致。r1仅从共享依赖集合排除已单独绑定身份的主程序，保留库/输入/源码/退出核验；r0原代码、构建、日志不改写，不复用其计时。r1重新按同一3+48协议执行，无产品修改。

## 整包业务控制 r0（存储r1结束后、业务采样前冻结）

存储r1已完成；业务控制是原T08.2另一必要端点，不补存储样本。复用原cost_fixture/matched_freehand_baseline/stage_probe的冻结源码及父/upstream二进制；current按当前头重编译同一夹具。三方恢复相同clear→composite拆分：父使用原plain-current，current仅在派生image库替换merger一个对象（merger产品源8198→16a4无差异），upstream原库。编译/链接对象及实际库分别绑定，不改产品源/对象/测试；派生库无产品事件observer。业务仍有原SOURCE_AUDIT披露的页分区、失败接线、参数外提及透明RGB修复差异，因此只作业务控制，不能冒充纯PageStore本体证据。

固定ARM64，8段、4个显式update callback、seed12345，原blank/painted哈希、undo/redo、strategy/image销毁断言，5个阶段CPU/wall及整进程退出。capability每侧1进程后，沿存储相同三方镜像顺序8块/48计时进程；每进程120秒、失败立即停止且reap，禁止补样或延续至通过。主端点Stroke process CPU、5阶段CPU合计与Teardown；wall/Undo/Redo和整进程另报。阶段CPU并非单worker归因，image/strategy销毁不代表进程静态pool已逐项收费。

沿用8块中位数、100000次seed20261011 bootstrap pointwise95%区间，5%值得收益及2%控制回退仅作工程解释，不降低正式门。无新的业务点预测，不能按存储11.7%乘整笔时间。先验证全部身份/输入/输出/退出，再解释当前较父增量及当前相对upstream剩余差额；此控制与存储各自冻结，不以其中一个通过替代另一个或live exact-view修复。

删除闭包最终冻结为16a4ff59eb01e87dc435afb81a305413d32223bb：生产+1/−28，测试不变；六组双架10414/0/0、公共upstream42点相同，当前结构门及6项工具自测通过。删除承诺重新绑定最终代码，两个无caller缓存接口退出、真实两consumer缓存方法收回private；人工清单与派生图独立统计。初次137条结构错误保留，只有manager经逐责任复审调整60/4侵入上限，原收敛起点/删除证明及其他上限不动。被删接口动态命中为0，不领取时间收益；live exact-view两个缺口及整包净价仍开放。[当前证据](README.md#deletion-closure-review)。下列事前约束按其冻结身份保留。

删除闭包与结构门复核事前（父2eb9f4236f）：全仓tracked C++调用核验发现copy refresh删除后，KisTile的installPageStoreReadCache/takeIdleReadCache只剩定义声明；本包删除二者。Backend readCacheForPage仍有selectCurrentReadTile/acquireTile两个真实consumer，保留但回收到private；tileDataForReadPage还有manager默认色/clone读取，不能误删。无新增状态/owner/回调/热路径，预期运行工作不变，不领取性能收益。

同次真实architecture gate失败137条，绝大部分为陈旧源hash/图/位置，另有已删除refresh、anonymous组、iteratorScope、PreparedTransactionState及改名测试的旧要求。不能恢复旧协议迎合门禁；将索引及owner/census更新到当前原scope事务终结、真实lease registry、KisPagePublicationDelta，重新生成编译数据库支持的完整图。manager侵入60个标识/4个include超出旧25/3，须先按92逐责任审查而非静默写baseline；32个出现是已有诊断timer/phase，另外28个为实际adapter/backend/operation能力。准备存储是操作局部，claim/manager gate延长、GC/free费用保留，未增加manager持久状态；当前批准蓝图的具体增量和删除条件在92记录后，才更新该一文件的精确上限，其他上限保持。原convergence-start与旧协议删除证明不刷新。

copy交付最终r4冻结为2eb9f4236ff3cf28550716717ec43c676336cd9d：定向80/0/0、双架六组10414/0/0。公共history42点及live-copy24点分别与upstream一致，后者保持此前原live语义。两架各64行安装探针，48真实窗口alloc0、16空操作无事件；free合计578/577，最多32，不授零free。生产+101/−189、测试+152/−3；三旧符号定义/声明/caller全部退出，原四raw恢复consumer迁完。原8个root反例、r1三失败及r2/r3各16失败完整保留；净时间未测，两个已知live exact-view失败仍未修复。见[最终交付与模型](README.md#copy-prepared-delivery)。以下按各自冻结身份解释。

copy交付r3定向仍64/16/0：一次drain只等待已在队列内的job，不包含history collector已安排的future retry wake，因此仍在归零断言处观察到四claim。r4依据原OwnedCancellationUnderPressure及HistoryCollector的明确合同，改为5s内观察生产自动retry使claim/owned transaction归零（history只保留原一事务），不显式abort、不主动processRequests、不用新操作代偿取消。先前r2/r3的立即/drain归零假设均未成立，原日志保留。

copy交付r2定向64/16/0：旧三项改用真实读后全部通过；新增16项均已通过拒绝后wrapper/extent/像素检查，但在解除MetadataArena压力、尚未原reclamation drain时观察到四个待取消claim，不能宣称同步取消完成。r3按原受压取消合同先执行既有drain，再验证claim归零和重试；保留r2原值及完整日志。成功交付时准备物在原claim释放前销毁；失败从未安装的候选只作局部析构，实际物理取消仍由原scope/orphan政策完成，不为此次copy另建owner或清理队列。

copy交付r1定向61/3/0：新增八个真实root拒绝全部通过，原CompatibilityCopyFailure的三个ordinary部分页用例在未加锁直接检查cached TileData时读到97而非49。KisTile契约要求成功lockForRead后才能读取data；取消失效选择并保留原wrapper/活跃pointer，下一次真实读重新选定已接受版本。r2将这三项改为验证原wrapper身份及加读锁后的原像素，不减弱真实Mapping/Allocation/Decompression拒绝与全区readBytes检查；同时新增四BPP×ordinary/rough×standalone/history的混合边缘页、warm/cold/default删除、实际overlay存储拒绝、已有history段保留、重试及undo/redo。原失败逐项保留，不将未加锁缓存检查作为公共像素语义。

copy交付收敛事前（父e1a26e14d9，原T06.3）：先用真实legacy source避开待选择的live-source语义，目标覆盖warm替换、cold新增和default删除。在CommitEpochPrepare处耗尽真实MetadataArena，验证canonical拒绝时原wrapper/范围不提前改变、失败后不用重新分配恢复，再解除压力重试。当前两模板在root前删/添wrapper，失败时refreshPageStoreIndex重新capture并扫描矩形，可能在同一预算拒绝下无法恢复；先保存反例。

目标复用原batch/scope的D及claim：seal的原overlay候选供接受前PreparedTileUpdates准备，root（或借用history的overlay）接受后由原保留write set借出只读变化用于安装；准备物在manager gate外、原claim释放前销毁。不复制D、目录或原overlay候选，不新增持久状态/队列/owner。原AdapterChanges只读借用表达可覆盖这两个真实消费者；正常raw working取消仍由原completeAdapters/B处理。copy在最终finish期间持一次manager gate，原像素循环和源pin在门外；取消与prepared installer不得保存栈回调。两模板合并为一个ordinary/rough编译期循环，同批删除两处提前wrapper替换、整区恢复及refreshPageStoreIndex/refreshPageStorePage定义声明。公共legacy目标原行为保持。live alias的取值与future-write行为此次不暗改，精确view反例仍须单独解决；净时间与新增必要prepare/借用视图费用未知。

import owned最终r2冻结为e1a26e14d91f26db4e4f03b470842105fda00165：双架六组10366/0/0，新/父共同API42点保持、成功输入upstream24点同义，旧坏尾/空流10点差异保留。retained token四轮2/4/6/8→0/0/0/0；N17/257×四BPP逐页真实换出后像素正确、单顺序session最大pin1。原guard归还已释放驻留，不为文件batch增加checkpoint/恢复器；D/B元数据峰值及净时间仍未知。生产+31/−29，测试+216/−16，无新持久owner/队列。删除仅覆盖导入私有history及接续，真实public undo/abort和legacy history保留。r0/r1定向43/51通过、全部原始尝试保留，见[导入交付](README.md#import-owned-lifecycle)。下列事前约束与旧反例按各自冻结身份解释。

import owned实施前（父667c8d6516，原T04.12）：实际read/readFrame上层只消费bool和设备内容，KRA失败disconnect、剪贴板读入失败丢弃，另有尺寸探测忽略bool后读范围；无caller获得局部nothing。保留当前坏尾全撤销/空流拒绝的可见行为，不采用upstream不同的失败内容。目标复用原Managed write batch一次拥有整次解码，原D/B负责working交付和撤销，原scope/orphan负责物理取消及最终事务退出；删导入getMemento、默认backing保活、before/after输出、脏区计算和专用abort全表准备，不新增import owner/队列/结果状态。原beginMutationBatch增加requireIdle准入参数，在原transaction/mutex保护下沿writableTransaction核对零活动事务，保持旧read不能借现有history或外部事务的要求；普通batch默认保持原政策。空有效文件也执行准入，不借早退改变busy行为。

原failure4通过QIODevice回调插入独立native OperationDelivery来阻止全局history取消；拥有整次解码后，该嵌套native入口在原batch注册表处拒绝，私有current history及“之后tryCommit它”的实现接续随之删除。该入口未向caller返回memento，真实读取caller不依赖此状态；保持read false和已清空结果，测试改验拒绝及原batch取消，并补真实raw guard跨read返回、最后unlock归还的接续。不得只删除失败断言：验证像素/索引、活动事务/retention及最终归还，保留旧反例。预测每次成功导入减少两份持久root token、一个memento结果及外层索引记录；每文件scope取代每tile私有批次，D/B和整文件并存payload的峰值必须记录，未测净时间、不授M6性能。

import判别冻结点（尚未修复时）：import-history-repro-r0-arm64四BPP各四次真实read/clear/drain后retainedSnapshots为2/4/6/8（基线0），2通过/4失败；产品工作树只有反测测试修改。共同API r0因protected入口未编译，r1当前日志缓冲交错未解析，r2行缓冲后各42点正常退出、32相同/10不同；坏尾流的部分内容保留及空流返回值不同。不得将此作为全场景同义或时间资格。先审核真实失败caller，再将成功及取消拒绝后接续纳入原T04.12的统一结果保活政策；不先补局部purge或新增导入恢复器。[完整反例](README.md#import-history-retention-counterexample)。

import私有history判别（父667c8d6516，原T04.12）：成功read的局部nothing未返回给任何undo consumer；commitHistory却建立before/after retention并将capability保存在两个memento索引中，局部KisMemento析构只释放默认色。先用真实压缩流做四次read→clear→drain，记录每次retainedSnapshots并断言最终回到起始值，验证是否有无人消费的持续保活。此时不预授匿名替代或只补purge：取消拒绝后原current仍可tryCommit，必须纳入完整政策；还需独立upstream核对失败输出，不能冻结当前私有history的实现边界为必要语义。该判别不测时间、不改变产品管线。

clone最终r6已冻结为667c8d65162017f872352b19a8c4a8e3e5815521：双架六组10302/0/0，最终公共upstream42点逐项相同；父/最终diff与实际加载库审计通过，所有前述失败和中间记录保留。生产+119/−107、测试+178/−1；同一capture/manifest贯穿三consumer，下游有序初始化不复制排序。仅关闭本clone投影及一致性责任，不结算全包净价或live-copy冲突，见[当前交付](README.md#clone-fixed-view-delivery)。

clone下游r6收敛：r4定向167/0/0，r5仅将只读manifest迭代显式设为const、完成构建。进一步沿实际consumer发现prepareInitialization无条件复制N条到EpochArray并排序；clone输出已按树序排列，该分支无必要。r6在原初始化责任内检查有序输入并直接建owned节点，仅真实无序外部输入继续复制/排序；无新API/状态/信任位。删一份N-entry临时目录和有序输入排序，新增有序性线性检查，必要root节点及公共验证保留。原sparse-batch独立std::map oracle的pattern1改为逆序初始输入，其余pattern继续有序；先核对初始manifest再执行原96轮delta。此处是PageStore初始化的共同实现清理，不单独冒称clone业务时间收益。最终r6重跑相同六组双架和公共42点，旧r3/r4资格不转授。

clone r3完整反测：定向103/0/0、公共upstream42点相同；完整ARM六组5147/4/0，四个失败均为testTileCloneRejectedWrite的manager clone、payload压力、无batch组合。旧hash复制经KisTile copy→tileData触发unexposed intent物化，额外申请payload才拒绝；新clone读sealed版本不需该申请。r4仅修正这四条旧测试：要求clone成功、source activeCpuWritePages为0且像素正确，再用真实tryWriteData申请证明同一预算仍拒绝；foreign transaction和active anonymous batch的原准入拒绝保持。直接Tile copy三入口仍消费源working data，未删除其真实拒绝。r3首次定向命令两个selector拼写错误（0/2），原样保留；r3b使用原实际名字并通过，未改样本数据。

clone r2反测修订：103项中71通过、32失败。20个带D的归并输出为空，原因是局部回调名emit被Qt宏展开，不是合法空输出，r3改名；4个cold pending行证明manager仍复制源working hash，多带入未sealed页。目标将初始化已消费的原manifest移动交给manager，直接建懒wrapper，删除canonical分支的源hash/cache复制，不再导出第二份N-key。独立backend两处真实consumer不建adapter，保留可选输出。另4个history-base夹具的clone核心已修复，但tryAbort按既有base-changed合同本来应拒绝，改为断言该拒绝并用backend原无memento退出完成测试清理；不改产品abort政策。4个存储注入未触发来自timer构造不通知observer，改在真实ManifestExport的next边界注入，不把未注入算资源证据。全部首稿和失败保留。

clone固定视图实施前约束（父a24062b966，原T06.2）：configureClone先导出current root、导出history prepared-set并逐项find/erase，再另capture transaction-base+overlay读取像素。实际consumer是新Store的完整初始化manifest及随后逐页采用的同一版本，不需要两个取样点或第二份delta。目标只capture一次，从原retained root和已冻结/排序的capture delta直接归并输出；保留原source transaction准入/manager排序、真实capture保护、每页descriptor/replica采用及失败构造RAII。删除clone的preparedPages consumer、逐项查找/删除和重复取样；derived extent已由原publication/epoch政策维护，验证后删除updateSnapshotDerivedExtent及额外N扫描。新manifest继续是必要输出，不能称零投影或零copy。

clone归并的内存选择：不预留N+D的大上界，也不新建N-key/排序目录。D非空时对同一不可变root及有序delta做计数和写出两次线性归并，按实际结果页数准备一个最终manifest；D空沿原一次manifest导出。这是2N树访问与受控峰值的明确权衡，不把两次判定说成一次；capture既有D排序/保护、输出验证、新Store建树和逐页采用均收费。旧逐项搜索/erase为O(ND+D²)，乱序追加还触发公共数组去重validator的平方回退；目标归并O(N+D)、有序validator线性，未测时间净价。先反测history base与current已分离时clone是否与原backend读视图一致；该夹具通过独立Store producer推进current，是跨层防御性证据，不冒称普通manager已命中。再覆盖N0/1/17/257与增删改/default/persistent/private pending、旧读及source退出、真实存储拒绝与重试。安装scope及copy live-source待选语义不在本包暗改。

history最终候选r5：已核对overlayKeyLess正是surface/row/column顺序，过滤同surface及缺wrapper后仍有序，故同时删除本入口的sortPrepared；其他无序输入入口继续排序。候选M的预备存储与逐页查找仍有实际consumer，不说整次操作零分配。新反测加入声明但未触碰页，确认不产生wrapper/安装/dirty extent。allocator探针将warm页全部读入旧cut缓存，再观察真实install；cold producer保持缺wrapper，不为读测试提前补齐它。探针将捕获数、真实安装开始/结束、像素及undo/redo一起校验，free只报告、不要求零。r4仅构建、没有单独运行资格；中间r3双架10198/0/0不转授最终r5，后者重新跑相同六组及独立公共/allocator探针。

history二次理想路径复审（r3之后、r4之前）：r3从原mutation写集借用变化避免了复制，但每次prepare/install仍扫S个声明项再过滤D个实际变化，S可以大于D；不得把该扫描写成2D。原KisPreparedOverlayUpdate已有唯一、排序、接受前后稳定的changes，直到finishUnlocked才销毁，正好覆盖两个同步consumer。下一版AdapterChanges仅借这个已有候选，删除两次原写集过滤和对coldPages有效性的依赖，不新建D数组/owner/状态；安装仍必须早于finishUnlocked，原claim贯穿。理想删量从累计history H_i的导出/解析/刷新收敛为各段2D_i借用访问及D_i实际安装；整次commit仍为脏区访问最终H项，候选M的必要准备/排序和实际缓存释放收费。r3通过只冻结r3身份，不转授r4；补未触碰声明页反测后重新验证最终源码。

history交付时序反测修订：r2构建成功，但定向75项得到27 passed / 48 failed；16个新交付行、8个拒绝后读行和24个原history行暴露真实漏安装。借用遍历用原coldPages区分实际变化与仅声明intent，首稿却在swap/释放coldPages之后调用安装，阶段计数仍报D而实际遍历已空。r3把安装前移到overlay接受后、原页状态及初始化source释放前，仍在Store主锁外；原段和claim保留到真正交付，不复制D、不新增标记，也不放宽像素断言。r3定向75/0/0。此反例说明阶段workItems仅为输入量，不能代替实际wrapper/像素结果验收；保留全部失败与源码diff。r1编译拒绝来自测试memento的const声明和漏迁移的旧bool refresh夹具；该夹具实际已有wrapper，改为直接失效原cache，没有为测试保留已无生产consumer的晚创建路径。

history实际consumer复核修订：manager checkpoint只消费成功/失败；后续读者各自选择新cut，没有任何调用方消费backend此前返回的captured view。因此内部checkpoint直接seal并交付，不创建/立即销毁无用读快照，删除这条内部capture拒绝责任；原公开mutation.checkpointForRead仍返回完整exact view并保留其真实capture失败/重试合同。第一稿围绕内部capture失败增加回调之后的恢复验证，是固定了多余工作边界，已撤去对应诊断阶段/内部分支，并保留初稿diff。新增反测在实际metadata预算耗尽时证明空内部checkpoint成功、capture计数不增，而真正capture仍拒绝。r0构建失败的直接原因是SurfaceId没有operator!=，未形成有效测试资格。新借用视图只在seal期间引用原写集；claim覆盖安装，checkpoint按原边界结束claim，候选在manager锁外释放；不会为了候选无语义的析构再建一个checkpoint ack/保活状态。

history段交付事前约束（父c1f4efcf07）：原T04.10/T06.2内收敛commit/checkpoint，不把已安装working wrapper误当已按新sealed版本失效。原mutation在Sealing及quiescence保护下借出只读AdapterChanges（只含原write set引用，不复制D、不拥有状态），接受前准备实际段D的缺wrapper/删除能力，overlay接受后、清掉D/claim前交付；Store gate外回调，caller既有manager gate保持，不重取。checkpoint的capture失败发生在overlay和交付之后，重试只capture新cut，不重放旧D；root失败则保留已sealed的history，不能恢复成更老像素。history累计delta仅用于undo/redo脏区，由原publication owner直接求实际proof/removal边界，去掉prepared-set三数组导出、D-key输出和再次版本解析。删除historyChangedPages、refreshPageStorePages及无consumer的bool-presence refreshPageStorePage；copy专用exact-view refresh仍保留。新增借用视图/两个同步回调只服务原段准备/安装，不增加持久owner、队列或缓存；cold能力、两次段D访问及回调单价未知。验证旧warm读、真实缺wrapper producer、连续checkpoint、空重试、metadata/refusal/read-capture/root失败、原Closing/foreign guard、脏区/undo/redo及完整双架。全过程保持已接受事实，最终净价随完整管线测量。

purge allocator反例修订：r1及带free栈的r2在首个D1安装得到alloc0/free1，原“零free”假设被推翻，失败不覆盖。实际栈为notifyDetachedFromDataManager→闲置Tiles3TileReadCache析构，不是QSBR旧tile最终释放，也不是prepare Absent去保活造成的晚分配。purge比较建立cache，前一clear探针没有此状态，旧clear的128个零free结论只覆盖其冻结夹具。缓存失去消费者后应释放；它不构成可拒绝的安装工作，不能仅为零free指标新增D份缓存保活/延迟队列。r3仍要求零晚分配与正确结果，另报全部free数量，不再授予零free资格。该局部释放及其锁上下文计入余项净成本，不能算删除或完整管线性能通过；早先候选/旧map引用锁外释放的结论不外推为整个安装无物理free。

purge交付复审补充：首版ARM六组5071/0/0后检查实际prepared token发现，无锁hash的Absent仍查询/保活旧tile，但删除仅用原key及QSBR动作；map引用在原retire中移交，RawPointerAccess析构仅减计数、不运行collector。因此本包同批删除此无consumer查询/强引用，覆盖clear/restore/trim/purge的纯Absent准备；Present/MayRemove不变。链式hash的unlink可能同步释放旧tile，候选引用仍保留以实现锁外最终释放。该区别来自真实释放消费者，不为了形式统一合并两种所有权。最后候选须重新构建并双架验证，不继承首版资格；每个无锁Absent静态省1次tile lookup/一次候选强引用保活，key/GC和原caller迭代器瞬时引用仍在，未测净时间。

任务为执行[原蓝图](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#soundness-and-deletion-review)直到完成。唯一状态仍在原T01–T08的33子项矩阵，本目录只保存实施证据，不缩小到一个快路或单次试验。

purge交付包事前约束（父e9d2048b4c）：实际clearSelection在迭代器析构后调用purge，设备清理任务按设备去重以避免并发写；保持此既有外部排序合同，不扩大为并发purge/default修改保证。内容比较与删除之间没有其他writer是前提，不能只靠删除时的新claim宣称观察版本已受保护。保留原H索引遍历、相交K页的默认backing pin/整页比较及D个实际默认页删除；不把逐页比较移入新大锁，不为K个非默认候选建立claim。以一份D-key选择取代D个TileSP列表再复制keys，原removePages/batch只为D>0工作；在原PreparedTileUpdates准备D个map-key/GC token后统一接受和安装，原claim至候选释放。PageStore删除接受后deleteTile分支，legacy仍按原hash删除。无新增owner/队列/恢复域。原D选择和预备安装token服务不同消费者；token容量、key准备和claim延长收费，未预报净毫秒。验证部分相交、页尾非默认、范围外默认页、D0/1/17、四BPP、history/保留读/默认色变化、真实metadata拒绝与同范围重试；双架安全、同一公开purge探针对照upstream及实际allocator安装窗口。只有这些边界通过才结算原T04.10的purge子责任，copy/history/完整性能不缩减。

当前owned终结包11adac3e3a：双架六组各5011/0/0、upstream42点一致，原scope/orphan承接实际物理cancel拒绝后的owned退出；普通finished facade不保活，真实lease保持原槽至最后归还。初次8个失败及所有中间批次保留；详细阶段限定及删除见原蓝图§17.6。完整raw/history/性能范围不缩减。

前置local adapter包e6fc6d687c：六组双架各4993/0/0、独立upstream42点一致，关闭父67ae的28个取消失败；父包及本包初次失败原样保留，不进行本包时间追采或M6晋升。原D/claim贯穿结果交付，B只保留实际冷插入的原PreparedTile逆向能力；成功匹配cache保持ready，finish释放准入不等待facade析构。完整余项统一约束在原[蓝图§17.6](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#owned-publication-migration)，不另建状态矩阵。旧各批协议及其失败保持冻结，不因本次选择修改原样本或将通过总数外推。

owned终结压力判别（父e6fc6d687c）：BPP1/4/8/16分别覆盖iterator放弃和raw最后归还，先在真实生产provider完成私有写，再填满共享进程MetadataArena，并保持压力跨越终结。释放压力后只观察原后台进度，不显式abort/processRequests或启动新工作来帮旧责任收尾；页claim和activeTransactions都归零后才验证同线程同页重新准入及旧像素。若真实拒绝留下事务/弱槽，沿原session→owned transaction完整终点复用已有orphan链，比较前置准备与原责任迁移，不新增backend永久队列。直接setDefaultPixel等无session caller也必须列入责任闭包；未经判别不增加恢复状态。原测试的压力在finish前释放，或在原生session取消后显式abort，均不能替代本边界。

local adapter实施前选择（父67ae4a8caa）：原batch只对实际working Tile consumer开启交付；成功seal保留原D/claim至root结果，失败时先冻结无guard的原段、锁外失效D并用原PreparedTile能力撤销实际冷插入B，然后物理cancel。原scope/orphan不持manager回调；取消拒绝后已经完成的adapter交付不重放。两hash把原consumed位改为Prepared/Inserted/Consumed，原map key复用，B在第一次暴露前补齐GC能力；warm不建记录。将原getTile冷准备直接交给已有backend/batch，删除其两回调和单页PreparedTileUpdates编排，不新建第二D或恢复队列。B能力存储、一个composition指针、一次实际consumer标志、D失效和延长claim均计费；独立native无working consumer不执行这段交付。原四raw恢复暂留，尤其full-tile legacy copy仍会提前replace/remove，不能把新冷插入恢复能力误称覆盖了暖页语义删除。先验证32个取消行及实际最后guard锁窗，再沿原四caller完整迁移；abort真实拒绝的事务尾仍属同一目标。

读入失败包事前边界（父 faffef592c）：T04.12 复用 manager 原 tryAbort 的准备→取消→安装政策。read 的私有 history 仍由原 backend/currentMemento 持有；统一 memento 开始时保留默认 backing。原 tryAbort 的两个局部候选只合并为同作用域的存储，声明在 manager gate 前，拒绝候选和替换旧表仍在锁外释放。不改变 clear 后恢复点，不将取消拒绝伪装成索引已恢复。删除 read 三处重复提前取消及取消结果未检查便 rebuild 的尾路。最坏仍按恢复基线 N 页准备全表，不能宣称纯 D、零分配或性能提升；私有导入 history 是否可由匿名 batch 取代尚缺默认页裁剪及失败语义等价证明，不在此包暗改。验证实际压缩流成功/中途失败、header/null、默认 backing、取消拒绝与释放；trim 仍是 rebuild 的最后 consumer，迁移后才删 helper。提交后的 prune 交付仍归原 T04.10 未闭项。

读入包复审修订：空流、空头、坏头尚无像素写入，先解析再创建 history，直接消除这些拒绝的历史/取消责任，不仅抽取原恢复分支。首轮 import-targeted-r0 的四个拒绝断言失败：持有 legacy raw tile writer 并不能证明取消应被拒绝，原协议可取消并脱离该缓存。因此改用实际 backend OperationDelivery 保留的原范围准入触发 activeCpuWritePages 拒绝；不为迎合测试扩大原取消拒绝条件。首轮失败和后续全部批次均保留。

trim 包事前边界（父 ee8a165fc7）：T04.10 最后一个 rebuild caller 迁到原 PreparedTileUpdates。原 allocatedPages 的有序 N-key 输出用于接受前目标集合检查；原 TrimPage 的 D 项同步借给交付，不再枚举 current 或重建未变 wrapper。原 batch/OperationDelivery 维持接受至候选锁外释放的寿命，不新增第二 delta/持久索引。保留完整候选发现、全局 activeCpuWritePages 屏障及 partial-page 原像素语义。删除 trim 重复的线程 batch 检查（beginMutationBatch 已在 join 前拒绝）、有序过滤后重复 sort、以及 rebuildPageStoreIndex 全部定义/声明/调用。

restore/trim 共同准备改为先穷举唯一目标集合并准备缺项 M，再验证 H = N−M；这已证明无多项时省去反向 H 查找。只有数量比较不构成证明；原数量相等但集合不同反例必须继续通过。发现多项才遍历原 hash 查目标集合，准备原 Absent key/GC；普通匹配集合为 N 次必要查找，不复制 N-key 新表；最坏仍 H log N + N + S log S，restore 树访问以上界整root计价，新增整数计数不作净时间收益。只失效原变化 D，补实际缺项；失败准备不安装/不开始像素。测试保持旧视图/默认/非相邻恢复、稀疏intent/独立backend缺项、trim partial/remove/no-op、准入拒绝及坐标拒绝，最终双架同源；全部净价留到全包测试。

history 包语义判别（父 e03742b0ef）：不得先假定 prune 是必要责任，再为其新增交付框架。同一公共 API 源码分别编译链接当前与冻结 upstream，`history-full-public-semantics-r0/r1` 验证两边真实加载库。当前对空页 writeBytes(default) 在写入即丢 extent；已存在页覆盖为 default 后 commit 保留 extent、redo 却为空；随后 setDefaultPixel(0x29)，三类写入都错误变为0x29，而 upstream 保持显式写入的0x13。显式 clear(default) 则两边都应移除，随后跟随新默认色。故像素相等不是“显式页存在”相等，自动 commit prune 及 absent-page packed no-op 都不合法。已有公开 purge(area) 才承载显式裁剪语义，不能用自动 prune 代替。

下一实施删除 pruneDefaultPreparedPages 的定义/声明/调用及其扫描/导出/capture/读取责任；packed 的 no-op 必须同时证明页已存在，空页默认写通过原普通写管线建立显式页。不新增 alias API 或第二逻辑存在账本。确定每次进入旧prune的history commit删除一份prepared-set导出；proof非空时另删一次overlay capture、本surface的D个proof对应descriptor/读取及实际默认比较字节。非默认页可能首像素就退出，不能按整页字节领取。此前被错误跳过的显式默认写会增加必要的页/metadata成本，须单列，不以性能名义维持错误语义。BPP×partial/full×existing×native/persistent及默认色/undo/redo验证后重跑同源双架；checkpoint/commit原adapter晚分配仍归T04.10后续，显式purge及clearAll的完整交付需在原项审计，不能由删除自动prune推定已完成。

history 反测接续：history-targeted-r0 的16条失败发现本分支关闭 PageStore 的 fallback 也继承了错误空页 no-op，故它不能充当 upstream oracle。同步以原 read selection 返回的 presence 收窄 fallback，保留已有页同字节 no-op，不加第二 lookup；这部分是通用语义修复，不算 PageStore 性能证据。随后 history-full-r1 的40条失败均来自旧测试把默认 packed 写当无工作/无存在（presence12、changed24、delivery4）；按独立 upstream 结果修正期望，并保留 native cursor 只声明不访问目标仍为空的区别。原始失败不移除。公共 r2 已证实四类真实写入/clear 与 upstream 一致，但追加的 getTile(writable) 无像素借用仍在redo及改默认色后不同；这是原 T01/T04 的未关闭语义缺口，不能宣布全入口同义或整个管线完成。

writable intent包事前边界（父1249396fa8）：公共getTile(writable)冷缺页即建立显式内容，不能等到commit扫描wrapper补偿，因为独立get→setDefault/clone也观察此事实。复用原batch/session的legacy key admission，准入后从原entry/transaction判断是否已有显式结果；只有真正缺页才alias原manager默认backing。已有同线程batch借用其原session，不新增client/owner、不提前seal、不复活failed/零client；独立入口走原batch及finishOperationBatch，OperationDelivery保留原准入直到局部候选释放。cold wrapper/key/extent在alias或publish前准备；已有warm wrapper保持原选择路径。删除“公开writable miss只是intent”的分支与假设，native prepareWrites未访问声明仍不建页。无新存在账本、可写guard或全表补偿；必要新增是冷缺页的显式metadata/alias与独立入口提交，不能算性能收益。最坏prepare/拒绝不得留下孤立wrapper或把已有批次内容改回default；cancel/clear/已有源别名/真实partial写及同语义upstream要反测。restore/trim集合扫描及legacy回滚在源头修复后另审，不先删防御闭包。

intent反测：targeted-r0的32条trim失败来自旧夹具仍用公开getTile制造adapter-only额外页；改成明确friend故障注入，不把旧缺陷写成长期合同。公共r0的25观察点全部与upstream一致。full-r1的15条失败中，8条新计数错误把CPU `generationsReserved`误当含alias的总generation计数（该计数源码仅CPU prepareTarget递增）；改为验证实际非default version、CPU/pin各自分母。另7条旧断言仍要求公开writable页无metadata/跟随新default或漏计其独立提交，按独立语义证据修正。build-r2因新测试基准变量插入了相邻同文本位置而失败；随后targeted-r2误调用旧测试可执行，缺新selector退出1，明确不具备该源码构建资格，不能计为验证。修正上下文后必须成功重建才跑新批次；全部失败留档。

intent-full-r4 ARM六组通过，x86 manager一条失败观察到alias采用后旧virtual-default版本仍排队回收（pageVersions为2，预期稳定1）；测量点从函数返回移至既有kisDrainPageStoreReclamation完成后，不能把未free对象算成已释放。其余语义未改，r5定向x86通过，最终双架重验。公共r1扩为七类42观察点（另含无history、commit前改default及clone），全部与冻结upstream一致。该证据覆盖这些明确入口；未完成的batch取消/旧raw恢复、commit/checkpoint交付及全包净价仍归原矩阵，不借此声明整条管线最优。

起点：产品`8198c36ed722030edae715b7423554036bf1bcf7`，产品tracked tree干净；设计`f1a2ece9d`。原20fd候选不合入，M7/条件直接canonical不暗中启用。当前宿主为同Qt/工具链的x86_64+arm64合并构建，既有_build-br0-cpu及父image身份单独冻结。

先按完整责任实施冷准备/真实借用/私有完成/alias/取消闭包，再共同发布、adapter下游与内部提交表示；退出和反例随各包完成，不留给最后补。每包可以聚焦提交，但不代替33项最终审计；没有实际consumer的旧入口、状态和失败恢复必须同包删除。有独立语义的保留项逐一说明，不能只标“兼容”。

事前机制预测：preflight公共guard和伪Exposed消失，必要的驻留验证pin可保留；真实mutable借用语义不变。合法完整final Fresh少一个无人使用的guard和一轮mutable metadata完成；guard删量上界P+F，不能视为同样的物理pin删量。现有普通overwrite仍可重借，handoff/fallback保持。metadata完成与alias接纳分别记录，重试不漏做也不重放。其他项按蓝图的实际J、D和N前提结算，不把未知单价填零。

结构与正确性先行：使用实际CpuMutation/manager/physical/read/history/epoch入口，增加能推翻新假设的反例。双架构执行受影响测试；失败、修复和重跑全部保留。迁移后反查原符号/consumer及净生产diff，检查锁外释放、原活动与最终债务。静态检查不代替行为测试。

性能与计数分开：各责任使用有限机制观察确认删量；最终完整候选采用既有公共存储同语义fixture和业务probe，冻结源码/运行库后才测。父/新和新/upstream分别8个ABBA顺序块，业务控制4块；端点及pointwise区间沿原分析器，不将其冒充正式M6 family。纳入全部失败和完整case/drain，构建与性能过程不得重叠。对未定价的新增责任只报告实测净值及原先未知，不补造精确预测；原final参考1.186/1.360ms不是可叠加新预算。不追样到通过；若控制回退，按实际证据修复本责任并另冻新版本，而非退回不完整的替代目标。

同语义资格修订：冻结父8198包含此次发现的显式默认页/自动prune/writable intent缺口。最终父/新比较不能只核对像素checksum；必须验证被测用例的presence、extent、历史和默认色观察亦等价。若某fixture实际触发上述差异，该原父只作为缺陷版本诊断，不能授等价增量收益；需要另冻结仅修复语义的父对照，或明确限定到经证明不受影响的用例，不隐藏必要工作增量。新/upstream仍为PageStore基础性能主证据，通用fallback修复不归PageStore收益。

显式页事实是语义必要项；当前以alias及独立入口提交实现它，是可构造方案的费用，不是“每次getTile必须发布一次root”的严格算法下界。已有iterator/batch已合并到原segment；进一步跨无scope入口合并仍需证明所有read/default/clone/取消/预算边界，不能凭本包测试宣布该上层拆分已最优。反之也不能因原错误实现省掉显式页就把其较低时间当正确基线。

clear残留接线清理（父73a9fde6b3）：manager::clear(rect)的operational PageStore分支必定在native fill后返回；后面的legacy fallback中，ScopedPageStoreWriteBatch构造也只接受operational backend，因此该实例必为空。删除这一个无效batch实例、replace拒绝清理分支、finish及legacy tile上的无效PageStore bridge/read-ready接线；原fallback像素/默认backing缓存/历史行为保留。其他copy/packed/planar的Scoped consumer仍真实可达，不删helper或共用replace接口。构造失败仍可回落legacy，故不把整个fallback或其缓存误删；修正缓存注释不再声称它省PageStore generation。该包只作控制流去冗余，不给PageStore基础性能领取收益，按受影响manager双架及原独立同义探针验证。

clear删除闭包复核：空batch的析构仍承担了早退/异常时报告job失败的真实通用职责，不能连带丢掉。用原函数局部qScopeGuard直接保留这一个职责，成功后dismiss；不保留backend指针、batch、QString错误槽、finish/replacement政策。新增真实default backing预算耗尽的fallback clear拒绝及释放后重试测试，而非仅断言死分支不被调用。

完成要求：原矩阵逐项有实际迁移/删除或经证明的保留依据；全部明确合同与真实拒绝接续已验；普通热路径无未定价新层；最终结果/旧视图/取消/资源与业务控制合格；报告父/新及upstream差额、预测偏差、生产/测试/派生物增删和仍未通过的正式门。M6资格独立裁决，不因完成重构自动标通过。

取消闭包判别（父75dc8fca5f）：先用公开manager的iterator scope/getTile/raw写入口，覆盖缺页/已有页、只取得/实际写入及BPP1/4/8/16，放弃原scope触发既有private cancel；核验canonical、adapter extent/数据、后续writable取得及默认色变化。原batch析构取消是当前合同，scope销毁本身不等于兼容索引已经恢复。此阶段先保存失败，不预设需要第二回滚表、逐warm查询或所有恢复路径N扫描。若不一致实际发生，继续沿原session的实际entry和原batch最后持有者收敛取消交付；确认拒绝前后及最后raw guard释放顺序，再决定最小改法。数量与净时间未定价，不凭本判别领取性能收益。

该判别r0缺页8项失败；r1加入真实cache准备预算拒绝后缺页12项失败；r2再覆盖CommitEpochPrepare处实际预算拒绝，双架各缺页16失败/已有页16通过。所有业务观察均在失败终点、后续新writable取得及default变化处取值；QTest总数额外含init/cleanup。只扩失败边界，不追采时间。生产75dc不变、反测代码仍待修复包处理，不能把repro当通过资格。蓝图修订到原session→transaction整个责任交接；同时比较消除不必要匿名共享的可能性，不因找到故障就默认新增回滚账本。

最后lease接续先行判别：保留原batch shared control block，只将可能触发其析构终结的最后引用交给Tile unlock局部变量，待原swap barrier释放后销毁；真实guard归还、cache移交仍在原锁域。通过原lease finish可选输出传递已有引用，不增加新owner/队列/持久阶段或额外分配；直接调用finish仍同步。原lease的两种实现与Tile读/写最后unlock同批迁移。真实反例使用已接受的兄弟operation，使放弃batch后的最后lease取消仍到达实际root准备；在原诊断边界由另一线程执行真实Tile invalidation，限时观察是否被当前swap barrier阻挡。覆盖writer/read最后释放及foreign unlock。此项只关闭最后batch引用释放锁域，不声称unscoped lease的同步root完成或整个adapter取消已关闭；余下调用闭包仍属同一包。

该首改实际4条锁窗反例由失败转通过，相关4函数19项通过。targeted-unlock-r0只因命令误用冒号而未选中正确data，不算产品验证；r1用runner规定的逗号选择。扩大同一反例后unscoped raw的4条仍失败，必须迁移其独立终结分支。同时新增当前writable返回Tile的真实lock/read观察：已有页在取消后也会借出0x71的旧私有缓存，原r2只读manager canonical所称“已有页通过”不覆盖这条合同。新批次32个取消业务组合变为28失败/4无写已有页通过；加4条unscoped锁窗失败和4条scoped通过及init/cleanup，总计10/32/0。原失败不覆盖或改写。

下一改动复用原WriteBatch::Private作为unscoped raw的终结记录，删除lease自持transaction/ownedMutation/dirty及独立seal/cancel/commit序列；其实际unused/exposed事实放回原control block的入口模式，与managed/iterator共用finish。保留原live anonymous lease链用于clear barrier，不把unscoped raw注册成iterator、不改变借用选择；两链不共用同一节点。直接finish保持同步返回，Tile路径将原control block交到锁外终结并报告真实失败。相比把整个lease移出锁再重装cache，这一表达保留原pin/cache移交顺序；相比新增延后队列，不增加第二执行者。新增unscoped control-block一次分配及sizeof增量要收费，不能称零成本；此责任统一不是性能收益资格，完整adapter取消仍待关闭。

raw统一后，targeted-raw-r1 ARM 53/0/0；full-raw-r1双架各1531/28/0，28失败全部是取消后的adapter缺口。下一次有界竞争原型只将无history事务从隐式全backend共享改为每个原batch/raw owner独立提交；保留原iterator内部借用与history分组。冻结当前完整diff为`cancel-independent-prototype-base.diff`，不将该原型作为生产优化或新配置。先复用实际raw/兄弟operation、取消、默认值、extent及旧reader检查，区分业务数据失败与原共享提交次数/诊断中间态断言。它若不能保持同义结果，记录需改变的原始算法及费用后还原；不能为让试验通过仅放宽业务断言，也不能用其失败证明隐式共享是外部必要合同。

竞争反测已得到决定性差异：同一24行业务测试，独立事务原型22/4/0（含生命周期2），只在cold成功终结的4个BPP行拒绝；还原共享算法后18/8/0，8个真实root预算拒绝把已返回Succeeded的独立兄弟operation一起撤销。前者的新增拒绝是extent整字段冲突，后者是错误的业务失败范围，不能只靠恢复两边adapter解决。下一原型在原root准备处只对已配置derived extent的surface允许extent重算，保留所有非extent元数据及同页冲突；用实际合并后页树的现成bounds派生最终extent/版本，不新增第二页集合。还须覆盖“本事务原本未改变extent，另一事务先缩小extent”情况，不能仅修已有surfaceChanges的分支。API外部普通epoch模型保持严格手工metadata冲突；这是竞争原型，完整调用闭包和净价仍未合格。

显式owner正式迁移从冻结r3的算法继续，先删除prototype保留的匿名selector、failed和clients字段。clone/history/clear的冷准入改用原Store活动事务事实（显式history可占一笔），不新增第二owned计数或事务登记表；热终结不再维护整群状态，原transactionMutex仍保护history切换。普通read/clone在seal处验证旧current，在root接受后及adapter安装后验证新current；history明确请求的overlay保持原语义。旧“兄弟尚未finish所以manifest必须为空”、seal提前新数据和取消别的owner触发最后root等断言不能继续作为外部合同，也不能只放宽：需要保留独立读线程、retained exact读和真实root拒绝后的公开结果。local取消、abort拒绝债务与所有旧raw恢复仍按原T项继续，不把本段迁移单独标完整重构完成。

copy包事前边界（父ccbf0bcb0d）：沿T01.4保留调用者一次选择的source/target view及其稀疏裁剪，不把准入扩张到未裁剪的请求矩形。只对选中K页采用已有managed range并由原batch持有到adapter局部存储析构；prepareExtent/PreparedTileUpdates/presence容量在首个页操作前完成。最终remove/alias/partial事实直接写入原changed/presence结果，finishOperationBatch共同交付，删除manager copy的发布后resolve/新建wrapper尾路。原有固定target选择不新增为整个跨store操作的原子快照；本包不凭准入宣称修复选择前的并发策略。删量为每次成功copy的1次presence查询及D项再选择、D次晚创建路径；新增为K页范围准入/准备遍历及冷wrapper预备，单价和净时间未知，不能算作K16 write收益。验证原fixed-view/bounds/self-copy/oldData/default/failure，并将copy接入原reader窗口和adapter barrier测试；whole-range拒绝应由先做部分工作再取消变成首字节前拒绝。无新的持久owner、队列或恢复域。refreshPageStorePages尚有history消费者，不能随copy删定义。

copy并发反测修订：两架第一版安全组通过后，独立追加range-wait反例，实际得到应为0x31、却保留0x71的错误（copy-full-wait-repro-arm64，publish失败、cancel通过）。因此上段“保留原target选择”不再是合法最终方案。源继续固定；目标预先只读取surface几何，不创建完整view；原范围准入后才捕获唯一target view并核对format/layout/contentExtent，no-op据准入后的页版本判断。目标总capture仍每次1次；新增一个surface查询和几何比较，未新增K次逐页锁或第二完整capture。已裁剪范围的依据变化则在像素前拒绝，不无界重试或忽略新增页。只比较实际几何/layout，不以无关revision变化强制拒绝。增加此保证的成本单列为未知，不抵扣成纯删除收益；原反例及所有中间通过批次保留，最终资格只归修复后的双架身份。

修订再收窄：直接比较整个surface几何仍过度保守。最终传递原请求和已选矩形，由准入后的target view重新计算一次裁剪；只有实际选中矩形变化才拒绝。范围外extent变化、同内容revision变化不触发拒绝，像素格式按实际源/目标能力校验。target view在range成功后、创建/join batch前捕获，避免为几何预查构造一份完整capture，也避免新建匿名事务导致本来committed的读取变成空overlay capture。反测同时覆盖先写publish/cancel、请求内新增页拒绝和请求外新增页仍成功。

内部提交包设计约束（ce903fe3e9 已实施，双架五组 9410 安全通过）：T02.3/T04.4–5/T04.8从原delta直接投影，公共prepared-set输入先由独立validator核对后进入同一提交核心；内部调用不export三数组后再和原delta回比。CommitPreparation仍在原owner中保护其引用跨unlock，provider证据/descriptor保活、epoch不可变delta及重试revision均保留；已复核beginMutation/generic-write/conditional-removal/surface stage全部准入与在途activity闭包。原delta的类型供epoch借读，不新建owner、缓存或容器副本。history changedPages和full-default事实作为原record的必要输出在root接受前准备；空事务仍走原abort，不提交空root，不把无效事务当成功。独立preparedPages导出保留给clone/prune/history差量查询和公共validator控制。删除每次内部提交三容器导出、重复isValid集合核验和逐proof回比；最终epoch投影/metadata/provider检查不算删除，时间未知。内部提交旧包装、memento两套成功终点及遗漏测试caller已同包清理；随后进入restore实际差量和三类manager rebuild的闭包。

恢复包边界：T04.9 的跨历史节点反例已实际失败（restore-full-repro-arm64）：M1 改 A、M2 改 B，直接 rollback(M1) 后读到正确旧 B，但新写 B 被拒绝。root 整体恢复而 metadata 只应用 M1 delta 是根因。目标是由原 current/retained 两个不可变树直接向原 preparedCommit.restoreTargets 输出实际版本差量；按序游标跳过指针相同的完整子树，没有中间 manifest、第二 delta 或新持久状态。一般树差异最坏遍历 O(N+M)，删除键解析另有 D_remove×log(M)；共享子树可减少访问，但未测量前不承诺任意旋转都为 O(D log N)。固定栈上界来自 AVL 的节点计数位宽，动态预算为差量输出的实际 capacity 及增长暂峰，不预备 N 项。default 改变仍扫描原 directory 中相关默认页并保持 registration revision 重试；不更改 head/activity/retained/provider 拒绝。删除 restoreRetainedEpochDelta、完整 root 复制及 memento restore 的两分支。净价未知，这一修复新增真实差量生成成本，不能以错误稀疏路径作为理想成本基线。manager 交付仍须下一包迁移，不能宣称三处 rebuild 已删除。

恢复包的最终释放闭包修订：继续反测 purge consumer，restore-full-purge-repro-arm64 前台失败/后台通过；先 purge M2 再 purge M1 后实际保留 49152 bytes、必要 current 32768 bytes，遗留一页。背景释放早已扫描原 history work index，前台按 memento changedPages 限定遗漏了“memento 自己未写、但其 root 是最后持有者”的页。因此不能仅以仍有 consumer 为由保留 changedPages/full-default。改用原公共 releaseSnapshot 的完整 history work 语义（不是扫描全部当前页），合并 purge/close 的释放政策，删除 history 两字段、commit 对应输出/构造、releaseSnapshotDelta 及 read coordinator 的 delta 参数/单 consumer locked 包装。背景原本 all+delta 的重复 key 请求同时退出；前台可能访问更多实际历史工作，是修复成本而非免费收益。before/after 独立 token、共享 token 一次释放、部分释放拒绝后的记录仍保留。修订覆盖 T04.8/T04.9/T07，独立 backend dirty/prune 输出未被误删。

T04.11 枚举包边界：保留原 publication read gate、selector 选择、committed manifest 和独立 overlay export，原 root 中序输出已经按 surface/row/column 排序；只排序拥有的 overlay proofs/removals，随后归并/过滤到最终 logical page 输出。删除 N-key visiblePages 中间数组、逐 delta 的线性 find/erase、最终 N 页再排序。复杂度从 O(ND+N log N) 降为 O(N+D log D)，全量 API 的 O(N) 输出、manifest及overlay export仍计费；不为它新建捕获/保活或常驻缓存。publication gate 阻止基根发布/交易选择消失，sealed overlay在其原 owner 下导出；后者时点与固定base构成同一可见cut。验证 N1/17/257、D0/1/N、负坐标、删除后覆盖、冷增删抵消、overlay/commit/undo/redo 和既有并发枚举。输出 reserve 的 N+proofCount 上界空间也计费；不据静态复杂度直接预报CPU毫秒或K16 write收益。

枚举的选基反测修订：上述“publication gate足以固定正确base”的假设被 enumeration-full-base-repro-arm64 证伪。active history自己的view仍应为base+overlay；另一个有效Store事务推进current后，pageAllocated(9)为false，allocatedPages却返回3页而非2页。最终输入选择必须在原Store owner中一次完成：publication owner验证原事务身份，保留其真实base root，并只复制本surface的原proof/removal key。Store显式解锁后，原root按序遍历直接归并到最终输出；没有N-version manifest、N-key中间表、完整proof/surface导出、重复isValid或额外pixel capture/retention。D key projection和输出实际capacity仍收费。提交后原history正确rebase，完整输出包括另一个事务的页。三处私有方法分别是原owner的输入选择、原Store锁边界、原不可变树输出，不新增owner/状态/队列；前一版通过批次和失败反例均保留，不能继承其最终资格。
枚举最终结算：0e55a60932，enumeration-full-r1双架9456/0/0。target-r1的唯一失败是夹具两事务同时扩extent引发合法冲突；预置page10边界后target-r2及最终全组通过。两次语义失败、首版通过、最终通过均归档；manifest成员108个已复核，产品冲突规则未更改。

manager恢复交付包事前约束：直接借用原preparedCommit.restoreTargets准备/安装兼容索引，不投影第二份D列表，不新增持久owner或恢复队列。manager gate固定表身份；恢复原idle/head/activity/retained检查保持。所有非默认冷wrapper及extent容量在root接受前准备；版本/目录重试只能扩默认虚拟页目标，原current/retained根不变，因此冷准备仅一次，成功用最终实际targets安装。root拒绝不交付；成功后安装不分配、不拒绝；候选和旧default backing在manager锁外析构。默认变化仍更新原default backing，不重建N个wrapper。trim/read失败三consumer全部迁移以前不得删除rebuildPageStoreIndex定义；本包不删除其余真实consumer。净CPU及相对upstream收益未知，先验证真实恢复/拒绝/重试/reader/后续写反例。
恢复交付反测修订：restore-delivery-full-r0-arm64 的 testUndoingNewTiles 失败，其他五组及新增恢复矩阵通过。只创建 writable wrapper、从未暴露像素的 legacy intent 会扩大兼容 extent，却没有任何 root 差量；因此原“实际 root D 已完整覆盖 adapter”的前提被证伪。不能删测试、改 intent 的既有可见语义或建立第二持久 touched 表。最终 preparation 同步借用原 retained root：遍历现有 hash，按 root membership 找出实际 absent wrapper，在原 PreparedTileUpdates 数组内准备删除；root 的非默认 D 仍只准备缺失 wrapper，成功后统一交付。保留未变 wrapper，但当前合同下必须支付 N 次 root membership 查询，最坏 O(N log M)，再加 D 准备/安装和候选排序；不能再声称 manager restore 是纯 D 或整个 N 遍历已删除。旧全量 clear/recreate 仍可删除，CPU净价待测。若以后想消除此扫描，必须先重新设计 intent 的归属和可见性并定价维护成本，不能靠两边 count 相等假设集合相等。

同包发现无锁 hash 的 deleteTile 在交付中调用 QSBR::prepare，并可能由普通 map.erase 参加迁移，原“无分配安装”保证不完整。现准备原 map key 和 GC action 后，以 PreparedKey::exchangeValue(nullptr) 接回原 queue；不新增回收队列。两 hash 的原 PreparedTile 扩展明确 Present/MayRemove/Absent 意图，所有 caller 和测试迁移，删除 prepareMissingTile 旧入口。只有完整页 clear/copy（rough 的全部页）准备可能删除；普通 warm 写、partial clear/copy不加记录。不能以等待前 default 相等性裁减候选，因为 admission 等待后 default 可以变化。restore 的纯 absent 不创建冷 wrapper。GC/key/candidate 增量、可能未用的完整页删除准备及一次额外 publication gate 均计费。
恢复交付锁序反测：在 r1 ARM 六组4792通过后，新增 testPageStoreRestoreDeliveryAllowsTileReader。已有 Tile 在 swap barrier 内进入真实 backend read selection，恢复在 RestorePublishOwnerWait 启动该 reader；旧新增交付仍持 backend mutex/publication write，再试取同一 tile barrier，发生环等。restore-delivery-full-lock-repro-arm64 由记录在案的12秒外部 watchdog 只终止本批测试子进程（exit−15、无Totals，runner完成身份校验，watchdog.json在原始归档）；不是测试通过。修订为原 transaction gate 保证memento身份，lookup后释放backend mutex，canonical接受后在进入adapter前释放publication write，manager gate仍覆盖兼容交付。读者先看到已接受canonical，再释放tile barrier供安装；与原operation completion锁序一致。原源码/失败批次保留，最终资格只归修复后的双架身份。
删除准备再收窄：填充/复制 producer 将其准入后原固定view的 default 比较事实传给原 prepareAdapter；非默认 fill、源/目标默认值不相等的 copy 无删除记录，partial 页也无删除记录。fill 的原 capture 提到 prepareAdapter 前，成功路径总 capture 数不增加；准备被拒绝的失败路径会更早创建/释放这份实际view，计入失败成本。相同默认值 copy 的完整页仍按可能删除上界准备，尚未逐页筛掉非默认源；这是有界新增成本，未冒充纯删除或已测净收益。没有第二份 selection、N-key 权威表或永久状态。
完整集合反测修订：restore-delivery-full-presence-repro-arm64 实际2通过/1失败。独立backend发布page5但manager尚无wrapper，再创建page9的intent；root/hash数量都是2，集合不同。仅扫描hash删多项仍遗漏目标root中无版本变化的缺项。最终prepare只借原retained root：一次原hash遍历找多项，一次root::forEachPage直接遍历找缺项，都进入原PreparedTileUpdates唯一候选数组；不创建N-key/manifest或持久第二索引。完成时先删多项，再用实际root D失效/安装版本变化，最后消费尚未安装的缺项token。原D完成后已消费的token不重复安装。准备复杂度为O(H log M + M + S log S)，H为原hash页数、M为目标root页数、S为实际多项/缺项候选数；另加原root差量生成及D交付。多surface树遍历仍访问完整root节点，M上界应取整棵root，不能默认单surface。删除的是全量销毁/新建及N-key枚举输出，不是必要的双向集合核对。整套方案不再依赖“root和adapter本来就一致”这一未经证明的前提。

owned终结r1反测：8个业务组合全部在解除真实MetadataArena压力后activeCpuWritePages归零、activeTransactions仍为1；2/8/0含init/cleanup，实际库/源码身份通过。开始实施前确定原责任：将batch的owned事实移入其原mutation，不复制第二终结账本；最后release与原orphan retry共同执行私有cancel→owned abort，直到原transaction接受退出。成功commit/abort解除该责任；明确borrowed history不被自动abort。manager交付仍在进入orphan前完成，backend最后弱槽在guard全归还且原scope可靠承接后退出。默认值入口改借同一原mutation承担事务寿命，删除其独立abort分支、Backend abort wrapper和忽略abort结果；冷创建失败的新空事务须同步撤销，不能遗失。代价为default额外原scope准备、必要终结锁/活动，普通batch复用既有scope，无新队列/执行者/持久事务目录。预先准备每个可能取消的retirement资源会放大所有成功路径且不能消除prepared reader阻塞；原orphan已具备无输入进度，选同一完整责任延续，不新增恢复域。

实现前直接方案复核修订：default是私有surface-only事务，无page proof/session/raw lease/prepared reader，不能为形式统一新增空mutation及其分配/活动。其三个独立abort分支改成一个函数内guard，阶段后既有commit失败同步abort；原空事务创建失败同样没有物理取消来源。真实pixel mutation才将owned事实从batch移入原scope并复用orphan。删除Backend独立abort wrapper和忽略返回，保留writableTransaction作为两个真实入口的共同分组选择。普通default不增加scope/control-block分配；以上替代先前default也建scope的草案，未对该草案领取验证/性能资格。

同一终点补充：r2初始8个压力反例及原取消/锁窗/独立owner控制共74项通过。继续覆盖finish返回false而公开facade仍存活：逻辑adapter已完成后，物理cancel拒绝立即释放原session引用给既有guard/orphan，不待无用facade析构；原Store claim仍排除冲突。尚有live working guard时completeAdapters会拒绝，原batch仍随该guard保留，不能提前丢manager交付。另覆盖seal后root真实预算拒绝，以及surface-only无像素proof的拒绝/重试与operationSessionsCreated不增。此为同一责任的真实生命周期边界，非独立优化收益。

最终持有者再审：r5 ARM六组5010/0/0后，发现仅释放mutation可能过早移除仍有真实native lease的线程槽，而只依赖facade析构又会延迟无输入收尾。最终普通finish/cancel移动掉facade的原shared引用，实际lease仍持有原batch；有lease时不交出其槽，最后lease锁外释放触发原终点。显式OperationDelivery仍保留原引用，因为adapter是实际consumer。原isActive和已finish replace入口同步处理空facade。增加真实native lease控制：finish拒绝/保留已finish facade→仍拒绝新batch→最后guard归还→无需销毁facade即可新准入/旧像素/事务归零。无新owner或回调，删除无消费者facade保活；不是给每次unlock新增一套终结政策。

最终r6成本边界：owned batch复用原scope承担事务末尾；成功直接进入原publication核心，不再从公共commit入口扫描同事务orphan，后者仍服务公共Store caller。owns标记从batch移入scope，未增第二份责任事实；scope布局变化的实际字节/净时间未定价。成功publish/abort不额外查询事务身份，仅拒绝后的cold分支区分仍活跃与已被显式Store abort。surface-only及新空事务撤销没有像素或prepared-reader消费者，保留同步局部退出，不构建恢复记录。r4 root预算拒绝4行在观察点activeTransactions已为0，不能冒充实际延迟abort拒绝；真实私有cancel压力12行观察为页/事务均1，解除压力后无新输入归零。最终全包的四raw producer、history交付及性能范围未缩减。

四raw producer迁移前判别（父11adac3e3a）：先核验live-source是否真的可以交给ImmutableAlias。当前两copy在源raw writer仍存活时调用captureCompletedTileSource，仅保活TileData，不冻结现存raw pointer；旧测试明确验证同指针，但只观察copy返回当时像素。新增ordinary/rough两个真实公开入口：copy之后取得目标exact view，再经原source pointer改字节；目标已捕获版本必须不变。若失败，必须先修正源输入能力及其算法成本，不能只延迟wrapper安装并继续把mutable source宣称不可变；公共upstream对应观察与新增exact能力分别记账，不把共享TileData地址当算法必须相同。此阶段仅反证，不改生产或领取净性能。

同一T06.3的packed/planar独立取消判别：调用者原先持有page0裸指针，本次函数写page0、已有page1、新增page2，随后page3真实swap-in在Mapping/Allocation/Decompression拒绝。检查本次原D/B撤销page1/2、canonical仍为before、原page0裸指针不被跨owner取消；最后归还原能力后重试同范围，history undo恢复。两API×两history状态×三真实拒绝，共12行。通过后拟删除这两caller的rect全量refresh：原D已经在claim内失效cache，原B撤销实际cold插入；不再capture/resolve/pin/换入未触碰页面来处理取消。直接读取未锁TileData不构成新读取合同，后续合法lock/read必须解析正确版本。剩余两个copy还有root前warm wrapper替换，保留其refresh直到真实producer迁移。数量预测仅为每次失败删除一次capture和A个矩形页的resolve/尝试安装；正常路径无独立收益，净时间未定价，不申领M6性能资格。

raw-write r2全组六组中manager1631/2/0，其余通过；仅两个既有RegionWriteFailure的planar行未收到原qWarning。保留原诊断输出并只删refresh，不改失败断言，后续独立r3冻结。live-copy诊断的两个失败仍保留原patch和独立归档；为避免把未解决的另一语义问题混成此候选的修复结论，活动测试移出该诊断，不能据r3全组通过宣称live-copy已通过。

T04.10 clear交付实施范围（父f25d3085d0）：沿上一版蓝图的原表/原token方案，将manager clear的hash删除准备移到同一remove batch接受前。复用PreparedTileUpdates的实际removal候选，restore/trim和clear共用prepareRemovals；全量clear无需排序或构造第二份变化输出。removePages接原prepare/completion/OperationDelivery，非空canonical的claim保持到安装及候选锁外释放；空canonical但仍有wrapper时仍完成兼容准备/交付，不为形式统一创建空事务。保留legacy-only hash clear、外部排序的clear barrier及原same-thread raw取消合同，不新增跨worker clear保证。删除PageStore成功后的hash clear晚分配/重试路径；保留原table identity。

这不是纯净删成本：原先已有的N个QSBR动作提前准备，另需原PreparedTile的map-key保活和候选容量，并延长原claim；不新增队列或权威集合，但峰值和净时间待定价。先验证受控adapter拒绝后canonical/extent/table不变，N0/1/17、history、独立backend造成的非空wrapper/空canonical、旧raw/exact读及undo；受控回调拒绝不冒充实际allocator失败。再用真实malloc/calloc/realloc/aligned/free拦截检查接受后的install区间，并有正分配控制，不以capacity断言代替。公共upstream语义及原清除/恢复控制保持；purge和history终结仍属原33项未完成部分。

clear allocator探针r0正控制没有观察到分配，exit2且0业务行；改为真实manager构造作为正控制。r1正控制620次分配已证明拦截生效，但timer构造不会通知phase observer，缺少install开始事件，结果误带入上一控制计数；该1行不是产品安装发生620分配的证据。改用与原adapter一致的IndexRefresh→next(Install)→next(Installed)，探针同时要求starts/events各1，r2重新固定身份运行。所有无效测量保留，不作为零分配资格。

clear r2真实拦截双架各64场景（BPP1/4/8/16、N0/1/17/129、有无history、有无canonical外的wrapper残留）均starts/events=1、安装线程alloc/free=0，正控制实际manager构造有分配。测量仅覆盖接受后install区间；候选/map-key准备和锁外回收仍收费，不外推为整次clear零分配或净时间改善。clear barrier先取消旧raw能力的原不可逆顺序保留，后续准备拒绝不承诺恢复被barrier取消的未发布raw内容；本次12行受控准备拒绝验证的是canonical/index未被新删除，不冒充这一原raw取消本身未发生。
