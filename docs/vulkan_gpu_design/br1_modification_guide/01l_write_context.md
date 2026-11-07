# 01l：从分区到执行的目标映射复验

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。本篇细分 **S03/C02/V01、BC3**，依据 [92 §9.1–§9.2、§12.3](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)。它解决“已经按旧 offset/wrap 分区的 job，不能按新映射写入”的具体缺口；不取代原 execution 准入、页权限或 scheduler 的生命周期责任。

## 当前实现与契约

`KisPaintDevice::WriteContext` 是在静止边界捕获的只读值：原 target、manager、color space、offset、time/LoD/frame、实际启用的 wrap 及其 border/axis。它仅保活原 device/manager，没有取得 immutable 像素快照、pin、mutation owner 或写权限。没有额外按页登记表。

原事务首次显式开启持久 mutation 时保存这个值，后续 apply（包括空范围）、checkpoint、重复 begin 和 commit 复验它。原 brush update 在 normalization/页分区前捕获一次，普通和镜像写 jobs 在合成前复验，最终 dirty/统计上报前再次复验。不匹配走原失败/取消链，不重分区后重放已接纳工作。

**这不是并发修改 device 元数据的锁。** 原 scheduler/caller 仍须使一次已通过复验的执行期间 target metadata 稳定；正在写入时并发改变 offset/wrap 仍不受支持。真实 painter owner 的寿命、source-dependent 读 footprint、完整 producer/cut 和资源仍归 [BC1–BC10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01j_real_stroke_integration.md#stroke-integration-map) 联合收口。

<a id="write-context-map"></a>
## 内容与待改代码的关系

| 单元 / 条款 | 当前代码与行为 | 联动及下一段责任 | 验收依据 |
|---|---|---|---|
| **WC1：捕获实际 target/mapping**；S03/C02 | [WriteContext 值类型](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.h:874)、[captureWriteContext](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1917)沿原 PaintDevice 取得目标和映射事实 | 仅由原事务或单次 update state 持有；不把它作为访问授权。color space/manager 保持原身份，device/manager 引用归还随原持有对象寿命 | 默认空值不匹配；等价 bounds 对象匹配。捕获/复验无 root capture、payload read 或页集合遍历 |
| **WC2：复验有效 wrap**；S03/C02 | [matches](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1936)比较 target/manager/layout、offset/time/LoD/frame，再比较 effective wrap；只有实际 wrapped 才比较 border/axis | 不能改为比较 bounds 对象地址，也不能让 inactive wrap 参数产生假拒绝；此值相等检查不宣称完成跨生命周期 ABA 或 concurrent metadata mutation 的控制 | offset X/Y、wrap support/mode/axis/border origin/size 都有拒绝；同值替换 bounds、inactive wrap 变化有成功对照 |
| **WC3：原事务静止准入**；S03 / §9.1 | [beginStrokeMutation](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp:187)首次成功准入才保存 context；[strokeMutationTargetIsCurrent](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp:173)结合原事务状态和 saved manager 复验 | 在 transaction 构造后、持久准入前的合法 offset 初始化仍允许；重复 begin 不重绑定已开启 stroke。原 transaction 继续是唯一 owner；默认业务启用仍需 BC1/BC2/BC9 | 原调用契约见 [transaction header](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.h:56)；变更映射后 apply/空范围/checkpoint/commit/rebegin 均拒绝，未进入像素 callback |
| **WC4：取消与普通移动不被锁死**；S01/S03 | [tryAbortTransaction](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp:264)仍使用 saved manager 和原 offset 恢复，不要求当前映射匹配。普通 transaction 未开启持久 scope 时保持原移动/undo 语义 | 不能把映射复验施加到取消入口或所有普通移动事务；重新恢复相同上下文后尚未终结的显式 scope 可继续，实际 owner/manager 仍复验 | [testStrokeMappingContext](/Users/apple/krita_gpu/krita/libs/image/tests/kis_transaction_test.cpp:60)覆盖 changed context 直接 abort、恢复后继续/commit、cut 前后 retained reader；[普通移动](/Users/apple/krita_gpu/krita/libs/image/tests/kis_transaction_test.cpp:127)覆盖 undo/redo |
| **WC5：真实 producer 捕获与写入**；S03 / §9.2 | [update 捕获](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:241)早于 dabs normalization/页分区；[普通/镜像写 job](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:180)共享该 context，写前检查 | 保留原并行页分区和镜像阶段屏障；不把每个 job 改成全局互斥。首条显式 direct 模式已把 BC2 painter 绑定与 target/mapping 复验一起送入 jobs；正式工具绑定为空，复杂模式和 BC10 失败仍开放 | [testBrushQueuedContext](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.cpp:772)先生成真实 jobs 再改映射/target/manager/time，像素 body 为零且失败不报成功 dirty |
| **WC6：绘画后到完成上报**；S01/S03 | [最终 report job](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:348)在 dirty/averageOpacity/性能统计之前复验，也停止已失败 job 的成功上报 | 已发生的目标写仍由原事务取消；拒绝不是“该 update 从未执行”，不能换 target 继续或 fallback 重放。原调度应完成整笔取消和 producer 析构清理 | late cases 先完成真实绘画 jobs、再改 offset/time，最终 job 拒绝且不新增成功 dirty；取消恢复原内容。稳定/等价 bounds 的最终上报保持成功 |
| **WC7：注册与真实构建**；V01 | [事务 slots](/Users/apple/krita_gpu/krita/libs/image/tests/kis_transaction_test.h)、[producer slots](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/tests/KisDabRenderingQueueTest.h)注册新增数据驱动用例，完整矩阵执行实际目标 | 正控制与拒绝、取消同测；最终源码须同时绑定 image、实际 paintops 插件/静态库与测试，不能只引用旧身份。性能比较仍须包含每 job 复验成本 | [本批验证记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_write_context_20260928/README.md)记录完整矩阵、失败保留、继承探针及源码身份 |
| **WC8：尚需联合接线**；S03/S04/S10/C02 | BC3 的映射值复验已实施，BC1/BC2/BC5–BC9 继续：原 owner/job 寿命、current/source、完整 cut、终结、真实资源/压力 | 执行期间 metadata 稳定必须由原 scheduler 保证；source/selection/painter 设置的稳定不由 target WriteContext 自动证明。不能把它当迁移资格、权限 token 或默认持久 brush 开关 | 默认长 stroke、完整 M6/M7/M8 和 BR1-PERF 仍由 92 验收；本批不新增这些完成资格 |

原子/锁/预算归属保持原 owner 不变。新增值只在 transaction/update state 中常数存储、按 job 复验，不增加每页快照或遍历；这不等同于整笔零开销或全部元数据已经完成 S10 计账。阶段和性能优先级仍为 stroke → undo → context。
