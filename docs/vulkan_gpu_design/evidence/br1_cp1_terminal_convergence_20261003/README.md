# CP1 停止接受、原尾释放与并发残留集中收口

产品提交 **`406bacb448997a2b63bf2d452a0a71d90587abdd`**；起点为产品 `0da7ba08899344496b3528e60cb98696f5007f07`、文档 `07650746`。工作区已有 TileData `tryRef`/atomic age 和四 bpp 终结测试候选，本轮先保存 [原增量](inherited.patch)，审查后纳入同一终结责任；不将其写成本轮从空工作区独立发明的改动。所有新失败与中间运行保留，最终资格以[提交blob/源码/运行物冻结](final-freeze.json)为准。

## 原责任、接受点和同批删除

| 原实现 / 故障 | 本轮最终归属 | 同批回收 |
|---|---|---|
| void enqueue 在 worker 停止后仍接晚 job，history idle 永不结束 | 原 executor gate 决定是否接受。停止后新 producer 保留原节点；已接受 worker continuation 排空 | 以 debug assert 代替实际拒绝、晚队列插入 |
| history/read/retirement/waiter 先记 scheduled/pin/activity 后假定已接受 | 原 caller 在拒绝时撤回本次临时记账，未完成业务仍留原记录；retirement idle 与原 notification gate 共读接受事实 | 无 executor 责任却保留的 scheduled/activity/pin |
| facade 最后引用、tree 和 publication Data 在 stop 后仍转交退出的 worker | 原 terminal task 移交成功才释放；拒绝则原 owner 销毁。tree 沿原非递归 list，Data 沿原 clearBatch 完成实际 free | terminal 先 release 后盲排；晚 tree/Data 自保活循环 |
| Swapper/map 使用允许零到一的 ref，final free 与复活 pin 同时拥有同一地址 | iterator barrier 保护地址，tryRef 只增加正计数；原 final free 独占零计数 | map traversal 的零计数复活；age 以原 body 内 atomic 读写 |
| proof 拒绝后测试误把 idle 当作 Debt drain | 原 one-page Debt 释放后，观察者再调用原 abort；真实预算拒绝保持 | 对未来 retry 尚未发生时必须 abort 成功的错误前提 |
| pooler testingRereadConfig 与 worker 并发读 limit | 原 m_memoryLimit 改 atomic relaxed 读写，配置语义和限额不变 | 对同一配置标量的无同步读取 |

未增加 owner、恢复队列、锁、callback 或业务失败阶段。private enqueue 返回接受事实，全部生产 consumer 同批迁移。tree 停止后同步释放单独记录 foreground；四个真实静态 tree 统计 atomic 共 32B 纳入原 process 固定费用，其中 8B 是本次新增统计，其余 24B 为原存储补齐。同步 final free 可以在退出 caller 上遍历全部原节点，不能冒称交互线程有界销毁；正常 worker 仍按原每 pass 128 个节点执行。

## 已定位的失败及保留样本

- [abort TSAN 原反例](abort-tsan-01/results.json)和[带拒绝原因及实际 Debt 的复现](abort-diagnostic-03/results.json)：最后 abort 的拒绝为 hard budget，Debt live=16384B、reserved=0、pending=1。idle 不等待未来重试；没有削减原硬限、将真实拒绝改成断言或自动重放。
- 原停止后晚 close 死等见 §16.79 旧 probe；本轮双架 [stop-04](stop-04/results.json)在原 process 恰满、四 bpp × facade 保留/先销毁下，晚 capture/read 保留 0x31，释放后无 ghost scheduled，provider 连续三次拒绝后原 close 可恢复。所有 participant storage 与原 parent 引用归还，parent 自身暖 high-water capacity 保持原收费。
- stop-01 错误要求外部 provider 尚存时全部 bytes 为零；stop-02 错误要求活 parent 的自身 slot capacity 为零；stop-03 使用不支持的嵌套 shared budget。修正 fixture 的所有权断言后仍验证完整父账本回到准备前基线，不放宽生产额度。build-04 的 fixture 参数/变量错误保留。
- [manager TSAN](manager-tsan-final/results.json)通过原 Swapper 失败位置后，在现行 Qt extent 读写锁边界报告 race/exit66。独立预算方法另报告 pooler 配置标量与 worker 读取竞态，见 [原新反例](swapper-tsan-final/results.json)；原 body atomic 修复后，[10 个预算场景 TSAN 进程](swapper-tsan-pooler/results.json) **60/0/0**、全部 exit0、无报告。[最终 manager](manager-tsan-qualified/results.json)再次通过原故障位置，停在 `Data::add ↔ updateExtent` 原 Qt extent 锁边界，实际66且已reap，不作整体并发通过。
- native-final 使用较旧 mixed 表，两架 overflow 非零，测量资格拒绝；native-wide 复用原 wide 工具重测。二者原日志完整保留。abort-tsan-02 的 20 进程通过后，源码注释编辑令最终 hash 校验失败；不作为同源冻结资格，最终运行重新绑定。

## 成本和最终冻结范围

相对产品起点的累计包：生产15文件 **+143/-67，净+76**，测试两文件 **+106/-0**，生成两JSON **+5773/-5360**。其中起点已有生产4文件+19/-7、PhysicalClaim测试+40/-0及旧图替换；本轮新增修改为生产11文件+124/-60、CPU测试+66/-0，继承候选明确纳入审阅。见 [实际清点与原增量](product-review.json)、[最终完整diff](product-final.patch)。保证增量、原静态漏费补齐和同步最终遍历成本不能记纯去重。

最终构建两架普通image及arm64 TSAN，原87 TU调用图及结构门复验；2164 APIs/27454 edges/27 callbacks，21 manifest/25 ownership/16 census/19 intrusion，原ratchet完全相同。六工具自测见gate-1；生成代码和测试身份由 [冻结脚本](freeze.py)核对提交blob、最终 **123输入并集/245运行物（含配置）**。各最终run保留开始前与结束后哈希，不将先前通过拼成最终同源资格。

| 最终同源范围 | 实际结果 |
|---|---|
| [双架构22进程完整矩阵](matrix-qualified/results.json) | **8244/0/0**，所有actual exit0 |
| [原六freehand方法三对压力](pressure-qualified/results.json) | **72/0/0**，六actual exit0，原预算保持 |
| [七PageStore TSAN目标](concurrency-qualified/results.json) | **2922/0/0**，全部actual exit0，无TSAN报告 |
| [原DataManager预算方法×10](swapper-tsan-pooler/results.json) | **60/0/0**，十actual exit0，无TSAN报告 |
| [完整DataManager TSAN](manager-tsan-qualified/results.json) | actual66、已reap；Qt extent边界 **Inconclusive**，不计通过 |
| [TSAN正反控制](control-runs.json) | 构建0、clean0、真实race66；halt_on_error保留，无suppression |

原native六方法每架 **12/0/0**、actual exit0、malloc12345B live/free正控制及overflow0。requested heap peak **98,667,099 / 98,771,600B**，paid栈识别子集 peak **6,552,674 / 6,774,834B**，节点peak **27,193 / 28,865**；after-main paid **672 / 680B**，after-static paid **0 / 0B**，实际fixed存储 **764 / 772B**仍正确归属。节点和caller/Qt/Tile尾保持原日志，不冒称owned总账/硬界或全部进程零尾。native builder原116输入之外的TileData/pooler头及audit由最终并集补绑，复用脚本与原wide工具hash均保留。

## 完整 CP1 剩余的有限工作组

| 工作组 | 必须结清的实际责任和出口 |
|---|---|
| 完整 owned 账本和硬界 | 每个 owner 的实际 request/capacity/control/native/TLS/static 与接受、reserved、同时 live/peak、最后 physical free 一一对应；caller heap 和 paid 栈子集不能代替总 owned 账本。保留旧/新数组、weak 尾和 OS mapping 重叠。 |
| 其余实际拒绝族与联合终结 | 原 Ledger `registerProvider/prepareLedgerNode`、provider observer/alias、metadata node/control、`kisPreparePageStoreReclamation/ReclamationThread::start`实际 allocator 拒绝；read/capture/history/publication/retirement/close 联合阻塞、晚 fence/caller transaction 与 facade 先退出组合。原 487 生命周期、702 clear 等冻结证据不外推为所有分配点。接受前拒绝保原输入/claim，接受后不重放，解除后同owner释放全部reservation/physical资源才结算。 |
| 平台及框架边界 | 明确自持与 caller 持有的 Qt/OS/usable/TLS；非 Darwin 线程创建、收费和退出尚无运行平台证据。已收费 CPU 对象不重新领取实现。 |
| 并发与默认失败退出 | 同源 TSAN 的 Qt extent 观测边界与十个旧 UE；[最终数值PID复查](old-ue-qualified.json)仍未退出，原raw捕获包含的ps/rg包装行单列排除。新 exit0 不能覆盖它们。原 app-server/宿主未处置；须解决观测边界并在宿主可正常reap后复验默认失败退出。 |

完整 CP1 不勾选；M6/M7/M8 正式 0/3，persistent 默认关闭。原 job 自动接续/持续公平归 CP5、正式性能归 CP10，不重新塞入本包。当前权威状态和下一领取最终原位更新到 92 §16.80 / §17。
