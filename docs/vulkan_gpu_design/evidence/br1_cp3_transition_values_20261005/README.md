# CP3 原 metadata 工作值与固定 M5 控制（2026-10-05）

产品 `b8581139d22bc68d1ff15d93f44167c18bac4db3`，父 `840d14ae71f5c5ed4999b7ce545bbeee685fb7cf`；文档父 `01104423a30cd09d329265d1795cfb636cbd5c10`。当前裁决见 [92 §16.116](../../92_br1_m6_m8_execution_baseline.md#cp3-transition-values-delivery)。**完整 M6 未通过，M7/M8 未取得资格，persistent 默认关闭。**

## 完整原责任与删除

seal 的私有 publication 产生可独立 capture、取消和重试的 Prepared/overlay；canonical commit 另行推进 root。两个可见性/回滚边界均保留。普通 publication 只需转换前的 identity/publication/preparedBy；原 `deltas` 数组暂存这些字段，消费原 working value 后原位压缩，新增 immutable records 直接从同一 working array 交给 installRecords。支持的三种普通转换保持输入顺序且只可能追加记录，现有 full oracle 覆盖它们。删除完整 before 深复制、第二 additions 数组和重复 authority 插入。

局部 owner sequence 也直接消费原 paid working value；只保留 original version identities，用于成功后的删除和 unlocked growth/debt 竞争重试记账。严格 revision、所有 lifetime/identity guards、部分准备拒绝和原 Data/Entry/arena token 终点保持。没有新 owner、公开 API、常驻字段、队列或通用 helper。

生产一文件 **+47/-27，净+20**：轻量字段/身份留存及原位压缩替代两份完整嵌套状态，不能把它说成净删行或驻留下降25%。测试新增0；三个 ownership/生成文件 **+524/-542**；原 ratchet 保持。实际 diff/审阅见 [checkpoint-review.json](checkpoint-review.json)和 `KisPageMetadataCoordinator.cpp.patch`。

## 当前同源验证

双架每架完整16 CPU目标5335/0/0、persistent业务11/0/0、ReadBaseline45/0/0、重建foundation14/0/0，共 **38进程10810/0/0**，actual0/reaped/指定库与前后SHA通过。早先目标组不累加；LIMIT_LONG_TESTS、未覆盖的完整模式/OFF/TSAN限制保持。两架各31080真实handoff及28 index/root/descriptor/restore安装区间，malloc family及明确audit线程的mmap/munmap均alloc0/bytes0/free0，实际拒绝和正控制保持。

结构门：87TU/2185APIs/28246edges/27callbacks，21manifest/25ownership/16census/19intrusion，六项工具自测通过。[最终核对](final-verification.json)绑定2315 source/audit Git blobs和202 runtime/harness输入。[固定M5核对](controls-final-verification.json)另绑定当前1158/M5 1143 Git blobs及152 runtime/harness输入、17核心构建选项和相同fixture源码，不累加为上述产品矩阵。capability原身份中未执行的旧公共fixture二进制已明确排除；两个有效throughput scope使用重编后的fixture/独立probe身份。

原native beginWrite的16次malloc请求计数：Fresh K1为25次/4680B（父26/5144），K16为441次/91856B（父457/99280）；handoff仍16次/3776B及238次/89728B。这只是冷请求分母，不是完整 metadata 驻留或性能证明，见 [cold-summary.json](cold-summary.json)。

## 性能与新取得的主阻塞

[latency-final/protocol.json](latency-final/protocol.json)沿用40独立进程配对、四桶轮换/顺序平衡、8warmup+64测量、诊断关闭、单侧98.75%每桶/整体至少95%、固定停止无剪裁。320进程23040操作全部正常。H0/N=K/B4，同一exact验证capture，begin transaction/native完整首写至seal/canonical commit，setup及验证/close另计。

| 架构 | K | Fresh/Handoff中位数 | 配对降幅 / 下界 | 原门 |
|---|---:|---:|---:|---:|
| arm64 | 1 | 30.22 / 28.67 μs | 5.25% / 4.55% | 20% |
| arm64 | 16 | 331.48 / 293.20 μs | 11.11% / 10.43% | 30% |
| x86_64 | 1 | 48.37 / 45.76 μs | 5.32% / 3.09% | 20% |
| x86_64 | 16 | 524.21 / 465.59 μs | 11.15% / 10.41% | 30% |

四桶均未达门，见 [latency-summary.json](latency-summary.json)。上一批绝对计时与本批不是直接源码配对，不能相减计算本批因果收益。opt-in phases嵌套且运行时有M5构建，只定位、不相加或授予性能。

固定 `5173c807c87bb1619325249a07a8b4f4f8f09f09` 已在 `build/br1-fixed-m5-20261005/source` 重建，依赖/工具链/架构/编译和核心选项匹配当前。原 public baseline CPP 源码完全相同，各自按其真实头文件编译。H0原scanline CpuReadable控制和H4新public full-payload/commit/逐页sentinel/四memento保留及purge控制各预注册40对/四桶、250ms直接completed-work throughput、20顺序平衡blocks、50000 bootstrap seed260926、单侧98.75%每桶，最低比值0.98。两个scope分别95% family，不能合称一个完整required family。H4的H是undo事务数，不冒充native root handle计数；setup、最终undo/redo与close在timer外。两个有效scope共640实际正常退出进程；全16 capability进程另计。

| Scope | arm64 K1 / K16 当前÷M5 | x86_64 K1 / K16 当前÷M5 | 裁决 |
|---|---:|---:|---|
| 原H0 scanline | 0.6934 / 0.4017 | 0.7270 / 0.3988 | 四桶均未通过0.98 |
| H4 public full-payload/history | 0.8945 / 0.5787 | 0.7844 / 0.5876 | 四桶均未通过0.98 |

完整比值/置信界见 [Fresh结果](fixed-m5-fresh-summary.json)、[history结果](fixed-m5-history-summary.json)。这是当前相对固定M5的累计差距，不能归因本批+20行。原来“固定对照未运行”已变为实际不通过：Fresh K1吞吐低27–31%、K16约60%；H4 K1低11–22%、K16约41–42%。后续优先处理原存储准入/实际收费/释放的共同成本，保留硬预算和真实收费，再校验受保护控制与handoff门；不继续围绕单个allocation堆helper。

额外hot sample已等待实际QTest init及N1024 setup后采样，current栈集中在 `KisBackingBudgetController::fitsLocked/reserveLocked/commitRetaining` 与 `kisAllocateMutationStorage` 的收费/锁链。仅作为下一原责任定位，不从sample占比计算因果收益；先前直接启动0.5s的sample只捕获dyld启动，保留且不用于定位。下一须审查原 allocation admission → 实际分配 → commit收费 → free/晚释放 → wake/close，不能为提速关闭accounting或放宽预算。

## 失败与剩余资格

第一次固定Fresh运行当前进程10492 actual-11/reaped，栈在extent memory_resource读取，地址为MUTZ allocation header。该独立fixture未先重建当前对象布局；Ninja随后实际重编CPP并重链接，产品源码未修。原失败/runner/协议/IPS保存在 `fixed-m5-fresh`，不混入新完整40对的 `fixed-m5-fresh-02`。首次新control builder借用了CPU-test link list，M5未构建testsupport静态库而链接失败；改用已构建public baseline真实flags/link list，全部日志保留。

共同working value责任本批完成；正式CP3/M6继续未通过。缺项仍包括原20%/30% handoff门、上述固定M5控制回修、重构前common metadata used/reserved/slack同义驻留≥25%的可运行分母、CP0完整required及正式样本。Git中BR1前仅disabled stub，重构前材料路径已向用户询问；不自行把sizeof ceilings或本表cold malloc bytes当分母。M7/全部M8/BR1-PERF及完整目标保持。

全部原 `.log` 与 sample/IPS失败保留；raw压缩清单和构建/源码/库身份见本目录的JSON。二进制、object、dylib、managed构建目录及外层gitlink不提交。
