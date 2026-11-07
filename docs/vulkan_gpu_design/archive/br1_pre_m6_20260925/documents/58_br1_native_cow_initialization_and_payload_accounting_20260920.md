> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D4：native COW 初始化与实际 payload 工作计量（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

本轮落实 52 的 3.2.1，消除 D3 确认的 preserve “先 default-fill、再整页 source-copy”。
**固定真实写 fixture 的分支内配对耗时下降约 41%–56%；不是 isolated M/K、upstream 不劣性或 BR1-PERF 结清。**
完整原件、脚本、源码切片和版本身份见 [证据目录](../../../evidence/br1_d4_20260920/README.md)。

## 1. 已落实的接口与路径

- `KisReplicaCapabilities::synchronousWriteCopy` 明确声明同步 CPU 初始化能力，默认 false；必须同时支持同步操作及 CPU view。
  新增 `prepareSynchronousWriteCopy(operation, source, targetVersion, descriptor, priority)`，默认 Unsupported、不执行工作。
- PageStore 仅对 preserve、同 provider/epoch、同 CPU 存储域选择该路径；未支持时在调用前选既有 prepare + transfer。
  一旦 native 调用已经执行，失败不静默重试另一条初始化路径。成功结果必须是终态 Ready、独立 allocation、正确目标
  version/layout/provider/epoch，并通过 owner completion 验证；随后沿既有 AcquireWrite/PrepareWrite/resolve/publish/commit。
- tiles3 provider 在既有局部 mutex 下验证 exact source、layout、目标同页新 generation 和 writer 状态；通过
  `KisTileDataStore::duplicateTileData` 创建独立新 backing，直接 source 初始化，不再 default-fill 后覆写。source 对象由
  provider ownership 保护，直接复制时复用主干 swap pin。旧 reader/history 不阻止安全 COW，活动 writer 阻止复制其 mutable bytes。
- 成功初始化后不再进行第二次 transfer/completion 消费；generic request、PageStore owner gate、epoch/metadata 和
  每次通用 write 的 generation/COW 仍在。**这不是 native guard/session、原位 permit 或整条管线同构主干。**

没有新增全局锁，也没有改成 CAS 状态机。provider allocation 记录增加活动访问数/writer 状态，lease 记录保存 mode；
retire 可 O(1) 检查活动访问，release 必须先归还 swap pin 再让 allocation 可退休。消费 write seed 后的早期失败也归还引用，
分配失败的 pending completion 终结为 Failed；metadata 拒绝 AcquireWrite 前不安装该 generation 的 descriptor。
这些安全/计量修正同时存在于 before/after，不作为 native 初始化的独立收益报告。

## 2. 正确性证据

本轮 CPU 构建及回归：Reference **42**、Foundation **24**、完整 tiled-manager **88** passed（Qt totals 含 init/cleanup）。
其中固定 N/K/H/模式/格式的 52 桶均包含在完整 tiled-manager 中；before 单跑该 fixture 为 54 passed。
补充 tile store **5**、pooler **3**、Vulkan foundation contracts **13** passed；pooler 的6条 `QEXPECT_FAIL` 在 original 和
after 同样出现，保留原件，不能当作本轮新失败或完整预克隆证明。Vulkan 配置首次构建缺少 `MACOSX_DEPLOYMENT_TARGET`，
按既有 cache 的12补齐后重建通过；失败及重试日志均保留。这是接口兼容构建/测试，不是 GPU 产品路径性能验证。
新增测试覆盖：

- 4/8/16 BPP exact 全页初始化、目标独立、修改目标不影响旧 source、保留 reader 期间复制；
- 活动 writer、stale provider epoch、跨页/非前进 generation、layout 失配、operation 重放及预算不足拒绝；
- 消费 seed 后预算失败不漏引用，active lease 阻止 retire；
- PageStore provider 回调可重入读取 session stats，验证全局锁外调用；错误 operation/非终态结果拒绝、候选回收、不转入 fallback；
- publish 后 abort、commit、保留旧 epoch 再读及 close 后 provider committed bytes 归零。

这些测试不是全部产品 suite、长压力或 GPU/UMA 性能证据。已知的长期 replay/metadata 有界性、所有并发失效组合、完整
native guard/session 和正式 upstream M/K/E 仍按 52 继续验收。

## 3. 对照设计与实际 payload 工作

`original` 为 D3 当前 binary，仅用于新增脚手架的关闭态对照。`before` 为 D3 加本轮 API、计数器、额外 provider phase、
生命周期修正和相同 fixture，native 实现已经编译但能力未启用；`after` 仅将 tiles3 的 `synchronousWriteCopy` 开为 true。
源码归档核对确认两侧 tracked image patch 相同，provider 源文件只有这一个能力值差异。正式配对使用同一 before executable
交替加载保存的 before/after library，loader 日志与 SHA256 验证身份；不是运行时绕过安全校验的 benchmark 开关。

十桶每桶六对，交替 A/B 顺序并轮换桶顺序；K1 为 32768 操作，K16 为 4096 操作，每个计时区间均 ≥100 ms。
其中 real 模式同一 operation 只改每页一条 scanline，保留其余 63 行；双方 actual page work、commits、adoptions/write requests、格式和
history 相同。配对计时不与构建/其他 benchmark 并发。

口径复核（不新增测量）：`testPageStoreFixedPageWork()` 的 alias 模式在计时内交替两种颜色调用 `clear()`；
`KisTiledDataManager::clear()` 的单项 uniform cache 因换色而 miss，调用 `createDefaultTileData()` 生成 source backing，
再共享/adopt 到目标页。该 caller-side 初始化未计入目标 provider 的 defaultInitialized 计数，故 alias 是包含数据准备的
操作级控制组，不是 isolated M；“目标 provider 零 default-fill”也不是进程零填充。正式 M 仍需按 39 单独配对。
另，`writeBytesBody()` 已将一个 tile 块的连续多行放在同一 WRITE wrapper 内；本 fixture 的单行输入不能证明实际多行写
每行重复 COW。once-per-session 优化需测显式 mutation 内的重复页访问，并保留发布/reader 可见性边界，见 52 的 3.2。
源码依据：`libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp::testPageStoreFixedPageWork()`、
`libs/image/tiles3/kis_tiled_data_manager.cc::clear()`、`libs/image/tiles3/kis_tiled_data_manager_p.h::writeBytesBody()`。

以下是**单位 operation** 的 μs，不是每页或 isolated pixel kernel：

| 模式 / N / K / H / BPP | before μs/op | after μs/op | paired median ratio | 探索性 95% 区间 |
|---|---:|---:|---:|---|
| alias / 4096 / 1 / 0 / 4 | 17.291 | 17.296 | 0.996 | 0.965–1.030 |
| alias / 4096 / 1 / 4 / 4 | 18.131 | 18.256 | 1.007 | 0.988–1.030 |
| alias / 4096 / 16 / 4 / 4 | 86.557 | 86.823 | 1.007 | 0.995–1.016 |
| real / 4096 / 1 / 0 / 4 | 19.810 | 11.148 | 0.562 | 0.556–0.566 |
| real / 4096 / 1 / 4 / 4 | 20.938 | 12.246 | 0.593 | 0.578–0.602 |
| real / 4096 / 16 / 0 / 4 | 245.508 | 107.220 | 0.436 | 0.434–0.441 |
| real / 1024 / 16 / 0 / 8 | 225.802 | 105.435 | 0.470 | 0.462–0.474 |
| real / 1024 / 16 / 4 / 8 | 237.179 | 117.607 | 0.498 | 0.486–0.501 |
| real / 1024 / 16 / 0 / 16 | 253.778 | 117.464 | 0.461 | 0.458–0.471 |
| real / 1024 / 16 / 4 / 16 | 265.040 | 128.711 | 0.486 | 0.482–0.503 |

ratio 是各进程 pair 比值的中位数，不等于两列中位数相除。六对进程 bootstrap（seed937，10000 resamples）为探索性区间，
未冻结 NI margin；控制桶区间跨 1 不证明不劣性。4 BPP 与宽格式的 N 不同，不据这些跨桶数字单独推算格式成本。

在计量覆盖的目标 provider/operation 区间内，每个 real changed page：

| 工作 | before | after |
|---|---|---|
| default 初始化 | 一整页 | 0 |
| 显式 provider transfer copy | 一整页 | 0 |
| native duplicate | 0 | 一整页 |
| native preclone hit | 0 | 本次全部 0 |
| 必要 source 保留与未改像素 | 保持 | 保持 |

4/8/16 BPP 的每整页逻辑字节分别为 16/32/64 KiB。after 并非零 payload copy；本次所有 native duplicate 均为前台直接复制。
这些是代码发起的逻辑工作，不是 DRAM 流量。defaultMaterializationRequests 两侧都可为零，不影响这里实际 default fill 的差异。
计数包含执行后被丢弃的初始化；adoption、generation、发布成功量另列，不能混用分母。

## 4. 采样与资格边界

新增 `write_provider_prepare` 和 `write_provider_transfer` 均包含于 write_acquire，再包含于 write_bytes_body，不能父子求和。
prepare 在 before 是 allocation + default 初始化 + provider bookkeeping，在 after 是 allocation + native source 初始化 +
bookkeeping；只比较同名 prepare 会漏掉 before 的 transfer。应比较 prepare+transfer 子路径及完整 acquire/operation，仍不能
将 provider inclusive 时间称为纯 M、纯 memcpy 或 isolated K。

六次操作级抽样合并的 wall μs/被采中 operation（K1/H0 共1548 samples；K16/H0 共193 samples，均4 BPP）：

| 阶段 | K1 before | K1 after | K16 before | K16 after |
|---|---:|---:|---:|---:|
| write_bytes_body（父区间） | 13.919 | 4.965 | 222.385 | 80.126 |
| ↳ acquireWrite | 11.320 | 2.356 | 181.247 | 38.641 |
| ↳↳ provider prepare | 8.414 | 0.731 | 134.376 | 12.412 |
| ↳↳ provider transfer | 0.632 | 无调用 | 10.427 | 无调用 |
| ↳ resolve | 0.387 | 0.394 | 5.979 | 6.176 |
| ↳ publishHostWrite | 1.217 | 1.209 | 19.409 | 19.368 |
| write_bytes_batch_finish（含 commit） | 10.253 | 10.337 | 46.875 | 46.703 |

这支持“实际初始化是重要放大项”的方向，但不是无扰动 self 成本；parent/child 不相加，也不把阶段差与 plain E 的差
做精确闭合。K1 after 的 finish 已超过 body，K16 after 则 body 和 finish 均显著；不能统一改口成只剩 commit 瓶颈。
残余 acquire 仍包含 native 初始化和协议；下一步分别量化局部 guard/resolve、host publication/proof 与 batch finish。

关闭态 scaffold 对照：alias K1 ratio1.000、区间[0.986,1.007]，real K1 ratio1.003、区间[0.990,1.013]，未确认整体偏移，
不证明零成本。plain/sample 校准并非全部中性：before 的 real K1/H0 ratio1.011 [1.005,1.023]，H4 ratio1.008
[1.005,1.019]；alias K1/H0 反向为0.984 [0.959,0.994]。after 六桶中位比约0.998–1.017，区间均跨1、最宽边界约
[0.994,1.039]。因此稀疏采样仅用于归因；不能承诺严格1%上界，也不能把反向偏移称为 profiler 加速。
原始顺序、offset、计数与进程 pair 全部保留，周期相关性/空 scope/更广环境控制仍待完善。

本轮未测硬件流量、预克隆后台补充 CPU/峰值 reserve、完整产品 replay/tail 或正式主干 M/K/E，不据零命中推断后台零工作。
新 provider lifetime counters 不是全进程计数、峰值、retire 有界或 GPU/UMA 证据。GPU/UMA 产品性能保持 NotMeasured。

## 5. 偏差登记与继续研究

| 编号 | 预期与实测 | 后续约束 |
|---|---|---|
| D4-payload-init | 消除覆写前 default pass；实测填充/transfer 归零且 real 桶明显降低 | 方向得到分支内证据支持，但融合还减少一次协议调用，不能把全部耗时收益归给 memcpy/填充单项 |
| D4-preclone-zero | 接上主干 duplicate 可能复用预克隆；实测命中全部为 0 | 不声称预克隆贡献；研究 provider ref 与 legacy usersCount、pooler 资格/唤醒/预算，再补前后台总工作证据 |
| D4-control | 未改 alias 路径；三控制桶未确认变化 | 不将本轮真实写收益外推到主要为 alias/history/delete 的原混合 stress，后者尚无本轮独立配对资格 |
| D4-sampling | 关闭态未确认偏移，但部分采样桶出现约1%正偏移与反向偏移 | 不承诺零扰动或严格1%上界；采样单次不能替代 plain E，继续校准空 scope/周期相关性/环境漂移 |
| D2-B-small-K | 56 的历史 6%–10% 回退仍是 D2-A→D2-B 问题 | 本轮 D3+脚手架→native 对照不自动关闭该项，保留原件与版本边界 |

下一步按 K1 的 finish 与 K16 的剩余访问/发布分别拆解：用共同语义 upstream 对照分出协议 M，推进 session 内复用与
native guard；同时检查 host proof/publication、candidate/root、retire 的必要工作和重复工作，不继续主攻已明显缩小的默认填充。
保留 52 的完整 P1–P6 目标。必须继续区分：payload 初始化已优化；generic request/
completion/metadata、owner gate、每 session/页一次 first-write、生产 root/cursor 与 adapter history delta 尚未完成。
需要正式 upstream 管理配对与原产品 resident E，不能用本轮约减半的定向 fixture 替代 CPU 主干等价结论。
