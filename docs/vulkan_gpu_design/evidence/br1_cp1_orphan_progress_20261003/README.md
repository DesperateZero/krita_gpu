# CP1 原 orphan scope 无输入清理与失败结算

本轮以产品 `71c8b27e08517408102ee03a367338543f3a1225` 为修改前基线；最终产品提交、116 个源码、113 个运行物及四配置由 [final-freeze.json](final-freeze.json) 绑定。普通绘画存在真实像素失败，完整 CP1 不通过；M6/M7/M8 正式仍为 0/3，persistent 默认关闭。

## 已修复的实际反例与原责任

[修改前反例](target-before-02/arm64.log)在同一个真实 Store 上构造两条原 scope、四页私有写入及一页 RetirementDebt 硬限。provider 持续拒绝后解除拒绝，三页仍留在 orphan 链；实际 shared MetadataArena 恰满后释放容量，四页仍留在链。两个 QTRY 均失败，进程实际 exit 2，失败清理完成。只调用显式 process/abort 的旧 fixture 不证明自主恢复。

现在原 `retainOrphanLocked` 接到现有 history collector 的冷准备 task/delay。collector 在 owner gate 内只查询原链是否有工作，在锁外调用原 `retryOrphans → cancelLocked`；未取消页、proof、claim 与 Store lifetime pin 仍在原 scope。拒绝后原 delay 按现有 1–100ms 政策再试，实际取消接受才销毁原 scope。显式 abort/close 与后台共用同一终结流程，前台权限、close 冻结与永久 stop latch 保留。没有新增恢复 owner、队列、持久阶段、task、timer 或上层生产 API；两项内部 callback 函数指针增加 16B，由原 Private 的实际 sizeof 收费。生产三文件 **+46/-7，净 +39**；测试一文件 **+89/-0**；两个 audit JSON **+8,503/-7,928**单列。这是进度保证增量，不能称纯去重或性能收益。

[最终目标](target-after-02/results.json)为每架 26/0/0、实际 exit 0，其中新增 16 行：四种 bpp × active/frozen scope × provider/arena 拒绝。解除拒绝后的观察窗口只有 stats、memoryUsage 和等待，不调用 process、abort、close 或新 mutation。最终四页取消、原 claim/proof 归零、物理退休恰接受四次、Debt/live 与 MetadataArena/reserved 为零；旧 capture 和 current 保留 0x31。原 caller 的两条 transaction 在观察后才显式 abort，本证据不声称这些 transaction 自动终结。早期八行目标通过对应较早 fixture，作为中间轮保留。

## 同源验证与必须保留的失败

- 双架原 11 组矩阵保留一个 x86 MatchedFreehand 像素失败；失败后停止派发，再只运行未覆盖的五个原目标，原失败行不替换。完整 22 行的实际结果见 [矩阵](matrix-01/results.json)，不能记为全绿。
- [原压力三对](matrix-pressure-01/results.json)六进程 72/0/0，实际 exit 0；原 8MiB 准入、producer、像素和准入后取消边界保持。
- [生命周期矩阵](lifecycle-matrix-01/results.json)505 进程＝18 控制＋487 实际首末拒绝，全部 exit 0；456 接受前拒绝重试、31 接受后保留结果的清理拒绝，threw/reserved 均零。无用新绿表抹去旧失败。
- 每架 operation 224 实拒＋3 正控制，暖父增长 site 缺席 1 项保留；[冷首次 operation](cold-operation-matrix-01/results.json)88 新进程＝86 实拒＋2 控制全部 exit 0，ordinal 11 实际父 reservation 数组增长再次命中。冷 Store/订阅/runtime 每架 17 实拒＋3 控制。
- 结构门为 87TUs/2164APIs/27370edges/27callbacks，21 manifest/25 ownership/16 census/19 外部侵入文件，ratchet 与父提交相同；六项工具自测通过。[93 文件 1715 词法复核位置](allocation-sites.json)仍不是完整分配覆盖证明。
- [TSAN](tsan-01/runs.json)七目标 2918/0/0，无报告，均实际 exit 0；原 clean/race 控制 0/66。DataManager 在同一 `KisTiledExtentManager.cpp:222` Qt 读写锁边界报告 race、实际 exit 66。未修改 extent 锁或加广泛 suppression，完整 TSAN 仍 **Inconclusive**，后续 case 被截断。

原 MatchedFreehand 的 projection/layer 摘要不同，并报告 `legacy mutation conflicts with an active page writer`，见 [首次矩阵失败](matrix-01/MatchedFreehandBaselineTest-x86_64.log)。[同源短复验](matched-recheck-01/results.json)十进程 30/0/0不能关闭该失败。[隔离父版本](parent-image-01/identity.json)机械提取父提交的两条 owner TU 及其 private header，按原编译参数重编译、复用 373 个未改 image 对象并链接独立 image；不改当前源码或二进制，仅供本批差异裁决。[实际加载验证配对](matched-pair-02/results.json)24 进程中，父版本一例、候选两例均复现相同 claim 冲突和像素摘要失败，均实际 exit 1、已 reaped。父 image 的加载路径与哈希均核验。该普通绘画缺陷在本批之前已经存在，**仍未修复**；不是新进度保证的全面兼容资格。

最初 loader 控制通过 `/usr/bin/arch` 环境传递 DYLD 变量未取得加载日志，资格拒绝并保留；第二轮用 arch 的显式 `-e` 参数验证父/候选实际 image。最初 native 工具主文件路径错误，在执行产品前终止，保留日志；正确原主文件的 native-02 才参与测量。最初 fixture 编译缺 error 参数及 shared/limits 顺序错误也保留，不能计入真实资源拒绝。

## allocator、最后 free 与退出边界

[native-02](native-02-arm64/identity.json)使用原 Freehand 六方法，每架 12/0/0、实际 exit 0；普通 malloc 12345B live/free 正控制、overflow 0。arm64 请求 heap 峰值 **98,779,037B**、可识别 paid 链峰值 **6,751,530B**、节点峰值 **28,699**；x86_64 分别 **150,965,290B / 7,034,114B / 30,307**。x86 本轮请求峰值高于上一冻结，实测值照录，不归因为这 16B 字段，也不据此裁决 owned 硬界。main 后 paid 672/680B，static 析构后辨认 paid 0；原 stop fixed anchor 2132/2140B 与静态 60B 仍按各自实际 free/映射寿命保留。

请求 heap 包含 caller 的既有 DataManager/Tile/Qt；paid 栈识别只是子集，不能证明整管线逐笔账本、同时 live/reserved/peak 或总硬界。pre-main/bootstrap、符号递归、usable/RSS/OS mapping、全部外部 owned Qt/native/TLS 和非 Darwin 线程存储/退出资格仍开放。

[十旧 UE 实际复查](old-ue-observed.txt)：32658、43034、48549、59123、70089、83020、87052、87095、91827、88291 仍未 drain。部分父进程 66413 是当前 Codex app-server，未杀它或重启宿主。新进程的正常退出不能替代旧默认失败出口的实际退出。

## 八项结算与直接下一责任

| 用户剩余项 | 本轮结算及仍欠条件 |
|---|---|
| 1 完整 allocation/free | 两内部指针随原 Private 收费、原 scope 取消接受后实际 destroy；93/1715 清单仍非覆盖证明。完整逐 owner、capacity、接受、最后 free 对账欠。 |
| 2 逐拒绝点 | 原 487 生命周期、operation/冷构造/父首次增长实拒通过；新增原 orphan 连续 provider/预算拒绝接续。alias/provider registration、所有 node/control/task/线程实际拒绝仍欠。 |
| 3 全局峰值/硬界 | 保留带正控制的总请求 heap 和 paid 子集，x86 峰值增加如实记录；完整 owned 逐笔对账、合计硬界、旧新数组及 weak 尾容量仍欠。 |
| 4 永久拒绝/无输入恢复 | **operational facade＋后台允许 provider 下，原 orphan scope 的两类拒绝解除后无输入清理关闭**。read/capture/history/publication/retirement/close 的完整联合阻塞、订阅拒绝与原 caller transaction 接续未全验。8MiB 准入后取消已有合同保持。 |
| 5 最后引用/完整退出 | 原 scope 费用至实际 destroy，原 job owner pin 和原 stop 协议保持。facade 先退出、晚 scope、provider 永久拒绝后的全部最终退出组合仍欠；固定 anchor 不是全覆盖。 |
| 6 外部/平台 | caller Qt 不重复收费，owned 部分须继续审计。Darwin 两架有限证据，非 Darwin 未验证，不能推定通过。 |
| 7 并发/失败退出 | 七 TSAN 目标通过，整体 Qt 边界 Inconclusive；十旧 UE 未 drain。新增普通 Matched claim/像素失败在父/候选均复现，须回原 writer/adapter 准入和失败交接修复。 |
| 8 同源冻结 | 最终身份绑定当前提交；失败与父差异对照全部保留。完整 CP1 不勾选，普通 Matched 缺陷、资源硬界与退出缺口不由其他通过数抵消。 |

直接下一责任是原 legacy writer claim 冲突的真实 caller：`reserveLegacyMutationPage → tile/manager adapter acquisition → actual freehand/update jobs`。必须固定不会等待持有自身 tile/manager gate 的复现，沿原 writer/input owner 消除丢失像素的失败交接；不能改单线程、fixture 摘要或原硬限掩盖。随后继续完整分配对账、全部 alias 冷拒绝与联合最终退出。
