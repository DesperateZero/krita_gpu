# CP1 资格结算尝试：真实 allocator 拒绝、竞态修复与退出缺口

本轮从产品父提交 `b10b2913a69604d42b51cac83ba81214d30d43de` 开始，沿当前 92 §16.72 和原16组合同补实际失败证据。**交付的是修复和有限资格结果；整包 CP1 仍未结清。** 不把1642处词法复核位置、Store子根5448B、有限绿矩阵或识别出的 allocator 子集当作完整覆盖证明。

产品聚焦提交 `a36e1b0ad090fb24e7cd43c22833b6026ab7c14f`，设计文档外层另行本地提交；最终产品身份和源码、依赖、二进制、配置的核对结果见 [final-freeze.json](final-freeze.json)。测试实际绑定 HEAD 加本轮补丁，提交之后再次核对字节身份，不因提交时间不同换用新源码。

## 已修复的真实反例

1. `KisPageMutationExecution::prepareWrites` 的冷虚拟默认页 snapshot COW 实际 malloc 失败，曾逃出原准备回滚。执行对象析构把仍未执行像素的 history owner 标为不可用，同 owner 重试返回 `pixel operation history owner is unavailable`。保留 [probe-01-arm64/run.log](probe-01-arm64/run.log)、[probe-02-arm64/run.log](probe-02-arm64/run.log)。现在准备循环捕获 `std::bad_alloc`，进入原 `finishPreparedWrites` 回滚，返回原 Failed；没有新增业务失败阶段或重放入口。
2. `applyProjectedSequence` 成功安装后解锁，局部 activity 回滚 scope guard 却在返回时访问 `shard->activities`。TSAN 指向该访问与 publication 删除的真实并发冲突，见 [修复前报告](tsan-02/KisPageStoreReferenceTest.log)。现在 `installHeader` 在原 shard gate 内结束这条责任并 dismiss 原 guard。
3. 同函数的 retirement receiver 拒绝分支在解锁后递增 `rejectedTransitions`。现在 callback 后先恢复原 gate，再处理成功或拒绝；新增双线程同时拒绝、原 page 完整保留、无 commit/cancel 和准确计数检查，见 [目标日志](refusal-target-01.log)。

生产只改原 PageStore 两个 cpp；上层生产/API、持久状态、锁、队列、恢复域新增0。测试改原 Reference/Freehand 三文件。实际增删与生成物分列见 [source-metrics.json](source-metrics.json)，不把保证增量说成纯去重或性能收益。

## 冻结的运行范围

最终双架11目标22进程使用 [matrix-03/identity.json](matrix-03/identity.json) 的115生产/测试/tool源码和113运行物，逐次命令、PID、Qt totals 与实际退出见 [results](matrix-03/results.json)；[frozen.json](matrix-03/frozen.json) 要求测试前后哈希不变。原压力六方法三对见 [matrix-pressure-01/results.json](matrix-pressure-01/results.json)，并独立核对身份。manager 的原 LIMIT_LONG_TESTS 配置、Matched 对照、24MiB/swap0 与8MiB/swap0额度未放宽。

8MiB取消原方法保留 queued-input 行，新增 admitted-visible-input 行：原 stroke 未终结时，有限等待3个 producer 已执行、2次可见像素 checkpoint、实际 persistent memento/Store session 和非零 resident；随后基础 tester 取消同笔，检查 cancel已执行、finish零次、无 undo、恢复空像素及 resident 回零。最初 fixture 调用 `image->waitForDone()` 等待尚未结束的自身 stroke，导致挂起；[sample](cancel-fixture-01.sample.txt)保留，该次 SIGKILL 后已实际退出。改为有超时的 producer handshake，不能将错误等待样本算作产品进度资格。

## allocator 探针与测量边界

[heap-interposer.cpp](heap-interposer.cpp) 是本轮 Darwin 审计工具，不是生产 API。dyld 拦截 malloc/calloc/realloc/aligned_alloc/posix_memalign/free，固定指针表记录请求字节、live/peak、节点数和释放；free/realloc 的物理动作及地址复用与表更新同步。测量从 main 内 `auditBegin` 开始，跨线程统计；故障注入仅当前测试线程、仅调用栈能识别的 paid 请求。工具自身固定表、递归符号查询、pre-main、malloc usable size、VM/RSS、Qt/OS/TLS隐藏容量不在该 heap interval 的完整资格内。

[ownership-probe.cpp](ownership-probe.cpp) 对普通 malloc 12345B 有数值正控制，要求 live 精确加12345并在free后回基线。对同一 COW 值连续三次真实拒绝，检查原值、paid费用和 reservation；随后正常重试。原 manager 在1/9/65页工作量中先发现实际调用链，分别拒绝其首末出现，检查像素回调零次、原 default 像素、同 history owner 重试及成功后 commit/purge/close。首次/末次覆盖不等于每次出现全覆盖；暖化消失的 site 单列 `absent_sites`，不会当作拒绝通过。

最终两架 [probe-07-arm64](probe-07-arm64/identity.json)、[probe-07-x86_64](probe-07-x86_64/identity.json) 记录各自命令、audit源码、链接image及产品源码前后哈希；日志包含 heap、process ledger 各桶、reservation、fixed anchor 与最后 weak/free 检查。`LEDGER_TOTAL` 的各桶之和不是独立物理字节证明，`sum_bucket_peaks` 是不同桶峰值之和，不能当同时总峰值。heap peak 是当前有限 manager workload 的总请求峰值，不能代替实际 freehand 全管线总硬界。

| 架构 | operation真实拒绝／成功控制／absent site | 三次连续COW | 有限heap请求峰值／峰值节点 | 识别paid峰值 | stop后fixed ledger |
|---|---:|---:|---:|---:|---:|
| arm64 | 224／3／1 | 通过 | 6,919,307B／3040 | 2,186,875B | 2128B |
| x86_64 | 224／3／1 | 通过 | 6,949,457B／3028 | 2,186,795B | 2136B |

这两行统计在同一probe进程中；冷准备的各16次拒绝单列，不与operation、预算拒绝或QtTest totals合并制造完整覆盖数。最终双架目标 totals为8086/0/0，原压力为72/0/0，28进程均实际exit0。

[cold-probe.cpp](cold-probe.cpp) 经原生产 Store factory、readiness subscription、task/delay/runtime准备逐 ordinal 拒绝；已有 subscription 保留且 notify一次。最终 [arm64](probe-cold-02-arm64/identity.json)、[x86_64](probe-cold-02-x86_64/identity.json)各16次拒绝、3个成功控制、实际exit0，结束 reservation零。singleton在尝试中会暖化，这不是每次重启后的冷 pthread/原生线程全部失败点矩阵。

stop后 ledger 仍保留 fixed anchor；已识别 paid heap 在最后 static report 为零，只证明该识别子集释放。冷探针 stop时已显示 paid零而生产固定anchor仍有费用，直接说明调用栈分类未识别所有固定存储。不得据此给全部anchor最终物理free、无漏收费/重复收费/提前退费或完整静态退出盖章。

## TSAN 与旧失败退出裁决

[tsan-04](tsan-04/runs.json) 在最终源码上跑两个受影响并发方法，4 passed/0 failed/0 skipped、exit0，无报告；clean控制exit0，故意race控制报告并实际exit66。最终完整八目标见 [tsan-05/runs.json](tsan-05/runs.json)及其[二进制/配置身份](tsan-05/identity.json)，全局裁决仍 **Inconclusive**，不从局部无报告推为全局 race-free。

当前 QtCore 6.8.0 未插桩，instrumented inline QMutex 与库内 QWaitCondition wait/relock 的锁观察不闭合。[tsan-qt-control.cpp](tsan-qt-control.cpp)是独立正确同步正例，以相同 Qt 和工具链复现 double-lock，见 [报告](tsan-qt-control.log)、[身份](tsan-qt-control.json)。这支持工具边界裁决，但不能自动忽略所有指向 Qt 的报告；实际 metadata map 竞态已逐行确认并修复。本轮报告退出设置 `abort_on_error=0`，保留66和失败日志，避免把报告退出误写成测试通过。

旧七进程32658/48549/43034/87095/59123/70089/83020均取 sample、核对原命令后发送 SIGKILL，见 [before](failed-processes-before.json)、[attempts](failed-processes-attempts.json)、[after](failed-processes-after.json)。32658的用户栈是旧stop mutex路径；多个进程停在QTest异常重抛/terminate/abort→pthread kill；59123栈在upstream font/SVG resource启动。它们是历史失败触发和当前退出栈，不能推定内核拒绝drain的最终原因。重启用户会话ReportCrash服务成功，见 [日志](reportcrash-restart.log)，仍未释放七进程。首轮TSAN故意race控制使用默认abort又增加87052 UE；该事实也保留，不将新正常退出覆盖旧失败。最终ps状态在 [failed-processes-final.json](failed-processes-final.json)。宿主仍需要环境复位后的失败退出复验；未执行会终止其他应用的主机重启。

## 八项结清登记

| 用户项 | 本轮结果 | 整包仍欠的必要证据 |
|---|---|---|
| 1 完整分配/释放清点 | 原16组合同接入真实运行失败与释放观察 | 全部实际存储的逐owner/capacity/接受/最后free对照；未分类heap与runtime遗漏不能用1642处位置排除 |
| 2 逐拒绝点故障矩阵 | 冷根/订阅/task、COW连续拒绝、原manager多页首末调用链拒绝与同owner恢复；修复实际反例 | capture/read/history/publication/retirement/线程的所有真实失败点、连续拒绝和接受后物理动作边界尚非完整矩阵；absent site未结算 |
| 3 allocator/总峰值 | 数值正控制、有限全heap live/peak/nodes、ledger各桶与weak尾 | 全freehand参与者同时live/reserved/peak、每笔物理收费对账、数组重叠和全部native/TLS容量，整体硬界仍未证明 |
| 4 硬满/永久拒绝/恢复 | 原完整预算/永久provider/无输入drain测试复验；8MiB实际准入后取消已补 | 联合链的真实allocator拒绝矩阵和所有可恢复阻塞无新输入接续仍须完整覆盖 |
| 5 最后引用/退出 | 原晚guard/Data/weak/in-flight/永久stop矩阵复验、识别子集static释放 | 全部fixed anchor物理free、owner各种先退出次序及完整static责任仍欠；旧UE未drain |
| 6 外部/平台 | 请求容量与caller-owned导出、原DataManager/Tile/undo、Qt/OS隐藏容量边界明确 | PageStore实际拥有的外部存储逐项核账仍欠；本机Darwin两架，未验证非Darwin线程及退出 |
| 7 并发/失败退出 | 确认并修复map竞态及解锁计数；正控制/Qt同步控制；取样及服务处置 | 全局TSAN仍Inconclusive；七旧UE加首轮TSAN UE未实际退出，内核/宿主处置后复验未完成 |
| 8 同源冻结 | 当前双架目标/原压力、结构门/工具自测与源码运行物一致，旧失败保留 | 该同源冻结只授上述有限结果；前七项未全闭合，CP1勾选条件不成立 |

原caller自己的Qt输出不重复收费；PageStore持有的外部分配不能仅因使用Qt类型便排除。预算按请求capacity归属，allocator内部和OS隐性容量须另测。关闭的原入口/实现不重领，剩余按此登记回原责任补齐；未授默认策略、M6/M7/M8或正式性能资格。

## 所有尝试保留

完整尝试索引见 [attempt-index.json](attempt-index.json)。probe01/02是实际owner恢复反例；probe03超时、04发现counter工具错误、05超时、06为随后计数修复前源码；不累计为最终候选。首次两次编译错误、未加载venv ninja的127、cancel错误等待、matrix01运行中源码改变导致freeze拒绝、旧TSAN候选及首轮UE、刷新前stale结构门均原样保存。最终只使用03矩阵、pressure01、07双架allocator、cold02双架、TSAN04/05和最终结构/工具结果。
