# CP1 原 clear 全范围准入及真实 claim 增长竞争

本单元关闭两条已复现的 writer 准入反例，完整 CP1 仍未通过。产品 `0da7ba08899344496b3528e60cb98696f5007f07` 与最终双架构矩阵身份见 `final-freeze.json`；运行开始时为父提交 `35dc0c4574bb1f2a4283ea6e0de5149333a21789` 加保存的候选 diff，最终冻结核对提交 blob、116 源码、113 运行物及四配置。正式 M6/M7/M8 仍为 0/3，persistent 默认关闭。

## 实际故障与原责任修复

1. 原产品 image 的诊断副本在实际 x86 MatchedFreehand 中捕获 `ManagedOtherThread`，栈为 `reserveLegacyMutationPage → acquireTile → fillRect → DataManager.clear → setupProjection → updatejob`。只替换原 Store TU，复用其余 image 对象；原 image、诊断 image、实际 loader、对象哈希及差异均保存。诊断 image 不授产品资格。原产品运行新 range fixture 的两个反例均正常 exit 2、已 reap。
2. `fillRect` 在 capture/pixel body 前以原付费 target 数组取得完整范围 reservation，原 batch mutation 持有它到 adapter install；部分页写、semantic alias/remove 和原取消仍共用原 owner。DataManager clear 使用已有 `PreparedTileUpdates`，原 manager gate 内完成 publication、presence resolve 和 index/extent install。packed、cursor、clear 共用该 install；删除三处重复诊断/安装/解锁政策。没有新锁、持久恢复状态、队列或独立 reservation owner。
3. 中间矩阵虽全绿，随后 Matched x86 第九次实际 exit 1，像素操作报 `write set intersects another writer`，摘要失败。审计 interposer 在真实 `claimAll` paid malloc 准备窗口暂停 A；B 在原范围接受一次操作并保留原 delivery；旧候选将 A 报 Failed，A body 尚未执行。私有 `claimAll` 改为临时 `Acquired/Contended/Failed` 结果，原 `reserveManagedRange` 对 managed contention 复验并等待已有 condition，资源失败仍直接拒绝，native/generic terminal conflict 仍保留。ClaimSet 只在首次实际需要时准备，复验沿同一 receipt；不重试真实 allocator 失败。

最终真实增长探针两架均 `waited=1`、A/B body 各一次、结果成功、current 0x71 / old capture 0x31、claim 0。不是模拟 fault switch，也没有生产暂停钩子。连续 40 个原 Matched 进程为 120/0/0，全部 exit 0、无原两种 pixel/claim warning；这证明已定位窗口的有限修复，不宣称全部 brush/claim 交错已穷尽。

## 行为、资源与同源证据

- 新 range fixture 32 行：四 bpp × partial/full × default-remove/nondefault-alias × history/anonymous；等待他人原 delivery 时独立页继续，原 claim 持有到 adapter install，旧 capture、最终像素、history undo/redo 保持。fresh selection 原 fixture 增加 clear 的 16 行；冷/暖/旧 raw/captured 和 adapter 窗口保留。
- 最终 22 行双架构完整矩阵 **8236/0/0** 见 `matrix-03`；DataManager 每架 1105/0/0。`matrix-02` 的成功 cleanup 测试实际失败行完整保留：它把 metadata install 拒绝后的 prepared candidate 清理也计入成功 cleanup。最终 fixture 只在真实 `CommitRootPublication` 后观察，仍要求一次发布、一次接受清理、reader 在该阶段完成且新旧像素/extent 一致；没有将次数断言放宽为大于零。
- clear 实际分配矩阵 `clear-matrix-02` 共 718 进程：8 controls、702 个实际首/末 occurrence fault、8 个同 history owner 连续三次拒绝后恢复进程（另 24 次拒绝）。四模式均为 bpp1、九目标页，涵盖 warm alias、partial COW、semantic default remove、cold missing wrapper；全部实际 exit 0、original current/captured 检查通过、claim/reservation 0。接受后 cleanup 拒绝保结果，接受前拒绝才重试原 owner。其他 bpp 的行为 fixture 不能替代它们尚未逐点注入的实际 fault 资格。
- 原六 freehand 压力/取消/失败方法三对 72/0/0、六 exit 0，原预算未改。native interposer 原六方法每架 12/0/0，malloc 12345B live/free 正控制、overflow 0；requested heap peak arm64 100,224,689B、x86_64 99,140,058B，paid 识别子集 peak 6,682,866/7,093,802B，节点 peak 48,505/30,823。main paid 672/680B、static paid 0；全部 caller/Qt/Tile requested heap 不是 owned ledger 总峰值或硬界证明，节点上涨照录。
- 93 文件 1718 词法复核位置、16 组合同；87 TUs、2164 APIs、27412 edges、27 callbacks；21 manifest / 25 ownership / 16 census / 19 intrusion 门、六工具自测通过。原 intrusion ratchet 未放宽；初次共享 install 前的 `26 > 25` 失败日志保留。
- 最后成功 cleanup fixture 改动只影响 DataManager 测试 TU；clear/native/growth/Matched/pressure 的实际 image、生产头及所有其他输入与最终候选相同。各旧 run 保存完整自身身份，`fixture_only_compatibility` 明列唯一测试源码和测试 binary 差异；最终 22 行及最终 TSAN 另在完整 116 源码上运行，未将不同生产源码日志合并为同源结果。

生产六文件 +105/-59，净 +46；测试三文件 +126/-25，净 +101；两个生成 JSON +2872/-2495 单列。范围准入和 contention 分类是保证增量，公共上层生产 API 零新增；原内部 fill signature 接收已有 delivery/hooks，全部当前 caller 同批迁移。新增枚举不增加持久内存；新 target/candidate 都沿既有 allocator 收费和实际 free。

## 保留失败与八项结算

`target-counterexample-01`、诊断副本、中间 `target-dm-01` / clear-02/03、`target-matched-02`、`matrix-02`、首轮结构门、构建/命令/清点错误均保留。最终通过不覆盖旧失败。还保留两条新退出事实：

- `probe-claim-before-01-arm64` 原 harness 在 facade/capture 仍存活时 permanent stop，随后析构阻塞在 `HistoryCollector::waitForIdleLocked`。sample 证明 worker 已退出，而晚 schedule 向停止队列插入 job、持有原 activity/ref。只 TERM 本次探针 PID 50484，实际 -15、已 reap。后续增长探针先关闭原 owner 再 stop，仅隔离增长断言；该改动没有修复生产 stop → late close。
- `tsan-02` 七目标 2918/0/0 无报告，DataManager 在 TileSwapper 的 `forgetTileData → freeTileData → pass` 实际 SEGV、exit 66，已 reap。它不能只标成 Qt 锁边界误报。原 map iterator 的普通 `ref()` 能从零引用复活等待 final free 的对象，源码上已识别风险，但确定性复现与修复尚欠；本冻结不宣布根因已经证实。最终 `tsan-03` 六目标 1564/0/0 无报告；CPU 为 1353/1/0，`proof-rejected-after-publish` 在解除拒绝、process/idle 后 abort 仍失败，exit1；DataManager 报 swapper 读 age 对 main `blockSwapping → resetAge` 的实际竞态，exit66。全部已 reap，均尚待独立复现和修复。最新 TSAN 资格未取得，原 Qt extent 非插桩边界仍 Inconclusive，无 suppression。

| 原八项 | 本单元结果及未关闭边界 |
|---|---|
| 1 完整 allocation/free | clear 原 target/adapter、claim growth owner 已核对；16 合同/1718 位置不是全部实际存储覆盖证明。 |
| 2 逐拒绝点 | clear 四模式 702 实拒、同 owner 连拒恢复通过；其他 alias/provider/node/control/task/thread 全族和全部 bpp 尚欠。 |
| 3 全局 allocator/总峰值 | 正控制及无 overflow 的真实 requested heap 已测；逐笔 owned ledger、所有同时 live/reserved/peak、旧新重叠/弱尾及硬界未关闭。 |
| 4 永久拒绝/恢复 | 已交付原 orphan 自动清理保持；read/capture/history/publication/retirement/close 全联合永久拒绝恢复仍欠。 |
| 5 最后引用/退出 | 新 stop → late close 死等已证实；facade/provider/store 先退出、全部 guard/capture/Data/weak、在途 callback 和 static 唯一 final free 尚欠。 |
| 6 外部/平台 | caller Qt/Tile 与 paid 子集不重复收费；实际 owned 外部归属与 non-Darwin 线程/退出资格未验证。 |
| 7 并发/失败退出 | 两 writer 准入反例已修；TSAN 新 SEGV、age 竞态及 CPU abort 断言失败尚欠裁决，整体资格未取得；十旧 UE 仍未 drain，未处置 app-server/宿主。 |
| 8 最终冻结 | 本单元源码/依赖/binary、目标矩阵/压力/结构/工具冻结；完整八项尚欠，整包 CP1 不勾选。 |

直接下一责任是最后引用/永久 stop 的实际交接：停止接受队列后原 owner 必须收回未接受的 pin/activity，物理尾释放沿原记录完成，不能晚排到已退出 worker、调用新 callback 或提前退费。并行消费者不能用普通零到一 `ref()` 复活 final-free 对象。无需改业务输入、预算、原四 worker 或默认开关。
