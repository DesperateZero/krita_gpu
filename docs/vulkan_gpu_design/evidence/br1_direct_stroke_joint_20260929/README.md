# BR1 BC10 联合 Freehand fixture，2026-09-29

本批只修改 `FreehandStrokeTest`，没有修改生产源码、生产 API、字段、include、friend、锁或 TLS。目标是把首条 direct 开发入口此前分散的策略行为放进同一个真实 `FreehandStrokeStrategy` fixture，而不是为了测试继续扩大 `tool/strokes` 或 PageStore 接口。

fixture 在资源快照创建前把专用 autobrush 的 `PaintOpAction` 明确设为 Buildup，并断言 `paintIncremental()`。原文件的值为 Wash，会走 indirect painting，而当前 persistent 资格明确排除 indirect；因此此前仅设置 protected opt-in 的 Freehand 结果不能单独证明 direct persistent 分支被执行。本批修正了这项测试证据，不修改预设文件或产品选择政策。checkpoint 失败行只有在 persistent mutation active 时才会因 write context 变化失败，给出了分支命中的反证式保证。

成功 case 执行两段实际 autobrush 写入，并在两次强制 update 后检查不同像素可见；随后由原 `KisRunnableStrokeJobsInterface` 递归追加三步 sequential 必要后继，不再输入新的外部 stroke 数据。`finishStrokeCallback` 只在三步全部完成后被观察到。成功结束后只执行一次 image strategy undo：两段写入同时消失且 undo store 回到空位置；一次 redo 后完整 `QImage` 与结束时快照逐像素相同。

这组结果从行为和代码所有权共同证明：多个 update/cut 仍属于原 strategy transaction 的一个 undo 单元，递归 producer 会在 finish 前排空。测试没有读取裸 transaction 指针、session token 或 incarnation，也没有引入 owner getter；这种内部身份暴露违反 MI6，且不是证明业务连续性的必要条件。测试同样没有 include PageStore 内部类型。

| 目标 | arm64 | x86_64 | 证明范围 |
|---|---:|---:|---|
| `FreehandStrokeTest testPersistentAutoBrushStroke testPersistentAutoBrushStrokeCancelled testPersistentAutoBrushStrokeFailure` | 8 / 0 / 0 | 8 / 0 / 0 | direct Buildup persistent 分支；两次实际写入/update、可见性、递归 drain、整笔 undo/redo、用户 cancel；admission/像素失败信号/checkpoint/finish 四类失败的回滚、无 undo 与唯一 cancel |

原始输出见 [arm64](freehand-arm64.log)和 [x86_64](freehand-x86_64.log)。测试环境使用 offscreen Qt、`_install` prefix、`_build-br0-cpu/bin` plugin path 和构建树 Fontconfig。运行中的资源加载 warning 是该 fixture 的既有环境输出；目标断言和 QtTest 结果均通过。

第一次加入 undo 断言时，未等待 image scheduler 就立即检查设备，因而看到撤销命令已排队而像素尚未更新。测试随后在 undo 和 redo 后调用既有 `image->waitForDone()`，双架构通过。这确认 undo/redo 的观察点必须位于 scheduler drain 之后，没有因此修改生产同步协议。

失败矩阵在同一个 strategy fixture 中给出四个终点：实际 target 上的竞争 transaction 触发 admission 拒绝；首段真实 brush update 后向既有 job failure context 注入像素失败信号；真实 pending brush jobs 排空后改变 write context，使 dirty-publication checkpoint 拒绝；成功 checkpoint 后改变 context，使 finish 拒绝。四行均只有一次 cancel callback、没有成功 undo、最终像素为空、memento 释放；失败后的 sentinel 不执行。低层 painter/PageStore 像素故障的真实 swap-in 路径仍由首条入口批次的 `KisPainterStrokeCompletionTest` 证明，本行只验证该失败信号在真实 persistent Freehand 生命周期中的联合终点。

本批的主干侵入账本为生产文件 **+0/-0**，新增生产函数、字段、include、friend、锁、TLS 均为 0，关闭状态成本不变。测试只复用原 runnable jobs 接口、原 surrogate undo store 与图像 scheduler。源码和二进制 hash 见 [manifest](manifest.json)。

[文档检查](document-validation.json)覆盖 17 份活动文档的 1,725 个本地链接和 557 个 fragment，并检查正式工具未启用 persistent mutation、Freehand 公共 flag 未扩张、联合 fixture 的 Buildup/失败源码标记存在，结果为零错误。该检查只验证映射与启用门，不代替行为测试。

本批完成 BC10 中首条 direct 入口的联合正确性 fixture，包括多 update、策略 undo/redo、递归无输入 drain 和四类结构化失败；它不等于 BC10 的完整性能/覆盖出口，也不等于 BC9、默认启用或 M6–M8 资格。下一批转入 BC9 的 tiny budget、慢 reader、长 stroke、多文档与 cancel/close 进度。BC5 current/self-source、BC8 复杂入口和正式性能门继续开放。
