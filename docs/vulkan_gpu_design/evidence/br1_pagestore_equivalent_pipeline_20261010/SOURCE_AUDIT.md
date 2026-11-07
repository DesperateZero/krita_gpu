# 同义责任与代码差异审查（实测前）

本包按[§16.171](../../92_br1_m6_m8_execution_baseline.md#pagestore-equivalent-performance-scope)执行。P01只恢复clear拆分；P02发现不能仅据此宣布整笔已是纯PageStore对照。因此以共同data manager API矩阵作为本轮基础能力证据，freehand控制保留为业务旁证，不借改标签消除差异。

| 位置/责任 | 当前与upstream对照 | 归属与本轮处置 |
|---|---|---|
| `kis_async_merger.cpp::setupProjection` | 当前有限clear/首层融合；upstream先clear后合成 | 通用工作拆分。派生当前库无条件执行原clear，保留其它产品对象；生产不回退 |
| `kis_simple_update_queue.cpp` | 源码同一包围矩形算法 | 共同通用算法；不实施Q01–Q07，不领取减少区域收益 |
| `kis_brushop.cpp::addDabJobs` / paint device `partitionWriteRectsImpl` | 当前按存储页对齐、QRegion分区与多clip任务，upstream原pixel patch任务 | PageStore接线与页互斥限制的成本。保留并计入整笔替代总成本；不能因位于插件目录而排除，也不能假定任务数相等 |
| `kis_painter_blt_multi_fixed.cpp::applyDevice/bltFixedImpl` | 当前cursor与全范围准备、同一operation消费多clip；参数和compositeOp移出最内层 | 必要接线与可共有的参数外提混合。整笔不作纯后端归因；共同存储矩阵完全不经过此路径 |
| `KoOptimizedCompositeOpOver32.h` | 当前用向量select保持透明source的隐藏RGB，upstream原kernel缺此保证 | 通用正确性修复，非PageStore优化；不回退修复、不把新增成本自动归为PageStore。共同存储矩阵不调用compositor |
| `freehand_stroke.cpp` / painter strategy | 当前发布dirty前checkpoint、失败报告及历史终结支持 | 引入PageStore后的可见性/失败接线费用计入业务替代总成本；普通模式与persistent分开，fixture仍ordinary |
| `kis_stroke.cpp` / queue / scheduler | 新失败/取消/重试和checkpoint责任；原队列仍执行 | 必要接线的正常与拒绝路径需定价；不把整个scheduler的成本全部算新增，不关闭保证来构造快组 |
| `tiles3/kis_tiled_data_manager.cc::writeBytes/readBytes` | 同一公共矩形和字节接口；当前转原native operation、adapter与可见性发布，upstream逐tile读写 | 本轮共同语义主入口；API形状、输入、current读点相同，内部粒度允许不同 |
| backend `runCpuMutationOperation` / Store `beginWriteImpl/sealImpl` | 当前范围准入、整域可失败准备、独立目标、seal及原manager联合交付 | 核心替代协议，包括接线和完结；冷准备次数是实现结果，不预先当作必要版本数 |
| upstream `KisTile::lockForWrite` | 必要swap保护；共享时复验并clone/registerTileChange，否则复用 | 对应可写隔离和COW职责；观察真实写锁与实际clone，不能只把调用次数当复制 |
| 两侧memento manager / current PageStore history | 同一getMemento→write→commit→rollback→rollforward→purgeHistory | 共同已承诺的undo/redo能力；H=0/H=1分开，不用去掉history降低当前成本 |
| manager析构 / current backend closeSession | history/manager销毁有正常终点；当前close等待read/history/retirement责任 | 本轮计入销毁阶段并核对进程退出。全局pool/runtime和跨case尾另列，未证精确最终物理free归属 |

共同存储矩阵的控制变量为实际字节、K、覆写次数、current可见点、历史保留和生命周期。它不依赖特定draw kernel、dirty集合或任务拆分；因此可以证伪“所有基础差额都来自通用绘画算法”的解释。它仍只覆盖同步packed write/read及一个history起点，不能外推其它API、并发、GPU或整个M6。

P01/P02不要求把所有分支改动都反向移植到upstream。对基础能力能构造完全共同操作时直接测该责任；对实际业务仍未隔离的共有差异明确披露，避免无限扩充“公平基线”工程。优化接线导致的工作量变化仍须保留在真实业务结果中，不能只报告理想匹配组。
