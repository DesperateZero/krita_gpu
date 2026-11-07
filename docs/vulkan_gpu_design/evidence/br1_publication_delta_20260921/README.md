# BR1 root metadata 索引候选与发布 delta

实现与范围见 [67 §22](../../67_br1_target_structure_reconstruction_20260920.md#22-2026-09-21root-metadata-的索引候选与发布-delta)。
普通 root 候选/安装只涉及 current、target、own Prepared 及必要冲突见证；严格 revision 与整批 claim 不变。
default/full restore 目录只导出 header，生产预检精确 lookup；缺失 default 的恢复在候选中生成记录与 descriptor，成功后 root 前安装。
同步 fused 退休有 32 records/changed-page 预算，超预算使用原有普通提交 fallback + 后台历史收集。

## 可复核记录

- `initial-build/initial-*`：第一版 CPU/Vulkan 构建完成后，Reference 211、CpuMutation 338 全部通过。
- `candidate-build/candidate-*`：补全 default 恢复候选化、退休移除计数与 8 个实际恢复回归；Reference 211、CpuMutation 346 通过。
- `final-build/final-*`：CPU/Vulkan 构建完成后，15 套完整测试 **1095 passed**、paint-device 选定 **9 passed**；
  16 组各 20 次、**320 次重复**全部通过，共 **336 个测试进程**，无 FAIL/SAFE ASSERT/QFATAL。
  Reference 211、CpuMutation 346、painter 99、tiled manager 291；相对 §21 新增 78 行。

最终 suite/repeat 清单与 source/binary/doc hashes 由 `verify-checkpoint.mjs --capture` 一次性记录，之后无参数复核；
拒绝覆盖 manifest。核对阶段构建/测试时序、完整 oracle/预算/真实 H 矩阵与默认候选 8 行、实际库/插件路径、
架构/whitespace、本地文档链接及 D11/D12 archive-only。旧目录/manifest 不覆盖。

`run-checkpoint.mjs` 拒绝覆盖标签。build 完成后才运行 focused/full；不允许测试与链接重叠。
full 包括 15 套完整测试、paint-device 7 个选定槽、16 组各 20 次重复；Qt totals 含 init/cleanup，不把重复进程混算完整套件。
所有运行仅作正确性/工作量证据，不作性能样本。

## 工作量与安全边界

Reference 新增 58 行：18 类 root/default/restore 情况 × H=0/31/511，加 fused 32/33 边界等 4 行。
比较完整安装状态、保护字段、失败不变性及效果；原有多页 claim、晚到 lease/last-use/completion、目录/root/retention 回归继续保留。
真实 BPP=1/4/8/16 × H=0/7/63 提交输入/安装 **2/2**、两页恢复 **3/2**，restore lookup **3**、目录 headers **2**，
所测前台完整 snapshot 导出 **0**。实际旧 View、恢复后像素和 close/provider bytes=0 均断言。
缺失 default 候选准备期间不增加 live 版本、新事务拒绝不留预检安装、成功后 descriptor 可用另验 8 行。

候选计数含失败/重做；fused 安装保留记录和移除记录分别计数。预算只限 changed page 的版本记录数，不限单版本 replica/保护列表，
不是全局回收预算或最优性能阈值。prepared/mutable 索引维护、默认节点/hash/descriptor 安装、目录 N、控制/GC、root/extent 与候选销毁仍有成本。
未授予原位 permit、所有 producer 接入、完整短发布、无锁、TSAN、回收总预算或 BR1 结清资格。
structural_completion=false，performance_qualification=false；最终同义主干 M、同域驻留 K、真实跨域 X、完整 E 仍待整体结构完成。
