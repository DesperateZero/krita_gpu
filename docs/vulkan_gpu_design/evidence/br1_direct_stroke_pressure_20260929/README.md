# BR1 BC9 首个资源与压力联合子范围，2026-09-29

本批只修改测试和活动文档，生产源码与生产 API 为 **+0/-0**。目标是把受限资源、慢读者、长 stroke、无新输入 drain、取消和 close 后资源归零接到已经成立的 direct persistent Freehand fixture，同时用较低预算留下结构化压力 continuation 的真实反例。该结果不授权扩大 `tool/strokes`。

## 通过的目标结果

`FreehandStrokeTest::testPersistentAutoBrushStrokePressure` 在 24 MiB TileDataStore 硬上限、soft/pool/swap 为零的配置下执行 1024×1024 Buildup direct autobrush。首段写入和显示 cut 后保留一个旧像素 reader；随后执行四组横纵长路径、第二次 update、旧值复验、reader 释放和三步递归必要后继。断言覆盖：

- 慢 reader 成功取得旧像素，长笔写入后旧值保持稳定，随后显式释放；
- 无外部新输入时，递归 producer 三步在 finish 前全部排空；
- finish 只有一次、没有 cancel；一次 undo 清除整笔，一次 redo 精确恢复；
- 采样的 TileDataStore resident 始终不超过 24 MiB，峰值至少达到上限的一半，fixture 退出后归零。

校准运行观察到 arm64 像素常驻峰值 15,237,120 B，x86_64 为 18,366,464 B。最终测试用相对下限断言，避免把实现固定到单一架构的页数量。

`testPersistentAutoBrushStrokePressureCancelled` 在 8 MiB 下复用原 500×500 取消控制，验证 finish 不发生、cancel 至少一次且退出后 resident 归零。它有意不把下述永久容量反例伪装成可恢复成功。

`KisPageStoreReferenceTest::tiles3BackendsShareProcessResidentLimit` 在 8 MiB 进程上限下验证：首个 backend 的 6 MiB current；慢读者保持被重写页的旧值并把旧 backing 计入 `RetainedHistory`；释放后 retained/debt live 和全部 reserved 归零；第二 backend 的超限批次原子拒绝且 changed 为空；两个 session close 后 TileDataStore resident 为零。

| 目标 | arm64 | x86_64 | 证明范围 |
|---|---:|---:|---|
| `FreehandStrokeTest testPersistentAutoBrushStrokePressure testPersistentAutoBrushStrokePressureCancelled` | 4 / 0 / 0 | 4 / 0 / 0 | 24 MiB direct 长 stroke、慢 reader、update/drain、undo/redo；8 MiB 原取消与退出归零 |
| `KisPageStoreReferenceTest tiles3BackendsShareProcessResidentLimit` | 3 / 0 / 0 | 3 / 0 / 0 | 8 MiB 共享进程额度、retained/release/reserved、超限原子拒绝和 close 归零 |

最终输出见 [Freehand arm64](freehand-arm64.log)、[Freehand x86_64](freehand-x86_64.log)、[PageStore arm64](pagestore-arm64.log)和 [PageStore x86_64](pagestore-x86_64.log)。构建目标仅为 `FreehandStrokeTest` 与 `KisPageStoreReferenceTest`，没有重跑历史全矩阵。

## 保留的压力反例与设计结论

同一长 stroke 改为 8 MiB 后失败，`slowReaderChecks` 为零，说明原 scheduler 在排队的 reader 释放 job 之前已经进入取消。临时只读诊断把 `KisPaintDeviceStrategy` 已有的局部错误字符串打印出来，观察到 PageStore metadata 容量拒绝；[失败日志](failure-arm64-8mib.log)中的诊断文字来自该临时打印。诊断 hunk 随即删除并重新构建，最终源码和通过日志均不包含它。另一次校准观察到 `metadata owning capacity budget is exhausted`，说明两种 metadata 容量边界都仍折叠到同一个布尔失败终点。

像素 operation 可能在多个页之间已经开始，因此不能在 UI 或 scheduler 中重放整个 dab。下一改动必须先在 PageStore/DataManager 形成永久容量拒绝、可等待压力和取消的结构化结果，并保证只有首字节前的原 job 输入进入 continuation；scheduler 只消费业务级结果。`tool/strokes`、paintop 和 painter 不持有 budget、reservation、waiter、page 或 session 身份。该要求已写入 [主干低耦合合同](../../br1_modification_guide/MAINLINE_INTRUSION_POLICY.md)和 [92 §16.18](../../92_br1_m6_m8_execution_baseline.md#direct-stroke-pressure-fixture)。

## 主干侵入账本与阶段裁决

生产文件、函数、字段、include、friend、锁、TLS 均新增 0；关闭状态成本不变。测试增加两个 Freehand case、一个可选硬上限 RAII、慢 reader/峰值探针，并扩展既有 PageStore 进程预算 fixture 的 retained/reserved/close 断言。最终源码与二进制身份见 [manifest](manifest.json)。

本批只关闭 BC9 的单文档受限预算成功、慢 reader 稳定、原 cancel 和 close 后资源归零子范围。结构化压力结果、首字节前 continuation、自动释放后的无输入恢复、多 store/多文档公平、完整资源收费、默认启用以及 M6–M8 仍开放。
