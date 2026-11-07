# S06：stable binding 物理 claim / retag 原语

本批实现 [03a §7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md) 的物理准备与一次消费。阶段状态统一在 [92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:475)。生产 selector 尚未调用本原语；物理 fixture 没有 PageStore root、alternate before 或 OwnerLedger，不能据此宣布 M6 完成。

## 唯一物理 owner 与消费顺序

完整 provider handle 从 Tiles3/test CPU allocation 记录移入 stable `KisCpuResidentBinding`，替代其原来单独保存的 allocation identity。provider 的 slot 索引只保存 binding 与既有 physical payload 归属，lookup/validate/lease release/transfer 使用 binding 局部 gate 验证完整 handle。retag 只更新一个 owner，没有跨 QHash 和 binding 的双写窗口，也不改变索引 key 或新建 payload。

`KisCpuBackingHandoff::prepare` 保留 provider，验证原 handle、descriptor 和目标逻辑版本，准备下一 allocation generation；不授予字节访问。`tryClaim` 非阻塞取得 binding、store iterator-read 与 TileData write 排斥，检查 resident、零 legacy/source users、无 memento、无 preclone，且只有 binding 自身的一份 TileData ref。多余 lifetime refs 包括同/跨 provider alias、immutable source 和 legacy cache；这些先保守拒绝。引用数不是写权限，两个物理屏障仍必需。

claim 期间 native/generic reader、其他 writer、source copy、retire 和 raw resident pin 都不能进入。成功 `commit` 在同一 binding gate 下 retag，再在 iterator 屏障保护下把 tile-write 转为普通 tile-read pin，返回现有 parked writer reservation。store 屏障在 pixel kernel 前解除；该 reservation 之后仍可 unpin、swap、materialize。旧 expected identity 即使仍持有原 binding 对象也不能重新取得访问。

Qt 不提供 write-to-read downgrade，因此转换期间仍保留 iterator-read，排除 swapper/pooler；binding 消费者直到新 pin 完成才重新进入。有效外部 lifetime holder 在 claim 时已被排除。claim 是同线程短区间，不能跨任意 callback/job 或未准备的工作。

未消费的 reset/析构解除 claim，保留原 handle 和字节。move 和 commit 仅消费一次；已消费对象仍保留 provider，要求在 owner gate 外清理，使最后 provider 引用的析构不落入安装区间。关闭后的已返回 resident writer 保持原有 pointer lifetime，后续新 pin 被拒绝。

## 代码、测试与边界

实现集中在 `KisCpuResidentBinding_p.h/.cpp`、`KisTiles3PageReplicaProvider.cpp`、`kis_tile_data_store.h/.cc`；test CPU provider 适配同一索引契约。物理 ownership fact 指向现有 stable binding，没有新增第二个 generation ledger。

PhysicalClaimTest 每架构新增 122 个 case，最终该目标 196 passed：

- 1/4/8/16 BPP × 15 种 claim 条件：空闲、native/generic read/write、parked writer、raw pin、额外 ref、legacy user、immutable source、同/跨 provider alias、preclone、swapped 与 pooler iteration；解除阻碍后可再取得 claim。
- 1/4/8/16 BPP × 4 种生命周期：取消、commit、移动、覆盖原有 claim；验证旧身份拒绝、原地址/完整字节保持、两次真实 retag、swap 后字节保持、payload work 与 committed bytes 不增长。
- 1/4/8/16 BPP × 11 种错误 handle/目标/descriptor 输入；拒绝不影响随后合法 claim，retired backing 不能重新准备。
- 并发 binding/generic 消费者，以及 provider 外部引用先释放、消费后延后 revoke 与原 pointer lifetime。

这些测试证明物理原语，不包含旧 captured PageStore view 的自动重解析、真实 before retention 或新旧 backing identity 的 ledger 安装。metadata 另有 pending-last-use/operation 拒绝，必须由未来联合计划与本物理 claim 一起消费；当前 CPU provider 的同步物理访问测试不授予 GPU last-use 资格。

## 真实 allocator 与兼容复验

[allocator-summary.json](allocator-summary.json) 将六个最终探针绑定到完整矩阵的同一个 image dylib 哈希；每个进程都有 shared Qt 分配正控制。

[physical-install-allocation-probe.cpp](physical-install-allocation-probe.cpp) 覆盖 1/4/8/16 BPP、1/8/64 页、连续两代 retag，分别计量 tryClaim 和 commit，每架构 48 个测量区间均为 0 allocations / 0 frees。每页都是独立准备、claim、retag；不是 M7 原子批。验证旧身份拒绝、字节保持和 provider payload work 未增加。探针明确测成功、无竞争的原语区间，不包含准备、延后销毁，也不提供 hold P99 或端到端性能资格。

同源码另复验 [recoverable metadata 探针](metadata-install-allocation-probe.cpp) 与 [原 publication/restore 探针](legacy-install-allocation-probe.cpp)，每架构分别 32 与 28 个测量区间全部为零分配、零释放。它们只证明所测安装区间兼容，不把物理与 metadata 探针的独立成功拼成 production M6 通过。

日志分别为 `install-<arm64|x86_64>-<final|metadata|legacy>.log`；对应 identity JSON 保存 compile/link/run、环境、probe/interposer/library 哈希。完整源码身份以 [checks-01/source.patch](checks-01/source.patch) 为准，因为探针 identity 的 tracked diff 本身不包含累计的三个未跟踪新源文件。

## 复现与增量关系

HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。完整 [manifest](checks-01/manifest.json)、[identity](checks-01/identity.json)、[result-summary](result-summary.json) 记录同源码双架构结果。最终 dry-run 检查没有待构建工作，并验证矩阵期间源码不变。

最终矩阵为 **17 目标 × 2 架构，4,196 passed，0 failed / skipped**，每架构 2,098 passed。完整源码补丁 SHA-256 为 `a7d889f0ed057ec4bd9c48c01ac4b78f6eddbf479a01a8211b4b211cf8345c4b`；核对时全部测试二进制、image/ui 库和构建身份仍与矩阵记录一致。结构门包含 21 manifest entries、21 ownership facts、16 runtime census groups、1,505 indexed APIs、14,285 reverse-call edges 与 19 frozen external intrusion files；6 项 reachability 工具自测通过。

[physical-implementation.patch](physical-implementation.patch) 只含相对上一 S06 metadata 批次的七个实现/测试文件及一个 ownership fact 文件；[incremental-review.json](incremental-review.json) 将八个前态逐一与上一完整 source.patch 复核。生成调用图/基线及累计新文件使用完整补丁复现。[ratchet-check.json](ratchet-check.json) 证明原始 ratchet 不变，未提高 reviewed ceilings。

`build-01/02/03.log`、`arm64-physical-01/02.log`、`callgraph-01.log`、`architecture-checkpoint-01.log` 和 arm64 initial probe 是保留的预检记录；196 passed 的定向结果不代替完整矩阵。没有覆盖、丢弃中间运行，最终资格来自 checks-01 与六个 final/metadata/legacy 探针的实际库身份。

复验使用不存在的新输出名，例如 `python3 docs/vulkan_gpu_design/evidence/br1_s06_physical_20260927/run_checks.py checks-02`。allocator 为 `run_install_probe.py arm64 rerun` / `x86_64 rerun`；兼容探针另传相应 `.cpp`。脚本拒绝覆盖输出，运行前必须使源码绑定调用图与当前代码一致。

下一段必须准备 OwnerLedger 的旧/新 identity 索引转换、分类差量与失败债务，再接独立 before、descriptor/metadata/终结记录、cache 重解析及共同 selector。不能在 retag 后才调用可失败的 registerBacking，也不能为固定 K 复制整张 backing 表。Vulkan、TSAN、完整 S10、产品 replay、M6/M7 性能与正式 BR1-PERF 仍缺新证据；完整目标继续开放。
