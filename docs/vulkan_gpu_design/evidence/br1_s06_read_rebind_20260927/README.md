# S06.2：captured read 的有界 exact version 重解析

阶段裁决在 [92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:475)，代码关系在 [03a §9](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md:123)。本批接通真实 captured read 的失配处理，并联合验证已有 metadata、physical、ledger 和读选择原语。生产 handoff selector、legacy cache 迁移和独立 before 的生产保活仍未接通，不授予 M6/M7/M8、Vulkan、TSAN 或性能资格。

## 改动与责任

`KisCapturedReadView::readResidentPageImpl` 从 retained view 解析一次 exact version，先查已有 link 并尝试 pin；仅 InvalidIdentity / Retired 触发冷重解析。初次尝试加最多两次立即重解析，总共不超过三次；Busy、NonResident 和其他拒绝保留原语义。有无 status 输出指针使用同一判定，不切到新 current，不因失败进行 generic replay。

冷查找移入既有 `KisPageReadCoordinator::discoverCpuReadBinding`。它条件移除失败的 link，优先复用并发已安装的替代，再按原 version 查合法 CPU replica 和 provider。metadata 的 `removeCpuReadBinding` 新增 expected link 条件：旧 A 不能删除替代 B，旧 B link 也不能删除同 handle 的新 B link。退休调用者保留按完整 replica 移除的原用途。cache 对象身份不代替 allocation generation，后者仍在 binding 局部 gate 验证。

没有新 generation owner、write set 或 selector。热缓存成功路径不新增 provider lookup；新增循环的实际延迟仍须经过正式性能比较，不能由调用次数直接推断。ownership 清单只补充既有读协调职责，数量不变。

## 验证范围

ResidentReadTest 每架构新增 160 个 case，定向 arm64 运行 [arm64-resident-03](arm64-resident-03.log) 为 **193 passed / 0 failed / 0 skipped**：

- 128 个真实 captured-view case：1/4/8/16 BPP × 八种失配/拒绝 × try/wait × status/null。覆盖一次错误 binding、一次/持续 InvalidIdentity 或 Retired、持续错误 binding、Busy 和 BindingUnavailable。用 generic discard 写建立新 current，避免参考 accessor 的 oldData 读取提前暖缓存；重试仍读旧 G，成功后连续 32 次暖读不增加 provider lookup，Busy 解锁后继续复用同 link。
- 32 个联合原语 case：1/4/8/16 BPP × 冷/暖旧 cache × publish/cancel × 同/跨 provider before。两个独立 exact replica 预先存在；准备 metadata/physical/ledger，claim 后依次消费、延后清理放在 gate 外，再写入新字节。旧 link 拒绝新 allocation identity，原 G 重选 B 并读取旧字节；发布后 T 读取新字节；迟到 reader 不删除新 link，结束后账本 live/reserved 归零。

两个 fixture 的证明范围不能合并成生产 M6：前者走真实 captured root，但用 provider 故障注入而非生产 handoff；后者发生真实 retag，但只接 metadata/physical/ledger/read 原语，没有 PageStore root/selector 全链路。仍须接生产联合候选，并证明 old View、新 capture、commit/cancel、legacy raw pin 和并发两种顺序。

累计矩阵的最终结果与同源码身份见 [result-summary](result-summary.json)、[manifest](checks-01/manifest.json) 和 [identity](checks-01/identity.json)。结构门、六项工具自测、完整源码补丁和构建 dry-run 均由 runner 记录；测试总数不代替阶段或性能资格。

最终 **17 目标 × 2 架构，4,678 passed / 0 failed / 0 skipped**，每架构 2,339 passed。源码补丁 SHA-256 为 `1a110cfd892c50c982e8365f196e9a3a248ad7d0123392996233c77671a1520e`；结构门为 21 manifest entries、22 ownership facts、16 runtime census groups、1,514 indexed APIs、14,614 call edges、19 frozen external intrusion files；6 项工具自测通过。

## 兼容安装探针

在矩阵同一 image dylib 上重跑 ledger、physical、recoverable metadata 与原 publication/restore 探针，各覆盖两架构。每进程有实际分配正控制；测量每架构 96/48/32/28 个独立单页安装或取消区间，结果及库哈希见 [allocator-summary](allocator-summary.json)。这些区间不包含准备和延后销毁，不是 M7 原子批；本批没有把冷重解析声明为零分配。

八个进程全部通过，所有测量区间均 **0 allocations / 0 frees**。image dylib SHA-256 为 `fb3814b657943d357bfbd13e280ca30b0cc12c0b53c07bb0972602f8052505d7`，与矩阵 identity 一致。

## 源码身份、失败记录与复现

HEAD 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`，最终累计改动以 [source.patch](checks-01/source.patch) 为准，包含三个尚未跟踪的新生产/测试文件。[read-rebind-implementation.patch](read-rebind-implementation.patch) 是相对上一 ledger 批的七文件增量；[incremental-review](incremental-review.json) 已逐个重建比较前态。[ratchet-check](ratchet-check.json) 对比原始 ratchet，未提高 reviewed ceilings。

中间失败全部保留：

- `build-01.log`：测试缺少 metadata 私有访问声明，并误用了 transition epoch 字段；修正后 `build-02.log` 编译通过。
- `arm64-resident-01.log`：49 passed / 144 failed。128 个 case 的 wrapper 未正确声明 capability，16 个 publish case 错用普通 applyOwner 执行 prepared-only CommitTransaction。修正 wrapper capability 与 domain admission 转发，改用 prepare/installPublication；同时补齐失败退出的 pin 清理及 gate 外 deferred cleanup。
- `arm64-resident-02.log`：65 passed / 128 failed。联合原语全部通过；故障注入 fixture 的第二次 fill 提前暖了旧页 cache，未触发预期 provider lookup。改为 generic discard 完整覆盖写，不读取旧 G。
- `build-04.log`：上述 fixture 修改错误调用了不存在的 descriptor.layout；改为使用已解析 writer 的 byteSize，`build-05.log` 编译通过。

没有放宽生产守卫或删除负例。完整矩阵拒绝覆盖已有输出：`python3 docs/vulkan_gpu_design/evidence/br1_s06_read_rebind_20260927/run_checks.py checks-02`。重跑 allocator 使用 `run_install_probe.py arm64 新标签` / `x86_64 新标签`，可另传相应 probe `.cpp`；runner 的 tracked diff 本身不包含未跟踪源码，复现应以完整矩阵 source.patch 为准。更新代码后先重新绑定调用图和 baseline，保持原 ratchet，再取新证据。
