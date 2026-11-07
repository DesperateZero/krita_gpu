# S06.9：预备 backing 计账身份转换

阶段裁决在 [92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:475)，代码消费关系在 [03a §8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md)。本批只扩展既有 OwnerLedger，并将其与真实 physical claim/retag 在 fixture 中联动。生产 selector、独立 alternate before、root/cache/descriptor 联合安装尚未接通；不授予 M6/M7/M8 或性能资格。

## 改动及不变量

`prepareBackingHandoff` 接受已登记、resident CPU、单一物理收费的 Current / ActivePending source。source/target 的完整 handle、provider/epoch、slot、layout/domain、逻辑 key/代次与 allocation generation 加一逐项验证。原分类 claim 同时冻结旧、新 key 及 physical domain；并预留 ActivePending 差量和 CPU RetirementDebt。取消准备通过原 class reservation 回收，不改旧 key、live bytes 或 provider。

唯一 backing 索引由 Qt hash 改为可提取节点的 `std::unordered_map`。commit 在 ledger mutex 下提取原节点、替换 key/handle 再插回，表基数不增、load factor 不变，因此不需要新节点或 rehash。没有目标占位表、整表副本或第二个 generation owner。准备期间其他登记可以扩容，commit 不保存失效 iterator；只处理被触及的 backing。

`commitBackingHandoff` 必须在逻辑解绑和 provider retag 后由原 owner admission 消费：更新 physical representative、将同一 payload 归到 ActivePending，并返回已预留的 debt 给既有 writer 终结。旧身份查询和迟到释放不命中新代；同一物理字节只收费一次。typed wrapper 防止被普通 publication 分类 API 消费。ledger/budget 必须覆盖 reservation 生命周期。

CPU debt 按准备时的 resident domain 预留；并不声称它自动覆盖 parked writer 之后的任意域迁移。生产接线还须证明债务域覆盖、cancel/retirement/close 的进度与 S09/S10 关系。标准节点索引及 prepared slots 的真实常驻开销也须继续计入 S10；安装零分配不代表 prepare 零成本或端到端性能通过。

## 行为验证

PhysicalClaimTest 每架构新增 81 个 case，目标最终为 277 passed：

- 1/4/8/16 BPP × Current/ActivePending × publish/cancel，验证取消准备、move/重复消费、真实 retag、旧身份失效、迟到释放、swap/restore 后 representative、债务消费及终结归零。
- 1/4/8/16 BPP × 16 类拒绝：provider、epoch、slot、allocation/logical generation、key/layout/domain、无效/伪造 source、历史分类、pending/debt 压力、已有分类 claim、swapped 和已登记 alias；解除阻碍后重新准备成功。
- 准备后再登记 129 个无关 backing，跨两代 retag（包含 pending→pending），验证索引扩容不丢候选、旧身份或其他登记。

fixture 的 swap/restore 用例会先恢复 CPU 再消费 CPU debt；它没有旧 PageStore root 或 before retention，也没有证明任意域上的直接取消。累计 CPU/业务矩阵与源码/二进制身份由 [checks-01 manifest](checks-01/manifest.json)、[identity](checks-01/identity.json) 和 [result-summary](result-summary.json) 记录。

最终同源码 **17 目标 × 2 架构，4,358 passed，0 failed / skipped**，每架构 2,179 passed；完整补丁 SHA-256 为 `be41bfcc6a87e20ad79f1772796e8572ed611187d7cb7f784b10499974d3c224`。结构门为 21 manifest entries、22 ownership facts、16 runtime census groups、1,514 indexed APIs、14,484 call edges、19 frozen external intrusion files；6 项工具自测通过。

## 实际 allocator

[ledger-install-allocation-probe.cpp](ledger-install-allocation-probe.cpp) 覆盖 1/4/8/16 BPP、1/8/64 页、准备后新增 0/129 个 backing、连续两代；分别计量取消准备和 physical＋ledger 安装，每架构 96 个测量区间。每页独立消费，不是 M7 原子批。检查原 bytes、旧/新分类、pending live/debt reserved 数量、reservation 归零以及没有 copy/new handoff payload。

原 physical、recoverable metadata、publication/restore 探针也在最终库上复验；每个进程都执行 shared Qt 分配正控制。结果与库身份见 [allocator-summary](allocator-summary.json)。只声明所测成功、无竞争的安装/取消区间；不包含准备、延后销毁或端到端延迟。

八个最终进程均通过：每架构 ledger/physical/metadata/legacy 的 96/48/32/28 个测量区间全部为 **0 allocations / 0 frees**。image dylib SHA-256 为 `42b97f3560fea7415669ba3748477e307c533c94dc5bc097a8fee9e3d0c7dd7e`，与完整矩阵一致。

## 身份、失败记录与复现

HEAD 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`。完整源码以 [source.patch](checks-01/source.patch) 为准，包含累计三个未跟踪的新生产/测试文件；probe identity 的 tracked diff 本身不完整。最终矩阵检查源码未变和 ninja 无待构建工作；probe library hash 必须与矩阵一致。

[ledger-implementation.patch](ledger-implementation.patch) 是相对上一 physical 批次的五文件增量；[incremental-review](incremental-review.json) 已把前态与上一完整 source.patch 逐个重建比对。生成的 graph/baseline 用完整 source.patch 复现。[ratchet-check](ratchet-check.json) 证明原始 ratchet 不变，未提高 reviewed ceilings。ownership inventory 新增一条描述既有 ledger 分类责任的 fact，不新增 owner。

保留所有中间记录：`build-02.log` 是新增测试错误调用 source API 的编译失败；`arm64-physical-01.log` 有 65 个 fixture 失败，64 个来自禁止在 live 账本中重配 limits，1 个来自重复 retirement operation ID。修正为用真实 reservation 制造/解除压力，并使用唯一 operation ID；没有放宽生产 guard。`arm64-physical-02.log` 为修正后的 277 passed。`callgraph-01.log` 是补齐 ownership fact 前的生成记录，最终使用 `callgraph-02.log` 和完整矩阵；arm64 initial probe 只作预检。

复验使用新的输出名：`python3 docs/vulkan_gpu_design/evidence/br1_s06_ledger_20260927/run_checks.py checks-02`；allocator 使用 `run_install_probe.py arm64 rerun` / `x86_64 rerun`，可另传兼容 probe `.cpp`。脚本拒绝覆盖已有证据。运行前须更新当前源码绑定的 graph/baseline，不能靠提高 ceiling 通过结构门。
