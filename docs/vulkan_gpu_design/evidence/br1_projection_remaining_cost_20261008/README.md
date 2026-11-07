# 剩余投影成本深挖：先修正价格，再选择责任

固定产品 `6644249a4cfd2c48225685a2c27f1a8318def1c3`，文档父 `d277af01c8e61699b7393da08dc9ac5ba8e8cf18`。本包只有外部派生观察库与分析，无产品修改；原候选Undo回退、原分支a918及M6未通过不变。先按[原协议](PLAN.md)分解，再因实测观察扰动按[补充协议](SELECTIVE-PROTOCOL.md)做一次分组观察，随后停止采样。

结论：冷准备、发布和operation准备均有实际成本，但没有发现一个已证实可删除、足以承担剩余约4ms差距的单点。特别是“局部metadata状态投影是最大核心”的预期需要降级：不打开其内部时钟时，prepare+publish整个外层只有约0.40ms，不能把重插桩后的约0.8ms当作新瓶颈。最值得形成完整替代方案的是同步CPU的准备/预算/登记/绑定生命周期，其次是每operation重复建立范围、batch和execution；具体净删除预算尚未证实。

## 1. 实测身份与观察扰动

首批4能力+10观察过程，后继3能力+16分组过程，合计33过程、99 QTest通过。全部像素、8 segment/4 update callback、销毁、实际加载库及正常退出/timeout/reap核验通过；全部19 projection updates。所有有事件过程无overflow/栈错误/活跃尾；逐事件self+children=inclusive，以及每过程互斥分解之和均核对。没有将这些过程计为新的安全大矩阵或性能资格。

| 观察方式 | 同批粗观察投影CPU中位 | 分项观察投影CPU中位 | 描述性观察增量 |
|---|---:|---:|---:|
| 首批全部分项 | 4.327ms | 5.791ms | 33.8% |
| 冷准备子调用，组1 | 4.320ms | 5.071ms | 17.4% |
| metadata内部，组2 | 4.320ms | 5.029ms | 16.4% |
| 发布/operation，组4 | 4.320ms | 5.410ms | 25.2% |

每种分项4个独立过程，组间不配成优化前后，不授概率CI。分组仍有明显扰动，只能用于工作量与量级排序；不能按一个固定比例扣除每项clock成本。首批upstream粗观察0.499/0.525ms用于边界核验，不与新候选构造正式性能比较；原约4.024ms差额仍属于上一冻结批，产品未改不领取新收益。

关闭标签在编译可折叠的标签选择后使用minimumMode=999，不进入事件/clock；旧基础scope仍保留。扩大的固定observer bank属于诊断资源。group源码、编译命令、链接对象及运行库身份见原始包与`build-identity.json/selective-identity.json`；不是将产品预算放宽。

## 2. 第一优先：冷页准备拆到具体消费者

组1整段cold 1.745～1.869ms；下面为同组互斥归属，中位数不能逐项相加成一个过程。各项均在132个投影冷版本内，base中另有56次descriptor准备归在base，不能把全投影188次误报成下面descriptor项的132次价格。

| 冷准备责任 | CPU中位 / 四过程范围（ms） | 实际内容及裁决 |
|---|---|---|
| 剩余cold外框 | 0.568 / 0.539～0.592 | 尚未单列的binding取得/写权reservation、终态核验、descriptor安装、锁交接、局部值/guard终结及观察边界费用；不能全部归给锁或析构 |
| provider allocate | 0.372 / 0.364～0.411 | 包含物理页、copy/fill、retirement票据与provider自有登记；不是全可删 |
| private metadata prepare | 0.246 / 0.232～0.254 | default源重读及两步metadata转换，内部时钟关闭 |
| base选择 | 0.209 / 0.195～0.218 | epoch/overlay解析、metadata base、虚拟default/descriptor建立与新身份；不是一个map lookup |
| backing reserve | 0.131 / 0.122～0.139 | domain同步、transient界、payload+retirement debt准入，原退休与安装节点预备 |
| backing register | 0.077 / 0.073～0.084 | 两次physical footprint观察围绕domain registration、logical/physical索引与实际收费接收 |
| 目标descriptor预备 | 0.054 / 0.051～0.055 | 132个target版本的节点/共享值准备；已有相等descriptor值会共享 |
| cold page存储 | 0.046 / 0.042～0.052 | 原ColdPageSet slot建立，暖slot不重复建立 |
| claim entry | 0.035 / 0.034～0.036 | 原write-set/claim接纳，含锁外实际存储准备 |
| writable pin | 0.022 / 0.022～0.023 | 132次冷链内原物理写保护；暖调用不混入本项 |
| plan选择 | 0.021 / 0.021～0.021 | 本用例没有自然recoverable-before机会，已是便宜的Fresh选择 |

源码闭包：[beginWriteImpl](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2048)、[base](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2657)、[reserve](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2875)、[register](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:968)。132条中有真正独立的provider、domain/收费和metadata权威；相同key不自动意味着重复所有者。

下一方案应沿同一已准备CPU结果检查哪些解析/布局/物理事实能随原reservation直接交付，哪些在真实解锁或domain变化后必须重验。不得把0.568ms未拆外框全当可删或预报可以追回1ms。一个具体相邻审查点是写路径descriptor清理guard即使安装后容器为空也会unlock/relock；它可能删掉空清理交接，但仍需证明allocator保活和非空拒绝路径的锁外释放，且它没有独立价格，不能单独冒充完整优化包。

## 3. 第二条假设的修正：metadata没有显示异常重试放大

四个metadata分组过程均264个local sequence、每个内部相位也264次，等于132 prepare+132 publish；本用例没有观察到局部growth/revision重试放大。代码只投影相关版本，不是每页复制全部历史。[applyProjectedSequence](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageMetadataCoordinator.cpp:3703)仍执行局部投影、转换、容量预备及权威索引安装，但这些事实不能自动授予整个桶的删除资格。

未开启内部时钟的组1，prepare+publish每过程合计**0.405/0.409/0.389/0.428ms**，中位约**0.407ms**。内部phase开启后，仅metadata_local就为**0.755～0.803ms**，parent prepare+publish为0.858～0.907ms。该额外增加来自观察条件变化，不能解读为产品新发现了约0.8ms状态机成本。

组2内部观察：状态投影约0.130ms、状态转换约0.070ms、预备约0.146ms、安装约0.143ms、清理约0.057ms，另约0.231ms在相位间外框中，包含观察器enter/exit等费用。它只支持“不能只盯状态转换算术”的方向；不能按这些数相加精确估计去掉通用状态机的净收益。整个未内插桩外层约0.41ms是该候选的工作桶价格，不是可实现的严格节省上界；大部分合同仍须执行，实际收益会小得多。优先级降到冷链整体之后，不直接另建CPU专用状态机。

## 4. seal/commit具体花在哪里

组4的seal约0.765ms、commit约0.648ms，包含观察扰动。seal主要为private publish0.215、proof准备及writer reservation释放0.131、overlay候选存储0.102ms；overlay metadata prepare仅约0.009ms。不能看到“metadata”标签便优先改该小项。

| canonical commit 相位 | CPU中位（ms） | 实际责任 |
|---|---:|---|
| transition preflight | 0.144 | metadata出版候选与其预备 |
| cleanup | 0.091 | 原metadata清理、回锁、proof撤销、overlay移出、history bookkeeping；不是仅free |
| completion | 0.076 | 包含backingChanges构造及预算变更预备，**不是完成票据单项价格** |
| provider validation | 0.069 | 逐proof核验metadata/provider及布局 |
| epoch prepare | 0.066 | 不可变root候选与重基准备 |
| metadata apply | 0.056 | preparedCommit联合安装调用；标签不等于只改metadata |
| provider retire | 0.039 | 原回收推进及最终候选/overlay释放 |
| epoch delta prepare | 0.019 | 为epoch owner建立独立delta |
| input proof validation | 0.017 | 公共输入与原owned状态一致性、descriptor保活 |

源码：[commit输入/校验](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:917)、[metadata/root预备](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1053)、[预算到清理](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1090)。组4四次commit为11/14/12/12，各prepare/install相位同次数，没有观察到重准备放大；首批全细分有两个过程各多一次prepare，仍不是数量级放大，全部保留。

这些阶段分属状态候选、预算接纳、联合安装和释放，说明成本确实分散在整条提交协议中。若只绕过公共输入反查，0.017ms整个桶也很小；不能拿整个0.65ms作为该改动预算。真正的提交设计必须共同消费一次原delta，保留独立epoch/metadata/预算接受点及晚reader，不是删除一次proof循环就算完成。

## 5. 按新证据排序及实施边界

组4在19次operation中，range准入约0.136ms，range取得后到adapter之前约0.200ms；后者实际包含`beginMutationBatch → writableTransaction → beginMutation → adoptReservation → borrowExecution → surface校验`，不是“等待”。像素body约0.255ms；adapter准备约0.032ms；changed export约0.004ms。源码[operation](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2064)和[batch建立](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:923)支持把完整作用域准备排在另一个小容器微改之前。该价格只覆盖19次合成operation，不外推成32次全部batch费用。

| 顺序 | 下一完整责任 | 已测工作桶与可证伪的方案边界 |
|---|---|---|
| 1 | 同步CPU冷准备→登记→绑定→清理 | 最大剩余有界责任；先细核原reservation是否可交付稳定事实，删重复接收/临时交接；base、provider物理、ledger收费、metadata接受点保持。约1.5ms旧低扰动整段不是全可删，0.568ms新外框也仍混有观察成本 |
| 2 | 一次operation的范围/batch/execution建立与终结 | 已测两个相邻桶约0.34ms量级；沿原owner共用已接纳target/claim，审查同步native是否重复构造facade/registry/borrow事实。保留与iterator交错拒绝、失败取消和实际释放，不跨clear/filter/composite强行合段 |
| 3 | seal/canonical原delta贯穿metadata、root、预算及清理 | 分项已明确，需整体减少表示/接收次数；输入反查仅0.017ms，不先为它增一套内部提交协议 |
| 4 | 读选择及merge外框 | capture约0.34～0.36ms，merge余项约1.1ms仍包含多个消费者；尚未在本包进一步细分，不称全已归因。要按真实source范围/oldData使用及释放端证明复用条件 |
| 降级 | 独立替换local状态机、继续优化plan、单独改changed数组/公共proof反查 | 相应整个工作桶已小或价格被观察器放大，不支持作为下一高收益主包 |

这不是所有项各自重跑一次优化验收的清单。形成候选时应把同一责任内已证明等价的相邻删除一起实施，再做固定父/候选/upstream和Undo控制。当前尚无足够证据给新的净收益百分比；条件删量和必要成本须先拆清。机制/稳定数量证据强于时间单价证据，未识别到所有remaining CPU不等于证明它们全是不可避免的维护。

## 6. 失败、复算与冻结

首次派生脚本因seal后下一成员的匹配假设错误，在编译前断言停止；原`build-v1.py/build-runner.log/observed/`保存，v2收窄到实际函数边界。初版分析器某项call count取全projection数量而CPU只取指定上下文，后改为上下文计数；v2又将输出prefix复用为Commit相位，导致输出文件名错误，日志及旧分析器保存。v3重析相同原始样本生成`group-1/2/4-summary.json`和accounting；没有重新采样或移除进程。`Commitsummary.json`及初始`summary.json`仅作开发记录，当前解释以group文件为准。

首次归档校验因库链接不是regular member而拒绝；改为dereference保存对应实体内容，旧脚本/日志/清单/归档以v1名称一并保留。这是打包修正，没有改变样本或数值。

复算：在本证据目录解开[原始包](raw.tar.xz)，运行 `python3 analyze.py --group 1`（同理2、4）；全部结果和验证应一致。`build.py/run.py`、`build_selective.py/run_selective.py`保留预定批次与拒绝覆盖规则；重跑须另取目录，不能覆盖冻结数据。原始派生源码、对象、两观察库、逐进程日志、实际加载哈希和失败随[清单](raw-manifest.json)及[EVIDENCE](EVIDENCE.json)保存。复用对象/fixture来自上一冻结包，链接输入逐项校验；本包不另复制完整构建环境，重建仍依赖已标识的原构建输入及前批fixture/对象。生产增删0，M6/原候选启用裁决不变。
