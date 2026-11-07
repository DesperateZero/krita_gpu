# 驻留协议残余清理

最终产品`69a01e929abce246bfeed0603dbf0825088e28a1`，产品父提交`e0fc83ab79a2d761bd61cdae64226a569330d3bb`，文档父提交`8f597fcbbbde4bdc015db9808f27353bdf391dc8`，见[Git身份](git-round-identity.json)。未push，未读archive。本批回收原驻留生命周期的旧失败与重复取消责任；收费候选已撤回。

| 旧协议 / 缺口 | 最终原责任与删除 | 真实保留 |
|---|---|---|
| Transition创建后局部guard仍取消同serial | 创建即接受取消，立即dismiss局部guard，删除第二份取消 | 创建前真实失败仍由局部guard负责，接受后拒绝由Transition析构承担 |
| 物理提交payload/serial/revision异常静默return | 原serial保护payload，untrack等待；两个静默return删除，内部违例终止 | 物理移动前source/registration/reader/active transition拒绝 |
| 原allocation引用丢失改报非最后释放 | 唯一原Payload保存准确slot及refs，删除假false | 正常多alias非最后释放与最后physical free |
| 删空重建复用数值revision | 原准备Qt数组保留存储，constData核对同一身份，修复ABA | 原physical/membership revision继续复验，无第二generation表 |
| alias与allocate/retire完成政策不一致 | 起点已统一completePrepared，本轮核对保持 | source/ticket冷准备、reader/transition忙；不重复计作本轮删除 |

直接设计采用原Transition、原Payload及原Qt数组事实，无新协议层。serial在原Payload发布，untrack等待其完成；swap在物理write gate复验后更新revision，再提交原候选，其他准备不能复用活动serial。原provider gate内的准确allocation负责其physical引用，丢失slot/count不属于可重试业务拒绝。仅把分支改成断言不能证明这些保证，原生命周期与实际拒绝后恢复测试共同提供依据。

## 最终验证与身份

[最终build-06](build-06-scoped-cleanup.log)使用Qt6.8.0、Xcode17、RelWithDebInfo、universal x86_64/arm64、offscreen、seed12345。[运行器](run_results.py)每架运行Registry87、CPU1315、Reference762、Physical381、Resident221、Foundation28、Freehand两个压力/取消方法4及普通tile-store9，[16进程](final-qualified-results.json)均退出0，合计[5614/0/0](qualified-summary.json)，包含init/cleanup。不是完整UI或全仓库资格。

新增测试实际暂停callback，注销最后observer并重建同一observer，resident/revision数值相同；释放暂停后原候选取消1次、新候选提交1次，RAM→SSD→RAM成功。双架构[定向测试](scoped-focused-results.json)各9/0/0，还验证allocation/payload/slot节点真实拒绝在像素前、domain claim实际拒绝后原serial取消/再swap、memoryUsage等待及满额journal提交。完整矩阵保持prepared ticket、epoch/root/restore/oracle、24 MiB长stroke成功和8 MiB取消。没有新增全局allocator、正式性能或TSAN资格。

最终[图](callgraph-scoped-final.log)87 TUs、2019 APIs、25183 edges、21 callbacks；[独立架构门](architecture-scoped-final.log)21 manifest/25 ownership/16 census/19 intrusion。[原ratchet](baseline-before.json)与[最终ratchet](baseline-after.json)相同。[17项删除/保留检查](deletion-checks.json)、56份[source blob](source-sha256.txt)、16份[runtime文件](runtime-sha256.txt)、5份[构建依赖](build-environment.json)绑定最终commit，[检查器](check_delivery.py)已用--commit验证源码blob和tracked产品树干净。

## 成本与主干边界

| 分组 | 文件 | 新增 | 删除 | 净增 |
|---|---:|---:|---:|---:|
| 生产 | 2 | 14 | 10 | 4 |
| 测试 | 1 | 44 | 0 | 44 |
| ownership合同 | 1 | 3 | 2 | 1 |
| 生成审计 | 2 | 6109 | 6107 | 2 |

见[指标](source-metrics.json)及四份incremental diff。生产逐文件：KisTiles3PageReplicaProvider.cpp+11/-10，kis_tile_data_store.cc+3/-0；净+4包含ABA保证及必要说明，不声称纯净删。主干仅后者+3/-0，原swap登记owner必须在此复验，UI/DataManager不能观察或决定该物理事实。主干新增API/类型/状态/字段/include/friend/锁/TLS为0，provider内部仅新增exception include；普通无observer tile走原早返回，无新增存储/扫描。原Qt快照成本未优化，Qt登记/observer/Transition仍有真实消费者与CP1收费欠项。

## 撤回候选

原始命令日志会显示改名前的`br1_residency_observer_storage_20261003`路径。build-01使用错误target；build-02/03/04/05属于收费迁移候选。[候选diff](withdrawn-storage-candidate.diff)冻结撤回前五个源码/合同文件，供复查，不是当前实施指导或交付源码。

候选为登记record/list/control/entry/array及observer/Transition实际存储收费，曾将登记放到像素创建后；[focused-01](focused-01.log)捕获slot-node拒绝顺序回归及旧满额journal夹具假设。前移原PreparedAdoption并按真实费用调整夹具后，[focused-02](focused-02.log)14/0/0只对应候选。随后[候选矩阵](qualified-results.json)的x86_64 Freehand长stroke遭metadata准备拒绝，slowReaderChecks=0；[隔离运行](freehand-isolated-01.log)再次复现。[调试日志](pressure-debugger-01.log)观察实际247936字节申请被拒绝、limit25165824字节；Qt内联符号求值失败，未取得完整parent usage或根因，不能宣称精确峰值。候选运行物已被最终build替换，不具备独立冻结runtime资格。

本次用户范围为旧协议回收，收费扩张未取得原压力资格，因而完整撤回；最终没有提高预算或删除断言，也不累加候选通过数。未来收费实施仍须兑现准备前移、原压力、身份复验和最后free，不照搬候选框架。

当前裁决见[92 §16.61](../../92_br1_m6_m8_execution_baseline.md#residency-protocol-cleanup-delivery)、[代码及MI账本](../../br1_modification_guide/CODE_INDEX.md#residency-protocol-cleanup-code-index)、[API替代](../../br1_modification_guide/API_CONVERGENCE_MAP.md#residency-protocol-cleanup-api-delivery)。有限残余清理已交付；完整CP1、CP0、全局allocator/TSAN、公平/原job接续、完整永久尾退出及BR1-PERF仍开放，M6/M7/M8正式0/3、默认关闭，§17估算未扣减。
