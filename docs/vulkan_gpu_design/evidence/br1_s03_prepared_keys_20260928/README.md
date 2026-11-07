# S03 / OP4：HX6 跨 job key 预留验证

2026-09-28，HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09` 加未提交源码差异 SHA-256 **`a101246c6d4c827c298964b992bcc148f9e7395bf085b410802d1a006dd9ec8d`**。本批完成原 ConcurrentMap 的可选预留记录及真实 tile hash 的兼容消费/关闭；**8,912 passed、0 failed、0 skipped，56 个最终故障/分配探针通过**。未提交、未切换分支；原有工作树修改保留。

当前修改关系见 [HX6 §9](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#prepared-key-implementation)。默认 manager/brush 尚未调用 prepareKey，HX7/OP6/OP7/HX9、M6–M8 和 BR1-PERF 均未完成。

## 实现与边界

- 原 cell 暂存 PreparedEntry 标签地址，逻辑 payload 仍唯一；同 key token 共用记录，迁移传递同一地址。最后 token 释放后恢复普通值并交原 QSBR。
- token 不保活旧表、不持 raw guard 穿过 kernel、不授予 writer 或 payload lifetime。安装只进入短 key gate，不调用可能分配的 insertOrFind/participate。
- get、原 Mutator、iterator 处理临时表示；逻辑空预留不增加 tile 数或通知。迁移 acquire 顺序带入记录初始化。
- close 要求正常 map 用户/迁移 worker 已静止，允许 token 留存/收尾；撤销旧记录后 drain，晚 token 对已销毁/同地址新表均拒绝写入。
- 真实 rebound allocator 存在于记录内，直到 grace 与 token 引用都释放才 deallocate。两架构普通/可预留 cell 均为 **16 B**，默认 allocator 的记录为 **136 B**；每个活动预留 key 一条，非每 token 一条。生产共享收费和全部新旧表峰值尚未接入。
- key gate 存在抢占/竞争等待，当前没有 lock-free 或固定尾延迟资格；最终 stroke 性能仍须实测。普通暖 lookup 的新增标签判断也要纳入控制组。

## 本批验证

| 范围 | 实际结果与身份 |
|---|---|
| [完整矩阵](checks-01/manifest.json)、[源码/库/测试身份](checks-01/identity.json) | 20 个 Qt 目标 × arm64/x86_64；共 44 条记录，8,912 passed、0 failed、0 skipped。包含原 painter、history、scheduler、tiles3、PageStore、brush 与新增 8 个 case；实际最终 Ninja no-op。 |
| [56 个最终探针](probes-manifest-01.json)、[整体源码身份](probes-source-01.json) | 原 54 个探针重新构建并绑定当前源码/库；新增两架构 prepared-key 实际 allocator 探针。每条 identity 保留命令、探针/interposer/binary/依赖哈希。 |
| [arm64 新探针](install-arm64-prepared-keys-01.log)、[x86_64 新探针](install-x86_64-prepared-keys-01.log) | 各 43 次实际分配拒绝、3 个正控制；涵盖记录准备、连续迁移/overflow 的失败后继续或直接销毁。每轮安装与最后 token 释放 allocator calls/frees 均为 0，root/job 未被推进；退出 tracked blocks 为 0。 |
| 晚 token 与 allocator owner | Qt case 验证 allocator owner 跨 map 析构存活、raw reader 延迟回收；探针确认表销毁后仅记录的 1 个 tracked block 留存，晚 token 释放后为 0。 |
| 同 key 竞争与 ABA | Qt case 覆盖多线程共享记录/释放、winner 保留、后台迁移/GC、close 交错，以及同一地址构造新表后的旧 token 拒绝。 |
| [调用图](graph-01.log)、[结构门](baseline-01.log) | 87 TUs、1,794 APIs、19,169 edges、17 callbacks；21 manifest、25 ownership、16 census、19 intrusion。更新内容指纹，未扩大布局或侵入门槛。 |
| QtCore | 沿用已验证运行库，SHA-256 `cd0a48d2948af55889625ae0750a7d08895068deae9b6e85bdc3e1fac6dc9434`；本批未更换依赖。原锁失败及修复因果记录留在 [Qt 证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_extent_lock_audit_20260928/README.md)。 |
| [冻结事实核对](evidence-scope.json) | 比对最终源码、所有矩阵/probe 库和 binary、no-op、diff --check；阶段与性能资格仍为 false。 |
| [文档检查](validation.json) | 15 个修改 ID、指南到代码/反向索引、符号行号和片段核对；不读取归档。 |

[产品增量](prepared-keys-code.patch)、[指南增量](guide-update.patch)、[行号迁移](source-link-remap.json)分别保存本批变更。初次构建与 focused 日志保留，完整资格以 checks-01 和最终 56 探针为准；初次探针发生在补充布局输出前，不能替代最终探针身份。

## 下一批及未验收范围

继续 HX7：原 manager/operation 在首字节前准备 wrapper/key/retirement/通知及其 owner 寿命；OP6/OP7 联合 canonical 与 adapter 安装。HX8 仍要交付另一种 hash 配置；HX9/S10 仍要接共享预算、真实峰值及有界维护。默认长 stroke、current/read/producer cut、M6/M7/M8 及正式 BR1-PERF 继续。当前本地 ON 配置回归不授予 OFF、Vulkan、TSAN 或性能结论。

本批复核入口：

```sh
python3 /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_prepared_keys_20260928/finalize_evidence.py
python3 /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_prepared_keys_20260928/validate_guides.py
```

上述脚本只应在本批源码仍匹配时运行；后续变更须新建证据目录。矩阵与探针 runner 拒绝覆盖已存在输出，历史失败与旧资格原样保留。
