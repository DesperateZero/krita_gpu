# CP1 集中结清续轮：实际等待容量和拒绝接续仍未关闭

产品 `1103defd830d463c50f8c6a83dd05cc8077e0bf3`，父 `a36e1b0ad090fb24e7cd43c22833b6026ab7c14f`；外层父 `f4aee735beb67e9b9e0a54cfdf1a8dcf6996a34b`。依据当前代码、92和 cohesive-refactor；未读取 archive。完整CP1未勾选，M6/M7/M8正式0/3，persistent默认关闭。

## 已修复与行为成本

`sealImpl` 三段手工 provider activity 合并为整个原seal的一次scope guard，异常退出先恢复owner gate再归还计数。真实第一个私有publish输入分配拒绝后，同owner重试及close已通过。已安装overlay后仅捕获输出失败，保留原session及接受结果；新增硬满测试连续三次拒绝、费用恢复后同scope捕获，sealed页数/provider准备次数不增加，原冻结视图保持。未将前期partial seal失败改成已解决。

原关闭诊断在新worker仍分配16B Darwin TLS。新增只读存在性检查跳过TLS；disabled recorder析构和setRecording也不访问TLS。4B实际全局atomic与原ProcessStorageState合计固定60B，收费原位增加4B；启用profiling的TLS仍在显式调用者诊断范围，需要独立计量。生产四文件+29/-13净+16，测试两文件+49/-0净+49；图/库存生成物单列。无新增业务owner、队列或上层生产API。

## 真实故障矩阵与原失败

[lifecycle-matrix-03/results.json](lifecycle-matrix-03/results.json) 为两架共505个隔离原进程：18成功控制、487个发现的paid调用链首/末目标；383进程成功，**122个实际同owner接续失败，正常exit9**。capture、冷default read、rollback、release已接受留债的检查通过；resident read、purge、合资格close此夹具未发现paid分配，不能当这些入口全部拒绝点已覆盖。故障只注入调用测试线程可识别的paid链，不覆盖每次中间发生次序和Qt/OS内部故障。

失败按真实终点分组：checkpoint54、commit54在前期准备拒绝后session已取消；checkpoint4、commit4重放先前页的私有publish而stale；commit6在终结后再次提交时原transaction capability无效。原root/冻结像素检查先于retry，像素body始终一次；原接受的工作不可重放条件仍未结清。下一修复必须在原mutation/publication/history记录中表达接受事实并前移可失败输出，不增加逐错误的旁路恢复模型。

第一版夹具把已接受的release/晚清理拒绝要求为未接受，并在close前保留history保护，已纠正且原结果保留；第二版parser不识别default-read连字符，保留partial记录。故障probe的terminate/abort handler用实际exit90/91避免宿主crash reporter新增UE，**不证明产品默认abort退出**；最终矩阵没有90/91。全部失败、工具超时、溢出和源码身份保留于[attempt index](attempt-index.json)。

## 全局探针、static和实际外部存储

最终[native arm64](native-06-arm64/identity.json)、[native x86_64](native-06-x86_64/identity.json) 重新编译原freehand源，只重命名main/qExec交到测量入口，原测试方法/真实Qt app/producer/display/策略/历史不改；每架12/0/0、exit0。观测从原资源框架初始化后、测试方法前开始，普通malloc12345B有精确live/free正控制。固定表、symbol缓存、混合指针散列与65536-site索引避免工具分配和长簇扫描；最终均overflow0。

| 指标 | arm64 | x86_64 |
|---|---:|---:|
| 全参与者被观测请求heap峰值 | 98,933,679B | 98,642,358B |
| 可识别paid链峰值 | 6,855,482B | 6,722,034B |
| 合计live节点峰值 | 29,402 | 27,657 |
| 原main结束paid尾 | 672B | 680B |
| static之后paid尾 | 0B | 0B |

总heap包含caller既有Tile/Qt和语言runtime，paid分类是工具识别子集。两者都不是PageStore完整收费峰值；不由总heap大小推硬界违规，也不由paid峰值低推无漏收费。pre-main、框架启动、递归符号服务、malloc实际usable/RSS和非Darwin不在该测量范围。生产硬预算没有放宽。

[边界调用栈](native-boundaries-02-arm64/run.log) 明确实测**PageStore Private、DeferredMetadataCleanupStatistics、Ledger Private、DefaultStorage、RetirementQueue、HistoryCollector/read wake等原owner构造的QWaitCondition私有heap，每个120B**；该存储由PageStore拥有，原sizeof根只含Qt指针，当前未收费。不能将这些块自动归给caller Qt内部例外。下一收敛单元为这些原owner的等待/唤醒与存储寿命；caller Image/Tile/undo和Qt导出仍不重复收费。未验证平台明确开放。

[tail arm64](probe-tail-03-arm64/run.log)、[tail x86_64](probe-tail-03-x86_64/run.log) 观测原cxa注册/实际析构顺序：stop后固定2132/2140B，外部parent释放后732/740B＝固定60＋Resource48＋Executor624/632；实际executor和resource析构分别归还其heap，paid最后为0，进程exit0。静态60B保持到进程映射释放，未调用已析构账本来伪造零费用。真实管线的resource/executor析构顺序可相反，但最后paid同为0。只是已辨认dynamic anchor的最后free资格，不代替所有晚guard/Data/weak/callback的完整分配归属。

原operation allocator sweep每架224实际拒绝/3控制/1暖site未出现，cold/runtime每架17拒绝/3控制；连续COW三拒绝、增长重叠及最后弱引用在同源工具中保持。[诊断探针](probe-diagnostic-03-arm64/run.log) 两架fresh worker关闭路径均不再增加16B。

## 同源结算和未结项

[final-freeze.json](final-freeze.json) 验证115已提交源码、113运行物、四配置、22完整原进程**8088/0/0**和原压力三对**72/0/0**，均exit0。图87TUs/2158APIs/27197edges/25callbacks，21manifest/25ownership/16census/19侵入文件，ratchet未放宽，六工具自测通过。当前[allocation-sites.json](allocation-sites.json) 92文件1693复核位置，加入fixed/TLS；它仍是复核清单，不能作为完整分配覆盖证明。

同源TSAN八目标三组正常通过、五组Qt wait/relock double-lock实际exit66，clean/race正控制0/66。两原metadata并发方法4/0/0无报告，diagnostic方法3/0/0无报告；新增capture方法仍被double-lock截断。全局**Inconclusive**，保留全部报告，不做广泛suppression。七旧UE和旧TSAN控制87052仍未drain；本轮超时工具实际kill exit-9，没有用新正常退出覆盖旧失败。

| 用户八项 | 本批结清程度与剩余 |
|---|---|
| 1分配/free清点 | 补诊断TLS与static识别；新确认owned Qt wait私有块，完整逐笔对账未关闭 |
| 2逐拒绝矩阵 | 原准备224＋冷17每架保留；新增487目标，122同owner接续失败明确保留 |
| 3全局/总峰值 | 原真实业务全heap/node有正控制和无溢出数值；owned/外部分类、全部fee及同时reservation峰值未关闭 |
| 4永久拒绝/恢复 | 已接受checkpoint输出的连续硬满拒绝与恢复关闭；其余seal/commit失败和联合无输入进度未关闭；8MiB准入后取消原合同保持 |
| 5最后引用/退出 | 已辨认executor/resource真正static free关闭；所有持有边界完整归属仍欠 |
| 6框架/平台 | caller边界有实际stack；owned Qt wait缺费须修，nonDarwin缺口保持 |
| 7并发/失败退出 | 当前TSAN仍Inconclusive，八旧UE仍未drain，需宿主复位和默认失败退出复验 |
| 8最终冻结 | 本候选同源冻结关闭；因1–7未结，**整包CP1不通过** |
