# 管理管线实施蓝图的覆盖核验

产品固定`6644249a4cfd2c48225685a2c27f1a8318def1c3`，文档父`02f7383d8ebb3c139826623135255899cf7e18d0`。本轮交付[03f代码改动位置索引](../../br1_modification_guide/03f_cpu_management_cleanup_index.md)和[03g唯一追踪矩阵](../../br1_modification_guide/03g_cpu_management_cleanup_tracker.md)，产品改动0、产品测试/性能新过程0；未重跑或改写前一冻结证据包。

覆盖范围为原A–J十个责任的22子项、10条入口/终结路径、9项保留/相邻责任。逐项核对当前源码及consumer，补齐legacy已有页重复预留、alias与generic相邻窗口、四处descriptor清理及保留admission时空write-set交接。待证明项保留在矩阵，不默认为可安全删除，也不计新性能收益。

`audit.py`是只读源码/文档检查器，仅把结果写入本证据目录。它核对固定产品身份、未修改产品、索引/矩阵子项双向覆盖、父项A–J映射、状态和路径数、声明/生产consumer检索，以及本轮新增链接和源码行定位。[核验结果](audit-result.json)记录源码/文档hash与链接计数；[consumer清单](consumer-census.json)记录原rg命令、全部结果及逐命中的MP/R处置，不允许未分类命中。[源定位](source-locations.json)记录代码链接落点及源文件hash。

命令为`python3 docs/vulkan_gpu_design/evidence/br1_cpu_management_blueprint_20261008/audit.py`。这是本轮设计基线的覆盖检查，不会运行产品、不证明并发语义等价、不证明搜索覆盖C++所有动态调用或整个仓库无其它冗余。实现后须更新候选身份、重审caller并填03g的D/S/Q证据；不能用本次通过代替V3–V5。

首次关联文档补丁因API文档标题上下文不匹配被工具拒绝，未改变文件；修正上下文后完整应用。这不是产品/测试失败。机制四案例及19/132/96旧数量继续引用[上一冻结包](../br1_cpu_management_pipeline_20261008/README.md)，不算本轮新样本。
