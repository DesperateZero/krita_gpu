# S06 前置：缓存 binding 的 expected physical identity

本批对应 [03a 的 S06.1](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md)，阶段裁决仍在 [92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:475)。只验证 binding 访问身份，不授予 recoverable handoff、commit-only handoff 或 BR1-PERF 资格。

## 改动与消费者

`KisCpuResidentBinding` 构造时保存 provider-minted `KisReplicaAllocationIdentity`。读、写、parked writer reservation 和 retire 都要求 expected identity，在原有 binding mutex 内先验证 provider、epoch、slot、allocation generation，之后才修改 reader/writer/retired 状态或取得字节指针；不保留无身份参数的重载。

PageStore native read 与 native writer reservation、provider generic access、同步 copy、transfer 和 retire 全部传入对应 handle 的身份。Tiles3 的普通分配、alias 导入、initial tile 导入及测试 CPU provider 均在创建 binding 时给出身份。测试中跨后续写操作使用的 pin 保存自己的原始 identity，避免用 provider 的“最后分配”测试字段代替 holder 的凭据。

当前 tag 固定于构造，没有 retag/claim API。新校验不是真实 ABA/retag 的通过证据；失配后的读选择重建、legacy tile cache 与 raw pin 排斥、独立恢复 retention、预备 transition 和物理复用仍待实施。Stable binding 的元数据驻留与预算属于 S10 后续闭环，本批没有取得其资源或性能资格。

## 最终同源码矩阵

最终运行 [checks-01](checks-01/manifest.json)：17 目标 × arm64/x86_64，共 **3,494 passed，0 failed / skipped**；每架构 1,747 passed。新增 `cachedBindingRequiresExactIdentity` 为每架构 60 行：1/4/8/16 BPP × 5 类错误身份 × 空闲/read pin/parked writer。检查错误 token 不取得访问、不撤销合法 holder、不退休正确 backing，释放 holder 后合法读写及退休仍正常。

完整 matrix 保留 painter、transaction、scheduler、manager、原 H/V/random iterator 和 PageStore 既有控制用例。PhysicalClaimTest 每架构共 74 passed；错误 token 用例不能替代真实 retag 后的旧 view/cache 与两种并发次序测试。

结构门：21 manifest entries、21 ownership facts、16 runtime census groups、1,479 indexed APIs、13,967 reverse-call edges、19 external intrusion files；6 项调用图工具自测通过。原始 ratchet 与上批 clear 累计源码一致，未修改 reviewed ceilings 或 ownership manifest。最终 dry-run 无待构建内容，矩阵期间源代码未改变。

## 源码、复现与增量审查

- HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。
- 最终完整 [source.patch](checks-01/source.patch) SHA-256：`9e05527a67686bc5de7322c8bd8ea02bf48020d4f16589e1a7fbfc297f992cbf`；包含累计改动、新源文件与生成的审计输入，不是单独本批 patch。
- [identity.json](checks-01/identity.json) 记录 CMake/compile_commands、image/UI dylib 和全部测试 binary 哈希及环境；[manifest.json](checks-01/manifest.json) 记录逐命令/时间/返回值/日志；[result-summary.json](result-summary.json) 汇总结果。
- [binding-implementation.patch](binding-implementation.patch) 和 [incremental-review.json](incremental-review.json) 只显示相对上一累计 clear 批次的 8 文件实现/测试差异，不包含生成清单；复现使用完整 source.patch。
- [ratchet-check.json](ratchet-check.json) 比较上一累计补丁中的实际 inventory；[source-anchor-remap.json](source-anchor-remap.json) 记录旧指南源码定位的迁移。
- `build-01.log`、`arm64-targeted-physical-01.log`、`callgraph-01.log`、`architecture-checkpoint-01.log` 为定向构建/测试及清单准备日志；最终资格来源为 checks-01，不以预检代替矩阵。

在对应源码工作树中运行 `python3 docs/vulkan_gpu_design/evidence/br1_s06_binding_20260927/run_checks.py checks-02` 可创建新目录复验；脚本拒绝覆盖已有运行。结构输入应与实际源码相符；不能通过忽略结构失败继续宣称通过。运行环境为 offscreen，seed 12345，Vulkan 关闭的 `_build-br0-cpu` 双架构构建。

本批未重新执行 Vulkan foundation、TSAN、publication install allocator、产品 freehand replay 或性能门。身份比较的热路径成本未取得 2% 不劣性结论。M6/M7/M8、剩余指南条目与 BR1-PERF 继续开放。
