# BR1 首条 direct stroke 开发入口，2026-09-29

本批把已有 history mutation 能力接到一个**显式开启**的真实 `FreehandStrokeStrategy`，范围固定为单 painter、Pixel Brush、RGBA8、OVER、无 selection/indirect/mask/wrap/LoD。测试派生 strategy 调用 base 的 protected opt-in setter；`FreehandStrokeStrategy::Flags` 与正式工具入口保持主干接口，因此这不是默认启用或 BC9/M6–M8 资格。

原 `KisTransaction` 在 strategy 初始化时完成准入；`KisPainter` 只保存非拥有绑定，multi-dab、scalar fixed、bitBlt 与 mirror 的无 owner 入口消费该绑定。更新在取走 dirty 之前 checkpoint；finish/cancel 继续由原 transaction 终结，并先解绑/销毁 painters，再释放 transaction。`KisBrushOp::addDabJobs` 删除显式空 owner 参数，实际 async jobs 因此进入同一原 owner。全 painter-based failure reporting 属于此前 S01：PageStore 可恢复拒绝后避免把部分写入登记为成功 stroke；本次收缩没有把它误归为 pilot 开关。

验证只覆盖本批目标：

| 目标 | arm64 | x86_64 | 证明范围 |
|---|---:|---:|---|
| `KisDabRenderingQueueTest testBrushPagePartition testSharpnessLine` | 50 / 0 / 0 | 50 / 0 / 0 | 实际 brush 的持久 owner、并行页分区、1px 同步分支、checkpoint、像素对照及 transaction undo/redo |
| `FreehandStrokeTest testPersistentAutoBrushStroke testPersistentAutoBrushStrokeCancelled` | 4 / 0 / 0 | 4 / 0 / 0 | 原 strategy、实际 autobrush/update、checkpoint 后可见像素、finish 与 cancel 回调 |
| `KisPainterStrokeCompletionTest testPixelFailure` | 22 / 0 / 0 | 22 / 0 / 0 | painter void 写失败进入 scheduler cancel；证明 base failure reporting 不能随 pilot 关闭 |

Freehand 原始输出见 [arm64](freehand-arm64.log)和 [x86_64](freehand-x86_64.log)，失败契约输出见 [arm64](completion-arm64.log)和 [x86_64](completion-x86_64.log)。测试环境沿用既有 freehand smoke 的 `_install` prefix、构建目录 plugin path 与 offscreen 平台，并显式使用 `_build-br0-cpu/fontconfig-test/fonts.conf`，避免系统字体枚举影响目标用例。最初缺 prefix/Fontconfig 的启动尝试没有进入或完成目标用例，不计为产品失败或通过。

架构调用图重新解析 87 个 PageStore 可达 translation units，得到 1,814 APIs、19,634 edges、17 callbacks；刷新源码 checkpoint 时 21 manifest、25 ownership、16 census、19 intrusion 检查通过。见 [callgraph](callgraph.log)和 [architecture](architecture-write.log)。调用图计数不等于公共 API 数；本批新增 API 账本见 [API §15](../../br1_modification_guide/API_CONVERGENCE_MAP.md#direct-stroke-pilot-delivery)。

[文档检查](document-validation.json)覆盖 17 份本批活动文档的 1,719 个本地链接和 554 个 fragment，确认正式工具未调用 protected opt-in setter、Freehand 公共 flag 未被扩张，并验证 MI1–MI8 合同入口，结果为零错误。该检查只证明映射与启用门一致，不代替产品行为或阶段资格。

当前不足保持明确：整链测试还没有把 owner 身份、策略层 undo/redo、admission/中途/checkpoint/finish 失败、无新输入 drain 和资源压力放进同一个 fixture；通用 painter path、source-dependent current/self-copy、indirect/mask/LoD/wrap 仍在 BC5/BC8；BC9 默认启用门和同依赖 upstream/Fresh/正式性能继续开放。下一批围绕这些目标补联合断言，不重开已闭合的 selector、copy 或 packed/cursor 发布窗口。
