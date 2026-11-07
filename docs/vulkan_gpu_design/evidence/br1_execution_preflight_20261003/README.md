# 原 execution 准备复用与 extent 增长修复

本轮当前裁决见[92 §16.63](../../92_br1_m6_m8_execution_baseline.md#execution-preparation-reuse-delivery)。本地产品提交`43799912101df77e6ebae0dc4d5c3622b7f0a6b3`，产品父提交`cd6c8394a6e49b9758176f120efe49a5df02611f`，文档父提交`4a6ecf258c2bd2bb4436051cc20ca285d9b45109`，完整记录见[Git身份](git-round-identity.json)。沿原owner收口§16.62暴露的实际成本/失败；没有读取archive或push，完整CP0/CP1及BR1目标保留。

## 根因与直接替换

| 已观察问题 | 原责任与本轮替换 | 仍有真实来源的路径 |
|---|---|---|
| HistoryMutation的24行pin数为旧期望两倍 | preflight与callback确实各取得guard，并非counter重复fold；prepareWrites仅准备缺失Page，原linked BoundEntry直接复用已有pending backing，删除暖页重复preserve guard/pin/restore | 冷generation仍需一次真实准备pin；callback仍重新pin/按需materialize，不停放像素指针或保证永久resident |
| K257 history ChangedStorage抛bad_alloc | Data::planGrowth只把新增slack留在右边，重复向负坐标扩展每次都翻倍；原Growth现在将slack放在扩展侧，两个轴仍先分配、复验后共同安装 | 真正超范围、实际数组分配拒绝及并发准备复验保持；extent原数组/其他post-commit兼容准备的完整收费/拒绝仍欠CP1 |
| 完整manager继续暴露两条并发generation计数失败 | cursor为两个declared页前置准备，未写第二页在原finishPreparedWrites取消；更新旧计数并新增sealed/cancelled/活动写页归零检查 | packed只准备实际输入，取消后的equal input仍no-op；不减少声明范围、删案例或放宽预算 |

[历史独立复现](history-before.log)24失败/exit24；当时runner将非零返回标为normal_exit=false，该字段仅是早期记录器错误，不表示此进程仍存活。[K257独立复现](changed-before.log)抛异常并留在UE，排除前面测试累积作为必要条件。关闭core文件未解决macOS失败进程退出；原始错误/进程状态保留。

首次[throw调试](throw-backtrace.log)停在Qt后台Security异常，不作为产品根因；[主线程单例](main-throw-backtrace.log)没有复现，保留。修正working-dir语法的[失败](bad-alloc-config-error.log)后，[bad_alloc断点](bad-alloc-backtrace.log)在完整ChangedStorage停住：planGrowth→prepareTileRange→notifyTileAdded→refreshPageStorePages→tryCommit，负坐标-167时触及整数容量检查；debug process在断点处被kill并正常返回。范围很小，拒绝来自增长政策，不靠加预算或捕获异常掩盖。

## 验证及实际成本

[初次manager目标](manager-after-01-arm64-result.json)189/0/0；包含K1/9/65/257、BPP1/4/8/16、standalone/history、四outcome、packed及真实8.5MiB拒绝/同owner重试。新extent案例逐步加入257个负坐标，核对每步extent、实际容量上界、重复计数/逐步移除和再次向正坐标增长。

新CPU swap案例覆盖四BPP：同一version/原reservation在guard返回后真实swap-out；warm prepare诊断实际pin/materialize均0，真实guard各1且字节正确，即使新provider allocation被拒绝仍可消费原pending。首次[探针失败](cpu-new-after-01-arm64.log)误把timer构造当observer边界；现用metrics真实workItems，不改生产诊断。原[错误函数名](cpu-targeted-after-02-arm64.log)启动失败也保留。

[首个完整arm64 manager](manager-final-arm64-result.json)1055/2，正常退出；两条旧并发计数假设随后按上表收口，未混入成功结果。最终[十进程](final-regressions.json)/[总数](final-regression-totals.json)均退出0，合计 **6304/0/0**：每架CPU1319、完整manager1057、Reference762、原Freehand普通/持久/失败/24MiB压力/取消11、Matched普通freehand3。完整manager使用原配置`LIMIT_LONG_TESTS=1`，包括原stress/benchmark，不授予TSAN或无限压力资格。最终十进程串行，未调低压力断言或扩大产品预算。

HistoryMutation的实际pin总数从`4D+2`降为`2D+4`：D=1两者均6；D=10为42→24；D=1000为4002→2004。`2D+1`为实际callback访问，另外3次冷generation准备明确计入；checkpoint后fresh generation、旧capture、commit/abort/undo/redo继续验证。并发cursor多准备一个未写页是前置保证成本，取消与未seal由新断言证明；不隐去真实generation请求。

Matched继续复用双方共享fixture/同一五插件，blank/painted摘要及8segment/4update/原owner释放与§16.62配对结果相同。本轮只作当前普通路径控制；没有独立upstream配对性能、canvas-visible、M/K/E、P95/P99或正式非劣新资格，不能把pin减少换算为上一轮stroke回退已经关闭。

[生产diff](production-incremental.diff)2文件+14/-4净+10；[测试](tests-incremental.diff)3文件+90/-4；[ownership](ownership-incremental.diff)+1/-0；[生成](generated-incremental.diff)+8182/-7858单列，[逐文件成本](source-metrics.json)。主干只有原ExtentManager.cpp+8/-2，沿原字段/Growth/锁安装；上层及低层API、类型、字段、状态、锁/TLS/队列新增0。冷准备收费/失败不变，暖页减少实际工作，extent增长是缺口修复，不能将净增记作等价去重收益。

[架构门](architecture-freeze.log)87TUs/2019APIs/25219edges/21callbacks，21manifest/25ownership/16census/19原侵入文件；[起点](baseline-before.json)与当前ratchet相同。只刷新source checkpoint，不放宽限制。[20份改动/关键consumer源码](source-identity.json)、[107运行物](runtime-identity.json)、[构建](build-identity.json)、[检查器](freeze_evidence.py)及[输出](freeze-final.log)绑定本地产品提交；新源未改shared fixture/input规则。

## 未关闭

[三个旧失败尝试](prior-failed-processes.txt)PID59123（原testui字体启动）、70089（上一轮完整manager）和83020（本轮K257复现）在kill后仍UE；本轮最终十进程正常退出与这些尝试分开，不能声明所有尝试drain。其他历史失败不被覆盖或改判。

本轮有限准备责任交付，完整CP0 required/测量端点、CP1其余wrapper/bootstrap/固定成本/完整永久尾出口、全局allocator/TSAN、公平/原job continuation、M6/M7/M8与BR1-PERF继续按92 §17；默认persistent策略资格仍关闭。extent原数组与其他Qt/控制本体收费并未因此完成，不按净增或通过数扣人日。
