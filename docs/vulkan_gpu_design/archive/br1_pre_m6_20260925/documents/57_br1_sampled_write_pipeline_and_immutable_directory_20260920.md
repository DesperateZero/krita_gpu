> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D3：操作级抽样、完整写管线与 immutable metadata directory（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

本轮回应 56 的 small-K 反证：延长区间、交替版本、测完整 writeBytes，再调整优化优先级。
**BR1-PERF 未结清；本轮未取得明确性能加速，不能以移除一把锁代替性能出口。**
命令、版本、完整日志及复算见 [证据目录](../../../evidence/br1_d3_20260920/README.md)。

## 1. 测量改进与实际边界

- 固定 fixture 最大循环数扩至 262144（默认正确性循环仍为 4）。配对诊断选 N4096/BPP4 的六桶：alias/real 的
  K1/H0、K1/H4，以及 alias K16/H4、real K16/H0；K1 每次 16384 操作，K16 每次 4096 操作。
  实际区间均检查 ≥100 ms。没有把此六桶替代 52 桶完整格式/复杂度矩阵。
- 每桶六对、奇偶 pair 反转 A/B 顺序、轮换 case 顺序；同一测试 executable，用 `DYLD_LIBRARY_PATH` 选保存的 library，
  loader trace 验证实际装载路径。记录 executable/library SHA256；没有构建与 benchmark 并发。
- 新增 writeBytes 的 owner-wait/batch-begin/body/batch-finish 四个连续阶段；body 内 acquireWrite/resolve/publishHostWrite
  是**包含于父阶段的子区间**，finish 内已有 commit 子区间。不能把父子阶段求和。
- recorder 可在无活跃 recorded timer 时切换记录，按整个操作采样；1/127 周期、各 pair 轮换 offset，使嵌套阶段共同
  进入/退出采样。记录实际 sampled_operations/intervals，不把未采到的操作说成零耗时，也不据此估算尾延迟。
- paired median ratio 的 95% 区间以**进程 pair 为单位** bootstrap，只有六对，是探索性区间。未冻结正式 NI margin，
  未作 upstream 对照；不能把区间跨 1 当成不劣性通过。

### 扰动校准

六桶 plain/sample 配对中位耗时比约 **0.998–1.005**，所有探索性区间跨 1（最宽边界约 0.976–1.019）；相比 55/56
全量阶段计时的约 15%–17% 扰动，支持采用稀疏操作级采样。**不证明绝对零开销或严格 1% 上界。**

关闭 recorder 的新旧诊断 binary 对照也不是完全中性：alias K1 中位比约 0.992，real K1 约 **0.942**。没有新增像素
优化却出现偏移，其原因未确定（代码布局、构建、运行环境等仍是候选），不能把它归入目录优化收益。该对照受旧 fixture
4096 循环上限限制、区间低于 100 ms，只作扰动诊断；因此后续 A/B 都冻结在相同的新诊断 executable/接口下。

抽样降低的是**整个 benchmark** 的时钟开销；被抽中的单次操作仍执行全部阶段时钟，其内部耗时仍受扰动。
不能用 sampled phase mean 乘 127 重建精确无 profiler E。空 scope 校准/尾延迟/更广环境复验仍未结清。

## 2. 完整真实写管线：不能只盯 commit

以下为目录优化前、六次抽样合并的 wall μs/**被采中的操作**；K1 共 774 samples，K16 共 193 samples。
K16 列是一次写 16 页的整个 operation，不是每页；每阶段含时钟成本。

| 层级/阶段 | K1/H0 | K16/H0 |
|---|---:|---:|
| writeBytes owner wait | 0.017 | 0.018 |
| writeBytes batch begin | 0.543 | 0.569 |
| writeBytes body（父区间） | 13.117 | 211.970 |
| ↳ acquireWrite（body 内） | 10.549 | 171.470 |
| ↳ resolve（body 内） | 0.379 | 5.827 |
| ↳ publishHostWrite（body 内） | 1.201 | 19.052 |
| writeBytes batch finish（父区间，含 commit） | 10.101 | 46.915 |

源码核对：`acquireWrite` 仍有 transaction/root/metadata resolve、多个 operation/request/writer identity、全局 request
map、provider prepareWrite 和 transfer 两次锁外调用/锁重取、完成票据消费及多次 metadata transition。
tiles3 provider 的 preserve 初始化仍是先创建 default tile backing，再由 transfer 复制 source bytes；它没有直接使用
主干 first-write COW/native guard 协议。因此这是 **native TileData backing + 通用 PageStore 控制管线**，不是与主干
完全同构的 CPU 实装。上表没有进一步隔离 allocation/copy/provider 同步与管理 M，不能把 acquireWrite 全部算成管理时间，
也不能把 CPU RAM COW copy 归为跨域 X。

进一步直接核对当前源码和固定 upstream `9a24ae0d8c070884fb013594191002e1a1b39a19`：

```text
当前 preserve：provider.prepareWrite → createDefaultTileData → KisTileData(default)
              → fillWithPixel（4096 个像素）→ provider.transfer → 整页 memcpy
主干复制：duplicateTileData → 预克隆命中，或 KisTileData(copy) → 整页 memcpy
```

因此一个 64×64/4 BPP 的普通 preserve allocation 在用户 scanline 修改前，先写 **16 KiB 默认内容**、再写 **16 KiB source
内容**；8/16 BPP 对应每遍 32/64 KiB。这里说的是源码所需的逻辑写入工作，不是已经实测的 DRAM traffic/带宽。
逐像素 default fill 的必要性已被 source 初始化覆盖，属于可消除的 resident payload 工作；具体 wall 占比还未单独测出。
`defaultMaterializationRequests==0` 只统计 PageStore 语义 default materialization request，**不证明 provider 新写 allocation
没有默认填充**。不能借旧计数掩盖这个额外初始化，也不能将它命名为 GPU/UMA 跨域开销。

## 3. 本轮代码改动：一次发布 shard 目录

`KisPageMetadataCoordinator::configure()` 仍在配置 mutex 内一次构建 shard vector，最后 release-store operational；
hot `shardFor`/`isOperational`/`shardCount` acquire-load 后访问 immutable directory，不再每页重复取 configurationMutex。
只移除了配置目录的全局锁；页面 mutex、revision/claim、writer/read/last-use 检查、PageStore owner gate 均保留。
不允许重配、不允许与 destructor 并发；这不是 RCU 生命周期，也不是 PageStore native reader 已免全局锁。

新增并发测试覆盖两个竞争 configure 仅一个成功、四个 reader 看不到半构建目录、拒绝重配及后续真实 page 访问。
Reference **39**、Foundation **24**、完整 tiled-manager **88** passed。当前代码同样澄清：短 claim 不等待外部 completion，
但取得单个 shard mutex 仍可能等待，不能将其宣传为严格 lock-free。

### 配对结果：没有确认收益

| 桶（N4096/BPP4） | before μs/op | after μs/op | paired median ratio | 探索性 95% 区间 |
|---|---:|---:|---:|---|
| alias K1/H0 | 17.143 | 17.270 | 1.009 | 0.989–1.043 |
| alias K1/H4 | 18.118 | 18.215 | 1.002 | 0.984–1.023 |
| alias K16/H4 | 86.221 | 87.119 | 1.011 | 0.992–1.018 |
| real K1/H0 | 20.045 | 19.740 | 0.983 | 0.966–1.012 |
| real K1/H4 | 20.752 | 21.000 | 1.007 | 0.991–1.026 |
| real K16/H0 | 246.917 | 246.321 | 1.003 | 0.981–1.008 |

ratio 是逐 pair 耗时比的中位数，不等于两列独立中位数相除。六桶区间均跨 1，不能宣称优化达成，也没有正式证据授予 NI。
此结构修正保留，因为它移除了只读目录无须重复取得的全局 gate；**不继续把它当作主要性能瓶颈**。

## 4. 偏差登记与新的执行优先级

| 编号 | 新证据 | 后续约束 |
|---|---|---|
| D3-instrumentation | recorder 关闭仍出现 real K1 binary 偏移 | 冻结诊断 binary/ABI，用相同 harness 交替 library；不把布局/环境偏移归给算法 |
| D3-directory | 六桶移除 config mutex 未确认收益 | 不宣称 lock-free 性能完成，不继续仅靠替换 mutex 名称求收益 |
| D3-write-body | K16 body 明显大于 finish，acquireWrite 是主要子区间 | 下一主线转向 P3/P5 resident write/COW/native guard，不能只缩短 commit |
| D3-default-fill | generic preserve 确有整页 default fill 再 copy，而 default request counter 可为0 | 下一切片加 provider 初始化工作量证据，优先对接 native duplicate/preclone；不将 acquire 全段归给该项 |
| D2-B-small-K | 本轮对照是 D2-B+新诊断 与 D3，不是 D2-A 与 D2-B | 56 的 6%–10% 反证仍保留，不能用新循环/新 binary 的绝对数值回填或宣布已消失 |

下一切片应沿 52 的正式接口推进：同一 canonical owner 下的 resident `CpuWriteIntent → native write guard`、一次 first-write
COW 与 mutation/session 复用；优先消除 prepare 默认填充再复制、通用 request/completion 重复工作，保持 abort/retention/
provider epoch 安全。主干 `duplicateTileData`/预克隆、first/last swap pin 应作为设计对照；不能直接把唯一 backing 裸写
原位而破坏已捕获 root/失败回滚。是否允许原位写仍必须由 owner permit 证明，不能用“当前没有 reader”瞬时判断替代。

进一步分离 acquire 内部 allocation/native copy、协议 M 和 handoff 成本时，采用当前操作级抽样并校准，不把低扰动的整体
E 等同于无扰动的每个采样区间。独立 M/K/X/E、upstream 配对、宽格式与长期 replay/retirement 内存有界性仍按 39 执行。
GPU/UMA 资格仍为 NotMeasured，硬件同域/跨域边界不变；P1–P6 的完整目标不因本轮诊断缩小。
