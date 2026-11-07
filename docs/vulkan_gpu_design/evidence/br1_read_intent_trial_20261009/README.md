# 技能试行：未消费 before 读者的合法替代与净价判别

本轮从“外框哪里慢”推进到一个**有明确消费者、可构造替代、实际删量的因果原型**：painter只读取current时，不准备其不会消费的before。实测删除18次before捕获，整个Stroke的before页获取80→0，current页获取保持96；但固定时间实验没有取得稳定净收益，**不准入产品改造，也不升级技能**。这不是证明该项零收益，更不是证明剩余upstream差额都必要。

产品保持`d182a34bd0196079bc40d2ab7d00b8e326e4a58a`，tree `e03a63d2a33324a55c72b7eb8ec097deab96b171`；文档父`2c1a93ad4`。原库SHA256 `da4304d429134da577087e15004b4d98d93b7fc5c97a1bf6d8da4f4a615d66d1`。产品/产品测试改动0，只有三个显式列出的派生TU和实验辅助代码。当前裁决在[92 §16.162](../../92_br1_m6_m8_execution_baseline.md#read-intent-selection-trial)，[协议](PROTOCOL.md)先于构建和运行冻结。

## 1. 从消费者推导，避免再按大桶领取收益

| 必要事实 / 原消费者 | 当前实现 | 构造的最小表达与边界 |
|---|---|---|
| `bitBltImpl<false>` source及mask | `createRandomConstAccessorNG`承诺current和before；调用者却只用`rawDataConst` | 受限局部读者显式要求current；同一构造时点、publication读锁、原current cut不变 |
| `bitBltImpl<true>` source | 只用`oldRawData`，但通用factory也构造两种视图 | 本轮保留；不能把current替代误用到before消费者 |
| 通用accessor的外部调用者 | 可在构造后任意选择current/oldRawData | 保留双视图合同；不得延迟到首次oldRawData才捕获，从而改变cut |
| cursor cache miss | current获取后`beforeMatches`解析；不同版本时再取before页 | 受限current读者无需before解析/页guard；保留current的缓存、物理pin、generic fallback和最终释放 |
| 历史、晚发布、wrap及legacy | original scope固定选择；live legacy writer不走immutable scope | 不合并不同真实cut，不改变existing scope验证和legacy旁路；wrap共享选择需在产品实现中明确贯穿 |

当前读者在painter局部创建、局部使用并析构，不返回或被异步回调保留；pixel callback同步消费。只有编译期false source和只用current的mask可取得本次删除许可。原型用短暂TLS把构造意图传入backend，作用域结束恢复旧值；没有修改对象布局或公共factory。它只用于定价，**不允许作为产品方案保留隐式TLS或环境分支**。before缺席后沿既有alias规则返回current；这些受限对象的oldRawData不再具有通用语义，所以必须由真实消费者边界限制。

取消、准备拒绝、关闭和current失效仍由原scope/guard处理；跳过原本不会消费的before也可能消除其独有的分配拒绝，这属于受限读意图允许的变化。普通双视图的失败传播不变。当前匹配fixture没有证明所有并发/压力/wrap反例，不能据像素通过授生产资格。

竞争解释R2“本例根本没有重复before”被计数否定；R3“删量存在但价格不足或难以分辨”仍成立。另两类外框没有成为默认赢家：cold中的Page、descriptor、binding承担不同寿命与解锁后验证；operation的reservation、session、execution承担接纳、取消与guard尾。尚未构造可以删除整个责任的合法算法，约0.88/0.97ms桶价不能作重写预算。已经完成的metadata、base hint、claim与薄状态项目不重领。

## 2. 原型索引与责任追踪

此表是**判别原型**的唯一状态表，不是获准待实施清单，也不重开03j。

| 位置 / consumer | 本轮动作 | 状态 / 产品化欠项 |
|---|---|---|
| `kis_painter.cc:bitBltImpl` | false source和mask构造处标识current；true source保持 | 派生实现完成；产品需显式factory参数或受限类型，去TLS |
| `KisTiledDataManagerPageStoreBackend.cpp:captureIteratorReadScope` | 非writable/非existing/非live legacy后，仅eligible跳过before capture | 派生实现完成；existing选择兼容性、拒绝和late publication需产品反例 |
| `KisPageStoreIteratorReadScope.cpp:readPage` | 仅加计数；原current/alias/guard不变 | 数量验证完成；未新增缓存或owner |
| `kis_paint_device.h/.cc`、`kis_paint_device_strategies.h`、random/wrapped accessor、base iterator、manager转接 | 本轮无产品修改 | 只有净预算获准才迁移显式意图；通用默认双视图保留 |
| last cache pin / captured view / history cleanup | 仍随原accessor和scope析构完成 | 匹配fixture销毁/退出通过；生产全生命周期资源/晚guard验证未领取 |

## 3. 预测删量与实际删量

协议给数量公式而没有伪造毫秒预测：E为eligible且有activeHistory的构造数，D为其中before不同的cache miss数。预期capture少E、未消费before页获取少D，必要current工作不减。原型用于取得净价，不能把“尚无单价”作为大包实施许可。

原库1过程、同一派生库计数A/B各1过程，共3能力过程。A保留两种读视图，B启用受限current。

| Stroke计数 | A | B | 解释 |
|---|---:|---:|---|
| painter current source构造 | 19 | 19 | 真实业务读者未减少 |
| eligible scope | 19 | 19 | 全部进入预定backend路径 |
| 原有activeHistory的eligible scope E | 18 | 18 | 两边相同 |
| 跳过before捕获 | 0 | **18** | 数量预测兑现 |
| 全部iterator current页获取 | **96** | **96** | 保留原current工作 |
| 全部iterator before页获取 | **80** | **0** | 该fixture的额外before读取消失；不是80次payload分配或80份复制 |

计数是各1过程的机制证据；最后两行是全程序阶段聚合，没有逐读者归属，不能外推任意工作量的D。计数中Setup没有受限读者；Redo有1次current source但没有activeHistory，删量0。bitBlt old source/mask未命中，因此不宣称它们在本fixture取得收益。

## 4. 固定时间实验：删量确定，净收益未决

关闭计数后，同一派生库固定4块ABBA/BAAB/ABBA/BAAB，共16过程。没有逐页时钟；关闭后的探针函数空调用仍存在，原型价格不直接等于未来显式API产品价格。探索δ=0.3ms，只用于判断跨factory/iterator/backend迁移是否值得；不是通用阈值或M6门。

| 块 | A Stroke CPU均值 | B均值 | A−B节省 |
|---|---:|---:|---:|
| 0 | 16.7850ms | 15.8290ms | +0.9560ms |
| 1 | 16.1545ms | 16.6135ms | **−0.4590ms** |
| 2 | 16.4760ms | 16.7290ms | **−0.2530ms** |
| 3 | 24.3775ms | 16.3920ms | +7.9855ms |

块节省中位**0.3515ms CPU、0.3425ms wall**，但2/4块CPU反向，未满足事前“四块方向一致且中位≥δ”的探索准入。A过程13 CPU32.526ms全保留；不删尾、不替换、不再采样。均值节省2.0574ms被该慢过程明显影响，不能作为优化预测。仅4块，**无确认CI、无概率置信度、没有否定零/正收益的统计结论**。

其余阶段块中位节省：Undo CPU0.00475ms、Redo0.04350ms、Teardown−0.00150ms；均为探索描述值，非保护控制正式通过。Setup CPU表观节省7.305ms，尽管该阶段计数没有候选命中；这提示存在与候选删除无关的批间变化，不能将含Setup全程CPU的7.72525ms中位节省领取为该优化收益。此诊断不用于扣除偏差或修改原筛选规则。

实测结果只能给出“结构上可删除、当前测试精度与变化下未取得价值确认”。本轮没有新增upstream对照，也没有细分写代际计数，不能拿本次中位从旧7.643ms差额扣减，不能宣称所有内部工作量除read外已逐项证同义。

## 5. 验证、复现与下一边界

共**19个真实过程，57 QTest passed / 0 failed / 0 skipped**。全部19 projection updates、8segments/4callbacks、固定像素hash、Undo/Redo、strategy/image销毁、正确实际加载库、退出/reap通过；共享实际依赖hash一致。它们是匹配fixture验证，不是新的产品安全矩阵。未运行新M6 family，M6/M7/M8仍0/3、校准2/20、persistent默认关闭。

[build.py](build.py)列出3个派生TU并保存机械diff与实际链接输入；[run.py](run.py)保存协议、过程、原始日志和加载库；[analyze.py](analyze.py)生成[完整结果](summary.json)，含逐过程、全部四块与依赖身份。[冻结清单](raw-manifest.json)和[原始包](raw.tar.xz)保存源副本、差异、运行库和原始过程；未修改的链接对象/fixture/共享依赖按hash引用已有环境，不把它们伪称包含在包内。

新取得的是“合同推导→有界合法替代→实际删除→净价否决/未决”的前瞻证据，超过仅给热点贴标签；仍缺有价值净收益的正向预测和产品独立确认。安装技能SHA256 `f63ac3e5130a8807298bff4ebe4e7613ca684d3a7aabda0d6ba14b7f13c65413`未变。03k保留试行。下一候选需有新的事实/消费者放大或合法替代依据；不继续给本项加同义样本，不退回重写H1，也不把cold/operation余项自动判为正常成本。
