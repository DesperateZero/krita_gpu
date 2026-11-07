# S01 首批开发验证：提交结果与 undo 登记

本证据对应 [92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:474) 的部分实施，日期 2026-09-27。它不代表 S01 全链闭合或 M6/M7/M8/BR1-PERF 通过。

## 源码与实际运行身份

- 基础提交：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。
- 实测工作树补丁：[source.patch](checks-02/source.patch)，SHA256 `f39366a7998f21372b3076cd48c249f6338070b456dd2b612c818912d8c31986`。这是未提交修改的身份，不把 HEAD 单独当作实测源码。
- [identity.json](checks-02/identity.json) 记录 CMake、编译数据库、实际 image dylib 与 11 个测试 binary 的 SHA256；[manifest.json](checks-02/manifest.json) 记录命令、架构、起止时间、退出码和 QtTest 总数。
- CPU 构建为 `RelWithDebInfo`、`x86_64;arm64`，Vulkan foundation 关闭。固定 `KIS_BR1_SEED=12345`，运行环境和目标列表写在 [run_checks.py](run_checks.py)。运行结束再次确认源码补丁相同、构建无待完成工作。

## 本批验证范围

`testRejectedCommitIsRetryable` 覆盖普通 undo adapter、post-execution adapter、带结果的 command transfer 三个入口。第一页已 seal，第二页仍持有真实 writable iterator；连续两次提交拒绝时检查：事务仍由原 owner 持有、未标记 finished、undo 栈为空、interstroke end command 未创建/执行。释放 writer 后提交成功，两页 undo/redo 内容正确；重复调用 data 终结入口不重复运行 end command。

`testPainterRetainsRejectedTransaction` 覆盖 Painter 的旧 void completion 包装：拒绝后保留事务，释放 writer 后可重试并正确 undo。额外修正 `saveNewDefaultPixel` 在重试时覆盖指针而泄漏旧缓冲的问题；本次没有运行单独的堆泄漏检测器，不能用上述语义测试冒充泄漏探针。

## 结果

| 检查 | 实际结果 |
|---|---|
| arm64：7 个 PageStore 目标 + painter / TileDataStore / DataManager / Transaction | 1,495 passed，0 failed，0 skipped |
| x86_64：同一目标矩阵 | 1,495 passed，0 failed，0 skipped |
| 总计 | 2,990 passed；按 QtTest 报告汇总，含 init/cleanup 与参数化行 |
| 架构门 | 通过；21 manifest、21 ownership、16 census、1,467 API、13,730 reverse edges、19 intrusion files |
| 调用图工具自测 | 6 passed |
| 结束时构建检查 | 无待构建工作；源码补丁与开始时一致 |

原始日志均保存在 [checks-02](checks-02/manifest.json)。通过判定要求测试进程退出 0、报告 0 failed，且日志无 `SAFE ASSERT` 或 `FAIL!`。资源插件探测、颜色配置和 swap 路径告警仍保留在原始日志，没有删去。

## 失败与重跑原因

首次新增三行 retry 测试的 arm64 定向运行通过，原始记录为 [transaction-retry-arm64-01.log](transaction-retry-arm64-01.log)；它早于最终新增的 Painter case，不与最终矩阵混算。

[checks-01](checks-01/manifest.json) 构建成功，结构检查因源码 checkpoint 和反向调用图指纹过期而失败，未进入 Qt 测试矩阵。审查本批结果接口后，按仓库工具重新生成调用图和源码 checkpoint；[生成日志](callgraph-generation.log)与[刷新日志](source-checkpoint-refresh.log)保留。刷新前后 `ratchet` 完全相同，没有放宽计数或外部侵入上限。之后在新目录运行 checks-02，没有覆盖失败日志。

## 尚未证明的范围

旧 `endAndTake/revert` 和 parent-attached command 的失败迁移、析构 purge 的隐式提交、直接 abort 的像素/索引/default/offset/frame/selection/interstroke 恢复、job/stroke scheduler failure sink 均未闭合。begin 失败、真实分配异常及所有提交准备故障点也未由新增用例穷举。

本批未运行新的 Vulkan、TSAN、真实 install allocator probe、产品 stroke replay 或正式性能比较；现有测试内 benchmark 输出不授予性能资格。M5 固定证据不覆盖本工作树的新行为，其他阶段及完整 V01 要求继续以 92 为准。

重跑命令：`python3 docs/vulkan_gpu_design/evidence/br1_s01_20260927/run_checks.py checks-03`（在 workspace 根目录执行；目录必须不存在）。每次运行前重新核对当前代码、目标注册和审计产物，不拿旧补丁哈希证明新修改。
