# S03 前置批：成功写后的元数据索引刷新

日期：2026-09-28。唯一阶段入口为 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)；设计条款与代码段的关系见 [01d / MR1–MR7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01d_metadata_refresh_and_pending_visibility.md)。本批未启用跨 dab 持久 pending，也不授予 S03 或 M6–M8 完成资格。

## 1. 身份与最终验证

HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含未跟踪生产/测试文件的源码差异 SHA-256：`190bb780ca86806c744ffe409f3a3b321de4d19dba6a85fc97f0aefe1360e859`。

同源码 17 CPU/业务目标 × arm64/x86_64：**6,484 passed、0 failed、0 skipped**；每架构新增 16 个 manager 场景与 4 个底层选择器场景。结构门与六项工具自测通过，最后构建 no work。完整命令、seed、源码与二进制身份分别在 [matrix manifest](checks-01/manifest.json)、[identity](checks-01/identity.json)、[source.patch](checks-01/source.patch)。[绑定检查](evidence-scope.json)逐一校验最终源码、全部测试与探针 image 哈希未变化；[本批代码增量](metadata-refresh-code.patch)相对前批快照，不含以前批次的实现。

[34 次最终探针](probes-manifest-01.json)全部通过，其中 32 次继承探针在本批 image 重新编译/运行，2 次新增真实刷新探针覆盖两架构。各 `install-*-identity.json` 保存实际探针/interposer 源码、命令、环境与哈希。[graph-01](graph-01.log)为 1,782 APIs / 18,061 edges / 17 callback registrations；[baseline-01](baseline-01.log)通过 21 manifest / 24 ownership / 16 census / 19 intrusion，未增加现有布局或外部侵入上限。

## 2. 本批代码与可见性

- Store 只在一次原 owner gate 内按既有 selector 分类存在性；结果是临时 0/1 数组，不是 retained snapshot、read protection 或像素访问能力。输出分配和 Qt detach 在 gate 前，旧输出释放在 gate 后；无效 selector 保留原输出。
- backend 沿原 publication read gate 保护事务选择，history / 健康 anonymous overlay / current 的顺序保持；没有第二份 selector 或页面权威。
- 普通成功 changed-delta 刷新只增删兼容 hash/extent，并清原 read-ready。正在使用的 reader 保留旧像素到最终 unlock；后续实际读取才重新解析并 pin。写后不再为 cache 准备另做一次 capture/payload read。
- 兼容 copy 失败回滚仍用一个 exact view 恢复缓存字节。`installPageStoreReadCache/takeIdleReadCache` 仍有该真实 caller，未删除。未迁移 raw consumer 不能依靠“下次 lock 才恢复”保证失败原子性。
- 原 per-operation seal 保留。存在性查询排除未 sealed pending，因此不能直接作为未来持久 scope 的 pending 新页/删除表；该接线仍按 SS1/SS5/SS7/SS8 联合实施。

## 3. 针对性验证与保留失败

| 记录 | 结果与含义 |
|---|---|
| [red-01](red-01.log)、[red identity](red-identity.json)、[red source](red-source.patch) | 新增 16 组 manager 用例在修改前生产实现均失败：写后多一次 capture。2 passed / 16 failed，保留可复现反例 |
| [green-focused-01](green-focused-01.log) | 18 passed：初版成功刷新已满足无额外 capture、旧 reader、新值和 history；尚未覆盖失败 raw 恢复 |
| [manager-early-01](manager-early-01.log) | 438 passed / 22 failed。六项是真实回归：失败 copy 后 raw cache 仍含第一页面的局部写入；另外 16 项为 packed 写旧计数仍期待一次成功 refresh capture |
| [manager-focused-02](manager-focused-02.log) | 56 passed：保留原失败 exact-view 字节恢复后，六项原断言不变通过；packed 只减少被删除的 refresh capture，保留 operation-start / 测试注入次数和全部像素/undo 断言 |
| [presence-focused-01](presence-focused-01.log) | 6 passed：四种 BPP 的 current/base/overlay、remove/default、pending 在 seal 前不可见、结束 selector/空 batch/无效 surface、输出不变及 close；query 不触发 provider binding/read request/capture |
| [build-focused-02](build-focused-02.log) | 首次新增底层测试误用 enum 名 `TransactionBase`，编译拒绝；改为实际 `TransactionBaseEpoch` 后 [build-focused-03](build-focused-03.log)及最终完整构建通过 |
| [checks-01](checks-01/manifest.json) | 在修正后的同一源码上完整双架构复验；不将上述初版通过或失败记录冒充最终资格 |

失败恢复的六项测试仍直接检查 `m_hashTable` 中已有 wrapper 的 raw bytes；没有改为通过 `getTile()` 或额外读取隐藏残留字节。原 process 8 MiB / 384 页负载和全部旧预算断言保持。

## 4. 实际刷新成本

[探针源码](metadata-refresh-probe.cpp)调用真实 `refreshPageStorePages`，每组重复 1,000 次，原有 wrappers 已存在且其中第一页真实 swapped。覆盖 1/4/8/16 BPP、history/no-history、K=1/9/65/257。两架构 [arm64](driver-arm64-metadata-refresh-final-01.log)、[x86_64](driver-x86_64-metadata-refresh-final-01.log)结果一致：

| K 页 | 每次 allocation / requested bytes / free | 1,000 次新增 capture / generic read | 原 swapped 页面 |
|---|---|---|---|
| 1 | 1 / 19 / 1 | 0 / 0 | 保持 NonResident |
| 9 | 1 / 27 / 1 | 0 / 0 | 保持 NonResident |
| 65 | 1 / 83 / 1 | 0 / 0 | 保持 NonResident |
| 257 | 1 / 275 / 1 | 0 / 0 | 保持 NonResident |

请求字节为 Qt 容器头与 K 个分类值（K+18），不是整个 allocator 实际堆占用。区间之后的真实 tile read 恢复正确像素；不把该冷读取归入零物化区间。正控制实际分配成功被记录。先期 [trial](driver-metadata-refresh-trial-01.log)通过，但最终资格只使用源码冻结后的两架构运行。

该区间不含新增 wrapper/hash/extent、seal/publication 或 cold reader 的成本；临时数组尚未接完整共享预算。不是零分配安装、恒定 gate hold 或端到端 stroke 时延/吞吐证据。

## 5. 修改指南与剩余出口

[MR1–MR7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01d_metadata_refresh_and_pending_visibility.md)逐项给出已落实函数、必须保留的失败终点和仍待修改的代码段：MR5 在发布前准备必要适配资源；MR6 将 history scope、job 身份/读写范围/cut、current/G0/source 与完整 checkpoint 联合接线；MR4 按 raw consumer 迁移条件收紧兼容恢复。原索引刷新仍为 void/assert，不能据此声称写入和索引在资源拒绝时整体原子。

[导航与映射检查](validation.json)覆盖 21 份指南及 3 份入口/证据文档、15 个修改 ID；302 个受本批源码移动影响的链接重新定位，01d 的 MR1–MR7 逐个匹配实际函数。源码映射记录见 [source-link-remap](source-link-remap.json)，完整文档增量见 [guide-update.patch](guide-update.patch)。检查明确跳过归档。

完整 S02/S03、S09/S10 必要准入与共享预算、M6 SSD/epoch/故障/资源资格、M7、M8、真实 stroke / Fresh 2% / BR1-PERF、Vulkan、TSAN 均未新增完成资格。优先级继续为 stroke → undo → 上下文切换。
