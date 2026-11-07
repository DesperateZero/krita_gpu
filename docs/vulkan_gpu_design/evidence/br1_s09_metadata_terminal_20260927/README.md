# S09 第五批：原地读保护终结与 metadata 容量归还

本批落实 04a §11 的单次 ReleaseRead / verified AcknowledgeLastUse 消费原 slot；mixed sequence 保持原子投影安装。实际阶段状态只由 [92](../../92_br1_m6_m8_execution_baseline.md)管理。

## 修改与验证范围

- 原 metadata owner 在 shard gate 下复验 exact identity、publication claim 和 revision；ReleaseRead 无 ticket 摘除原节点，有 ticket 将原节点移至链尾并转换，保持 reference 中 ticket 的顺序。已验证 acknowledge 清除同 replica 上全部匹配 ticket；普通 owner 入口仍拒绝未验证 acknowledge。
- 不再复制版本、准备新 arena/index 存储或导出快照。成功推进 revision，旧 publication 候选失效；诊断分别计局部 transition、节点访问、slot 复用和释放，不虚报版本安装。
- erase 只检查被摘节点所在的块；空块沿既有 intrusive ownership 链转移，保留一个暖块，reservation 未终结时保留已准入容量。payload 先销毁再归还 charge，释放链改为迭代析构。该批证明 shard 外析构，**尚未证明外层 store owner gate 外的全部销毁或整轮字节/时间上界**。
- macOS 探针发现原回收线程 TLS 标志首次读取会分配。改为既有单 worker 的活动作业身份；捕获在标记清除前析构，前台新线程不被误认，job 结束后没有可复用的陈旧 thread ID。没有新增调度队列或 metadata authority。

## 证据

- 修复前两架构各 18 个满容量终结反例全部拒绝（`metadata arena budget is exhausted`）；见 `counterexample-*.log` 与 binary/library 哈希 `counterexample-identity.json`。生产前态来自 `before-source.json`，测试入口是 `metadataReadProtectionAtCapacity`。
- 新增 68 case / 架构：18 个满容量用例、48 个 reference/身份/顺序/重复/mixed-sequence 用例、实际空块/预算/保留 reservation、worker body/capture/前台及 drain 后重建。定向最终各 72 passed（含已有候选失效与 arena 用例），见 `focused-fix-03-*.log`。
- 初次探针 `install-arm64-cleanup-01.log` 的 32 B TLS 分配失败保留；`cleanup-02` 为修复后的中间观测；最终资格使用 **cleanup-03**。每架构 42 个区间都在新建、未预热的前台线程上执行，期间真实 reclaimer 保持活跃；allocations/bytes 为零，10 次实际 block free 与 arena 变化相等。这里允许并核对真实释放，不声称 frees 为零。
- 五组既有探针每架构 96 / 72 / 28 / 96 / 31,080 区间，allocations/bytes/frees 全零，分配正控制均有效。12 次最终探针均与完整矩阵的 image dylib 相同。测量端点及编译/链接命令见每个 `install-*-identity.json`；不外推为整条 read-release/通知/retirement 零分配。
- 最终 **17 目标 × 2 架构：5,934 passed，0 failed/skipped**；结构门 1,636 APIs / 16,231 edges / 15 callbacks，21 manifest / 24 ownership / 16 census / 19 intrusion；6 项工具自测通过，intrusion ratchet 未改。
- `fix-build-02.log` 保留新增 arena fixture 误用 pointer 参数的编译失败；`fix-build-03/04.log` 保留修正与 TLS 改动后的构建。最终构建、所有命令、seed、逐目标日志、源码 patch、binary 哈希和结束 dry-run 均在 [checks-01](checks-01/identity.json)，没有跳过失败记录。

源码身份：HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09` + 完整工作树 patch `ff6e867d3bf4bc84f20549f64f130d127567a22a06e781aa051feb2c159bdf02`；image `58b4b139b32486684d9f7238eb56441a0d1297b1be1bfd61627cf41f45d02d91`。五文件手工增量见 `incremental.patch` / `incremental-review.json`；调用图和 inventory 为另行生成的审计产物。未提交源文件仍由 run_checks 完整冻结。

## 继续实施

T5 的 claim/其他拒绝后原记录接续，T6 的通知/派发必要容量、S10 共享与实际 metadata 计账仍开放。T4 的单次 removeAll 可以随保护节点数增长；shard 外 block 销毁仍可能位于调用者的 owner gate 内，须继续完成外层销毁预算和有界执行。未新增完整 claim/revision 耗尽故障矩阵、Fresh 2% 回退、真实 stroke、Vulkan、TSAN 或 BR1-PERF 资格；S02/S03/S04/S05、M6 全出口、M7/M8、undo/context 及完整目标继续。

函数对应见 [04a §12](../../br1_modification_guide/04a_retirement_wakeup_implementation_map.md#metadata-terminal-implementation)，下一批按 [NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md)领取。
