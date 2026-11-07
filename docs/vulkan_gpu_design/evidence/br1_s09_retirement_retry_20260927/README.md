# S09：有界延迟重试与退出调度

本批落实 [04a 的 R6–R9](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md)，阶段状态只回写 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)。证据范围是 CPU 退休事件链的延迟维护扩展，不授予完整 S09/S10、M6/M7/M8 或 BR1-PERF 资格。

## 改动和边界

- 原回收 executor 增加惰性 deadline monitor；计时不占绘画/回收 worker，不依赖 GUI event loop。move/reset 取消真实排队节点，已经取出的回调仍靠消费者 incarnation 拒绝。
- 原 queue 增加 retry 分区，仍独占每条债务。每 store 最多一个延迟任务，1→2→4…→100 ms 退避，一次最多移入 32 条，失败追加到尾部。已订阅的 Pending operation 等事件，不重复 dispatch。
- 原分类及 orphan 在后台调用 provider 前复验 Debt 准入。orphan 只使用原 reservation；缺失额度不会由重试补造。成功终态在 worker 释放 owner lease 前归还 orphan reservation。
- 通知 gate 在 close 等 idle 前关闭派发；producer 原子记住早到事件，实际 queue/owner 复验仍在原 worker。close 接管所有分区；拒绝 close 后恢复。
- facade 析构停止自动唤醒/退避，防止慢批次与到期通知连续保活 owner；已 ready 的有限工作和活跃 capability 原寿命保留。析构不等待 provider，不冒充成功 close。
- idle、未来 deadline、实际 debt drained 分开观测。新增冷统计包括 delayed records、单任务状态、wake 次数、每 wake 最大记录数和下一退避间隔。

实际修改函数、联动终点和测试逐项见 [04a §8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md)。本批增量见 [incremental.patch](incremental.patch)，八个手工修改文件的前后身份见 [incremental-review.json](incremental-review.json)；另更新生成调用图与 baseline source inventory，不修改 ratchet ceilings。原有其他未提交改动均保留。

## 验证记录

`checks-01` 的完整 17 目标双架构矩阵为 5,586 passed，0 failed/skipped；四个第一版 allocator 探针通过。这属于 facade 退出补强前的冻结身份，只作保留的中间证据。

随后发现慢批次可让下一 deadline 在 worker 结束前派发，补充 `stopAutomaticWakeups` 和真实阻塞批次/已到期通知用例。`targeted-01` 两架构各 33 passed；`targeted-02` 两架构各 10 passed。所有编译、调用图及运行日志保留，未覆盖失败或把中间身份混用为最终资格。

最终 [checks-02/manifest.json](checks-02/manifest.json) 覆盖 **17 目标 × 2 架构，5,588 passed，0 failed/skipped**（各 2,794）。每架构较上一批增加 11 个 case。结构门 1,574 APIs / 15,457 edges / 15 callback registrations、21 manifest / 22 ownership / 16 census / 19 intrusion；6 项工具自测通过，ratchet 不变且未提高 ceilings。

最终 allocator 使用 `warm-02` / `joint-02` 标签，两架构分别各 96 / 31,080 个区间，allocations/bytes/frees 全零，正控制为 4。暖读各 98,304 次外层读取（含 nested 共 196,608 次 lock）；joint 的成功及两类竞争各 10,360。四个 probe 的 image 哈希均与最终矩阵一致。

- HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。
- 全源码补丁 SHA-256：`e1bb81df269cf9dd6416a59a6eb33613df2a96750e5aedec513a56ea55c7068d`。
- image dylib：`d49ae496e29172726bef19ce728e1a842a7a90da1da71ef7fece5aec1b4359df`。
- UI dylib：`f20fe2f83feab2784405119e7a2650d5c2fc2bc9c16765905c182f596e5d33bc`。

详见 [最终身份](checks-02/identity.json)、[累计源码补丁](checks-02/source.patch)、[结果汇总](result-summary.json)、[ratchet 校验](ratchet-check.json)。最终 dry-run 无待编译工作，结束时源码与二进制身份复验不变。构建和调用图各轮均通过；退出审查触发额外冻结，未将第一版结果挪作最终身份。

## 复现

在源码/工具输入冻结后生成调用图并通过 architecture baseline 校验，再执行本目录 `run_checks.py`（传未使用的目录名）。完整矩阵固定 `KIS_BR1_SEED=12345`、offscreen、17 个目标，依次运行 arm64/x86_64，记录 HEAD、全工作树补丁及新源码、构建/库/测试哈希。结尾要求源码不变且 ninja dry-run 无待编译工作。

`run_install_probe.py <arch> <唯一标签> <probe.cpp>` 分别运行本目录暖读和共同安装 probe；身份文件含编译/链接/执行命令、环境与 image dylib 哈希。暖读只测缓存已准备的 repin/read/unpin；共同安装只测 physical claim 至 metadata/retag/ledger/descriptor 消费，均不含准备、kernel、seal/root 或延后销毁。通知注册、派发、计时及退休路径不在零分配声明中。

## 继续实施

完整 last-use acknowledge、S10 可准入等待者、通知/节点/deadline 的真实元数据预算、取消后空 completion signal 的回收与冷分配故障仍未闭合。单 queue 的一个 deadline 上限不等于进程全局字节预算；1–100 ms 是维护策略，尚无 stroke 延迟资格。仍需压力/退出全矩阵、Fresh 2% 回退、真实 stroke/首 dab/pen-up，以及正式 BR1-PERF；本批未重新取得 Vulkan 或 TSAN 资格。
