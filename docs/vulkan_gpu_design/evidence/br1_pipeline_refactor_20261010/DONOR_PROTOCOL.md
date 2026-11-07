# 旧目标交接能力判别：事前协议

2026-10-12；固定产品11c6895ddfeae074df727c76dcbf9e12988479ee。只构建隔离派生库，产品与原库不改。

问题：撤销旧Prepared proof之后、提交历史回收之前，源backing实际收费类是什么？现有物理独占与owner handoff的prepare/cancel是否接受它？下一次同页冷准备时原身份是否还在？若必须延长保留，则复用不是仅在prepareTarget加一个查找。

1. 从当前Publication接受点记录superseded handle，只保存诊断值，不保活产品对象。按publication实例/transaction/page索引；构造时清除地址复用旧记录。容量512，溢出拒绝本包，不扩容续采。
2. 两个位置观测：接受后原proof已撤销的即时位置；下一同页prepareTarget、取得write base以后。完整metadata快照验证Historical、authority、无capture/read lease/pin/pending last-use/active operation，无writer/handoff。该快照只是观察，不能授权未来写入。
3. mode1只记录逻辑和backing类；mode2另对已有provider/binding执行原prepareHandoff→prepareBackingHandoff→tryClaim→全部cancel，绝不retag、改字节或跳过原回收。先释放store owner gate，并保留原activeProviderCalls/调用责任；重取metadata快照核对观察后身份。允许回收在窗口中抢先，单列stale。物理cancel后验证旧handle仍有效；owner取消后非MetadataArena的live/reserved应保持（无外部并发资源控制用例），容量缓存新增单列，不伪称观察器无副作用。
4. 使用原公共64case夹具，加可选H1首个Prepared结果的clone或原生tile读保持至后续覆写结束，验证旧像素、最终像素及undo/redo。只将原64格中已合格60格视为跨实现同义；新held控制是current自身合同验证，不授upstream性能。
5. 固定上限：原64格mode1/2各一个能力过程；正式六过程：普通、H1 held clone、H1 held tile各mode1/2一次，正反case顺序交替。共8过程；退出/超时/加载身份/全部case断言/计数守恒任一失败即停。构建或夹具错误保留后可修订新目录；禁止删除原失败。每过程120秒上限，超时kill/reap。
6. 本包不报告CPU/指令收益，不用资格查询成本给完整复用定价。没有达到写/retag原子安装，不声称“合法复用实现成功”。计数仅说明观察运行中的原组件可接性、原生保护及保留依赖；不移授plain调度比例。按事实更新原§19.12/33行，不另起实施状态表。
7. 同时建立有界参考状态探索，明确原owner持有、预算类、逻辑删除/claim/接受/取消/close的目标交接。模型只证明其建模域，不代替实际provider/metadata/并发验证。若发现现有接口已可prepare，纠正此前将枚举边界泛化成实际拒绝的推断。

开跑前补充：原后台仍会在释放owner gate的观测窗口中推进，所以全局payload live/reserved的变化仅记录为window changed，不能据此断言观察器泄漏。旧handle取消核验在原owner accounting claim释放前完成；后续metadata复核有独立after前缀，不重复计入即时资格分母。

停止后交付全部日志、库/对象/源码身份、计数与失败、可复算结果，以及已关闭/仍开放的具体设计缺口。净收益仍只能由后续完整合法替代的独立对照获得，当前不以本包制造生产收益。

r1构建记录：派生库已构建，夹具误用`KisSharedPtr::reset()`导致编译失败，未运行样本。r2仅改为该指针已有的空赋值释放方式，另开目录，保留r1源码/命令/失败。
