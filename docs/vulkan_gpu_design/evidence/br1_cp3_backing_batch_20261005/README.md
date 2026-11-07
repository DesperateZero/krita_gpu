# CP3 backing 分类批量准备（2026-10-05）

产品 `feff9031b1e356c7967e1b5066ec6896549dc491`，父 `58b4dfc09c3048d2f344ccb35a3d92d80adc390f`。当前资格统一见 [92 §16.121](../../92_br1_m6_m8_execution_baseline.md#cp3-backing-batch-delivery)。

本批收敛同一 Ledger gate 内的逻辑目标合并、物理别名投影和 prepared claims：四组临时收费哈希存储替换为连续 pointer/index 数组，物理 claim 从逐次线性查找改为排序去重。实际 class priority、原 retirement record、每物理页首个 credit、预算与 rollback、handoff node 转交及最终 free 保持。完整入口/删除/增长理由见 [开始边界](start-review.json)、[责任核对](checkpoint-review.json)。多项独立非法输入同时存在时，首先报告的拒绝原因可改变；接受、单项拒绝及权威状态语义保持。

生产一文件 **+98/-60，净+38**；独立 flat physical accounting 测试 **+92/-0**，八个打乱次序的 24 逻辑／8 物理页批次核对重复 effects、分类竞争、并存 claim、取消与最终收费。无新增常驻字段、owner、队列或公开 API。生成审计两文件 +6349/-5897 单列；[最终补丁](product-final.patch)、[交付身份](delivery.json)保留实际字节。

全部 build/safety/control 前置完成后顺序运行三个原 40 对／四桶 scope，960 性能进程正常退出并回收，不并行构建、benchmark 或采样，不截尾或扩样。每桶采用原单侧 98.75% 下界，四桶 family 至少 95%；Fresh/H4 吞吐下界须≥0.98，handoff 延迟降幅下界 K1≥20%／K16≥30%。

| 指标 | ARM K1 | ARM K16 | x86 K1 | x86 K16 |
|---|---:|---:|---:|---:|
| Fresh 当前÷固定 M5 | 1.0307 | 0.8355 | 1.1136 | 0.8737 |
| Fresh 单侧下界 | **1.0260** | 0.8262 | **1.0918** | 0.8660 |
| H4 当前÷固定 M5 | 1.3601 | 1.0924 | 1.1695 | 1.1398 |
| H4 单侧下界 | **1.3511** | **1.0799** | **1.1653** | **1.1316** |
| handoff 延迟降幅 | 4.03% | 9.44% | 3.87% | 9.22% |
| handoff 单侧下界 | 3.03% | 8.59% | 2.85% | 8.52% |

[Fresh](fixed-m5-fresh-summary.json) K1 两桶通过，K16 仍低固定 M5 约13–16%，整族失败；[H4](fixed-m5-history-summary.json) 四桶及 scoped family 通过；[handoff](latency-summary.json) 四桶失败。固定 M5 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`，[实际构建选项](matched-control-build-options.json)和全部来源/依赖/运行库均核对。Fresh 是原公共 N1024/K16 单 scanline 端点，H4 为四个 undo 事务，handoff 为 native N=K/H0/B4 完整 first-write/seal/canonical commit；三个分母不能互换。跨轮归一化结果只作趋势，不推算本提交因果速度或真实绘画体验。

同 ABI 的 [冻结父库](parent-runtime-identity.json)由父批最终运行库 SHA 绑定；两架加载同一当前 harness，16 进程／128 实际样本核对 payload、前后内容和 close。[外部请求诊断](allocation-summary.json)中首次完整 begin/write/seal/commit：Fresh K1 **74次/16888B→66次/16168B**、K16 **758次/208400B→656次/196400B**；handoff K1 **68次/18128B→58次/17312B**、K16 **622次/237088B→500次/223456B**。两架一致，所有样本和范围保留。分母是 audit 线程 malloc-family 请求；native payload delta 独立验证，不是 common metadata 的完整驻留分母，也不是性能门。

[安全结算](validation-summary.json)：原双架 38 进程 **10820/0/0**、actual exit 0/reaped，正确 ReadBaseline、selected persistent business 和 Vulkan foundation 齐全；额外每架 31080 handoff 和28 publication/restore 安装区间 malloc/VM alloc/bytes/free 均0，24 allocator 边界通过。结构门 87TU/2185 APIs/28547 edges/27callbacks、21 manifest/25 ownership/16 census/19 intrusion及六工具自测通过，原 ratchet 保持。[最终核对](final-verification.json)绑定2315当前／1143 M5 Git blobs、301 runtime/harness 和19身份集合。

原 public fixture 的 [steady 采样](public-fresh-steady-profile/localization.json)等待实际 init marker，确认 write loop；all-thread exclusive 产品栈仍以 fitsLocked126、storage owner deref30、实际分配16以及 prepared claims/metadata 为定位。后台等待与产品工作分列，不计因果占比。下一审完整首写 publication 内原 authority/候选容量及实际费用准入，先明确真实 consumer 和拒绝/安装边界，再决定消除哪些存储；不增加同义 helper 或第二 selector，不重领本批 backing merge/claim 去重、已交付工作值移动/sparse root 或 CP1/CP2。

**本批交付不关闭完整 CP3/M6。** Fresh K16、handoff20%/30%、common metadata 重构前 used/reserved/slack 同义驻留≥25%分母及 CP0 完整 required 仍开放；M6/M7/M8仍0/3，persistent默认关闭。原长压测、OFF、其他完整模式及TSAN的既有限制保持。[原始日志附件](raw-logs.tar.gz)与[逐 member SHA](raw-log-manifest.json)保留运行原文；二进制、对象及测试图片不入库。
