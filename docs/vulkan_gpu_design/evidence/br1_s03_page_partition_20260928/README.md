# S03：真实 brush 页分区与透明源合成一致性

日期 2026-09-28；阶段入口 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)，修改内容与实际代码的关系见 [S03 / PG1–PG8：页归属与真实 brush jobs](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01i_page_owned_brush_jobs.md#page-partition-map)。

## 身份与完整验证

HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；含未跟踪生产/测试文件的源码差异 SHA-256 `1e7220d4a6188ef1e6f9ea7bd5f8ef1952269f2d97c4c5c9405d9c8a44f55cda`。最终 19 测试目标 × arm64/x86_64：**7,346 passed、0 failed、0 skipped**；实际 `kritadefaultpaintops` 插件构建通过。[完整 manifest](checks-02/manifest.json)、[源码及 image/pigment/插件/静态库/测试 identity](checks-02/identity.json)、[完整源码差异](checks-02/source.patch)、[绑定检查](evidence-scope.json)给出同源证据。最终构建 no work，结构门和六项工具自测通过。

[调用图](graph-02.log)：85 TUs / 1,788 APIs / 18,429 edges / 17 callbacks；[结构清单](baseline-02.log)：21 manifest / 25 ownership / 16 census / 19 intrusion；没有提高 ratchet。[36 次继承探针](probes-manifest-02.json)在本批 image/pigment 下重编译运行，身份见各 `install-*-final-02-identity.json` 与上述绑定检查；它们约束原底层分配/安装/借用/终结，不测新增 QRegion/QHash/clip 总成本。[本批代码增量](page-partition-code.patch)对照开始前快照。

## 已实施与新增覆盖

真实普通/镜像 producer 从实际 dab coverage 生成映射后页分区，保留原自适应 patch 大小、dirty rects 和镜像阶段屏障。每个 manager patch 对应一个并行 job，一个 job 可有多个画布 clips；dab 顺序在整个 job 内不变。原 cursor 映射被共同使用，未在 brush 复制页权限表；默认 owner 仍为空。

| 场景 | 新增数量/架构 | 证明 |
|---|---:|---|
| 透明源 SIMD lanes | 72 | RGBA8/U16/F32 × mask × opacity × 全透明/混合目标 alpha × 三种对齐；有效源 alpha 为零时逐字节保持目标，非零 lane 有实际变化，prefix/stride/padding 不越界 |
| 独立几何与像素 oracle | 64 | 1/4/8/16 BPP × 四 wrap × 四镜像；offset、负坐标、重复 coverage 与洞；128/320 patch 逐像素映射，不重不漏、页不共享；反序独立 jobs 的 OVER 像素、commit/undo/redo。整数精确；F32 有限且误差 ≤5e-6 |
| 原 owner 全组并行 | 4 | 所有 partition jobs 在真实线程上同时进入 PixelOperationBody 持有 execution；活跃 cut 拒绝，归还后像素和 abort 正确 |
| 拒绝与正控制 | 1 | 非法 patch/null 输出/overflow 拒绝且不替换结果；空输入成功；旧世界坐标相邻分块确实共享一页 |
| 实际 brush producer | 16 | 实际自动笔刷 dabs 与普通/水平/垂直/双镜像 jobs；四 wrap 模式。同阶段绘画 jobs 全部同时持有 execution，串行/并行且不同 offset 输出逐字节一致，producer drain、undo/redo |

合计每架构 157 个新 case（141 painter、16 producer）；完整目标还包括已有测试与 init/cleanup。输入 dab 生成使用原同步测试 executor，输出绘画 jobs 使用真实线程并遵守 producer 的阶段屏障；不是完整自由绘画 scheduler 压力或性能 replay。

## 失败保留与修订依据

[build-02](build-02.log)保留新 producer fixture 缺少 KisNode/KisImage 完整类型的构建错误；补 includes 后 [build-03](build-03.log)通过。[painter-focused-01](painter-focused-01.log)先通过 196 项。[producer-focused-01](producer-focused-01.log)为 5 passed / 13 failed：旧像素 patch 的空白部分生成空任务，使“每个绘画 job 都进入 body”的断言失败；改为实际 dab coverage 后，这一问题解决。测试仍保留全部 body 同时进入的断言。

[producer-focused-02](producer-focused-02.log)继续保留三处逐字节差异，诊断显示透明像素的隐藏 RGB 被写入，最大通道差 191。源码定位为 OVER SIMD 的全透明目标 shortcut；RGBA8 混合目标也需将零源 lane 的 NaN blend 变为零。修正 RGBA8 与 U16/F32 分支后，[producer-focused-03](producer-focused-03.log)18 passed；新增 72 个零 lane case 后 [painter-focused-02](painter-focused-02.log)268 passed。没有忽略透明 RGB、放宽原始字节比较或延长并发同步超时。

[graph-01](graph-01.log)保留调用图工具参数拼写错误；使用其支持的参数重新生成上述 graph-02。首轮[完整矩阵](checks-01/manifest.json)保留 x86_64 painter 的 48 处与 producer 的字节差异失败；[build-05](build-05.log)显示当时只重编译了 NEON64。AppleClang universal depfile 的最后架构跳过了其他 SIMD 实现的条件 includes，原 Ninja 依赖没有 OVER 头文件。已在 pigment 的 CMake 给所有 factory 变体加 compositor header 依赖；[六变体规则核对](universal-header-dependencies.json)、[build-08](build-08.log)、[x86 painter 定向 143 passed](painter-x86-focused-03.log)与 [x86 producer 定向 18 passed](producer-x86-focused-04.log)确认重新构建与执行。最终资格使用 checks-02 和 final-02 探针；首轮已通过的探针仍保留原身份，不能代替这轮重新绑定。

CMake 的 CONFIGURE_DEPENDS 需要实际执行 glob 检查；因此最终构建检查使用实际 Ninja 无工作构建，要求输出 no work 并复验源码及全部二进制哈希，不能用只计划 glob/重新配置的 dry-run 代替。定向日志不代替最终 identity。

## 待改范围

默认持久 owner、current/G0/source、producer 完整 cut 与显示读选择、必要存储/实际预算/压力窗口、其他读写依赖和 indirect/mask/LoD 均继续。临时几何不是权限，也未取得零分配、硬 bytes 或实际 stroke 性能资格。M6/M7/M8、Fresh 2%、Vulkan、TSAN 和 BR1-PERF 仍开放。

[文档校验](validation.json)检查 26 篇指南、15 个全局 ID、MD 的 33 个源码锚点、SR 的 17 个锚点、PG 的 20 个锚点、正反向文件映射和最终源码身份；该脚本本身不运行业务测试。[47 处旧链接重定位](source-link-remap.json)与[文档增量](guide-update.patch)保留修改过程。前批证据继续绑定各自源码。
