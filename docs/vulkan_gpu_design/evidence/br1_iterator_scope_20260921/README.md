# Iterator / planar read correctness checkpoint

本目录仅用于这轮生产读入口迁移的正确性证据，不授予核心重构或 M/K/X/E 性能完成资格。
开发中首次新增测试失败的日志保留为 `development-new-tests.log`：三个完成 history 的 fixture
未 purge 合法 memento，却错误要求所有 capability 都清零；四个 planar fixture 使用只在 `next()`
触发的 observer，却仅构造 timer，未实际注入发布。修正 fixture 端点及 planar 分段计量后重新验证。

曾试验新读开始时自动释放同线程 writer 的缓存。尽管已有 iterator 测试通过，该方式会撤销仍被业务
持有的裸写指针，已撤回，不能成为正式设计。当前显式保留活跃同线程 legacy writer 的重叠读兼容路径；
这条路径不是 immutable View，也不计入已迁移资格。新增 pointer-lifetime 回归检查读操作不会 seal writer。

## 最终范围

- CPU-only 与 Vulkan contract 构建成功；selection 插件重新编译，避免 direct iterator ABI 新旧混用。
- 最终 `verified-results.json`：14 套完整回归合计 **390 passed / 0 failed / 0 skipped**（含 init/cleanup）。
- paint-device 仅选定 planar、wrapped packed/random/H/V 及越界包裹七个槽，**9 passed**；不是全套产品测试。
- 四组各 40 次：并发提交、生产并发写、overlay 生命周期、iterator 生命周期，共 **160 次**额外运行。
  共 175 个进程运行，全部成功，无 SAFE ASSERT；开启并发或诊断时钟的结果不是性能样本。
- 新增 26 个场景覆盖固定 current/before、提交/abort/default、LRU 淘汰/重访、wrapped/repeat 重建、
  nextPixels stride、跨线程不读未完成写、活跃 writer 指针寿命及 planar 拆平面。generic helper 的移动/归还在既有槽补强。
- 架构检查通过；历史 D12 的 497 个封存文件、D11 的 539 个文件保持不变。

运行时使用 `QT_QPA_PLATFORM=offscreen`、源码 `_install` prefix 与当前 `_build-br0-cpu/bin` plugin path；
Vulkan contract 使用 `_build/bin`。loader 日志验证 image/shape/lcms 来自当前测试构建，不借用旧安装库通过测试。

从工作区根目录可运行：

```sh
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_iterator_scope_20260921/run-checkpoint.mjs another-label
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_iterator_scope_20260921/verify-checkpoint.mjs
```

runner 拒绝覆盖已存在报告/日志；封存 manifest 仅首次使用 `--capture`，随后默认验证。
当前默认验证 `verified-manifest.json`。较早的 `final-*` 完整通过记录及 `checkpoint-manifest.json` 保留，
随后复查增加了 observer/unregister 互斥和跨线程最终析构回归，因此旧 live manifest 自然失效。
新 `verified-*` 是重建后的全部矩阵重跑，不是只执行新增测试；两个版本的报告不混算。
这是 live correctness checkpoint：后续源码、二进制或文档改变会使 live hash 校验失效，不回写旧报告伪造新版本证据。
旧 overlay 检查点的 live hashes 已因本轮改动自然失效，其报告与原始日志不修改。

仍未完成：重叠读兼容分支和完整 brush/dab mutation、owner-issued in-place permit、完整短发布成本、
单页长历史/root reachability/同步 overlay token 释放、总回收背压及非 CPU 异步进度。整体性能测试留待结构结清之后。
