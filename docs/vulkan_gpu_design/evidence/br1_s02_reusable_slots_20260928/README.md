# S02 第二批：可复用 slot、原 claim 部分取消与锁外存储归还

设计与当前阶段以 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)为准；函数、消费者和剩余修改见 [01c §9–§10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#reusable-slot-implementation)。本批保留原 session/thread、selector、metadata、ClaimSet、budget 与 retirement owner。

最终源码 HEAD 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`，含六个未跟踪生产/测试文件的工作树差异 SHA-256 为 **`796219267176e019bb27b18c811250c8057fff56d79c82c329551dfcedfaf7b5`**。最终身份与完整矩阵见 [checks-02/identity.json](checks-02/identity.json)、[manifest.json](checks-02/manifest.json)、[source.patch](checks-02/source.patch)；九个手工源码文件相对第一批的增量见 [incremental-review.json](incremental-review.json)、[incremental-code.patch](incremental-code.patch)。生成的调用图/源码基线另外计入完整源码身份，不充作手工修改数量。

## 实际实现

- 热、冷块支持 live 枚举与槽位复用；原 key 索引和 guard 校验 index/incarnation，inline 同样拒绝旧身份。birth 耗尽拒绝，不回绕；存储仍由外层串行访问，稳定地址不授予并发访问权。
- 原 ClaimSet 增加单项释放，验证原 write set、slot、token 与 origin。取消成功一项才删除一项；剩余债务留在同一 session。旧 session 重试不能撤销新 writer 的 claim，取消统计不重复累加。
- 空块锁内摘除，清理值保留原 controller。初始化源最后引用、摘出的冷热块和最后集合/索引/目录均在 owner gate 外释放，实际 free 后返还 charge；activity 保持到清理完成。
- seal 的所有枚举支持空洞，冷槽创建消费真实 slot index。丢弃目标后先归还空块，再准备 alias，避免继续占着已可释放容量。单页 inline、104 B entry / 688 B Page / 128 B guard 上限保持。

## 验证与实际成本

最终 **17 目标 × arm64/x86_64，6,352 passed，0 failed/skipped**；相对第一批每架构新增 30 项。新增覆盖窄 incarnation 耗尽、ABA、目录/inline 空洞、move/rebind、资源未终结时拒绝 erase、原 claim 单项释放、四 BPP 的 2/17/65 页部分取消和竞争 writer、seal 中先归还容量再复用冷槽。旧增长/分配拒绝/晚 guard 用例同时复验。

[graph-02.log](graph-02.log)绑定 84 个 translation units：1,715 APIs、17,266 edges、15 callbacks；21 manifest / 24 ownership / 16 census / 19 intrusion 与六项工具自测通过，ratchet 未放宽。最终结构门见 [architecture.log](checks-02/architecture.log)。本批未运行 Vulkan 或 TSAN。

[20 次最终探针](probes-manifest.json)均使用 checks-02 的同一 image，每架构包括：

| 探针 | 实际覆盖与结果 |
|---|---|
| address | 2→1,000 页增长后原 overflow 地址保持 |
| storage | 1/2/8/9/1,000 页各重复命中 1,000 次，allocation/bytes/free 为零 |
| write-set 故障 | 24 区间、20 次实际 allocator 拒绝；原集合和随后重试/预算清理正确 |
| native/semantic 故障 | 50 区间、42 次实际拒绝；取消、重试、close 正确。只注入 `kisAllocateMutationStorage`，不宣称内部所有 OOM 已闭合 |
| joint / legacy / warm-read | 原 31,080 / 28 / 96 个观测区间保持零 allocation/bytes/free，正控制有效 |
| outer cleanup | 复验既有 metadata 空块在外层 owner gate 外 free，原 charge/activity 责任保持 |
| slot reuse | 1/2/8 页各 erase/recreate 1,000 次零 allocation/bytes/free；9/1,000 页各有 1,000 次索引节点分配和释放，共 48,000 B，live charge 不增长 |
| mutation cleanup | 在调用栈确认的 `kisFreeMutationStorage` 实际 free 处暂停，cancel/seal 时另一线程均可取得 owner 锁，activeProviderCalls=1；随后终结、abort、idle、close 成功 |

存储的实测 live bytes：1/2/8/9/1,000 页分别为 **0 / 1,064 / 1,064 / 1,584 / 193,848 B**。保留目录、一个暖块和索引容量继续收费；slot 身份/链的额外 bytes 已计入，不能沿用第一批较小数字。单页探针的 peak=1 B 来自测量前 controller reservation 正控制，不是 mutation 容器分配。

mutation cleanup 的 cancel 分支在首次 block free 前已释放三个索引节点，因此该时刻总 charge 比准备完成时少 144 B；这不代表 block 提前退账。探针按真实释放栈暂停，源码 `kisFreeMutationStorage` 在 delete 返回后才返还对应 bytes。该证据证明锁外释放与原寿命责任，不证明整个维护 pass 的时间/字节上限。

## 执行记录与可复查命令

最终矩阵命令为 `python3 docs/vulkan_gpu_design/evidence/br1_s02_reusable_slots_20260928/run_checks.py checks-02`。脚本保留命令、环境、seed=12345、源码和库/测试二进制哈希；已有输出目录不可覆盖。复查时使用新的输出目录。

构建 build-01 至 build-04 均成功；[focused-01-manifest.json](focused-01-manifest.json)对应两架构 104 项定向通过。补强的 seal 容量用例见 [seal-reuse-focused-02.log](seal-reuse-focused-02.log)，其临时默认环境产生了 swap 目录 fallback 提示，正式矩阵仍使用固定测试环境。

checks-01 的完整矩阵和 [probes-manifest-01.json](probes-manifest-01.json)也通过；复核后增加 seal 在 alias 准备前释放空块的消费点，重新生成 graph-02、构建并运行 checks-02 与全部 20 次 `*-final-02` 探针。早期记录原样保留，最终结论只绑定后一组身份。所有探针实际编译/链接/运行命令及 image 哈希在对应 `install-*-identity.json` 中。

[validate_guides.py](validate_guides.py)核对当前源码/image/测试/探针身份及文档双向映射，结果见 [guide-validation.json](guide-validation.json)、[mapping-validation.json](mapping-validation.json)。本批重定位的 170 个源码链接见 [guide-link-remap.json](guide-link-remap.json)，指南增量见 [guide-update.patch](guide-update.patch)。不读取归档。

## 保持开放的出口

本批生产子集释放消费的是**部分取消**，不等于 `sealSubset` 或完整 checkpoint。持久 stroke scope、job/range borrow、跨 worker、不相交并行、读取意图、projection/refresh 和真实 stroke 接线仍待实现。整体范围准入、admission/activity 的内部 QHash 分配拒绝、scope/range/control-block 计账、必要终结容量、共享父额度，以及 S08/S09 整轮工作预算与完整压力进度继续。

这些结构/故障证据不授予真实 stroke 加速、Fresh 2% 控制桶、完整 M6/M7/M8、undo/context 或 BR1-PERF 资格；没有新增 Vulkan、TSAN 或 SSD 全矩阵结论。

文档检查首轮仅因比较器将源码行去缩进、却未将预期符号去缩进而拒绝三个内部方法；保留 [guide-validation-01.json](guide-validation-01.json)。修正比较器后重新核对全部链接、符号及源码/image；未改生产代码或测试资格。

加强 A1–A7 旧定位复核时，检查器又因 `detachLocked` 有意新增 lock 参数而拒绝整行签名比较，记录见 [guide-validation-02.json](guide-validation-02.json)；检查改为验证同一函数符号，签名变化仍在代码增量中审查。最终检查包含这 21 个原实施入口与 11 个新增实现入口。
