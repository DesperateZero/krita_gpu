# Write claim / semantic revival reconstruction

本目录记录本轮写侧核心结构补强；不授予结构完成或 M/K/X/E 性能资格。
按 PageKey 的 owner-gated claim 覆盖 provider 准备、request、lease 与 seal/cancel；
删除后的页面不能在准备期间提前恢复可见。实现边界见 [67 §12](../../67_br1_target_structure_reconstruction_20260920.md#12-2026-09-21写准备-claim-与语义-seal-一致性)。

## 最终验证范围

- CPU-only、selection 插件及 Vulkan contract 重新构建。新增 session stats 改变了按值返回结构布局，
  不能用旧测试二进制配新 image 库；最终测试均在构建结束后运行。
- `verified-results.json`：14 套完整回归，合计 **414 passed / 0 failed / 0 skipped**（含 init/cleanup）。
  Foundation 27、Reference 68、CpuMutation 83、ResidentRead 31、PhysicalClaim 21、Completion 11，
  tiles3 pool/store/swapped/low-memory 3/5/4/4、tiled-manager 124、iterator 9、iterators_ng 11、Vulkan contract 13。
- paint-device 仅选定 packed/planar/wrapped 的 7 个槽，**9 passed**，不冒称完整产品套件通过。
- 并发提交、生产并发写、overlay 生命周期、iterator 生命周期、write-claim 生命周期五组各重放 40 次，
  共 **200 次**额外运行；连同完整套件/选定槽，共 **215 个进程运行**，全部成功、无 SAFE ASSERT。
- 相对前轮增加 24 个数据场景：generic 删除后写的 7 种终结、adoption 成功/失败与 default 变化的 4 种组合、
  无关请求量的 6 种组合、真实线程暂停的 6 种组合、1 个状态机测试（内部覆盖 Reserved/Writable/Prepared）。
  既有 request/lease/commit 测试同步加强 claim 与 surface 契约断言。
- 架构门禁通过；旧 D12 497 个封存文件与 D11 539 个文件校验保持不变。

## 保留的反证与修复

| 开发日志 | 失败含义与修复 |
|---|---|
| `development-claims-tests.log`（5 failed） | 另一 exact version 存在 writer/Prepared 时，removed/default 的 generic read 被错误拒绝。允许独立 immutable historical default 共存，仍禁止相同 identity/物理 slot，且不改变 head/writer。 |
| `development-adoption-default-failure.log`（1 failed） | staged default 改变后，adoption 使用旧 before descriptor 拒绝合法 seed。整页 payload 改用当前 surface overlay 契约。 |
| `development-metadata-race-negative.log`（6 failed） | provider 在真实线程中暂停时，同一事务仍可修改 default。generic/adoption 准备、request/lease 及 terminal release 现冻结本事务 surface 契约；不同页事务仍可提交。 |

`checkpoint-*` 保留第一轮 413 Qt totals / 215 次运行的通过记录；之后将无效 completion 和真实失败 completion
拆为两个场景，并补齐公开 API 的生命周期约束。最终 `verified-*` 为重建后的全部矩阵重跑，不混算两个版本的通过数。
运行环境使用 offscreen、源码 `_install` prefix 与当前构建 `bin` plugin path；loader 检查 image/shape/lcms 都来自当前 CPU 构建。

## 校验与边界

```sh
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_write_claims_20260921/run-checkpoint.mjs another-label
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_write_claims_20260921/verify-checkpoint.mjs
```

runner 拒绝覆盖已有日志/报告。manifest 只首次以 `--capture` 生成；默认验证 `verified-manifest.json`，
绑定源文件、实际库/测试/插件、设计文档及本轮原始证据。它是 live correctness checkpoint，不是独立封存源码：
后续编辑自然使 live hashes 失效，不回写历史结果。上一轮 iterator/overlay live hashes 因本轮修改失效，其原始证据未修改。

计数只证明首写/删除冲突判定不扫描全局 request/active-write map；不证明完整写路径为 O(1)、无全局锁或已具有原位 permit。
metadata 历史 H、abort、owner 等待、proof/commit、合法保留与退休各有成本。仍须推进真实 brush/dab mutation/重叠读、
owner-issued permit、完整短发布、session pin 预算、单页长历史/root reachability/总队列背压及 GPU/I/O 进度。
并发/故障注入日志不是性能样本；结构结清后再冻结同义主干 M、驻留 K、实际交接 X、完整操作 E。
