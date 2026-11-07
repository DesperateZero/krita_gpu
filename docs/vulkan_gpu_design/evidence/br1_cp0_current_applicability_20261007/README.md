# CP0 当前业务对照、required 清单与真实 archive 容量补证

本轮推进了三个具体事项：重新取得当前普通 freehand 的同依赖 upstream 对照；把 required 责任落实到 31 组代码/证据清单和 48 个既有数值桶；补上真实 archive 容量耗尽与恢复的安全测试。**没有生产加速，M6 仍未通过。** 当前裁决在 [92 §16.140](../../92_br1_m6_m8_execution_baseline.md#cp0-current-applicability-delivery)。产品起点 `38834c4e2612c819f9d088dfd59c59889f295a49`，测试提交 `128fb32a71`，文档父 `bb479be2c085d8363f42d2ec5ceaeafd16d0fee8`；未读 archive，未 push。

## 当前普通业务存在大于微路径的成本差距

[事前协议](PLAN.md)复用 CP0 20261003 的实际 upstream `9a24ae0d8c070884fb013594191002e1a1b39a19` 构建、四个同字节夹具/资源文件和 15 个一致构建选项。当前 build 实际执行 Ninja 后无需重编。先四个能力过程，再两架各 24 个独立配对、12 个顺序平衡块，共 **100 个正常退出过程、300 个 QTest passed**。全部像素摘要、8 个输入 callback、4 个更新 callback、一次 finish/strategy 析构、undo/redo 和 image 最后强引用检查通过；实际 dyld 路径及依赖集合逐过程相符，hash 在整批前后相同。结果、协议和 source/runtime 身份见 [summary](summary.json)、[source](source-identity.json)、[runtime](runtime-final.json)，所有原始过程另存 [归档](raw-evidence.tar.xz)。

以下为预注册顺序块 log latency ratio 的几何平均，括号是各端点独立、未经 family 调整的双侧 95% bootstrap 区间；不是中位数比，也不是 throughput。x86_64 是 Rosetta。

| 当前/upstream 时间比 | arm64 | x86_64/Rosetta |
|---|---:|---:|
| stroke → projection-ready | **2.258 [2.107, 2.426]** | **2.318 [2.180, 2.448]** |
| pen-up → projection-ready | 2.285 [2.131, 2.458] | 2.352 [2.210, 2.485] |
| undo + drain | **6.490 [6.129, 6.833]** | **6.881 [6.399, 7.388]** |
| redo + drain | **7.688 [7.441, 7.917]** | **6.482 [6.264, 6.698]** |
| owner teardown | 2.183 [2.070, 2.296] | 2.089 [2.021, 2.158] |
| fixture total | 1.000 [0.994, 1.006] | 1.011 [1.001, 1.022] |

stroke 当前/upstream 边际中位时间为 ARM **8.103/3.541 ms**、Rosetta **13.712/5.955 ms**；undo 为 **0.465/0.068 ms** 和 **0.817/0.115 ms**。undo 倍数很大但绝对时间短，不应压过 stroke 的优化优先级。total 被 setup 主导，不能掩盖操作回退。这是当前对照差距，不能与 10 月 3 日不同批次绝对时间相减宣称优化收益。

本批未测 canvas-visible、first-dab、P95/P99、独立 M/K、完整资源峰值或自然 handoff 来源。普通策略未 opt-in persistent，原 DataManager 仍接 PageStore adapter；它不等于“整个 adapter 关闭”。本结果足以选择下一诊断责任，但不能直接适用合成 read/write 的 1.2/1.3/1.5 上限，也不授正式 BR1-PERF。

## 算法判断和下一责任

必要工作是实际像素、按输入顺序的混合、正常 projection 更新、一笔 undo、合法旧值及全部失败/退出。可构造的目标是同一未发布段共用原准备与 pending、按真实可见性冻结，而不是随每个局部访问重复完整协议；任何 independent rollback 或显示/旧 reader 边界仍须保留。当前普通路径的 `writePageStoreOperation → write batch/mutation → seal/private publication → canonical commit` 与 undo 的 `restoreHistory → rollback/rollforward → restoreRetainedEpoch → index/projection` 是下一整段成本账的入口，见 [代码索引](../../br1_modification_guide/CODE_INDEX.md#cp0-current-applicability-code-index)。

若仅把达到 upstream 时间作为目标，stroke 需要下降约 **55.7%/56.9%**；这只是 `1−1/ratio` 的目标距离，**不是已经证明可删除的算法成本**。没有各段调用数、自身 CPU、冻结原因与同义消融，就不能把 2.3× 全归因于管理或许诺上述加速。下一先测完整业务责任的重复工作，再选可删预算；不要重新猜改已经结算的 provider 借用/引用计数。旧同义 M6 fixture 的统计分辨率问题仍独立存在。

## 清单发现并补齐的实际缺口

[机器可核清单](required-census.json)及 [生成器](census.py)登记 31 个合同组、15 个源码文件、8 个实际测试日志；48 个既有数值桶为校准 20、hit 4、miss 16、Fresh 4、H4 4。行内保留 required 轴、真实 consumer、测试方法/行号、实际 PASS 行数、适用阶段及欠证；这不是全部轴的笛卡尔积覆盖证明，也没有补齐所有正式 workload 的预注册。**完整 CP0 仍开放。** 未支持 SSD/GPU alternate 不能当正例，但 SSD 耗尽/恢复安全不能删除。

原 `exactGenerationArchivePreservesPublishedAuthorityOnFailure` 只使用注入失败。本批按 [补证方案](SSD-PLAN.md)保留原 ample 场景，加入 1/4/8/16 BPP 各一页实际 archive byteBudget：第二代归档在注入失败已消费后再次因真实容量拒绝，原 archive 全页内容、current 和 retained old View 不变；forget 旧 record 后，同一 store/archive 重试成功并核对整页，旧 View 仍可读；最后 records/retention 和原 outstanding capabilities 清理完成。

两架完整 ReferenceTest **各 946/0/0，合计 1892/0/0**，均 actual exit0/reaped、无 timeout，source/runtime 前后相同。只改测试 **1 文件 +61/−5**，生产 0；它证明配置的 archive payload 容量拒绝及恢复，不证明物理磁盘 ENOSPC、全进程统一 SSD 压力或 SSD handoff。当前阶段状态和正式业务默认未改变。

## metadata 门和剩余限制

[分母审计](metadata-denominator.md)确认当前 footprint 同时含 sizeof 型 used 数据、实际 map/index capacity 和 arena block 数据，其中有重叠及未覆盖目录/control；直接相加会重复收费。最早检查的 Git arena checkpoint 已含 arena，固定 M5 更不是该重构前版本；本轮没有取得可复现实测的合格旧分母。保持 **≥25% 未通过/未测**，不填零、不选空 upstream，不把安全收费测试转成结构性能资格。

原生产 11180/0/0、六资源、结构和 Fresh/H4 八桶保留对应冻结证据，未重跑；新 1892 不与它们相加宣称全矩阵。原正式校准仍 **2/20**、联合 hit **0/4**、miss **2/16**，M6/M7/M8 **0/3**，persistent 默认关闭。

配对前 CMake 配置解析错误（没有启动测试）与修正前脚本、清单两次路径核验错误、全部构建日志/警告均保留；测试与性能运行没有失败样本。产品提交只包含上述测试，外层原有 gitlink 修改未纳入文档提交。证据完整性、身份复核和派生结果复算见 [verification](verification.json)。
