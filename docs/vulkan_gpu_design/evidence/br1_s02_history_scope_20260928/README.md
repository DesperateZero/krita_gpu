# S02 第八批：原 history 持有 mutation scope

日期：2026-09-28。唯一阶段入口为 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)；设计 → 函数 → 终结 → 待改责任见 [01f / HS1–HS8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01f_history_owned_mutation_scope.md#history-scope-map)。本批提供显式原事务/cursor 入口，没有默认启用 freehand 持久写段。

## 1. 身份与最终验证

HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含未跟踪生产/测试文件的源码差异 SHA-256：`ec504abbf486ea08f9f2ce70f5d6937f98e1989c14b0aa694e3a2978fc67d12a`。

最终 17 CPU/业务目标 × arm64/x86_64 为 **6,756 passed、0 failed、0 skipped**。以 [matrix manifest](checks-01/manifest.json)、[源码/库/二进制 identity](checks-01/identity.json)、[完整源码差异](checks-01/source.patch)及 [绑定检查](evidence-scope.json)共同证明；末次构建 no work。结构门和六项工具自测通过。[本批增量](history-scope-code.patch)仅对照批前快照，不混同整个累积工作树差异。

[36 次继承探针](probes-manifest-02.json)在本批源码/image 下重编译并运行通过，原安装、稳定存储、准入、execution、metadata refresh 和 checkpoint 约束保留。它们没有测量整个新事务/cursor 路径的 allocator、gate hold 或端到端 brush 性能；不得把底层 warm-guard 零分配外推为每 dab 整条管线零分配。各 `install-*-final-02-identity.json` 记录完整命令和哈希。

[最终调用图](graph-04.log)：85 TUs / 1,788 APIs / 18,413 edges / 17 callbacks；[结构基线](baseline-02.log)：21 manifest / 25 ownership / 16 census / 19 intrusion。扩展原 writer-admission ownership 条目说明原 history/session 消费与终结，没有新增 page/transaction 权威，也没有放宽侵入、布局或旧预算负载。

## 2. 改动与性能因果

`KisTransactionData` 显式启用原 memento 对应的 backend session；后续声明目标的同步 cursor 操作借用该 session。无 freeze 时，D=1/10/1000 的两页重复写只创建一个 session、准备两页 generation，不逐 operation seal/capture；完整 checkpoint 后再改一页只新增该页下一段 generation。归还 execution 仅解除本次访问，原 session 继续持有 pending。

普通 current immutable 读取保持最后 checkpoint；cursor 内可读本次借用的 pending。成功 touched 更新原兼容索引并失效 cache；checkpoint 依据原 history proof/removal delta 失效旧缓存。commit 先关闭新接纳，再 seal/原 history commit，成功才交付 undo；活跃写导致拒绝后保留 Closing，归还后可重试。callback 失败使原 scope 失败，只能取消。取消先 cancel 原 scope 再 abort 原 history；无活跃借用的未完成显式事务析构走取消。

业务事务层保持存储类型隔离。manager 的 bool 入口消费原 typed operation 结果，checkpoint 的 exact view 留在数据管理边界；需要保留 cut 的读取仍经既有 immutable read scope，在调度切点内取得。该 bool 不授予像素权限，也不保证稍后的 reader 仍观察同一个 cut。

每次 checkpoint/end 仍从原 delta 枚举 O(K_history) 临时 keys，没有常驻第二份 touched authority。targets/range/touched、wrapper/hash/extent 和 capture 仍有实际存储准备与失败成本；完整 job 准入、预算和短 publication gate 尚未闭合。

## 3. 新增用例与失败记录

每架构新增 **55 项**：manager 44、transaction 11。最终定向运行分别为 [46 passed](kis_tiled_data_manager_test-focused-02.log)、[13 passed](kis_transaction_test-focused-03.log)，各含 init/cleanup；最终资格仍以完整矩阵为准。

| 组 | 数量/架构 | 验证内容 |
|---|---:|---|
| manager 重复写与 cut | 24 | 四种 BPP × D=1/10/1000 × commit/abort；pending 前值、两页含远页、无每次 seal/capture、旧 cache 失效、旧精确 view 跨新段与终结、undo/redo、准确 session/generation/pin 计数 |
| manager callback 失败 | 8 | 四种 BPP × cut 前后；已经写字节后返回 false，后写与重复 commit 拒绝，abort 恢复原值，旧 view 不变 |
| manager 活跃工作终结 | 8 | 四种 BPP × commit/cancel；真实 worker 持 guard 时 cut 非终结拒绝、关闭后新借用/重开拒绝，原工作归还后唯一 owner 重试 |
| manager 身份 | 4 | null/foreign/stale memento、未携带 owner 写入、错误 owner 的空范围；callback 不执行，不能干扰其他 history |
| 实际事务/device | 6 | D=1/10/1000 × commit/abort；跨 worker cursor、checkpoint 后普通 pixel 读取、下一段写、旧 immutable reader、undo/redo、终结后拒绝 |
| 事务析构与失败 | 2 | 无活跃借用的未完成 scope 析构恢复原像素并可开下一笔；callback 失败不能 commit，原取消可恢复 |
| 事务上下文 | 3 | time/frame/LoD 改变后非空/空操作、再次启用、checkpoint、commit 均拒绝；回到原上下文后仍可继续，undo/redo 正确 |

[build-03](build-03.log) 与 [graph-01](graph-01.log) 保留新增测试使用文件中段头文件之前的编译失败；头文件移到顶部后 [build-04](build-04.log) 成功。[baseline-01](baseline-01.log) 拒绝事务层新增 PageStore 类型侵入；改为既有 manager 边界消费后，原 19 文件 ratchet 保持。[build-05](build-05.log) 与 [graph-03](graph-03.log) 保留测试改用原 read scope 后指针 cast 类型不匹配；修复后 [build-06](build-06.log)、最终图及完整矩阵通过。首轮探针驱动仍引用前批临时目录，被不覆盖保护拒绝，36 个探针均未启动；[失败 manifest](probes-manifest-01.json) 与初版脚本保留。改用本批独立目录和 final-02 标签后完整重跑。早期定向日志不替代最终源码资格，没有删减用例或放宽门。

## 4. 指南关系与剩余出口

[HS1–HS8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01f_history_owned_mutation_scope.md#history-scope-map) 对应 26 个函数入口；[符号校验](history-scope-mapping-validation.json)、[导航校验](validation.json)覆盖正向条款、反向文件索引、15 个全局修改 ID 和所有主题链接。源码链接先后随初版实现和边界修正重定位，见 [首次 remap](source-link-remap.json)、[边界 remap](boundary-source-link-remap.json)；[文档增量](guide-update.patch)记录完整变化，未读取归档。

只允许在无 writer 的初始化边界显式启用；尚未证明运行中 legacy admission 的原子转换。实际 strategy/painter/iterator、job 身份与读写 footprint、current/G0/source、freehand 异步 producer、mask/indirect、多 store/LoD 仍需联合接线。无真实 freeze 不应每 dab checkpoint；默认普通路径维持原 operation 语义。

MR5 的发布前适配存储与失败输出、S05 最外层短 gate、SS7 pressure subset、S09/S10 必要终结容量和进度、完整 allocator 异常/共享预算、任意 owner 提前销毁与晚 guard 的业务终结责任仍开放。本批不新增真实 stroke 吞吐/尾延迟、Fresh 2%、Vulkan 或 TSAN 资格；完整 S02/S03、M6/M7/M8 和 BR1-PERF 未完成。优先级保持 stroke → undo → 上下文切换。
