# S06：recoverable write 的逻辑转移与预备 metadata 安装

对应 [03a 的 S06.6 / S06.8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md)，阶段状态仍由 [92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:475)裁决。本批只落地逻辑原语及预备 metadata 安装，尚未接入生产 selector，也没有 provider physical claim/retag。不同 logical slot 不能代替物理独立性证明。

## 实际改动与终结责任

`AcquireRecoverableWrite` 复用原 writer 生命周期，但只接受 Published 或本事务 Prepared base G、已经 Valid 的 alternate B，以及可转移的旧 authority A。检查 A 没有 reader/pin/last-use/operation、没有 authority handoff；A 与 B 的 slot 不同、layout 相同；T 使用 A 原 provider/epoch/slot、相同 layout/domain 和下一 allocation generation。普通 AcquireWrite 继续拒绝占用中的 slot。

纯 transition 移除 G→A、令 G.authority=B，沿原逻辑 writer 保留 B，再建立 T。metadata 的私有 `prepareRecoverableWrite` 在准备阶段计算 Acquire + PrepareWrite；候选安装后 writer 已为 Writable，因此未来 retag 后不需要再执行可能失败的 PrepareWrite。它不直接触碰 provider 或字节，不授予物理写权限。

准备读取 current、exact base 和必要冲突 witness，复用 PreparedPublication 的真实 arena/index/activity reservations；不导出整个 history。RecoverableWrite 候选持有严格 page revision，只安装 base 与 T；任何保护变化令候选拒绝，不能覆盖晚到的 reader/pin/last-use。既有 DetachPreparedVersion 仍保留其动态保护与语义 delta 策略。准备种类也在安装时复验，不能把 detachment/publication/recoverable 候选交叉消费。

成功后的 publish/cancel 仍使用原 writer 匹配与 before pin 释放：source/baseAuthority 为 B。取消只产生 T/A 的退休责任，G 继续由 B 解析，不恢复 G→A、不倒写 A。候选 move、拒绝、取消和 owner 析构均释放预留；生产集成必须在 gate 外消耗 DeferredPublicationCleanup。

完整生产 handoff 仍需 S06.2–S06.5、S06.7、S06.9：独立且持续保活的 before、raw pin/alias/source/swap/preclone/retire 排斥、cache 失配重解析、预备 descriptor/预算分类/终结记录。先取得并持有 physical claim，再尝试 metadata 安装；安装成功后的 retag 与相关安装必须消费预备资源且不可失败，最后才能暴露字节。不能先 retag 再调用可能拒绝的 metadata install。

## 定向与完整验证入口

ReferenceTest 新增每架构 229 个 case：

- `recoverableWriteGuards`：1/4/8/16 BPP × 26 种合法/冲突/身份输入，共 104 行；同时证明 immediate applyOwner 不接受该 transition、普通 AcquireWrite 没有继承 slot 复用权限。
- `preparedRecoverableWriteLifecycle`：124 行，覆盖 H0/H128、Published/同事务 Prepared base、晚到保护、跨 owner/错误安装种类、move/重复消费、owner 先析构、普通 publish/cancel 及全部 reservations 释放。
- `recoverableWritePreparationHonorsBudget`：相同输入的无限额正控制与精确元数据硬上限拒绝；验证 backpressure 增加、状态不变、reservation 归零和 owner 关闭后 live 归零。

最终同源码矩阵为 **17 目标 × 2，3,952 passed，0 failed / skipped**，每架构 1,976 passed。结构门为 21 manifest、21 ownership、16 census、1,481 APIs、14,126 call edges、19 intrusion files；6 项工具自测通过。完整 source.patch SHA-256：`4f48f935f83ba1fde99e764eb6626c65ad25d6ed2d6b3a75a36bb5f705a6bd62`。

最终定向 [arm64-targeted-06.log](arm64-targeted-06.log) 含 init/cleanup，共 231 passed。完整矩阵由 [run_checks.py](run_checks.py) 运行；结果与最终源码身份在 [result-summary.json](result-summary.json)、[checks-01/manifest.json](checks-01/manifest.json) 和 [checks-01/identity.json](checks-01/identity.json)。此矩阵包含原有 painter、transaction、scheduler、manager 与 H/V/random iterator 控制用例；没有用定向结果替代完整矩阵。

## 两架构真实 allocator 证据

[allocator-summary.json](allocator-summary.json) 将四个最终探针与矩阵的同一 image dylib 哈希绑定。每个进程均有 shared Qt 分配正控制，不能用未启用的拦截器冒充零分配。

- 新 [metadata-install-allocation-probe.cpp](metadata-install-allocation-probe.cpp)：1/4/8/16 BPP × 1/64/65/129 页 × H0/H128，每架构 32 组。先同时准备两个候选再取消一个；所有候选与 deferred cleanup 容器在审计区间外准备。计数只包围每次真实 installRecoverableWrite；区间后检查 reservation 归零与 CancelWrite 效果。这是多次单页安装，不是 M7 多页原子提交。
- 原 [legacy-install-allocation-probe.cpp](legacy-install-allocation-probe.cpp) 按既有 M5 探针原样复验：exact index tier、physical index 插入/删除、1/64/65/129 页的 metadata/descriptor/root 安装、restore additions 及 prepare bad_alloc。证明本批对公共 prepared 容器的扩展没有破坏原安装区间。

两个架构、上述两类探针的所有测量区间均为 0 allocations / 0 frees；准备与延后清理不在零分配声明内。最终日志：[arm64 新原语](install-arm64-final.log)、[x86_64 新原语](install-x86_64-final.log)、[arm64 原路径](install-arm64-legacy.log)、[x86_64 原路径](install-x86_64-legacy.log)。各同名 identity JSON 保留编译/链接/运行命令、环境、probe/interposer/library 哈希与 tracked diff；完整源码复现身份以矩阵 source.patch 为准，包含三个未跟踪的新源文件。

## 源码复现与保留的中间失败

HEAD 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`，最终完整 [source.patch](checks-01/source.patch) 含累计生产/测试改动、新源文件和生成的审计输入。[metadata-implementation.patch](metadata-implementation.patch) 仅为相对上一 binding 批的五文件差异；[incremental-review.json](incremental-review.json) 校验这五个文件的前态确实来自上一完整补丁。复现不能只使用增量 patch。

[ratchet-check.json](ratchet-check.json) 比较上一累计补丁与本批的完整 raw ratchet，未提高 reviewed ceilings。最终调用图为 callgraph-04，结构检查准备日志为 architecture-checkpoint-01；完整矩阵再次运行 architecture gate 和六项工具自测，并检查结尾无待构建工作、运行期间源码未变。

所有中间日志保留：

- targeted-01 的 48 个失败：把 Historical 当作合法写 base 的错误预期，以及在 Published 上使用只允许 Prepared 的 retain 操作。
- targeted-02 的 8 个失败：Prepared base 的 AcquireRead fixture 遗漏 transaction。
- targeted-03 为 210 passed；新增负例后 targeted-04 为 218 passed / 9 failed，其中 8 行把 Valid replica + active operation 当作有效初态，另 1 行错误地要求预算拒绝文本包含 budget。
- 后续 fixture 分开检查无效初态与 Materializing before；预算用例检查实际 allocation 拒绝和 backpressure。targeted-05 为 227 passed；增加 target domain 保持约束后最终 targeted-06 为 231 passed。没有放宽 authority/reader/预算语义或删除失败输入。
- callgraph-01/02/03、build-01 至 build-08 和 arm64 initial probe 对应中间源码，仅为开发记录。特别是 initial probe 早于准备阶段合并 PrepareWrite，不能作为最终原语的零分配证据。

复验使用新的、不存在的输出名：`python3 docs/vulkan_gpu_design/evidence/br1_s06_metadata_20260927/run_checks.py checks-02`；探针为 `run_install_probe.py arm64 rerun`、`run_install_probe.py x86_64 rerun`，原路径额外传 `legacy-install-allocation-probe.cpp`。脚本拒绝覆盖已有输出；使用前先保证源码绑定调用图与当前代码一致。

Vulkan foundation、TSAN、产品 freehand replay、真实 handoff 字节/并发验证和正式性能未在本批取得新证据。元数据局部预算拒绝不等于完整 S10 资源闭环；零分配安装也不等于 stroke 延迟合格。M6/M7/M8、其他指南条目和 BR1-PERF 继续开放。
