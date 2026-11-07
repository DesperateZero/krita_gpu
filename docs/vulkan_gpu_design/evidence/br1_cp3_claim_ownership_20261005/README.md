# CP3 登记源 claim 归回原物理 slot（2026-10-05）

产品 `84b5d5aad9f4c0c890ea2fc6dd5fb92548111524`，父 `5086aa6ef92e81575eca58e6862d411a593cfb7c`。当前资格统一见 [92 §16.123](../../92_br1_m6_m8_execution_baseline.md#cp3-claim-ownership-delivery)。

已登记源的逻辑 claim 从原物理记录 classClaim cookie、slot generation 和原 slot.changes 派生；空闲查询使用既有 free-slot 计数。删除逐源键 reserve/insert/erase/extract、对应收费节点/桶增长及第二个 detached handoff node。未登记目标仍保留独立键索引与冷 slot detached node，安装后至冷复用/析构才实际 free。选中源拒绝 same-class no-op，未选中 alias 允许 no-op；实际 class/domain transition、新 alias、取消、并发、退休及预算边界保持。[开始边界](start-review.json)、[完整责任](checkpoint-review.json)列全部消费者和等价依据。

生产一文件 **+139/-133，净+6**（含原91行 projection 移入既有 Private）；独立行为测试 **+80/-0**。12组物理页、24个alias同时准备，覆盖增长、选中/未选中 no-op、实际变更/新alias排斥、部分取消、slot复用、commit及完整退休。无新常驻字段、owner、队列、公开API或保证；busy membership沿其原slot扫描O(K)，不是第二索引。[补丁](product-final.patch)、[提交身份](delivery.json)保留原字节；生成audit两文件+6742/-6037另列，ratchet不提高。

原三个四桶40对协议顺序运行960进程，全部正常退出/reaped/同源绑定，不并行build/benchmark/采样，不扩样或截尾。Fresh/H4原单侧98.75%桶下界须≥0.98；handoff降幅下界K1≥20%/K16≥30%，四桶family至少95%置信。

| 指标 | ARM K1 | ARM K16 | x86 K1 | x86 K16 |
|---|---:|---:|---:|---:|
| Fresh 当前÷固定M5 | 1.0704 | 0.8810 | 1.1307 | 0.9241 |
| Fresh 单侧下界 | **1.0612** | 0.8732 | **1.1150** | 0.9151 |
| H4 当前÷固定M5 | 1.3803 | 1.1510 | 1.1875 | 1.1950 |
| H4 单侧下界 | **1.3710** | **1.1490** | **1.1821** | **1.1902** |
| handoff延迟降幅 | 4.40% | 10.92% | 4.50% | 12.07% |
| handoff单侧下界 | 3.39% | 10.06% | 3.14% | 11.54% |

[Fresh](fixed-m5-fresh-summary.json) K1两桶通过，K16仍低固定M5约8–12%，整族失败；[H4](fixed-m5-history-summary.json)四桶/scoped family通过；[handoff](latency-summary.json)四桶失败。固定M5 `5173c807c87bb1619325249a07a8b4f4f8f09f09` 的[实际选项/依赖](matched-control-build-options.json)保持。Fresh是原公共scanline端点N64/K1、N1024/K16，H4包含四个undo事务，handoff是native N=K/H0/B4完整first-write/seal/canonical commit。跨轮归一化比值只描述趋势，不授予本提交因果速度或真实brush体验结论。

[冻结父库](parent-runtime-identity.json)由§16.122最终运行库SHA绑定；当前/父同ABI同harness，两架16进程/128样本核对before、新内容、真实payload及close。[首次完整操作请求](allocation-summary.json)：Fresh K1 **64次/16088B→61次/15944B**、K16 **624次/200176B→591次/198352B**；handoff K1 **56次/17200B→53次/17024B**、K16 **468次/226720B→419次/224128B**，两架一致。完整范围/全部样本保留；这是audit线程malloc-family累计请求，native payload另核对，不替代common metadata实际驻留或速度门。

[安全结算](validation-summary.json)：原双架38进程 **10824/0/0**，正确ReadBaseline、selected persistent business及Vulkan foundation齐全；[实际安装](install-counts.json)每架31080 handoff/28 publication区间malloc-family alloc/bytes/free0，24实际allocator边界、registration64通过。结构87TU/2185 indexed APIs/28716 edges/27callbacks，21manifest/25ownership/16census/19intrusion及六工具通过，原ratchet保持。[最终核对](final-verification.json)绑定2315当前/1143 M5 Git blobs、301runtime/harness及19身份集合。

[真实write-loop定位](public-fresh-steady-profile/localization.json)等待init marker并确认write frames；all-thread exclusive产品栈包括fitsLocked108、storage owner deref41、snapshot14、实际分配13及projection12，不计因果比例。按§17.4的[下一完整责任审查](next-metadata-batch-audit.json)，原ShardRecordStore::putBatch的物理identity去重临时set仍按每个真实replica分配节点；先核对完整输入/消费者、canonical collision、arena/index预留、拒绝/安装/free，再选表示。本审查尚未实现或取得性能资格，不新增snapshot owner或放宽limiter。

**完整CP3/M6仍开放，M6/M7/M8为0/3，persistent默认关闭。** Fresh K16、handoff20%/30%、common metadata重构前used/reserved/slack同义驻留≥25%分母及CP0完整required仍缺。CP1/CP2和本批源claim、已结算authority/工作值移动/sparse root不重领；原长/OFF/其他完整模式/TSAN限制保持，不从请求/行数/测试数扣工时。[原始日志附件](raw-logs.tar.gz)与[逐member SHA](raw-log-manifest.json)保留运行原文，二进制、对象、测试图片不入库。
