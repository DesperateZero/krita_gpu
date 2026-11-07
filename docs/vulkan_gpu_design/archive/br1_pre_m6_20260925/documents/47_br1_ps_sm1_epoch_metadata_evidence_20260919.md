> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 PS-SM1：ImageEpoch、分片 metadata 与 fake CPU provider 证据（2026-09-19）

> 状态更新：本文是 BR1 中间切片记录；其中“尚未完成”只描述当时状态。51 已关闭功能/正确性 cutover；
> reference manifest 不得进入 production 的条件尚未落地，BR1 已以 **BR1-PERF** 重开，见
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](52_br1_cpu_fast_path_optimization_plan_20260920.md)。

本文记录 [46_br1_baseline_api_reliability_20260919.md](../../../46_br1_baseline_api_reliability_20260919.md) 之后的下一代码
切片。当前关闭的是 `PS-SM1/PS1` 的 reference baseline，不是 BR1、PS1 或真实 tiles3 cutover 完成声明。

## 1. 本切片解决的风险

首个 PS-SM0 状态机只能证明单页 generation transition。若直接接 `KisTileData`，仍有三类未闭合风险：

1. 多页 transaction 逐页更新 published cache，reader/save 可能看到混合 generation；
2. 同一个 materialization 被多个 reader 重复生产，或 completion 入队前失去逻辑 reservation；
3. provider 的完成乱序、失败、重启和 retirement 失败只有接口描述，没有可执行的无 I/O 证据。

本切片分别建立 immutable ImageEpoch reference model、sharded metadata/completion owner，以及 test-local fake CPU
provider。三者仍与产品 PageStore 保持 fail-closed 隔离。

## 2. Immutable ImageEpoch reference model

`KisImageEpochReferenceModel` 保存不可变 `KisImageEpochRootSnapshot` 历史：

```text
EpochRoot(N)
  previous = EpochRoot(N-1)
  commitSequence
  sorted PageKey -> exact PageVersion manifest
```

当前 manifest 使用 Qt implicit-sharing `QVector` 作为确定性 COW reference representation；它不是已冻结的 production
persistent-map ABI。commit 只构造新 root，捕获过的旧 root 不被修改。

2026-09-20 production 校正：这里的“新 root”仍会重建/排序完整 vector，只证明 reference 不可变性，不满足生产
复杂度。production 必须使用 persistent root/changed-page delta；该 vector 只能留在 oracle、debug export 或 serialization。

transaction 语义：

- `beginTransaction(baseEpoch)` 只能引用仍保留的 immutable root；
- `prepare()` 记录每个 PageKey 的 before/after exact generation，同 transaction 后续 prepare 只能推进 generation；
- commit 以当前 head 为父 root，并原子安装完整 manifest；
- stale base 上修改过的 PageKey 若已变化则返回 `Conflict`，不静默覆盖；
- stale base 上的不相交修改可以按 commit sequence rebase 到当前 head；
- `TransactionOverlay` 读取 prepared after，其余页面仍解析 transaction base；普通 committed view 不可见 prepared 页面；
- abort 不修改任何 committed root。

## 3. Sharded metadata 与 completion queue

`KisPageMetadataCoordinator` 使用稳定 PageKey hash 固定分片。每个 shard 独立拥有：

- PageState snapshot map；
- materialization dedup map；
- completion event queue；
- 短临界区 mutex。

`reserveMaterialization()` 在一个 shard lock 内完成 dedup 和全局 request/proposed-operation identity 消费，但不调用
provider。producer 锁外分配 target 后，通过 `bindMaterialization()` 在 shard 内执行 `BeginMaterialize` 并绑定 logical
readiness；只有 source pin 生效后才可启动实际 transfer。公共 `apply()` 明确拒绝 materialization
begin/complete/fail，防止绕过 reserve/bind/drain。

Dedup key 固定为：

```text
(exact PageVersion, AccessRequirement, target ProviderId, target ProviderEpoch)
```

重复 request 只附着已有 operation/readiness。completion 入队后 dedup entry 继续存在，因此 late attachment 仍加入同一
producer；`drainCompletions()` 在单 shard lock 内通过同一 `KisPageStateMachine` 应用成功/失败 transition，然后一次性
返回全部 request。completion 必须同时精确匹配 operation 与 reservation ticket；不能把 CPU/IO job 的更大 ticket
误当成 timeline advance。stale、foreign-ticket 和重复 completion 均被拒绝并计数。

当前 coordinator 没有 provider 指针，也不会在 shard lock 内调用 provider、I/O、GPU queue 或 wait。跨页可见性仍只由
ImageEpoch root commit 完成。

## 4. Fake CPU provider 与故障注入

`KisPageStoreReferenceTest` 内的 fake CPU provider 实现完整 `KisPageReplicaProvider` 契约，但不进入产品运行时：

- PageStore-supplied operation id 回显；
- completion registry ticket；
- CPU allocation、write-generation transfer、按值消费的 resolve/release access 与 retirement；
- allocate/transfer/validate/retire 注入失败；
- 手动乱序完成；
- provider restart 递增 epoch，使旧 allocation/completion 失效。

测试包含 128 个 operation 的逆序完成序列，并交错成功/失败，验证 completion status 与 replica validation 一致。SSD index
故障属于后续统一 SSD provider，不由 CPU fake 伪造。

## 5. 测试证据

```text
cmake --build _build-cpu --target KisPageStoreReferenceTest -j6
_build-cpu/bin/KisPageStoreReferenceTest -maxwarnings 0
Totals: 8 passed, 0 failed

ctest --test-dir _build-cpu --output-on-failure \
  -R '^(libs-image-kis_transaction_test|libs-image-kis_stroke_test|libs-image-kis_strokes_queue_test|libs-image-KisPageStoreFoundationTest|libs-image-KisPageStoreReferenceTest|libs-image-tiles3-kis_tiled_data_manager_test|libs-ui-KisFrameCacheStoreTest)$'
100% tests passed, 0 tests failed out of 7

_build/bin/KisVulkanFoundationContractsTest -maxwarnings 0
Totals: 13 passed, 0 failed
_build/bin/kritavulkanoffscreen.app/Contents/MacOS/kritavulkanoffscreen
checksum=32896
cmake --build _build --target krita_vulkan_shader_assets -j4
ninja: no work to do.
build-tools/ci-scripts/check-vulkan-architecture.sh
Vulkan architecture checks passed.
```

内外层 `git diff --check` 同时通过。以上 Vulkan 结果只证明 backend-neutral API 变更没有破坏 foundation，不表示
Vulkan PageStore 已启用。

覆盖：

- 双页 transaction commit 前后只观察旧集合或完整新集合；
- 历史 epoch snapshot 在后续 commit 后不变；
- overlapping stale-base commit 冲突，disjoint stale-base commit 有序 rebase；
- materialization producer/attachment/late attachment 只有一个 operation；
- stale operation、foreign ticket 与 duplicate completion 拒绝；
- materialization success/failure 都通过共享状态机收束；
- fake CPU provider 的逆序完成、copy、按值消费 lease、active-lease retirement 阻断、failure injection、retire retry、
  provider epoch 重启与未完成 ticket cancel。

## 6. 仍未完成与下一入口

本 reference 切片完成时 `KisPageStore::isOperational()` 仍为 false、没有真实 RAM owner，也没有修改 tiles3
pointer/lock 热路径。进入下一切片前保持以下边界：

- reference `QVector` manifest 在 production 接线前必须替换为 persistent map，且 conflict/visibility 语义不能分叉；
- test-local fake provider 不得被注册成产品 provider；
- completion queue 只提交逻辑状态，不承担物理 I/O；
- `KisTileData` bridge 必须携带 exact PageVersion、provider epoch/allocation generation 和 lease owner；
- memento/oldData 接线必须消费后续 owner-sealed prepared proof 与 snapshot retention/release，不另建旁路 retention；
- 在真实 tiles3 接线前补多线程 shard stress、metadata bytes/page 和 transition latency 基准。

下一代码切片 CPU RAM provider + PageStore owner ledger + snapshot retention 已在隔离 facade 落地，证据见
[48_br1_cpu_owner_api_correction_20260919.md](48_br1_cpu_owner_api_correction_20260919.md)。其
`finalizeInitialization()` operational 只表示手工 initial manifest 可运行，不表示已映射 `KisTileData`。后续仍先完成
tile/COW/default/extent/iterator 对照，再逐步替换 accessor 路径；禁止双写或提前宣称 production cutover。
