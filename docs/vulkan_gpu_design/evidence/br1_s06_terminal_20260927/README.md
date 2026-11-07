# S06.9：ledger 持有的 handoff 债务与普通终结

阶段裁决仍在 [92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:475)，代码对应关系见 [03a §10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md)。本批修复生产联合候选接线前发现的债务归属缺口；生产 handoff selector、独立 before 的完整保活和 descriptor/terminal 联合存储仍未接通，不能据此授予 M6/M7/M8 或性能资格。

## 问题与修改

原 `commitBackingHandoff` 把 CPU RetirementDebt reservation 返回给临时 caller。普通 metadata cancellation 会通过 OwnerLedger 再申请 debt，看不到 caller 手中的预留；单页 debt 硬额度下因此可能拒绝本应已获得保证的取消。writer 换出后，原 CPU 预留也不能直接支付 SSD 上的分类转换。

现在 reservation 留在既有 backing record，由同一 OwnerLedger 持有。`commitBackingHandoff` 返回消费结果，retag 时原索引节点连同 headroom 转入新身份；再次合法 pending handoff 复用已有 headroom，不重复申请。没有新增 session page 字段、adapter 终结 token 或另一张退休表。

真实 provider domain admission 在公布域变更前同步更新 headroom 的 reserved 域，aggregate debt 额度保持不变。该预留只保证已计费物理对象将来改为 RetirementDebt；SSD 的未来分类转换不另占一个 payload 容量，实际 swap 新增的 SSD 容量仍经原 admission。利用 sole-owner handoff 建立 representative、退休前消耗预留再替换 representative 的不变量，迁移只查一个 backing，不扫描 aliases/history。

普通 `prepareBackingChanges/prepareRetirementDebt` 在原物理分类投影中找到 touched backing 的 headroom，按物理 charge 抵扣一次；未覆盖的退休部分仍须正常准入。取消 prepared candidate 保留 headroom，提交退休时消费它，成功发布到非 ActivePending 分类后释放它。共享 aliases 一起退休只支付一次 physical debt；保留 alias 时不能把仍活着的 physical charge 再收费一次。准备与消费复用原 class claim。

新增的 backing reservation 字段、prepared credit 索引/数组仍属于 S10 的真实元数据计账范围；本批没有证明完整全局预算或 metadata footprint 目标。Fresh 登记成本、swap 干扰及 stroke 尾延迟也仍需正式比较，不能由零分配安装推断性能通过。

## 行为与资源验证

PhysicalClaimTest 每架构新增 64 个 case，定向结果为 **341 passed**：

- 32 个单页硬额度 case：1/4/8/16 BPP × CPU/SSD × direct retirement、prepared retirement、取消准备后重试、发布后释放。pending、debt、SSD 额度压到一页，连续两代 handoff；额外 debt 被拒绝，而既有 headroom 支持原取消/退休。取消准备后真实 swap-in/out 再重试，最终 live/reserved 归零。
- 32 个 shared case：1/4/8/16 BPP × CPU/SSD × 保留/一起退休 alias × 两种变更顺序。先取消准备再提交，验证单次物理收费和代表身份替换后的释放。

ResidentReadTest 的 32 个联合 retag case 现在接入 metadata 的真实 prepare/commit/cancel debt callbacks，并把 debt 额度压到一页；整个目标 **193 passed**。这证明普通 metadata 终结能使用 ledger 已有预留，但该 fixture 仍没有 PageStore root/selector 全链路。

最终累计矩阵与身份见 [result-summary](result-summary.json)、[manifest](checks-01/manifest.json) 和 [identity](checks-01/identity.json)。测试记录、结构门、工具自测与最终 dry-run 均保留，不以总数替代阶段出口。

最终 **17 目标 × 2 架构，4,806 passed / 0 failed / 0 skipped**，每架构 2,403 passed。源码补丁 SHA-256 为 `78d29b5641833b40f6826cd9e9446f83cf6e29303fba1f7c05cfe59a9ad6f3a7`。结构门：21 manifest entries、22 ownership facts、16 runtime census groups、1,518 indexed APIs、14,728 call edges、19 frozen external intrusion files；6 项工具自测通过。

## 真实 allocator

[ledger probe](ledger-install-allocation-probe.cpp) 覆盖 1/4/8/16 BPP、1/8/64 页、索引增长 0/129、连续两代 handoff；预留跨两代保留。新增普通退休准备的取消/安装测量，并在增长组混入一个无 handoff 预留的 Current backing，验证该未覆盖部分额度耗尽时拒绝、解除压力后成功。所有 backing 真实退休后检查 live/reserved 归零。

ledger 每架构 **144 个测量区间**，兼容 physical/metadata/publication 探针各为 48/32/28 个；最终八进程使用矩阵同一 image dylib，结果和正控制见 [allocator-summary](allocator-summary.json)。仅测量已准备、成功、无竞争的独立区间；prepare、域迁移、延后销毁不在零分配声明内，不是 M7 原子批。

八个最终进程全部通过，所有测量区间均 **0 allocations / 0 frees**。image dylib SHA-256 为 `dcf1b6c0e275b23c4e5608b1335478ade473d8c054da2c004bbb76f53239d066`，与矩阵 identity 一致。

## 源码与复现

HEAD 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`。完整累计源码以 [source.patch](checks-01/source.patch) 为准，包含三个未跟踪的新生产/测试文件；[terminal-implementation.patch](terminal-implementation.patch) 是相对上一 read-rebind 批的七文件增量。[incremental-review](incremental-review.json) 重建比对了每个前态；[ratchet-check](ratchet-check.json) 证明原始约束未放宽。

`build-01.log` 的 missing-field initializer warning 已在后续构建补齐，未忽略；定向两个目标运行均成功。`callgraph-01` 与初始 ledger probe 在域迁移改为 O(1) 查找之前产生，只作中间记录；最终使用 `callgraph-02`、完整矩阵和带 `final` 的八个 probe。此前批次的失败与资格保持原记录，不覆盖或重解释为本批结果。

复验使用新目录名：`python3 docs/vulkan_gpu_design/evidence/br1_s06_terminal_20260927/run_checks.py checks-02`。allocator 使用 `run_install_probe.py arm64 新标签` / `x86_64 新标签`，可另传对应 probe `.cpp`。脚本拒绝覆盖已有日志；更新代码后先重新绑定调用图和 baseline，保持原 ratchet。probe identity 中的 tracked diff 不含未跟踪源码，应以完整矩阵补丁与同库哈希复现。
