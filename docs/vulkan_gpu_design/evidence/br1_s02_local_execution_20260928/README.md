# S02 第五批：execution 局部 resident 访问

日期：2026-09-28。执行入口为 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)，要求到代码段见 [01c §14](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#local-execution-implementation)。本批沿原 managed/packed 消费者落实借用内热访问；持久业务 stroke、scheduler job/cut、完整 checkpoint、M6–M8 与 BR1-PERF 仍开放。

## 1. 源码与验证身份

HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`；含未跟踪生产/测试文件的差异 SHA-256：`f1c48cb0918923da6b2054365dd6db28ecc6b680ecb785ab2414f379eaa737ef`。

最终 17 目标 × arm64/x86_64：**6,444 passed、0 failed、0 skipped**；结构门与六项工具自测通过，最终构建检查 no work。完整 CPU/业务资格以 [checks-01 manifest](checks-01/manifest.json)、[源码与二进制身份](checks-01/identity.json)及[完整源码差异](checks-01/source.patch)为准。[最终绑定检查](evidence-scope.json)逐一确认源码、测试与 32 个探针 image 一致；[本批代码增量](local-execution-code.patch)及 [diff 检查](diff-check.log)保留。第四批结果不作为本批资格。

[32 次最终探针](probes-manifest-02.json)已在 arm64/x86_64 全部通过；标签 `final-02` 沿用执行器的标识，没有本批 `final-01` 运行。每次 `install-*-identity.json` 包含实际探针源码、interposer、编译/链接/运行命令及 image 哈希。[graph-02](graph-02.log)生成 1,780 APIs / 18,022 edges / 17 callback registrations；[baseline-02](baseline-02.log)通过 21 manifest / 24 ownership / 16 census / 19 frozen intrusion，原布局上限保留。

## 2. 实际行为与边界

- 原借用范围改为每页 16 B 的原 entry/冷 Page 引用。绑定在 session 结构 gate 下校验原 slot；活跃借用和 guard 保活禁止 erase/reuse。原 write set 仍唯一保存 key/pending；没有新增页状态权威或持久像素指针。
- `claimRange` 按声明 keys 查询原 write set，先全范围复验再安装原 claims；拒绝撤销本次新 entries，保留旧 pending 和 claims。
- 已绑定冷页的 beginWrite、version、providerBacking、unpin/exposure 只使用 execution 局部 gate 和原 binding。另一个 worker 的冷准备或目录增长不再阻塞这些访问。每次实际 pin，NonResident 继续真实 materialize，失效不冒充热命中。
- 原 scope 生命周期改为 atomic。取消令后续入口拒绝；取消前已接纳调用可安全完成，由原 scope 保留终结责任。没有新增回滚权限或第二份取消状态。
- 每个 execution 局部累计 pin/释放/materialize/字节，最后归还时在原 session 中一次归并。峰值明确改名为 `maximumPinnedPagesPerExecution`，指单 execution 的精确峰值；直接串行 session 视为一次 execution。不将局部峰值相加冒充并发瞬时峰值，不为诊断引入共享热计数器。

锁序为 execution → session（仅冷缺页）→ owner；resident 分支不取 session 结构锁。取消和 seal 不持结构 gate 等待 execution 局部锁；最终借用归还仍需结构 gate 摘链。首次冷准备的串行和末端等待继续开放。

## 3. 行为、故障与资源证据

[focused-02](focused-02.log)：42 passed、0 failed/skipped，覆盖 1/4/8/16 BPP。

| 场景 | 实际证明 |
|---|---|
| executionWarmDuringColdPreparation | worker B 被阻塞在真实 provider 冷准备时，worker A 对两个已准备页交替访问 1,000 次并读取 version；期间跨线程归还 guard 也完成。64 页范围增长不使原 entry/Page 引用失效 |
| executionLocalCountersAndCancellation | 同一 execution 两个并存 guard、重复访问、取消后停新访问、晚 guard 归还、唯一取消与原像素保持；累计 pin/释放成对，单 execution 峰值精确为 2 |
| guardReleaseParksPendingBacking | 原 direct 和新增 borrow 两种路径，各格式、seal/cancel；真实 swap-out 后 materialize 一次，generation、像素和旧 exact view 不变；终结不额外 swap-in |
| 原四个 execution 用例 | 不相交 worker、重叠/错误 worker/surface 排斥、预算拒绝、放弃、取消及晚 facade/guard，继续通过 |
| 原 process resident limit | [product-limit-01](product-limit-01.log)通过原 8 MiB、384 页、6 MiB 输入及第二 backend 拒绝，未提高预算或缩小工作量 |
| 取消与 materialize 交错 | [arm64](driver-arm64-execution-cancel-progress-final-02.log)、[x86_64](driver-x86_64-execution-cancel-progress-final-02.log)：真实 NonResident materialize 入口暂停时，取消无需等待恢复即可记录失败；已接纳调用完成，下一次访问和成功 finish 被拒绝，后续原 cancel/abort/close 成功 |
| 实际范围存储拒绝 | [arm64](driver-arm64-execution-failure-final-02.log)、[x86_64](driver-x86_64-execution-failure-final-02.log)：每架构 121 区间 / 117 次实际拒绝，旧 pending 的版本及字节不变，重试和唯一原终结成功 |

[原有 allocator/install/read/admission 探针](probes-manifest-02.json)全部在本批 image 上重新编译运行。

## 4. 分配成本

两架构 [execution-allocation](driver-arm64-execution-allocation-final-02.log)结果一致。每个范围内 1,000 次 resident guard 获取/version/归还均为 allocation/bytes/free = **0/0/0**。一次完整再次借用（含 finish/free）：

| 范围页数 | allocation / bytes / free |
|---|---|
| 1 | 1 / 216 / 1 |
| 9 | 2 / 360 / 2 |
| 65 | 3 / 1,272 / 3 |
| 1,000 | 3 / 16,344 / 3 |

局部 gate 与计数使控制记录从第四批 152 B 增为 216 B；每页范围保持 16 B。额外存储通过原 allocator 实际收费，归还后 live charge 回到借用前。这里证明分配成本和并发进度，不证明吞吐、时延或 Fresh 2% 门。

## 5. 中间失败与修正

- `build-01`：冷准备分支仍需更新 entryIndex，新增局部变量误标 const。改回可变 index 后 build-02/build-03/full 构建通过；没有改变准备语义。
- `baseline-01`：runtime census 的三处峰值字段仍指旧名字，结构门明确拒绝；同步实际单 execution 峰值后重新生成 graph-02/baseline-02，没有放宽布局或侵入上限。
- `cancel-progress-preliminary`：探针错误地等待 timer 构造时的 observer；原 recorder 只在显式 next 时通知，因此没有进入预期交错。修正为真实 swap-out 后的 WritePendingMaterialize 显式阶段；preliminary-02 和两架构最终交错均成立，生产诊断接口未改。
- 首次文档锚点重定位拒绝已修改签名的 claimRange；按同一实际函数符号定位后重新从修改前快照映射。未以相邻行替代函数锚点。

所有失败日志保留，最终资格只绑定本批最终源码和二进制。

## 6. 后续交付

SS1/SS5 业务 owner 持久 scope、job ID/read-write footprint/cut/continuation → SS7/S04/S05 完整 checkpoint 与压力窗口 → SS8/S03 painter/iterator/refresh 联合启用。当前 managed/packed 仍每 operation seal。全 job 冷资源准入、必要终结存储、共享预算及 facade 消失后的自动进度继续按 S09/S10 收口。

完整 M6 epoch/SSD/故障/资源、M7、M8、真实 stroke、Fresh 2%、Vulkan、TSAN 与 BR1-PERF 没有在本批获得新资格。undo/context 仍排在 stroke 之后。

## 7. 指南核对

[导航与符号检查](validation.json)覆盖 20 份指南、3 份入口/证据文档与 15 个修改 ID；131 个主题源码文件全部在反向索引中。01c §11–§14 共 77 个重点锚点逐一匹配实际符号。文档更新期间源码身份保持不变；检查不读取归档，也不另授阶段资格。
