# S03：固定源 cursor 与 sharpness 同步消费者

日期 2026-09-28；阶段判断见 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)。内容到代码与后续责任见 [FC1–FC8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01k_fixed_source_and_sharpness.md#fixed-cursor-map)，真实业务联合接线见 [BC1–BC10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01j_real_stroke_integration.md#stroke-integration-map)。

## 身份与验证范围

HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含未跟踪生产/测试文件的最终源码差异 SHA-256 `15a00c31cf4b8d1037b73ade9d0e5831b231b42a2aeafa4f4cc7971346f1aec7`。19 目标 × arm64/x86_64 完整矩阵为 **8,096 passed、0 failed、0 skipped**，实际笔刷插件也完成构建。[manifest](checks-01/manifest.json)、[源码/库/插件/静态库/测试身份](checks-01/identity.json)、[完整差异](checks-01/source.patch)与[最终 no-op 构建](checks-01/final-build-no-op.log)绑定同一工作树。

[结构门](checks-01/architecture.log)、[六项工具自测](checks-01/reachability-self-tests.log)通过。[最终调用图](graph-04.log)为 86 TUs / 1,788 APIs / 18,436 edges / 17 callbacks；[结构基线核对](baseline-02.log)为 181 个 dirty source/build files、21 manifest / 25 ownership / 16 census / 19 intrusion。没有放宽 ratchet 或布局门。

[36 次继承资源/分配探针](probes-manifest-01.json)已全部通过，均以本批 image/pigment 重新编译运行；[源码/二进制绑定复验](evidence-scope.json)核对矩阵、探针和当前文件哈希。[本批九文件代码差异](fixed-cursor-code.patch)对照修改前快照，保留完整矩阵所对应的其余工作树。探针约束各自既有底层区间，不测 scalar fixed 全路径或整笔 stroke 性能。

## 本批修改及测试

标量 fixed 合成原先读取整块目标与 selection，分配缓冲、合成后再次写回；现在直接通过原 cursor 消费当前目标并复用 multi-dab span helper。source subrect 与目标 origin 分开，源行距保留完整 bounds；调用参数局部复制。wrap 只消费首周期，保持旧 writeBytes 的实际语义，避免映射回同页后重复合成。旧公开入口保留默认 standalone 行为。

新增 bitBlt、scalar fixed 与 PaintDevice mirror 的显式同步 transaction overload；独立 source 和 selection 在 operation body 前取得 const 读选择。显式 owner 的同 manager source 被拒绝，不混淆 source-dependent/current 读。mirror 保留 H→HV→V 次序，每次目标写用同一原 owner。默认真实 1px sharpness 已消费新 scalar 实现，但业务尚未传入持久 owner。

| 新增验证 | 每架构数量 | 证明与限制 |
|---|---:|---|
| fixed cursor oracle | 288 | 1/4/8/16 BPP × standalone/commit/abort × mask × 四 wrap × OVER/COPY/ALPHA_DARKEN；非零 source bounds/subrect、device offset、重复操作、部分通道；源宽高超过 wrap period。旧平面 read/compose/write 算法作对照，整数 exact、F32 有限且 ≤5e-6 |
| 重复准备 | 3 | D=1/10/1000，同段两页 prepare=2、seal=0；freeze 后再次写两页累计 prepare=4，旧 retained reader 保持不变 |
| 显式 owner 与 sharpness mirror | 32 | 四 wrap × 四镜像 × mask；连续目标 pending、checkpoint、undo/redo；独立 source + 原镜像算法对照 |
| 拒绝/边界 | 1 | wrong owner、同 manager bitBlt/mirror 在 body 前拒绝；极端 world offset 配合合法 manager-local 页检查 source view 不溢出 |
| 第一页写后取消 | 1 | 实际 copy kernel 写后暂停；活跃 abort 拒绝但标记取消，后续页不再进 kernel；原 owner 重试恢复 G0 |
| operation-start 快照 | 2 | body observer 改变 selection 或 source，固定/设备 source 合成仍消费操作前输入 |
| Alpha Darken span invariant | 16 | U16/F32 × mask × average 两分支 × flow；宽块与 1/3/17/64 spans、三种对齐、重复两遍，padding 不变 |
| 实际 1px producer | 32 | 实际自动笔刷/sharpness/paintLine，四 wrap × 四镜像 × mask；确认 update 无异步 jobs，旧镜像算法对照及 undo/redo |

合计新增 **375 cases/架构**（343 painter、32 producer），完整矩阵包含既有测试及 init/cleanup。实际 producer 与显式 owner 是不同 fixture；尚未验证完整 freehand 的 sync/async 交错、display cut、压力和资源全链。

Alpha Darken 的 U16 舍入差异在跨 span 后暴露。修正先归一化 source alpha 再应用 mask，由同一 ISA alpha helper 执行 scalar edge 与 vector 的插值；没有全局关闭 SIMD，没有放宽整数或透明 RGB 比较。此修正会统一旧路径中原本不一致的结果，oracle 使用修正后的 composite，**不代表所有修正前像素逐字节不变**。实际吞吐、scalar edge 成本与产品视觉 replay 仍待补。

## 保留的失败与收敛过程

[build-01](build-01.log)、[build-02](build-02.log)、[build-03](build-03.log)保留新 include/测试 fixture 的编译问题，分别修正不完整类型、registry/phase 名称和 QSharedPointer 构造。后续构建均单独记录。

[painter-focused-01](painter-focused-01.log)的 wrong owner 用例用空 source，source 裁剪合法地成为 no-op；fixture 改为实际非空源，保留生产 no-op 行为。[painter-focused-02](painter-focused-02.log)记录 18 个 U16 Alpha Darken 差异；统一 source alpha 归一化顺序后仍有差异，进一步以 [span 对照](alpha-diagnostic-01.log)收敛到 alpha 舍入运算。[alpha-focused-01](alpha-focused-01.log)、[painter-arm64-focused-03](painter-arm64-focused-03.log)保留中间失败。共用 alpha helper 后 [alpha-focused-02](alpha-focused-02.log)为 306 passed；最终资格由完整矩阵覆盖，早期 x86 定向通过不替代最终二进制身份。

[edge-focused-01](edge-focused-01.log)最初把极端 world 坐标作为 manager-local 坐标，触发原合法 tile 范围限制；fixture 改为先移动 device，维持极端 world origin 与合法 local 页。[edge-focused-02](edge-focused-02.log)为 3 passed。[baseline-01](baseline-01.log)保留测试源码变动后的 stale graph 拒绝；重新生成 graph-04，再运行 baseline-02 和完整结构门通过。没有放宽生产坐标限制或调用图检查。

## 剩余责任

默认持久 stroke 的原 owner/context/job、offset/wrap 生命周期、current/G0/self-source、producer 完整 cut 与 dirty 接续、finish/cancel、整 job 实际存储/共享预算/压力窗口，及 fixed-selection/path/indirect/mask/LoD 继续按 BC/FC8 联合实施。临时 source mirror buffer 仍存在；整路径零分配、真实 stroke 时间收益、Fresh 2%、Vulkan、TSAN、完整 M6/M7/M8 与 BR1-PERF 均未新增资格。

[指南检查](validation.json)核对 28 篇指南、15 个全局 ID、FC/BC 单元、正反向索引和最终源码；[旧源码链接重定位](source-link-remap.json)、[本批文档差异](guide-update.patch)保留目录维护过程。旧证据不重写、不挪用为新源码资格。
