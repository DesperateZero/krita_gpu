> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 从 M5 修复出口到 M6/M7/M8 与完成的前置计划（2026-09-25）

**状态：条件计划，尚未放行 M6。** 当前代码检查点为 `095193d11a`，三个阻塞及新证据见 [90](90_br1_m5_baseline_freeze_review_20260925.md)。本篇把已有 31/39/52/68/69/86 的依赖与出口汇总为下一阶段入口，不替代它们的语义、性能阈值或删除证明。特别是 **M7 后还有 M8**，不能把完成两种 handoff 等同 BR1 完成。

## 1. 先形成可冻结的 M5 基线

| 门 | 必须交付 | 退出条件 |
|---|---|---|
| B1 默认像素原子更新 | 在现有 manager/backend owner 中统一 default/restore 的可失败准备与安装 | 满 RAM、零 swap、有限 metadata 下 defaultPixel/读取/history/clone 一致；失败保留旧值，释放后可重试 |
| B2 manager 构造失败 | 明确可工作的对象不变量及失败传播，审计 constructor/copy/读取/销毁调用链 | 零/不足一页/满额/多文档下无未初始化默认值、null 默认 tile 和崩溃；不通过预算外分配掩盖拒绝 |
| B3 实际 install 存储准备 | 关闭 QHash span/node 懒分配，使用既有 shard index/arena owner | prepare 后真实 install allocator=0、rehash=0、大对象析构=0；并存 candidate、cancel、restore/addition 和边界增长通过 |
| B4 同源码整体验证 | 重生成源码/调用图，跑结构门与自测、双架构 10 套 CPU/业务矩阵和 Vulkan foundation 兼容，补确定性交错/紧预算/退出 | 保存 source/配置/库/测试 binary 哈希、命令、seed、全部失败和成功日志；源变化后不得借旧 Pass |
| B5 控制工作与 selector | 复核固定 K 增长 N/H、诊断关闭、预约高水位与真实生命周期；重跑受影响 selector matched-control | selector forced-COW 回退不超过 2%；正式置信/停止规则预冻结，旧失败不能覆盖重写 |
| B6 冻结与文档一致 | 新代码 commit、外层 gitlink、当前清单、验证 manifest、归档索引一致 | tracked 生产代码干净，未结项明确；00/68/69/90/91 同步，才授予 M6-ready |

当前 B1/B2/B3 明确未通过；B4/B5 需在修复源码上重新评估；B6 仅有失败检查点身份，尚无合格前置基线。TSAN 作为 86 已规定的补充资格单列，不能冒称已通过，也不能用它掩盖已有确定性失败。

## 2. 三种比较基线保持独立

| 基线 | 用途 | 身份规则 |
|---|---|---|
| 当前 `095193d11a` | 修复前可复现检查点、成本变化定位 | 不称为 M5-ready；证据包含三个失败 |
| B1–B6 完成后的 M5 提交 | M6/M7 相对 FreshCow 的增量收益、回退与行为对照 | 进入实现前冻结 commit、构建参数、实际动态库、fixture 和资源状态 |
| 冻结同义 upstream | 正式 BR1 CPU M/K/E 不劣性及操作上限 | 既有 upstream 参照为 `9a24ae0d8c`；正式运行须核对同源 fixture/操作端点与配置，不能沿用历史比值或未核验二进制 |

selector 控制实验是第四种局部因果控制，不能代替以上整条管线或 upstream 对照。Vulkan foundation 兼容和 CPU-only X 的 NotApplicable 也不能外推 GPU/UMA 性能。

## 3. M6：可恢复 backing handoff

入口为 B1–B6 全通过。只扩展现有 selector、provider claim、metadata physical-slot transition 和 owner ledger，不新增另一份 handoff 决策器。

- 消费已经 Ready、exact identity/layout 且独立保活的 alternate before；禁止为制造命中先复制 before。
- 闭合 prepare → claim → revalidate → retag → expose → seal/commit/cancel，旧 G 在暴露 writable A 前已能通过 alternate 读取。
- 同时验证 active reader/raw pin、alias、source copy/transfer、swap/preclone/retire、last-use、ABA、旧 binding、provider epoch；每个首字节前失败有明确 owner/回滚。
- cancel/abort 保证旧 G 仍可读；未满足条件的 FreshCow 正常可用。counter 区分实际 before copy、payload allocation、migration 和 retirement；比较完整 drain。

出口：确定性并发/失败矩阵通过、没有额外 before copy、预算与退出闭合，符合 68 的收益及 forced-COW 控制约束；所得资格只属于 M6。

## 4. M7：有界 commit-only handoff

入口为 M6 已验收，并重新确认 B3 的实际无分配发布保证。先建立 capture fence、全部目标 preclaim 与完整 `KisPreparedMutationCommit`，再暴露首个可写字节。

- 首批限同步受控 packed write/full clear/fill/copy 与已证明的单页 adapter；每个 fence **不超过 8 页且 payload 不超过 256 KiB**。
- 任一页准备失败必须发生在首字节前；第二页冲突不能留下第一页半提交。
- 首字节后只同步推进到不可失败安装与 fence release，`postFirstByteFailures == 0`；异步 GPU、一般 callback 和未证明的多页取消仍走既有安全路径。
- capture-before/handoff-before 两种次序均测试；读取 fence hold **P99 ≤100 μs**，压力、不同 BPP、边界 batch 均有足量样本。

出口：完整安全矩阵、allocator/rehash/大析构零工作、fence 尾延迟与吞吐控制门通过；不得按平均 memcpy 带宽放宽 8 页/256 KiB。

## 5. M8：业务 scope、剩余迁移与生命周期

- 一笔 undo transaction 内每页 first-change 一次，跨 dab 复用 pending；中间 display/save 通过真实 frozen version/last-use 决定下一段。
- 逐入口检查 brush、H/V/random iterator、packed/planar、alias/source producer、clone/default/history，统一进入同一 selector。
- 有界 multi-buffer、backpressure、慢 reader/retirement、长 history、多文档、swap pressure、drain/close 的峰值与进度形成完整证据。
- 对仍在源码中的 `beginCpuMutation()/enableCpuWrites()` 等旧包装按 caller 与寿命逐项决定退出；已不存在者不重复建立“待删除”任务。保留 FreshCow，不用无使用者占位 API 冒充能力完成。
- 生产删除、测试搬迁、必要新增协议分别统计；更新 69 manifest/ownership/census/调用图，43 静态候选不能批量认定为死代码。

## 6. 正式 BR1-PERF 与 BR1 完成

先按 39 §5.6–5.9 预注册 required buckets、M 容差、置信度至少 95%、独立配对、顺序平衡、停止规则和失败保留规则。覆盖 N/K/H、1/4/8/16 BPP、冷/暖、native/generic、真写/COW/default/alias、history/save、资源压力与完整退出。吞吐、固定-work 延迟和 P95/P99 分别测量，不能用五轮运行推导尾分位数。

既有操作时间出口保持：blank/default 与 resident read ≤ upstream 1.2×；无 history resident write ≤1.3×；first-write COW/undo 与两个 stress ≤1.5×。这些上限不能充当 M 的容差；M 同义管理不劣性、K/resident E 吞吐/延迟、结构零工作和容量/寿命必须独立通过。

可 handoff 桶需同时证明 before-image copy=0、new payload allocation=0、payload migration=0、retirement payload=0；必要 COW 桶每段每页至多一次。无源更新的 resident hit 不制造 generic heap request/global map/active-lease scan/tile-unlock commit；固定 K 的 commit 不退回 O(N) rebuild/export/sort。

最终只有当前提交的 correctness/property/fault、业务生命周期、硬预算/进度、M/K/E 性能、source/binary 身份与状态文档全部一致，才能把 BR1 从 BR1-PERF 改为完成，并按 31 开放 BR2 production 接线。当前未满足；不得靠归档历史或完成 M6/M7 直接改状态。
