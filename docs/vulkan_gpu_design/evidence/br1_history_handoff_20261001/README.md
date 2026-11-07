# CP1：history 原工作记录与预付退休 operation 接受

2026-10-01。产品父提交 `8a5b92ef8dfd1e43ea84488cf7303653febd8465`，文档父提交 `e256323c2d9fee1ce80c1f7ddd36cd1c27c40ec4`。活动合同为 [92 §16.37](../../92_br1_m6_m8_execution_baseline.md#history-handoff-lifecycle)，本批仍是CP1子范围，M6/M7/M8正式资格未结算、默认关闭。

## 同一责任的替换与删除

| 原实现 | 最终归属与删除 |
|---|---|
| pending/queued/deferred/ready/scans五组容器 | 一个收费WorkIndex原key节点，ready仅为intrusive link；固定32 candidates，pass固定16指针 |
| collectBatchLocked与后台collectSlice两套GC政策 | 共用collectPassLocked/collectSliceLocked，旧batch与queueContinuation/deferredKeys删除 |
| detach效果复制、pass与Read/Publication/Store跨caller累加 | 立即move metadata结果到原Work，逐项queue接受后推进cursor，返回效果与overlay输出参数删除 |
| 失败须等下一次输入；每轮单独的恢复阶段 | 原task加一个冷准备Delay/context，实际key/Debt拒绝沿原记录以1–100ms退避，恢复真实容量后无新输入继续 |
| provider退休后才申请operation登记存储 | 原record在物理准入前准备收费map node，调用前转入原ledger，terminal提回原record，到实际free才退费 |
| detach后查询provider能力 | 原provider注册entry保存线程许可，take原record时转交；效果接受不执行provider代码或分配节点 |

比较了继续扩展旧容器、只换allocator和准备前移。最终没有新executor、通用pool或第二份效果队列。Work保存最后确认的扫描和效果接受事实；queue/ledger继续拥有physical debt和operation；root权限仍由epoch模型决定。有效provider result留在原record，登记拒绝不重放退休。map node allocator不匹配在provider副作用前拒绝，避免跨收费owner转移。

同步消费者即使没有返回效果数组，也在锁外处理已接受退休。新解保护在两片之间标repeat；整页扫描在片间继续计为active，最终清除缓存。idle等待在途task/通知的真实root pin归还，future deadline不等于drain。stop/close冻结deadline；未接受效果拒绝close。

[生产差异](production-incremental.diff)为12文件 **+499/-289，净+210**；[测试差异](tests-incremental.diff)为2文件 **+216/-18，净+198**。3份审计JSON单列在 [source-metrics.json](source-metrics.json)，不计为人工生产行数。净增主要为实际收费、拒绝接续、operation前置存储和完整活动寿命，不记为纯去重收益。每个deferred key的固定候选数组增加驻留；generic operation从QHash变为std::map，性能及完整内存收益未测量。上层UI/tool/painter/PaintDevice/scheduler生产改动和public/protected API净增0。

## 同源验证与实际拒绝范围

[最终构建](build-allocator-final.log)后的同源码双架构：

| 目标 | arm64 | x86_64 |
|---|---:|---:|
| CPU mutation全组 | 1271/0/0 | 1271/0/0 |
| Reference全组 | 659/0/0 | 659/0/0 |
| PhysicalClaim全组 | 379/0/0 | 379/0/0 |
| 原Freehand persistent pressure/cancel两方法 | 4/0/0 | 4/0/0 |

合计 **4626 passed / 0 failed / 0 skipped**，含init/cleanup。argv、退出值和原始日志见 [frozen-results.json](frozen-results.json)、[run-frozen.log](run-frozen.log)及八份frozen日志。[runner](run_results.py)固定 `_build-br0-cpu/bin`、其插件、原 `_install` prefix、offscreen和seed12345；中间通过不累加到最终数量。

5个新行采用原metadata/epoch/ledger/history/queue/provider组合。fixture构造前固定256KiB Metadata和16KiB Debt；测试friend仅在冷初始化时接真实budget与debt owner，注册合法历史初态，不改private事实或活跃Store额度。两行分别填满实际Metadata allocator和实际Debt额度；至少三次自主retry期间metadata仍保留历史、provider退休次数为零，释放容量后没有collect/request/显式wake也能完成一次退休、无operation/效果/扫描遗留，节点实际退费和pin归还。

效果硬满行在原Debt commit回调边界占满真实Metadata额度，确认效果接受没有后置能力callback和额外节点申请。operation自动/close两行在provider有效result返回时填满额度，绑定原准备node成功，完成前至少三次原queue retry而retire只执行一次，终态清空operation/payload并归还实际费用。这个组合夹具不是全局heap interposition；Qt snapshots/effects本身未进入该预算，不能由恰满通过证明整个pass零分配。原Store长/multi-page历史、半扫发布、restore、raw/capture/read终结、shutdown和真实pressure/cancel回归包含在最终矩阵。

## 保留的失败与修复

本目录保留各build与focused日志，不覆盖失败。初始编译中Key坐标/API可见性错误已修复；历史组合初态改合法generation，固定额度改在构造前设置，避免把原64KiB夹具的metadata块拒绝误当目标阶段失败。

`focused-final`等中间长历史留下游标前版本：只在cookie存在时标repeat漏掉两片间的新解保护，改为原扫描活动覆盖整个key sweep。`qualified`首次全组CPU在permanent Metadata pressure超时，Reference9失败，Physical81失败；`final-consumers`保留部分修复后的CPU5/Reference9失败。原因分别为idle错误等待future retry、同步入口空效果直接返回、active/cached观察语义缩小，以及预算断言只扣record本体。恢复原idle/扫描含义，全部同步caller空数组也推进已接受退休，预算断言实测完整节点费用。行为、payload、capability断言未放宽。

`sync-dispatch-final`仅arm64一个原last-use目标失败：idle发布后任务/通知还持有临时root pin。冷context活动计数配对实际pin，归还后才通知idle，保留future retry与drain的区分。之后同源全组通过；最后只补operation node收费allocator身份检查，再冻结最终矩阵。测试与失败总数不能代替这些边界的逐项判断。

## 结构、身份和提交

[最终调用图](callgraph-frozen.log)覆盖87 TUs，1915 APIs / 20927 edges / 20 callbacks。[正常结构门](architecture-frozen.log)通过21 manifest / 25 ownership / 16 census / 19原侵入文件。checkpoint刷新前只有源码哈希过期；原owner审查和图重建后刷新 [前](baseline-before.json)/[后](baseline-after.json)，再独立跑正常门。manifest/侵入/布局上限未放宽。

[source-sha256.txt](source-sha256.txt)冻结35份源码/测试/审计文件，包含全部本批改动及前轮相关依赖；[runtime-sha256.txt](runtime-sha256.txt)冻结4目标和8份库/插件，加载配置见 [runtime-rpaths.txt](runtime-rpaths.txt)。[freezer](freeze_evidence.py)只读实现/指导文档，生成diff/哈希/身份；[代码commit](code-commit.txt)和 [Git绑定](git-round-identity.json)在聚焦产品提交后核对全部blob和runtime。文档仓独立提交活动指南、本证据和gitlink，原其他未跟踪文件不混入，无push。

普通指导文档、脚本与JSON空白检查通过；原始build/test日志和unified diff保留原输出空白，不改写失败证据。活动链接、最终矩阵、35份源码/12份runtime身份和旧符号删除检查见 [document-validation.json](document-validation.json)，归档链接不参与检查。

## 同一CP1的剩余端点

下一处理metadata historySlice/versionSnapshot/pageKeys、discard/effects及Debt准备的Qt投影容量，仍在原metadata/ledger准备边界保证存储齐全才detach，原Work继续承接未接受效果。泛型write/transfer及foreign legacy仍有consumer，其operation前置准备未闭合；provider/registry核心索引、capture Private/Qt控制块/辅助集合、tree/deferred及一次性task、close handles/seen/诊断、控制本体/runtime/clock、永久拒绝最后handle退出仍欠。

没有全pass allocator interposition、TSAN、完整CP0同依赖upstream、公平/原job continuation或BR1-PERF新增资格。完整CP1和M6–M8未勾选。函数/删除映射见 [CODE_INDEX](../../br1_modification_guide/CODE_INDEX.md#history-handoff-code-index)、[API](../../br1_modification_guide/API_CONVERGENCE_MAP.md#history-handoff-api-delivery)，领取仍只维护 [NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)和92。
