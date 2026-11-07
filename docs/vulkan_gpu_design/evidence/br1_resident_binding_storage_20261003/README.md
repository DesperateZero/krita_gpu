# 原 CPU binding 实际存储与最后 handle

当前裁决见[92 §16.64](../../92_br1_m6_m8_execution_baseline.md#resident-binding-storage-delivery)。本地产品提交`50304c3da6881c535e790b3b64dd0f02a812469c`，产品父提交`43799912101df77e6ebae0dc4d5c3622b7f0a6b3`、文档父提交`296fb283024b41a50c0de3a9d7c818677c91f9a0`，见[Git身份](git-round-identity.json)。未读archive、未push，普通源码/文档使用显式apply_patch，完整CP1及BR1保持开放。

## 原责任与替换

原binding由provider allocation index唯一登记，guard/reservation/handoff/read cache及metadata link共享同一记录。原Qt构造未覆盖对象/control实际容量；附加估算额度无法约束该分配。仅在原adopt位置加收费会让新拒绝发生于像素初始化之后，因此原prepareAdoption在已有allocation node内前置allocate_shared，沿observer的retained allocator计入实际请求容量；候选尚不持tile。adopt只接受原tile引用及节点，不再创建Qt控制块，无桥接共享owner、第二binding或回收队列。

| 旧路径 | 原位最终归属 | 验证 |
|---|---|---|
| adopt阶段Qt创建binding | 原prepareAdoption准备对象/control，原adoptTile接受tile引用 | allocation/payload/slot/binding-control逐个真实容量拒绝；callback/payload work未开始，原fee/alias/committed bytes/ticket保持，释放压力后同入口成功 |
| QShared binding字段、参数、返回、cast | 全部生产provider、generic/native guard、reservation/handoff、metadata link/cache及测试override共享同一std binding | 完整CPU/Physical/Resident及manager、reference、业务控制；三个实际派生类均迁移，Qt binding路径搜索为0 |
| provider/controller退出即返还对象费用 | 原retire/revoke结束权限，retained accounting owner保持实际allocation费用至最后control block free | 四BPP×retire/provider退出/带read pin退出共12行；拒绝新pin、原pin字节正确；最后强引用后weak仍收费，最后weak释放精确回parent基线 |

CPU adoption原三行进一步分开实际alias node与binding/control容量：保留原allocation/payload/slot拒绝，加一行仅少一个字节触发最后binding/control allocation。都先于fresh像素准备。alias/initial仍共用该同一prepareAdoption；原节点、物理引用与退款断言保留。晚handle测试不增加生产诊断/API，并继续保持原身份、local gate、pin/readiness、retag及prepared completion政策。

## 验证、反例与成本

[build-01](build-01.log)漏迁移test-only StorageFailureBinding派生对象，编译拒绝；三个派生生产/测试类共同迁移后[build-02](build-02.log)通过。新增[晚handle](physical-new-01-arm64-result.json)14/0/0和[adoption](adoption-new-01-arm64-result.json)6/0/0先通过，不替代最终完整consumer回归。

[首轮十四进程](initial-regressions.json)7533/1/0、全部正常退出：x86_64的组合Freehand 24MiB pressure在checkpoint metadata preparation拒绝，slowReaderChecks=0，见[原始失败](FreehandStrokeTest-final-x86_64.log)。[单独复现](pressure-repro-01-x86_64-result.json)3/0/0和[组合复验](freehand-repro-02-x86_64-result.json)11/0/0通过，**没有解释或关闭首轮反例**。首轮与索引进程共时，不能据此断定索引是原因。完整压力进度/准备峰值仍待原owner审查，不提高预算、缩输入或降低断言。

曾怀疑metadata link持续保活，但当前retirementQueue/close已经调用removeCpuReadBinding。新增四BPP×33代真实read→释放view→fill→原waitForRetirementIdle验证cpuReadBindings每代1→0、像素正确，[探针](cache-before-arm64-result.json)6/0/0排除这条路径作为必要原因；未改metadata/retirement，不新建重复GC。测试随后纳入最终CPU完整组。

[最终矩阵](final-regressions.json)/[汇总](final-regression-totals.json)为两架七组14进程，**7542/0/0、全部正常exit0**：每架CPU1324、Physical393、Resident221、Reference762、完整manager1057、Freehand普通/持久/失败/24MiB压力/取消11、Matched3。完整manager保留LIMIT_LONG_TESTS=1、原stress/benchmark和线程/worker配置。最终运行前索引已结束，最终进程串行；109个[运行物起点](runtime-before-tests.json)与结束[身份](runtime-identity.json)逐物相等。不授予TSAN、全局allocator或完整资源尾出口资格。

Matched继续复用共享fixture及相同五插件，普通路径的blank/painted摘要、callbacks和原owner释放与§16.63一致；没有新upstream独立配对性能。原普通stroke/undo/redo回退、canvas/M/K/E、P95/P99与正式非劣门仍未关闭。

[生产](production-incremental.diff)9文件**+53/-43净+10**；[测试](tests-incremental.diff)5文件**+102/-19**；[ownership](ownership-incremental.diff)**+2/-1**；[生成](generated-incremental.diff)**+7374/-6992**及[逐文件统计](source-metrics.json)单列。收费/准备顺序及最后free是保证增量，不能报等价净删。上层API/持久字段/状态/锁/TLS/队列新增0，现有低层binding seam表示同步迁移，需要消费者共同重建，不宣称旧二进制ABI兼容。TU内新增adoptTile一个实际consumer；主干侵入仍原19文件，无新增文件或PageStore上层扩散。

[最终图](callgraph-final.log)87TUs/2020APIs/25258edges/21callbacks；[架构门](architecture-final.log)21manifest/25ownership/16census/19intrusion，原ratchet与[起点](baseline-before.json)相同，只刷新source checkpoint。92份源码、运行物、构建与本地Git绑定见[源码](source-identity.json)、[运行物](runtime-identity.json)、[构建](build-identity.json)及[检查器](freeze_evidence.py)。

## 未关闭

[此前三个失败进程](prior-failed-processes.txt)59123/70089/83020仍UE，当前通过/正常退出不能授予所有尝试drain。首轮24MiB组合pressure反例保留；provider/observer/Transition/Reservation本体及Qt控制、metadata link本体/control、source/read cache、Ledger/Registry/facade/bootstrap、固定成本和全部参与者永久尾出口仍欠。原binding/control已收费及已存在cache清理不重领。完整CP0/CP1、公平/原job continuation、allocator/TSAN、M6/M7/M8正式0/3及BR1-PERF继续按92 §17，默认persistent策略资格不改变，不按通过数或净增扣人日。
