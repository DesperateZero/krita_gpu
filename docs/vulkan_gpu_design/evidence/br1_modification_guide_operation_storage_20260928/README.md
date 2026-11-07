# BR1 修改指南：operation 资源准备映射核对

2026-09-28。本批为文档修改，交付 [01m / OP1–OP10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#operation-storage-map) 及其目录、前向/反向索引和阶段依赖导航。原 15 个修改 ID 与 stroke → undo/redo → context 顺序保持不变。

## 核对范围

- 当前 `runCpuMutationOperation` / cursor / packed 的 touched 与 changed 分配位置。
- publication 后的 presence 查询、wrapper/hash 增删及 extent 适配。
- 当前 lock-free hash 的插入/删除回收节点，以及另一种 hash 实现的 wrapper 构造。
- 原 checkpoint/finish、copy/fill/planar/clear 旁路、MR4 exact 字节恢复和原预算接点。
- 每个待改单元的原 owner、失败/取消终点、实施顺序和验证入口。

以上是当前源码阅读结论与待改要求。OP1–OP10 的准备/安装协议尚未由本批实现；没有新增运行时、零分配或性能通过结论。

## 源码身份与验证

HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。含未跟踪生产/测试文件的工作树差异 SHA-256：`e8618e8cce3069b5196f3aa9d8199803c7d495bb6372a879551190f591619009`。身份采集沿用上一批脚本的 `source()`，只读取函数，不重新运行旧矩阵。记录见 [source-before.json](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_modification_guide_operation_storage_20260928/source-before.json)。

[validate_guides.py](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_modification_guide_operation_storage_20260928/validate_guides.py)检查所有当前指南及 README/92 的本地链接、文档片段、源码定位、15 个 ID、OP1–OP10、前向/反向索引，并重新核对上一批保存的源码锚点。归档链接只跳过，不打开归档。加入导航导致的文档行号变化由 [document-link-remap.json](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_modification_guide_operation_storage_20260928/document-link-remap.json)记录。

执行：

```sh
python3 /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_modification_guide_operation_storage_20260928/validate_guides.py
```

结果与准确计数见 [validation.json](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_modification_guide_operation_storage_20260928/validation.json)，文档增量见 [guide-update.patch](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_modification_guide_operation_storage_20260928/guide-update.patch)。验证同时要求源码身份与本批开始时一致。当前构建 `USE_LOCK_FREE_HASH_TABLE=ON` 仅作为阅读分支依据记录，不代替另一配置的构建/运行资格。

本批不改业务代码，不重跑运行时矩阵，不修改之前冻结的证据。下一批实际实现从 01m 的 A 批开始，仍需绑定新源码、真实 binary、必要语义/故障矩阵与 allocator 探针；阶段资格继续由 92 裁决。
