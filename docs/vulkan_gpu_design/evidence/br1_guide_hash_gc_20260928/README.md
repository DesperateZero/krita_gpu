# BR1 修改指南：hash/GC 代码关系核对

本批补齐[修改指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)中的 [OP4 / HX1–HX10 逐函数关系](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#hash-storage-map)，并同步 CHANGE_MAP、NEXT_EDITS、CODE_INDEX、STAGE_MAP、01m 和项目入口。15 个主修改 ID 及 stroke → undo → context 的优先级保持不变。

核对将“在 map 变更前准备回收记录”和“在首个像素前准备全部 operation 安装资源”分开验收。QSBR 的工作树草稿已有接口，原 hash/迁移调用者尚未改用；文档明确保留其未验证状态，以及真实表容量、通知、manager/table 寿命、预算与发布协调的剩余责任。没有将上一批 extent 的构建资格沿用到当前草稿。

本批只编辑文档及文档检查材料，保留开始时所有未提交生产代码。验证命令：

```sh
python3 /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_guide_hash_gc_20260928/validate_guides.py
```

- [validation.json](validation.json)：全目录本地链接、行号、锚点、15 个主 ID、10 个 HX 单元及源码正反向索引覆盖。
- [hash-gc-code-map.json](hash-gc-code-map.json)：每个 HX 的当前段、具体修改、下游验收及源文件入口行/原文/哈希。
- [source-before.json](source-before.json)：文档编辑前 HEAD 与生产源码/构建脚本身份；校验结束后逐文件比较，确认未改动。
- [guide-update.patch](guide-update.patch)：相对于本批开始时工作树的文档增量，保留前序证据。

检查不读取或跟随归档。本批没有运行构建、容器测试、行为/故障测试或性能探针；映射存在及链接有效不能授予 OP4、M6–M8 或 BR1-PERF 资格。
