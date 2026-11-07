# BR1 共同安装与交付协议收敛记录（2026-09-29）

本批从读取选择冻结点继续，收束 API 映射 §4/§5 的结构子项：packed/cursor 共用一次安装政策，原 batch/execution 以互斥交付结果传递。**JP6 页/manager bounds 的整体观察窗口仍开放；真实 direct stroke、默认启用、资源/性能与 M6–M8 尚未完成。** 当前裁决见 [92 §16.11](../../92_br1_m6_m8_execution_baseline.md#adapter-delivery-convergence)。

## 实际改动与调用者

- backend 导出头新增嵌套 move-only `OperationDelivery`，用栈上 variant 移动原 batch/execution；`writeOperation/writeBytes/runCpuMutationOperation` 的独立 `completedBatch/completedExecution` 输出及旧签名删除。history 原 worker 安装后显式 finish；遗弃沿原失败/取消，错误线程 finish 不消费；standalone 已 seal，原 admission 到 gate 和适配存储释放后归还。
- 两条 manager 生产 caller 共用 `PreparedTileUpdates::install`；原重复的 bridge/cache/extent 循环删除。actual touched 不含删除，故删除这两条路径的 presence buffer 准备和二次全局查询；clear/copy/remove 原查询不受影响。
- 生产三个文件 +92/-77，净增 15 行；两个测试文件迁移签名、明确查询次数，并增加 history 实际寿命验证。新增一个导出头类型及五个成员，不能报告成“API 总数减少”。无新 manager/Tile 字段、friend、session、write set 或 TLS。保留原 prepare、pixel、install、release 锁序，不在 Store gate 内加入外部 callback。
- [编译图摘录](delivery-callgraph.json)确认 `writeOperation` 的唯一生产 caller 为 `KisTiledDataManager::writePageStoreOperation`，`writeBytes` 的唯一生产 caller 为 manager 同名函数；其余直接使用来自测试。类型的两个生产构造点对应两条路径，finish 的生产消费来自 cursor/history 安装。公共 painter/Tile 接口不变；完整 OFF 配置资格没有借此取得。

原始文件保留在 [before-source.json](before-source.json)，实际增量见 [源码与测试补丁](production-and-tests-increment.patch)及[规模清点](increment-stat.json)。不是通过重命名隐藏旧实现；原参数名已无源码消费者。

## 同源验证

产品 HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`；含六个未跟踪源码的差异 SHA-256：`40ecb952fbc6a0a19bd9047b839be3a11e097f92b7cc6c01717e44d1d37addaa`。不能仅用 HEAD 代表本批。最终 [20 目标矩阵](checks-02/manifest.json)、[库/配置身份](checks-02/identity.json)、[124 文件源码清点](source-inventory.json)互相绑定。

| 验证 | 结果与范围 |
|---|---|
| 20 产品目标 × arm64/x86_64 | 9,336 passed / 0 failed / 0 skipped；包括原 manager、mutation、resident/read、painter、transaction、调度、stroke completion、iterator、dab queue 等；不是正式 Vulkan/OFF/TSAN/M8 资格 |
| 交付聚焦回归 | 199 passed / 0 failed / 0 skipped；原准备拒绝、legacy 冲突、presence/extent、成功/失败/no-op 与新增 history 移动/遗弃/异线程拒绝均保留 |
| 结构检查 | 87 TUs、1,815 indexed APIs、19,635 edges、17 callbacks；21 manifest / 25 ownership / 16 census / 19 intrusion 通过；manager 25 identifiers / 3 includes 上限未提高 |
| 构建/工具 | 工具自测通过；最终实际 Ninja no-op；最终源码身份与检查开始一致 |
| 原整体窗口探针 | 每架构 44 场景、172 观察；raw 违例 0、控制错误 0；manager extent 仍有 32 个不一致点，`--require-converged` **仍返回 3**，未改断言换通过 |
| 暖 getter allocator | 每架构 16,384 次，无分配/释放/capture/generic request；正对照产生 1 次分配 / 8,210 B |
| 原 adapter allocator | 每架构 192 次 install allocations/frees 均为 0；144 次暖准备均为 0，48 次冷准备实际分配；cursor/packed/history × bpp 1/4/8/16 × K 1/9/65/257。仅证明受测区间，不外推整链零分配或有界尾延迟 |

矩阵 [checks-01](checks-01/manifest.json)的最终冻结被拒绝：启动时 source.patch 早于审计 baseline 刷新完成，仅 baseline-source.json 不同，产品代码没有在测试中改动。完整原记录和[拒绝原因](checks-01-rejection.json)保留；在刷新完成后完整重跑 checks-02 作为最终证据，不覆盖旧结果。初次构建启动的工作目录/日志路径错误发生在 Ninja 执行前，后续 build-01/build-02 为实际构建日志。

重跑入口：[run_checks.py](run_checks.py)、[run_read_probe.py](run_read_probe.py)、[run_install_probe.py](run_install_probe.py)；已有目录/日志不能覆盖。probe 身份文件保留源码、库、allocator interposer 和命令。最终[验证结果](validation.json)与[文档检查](document-check.json)同时核验身份、调用者、删除对象、运行结果、活动链接/锚点/行号边界。

## 文档统一与下一交付

[API_CONVERGENCE_MAP §11](../../br1_modification_guide/API_CONVERGENCE_MAP.md#adapter-delivery)给出实际函数替代、保留能力及 bounds caller 静态分类；[CODE_INDEX](../../br1_modification_guide/CODE_INDEX.md#api-convergence-index)按文件反查；[清点 §14](../../br1_modification_guide/CONVERGENCE_CHECKLIST.md#adapter-delivery)与 NEXT_EDITS 对齐已改/待改。operation storage、hash consumer、publication 指南的旧 presence 和独立输出描述已同步修正；157 处原源码引用随本次变动重定位，见[映射](source-link-remap.json)。

下一必交付结果：同一选择下闭合 page/bounds/adapter；迁移需要固定源范围的实际读取/复制 caller，同时保留 working bounds、pending/intent、frame/offset/default 和修改扫描语义。原整体探针、删除/default 控制通过后，立即进入有限真实 direct stroke 的 owner/display/finish/cancel/drain，接线时同步删等价 owner/结果分支。已收束的 selector/交付不再重领；不新增底层泛化作为无限前置。
