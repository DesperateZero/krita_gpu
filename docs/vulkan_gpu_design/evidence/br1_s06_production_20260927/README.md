# S06：驻留 CPU exact before 的生产 recoverable 计划

本批将已有 handoff 原语接入真实 PageStore 的 native/generic 首写入口。状态裁决仍只在 [92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:475)；逐函数修改关系见 [03a §11](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md:149)。M6/M7/M8 及性能资格未完成。

## 实现与证据身份

- 基础 HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`，加 [完整工作树补丁](checks-01/source.patch)，SHA-256 `223665aa6c4d516bcf27c8e99d67fc182131a06bdca452ceb7db1386191807f1`。包含尚未进入 Git index 的既有三个源文件；不是已提交 revision。
- image 库 SHA-256：`a529df6b942d1ecd016b4bbc0b23bfb1b03f6f2051477410c509210c4a2eb517`；UI 库、34 个测试进程的二进制与环境见 [identity](checks-01/identity.json) 和 [manifest](checks-01/manifest.json)。矩阵后源码与 frozen patch 一致。
- 相对上一批的九文件 [增量补丁](production-implementation.patch) 及 [重建核对](incremental-review.json)：每个修改前文件均从 HEAD 加上一批 terminal 完整补丁重建并比对，全部一致。生成的调用图、baseline 单独由完整补丁保存。
- [结构门](checks-01/architecture.log)：1,522 APIs、14,985 reverse-call edges、21 manifest entries、22 ownership facts、16 census groups、19 intrusion files；[调用图](callgraph-01.log) 的 physical reservation production/test callers 为 1/10。[ratchet](ratchet-check.json) 原始限制未变，六项工具自测通过。

## 实际改动

1. 共同 `prepareWritePlanLocked` 消费原 base snapshot 的 CPU alternate 候选；锁外取得 B 的 resident-only pin，准备 physical、ledger、metadata，回到 owner gate 准备真实 descriptor nodes。physical claim 与 strict metadata install 成功后，连续消费 retag、计账和 descriptor，随后才交付 writer。
2. native 预备原 session page 终结存储，generic 预备原 request/activity/page claim；复用同一计划、source=B、target=T 和原提交/取消链。拒绝前未改状态时保留 Fresh。discard 无完整输入保留默认像素初始化；完整 payload 不先填默认。
3. 初始 manifest 可以导入调用者已持有的 exact alternates，校验完整身份和预算；失败撤销本次登记。它不在写入时复制 before，不提供运行中的副本生产，也不开放 BR3。
4. 同一 provider 登记多个 owner 后，物理 handoff 保守拒绝；短 claim 期间拒绝新的 owner 注册，释放后可重试。gate 只保护注册排斥，不包住普通 provider 操作；不同 allocation 可同时持 claim。该 eligibility 不是新 generation authority，也未证明跨 Store 共享同 handle 的完整退休寿命。

共同计划只接受驻留 CPU B，当前只尝试首个合格候选。provider identity、额外引用、pin、last-use、transient 限额等证明不足时，仍选择安全 Fresh 或明确资源拒绝。候选、B pin 和 deferred cleanup 在 owner gate 外释放。

## 验证结果与范围

[最终汇总](result-summary.json)：**17 目标 × 2 架构，5,138 passed，0 failed / skipped**；arm64 与 x86_64 各 2,569。

新增每架构 164 个 CPU mutation 场景：20 个初始导入拒绝/重试、80 个真实生产 handoff、64 个安全 fallback。覆盖 1/4/8/16 BPP，native preserve/payload/discard 与 generic preserve/discard，commit/cancel/abort/undo-redo；拒绝 Fresh payload allocation 的正例仍完成，验证同地址、allocation generation 加一、旧 A 失效、T 可写、旧 View 经 B 读取。关闭后 payload live 与全部 reservations 归零；metadata arena 随仍存活的 Store 持有，直到 Store 析构，不要求 close 提前析构它。

PhysicalClaimTest 新增两个 owner 注册次序场景，全目标每架构 343 项通过；CpuMutationTest 全目标每架构 747 项通过。定向最终记录为 [production-04](arm64-production-04.log) 和 [physical-02](arm64-physical-02.log)，分别 166 与 343 passed，包含 fixture init/cleanup。

[allocator 汇总](allocator-summary.json)：八组探针使用与矩阵相同 image 库，正控制有效；每架构 ledger/physical/metadata/legacy 分别测得 144/48/32/28 个零 allocations/bytes/frees 区间。这些是各原语的独立安装/取消区间，**尚未直接测量 `prepareWritePlanLocked` 的整个联合安装区间**，不能合并外推为生产 M6 零分配资格。

## 保留的失败与修正

| 原记录 | 结果与原因 | 最终修正 |
|---|---|---|
| [build-01](build-01.log) | Qt 6 `QMutexLocker` 缺少模板参数 | 显式使用 `QMutexLocker<QMutex>` |
| [build-03](build-03.log) | fixture 对 move-only lease 赋值 | 使用 optional emplacement |
| [production-01](arm64-production-01.log) | 58 passed / 48 failed；正例操作成功，close 后错误要求 metadata arena 立即归零 | 区分 payload/reservation 与仍由 Store 持有的 arena 生命周期；不放宽 payload 释放 |
| [production-03](arm64-production-03.log) | 146 passed / 20 failed；初始 import fixture 在 operational 前调用 `resolveSurfaceState` | 用 fixture 保存的初始 descriptor 验证 |
| [physical-01](arm64-physical-01.log)、[挂起堆栈](physical-hang-01.txt) | claim 跨期持普通 provider mutex，随后同线程 `resolveAccess` 再取锁而挂起；确认后终止，exit 143 | 改为仅保护注册的短 admission/count gate；普通 provider resolve 不持该 gate |

build-02/04/05/06/07/08 和 production-02 也原样保留。最终 build-08 后生成调用图、刷新 baseline，再执行完整 checks-01；没有以定向成功替换完整矩阵，也未删除早期失败。

## 后续修改指南

M6 下一步仍需 legacy cache expected identity/重解析、整个联合安装的 allocator 区间、各准备失败点及完整 epoch/晚 completion/并发双次序、S09/S10 资源与关闭进度。SSD/nonresident/archive before 未接入；多 owner 与首候选选择保守。M7 的 admission/fence/全部页首字节前准备、M8 持久 stroke scope、剩余 caller 迁移及 undo/context 工作继续按指南推进。

本批未重新取证 Fresh 2% 回退、真实 brush replay、首 dab/抬笔尾延迟、Vulkan、TSAN 或 BR1-PERF。正确性测试与 primitive allocator 探针不授予这些资格。
