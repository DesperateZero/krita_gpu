# CP1 固定根漏费与完整 manager 暴露的 extent 竞态

本轮从产品 `61a0e28bdd1d8d6ac56f471550eb3f0e1db42b4b`、文档
`4d913ae24d98b11967f1bd44762b4a8a0ccb06dd` 取差集。当前裁决只写入
[92 §16.85](../../92_br1_m6_m8_execution_baseline.md#cp1-static-root-extent-delivery)。
产品提交为 `7804582f93bb1eb841b7520728169f0e228b046c`。

独立 Mach-O 符号、section 和 DWARF 清点发现，原固定费 92B 遗漏九个
identity、reclaimer worker identity、Resource/executor handle 及实际初始化
guard。原命名存储实际 arm64 220B、x86_64 292B；后者还保留 capability
静态值和 guard 共72B，arm64 已优化掉该存储。

原 process 的两个 gate 改为内嵌 `std::mutex`，原锁序和消费者继续使用。
原 capability 直接返回相同 inline 值；删除其静态 handle/guard。
固定费补齐原实际字段、handle 和三个 guard。两架实际命名存储及冷启动
计数均为332B，费用比92B增加240B；物理存储分别增加112B/40B，属于
保证成本。[独立清点](static-census-primary-01/summary.json)与
[运行时及原EAGAIN结算](fixed-root-and-native-summary.json)分别保留，
不将产品计数作为独立清点依据。只关闭该命名固定存储范围。

旧完整 manager 在4232.14秒实际退出66，原1100项 passing prefix包括
stressTest/stressTestLazyCopying，随后 `stressTestExtentsColumn` 的
`Data::remove` 写入与未加锁 `Data::min` 读取构成TSAN竞态。
[失败后冻结](../br1_cp1_final_qualification_20261004/qt-manager-full-01/terminal-freeze.json)
确认原123源码/61运行输入未变、进程已回收，不能记作超时或通过。
三个原getter使用已有 extent read gate；`updateExtent` 已持原gate的
消费者直接读取同一字段，避免递归获取。未增加锁、owner、队列或公共API。

隔离候选与主树重建分别验证。原两架 Foundation/CPU/Reference/extent
完整body各四进程合计4414/0/0，均actual0且确认加载对应库；
[主树arm64](primary-ordinary-01-arm64/results.json)、
[主树x86_64](primary-ordinary-01-x86_64/results.json)。
[原extent TSAN](qt-extent-01/results.json)3/0/0、actual0，实际加载匹配
插桩QtCore，无suppression。原worker/monitor两架12实拒/4控制、四actual0，
回滚与static后paid0/overflow0成立。
[七个完整PageStore TSAN body](qt-concurrency-01/results.json)同次
2954/0/0、七actual0；所有源码和库在运行后复核。

[调用图](callgraph.log)为87TUs/2166APIs/27531edges/27callbacks；
[架构检查](architecture.log)维持21manifest/25ownership/16census/19-file
原ratchet。生产五文件+50/-15；产品测试修改0。两个新增私有constexpr
函数只供固定费计算与ABI guard类型推导，原失效常量及静态capability删除。
派生两JSON+1159/-1067，产品提交合计+1209/-1082。

`candidate-build-01`/`02`保留前候选；`ordinary-01`/`02`虽实际退出0，
但未加载候选库，全部保持Inconclusive。最终03通过显式
`arch → env → binary`传递加载路径，修复macOS保护程序过滤DYLD环境的
观察错误。每个运行保留命令、源码/运行库哈希、原始日志及实际退出；
先启动的runner保存原输入副本。120个C++源/头、1个审计Python和2个
派生JSON分列；运行source集合121指非派生源及审计输入，不伪称
测试启动前已经取得随后生成的审计文件。

两个Freehand容量body复用原audit-only main/qExec和未改body，加载新库。
`capacity-01-x86_64`因与arm64共享资源数据库而在SQLite busy等待，诊断
SIGTERM实际-15/reaped、未进入body，采样与失败保留；后续顺序执行。
[最终容量结算](capacity-summary.json)：双架14/0/0、四actual0，8MiB取消
峰值7,960,366/8,031,374B，24MiB压力13,269,222/13,072,630B。观察式仅为
E8识别paid请求＋实际native请求＋独立命名固定存储332B；四次12,345B
正控制均在333B界观察12,677B/一次越界后复位，实际body无越界。
join地址实际unmapped、native和static后paid归零。框架初始化完整，
该式不覆盖未归类/Qt/OS/usable/TLS与全owned硬界。
[最终冻结](final-freeze.json)绑定产品blob的123输入：120个C++源/头、
1个审计Python、2个派生JSON，以及174运行/审计输入。早期121标签曾把
审计Python计作编译输入，分类修正及原标签保留；输入和hash没有变化。
完整manager第二次运行使用原48tasks/16threads/100000cycles和seed12345，
源/库保持冻结；实际终点取得前保持Pending。

**完整CP1仍开放：** 全owned独立总硬界/初次native外部合并；其余真实
fault及read/capture/history/publication/retirement/close、晚fence/caller
联合终点；Qt/OS/usable/TLS和非Darwin；完整manager实际阳性终点及十三UE/
宿主默认abort退出。原arena、两线程重费、scope自保环、单transition及
已关闭有限拒绝不重领。M6/M7/M8正式0/3，persistent默认关闭，CP5/CP10归原包。
