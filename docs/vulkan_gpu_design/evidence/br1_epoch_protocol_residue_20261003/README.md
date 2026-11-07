# epoch 保护事实与 restore 残余清理

产品提交 `9e0534018d9db0e1376272fb5889ae0d46deb639`，父提交 `36189cb3b1bc91d77ea565894bb1fd51f9b6056a`，文档父提交 `00cd19212d15d6e6a8935d049ba6d2d8e1947820`，见[Git身份](git-round-identity.json)。显式补丁、本地提交、未 push、未读 archive。provider allocate/alias/transfer/retire completion旧分支此前已清除，本批不重复领取。

| 原残余 | 原责任与删除 | 保留边界 |
|---|---|---|
| active base 丢失、current capture 缺 root 软失败及默认空root投影 | current/transactionBaseCounts/retainedRootCounts 与 collector 共用mutex；protectedRoot统一查找已发布root，内部身份破坏按不变量处理 | 未保护epoch、非法/过期/foreign token、伪造metadata仍拒绝；真实prepare/install冲突保留 |
| release接受token后缺count静默跳过 | 同锁消耗原计数，最后保护才unlink/queue；缺count不再报成功 | 重复/stale release仍拒绝，交易保护仍阻止GC |
| restore逐字段重建、重复QSet验证及validation假拒绝 | 复制原已验证不可变root，只改受exhaustion guard约束的epoch/previousEpoch/sequence | retained输入与metadata验证、active交易、exhaustion、晚head/activity及metadata callback拒绝保持 |

initialize先完成root索引再发布current；transaction/retention先准备计数槽，记录插入异常时局部scope guard撤销空槽，成功后才计保护。没有新持久阶段/队列/重试政策，原分配异常语义保留。**Qt索引异常窗口按代码顺序审查，本批未注入真实allocator失败，不能宣称其实际容量或完整硬满验收完成。**

生产1文件 **+51/-64净-13**；测试1文件 **+28/-1净+27**；生成2文件 **+4578/-4299**单列，见[统计](source-metrics.json)、[生产](production-incremental.diff)、[测试](tests-incremental.diff)、[生成](generated-incremental.diff)差集。登记顺序/空槽回滚是异常安全修补，成本包含其中，不能单独计为去重收益。一个新增Private查找方法共享保护政策，上层API/持久阶段/队列净增0。

[最终universal构建](build-final.log)后复用[原七组runner](run_results.py)，[结果](qualified-results.json)及[汇总](qualified-summary.json)为 **5534 passed / 0 failed / 0 skipped**，双架构14进程exit0。每架Registry87/CPU1311/Reference735/Physical381/Resident221/Foundation28/Freehand压力取消4。首次构建也通过，登记顺序修补后再构建，最终只跑一次矩阵。原collector测试扩展验证最后token释放/GC后交易读旧base、继续prepare及真实commit conflict，最后交易退出才收回root；三surface restore保持内容/revision并更新发布身份；epoch0非法Committed/Exact surface view仍拒绝。原rootAdmission交错、候选隐身/单次消费/foreign/晚输入变化、完整write set重试和Freehand压力/取消保持。

build/MOC后[图](callgraph-final.log)为87TUs/2006APIs/24753edges/21callbacks。[初检](architecture-stale.log)仅两份源指纹过期；审阅后[刷新](architecture-refresh.log)、[独立门](architecture-final.log)通过21manifest/25ownership/16census/19intrusion。[前](baseline-before.json)/[后](baseline-after.json)ratchet不变，checker/manifest/ownership政策未改。[12项检查](deletion-checks.json)及[冻结脚本](check_delivery.py)绑定[52源码](source-sha256.txt)、[15运行物](runtime-sha256.txt)及[环境](build-environment.json)，不以静态删除代替行为。

列明清理完成；epoch工作数组/root/core/control、Qt实际容量和tree最后释放仍归原CP1。未新增TSAN、性能、全局allocator或完整永久尾退出资格。**完整CP1开放，M6/M7/M8正式0/3、默认关闭。** 当前裁决见[92 §16.58](../../92_br1_m6_m8_execution_baseline.md#epoch-protocol-residue-delivery)，差集从[NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)领取。
