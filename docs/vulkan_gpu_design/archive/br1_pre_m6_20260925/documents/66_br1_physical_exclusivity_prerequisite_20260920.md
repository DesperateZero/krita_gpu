> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D12：allocation 物理独占前置切片（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

**这是原位 permit 的物理前提，不是完整 permit，也尚未消除生产 COW。** 生产 `writeBytes()` 继续走 D11 的新 allocation
安全写段；root/capture/retention、旧版本恢复、不可失败提交与短发布仍是后续主线。不能将低层独占测试称为 CPU 性能结清。

## 1. 本轮修正的安全边界

D11 的 binding 内 writer 排他不会自动覆盖另一个 alias binding，TileData 的共享 swap pin 也只是防换出。
新增 `KisTileData::tryBeginExclusiveAccess(ownedReferences, ownedUsers)` / `endExclusiveAccess()`，由内部
`KisCpuResidentBinding::tryAcquireExclusiveWrite` 接入 tiles3；不支持该存储协议的 provider 默认拒绝。

- 用同一 `m_swapLock.tryLockForWrite()` 排除 legacy/native/generic 已有像素 pin 与 swap/pool迁移，不增加普通读的全局登记。
- refcount 的 sign bit 暂时关闭新 alias 获取。CAS 的 expected 是调用者确实控制的 owner refs，不是瞬时采样总数。
  ref 在 CAS 前增量则使未知引用阻止 claim；在 CAS 后增量则保留等待者寿命，并在 ref/acquire 返回前等待 swap gate。
  普通 ref 仍一次原子增量加慢路径判断，不为每次 read 叠加另一把锁。
- claim 自己原子取得一个额外 lifetime ref；解锁后才释放，允许 provider 撤销/销毁，避免最后引用在持有 swap 锁时销毁对象。
- 校验已知 users（0或1），清除 speculative preclone，保持驻留；新 generation 的后续 clone 不得拿到旧预克隆字节。
  非驻留只拒绝，不偷偷 swap-in。`try` 不是无等待/常数耗时的完整发布保证：clone清理、allocator、最后释放另计。
- 同线程成对释放；持有 claim 的线程不得再次 ref/acquire/pin/clone 同一对象。未来 identity/ownership 记录应提前创建。

计数参数是内部前置条件，不是可供消费者自签发的权限。future owner 必须先保护这些引用的身份与寿命，禁止未知引用替代
已知引用的 ABA；物理 gate 不保存旧 G，也不决定新 alias 应解析 G 还是 G+1，等待后仍需逻辑层精确复验。

## 2. 接入和未完成项

底层：[TileData](../../../../../krita/libs/image/tiles3/kis_tile_data.cc)、[inline ref](../../../../../krita/libs/image/tiles3/kis_tile_data.h)、
[binding](../../../../../krita/libs/image/pagestore/KisCpuResidentBinding.cpp)、[tiles3 provider](../../../../../krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp)。
测试：[PhysicalClaimTest](../../../../../krita/libs/image/tests/KisPageStorePhysicalClaimTest.cpp)。

本次只完成 physical claim 与 binding 的接入，**没有生产 PageStore 调用者**。不为了跑分跳过 D11 对新 allocation 的校验。
下一步仍是同一生产入口的纵向 permit：

1. 操作起点区分 read-view 与 mutation-base；不要额外持一个阻断独占的普通 reader。
2. 以 owner claims 保护 root/transaction/provider 与已知物理 owners，协调 legacy write-intent 自身 shared pin 移交。
   不能把读锁直接升级成写锁；竞争失败时保留安全 COW 分支。
3. 区分 recoverable-before 与 exclusive-immediate：前者保有 exact-before，后者首字节前完成全部可失败准备，之后不可普通 abort。
4. G 的旧 binding/alias 不得在 A 被复用于 G+1 后继续授权旧内容；metadata/root发布与capture复验必须闭环。
5. 再迁移其余入口、短发布、增量删除与有界回收，不以本次低层 primitive 替代最终结构。

## 3. 验证与实测

本轮构建、回归与配对数据见独立 [D12证据目录](../../../evidence/br1_d12_20260920/README.md)；D11及更早封存证据不修改。
新 PhysicalClaim **16** 项通过（Qt totals含init/cleanup）：1/4/8/16 BPP、legacy Tile读pin、generic/native读写、未知ref、
seed/provider alias、已知单wrapper、alias等待、12,000次并发ref/claim尝试、provider撤销/销毁、swap miss、最后ref和preclone失效。
并发try可以拒绝；没有从一次调度中接受的claim数量推导公平性或吞吐。等待测试也不替代capture/epoch并发证明。
Mutation17、ResidentRead28、Reference59、Foundation24、read fixture41、tiled88、native fixture34、pooler3、store5、
low-memory4、swap-store4、Vulkan contracts13及architecture guard通过。未运行GUI、sanitizer或完整native/permit并发及长压矩阵。

冻结95份生产/测试源码、D12 runtime `/tmp/br1-d12-runtime.1kuWO0`，与D11/固定upstream共424项身份hash。
Mac16,10、24GiB、macOS15.7.3，Qt6.8、RelWithDebInfo universal构建/arm64执行；候选HEAD仍为`f5fbbde618df6fb4e1068ace7381c339a70dd4c0`
加冻结dirty源码，upstream为`9a24ae0d8c`，不是实时最新主干。共同fixture源hash一致，各版本分别编译且使用自己的runtime；
**不把旧inline ref代码装进新physical claim协议**。runtime依赖本机安装与`/tmp`，不是自足归档。
low-memory/swap-store在rate采样结束后补跑，其2份源码、冻结副本、binary与日志身份另存`supplement.json`，不改写计时前identity。

两组各11桶×8对，每进程独立>=200ms，共 **352次rate运行、4次loader核验**，未与构建/回归/profiler并发。
以下为完成吞吐比（大更好），括号为进程pair探索性95%bootstrap区间；不是正式不劣性或事件尾延迟：

| 桶 | D12 / D11 | D12 / 固定upstream |
|---|---:|---:|
| write N64 K1 B4 | 0.998 [0.981–1.014] | 0.00280 [0.00277–0.00290] |
| write N64 K1 B8 | 0.981 [0.954–0.999] | 0.00306 [0.00294–0.00317] |
| write N64 K1 B16 | 1.000 [0.989–1.024] | 0.00333 [0.00327–0.00338] |
| write N1024 K16 B4 | 1.003 [0.998–1.035] | 0.00433 [0.00405–0.00452] |
| write N4096 K1 B4 | 1.047 [1.000–1.079] | 0.00248 [0.00241–0.00259] |
| read N64 K1 B4 | 1.003 [0.992–1.029] | 0.893 [0.880–0.934] |
| read N1024 K16 B4 | 0.984 [0.952–0.995] | 0.843 [0.821–0.886] |
| guard N64 K1 B4 | 1.000 [0.985–1.019] | 0.756 [0.747–0.776] |
| intent N64 K1 B4 | 1.020 [0.982–1.032] | 0.886 [0.876–0.911] |
| prebound RAM copy K1 B4 | 0.979 [0.769–1.308] | 1.007 [0.912–1.049] |
| prebound RAM copy K16 B4 | 1.054 [1.010–1.072] | 0.966 [0.936–1.028] |

K1 B8写和K16读的负偏移保留，不能宣布新增gate零成本。copy控制桶也有偏移/宽区间；实际Qt hash seed、热状态与完整后台
活动未观测，不能将偏移直接归给ref分支、布局或噪声。N4096写区间下端未四舍五入值为0.999816，不据表中1.000称全区间改善。
没有生产claim调用者，本轮不预期COW量下降；真写仅主干约 **0.25%–0.43%**，仍是待迁移的安全COW/metadata/commit管线。
M代理、预持CpuRam copy K、完整入口E独立判读，不将E-K称纯M，不将差额称跨硬件域成本。没有GPU/UMA产品测量。
本轮没有新增分段采样或claim延迟分位；D11 inclusive计时保留其版本边界，不能当作D12新锁self归因。

## 4. 反证/缺测存根

- `D12-OwnerPermit`：physical claim 尚未被 owner 生产路径消费，真实 COW/copy 数不应假定下降。
- `D12-RefCost`：普通ref路径已变化；K1/B8写约-1.9%、K16读约-1.6%。下一研究冻结相同布局/工作量的ref路径消融或更粗边界诊断，
  不能由源码存在新branch就认定其造成全部负偏移，也不能通过扩大样本直到区间有利来关闭反证。
- `D12-ControlVariability`：prebound copy K1区间宽、K16在分支对照中偏高；控制变量先有独立证据再归因，不追认环境静默。
- `D12-AliasIdentity`：引用等待只保护物理顺序，不保护 logical old-version identity；上层闭环是下一实施前提。
- `D12-ProviderSourceGate`：收尾源码审阅发现 `prepareSynchronousWriteCopy` 仍在 provider mutex 内按 allocation `activeWriter`
  检查source，再直接调用 `duplicateTileData`；该flag主要由generic lease维护，不等于native binding writer。实际复制的swap pin
  可排除本次physical claim，但源copy入口尚未与binding写门禁统一，且未来claim期间若再取provider锁可能形成锁顺序风险。
  这不是已测到的生产损坏/死锁；下一切片须先补native writer→copy/transfer/retire矩阵及source访问claim，不能仅把
  `tryAcquireExclusiveWrite` 接入owner就开放原位写。持claim线程不得调用同allocation的clone/pin或等待可能反向依赖它的操作。
- `D12-ClaimLatency`：无量化 claim/等待尾延迟、preclone清理/最后释放预算，未有 sanitizer 与完整permit并发矩阵。
- D11-K1Regression/WriteParity/PinBudget/Attribution/Compatibility/ControlResidual 仍开放；本轮不得覆盖其历史反证。

## 5. 2026-09-21 接入审阅补充（不改写 D12 检查点）

当前进展见 [67 §24](67_br1_target_structure_reconstruction_20260920.md#24-2026-09-21packed-write-原生生产入口与锁边界)：
真实 packed write 已直接消费 native mutation，与像素操作共用全范围保留、事务及私有取消，退出 legacy wrapper 写体。
它**不是** physical claim 的生产 permit 消费者。整页 discard 避免源复制，但仍默认初始化；部分 preserve 仍 COW。

本次审阅再次确认逻辑接通必须先解决的具体边界：

- `beginCpuMutation` 允许后页失败和 private cancel；history/共享匿名 client 的 seal 不是不可撤回 root commit。
  不能仅因写入 kernel 是 memcpy、不抛出业务错误，就原位修改已 Published backing。
- fixed before View 本身也是保护者；释放它不等于新捕获已被 fencing，也不证明旧 alias/root/事务/last-use 都消失。
  不能读取瞬时 ref/readers 值给自己填入 `ownedReferences/ownedUsers`。
- exclusive-immediate 要先完成可失败的分配、候选/proof/descriptor/extent 准备与保护预约，最终写入阶段不再进入普通 abort；
  否则必须保留 exact-before 恢复能力。现有 commit 仍可 retry/reject，不能写完以后调用它碰运气。
- 新 generation 需要新合法 logical binding/replica identity。共享旧 TileData 的新 owner 若是准备步骤，必须在物理 claim 之前完成；
  持 claim 时不得再对同一 allocation ref/acquire/pin/clone。旧 binding/source/legacy cache 的失效必须和新 View 捕获协调。

因此本轮保持安全 COW fallback，并以真实生产迁移、工作计数和并发旧读验证改进，而不为关闭计划项增加一个没有实际授权语义的 permit 类。
后续仍须落实本文件 §2 的完整 owner-issued 协议及并发/失败矩阵，再声明 P3 的原位写部分完成。

后续 67 §25 已用同步完整输入消除正常 packed 整页的默认填充；输入在新 TileData 注册前复制完成，不暴露未初始化 guard。
它仍是独立 backing、仍可 cancel/abort，既不复用 Published allocation，也没有消费物理 claim；原位许可的上述缺口不因此关闭。

67 §26 收紧另一个实际前提：旧 root 失去最后 snapshot/active-base 保护后立即拒绝新的历史接入，不再因后台尚未删除 registry 而复活。
当前 root 及仍受保护的历史可继续捕获；native guard 也保留自己的 View。准入/最终释放由 epoch gate 线性化，GC 只遍历 distinct admitted roots。
这关闭“退休队列仍能重新产生历史读者”的缺口，但**没有**禁止真实原位写期间的新 current 捕获，也没有完成失败恢复或不可失败发布。
不能把该逻辑边界或 `historyReachabilityRootsVisited` 的结构计数当作物理独占许可；本文件 §2/§5 的剩余授权条件仍全部有效。

67 §28 又把 existing-version history node 与 bounded fused record-set 的构造移到 metadata 准备期，并保持失败候选不修改 live index。
这减少了未来不可失败发布面的一个子集，但新增 default/descriptor storage、外层 owner cleanup、capture fence、allocation retag 与旧 binding
失效仍开放；本文件的 physical claim 依旧没有生产调用者，不能因此开始原位写。

67 §29 继续补齐了新 default record node 与 exact/slot capacity 的准备；metadata 新增记录不再是已知安装期增长点。但 descriptor、
capture fence、allocation retag、old binding invalidation、rollback/不可失败 root publication 仍未完成，physical claim 的生产禁用结论不变。

67 §30 又关闭了 default descriptor 在最终 callback 中扩容的已知路径，并复验解锁期 descriptor churn；但 reserve、completion、旧
metadata 析构与 postwork 尚未退出/预算化，capture/retag/rollback 也未实现，physical claim 仍不得由生产路径消费。

67 §31 已把 publication candidate 与 fused 旧 metadata record-set 的析构移出 PageStore owner gate，并在开锁前保留刚发布 epoch；
这减少了最终临界区，不等于析构已预算化或异步化。mutation cleanup、completion、capture gate、recoverable-before/不可失败提交、
allocation identity 移交和 binding 失效仍未闭环，physical claim 的生产禁用结论不变。

67 §32 已把大 metadata cleanup 纳入分批 reclaimer、把 mutation 调用点接入，并用预完成 host ticket 移除最终发布的 completion 分配。
这些改进缩小首字节后仍可能失败/阻塞的表面，但 PageStore 其他候选容器与 proof/postwork、current capture fence、recoverable-before、
allocation retag/binding invalidation 仍未闭环；因此仍不得把底层 physical claim 接入生产原位写。
