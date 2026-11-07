# 完整投影CPU责任实施：候选已验收，默认晋升失败

目标沿03d §8：完整准备、写入、seal、交付、读取和释放的替代及统一验收；不以以下第一个实现点通过结束。产品父a918e45e02，活动文档父506f60da7。初始源码快照与父库哈希见initial-identity.json；父库与当前build库逐字节相同。旧证据包保持冻结。

最终九行处置及统一验收见下表与[报告](README.md)。保留事前状态、失败与中间批次，避免把事后删量伪装成已有精确时间预测。本有限实施闭包结束；Undo回退和仍显著的upstream差距未解决，不称优化目标整体达成。

## 事前设计及数量预测

先落实贯穿冷准备和封存的原数据直接消费，继续审查其它责任：

| 责任 | 原表达与目标 | 预期删除/保留 | 状态 |
|---|---|---|---|
| 同步metadata序列 | 两步Acquire/Prepare、BeginPublish/Publish通过拥有型SnapshotArray传递；改为调用期间借用连续输入 | 每次两步调用去掉SnapshotArray的shared control和vector分配/归还；原状态机、锁外增长复验和失败原子性保留；实际次数以候选诊断核定 | 待实施 |
| seal→overlay | 临时overlayChanges再复制到candidate->changes；由原write-set直接生成候选输入 | 删生产者临时vector/填充复制/归还，保留候选拥有的输入、排序、proof/alias/removal及重试；不能按整个seal桶领取时间 | 设计中 |
| 同步provider完成事实 | ready在返回前已成功，却逐operation创建Pending/完成；研究原provider初始化时的一份成功事实，物理retirement仍逐allocation独立 | 默认fill/copy/payload/alias/transfer统一消费；不合并ready和retirement，不触碰异步SSD/GPU；如成立每次成功同步准备少一次ready allocate/complete | 合同/consumer核对中 |
| 默认初始化 | 在当前pin修复上整合块fill候选 | 每页4096→13调用，像素字节不变；整笔与投影分价；负控制仍待完整候选验收 | 待整合 |
| 范围/跨操作 | 原merge中间reader、独立失败结果决定合法分段；不能直接132→96 | 不重做已完成来源计数；形成具体保留/可替代结论 | 未完成 |
| base/provider/预算登记 | 物理PayloadMap节点是原状态owner；SlotMap只存指向同一Payload的指针，改为嵌入Payload的intrusive slot索引，登记/ack/untrack/最终释放一起迁移；锁外新状态复验保留 | 每次新物理payload少一个SlotMap节点分配/归还；新增内嵌hook替代原map节点，两个查询键仍保留。multi_index scratch需额外header分配，故选择原记录嵌入索引；不新增owner或状态副本 | slot索引实施中，其余冷链未完成 |
| canonical/adapter/geometry | 原delta、targets/touched/changed/prepared tiles的生产与实际消费者一起收敛 | 真实发布原子性/changed失败清空保留 | 未完成 |
| 读侧 | current/old/overlay实际消费者与保活寿命审查 | 不能懒捕获改变原snapshot cut；18 before不自动可删 | 未完成 |
| 释放/残差 | 检查全部新增借用和准备的最终归还、失败及晚读者 | 不把工作移出Stroke/放到Undo当收益 | 未完成 |

所有新API替代旧签名并迁移实际caller，内部借用不得逃逸同步调用。若准备前移消除失败点，同批更新依赖该失败点的测试为仍真实可达的压力拒绝，保留旧失败来源消失的说明。测试不得改成只验证计数或放宽语义。

## 实施责任裁决（最终候选冻结前）

上表是事前记录。现五项替代均已实施，具体全路径裁决如下；关闭审查不等于声称其全部费用已删除。

| 责任 | 本包最终差集与保留依据 | 更直接表达的比较 |
|---|---|---|
| 范围与分段 | 保留原startMerge/setupProjection/composite边界。setupProjection清理parentOriginal后，调整层投影更新、filter/selection处理能读到该版；失败也必须保留此前成功操作。32 batch与19更新不是同义计数 | 合并clear/composite会延迟可见或使后操作失败吞掉已成功结果。仅复用rect不能证明中间consumer不存在，因此本包代际数预测不变，而不是领取36条冷链 |
| base/plan/descriptor | beginWriteImpl已让同一execution绑定entry/Page，暖写不重做cold；原claim保护key，prepareWriteBaseLocked一次queryMutationBase得到selected/nextGeneration/before。ColdPage借用已安装descriptor，非新共享缓存。两步metadata输入改为stack借用 | 跨provider解锁后默认页可被reader物化、预算/可恢复before/domain可变，preparePrivateWrite的再观察与handoff复验不是同窗口重复查询。省略它们会漏掉实际source pin或接收过期计划 |
| 实体登记及ready | Payload拥有物理slot/domain/revision；slot索引嵌入该节点，登记/ack/untrack一起迁移。同步ready在provider配置一次成功，default/fresh/copy/payload/alias及CPU transfer共同返回它 | provider物理record、owner预算backing与CPU binding分别管理swap/多owner收费/访问pin，不因键相同可合一。实际retirement仍逐allocation有Pending记录，free才完成；无共享可变状态或新增恢复队列 |
| 默认填充 | 当前pin安全修复上接入块fill，全部实际BPP/default字节入口共享；4096→13调用，按实际fill页计数 | 保留copy/row布局和字节数，不把copy也计成fill收益；默认启用取决于最终Undo等控制 |
| seal | 两步publish同样借用；原write-set直接向overlay candidate生成最终change，移除生产者vector及其复制/free；private publish/proof仍可部分接受后retry | 发布/proof/overlay各接受点不同；机械合遍历会把后页失败变成前页重复publish或失去冻结责任。原ColdPage proof记住接受，overlay候选仍需拥有输入供锁外metadata准备及重试 |
| canonical交付 | 原preparedPages快照、descriptor强引用、metadata/root/backing candidates保留；输入与owned proof一致性仍查验 | 公共commit输入可陈旧/伪造；epoch owner需要独立不可变delta供重基。descriptor数组跨锁外provider校验保护布局；只借原map迭代器会允许其它commit/GC并发更改容器。替代它需改变原跨owner输入合同，当前没有已证明等价且净省的实现，不将1.15ms全领取 |
| adapter/presence/geometry | changed只由finishPreparedWrites一次写入，原buffer在首字节前预留、失败清空；PreparedTileUpdates只为缺失wrapper准备，暖页不建第二键表；clear的presence供联合安装删除sparse tile和更新extent | targets是准入全集，changed是实际成功delta，missing是仅新wrapper集合，presence含删除语义。用targets替changed会把未写页报脏；去missing会在发布后分配；借mutation内部集合跨finish则在seal释放后悬空。故保留不同寿命集合，不重复改已完成的共享delta迁移 |
| 读侧 | accessor scope在建立时固定current/transactionBase；已有兼容scope复用和writable before-only规则保留；clear固定before受同一range claim保护 | 通用const accessor可在稍后首次调用oldData；懒捕获会改变snapshot cut。18 overlay与18 before是不同版本。借活动overlay map不能给晚reader不可变语义；显式声明只读current需迁移更广API，当前调用不能证明其合法性 |
| 终结/残差 | 原qScopeGuard/retirement接续保留；新的borrow仅同步调用，overlay候选拥有最终事实，intrusive slot/dirty在Payload释放前均解除，完成记录实际free后合并；不将工作移到Undo | 合并Ready与Retire会把未free的物理页报终结。移出Stroke只改变测量位置；最终5阶段和Fresh/H4仍整体验收。未解释的bitBlt/job费用不归零、不包装成已优化 |

## 开发纠错账

- dev-01：Reference946通过，CpuMutation1591通过/3失败。两项测试假设依赖每operation新Ready：零余量仍拒绝，单retirement-node余量现在应成功；out-of-order retire只有所有相邻Pending完成后才压成一记录。已改为验证新的真实容量边界、物理free及最后压缩，保留原失败日志。
- dev-01的bpp16-K9-mode2 overlay像素异常原因未定。原helper未检查空read结果；现显式报告read失败并先验证长度。原单行重跑通过，dev-02/03/04完整CpuMutation均1594通过，不能据此宣称异常已因果修复。
- dev-03与dev-04各Reference946/CpuMutation1594通过，分别覆盖直接overlay输入、内嵌slot索引。没有用这些安全总数替代实际性能验收。
- 首次完整safety-arm64在bpp8-K9-mode2再次失败，明确是默认版无有效replica。ensureDefaultPageLocked结束的descriptor scope guard无条件解锁，历史default可在materialize与AcquireRead之间被collector移除。把原临时map移交外层读调用栈，owner锁释放后销毁，此时read pin已注册；保留竞争物化后的重新选择。不是增加常驻保活或屏蔽回收。
- forced-read-collection-v2在旧清理窗口调用真实collector，49通过/1失败并复现原错误；新清理点50通过。safety-read-fix双架16组合计9220通过，结构审计与6项审计器测试通过。两次read-fix编译错误和一次误使用旧库的无效开发批均留存，见dev-read-fix/INVALID.md。此前异常现有代码机制和干预对照支持该归因，但单次压力通过不声称覆盖所有并发调度。
- read-fix完整性能批结束后的提交复核发现provider配置拒绝会遗弃已注册完成源：源登记成功、Ready记录拒绝、恢复重试时又建新源。common state现用原completionSource/completions保存接受点，跨registry拒绝；新增精确容量测试验证恢复仍用原源。dev-config-fix定向3通过；该早期runner只记录unstaged两文件，源差集不完整，不能当最终身份。runner已改为git diff HEAD覆盖staged/unstaged，最终candidate-config-fix冻结12文件并新批验收。

## 验证安排

开发期先编译受影响image与Reference/CpuMutation测试，再运行覆盖真实失败、并发、旧视图和退休的原用例；修复新失败后保留失败日志并重跑受影响范围。实现责任表尚未关闭时不运行完整性能批。最终候选形成后冻结样本协议、运行库和工作量要求，再做无内部插桩父/候选/upstream，独立机制诊断，原Fresh/H4及受影响安全/控制；完整方案未通过时不标为M6完成。

事前无完整结构项时间价格：上述是可核定的工作删除，不能把事后诊断回填为预测。原投影4.739ms差额、fill约0.55ms局部预算及36链约0.48ms来自独立冻结批，不拼成精确新账。最终源的完整安全9222/0/0、固定性能和容量诊断均已完成；逐项理论/实际、慢值、Undo失败及剩余差额统一见报告。
