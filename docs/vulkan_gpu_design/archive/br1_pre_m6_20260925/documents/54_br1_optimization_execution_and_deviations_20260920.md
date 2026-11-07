> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 优化实施、实测校准与偏差登记（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

按 52 的完整 P1–P6 目标推进，39 的 M/K/X/E 与 CPU 同义管理不劣性判据保持不变。
本记录区分代码切片、定向正确性/结构断言与性能证据；文档口径校准不等于性能目标达成。**BR1-PERF 未结清。**

版本边界：本文“当前/最终”指 D1 的 hash 检查点，不自动描述后续工作树。D2 的新阶段证据、事务起点 API、
正/负收益与诊断扰动见 [55](55_br1_d2_phase_measurement_and_atomic_transaction_begin_20260920.md)，不改写本文历史数据。
后续同步 prepared metadata publication 及首版偏差/修正见 [56](56_br1_prepared_metadata_publication_20260920.md)。

## 1. 当前切片 D1：删除/default 语义化

切片前源码：`KisPageStore::commit()` 对 removedPages 调用 `ensureDefaultPageLocked()`，
`restoreRetainedEpochImpl()` 也为缺失的 default version 申请/填充像素 backing。与 53 的历史热点归因一致。

当前工作树已把这两处改为 `ensureVirtualDefaultLocked()`，default revision 切换和同步整页覆写 adoption 的 base 也允许
虚拟 default。其 exact 内容由被保留的 surface format/default revision/descriptor 决定；仅 Published/Historical default
允许无 replica、无物理 authority，普通像素版本不能借此绕过 authority/recoverability 不变量。
真正需要 default 像素的通用访问仍通过 `MaterializeDefault` 延迟附加 backing，不改变 exact identity 或 generation 高水位。

预期与实验边界见 [实验清单](../../../evidence/br1_optimization_20260920/README.md)。先消除删除产生的新像素工作，再检查成本是否
转移到后续读取/首次写入、history metadata 或 adapter 索引。虚拟状态必须保留精确 default revision 和 generation 高水位。

## 2. 结果与偏差状态

| 项目 | 状态 | 证据/下一步 |
|---|---|---|
| D1 前基线 | 已保存 5 次，仅诊断 | Qt 26.059 / 26.451 / 26.789 / 26.629 / 26.556 s；median 26.556 s，range 26.059–26.789 s；全部 stress 通过，不与旧 upstream 单次值构成配对 |
| D1 结构与安全性 | 当前切片回归通过，非 BR1 全量结清 | 最终 Foundation 24、Reference 31、完整 tiled-manager suite 36 项通过；init/cleanup 计入 Qt totals |
| D1 后基线/采样 | 已测诊断，非主干资格 | 首轮 5-run median 16.528 s；补齐 overlay 语义后的最终 5-run median 16.212 s；独立 profile/1、5 ms 采样见第 5 节 |
| CPU M 不劣性与 K/E 全矩阵 | 未完成 | 继续 P1/P6；本切片 stress 不替代整体目标 |

没有实测的收益不写成已实现；实验失败、未见收益或成本转移也保留记录，随后依据证据调整研究顺序。

### 2.1 结构/正确性证据及范围

| 原件 | 覆盖 | 不能据此推出 |
|---|---|---|
| [after-foundation-v2.log](../../../evidence/br1_optimization_20260920/after-foundation-v2.log) | virtual default 恢复、物化版本/物理槽负例、高水位不回退、虚拟历史回收；24 passed | 所有产品并发/性能场景通过 |
| [after-reference-v3.log](../../../evidence/br1_optimization_20260920/after-reference-v3.log) | 31 passed；新增 removal/revision 不物化，旧 reader 和 retained default revision 保持正确，真正的两次 default read 各按需物化一次 | 通用 default 读已实现共享 guard 或零物化 |
| [after-targeted-tiles-v2.log](../../../evidence/br1_optimization_20260920/after-targeted-tiles-v2.log) | 1/4/8/16 BPP 的 fill/undo/redo/purge/trim/clear/default read 生命周期计数不增长；另含 sparse purge、default undo、adoption、save/reopen；10 passed | 全量 tiles3/CPU/OpenGL 套件或跨域性能通过 |

`after-reference.log`/`after-reference-v2.log` 为 30 passed 的旧测试集合，未覆盖新增 reader/default-revision 用例；该用例只引用 v3。
定向 tiles3 与 Foundation 的 v2 日志对应修正后的生产库；Reference v3 是补入新测试、重新构建后的复验。
首轮检查点的源码与测试/库 SHA256 见 [after-artifact-sha256.txt](../../../evidence/br1_optimization_20260920/after-artifact-sha256.txt)，不是最终检查点身份。

上述为首轮 D1 检查点。随后扩展的事务 default/clear 验证及修正，以
[d1-final-reference.log](../../../evidence/br1_optimization_20260920/d1-final-reference.log)、
[d1-final-foundation.log](../../../evidence/br1_optimization_20260920/d1-final-foundation.log)、
[d1-final-full-tiles.log](../../../evidence/br1_optimization_20260920/d1-final-full-tiles.log) 为准，分别 31/24/36 passed。
当前身份为 [d1-final-artifact-sha256.txt](../../../evidence/br1_optimization_20260920/d1-final-artifact-sha256.txt)，不覆盖首轮 hash。

## 3. 偏差与修正登记

| 编号 | 预期与实际偏差 | 原因、修正及复验 | 剩余边界 |
|---|---|---|---|
| D1-A | 初版希望生命周期零新 default payload；四个 BPP 用例均实际出现 16 次、期望 0 | history prune 的 TransactionOverlay read 在选择 prepared 覆写页前先物化 default base；改为先解析 prepared version，v2 四行通过 | 最终 stress 目标 manager 新 default 物化为 0；通用 default 真正消费仍会物化，长期/全产品成本转移待测 |
| D1-B | idle fused commit 应继续成立；初版 adoption 测试实际 fused counter 为 0、期望 1 | 历史回收把“有物理 authority”作为唯一资格，遗漏可精确恢复的 virtual default；增加受限分支，v2 通过 | 非 default authority 校验不放宽；回收总成本及积压仍待测 |
| D1-C | 新 Reference 用例应进入复验；首次编译调用了 private retained-root API，未形成新二进制 | 改用公开 `captureRetainedEpoch()`，重新构建后 v3 31 passed | 旧 30 passed 日志不冒充新用例已跑 |
| D1-D | 同一 TransactionOverlay 的 identity 查询和 acquireRead 应一致；新增用例发现删除后 query 返回 default，read 仍返回旧像素版本 | 保存失败 `d1-overlay-before-fix.log`；统一锁内 selector/surface 解析，先处理 prepared/removal/staged default，再物化；跨 provider 工作保持已捕获 exact version | 普通和 native 读共用同一语义，不以 cache 命中遮掩通用接口错误 |
| D1-E | overlay default revision 更新后，删除/空白再写应初始化为新 default；初次修正误要求所有普通写都有 Surface 记录，既有低层 fixture 4 项失败 | `d1-overlay-reference.log` 保留 27 passed / 4 failed；只在 removed/default base 分支解析 overlay 初始化描述，v2/最终 31 passed | 普通已分配页沿用完整 base descriptor，不扩大 API 前置条件；generation/旧 reader 安全边界不变 |
| D1-F | 从旧注释怀疑 history clear 还填充 default 像素；新增 1/4/8/16 BPP 用例在简化前已通过零 write-request/default-materialization 断言 | 源码追踪确认 full-page default fill 已下降为 removal，不能重复归功；仅合并为直接 removal 循环，删除每页 accessor/session 包装及过时注释，最终完整套件通过 | 该分支没有独立计时收益证明，不把前后约 0.3 s 差异归因于它 |

D1-A/B 首次失败原件 [after-targeted-tiles.log](../../../evidence/br1_optimization_20260920/after-targeted-tiles.log) 保留（5 passed / 5 failed），
不以成功日志覆盖。D1-C 编译失败只留有当时工具输出，没有单独归档文件；不得伪称已有完整编译日志证据。

## 4. 未结清范围

1. D1 后重复计时及独立采样已补齐，见第 5 节；同主干配对、固定页集/K/N/H、真实像素写和尾统计仍缺失。
2. 继续按 39 的 5.10 检查成本转移、交错导致的页数变化、采样扰动及关键路径，不把此次混合 stress 当完整 M/K/E。
3. 通用 default 共享读取、坐标 metadata 长期有界性、history adapter delta、production owner/cursor、mutation/permit 和
   安全免全局锁读路径继续按 52 推进；当前仍是复用 tiles3 存储、另有 PageStore 协议的混合管线，不称完全同构主干。
4. 最终仍须先冻结同主干 M 不劣性 profile，再提交独立 M/K/resident E 与真实写、尾延迟、drain/长压证据。
   GPU/UMA 性能为 `NotMeasured`；UMA 零迁移复制及 CPU 相对产品门禁不因 D1 改变。

## 5. D1 重复计时与新归因

机器/构建环境沿用 53；所有性能测试顺序运行，不与编译/其他测试并发。seed 12345、8 workers、1 BPP；Qt test elapsed
与进程 time 分列。下面的 before/after 非交替、非同主干配对，固定事件流也不固定线程交错和实际 page work。
只作切片诊断，不能授予 CPU M 不劣性、真实写 K、GPU/UMA 或 BR1-PERF 资格。

| 版本/无 profiler 运行 | Qt elapsed（s，5 次） | median / sample stddev（s） | peak RSS median（MiB） |
|---|---|---|---:|
| D1 前 | 26.059 / 26.451 / 26.789 / 26.629 / 26.556 | 26.556 / 0.274 | 343.31 |
| D1 首轮 | 16.026 / 16.283 / 16.593 / 16.586 / 16.528 | 16.528 / 0.246 | 210.34 |
| D1 最终（含 D1-D/E/F） | 16.006 / 16.212 / 16.211 / 16.350 / 16.253 | 16.212 / 0.126 | 211.61 |

最终相对 before 的中位耗时比 0.6105（下降约 39.0%）。两组 D1 区间重叠，不为 D1-D/E/F 单独计算因果收益。
RSS 是进程 peak，不是 live payload 或精确 metadata budget；此次结果仍不能证明长期退休/防重放集合有界。
原件与可复算数据见 [实验目录](../../../evidence/br1_optimization_20260920/README.md)、`summary.json` 和 `analysis.json`。

最终独立 profile 为 Qt **16.146 s**。以下 counter 仅覆盖目标 manager，不含 bitBlt 临时 source manager：default
materializations **0**，generic write requests **0**，read requests **1,043,134**，synchronous adoptions **1,500,864**，
commits **24,077**；该 manager 在销毁前的 pages/versions/replicas 存活终值为 **512/512/64**，不是累计创建数或 drain 后终值。
53 旧 profile 的 default materializations 为 1,260,800，adoptions 为 1,499,968；page work 近似但不逐操作配对。
删除的 payload 工作没有在该 stress 的目标 manager 内变成另一批 default materialization，但真正的 generic default 消费仍允许按需物化，
其覆盖由 Reference 测试单独证明；不能声称所有 default 读取或真实写都已零成本。

### 5.1 分操作和结构交叉验证

最终 opt-in profile 的执行体累计（跨 worker，非进程墙钟分段求和）：

| 操作/阶段 | body wall（s） | thread CPU（s） |
|---|---:|---:|
| history 总体 | 7.178 | 7.146 |
| clear-all | 2.449 | 2.433 |
| setExtent | 1.983 | 1.974 |
| history commit（history 的子阶段） | 2.700 | 2.690 |
| rollback / rollforward（子阶段） | 1.145 / 1.102 | 1.143 / 1.099 |
| purge history（子阶段） | 0.587 | 0.586 |

父级与子阶段不能相加。history/clear-all/setExtent 的 wall 与 thread CPU 仍接近，支持继续减少控制工作；
不排除短锁、自旋、唤醒或缓存争用，也不能把其他线程的测试锁等待占比称为可消除 CPU 时间。
分段图：[operations.svg](../../../evidence/br1_optimization_20260920/operations.svg)、
[history.svg](../../../evidence/br1_optimization_20260920/history.svg)，明确选择 `timed-02-d1-final.log`，不混入首轮图数据。

独立采样的互斥非等待 worker 栈占比：

| 结构 | 首轮 5 ms | 首轮 1 ms | 最终 5 ms |
|---|---:|---:|---:|
| canonical commit（扣除下列独立子类） | 26.71% | 27.29% | 26.63% |
| synchronous whole-tile adoption | 17.40% | 18.11% | 19.30% |
| history GC / release | 15.11% | 14.34% | 14.24% |
| history default prune | 5.98% | 6.48% | 6.25% |
| adapter index rebuild | 6.02% | 5.80% | 5.91% |
| canonical history restore | 6.19% | 6.01% | 5.60% |
| generic read/native refresh | 4.26% | 3.70% | 4.45% |
| derive extent | 1.47% | 1.74% | 1.80% |
| 其他 | 16.86% | 16.54% | 15.81% |

对应非等待样本数 2,793 / 15,667 / 2,606；采样运行 Qt 16.727 / 17.402 / 16.668 s，不用于性能 pass/fail。
首轮同版本 1/5 ms 的主要排序一致，最终 5 ms 也保留该宏观排序。不能把百分比乘 16.212 s 生成精确阶段耗时，
也不能把提高采样频率的额外运行当无扰动正式计时。图见
[sample-d1-final-5ms-structure.svg](../../../evidence/br1_optimization_20260920/sample-d1-final-5ms-structure.svg)。

### 5.2 继续研究：从宏观热点到可验证切片

`summarize.py` 对相同叶样本另作互斥实现路径分类，并与原解析器检查样本守恒。最终 5 ms 中：metadata transition apply
约 7.37%、完整 invariant 检查 6.06%、snapshot/lookup 3.95%、proof seal/revalidate 3.88%/2.03%、epoch prepare/root commit
2.07%/2.38%；PageStore commit/adoption remainder 仍为 11.97%/11.09%，未归入所选实现路径的残余约 28.97%。
这是第 5.1 节的另一切面，不能再相加，也不是已经测得的 self CPU 耗时。它尚不足以把 commit 总量全部归给锁、proof 或 root。

下一 D2 优先验证 **owner-held prepared metadata batch**：在 prepare 阶段构造一次精确 page delta、完成一次必要完整校验，
发布前复验可变化的 generation/writer/retention/provider 事实；不能只把 `apply()` 改为跳过 invariant 的入口来赚取上述 6%。
逐页 snapshot/preflight/apply 的重复集合构造和验证应由能力对象复用结果，reference 仍完整核对。

API 落地前必须证明：能力不可伪造、不可复制且一次消费；绑定 owner/transaction/base epoch/page revision/provider epoch；
prepare 后 reader、last-use、abort、provider reset 或同页变更使验证前提失效时，能在 root publish 前拒绝/重准备，不用
旧 snapshot 覆盖新活跃状态；所有新 root 引用的状态在可见前已可读；失败/取消不破坏旧 root。契约已同步到 33 的 6.1
和 52 的 P4，代码尚未实现。不要以长时间同时持有所有 shard 锁或 root-CAS 重试风暴代替当前开销。
不同页锁外准备，同页局部独占，短发布窗口与有界退休仍是目标，当前全局协调不能因 D1 通过而称为无锁。

D2 定向实验需固定 K/N/H、数据格式、真实变化/alias/no-op 三类工作，拆 prepare、内容判断、seal/validation、preflight、
root 构造、publication、adapter、retire/drain 的 wall/CPU/调用/分配计数；与同一原 workload 的无 profiler E 对照。
随后推进精确 uniform/alias 属性以消除约百万次 generic prune/read 的来源、history delta 贯通 adapter，以及独立真实写路径。
同主干 M profile 的预冻结容差、配对 harness 和最终完整出口继续由 52 的 P1/P6 约束，不因为本切片收益而延期豁免。
