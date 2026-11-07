# 01h：稀疏 dab 范围与原页准入

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)。本篇细分 S03/MD2–MD3、联动 S02/SS5、S03/MR5、S10 和 V01；依据 [92 §9.1–§9.2、§9.5](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)。SR1–SR7 是同一原准入链的代码关系，不新增 writer、pending 或 job 权限表。

## 1. 为什么要改这一段

multi-dab 原先将 `applyRect ∩ 所有 dab 的总包围矩形` 传给 cursor operation。两个小 dab 相隔多页时，中间空白页也进入 reservation/execution 范围；包围框冲突会挡住实际页面独立的 worker。当前改为提交每个 `applyRect ∩ selectionBounds ∩ dabBounds`，在原 wrap/offset 适配后取相交页的并集。像素仍按原 dab 顺序处理，一次调用仍只有一个 operation/callback。

范围以**声明矩形相交的页**为粒度；不扫描透明像素、不按 mask 的非零像素猜测写权限，也不提供像素级越界保护。同一物理页内的不同像素仍共享该页准入，真正共页的 jobs 仍需排序。source/mask 当前要求不可变，完整 read footprint 不因这次改动自动具备。

当前定位为 `5173c807c87bb1619325249a07a8b4f4f8f09f09` 上的未提交工作树。本批 17 个 CPU/业务目标 × 双架构共 **7,006 passed、0 failed、0 skipped**，36 次继承探针通过；源码、库、测试二进制、定向场景与本轮增量均在[本批证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_sparse_ranges_20260928/README.md)归档，阶段判断仍只看 92。

<a id="sparse-range-map"></a>
## 2. 设计内容 → 代码段 → 联动责任

| 单元 / 关联修改 | 实际代码段 | 已实施关系 | 尚需修改 / 验收边界 |
|---|---|---|---|
| **SR1：一组声明，一次操作**；S03/MD3 | [公开多矩形声明](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.h:866) → [Device 多矩形入口](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1898) | 增加 `QVector<QRect>` 入口；单矩形旧 ABI 仍转入同一路径，普通空矩形保留无需构造列表的返回。显式 owner 的空集合仍需验证原目标/事务；callback 只执行一次 | 原 owner/target/context 寿命仍由调用者保证。多矩形不会授予 job 身份、源读取或提交权限；所有未迁移 ABI 仍保留原失败保证 |
| **SR2：沿原坐标适配**；S03/MD2、C02 | [普通 strategy](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:171)、[wrapped strategy](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:520) → [原坐标适配](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:280) | 普通路径保留原矩形组；wrapped 路径逐矩形使用原 `KisWrappedRect`，再统一 offset 到 manager-local。全部坐标先检查，再走原显式事务或 standalone 分支 | 不在 brush 复制另一套页面身份转换；后续调度几何必须与这个入口使用同一目标/上下文。offset/wrap/context 变化需在原安全边界协调，不能靠缓存矩形绕过复验 |
| **SR3：真实 painter 消费者**；S03/MD2–MD3 | [带 owner 的 multi-dab](/Users/apple/krita_gpu/krita/libs/image/kis_painter_blt_multi_fixed.cpp:169) → [实际范围消费者](/Users/apple/krita_gpu/krita/libs/image/kis_painter_blt_multi_fixed.cpp:215) | 原筛选 dab 时收集真实交集，替换总包围矩形声明；source 列表顺序、mask reader 捕获、局部 composite、opacity/flow 与原错误 sink 保持。生产 caller 不再传显式空 owner；显式 direct 开发入口经 painter 绑定消费原 transaction，正式工具绑定为空 | 不因范围缩小省略像素或降低显示工作。这里改的是本次写范围；复杂 read footprint、联合失败/drain 和默认启用继续 MD1/MD2/MD4/MD5、BC9/BC10 |
| **SR4：先合并页几何，再查询一次**；S02/SS5、S03/MR5、S10 | [Manager 准入入口](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1734)；[临时页几何并集](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1743) | 全部声明先转页坐标并检查兼容索引范围；在 manager 读锁外生成临时 `QRegion`。其不重叠页矩形供原锁内查询，每个目标页只查一次兼容 tile，将去重目标交给原 selector/admission/execution，权限仍由原 owner 授予 | 临时几何不是第二份 write set，也不持有 pending。范围列表、QRegion、QSet、wrapper/extent/dirty 和必要终结容量仍需完整 job 预算与准入；本批不授予零分配或实际 bytes 上限 |
| **SR5：空白页不能借包围框获得写权限**；S01、S03 | [原 BoundedCursor](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2051)；[越界与取消测试](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:687) | callback 改完第一页后移到未声明的中间页，原 cursor 拒绝；即使 callback 返回 true，operation 仍失败且不 fallback/replay，原事务拒绝提交并 abort 恢复 G0 | 这是页粒度边界。更广的异常、存储拒绝、晚 guard 和业务取消仍用原 S01/S09/S10 终结责任；不能把局部 bool 结果当完整应用恢复 |
| **SR6：范围与像素一起证明**；V01 | [范围与像素 oracle](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:557)、[真实 worker 并行](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:643)、[owner 拒绝](/Users/apple/krita_gpu/krita/libs/image/tests/kis_painter_test.cpp:1063) | 64 个四种 BPP × 四种 wrap 模式 × 镜像开关 × standalone/owner 用例，以逐像素独立映射得到期望页集合；旧包围矩形声明作为正控制，必须声明更多页。4 个并行 case 同时持有交错稀疏页；2 个写后越界 case 覆盖普通/wrapped；原拒绝测试补多矩形空/非空错误 owner | 正控制与页计数不替代实际 stroke 耗时、Fresh 控制、资源预算或所有插件覆盖。完整矩阵须绑定最终源码与 binary，不能仅引用定向总数 |
| **SR7：真正共页的下一段**；S02/SS5、S03/MD1–MD2 | [镜像 jobs](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:189)、[普通异步 producer](/Users/apple/krita_gpu/krita/plugins/paintops/defaultpaintops/brush/kis_brushop.cpp:230)、[当前 rect 分块](/Users/apple/krita_gpu/krita/libs/image/brushengine/kis_paintop_utils.cpp:75) | 稀疏范围批次时，producer 仍按像素 rect 分块；本批只去掉实际 dab 不相交页造成的假依赖。后续默认普通/镜像 jobs 已按 [S03 / PG1–PG8：页归属与真实 brush jobs](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01i_page_owned_brush_jobs.md#page-partition-map) 将同页归入同一 job；原 admission 继续复验并排斥真正重叠页 | 上述后续批次已覆盖默认 compositor 的非零 offset、镜像和 wrap 边缘；其他读写依赖仍需在真实 producer/原调度表达；独立页保持并行，重叠写和读写依赖保持语义次序。不能在 beginWrite 失败后重放 kernel，也不能默认退成整笔单线程 |

<a id="sparse-range-next"></a>
## 3. 继续实施的顺序

1. 默认 compositor 的页归属已按 [S03 / PG1–PG8：页归属与真实 brush jobs](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01i_page_owned_brush_jobs.md#page-partition-map) 实施；继续其他入口，让真实 producer 的任务范围与实际 compositor 声明一致；保留原 task/transaction 身份，在原调度中表达真正共享页的依赖。镜像阶段的几何必须对应镜像后的 dabs，不能拿之前的范围授权后面的写。
2. 联合完成 MD1/MD4/MD5 的静止 owner 初始化、current/G0/source、producer 最终输出、scheduler cut、finish/cancel。callback 内解析出的页集合不能倒过来充当已经排好序的完整 job footprint。
3. 将实际范围/索引/输出及必要终结存储接到原 job admission 与预算，验证 tiny-budget、长 stroke、压力切段和 drain。随后才默认启用持久 stroke，并按固定输入与最终 merge 端点取得性能证据。

本批只消除总包围框的虚假写范围，不改变 M6 → M7 → M8 → BR1-PERF 出口，也不调整 stroke → undo → 上下文切换的优先级。
