# 已准备事实的旧失败分支与 commit 副本回收

最终产品提交 `1427f464d57e54e9a16245ef4dfd7163d47cdb06`，中间提交 `bdba047303e80570afc6698811eb88c0f28a04c9`；本包起点为产品 `7141769304ae83437db17339383e6f43e464963c`、文档 `c52c547b1dc8e286d8031e7ede11fc5983f4164a`。退出审查补齐同一 claim 下的 epoch 假拒绝，以第二个聚焦提交追加，没有改写首次提交。本地提交、不 push；[Git 身份](git-round-identity.json)核对 52 份源码 blob、15 份运行物及 tracked 产品树清空。[源码](source-sha256.txt)、[运行物](runtime-sha256.txt)、[环境及原 runner 身份](build-environment.json)绑定最终结果。源码、测试、文档用显式 apply_patch；脚本只编排和生成证据。

| 原残余 | 最终责任与删除 | 保留边界 |
|---|---|---|
| native seal 的两次 host completion 缺失失败，以及 commit/restore 的同类候选回滚 | Store 配置先准备并成功终结唯一 host ticket，再开放 configured/operational 入口；ticket 只有一次赋值。所有上述消费者直接读取同一事实，旧业务拒绝/回滚删除 | 配置本身的 source/ticket 准备拒绝保留；真实 provider/proof/metadata/epoch/backing 准备不从该保证获得豁免 |
| 原 owned proof 撤销返回 false，以及 abort 的 epoch 身份失配仍据此退出 | commit/abort 的同步 claim 排除原交易修改；proof 来自唯一原索引，Ledger revoke 只 unlink/free paid node，没有分配或 provider 交接。私有撤销改为 void noexcept；原有效且 active 的 epoch 在 claim 内完成 abort。身份破坏统一按不变量处理，两种可重试 false 出口删除 | 公开 Ledger revoke/epoch abort 的 foreign/重复/无效身份拒绝保留；abort 的 metadata/Debt 真实拒绝及原 pump 保留 |
| commit 的 surfaceChanges QHash / preparedKeys QSet | 直接读取原付费交易 state；同步 claim 覆盖 provider 验证、重准备及清理的解锁窗口。两份重复容器及 QHash include 删除，完整 public validity、精确值/数量/所有权检查保留 | 公共 isValid 的去重验证、Qt proofDescriptors/transitions/directory/backing 输入及 epoch/core 仍有消费者，继续原 CP1 |

没有新增持久状态、队列、上层生产 API 或业务保证。surface 查询由原 vector 的线性查找替代临时 hash，proof key 查询仍为原 hash；多 surface 成本尚未测性能。**生产 3 文件 +49/-67，净 -18；测试 1 文件 +48/-0；生成审计 2 文件 +7535/-7167 单列**，见[统计](source-metrics.json)、[生产差集](production-incremental.diff)、[测试差集](tests_and_model-incremental.diff)。差集覆盖两个提交的完整生产边界，图重索引不计作实现简化或增长。

最终[universal build-02](build-02.log)完成后才运行[原七组 runner](run_results.py)；它复用上轮已冻结 runner，环境记录其 hash，输出写入本目录。[最终结果](qualified-results.json)为 arm64/x86_64 每架 Registry87、CPU1306、Reference680、Physical381、Resident221、Foundation28、Freehand压力/取消4，合计 **5414 passed / 0 failed / 0 skipped**，14 进程 exit 0，见[汇总](qualified-summary.json)。补齐 epoch 之前的构建、5414通过、源码/运行物/中间 commit 身份、图和结构结果完整保留在 [before-epoch-closure](before-epoch-closure/git-round-identity.json)，不与最终结果累加；没有中间产品失败或诊断 build 计入资格。

新增 `commitValidatesOriginalDelta` 在同一真实 Store 上组合两个 proof、surface default 和 removal；8 类伪造/缺项/重复输入拒绝后仍保留原交易/proof且不进入 commit 候选，合法乱序 export 随后成功并撤销原 proof。原 `hostLogicalCompletionIsPreparedOnce`、preparation claim/晚 capture、disjoint rebase、冲突原子拒绝、default/directory/descriptor 复验、真实硬满及 24MiB Freehand 压力/取消沿原断言回归。新增行没有替代硬满测试；本轮没有授予完整 CP1 资源保证。

[14 项删除/保留检查](deletion-checks.json)由[脚本](check_delivery.py)核对实际保证与剩余来源，不用静态检查代替行为。build/MOC 完成后生成[最终图](callgraph-final.log)：87 TUs、2000 APIs、24588 edges、21 callbacks。首次[结构检查](before-epoch-closure/architecture-stale.log)仅报告 4 份改动源指纹过期，补齐 epoch 后[再检查](architecture-stale.log)仅有 publication 源指纹过期；审阅后[刷新](architecture-refresh.log)，再跑[独立门](architecture-final.log)：21 manifest/25 ownership/16 census/19 intrusion 全通过。[前](baseline-before.json)/[后](baseline-after.json) ratchet 相同，checker、manifest 和 ownership 政策未改。[冻结脚本](freeze_evidence.py)核对最终 Git/source/runtime 身份。

surface 准备仍实际分配工作数组，metadata/root/revision/proof/Debt/physical Pending 拒绝仍可达；这些阶段及原 retry 不属于过时协议。旧 native 失败 PID43034/87095 本轮仍 UE/parent1，本轮合格测试均正常退出，不能推定完整永久尾退出已关闭。未运行 TSAN、全局 allocator 或性能矩阵。**本轮列明清理完成；完整 CP1 开放，M6/M7/M8 正式资格 0/3、默认关闭。** 当前裁决见 [92 §16.56](../../92_br1_m6_m8_execution_baseline.md#prepared-fact-residue-delivery)，当前领取从原 Qt 输入/投影剩余差集继续。

活动文档与交付核验见[结果](document-validation.json)及[脚本](check_documents.py)：6份文档的50个本轮本地链接、52份源码和15份运行物、最终Git及5414结果、差集与ratchet均一致；没有读取归档内容。
