# HX6：迁移存储拒绝与 HX8 TileDataStore 交付

本批对应 [HX6/HX8 已实施子范围](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#hash-migration-storage-implementation)。[92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)继续维护唯一阶段状态；stroke → undo → context 的优先级不变。

当前源码为 HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09` 加工作树差异 SHA-256 **`e809ed039190e4bbc0a6b653653b67325d2761de666bb580a2dbd3e347b73830`**。包含既有未提交改动，无提交／分支切换。**完整矩阵未通过：8,891 passed、1 failed、0 skipped；超时导致该进程另有 4 项未执行。** 54 个最终探针通过，但不覆盖这一未解决失败。

## 代码与所有权

- Table/Migration 的实际存储检查容量、溢出和 malloc 返回。Table 内实际 QWaitCondition 构造失败释放原始块；未发布候选拥有自己的目标表，源表只在发布时附着。
- overflow finisher 先完整准备后继，再转交全部源表和部分目标表。失败保留当前迁移、通知同 job 的 retry revision；工作者退出和重试接手的 load/CAS 失败路径均以 Acquire 观察已完成复制。
- get/erase 解析现有 source/destination，复制完成以 Release 发布 Redirect。旧 migration 的源指针不因所有权转交而改写，原 QSBR 保护继续存在；读取、删除不再为帮助迁移申请存储。
- 静止 iterator/析构枚举并清理部分迁移。空 hash 的 cell 也可能已 Redirect，insertOrFind 返回前必须处理这一状态，不能把安装分配推迟到 payload 改变后。
- TileDataStore 注册候选由 RAII 持有到真实 map 安装成功；注册拒绝释放候选、恢复编号并归还 reservation。swap-in 在原 iterator→swap 写保护内先准备实际 cell；拒绝返回 false 且保留 SSD chunk。成功仍返回原 read pin。GC update 位于原 iterator/swap gate 释放之后。

## 新增验证与观察边界

| 场景 | 实际证明 |
|---|---|
| 六个 Qt 场景 | 部分迁移下 get/erase/iterator、连续 overflow、真实 hash 部分迁移析构、Redirect 空 cell 准备、非法容量和同 job 唤醒 |
| map allocator 扫描 | 每架构 44 次实际拒绝、3 个正控制：初始 Table 两点，完整迁移链 21 点分别走重试与直接析构；逐点核对旧值和实际 allocation ledger，析构无新增分配且记录内块全部释放 |
| 部分迁移读／删 | 每次拒绝后验证 256 个原 key，删除 7 的倍数后剩 220 个；get/erase/iterator 审计区间零分配／释放 |
| 实际并发等待者 | 在后继准备处一次拒绝，4 个实际迁移参与者继续完成，所有值保留；TLS ledger 不统计这些 worker 上全部分配，完整泄漏证明来自前述顺序扫描 |
| TileDataStore 五种入口 | 默认创建、整行创建、普通复制、已 pin 复制、swap-in 各 9 个 map 实际分配点拒绝，共 45 次/架构，加 5 个正控制；原计数、memoryMetric、reservation、旧字节和锁责任保持，重试成功，最后跟踪块为零 |
| swap-in 顺序 | map 拒绝时 SSD chunk begin/size 保持；恢复后字节正确，成功返回的 read pin 可正常释放。无 observer 的受测场景中，数据变 resident 后没有新的 allocator 调用；不外推全部 observer 或 swap-in 无分配 |

## 中间记录与修正

初始构建／定向测试／探针均保留。store 初始探针一次漏传调用参数而编译失败；随后密集表夹具找不到已 Redirect 的空 cell，提前退出并报告未清理夹具对象。后续夹具经真实迁移形成 512-cell 稀疏源表后，通过实际 allocator 拒绝建立可测状态，未修改生产故障分支。

`graph-01.log` 保留错误参数调用。`checks-01` 因最终内存序复核而主动中断；`final-01` 的 54 个探针虽然全部通过，也只属于 CAS 失败 Acquire 修正之前的中间源码。最终证据必须使用 `checks-02`、`final-02`，不覆盖旧记录。[中断说明](interrupted-intermediate-runs.json)仅列出本批终止的矩阵 runner 和其子测试。

## 下一段与未取得的资格

HX6 的跨 job key/结构预留、HX7 原 manager/table incarnation 与候选寿命、OP6/OP7 联合发布仍未闭合。现有排他 swap-in 区间的 cell 准备不能推广到跨任意像素 kernel 的长期 token；不能持整表 gate 穿过绘画来获得安装保证。

失败的部分迁移仍可能保留到下一次 writer 重试或静止析构；独立维护、真实共存峰值收费和清理时间预算继续。此次真实 payload 探针使用 1 BPP、关闭背景 pooler/swapper，覆盖 map 拒绝而非全部 payload／预克隆／池 allocator 故障。当前配置 lock-free ON；OFF、TSAN、Vulkan、完整业务与正式 stroke 性能未由本批取得。M6/M7/M8 与 BR1-PERF 继续开放。


## 最终同源码观察

| 记录 | 结果与未闭合项 |
|---|---|
| [完整矩阵](checks-02/manifest.json) | 20 个 Qt 目标 × arm64/x86_64，44 条记录；8,891 passed、1 failed、0 skipped。ARM64 的 stressTestExtentsColumn 在 300 秒超时后 SIGABRT，后续四项未执行；runner 保留失败并继续其余目标／架构 |
| [54 个最终探针](probes-manifest-02.json) | 前序 50 项重新绑定最终源码／库，新增两架构 map/storage 与 store/storage；全部通过。identity 保存命令、环境、探针／interposer／binary／动态库哈希 |
| [调用图](graph-03.log)、[结构门](baseline-02.log) | 87 TUs、1,794 APIs、18,809 edges、17 callbacks；21 manifest、25 ownership、16 census、19 intrusion，187 个 dirty source/build 文件；未放宽 ratchet 或布局限制 |
| [源码与二进制一致性](evidence-scope.json) | 失败矩阵与 54 探针所用源码／库一致；git diff --check 及实际最终 Ninja no-op 通过。matrix_passed=false，失败没有被过滤 |
| [文档检查](validation.json) | 只核对修改 ID、源码／片段、反向索引与真实结果；通过文档检查不等于矩阵通过 |

## 未解决的 extent 锁等待

[原失败日志](checks-02/arm64-kis_tiled_data_manager_test.log)、[3 秒连续采样](hung-extent-column-02.sample.txt)与 [LLDB 全线程／对象状态](hung-extent-column-02-lldb-locks.log)保留现场。8 个 worker 中 7 个停在 extent read lock，1 个停在 add 的 write lock；主线程等待线程池。该场景索引 18–20，capacity=256，没有触发本批 map/migration 或 extent 容量准备。不能据此排除所有早先状态破坏，仍须明确根因。

同源码的[单独 extent 场景](extent-isolated-arm64-01.log)通过。只链接 QtCore 的三个独立程序也未复现：读写切换 40 轮、计数增删 200 轮、对象生命周期竞争 10 轮。它们是补充诊断，不能取消完整矩阵中的失败；命令、实际 QtCore 与 binary 身份见 [独立诊断记录](qt-diagnostics-identity.json)。

Qt 上游确有 [private 状态发布修复](https://github.com/qt/qtbase/commit/80d01c4ccb697b9d390cc0da49c2f111b19b4c5b)和 [QTBUG-142321 弱内存序修复](https://github.com/qt/qtbase/commit/4fd88011fa7975ce64d5648698a234f85bac359c)，后者说明 ARM64 release 下可能全部 worker 阻塞。当前运行库标识为 Qt 6.8.0，源码路径与观察相符；**尚未通过本地原库／修复库对照确认本次根因**，没有替换依赖或给测试加豁免。

下一步在隔离构建中核对实际 QtCore 源码/补丁身份，复现上述场景并做上游修复前后对照；同时排查本地 extent 锁使用和更早的内存破坏。修复后重新完成所有原目标，再恢复完整工作树资格。不得用重复运行中某一次通过替代根因和失败关闭。

[代码增量](map-migration-storage-code.patch)、[指南增量](guide-update.patch)、[源码链接迁移](source-link-remap.json)分别保存实现和定位变化。复核冻结事实：

```sh
python3 /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_map_migration_storage_20260928/finalize_evidence.py
python3 /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_map_migration_storage_20260928/validate_guides.py
```

这些脚本核对失败仍被记录，绝不把它改成通过。重跑矩阵／探针须使用新目录或标签，不能覆盖证据。独立诊断初次编译的头路径和 Qt slots 宏冲突已在探针中修正，未改变产品源码。
