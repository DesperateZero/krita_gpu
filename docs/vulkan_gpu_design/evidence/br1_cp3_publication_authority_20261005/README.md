# CP3 publication authority 快照批量构造（2026-10-05）

产品 `5086aa6ef92e81575eca58e6862d411a593cfb7c`，父 `feff9031b1e356c7967e1b5066ec6896549dc491`。当前资格统一见 [92 §16.122](../../92_br1_m6_m8_execution_baseline.md#cp3-publication-authority-delivery)。

原 Data 独占的 authority 哈希快照改为同一收费 owner 的连续数组：首个实际页按真实 authority 数量 reserve，后续使用原 vector 增长，准备完成时按既有 MetadataKeyLess 排序，所有查询二分并校验完整身份。原页键/工作版本已唯一，删除 insert-or-assign、VersionHash、哈希节点/桶及依赖 include。每个原 authority 都保留，recoverable base/target 仍由 installRecords 派生；revision、claims、arena/activity准备、取消/移动/安装及实际 free保持。见[开始边界](start-review.json)、[完整责任](checkpoint-review.json)。

生产一文件 **+22/-16，净+6**，独立查询测试 **+65/-0**；无新常驻字段、owner、队列、公开API或保证增量。32个打乱页键、64个 authority 核对负坐标、多surface、generation/default revision/surface缺失查询、移动/取消/重试和最终安装。生成audit两文件+7459/-6646单列；[补丁](product-final.patch)、[身份](delivery.json)保留原字节。

全部前置完成后，原三个40对/四桶scope顺序运行960正常进程，不并行build/benchmark/采样，不截尾或扩样。原单侧98.75%桶下界及至少95%family置信保持；Fresh/H4下界须≥0.98，handoff降幅下界K1≥20%/K16≥30%。

| 指标 | ARM K1 | ARM K16 | x86 K1 | x86 K16 |
|---|---:|---:|---:|---:|
| Fresh 当前÷固定M5 | 1.0409 | 0.8604 | 1.1059 | 0.8940 |
| Fresh 单侧下界 | **1.0256** | 0.8539 | **1.0705** | 0.8907 |
| H4 当前÷固定M5 | 1.3777 | 1.1188 | 1.1782 | 1.1820 |
| H4 单侧下界 | **1.3648** | **1.1116** | **1.1735** | **1.1765** |
| handoff延迟降幅 | 3.31% | 10.29% | 3.66% | 10.35% |
| handoff单侧下界 | 2.83% | 8.84% | 2.16% | 9.34% |

[Fresh](fixed-m5-fresh-summary.json) K1两桶通过，K16仍低M5约11–14%，整族失败；[H4](fixed-m5-history-summary.json)四桶及scoped family通过；[handoff](latency-summary.json)四桶失败。固定M5 `5173c807c87bb1619325249a07a8b4f4f8f09f09` 的[实际构建选项](matched-control-build-options.json)及依赖保持。Fresh为原公共scanline端点N1024/K16，H4为四个undo事务，handoff为native N=K/H0/B4完整first-write/seal/canonical commit；三个分母不互换。跨轮归一化只描述趋势，不推算本提交因果速度或真实绘画体验。

[冻结父库](parent-runtime-identity.json)由§16.121最终运行库SHA绑定；两架16进程/128样本加载同一harness，真实payload、before、新内容和close核对。[首次完整操作请求](allocation-summary.json)：Fresh K1 **66次/16168B→64次/16088B**、K16 **656次/196400B→624次/200176B**；handoff K1 **58次/17312B→56次/17200B**、K16 **500次/223456B→468次/226720B**，两架一致。K16少32次请求，但数组增长使累计请求字节增加3776B/3264B；全部样本与范围保留。分母是audit线程malloc-family请求，native payload另核对；不作为common metadata驻留或速度资格。

[安全结算](validation-summary.json)：原双架38进程 **10822/0/0**、actual0/reaped，正确ReadBaseline、selected persistent business和Vulkan foundation齐全；额外每架31080 handoff/28 publication安装区间malloc/VM alloc/bytes/free0，24 allocator边界通过。结构门87TU/2184 APIs/28641 edges/27callbacks、21manifest/25ownership/16census/19intrusion及六工具通过，ratchet保持。[最终核对](final-verification.json)绑定2315当前/1143 M5 Git blobs、301runtime/harness与19身份集合。

[后继steady定位](public-fresh-steady-profile/localization.json)等待真实init marker并确认write loop；all-thread exclusive产品栈仍为fitsLocked127、storage owner deref41、实际分配25和prepared claims11等，不计因果占比。按§17.4重审下一完整claim责任：[原消费者清点](next-claim-audit.json)发现既有source键与physical classClaim/slot changes可能表达重叠事实；未登记handoff目标必须保留键保护，same-class no-op对选中源与未选中别名的拒绝差异也必须保留。该清点尚未实现或授予删除/性能资格，不直接删掉logical guards，不引入第二claim owner或放宽limiter。

**完整CP3/M6仍开放，M6/M7/M8为0/3，persistent默认关闭。** Fresh K16、handoff20%/30%、common metadata重构前used/reserved/slack同义驻留≥25%分母及CP0完整required仍缺。原长/OFF/其他完整模式/TSAN限制保持；不重领本批authority快照、已结算backing合并/工作值移动/sparse root或CP1/CP2。[原始日志附件](raw-logs.tar.gz)与[逐member SHA](raw-log-manifest.json)保留运行原文；二进制、对象和测试图片不入库。
