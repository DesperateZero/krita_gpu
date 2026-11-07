# CP3 原 metadata 候选一次收费分配（2026-10-06）

产品 `6ffe097909e23adf3afd229a2a14e93986fae00b`，父 `864627f95737c62fe79da87677c8f4b0ab44c55a`；当前裁决见 [92 §16.125](../../92_br1_m6_m8_execution_baseline.md#cp3-candidate-storage-delivery)。

原 PreparedPublication::Data 的 entries、publications、arenaGrowth 三套独立收费 vector 改为同一 Data 分配中的有界尾部存储。detachment 不分配 publication/growth，多页发布按实际分片数预留，单页恢复候选跳过分片 census；嵌套保护列表、arena 和 authority 仍由原 allocator 收费。所有原准备、查询、claim/install、取消、分批/延迟清理和最终 free 消费者一起迁移，三套独立 reserve/growth/free 删除。原身份、revision、容量、activity、预算与失败政策保持，无新 owner、队列、公开 API、许可开关或恢复域。[开始边界](start-review.json)、[完整责任及净增长审查](checkpoint-review.json)绑定本批。

生产 **+110/-17，净+93** 实现原 owner 的有界视图和检查过的对齐布局；直接固定内嵌会增加所有 detachment/batch 候选成本，按 kind 再建 owner/allocator 会分裂清理规则。测试 **+31/-21** 将原生命周期 fixture 扩到0/1/2/33页及1/4分片，覆盖原六种终结；旧夹具复用物理 slot 的注册失败修正为每页独立身份，生产碰撞检查保持。初次54失败、构建目录拒绝及修复分别保留在[失败登记](execution-issues.json)；修正后的当前/父同ABI专项均282/0/0。[交付补丁](delivery.json)与生成audit单独统计，ratchet不提高。

原三个四桶40对协议顺序运行 **960进程**，全部正常退出/reaped/身份绑定；Fresh/H4各桶单侧98.75%下界≥0.98，handoff降幅下界K1≥20%/K16≥30%，四桶family置信至少95%。未扩样、删失败或调整阈值。

| 指标 | ARM K1 | ARM K16 | x86 K1 | x86 K16 |
|---|---:|---:|---:|---:|
| Fresh 当前÷固定M5 | 1.1064 | 0.9064 | 1.1594 | 0.9790 |
| Fresh 单侧下界 | **1.0907** | 0.8635 | **1.1329** | 0.9648 |
| H4 当前÷固定M5 | 1.2928 | 1.1976 | 1.2303 | 1.2606 |
| H4 单侧下界 | **1.2731** | **1.1366** | **1.2111** | **1.2508** |
| handoff延迟降幅 | 5.54% | 12.60% | 4.80% | 13.48% |
| handoff单侧下界 | 4.78% | 11.37% | 3.35% | 12.56% |

[Fresh](fixed-m5-fresh-summary.json) K1通过，K16仍失败；[H4](fixed-m5-history-summary.json)四桶/scoped family通过；[handoff](latency-summary.json)四桶仍未达到原门。与上一轮相比，handoff K16降幅约8.1%/8.6%→12.6%/13.5%，Fresh K16比值0.9075/0.9666→0.9064/0.9790；这是[跨轮描述](performance-comparison.json)，不计算提交因果收益。当前native K16 Fresh/handoff中位延迟为ARM155.59/136.56μs、x86 240.61/207.99μs。固定M5 `5173c807c87bb1619325249a07a8b4f4f8f09f09` 的[依赖/选项](matched-control-build-options.json)相同；public Fresh N64/K1、N1024/K16，H4含四次undo，native handoff N=K/H0/B4完整first-write/seal/canonical commit，端点/分母不互换。

[冻结父库](parent-runtime-identity.json)来自§16.124实际最终库SHA。原Store MutableGuard完整首次写入/seal/commit的[同ABI16进程128样本](allocation-summary.json)核对before、新像素、物理增量与close。两架一致：Fresh K1 **55次/15720B→52次/15864B**，K16 **495次/194768B→490次/192928B**；handoff K1 **50次/16912B→44次/17200B**，K16 **371次/222336B→318次/222800B**。请求减少，累计字节不一致下降；不得当作common metadata used/reserved/slack驻留节省，free计数受合法后台回收影响亦保留全部值。

[安全矩阵](validation-summary.json)原双架38进程 **11112/0/0**，每架16目标5486/0/0，正确ReadBaseline45、selected persistent五方法11及Vulkan14；[实际安装](install-counts.json)每架31080 handoff/28 publication区间alloc/bytes/free0，正allocator控制4，24真实storage边界和registration64通过。[结构](structure-summary.json)87TU/2207 indexed APIs/28842 edges/27callbacks，21manifest/25ownership/16census/19intrusion及六工具通过。indexed私有视图方法数不代表公开API增长。[最终核对](final-verification.json)绑定提交Git blobs、实际库/harness及全部同源身份。

[真实public写循环](public-fresh-steady-profile/localization.json)在原6s write/3s sample和实际init marker后确认writeBytes、provider allocation/adoption等13条上下文。all-thread exclusive仅定位预算/收费/free，不计因果占比。按§17.4，[下一完整provider候选审查](next-provider-candidate-audit.json)核对原物理分配、adoption、residency注册、binding、retire/free；逻辑句柄/共享物理backing的实际基数和保活区别保持，尚未选择或实现下一替代。

**完整CP3/M6仍未通过，M6/M7/M8为0/3，persistent默认关闭。** Fresh K16、handoff20%/30%、common metadata重构前同义驻留≥25%分母及CP0完整required/正式场景样本继续开放。已结算责任不重领；长/OFF/其他完整模式/TSAN限制保持，不用请求/行数/局部速度扣旧工时。[原始日志](raw-logs.tar.gz)及[逐member SHA](raw-log-manifest.json)保留全部成功与失败，二进制/对象/图片不入库。
