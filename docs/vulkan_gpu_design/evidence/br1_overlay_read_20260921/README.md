# BR1 sealed overlay / packed read 检查点（2026-09-21）

继续核心重构，**结构完成与性能资格均为 false**。实现与限制见 [67 §10](../../67_br1_target_structure_reconstruction_20260920.md#10-2026-09-21冻结-sealed-overlay-与生产-packed-读取)。
不修改前轮回收、提交准备、D13、D11/D12 原件；前轮 live manifest 的源码哈希不代表本轮。

## 验证

`run-checkpoint.mjs` 在构建完成后运行 14 套正确性测试和 120 次额外重放。
额外运行分别覆盖并发提交/overlay 捕获/晚到捕获，生产并发写，以及 overlay 的终态、默认 identity、删除未 seal 和通用回退寿命。
报告保存 binary、参数、环境、退出码、日志和 QtTest totals；totals 含 init/cleanup，不是独立业务场景数。
可传新的 run label 保留各次尝试，禁止覆盖已有日志/报告。第一次 `checkpoint` 全套已通过；随后补齐 API abort 注释与契约说明，
重新构建并用 `final` 标签全套重跑。最终 manifest 使用 `final-results.json` 与 `final-*`，两次原件均保留。

检查命令为 `node verify-checkpoint.mjs --capture`（只允许首次建档）及 `node verify-checkpoint.mjs`（核对当前文件）。
源码、二进制、插件运行库、全部设计 Markdown、构建/测试日志和运行报告均纳入 SHA-256；后续修改会使 live checkpoint 失效，不能回写旧哈希冒充本次测试。
最终 CPU/Vulkan 重建日志是 `cpu-build-api-doc.log` / `vulkan-build-api-doc.log`；架构门禁为 `architecture-checkpoint.log`。

最终 14 套合计 **364 passed / 0 failed / 0 skipped**，120 次额外重放全部成功，日志无 SAFE ASSERT。
其中 Foundation 26、Reference 68、CpuMutation 60、ResidentRead 31、PhysicalClaim 21、Completion 11；
tiles3 pool/store/swapped/low-memory 分别 3/5/4/4，tiled-manager 98，iterator 9、iterators_ng 11，Vulkan contract 13。
架构检查通过；D11/D12 archive-only 复验仍为 497 个封存文件、539 个前序 D11 原件未变。
这些都是正确性/结构检查，未执行正式 M/K/X/E，不授予 GPU/UMA 或全核心结构资格。

生产 packed read 测试覆盖负坐标、跨页/行、1/4/8/16 BPP、行 padding，以及两页之间发生 head 发布、history commit 或 abort。
断言一次捕获、驻留零 generic request、空白不注册页面、不物化；并对完整像素结果逐段比对。
状态机测试覆盖重复/外来 token、superseded/historical discard 拒绝、abort 转 Historical、最后 token 释放。
CPU mutation 用例还覆盖多捕获者、未 seal backing、facade 销毁、generic fallback、A→B→A 与 abort/restore 后默认 revision 不复用。

开发期发现：packed-read publication 测试最初有 1 个失败，overlay-commit 的 readRequests 增加 2；定位到嵌套 commitHistory 的默认页裁剪仍走 generic。
未放宽零请求断言，而是将裁剪也接入 captured resident read；不能将嵌套提交的请求归因为 packed read 内核。
编译期修正了 move-only lease 的不可赋值使用，以及 helper 重构时的错误作用域。开发工具输出不冒充最终冻结日志。

## 限制

本轮无正式采样、主干配对或 GPU/UMA 吞吐/延迟结论。阶段计时包含注入/并发，仅用于正确性。
完整 legacy iterator/planar/brush scope、owner-issued 原位 permit、完整发布临界区、overlay K 项同步释放与总队列背压继续开放。
最后回收/drain 仍计入最终 E；native 路径减少请求次数不自动等于主干性能等价。
