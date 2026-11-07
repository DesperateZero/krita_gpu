> **历史归档：已退出当前执行入口。** 本文全部状态、计划、类型草图与数字仅描述当时检查点；不再授予当前阶段资格。有效约束与剩余 M6–M8 / BR1 收口任务已统一到 [92](../../../92_br1_m6_m8_execution_baseline.md)。原文与失败证据保留如下。

# BR1 D2 分阶段测量与原子事务起点（2026-09-20）

> 历史归档（2026-09-25）：本文保留原时点的实现、测量和判断，正文“当前/已完成/下一步”不代表现状。当前裁决见 [90](90_br1_m5_baseline_freeze_review_20260925.md)，后续条件路线见 [91](91_br1_m6_to_completion_entry_plan_20260925.md)；[归档索引](../../br1_tuning_20260925/README.md) 保留本篇及证据身份。

本轮落实 52 的定向测量、固定 page-work 和事务起点无 manifest 导出要求，按新证据校准后续优化。
本文冻结 D2-A 版本事实；后续同步 prepared metadata publication 与新版测试/测量见
[56](56_br1_prepared_metadata_publication_20260920.md)，不把本文的发布顺序/热点作为最新实现。
**BR1-PERF 未结清；prepared metadata batch、免全局锁 native guard 与完整 M/K/E 配对仍未完成。**
D1 历史证据保留在 54；本轮版本身份、命令及原始日志见 [实验目录](../../../evidence/br1_d2_20260920/README.md)。

## 1. 实施内容与 API 边界

1. 新增私有、thread-local、owner-filtered opt-in phase recorder，切分 commit/adoption/事务起点/显式 manifest 导出。
   不引入诊断全局锁，不触碰像素 authority 或 lifetime 协议；默认不读时钟、不累计统计，仍有 TLS/分支成本。
2. 新增 52 个固定 N/K/H/bpp/mode 数据桶，验证真实 scanline 修改、整页 alias、known no-op、相同内容但缓存未命中，
   同时检查未写行、相邻页和 retained exact bytes。每项日志记录实际 canonical page work，不以 seed 代替工作量控制。
3. 增加 `KisPageStore::beginCurrentTransaction()`，在同一 owner gate 内捕获当前 immutable root 并建立 transaction
   base retention，不调用 `captureCommittedEpoch().snapshot()/manifest()`。适配层匿名事务使用它；显式历史 base 的
   `beginTransaction(baseEpoch)` 保持原语义，非法显式 epoch 仍拒绝。没有新增可伪造的 current-epoch 裸 capability。

这仍使用现有 PageStore owner mutex；不宣称新 API 已免全局锁。它消除了事务起点 O(N) 清单导出和两次公开调用之间的
capture/retention 窗口。root/epoch 与 transaction ownership 不变，snapshot 导出继续供显式 cold-path 查询使用。
prepared batch 的状态复验/发布次序尚未调整，不能以此宣称 P4 整体完成。

正确性：Reference **33**、Foundation **24**、完整 tiled-manager **88** passed（均含 init/cleanup；88 包含新增 52 桶）。
Reference 新用例覆盖禁用/嵌套 owner 过滤及线程隔离的诊断边界、原子 current-base、新提交后旧 base 仍可读及无 manifest 导出。
其他产品全套/长压没有因此自动取得新版本资格。

## 2. 定向 before/after：复杂度修正有收益

before/after 均带相同诊断代码，正式取值时 recorder 关闭；52 桶各 5 次、每次 256 操作。下表为无 profiler 的操作区间
median，单位 μs/操作，非主干配对，不构成 M 不劣性证明。设置、known-noop warmup、正确性检查与 retained-root release
在区间外且单列。短桶没有达到正式微基准时长要求，本表只用于定位和切片趋势。

| 操作 | N/K/H/BPP | before | after | 耗时比 after/before |
|---|---|---:|---:|---:|
| full-page alias | 64/1/0/4 | 15.457 | 15.007 | 0.971 |
| full-page alias | 1024/1/0/4 | 19.618 | 16.463 | 0.839 |
| full-page alias | 4096/1/0/4 | 32.958 | 17.846 | 0.541 |
| full-page alias，retained | 4096/1/4/4 | 34.121 | 18.882 | 0.553 |
| known no-op | 4096/1/0/4 | 15.129 | 0.659 | 0.044 |
| real partial-page write | 4096/1/0/4 | 36.485 | 20.372 | 0.558 |
| real partial-page write，retained | 4096/1/4/4 | 37.271 | 21.979 | 0.590 |
| real write，K=16 | 4096/16/0/4 | 256.472 | 243.392 | 0.949 |
| real write，宽格式 | 1024/16/4/8 | 241.582 | 246.666 | 1.021 |
| real write，宽格式 | 1024/16/4/16 | 266.549 | 266.610 | 1.000 |

[固定 K 的 N/H 图](../../../evidence/br1_d2_20260920/fixed-n-scaling.svg)。完整 52 桶的 range、sample stddev 与 release 时间见
`analysis.json`；不能只选有收益的桶。宽格式/K=16 的像素访问与控制成本仍在，不能外推 44%–46% 为普遍提升。

独立 profile 在 before 的每个桶每轮均发现一次显式 manifest 导出：N=4096、256 次导出 **1,048,576 entries**；
alias/K=1/H=0 的该阶段累计 wall **3.669 ms**。after 操作区间的这类导出在全部 52 桶均为 **0**。
结构断言证明的是 PageStore 显式清单导出，不是所有内部 tree 路径均 O(1)：稀疏 tree 更新仍随深度变化，dense rebuild
仍有其 N≤4K 条件，其他 clear/extent/history 场景也未据此豁免。

## 3. 原混合 stress：没有可确认的整体收益

seed 12345、8 workers/8 threads、1 BPP，无 profiler 顺序运行，不与构建/其他 benchmark 竞争。固定 seed 不固定交错或
删除页数；before 全部先于 after，非交替、非主干配对。

| 版本 | Qt elapsed（s） | median（s） |
|---|---|---:|
| D2 before（诊断关闭） | 16.010 / 16.177 / 16.048 / 16.275 / 16.250 | 16.177 |
| D2-A after（诊断关闭） | 16.229 / 16.096 / 16.318 / 16.286 / 16.290 | 16.286 |

中位耗时比 **1.0067**；区间重叠，不能判定本切片有整体加速，也没有配对置信证据判定因果回归/不劣性。
这与定向结果并不矛盾：before 的目标 manager 显式 manifest 导出在有扰动 profile 中仅约 **45 ms worker-wall**；
after 仍有约 **30 ms**，主要其余 allocatedPages/clear/history 等调用，不是新 begin 再导出。
它从来不足以解释剩余约 16 s；这次修正是必要的复杂度修正，不是主要 stress 瓶颈的结清。

## 4. 新分段证据及其扰动

after 独立 `BR1_PROFILE + BR1_STAGES` 的 Qt 时长 **18.793 s**，比 plain median 高约 **15.4%**；before profile 为
18.893 s，比对应 plain 高约 **16.8%**。开启细粒度阶段时钟明显扰动运行，不用于 Pass/Fail，不能称“低扰动已证明”。
关闭诊断的 before median 16.177 s 与 D1 的 16.212 s 区间重叠，仅未观察到大的禁用态退化，不证明零开销。

下表是 after profile 的目标 manager 区间累加（跨 worker，不是进程 E）；取值是实际 scope wall/thread CPU，
不是 54 的采样百分比换算。细短区间的时钟读取端点与读取成本会令 CPU 略高于 wall，未做空 scope 扣除，不能据此推导
负锁等待或精确纳秒 self。provider 区间包含锁外调用及重新取得 owner lock，入口 wait 也不是完整锁调度 trace。

| commit 阶段 | wall（s） | thread CPU（s） |
|---|---:|---:|
| proof/input validation | 0.566 | 0.567 |
| default/removal preparation | 1.148 | 1.147 |
| transition preflight | 0.475 | 0.477 |
| epoch prepare | 0.323 | 0.325 |
| root commit | 0.399 | 0.401 |
| metadata apply | 0.652 | 0.652 |
| cleanup | 0.096 | 0.098 |
| history collection | 1.132 | 1.131 |
| provider retirement + commit tail | 1.166 | 1.165 |

图：[commit 分段](../../../evidence/br1_d2_20260920/after-commit_phases.svg)、
[adoption 分段](../../../evidence/br1_d2_20260920/after-adoption_phases.svg)。adoption owner entry wait 为 2.315 s wall/0.641 s CPU，
provider 区间为 2.291/0.974 s，均为并发累加，不能当作可直接从 E 扣掉的等待。
commit 的主要阶段 wall/CPU 接近，继续支持先消除重复控制工作，同时保留局部独占/短发布/有界回收的设计。

本次目标 manager：default materializations **0**、generic write requests **0**、adoptions **1,502,592**、
commits **24,180**；不含临时 source manager。default/removal 阶段处理 1,261,056 个 removal，proof preflight 处理
1,500,800 页，metadata apply 合计 2,761,856 页。零 default payload 不等于零删除 metadata 成本；批量化不能只处理 write proof。

## 5. 偏差存根与下一研究

| 编号 | 预期/实际 | 校准与后续 |
|---|---|---|
| D2-A | 相同 fill 原以为均可当零工作；H=4 的 6 个初版桶实际首次额外 adoption K 页 | 保留 6 fail 原件；setup 的换色挤出单项 uniform cache，现分开 warm known-noop 与 cold identical，后者完整计入版本/提交成本。精确 Uniform/Alias 属性仍待 owner 安全维护，不靠增加无界缓存修饰结果 |
| D2-B | 细阶段计时便于替代采样猜测，但开启后 stress 慢约 15%–17% | 仅作区间定位；对短 adoption 路径下一步使用有界抽样 scope/固定批次和空 scope 校准。禁用态与启用态、CPU/wall、时钟 overhead 单列，不盲目再加密采样 |
| D2-C | 消除 O(N) 事务起点后，大 N 小 K 明显改善；原 stress 未见整体收益 | 不是方向失败：该项在原 workload 占比很小。不能称“整体又快约 45%”，也不能用 stress 无变化否定已消除的 N 放大 |
| D2-D | default payload 已为零，但 default/removal prepare 仍约 1.148 s | 剩余为状态解析/预演等控制工作，不是隐含 GPU 迁移。prepared batch 必须合并语义 removal/default delta 与 write proofs，复用一次验证后的候选状态 |

下一切片仍是 owner-held prepared metadata batch：分别计入 prepare、动态复验、publication、retire/drain，不删校验。
按 33 的 6.1 绑定 owner/transaction/base/page revision/provider epoch，并测试 reader/last-use/abort/reset/同页冲突、重复消费、
整批拒绝和旧 root 完整可读。当前 PageStore mutex 使现有“预演→root→metadata apply”对公开访问不可穿透，但未来 native
reader 不得依赖它；候选 metadata 必须先就绪再让新 root 可见，不能仅缓存 snapshot 后在 root 发布后盲目覆写。
同时推进精确内容属性、history adapter delta、production root/cursor、真实 mutation/permit 与独立 M 基线；本轮不缩小 52 的出口。
