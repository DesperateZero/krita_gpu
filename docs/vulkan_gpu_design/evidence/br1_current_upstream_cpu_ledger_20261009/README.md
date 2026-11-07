# 当前/upstream CPU差额对账：任务覆盖与后台终结

本轮将[§16.156](../../92_br1_m6_m8_execution_baseline.md#cpu-residual-ranking)尚未覆盖的8–9ms总CPU推进到**同批业务任务差额及线程归属**。主要缺口已定位：投影任务约3.7–3.8ms额外CPU，绘画任务约2–3ms，原回收/延迟唤醒线程解释此前约1.3ms任务外差额的主体。主线程提交/等待期间CPU很小。这里完成的是责任层对账，尚未证明各项都冗余或已得到合法可删除预算。

产品704d96e81cf29d16191bc3db8785859d79775e27/tree4e7fc164db46c02b968fdd04400b9e4402e289d0，upstream9a24ae0d8c070884fb013594191002e1a1b39a19，文档父a5004b3836c4b08fb76b9adcc1a00f3a0127ad4f。产品/产品测试增删0；只派生观察库、边界fixture和分析。原库SHA256 current `9f138c80f6b9c66223f3411684069f3a082f6a39d5ed58d7bd2c4c0cf92daed6`，upstream `a288ac214124c80c4d3961112c3b4ca8c13ee922e8208a63b204dd597f441908`。

## 1. 同批粗账：差额来自哪些任务

按[事前协议](PROTOCOL.md)完成8能力+64主过程：原库、关闭观察、仅jobs、jobs加完整责任边界四配置，各4个平衡ABBA块、8配对。复用原ARM64、4workers、RGBA8 512、8segments、4callbacks、projection-ready fixture；所有过程19次projection更新。没有加细粒度metadata或逐像素时钟。

下面为**同一个detail配置8对的CPU均值**；每过程先按线程内父子关系做互斥分配，三行差额严格可加。每行是完整业务责任，包含有用计算和维护；额外差额才用于排序。

| 业务责任 | 当前CPU均值 | upstream CPU均值 | 额外CPU均值 | 该批差额份额 |
|---|---:|---:|---:|---:|
| projection merge jobs | 4.236547 ms | 0.539031 ms | **3.697516 ms** | **50.58%** |
| stroke jobs | 10.597545 ms | 8.283157 ms | **2.314388 ms** | **31.66%** |
| job区间之外 | 1.779033 ms | 0.480062 ms | **1.298971 ms** | **17.77%** |
| 总Stroke | 16.613125 ms | 9.302250 ms | **7.310875 ms** | 100% |

仅jobs配置对应额外3.752084/1.961726/1.377064ms，合计7.090875ms，与detail的主要归属一致。两边每过程均937个stroke jobs、19个merge jobs，不能归因为多派发了几倍任务。detail四块projection额外3.552–3.943ms；job外额外1.249–1.330ms，比未拆开的总CPU更稳定。均为描述统计，不授新的95%区间、family或M6资格。

“job区间”包含原run、setDone、doSomeUsefulWork和jobFinished，退出在原解锁后；它不等于纯像素函数。CPU为各线程执行总量，不将累计job wall或wall−CPU叠到前台延迟上。

## 2. 原来未覆盖的8–9ms去了哪里

在**本批同一current detail样本**中，选择上轮的主要观察集合（operation/cold/seal/commit/capture/proj_merge的最外层，不含上轮独立completion细标签），未覆盖均值为8.427025ms。新增job边界将它拆为：

| 新增覆盖/剩余 | 当前CPU均值 | 含义 |
|---|---:|---|
| stroke job内、上述主要scope之外 | **6.573695 ms** | 画笔任务其余工作及原调度/终结；不能全部当额外开销，也不能未经对照全判必要 |
| merge job内、上述主要scope之外 | 0.074297 ms | startMerge以外的原job责任 |
| 仍在job区间外 | **1.779033 ms** | 含其它线程与观察/调度边界；相对upstream多1.298971ms |
| 合计 | 8.427025 ms | 本批同源覆盖桥接，无旧时间相减 |

因此8–9ms不是又发现8–9ms回退；其中大部分是以前没有包围的任务内执行。真正需要追加解释的是约1.3ms的**额外**job外CPU，而不是继续按整个8–9ms寻找管理漏洞。

## 3. 唯一追加：约1.3ms额外job外CPU主要是后台终结

依据原协议允许的一个判别追加，[补充协议](SUPPLEMENT.md)在首批结束后冻结：4能力+32主过程，control与census配置各4平衡块。两者使用同一侧观察库；census fixture仅增加主线程区间与Stroke边界前后各一次Mach线程累计CPU快照。current只在原reclaimer/monitor启动时命名，未改其调度、循环、工作量或锁。代码重建检查证明fixture原有语句及顺序完整保持。

严格事件边界的census账：job_merge额外3.774172ms、job_stroke额外2.063652ms、main_stroke额外−0.006781ms、剩余额外1.340457ms，合计7.171500ms。control合计7.820125ms；差异主要落在stroke jobs，census一个upstream过程CPU17.125ms明显慢于其它过程，全部保留，不能把均值变化当观察带来的优化。

| 线程归属 | 当前CPU均值 | upstream CPU均值 | 证据边界 |
|---|---:|---:|---|
| 原回收worker `BR1-reclaim` | **1.265625 ms**，范围1.182–1.400 | 无该线程 | 原job invoke、dispose、finished及排队循环的完整线程CPU；尚未按任务类型分价 |
| 原deadline/wake monitor `BR1-delay` | **0.175500 ms**，范围0.154–0.217 | 无该线程 | ready wake、delay dispatch、引用/容器释放及调度；不能全部叫空唤醒 |
| job worker线程合计 | 15.518250 ms | 9.745125 ms | 包含job scope内外工作及新线程启动/观察边界 |
| 主线程 | 0.117375 ms | 0.121625 ms | 快照窗口略宽；严格main_stroke事件分别0.086114/0.092896ms |
| TileDataSwapper | 0 | 0.008750 ms | 本批其它可见线程均未取得正CPU差；零只限当前快照分辨率/窗口 |

回收worker和monitor在Stroke开始前已存在；两侧快照间新增的4线程均对应job workers，没有消失线程。主线程start+strategy、输入提交、endStroke和waitForDone CPU均没有约1ms级新增量。故原任务外差额**主要来自原回收与唤醒执行**，不是主线程等待的解释空白；该归属证据强，可删量仍未知。

线程快照不是严格同时端点。current外窗口比Stroke多0.060–0.112ms进程CPU，upstream多0.045–0.088ms。按每个线程实际读数求和，分别比严格Stroke多均值0.055250/0.025500ms；其差仅**0.029750ms**。同一census批的线程差额账为：

```text
job workers       +5.773125 ms
reclaimer         +1.265625 ms
delay/wake        +0.175500 ms
main              -0.004250 ms
swapper           -0.008750 ms
线程累计差额       7.201250 ms
保留的快照/端点差  -0.029750 ms
严格Stroke差额     7.171500 ms
```

这是带明确边界差的对账，不是按偏差修正性能，也不是把后台1.441125ms硬塞进另一批1.298971ms。严格事件账留下的worker/main边界费用、快照窗口和CPU取整仍分别保留。责任层不再有可与首要瓶颈竞争的未知CPU块；函数级任务分摊和真正关键路径仍未完成。

## 4. 对优先级1、2的进一步限定

同一首批detail current内的互斥工作均值如下。这里是当前桶价，不能当作相对upstream超额或全部可删；观察边界比上轮少，数字变小不构成代码性能改善。

| 责任 | 投影内CPU | 绘画job内CPU | 合计 |
|---|---:|---:|---:|
| cold完整准备 | 1.161277 | 0.981634 | **2.142911 ms** |
| private seal | 0.461970 | 0.330856 | **0.792826 ms** |
| canonical commit | 0.494473 | 0.159531 | **0.654004 ms** |
| operation扣除已记录子区间 | 0.402759 | 0.484523 | **0.887282 ms** |
| pixel callback扣除其cold等子区间 | 0.232995 | 2.053171 | **2.286166 ms** |
| capture | 0.359079 | 0.014135 | 0.373214 ms |
| startMerge余项 | 1.049696 | — | 1.049696 ms |

cold+seal+commit合计3.589741ms，说明整条前台生命周期仍是大责任；callback约2.286ms混合kernel与暖访问，尚不支持把原3.3ms operation余项全叫scope/wrapper。投影约3.7ms额外仍是最稳定的大桶，前台准备/发布优先级保留。

新增的后台约1.4ms要求**把原1、2的“发布完成”边界延伸到实际终结与释放**：只减少前台接收、把清理移到另一个线程，可能改善wall却不降低总CPU。下一完整设计应同时核对每个版本/候选/reader的前台表示与后台最终释放、通知次数，而不是另建一套后台owner或直接取消异步回收。

执行审查顺序为：

1. 投影主导的冷准备、private版本和canonical交付，连同原后台cleanup/retirement/通知形成完整责任。
2. 并行纳入同一责任的回收worker/monitor实际消费者，先按原类型/节点/真实释放确定必要次数及重复表示，约1.4ms只给审查规模，不给删除比例。
3. operation真实pixel/暖访问及read/merge余项保留第二梯队；先补其必要工作对照，不能拿混合桶比大小。已清理claim/空锁、旧fill小调用不重领。

## 5. 后台消费者源码索引：已有责任，不是新增待实现矩阵

下表是当前源代码可确认的队列生产者/终点；**本轮只取得线程总CPU，尚未证明每一种任务在该窗口的次数或耗时**。不能把1.265625ms全归给metadata或history，也不因入口存在就宣称观察到该分支。

| 原消费者 | 当前源码入口 | 下一审查的完整边界 |
|---|---|---|
| executor及monitor | `KisPageStoreReclamation.cpp:366 runJobs`、`:414 ensureClockLocked` | invoke之后的dispose/finished与owner保活；ready/delay通知、dispatch及实际回队；保留无输入进度、停机和真实free |
| publication candidate cleanup | `KisPageMetadataCoordinator.cpp:2215`、`:2246 PreparedPublication::Data::invoke` | 原candidate自身作为任务；小量同步、bounded batch、统计/预算与最终dispose。不得将所有异步清理一律改同步或取消公平界 |
| history collection | `KisPageHistoryCollector.cpp:317` | collectionWork/ready/rescan/abandoned触发，原scope/epoch pin、retry及最终引用归还 |
| retirement/last-use | `KisPageRetirementQueue.cpp:467 schedulePassLocked`；`KisPageReadCoordinator.cpp:138 prepareTask` | 真正ready的退休与last-use释放，owner lifetime、预付节点、wake/retry和实际provider终点 |
| epoch释放与budget waiter | `KisImageEpochReferenceModel.cpp:383`；`KisPageWriteCoordinator.cpp:731` | 原epoch release任务与费用等待通知；检查合并/重复唤醒须保留真实有待工作、动态限额和拒绝恢复 |
| 原Store最后owner释放 | `KisPageStore.cpp:3020 PrivateReleaser::cleanup` | 原终态任务移交及Private最终销毁；不在剩余capability存活时提前free |

本包到责任层对账即止，不新增产品缓存/锁/计数器，不执行下一优化。可删除集合、必要成本下界和未插桩因果收益仍由下一完整蓝图证明。

## 6. 观察扰动、置信与全部结果

原库首批CPU差额均值9.512375ms、配对中位7.943ms；其中current过程52为31.813ms，未删。off/jobs/detail均值差额分别7.402625/7.090875/7.310875ms。模式间各块变化有正有负，原库慢值和独立调度使本批不能估一个可靠固定观察单价；不机械扣clock、不把detail变快称收益。投影差额及job外差额在多模式/追加中稳定，绘画任务价格更受慢值影响，给约2–3ms范围而非精确百分比承诺。

总计**108个真实fixture过程、324 QTest passed/0 failed/0 skipped**；全部8 segment/4callback/19 projection updates、像素哈希、undo/redo语义、strategy/image销毁、实际加载库、正常退出/reap通过。所有观察事件CPU/wall父子等式成立，无栈错、overflow、跨stage或活跃尾。79个共享安装依赖哈希一致。观察器关闭/嵌套/异常展开自检通过；没有新安全大矩阵或正式性能资格。

保留两次运行前开发失败：初次capability在协议文档的编辑哈希检查处停止，未启动fixture；编译新增fixture时原/复制stage_probe双include导致重定义，修正为共用原头后构建通过。原失败日志、旧runner/头与编译命令均在原始包；没有丢弃失败样本或重采替换。首次打包包含了仍在写入的freeze-runner日志，后将该派生输出移出输入清单重新打包，旧脚本/清单/元数据保留。复算逐字节检查发现JSON字典键输出顺序不稳定，改为sort_keys后重析同批；旧分析器/输出保留，解析后所有数值相等。测量输入未变。停止规则兑现：一次主批、一次预先冻结的具体追加，之后停止采样。

## 7. 复现、冻结与当前裁决

[analyze.py](analyze.py)/[summary.json](summary.json)复算原64主过程任务账与模式扰动；[analyze_census.py](analyze_census.py)/[census-summary.json](census-summary.json)复算追加32主过程的主线程及线程账。两分析器保留逐过程、块均值、全部慢值和输入哈希，无新CI。原始日志、JSON、源副本/差异、观察库、fixture、命令及失败随[原始包](raw.tar.xz)、[manifest](raw-manifest.json)和[冻结核验](EVIDENCE.json)保存。

原fixture、未变动的实际链接对象及共享依赖复用前包/本地构建，哈希记录在build/runtime identity；本包保留实际运行的派生库与新增fixture，但不另复制所有可重建对象和公共依赖。复算需先解包本目录原始包；重跑用新的输出目录，不能覆盖冻结结果。重建依赖已标识的原compile/link输入，不把未来build目录当作本批二进制。

当前阶段裁决统一见[92 §16.157](../../92_br1_m6_m8_execution_baseline.md#current-upstream-cpu-ledger)：本包完成业务责任和线程层差额对账，默认不晋升、M6/M7/M8 0/3、正式校准2/20、metadata同义驻留分母和完整CP0 required保持开放。未将后台成本转换成收益预测，也未重新领已删除工作。
