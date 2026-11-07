# S06：生产共同安装区间与并发消费者

本批扩展现有诊断 timer，直接观测 `prepareWritePlanLocked` 的生产安装区间；增加真实 PageStore 在准备后和安装后的并发消费者验证。没有另建 selector、write set、generation owner 或测试专用 handoff 路径。阶段结论仍由 [92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:475)管理；修改关系见 [03a §12](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md:165)。

## 最终结果与身份

[checks-01](checks-01/manifest.json) 的 17 个目标 × 2 架构全部通过：**5,426 passed，0 failed / skipped**，每架构 2,713；[结果汇总](result-summary.json)已与原始日志对账。六项工具自测通过；[结构门](checks-01/architecture.log)为 1,522 indexed APIs / 15,075 call edges，未提高原 ratchet。

源码为 HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09` 加 [source.patch](checks-01/source.patch)，SHA-256 `e75930341f74f86a4433c3bbca2520a94cca5da803e5a0dfab7417bd55ffd185`，并非已提交 revision。最终 matrix 后源码未变。[identity](checks-01/identity.json)记录所有 binary、构建参数与 seed；image 库 SHA-256 为 `dabf503f24426fb599e68ae86a66c633f21c0e9d3d24e8805267ee697376502a`，UI 库保持上一批身份。

[arm64 joint-03](install-arm64-joint-03.log) 与 [x86_64 joint-final](install-x86_64-joint-final.log)各有 480 组配置、31,080 个区间；正常安装、物理拒绝、metadata revision 竞争各 10,360，均为 **0 allocations / 0 bytes / 0 frees**。两架构的正控制均观测到 4 次分配，probe 与矩阵 image 库哈希一致，详见 [allocator-summary](allocator-summary.json)。这是当前 CPU 子集指定安装区间的直接证据，不是 M6 全阶段或性能资格。

## 测量边界

`RecoverableInstall` 在 descriptor 实际存储准备完毕、physical claim 之前进入，`RecoverableInstalled` 在 metadata、physical retag、ledger、descriptor 消费完毕后进入；两点之间持有 owner gate，尚未暴露像素。安装被拒绝时，区间在 `RecoverableCleanup` 的入口结束；其后才在 gate 外销毁候选、解除未消费 claim 和释放 deferred storage。

探针调用真实 native preserve/payload/discard 与 generic preserve/discard 入口。每组使用已导入的 exact alternate，无临时 before copy；验证旧 handle 失效或保留、目标地址、物理 payload 数量、默认像素语义、旧 G 读取、提交/取消与 close。覆盖 1/4/8/16 BPP、1/64/65/129 页、两种终结，以及正常安装、native reader 抢先、generic reader 取得并释放后导致 metadata revision 过期三类情况。

准备、像素 kernel、adapter 返回、seal/publication、retirement、deferred cleanup 与整笔 operation 的耗时/分配不在这个区间。诊断关闭时，沿用既有 TLS 分支，不采时钟、不分配或写热原子；没有 handoff 候选的 Fresh 不进入这些新阶段。这不授予 Fresh 2% 或 stroke 性能资格。

## 并发矩阵

`productionHandoffConcurrentConsumers` 通过另一个线程与信号量，固定准备完成后和安装后两种顺序。它覆盖 native reader、generic lease、取得后立即释放的 generic reader、pending last-use、swap、新 provider owner、只保留 root 的 capture、B 的额外 reader，并另测 ledger 准备前的 swap。共 4 BPP × 2 adapters × 9 consumers × 2 orders = **144 个新增场景/架构**。

A 的访问或过期 revision 阻止安装并走 Fresh；纯 root capture 或 B reader 允许合法 handoff。ledger 分类 claim 准备后拒绝 A 的 domain move；准备前的 swap 可以成功，随后 handoff 准备失败并通过 Fresh 完成。安装后的 exact G 读 B，取消 T 不倒写 A。

## 保留失败与审查记录

- [arm64-concurrent-01](arm64-concurrent-01.log)：122 passed / 8 failed。fixture 错误要求已持 ledger class claim 的 A 仍能 swap；源码的 domain admission 正确拒绝了它。修正断言，并增加 ledger 准备前实际 swap 的独立场景。[arm64-concurrent-02](arm64-concurrent-02.log) 为 146 passed，含 init/cleanup。
- [joint-01 编译日志](probe-build-arm64-joint-01.log)：独立探针误用 cancel/abort/commit 签名，并缺少 backing usage 的完整定义；修正 harness 的调用与 include。
- [arm64 joint-02](install-arm64-joint-02.log)：只覆盖成功路径，10,360 个零分配/释放区间。随后扩展物理拒绝与 metadata revision 拒绝，没有用这个较窄样本替代完整结论。
- [六文件增量补丁](install-instrumentation-and-concurrency.patch) 与 [修改前重建核对](incremental-review.json)：从上一批 source patch 重建修改前文件并逐一匹配；全部匹配。完整源码快照与生成的 graph/baseline 由各 checks 目录保存。
- [ratchet 检查](ratchet-check.json)：原始约束未提高。既有 22 个 state ownership facts、21 个 manifest entries、16 个 runtime census groups 与 19 个 intrusion files 保持。

最终运行身份和结果由 allocator 汇总、checks-01 的 manifest/identity 与 result-summary 对账。新增诊断阶段与线程调度不改变已通过的 Fresh、提交/取消和业务终结测试。

## 未完成边界

legacy tile 的 ready 标记仍不含 expected identity，长期 TileData 引用仍保守排斥 handoff。本轮只审查了其 lifetime 和 raw consumer 关系，没有放宽 refs/users 检查，也没有声称完成缓存迁移。继续迁移须覆盖 detached tile、copy/compressor、解锁后缓存和已借出的 raw 指针，不能给每个 manager cache 永久保留整个 captured root 来替代这些关系。

M6 的各准备失败点、provider epoch/晚 completion 全矩阵、S09/S10 资源与关闭压力仍需补齐；M7 fence、M8 scope、undo/context、Vulkan/TSAN 和正式 BR1-PERF 未取得本批资格。当前 CPU 生产安装区间的零分配证据不能扩大为这些结论。
