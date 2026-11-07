# S08：后台 root 枚举的有界切片

本批落实 [04 / G1–G7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04_reclamation_and_budgets.md) 的有界枚举子集，阶段结论只回写 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)。完整 S08、S09/S10、M6/M7/M8 和 BR1-PERF 继续开放。

## 改动与责任

- 原 epoch root records 保存保护枚举链接；current、retained count、transaction base count 仍是唯一保护权威。最多 16 个固定 value cursors，cookie 防止晚取消命中复用 slot。游标不保活 H 个 roots、不保存跨锁 QHash iterator。
- 每次开始先计入 current 的完整版本身份，再续扫原有限边界。释放最后保护时在原 epoch gate 调整受影响游标，随后允许实际 root 记录销毁；无关页面的后续发布不会无限延长扫描。
- commit/restore 比较最多 16 个活跃 key 的前后完整版本身份；仅改变的 key 失效。defaultPixelRevision 属于身份，不能只比 generation。此逻辑仍在原安装链，未引入新 retention 或 publication owner。
- 原 collector 每页保存最多 32 个候选及 live 位图；整个 worker pass 最多 32 次 root 访问，包括各候选组开始时的 current。最多 16 页共享额度；不完整或失效时不 detach。
- 完整扫描后持原 store owner gate 重新读取 exact candidate 的 metadata，确认 Historical、pin/last-use 等状态，再走原 owner transition；物理退休仍在锁外由原队列负责。clear/destructor 终结所有游标。
- 冷统计区分候选组 refresh、实际 root visits、单轮最大 root visits 和失效重启次数。一个 root 可因不同候选组或重启再次访问，计数不等于全局去重 root 数或耗时。

九个手工修改文件的增量与前后身份见 [incremental.patch](incremental.patch)、[incremental-review.json](incremental-review.json)。另外更新生成调用图与 source inventory；没有提高 ratchet ceilings，也没有处理其他未提交文件。

## 验证与失败保留

新增每架构 31 个 case：ReferenceTest 19 个、CpuMutationTest 12 个。覆盖 H=0/1/33/97 下移除 next/last/all 保护、真实擦除及异页发布；slot 复用/晚取消；同页 commit/restore 与 default revision 的失效；8 页共享上限；四种 BPP 下真实 worker 扫到一半时同页/异页发布、旧 View 内容保持、保护释放后 payload 收敛。既有长历史及退休 backlog 用例继续运行，refresh 断言调整为候选组口径。

`targeted-01` 两架构各 60 passed；`targeted-02` ReferenceTest 各 20 passed / 1 failed，CpuMutationTest 各 22 passed。该失败来自新增默认值测试误用 ordinary replica proof，未通过 `model.prepare`；修正为真实 surface metadata change，并补旧游标失效断言，没有放松生产比较。所有失败、构建和中间探针日志保留。最终 `targeted-03` 两架构各 59 passed，0 failed/skipped。

最终 [checks-01/manifest.json](checks-01/manifest.json)：**17 目标 × 2 架构，5,650 passed，0 failed/skipped**（各 2,825）。结构门为 1,580 APIs / 15,610 edges / 15 callbacks，21 manifest / 22 ownership / 16 census / 19 intrusion；6 项工具自测通过。[ratchet](ratchet-check.json) 不变，最终 dry-run 无待编译任务，源码与库/测试身份复验一致。

四类最终 allocator probe 均与矩阵使用同一 image dylib，每架构：

| Probe | 测量区间 | 结果 |
|---|---|---|
| `root-final` | 16 个活跃游标下 commit 24 次、restore 24 次；完整 cursor 生命周期 24 次（各 16 次 scan） | 72 区间；allocations/bytes/frees 全零 |
| `legacy` | exact index 10、physical index 1、root/metadata/descriptor 16、restore additions 1 | 28 区间；全部零，准备失败保留索引验证通过 |
| `warm` | 已准备缓存的 98,304 次外层读；含 nested 共 196,608 次 lock | 96 区间；全部零 |
| `joint` | 共同生产 handoff 安装：成功与两类冲突各 10,360 | 31,080 区间；全部零 |

全部正控制 allocations=4。`root-final` 覆盖 N=1/64/65/129、H=0/33/97、两种扫描 key 变更关系；通过既有 ReferenceTest friend 调用真实 epoch 安装，无新增生产 hook。准备、完整对象销毁及后台 collector 的候选/队列分配不在零分配声明中。warm/joint 排除范围沿用原证据：暖读不含初建、写入、refresh、swap；joint 不含准备、kernel、seal/root 或 deferred cleanup。`root` 标签的 ARM64 首次运行属于 graph baseline 更新前的中间记录，最终采用 `root-final`。

- HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。
- 全源码补丁 SHA-256：`30861e79cfe0ce72beed9cc0b267bcee1166b21cb51df786c8d08fcc9ade36b8`。
- image dylib：`7c8c470b2e1db32af6e437232691ee701d89fa4e174284b72f7385b9fd637980`。
- UI dylib：`f20fe2f83feab2784405119e7a2650d5c2fc2bc9c16765905c182f596e5d33bc`。

详见 [identity](checks-01/identity.json)、[累计源码补丁](checks-01/source.patch)、[结果汇总](result-summary.json)。`run_checks.py <新目录名>` 保存完整命令、环境、seed 和源码/二进制身份，拒绝覆盖旧目录；冻结代码后先生成 callgraph、检查 architecture baseline，再运行。`run_install_probe.py <arch> <新标签> <source.cpp>` 记录各探针编译/链接/执行命令和哈希。

## 剩余出口

该子集只限制单轮枚举和 scan 暂存。每 32 个候选仍可能遍历 H 个保护 roots，总工作随候选组数增长；树路径、replica 列表、root/metadata 销毁与 provider 调用另有成本。持续同 key 写入仍可反复使扫描失效，必须接 job admission 安全点的进度控制。销毁 bytes/nodes 预算、多 store 压力、公平性、锁占用和所有新增元数据的硬收费/分配失败仍未闭合。

未取得 Fresh 2% 回退、真实 stroke/首 dab/pen-up、正式 BR1-PERF、新 Vulkan 或 TSAN 资格。S09/S10 完整压力链、legacy batch/idle 迁移、长 stroke scope、M6 全出口、M7、undo/context 仍按 92 继续；本批不能单独授权长 scope 的默认启用。
