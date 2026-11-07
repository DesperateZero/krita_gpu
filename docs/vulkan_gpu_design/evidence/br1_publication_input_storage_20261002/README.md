# 原 publication 工作输入、候选释放与 epoch 完整 write set

最终产品提交 `36189cb3b1bc91d77ea565894bb1fd51f9b6056a`，产品父提交 `1427f464d57e54e9a16245ef4dfd7163d47cdb06`，文档父提交 `63edf439a6ee32bfe3b3b1c41617bb548b38322a`。本地提交、没有 push；[Git身份](git-round-identity.json)、[52份源码](source-sha256.txt)、[15份运行物](runtime-sha256.txt)及[构建环境](build-environment.json)绑定最终结果。普通源码、测试、文档和脚本采用显式 apply_patch；Python用于运行与派生证据。

| 原对象 / 失败来源 | 最终归属与同步删除 | 保留的真实合同 |
|---|---|---|
| proofDescriptors 的完整描述复制 | 原 claim 先安装，付费数组只保留原 immutable descriptor 的 shared_ptr，验证后在门外归还容量 | 避免逐 proof 重取 owner gate；真实 descriptor-array 准备拒绝保留原交易/proof |
| publicationHeaders / publicationSnapshot 的 Qt 页头、版本及嵌套保护投影 | 目录只返回付费 version identities；queryPublication 在同一 shard cut 返回 current/target 标量。两个旧函数及唯一 oracle consumer 同批迁移 | 目录注册计数、页 revision/root/descriptor 复验仍是原责任；观察不授予 mutation authority |
| commit / restore 的完整 Transition 数组 | 原 Data 的 compact change / target array 直接供 metadata 消费；每页构造一个 stack Transition，与 Qt oracle 共用现有政策 | Qt Transition oracle、generic/recoverable 等真实消费者继续保留，不复制另一套状态机 |
| restore changedDefaults / seen / targeted / 第二 Transition 数组及 manifest 中间副本 | 原 immutable surfaces 推导 defaultChanged；原 target prefix 排序去重后作二分查询，目录按 shard 唯一性追加 suffix；full root 直接复制进已付费容量 | changedPages 的无效键跳过、重复键唯一化、隐式 default、晚目录注册与 original retry 保持 |
| backingChanges 的生产 Qt→付费数组再复制 | 原 Data 付费数组移动到 Ledger 原 cookie/slot；native seam 收在 private friend 内，Qt wrapper 使用同一 prepareBackingChangesImpl | 物理/class/Debt 真拒绝与原 slot 取消、缓存和收费继续；slot clear 不虚报数组物理释放 |
| 局部 metadata / epoch 候选与 discardPreparedCandidates | 两种候选从准备开始就在原 Data；全部冷拒绝、revision retry 和安装后释放共用原门外 discardCommit。独立 helper、四处手动 discard 和后置 move 删除 | 准备前无业务 owner；接受 backing reservation 后才开放 tryInstall；没有新增持久阶段或结果队列 |
| Ledger 拒绝后再次 commit 将完整 delta 当增量重放 | 原 epoch prepareImpl 共享验证/原子更新政策；生产 private preparePublication 从完整 owner-validated write set 构造原交易记录，公开 prepare 仍合并 advancing incremental delta | 同一交易原 proof/default/removal 可重试，也能在拒绝后继续写入；公开相同 generation 的增量拒绝保持 |

等价删除与保证增量分别裁决。**生产7文件 +336/-237，净+99；测试2文件 +202/-9；生成2文件 +13919/-12472 单列**，见[统计](source-metrics.json)、[生产差集](production-incremental.diff)、[测试差集](tests_and_model-incremental.diff)、[生成差集](generated-incremental.diff)。本轮增加的是原工作容量的真实收费/冷拒绝，以及完整 write set 拒绝后的正确接续；不能将净增算成等价去重收益。直接保留 Qt 数组加估算额度不能约束真实容量；逐 proof 加锁可省数组，却改变批量 provider 验证的锁成本。本轮保留批量窗口，以同一 paid Data 和紧凑输入完成责任，没有新协调层或上层生产 API。partial restore 准备顺序改为按页键排序，K 项去重为 O(K log K)，目录查询原 prefix 为 O(log K)；多 surface 查询和峰值性能没有取得正式裁决。

最终[universal build-10](build-10.log)完成后运行[七组原 runner](run_results.py)，它复用此前冻结的 runner，环境记录实际源 hash。[最终结果](qualified-results.json)为两架构每架 Registry87、CPU1311、Reference735、Physical381、Resident221、Foundation28、Freehand压力/取消4，共 **5534 passed / 0 failed / 0 skipped**，14进程 exit 0，见[汇总](qualified-summary.json)。未将目标 smoke、首次失败或中间构建累加进最终通过数。

新增或扩展的实际边界：

- `indexedPublicationTransitions` 在相同 history0/31/511 × 18转换上同时走 Qt 与 native compact/version 输入，共用完整 page-record oracle。
- `publicationDirectoryStorageLifetime` 在真实 MetadataArena 恰满时拒绝新目录数组，scalar current/target 仍能观察；metadata/controller 退场后，原数组及 accounting owner/parent-child registration 继续收费，最后数组物理释放后回到基线。
- `freshWriteSelectorAndBackingBudgetAreBounded` 保留 Qt consumer，新增真实大容量 paid producer 的 Ledger move、从 hard full 开始完成 class commit、原 slot 替换后的实际数组归费。原 retirement headroom 可真实释放，未将其错误算作泄漏或要求缓存费用恒定。
- `publicationInputRefusalKeepsOriginalTransaction` 实际填满共享父额，在 descriptor-reference admission 前、metadata/epoch 已准备后的 backing-array admission 两种 cut 拒绝；同 proof/default/removal 保留，容量释放后重试或继续改写一个 proof 都能提交。
- `restorationUsesOriginalTargets` 同一 Store 验证 full root 与重复/乱序/无效键 delta、多个默认页，以及准备窗口新增目录键后的 original reprepare。原 claims/capture、冲突/descriptor/reader/rebase 和 24MiB Freehand 压力/取消同步回归。

原始失败保留：[首次 CPU](focused-cpu-arm64.log)暴露真实完整 delta 被增量重放的缺口；[首次 Reference](focused-reference-arm64.log)含漏算 accounting owner 与非法同类变更的夹具问题；[第二次 Reference](focused-qualified-reference-arm64.log)、[第三次 Reference](focused-qualified2-reference-arm64.log)继续修正 retained registration / 旧 slot 替换 / retirement headroom 的实际费用假设。[错误方法名调用](focused-final-reference-arm64.log)未执行目标组，不作产品失败或资格证据。最终目标结果为[CPU10/0/0](focused-final-cpu-arm64.log)、[Reference129/0/0](focused-qualified3-reference-arm64.log)，最终全组另行冻结；保留的中间日志仅记录诊断，不授予源码资格。

[16项删除/保留检查](deletion-checks.json)由[脚本](check_delivery.py)核对。最终 build/MOC 后才生成[图](callgraph-final.log)：87TUs、2005APIs、24727edges、21callbacks。[首次结构门](architecture-stale.log)只报告9份改动源指纹过期，审阅后[刷新](architecture-refresh.log)并运行[独立结构门](architecture-final.log)，21manifest/25ownership/16census/19intrusion通过。[前](baseline-before.json)/[后](baseline-after.json)ratchet相同，checker、manifest、ownership政策未改。[冻结脚本](freeze_evidence.py)核对最终源码/runtime/Git blob。

Qt oracle/输入验证、原 epoch working/core/root/control、Ledger等挂接前 bootstrap、TileDataStore observer、tree/deferred/close及 runtime 固定费用和完整永久尾出口仍是原 CP1 剩余项。旧 PID43034/87095 仍 UE/parent1，另有此前 Freehand PID91827 未退出，见[现存进程](existing-processes.log)；本轮14个进程均正常结束，不能据此宣告全永久尾退出关闭。没有运行 TSAN、全局 allocator 或正式性能矩阵。**列明输入/释放/重试清理完成；完整 CP1 开放，M6/M7/M8正式0/3、默认关闭。** 当前裁决见[92 §16.57](../../92_br1_m6_m8_execution_baseline.md#publication-input-storage-delivery)，后续只领取当前代码的 epoch/core 等剩余差集。

活动文档核验覆盖6份文档和65个本轮本地链接，并验证52份源码、15份运行物、产品Git、5534结果、差集和ratchet；见[核验结果](document-validation.json)与[脚本](check_documents.py)。本轮没有读取归档内容。
