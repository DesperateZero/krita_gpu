# 原 epoch root/core：实际存储与最后释放

产品提交`e0fc83ab79a2d761bd61cdae64226a569330d3bb`，父提交`1bc171aefe59b5931fead205155311292f3534ca`，文档父提交`7a88750a74b4c00b981cd6509d5d11e003bfb433`，见[Git身份](git-round-identity.json)。显式补丁、本地聚焦提交、未push、未读archive。§16.59的写集不重做；本批沿原configure/initialize、root候选/保护/collector到最后immutable树引用实际free收口。

| 原对象 / 政策 | 最终原责任 | 同批删除 |
|---|---|---|
| 构造即QShared Private、Qt roots/transactions/retainedSnapshots | lazy core及实际std控制块收费；原三ordered registry实际节点由retained allocator准入 | 旧QShared core、Qt registry与detach/bucket协议 |
| transactionBaseCounts、retainedRootCounts | 两种计数在唯一原root record，原protected list回答逻辑admission及reachability | 两张count索引及冷可达查询的重复扫描 |
| 门内registry growth、cancel/release/collection实际free | 原node门外准备、回锁重新查原事实并复验后insert；extract同node门外free | 后置增长及门内实际node/value析构 |
| Qt root surfaces/control和生产restore导出 | 原paid immutable surfaces值/control/数组；页变化共享，surface变化才复制；private count/at读取原数组 | native Qt surfaces投影；公开冷export保留 |
| 重复root.validate/QSet/validation失败与surface替换找不到base业务失败 | 外部完整input.isValid、原immutable root及已验证surface替换构造权威 | 重复验证及对应不可达业务失败；真实输入/身份/晚复验拒绝保留 |
| TreeReleaseBatch/deque/TLS activeTreeRelease、析构时创建task、前台析构节点 | 原tree storage冷准备一个paid reusable task，最后deleter只接入intrusive原节点，taskPin保护invoke/finished，每pass实际free最多128 | batch/deque/TLS、last-release任务准入及前台Node析构 |
| 冷configure局部成功后无法继续、已接受source首ticket拒绝时重复register | 可见epoch安装前完成原准备；default/metadata原事实复用，原Store保留registry/source receipt，继续同source allocatePending | 已完成准备的重复登记；无新失败stage/恢复队列 |

原Qt容器加估算额度不能约束实际node/control容量；ordered node可门外准备并原位安装，core/surfaces/control均用std allocator实际收费。原计数表可直接并回已有root，无需另建权限owner。旧release batch即使改用paid deque，仍会把新的容量拒绝放到最后析构；本批把一个reusable task前移到创建任何tree node之前，intrusive节点复用实际存储。业务root资格由原core计数决定，最后共享引用后的物理释放由原tree storage承担，两者不合成新阶段。

Store顺序调整消除了“可见epoch已安装但后续冷准备失败”的局部状态。Registry source接受后首ticket仍可真实拒绝，单靠排序不能撤销/重放外部接受；本批新增原Store的registry/source两个最小receipt字段。把外部Registry改为source+ticket原子bundle会扩大其接口/责任，不作为本闭包必要改动。已接受source仍属原Registry寿命，close与所有固定包装未获全量资格。

生产4文件 **+553/-356净+197**，测试2文件 **+328/-14净+314**，ownership合同1文件 **+3/-2**，生成2文件 **+15946/-12949**，见[统计](source-metrics.json)、[生产](production-incremental.diff)、[测试](tests-incremental.diff)、[合同](contracts-incremental.diff)、[生成](generated-incremental.diff)。增长承担actual fee、门外准备/释放、满额最后free与冷配置接续，不能称为等价净删；上层生产API零新增。Registry lookup由hash平均O(1)变O(logH)，冷default复用核对O(S²)，sparse AVL/dense阈值保持，正式延迟/峰值性能未测。

[最终universal build](build-06.log)后[原七组runner包装](run_results.py)产出[结果](qualified-results.json)及[汇总](qualified-summary.json)：**5594 passed / 0 failed / 0 skipped**，双架构14进程exit0。每架Registry87/CPU1314/Reference762/Physical381/Resident221/Foundation28/Freehand压力取消4；不是全仓库测试或完整阶段验收。

每架13个新增有效Reference案例：

- 4行初始化准入：2MiB原parent，core/control真实硬满；4096 manifest/surfaces留8192字节触发原数组拒绝；4096页manifest及16384字节余量触发部分实际树拒绝。未发布core/root，局部树在原压力下drain，精确rollback后同facade成功。
- 1行8MiB原parent、同facade双线程4096页初始化，只一个接受、一份可见root，最后精确归费。未强制两个线程同时进入门外窗口，不作TSAN证据。
- 6行原registry/root：transaction节点、retention token、restore placeholder硬满；512页sparse实际树、64页dense重建、4096 surfaces clone真实容量拒绝。原head/transaction/token保持，局部fee实际归还；释放压力后同原入口成功。candidate准备后再硬满，commit/restore无增长安装，release/collector可继续。
- 2行controller存活/已退出的8192节点raw root：test-only blocker/probe任务在压力前准备，worker阻塞后用原parent填满额度，最后root drop无前台Node析构且原Node仍收费；probe在首128个实际free后执行，然后全部8192后台free，原accounting registration/task/control最后费用返回精确parent基线。test-only无预算helper不授予全process/bootstrap收费或全局allocator资格。

每架3个新增有效CPU案例使用已有private friend fixture，不扩大Reference公共边界：2MiB Store预算留8192字节触发metadata directory准备拒绝；64KiB Registry硬满触发source拒绝；按原source实际成本只留一次source费用，source2被接受而首ticket拒绝。均无可见epoch、同Store释放压力后configure/finalize成功；第三行foreign Registry重试拒绝、source2仅一个terminal ticket、source3未登记，证明不重放source接受。

原root候选隐身/单次消费/foreign/晚revision、collector/retention/rebase/conflict、dense/sparse与Qt oracle、production input接续及Freehand压力取消保持。既有mutation容量测试把事务记录、scope、collector费用分开：cancel scope仍保有原96字节record，abort+实际collector后才回目录基线，所有精确归费/拒绝断言保留。

失败与中间日志保留：

- [build-02](build-02.log)中配置测试最初放在无Store private friend的Reference fixture，且遗漏prepareRestore的error参数；迁到已有CPU friend并修正参数，[build-03](build-03.log)通过，未扩大生产API。
- [首矩阵](initial-qualified-results.json)的CPU两架各9处旧fee断言失败，差额均为新收费的原transaction record；[focused-04](focused-04.log)在分离费用寿命后11/0/0。[focused-03](focused-03.log)只记录错误app binary路径，未执行测试；随后改用既有build/bin路径。
- [中间完整通过](pre-final-qualified-results.json)与[图02](callgraph-02.log)发生在删除最后surface软失败之前，不能绑定最终提交。最终生产变动后重新[build-06](build-06.log)、[七组14进程](test-run.log)和[图](callgraph-final.log)，只有qualified记录授予本批资格。

[最终图](callgraph-final.log)87TUs/2019APIs/25183edges/21callbacks；[初检](architecture-stale.log)仅六个实际源码文件指纹过期，[刷新](architecture-refresh.log)后[独立门](architecture-final.log)通过21manifest/25ownership/16census/19intrusion。[前](baseline-before.json)/[后](baseline-after.json)ratchet不变。ownership只更新原事实的存储/锁外准备/最后free合同，不新增业务owner或放宽政策。[22项删除/保留检查](deletion-checks.json)、[冻结脚本](check_delivery.py)、[提交绑定验证](delivery-validation-commit.log)及[52源码blob](source-sha256.txt)/[15运行物](runtime-sha256.txt)/[工具链依赖](build-environment.json)对应产品提交。静态删除检查不替代上述实际边界行为，也不证明全局allocator零分配。

[活动文档及身份检查](document-validation.log)核对新增本地链接、52源码/15运行物和最终14进程身份，脚本见[validate_documents.py](validate_documents.py)；检查在读取目标前排除archive。链接检查只证明可定位，不授予行为或性能资格。

尚有公开Qt输入验证/oracle/retention/serializer、嵌套format数据与实际export容量，standalone controller/facade/process/bootstrap未完全收费。其余provider/binding/Registry/observer/Ledger包装、TileDataStore observer登记、shared核心/控制本体、close/runtime固定成本与全部参与者永久拒绝最后handle/自主drain同属CP1。原native seal/generic真实prepare拒绝仍由Failed/cancel承担，原job自动接续归CP5。未取得TSAN、全局allocator、完整永久尾退出、公平或正式性能新资格。

**本批原epoch root/core/三registry/surfaces/tree及raw最后释放已交付；完整CP1开放，M6/M7/M8正式0/3、默认关闭。** 活动裁决见[92 §16.60](../../92_br1_m6_m8_execution_baseline.md#epoch-root-storage-delivery)，下一实际差集从[NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)领取，估算不按净增行或测试数扣减。
