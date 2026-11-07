# S03：稀疏 dab 页范围与原准入

日期：2026-09-28。阶段判断见 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)，设计内容与待改代码的关系见 [S03 / SR1–SR7：稀疏写范围](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01h_sparse_write_footprints.md#sparse-range-map)。本批将真实 multi-dab 的总包围矩形声明改为实际交集的页并集，去掉无 dab 覆盖的空白页占用；没有默认启用持久 brush owner。

## 身份与完整验证

HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含未跟踪生产/测试文件的源码差异 SHA-256 `422ae24b2e8aa084e34fa3965c744ae0a1f722949a482c57140c39d2833fb1b7`。

最终 17 目标 × arm64/x86_64：**7,006 passed、0 failed、0 skipped**。见 [完整 manifest](checks-01/manifest.json)、[源码/库/测试二进制 identity](checks-01/identity.json)、[完整源码差异](checks-01/source.patch)、[绑定检查](evidence-scope.json)。最终构建 no work，结构门和六项工具自测通过。[调用图](graph-01.log)为 85 TUs / 1,788 APIs / 18,427 edges / 17 callbacks；[结构清单](baseline-01.log)为 21 manifest / 25 ownership / 16 census / 19 intrusion；ratchet 未放宽。

[36 次继承探针](probes-manifest-01.json)在本批源码/image 下重新构建并通过，身份见各 `install-*-final-01-identity.json` 与上述绑定检查。它们保留底层安装/存储/准入/execution/checkpoint/刷新约束，不是新增范围列表/QRegion 的完整 allocator 或端到端性能证明。[本批代码增量](sparse-ranges-code.patch)对照开始前的 8 文件快照。

## 改动与测试

PaintDevice 的三参数多矩形 overload 复用原坐标适配器和显式 owner/standalone 分支，旧单矩形 API 与空操作快捷返回保留。multi-dab 按原筛选顺序声明实际交集，一次 callback 按原顺序执行所有 dabs。manager 在锁外合并声明页几何，锁内对每个目标页查询一次兼容 tile，原 owner/selector/admission/execution 继续承担权限和生命周期。

| 新增场景 | 数量/架构 | 证明范围 |
|---|---:|---|
| 独立范围与像素 oracle | 64 | 1/4/8/16 BPP × 无/水平/垂直/双轴 wrap × 镜像开关 × standalone/owner；非零 offset、负坐标、裁切与重复声明；独立逐像素映射和整窗口逐字节比较；checkpoint、commit、undo/redo |
| 旧包围矩形正控制 | 上述 64 内 | 同输入的旧单矩形声明必须占用更多页，实际声明页数等于独立 oracle 的不同页数，避免用零计数或失效探针证明优化 |
| 真实 worker 稀疏并行 | 4 | 无/有 wrap × 无/有水平镜像；包围框重叠、实际两组页交错但独立，两个 worker 同时持有原 owner 的 execution；活跃时 cut 拒绝，归还后像素与 abort 正确 |
| 写后空白页越界 | 2 | 普通/wrapped；改完第一页后访问中间未声明页，cursor 拒绝；callback 的 true 不掩盖失败，commit 拒绝，abort 恢复 G0 |

共 70 个新 case/架构；原 owner 拒绝 case 另补多矩形空/非空输入，不重复计数。范围权限是页粒度，页内像素 clipping 仍由原 compositor 负责，未按透明值或 mask 非零值推测权限。

[build-01](build-01.log)与 [focused-01](kis_painter_test-focused-01.log)先通过 127 项（70 个新增、55 个上一批 case、init/cleanup）。加入旧包围矩形正控制后 [build-02](build-02.log)、[focused-02](kis_painter_test-focused-02.log)通过 72 项（70 个新增、init/cleanup）。随后保留单空矩形快捷返回并完成 [build-03](build-03.log)及最终完整矩阵；最终源码资格以完整矩阵身份为准。本批没有失败的构建或测试；继承测试私有 composite 的显示名 warning 不影响断言。

## 待改边界与导航

下一段必须在真实 producer 与原调度内表达映射后实际共享页的次序，覆盖 offset/wrap/mirror；独立页保持并行，不以冲突后重放 kernel 或整笔串行替代正确接线。默认持久 owner/current 读/producer cut、必要存储与压力预算仍联动 MD1/MD2/MD4/MD5/MD6。临时矩形列表、QRegion、QSet 和适配输出未取得完整 job 预算/零分配资格。完整 M6/M7/M8、实际 brush 性能、Fresh 2%、Vulkan、TSAN 与 BR1-PERF 继续开放。

[导航与符号校验](validation.json)检查 25 篇指南、15 个全局 ID、MD1–MD7 的 33 个源码锚点、SR1–SR7 的 17 个锚点、正反向文件映射及最终矩阵源码身份；该脚本本身不运行业务测试。[行号重定位记录](source-link-remap.json)保留 70 处原链接修订，[文档增量](guide-update.patch)对照本批开始前快照。前批证据保留各自的源码身份。
