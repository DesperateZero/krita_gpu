# BR1 产品 PageStore 非载荷共享父额度，2026-09-29

本批交付 S10 的一个可独立判定子范围：同时存活的产品 PageStore 共享 metadata/default-cache CPU 总额，父子注册控制节点也实际收费，空闲注册项不压缩活跃 store，并在真实释放/析构后返还容量。阶段权威仍是 [92 §16.22](../../92_br1_m6_m8_execution_baseline.md#shared-nonpayload-budget)；本结果不授予完整 S10、BC9 或 M6–M8 资格。

## 实现与边界

- 每个 store 保留原本地 controller、`MetadataArena` / `OptionalCache` 分类和诊断；父 controller 把两类合并为一个非载荷总额。
- 父 reserve 先于本地 reserve；本地拒绝自动释放父 reservation。commit、retained reservation、cancel 与 live free 同时更新两层，但不同时持有两层 mutex。
- 父子注册表使用父 controller 的 budget allocator。节点在父 gate 外准备、无分配安装，注销后在 gate 外释放；1 B 父额拒绝注册且 live/reserved 回到零。
- live 产品 backend 通过弱持有池共享同一个父 controller。活动 store 存在时改变产品内存配置会拒绝；最后一个 store 析构后父池可重建。
- tile payload 继续只由 `KisTileDataStore` 进程级 resident admission 收费，不在非载荷父层重复计费。
- 父额采用 work-conserving 准入：注册是 topology，不是 demand；空闲注册项不静态分额，活跃 store 可借用全部剩余容量。曾实现的注册数静态 (1/N) 分额会把单图像投影/辅助 backend 当成竞争文档，已删除。
- 共享父层没有异步 waiter；metadata/default-cache 压力继续返回现有失败。具有原请求 owner 的跨 store 公平、自动 scheduler continuation和剩余通知/派发/终结存储收费仍开放。

生产改动限于 PageStore/write coordinator/backend 五个内部文件。PageStore 增加一个 private friend 配置桥；budget controller 增加内部父预算组合和 allocator-aware child registry；backend 增加内部弱持有父池。UI/tool/paintop/painter/PaintDevice/scheduler、public/protected 产品 API、字段、friend、TLS 和外部侵入文件均无增长。测试扩展一个 controller 结果用例、既有双 backend 共享断言，并用既有真实 Freehand 压力 fixture 复验。

## 目标验证

构建命令和 no-op 结果见 [build.log](build.log)。arm64 运行：

```text
KisPageStoreReferenceTest sharedNonPayloadBudgetBoundsStoresAndReleases tiles3BackendsShareProcessResidentLimit
FreehandStrokeTest testPersistentAutoBrushStrokePressure testPersistentAutoBrushStrokePressureCancelled
```

[测试日志](tests-arm64.log)为两个目标程序合计 **8 passed / 0 failed / 0 skipped**。controller 用例验证 1 B 注册失败退费，以及 1024 B 父额跨两个 controller 的 metadata/cache/注册控制合并拒绝、精确剩余准入、释放后借满、child 析构退费和最终 live=0；产品用例验证真实双 backend、8 MiB tile resident、24 MiB 非载荷共享上限、慢 reader/history、第二 store 原子拒绝与 close 清零。真实 Freehand 保持 24 MiB tile hard limit、pool/swap 为零，完成长 stroke、慢 reader、两次 update、递归 drain、undo/redo、取消和退出归零；没有提高预算。

[结构门](architecture.log)通过：21 manifest entries、25 ownership facts、16 runtime census groups、1,826 indexed APIs、19,821 reverse-call edges、17 callback registrations、19 frozen external intrusion files。`git diff --check` 见 [diff-check.log]，源码 HEAD 和目标文件的 SHA-256 分别见 [head.txt](head.txt)与[source-sha256.txt](source-sha256.txt)。

## 后续领取

下一段先在 PageStore 内补齐 notification/dispatch/retry/pass、必要终结和其他尚未计账控制存储，再把跨 store 无饥饿次序与原 job ownership transfer 同批设计。禁止按注册 backend 数静态分额，也不保存无 owner 的永久 pending-child 标志。真实多文档并发长 stroke、慢 reader/retirement、取消和退出归零是公平完成证据；没有原 job ownership transfer 和实际 consumer 前，不增加 pressure 枚举或上层重试 API。
