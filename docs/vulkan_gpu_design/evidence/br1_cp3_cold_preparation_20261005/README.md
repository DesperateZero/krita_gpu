# CP3 共同冷准备与 activity 安装释放收敛（2026-10-05）

产品 `840d14ae71f5c5ed4999b7ce545bbeee685fb7cf`，父 `500fd0702cfa07ba447d538fb9aad2b086e3160f`。当前裁决见 [92 §16.115](../../92_br1_m6_m8_execution_baseline.md#cp3-cold-preparation-delivery)。本批减少实际冷分配并关闭恢复安装 free=129；**完整 CP3/M6 未通过，M7/M8 未取得资格，persistent 默认关闭。** 完整目标和 CP0–CP10 排期保持。

所有原始 `.log` 逐字节保存在 [raw-logs.tar.gz](raw-logs.tar.gz)，路径、长度与 SHA 见 [raw-logs.json](raw-logs.json)，已完整解包核对。新 checkout 在本目录执行 `tar -xzf raw-logs.tar.gz` 即恢复原日志路径，供下述 probe/分析脚本读取；失败和早先候选也完整保留。当前 workspace 的原日志未删，Git只提交压缩包，避免把重复loader输出展开到代码审阅。

## 原责任与删除

- Recoverable preparation 将原收费 working array 交给 StateMachine，再直接转交 base/target 两记录给原 installRecords。两者 authority 从同一记录派生；其他 authority 保留原索引语义。删除 recoverable 的深复制、第二安装数组及两份 authority hash 节点，不改变严格 revision、保护、physical/logical claim 或首字节前拒绝。
- 全部 publication/restore/recoverable 的 arena 准备共用原 `growMetadataArenasOutsideLock`。已有未预留容量在锁内立即预留，只为缺口门外分配并复验；删除无条件 full-demand blocks 和第二套 attach/growth 循环。全部 shard 的 slot/index tokens 仍在安装前取得，部分拒绝仍由原 Data 取消；空块不能脱离 outstanding reservation。
- Ledger 原收费冷 slot 内联两个原 node handles，删除动态 holder 分配和 reserve。实际节点费用到冷复用/析构才释放；没有新 selector、owner、队列、字段或公共 API。
- 恢复 additions 探针在父提交实测 alloc0/free129、actual24/reaped，栈落在清除 publication claim 时 erase activity 节点。原 Entry 现在继续持有已准备 reservation，瞬时 claim 仍立即撤销；原 `releaseActivity` 统一 installed/cancelled Data 析构及增量 cleanup。删除提前消费 count/清除 Entry 标记的私有函数，没有新增节点或退休队列。真实费用保持至原延迟清理释放。

生产两文件 **+67/-96，净-29**；已有 Reference 测试 +3；架构 checker +6/-1；三份生成/ownership 审计 **+5162/-4678**。删除的 `consumePublicationActivity` 由现有 `setPublicationClaim` 和 `releaseActivity` 接替；checker 同步要求这两个责任，并拒绝恢复安装期消费保护的旧路径。全部原 layout/intrusion/ownership 上限不提高。真实分配/寿命保证和等价删除分列，不以净删行数领取性能。

## 实际冷分配

外部 malloc/calloc/realloc/aligned allocation/free interposition 只包围每页原 native `beginWrite`，每组16次真实完整操作。父 critical image 在改动前保留并核对 SHA；最终每次均验证像素、地址复用、payload delta、commit 和 close。以下为每组计数中位数；**这是 allocator 请求字节，未把 VM payload 或全 metadata 驻留算入该分母。**

| K / variant | 父请求次数 / bytes | 当前请求次数 / bytes | 当前 frees |
|---|---:|---:|---:|
| 1 Fresh | 26 / 5144 | 26 / 5144 | 12 |
| 1 handoff | 31 / 56608 | 16 / 3776 | 7 |
| 16 Fresh | 457 / 99280 | 457 / 99280 | 203 |
| 16 handoff | 447 / 909744 | 238 / 89728 | 169 |

handoff 请求字节减少约93.3%/90.1%，没有新增 before payload。计数见 `cold-complete-allocations.json`，父原日志保留；这些 interposed 操作的计时不作性能判断。

## 当前同源验证

`matrix-final-{arm64,x86_64}` 各完整16目标5335/0/0；`business-current-*` 各11/0/0，保留正常、cancel、四类拒绝、24MiB压力及8MiB取消；`read-current-*` 各45/0/0；重新构建的 `foundation-current-*` 各14/0/0。最终 **38进程10810/0/0**，均actual0/reaped、无超时、指定库和前后 SHA 核对；Qt init/cleanup 包含在 totals，未注册长测试、TSAN、完整其他模式/hash/OFF 不授新资格。早先候选矩阵不累加。

`install-final-vm-*-run` 两架各 **31080** 个真实 handoff 安装区间，五 route、四 BPP、1/64/65/129页、commit/cancel及两类竞争，全部 alloc0/bytes0/free0。`publication-final-vm-*-run` 各28个 exact/physical index、root/metadata/descriptor、restore additions 区间也全部零；包括并存候选取消及实际映射分配拒绝后 index 保持。共享 Qt 正控制分配4次。最终 interposer 同时覆盖 malloc family 和明确 audit 线程的 mmap/munmap，未添加生产故障开关。

`parent-publication-02` 明确加载保存的父 image，复现 restore free129；第一次父 launcher 缺 image soname 链接，未算有效父身份。旧 probe 的 new override 无法命中当前收费 allocator；后继只拦 malloc 仍漏掉大 index 的 VM 分配；首次全局 mmap interposition 在 bootstrap 退出-6。改为仅对明确 audit 边界已经初始化的线程启用 VM 观测，最终实际拒绝与安装都通过。失败原日志保留，没有据此重开已结算的 CP1。

`architecture-qualified.log`：21manifest/25ownership/16census、87TU/2185APIs/28248edges/27callbacks、19intrusion；六项工具自测通过。`checkpoint-review-final.json` 审阅三个实际 source 差集及独立 CI checker，随后刷新 source checkpoint。旧 checker 对已删除函数的拒绝日志保留；替代的是实际责任断言，没有提高 ratchet。`final-verification.json` 将最终源 SHA 对应产品 Git blobs，并核对两个构建目录及 probe/harness 输入。源码与产品测试的编辑只使用显式补丁。

## 性能与剩余主路径

最终 `latency-final/protocol.json` 先冻结40对/四桶轮换/顺序平衡、每进程8warmup+64操作、诊断关闭；进程为独立配对单位，20000次 bootstrap、单侧98.75%每桶、四桶整体至少95%。固定停止，不剪裁/扩样。端点包含 begin transaction、native preserve首写、完整 payload、seal、canonical commit；setup及validation/close另计。H0、N=K、B4、两侧同一exact验证capture，仅 alternate availability 不同。320实际正常退出进程/23040操作，所有行为和输入 hash 正确。

| 架构 | K | Fresh中位数 | handoff中位数 | 配对延迟降幅 | 单侧98.75%下界 | 门 |
|---|---:|---:|---:|---:|---:|---:|
| arm64 | 1 | 32.26μs | 30.51μs | 5.36% | 4.81% | ≥20% |
| arm64 | 16 | 364.76μs | 321.50μs | 11.79% | 10.38% | ≥30% |
| x86_64 | 1 | 50.70μs | 47.92μs | 5.49% | 4.74% | ≥20% |
| x86_64 | 16 | 578.03μs | 509.05μs | 11.64% | 10.76% | ≥30% |

从父受控场景慢5–7%转为当前快5–12%，但四桶仍未达门。这是当前 controlled selector 场景，**不是 fixed-M5/history nonregression、upstream、stroke E、尾分位数或完整正式 M6 性能资格**。早先 `latency-paired` 是 activity 修复前候选，脚本原文和失败样本保留，不与最终320进程累加。

额外 opt-in phase 仅定位：K16 seal private publication约64μs、commit transition preflight约62μs、completion约45μs，Recoverable prepare约65μs/install约9.7μs。采时有开销、nested interval 重叠且当时有并发正确性矩阵，不能相加或计算因果收益。实际仍有普通 publication 的 before→StateMachine 深复制及 seal/commit 两次既有准备；下包先从真实消费者核对完整共同 publication 准备责任和必须独立的可见性/失败边界，再决定如何合并/删除，不继续围绕单个 allocation 增加 helper。

固定 `5173c807c87b` 同依赖 Fresh/history≤2%、common metadata实际驻留≥25%及重构前同义 used/reserved/slack 分母、CP0完整required/正式样本仍欠；不能用本表冷请求字节或 layout ceilings 代替。连续两次 CP3 局部交付尚未达主性能门，已按92 §17.4重审剩余 owner/端点；没有可靠实际人日，原27–43人日剩余估算继续低置信，不能把本批净删或请求减少折算成 M7/M8 交付速度。
