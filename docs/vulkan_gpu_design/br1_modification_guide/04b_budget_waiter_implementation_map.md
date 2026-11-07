# 04b：预算准入等待者的修改关系

**当前资源差集见 [92 §16.35](../92_br1_m6_m8_execution_baseline.md#read-terminal-storage)：** 原read节点/控制存储有实际付款owner，cancel/release重试复用原身体，ack/close不复制matching/pending/released列表；last-use订阅被64KiB恰满拒绝仍由原预付retry继续，GC通知拒绝保留原义务到接受。Store额度仍在初始化前冻结，组合目标用真实allocator占用和释放容量。此处不授予全局hard-full/close或原job接续资格；captured/history/pass/core及固定成本继续，当前改动按 [CODE_INDEX](CODE_INDEX.md#read-terminal-storage-code-index)和 [API](API_CONVERGENCE_MAP.md#read-terminal-storage-api-delivery)领取，既有waiter框架不重建。

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。依据 [92 §10.5–10.6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:328)，联动 S09 的 R9/R10、S10 与后续 S02/S03。该篇只定位代码和验证；阶段状态以 92 为准。当前已接局部预算等待者到原 CPU 退休队列；每请求 state、每 controller 冷 context 与 prepared wake state 本体已实际收费，state 收敛为 context 唯一所有，wake 队列与 monitor 临时引用改为 state 内嵌，删除 per-wake list node 和 shared control block。context 控制块、独立 free-list 和未收费 slot 数组已收敛；请求数组与 slot 数组都实际收费并在 controller 退出时释放。callback/派发任务、墓碑尾存储、前台 job 接续和完整故障资格仍开放，见 [92 §16.27](../92_br1_m6_m8_execution_baseline.md#reservation-storage-admission)。

## 准入和物理权限分开

```text
原分类下的退休记录暂时不能取得 Debt 额度
  → ledger 从真实 physical record 投影当前分类变化
  → controller 登记需求，准备空 reservation slot 与一次性等待身份
  → 资源归还仅合并预分配通知节点
  → 原后台 executor 按顺序授予实际 reservation
  → 锁外通知原 queue，原 record 转 ready
  → ledger 再核验 exact identity、物理域与分类变化
  → 消费 reservation，再调用原 provider 退休协议
  → 真实终态归还 charge，继续唤醒后继
```

Waiting 不持 payload pin，不额外创建 provider operation；Granted 已占用真实 reserved 额度，不能被其他 request 再使用。take 只转移一次 reservation，不授予像素写入或退休权限。取消/close 归还未消费的空 slot 或 grant；晚通知仍须通过 queue 的弱 incarnation。

## W1–W8：代码与联动终点

| 单元 | 实际代码段 | 已接线的责任与继续保持的约束 |
|---|---|---|
| W1：可在安装区间调用的唤醒 | [ReclamationWake::notify](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreReclamation.cpp:268)；[预备通知句柄](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreReclamation_p.h:49)、`prepareWake/reset/placeWake/releaseWake` | 冷路径以所属 controller 的 mutation-storage allocator 准备一个可复用 wake state；dormant/ready 前后链接与 monitor 临时引用内嵌在 state，删除 `std::list` 节点和 `shared_ptr<WakeState>` control block。notify 只移动既有节点并 signal，不分配/执行 callback/析构捕获；monitor 在锁外派发。可能外置的 capture 与 worker task 仍开放 |
| W2：需求投影与容量口径 | [prepareBudgetChange](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:178)；`fitsLocked` | 正的 per-domain 目的需求与净 aggregate/SSD 增长分开；SSD 同一实物换分类不能收费两次。立即 reserveChange 与 waiter 共用计算，超过空载容量的请求直接拒绝 |
| W3：登记与实际存储准备 | [waitForChange](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:420)；[Waiter 类型](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator_p.h:193) | 永久超容量 preflight 计入一次请求不可约的 context+固定请求数组+state+wake+最小 slot 字节，32 项已满也先无分配拒绝；每请求 state、首次冷 context 与 controller wake state 都在 controller gate 外经现有 mutation-storage 路径实际收费，再在 gate 内复验并安装。context 数组唯一拥有 state，handle 只存 intrusive inert context+sequence。context/wake 独立控制块和独立 free-list 已删除；原 slot 数组通过 `prepareReservationSlot` 在 gate 外准备，使用内嵌冷 reservation 和原父 token 收费，reserve 安装前复验需求 |
| W4：后台授额与公平顺序 | [dispatchWaiters](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:453)；`activateReservationLocked/priorWaiterConflictsLocked` | 只把已准备 slot 变成真实 reservation，再取出一次性 callback；callback 在 budget/lifetime gates 都释放后执行。重叠额度按 FIFO，不相关资源可继续；普通新请求也不能越过早到的重叠需求 |
| W5：安装/归还的热边界 | [releaseLive](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:734)；`commitRetaining/release/notifyWaitersLocked` | 生产者只更新原计数并合并唤醒，零等待者快速返回。实际检测等待者和创建 worker task 不在发布安装线程执行；仍须真实 allocator 证明 |
| W6：真实 ledger 投影 | [watchRetirementBudget](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:974)；[ledger 入口](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.h:104)、`reclassifyBackingImpl` | 检查 exact backing、物理 claim 与现有 retirement headroom，再按当前物理分类生成需求。grant 到达后重新验证；域/别名/分类变化导致旧 grant 不适用时归还并重试，不绕过 owner |
| W7：原退休记录消费 | [prepareWait](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp:128) → `dispatchReady/disarmLocked` → [admitOwnedRetirementDebt](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp:243)；[原 record](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue_p.h:29) | Wait 只保存订阅和预备 grant 容器；唤醒去重后把已授额度交给原记录，先完成 reclassify 再调用 provider。无归属的 orphan 继续只使用原 reservation，不能用 waiter 补造额度 |
| W8：取消/退出 | [Waiter::reset/take](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:270)；`ReclamationWake::reset`；controller destructor；queue `beginClose/stopAutomaticWakeups/takeForClose` | controller 的 lifetime context 不保活 store；后台/cancel/析构按 context→budget 顺序串行，生产者仅 budget→monitor。take/reset/析构先从唯一 requests owner 移出 state，再在 budget gate 外退费；controller 析构先失效 owner、摘除 wake、锁外释放 state 和请求数组，再分离小型 anchor charge、释放 slot 数组和退费，最后注销共享 child；未安装候选先取消 wake 解除引用环。monitor 已持有的内嵌引用保留 tombstone state；reset 先清空 budget 身份，最后引用稍后只释放原始内存。晚 handle/callback 不复活 owner；anchor 的实际尾内存仍须绑定进程 owner 和硬上界。take 后遵守原 reservation owner 寿命约束 |

## 验证关系

| 验证入口 | 对应单元与明确断言 |
|---|---|
| [budgetWaitersReserveInOrder](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:3307) | W2/W4/W5：8-byte 请求前面等待时，后来的 2-byte 请求与普通同步 reserve 均不绕行；独立 cache 额度可进展；授予总额实际计入 reserved，take 一次消费 |
| [budgetWaiterStateStorageIsChargedAndReleased](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:3455) | W3/W8/S10：1 B metadata 在分配前拒绝 context+state+wake 且归零；共享父额下首次 Ready 收费持久 context+wake 与每请求 state，take 后只留 context+wake，Waiting→reset 只增减 state；父额度少 1 B 与八线程首次登记覆盖失败和竞争候选。当前按92 §16.30：child析构后dormant handle/in-flight wake仍占原parent/child实际收费，最后physical free才退费/注销；父controller本身slot cache存活仍收费，晚实际存储可延长原父寿命而不pin PageStore |
| [budgetWaiterCancellationAndLifetime](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:3350) | W3/W8：32 个 slots、槽满拒绝、move/reset/复用、未取 grant 的 controller 先析构；仍有等待者时禁止重配 limits |
| [budgetWaiterQueuedCancellation](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:3375) | W8：后台授额前取消，以及 callback 已取出后取消/销毁；证明 callback 不持 controller gates，消费身份失效后不再行动 |
| [budgetWaiterSignedDurableTransfer](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:3412) | W2：SSD 容量已满时，同实物从 Current 换 History 的净 durable 增长为零；Ready 不内联回调，超容量需求不入队 |
| [budgetWaiterCommitReleasesUnusedCapacity](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:3437) | W5：reserve 10、commit 4 后，余下 6 主动授予等待者；live 与 reserved 分开核对 |
| `budgetReservationRecyclingPreservesHeldGrants` | W3/W5/W8：128 个并存 grant 的交错回收、move、commit；metadata 恰满时扩容拒绝且原 grant 保留，释放后不需额外字节即可复用；两个 store 的 slot 容量同受父额限制并在析构返还 |
| [preparedReclamationWakeCancellation](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:3457) | W1：4096 B metadata controller 下实际 wake state 收费；move 与可复用通知不重复收费。reset取消引用；in-flight callback被阻塞时实际wake与capture继续收费到monitor最后引用，释放后退费，收费owner cache继续存活，见92 §16.30 |
| [retirementBudgetWaitersProgress](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:3472) | W6–W8：原 ledger+queue+实际 provider，20/40 页 × 四种 BPP × 自主恢复/close；每次仅一页 Debt 额度，归还后无新编辑/手动 process 收敛；超过 32 个 waiters 的记录继续有界退避 |

最终同源码矩阵、五类分配探针及保留的中间失败见[本批证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s10_budget_waiters_20260927/README.md)。调度夹具修正后已重新构建、冻结并完成验证；该结果仅覆盖本批局部准入与 CPU 退休消费，不代替下列完整资源出口。集成测试直接使用原生产 queue，私有头中只导出原有冷方法的测试可见性，未新增第二队列或生产旁路。

## 继续修改的目录

1. **真实字节和共享额度：** 每请求 state、每 controller 冷 context 与 prepared wake state 本体已进入本地与共享父 `MetadataArena`，且 context 成为 state 唯一 owner；wake 的 per-item list node 与 shared control block 已删除。context 控制块、请求数组退出、free-list 和 slot 数组已收费/收敛；下一完整存储段处理可能外置的 callback capture、`QRunnable`/dispatch task、retry/pass/terminal 与 inert anchor 实际内存；32-request 上限仍不能替代这些字节。必要终结记录预留与局部/全局单次收费须共同完成。
2. **前台 job 压力：** 按 [API §19](API_CONVERGENCE_MAP.md#stroke-continuation-ownership-audit) 先一次转交原未执行 job 的输入、队列位置、取消和析构权，再同批接 typed result 与旧失败分支；不得把整个像素操作当 budget callback 重放。拒绝理由需结构化地贯穿业务，明确永久拒绝、可等待压力和取消。
3. **完整故障与公平性：** 冷准备拒绝、dispatch 分配失败、持续压力、多 store、长时间未取 grant、exit 交错和元数据耗尽仍须补完整验证。monitor 不占绘画 worker，但一次最多 32 个 request 和零分配 producer 不等于时间/全局容量资格。
4. **S09 上游链：** CPU last-use 正常终态链已接 [04a §10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#10-上游-last-use-到实际退休的代码与验收对应)；其单次 metadata 终结已按 [04a §12](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#metadata-terminal-implementation)消除新增容量需求；其他拒绝接续、通知冷失败和真实全局预算归还仍按 R9/R10 闭合。取消后空 completion signal 与空表容量的清理已接原 registry，见 [04a §9](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#9-r3-取消清理的代码与验收对应)，仍须对存活通知做实际元数据收费。本批只接已有归属的 CPU 退休预算等待者，不能据此启用长 scope 或移除 legacy idle 强引用。

正式 Fresh 2% 回退、真实 stroke/首 dab/pen-up、Vulkan、TSAN 和 BR1-PERF 仍独立验收。

S09 / T4 的外层空块释放、原预算与 close/idle/abort 责任映射见 [04a §13](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#outer-read-cleanup)；当前仍待修改的是整轮节点/字节/时间上限、其他临时对象、T5 拒绝接续及 T6/S10 必要存储准入。本项不关闭 S09 或 M6–M8。

S09 / T5–T6 的实际安装 gate 核对、completion 存储拒绝原子性与后续必要准入责任见 [04a §14](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#completion-failure-atomicity)；本批不建立基于未证实交错的轮询队列，也不把保留 Pending 当作自动接续完成。

读请求/lease/provider 准备与保护、pin、取消和退出的代码关系见 [04a §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#read-storage-admission)；T6/S10 的必要通知、派发、retry/pass 存储及全局计账继续开放。

<a id="retained-storage-waiter-delivery"></a>
## 当前收费寿命与剩余存储（92 §16.30）

原waiter context与prepared wake已经复用原allocator的retained模式。controller stop→释放request/state/array/slot→detach原parent/child；inert handle和monitor引用保留真实存储费用到物理free，最后收费owner本体free后注销child。此处替代原reset/controller先返费用的实现和文案，不要求重建free-list/shared wake控制块。原请求数组与state只在controller范围内存活，raw allocator继续适用。

实际read/retirement shared弱控制存储、retry DelayState也已进入同一收费寿命。W3冷预检包含sizeof收费owner；已建owner/slot cache拒绝后可存活且继续收费，不断言其归零。read冷准备在原owner gate外，关闭/identity重验和候选释放沿原责任，不新增语义权限。

后续仅领取尚欠分配及必需终结预留：waiter移出的外置callbacks和未传预算dispatch task、deadline node/capture、retirement record/orphan、pass scratch、terminal/runtime与其他真实控制存储。收费拒绝后必须保留原physical/read/demand ownership并明确自主恢复；硬满时不依赖新分配才能清理。实际映射和API合并见 [CODE_INDEX](CODE_INDEX.md#retained-storage-code-index)、[API](API_CONVERGENCE_MAP.md#retained-storage-api-delivery)，最终双架构目标与初始失败见 [证据](../evidence/br1_retained_storage_owner_20260930/README.md)。完整CP1、公平、continuation和M6–M8仍未结算。

上述task/terminal欠项已经由 [92 §16.31](../92_br1_m6_m8_execution_baseline.md#prepared-reclamation-tasks)更新：原budget context的实际prepared node费用计入W3 preflight，monitor只临时pin/context enqueue；活动中的事件coalesce到完成点。read/退休/history原任务也冷准备复用，terminal实际收费，不再领取它们的重复投递分配。cache存活仍收费，活动context pin到finished后释放；W3整包仍欠外置notify/callback、实际deadline/record/pass存储和硬满自主恢复，见 [当前差集](CODE_INDEX.md#prepared-reclamation-code-index)。

当前§16.31表中的capture/subscription/deadline节点欠项已由 [92 §16.32](../92_br1_m6_m8_execution_baseline.md#callback-storage-convergence) 更新：一个实际typed捕获冷收费，copy只retain；subscription/signal/registry readiness真实节点与控制块沿原付款owner收费，deadline节点嵌入原state。W3含实际notify/wake捕获大小，永久不可满足判定先于cache准备；producer链接/通知预备节点，不重建外置function。cancel/in-flight/弱尾到physical free才退费；read/binding/registry/backing门外准备，原身份重验。不会再领取已删除的std::function/map额外节点/QP包装或prepared task投递分配。

唯一retirement record和分区转交已由§16.33交付；原queue必要retry由 [92 §16.34](../92_br1_m6_m8_execution_baseline.md#prepared-retirement-retry) 更新：configure物理adoption前一次冷准备context/Wait/task/capture/Delay，拒绝record订阅时同debt转原固定retry；arm/cancel/takeReady核对generation并coalesce在途通知。旧scheduleAfter及每retry重建删除。metadata恰满下registered/orphan自主恢复、实际Debt额度释放后无新输入继续已验证；不代表整个pass零分配。下一从原read/history/pass的scratch/效果/索引与拒绝接续整包关闭必要容量、收费和最后free；tree/deferred、Store/registry/provider本体及runtime固定成本继续开放。当前映射只维护 [CODE_INDEX](CODE_INDEX.md#prepared-retirement-retry-code-index)、[API](API_CONVERGENCE_MAP.md#prepared-retirement-retry-api-delivery)，完整CP1未结算。

§16.66原metadata配置目录/control接同一retained allocator：shard对象及实际shared control、immutable pointer array、三个typed arena目录和publication identity按实际请求收费，完整局部候选成功后一次发布。原目录估算/手工fee与分配后超预留分支删除，真实父额少一字节连续拒绝不留capacity，压力释放后原对象可配置；晚cancel/cleanup在coordinator/controller后精确归费。见[代码/API](CODE_INDEX.md#metadata-directory-storage-code-index)及[该轮证据](../evidence/br1_metadata_directory_storage_20261003/README.md)。

§16.67已删除eager全目录及重复full-growth规划，原growth承接同allocator目录门外准备、原grow/revalidate竞争接续和旧数组晚free，空配置64 shard减少1.5MiB。真实少一字节拒绝/准备后父硬满安装/晚Data归费通过，目录候选本身及新旧数组峰值仍实际收费。原预算/等待者协议和block/hash手工fee保持；Private/authority/bootstrap、其余wrapper与全部参与者总峰值/永久尾出口仍欠，有限绿压力样本不关闭完整CP1。见[当前代码/API](CODE_INDEX.md#metadata-directory-growth-code-index)及[同源证据](../evidence/br1_metadata_directory_growth_20261003/README.md)。

§16.68关闭上述authority本体/实际control差集：configure以同retained allocator准备完整局部候选，发布前已有原accounting owner，旧未收费构造/重挂接/后置补owner拒绝删除。原预算选择不分配authority，不放宽controller冻结/挂接要求；每coordinator新增64B实际请求费。原shard/Data和仅read cleanup保有费用到最后free，controller后父硬满clear/析构精确归费已验证，见[当前代码/API](CODE_INDEX.md#metadata-authority-storage-code-index)及[证据](../evidence/br1_metadata_authority_storage_20261003/README.md)。原block/hash/reservation拒绝政策继续；Private本体、standalone controller及其他bootstrap、总峰值和全部永久尾出口仍欠，完整CP1未结算。

§16.69进一步把实际Private104B纳入原configure候选；原配置事实留在冷facade，core指针一次发布替代独立operational，拒绝和最终析构共用同retained allocator的destroy/free。生产使用原attached controller，删除始终不用的内嵌standalone；双架attached的facade+Private对象尺寸1,496→160B，配置费1/4/64 shard为1,416/5,016/77,016B。constructor收费会阻断既有shared/limits冻结顺序，估算补费另立权威，因此沿原配置准备，不放宽controller合同。真正standalone的1,352B controller体和Store根对象/其他bootstrap仍未授收费资格，原block/hash及实际准入拒绝保持。见[当前代码/API](CODE_INDEX.md#metadata-core-storage-code-index)与[同源证据](../evidence/br1_metadata_core_storage_20261003/README.md)。

§16.70关闭生产Store facade/Private本体的冷收费差集：backend已取得原父预算，临时栈child以原retained allocator准备实际两对象，返回前controller退出，原accounting持父/child登记到最后free。内部shared→limits→configure顺序及冻结保持；原new/delete入口删除，拒绝回滚、同步/退休线程和late captured共享原Private destroy，facade独立归费。双架实际冷请求4,520B＝8B facade＋4,392B Private＋120B accounting/登记；保存allocator16B、backend deleter8B及栈controller对象1,352B是保证成本，根allocator只供free。真实只余1B/候选少1B拒绝与同父重试、外部parent退出后的硬满最后free验证通过。默认/reference/真正standalone及其他嵌套heap/control、backend/provider/history/process根与完整峰值/永久尾出口仍欠。见[当前代码/API](CODE_INDEX.md#store-root-storage-code-index)及[证据](../evidence/br1_store_root_storage_20261003/README.md)。

§16.71把Ledger Private/admission/control纳入同Store冷allocator，原Root child/accounting继续承担真实最后free；原new/Qt创建删除，Store shared/limits冻结保持。原domain强/弱控制、provider登记与transition receipt vector同批迁移到std；无physical record只复用已付费authority保活，删除独立receipt分配及拒绝，父硬满也完成；有record的inactive receipt/control72B与claim节点352B仍在domainClaim发布前准入，原cancel/commit/detach及锁序保持。双架生产冷根5,104B新增584B，Ledger Private16B allocator及admission8B接口是保证成本；单独Ledger测试冷fee704B含另一child/accounting，不能在生产重复计费。真实claim少1B三次拒绝/重试及仅receipt weak存储在controller后父硬满free归基线已验证；默认standalone/测试heap facade、其余Qt控制和全参与者峰值/永久出口仍开放。见[代码/API](CODE_INDEX.md#ledger-control-storage-code-index)及[证据](../evidence/br1_ledger_control_storage_20261003/README.md)。
