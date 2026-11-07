# S09 第七批：completion 存储拒绝的原子性

本批从 T5 的实际 caller/gate 审查进入 T6 的真实存储故障；设计/代码/后续修改映射见 [04a §14](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#completion-failure-atomicity)，阶段权威仍为 [92](../../92_br1_m6_m8_execution_baseline.md)。

## 实际改动

- 原 registry/source/domain/value 仍是唯一完成权威。source 私有 range/status/readiness 容器和 signal callback 容器改用标准 map/unordered_map，避免隐式共享的可写访问分配及当前 Qt QHash noexcept 插入的不可恢复分配路径。
- 先校验 Pending，再准备 Failed/Cancelled 状态，最后推进 prefix/range；覆盖插入失败撤销新状态项并返回 false，原 Pending、旧终态、其他 waiter 均保留。顺序 Succeeded 不需要新存储；未用整表复制回滚。
- source/订阅插入拒绝保留已存在的记录；取消继续按原 signal identity/空表复验，capture 与空 lookup storage 在原 gate 外清理。complete 在准确终态可见后才通知。
- 当前三个生产 metadata 安装路径与 generic read 终结共用 owner gate，核对见 [source-bound gate audit](publication-owner-gate-audit.json)。这是当前 caller 事实，不代表完整并发资格，也不约束将来改变 admission 的 M7/M8。没有为未证实的生产 claim 交错新增轮询队列。

## 可复现验证

- 17 目标 × arm64/x86_64：**6,072 passed，0 failed/skipped**；每架构新增 54 项 six-range × three-status × three-duplicate 组合。完整命令、seed、日志和身份见 [manifest](checks-01/manifest.json) / [identity](checks-01/identity.json)。
- 结构门 1,655 APIs / 16,389 edges / 15 callbacks，21 manifest / 24 ownership / 16 census / 19 intrusion；6 项工具自测通过，ratchet 未改。
- terminal-final：每架构 46 个真实 allocator 区间、28 个逐次分配故障；拒绝后仍 Pending、无 verified terminal、原 waiter/terminal 数不变，随后同 ticket 重试成功并且只通知一次。
- readiness-final-02：每架构 26 个区间、20 个故障，覆盖新/已有 signal、257 个 ticket 或 subscriber 及 source 扩容；已有 waiter/source 不丢失，失败 capture 析构可重入 registry 查询，最终容量归还。
- ordered-final：每架构 1,024 个 fresh-thread 顺序 Succeeded 区间，0/257 个既有非成功结果，allocation/bytes/free 均为零；正控制有效。
- 八组既有探针继续通过：budget96/root72/legacy28/warm96/joint31080、immediate cleanup42、deferred cleanup42 及公开 outer cleanup。原区间与上批相同，空块释放实际 charge 与 owner 活动责任保持。二十二次最终探针共享矩阵 image，见 [probe manifest](probes-manifest.json)。

源码 HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；累计 patch SHA-256 `11d8366ad8a91fa2d274802364d6d3d57266797ffa718840fbe2a20432979dd3`；image SHA-256 `ac434aa9a0576e8a9b2b06151906f86d66f5eec1daa10c4871c21d5918b74063`。五文件本批增量见 [incremental review](incremental-review.patch)，改前源码见 [before source](before-source.json)；probe identity 内含具体 probe/interposer 文本及哈希。

## 修复前反例与中间失败

`before-01` 的 arm64 真实 Registry complete 在注入后出现终态数量已经增加、目标被视为 Succeeded、原订阅未通知，并在后续 QHash 分配点终止进程。`before-trace-02` 将反例收窄为首个 Succeeded：markTerminal 内分配抛出后，已发布 prefix 且未通知，重试已无法成功；2 区间/1 次注入/1 个不变量失败。原日志与旧库身份保留。

独立 `qt-hash-control` 用相同安装依赖和 QHash<quint64,KisCompletionStatus> 在第三次分配处复现不可被外围 catch 接住的 bad_alloc 终止；调用栈进入 findOrInsert，相关依赖版本/源码片段哈希见 [Qt path](qt-hash-failure-path.json)。该控制不是生产测试通过项。

`build-01` 保留容器迁移漏改 isEmpty 的编译错误，build-02 修正；后续 build-03 含新增测试与完整类型注释。定向中间探针只是调试结果，最终结论仅取 checks-01 与 final tags。

x86_64 的首轮 `readiness-final` 在首个分配故障后失败；`readiness-debug-01` 确認 probe 自己的 moved-from std::function 仍持有 capture（caller_callback=1、uses=1），registry 仍为 Unavailable、零 signal/容量。C++ 不要求 moved-from std::function 为空，原生命周期断言不成立。探针改为 std::exchange 显式清空自身 callback 后再传值，并检查源为空；两架构 readiness-final-02 通过。生产源码和矩阵 image 未变，原失败日志、源码和身份保留；最终采用 corrected tags，不把探针错误计为生产修复。

## 尚未完成

complete(false) 只保证不伪造完成，不代替 producer continuation。乱序/Failed/Cancelled、冷订阅仍可能分配；必要状态/range/callback/wake/dispatch 存储须在产生终结义务前准入，并联动未消费返回值的 provider 失败终点。armLastUse Unavailable 和 dispatch bad_alloc 的自动进度、T4 整轮预算、T5 真正可达拒绝/不可恢复错误终点、T6/S10 全局收费与压力资格继续。未完成 M6/M7/M8 或完整目标，未新增真实 stroke、Fresh 2%、Vulkan、TSAN 或 BR1-PERF 资格。
