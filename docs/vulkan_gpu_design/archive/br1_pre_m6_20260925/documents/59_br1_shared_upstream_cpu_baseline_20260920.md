> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D5：共享主干 CPU 基准与剩余管线差距（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

本轮落实 52 的 P1：固定 `origin/master@9a24ae0d8c` 与当前 D4 生产实现，使用**同一份测试源码**、双方原生 tiles3
接口比较，不在主干套 PageStore 协议。本轮新增测试/测量脚手架，未修改生产性能实现。

**独立限时完成吞吐揭示：暖读管理仍有差距，单行真实写的差距远大于预绑定 memcpy 控制组。D4 的分支内收益不等于
恢复主干性能；BR1-PERF 仍未结清。** 固定工作量长桶、尾延迟、完整 M/K/E 不劣性和 GPU/UMA 产品资格均未由本轮取得。
原件和复算入口见 [D5 证据](../../../evidence/br1_d5_20260920/README.md)。

## 1. 实现与对照边界

- 新 target：`kis_tiles3_cpu_baseline_test`。同一源文件 SHA256 为
  `4caba36adde8bcf3a18245a7ae9be86391b5e9b3071591dba4e6ab0c6e9761c3`；主干仅添加该 fixture 和 CMake 测试入口。
- 两侧均为 Qt 6.8、RelWithDebInfo `-O2 -g -DNDEBUG`、universal x86_64/arm64 构建，在 Mac16,10、24 GiB、macOS 15.7.3
  上以 arm64 执行。冻结的编译器/架构/优化/测试/lock-free hash 配置逐项核对；完整 CMake cache、编译命令、源码切片和
  实际装载库身份保存在 identity 与 run manifest。Python 查找环境存在差异，不用于本 target 的像素/管理执行路径。
- 32 个 fixture 数据桶涵盖 4/8/16 BPP、guard、lookup、blank、未暴露 pointer 的 write intent、alias、readBytes、writeBytes、
  预绑定 memcpy。双方全 fixture 均 **34 passed**（含 init/cleanup）；验证最终像素、未修改的其余行、extent 和 alias source 不变。
- 配对完成后，当前 Foundation **24 passed**、Reference **42 passed**，静态架构检查通过；日志随证据保存。
  本轮未重跑完整 tiled-manager/产品套件或 Vulkan 测试，不将 D4 的历史全套记录改写为 D5 新测。
- 非空目标先通过真实 writeBytes 建立独立 native backing，随后预热读访问。alias 的两个 immutable source 在计时前准备，
  timed region 调用 `bitBltRough`，不再使用 D4 交替 clear 的 caller-side uniform 初始化；仍保留双方原生比较、索引与提交成本，
  归为操作级 E，不标纯 M。
- real write 每次只改变每页一条 scanline，交替两个不同值，其余 63 行保留；H=0，无外部旧 reader、单线程、in-flight=1。
  主干可复用独占 tile；当前仍经过 native COW 初始化及 generic request/lease/proof/epoch 路径。这是同一同步写任务的
  不同实现成本，不能把内部多出的协议记账作为 additional semantics 扣掉。
- kernel 桶提前持有 read pin，按相同 memcpy 算法复制 16 页共 256 KiB 到预备输出。它只是 resident payload 控制，
  不是 brush/SIMD 产品 K 的完整资格，也不是 GPU/UMA 证据。

## 2. 已完成的测量与结果

主协议十桶、补充 readBytes 一桶；每桶 **12 对**独立进程、轮换桶顺序并交替 upstream/current，合计 **264 次配对运行**。
每个进程独立运行至少 200 ms，每完成 64 个原生操作检查一次截止时间；不合并业务操作、不记录逐事件时间、不启用 phase
profiler。吞吐按实际完成量/墙钟计算。whole-window calling-thread/process CPU 另测，setup、manager destruction 另列。

下表是每秒完成的 **operation**，不是每秒 tile 或像素字节；guard/lookup 的 K=16 表示每操作访问 16 页，write 的 K=16
表示一次 writeBytes 修改 16 页。各行独立配对，不能跨不同 N/K/BPP 直接归因格式成本。

| fixture（N/K/BPP） | 主干 ops/s | 当前 ops/s | 当前/主干吞吐比 | 探索性 95% 区间 |
|---|---:|---:|---:|---|
| cached guard 1024/16/4 | 6,173,117 | 4,562,390 | 0.7408 | 0.7343–0.7485 |
| lookup + guard 1024/16/4 | 3,084,727 | 2,397,595 | 0.7781 | 0.7701–0.7888 |
| blank lookup 64/1/4 | 28,625,047 | 22,421,491 | 0.7840 | 0.7809–0.7860 |
| 未升级 intent 64/1/4 | 49,481,822 | 42,621,004 | 0.8621 | 0.8566–0.8659 |
| prebuilt-source alias 1024/16/4 | 419,427 | 10,705 | 0.0257 | 0.0254–0.0261 |
| real write 4096/1/4 | 33,832,641 | 91,966 | 0.0027 | 0.0027–0.0028 |
| real write 1024/16/4 | 2,513,511 | 9,853 | 0.0039 | 0.0039–0.0040 |
| real write 64/1/8 | 30,948,645 | 103,598 | 0.0034 | 0.0033–0.0034 |
| real write 64/1/16 | 26,896,868 | 94,995 | 0.0035 | 0.0035–0.0036 |
| prebound memcpy 1024/16/4 | 278,100 | 289,485 | 1.0408 | 1.0045–1.0645 |
| readBytes 1024/16/4（补充协议） | 2,508,086 | 2,162,312 | 0.8621 | 0.8584–0.8680 |

比值是进程 pair 比的中位数，不是两列中位数相除；区间按完整 pair bootstrap，seed591137、20000 resamples。
补充 read 桶单独冻结协议后测量，不与主协议伪装成同一运行。没有冻结 M 不劣性容差，故不授予 M Pass；也不把 CI 跨 1
称作等价。这里是 **200 ms 窗口的完成吞吐**，不是单次延迟分布、饱和多线程吞吐或无限长稳态。

calling-thread CPU/完成 operation 的独立时钟结果：guard、lookup、blank、intent 的当前/主干比约为
1.350/1.285/1.275/1.160，alias 约 38.88，四个 write 桶约 255–367。它们不是延迟倒数，也不能直接填为 P50/P95。
该窗口 process CPU 与 calling-thread CPU 接近，只说明本次覆盖窗口的成本主要在调用线程，不能据此宣布预克隆/后台 drain 为零。

memcpy 控制组的某一 pair 也存在约 1.41× calling-thread CPU/operation 的反向偏移，原件保留；不能以总表中位数声称普遍
4% 算子加速。其作用是反证“当前所有 RAM 像素访问都数量级变慢”，不用于量化 write 管线每个子阶段占比。

## 3. 与预期不符及缺测存根

| 存根 | 预期与实际 | 处理与下一证据 |
|---|---|---|
| D5-upstream-gap | D4 real fixture 约减半，但与主干同 harness 的真实写完成吞吐仍仅约 0.27%–0.39% | native CPU 访问/写入/提交路径仍是主线；不能以 native duplicate 已接入宣布同构或性能恢复 |
| D5-warm-management | native cached read/intent 已有局部优化，管理生命周期吞吐仍只有主干约 74%–86% | 继续正式 captured view/stack guard/local pin；冷 miss、retained view、并发读与独立 self 尚需补测 |
| D5-long-window | 主干 K1 write 达到 200 ms 需 8,388,608 次，K16 需 1,048,576 次；当前逐 ticket 终态存储随累计操作增长 | 先跑独立限时 rate；固定-work 配对未跑，不能用 rate 代替 latency。见下文记录增长研究 |
| D5-counter-scope | rate 两侧完成数不同；RSS 包含 setup/allocator/进程其他部分 | 不用其比值证明每操作内存效率；按相同累计操作数补 registry/provider/root 分项及 drain |
| D5-kernel-variation | payload 控制无数量级退化，但某一 pair 反向偏移明显 | 保留原件，后续扩展环境/缓存/算子矩阵；不删除离群点或外推 GPU/UMA |

源码已确认 `KisCompletionRegistry` 每 source 用 QHash 保存每个分配 ticket，complete 仅修改终态；当前没有逐 ticket
释放或压缩。tiles3 provider 另有 `consumedOperations` QSet。前者是可直接定位的累计记录增长，不代表已量化其 RSS 占比，
更不代表数百倍操作差值都来自它。固定-work 长桶在计时前发现这一混杂因素，因此尚未执行；测量分支决定见
[measurement-decision.md](../../../evidence/br1_d5_20260920/measurement-decision.md)，不是发生 OOM 后删除失败结果。

下一记录布局研究需保留完整语义：对已逐项确认且相邻同状态的终态压缩，pending gap、Failed/Cancelled、乱序完成、
重复 complete 拒绝及 registry/source/value identity 不能丢。较大 host ticket 成功绝不代表较小 ticket 成功。加入实际记录数、
累计 ticket/operation、active/retired 与峰值指标，再分别测有界性与 CPU；压缩只是候选，尚未实装。provider replay ledger
与 root/history 留存仍独立验收，不能以 completion 压缩替代全系统有界回收。

## 4. 对优化方向的校准

本轮支持原来的架构判断：不是推翻 canonical PageStore，而是让 CPU resident data path 实际下沉到 native guard/session/
受 owner 证明的原位或必要首写 COW，以及短发布；不能继续把通用异步协议逐页套在原生 CPU 操作上，再期待 memcpy 微调
追回差距。管理暖路径也未达到目标，不能只优化写。

下一步同时保留两条约束：

1. 主线是 P2/P3/P5 的原生 CPU 访问与写提交，并以本 fixture 加上历史/reader/abort/并发负例和原产品 E 验收。版本可见性、
   safe permit 与唯一 authority 不因主干更快而放宽；不合并原有可见操作来制造吞吐。
2. 完成记录/防重放布局是阻止长跑测试被累计状态污染的具体子项；先加精确统计/安全负例，再切片优化和 before/after。
   不预言其单独能够恢复主干水平；每个切片仍需重新采样 prepare/resolve/publish/commit/retire。

D4 分段图只解释 D4 相应 fixture；不能把 D5 吞吐比反算成这些子阶段的绝对耗时。D2-B-small-K 历史反证仍未关闭。
完整固定-work latency、尾分位、M 不劣性、H/并发/压力、产品 replay、drain 和 GPU/UMA 保持待测；本轮不开放 BR2 产品接线。
