# CP3 已接受 metadata batch 删除重复物理索引（2026-10-05）

产品 `864627f95737c62fe79da87677c8f4b0ab44c55a`，父 `84b5d5aad9f4c0c890ea2fc6dd5fb92548111524`；当前裁决见 [92 §16.124](../../92_br1_m6_m8_execution_baseline.md#cp3-metadata-batch-delivery)。

原 `applyProjectedSequence` 的 canonical 输入和状态机逐步接受结果已经保证物理身份唯一。原 ShardRecordStore 直接消费同一个 accepted working result，删除 `batchPhysicalSlots` 的 hash、桶、逐 replica 节点及完整构造/free 生命周期。`canInstallPhysical` 的版本内重复与全 canonical 跨页面碰撞检查、arena/index 实际预留、输入顺序、revision 重试、Debt、拒绝和安装边界保留。无替代数组/排序器、第二 snapshot owner、常驻字段、公开 API 或绕过开关。[开始边界](start-review.json)、[完整责任](checkpoint-review.json)清点全部身份引入、转移及真实消费者。

生产一文件 **+10/-14，净-4**；两个测试文件 **+127/-3**。新增24组独立 oracle/global collision 用例，覆盖1/2/3/33 replicas、同 numeric slot 不同 provider/epoch、跨版本新/新与已有 identity、foreign page 冲突、原记录读/release、整体拒绝及无预留泄漏。旧压力用例经实际反例修正：观察到旧 epoch root 的真实176B后台free后，每次seal重试前重新填满原4MiB限额；Debt用例占满实际 spare replica slots，强制接受Debt后实际arena增长，原2MiB/原子回滚断言保持。[全部失败、父控制及修正](execution-issues.json)分别保留，不计入最终通过总数。[补丁/提交](delivery.json)绑定原字节；生成audit两文件另列，ratchet不提高。

原三个四桶40对协议顺序运行960进程，全部正常退出/reaped/同源绑定。Fresh/H4原单侧98.75%桶下界须≥0.98；handoff降幅下界K1≥20%/K16≥30%，四桶family至少95%置信。未扩样或截尾。

| 指标 | ARM K1 | ARM K16 | x86 K1 | x86 K16 |
|---|---:|---:|---:|---:|
| Fresh 当前÷固定M5 | 1.0881 | 0.9075 | 1.1421 | 0.9666 |
| Fresh 单侧下界 | **1.0697** | 0.8873 | **1.1185** | 0.9625 |
| H4 当前÷固定M5 | 1.4034 | 1.1837 | 1.2144 | 1.2582 |
| H4 单侧下界 | **1.3844** | **1.1445** | **1.1875** | **1.2417** |
| handoff延迟降幅 | 1.48% | 8.14% | 2.23% | 8.64% |
| handoff单侧下界 | 0.90% | 7.12% | -0.13% | 7.71% |

[Fresh](fixed-m5-fresh-summary.json) K1通过，K16仍低固定M5约3–9%，整族失败；[H4](fixed-m5-history-summary.json)四桶/scoped family通过；[handoff](latency-summary.json)四桶失败。相对上一轮，Fresh K16比值0.8810/0.9241→0.9075/0.9666，handoff相对当前Fresh的优势10.92%/12.07%→8.14%/8.64%。native K16绝对中位延迟的跨轮描述趋势：ARM Fresh177.38→158.75μs、handoff158.20→145.43μs；x86 Fresh/handoff原值见各轮summary。跨轮归一化和绝对值不计算本提交因果收益，也不外推真实brush体验。固定M5 `5173c807c87bb1619325249a07a8b4f4f8f09f09` 的[实际依赖/选项](matched-control-build-options.json)保持；公共Fresh N64/K1、N1024/K16，H4包含四个undo事务，native handoff N=K/H0/B4完整first-write/seal/canonical commit，端点/分母不互换。

[冻结父库](parent-runtime-identity.json)来自§16.123最终运行库SHA；当前/父同ABI同harness的两架16进程/128样本核对before、新内容、实际payload和close。[首次完整操作请求](allocation-summary.json)：Fresh K1 **61次/15944B→55次/15720B**、K16 **591次/198352B→495次/194768B**；handoff K1 **53次/17024B→50次/16912B**、K16 **419次/224128B→371次/222336B**，两架一致。Fresh每页少6次、handoff少3次，是累计malloc-family请求，不能替代common metadata实际驻留或速度门。

[安全结算](validation-summary.json)：原双架38进程 **10872/0/0**，每架16目标5366/0/0，正确ReadBaseline45、selected persistent business11及Vulkan foundation14齐全；[实际安装](install-counts.json)每架31080 handoff/28 publication区间alloc/bytes/free0、正allocator控制4，24真实allocator边界及registration64通过。结构87TU/2185 indexed APIs/28750 edges/27callbacks，21manifest/25ownership/16census/19intrusion及六工具通过，原ratchet保持。[最终核对](final-verification.json)绑定2315当前/1143 M5 Git blobs、302runtime/harness及20身份集合。

[实际公共write-loop](public-fresh-steady-profile/localization.json)仍指向完整预算准入/费用/free与原工作值；[原生handoff准备定位](native-handoff-profile-02/localization.json)在原未改harness4096上界内、实际completed-operation marker后采样，确认原prepareWritePlanLocked/preparePublicationImpl。后者包含setup/validation/cleanup，exclusive各线程及context rows仅定位，不能相加或当因果占比。[下一完整候选责任审查](next-recoverable-candidate-audit.json)沿原单页recoverable候选的输入/容量/收费/revision/claim/安装/拒绝/冷free核对所有消费者；shared Data的普通publication/restore/detachment区别保持，不盲合数组或新增owner。

**完整CP3/M6仍开放，M6/M7/M8为0/3，persistent默认关闭。** Fresh K16、handoff20%/30%、common metadata重构前used/reserved/slack同义驻留≥25%分母及CP0完整required仍缺。CP1/CP2及已结算责任不重领；长/OFF/其他完整模式/TSAN限制保持，不由请求/行数/局部速度扣工时。[原始日志附件](raw-logs.tar.gz)与[逐member SHA](raw-log-manifest.json)保留成功与失败原文，二进制、对象和测试图片不入库。
