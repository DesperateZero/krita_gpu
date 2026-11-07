# BR1 S03 / HX7：缺失 wrapper/key 的原 operation 准备

本批绑定已检出工作树；实现关系和下一批入口见 [HC1–HC7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#adapter-candidate-implementation)。最终验证已完成，阶段资格仍统一由 92 管理。

- 原准入内准备实际缺失候选；cursor/packed 成功交付只消费既有存储，暖页不创建 key record。
- 原 claims 覆盖 clear/trim、history commit/abort、restore 的初查与锁外准备后复验。冷候选拒绝正常归还未写 borrow，保留之前 pending。
- 两种 hash 模板消费一次，候选跨迁移、取消、竞争 winner 和旧表地址复用均有行为验证；完整 OFF 产品构建继续。

开发失败记录保留：首次双模板测试编译因类型别名冲突失败，改用测试内别名隔离；restore 初版测试错误地等待计时器构造观察，未进入目标窗口。修正为原 range 取得后的显式诊断边界后，通过无 transaction 的真实占用竞态测试。这些开发失败均保留。首轮完整矩阵的 clear/trim 旧测试仍预期部分写入后取消，本批已改为整索引变更前拒绝；随后将这些 case 改为严格断言 generations/pages/removals 零变化，并保留 planar/removePages 的部分失败取消检查及全部像素/历史检查，再重新冻结与验证。

最终资源探针只覆盖 MutationAdapterPrepare → Prepared 与 MutationAdapterInstall → Installed。候选的清理、完整 publish、未迁移语义入口、冷热锁争用、cache 释放和完整 stroke 不包含在局部零分配结论中。stroke 优先级不变；完整预算、OP6/OP7、真实 brush owner/current/source/producer、M6–M8、TSAN/Vulkan/Fresh 2% 与 BR1-PERF 继续。

进一步资源寿命复核发现：原 extent 准备若发生在页准入前，abort 可在其间替换 extent。最终源码把 cursor/packed 的实际 extent 准备也移入原准入，新增两个准入前 abort 的回归；下述最终矩阵和探针须使用这一版源码。

## 最终同源结果

源码 HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09` 加完整工作树差异 SHA-256 **`7c5e6e2e96f5e56c2325ed74c78184cb12da058749910bce19be0aaa7881523a`**；差异包含未提交实现，HEAD 本身不是本批源码身份。QtCore SHA-256 `cd0a48d2948af55889625ae0750a7d08895068deae9b6e85bdc3e1fac6dc9434` 与上一批相同。

| 验证 | 结果与边界 |
|---|---|
| 20 个目标 × arm64/x86_64 | **9,034 passed、0 failed、0 skipped**；实际默认笔刷插件、结构检查、六项工具自测及最终 Ninja no-op 通过。 |
| 62 个最终探针 | 全部通过，重新绑定最终源码和实际二进制/QtCore；包含全部继承探针。 |
| 真实 native manager 安装 | 每架构 192 次，4 种 bpp × 4 种页数 × cursor/packed/history × 4 次改写；install allocations/frees 均为 0。 |
| 暖准备 | 每架构 144 次 allocations/frees 均为 0；48 次冷准备实际分配。正控制各产生 1 次分配 / 8,210 B。这些是无争用受测边界，不包含候选析构和全链性能。 |
| 真实逐点分配拒绝 | 每架构 **510 个拒绝 + 9 个成功对照**；body 未执行、此前笔迹保留、正常重试，最终 tracked live blocks/bytes 均为 0。 |
| 代码结构 | 87 TUs / 1,796 APIs / 19,296 reverse edges / 17 callbacks；21 manifest / 25 ownership / 16 census / 19 intrusion。manager 标识上限经 92 显式审查 **23 → 25**，3 个 includes 与类型集合不变；manager 无新字段/TLS，其他侵入及布局上限不变。 |

首轮完整矩阵 **9,014 passed / 16 failed** 保留在 checks-01；八个早拒绝计数断言每架构各失败一次。最终 checks-02 包含严格的零修改断言和新增 extent 准入回归，不隐藏失败。两种 hash 模板通过不代表完整 OFF 产品构建；完整实际预算、联合发布和 M6–M8 仍开放。

- [完整矩阵与身份](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_candidates_20260928/checks-02/manifest.json)
- [源码身份](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_candidates_20260928/checks-02/identity.json)
- [冻结源码差异](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_candidates_20260928/checks-02/source.patch)
- [本批代码增量](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_candidates_20260928/adapter-candidates-code.patch)
- [最终探针清单](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_candidates_20260928/probes-manifest-02.json)
- [测量范围与剩余项](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_candidates_20260928/evidence-scope.json)
- [指南校验](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_candidates_20260928/validation.json)
- [指南增量](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_candidates_20260928/guide-update.patch)
