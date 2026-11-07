# 读写未闭边界：物理续费、活动记录与最后交付

2026-10-13。产品仍为 `ed0f229821a0c9953cd07685a886010ee52e8f62`，生产/产品测试改动均为0。实施状态只有[原33×6矩阵及§19.27](../../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-boundary-cost-audit)，本文提供诊断证据，不授予优化完成或M6资格。

**本轮关闭了两处对象归属，进一步分清了大责任桶，但必要金额和合法替代净价仍未闭合。** 物理plan的908次管理申请中，896次是metadata activity节点、12次是交接账本存储；此前scope外1408次释放，全部来自原范围准入和batch/scope，确实在manager最后交付退出。descriptor临时堆分配假设被本格数量否决。物理plan内部较大的当前支出是收费准备/retag提交6.805M、native准入2.917M、descriptor往返1.364M；真实物理claim仅0.232M。不能把这些桶全算可删除。

## 1. 同义分母与普通库差额

复用原69格能力和13格价格夹具。主格7为K16/W16/H1：64次公共写、1024个页写、16MiB写入及16MiB显式读取，每次写后都有真实读，64个可见cut不能合成一次。upstream固定 `9a24ae0d8c070884fb013594191002e1a1b39a19`，同依赖同架构；普通产品库SHA256 `aa92b11501215f7cadc838727712c2cf7f748f55d5d56ff80fec78b627854bf6`。全套命令/源/库/装载身份见机器账及原始包。

| 普通库端点 | 当前 | upstream | 额外费用 |
|---|---:|---:|---:|
| write 指令 | 55.101654M | 6.028255M | 49.073399M |
| read 指令 | 9.358441M | 5.986514M | 3.371927M |
| 读写合计指令 | 64.460095M | 12.014769M | **52.445326M [52.401692,52.488961]** |
| write CPU | 3.255845ms | 0.364624ms | 2.891221ms |
| read CPU | 0.745328ms | 0.377863ms | 0.367465ms |
| 读写合计CPU | 4.001173ms | 0.742487ms | **3.258686ms [3.119158,3.409029]** |

区间是固定4个镜像块、10000次bootstrap、seed12345的pointwise95%区间，不是同时区间或算法正确率。产品没有变化，不能与前批52.414M/3.193ms相减宣称收益或回退。费用也不能由通用投影优化抵扣。

## 2. 908次申请的对象与1024次活动周转

r2正反序两个69格过程的主write计数完全相同。仅覆盖预算感知管理分配器；payload、普通process allocator、RSS不是该分母。

| 实际consumer | 主write申请次数 | 实际容量 | 归属 |
|---|---:|---:|---|
| PhysicalPlan → `reservePrivateWrite` | 896 | 129024B | 896个144B的`std::map` activity节点 |
| PhysicalPlan → `prepareBackingHandoff`直接存储 | 4 | 576B | 交接准备缓冲增长 |
| PhysicalPlan → `storePreparedChange` | 8 | 256B | 原prepared-change槽/索引存储 |
| Fresh → `reservePrivateWrite` | 128 | 18432B | 同类activity节点 |
| descriptor prepare / install | **0 / 0** | **0 / 0** | 各调用1024次；单项inline容器和已有shared layout足够 |

因此，原physical908＝896＋4＋8；原Fresh未知的128个申请也接上同一activity责任。1024次native准入产生1024个节点，**全部1024个/147456B的配对free发生在后台线程**，不是主write scope内。背景线程没有更细scope标签；具体释放者由下面的源码链解释，不能把后台金额倒算进write。

```mermaid
flowchart LR
    A[1024次私有页准入] --> B[原shard activities新建1024节点]
    B --> C[原D预留 preparedPublications]
    C --> D[接受时清nativeWrite与publicationClaim]
    D --> E[原metadata cleanup保留最后reservation]
    E --> F[后台 releaseActivities 减到0并erase]
```

源码链（均为当前ed0f）在`KisPageMetadataCoordinator.cpp`：`reservePrivateWrite:3903/try_emplace:3936` → `reservePublicationActivity:1875` → install的`nativeWrite=nullptr:3364` → `Data::releaseActivities:2214` → `releasePublicationActivity:1892`。`KisPreparedPagePublication::finishUnlocked:513`通过原dispose回调转交cleanup。`MetadataMapAllocator:592`确实走原预算allocator，而非观测器自建分配。

**算法差距：** backing的896次复用没有带来管理记录同样的复用。写许可、publication claim及准备计数这些事实必要；每次页写新建一个树节点、接受后异步销毁，并非已证明必要的表示。当前每页头不含这份完整稀疏activity，不能简单把整个96B记录永久塞进每页而不计空闲页成本。

可验证的下一表示应比较：原page中最小链接/状态＋原已收费记录，或者原shard内有界容量复用。设该scope内真实容量增长为`G`，在身份/并发/费用允许复用的前提下，活动存储申请目标为`G`而不是1024；条件少申请`1024−G`，该allocator四个prepare/settle入口少`4×(1024−G)`。**G尚未确定；不能预报1024→0，也不能把准入2.917M全部领取。** 必须同时结算空闲容量、shard销毁、压力拒绝、最后cleanup与同key重入，保持一个原owner，不增加第二活动目录或退出队列。

## 3. 延后释放的账已经接回manager

主write最后`OperationDelivery`退出的1408次free/359424B已按地址配对：

| 出生责任 → 最后交付退出 | 次数 | 容量 |
|---|---:|---:|
| 原`reserveManagedRange` | 1280＝64×20 | 257024B |
| 原`beginBatch`的batch/scope | 128＝64×2 | 102400B |
| 合计 | **1408** | **359424B** |

范围原有22次/operation申请，其中两个对象先在backend退出，其余20个随delivery退出。`Store::finishSegmentLocked:854`的`retainAdmission`保留原admission/entries，manager `writeBytes:1707`中delivery声明早于PreparedTileUpdates及locker，所以实际析构晚于后两者。没有新交付owner，原scope寿命跨出了backend函数。前批finishSegment小额价格不是完整结束价。

同一次manager写调用连续六段计价，instruction点观察门通过：

| 互斥段 | 指令M（点估计） |
|---|---:|
| manager前段 | 0.319838 |
| packed前段 | 0.708750 |
| backend完整体及其局部退出 | 53.702818 |
| packed尾 | 0.132368 |
| manager尾、delivery前 | 0.101241 |
| 最后delivery退出 | **1.967197 [1.946166,1.995870]** |
| 总计 | 56.932211 [55.835117,58.029306] |

backend外同窗合计**3.229393M [3.156709,3.316147]**，入口前段合计1.028588M；最后delivery约占这份外部责任61%。这是manager范围内的当前责任归属，不是相对upstream的额外净金额。总估计比同批plain多1.830557M，偏差+3.32%，没有按比例缩放凑平；更不能拿新3.229M与前批2.882M相减。

**manager CPU计价被拒绝：** 全局write CPU扰动+11.78%、同窗总额相对plain端点+11.98%，都超过事前10%门。原始CPU及修正值保存在account中，但不领取“delivery值多少ms”或各段精确CPU占比。指令价格也未获得局部观察偏差上界，只能作为有门限限制的责任暴露。

## 4. 物理plan内部：最大的不是实际claim

另一独立模式按同次plan调用连续十段采样。主write全局扰动：指令+4.74%、CPU+2.94%，均过事前点门。plan父项13.394977M [12.701607,13.847673] /1.001508ms [0.867640,1.172877]；费用含进入plan后最终走Fresh的早退部分。不能与前批12.385M跨观察模式相减。

| 互斥责任 | 指令M | CPU ms（探索价） | 内容边界 |
|---|---:|---:|---|
| plan入口 | 0.559884 | 0.088469 | 选择/资格，含早退 |
| physical/source准备 | 1.111242 | 0.101976 | 原物理观察及必要源保活 |
| accounting准备 | **4.137922** | 0.250040 | ledger身份/收费准备及owner重锁，非纯预算锁 |
| descriptor准备 | 1.011442 | 0.088608 | base布局、target探查、inline候选 |
| physical claim | **0.232170** | 0.023024 | 动态独占权限；必须保留其合同 |
| native准入 | **2.916914** | 0.168048 | activity出生及真实base/身份/transient检查 |
| physical retag＋accounting提交 | **2.667178** | 0.187608 | 实际物理提交、ledger rekey/预算提交 |
| descriptor安装 | 0.352346 | 0.044032 | 原结果descriptor交换及revision |
| plan尾 | 0.141226 | 0.017680 | 返回前处理 |
| plan局部清理 | 0.264650 | 0.032024 | 原局部对象/claim及锁外退出 |

三条判断比继续按函数小修更有用：

1. **收费准备＋retag提交共6.805101M [6.392299,7.087265]，约占本plan51%。** 896次prepare/commit只有12次相关管理存储申请，无法用“主要是反复malloc”解释这项。`OwnerLedger::prepareBackingHandoff:1574`逐次域同步、backing/physical查找、独占/类账检查、差量准入及prepared登记；`commitBackingHandoff:1648`再次消费cookie、rekey、提交及归还槽。原准备缓冲已复用，下一方案须改变共同事实与收费变更的表达粒度。原budget动态限额、父预算、公平性、负delta、真实retirement headroom及解锁后的失效仍需证明；本轮未重测旧bb62的768零delta/128补debt数量。
2. **native准入有确切的活动记录周转，尚无其独立净价格。** 896个节点在此plan内，另128个在Fresh。不能把其他128个的价格加进本2.917M，也不能把base合法性、generation、物理owner、transient限制一并删除。
3. **descriptor往返1.363789M [1.303414,1.410913]主要不是堆分配。** `PreparedDescriptors`的inline容量为1；base布局查询→target探查→候选→按target再找原native结果并swap→`Store::prepareTarget:1493`再按同target读回同一个结果。理想表达是原选择携带受保活的布局，由原private result直接持有，再供同一D接受。稳定布局路径可条件消除这些中间往返；changed layout/default revision、generic/lease和失败候选仍需迁移。源码条件模型为4次descriptor shard入口/页，即主格4096次；这是静态路径模型，本轮没有独立测成“4096把多余锁”。其中最后自取在target后段，不能重复算进本1.364M。

连续区间原始加法恒等式与修正后总和都通过，但修正后的父总额按相同边界修正构造，因此**加法闭合不是独立准确性验证**。plan的CPU只获得本格粗探索资格，没有局部观察偏差上界；不以其比例将52.445M/3.259ms摊成“必要/可删”金额。

## 5. 全寿命数量闭合到哪里

r2全部69格、两个方向的管理申请/free事件分别与配对流核对，3420＋3410个分组通过；未匹配出生、未见释放、地址复用缺口和容量不一致均为0。主write5096次出生/2678720B的最终去向正反序相同：

| 释放阶段/线程 | 次数 | 容量 |
|---|---:|---:|
| 同write主线程 | 2640 | 1735040B |
| finish主线程 | 84 | 24064B |
| teardown主线程 | 640 | 123904B |
| case窗口内后台线程 | 1732 | 795712B |
| 合计 | **5096** | **2678720B** |

write实际free2644次中还有4次源于setup，故不能用write内分配−free推断泄漏。所有同计数组的实际出生容量与local settle容量相符，原观察器abort不构成产品预算少记容量的证明。

这些是**所选allocator、这些case窗口内的数量闭合**。跨方向全69格仍有250个事件分组不同，原始差异全保存，不提升为跨调度不变量；全进程资源峰值、空闲保留时长、RSS、全部锁等待及后台CPU机制净账仍未闭合。观察锁可能改变调度；counts没有性能资格。

## 6. 下一完整责任与尚不能填写的金额

原T03.1/T05.2/T04.3/T07.2应共同审查“原operation计划→原已收费物理记录＋原私有结果→同一D接受→唯一最终清理”。当前证据支持优先验证**页级重复收费准备与activity生命期**，descriptor同源往返作为该路径的关联清理；原T01/T02/T07的范围/交付存储仍为竞争方向。不能只删1.364M的描述符工作便声称解决读写核心，也不能把真实claim的0.232M设成主要优化目标。

修改位置索引仍回填原矩阵成本列：

- **T03.1/T04.3/T07.2：** Metadata `activities`、native reserve/complete/cancel、publication reserve/claim/install、prepared cleanup `releaseActivities`及shard/close；原page/activity/原private result只保留一份事实，generic writer和真实handoff消费者同步审查。
- **T03.1/T05.2：** Store `prepareTarget`、WriteCoordinator `prepareWritePlanLocked`、OwnerLedger `prepareBackingHandoff/commitBackingHandoff/storePreparedChange`与budget reserve/commit；共同事实与逐页动态权利分开，准备失败/第二页失败/retag ABA不得绕过。
- **T03.1/T04.3：** Publication descriptor prepare/install及metadata versionDescriptor/exchange、default/removal/restore/generic caller；CPU原结果直接继承布局后才允许删除被替代中间链，保留布局revision真实消费者。
- **T01.3/T02.1/T07.1：** manager `OperationDelivery`、原batch/scope、range reservation/claim与`finishSegmentLocked/releaseOrRetain`；任何申请减少须计入最后1408次free及未命中/取消/late guard尾账，不能只把free搬走。

必要CPU/指令最低金额、合法可删除金额、完整替代净收益继续是`null`。下一步应以一条保持失败/预算/晚读者合同的完整替代验证净价，而非不断追加细粒度观察器追求表面无残差。事前先记录条件`G`、重复查询/准入删量、新增固定存储及保留预算，再按普通库全寿命端点独立计价。无论局部收益如何，旧坏尾52–55不等价和控制项失败都不能被抹去。M6/M7/M8仍0/3、calibration2/20、默认关闭。

## 7. 有限实验、失败与复算

- [事前协议](PROTOCOL.md)：4能力＋40价格过程；[r1观察修订](OBSERVER_REVISION.md)在价格前冻结。首编译脚本把scope插入默认参数的`{}`，失败构建未运行；首counts观察器因预计/实际容量及缺后台配对假设中止，原两个过程及故障帧保留。
- r1最终44过程全部通过运行/装载/退出检查；69格plain/counts同义，upstream52–55仍不等价。40个价格过程的expected/calls/samples/weight及同窗加法检查通过。部分控制格全局指令/CPU点观察门失败，详见`overview.json/all_rejected_point_gates`；主格通过不能移授其他格。
- 价格全部结束后发现r1在物理free后记录地址，存在跨线程复用竞态。[r2事前协议](census-r2/PROTOCOL.md)只把三个派生管理free记录点前移，固定两次69格数量重核。**价格40过程保持原样，没有用r2替换失败价格**。r1地址流保留作线索，最终配对结论用r2。
- 共启动48个fixture过程、1005条case记录：r1完整44＋r2完整2，另保留r0两过程（其中counts中止）。编译失败不算fixture过程。r1核对510个身份路径，r2核对521个。期间manifest恢复只修编排元数据，未更改已编译源/对象/库，见`manifest-repair.json`。
- 最后分析器r0忘记将delivery配对限定write，把setup的88次交付释放也带入断言；保留`finalize-r0.py`，修正phase条件后只重算相同原始数据，未重测。

[互斥价格账](account.json) · [最终数量/资格账](overview.json) · [源码插桩位置](scope-index.json) · [原矩阵对应源码索引](source-index.json) · [身份/原始包/33×6/链接复核](verification.json)。原始r1及失败数据在[raw.tar.gz](raw.tar.gz)，r2在[census-r2/raw.tar.gz](census-r2/raw.tar.gz)，对应两个`raw-manifest.json`保存逐文件哈希。在本目录分别解压两包（r2包在census-r2内解压），运行`python3 analyze.py`、`python3 finalize.py`即可重算；身份校验还需要冻结源码/库仍在原路径。派生完整源码/对象/库留本地，提交其diff、生成脚本、构建命令及身份，不把诊断库冒充产品库。
