# 普通绘画实际瓶颈：projection 写入作用域

本包完成诊断，**优先候选是 projection 的 clear→composite 在分立 mutation 中反复准备与发布**；其次是画笔普通 operation 的准备成本。没有产品补丁或新的速度收益声明。产品 `128fb32a71fef69f462da2c2dfa8d187ed94db52`，生产仍与 `38834c4e2612c819f9d088dfd59c59889f295a49` 相同；外层父 `875f364b77c5667f0c2ca85bc68bc245b35f3ef3`。当前状态只见 [92](../../92_br1_m6_m8_execution_baseline.md#business-cost-localization-delivery)。

上一包当前/upstream stroke 比 ARM 2.258、Rosetta 2.318 是独立冻结的业务差距。本包不重算其置信区间，不把差额全算为可删除成本。

## 实验与证据强度

- [预注册 profile](PLAN.md)：ARM 当前/upstream 各一次能力运行，随后固定 current/upstream/upstream/current 四过程，每过程 64 次完整 replay。原业务、计时和像素断言保留，只在边界外加 signpost。四个 trace 各捕获 Setup/Stroke/Undo/Redo/Teardown **每阶段 64 个完整区间**，无缺失边界。后续 replay 暖全局 cache，与上一包一过程一笔不同。
- [计数协议](MECHANISM_PLAN.md)：同一当前生产库，普通/已有 persistent opt-in/opt-in/普通四过程，各一笔；在阶段边界外通过已有 test friend 读取既有统计，没有生产插桩或 API。只覆盖仍存活的 node 和 root manager，实际指针去重，临时已销毁设备未计入。
- 共 **10 个夹具过程、262 次语义 replay、30 QTest passed**；四个 profiler 过程亦正常退出，全部已 reap，无运行超时或像素/断言失败。262 次 replay 不当作独立统计样本，30 也不替代产品完整安全矩阵。
- 当前/upstream 原库、插件和依赖实际加载身份通过；构建前后 identity 一致。所有计时、构建、导出串行。没有在计数/采样时延上计算加速。

对“额外工作主要落在画笔写准备与 projection 管线”的定位有较强证据：两次当前 profile 分布接近，当前/upstream 使用相同输入，四次计数中主要工作量完全一致。对“projection 可以安全合并多少以及能快多少”只有中等候选置信度：尚未实施该消融、核定中间读者与失败终点，也没有未插桩增量对照。**不提供凭经验编造的 90%/95% 概率。**

## 分阶段实际运行上下文

下表为 Stroke signpost 内所有线程的 Running 样本。每行互斥分类；列为四个独立 profile 过程，各 64 replay。

| 责任 | 当前 0 | upstream 1 | upstream 2 | 当前 3 |
|---|---:|---:|---:|---:|
| 画笔策略/渲染/finish | 626 | 363 | 382 | 619 |
| projection merger | 299 | 25 | 46 | 308 |
| history collector | 39 | 0 | 0 | 44 |
| retirement | 23 | 0 | 0 | 22 |
| reclamation 调度及剩余栈 | 34 | 0 | 0 | 34 |
| 其余 worker | 62 | 80 | 83 | 69 |
| main | 1 | 0 | 1 | 1 |
| 合计 | **1084** | **468** | **512** | **1097** |

当前 projection 占阶段运行样本约 **27.6%/28.1%**，是明显的新增成本区域，不能解释成可删 CPU 比例或 wall 收益。画笔仍是最大总上下文，其中包含必要 brush/composite 工作。后台样本是落在本阶段时间窗内的实际执行，不能证明全部由这一笔产生；没有把窗口外工作补到阶段内。

projection 中 `setupProjection/clear` 为 85/82 样本、`compositeWithProjection` 为 214/226；`prepareWrites` 82/93、`prepareFreshReplica` 54/58、`sealImpl` 32/42、`commitLocked` 31/31。后四项是重叠 inclusive 上下文，**不能相加**。完整互斥机制交叉表见 [actor-mechanism-summary.json](actor-mechanism-summary.json)。

undo/redo 的当前样本分别 43/29、90/82，upstream 为 6/0、13/10；采样过稀，不做精确百分比分摊，零样本不等于零成本。当前 redo 中 projection 占 65/67 个样本，支持先处理共同 projection 路径，但不是收益证明。`__ulock_wait2` 等叶符号即使标为 Running，也不能据此换算等待时长或认为锁成本全部可删。

## 数量反证：少建 session 并未少准备页

[去重阶段差值](mechanism-summary.json)均为 Stroke 结束减 Setup 结束；所有四过程都是 8 segment、4 update callback、19 次 projection update，最终 projection、layer、undo/redo hash 相同。

| 活着的实际 manager / 工作 | 普通两次 | persistent 两次 | 判断 |
|---|---:|---:|---|
| node operation session | 27 | 1 | 现有 opt-in 确实改变作用域数量 |
| node canonical commit | 1 | 1 | 否定“普通每个 dab 都 canonical commit” |
| node 页代际准备 / seal 页数 | 76 / 76 | 76 / 76 | 本例没有减少 |
| node 默认初始化 / native duplicate 页 | 56 / 20 | 56 / 20 | 本例没有减少 |
| node 写 pin 获取 / 归还 | 2420 / 2420 | 2420 / 2420 | 本例没有减少 |
| root projection operation session | 32 | 32 | stroke opt-in 没迁移 projection |
| root 页代际准备 / seal 页数 | 149 / 149 | 149 / 149 | 本例没有减少 |
| root 默认初始化 / native duplicate 页 | 60 / 89 | 60 / 89 | 本例没有减少 |
| root 写 pin 获取 / 归还 | 245 / 245 | 245 / 245 | 本例没有减少 |
| root canonical commit | 12 / 12 | 14 / 12 | 匿名 transaction 原来已按并发 client 合并，不能当成每 session 一次 |

node paint/original/projection 是同一 backend；root original/projection/image projection 是另一 backend。不能把六个观察角色加成六份工作。sealMetadataPreparations 随并发状态变动（node 普通 10、opt-in 3；root 1～8），未把它当稳定收益。

RGBA8 一页 16,384 B。两 manager 合计 **225 次代际准备、116 次默认初始化、109 次 native duplicate**。其中 root 占 149/225=66.2% 的代际准备、89/109=81.7% 的 native duplicate；后者为 **1,458,176 B**，四次 preclone hit 均为 0。它是 provider 逻辑复制工作，不是测得的 DRAM 流量，也不是 81.7% 时间。node 加 root 的累计初始化/复制字节为 3,686,400 B，普通与 opt-in 相同。

这解释了为何仅减少某类管理对象可能影响很小：可观测 session 从合计 59 降至 33，但页工作、复制和 pin 不变。此处不声称实测时延没有改善——本包没有对 opt-in 做合格时延对照。

## 必要成本、可构造目标与尚待证伪之处

当前 `KisAsyncMerger::setupProjection` 对 parent original 清区域，`compositeWithProjection` 再用 `KisPainter` 合成。clear 经 `fillRect→beginMutationBatch→seal`，合成经 `writePageStoreOperation→runCpuMutationOperation→prepareWrites→seal`；匿名最后 client 再 canonical commit。stroke 已共享 history transaction，普通操作仍各自 private mutation；二者不可混称。

对一次具备明确结束点的 merge，定义操作数 O、各操作页集合 Pᵢ、合法可共享写作用域 G。当前页准备量按实际操作/冻结边界累计；理想候选为同一 G 内按 `|∪Pᵢ|` 准备，再在真正需要的可见性边界结算。理论可省量是 `Σ|Pᵢ| − Σ_G|∪Pᵢ|`，还须扣除真实读者冻结、并发冲突、独立失败语义所要求的重新准备。现有 149 是实际页代际数，不是已测的集合并集；**目前不能给出可删页的具体数量**。

有限候选：让原 merge 工作单元在 clear 和随后的合成之间持有原 mutation 的写入责任，完成后统一交付。复用原 PageStore owner/准入/失败终结，不建立第二份状态账本。先从当前直接 parent projection 范围证明成立；temp projection、clone、mask/style、source-dependent、多个并发 merge 逐一明确适用/拒绝路径。不能在上层自行保存 page/budget 或直接放开默认 persistent。

必须保持：旧 projection/retained reader 隔离；64×64 页上不同矩形并发的冲突规则；清空后合成失败不能暴露半成品；copy-on-first-write/边缘页保留；实际 dirty/显示 cut；预算拒绝、重试、取消、晚 guard 与物理释放。整页默认 clear 已有语义删除，不能反向物化零页。当前 FreshCow 已可在 allocation 中同步复制，profile 中的默认初始化不能自动说成“先 fill 再 copy 的双写 bug”。

2420 个 node pin 的进一步归因是第二候选：`BoundedCursor::moveTo` 仅保留当前页，跨页再回访会重新取 guard；全目标 prepare 为保证像素阶段安全而提前执行。多 pin 不自动构成低成本可删工作，不能直接降到 76：跨 dab 顺序、并发、驻留峰值、释放终点和 pin 成本仍须验证。当前 CPU 证据优先支持完整 projection 责任，暂不据次数开启 guard/cache 重写。

## 下一包位置与验证矩阵

| 位置 / consumer | 原责任与待核定变化 | 必须保留 / 验证 | 本包状态 |
|---|---|---|---|
| `kis_async_merger.cpp` setupProjection/compositeWithProjection/writeProjection/resetProjection | 原 merge 生命周期能否覆盖 clear+所有合成；明确多层与 temp 分支 | 正常退出、各中途退出、clone 通知、显示 cut；不要只包单层 blt | 已定位；未修改 |
| `kis_painter.cc` blt/bitBlt 与 `kis_paint_device.cc` applyPixelOperation | caller 如何借用原责任及原失败传播 | 原 kernel/合成顺序、source 读取、selection/格式路径 | 已定位；待设计 |
| `kis_tiled_data_manager.cc` clear/writePageStoreOperation 与 extent/index delivery | clear 与像素写入在同一可取消边界交付 | 原 adapter gate、完整准入、部分页、旧缓存不暴露 | 已定位；待设计 |
| `KisTiledDataManagerPageStoreBackend.cpp` fillRect/runCpuMutationOperation/batch finish | 原 session/transaction/anonymous clients 的最小完整迁移 | sibling 不被错误取消、claim 重叠、retry、不重放 kernel | 已定位；待设计 |
| `KisPageStore.cpp` execution prepare/guard/seal；write coordinator/provider | 只在上述 caller 需要时调整既有借用范围；不先重写底层容器 | generation/reader/COW/预算/晚 pin/物理释放；实际字节与次数 | 已计数；可删量待证 |
| `kis_async_merger_test`、原完整 manager/PageStore 与 freehand fixture | 扩展真实反例，再做固定未插桩对照 | group/clone/mask/style、失败不交付、重叠矩形、像素/undo/redo；预测页数/字节与实测匹配 | 本包只跑所列诊断，产品安全矩阵未重跑 |

先取得 merge 单元内页集合与必要冻结边界的实际计数，得到可删数量，再实施最小 consumer 闭包。实现后未插桩当前/候选比较才能给收益；同时重验原控制，不能把与 upstream 的差距或 opt-in 数量变化算成本次加速。

## 可复现性、失败及阶段边界

脚本按 `build_fixture.py → run_profiles.py capability → run_profiles.py profile → export_signposts.py → analyze_profiles.py` 产生 profile；补充按 `build_mechanism.py → run_mechanism.py → summarize_mechanism.py`。runner 目录采用排他创建；重跑另开新包，勿覆盖本包固定样本。编译命令、环境选择、实际运行日志/库哈希、trace/XML、全部源码副本与差异见 [raw-manifest.json](raw-manifest.json) 和 raw-evidence.tar.xz；[verification.json](verification.json) 给出校验。

分析修正两次，均重读原 trace：初版错把共同 dispatcher `KisUpdateJobItem` 当 projection；第二版补上实际 history collector、retirement 及派生 Strategy finish 的 actor。两版旧分析器/输出都保留，最终表只用修正版。机制 fixture 初编缺少 `kis_datamanager.h` 导致 incomplete type，失败源码/命令/log 保留，补 include 后编译通过；没有运行失败或换样。

本包产品源码/测试增删 **0/0**，仅新增证据脚本、派生夹具与活动文档。原完整安全/资源/结构与 Fresh/H4 保持原资格、未重跑。M6 正式校准仍 **2/20**，联合 hit **0/4**、miss **2/16**；metadata 重构前实际驻留分母与完整 CP0/业务/GPU 证据仍欠。**M6/M7/M8 仍 0/3，persistent 默认关闭**。定位到真实热点不等于解决了它，也不等于 M6 性能资格已通过。
