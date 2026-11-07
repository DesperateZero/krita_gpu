# CP3 原 handoff 准备槽存储复用

父产品 `0a00bd3fe3fe71e44c04b987f9558bcd37f00dc6`。本包按 algorithm-cost-optimization skill 继续原 native handoff 的差异准备审查，冻结 [起点身份](start-identity.json) 和 [有限协议及预测](validation-protocol.json) 后修改产品。主阶段资格仍由 92 维护。

最终产品 `f0c40a5d195f1c20a0f915faaef18b1f3ee5b575`。本轮重复存储准备已消除；Rosetta native K16 有小幅直接配对收益，ARM K16 尚未确认时间收益，正式 M6 门仍失败。提交、实际增删及身份见 [交付](delivery.json)、[责任复核](closure-review.json)、[最终 Git blobs/库/输入核对](final-verification.json)。

## 必要成本、实际差距与范围

每次 handoff 必须验证新旧身份、独占物理 owner、预算和退休额度；准备失败不能留下 claim，安装区间不能分配或释放。原 ledger 已有 reusable PreparedBackingChangeSlot，并在 commit 后留下已收费的空 changes 数组和 detached target claim 节点。顺序逐页 handoff 重用同一个槽，但旧实现每页新建 changes 数组，并先销毁 detached 节点再分配同样的节点。

可达到的表达是：原槽的单元素 changes 容量经原准备参数转回同一槽；原 detached 节点改写 key，再插回原 preparedHandoffTargets，只有插入才成为 claim。大于一元素的旧普通批量缓冲区继续在冷槽复用时按原路径释放，避免扩大历史容量的保留。现有 ledger mutex 覆盖整个准备，不增加持久字段、owner、索引、队列或 authority。无需改变数据结构、合并独立页 claim、绕开容量收费或扩大批量边界。

对顺序成功 K 页且一个已完成槽可复用的用例，两类请求 `2K → 2`，K16 为 `32 → 2`，预测删除 30 次物理分配和对应最终 free，以及 60 次 parent/local 准备和 60 次结算。K1 无数量收益。该模型不是任意并发/取消情形的下界：同时存在 P 个 preparation 仍须 P 份存储，取消沿原路径释放 target 节点，普通 class change 可能替换 changes 容量。仍须保留新身份、class/domain claim、实际费用与保活尾。

父证据中的 public CPU 只能指出账务与分配的成本范围，不能把这些样本全部归给 native 两个站点。这里没有已校准单价，不预报时间下界，也不声称它足以承担 ARM/Rosetta K16 约 22.49/33.50μs 的原条件缺口。本包优先直接回用已存在原槽的存储，未启动另一轮容器重写。用新增父/候选 native 配对取得有限增量，再按原 Fresh 分母和原门重算；结果出来后不扩样或转做第二候选。

## 全部消费者与生命周期矩阵

| ID | 原位置/consumer | 理想表达与删除 | 必须保持 | 退出证据 | 状态 |
|---|---|---|---|---|---|
| H1 | prepareBackingHandoff → storePreparedChange | 空闲槽单元素 changes 容量经原参数移出/移回；删除每页 initializer-list 数组分配 | 源/目标/物理独占、reservation、generation、原 mutex；异常局部输入实际释放 | 数量 trace、额度耗尽行为、原物理 claim 测试 | 完成 |
| H2 | storePreparedChange → preparedHandoffTargets | 改写同一 detached 节点并插入原索引；删除每次先 free 再 new | inert 旧 key 不可查询；新目标仍独占；reserve 在安装前 | 原重复 claim/增长、取消重试、安装零 alloc/free | 完成 |
| H3 | releasePreparedClaims、commit/cancel、generic reuse、ledger destruction | commit 仍 extract；取消仍 erase；generic reuse 仍清理旧节点；最后析构仍释放实际容量 | 不改变物理 claim、费用释放时点、rollback/最后 owner | 原 joint/publication/storage、压力和 close 测试 | 完成 |
| V1 | 当前两架安全与结构 | 更新原 ownership；保留原完整消费者 | 无新字段、第二账本或公共 API | 同源 38 QTest + 6 probes、结构/工具自测 | 完成 |
| V2 | 原 public/native 28 数量进程 | K16 handoff 少 30 请求；其他 12 行请求不变 | 同义页数/字节/旧新读/复制/physical delta | 两个原顺序块、实际库/来源哈希；一处非目标寿命歧义保留 | 数量完成，局部寿命不确定性单列 |
| V3 | 未插桩父比较与原控制 | native 父比较 640 进程；public/M5/H4/native 各 320 | 固定 40 对、不加样、不改门、不并发测性能 | 配对块区间和原 family 下界分别裁决 | 完成；native 正式门失败保留 |

新增额度测试用原固定 metadata 限额、预热必要 reservation 容量，再用真实预留耗尽剩余空间；验证同一份测试二进制在父库请求额外容量而失败，在候选复用原已收费存储而成功。前两次测试准备的合同错误和全部日志见 [执行问题](execution-issues.json)，不能充当产品回归或优化收益。

最终安全轮曾在 Rosetta `testPageStoreTileSelectionFailure` 的 bpp16/allocated0/abort1 两行失败：全局额度预填后比 limit 少 12,976 B 和 320 B，均在调用目标选择之前。`waitForRetirementIdle` 只等原 Store 的读/退休/metadata idle；原 executor 的 detached root/task 最后释放与其他 Store 共享 process 费用，因此该等待不构成全局预算快照的静止边界。修复仅在两个读取全局容量的压力 fixture 中调用原 `kisDrainPageStoreReclamation`，保持同一额度、真实 filler、目标拒绝及旧/新像素断言。父/候选和双架的固定 4 个目标进程均通过；随后重新运行最终安全矩阵。失败批在 `pre-fixture-repair/`，没有开始性能采样，也没有将失败样本改写为通过。

## 理论与实际数量

原 ARM [28 进程/14 trace](summary.json) 全部正常退出、同义工作与加载库核对通过，共 333,111 个事件。[两块父/候选对照](quantity-comparison.json) 精确兑现 `2(K−1)` 模型：

| native handoff K16 | 父版本 | 实测候选 | 变化 |
|---|---:|---:|---:|
| 两个目标站点分配 | 32 | 2 | −30，−93.75% |
| 整个原账务准备的分配 | 36 | 6 | −30；另外四个必要容量保留 |
| 该准备的累计收费分配容量 | 3,456 B | 576 B | −2,880 B；不是峰值或驻留减少比例 |
| 完整事务控制存储请求 | 313 | 283 | −9.58% |
| controller 成功分配 | 279 | 249 | −30 |
| parent/local 准备各自 | 279 | 249 | 合计−60；结算同量减少 |
| 逻辑预算判断 | 624 | 564 | −60，−9.62% |
| raw free | 124 | 94 | −30，均落在 beginWrite 准备阶段 |
| deref / retained request | 575 / 166 | 575 / 166 | 必要保活未变 |

K1、native Fresh、三个 public 端点的分配/收费数量均保持。public K16 仍是 524 请求/446 controller 成功/988 准入，目标旧 working 引用链仍 54；本包不重新领取这些已结算项。两块 public 操作内/后续/窗口外释放分别 144/257/45 与 193/208/45，不能据其中一块推定统一释放时点。各目标对象、容量和来源见 [存储对照](target-storage-comparison.json)。

原汇总器的“全部地址都能唯一配对”断言被一条 native 记录拦下：phase13 的 epoch 准备对象与 phase15 的 history discard 对象复用同一地址，各 160 B，前一个 free 未被观测。相位切换短暂关闭 observer，允许 worker free 遗失；这只是可解释机制，无法从缺失事件确定实际释放点。两个对象继续标记歧义，不用于精确寿命推论；handoff ledger 的 phase11 和本轮数量模型没有此歧义。保留 [原脚本映射](trace-input-snapshots.json)、原失败及 [同一批数据重析](quantity-analysis-repair.json)，不补样、不删除记录。安全探针与实际最后释放的证明独立于这项观测局限。

## 未插桩 native 增量与置信范围

[父/候选 native 配对](native-parent-summary.json) 为 640 个成功进程，8 桶各 40 对、20 个事前顺序平衡块；每进程原 8 次 warmup 与 64 次测量，中位数进入配对统计。下表为补丁整体的 wall 延迟减少及双侧 95% 描述性区间，不是 8 桶 family 资格，负数表示候选变慢。

| 架构 / K | Fresh 延迟减少 | handoff 延迟减少 | handoff 节省 μs |
|---|---:|---:|---:|
| ARM / 1 | −1.06% [−1.44%, −0.01%] | −0.57% [−1.49%, 0.43%] | −0.068 [−0.177, 0.052] |
| ARM / 16 | −0.18% [−1.39%, 1.22%] | 1.79% [−0.12%, 2.87%] | 1.880 [−0.140, 2.963] |
| Rosetta / 1 | −0.88% [−2.21%, 0.44%] | 1.72% [0.07%, 3.01%] | 0.308 [0.021, 0.552] |
| Rosetta / 16 | 0.17% [−1.98%, 2.24%] | 1.99% [1.47%, 3.07%] | 3.287 [2.396, 5.078] |

ARM K16 尚不能在该 95% 区间确认延迟收益；Rosetta K16 的直接配对支持小幅改善。ARM Fresh K1 约慢 0.146μs，区间 [0.0004, 0.1773]μs，必须保留，不能因未触及 Fresh 分配路径就声称时间完全不变。K1 分配数无变化却仍有小幅时间变化，也说明总补丁、代码生成和样本波动不能精确归为某个分配的固定单价。

事前登记的 handoff 增量减 Fresh 增量对比在 K16 为 ARM 0.219μs [−0.734, 5.005]、Rosetta 3.958μs [−1.989, 7.214]，两者均跨零；该更严格对比尚不能确认 handoff 专属的时间收益。它与上表直接 handoff 配对回答不同问题，不能择优隐去。这里没有 native CPU 测量，不将 wall 变化称为 CPU 节省。

数量模型已完全兑现，时间回报约为微秒级。本包确认并移除一处重复准备开销，同时排除了它能独自承担原约 22.49/33.50μs 缺口的假设；不把目标站点 −93.75% 的次数变化冒称整体管理成本或延迟降低 93.75%。必要保活、物理/身份决策和其他 metadata 准备仍然存在。

[原 public 父比较](parent-comparison-summary.json) 另有 320 个成功进程、每桶同样 40 对/20 顺序块。吞吐候选/父为 ARM K1 1.0002 [0.9907, 1.0201]、K16 0.9956 [0.9803, 1.0178]；Rosetta K1 1.0022 [0.9909, 1.0113]、K16 1.0007 [0.9923, 1.0097]，双侧 95% 区间均跨 1，未确认变化，不把不显著当作完全等价。ARM K16 配对 CPU 节省 −0.087μs [−2.671, 4.373]，也未确认变化；Rosetta 线程时钟仍未校准，不解释其 CPU 数值。

## 原保护控制、正式门与剩余预算

[固定 M5 Fresh](fixed-m5-fresh-summary.json) 四桶全部通过原单侧 98.75% 下界 ≥0.98。ARM K1/K16 吞吐比为 1.3248/1.1026，下界 1.3177/1.0474；Rosetta 为 1.4119/1.1324，下界 1.3831/1.1053。[H4](fixed-m5-history-summary.json) 也全部通过：ARM 1.5009/1.4030，下界 1.4646/1.3718；Rosetta 1.4773/1.4656，下界 1.4651/1.4463。

原 [native selector 门](latency-paired-summary.json) 沿用每桶 40 对、单侧 98.75% 下界和原阈值，没有补样：

| 架构 / K | 相对当前 Fresh 延迟减少 | 下界 | 原要求 | 裁决 |
|---|---:|---:|---:|---|
| ARM / 1 | 4.40% | 4.03% | ≥20% | 失败 |
| ARM / 16 | 13.55% | 12.06% | ≥30% | 失败 |
| Rosetta / 1 | 3.89% | 2.42% | ≥20% | 失败 |
| Rosetta / 16 | 14.50% | 13.98% | ≥30% | 失败 |

这些当前 selector 比值不能与上一包的 11.99%/12.60% 相减来计算本次增量；本次增量以同时冻结父库的 native 配对为准。全部 1,920 个未插桩进程退出、语义、实际库与前后输入哈希通过，实验按事前规模停止。

当前边际中位数作条件规划：ARM K16 Fresh124.614μs/handoff107.240μs，Rosetta195.615μs/166.302μs。若 Fresh 不变，handoff 仍需另减约 **20.01/29.37μs** 才到 30%；若两边等量削减共同成本，则需约 **66.70/97.91μs**。这是边际条件预算，不是配对置信裁决，也不证明这些成本可删。本轮 1.88/3.29μs 的直接配对点估计远小于缺口，不能把局部实现闭合写成 CP3/M6 闭合。

剩余 handoff beginWrite 仍有 108 个 controller 成功分配，其中 owner ledger 仅 6 个/576 B 累计收费容量；metadata publication 32 个/51,456 B、working values 16 个/7,424 B、write protocol 38 个/16,096 B、descriptor16个/1,280 B。共同 seal/commit 仍有 279 次 deref、handoff314 次逻辑准入。下一优先在原 `prepareRecoverableWrite`/工作投影和共同 seal/commit 上补 native 独占 CPU、等待与必要成本账，先证明可删预算；这些容量/次数不是时间占比，也不直接授权下一轮容器重写。已完成槽复用、作用域借用和六类重复扫描不重领。metadata 同义实际驻留分母、CP0 required、TSAN 补充资格及 M6–M8/BR1 后续资格保持原状态。

## 安全、复杂度与复现

最终双架 38 个 QTest 进程为 **11116 passed、0 failed、0 skipped**。另 6 个原资源探针分别记录每架 31,080 个 joint install、28 个 publication install 区间零 alloc/free，以及 24 个 storage 边界。4 个 funded-capacity 对照进程和 4 个压力 fixture 对照进程单列，原预期父失败及中途失败都保留，不能计入最终全绿测试数。结构为 87 TU/2211 APIs/28930 逆边/27 callbacks，原 21 manifest/25 ownership/16 runtime census/19 intrusion 及 6 工具自测通过。

生产 1 文件 **+23/−6，净+17**；测试 2 文件 +72/−0（新行为测试66行、全局压力边界6行）；ownership +1/−1；派生 inventory/callgraph +2131/−1681。没有新增字段、热记录容量、业务 API、第二 owner 或恢复域。较大旧 changes 容量继续冷缩减；保留的节点和单元素数组仍按实际物理容量收费到最后释放。

复现使用 [源码补丁](product.patch)、[原工具来源](reused-tools.json)、各 runner 保存的命令/退出/timeout/reap 和 [最终身份](final-verification.json)。机制分析保留原 observer 的相位间隙局限，时间实验使用未插桩原端点。所有成功、失败、事件/映射/符号、修复前脚本和输入身份见 [原始证据包](raw-evidence.tar.gz) 与 [逐文件 hash 清单](raw-evidence-manifest.json)；编译镜像和对象仍保留本机。有限 H1–H3/V1–V3 工作包完成，未通过的原门独立保留。
