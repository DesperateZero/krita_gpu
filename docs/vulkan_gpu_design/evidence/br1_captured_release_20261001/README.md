# CP1：capture 准入与原释放记录生命周期

2026-10-01，产品分支 `refactor/brush-s2-predefined-sanity`。产品父提交 `9a5e24a88901681f2595d0ddaeed3adf3fa99e35`，文档父提交见 [parent-document-commit.txt](parent-document-commit.txt)。活动合同为 [92 §16.36](../../92_br1_m6_m8_execution_baseline.md#captured-release-lifecycle)；完整CP1与M6/M7/M8正式资格未结算，默认关闭。

## 最小完整责任和替换结果

共同目标是 capture→history→retirement 的原记录保债和接受后交接。本批先关闭capture这一有明确准入点的完整生命周期，后续history/operation沿同一目标继续；未把三个owner塞成一套状态机。

| 原实现 | 最终归属和同批删除 |
|---|---|
| sealedPages QHash、析构时复制versions | 原释放节点的一份收费排序版本数组，capture二分查询、销毁和rollback共用；QHash和复制删除 |
| retainSnapshot后才创建Private/释放记录、claim后插入QHash | 身体/节点先准备，版本容量门外准备后重新选择root/delta；所有delta容器在保护前填好，只记录已取得保护前缀 |
| PendingCapturedRelease/deque、重试先pop、failed/released数组 | 同一unique node转intrusive重试链，原read owner一处finish保存已完成事实；原容器与两份阶段序列删除 |
| 只能等新release/close推进captured失败 | 原read task/预付Delay接续，close drain/rearm，stop冻结派发；没有新executor/通知框架 |
| legacy releaseSnapshotLocked仍保留capturedScope分支 | 只服务legacy retained snapshot，capture计数/事实回到原节点，无consumer的参数和分支删除 |
| metadata putBatch后才分配retained集合 | 原投影准备前移；capture token变化后没有该后置集合分配窗口 |

metadata ReleaseCapturedVersion成功后记住versionReleased，history接受精确key后才推进原cursor；snapshot成功后记住snapshotReleased和未完成history通知，不重放token。原节点始终挂接直到接受，必要数据不在可失败交接前移走。实际节点和vector allocator请求capacity计入MetadataArena，锁外free后才归还原lifetime pin。纯销毁不增加restore语义忙条件；未交接记录由close内部snapshot检查阻止误关。

[生产差异](production-incremental.diff)为4文件 **+250/-133，净+117**；[测试差异](tests-incremental.diff)为1文件 **+91/-1，净+90**。派生调用图/checkpoint和ownership分开计入 [source-metrics.json](source-metrics.json)，不把生成物算作人工生产行数。增长用于前移准入、收费和已完成事实接续，是新增保证成本；没有宣称等价重构使总源码下降。上层tool/strokes/Painter/PaintDevice/scheduler生产改动与public/protected API净增0。内部prepare/deleter导出及两项原方法测试可见性见 [API账本](../../br1_modification_guide/API_CONVERGENCE_MAP.md#captured-release-api-delivery)。

## 同源验证

[build-final.log](build-final.log)后的双架构最终结果：

| 目标 | arm64 | x86_64 |
|---|---:|---:|
| KisPageStoreCpuMutationTest全组 | 1266/0/0 | 1266/0/0 |
| KisPageStoreReferenceTest全组 | 659/0/0 | 659/0/0 |
| KisPageStorePhysicalClaimTest全组 | 379/0/0 | 379/0/0 |
| FreehandStrokeTest原persistent pressure/cancel两个方法 | 4/0/0 | 4/0/0 |

合计 **4616 passed / 0 failed / 0 skipped**，含init/cleanup。实际argv/exit/用时见 [results.json](results.json)、[run-qualified.log](run-qualified.log)及八份对应日志。[runner](run_results.py)固定 `_build-br0-cpu/bin`、同目录插件、原 `_install` prefix、offscreen和seed12345。受影响目标两架构各33/0/0在 [focused-results.json](focused-results.json)，最后只清理无人使用的legacy内部参数/分支，再执行上述同源全组；不将focused或中间通过累加到最终数量。

4个新增行中，3个原owner组合行在64KiB实际allocator恰满时保留同一capture释放节点；metadata token已移除而snapshot仍未接受，至少三次原task retry，恢复原owner状态后无新输入完成，确认不重复ReleaseCapturedVersion、只计一次snapshot release、实际节点/数组退费和pin归还。覆盖普通继续、begin/cancel-close和stop后手动drain；stop行不记自主恢复。这个组合夹具以原公开metadata注册构建有capture保护的初态，没有改private字段或放宽budget冻结合同；为模拟原close/恢复时序控制组合owner的operational状态，不是实际metadata分配拒绝注入。

另一行使用真实Store，构造前固定128KiB额度，保留capture直到原节点storage拒绝；拒绝没有新增snapshot保护，释放一个handle后再次capture成功，全部退出的费用回到实际起点、close通过。既有overlay commit/abort/removal、晚facade/guard、long/multi-page/root revalidation和持续capture并发publication/restore目标重新通过。真实history物理退休由这些既有目标覆盖，不据此宣称恰满时整条history/provider链已合格。

## 保留的失败及修复

首次统一验证两架构CPU各1265 passed/1 failed，原 `publicationWhileCapturedReadersChange` 的restore返回无效。新纯节点销毁错误地增加activeProviderCalls，而原restore idle禁止该计数非零；移除该语义阻塞，继续由原lifetime pin覆盖实际free。原失败日志/八目标结果见 [restore-blocking-failure](restore-blocking-failure/results.json)，原测试断言未放宽。[build-initial.log](build-initial.log)记录未找到shell PATH中的cmake，随后使用该build CMakeCache指定的bundled cmake；这不是产品编译失败。

## 审计与提交边界

[最终调用图](callgraph-qualified.log)为87 TUs / 1910 APIs / 20813 edges / 20 callbacks。[正常结构门](architecture.log)通过21 manifest / 25 ownership / 16 census / 19既有侵入文件，manifest未改。首次门只报5份源码checkpoint失配；原owner审查和图重建后刷新 [前](baseline-before.json)/[后](baseline-after.json)，最终再次独立运行正常门，没有放宽侵入或布局上限。

[source-sha256.txt](source-sha256.txt)冻结33份源码/测试/审计文件，[runtime-sha256.txt](runtime-sha256.txt)冻结4个目标及8份库/插件，Mach-O加载配置见 [runtime-rpaths.txt](runtime-rpaths.txt)。[freeze_evidence.py](freeze_evidence.py)只读实现和指导文档，写派生diff/哈希/身份。最终产品commit见 [code-commit.txt](code-commit.txt)及 [Git身份](git-round-identity.json)，父固定上述提交；文档仓单独提交活动文档、本证据及Gitlink，原其他未跟踪文件不混入，无push。普通源码/测试/指导文档和本目录脚本使用显式patch。

产品提交 **`8a5b92ef8dfd1e43ea84488cf7303653febd8465`** 已完成，33份源码blob和12份runtime身份相同，tracked产品树清空。[文档验证](document-validation.json)检查活动链接、身份、目标结果、删除项和35–59人日剩余排期求和；归档不参与当前判断。

普通产品/指导文档/脚本及其余证据空白检查通过。外层格式检查仅排除两份原始unified diff `production-incremental.diff` 和 `tests-incremental.diff` 的上下文空行，不改写原始diff或测试失败日志。

## 同一CP1仍欠

history pending/queued/deferred/ready/scans、每scan candidates和pass keys/effects、metadata snapshots及detach后的效果接受；退休operation/core及ledger/provider/registry索引；capture Private/Qt控制块、removed/staged/default存储；tree/deferred和一次性任务；close handles/seen/诊断、控制本体/runtime/clock固定成本及永久拒绝后完整退出。foreground history内部bad_alloc效果保债、provider已发生副作用后的登记、全部硬满自主drain、完整CP0同依赖对照、TSAN、公平/原job接续和BR1-PERF没有由本批证明。

按 [NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)沿同一接受目标继续history工作记录与operation登记前置，不重做capture包装。CP1剩余工时在92 §17.2按实际端点重估，实际工程人日无记录，不能从轮数推算；完整CP1与M6–M8继续未勾选。
