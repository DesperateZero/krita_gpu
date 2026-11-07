# BR1 修改指南目录核对

本次仅整理文档与待改代码段的对应关系。入口为[修改指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)，设计与阶段资格仍由 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)管理。

- 15 个修改 ID 按 stroke、undo、上下文切换排序；CHANGE_MAP、NEXT_EDITS、主题指南、CODE_INDEX、STAGE_MAP 分别承担设计追踪、领取、具体改法、反向定位和依赖顺序。
- [S02 §9 / A1–A7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#reusable-slot-integration)补齐当前原语与待改消费者的逐段关系；明确索引、冷槽、guard、admission、部分取消、seal/detach 和验证必须联动。
- 修正文档中的源码身份边界：第一批已验证差异 `4d0db8a75988529ce53adad9ed1af976cf267fb6ec9bd804f392a2393fa29fac` 不代表当前未验收 slot 草稿。核对时 HEAD 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`，当前源码差异见 [source-before.json](source-before.json)。

[validate_guides.py](validate_guides.py)检查本地文件/行号/章节锚点、15 个 ID 覆盖、每项领取字段、主题到反向文件索引覆盖，以及新增 S02 段的源码符号。脚本沿用第一批的源码捕获方法，比较文档编辑前后包含未跟踪生产文件的差异哈希；不执行旧构建脚本或覆盖旧证据。

运行：`python3 docs/vulkan_gpu_design/evidence/br1_guide_directory_20260928/validate_guides.py`。结果见 [validation.json](validation.json)，逐段源码定位见 [mapping-validation.json](mapping-validation.json)，本次增量见 [guide-update.patch](guide-update.patch)。

本次不运行生产构建/测试、性能探针或架构资格门，不声称原语已经正确接线。链接检查只证明文档可导航和列出的符号存在。归档链接遇到即跳过，不读取归档内容。
