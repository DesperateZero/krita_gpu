# 完整最终输入直接接纳：事前范围与有限实验

父产品8198c36ed722030edae715b7423554036bf1bcf7；承接92 §16.172和T01–T08。本包优化PageStore公共存储替代管线，不使用绘画通用收益抵扣基础差额。

## 合法替代

packed producer对一个execution内的每个目标只写一次。完整页最终输入由同步provider初始化独立Fresh backing后，借原AdoptPreparedWrite直接接纳为私有Prepared；不再建立供外部修改的writer、源pin或临时writable guard。仍使用原selector、entry、descriptor、budget/backing ledger、proof、overlay、canonical及retirement。存在可恢复handoff时保留原路径，普通overwritePage可继续修改pending的合同保持。部分页/无同步payload能力也保留原路径。

这不是M7原地写。旧current和history保持独立，任何后页、proof、overlay、adapter或commit失败仍可沿原取消链退出。最终输入返回后不保存借用指针；不新增缓存、owner、许可开关或第二账本。

预测：每个命中的冷FreshPayload目标，metadata写生命周期Acquire/Prepare/BeginPublish/Publish四次转换合为一次AdoptPreparedWrite；取消原mutable source pin、writer reservation与临时写guard的获取/归还。目标generation/Fresh数量、输入字节、no-op比较、proof/seal/发布次数不变。K16/N16四寿命预测1024个目标命中，减少3072次该类metadata转换；960个相对upstream周转差仍存在。净时间未知，不能把全部8.256/6.976ms额外write时间当可回收预算。

## 索引和验证闭包

| 位置 | 本包责任 | 保留边界 |
|---|---|---|
| backend writeBytes / execution | 仅完整最终输入使用内部入口，一次key一次交付 | partial/no-op/legacy冲突/共同adapter保持 |
| session共同写准备 | 复用原selector和Fresh接纳，完成输入不暴露mutable guard | handoff/provider fallback不削弱；源码没有第二准备管线 |
| write coordinator | 复用AdoptPreparedWrite与default并发materialize修正 | 原state machine检查base/identity/physical ownership |
| seal / cancel | 完成输入跳过mutable publication，其余proof/overlay/终结共用 | 未交付结果可取消，旧view/history不变，预算失败可重试 |
| tests | 完整/partial、1/4/8/16BPP、后页失败、provider失败、旧reader、取消、seal重试/资源退出 | 原普通overwrite继续可改pending、handoff控制不回退 |

## 固定批次

先保存原image、构建命令/哈希与源码身份。构建和功能验证不与性能样本并发。先运行新增反例与原CpuMutation、tiles3 manager及物理claim/reader相关套件；必要修复保留全部失败。架构与结构检查按当前工程要求完成。

探索仅2个ABBA/BAAB块（8进程），公共8行同源夹具，判断净方向和代码价值；没有独立置信资格。若无正向证据或有语义/资源退化，停止候选并报告，不为成功不断换项。候选值得收益工程目标为K16/N16四寿命write节省至少0.5ms（约旧额外成本6–7%），它是选择目标，不改M6门。

功能与探索通过后，冻结源码再作独立确认：同公共fixture，8顺序平衡块，每块父/新/新/父或新/父/父/新，32进程；每进程8行，奇偶块反转case顺序。分析每块两过程均值的父减新，中位数与100000次固定seed20261010的pointwise95% bootstrap；write及完整case并列，setup/read/history/销毁作控制，不能把区间跨0称严格非劣。

同源码fixture再以新/upstream做8块32过程，用于更新差额而非把不同批次中位数相减。真实freehand为受保护旁证，4块16过程父/新对照，报告全部阶段，不授整应用门。机制独立2进程/版本统计准备/转换/pin/实际计划，不能用插桩时间定价。任何超时、非零退出、像素/身份不匹配停止该批并保留，修复后新批，不替换单样本、不追样到通过。
