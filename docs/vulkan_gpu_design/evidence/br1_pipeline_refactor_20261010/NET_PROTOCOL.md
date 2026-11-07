# 机制净账判别：aggregate-r0（采样前冻结）

r0在第一个off capability的case0停止：tiles3 pooler按其零memory-limit正常退出，观察器随后读取失效Mach thread port而报错。没有计时样本。r1为具名线程增加进入/退出RAII，在原线程退出前读取CPU并保留累计值；边界查询与登记/退出使用独立诊断registry锁，热scope不使用该锁。其余实验不变，r0全部源/库/输出保留；r1重新领取原固定68过程，不把失败样本混入性能估计。

产品仍为11c6895ddfeae074df727c76dcbf9e12988479ee，上游9a24ae0d8c070884fb013594191002e1a1b39a19。只生成派生源、库和两侧ABI夹具，不修改产品或原对象。以原8个公共存储case、每case四manager寿命及所有像素/历史断言为共同工作；这不是业务Stroke或正式M6验收。

修复上轮两个证据缺口：使用固定TLS累计桶、仅thread CPU两端时钟，去掉逐事件日志、wall时钟及标签；对reclamation job连同dispose/finished计费，保留原任务动态类型。worker、monitor、tiles3 pooler/swapper另外用Mach线程CPU边界读数计费，未覆盖线程仍列残差，不将等待当CPU。机制inclusive与exclusive分开，只加后者。

保留原case端点，再单列显式kisDrainPageStoreReclamation的尾账；upstream无该队列，执行空hook。drain只证明即时任务排空，不代表未来deadline或全部物理债务关闭。每case测量窗口从begin hook完成准备后到drain完成；线程快照与process CPU端点不同时刻的读数偏移显式保留为残差。manager四寿命、结果核验及原stage不改变。原端点、增广端点和旧批不得混加。跨case活动scope、容量溢出、身份/语义/退出错误均停止；不删除失败。

四侧current-off/current-on/upstream-off/upstream-on各一次capability，然后8独立顺序块，每块四侧排列及其镜像各一次，总68过程；case顺序随块奇偶反转。每过程120s timeout、kill/reap。产品、原库、派生源/对象/库/命令、夹具及加载依赖前后核验。构建、采样、分析顺序执行。

统计每侧块内两过程均值，配对差的中位数及100000次seed20261011的pointwise95% bootstrap；加法账用同8块均值，不能加中位数。粗责任解释要求各侧K16/W16/H0、H1的完整前台on−off区间落在±0.75ms；process CPU另报告，不以总量抵消证明每个桶无扰动。线程归因只在边界有效、无活动尾且过程扰动可解释时使用。失败则报告未知，不扩样到通过。

三层分别裁决：当前责任成本；同义upstream差额；合法替代净预算。upstream没有同名细桶时，只能给映射范围/包络，不能把上游整条write重复扣到多个当前子桶。没有实现可构造替代、必要剩余工作和新增尾成本的项，其净预算仍未知。本批优先证伪“4.6ms都是未知管理成本/遗漏尾”“冷准备都是可删”“读侧只是memcpy”，不预授优化收益或960次删除。

## r2：仅后台责任（r1分析后另行冻结）

r1完成68过程，H1前台on−off为0.591ms [0.112,1.987]，process为0.838ms [−0.007,2.735]，不通过粗门；不重试相同观察或增加其样本。off边界线程账把H1其他线程4.189708ms差额中的4.189938ms落实到reclaimer，线程/时钟残差0.000333ms；此线程归因来自off，不依赖逐事件时钟。r2只检验该责任的内部构成：复用r1当前全部派生对象，唯一改动是mode1在role0直接返回、不计前台scope。mode0与mode1均保留同一线程边界读数和drain。原r1全部失败门与数据保持。

固定current mode0/1各capability，之后8块×4镜像过程（偶0/1/1/0，奇1/0/0/1，case次序随奇偶），共34过程。原身份、timeout、语义、样本单位和bootstrap规则保持。K16/W16/H0和H1分别要求前台及process on−off区间都落在±0.75ms，才按该粗精度解释后台内部规模；不授小额净回收或前台桶资格。upstream后台只有边界线程费用，r2不重采其细分或混入新配对；r1同批off差額继续独立报告。若仍失败，停止本轮后台定价，保留计数/线程总责任，不扩样。

## r3：只核对物理生命周期数量，不再领取计时资格

r2完成34过程但联合扰动门仍失败（H1 foreground [−0.811,0.337]、process [−1.105,0.832]ms）；停止内部单价确认。具名worker的off总CPU仍有效，内部时长仅作描述线索。最后用4个固定过程current/upstream/upstream/current、mode3，只记录成功Fresh目标、tiles3物理创建/复制请求/free及provider retire调用次数，不为任何scope读时钟。两个重复仅验证数量与首尾守恒，无时间推断/置信区间；全部8case、四寿命、像素/历史/退出及库检查保持，case顺序按过程奇偶反转。目标是区分后台工作来自大量页面生命周期，还是相同页面数量下纯任务调度。只统计真实调用，不用cold次数替代物理分配，不把副本请求当真实新分配或计数占比当时间收益。
