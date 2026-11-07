# 预算补数 C/D 与 plain 慢态能力：事前协议

产品11c6895ddfeae074df727c76dcbf9e12988479ee、同依赖upstream 9a24ae0d8c070884fb013594191002e1a1b39a19冻结。本包不优化产品；原预算图的net-ledger-r1时间不替换，新数据独列。

## 固定范围

1. 真正plain：原始产品库，无派生钩子；相同公共fixture仅在外部读阶段/进程时钟。保留冷启动/顺序，固定慢case为同侧同case plain CPU大于本批中位1.5倍，仅列出，不剔除。
2. 系统追踪能力：先对一个短寿命无业务程序验证System Trace能否获得running/runnable/blocked。可用才各追踪一个current/upstream plain fixture，最多两次业务追踪；不可用即保存实际拒绝，不以CPU编号或wall−CPU替代。追踪样本不进入plain性能估计。
3. C：隔离资源派生库记录物理payload、PageStore非payload存储，以及provider/binding/owner/proof/metadata/descriptor、completion实际记录、read/retirement record、root实体建立/退出。记录原始单调时间、身份、字节，重放建立/退出、峰值、保留时长和末端存活。实际内存容量与逻辑对象分账，子项不与共同分配再相加；缓存持有和进程runtime尾单列。缺少锚点的类型明确标未覆盖，不用零代替。
4. D：公共输入覆盖原八case及1/4/8/16 BPP的full/partial/no-op/default/change-default、clear/purge、committed-source copy、clone、history、成功/坏尾导入、raw及保留clone/reader。各侧相同源、输入、像素/presence/extent/失败效果；不等价格保留结果但禁止性能比较。已知live-source exact-view冲突不纳入合格copy格。
5. 压力另用现有真实预算拒绝、swap-in失败、保留root/reader、取消/退休重试测试；先原库后资源库，验证观察不破坏合同。它们是current独有合同/资源证据，不能冒充同义upstream性能。

## 固定实验与退出

- ARM64；公共矩阵固定4个capability过程（current plain、upstream plain、current resource、upstream resource），然后4个镜像块，每块四侧轮转并镜像，共36过程。奇块反转case顺序。每过程120秒，timeout必须kill/reap；任何语义自身断言、身份、事件容量/配对失败立即停止，保留失败，修正观察器/fixture后另开版本。跨实现不等价不静默删格。
- 固定压力函数清单在runner内保存，按测试族各原库/资源库一次；不重复到通过，不以Qt内部data行充当独立性能样本。未覆盖压力组合保持矩阵空项。
- resource热路径不读线程CPU，不分配记录容器、不写日志；使用预分配有界事件缓冲。记录本身仍扰动调度；plain与resource的前台/process配对区间用4块、100000 bootstrap、seed20261011、pointwise95%、原±0.75ms诊断门。失败时峰值/时长只能描述观测运行，不能移授原库或合法净收益。
- 每个公共case保存本体、即时drain、完整CPU/wall；四manager寿命及验证读均明示。所有时间格单列，保留负项/慢态。当前新增覆盖不代表一般负载最优或正式M6通过。
- 保留全部源/库/运行依赖SHA、命令、stdout/stderr、退出状态、timeout/reap、准备/构建/运行失败。完整回放逐资源身份匹配，报告左/右截断及已闭合寿命；不得把跨case缓存/全局runtime残留当泄漏或强行归零。

交付更新原预算账本及唯一蓝图§19，分别给出plain慢态、资源峰值/时长、同义入口、压力合同的已闭/未闭范围。A的机制单价、B完整等待因果、E最优设计不因本包有数字就自动通过。

准备修正：r1资源库已构建，公共fixture因`purge`为protected而编译拒绝，尚无业务样本。r2沿原派生测试类显式暴露该现有入口，补已安装descriptor的完整退出；保留r1源码及编译日志。实体分类未覆盖独立native read guard、adapter类型时，仍记录共同物理管理存储，不能冒称类型级寿命已闭。

r2能力拒绝：两侧plain能力通过；current资源过程在case61触及累计1048576事件容量并abort，原始事件和失败保留，没有正式块。r3仍使用相同容量，改为已输出槽位可重用的有界环缓冲，全局事件序号不断、不丢样；每个未输出窗口仍受容量门约束。仅替换观察器/fixture，不改派生产品锚点。trace-only外部case signpost用于对齐内核时间，plain关闭；额外注册退出dump，关闭过程后的runtime尾继续保留。36过程重新作为独立能力/诊断批，不与失败批拼样。

r3能力拒绝：current 1325480事件及64case回放通过；upstream像素/退出通过，但cache命中也被误记pool槽位释放，实体回放拒绝。r4仅把upstream释放事件移入其原有`!m_cache.push`分支，current库和两侧fixture保持r3二进制，保留r3全部四过程；固定36过程另开独立批次。

压力包在第7过程停止：原库冷进程`processStorageRejectsAndRetains`于12474行得到1154804 B而基线581124 B，增加573680 B；不删除或追认通过。另冻结剩余5个未执行格（同组resource、独立stop及reader两模式），每格只执行一次，原失败格不重跑。该resource格允许保存同一合同失败及完整资源回放，其余格仍失败即停止。先区分初始化保留与对象尾债，不能预先叫泄漏或外部噪声。

两种新条件判别：冷resource组重现相同573680 B差额，实体回放通过。追加仅2个已声明不同条件的诊断：隔离测试副本在原baseline/退出比较前各放外部marker（保留失败断言）；另用原库先执行`storeRootStorageRetained`再执行原测试，判别初始化顺序。各一次，不改产品/原测试、不重领正式资格；若结果不符，保留未归属。
