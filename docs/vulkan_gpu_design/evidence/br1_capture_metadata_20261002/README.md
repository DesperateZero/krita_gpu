# BR1 exact 查询与 capture 原记录（2026-10-02）

产品父提交`e3d6161b99a9c668f3d9aee5502741d562e74ce7`、文档父提交`243c9711694e870c78b1cfc6891ad54ec9c4d49e`。有限责任为exact查询与capture准备→保护→查询→释放；[源码身份](source-sha256.txt)、[运行物身份](runtime-sha256.txt)、[构建依赖](build-environment.json)和[Git身份](git-round-identity.json)绑定最终结果。普通源码/测试/活动文档用显式apply_patch，脚本仅编排或生成证据，本地聚焦提交、不push。

生产exact消费者只读原record的scalar VersionInfo；generic read用原budget的最小候选数组，Store/shard gate外准备后重选完整cut。native CPU discovery借原slot，Prepared仍需captured保护。projectVersionPair只余mutationBase消费者，原body归mutationBaseSnapshot，包装/count开关删除；通用mutation/publication的Qt投影仍真实可达。

capture从原PreparedTransactionState直接填同release记录的paid versions/removals/surfaces，准备容量后重选cut、再retain；旧capture Qt delta导出和Private QSet/QHash删除。Private/control实际allocate_shared接原retained allocator；default map节点先于buffer准备，成员/root/default销毁后归还最后Store引用，真实控制块继续收费到free。singleton retain/release直接操作原overflow链，release将空block/charge归同record cleanup，原gate-free dispose才归费。history/key/epoch实际拒绝所需已完成事实仍留同记录，无新增恢复队列。

生产10文件 **+363/-147，净+216**，测试2文件 **+137/-10，净+127**；生成审计独立见[统计](source-metrics.json)。[生产diff](production-incremental.diff)与[测试diff](tests_and_model-incremental.diff)包含完整跨文件差集。增长支付scope/control/aux收费、锁外准备和原slot生命周期保证，不宣称纯去重或性能收益；没有上层生产/API增长，一个test friend只用于原private shared-budget配置。raw diff的Git空context及原失败build命令行空格保留，whitespace检查排除原始证据。

一个universal build writer，最终[构建](build-query-window-fix.log)退出0，再运行[脚本](run_results.py)，offscreen、seed12345、原prefix/plugin，禁core及Qt crash handler。实际命令和退出码见[最终结果](qualified-results.json)。

| suite | arm64 | x86_64 |
|---|---:|---:|
| CompletionRegistry | 87 / 0 / 0 | 87 / 0 / 0 |
| CPU mutation | 1297 / 0 / 0 | 1297 / 0 / 0 |
| Reference | 661 / 0 / 0 | 661 / 0 / 0 |
| PhysicalClaim | 381 / 0 / 0 | 381 / 0 / 0 |
| ResidentRead | 221 / 0 / 0 | 221 / 0 / 0 |
| Foundation | 28 / 0 / 0 | 28 / 0 / 0 |
| Freehand压力/取消两个方法 | 4 / 0 / 0 | 4 / 0 / 0 |

合计 **5358 passed / 0 failed / 0 skipped**，含init/cleanup，14进程正常退出。Reference新增真实MetadataArena-full行：overflow无空slot时retain被拒绝、原记录不变；scalar/native仍可查询、paid候选准备拒绝不改输出；hard-full旧token全部释放，detached block未free前仍收费，cleanup实际free后归费。四线程1600转换记录不变，投影input/install为0。CPU新增shared-parent行：实际default map/capture容量拒绝不增保护，冻结removed/default cut不随后来surface更新变化，abort/facade销毁/晚guard后最终返回原parent预热cache基线。原capture/read/history/close/manual、default cache跨70revision eviction、真实brush压力/取消等回归保留。

失败样本保留：初次生产构建复用了错误snapshot类型，后续修正surface identity比较/C++17 lambda、测试误用字段和private预算访问，均仅为编译失败，见各build日志。初次[目标结果](focused-results.json)新行为通过、Reference并发旧成本断言失败（要求1600投影input）；改为0 input/0 install并保留原结果/oracle断言。中间[完整矩阵](pre-query-window-qualified-results.json)为5357/1/0，x86_64取消写后default read空结果暴露每次查询都unlock的回归，修为容量不足才准备、第一candidate先于default materialization准备，容量齐全后查询/准入保留原owner gate；该中间[源码](pre-query-window-source-sha256.txt)/[运行物](pre-query-window-runtime-sha256.txt)身份冻结。只有最终结果取得当前源码资格，各轮不累加。

初次callgraph在build/MOC写入期间失败，日志保留；最终图在完成构建后生成，见[最终日志](callgraph-final.log)，87 TUs、1957 APIs、21845 edges、21 callbacks。初次[结构门](architecture-stale.log)仅报告12个source checkpoint过时，核对后门限不变[刷新](architecture-refresh.log)，再[独立检查](architecture-final.log)。[baseline before](baseline-before.json)/[after](baseline-after.json)保留。[18项替代检查](deletion-checks.json)与[脚本](check_deletions.py)核对旧副本/包装退出、准备顺序、原记录/收费寿命及合法剩余consumer；静态检查不替代实际压力与生命周期行为。

generic applyProjectedSequence、mutationBase/preparePublication与overlay真实Qt容量、其他Qt wrapper/bootstrap、TileDataStore登记、tree/deferred/task、close诊断及Store/provider/Ledger/runtime固定成本仍欠。mixed sequence/oracle保留StateMachine，history/key/epoch真实拒绝保留versionReleased/snapshotReleased/next。proof及其他准备拒绝使native seal/generic finishWrite的Failed/cancel仍有真实consumer；CP5自动job接续未新增。旧失败native PID43034/87095仍UE/parent1，完整永久尾退出未取得资格；没有全局allocator、TSAN、公平、CP0同依赖upstream或性能结论。

当前裁决见[92 §16.47](../../92_br1_m6_m8_execution_baseline.md#capture-metadata-delivery)，[代码](../../br1_modification_guide/CODE_INDEX.md#capture-metadata-code-index)与[API](../../br1_modification_guide/API_CONVERGENCE_MAP.md#capture-metadata-api-delivery)同步。有限端点完成，完整BR1继续、**CP1开放、M6/M7/M8正式资格0/3、默认关闭**。
