# BR1 核心提交重构：2026-09-21 工作检查点

这是正确性/生命周期检查点，**不是冻结源码归档，不授予结构完成或 BR1-PERF 资格**。
执行清单与剩余结构以 [67](../../67_br1_target_structure_reconstruction_20260920.md) 为准。
本轮未运行 M/K/X/E 性能配对；QtTest 时长、重复并发、启用 loader/observer 的运行不作为性能证据。

## 实现范围

- PageStore 事务 claim、通用写 request→lease→publish/cancel 的事务计数及首次 provider 调用前的准备 claim。
- provider proof、epoch delta、metadata 候选和 persistent root 构造移出 owner gate；安装前复验 head、retention、页 revision 和必要的页目录注册变化。
- 无冲突 rebase、lease revision/目录变化重做；真正冲突不暴露半批。没有新增全局 publisher 构造锁。
- restore 独立保留源 root，锁外准备 metadata；新增事务或 head 变化拒绝，读 lease/目录变化重做。full restore target 去重不再逐页二次扫描。
- `publicationStatistics()` 和阶段计量记录实际 candidate/retry；不是仅计最终 root 赋值。
- 测试框架增加显式 `KIS_TEST_PLUGIN_PATH`，默认安装路径不变；使用当前 build 的 shape/color 插件解除应用 iterator 启动障碍。

尚未完成：owner-issued 原位写 permit、全部生产 operation-wide read scope、完整预算回收/后台进度；
默认/删除输入组装、安装、历史清理仍有 owner 临界区，持续竞争下的乐观重做未获得固定上界或尾延迟资格。

## 复现

从 `/Users/apple/krita_gpu` 执行，源码是内层 `krita` 工作树，不覆盖已有用户修改。
构建使用 `MACOSX_DEPLOYMENT_TARGET=12`、`CMAKE_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install`：

```sh
env MACOSX_DEPLOYMENT_TARGET=12 CMAKE_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install \
  .venv/bin/cmake --build krita/_build-br0-cpu --target \
  KisPageStoreCpuMutationTest KisPageStoreReferenceTest KisPageStoreResidentReadTest \
  KisPageStorePhysicalClaimTest KisPageStoreFoundationTest KisCompletionRegistryTest \
  kis_tiled_data_manager_test kis_low_memory_tests kis_tile_data_pooler_test \
  kis_tile_data_store_test kis_swapped_data_store_test kis_iterator_test kis_iterators_ng_test \
  krita_shape_image krita_shape_paths kritalcmsengine -j6
env MACOSX_DEPLOYMENT_TARGET=12 CMAKE_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install \
  .venv/bin/cmake --build krita/_build --target KisVulkanFoundationContractsTest -j6
```

`run-checkpoint.mjs` 运行 14 个完整套件以及两类各 40 次重复并发，记录每次退出码、signal、环境和原始日志。
它拒绝覆盖既有 `run-results.json` / `checkpoint-*.log`；后续重跑应使用新的证据目录，不覆盖本检查点。
GUI 测试显式使用当前 build 的插件；NG 测试同时记录 dyld loader，校验 image 库、ImageShape、path shapes、色彩引擎均来自当前 CPU build。
应用启动扫描系统字体/测试资源的耗时不等于 PageStore pipeline 耗时；`iterator-startup.sample.txt` 是排障采样，不是性能剖析报告。

```sh
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_core_reconstruction_20260921/run-checkpoint.mjs
bash krita/build-tools/ci-scripts/check-vulkan-architecture.sh
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_core_reconstruction_20260921/verify-checkpoint.mjs
```

首次生成 manifest 使用 `verify-checkpoint.mjs --capture`，它拒绝覆盖已有 manifest。
默认验证检查当前源文件、两个 build 的 runtime/测试 binary、文档、harness、日志 SHA-256 与本检查点一致。
后续代码变化导致验证失败是预期失配，不得改旧 hash 伪装为新代码的测试证据。

## 正确性结果口径

| 套件 | QtTest totals passed |
|---|---:|
| Foundation / Reference / CPU Mutation | 25 / 67 / 44 |
| Resident Read / Physical Claim / Completion | 31 / 21 / 11 |
| tile pooler / tile store / swapped store / low memory | 3 / 5 / 4 / 4 |
| tiled data manager | 91 |
| application iterator / iterator NG | 9 / 11 |
| Vulkan foundation contracts | 13 |

合计 339，均要求 0 failed / 0 skipped / 无 SAFE ASSERT，包含 init/cleanup，不代表 339 个独立业务场景。
额外 80 个重复运行不重复计入 339；每次各为 init、所选并发场景、cleanup 共 3 totals。
Mutation 新增 13 个用例含 12 线程同时提交不同页；其余为确定性公开 API/私有诊断 phase observer 交错。
observer 不修改内部候选、不授予权限；只在文档指定锁外阶段安排 capture/read/commit/abort，关闭 observer 时无此调度行为。

## 保留的过程中间记录

- `build-cpu.log`：新增测试误用了不可 move-assign 的 `KisReadLease`，编译失败；改用独占持有 move-constructed lease。
- `mutation-preliminary.log`：上述编译失败后尚存旧测试 binary 的 31 totals，**不是新增用例通过证据**。
- `build-cpu-v3.log`：测试误调用 private retained-root API，编译失败；改用公开 capture API，不放宽生产接口可见性。
- `build-cpu-v2/v4`、`*-v4.log`、无 `checkpoint-` 前缀的回归/并发日志是中间构建的检查，不替代最终检查点。
- 前轮字体缩略图启动崩溃保留在 `br1_d13_20260920`；只配置 prefix 的安装插件目录缺少 ImageShape/RectangleShape。
  本轮没有修改字体业务源码，而是用显式测试路径加载当前已构建的插件，两套 application iterator 最终均完整运行。
- D11/D12 封存原件不修改；D13 是旧 live-file 检查点，不能将其 source/runtime hash 更新成当前值。
