# BR1 修改目录与真实 stroke 代码关系核对

本批仅修改文档。入口为[修改指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)，新增 [BC1–BC10 联合接线指南](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01j_real_stroke_integration.md#stroke-integration-map)。设计、实施状态和阶段资格仍以 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)及当前代码为准。

目录将设计依据、15 个待改项、函数级改法、源码反向索引与 M1–M5/M6–M8 依赖分开导航。BC1–BC10 进一步列明原事务、painter 借用、异步 jobs、1px 同步旁路、读选择、producer/display cut、终结、多设备、资源与真实 scheduler 验证之间的关系；同步更新 NEXT_EDITS、CHANGE_MAP、CODE_INDEX、STAGE_MAP、MD/PG 指南和主入口。

核对中修正了“普通/镜像有两个直接 painter 调用点”的过时定位：当前二者共用 `addDabJobs`。明确记录持久事务尚未检查 offset/wrap、mask renderer 设备与主事务 target 不同，以及两个业务 replay/benchmark 的 broken-test 注册；这些是待实施边界，不表示本批修复了生产行为。

验证命令：

```sh
python3 /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_guide_stroke_chain_20260928/validate_guides.py
```

- [validation.json](validation.json)：全部目录文档的本地路径、行号、章节锚点；15 个修改 ID 及领取字段；正反向索引覆盖；BC1–BC10 与 35 个新源码定位。
- [stroke-chain-anchors.json](stroke-chain-anchors.json)：35 个入口的实际源码行，涉及 16 个源码/构建文件；原 MD/SR/PG 映射也只读复验，不覆盖先前证据。
- [source-before.json](source-before.json)：文档编辑前的 HEAD 及 `libs/plugins/build-tools` 中已跟踪与未跟踪文件哈希；检查确认编辑后未变。
- [guide-update.patch](guide-update.patch)：相对此次开始前工作树的文档增量；原有未提交改动保留。

检查跳过归档链接且不读取归档内容。不运行构建、运行时测试或性能探针；文档可导航与符号存在不授予实现、性能或 M6–M8 资格。新增指南中的完成判据均为后续实施要求。
