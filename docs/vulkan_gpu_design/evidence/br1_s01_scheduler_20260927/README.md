# S01 第三批：stroke 终结失败与调度接续（2026-09-27）

本目录记录工作树的开发正确性证据。唯一阶段状态见 [92 §15](../../92_br1_m6_m8_execution_baseline.md:475)，代码关系见 [S01 指南](../../br1_modification_guide/01_stroke_scope_and_failure.md:5)。M5 比较基线不变；本批不授予 M6/M7/M8、BR1-PERF、Vulkan、TSAN 或 allocator 资格。

## 源码与运行身份

- 源码 HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`；工作树补丁 SHA-256：`c4a30e3e14b67c5e53454d754efabc1864be30158da8bd00f986d5d9ab6ab849`。
- [source.patch](checks-01/source.patch) 包含全部 tracked diff，并显式附入尚未进入 git index 的 `KisPainterStrokeCompletionTest.cpp`。新增测试的 CMake 注册已在补丁中；没有依赖未记录的测试源码。
- [identity.json](checks-01/identity.json) 记录 CMakeCache、compile_commands、image/UI dylib 和 16 个测试 binary 的 SHA-256。构建为 RelWithDebInfo、arm64+x86_64、Vulkan OFF，seed=12345、offscreen。
- [manifest.json](checks-01/manifest.json) 保存每条命令、开始/结束时刻、退出码和 Qt totals；32 个测试进程均无 FAIL/SAFE ASSERT。最终 ninja dry-run 无待构建项，运行前后源码补丁一致。
- `callgraph-generation-02.log` / `source-checkpoint-refresh-02.log` 对应最终接口顺序；早一轮同名无后缀日志保留为开发检查点。原有虚函数次序保留，新 worker 接口追加。

## 本批变化与覆盖

`KisPainterBasedStrokeStrategy` 检查 memento 准入，direct 使用 tryEndAndTake，indirect 临时事务使用 tryEnd；只有成功后才移交 auto-key 与 undo command。取消被拒绝时保留 transaction/painters/temporary target，重新排入取消；恢复 frame 内容后才撤销 auto-key。主事务准入成功后才开始 interstroke，拒绝的新事务不终结已有 owner。

`KisStroke` / `KisStrokesQueue` 保存现有调度所有权：失败后停止新输入和可取消后继，保留必需 children；未抬笔的句柄保留到输入 owner 结束。只向仍在队列中的 LoD buddy 传播失败；已经完成但被强引用的 buddy 不重新排任务。重复 cancel 不再次减少 opened counter。

取消重试使用每 stroke 一个既有队列任务与 1→100 ms 退避，scheduler 合并唤醒，复核剩余 deadline；普通异步执行无需后续编辑才能继续。waitForDone/barrierLock 在 owner 锁外等待最多 10 ms 再检查，不依赖 GUI event loop。此机制不证明永久预算拒绝能恢复，也不替代 S09 的 pin/completion 通知。

新增场景包括：

- worker/dab 或 finish 失败、必须完成的 children、重复终结、仍打开的输入句柄；LoD 双向失败及 LoDN 已完成情形。
- 无新输入的 timer 唤醒，以及不泵 GUI 事件的 waitForDone/barrierLock；重复取消仍保留清理 owner。
- 真实 painter-based strategy/scheduler 的 direct/indirect、auto-key 开/关、正常完成/拒绝提交/拒绝取消 12 组组合；真实 live writer 阻止终结，释放后自动取消，undo 不误登记。正常路径还核对 undo/redo。
- 初始化拒绝不执行 paint、不移交 undo、不取消其他 active history，也不启动对方正在使用的 interstroke 辅助事务。

UI 目标使用固定像素与不执行 brush kernel 的 preset fixture，检查真实业务终结边界；它不是 freehand 产品 replay 或绘画性能测试。

## 验证结果

| 架构 | 目标 / 进程 | Qt passed | failed / skipped |
|---|---:|---:|---:|
| arm64 | 16 | 1593 | 0 / 0 |
| x86_64 | 16 | 1593 | 0 / 0 |
| 合计 | 32 | 3186 | 0 / 0 |

PageStore architecture 与 6 项 reachability 工具自测通过：21 manifest entries、21 ownership facts、16 runtime census groups、1,472 indexed APIs、13,805 reverse-call edges、19 external intrusion files。`ratchet-check.json` 与 HEAD 对比相同，未放宽限制。PageStore source inventory 的范围不包含新增 UI test；该文件由上述 source.patch 与 binary identity 单独绑定。

复现当前工作树验证：`python3 /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s01_scheduler_20260927/run_checks.py checks-02`。脚本拒绝覆盖已有证据目录；源码改变后先重新生成调用图和 source checkpoint。

## 保留的失败与限制

`build-ui-01.log`、`build-all-02.log` 保留新测试 fixture 的编译错误（抽象 settings 方法、QSharedPointer 显式构造、timed bounds include），在后续 build-03/04 修正。`development-arm64-KisPainterStrokeCompletionTest-02.log` 虽 Qt totals 为通过，但假 preset 缺 factory 产生 SAFE ASSERT，不能作合格证据；已补真实注册的无 kernel 测试 factory，-03 与最终矩阵没有该告警。早期 core 单架构试运行不是最终源码资格。

S01 仍未全闭合：像素写失败尚未贯穿 PaintDevice→painter/job sink；其余 legacy 终结/析构 owner、parent-attached command、interstroke 辅助 void command、indirect merge 多设备结果仍待迁移。取消的 O(N) compatibility 准备与硬预算保证由 S03/S05/S10/U01 接续。没有延长生产 pending 生命周期；没有实现 M6/M7 handoff；没有重测 install allocator、产品 replay 或正式性能。
