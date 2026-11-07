# 原 epoch 写集：实际容量、准备与释放

产品提交`1bc171aefe59b5931fead205155311292f3534ca`，父提交`9e0534018d9db0e1376272fb5889ae0d46deb639`，文档父提交`bb4e659b9db39467e7015fd9285d1f476b4071f7`，见[Git身份](git-round-identity.json)。显式补丁、本地提交、未push、未读archive。§16.58的已保护root/restore残余不重复领取；本批完整责任为原transaction写集的准备、拒绝保留、commit共享及实际释放。

| 原对象 / 政策 | 最终原责任 | 同批删除 |
|---|---|---|
| Qt snapshot写集及三种辅助membership/index | 原record唯一immutable delta；值及实际std共享控制块、三数组实际capacity由原retained allocator收费 | changeIndexes、surfaceChangeIndexes、removedPageSet及旧record snapshot |
| under-gate构造、拒绝后局部变动 | 门内捕获原base/old delta/revision；门外准入/准备；回锁查原record并复验后原子替换；拒绝保存原事实/revision | 无额外失败stage、恢复record或队列 |
| native相同完整集重建并使root候选失效 | 在revision exhaustion/分配之前复用已接受原值及revision | 重复完整事实的分配/增代；公开incremental同generation仍拒绝 |
| 先remove后write与反向操作政策不一致 | 合并后原delta两种incremental顺序都原子拒绝；complete合法替换整个集合 | 单向的冲突判断；这是已证实的行为修复 |
| commit Qt transaction复制、dense工作集合 | root准备共享原delta；付费manifest从immutable tree与排序change/removal事实merge | replacement QHash、removal QSet、current.manifest中间Qt数组及重排 |
| 全部7处native transaction导出 | 私有active identity查询；公开transaction仅为冷Qt oracle导出 | Store/Publication生产Qt快照调用 |
| finished record锁内实际free | 原finished链摘取record，移出原delta门外reset，回锁重新查下一记录 | 无新retirement队列、状态或通知协议 |

原位可变数组无法同时保留旧三字段、原子拒绝且允许锁外root准备/冷快照共享；对Qt数组另计估算额度也不能界定其实际capacity。本批用一个不可变原值承载这些事实，复用现有allocator/accounting与finished链。native attach只接原controller，不分配fallback controller；standalone reference/oracle在initialize才建立兼容controller，其bootstrap未宣称收费。

生产4文件 **+229/-130净+99**，测试1文件 **+199/-0**，生成2文件 **+8147/-6806**单列，见[统计](source-metrics.json)、[生产](production-incremental.diff)、[测试](tests-incremental.diff)、[生成](generated-incremental.diff)。增长对应实际容量收费、门外准备/释放、原值保留与两种相反输入政策修复，不能记为等价净简化；无新上层生产API、持久阶段或队列。页键排序查询/merge保留原sparse AVL和dense K≥(N+3)/4阈值，dense O(N+K)；surface membership仍线性，未测正式多surface/峰值性能。

[最终universal build](build-02.log)后[原七组runner包装](run_results.py)产出[结果](qualified-results.json)及[汇总](qualified-summary.json)：**5562 passed / 0 failed / 0 skipped**，双架构14进程exit0。每架Registry87/CPU1311/Reference749/Physical381/Resident221/Foundation28/Freehand压力取消4。第一次构建及[focused 15/0/0](focused-01.log)为中间验证；最后增加并发/root复用验证和调整相同complete/exhaustion顺序后重新构建，不将中间结果混入最终总数。

每架14个新增有效Reference案例：

- 8行complete/incremental × control/changes/surfaceChanges/removal容量边界。原1MiB预算：control行实际硬满；数组行留2048字节给值/control及小preceding输入，再用512元素触发所选真实容量拒绝。局部收费全部回滚，原write set及revision保持，释放压力后同交易接续成功。已准备root后再硬满，相同complete仍复用原事实，安装成功且不增长写集费用。collect(0)保持费用、collect(1)归还。
- 1行原controller和facade退场后candidate保留原core/已收费值；最后candidate释放返回原parent精确基线。这是原写集和accounting owner尾释放，未授予全部tree尾资格。
- 1行同原交易两线程、32768页proof增量，恰一个接受，另一拒绝，最后只有一份值/control/数组费用；abort+collect返回精确基线。测试不强制双方同时进入锁外窗口，拒绝可能来自晚revision或原generation政策，不能代替TSAN。
- 4行先remove/先write × incremental/complete；相反增量拒绝且原事实保持，合法complete替换接受并得到正确最终页presence/generation。

原root候选隐身/单次消费/foreign/晚revision、collector/retention/rebase/conflict、dense/sparse oracle及production input拒绝接续与Freehand压力取消保持。[图](callgraph-final.log)87TUs/2011APIs/24882edges/21callbacks；[初检](architecture-stale.log)仅5个实际改动文件指纹过期，[刷新](architecture-refresh.log)后[独立门](architecture-final.log)通过21manifest/25ownership/16census/19intrusion。[前](baseline-before.json)/[后](baseline-after.json)ratchet不变，checker及ownership政策未改。[15项删除/保留检查](deletion-checks.json)、[冻结脚本](check_delivery.py)与[验证输出](delivery-validation.log)绑定[52源码blob](source-sha256.txt)、[15运行物](runtime-sha256.txt)及[工具链/依赖环境](build-environment.json)。

仍有实际consumer的公开Qt输入验证/oracle/serializer、嵌套format字节未纳入三数组capacity收费。原QShared Private/control、standalone controller bootstrap、root/transaction/protection/retention Qt registry、immutable root surfaces/tree节点及原last-tree释放batch/deque/task仍欠；其他wrapper/TileDataStore observer/close/固定成本与完整永久拒绝最后handle同属CP1。实际准备/revision与合法公共身份拒绝保留；未取得TSAN、全局allocator、完整永久尾退出、公平/原job接续或正式性能新资格。

**本批原写集/dense工作数组已交付；完整CP1开放，M6/M7/M8正式0/3、默认关闭。** 活动裁决见[92 §16.59](../../92_br1_m6_m8_execution_baseline.md#epoch-transaction-storage-delivery)，下一实际差集从[NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)领取，估算不按净增行或测试数扣减。
