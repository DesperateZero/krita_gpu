# Commit / descriptor 旧存储协议回收（2026-10-02）

产品提交 [7141769304](code-commit.txt)，父产品 `5188f8d9c5c2a2e0e726a3ef667890e49b630585`、父文档 `c9bd8ded50c40084e6c6895ac3d3eef4af08eb24`；[Git 身份](git-round-identity.json)绑定 52 份源码 blob、15 份运行物和 5 份构建依赖。范围为原 commit/restore Data、descriptor/configuration 索引及全部实际 descriptor consumer。未 push；完整 CP1、M6–M8 和 BR1 仍开放，默认关闭。

原索引唯一决定版本描述。实际 paid map 节点在 metadata 成功前准备；native/generic/alias/implicit fresh 路径也在其 provider 调用前准备。初始 adoption 接收 caller 已拥有的 replicas，adoptInitialPageBytes 的拒绝继续由原预付退休记录承担，本批不宣称所有初始化存储都早于外部 physical allocation。安装只转交节点或交换既有值；ordered index 删除旧 hash/bucket 容量协议。相同布局共用索引中的 immutable descriptor/control，同一候选只查原索引与自己的冷节点，不增加另一份可见索引或全局 intern cache。native Page 在原 claim/session 保护下借用该版本的描述值，取消/封存结束使用后才允许删除，旧 Page 描述副本删除。完整 descriptor 的相等查找为冷准备线性扫描，版本查找变为 O(log N)；没有取得性能资格。

原 commit/restore Data、descriptor-change 数组与节点/control 接实际 MetadataArena；冲突或拒绝在已有解锁窗口丢弃同一候选。原同步 commit/abort 调用栈拥有 intrusive claim，替代可能分配的 QSet，无新活动计数、业务阶段或 retry 队列。配置 high-water 表一次准备完整 paid 值，原子交换先于 owner/metadata/epoch 初始化，旧逐 surface 后置导入删除。此保证仅消除本次存储拒绝的后置副作用，其他 bootstrap 初始化失败没有取得全局原子配置资格。

同批删除 putDescriptorLocked 和全部 post-success 插入、DescriptorHash/bucket reserve、未付费 make_unique Data、Qt descriptor-change 数组、额外 History key 数组、allocated claim 集合、递归 virtual-default 重复准备及不必要的描述副本。真实 descriptor revision、metadata/root/claim/physical/backing 拒绝仍保留；History 原 rescan/retry 政策保持。公共 Qt 输入/输出、epoch core、其他 wrapper/bootstrap/固定成本与完整永久拒绝尾出口继续原 CP1。

生产 4 文件 **+287/-134，净 +153**；测试 1 文件 **+103/-1**；验证工具 1 文件 **+8/-3**；生成审计/ownership 3 文件 **+9471/-8060** 单列，见 [差集](source-metrics.json)。净增是实际收费、冷准备和安全借用的保证成本，不能声称等价重构实现净减行数。原 descriptor 查询同时提供 protected borrow，外部 Store 的 bool/copy 合同保持；私有导出仅供实际存储集成测试。

[最终 universal build-09](build-09.log)后，[双架构 7 组结果](qualified-results.json)为 **5412 passed / 0 failed / 0 skipped**，14 进程退出 0；每架 Registry 87、CPU 1305、Reference 680、Physical 381、Resident 221、Foundation 28、Freehand 压力/取消 4。新增一个 integration case 实际耗尽 MetadataArena，验证节点及 Data 冷拒绝、virtual-default 拒绝不注册 metadata、两个在途候选硬满安装、相同值不再分配节点、配置拒绝/重复输入不留下部分 high-water、解除压力后成功，以及 controller 退场后 inert Data/node/control 继续收费至最终释放。Data 拒绝测试触发实际 wrapper allocation，未证明所有语义 commit 阶段都能在硬满完成；活 semantic candidate 仍依赖原 owner。

父 controller 的真实 reservation cache 在测试前温热，最后费用精确回到这个原基线。空 map 也持有 retained allocator；必须销毁它们后才能判断最后尾引用的释放。该事实是原 accounting 寿命，不能通过放宽最终费用断言消除。

原 24 MiB 预算、正常 stroke/慢 reader/finish/undo 和取消断言未改。working-04-all 的 x86 压力失败，working-07 在删除 Page 副本后仍出现真实 269568-byte shared-budget 拒绝，促使相同布局改为共享不可变描述。working-08 双架构全通过，但仍含临时 allocator 诊断；只有移除诊断后的 qualified 结果取得本批资格。focused-02 的 final-tail 失败与 working-04 的 budget 诊断文字合同失败均保留。working-05 首次手动 Freehand 启动遗漏 harness 环境，未进入测试并被终止；configured 日志为恢复原环境后的独立运行，不作为最终资格。build-06 的中间 borrow 顺序在 build-07 前修正，没有运行该中间测试。所有 checkpoint 分开保留，不把中间通过累加到最终数。

[18 项删除/保留检查](deletion-checks.json)、[调用图差集审查](callgraph-delta-review.json)及[独立架构门](architecture-final.log)绑定最终源码：87 TUs、2000 APIs / 24547 edges / 21 callbacks，21 manifest / 25 ownership / 16 census / 19 intrusion 门通过。API 净 +4 为原 paid Data/deleter、调用栈 claim、ordered comparator 和准备签名替代的合计；无上层新生产 API。checker 更新旧 unique_ptr 和 688-byte 字面合同，并补 descriptor/high-water/claim 形态检查；native Page ceiling 收紧至 512 bytes，baseline ratchet 字段完全不变。stale 与首次 refresh 拒绝保留，最终不豁免旧布局检查。

当前裁决见 [92 §16.55](../../92_br1_m6_m8_execution_baseline.md#commit-descriptor-storage-delivery)与 [NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)。下一有限端点为原 commit/restore 的 Qt 工作输入/投影和真实 downstream consumer；公共边界及 epoch/core 依赖继续按实际合同清点，原 native seal/generic finish 的真实拒绝与 Failed/cancel 保留。CP0、CP5 原 job 接续、TSAN、公平及 BR1-PERF 无新增资格。
