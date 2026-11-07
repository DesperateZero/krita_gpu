# CP1 commit retention 原子准入冻结（2026-10-03）

产品从 `0d3b9f5d87e16e01587acdb03e00985ac07aae80` 到 **`f6fb240a2648140b704a414acdafb4d76c557d00`**。当前裁决见 [92 §16.76](../../92_br1_m6_m8_execution_baseline.md#cp1-commit-retention-delivery)。本批关闭六个已安装 root 后 retention 拒绝导致原 history capability 丢失的真实分配故障；**完整 CP1 未通过，M6/M7/M8 正式 0/3，persistent 默认关闭。**

## 原责任与同批删除

`PreparedCommit` 在 root 可见前准备原 retention registry 的付费 node，以及 structural snapshot 的 surface 输出。候选尚未增加可见 root/token；拒绝、重验冲突、替换候选及晚于 facade 释放均由同一候选释放。原 epoch gate 内安装 root 并转移已准备 node/输出；接受后没有第二次 retention 分配。registry node 使用原 retained allocator，收费跟随最后实际 free；输出沿既有 process storage allocator，未改成 caller Qt 例外。

publication 将原 sink 要求传至候选；memento 原 active record 在拒绝时保留。旧 post-install `retainSnapshot`、after-root 失败返回、`orphanedAfter` 字段及其释放分支同批删除。普通 reference commit、独立 snapshot retention、restore 的外部语义保持。生产五文件 **+73/-42，净 +31**；测试两文件 **+61/-12，净 +49**。两份生成审计 JSON **+7663/-7364** 单列。候选新增 node/snapshot 字段，费用仍按实际 `sizeof`/capacity 收取；这是保证增量，不授性能或峰值减少资格。无新公共生产 API、业务 owner、恢复队列或锁；新增一个私有 description helper 由正常 retention 和候选 preparation 共用。

## 同源结果及原失败

[最终冻结](final-freeze.json)逐项校验 **116 已提交源码、113 运行物及四配置**，并记录不参与各旧探针的 Reference/DataManager fixture 差异。生产 image、原 probe sources/compile/link inputs 不变；旧失败身份不改写。

| 证据 | 实际结果与范围 |
|---|---|
| [最终双架矩阵](matrix-03/results.json) | 22 原进程 **8100/0/0**，全部 exit 0；冻结结束再次核验源码/运行物 |
| [原压力三对](matrix-pressure-01/results.json) | 六进程 **72/0/0**，原六 freehand 方法、8MiB 准入后取消及旧压力合同保持 |
| [候选目标](retention-reference-arm64-04.log) | 14/0/0；不可见、单次安装、实际 token/root 保护与最后释放、重验拒绝、move assignment、foreign owner/晚 candidate |
| [实际拒绝最终矩阵](lifecycle-matrix-02/results.json) | **505 进程 = 18 controls + 487 首末拒绝目标；389 成功、116 exit 9**；原六个 post-acceptance refusal 全部关闭，无 accepted=0/install=0→1；原 body 一次，旧 captured 像素保留、reservation 归还、同 owner retry |
| [未关闭故障](failed-lifecycle-final.json) | checkpoint/commit 各 54 原 seal 取消，共 **108**；各 4 partial private publish 重放，共 **8**。第一轮相同 116 失败完整保留；其全清单身份因无关 Reference fixture 修改而拒绝冻结 |
| [结构门](architecture-02.log)、[工具自测](audit-selftests-01.log) | 87 TUs / 2161 APIs / 27260 edges / 25 callbacks；21 manifest / 25 ownership / 16 census / 19 external intrusion，ratchet 未提高，六自测通过 |
| [词法复核](allocation-census-01.log) | 93 文件、1715 复核位置；不是完整 allocation/free 或故障覆盖证明 |

`matrix-01` 及前三份目标日志保留扩展 fixture 的失败：后续事务先未 prepare，继而 empty prepared set 不合法；最终使用真实增代 proof。两次 callgraph 因 indexing 中 source 变化拒绝，失败日志保留，最终稳定源码生成通过。

`matrix-02` 的 **PID 88291** 在 `testPageStoreHistoryClearStagesAbsence → backend::store` 解引用空 backend，超时 kill 后仍 UE；[sample](new-ue-88291-sample.txt)、[记录](new-ue-88291.json)及原日志保留。构造允许拒绝，fixture 原先缺准入断言；前一压力 scope 恢复配置前未 drain 原 terminal cleanup。现先 drain 后恢复配置，并在该 clear fixture 明确断言准入；[六个独立复验](drain-fixture-results.json) **60/0/0**，最终两架完整矩阵通过。具体首次构造拒绝原因未直接取得，cleanup/policy 时序是源代码支持的解释；不宣称宿主失败退出已修复。原九个 UE 加本批一例，当前 **至少十个未 drain**，见 [快照](ue-snapshot-final.txt)。

## allocator、峰值与退出边界

native 直接编译原 Freehand source，只替换 main/qExec 边界，原 bootstrap 和六方法保持；每架 12/0/0、exit 0。[arm64](native-01-arm64/run.log) / [x86_64](native-01-x86_64/run.log) 均有 malloc **12345B live/free 正控制，overflow 0**。

| 架构 | 所有 requested heap 峰值 | paid 识别子集峰值 | 峰值节点 | main 后 paid | static 后 paid |
|---|---:|---:|---:|---:|---:|
| arm64 | 98,736,045B | 6,576,538B | 27,621 | 672B | 0B |
| x86_64 | 99,071,472B | 6,952,186B | 27,018 | 680B | 0B |

总 heap 含 caller 既有 DataManager/Tile/Qt 容量；paid 依 stack 识别而非所有 owned 逐笔对账。pre-main/runtime bootstrap、符号递归窗口、usable/RSS/OS mapping 等边界沿 [§16.75](../br1_cp1_wait_storage_20261003/README.md)保留。stop 的 fixed anchor、static 60B、enabled profiling TLS 等责任没有由这个 heap 子集关闭；Store 子根 5448B 仍不代表整管线。未测 non-Darwin，不能授跨平台完整退出或总硬界资格。

## TSAN 裁决

[首轮八组](tsan-01/runs.json)和 [最终 DataManager fixture](tsan-02/runs.json)均带 clean/race 正控制 0/66。其余七个最终二进制不变，共 **2898/0/0**、无报告；最新 DataManager 实际 exit 66，原 extent 的 Qt 读写锁边界报告保留。Qt 身份与 [独立同步控制](../br1_cp1_wait_storage_20261003/tsan-qt-sync-controls-01.json)相同；未插桩 Qt 与标准 shared_mutex 的分歧未消失，不加广泛 suppression，完整 TSAN **Inconclusive**。后续方法被首报截断。

## 用户八项结算

| 项 | 当前处置 |
|---|---|
| 1 分配/free 清点 | retention node/output 前移及实际 owner/free 已闭合；16 合同与 1715 位置不替代全量逐笔清点 |
| 2 拒绝矩阵 | 六个 after-root 故障关闭；487 目标仍 116 接续失败，须回原 seal/metadata/proof owner |
| 3 全局 allocator/总峰值 | native 正控制、无溢出和总 requested 峰值重验；完整 owned/live/reserved/peak、漏费/重复费/硬界仍欠 |
| 4 硬满/永久拒绝/恢复 | 原压力与准入后取消保持；seal 部分准备、联合永久拒绝/释放后自主恢复仍欠 |
| 5 最后引用/退出 | 候选晚引用及已识别 static paid 最后 free 通过；全部 anchor、在途回调和最终责任仍欠 |
| 6 框架/平台 | 输出沿原付费 owner；caller 与 owned 分类、其他外部容量和 non-Darwin 仍欠 |
| 7 并发/失败退出 | 七组 TSAN 2898 通过，整体 Inconclusive；旧九 UE 加本批一 UE 均未 drain，不能被最终绿表覆盖 |
| 8 同源冻结 | 本有限实现及所有失败绑定 f6fb240；完整 CP1 未冻结通过，后续源码必须重新结算 |

直接下一责任：原 seal 接续保留已接受 private metadata/proof，资源拒绝保留原 frozen input/claim，语义拒绝按原取消责任终结；防止再次借出可变 bytes 或重放已接受动作。先关闭 108+8 失败，再完成其余完整 CP1 差集，不建立错误专属旁路记录。
