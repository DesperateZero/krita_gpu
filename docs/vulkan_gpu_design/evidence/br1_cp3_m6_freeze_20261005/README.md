# CP3：M6 安装与结构收口，性能候选未过门（2026-10-05）

产品提交 `500fd0702cfa07ba447d538fb9aad2b086e3160f`，父 `25ae0dbf8149e8c6620fc5a42d3b15b957bc37b3`。当前执行/资格仅见 [92 §16.114](../../92_br1_m6_m8_execution_baseline.md#cp3-install-containment-delivery)。本批关闭三个实际阻塞：成功 handoff 安装中的两次 free、memento 私有存储 include 越界、tile bridge 引用越界。**CP3/M6 尚未完成；M7/M8 资格和 persistent 默认策略不变。**

## 原责任与修复

- 父探针 `install-arm64-01.log` 为 alloc0/free2、actual exit3；`install-arm64-stack.log` 显示 free 来自 `KisPageOwnerLedger::releasePreparedClaims` 的两个 prepared index node。成功 commit 在原 slot 中接收预留容量的 node handles，马上撤销原逻辑/物理 claims；节点实际收费保留至下次冷 slot 复用或 Ledger 析构。最多两个节点，不增加 cleanup 队列或第二 claim owner。原 cancel/generic 清理及容量拒绝 rollback 保留。
- 完整 paid/unpaid `KisMemento` 分配、默认像素保存及释放实现移入已有 PageStore history TU，两端共用 prepare/copy/free 政策；原 ABI、正常模式及失败保护保持。移走的 97 行不计删除收益，私有存储 include 恢复原上限 0。
- 四个 tile lease caller 共用一个私有意图转换，保留原 ReadSelection/ReadCache/Write 和 dormant cache，bridge 标识恢复 9、include 1；没有新增公开/受保护 API 或 tile 字段。

生产六文件 **+136/-124，净+12**；Ledger 的有界收费存储为保证成本，memento 移动单列，不能从净行数领取性能。审计三文件 **+25,766/-18,203**，其中 ownership 一行、其余为生成物；见 `candidate.patch`、`convergence.json`。

## 当前验证与身份

`build-02.log`、`build-freehand.log` 和 `build-vulkan-foundation-02.log` 绑定当前源码。主 CPU 构建为 universal/RelWithDebInfo，LIMIT_LONG_TESTS=ON；未注册长测试不计通过。Vulkan 使用既有 `_build` 的 foundation ON 配置实际重建，兼容检查没有授予 GPU 产品/性能资格。

`matrix-03-{arm64,x86_64}` 每架完整运行16个目标，各5335/0/0；`read-baseline-*` 各45/0/0；`business-*` 的正常、cancel、四类拒绝、24MiB压力和8MiB取消各11/0/0；`vulkan-*` 各14/0/0。共38进程 **10,810/0/0**，全部 actual0/reaped、无超时、加载指定库。不同范围分列，init/cleanup包含在Qt totals中，未与旧源码或诊断样本累加。

`install-results.json`：两架各31,080个真实共同安装区间（1/4/8/16 BPP，1/64/65/129页，五route，commit/cancel及两类冲突控制），全部 alloc0/bytes0/free0；共享Qt正控制实际分配4次。探针复用原 diagnostic/friend 边界，没有添加生产分配开关。binary/interposer SHA、命令及当前image SHA见各 `install-final-*/build-identity.json`。

`checkpoint-review.json` 审阅旧源 checkpoint 至当前的34文件差集，关联已关闭CP1/CP2与本批具体责任；`baseline-before.json` 保留旧门。随后才刷新源码 checkpoint；不提高ratchet。首次刷新后的图因ownership输入更新而拒绝，原日志保留；重生成后 `architecture-final.log` 和 `architecture-before-commit.log` 通过：21manifest/25ownership/16census、2186 APIs/28191 edges/27 callbacks、19intrusion。`tool-selftests.log` 六项通过。

`final-verification.json` 将全部最终 source SHA 对应产品 Git blobs，并复核两个构建目录的实际运行库、测试、Qt、probe和harness；产品tracked树干净。矩阵运行时为父HEAD+明确diff，提交后以blob核对到上述产品commit，不把父HEAD误写成最终代码。

## 性能阻塞与下一有限端点

`latency-paired/protocol.json` 在运行前冻结40对、四桶顺序轮换、每进程8个warmup+64个测量操作，诊断关闭；独立配对单位为进程，固定样本量不延长/剪裁，20000次配对bootstrap，单桶单侧98.75%、四桶整体至少95%。两侧都是当前同一生产库，唯一差异为既有 exact alternate 的可用性；每次完成真实 native first-write/full write/seal/canonical commit。setup和验证/close单列。H=0 retained history，同时保留一个相同的旧exact验证capture；N=K，B=4。**这不是固定M5回退、upstream、stroke E、P95/P99或完整正式M6性能裁决。**

| 架构 | K | Fresh中位数 | handoff中位数 | 配对延迟降幅 | 单侧98.75%降幅下界 | 要求 |
|---|---:|---:|---:|---:|---:|---:|
| arm64 | 1 | 32.69μs | 35.06μs | -6.59% | -7.73% | ≥20% |
| arm64 | 16 | 378.44μs | 398.05μs | -5.18% | -5.69% | ≥30% |
| x86_64 | 1 | 52.77μs | 56.32μs | -6.49% | -7.46% | ≥20% |
| x86_64 | 16 | 596.17μs | 623.27μs | -4.75% | -6.09% | ≥30% |

全部320进程actual0/reaped，23,040操作含2560 warmup；像素、地址复用、physical delta和close全部正确，输入hash不变。四桶均未达标，所有样本保留；负降幅意味着handoff更慢。表中时间为各组进程median的median，降幅按配对log ratio求median，两种统计不混算。

额外 `handoff-phases.cpp` 使用已有opt-in timers，arm64每个variant/K各64操作，`phase-summary.json` 保留全部阶段。K1 recoverable prepare约9.25μs、install0.667μs；K16 prepare118.96μs、install9.35μs。诊断开销及嵌套interval不可求和/当收益；只将下一排查限定到 `prepareWritePlanLocked → prepareBackingHandoff / preparePublicationImpl` 的原冷准备，不推定某一个分配已被因果定位。

下一包先审查这条共同准备责任，减少重复候选/工作而保留严格revision、claim和失败保证；不加新selector/公共结果层。回修后复验受影响语义与实际allocator，再按冻结规则测收益。固定 `5173c807c87b` 的同依赖 Fresh/history ≤2% 控制、common metadata record实际驻留≥25%与重构前同义分母、CP0完整required清点/正式样本仍开放。不能以本批layout ceilings、源码移动或净删行数替代这些门；M6通过后才执行M7主包。

## 失败保留与复现

`matrix-01-arm64` 的实际test通过但DYLD变量在system arch前被剥离，launcher因未加载指定库退出1，不授资格；最终把loader环境设在arch后的env。`matrix-02-arm64` 属修复free之前的源码，不计最终矩阵。最初性能harness缺完整类型/header/API，三个编译失败日志保留；修正的是证据源。Vulkan第一次缺既定MACOSX_DEPLOYMENT_TARGET=12而configure失败，补齐既有环境后实际重建成功。

编排脚本拒绝覆盖目录；复现应使用新证据目录/round。`build_probe.py` 使用当前真实CPU目标的compile/link flags；`run_matrix.py`、`run_selected.py` 保存PID/command/实际exit/库装载与前后hash；`run_latency.py` 先写协议再运行。`analyze_latency.py` 重算到新文件，与原 `analysis.json` 逐字节相同，不覆盖失败样本。原构建日志的尾空格及patch上下文空行保持原文，Git whitespace检查单列这些数据，不规范化证据；源码、脚本与活动文档检查通过。局部二进制/objects不提交，路径、SHA和重建命令保留。未重跑CP1已结算的默认abort或长压测；TSAN仍Inconclusive。
