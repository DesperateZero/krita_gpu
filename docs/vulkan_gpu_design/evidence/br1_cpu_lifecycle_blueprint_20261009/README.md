# CPU全生命周期蓝图：源码与一致性核验

交付[03h理想算法](../../br1_modification_guide/03h_cpu_lifecycle_ideal_blueprint.md)、[03i代码/删除索引](../../br1_modification_guide/03i_cpu_lifecycle_edit_index.md)、[03j唯一追踪矩阵](../../br1_modification_guide/03j_cpu_lifecycle_tracking_matrix.md)。产品固定704d96e81cf29d16191bc3db8785859d79775e27/tree4e7fc164db46c02b968fdd04400b9e4402e289d0，外层文档父c2556c725d4ff8bd63fe09535694c6bf97f7f3b6；未编辑产品或运行新产品测试/性能过程。原对账与108过程证据继续保留在[成本账](../br1_current_upstream_cpu_ledger_20261009/README.md)。

本包10个责任族、28核销项、12路径和七类后台consumer，覆盖最小变化字段、分片组织、准备/接纳/失败/门外清理、通知及最终free。19项设计固定待实施，5项待证明，3项有具体consumer保留，1项完整交付核验；状态只在03j演进。数量公式独立于时间预测，没有新增ms或百分比承诺。

复算命令：

```sh
python3 docs/vulkan_gpu_design/evidence/br1_cpu_lifecycle_blueprint_20261009/audit.py
```

[audit.py](audit.py)只读产品与活动文档，只在本目录写派生JSON；检查固定产品HEAD/tree/无tracked修改、算法/索引/矩阵ID双向覆盖、状态/路径/后台责任数、新文档本地链接及源码行落点、原测试函数定义、executor和metadata关键符号的全部检索命中归属。[audit-result.json](audit-result.json)保存结果/源hash，[source-locations.json](source-locations.json)保存真实源行文本，[consumer-census.json](consumer-census.json)保留命令和每条命中分类，[test-locations.json](test-locations.json)记录测试位置。

本检查不构建/运行产品，不证明并发语义或收益，也不证明关键词检索覆盖全部动态C++调用/全仓库冗余。实施后须在新候选记录D/S/Q/P并重新审查全部consumer，不能把本次链接/源码核验当安全验证。带序号源位置以此固定tree为准。

编辑期间首次导航补丁因NEXT_EDITS整行上下文未匹配被工具拒绝，整份补丁未生效；核对后重新应用。该记录不是产品失败、性能样本或测试次数。

首次审计脚本误将无空格的Markdown表分隔行排除后又跳过两行，导致漏读首个子项并主动失败；改为按全部表行解析后通过。最终检查还覆盖原StateMachine全部转换kind的唯一归属，条件项不因未实施而从全集中消失。
