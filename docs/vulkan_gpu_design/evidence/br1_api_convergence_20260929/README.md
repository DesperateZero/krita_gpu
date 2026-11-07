# API 收敛方案与文档映射核验

本次落实用户要求的明确收敛方案与类似 CODE_INDEX 的代码映射，仅修改指导文档；未修改生产实现、未运行新的产品回归、不授予新阶段资格。原 JP5 生产事实继续绑定原冻结证据。

- [方案与函数映射](../../br1_modification_guide/API_CONVERGENCE_MAP.md)：读取选择、adapter/bounds、单次交付、owner 接线、结果边界及条件删除；列出具体函数/caller、替代关系、锁与寿命、验收落点。
- [源码反向索引](../../br1_modification_guide/CODE_INDEX.md#api-convergence-index)：从文件和函数定位需要合并、迁移、删除或保留的责任。
- [领取清点](../../br1_modification_guide/CONVERGENCE_CHECKLIST.md#api-convergence-work)及 [92 §16.9](../../92_br1_m6_m8_execution_baseline.md#api-convergence-plan)：统一执行顺序；内部等价政策随本次修复收束，只有依赖模式迁移的外部 API 删除后置。

核验包含活动指南的链接、锚点、源码行号范围、空白，以及 JP5 清点中 124 个范围内文件的 SHA-256。源码链接还抽查了关键符号；它们是编辑入口，不代表整份文件或全部 caller 已逐行审计。没有读取 archive。

执行与结果见 [validate.py](validate.py)、[文档检查](document-check.json)和[范围内源码/关键符号检查](validation.json)。本次文档增量见 [documents.patch](documents.patch)。验证脚本不重写旧批次证据。[首轮检查](document-check-initial.json)仅因报告尚未生成而报其链接不存在，已修正生成顺序后重新核验。
