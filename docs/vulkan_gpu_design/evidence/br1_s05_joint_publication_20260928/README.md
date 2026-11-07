# BR1 S05 / OP6：overlay 安装前置与联合发布指南

本目录记录 2026-09-28 工作树的 JP1 实施及 JP1–JP8 代码映射。完整目标仍是按指南从 M1–M5 调整推进到 M6–M8；本批不关闭外层联合可见性、完整预算或 BR1-PERF。

## 改动及原 owner

原 PublicationCoordinator transaction delta 保持唯一可查询 authority。缺失 proof/removal 的实际节点和原 map 桶在安装前准备；桶需求包含其他未安装候选。候选用标准共享控制块保活同一个原 state，取消只归还容量和未交付 proof。暖 proof 原位更新，旧节点锁外析构；metadata/delta 安装后，ledger proof 撤销与历史收集进入 cleanup。

原 session seal、generic publish 和条件删除共用这一协议；通用写改为查询单页 proof，删除原分配式安装 helper。空存储记录不构成 semantic delta。节点/桶准备仍有 owner gate 内工作，完整预算和首字节前终结存储仍待继续。

具体函数、caller、失败终点和后续责任：[JP1–JP8 指南](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/02a_joint_publication_boundaries.md)。阶段状态由 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)裁决。

## 有意保留的失败记录

- `overlay-install-01/02` 探针把 observer 抑制的嵌套 callback 也计入预期安装次数。修正夹具后只统计外层真实区间；sibling 的像素与 delta 另行断言。
- `overlay-failure-01` 至 `04` 保留准备拒绝开发样本。Qt QVector 的 reserve 可能未取得容量，之后 append 重新分配；本批现对要求的实际容量显式检查，最终不把这种再次分配算作准备成功。
- `overlay-failure-04-backtrace.log` 保留真实 OOM 崩溃：当前 Qt `QSharedPointer::create` 在 `::operator new` 失败时销毁未初始化的控制块。该原 state 保活现使用 `std::make_shared`；本批没有修改 Qt 运行库。
- `graph-01.log` 是索引期间 audit 输入变化的拒绝；`architecture-freeze-01.log` 是旧 R1 容器文本契约的拒绝。规则现显式约束实际原 state、ProofMap/RemovalSet 与两类容量计数；禁止平行 side map 和现有侵入/布局上限保留。最终资格必须使用重新生成的图和新冻结身份。

## 证据入口与范围

- [真实读窗口复现](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/reader-window-probe.cpp)：冷页 seal 后新像素仍配旧 extent/adapter；暖页仍存在兼容旧 cache。它证明 JP2–JP7 的待改边界，不表示窗口已经修复。
- [安装 allocator 探针](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/overlay-install-probe.cpp)：4 BPP × K=1/9/65 × 4 种 overlay 变更 × 有/无 sibling，共 96 个实际外层安装区间；正控制为 1 次 / 8,210 B。区间仅为 `MutationSealInstall → MutationSealCleanup`。
- [准备 allocator 故障探针](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/overlay-storage-failure-probe.cpp)：实际 Tiles3 provider；逐点拒绝、旧值/新值、重试、最终追踪块/字节归零。区间为 `MutationSealStoragePrepare → MutationSealMetadataPrepare`，不把其他调用阶段或完整 job 准入纳入此结论。
- [测试运行器](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/run_checks.py)绑定 HEAD、完整工作树 diff（包含未跟踪生产文件）、运行库、实际库/插件/测试 hashes，并要求最终实际 Ninja no-op。
- [最终探针运行器](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/run_final_probes.py)重跑前批 62 项并增加本批 4 项；新探针身份包含共享 fixture header，不能只记录 .cpp。
- [文档校验](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/validate_guides.py)验证原 15 IDs、JP1–JP8、源函数入口、正反向关系与可定位链接；不授予运行时或阶段资格。

最终同源码矩阵 **9,154 passed、0 failed、0 skipped**；**66 个最终探针全部通过**。每架构 96 个外层 overlay 安装区间 allocations/frees 为 0，627 个准备分配拒绝和 12 个成功对照通过，退出后追踪块/字节为 0。源码差异 `c1c6f145e69d6e841fb15c5873ea23db49da681f31ddc66f33b6530fd1ae3c2d`，QtCore 与前批相同；全部库/插件/测试/probe hashes 与最终实际 Ninja no-op 已复验。

机器记录见 [evidence-scope.json](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/evidence-scope.json)、[矩阵身份](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/checks-01/identity.json)、[探针源码身份](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/probes-source-01.json)及 [指南校验](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/validation.json)；本批 [生产改动](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/overlay-code.patch) 与 [指南改动](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/guide-update.patch) 分别保留。完整 M6/M7/M8、Vulkan、TSAN、Fresh 2%、真实 stroke 尾延迟、OFF 产品配置、共享预算和外层联合发布仍待实现及验证。
