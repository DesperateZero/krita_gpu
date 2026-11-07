> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R0 Clang reverse-call graph 与 containment 收口（2026-09-22）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**R0 完成；没有项目满足 D0 删除门槛。下一步允许进入 R1，但 M1–M7、backing handoff 与 zero-copy 仍未开始。**

本文完成 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) M0 与
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R0 的最后一项静态证据，并承接
[70](70_br1_r0_containment_and_layout_gate_20260921.md) 的 source/layout ratchet 和
[71](71_br1_r0_runtime_census_and_test_binding_20260922.md) 的 runtime census。

本轮没有修改 PageStore publication、write authorization、retirement 或 backing 所有权语义；它只建立可重复的静态图、
把裁决接入 architecture gate，并关闭 R0。

## 1. 生成器与冻结产物

新增：

```text
krita/build-tools/ci-scripts/generate-pagestore-callgraph.py
krita/build-tools/ci-scripts/pagestore-audit/reverse-callgraph.json
```

生成命令：

```sh
cd krita
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py \
    --compile-commands _build-br0-cpu/compile_commands.json \
    --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py
```

生成器读取真实 compilation database，保留原编译器、defines、include path、language mode 与目标参数，只移除 object/dependency
输出并追加 `-fsyntax-only`、临时 `-index-store-path`、`-index-ignore-system-symbols` 和 `-index-ignore-pcms`。临时 object 名按 TU
路径哈希隔离，因此不会覆盖构建产物。宏没有被忽略。

当前冻结环境：

| 项目 | 值 |
|---|---|
| 编译器 | Apple clang 17.0.0 (`clang-1700.6.4.2`) |
| target | `arm64-apple-darwin24.6.0` |
| compile database | `_build-br0-cpu/compile_commands.json` |
| compile database SHA-256 | `f998a66029561fdf8723fd0b540af74e98d731908f11485cde1c9fdec13837cf` |
| IndexStore | Xcode `libIndexStore.dylib` |

## 2. TU 闭包与图语义

生成器不是按文件名硬编码测试集合。它从 `libs/image` 和 `libs/vulkanbackend` 的 compile commands 出发，递归解析仓库内 include
闭包，选取 PageStore implementation、直接出现 PageStore 类型的 TU，以及传递可达 PageStore 的 TU。当前结果为：

| 选择原因 | TU 数 |
|---|---:|
| PageStore implementation | 31 |
| 直接 PageStore identifier | 15 |
| 传递 include 可达 | 33 |
| 合计 | 79（production 56，test 23） |

IndexStore 共给出 533 个仓库内 source/header record。图以 Clang USR 为 identity，因此同名 overload 不会合并；每个 API 记录：

- declaration 与 definition 的 path/line/column；
- production caller 与 test-only caller；
- dynamic/virtual 和 implicit call 标记；
- specialization/override relation；
- address-taken callback registration 及其 containing/calling symbol。

namespace/global initializer 没有函数 caller 时使用明确的 `<translation-unit-initializer>` synthetic caller；它仍保留源位置，
不算未解析边。address-taken API 如果没有 containing/calling symbol 则进入 `unresolved-edges`，生成器与 CI checker 都 fail closed。

当前冻结图：

| 指标 | 值 |
|---|---:|
| PageStore public/private function/method USR | 1,122 |
| reverse-call site | 11,434 |
| 至少有 production caller 的 API | 755 |
| 至少有 test caller 的 API | 516 |
| dynamic call site | 501 |
| specialization/override relation | 315 |
| address-taken callback registration | 0 |
| unresolved call/callback edge | 0 |

callback 数为 0 表示当前 PageStore API 没有 address-taken registration，不表示检查被省略；今后首次出现该模式时必须产生可解析
registration，否则 graph generation 和 architecture gate 都会失败。

## 3. manifest 与 CI 绑定

`reverse-callgraph.json` 为 17 个 intrusion manifest entry 各保存一个 binding：source record 是否被索引、该路径声明的 API USR，
以及可匹配的冻结 caller symbol。`KisVulkanPageReplicaProvider` 不属于 CPU compile database，且在 BR1 保持 fail-closed；它是唯一
`deferred-outside-cpu-compile-database` binding，并且只能因为 runtime census 状态为 `deferred` 而通过。其 BR3 前失败行为仍由
`KisVulkanFoundationContractsTest::pageProviderFailsClosedBeforeBr3` 约束。

`check-pagestore-architecture.py` 现在额外验证：

1. graph schema、milestone、API USR 唯一性与计数一致；
2. compile database path/hash 与 `baseline-source.json` provenance 完全一致；
3. 每个 declaration、definition、caller 和 callback source location 指向现存 inventory 文件及合法行号；
4. test/production caller 分类与路径一致；
5. 每个 manifest entry 恰好有一个 binding，非 deferred source 必须已被索引；
6. callback 必须有解析后的 container，`unresolved-edges` 必须为空；
7. physical gate 的 API、caller count、ownership fact、manifest status 和 runtime disposition 彼此一致；
8. allowlist 外任何新的 `tryAcquireExclusiveWrite()` production 使用都会破坏 quarantine gate。

CI 的 `pagestore-architecture` job 继续只读冻结产物，不在无 compile database 的轻量 job 中重新编译。修改 graph 边界时必须在
具备 compile database 的构建目录重新生成，再由只读 checker 审核结果与 provenance。

## 4. physical-exclusive gate 裁决

`BR1-PS-PHYSICAL-GATE-015` 的索引结果：

| 条件 | 结果 |
|---|---|
| `tryAcquireExclusiveWrite()` production call site | 0 |
| test call site | 20 |
| address-taken registration | 0 |
| ownership fact | `BR1-OWN-PHYSICAL-ALLOCATION` |
| ownership status | `split` |
| manifest status | `quarantined` |
| runtime disposition | `static-proven` |
| D0 eligible | 否 |

零 production caller 关闭了 71 中“文本扫描不是证明”的缺口，也允许把旧门放入隔离态；但它不等于可删。按照 69 §9：

- `KisCpuResidentBinding physical claim` 与 provider allocation record 仍共同写 physical allocation owner；
- 20 个测试 callsite 仍直接表达 alias、pin、revocation、provider destruction 和并发 claim 的失败契约；
- replacement owner 尚未具备等价的 live/peak/budget/drain 可观测性；
- BR1 没有 production runtime route，因此不能伪造 runtime counter 来满足删除条件。

结论是 `retain-until-R3-provider-owner-unification`，不是 D0。架构检查只允许 declaration/definition 留在
`KisCpuResidentBinding_p.h/.cpp`，禁止新的 production caller 重新出现。

## 5. R0 完成判定

69 R0 要求的六类产物现已全部冻结：

| R0 产物 | 证据 |
|---|---|
| source inventory | `baseline-source.json` |
| intrusion manifest | `intrusion-manifest.json`，17 项 |
| reverse-call graph | `reverse-callgraph.json` |
| ownership matrix | `state-ownership.json`，12 facts |
| runtime census | `runtime-census.json`，11 groups |
| architecture ratchet | `check-pagestore-architecture.py` + CI job |

manifest 的 `containment_status` 已设为 `r0-complete-no-d0`。本轮没有任何项同时满足 production caller、唯一事实、测试、runtime、
replacement observability、guard 与一里程碑 quarantine 七个删除条件，所以删除量为 0；这与 69 的保守预期一致。

## 6. 验证

本轮执行并通过：

```text
python3 -m py_compile \
  build-tools/ci-scripts/generate-pagestore-callgraph.py \
  build-tools/ci-scripts/check-pagestore-architecture.py

python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py
```

architecture 输出为：17 manifest entries、12 ownership facts、11 runtime census groups、1,122 indexed APIs、11,434 reverse-call
edges、21 frozen external intrusion files，检查通过。生成器重复运行后的 JSON SHA-256 必须保持一致；这项确定性检查作为本轮最终
收口验证执行。

## 7. 下一步边界

R0 完成后，下一步只能开始 69 R1 的无语义职责拆分，首项是 `DefaultStorage`，随后依次为 `RetirementQueue`、
`HistoryCollector`、`ReadCoordinator`、`PublicationCoordinator`。每次只搬一个 owner，并保持结果、锁序、统计和 failure contract
等价。

2026-09-22 后续：R1 五项提取均已完成。前两项见
[73](73_br1_r1_default_storage_extraction_20260922.md)、[74](74_br1_r1_retirement_queue_extraction_20260922.md)，其余三项及 R1 收口见
[75](75_br1_r1_history_read_publication_extraction_20260922.md)；当前顺序位置为 R2/M1 authoritative metadata records。

以下工作仍未获授权：

- 68 M1–M4 metadata 表示替换；
- 68 M5–M7 write unification、recoverable/commit-only handoff；
- zero-copy 或 bounded-memory 性能资格；
- 删除 physical claim、Tile/backend compatibility state 或其他未满足 69 §9 的项。
