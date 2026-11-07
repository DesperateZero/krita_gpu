# CP1 原 seal owner 拒绝接续冻结（2026-10-03）

产品从 `f6fb240a2648140b704a414acdafb4d76c557d00` 到 **`71c8b27e08517408102ee03a367338543f3a1225`**。当前裁决见 [92 §16.77](../../92_br1_m6_m8_execution_baseline.md#cp1-seal-retry-delivery)。原矩阵的 **108 seal 取消和 8 partial publish 重放**缺口关闭；**完整 CP1 未通过，M6/M7/M8 正式 0/3，persistent 默认关闭。**

## 原责任、接受点与同批删除

原 mutation session 进入 seal 时冻结写入集合，在同一原 state 增加 `Sealing` 值。真实 metadata、proof、overlay 输入与 surface 准备的存储拒绝保留原输入、claim、page/proof；再借 write guard、execution 或 semantic 修改均拒绝。`isActive()` 包括这段可重试寿命，不表示仍能借出可变像素。checkpoint 接受后恢复原 Active，terminal seal 按原协议 detach；语义/provider validation 拒绝仍取消原 segment，保留先前已接受结果。

private publish 从原 metadata 的 Prepared/transaction/authority 查询接受事实，跳过已消费 writer；proof 从原 page 查询，仍由原 Ledger 校验。overlay preparation 借用 proof，仅 install 接受才转移；删除准备成功时清空原 proof、候选取消时撤销借用 proof，以及资源拒绝时取消原 scope 的旧分支。单次 generic lease caller 同批迁移至 install 接受才放弃 proof，真实终态失败仍撤销其原 proof。alias 重试复用已接受 target，provider 窗口的 gate/activity 用原 scope guard 归还。

metadata 原结果增加 typed storage refusal；原 publication conflict bool 改为同一字节的失败枚举，未按 QString 文本解析政策。生产九文件 **+114/-58，净 +56**，测试一文件 **+73/-0**；生成 JSON 两文件 **+10047/-9503** 单列。没有新业务 owner、恢复队列、锁或上层 public/protected API；原内部方法参数承担拒绝分类。新 frozen 阶段及接受事实查询是保证成本，未授性能收益。alias provider `Failed`/registration 的所有真实分配原因尚未逐点分类，本批九页 CPU seal 不覆盖该族完整拒绝资格。

## 最终同源结果及保留失败

[最终冻结](final-freeze.json)绑定 **116 已提交源码、113 运行物、四配置**；最终矩阵、实际 probe、native、TSAN 均核验 source/runtime hashes。`lifecycle-matrix-01` 是 header/test 最终重建前的中间二进制，505 进程通过但不提升为最终同源资格；`lifecycle-matrix-02` 才是最终矩阵。所有旧失败保留在各自原目录，不改写为通过。

| 证据 | 实际结果与范围 |
|---|---|
| [最终双架原矩阵](matrix-01/results.json) | 22 原进程 **8108/0/0**，全部 exit 0 |
| [原压力三对](matrix-pressure-01/results.json) | 六进程 **72/0/0**，原六方法及 8MiB 准入后取消保持 |
| [连续硬满及语义拒绝](seal-capacity-arm64-01.log) | 13/0/0；seal/checkpoint × retry/cancel 四行，各三次实际父 MetadataArena 硬满；原输入冻结、provider activity 归还、同 owner 恢复、取消释放；旧语义失败契约保持 |
| [最终生命周期拒绝](lifecycle-matrix-02/results.json) | **505 进程 = 18 controls + 487 实际首末拒绝目标，全部 exit 0**；456 未接受后重试、31 后续清理拒绝仍保留接受结果；无 exception、reservation 均 0、旧 captured 像素及 body 一次保持 |
| [operation arm64](probe-ownership-02-arm64/run.log) / [x86_64](probe-ownership-02-x86_64/run.log) | 每架 **224 实际拒绝 + 3 controls + 1 暖态消失目标**；COW 三次连续拒绝、弱尾与真实 free、同 history owner 重试通过；无探针溢出 |
| [冷 operation 独立矩阵](cold-operation-matrix-01/results.json) | **88 进程 = 86 实际拒绝 + 2 controls**，全部 exit 0；每架 ordinal 0–42 逐真实分配拒绝，43 为正常控制；补 discovery 已消费的首次父 reservation 增长 |
| [cold arm64](probe-cold-01-arm64/run.log) / [x86_64](probe-cold-01-x86_64/run.log) | 每架 **17 实际冷拒绝 + 3 controls**，store/subscription/runtime 及 stop 后 callback 断言保持 |
| [结构门](architecture-01.log)、[工具自测](audit-selftests-01.log) | 87 TUs / 2162 APIs / 27317 edges / 25 callbacks；21 manifest / 25 ownership / 16 census / 19 外部侵入门，ratchet 未放宽；六自测通过 |
| [词法复核](allocation-census-02.log) | 93 文件 / 1715 位置；不能作为完整 allocation/free 或故障覆盖证明 |

消失的目标原控制记录实际 **1248B**、`reserveSharedNonPayload` caller；冷进程 [arm64 ordinal 11](cold-operation-matrix-01/arm64-011.log) / [x86_64 ordinal 11](cold-operation-matrix-01/x86_64-011.log)在同一 owner 分别 +632/+772 真实拒绝，body=0、reserved=0，原 owner retry 成功。因此未将 absent 当成注入通过。冷 probe 保留原 ownership probe 的 COW/weak warm-up，仅将第一 operation 改为 fresh-process ordinal 注入。

`cpu-build-02.log` 保留新 fixture 使用错误方法名的编译失败，修正后 build-03 和所有最终测试通过。首轮 operation 两架在 300 秒观察限额被 kill，实际 exit -9、已 reap；原日志保留，未新增 UE。native-01 错用 4096 项旧线性表发生 overflow，峰值资格拒绝；native-02 改回原 65536 项 indexed 表，无生产源码变化，完整重验。第一次词法清点在矩阵 identity 尚未生成时报错，最终清点重新核验冻结 hash。

## 总 heap、账本及退出边界

native-02 沿原 Freehand bootstrap 和六方法，每架 12/0/0、exit 0；malloc **12345B live/free 正控制**及 overflow 0。

| 架构 | 所有 requested heap 峰值 | paid 识别子集峰值 | 峰值节点 | main 后 paid | static 后 paid |
|---|---:|---:|---:|---:|---:|
| arm64 | 98,702,277B | 6,609,338B | 26,762 | 672B | 0B |
| x86_64 | 98,732,438B | 6,728,562B | 28,728 | 680B | 0B |

总 requested 包含 caller 既有 DataManager/Tile/Qt 容量；paid 按 stack 识别。完整 owned 逐笔 ledger、同时 live/reserved/peak、pre-main/bootstrap、符号递归、usable/RSS/OS mapping、Qt/OS/TLS 内部容量仍未取得资格。operation 停止后仍有 fixed **2132/2140B** anchor，费用未提前消失；这不能代表所有尾 handle 已退出。Store 子根 5448B 仍不代表整管线。non-Darwin 未验证。

[TSAN](tsan-01/runs.json)带 clean/race 正控制 0/66；七目标 **2902/0/0**、无报告。DataManager 在原 Qt extent 读写锁边界实际 race66，后续方法截断；同 Qt [独立标准/Qt 同步控制](../br1_cp1_wait_storage_20261003/tsan-qt-sync-controls-01.json)沿用，未加广泛 suppression，完整 TSAN **Inconclusive**。

[最新 UE 快照](ue-snapshot-final.txt)仍有 **十个旧 UE**，本批新进程已全部回收。父进程 66413 是 Codex app-server，不能把杀父作为测试环境处置；宿主未 drain 的原因和默认失败退出复验仍欠。

## 用户八项结算与直接下一责任

| 项 | 当前处置 |
|---|---|
| 1 分配/free 清点 | 原 proof/overlay/session 转交责任收口；16 合同与词法清单不替代所有实际存储逐笔对账 |
| 2 拒绝矩阵 | 原 116 接续失败关闭；487 生命周期、224 operation/架、17 cold/架及首次父增长实际通过；alias/provider/其他原 owner 的完整拒绝覆盖仍欠 |
| 3 全局 allocator/总峰值 | 正控制、无溢出和完整 requested heap 重验；全部 owned 与 ledger 的逐笔及同时硬界仍欠 |
| 4 硬满/永久拒绝/恢复 | 连续硬满冻结及同 owner retry/cancel 通过；联合 read/capture/history/publication/retirement/close 的永久拒绝与无新输入清理仍欠 |
| 5 最后引用/退出 | 原 proof 接受点与已识别 static paid 最后 free 通过；所有晚 handle/在途 callback/anchor 永久 stop 仍欠 |
| 6 框架/平台 | caller 不重复计费；owned 外部容量与 non-Darwin 尚未关闭 |
| 7 并发/失败退出 | 七 TSAN 目标 2902 通过；整体 Inconclusive，十旧 UE 未 drain，原失败事实保留 |
| 8 同源冻结 | 本有限实现与全部失败绑定 71c8b27；完整 CP1 未取得整包冻结通过 |

直接下一责任是联合永久拒绝、容量/保护释放后的无新输入清理。当前原 orphan mutation 链的 retry caller 仅在 abort/close；已有 abandonment fixture 使用显式 `processRetirements → abort` 推动，不构成自主恢复证明。应先核验这条实际原 owner 接续，再完成 alias 与全局逐笔对账；不另建错误专属记录或第二恢复队列。
