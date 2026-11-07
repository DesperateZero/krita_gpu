# 全流程账本复核：仅观测基线，先于优化选择

用户要求先完整理清流程和数据，再按最优设计实施。本包冻结任何新优化原型及产品改动；之前“完整身份复用优先”降为待比较设计，不预选赢家。产品11c6895ddfeae074df727c76dcbf9e12988479ee及原库不变，upstream9a24ae0d8c不变。执行索引仍原33项，新增的是证据覆盖视图，不建立第二实施状态矩阵。

先重算原8case同批off线程差额和前台阶段账，核对块级加法、阶段/线程分母、扰动失败、净价区间及已撤回候选。旧170、106、56、44过程保持各自身份，不跨批相减或用其区间端点凑预算。当前责任、相对upstream额外责任和合法替代净收益分开；没有合格价格的格子写未知，不因安全或结构已完成而写零。

唯一新增运行是**基线生命周期普查**：沿原8公共case、4manager寿命，两次current与两次upstream，顺序C/U/U/C，case按过程奇偶反转。使用原mode3计数框架，不增加热路径时钟，不读取运行时间作价格。保持像素/undo/redo/最终销毁和原显式drain，不替换算法或禁用保证。120s timeout、kill/reap、实际库/依赖及源哈希校验；无构建并跑，无失败排除，无数量达标后的追加样本。

当前新增计数位置：

- Provider：binding成功创建/析构、成功adopt、新physical登记/最后解绑、实际allocation提取、析构剩余allocation。
- Owner：实际backing/physical插入与提取、sealed proof插入/撤销、析构剩余backing/proof。保留两次footprint及原domain admission，不改准入。
- Metadata：`ShardRecordStore::putReserved`实际新增/更新、`remove`实际slot删除；析构前原footprint中剩余versions/replicas，区分逻辑default和非default。它们是slot周转，不默认等于唯一generation。
- Descriptor：候选节点实际emplace、安装、显式删除、候选显式discard；唯一实体consumer在Store，派生Publication析构计剩余map节点，Store/Publication一起重编保证观察实际执行。
- Completion：成功Pending发行。原Fresh/rows/provider retire/free计数保持。upstream只使用已有同义payload副本/free计数，不伪造同名provider/metadata事件。

数量假设：本fixture每case非默认Fresh `F=4K(W+1)`；provider/owner无alias时预计各有F次建立和完整退出，binding在drain终点归还。metadata和descriptor可能包含虚拟default、投影重建和最终容器释放，不硬套F；先按真实创建→移交→显式删除/析构方程对账。尝试与接受分开，未找到最终consumer则留残差，不把残差强归GC。计数扰动可能改变worker分工/重试，两个重复的角色分布与总数均保留；重复一致只证数量，不构成时间置信区间。

闭环定义：①同义工作与输入、可见性、失败、终点；②阶段总账与线程总账；③对象/身份/物理字节和资源终点；④互斥机制增量与锁/调度事件因果；⑤所有设计在相同合同下的完整流程/必要工作/新增工作/资源/失败比较；⑥选定设计的独立净价和控制。只有前两层或局部数量闭合，不叫完整净账。

本普查补③的有限公共矩阵，不能覆盖完整copy/clone/default/partial/import/raw/swap/pressure/held-reader业务，也不能把计数转为④或⑤。完整覆盖视图必须列出这些真实缺口、每项可以改变设计选择的观测与停止标准；数据尚不齐时不产出“已最优”或新产品蓝图实施授权。已有普通安全矩阵不是这些路径的性能价。

r0在任何编译/运行前因binding析构是单行定义、构建器预期多行而拒绝，冻结源保留。r1修正精确锚点；同时静态确认metadata `remove`的identity可能借自即将删除的record，在erase前读取default标记，避免观察器读取已销毁记录。没有改变产品语义或样本数量。

结果审计的措辞修正（不改冻结观测代码或数据）：上文metadata“新增/更新”描述了putReserved入口；本次新增计数实际只统计成功新slot，未计原slot更新次数。descriptor安装计数位于同一锁下先确认目标不存在再插入的分支；候选交换与其他RAII丢弃未作为通用全路径计数。Pending只统计成功发行，并未补逐ticket终态。因此只对实测fixture的上述数量方程闭环，不宣称全部管理对象已普查。本轮r0工具错误未单独写为原始日志，保留其失败源码与协议及此说明。
