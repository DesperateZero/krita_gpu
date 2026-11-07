# S09：CPU 退休事件接线证据（2026-09-27）

执行入口：[92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:475)。函数级修改关系：[04a / R1–R10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md)。本批落实 CPU physical pin / completion 到现有退休队列的事件子集；完整 S09/S10、M6/M7/M8 与 BR1-PERF 仍未通过。

## 实际改动与责任边界

- binding 在同一 gate 内核对 exact identity、reader/writer 并登记冷订阅。最后 reader 或真正释放 writer 时派发；Reserved writer 仅 unpin 不派发，Handoff 状态拒绝登记，联合安装区间不引入通知。
- completion 检查与登记在 registry gate 内完成。已 terminal 返回 Ready；Pending 订阅在终态后派发。ledger 使用原 operation→ticket 映射，不为队列复制 operation 权威；Pending operation 继续只复验，不再次 dispatch provider retire。
- queue 采用稳定 list 节点和每次登记独立的弱等待身份；事件 O(1) 移动对应 pending 到 ready，沿原有最多 32 条的后台 pass 复验。登记前已就绪时允许一次立即重试，持续无信号拒绝仍保留 pending。
- producer 回调只向既有 reclaimer 派发，不在外层 provider gate 内进入 queue/owner。休眠订阅不强保活 store；实际派发时在弱通知上下文保护下，仅从非零引用取得临时 owner lease。queue 析构先使上下文失效。
- process/close 撤销原等待身份；close 拒绝后重新调度合格记录，晚通知不复活已接管记录。close 窗口中尚在登记的有效等待对象保留早到 notified 事实。`waitForIdle` 包含已派发通知，仍与 debt drained、session closed 分开。

仅允许原本已准入 RetirementDebt、且 provider 允许 backgroundRetirement 的记录进入新增事件路径。原分类/orphan reservation、终态成功后释放 backing charge 等协议保留。普通暖读没有通知对象分配；等待路径新增的冷元数据尚未取得完整 S10 预算资格。

## 冻结身份

| 项目 | 身份 |
|---|---|
| HEAD | `5173c807c87bb1619325249a07a8b4f4f8f09f09` 加本目录冻结工作树补丁 |
| source.patch SHA-256 | `1178eeb58df05e80d0d20d31fc98f510d1743f30110b30fbfa67de7bda355d09` |
| image dylib SHA-256 | `5d7046f5cbcfb9045a64fb7c36532d3b9e01d87a2a34d9ab136b0cbaa7ab3db8` |
| UI dylib SHA-256 | `f20fe2f83feab2784405119e7a2650d5c2fc2bc9c16765905c182f596e5d33bc` |

[完整身份](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/checks-01/identity.json)包含编译配置、17 个 binary 和库哈希；[源码补丁](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/checks-01/source.patch)同时包含尚未跟踪的 readiness、已有 stroke failure 和 UI fixture 源文件。源码、binary 及四个探针的 image 身份已在结果汇总时重新核对；没有借用旧 image 的探针结论。

[增量补丁](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/incremental.patch)和[逐文件哈希](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/incremental-review.json)覆盖本批 15 个实际改动文件，含 ownership 更新。全工作树冻结补丁与本批增量分别使用，不把此前已验证的累计修改当成本批新增。

## 验证结果

| 验证 | arm64 | x86_64 |
|---|---:|---:|
| 17 目标 CPU/业务矩阵 | 2,783 passed；0 failed/skipped | 2,783 passed；0 failed/skipped |
| 暖 tile read allocator | 96 区间；98,304 次外层读；allocations/bytes/frees 全零 | 同左 |
| 生产联合 install allocator | 31,080 区间；allocations/bytes/frees 全零 | 同左 |
| allocator 正控制 | 每种探针 4 次 allocation | 同左 |

完整矩阵共 **5,566 passed，0 failed/skipped**。[运行 manifest](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/checks-01/manifest.json)保存命令、时间、返回值和各日志；[结果汇总](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/result-summary.json)保存分架构与探针统计。

相对上一冻结矩阵，每架构新增 42 个 case：registry 9 个、physical readiness 24 个、CPU mutation 9 个增量（含原 pin 测试扩展 generic provider lease）。覆盖登记与 terminal 竞争、成功/失败/取消、move/reset、已派发回调、reader/Active/Reserved/revoke、登记前释放、延迟退休 completion、close 拒绝重挂，以及休眠/已派发通知下的直接 store 析构。queue 用例通过真实 PageStore/provider，并在释放后不再编辑、不调用 `processRetirements`；直接析构后检查 provider 弱引用可过期，不把这等同于 TSAN 资格。

结构门及 6 项工具自测通过：**1,557 APIs / 15,364 reverse-call edges，21 manifest / 22 ownership facts / 16 census groups / 19 intrusion files**。[ratchet 对照](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/ratchet-check.json)确认完全不变，reviewed ceilings 未提高。

暖读探针复用 S06 第九批的相同 harness，覆盖 1/4/8/16 BPP、初建读缓存/独立写后缓存/refresh 后缓存及嵌套读；196,608 次 read lock 含嵌套。联合安装覆盖成功、physical claim 拒绝、metadata revision 竞争各 10,360 区间。暖读区间不含初始化、写入/refresh、swap-in、发布或销毁；联合安装不含 preparation、像素 kernel、adapter 返回、seal/root 或 deferred cleanup。等待对象登记、事件派发与退休工作不在这些零分配区间内。

## 复现与保留的失败

```sh
cd /Users/apple/krita_gpu/krita
python3 ../docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/run_checks.py checks-next
python3 ../docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/run_install_probe.py arm64 warm-next warm-tile-read-allocation-probe.cpp
python3 ../docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/run_install_probe.py x86_64 warm-next warm-tile-read-allocation-probe.cpp
python3 ../docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/run_install_probe.py arm64 joint-next joint-install-allocation-probe.cpp
python3 ../docs/vulkan_gpu_design/evidence/br1_s09_retirement_wakeup_20260927/run_install_probe.py x86_64 joint-next joint-install-allocation-probe.cpp
```

更改代码后先重新生成源码绑定调用图并通过结构门；复现须使用新目录/标签，不覆盖已冻结证据。

- `build-01` 生产接线编译成功；`build-02` 新 fixture 使用了错误的 `pin` / `allocationGeneration` 名称，改为真实 `pinResident` / `allocation.generation` 后 `build-03` 成功。
- `build-04` generic fixture 错用 `cpuData`，改为真实 `cpuReadData` 后 `build-05` 成功。未改变生产权限来迁就 fixture。
- `callgraph-01` 正确拒绝索引期间的源码变化；收束代码后 `callgraph-02` 成功。随后结构基线刷新、完整矩阵和探针均使用冻结源码。
- targeted-01 为 51 passed，targeted-02 的扩展 CPU 子集为 15 passed；这些局部结果由完整 checks-01 覆盖。原始编译/工具失败日志保留，没有任何失败测试被跳过或记为通过。

## 剩余出口

无信号或反复瞬时拒绝的可取消退避、非 Debt/orphan 准入进度、完整上游 last-use acknowledge、S10 可准入等待者仍未接通。取消后的空 completion signal 可能留到 ticket terminal；其存储回收/硬上界、全部新增冷元数据计账及分配故障责任仍须闭合。M6 的其余 legacy/batch/raw 生命周期、故障/epoch 资格，M7，M8 的持久 stroke scope、undo/context 和正式 BR1-PERF 继续实施。本批不新增 Vulkan、TSAN、Fresh 2% 回退或真实 stroke 时间/吞吐资格。
