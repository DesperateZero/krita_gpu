# BR1 基线需求、API 可靠性与首个代码证据（2026-09-19）

> 状态更新：本文是 BR1 初始切片记录；其中“尚未完成”只描述当时状态。51 已关闭功能/正确性 cutover，但
> 2026-09-20 审计验证了本文对 reference `QVector` 热路径风险的预警，BR1 整体以 **BR1-PERF** 重开。当前计划见
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)。

本文记录 BR1 开始时对完整阶段需求的反推、公共接口修正和 `PS-SM0` 首个可构建基线。它是执行证据，不替代
[25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md) 与
[33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md) 的权威语义。

## 1. BR1 整体基线必须同时成立

BR1 不是“先做一个 GPU cache API”。关闭 BR1 前必须形成以下一条完整链：

```text
Krita logical tile identity
-> SurfaceId + LogicalPageId + Generation
-> exact read/write request
-> move-only lease
-> provider replica + completion validation
-> Prepared generation
-> immutable multi-page ImageEpoch commit
-> tiles3 iterator/COW/memento/swap facade
-> CPU pixel parity and injected-failure evidence
```

因此施工顺序固定为：

1. `PS0/PS-SM0`：记录现有 tiles3 行为，冻结 identity、transition 和不变量。
2. `PS-SM1/PS1`：分片 metadata、completion queue、dedup、immutable epoch root、CPU RAM replica。
3. `PS-SM2/PS2`：把 COW、oldData、undo/redo 映射到 generation retention，不另建 undo。
4. `PS3`：把 `KisTileDataStore/KisSwappedDataStore` 收口为 RAM/SSD provider，不保留双写真相。
5. `PS4/PS5`：iterator/accessor facade 全量接管，CPU 对照与故障矩阵通过后才令 PageStore operational。

Vulkan replica、SubmissionCoordinator 和产品 canvas 均不属于 BR1 首个基线；它们不能提前成为 canonical authority。

## 2. 接口审计发现的问题与决定

| 审计问题 | 风险 | 已采用的基线决定 |
|---|---|---|
| `PageRange` 可含多页，但 request/lease 只暴露一个 `version()` | 多页不同 generation 时语义不可定义，容易观察半提交 | acquire/resolve 固定为单页原语；region facade 组织多个 request，多页可见性只由共享 epoch/transaction 保证 |
| 默认 move 的 write lease 不会清空源对象 | 一个 writer token 可被两个看似有效的对象持有 | read/write lease 均禁止 copy；显式 move constructor 使源失效，并禁止 move assignment 覆盖未释放 capability |
| request/lease/writer/operation 使用裸整数或没有 identity | 无法区分重试、迟到完成和重复 release | 分别使用 typed `RequestId/LeaseId/WriterToken/OperationId`，不允许跨角色混用；消费 move-only lease/access 的入口按值接收，确保调用边界实际 move 并使原 capability 失效 |
| replica 只有 provider/allocation 数字 | provider 重建或 slot 复用产生 ABA，旧 completion 可能误命中新对象 | identity 固定包含 provider id、provider epoch、allocation slot、allocation generation 和 exact PageVersion |
| provider 可自行产生无关联 operation | PageStore 无法证明回调属于它发出的 intent | provider API 接收 PageStore 分配的 operation id，并在结果中回显；id/epoch 由 provider 注册实例暴露 |
| provider 只有 allocation handle，domain 也不区分 UMA 的 CPU/GPU consumer | PageStore 无法构造 lease，UMA 可能把 pointer 与 binding 需求混淆 | `AccessRequirement = domain + kind`；provider 增加 move-only、lease-scoped `resolveAccess/releaseAccess`，SSD 禁止直接 consumer resolve |
| provider 用 domain 加全局 CPU/GPU bool 声明能力 | 会隐式形成并不存在的 domain×access 笛卡尔积，错误选择 UMA/VRAM allocation | capability 改为精确 `(domain, access kind)` 集合；SSD 只声明 durable storage domain；同时提供 UMA CPU/GPU view 时必须声明 shared backing |
| replica copy 与 PreserveContents COW 初始化共用无类型 transfer | 要么错误拒绝 G→G+1，要么放宽后允许跨 generation 污染 | transfer 显式区分 exact-version materialization 与 write-generation initialization；`prepareWrite` 接收 WriteMode |
| handoff/retirement 有 begin 但没有失败终态，`retire()` 也不回显 operation | provider 错误会永久占用 pin/operation，迟到完成无法归属 | 增加 handoff/retirement failure transition；retire 返回带 caller operation id 与 completion 的 operation result，可失败、重试并拒绝 stale callback |
| backend-neutral completion 仅凭同源更大数值放行 | CPU/IO job 可乱序，后一个 ticket 不证明前一个 operation 完成 | 通用 PageStore/metadata/binding publication 必须精确匹配 reservation ticket；只有显式 timeline-only 组件可解释 `completedThrough` |
| published cache 可能被逐页更新误当作多页线性化点 | save/undo/read 可看到混合 generation | committed ImageEpoch immutable root 是唯一线性化点；单页 state transition 只是 root switch 后的 generation-qualified cache |
| BR0 文档仍保留“未重放 upstream”旧快照 | 阶段口径冲突 | 执行序列已改为 BR0 closed，并明确 BR1 started/not complete |

## 3. 本次落地范围

`KisPageStoreTypes` 已增加：

- `KisPageReadView` 四种互斥 selector；
- typed request/operation/writer/lease/provider/epoch/allocation identity；
- 单页 exact request 结果；
- domain/capability 分离的 `AccessRequirement`、精确 consumer capability set 与 provider access resolve/release 边界；
- move-only read/write lease；
- `PreparedPageSet` 与 `ImageEpochSnapshot` 的重复 PageKey 拒绝。

`KisPageStateMachine` 已从 fail-closed 空桩演进为确定性单页 transition core，覆盖：

- read lease acquire/release；
- writer reserve/resolve、`BeginPublish`、producer success/failure、`CancelPending`；
- materialization begin/complete/fail；
- authority handoff success/failure；
- lease/pin 安全且可失败重试的 retirement；
- Prepared → Published 与 abort；
- transition 前后统一 invariant validation，拒绝路径返回原状态。

本切片完成时，`KisPageStore` 只更新了可靠 API 形状并保持 `isOperational() == false`。这是当时的刻意门禁：尚未把
`KisTileData` 作为 RAM replica，也没有 immutable ImageEpoch root 和真实 lease release owner，不能报告成功。

当前 `KisPageStateSnapshot` 的 `QVector` 布局是 deterministic reference/contract representation，不是已冻结的热路径
metadata ABI。`PS-SM1` 可以把 production record 改为分片内 compact index/persistent handle，并用 adapter 调用同一
transition decision/invariant core；不得另写一套宽松状态语义。进入 tiles3 热路径前必须补 metadata bytes/page 与
transition latency 基准，避免把 reference copy 成本固化为长期负担。

2026-09-20 校正：该条件当时没有形成 cutover 硬门禁，初始 production epoch commit 实际仍包含完整 manifest 的
`QHash` rebuild、`QVector` export 和 sort，成为数量级退化的组成部分。当前代码已接入结构共享平衡 persistent root、
sparse/dense changed-page commit、retained-root 复用和 history delta restore/purge；history capture 不再导出 owning manifest。
但实现仍位于名为 `KisImageEpochReferenceModel` 的 owner 中，公共 `KisImageEpochSnapshot` 仍以 owning `QVector` 表达完整
导出，也尚无独立 production cursor ABI 和完整 K/N sweep。因此只能记为 P4 部分完成，不能称 production layout 已冻结
或 BR1 整体结清。53 的历史检查点还存在 transaction start 仅取 epoch 却导出完整 snapshot、rollback/rollforward adapter
全量 rebuild index、删除 extent 扫描 manifest。后续 D2-A 已以 `beginCurrentTransaction()` 消除第一项（55），后两项仍待
解决；“root 局部更新”不能推出产品操作整体 O(K)。最新状态见 52，历史归因见 53/54，新阶段与固定工作量证据见 55，
同步 prepared metadata publication 的一次消费/revision/先安装后发布契约与局部慢化复验见 56；生产布局和免全局锁路径仍未结清。

## 4. 当前测试证据

CPU-only 构建目录：`krita/_build-br0-cpu`。

```text
cmake --build _build-br0-cpu --target KisPageStoreFoundationTest -j4
_build-br0-cpu/bin/KisPageStoreFoundationTest -maxwarnings 100
Totals: 19 passed, 0 failed
```

新增验证覆盖 deterministic lifecycle、writer conflict、发布中取消/producer failure/abort 保持旧 published、
materialization/handoff/retirement failure、stale operation/provider epoch、allocation ABA、read lease 阻止 retirement，以及 512 步固定
seed 的接受/拒绝序列不变量；另覆盖同 transaction 连续 generation 只提交最新值、read selector 互斥、
manifest/prepared-set 重复 PageKey 和 UMA access kind。

Vulkan foundation 兼容性复核：

```text
cmake --build _build --target KisVulkanFoundationContractsTest kritavulkanoffscreen -j4
_build/bin/KisVulkanFoundationContractsTest -maxwarnings 0
Totals: 13 passed, 0 failed
_build/bin/kritavulkanoffscreen.app/Contents/MacOS/kritavulkanoffscreen
checksum=32896
```

该复核只证明 backend-neutral API 变化没有破坏 BR0 foundation，不表示 Vulkan PageStore 已启用。

同时复跑 BR0 冻结的 CPU/OpenGL 稳定套件及新增 reference suite 7/7（transaction、stroke、strokes queue、PageStore
foundation、PageStore reference、tiles3 data manager、frame cache）、`check-vulkan-architecture.sh`、内外层
`git diff --check`，均通过；shader asset 二次构建为
`ninja: no work to do.`。

## 5. 下一基线的强制入口条件

下一步进入 `PS-SM1/PS1` 前，不再修改上述 identity 语义；允许补实现，但若改变以下任一项必须先更新权威文档和
反例测试：

- 单页 acquire/lease 与多页 ImageEpoch transaction 的职责分界；
- PageStore 分配 operation/writer/lease identity；
- provider epoch 与 allocation generation 的双重 ABA 防线；
- 每个异步 begin 都有 success/failure 终态，provider operation 回显 caller identity；
- capability 只按精确 `(domain, access kind)` 匹配，不推导隐式组合；
- rejected transition 不改变状态；
- Prepared 不对普通 committed reader 可见；
- CPU/SSD/Vulkan provider 都复用同一 transition validator。

上述下一切片的 reference baseline 已于同日落地，证据见
[47_br1_ps_sm1_epoch_metadata_evidence_20260919.md](archive/br1_pre_m6_20260925/documents/47_br1_ps_sm1_epoch_metadata_evidence_20260919.md)。下一步转为
CPU RAM provider adapter、PageStore owner ledger 与 snapshot retention。该独立 CPU facade 后续也已完成并通过接口
复核，见 [48_br1_cpu_owner_api_correction_20260919.md](archive/br1_pre_m6_20260925/documents/48_br1_cpu_owner_api_correction_20260919.md)；其 operational
状态仅适用于手工 adopt 的隔离 facade。在通过现有 tiles3/COW/default/extent 对照前，不修改 tiles3 的 pointer/lock
热路径，也不宣称 production cutover 或 BR1 完成。
