# Writable reservation / residency reconstruction

本轮将未发布 writer reservation 与 guard 的物理 RAM pin 分离。保留生成版本及写排他，
释放 guard 不 seal、不开放读者，也不改变旧 span 的有效期。范围见 [67 §13](../../67_br1_target_structure_reconstruction_20260920.md#13-2026-09-21未发布-writer-预约与-ram-驻留分离)。
本目录只记录正确性与结构证据；不是核心重构完成或 M/K/X/E 性能资格。

## 最终范围

- CPU-only、selection 插件、Vulkan contract 构建通过；公开 mutation stats 和诊断 recorder 布局改变，
  所有本轮运行的依赖二进制均重新构建，测试不与链接并行。
- `final-results.json` 的 14 套完整回归共 **441 passed / 0 failed / 0 skipped**（Qt totals 含 init/cleanup）：
  Foundation 27、Reference 68、CpuMutation 95、ResidentRead 31、PhysicalClaim 30、Completion 11，
  tiles3 pool/store/swapped/low-memory 3/5/4/4、tiled-manager 130、iterator 9、iterators_ng 11、Vulkan contract 13。
- paint-device 选定 packed/planar/wrapped 7 个槽，**9 passed**；不是完整产品套件。
- 八组各 40 次：并发提交、生产并发写、overlay 生命周期、iterator 生命周期、write-claim、writable-residency、
  parked-binding、生产 writeBytes pin 工作集，共 **320 次**重放。连同完整套件和选定槽，共 **335 次运行**，全部成功，无 SAFE ASSERT。
- 相对上一轮新增 27 个数据场景：CPU mutation 12、binding 9、生产 writeBytes 6；原 seed budget-failure 用例改为
  验证独立 mutable 准备不消费 seed，后续 adoption/retirement 正好消费/释放一次。
- 架构门禁通过；旧 D12 的 497 个封存文件、D11 的 539 个文件保持不变。

## 关键证据与边界

- 64 个 dirty 页顺序访问时目标 writable pin 峰值 1；保留 64 个 guard 时峰值 64，旧指针保持有效。
  生产 `writeBytes` 修改 2/32/256 页、1/4 BPP 时目标 writable pin 峰值均为 1，包含读回及 undo/redo。
  这些计数不包含 source/oldData/额外 legacy pin；不是总 dirty metadata、总 backing 或进程 RAM 的 O(1) 上界。
- 1/4/8/16 BPP 的实际换出/恢复测试保持同一 pending generation、同一 COW 次数和旧 View；parked 页 seal/cancel 不强制恢复 payload。
  双线程在 64 个 pinned/parked 周期交错，另一线程的 native/generic read、copy、retire 始终被拒绝。
  另覆盖 transfer/preclone 排他、reservation move、provider revoke/destruction、仍借出指针的寿命。
- `write_writable_pin` 与 `write_pending_materialize` 分开记录。后者只在真实 NonResident 后走 owner gate 外的
  tiles3 同步 swap 控制路径；不是异步 GPU/I/O materialization 已完成，也不是跨域 payload 计数。
- `development-mutation-tests.log` 保留首次 8 个失败：初版只构造 materialize timer，没有触发仅在 `next()` 调用的 observer，
  因而测试的恢复事件计数为零。拆分 pin/materialize 阶段后，完整测试同时验证恢复内容与 owner-unlocked 交错。
- `development-seed-alias-negative.log` 保留 native/generic 两个真实反证：旧 mutable `prepareWrite` 消费 adoption seed，
  目标 default 初始化读到 seed 内容，违背独立 backing 契约。现在普通 allocator 不再有 seed-alias 分支；
  完整 payload 的零复制 alias 仅由明确的 adoption 接口消费，失败由原 caller discard。

`verified-*` 是较早完整通过的 440 Qt totals / 335 次运行；之后增加双线程 parked/pinned 交错回归，
最终 `final-*` 为重建后的完整矩阵重跑，不混算两个版本。当前 loader 验证 image/shape/lcms 来自 CPU 构建目录。
使用 offscreen、源码 `_install` prefix 和当前 build/bin 插件路径，Vulkan contract 使用 `_build/bin`。

## 校验

```sh
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_writable_residency_20260921/run-checkpoint.mjs another-label
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_writable_residency_20260921/verify-checkpoint.mjs
```

runner 拒绝覆盖已有报告/日志；首次以 `--capture` 建立 `final-manifest.json`，默认验证源码、二进制/插件、文档及原始证据。
这是 live correctness checkpoint，后续编辑自然使 hashes 失效；旧 write-claim/iterator 检查点不修改，不回写其结果伪装成新源码资格。
多线程、诊断与故障运行均非性能样本。仍未结清全 span session/legacy 借用工作集、brush/dab/重叠读边界、owner 原位 permit、
完整短发布、长历史/总回收背压与 GPU/I/O 进度；结构完成后才重新冻结并测试 M/K/X/E。
