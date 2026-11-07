# BR1 批次结束后的收敛审查，2026-09-28

本记录冻结一次源码/证据核对、主干结构比较、并发容器静态审查和真实 freehand 入口 smoke。没有修改生产源码，没有重新运行 JP1 全矩阵，也没有取得新阶段或性能资格。后续执行规则见 [CONVERGENCE](../../br1_modification_guide/CONVERGENCE.md)，当前裁决见 [92 §16](../../92_br1_m6_m8_execution_baseline.md#br1-convergence)。

## 身份与已执行检查

| 项目 | 结果 |
|---|---|
| 产品 HEAD | `5173c807c87bb1619325249a07a8b4f4f8f09f09` |
| 含未跟踪源码的差异 SHA-256 | `c1c6f145e69d6e841fb15c5873ea23db49da681f31ddc66f33b6530fd1ae3c2d`，与最后 JP1 批相同 |
| 固定 upstream 对照 | `9a24ae0d8c070884fb013594191002e1a1b39a19`，使用本地 git 对象读取原代码 |
| 原 JP1 身份核对 | 28 个构建/运行文件逐项 hash 相同；原 manifest 44 条记录全部通过，计数 9,154 / 0 / 0；66 个探针是原批证据 |
| QtCore SHA-256 | `cd0a48d2948af55889625ae0750a7d08895068deae9b6e85bdc3e1fac6dc9434` |
| 新构建 | `FreehandStrokeTest` 和 `FreehandStrokeBenchmark` 构建成功，配置为 RelWithDebInfo、arm64/x86_64、lock-free hash ON |
| 新运行 | `FreehandStrokeTest testAutoBrushStroke` 两架构分别 3 passed / 0 failed / 0 skipped；每组含 init、所选 test、cleanup |
| 没有执行 | 新整链 persistent-owner case、产品 benchmark、upstream 同依赖性能对照、OFF 完整产品配置、TSAN、Vulkan 与正式 M6–M8/BR1-PERF 验收 |

[review.json](review.json)与文档更新后的 [review-final.json](review-final.json)均核对通过，产品源码和原 28 个文件身份未变；两者记录核对时间、各文件 hash、符号位置、主干 blob 与行数；[collect_review.py](collect_review.py)只读源码/原证据，并拒绝覆盖指定输出。最后批次的窗口结论以其 [evidence-scope](../br1_s05_joint_publication_20260928/evidence-scope.json)和 [02a 观察表](../../br1_modification_guide/02a_joint_publication_boundaries.md#joint-publication-map)为据，本次没有把该复现重跑成“已修复”。

构建命令为 `/Users/apple/krita_gpu/.venv/bin/ninja -C /Users/apple/krita_gpu/krita/_build-br0-cpu -j6 FreehandStrokeTest FreehandStrokeBenchmark`，见 [build log](freehand-build.log)。逐架构命令、环境与测试/benchmark 二进制 hash 见 [freehand-smoke.json](freehand-smoke.json)，原始输出见 [arm64](freehand-arm64.log)、[x86_64](freehand-x86_64.log)。日志有资源/i18n 与 swap 路径回退警告；运行通过不等于已修复这些环境差异。

两个目标仍以 `krita_add_broken_unit_test` 注册，但本次显式构建与所选 case 可以运行；不能说它们不存在，也不能假设默认 ctest 已覆盖。该 case 使用真实 FreehandStrokeStrategy/brush，但默认 `addDabJobs` 仍向 `bltFixed` 传空 owner；因此没有证明持久 stroke 已接通。smoke 计数独立于原 9,154 项，不合并为新矩阵。

## 主干比较与质量密度

本次未提交增量相对产品 HEAD：生产源码 90 文件，+9,954 / −2,145，净 +7,809 行；测试源码 25 文件，+11,153 / −152，净 +11,001 行。生成审计数据另列 6 文件、净 +64,424 行，不计作生产复杂度。分类方法为物理行 diff，包含 libs/plugins 未跟踪 C/C++；这不是整个 BR1 相对 upstream 的全部增量，更不是缺陷率。

| 主干已有行为 | 当前差异与评价 |
|---|---|
| TransactionData/memento 覆盖整笔；Tile 在 `m_usersCount > 1` 时 COW，后续非共享写复用 backing | session/borrow/authority/read-selection 增加新协议责任；跨 dab 复用首先是在这些约束下恢复原有效率，不能当作主干原本没有整笔生命周期 |
| multi-dab 直接使用 accessor，已有异步队列和并行执行 | 当前 cursor、映射后页归属与稀疏范围已有真实消费者；收益需分别证明协调成本下降和像素/依赖正确性，不能只用 helper 测试数说明整链收益 |
| 标量 fixed-source 曾整块读回/合成/拷回 | 复用原 cursor/span kernel 是可定位的工作量减少；与持久 owner 默认启用分开评价 |
| 主干职责较集中在 tile/transaction/manager | 当前 manager 从 782 到 1,871 行、ConcurrentMap 从 366 到 722 行，承担额外适配和预留生命周期；行数本身不判坏，但维护成本已经需要真实整链交付来支撑 |

结论是**局部实现与故障证据较充分，产品闭环和相对复杂度的收益证据仍不足**。已有候选、零分配区间和失败恢复有价值；仍可复现的联合发布窗口及默认空 owner 阻止把局部成功解释为整条 stroke 质量。没有新的实测性能数据，本次不赋予“更快”结论，也不以主观分数作为阶段门。

## 并发容器定点审查

核对 `concurrent_map.h` 的 prepared-key 引用、撤销、迁移查找和 close，以及 `qsbr.h` 的 embedded action 入队/回收；这是静态抽查，未做完整形式化证明或 TSAN。

| 边界 | 观察与影响 | 后续应归属的工作 |
|---|---|---|
| entry/list gate 锁序 | token detach 在 entry gate 内 unlink；close 在取 entry gate 前已释放 list gate，检查到的这组路径没有直接 ABBA。不能外推整个 manager/publication 调用图无环 | JP6 列真实跨层锁序，默认启用前联合验证 |
| close 与晚 token | 明确要求普通 map caller/migration worker 已静止；晚 token 用引用保活，close 等 raw access 归还 | 保留这一前提并核对真实析构 caller；不能把测试中的静止关闭当任意并发 close 支持 |
| 新增 prepared-key gate | `atomic_flag` + `qYieldCpu()` 自旋；detach/redirect 查找含重试循环，未提供整体延迟上界 | HX8/JP8/S10 按实际入口测等待与进度；不是仅凭容器名即可声称 lock-free/wait-free |
| QSBR 回收 | 当前先遍历 detached chain，再按条件等 raw users，最后整链回收；强制或 >4096 时等待及整批回收在固定 upstream 也存在 | 这是继承的进度限制；新链式存储的遍历成本另计。S08/S09/S10 的全 pass 有界性不能由局部零分配入队推出 |
| 内嵌回收记录 | 取消/迁移把实际记录交给原 QSBR；降低入队分配，并增加记录与对象寿命耦合 | 保持现有故障/晚 token 证据；没有新反例不另起第三方容器重写 |

本次未确认新的容器数据竞争缺陷。最确定的当前正确性缺口仍是 JP1 证据中已捕获的 cold/warm current、extent、adapter 发布窗口；资源和延迟未证明属于资格缺口，不混写成已发生的崩溃。

## 已裁决的后续边界

下一实现批以 JP2/JP4/JP5/JP6 的真实观察窗口为主，联动其实际调用到的 JP3/JP7 端点；V01/BC10 建立真实 freehand 对照和 owner/display/finish/cancel 断言。完整资源与压力仍是默认启用门，M6 → M7 → M8/39 不变。

原 benchmark helper 默认使用 indirect 且不做普通更新，whole-stroke elapsed 也不包含所需分段指标；本次仅构建，没有拿它生成性能结论。现有 upstream worktree 登记路径已不可用，未找到并核验同一修复 Qt 下的 upstream 对照二进制。下一批先按 [比较协议](../../br1_modification_guide/CONVERGENCE.md#comparison)补齐可执行基线与 workload，再报告质量密度中的实际收益。

接口压缩安排在首条真实链成立后、扩大模式前；删除安排在消费者迁移证据齐全后。更详细的领取、停止与结果模板见 [CONVERGENCE](../../br1_modification_guide/CONVERGENCE.md)。

## 文档调整与检查范围

新增 CONVERGENCE，调整 92、两层 README、NEXT_EDITS、STAGE_MAP、CHANGE_MAP、CODE_INDEX、01j、01n、02a 和 07。当前裁决归 92 §16；导航删除重复的滚动状态，保留函数/责任索引及各批冻结证据。本次不改写旧证据或读取 archive 来指导当前工作。

[check_documents.py](check_documents.py)检查这 13 份新增/调整文档中的本地目标、锚点、行号范围和尾随空白，并跳过 archive 链接；[初次检查](document-check-initial.json)为 1,477 个链接、0 错误。最终结果另存 `document-check.json`，各版检查绑定其当时文档 hash。文档检查不证明源码行号处的语义，也不构成产品验证。根仓库 `git diff --check` 通过；原产品源码身份复核见上面的 `review-final.json`。
