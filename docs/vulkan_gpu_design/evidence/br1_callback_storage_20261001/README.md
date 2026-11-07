# CP1 实际通知、订阅与 deadline 存储收敛

2026-10-01 同源冻结，当前入口为 [92 §16.32](../../92_br1_m6_m8_execution_baseline.md#callback-storage-convergence)。按每轮先审查再选择：原 task 已冷准备，不再增加同义 task/helper；真正欠项是通知捕获、订阅/信号控制块、registry readiness record 和 deadline 容器的实际分配。因此本批实现这些原消费者的必要存储，同时替换旧分配路径，没有提前实现 M7 或扩大 stroke 模式。

## 真实责任与删除对象

| 原消费者 | 当前实际存储 / 门 / 最后释放 | 同批替代或删除 |
|---|---|---|
| read/retirement/budget/wake/deadline typed callback | 一个真实 inline capture 经原 retained allocator 冷准入；copy只引用同一body，funded body保持原付款身份；真正最后free后退费 | 原std::function的外置捕获与派发复制；没有额外callback执行服务 |
| Readiness Subscription / Signal | subscriber节点先收费准备，原signal gate仅链接；signal/state真正shared控制块收费；取消按原单调ID，notify/取消门外释放capture；弱subscription费用留到最后weak reset | unordered callback节点/bucket域、原QP内部state包装、门内try_emplace与捕获搬移 |
| CompletionRegistry readiness | 门外准备callback/subscriber/signal/state/record，原ticket/status重验后装入侵入树；末次取消仍重验原signal identity/emptiness；terminal先发布状态、移除且free record，再通知 | readiness unordered节点/buckets/空表交换；核心Private、source/terminal maps没有被本批冒充为已收费 |
| CPU binding / read owner / backing ledger | 原allocation/readers/writer及original record/closing在原门重验，准备和失败候选free不持相应provider/registry/read/backing门；旧consumer自己复验权限 | provider/read/backing门内通知存储准备；不增加retire/handoff许可 |
| Budget waiter | W3包括实际notify/wake捕获，永久不可能判定先于收费cache分配；原32 slots只是count；移出的callback费用跟随原body | 对未收费capture的固定slot假设；永久拒绝前无谓的owner cache准备 |
| Deadline | hook嵌入原DelayState，原O(log N)排序和monitor保留；queuedPin仅覆盖排队，cancel/pop/shutdown先unlink，门外free state/callback | 额外multimap节点、外置dispatch副本；每次retry仍新建原Wait/Delay/capture，不盲目复用晚取消身份 |

生产 caller 传实际 typed 弱身份捕获及原budget。默认无budget的synthetic测试通知不授予生产收费资格；任意外来functor内部自行持有的额外heap也不由本批泛化推定为已收费。budget冷fund拒绝保留原capture，cold存储准备失败保留原read/physical/demand债务。

同一信号的首个付款controller退出后，已有state/弱控制块仍由原parent/child承担真实费用；新订阅用新的活跃付款owner准备自己的节点。信号安装不再向已退出的首个controller申请容量。原付款owner只管存储收费，不是page/root/payload语义权威。

## 最终结果

| 实际目标 | arm64 | x86_64 |
|---|---|---|
| Reference全组，含三个新增通知/原付款/deadline目标 | 657/0/0 | 657/0/0 |
| CPU mutation全组 | 1247/0/0 | 1247/0/0 |
| Completion全组：取消/重订阅/并发/晚派发/终态 | 83/0/0 | 83/0/0 |
| 原Freehand压力成功与取消 | 4/0/0 | 4/0/0 |

合计 **3982 passed / 0 failed / 0 skipped**。实际argv、退出码、架构配置和totals见 [results.json](results.json)，运行环境见 [run_results.py](run_results.py)：offscreen、KIS_BR1_SEED=12345、原_install与_build/bin夹具路径；UI 24 MiB成功/8 MiB取消预算未改。

新增Reference结果验证128-byte aligned大inline捕获、满额时64次copy/invoke不克隆Function或增加费用；冷订阅/deadline拒绝，原callback/已装信号保留；原付款退出后另一live付款成功订阅同一signal，completion在满额下执行且最后weak reset实际退费；deadline callback已派发后reset/controller退出，实际body/control block留到monitor最后释放。原CPU的自动last-use验证新增实际订阅费用并在最终cleanup返还，wake按不同实际capture尺寸计费，原最终释放断言保留。

本包完成后统一验证，没有对每个hunk跑测试。保留 [首次运行失败](initial-failures/results.json)：W3永久拒绝太晚导致无谓cache；新增测试表达式被C++解析为声明而非构造；旧wake/read断言假定不同capture费用相同或通知免费。前者修复生产顺序，后者按实际storage修改断言，容量/资格没有放宽。首轮UI缺夹具prefix/plugin路径而退出、错误QT_HASH_SEED被Qt忽略，均不能当当前资格；最终runner使用正确夹具环境。初始编译类型迁移失败见 [build.log](build.log)。最终源码构建成功见 [build-qualified.log](build-qualified.log)，之后形成最终测试及身份，未再执行no-op重建改变binary。

## 结构、密度与未关闭条件

[architecture.log](architecture.log)通过：21 manifest条目、25 ownership事实、16 census组、1894 indexed APIs、20482 call edges；callgraph登记20 callbacks。源码失配与更新顺序见 [architecture-initial.log](architecture-initial.log)、[callgraph.log](callgraph.log)、[前](baseline-before.json)/[后](baseline-after.json)身份。intrusion manifest与上一批完全相同，19个既有上层侵入文件限制未放宽。

本批只改PageStore内部与原测试，上层UI/tool/strokes/paintop/painter/PaintDevice/scheduler生产改动、public/protected API净增均 **0**。14个实际生产文件相对本批起点 **416 added / 196 removed**：新增主要是收费inline body、预备节点及两次身份重验；不声称代码总行数下降，也不把private API census增量当阶段完成。删除对象和实际consumer见 [API账本](../../br1_modification_guide/API_CONVERGENCE_MAP.md#callback-storage-api-delivery)。

[before-code.json](before-code.json)与[source-incremental.diff](source-incremental.diff)只对应上述14个生产文件，本轮测试diff未保存起点不纳入该净增数字；[source-union.diff](source-union.diff)是所列文件相对HEAD累计差异，含此前工作，不能当本轮增量。[source-sha256.txt](source-sha256.txt)冻结28个相关源码/测试/结构文件，[runtime-sha256.txt](runtime-sha256.txt)冻结4个目标binary及8个运行库/插件，[HEAD](head.txt)只标checkout提交，实际实现仍在未提交工作树。检查脚本及结果见 [validate_documents.py](validate_documents.py)、[document-validation.json](document-validation.json)。

**完整CP1仍未结算，M6/M7/M8正式资格0/3，默认关闭。** 下一优先为必要retirement record/orphan准入、partition转交及pass真实存储/硬满保债与恢复；每次retry重建、history/read scratch、tree/deferred metadata对象及一次性task、Store `new Private`/内嵌服务/statistics、registry/provider本体与core索引、runtime/clock固定成本仍欠。通知满额执行不能外推为所有pass零分配、所有原physical debt自主恢复、全分配interposition或TSAN通过。清点只在 [当前CODE_INDEX](../../br1_modification_guide/CODE_INDEX.md#callback-storage-code-index)，领取只在 [NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)维护，不重复重建已合并的收费寿命、callback和prepared任务。
