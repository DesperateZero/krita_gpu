# BR1 旧协议残余清理与退出审计（2026-10-02）

本轮从产品父提交`643965d644e6ed13d0437b2289b8abad0161ce05`、文档父提交`3a8f843e0d82bb34b8bfd25cc60e9febeea437b0`继续。[Git身份](git-round-identity.json)对应46份[源码blob](source-sha256.txt)、15份[运行物](runtime-sha256.txt)和5份[构建/依赖身份](build-environment.json)。普通源码、测试和活动文档均用显式apply_patch，Python仅分析、编排和生成证据；本地两仓库聚焦提交，不push。

本轮关闭Read空effects协议、retirement后台许可第二事实与retry capabilities重查、batch effects缺Debt补准入/缺record静默跳过、两个无consumer公开查询及extent私有实现。batch/History以一个私有takeEffectRecord消费已提交Debt及原record；原批量/前台/History调度和activeProviderCalls窗口保留。registered复用登记许可，orphan准入固定一次。当前extent联合准备、底层contentExtentAfterDelta、manager预备scratch及真实generic effects/Pending继续消费原职责，没有新增持久阶段、队列或业务保证。

生产14文件 **+38/-117，净-79**；测试1文件 **+6/-0**；生成审计/ownership3文件 **+4665/-4892**单列。上层生产/API净增0。完整差集见[生产](production-incremental.diff)、[测试](tests_and_model-incremental.diff)、[统计](source-metrics.json)，没有靠压行或删除说明取得净减行。原始diff中的空context行属于Git格式，保存原字节；外层文档whitespace检查仅排除这两份raw diff，产品diff单独完整检查。

一次universal build writer；[初始构建](build.log)、[废弃入口删除后构建](build-final.log)和[效果政策最终构建](build-effects-policy.log)依次完成。最终构建退出0后才运行[脚本](run_results.py)，实际命令在[结果](qualified-results.json)；环境offscreen、seed12345、原prefix/plugin路径，禁core及Qt crash handler。各架构最终结果：

| suite | arm64 | x86_64 |
|---|---:|---:|
| CompletionRegistry | 87 / 0 / 0 | 87 / 0 / 0 |
| CPU mutation | 1295 / 0 / 0 | 1295 / 0 / 0 |
| Reference | 660 / 0 / 0 | 660 / 0 / 0 |
| PhysicalClaim | 381 / 0 / 0 | 381 / 0 / 0 |
| ResidentRead | 221 / 0 / 0 | 221 / 0 / 0 |
| Foundation | 28 / 0 / 0 | 28 / 0 / 0 |
| Freehand压力/取消两个方法 | 4 / 0 / 0 | 4 / 0 / 0 |

合计 **5352 passed / 0 failed / 0 skipped**，包含init/cleanup，14进程正常退出。现有retirementRecordTransfersAtCapacity增加查询计数及3处断言、合计6行，至少3次自主retry及最终free验证registered0次、orphan1次；真实费用/额度/close/manual断言不变，无新增数据行。实际generic取消/abort/seal/publication和History/原Pending全组回归，同时保留manual read pump、capture/close、Fresh及真实brush压力/取消。

最终effects接受政策形成前的[14进程中间结果](pre-effects-policy-qualified-results.json)也为5352/0/0，日志和[对应运行物](pre-effects-policy-runtime-sha256.txt)单独保留，不与最终通过数累加，不授予最终源码资格。callgraph-pre-effects-policy.log同样仅记录中间索引；最终资格只使用callgraph-final.log和当前reverse-callgraph.json。

[19项删除检查](deletion-checks.json)通过。[退出审计](residue-audit.json)覆盖当前BR1 producer/Ledger/metadata/read/capture/history/queue/close及实际publication/adapter消费者，不读archive。最终图29个非operator/特殊成员零入边候选逐项核对：模板/ADL、Qt shutdown callback和图外Vulkan真实consumer保留；Foundation/fail-closed后续接口及纯值访问器没有旧协议替代依据。6组剩余实际协议分别列consumer、失败来源和删除条件。在该责任闭包内未发现已具删除条件却未处理的旧协议，本次持续清理目标完成；这一结论不等于全仓库无unused代码或完整CP1通过。

初次结构门只报告15份源码checkpoint过时，见[原日志](architecture-stale.log)。核对后在阈值不变下更新原baseline，再独立[最终检查](architecture-final.log)：21 manifest、25 ownership、16 census、19 intrusion，最终图1941 APIs/21625 edges/20 callbacks；[生成](callgraph-final.log)、[刷新](architecture-refresh.log)和before/after baseline保留。

既有失败native PID43034/87095本轮复核仍为UE/parent1；本轮没有新增native崩溃。完整永久尾退出、全局allocator、TSAN和性能资格未取得。当前裁决及保留条件只在[92 §16.45](../../92_br1_m6_m8_execution_baseline.md#protocol-residue-delivery)维护，函数/API索引同步更新；完整CP1开放、M6/M7/M8正式资格0/3、默认关闭，下一provider/pending登记、route cut及proof接纳/撤销不变。
