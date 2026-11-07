# 01k：固定源合成与 1px sharpness 同步分支

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。本篇细分 **S01/S03/S04/V01、BC4/BC5**，把同步消费者的改动与待接业务责任列在一起。设计依据为 [92 §9.1、§9.3–§9.5、§14](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)；优先级保持 stroke → undo → 上下文切换。

## 当前实现边界

单个 fixed source 的 `bltFixed` 已改为原目标 cursor 合成，去掉整矩形目标和 selection 的读回、临时缓冲与再次 `writeBytes`。它和 multi-dab 共用 span kernel，并保留调用者的 opacity、averageOpacity、flow、lastOpacity 和通道设置。`bitBlt`、标量 `bltFixed`、multi-dab 及 PaintDevice-source `renderMirrorMask` 都通过一个 painter 非拥有绑定同步借用原 transaction；未绑定时仍走原 standalone 语义。为测试引入的 public 显式 owner overload 已删除，owner 参数只保留在 painter private implementation helper 内部。

实际 `KisBrushOp::paintLine` 的 1px sharpness 分支因调用这些入口而消费新 cursor；显式 direct 开发入口会由原 strategy 在 jobs 生存期绑定同一 owner，正式工具默认仍未启用该持久 scope。**同步消费者能力已经接通，真实 stroke 的默认启用仍受 BC9 资源与进度门约束。** 不给 painter 增加第二个自持事务，也不把借用 owner 放进自持 `d->transaction`。

以下条目是当前代码关系；验证及失败保留见[本批证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_fixed_cursor_20260928/README.md)。完整状态只由 92 维护。

<a id="fixed-cursor-map"></a>
## 内容—代码—验收关系

| 单元 / 条款 | 主改代码与已实施行为 | 联动 / 尚需修改 | 验收落点 |
|---|---|---|---|
| **FC1：原 cursor 消费固定源**；S03 / §9.1 | [标量 bltFixed](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:1006)保留旧 wrapper，经 `applyPixelOperation` 取得目标 current pending；[接口](/Users/apple/krita_gpu/krita/libs/image/kis_painter.h:303)仅在调用期间借用 owner | 目标授权仍由原事务/manager/execution 给出；默认 brush 原 owner 传递继续由 BC1–BC3 完成。不能把一个合成入口迁移算成全 stroke 迁移 | [testFixedCursor](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:186)：四种 BPP、standalone/commit/abort、mask、wrap、OVER/COPY/ALPHA_DARKEN 与原平面合成 oracle；连续两次操作检查 pending |
| **FC2：局部参数与 source view**；S03 / §9.1 | [applyDevice](/Users/apple/krita_gpu/krita/libs/image/kis_painter_blt_multi_fixed.cpp:18)、[applyDeviceWithSelection](/Users/apple/krita_gpu/krita/libs/image/kis_painter_blt_multi_fixed.cpp:88)、[私有签名](/Users/apple/krita_gpu/krita/libs/image/kis_painter_p.h:83)接受 source subrect 和是否取 dab 参数；原 scalar 参数逐调用复制，不写共享 composite cache | 源行距仍取完整 fixed bounds；source view 与目标坐标分开，避免用虚构 dab origin 做极端坐标减法。默认 multi-dab 仍取各 dab 的参数；source immutable 保证由调用者提供 | 非零 source bounds、subrect、部分通道、非单位 opacity/flow；[边界坐标与拒绝](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:307)使用合法 manager-local 坐标和极端 world offset |
| **FC3：wrap 首周期与顺序**；S03 / §9.1 | [writeRect 限制](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:1018)按实际启用的 wrap 轴截取首周期；沿原 PaintDevice mapper 处理 offset/seam | 原 [wrapped writeBytes](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:609)只消费首个周期；不能把 repeated 映射逐次合成，也不能换成末次样本。此约束属于标量 fixed 的旧语义，不强加给原 multi-dab/bitBlt 的其他规则。排队到执行的映射复验现见 [WC1–WC8：目标映射复验](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01l_write_context.md#write-context-map)，执行期间稳定仍归 BC3 | fixed 测试源宽高均超过 wrap period；负坐标、offset、四种 wrap，对照 [legacyFixedBlit](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:80)原 read/compose/write 算法 |
| **FC4：1px 独立 source 与镜像链**；S03/S04 / §9.1、§9.4 | [bitBltImpl](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:682)在 painter 已绑定 owner 时禁用 bypass fast copy，拒绝同 manager source；[PaintDevice mirror](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:3040)准备源 fixed buffer，再由 [mirror impl](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:2965)将同一 owner 传到各 scalar 写入，保留 H→HV→V 次序 | [KisBrushOp::paintLine](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:411)的线缓存仍是独立 source。开发入口已经由 BC2 原 strategy 绑定接通；同 target source/current sampler/self-copy 需 BC5 明确读意图后迁移，当前不支持 | [testSharpnessMirrorOwner](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:277)覆盖 repeated pending、四镜像/四 wrap/mask、checkpoint/undo；实际 producer 见 FC7 |
| **FC5：捕获、失败与原 owner 终结**；S01/S04 / §9.3–§9.4 | source/selection const accessor 在 callback 前捕获；错 owner 与同 manager source 在 body 前拒绝；合成失败上报原 job，不记成功 dirty、不重放。当前失败恢复仍由原 transaction / operation 负责 | 保持 BC7 的唯一 finish/cancel 责任；显式裸指针仅作同步借用，异步任务必须由原调度保活，不能直接捕获它替代寿命契约。准备/快照的实际容量和首字节后保证仍要经过 BC9 | [snapshots](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:991)在 body 时改变源/selection 仍读 operation-start；[cancellation](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:868)第一页真实写后暂停，活跃 abort 拒绝、下一页不写、重试恢复 G0 |
| **FC6：Alpha Darken 分块一致性**；S03/V01 / §14 | [calculateAlpha](/Users/apple/krita_gpu/krita/libs/pigment/compositeops/KoOptimizedCompositeOpAlphaDarken128.h:28)由 SIMD 与 scalar edge 共用；统一先归一化 source alpha 再乘 mask，并统一 alpha 插值运算 | U16/F32 共同模板覆盖 hard/creamy 类型；测试覆盖实际运行配置，不声称所有 ISA/配置已穷尽。继续保持 [全部 factory 头依赖](/Users/apple/krita_gpu/krita/libs/pigment/CMakeLists.txt)，避免 universal build 只重编某个 ISA。scalar edge 的成本仍需性能对照 | [testAlphaDarkenSpanInvariant](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:142)：U16/F32、mask、两种 average 分支、flow，宽块与 1/3/17/64 spans、三种对齐、两遍合成；U16 exact，F32 有限且误差 ≤5e-6 |
| **FC7：实际同步 producer 与重复准备**；V01 / §8.1、§14 | [testSharpnessLine](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.cpp:717)调用真实 1px sharpness `paintLine`，确认异步 update 无 jobs，像素对照旧镜像算法并验证 undo/redo；[testFixedCursorReuse](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:251)验证同段 D=1/10/1000 | 实际 producer fixture 与绑定 owner fixture 分别验证；联合 FreehandStrokeStrategy 的多 update、display cut、取消和 drain 已在 BC10 闭合，默认启用仍缺 BC9 资源/进度与 pen-up 性能门 | 32 producer cases/架构；同段两页 provider prepare 始终 2、seal 0；完整 freeze 后再写累计 4，retained reader 保持原像素。因果计数不等于吞吐结论 |
| **FC8：剩余迁移与默认启用**；S03/S04/S10 / §9.1–§9.5 | [BC1–BC10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01j_real_stroke_integration.md#stroke-integration-map)继续作为联合领取入口；[带 fixed selection 的 blt](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:1056)与其他通用路径不因本批自动取得持久能力 | 下一批明确整笔入口资格 → 原 owner/context/job → current/G0/source → producer cut/dirty 接续 → finish/cancel → 必要资源与压力；mask/indirect/LoD 各实际 target 有各自原 scope。未迁移分支须在 scope 启用前选定模式，不在半笔后 fallback | 原同步分支正确性只是 BC4 子项；业务启用需要 BC1–BC9 联合证据，M6/M7/M8 与 BR1-PERF 仍按 92 独立验收 |

测试入口在 [painter slots](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.h:31) 与 [producer slots](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.h:18) 注册；完整矩阵逐个执行两个测试目标，不由测试函数存在推定覆盖。

## 本批结论如何使用

固定源新路径消除了整块目标读回和拷回；这是代码结构与因果计数结论，尚无整笔绘画时间收益资格。未绑定的 public 入口仍按独立 operation 终结，只有 painter 已绑定原 owner 时才跨调用复用 pending。source/selection 的选择不授予读取目标 live pending 的权限。

Alpha Darken 的旧 scalar/SIMD 运算本身存在舍入次序差异，换分块会暴露 U16 单位级差值。本批统一其运算后检验不同分块一致；oracle 使用同一修正后的 composite。**不能据此宣称修正前所有图像逐字节不变**，也不能将 F32 容差套用到整数或忽略透明 RGB。真实视觉/性能 replay 仍属于 FC7/BC10 的后续责任。

后续修改此处，至少同时核对 FC1–FC6 的 source view、wrap、参数、快照和失败语义，再核对 BC 的 scope/读/调度/终结。默认启用必须保持原显示频率、镜像屏障与 completed-work 统计，不通过减少可见工作获得性能。
