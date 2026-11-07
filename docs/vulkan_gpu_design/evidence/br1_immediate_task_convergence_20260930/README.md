# CP1 即时任务、投递失败与 owner 归还收敛

执行入口为 [92 §16.29](../../92_br1_m6_m8_execution_baseline.md#immediate-task-convergence)。本轮按新排期先审现有分支/API/owner，再选择 CP1 的安全收敛：原任务重复包装、投递失败后计数/引用不撤销、最后 root 引用归还仍需分配。没有扩大 stroke 模式、M7 或 continuation 能力。CP0 同依赖 upstream 对照仍未验收。

原专用 QThreadPool 只冷启动一个常驻 runnable；准备好的 typed task 进入原 executor 的侵入 FIFO，worker 依次执行、销毁捕获、释放实际存储/收费，再发布 consumer idle、接下一 pass 和归还原 root 引用。已删除每任务 QRunnable::create、std::function 包装及四类 callback 内提前归还 root 的出口。最后 root 引用只转交 Private 冷准备的独立终结 node。没有第二执行器或 semantic release 权威；deadline monitor 仍独立，drain 不等待未来 deadline。

## 最终目标验证

| 实际范围 | arm64 | x86_64 |
|---|---|---|
| CPU mutation 全目标：history/退休/last-use/waiter、close/lifetime 和原 Fresh 控制 | 1,246 / 0 / 0 | 1,246 / 0 / 0 |
| Reference 全目标：含新增 task 存储/最后 owner/准备拒绝 | 650 / 0 / 0 | 650 / 0 / 0 |
| Freehand 原压力成功、压力取消 | 4 / 0 / 0 | 4 / 0 / 0 |

总计 **3,800 passed / 0 failed / 0 skipped**；实际 argv、退出码、架构和 totals 保存在 [results.json](results.json)。core 运行 `_build/bin/KisPageStoreCpuMutationTest` 和 `KisPageStoreReferenceTest`，Freehand 只运行 `testPersistentAutoBrushStrokePressure` 和 `testPersistentAutoBrushStrokePressureCancelled`，由 `/usr/bin/arch -arm64/-x86_64` 分别启动。UI 环境为 `QT_QPA_PLATFORM=offscreen`、`KIS_BR1_SEED=12345`、`KIS_TEST_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install`、`KIS_TEST_PLUGIN_PATH=/Users/apple/krita_gpu/krita/_build/bin`。24 MiB 成功与 8 MiB 取消产品预算未修改。

新增测试使用 move-only、128-byte alignment 的大 inline capture，worker 被原 barrier 暂停时检查真实 MetadataArena live bytes；最终回调在 capture 销毁、task 实际释放/退费后直接析构 controller，验证最后 owner 顺序。另以真实存储填满剩余额度，检查 task 拒绝不执行/不归还尚未转交的引用；任务构造主动拒绝时实际存储与 reservation 清零，释放额度后重试成功。没有生产测试 flag、allocator 故障开关或新增指标 API。这些断言不是全部生产分配点的 interposition 资格，未测路径不假装已覆盖。

保留 [初始 arm64](reference-initial-arm64.log) 和 [初始 x86_64](reference-initial-x86_64.log) 的唯一失败：测试试图在已有收费 cache 时重配 controller limits，被原合同拒绝。改为分配真实 filler 填满余量，没有放宽产品合同。最终 idle 发布顺序调整前的成功日志保留在 `pre-finalization-order/`，不计入最终总数。构建见 [最终构建](build-final.log)，源码变化后重跑受影响目标；末次构建检查因 Ninja 日志恢复而实际重建，保留 [该日志](build-noop.log)（文件名不是 no-op 结论）与 [dry-run](build-dry-run.log)，原测试结果保留在 `pre-verification-build/`。最终已按刷新后的二进制补跑同一范围，不扩大历史矩阵；哈希验证绑定这些最终二进制。

## 存储及未关闭条件

| 对象 | 当前实际 owner / 结果 | 剩余条件 |
|---|---|---|
| typed last-use task/capture | 原 store pin 保持 controller；sizeof/align 经 MetadataArena 准入；dispose 实际 free 后退费，然后 idle/root 归还 | callable 引用的 context/read record/control block/pass scratch 仍须逐项结算 |
| 退休通知/退休 pass/history pass | 共用 task/finalizer；投递失败撤销多加的计数/引用，原记录保留 | task 的冷准备/收费及 pass 内其他分配失败恢复仍开放，不能在 owner/provider 安装 gate 添预算分配 |
| budget waiter task | 投递失败 scheduled=false，原请求保留，不让 bad_alloc 终止 monitor | task/capture 和 controller 后尾内存未结算；不能称无新输入进度已合格 |
| terminal node | 每个 Private 冷准备一个独立 node，最后引用只入队；root 析构后 node 自行释放 | 实际 node 收费及 controller 后收费 owner 未结算，不可直接用已析构 child 的 raw budget |
| runtime/clock/deadline/retry/record/pass | 原 runtime 只持一 worker/runnable；队列本身不新增节点包装 | 一次 runtime 成本、std::function 内部 capture、shared/QShared control block、map/list node、scratch 和必要尾内存须统一实际收费/失败/最终 free |

**CP1 未结算；M6/M7/M8 正式资格仍为 0/3。** 默认开关、完整 BC9、多文档公平、原 job 接续和 BR1-PERF 均未关闭。原 footprint、provider、逻辑/物理释放 eligibility 责任不变。下一轮先补齐上表中原收费与寿命 owner，再考虑能力扩展；不新增等价通知框架。

## 结构和身份

最终结构检查见 [architecture.log](architecture.log)，生成图见 [callgraph.log](callgraph.log)，预期旧身份失配保留在 [architecture-initial.log](architecture-initial.log)。只刷新实际源码/图身份，不修改 intrusion ratchet。新增 private prepared-node/finalizer/queue 操作有本批消费者，替代原 wrapper/投递/退出分支；UI/tool/paintop/painter/PaintDevice/scheduler public/protected API 净增长 **0**，本批没有修改这些文件。API 逐项替代见 [账本](../../br1_modification_guide/API_CONVERGENCE_MAP.md#immediate-task-api-delivery)，函数及剩余改动映射见 [CODE_INDEX](../../br1_modification_guide/CODE_INDEX.md#immediate-task-code-index)。

[源码/测试/二进制哈希](source-sha256.txt)、[实际加载的运行库与插件哈希](runtime-sha256.txt)、[本批前架构身份](baseline-before.json)、[最终架构身份](baseline-after.json)和 [HEAD](head.txt)标识脏工作树。`source-union.diff` 是列明文件相对 HEAD 的累计 diff，含此前实现，**不是本轮净增规模**。文档链接、最终运行与源码身份核验见 [document-validation.json](document-validation.json)。不使用 archived 文档作为当前指导，不继承旧日志的阶段资格。
