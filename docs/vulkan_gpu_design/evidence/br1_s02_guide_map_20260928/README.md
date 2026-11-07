# S02 修改指南与代码关系核对

本批为文档修改：新增 [01c：持久 session、稳定存储与 job 借用](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md)，并接回项目入口、指南目录、设计关系、待改代码入口、阶段对照和源码反查。没有修改生产代码、构建脚本或测试，没有新增阶段通过结论。

核对当前工作树，不读取归档。Git HEAD 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`；采用上一批相同的源码身份算法，包含五个尚未跟踪的生产/测试文件，差异 SHA-256 为 `f4564c579d730a9efd269269255136fbaa67feda9c27d995ee7330a04012ea94`。具体算法及身份见 [source-identity.json](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s02_guide_map_20260928/source-identity.json)；这只是确认本次没有改源码，不重新授予上一批构建或测试资格。

指南将 S02 拆为 SS1–SS10，逐项列出当前函数、待改行为、调用者/终结消费者和验收要求。单页 inline、冷热尺寸、原 write set/admission、Operation rollback、完整 exact cut 和真实存储预算均延用 92 约束。原 arena 的同步/目录契约、dense-index 遍历、冷槽搬移、range 的 move/rebind 及 iterator 后刷新均显式映射，避免仅换容器或延长对象寿命。

验证覆盖本目录所有指南、项目入口和本记录的本地链接/行号/片段锚点，15 个修改 ID 的目录对应、主题代码的反查覆盖、新指南 50 个源码定位的符号一致性，以及修改前后源码身份相同。结果见 [guide-validation.json](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s02_guide_map_20260928/guide-validation.json)，逐项源码锚点见 [source-anchors.json](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s02_guide_map_20260928/source-anchors.json)，文档差异见 [guide-update.patch](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s02_guide_map_20260928/guide-update.patch)。归档链接跳过，不读取其内容。

生成与核对脚本保存在本目录：`build_guide.py`、`integrate_guide.py`、`validate_guides.py`；前两者是一次性构建脚本，保留防重复保护。验证命令：

```text
python3 docs/vulkan_gpu_design/evidence/br1_s02_guide_map_20260928/validate_guides.py
```

未运行生产测试、性能 replay、Vulkan 或 TSAN；待补场景只指向现有测试扩展入口，不声称已经新增或通过。当前阶段和剩余交付仍只由 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)裁决。

首次文档检查先遇到尚未生成的 `guide-validation.json` 自身链接；该次结果保留在 [guide-validation-01.json](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s02_guide_map_20260928/guide-validation-01.json)。结果文件生成后重新核对全部链接，不豁免源码或其他文档链接。
