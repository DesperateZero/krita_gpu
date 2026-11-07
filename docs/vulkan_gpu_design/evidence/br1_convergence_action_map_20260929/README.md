# 收敛行动与代码映射核验（2026-09-29）

本次仅修改八份指导/导航文档，回答明确方案、API 合并删除与 CODE_INDEX 式改动映射的要求。未修改产品源码、未构建或执行产品测试，未恢复或启动持续实现任务；不授予新的产品或 M6–M8 资格。

- [API 行动表](../../br1_modification_guide/API_CONVERGENCE_MAP.md#convergence-action-map)：六项有序工作，逐项列出现状、函数、待改及同批删除对象、验收和停止条件；另列 copy 候选与联合窗口设计缺口。
- [源码反向索引](../../br1_modification_guide/CODE_INDEX.md#api-convergence-index)：从文件/函数定位具体动作。
- [执行勾选](../../br1_modification_guide/CONVERGENCE_CHECKLIST.md#convergence-action-checklist)与 [92 §16.12](../../92_br1_m6_m8_execution_baseline.md#convergence-action-plan)：统一规划和候选状态；最近已冻结的产品资格仍属 §16.11。

静态核对确认当前非 wrapped clone/copy 已有新候选，默认 brush 的 `addDabJobs` 仍向 `bltFixed` 传入 `nullptr`。copy 候选的 32 个 clone 局部通过来自[原日志](../br1_copy_bounds_convergence_20260929/focused-arm64-01.log)，后续 bounds 测试发生 SIGABRT；[诊断日志](../br1_copy_bounds_convergence_20260929/bounds-lldb-01.log)记录非法释放，当前源码已改显式基类调用。本次不把这些旧局部记录当作修正后源码的通过资格。

[源代码读取身份](source-before.json)覆盖当前 124 个改动范围文件（含六份未跟踪源码）及 tracked diff；[验证脚本](validate.py)比较编辑前后身份，检查新映射关键符号和完整活动指南的链接/锚点/行号范围/空白。源码链接是编辑入口，文档检查不证明语义正确、全 caller 审计或运行通过。未读取 archive。

[验证结果](validation.json)记录源码未变、copy 相对开始前的增删清点与关键定位；最终文档检查结果另存 `document-check-delivery.json`，前两次检查记录保留。[本次文档增量](documents.patch)只相对于开始本次文档任务时的八份文件；[20 处旧源码链接重定位](source-link-remap.json)仅更新行号，没有将历史测试资格转移到新实现。
