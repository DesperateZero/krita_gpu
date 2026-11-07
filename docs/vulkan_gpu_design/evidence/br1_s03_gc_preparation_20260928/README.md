# OP4：map 局部回收准备与引用终结

本批落实 [HX1–HX5 的局部回收子范围](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#hash-reclamation-implementation)。阶段状态与完整目标仍以 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)为准；不关闭整体 OP4、M6/M7/M8 或 BR1-PERF。

当前源码为 HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09` 加工作树差异 SHA-256 **`5d9b13f15d937d47839d1fd9610a7d5a873aa757d0029977f8f7acb25fd05c6e`**。包含既有未提交生产文件；无提交、无分支切换。前序 QSBR 草稿在本批完成接线，文档整理批的未验证记录原样保留。

## 修改与证据

- QSBR 的实际退休记录就是队列节点。prepare 先分配，enqueuePrepared 只转交；typed closure 在真正的局部对象中恢复后执行。heap 和 embedded 两类都在 callback 前取齐所需字段，自销毁 callback 后不访问原节点。
- TableMigration 内嵌 Action，真实迁移结束不再分配回收节点。普通迁移和实际多线程迁移覆盖在测试中；overflow 半迁移的完整 malloc 故障协议仍未通过。
- Mutator 的 insertIfAbsentValue 在 redirect 后仍保留已有 winner，lazy wrapper 的未发布输家锁外释放。原 exchange/assign 语义保持；真实 redirect 的旧 API 对照会替换 winner，新 API 保留它。
- insert/erase 在 map 变更前准备必要退休节点；移除值先进入回收责任链，再进行通知。raw-user 计数由 RAII 维护，通知异常不丢原引用或泄漏计数。
- 公开删除遵守 iterator 排他协议，计数随变更在相同保护范围更新。clear 先准备全部真实节点，再锁内复验，最多三次候选；不足时未修改 map。析构沿既有 owner 静止前提 drain，不调用会申请新回收节点的 clear。iterator 退出先释放其 gate，再 update GC。

## 验证范围

| 证据 | 结果与边界 |
|---|---|
| [完整矩阵](checks-01/manifest.json) | 20 个 Qt 目标 × arm64/x86_64，**8,884 passed、0 failed、0 skipped**；44 条记录含构建、结构门、六项工具自测和最终真实 Ninja no-op |
| 新增 Qt 场景 | 每架构 8 个：prepared 取消/移动/入队、embedded 自销毁、6 worker 共 12,000 次回收、强制 redirect、8 worker 同 key 插入、hash 引用/iterator 转移、通知异常、并发 clear。hash 异常夹具用受控 TileType；原容器是真实生产模板 |
| [50 个最终探针](probes-manifest-01.json) | 在本批源码重跑前序 48 项，新增两个架构的 GC/storage 探针；全部通过。各自命令、源码、interposer、binary 和实际动态库哈希保留在对应 identity 文件 |
| 实际 allocator / KisTile 探针 | 每架构替换 1、删除 1、clear 33 个实际分配点逐点一次性拒绝，共 **35 次拒绝 + 3 个正控制**；旧 32 个 map 值和计数保留，随后重试成功。clear 的 33 点含 vector 存储及 32 个实际节点 |
| 安装与暖路径区间 | 实际 Action 准备有一笔分配正控制；prepared 入队区间零分配/释放；小表增长到 4096 keys 未申请 heap Action。1000 次已有 tile lookup 零分配/释放；不外推为整个冷写入口无分配 |
| 析构区间 | 外部强引用保留实际 KisTile/TileData 时，map 析构零分配；不涵盖 provider 最后释放和所有业务通知的资源需求 |
| [结构门](baseline-01.log) | 87 TUs、1,794 API、18,719 edges、17 callbacks；21 manifest、25 ownership、16 census、19 intrusion。刷新实际源码身份，未放宽布局或 intrusion ceilings |
| [最终一致性](evidence-scope.json) | 源码、构建、全部探针及所用库身份一致；最终 Ninja 无工作，git diff --check 通过 |

初始构建、定向场景和初始探针也保留；当前资格以 `checks-01` 与 `final-01` 为准。旧证据未覆盖或修改。原 generic stack 压力/benchmark 仍按原规模运行，没有为了本批降低循环数。

## 继续实施的边界

**回收记录先于 map 变更，不等于完整 operation 资源先于像素写入。** 下一段必须处理 HX6 的真实结构容量与迁移凭据，HX7 原 manager/table 寿命，以及 OP6/OP7 的 canonical/adapter 联合安装。仅 reserve 或 null-value cell 占位不足以解决迁移后的容量保证。

本批未完成两种 hash 配置资格、完整通知/历史资源、iterator 持锁期间的全部节点预备、最外层 manager gate、GC 阈值自旋与销毁预算、共享父额度或长 stroke 联合启用。当前构建继续 `USE_LOCK_FREE_HASH_TABLE=ON`。并发测试不代替 TSAN；局部 allocator 证据不代替真实 stroke 尾延迟或正式 BR1-PERF。

## 复验入口

```sh
python3 /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_gc_preparation_20260928/finalize_evidence.py
python3 /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_gc_preparation_20260928/validate_guides.py
```

重新运行矩阵/探针须使用新的目录或标签，不能覆盖冻结证据。[代码增量](gc-preparation-code.patch)、[指南增量](guide-update.patch)、[源码链接迁移](source-link-remap.json)与[文档检查](validation.json)分别记录实现和定位责任。文档检查不重新授予运行时或阶段资格。
