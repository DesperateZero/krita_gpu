# 整体结构重构工作证据（沿用 D13 工作目录）

本目录承接D12的`D12-ProviderSourceGate`；先保留新增负例在修复前的结果，再落实与验证修改。
未完成的运行或尚未冻结的性能实验不构成资格，不能改写D12及更早封存结果。

最新要求为先整体结构重构、后统一性能测试；本轮没有运行性能配对或申请 M/K/X/E 资格。
完整工作清单、已落代码与未结项见 [67](../../67_br1_target_structure_reconstruction_20260920.md)。
QtTest 自带 benchmark/stress 的输出仅属于本次正确性回归，不用于当前版本性能判断；回归与构建有并行运行。

## 原始失败必须保留

- `pre-fix-native-source-copy.log` 是旧 binary 未识别测试名称的无效调用，不是并发缺口证据。
- `pre-fix-native-source-copy-v2.log` 才是在新增测试下复现 native copy 绕过 writer 的有效修复前失败。
- `post-fix-physical-claim.log` 的 4 个失败来自新增测试的 transfer 版本关系写错；修正为合法同 key 新 generation，
  显式断言请求有效后，`post-fix-physical-claim-v2.log` 的 20 项全部通过。
- `native-entry-tiled.log` 中旧计数要求真实写创建 generic request/default 源物化，迁移后不再符合结构目标；
  已改为核验零 generic request/default 源物化与一次 native generation/seal，不删除像素/历史断言。
- `root-index-build.log` 使用了不存在的 `kis_random_accessor_test` target；`root-index-build-v2.log` 改为实际 target。
- `native-integration-build.log` 的直接 iterator 测试错用了基类 `KisTiledDataManager*`；修正为生产要求的 `KisDataManager*`。
- `current-KisPageStoreResidentReadTest.log` 记录一项旧 cache 数量断言失败：CPU write session 现在真实 native 读取 oldData，
  retained old View 合法保留 3 个旧 binding；更新断言继续检查按需建立、旧 View 释放回收和 close 清空，最终重测另存。
- `native-iterator.log`、`native-iterators-ng.log`：缺安装 prefix，退出 134；`native-iterators-ng-v2.log`：
  已设 `KIS_TEST_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install`，但资源初始化字体缩略图路径崩溃（退出 139），未进入 QtTest 正文。
  原始系统崩溃报告位于 `/Users/apple/Library/Logs/DiagnosticReports/kis_iterators_ng_test-2026-09-20-233753.ips`。
- `shared-default-KisPageStoreResidentReadTest.log` 保留过早将局部 `Busy` 当作业务失败造成的 2 个并发失败；
  native read 增加局部 mutex/swap barrier 等待及驻留复验，仍不启动 swap-in，也不创建 generic request。
- `shared-default-KisPageStoreReferenceTest.log`、`local-gate-KisPageStoreReferenceTest.log` 保留生产并发写失败；
  `concurrent-product-1.log` 的增强诊断定位为锁外目标准备期间 default 被 reader 物化，旧空 source 授权失效。
  修复为 writer reservation 前在 owner gate 内重查 exact base；新增 provider 回调使该交错确定性复现，不以随机重测通过替代修复。
- `verified-kis_low_memory_tests.log` 虽输出 4 passed / exit 0，却含大量 `SAFE ASSERT`，明确不计为通过。
  共享 legacy wrapper 在其他线程最终 unlock，与普通 native session 的线程限制冲突；兼容层增加无活跃 guard 才可调用的 terminal seal，
  普通 session 的跨线程 beginWrite/seal 拒绝测试保持不变；修复后低内存回归另存。

## 当前正确性检查点（不是整体结构完成）

最终本轮回归使用 `checkpoint-` 前缀；12 个套件 QtTest totals 合计 306，均要求 0 failed / 0 skipped 且无 `SAFE ASSERT`：

| 测试 | QtTest passed |
|---|---:|
| KisPageStoreFoundationTest | 25 |
| KisPageStoreReferenceTest | 67 |
| KisPageStoreCpuMutationTest | 31 |
| KisPageStoreResidentReadTest | 31 |
| KisPageStorePhysicalClaimTest | 21 |
| KisCompletionRegistryTest | 11 |
| kis_tile_data_pooler_test | 3 |
| kis_tile_data_store_test | 5 |
| kis_swapped_data_store_test | 4 |
| kis_low_memory_tests | 4 |
| kis_tiled_data_manager_test | 91 |
| KisVulkanFoundationContractsTest | 13 |

上述计数含 init/cleanup，不等于独立业务场景数量。另有生产并发写 40 次重放、CPU 动态运行库确认和 architecture guard。
QtTest 自带 timing/benchmark 不是最终性能采样；完整应用级 iterator 启动失败仍未关闭。
`checkpoint-manifest.json` 记录工作树源码、构建配置、运行库、测试二进制及日志的哈希；`verify-checkpoint.mjs` 可重验。
这是 live-file 检查点，不是另建的冻结源码/二进制归档；后续代码修改应使身份校验失败，不能继续引用它代表新版本。

所有未结边界继续列在 67；没有执行最终整体性能测试，没有取得新 M/K/X/E 资格，也未宣告 BR1-PERF 结清。
