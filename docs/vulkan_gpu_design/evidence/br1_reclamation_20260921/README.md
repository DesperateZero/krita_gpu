# BR1 CPU 回收链路重构检查点（2026-09-21）

当前工作检查点，**不是核心结构完成，也不是性能通过**。设计、边界及后续缺口见 [67 §9](../../67_br1_target_structure_reconstruction_20260920.md#9-2026-09-21生产-cpu-回收链路卸载)。
不覆盖 `br1_core_reconstruction_20260921`、D13 或 D11/D12 封存原件。

## 本轮实现

- tiles3 CPU provider 显式 opt-in 后台退休；全 owner provider 均满足时，生产历史评估也在后台分批执行。
- commit/abort/restore/lease/last-use/View release 接同一历史候选队列；当前或仍受保护 View 释放不重新扫描全部历史。
- 独立回收执行器：每个历史 pass 至多 32 个 transaction / 32 个 root 候选 / 16 个历史页；首次退休至多 32 个 replica；树释放至多 128 个引用。
- persistent tree 不在最后 reader 栈上递归析构；共享分支只归还引用。任务持有 owner 寿命，支持后台回收的 owner 最后销毁也卸载。
- 显式 wait/drain 与 close 协调 queued/in-flight/failed 债务，关闭失败恢复调度；Qt 退出前还有静止 drain，宿主必须先停止 document/session 生产者。
- 物理 pin、逻辑 retention 和 last-use 不互相替代；失败记录没有出队即消失，in-flight 仍计入 pending 数量与 bytes。

## 验证协议

`run-checkpoint.mjs` 运行 14 套正确性测试，并分别重放 40 次并发提交、40 次生产并发写、40 次五项后台回收场景。
`run-results.json` 记录绝对 binary、参数、环境、退出码、log 和 totals；`verify-checkpoint.mjs --capture` 只允许首次创建 manifest，随后不带参数重验。
最终运行结果与已冻结文件列表以 manifest 为准，QtTest totals 包含 init/cleanup，不能当成独立业务场景数。

最终 14 套共 **345 passed / 0 failed / 0 skipped**，无 SAFE ASSERT；120 次额外重放全部通过。
CPU 库最终实现构建为 `development-br1-reclamation-build10.log`，随后测试端点重建为 `build11`（ResidentRead/tiled-manager）和 `build12`（Reference）同前缀日志；
Vulkan contract 最终实现构建为 `development-br1-reclamation-vulkan-build5.log`。各构建均 exit 0；架构检查见 `architecture-final.log`。

新增场景：8192 节点树最后引用释放；后台首次退休；provider 退休阻塞时发布仍返回且 in-flight 仍有债务；96 页 retained 历史释放；
当前 View 的重复释放不额外扫历史；last-use 未完成阻止回收；旧 transaction base 最后释放触发被延迟的历史回收；关闭拒绝后继续进度。
原有失败退休、物理 pin、facade lifetime、失效分配、undo/redo 与并发测试保留；即时内存断言在显式 drain 后检查原有释放量，不改成容忍泄漏。

开发阶段日志单独保留。首次链接失败是缺少测试可见性 export；早期未完整重建时的旧 test/new library 混跑不作为结果。
其他旧测试的即时释放断言失败保留为端点迁移记录。只有 `checkpoint-*` 与 `run-results.json` 对应的冻结运行进入最终检查。
第一轮 134 次完整运行的日志及报告以 `development-attempt1-` 前缀保留；`development-attempt1-relocation.json`
记录原绝对路径、归档路径与原始 SHA-256，原始报告内容未重写。其两套失败分别是 ResidentRead 的 2 项、tiled-manager 的 4 个格式数据行；120 次重放已通过。
第二轮同样以 `development-attempt2-` 和 relocation 清单保留：ResidentRead 与 tiled-manager 已通过，Reference 的重叠 anonymous lease 测试仍在 drain 前检查退休债务；随后补齐该处及生产并发写终止端点。

## 不能外推的结论

数量批次不是硬时间预算：单页版本 QVector/状态机评估、root reachability 查询及元数据析构仍可能随保留规模增加。
整体队列/树引用积压、内存压力反馈、背压、非 opt-in provider 与通用 GPU/I/O 完成唤醒仍需继续。
失败或外部直接 pin 的物理债务可能需要显式 `processRetirements`/close；wait-for-idle 不是强制释放或无限重试。
后台耗时不会自动进入前台 TLS recorder，后续必须补充后台 trace/CPU 归因以及 E 的 drain、峰值债务、交互尾延迟；本轮耗时均不是性能证据。
原位写 permit、完整生产 read scope、默认/删除准备及完整发布成本继续开放，不能用本轮回收迁移代替整个核心结构结清。
