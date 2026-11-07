# CPU access cursor / page-block reconstruction

本轮将 CPU facade 的借用寿命分成默认 OperationSpans 与显式 CursorPage，RandomAccessor 使用后者。
native 当前 target/before-image 各至多一个 guard；固定 View、未发布 generation 与 writer reservation 不因换页结束。
generic 仅归还离开页的 before/read lease，所有未发布 write leases 保留至 finish/cancel。
完整范围见 [67 §14](../../67_br1_target_structure_reconstruction_20260920.md#14-2026-09-21accessor-游标寿命与区域页块遍历)。
本目录是正确性/结构检查点，不是核心重构结清或 M/K/X/E 性能资格。

## 最终结果

CPU-only/selection 插件与 Vulkan contract 构建完成后运行测试，不与构建并行。
`final-results.json` 的 14 套完整回归共 **456 passed / 0 failed / 0 skipped**（含 init/cleanup）：
Foundation 27、Reference 68、CpuMutation 110、ResidentRead 31、PhysicalClaim 30、Completion 11，
tiles3 pool/store/swapped/low-memory 3/5/4/4、tiled-manager 130、iterator 9、iterators_ng 11、Vulkan contract 13。
paint-device 选定 7 槽 **9 passed**；九组各 40 次、共 **360 次**额外重放，合计 **375 次运行**全部成功，无 SAFE ASSERT。
架构门禁通过，旧 D12 的 497 个与 D11 的 539 个封存文件保持不变；loader 验证 image/shape/lcms 来自 CPU build/bin。

## 核验内容

- CPU SurfaceOps 矩形读写按页块处理所有相交行；同页像素移动复用 accessor span，不重复调用 session/pin。
  native cursor 使用内联 write record，不重复建立 facade 的逐页 heap record/hash entry。
- 15 个新增场景覆盖 native/generic × seal/cancel、旧 View/default、真实换出恢复、failed-segment 不重放、
  1/4/16 BPP、跨正负页、行 padding、重叠 copy、正负坐标极限。默认全 span 的跨页指针继续有效。
- 地图级/总 dirty metadata 不声称常数空间；generic write lease 不能停驻，copy 仍有完整 source buffer。
  其他 tiles3 生产 iterator 与 brush 不因 facade 测试通过而被标记全部迁移。
- 开发负例保留：`development-build.log` 记录 lease move-assignment 被禁止，改用显式 release + optional/emplace；
  `development-cursor-tests.log` 的 1 失败来自错误要求 poisoned native segment 可继续写，现按失败回滚契约测试；
  `development-resident-full.log` 的 1 失败证明 generic before-image 的 native 探测多建 lazy bindings，
  已恢复 control 路径并保留原有断言，不把新增工作当成预热收益。

## 重放与边界

```sh
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_access_cursor_20260921/run-checkpoint.mjs final
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_access_cursor_20260921/verify-checkpoint.mjs
```

runner 使用 offscreen、源码 `_install` prefix 与匹配 build/bin 的插件；不与构建/链接并行。
保留完整 14 套与 selected paint-device 7 槽，再重放既有八组各 40 次及新增 access-cursor 40 次。
首次以 `--capture` 建立 live manifest，默认核验源代码、二进制/插件、文档链接和原始日志。
旧检查点不回写；后续编辑使旧 live hashes 失效，不使其历史日志变成新版本资格。
多线程、诊断与故障运行不能用于性能结论。owner permit、完整短发布、brush/重叠读、长历史/总回收背压、
GPU/I/O 进度仍未结清；完成目标结构后才冻结并测量主干 M、驻留 K、事实交接 X 和完整 E。
