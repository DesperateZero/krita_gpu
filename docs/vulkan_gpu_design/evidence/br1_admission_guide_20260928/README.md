# BR1 修改指南：准入责任映射核对

本次整理的是修改指南与当前代码的对应关系。总入口为[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)，15 个修改项仍按 stroke、undo、上下文切换排序，阶段和性能资格仍由 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)管理。

本次增量将 S02 下一批准入要求展开为 [01c §11 / J1–J8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-implementation-map)：claim 存储、三类 caller、activity、session/control block、publication 回调、原终结责任、实际预算与生产验证。每段包含当前代码、待改行为、联动终点和验收要求，并列出准备拒绝、复验失败和取消压力下必须保留的状态。修正了指南中仍把 live 枚举写成密集索引依赖的旧表述。

导航同步到 README、CHANGE_MAP、NEXT_EDITS、CODE_INDEX、STAGE_MAP 和项目文档入口；未另建阶段状态表。修改前文档快照为 [before-guides.json](before-guides.json)，本次增量为 [guide-update.patch](guide-update.patch)。

核对命令：`python3 docs/vulkan_gpu_design/evidence/br1_admission_guide_20260928/validate_guides.py`。脚本检查 15 项正向映射、领取字段、主题文件的反向索引覆盖、本地文件/行号/章节锚点，以及 J1–J8 新增源码链接处的实际符号；结果见 [validation.json](validation.json)与 [mapping-validation.json](mapping-validation.json)。遇到 archive 路径即跳过，不读取归档内容。

文档编辑前后用既有 source 捕获函数比较 HEAD、工作树差异及未跟踪生产/测试文件，源码身份保持 `796219267176e019bb27b18c811250c8057fff56d79c82c329551dfcedfaf7b5`。本次只进行文档与源码定位核对，没有修改生产代码、运行生产构建/测试或授予性能资格。
