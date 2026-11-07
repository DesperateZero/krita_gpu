# 同步退休完成证明：运行前固定判别

基线产品 `11c6895ddfeae074df727c76dcbf9e12988479ee`。原33项T03.1/T04.2/T07.2的同一生命周期候选，不另立状态矩阵。此前直接回收Prepared的负净价不重试。本候选在本轮静态审查和有限原型源码形成后、任何构建/运行前冻结；不是事前时间点预测。

当前路径：allocation/alias/initial adoption预备每allocation独立Pending票据 → 保存到AllocationMap → 拒绝保留 → 同步物理退休 → 完成票据 → 原owner绑定operation结果、验证、释放。票据在退休返回前无外部consumer；成功结果始终在真实释放之后。析构取消的是未向外签发的私有票据。

理想路径：provider configure预备原有Succeeded票据一次；原identity/replay/last-use/pin/residency准入不变 → 同步释放 → 返回原operation和exact replica及共享Succeeded证据。共享的是同步完成事实，不共享operation身份、不提前宣称已释放。原retirement record、debt、预算归还与owner验证链保留；异步provider的Pending/失败/通知不改。

修改闭包：`KisTiles3PageReplicaProvider.cpp` 的allocation字段、adopt及三调用、retire；`KisCpuResidentBinding_p.h` 的Retirement返回类型、beginRetirement、revokeBindings；测试CPU provider同模板迁移（它的独立allocation request ticket保留）；CPU mutation测试原位迁移满额准备/乱序退休/来源记录断言，增加Pending last-use、原operation拒绝后重试、重放和stale访问反例。无新增owner/queue/cache/持久字段。原initial/alias/adoption失败矩阵及generic async退休测试继续运行。

预测删量：每次tiles3 adoption少一个Pending申请、AllocationMap内一个ticket字段、一次成功/取消/失败终结；configure一次ready不变。K16/W16四manager预计非默认1088加默认4，即1092个申请消失，Fresh/rows/retire/free仍1088/1088/1088/1092。对比upstream额外960周转的这一项费用可删，但当前1092删量不是相对差额1092；upstream没有本completion协议。字段和节点字节由实际编译类型/分配证据验证，未知单价不写零。

隔离构建：不覆盖产品对象/运行库。原源码和补丁保存，基线plain库沿用已冻结且含同一空begin/end和显式drain的detach baseline；原型只换provider TU，模板两个consumer一并编译，六个安全binary重链接新测试支持库，CPU mutation以原位修改断言重编译。计数两侧重编译相同provider/registry观察入口，使用原mode3（无scope时钟），不用于价格。构建参数继承同fat x86_64/arm64 O2命令；本判别只跑ARM64。

顺序：六组安全全部通过 → 4个计数过程base/proto/proto/base → 34个plain时间过程（各一capability，8独立ABBA/BAAB块，奇偶反转case顺序）。每过程仍原8case×4manager寿命，包含setup/write/read/finish/undo/redo/purge/destroy及额外drain。120s性能timeout，600s安全timeout，kill/reap和全部失败保留；实际库/依赖/源码身份、像素和历史必须匹配。任何安全失败先停止；真实修复另存批次，不追加时间样本。

主判别与上轮精度口径一致：K16/W16/H1 process+tail净节省的pointwise95% bootstrap下界≥0.75ms才值得进入独立确认（旧约12ms额外成本的6.3%；不是M6门）。H1 foreground及H0 process/foreground下界≥−0.75ms。每块两过程均值后取8配对差中位数；100000 bootstrap、seed20261011。可加净账使用均值；不加阶段中位数。不与构建/其他benchmark并跑，无排除、无追加。不合格保留证据并撤下产品候选；通过仍需独立确认与原业务控制，不因局部收益宣布M6通过。后台/收尾净增已含process端点。

此项源自确证的不必要状态寿命，但价格未知，因此只是有限判别，不宣称命中性能榜首。物理身份复用仍是更大竞争解释；不引入阻碍其后续实现的新状态。静态审查没有证明整个CPU管理链足够优。

r0构建失败保留：macOS `ar r` 不接受已有fat archive，尚未运行任何测试/性能。r1用原六个测试支持对象及新CPU provider对象经Apple libtool重建隔离archive，产品候选与运行协议不变。

r1首组1746/1/0后停止：测试新增的外部last-use从Pending完成时，registry正常释放80 B原区间，原断言错误地要求仍满额。r2在该完成后重新填满释放的容量，保证真正物理退休仍在hard cap发生；生产候选没有修改。重新跑全部六组，再决定数量/时间，r1未跑性能。

数量后、首个时间过程之前的模型修正：4个mode3过程均通过，K16/W16实际Pending请求1096→8，删除**1088**，不是初报1092。每manager默认TileData由manager `prepareDefaultTile` → hash/memento持有；backend `configure`只准备surface/default格式，`configureClone`才对manifest逐页adopt，本fixture没有clone。默认对象的4次创建/free不是provider adoption。因此所有8case都少`4K(W+1)`张，保留每manager provider/host各一次准备共8张；rows/Fresh/retire/free完全符合原模型。初报多算4个consumer（K16/W16约0.37%），保留错误预测，不补测、不改产品或时间阈值。该修正再次说明物理对象、provider allocation、logical generation并非同一分母。

文档索引勘误（时间样本结束后）：上段运行时冻结副本误写了不存在的`initializeFromTiles`函数名；按实际源码修为`configure/configureClone`。消费者结论、1088预测、候选源码、样本和阈值均未变；冻结副本保留供核查。
