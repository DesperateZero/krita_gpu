# D7 captured-read 证据

报告：[61](../../61_br1_captured_read_scope_and_integration_cost_20260920.md)。这是捕获一致性修正和分支内诊断，**不是 native
pixel guard 或管理/产品性能通过**。完整 generic session 的明显慢化与原生写小幅反向偏移均保留。

## 冻结来源

- before 使用 [D6 after-sparse identity](../br1_d6_20260920/after-sparse/identity.json) 的不可变 library，未改 D6 证据。
- `identity.json` 固定 after runtime、两侧全部 Krita dylib、公共兼容 fixture 和主要源码 SHA256；`source/` 保存 14 个源文件。
  `tracked-image.patch`、`untracked-image.tar.gz` 相对记录的 dirty-tree base 保存 image 变更，`CMakeCache.txt` 保存 CPU 构建配置。
  这不是完整依赖包；临时 dylib 被系统清理后须重建，不能用新库冒充旧 hash。
- PageStore 单指针与原有 SessionStats ABI 保持；`KisPageStoreReadBaselineTest` 不引用新 captured API，实际 loader 日志核对 D6/new。
  component 才调用新 API，始终使用同一 new binary/library。
- `d6-coherence-counterexample.log` 记录同一 session 中途 commit 后混合值；`history-release-counterexample.log` 记录初版 64 次
  短 scope 多扫 1024 页。后者是当时失败测试原件，不是一个另行保存 binary 的性能版本；修复与最终回归由源码/报告说明。

## 测量与复算

`protocol.json` 在测量前冻结三组 bucket/8 pairs/200 ms。component 和 integration 各 96 次，native 48 次，另有 6 次
loader 短检查；功能反例不参与统计。计时串行，无 profiler；component 是 identity API 比较，integration 稳定 head 才具备
双方相同输出，不能把旧库并发一致性失败当作可回退的产品路径。native 复用原生 tiles3 fixture，不是新的 upstream 对照。

```sh
node docs/vulkan_gpu_design/evidence/br1_d7_20260920/analyze.mjs docs/vulkan_gpu_design/evidence/br1_d7_20260920/component-paired/manifest.json /tmp/new-d7-component.json
node docs/vulkan_gpu_design/evidence/br1_d7_20260920/analyze.mjs docs/vulkan_gpu_design/evidence/br1_d7_20260920/integration-paired/manifest.json /tmp/new-d7-integration.json
node docs/vulkan_gpu_design/evidence/br1_d7_20260920/analyze.mjs docs/vulkan_gpu_design/evidence/br1_d7_20260920/native-paired/manifest.json /tmp/new-d7-native.json
node docs/vulkan_gpu_design/evidence/br1_d7_20260920/run.mjs component /tmp/new-d7-component-run
node docs/vulkan_gpu_design/evidence/br1_d7_20260920/run.mjs integration /tmp/new-d7-integration-run
node docs/vulkan_gpu_design/evidence/br1_d7_20260920/run.mjs native /tmp/new-d7-native-run
```

工具拒绝覆盖输出并在开始/结束检查身份。报告 throughput 与 process CPU/完成量，不伪造单操作延迟；history release/close
单列但不宣称全进程/后台 drain。配对 bootstrap 是探索性，不是不劣性验收。缺少 upstream M、完整 tail、GPU/UMA 资格。

`*-final.log` 为最终代码回归：Reference59/read9/Foundation24/tiled88/native34/Vulkan13；`architecture.log` 为静态门禁。
早期 build/regression 和两个失败原件保留。`verification.json` 与 `artifacts.sha256` 固定最终复算、完整矩阵和文件校验结果；
后续优化另建切片证据，不修改这些样本以消除回归。
