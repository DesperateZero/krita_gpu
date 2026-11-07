# S09 第六批：读保护空块的外层锁外释放

本批对应 04a T4 的空块存储去向、原预算与 owner 生命周期；唯一阶段状态仍在 [92](../../92_br1_m6_m8_execution_baseline.md)。函数级实施与后续待改责任见 [04a §13](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#outer-read-cleanup)。

## 实现与边界

KisPageMetadataReadCleanup 携带原 arena 已摘空块、原 MetadataBudgetAuthority 与 bytes；跨 coordinator 的非空 carrier 在修改前拒绝，块拼接不分配。payload free 后才归还原 charge。KisPageReadCleanup 是栈上终结作用域，构造先于外层 owner locker；首次接到块时在原 owner 下保留既有活动计数，scope 在解锁后 free/归还预算，再减活动计数。没有新调度队列或第二份元数据权威。

全部读终结 caller、abort 预检、close 和后台完成均接入。close 先清理自身 scope 再检查 outstanding capabilities；worker 清理先于 idle 和 owner lifetime 释放。完整 T4 节点/字节/时间上限、其他临时大对象、T5 自动重试、T6 必要通知/派发准入及 S10 全局预算仍开放。没有新增 stroke 性能或阶段资格。

## 最终验证

- 17 目标 × arm64/x86_64：**5,964 passed，0 failed/skipped**，每架构新增 8 个 carrier/reference case 与 7 个业务路径 case。完整命令/seed/输出见 [matrix manifest](checks-01/manifest.json)，源码与所有测试 binary/image 哈希见 [identity](checks-01/identity.json)。
- 结构门与 6 项自测通过；1,654 API / 16,371 edges / 15 callbacks；21 manifest / 24 ownership / 16 census / 19 intrusion；ratchet 未放宽。
- 每架构 deferred-final 的 42 个真实转移区间 allocations/bytes/frees 全零，42 个后续 clear 区间 allocations/bytes 全零、实际 free 10 块，与 footprint 和 charge 差额一致。新线程没有预热目标终结；原 reclaimer 同时活跃。
- outer-final-02 暂停在实际 metadata cleanup 栈内的 16 KiB block free；另一个线程 sessionStats/backingUsage 均可返回，active cleanup=1、预算仍计 live；继续后确认成功且 idle/close 成功。分别见 [arm64](install-arm64-outer-final-02.log) 与 [x86_64](install-x86_64-outer-final-02.log)。
- 六组原探针：budget96/root72/legacy28/warm96/joint31080 保持零 allocation/bytes/free，immediate cleanup42 保持零 allocation/bytes、各实际 free10块。正控制有效；[十六次最终探针](probes-manifest.json)与完整矩阵 image 身份一致，最终探针 identity 同时内嵌 probe/interposer 源码。

源码 HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；累计 patch SHA-256 `c399d717f1843d5a5ab517fab6f74d1b6d711e8e97ae4137b573ac92968f6e93`；image SHA-256 `f6b66bade6695db27be088ceff04b9169188fe220c9202f9441c607f9c390232`。九份生产文件、两份测试和 ownership 清单的本批改动见 [incremental review](incremental-review.patch)；改前精确内容见 [before source](before-source.json)。生成调用图、source inventory 的变化单列在累计 source.patch 中。

## 失败记录与证据修正

- outer-final 两架构在探针编译阶段失败：新增 backingUsage 核对漏含完整类型头文件。补齐后仅重跑 outer-final-02；生产源码、库和其余十四次已通过的探针均未变化，原失败日志保留。
- outer-before 两架构与 outer-after-01/02/03 是早期按 malloc size 筛选的观测；Qt 确认列表扩容会释放相同尺寸存储。after-03 的调用栈明确显示命中 acknowledgeLastUseLocked 的临时列表。**撤回这些结果作为“空 arena block 锁内释放”的独立反例资格**，保留原日志/身份；修复前的嵌套锁关系可从 before-source 核对。after-04 及最终 outer-final-02 按 cleanup/applyReadProtection 实际调用栈筛选，日志明确出现 KisPageMetadataReadCleanup::clear。
- build-03 缺少私有 arena 类型头文件，build-04 修复；focused-business-arm64-01 的 6 项失败来自新增 fixture 错用 1 BPP，而默认 fixture 为 4 BPP。build-05 和 focused-business-arm64-02 修正后 7 条路径通过；完整最终矩阵另行冻结。
- callgraph-generation 第一次因索引期间新增测试源变化而拒绝，没有接受混合身份；callgraph-generation-02 与之后 architecture-baseline/最终 matrix 通过。

这些中间失败不覆盖或替换；最终结果只取 checks-01 与 final tags。更多剩余责任见 04a §13，M6/M7/M8 和完整目标未完成。
