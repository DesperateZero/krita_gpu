# BR1 收敛目标与改动清点

这是一份可领取、可验收的改动清单，落实 [CONVERGENCE](CONVERGENCE.md)；当前裁决仍由 [92 §16](../92_br1_m6_m8_execution_baseline.md#br1-convergence)维护。§2 保留 JP1 的冻结规模；生产改动清点见 §8–§9 和 [§11](#fresh-read-delivery)，联合目标及剩余修复见 [§10](#current-read-work-order)，API 函数级映射见 [§12](#api-convergence-work)，读取选择见 [§13](#read-selection-delivery)，交付协议与共同安装见 [§14](#adapter-delivery)。冻结结果不是对未来源码的自动认可。BC/JP/HX 沿用原编号，不新增阶段。

**当前目标与顺序统一查 [92 §17 完整排期](../92_br1_m6_m8_execution_baseline.md#br1-closure-schedule)，当前事实查 [§16.28](../92_br1_m6_m8_execution_baseline.md#m6-m8-completion-matrix)，本清单按 [§21 CP0–CP10](#closure-package-checklist)领取/结算。** 首条direct、联合fixture和已关闭的控制存储不重领；完整控制存储CP1已按§16.108关闭，当前推进CP3/M6正式冻结，随后执行M7和M8全出口。`tool/strokes`保持最窄适配，不预埋typed pressure API，不按注册backend数静态分额。工时不在本篇另建一份。

| 顺序 | 交付物 | 当前动作 | 退出后去向 |
|---|---|---|---|
| CP0/CP1 | required/对照与完整控制存储 | 一次清点实际owner、收费、硬界、失败和退出；不继续拆通知变体 | CP2/CP3完成M6 |
| CP2–CP4 | M6安全/预算/资格 → M7真实生产协议 | 保留Fresh，补实际consumer、共同epoch gate及首字节后不可失败证明 | M6/M7分别冻结 |
| CP5–CP7 | 多文档压力/公平/原job接续、读发布族与全stroke模式 | 每模式联合写/读/显示/失败/undo/drain，原caller迁走即合并/删除 | stroke核心出口；未完成族不隐藏 |
| CP8 | undo → context | delta穿透适配；准备缓存有界、依赖准确，不污染旧stroke | CP9完整M8 |
| CP9/CP10 | API/配置/完整业务 → 正式性能 | 当前同源完整资格、删除证明、各独立性能门和默认策略 | BR1总出口；不以测试数或计划文档代替 |

<a id="targets"></a>
## 1. 明确的目标与完成定义

当前管理协议清理按[92 §16.154](../92_br1_m6_m8_execution_baseline.md#cpu-management-cleanup-blueprint)、[03f代码索引](03f_cpu_management_cleanup_index.md)及[03g完成合同](03g_cpu_management_cleanup_tracker.md#completion-contract)核销22子项/10条路径；不在本页复制实施状态。全部hunk绑定固定MP/R，差集/consumer/删除、安全与数量证据齐全才关单项；有证据保留和撤回仍须列理想设计差额，不能当全包已实现。净收益、默认晋升与M6独立结算。

**当前完整交付目标：在已有direct闭环上，依次关闭M6、M7、M8与BR1-PERF；所有实际owner、存储、模式迁移及临时API都有完成条件。** 下表保留各类结果的验收定义；其中首条direct已有冻结证据，不再要求从零接线。指定入口默认启用仍受完整资源与收益门约束。

| 目标 | 必须交付的结果 | 关闭该目标的证据 | 不能充当完成证明 |
|---|---|---|---|
| 发布一致 | 同一观察窗口/read selection 内，page、extent/default、fresh current 与 adapter 一致；旧固定读稳定 | 冷缺页/暖缓存窗口由失败复现改为精确断言；并发 reader、准备拒绝和 cancel 交错通过 | JP1 局部安装零分配、仅在 root commit 加锁 |
| 真实链成立 | 原 transaction owner 到达实际 brush jobs；正常显示 cut、finish/cancel、最终 drain 闭合 | 同一真实 FreehandStrokeStrategy case 联合验证 owner、accepted input、像素、显示、undo/取消和清理；见 §4 | painter、scheduler、session 三组独立 fixture 的通过相加 |
| 指定入口可默认启用 | 完整必要资源收费、压力接续、长笔窗口、无新输入 drain；相同工作量不回退 | BC9/S08–S10、双 hash 适用配置及 92 §14 的实际回归/性能证据；正式阶段依赖照旧 | 有限测试场景内可跑、只测正常预算、只报告平均耗时 |
| 复杂度收敛 | 每个状态、包装、参数族有唯一责任和实际消费者；重复分支合并，旧路径保留理由可核查 | §5 的接口逐项审查，§6 的删除前提逐项给出 caller/trace；行为证据保持 | 净删若干行、压缩类型名、删掉失败或兼容分支 |
| BR1 完整结果统一 | M6 → M7 → M8、stroke → undo → context 与 39 的正式要求全部兑现 | 92 更新对应阶段裁决和同源证据；本清单不另发资格 | 首条 direct 入口、文档清点或测试总数 |

首条入口固定为单目标设备、direct、普通 default brush/composite、无 wrap/LoD/indirect/mask，且不依赖可变目标 source。资格由实际 strategy/painter/target/输入分支决定；设置或输入不满足时，在首字节前选择旧模式。写到一半不能切换实现或重放 dab。保留真实异步 producer 和区域并行，不用同步手写像素循环代替业务链。

首个验收配置进一步固定为 **RGBA8、COMPOSITE_OVER、普通 autobrush 异步 dab 分支、单 painter、无选区/镜像/texture/scatter/1px sharpness/interstroke**。使用非空的确定输入 trace 和正常显示节奏；opaque 与半透明分别取证。预设内容/hash、实际 direct 模式、target 和所有资格分支都要记录，不能只指定一个 `.kpp` 文件名。其余模式在入口初始化时走既有实现，后续覆盖要求保留。

**本轮实现退出点：** 发布观察点闭合、上述真实入口通过整链回归、接口责任清点完成，即冻结这个交付。资源/性能尚未完成时结论为“开发入口通过，默认启用仍开放”；不能转成一批无限延伸的微优化。完整 BR1 范围仍保留。

<a id="inventory"></a>
## 2. 已有改动的清点口径

产品 HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`，工作树差异 `c1c6f145e69d6e841fb15c5873ea23db49da681f31ddc66f33b6530fd1ae3c2d`；固定 upstream `9a24ae0d8c070884fb013594191002e1a1b39a19`。这是实施 JP3 前重新核对的冻结基线；后续源码变化不能沿用其二进制资格。详细方法见 [原清点证据](../evidence/br1_convergence_inventory_20260928/README.md)。

| 类别 | 文件数 | 增加 / 删除 / 净增行 | 如何使用 |
|---|---:|---:|---|
| 生产 C/C++ | 90 | 9,954 / 2,145 / 7,809 | 审查新增责任、调用层次、热路径与寿命 |
| 测试文件（含测试注册） | 25 | 11,153 / 152 / 11,001 | 按反例与覆盖分类，不能把行数当质量 |
| 构建/检查脚本等其他文件 | 3 | 22 / 3 / 19 | 保证实际目标启用、规则随真实实现更新 |
| 生成审计/manifest 配套文件 | 6 | 105,750 / 41,326 / 64,424 | 与生产复杂度分列；禁止手改生成结论换通过 |

合计 **124 个文件，含 6 个未跟踪源码文件**。JP3 实施后的[原完整清点](../evidence/br1_s05_commit_preparation_20260928/inventory-final.md)保留同一范围，生产净增更新为 7,833 行、测试净增为 11,086 行；JP3 相对 JP1 只净增 24 行生产、85 行测试，见 §8。JP4 [文件清点](../evidence/br1_s05_overlay_extent_20260928/inventory-final.md)的生产/测试净增分别为 7,929 / 11,298 行；本批相对 JP3 为生产 +96、测试 +212 行，见 §9。最新 JP5 规模与本批增量见 [§11](#fresh-read-delivery)。这是相对当前 HEAD 的未提交增量，不是整个 BR1 相对 upstream 的规模。构建目录、图片和其他测试输出不计入。逐文件路径、增删量、责任分组和 hash 见 [文件级清点](../evidence/br1_convergence_inventory_20260928/inventory.md)及 [JSON](../evidence/br1_convergence_inventory_20260928/inventory.json)；分组是审查路由，不表示所有 diff hunk 已完成逐行审计。

主干已经有整笔 transaction/memento、共享 tile 首写 COW、后续复用和异步 batching。本清点将“新增 PageStore 保证”“恢复原有效率”“减少原有工作量”分别判断；对照收益必须实际测量。

<a id="work-orders"></a>
## 3. 可直接领取的实现范围

本节保留早期收敛工作单的责任范围；当前领取顺序使用 [§21](#closure-package-checklist)和 [NEXT_EDITS](NEXT_EDITS.md#closure-next-work)。已完成窗口/入口不从这里重复领取，未完成族进入对应CP的差集。

一次领取一个有明确结束条件的范围。下面是依赖关系，不要求在第一次真实验证前先完成全部细化。

| 领取范围 / 原 ID | 具体改动入口与联动 | 本批结束条件 | 保留到后续的责任 |
|---|---|---|---|
| **下一实现主线：联合 bounds/caller**；JP6，联动原 JP2/JP3/JP5/JP7 | `getTile/getReadOnlyTileLazy` → backend 原 current 选择 → Tile/cache；`extent` 的真实 caller 与 packed/cursor adapter；具体函数及逐项处置见 §10/§12，六处读取选择已按 §13 合并 | §4 的发布断言成立，含写返回后另一线程 fresh read；原 owner 保留准备、安装、取消责任；锁序涵盖 manager/publication/session/tile barrier；JP4 页/extent 控制不退化 | 其他入口、完整短 gate/维护性能逐项留存；不得只修 fresh raw 就宣布 JP5/JP6 全部完成 |
| **可同时准备：真实测试与基线**；V01/BC10 | [FreehandStrokeTester](/Users/apple/krita_gpu/krita/libs/ui/tests/freehand_stroke_test.cpp:25)、[StrokeTester](/Users/apple/krita_gpu/krita/sdk/tests/stroke_testing_utils.cpp:158)、UI tests 注册及原 diagnostics | 旧模式实际 trace/像素/终结可复现；待启用模式有明确断言，未接入时不得假通过；固定同 Qt/toolchain 的 upstream 对照构建和 workload 条件 | 性能样本不足记 Inconclusive；现有 benchmark 不冒充正常显示 workload |
| **当前联合接线：原 owner 到业务链**；BC1–BC7/BC10 | [strategy 原事务](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:312) → [addDabJobs](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:169) → painter → 原 history session；[tryDoUpdate/dirty](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/freehand_stroke.cpp:228) → cut → finish/cancel | 原 owner、display checkpoint、finish/cancel、多 update、策略 undo/redo、递归 drain 和四类失败唯一终点已在同一 direct persistent fixture 成立；BC9 首个资源子范围未扩大该链 | 默认启用、复杂模式覆盖、结构化压力 continuation 与完整资源/性能资格 |
| **贯穿当前修复与接线：API 收敛**；S01/S03/S04/S05/BC | [函数映射](API_CONVERGENCE_MAP.md)：selector 副本 → 共同 adapter/交付 → owner/结果分支；§5 保留责任概览 | 每项给出迁移 caller 和已删签名/body；结构与行为检查同时通过 | 仅外部包装/未迁移模式依赖的删除后置，见映射的条件删除账本 |
| **默认启用门：资源与增量对照**；BC9/JP8/HX8/HX9/S08–S10 | 原 budget/ledger、admission、退休/通知、pending 工作窗口、ON/OFF 产品构建及主干对照 | live+reserved/实际峰值对账；压力拒绝与写后失败分开；无新输入可 drain；92 §14 的结构消除和 2% 不劣性条件有充分证据 | M6/M7/M8 其他范围及 39 正式资格分别裁决 |

新发现只有附上“违反条款或复现 → 真实 caller → 阻塞上述哪一出口 → 有限验收”才进入当前批。仅能解释潜在收益的分配、缓存、容器细化列入后续，不自动变成新前置。

<a id="acceptance"></a>
## 4. 验收清点：需要看到什么

以下是交付必须满足的断言；已运行范围以 92 和各批冻结证据为准。本次 §10 的反例运行只固定当前失败，未替修复或真实链打勾。

| 检查面 | 必需正例 / 反例 | 精确判据与证据落点 |
|---|---|---|
| 发布观察 | 冷缺页、暖旧缓存、边缘 extent/default、新 current、旧 captured view、慢 raw reader | 相同 selection/window 内各入口一致；跨独立调用遇到真实发布允许版本变化。[新反例](../evidence/br1_current_read_convergence_20260928/current-read-probe.cpp)已覆盖旧 raw 未归还时，写返回后另一线程新读；其 `--require-converged` 当前失败。修复后转为精确断言，按 [02a §10](02a_joint_publication_boundaries.md#current-read-contract)保留 pending/intent 对照并补失败和交错 |
| 模式与 owner | 进入指定 direct 分支；不满足资格的输入/目标作为控制 | 运行时记录目标 manager、原事务/session 身份、job 借用区间；整笔一个逻辑 owner，job 不成为提交 owner；若仍走 `nullptr` 或旧模式，目标模式 case 明确失败。`testOneStroke` 的 `indirectPainting` 参数只影响命名，不能作为模式证据 |
| 重复写与并行 | 同页 1/10/1000 dab，K=1/16；跨 worker、同页重叠及独立页 | 首次准备与真实 freeze 后重写分别计数；无新 freeze 的重写不新增 per-dab COW/allocate/seal。并发证据证明独立页仍可同时执行，不能靠全局串行通过 |
| 像素与读意图 | current、G0、operation-start、exact；透明/半透明与未迁移 source 控制 | 精确检查对应版本/字节和取消结果；[原 fixture](/Users/apple/krita_gpu/krita/libs/ui/tests/freehand_stroke_test.cpp:25) 的 `setBaseFuzziness(3)` 只支持其图像比较范围，不能替代一致性断言或掩盖隐藏 RGB 变化；预期 kernel 修正单独说明 |
| 显示与 cut | 正常更新，递归异步 producer，cut 后继续输入，屏幕外已修改页，dirty/准备拒绝 | cut 前已接纳输入及必要后继完成；checkpoint 包含完整 write set；拒绝保留 dirty/continuation；borrow 归还后才切，不同步等待自身 |
| 结束与撤销 | finish、第一页写后失败、准备拒绝、显式/重复 cancel、晚 guard、析构 | 成功恰好交付该 stroke 的 undo；失败不误交付、不 replay；取消恢复原结果，原 owner 保留到真正终结，最后释放 guard/charge |
| 资源与维护 | tiny budget、长笔、慢 reader、多文档、取消/close，无后续输入 | 候选和旧/新结构共存峰值收费；无丢唤醒、忙转或永久 debt；front-end/后台成本分列，QSBR/容器等待不被局部零分配掩盖 |
| 对照与成本 | upstream、JP1 检查点、新候选；同依赖/输入/显示/线程条件 | 首 dab、steady、input-to-visible P95/P99、pen-up、完全 drain、峰值字节各自报告；92 §14 要求的样本/不确定性/2% 容差和 39 门限不变 |

真实 freehand 先完成精确语义和执行路径断言，再记录分段性能。现有 smoke 仅证明入口可运行；现有 benchmark helper 关闭普通更新，实际 direct/indirect 由 preset 决定；两者都不能顶替本表。未实现 case 名、未构建 target 和未测量数据不得写成通过。

<a id="change-disposition"></a>
## 5. 收敛改动清点：保留、修复与合并

| 原修改项 / 对象 | 本次核对的已有能力或缺口 | 处置与明确改动目标 | 完成/保留依据 |
|---|---|---|---|
| S01：事务结果与 job 失败 | `tryEnd/tryRevert`、job 失败桥已有 caller；direct 与 indirect 终结责任不同 | 保留结果链，补第一条链的失败到 cancel；业务调用优先消费结果。不要把所有 void API 一次性改签名 | 当前路径已有生产消费者；迁移后成功才交付 undo，失败保留 owner |
| S02：session/storage/borrow | 原 memento 可持有 session，稳定 slot、execution borrow、checkpoint 已有受测能力 | 保留唯一 write set 与 slot 身份；接原业务 owner/job。没有新复现时暂停再造存储层 | 同一 owner 跨 job，borrow 仅控制执行寿命；freeze/finish/cancel 统一 |
| S03：真实写入与映射 | multi-dab/cursor、稀疏范围、映射后页分区、fixed-source 已接线；显式 direct 开发入口、BC10 联合正确性和 BC9 首个资源 fixture 已完成，正式工具默认未启用 | 保留已做的实际工作量削减；先做 PageStore 内资源/公平收敛。continuation 只有在原 job/data 可一次性转交且同批替换旧错误分支时才领取 | 同输入像素、页依赖和旧模式控制；不能把主干已有 batching 计成新增收益 |
| S04：读选择/显示 | 四类读意图和 scheduler cut 有能力，真实 producer/dirty/cut 未联合 | 在同一业务链显式选择；projection/save 使用 immutable checkpoint，current 在合法 borrow 下读 pending | 本表 §4 的读与显示断言；不能用每 dab seal 修补语义 |
| S05：publication | JP1 安装准备成立；本批匿名 root 成功后的 cleanup 已移出 publication gate（§8）；锁外准备因进度回退撤回；JP4 canonical 页/extent 已联合安装（§9），JP5 fresh raw 已推进到 §11，manager extent/caller 及其他入口仍开放 | 优先修窗口，复用原候选/owner；再完成必要锁外准备与短安装。用同一个联合交付协议覆盖直接调用到的终结 | 冷暖窗口及失败/锁序证据；一致性和短 gate 性能分别关闭 |
| S06/S07：计划与 ledger | recoverable CPU、原 selector/claims、domain 对账已有实现；完整 M6/M7 未闭合 | 保留唯一计划与 Fresh 控制，按正式出口补证据；不为首条普通 brush 加第二条 commit-only 通道 | M6/M7 各自资格；普通 brush 保持既定失败保证 |
| S08/S09/S10：回收、通知、预算 | 局部扫描/等待/授额/通知已受测，完整工作窗口和资源仍开放 | 保留现有 owner；补实际收费、跨 store 进度和关闭。generic/readiness/completion 不合并成一个含糊错误标志 | 必要存储与释放的真实账本、慢 reader/多文档/无新输入证据 |
| U01/U02：history/extent | 普通 restore 仍调用 `rebuildPageStoreIndex`，extent 容量前移不等于 delta 恢复完成 | 首条链正确取消/undo 必须现在保持；全量 delta 优化在 stroke 后执行。普通恢复改成 changed keys 后才删对应全量调用 | 固定 K 放大 N/H 不增加全量重建；其他构造/恢复 caller 另行保留 |
| C01/C02：上下文 | WriteContext 已复验 target/offset/wrap 等值；它不是写权限 | 保留映射复验，联合 job 寿命；preset/context 优化后续按原范围，不侵入本批扩大缓存 | 错目标拒绝和执行期间稳定；原 budget/owner 不被值快照替代 |
| HX：并发容器 | prepared key、迁移/GC/关闭有实际消费者；自旋、静止关闭和整批回收存在边界 | 保留已测存储能力及寿命；补适用双配置/进度证据。没有新反例不重写 map | 新增等待与上游已有 QSBR 限制分开；局部无分配不代表 wait-free |
| V01：测试/诊断/生成证据 | 大量局部反例，缺同一真实链与同依赖主干性能 | 复用独立反例，补整链和因果指标；维护源码/运行库身份，生成审计与生产代码分列 | 实际运行命令和原始结果；计数不相加制造新资格 |

优先审查下面四组**具体接口**，目标是减少重复责任，是否新建内部类型须由实际调用链证明：

| 接口/状态族 | 代码定位与当前职责 | 允许的收敛方向 | 不能丢的边界 |
|---|---|---|---|
| painter 的可选 `strokeOwner` 参数族 | [bitBlt](/Users/apple/krita_gpu/krita/libs/image/kis_painter.h:182)、[bltFixed 各 overload](/Users/apple/krita_gpu/krita/libs/image/kis_painter.h:297)、mirror 与 PaintDevice；同步借用已由一个 painter 绑定统一 | public 显式 owner overload 已删除，测试迁移到与生产相同的绑定入口；owner 参数只保留在 private impl，不再为同步/隔离测试暴露第二套接口 | owner 不是 painter 的私有事务；异步 job 必须由原 strategy 保活，source 与 target 不能混用；若既有 execution context 可承载，迁移后删除唯一 setter |
| backend 交付参数 | [runCpuMutationOperation](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h:258) 的 `historyOwner/delivery/prepareAdapter` | 已按 [API 映射 §11](API_CONVERGENCE_MAP.md#adapter-delivery)替代两种独立输出并删除旧签名；继续闭合 JP6 联合可见性，不新增 owner | standalone batch 与 borrowed execution 寿命不同；安装后才归还的原能力不可提前析构，不新增第二份事务 |
| native packed/cursor 的 adapter 交付 | [PreparedTileUpdates](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:57)、[writeBytes](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1555)、[writePageStoreOperation](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1734) | 共同安装与能力交付已收束，并删除这两条纯写路径的 presence 二次查询；联合 bounds 验收仍开放 | packed layout/legacy 借用与 cursor job 语义不能硬合并；不得通过持 manager/publication gate 执行整段 kernel 消除重复 |
| job 错误 TLS 桥 | [KisStrokeJobFailureContext](/Users/apple/krita_gpu/krita/libs/image/KisStrokeJobFailureContext.h:8)、[SimpleStrokeJobStrategy::run](/Users/apple/krita_gpu/krita/libs/image/kis_simple_stroke_strategy.cpp:25) | 保留 legacy void 的短栈错误收集，入口和消费点清晰；能返回结果的新内层调用使用显式结果，不继续扩大隐式错误通道 | 该 TLS 不拥有事务/像素，也不能代替跨 job 状态；仍有 painter/manager/brush 生产 caller，当前不删除 |

`KisPageReadiness`（等待与唤醒）、`KisStrokeJobFailureContext`（单 callback 错误）和 `WriteContext`（目标映射值）寿命与职责不同；即使都参与失败处理，也不以“状态统一”为理由合并。

<a id="deletions"></a>
## 6. 删除与暂缓清单

**JP4 已删除 backend 事后 `stageDerivedExtent` 及其两处调用，证据见 §9。** 以下其余项目仍是条件删除候选，实施前必须补静态 caller、callback/override 和实际 runtime census；不能把“目标代码更短”当删除授权依据。

| 候选 | 当前仍需保留的原因 | 何时可以删除/收缩 |
|---|---|---|
| 普通 undo/redo 的全量 index rebuild 调用 | [restoreHistory](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:465)仍实际调用；构造/其他 barrier 也可能使用同 helper | U01/U02 的 changed delta 贯穿适配且固定 K 证据成立后，删除普通恢复中的调用；不能直接删除整个 helper |
| legacy/Unavailable/Borrowed 分支、无 owner painter 包装 | 未迁移模式、standalone 与旧 raw/source 语义仍消费 | 对具体入口证明迁移完成或 fallback 仍由更上层首字节前选择；保留 ABI 的包装可变薄，不贸然删除 |
| 临时模式开关/重复结果转换 | 首条开发入口需要明确隔离；当前尚未形成新开关，不预造长期双协议 | 对应入口稳定且资格闭合后移除只服务实验的切换与重复转接；保留必要算法选择与 Fresh fallback |
| 旧注册/通知/adapter 协议 | 仅凭新接口存在无法证明消费者为零 | 静态及运行时消费者均已迁移，唯一 owner/终结仍成立，取消/关闭/插件边界回归通过后再删 |
| 重复 probe/helper/滚动状态文案 | 相同名称可能覆盖不同失败点；旧日志本身是冻结证据 | 相同契约、入口、故障和配置确实重复时合并测试 helper；旧失败记录保留。导航的动态状态已统一到 92，后续不再复制 |

暂缓新增通用容器框架、仅为零分配数量增加的探针、新缓存层、preset/context 微优化及非首条入口的同步旁路改造；若出现本批契约反例，再按领取规则提升。**不暂缓**首条入口的错误终结、真实显示、必要资源安全，也不降低默认启用的完整预算/进度要求。

<a id="closure"></a>
## 7. 一次收敛改动如何交付

每批只提交一个可核验结果，使用以下清点单；“暂未测量”不能填“无回退”。

```text
领取目标与原 BC/JP/S/U/C/V ID：
当前源码/依赖身份；与本清点是否一致：
精确观察问题、主改符号与联动 caller：
保留 / 修复接通 / 合并 / 条件删除 / 暂缓，各有哪些：
每个新增状态的 owner、实际消费者、成功/拒绝/取消/析构终点：
已关闭反例；新增整链断言；原始运行结果与失败记录：
实际输入、显示、drain 和因果成本；与哪组基线比较：
未完成项阻塞的是开发入口、默认启用还是正式阶段：
停止条件是否满足；回写 92 的结论和证据链接：
```

新增代码未改变可观察行为、消除已证明重复责任或提供必需验收证据时，先说明为何需要；不能仅以“让下一层更容易实现”不断增加层级。达到本批结果后结束，后续条目重新按真实阻塞领取。

<a id="jp3-delivery"></a>
## 8. 本批收敛改动清点：成功提交后的清理

本批关闭 JP3 的一个有限问题：匿名 root 已成功安装后，backend reader 仍被不需要持 publication 锁的清理工作阻塞。**最终只提前释放成功提交的 publication 锁**，保留原准备、读选择切换、重试和失败语义。锁外准备候选经压力回归发现进度退化，已经撤回。当前结果由 [92 §16.5](../92_br1_m6_m8_execution_baseline.md#jp3-commit-preparation)裁决，代码增量、源码身份及所有失败样本见 [本批记录](../evidence/br1_s05_commit_preparation_20260928/README.md)。

| 处置 | 对象 | 本批最终结果 / 保留理由 |
|---|---|---|
| 修复 | backend `finishOwnedTransaction` → Store 私有 `commitAndReleasePublicationLock` → 原 `commitLocked` | 原 selector 在持锁时按旧路径隐藏；root/metadata 成功安装并释放 Store owner 锁后，立即解开 backend publication 锁，再清理。reader 可以在成功 cleanup 期间捕获 committed root |
| 保留 | 原候选、事务、prepared delta、transaction mutex、准备及失败语义 | 安装前失败或重准备仍持原 publication 锁；最终 writer 仍由原 mutex 串行。没有新增长期状态、selector 回调、第二份 session 或 writer 表 |
| 验证 | manager 原测试和独立旧二进制复现 | BPP 1/4/8/16 × packed/cursor × cold/warm；cleanup 阶段另线程 reader 必须完成，读取新字节和正确 extent；旧 captured view 保持原字节；最终无活跃事务 |
| 撤回 | 固定三次重试，以及配套重复 prepare 规则 | 原独立页/产品并发写会被错误拒绝。固定次数不能代替原 owner 接续，不能提高次数或放宽测试换通过 |
| 撤回 | root 全部准备移到 publication 锁外、late-selector 回调与额外取锁复验 | 连续 reader 下产品写进度超过原 10 秒上界，隔离复查触发 45 秒超时。读保护 revision 与候选重准备的进度尚未闭合；删除这批新增生产状态组合，保留失败证据 |
| 保持开放 | 完整短 gate、page/surface/adapter 联合观察、其他终结入口 | 成功 cleanup 解锁不证明准备有界、gate 零分配/释放、history/checkpoint/abort/restore 或 M8。锁外准备候选还出现一次区间内 free，不移植其局部零值资格 |

本批停止条件：原成功 cleanup 阻塞被确定性断言关闭，既有并发提交、失败和旧读回归保持，冻结最终代码与证据；不再继续向本批叠加 root 准备优化。

**下一实现主线**仍是 JP2/JP4/JP5/JP6：固定同一 read selection / 观察窗口，关闭 page、extent/default、fresh current 与 adapter 不一致。联动的 root 准备如需外移，必须先证明持续 reader 下候选能取得提交进度，保留原并发写成功及原时限断言，并说明拒绝后的原 owner 接续；不能把无限重准备或普通竞争变成写入失败。V01/BC10 可准备真实 freehand harness；开发入口、默认启用、正式 M8 的门继续分开。

质量判断：最终产品增量集中于一个私有交付边界，删除了本轮未通过进度检验的复杂候选，复用原生命周期。它关闭一个实际阻塞点；整链收益、默认持久 owner、资源和主干性能尚未证明，不能据此给整体代码质量打“已收敛”的结论。

<a id="jp4-delivery"></a>
## 9. 本批收敛改动清点：页与派生 extent 同步发布

**本批目标：** 关闭冷页 seal 后“新 canonical 像素 / 旧 canonical extent”，覆盖原 native seal、generic publish 和条件删除；保留旧固定读与之前 sealed 笔迹。下一整体目标仍是 §1 的真实 direct stroke，不把这一子结果当作整链完成。当前裁决见 [92 §16.6](../92_br1_m6_m8_execution_baseline.md#jp4-overlay-extent)，实现、锁边界及成本范围见 [02a §9](02a_joint_publication_boundaries.md#overlay-extent-implementation)。

| 处置 | 具体改动 | 收敛效果与边界 |
|---|---|---|
| 合并 | 原 `KisPreparedOverlayUpdate` 承接派生 surface change；`sealImpl/finishWrite/stagePageRemovalLocked` 统一消费 | 页与 extent 由同一个候选、同一 owner 临界区安装；不再出现两个独立可见步骤 |
| 删除 | backend `stageDerivedExtent` 定义、声明及匿名/history commit 调用 | 删除已被原候选覆盖的事后派生与提交依赖；其余 default metadata、commit、restore 路径仍保留 |
| 删除 | `contentExtentAfterDelta` 为查询创建并销毁临时 persistent tree | 仅准备排序删除 key，沿原树路径复用未变子树边界，再合入新增页；消除无查询以外消费者的候选树 |
| 保留 | 原 prepared delta、page claim、admission、transaction base、snapshot、selector 与 adapter 交付 | 没有第二套可查询 extent/页表或 writer authority；普通 PageStore 不启用 Tiles3 派生策略 |
| 修复 | surface 修订号、容量拒绝、坐标范围与并发 sibling | extent A→B→A 仍保留新 identity；实际容量不足在安装前拒绝；新增只看本 segment，删除包含原 overlay；最后一次取得 owner 后再推导，避免覆盖 sibling |
| 验证 | 原冷/暖窗口、BPP×packed/cursor、history checkpoint、generic/条件删除、删除后重写、独立 sibling、范围/分配拒绝 | 检查页和 extent 的同一固定选择，旧 view 稳定、失败不改变已发布状态、正常重试和最终释放；不靠放宽像素断言通过 |
| 保持开放 | manager `getTile/extent`、warm raw cache、外层 gate、全部实际预算及真实 brush | 本批只关闭 canonical 页/extent。manager 和 fresh current 的滞后仍有复现，不能默认启用持久 owner 或宣称 M8 |

新增状态只有初始化时固定的 derived surface policy，以及原单次候选的 surface change/index/prepared 标志。前者随 Store 生命周期结束；后者随原成功清理或取消销毁，不进入第二个注册表。surface vector 的准备仍在 owner 锁内，删除仍可能处理累计 overlay；完整短 gate、首字节前收费和全链性能继续审查。

**下一批明确出口：** 在同一原 read selection 下，冷缺页的 fresh `getTile` 不再落回 default，暖 current 不再读旧 cache，manager extent 与该选择一致；保留正在使用的旧 raw/captured 读。先明确 retained TileSP、嵌套读、fresh current 各自契约，再联动 JP5/JP6 的准备与交付，禁止以 publication write 锁内等待 tile barrier 消除窗口。原窗口探针分别变为精确断言后，进入首条真实 direct stroke 的 owner/display/finish/cancel/drain 联合验收；期间不再重开无反例的容器微优化。

本批相对 JP3 生产净增 96 行、测试净增 212 行；最终 20 目标 × 两架构 9,238 passed / 0 failed / 0 skipped，14 个针对性探针通过。实际文件增删、同源验证和失败记录统一在 [证据与文件清点](../evidence/br1_s05_overlay_extent_20260928/README.md)。新增代码是否值得保留以关闭的观察缺口和删除的重复责任判断；目前具备局部正确性收敛，尚无主干同依赖性能收益或整体质量完成结论。

<a id="current-read-work-order"></a>
## 10. 下一批清点：关闭新读取窗口，保留原读取寿命

**§16.7 的反例审查之后，fresh raw 修复已交付到 §11；本节联合目标仍未全部完成。** [改动前证据](../evidence/br1_current_read_convergence_20260928/README.md)在 JP4 同源二进制上确认：暖页旧 reader 未释放时，写调用已返回，另一线程的两种 fresh getter 仍读旧值；不能只在 adapter 安装时 invalidate 就判定完成。另一方面，history pending 和纯写意图的兼容 extent 先于 canonical 扩大是既有行为，必须按调用目的区分。新裁决统一见 [92 §16.8](../92_br1_m6_m8_execution_baseline.md#fresh-read-implementation)。

下表是同一 JP5/JP6 交付的工作清点，不是六个新版本或六个可单独授予资格的阶段。详细读契约、caller 和锁序见 [02a §10](02a_joint_publication_boundaries.md#current-read-contract)。

| 要改/要保留 | 具体端点与处置 | 必须看到的完成结果 |
|---|---|---|
| 修复 fresh 选择 | [getTile/getReadOnlyTileLazy](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:285)共用 backend 原 current 选择；hash miss 不直接代表 canonical default，物理 cache 可 pin 不代表逻辑版本当前 | seal/operation cleanup 与写返回后的两个 getter 都读对应发布值；`existingTile` 不得误导 copy 把已发布页当稀疏 default 跳过 |
| 保留旧能力、隔离新读 | [Tile::lockForRead/refreshPageStoreData](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:349)及原 read lease；新选择与已 pin 的旧版本不同时，不能复用同一锁计数来冒充新能力 | 旧 raw 指针和 captured/G0 不变；另一线程新读取到新值；新读不等待旧 reader 生命周期结束。保留原 TileSP 的嵌套读含义，不能把所有 `lockForRead` 都改成 chase current |
| 明确 extent 消费者 | [extent](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1525)、PaintDevice strategy/frame bounds、clone/LoD/purge；联动 packed/cursor adapter 和 checkpoint | 普通已发布路径的页/extent 同选；exact 消费者使用其固定 surface state；pending/intent 工作范围保留必要语义。单改 `extent()` 返回 canonical，或把所有不一致改称“兼容行为”，均不算关闭 |
| 统一拒绝与 caller 责任 | manager raw getter → [KisTileDataWrapper](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_wrapper.h:41)、[base iterator](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_base_iterator.h:53)、copy fallback 的 source/destination | 选择或 pin 失败不返回陈旧数据冒充成功；如 getter 可返回空，所有解引用 caller 同批处理。失败保持原取消责任，不 replay、不交付成功 undo |
| 约束新增成本与状态 | [Tiles3TileReadCache](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:144)、原 binding/selector、两种 hash | 命中时复用原缓存；不为每次 fresh getter 无条件 capture/freeze、走 generic 或分配 wrapper；失配/旧 pin 并存的冷代价单独报告。新元数据只能是原身份派生的提示，不增加 current/writer 注册表 |
| 联合验收后冻结 | 现有窗口探针 + manager/cache/default/history/claim/progress 回归；实际 manager/publication/session/tile barrier 锁序 | `--require-converged` 由当前非零退出转为精确通过，旧读、default、pending/intent 控制保持，准备失败与并发进度有证据；按新源码重新构建、跑必要矩阵和架构检查，未覆盖模式明确留存 |

**保留清单：** JP4 原候选的 page+surface 安装；JP3 成功 cleanup 解锁；原 claims/admission；`getOldTile`/detached Tile 的固定语义；稀疏 default 不建 canonical 页；write intent 不提前物化；live legacy 写/嵌套读写仍有消费者。以上不能作为“统一 current”时顺手删除的分支。

**合并/删除清单：** 两种 fresh getter 的选择规则应只维护一次；如果建立了有明确能力的 current 入口，迁移其调用者后再删等价的重复刷新分支。此时没有依据删除整个 `refreshPageStoreData`、read lease、hash、memento 或失败桥。packed/cursor 共同交付按 §12 在联合修复中合并，owner 的等价分支随接线收束；仅依赖模式迁移的外部包装删除后置。

**停止条件：** 上表联合结果成立即冻结本批，下一批执行 BC1–BC7/BC10 的真实 direct stroke。若只关闭 raw 而 extent/caller/失败责任仍缺，最多记 JP5 子范围；不能宣布读窗口整体完成。准备外移、完整预算、M6/M7/M8 和全部模式仍在原门中，不因本清单缩小而删除，也不无条件扩成当前修复前置。

**§16.7 检查点的质量密度复核：** 与固定 upstream 对照，manager 当时 1,871 行对 782 行，Tile 实现 644 行对 334 行，backend 新增 2,442 行；这些是文件物理行数，不是本轮净增或缺陷率。新增层需要用完整可观察保证和业务收益支撑。当前结论为“局部能力较充分，产品接线与复杂度收益待兑现”；该审查产品净增为 0，只新增反例 harness 和收敛约束；随后实现增量见 §11。后续按“关闭哪个反例、消除哪个重复责任、保留哪个生产消费者”评价每一项改动，不追求版本数或测试总数。

<a id="fresh-read-delivery"></a>
## 11. JP5 改动清点：新读取已闭合，联合 extent 继续

本批相对 JP4 改动 13 个生产文件，增加 184、删除 11、净增 173 行；2 个测试文件增加 205 行，新增 47 个 case/架构。没有新增生产文件或 Tile/manager 常驻状态。[完整清点](../evidence/br1_s05_fresh_read_20260928/inventory-final.md)的 124 文件范围未变；相对 HEAD 的生产/测试净增分别为 8,102 / 11,503 行，生成审计单列。§10 的零产品增量及文件行数仅属于前一次反例审查，不能套用到本批。

| 处置 | 已交付的变化 | 剩余/保留责任 |
|---|---|---|
| 合并 | 两个 manager fresh getter 共用 backend 原 selector 与 `selectCurrentReadTile` | writable/getOld/合法 live legacy 不混成同一种读取 |
| 修复 | hash miss 不再代替 canonical absence；binding 逻辑版本比较不再被物理可 pin 替代 | 原 `existingTile` 在 live legacy 分支仍按其工作索引语义；全模式组合继续验证 |
| 隔离 | 旧 wrapper active 时，新版本用原 detached Tile/COW 存储寿命；不留 manager 裸指针 | 旧 raw/G0/捕获读稳定；这里没有解决全部 canonical idle-reference 迁移 |
| 保留/复用 | warm 原 cache、稀疏 default、native/generic 能力、原 allocator 与 failure context | default 失配的冷兼容分配会明确拒绝；warm 零分配不等于 Fresh 2% 资格 |
| 联动 | wrapper/base iterator/copy fallback 处理空 getter；关闭和预算拒绝不返回旧像素 | 完整异步/多模式失败矩阵及真实 owner 仍待整链验收 |
| 明示侵入 | Tile 与 manager header 各增加一个 backend friend；未加字段/直接 include | 按 92 §16.8 记录访问范围、锁序、内存与删除条件；不是所有侵入计数保持不变 |
| 保持开放 | manager extent、固定 bounds 的实际 caller 与 adapter 的联合结果 | 整体 probe 仍失败，不能将 JP5 raw 子范围升级成 JP5/JP6 或 M8 完成 |

同源运行、暖 getter 分配计数与整体探针的剩余失败见 [本批证据](../evidence/br1_s05_fresh_read_20260928/README.md)。下一步按 §10 处理 JP6 bounds/caller，保持 pending/intent 对照；BC10 真实 harness 不因局部修复而延期。达到联合出口后进入原 direct stroke 整链，不继续增加没有新反例的底层缓存/容器细化。

<a id="api-convergence-work"></a>
## 12. API 收敛领取与改动映射（2026-09-29）

当前按 [§15](#convergence-action-checklist)执行勾选；本节和 §13–§14 保留此前规划及冻结交付；copy 的后续验收见 [§16](#copy-bounds-delivery)，不复用候选时点的局部日志。

本节修正此前“首条链后再压缩全部接口”的安排。完整函数、caller、替代关系、锁/寿命、测试和条件删除统一维护在 [API_CONVERGENCE_MAP](API_CONVERGENCE_MAP.md)，文件反查见 [CODE_INDEX 专节](CODE_INDEX.md#api-convergence-index)。以下区分已交付与待执行；读取选择见 §13，早期共同安装/交付见 §14，packed/cursor 短 completion 的最终处置见 §17；其余发布族与真实业务仍待完成。

| 原责任 | 本次必交付的结构结果 | 行为出口 | 状态 |
|---|---|---|---|
| JP5/S04 [读取选择](API_CONVERGENCE_MAP.md#read-selection) | 六处同源选择规则归一，删除等价分支副本；五个 JP5 新函数逐项保留/迁移理由明确 | current/base/captured/live legacy、旧读、默认值、失败/进度不退化 | 已按 §13 交付，六处重复分支已删 |
| JP2/JP6 [adapter/bounds](API_CONVERGENCE_MAP.md#adapter-bounds) | packed/cursor 共同安装实现只有一份；真实 bounds caller 有迁移或保留结论 | add 的 page/bounds/adapter 窗口闭合；删除/default/pending/intent 对照保持 | add 已按 §17 通过；删除/default/copy/restore/purge 按 direct 依赖领取 |
| JP2/JP3/JP7 [交付结果](API_CONVERGENCE_MAP.md#delivery-contract) | 两种独立能力输出收束；history 不再输出，standalone holder 只保留 admission | 成功、空目标、准备拒绝、执行失败和析构责任明确 | 最终处置见 §17；`finish()` 与 history state 已删 |
| BC1–BC7/S03 [owner 接线](API_CONVERGENCE_MAP.md#painter-owner) | 复用既有私有实现，等价 owner/模式分支随接线删除 | 真实 direct jobs、正常显示、finish/cancel/drain | 先核对 direct 是否依赖剩余发布族，无依赖立即接线 |
| S01 [结果边界](API_CONVERGENCE_MAP.md#failure-boundary) | 显式结果贯穿可返回的内层，冗余转换如有则删；legacy 错误桥保留 | 原取消链与唯一 undo/终结不变 | 随触及的 caller 联动 |
| U01/U02、raw/兼容包装 [条件删除](API_CONVERGENCE_MAP.md#conditional-removal) | 各对象写清具体消费者与退出触发条件 | 对应模式/恢复语义及适用 ABI/配置证明 | 后续条件项，非当前全部前置 |

当前单元的每个新增函数必须附责任与替代对象；有替代关系时，同批迁移 caller 并删旧实现。没有净删除配额，也不能以只新增文档、wrapper 或测试数量宣称结构收敛。交付按 [映射 §9 模板](API_CONVERGENCE_MAP.md#verification)回填实际改动和证据，资格只更新 92。

<a id="read-selection-delivery"></a>
## 13. 读取选择收敛的实际改动清点

| 处置 | 本批实际结果 | 保留边界 |
|---|---|---|
| 合并/删除 | 六处 backend 同源选择分支删除，统一到原 Private 的一个受锁选择函数 | 六种入口的读取寿命与访问模式不合并；iterator 的 before 条件保留 |
| 新增 | 一个 `.cpp` 内部实现函数；生成图确认六个生产入口、七个调用点 | 无新公共签名、字段、friend、TLS、owner 或独立状态表 |
| 规模 | 生产单文件 +24/-38，净减 14 行；测试源码不变 | 另刷新两份生成 source/graph 审计数据，侵入上限和 ownership 规则不变 |
| 验证 | 七相关目标双架构 4,116 passed / 0 failed / 0 skipped；工具自测、架构及实际 no-op 通过 | 没有重跑全部旧 20 目标；原窗口与分配探针、最终身份见本批证据 |
| 剩余 | JP6 bounds/caller/adapter 和单次交付参数；随后真实 owner/显示/取消/drain | 本次结构去重没有关闭这些行为或 M6–M8 资格 |

[源码/调用者/运行证据](../evidence/br1_read_selection_convergence_20260929/README.md)与 [92 §16.10](../92_br1_m6_m8_execution_baseline.md#read-selection-convergence)统一当前结论。下一批按 [API 映射 §4–§5](API_CONVERGENCE_MAP.md#adapter-bounds)继续，不为已收束的 selector 再增加框架或重复探针。


<a id="adapter-delivery"></a>
## 14. 共同安装与交付协议的实际改动清点

| 处置 | 已改对象 / 明确保留对象 | 验收边界 |
|---|---|---|
| 合并 | 两条 manager 写入口共用 `PreparedTileUpdates::install`，原重复循环删除 | packed/cursor 像素执行仍不同，安装政策唯一 |
| 替代并删除 | backend 三个内部签名先改为一个 `OperationDelivery*`，两条生产 caller 和直接测试迁移；独立 batch/execution 输出删除 | 该冻结点的 history 显式 finish 随后在 §17 改为 worker 内归还，delivery 不再保存 execution |
| 减少工作 | 删除这两条实际写入路径的 presence buffer 准备和二次全局查询 | clear/copy/remove 不属于纯写入语义，原查询保留 |
| 新增及规模 | 该冻结点导出头增加互斥 move-only 类型及五个成员；生产三个文件 +92/-77，净增 15 行 | §17 已删其中 `finish()` 和 history 状态；本行仅保留早期冻结规模 |
| 回归 | 复用原 adapter/presence 断言，增加真实 history 移动/异线程拒绝/遗弃取消用例 | 精确矩阵和身份见本批证据，不把代码重构当成正式性能结论 |
| 后续结果 | 此冻结点的 manager bounds 窗口在 §17 关闭 packed/cursor add 子范围；真实 direct owner/显示/finish/cancel/drain 仍开放 | delete/default/copy/restore/purge 与 JP6 整体、默认启用、M6–M8 不由早期结构批完成 |

代码/调用者反查见 [API 映射 §11](API_CONVERGENCE_MAP.md#adapter-delivery)与 [CODE_INDEX](CODE_INDEX.md#api-convergence-index)，该冻结点证据见[交付协议记录](../evidence/br1_adapter_delivery_convergence_20260929/README.md)。当前最终处置和下一领取以 §17 / [92 §16.14](../92_br1_m6_m8_execution_baseline.md#joint-adapter-window-delivery)为准；已收束的函数不再重复整理。

<a id="convergence-action-checklist"></a>
## 15. 当前执行勾选与改动结算

本节结算2026-09-29的局部API行动，当前完整包清点移至 [§21](#closure-package-checklist)；旧“下一项”不覆盖92 §17。

本节的局部方案/替代关系见 [API §12](API_CONVERGENCE_MAP.md#convergence-action-map)和 [旧函数映射](CODE_INDEX.md#api-convergence-index)，联合fixture冻结资格见 [92 §16.17](../92_br1_m6_m8_execution_baseline.md#direct-stroke-joint-fixture)，原规划检查点见§16.12。当前完整领取/结算使用本篇§21，当前资格使用92 §16.28，不将此检查点的“下一项”重复执行。

- [x] JP5/S04：六处选择政策归一并删除副本，证据见 §13。
- [x] JP2/JP3/JP7 结构子项：共同安装和互斥交付，删除重复 body 与旧输出签名，证据见 §14。
- [x] JP6 copy：共同 copy 实现、显式 source/target view 与非 wrapped clone 裁剪已按 [API §13](API_CONVERGENCE_MAP.md#copy-bounds-delivery)完成同源验收；旧签名/重复分支已删，新增私有声明已审。两端 backend 关闭的 legacy 对照通过，不授予完整 OFF 构建资格。
- [x] JP6 packed/cursor add 联合窗口：原 publish 与 prepared adapter 安装共用短 manager gate；旧 history delivery/finish 删除；44 场景/172 观察在双架构三类违例为零。见 §17。
- [ ] JP6 剩余发布族：只审查 delete/default/copy/restore/purge 对首条 direct 链的实际依赖；有依赖就关闭对应窗口，无依赖就转真实链。不得把 add 的只增页安装强套删除语义。
- [ ] JP6 caller：LoD/transfer/frame copy 与 working/估算/purge 按实际用途逐项迁移或保留；复杂模式未迁移登记 BC8，不能无记录留空。
- [x] BC1–BC7 首条开发入口子范围：有限 direct 的原 owner 已到达真实 async/1px brush 写入，dirty 前 checkpoint，finish/cancel 先解绑 painter 再释放 owner；正式工具默认仍关闭。见 §18。
- [x] BC10 首条 direct 联合正确性 fixture：多 update、策略 undo/redo、递归无输入 drain，以及 admission/像素失败信号/checkpoint/finish 的结构化失败和唯一 cancel 终点均按 §18 完成。完整 BC10 性能与 BC1–BC9 覆盖仍按各自门裁决。
- [ ] BC9/V01：默认启用前完成真实资源/压力/进度与同依赖主干/OFF/Fresh 对照；正式 M6–M8 按原门单独裁决。
- [ ] BC8/U01–U02/S06：具体消费者迁移后删除对应兼容包装、raw friend/helper、普通 restore 全量调用，并降低适用侵入上限。

每次只领取足以关闭一个既定出口的修改与直接依赖。结算必须填明新增函数、迁移 caller、删除的旧符号/重复体、暂留消费者与触发条件、行为证据及源码身份；采用 [API §9 模板](API_CONVERGENCE_MAP.md#verification)。没有替代关系的独立函数保留，没有新失败证据的底层泛化不进入本批。不得把旧测试总数、候选 diff 或文档勾选充当实现验收。


<a id="copy-bounds-delivery"></a>
## 16. copy 子项交付与仍开放的联合边界

本项按 §15 第一项结算：生产五文件 +96/-64，测试三文件 +167/-6；共同 helper 替代 precise/rough 两份 native body，backend 原 copy 签名和内部二次 capture 删除，公开 bitBlt/clone 入口不增加。固定选择的 clone 反例、source/target/default/history 与 legacy 对照通过；测试的 LoD 临时结构漏释放也已修正。

20 完整目标加选定 PaintDevice 方法的双架构矩阵共 9,560 passed / 0 failed / 0 skipped，架构/工具自测及实际 no-op 通过。原整体 reader-window 每架构仍有 32 个 extent 不一致点，验收退出 3；raw 和控制错误为零。故只勾选 copy，JP6 联合窗口、真实 owner/display/finish/cancel/drain、默认启用及 M6–M8 均继续开放。

[函数替代与源码映射](API_CONVERGENCE_MAP.md#copy-bounds-delivery)、[本批冻结证据](../evidence/br1_copy_bounds_convergence_20260929/README.md)和 [92 §16.13](../92_br1_m6_m8_execution_baseline.md#copy-bounds-convergence)统一状态。下一项固定为原联合安装的锁序/拒绝回退及 caller 对齐，不重领已验收的 copy 整理。


<a id="joint-adapter-window-delivery"></a>
## 17. packed/cursor 联合完成边界与剩余收敛清点

本节结算 [API §14](API_CONVERGENCE_MAP.md#joint-adapter-window-delivery)，当前源码资格见 [92 §16.14](../92_br1_m6_m8_execution_baseline.md#joint-adapter-window-delivery)。

- [x] standalone packed/cursor：原 publish closure 在 manager `m_lock` 内执行，成功后立即消费已准备 wrapper/extent；publish 拒绝不安装 adapter。
- [x] history cursor：不输出或搬移 execution；在原 borrow 存活时安装 pending adapter，随后由 backend worker 归还 borrow。
- [x] manager bounds reader：`extent()`、`region()` 取得 read gate；`setExtent()` 已持 write gate 时直读 extent manager，避免非递归重入。
- [x] API 删除：移除 `OperationDelivery::finish()`、execution/monostate variant 与 `<variant>`；删除两个失去产品语义的 history-delivery 测试项。新增仅为既有写方法的 completion 参数与 callback 类型别名，没有新具名函数。
- [x] legacy 冲突：被拒绝的 raw/planar/intent 写不能污染原匿名 transaction；原 standalone admission 仍阻塞同页竞争直至局部 prepared storage 销毁。
- [x] 目标证据：双架构联合探针各 44 场景/172 观察，publication/raw/control 均为 0；20 目标加 PaintDevice 选择方法的冻结矩阵共 9,556/0/0；图为 1,814 APIs / 19,634 edges。
- [ ] 删除/default：确认 `clear(QRect)`、trim/remove、default revision 是否存在 canonical 与 manager adapter 可分离观察；只对能复现或 direct 链依赖的路径实现 prepare/completion。
- [ ] copy/restore/purge：copy 已固定 source/target selection，但其 target adapter 发布、restore delta 和 purge 删除语义分别审查；不能复用只增页的 `PreparedTileUpdates::install` 假装完成。
- [ ] 实际 caller：LoD/transfer/frame bounds 需要固定内容时与像素共用 view；working/估算/purge 保留原语义并记录原因。
- [ ] direct stroke：若上述未完成项不在 RGBA8/OVER/direct 正常显示和 finish/cancel 路径中，立即接 BC1–BC7/BC10，不等待全模式整理。

后续每次修改只运行能够证伪目标结果的测试：改一个发布族就跑其并发窗口、失败/取消和直接消费者；改 direct 链就跑真实 brush/display/finish/cancel/drain 与必要控制。完整矩阵只在形成新的跨模块冻结点、改 ABI/公共行为或准备默认启用时运行，不能对每个局部编辑重复执行。

<a id="direct-stroke-pilot-delivery"></a>
## 18. 首条 direct 开发入口清点与下一联合出口

- [x] 资格在首个像素 job 前一次决定：单 painter、Pixel Brush、RGBA8、OVER、无 selection/indirect/mask/wrap/LoD；不满足时整笔保留旧模式。
- [x] 原 `KisTransaction` 完成 `beginStrokeMutation`；painter 绑定是非拥有指针，不占用原自持 `d->transaction`。
- [x] `addDabJobs` 删除显式空 owner；async multi-dab、1px scalar、bitBlt 和 mirror 共用 painter 绑定，没有为各分支新增业务参数。
- [x] 有 dirty 时先 checkpoint，成功后才取 dirty 并通知 projection/display；拒绝时 dirty 未被消费。
- [x] finish/cancel 成功路径先清空/销毁 painters，再释放 transaction；取消拒绝仍保留 owner 并沿原 retry 责任接续。
- [x] `FreehandStrokeStrategy::Flags` 保持主干接口；只有测试派生 strategy 调用 protected opt-in setter，正式 `KisToolFreehandHelper` 不调用；BC9 前没有默认启用。
- [x] 目标结果：brush owner/1px/checkpoint/undo-redo 双架构各 50/0/0；真实 freehand 显示/finish/cancel 双架构各 4/0/0；架构门通过。
- [x] 同一 `FreehandStrokeTest` fixture 执行两次实际写入和两次 update；一次策略 undo 同时清除两段且命令栈回到空位置，一次 redo 精确恢复完整图像。该业务语义与原 owner 代码路径共同证明 transaction 连续性，不新增裸 owner/session/incarnation getter。
- [x] 策略层一次 undo/redo 已在 scheduler drain 后验证；两次 update 仍只有一个 undo 单元。
- [x] admission、真实 brush update 后的像素失败信号、checkpoint、finish 四类失败均进入原 scheduler failure/cancel 链；每行一次 cancel、无成功 undo、回滚为空并释放 memento。
- [x] 强制 producer 递归三步后停止输入，finish 观察到必要后继全部完成；原 cancellation 控制仍通过。
- [x] BC9 首个资源子范围：24 MiB 单文档长 stroke 的慢 reader、两次 update、递归 drain、undo/redo、取消和退出 resident 归零；8 MiB 双 backend 的 retained/reserved/release/原子拒绝/close 归零。
- [x] BC9 / OP9 原子准备子范围：普通 direct `writeOperation` 在 callback 前准备全部 mutable target backing；失败时 callback 零进入，只回滚本 execution 新准备页，保留同一 history owner 与既有 pending 的重试；成功时取消未触碰准备页，不增加 `pagesSealed`。
- [x] BC9 continuation 所有权审查：原 job 已出队，updater 在返回后删除 job/data；通用 data 无重试克隆，一次 update 有并发兄弟与后继 cut。当前不能安全消费 `RetryablePressure`，见 [92 §16.20](../92_br1_m6_m8_execution_baseline.md#stroke-continuation-ownership-audit)和 [API §19](API_CONVERGENCE_MAP.md#stroke-continuation-ownership-audit)。
- [x] BC9 共享非载荷子范围：产品 metadata/cache 共用父总额；child registry 节点实际收费，空闲注册项不静态分额；1 B/1024 B controller、双 backend 和原 24 MiB/pool=0 真实长 stroke 通过，析构/退出归零。
- [x] BC9 waiter state/context 本体历史检查点 §16.23：唯一 owner 和本体收费成立，原目标结果 26/0/0；当时 weak context handle 已由 §16.26 的 intrusive inert context+sequence 替代。当前数组/cache 计账与结果按 §16.27，不外推历史运行。
- [x] BC9 prepared wake state 子范围：既有 prepare 入口接受内部 budget；waiter/read last-use 的 wake state 本体实际收费，dormant/ready 内嵌链删除每 wake list node；context+state+wake 空载预检、move/reuse/reset/析构归零成立，目标联合矩阵 67/0/0。
- [x] BC9 wake control block 子范围：删除 `shared_ptr<WakeState>` control block，以已收费 state 内原子引用承载 handle 与 monitor 临时所有权；in-flight reset 证明先退预算、回调结束后释放 capture，目标联合矩阵仍为 67/0/0。
- [ ] BC9 下一完整存储段：补 callback/task/retry/pass/必要终结和墓碑实际尾内存的收费 owner 与失败出口；跨 store 公平必须绑定可取消的原请求/continuation owner，再用真实多文档并发长笔验证。context/wake 控制块、独立 free-list 和 slot 数组已有替代，不再列待删。继续使用现有 `Failed`，禁止新增等价通知族、按注册 backend 数分额或预埋上层参数。
- [ ] BC9 自动恢复：只有同批实现原未执行工作单元的 ownership transfer、可靠 permanent/waitable/cancel 分类、原 scheduler 唤醒/取消/finish 排序，并合并旧模糊失败分支后才可领取。
- [ ] BC5/BC8：current/self-source、通用 path、selection、indirect/mask、LoD/wrap 按实际入口迁移或保留，并列清退出条件。
- [ ] BC9：真实资源计账、tiny budget、长 stroke、多文档和 close/cancel 进度完成后，才由稳定策略配置调用 opt-in；不增加公开 flag。

API 增删账本见 [API §15](API_CONVERGENCE_MAP.md#direct-stroke-pilot-delivery)和[无 API 增量的联合 fixture §17](API_CONVERGENCE_MAP.md#direct-stroke-joint-fixture)，实现关系见 [01j §6–§7](01j_real_stroke_integration.md#direct-stroke-pilot-delivery)。首条接线证据见[原记录](../evidence/br1_direct_stroke_pilot_20260929/README.md)，其中 Freehand case 的 Wash 证据限制由[新记录](../evidence/br1_direct_stroke_joint_20260929/README.md)修正；当前 direct persistent 联合正确性以新记录为准。下一批领取 BC9，不因身份断言增加 getter，不因可选 helper 再细化底层版本。

<a id="stroke-mainline-intrusion-audit"></a>
## 19. `tool/strokes` 主干侵入收缩清点

- [x] 以 `origin/master` 复核真实差异；color sampler 与 move strategy 不属于 BR1 改动。
- [x] 删除测试专用 `FreehandStrokeStrategy` flag；`freehand_stroke.h` 恢复为主干接口。
- [x] `freehand_stroke.cpp` 只保留 dirty 发布前的一次必要调用；active 检查和 dirty 扫描收回 transaction owner 基类，默认路径只有一次 inactive 判断。
- [x] 保留 base failure reporting、结果化 finish/cancel 和 retry；双架构 `KisPainterStrokeCompletionTest::testPixelFailure` 各 22/0/0，证明它们是可失败写正确性消费者。
- [x] persistent pilot 双架构各 4/0/0；收缩没有改变 owner/display/finish/cancel 结果。
- [x] 本次多 update、策略 undo/redo 和递归 drain 仅修改测试，生产 `tool/strokes` 与生产 API 均为 +0/-0。
- [x] 本次 BC9 子范围保持 `tool/strokes` 和全部生产源码 +0/-0；8 MiB 元数据容量反例没有被用来增加 UI 状态。
- [ ] BC9 余项继续不扩大 `tool/strokes`；新改动必须由资源、进度或 save 的具体反例证明必要，并优先落在 PageStore/DataManager 结果边界或原 scheduler owner。
- [ ] 默认启用时优先由既有 preset/strategy 能力推导资格；只有无法表达且有产品消费者时才保留 protected opt-in setter。

详细逐项理由和退出条件见 [API §16](API_CONVERGENCE_MAP.md#stroke-mainline-intrusion-audit)。

<a id="mainline-intrusion-contract"></a>
## 20. 新管线内聚与主干低耦合强制门

- [ ] **MI1 单向依赖：** UI/tool/paintop 及 PaintDevice/DataManager 以上公共层的 header、字段、参数和返回值不出现 PageStore session/page/claim/borrow/publication/budget 内部类型；tiles3 既有适配债务不扩大；PageStore 不依赖 UI/paintop/preset。
- [ ] **MI2 原 owner 唯一：** transaction、scheduler、painter 的原职责不分裂；没有第二 owner、第二完成队列或并列成功/取消状态。
- [ ] **MI3 最窄桥接：** 每个跨层语义只有一个桥；同批列出替代/删除对象，不能按 async/1px/mirror 等分支复制同义接口。
- [ ] **MI4 默认路径轻量：** 关闭状态的特性专属路径至多一次 inactive 判断；无新增特性专属扫描、分配、容器、锁、TLS 写、页查询和 checkpoint；S01 通用 failure context 独立计账。
- [ ] **MI5 失败复用：** 拒绝进入原 scheduler cancel/retry 与 transaction 终点；无 replay、部分提交或析构静默成功。
- [ ] **MI6 API 克制：** 无测试专用 public API；当前 pilot 后 UI/tool/paintop/painter/PaintDevice/stroke scheduler 的 public/protected API 默认净增长为零；例外必须同批列产品 consumer、替代/合并对象和删除触发条件。
- [ ] **MI7 主干局部性：** 每个主干 hunk 映射到原 owner、真实 cut、失败或终结；页调度、预算、缓存、COW 和发布策略留在新管线。
- [ ] **MI8 债务退出：** setter/friend/overload/模式判断逐项列消费者；默认启用前复核，消费者归零时同批删除。
- [ ] **侵入账本：** 记录对照 commit、逐文件 `+/-`、新增符号/字段/include/friend/锁/TLS、关闭状态成本、同批删除与目标测试。
- [ ] **停止条件：** 主干 diff 若没有关闭新业务断言、删除重复责任或减少原工作量，停止并回退扩张。

具体定义、拒绝示例、当前 direct stroke 裁决和默认启用门见 [主干低耦合合同](MAINLINE_INTRUSION_POLICY.md)。每个后续批次复制本节并按实际代码勾选；不得以总测试数、性能预测或提高架构 ratchet 代替。

**最近三批 MI1–MI8 结算：** BC10 联合 fixture 与 BC9 首个资源 fixture 都只改测试，生产文件 +0/-0；当前 backing 原子准备批只修改 PageStore、write coordinator 和 DataManager backend 六个内部文件及两个测试文件。当前批新增 execution 私有准备/收尾、session 私有 preparation mode、coordinator 内部取消复位和 backend 私有模板策略参数；public/protected 产品 API、manager/Tile/UI 字段、include、friend、锁、TLS、`tool/strokes`、paintop、painter、PaintDevice 和 scheduler 改动均为 0。PageStore 创建并回滚物理准备，backend 只选择既有 cursor ABI 是否启用；两组 execution bits 复用原 BoundEntry 位置与原预算 allocation，没有第二份键表或状态 owner。现有 `Failed` 保留到可靠分类与实际 consumer 同批出现。因此三批均满足 MI1–MI8；上面的全局门仍保持未勾选，供默认启用与后续生产批逐项复核。证据见 [BC10 联合 fixture](../evidence/br1_direct_stroke_joint_20260929/README.md)、[BC9 资源 fixture](../evidence/br1_direct_stroke_pressure_20260929/README.md)和 [backing 原子准备](../evidence/br1_operation_pressure_boundary_20260929/README.md)。

**§16.61 驻留残余清理 MI1–MI8：** 对照产品`e0fc83ab79a2d761bd61cdae64226a569330d3bb`，主干仅TileDataStore.cc+3/-0，在原swap登记owner复验准备数组身份；真实caller为swap-in/out，UI不能观察或决定该物理事实。上层API/类型/状态/字段/include/friend/锁/TLS新增0，普通无observer tile走原早返回，无新增存储/扫描。provider内部删除重复取消与静默拒绝，保留真实冷拒绝/reader/transition忙。ABA时序和原24 MiB压力、双架构八组5614/0/0通过；无性能/allocator/TSAN资格。收费扩张已撤回，Qt欠项保持。该有限批符合MI1–MI8，全局门仍未勾选；[账本](CODE_INDEX.md#residency-protocol-cleanup-code-index)、[API](API_CONVERGENCE_MAP.md#residency-protocol-cleanup-api-delivery)、[证据](../evidence/br1_residency_protocol_cleanup_20261003/README.md)。

<a id="closure-package-checklist"></a>
## 21. CP0–CP10 收口包领取与结算

包定义/工时/依赖只见 [92 §17](../92_br1_m6_m8_execution_baseline.md#closure-work-packages)，源码反查见 [CODE_INDEX](CODE_INDEX.md#closure-code-index)，API替代见 [行动账本](API_CONVERGENCE_MAP.md#closure-api-actions)。下列勾选代表整个工作包已达到交付条件；局部已有代码不预先勾成完整完成。CP1由§16.108整体结算；CP2由§16.109–§16.113逐项结算代码/安全范围，完整审查绑定当前源码与结果。CP3和正式M6不随CP2勾选取得资格；下方历史子项的开放描述仅属于其冻结点。

- [ ] **CP0：** required模式/恢复域与缺测清单冻结；实际工作树/依赖和upstream对照可运行，正式测量包含显示和drain；范围变更明确登记。
- [x] **CP0当前基线/执行清单子包：** [§16.140](../92_br1_m6_m8_execution_baseline.md#cp0-current-applicability-delivery)落实31组合同责任、48个既有数值桶及实际consumer/测试/缺证；当前普通freehand四能力+96计时过程全部通过，stroke约2.26/2.32×upstream。只结算本批可运行对照与清单，不代替正式场景实例/协议、visible/尾/M/K或完整CP0。
- [x] **实际archive容量补证子项：** 同包保留ample原行，增加四BPP的一页byteBudget真实耗尽、旧archive/current/View保持、forget后同owner重试和最终清理；两架完整Reference1892/0/0，测试+61/−5、生产0。不是物理磁盘满、统一SSD全压力或SSD handoff资格。
- [x] **CP1：** 实际callback/context/task/retry/pass/terminal/墓碑尾内存及两个平台出口已由§16.108结算；沿用§16.107真实fault停止规则，不重领旧子项。
- [x] **CP2：** M6剩余legacy身份/原exact重解析、raw/batch排斥、epoch/ABA/晚completion和实际准备失败点联动；旧G、Fresh、cancel/abort与退出正确。[§16.113完整审查](../evidence/br1_cp2_epoch_completion_20261004/cp2-audit.json)结算代码/安全；当前install/结构阻塞由§16.114结算，CP3正式M6仍开放。
- [x] **CP3已知拒绝子包：** [§16.136](../92_br1_m6_m8_execution_baseline.md#m6-early-rejection-delivery)完成M1–M3/C1/V1–V2；lease/last-use准备K→0，native pin后续准备/安装尝试K→0，最终claim保留。12/12个blocker原库增益成立，完整安全11116/0/0、6资源探针和结构通过；固定性能矩阵已结束，不续采。
- [x] **CP3冷准备/借用子包：** [§16.137](../92_br1_m6_m8_execution_baseline.md#m6-provider-borrow-delivery)完成B1–B3/V1–V2；K16同provider lookup16→0、native pin冷Prepared16→0，foreign强引用和最终claim保持。当前安全11180/0/0、6资源探针、结构通过，父库foreign目标控制228/0/0另列；固定3824实验进程及冻结身份通过，不续采。原库ARM K1确认+1.76%，K16时间增益未确认。
- [x] **CP3有限计量诊断：** [§16.138](../92_br1_m6_m8_execution_baseline.md#m6-calibration-resolution-delivery)完成D1–D4/V1：1920诊断+72预检通过、2504输入未变；64→512ms使16/16组合波动下降、描述性±2%组合4/16→12/16。完整sample/产品保持；QoS/seed无一致修复，本包停止窗口诊断和昂贵正式扩样。
- [x] **CP3执行变异有限包：** [§16.139](../92_br1_m6_m8_execution_baseline.md#m6-execution-variance-delivery)完成C1/D1–D3/I1/V1及P1记录：274测量过程/6188927操作通过，P1另计1通过/1上限失败并保留；CPU时钟覆盖与E/P查询关联定位完成，原timed work保持。ABBA同期两策略均0/4满足±2%，候选否决、不续采，不等于产品加速或计量责任关闭。
- [ ] **CP3完整资格：** 计量责任仍未闭合；稳定并验证实际执行条件后独立完整正式family，不继续同义runner调参或无预算微优化。旧正式校准2/20、联合hit0/4和miss2/16、Fresh/H4八桶保持；不借诊断追认资格。common metadata实际驻留≥25%分母、CP0 required独立补证。自然正例/业务分布仍未建立；旧20%/30%失败、M6/M7/M8未通过、persistent默认关闭，完整资格只在92更新。
- [x] **CP3 §16.135有限基线包：** 事前冻结后完成2942运行进程及161396个fixture原始样本，双库双架针对性安全1832/0/0、受限容量和代际消费已测，源/库身份和全部失败保留。生产改动0；只结算本轮基线，不勾选完整CP3。[结果、理论差距与下一责任](../evidence/br1_m6_opportunity_baseline_20261006/README.md)。
- [ ] **CP4：** M7存在实际生产consumer及唯一selector/epoch admission；全部页先claim，首字节后失败0；第二页冲突与fence分布通过；超限fallback保留。
- [ ] **CP5：** 原未执行工作由原scheduler唯一拥有，永久拒绝不等待，可等待释放后无新输入继续；cancel/finish有序、兄弟不重放；持续热点/慢退休/SSD耗尽/真实多文档公平与预算均通过。
- [ ] **CP6：** current/G0/operation-start/exact读意图及clear/remove/default/copy/alias/planar/restore/purge联合发布/失败语义闭合；独立working extent用途保留。
- [ ] **CP7：** 通用direct/source-dependent、selection/path、indirect/mask、多painter、wrapped/LoD/异步target和iterator族逐入口迁移；联合写/读/显示/undo/失败/drain，有界资源与必要COW，不增加第二owner。
- [ ] **CP8：** 先普通undo delta与固定K成本，再有界preset准备和完整context失效；配置缓存不持writer/token，旧stroke不受新设置污染，stroke控制不回退。
- [ ] **CP9：** 每个wrapper/字段/注册/回调有静态及运行consumer清单；无consumer项删除，ABI/不同语义留理由；适用配置和完整M8语义/资源/退出同源通过，临时主干债务结算。
- [ ] **CP10：** 正式required M/K/E、尾延迟、峰值、默认/关闭状态成本与最终身份全部过门；保留失败；默认策略明确，BR1正式裁决更新。

每个包结算附“实际改动/同批删除 → 结果断言 → 当前证据身份 → 未关闭条件 → 实际人日”；连续两次小交付未达主要结果时按92 §17.4复核，不自动再拆一个新版本。不会为纯文档更新或每个小hunk新增产品测试。

- [x] **CP3 §16.115有限收口：** 原paid work array/authority/缺口增长与固定两node handles收敛；Entry原reservation持有到Data延迟释放，父restore free129改为两架零释放，无新owner/字段/队列。生产净-29；最终38进程10810/0/0，两架各31080 handoff和28 index/root/restore区间alloc/free0，结构及Git blobs/运行SHA通过。冷请求减少90–93%，受控延迟改善5–12%仍未达20%/30%。完整CP3不勾选；已按§17.4重审共同publication/seal/commit责任。[证据及剩余门](../evidence/br1_cp3_cold_preparation_20261005/README.md)。

- [x] **CP3 §16.114有限收口：** 成功handoff安装中的两次free改为原paid冷slot接收最多两个node handles；完整memento存储与tile意图政策收敛，原ratchet恢复。38同源进程10810/0/0、两架各31080安装区间alloc/free0、结构/ownership/六工具与2311source Git blobs/192运行和harness输入核对通过。生产净+12，移动与生成物单列。当前受控40对性能四桶未达门，完整CP3不勾选。[审查及剩余门](../evidence/br1_cp3_m6_freeze_20261005/cp3-audit.json)。

- [x] **CP2 §16.113结算：** 真实两个provider incarnation的epoch/numeric token重用/晚completion联合48项，五有限准备压力点/两载体/原三终结120项；共同plan真实136B candidate/80B descriptor拒绝接回native原fail/cancel/abort，无新生产API/owner，生产净+6。当前双架十进程8562/0/0、actual0/reaped、source/runtime/Git blobs同源；原始UE、fixture和ENOSPC记录保留。完整CP2完成，CP3/结构门及正式M6未验收。[证据](../evidence/br1_cp2_epoch_completion_20261004/README.md)。

- [x] **CP2 §16.112有限差集：** 三Tile构造消费raw空结果，manager先准备canonical clone，legacy源继续legacy；空backend回退与chained重复初始化/局部未安装链删除，两hash部分失败沿正常析构。原extent在RAII交出前准备。生产+17/-35、无新生产类型/字段/owner；最终双架十进程8226/0/0、actual0/reaped、source/runtime/Git blobs同源。两模板测试不等于完整另一hash/OFF配置；结构门及完整CP2未通过，下一[联合时序与准备核验](../evidence/br1_cp2_clone_refusal_20261004/cp2-audit.json)。[证据](../evidence/br1_cp2_clone_refusal_20261004/README.md)。

- [x] **CP2 §16.111有限差集：** 原G0先取得有效read再交接只读COW存储，getter拒绝不返回wrapper；manager销毁后原字节可读、写锁拒绝。删除attach、current复制/presence二查、临时cache及桥oldData参数，全部caller迁移。生产+44/-31、无新状态/owner；最终双架十进程8064/0/0且actual0/reaped。完整CP2及结构门仍未通过，下一步按[有限差集](../evidence/br1_cp2_tile_selection_20261004/cp2-audit.json)推进。[证据](../evidence/br1_cp2_tile_selection_20261004/README.md)。

- [x] **CP2 §16.110有限差集：** 原parked batch wrapper读取借原mutation并复验expected；foreign拒绝、nested guard复用、真实cache/lease交接硬满走原failed/finish/cancel，current/exact保持。生产+96/-54、无新state field/owner/queue；双架十进程7992/0/0且actual0/reaped。当前调用闭包unresolved0，旧checkpoint/memento include及本轮bridge引用13>9仍未通过；其余exact/raw-batch寿命/epoch/ABA/晚completion/准备拒绝继续开放，不勾整包CP2。[证据](../evidence/br1_cp2_batch_read_20261004/README.md)。

- [x] **CP2 §16.109有限差集：** 原raw四入口共用写准入结果，拒绝不暴露/修改before-image；copy/purge解锁与codec空结果同批迁移，生产+70/-71、无新state/API。双架八进程4186/0/0且实际exit0/reaped；当前调用图已重建，旧checkpoint/memento include ratchet仍未通过。原exact、Reserved batch、epoch/ABA/晚completion及完整准备拒绝差集继续开放，不勾选整包CP2。[同源证据](../evidence/br1_cp2_raw_access_20261004/README.md)。

- [x] **CP1 §16.73有限差集：** 真实冷COW拒绝走原execution回滚、同owner恢复；metadata成功activity与receiver拒绝统计在原gate内终结；8MiB原stroke准入、producer执行和visible checkpoint后取消。最终双架8086/0/0、原压力72/0/0和有限allocator拒绝同源；[八项登记](../evidence/br1_cp1_qualification_20261003/README.md)保留完整allocation/free对账、所有阶段故障/联合恢复、总硬界、全static、外部/非Darwin、TSAN Inconclusive及八UE未drain。该子项不勾选整包CP1。
- [x] **CP1 §16.74有限差集：** seal activity异常安全归还、已接受checkpoint捕获连续硬满恢复、关闭诊断无16B TLS及4B固定收费、识别的static最后free；双架8088/0/0与原压力72/0/0同源。真实heap正控制/无溢出已补，但487首末拒绝目标122接续失败、owned QWaitCondition私有120B漏费、完整owned峰值/平台/TSAN和八UE仍开放；该子项不勾选整包CP1。[证据](../evidence/br1_cp1_reconciliation_20261003/README.md)。
- [x] **CP1 §16.75等待容量差集：** 九类owned Qt wait隐藏heap删除，内嵌容量随原owner sizeof收费/最后引用释放；read fixture实际竞态关闭，CPU故障开关atomic。最终双架8088/0/0、压力72/0/0；七组TSAN2892通过，Qt读写锁独立控制保留Inconclusive。505生命周期进程122接续失败、完整对账/硬界/联合恢复/nonDarwin和至少九个旧UE未drain仍欠；整包CP1不勾选。[当前证据](../evidence/br1_cp1_wait_storage_20261003/README.md)。
- [x] **CP1 §16.76 commit retention差集：** 原候选在root安装前准备付费node/output，关闭六个已接受后拒绝；删除后置retention、orphanedAfter及其cleanup。双架8100/0/0、原压力72/0/0；505实际生命周期进程389成功、116 seal接续失败保留。七组TSAN2898通过、整体Inconclusive；原九UE加本批空backend fixture事故一例共至少十个未drain，后续绿表不覆盖。完整清点/硬界/联合恢复/nonDarwin仍欠，整包CP1不勾选。[当前证据](../evidence/br1_cp1_commit_retention_20261003/README.md)。
- [x] **CP1 §16.77 原seal接续差集：** 资源拒绝保原frozen input/claim/page/proof，原metadata接受事实阻止重放，overlay install才转proof，generic caller同步迁移；语义拒绝仍cancel。关闭108取消/8重放，505生命周期进程487实拒全exit0；双架8108/0/0、压力72/0/0。operation每架224实拒，暖态消失的父1248B增长以88冷进程86实拒补测，cold每架17实拒；四种连续硬满恢复/取消通过。七TSAN目标2902通过，整体Inconclusive、十旧UE未drain；联合无输入内部清理、完整对账/硬界/所有拒绝族/晚handle/外部/nonDarwin仍欠，整包CP1保持未勾选。[该冻结证据](../evidence/br1_cp1_seal_retry_20261003/README.md)。
- [x] **CP1 §16.78 原orphan scope进度差集：** 原链复用既有collector task/delay，锁外共用原cancel；provider/实际arena连续拒绝解除后，无新输入释放claim/proof/private payload，16新增行每架通过，未声称caller transaction自动终结或facade先退出全恢复。生产+46/-7净+39，内部指针16B随原sizeof收费，无新队列/task/阶段。487生命周期实拒及原压力72/0/0保持；原矩阵8139/1/0，Matched claim/像素失败在隔离父/候选24进程中均复现，仍待修。七TSAN目标2918通过、整体Inconclusive，十旧UE未drain，完整对账/硬界/联合退出/外部/nonDarwin仍欠，整包CP1不勾选。[当前证据](../evidence/br1_cp1_orphan_progress_20261003/README.md)。
- [x] **CP1 §16.79 原clear范围/实际增长竞争差集：** 付费原target在像素前取得完整claim，原batch保持到共同adapter install；临时typed结果区分contended/真实storage拒绝，原range/condition承担等待。双架8236/0/0、40 Matched进程120/0/0、702 clear真实fault及同owner连拒恢复通过；原压力72/0/0，全部中间失败保留。生产+105/-59净+46、无上层新API/owner/队列。stop后晚close死等和TSAN新TileSwapper SEGV尚未修复/裁决；十旧UE未drain、总owned硬界/完整fault与外部/nonDarwin仍欠，整包CP1保持未选。[同源八项结算](../evidence/br1_cp1_legacy_claim_20261003/README.md)。
- [x] **CP1 §16.80 permanent stop/最终引用差集：** 原enqueue返回实际接受，全部生产caller收回未接受的临时pin/activity，原Store/tree/Data完成停止后尾free；Swapper正计数pin及atomic age/pooler配置修复。停止后四bpp×facade存活/先退出和父账本验证，CPU abort等待实际Debt释放且原硬限保持。最终双架8244/0/0、压力72/0/0、七TSAN2922/0/0、预算TSAN十进程60/0/0，123源码/245运行物核对产品提交。完整owned硬界/其余fault与联合退出/平台/Qt TSAN及十旧UE四组保留，整包CP1未选。[当前同源结算](../evidence/br1_cp1_terminal_convergence_20261003/README.md)。
- [x] **CP1 §16.81实际arena/有限拒绝及可观测依赖差集：** 原arena所有收费点共用sizeof(Block)，直接malloc记录验证三真实单位/最后free；无新owner或字段。provider64实拒、operation每架234实拒、九族lifecycle497实拒/18控制/native连续EAGAIN12次均exit0；原双架8244/0/0、压力72/0/0保持。匹配插桩QtCore正反控制0/66、最终七组2922/0/0且确认实际加载。arm64 native合并区域多收16KiB仍未修，完整manager/十二UE默认失败、全owned硬界/联合退出/外部/nonDarwin保留；整包CP1保持未选。[同源证据及全部失败](../evidence/br1_cp1_owned_qualification_20261003/README.md)。
- [x] **CP1 §16.82原两线程重费差集：** 原monitor扣除仍live worker已付span，原64KiB唯一容量上限及接受/拒绝/join责任保持；executor actual +32B沿原allocator收费。两架各34真实native端点差额0、join地址unmapped，12连续EAGAIN/4控制、双架CPU/Reference4288/0/0、插桩Qt原目标12/0/0全部actual0；原图/ratchet保持。初次查询外部合并、全owned硬界/联合最后退出/平台/完整TSAN/十二UE仍欠，整包CP1保持未选。[本轮证据](../evidence/br1_cp1_native_span_20261004/README.md)。

- [x] **§16.72当前CPU列明存储集中实现：** root/control/bootstrap、observer登记、format/oracle值、metadata map/index/link、source/read cache、history/backend/extent及Darwin runtime/deferred实际收费；原close转交terminal节点，删除复制集合/诊断；同Growth复验删除三次竞争业务拒绝，null free不归活费。生产63文件净+947、测试14文件净+155体现保证增量，非纯去重；同源双架22进程8082/0/0、压力三对66/0/0全部exit0，Matched字节/callback/实际释放不变。图87TUs/2158APIs/27137edges/25callbacks，原19-file侵入门未放宽，backend重复状态两项删除，manager引用25→24。新增helper有实际consumer，原业务阶段/队列不新增；native starter同步及COW/control成本单列。[16组分配合同与失败链](../evidence/br1_cp1_concentrated_20261003/README.md)、[代码](CODE_INDEX.md#cp1-concentrated-storage-code-index)、[API](API_CONVERGENCE_MAP.md#cp1-concentrated-storage-api-delivery)。**整包CP1仍未勾选：** 完整逐拒绝点/全局allocator/总峰值、Qt/OS外部容量、非Darwin/最终static退出、旧UE未drain和TSAN未qualified；M6/M7/M8正式0/3，persistent默认关闭，实际工程人日未记录。

- [x] §16.26：context 控制块、请求数组收费/退出释放、候选引用环和独立 free-list 收敛；双架构目标回归 146/0/0，仅绑定该批源码。
- [x] §16.27：普通/父 reserve 和 waiter 共用实际 slot 数组冷准入；内嵌 reservation 引导自身收费，锁外分配/释放、重新复验，满额拒绝保留 grant、复用不需新存储。controller 存活期间 cache 继续收费，退出实际释放。该项不关闭 callback/task/墓碑、公平或 M6–M8。

- [x] §16.29：所有即时任务共用原 executor 的 typed node/FIFO/最终释放；last-use 实际 task/capture 收费，退休/history 投递失败撤销状态，terminal 冷准备。不关闭其余 task/context/deadline/record/pass/尾内存收费和完整 CP1。见 [本批证据](../evidence/br1_immediate_task_convergence_20260930/README.md)。
- [x] §16.30：原allocator的retained收费寿命实际接wake/context/已预算task及read/retirement弱控制块；controller后保留原parent/child收费到物理free，stop后无新分配；read冷准备出owner gate并重验。原提前退费/raw字段/ensureWakeContextLocked已删除；双架构目标3806 passed。本项不关闭其余capture/node/record/pass/task/terminal/runtime准入与自主进度，完整CP1仍未勾选。见 [本批证据](../evidence/br1_retained_storage_owner_20260930/README.md)和 [实际差集](CODE_INDEX.md#retained-storage-code-index)。
- [x] §16.31：history/退休pass、budget/read通知及退休wait原任务冷准备并复用；terminal实际收费到controller后free；删除重复分配/捕获/dispatch bad_alloc分支和旧TerminalCleanupJob。两架构满额复用、业务终结与原目标3810 passed，上层API净增0。整个CP1仍未勾选；pass scratch、capture/deadline/record、tree/deferred task和runtime及对应硬满恢复按 [当前差集](CODE_INDEX.md#prepared-reclamation-code-index)继续，见 [证据](../evidence/br1_prepared_reclamation_20260930/README.md)。

- [x] §16.32：实际typed callback/subscriber/signal/state/registry readiness record收费，deadline node嵌入原state；门外准备、原identity重验、取消/在途/弱尾物理free后退费，删除旧std::function/额外map节点/QP内部包装。双架构3982 passed，上层生产改动/API净增0。每次retry重建、record/orphan/pass与固定控制成本仍开放，完整CP1未勾选；[下一代码差集](CODE_INDEX.md#callback-storage-code-index)、[证据](../evidence/br1_callback_storage_20261001/README.md)。

- [x] §16.33：backing/provider前冷准入实际唯一退休节点；registered/orphan、retag/handoff及分区/pass/process/close转交同node；orphan/admission/grant内嵌，删除重复容器/三类shared box。initial整体准备，原门内注册/回滚、门外free。双架构4580/0/0，上层生产/API净增0；[源码差集](CODE_INDEX.md#retirement-record-code-index)、[API](API_CONVERGENCE_MAP.md#retirement-record-api-delivery)、[证据](../evidence/br1_retirement_record_20261001/README.md)。恰满节点目标显式停auto，必要wait/retry、其他scratch/core/固定成本及完整自动进度仍欠，CP1未勾选。

- [x] §16.34：原queue context/retry Wait/task/capture/Delay在physical adoption前一次冷准备；metadata恰满、必要record订阅拒绝仍保留同debt并自动retry，registered/orphan与实际Debt释放后无新输入可drain。generation重臂、取消/晚callback和在途coalesce沿原活动pin；旧scheduleAfter/one-shot及每retry重建删除。正确build路径双架构4590/0/0，首次旧build结果不计入，上层生产/API净增0；[源码差集](CODE_INDEX.md#prepared-retirement-retry-code-index)、[API](API_CONVERGENCE_MAP.md#prepared-retirement-retry-api-delivery)、[证据](../evidence/br1_prepared_retirement_retry_20261001/README.md)。其他read/history/pass/core与固定成本、全部硬满失败/恢复仍欠，完整CP1继续未勾选。
- [x] §16.35：原read request/lease内嵌cancel/release retry，删除ID deques、ack快照、releasedKeys和Store聚合；冷context/Delay保持恰满自主last-use恢复，GC通知拒绝保留原key/记录，cleanup锁外实际free后归还activity。request冷节点准备在读选择前，选择/AcquireRead同锁，修复本轮发现的default GC窗口；effects异常重锁/计数归还。双架构4608/0/0，9个新数据行实际64KiB恰满及拒绝恢复，初始失败保留；[清点](CODE_INDEX.md#read-terminal-storage-code-index)、[API](API_CONVERGENCE_MAP.md#read-terminal-storage-api-delivery)、[证据](../evidence/br1_read_terminal_storage_20261001/README.md)。不等于整Store硬满close/物理GC或全局分配失败原子性；captured/history/pass/core及固定成本仍欠，完整CP1继续未勾选。
- [x] §16.36：原capture保护前准备收费释放节点/版本容量；销毁和部分准入回滚转交同一节点，查询与释放共用排序数组。旧sealedPages QHash/析构复制、PendingCapturedRelease/deque、failed/released数组及无consumer的legacy capturedScope分支删除；已完成metadata/snapshot解保护不重放，原read task/Delay接续，close/stop复用原出口，锁外实际free后归还pin。4个新数据行及既有目标双架构4616/0/0，首次并发restore回归保留且修复；[清点](CODE_INDEX.md#captured-release-code-index)、[API](API_CONVERGENCE_MAP.md#captured-release-api-delivery)、[证据](../evidence/br1_captured_release_20261001/README.md)。生产净增是新增保证成本，不记纯去重收益；history/effects/core、capture辅助存储及完整退出/自主进度仍欠。完整CP1未勾选，92 §17.2按剩余端点原位重估，实际人日未记录。
- [x] §16.37：history五组容器/独立foreground扫描/caller效果聚合删除，收费Work保存原key/扫描及未接受效果，固定32 candidates/16-pointer pass；原退休record物理准入前准备operation node，效果交接无provider callback/新存储，有效result仅绑定/轮询。真实key/Debt拒绝无新输入恢复，效果/operation硬满转交、同步退休、跨片扫描与idle pin归还验证，双架构4626/0/0；[清点](CODE_INDEX.md#history-handoff-code-index)、[API](API_CONVERGENCE_MAP.md#history-handoff-api-delivery)、[证据](../evidence/br1_history_handoff_20261001/README.md)。Qt投影/效果容量、generic operation/core、永久压力尾退出和其他实际控制存储继续同CP1，未授予全pass零分配或M6–M8资格。

- [x] §16.53：原Debt提交直接接受paid effects并转交原record，metadata Qt输出、Store/publication聚合、History输出/二次交接和旧retireEffects入口删除；同一ready许可与retireBatch保留foreground/worker/manual政策，部分operation回滚的拒绝出口也泵送前页。双架构5404/0/0、实际提交后恰满/原节点/额度/receiver拒绝及双页Debt拒绝接续验证，生产净-12，无新持久阶段/队列，门限不变；[清点](CODE_INDEX.md#effect-acceptance-code-index)、[API](API_CONVERGENCE_MAP.md#effect-acceptance-api-delivery)、[证据](../evidence/br1_effect_acceptance_20261002/README.md)。§16.38–16.52中间交付以92的冻结记录为准，不累加不同源码测试资格。overlay、外部Qt/控制本体/bootstrap/固定成本及完整永久压力尾出口仍欠，CP1继续未勾选。

**§16.62 CP0 / dirty extent MI1–MI8：** 生产仅backend与低层KisMemento，前者在原history接受后交接同一canonical delta的dirty bounds，后者只更新原四个标量。新增低层语义setter有真实undo/redo消费者，上层public/protected API、字段、PageStore include、锁/TLS/队列新增0，PageStore类型不向上扩散；原19-file ratchet未放宽。普通history终结增加delta查询/扫描，不能声称MI4实际成本合格或零分配；描述性12对/架已暴露stroke/undo/redo回退。相关4210/0/0通过不抵消完整manager353/25和两个未退出尝试，全局MI/阶段门仍未勾选。[责任账本](CODE_INDEX.md#cp0-matched-baseline-code-index)、[API](API_CONVERGENCE_MAP.md#cp0-matched-baseline-api-delivery)、[同源证据](../evidence/br1_cp0_matched_baseline_20261003/README.md)。

**§16.63 准备复用 MI1–MI8：** 原execution复用admitted Page/原reservation，删除暖页prepare guard/pin/restore；原Extent Growth修复负坐标slack政策。主干仅ExtentManager.cpp+8/-2，无新增API/类型/字段/状态/锁/TLS/队列或上层依赖。冷pin和未写generation成本单列，actual guard真实swap-in保持；19-file ratchet未放宽。双架构十进程6304/0/0含完整manager/CPU，三个旧失败尝试仍UE；原extent/其余控制存储收费、全局MI/阶段/性能保持未勾选。[账本](CODE_INDEX.md#execution-preparation-reuse-code-index)、[API](API_CONVERGENCE_MAP.md#execution-preparation-reuse-api-delivery)、[证据](../evidence/br1_execution_preflight_20261003/README.md)。

**§16.64 CPU binding存储 MI1–MI8：** 原prepareAdoption前置实际binding/control容量准备，原adopt接受tile，全部provider/guard/reservation/handoff/link/cache及测试派生类同步迁移；旧Qt binding创建/持有/cast删除，无桥接owner。生产仅原PageStore9文件+53/-43净+10，TU内adoptTile一个consumer，上层API/持久字段/状态/锁/TLS/队列新增0；实际收费和最后weak尾free是保证增量，不能记等价净删。架构/原19-file ratchet不放宽，双架十四进程7542/0/0、全exit0；首轮24MiB组合pressure准备拒绝未解释，旧UE和性能回退仍保留，完整CP1/全局MI/阶段门未勾选。[账本](CODE_INDEX.md#resident-binding-storage-code-index)、[API](API_CONVERGENCE_MAP.md#resident-binding-storage-api-delivery)、[证据](../evidence/br1_resident_binding_storage_20261003/README.md)。

**§16.65 detachment候选 MI1–MI8：** 原Entry不再无条件保留发布载荷，prepare/install/clearBatch同步消费共同事实与同Data可选数组；原取消/claim/分批释放政策保持，上层生产API/持久阶段/生产侵入文件新增0。生产+50/-43、测试+70/-0；新增一个TU内载荷类型/数组，多40字节候选头部，不能记复杂度净删。双架父硬满安装/取消及精确归费、十四进程7546/0/0通过；后续surface容量拒绝、8MiB初始准入、旧UE与完整CP1/全局MI/性能仍未勾选。[账本](CODE_INDEX.md#checkpoint-pressure-code-index)、[API](API_CONVERGENCE_MAP.md#checkpoint-pressure-api-delivery)、[证据](../evidence/br1_checkpoint_pressure_20261003/README.md)。

**§16.66 metadata目录/control MI1–MI8：** 生产仅原PageStore三文件+36/-86净-50；原allocator收费真实shard/control、directory和identity，configure局部候选一次发布、拒绝/晚free共用原责任，旧估算/手工目录fee/超预留拒绝删除。上层API/业务阶段/锁/TLS/队列/外部侵入新增0，原19-file ratchet不放宽。真实少一字节三次拒绝/同对象重试和coordinator/controller后cancel/clearBatch精确归费通过；该轮同源24MiB surface压力失败保留，不能用初始绿矩阵关闭它。eager目录差集由§16.67更新，Private/authority/bootstrap及完整CP1/全局MI/性能仍未勾选。[账本](CODE_INDEX.md#metadata-directory-storage-code-index)、[API](API_CONVERGENCE_MAP.md#metadata-directory-storage-api-delivery)、[证据](../evidence/br1_metadata_directory_storage_20261003/README.md)。

**§16.67 metadata按需目录 MI1–MI8：** 生产仅原PageStore两文件+132/-44净+88；原growth统一目录几何/门外准备/竞争复验/退下数组晚free，constructor eager reserve、重复full-growth规划和attach隐式增长删除。新增一个私有PreparedDirectory类型、三carrier共120B、局部plan+24B及移动/峰值成本由真实增长consumer承担，不能计等价净删或MI4性能合格；上层API、持久业务阶段、锁/TLS/队列和外部侵入新增0。图87TUs/2025APIs/25510edges/21callbacks、原21manifest/25ownership/16census/19-file ratchet不放宽。真实父额少一字节拒绝/准备后硬满安装/确实不足候选复验及coordinator/controller后Data cancel/cleanup归费通过；双架十四进程7570/0/0、压力三对66/0/0均exit0。固定预留消失、64 shard空配置减少1.5MiB已验证；完整总峰值/永久压力、8MiB准入后取消、旧UE、Private/authority/bootstrap及CP0/CP1/全局MI/阶段/性能门仍未勾选。[账本](CODE_INDEX.md#metadata-directory-growth-code-index)、[API](API_CONVERGENCE_MAP.md#metadata-directory-growth-api-delivery)、[证据](../evidence/br1_metadata_directory_growth_20261003/README.md)。

**§16.68 metadata authority MI1–MI8：** 生产仅原PageStore一个文件+17/-29净-12；原configure候选负责actual authority/control、原shards/目录/identity准备与一次发布，删除未收费构造/重挂接/后置owner准备拒绝。原read/captured cleanup先acquire再比较同shard authority，真实foreign/身份和reservation拒绝保留。Private预算选择指针+8B、配置64B实际请求单列，不称内存净删或MI4性能合格；上层API、类型/业务阶段、锁/TLS/队列及外部侵入新增0。图87TUs/2023APIs/25535edges/21callbacks及原21manifest/25ownership/16census/19-file ratchet不变。首次实际分配/完整候选少1B连续拒绝和重试、仅read cleanup保活的controller后父硬满clear/析构精确归费通过；完整矩阵7584/0/0、压力三对66/0/0均exit0，错误测试名称的首轮日志保留。Private/standalone bootstrap、全参与者总峰值/永久尾出口、8MiB准入后取消、旧UE及完整CP0/CP1/全局MI/阶段/性能仍未勾选。[账本](CODE_INDEX.md#metadata-authority-storage-code-index)、[API](API_CONVERGENCE_MAP.md#metadata-authority-storage-api-delivery)、[同源证据](../evidence/br1_metadata_authority_storage_20261003/README.md)。

**§16.69 metadata Private MI1–MI8：** 生产原PageStore两文件+128/-94净+34，实际Private进入原configure完整候选，拒绝/最终free共享destroy；eager Private/独立operational和生产无用standalone controller删除，全部consumer acquire同core指针。Private104B实际新增fee与attached对象尺寸减少1,336B分列，facade8→56B；真正standalone体1,352B和含facade的根对象bootstrap未授收费资格。上层API/新业务阶段/锁/TLS/队列/外部侵入新增0，两个原shard签名替换，私有构造/销毁有真实consumer。图87TUs/2025APIs/25550edges/22callbacks，原21manifest/25ownership/16census/19-file ratchet不放宽。冷配置/真实首Private拒绝/少1B三次拒绝与原对象重试、空core消费者、原晚Data/read cleanup和standalone outcome9释放通过；双架十四进程7584/0/0、压力三对66/0/0均exit0。完整CP0/CP1、全参与者总峰值/永久出口、8MiB准入后取消、旧UE、全局MI/阶段/性能门仍未勾选。[账本](CODE_INDEX.md#metadata-core-storage-code-index)、[API](API_CONVERGENCE_MAP.md#metadata-core-storage-api-delivery)、[证据](../evidence/br1_metadata_core_storage_20261003/README.md)。

**§16.70 Store根存储 MI1–MI8：** 原backend唯一prepareStore通过原child/accounting冷准入实际facade/Private，configure/clone共用；旧new Store/new Private/两处delete owner删除，同Private destroy承接拒绝、同步/原terminal task及最后captured lifetime。原内部shared/limits冻结、facade一指针ABI8B保持，上层API/业务阶段/锁/TLS/队列/外部侵入新增0。生产三文件+66/-7净+59，实际冷fee4,520B、Private allocator16B、backend deleter8B、原accounting/登记120B及临时栈controller对象1,352B单列，未宣称纯去重/性能收益。图87TUs/2029APIs/25603edges/24callbacks，原21manifest/25ownership/16census/19-file ratchet保持；净增4私有API及同deleter两个登记均有真实consumer。四行真实冷拒绝/同父重试、外部parent退出及cold/late captured父硬满最后free通过；双架十四进程7592/0/0、原压力三对66/0/0均exit0。生产Store本体不重领，默认/reference/真正standalone、其他嵌套heap/control、backend/provider/history/process根、完整峰值/永久尾出口及完整CP0/CP1/全局MI/阶段/性能仍未勾选。[账本](CODE_INDEX.md#store-root-storage-code-index)、[API](API_CONVERGENCE_MAP.md#store-root-storage-api-delivery)、[证据](../evidence/br1_store_root_storage_20261003/README.md)。

**§16.71 Ledger/domain控制 MI1–MI8：** 生产七文件+58/-28净+30，Ledger Private/admission/control同Store冷allocator收费，原new/Qt类型/创建和无操作receipt独立分配删除；无record直接复用authority，原transition vector清空是释放点，有record仍以原预算准备inactive paid receipt/control再发布claim。原identity/Busy/claim/commit/cancel/detach、singleOwner与锁序保持，上层API/业务阶段/锁/TLS/队列/外部侵入新增0。Private16B allocator、admission8B receipt接口及冷根新增584B单列；当前冷根5,104B、真实claim424B、receipt/control72B、无操作0B，Store/Ledger facade8B保持，不授纯去重/性能资格。图87TUs/2033APIs/25660edges/24callbacks及原21manifest/25ownership/16census/19-file ratchet保持；原provider/receipt签名、实际override与weak/strong数组全部迁移。目标14/0/0、最终双架十四进程7598/0/0、原压力三对66/0/0均exit0；真实冷/claim拒绝与重试、原父满额无操作完成、最后admission/receipt weak free精确归费通过。默认standalone及测试heap Ledger facade、其他Qt控制/根/process、全参与者峰值/永久尾出口、完整CP0/CP1/全局MI/阶段/性能仍未勾选。[账本](CODE_INDEX.md#ledger-control-storage-code-index)、[API](API_CONVERGENCE_MAP.md#ledger-control-storage-api-delivery)、[证据](../evidence/br1_ledger_control_storage_20261003/README.md)。

- [x] §16.83有限交付：原scope最后façade/handle不自保，原单transition接受前临时数组删除；双架4352普通/2954同源Qt七body及独立paid尾0，32行/四bpp双满额stop组合通过。生产+51/-23净+28、原4960B/ratchet保持，失败和十三UE全部保留。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-orphan-terminal-delivery)。完整CP1总出口仍未勾选，M6/M7/M8正式0/3。
- [x] §16.84有限资格：同产品双架8MiB取消/24MiB压力完整body14/0/0，已识别paid/native/启动前fixed并存观察无越界、join地址unmapped/static paid0；原有限1041 handled拒绝/52控制默认正常退出，加容量primary527 actual0。生产/测试/派生增删0，原源码blob/依赖/ratchet保持。[冻结裁决](../92_br1_m6_m8_execution_baseline.md#cp1-finite-default-qualification)的manager当时Pending，实际终点及后续修复由§16.85接续；完整CP1总出口和M6/M7/M8正式0/3保持。
- [x] §16.85命名固定根计费和extent竞态：独立编译产物及冷计数两架均332B，原identity/handle/guard完整计费、capability静态值删除、原两个process gate内嵌。旧完整manager实际66/reaped暴露的原getter竞态沿已有读gate修复；候选和主树双架各4414/0/0，七个完整PageStore TSAN同次2954/0/0及目标3/0/0，原EAGAIN12实拒/4恢复均actual0。生产+50/-15、测试0、派生单列、原ratchet保持。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-static-root-extent-delivery)保留四组差集，完整CP1总出口未勾选。
- [x] §16.86独立观察及隔离候选验证：修正析构审计槽溢出、保存误判/溢出原日志和实际trace；原双架各296次416B调用内未收费请求在候选消失，四完整body5544/0/0、目标TSAN290/0/0 actual0，120编译源匹配候选commit。主树冻结未变，候选+3/-1、测试/派生0。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-unclassified-storage-observation)。
- [x] §16.87候选合入、共同capacity及最终派生核验：原allocator/retained owner、slot/arena/readiness/map/index/default consumer沿原责任预留/最后free，默认read span与实际费区分；native大块复用及memalign反例修复，原16KiB和8/24MiB预算保持。最终双架5908普通、业务14、匹配Qt TSAN七body2954均actual0/reaped，独立两架各72次观察归费/释放平衡；图87 TUs/2172 APIs/27405 edges/27 callbacks、结构门及六工具自测通过，原ratchet保持。产品6ddccc3097。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-actual-capacity-delivery)。
- [x] §16.88原VM释放拒绝与reset默认像素ownership：munmap真实拒绝双架负例actual3/reaped、同地址native释放修复双架actual0；原完整矩阵5908普通/2954 TSAN/14业务通过。语义reset原172次未收费分配两架均消失，最终3c完整CPU双架2772、匹配Qt TSAN1386及独立paid尾0，全部actual0/reaped；127源码匹配、图及原ratchet通过。6dd完整manager1105/0/0实际终点已结算，不重领Pending。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-physical-release-reset-delivery)。
- [x] §16.89结算3c完整manager实际66/reaped：同版本插桩KConfig冷探针复现全局test-mode竞争，主线程初始化控制actual0；原fixture新增initTestCase完成两步配置初始化，测试+11/−0、生产0，原压力负载不减。8 TU/MOC/链接及派生门通过，产品2e471d5efb、127源码匹配；新完整manager同时加载插桩QtCore/KConfigCore继续运行。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-config-initialization-delivery)。
- [x] §16.90删除原mutation错误拼接与configure格式编号临时Qt字节，生产+8/−3、测试0，产品87a8b43ae9；双架每架139+10次已定位请求消失，普通2772/0/0、Qt TSAN1386/0/0、独立paid尾0及图/ratchet通过。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-qt-temporary-delivery)。
- [x] §16.91收口TileData原分配、nullable候选、pool/cache、iterator/preclone、swap转换和未登记backing物理释放：父87a双架32个control/fault中14个fault失败，另有worker与活backing双架4个失败；最终候选36个进程全部actual0/reaped。产品1177fa5ecab8318fe044b071342eb0ab51654e27，五生产文件+198/−202、测试0；CPU2772、Qt TSAN1386、目标60、业务14及同源完整manager1105/0/0均通过，图/ratchet保持。旧8f/2e manager各1105/0/0也已结算。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-tile-lifetime-delivery)。
- [x] §16.92撤销低内存伪产品反例：可靠SIGSEGV上下文定位manager从错误布局读取空hash table；陈旧测试对象双架DWARF为232B，当前对象为288B，旧栈对象少56B。按当前头、MOC和原链接输入重建后，arm64/x86_64原body各3/0/0、actual0/reaped，候选镜像确认加载、故障上下文0。产品/产品测试/派生改动0，旧失败仍保留不计通过。[ABI裁决](../92_br1_m6_m8_execution_baseline.md#cp1-low-memory-abi-ruling)。
- [x] §16.93双native释放失败实际到达fail-fast：双架对同一映射分别真实注入munmap与mach_vm拒绝，诊断SIGABRT子进程均收到三个独立标记、exit134并由父进程回收。无守护arm首轮实际到达terminate/abort后被宿主保留为UE，不计通过且不继续x86默认崩溃；产品改动0。[退出裁决](../92_br1_m6_m8_execution_baseline.md#cp1-default-exit-ruling)。
- [x] §16.94后台retirement provider分配拒绝：原owner在accepted result前收回`bad_alloc`，取消prepared operation并保留同一record沿既有retry/Debt/close继续；晚captured view释放贯通history→retirement，三次拒绝后无新输入归零。产品ee67754c02，生产+10/−2、测试+34；定向normal双架/TSAN各3/0/0，完整CPU normal双架各1387/0/0、TSAN 1387/0/0无报告。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-background-retirement-failure-delivery)。
- [x] §16.95首次外部pthread span合并：`ReclamationThread`只计费并校验页对齐SDK控制对象，删除整段VM region交集及两个span字段；父提交arm64反例在外部线程形成64KiB合并边界后调度失败。产品e1c328ce8d，生产+20/−26、测试+105；定向normal双架/TSAN各3/0/0，完整CPU normal双架和TSAN各1388/0/0、无TSAN报告。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-external-native-span-delivery)。
- [x] §16.96 process/native预留到物理释放：独立报告reserved/live，准入覆盖域上限与aggregate pending，并存更新peak；准备额提交实际capacity并退回余量，物理free或pthread join后再撤销live。父提交测试2/1/0；产品02a92eb98d，目标组三环境各6/0/0，完整CPU三环境各1389/0/0，三个核心套件三环境各1274/0/0，无TSAN报告。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-process-storage-accounting-delivery)。
- [x] §16.97 PageStore memento owned存储与presence包装收敛：legacy memento保持全局heap；PageStore对象及old/new默认像素沿process allocator实际收费/物理free，析构精确归零；无生产caller的分配型`resolvePagePresence`删除，保留caller-owned selector。父提交测试2/1/0；产品0933ea04dd；目标normal双架各7/0/0，CPU三环境各1390/0/0，Reference三环境各790/0/0，完整manager normal双架各1105/0/0，legacy定向三环境各8/0/0且TSAN无报告；完整manager TSAN复现未改extent并发报告后停止。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-memento-storage-delivery)。
- [x] §16.98 当前Darwin owned存储总硬界清点：backend/provider/history/scope/lease/cache/extent/transfer全部动态owner逐项落入process对象、retained allocator、paid byte value或process PMR；caller DataManager/hash/Tile兼容对象、输入输出和未启用原型明确排除重复收费。控制`live+reserved`总界与provider/ledger物理域界共同约束且backing不重费；产品/测试改动0，复用已完成8/24MiB压力并核对6dd→0933全部生产分配增量。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-owned-total-bound-delivery)。
- [x] §16.99 Tiles3 read/capture真实分配拒绝：process硬限上的completed-source旧实现泄漏`bad_alloc`；现由原error/空source终结，可选read-cache冷对象拒绝返回空lease。原guard/字节/费用保持，释放filler后同guard重试且source/cache销毁精确退费。产品a7f0d7c537；CPU normal双架及TSAN各1391/0/0、Physical双架各397/0/0、Reference双架各790/0/0，无TSAN报告。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-read-capture-fault-delivery)。
- [x] §16.100 caller联合分配失败：初始化字节导入在provider request/resolve实际硬限拒绝时归还active计数，resolve后新backing沿原retirement退出；archive write拒绝释放原read lease且不安装pending记录。释放容量后两条caller均沿原协议重试成功。产品caaafcf58d；CPU normal双架各1392/0/0、Reference双架各790/0/0，定向TSAN各3/0/0无报告。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-caller-storage-fault-delivery)。
- [x] §16.101 archive完成轮询/取消终点：父版本最终contains拒绝后pending record永久busy，定向2/1/0；当前无分配作用域只解除身份仍匹配的survivor，取消拒绝同时归还active计数，两个原操作均可原位重试。产品6574616883；Reference normal双架各790/0/0，定向TSAN 3/0/0无报告。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-archive-terminal-fault-delivery)。
- [x] §16.102 initial replica validation活动终点：父版本provider validate分配拒绝后active计数残留1；当前作用域先恢复owner gate和计数，原caller返回false，同一外部replica原位重试进入完整流程。产品65e7d60aba；Reference normal双架各790/0/0，定向TSAN 3/0/0无报告。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-initial-validation-fault-delivery)。
- [x] §16.103 implicit default materialization终点：父版本provider request分配拒绝越过caller并遗留active/default preparation；当前失败返回原read error，两个活动计数均归零，同一稀疏页原位重试继续完整default/write/undo/close流程。产品c19c6d8301；Reference normal双架各790/0/0，定向TSAN 3/0/0无报告。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-default-materialization-fault-delivery)。
- [x] §16.104 native mutation provider preparation终点：父版本Fresh provider准备的`bad_alloc`越过`beginWrite`并跳过owner gate/active归还；当前返回原mutation错误，active为0，原session可取消、transaction可abort，后续原generic流程继续。产品f0246c95c4；Reference normal双架各790/0/0，定向TSAN 3/0/0无报告。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-mutation-prepare-fault-delivery)。
- [x] §16.105 commit provider validation终点：父版本prepared proof复验的provider `bad_alloc`越过`commit`；当前返回原无效ticket，commit准备活动归零，原transaction与proof保留，同一prepared input解除故障后提交成功。产品5b4c65ae4b；CPU normal双架各1393/0/0，定向TSAN 3/0/0无报告。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-commit-validation-fault-delivery)。
- [x] §16.106 native mutation alias provider preparation终点：父版本alias seal的provider `bad_alloc`越过`seal`；当前返回原storage-refused，active为0，原transaction/page claim/alias输入保留，同一mutation解除故障后seal与commit成功。产品db7930797f；CPU normal双架各1394/0/0，定向TSAN 3/0/0无报告。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-alias-prepare-fault-delivery)。
- [x] §16.107 余下实际fault清点与停止规则：反查provider/archive/publication/read/retirement/close真实分配边界，没有§16.99–§16.106外的新生产反例；以后只凭生产allocator栈＋父红＋原owner终点重开，不为无分配测试缝制造修复。产品/测试改动0。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-platform-exit-audit)。
- [x] §16.108 CP1两个平台出口：Linux/Unix按系统页取整并用匿名mmap/munmap，Windows按系统页取整并用VirtualAlloc/VirtualFree；Ubuntu 24.04与Windows Server 2025各48个边界＋1024个并发用例通过。默认`SIGABRT`回收改列测试宿主健康前置，当前UE PID90016保留且不再重复崩溃探针。[当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-platform-exits-delivery)与[证据](../evidence/br1_cp1_non_darwin_capacity_20261004/README.md)。
- [x] 完整CP1关闭：§16.107 fault停止规则与§16.108两个平台出口均结算；8/24MiB长压测沿用§16.98证据、不重跑。M6/M7/M8正式资格仍为0/3，下一包为CP2。
