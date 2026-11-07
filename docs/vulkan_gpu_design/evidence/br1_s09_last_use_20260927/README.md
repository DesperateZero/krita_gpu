# S09：上游 last-use 的自动确认与退休接线

本批落实 [04a §10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#10-上游-last-use-到实际退休的代码与验收对应)。设计及阶段状态仅由 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)裁决。范围是**成功 ReleaseRead 后**的 CPU last-use 正常终态链，以及其原 close/析构消费者；不授予完整 S09/S10/M6/M7/M8、冷故障恢复或 stroke 性能资格。

## 问题与改动

原退休队列只能处理已经 detach 的物理记录。上游 metadata 的 pending last-use 必须等外部显式 acknowledge；仅完成 registry ticket、且不再编辑时，旧 payload 仍被保留。去掉原集成用例中的显式 acknowledge 后，两架构均记录 `pendingLastUses` 实际 1、预期 0 的失败。原 [ARM64](counterexample-arm64.log)、[x86_64](counterexample-x86_64.log)日志、[反例二进制](counterexample-identity.json)和 [前一冻结身份](predecessor-identity.json)保留；反例 image 与前一冻结 image 相同。

1. 原 `ActiveReadRecord` 在成功 metadata ReleaseRead 后继续持有 exact replica、lease ID 与 ticket，直到真实保护解除；移除原 pending-last-use replica vector，仅保留冷数量统计。原 lease map 继续拥有记录，ready 链只承载其调度关系。
2. 只在有 last-use 且允许后台退休时冷准备通知上下文和可复用 wake。订阅回调链接已存在的记录并 notify，不进入 Store/metadata/provider gate；monitor 在 owner 引用仍非零时借用临时寿命，向原回收 worker 合并一个作业。每 pass 最多处理 32 条，余项让出 worker 后继续，不扫描全部 lease map。
3. worker 以原 lease ID 与记录 identity 复验，再从 registry 取得真实 terminal evidence；metadata 解除保护后仍经原 history collector、retirement queue 和 ledger。未完成 ticket 不被清理；失败/取消的 terminal 只证明 consumer 已结束，不伪造 provider 退休成功。
4. 同 ticket 可覆盖同一 replica 的多次读。metadata 会一次移除其全部保护，剩余原读记录通过 `queryLastUsePending` 查询 exact metadata 状态收敛；不导出整页、不新建 ack 权威、不改变状态机的 stale transition 拒绝契约。
5. close 先关闭通知准入并注销订阅，锁外等待即时作业；随后主动确认原 terminal 记录。close 被活跃能力拒绝后重挂，facade 析构停止新唤醒。休眠通知不持 Store 强引用；已经取出的通知仍按原记录 identity 拒绝过期消费。`waitForRetirementIdle` 先等 last-use 作业，再等 history 和实际退休。
6. 无后台能力时保留显式 acknowledge。自动与显式消费竞争时，只有先消费者返回首次匹配成功；业务测试核对真实 pending 保护已经解除。冷统计加入 acknowledge passes、单 pass 最大记录数和 dispatch failures。

[八文件增量](incremental.patch)及 [前后哈希](incremental-review.json)涵盖 ReadCoordinator、metadata exact 查询、Store 生命周期、冷统计、CPU 集成测试和原 ownership fact。生成 callgraph/source inventory 单独记录于累计源码补丁，未放宽 [ratchet](ratchet-check.json)。`BR1-OWN-READ-COORDINATION` 继续属于原 read coordinator；metadata 保护仍由 metadata 写入，executor 不决定资格。

## 测试与构建身份

`build-counterexample` 及两份失败日志保留；`build-01/02` 是实施中间版本。定向 [targeted-01](targeted-01.json) 两架构各 **337 passed，零失败/跳过**，覆盖新增路径及原 handoff fallback/并发/overlay 消费者。之后补强 exact metadata 查询的失败关闭分支，`build-03` 后重新生成审计并冻结完整验证。

每架构新增 **42 个 case**：四种 BPP × Succeeded/Failed/Cancelled × 三种完成次序共 36；129 条独立/共享 ticket 的 burst 两种；排队事件 close、Pending 析构、排队事件析构三种；无后台能力的显式兼容一种。原 `lastUseDefersBackgroundHistory` 改为无显式 acknowledge，并保留 close 先拒绝后恢复的验证。两种 burst 均至少 5 个 pass、每 pass ≤32；实际旧 payload 收敛，当前像素保持正确。数量界限不证明 metadata 内部节点销毁或锁时间上限。

最终 [checks-01/manifest.json](checks-01/manifest.json)：**17 目标 × 2 架构，5,798 passed，0 failed/skipped**（各 2,899）。结构门 1,631 APIs / 16,026 edges / 15 callbacks、21 manifest / 24 ownership / 16 census / 19 intrusion；6 项工具自测通过。最终 dry-run 无待编译工作；源文件、库和所有测试身份复验一致。

五类 allocator probe 与矩阵使用同一最终 image，每架构：

| Probe | 指定测量区间数 |
|---|---:|
| budget-01：16 实际等待者下 release/部分 commit/live release | 96 |
| root-01：16 活跃 cursor 下 commit/restore 及 cursor 生命周期 | 72 |
| legacy-01：原 index/metadata/descriptor/root 安装 | 28 |
| warm-01：98,304 次外层暖读，含嵌套 196,608 次 lock | 96 |
| joint-01：生产 handoff 安装，成功/两类冲突各 10,360 | 31,080 |

全部区间 allocations/bytes/frees 为零，各正控制 allocations=4。**新 last-use 的登记、通知、acknowledge、close 及 worker/monitor 工作不在这些零分配声明内。** 各原探针的准备、kernel、seal/root/deferred cleanup 排除范围不变，不能据此声称真实 stroke 吞吐/延迟通过。

- HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。
- 累计源码补丁 SHA-256：`1d349dfed9720bc4dcc9970f33a6df5be174960d450e57e0a7eaf0ce964d07b0`。
- image dylib：`6a69b0dc47afabb5b9e42a3c6004219690f977d5a2eb57536b1258d6870892e2`。
- UI dylib：`f20fe2f83feab2784405119e7a2650d5c2fc2bc9c16765905c182f596e5d33bc`。

完整命令、环境、seed 与哈希见 [identity](checks-01/identity.json)、[source.patch](checks-01/source.patch)、[结果汇总](result-summary.json)。按冻结源码生成 graph/architecture baseline，再用 `run_checks.py <新目录名>`；探针使用 `run_install_probe.py <arch> <新标签> <source.cpp>`。既有证据不覆盖。

## 仍需落实的完整出口

metadata ReleaseRead **本身拒绝**时，原记录仍在 release-retry 链，自动订阅尚未建立。订阅冷准备、dispatch 分配失败或 metadata acknowledge 拒绝均保留原记录/真实保护，已有显式 acknowledge 或 close 可继续，但尚无完整自主压力恢复保证；不能将 catch 后留债冒称资源问题已解决。

ActiveReadRecord、ready 链、subscription 和 wake 的真实存活字节预算、必要终结空间、多 store 公平性与故障矩阵继续由 S09/S10 闭合。32 条/pass 不等于字节/耗时上限，未启用无限长 stroke scope，也未移除 legacy idle 强引用。

S08 热点/销毁、S06.3 batch/idle/raw、完整 M6/M7/M8、undo/context 和 BR1-PERF 仍开放；未新增 Fresh 2% 回退、真实 stroke/首 dab/pen-up、Vulkan 或 TSAN 资格。
