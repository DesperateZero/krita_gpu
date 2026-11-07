# PageStore 完整最终输入的管理管线优化

承接[92 §16.172](../../92_br1_m6_m8_execution_baseline.md#pagestore-equivalent-pipeline-diagnosis)，以公共存储同义操作评价 PageStore 本体。父产品为 `8198c36ed722030edae715b7423554036bf1bcf7`，固定 upstream 为 `9a24ae0d8c070884fb013594191002e1a1b39a19`。候选、各次修订和失败独立冻结；正式 M6/M7/M8 与默认策略不因本包自动晋升。

**裁决：候选有可复现的同义存储局部收益，但业务控制尚未恢复，未晋升生产。** 完整候选保存为产品提交 `20fd6d9897f5f0ef3f89d215df0cfb2e6a1b63b9`、分支 `codex/br1-final-payload-candidate`；活动分支 `codex/br1-cpu-lifecycle` 恢复父产品8198及原image。下面的候选收益不是当前检出产品已经获得的收益。

## 替代算法与保留成本

原完整页输入已经由 provider 直接填入独立 Fresh backing，并没有先复制旧页再覆盖。冗余发生在填完之后：仍以可变写者进入 Acquire/Prepare，取得物理 writer reservation、pin 和临时 guard，再于 seal 经 BeginPublish/Publish 转回不可变 Prepared。

新路径利用 packed producer 对同一 execution 的每个 key 只交付一次最终数据这一事实：同步 provider 完成独立 Fresh 初始化后，由原 `AdoptPreparedWrite` 直接接纳私有 Prepared。原 entry/claim、descriptor、backing ledger、预算、proof、overlay、canonical 和退休链仍共同承担生命周期；不保存借用输入指针，不增加 owner、持久状态或独立准备管线。

只有内部 `overwriteFinalPage` 声明最终输入。公共 `overwritePage` 仍允许随后修改 pending；partial、无同步 payload 能力和 RecoverableHandoff 保留原可变路径。R3 使用同一模板函数体在编译期选择 bool 或 guard 返回，普通可变写保持原具名返回对象，不经新增 bool/output wrapper。

这是 Fresh 管理表示的替代，未改变每次操作的可见性和失败边界，也没有执行 M7 原地覆盖。目标 generation、物理 Fresh 准备、输入字节、no-op 比较、seal/proof、每次发布与回收仍需支付。全部五处首字节后拒绝仍允许取消独立目标，不能据此宣布不可失败安装已经完成。

代码位置和原 T01–T08 责任只在[原管线矩阵](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md)结算，不新建第二份总计划。

## 预测与计数的含义

事前[协议](PROTOCOL.md)预测每命中目标删去三次 metadata policy 转换及一对写 pin；未知时间不以数量比例替代。K16/N16 四个 manager 寿命共 64 次 write、1024 个目标，工程目标为 write CPU 节省至少 0.5ms，属于候选价值目标，不是修改后的 M6 门槛。

诊断 fixture 复用原公共操作，仅读取现有累计计数；计数用量不参与时间定价。JSON `mechanism.fresh` 字段实际读取 `generationsReserved`，不能仅凭该字段证明物理计划；Fresh 判断来自前包计划观察及本包未改变的 selector。`localTransitionSequences` 是执行序列数，多个 policy 转换可合在一个序列，不能把预测的 3072 次 policy 转换称作 3072 把锁。

## 固定实验与修订历史

8 个同源公共存储用例为 K1/K16 × N1/N16 × H0/H1，每用例四个 manager 寿命；每次写后立即读取并核验字节，H1 验证 Undo/Redo，最后 purge/销毁。两侧相同源 fixture，绕开画笔、queue 和 compositor。正常输出同义不等于两侧所有失败保证相同，PageStore 的 retained exact view、operation rollback 与硬预算另由产品反例验证。

探索两块只定价方向；每次最终确认独立八个 ABBA/BAAB 顺序块、32 进程，另八块新/upstream、四块16进程 freehand 控制。每块两过程均值差，再取块中位，bootstrap100000次、seed20261010，区间均 pointwise95%，非联合family资格。进程 CPU 包含其他线程，read 段不能全部归为前台读取；全 case 同时报告防止仅搬移到其他阶段。不同修订与探索均不混池，全部慢块保留。

- 探索 r1：H0/H1 write 节省0.92025/1.598ms。
- r1 独立确认：0.4635 [0.1635,1.2905] / 1.60475 [1.2105,1.8895]ms；H0 点估计未达0.5ms。freehand Stroke CPU 节省−0.14875 [−0.4245,−0.0135]ms，出现回退。新增临时 guard 搬移是源码发现的可删开销，但未证明解释全部回退。
- [R2](R2_PROTOCOL.md)消除搬移后：0.813 [0.6725,0.8945] / 1.1745 [1.058,1.4745]ms；全 case 节省1.06475/1.10425ms。freehand仍为−0.30725 [−1.184,−0.023]ms，故不能将搬移修复当作控制恢复。
- [R3](R3_PROTOCOL.md)最后有界修订恢复普通可变写的直接返回，消除 runtime output wrapper。修订前已冻结停止规则；若控制仍有回退信号则恢复父产品，不追加样本到通过。

## 安全、失败与资源

新增97个数据行：完整输入80行，覆盖1/4/8/16BPP、resident/virtual default、同步payload/普通provider、commit/cancel/第二页provider失败/proof拒绝/混合partial；一个 seal 真实预算拒绝后重试；16个原生产 RecoverableHandoff 数据行扩展到 final-input 入口。验证借用输入同步消费、旧current与retained reader不变、并发default materialize、失败回滚、原physical retag、旧replica、Undo/Redo和close归零。

r0完整manager的14个失败均是原full packed write非零pin计数预期过时，像素/历史/资源断言未失败；只将完整同步最终输入的预期改为0，partial和fallback保持。原始失败不删除。r1/r2各自双架构四完整套件均7266 passed/0 failed/0 skipped，不能相加成最终候选的独立覆盖数。

R3首次调用图生成与构建并行，遇到临时缺失的moc派生文件而失败；构建完成后重新生成，保留原日志。这是派生检查调度错误，不是产品测试成功证据。

最终R3两架构四套件各3633、合计 **7266 passed / 0 failed / 0 skipped**，其中CpuMutation1692、manager1322、physical claim398、resident read221。结构检查21 manifest/25 ownership/16 census、2222 API/29434调用边/19外部侵入文件通过，未放松边界。候选生产5文件 **+87/−25**、产品测试2文件 **+122/−9**；3份审计文件为派生身份/所有权更新，不能把其大幅行号变动当本轮新增生产逻辑。207文件baseline inventory覆盖先前分支累积范围，非本包207处源码改动。

恢复后测试程序按8198重建，活动image逐字节还原父库；两架构的completePayload/preparation claims/production handoff与packed write/pin working set复核 **406 passed / 0 failed / 0 skipped**。活动产品tracked tree干净。全过程共287个候选/诊断/控制/完整测试进程，另4个恢复核验进程；其中原r0 manager一过程保留14个旧计数预期失败，其余退出/语义核验通过。安全覆盖按最终7266报告，不叠加反复运行数。

## 最终数量与时间

R3机制两次/侧完全一致。以下均K16/N16、四寿命：

| 机制 | 父 → 候选 | 判断 |
|---|---:|---|
| generation reserved / pages sealed | 1024 → 1024 / 1024 → 1024 | 逻辑目标与交付次数未删 |
| write pin / unpin | 1024 → 0 / 1024 → 0 | 最终输入不再临时暴露可变访问 |
| 前台metadata version inputs | 3072 → 1024 | 每页少两个重复投影输入 |
| 前台metadata version installs | 1024 → 1024 | 安装必要工作保留 |
| 前台local transition sequences，H0/H1 | 2048 → 1024 / 6016 → 4992 | 每页少一个实际执行序列；不是三把锁 |

最终八块父减候选的独立确认如下；正值为节省，单位ms，区间为pointwise95%：

| 端点 | H0 | H1 |
|---|---:|---:|
| write CPU | **1.18575 [1.014,1.6975]** | **1.35975 [0.835,1.6405]** |
| write wall | 1.164 [0.8075,1.88] | 1.12925 [0.6925,1.371] |
| 完整case CPU | **1.3515 [0.8995,1.807]** | **1.572 [1.0205,1.9675]** |
| 完整case wall | 1.31975 [0.8215,1.895] | 1.381 [0.896,1.8445] |

数量假设兑现，write点估计与区间下界均超过事前0.5ms工程目标，完整case也有收益。时间事前只有目标、没有测得的单价；不能把“达目标”写为准确预测1.19/1.36ms。R3与r1/r2的差异不是同批候选间因果比较，不能给wrapper删除单独领取毫秒收益。

最新独立新/upstream批次仍有很大残差：write CPU额外H0 **7.912 [7.7595,8.284]ms**、H1 **6.68675 [6.3565,7.2035]ms**；read过程CPU额外5.54125/5.36625ms；完整case额外14.63775/14.83875ms。前包父/upstream差额8.256/6.976ms与本包父/新收益不能机械相减；不同批次绝对时间不同，只有同批对照分别支持各自结论。本候选仍未减少1024对64的物理周转差，也没有关闭主要upstream差额。

## 控制与不晋升裁决

R3 freehand四块Stroke CPU父减候选为 **−0.540 [−1.2865,0.2165]ms**，wall **−0.209 [−0.4255,0.135]ms**。四块CPU差为−1.2865、+0.2165、−1.1005、+0.0205ms；不能称本批统计确认回退，也不能称修复恢复。Setup CPU−0.0915 [−8.888,14.115]、Undo+0.00525 [−0.101,0.061]、Redo−0.01825 [−0.1585,0.0395]、Teardown+0.0165 [−0.0615,0.0645]ms，均没有严格非劣资格。

r1/r2控制均曾出现区间排除0的负值，R3点估计没有恢复且不确定性扩大。不同源码批次不合并计算概率，也不因最后区间跨0就否定前面的风险。按最后协议停止本包、保存候选并恢复父产品；没有第四次表示微调或追样到通过。局部机制成立、存储净收益成立、业务控制未闭合、整体阶段未完成是四个独立判断。

下一优先仍为T01–T08中的完整Fresh准备/交付/退出成本及真实后台归属。本包已给最终输入的重复可变协议定价；在重新接纳该候选前，须对无删量的普通可变路径实际调用/释放与控制回退作因果判别，而非继续换返回表达后复抽同一小样本。尚不能把残差统称必要的锁或管理费，也不具备直接领取960次原地复用的M7资格。

技能本轮完成了事前假设、实现、反例、独立收益和负控制拒绝的闭环；未完成全局可回收榜首、精确时间预测或生产正向晋升的验证，因此没有升级安装技能。**M6/M7/M8仍0/3、校准2/20、persistent默认关闭。**

## 证据入口

事前协议、PRE_CONFIRMATION、R2/R3协议、各版 summary JSON、`run-r1.py`/`run-r2.py`/`run.py`、`analyze.py` 保留在本目录。原始过程的 command/env、退出/timeout/reap、语义校验、实际加载库哈希及源码差异均保存。二进制依赖本机原工具链/安装目录，不声称完全独立运行。

[最终增量](confirm-r3-summary.json)、[同义upstream残差](upstream-r3-summary.json)、[业务控制](business-r3-summary.json)、[源码/测试验证](verification.json)、[全部原始证据](raw.tar.xz)、[逐文件清单](raw-manifest.json)、[归档校验](EVIDENCE.json)。原始包含四个image版本、共同fixture/业务probe、最终测试二进制、源码快照及差异、全部成功/失败日志。最终候选image SHA256 `ac2a8d74f544325270e153e676506df664fdaa7e6fd55ed0731c588c7cb9529a`；原活动image恢复为 `77299ab0a112f338b0216eac38a52aa83b2fec3054fb6992a8a3b1417f15ec3d`。
