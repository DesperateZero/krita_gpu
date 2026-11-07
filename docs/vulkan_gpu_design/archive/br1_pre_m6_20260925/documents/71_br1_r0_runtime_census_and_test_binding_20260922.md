> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R0 compatibility runtime census 与测试绑定（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**R0 第二切片已落地；运行时兼容路径盘点已冻结，静态收口结果见 72。**

本文继续执行 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) M0 与
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R0。它只增加冷路径统计、审计清单和测试证据，
不改变 PageStore 写入权限、publication、retirement、handoff 或 zero-copy 语义。

## 1. 新增兼容路径 census

`KisTiledDataManagerPageStoreBackend` 新增 `KisPageStoreCompatibilityCensus` 快照。所有字段都在 backend
现有 control-plane mutex 下更新；它们不参与 close eligibility，不授予 capability，也不进入像素内循环原子路径。

| 路径 | operation/page | live/peak | terminal/fallback |
|---|---|---|---|
| legacy tile lease | attempt、generic read/write、native write | live/peak lease | success/cancel/fail、reject |
| anonymous transaction | request、start、client join | live/peak client | success/cancel/fail、reject |
| backend writer admission | attempt、acquire/release | live/peak claim | conflict、wait |
| iterator boundary | register/unregister、probe/hit | live/peak boundary | balanced unregister |
| tile refresh | attempt、success | 不适用 | success/fail |

`KisTiledDataManagerTest::testPageStoreCompatibilityCensus` 验证本轮代表路径的增量和守恒关系：

- lease attempt = 三种 created lease + rejected lease；
- created lease 全部进入唯一 terminal，测试结束时 live lease 为 0；
- anonymous transaction request/start/join/success 成对，live client 为 0；
- writer claim acquire/release 成对，live claim 为 0；
- iterator register/unregister 成对，probe/hit 可区分；
- tile refresh attempt = success + failure，当前成功 workload 不产生 failure。

## 2. 机器可读 runtime map

新增：

```text
krita/build-tools/ci-scripts/pagestore-audit/runtime-census.json
```

它把全部 17 个 intrusion manifest 项唯一映射为 11 个 runtime group，并分别记录 operation、page、live、peak、terminal、
fallback 维度、指标来源、代表性测试和证据说明：

| 状态 | 分组数 | 含义 |
|---|---:|---|
| `instrumented` | 5 | 本轮新增 compatibility census，入口与 terminal 直接计数 |
| `existing` | 4 | 复用现有 session/mutation/history/retirement/diagnostic 指标，不重复加计数 |
| `static-proven` | 1 | physical-exclusive gate 已由 Clang graph 证明 production caller 为零 |
| `deferred` | 1 | Vulkan provider 在 BR1 fail-closed，生产 runtime 路径延后到 BR3 |

retirement 双队列此前只存在于 ownership matrix，本轮补入 manifest：
`BR1-PS-STORE-RETIREMENT-017`，绑定 `pendingRetiredReplicas`、`readyRetiredReplicas`、
`pendingRetiredBytes` 以及 debt/budget/close-drain 测试。

architecture checker 现在额外保证：

1. 每个 manifest 项恰好被一个 runtime group 覆盖；
2. census 状态、六个统计维度和指标来源具有合法 schema；
3. `instrumented`/`existing` 分组必须有实际 counter 和代表性测试；
4. manifest `failure-tests` 与 census `representative-tests` 引用的方法必须真实存在；
5. `static-proven` 只允许用于 graph 已证明生产路径不可达的项目；`deferred` 仍是显式缺口，二者都不能用不存在的 counter 冒充覆盖。

## 3. Vulkan fail-closed 证据

新增 `KisVulkanFoundationContractsTest::pageProviderFailsClosedBeforeBr3()`。它验证未配置 provider 不暴露 provider identity，
不宣称同步操作，并使 read、write、retire 全部返回失败。测试目标显式编译 provider implementation，使这条 manifest
failure test 不再只是设计阶段占位名称。

## 4. 验证结果

本轮运行：

```text
python3 build-tools/ci-scripts/check-pagestore-architecture.py
bash build-tools/ci-scripts/check-vulkan-architecture.sh

kis_tiled_data_manager_test testPageStoreCompatibilityCensus
kis_tiled_data_manager_test testPageStoreCancelledPrivateClient \
  testPageStoreIteratorFixedView testPageStorePixelOperationConcurrent

ctest --test-dir _build-br0-cpu --output-on-failure \
  -R 'libs-image-(KisPageStore|KisCompletionRegistry)' -j2

ctest --test-dir _build-br0-cpu --output-on-failure \
  -R '^libs-image-tiles3-kis_tiled_data_manager_test$'

KisVulkanFoundationContractsTest
```

结果：

- PageStore architecture：17 manifest、12 ownership fact、11 runtime group，检查通过；
- Vulkan architecture：通过；
- compatibility census：3/3 通过；
- cancellation/iterator/concurrency 定向集：19/19 通过；
- 完整 tiled data manager test：1/1 通过（43.99 s）；
- PageStore/Completion 核心测试：7/7 通过；
- Vulkan foundation contracts：14/14 通过。

测试环境仍报告既有 swap 目录不可写并使用系统临时目录；不影响断言和结果。

## 5. R0 静态证据接续

[72](72_br1_r0_reverse_callgraph_and_closure_20260922.md) 已完成本文件当时保留的静态缺口：

1. 输出每个 PageStore public/private API 的 production caller 与 test-only caller；
2. 保留 overload USR、template/specialization、dynamic call、macro callsite 与 address-taken registration；
3. 将全部 manifest 项绑定到 graph，并对未解析 callback fail closed；
4. 证明 `BR1-PS-PHYSICAL-GATE-015` 没有 production caller，但因 ownership `split` 和测试失败契约仍在，裁决为
   `quarantined`、非 D0；
5. graph 与 census 已同时通过 architecture gate，R0 关闭。

这不删除 Tile/backend compatibility state，也不授权 metadata replacement 或 backing handoff。下一步只能按 69 的顺序进入 R1
`DefaultStorage -> RetirementQueue -> HistoryCollector -> ReadCoordinator -> PublicationCoordinator`。
