# CP1：同步 provider 结果直接接受

本包从产品父提交 `b6ad3447acc855bae91aeb15541ddb5c5049c528`、文档父提交 `646ee539b5c37cae2101045dbe4ca024f274cecb` 继续原provider准备→接受责任。产品提交 `a561ca7b0ba920872fd2d8e0420016967a354985` 的37份源码blob、14个运行物和Git身份见 [绑定](git-round-identity.json)、[源码哈希](source-sha256.txt)、[运行物哈希](runtime-sha256.txt)；只提交明确路径，不push。

## 目标形态与删除

先核对原consumer：Store只注册同步provider，transfer bridge也要求同步。原request/adoption/write activity及claim已经持有物理结果直到接受；为这些终态结果增加预备登记节点并无必要。因此采用直接验证，避免新token、结果队列或持久失败阶段。

| 原路径 | 最终归属与删除 |
|---|---|
| consumeTerminalProviderOperation → bind → verify → release | 原owner保留result，Ledger verifyTerminalProviderResult直接检查原operation/provider/epoch及registry终态；删除旧方法和临时收费节点生命周期 |
| Store default/source adoption/native Fresh/initial bytes/generic write及WriteCoordinator transfer | 6个同步点全部迁移，原activity、writer与adoption保护保持。provider物理动作不因登记存储拒绝而需要重放 |
| 无原record的foreign retire → generic登记/查询/释放 | 同步结果直接验证；不制造无owner的operation节点。原已归属retirement record的预付map node、保存结果、terminal取回及retry保持 |
| 两条结果接受各自核对身份 | acceptsProviderResultLocked统一直接验证和显式binding政策。显式binding仍被reference/组合测试消费，保留独立pending登记、计数和释放合同，不是同步生产consumer |
| transfer用返回operation核对返回结果 | 必须核对原request.operation；真实错误ID返回被拒绝，provider只调用一次 |

生产5文件 **+44/-32，净+12**；测试2文件 **+138/-1，净+137**，生成图/基线及ownership3文件另记 **+10641/-9786**，见 [metrics](source-metrics.json) 和实际 [生产差集](production-incremental.diff)、[测试差集](tests-incremental.diff)。净增是直接registry检查和共同身份政策的表达成本，不算纯行数去重；实际删除一次节点分配/释放及登记查询往返。没有新增上层生产/public-protected API、失败状态、调度器或等待机制；未测性能。

## 行为证据与身份

最终同源双架构各CPU1277、Reference660、PhysicalClaim379、ResidentRead221、Foundation28、Freehand压力/取消4，合计 **5138 passed / 0 failed / 0 skipped**。命令、退出码及原始日志见 [accepted结果](accepted-results.json)、[完整汇总](run-accepted.log)；[repaired聚焦](repaired-results.json)仅验证指定边界，不与完整结果累加。

- 固定64KiB额度，先将真实accounting owner和可复用reservation容量计入live，再用实际allocator填满Metadata。旧路径使用的charged insertion确实返回storage refusal；同一allocation/write/transfer物理结果直接验证成功，live不增加、operation计数为0、transfer一次。
- 同一硬满窗口内，无原record的两个foreign handle各retire一次，实际provider payload归零、无operation/queue pin遗留。不是异步foreign结果的责任接受证明。
- initializeFreshReplica实际provider transfer返回错误operation ID：拒绝，调用一次，target沿原清理实际free，没有新增结果重试。
- reference核对错误operation/epoch、另一registry的成功ticket、Pending及三种terminal状态、与已有binding冲突。Pending不留下同步登记，已显式绑定的operation不会被直接验证消费。
- 原退休硬满绑定、自动/close、registered/orphan及Debt释放后无新输入继续回归仍通过。完整Store/ResidentRead/Reference/Freehand覆盖现行同步consumer，但不等于provider内部准备或全部永久退出已验收。

最初 [build-initial](build-initial.log) 缺少测试retireOrDefer的backing实参；[build-repair](build-repair.log)完成链接后，初始硬满夹具未计入controller冷reservation容量，在填充阶段抛出bad_alloc。原始 [CPU失败](focused-cpu-arm64.log) 保留；该runner的异常退出未完成，已终止，不作为同源双架构验收。夹具修复保留固定额度、实际allocator和原断言，最终构建见 [build-fixture](build-fixture.log)。

环境遗留：初始失败子进程PID87095在macOS显示UE，TERM和KILL未清除；采样主线程停在abort→pthread_kill→__pthread_kill，见 [系统退出采样](initial-failure-process-sample.txt)。runner已停止，但不能将子进程写为已退出；修复后的repaired/accepted进程均正常结束。该旧二进制失败进程不计入当前源码验收，没有据此取得永久退出保证。

首次 [architecture-refresh](architecture-refresh.log) 在最终索引完成前启动，报告test source stale，不计资格；最终索引1920 APIs/21119 edges/20 callbacks完成后重新核对并刷新，见 [callgraph-final](callgraph-final.log)、[最终刷新](architecture-refresh-final.log)、[独立结构门](architecture-final.log)。21 manifest/25 ownership/16 census/19上层intrusion文件通过，原manifest阈值不变。普通源码/文档使用显式补丁，Python只编排运行和生成身份/差集。

## 相邻容量与未关闭条件

| 实际剩余端点 | 原权威与失败衔接 |
|---|---|
| Registry Private/control block、sources、terminalRanges/nonSuccess | 原source/ticket决定Pending与terminal，complete已保留失败回滚；实际容量收费、终结前准备及producer在物理动作后如何确认ticket仍欠。不能以结果验证无分配替代生产终结保证 |
| provider allocation/domain journal/admission索引；Ledger core provider/backing/physical索引 | 原provider physical slot和domain revision、原admission/BackingRecord保持权威。核心存储必须在其责任边界收费/准备；拒绝不能重放已发生physical动作 |
| backingDomainChanges → Ledger changes/probes/acknowledged数组 | 原provider journal直到精确revision ack才释放；现行Qt复制/聚合容量未替换，后续必须保留原锁序、revision和拒绝接续，不增加结果队列 |

generic metadata投影、capture辅助存储、tree/deferred及一次性task、close handles/seen/诊断、runtime/clock与完整永久压力最后handle继续CP1。**完整CP1未闭合，M6/M7/M8正式资格0/3、默认关闭。** CP0同依赖upstream、TSAN、公平/原job接续与BR1-PERF没有新增资格。当前排期与下一端点在 [92 §16.39/§17](../../92_br1_m6_m8_execution_baseline.md#synchronous-provider-result-acceptance)、[NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)原位维护。
