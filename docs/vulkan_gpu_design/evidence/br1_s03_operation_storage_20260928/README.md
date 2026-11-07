# S03 / OP2：原 execution 触页位图与 changed 输出准备

日期 2026-09-28。当前设计与阶段状态以 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)为准；待改内容、具体代码段、联动 owner、失败终点与验收关系见 [OP1–OP10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#operation-storage-map)，本批落地范围见 [OP2 实施表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#operation-storage-implementation)。

## 本批改变

cursor/packed 操作不再在像素循环中向独立 QSet 插入触页键。原 `KisPageMutationExecution::Private` 持有本次借用的位图，复用已有 BoundEntry 的位置：≤64 页使用 inline word，更多页按 ceil(K/64) 准备 word，并由原 MetadataArena allocator 实际收费。已有 16-byte BoundEntry 不扩张，不复制页键，不增加权限表或一次热路径查找。成功取得原 write guard 后置位；位图随原 execution 终结。

changed 输出在范围借用和像素执行前准备为唯一 buffer，并在 Qt reserve 返回后检查实际容量。此 Qt 构建在空容器的分配被拒绝时可能保留零容量而不抛异常，因此只捕获 bad_alloc 不足以拒绝执行。callback 成功、guard 释放后，先从原绑定导出 changed，再 finish execution/batch；最终只交换已有输出，旧 caller buffer 在 cleanup 释放。失败保留原结果、owner 与取消责任，不重放像素 callback。

## 行为与故障验证

每架构新增 **161 个 case**：128 个 cursor 场景、1 个真实预算场景和 32 个 packed 场景。覆盖 BPP 1/4/8/16、K 1/9/65/257、重复/稀疏/空/拒绝、standalone/persistent、共享旧输出、partial/full/no-op、pending 与旧快照逐字节一致、失败后原 owner 重试及实际预算。真实限额场景在 8 MiB 元数据上限内拒绝超大声明范围，body 不执行，先前 pending 字节保留；允许原 range 保留已收费且可复用的容量，不要求拒绝后全部 live 字节回到原值。

新增探针与原 36 次探针共 **40 次**，均以最终库重新编译和执行：

| 探针 | 每架构结果 | 测量边界 |
|---|---|---|
| [暖路径分配探针源码](operation-storage-allocation-probe.cpp)；[arm64](install-arm64-operation-storage-allocation-final-01.log)、[x86_64](install-x86_64-operation-storage-allocation-final-01.log) | 192 次 operation 的 body、changed export、changed delivery 各自 allocation/free 均为 0；旧 QSet 方式的正控制确实分配 | 预热 resident pending 后，每次重新借用 execution 并首次触页；BPP × K × 空输出/唯一旧输出/共享旧输出 × 4 次。**不含冷 COW/materialization、finish、cleanup 或 manager 后续刷新** |
| [准备拒绝探针源码](operation-storage-failure-probe.cpp)与[一次性拒绝 interposer](preparation-failure-interposer.cpp)；[arm64](install-arm64-operation-storage-failure-final-01.log)、[x86_64](install-x86_64-operation-storage-failure-final-01.log) | 各 834 个实际注入拒绝、16 个无注入成功对照，全部通过 | 分别扫描输出准备与原范围/execution 准备的每个匹配分配，直到没有可注入的下一点；拒绝不进 body、不泄漏 reserved、不破坏旧输出共享者、pending 或 owner；随后正常重试并核对像素 |

这些结果只证明指定区间的行为和分配，不是整笔 stroke 的时间收益或正式性能资格。

## 失败记录与修正

- [checks-01](checks-01/manifest.json)保留首版独立平坦触页表的失败：重复存储页键使原 384 页、6 MiB resident 场景触及 8 MiB 元数据预算；两架构 Reference 各 1 项失败。改为原 execution 位图，384 页只需 48 字节位数据，另有固定控制对象开销；没有提高原预算。
- 同一矩阵中 Painter 各 68 项失败暴露 RangePrepare 被重复计数。初始观测改为独立 Preflight，RangePrepare 仍每 operation 计一次实际 K，没有放宽稀疏范围断言。
- [准备拒绝初轮](failure-initial-01-driver.log)、[第二轮](failure-initial-02-driver.log)保留 Qt reserve 拒绝后仍进入 body 的反例；最终代码增加实际容量检查。
- [第三轮](failure-initial-03-driver.log)至[第五轮](failure-initial-05-driver.log)及 [LLDB 定位](failure-debug-02.log)保留探针错误：持续拒绝模式也拒绝 C++ 异常运行时的分配并终止进程。最终 interposer 只拒绝一个目标分配，使异常传播可用；没有跳过产品拒绝点。[第七轮](failure-initial-07-driver.log)达到初始扫描上限，未取得全部成功对照；扩大扫描上限后[第八轮](failure-initial-08-driver.log)完成 834/16。最终双架构另行重跑，旧日志不覆盖。

## 同源码完整验证

HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含未跟踪生产/测试文件的完整源码差异 SHA-256 `fe5286f8f7140711d47f0cc918241cbcb6ba5beaf4a2b5470d88fa15daa91188`。19 目标 × arm64/x86_64 最终为 **8,560 passed、0 failed、0 skipped**；实际笔刷插件、结构门与六项工具自测通过。

[最终矩阵](checks-02/manifest.json)、[源码与二进制身份](checks-02/identity.json)、[完整源码差异](checks-02/source.patch)、[实际 Ninja no-op](checks-02/final-build-no-op.log)、[40 次探针清单](probes-manifest-01.json)和[身份复验](evidence-scope.json)绑定同一源码及 image/pigment/插件/静态库/测试/probe。 [本批七文件增量](operation-storage-code.patch)对照实施前快照；[diff 检查](diff-check.log)通过。

[调用图](graph-02.log)为 86 TUs / 1,791 APIs / 18,525 edges / 17 callbacks；[结构基线](baseline-02.log)为 181 dirty source/build files、21 manifest / 25 ownership / 16 census / 19 intrusion，未放宽 ratchet 或布局门。当前 `USE_LOCK_FREE_HASH_TABLE=ON`；未运行另一实现的构建，不能外推其资格。

## 剩余代码与阶段边界

OP1 的范围集合转换；OP3 的 presence buffer；OP4 的 wrapper、hash 插入及必要删除回收；OP5 的 extent；OP6/OP7 的原 owner publication/cut；OP8 的 fill/copy/planar/clear 旁路；OP9 的 Qt 输出完整收费、shared parent budget；OP10 的完整压力与产品性能均继续。MR4 的兼容失败 exact 字节恢复保留。

默认真实 brush 仍未传入持久 owner。BC1–BC10 的 owner/current/source/producer cut、终结、必要资源、长笔窗口以及 M6/M7/M8、Fresh 2%、Vulkan、TSAN、BR1-PERF 未因本批取得完成资格。优先级保持 **stroke → undo → context**。

[指南校验](validation.json)核对 15 项导航、30 篇指南的本地链接、源码锚点和反向索引；[首次代码重定位](source-link-remap.json)、[位图改法重定位](source-link-remap-redesign.json)、[文档行号重定位](document-link-remap.json)与[指南差异](guide-update.patch)保留关系变化。先前冻结的证据文件不改写。
