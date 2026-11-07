# S03：原事务与真实 brush jobs 的目标映射复验

日期 2026-09-28；设计与阶段状态入口为 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)。内容—函数—caller—终结—验收关系见 [WC1–WC8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01l_write_context.md#write-context-map)，业务联合出口继续由 [BC1–BC10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01j_real_stroke_integration.md#stroke-integration-map) 定位。

## 当前实现

原 PaintDevice 提供 `WriteContext` 值快照，保存实际 target/manager/layout、offset/time/LoD/frame、effective wrap 的 border/axis。原持久事务在静止准入时捕获，后续 apply（含空范围）、重复 begin、checkpoint、commit 均复验；初次准入前的 offset 初始化仍合法，普通位移事务行为不变。abort 继续通过 saved manager 和原 offset 完成，不因上下文变化而锁死。

真实 brush update 在 normalization/分区前捕获一次，普通/镜像写 job 合成前复验，最终 dirty/averageOpacity/性能统计上报前再次复验。变化则上报原失败链，不写入新映射，不重分区重放。已失败 job 不上报成功。time/LoD 在访问可能惰性创建当前 manager 的接口前检查，避免已知过期 job 再创建无关 LoD 存储。

该值不拥有像素快照、pin、页面权限或独立 mutation；只按原 transaction/update 生命周期保活 device/manager。它是边界复验，**不支持在一次已通过复验的执行期间并发改变 metadata**。原 scheduler 仍负责这个稳定区间、painter/source 设置和异步寿命。

## 新增覆盖

| 用例 | 每架构数量 | 验证内容 |
|---|---:|---|
| 持久 transaction mapping | 40 | 十种变化/对照 × 直接 abort 或恢复后 commit × 有无 checkpoint；offset X/Y、wrap support/mode/axis/border origin/size 拒绝；等价 bounds、inactive wrap 和准入前 offset 变化成功。拒绝不进 body，空范围也复验，重复 begin 不重绑定；直接取消、undo/redo 与 retained reader 保持正确 |
| 普通移动事务 | 1 | 未启用持久 scope 的 move/commit/undo/redo 保持合法 |
| 真实 producer 已排队 jobs | 22 | 十一种变化/对照 × 无镜像或双镜像；offset/support/mode/axis/border/time、painter 目标替换、实际 clone/layout 引起的 manager 变化在目标写前拒绝；稳定、等价 bounds、inactive wrap 成功 |
| 绘画后、完成上报前 | 8 | 稳定/offset/time/等价 bounds × 无镜像或双镜像；先证明实际像素已写、worker 尚未报告 dirty，再改变上下文；最终 job 失败不新增成功 dirty，原事务取消回到起点；两个稳定对照正常完成 |

合计 **71 个新增 case/架构**。早期定向 [transaction-focused-01](transaction-focused-01.log)为 43 passed、[producer-focused-02](producer-focused-02.log)为 32 passed（各含 init/cleanup）；最终同源码完整矩阵另行冻结，不以定向通过代替它。

## 构建与失败保留

[build-01](build-01.log)保留 producer fixture 调用只有声明、无链接实现的 `setDataManager` 失败；fixture 改用实际 `prepareClone` 加不同 layout 来切换 manager，并断言 manager 确实变化，没有给生产代码补测试专用 setter。[build-02](build-02.log)、[build-03](build-03.log)分别记录修正后的构建。

[producer-focused-01](producer-focused-01.log)为 24 passed / 8 failed：late fixture 错误期待绘画 worker 已报告 dirty。原 multi-dab 将报告交给最后的顺序 job；修订测试为同时验证实际目标像素已存在、此时 dirty 仍为空，再验证最终上报的成功/拒绝。没有删掉 late 场景，也没有降低“已写入后取消”的要求。[build-04](build-04.log)、[build-05](build-05.log)保留修订及 time/LoD 提前复验的重新构建。

[调用图](graph-01.log)为 86 TUs / 1,788 APIs / 18,440 edges / 17 callbacks；[结构基线](baseline-01.log)为 181 个 dirty source/build files、21 manifest / 25 ownership / 16 census / 19 intrusion。结构门与布局门未放宽。

HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含未跟踪生产/测试文件的源码差异 SHA-256 `e8618e8cce3069b5196f3aa9d8199803c7d495bb6372a879551190f591619009`。最终 19 目标 × arm64/x86_64 为 **8,238 passed、0 failed、0 skipped**，实际笔刷插件、结构门和六项工具自测通过。[manifest](checks-01/manifest.json)、[源码/库/插件/静态库/测试身份](checks-01/identity.json)、[完整源码差异](checks-01/source.patch)、[最终实际 no-op 构建](checks-01/final-build-no-op.log)给出同源证据。[36 次继承探针](probes-manifest-01.json)已全部通过，与矩阵使用同一最终 image/pigment；[绑定复验](evidence-scope.json)检查全部源码/二进制哈希，[本批九文件增量](write-context-code.patch)对照实施前快照。探针仅证明各自既有底层区间，未测整笔 target 复验开销或证明新增值的全部 S10 计账。

## 剩余边界

本批关闭 BC3 中“排队到执行的映射值未复验”这一缺口；执行期间稳定、scope/job 身份与寿命、source/current 读依赖、producer 完整 cut、dirty 拒绝接续、finish/cancel、整 job 必要资源与压力窗口继续联合实施。默认真实笔刷仍未传持久 owner。context 是常数级值，不是每页权限表；其引用保活和复验成本仍须进入整笔性能与 S10 容量评估。

没有新增默认长 stroke、完整 M6/M7/M8、Fresh 2%、产品 stroke replay、Vulkan、TSAN 或 BR1-PERF 完成资格。优先级保持 stroke → undo → context。

[指南验证](validation.json)核对全部 29 篇指南、15 个全局 ID、WC/FC/BC 单元、源码锚点及反向索引；[旧链接重定位](source-link-remap.json)、[文档差异](guide-update.patch)保留修改过程。旧证据与失败日志不覆盖、不改写。
