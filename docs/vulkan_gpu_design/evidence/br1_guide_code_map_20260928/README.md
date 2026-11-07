# BR1 修改指南：当前代码关系核对（2026-09-28）

本次交付是文档定位与待改责任整理。保留原 15 个 S/U/C/V 修改 ID，补充 [01g / MD1–MD7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01g_multi_dab_and_painter_scope.md#multi-dab-map)，串联两个真实默认笔刷调用点、painter/坐标适配、原事务、调度和失败/资源终点；同步更新目录、设计关系总表、待改入口、反向代码索引和阶段依赖。

本次没有修改生产代码或测试，没有运行新的业务矩阵。代码中已有的 multi-dab 改动尚未验收，既存 focused 失败记录按原样保留；不把文档检查计入 CPU、Vulkan、M6–M8 或性能资格。92 的既有冻结证据不覆盖未验收工作树。

验证命令：

```sh
python3 /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_guide_code_map_20260928/validate.py
```

- [validation.json](validation.json)：目录链接/片段、15 项正向映射与四项必填关系、主题到源码反向覆盖、MD1–MD7 和 32 个具体源码定位；保存文档/映射源码哈希及代码未改动检查。
- [source-link-remap.json](source-link-remap.json)：根据 multi-dab 改动前源码与当前源码，修正 12 处发生位移的旧链接；未读取归档。
- [guide-update.patch](guide-update.patch)：相对此次文档整理前的变更，用于区分已有工作与本次交付。
- [source-before.json](source-before.json)、[before-docs.json](before-docs.json)：本次开始时的源码差异身份和文档快照；HEAD 相同不等于工作树相同。

检查仅证明定位、覆盖和文件关系。除 MD 的具体符号核对外，其他已有源码链接仅检查目标存在与行号范围，不能据此声称逐一重新审查了所有旧调用链。改代码后需更新定位并重新取得对应运行证据。
