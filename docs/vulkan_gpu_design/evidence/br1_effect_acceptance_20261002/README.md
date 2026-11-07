# Metadata effects 直接接受与残余协议清理（2026-10-02）

本批从产品 `8896ac1dab5364e403048d9069703c4ed9dd0978`、文档 `24e432ad1ac31300db027806b7c405efd306d72a` 继续，有限端点是 metadata 准备 effects/Debt → 权威修改 → 原退休 record 接受 → 前台/后台处理 → 实际释放。产品提交及源码 blob 核对见 [Git 身份](git-round-identity.json)、[提交](code-commit.txt)；实际增删见 [source-metrics.json](source-metrics.json)。完整 CP1、M6–M8 与 BR1 仍未结算，默认启用关闭；未读 archive、未 push。

原 paid effect span 在修改前准备，配置的原 Debt owner 在提交回调中直接转交 exact backing 的原退休 record。metadata 只返回 `accepted/rejectionReason`；Qt effects 输出、Store/publication 的聚合数组和追加/复制、cancelPage/prepareAlias/PrepareAbort 的输出参数、History 的局部输出类型与二次交接、旧 `retireEffects` batch API 同批删除。没有新持久阶段、队列或恢复记录。缺少 receiver 的 effect-bearing generic transition 在修改前拒绝，这是本批补齐的接受保证；真实 Store 一直配置原 owner，独立 oracle 夹具迁到明确 receiver。

同一 `m_ready` 暂存首次处理的原 record，其既有 `backgroundRetirement` 决定 worker 许可。显式 process 保留总条数额度，后台保留 32 条上限；前台首次尝试在原 pump 边界执行，之后仍归原 pending/retry、subscription、operation、close 政策。worker、manual 和 pump 共用 `retireBatch`，provider 调用保持在 Store/queue 门外。operation 未触及页回滚的提前返回也使用同一退出 pump，前页接受不会因后页 Debt 拒绝而丢失首次处理。逻辑 borrow/claim 与物理记录数量仍是不同事实；没有改变原活动计数含义。

最终 universal build 为 [build-08](build-08.log)。[双架构完整结果](qualified-results.json)共 **5404 passed / 0 failed / 0 skipped**，14 个进程均退出 0；每架 Registry 87、CPU 1301、Reference 680、Physical 381、Resident 221、Foundation 28、Freehand 压力/取消 4。新增 generic 三行使用真实 Ledger/provider/MetadataArena：提交后耗尽全部剩余容量仍完成转交、原节点地址及许可不变、foreground process(0/1) 守界、missing receiver 不移除、不转 Debt；拒绝后的原记录经 close 实际一次释放，backing/Debt/operation 全清。新增双页 operation 回滚行实际只容纳一页 Debt，后页拒绝仍泵送前页，解除拒绝后只取消未完成页，像素、关闭及物理释放正确。

既有 partialCancellation 覆盖 native/generic/sealed 的部分成功，History actual capacity/no-input retry、accepted Pending 不重发、close/晚通知与 oracle 矩阵继续通过；不将这些结果升级为完整永久压力尾退出、全局 allocator、TSAN、公平、CP5 原 job 接续或性能资格。foreground ready 的 permission 扫描及额外 pump 窗口有成本，未测短 gate/正式性能。公开 Qt StateMachine oracle、Ledger 显式 effects 输入、实际 paid metadata/Debt/arena/claim/proof/overlay 拒绝及 Failed/cancel 仍有 consumer，不做无依据删除。

生产 **11 文件 +144/-156，净 -12**；测试/模型 **3 文件 +240/-49，净 +191**；生成审计/ownership/manifest **4 文件 +13593/-13125**单列。净删来自完整交接收敛，必要 compact result、共同 batch 和许可选择的增量已计入生产差集；Store.h 的一行 friend 只授权现有 integration test 访问原私有 operation 端点。上层生产改动与 public/protected API 净增长均为 0，manifest 门限不变。静态删除检查与剩余依据见 [deletion-checks.json](deletion-checks.json)；它们不替代实际容量和时序测试。

最终调用图、独立 architecture 检查与 [API 差集审查](callgraph-delta-review.json)绑定同一源码；50 份 [源码身份](source-sha256.txt)、15 份 [运行物身份](runtime-sha256.txt)、5 份 [构建依赖](build-environment.json)随本地提交复核。API 多一个原 queue 私有 `retireBatch`，三个真实入口共享它；改签名和无 effects 的 pump 替换原入口，不增加上层状态权威。manifest 仅把原退休服务的 `retireEffects` 符号换成 `processAcceptedEffects`，其余内容和全部 ratchet 门限字节一致；图在该最后消费者迁移后重新生成，审计/ownership 共 4 文件单列。

失败及中间结果完整保留：build-02 的测试字段拼写、build-05 的 private consumer 访问在最终修复；working-03 两架各两个 Reference 旧 receiver 假设失败，working-04 5402/0/0 只对应回滚修复前源码，working-06 的活动计数断言和 working-07 的 default 读取后物理内存断言各在两架失败。修正测试以保留原逻辑 claim 和 default read materialization 合同，没有放宽退休次数或释放断言；[双页目标日志](rollback-target-arm64.log)及 x86_64 目标通过后才冻结最终矩阵。中间源码/运行物哈希、完整 diff、图和日志独立保存，不累加为最终资格。

当前继续范围统一维护于 [92 §16.53](../../92_br1_m6_m8_execution_baseline.md#effect-acceptance-delivery)和 [NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)。overlay、外部 Qt/注册/诊断/Transition 输入、bootstrap/控制本体/固定成本以及完整尾退出仍属于原 CP1。
