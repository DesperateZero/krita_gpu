# S09：最后订阅取消后的 completion 存储清理

本批落实 [04a / R3、§9](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#9-r3-取消清理的代码与验收对应)。设计和阶段状态仅由 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)裁决；本证据绑定原 registry 的通知清理及实际 CPU close 消费，不授予完整 S09/S10、M6/M7/M8 或 BR1-PERF 资格。

## 问题、改法与终结责任

修复前，最后订阅取消只删除 signal 中的 callback，原 completion source 仍保存 Pending ticket 的空 signal，直到 ticket 终态。新增反例在两架构的前一版 image 上均失败：预期 `storageRecords == 0`，实际为 1。原 [ARM64 失败](counterexample-arm64.log)、[x86_64 失败](counterexample-x86_64.log)及 [二进制身份](counterexample-identity.json)完整保留，前一冻结源码/库身份见 [predecessor](predecessor-identity.json)。

- 原 registry `Private` 继续独占 ticket 状态和通知 map。signal 的不可变清理通知只保存其弱引用；取消期间临时取得原 Private，休眠订阅不保活 facade、PageStore 或 provider。facade 显式禁拷贝，没有第二份 completion 权威。
- `reset` 取出未派发 callback，释放 signal gate 后再请求清理。原 registry 以 registry→signal 顺序复验 exact state 和当前空状态；新订阅先到则保留，旧取消不能误删同一 ticket 的替换 signal。state 在复验期间保活，避免地址复用。
- 最后 readiness entry 删除后，将空查找表容量移到 registry gate 外释放；terminal 路径在任意外部 callback 前释放空表。取消释放空 state 后再析构 callback 捕获，捕获析构可重入 registry。已取出的 callback 不可撤回，取消不等待它完成，消费者仍须复验自己的 incarnation。
- 冷登记先准备真实 callback 节点，成功后才 noexcept 移入捕获；失败时局部 signal/subscription 活到 registry gate 释放后，空 map 容量也移到锁外。**此项完成代码责任审查，尚未取得完整 allocator 故障注入资格**，不外推为所有冷 caller 都可恢复。
- `readinessWaiters`、`readinessSignals`、`readinessCapacity` 为冷统计，分别是订阅数、通知记录数和查找槽数。容量归零不是字节预算；有消费者的 map 保留正常容量，terminal coverage 和其他通知元数据仍须独立硬计账。
- 原 queue 的 close 接管仍保存 Pending operation 和实际债务；取消通知不完成 ticket、不重派发 provider retire。原 operation 后来终态，close 才沿原 ledger 归还实际 payload。

七个手工修改文件见 [incremental.patch](incremental.patch)及 [前后身份](incremental-review.json)；生成 callgraph/source inventory 的变化另在累计源码补丁中记录。ownership 新增原 registry 的 `BR1-OWN-COMPLETION`，[ratchet](ratchet-check.json) 不变、ceilings 未放宽。函数→消费者→测试的对应表在指南 §9，剩余工作在 NEXT_EDITS 的 S09/S10。

## 验证与身份

`targeted-01` 是中间源码：两架构各 registry 29 passed、CPU close/physical-pin/retry 10 passed，零失败/跳过。随后补强锁外空存储终结、登记捕获保留及最后订阅/有 sibling 两种析构竞争；`build-02/03/04/05` 记录这些增量。最终资格只用下面完整矩阵与 `*-01` 五类 probe 的身份，不混用中间总数。

每架构新增 **9 个 registry case**：256 个仍 Pending ticket 反复订阅/取消；257 项集中创建后的取消及终态清空；捕获析构重入与重新订阅；取消先到、登记先到、并发三种次序各 128 次；最后订阅和有 sibling 的析构竞争各 128 次；终态 callback 阻塞期间查表/取消。原终态和已派发回调用例继续保留。CPU close 原两种 provider 用例增加断言：operation 仍 Pending 时，通知 waiters/signals/capacity 已归零，之后消费同一 operation 收敛真实资源。

最终 [checks-01/manifest.json](checks-01/manifest.json)：**17 目标 × 2 架构，5,714 passed，0 failed/skipped**（各 2,857）。结构门 1,619 APIs / 15,914 edges / 15 callbacks、21 manifest / 24 ownership / 16 census / 19 intrusion；6 项工具自测通过。最终 dry-run 无待编译工作，源文件和所有测试/库身份复验一致。

五类 allocator probe 均与矩阵使用同一 image dylib，每架构：

| Probe | 测量区间 | 数量 |
|---|---|---|
| `budget-01` | 16 实际等待者下，reservation release / 部分 commit / live release 各 32 | 96 |
| `root-01` | 16 活跃 root cursors 下 commit/restore 各 24，cursor 生命周期 24 | 72 |
| `legacy-01` | 原 physical/index/root/metadata/descriptor 和 restore 安装 | 28 |
| `warm-01` | 98,304 次外层暖读；含嵌套共 196,608 次 lock | 96 |
| `joint-01` | 共同生产 handoff 安装，成功及两类冲突各 10,360 | 31,080 |

全部区间 allocations/bytes/frees 为零，各 probe 正控制 allocations=4。冷订阅登记、取消、终态通知、monitor/worker 派发与 callback **不在零分配声明内**；其他准备/kernel/seal/root/deferred cleanup 排除范围沿用各探针定义。这些结果证明已测热区间没有新增 allocator 活动，不证明真实 stroke 延迟/吞吐，也不证明本批全部冷路径无分配。

- HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。
- 全源码补丁 SHA-256：`c560df68149c4adce83e27571a9569ef1c58447e278a9018f3708fbcb4c7309c`。
- image dylib：`ef5c496eeeba8af375932144855888115f8378f192b2f92389d9cfbdfd8e8a4d`。
- UI dylib：`f20fe2f83feab2784405119e7a2650d5c2fc2bc9c16765905c182f596e5d33bc`。

完整命令、环境、seed、文件哈希见 [identity](checks-01/identity.json)、[累计源码补丁](checks-01/source.patch)、[结果汇总](result-summary.json)。先冻结源码并生成 callgraph/architecture baseline，再运行 `run_checks.py <新目录名>`；`run_install_probe.py <arch> <新标签> <source.cpp>` 保存编译、链接、运行和哈希。脚本拒绝覆盖既有证据。

## 后续边界

上游 last-use acknowledge、存活通知/queue/deadline 的真实硬字节预算、共享全局额度、必要终结资源、前台 job continuation、结构化拒绝原因、冷分配/dispatch 故障及完整压力/退出仍须实施。空通知回收不能授权无限长 scope、删除 legacy idle 强引用或放松 pin/COW 条件。

S08 热点与销毁成本、S06.3 batch/idle/raw、完整 M6/M7/M8、undo/context 和正式 BR1-PERF 保持开放。未新增 Fresh 2% 回退、真实 stroke/首 dab/pen-up、Vulkan 或 TSAN 资格。
