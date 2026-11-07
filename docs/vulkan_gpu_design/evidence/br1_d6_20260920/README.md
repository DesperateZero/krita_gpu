# D6 completion 布局切片证据

报告：[60](../../60_br1_completion_coverage_and_sparse_terminal_status_20260920.md)。这是 CPU 分支内组件/操作诊断，不是正式 upstream M/K/E、尾分位或 GPU/UMA 资格。

## 版本与来源

- `before`：D5生产代码加冷诊断 API、非法终态修复和共同新测试，仍逐 ticket QHash。
- `after`：相邻同状态区间，交替终态变慢约2.807倍；`after-tail`：单调尾部优化，交替终态仍有RSS回归。
- `after-sparse`：当前完成覆盖 + 非成功稀疏表，保留精确状态和pending gap。各目录保存源码、测试、CMake cache、
  tracked-image patch、untracked-image tar及库身份；base为`f5fbbde618df6fb4e1068ace7381c339a70dd4c0`加已有dirty tree。
  源码切片不是整个依赖包。临时库/executable副本位于`/tmp/br1-d6-runtime.9ZNmdJ/`，系统清理后需从源码快照重建。
- 所有 paired 测量均运行共同 before executable，按DYLD选择对应完整Krita库副本，loader日志核验实际image路径；
  driver开始/结束复验所列库hash。相同Qt6.8、universal构建/arm64执行、RelWithDebInfo、Mac16,10及CPU-only profile。
  正式性能运行串行，不与构建/回归并发；功能回归计时不用于性能结论。

## 测量链

- `registry-paired/`：原4,194,304次协议，首个after区间92.324 ms，按100ms门槛停止；保留`protocol-v1-short-window.json`。
- `registry-paired-v2/`、`registry-tail-paired/`、`registry-sparse-paired/`：三候选各64次配对，固定8,388,608次，四桶各8对。
  `run-v1.mjs`对应初版，`run-v2.mjs`对应tail，当前`run.mjs`对应sparse；实际hash随manifest保存。
- `tiles-tail-paired/`、`tiles-sparse-paired/`：两候选各80次配对，五桶各8对，独立200ms完成吞吐，不是单次延迟。
- `memory-tail/`、`memory-sparse/`：两种状态分布各2对，固定相同操作数的全进程RSS/CPU诊断。Apple保护的time进程之后
  用env参数设置DYLD并核验loader，避免环境变量被系统过滤而装错库。`memory-v1.mjs`对应tail，`memory.mjs`对应sparse。
- component计时排除setup/statistics/destruction；外层time诊断包含它们，但不等于provider/root/后台drain。
  记录数含非空inline prefix、覆盖区间和非成功entry，不是字节；RSS包含整个进程，不推导每record内存。
- 第一次CMake配置曾因误将两个测试源码放进单个`kis_add_test`失败，改为独立target后重建成功；不是测试失败或测量样本。

## 复算与重跑

```sh
node docs/vulkan_gpu_design/evidence/br1_d6_20260920/analyze.mjs docs/vulkan_gpu_design/evidence/br1_d6_20260920/registry-sparse-paired/manifest.json /tmp/new-d6-registry-analysis.json
node docs/vulkan_gpu_design/evidence/br1_d6_20260920/analyze.mjs docs/vulkan_gpu_design/evidence/br1_d6_20260920/tiles-sparse-paired/manifest.json /tmp/new-d6-tiles-analysis.json
node docs/vulkan_gpu_design/evidence/br1_d6_20260920/run.mjs registry /tmp/new-d6-registry after-sparse
node docs/vulkan_gpu_design/evidence/br1_d6_20260920/run.mjs tiles /tmp/new-d6-tiles after-sparse
node docs/vulkan_gpu_design/evidence/br1_d6_20260920/memory.mjs /tmp/new-d6-memory after-sparse
```

工具拒绝覆盖输出；重建后不能用新库冒充历史身份。paired CI是进程pair的探索性bootstrap，不是已冻结不劣性判据。
registry的部分/全套测试分版本保留；CPU/Vulkan最终回归另存`*-sparse.log`/`vulkan-regression.log`，不能把中间候选通过
替代最终候选验证。后续切片另建证据目录，不覆盖本轮原件。

最终相关回归：registry 11、Foundation 24、Reference 42、tiled-manager 88、共享fixture 34、Vulkan contracts 13 passed，
静态架构检查通过；不代表完整产品/长压/真实GPU性能。`artifacts.sha256`固定交付文件（不含自身），复算校验各manifest的
日志、真实完成量、scope、记录数和版本身份；两种中间候选的反证原件仍保留。`verification.json`记录五份分析逐字节复算、
352次完整配对、16次内存诊断、当前源码/库身份及63份文档425个本地链接的核对结果。
