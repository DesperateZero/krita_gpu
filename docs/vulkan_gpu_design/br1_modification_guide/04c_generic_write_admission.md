# 04c：通用写请求、lease 与失败终结修改单

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。本篇将 **S09/T6 必要记录准入**在通用写入口上的剩余工作拆到具体代码段，联动 S01 失败责任、S06 共同写计划和 S10 实际收费。设计依据为 [92 §2–§6、§10.5–§10.6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)；阶段状态仍只由 92 管理。

核对对象：2026-09-28 已检出工作树，HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`，含未提交实现。**GW1–GW7 表示完整修改责任；本批已接线的节点/异常/终结边界与仍待实施的预算、内部故障范围见 §6。** 它们是原 S09 的子项，不增加顶层修改 ID。相邻读侧已经前移必要记录的边界见 [04a §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#read-storage-admission)。

## 1. 为什么改，以及与 stroke 优先级的关系

修复前 [write resolve](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3756)先将请求设为 Resolving，锁外取得 provider access，再构造 `ActiveWriteRecord` 控制块并插入 `activeWrites`。最后两步仍有实际分配；provider 调用也没有本层异常恢复。本批已有写侧独立真实 allocator 反例：首分配拒绝后 threw=1、pending=1、active lease=0。修复后必要节点前移，并按 §5 建立同源码双架构证据；结果与剩余边界见 §6。

目标是让必要记录先于可写能力准备，失败后原请求仍可重试或取消，已经产生的写入/退休责任始终有原 owner 承接。它支持 stroke 压力失败与退出收敛；收益首先用必要分配位置和生命周期证明。**native resident pending 热路径继续直接借用原 entry/binding，不引入 generic request、lease 或全局索引。** 此项本身不宣称连续 dab 提速，真实 stroke 性能仍由 S02–S05、V01 证明。

## 2. 源码段 → 目标行为 → 联动终点

代码链接定位函数/类型入口；“段界”指出实际修改范围，避免将整份文件都视为重写对象。行号漂移后先按符号重定位。

| 子项 / 角色 | 当前代码与段界 | 具体改法 | 必须联动的终点 |
|---|---|---|---|
| GW1：主改，请求实际存储 | [acquireWrite](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3479)，`writeRequests.emplace` 至 `prepareWritePlanLocked`；[原索引](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:731) | 保留“请求节点先于共同计划”的已有顺序，改为可报告分配拒绝的实际 node 准备。准备失败时撤销本次 page claim/preparation activity，不产生悬挂 Preparing，不开始 provider 工作。共同计划后更新已有节点，不用可能补插节点的 `operator[]`。 | [releaseGenericWrite](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:699)、[activity 计数](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1847)；各所有权转交点只归还一次。activity/admission 更早的实际存储准备现见 [S02 第三批：实际准入与寿命](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-implementation)，其资格独立于请求节点探针。 |
| GW2：主改，lease 控制块与索引 | [ActiveWriteRecord](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:97)、[resolve](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3756)，状态改为 Resolving 之前及 provider 返回后的安装段 | 在取得 pin 前预构造控制块与原 active index 的真实节点。record 可用 `optional<KisReplicaAccess>` 延迟接入 access；返回后只 noexcept move 构造 access、插入预备节点、交付 lease、消费原 request。 | 析构、`finishWrite` 和 abort 对 access 的有效性检查一起迁移。未交付的候选不计作 active lease；实际 pin 不能因候选析构漏放或重复释放。 |
| GW3：主改，锁外 provider 与身份复验 | [resolve](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3756)，`locker.unlock()` → `resolveAccess` → 重新查找请求；对照 [cancel(request)](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3856) | 对约定的可恢复存储异常先恢复 owner gate，再把原 Resolving 恢复为 Pending；失败不消费请求。解锁后不得保留迭代器。resolve 与 cancel 核对同一组 request 身份：transaction/base/write/writer/access/mode/readiness，以及传入 completion 的终态。返回的有效能力若不被接纳，必须锁外归还 provider。 | provider 保证抛出前未转交无主 pin，或自行撤销；PageStore 不猜测无法取得的 access。重复/篡改 token 被拒绝，合法原请求不受影响。 |
| GW4：主改，写准备异常 | [acquireWrite](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3479)，`prepareFreshReplica`、`initializeFreshReplica` 锁外段与 `rejectAllocation/rejectPrepared`；联动 [共同计划](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1472) | 区分“尚无私有 writer”和“已取得 writer/已完成 handoff”的清理。provider 准备异常先重入 owner，再处理原 request、预算与 claim；已取得私有写责任走原 cancel/retire，取消拒绝则保留原记录交事务 abort。审查共同计划每条异常路径的锁状态与安装边界。 | [prepareFreshReplica](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1668)、[initializeFreshReplica](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1712)。不得用宽泛 catch 后 Fresh fallback 重放已发生的 retag、fill 或像素操作。provider 内部部分分配仍由 provider 自己回收。 |
| GW5：联动，终结与关闭 | [finishWrite](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:4095)、[preparePublicationAbort](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:368)、[closeSession](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2839) | 保持 lease 释放到终结期间的原 activity/admission。发布失败且 cancel 被拒绝时，保留已消费 access 的 active record，abort 沿原记录重试。更换容器后逐个核对 find/erase/遍历、析构顺序与统计。 | [cancelWriteLocked](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:489) → 原 metadata/descriptor → retirement → 原预算归还。Preparing/Resolving、已交付 pin 与终结债务分别阻止不合法的 abort/commit/close，不能以 active pin 数量为零推定债务清空。 |
| GW6：联动，provider 与预算 | [kisAcquireCpuBindingAccess](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp:351)、[kisReleaseCpuBindingAccess](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp:373)；[S10/W1–W8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04b_budget_waiter_implementation_map.md) | 复用已前移的 provider active-leases 登记，补通用写 caller 的消费/释放验证。请求 node、控制块、active node 的预备及保留容量接原 budget，统计 reserved/live/released；不得只 reserve bucket 或只报记录数。 | provider index 只管理物理访问，PageStore 原索引只管理通用请求/lease。两者不互相替代；已有 payload RAM 收费不能重复计算。新增硬预算接线未完成时，明确保留 S10 未闭合边界。 |
| GW7：验证与结构索引 | [TestProvider](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:39)、[genericWriteLifetimeBlocksCommit](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:2355)、[genericPreparationProtectsTransactionBeforeRequest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:2396) | 在现有真实 PageStore + provider fixture 上加准备失败、resolve 重试/取消、锁外并发增长与退出场景，具体断言见 §5。生产代码不加入只供探针使用的第二份记录。 | [state-ownership](/Users/apple/krita_gpu/krita/build-tools/ci-scripts/pagestore-audit/state-ownership.json)、[V01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/07_validation_and_migration.md)：字段/容器变更后更新同一 owner 的清单、调用图与真实源码身份。 |

## 3. 数据结构与安装顺序

优先沿用读侧 [resolveLocked](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReadCoordinator.cpp:380)已经采用的方式：将原 `writeRequests/activeWrites` 换为可报告分配失败的节点容器；active 节点在临时同类型容器中准备后提取，最终转入**原** active index。临时候选只有短寿命存储，不持有第二份事务 authority。

本批已使用 `std::map<quint64, ...>` + node handle；要求相同 allocator、不会抛出的 key 比较、ID 不重复。`reserve()` 并不准备独立节点；无序索引即使准备了节点，也必须证明解锁期间其他请求增长不会使最终插入 rehash。不要在 pin 已到手后补 reserve。改为树索引的 O(log L) 冷路径成本需要测量，不能把结构正确性当性能收益。

```text
owner gate：校验原 Pending request / exact completion
  → 准备 lease 控制块 + active index 实际 node（拒绝则 Pending 不变）
  → 原 request 标记 Resolving；拷贝短寿命身份；释放 gate
provider：准备物理访问记录 → 获取 writable pin → 返回 access
owner gate：重新查找并复验原 request
  → noexcept 接入 access → 转入预备 node → 消费 request → 交付 lease
后续：原 finishWrite / cancel / transaction abort → retirement / budget
```

`KisReplicaAccess` 的 [move 构造为 noexcept、move assignment 被删除](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageReplicaProvider.h:151)，因此使用原地构造，不为方便赋值而放宽其单次消费约束。预备对象归还和 provider release 不在 owner gate 内执行外部 callback；失败路径与成功路径都检查析构位置。

## 4. 失败位置 → 状态 → 唯一终结者

| 发生位置 | 对外结果与保留状态 | 后续责任 |
|---|---|---|
| request node 准备拒绝，尚未进入写计划 | 本次 acquireWrite 明确失败，没有可交付 request | 原 scope 归还本次 preparation/page claim；已有其他请求及事务不受损。 |
| lease 控制块 / active node 准备拒绝 | resolve 返回无效 lease，原请求仍 Pending，未取 pin | 调用者可用同一合法请求重试或 cancel；不要求重放 acquireWrite/像素操作。 |
| provider 在能力转交前报告失败或抛出约定存储异常 | owner gate 恢复；请求回到 Pending | provider 清理内部未交付资源；PageStore 保留原逻辑写责任。其他异常按 provider 契约处理，不静默吞掉编程错误。 |
| provider 返回后身份复验拒绝 | 不交付 lease；实际返回的 pin 锁外归还 | 依据原请求实际状态处理，不能随意 erase 不再属于本次 resolve 的记录。 |
| Fresh 初始化失败，已建立私有 writer | Failed；沿原 cancelWriteLocked 取消 | cancel 成功才清除原请求/claim；cancel 拒绝则原记录留下供 abort 重试。 |
| lease 消费后发布失败，detach/cancel 暂时拒绝 | 无成功 completion；保留已消费 lease 的终结债务 | `activeWrites` 原 record + transaction abort；不得退回可再次执行像素的 Pending。 |
| close 遇到 Preparing/Resolving/已交付 lease/未结债务 | 关闭不成功，保留可继续终结的状态 | caller/原 abort/retirement 完成各自责任后重试 close；不强删 map 冒充归零。 |

这张表规定终结归属，不承诺内存拒绝后已有自动重试调度。必要通知、派发、终结容量与压力 continuation 继续按 S09/T6、S10 接线。

## 5. 验证与完成判据

| 场景 | 需要证明的结果 |
|---|---|
| request、控制块、active node 的真实 allocator 拒绝 | 每个失败点有实际命中证据；旧像素和其他请求不受损；本次计数、claim、pin、reservation 有唯一归属。与 metadata/provider 内部分配分开标记覆盖范围。 |
| provider 准备 / 初始化 / resolve 的受控异常 | 锁能重新进入，无卡住的 Preparing/Resolving；按上表分别 retry、cancel、abort、close；已发生的 fill/retag 不被第二条写管线重放。 |
| 取得 pin 后暂停，同时让其他 key 的 257 个请求/lease 增长 | 返回后不依赖旧迭代器或预留 bucket；安装无新增分配，已有 lease 仍有效；并发 commit/abort/close 不越过原 activity。包含 0 个已有 lease 的控制。 |
| Fresh 与已具备的 CPU recoverable 子集，1/4/8/16 BPP | publish/cancel 两端正确；旧 exact 读、同 key 竞争、重复 resolve/cancel、篡改 token 均受约束；取消后的旧 G 仍从合法 before 读取。 |
| lease 已消费但 cancel 被拒绝 | 不能提前释放 admission；abort 后续沿同一记录收敛；完成后 pending/active/control、provider pin 与预算匹配，最终 close 成功。 |
| native 与业务性能控制 | native warm pending 不进入 generic index；重跑实际零分配区间，另测 generic cold resolve 成本。真实 stroke、Fresh 回退及正式性能门使用 V01/92 的同源码对照，不能由零分配推定速度。 |

本批已保留写侧旧行为反例、实施 GW1–GW3 并同步适配 GW5，补充 GW4 的共同计划/Fresh 准备/初始化调用边界。后续继续 GW4 各内部存储与 producer 异常责任、GW6 实际收费和 GW7 完整压力/性能资格；节点前移的局部证据不关闭这些剩余项或 M6–M8。

交付记录必须回填：实际修改符号、异常覆盖区间、残留 caller、测试命令、源码/二进制身份、故障样本和性能控制；正向更新 [CHANGE_MAP](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/CHANGE_MAP.md)，反向更新 [CODE_INDEX](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/CODE_INDEX.md)，资格只写入 92。

<a id="write-admission-implementation"></a>

## 6. 本批实现、验证与剩余代码责任

证据见 [S09 第九批](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s09_write_admission_20260928/README.md)。下表描述实际完成的调用边界；上文 GW 表仍是完整契约。

| 子项 | 已落地源码 | 已验证边界 / 尚需实施 |
|---|---|---|
| GW1 | [acquireWrite](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3479) | std::map 实际 request node 在共同计划之前准备；真实节点拒绝不遗留 claim/request，已有 0/257 requests 保持。更早的 activity/admission 现已接 [S02 第三批：实际准入与寿命](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-implementation)；metadata 内部存储故障仍继续。 |
| GW2–GW3 | [resolve(write)](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3756)、[ActiveWriteRecord](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:97) | 控制块与 active node 先于 pin，optional 原地接入 access；bad_alloc 后重新入 gate 并保留 Pending。完整 request 身份以及返回 access 的 mode/replica/lease/operation 均复验，不匹配的有效 pin 锁外归还。 |
| GW4 | [prepareWritePlanLocked](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1472)、[acquireWrite](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:3479) | 共同计划清理先检查 locker.isLocked，锁外析构后恢复 gate；generic 捕获三类准备调用的 bad_alloc。已经取得私有 writer 的初始化失败沿原 cancel，拒绝则保留 request 供 abort。provider 自身部分分配、metadata/descriptor/ledger 内部与整个 finishWrite 的故障资格仍开放。 |
| GW5 | [finishWrite](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:4095)、[preparePublicationAbort](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:368) | 原 activity/admission 与 consumed-record 重试责任保持；close 继续拒绝存活 capability/债务。预算阻塞与恢复通过真实原 reservation/retirement 路径验证。 |
| GW6 | [reserveBacking](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1582)、[W1–W8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04b_budget_waiter_implementation_map.md) | provider 已有登记复用；本批没有为原 request/control block/map node 接全局/metadata 硬预算。必要通知/派发/retry/pass 存储与实际容量收费继续。 |
| GW7 | [准备拒绝、同请求重试/取消/abort](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:2110) | 24 项：四 BPP × Fresh/recoverable × 三种终点。 |
| GW7 | [锁外并发增长](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:2157) | 8 项：四 BPP × Fresh/recoverable，257 个其他 request/lease 在 pin 已取得时增长。 |
| GW7 | [准备调用异常](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:2216) | 12 项：共同计划、Fresh provider 准备和初始化调用边界。 |
| GW7 | [初始化失败与退休预算阻塞](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:2242) | 4 项：原 fallback reservation、取消拒绝、无请求 capability 下的 abort 责任。 |
| GW7 | [返回能力失配](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:2299) | 16 项：mode、replica、lease id、operation 失配的真实有效 pin 归还。 |
| GW7 | [请求身份一致性](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:2325) | 4 项：每项检查七个篡改字段，合法原请求随后仍能 resolve。 |

每架构新增 68 项用例；17 目标双架构 **6,264 passed，零失败/跳过**。每架构新 write request / resolve allocator 探针分别 4/9 区间、2/7 次实际拒绝；post-pin 两区间分配尝试为零。其余 15 组探针按原边界重跑，36 次 final 与矩阵 image 相同。冷 generic 索引为 O(log L)，真实 stroke 与 Fresh 回退性能未新增资格。

**继续实施：** GW4 的内部故障/producer 部分资源责任、GW6 必要容量准入及全局/metadata 收费、S09 通知与拒绝后自动接续、T4 整轮预算仍未闭合。M6 全资格、M7/M8、S02–S05、undo/context 和正式 BR1-PERF 继续。
