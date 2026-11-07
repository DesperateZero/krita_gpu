# S10：局部预算等待、实际授额与退休消费

本批落实 [04b / W1–W8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04b_budget_waiter_implementation_map.md)，阶段状态只由 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)裁决。该范围是局部 budget controller 的等待协议及原 CPU 退休队列消费，不授予完整 S10/S09、M6/M7/M8 或 BR1-PERF 资格。

## 改动与边界

- 原 reclaimer 增加冷准备的 reusable wake：登记时分配 monitor 节点，生产者 notify 只 splice 已有节点和 signal；不在 release/commit 内分配、执行 callback 或析构捕获。monitor 将 ready wake 与已到期 deadline 轮转；每 controller 合并一个 worker 作业，仍使用原单 worker。
- 原 budget controller 保存最多 32 个 Waiting+Granted 请求及 FIFO identity，准备原 reservation slot/free-list 存储。请求保留 per-class/domain 目的需求、净 aggregate 与净 durable 增长；立即 reserveChange 与等待路径共用计算。超过空载容量、槽满或冷准备失败不登记。
- 资源归还只发合并信号，后台在 controller gate 内授予**真实 reserved 额度**，然后在 budget/lifetime gates 外通知。早到的大需求不被重叠的小需求或普通同步 reserve 绕过，不相关资源可继续。Granted 由 move-only waiter 一次 take；取消归还空 slot 或已授额度。
- 原 ledger 从真实 physical/class records 投影退休需求，原 queue 继续独占债务。通知将 grant 转入原 record，ledger 再核验 exact identity、物理域、alias/class claim 后消费，再调用 provider。失配归还 grant 并重试；orphan 不借此补造原来缺失的 reservation。
- close/stop 取消等待身份；controller 析构使剩余 handles 失效，context 不保活 store。晚 callback 仍由消费者的弱 incarnation 拒绝。私有 queue 头仅导出原有冷方法供集成测试使用，没有新增队列或 authority。
- 冷统计分别报告 waiting、granted、累计 grants/cancellations。32-request 上限限制对象数量，**尚不代表所有等待/context/slot/monitor 元数据已计入共享硬字节预算**。

十二个手工修改文件见 [incremental.patch](incremental.patch)、[前后身份](incremental-review.json)，另更新生成 callgraph/source inventory。所有其他未提交文件保持原状；[ratchet](ratchet-check.json) 不变，未提高 ceilings。ownership 增加原 controller 的 admission 事实，划清 executor 只调度、ledger 决定真实物理分类的责任。

## 验证与失败保留

每架构新增 23 个 case：FIFO 与独立资源、32 slots/move/reset/复用/controller 先析构、SSD 满载同实物换分类、部分 commit 释放未用额度、预备 wake 取消/复用；授额前取消与 callback 已取出后的取消/销毁；实际 ledger+queue+provider 的 20/40 页 × 四种 BPP × 自主进度/close。集成 fixture 直接消费原生产队列，不把单独 budget 单测写成全应用压力资格。

`build-02` 保留私有 queue 方法未导出的链接失败；增加原冷方法的符号可见性后 `build-03/04` 通过。`targeted-01` 两架构各 32 passed，`targeted-02` 各 21 passed，均 0 failed/skipped；第二轮补退出交错，没有删减失败条件。ARM64 `budget` 及首轮 `budget-final/root/legacy/warm/joint` 为中间身份；本次重新冻结后，最终统一使用带 `-02` 的五类探针。

首次完整 [checks-01](checks-01/manifest.json) 为 **5,695 passed / 1 failed**；ARM64 `testMutatedJobs` 的共享日志出现空项，原失败保留。修复前两架构各 100 次隔离运行均成功，不能声称已隔离复现。原夹具多个 worker 并发追加同一 QStringList，先在 `scheduler_utils.h` 的记录入口加互斥；`build-05` 后的 [scheduler-race-after](scheduler-race-after.json) 又记录 ARM64 1/100 失败，x86_64 0/100：这次是实际执行 3 项而断言只允许 2 项。

进一步核对生产 scheduler 可在同一次 dispatch pass 中复用刚释放的 worker slot，原测试错误地把双 worker 上限当成两项 batch 上限。因此在 `testMutatedJobs` 的测试 strategy 内增加 semaphore 完成屏障：先让两个真实 worker 都进入，再由测试释放；保持原顺序/数量断言，未串行化生产调度、添加 sleep 或放松期望。`build-06` 后的 [scheduler-race-after-02](scheduler-race-after-02.json) 两架构各 100 次通过，随后重新生成调用图、冻结源码并运行下面的完整矩阵。该结果不授予 TSAN 或全应用无竞态资格。

最终 [checks-02/manifest.json](checks-02/manifest.json)：**17 目标 × 2 架构，5,696 passed，0 failed/skipped**（各 2,848）。结构门 1,612 APIs / 15,830 edges / 15 callbacks，21 manifest / 23 ownership / 16 census / 19 intrusion；6 项工具自测通过。最终 dry-run 无待编译工作，源码和库/测试身份复验一致。

最终五类 allocator probe 均与矩阵使用同一 image dylib，每架构：

| Probe | 真实测量边界 | 区间数 |
|---|---|---|
| `budget-02` | 16 个实际等待者存在时，reservation release、部分 commit、live release 各 32 次 | 96 |
| `root-02` | 16 活跃 root cursors 下 commit/restore 各 24；cursor 完整生命周期 24 | 72 |
| `legacy-02` | exact/physical index、root/metadata/descriptor、restore additions | 28 |
| `warm-02` | 98,304 次外层暖读；含 nested 共 196,608 次 lock | 96 |
| `joint-02` | 共同生产 handoff 安装，成功及两类冲突各 10,360 | 31,080 |

全部区间 **allocations/bytes/frees 为零**，每个 probe 正控制 allocations=4。预算探针只对实际生产者线程的 commit/release 区间作此声明，冷等待注册、monitor 派发、worker/grant callback 和清理在区间外；后台仍可能分配。原 warm/joint/root/legacy 的准备、kernel、swap、seal/root 或 deferred cleanup 排除范围分别沿用原证据，不把这些 allocator 结果当作 stroke 耗时资格。

- HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。
- 全源码补丁 SHA-256：`26ac3c6d8632780afad8d2916227af28375a20f0288a8e57ed13ee5f4bcd365e`。
- image dylib：`3705df42e127c7481e75f2759b402ba9ddb8aef7ddbd031ecddf6312f61cb5fa`。
- UI dylib：`f20fe2f83feab2784405119e7a2650d5c2fc2bc9c16765905c182f596e5d33bc`。

完整记录见 [identity](checks-02/identity.json)、[累计源码补丁](checks-02/source.patch)、[结果汇总](result-summary.json)。先冻结源码并生成 callgraph/architecture baseline，再用 `run_checks.py <新目录名>` 运行矩阵；`run_install_probe.py <arch> <新标签> <source.cpp>` 保存编译/链接/执行命令和哈希。脚本拒绝覆盖已有证据。

## 继续实施

共享全局额度、context/slot/callback/monitor 的真实元数据收费、必要终结空间、前台 job 的首字节前 admission continuation、结构化拒绝理由和 dispatch 分配失败处理尚未闭合。跨 store 压力、长时间未取 grant 与完整退出/故障矩阵仍须验收；固定数量及局部 FIFO 不证明全局容量或时间上限。

S08 的持续热点/销毁预算、S09 上游 last-use acknowledge 与取消后 completion signal 回收、legacy batch/idle 迁移、persistent stroke scope、完整 M6/M7/M8、undo/context 继续按 92 推进。未新增 Fresh 2% 回退、真实 stroke/首 dab/pen-up、Vulkan、TSAN 或正式 BR1-PERF 资格。
