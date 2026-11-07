# Overlay 存储闭环与旧拒绝政策回收（2026-10-02）

产品提交 [5188f8d9c5](code-commit.txt)，父产品 `7c90a4f07d9486391df22eb2cc7aed6bf8a5e171`、父文档 `348c921f86972e4202bdfa9cc17358117a26ec28`；[Git 身份](git-round-identity.json)绑定 52 份源码 blob、15 份运行物和 5 份构建依赖。有限端点是原 overlay 准备、复验、安装、History 清理责任接受与实际存储释放。没有 push；完整 CP1、M6–M8 和 BR1 仍开放，默认关闭。

原交易 state 继续唯一拥有 proofs/removals/surfaceChanges。Data、交易 index/state/control、节点/buckets、输入/版本/变化数组与抽出的旧节点使用真实 MetadataArena 容量；候选为全部在途插入准备容量，安装只转交原节点。commit/abort 完成原可见性修改后，在已有解锁窗口释放最终聚合；已安装并收集的候选尾存储可以晚于 facade/controller 销毁，费用保留到实际 deallocate。未安装候选仍依赖原 owner/activity 寿命，没有授予任意 capability 在 owner 退场后继续操作的保证。

同批删除重复 keys 集合、historical 数组、derived extent 的完整 Qt delta 导出和临时 RemovalSet、Qt surface detach/后置容量拒绝、完整 detachment Transition 数组及无法再进入 typed input 的旧字段检查。生产私有 detachment 输入仅为版本身份；底层仍复验 Prepared 所属交易、writer 和全部页的原子 claim，reader/pin/last-use 保留当前值。公共 Qt oracle/commit/restoration 输入仍有真实 consumer。

History 原来已用 metadata 保留未退休版本、用 rescanRequested 保留 missing-key 枚举责任；后台节点拒绝进入原冷 retry，前台却抛出。现在 requestKeyLocked 统一保留该责任，collectPassLocked 独占重新枚举，foreground/worker 共用它。已发布结果不会因后续清理的真实节点拒绝改报失败。没有增加阶段、恢复队列或候选节点协议；实际 Work/GC/Debt 拒绝、reachability、subscription、provider Pending 和原自动 retry 保留。

最初把 History 节点复制到候选的方案在真实 24 MiB 共享预算下使 x86 stroke 失败。只提前释放 producer 输入及压缩 Transition 并不足够；沿原 collector 的事实收敛后删除了整套候选 History 节点。原新保证的实际收费有必要，但重复保活不必要。最终生产 9 文件 **+279/-181，净 +98**；测试/模型 2 文件 **+228/-26，净 +202**；验证工具 1 文件 **+2/-1**；生成审计/ownership 3 文件 **+11746/-10261** 单列，见 [差集](source-metrics.json)。净增包括实际收费、保活和无后置增长的保证成本，不能作为等价去重净减行数的结论。

[最终 universal build-14](build-14.log)后，[双架构完整结果](qualified-results.json)为 **5410 passed / 0 failed / 0 skipped**，14 进程均退出 0；每架 Registry 87、CPU 1304、Reference 680、Physical 381、Resident 221、Foundation 28、Freehand 压力/取消 4。原 24 MiB 限额及正常 stroke/慢 reader/undo/finish/取消断言未改。新增三行覆盖候选与 surface 实际硬满拒绝、两个在途候选、取消后容量归还、硬满安装及真实 History 节点拒绝；解除压力后仅泵送原 collector 即完成两次实际退休，无安装重放，最后候选释放后 child 费用精确回到 parent 自有缓存基线。

parent 自己的 reservation slots 是活 owner 的缓存：测试在子 owner 进入前用真实并行 reservations 温热该缓存并冻结基线，不能错误断言 parent 所有 live 费用为零。原 controller 销毁后候选仍收费，最后候选释放后 child 所有费用归还；这项测试不替代所有 wrapper/永久拒绝的最后 handle 资格。已有 History 无新输入 retry、partial cancel、capture/conditional removal 和完整 oracle 继续通过。

[22 项删除/保留检查](deletion-checks.json)、[调用图审查](callgraph-delta-review.json)及[独立架构检查](architecture-final.log)绑定最终源码：87 TUs、1996 APIs、24407 edges、21 callbacks；21 manifest、25 ownership、16 census、19 intrusion 门通过。API 净 +6 为 paid Data/state 构造与 deleter、排序 lookup/comparator 和私有 extent 投影；改签名替代旧入口，无上层生产改动、新业务阶段或新 retry 队列。checker 同批删除原 QHash 形态假设，检查原 paid TransactionMap；ratchet 门限字节一致。

原始失败全部保留。build-02 字段名错误、build-03/04 未导出测试端点在最终修正；working-05 冷配置断言、working-06 退休观察时序、working-10/11 parent cache 断言各有日志。working-08-all、working-10-all、working-11 和 working-12 的 x86 压力失败暴露真实共享预算拒绝；working-13 首次全通过但仍含临时 allocator 诊断，只有去诊断并加强实际拒绝断言后的 qualified 结果取得本批资格。中间 build/source/runtime checkpoint 单独保存；没有完整 source checkpoint 的早期编译错误仅作诊断记录，不充当最终资格。architecture-stale/working-obsolete-contract 日志也保留，最终只更新容器合同和 source checkpoint，没有放宽门限。

当前结论见 [92 §16.54](../../92_br1_m6_m8_execution_baseline.md#overlay-storage-delivery)和 [NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)。commit facade、descriptor/configuration indexes、外部 Qt oracle/注册/诊断/Transition 输入、其他 wrapper/bootstrap/控制本体/runtime 固定成本与完整永久压力尾出口仍在原 CP1；CP0、CP5 job 接续、TSAN、公平和 BR1-PERF 无新增资格。
