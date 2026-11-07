# 操作级发布与工作容量：完整候选的实际结果

2026-10-12。当前checkout为本地候选 **02bccf1d12aba554e02d827ed418d5f94ed8fa99**，已验收比较起点仍为11c689。实现、安全、主要事件差及H1局部净价已验证；**独立确认指令省16.74%、CPU省2.86ms，但5个存储CPU控制、业务收益/控制及全部资源资格未闭，整包和M6未验收。** [完整计价与剩余账](RESIDENT_OPERATION_PRICE.md)含重启后的126过程。原33项唯一实施状态仍在[蓝图§13](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-change-index)，事前理想设计/数量预测仍在§19.15。

## 实际实现与保留责任

内部CPU证明和descriptor使用原metadata版本的预付facts槽。独立DescriptorMap已经删除；同布局只借用同base或同准备批次的不可变值，不再全表寻找相等descriptor。公开generic多次签发proof有独立consumer，继续保留原注册表；不能宣称所有proof或shared_ptr都消失。

H1原transaction/page节点最多留一个仍收费的备用backing。无逻辑保护的旧CPU Prepared在接受时直接退出metadata；下一次取用仍须通过物理claim、generation retag、费用rekey和metadata复验。被拒、未取用、semantic alias/source初始化、remove、commit、abort、close沿原预付retirement record退出，没有第二个cache owner、退休队列或恢复账本。已有读者/capture/clone/last-use的保护不削弱。

合格H0匿名operation在原scope和commit claim之间交接，借用同一组候选行进入共同canonical提交核心。它不安装中间overlay；显式history、checkpoint、legacy/generic及不满足独占条件的入口保留原overlay。root准备失败仍由原scope取消/abort；adapter安装继续使用原候选与原manager联合交付窗口。

新增17份生产文件的差集为 **+913/−288，净+625行**；3份测试+348/−42；审计源+13/−7；派生审计JSON+27019/−21913。新增代码主要表达版本facts预付/退出、容量换代及借用输入适配，不能将其称为整体复杂度下降。PrivateWrite目前仍通过原prepared core准备base/target工作值；这个成本与新facts、PageState备用字段、动态检查和长期保留都须在净价中扣回。此时不再按热点追加微补丁。

精确文件、哈希、增删及旧符号删除检查见[source-index.json](resident-operation-r1/source-index.json)。`DescriptorMap`、`KisPreparedOverlayUpdate`、两个旧prepareOverlay入口、`removeDescriptorLocked`、`revokePreparedProofLocked`在生产范围已无引用。新版结构索引为87 TU、2292 API、31087调用边、26 callback；原21 manifest、26 ownership、16 census及侵入上限没有放宽。

## 数量预测与实际

下表是四寿命、每写立即读及完整退出的隔离计数，**所有该库的时间数值弃用**。birth/retire计的是非默认backing identity登记/退出；主H1无alias时与独立payload/binding周转一一对应，clone子例的identity数不能直接叫物理字节分配数。

| 项目 | 事前基线→目标 | 实际候选 | 解释 |
|---|---:|---:|---|
| K16/H1/W16 backing建立及最终退出 | 1088→192 | **192/192** | 896次复用成功；没有把退休延后藏出终点 |
| 同用例旧Prepared进入Historical | 960→0 | **0** | 960次逻辑退出保留，在原接受中直接执行 |
| 同用例内部独立proof节点 | 1088→0 | **0** | stamp与真实校验仍在facts中；generic节点保持可达 |
| 每代独立descriptor map节点 | 1088→0 | **0，静态删除** | 不等于descriptor值/引用或metadata槽免费 |
| K16/H0/W16过渡overlay | 路径推导68→0 | **0** | 实际匿名canonical提交仍68；backing1088保持 |
| H1/W2容量循环收益 | 0次 | **0次** | backing192/192，不把预留备用误称已复用 |
| H1直接native单页holder，原能力用例 | 源backing196 | **196/196** | 仅PageStore能力对照；旧指针跨覆写不变并非同义前提 |
| H1 full clone holder | 源256 | **全用例320/320** | 含clone自身64个登记，源条件数256；832次复用 |
| 修订的一页副本＋native holder | 源196＋副本4 | **全用例200/200** | 892次复用；三方公共净价及控制见计价报告 |
| H1重复partial | 未给毫秒预报 | **96/96，复用224** | 仍复制3,670,016字节，不能记为零COW工作 |
| H1重复no-op | 保留既有no-op | **64/64，复用0** | 只有初始payload；overlay0 |

H1主格新facts block累计实际分配容量为 **15,872 B/四寿命**，不是峰值或常驻量；directory、引用控制块、所有权节点扩大仍包含在真实预算和最终CPU账内。必要逻辑generation没有融合，中间每写可见性保持。H1的4次匿名初始canonical加4次history提交仍为8次；计数中的`canonical_operations=4`只计匿名路径，不能误读为总提交4。

原数据：[quantity](resident-operation-r1/quantity/results.json)、[修订holder后的quantity-r2](resident-operation-r1/quantity-r2/results.json)，同库身份与实际加载依赖在各目录的identity/runtime文件。clone的源256来自全登记320扣除四次clone各16页登记，不是独立物理分配采样。原冷/暖、资源峰值、留用时间及其他压力资格不因这13格数量成立而自动完成。

## 安全与实际安装

同候选普通库`e81d7a92b47d8126f89edbd852e5c623847ae937fe8337c4507a3b620b591ef8`，六组测试两架构各5313项，合计 **10,626 passed / 0 failed / 0 skipped**：[完整结果](resident-operation-r1/safety-r3.json)。新增80项覆盖工作容量循环、取消/abort/removal、初始/晚物理reader、capture、clone、last-use，以及H0接受、root存储拒绝后重试与显式history控制。

实际allocator interposition每架构32格、544个安装窗口：canonical80、工作容量272、manager adapter128、overlay64，**分配/释放均为0**；包含真实分配正控制及加载库身份：[arm64](resident-operation-r1/install-r5-arm64/result.json)、[x86_64](resident-operation-r1/install-r5-x86_64/result.json)。这证明所测安装区间，不代表整个operation无分配。结构门及6项工具自测通过。

原失败全部保留。早期版本facts槽被reset、budget目录容量漏算、CPU证明终结重复处理、旧失败注入断言均已修复并由最终完整矩阵覆盖。两页ActivePending循环与最终Debt额度分开，四BPP压力测试为ActivePending两页、Debt三页，不能把“循环只需两页”误写成全生命周期退出也只需两页。

完整manager首轮每架构112个失败来自旧测试在`MutationSealCleanup`期望尚未canonical；新的H0路径此时已经接受。三组测试改在真正接受之前的`MutationSealPublishOwnerWait`观察旧值，保留新值、旧View、extent、clone和并发联合可见性断言；双架130项定向及最终完整组通过。x86安装探针的一次SIGABRT是探针漏掉metadata安装拒绝的区间终点，导致合法reprepare触发探针嵌套断言；[栈归因](resident-operation-r1/install-r3-x86_64/failure-attribution.json)与原失败保留，补`CommitCleanup`拒绝终点后两架通过。它不是可删的生产重试。

## 净价结果与剩余责任

用户重启后残留已清除，产品与原库哈希保持；[恢复后身份](resident-operation-r1/resume-after-reboot.json)。修订三方能力3过程全部通过：candidate-original69/69一致，upstream65个同义格一致，bad-tail52–55的既有差异单列。计价13格均同义。随后探索24、独立确认48、原业务51过程全部正常退出、加载/语义正确，无排样或补样。

[完整价格报告](RESIDENT_OPERATION_PRICE.md)和[可复算净账](resident-operation-r1/price-ledger.json)给出：H1指令179.2301→149.2214M，净省16.7419%，单侧95%下界16.5468%；CPU13.4207→10.5621ms，净省2.8586ms，下界2.4320ms；前台增费上界0.1601ms。三项局部门通过，前台改善本身未确认。其余线程指令少37.1641M，前台反增7.1553M，其中write多8.4426M；候选仍比upstream多122.6434M指令、9.1133ms CPU。

12个存储控制的指令非劣均通过，CPU在case0/2/4/5/64未能排除>2%回退；并非证明真实回退。业务Stroke净省0.4158ms [−0.3950,0.6205]，收益未确认，Undo/Teardown非劣未闭。整体性能资格为false，M6/M7/M8仍0/3、校准2/20、默认关闭；候选未push，不能用主格局部收益替代全部资源/压力与原控制。

本批有限样本冻结。下一责任是复用写的准备→收费/metadata转换→接受，先解释前台新增工作与剩余write差额，不追加零散微优化追门。原33行状态和成本列已更新；原数量、安全、生产净+625行和完整资源未知项保持。

## 保留的阻塞与归因修正

重启前upstream旧case66在同一tile持read指针后覆写，要求指针仍返回首写旧值。日志已有COVERAGE_ASSERT_FAILED，采样停在fixture.cpp:76→abort→pthread_kill；旧“等待自身读写锁”归因已撤回。180秒timeout、SIGKILL后reap失败及定向恢复失败全部保留于[原失败](resident-operation-r1/capability/02-upstream/failure.json)和[恢复诊断](resident-operation-r1/environment-recovery-r1/README.md)。这些时间没有进入净价，具体OS退出阻塞根因仍未知。修订case66先经公共bitBlt创建单页副本，再持副本native reader并覆写原manager，三方承担相同快照工作。
