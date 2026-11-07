# CP3 原限额计算与完整准入政策（2026-10-05）

产品 `822456732bd02a13d128b855ed9856415544ec00`，父 `9c707902d68130a17de4cbd6d64a761215387be0`；文档父 `5a808ce5f24e2cd63799eff5681899319398319e`。当前裁决见 [92 §16.118](../../92_br1_m6_m8_execution_baseline.md#cp3-budget-limits-delivery)。**完整 CP3/M6 未通过，M6/M7/M8仍0/3，persistent默认关闭。**

原 `fitsLocked` 和 `priorWaiterConflictsLocked` 共同改为每类一次 domain 值、每次调用一次 aggregate 值；两个 scalar selector 删除。七类四域、负请求拒绝、live/reserved/aggregate/durable、饱和求和、空 usage 的 irreducible metadata、原 process snapshot 和先前 waiter 的有限额度冲突全部保持。没有常驻 cache、字段、owner、队列或公共 API，没有跳过未变化类的检查。signed physical move 的正域预留与净 class/SSD 增长、原 allocation/commit/free/晚尾/wake/close 不变，见 [完整政策审查](policy-review.json)。

生产一文件 **+22/-30净-8**，测试改动0；两个生成 audit **+867/-867**，原 ratchet 相等。arm64 实际编译的 fits 指令264→212、waiter冲突164→136，只是静态编译结果，不作为吞吐因果收益。原 helper 的全部两个消费者已经迁移，见 [审阅](final-review.json)及三份原 Git `.patch`。

保存的父库 SHA 与上一包最终证据相符；相同 evidence binary 分别加载父/当前库，两架每进程 **800000** 次实际私有 member 判断，四进程结果 digest/接受分布完全一致。包含任意及边界 usage/reserved、负 delta、UINT64、全部类/域、empty usage 与实际 process storage。evidence-only template friend access 没有进入生产。该差分证明列明输入的等价，生产竞争/生命周期由原矩阵和探针另证，见 [差分](policy-differential-summary.json)。

最终原 **38进程10810/0/0**：每架完整16 CPU目标5335、选定 persistent业务11、ReadBaseline45、正确的 VulkanFoundationContracts14；actual0/reaped/指定库及前后SHA通过。两架各31080 handoff、28 index/root/descriptor/restore安装区间malloc/VM alloc/bytes/free0，真实allocator22边界通过。87TU/2185APIs/28248edges/27callbacks、21manifest/25ownership/16census/19intrusion和六工具自测通过。[最终绑定](final-verification.json)验证当前2315/M5 1143 Git blobs及271 runtime/harness输入、18身份集合；LIMIT_LONG_TESTS、完整其他模式/OFF/TSAN资格保持开放。

三个性能 scope 沿原40对/四桶、顺序平衡、预注册样本/停止规则和单侧98.75%门。Fresh/H4各20独立blocks、50000 bootstrap seed260926、throughput下界≥0.98；handoff原20%/30%门、20000 bootstrap seed12345。全部960性能进程actual0/reaped/身份与正确性通过，三个scope分别裁决，不合称完整required family；绝对值不与上一包相减作为因果收益。

| 架构 / K | Fresh÷M5 / 下界 | H4÷M5 / 下界 | handoff降幅 / 下界 |
|---|---|---|---|
| arm64 / 1 | 0.9410 / 0.9299，未过 | 1.2062 / 1.1753，通过 | 4.44% / 3.95%，未过20% |
| arm64 / 16 | 0.5535 / 0.5432，未过 | 0.7884 / 0.7716，未过 | 9.83% / 7.91%，未过30% |
| x86_64 / 1 | 0.9887 / 0.9718，未过 | 1.0620 / 1.0506，通过 | 4.25% / 3.63%，未过20% |
| x86_64 / 16 | 0.5536 / 0.5433，未过 | 0.8048 / 0.7846，未过 | 9.62% / 8.96%，未过30% |

[Fresh结果](fixed-m5-fresh-summary.json)、[H4结果](fixed-m5-history-summary.json)、[延迟结果](latency-summary.json)绑定原协议、完整样本和身份。x86 K1点估计在2%范围内，但下界仍失败；H4 K1两桶通过不关闭完整family。

本轮执行错误和失败保留于 [问题记录](execution-issues.json)：父库首次缺loader别名，检查发现加载当前库而拒绝，另开完整有效差分；首次policy binary在执行前修正有溢出风险的证据输入生成，旧binary不参与资格。误跑全部Freehand为15/4，精确父库同样15/4且四失败case相同，两个失败进程都不计成功业务资格，不修改容差。误选PageStoreFoundation的两组中间兼容结果不参与最终共同绑定；正确Vulkan contracts重建后每架14通过。性能预检查两次在任何benchmark启动前拒绝错误路径/缺终态。没有生产修复与失败样本混入成功组。

[原准备边界审查](plan-preparation-review.json)确认native已经在Ready实际allocation/terminal verification后合并Acquire/Prepare；generic的初始化/readiness和失败终结有独立消费者，private Prepared/overlay与canonical root仍需不同接受边界。下一完整责任为实际首写metadata/ledger工作存储与每页分配：先枚举值、consumer、转交、拒绝及真实free，不能继续添加等价helper或盲合并这些边界。common metadata重构前used/reserved/slack同义驻留≥25%分母、CP0完整required及正式M6继续欠缺；CP1/CP2不重领，CP4/M7仍以M6资格为前置。

所有实际运行日志保存于 `raw-logs.tar.gz` 和逐文件SHA清单，编排失败另由问题记录与原runner保存；二进制/object/dylib/构建目录、图片与外层gitlink不提交。
