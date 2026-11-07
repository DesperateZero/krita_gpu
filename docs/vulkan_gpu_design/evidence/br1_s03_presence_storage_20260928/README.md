# S03 / OP3 写前 presence 准备与 S02 准入竞争修正

日期 2026-09-28；设计与阶段状态以 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)为准，待改内容与函数/行号/终结/验收关系见 [OP3 实施表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#presence-storage-implementation)。

## 实现与责任

默认 cursor、packed write、native clear、precise copy、rough copy 五个入口按本次声明页数准备 presence scratch，生命周期由原同步 manager operation 持有。具体准备和诊断放在现有 backend；≤64 页使用 QVarLengthArray 栈内 buffer，更多页在像素执行前分配一次。cursor 使用实际页并集大小，矩形入口使用其原遍历页数；没有扩大写范围，也未新增 writer registry。

写后查询通过私有 `resolveCurrentPagePresenceInto/resolvePagePresenceInto` 消费已有容量。原 publication read gate 保活选择，原 metadata gate 分类整组页面；不创建 snapshot、read protection 或 physical pin。内部 scratch 只有查询完全成功才进入刷新循环；公共 QVector 查询使用独立候选，检查实际容量，成功后交换，拒绝时共享旧输出保持不变。

显式 history cursor 的未 sealed pending 仍由成功 touched 集合派生适配，不调用这个 immutable presence 查询。已知 legacy Borrowed 不新增 presence 准备。默认写的准备拒绝沿原 typed 结果或 void failure context 返回，不执行 native 像素，也不转 fallback 或重放。

## 验证落点与测量边界

新增每架构 96 个 manager case：BPP 1/4/8/16 × K 1/64/65/257 × 五个默认入口及显式 pending。包含负坐标、重复声明、稀疏触页、partial/rough copy、default 删除、完整页像素、索引、extent、旧快照与 undo/redo。原 metadata selector 测试增加共享旧输出检查，继续覆盖 current/base/overlay、remove/default、seal 前后、无效/已结束 selector 与空查询。

- [准备和查询分配探针](presence-allocation-probe.cpp)覆盖实际六条路径。只测 presence prepare 和 metadata resolve 两个区间，包含各自锁操作；不包含 wrapper/hash/extent 安装、冷像素准备、终结或 cleanup。公共查询分配作为正控制。
- [故障探针](presence-failure-probe.cpp)与[一次性拒绝 interposer](presence-failure-interposer.cpp)覆盖 native presence 准备、Store 公共输出、backend 公共输出。每个匹配分配分别拒绝一次并扫到无故障成功对照；核对零像素 body、generation/transaction/预算不变、旧输出共享者、原像素与正常重试。
- [终结 helper 探针](metadata-refresh-terminal-probe.cpp)继承前序 swapped compatibility tile、1000 次刷新、无 capture/通用读请求和后续实际像素断言。它测没有外部 prepared buffer 的旧入口：≤64 页应零分配，>64 页仍每次一次分配/释放。调整只对应当前明确的 inline 行为，前序冻结源码不改写；这个 helper 的结果不代替五个 native 入口的准备/查询区间。

## 失败保留与修正

[build-02](build-02.log)保留 fixture 调用派生 KisDataManager 未提供的 QRect clear overload 的编译失败，改用既有坐标 overload 后重建。[manager-focused-01](manager-focused-01.log)在 copy 场景中止；[LLDB](manager-debug-02.log)确认 fixture 把栈 source 传入共享所有权参数，导致 KisSharedPtr 尝试删除栈对象。fixture 改为实际 API 要求的共享 source，未改变产品 copy 语义。[manager-focused-02](manager-focused-02.log)为 114 passed、0 failed、0 skipped，包含 96 个新增场景和 16 个原刷新场景及 init/cleanup。

[初轮拒绝探针](failure-initial-01-driver.log)仅实际注入了公共 QVector 的 8 点，漏掉被内联的 QVarLengthArray 分配，因此整体失败。最终改为仅在明确准备区间拒绝一个实际分配，不依赖符号筛选，异常运行时分配仍可进行。[第二轮](failure-initial-02-driver.log)为 18 个实际拒绝和 32 个成功对照，全部通过。

[第一次结构门](baseline-01.log)拒绝 DataManager 类型侵入从 21 增为 26。将准备和诊断责任收回 backend 后，[第二次结构门](baseline-02.log)通过，未放宽 ratchet。具体位移保留在[首次源码重定位](source-link-remap.json)与[责任调整重定位](source-link-remap-placement.json)。

<a id="admission-revalidation"></a>
## 完整矩阵发现的准入竞争

第一次完整矩阵 [checks-01](checks-01/manifest.json) 为 **8,751 passed、1 failed、0 skipped**。唯一失败是 arm64 的 `testBrushPagePartition(wrap0-mirror1)`：真实 job 在进入 body 前因 `mutation admission changed during storage preparation` 被拒绝，随后 fixture 的并发入口等待失败。因此它是生产准入的竞争反例，不能按一次测试超时忽略。同源码的 44 个 final-01 probe 虽然各自通过，也不能覆盖这次矩阵失败；记录保留在 [原探针清单](probes-manifest-01.json)。

[确定性交错探针](admission-revalidation-probe.cpp)及[实际 allocation interposer](admission-revalidation-interposer.cpp)在每次真实存储分配时，让另一 worker 持原 gate 插入并移除无关 claim。修正前的 [before-02](install-arm64-admission-revalidation-before-02.log) 稳定复现拒绝；此前 before-01 只因探针漏传必需 error 参数编译失败，不能算产品反例。修正后的 [after-01](install-arm64-admission-revalidation-after-01.log) 接纳无关变化，真实冲突和 operational=false 仍拒绝，且所有分配时原 gate 都已释放。

修正由原 `KisMutationAdmissionTable::capture` 在**实际复制记录时**绑定 revision，并验证目标容量足以容纳最新需求；`install` 保留复制后严格 revision 检查。原 `admitMutationRecords` 在 allocate/build 后复验完整请求，可直接使用其他线程已安装的容量。最多三次候选准备保持不变，第三次释放后只有一次无分配的原表容量检查。值更新、插入/删除替换、foreign owner、容量不足和几何变化由新增 ReferenceTest 覆盖；原复制后竞争拒绝测试保留。具体代码映射见 [J1/J2/J3 修正表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-capture-revalidation)。

生产分区的 [重复回归](producer-stress-01/manifest.json) 覆盖 arm64/x86_64 各 20 个独立进程，每进程 16 个实际场景，合计 **640 个场景**全部通过；另有 80 个 Qt init/cleanup。该重复测试验证当前竞争修正，未宣称持续热点的公平性或延迟资格。

## 最终同源码验证

最终身份以 [checks-02](checks-02/identity.json)、[矩阵清单](checks-02/manifest.json)、[46 个 final-02 探针](probes-manifest-02.json)和 [evidence-scope](evidence-scope.json)为准：

- **19 个 Qt 测试目标 × arm64/x86_64：8,754 passed、0 failed、0 skipped**；42 条记录另含实际 build、architecture、六项工具自测和最终 Ninja no-op。较前序 OP2 增加每架构 96 个 presence case 和 1 个 admission case。
- 最终 **46 个 probe 全部通过**：继承前序 40 个测量入口（其中 metadata-refresh 使用本批明确的 terminal helper 预期），新增双架构 presence allocation、presence failure、admission revalidation 各一个。每架构 96 个 presence allocation 场景、18 个实际存储拒绝和 32 个成功对照；presence resolve 零分配/释放，≤64 页准备零分配，>64 页准备一次实际 K 字节分配。该结论不包含后续 wrapper/hash/extent 安装或整个 operation。
- 双架构 40 个独立生产分区进程 / **640 个实际场景**通过，producer、image、pigment 的 SHA-256 与最终矩阵完全一致，记录见 [stress identity](producer-stress-01/identity.json)。
- [第三次结构门](baseline-03.log)和[调用图](graph-03.log)：86 TUs、1,794 APIs、18,640 edges、17 callbacks；21 manifest、25 ownership、16 census、19 intrusion。DataManager 类型计数仍为 21，原 ratchet 和布局门未放宽。
- HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含必要新文件的源码差异 SHA-256 **`025c7bf2bada420c45598ecfa4d4e18d428ffa9a9c73b999bff13d15215a2a81`**。最终矩阵、probe、实际库/插件/静态库/测试及 no-op 构建身份已逐项复验；[diff-check](diff-check.log)通过。只含本批 14 个生产/测试文件增量的审查入口为 [presence-storage-code.patch](presence-storage-code.patch)。

[指南校验](validation.json)记录 15 个修改 ID、逐段代码锚点、反向索引及文档链接检查；[指南增量](guide-update.patch)可单独审查。指南校验没有重跑测试或授予新阶段资格，运行证据仍以本节最终身份为准。

## 剩余责任

tryCommit 的原 delta 刷新仍有写后 presence 准备，checkpoint 仍逐页适配；planar/raw compatibility 保留独立 batch 和 MR4 exact 字节恢复。缺失 wrapper、hash 插入/删除回收、extent、完整 publication/cut 的必要存储与失败线性化边界继续按 OP4–OP8 实施。scratch overflow 的完整 MetadataArena/共享父额度仍待 OP9，栈内优化与提前分配不等于完整预算准入。

默认真实 brush 仍无持久 owner；BC1–BC10 的 owner/current/source/producer cut、长笔压力与终结，M6/M7/M8、Fresh 2%、Vulkan、TSAN、BR1-PERF 均未因这批局部实现取得完成资格。优先级保持 stroke → undo → context。
