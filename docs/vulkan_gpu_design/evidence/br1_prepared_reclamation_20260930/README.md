# CP1 原回收任务冷准备与复用

2026-09-30 开始，2026-10-01 冻结。当前实施入口为 [92 §16.31](../../92_br1_m6_m8_execution_baseline.md#prepared-reclamation-tasks)。先核对现存API/分支，再选择CP1必需能力并合并旧路径：history/退休pass、read/budget通知及退休wait仍在每次投递时分配task，真正硬满时不能保证派发；终结node虽冷准备，却未收费。

## 实际改动和存储责任

沿原 typed task 增加冷准备路径，实际 inline closure/node 一次由原 retained allocator 准入。可复用任务仍进入原 executor/FIFO，worker 复制完成信息，invoke 后调用原 finalizer；owner 的 scheduled/inFlight gate 排除重复入队，完成时可在原FIFO接续。它不再每次dispose实际节点，节点作为真实收费cache存活到owner最后析构。原一次性 schedule 包装复用同一准备/释放实现，仍用于真实一次性消费者，没有第二executor或semantic释放权威。

| 实际消费者 | 冷准备 / 活动寿命 | 同批删除 |
|---|---|---|
| history和retirement pass | store configure离开原owner gate后各准备一个实际node；每次投递仅取得原root引用，原finalizer发布idle/接续/归还root | 每pass分配task与相应分配失败调度标志/计数回滚 |
| budget waiter | context冷准备时收费实际task尺寸；每次投递临时pin原context，完成后释放；运行中的事件合并到dispatchAgain并在完成后通知 | monitor每次新建task、重复捕获context及dispatch bad_alloc分支 |
| read last-use | 原context冷准备同时收费一个node，原root pin覆盖每次执行；沿原jobScheduled/finalizer终结 | 每次dispatch新建task/重复强捕获；process内部拒绝仍按原dispatchFailed保留debt |
| retirement readiness/retry wait | 原wait在注册provider/budget/deadline前准备自己的inline任务；inFlight仅在活动投递时持有self pin，并取得原root引用；相同wait重复通知合并 | 每notification新建task/捕获weak身份/分配失败回滚；没有新增通知队列或record权威 |
| terminal node | configure在任何物理adoption前经原retained allocator准入；一次性执行delete Private，controller退出后实际node仍能退费 | 原独立TerminalCleanupJob类型与未收费make_unique；未配置且没有node的空root直接析构 |

configure的冷准备区间由原activeProviderCalls排除并发configure，节点准备不持原store owner gate。准备拒绝返回原失败且不进入物理adoption；已经存活的owner/cache继续收费。任务捕获以inline raw consumer身份为主，活动原owner/context/self pin保证寿命； dormant prepared storage不额外pin PageStore。完成后的实际cache仍收费，idle不意味着cache费用归零。

## 最终验证

| 实际目标 | arm64 | x86_64 |
|---|---|---|
| CPU mutation全组，含新增终结回收 | 1247/0/0 | 1247/0/0 |
| Reference全组，含新增满额复用 | 654/0/0 | 654/0/0 |
| 原Freehand压力成功/压力取消 | 4/0/0 | 4/0/0 |

总计 **3810 passed / 0 failed / 0 skipped**，以 [results.json](results.json) 的实际argv、退出码、架构和Qt totals为准。UI使用offscreen、seed=12345、原_install与_build/bin路径，24 MiB成功/8 MiB取消预算未改。最后构建成功后才形成最终运行与哈希，不再运行所谓no-op构建改变binary身份。

Reference新增目标在实际MetadataArena恰满时拒绝另一cold task，却使同一个已收费node连续执行64次，验证大inline/move-only/128-byte aligned捕获到最后才析构，cache实际free才退费。CPU新增目标通过原public业务能力量取并重建精确metadata上限，确认额度满时facade退出、原scope取消与最后view释放后，原排队维护/terminal完成最终root/provider析构。后一目标在capability释放时会返还部分存储，不声称整个pass/终结过程始终剩余零字节；实际node在满额下的无新准入由前一目标验证。这些结果不替代全分配interposition、完整硬满恢复或TSAN资格。

保留 [初始构建](build.log) 的编译失败：新测试试图调用private共享父配置。修正为使用原public业务能力测量实际上限，没有添加测试friend、getter或上层API。`unqualified-after-build-failure/`保留错误地在该构建失败后启动的旧测试binary运行，**不能当当前源码通过或累加资格**；它暴露了零metadata预算拒绝文本不含budget，已明确写成reclamation budget storage拒绝，预算条件没有放宽。[最终构建](build-final.log)成功之后重新运行上表范围。

## 结构、身份及未关闭条件

[architecture.log](architecture.log)、[callgraph.log](callgraph.log)、[旧身份失配](architecture-initial.log)、[前](baseline-before.json)/[后](baseline-after.json)架构身份绑定当前工作树，只刷新实际身份和原owner说明，intrusion ratchet未放宽。本批只改PageStore内部和测试；UI/tool/paintop/painter/PaintDevice/scheduler生产改动、public/protected API净增均为 **0**。

[source-sha256.txt](source-sha256.txt)、[runtime-sha256.txt](runtime-sha256.txt)、[HEAD](head.txt)、[文档/结果核验](document-validation.json)冻结身份。before-code.json保存本批涉及生产文件的起点；source-incremental.diff只比较这些已记录文件，source-union.diff是列明文件相对HEAD的累计差异，包含此前实现，不能作为本轮净增。Ninja premature-end恢复继续作为工具事实保留，不以构建成功推导阶段资格。

**整个CP1仍未结算，M6/M7/M8正式资格仍0/3，默认入口关闭。** 源码仍有callback/订阅的外置std::function捕获、deadline map及每次retry准备、retirement record/orphan容器、history/read/pass临时存储、tree/deferred metadata cleanup的一次性task及其存储、一次runtime/clock成本和对应硬满失败/自主恢复。下一轮从 [剩余改动清点](../../br1_modification_guide/CODE_INDEX.md#prepared-reclamation-code-index) 的差集推进；不重建已合并的worker/FIFO/收费寿命或这些冷任务，不将prepared enqueue资格外推为整个pass零分配。

固定控制成本清点还包括Store的`new Private`本体/内嵌服务和statistics；本批节点计费不能代替它们的实际genesis/admission/最终释放收费。原预算/controller不是新的语义owner，完整CP1结算时这些真实分配不得从清单消失。
