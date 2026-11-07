# 01i：按映射页归属组织真实笔刷 jobs

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。本篇细分 S03/MD2–MD3、SR7，联动 S02/SS5、S01、S10、V01。PG1–PG8 是原业务链的代码关系，阶段与设计判断仍以 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)为准。

## 1. 当前修改与边界

原 `splitDabsIntoRects` 按画布坐标分块。设备 offset、镜像和 wrap 的页边缘会使像素上分开的 rects 共享 manager 页；只缩小 dab 的声明范围不能解决这种真实共页。当前保留原自适应 patch 大小和 dirty 上报，用原 PaintDevice cursor 的映射将实际 dab 覆盖区域分配到 manager patch。patch 边长是原 tile 边长的整数倍；每一页只属于一个并行 job。一个 job 可以含多个画布 clip，并在这些 clip 上按原 dab 次序运行一次 operation。

普通、水平、垂直与双镜像的阶段继续由原 SEQUENTIAL 屏障串接；同一阶段内不同页组并行。此处解决不可变 dab 输入的默认笔刷 compositor 分区，不给任意 source-dependent、跨 store 或第三方 jobs 自动授予读写独立性。生产 caller 已删除显式空 owner：首条显式 direct 开发入口从 painter 绑定取得原 transaction；正式工具绑定为空，保留独立 operation 的终结保证。复杂 current/source 读、联合失败/drain、资源与压力接线继续。

本批 19 个测试目标 × 双架构共 **7,346 passed、0 failed、0 skipped**，36 次继承探针通过。源码、image/pigment/实际插件/测试二进制、失败保留和证据范围见[本批证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_page_partition_20260928/README.md)；未提交工作树以源码 SHA 和运行二进制共同定位。

<a id="page-partition-map"></a>
## 2. 修改内容 → 代码段 → 联动责任

| 单元 | 实际代码段 | 已实施行为与不变量 | 剩余责任 |
|---|---|---|---|
| **PG1：复用同一坐标映射** | [原 cursor 映射](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:18)、[共享 wrap span 边界](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:41) | partition 与实际 cursor 使用同一 offset/wrap/axis 转换和 seam 边界；常规与 wrapped strategy 选原上下文 | 调度到执行期间 target/frame/LoD/offset/wrap 必须保持稳定。几何不冻结上下文，也不替代原事务复验 |
| **PG2：每页一个并行 job** | [公开几何接口](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.h:901) → [入口校验](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1951) → [原 strategy 分区](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:226) | 先取画布矩形并集，在 wrap seam 与 manager patch 边界切分，再把映射到相同 patch 的 source clips 归为一个 job。输入像素不重复不遗漏；不同 jobs 的页集合互斥；负坐标按 floor 对齐；失败不替换调用方输出 | QRegion/QHash/clip 输出都是派生几何，不持 writer 或 pending；完整容量准入、实际计账与异常路径继续 MD6/S10 |
| **PG3：真实普通 producer** | [保留自适应 patch 大小](/Users/apple/krita_gpu/krita/libs/image/brushengine/kis_paintop_utils.cpp:81)、[真实 job 构造入口](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:169)、[异步 producer](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:230) | 原分块结果继续用于 patch 大小/dirty；实际 dab 覆盖单独用于 write jobs，避免 gap 产生空任务。最终 clips 在 job 创建时按值捕获；owner 由 painter 绑定解析，显式 direct 开发入口为原 transaction，默认工具为空；不缩减被接纳 dabs | 原更新节奏、完成端点和 dirty 保留。继续同 MR5/S04 联合验证复杂读、失败、drain 与资源门 |
| **PG4：镜像后重新分区** | [镜像阶段](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:189) | 按既有顺序镜像 dab 像素；相应 write coverage 同步镜像后再分区。前后的原 SEQUENTIAL jobs 保证普通绘画 → 镜像输入变换 → 镜像绘画的次序，不让旧对齐假设传到新阶段 | 输入生成与阶段屏障仍属原 scheduler。不能把几何 cache 或新辅助表当作另一个 writer owner |
| **PG5：多 clip 一次 operation** | [多 clip 合成接口](/Users/apple/krita_gpu/krita/libs/image/kis_painter.h:323) → [有序合成实现](/Users/apple/krita_gpu/krita/libs/image/kis_painter_blt_multi_fixed.cpp:175) | caller 提供 pairwise-disjoint 的画布 clips；selection bounds 先裁切，实际 dab 交集交给原准入，callback 内 dab 在外、clip 在内。每 job 一次 operation，source/mask 捕获和错误 sink 沿原责任链 | 公共单 rect ABI 保留。vector clips 不授予跨 job current reader、终结或持久 owner；未知 source-dependent 操作继续原保证 |
| **PG6：透明源不能因 SIMD 邻居写入** | [RGBA8 OVER 向量分支](/Users/apple/krita_gpu/krita/libs/pigment/compositeops/KoOptimizedCompositeOpOver32.h:81)、[RGBA16/F32 OVER 向量分支](/Users/apple/krita_gpu/krita/libs/pigment/compositeops/KoOptimizedCompositeOpOver128.h:102)、[通用构建头文件依赖](/Users/apple/krita_gpu/krita/libs/pigment/CMakeLists.txt:10) | 真实 producer 的逐字节对照揭示：混合 source alpha 的 SIMD 组曾将完全透明的 source lane 也复制到透明目标，改变隐藏 RGB；scalar lane 则不写。通用构建另补 compositor headers 的显式依赖，防止被最后架构 depfile 漏掉的 x86 变体继续使用旧对象。现对有效 source alpha 为零的 lane 选择零 blend，保留目标字节，并在 RGBA8 混合目标分支排除 NaN blend | 这是保证分块变化不改变原始像素的必要修正。不能通过忽略透明 RGB 或放宽精度断言掩盖差异。其他 composite 与非有限浮点输入不由此自动覆盖 |
| **PG7：独立 oracle 与真实 producer** | [72 组透明 lane 测试](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:345)、[64 组几何/像素 oracle](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:397)、[4 组全部 borrow 并行](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:498)、[拒绝与旧分块正控制](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:528)、[16 组真实 brush producer](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.cpp:629) | 单位层逐像素独立 floor/mod oracle 验证 disjoint pages、完整覆盖和反序 jobs 下的 OVER 像素/undo。真实 producer 使用真实自动笔刷与普通/镜像 jobs；生成输入同步，绘画 jobs 在真实线程上同阶段全部持有 execution，再放行；与串行且不同 offset 的结果逐字节一致 | 真实 producer fixture 尚非完整 FreehandStrokeStrategy/scheduler 压力或性能 replay。没有用相同实现生成像素期望替代单位 oracle；两个层次必须保留 |
| **PG8：下一段联合启用** | [1px sharpness 同步旁路](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:411)；[MD1/MD4–MD6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01g_multi_dab_and_painter_scope.md#multi-dab-map)、[HS1–HS8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01f_history_owned_mutation_scope.md#history-scope-map) | 此前 SR7 的真实默认 compositor 页冲突已通过“同页归一个 job”收敛，跨镜像阶段继续原次序；1px sharpness 与 async jobs 已在受限显式 direct 模式共用原 transaction 绑定；同一 Buildup direct strategy fixture 已证明多 update 的一个 undo 单元、递归无输入 drain，以及 admission/像素失败信号/checkpoint/finish 的唯一 cancel 终点 | 下一步直接闭合 BC9 必要存储、预算与进度。全局 job 读写依赖、其他插件、selection/indirect/mask/wrap/LoD 和压力窗口仍继续；这些完成前正式工具不调用 opt-in setter |

<a id="page-partition-next"></a>
## 3. 后续修改顺序

PG8 的具体待改函数、联动消费者与完成判据现见 [BC1–BC10：真实 stroke 联合接线](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01j_real_stroke_integration.md#stroke-integration-map)；其中 BC4 单列 1px sharpness，BC6/BC7 联合显示 cut 与终结，BC8 单列 masking 的目标差异。

先把该 producer 的实际 jobs 接入原 strategy/transaction 的持久生命周期与明确读意图；checkpoint 必须等本轮所有必要 mirror/merge 子任务完成后才发 dirty 给外部 reader。默认启用以前，把范围/索引/输出/取消存储接入原 admission 与硬预算，并补真实 scheduler、完整生命周期和压力验证。随后按 92 的固定输入与可见端点测 stroke；undo、上下文切换保持第二、第三优先级。

本批不改变 M6 → M7 → M8 → BR1-PERF 的出口，不以局部并行或 SIMD 修复直接宣称 stroke 提速。

固定源 cursor 的下一批验证又暴露 Alpha Darken 的 scalar/SIMD 舍入边界，修正与独立 span 对照见 [FC1–FC8：固定源与 sharpness](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01k_fixed_source_and_sharpness.md#fixed-cursor-map)。原 OVER 透明 lane 结论仍保留；当前两种合成修正及全部 SIMD factory 需绑定最终同源码二进制，不能混用旧矩阵。

原事务与真实 producer 的 target/mapping 复验已由 [WC1–WC8：目标映射复验](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01l_write_context.md#write-context-map) 接线；它是值快照，既不授予页权限，也不支持在已借用执行期间并发修改 device 元数据。恢复相同映射后的继续与直接取消分别验证；剩余 BC 原 owner/读/cut/资源继续。
