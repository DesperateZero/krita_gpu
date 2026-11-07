> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 R0 containment、source inventory 与布局门禁（2026-09-21）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

状态：**R0 containment/audit 已完成；本文件保留第一切片与布局门禁证据。**

2026-09-22 更新：compatibility runtime census 已在
[71](71_br1_r0_runtime_census_and_test_binding_20260922.md) 落地；compilation-database-backed reverse-call graph、
物理写门裁决与 R0 完成证据见
[72](72_br1_r0_reverse_callgraph_and_closure_20260922.md)。本文 §6 的缺口均已关闭；下一阶段只能按 69 进入 R1，
不能跳到 metadata replacement 或 backing handoff。

本文记录 [68](68_br1_bounded_backing_handoff_and_zero_copy_writes_20260921.md) M0 与
[69](69_br1_pagestore_decomposition_and_intrusion_audit_20260921.md) R0 的第一批实现证据。
它不修改写入语义，不删除旧 owner，不授予 backing handoff、zero-copy、bounded-memory 或性能资格。

## 1. 本轮完成内容

新增独立 PageStore architecture gate：

```text
krita/build-tools/ci-scripts/check-pagestore-architecture.py
krita/build-tools/ci-scripts/pagestore-audit/intrusion-manifest.json
krita/build-tools/ci-scripts/pagestore-audit/state-ownership.json
krita/build-tools/ci-scripts/pagestore-audit/baseline-source.json
```

并在 `.gitlab-ci.yml` 中增加 `pagestore-architecture` job。当前 gate 执行以下检查：

1. manifest schema、唯一 ID、状态枚举、路径和 symbol 存在性；
2. ownership matrix schema，以及 `canonical` fact 只能有一个 current writer；
3. PageStore 外部引用文件集合不得扩张；
4. 每个外部文件的 PageStore identifier 与 direct include 数量不得超过冻结值；
5. `KisTile` 不得新增 `m_pageStore*` compatibility field；
6. backend 不得新增 writable-page、mutation batch 或 iterator-boundary duplicate state；
7. ratchet 中的 tile/backend compatibility symbol 必须登记在 manifest；
8. TileData count、swap lock 和 `tryAcquireExclusiveWrite()` 不得越过 provider physical gate。

该 gate 是 ratchet，不是基线自动接受器。`--write-baseline` 只用于明确审查的基线更新；普通 CI 永远只读冻结文件。

## 2. 冻结 source inventory

比较点为 Krita 内层仓库：

```text
f5fbbde618df6fb4e1068ace7381c339a70dd4c0
```

当前 inventory 包含 tracked diff 与 untracked source/build 文件的并集：

| 项目 | 冻结值 |
|---|---:|
| dirty source/build 文件 | 108 |
| PageStore 外部侵入文件 | 21 |
| intrusion manifest 条目 | 17 |
| state ownership fact | 12 |

每个 dirty 文件记录 SHA-256、行数、public type、member field、container/synchronization declaration 数、include edge 与
PageStore identifier。构建输入同时记录 `_build-br0-cpu/compile_commands.json` 和 `CMakeCache.txt` 的 SHA-256；这些 hash 是本轮
本机构建配置证据，不要求 CI runner 存在相同本地路径。

## 3. ownership 结论

当前 12 类事实中，以下已经是单 writer：

- pending generation：`KisPageMetadataCoordinator`；
- read/writable pin：`KisCpuResidentBinding`；
- captured/retained exact version：`KisImageEpochReferenceModel`；
- provider operation：`KisPageOwnerLedger`。

以下仍是 `split` 或 `misplaced`，因此不能提前删除容器或开启 handoff：

- transaction lifetime；
- page writer admission；
- physical allocation owner；
- GPU/I/O last-use；
- retirement debt；
- history reachability；
- default source/materialization；
- binding/cache validity。

matrix 冻结 current writer、observer、lock/claim、creation path、terminal path 与 target authoritative owner。`split` 是待偿还债务，
不是最终允许的多 owner 架构。

## 4. M0 布局门禁

`KisPageStoreFoundationTest::layoutBaselineDoesNotGrow()` 现在报告 `sizeof/alignof` 并阻止现有大值类型在 M1–M4 前继续膨胀。
本轮 arm64/Qt 6.8 实测为：

| 类型 | sizeof | alignof | 上限 |
|---|---:|---:|---:|
| `KisReplicaHandle` | 128 B | 8 B | 128 B |
| `KisPageTransition` | 440 B | 8 B | 440 B |
| `KisPageAllocationDescriptor` | 216 B | 8 B | 216 B |
| `KisPreparedPageProof` | 176 B | 8 B | 176 B |
| `KisCpuWriteGuard` | 200 B | 8 B | 200 B |

这些是 pre-refactor 上限，不是 68 §4.2 的最终 compact target。后续类型可以缩小，不能静默增大；新的 intent/plan/claim/entry
类型出现后仍需加入各自目标上限。

## 5. 验证结果

本轮运行：

```text
python3 build-tools/ci-scripts/check-pagestore-architecture.py
bash build-tools/ci-scripts/check-vulkan-architecture.sh
ctest --test-dir _build-br0-cpu --output-on-failure \
  -R 'libs-image-(KisPageStore|KisCompletionRegistry)' -j2
```

结果：

- PageStore architecture：通过；
- Vulkan architecture：通过；
- PageStore/Completion 核心测试：7/7 通过；
- `KisPageStoreFoundationTest`：28/28 通过；
- 布局报告与 68 冻结基线一致。

## 6. R0 收口（2026-09-22）

69 要求的 runtime census、failure-test 绑定和 compilation-database reverse-call graph 均已成为机器可读 gate。
`containment_status` 已从 `ratcheted-not-removable` 更新为 `r0-complete-no-d0`：

- 17 个 manifest 项全部唯一绑定 runtime group 与静态 graph binding；
- graph 覆盖 overload、template、virtual/dynamic call、macro 展开和 address-taken registration；
- 未解析 call/callback edge 为 0；
- `tryAcquireExclusiveWrite()` 的 production caller 为 0、test caller 为 20，已进入 `quarantined`；
- physical allocation owner 仍为 `split`，因此它不满足 69 §9，也不认证 D0；本轮删除量仍为 0。

详细生成方法、计数、D0 裁决和验证结果见 72。R0 完成只解除 R1 的前置门槛；仍禁止提前进行 metadata 表示替换、
recoverable/commit-only handoff 或 zero-copy 性能宣称。
