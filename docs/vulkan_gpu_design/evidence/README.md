# Evidence 提交与恢复

## 继续 M6 的检出点

外层和内层工作分支均为 `codex/m6-native-baseline`。外层树的 `krita` gitlink 固定 CPU 产品 `0fd96f2fa3f24e70c1652ea17b8cc87192acf6d2`。两仓独立，外层没有子模块 URL。取回两仓后，以 `git rev-parse HEAD:krita` 和 `git -C krita rev-parse HEAD` 相等为准。个人远端分别是 `DesperateZero/krita_gpu` 和 `DesperateZero/krita`。登记历史价格时仍须注明对应构建和端点。

| 要继续的工作 | 使用的入口和材料 |
|---|---|
| 正式 M6 | [92 §1](../92_br1_m6_m8_execution_baseline.md#native-cpu-baseline)和 [§6.1](../92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)。固定 M5 原包含完整校验清单、失败、双架和性能协议。[M5 修复基线](br1_m5_repair_20260925/README.md) |
| CPU 基线取证 | 从外层执行 `python3 docs/vulkan_gpu_design/evidence/manifests/verify_native_cpu.py`。它从随仓原始包读取全部三组样本，在临时副本中删除三份结果和验证协议中的预测摘要，保留预注册样本顺序，重算后逐字节核对四份文件。[冻结清单](manifests/native-cpu-0fd96.json) |
| 独立优化 | 投影融合的生产报告、原失败、统计输入及整包保留。笔刷 Alpha Darken、固定源、stroke、预算与真实储存从[责任索引](../README.md#evidence-scope)进入，各自沿用其有效端点。其他专题的回执按原构建查阅。 |
| 后端能力扩展 | 使用 [105 设计](br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/UNIFIED_BACKEND_DESIGN.md)和[设计验证器](br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/unified-backend-design-105/verify_design.py)。正式 M6、M7、M8 和硬件能力仍按各自门禁验收。 |

### 按原路径取回历史证据

[本次处置回执](manifests/cutover-pre-native-20261107.json)登记两份冷存对象的大小与 SHA-256。[压缩路径清单](manifests/evidence-paths-pre-native-20261107.jsonl.gz)每行记录从 evidence 起算的相对路径、字节数、来源、Git 模式和内容摘要。专题报告里的历史脚本、原始日志或改动若已移出工作树，可用原链接的路径查此清单。未完成逐项语义审阅的材料保留原件供定向核查。

- 来源为 `git` 时，从外层历史提交 `ca5ddcfc32eba733d7b1d0039517aa2b5a91a8d6` 用 `git show <提交>:docs/vulkan_gpu_design/evidence/<相对路径>` 读取。历史分支 `refactor/brush-s2-predefined-sanity` 和增量包 `docs-history.bundle` 均保存该树。异机导入该包需要外层个人远端已有的 `3b940b4f885f673c8e491a02ef561b829f92fc98`；可用 `git bundle verify` 验证前置对象。
- 来源为 `tar` 时，`untracked.tar.zst` 的成员名是从外层仓库起算的完整路径。在临时空目录从指定包解出所需成员，对照清单验 SHA-256。重复内容、未完成实验和原失败仍按原路径区分。本机两份冷存均在 `build/m6-baseline-cutover-20261107/`。截至本次清理，冷存仅有本机回执。
- 11 月 5 日回收的采样沿用[上一份恢复账](manifests/cleanup-pre-m6-b1c2f6129.json)。若其恢复程序需要后来移出的 tar 分片，请在上述 `ca5ddcfc3` 的独立工作树中运行原程序。源码仓的 P/U/N、固定 M5 和 upstream 对照提交均可从当前内层提交的历史定位。

日常 M6 通过[责任索引](../README.md#evidence-scope)选择证据。一次结果需要分别决定两件事：哪些结论今天还有消费者，哪些文件用来恢复或检验原结论。实验已经结束时，原假设、原始失败和最终比较仍须能对应到同一个源码、输入与运行端点。

| 文件承担的责任 | 进入 Git 的内容 | 大件、混合包与例外 |
|---|---|---|
| 设计、判据与回执 | 写明责任、作用域、版本和端点的报告；预注册判据、样本顺序与停止条件；最终结果、失败清单、源与库身份、校验值 | 活动索引只引用当前适用的结论。旧价格与否决理由留在原包。逐事件 JSON、整份编译数据库和原始 trace 单列 |
| 可复算样本与脚本 | 得出结论实际读取的小型样本集、分析程序和运行说明。以干净目录复算结果并比对哈希；保留全部预注册样本和原失败 | 可重跑分析与可重跑目标二进制分开验收。依赖本机绝对路径、SDK、库或硬件的 runner 登记输入与限制 |
| 实验改动和反例 | 产品实现归内层源码提交。孤立实验保留基准提交、应用顺序、经过重放的最小补丁/fixture、消费者及判别结果 | 累积 diff、整份 before/after 源树与已被 Git 覆盖的副本按路径、类型、模式和对象号建索引。无法定位基准的独有改动先保全，等待审阅 |
| 原始测量与故障记录 | 提交 manifest，记录样本范围、关键失败、对象大小、SHA-256、存储位置和取回办法。通过/失败收据同等保留 | 大日志、进程级输出、trace、原始包存于持久证据存储，按需取回。先验证成员内容和原路径，再给展开副本标记覆盖 |
| 构建产物与快照 | 构建命令、工具链版本、源码及二进制身份、需要保留的精确例外 | 对象文件、临时库和构建树默认留本地。若某个二进制被冻结门禁按哈希读取，须保全原文件或实际证明可重建到同一哈希 |

**新实验的提交单位。** 在 `evidence/<专题>/` 放报告和必要轻量文件，可按 `results/`、`replay/`、`changes/` 区分职责；大运行输出写到 `build/` 或外部证据目录。用明确文件列表暂存，核对 staged 文件与大小。原有冻结包维持原路径。失败日志、未跟踪补丁或 JSON 的去留，仅凭文件名无法裁决。外部对象状态区分“本机验证”“远端有回执”“干净机器恢复通过”。清理本地原件以最后一项为准。

## 生成物与旧采样的清理

外层仓库对任意目录的 `*.o`、`*.dylib` 应用 Git 忽略规则。独立检出的内层仓库使用自己的忽略文件；本工作区已在这些仓库的共享 `info/exclude` 加入同样两行，覆盖链接工作树。新建内层克隆时也要设置这两行。实际运行仍需的已冻结库按精确路径和 SHA-256 保全。

新的逐轮原始样本写到 `build/` 或忽略的 `raw-samples/`。供正式结论复算的有限输入、门禁、最终结果、失败证据和源码身份留在已审核清单。旧版逐次运行指标、事件流、栈、逐运行装载表可以从工作树清理。同名的 `result.json`、`identity.json` 或 `RUNS.json` 需核对内容和消费者。某些旧探针把完整源码差异嵌入每次运行的 JSON；先按内容保全独有差异，再清理展开副本。新探针可只存一份差异并在每次运行中引用其哈希。

[2026-11-05 清理回执](manifests/cleanup-pre-m6-b1c2f6129.json)记录实际删除、旧 JSON 的恢复来源与当前基线验证。早先的全目录传输估算仅对应清理前快照。需要重放那一版时取其冻结提交及相应原始包或本地冷存残余。

## 已审核的首包

CPU 产品 `0fd96f2fa3f2` 的白名单包含 11 个已跟踪散文件和从已跟踪压缩包取出的 3 份样本。另带一份来源清单，共 15 个文件。独立 Git bundle 为 112,908 字节，可在空仓库取回。分析所需的 12 个校准、144 个确认、160 个 Fresh 控制样本齐全；空目录重新生成的预测、验证协议、联合结果和 Fresh 结果与原件逐字节一致。[逐文件清单、来源与复算回执](manifests/native-cpu-0fd96.json)

要追查原始过程，可另取 `CHECKPOINT_91_RAW.tar.gz` 与 `JOINT_PRICE_RAW.tar.gz`，共 10,623,293 字节。原运行门禁 21 个输入中，19 个在两包成员中找到相同内容；另两个精确二进制 `fresh-P` 和 `kis_tiles3_cpu_baseline_test` 在本机已核对哈希，合计 435,080 字节。真机重跑还依赖相应构建和运行环境。原归档、二进制及其他失败用例均保留。[原交付](br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/write-unit-accounting/native-result-construction-104/production-integration/REPORT.md)

## 首次历史盘点的边界

盘点作用域为外层 `796960143` 的 evidence 树及同目录未忽略的未跟踪文件。逐路径处置表保存内容哈希、恢复来源和本地文件类型/模式。比对对象包括两仓本地分支可达 blob、当前受跟踪 tar 普通文件成员，以及本次未跟踪集合中的同内容文件。跨包字节相同只用于恢复文件内容。各条路径的实验身份、消费者和结论仍分别登记。目录外的旧工作树、外部依赖以及机器环境另行保全。[数量、压缩实价、路径索引校验值与远端状态](manifests/evidence-audit-796960143.json)

独立收据可先走个人远端的证据 ref。若需保留外层完整提交关系，对已经核对的 personal 端点，归档 ref 可先推 `d277af01c8e6`，再快进至 `796960143`；两批实际生成的本地 thin pack 分别为 1.422 和 1.286 GB。推送前重新核对端点和现有 ref。内层产品提交须在其个人远端单独可取。全量未跟踪对象如需远端冷存，可按内容分块上传，登记每块 SHA-256 与位置，并从异机恢复。当前清单记录本机结果，远端交付待执行。
