# BR1 当前基线与 M6–M8 收口计划

<a id="native-cpu-baseline"></a>
## 1. 当前基线与剩余工作

已验收的 CPU 产品为 `0fd96f2fa3f2`。它从 `48c89b04f88e` 切换到 native result 协议，完整原型 `d10d8caf4268` 留作同批比较。正式 M6、M7、M8 各有独立出口，Vulkan 产品路径保持默认关闭。[生产交付与适用边界](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/write-unit-accounting/native-result-construction-104/production-integration/REPORT.md)

| 要使用的结论 | 证据与下一步 |
|---|---|
| 当前 CPU 行为与价格 | 生产集成双架共 13,636 项检查通过。固定 H1 暖写 1024 个页结果，P/U/N 分别为 21.526595 / 9.774743 / 10.447100 M 指令。两桶 Fresh 保护结果只用于本次 CPU 产品替代。[联合价格](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/write-unit-accounting/native-result-construction-104/production-integration/JOINT_RESULT.json) · [Fresh 控制](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/write-unit-accounting/native-result-construction-104/production-integration/FRESH_RESULT.json) |
| 当前 M6 任务 | 按 [§6.1](#m6-opportunity-gate) 对独立 Ready exact alternate 的命中、受阻拒绝、安全 Fresh/COW、容量、尾部与固定 M5 保护桶取证。M5 修复对照为 `5173c807c8`；同语义 upstream 单列。产品集成价格不能代替这些比较。[冻结 M5](evidence/br1_m5_repair_20260925/README.md) |
| 仍然适用的业务与共享服务优化 | 查[责任与证据适用范围](README.md#evidence-scope)。投影融合、像素分块、真实储存和终结按当前消费者保留；原业务价格、旧写协议单价各归原用例 |
| 完整后端扩展 | 105 给出 provider、多副本、ImageEpoch、设备布局、异步失败和最终释放的设计。UB01–UB16 实施与能力验收均为 0/16，UB14 包括真实公共消费者迁移。[完整设计](evidence/br1_pagestore_equivalent_pipeline_20261010/v3-minimum-write-rewrite-r0/UNIFIED_BACKEND_DESIGN.md) |

阅读本篇时，§2–§7 给出阶段合同与门禁。涉及旧实现术语时以可观察的语义端点为准，具体所有者与动作按现行源码核对。§8–§14 按业务责任取用；§15–§17 供追溯原批及其门禁依据。旧计划中引用的候选、未完项和价格，需在当前产品重新核实后才进入待办。切换前全文可用 `git show d6062041a5f1:docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md` 还原。

## 2. M6–M8 共同边界

- PageStore/metadata 决定逻辑 generation、可见性与权限；provider 决定真实 allocation、物理 pin/claim；TileData 引用数不授予写权限。每个事实只有一个可写 owner。
- 发布的逻辑版本不可变。复用的是物理 allocation，必须先从旧版本解绑、绑定新身份，再暴露可写字节；不能让两个可读版本同时把同一可变字节当作 exact replica。
- 同一未发布段复用 pending。remove/default/alias/no-op 保持语义操作；完整最终输入直接初始化新 backing，不先填默认再复制。
- logical admission、metadata writer、provider physical claim、read/raw pin、source lifetime、last-use 和 budget reservation 是不同事实，不合成一个“独占”布尔值。
- `Unavailable` 只有未开始工作才允许 fallback；`Failed` 不得通过重放另一条管线处理。证明不足、竞争或预算不足时保留安全 Fresh 路径。
- prepared 对象只承载短寿命候选；不另建 selector、generation ledger、事务终结器或第二份 write set。按相应入口合同前置可失败准备；覆盖现有可见字节的不可逆路径严格要求首字节前全部准备。独立Fresh私有结果仍可按原合同撤销，不把它误套成commit-only；成功、取消、失败和析构各有唯一终点。此区分见§16.174–175，不放宽普通callback的既有预备要求。
- owner gate 内不分配大对象、不等待 I/O/GPU、不执行外部 callback；publication install 的 allocator、rehash、大对象析构必须为零。空余 bucket 不等于已准备 node storage。
- 当前真实 layout ceilings、intrusion ratchet、调用图与所有权清单保持生效。新增 handoff 字段随真实消费者一次引入；不照抄历史 512/904 B 草图放宽已经收紧的热记录。

比较基线分开冻结：本轮修复提交用于 M6–M8 增量收益/回退；固定同义 upstream `9a24ae0d8c` 用于正式 CPU 比较；selector 匹配控制只回答 selector 的因果成本。不同提交、构建参数、fixture、操作端点或库身份不得混用。

**PageStore基础性能优先。** 主线比较PageStore完整替代管线与upstream同语义能力，包含必要adapter/manager接线、版本/历史、预算及最终回收。通用工作量、kernel或调度优化独立记账；仅当前分支少做工作的收益，不能用作PageStore本体效率证据。双方采用相同上层策略后才可归因基础差额；内部copy/generation数量是算法结果，不固定为外部合同。新增能力的必要费用须单列并证明，不能无条件称为正常管理成本。当前证据重分类、对称模型与下一矩阵见[§16.171](#pagestore-equivalent-performance-scope)。

<details>
<summary>旧产品 ed0f229821 的读写定价与当时的优先级（2026-10-12 至 13）</summary>

**读写目标与当前差额（2026-10-12，ed0f229821）。** 统一后同批相对upstream仍多49.060M写指令、3.347M读指令，读写额外52.407M/3.535ms，process额外76.195M/5.936ms。较同批bb62读写少1.065M，仅回收额外指令约1.99%；CPU改善未确认。旧53.451M/3.374ms是前批bb62账，不能跨批相减或称剩余全部必要。[当前报告及互斥账](evidence/br1_pipeline_refactor_20261010/unified-rw-r1/RESULT.md)。

**最高优先级：新版读写协议继续降本。** 产品ed0f229821已完成final/mutable/source/alias/recoverable的原私有结果统一，full/range例外共同exact-ref保护与原释放责任；旧CPU通用writer fallback和封印快照往返删除。真实异步lease、recoverable before和完整快照能力保留。最新[查账与最低成本路径](evidence/br1_pipeline_refactor_20261010/rw-minimum-cost-r0/RESULT.md)将下一完整方向收敛为原operation计划→原私有结果→同一D接受，不能只删除小额proof查询便宣布核心降本。[唯一蓝图§19.25](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-minimum-cost-audit)，不恢复旧协议。

**最新边界补账（2026-10-13，产品未改）。** [48次启动、含失败的报告与机器账](evidence/br1_pipeline_refactor_20261010/rw-boundary-cost-r0/RESULT.md)给出同批普通读写额外52.445M [52.402,52.489]/3.259ms [3.119,3.409]。physical plan的908次申请为896个144B activity节点＋12次账本存储；另128个Fresh activity共同构成1024个write出生节点，最终全部在后台释放。原scope外1408次free精确配对为range1280＋batch/scope128；manager同窗backend外3.229M，最后delivery占1.967M。plan当前责任中收费准备/retag6.805M、native准入2.917M、descriptor往返1.364M；descriptor管理堆申请0，真实physical claim仅0.232M。这支持优先审查逐页收费/活动记录生命期与原结果重复查询，不能全归必要保护或malloc。r2两次69格完成所选管理allocator窗口内的分配/释放配对；不授全进程资源、保留时长或后台CPU闭合。manager CPU全局扰动+11.78%及端点偏差+11.98%未过门；plan只具主格粗探索资格，必要金额/合法净价仍为未知。原始失败、控制格观察失败和upstream坏尾52–55全保留。按[唯一矩阵§19.27](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-boundary-cost-audit)继续完整替代验证，M6/M7/M8 0/3、calibration2/20、默认关闭不变。

**前批余项补账（冻结318过程）。** [原报告](evidence/br1_pipeline_refactor_20261010/rw-residual-cost-r0/RESULT.md)为52.414M/3.193ms；cold768/range1408次管理申请、5096次write管理申请及20384次该allocator预算prepare/settle入口保持该批身份。target未对齐1.061M区间跨0，CPU父子差不合理为负，未授精确机制CPU资格。旧backend外2.882M由新同窗观察深化，不跨批拼账。

**前批统一后责任计价（冻结203过程）。** [原报告](evidence/br1_pipeline_refactor_20261010/rw-minimum-cost-r0/RESULT.md)为52.402M/3.263ms；target21.351M、seal17.965M，ownership查询2.810M，range捕获/解析/释放3.200M。16页实落8个shard，retain/release条件1024→512，1024次slot重解析须有exact binding保护证明才能删。原target余项8.936M、seal余项5.691M及外包络7.403M由最新同批重测深化，不跨批拼账；seal CPU门失败和控制格metadata多一次准备保留。

**读写统一与独立计价（2026-10-12）。** ed0f229821普通同库双架六组10816/0/0，结构门及6工具自测通过。6760源码文件检索、17退役符号归零，生产净−170行；range实增688+16K B且最后物理释放归零。固定8块48过程主格write省1.174M、read增0.109M，完整process省0.944M；CPU节省−0.418125ms [−1.376591,0.299878]，0.75ms门未过。10个CPU控制的非劣证据不足，不等于确认10格回退；原全部业务/资源欠项仍保留。[完整删除/保留/失败/净价报告](evidence/br1_pipeline_refactor_20261010/unified-rw-r1/RESULT.md)。M6/M7/M8 0/3、calibration2/20、默认关闭。

</details>

## 3. M6：可恢复 backing handoff

**读写方案的冻结依据（2026-10-12，bb62）。** [192过程责任定价](evidence/br1_pipeline_refactor_20261010/rw-protocol-audit-r0/README.md)发现输入/物理计划与seal混合表达，1024页触发3968次proof查询，noop先发行两类ID。原[§19.22设计](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-single-protocol-audit)已由§19.24实施统一；其中预算合批和proof进一步合并仍未实施，零D范围保留完整root的方案因扩大保留责任未采用。该旧诊断数量不自动成为新版事件实测。

**必要性证据的边界（bb62冻结）：** [138过程拆分](evidence/br1_pipeline_refactor_20261010/rw-protocol-audit-r0/NECESSITY_RESULT.md)确认768次零delta/128次补debt、1024次无dirty域探查、1984次无Retiring版本访问；ledger交接准备/提交暴露约6.050M/0.401ms，真实物理claim约0.038ms，completion验证约0.035ms。新版没有重新测这些内部桶，不能从新52.407M中按旧暴露直接扣价。A/B/C精确金额仍未知；[§19.23](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-necessity-audit)保持动态保证和必要性证明条件。

只消费**已 Ready、exact identity/layout、独立保活**的 alternate before。可以是已有有效 replica/SSD record/immutable before；首版不把待完成 transfer、未校验内容或“以后可以 replay”当恢复保证。不得临时复制一整页 before 来制造 handoff 命中。

固定顺序：

1. 现有 selector 先利用原metadata shard与binding mutex内的事实拒绝已知writer/pin/lease/last-use；明确不合格即走原Fresh。通过观察后才保活独立before，准备target identity、metadata/index/binding、descriptor、预算与publication输入。预检不占有写权限，拒绝后下一次准备重新观察。
2. 在既有逻辑和物理 gate 内取得 claim，复验 page revision、provider epoch、allocation generation、recovery retention。
3. 排除 source 上的 reader/lease/raw pin、alias、copy/transfer source、swap/preclone、retire、last-use 和其他 operation。
4. 由 owner-only transition 移除旧 G 对 A 的绑定，保持 G 经 alternate before 可解析；消费 provider retag，递增 allocation generation，再暴露 T 的 writable view。
5. seal/commit 走既有统一发布；cancel/abort 退休或重分类 A，G 继续由 alternate before 读取，不把已改写的 A 倒写回 G。

claim 为 move-only、一次消费；prepare 可失败，commit/cancel 是已准备记录的 `noexcept` 终结。旧 binding/cache 的 expected generation 失配必须拒绝并重新解析；真正退休物理 slot 时才释放 stable binding。通用 `AcquireWrite` 仍拒绝复用可见版本的 physical slot，不能加 `allowSameAllocation` 开关绕过证明。

M6 出口：reference oracle 与生产 transition 一致，正反例、两种并发顺序、取消与 ABA/provider epoch 矩阵通过；没有额外 before copy；全部预算与退出终结闭合，并通过[§6.1机会型能力门](#m6-opportunity-gate)。M6 通过只授权 M7，不代表真实stroke默认启用、GPU能力或BR1完成。

## 4. M7：有界 commit-only handoff

入口是 M6 已验收及实际零分配安装资格仍成立。没有 alternate before 时，必须同时满足：

- 旧 current 无外部 retained snapshot/View/active transaction base，或相关 G 已被证明不可达；首版采用保守 O(1) 判定，不扫描 H 个 root 或 N 个页面。
- 检查 handoff、最后保护释放、新 capture 和 root publication 使用同一 epoch admission gate 线性化。capture 先到则拒绝 handoff；fence 先到则新 reader 等待/重试到新 root。
- 全部目标、输入、provider、descriptor、completion、root delta、retirement record、预算与实际存储已准备；全部 logical/physical claims 先成功，才允许任一页写入。
- 首字节后只执行受控同步 kernel、预构造的不可失败安装、预算重分类和 fence release。没有普通 cancel、后页准备失败、I/O/GPU 等待或 callback；`postFirstByteFailures == 0`。

首批消费者仅为完整预检的内部 packed write、clear、fill、resident copy，及证明 unlock 即提交语义的单页 adapter。普通 mutable span、可失败 painter callback、长 session、一般多页事务与异步 GPU 默认保留可取消路径。

**每个 fence 最多 8 页且总 payload 不超过 256 KiB；hold P99 ≤100 μs。** 超限选择已证明的 recoverable/Fresh 路径。调整上限必须基于真实 fence 分布，不能依据平均 memcpy 带宽。第二页冲突不得留下第一页半提交。

M7 专用 transition 在首字节前冻结等价验证，首字节后只能消费已经取得的 claim/cookie/capacity 并安装新 root；不得把“通常不会失败”当成不可失败协议。

## 5. M8：业务 scope、剩余迁移和生命周期

- 一笔 undo transaction 内同页只登记一次 undo 起点；无新增可见性或独立回退边界时，1/10/1000 次 dab/span 重写复用 pending。undo 起点、单操作失败回退点与 exact reader 冻结版本分别建模；每页每段至多一次必要 COW。中间 display/save/exact reader 冻结版本后，按真实 capture/last-use 决定下一段复用或 COW，不能吞掉业务可见性边界。具体 stroke scope 与错误策略见 §9。
- display 为 derived consumer，保护与 undo retention 分账；不得让展示频率增加 canonical history。每页 transient version、pending、in-flight、retirement、cache 均有字节和数量上限。
- 逐入口迁移 brush、H/V/random/wrapped/repeat iterator、packed/planar、clear/default、copy/alias/source、clone/history；全部借用已有 scope/selector/终结协议。
- 旧 wrapper/注册表/回调只有在 caller、生命周期和失败责任迁走后删除；必要 ABI adapter 记录具体理由。已删除接口不再列待办，不为了形式统一再建一个 facade。
- 无 history 的立即写在有资格时 handoff；需要旧值时每页每段至多一次必要 COW；最后 history purge 后恢复资格。full overwrite 保留 before 时直接初始化新页，允许复用时直接写最终输入。
- source borrowed rows 必须同步消费；guard 通过稳定 entry index 访问，不能因容器增长使指针失效。alias 强引用、物理 pin 和非 owning 热指针的职责分别证明。
- 关闭和失败后没有 orphan、未结 reservation、匿名 client、pending journal 或单调增长队列；retirement 拒绝仍保留债务，不能用“任务队列空”冒充 drain 完成。

资源上界保持：current + retained exact history + active pending + in-flight + **有界** retirement slack + **有界** optional cache，不包含进程启动以来所有 generation。每个 resident domain 和统一 SSD 的容量分别受限；logical history 不得永久占满 RAM。

压力响应顺序：收割已完成 last-use/retirement → 丢弃可重建 cache/preclone → 尝试合法 handoff → retained history 转统一 SSD → 有界 backpressure → 明确资源拒绝。禁止预算外分配、丢历史或覆盖旧值；慢 reader、慢 retirement、SSD 耗尽与多文档均要验证进度。

## 6. 验证、性能与删除门

| 维度 | 必须覆盖 |
|---|---|
| 语义/格式 | 1/4/8/16 BPP，full/partial/no-op/default/removal/alias；undo、save、旧 View、active base |
| 并发/失败 | capture 两种次序，native/generic/legacy reader，raw pin/source，swap/preclone/retire/last-use；claim、metadata、descriptor、completion、root、publication 各失败点；第二页冲突、ABA、晚 completion、epoch 变化 |
| 存储准备 | 实际 allocator interposition 有正控制；index tier/碰撞/删除，prepare 并存、cancel/retry、additions/restore；install allocator/rehash/大析构均为零 |
| 资源/终结 | 极小预算、长 history、慢 consumer、swap 压力、持续写、多文档、完整 drain/close；live/reserved/peak 与真实资源核对 |
| 构建身份 | 同一源码提交、arm64/x86_64 完整 CPU/业务矩阵、Vulkan foundation 契约兼容；命令/seed/源码/库/测试 binary 哈希与所有失败日志保留 |
| 结构 | 生成源码绑定调用图，architecture gate 与工具自测；ownership/manifest/census 与真实消费者一致；旧参考/测试代码不作为第二个生产 authority |

结构计数按 operation/transaction 关联 plan/fallback、handoff prepare/commit/cancel、before copy、payload allocation/migration、retirement payload、各类 live/reserved/peak、transient high-water、backpressure、capture wait/hold、首字节前失败与首字节后失败。关闭诊断时不采时钟、不写跨 shard 热原子；统计 reservation 不随历史高水位扫描。 S02 局部执行路径的累计 pin/释放/materialize/拷贝计数按 execution 归并；峰值字段明确为 `maximumPinnedPagesPerExecution`，表示单 execution（直接串行 session 视为一次 execution）内的精确峰值，不累加为并发 segment 峰值。并发性由同时存活的真实 guard 与阻塞冷准备下的进度验证；普通绘画不为跨 execution 峰值增加共享热计数器。此统计边界修订不改变资源硬上限、pin 成对或取消保证。

2026-10-06按用户要求，将M6从固定相对降幅改为下述机会型能力门。原K1/H0/B4下降20%、K16/H0/B4下降30%保留为原形状的研究目标和冻结实验判据，**不再是当前M6退出的硬条件**，也不改成另一组事后挑选的10%/15%门槛。原数据、置信界及失败结论不变；新门必须另行预注册和取证，§16.133的描述性诊断不追认为正式通过。

正式运行前按 39 §5.6–5.9 预注册 required buckets、M 容差、至少 95% 置信度、独立配对/顺序平衡、样本量、停止与失败保留规则。覆盖 N/K/H、冷/暖、native/generic、真实写/COW/default/alias、history/save、压力和完整退出。吞吐直接测 completed work/time；固定-work 延迟、P95/P99 分别取得足量样本，不用少数进程均值冒充尾分位数。

操作时间上限保持：blank/default 与 resident read ≤ upstream **1.2×**；无 history resident write ≤**1.3×**；first-write COW/undo 与两个 stress ≤**1.5×**。这些不是 M 管理开销容差，M 同义不劣性、K/resident E 吞吐/延迟、容量和寿命必须独立过门。CPU 同域 before copy 不计为跨硬件域 X；CPU-only X 的 NotApplicable 不授予 GPU/UMA 资格。

可 handoff 桶证明 before-image copy=0、new payload allocation=0、payload migration=0、retirement payload=0；必要 COW 桶每段每页至多一次。无源更新的 resident hit 不制造 generic heap request/global map/active-lease scan/tile-unlock commit；固定 K 的提交不退回 O(N) rebuild/export/sort，root capture 不扫描全图。

删除必须同时具有静态 caller/模板/虚调用/回调证据、唯一 ownership、runtime census 和行为/失败验证。静态 unreached/test-only/indirect 是候选分类，不是可删除数量。目录移动不计为代码删除；生产删除、测试搬迁与必要正确性新增分别报告。保留 Fresh fallback，不复制旧协议以满足历史命名。

<a id="m6-opportunity-gate"></a>
### 6.1 M6机会型能力门：当前CPU范围

以下各项共同构成CP3出口；当前支持域是resident CpuRam独立exact alternate。未支持恢复域须安全拒绝或在未执行前选择Fresh，不为本门临时增加SSD/GPU producer。CP0仍须核清全部既有required能力，不能借范围说明删去原安全、SSD耗尽或退出要求。

| 判据 | 当前硬条件 | 比较与证据边界 |
|---|---|---|
| 安全与机制 | §2/§3及本节既有语义、并发、故障、真实安装零分配、硬预算、取消和close/drain全部成立；成功首写无额外before copy、新payload、迁移和由此次替换产生的payload retirement | 零复制不等于零管理成本；取消或最终退出的必要退休单列，不伪报为零 |
| 合格命中的局部时间收益 | 同状态K1、K16/H0/B4 Preserve完整首写的延迟减少`1−TH/TF`，各required桶单侧置信下界严格大于0 | 两边均已有两个独立Ready exact副本；同候选、输入、预算、读者、保留关系和完成端点。Fresh只在准备前拒绝handoff，走原安全分支；不删除检查或使用较差复制算法制造分母 |
| 原受保护控制 | 相对固定M5的Fresh及history/forced-COW完成吞吐比下界均≥0.98 | 沿原同义工作量、构建与scope；已有通过只对其冻结源码有效，不与新命中family合并宣称更强置信度 |
| 未命中与拒绝成本 | 自然单副本、已有alternate但被reader/pin/last-use等阻挡的required路径，相对同源码准备前禁用handoff的安全Fresh，完成吞吐比下界≥0.98 | 分别记录尝试、拒绝原因及新增开销；真实资源失败不要求强行完成，按同等拒绝/恢复端点验证，不能用成功吞吐比掩盖丢失工作 |
| 容量与进度 | 同状态下每个成功页避免一份新payload需求，记录每域live/reserved/peak、retirement尾和完整释放；受限预算下旧/新值、失败恢复与进度有证据 | CPU K16/B4为256KiB逻辑payload，物理容量按实际收费；固定容量控制须同时包含一副本Fresh与两副本Fresh。不能由某一路Fresh拒绝声称所有合法回收后Fresh均不可行 |
| 结构与范围 | common metadata record同义实际驻留相对重构前基线降幅≥25%；CP0 required、源码/库身份、结构与适用构建矩阵齐全 | used/reserved/slack均入账；不能用malloc次数、sizeof上界、payload减少或GPU容量替代该分母 |

局部收益门采用“可重复正收益”是机会型能力的最低资格；实际收益是否足以支撑产品投入由§6.2裁决。容量价值独立报告，不抵消CPU局部时间失败、miss回退或安全失败。若将来GPU需要“容量优先、允许一定等待”的策略，应在对应硬件profile中事前冻结产品时间预算，不能拿本CPU门自动授权。

首轮新命中family保持K1/K16×arm64/x86_64共4桶、每桶40个独立配对、顺序平衡，单侧98.75%界使该family覆盖至少95%。本机x86_64实际为Rosetta，必须标识，不外推原生Intel。保留原完整first-write/seal/canonical commit端点，另计setup、before维护、验证和close/drain；合格fixture初始化不能当业务免费来源。追加partial/full-input、1/4次发布和实际自然来源作为机制/业务诊断，不能在看到结果后替换主桶。

每个family在新样本前冻结对照开关及其关闭态校准、有效工作/输出校验、构建与库身份、估计量、bootstrap方法/seed、样本量、排除/失败/停止规则。miss family按实际适用原因预先列出m个桶，固定每桶40对并用单侧`1−0.05/m`界；Fresh/H4沿原各自family。正式样本无profiler/阶段计时扰动，与构建和其他性能实验串行。区间跨界标未通过/证据不足，不扩样到通过；结构计数另测。CPU self、wall、等待与后台分开，inclusive阶段不得相加。

CPU归因先验证每架构时钟的busy/sleep覆盖，process CPU含后台，不能用翻译层漏计的thread CPU推断等待。异构核/缓存/频率等执行条件可改变必要工作单价，与合法可删算法成本分开；CPU查询是瞬时旁证，不作删样、归一化或门禁校正。[§16.139](#m6-execution-variance-delivery)的执行变异和ABBA失败不改变±2%/0.98及family规则，也不证明产品回退；控制分辨率未建立时不授资格、不以同义runner调参或未定价微优化替代正式证据。

<a id="m6-business-value"></a>
### 6.2 业务价值、理论空间与默认策略

M6证明受控机会可安全获益；真实业务启用仍须在既有CP7–CP10/BR1-PERF端点通过。CP0/CP3先清点真实producer与consumer、exact generation、候选/命中/拒绝分布；没有自然正例应报告“来源未建立”，不造副本凑命中，也不为此无限扩大M6范围。正式业务trace的完整模式/尾延迟资格仍归CP7–CP10，阶段顺序不变。

成功转换为`G0:{A,B} → G0:{B}, G1:{A′}`：B只能恢复G0；新G1再次写入须重新证明其alternate。仅在同一未发布段复用pending的多dab，不计作每dab一次handoff。display派生结果、物理alias、未完成transfer或不同generation均不是独立exact before。

同状态、同端点且共同关键路径不变时，用`TF=C+A，TH=C+R+W`作条件预算：A为Fresh专属的必要复制/分配/结算暴露成本，R为handoff专属证明/绑定/结算，W为额外等待或并行损失。30%要求`0.7A≥0.3C+R+W`；算法正确、复杂度降低或引用计数下降不保证此式。CPU/GPU时间重叠时直接比较依赖关键路径，不能机械相加。必要下界、可构造优化及观测热点分别标注，共同路径优化不能全算作handoff独享收益。

真实混合负载按同一统计单位估计`净收益=p·d−(1−p)·e−q`：p为实际命中率，d为命中净节省，e为miss新增成本，q为本策略额外保留/维护alternate的摊销成本；不同形状分层或按实际权重汇总，不相乘无关总体均值。仅基线也会保留的自然副本可令其增量创建成本为零，额外保留寿命、迁移、恢复、驱逐与退出仍须入账。模型用于提出可证伪预测，产品结论以无插桩同义trace的first-dab/input-to-visible P95/P99、pen-up、drain及资源峰值为准。

指定入口默认启用仍受§14和39的原不劣性、绝对交互预算及正式M/K/X/E门约束。局部显著收益不等于业务收益；容量改善不抵消交互超预算。后续优化按真实可删工作及产品敏感度排序，不继续为未校准的20%/30%比值逐容器猜改。

<a id="m6-gpu-prediction"></a>
### 6.3 GPU预测与后继验证边界

当前WriteCoordinator资格限定CpuRam/CpuPointer，Vulkan provider仍是BR3分配/写入/传输/退休未实现的foundation。以下是设计推论，**不是GPU测量或能力通过**；CPU及Rosetta百分比不外推到UMA/dGPU。

| 条件 | 价值预测及必须验证的限制 |
|---|---|
| CPU上传后仍因业务保留G0，GPU也有Ready G0独立页 | 有自然alternate来源；确认相同exact内容/layout、恢复retention和GPU旧last-use完成后，才可能复用GPU页写G1。额外保留CPU副本的代价仍入账 |
| dGPU显存预算紧张 | 避免新增显存payload可能减少驱逐、背压与拒绝；测实际live/reserved/peak和回收后Fresh，不把子分配复用自动写成驱动分配或reserved容量减少 |
| UMA CPU/GPU映射同一allocation | 只有一份字节，不能互为before；零domain-copy不消除COW、cache/order、同步和管理成本 |
| 旧页仍被显示/compute读取 | 复用须拒绝或在合法调度边界等待；Fresh可能允许旧读与新写重叠。owner gate内不得等待GPU，不能用省容量抵消未计入的流水线损失 |
| GPU连续发布或算子仍需旧输入 | alternate代际消费不变；不可原地执行的邻域/别名算子仍需独立源，不能通过retag绕过算法输入寿命。普通异步GPU不取得§4的同步commit-only资格 |

GPU基线须为合理池化/子分配Fresh：resident旧页做必要的本地COW，full overwrite不强制旧像素复制；不默认节省一次PCIe upload/download或一次`vkAllocateMemory`。GPU阶段最小验证轴、关键路径与产品门见[39 §10.1.1](39_virtual_texture_performance_gates.md#handoff-value-gates)，副本独立性见[26 §3.1](26_p0_replica_uma_dgpu_ssd.md#recoverable-backing-handoff)。对代际、alias和last-use约束的判断置信度高；对独显压力场景的收益方向为条件性、中等置信；具体百分比、自然命中率和30%可达性均未测。

## 7. BR1 收口裁决

顺序固定为 **M6 → M7 → M8 → 正式 BR1-PERF**。每个阶段只更新本篇当前表和证据入口，不再追加一串互相覆盖的“当前状态”文档。

只有当前提交的语义/故障/业务生命周期、硬预算/进度、唯一权威/删除证明、M/K/E 性能和源/二进制身份全部一致，才能将 BR1 标为完成，并按 31 开放 BR2 production。归档、M6/M7 完成、foundation 构建或测试总数本身均不授予这一结论。

## 8. Stroke 优先的设计目标与状态归属

本节及后文以当前 `5173c807c87b` 源码为出发点，落实 2026-09-27 的用户优先级。§2–§7 的语义、安全和资格门保持生效。下文接口名称表示拟议职责，不表示代码已存在；优先扩展现有类，禁止据此另建一层 PageStore、selector、write set、缓存权威或事务管理器。

### 8.1 性能裁决顺序

按以下顺序裁决，不用一个加权平均分掩盖首要路径退化：

1. **Stroke：** 输入到可见结果、连续 dab 吞吐与尾延迟、首 dab、抬笔收尾。包含 brush kernel、PageStore、projection/display 与后台维护的干扰；不能只测页写接口。
2. **Undo/redo：** 固定变更页数 K 的恢复与可见结果；历史深度 H、总页数 N 增长时的工作量与资源收敛。
3. **上下文切换：** 切换响应和切换后的首 dab，分别测热缓存和冷准备；不靠提前占满内存或抢占绘画换取更快切换。

任何 correctness、容量或进度门失败均不能用性能抵消。undo 或切换的收益不能补偿 stroke 关键桶的回退。M6 的 H0 handoff microbenchmark 也不能替代真实有 undo 的 stroke。

普通连续绘画的目标热路径为：

```text
job 借用现有 stroke scope
  → 查当前段 entry（命中则跳过首写准备）
  → 短期 physical pin
  → 原有 SIMD/composite kernel
  → 释放 pin、合并 dirty
  → 归还 job borrow，pending 继续保留
```

命中同段 resident pending 时不创建 generation、不再分配 payload、不重新 reserve 同一 backing、不导出 manifest、不 seal/commit、不进入 generic request map、不扫描 provider 全表。物理 pin 和局部身份复验仍保留。

### 8.2 唯一所有者

| 事实 | 唯一 owner 与改法 | 不承担的职责 |
|---|---|---|
| stroke 生命周期、取消意图、job 顺序 | 现有 `KisPainterBasedStrokeStrategy` / stroke scheduler | 不直接修改 replica 或预算 |
| history 起点、结束与结果 | `KisTransactionData` → backend activeHistory → 现有 MementoManager | 不复制一份 stroke page ledger |
| 当前可变段及 page entries | 延长现有 `KisPageMutationSession` 生命周期，继续使用 `KisMutationWriteSet` | 不是新 undo 数据库 |
| job 执行借用 | 上述 session 发出的短寿命 token，绑定 session incarnation/job/range | 不拥有独立 generation 或 before 副本 |
| page writer、generation、冻结版本 | 现有 metadata / write admission / epoch owner | 不以线程 ID 或 TileData 引用数推断权限 |
| exact read selection | epoch owner 的 retained root / overlay snapshot；backend 只保存受保护的选择句柄 | 不缓存未保活 transaction id |
| physical claim、pin、retag | provider / resident binding | 不决定业务可见性 |
| dirty、extent、projection | 现有 changed delta 与派生消费者 | 不成为 canonical 内容来源 |
| budget、retirement | 现有 budget controller / owner ledger / retirement queue | 不由 UI 直接清空或绕过 |
| preset 准备缓存 | 现有 `KisPresetShadowUpdater` 与 `KoResourceCacheInterface` | 不缓存可变 painter、随机源或页面写权限 |

### 8.3 复杂度与复制的正确目标

定义 D 为 dab 数，K 为本笔不同写页数，W 为同时保留的活跃可变页数，F 为真实冻结事件，H 为不同受保护 roots，N 为总页数。

- 无 freeze、独立 operation rollback 或压力分段时，首写 payload 准备随 K 增长；同页反复写不能随 D 重复准备。
- 有 freeze 时，只对冻结后又实际写到的页重新选择 plan，不能将整笔 K 页一起 COW。必要复制按这些真实转折逐页计数；M6/M7 合法命中再减少复制。
- 不承诺带长时间 exact reader 的整笔 stroke 零复制。G0（undo）、G1（若需要单操作回退）、G*（冻结读者）不同，不能由一份可变字节同时表示。
- 活跃 mutable backing 随 W 受限；历史和 sealed overlay 的必要元数据可随 K 增长，但必须计入硬预算。不能声称任意长 stroke 的全部状态 O(1)。
- commit/undo 的元数据工作随 changed pages 与树路径增长；热路径不承担 O(N) 全量索引重建或 O(H) 可达性扫描。

## 9. 第一优先级：跨 dab 复用与可见性边界

### 9.1 将 scope 交给业务，执行权按 job 借用

当前 [stroke 初始化](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:251)已经持有 target device 的 `KisTransaction`；[结束与取消](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:395)分别收口事务。把持久 mutation scope 接到这条既有生命周期，而非每次 `runCpuMutationOperation` 或 iterator 最后一个 client 退出时重建。

具体修改：

1. `KisTransactionData::init()` 在既有 memento/history 成功后，为已迁移的 stroke 取得 backend scope token。token 引用既有事务和 session，不新建 transaction。scope 创建失败必须在开始对应绘画前返回明确结果。
2. `KisPainter`、内部 pixel-operation 入口及 iterator 保存/传递该 token。新内部 overload 可显式接收执行上下文；未迁移的 public ABI 保留现有 standalone operation 语义。
3. stroke job 开始时 `borrowExecution(jobId, ranges, failurePolicy)`，结束时释放 borrow。job 可由另一 worker 接手；线程 ID 只校验本次借用及裸指针使用，不再定义整笔 scope 的身份。
4. 不在共享 PaintDevice 上保存一个可被并发 job 改写的“当前 writer 指针”。难以立即修改参数链的 legacy 调用可用 job 入口安装的临时 TLS 查找 token，但它只是查找桥；owner 仍验证 store、session incarnation、job 和 range。无有效 token 就走旧安全路径。
5. iterator 析构仅释放 guard/borrow；明确的 `freeze`、`finish`、`cancel` 才结束段或事务。保留 standalone batch 的显式 finish，迁移完成后移除 stroke 路径对 `cpuMutationBatches[thread]` 的生命周期依赖。

当前 [session](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:741)和 [beginWrite](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:1806)有线程绑定，不能只延长对象寿命。需要把 session 管理状态与 job 借用分开：

```text
Open → Quiescing → Frozen/Checkpointed → Open（新段按需建立）
Open/Checkpointed → Finishing → Finished
Open/Quiescing/Checkpointed → Cancelling → Cancelled
任何故障 → FailurePending → 唯一取消/失败终结
```

这些是 session/业务状态，不额外复制 page 的 publication 状态。Quiescing 拒绝新 borrow，等待已有 borrow 在 job 边界归还；等待由 scheduler continuation/barrier 表达，不在 UI、image/node 锁或 owner gate 内阻塞。

Quiescing 的界线是 scheduler job 序号 cut：cut 之前已接纳的 job 及其必需后继仍可执行，cut 之后的 job 排队；不能一边拒绝已排队 job 借用，一边等它们结束。请求 checkpoint 的 job 先归还自己的 borrow，再安排 barrier，禁止同步等待自己。finish 先完成现有 `tryDoUpdate(true)` 等异步 producer 的最终输出及其子 jobs，再关闭 admission；cancel 按既有 cancellable/non-cancellable 规则收口，不取消已经进入不可取消的 indirect merge。

### 9.2 并发不能靠整笔全局互斥解决

保留现有 scheduler 对同一 painter 和输入顺序的约束。已声明不相交范围的 jobs 可以并行；有重叠写或读写依赖时遵守原绘画顺序。smudge、clone source、mask 与目标重叠时，依赖包括读取范围，不能只按 target rect 宣称独立。

具体存储改法：

- 继续以现有 `KisMutationWriteSet` 保存活跃段唯一 entry；将会因 vector 增长而移动的可并发访问存储改为有预算的稳定分块 slots。仍保留单页 inline 情况，索引和并发分区按需建立，避免每笔 stroke 预分配一套 64-shard 大对象。
- guard 持有 slot index + slot incarnation；slot 复用递增 incarnation。正在借用时不得搬移/回收对应 entry。现有 logical admission 指向同一 entry，不再建第二份 PageKey→pending 表。
- job 首次绑定范围时按固定 shard/key 顺序取得逻辑权限，预留本批实际需新增的 entry/index storage；像素运算不持有这些锁。
- resident pending 命中通过局部 entry/binding gate 复验；store owner gate 仅用于新 entry、首次准备、冻结或终结。不要让全部并发 job 的每个 span 争用一个 session mutex。
- job range 分块只限制调度与内存，不改变非交换绘画的执行次序。未知 footprint 的第三方调用保留当前 operation 边界，直到声明与失败责任迁移完成。

逻辑 writer reservation 可跨 job 保留，physical pin 不跨 job 保留。结束/取消必须等待所有借出的 guards；guard 晚释放时只完成既定终结，不能在析构中重新选择提交。

### 9.3 明确选择失败保证，避免把重用变成隐式语义变更

首版按消费者区分三种保证，不能由调用方传一个 `allowInPlace` 布尔值自授权限：

| 模式 | 适用范围 | 失败后行为 | pending 复用 |
|---|---|---|---|
| Stroke rollback | 完成错误传播迁移的普通 freehand job；用户取消本来就是取消整笔 | 停止接收本笔新 job，在安全边界取消该 stroke，恢复 G0；明确报告未完成 | 可跨 dab 复用私有段 |
| Operation rollback | 需要“本操作失败但保留之前成功工作”的 callback、未迁移插件 | 只撤销本 operation，保留 G1 | 独立段；必要时 Fresh，不强行跨 operation 复用 |
| Commit-only | §4 列出的受控内部同步 kernel | 首字节前可拒绝，首字节后无普通失败/取消 | 仅满足 M7 全部证明时 handoff |

普通 brush callback 不因属于 stroke 就获得 M7 资格。Stroke rollback 允许 callback 失败，因为所有可变工作仍私有且 G0 可恢复；它不承诺把当前 dab 单独恢复成 G1。未迁移入口继续 Operation rollback，禁止改默认值后悄悄吞掉原保证。

必须先接通错误链再启用 Stroke rollback：`PageStore result → PaintDevice strategy → painter/job 的 failure sink → stroke scheduler 的取消/终结`。[pixel operation 结果](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device_strategies.h:280)保留 typed/bool 供调用者处理单操作回退；不能返回结果的 painter/DataManager 绘画边界负责报告无法处理的失败。不能把每一个 callback false 都自动升级为整笔取消，也不能只丢掉失败 dab 后仍登记成功 undo。具体接线与尚未迁移边界见 [01b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01b_pixel_failure_boundaries.md)及 §15。

在现有 result 类型中区分 `Succeeded`、未执行的 `Unavailable/Borrowed`、首字节前的 `RetryablePressure`、以及 `Failed`；只有未执行者允许选择 fallback。可通过内部带结果的 overload 保留 public ABI，旧 void 入口至少把失败写入所属 stroke 的 sink。`KisTransactionData::endTransaction` 必须在底层真正成功后才标记 finished，`endAndTake/commit` 不得把失败事务加入 undo adapter。没有 session token 的旧调用保持现有兼容保证。

结果入口的具体落点为 `KisTransactionData::tryEndTransaction(...)` / `tryAbortTransaction(...)` 等内部方法，调用者在成功后才执行 undo adapter 登记；不要仅修改返回类型而破坏旧虚函数 ABI。旧 `endTransaction()` 包装它并向已有 failure sink 传播结果，不能清空事务后只写一条 warning。

取消未提交的 stroke 直接走既有 abort/保留 reader 的 Historical 终结协议；新增带结果的业务 abort 入口，避免仅为取消而先完整 commit 再 undo。offset、frame、selection/interstroke 命令仍按原事务顺序恢复。已冻结 reader 保留其旧 exact 内容，不能强行撤销 reader capability。

### 9.4 明确读取意图，显示更新不等于每个 dab seal

| 读取意图 | 选择 | 边界 |
|---|---|---|
| 本 job 的 current/read-after-write | 同一借用下的当前 pending；跨 job 源需有明确依赖和借用 | 不形成外部 immutable snapshot，不允许指针逸出或与写并发 |
| 算法要求的 operation-start source | 本 operation 开始时的 exact 输入 | 自拷贝/重叠源等保留原读取顺序和快照语义；需要冻结就付必要成本，不能替换为实时 read-after-write |
| painter oldData/undo before | transaction base G0 | 整笔固定；不因新 dab 改成上一次 dab |
| projection、save、外部 exact reader | 在 scheduler 安全点捕获冻结 overlay/root | 一致 cut，受 retention 保护；后续写另选 plan |

实现 `checkpointForRead(reason, dirtyKeys)` 为现有 seal/capture 的组合入口：停止相关 scope 的新 borrow，收回本次写 guards，在锁外准备仅 dirty entries 的 proof/overlay 候选，再在短 gate 一次安装并取得 retention。完成后可开新段，但只对再次写到的页做 Fresh/handoff。不得遍历整个 N-page manifest。

首版完整 exact checkpoint 必须纳入 cut 之前全部已完成 job 的变更，包括屏幕外页；这里的 dirty 是“自上次 checkpoint 的 delta”，不是仅 viewport。不能把一次多页操作的一部分新值和另一部分旧值当完整一致快照。只读局部范围的优化需要另有明确受限视图契约，不能冒充整个 image/store 的 exact capture。

不能把尚未 seal 的 pending 伪装成 `CapturedReadView`。独立 sampler 若要看到正在绘画的 current，走明确 checkpoint；不允许直接读另一个 worker 的可变 backing。自拷贝、源目标重叠必须按既有同步快照/顺序语义处理；跨 job 重排不能改变像素结果。

[FreehandStrokeStrategy::tryDoUpdate / issueSetDirtySignals](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/freehand_stroke.cpp:229)已承接异步更新与 dirty 信号。在实际 projection 更新的调度边界统一 checkpoint：

1. dab 完成只累计 dirty rect/page，不立刻为每个 iterator seal。
2. 利用现有 update 节奏安排安全点，freeze 本轮确实需要消费的变更，再发 dirty 更新。不能用降低原有更新频率掩盖 PageStore 成本。
3. 相同 scope/revision 的多个消费者共用同一不可变 checkpoint。合并尚未执行的显示请求时必须合并 dirty，保留最新请求；不能丢 accepted dab，不能丢 save 或用户明确的 exact capture。
4. projection job 完成读取就释放 canonical snapshot；画面显示寿命由既有 projection/display 派生内容承担。仅做重绘、缩放或曝光显示调整，不应反复延长 canonical before 的保活。
5. 慢消费者导致冻结版仍保活时，下一次写付必要 COW 或合法 M6 成本；不因“仅用于显示”覆盖其源。未完成 BR2 的 DisplaySurface 不能作为本节 CPU 收口的依赖。

对没有明确 update barrier 的旧消费者维持原 scope 行为，逐一迁移；不能让它悄悄读到比原实现更旧的 committed G0。最终门验证从输入到实际 canvas 可见的延迟，防止把等待转移给 projection。

### 9.5 处理 indirect、mask、LoD、长 stroke

- **Direct stroke：** canonical target 的现有事务持有 scope；undo G0 不变。
- **Indirect stroke：** scope 绑定 temporary target；结束时按原语义 merge 到 layer。不得把临时内容提前标为 layer authority，或把 pen-up merge 成本排除在测量外。
- **Mask：** strokeDevice、maskDevice、合成 target 各有自己的 store/scope；同一 update barrier 准備相关 checkpoint 后才启动合成。使用现有 strategy/scheduler 协调，不声称多个 store 自动拥有同一个原子 ImageEpoch。
- **LoD/frame：** 每个实际 data manager 的 session/token 独立。clone 的配置可共享，mutable entry 不共享。保存 device offset、frame 与映射契约，变化后禁止旧 token 再借用新目标。
- **Suspend/resume：** 停发 borrow，释放 pins；只有外部需要观察时 checkpoint。恢复复验 scope incarnation 与 context，再续用仍合法的 pending，不能靠线程恰好相同恢复权限。
- **长线/大笔刷：** 以 activePending/metadata 硬预算控制工作窗口 W，不将所有写页永久 pin 在 RAM。扩展现有 seal 为 `sealSubset`：只把冷页的 entries 交给原 publication overlay/proof 存储并归还 writer/slot，其他页继续复用。必要 K-page overlay/history 元数据仍计账；不另建 allTouched write set。
- 单次 batch 大于窗口时分批准备与执行，Operation rollback 必须仍保有完整取消责任，Stroke rollback 可按整体失败保证取消。M7 不能以分批规避“全部 claims 在首字节前就绪”和 8 页/256 KiB 限制。
- 压力下可通过既有 tiles3 swap/provider 降低冷 backing 驻留；统一 SSD 架构未接线的能力不能提前宣称。无法保持硬预算时返回可重试压力或明确拒绝，不能无限延长 dirty/pending 队列。

`sealSubset` 是内部存储检查点，不单独推进对外 read selection；否则会泄漏某个多页 job 的半完成结果。外部完整 checkpoint 将已 staged 的子集与仍活跃的 dirty entries 一起形成一致 cut。这里复用现有私有 write set 与 publication proof 存储的职责，不另加一套可变 overlay。

## 10. 第一优先级：首写决策、发布与后台干扰

### 10.1 将 plan 与证明集中到现有 WriteCoordinator

扩展现有 selector 的输入和一次性准备结果，而非把 M6/M7 判断分别塞进 native/generic/legacy 入口。输入包括 exact base、输入完整性、failure policy、已有 pending、冻结/恢复事实、physical claim 和预算。返回 plan、拒绝/fallback 原因，以及已经取得的 claims/reservations；不能返回一个可长期缓存的“允许原位”布尔值。

决策顺序：

1. no-op/remove/default/alias 等语义操作直接形成 delta，避免分配像素。
2. 同段合法 pending 优先复用，不重复 backing admission；full overwrite 按最终 payload 初始化。
3. 需要新 target 时，尝试已有 independent Ready exact before 支持的 M6；不得复制 before 制造成功。
4. 仅受控完整预检 kernel 尝试 M7。一般 brush、mutable span、异步 paintop 不进入此分支。
5. 其余选择 FreshPayload/FreshDiscard/FreshCow，保留旧内容和取消保证。来源选择按 exact/readiness/capability 与访问成本判断，不能把可读 source 与 authority 混成一个概念。

native 消费直接 guard，generic 消费 request/lease，语义操作消费 delta；所有入口使用同一决策和终结责任。首次写产生的 proof、budget 和实际 provider retag 必须与 reference transition 一致。

### 10.2 逐页对账改为无变化快速路径

当前 [reserveBacking](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1582)会调用 provider domain journal 对账。改为：

- domain/revision 更新仍由现有 pre-admission token 安装；journal 保留验证和观察责任。
- 每个 provider 维护已有序列语义下的发布标记；无变化时不用物化 provider list/change vector。只对实际 dirty provider 排空已登记的 changes，未登记 physical backing 的观察仍保留。
- 首批可用 journal 非空的原子提示，不在 ledger 缓存“已看过的 sequence”。提示为空只等价于本次读取空 journal；有变化或 provider 不支持提示时仍读取并复验原 journal。提示随插入、精确 acknowledge 和 untrack 在同一 journal 锁内发布，不参与预算授权；provider 注册表用受保护的隐式共享快照遍历，provider 调用保持在 owner gate 外。
- 在 job 首次准备/批量准入处处理同一批变更，不在每个 span 重做。sequence 只作为无变化提示，不授权跳过并发变化的复验；prepare 完成前再次检查变化标记，正确处理 wrap 和 provider epoch。
- 多 owner alias 的所有预算接受完成后才能公开 domain 变化。序列不匹配必须回到原安全验证，不接受少记 RAM/SSD 的“最终一致”。

resident pending 重用本来就不需要新的 backing reservation，应先删除重复进入路径，再优化真正首次分配的对账。对账收益单列，不能默认它大于 COW 或 kernel 成本。

### 10.3 收窄整个 backend 的 publication gate

本节中 changed/适配存储的待改代码关系见 [OP1–OP10：operation 资源准备](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#operation-storage-map)：准备覆盖 touched/输出、presence、wrapper/hash 插入与删除回收、extent，再与 publication/cut 协调安装。该指南只细分 MR5/BC9；已实施的触页/输出与 native presence 子范围见指南实施表，完整 adapter 安装、publication/cut 和资源保证仍未闭合，不改变当前阶段资格。

当前 [finishOwnedTransaction](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:947)和 [commitHistory](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1642)在长准备期间持有 publication 写锁。按现有职责重排为：

1. 在短 owner 区间 claim 本次终结，冻结其 delta；将 backend 对外选择切为受保护、不可变的旧 overlay/root 句柄，避免 commit 移除 transaction 后悬空。
2. 释放 backend mutex、publication gate 和其他不必要的上层锁；准备 metadata/root/descriptor、changed tile/extent 更新、memento 槽位和预算转移。需要序列化多个终结时由 existing transaction claim 保证，不让新 capture 等整段准备。
3. 重进短 gate，复验 token/head/revision；按既有 `PreparedMutationCommit` 原子安装 metadata→descriptor→root，并切换 backend 选择句柄。旧捕获继续合法，新捕获观察到新 cut。
4. 锁外分发 dirty delta、释放候选和做退休。UI/node/image/manager 外层若仍覆盖整段准备，必须同步审议收窄；只改核心 owner 锁不计完成。

现有 `for (;;)` 重准备改为单次调用最多 **2 次立即重准备**的初始策略；随后归还 scheduler，在新 head 上重新准备。这个数字是待测调度参数，不是新性能资格。仍然保留 transaction 与输入，不把重试当成功、不重复像素 callback。后台竞争持续时通过已有终结队列公平排队；取消、超时和资源拒绝有明确出口。

这不授权 M7 在首字节后让出或重新准备。M7 先完成本节全部可失败准备，再进入 §4 的短 fence，只消费已取得的候选。

### 10.4 GC 同时限制 H 扫描与版本扫描

本节设计起点是每批 `PageAdmissionBudget=16`、`VersionScanBudget=32` 尚未限制 root 枚举。§15 的 S08 子集现已让后台 collector 使用原 epoch owner 的有界 cursor，整轮共 32 次 root 访问；显式同步全量路径仍保留 `reachablePageVersions`。下列销毁工作、持续热点和跨 store 进度要求继续有效。

具体改为现有 HistoryCollector scan 内的增量候选判定：

1. 每次取最多一个有界版本 slice，为这些候选保留定长/有预算的 live 位图；逐批扫描 protected roots，解析该页版本并标记命中的候选。无需为该页构造覆盖 H 个 roots 的 reachable QSet。
2. root owner 为现有 counted protected-root records 提供可续扫 cursor。链接/游标是同一 root record 上的枚举设施，不是第二套 retention。移除记录时在 owner gate 内更新活跃 cursor，禁止保存跨解锁失效的 QHash iterator；也不一次保活 H 个 root。
3. 以现有活跃 scan 数为上限，给扫描 key 维护短寿命 reachability revision。publication/restore 可能为该 key 引入新的可达候选时使其失效；无关 key 更新不令全部扫描重来。任何无法给出变更 keys 的新保护入口，保守失效有界的活跃 scans。
4. 在 detach 前重新验证该 key 的 reachability revision、page revision、pin/writer/last-use。失效就保留候选并重新扫描；未完成的扫描绝不退休。仅释放保护可留下保守的 false positive，下一轮处理。
5. 初始 `rootVisitBudget=32` **按整个 worker pass 合计**，不按 16 页分别乘 32。同时保留版本预算，补销毁 bytes/nodes 预算和测量；单个不可切分 provider retire 若耗时长，需单独归因/改 provider，不能声称计数上限就是时间上限。

现有进程级 reclaimer 改为按 store 的 round-robin 有界 runnable slices，避免一个长历史独占。优先归还能解除前台预算压力的 ready debt，但每轮仍保证其他 store 进展。不先盲目增加线程数；后台统计关闭时不在每个像素路径打时钟或全局原子。

持续写导致个别 key 扫描反复失效时，只在该 key 后续 job 的 admission 安全点暂缓新写，让回收完成一个有效切面；不持 gate 等待，不扫描全图后才恢复。冷页的扫描不能因另一个热页持续写而饥饿。

### 10.5 退休事件与压力恢复建立确定的唤醒关系

扩展既有 retirement record 的等待原因：physical pin、last-use/completion、provider operation、预算分类转移。记录 provider epoch、allocation generation 和 operation identity，继续由同一 queue 拥有债务。

- 尝试退休发现阻碍时，执行“读状态序列→注册唤醒→复验序列/状态”；阻碍已解除就直接入 ready，避免最后 pin 恰在登记前释放导致丢唤醒。
- last pin 释放、completion 终态和相关预算释放只标记对应记录 ready；通知在 binding/provider 锁外提交，不能持物理锁重入 PageStore owner。
- ready 通知去重，不为每次重复 release 新建队列项；取消/close 注销 waiter，已排队通知依靠 record incarnation 失效，防止 UAF/ABA。
- provider 无可订阅信号时使用有界、退避的维护重试作为兼容路径；不得依赖“下一次用户编辑”或要求 UI 调用 process 才进展。
- budget waiter 由已有 controller 记录 reason/domain/需求和公平排队顺序，释放资源后唤醒可准入请求；waiter 不持 payload pin，不占 worker 忙等。

压力处理沿 §5 顺序，区分首字节前重试与操作后的失败。Foreground stroke 有调度优先，但保留后台服务份额并限定可占预算；不能无限借用 history/retirement 配额。实际 byte 配額仍由既有全局 TileDataStore 与局部 ledger 各自范围承担，跨 store 的 metadata/cache 总额需接到明确的共享额度 owner，不能把相同配置值当作多份免费额度。

首版压力参数使用小预算/多文档 sweep 校准；不在设计中凭空指定几百 MiB 的常驻 stroke/cache 空间。W、waiters、ready/debt 数量和 metadata slots 均按页字节数与当前可用额度推导并设上限。

### 10.6 多 store 共用配额的具体落点

沿用 `KisBackingBudgetController` 的 reservation/commit/release 类型，在进程存储资源的既有 lifetime owner 下放置共享总额实例；store 实例保留局部分类和公平份额。它们分别表达进程物理总额和局部准入，不各自宣称独立的一整份 RAM 配置。BR1 首先覆盖 CPU RAM、metadata/default 与可选 cache；GPU 的跨域计账仍按后续阶段开放。

- `KisTileDataStore` 的物理分配/交换路径是 tile payload 的真实计量点，在该路径接共享 reservation；PageStore ledger 对同一实物只建立局部逻辑归属，不能再次从全局扣除同一 payload。
- 新 backing 的全局物理份额与局部分类别额度在暴露写指针前都取得；后者失败立即归还前者。只持一层 budget gate 完成 token 操作，不嵌套两层锁等待；失败的短暂预留仍计入 reserved，不能超售。
- metadata、默认 backing 与可选准备资源在各自真实 allocator/control block 持有全局 charge，最终析构才归还。clone/多个 store/cache aliases 共用该 control block，不按引用次数重复收费。局部 retained/current 账是逻辑分类，不能简单相加冒充全局物理总量。
- 批量 job 可预取有上限的额度 token，随后按实际分配消费，未用部分在边界归还；它是已计入全局 reserved 的额度，不是预算外线程缓存。命中 pending 不再次取得 token。
- 必要 metadata/default 先于可重建 brush/display cache 准入；保留必要终结记录的空间，防止所有额度被 payload 占满后连取消都无法记录。精确的预留量取自下一批已知需求与有界 retirement slack，不按整笔未知 K 一次预留。
- preset 资源只有能报告实际 owned bytes 或受检验的保守上界才进入新的常驻准备缓存。无法计量的资源仍走有明确 lifetime 的按需路径，不能标成零字节常驻；普通进程 RSS 继续作为账外差额监测。

实现前核对现有 TileDataStore RAM/pool/swap 配置的包含关系，建立唯一总额公式，禁止把父额度与子额度加在一起扩大配置。共享总额只管理预算，不管理页面 generation、事务或 paintop；跨层队列仍由其原 owner 负责。

## 11. 第二优先级：undo/redo 全链路 delta

### 11.1 把已有 changedPages 送到最外层

[MementoManager::restore](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreMementoManager.cpp:259)已有 delta，但 [DataManager::restoreHistory](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:465)仍全量 rebuild。修改现有 restore 返回结果，使成功值同时携带 retained target、changed keys、页存在性前后差异和 default/surface 变更标记；沿 backend 传给 manager，不另算一次全图 diff。

准备阶段构造兼容索引变更：

- 原来有、目标无：移除/失效该 key 的兼容 tile，extent 做 remove。
- 原来无、目标有：准备新增索引节点，extent 做 add；不为未读取页面提前 materialize payload。
- 两边都有且内容版本变：只失效该 key 的 cached identity/binding；页坐标集合不变，不重复 add/remove extent。
- 未变化的 key：保留索引和缓存。

先准备所有可能失败的 index/default/extent 存储，再安装 root 和 manager 的派生选择。若 adapter 改为 lazy cache，reader 按版本复验，不让 root 已成功而索引分配失败留下不可恢复的半状态。旧 tile 指针通过已有 capability 生命周期保活；有活跃 writer 的 undo 必须先经过 scheduler barrier。

default revision、format、特殊 surface 变化保留明确的全量恢复分支，单列性能结果。普通小 delta 不能顺便进入该分支。

### 11.2 extent 与像素边界缓存分别维护

`KisTiledExtentManager` 已提供 add/remove，普通 undo 直接消费 delta；删除最外层 tile 后其 row/column 查找仍可能扫描坐标空洞，不能把“没有遍历 N 个 tile”写成严格 O(K)。若该成本在稀疏画布桶中显著，复用/改造该类的非空坐标索引为有序计数或分块摘要，局部删除更新边界；不要再导出完整页面列表。

tile extent、exactBounds/nonDefaultPixelArea 与 projection invalidation 是不同缓存。现有 [PaintDevice::applyPixelOperation](/Users/apple/krita_gpu/krita/libs/image/kis_paint_device.cc:1884)前后失效不能直接延迟到抬笔，否则中途查询可能读到旧结果。先保留正确性，再按内容 revision/受影响区域合并重复失效；只变像素不变页存在性时，不重做 tile extent。存在同步查询的 job 必须观察自身写后的有效状态。

undo 完成只安排变更区域及必要滤镜依赖范围的 projection 更新；滤镜 halo/全局依赖仍由现有节点负责。用户看到结果的时间、后台历史 purge 与总 drain 分别计时，不能仅测切换 root 的几微秒。

### 11.3 history 生命周期不得反噬 stroke

复用既有 before/after retained roots 和 changedPages，不为加快 undo 常驻全部历史像素。内存压力下利用既有 swap 路径，保住 exact 内容；释放 memento 只投入有界回收，不能在下一笔首 dab 或 UI 线程同步扫完 H。

冷 undo 的页故障按实际变更和显示需求处理，相关元数据 cut 原子可见。预读只能是有预算的 hint，不把用户没撤销到的全历史提前载入 RAM。

## 12. 第三优先级：笔刷与内容上下文切换

### 12.1 沿用已有缓存，区分配置准备与像素内容

源码已存在 [KisPresetShadowUpdater](/Users/apple/krita_gpu/krita/libs/ui/KisPresetShadowUpdater.cpp:78)：设置变化清空当前 cache，延后 1500 ms 触发后台重建；完成以 sequence 拒绝过期结果。[ResourcesSnapshot](/Users/apple/krita_gpu/krita/libs/ui/tool/kis_resources_snapshot.cpp:96)会 clone 并附着合法 cache，[preset](/Users/apple/krita_gpu/krita/libs/image/brushengine/kis_paintop_preset.cpp:625)用 settings sanity cookie 校验。因此改造此机制，不新增一套 brush manager。

把 current-only 准备结果扩展为有字节/entry 上限的缓存，使用现有 resource cache 容器存实际资源。缓存 key 至少包括 preset identity + settings revision/cookie、linked/embedded resource 的内容版本，以及该 preset 声明依赖的 canvas resources 值/版本。色彩空间、profile、LoD 等只加入实际依赖它们的准备项；不能把 whole-image epoch 塞入纯配置缓存 key，让每次 dab 都失效。

不把 UI preset 指针或 preset 名字当内容身份。masking preset 纳入同一依赖树；旧异步完成只能进入其对应 key 的缓存，只有仍匹配当前选择与 sequence 才安装到 `CurrentPaintOpPresetCache`。计入被 stroke snapshot 持有的 cache bytes；LRU 移除索引不等于物理内存已释放。

缓存 immutable 的 brush tip/texture/曲线或允许共享的预计算资源；每笔重建很小的可变 paintop 状态，随机源、spacing accumulator、smudge 状态和目标写 token 不跨 stroke 盲目复用。settings 修改后的 sanity cookie 与依赖变更仍必须使旧结果失效。

### 12.2 区分“切到已有 preset”与“连续编辑设置”

- 切 preset：先按 key 查缓存，命中立即切换资源引用；miss 则在现有 spontaneous-job 机制中尽快启动低优先级准备，不必套用设置拖动的 1500 ms debounce。
- 连续拖动设置：保留合并/延迟机制，只对最终 revision 预热，避免生成大量已过期资源。
- 用户在预热前落笔：使用固定的资源 snapshot；需要冷准备则计入首 dab。不能等 UI 线程持锁阻塞后台任务，也不能使用旧 brush 暂画后补算。
- 缓存命中无需重建 canonical PageStore、清空 tile index、迁移整层内容或清空 undo。`KisPaintopBox` 已按 engine 复用 option widgets，先测其设置读取/信号成本，避免无依据重写 UI。
- 预热可被新版本覆盖/取消；foreground stroke 到来时让出，后台建立的缓存受共享可选缓存额度限制。仅有进程空闲时间并不足以授权无界预热。

### 12.3 内容上下文的失效矩阵

| 变化 | 保留什么 | 必须切换/失效什么 |
|---|---|---|
| 仅 preset 或笔尖大小/不依赖图像的设置 | canonical pages、history、无关配置 cache | 对应 preset 准备项与下一笔 paintop 状态 |
| FG/BG/opacity/composite/selection | 无关资源和页面 residency | 仅声明依赖这些值的准备项；新 snapshot 固定值；selection 的读取视图重取 |
| 切 layer/device | 可共享 immutable preset 资源、原层合法 cache | target/store token、源读取选择、device 相关 interstroke 兼容性 |
| frame/LoD/offset/wrap 变化 | 独立资源与未失效 exact backing | 实际 data manager、坐标映射、目标 identity；旧 scope 不跨映射继续写 |
| color space/profile 或真实内容转换 | 源 exact 版本与必要历史 | 转换目标的 format/layout 与派生缓存；作为显式内容操作分块执行，不能伪装成轻量 preset 切换 |
| undo/redo/外部内容修改 | 纯 preset 缓存、未变更页 | changed pages 的内容相关采样/投影/interstroke 依赖 |
| canvas zoom/显示设置 | canonical 内容与 history | 必要派生显示结果；实际依赖 zoom 的 brush 参数进入新 snapshot |

旧 stroke 已捕获资源 snapshot，UI 切 preset 不能改写它；下一笔使用新 snapshot。若用户操作要求改变目标/frame 或取消当前 stroke，沿 scheduler 既有 finish/cancel/barrier 语义执行。不能为切换方便强制全局 drain 所有后台 GC 或所有文档。

### 12.4 尊重 interstroke 的业务语义

[KisInterstrokeDataTransactionWrapperFactory](/Users/apple/krita_gpu/krita/libs/image/KisInterstrokeDataTransactionWrapperFactory.cpp:115)已判断 continued-data 支持、`isStillCompatible()` 与 factory compatibility，并用 undo 命令保存变化。保留这条路径，扩展实际依赖校验，不用新 preset cache 取代它。

对于 smudge/颜色混合等依赖内容的跨笔状态，必须明确它是有 undo 语义的模型状态还是可重建缓存。前者继续参与原事务；后者按其实际源 PageVersion/区域 revision 失效。不能仅因 preset 相同就复用，也不能每个页面变化都清空所有 brush 资源。

## 13. 文件级实施拆分与迁移出口

§3–§7 的正式阶段依赖不变。先冻结下面的业务契约与验证 harness，再实现/验收 M6、M7；M8 内按 stroke → undo → context 顺序迁移。为 stroke 必需的错误链、后台进度和 publication 依赖可作为前置改动提交，但不得将“前置完成”记为 M8 已完成。

| 改动单元 | 主要现有文件/职责 | 合入条件 |
|---|---|---|
| A：观测与失败契约 | diagnostics、`KisTransactionData`、`kis_transaction.h`、PaintDevice strategy、painter/stroke job | 单操作失败与整笔取消矩阵；成功才登记 undo；各计时端点可归因 |
| B：M6/M7 统一准备 | WriteCoordinator、PageStore、StateMachine、provider/binding、PublicationCoordinator | §3/§4 全部资格；无额外 before copy；只允许指定消费者 |
| C：持久 scope 与 job borrow | backend、PageMutationSession、MutationWriteSet、write admission、iterator scopes | 跨 worker、同页冲突、不相交并发、晚 guard、长 stroke、压力下全部正确 |
| D：真实绘画接线 | `kis_painter_based_stroke_strategy.cpp`、`freehand_stroke.cpp`、`kis_painter.cc`、PaintDevice strategies | 优先 direct/常用 composite，再 indirect、mask、smudge、wrapped、LoD、异步 paintop；每批都有相同输入 replay |
| E：checkpoint 与发布 | backend read selection、seal/capture、epoch/publication、projection 调度入口 | 不读可变 snapshot；不降低显示频率；完整外层锁计时达标 |
| F：压力和维护 | HistoryCollector、EpochReferenceModel、RetirementQueue、ResidentBinding、CompletionRegistry、OwnerLedger | 无新编辑仍能回收；无丢唤醒/ABA；H/多文档与持续写有界进展 |
| G：undo delta | MementoManager、backend restore、DataManager、TiledExtentManager | 固定 K 无全量 export/sort/rebuild；default/extent/sharing 与失败原子性 |
| H：context cache | PresetShadowUpdater、ResourcesSnapshot、preset/settings cache、interstroke factory | warm/cold 分离；依赖准确；旧 completion 拒绝；首 dab 与 stroke 无回退 |

D 与 E 必须组成可安全对外观察的迁移单元，不能先把 pending 留到抬笔、让旧 projection 静默读旧值。C 可以先作为受测能力合入，业务默认启用要等 D/E 与错误链闭合。F 的基础压力保证是启用长寿命 scope 的前提，不因用户把 undo 放第二就后置。逐段映射使用指南 S01–S10/U01–U02/C01–C02/V01；尤其 D 必须联动 `KisTiledDataManager::writePageStoreOperation → refreshPageStorePages/Page`；成功 delta 的 capture/payload 已按 [MR1–MR3](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01d_metadata_refresh_and_pending_visibility.md)拆出，仍须接未 sealed pending 变更、完整 checkpoint 和发布前适配准备，失败回滚的 raw 字节恢复按 MR4 保留。具体代码落点见 [指南 01 的 S03](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01_stroke_scope_and_failure.md)。

逐入口保留 Fresh 安全 fallback，但 fallback 原因必须可诊断。删除旧 thread-owner 注册、重复终结、全量重建调用或 journal 对账路径时，先提供所有 caller/回调迁移、唯一 owner 和实际 trace；不长期保留两套由运行时 flag 随意切换的协议。

## 14. 验收矩阵与停止条件

### 14.1 Stroke 为主的 required workloads

| 桶 | 主要变化轴 | 必须测到的结果 |
|---|---|---|
| 同页短线/密集重叠 dab | 1/10/1000 dab，K=1/16，BPP=1/4/8/16 | pending 重用、copy/allocation/generation/lock 次数，吞吐与输入可见尾延迟 |
| 真实笔刷连续绘画 | opaque/半透明、texture/scatter、smudge/source 读取 | 同 seed/输入像素等价；kernel 和管理时间分开，含 source/mask 成本 |
| 大笔刷与长线 | K 增长、冷/暖、稀疏大坐标、W 达上限 | 受控工作窗口、真实 swap、压力恢复、pen-up 及 drain |
| 显示与 exact consumer | 正常更新频率、慢 projection、save、长旧 View | 必要 COW 随真实冻结后重写增长，无数据竞争/半页快照 |
| 多 painter/异步/mask/indirect/LoD | 不相交与重叠 jobs、worker 迁移、cancel/suspend | 保留输入顺序与并发收益；合成/收尾没有漏算 |
| 长 history 与多文档 | H、后台 purge/save、极小预算 | stroke 的 wait/hold P95/P99，后台公平性、债务与峰值字节 |

先对 `5173c807c87b` 和最终候选运行完全相同产品 replay；正式资格另对 §2 固定 upstream 做同义比较。预注册需包含每桶样本数、最小可检测差异与尾分位数不确定性，不用几次平均值作 P99。

新增 stroke 方案的增量裁决：先证明结构性消除（无 freeze 重写时 per-dab COW/allocate/seal 为零），再证明主要重复 dab 桶的实测收益；其他 required stroke 桶采用预注册的 **2% 不劣性容差**检查 completed throughput 和固定-work latency。P95/P99 单独按同一容差与足量样本检验，证据不足标 Inconclusive。2% 是本次改法的增量防回退要求，不替代 §6/39 的 M/K/E 规则，也不代表预计加速幅度。

不得通过减少实际接受的输入、降低显示更新频率、扩大后台未完成工作或改变像素语义通过门禁。首 dab、steady state、pen-up、完全 drain、峰值内存分别报告；新增缓存启动/预热计入 cold 结果。

### 14.2 Undo 与 context 桶

- Undo：K 固定为 1/16/较大 delta，独立增加 N/H；验证 full manifest export、sort、hash clear 在普通恢复中为零。覆盖删除边界 tile、default 修改、稀疏坐标、cold history、redo、purge、并发 save。stroke 热路径开销不因新增 undo 索引明显增加。
- Context：A→B→A 热切、首次冷 brush、连续改设置、资源版本变更、FG/BG 依赖、切层/frame/LoD、profile 转换、interstroke 兼容/不兼容。分开记录 UI 切换响应、snapshot/准备时间、首 dab、可见结果；与后台预热同时绘画时通过 stroke 防回退门。
- 错误：range/reservation/provider/metadata/root/index/default 准备失败，callback 写到一半失败，晚 guard、旧 completion、缓存 ABA、close、取消期间 freeze。必须证明正确终结，不能只检查没有崩溃。

### 14.3 必须可观测的因果指标

按 stroke/job/segment 关联：pending hit、每页 first-write 与 freeze 原因、Fresh/M6/M7/fallback reason、before-copy bytes、new payload bytes、entry/index 分配、pin 次数、prepared/root 安装、capture wait/hold、重准备次数、dirty 合并、GC root/version visits、retirement ready/pending/wakeup、budget wait/reject、preset cache hit/miss/失效原因。

稳态计数尽量在线程/段局部累计，在边界合并；关闭诊断不采时钟、不加跨 shard 热原子。不能为证明更快而让计数器本身成为新热点。

停止与回退条件：任何像素/版本/失败保证回归立即停止启用该消费者；stroke 关键桶未达增量门时先定位 source/COW/控制/显示/维护分量，不用 undo 或切换收益抵消。阶段状态只在实际证据完成后更新，设计文档、接口合入或局部微基准不代表 BR1 完成。

## 15. 指南实施记录（2026-09-27 起）

> 本节保留各批次的原始判断与索引。涉及当前产品、领取顺序与性能价格时，先核对[§1](#native-cpu-baseline)和[证据适用范围](README.md#evidence-scope)。

M1–M5 的受保护比较基线仍为 `5173c807c87b`。以下是其上的工作树实施，不覆盖 M5 冻结证据，也不授予 M6/M7/M8 或 BR1-PERF 资格。

**S01 首批：带结果的提交与成功登记。** DataManager 新增 `tryCommit`，TransactionData 新增 `tryEndTransaction/isTransactionFinished`，实际提交成功后才完成事务；KisTransaction 两类 `tryCommit` 只在成功时向 undo adapter 转移命令，并新增失败保留所有权的 `tryEndAndTake`。Painter 的两类 endTransaction 失败时保留事务。DataManager 恢复历史遇到前置提交失败就停止；memento 重试保存 newDefaultPixel 时释放上次缓冲。未改变每 dab 的 session/seal 边界。

新增事务测试使用真实未释放 writer 拒绝提交，两次拒绝均不登记 undo、不执行 interstroke end command；释放后重试、重复终结及 undo/redo 验证两页内容。另测 Painter 的拒绝后保留与重试。开发验证记录见 [S01 证据目录](evidence/br1_s01_20260927/README.md)。

本批工作树双架构 CPU/业务矩阵 **2,990 passed，0 failed**，结构门及 6 项工具自测通过，intrusion ratchet 未放宽。实测身份为上述 HEAD 加证据目录保存的 `source.patch`，不是新的已提交/正式资格基线。Vulkan、TSAN、install allocator 和性能未在本批重新取证。

**S01 第二批：主像素事务直接取消。** `KisTiledDataManager::tryAbort` 先准备兼容 hash/extent 存储，复验当前 memento 和 base epoch，成功 abort 后交换存储并恢复开始时保留的 default backing。`KisTransactionData::tryAbortTransaction` 恢复 offset、保存 frame、selection/outline 和 interstroke；SuppressUpdates 仍失效内容缓存。`KisTransaction::tryRevert` 与 Painter 的取消包装在拒绝时保留事务，进入 Cancelling 后禁止改为 commit。主像素取消不创建中间 committed root；辅助 interstroke 仍沿用既有 command 收尾协议。

同工作树双架构 CPU/业务矩阵 **3,026 passed，0 failed**，结构门及 6 项工具自测通过；源码补丁、binary 哈希、22 个进程和首次测试编译失败日志见 [S01 直接取消证据](evidence/br1_s01_abort_20260927/README.md)。这些结果对应第二批 `source.patch`，不覆盖第一批证据，也不代表新的阶段资格。Vulkan、TSAN、install allocator、产品 replay 与性能未重新验证。

**S01 尚未闭合：** 旧 `endAndTake`、忽略 void revert 结果的 caller、未检查初始化准入的旧入口及 parent-attached command 尚未统一迁移；Active 析构 purge 仍可能尝试 commit，其他 Cancelling owner 的析构拒绝仍需接续。第三批已接通 painter-based stroke 的初始化/完成失败与取消重试，第四批补充部分像素故障边界，见下文；仍不覆盖 interstroke 辅助事务的 void command、indirect merge 多设备终结与全部 raw iterator/brush 消费者。直接取消仍在 manager 外层锁内做 O(N) manifest/索引准备，元数据准入和 delta 适配由 S10/S03/S05/U01 接续，不能声称压力下必然取消成功或固定 K 有界。不得据此延长生产 stroke 的 pending 生命周期。S02–S10、U01–U02、C01–C02 及完整 V01 验收继续按指南推进。


**S07 首批：空 journal 对账路径。** `synchronizeBackingDomains` 改为隐式共享 provider 注册表快照，保持所有 provider 调用在 owner gate 外；Tiles3 provider 的 `mayHaveBackingDomainChanges` 只提示 journal 是否可能非空。提示为空时跳过 change vector；不支持提示的 provider 保守返回 true。journal 插入、精确 acknowledge 和 untrack 在原锁内更新提示，原 bytes/revision/登记与 pre-admission 检查保持生效，不增加 owner 已见序列权威。

新增测试覆盖空 journal 跳过、保守 fallback、无预算拒绝、登记前观察保留、过期 acknowledge、新旧 domain 变化和遍历期间注册 provider；原多 owner/stale snapshot/swap 失败用例仍通过。最新累计工作树双架构 CPU/业务 **3,038 passed，0 failed**，结构门与 6 项工具自测通过，ratchet 未放宽。两架构真实 allocator interposition 的正控制有效；1/4/16 个 provider 分别执行 1,024 次无变化对账，均为 **0 allocations / 0 frees**。源码、二进制、探针与矩阵的身份关系见 [S07 证据](evidence/br1_s07_20260927/README.md)。此探针只覆盖 domain sync，不代替 publication install 或 stroke 性能资格。

S07 的 job 批量准入、pending 命中不再 reserve 等剩余关系仍与 S02/S03/S06 联动；本批没有改变每 dab 的 session 边界，没有实现 M6/M7。S01 剩余 caller/故障/进度链、S02–S06/S08–S10、undo/context 及 V01 正式验收继续开放。


**S01 第三批：stroke 终结失败与调度接续。** 主事务先取得 memento，成功后才启动 interstroke；painter-based stroke 准入拒绝后停止绘画。direct 使用 tryEndAndTake，indirect 临时事务使用 tryEnd，成功后才移交 auto-key/undo command。失败进入现有 stroke queue 的取消流程；tryRevert 拒绝时保留 transaction、painters 和 temporary target，成功恢复 frame 内容后再撤销 auto-key。已交付的不可取消 merge 仍保持原调度承诺，其多设备失败链继续开放。

worker failure 保留尚未抬笔的输入句柄，拒绝后续新输入并清除可取消 jobs，保留必需 children；LoD 故障只传播给仍在队列中的 buddy。取消重试按 1→100 ms 退避，scheduler 合并唤醒并复核 deadline；没有新输入也能继续，显式 waitForDone/barrierLock 不依赖 GUI timer。此保活只覆盖已接线的 stroke owner，不授予永久资源拒绝的进度保证，也不替代 S09/S10。

本批同源码双架构 **16 目标 × 2，3,186 passed，0 failed / skipped**，结构门及 6 项工具自测通过，ratchet 未放宽。新增真实 strategy/scheduler 的 direct/indirect、auto-key、live writer 拒绝、取消重试与准入拒绝验证；LoD 已完成 buddy、抬笔后 finish 失败、阻塞/异步 drain 均有用例。源码补丁、image/UI binary 哈希与保留失败记录见 [S01 调度接续证据](evidence/br1_s01_scheduler_20260927/README.md)。UI fixture 固定像素、不运行 brush kernel，不是产品 replay；Vulkan、TSAN、install allocator、stroke/undo/context 性能均未在本批重新取证。**M6/M7/M8 与 BR1-PERF 仍开放，完整实施目标保持进行中。**


**S01 第四批：像素故障边界与可写指针准入。** 新增栈上 job 故障桥，只有显式启用的 cancellable DOSTROKE 接入；typed callback false 保留单操作回退，void painter/DataManager 在不能返回结果处上报首个故障，job 退出后交给原 queue/transaction 取消。覆盖普通 composite、fast copy、fixed/selection、packed/planar/default/clear/copy/trim 等边界；fixed 临时缓冲按作用域释放。KisTileDataWrapper 与 H/V/random 共用 base iterator 改用 tryWriteData，写 intent 成功但 canonical admission 拒绝时不再暴露 cached before-image，兼容 partial copy 同步检查目标指针。

本批源码补丁和 34 个双架构测试进程见 [S01 像素故障证据](evidence/br1_s01_pixel_20260927/README.md)。16 个原有 CPU/业务目标双架构 **3,296 passed，0 failed**；新增完整 iterator 目标每架构 **8 passed / 3 failed**，故全矩阵合计 **3,312 passed / 6 failed，未通过**。结构门及 6 项工具自测通过；已有 reviewed ceiling、tile fields 与 duplicate state 没有提高。DataManager 的类型名出现次数 20→21 在原审议上限 21 内，不能说原始 census 完全未变。

尚未通过的 H/V/random 用例均涉及存活 iterator 期间 clear，再修改 offset/创建新 iterator。撤回本批 DataManager、tile wrapper、base iterator 三文件改动的隔离对照产生相同 66 条断言详情；这不是完整 HEAD-only 基线构建。该批失败要求补齐 clear barrier 与 iterator batch/client 的共同终结并重跑完整矩阵；后续修复见下文。具体待改函数和原样验收入口已列入 [01b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01b_pixel_failure_boundaries.md)。不能提前销毁测试 iterator、丢弃失败样本或用 16 个通过目标代替完整出口。

UI 故障 fixture 运行实际 painter/queue/transaction，但没有 brush paintop/freehand 产品 replay；未重新取得 Vulkan、TSAN、install allocator 或正式性能资格。完整 raw iterator/brush 故障 caller、interstroke/indirect merge 多设备结果及资源进度仍待迁移；没有延长生产 pending 生命周期，M6/M7/M8 与 BR1-PERF 仍未完成，完整实施目标继续进行。


**S03/S04 前置批：存活 iterator 的 clear barrier。** 在原 batch owner 内追踪存活 lease，先拒绝 foreign/non-iterator/终结中的 batch，再撤销本线程 iterator mutation。取消前以非阻塞方式保留旧 backing 的 resident pin 和引用；旧 raw pointer 可继续存活，但不能再发布。新 iterator 不接回旧 batch，旧 scope 再取新页被拒绝；迟到 finish 不删除新的线程槽。history 保留原 transaction/G0，clear 的删除仍走统一 semantic publication。没有另建 page write set，也未延长生产跨 dab pending。

最终累计源码双架构 **17 目标 × 2，3,374 passed，0 failed / skipped**。原 H/V/random clear→offset 三个用例未改调用顺序，两架构均通过；新增 1/4/8/16 BPP、多个 iterator、history/undo/redo、旧 View、晚 raw pointer、新旧 scope 交错、foreign/native batch 拒绝、swap pin 正反向和 bare lease 生命周期验证。结构门及 6 项工具自测通过，原始 ratchet 相对上一累计批次不变，reviewed ceilings 未提高。源码/二进制身份、最终 nonblocking pin 版本与之前运行的区别、结构描述修正及保留的失败日志见 [clear/iterator 证据](evidence/br1_s03_clear_20260927/README.md)。

此批只收口上述已排序 clear 语义；独立 raw Tile/history lease 的登记范围、完整 caller 失败链、局部债务和资源进度仍待接续。Vulkan、TSAN、install allocator、产品 stroke replay 与性能没有重新取证；新增局部同步成本不能视为已通过性能门。指南同步补充 M6 与 legacy tile cache 的 expected generation 复验关系，接续 S06/M6 时不能只实现 provider retag。**M6/M7/M8、其余指南项和 BR1-PERF 继续开放，完整实施目标未完成。**


**S06 前置批：缓存 binding 的物理身份校验。** 在现有 `KisCpuResidentBinding` 的局部 gate 内，read/write/reserve/retire 先核对 expected provider、epoch、slot 与 allocation generation；native read/writer、generic access、同步 copy/transfer 和 retire 统一传入各自 handle 身份。provider 的全部 binding 创建入口给出构造时 tag，不保留无身份校验重载，没有新增逻辑 generation owner。

最终累计源码双架构 **17 目标 × 2，3,494 passed，0 failed / skipped**。新增每架构 60 行错误身份测试，覆盖 1/4/8/16 BPP、5 类身份失配及空闲/read pin/parked writer，证明错误访问、reserve、retire 被拒绝且合法 holder 不受破坏。结构门和 6 项工具自测通过，原始 ratchet 与上一累计批次一致，reviewed ceilings 未提高。源码/二进制身份、增量代码和完整日志见 [S06 binding 证据](evidence/br1_s06_binding_20260927/README.md)。

此批 tag 固定于构造，不包含真实 claim/retag、失配后的重新解析或 legacy tile cache 迁移；错误 token 测试不等于真实 ABA/retag 并发验证。后续代码与证明关系已细化为 [03a 的十个责任点](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md)：cache 消费者、独立 before、物理排斥、预备存储、共同 selector、逻辑转移、终结计账及 M7 admission 必须共同闭合。Vulkan、TSAN、install allocator、实际元数据预算和 stroke 性能未在本批重新取证；**M6/M7/M8 与 BR1-PERF 仍未完成，完整实施目标继续进行。**


**S06 第二批：recoverable 逻辑转移与预备 metadata 安装。** `AcquireRecoverableWrite` 验证现有 Valid alternate B 与旧 authority A 的逻辑条件，移除 G→A、令 G.authority=B，再建立 T；同 allocation 保持 provider/epoch/slot、layout/domain，generation 严格加一。普通 AcquireWrite 仍拒绝可见 slot 复用。`prepareRecoverableWrite` 复用既有 PreparedPublication/arena/index/activity 存储，并在准备阶段计算 Acquire + PrepareWrite；严格 revision 复验后安装 base 与 Writable T，不在 retag 后留下可失败的 PrepareWrite。候选种类、owner/transaction 与一次消费均校验；晚到保护使候选拒绝，不以旧快照覆盖新 reader/pin/last-use。

publish/cancel 继续走原 writer 终结，以 B 为 baseAuthority 释放 before pin；cancel 只产生 T/A 的退休责任，不恢复 G→A、不倒写 A。新增逻辑负例、H0/H128、Prepared base、move/重复消费、owner 先析构、保护变化与局部 metadata 硬预算测试；各 reservation 在终结后归零。该原语只准备逻辑 metadata，独立物理 before、provider claim/retag、descriptor/预算分类/退休存储与 cache 重新解析仍须由生产共同计划接续。

最终累计同源码 **17 目标 × 2，3,952 passed，0 failed / skipped**；每架构新增 229 个 reference case。结构门和 6 项工具自测通过，原始 ratchet 与上一累计 binding 批一致，reviewed ceilings 未提高。两架构真实 allocator 正控制有效：新原语覆盖 1/4/8/16 BPP、1/64/65/129 页、H0/H128 的单页预备安装；原 metadata/descriptor/root、index tier 和 restore additions 探针也重新通过，所有测量 install 区间均 **0 allocations / 0 frees**。准备和延后清理不在零分配声明内，不能把多次单页安装解释为 M7 原子批。完整源码/二进制身份及中间 fixture 失败记录见 [S06 metadata 证据](evidence/br1_s06_metadata_20260927/README.md)。

生产 selector 尚未调用新原语，未发生真实 backing retag，也没有产品 stroke 或 handoff 性能结论。先 claim、后逻辑安装、再不可失败 retag/descriptor/分类消费，最后暴露字节的代码关系已列在 [03a §6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md:76)。Vulkan、TSAN、产品 replay、完整 S10 资源闭环与正式性能仍缺本批证据；**M6/M7/M8、其他指南条目及 BR1-PERF 继续开放，完整实施目标继续进行。**


**S06 第三批：stable binding 的物理 claim / retag。** 完整 provider handle 收敛到现有 `KisCpuResidentBinding`，provider slot index 不再保存第二份 handle。`KisCpuBackingHandoff` 先保留 provider 并准备目标身份，再非阻塞取得 binding、store iterator-read 与 TileData write 排斥；resident、零外部 users、无 memento/preclone、唯一 binding ref 等条件共同排除外部 raw pin、alias、source、swap 和 retire。引用数只排除 lifetime holder，不能代替物理排斥或逻辑准入。

commit 一次更新 handle，将 tile-write 在 iterator 屏障内转为普通 tile-read pin，交回已有 writer reservation；store 屏障在 pixel kernel 前解除。取消未消费 claim 保持旧身份和字节，消费后的候选保留 provider 到 gate 外清理。物理 fixture 新增真实连续两次 retag、旧身份拒绝、reader/writer/alias/source/preclone/swap 竞争、取消/移动、provider lifetime 与完整字节保持；每架构新增 122 个 case。该原语不拥有逻辑 generation、before retention 或预算分类，也没有新增 selector。

最终累计同源码 **17 目标 × 2，4,196 passed，0 failed / skipped**；结构门和 6 项工具自测通过，原始 ratchet 不变，reviewed ceilings 未提高。两架构六个真实 allocator 探针使用同一最终 image dylib；物理 claim/commit、recoverable metadata、原 publication/restore 的每架构 48/32/28 个测量区间均 **0 allocations / 0 frees**，各进程分配正控制有效。这是独立单页、成功且无竞争区间的证据，准备和延后销毁不在声明内，也不是 M7 原子批或端到端性能结论。完整源码/二进制身份、增量补丁、边界与复现命令见 [S06 physical 证据](evidence/br1_s06_physical_20260927/README.md)。

下一段按 [03a §7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md)先准备 OwnerLedger 的旧→新 allocation identity 索引转移、分类差量及失败债务，再联动独立 Ready before、metadata/descriptor/终结存储、旧 cache 从原 version 重新解析和唯一 selector。不得在 retag 后才调用可失败的 registerBacking，不得为固定 K 复制整张 backing 表。当前 primitive 测试没有 PageStore root 或计账链，**生产 M6 尚未接通，M6/M7/M8 与其他指南项、BR1-PERF 继续开放**；Vulkan、TSAN、完整 S10、产品 stroke replay 及正式性能仍待按指南取证。


**S06 第四批：预备计账身份转换与物理原语联动。** `prepareBackingHandoff` 在现有 OwnerLedger 复用分类 claim 与 budget reservation，校验已登记、resident CPU、单一物理 owner 的 Current / ActivePending source，冻结旧/新 key 及 physical domain，并预留分类差量和 CPU RetirementDebt。`commitBackingHandoff` 在逻辑解绑和 provider retag 后一次改登记身份、physical representative 与分类，返回原 writer 终结所需的 debt；取消准备保持旧 key 和 live bytes。普通 class reservation 与 typed handoff wrapper 的消费边界分开，未新建 generation 或分类 owner。

唯一 backing 索引使用可提取的标准哈希节点；安装复用原节点，基数不增，不创建 target placeholder、不复制整表，也不依赖 prepare 时的 iterator。已用真实 provider retag 验证准备后插入 129 个无关 backing 的索引扩容、连续两代、旧身份迟到释放、swap/restore 的 representative、预算/alias/分类拒绝、取消和资源归零。每架构新增 81 个 case；owner/budget 仍须覆盖 reservation 生命周期。

最终累计同源码 **17 目标 × 2，4,358 passed，0 failed / skipped**；结构门和 6 项工具自测通过，原始 ratchet 不变，reviewed ceilings 未提高。ownership inventory 增加一条明确既有 ledger 分类责任的 fact，未增加新 owner。八个最终真实 allocator 探针与矩阵使用同一 image dylib；每架构账本取消/物理＋账本安装 96 个区间，以及原 physical/metadata/publication 的 48/32/28 个区间全部 **0 allocations / 0 frees**，正控制有效。这里仍是独立单页成功区间，不授予 M7 原子批或端到端性能资格。完整身份、保留的 fixture 失败及修正、增量补丁见 [S06 ledger 证据](evidence/br1_s06_ledger_20260927/README.md)。

本批 debt 按 resident CPU 域准备，swap 测试在恢复 CPU 后消费；parked writer 跨域后的债务覆盖、cancel/retirement/close 进度仍须随生产终结链证明。节点索引与 prepared slots 的真实常驻开销继续受 S10 约束，Fresh 登记/查询成本仍待产品性能复验。后续按 [03a §8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md:110)接独立 Ready before、descriptor/metadata/physical/ledger 联合候选、旧 cache 从原 version 重新解析及唯一 selector；**M6 生产路径、M7/M8、其他指南项和 BR1-PERF 仍未完成，完整目标继续进行。**


**S06 读侧后续改动的初次未验收记录（后续验证见下一段）。** `readResidentPageImpl` 在原 retained version 上进行初次尝试加最多两次重解析，冷查找迁入既有 ReadCoordinator，metadata cache 删除新增 expected link 比较。具体主改函数、调用关系、测试范围和后续要求见 [03a §9](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md:123)。这批代码不包含生产 handoff selector 或 legacy cache 迁移。

已留存的 [build-02](evidence/br1_s06_read_rebind_20260927/build-02.log) 完成编译，但初次 [arm64 resident 测试](evidence/br1_s06_read_rebind_20260927/arm64-resident-01.log) 为 **49 passed / 144 failed**；失败分别发生在 probe fixture 初始化和联合 fixture 的 CommitTransaction 调用。这些样例不能用来推断生产重解析正确或错误。前一 ledger 批的 4,358 passed 只覆盖该批冻结源码，不覆盖新增读侧改动。当时的指南整理只更新定位和反向索引，未授予新增代码通过资格；失败日志保留。


**S06 第五批：captured read 有界重解析及联合原语验证。** 失配重解析保持原 captured root/version；只有 InvalidIdentity / Retired 重选，最多两次立即重解析，Busy/NonResident 保留原路径。有无 status 输出指针均使用相同状态判断；热命中不增加 provider lookup。metadata cache 以 replica 和 expected link 对象共同匹配后删除，避免迟到 reader 淘汰新 link；实际 allocation identity 仍由 binding gate 验证。

已修正 probe wrapper 的 capability/域准入转发、prepared-only CommitTransaction 用法，补齐失败退出 pin 清理与 gate 外 deferred cleanup。第二次运行发现 reference fill 提前读取 oldData、暖缓存而绕过注入；改用 generic discard 完整写建立新 current，不读取原 G。原始 49/144、65/128 测试结果及编译失败均保留，没有放宽生产守卫。每架构新增 128 个真实 captured-view 故障注入 case 和 32 个 metadata/physical/ledger/read 联合 case；覆盖冷暖 cache、同/跨 provider B、publish/cancel、旧 G 的字节和新 T 的字节、迟到淘汰与资源归零。

最终累计同源码 **17 目标 × 2，4,678 passed，0 failed / skipped**；结构门、6 项工具自测通过，原始 ratchet 不变，reviewed ceilings 未提高。八个兼容安装探针与矩阵使用同一最终 image dylib，每架构 ledger/physical/metadata/publication 的 96/48/32/28 个独立区间均 **0 allocations / 0 frees**，正控制有效。准备、延后销毁和冷重解析不在零分配声明内；不是 M7 原子批或性能资格。源码/二进制身份、七文件增量和完整失败记录见 [S06 read rebind 证据](evidence/br1_s06_read_rebind_20260927/README.md)。

生产 captured read 已接入重解析，但故障注入 fixture 未运行生产 handoff；真实 retag 的联合 fixture 又不包含 PageStore root/selector 全链路。下一段仍须将 Ready exact 独立 before 的保活、metadata/physical/ledger、descriptor 与终结存储组成唯一 selector 的联合候选，在 claim 前全部准备，再接原 seal/commit/cancel；legacy cache 的身份验证和 raw pin 顺序也须接续。**M6 生产路径、M7/M8、其余指南项和 BR1-PERF 继续开放，完整目标未完成**；本批未重取 Vulkan、TSAN、产品 stroke replay、完整 S10 或正式性能资格。


**S06 第六批：预留债务归属、跨域与普通终结消费。** 联合接线检查发现，原 handoff 把 CPU debt reservation 返回给 caller，而普通 metadata cancellation 又会向 ledger 请求额度；在单页 debt 上限下形成重复准入，换出后的 CPU reservation 也无法直接支付 SSD 退休。现将 reservation 留在原 ledger backing record，`commitBackingHandoff` 返回消费结果，不给 native/generic 各建终结 token；连续合法 pending handoff 复用已有 headroom。

真实 domain admission 同步迁移 headroom 的 reserved 域，aggregate debt 额度不变；其 SSD 部分只保证已计费 payload 的分类转换，不新增 durable payload 额度。实际 swap 新域容量仍由原 admission 保证。利用 sole-owner handoff/representative 的不变量，移动时 O(1) 查找到原 backing，不扫描 aliases/history。普通分类准备按 physical charge 抵扣已有 headroom，未覆盖部分继续正常准入；取消 prepared candidate 保留预留，成功退休消费它，发布到非 pending 分类释放它。共享 aliases 同退只支付一次。

每架构新增 64 个 CPU/SSD 硬额度与 alias 顺序 case，并把 ResidentReadTest 的 32 个联合 retag case 接上 metadata 的真实 prepare/commit/cancel debt callbacks、限制到单页 debt。普通 metadata 取消可以消费已有预留，不再依赖测试手工传回 reservation。完整矩阵为 **17 目标 × 2，4,806 passed，0 failed / skipped**；结构门和 6 项工具自测通过，原始 ratchet 不变，reviewed ceilings 未提高。

八个最终 allocator 探针与矩阵使用同一 image dylib。ledger 每架构 144 个安装/取消区间包含连续两代、索引增长，以及 funded/普通退休混合批；无预留部分额度耗尽时拒绝，解除压力后通过，完整退休后 live/reserved 归零。兼容 physical/metadata/publication 各 48/32/28 区间也通过，所有测量区间 **0 allocations / 0 frees**，正控制有效。prepare、域迁移、延后销毁不在零分配声明内，也不是 M7 原子批或端到端性能资格。完整身份、增量与复现命令见 [S06 terminal 证据](evidence/br1_s06_terminal_20260927/README.md)，代码关系见 [03a §10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md)。

此批修复了联合候选依赖的债务终结，不等于生产 selector 已接通。下一段仍需独立 Ready exact before 保活、metadata/physical/ledger/descriptor 与实际终结存储共同准备，以及 legacy cache 身份迁移。账本新增 reservation 字段及 prepared credit 索引/数组仍须纳入 S10 的完整元数据预算，Fresh/stroke 性能仍待实测。**M6/M7/M8、其余指南项及 BR1-PERF 继续开放，完整目标未完成**；没有新增 Vulkan、TSAN、全局 S10 或产品 replay/正式性能资格。


**S06 第七批：native/generic 共同生产计划的 CPU recoverable 接线。** `prepareWriteBaseLocked` 从已有 exact base 快照提取 CPU alternate 候选；`prepareWritePlanLocked` 共同完成 B 的 resident-only 保活、physical target、metadata、ledger、descriptor 与终结存储准备。唯一 selector 在这些条件满足后选择 RecoverableHandoff；claim 后严格安装逻辑转移，紧接 retag、计账及 descriptor 消费，之后才暴露 T。native 使用原 session page/guard，generic 使用原 pending request/lease；提交、取消、abort 和 undo/redo 继续走原终结链。discard 无最终输入仍填 surface default，完整最终输入直接写入。没有新增 before copy 或第二份 generation/write set/终结 token。

初始导入接口可登记调用者已准备的 exact alternates，仅用于 operational 前 manifest。共同计划当前只接受已驻留 CPU B，未增加副本生产、SSD/archive 恢复或 swap-in。Tiles3 注册与 claim 使用短 admission gate：不同 owner 登记后保守拒绝 handoff，claim 期间拒绝新 owner 注册并允许释放后重试；普通 provider 访问不持该 gate。此规则弥补单一 Store 的 ledger 与 TileData refs 无法证明跨 owner 独占的问题，不宣称解决跨 Store 共享 handle 的完整退休寿命。

新增每架构 164 个真实 PageStore 场景及 2 个物理注册次序场景；同源码 **17 目标 × 2 架构，5,138 passed，0 failed / skipped**。结构门为 1,522 indexed APIs / 14,985 reverse-call edges、22 ownership facts、16 census groups、21 manifest entries、19 external intrusion files；6 项工具自测通过，原 ratchet 未放宽。四类独立 allocator 探针在两架构均有有效正控制，ledger/physical/metadata/legacy 每架构分别为 144/48/32/28 个零分配与零释放区间。**这些探针尚未覆盖整个共同生产安装区间。** 源码补丁、库/测试身份、失败日志和九文件增量审查见 [S06 生产接线证据](evidence/br1_s06_production_20260927/README.md)；修改责任到代码与测试的关系见 [03a §11](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md:149)。

**M6 仍未闭合：** legacy cache 迁移、整个生产安装区间的零分配资格、各准备失败点与 epoch/晚 completion/并发双次序、S09/S10 压力及退出进度继续补齐；非驻留/SSD/archive before 尚未接入。初版 provider 多 owner 规则与首候选策略仍保守。未新增 Fresh 2% 回退、真实 stroke/first-dab/pen-up、Vulkan、TSAN 或正式 BR1-PERF 资格。M7、M8 及完整实施目标保持进行中，不以测试总数或生产入口接通宣告阶段完成。


**S06 第八批：生产共同安装区间的直接观测与并发验证。** native/generic 传入其既有诊断 timer；在 owner gate 外提供 prepare/prepared/cleanup 观测，在 gate 内界定 physical claim 前至 metadata、retag、ledger、descriptor 消费后的安装区间。没有 handoff 候选的 Fresh 不进入新增阶段，关闭诊断不新增计时、分配或热原子；这不替代实际吞吐回退测量。

新增每架构 144 个真实 PageStore 并发场景，覆盖两种访问载体和 1/4/8/16 BPP：准备后与安装后的 native/generic reader、已释放 reader 导致的 revision 变化、pending last-use、swap、provider owner 注册、root capture 和 B reader；另测 ledger 准备前的 swap。观察到 class claim 准备后会拒绝 source domain move，准备前移出 RAM 则安全选择 Fresh；安装后的 G 仍从 B 读取。首轮 fixture 对 swap 次序的错误断言及修正日志原样保留。

同源码 **17 目标 × 2 架构，5,426 passed，0 failed / skipped**；结构门为 1,522 APIs / 15,075 call edges，22 ownership facts / 16 census groups / 21 manifest entries / 19 intrusion files，6 项工具自测通过，原 ratchet 未放宽。直接 allocator 探针调用真实生产入口，每架构 480 组配置、**31,080 个区间**：成功、physical claim 拒绝与 metadata revision 竞争各 10,360，全部零 allocations/bytes/frees，正控制有效。覆盖五条写入路线、两种终结及 1/64/65/129 页；probe 与矩阵使用同一 image 库。区间不含 fallible preparation、像素 kernel、adapter 返回、seal/publication 或 deferred cleanup，不宣称整笔写入零成本。源码、二进制、增量审查和失败记录见 [S06 生产安装证据](evidence/br1_s06_install_20260927/README.md)，修改关系见 [03a §12](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md:165)。

legacy cache 的 lifetime/raw consumer 已审查，**尚未迁移**：长期 TileData 引用仍保守排斥 handoff；不能只放宽 refs/users，也不能用每个 manager cache 永久保留整个 root 来替代身份与 detached tile 寿命。M6 的其余准备故障、epoch/晚 completion 全矩阵、S09/S10 压力与退出进度继续开放；M7、M8、undo/context 与真实 stroke 性能继续实施。本批没有新增 Vulkan、TSAN、Fresh 2% 回退或正式 BR1-PERF 资格。


**S06.3 接口草案的初次文档核对（后续接线见下一段）。** 当时工作树在 `KisTilePageStoreBridge` 增加可复用缓存虚函数和五参数 `acquireTile`，provider 增加读/写缓存工厂声明，binding 增加私有 `readIdentity`。provider 工厂尚无定义，backend override 仍为四参数，KisTile 和 manager 仍使用原 ready/raw-cache 路径；声明与实现尚未闭合。该次只进行文档和源码关系核对，没有编译、运行或性能结论；5,426 passed 仍仅属于第八批冻结源码。具体待改代码段、pin/存储寿命、exact/G0 与 detached 边界和分批顺序见 [03b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03b_legacy_cache_migration.md)。长期 TileData 引用保护继续保留，不能为了命中 handoff 提前放宽 refs/users；M6/M7/M8 和 BR1-PERF 资格不变。


**S06 第九批：legacy canonical 缓存身份与短 pin。** provider 从有效 native guard / generic read lease 签发紧凑 expected cache，native 同时核对所属 provider 的实际 binding。外层暖读在 binding gate 验证并取 pin，nested lock 复用，最后 unlock 归还 pin 但保留缓存存储；闲置 candidate 不持 root 或 RAM pin。manager refresh 复用闲置对象并在转移前清 ready；独立写入从有效 writer 预备未来缓存，原 finish 成功后移交，bulk caller 不强制分配缓存。当前声明、定义、override 与真实 caller 已接通。

身份失配拒绝，Busy/资源不可用不改读 current。Retired 关闭的原 binding 不再复用，wrapper 仍拥有的 TileData/COW bytes 可继续作 immutable 旧值读取；detach/dead 清 bridge，已有指针及 clear barrier pin 保持至原 unlock。此保护仍依赖 TileData 强引用。**iterator/batch 的 Reserved writer 尚未迁到新 cache，仍走原 raw/TileData 路径；必须随后接原 mutation borrow，再完成原 exact 选择重解析、idle 引用与全部 raw consumer 迁移。** 不能为此放宽 refs/users 或 binding 读写排斥；最后 pin 后自主退休和实际物理收费继续由 S09/S10 闭合。

新增每架构 16 个 manager case 和 12 个 physical cache case；最终同源码 **17 目标 × 2 架构，5,482 passed，0 failed / skipped**。结构门为 1,536 APIs / 15,156 edges、22 ownership facts / 16 census groups / 21 manifest / 19 intrusion，6 项工具自测通过；kis_tile.cc 标识符计数 10→9，其余 ratchet 字段不变，reviewed ceilings 未提高。manager 验证暖读无新 request/capture、swap、嵌套、独立写后读、detach、实际 hash 替换和 purge 后旧值；physical fixture 验证 cache 复用、pin 排斥、Busy、retag/retire/revoke。

两架构暖读 allocator 探针各有 96 个区间、98,304 次外层读和 196,608 次含嵌套 read lock，**allocations/bytes/frees 全零**；四种 BPP、初始读/独立写后读/refresh 后读均覆盖，正控制为 4。联合生产 install 也在同一最终 image dylib 重新通过，每架构 31,080 个零分配/零释放区间，成功及两类竞争各 10,360。暖读测量不含缓存初建、写入/refresh、swap-in、发布或销毁；联合安装仍不含准备、像素 kernel、seal/root 或 deferred cleanup。这些不是 stroke 时间、吞吐或 M7 原子批资格。

源码/二进制身份、增量补丁、完整矩阵、probe 与保留的编译/fixture 失败见 [S06 legacy identity 证据](evidence/br1_s06_legacy_identity_20260927/README.md)，逐段关系见 [03b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03b_legacy_cache_migration.md)。**M6/M7/M8、其余指南项和 BR1-PERF 继续开放，完整实施目标未完成。** 本批未新增 Fresh 2% 回退、真实 stroke/first-dab/pen-up、Vulkan、TSAN 或完整 S09/S10 资格。

**S09 通知原语的初次文档核对（后续接线见下一段）。** 当时工作树新增 `KisPageReadinessSubscription/Signal` 和 `CompletionRegistry::watchTerminal`，并注册构建源文件；binding、ledger、retirement queue 与 close 尚未消费这条通知链。原 pin 测试仍在释放后手动 process，未证明无新编辑时的自主进度。该次只核对文档与源码关系，没有新增编译、运行或性能结论；5,482 passed 仅属于上段冻结源码。待改函数、原 operation 绑定、外层锁、弱寿命、去重/晚通知、close、无信号退避和 S10 计账见 [S09 修改目录 R1–R10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md)。

**S09 首批：CPU pin/completion 的退休事件消费。** binding 在同一 gate 内检查 expected identity 与 reader/writer 并登记冷订阅；最后 reader 或真正释放 writer 派发通知，Reserved writer 的 unpin 仍保留阻碍。Handoff 状态拒绝订阅，安装区间不引入通知。registry 将已 terminal 返回为 Ready，Pending 则登记；queue 经 ledger 的原 operation→ticket 订阅，仍在原终结协议复验成功后释放实际 backing charge，Pending operation 不重复 dispatch。

queue 使用稳定 list 节点与每次登记独立的弱等待身份，事件 O(1) 将对应 pending 移入 ready，沿原有最多 32 条的 pass 执行。producer 回调只取得临时寿命并派发，实际 queue/owner 复验在既有 reclaimer 运行，不持生产者的 provider gate。休眠订阅不保活 owner；派发只从非零引用取得 lease，queue 销毁先使弱上下文失效。process/close 注销旧身份；close 拒绝后重挂，登记期间的早到通知仍保留，已接管记录不被晚回调复活。`waitForIdle` 纳入已派发通知，但不等于 debt drained。

每架构新增 42 个 case：registry 9、physical readiness 24、CPU mutation 9 个增量，覆盖注册/terminal 竞争、move/reset、已派发回调、reader/Active/Reserved/revoke、登记前释放、延迟 completion、close 拒绝重挂与直接 owner 析构。实际 PageStore 用例在释放 native pin 或 generic provider lease 后不再编辑、不手动 process，自动清空退休债务；延迟 completion 不增加原 provider retire 次数。

最终同源码 **17 目标 × 2 架构，5,566 passed，0 failed / skipped**。结构门为 1,557 APIs / 15,364 edges、22 ownership facts / 16 census groups / 21 manifest / 19 intrusion，6 项工具自测通过，ratchet 完全不变，reviewed ceilings 未提高。两架构暖读探针各 96 区间、98,304 次外层读；联合生产 install 各 31,080 区间，成功与两类竞争各 10,360；所有测量区间 allocations/bytes/frees 为零，正控制有效，并与矩阵使用同一最终 image dylib。等待对象准备、事件派发与退休不在这些零分配区间内；原暖读和 install 的测量排除范围保持不变，不外推为 stroke 性能。

源码/二进制身份、15 文件增量、完整矩阵、probe 与编译/调用图失败日志见 [S09 retirement wakeup 证据](evidence/br1_s09_retirement_wakeup_20260927/README.md)，接线与剩余关系见 [04a](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md)。**完整 S09 仍未闭合：** 首批冻结时仅接已准入 Debt 且允许后台退休的事件路径；无信号/反复瞬时拒绝的退避、原分类/orphan 准入进度、完整上游 last-use acknowledge、S10 可准入等待者和全部通知元数据的硬预算继续实施。取消后的空 completion signal 仍可能保留到 terminal，冷分配故障与更多退出交错尚需补证。本批不新增 Vulkan、TSAN、Fresh 2% 回退、产品 stroke replay 或 BR1-PERF 资格；M6/M7/M8 与完整实施目标保持开放。


**S09 第二批：无信号的有界延迟维护与退出准入。** 原回收 executor 增加惰性 deadline monitor，计时不占绘画或回收 worker、不依赖 GUI event loop；可移动句柄取消实际排队节点，已派发回调仍由弱 incarnation 拒绝。原 queue 内的 event pending、retry pending、ready 和 active batch 分区共同拥有原记录，不增加债务权威。每 queue 合并一个 deadline，1→2→4…→100 ms 退避，每 wake 最多移入 32 条；失败追加到队尾。已订阅的 operation 继续等待原 completion，不用 timer 重派发。

原分类的延迟尝试仍先取得 Debt 准入；orphan 只保留原 reservation，在合法 footprint 覆盖时才允许后台 provider 调用。成功终态先归还实际 charge/orphan reservation，再释放 worker owner lease；通知或暂时 idle 均不归还债务。缺失 reservation 或不可恢复额度不因重试而变成合法，完整资源恢复仍由 S10 闭合。

close 先在通知 gate 关闭新派发，再取消等待身份/deadline 并等待即时通知；producer 提前原子记住早到事件，close 拒绝后重新调度复验。facade 析构显式停止自动唤醒/延迟续排，防止慢批次与到期通知连续保活 owner；已 ready 的有限工作和现有 capability 原寿命保留，不在析构等待 provider。统计区分即时 worker、未来 deadline 与实际债务。

每架构增加 11 个 case，覆盖 deadline move/reset 和真实捕获回收、129 页 × 四种 BPP 的持续拒绝/退避/跨 store 进度、无信号 pin、orphan 延迟终态、close 拒绝恢复/接管、休眠及活动批次/已到期通知下的直接析构。兼容显式 process 的准确预算用不支持后台退休的真实 provider 能力验证；自动路径解除拒绝后不再编辑、不手动 process。先前完整矩阵 5,586 passed 及第一版探针作为中间身份保留；退出补强后重新冻结并验证如下结果。

最终同源码 **17 目标 × 2 架构，5,588 passed，0 failed / skipped**。结构门为 1,574 APIs / 15,457 edges、22 ownership facts / 16 census groups / 21 manifest / 19 intrusion；6 项工具自测通过，原 ratchet 完全不变，ceilings 未提高。两架构暖读各 96 个区间、98,304 次外层读；共同生产安装各 31,080 个区间，成功及两类竞争各 10,360；全部 allocations/bytes/frees 为零，正控制有效，且与最终矩阵共用同一 image dylib。等待对象、计时、通知和退休不在测量区间中；原准备/kernel/seal/root/deferred cleanup 排除范围不变，不外推为真实 stroke 吞吐或延迟资格。

最终源码/库/测试身份、中间记录、八文件手工增量及生成审计更新见 [S09 retirement retry 证据](evidence/br1_s09_retirement_retry_20260927/README.md)，函数→联动→验收对应见 [04a §8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md)。**完整 S09/S10 仍开放：** 上游 last-use acknowledge、可准入预算等待者、取消后空 completion signal、节点/订阅/deadline 的硬计账和冷分配故障，以及更多压力/退出交错仍须实施。未新增 Vulkan、TSAN、Fresh 2% 回退、产品 stroke replay 或 BR1-PERF 资格；M6/M7/M8、undo/context 与完整实施目标继续开放。


**S08 首批：原 root owner 内的有界可达性枚举。** epoch root records 增加保护枚举链接，原 current/retained count/transaction base count 继续拥有保护事实；最多 16 个固定 value cursors，不复制 H 个 roots、不保存跨锁 QHash iterator。开始时先记 current 完整版本，之后只续扫原有限边界；最后保护释放在同一 epoch gate 调整游标，再允许延后擦除。commit/restore 只比较活跃 scan key 的前后完整身份，使改变的 key 失效，异页发布不迫使全部重启；defaultPixelRevision 与 generation 一同参与比较。

原 collector 每页最多 32 个候选及 live 位图，整个 pass 共 32 次 root 访问，包含每组开始的 current；最多 16 个页面分享额度。未完成/失效绝不 detach，完成后仍持 store owner gate 重读 exact candidate 的 Historical、pin/last-use 等 metadata，再走原 owner transition；物理退休保留原锁外队列。退出终结原游标，冷统计报告候选组 refresh、root visits、单轮最大值与失效重启。

新增每架构 31 个 case，覆盖 root 移除/实际擦除、cookie 复用/晚取消、同页 commit/restore/default revision、8 页共享上限、四种 BPP 下实际半扫时同页/异页发布与旧 View 内容、保护释放后 payload 收敛。默认值夹具首次误用普通 replica proof 的失败日志保留，修正为合法 surface metadata change 后重跑；未放松身份判断。

最终同源码 **17 目标 × 2 架构，5,650 passed，0 failed/skipped**。结构门 1,580 APIs / 15,610 edges / 15 callbacks、21 manifest / 22 ownership / 16 census / 19 intrusion；6 项工具自测通过，ratchet 不变。两架构各完成 72 个 root/cursor 探针区间、28 个原安装/index 区间、96 个暖读区间及 31,080 个共同 handoff 安装区间；allocations/bytes/frees 全零，正控制有效，全部与矩阵使用同一 image dylib。新增 root 测量覆盖 16 活跃游标下的 commit/restore，准备与完整销毁在区间外；其他探针的原排除范围不变，不外推为 stroke 耗时资格。

逐段改动→函数→验收见 [04 / G1–G7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04_reclamation_and_budgets.md)，完整身份、九文件增量、中间失败及最终矩阵见 [S08 root slices 证据](evidence/br1_s08_root_slices_20260927/README.md)。**完整 S08 仍开放：** 同 key 持续发布仍可反复失效，尚需 job admission 安全点进度控制；每组候选仍可重走 H 个 roots，尚未证明总吞吐、销毁 bytes/nodes 预算、锁占用或多 store 压力公平性。新增 scan/queue 元数据的实际硬预算及冷分配故障与 S10 联动。未新增 Fresh 2% 回退、真实 stroke、Vulkan、TSAN 或正式 BR1-PERF 资格；S09/S10、M6/M7/M8、undo/context 与完整实施目标继续开放。


本目录的后续实施已按 15 个 ID 补充 [待改代码段与实施入口](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/NEXT_EDITS.md)，每项明确已有实现、剩余改动、联动终点及完成判据。该索引只细化 §8–§14 与主题指南的代码关系，不新增阶段资格。


**S10 首批：局部预算等待者、实际 grant 与原退休队列。** reclaimer 的原 monitor 增加冷准备可复用通知节点，生产者归还额度只 splice/signal，不在安装区间创建任务、执行 callback 或析构捕获。ready 通知与到期 deadline 轮转，每 controller 合并一个原 worker 作业。budget controller 最多 32 个 Waiting+Granted，登记时准备原 reservation slot/free-list；正 per-domain 需求与净 aggregate/SSD 增长沿用同一计算，超过空载容量的需求拒绝登记。

后台按 FIFO 给原 slot 授予真实 reserved 额度，再在 budget/lifetime gates 外通知；重叠的小请求或普通同步 reserve 不能绕过早到的大需求，不相关资源可继续。waiter take 一次转移 reservation，取消归还空/已授 slot；controller 析构使剩余 handle 失效，等待 context 不保活 store。原 ledger 投影真实 physical/class 变化，原 queue 仍独占退休记录；grant 到达后复验 exact identity、物理域、alias/class claim，消费后才调用 provider。失配归还重试，orphan 仍只依赖原 reservation；close/stop 注销等待身份并拒绝晚通知。

每架构新增 23 个 case，覆盖 FIFO/独立资源、槽满与 move/reset/复用、controller 先析构、SSD 同实物换分类、部分 commit、授额前取消与已取通知后的取消/销毁，以及实际 ledger+queue+provider 的 20/40 页 × 四种 BPP × 自主恢复/close。私有 queue 集成测试的首次链接失败保留；只导出既有冷方法，未新增生产旁路或第二 owner。

初次完整矩阵为 5,695 passed / 1 failed，ARM64 `testMutatedJobs` 的原失败保留。先修复夹具共享 QStringList 的并发追加；隔离复验又发现 worker 快速完成会让第三项进入同次 dispatch，原测试将双 worker 误作两项 batch。测试 strategy 增加 semaphore 完成屏障，保持真实双 worker 与原断言，不改变生产调度；新源码两架构各 100 次隔离通过，再重新构建和冻结完整矩阵。

最终同源码 **17 目标 × 2 架构，5,696 passed，0 failed/skipped**。结构门 1,612 APIs / 15,830 edges / 15 callbacks、21 manifest / 23 ownership / 16 census / 19 intrusion；6 项工具自测通过，ratchet 不变。每架构 96 个预算生产者探针区间（16 等待者下 release/部分 commit/live release）、72 个 root/cursor、28 个原安装/index、96 个暖读及 31,080 个共同安装区间，allocations/bytes/frees 全零，正控制有效，全部与矩阵共用同一 image dylib。预算冷注册、monitor/worker 派发和 callback 不在零分配声明内；其他探针的原边界不变，不外推为 stroke 耗时。

函数→联动→验收见 [04b / W1–W8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04b_budget_waiter_implementation_map.md)，完整身份、十二文件增量和全部中间/最终记录见 [S10 budget waiters 证据](evidence/br1_s10_budget_waiters_20260927/README.md)。**完整 S10/S09 仍开放：** 32-request 上限不等于 context/slot/callback/monitor 已硬计账；共享全局额度、必要终结空间、前台 job continuation、结构化拒绝理由、dispatch 分配失败和完整压力/退出仍待实施。S08 热点/销毁、last-use/completion 清理、legacy batch/idle、M6/M7/M8、undo/context 与完整目标继续；未新增 Fresh 2% 回退、真实 stroke、Vulkan、TSAN 或 BR1-PERF 资格。


**S09 第三批：最后订阅取消后的 completion 存储清理。** 原 registry 增加 exact signal/空状态复验，最后订阅取消后移除仍 Pending ticket 的空通知记录；source 通知表变空时将槽容量移到 gate 外释放。ticket 状态、原 operation 和 payload 债务不因此终结。取消先释放 signal gate，再取 registry→signal gates 复验；新 waiter 或替换 signal 不被旧取消删除，已取出的 callback 仍由消费者 incarnation 复验。

弱清理引用指向原 Private，仅清理期间临时保活，不捕获 facade/store/provider。空表在 terminal 外部 callback 前释放，取消的空 state 在捕获析构前释放；冷登记先准备真实节点，再移入 callback，失败的捕获/订阅活到 registry gate 外终结。该冷失败责任尚无完整 allocator 故障注入资格，存活 map/terminal 索引/其他通知的硬字节预算也未闭合。

修复前同一 Pending-ticket 取消反例在两架构均记录 storageRecords 1（预期 0），失败保留。每架构新增 9 个 registry case，覆盖反复/集中取消、容量回收、重入/重登记、取消与登记三种次序、最后订阅及有 sibling 的析构竞争和阻塞中的已取 callback；原 CPU close 两种 provider 用例证明通知清理后仍保存并最终消费同一 Pending operation。

最终同源码 **17 目标 × 2 架构，5,714 passed，0 failed/skipped**。结构门 1,619 APIs / 15,914 edges / 15 callbacks、21 manifest / 24 ownership / 16 census / 19 intrusion；6 项工具自测通过，ratchet 不变。两架构各 96 个预算生产者、72 个 root/cursor、28 个原安装、96 个暖读和 31,080 个共同安装区间，allocations/bytes/frees 全零，正控制有效，并与矩阵共用同一 image dylib。冷登记/取消/通知不在零分配声明内，其他原测量边界保持不变，不外推 stroke 性能。

函数→联动→验收见 [04a §9](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#9-r3-取消清理的代码与验收对应)，七文件增量、反例和最终身份见 [S09 subscription cleanup 证据](evidence/br1_s09_subscription_cleanup_20260927/README.md)。前两批记录中的空 completion signal 回收待办由本批覆盖；**完整 S09/S10 仍开放：** last-use、实际元数据收费、共享预算、前台 continuation 和完整故障/压力/退出继续。S08、legacy batch/idle/raw、M6/M7/M8、undo/context 与完整目标保持开放；未新增 Fresh 2% 回退、真实 stroke、Vulkan、TSAN 或 BR1-PERF 资格。


**S09 第四批：原读释放记录的上游 last-use 自动确认。** 成功 metadata ReleaseRead 后，原 ActiveReadRecord 保留 exact replica/lease ID/ticket 直至保护解除，删除原 pending-last-use 复制记录 vector。通知仅链接原记录并 notify 冷预备 wake，monitor 在非零 owner 引用上取得临时寿命；原 worker 每轮最多 32 条，acknowledge 后交原 history/retirement/ledger 继续，不扫描全 lease map。多个 lease 共用 ticket 时，原 metadata 一次清除全部保护，剩余读记录以 exact 查询收敛，不新增 acknowledgement 权威或写权限。

close 先关闭通知准入/注销订阅，再锁外等待即时工作，主动确认原 terminal 记录；拒绝后重挂。facade 析构停止新唤醒，休眠通知不保活 Store。idle 等待包含 last-use→history→retirement；未完成 ticket 仍为实际债务。无后台能力保留显式 acknowledge，自动与显式竞争只消费一次。

修复前无外部 acknowledge 的反例在两架构均保留 pendingLastUses=1，失败日志保留。每架构新增 42 个 case：四种 BPP/三种终态/三种完成次序、129 条独立或共享 ticket 的有界 pass、排队 close、Pending/排队事件下直接析构和显式兼容。定向矩阵各 337 passed 后，最终同源码 **17 目标 × 2 架构，5,798 passed，0 failed/skipped**。结构门 1,631 APIs / 16,026 edges / 15 callbacks、21 manifest / 24 ownership / 16 census / 19 intrusion；6 项工具自测通过，ratchet 不变。

两架构各 96 个预算生产者、72 个 root/cursor、28 个原安装、96 个暖读及 31,080 个共同安装区间，allocations/bytes/frees 全零，正控制有效，与矩阵共用同一 image。新 last-use 冷登记/通知/acknowledge/关闭不在这些零分配声明内，原测量边界不变，不外推 stroke 性能。

函数→消费者→测试见 [04a §10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#10-上游-last-use-到实际退休的代码与验收对应)，八文件增量、反例及最终身份见 [S09 last-use 证据](evidence/br1_s09_last_use_20260927/README.md)。**完整 S09/S10 仍开放：** metadata ReleaseRead 本身拒绝时仍由原 release-retry 链保留，自动订阅尚未建立；冷准备/dispatch 分配失败及 metadata acknowledge 拒绝后仍须完整自主压力恢复。存活记录/通知硬预算、共享额度、前台 continuation、多 store 公平性和完整故障/退出继续。M6/M7/M8 与 BR1-PERF 未完成，未新增 Fresh 2% 回退、真实 stroke、Vulkan 或 TSAN 资格。


**S09 第五批：单次读保护原地终结与 metadata 容量归还。** `applyOwner` 的单个 ReleaseRead 与 verified `acknowledgeLastUse` 进入原 metadata owner 的 `applyReadProtection`；exact identity、publication claim 和 revision gate 保持。无 ticket 摘除原 ReadLease，有 ticket 将原 slot 移到链尾并转为 PendingLastUse；acknowledge 清除同 exact replica 的全部匹配 ticket。成功推进 revision，不触及无关 writer/history；mixed sequence 保持原子投影安装，未验证 acknowledge 仍被普通 owner 拒绝。局部 transition、节点访问及 slot 复用/释放分别计数，不再把直接终结记作版本投影/安装。

节点 erase 只检查其所在 block，空块沿既有 intrusive 链转移，不扫描整个 arena；保留一个暖块和尚有 reservation 的已准入容量。链改为迭代析构，payload 销毁后才归还真实 charge。析构发生在 shard gate 外；外层 store owner gate 和一条共享 ticket 下任意多节点的整体销毁预算仍须继续，不能由本批零分配推出恒定时间。

修复前满容量用例两架构各 18 项全部因 arena 预算拒绝而失败；新增 reference/身份/顺序/重复/mixed-sequence、实际 block/预算/reservation、worker/body/capture/新前台线程等共 68 case / 架构。allocator 探针额外揭示首个回收线程 TLS 读取分配 32 B；改用既有单 worker 的活动 job 身份，捕获析构后再清除，drain 后线程复用不留下陈旧标记。原反例、初次 fixture 编译失败和 TLS 探针失败均保留。

最终同源码 **17 目标 × 2 架构，5,934 passed，0 failed/skipped**。结构门 1,636 APIs / 16,231 edges / 15 callbacks、21 manifest / 24 ownership / 16 census / 19 intrusion；6 项工具自测通过，ratchet 未改。每架构新增 42 个未预热前台线程终结区间，真实 reclaimer 同时活跃，allocations/bytes 全零；各释放 10 个实际 blocks，frees 与 arena 变化一致。原 96 个预算生产者、72 个 root/cursor、28 个原安装、96 个暖读和 31,080 个共同安装区间，allocations/bytes/frees 仍全零；正控制有效，十二次最终探针与矩阵共用同一 image。

代码→验证见 [04a §12](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#metadata-terminal-implementation)，五文件增量、所有失败与最终源码/库身份见 [metadata terminal 证据](evidence/br1_s09_metadata_terminal_20260927/README.md)。前批“单次 ReleaseRead/ack 为安装申请新 metadata”的容量拒绝由本批消除；**完整 S09/S10 仍开放：** 其他 claim/身份/revision 拒绝后的接续、cold subscription/dispatch 必要容量、全局/实际 metadata 收费、前台 continuation，以及外层销毁与完整故障/压力资格继续。未新增完整 claim/revision 耗尽定向矩阵、Fresh 2% 回退、真实 stroke、Vulkan、TSAN 或 BR1-PERF 资格；S08、legacy batch/idle/raw、S02–S05、M6 全出口、M7/M8、undo/context 与完整目标保持开放。


**S09 第六批：读保护空块移出外层 owner gate，保留实际 charge 与退出责任。** 原 metadata 在 shard gate 内把空块与原预算责任交给调用者的栈上 cleanup 值；intrusive 链 O(1) 拼接，无新增队列或权威。公开 acquire 取消重试、resolve 失败取消、release/ack/cancel、abort prepared request 及 close 传同一 scope；scope 在外层 owner 解锁后迭代 free，再归还原 live charge。清理期间原 activeProviderCalls 保持活动；后台先清理再发布 idle/释放 owner lifetime，close 先清理自身 scope 再作能力检查。

新增 15 case / 架构覆盖跨 shard、跨 owner 拒绝、move/reset/destructor 预算责任及七条真实业务路径。最终同源码 **17 目标 × 2 架构，5,964 passed，0 failed/skipped**；结构门 1,654 APIs / 16,371 edges / 15 callbacks、21 manifest / 24 ownership / 16 census / 19 intrusion，6 项工具自测通过，ratchet 未改。每架构 42 个 carrier 转移区间 allocations/bytes/frees 为零，随后 42 个 clear 区间 allocations/bytes 为零、各实际 free 10 blocks。公开 acknowledge 暂停在经过调用栈确认的 block free 时，另一线程可取得 owner 锁，活动计数为 1、原 charge 仍 live；继续后 idle/close 成功。六组既有探针保持原资格，十六次最终探针与矩阵共用同一 image。

早期尺寸筛选误命中确认列表的扩容释放；这些失败不作为空 arena block 的独立反例，保留原始日志、实际调用栈和修正说明。新增测试的缺少头文件/默认 4 BPP fixture 修正及生成期间源码变化的拒绝记录同样保留。

代码到验证与后续待改段见 [04a §13](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#outer-read-cleanup)，源码/库身份和增量见 [外层清理证据](evidence/br1_s09_outer_cleanup_20260927/README.md)。**本批没有完成 T4 的整轮节点/字节/时间预算或其他临时大对象清理，也没有补齐 T5 拒绝接续、T6 必要存储准入、S10 全局计账/压力资格。** 实际 stroke 收益未测，不新增 Fresh 2%、正式性能、Vulkan 或 TSAN 资格。S08/S09/S10、legacy batch/idle/raw、S02–S05、完整 M6、M7/M8、undo/context 与完整目标继续开放。


**S09 第七批：completion 故障原子性与 T5 生产前提核对。** 当前 commit/restore、overlay 和 recoverable write 的 metadata 安装与 generic read 终结共用 store owner gate，claim 只活在同步安装调用内。没有据 reference 层独立调用的 claim 反例新增生产轮询队列；M7/M8 若改变 admission/gate，必须重新证明交错与接续。

实际故障探针发现原 complete 的 prefix 已推进后，空 QMap 的可写 begin 仍可能分配失败，留下“已终态、未通知”；Failed/Cancelled 原先在覆盖发布后才分配例外结果，同样可能被误读为 Succeeded。当前 Qt QHash 的 findOrInsert 带 noexcept、内部仍可申请 span/node，真实定点失败会终止进程，外围 bad_alloc catch 不足以构成恢复契约。

原 registry/source/readiness owner 保持；私有存储改用不隐式共享且插入有强异常保证的标准容器，先准备准确非成功状态，再推进终态覆盖。失败撤销新状态项并保留 Pending/原 waiter；成功后才摘通知并在 gate 外调用。订阅插入失败保留其他 waiter/source，capture 门锁外清理，空 bucket storage 在 callback 前释放。没有用整表复制回滚。

新增每架构 54 项 range/status/duplicate 用例。最终同源码 **17 目标 × 2 架构，6,072 passed，0 failed/skipped**；结构门 1,655 APIs / 16,389 edges / 15 callbacks、21 manifest / 24 ownership / 16 census / 19 intrusion，6 项工具自测通过，ratchet 未改。每架构终态故障 46 区间/28 次实际拒绝，订阅/source 故障 26 区间/20 次实际拒绝，均保持原状态且可以重试；1,024 次首个及后续顺序 Succeeded 区间 allocation/bytes/free 为零。八组既有探针继续通过，二十二次最终探针与完整矩阵 image 一致。

具体代码、真实失败与测试边界见 [04a §14](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#completion-failure-atomicity)及 [completion atomicity 证据](evidence/br1_s09_completion_atomicity_20260928/README.md)。本批保证拒绝不伪造成功，**没有完成**乱序/非成功终态与订阅/派发的必要存储准入、producer complete(false) continuation、armLastUse/dispatch 失败后的自动进度、完整 T4/T5/T6/S10 及故障/压力资格。S08、legacy batch/idle/raw、S02–S05、完整 M6、M7/M8、undo/context、Fresh 2% 与正式 BR1-PERF 继续开放；没有新增真实 stroke、Vulkan 或 TSAN 资格。


**S09 第八批：读请求、lease 和 provider 节点的准入前移。** 真实 allocator 反例证明原 resolve 在 pin 返回后构造 ActiveReadRecord 失败，会遗留 Resolving request 且无法交付 lease。现先准备 request 节点再 AcquireRead；先准备原 ActiveReadRecord/control block 和可转移 active node，再调 provider。成功消费原节点，准备失败保留 Pending；CPU/tiles3 原 activeLeases 节点同样先于物理访问准备，pin 拒绝/异常仅撤销预备项。binding 的读门锁改为 RAII，保留 native try/wait 语义；原 owner/lease/last-use/close 责任保持。

每架构新增 28 项用例；17 目标 × 两架构 **6,128 passed，零失败/跳过**。调用图 1,655 APIs / 16,459 edges / 15 callbacks；21 manifest / 24 ownership / 16 census / 19 intrusion 与 6 项工具自测通过，ratchet 未改。每架构 request/resolve/provider 分别 4/9/10 区间、2/7/6 次真实拒绝；既有读者保持，随后可以清理/close。两种规模的 pin 返回区间无分配尝试；其余十一组既有探针继续通过，30 次 final 与矩阵 image 一致。

实现与待改代码关系见 [04a §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#read-storage-admission)；[read admission 证据](evidence/br1_s09_read_admission_20260928/README.md)保留命令、失败与身份。本批未闭合必要 notification/wake/dispatch/retry/pass 准入及收费、完整 metadata/swap/SSD 故障、自动接续、T4/T5/T6/S10 或通用 write coordinator 的 pin 后记录。S02–S05、完整 M6、M7/M8、undo/context、Fresh 2% 和 BR1-PERF 继续；没有新增真实 stroke、Vulkan 或 TSAN 资格。


**S09 第九批：通用写节点准入、准备异常与原终结责任。** 旧 image 的真实 post-pin 分配拒绝命中 ActiveWriteRecord 控制块，留下 Resolving request 且无 lease。现原请求节点在共同写计划前准备，ActiveWriteRecord/control block 与可转移 active node 在 provider pin 前准备；成功后 noexcept 接入能力、转入原 map 节点。准备拒绝保留 Pending，provider bad_alloc 先恢复 gate 再恢复原请求。resolve/cancel 的请求身份一致，返回能力的 mode/replica/lease/operation 不匹配时锁外归还实际 pin。

共同 recoverable 准备清理改为条件 unlock，避免锁外异常引发重复解锁；generic 的共同计划/Fresh provider/初始化调用边界分别恢复原责任。初始化已有 private writer 后失败，取消拒绝时仍由原 request/transaction abort 承担；已消费 lease 的失败仍留原 active record。没有新增 selector、write set 或终结 ledger，native resident pending 不进入 generic 索引。

新增每架构 68 项用例：Fresh/recoverable 四 BPP 下重试/取消/abort、257 个锁外并发 request/lease 增长、准备异常、真实预算阻塞恢复、请求身份及 provider 能力失配。最终 **17 目标 × 两架构，6,264 passed，零失败/跳过**；调用图 1,655 APIs / 16,633 edges / 15 callbacks，21 manifest / 24 ownership / 16 census / 19 intrusion 和 6 项工具自测通过，ratchet 未改。

每架构新 write request / resolve allocator 探针分别 4/9 区间、2/7 次实际拒绝；原请求、其他 0/257 条 capability、取消与 close 均保持。post-pin 两区间无分配尝试，具有修复前同路径反例；十五组既有探针继续通过，36 次 final 与矩阵 image 一致。所有编译和夹具失败记录保留，最终资格仅绑定 checks-01 与 final。

函数、已接线与剩余修改见 [04c：通用写准入 GW1–GW7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04c_generic_write_admission.md)；[write admission 证据](evidence/br1_s09_write_admission_20260928/README.md)保留完整身份和失败。本批没有闭合更早 activity/admission、metadata/descriptor/ledger/provider 内部全部存储故障，必要终态/notification/dispatch/retry/pass 准入及收费、自动接续、整轮 T4/T5/T6/S10 或完整压力资格。冷 generic 索引 O(log L) 尚需性能实测。S02–S05、完整 M6、M7/M8、undo/context、Fresh 2% 和 BR1-PERF 继续，未新增真实 stroke、Vulkan 或 TSAN 资格。


**S02 第一批：冷热稳定分块、原索引拒绝原子性与实际容器计账。** 原 write set 保留单页 inline，热 overflow 改为 8-slot 稳定块，冷 Page overflow 同步改为 2-slot 稳定块；目录按需几何增长。原唯一稀疏索引使用带原 controller allocator 的标准容器，第 9 项先完整准备索引候选，成功后才安装 noexcept entry；插入拒绝保持原 size、keys 和稳定地址。块、目录、index node/bucket 在分配前计入原 MetadataArena，free 后归还；保留容量仍收费。

native/semantic entry、cold storage 与 managed-range 准备拒绝回到原失败/取消链；guard 晚于 session façade 释放时仍保活原 owner。没有新增 write set、selector、generation 或 budget authority，也没有放开线程边界。原来 append-only 的密集索引语义保持，后续 subset 才引入相应 slot 复用与 incarnation。

每架构新增 14 项用例，最终 **17 目标 × 两架构 6,292 passed，零失败/跳过**；结构门 1,681 APIs / 16,833 edges / 15 callbacks、21 manifest / 24 ownership / 16 census / 19 intrusion，六项工具自测通过，ratchet 未改。旧 image 的 2→1,000 页探针证实 overflow 地址移动，当前两架构均保持。每架构 write-set 24 区间/20 次、native/semantic 50 区间/42 次真实 allocator 拒绝后，原索引、取消、重试与 close 均成立；五种规模 repeated-hit 区间零 allocation/bytes/free。另复验共同安装、legacy install、暖读与外层清理；16 次最终探针与完整矩阵 image 一致。

实现及下一段代码见 [01c §8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#stable-storage-implementation)，命令、失败样本、实际 bytes 和身份见 [S02 稳定存储证据](evidence/br1_s02_stable_storage_20260928/README.md)。本批只覆盖稳定增长及这些容器的实际计账：空位/空块回收、slot incarnation、job borrow、subset/完整 checkpoint、scope/range/control-block 和 admission/activity 内部全部故障、必要终结容量及共享父额度仍待落实。不能把 append-only 存储当成长 stroke 最终方案。A 批、S02–S05、完整 S08–S10、M6/M7/M8、undo/context、Fresh 2% 和 BR1-PERF 继续开放，未新增真实 stroke、Vulkan 或 TSAN 资格。


**S02 第二批前的未验收检查点（2026-09-28 文档核对，已由下述第二批更新）。** 上述 S02 第一批的 6,292 passed 绑定其冻结源码 `4d0db8a75988529ce53adad9ed1af976cf267fb6ec9bd804f392a2393fa29fac`。当时工作树已有 `KisMutationStorage` 的 slot/incarnation/live 枚举/空块转移草稿，但 write-set 索引、ColdPageSet、guard、admission 和 seal/cancel 消费者尚未一起迁移；这份后续源码没有取得该矩阵资格。具体待改段、联动顺序及新验收要求见 [01c §9 / A1–A7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#reusable-slot-integration)。本次只补文档映射，不新增任何 M6/M7/M8 或性能通过结论。


**S02 第二批：可回收 slot、准确身份、原 claim 单项取消与锁外归还。** 原热集合/冷槽采用 live 枚举，索引与 guard 校验 incarnation，inline 同样拒绝旧身份；计数耗尽不回绕。取消成功项按原 metadata 终结、冷资源/源、logical claim、entry 的顺序释放；后项拒绝只保留未完成债务。重试不能误撤已释放 key 上的新 writer，removal 只计一次。空块和最后集合/索引/目录在 owner gate 外实际 free 后归还原 charge，清理期间保留 activity 与 owner 寿命；seal 丢弃目标后先归还摘出的容量，再准备 alias。

每架构新增 30 项；最终 checks-02 为 **17 目标 × 两架构 6,352 passed，零失败/跳过**。结构门与六项工具自测通过，20 次最终 allocator/失败/清理探针与矩阵 image 一致；checks-01 及其探针保留但不覆盖最后的 seal 释放时点修正。1/2/8 页各复用 1,000 次零 allocation/bytes/free；9/1,000 页每次新 key 保留一个实际索引节点分配/释放，live bytes 不累积。同一 live key 重复命中仍零分配。冷热布局上限保持，新增 slot 身份/链与保留容量全部实际收费；不以这些结构结果推定真实 stroke 加速。

函数、联动和剩余修改见 [01c §10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#reusable-slot-implementation)，源码/image、命令和成本见 [S02 复用槽证据](evidence/br1_s02_reusable_slots_20260928/README.md)。本批单项释放只消费原部分取消，不等于 subset seal 或完整 checkpoint；仍未开放跨 worker/job，未接持久 stroke。SS1/SS5/SS6/SS7/SS8、整体范围/borrow 准入、admission/activity 内部全部分配拒绝、scope/range/control-block 计账、必要终结容量和共享父额度继续。完整 S01–S10、M6/M7/M8、undo/context、Fresh 2% 与 BR1-PERF 保持开放，没有新增真实 stroke、Vulkan 或 TSAN 资格。


### S02 第三批：实际 claim/activity 接纳与原终结寿命（2026-09-28）

本批落实 [01c §11 / J1–J8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-implementation-map) 的原表与 caller 子范围，逐段交付及剩余责任见 [01c §12](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-implementation)。原 claims/activity 改实际预构造平坦桶，managed/native/generic 同步接准备、复验、无分配安装；首次 activity 可报告拒绝，publication removal 回调一并迁移。原 set/token/slot/origin 权限保持，token 耗尽拒绝新 set。scope、std shared control block 与 range 对象接原 allocator，未激活候选不会进入活动取消协议；实际 free/还账前保持原 owner。原 scope 的 intrusive orphan 链消除取消拒绝时新增保留节点的依赖。

最终同源码双架构 17 CPU/业务目标 **6,380 passed，0 failed，0 skipped**，结构门、六项工具自测与 26 次最终探针通过。每架构新增 admission 故障探针 132 区间/122 次真实拒绝；managed 拒绝 body=0，恢复后可重试并 close。扩容期间冲突/关闭拒绝、无关 revision 修改重准备均验证；allocation/free 期间其他线程可取得 owner gate。1/4/5/65/1,000 claims 的 1,000 次重复接纳及 release/reclaim 均零新增分配。冷增长成本与保留 charge、原始失败、源码/image 身份见 [本批证据](evidence/br1_s02_admission_20260928/README.md)。先前 checks-01 两个旧预算夹具失败原样保留，修正实际 scope 准入预算后完整重跑；不将失败矩阵作为最终资格。

动态桶保留到 owner 析构并持续收费，尚无 shrink/压力策略；增长 snapshot 在 gate 内复制全容量，未授予 hold 上界或真实 stroke 性能。仅闭合原 orphan 链的节点分配，其余必要取消/通知/派发存储及自动进度继续。generic request/lease 控制块、Store/controller 内部 bookkeeping、共享父额度和整个 job 冷资源准入仍开放。下一批沿 SS1/SS5 业务 scope/job 借用推进，联动 SS6–SS8、S01/S03–S05/S09/S10。完整 S02、M6/M7/M8、undo/context、Fresh 2% 与 BR1-PERF 均未关闭；没有新增 Vulkan 或 TSAN 资格。


### S02 第四批：执行范围借用与真实 operation 消费者（2026-09-28）

原 session 新增 `borrowExecution`，能力仅绑定原 write set 的 slot/incarnation；跨 worker 接续通过新 borrow，同一个 borrow 限创建它的 worker。原 `claimRange` 只访问本次范围，全复验后接纳新增 claims；拒绝回滚本次新 entries，旧 pending/claims 保持。guard 的 aliasing owner 保留原 execution、scope 和 budget owner，晚 guard 归还前不能重用范围；finish 只归还 execution，abandon/cancel 选定原 scope 的失败终结。managed pixel operation 与 packed overwrite 已实际消费，仍由原 batch 每 operation seal；未启用业务层持久 stroke。

最终同源码双架构 17 CPU/业务目标 **6,412 passed，0 failed，0 skipped**，结构门、六项工具自测和 30 次最终探针通过。两个 worker 不相交 guards 同时存活、65 页扩容期间旧 slot/字节保持、另一个 worker 对同页 1,000 次访问复用同一 generation，四种 BPP 均验证。每架构范围故障探针 121 区间/117 次真实拒绝，旧 pending 版本/字节保持并可 retry/cancel/abort/close；借用内 1,000 次 resident guard 访问零分配。

初版每页 40 B 的重复 key/slot/回滚记录导致原 8 MiB、384 页/6 MiB packed-write 用例在两架构失败，checks-01 的 6,410 passed / 2 failed 原样保留。现仅常驻原 16 B slot handle，临时回滚 bitmap 在 body 前释放；原负载、预算和第二 backend 拒绝/退出断言均保持，checks-02 完整复验恢复通过。1,000 页再次借用的实际申请量由 40,176 B 降为 16,280 B，仍有 3 次真实申请和对应 free，不称整个 job 准入零分配。

代码关系和明确剩余责任见 [01c §13](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#execution-borrow-implementation)，源码/image、所有命令/失败及对账见 [本批证据](evidence/br1_s02_execution_borrow_20260928/README.md)。每个 guard 仍争用 session mutex，首次准备仍串行；SS6 局部 gate、SS1/SS5 业务 token/job/read footprint/cut、SS7 checkpoint/压力窗口、SS8 painter/iterator/refresh 继续。完整 B、S02、S09/S10、M6/M7/M8、undo/context、Fresh 2% 和 BR1-PERF 均未关闭，没有新增真实 stroke、Vulkan 或 TSAN 资格。


**S02 第五批：execution 局部 resident 访问与 guard 归还。** 原范围每页仍 16 B，绑定在结构 gate 下验证的原 entry/冷 Page 引用；活跃借用与晚 guard 保活排除 slot 回收或复用。原 claimRange 按声明 keys 查询唯一 write set，全范围复验再安装。resident beginWrite/version/providerBacking/unpin 不再取 session 结构锁或查询可增长目录；仍经原 binding 真正 pin，NonResident 继续真实 materialize。原 lifecycle 为 atomic，取消停止后续接纳，已接纳调用可安全归还，原 scope 保留取消责任。

累计 pin/释放/materialize/字节在 execution 局部写，最后借用归还时一次归并；§6 已明确峰值字段为单 execution 的精确峰值，runtime census 与测试同步。没有新增跨 execution 共享热计数或像素访问权威。控制记录实测增加 64 B 至 216 B，每页范围仍 16 B；原 8 MiB、384 页、6 MiB 输入及第二 backend 拒绝用例保持通过。

本批 17 目标 × 两架构 **6,444 passed、0 failed/skipped**；结构门 21 manifest / 24 ownership / 16 census / 1,780 APIs / 18,022 edges / 17 callbacks / 19 intrusion，六项工具自测通过。32 次最终探针全部绑定本批源码与 image：借用内各 1,000 次 guard/version/归还零分配；范围存储每架构 121 区间 / 117 次实际拒绝保留旧 pending；真实 materialize 阻塞期间取消可记录意图，已接纳调用完成且后续访问拒绝。定向测试证明冷准备阻塞时另一 worker 的 1,000 次双页访问和跨线程 unpin 可完成，swap-out/in 保持原像素与 generation。

函数、联动与剩余责任见 [01c §14](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#local-execution-implementation)，实际成本、失败日志、源码与二进制身份见 [S02 局部 execution 证据](evidence/br1_s02_local_execution_20260928/README.md)。冷缺页仍按 execution → session → owner 串行准备，末端摘链仍需结构 gate。业务持久 scope、scheduler job/cut/read footprint、完整 checkpoint/压力 subset、painter/iterator/refresh 联合迁移与全 job 冷资源继续；M6/M7/M8 和 BR1-PERF 未完成，未新增真实 stroke 时延/吞吐、Fresh 2%、Vulkan 或 TSAN 资格。


### S03 前置批：成功 delta 的元数据刷新与失败字节恢复（2026-09-28）

Store 新增批量 `resolvePagePresence`，在原 owner gate 内消费 canonical selector；输出存储/Qt detach 在 gate 前，旧输出释放在 gate 后。backend 保持原 publication read gate 和 history/anonymous/current 顺序。成功 `refreshPageStorePages` 只增删兼容索引并清 read-ready，不再 capture 或读取 payload；已存活 reader 的字节/pin 保留到 unlock，下一次真实 reader 再解析。不存在第二份 presence/selector 权威，也未将未 sealed pending 暴露给 metadata 查询。

初版将失败回滚也改为仅失效，六项 copy swap-in 故障用例证明 raw cache 会保留局部写入；已恢复 `refreshPageStoreIndex(rect)` 的一个 exact-view 缓存字节恢复路径，原六项 raw 字节断言不变。`installPageStoreReadCache/takeIdleReadCache` 仍有该真实消费者，不能提前删除。16 项 packed 计数仅移除成功 refresh 的一次 capture，保留 operation-start 和测试注入次数。

最终 17 CPU/业务目标 × 两架构 **6,484 passed、0 failed、0 skipped**，结构门、六项工具自测和 34 次最终探针通过；图为 1,782 APIs / 18,061 edges / 17 callbacks，21 manifest / 24 ownership / 16 census / 19 intrusion 与布局约束保持。新增 16 组 manager 与四种 BPP 底层选择器场景，覆盖旧 reader、新增页/extent、后续读取、history、未 sealed pending、remove/default、无效 selector 输出不变和无保留 close。

真实成功刷新探针在两架构、四种 BPP、history/no-history、K=1/9/65/257 各重复 1,000 次：新增 capture/read request 为零，原 swapped 页保持 NonResident；每次仍有一次 K+18 requested bytes 的 Qt 分类数组分配及释放。不是全刷新零分配、恒定 hold 或端到端 stroke 加速证明。原 8 MiB/384 页及全部旧预算负载保持。

逐段代码和下一批入口见 [01d / MR1–MR7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01d_metadata_refresh_and_pending_visibility.md)，源码/image、最终矩阵、探针成本及全部失败记录见 [S03 元数据刷新证据](evidence/br1_s03_metadata_refresh_20260928/README.md)。MR5 发布前适配存储/预算与结构化失败、MR6 持久 scope/job/cut/current/checkpoint、MR4 raw consumer/idle 引用继续；当前仍每 operation seal，元数据查询不能替代 pending 的变更传播。S02/S03、S09/S10、完整 M6/M7/M8、Fresh 2% 与 BR1-PERF 均未完成，未新增真实 stroke、Vulkan 或 TSAN 资格。


### S02 第六批：完整 session checkpoint 与原 owner 再开放（2026-09-28）

原 session 新增 `checkpointForRead`，完整消费原 seal/overlay/proof 后，通过与公开 capture 共用的 helper 冻结完整 sealed overlay。保留原 session activity 与 owner，使事务在 scope 打开期间不能 commit/abort；原 page claims、冷热段存储和源在原终点释放，空的新段仍沿原 allocator 计账。scope gate 保持到 capture 完成，之后同一 session 可由另一 worker 重新借用；局部累计统计只归并一次。存在 execution/guard 或结构锁忙时立即拒绝，不等待冷准备，也不改变 Active 状态。

最终 17 CPU/业务目标 × 两架构 **6,580 passed、0 failed、0 skipped**；新增 48 项/架构覆盖四种 BPP、1/10/1,000 次重复写、跨 worker、多次/空 checkpoint、远页完整性、旧视图跨失败/取消存活、remove/default/rewrite、实际范围存储归还和完整 close。结构门及六项工具自测通过：1,785 APIs / 18,267 edges / 17 callbacks；21 manifest / 24 ownership / 16 census / 19 intrusion 保持，未放宽原布局或预算负载。

36 次最终探针绑定本批源码和 image；新增探针覆盖 K=1/9/65/257、同一个 session 连续三个 checkpoint。每段 1,000 次已准备 guard 访问 allocation/bytes/free 均为零；checkpoint 本身有非零 seal/capture/retention 分配，不授予零分配安装或恒定 gate hold。最初资源断言错误地要求写入后 total MetadataArena 净下降，四种 BPP 及探针均保留失败反例；现分别验证声明未写范围的真实归还和冻结视图的新增保护，不降低原像素、版本、取消及预算约束。

代码关系和剩余接线见 [01c §15 / CP1–CP5](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#checkpoint-implementation)，源码/二进制身份、全部失败和实际成本见 [S02 checkpoint 证据](evidence/br1_s02_checkpoint_20260928/README.md)。锁空闲不等于 scheduler cut；排队 jobs、必要子任务、跨 store 及其他 mutation 的协调仍须由业务 owner 接线。seal 后 capture 若返回拒绝，新段已在 overlay，接口终结空 scope；整笔回退由原事务 owner 处理，不能作为跨 checkpoint 的 Operation rollback。完整 allocator 异常与必要终结容量仍须闭合。

下一段为 SS1/SS5 history-owned scope、job 身份/读写 footprint/cut 与 SS8 current/G0/source、painter/iterator 联合接线，再完成 SS7 pressure subset、S04/S05/S09/S10 的发布/资源/终结出口。原生产仍每 operation seal，未启用持久 stroke。S02/S03、完整 M6/M7/M8、真实 stroke / Fresh 2% / BR1-PERF、Vulkan 与 TSAN 均未新增完成资格；优先级仍为 stroke → undo → 上下文切换。


### S02 第七批：原 scheduler 切点与必要子任务（2026-09-28）

新增 `KisStrokeStrategy/Queue/Stroke::addCheckpointJob`，在原 queue mutex 内与输入接纳线性化。请求前已排队 jobs 及运行中 jobs 递归产生的必要 children 先完成，后接纳普通输入在 cut 后；请求方立即返回并归还自身 borrow。普通 mutated job 会 prepend 到队首，不能替代该切点。pen-up 已排队时 continuation 放在 finish 前，finish 已派发后拒绝；一个 non-owning 指针索引原队尾 finish，在删除或派发时清除，不扫描 job backlog、不另建 job 集合。

SEQUENTIAL 沿原调度规则等待 stroke jobs，BARRIER 另等待 merge/external work；二者均沿原 dab strategy 执行。请求必须 cancellable、LoD 匹配；原取消/失败丢弃未开始的 cut，保留必要 non-cancellable child 先于 cancel。已离队但仍被 LoD buddy 保留的 owner 不能重新接纳 cut；成功/拒绝均归还 data 的唯一所有权。PageStore 像素、事务和精确视图仍由原 owner 授权，队列位置不提供第二份权限。

最终 17 CPU/业务目标 × 两架构 **6,646 passed、0 failed、0 skipped**，每架构新增 33 项：12 项队列排序/拒绝，16 项真实 2-worker + Tiles3/Store/session 的像素切点，4 项取消次序，1 项保留句柄拒绝。真实测试覆盖四种 BPP、两种 cut、pen-up 两种次序，先前排队/递归派生的五页全部纳入冻结视图，后输入重写不改变旧 view，原 session 仅创建一次，generation/pin/终结准确。

结构门、六项工具自测与 36 次继承探针通过；调用图为 85 TUs / 1,785 APIs / 18,331 edges / 17 callbacks，21 manifest / 25 ownership / 16 census / 19 intrusion。新增 `BR1-OWN-STROKE-CUT` 仅明确原队列事实，原布局与侵入上限保持。源码/image 和最终矩阵绑定见 [S02 scheduler cut 证据](evidence/br1_s02_scheduler_cut_20260928/README.md)；这些探针没有测量新 cut 的分配/等待成本，不授予零分配、恒定 hold、真实 stroke 延迟或 Fresh 2% 资格。

逐段函数与联动责任见 [01e / SC1–SC6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01e_scheduler_cut_and_job_admission.md#scheduler-cut-map)。测试 strategy 直接持有原 session，尚未接 TransactionData/freehand 的持久 token；下一段必须联合完成 SS1 history-owned scope、SS5 job 身份/读写 footprint、SS8 backend/painter/iterator/current/G0/source。job 返回后仍能产出工作的异步 producer、多 store/LoD/mask 需显式协调，不能把空队列或已有切点当作完整 producer 结束。

生产仍每 operation seal；不可每 dab 插入 cut 冒充跨 dab 复用。SS7 pressure subset、S04/S05/S09/S10 的发布准备/必要容量/故障/进度、完整 M6/M7/M8、真实 stroke / BR1-PERF、Vulkan 和 TSAN 继续开放；优先级保持 stroke → undo → 上下文切换。


### S02 第八批：原 history 持有 session 与显式事务 cursor（2026-09-28）

原 TransactionData 显式启用后，以原 memento 选择 backend activeHistory 持有的同一个 MutationSession；每次声明目标的 cursor operation 借用原 execution，归还 guard/borrow 后保留 pending，默认普通事务仍 per-operation seal。原 session 唯一持有 entries、claims、失败与像素生命周期；原 history 仅增持有成员及 Open/Closing/Sealed 终结阶段，不另建 token、pending/touched 表或事务。事务层经已有 manager 边界消费 bool，PageStore 类型和 exact view 不上移；后续 reader 在同一调度切点取得既有 immutable read scope。

当前 cursor 坐标为 manager-local、source 须不可变；普通 current immutable 读取仍只观察最后完整 checkpoint。同一 session 完整冻结后，原 proof/removal delta 驱动兼容索引与 device cache 失效。commit 关闭新借用、seal 后走原 history 提交，成功才交付 undo；活跃 execution 导致拒绝时原 Closing 保留并可重试。cancel 先终结原 session，再 abort 原 history；失败 callback 不得后续提交。原 target/saved manager/time/frame/LoD/memento 每次校验，无活跃借用的未完成显式事务析构取消。

最终 17 CPU/业务目标 × 两架构 **6,756 passed、0 failed、0 skipped**，每架构新增 55 项：44 manager、11 实际 TransactionData/device。四种 BPP、D=1/10/1000、跨 worker、完整 cut、远页、commit/abort、旧 reader、活跃写终结拒绝/重试、错误/旧 owner、time/frame/LoD 变化及无活跃借用析构均覆盖。两页同段反复写只创建一个 session、两个 generation，cut 后重写一页只增加一代；该因果计数不代替真实 brush 性能。

结构门、六项工具自测与 36 次继承探针通过；调用图为 85 TUs / 1,788 APIs / 18,413 edges / 17 callbacks，21 manifest / 25 ownership / 16 census / 19 intrusion。初版事务直接引用 PageStore view 被原 ratchet 拒绝，已把结果/精确视图留在原数据管理边界；原门和布局未放宽。两次测试编译失败、结构拒绝及最终源码/image 绑定见 [S02 history scope 证据](evidence/br1_s02_history_scope_20260928/README.md)，具体函数和后续责任见 [01f / HS1–HS8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01f_history_owned_mutation_scope.md#history-scope-map)。

启用必须在无 writer 的初始化边界，尚不支持运行中 legacy admission 的并发转换；真实 freehand/painter/iterator、scheduler job 身份/读写 footprint、current/G0/source 与异步 producer、多 store/mask/LoD 继续联合接线。callback 路径仍有 targets/range/touched 存储，checkpoint/end 仍枚举 O(K_history) 原 delta；MR5/S05/S09/S10 的首字节前适配准备、短 gate、完整 allocator 故障、必要终结容量、任意 facade 提前销毁及共享预算不因 bool 入口而关闭。SS7 pressure subset、S02/S03、完整 M6/M7/M8、真实 stroke / Fresh 2% / BR1-PERF、Vulkan 和 TSAN 均未新增完成资格。


### S03 multi-dab 工作树的指南映射（验证前记录，2026-09-28）

文档整理时的工作树已增加 `bltFixed(rect, dabs, strokeOwner)` 与 PaintDevice 坐标适配入口，两个默认笔刷异步生产调用仍不传 owner。实际代码、待接责任和下一批顺序见 [S03 / MD1–MD7：真实 multi-dab 与 painter scope](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01g_multi_dab_and_painter_scope.md#multi-dab-map)；这是待改代码关系的补充，不改变上述冻结资格。现存 [focused-01 日志](evidence/br1_s03_multi_dab_20260928/kis_painter_test-focused-01.log)为 52 passed、4 failed、0 skipped；三个重复写计数断言失败、一个取消同步点超时，具体诊断边界修订要求见 [01g §3](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01g_multi_dab_and_painter_scope.md#multi-dab-validation)。本次文档整理未修改生产代码或测试，未运行新的业务矩阵，不能以此前 6,756 passed 覆盖这一工作树改动。


### S03：真实 multi-dab cursor、显式 owner 与像素/取消验证（2026-09-28）

默认笔刷的普通/镜像异步 jobs 调用 `bltFixed(rect, dabs)`；该函数现将整个有序 dab 列表放入一次原 PaintDevice 坐标适配的 cursor operation。新增三参数 overload 同步借用原 `KisTransaction`，通过原 history/session 归还 execution，不逐调用 seal；旧 overload 保持独立 operation 语义。源、mask、通道、opacity/averageOpacity/flow 和 wrap/offset 语义保留；共享 painter 的 composite 查找移到每调用局部，新增 overload 按 const 引用消费 dabs，避免包装转发额外复制列表。无新 PageStore 类型上移或新 pending/owner 表。

新增每架构 55 项：48 个四种 BPP × ordinary/commit/abort × mask × wrap 的独立像素 oracle；3 个 D=1/10/1000 重复准备控制；实际双 worker、第一页写后取消、遮罩快照、错误 owner 各 1 项。无 cut 的两页重复写 provider 准备保持两次、seal 为零，完整 checkpoint 后再写两页累计四次。取消用本地颜色空间的原 Copy kernel 写后暂停，确认已改字节、活跃借用拒绝本次终结、第二页 kernel 不执行、原 owner 重试恢复 G0。它证明本入口的具体因果与语义，不是所有 brush 的吞吐或零分配证据。

最终 17 CPU/业务目标 × arm64/x86_64 为 **6,866 passed、0 failed、0 skipped**，36 次继承探针、结构门与六项工具自测通过。源码差异 SHA-256 `62187b32744af5a5b7360a0e2726cc42d20cb419b0fa5113cb8579e3f69bf63c`；调用图 85 TUs / 1,788 APIs / 18,420 edges / 17 callbacks，21 manifest / 25 ownership / 16 census / 19 intrusion。完整身份、失败保留与批次增量见 [multi-dab 验证记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_multi_dab_20260928/README.md)；函数与后续修改见 [S03 / MD1–MD7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01g_multi_dab_and_painter_scope.md#multi-dab-map)。

初轮 focused 的四处失败来自错误准备 phase 和不可达 observer，修订后保留正控制及更直接的中途写覆盖；测试颜色空间的两次构建失败亦保留。完整矩阵绑定最终源码，先前文档定位或定向日志不替代它。

剩余按 MD1/MD2/MD4/MD5/MD6 与 S02–S05/S08–S10 联合推进：默认 stroke owner 的静止启用和寿命、映射后页冲突/读写依赖、producer 完成与 scheduler cut、current/G0/source、其他 painter/iterator/indirect/mask/LoD、实际存储和压力准入。当前没有默认启用持久 freehand，没有取得完整 M6/M7/M8、Fresh 2%、真实 brush 吞吐/尾延迟、Vulkan、TSAN 或 BR1-PERF 新资格。优先级仍为 stroke → undo → 上下文切换。


### S03：实际 dab 页并集与稀疏范围验证（2026-09-28）

真实 multi-dab 消费者改为收集每个已筛选 dab 与 apply/selection bounds 的交集，交给新增 PaintDevice 多矩形入口。普通和 wrapped strategy 沿原适配器转换到 manager-local，保留一次 callback、原 dab 次序、mask/source 和 composite 参数。单矩形旧 ABI 与普通空矩形快捷返回保留；显式 owner 的空集合仍验证目标和原事务。

manager 在原读锁外先验证坐标并构造临时页几何并集，再在原锁内对每个目标页查询一次兼容 tile；页集合交给原 selector/admission/execution，权限仍属于原 owner。没有增加第二份 writer/pending 权限表。范围以与声明矩形相交的页为粒度，不扫描透明像素或 mask 非零像素，同页不同像素仍需同一页准入。

每架构新增 70 项：64 个四种 BPP × 四种 wrap 模式 × 镜像 × standalone/显式 owner 的独立逐像素页映射、像素和 undo/redo 验证；旧式总包围矩形作正控制，必须声明更多页。4 个真实双 worker 用例证明包围框重叠但实际页独立时可同时持有 execution，活跃时 checkpoint 拒绝；2 个普通/wrapped 用例在改完第一页后访问未声明空白页，即使 callback 返回 true，原 operation 仍失败、commit 拒绝、abort 恢复 G0。原错误 owner 用例补充多矩形空/非空声明。

最终 17 CPU/业务目标 × arm64/x86_64 为 **7,006 passed、0 failed、0 skipped**，36 次继承探针、结构门与六项工具自测通过。源码差异 SHA-256 `422ae24b2e8aa084e34fa3965c744ae0a1f722949a482c57140c39d2833fb1b7`；调用图 85 TUs / 1,788 APIs / 18,427 edges / 17 callbacks，结构清单 21 manifest / 25 ownership / 16 census / 19 intrusion，ratchet 未放宽。身份、代码增量和验证见 [稀疏范围验证记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_sparse_ranges_20260928/README.md)；逐段修改和后续责任见 [S03 / SR1–SR7：稀疏写范围](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01h_sparse_write_footprints.md#sparse-range-map)。

该批只消除声明范围的虚假占页。默认 brush 仍用独立 operation；真正共享页的 producer 次序、持久 owner、current/G0/source 与 cut、完整范围/索引/输出和终结存储的预算、压力准备继续。临时 QVector/QRegion/QSet 不具有零分配或已全部计账资格。本批不授予真实 stroke 性能、Fresh 2%、Vulkan、TSAN、完整 M6/M7/M8 或 BR1-PERF 资格；优先级保持 stroke → undo → 上下文切换。


### S03：真实 producer 按页归属分区与透明源合成一致性（2026-09-28）

默认 brush 普通和镜像 jobs 通过原 PaintDevice 映射分区，以原自适应 patch 大小的 manager 网格组织实际 dab 覆盖，边长保持 tile 的整数倍。每个页只属于一个并行 job；绕 wrap seam 的多份画布 clips 归入同一个 job，原 dab 次序贯穿全部 clips。mirror 的输入变换与绘画阶段继续由原 SEQUENTIAL jobs 排序；dirty rects 与原更新节奏保留。临时 QRegion/QHash 不授予访问权，execution 仍由原 admission 取得，默认调用仍为空 owner。

实际 producer 的不同对齐逐字节对照发现 OVER 向量组把透明 source lane 的隐藏 RGB 也写入透明目标，scalar 则不写。pigment 通用构建显式记录各 SIMD factory 对 compositor headers 的依赖，避免最后架构 depfile 漏项使 x86 使用旧对象。RGBA8 的全透明/混合目标分支和 RGBA16/F32 的全透明目标分支现将有效 source alpha 为零的 lane 选择为零 blend，保留目标字节；未忽略透明通道或放宽图像比较。额外开销未以功能测试冒充性能资格。

新增每架构 141 个 painter case：72 组透明 lane/零 mask/opacity/目标 alpha/对齐，64 组四 BPP × 四 wrap 模式 × 四镜像模式的独立逐像素页归属与 OVER oracle（同时检查 128/320 两种 patch、反序执行、undo/redo），4 组全部 jobs 同时持有原 owner execution，1 组拒绝和旧分块共享页正控制。另有 16 组真实 KisBrushOp producer：实际自动笔刷输入与镜像 jobs 在独立线程上执行，同阶段绘画 jobs 全部持有 execution 后才放行；与串行且不同 offset 的输出逐字节一致，drain 与 undo/redo 通过。

最终 19 目标 × arm64/x86_64 为 **7,346 passed、0 failed、0 skipped**，36 次继承探针、结构门及六项工具自测通过；生产插件也完成构建。源码差异 SHA-256 `1e7220d4a6188ef1e6f9ea7bd5f8ef1952269f2d97c4c5c9405d9c8a44f55cda`；绑定 image/pigment/插件/静态库和测试二进制。调用图 85 TUs / 1,788 APIs / 18,429 edges / 17 callbacks；21 manifest / 25 ownership / 16 census / 19 intrusion，ratchet 未放宽。代码与剩余责任见 [S03 / PG1–PG8：页归属与真实 brush jobs](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01i_page_owned_brush_jobs.md#page-partition-map)，全部身份及失败记录见 [页分区验证记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_page_partition_20260928/README.md)。

本批闭合的是默认不可变 dab compositor 的实际共页分区。持久原事务的默认启用、通用 job/current/G0/source、producer cut/显示一致性、完整 job 存储与压力预算、其他 painter/iterator/indirect/mask/LoD，以及 M6/M7/M8、Fresh 2%、真实 stroke/尾延迟、Vulkan、TSAN、BR1-PERF 继续。真实 producer fixture 不等于完整 FreehandStrokeStrategy/scheduler replay；优先级保持 stroke → undo → 上下文切换。


### S03：固定源 cursor、1px 同步镜像与 Alpha Darken 分块一致性（2026-09-28）

scalar `bltFixed` 改为通过原 PaintDevice cursor 合成目标 current，复用 multi-dab span helper。source subrect 与世界坐标 origin 分开，完整 source stride、调用者 opacity/averageOpacity/flow/lastOpacity、通道及 selection 保持原语义；不再读取、缓冲和拷回整个目标矩形。wrapped scalar 写入只处理原 writeBytes 会消费的首周期，避免一页重复合成。该批当时为 bitBlt、scalar fixed 和 PaintDevice-source mirror 新增显式同步 owner overload，旧 ABI 仍为空 owner；显式 owner 拒绝同 manager source，并沿原失败/取消链终结。源与 selection 在 operation body 前捕获，镜像保留 H→HV→V 次序。没有新增 PageStore 权限表或 painter 自持事务。该批的 public 显式 owner 变体已在 §16.21 收缩为 private implementation helper；本段保留当时交付背景。

分块对照暴露 Alpha Darken U16 的旧 scalar/SIMD 舍入次序差异；统一先归一化 source alpha 后乘 mask，并共用同一 ISA 的 alpha 插值运算。整数比较仍为 exact，F32 有限误差 ≤5e-6，不忽略透明 RGB，不关闭 SIMD。此修正统一原本不一致的结果；oracle 使用修正后的 composite，不宣称与修正前所有像素逐字节一致，也没有取得 scalar edge 或整笔绘画的时间收益资格。

新增每架构 375 个 case（343 painter、32 实际 1px producer）：四 BPP、三终结模式、三 composite、mask、四 wrap、source subrect/offset、镜像、跨调用 pending、snapshot、错误 owner、合法 local 页上的极端 world 坐标、第一页真实写后取消，以及 U16/F32 span/alignment 对照。D=1/10/1000 的同段两页 prepare=2、seal=0，真实 freeze 后重写累计 prepare=4。实际 sharpness fixture 证明同步分支和旧镜像算法的像素/undo 一致；它与显式 owner fixture 分别验证，未拼成完整业务 scope 资格。

最终 **19 目标 × arm64/x86_64：8,096 passed、0 failed、0 skipped**，实际笔刷插件、结构门、六项工具自测和 36 次继承探针通过。源码差异 SHA-256 `15a00c31cf4b8d1037b73ade9d0e5831b231b42a2aeafa4f4cc7971346f1aec7`；调用图 86 TUs / 1,788 APIs / 18,436 edges / 17 callbacks，21 manifest / 25 ownership / 16 census / 19 intrusion；原 ratchet 与布局门未放宽。最终实际 Ninja no-op，并复验 image/pigment/插件/静态库/测试与全部 probe 哈希。源码增量、完整失败记录和测量边界见 [固定源验证记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_fixed_cursor_20260928/README.md)，内容—函数—caller—验收关系见 [FC1–FC8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01k_fixed_source_and_sharpness.md#fixed-cursor-map)。

下一段继续 [BC1–BC10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01j_real_stroke_integration.md#stroke-integration-map)：真实 owner/context/job、排队期间 offset/wrap 稳定、current/G0/self-source、producer 完整 cut/dirty 接续、终结与必要资源联合启用，再扩展 fixed-selection/path/indirect/mask/LoD。默认长 stroke 仍未启用；完整 M6/M7/M8、S05/S08–S10 资源与进度、真实 stroke/Fresh 2%/BR1-PERF、Vulkan、TSAN 继续开放，优先级保持 stroke → undo → context。


### S03/C02：原事务与真实 brush jobs 的 target/mapping 复验（2026-09-28）

原 PaintDevice 增加只读 WriteContext 值，捕获原 target/manager/color space、offset、time/LoD/frame 与实际启用的 wrap border/axis。该值由原 transaction/update state 持有并保活 device/manager，不持像素快照、pin 或 mutation 权限。首次持久准入后，apply（含空范围）、重复 begin、checkpoint、commit 均拒绝不匹配；初次准入前的 offset 初始化仍可进行，普通移动事务不受新持久约束。abort 继续经 saved manager 和原 offset 终结，不因当前映射改变而锁死。time/LoD 先于可能惰性创建新 manager 的查询检查。

真实 brush 在 normalization/分区前捕获，普通/镜像写 jobs 在合成前复验，最终 dirty/averageOpacity/性能统计上报前再复验；已失败 job 不上报成功。失败沿原取消链，不能重分区后重放已经开始的工作。等价 bounds 对象、未启用 wrap 的 border/axis 变化不产生假拒绝；实际使用的映射变化才拒绝。值复验不支持执行中并发改 metadata，原 scheduler/caller 仍负责这个稳定区间和 painter/source 设置。

新增每架构 **71 个 case**：40 个显式 transaction context/cut/commit/abort 对照、1 个普通 move/undo/redo、22 个实际 producer 已排队 job 的变化/成功对照、8 个绘画后至最终上报间的变化/成功对照。覆盖映射变化后零像素 callback、空范围与重复 begin 拒绝、恢复后继续、直接 abort、retained reader、painter target 和实际 clone/layout 引起的 manager 变化；late cases 先证明像素已写、worker 尚未报告 dirty，再验证最后上报和取消。没有把各自 fixture 拼成完整 freehand scope 资格。

最终 **19 目标 × arm64/x86_64：8,238 passed、0 failed、0 skipped**，实际笔刷插件、结构门、六项工具自测与 36 次继承探针通过；源码差异 SHA-256 `e8618e8cce3069b5196f3aa9d8199803c7d495bb6372a879551190f591619009`。调用图 86 TUs / 1,788 APIs / 18,440 edges / 17 callbacks；21 manifest / 25 ownership / 16 census / 19 intrusion；原 ratchet 与布局门未放宽。最终实际 no-op Ninja 和全部库/插件/测试/probe 身份已复验。fixture 的链接失败和初轮 late dirty 断言失败均保留，具体代码、源码身份与测量边界见 [目标映射验证记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_write_context_20260928/README.md)，逐段修改关系见 [WC1–WC8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01l_write_context.md#write-context-map)。

本批补齐 BC3 的排队映射值复验；默认真实 brush 仍为空持久 owner。BC1/BC2 的原事务/job 寿命、BC5–BC9 的 current/source、producer cut、终结、必要资源/压力与执行期间 metadata 稳定继续。新增值的引用寿命、容量和每 job 复验成本继续纳入 S10/产品性能评估；完整 M6/M7/M8、Fresh 2%、Vulkan、TSAN 和 BR1-PERF 未新增完成资格。优先级保持 stroke → undo → context。


### S03：原 execution 触页位图与 changed 输出准备（2026-09-28）

cursor/packed 已移除像素循环中独立 QSet 的触页插入。原 execution 复用 BoundEntry 的位置记录位图，≤64 页使用 inline word，更多页按 ceil(K/64) 个 word 由原 MetadataArena allocator 收费；没有复制页键、增加权限索引或扩张 16-byte BoundEntry。成功取得原 write guard 后置位，随原借用终结。changed 输出先于范围借用准备为唯一 buffer；Qt reserve 后检查实际容量，拒绝不进入 body。callback 成功且 guard 归还后，先从原绑定导出 changed，再 finish execution/batch，最后交换已有输出；旧 caller buffer 在 cleanup 释放。

新增每架构 161 个 case，覆盖四 BPP、K=1/9/65/257、重复/稀疏/空/拒绝、持久/独立 owner、共享旧输出、packed partial/full/no-op、pending/旧快照逐字节一致与真实 8 MiB 元数据拒绝及重试。每架构 192 次暖 pending operation 的 body/export/delivery 区间均为零分配/释放；冷 materialization、finish/cleanup 与 manager 后续刷新不在该结论内。每架构逐点扫描 834 个实际分配拒绝和 16 个成功对照，拒绝均不执行 body，原 pending/owner/预算和后续正常重试成立。

首版额外页键表导致原共享 resident 限额场景失败，范围 phase 重复计数导致原稀疏范围断言失败；已改为位图与独立 preflight，原预算和断言未放宽。Qt 空容器 reserve 静默保留零容量的反例已补实际容量检查；探针持续拒绝模式误伤异常运行时的失败记录也保留，最终改为逐次仅拒绝一个目标分配。

最终 **19 目标 × arm64/x86_64：8,560 passed、0 failed、0 skipped**；实际笔刷插件、结构门、六项工具自测及 40 次探针通过。源码差异 SHA-256 `fe5286f8f7140711d47f0cc918241cbcb6ba5beaf4a2b5470d88fa15daa91188`；调用图 86 TUs / 1,791 APIs / 18,525 edges / 17 callbacks，21 manifest / 25 ownership / 16 census / 19 intrusion。最终实际 Ninja no-op、库/插件/静态库/测试/probe 身份与 git diff 检查通过；ratchet 与布局门未放宽。具体修改关系见 [OP1–OP10 及 OP2 实施表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#operation-storage-implementation)，完整同源证据和失败记录见 [触页/输出准备验证记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_operation_storage_20260928/README.md)。

OP1 范围转换、OP3–OP5 的 presence/wrapper/hash 插入与回收/extent、OP6/OP7 的 publication/cut、OP8 旁路及 MR4 exact 失败恢复、OP9 完整共享预算与 Qt 输出计账、OP10 产品性能继续。默认真实 brush 仍无持久 owner，BC1–BC10 联合接线、完整 M6/M7/M8、Fresh 2%、Vulkan、TSAN、BR1-PERF 未获新完成资格。优先级保持 stroke → undo → context。


### S03 / OP3 与 S02：presence 存储前置及准入捕获复验（2026-09-28）

默认 cursor、packed write、native clear、precise/rough copy 五个入口现在原 manager operation 中持有 presence scratch，由既有 backend 在像素执行前准备；≤64 页 inline，更多页一次 K 字节分配。cursor 使用声明页并集，矩形入口按原遍历计算容量。写后私有 metadata 查询沿原 selector/publication gate 填已有存储，不 capture、不 pin，整组成功才刷新；公共查询失败保持旧输出及共享者。显式 history pending 继续消费原 touched 结果，已知 legacy Borrowed 不新增该准备。overflow 的完整计账与 history 终结存储仍待继续。

首轮完整矩阵为 8,751 passed / 1 failed：真实 brush 分区准入在空存储分配期间被无关 claim 变更耗尽准备次数，body 未执行。确定性交错探针复现后，原 admission 改为在实际复制当前记录时绑定 revision，并验证新容量；复制后的变化仍严格拒绝。allocate/build 后重新复验原请求，可直接使用其他线程已扩好的原表；最多三次候选准备保持不变。真实冲突、operational=false、foreign owner、容量不足、旧几何及旧 claims 保护继续验证。没有新增 queryable 表或延长重试上限。

最终 **19 目标 × 两架构：8,754 passed、0 failed、0 skipped**，46 个 final-02 探针、双架构 640 个真实 producer 分区场景、结构门、六项工具自测和实际最终 Ninja no-op 通过。源码差异 SHA-256 `025c7bf2bada420c45598ecfa4d4e18d428ffa9a9c73b999bff13d15215a2a81`；调用图 86 TUs / 1,794 APIs / 18,640 edges / 17 callbacks，21 manifest / 25 ownership / 16 census / 19 intrusion。原 DataManager intrusion=21，ratchet 与布局门未放宽。新增每架构 96 个 presence case、1 个 admission case；实际准备/查询与存储拒绝分别测量，不外推完整 stroke 性能。初轮失败、fixture 与 probe 修正、三次结构图及最终身份均保留在 [本批证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_presence_storage_20260928/README.md)。

待改内容与代码关系见 [OP3 实施表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#presence-storage-implementation)和 [J1/J2/J3 捕获时复验](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-capture-revalidation)。下一段继续 OP4/OP5 的 wrapper、hash 增删/回收、extent，联动 OP6/OP7 的 publication/cut/终结、OP8 旁路与 MR4 exact 恢复、OP9 全部实际计账与共享父额度。默认真实 brush 持久 owner/current/source/producer、完整 M6/M7/M8、Fresh 2%、Vulkan、TSAN、BR1-PERF 仍开放；顺序保持 stroke → undo → context。


### S03 / OP5：原 extent 双轴容量写前准备（2026-09-28）

原 extent 扩容不再先修改活动 capacity/offset 再分配。原 Data 的 Growth 只持真实 buffer 和几何；64 位临时量验证 span/容量/偏移/字节，双轴分配成功后才在原 migration gates 下复验并复制当前计数。分配期间没有计数快照，当前几何已覆盖目标时直接复用；候选不适用时最多准备三次，最后只检查原容量。旧 buffer/未用候选在原 extent gates 外释放，不改变唯一 count/min/max/currentExtent 责任。

原 manager 的 cursor、packed、clear、precise/rough copy 及显式持久 cursor 在像素前准备轴容量；packed 在释放 manager gate 后扩容。cursor 使用原页并集边界确定稠密轴容量，没有扩大实际写页。准备不改变 visible extent；拒绝返回原 Failed/failure context、无像素 body。notifyTileAdded 先保证双轴再改计数，replaceTileStats 在清原统计前准备完整边界。原 takePrepared 仍要求调用者排除并发结构替换，容量不是权限。

每架构新增 50 项测试，包括八 worker × 1,000 次准备/增删、极端坐标与候选失效，以及四 BPP × 正负远坐标 × 六实际路径的完整页/旧 view/undo/redo/删除。实际 allocator 探针每架构拒绝两轴分配共 96 点、48 个成功对照，核对原 buffer/几何/extent、generation/事务/预算不变与正常重试。初始冷扩容为 2 次分配、12,288 B、2 次旧 buffer 释放，1,000 次暖准备增删为零分配/释放；计数变更或更大几何插入的确定性交错仍保留当前状态。所有结论只覆盖 extent 准备与既定增删调用，不覆盖 map/GC、payload 或整体 stroke。

最终 **19 目标 × 两架构：8,854 passed、0 failed、0 skipped**，48 个最终探针、结构门、六项工具自测和实际最终 Ninja no-op 通过。源码差异 SHA-256 `a8c44c0b58d67b79be406ab4f0106a2e83c211fb7a56c6ab05b926c1aeaf7f03`；调用图 86 TUs / 1,794 APIs / 18,659 edges / 17 callbacks，21 manifest / 25 ownership / 16 census / 19 intrusion。原 ratchet 与布局门未放宽。探针 header/exception runtime 计数失败与最终身份均保留在 [本批证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_extent_storage_20260928/README.md)；代码与剩余责任见 [OP5 实施表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#extent-storage-implementation)。

暖准备增加两个原 migration read gate 的固定检查，冷扩容仍复制 O(axis capacity)；真实 stroke 性能须正式验证。OP5 的边缘删除扫描、clear/destructor 工作预算、OP4 wrapper/map/GC、OP6/OP7 最外层 publication/cut/终结、OP8 raw/planar 与 MR4 exact 恢复、OP9 retained/peak/shared-parent 计账继续。默认真实 brush 联合 owner/current/source/producer、M6/M7/M8、Fresh 2%、Vulkan、TSAN、BR1-PERF 仍开放；stroke → undo → context 优先级不变。

OP4 的 map 局部回收链现已接线，具体代码、已验证范围和剩余责任见 [OP4 局部回收实施表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#hash-reclamation-implementation)。原 QSBR 节点先准备再入队，migration 内嵌回收记录，lazy 插入跨 redirect 保留 winner；clear/析构与 raw 引用异常责任已分开。完整 operation 的结构容量、通知、publication 和预算仍未闭合；M6/M7/M8 及 BR1-PERF 继续。

### S03 / OP4：局部 map 回收准备

[本批证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_gc_preparation_20260928/README.md)绑定源码差异 `5d9b13f15d937d47839d1fd9610a7d5a873aa757d0029977f8f7acb25fd05c6e`、20 个目标 × 双架构 8,884 项及 50 个最终探针。每架构 35 次实际分配拒绝和 3 个正控制覆盖替换/删除/clear；prepared 入队区间零分配/释放。真实迁移竞争对照证明原 exchange 会替换 winner，新增 insert-if-absent 保留它。结构门未放宽。

本批仅闭合局部 map 引用转交和必要回收落点。HX6/HX7 的真实结构安装能力、原 operation 首字节前全资源、通知/外层 gate/完整预算和默认长 stroke 联合接线继续；M6/M7/M8 与 BR1-PERF 未完成。具体代码与待改段见 [OP4 实施表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#hash-reclamation-implementation)。


### S03 / OP4：HX6 迁移失败协议、HX8 接线与当前验证缺口

实现与待改段见 [HX6/HX8 实施表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#hash-migration-storage-implementation)。实际表／迁移候选先准备再转交；overflow 后继失败保留源表和部分目标并唤醒同 job 重试。worker load/CAS 失败采用 Acquire 观察复制结果；get/erase 解析现有迁移内容，静止析构处理部分迁移。TileDataStore 注册失败由 RAII 释放未发布候选；swap-in 在原排他区间内先准备实际 cell，处理空 hash 已 Redirect，再消费 SSD。该能力仍不构成跨 job 安装凭据。

[本批证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_map_migration_storage_20260928/README.md)绑定源码差异 `e809ed039190e4bbc0a6b653653b67325d2761de666bb580a2dbd3e347b73830`。54 个最终探针全部通过，包括每架构 map 44 次实际拒绝＋3 个对照、TileDataStore 五入口 45 次拒绝＋5 个对照，另有实际四 worker 迁移失败后的推进场景。结构门保持 87 TUs / 1,794 APIs / 18,809 edges / 17 callbacks，21 manifest / 25 ownership / 16 census / 19 intrusion；未放宽原门槛。最终 Ninja no-op，源码与所用库身份一致。

**该批初次矩阵未通过：8,891 passed、1 failed、0 skipped，超时终止的进程另有四项未执行。** ARM64 的 `stressTestExtentsColumn` 出现 extent 读写锁全员等待；原采样、LLDB 和超时记录保持不变。当时单次场景与三个独立程序未复现，因此没有豁免。后续使用原调度形态的重复测试和纯 QtCore 程序复现负 reader 计数，并完成下节的依赖修复和完整矩阵；此处的失败是保留的原始记录。

锁等待与缺失矩阵现按下节关闭；下一步继续 HX6 跨 job key/结构预留、HX7 原 manager/table incarnation 与 operation 候选、OP6/OP7 联合发布、HX9/S10 实际峰值／通知／维护预算。默认长 stroke、两种 hash、完整 allocator 故障及 M6/M7/M8、BR1-PERF 继续开放。文档校验和本次开发回归不授予这些阶段资格。

### S03 回归收口：QtCore 锁计数修复

原安装 QtCore 和独立 QtCore 计数器程序均捕获 `readerCount=-1`，无持有者而所有 worker 等待；原版 v6.8.0 源码构建也复现负计数。同源码只加入上游 `80d01c4`、`4fd8801 / QTBUG-142321` 的两处 acquire 同步后，独立程序连续 1,000 轮通过。修复针对 private freelist 对象复用后的发布同步，不改 extent 的并行访问协议。

随后从固定 Krita Qt 6.8 fork 重建 Core，保留现有 compressor 与编译器兼容补丁；421 个源头文件、三个生成配置头和两架构导出集合与原安装相符。最终库 SHA-256 为 `cd0a48d2948af55889625ae0750a7d08895068deae9b6e85bdc3e1fac6dc9434`，原 framework 已备份。依赖重建来源明确记录，不冒称恢复了旧库的完整构建来源。

[最终证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_extent_lock_audit_20260928/README.md)在同一产品源码差异 `e809ed039190e4bbc0a6b653653b67325d2761de666bb580a2dbd3e347b73830` 和相同产品二进制下完成：Qt 自身锁测试每架构 24 项、真实 extent 每架构 1,000 次、完整 20 目标 × 双架构 8,896 passed / 0 failed / 0 skipped、54 个最终故障／分配探针。结构门与末次 Ninja no-op 通过；原 8,891+1 的失败矩阵保持冻结。源码—消费点关系见 [01n §8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#8-本批回归暴露的-qtcore-锁依赖)，重建与恢复方法见 [依赖构建记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_extent_lock_audit_20260928/qt-build-recipe.md)。

本次恢复的是当前工作树的开发回归资格，未新增跨 job 安装能力或正式性能证据。新旧 Qt 使用不同编译器，后续基线和改动必须统一到同一运行库重测；不得直接继承旧库的性能比值。M6、M7、M8 与 BR1-PERF 状态不变。


### S03 / OP4：HX6 预留 key、迁移兼容与关闭寿命

原 ConcurrentMap 以 opt-in 标签记录保留 key 的结构能力；同 key token 共享原 cell 的逻辑值，迁移转交同一记录地址。安装只消费短 key gate 和已存在存储，不调用 insertOrFind/participate，不持 raw 或整表锁跨 kernel。最后 token 释放恢复普通 cell，原 QSBR grace 回收真实记录；allocator 与收费 owner 的寿命可延续到最后实际 free。普通 map cell 仍为 16 B，默认 allocator 记录为 136 B；通用非 opt-in map 保持原表示。

原 Mutator/get/iterator 已解码，逻辑空预留不会提前添加 tile 或通知。hash 析构先撤销预留再 drain；map close 仍要求普通用户和迁移 worker 静止，允许 token 并发收尾或晚释放。旧 token 不再依赖死表，地址复用不恢复资格。key gate 可能因抢占等待，本批没有锁自由或尾延迟承诺。

[当前证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_prepared_keys_20260928/README.md)绑定源码差异 `a101246c6d4c827c298964b992bcc148f9e7395bf085b410802d1a006dd9ec8d`：20 个测试目标 × 双架构共 **8,912 passed、0 failed、0 skipped**，56 个最终探针通过；新增 key 探针每架构 43 次实际拒绝及 3 个正控制，失败迁移中的安装/释放 calls/frees 为 0，root/job 不推进，最终实际 tracked blocks 为 0。调用图为 87 TUs、1,794 APIs、19,169 edges、17 callbacks；原侵入与布局门未放宽，最终构建 no-op。QtCore 沿用上一批已验证库。

逐段修改关系与并发状态见 [HX6 §9](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#prepared-key-implementation)。**生产 manager/brush 尚未调用 prepareKey**；下一步 HX7 原候选、OP6/OP7 联合 canonical/adapter 安装，配套 HX8 双配置及 HX9/S10 全资源收费/维护。该记录没有逻辑 writer、tile payload 或 provider pin 权限，不新增 PageStore authority。M6/M7/M8 与 BR1-PERF 继续开放。


### OP6 / HX7 接线约束：原 admission 与 borrow 延续至 adapter 交付

本批修正前，`runCpuMutationOperation` 在 manager 刷新之前结束原 session／execution，留下同页后继或 history checkpoint 提前进入的窗口。本批现让**原能力延续**，具体代码、锁序及剩余修改见 [AD1–AD6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#adapter-delivery-implementation)；HX7 写前候选继续，不能用新增 key 权限表或每 dab 新建预留记录弥补生命周期缺口。

普通 cursor／packed 写使用原 WriteBatch 的同一个 mutation session：seal 后不可再写，事务 activity 正常结束并完成原 commit；原 ClaimSet 与其唯一 write set 留到 manager 索引交付后随该 batch 析构。显式 history 交还的仍是原 execution，manager 完成 pending 索引刷新后才 finish；checkpoint 仍由原活跃借用排斥。所有权、writer 身份、预算 controller 及失败取消链不变，没有复制 target 权限或 pending。

本次允许 `libs/image/tiles3/kis_tiled_data_manager.cc` 的现有 PageStore 标识出现数由 **21 → 23**：两处局部 `unique_ptr<原 WriteBatch>` 分别接住 cursor 与 packed 的完成对象；direct includes 保持 3，相关 PageStore 类型集合不增加。history 同步函数另持原 execution 的 move-only 值。这些都是原有堆对象的局部持有句柄，不新增 manager 常驻字段、容器、TLS 或 heap allocation。原 session 布局和 metadata record 上限不变；被保留的 write set 继续按原 budget 实际存活时间收费，manager gate 释放后才销毁。后续 HX7/OP6 共用候选接入时合并这些原有交付持有点；删除适配时随调用者一起删除，不能为通过计数而改名隐藏。其他侵入／布局门槛不变。

持锁 legacy 准入现必须即时拒绝冲突：`reserveLegacyMutationPage` 的 caller 可能已持 tile swap barrier 或 manager gate，原 writer 交付索引正需要这些 gate，故不能等待。已取得同一 session claim 的嵌套访问仍复用；已迁移的 setPixel/tryWriteData 消费者在冲突时不返回旧 cache 的可写指针，借用 packed 的比较也先处理获取拒绝；仍直接使用 raw data 的旁路不据此视为已迁移。已写的兼容 batch 沿原取消和 exact 恢复链处理，不在写后改走另一路。managed 范围等待仍在取得 tile/manager gate 之前。该改变是明确的兼容失败契约；它不构成 legacy job 的自动重试或 scheduler continuation，后续 OP8/BC4 迁移仍须闭合。

本批已验证 delivery 前 managed 同页后继阻塞、独立页推进、history checkpoint 拒绝、setPixel/planar/borrowed packed 冲突即时返回和取消、能力释放后的恢复，以及拒绝／空操作／无转交分配。本项不证明 wrapper/通知已写前准备，也不解决全部 canonical/index reader 的联合发布、旁路或 M6–M8／BR1-PERF。


[最终同源证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/README.md)绑定源码差异 `c57edb423118c85e851a0962a3a936463df61b9bb11c6202f68a8820489f5d45`：20 个测试目标 × arm64/x86_64 **9,006 passed、0 failed、0 skipped**，58 个最终探针通过；其中每架构 192 次原能力转交的实际 allocations/frees 为 0，正控制各 1 次 / 8,210 B。仅覆盖 ChangedDeliver → Cleanup，不外推 manager 安装、seal 或完整 stroke。调用图为 87 TUs / 1,796 APIs / 19,239 edges / 17 callbacks；21 manifest / 25 ownership / 16 census / 19 intrusion；本节明确核准的 manager 标识 21 → 23 之外，其他侵入与布局门不变。QtCore 未变，实际最终 Ninja no-op、库/插件/测试/probe 身份与差异检查通过。

首轮完整矩阵 8,930 passed / 76 failed 及新增 borrowed packed 的 SAFE ASSERT 保留：修正原同线程重入原因和实际比较的可失败获取后，重新冻结源码并执行完整矩阵和全部探针。未忽略断言或放宽像素/取消测试。新增每架构 47 项 case；具体生产函数、共用 caller、取消终点和下一批领取位置见 [01m §10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#adapter-delivery-implementation)。下一批继续 HX7 原 operation 缺失资源、OP6/OP7 联合发布、HX8 双配置、HX9/S10 收费/维护，再联合真实 brush；完整 M6/M7/M8、Vulkan、TSAN、Fresh 2% 和 BR1-PERF 未完成，stroke → undo → context 优先级保持。


### S03 / HX7：缺失 wrapper 候选、原准入内 extent 与交付边界

本批将原 cursor/packed 的缺失 wrapper、map key 与 map 持有引用移到原 admission/execution 内、像素 body 前；暖已有页不创建 key record。原 claim 同时约束 clear、history commit/abort 与 restore 的锁外准备后复验。`PreparedTileUpdates` 只有本次缺失页的局部候选，两个 hash 的 candidate 仅绑定存储 incarnation，不拥有 PageStore 写权限。链表实现首次冷准备增加一个惰性 shared identity；锁自由实现复用原 PreparedKey；两者取消和旧表关闭后的释放都不访问旧 table。完整实际预算、联合 root/index 发布和 semantic/restore 候选仍待收口，不能从局部准备推导 M7 资格。

**侵入审查：** `kis_tiled_data_manager.cc` 的现有 PageStore 标识数 **23 → 25**，来自 cursor 适配安装在原函数内显式使用既有 diagnostic phase/timer；原 `refreshPageStorePages` 的计时仍服务其他 caller。类型集合和 direct includes（3）不变，manager 无新常驻字段或 TLS。接受这两处可见诊断依赖，不改名规避审查；随适配消费者删除而删除。其他侵入／布局上限不变。代码审查范围由下述最终同源验证约束，不授予完整阶段资格。


[本批同源证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_candidates_20260928/README.md)绑定源码差异 `7c5e6e2e96f5e56c2325ed74c78184cb12da058749910bce19be0aaa7881523a`：20 目标 × 双架构 **9,034 passed、0 failed、0 skipped**，62 个最终探针通过。每架构真实 manager 安装 192 次、暖准备 144 次 allocations/frees 为 0；510 个真实 allocator 拒绝及 9 个成功对照保持首字节前拒绝、之前笔迹、重试与最终候选释放。原 extent 准备也已进入原 admission，准入前 abort 替换 table/extent 的两条 native 回归通过。完整失败矩阵 9,014 / 16 和修正原因保留。

调用图 87 TUs / 1,796 APIs / 19,296 edges / 17 callbacks，21 manifest / 25 ownership / 16 census / 19 intrusion；仅本节明确审查的 manager 标识 23 → 25，其他侵入／布局门不变。QtCore 未变，最终库/插件/测试/probe 身份和实际 no-op 已复验。具体修改、后续函数与拒绝终点见 [HC1–HC7：缺失候选、原准入与下一批代码](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#adapter-candidate-implementation)。OP6/OP7 联合可见性、其他语义/终结候选、完整实际预算与 OFF 产品配置、真实 brush owner/current/source/producer 继续；M6/M7/M8、Vulkan/TSAN、Fresh 2% 与 BR1-PERF 未完成。


<a id="joint-publication-implementation"></a>
### S05 / OP6 当前批次：overlay 安装存储与联合发布边界

[JP1–JP8 指南](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/02a_joint_publication_boundaries.md#joint-publication-map)将实际 reader-window、原 session/transaction 和每个读取入口对应到下一段代码。真实 manager 探针已观察到 seal 后“新页 / 旧 canonical extent / 旧 adapter”，以及 commit 后“新 canonical / 旧 adapter”；这些窗口仍待外层联合发布关闭。

JP1 原 `PreparedTransactionState` 保持唯一可查询 delta，proof/removal 改用可转移实际节点的容器；原 transaction 索引保存同一状态的标准共享指针，候选保活它并承担并发 bucket insertion 的实际预留。两个 atomic 仅允许候选取消在 owner gate 外归还容量，不表示页面权限或另一套 pending 选择。新增节点按缺失项准备，暖 proof 原位替换；被摘下的节点锁外释放。原分配式安装 helpers 已删除，seal、generic publish、条件删除共用原 aggregate。准备留下的空状态不能被当作 semantic delta 提交。

架构 guard 的 R1 文本契约随实际存储形状从 `QHash<quint64, PreparedTransactionState>` 更新为 `QHash<quint64, std::shared_ptr<PreparedTransactionState>>`，并显式检查原 `ProofMap` / `RemovalSet` 与两类容量计数；禁止平行 prepared side-map 的规则保留。没有新增 manager 字段、TLS、页面 authority，也没有上调现有 manager 25 标识 / 3 include 或任何布局上限。原 state/control block、节点与桶的完整 budget 收费仍是 JP8 责任，不能从容器资格推定硬预算达标。

本批源码差异 `c1c6f145e69d6e841fb15c5873ea23db49da681f31ddc66f33b6530fd1ae3c2d` 已完成 **9,154 passed、0 failed、0 skipped，66 个最终探针通过**。每架构 96 次 overlay 安装 allocations/frees 为 0，627 个真实准备分配拒绝与 12 个成功对照通过；追踪块/字节在退出后归零。新增 60 个 case / 架构；完整图为 87 TUs / 1,800 APIs / 19,382 edges / 17 callbacks，架构检查 21 manifest / 25 ownership / 16 census / 19 intrusion。QtCore 不变，库/插件/测试/probe hashes 与最终实际 Ninja no-op 已复验。[本批同源证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s05_joint_publication_20260928/README.md)。此前 9,034 / 62 probes 仅适用于前批冻结身份。准备/清理仍需移出外层 gate，extent/default/current/raw 观察边界、checkpoint/history/restore、真实 brush owner/current/source/producer、OFF 产品配置、完整预算、M6/M7/M8、Vulkan/TSAN/Fresh 2%/BR1-PERF 继续开放。优先级仍为 stroke → undo → context。

<a id="br1-convergence"></a>
## 16. 批次结束后的收敛裁决（2026-09-28）

> 本节保留各批次的原始判断与索引。涉及当前产品、领取顺序与性能价格时，先核对[§1](#native-cpu-baseline)和[证据适用范围](README.md#evidence-scope)。

本节统一当前结论与下一批范围，当前收敛行动与候选状态见 [§16.12](#convergence-action-plan)，最近已冻结的生产交付为 [§16.14 packed/cursor 联合 adapter 窗口](#joint-adapter-window-delivery)，copy 子项见 [§16.13](#copy-bounds-convergence)，既有 fresh raw 修复见 [§16.8](#fresh-read-implementation)；§15 各批记录继续绑定各自冻结源码，不把早期“下一步”累加成当前任务。实施和停止规则见 [收敛与统一验收指南](br1_modification_guide/CONVERGENCE.md)，实际已执行的审查见 [收敛审查记录](evidence/br1_convergence_review_20260928/README.md)。本节不改变 §2–§14 的语义、资源或正式门限。

### 16.1 JP1 检查点已核验的事实与资格

- 产品 HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`，包含未跟踪源码的差异 `c1c6f145e69d6e841fb15c5873ea23db49da681f31ddc66f33b6530fd1ae3c2d`。与最后 JP1 批一致，28 个构建/运行文件 hash 一致；原批矩阵为 **9,154 passed / 0 failed / 0 skipped，66 个探针**。本次核对了既有记录，没有重跑或扩大原批资格。
- JP1 的 overlay 实际节点/桶安装能力成立；原窗口探针仍报告 fresh current、canonical extent 和 adapter 的不一致。原 captured view 保持旧版本是正确语义，不与 fresh current 的陈旧缓存混为一谈。
- 原 history/memento 有显式 session，cursor、multi-dab、页分区等已有消费者；默认 brush `addDabJobs` 仍向 `bltFixed` 传 `nullptr`。当前不能称为默认持久 stroke 完成。
- 本次实际构建 FreehandStrokeTest/Benchmark，运行所选 `testAutoBrushStroke`，arm64/x86_64 各 **3 passed / 0 failed / 0 skipped**（含 init/cleanup）。这是原业务入口 smoke，不是 persistent-owner 整链、性能资格或新全矩阵；与 9,154 项分开报告。
- 固定 upstream 对照仍为 `9a24ae0d8c070884fb013594191002e1a1b39a19`。当前没有本次核验通过的同依赖 upstream 性能二进制；修复 Qt 下真实 stroke 对照、Fresh 2% 控制及完整阶段/正式性能证据仍待取得。OFF 完整产品配置、TSAN、Vulkan 证据不能由 ON 的 CPU 测试推定。

### 16.2 有限阻塞清单与下一步

| 责任 | 当前缺口与实际端点 | 下一批/后续的有限完成判据 | 所阻塞的出口 |
|---|---|---|---|
| S04/S05，JP6，联动原 JP2/JP3/JP5/JP7 | JP4 canonical 页/extent 已联合；JP5 fresh raw 已修复；§16.14 已关闭普通 packed/cursor add 的 32 个冷页联合观察点；delete/default/copy/restore/purge 的发布族与部分实际 bounds caller 仍未统一 | 保持整体 reader-window、旧 captured/raw、pending/intent 与进度断言；逐发布族确认是否需要同一 completion，禁止用只增 union 掩盖删除；同链 prepare、finish/cancel 保持唯一责任 | 剩余发布族影响首条 direct 链时先闭合，否则转真实 owner/显示/finish/cancel/drain；S05 完整资格仍开放 |
| V01/BC10 | 真实 freehand 入口可运行，但缺 owner/display/终结共同断言及相同 workload 的 upstream 对照 | 从原 strategy 接实际 brush/jobs/更新；断言模式和 owner 寿命，补 finish/cancel、旧模式控制、源码/运行库身份；再补同依赖 upstream 构建与分段测量 | 整链/性能结论；**现在开始，作为联合接线的验证入口** |
| BC1–BC7，S01–S05 | 默认 owner/current/producer cut/finish/cancel 尚未一起启用 | 先以 direct/common、单设备、无 wrap/LoD/indirect/mask 的显式开发/测试入口闭合初始化到 drain；初始化前资格选择，禁止半笔 fallback | 指定入口可用性；窗口语义闭合后联合验证，不等待所有可选微优化 |
| BC9、JP8、HX8/HX9、S08–S10 | 完整必要存储收费、pending 窗口、压力接续、无新输入 drain、双 hash 产品路径与维护界限仍缺完整证据 | 保持 §9.5、§10 的预算/进度要求；实际分配、共存峰值、慢 reader、多文档、取消/close 均有结果，不能只测入队零分配 | **默认启用前必须闭合**；测试入口先行不授予资源资格 |
| JP3/JP7、U01/U02、BC8、C01/C02 | 外层短 gate、其余终结/恢复、多模式与上下文全覆盖仍待完成 | 首条链直接调用的端点现在联动；全量 undo delta、多模式与 context 依原优先级分批；正式门仍按 §2–§14 | 完整 M8、BR1 总出口；不能拿首条入口覆盖替代 |

领取实现批时只选上表的可观察结果并列实际调用端点。新增前置必须说明违反的契约或复现、阻塞入口和停止条件；纯潜在性能收益进入后续清单。JP 的全部函数映射仍见 [02a](br1_modification_guide/02a_joint_publication_boundaries.md#joint-publication-map)，它是责任库存，不意味着一次性扩展所有子项。

### 16.3 代码质量与统一交付的裁决

主干已有整笔事务、共享 tile 首写 COW、重复写复用与异步 batching；本项目必须区分新增保证、恢复这些效率、真正减少原工作量。当前局部验证较充分，整链收益仍未证明，不能用新增测试数量抵消已知可见性缺口。JP1 检查点未提交生产源码净增 7,809 行、测试净增 11,001 行；最新规模见 §16.8；生成审计数据分列，此统计不是全项目相对 upstream 的增量或质量分数。

定点并发审查未确认新 race 缺陷，但新增 prepared-key 的自旋及继承自 upstream 的 QSBR 强制等待/整链回收均不提供整体延迟上界；静止关闭是明确前提。默认启用的资源/进度证明必须覆盖实际调用链。无新反例时不额外启动容器重写。

读取政策已按 [§16.10](#read-selection-convergence)合并；继续按 [§16.9](#api-convergence-plan)，adapter/交付在 JP6 联合修复中收束，owner/结果分支随真实链接线合并；仅依赖模式迁移的外部 API 删除后置。删除旧路径须证明静态及运行时消费者已迁移。每批完成既定检查后冻结并结束，只有新契约失败才重开；实际命令、身份、测量范围和剩余项使用 [统一模板](br1_modification_guide/CONVERGENCE.md#delivery)。当前导航只链接本节，不再多处追加不同计数的“当前验证”。

### 16.4 收敛目标与改动清点的执行约束

[收敛目标与改动清点](br1_modification_guide/CONVERGENCE_CHECKLIST.md)将本节的有限阻塞落实为可领取的函数范围、必要断言及保留/修复/合并/条件删除/暂缓判断；[逐文件清点](evidence/br1_convergence_inventory_20260928/inventory.md)覆盖 JP1 检查点相对 HEAD 的 124 个范围内改动文件，含 6 个未跟踪源码。重新核对的产品身份和原 28 个构建/运行文件未变；本轮没有新的产品运行或阶段资格。

本轮实现的目标出口是：**发布窗口关闭 → 首条真实 direct stroke 的 owner/写入/显示/finish/cancel/drain 共同验证 → 在扩大模式前完成接口责任收敛**。此处保留早期目标记录；接口合并的当前执行时机已由 [§16.9](#api-convergence-plan)修正为随修复和接线同步交付，仅条件删除后置。验证 harness 可与发布修复同时准备。尚未满足完整资源/进度和性能条件时，结果只记开发入口通过，不能默认启用；M6 → M7 → M8/39 不变。

接口审查已按 §16.21 删除 painter 只有测试外部调用的 public owner overload；后续仍沿原 owner 收敛，不预造新通用框架。backend 的 `historyOwner/completedBatch/completedExecution/prepareAdapter` 合法组合及 packed/cursor adapter 共同交付已按 §16.14 收敛。job 错误桥、legacy/standalone 分支及普通 restore 的全量 rebuild 仍有实际消费者，**这些路径目前没有取得立即删除的依据**；条件删除按清点中的 caller/trace 和语义证明执行。

真实 freehand 的模式命中、读选择和发布一致性使用精确断言；原图像 fixture 的容差只覆盖其既有比较范围，不能代替这些断言。所有新增前置继续按 §16.2 的真实阻塞规则领取；达到已登记结果后冻结该批，不因尚有可选微优化而持续扩展。

本次继续核对 `StrokeTester::testOneStroke` 的实参后修正前轮模式判断：`indirectPainting` 已不控制执行，direct/indirect 来自 preset；benchmark 关闭普通更新，但其旧注释不能证明实际 indirect。前次 smoke 的通过事实保留，双模式覆盖或 direct 性能均未取得。现行 [V01](br1_modification_guide/07_validation_and_migration.md#freehand-convergence-validation) 和清点已更正，旧冻结记录不覆盖；首个验收配置按清点固定到 RGBA8/OVER/普通 autobrush 分支并作 runtime 断言。

<a id="jp3-commit-preparation"></a>
### 16.5 JP3 匿名 root 成功清理的读进度收敛

本批只关闭 `finishOwnedTransaction` 在 root 已安装成功后的 cleanup 阶段仍阻塞 backend reader 的问题。最终改动与撤回项见 [收敛清点 §8](br1_modification_guide/CONVERGENCE_CHECKLIST.md#jp3-delivery)，锁序与生命周期见 [02a §8](br1_modification_guide/02a_joint_publication_boundaries.md#commit-preparation-implementation)，源码身份、运行结果和失败样本见 [本批证据](evidence/br1_s05_commit_preparation_20260928/README.md)。§16.1/§16.4 的 JP1 身份和规模是改动前冻结记录，不能继续代表当前产品二进制。

原 preparation、selector、重试和失败语义保留。backend 把原 publication RAII 锁通过 Store 私有入口借给 coordinator，成功 root/metadata 安装后先释放 Store owner，再释放 publication 锁，随后清理；transaction mutex 仍串行最终 writer。没有新增事务、selector 回调或长期候选状态。测试断言 cleanup 期间新读能完成、字节和 extent 正确，旧 captured view 保持原字节。

两项候选已经撤回：固定三次拒绝破坏原独立页/产品并发提交成功；把全部 root 准备放到 publication gate 外则在持续 reader 下出现超过原 10 秒进度断言、隔离复查 45 秒超时。配套重复 prepare 和额外 selector/取锁状态也不进入最终产品。失败样本保留为后续进度设计的约束。锁外准备候选另有一次区间内 free，不能移用其局部零值结果宣称完整 gate 资格。

最终身份为 HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`，含未跟踪源码差异 `fd89833d8f20e5532b9f184f8d77e3c16199e3adb3e2646163eef36fa7e14220`。原 20 目标 × arm64/x86_64 合计 **9,186 passed / 0 failed / 0 skipped**；架构 gate、6 项 reachability 自测、最终构建 no-op 及源码/运行库身份检查通过。另有 12 次针对性回归探针通过、2 次已知 reader-window 缺口复现；后两次不能记为一致性修复。本批相对 JP1 的生产净增为 24 行、测试增加 85 行，生成审计另列，见 [最终文件清点](evidence/br1_s05_commit_preparation_20260928/inventory-final.md)。

下一实现主线仍为 JP2/JP4/JP5/JP6 的 page、extent/default、fresh current 与 adapter 联合可见性。准备外移须先处理持续读下原 owner 的提交进度和拒绝接续；history/checkpoint/abort/restore、完整资源、真实 freehand owner/display/finish/cancel/drain、同依赖主干对照、Fresh 2% 均保持开放。默认启用与 M6/M7/M8、BR1-PERF 资格不变。


<a id="jp4-overlay-extent"></a>
### 16.6 JP4：canonical 页与派生 extent 的联合安装

本批关闭冷页 seal 后“新 canonical 像素 / 旧 canonical extent”。Tiles3 在 Store 初始化时配置不可变派生 surface 策略；原 overlay 候选在最后取得 owner 锁后，合入最新 sibling 状态，随后同一次安装页、metadata 与 extent。native seal、generic publish、条件删除共用该候选，history checkpoint 返回相符的固定 view；普通 PageStore 仍保留调用者显式 surface 语义。

收敛删除了 backend `stageDerivedExtent` 及匿名/history commit 的两处后补调用。删除 extent 查询也不再构造临时 persistent tree：排序删除 key 沿原树搜索，未变子树使用已有 bounds，新增 proof 并入。新增/覆盖遍历本 segment K；删除仍可能处理累计 overlay，surface 存储准备仍在 owner gate 内，不能宣称完整短 gate、全部收费或已达到固定 K 工作上界。extent A→B→A 的修订号继续递增，实际容量、坐标范围或准备失败均在原 overlay 安装前拒绝，之前 sealed 结果和旧 view 保持。

改动清点见 [§9](br1_modification_guide/CONVERGENCE_CHECKLIST.md#jp4-delivery)，原状态/锁边界见 [02a §9](br1_modification_guide/02a_joint_publication_boundaries.md#overlay-extent-implementation)，原始运行和失败证据见 [本批记录](evidence/br1_s05_overlay_extent_20260928/README.md)。本批相对 JP3：10 个生产文件净增 96 行、3 个测试文件净增 212 行；没有新增生产文件、manager 常驻状态或第二套 extent/writer authority。完整 124 文件的未提交差异中，生产净增 7,929 行、测试净增 11,298 行，生成审计另列，见 [文件清点](evidence/br1_s05_overlay_extent_20260928/inventory-final.md)。这证明一个实际一致性缺口被关闭、重复后补责任被消除；整体主干性能收益仍未证明。

源码差异 SHA-256 `66e7ff89c8a9208ef3253e2d8e0c0b4fc6d2f92e07f664caae4e05138dd1f54d`，HEAD 与 QtCore 保持前批。20 目标 × arm64/x86_64 合计 **9,238 passed / 0 failed / 0 skipped**，6 项工具自测、结构门、最终构建 no-op 和 28 个构建运行文件身份复核通过，见 [checks-02](evidence/br1_s05_overlay_extent_20260928/checks-02/manifest.json)与 [最终汇总](evidence/br1_s05_overlay_extent_20260928/final-results.json)。14 个最终探针已通过：每架构 96 次联合安装 allocations/frees=0，104 个 surface 准备分配拒绝与 9 个成功对照，原 overlay/adapter/cleanup 回归保持。调用图 87 TUs / 1,804 APIs / 19,556 edges / 17 callbacks；原侵入和布局门不提高。往返 revision、空 vector 容量、Qt hash noexcept 与临时树分配异常的失败记录全部保留，checks-01 中止不累计资格。

**下一批出口：JP5/JP6 的 fresh raw/current、manager extent 与 adapter 在同一选择下相符。** 原窗口探针仍观察到冷页 raw default / manager extent 为空，以及暖 current 旧 cache；先明确 retained TileSP 与嵌套读语义，再共用原交付和 admission，不能在 publication write gate 内等待 tile barrier。窗口闭合后进入真实 direct stroke 的 owner/display/finish/cancel/drain 联合验收；V01/BC10 harness 可并行准备。完整资源、root/其他终结的分配故障与进度、OFF 产品、同依赖 upstream 对照、Fresh 2%、M6/M7/M8 和 BR1-PERF 继续开放，stroke → undo → context 顺序不变。

<a id="current-read-convergence"></a>
### 16.7 JP5/JP6 收敛审查：将下一批固定到新读取与旧能力共存

本次没有改变 §16.6 的生产源码或二进制；执行前后复核 JP4 差异身份及原 28 个构建/运行文件。新增可执行反例和 scoped caller 审计见 [证据](evidence/br1_current_read_convergence_20260928/README.md)。原 9,238 项仍是 JP4 冻结矩阵，不与本次观察数合并。

arm64/x86_64 各运行 44 个场景、172 个观察点，0 个控制错误，80 个重复的不一致观察点；修复验收模式 `--require-converged` 两架构均返回 **3（未通过）**。除原 seal/operation 窗口外，确认暖页仍有旧 reader 时，writer 已返回后的另一线程 fresh `getTile(false)` 和 `getReadOnlyTileLazy` 都返回旧 wrapper / 49，而 canonical 已是 97。旧 raw 指针和 captured view 保持旧值正确，不能为修 fresh 而破坏。adapter invalidate 本身不足以关闭此边界。

另外验证 history pending 和纯 write intent 可使兼容 extent 先于 canonical 扩大：前者 checkpoint 后相符、abort 恢复，后者尚未发布像素。这些是不同选择的控制，没有计为窗口违例。下一批须核对 PaintDevice/frame/clone/LoD/purge 的真实消费者，分别保留工作范围与 exact surface 的用途；既不能无条件令 manager `extent()` 返回 canonical，也不能以“兼容语义”豁免普通已发布页的已知不一致。

**执行清单已固定为 [清点 §10](br1_modification_guide/CONVERGENCE_CHECKLIST.md#current-read-work-order)：fresh 选择、旧 reader 隔离、extent caller、失败上送、暖路径成本、联合验收。** [02a §10](br1_modification_guide/02a_joint_publication_boundaries.md#current-read-contract)明确函数、原 selector/lease、nullable caller 风险和 tile barrier/publication 的锁序。六项属于同一交付，不各自发展成新阶段。只修 raw 而 extent/失败/真实消费者未闭合，最多记子范围；联合完成即转入 BC1–BC7/BC10 的真实 direct 链。

本检查点的质量裁决为：局部实现和故障证据较充分，整链交付及相对主干复杂度的收益尚未兑现。保留 JP3/JP4 已证行为，不新建 current 表、writer TLS 或默认每次 capture 的刷新层；当时将接口全面压缩安排在首条真实链后，该时机现由 [§16.9](#api-convergence-plan)修正。完整预算/短 gate/模式覆盖按原门推进。真实 owner/display/finish/cancel/drain、默认启用、同依赖性能及 M6/M7/M8 均未由本次文档与反例审查取得资格。

<a id="fresh-read-implementation"></a>
### 16.8 JP5 新读取实现：旧读隔离与保留的 JP6 窗口

本轮已使 manager 的两个 fresh getter 共用 backend `selectCurrentReadTile`：原 selector 下核对逻辑版本，匹配时复用原 provider cache；失配时捕获精确能力，先取得 TileData 原 COW 引用，再释放精确 pin。旧 wrapper 有 active reader 时给新读取独立的 detached wrapper，不改其旧指针。default 读取使用原 uniform TileData 或必要的兼容默认存储，不创建 canonical default 页；失败向原 job 错误上下文报告，nullable caller 一起处理。最终身份、完整矩阵及剩余窗口见下文；本批不授予阶段资格。

在刷新架构基线前明确审查两个新增 friend：`kis_tile.h` 的 PageStore 标识次数由 6 到 7，`kis_tiled_data_manager.h` 由 10 到 11，分别允许原 backend 读取/更新已有 Tile cache 与 pin 状态、取得原 hash 的默认 TileData。唯一新生产消费者是上述 private helper，经 manager 新读入口调用。采用这一边界以避免把 PageStore 版本类型、新的可选参数族或独立 current 状态加入 Tile 的公共接口；friend 范围较宽是明确的适配债务，不是零侵入。两个直接 include 数保持 1，manager `.cc` 25 标识/3 include 及全部布局上限保持；没有新增 Tile/manager/binding 常驻字段、TLS、write set 或 owner。

并发上，读取 hash/default 引用先于 tile barrier，且取得 barrier 前释放 publication read；冷路径沿既有 tile barrier → publication read 顺序取得精确 view，provider/binding 仍承担物理排斥。独立 wrapper 的 COW 引用在精确 pin 有效时取得，原 TileData handoff 排斥持引用/有用户的 backing；它不持有裸 manager/bridge 指针。默认存储使用原 allocator/预算，失败不回退旧像素；暖命中不增加 wrapper。raw ABI 迁移到原 read capability 后，应连同该 private helper 删除两处 friend，并降低这两个计数。最终验证覆盖 active old reader、manager 析构后独立 wrapper、default revision/实际压力拒绝、原嵌套写及暖入口成本。架构首轮拒绝日志与后续同源结果全部保留，不能仅通过刷新 hash 掩盖计数增长。

最终源码差异 SHA-256 `73c04adf447603eaad0cfd272f0d055136a6c8c833cd8f73bc00ee9b3a0f84a3`，HEAD/QtCore 保持前批。20 目标 × arm64/x86_64 合计 **9,332 passed / 0 failed / 0 skipped**，新增 47 case/架构；6 项工具自测、架构检查、最终实际 Ninja no-op 和运行身份复核通过。[同源证据](evidence/br1_s05_fresh_read_20260928/README.md)记录每架构 16,384 次 warm fresh getter：allocations/frees/capture/generic request 均为 0；这不代替锁成本、主干对照或 Fresh 2% 性能门。调用图为 87 TUs / 1,809 APIs / 19,614 edges / 17 callbacks。

本批相对 JP4 为 13 个生产文件净增 173 行、2 个测试文件增加 205 行；完整 124 文件的生产/测试未提交净增为 8,102 / 11,503 行，生成审计分列。处置见 [清点 §11](br1_modification_guide/CONVERGENCE_CHECKLIST.md#fresh-read-delivery)，实现边界见 [02a §11](br1_modification_guide/02a_joint_publication_boundaries.md#fresh-read-implementation)。

**裁决仅为 JP5 fresh raw 子范围通过。** 整体窗口 probe 每架构仍运行 44 场景/172 观察点，raw 像素违例为 0、控制错误为 0，但 manager extent 仍有 32 个不一致观察点，`--require-converged` 继续返回 3；原 80 个不一致没有被改写成“整体通过”。下一批继续 JP6 的 manager extent/bounds caller/adapter 与固定选择联合交付，保留 pending/intent 工作范围。联合出口后进入真实 direct stroke 的 owner/display/finish/cancel/drain，BC10 harness 可先行；完整短 gate、预算、其他模式与故障组合、OFF、同依赖 upstream、Fresh 2%、M6/M7/M8 和 BR1-PERF 仍开放。

<a id="api-convergence-plan"></a>
### 16.9 API 收敛执行方案与代码映射（2026-09-29）

本次为文档与代码责任审查，没有修改生产实现或新增运行资格；最新产品事实仍是 §16.8。**局部正确性修复不等于 API 已收敛。** 此处修正 §16.4/§16.7 及早期指南中“先真实链、再全面接口压缩”的执行安排：已证明等价的内部政策在本次修复中合并删除，依赖模式迁移的外部 API 才后置。

明确方案与待改函数统一维护在 [API_CONVERGENCE_MAP](br1_modification_guide/API_CONVERGENCE_MAP.md)，[CODE_INDEX](br1_modification_guide/CODE_INDEX.md#api-convergence-index)提供文件反向映射，[清点 §12](br1_modification_guide/CONVERGENCE_CHECKLIST.md#api-convergence-work)和 NEXT_EDITS 负责领取。原 S/JP/BC 编号、所有阶段出口与语义保证不变，不增加一套项目阶段。

执行顺序：先将 backend 六处同源读取选择集中到原受锁政策并删除副本；随后在 JP6 bounds/caller/adapter 联合修复中共用 packed/cursor 安装流程，并以一个内部单次交付边界替代独立的 batch/execution 输出组合，迁移 caller 后删除旧内部签名。原 batch/session/execution 仍是唯一能力 owner。真实 direct harness 现在准备；窗口闭合后沿原 strategy/transaction 接入业务，同步删除已等价的 owner/结果分支。

`resolveTileReadIdentity` 的同锁 version/default 查询、cache/binding 的身份与 pin 区分、retained raw/captured 旧读均保留；不能为减少函数数破坏这些语义。两个 backend friend 仍是适配债务，raw 消费者完成迁移后才连同 helper 退场。旧模式包装、错误 TLS 桥、普通 restore 全量 rebuild 各有消费者，按具体条件删除，不能把它们全部列为立即可删项。

每个实施单元必须同时记录：新增责任及理由、迁移 caller、删除的具体签名/重复 body、暂留消费者及退出条件、锁/寿命和行为证据。仅新增 helper、放宽侵入上限、累计测试数量或减少物理行数均不能证明结构收敛。整体 reader-window、pending/intent/旧读控制、真实显示与终结、资源/性能及 M6–M8 仍保持原出口。[本次文档核验](evidence/br1_api_convergence_20260929/README.md)只证明映射和导航有效。

<a id="read-selection-convergence"></a>
### 16.10 JP5/S04 读取选择政策合并（2026-09-29）

已执行 API 收敛的第一个单元：在 backend 原 Private 内增加 `selectReadViewLocked(bool oldData)`，`captureIteratorReadScope`、`captureReadView`、`resolveCurrentPagePresenceInto`、`selectCurrentReadTile`、`acquireTile`、`pageAllocated` 六处删除同源选择分支。iterator 的 current/base 两次选择使调用点为七个；生成调用图确认全部来自原生产入口，没有新公共声明、字段、friend、TLS 或 owner。原 operational/live legacy/访问模式检查和锁边界不变；helper 只计算选择值，原 caller 继续负责捕获/解析前的 publication 保护。

相对 JP5 仅一个生产 `.cpp` 增加 24、删除 38、净减 14 行；产品测试源码未改。源码差异 SHA-256 为 `740dd7f48e86c7111dfb98b429782d9fdf3a015dc725980874c9b463fd50ac0d`，包含未跟踪源码。新图为 87 TUs / 1,810 indexed APIs / 19,599 edges / 17 callbacks；这里的 indexed API 包含内部函数，不是公共 API 增加。原 21 manifest / 25 ownership / 16 census / 19 intrusion 检查通过，未放宽侵入上限或变更状态归属，仅重新冻结 source/graph。

七个相关产品目标 × arm64/x86_64 合计 **4,116 passed / 0 failed / 0 skipped**，工具自测通过，最终实际 Ninja no-op。这个范围覆盖 manager、iterator、read baseline、resident read、transaction、painter、stroke completion，不冒充本轮重跑旧 20 目标矩阵。[本批证据](evidence/br1_read_selection_convergence_20260929/README.md)绑定测试、原窗口/分配探针、源码与库身份；接口政策的结构结果与行为结果分别记录。

新源码的原窗口探针每架构 raw 违例为 0、控制错误为 0，manager extent 仍有 32 个不一致观察点，整体验收继续返回 3；暖 getter 每架构 16,384 次分配/释放/capture/generic request 均为 0，正对照通过。探针首轮脚本误用旧输出格式的记录保留，改回 JP5 探针源码后重新运行，未修改产品换通过。

本单元仅关闭重复读取政策，下一实现范围为 JP6 bounds/caller/adapter，联动 JP2/JP3/JP7 单次交付；不再重开已合并的选择规则。manager extent、真实 owner/display/finish/cancel/drain、资源/进度、OFF、同依赖性能与 M6–M8 全部保持原出口。待改/已改关系见 [API 映射 §10](br1_modification_guide/API_CONVERGENCE_MAP.md#read-selection-delivery)和[清点 §13](br1_modification_guide/CONVERGENCE_CHECKLIST.md#read-selection-delivery)。

<a id="adapter-delivery-convergence"></a>
### 16.11 JP2/JP3/JP7 交付协议与共同安装收敛（2026-09-29）

本批完成代码替代并绑定同源验证：backend 的 `writeOperation/writeBytes/runCpuMutationOperation` 将独立 `completedBatch/completedExecution` 输出改为 `OperationDelivery`；manager 两条生产调用和直接测试同步迁移，旧签名不保留包装。`PreparedTileUpdates::install` 接替 packed/cursor 的两份安装循环，并删除这两条实际写入路径的 presence 二次查询及准备。clear/copy/remove 仍有不同语义，原查询继续保留。该结构子项不能授予 JP6 整体窗口或真实 stroke 完成资格。

**本批结构审查：** 新嵌套类型位于导出的 backend 头，提供默认构造、移动构造/赋值、`isEmpty`、`finish`；因此不是“没有新增接口”。它以栈上互斥值移动原 batch 或 execution，不新增 session、owner、write set、manager/Tile 字段、TLS 或 friend。history 安装后由原 worker 显式 finish，遗弃沿原 execution 失败/取消；standalone 已 seal，仅保留原 admission 到 manager 锁与局部准备存储释放之后。共同安装继续在原 manager gate 内，不增加 Store owner gate 内 callback，不引入 publication write → tile barrier 锁序。替代对象和退场条件按 API 映射维护，不以具名函数净增数代替责任是否减少。

生产三个文件 +92/-77，净增 15 行；两个测试文件迁移签名并补齐 history 移动/遗弃/异线程 finish 拒绝，原 presence 测试断言两条纯写路径的查询次数归零、clear/copy 保持。调用图为 87 TUs / 1,815 indexed APIs / 19,635 edges / 17 callbacks；manager 仍为 25 identifiers / 3 includes，仅刷新 source/graph checkpoint，21 manifest / 25 ownership / 16 census / 19 intrusion 通过，未提高上限。新增五个 indexed API 属于嵌套交付类型成员，不能以函数数下降描述此改动。

最终 20 产品目标 × arm64/x86_64 共 **9,336 passed / 0 failed / 0 skipped**；工具自测通过，实际 Ninja no-op。源码差异 SHA-256（含未跟踪源码）为 `40ecb952fbc6a0a19bd9047b839be3a11e097f92b7cc6c01717e44d1d37addaa`，源码、库、配置与运行见[本批证据](evidence/br1_adapter_delivery_convergence_20260929/README.md)。首轮矩阵冻结因 baseline 刷新时序被拒绝，原记录保留，刷新结束后完整重跑的 checks-02 才是本批资格。

每架构 192 次共同安装分配/释放为零，144 次暖准备为零，48 次冷准备实际分配；暖 getter 16,384 次分配/释放/capture/generic request 仍为零，正对照有效。整体窗口每架构 raw 违例 0、控制错误 0，**32 个 manager extent 不一致点仍在，整体验收返回 3**。这些受测子范围不是整链预算/性能资格，JP6 不能关闭。

bounds caller 的静态用途已逐项核对并映射在 [API §11](br1_modification_guide/API_CONVERGENCE_MAP.md#adapter-delivery)：公开 working/frame bounds 保留 offset/default 语义；估算不升级为账本；LoD/transfer/frame copy/clone 的源裁剪与像素要迁移到同一选择；purge 保留 writer 全范围扫描。下一必交付结果为联合窗口闭合，随后真实 direct owner/显示/finish/cancel/drain，重复 owner/结果分支随接线删除。不得重新整理已收束的 selector/交付，也不以本次结构完成授予默认启用、OFF、正式性能或 M6–M8 资格。


<a id="convergence-action-plan"></a>
### 16.12 明确收敛行动、代码映射与候选状态（2026-09-29）

本节保留规划时点的候选状态；copy 后续验收已交付到 [§16.13](#copy-bounds-convergence)，执行顺序和其余停止条件保持。

本次落实收敛方案和改动文档，未修改产品代码，未执行新的产品回归。**最近已冻结的产品交付仍是 §16.11；当前工作树另有 copy bounds 候选，不能沿用旧源码的测试资格。** 统一执行入口为 [API_CONVERGENCE_MAP §12](br1_modification_guide/API_CONVERGENCE_MAP.md#convergence-action-map)，[CODE_INDEX](br1_modification_guide/CODE_INDEX.md#api-convergence-index)按文件反查，[清点 §15](br1_modification_guide/CONVERGENCE_CHECKLIST.md#convergence-action-checklist)负责领取与勾选。三者沿用原 JP/BC/S/U/V 编号，不新增项目阶段。

当前候选将 precise/rough 两条 native copy 分支收进 manager 私有 `copyPageStore`，backend `copyFrom` 改为消费 caller 固定的 source/target view，非 wrapped clone 删除独立 working extent 预裁剪。旧内部签名和重复分支已有替代，但完整验收未完成：clone 局部通过之后，新增 bounds 测试发生栈对象智能指针误用；调用已修正，尚需重建重跑。manager 头部增加的类型引用也须在实现验收中补齐侵入/寿命审查，不以本节自动提高 ratchet。候选具体文件和既有失败日志见 [§12.1](br1_modification_guide/API_CONVERGENCE_MAP.md#copy-bounds-pending)。

**执行顺序固定：** 先验收现有 copy 候选；随后在原 admission/prepare/install/release 协议上关闭 JP6 联合窗口，实际 bounds caller 按固定内容或 working/估算/修改用途迁移或保留；真实 direct harness 可立即准备，窗口闭合后联合接原 owner、显示、finish/cancel/drain。结构重复随修复和接线删除。默认启用之前完成真实资源、压力、进度及同依赖主干/OFF/Fresh 对照；raw/外部兼容包装/普通 restore 全量调用按具体消费者条件退出。未覆盖的 LoD/frame/wrapped 等模式逐项登记 BC8，不能由一个 clone 修复宣称全模式完成。

联合窗口安装方案仍须提交成功和 commit 拒绝的实际时序；提前安装 adapter 会产生回退责任，不能只移动调用位置。禁止 Store owner gate 内回调 manager、publication write→tile barrier、用 union 掩盖删除或以 canonical getter 替代全部 working 语义。原整体 reader-window 必须精确通过，§16.11 的 32 个 extent 不一致点是旧冻结证据的未关闭问题；本次未重新运行，不宣称当前候选的实测计数。

**收敛验收：** 每项记录旧符号/重复体→唯一职责→caller 迁移→同批删除→保留消费者/退出条件→行为证据。已完成的 selector/共同安装/交付不重新整理；一个出口通过就转下一项，只有新契约失败才能重开。函数总数、净增行数、测试总数都不单独代表质量；不得无限增加底层接口来推迟真实业务交付。M6→M7→M8、stroke→undo→context 与全部原门限保持不变。[本次核验记录](evidence/br1_convergence_action_map_20260929/README.md)仅证明文档映射与产品源码未被本次编辑改变。


<a id="copy-bounds-convergence"></a>
### 16.13 JP6 copy bounds：共同选择与复制分支收敛（2026-09-29）

本项按 §16.12 第一项完成同源验收，只关闭 copy 子项，未授予 JP6 整体或 M6–M8 资格。`copyPageStore` 是 manager 私有、operation 局部的共同实现：两条 native precise/rough 分支复用它，四个公开 bitBlt 入口和 legacy 算法保留。backend 原 `copyFrom` 改为消费原 caller 固定的 source/target view，删除其内部重复捕获；两份 view 各自绑定原 store/surface，分别固定选择，不承诺跨 store 原子快照。

**头部侵入及寿命审查：** manager 头从 11 到 12 处 PageStore identifier，只增加私有 helper 的既有结果枚举引用；直接 include、对象布局、friend、TLS、owner/session 数不变。它替代两个 native 选择/准备/复制 body，源与目标 view 仅存于原调用栈，几何和像素使用同一能力；能力延续到 adapter 刷新结束后随返回释放。capture 的 publication 保护由原入口管理，不增加跨 kernel 的 gate，不引入 Store owner gate 内 callback 或 publication write→tile barrier。首字节前选择/范围/准备拒绝返回原 Failed，legacy Unavailable 只在写前选择，执行失败保持原取消责任。copy helper 的类型引用随未来整个 manager copy adapter 消费者迁移而删除并降低上限；JP5 friend 的独立退出条件保持原约束。该声明增量明确获审，不允许借此提高其他侵入/布局上限。

新增页丢失反例已在旧实现复现，修复将非 wrapped clone 的独立 working extent 预裁剪移入同一固定 copy 选择。相同 default 的范围同时包含 source 与 target，保证空源能清除目标旧内容；default 不同保留完整请求范围。wrapped 路径及 LoD/transfer/frame copy 的独立范围消费仍单列，manager working extent 的整体窗口未由此关闭。完整源码身份与失败记录见[本批证据](evidence/br1_copy_bounds_convergence_20260929/README.md)，实际函数替代与清点见 [API §13](br1_modification_guide/API_CONVERGENCE_MAP.md#copy-bounds-delivery)。


生产五文件 +96/-64（净增 32），测试三文件 +167/-6。每架构新增 32 个真实 clone 窗口场景、32 个 native 固定选择场景和 32 个两端 backend 关闭的 legacy 对照；后者不等于完整 OFF 构建资格。PaintDevice 隔离检查发现原 HEAD 的 `syncLodCache` 没有释放创建的 LodDataStruct，已用测试局部 unique_ptr 修正；没有放宽像素断言或修改生产回收以消除警告。旧栈对象误用、最初 compile alias 错误和调用图过期拒绝日志均保留，最终证据不引用这些失败运行作为通过。

最终 20 个完整产品目标及 14 个选定 PaintDevice 方法 × arm64/x86_64 共 **9,560 passed / 0 failed / 0 skipped**，无 tile 泄漏警告；架构、工具自测和实际 Ninja no-op 通过。源码差异 SHA-256（含六份未跟踪源码）为 `182a7d820fff8003c50fdbb23b84be44be79b4f5549eb06ed8cc40c6d46aca1a`，125 个范围文件与 29 个运行/配置文件绑定同源。调用图为 87 TUs / 1,815 indexed APIs / 19,661 edges / 17 callbacks；这些 indexed API 数不等于公共函数数。PaintDevice 未跑压力/benchmark 全集，本批未重测暖 getter 或 adapter 分配成本，不沿用旧数字授予新性能资格。

原 reader-window 探针每架构 44 个场景、172 个观察，raw 违例 0、控制错误 0，**manager extent 仍有 32 个不一致点，整体验收退出 3**。下一项固定为 §16.12 的联合安装锁序/拒绝回退设计及真实 bounds caller 对齐；通过后立即进入原 direct owner/显示/finish/cancel/drain。copy 不再无反例地反复整理；默认启用、完整 OFF/资源/性能、M6/M7/M8 继续保持原门。


<a id="joint-adapter-window-delivery"></a>
### 16.14 JP6 packed/cursor：canonical 发布与 prepared adapter 的短 gate（2026-09-29）

本批关闭 §16.13 记录的 32 个冷页观察点，范围限定为普通 standalone packed write、operation-private cursor 与 history cursor 的 add/update 交付。像素 body 继续在 manager 锁外执行；backend 在 changed delta 已固定、execution 已归还可写 guard 后，把原 publish closure 交给 caller completion。manager 的两个原写入口仅在 completion 内取得原 `m_lock`，依次执行 standalone publish（history 使用原 pending 选择）、`PreparedTileUpdates::install` 和 extent 通知，再释放 manager gate。`extent()` 与 `region()` 的独立读取使用该 gate，因此 reader 只能看到旧页/旧 adapter 或新页/新 adapter，不再看到新 canonical 页配旧 working extent。

该锁序没有在 Store owner gate 内回调 manager，也没有新增 publication write → tile barrier。准备仍在首字节前完成，pixel body 不持 manager gate；`MutationAdapterInstalled` 在 manager gate 释放后发出，诊断 callback 可重入。standalone 原 batch 在完成后只保留 admission 到局部 prepared 存储销毁；history 在安装时保留原 execution borrow，并由原 worker 随后归还。commit/publish 拒绝先于 adapter install，不能留下只安装兼容索引的回退状态；已发布后的 install 是预备结构的无分配安装，其不成立属于内部不变量失败，不能 replay 像素。

**API 收敛结果：** `writeOperation`、`writeBytes` 与其内部模板各增加一个 `AdapterCompletion` 参数，现有 manager caller 就地使用；没有新增具名函数、owner、session、write set、manager/Tile 字段、TLS 或 friend。`OperationDelivery` 从 batch/execution 互斥状态缩成只持已完成 standalone batch，删除 `finish()` 和 history execution 分支；对应两个仅验证 history delivery 搬移/析构的测试项删除。相对 copy 冻结点，生产三文件 +95/-67（净增 28），测试两文件 +31/-76（净减 45）；生成图从 1,815 APIs / 19,661 edges 降为 **1,814 / 19,634**，callbacks 仍为 17。indexed API 不等于公共 API，但本批没有用新增 helper 隐藏旧责任。

最终 HEAD 仍为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`，工作树差异 SHA-256 为 `7e1c6465029f5dffac8d5fb8df310df65aa1c60de63846b8b4fbc183b3bf317b`。20 个完整产品目标和 14 个选定 PaintDevice 方法 × arm64/x86_64 共 **9,556 passed / 0 failed / 0 skipped**，架构检查、工具自测、实际 Ninja no-op 及无 tile leak warning 均通过。联合探针每架构 44 场景/172 观察：publication/raw/control 三类违例均为 0，`--require-converged` 退出 0。独立 reader 在 seal cleanup 已确认新 canonical/raw 后，必须等待 manager gate，随后取得对应新 extent；原 retained raw/captured、pending/intent 及 legacy 冲突控制保留。[同源证据](evidence/br1_joint_adapter_window_20260929/README.md)记录矩阵、探针、调用图与中间失败设计。

**裁决是 packed/cursor add 联合窗口完成，不是 JP6 所有发布族或 S05 完成。** `clear(QRect)`、删除/default、native copy、restore/purge 与其 working/frame/LoD caller 尚未全部进入同一 completion；它们必须按实际语义核对，不能把仅增页的 prepared install 直接套到删除，也不能将 working bounds 改成 canonical extent。下一批先做有限发布族依赖审计：若首条 RGBA8/OVER/direct stroke 的正常显示、finish/cancel 会经过未闭合路径，则只修该路径并提交相同联合断言；否则立即转 BC1–BC7/BC10 的真实 owner、brush jobs、display cut、finish/cancel/drain 接线。已闭合的 selector、copy 与本批 completion 不再无反例重构。完整 OFF、资源/进度、同依赖 upstream/Fresh 2%、M6/M7/M8 和 BR1-PERF 保持原门。

<a id="direct-stroke-pilot-delivery"></a>
### 16.15 BC1–BC7：首条 direct stroke 显式开发入口（2026-09-29）

有限发布族依赖审计确认首条 RGBA8/OVER/direct 正常 add/update/finish/cancel 不依赖 §16.14 尚开放的 delete/default/restore/purge，因此本批直接进入真实业务接线，没有继续扩大底层 completion API。正式工具默认保持旧路径；测试派生 strategy 只调用 base 的 protected opt-in setter，没有修改 `FreehandStrokeStrategy::Flags` 公共接口。BC9 前不默认启用。

原 `KisPainterBasedStrokeStrategy` 创建主 `KisTransaction` 后，在首个像素 job 前按单 painter、Pixel Brush、RGBA8、OVER、无 selection/indirect/mask/wrap/LoD 一次选择资格并调用原 `beginStrokeMutation`。`KisPainter` 新增一个非拥有 transaction 绑定，与原自持 `d->transaction` 分离；multi-dab、scalar fixed、bitBlt 和 mirror 的无 owner 入口共用它。实际 `KisBrushOp::addDabJobs` 删除显式空 owner。更新在取 dirty 前调用原 transaction checkpoint，成功后再交给 projection/display；finish/cancel 成功路径先解绑/销毁 painters，再释放原 transaction，失败重试仍保留 owner。

**API 账本：** 本批当时新增一个 public painter setter和两个 protected strategy 函数；没有增加 `FreehandStrokeStrategy` 公共 flag，也没有新增 session、write set、PageStore owner、manager/Tile 字段、TLS 或 friend。它们分别承担 image/ui 非拥有桥、受控 opt-in 和 dirty 发布前原 transaction checkpoint。painter-based strategy 的 job failure reporting 来自此前 S01：PageStore 写入可恢复拒绝后，void painter API 必须把失败送到 scheduler，不能提交部分 stroke；它不是本 pilot 的性能接口。删除生产 caller 的硬编码空 owner，四类 painter 写入口合并到一个绑定政策；当时保留的显式 owner overload 后续确认只有测试外部 consumer，已在 §16.21 删除并收回 private impl。正式工具不调用 opt-in setter，退出条件记录在 [API §15](br1_modification_guide/API_CONVERGENCE_MAP.md#direct-stroke-pilot-delivery)。

对 `tool/strokes` 的主干侵入复核又删除了测试专用公开 flag：`freehand_stroke.h` 相对 `origin/master` 零差异，`freehand_stroke.cpp` 只增加 dirty 发布前的一次调用；active 判断和 dirty 扫描由原 transaction owner 基类承担。base strategy 的结果化 finish/cancel、cancel retry 和 failure reporting 保留，因为它们已有可失败写消费者，并非为追求性能扩大 UI 层。逐项裁决与禁止继续侵入的边界见 [API §16](br1_modification_guide/API_CONVERGENCE_MAP.md#stroke-mainline-intrusion-audit)。

目标验证按用户要求只覆盖结果，不重跑 9,556 项历史矩阵。`KisDabRenderingQueueTest testBrushPagePartition testSharpnessLine` 在 arm64/x86_64 各 **50 passed / 0 failed / 0 skipped**，覆盖实际 brush 的持久 owner、并行分区、1px、checkpoint、像素对照与 transaction undo/redo；`FreehandStrokeTest testPersistentAutoBrushStroke testPersistentAutoBrushStrokeCancelled` 两架构各 **4 / 0 / 0**，覆盖原 strategy、实际 autobrush/update、checkpoint 后显示、finish 与 cancel；`KisPainterStrokeCompletionTest testPixelFailure` 两架构各 **22 / 0 / 0**，确认 void painter 写失败必须进入 scheduler cancel。最终 source checkpoint 为 189 dirty source/build files；架构门 21 manifest / 25 ownership / 16 census / 1,814 indexed APIs / 19,634 edges / 17 callbacks / 19 intrusion files，通过。证据见[本批记录](evidence/br1_direct_stroke_pilot_20260929/README.md)。

**该批裁决是首条显式开发入口成立，不是 BC10、BC9、默认启用或 M6–M8 完成。** 当时两个目标分别证明 strategy 显示/终结与 brush owner/undo；随后 §16.17 已在显式 Buildup direct fixture 中补齐策略 undo/redo、四类失败和无新输入 drain，并修正本段 Freehand 预设为 Wash/indirect 的证据限制；§16.18 又补齐 BC9 首个资源子范围。当前剩余的是结构化压力结果、自动 continuation、多文档和公平性。BC5 的 current/self-source 与 BC8 的 path/selection/indirect/mask/LoD/wrap 逐项迁移或保留。已闭合的 selector、copy、packed/cursor 与本批 owner bridge 没有新反例时不再重构；完整 OFF、同依赖 upstream/Fresh 2%、正式性能、M6/M7/M8 和 BR1-PERF 保持原门。

<a id="mainline-intrusion-contract"></a>
### 16.16 新管线内聚与主干低耦合强制合同（2026-09-29）

后续 BR1 修改必须保持依赖单向：`tool/strokes` / paintop → `KisTransaction` / `KisPainter` 语义桥 → PaintDevice/DataManager → PageStore。PageStore 内部 session、page key、claim、borrow、publication token、budget record 和状态枚举不得进入 UI、tool 或 paintop 的字段、公开签名与控制流；PageStore 也不得反向依赖 preset、strategy、projection 或 UI 对象。

主干只允许承载原 owner 已经负责的事务准入、像素调用、dirty 对外观察、finish/cancel/undo 和失败上送。页归属、COW、pending/current、预算、回收、发布与性能策略必须内聚在新管线。关闭状态的特性专属热路径至多一次可预测 inactive 判断，不得新增特性专属扫描、分配、容器、锁、TLS 写入、页查询或 checkpoint；此前 S01 的通用 failure context 作为可失败写正确性单独计账。测试专用 public flag/API 一律禁止；临时 protected/private bridge 必须列真实消费者、无法复用既有接口的原因和删除触发条件。

每个涉及主干的批次必须提交对照 ref、逐文件 `+/-`、新增符号/字段/include/friend/锁/TLS、原 owner 与 caller、关闭状态成本、同批删除、暂留消费者和退出条件。性能收益、局部测试通过、代码搬移或提高侵入上限不能单独批准主干扩张。没有关闭新业务断言、删除重复责任或减少原工作量的 diff 应停止并回退。

完整 MI1–MI8 条款、当前接口裁决、审查问题和默认启用门见 [主干低耦合合同](br1_modification_guide/MAINLINE_INTRUSION_POLICY.md)。API 逐项处置见 [API §16](br1_modification_guide/API_CONVERGENCE_MAP.md#stroke-mainline-intrusion-audit)，执行勾选见 [清点 §20](br1_modification_guide/CONVERGENCE_CHECKLIST.md#mainline-intrusion-contract)。该合同是后续实现约束，不授予新的阶段资格。

<a id="direct-stroke-joint-fixture"></a>
### 16.17 BC10：同一 direct Freehand fixture 的 undo/drain 与失败终点（2026-09-29）

本批按 §16.16 先从测试关闭联合行为，**生产源码和生产 API 零改动**。测试在资源快照创建前把专用 autobrush 明确设为 Buildup 并断言 `paintIncremental()`；原 `autobrush_300px.kpp` 是 Wash，会走当前资格排除的 indirect painting，因此 §16.15 的 Freehand 4/0/0 只能证明 strategy 显示/finish/cancel，不能单独证明 direct persistent 已命中。本批修正测试配置后，同一个显式 persistent `FreehandStrokeStrategy` case 执行两段实际 autobrush 写入和两次强制 update，在两个观察点确认像素可见；随后通过原 runnable-jobs interface 递归追加三步 sequential 必要后继，不再输入新的外部 stroke 数据。`finishStrokeCallback` 只在三步全部完成后被观察到。

成功结束后，测试在原 image strategy 上只执行一次 undo：两段写入同时消失，surrogate undo store 回到空位置；一次 redo 后完整图像与结束快照逐像素相同。undo/redo 是 scheduler job，断言位于既有 `waitForDone()` 之后。这从原 owner 的代码路径和一个 undo 单元的外部行为证明 transaction 连续跨越两个 update/cut；没有为测试增加 transaction 指针、session/incarnation getter，也没有把 PageStore 内部类型引入 UI fixture。

同一 fixture 还覆盖四个结构化失败终点：实际 target 的竞争 transaction 触发 admission 拒绝；首段真实 brush update 后注入既有 job pixel-failure signal；pending brush jobs 排空后改变 write context，令真实 checkpoint 拒绝；成功 checkpoint 后改变 context，令 finish 拒绝。四行均只有一次 cancel、没有成功 undo、最终像素为空且 memento 已释放。低层 painter/PageStore swap-in 像素故障仍由 §16.15 的 completion test 证明；这里验证它的 scheduler 信号在 persistent Freehand 生命周期中的联合终点。

`FreehandStrokeTest testPersistentAutoBrushStroke testPersistentAutoBrushStrokeCancelled testPersistentAutoBrushStrokeFailure` 在 arm64/x86_64 各 **8 passed / 0 failed / 0 skipped**。本批主干侵入账本为生产文件 +0/-0，新增生产函数、字段、include、friend、锁和 TLS 均为 0；完整源码、二进制与日志身份见[本批证据](evidence/br1_direct_stroke_joint_20260929/README.md)。

**裁决是首条 direct 入口的 BC10 联合正确性 fixture 完成：多 update、策略 undo/redo、递归无输入 drain，以及 admission/像素失败信号/checkpoint/finish 的唯一 cancel 终点均在同一真实 strategy 中成立。** BC10 的完整性能与 BC1–BC9 全覆盖仍未完成；其后 §16.18 已交付 BC9 的单文档受限预算、慢 reader、长 stroke 和退出计账子范围，结构化压力 continuation 与多文档仍是默认启用前置。BC5/BC8、正式工具启用、完整性能和 M6–M8 均未由本批改变。后续不再为该 fixture 增加身份 getter或重复失败状态。

<a id="direct-stroke-pressure-fixture"></a>
### 16.18 BC9：受限资源、慢读者与退出计账的首个联合子范围（2026-09-29）

本批继续遵守 §16.16，**生产源码和生产 API 零改动**。`FreehandStrokeTest` 在 24 MiB TileDataStore 硬上限、soft/pool/swap 为零的配置下执行 1024×1024 Buildup direct autobrush：首次真实写和显示 cut 后保留一个旧像素 reader，再执行四组横纵长路径、第二次 update、旧值复验与释放，最后递归产生三步必要后继并停止外部输入。两架构都完成 finish、一次 undo/redo、慢 reader 旧值稳定、递归 drain 和退出后 resident 归零；采样的像素常驻峰值分别为 arm64 15,237,120 B、x86_64 18,366,464 B，均超过硬上限的一半且不越界。独立 8 MiB PageStore 双 backend fixture 同时验证：首个 6 MiB current、慢读者保持被重写页的 retained history、释放后 retained/debt 清零、第二 backend 的超限写原子拒绝、两个 store 的 reserved 和进程 TileDataStore resident 在 close 后归零。8 MiB 下的普通取消控制也沿原 Freehand cancel 终点收敛。

校准期间保留了一个必要反例：把同一长 stroke 压到 8 MiB 时，PageStore 进入 metadata 容量拒绝（诊断运行观察到 `metadata arena budget is exhausted`，另一次为 `metadata owning capacity budget is exhausted`）；随后原 scheduler 取消剩余 job，因此释放慢 reader 的排队 job不会运行。当前写入结果仍把永久容量拒绝、可等待压力和取消折叠为失败，像素 operation 也可能已经开始，不能安全重放整个 dab。该反例定位的是 PageStore/DataManager 的结构化结果与首字节前 job continuation 缺口；它不授权在 `tool/strokes` 加预算状态、waiter、轮询或重放逻辑。具体强制边界已回写 [MI 合同](br1_modification_guide/MAINLINE_INTRUSION_POLICY.md)。

目标验证只运行本批结果：`FreehandStrokeTest testPersistentAutoBrushStrokePressure testPersistentAutoBrushStrokePressureCancelled` 在 arm64/x86_64 各 **4 passed / 0 failed / 0 skipped**；`KisPageStoreReferenceTest tiles3BackendsShareProcessResidentLimit` 各 **3 / 0 / 0**。本批生产文件 +0/-0，新增生产函数、字段、include、friend、锁和 TLS 均为 0；测试新增压力 workload、慢 reader 探针与现有进程资源 fixture 的 retained/reserved/close 断言。源码、命令和失败样本见[本批证据](evidence/br1_direct_stroke_pressure_20260929/README.md)。

**裁决仅关闭 BC9 的单文档受限预算成功、慢 reader 稳定、原取消与 close 后计账归零子范围。** 结构化永久/可等待/取消结果、首字节前 scheduler continuation、自动释放后的无输入恢复、多 store 公平和真实多文档长笔仍开放，默认启用资格不变。本节当时提出“下一段先形成结果边界”；§16.20 的 job 所有权复核已撤销该顺序，当前先做 PageStore 内完整收费、公平与释放进度，保持 `tool/strokes` 零扩张。

<a id="direct-operation-pressure-boundary"></a>
### 16.19 BC9 / OP9：普通 direct operation 的首字节前 backing 准备边界（2026-09-29）

§16.18 的 8 MiB 反例证明，原 cursor callback 可能已经改写前页，后页才因 metadata/backing 容量失败；这种失败无法安全转成 scheduler continuation。本批先在原 `KisPageMutationExecution` 内关闭这个必要前提：`writeOperation` 的普通 mutable 目标在 callback 进入前逐页取得并归还 preserve-content guard，确保全部目标 backing 已经可用。任一准备失败时 callback 调用次数保持零，只取消本次 execution 新准备的页，并把对应 entry 恢复为可重试的 intent；原 history session、此前 pending 页与 claim 继续存活，同一 history owner 在压力解除后可以重试。

成功准备也不制造无意义版本。execution 继续复用原排序 `BoundEntry`；≤64 页使用 control block 内的一组 touched 位和一组“本次准备但未触碰”位，更多页使用原 `KisMutationStorageAllocator` 一次收费的 `2 * ceil(K/64)` 个 word，没有第二份 page-key map。callback 真正取得写 guard 时清除 preparation 位并设置 touched 位；导出 changed 前，所有仍只有 preparation 位的页经原 cancel/retirement 链回滚，因此只读声明范围而未写的页不会 seal 新 generation。取消后 entry 的 transition 身份由 `recordCancelled` 清空并回到 `IntentOnly`，避免同一持久 scope 重试时复用已经撤销的 Prepared 状态。

范围有意受限。semantic removal 和带 staged alias initialization 的 entry 返回内部 `Unsupported`，继续走已有语义路径；packed `writeBytes` 已拥有完整 payload 与逐页直接初始化优化，也不启用这次 cursor preflight。clear/copy/planar/restore 不能由本结果推定完成。对外结果目前仍是既有 `Failed`，本批没有增加 `RetryablePressure`、waiter、continuation 或 UI 状态。只有当可靠分类与安全持有原未执行工作单元的真实 consumer 同批出现时，才扩展 PageStore/DataManager 的 operation 结果并合并旧失败分支；§16.20 已确认当前 scheduler 尚不具备该所有权。

**主干侵入账本：** 生产改动限定为 PageStore、write coordinator 和 `KisTiledDataManagerPageStoreBackend` 六个内部文件；新增的是 execution 私有准备/收尾方法、session 私有 preparation mode、coordinator 内部取消复位及 backend 私有模板策略参数。public/protected 产品 API、manager/Tile/UI 字段、include、friend、TLS、`tool/strokes`、paintop、painter、PaintDevice 和 scheduler 改动均为零。PageStore 决定并回滚物理准备，backend 只选择既有 operation 是否使用该政策；budget/page/waiter 身份不越过适配层，符合 §16.16 的单向依赖和最窄桥要求。

目标验证未重跑历史矩阵。arm64 运行 `testPageStorePixelOperationPreflightBudgetPressure` 与完整参数化 `testPageStoreChangedStorage`，共 **131 passed / 0 failed / 0 skipped**：前者验证压力拒绝时 callback 未进入、同一 history owner 随后重试成功且 active write pages 归零；后者的 128 个 BPP/K/owner/outcome 组合额外断言 `pagesSealed` 只随实际 changed 页增长。x86_64 的压力用例为 **3 / 0 / 0**。最终架构门通过：21 manifest / 25 ownership / 16 census / **1,824 indexed APIs / 19,890 reverse-call edges / 17 callbacks / 19 intrusion files**。命令、日志和源码身份见[本批证据](evidence/br1_operation_pressure_boundary_20260929/README.md)。

**裁决是首字节前原子拒绝的底层边界成立，不是自动恢复完成。** §16.20 的所有权复核已撤销“下一批直接增加 typed result”的安排：没有安全 consumer 时继续返回 `Failed`。下一可执行生产批优先完成 PageStore 内完整收费、多 store/多文档公平和释放进度；continuation 只在同一有限批次能转交原未执行工作单元且合并旧失败分支时实现。`tool/strokes` 保持零扩张，正式工具默认启用与 M6–M8 资格不变。

<a id="stroke-continuation-ownership-audit"></a>
### 16.20 BC9：scheduler continuation 所有权与主干零增长裁决（2026-09-29）

本批只做当前源码的所有权审查和收敛裁决，没有修改生产代码。`KisStroke::popOneJob()` 把 job 从 stroke 队列移交给 updater；`KisUpdateJobItem::setDone()` 在 `run()` 返回后删除 `KisStrokeJob`，并由该对象析构其 `KisStrokeJobData`。通用 job data 没有失败后重试克隆协议，`KisRunnableStrokeJobData` 独占其 runnable/closure。真实 brush update 又可拆成多个并发页 job，后接 dirty/checkpoint 和递归 producer；一个页 job 在 callback 前被拒绝时，兄弟 job 可能已经完成。因此，重放整个 dab/update 不安全，把已经出队的 job 重新加入队列也没有现成的所有权转交点。

现有 `KisStrokeJobFailureContext` 只负责把 void 绘画调用的首个失败交回原 job owner；它不拥有 transaction、job、像素、队列位置、预算 waiter 或取消回调。当前 `Failed → failStroke → 原 cancel/abort` 仍是唯一正确的生产终点。把 pressure 枚举塞入该 TLS，或在 `tool/strokes` 保存 budget/waiter 并轮询，都会制造第二个调度 owner，违反 §16.16。

**强制接口门：** 当前 pilot 之后，UI/tool/paintop/painter/PaintDevice/stroke scheduler 的 public/protected API 默认净增长为零。`RetryablePressure` 或等价 deferred 结果只有在同批证明并实现以下全部条件时才能出现：callback 零进入；原未执行工作单元的输入、队列位置、取消权和析构权一次性转交；并发兄弟 job 与后继 cut 不被重放或越序；唤醒后仍由原 scheduler 决定 continue/cancel/fail；页、reservation、budget revision 和 waiter 对象不越过 DataManager 适配边界；原模糊失败分支在同批合并或删除。仅有底层分类、测试需要或未来计划都不能增加接口。

**下一实现顺序调整：** 先领取仍可内聚在 PageStore 的完整资源收费、多 store/多文档公平和释放进度，继续使用现有 `Failed`；并行维护一个有限的 continuation ownership 设计清单，但不提交预留函数。只有该清单能形成上述单批闭环时，才进入 scheduler 接续；否则保持明确拒绝，不牺牲正确性换自动等待。完整规则见 [主干低耦合合同 §6](br1_modification_guide/MAINLINE_INTRUSION_POLICY.md)。本节不授予 BC9、默认启用、M6–M8 或 BR1-PERF 新资格。

<a id="painter-owner-api-convergence"></a>
### 16.21 Painter owner 公共接口收缩与主干低耦合落实（2026-09-29）

本批把真实 direct pilot 已经形成的 owner 传递收束为一个公共语义：strategy 在其保活期内通过 `KisPainter::setStrokeMutationOwner` 绑定原 `KisTransaction`，所有普通 painter 写入口自动消费该非拥有绑定。`bitBlt`、标量 `bltFixed`、QRect/vector multi-dab `bltFixed` 和 PaintDevice-source `renderMirrorMask` 不再各自暴露显式 owner 变体；owner 参数只留在 private `bitBltImpl`、`bltFixedImpl` 与 `renderMirrorMaskImpl`，用于一次同步调用内的传递。目标测试也先绑定 painter，再调用与生产 brush 相同的 public 入口，不再成为保留测试专用生产 API 的理由。

相对本批前工作树，删除 5 个 public 显式 owner 变体，并增加 1 个无 owner vector multi-dab public 入口承接原业务调用，public 声明净减 4。原 target/history owner、source 独立性拒绝、G0/current 选择、checkpoint、取消和失败终点均未改变；PageStore 类型、page/budget/waiter 身份没有向 painter、paintop 或 `tool/strokes` 上移。动态 `kritadefaultpaintops` 首次加载暴露了构建目录中的旧 owner 符号引用；重建该真实插件后旧引用消失，证明生产消费者已经迁移，未通过保留兼容 overload 掩盖陈旧二进制。

目标构建 `kis_painter_test KisDabRenderingQueueTest` 与动态 `kritadefaultpaintops` 均通过。arm64 Painter 的 fixed/multi-dab owner、错 owner、取消、snapshot、selection、稀疏范围与并行矩阵为 **520 passed / 0 failed / 0 skipped**；实际 brush 页分区与 sharpness/mirror 路径为 **50 / 0 / 0**；插件重建后的 owner 拒绝加载复验为 **3 / 0 / 0**。架构门通过 21 manifest / 25 ownership / 16 census / **1,818 indexed APIs / 19,722 reverse-call edges / 17 callbacks / 19 intrusion files**，相对 §16.19 减少 6 个 indexed APIs 和 168 条边，外部侵入文件数不变。完整范围和命令见[本批证据](evidence/br1_painter_owner_api_convergence_20260929/README.md)。

**裁决是 Painter 对外 owner 入口已经由并列 overload 收敛为一个有退出条件的绑定桥。** MI6 的默认公共接口净增长为零继续生效；不得为测试、future continuation 或新 paintop 恢复 owner overload。下一生产批仍是 PageStore 内完整收费、多 store/多文档公平和释放进度，正式工具默认启用与 M6–M8 资格不变。

<a id="shared-nonpayload-budget"></a>
### 16.22 BC9 / S10：产品 PageStore 非载荷共享父额度与释放返还（2026-09-29）

本批把每个 `KisTiledDataManagerPageStoreBackend` 原先独立拥有整份 RAM+pool 非载荷上限的行为改为两层计账。每个 `KisPageStore` 继续保留原 `KisBackingBudgetController`、分类诊断和单 store 限制；所有同时存活的产品 backend 另外共享一个由同一产品配置派生的父 controller。局部 `MetadataArena` 与 `OptionalCache` 在父层合并为一个非载荷总额，因此多个文档不能再分别把同一 metadata/default-cache 配置当作完整免费容量。物理 tile RAM 已由进程级 `KisTileDataStore` 唯一收费，本批没有把 payload 再计入父层。

父 reservation 在局部 reservation 前取得；局部拒绝由组合 reservation 自动归还父 token。commit、retain、release 与 live free 同时更新两层账本，但不同时持有两个 controller mutex。每个子 controller 的注册节点也通过父 `MetadataArena` allocator 实际收费；注册失败和析构都在父 gate 外释放候选/节点，1 B 父额无法伪装成可注册。产品配置在仍有 live store 时若改变会明确拒绝，最后一个 store 释放后弱持有父 controller 自动消失。PageStore 对外 public/protected API、DataManager/Tile/UI 字段、`tool/strokes`、paintop、painter、PaintDevice、scheduler、friend、TLS 均无增长；只增加 PageStore 私有 friend 桥、budget 内部组合能力和 backend 内部父池获取函数。既有 `KisPageStoreWriteOperationResult` 仍保持不变。

本轮否决了“按已注册 store 数静态平分父额”的中间实现：一个图像本身就会创建多个 PageStore backend，注册数是对象拓扑，不是正在等待的业务需求；静态 (1/N) 会让未竞争的投影/辅助 store 压缩主 paint device，并使原 24 MiB 长 stroke 误报 metadata exhausted。当前父层保持 work-conserving：注册节点收费且所有子项共同受进程总额约束，但空闲注册项不分走容量，活跃 store 可借用全部剩余父额。真正的无饥饿公平仍必须绑定可取消的原请求/continuation owner，不能用永久 child 标志或新增 stroke 轮询伪造。

controller 目标用例先用 1 B 父额证明注册节点分配拒绝且 live/reserved 归零，再把两个本地 controller 接到 1024 B 父额：第一方提交 600 B metadata，第二方注册节点占用实际控制字节，随后只能取得父额的精确剩余值，额外 1 B 被拒绝；第一方释放 600 B 后第二方可借满这 600 B，第二方析构又归还注册节点。真实 `FreehandStrokeTest` 保持 24 MiB tile hard limit、pool/swap 为零，不提高预算即重新通过长 stroke、慢 reader、递归 drain、undo/redo、取消和退出归零。双产品 backend 继续验证 8 MiB tile payload、16 MiB pool、慢 reader/history、第二 backend 原子拒绝与 close 清零。arm64 两个目标程序合计 **8 passed / 0 failed / 0 skipped**。

架构门为 21 manifest / 25 ownership / 16 census / **1,826 indexed APIs / 19,821 reverse-call edges / 17 callbacks / 19 intrusion files**；改动仍位于 PageStore 内部父子计账和 backend policy，没有扩大冻结的外部侵入文件集。构建、测试、结构结果和源码哈希见[本批证据](evidence/br1_shared_nonpayload_budget_20260929/README.md)。

**裁决关闭非载荷共享总额、跨类合并收费、注册控制存储收费、空闲 store 不限流和同步释放返还子范围。** 当前没有拥有原失败请求的跨 store waiter 或安全 scheduler continuation，因此不宣称无饥饿公平；父额度不足仍沿原 `Failed` 终点，释放后由测试发起的新 reserve 不是自动接续证明。S10 下一段先补 notification/dispatch/retry/pass 与必要终结存储的实际收费，并把公平需求映射到原 job ownership transfer；禁止再次按注册 backend 数静态分额。随后用真实多文档并发长 stroke 验证等待次序、取消、退出归零。完整 BC9、正式工具默认启用、M6–M8 与 BR1-PERF 资格不变。

<a id="budget-waiter-state-storage"></a>
### 16.23 S10：预算 waiter 请求状态、冷 context 的唯一所有权与实际收费（2026-09-29）

本批收敛既有预算等待者内部所有权，没有新增等待入口或上层结果。原实现让 `KisBackingBudgetWaitContext::requests` 与外部 `KisBackingBudgetWaiter` 共同以 `QSharedPointer` 持有 `KisBackingBudgetWaitState`；state/control block 由普通 heap 隐式分配，32-request 上限只限制数量，不能证明实际字节受 `MetadataArena` 约束。现在 context 是请求状态的唯一 owner，数组持有 allocator-backed `unique_ptr`；外部 handle 只保存弱 context 与单调 sequence。state 不再保存一份反向弱 context，take/reset/isValid 都在既有 context→controller 锁序下按 sequence 复验。

每个 state 与每 controller 的冷 `KisBackingBudgetWaitContext` 本体都在取得 controller mutex 前由现有 mutation-storage 路径分配，因此真实字节同时进入本地 `MetadataArena` 和 §16.22 的共享父额。空载容量 preflight 把一次请求不可约的 context+state 字节计入需求，避免等待控制存储自身吃掉唯一可授容量而形成永久排队；32 项已满也先无分配拒绝，竞态后在安装前再复验。take、排队取消和已授额取消先从唯一 requests owner 移出 state，再在 controller gate 外析构退费；context 在 controller 寿命内复用。controller 析构先失效 owner、锁外释放全部 state 与 context charge，再注销共享父 child，外部 dormant handle 只保留不带 charge 的 tombstone control block，不再延长 controller 或父预算身份。原 reservation slot、FIFO 冲突规则、独立资源越过、通知派发和 CPU 退休 consumer 不变，public/protected 产品 API 与 `tool/strokes`、scheduler、Painter、PaintDevice 均零增长。

新增 `budgetWaiterStateStorageIsChargedAndReleased` 用 1 B metadata 上限证明 context+state 的空载控制存储预检拒绝且 live/reserved 归零；再把 child 接到共享父额，验证首次 Ready 同时收费 context+state，take 后只留下可复用 context，Waiting→reset 只增加/退还 state，child 析构后 registration、state、context 在父层全部归零。额外保留 dormant waiter 跨 controller 析构，证明 handle 失效且不会阻止共享 child 注销。连同原 FIFO、取消/寿命、queued cancellation、durable transfer、unused capacity、wake 和 16 个退休参数组合，arm64 为 **26 passed / 0 failed / 0 skipped**。架构门与源码身份以本节证据目录的最终日志为准。证据见 [waiter 控制存储收费记录](evidence/br1_waiter_state_budget_20260929/README.md)。

**裁决关闭“每请求 state 本体、每 controller 冷 context 本体、唯一 owner、空载自占容量预检及失败/取消/take/析构退费”子范围。** `QSharedPointer` control block、prepared wake/monitor 节点、reservation slot/free-list 高水位、可能逃逸 `std::function` 小对象缓冲的 capture，以及 worker dispatch task仍须逐一决定收费 owner；不能把 context/state 本体收费外推为 notification/dispatch/retry/pass 完整收费。跨 store 公平和前台 continuation 仍须绑定原请求所有权，M6–M8 与默认启用资格不变。

<a id="budget-wake-state-storage"></a>
### 16.24 S09 / S10：prepared wake 状态实际收费与节点收敛（2026-09-29）

本批继续收敛既有 `KisPageReclamationWake`，没有建立第二套通知、等待或调度入口。原实现以普通 heap 的 `make_shared` 分配每个 wake state，并用两条 `std::list<std::shared_ptr<...>>` 表示 dormant/ready；因此一个逻辑 wake 至少有 state、shared control block 和 list node 三处隐式分配，§16.23 的 context/state 收费并未覆盖它们。现在 state 本体通过现有 mutation-storage allocator 计入所属 PageStore 的 `MetadataArena`，dormant/ready 的前后链接内嵌在同一个 state 中；单个 `placeWake` 统一摘链和入链，删除每次 wake 独立的 list node 分配。既有 `kisPreparePageStoreReclamationWake` 只增加 private budget 参数，预算 waiter 和 read last-use 的既有 constructor/call site 各传入原 backing controller；没有增加产品 API、上层 pressure 结果或 `tool/strokes` 依赖。

预算 waiter 的空载永久容量预检同步扩大为 context + request state + wake state，避免先建立 wake 后才发现最小请求永远无法进入。`KisPageReclamationWake::reset` 在预算 controller 仍存活时先从 monitor 链摘除，再分离并归还 state charge；如果 monitor 已取得一次强引用，余下 tombstone 只负责稍后释放原始内存，不再携带预算身份。read coordinator 也在自身析构中先 reset wake，而其 backing controller 后析构。producer `notify()` 仍只在 monitor mutex 下移动已存在节点并 signal，不分配、不执行 callback；process-global executor 不按 store 重复收费。

`preparedReclamationWakeCancellation` 现用真实 4096 B metadata controller 验证 wake 创建后 live 增加、move 与多次 reusable notify 不重复收费、reset 后归零；预算 waiter、CPU 退休、read last-use 的目标联合矩阵为 **67 passed / 0 failed / 0 skipped**。架构门为 21 manifest / 25 ownership / 16 census / **1,829 indexed APIs / 19,891 reverse-call edges / 17 callbacks / 19 intrusion files**。唯一新增 indexed API 是 PageStore 私有实现中的 `placeWake`，用于替代两条容器节点维护路径；既有 exported prepare 函数只是内部签名扩展，public/protected 产品接口没有增长。构建、测试、结构结果与源码哈希见 [wake 控制存储证据](evidence/br1_wake_state_budget_20260929/README.md)。

**裁决关闭“prepared wake state 本体实际父子收费、每 wake list node 消除、budget/read 两个现有 consumer 接线、空载预检与 reset/析构退费”子范围。** `shared_ptr` control block、可能越过 `std::function` 小对象缓冲的 capture、`QRunnable`/worker dispatch task、reservation slot/free-list 高水位、其他 retry/pass/terminal 存储仍开放；跨 store 公平与 scheduler continuation 仍须绑定原请求 ownership transfer。本批不关闭完整 S09、S10、BC9 或 M6–M8。

<a id="wake-control-block-convergence"></a>
### 16.25 S09 / S10：prepared wake shared control block 消除（2026-09-29）

§16.24 虽已让 wake state 本体收费并删除 list node，但 handle 与 monitor 临时所有权仍由 `std::shared_ptr<KisPageReclamationWakeState>` 的普通堆 control block 承载。给这块实现相关的隐藏布局做估算收费不能证明实际字节，也会把标准库实现细节写进预算合同。本批直接删除该 control block：`KisPageReclamationWake` 只持有 state 原始指针，state 内新增一个已随本体收费的原子引用计数。handle 是基准引用；monitor 或 shutdown 在 clock mutex 下看到已登记节点时取得一次临时引用，移出锁后执行 callback/清理，再用唯一的 `releaseWake` 归还。move constructor/assignment 用 exchange 明确转移基准引用，避免原始指针的默认 move 复制所有权。

reset 仍先在 clock mutex 下摘除节点，再把 `storageBudget` 原子式分离并在 controller 存活期归还 charge，最后释放 handle 引用。若 callback 已在运行，monitor 引用保留 state 和 dispatch capture；此时 reset 已归还预算且 tombstone 不再保存 controller 身份，callback 结束的最后一次 intrusive release 只析构并释放原始内存。这样保留原“回调可与取消并发、晚工作不复活 owner”的协议，同时每 wake 从 state + list node + shared control block 三处动态存储收敛为一块已收费 state。process-global clock/executor 仍只存在一份，没有按 store 复制或收费。

`preparedReclamationWakeCancellation` 增加 in-flight reset 交错：monitor callback 用 semaphore 停在执行区间，主线程 reset 后 metadata live 立即归零，capture 在 callback 放行前继续存活，回调结束后释放。连同 waiter、退休和 read last-use 的目标联合矩阵仍为 **67 passed / 0 failed / 0 skipped**。架构图为 21 manifest / 25 ownership / 16 census / **1,830 indexed APIs / 19,897 reverse-call edges / 17 callbacks / 19 intrusion files**。相对 §16.24 只增加一个 PageStore 私有 `releaseWake`，统一三处最后引用释放；没有增加 exported/public/protected 入口，也没有扩张 `tool/strokes`、scheduler、Painter 或 PaintDevice。构建、测试、结构结果与源码哈希见 [wake control block 收敛证据](evidence/br1_wake_control_convergence_20260929/README.md)。

**裁决关闭 prepared wake 的 shared control block 分配与收费缺口。** 仍开放的是 budget wait context 的 `QSharedPointer` control block、可能外置的 callback capture、`QRunnable`/worker dispatch task、reservation slot/free-list 高水位以及其他 retry/pass/terminal 存储。context 的弱 handle tombstone 寿命不同于 wake 的单 handle+monitor 临时引用，不能为了净 API 数量把两者强行共用。跨 store 公平与 scheduler continuation 继续等待原请求 ownership transfer；完整 S09、S10、BC9 和 M6–M8 状态不变。

<a id="wait-context-control-convergence"></a>
### 16.26 S10：context 控制块删除、请求容量退出与 reservation 空闲链收敛（2026-09-30）

本批关闭 §16.25 留下的两个隐式分配来源。`KisBackingBudgetWaitContext` 的 `QSharedPointer/QWeakPointer` 控制块已删除；复用现有 Boost 依赖的 `intrusive_ptr`，引用计数放进已实际收费的 context 本体。waiter 仍只有 context + sequence，保留的是失效寿命锚点，不拥有 controller、请求 state 或 reservation。`isValid/take/reset` 继续在 context→controller 原锁序下复验 owner 和 sequence。两个 ADL retain/release 钩子替代旧 `KisBackingBudgetWaitContextDeleter`，只在既有 PageStore 私有头导出以满足模板跨库链接；waiter/public 产品方法集合没有增长，页或预算身份没有向主干上移。

为了避免 dormant handle 保留原 context 内的整组请求容量，32 项 requests 改为 context 唯一拥有、通过既有 mutation allocator 收费的固定长度 vector；不在登记后增长。空载不可约容量预检明确包含 context 本体 + 32 项指针存储 + request state + wake state。controller 析构在原 gate 内使 owner 失效、取消 wake 并移出请求数组，锁外真正释放 state 和数组，再分离小型 context 锚点的 charge、最后注销共享父 child。未安装候选的 owner 保持为空；scope guard 在准备失败或竞争输掉时先 reset wake，解除 callback 对候选的引用再退费，避免未安装候选形成引用环。安装后的 wake/context 引用由 controller 唯一负责在退出时解除。

`m_freeSlots` 的独立 vector 同批删除，inactive `ReservationSlot::nextFree` 与 controller 的一个 head index 承载原空闲索引链。reserve、commit、retain 与 release 继续使用原 cookie/generation 和预算计数；回收旧 slot 不需要另一个容器的容量，也不扫描历史 slot。索引达到 `quint32` 上限时拒绝增长，避免截断后复用旧位置。slot 数组本体仍是普通 vector，其自身收费不能直接套 `KisMutationStorageAllocator(this)`：增长当前发生在同一个 controller mutex 下，该 allocator 会调用 reserve 并重入；这仍是下一资源批的实际缺口。

扩展原收费用例验证父额度恰少 1 B、context/wake 已准备但 request state 被拒绝时的全部候选退费，以及八线程首次登记后只保留一个 context/数组/wake 和八份请求状态。dormant handle 在 controller 退出后、reset 前即失效，父 live 为零。新增 128 个 reservation 的交错回收用例，保留相邻 grant 并覆盖 move-assignment、commit 和全部归零。CPU waiter/retirement/read 联合矩阵两架构各 **68 / 0 / 0**；共享父、Fresh budget 与 mutation-storage 实际路径两架构各 **5 / 0 / 0**，本批合计 **146 passed / 0 failed / 0 skipped**。结构图为 **1,832 indexed APIs / 19,946 edges / 17 callbacks**；21 manifest / 25 ownership / 16 census / 19 intrusion 由本批结构门核验。证据见 [context 与空闲链收敛记录](evidence/br1_wait_context_convergence_20260930/README.md)。

**裁决关闭 context 独立 shared control block、请求数组实际收费与退出释放、未安装候选引用清理，以及独立 free-list 分配子范围。** 小型 inert anchor 的原始内存仍可活到最后一个 handle/callback 释放；controller 退出时先退 charge 的既有政策只证明没有悬空预算访问，尚未证明墓碑内存的进程级字节/数量界。剩余完整控制存储批必须一起确定 slot 增长、自身准入、callback/worker task、retry/pass/terminal 与墓碑锚点的实际分配 owner、失败出口和退出收费；不再逐个产生等价通知变体。该闭环后用真实多文档压力裁决 S10，再进入原请求 ownership transfer 的跨 store 公平/continuation。完整 S09、S10、BC9、M6–M8 和默认启用资格继续开放。

<a id="reservation-storage-admission"></a>
### 16.27 S10：reservation 数组自身准入、父子收费和锁外增长（2026-09-30）

原 `reserveLocked` 在 controller gate 内增长普通 vector；直接套用调用 `reserve()` 的 mutation allocator 会重入自己。当前以一个仅供冷增长的内嵌 reservation 通过既有 activate/commit/release 计数引导数组自身收费；产品方法和父子组合协议不变。`prepareReservationSlot` 为普通 reserve、父层 reserve 与 waiter 登记准备原始数组的实际字节。增长串行化在独立冷 gate，分配与旧数组 free 在 accounting gate 外，短安装只复制记录并保持原 cookie。安装后原请求重新核验 FIFO/容量；期间已有 slot 释放则复用，不强制扩容；新增冷控制存储仍不能越过早到的重叠 metadata 需求。空载 preflight 同时计入实际已缓存 slot 字节，避免把新 controller 可授、当前 cache 下永远不可授的请求排队。

增长时旧数组仍收费，新数组全部字节先进入本地 `MetadataArena` 与原父 reservation；新旧共存峰值不藏进分母。内嵌冷 slot 不进入普通空闲链，不交给 waiter 或上层 caller；一般 slot 的 `nextFree`、generation 与原预算衍生计数继续唯一归 controller 所有。拒绝增长不改变已有 grant，已有空闲 slot 在 metadata 恰满时仍可复用。controller 析构实际释放数组并退费，再注销 shared child。仍被外部持有的父 controller 自身 slot cache 继续收费；真实产品弱池在最后一个 store 退出后释放父 owner，不能将“零请求”误报为“零 controller 存储”。

128 个 grant 的交错回收测试增加实际数组收费、满额扩容拒绝/原 grant 保留/释放后复用及两个 store 的父额度拒绝和退出返还；fresh 可授、带历史 slot cache 永久不可授的 metadata 请求对照证明登记前拒绝，不留永久 Waiting。原 owning-storage、failure-atomic 与 wake 测试把 controller cache 和已释放请求资源分账；自动 last-use cleanup 先准入冷 wake 再测保护释放区间，保留原 overflow 实际释放断言。最终源码 CPU mutation 与 Reference 两架构各 **1,246 / 0 / 0** 和 **648 / 0 / 0**；Freehand 正常压力/取消两架构各 **4 / 0 / 0**，原 24 MiB、pool/swap 为零不变。结构门通过，总计 3,796 / 0 / 0 只覆盖上述范围，不能称为完整 M8 或性能资格。UI 中间启动失败由缺少 prefix/shape 插件导致，调试定位与全部失败保留在[本批证据](evidence/br1_reservation_storage_admission_20260930/README.md)；未修改任何资源或 shape 产品代码。

**本段关闭 slot 数组动态存储本体、冷增长自准入和实际父子收费缺口；没有新增 pressure/continuation 产品 API，没有修改 `tool/strokes`、painter、PaintDevice 或 scheduler。** 增加一个私有冷准备汇合点及原始数组 deleter，替代原 gate 内 vector 自动增长；当前图为 1,834 APIs / 20,078 edges / 17 callbacks；结构门通过 21 manifest / 25 ownership / 16 census / 19 intrusion files。完整控制存储批仍须处理 callback/task/retry/pass/必要终结和墓碑实际尾内存；这两类真实 owner/失败出口统一后再验收真实多文档进度和原 job 接续，禁止以继续添加通知变体代替业务结果。M6/M7/M8、BC9、默认启用和 BR1-PERF 均未关闭。

<a id="m6-m8-completion-matrix"></a>
### 16.28 M6–M8 完成矩阵与功能分支覆盖（2026-09-30 盘点，后续原位更新）

盘点对象为当前 `refactor/brush-s2-predefined-sanity` 的已检出代码，最新产品实施边界为§16.142，机会门与计量缺项沿§16.134–§16.139。本节不新增运行资格；源码映射继续维护在 [CODE_INDEX](br1_modification_guide/CODE_INDEX.md)。**CP1、CP2已关闭；M6驻留CPU子集已实现、完整验收未关闭；固定M5 Fresh/H4原四桶已通过且§16.142重验8/8保持，原handoff20%/30%协议失败保留，新§6.1门正式资格未闭合；M7尚无生产commit-only handoff；M8已有首条真实direct开发入口闭环，剩余入口及资源出口未关闭。正式阶段通过为0/3。** M8子范围提前接线不改变§7的阶段验收顺序。

下表的“已实现”只裁决列明的代码范围；“部分”表示已有实际消费者但该项完整出口仍开放；“未实现”表示目标生产协议尚未接入；“未验收”表示缺少当前阶段的完整资格。功能分支盘点对应入口、模式、拒绝和终结路径。当前构建及证据没有提供 gcov/llvm-cov 分支覆盖率，不能从 QtTest 数据行或测试总数计算代码覆盖百分比。

#### 完成矩阵

| 阶段 / 交付项 | 实现情况 | 已成立的范围 | 尚缺的完成条件 / 修改映射 |
|---|---|---|---|
| M6：唯一 selector 与 native/generic 接线 | 已实现 CPU 子集 | 两种载体消费同一 recoverable 准备；没有候选时保留 Fresh | 非驻留恢复来源未接入；完整资格不能由入口接通替代；S06 / [03a §11](br1_modification_guide/03a_handoff_implementation_map.md#11-s064s067驻留-cpu-before-的生产联合消费) |
| M6：exact before、物理 claim/retag、统一终结 | CP2、已知拒绝及冷准备/借用优化完成，正式未验收 | §16.145完整03c候选已实现：P/R/F/C核定76/2344/5363/76，pin2420→152精确兑现；未插桩两架收益未确认，完整回退，当前代码保持原路径。§16.142既有删除与收益未确认保持 | 正式校准2/20、联合hit0/4和miss2/16保持；冷协议独占单价/关键路径、metadata实际驻留分母、完整CP0仍欠；已核定数量不能增加formal资格 |
| M6：legacy cache / raw / batch 消费者 | CP2安全范围完成，业务迁移未完成 | §16.109–16.112关闭raw/batch/G0/clone拒绝；§16.113核验共同plan与epoch联合时序，原exact重解析和保守排斥保持 | idle强引用及其他业务consumer迁移归CP6–CP9；refs/users/raw pin/Reserved不放宽，见[完整CP2审查](evidence/br1_cp2_epoch_completion_20261004/cp2-audit.json)及[03b](br1_modification_guide/03b_legacy_cache_migration.md) |
| M6：安装与并发资格 | §16.137/16.142冻结资格保持；§16.145候选已回退，阶段未验收 | 本批候选相关组9470/0/0、回退后9402/0/0分列，均含原PaintDevice stress排除；回退结构恢复2211 APIs/29025 edges，6工具通过。候选原Fresh/H4重验8/8；§16.142的merger等4554/0/0及旧完整矩阵保留各自冻结身份 | 候选未确认业务收益，不授默认/正式资格；原stress崩溃未修，正式校准18桶、metadata分母、CP0 required及完整阶段资格仍欠；S05/S06/V01 |
| M7：epoch admission 与 commit-only 选择 | 未实现 | 现有 claim、publication prepare 和原子准入可作前置能力 | capture 与 handoff 同一 gate、无旧保护资格、专用 transition 与真实 consumer；S06 / §4 |
| M7：全部输入/claims、不可失败安装与 fence | 未实现，未验收 | direct cursor 的 backing preflight 已有，但仍是可取消写 | 首字节后失败为零；≤8 页、≤256 KiB、hold P99≤100 μs；第二页拒绝时第一页必须仍未写入；§4/V01 |
| M8：persistent session、borrow、pending 与 checkpoint | 已实现能力子集 | 原 history/transaction 持有 session，稳定 slots、job borrow、完整 checkpoint/再开放与局部复用 | 完整 job 冷资源、subset/cut、所有业务 consumer 和压力进度；S02–S05 |
| M8：真实 direct stroke 生命周期 | 已实现开发入口子集 | Buildup、RGBA8/OVER、单 painter；真实 multi-dab/update、dirty 前 checkpoint、finish/cancel、整笔一次 undo/redo、递归 producer drain | 正式工具默认关闭；BC9 全出口及 BC10 完整模式/性能资格；BC1–BC7/BC10 |
| M8：显示与适配联合发布 | 部分 | packed/cursor add/update 的 canonical 与 prepared adapter 联合窗口关闭 | clear/remove/default/copy/restore/purge 及 working/frame/LoD 发布族仍须逐族裁决；S04/S05/JP1–JP8 |
| M8：复杂入口与剩余迁移 | 未完成 | fixed/sharpness、multi-dab、同步 bitBlt/mirror 已有实际 owner 消费者 | 通用 current/self-source、selection/path、indirect/mask、多 painter、wrapped/LoD、异步 target 寿命；BC5/BC8 |
| M8：硬预算、退休、压力和退出 | CP1 已完成；M8 其余资源出口部分 | §16.35–§16.107的原存储/owner/终结、实际capacity/VM释放、当前Darwin owned总硬界与真实fault停止规则保持；§16.108补齐Linux/Windows精确capacity/free实现和目标平台运行，并完成默认abort宿主合同处置 | [§16.108](#cp1-platform-exits-delivery)关闭完整CP1，不再保留CP1出口。CP5持续热点/公平/多文档/原job接续仍属M8后续包；M6/M7/M8正式资格仍为0/3 |
| M8：pressure continuation | 未实现 | cursor 准备拒绝时 callback 零进入、原 history 可由调用者重试；当前 Failed 仍正确取消 | 原未执行 job 的输入/队列位置/取消/析构权一次转交，释放后无新输入恢复，兄弟 job 不重放；[§16.20](#stroke-continuation-ownership-audit) |
| M8：undo/context、删除和最终出口 | 未完成 | 核心 delta、原事务 undo/redo、局部 API 合并/删除已有基础 | 普通 restore 全量索引路径、固定 K 成本、切层/笔刷/frame/LoD 缓存、剩余 caller 迁移与删除理由；U01/U02/C01/C02/V01 |
| BR1：默认启用与正式性能 | 未验收 | 局部正确性与结构门通过 | 当前同源完整 CPU/业务/资源及正式 M/K/E/upstream/Fresh 性能；不能用历史 M5 或局部零分配替代；§6–§7 |

以下实现段落说明对应冻结批次的增量，其中“仍欠／仍开放”只属于该批边界；当前实现和资格差集以§16.114和§17为准。

资源行按§16.47补充：exact标量查询与native CPU discovery已退出嵌套Qt投影；generic read只准备实际收费的候选数组。capture Private/control、原cut的version/removal/surface数组及per-cut default map已收费，retain/release直接修改原overflow slot、同释放记录承接实际cleanup。这些容量不再列待办；该批generic mutation/publication投影、其他Qt wrapper/固定成本及完整永久尾退出仍开放。

§16.48–16.49进一步删除空publication效果协议和detach重复快照；原PreparedPublication独占Data、entries/deltas/growth、authority哈希节点和嵌套安装保护容量均已收费，全部MetadataArenaGrowth holder迁移。原metadata directory/block费用经同一accounting owner跨controller退场保留至实际free。通用StateMachine临时Qt投影/集合、mutationBase/overlay与既有shared核心bootstrap仍欠，完整资源行没有关闭。

§16.50把native/generic/semantic共用首写入口的mutationBase快照改为同一shard cut的标量查询，原两版本与嵌套保护列表复制删除；候选观察仍不授予write/physical claim。通用StateMachine转换和overlay存储继续开放。

#### M6 / M7 分支覆盖

最新 CPU mutation 日志中，以下三组在 **arm64、x86_64 各有 80 + 64 + 144 = 288 个通过数据行**；这是三个测试的组合数，不是实现覆盖率，也不能相加为阶段完成度。入口与断言可查 [productionRecoverableHandoff](../../krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:7439)、[productionHandoffFallback](../../krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:7538)、[productionHandoffConcurrentConsumers](../../krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:7619)；对应最新日志见 [arm64](evidence/br1_reservation_storage_admission_20260930/cpu-arm64.log) / [x86_64](evidence/br1_reservation_storage_admission_20260930/cpu-x86_64.log)。

| 功能分支 | 覆盖与证据 | 边界 / 剩余 |
|---|---|---|
| Ready resident CPU alternate → recoverable 命中 | 4 BPP（1/4/8/16）×5 route（native preserve/payload/discard、generic preserve/discard）×4 terminal（commit/cancel/abort/undo-redo）=80/架构 | 验证地址复用、旧 G 经 B 读取、拒绝 Fresh 分配时仍成功、无新增 provider payload；不覆盖 SSD before |
| 无 before / pin / lease / last-use / raw ref / before 不可用 / transient 上限 / 多 provider owner | 4 BPP×native/generic×8 blocker=64/架构；Fresh 或明确拒绝且旧身份保留 | 多 owner 为保守拒绝；不等于跨 store handoff 寿命已经开放 |
| 九类消费者在准备前后/安装后交错 | 4 BPP×native/generic×9 consumer×2次序=144/架构；涉及 read pin、lease/release/last-use、swap、owner 注册、新 capture、before pin | 是实际设置的两类时点；不能推定所有 epoch/ABA/晚 completion/close 交错已覆盖 |
| 物理 ABA/错误 identity、retag/retire/revoke、cache 暖读 | PhysicalClaim/ResidentRead 与 legacy fixture 已有代码及冻结证据；见 [03a](br1_modification_guide/03a_handoff_implementation_map.md)、[legacy 证据](evidence/br1_s06_legacy_identity_20260927/README.md) | 这些目标没有在 §16.27 的最新局部回归中全部重跑；全出口继续开放 |
| SSD/archive / 非 Ready transfer 作为 before | 当前生产共同计划只选择 CpuRam alternate | SSD/archive 尚未接入；未 Ready transfer 不取得恢复资格；不得临时复制 before 制造命中 |
| M7 无 alternate、无旧保护 → commit-only | 生产 selector 仅有 SemanticOnly/ReusePending/FreshPayload/FreshDiscard/FreshCow/RecoverableHandoff；[枚举](../../krita/libs/image/pagestore/KisPageWriteCoordinator_p.h:54)没有 commit-only 分支 | 尚无生产正例、capture/fence 双次序及首字节后不可失败测量；所有 M7 正式分支待实现 |
| GPU / UMA / discrete handoff | 不在当前 BR1 CPU production 子集；BR2 production 门仍关闭 | Vulkan foundation 的历史测试不覆盖这些产品分支 |

#### M8 业务 / 失败 / 资源分支覆盖

入口资格由 [strategy 的实际条件](../../krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:350)约束；[opt-in 默认值](../../krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.h:140)为 false，正式工具没有开启调用。源码有某种 iterator/clear/copy 能力，不足以说明它已纳入 persistent stroke 的完整生命周期。

| 功能分支 | 当前覆盖 | 缺口或证据边界 |
|---|---|---|
| 原 session 同页重复与 checkpoint 再开放 | 当前 CPU 全集包含 1/10/1000 repeats、4 BPP、commit/abort；[checkpointKeepsOriginalScope](../../krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp:5648) | 是能力层重复验证；真实 brush 每页必要 COW 次数与完整性能仍待测 |
| direct Buildup、RGBA8/OVER、单 painter、无 selection/indirect/mask/wrap/LoD | 开发入口已有真实 autobrush，多 update 与同一策略 undo/redo、finish/cancel；[联合 fixture](evidence/br1_direct_stroke_joint_20260929/README.md)双架构各8/0/0 | 冻结在该批源码；早期 Wash fixture 的 direct 资格已被修正，不能引用它代替本组；默认关闭 |
| admission / pixel failure signal / checkpoint / finish 拒绝 | 同一 Freehand fixture 的四类终点已有：无成功 undo、原 cancel、后继 sentinel 不执行 | pixel 行是既有失败信号联合终结；实际低层 swap-in 故障另由 Painter completion fixture 验证；不是全部像素故障点 |
| multi-dab 页分区、scalar fixed、1px sharpness、bitBlt/mirror 同步读写 | 已有实际 owner consumer 和局部目标证据；见 [首条入口](#direct-stroke-pilot-delivery)及 [fixed 指南](br1_modification_guide/01k_fixed_source_and_sharpness.md) | 不能外推通用 current/self-source、任意 paintop/composite/depth 或异步多 target |
| 普通 direct cursor，多页准备预算拒绝 | callback=0；原 history/已有 pending 保留，压力解除后同 owner 重试；[冻结证据](evidence/br1_operation_pressure_boundary_20260929/README.md)arm64 131/0/0、x86_64 3/0/0 | 最新 §16.27 没重跑完整 manager 矩阵；这是调用者重试，尚无 scheduler 自动继续 |
| semantic remove / staged alias / packed payload | 原语义/Fresh/payload 路径继续受保护，CPU 全集有语义测试 | remove/alias 对 cursor preflight 返回 Unsupported；packed payload 使用直接初始化路径；不授予 M7 或全族联合发布资格 |
| H/V/random/repeat/wrapped iterator、planar、clear/default、copy/clone、restore/purge | 部分底层能力/adapter 已有消费者与冻结回归 | 各入口的 persistent scope、读意图、adapter/extent、失败与退出没有完整联合证明；不能统一填“已覆盖” |
| selection/path、indirect/mask、多 painter、LoD/wrap | 首条 persistent 入口明确不纳入这些模式 | 保留现有路径；BC5/BC8 的业务 owner、target/merge、source/cut 和取消责任仍待迁移 |
| 单文档长 stroke +慢 reader +递归无输入 drain | 最新双架构重测，正常压力 case 为24 MiB、pool/swap=0；读者旧值稳定、finish、undo/redo、最终 resident=0 | 测试没有因可等待容量拒绝而暂停/再继续；不能替代压力释放后的无输入自动恢复 |
| 受限预算用户 cancel | 最新双架构重测8 MiB basic stroke，cancel 后 resident=0 | 与24 MiB长 stroke 成功为不同 workload；不宣称8 MiB长 stroke 成功 |
| 共享资源准入与释放 | 当前 Reference 全集覆盖父额合并限制、空闲 store 不分额、退出返还；CPU 全集覆盖 waiter/cancel/cache 实际收费；[§16.22](#shared-nonpayload-budget)及[§16.27](#reservation-storage-admission) | 两 backend 资源 fixture 不等于真实多文档并发长笔；callback/task/tail 实际收费与无饥饿公平未关闭 |
| 慢退休 / SSD耗尽 / 持续热点 / 完整 close / pressure 自动继续 | 局部退休重试、last-use、拒绝保留债务已有测试 | 完整组合、总 nodes/bytes/time 硬界及原 job 接续未统一验收；S08–S10/BC9 仍开放 |
| undo 固定 K / 切笔刷切层 / frame/LoD context | 原 undo/redo 正确性及核心 delta 有基础 | 普通 restore 全量 export/sort/rebuild 与上下文完整成本/缓存失效仍未关闭；U01/U02/C01/C02 |

#### 证据口径与下一完成点

最新 §16.125 的同源双架构每架完整16目标5486/0/0、ReadBaseline45/0/0、persistent五方法11/0/0及Vulkan foundation14/0/0，38进程共11112/0/0，均actual0/reaped，含init/cleanup；[当前证据](evidence/br1_cp3_candidate_storage_20261006/README.md)绑定产品Git blobs和两个构建目录的实际运行物。原生命周期夹具补充0/1/2/33页与1/4分片；修正物理slot复用后当前/父专项均282/0/0，初次54注册失败独立保留。完整oracle/生产/失败/时序/压力保持，LIMIT_LONG_TESTS未注册范围、其他模式/配置及正式性能不由总数取得资格。

最近生产改动已进入 **CP3/M6 冻结**。CP1/CP2分别由§16.108/§16.113结算。§16.132在已完成借用/六类扫描之后复用原handoff槽的单元素缓冲区和目标claim节点，K16请求313→283；Rosetta直接配对约1.99%局部收益，ARM区间跨零。当前Fresh/H4四桶全过，native K16约13.55%/14.50%、下界12.06%/13.98%仍未达30%，K1未达20%。下一补native metadata准备/工作投影及共同seal/commit的独占成本和必要下界，不能按剩余分配次数或旧public热点直接重写容器。原容量、拒绝、身份/物理claim、晚free保持；metadata驻留分母/CP0 required继续开放。完整顺序由[§17](#br1-closure-schedule)统一，M6通过后执行CP4/M7。

<a id="immediate-task-convergence"></a>
### 16.29 CP1 实施：即时回收任务与最后 owner 归还（2026-09-30）

本轮先核对收敛债务与能力缺口，选择修复重复任务存储和投递失败状态，不扩大 stroke 模式或增加 M7/continuation 接口。退休通知、退休 pass、history pass 和 budget waiter 的投递失败处理不完整；最后一个 root 引用的归还还会重新分配析构任务。这些安全问题可先修复，不能以本批代替 CP0 的 upstream 对照准备。

原 `ReclamationExecutor` 继续使用唯一专用 QThreadPool worker，冷启动一次常驻 runnable，以侵入 FIFO 消费实际 typed task。每次投递的 `QRunnable::create` 与 `std::function` 包装已删除；drain 等待该队列和活动 task，仍不等待未来 deadline。worker 身份覆盖 callback、capture 销毁、实际 task 释放和最终 owner 归还；各 pass 仍排入同一 FIFO，deadline monitor 和 semantic owner 不变，没有第二 executor 服务或 release 权威。

last-use worker 的实际 task/capture 经原 MetadataArena 准入，物理释放并退费后才归还 root 引用。退休通知/退休 pass/history pass 共用这一最终归还点；投递失败撤销额外引用、notification 计数和调度标志，原记录继续由队列持有。budget waiter 投递失败保留请求和 scheduled=false。Private 冷准备一个独立终结 node；最后引用在生产通知线程上归还时，只转交该 node，不再分配任务或线程。

**这是 CP1 已交付子范围，不是 CP1 结算。** 其余 task、独立终结 node 和一次性 runtime 存储尚未全部收费；callback/context/control block、deadline/map node、retry/record、pass 临时存储和 controller 后的实际尾内存仍须统一原收费 owner、失败与最后释放。不能给晚于 controller 释放的对象直接装 raw budget 指针，也不能把预算分配塞入 owner/provider 安装 gate。下一轮继续完成这些存储及冷准备责任，不再添加等价通知类型；M6/M7/M8 资格仍为 0/3，默认启用、完整 BC9 和 BR1-PERF 不变。

最终目标结果、保留的测试初始失败与结构/身份见[本批证据](evidence/br1_immediate_task_convergence_20260930/README.md)；实际替代和删除见 [API 账本](br1_modification_guide/API_CONVERGENCE_MAP.md#immediate-task-api-delivery)，逐函数清点见 [代码索引](br1_modification_guide/CODE_INDEX.md#immediate-task-code-index)。本批只修改 PageStore 内部和原 Reference 测试，没有修改 tool/strokes、UI、painter、PaintDevice 或 scheduler。

<a id="retained-storage-owner"></a>
### 16.30 CP1 实施：实际控制存储与 controller 后收费寿命（2026-09-30）

本轮按 §17 先审 API/分支债务：wake reset/controller 退出会提前返还 monitor 或 inert handle 仍持有的实际存储，read/retirement shared 弱控制块缺少同寿命收费。选择实现 CP1 的必需收费寿命，同时删除提前退费、raw storageBudget 字段和原 ensureWakeContextLocked 包装；不增加 stroke 模式、M7 或 continuation API。

既有 MutationStorageAllocator 增加 retained 模式，一个原 controller 冷准备一个收费 owner。真实 allocation 与 allocator handle 持有它；allocate_shared 收费包含真实弱控制块，普通 raw 模式不加 allocation header。controller 退出先拒绝新 retained 分配，清掉原 requests/array/slots，再保留原共享父与原 child 身份，存储物理释放后才退费，最后收费 owner 本体释放后才注销 child。晚 weak/control/inert/monitor 尾不 pin PageStore/payload/权限，但仍占原全局容量，不能通过弱父池重建预算绕过硬界。

原 waiter context、prepared wake、已传预算的 typed task；read ActiveReadRecord/last-use context；retirement Wait/WakeContext/grant control block 与 retry DelayState 已接同一机制。read record/node/context 冷准备移出原 store owner gate，Resolving 排除重复消费，拒绝恢复 Pending 且 provider 尚未进入，安装前重验 closing/identity，失败候选在 owner gate 外释放。close 在 active map 遍历前准备 context，原 metadata/physical debt 不因通知准备拒绝而丢失。

**本批结果为 CP1 子范围。** 未收费的外置 callback capture、deadline map/record list/orphan container、其余 waiter/retirement/history task、pass scratch、必要 terminal/runtime 及硬满时终结/自主进度仍开放。下一段从这些真实分配和必要冷预留消费点继续，不能将剩余 raw allocation 直接装上已失效 budget 指针，也不能把终结必需存储推迟到硬满时才申请。完整 CP1 未结算，M6/M7/M8 正式资格仍 0/3，默认入口仍关闭。

当前同源目标验证双架构 CPU 各1246/0/0、Reference各653/0/0、原 Freehand 压力/取消各4/0/0，合计3806 passed；新增弱引用/父硬界、并发退出/对齐和 monitor 活动尾寿命结果。实际缓存收费与恢复夹具竞争的初始失败均保留并回修，没有放宽预算或语义门。见[本批证据](evidence/br1_retained_storage_owner_20260930/README.md)、[代码改动与欠项](br1_modification_guide/CODE_INDEX.md#retained-storage-code-index)、[API替代账本](br1_modification_guide/API_CONVERGENCE_MAP.md#retained-storage-api-delivery)。本批生产改动仅 PageStore 内部，上层 public/protected API 净增0；CP0对照、正式阶段/性能与TSAN仍未获资格。

<a id="prepared-reclamation-tasks"></a>
### 16.31 CP1 实施：原回收任务冷准备、满额投递与终结收费（2026-10-01）

本轮先审分支/API与缺失能力，发现原history/退休pass、budget/read通知和退休wait仍在每次投递时分配task；terminal节点虽冷准备却未收费。选择补齐CP1的必要任务存储，并同步删除这些重复分配/捕获/dispatch bad_alloc回滚，不扩展stroke模式、M7或上层API。

原typed task统一支持冷准备/实际inline捕获，仍进入同一executor/FIFO。history/retirement各持一个收费node，budget/read context及退休wait持各自原node；原scheduled/inFlight gate排除重复入队，每次活动投递取得原root/context/self pin，原finalizer归还并接续。cache存活一直收费，不能因idle就退费；一次性schedule仍复用同一准备/释放实现。budget运行中的通知合并后在完成点再次投递，退休相同wait的重复通知合并，不新增通知队列或record权威。

store configure在原owner gate外准备terminal与两个pass节点，并在任何物理adoption前完成准入；拒绝保持失败。terminal一次执行delete Private，实际node用§16.30收费寿命在controller后物理释放/退费。删除旧TerminalCleanupJob与未收费make_unique；未配置、无任务节点的空root直接析构。

本批同源双架构CPU各1247/0/0、Reference各654/0/0、原Freehand压力/取消各4/0/0，合计3810 passed。新增目标验证恰满时同一node连续执行64次、cold拒绝保持旧node、capture到最终free才销毁；真实store按原public业务能力重建精确metadata上限，在满额facade退出后完成最后scope/view与root回收。capability释放会返还存储，不将此测试外推成整个pass始终零剩余字节或零分配。初始private测试调用编译失败和构建失败后的旧binary运行保留，后者不授予当前资格；没有为测试增加friend/getter。

**整个CP1仍未结算。** 实际callback/订阅外置capture、deadline map/每次retry准备、record/orphan容器、history/read/pass临时存储、tree/deferred cleanup一次性任务、runtime/clock及对应硬满失败/自主恢复仍开放。下一轮取这些实际分配的差集，不重复重建已有收费寿命、worker或冷任务。本批未修改tool/strokes或上层生产API，M6/M7/M8仍0/3、默认关闭，CP0/公平/continuation/正式性能/TSAN均未获得本批资格。见 [证据](evidence/br1_prepared_reclamation_20260930/README.md)、[代码及下一差集](br1_modification_guide/CODE_INDEX.md#prepared-reclamation-code-index)、[API替代](br1_modification_guide/API_CONVERGENCE_MAP.md#prepared-reclamation-api-delivery)。

<a id="callback-storage-convergence"></a>
### 16.32 CP1 实施：实际通知捕获、订阅与 deadline 节点统一收费（2026-10-01）

每轮先审查再选择：§16.31 的原任务已冷准备，继续新建任务或扩展 stroke API 没有必要；真正阻塞 CP1 的是外置 `std::function` 捕获、订阅节点/信号控制块、registry readiness 节点和 deadline map 节点。选择实现这些实际存储并同步替换旧路径，未提前进入 M7。

实际 typed 捕获以原 retained allocator 冷准入，复制只保留同一已准备捕获，派发不复制另一份 callable。生产 read/retirement/wake/deadline 原 caller 显式使用原 budget；budget waiter 的外来 callable 在冷准入时收费，W3 判定含实际 notify/wake 捕获大小，永久不可满足判定先于收费 cache 准备。取消、已取出 callback、controller 退出后的捕获和弱控制块都收费到实际 free；不授予 page/payload 权限。

原信号/registry readiness 表替换为预备的 intrusive 节点；signal/state 的真实 shared 控制块与 registry 清理捕获进入同一原付款寿命。registry、CPU binding 和 read owner 在门外准备，回到原门后重验 ticket/identity/closing，胜者只链接节点，失败候选在门外释放。取消仍按原单调 subscription ID；最后取消按原 signal identity/emptiness 删除记录；terminal 先发布状态、移除并释放 record，再通知。已有 signal 的首个付款 controller 退出后，新订阅用自己仍活跃的原预算准备节点，不向失效 owner 申请存储。原 registry Private/core source/terminal 索引没有因此获得收费资格。

原 deadline 的 O(log N) 排序与同一 monitor 保留，树节点嵌入原 DelayState；删除另一个 multimap 节点，queuedPin 只覆盖排队期间，cancel/pop/shutdown 先 unlink、后门外释放 capture/state。没有新增执行器、通知队列或重试语义权威；**每次 retry 仍准备新的 Wait/Delay/capture**，晚取消身份不能为减少分配而盲目复用。

同源双架构 Reference 各657/0/0、CPU各1247/0/0、Completion各83/0/0、原Freehand压力/取消各4/0/0，合计 **3982 passed**。新目标覆盖满额时64次捕获保留/调用不克隆函数、冷订阅/deadline 拒绝保留原信号/捕获、原付款退出后新订阅与最终弱块退费、deadline 在途尾；原注册/取消竞争、预算 FIFO 与实际 stroke 目标同时通过。测试只在整包改动后验证，初始失败和最终构建/运行身份保留；不推定全分配 interposition、完整硬满进度或 TSAN 已通过。

**完整 CP1 未结算，M6/M7/M8 正式资格仍0/3，默认关闭。** 下一实施优先处理丢弃原 physical ownership 前的 retirement record/orphan 准备与 partition 转交、pass 临时存储及硬满保债/恢复；retry 重建、history/read scratch、tree/deferred 一次性存储、Store/registry/provider 控制本体和 runtime/clock 固定成本仍在清单。不得重复领取已合并的 typed callback、prepared task/FIFO 和收费尾寿命。本批上层生产改动与 public/protected API 净增均0。见 [证据](evidence/br1_callback_storage_20261001/README.md)、[实际代码与剩余改动](br1_modification_guide/CODE_INDEX.md#callback-storage-code-index)、[API替代/删除](br1_modification_guide/API_CONVERGENCE_MAP.md#callback-storage-api-delivery)。

<a id="retirement-record-preparation"></a>
### 16.33 CP1 实施：backing 前准备真实退休节点，同一节点贯穿失败、分区与 close（2026-10-01）

本轮先核对原consumer与已收敛API：已有typed通知和prepared task继续使用，真正缺项是放弃physical ownership后才分配record、分区/pass/close容器反复造节点，以及orphan/admission/grant的另一个shared包装。选择实现必要存储，同时删除这些重复路径；没有提前扩展M7、stroke模式或主干接口。

原 `reserveBacking` 直接返回原payload/debt reservation与一个实际收费terminal node。Fresh/default/native/generic/import在provider进入前完成冷准入；拒绝返还reservation且没有physical result。initial adoption在第一笔registration前备齐整个真实节点数组/容量，回到原Store门后重验；注册与失败回滚保持原门内原子边界，节点转回同一已预留数组，门外物理free。直接ledger注册的原caller仍拥有其外部physical result，节点拒绝不会接收其所有权。其余ledger/core索引分配失败与完整回滚尚未结算，不能外推为所有准备点已关闭。

registered backing持有唯一节点，retag/handoff保留原节点；退休与close按原完整handle取走一次。被拒绝的未注册provider result保留冷准备的同一节点和原composite reservation。orphan/admission及原wait budgetGrant直接内嵌reservation，删除三种shared box。pending/retry/ready、实际worker batch/process、close/failed-close全部splice原节点，不再分配list/vector节点；原provider/last-use/预算判定与32项pass上界保留。节点只是收费存储，不能取得page/root/payload或retire许可；成功physical retire之后，节点仍收费到门外实际free才退费。

目标验证：冷存储余量只差一个真实节点时原backing准入拒绝、provider尚未进入且payload/debt reservation全退；registered与rejected-unregistered两条实际消费者在metadata恰满、provider连续拒绝后，经pass/process/close保持同一节点地址，最终physical retire与节点free分开核对退费。此恰满目标显式停用自动wake，只裁决节点转交与债务保留；不能称为全部等待/重试在硬满下自主恢复或全pass零分配。原physical handoff/retag/共享alias/index-growth断言按每个实际节点退费检查，所有payload与reservation归零断言仍保留。

最终源码统一结果为两架构CPU各1250/0/0、Reference各657/0/0、PhysicalClaim各379/0/0、原Freehand压力/取消各4/0/0，合计 **4580 passed / 0 failed / 0 skipped**。初始失败、最后回滚审查之前的通过、最终构建/运行身份均保留；不以旧binary或旧通过覆盖最后修复。结构事实仍21 manifest/25 ownership/16 census/19既有侵入文件，未放宽主干限制。本批上层生产改动与public/protected API净增均0；私有既有process/stop符号增加测试链接可见性，记录在API账本，不是新增业务函数。

**完整CP1未结算，M6/M7/M8正式资格仍0/3，默认关闭。** 下一有限端点是原retirement必要Wait/订阅/Delay/capture和generation-qualified retry重臂：准入耗尽时保留同一physical debt、无新输入能继续；同批审计剩余pass/core索引/效果清单，不再重做record分区或通知框架。history/read scratch、tree/deferred对象与一次性task、Store/registry/provider控制本体、runtime/clock固定成本及完整硬满释放/自主进度继续开放。见 [证据](evidence/br1_retirement_record_20261001/README.md)、[源码与剩余改动](br1_modification_guide/CODE_INDEX.md#retirement-record-code-index)、[替代与删除](br1_modification_guide/API_CONVERGENCE_MAP.md#retirement-record-api-delivery)。

<a id="prepared-retirement-retry"></a>
### 16.34 CP1 实施：原队列 retry 冷准备，恰满时保持自动恢复（2026-10-01）

本轮先审API/失败分支：每次retry重新分配Wait、task、capture和Delay，必要订阅被metadata硬满拒绝后，备用retry也可能无法准备，留下无人推进的原债务。选择关闭这个实际进度缺口，并同批删除重建路径。原 `prepareTask` 在configure门外、任何physical adoption之前一次准备pass、context、retry Wait/task/capture/Delay；全部候选成功后才安装。每条record的provider/budget订阅仍有独立弱身份；准备拒绝保留原record并转交同一个预付retry，无需新输入或手动process。

原Delay只保留一条冷准备/arm/cancel/takeReady路径：排序hook及实际收费存储复用，monitor发布当前generation，consumer最多取一次；cancel清除资格，晚通知不能授予下一代就绪。在途任务期间收到新arm通知，由原完成点coalesce并重排同一task，沿原self/root活动pin退出，不另建worker/债务队列。原1–100 ms退避和每次最多32条仍保留；dormant存储继续收费到物理free，不pin composition root。旧 `kisSchedulePageStoreReclamationAfter`、one-shot变体、每retry分配及对应bad_alloc清空分支已删除，六处测试caller改消费同一Delay协议；上层生产文件与public/protected API净增均0。

最终目标：registered与unregistered orphan在metadata恰满且订阅无法准备时至少自主retry三次，原provider恢复后自动drain；Current backing另有Debt额度占满对照，实际释放额度后无新request/input可继续。原冷timer在恰满下32次重臂/取消不增费；被阻塞的旧callback在cancel/rearm后不能取新generation。最终两架构各CPU1253、Reference659、PhysicalClaim379、Freehand压力/取消4，合计 **4590 passed / 0 failed / 0 skipped**；原自主取消、在途退出与业务回归包含在这次统一运行中。首次runner误指另一套 `_build/bin` 的结果保存在 `initial-unqualified/`，不授予当前源码资格；最终runner固定 `_build-br0-cpu/bin`、插件路径和期望数量，源码/实际二进制身份一起冻结。

结构门为21 manifest / 25 ownership / 16 census / 1905 APIs / 20654 edges / 20 callbacks / 19既有侵入文件，manifest与主干限制未放宽。该批对原queue/gen消费责任的描述更新不增加状态权威。源码增删从累积Git基线 `9697196acab538329359a2d6c5bc45c2cf001a36` 精确取差集；产品和文档独立本地提交，见 [证据](evidence/br1_prepared_retirement_retry_20261001/README.md)。

**完整CP1未结算，M6/M7/M8正式资格仍0/3，默认关闭。** 本结果仅覆盖列明的原退休retry自主恢复，不证明整个pass零分配：`prepareRetirementDebt({effect})`及ledger/provider/registry索引仍有实际分配；history scans/keys/candidates/effects、read release/cancel/effects、close shutdown handles/seen set/诊断，tree/deferred对象及一次性task、Store/registry/provider本体和runtime固定成本继续开放。下一批沿原read/history/pass owner把必要容量、收费、失败接续和最后free一起闭合；不再领取已经删除的retry重建或重做通知框架。见 [当前代码清点](br1_modification_guide/CODE_INDEX.md#prepared-retirement-retry-code-index)、[API替代](br1_modification_guide/API_CONVERGENCE_MAP.md#prepared-retirement-retry-api-delivery)、[下一领取](br1_modification_guide/NEXT_EDITS.md#closure-next-work)。

<a id="read-terminal-storage"></a>
### 16.35 CP1 实施：原 read 终结节点、固定重试与读选择保护（2026-10-01）

先审分支/API：原cancel/release重试仍分配ID deque，ack/close/worker复制matching/pending/released数组；last-use订阅准备拒绝后只能等手动ack/close，GC通知拒绝还可能丢掉已ack记录的清理责任。因此选择实现必要原owner接续并同步删除旧容器和Store聚合，不增加stroke、M7或第二通知权威。

原configure在physical adoption前准备read context/task/wake/可重臂Delay，替代last-use懒建。原request/lease身体内嵌重试hook，原ready节点和任务处理至多32条，非终态或拒绝用同一1–100 ms退避timer继续；在途timer发布由原任务完成点coalesce。取消已完成metadata release但GC通知尚未接受时保留原request；last-use已ack但GC通知拒绝时保留原lease/key，直到原history owner接受。原cleanup栈scope转移预算收费map节点及metadata blocks，owner锁外实际释放后才归还activity；常驻cache不因idle退费。

request节点必须**在读选择之前**门外准备，随后读选择与AcquireRead保护共享owner锁区间。统一验证曾发现arm64原generic removal的临时default在选择后冷准备窗口被GC，读返回空；现在原cleanup先持有预付节点，原register只填值/转节点并保护，消除这个新窗口。effects退休调用的异常出口也由作用域保证重锁及归还activity。新增两个private操作分别服务真实冷准备和统一GC终结；旧懒prepare、ID deques、ack快照、releasedKeys结果及Store/Publication的QVector包装同批替代，见 [API账本](br1_modification_guide/API_CONVERGENCE_MAP.md#read-terminal-storage-api-delivery)。

最终两架构 **4608 passed / 0 failed / 0 skipped**，各CPU1262、Reference659、Physical379及Freehand两个pressure/cancel方法4。9个新增数据行使用原read/metadata/epoch/history/retirement组合及真实imported replica，预算在构造前固定为64 KiB，通过实际allocator占满；没有修改Store初始化后冻结额度的合同。三种终态、begin/cancel-close重臂及stop后晚completion、订阅拒绝后的至少三次自主pass、actual node free/活动pin归还、request/lease准备拒绝且provider=0及同request恢复均验证。该组合不等于整Store恰满close/history物理退休；既有Store lifetime/close/history目标在最终CPU全组重新通过。初始失败和修复边界详见 [证据](evidence/br1_read_terminal_storage_20261001/README.md)。

生产6文件增419/删227，测试1文件增204/删0；另有3个审计JSON。上层tool/strokes/Painter/PaintDevice/scheduler改动和public/protected API净增0；private层原19个方法扩大测试可见性，新增冷准备方法也导出，范围在账本列明。最终结构门为21 manifest / 25 ownership / 16 census / 1907 APIs / 20761 edges / 20 callbacks / 19既有侵入文件，未放宽manifest。产品父提交固定 `125ed0c0e2a7d5224a062239330066a638803e88`，文档父为 `fe39219ea0c6c76bb5e2cef050a21642017cd644`；最终commit及33份源码/12份运行身份见证据，普通编辑使用显式补丁。

**完整CP1未结算，M6/M7/M8正式资格仍0/3、默认关闭。** 此处仅关闭列明read节点/索引/快照和固定重试子范围；history通知内部QSet/keys/scans/candidates/effects、captured release deque/版本复制、retirement core effect/operation及ledger/provider/registry索引、close handles/seen/诊断、tree/deferred对象与一次性task、本体及runtime/clock固定成本在本批冻结时仍开放。不是全pass allocator interposition或全局bad_alloc失败原子性证明。captured欠项随后由§16.36更新；当前领取从最新实际差集开始，不重做已删除的read包装。

<a id="captured-release-lifecycle"></a>
### 16.36 CP1 实施：capture 准入与原释放记录的完整生命周期（2026-10-01）

按整体收敛技能复核后，目标仍是 capture→history→retirement 的接受后交接。先关闭有明确准入点的最小完整责任：原capture在取得任何root/version保护前准备收费释放节点及immutable版本容量；销毁和部分准入回滚转交同一节点，原read owner负责推进到接受及实际free。history扫描/效果与provider operation有各自权威和准备协议，本批保留在同一剩余模型，不为它们另外加失败包装或宣称整包已完成。

原 `sealedPages` QHash 与析构版本复制合并为一份排序版本数组，查询用二分查找；冷容量准备出owner gate后重新选择root/delta，再在同一gate取得保护。只记录实际取得保护的前缀，后页拒绝或bad_alloc经原释放入口回滚。旧 `PendingCapturedRelease`、retry deque、failed/released临时数组和释放前弹出记录删除。已完成metadata release、snapshot release与未接受history交接是不同事实：记录保留精确token/key，不重复解保护；原read task/1–100ms Delay自动接续，close轮询或重臂，stop冻结派发。节点和数组按实际allocator capacity收费到锁外free，原lifetime pin随后归还；纯销毁不阻塞合法restore。metadata原投影安装的retained集合准备前移到putBatch之前，避免token已变却因后置集合分配抛出。

本批新增保证的成本和最终结果见 [同源证据](evidence/br1_captured_release_20261001/README.md)，原文件/caller及同步删除见 [CODE_INDEX](br1_modification_guide/CODE_INDEX.md#captured-release-code-index)，内部接口处置见 [API账本](br1_modification_guide/API_CONVERGENCE_MAP.md#captured-release-api-delivery)。生产源码净增用于前移准入、事实接续和收费寿命，不记为等价去重收益。完整CP1及M6–M8资格不变，当前剩余和重估在§17原位维护。

<a id="history-handoff-lifecycle"></a>
### 16.37 CP1 实施：原 history 工作记录与预付退休 operation 接受（2026-10-01）

沿§16.36同一capture→history→retirement目标推进，未为本轮失败另立终结模型。一个实际收费key节点保存intrusive ready link、固定32 candidates、扫描cookie/游标/重扫事实和未交接效果，pass只取最多16个原记录指针并共享32次root访问。pending/queued/deferred/ready/scans五组旧容器、collectBatchLocked、queueContinuationLocked、deferredKeysLocked以及Read/Publication/Store的history效果复制/累加删除；前台/后台共用原扫描政策。metadata成功detach后立即move效果到原Work，下一owner接受一个效果后才推进该cursor，拒绝不丢原记录。

先比较了继续扩展旧容器、只换allocator与准备前移的直接表达。最终原retirement record在物理准入前准备实际收费operation map node，provider retire前插入该node，有效result保存于原record，bind只填completion，terminal提取同node回record，到实际free才退费。provider后台退休许可在原注册entry固定，效果交接不执行provider callback或分配node。generic write/transfer/reference及无原record的foreign legacy仍有真实consumer，继续generic登记，其整体前置准备/失败责任未被本批关闭。相邻Qt效果准备拒绝仍回同一metadata/Work边界，不需要新效果队列。

实际key存储或Debt拒绝沿原task和一个冷Delay以1–100ms退避继续；释放真实容量后无新输入恢复。close/stop冻结future wake，原未接受效果阻止误关。新解保护发生在两片之间也标记repeat，防止遗漏已越过的历史。扫描活动跨slice保留原观察含义；idle等待在途task/通知的真实root pin归还，future deadline仍不是drain。同步consumer即使没有返回效果数组，也在锁外推进已接受退休。

最终同源双架构各CPU1271、Reference659、PhysicalClaim379、Freehand压力/取消4，合计 **4626 passed / 0 failed / 0 skipped**。5个新数据行覆盖真实Metadata key拒绝、Debt拒绝后的自主恢复，metadata效果和provider有效result在真实硬满下转交/绑定，以及自动与close物理终结。不是全局allocator interposition或永久压力尾退出证明。初始编译/夹具失败、长历史漏扫、同步consumer、预算旧sizeof计算、idle提前归还观察失败均保留，原行为断言未放宽；实际record费用断言改测完整节点和map存储。

生产12文件 **+499/-289，净+210**；测试2文件 **+216/-18，净+198**，派生审计单列。净增用于原记录收费/拒绝接续、operation前置准备及真实活动寿命，不记为纯去重收益。每个deferred key固定候选数组增加了驻留成本，generic operation由QHash改为std::map的查找/驻留成本尚无性能资格；不能用通过数或外层变薄推定stroke更快。上层生产与public/protected API净增0。结构门、源/库身份、聚焦产品/文档提交及失败修复见 [证据](evidence/br1_history_handoff_20261001/README.md)，具体替代与剩余见 [CODE_INDEX](br1_modification_guide/CODE_INDEX.md#history-handoff-code-index)、[API账本](br1_modification_guide/API_CONVERGENCE_MAP.md#history-handoff-api-delivery)。

**完整CP1未结算，M6/M7/M8正式资格仍0/3、默认关闭。** historySlice/versionSnapshot/pageKeys、discard/effects和Debt准备的Qt容量、generic operation/core、capture辅助存储、tree/deferred及一次性task、close handles/seen/诊断、控制本体/runtime/clock和永久拒绝退出仍欠；CP0同依赖upstream、公平/原job接续、TSAN与BR1-PERF未新增资格。下一从上述同一metadata/ledger准备边界继续，不重领已删除的key容器、task、效果聚合或通知框架。

<a id="metadata-retirement-preparation"></a>
### 16.38 CP1 实施：原 metadata/ledger 准备与实际收费效果（2026-10-01）

产品本地提交 `b6ad3447acc855bae91aeb15541ddb5c5049c528`，父为§16.37的`8f07d43ec1646ad0e979f93f9564fcdd8838dcef`；37份源码blob和14个运行物已与最终测试及提交身份绑定，不push。

沿§16.36–16.37同一接受边界继续，选择直接使用实际consumer所需事实并前移准备。historySlice只枚举固定32 identity，metadata原compact records检查capture/read/last-use/pin/operation/authority并收齐实际收费effects；Debt准备后复验真实page revision，再原位unlink。原Work接受同一packet、逐项queue接受后推进cursor，全部交接后实际free容量。history完整version投影、逐版本snapshot/eligibility helper、discard Qt数组和重扫整目录Qt数组删除；public/reference pageKeys仍有真实输出consumer，删除其临时shard数组。没有新效果队列、扫描executor或失败阶段。

原Ledger准备的scratch分类/maps/set、slot/free-list、change/physical/credit数组及claim index全部使用实际收费allocator。generic Qt输入和history pointer/count进入同一私有实现；原cookie、class/domain claim、commit/cancel含义保持。所有容量/node齐全才发布physical class claims，中途拒绝统一撤销同slot全部claims和reservation，未完成责任仍归metadata/Work。原已接管单retirement record改复用atomic reclassify，删除effect/cookie/batch绕路，Metadata硬满下Debt容量释放后仍无新输入继续。未改变provider retire结果和operation已执行事实。

真实硬满effect/ledger准备拒绝、原task自主恢复、两backing 0–4096/64字节冷配额扫描及拒绝/cancel后同backings重试均验证。Debt准备后shard解锁窗口新增真实read lease时，旧准备cancel且版本不detach；释放read后原history继续。bounded history oracle直接消费目标compact删除，与原状态机核对效果和最终版本，长history/default revision重启保留。完整ResidentRead又暴露冷backing准备门外窗口遗漏默认页key去重/64项准入复验，已在两侧复用同一等待政策修复，不放宽上限或去重断言。

最终同源双架构各CPU1275、Reference659、PhysicalClaim379、ResidentRead221、Foundation28、Freehand压力/取消4，共 **5132 passed / 0 failed / 0 skipped**。新增4个CPU数据行；阶梯quota扫描不是全局allocator interposition，stop/close/晚handle原回归也不是完整永久拒绝出口证明。初始编译/混合二进制误启动、夹具Debt/fallback寿命、Queue Metadata硬满及Default并发失败日志均保留。ResidentRead的payload继续清零，Metadata实际cache收费到原owner销毁，外部共享process验证回到实测预热cache基线。

生产8文件 **+290/-132，净+158**；测试4文件 **+160/-33，净+127**，派生审计单列。净增属于实际收费/准备回滚、compact删除接受和必要并发修复，不能算等价去重。新增3个必要私有操作、没有新增上层public/protected API；固定slice约1KiB栈、Ledger实际收费cache及physicals线性去重/锁内准备成本仍待性能测量。具体映射/删除见 [CODE_INDEX](br1_modification_guide/CODE_INDEX.md#metadata-retirement-code-index)、[API账本](br1_modification_guide/API_CONVERGENCE_MAP.md#metadata-retirement-api-delivery)，最终源码/库/Git身份与所有失败见 [证据](evidence/br1_metadata_retirement_20261001/README.md)。

**完整CP1仍未结算，M6/M7/M8正式资格0/3、默认关闭。** generic applyProjectedSequence/versionSnapshot和provider journal Qt容量、generic operation前置登记/有效result归属、core backings/physical/registry及本体、capture辅助存储、tree/deferred/一次性task、close handles/seen/诊断、runtime/clock与完整永久压力最后handle仍欠。下一沿原provider operation准备/接受责任继续；不重领已删除history投影、effects或Debt准备框架。CP0同依赖upstream、TSAN、公平/原job接续和BR1-PERF无新增资格，剩余估算仍按§17原位维护。

<a id="synchronous-provider-result-acceptance"></a>
### 16.39 CP1 实施：同步 provider 结果直接接受（2026-10-01）

产品本地提交 `a561ca7b0ba920872fd2d8e0420016967a354985`，父为§16.38的`b6ad3447acc855bae91aeb15541ddb5c5049c528`；37份源码blob和14个运行物与最终测试及提交身份绑定，不push。

沿同一provider准备→接受责任核对真实consumer后，采用比逐调用预备登记更直接的形态：Store只注册同步provider，transfer bridge也要求同步；原request/adoption/write activity及claim保留物理结果到接受。Ledger的`verifyTerminalProviderResult`共同检查原operation、provider/epoch、重复绑定和原registry终态，不再为已终态的结果执行“bind→verify→release”。5个Store调用、WriteCoordinator transfer和无原record的foreign同步retire全部迁移，旧`consumeTerminalProviderOperation`及临时节点往返删除。身份政策与显式binding共用一处私有检查；没有新增token、结果队列、失败状态或重试框架。

原有退休record的预付map node、有效result保存、terminal取回及自主retry保持。显式generic/pending binding仍被reference和组合测试消费，保留其独立登记/计数/释放合同；它不再是同步生产结果的consumer，不能把本批保证推广为异步provider接线。另修复transfer以provider返回ID验证自身的缺口：现在必须匹配原request.operation，真实错误ID返回被拒绝且只调用一次。

固定64KiB Metadata实满下，旧路径同一charged insertion实际拒绝；allocation、write及transfer结果直接验证成功，预算和operation计数不增长。foreign两个物理retire各一次，实际payload归零、没有遗留登记。reference另覆盖错误operation/epoch、其他registry ticket、Pending及Succeeded/Failed/Cancelled终态、已有binding冲突；Pending不会遗留同步登记。该夹具只验证结果已返回后的接受边界，provider自身准备与registry终结容量未因此取得资格。

最终同源双架构各CPU1277、Reference660、PhysicalClaim379、ResidentRead221、Foundation28、Freehand压力/取消4，共 **5138 passed / 0 failed / 0 skipped**。新增3项测试；完整链接后才运行。初始缺少backing实参的测试编译失败、硬满夹具漏计冷reservation容量的异常及索引未完成时刷新失败均保留，不计入资格；修复后的原额度、身份、计数和像素断言未放宽。最终结构门21 manifest/25 ownership/16 census通过，上层阈值保持。

生产5文件 **+44/-32，净+12**；测试2文件 **+138/-1，净+137**，生成图/基线及ownership单列。实际删掉的是同步接受的一次收费节点分配/释放和登记查询往返；净增用于直接registry检查及共用身份政策，不记纯行数去重。性能未测，不能将减少节点等同于stroke性能资格。具体caller与删除见 [CODE_INDEX](br1_modification_guide/CODE_INDEX.md#synchronous-provider-result-code-index)、[API账本](br1_modification_guide/API_CONVERGENCE_MAP.md#synchronous-provider-result-api-delivery)，Git、失败和最终证据见 [记录](evidence/br1_synchronous_operation_20261001/README.md)。

**完整CP1仍未结算，M6/M7/M8正式资格0/3、默认关闭。** 已定位相邻实际容量：Registry Private/control block、sources、terminalRanges/nonSuccess；provider allocation/domain journal/admission索引；Ledger provider/backing/physical核心索引及synchronizeBackingDomains的changes/probes/acknowledged数组。下一沿这些producer→原owner→terminal/ack边界准备实际容量、核对拒绝接续与最后free，不另建结果框架。generic metadata投影、capture辅助存储、tree/deferred/一次性task、close handles/seen/诊断、runtime/clock及永久压力最后handle仍欠；CP0、TSAN、公平/原job接续和BR1-PERF无新增资格。

<a id="registry-terminal-preparation"></a>
### 16.40 CP1 实施：Registry 与原 provider 退休终结准备（2026-10-02）

产品本地提交 `7708613905a183dfb1d1424bc961ee70300ee438`，父为§16.39的`a561ca7b0ba920872fd2d8e0420016967a354985`，文档父 `20c68559f7001c190a91958eb2cfbc9b42405a16`；41份源码/15个运行物绑定见[Git身份](evidence/br1_registry_completion_20261002/git-round-identity.json)，不push。

真实缺口是allocatePending只发行ID，terminalRanges/nonSuccess在物理动作后仍可能申请存储；仅给旧两表预备节点会继续双重维护coverage/status。因此选择一个原source的intrusive区间，Pending节点在发行前实际收费，complete只写状态/合并并推进明确coverage，成功prefix不保留节点，同类Failed/Cancelled区间合并；原Pending gap、三终态与重复终结语义保持。删除两索引、markTerminal/terminalStatus和终结时分配/回滚。合并后实际free在registry门外、notify之前；没有新结果队列或失败阶段。

Registry Private/std共享控制块、source map节点和区间接入独立retained child，真实backend使用原shared process root；弱callback仍指向原Private，不绑定单一Store寿命。sourceStatistics的storageRecords计入实际Pending准备，已核对consumer只有诊断/测试，不作为准入/关闭业务活动。每活跃allocation提前保存一张private retirementCompletion，allocate、immutable alias及initial adoption均在物理副作用前准备；reader/transition拒绝沿用同一Pending，物理detach/free后完成，provider teardown取消未消费ticket。共用transfer和archive在原scope中前移准备/归还，不复制终结协议。

固定64KiB真实process Metadata硬满，source/ticket新增被实际allocator拒绝且不消耗身份；Succeeded/Failed/Cancelled均能乱序、桥接并关闭gap，callback看到终态、原节点已释放。真实Tiles3分别在operation节点/退休节点准备处拒绝，payload工作与committed bytes不增加，没有遗留Pending，释放额度后新请求成功；pin拒绝后硬满下用原退休ticket实际free两backings，不新增ticket。Registry销毁及最后弱订阅返回同一实测预热process cache基线。不是全局allocator interposition或完整永久压力退出资格。

最终同源双架构各Registry87、CPU1280、Reference660、PhysicalClaim379、ResidentRead221、Foundation28、Freehand压力/取消4，共 **5318 passed / 0 failed / 0 skipped**。编译最初暴露Boost不能把noexcept function pointer作为intrusive disposer继承，改为直接lambda后完成构建；初始日志保留。最终结构21 manifest/25 ownership/16 census/19上层intrusion通过，1928 APIs/21265 edges/20 callbacks，原阈值未变。

生产7文件 **+161/-119，净+42**；测试/模型3文件 **+202/-4，净+198**，派生审计另记。净增是收费、发行前准备和必要producer接续的保证成本，不记纯行数去重；每Pending一个实际节点、每活跃backing一张预备退休ticket，source改有序map和状态查询/合并成本待测。没有新增上层生产/public-protected API、调度器或通知权威。具体caller/删除见[CODE_INDEX](br1_modification_guide/CODE_INDEX.md#registry-terminal-preparation-code-index)、[API账本](br1_modification_guide/API_CONVERGENCE_MAP.md#registry-terminal-preparation-api-delivery)，原始日志/增量/身份见[证据](evidence/br1_registry_completion_20261002/README.md)。

**完整CP1未结算，M6/M7/M8正式资格0/3、默认关闭。** Registry外层Qt facade/child controller包装/bootstrap固定成本，provider allocation/physical/domain journal/admissions、Ledger核心索引和changes/probes/acknowledged Qt数组仍欠；generic metadata投影、capture辅助存储、tree/deferred/一次性task、close handles/seen/诊断、Store/provider/Ledger本体及runtime/clock和完整永久压力最后handle继续CP1。下一沿原provider journal/admission→Ledger精确revision ack准备/接续，不重领已删除的terminal两索引，不重放已发生physical动作。CP0同依赖upstream、TSAN、公平/原job接续与BR1-PERF无新增资格。

<a id="domain-journal-delivery"></a>
### 16.41 CP1 实施：原 Payload journal 与 domain admission→Ledger 精确确认（2026-10-02）

产品本地提交 `5942e1c0f6716c75a66d942f34ed1e4cf7461cd8`，父为§16.40的 `7708613905a183dfb1d1424bc961ee70300ee438`，文档父 `4eecdd0efe90cc2efb1139fd7de667896ed854bb`；44份源码blob和15个运行物绑定见[Git身份](evidence/br1_domain_journal_20261002/git-round-identity.json)，不push。

本轮整体目标是physical副作用前准备、提交只改原事实、Ledger完整验证后精确ack。原Payload已有domain/revision，另一个m_changes却复制同一事实且noexcept commit仍在physical移动后插入Qt节点；单独收费该journal会留下两份状态和终结分配。因此保留实际收费的稳定Payload节点、slot→Payload只读索引及Payload内嵌dirty link，删除m_changes。commit只更新原domain/revision并链接；ack仅在原revision相等时unlink，较旧ack保留较新变更，untrack取出原节点到门外实际free。

真实backend将observer独立收费child接原process root，retained allocator覆盖payload/slot索引、weak admissions、准备快照和transition reservation容量。prepareResidencyChange先准备admission快照，才发布原transition serial；返回对象和全部reservation数组在physical移动前完成。任一cold拒绝取消同serial及先前owner reservation，不增加失败队列/阶段。Ledger domain admission先准备inactive返回对象和实际收费claim node才发布domainClaim，pending-registration也收费；cancel/commit/detach在原权威内清事实并把实际存储转到门外释放。

backingDomainChanges改为实际收费vector，全部生产和测试override同批迁移；Ledger仍保留原provider registry的不可变共享cut，准备charged changes和一份Probe数组，ack标志存原Probe。完整cut验证通过前不确认任何revision；两个实际allocator拒绝都保留原journal及已发生physical结果，释放后沿同一owner重试，不重放swap。旧live弱数组和第二acknowledged数组删除。默认诊断snapshot保留原accounting寿命到其最后容量free；Ledger局部snapshot使用原Ledger预算。

最终双架构各Registry87、CPU1284、Reference660、Physical379、Resident221、Foundation28、Freehand压力/取消4，合计 **5326/0/0**。固定64KiB实际硬满分别拒绝snapshot和Probe；claim node准备拒绝保持原resident/domain/revision、SSD reserved归零，解除压力后同payload成功迁移；测试observer在real provider准备后填满原root，physical commit/journal仍完成，later owner登记拒绝后可原位重试。旧revision ack不能清掉较新dirty，snapshot晚于provider/accounting facade销毁仍收费至实际free。现行snapshot/registration并发、swap-in失败、read/history/退休、Fresh和真实brush压力/取消回归保留。不是全局allocator interposition、TSAN或永久压力全出口证明。

生产6文件 **+218/-127，净+91**；测试2文件 **+162/-13，净+149**，生成审计单列。净增用于实际收费、准备失败原子性和寿命保证，不记为纯去重；另一个journal状态、live数组和ack数组实际删除。稳定map查询、slot索引和两类同步快照容量仍有成本，未取得性能收益资格。上层生产/public-protected API净增0；方法签名替代没有兼容overload。具体替代及成本见[CODE_INDEX](br1_modification_guide/CODE_INDEX.md#domain-journal-code-index)、[API账本](br1_modification_guide/API_CONVERGENCE_MAP.md#domain-journal-api-delivery)、[证据](evidence/br1_domain_journal_20261002/README.md)。

**完整CP1未结算，M6/M7/M8正式资格0/3、默认关闭。** observer/Transition/DomainAdmission/Reservation的Qt本体与控制块/bootstrap、provider allocation/physical Qt索引和Ledger provider/backing/physical/sharedMembers/sealedProof核心仍欠；Registry外层固定成本、generic metadata投影、capture辅助、tree/deferred/一次性task、close handles/seen/诊断、Store/provider/Ledger本体及runtime/clock和完整永久压力最后handle继续同一CP1。下一审查原physical adoption→索引安装→退场的全部容量和失败窗口，不重领已删除journal，不重放副作用。CP0同依赖upstream、TSAN、公平/原job接续与BR1-PERF无新增资格。

<a id="provider-adoption-delivery"></a>
### 16.42 CP1 实施：原 provider adoption 节点准备与 physical 记录收敛（2026-10-02）

产品本地提交 `2e39b9e760513ecab9c0aa7337a62308ddfd2c00`，父为§16.41的 `5942e1c0f6716c75a66d942f34ed1e4cf7461cd8`，文档父 `e1bbaf1197e4f67298ca3ff1397f40e17789d450`；44份源码/15个运行物见[Git身份](evidence/br1_provider_adoption_20261002/git-round-identity.json)，不push。

原physicalPayloads保存identity/refcount，原observer Payload已有同一identity/domain/revision，三个adoption入口各拼装binding、physical retain和allocation插入。目标采用原Payload承接logicalReferences，删除Tiles3PhysicalPayload/physicalPayloads；physical字节仍只计一次，最后逻辑引用才untrack原节点。prepareAdoption共用实际收费allocation node及必要Payload/slot node准备，fresh在创建/复制pixels前收齐三个节点；已有physical alias只准备一个allocation node。原adopt共同安装binding、physical引用和prepared allocation node，拒绝/异常撤销同一physical登记。临时PreparedAdoption/PreparedPayload只持有本次未安装的实际nodes，无新持久阶段、第二物理权威或结果队列。

共用allocation索引改为稳定charged map，真实Tiles3 allocation和active lease节点/buckets复用§16.41原retained process allocator；reference CPU消费者同批迁移map接口，其默认预算接线没有扩大。actual lease插入仍先于pin，拒绝保留全部原leases和未占用ID；释放原node后同ID可用。retire提取原allocation node在provider门外释放；原Payload/slot free仍在observer门外。provider析构逐项撤销原payload登记，不复制整个列表。

统计不能在observer锁下读tile锁，否则和swap的physical→observer顺序相反。residentBytes等待原transition serial结束，再从唯一Payload domain计数；原memoryUsage不新增计数权威。实际PausedObserver让swap已准备但尚未移动，统计等待同serial，迁移完成后resident bytes正确下降、committed bytes保持；没有锁内tile访问。

固定64KiB实测成功alias节点费用和fresh三节点总费用，再分别给0、仅allocation、总费用少1B空间，触发三个实际cold allocator拒绝。未创建default pixels、physical committed/pending retirement不变，部分准备费用全退；已有alias/initial在满额下拒绝，解除后原source/tile可安装并同physical一次计费/逐项退休。实际lease满额拒绝不丢旧pin/数据，旧lease阻止退休，release后同ID重试。最终双架构各Registry87、CPU1289、Reference660、Physical379、Resident221、Foundation28、Freehand4，合计 **5336/0/0**，见[结果](evidence/br1_provider_adoption_20261002/qualified-results.json)。首次完整x86_64有lastUseAtMetadataCapacity引用数3/预期1失败：组合测试只等read/history语义idle，遗漏retirement与原任务finished回调尾部；补齐其wait及原executor drain，保留严格引用断言。修复后相关双架构各22/0/0及最终全组通过，原失败日志保留，未放宽像素/额度/行为条件。

生产2文件 **+211/-112，净+99**；测试/模型2文件 **+140/-3，净+137**，生成审计单列。净增表达节点准备、拒绝原子性、实际收费与统计锁序保证，不能计为纯去重；重复physical表和三入口直接插入/回滚实际删除。稳定map、cold三个节点、lease buckets和等待成本未测性能；上层生产/public-protected API净增0。调用图1939 APIs/21485 edges/20 callbacks、独立结构门及源码身份见[证据](evidence/br1_provider_adoption_20261002/README.md)，具体替代见[CODE_INDEX](br1_modification_guide/CODE_INDEX.md#provider-adoption-code-index)、[API](br1_modification_guide/API_CONVERGENCE_MAP.md#provider-adoption-api-delivery)。

**完整CP1仍未结算，M6/M7/M8正式资格0/3、默认关闭。** Ledger provider/backing/physical/sharedMembers/sealedProof核心仍欠；provider/binding/read-cache/source/observer/Transition/Admission/Reservation的Qt本体/control/bootstrap和TileDataStore登记内部Qt容量未关闭，原allocator收费缓存允许存活到owner销毁。Registry外层、generic投影、capture辅助、tree/deferred/一次性task、close handles/seen/诊断及runtime/clock和永久压力最后handle继续CP1。下一收口原Ledger注册→classification/claim→retirement/take的全部存储和失败接续，不重建physical表或重放副作用。CP0、TSAN、公平/原job接续与BR1-PERF无新增资格。

<a id="ledger-backing-delivery"></a>
### 16.43 CP1 实施：Ledger backing 安装准备、共享成员与同节点退场（2026-10-02）

本轮有限责任是原backing注册→classification/domain claim→handoff→retirement/take：旧registerBacking先改physical引用、再分配logical backing与shared成员，插入失败没有同一回滚点。直接收费原容器仍会留下provider有效结果后的异常窗口；因此将actual backing/physical稳定map节点并入原retirement record的cold准备，fresh先于provider物理动作，成功安装只修改key并转移同nodes。直接adoption失败原结果/reservation仍归caller，initial rollback取回原Record后只补缺失nodes；无新结果队列/阶段/token或上层API。

原backing节点内嵌双向member link，原physical只保存成员头，**sharedPhysicalMembers及每physical QSet删除**。projection只读link，class/revision/headroom政策保留；handoff rekey同节点、member地址和退休记录不变。takeRetirementRecord转交同Record给原queue，releaseRetiredBacking先unlink并extract actual backing/last physical nodes，locker销毁后才free。alias成功时不用的预备physical node也在门外返还，物理bytes仍只计一次。

DomainAdmission的allocated registration index替换为同步registerBacking调用栈上的原标记，由原authority gate维护link，scope出口归还；只排除原两次footprint窗口中的同physical登记/domain移动，没有异步责任或持久阶段。claim map原准备/取消/commit不改政策。首个候选在attachBackingBudget提前创建retained accounting owner，违反既有冷limits/shared-parent配置；完整回归定位后改为挂接空map不分配，首次安装锁内绑定已准备nodes的allocator，不增加bootstrap状态，之后安装仍不分配。

固定64KiB，预热原reservation/accounting缓存后按实测费用分别拒绝actual backing/physical nodes：fresh物理入口0次、部分准备费全退；直接有效结果、caller reservation和Ledger事实保留，释放后仅继续登记。rollback原Record补齐被拒时身份不变，恢复后同Record安装。原queue组合将压力提前到登记前，registered/orphan硬满接受、拒绝retire、Debt释放无输入继续与close同Record保持。真实第二footprint窗口阻止swap和同physical竞争，竞争拒绝保留其Record/reservation，原marker归还后同alias结果接受、解除压力后SSD迁移正确。三alias硬满准入、删除middle/head/代表和最后physical，逐项严格断言actual逻辑/physical存储费归还；共享Debt、SSD、claim取消、跨索引增长和原handoff回归保留。

最终同源双架构各Registry87、CPU1292、Reference660、Physical381、Resident221、Foundation28、Freehand4，合计 **5346 passed / 0 failed / 0 skipped**，见[结果](evidence/br1_ledger_backing_20261002/qualified-results.json)。初次完整矩阵的冷配置回退、未预热缓存导致的测试差值、旧last-use组合future history retry引发的root观察竞争及新增测试默认init后访问空initial数组的错误均保留。后者由LLDB定位并修复为显式一页；原root==1、额度及业务断言不放宽，自动终态先观察完成再停止future history/retirement dispatch并等原回调尾部。旧失败PID87095和本轮失败native PID43034仍为UE，runner已停，不能声称native已退出；后续测试禁core且关闭Qt崩溃处理，全部14个qualified进程正常退出，完整永久尾退出仍未取得。

生产3文件 **+271/-176，净+95**；测试2文件 **+256/-8，净+248**，生成审计单列。净增表达真实收费、完整准备/原子安装及实际free保证，不能记作纯去重；成员表和allocated domain registration index实际删除，Ledger cpp本轮净+10，跨文件总量已计入private头，未靠搬移宣称减行。map查询、cold两节点及record增大未测性能。最终调用图1944 APIs/21627 edges/20 callbacks，结构门21 manifest/25 ownership/16 census/19上层intrusion、阈值不变；源/库/本地Git身份见[证据](evidence/br1_ledger_backing_20261002/README.md)，替代见[CODE_INDEX](br1_modification_guide/CODE_INDEX.md#ledger-backing-code-index)和[API](br1_modification_guide/API_CONVERGENCE_MAP.md#ledger-backing-api-delivery)。

**完整CP1未结算，M6/M7/M8正式资格0/3、默认关闭。** 下一是Ledger provider/pending registry、provider snapshot/route与sealedProofs接纳/撤销，保留budgetless/先登记后挂接的实际consumer和冷配置合同；provider接受admission后不得再因索引分配丢失责任，seal拒绝不得消耗stamp或丢失原prepared结果。generic metadata投影/capture辅助，TileDataStore observer登记、tree/deferred/一次性task、close handles/seen/诊断、Store/provider/Ledger与Qt本体/control/bootstrap、runtime/clock及永久压力最后handle仍在同一CP1。CP0、TSAN、公平/原job接续及BR1-PERF无新增资格。

<a id="retired-policy-delivery"></a>
### 16.44 CP1 清理：传播准备保证并回收旧失败政策（2026-10-02）

本轮按用户要求回收前几轮已失去失败来源的协议，边界为原producer completion、History detach→queue交接和退休operation binding。`allocatePending`已准备实际区间节点，终结只更新/合并原节点；新增内部producer入口`completePrepared noexcept`统一原真实provider、reference CPU provider、transfer、archive及host-ready终结政策。公开`complete`继续拒绝无效/foreign/重复ticket；producer独占的已铸造Pending违反身份或重复终结属于不变量破坏，不能包装成物理成功后的可重试业务失败。allocate late rollback、free后的retire Failed、memcpy后的transfer Failed和archive completion rollback同批删除；alias、initial adoption、准备失败scope与teardown取消均使用同一政策。`beginRetirement`缺少原private ticket不再误报现场分配失败，真实pin/last-use/transition拒绝仍保留。

History交接先收紧原准备边界：有replica effects时必须配置Debt owner，Ledger逐项验证已登记的精确backing及原retirement record，拒绝保留metadata和原Work。成功detach已经提交Debt，caller原owner gate排除同一记录的竞争取出；queue只取原record并插入原intrusive链，无分配或provider调用。effects改为一次slice内的收费局部packet，删除`Work.effects/nextEffect`、`finishEffectsLocked`、`pendingEffects`及close诊断/guard，不再保留已消失的detach后重试阶段。key/root/revision、packet/Debt准备拒绝仍由原Work/task/Delay接续；正常retirement的Pending/pin/Debt拒绝不受此删除影响。

`bindRetirementOperation`只填入原record预先安装的operation node，删除缺节点时转generic分配的fallback；`detachedRetirement`缓存字段及私有bool转接wrapper删除，publication阻塞分类直接读取原record指针。reference模型迁移到真实FakeCpu provider Pending→原Queue→同operation node回收，验证未准备结果拒绝、generic Pending共存、无退休重放和计数归零。generic `bindProviderOperation`仍有reference/Pending consumer及真实容量拒绝，保留其独立合同，不将其误删为退休残余。metadata索引oracle配置显式模型责任接收者，合成replica不冒充真实物理交接证据。

最终同源双架构各Registry87、CPU1295、Reference660、Physical381、Resident221、Foundation28、Freehand4，合计 **5352 passed / 0 failed / 0 skipped**；另有聚焦240/0/0，不能相加。三种缺owner/backing/record拒绝均在detach前；准备后硬满完成及原History一次交接使用真实容量；Pending退休使用原预付节点。初次完整回归暴露5个未配置责任接收者的metadata oracle行，两架构失败保留，迁移后重新全组通过。所有最终14个测试进程正常退出；既有失败native进程仍UE，完整永久尾退出没有新增资格。见[本轮证据](evidence/br1_retired_policy_20261002/README.md)。

生产16文件 **+79/-119，净-40**；测试/模型4文件 **+88/-33，净+55**；生成审计/ownership3文件+11279/-11177单列，图重索引不计作实现增长或简化。新增方法吸收一项被多个producer消费的完整政策，新增前置检查修复History可能detach后无合法接收者的缺口，没有新增持久阶段/队列或上层生产/API。最终图1943 APIs/21642 edges/20 callbacks；结构门21 manifest/25 ownership/16 census/19上层intrusion通过，阈值不变。替代/删除见[API](br1_modification_guide/API_CONVERGENCE_MAP.md#retired-policy-api-delivery)，实际端点及剩余见[CODE_INDEX](br1_modification_guide/CODE_INDEX.md#retired-policy-code-index)。

**本轮旧政策回收完成，完整CP1未结算，M6/M7/M8正式资格0/3、默认关闭。** 下一provider/pending登记、route cut及proof接纳/撤销端点不变；generic metadata投影、TileDataStore登记、控制本体/固定成本与完整永久压力最后handle继续同一CP1。未取得全局allocator、TSAN、性能、公平、原job接续或M6–M8资格，不从净删行或测试总数扣排期。

<a id="protocol-residue-delivery"></a>
### 16.45 CP1 清理退出审计：统一效果接受与后台许可、删除废弃入口（2026-10-02）

本轮从产品`643965d644e6ed13d0437b2289b8abad0161ce05`、文档`3a8f843e0d82bb34b8bfd25cc60e9febeea437b0`继续，按用户“持续清理旧协议直到没有可清理残余或均不适合现在清理”的目标，复核当前producer→Ledger→metadata→read/capture/history→queue/close及实际publication/adapter消费者，不读取archive。有限删除对象、实际consumer与保留依据见[审计](evidence/br1_protocol_residue_20261002/residue-audit.json)，当前Git/源/运行物身份见[证据](evidence/br1_protocol_residue_20261002/README.md)。

原record的`backgroundRetirement`成为唯一后台许可事实：registered取登记时的许可，unregistered原record在接纳时固定一次；初次退休、effect交接、订阅/Delay重试与close恢复共用它。删除`wakeEligible`及retry时provider capabilities重查，不改变foreground/provider锁域。原`retirementRecordTransfersAtCapacity`行增加查询计数及3处断言、合计6行，在至少3次无输入重试和最终释放后分别验registered查询0次、orphan1次；实际费用、Debt释放、manual与close断言不变，没有新增测试数据行。

继续沿batch effects生产者核对：Store在运行前配置真实Debt owner；generic取消/abort经metadata apply先准备/提交Debt，commit/restoration经原backing reservation先验证精确backing及record，成功后metadata已移除该选择。与History相同，交接不能合法缺Debt或原record。两个接收入口共用私有`takeEffectRecord noexcept`，删除batch的缺Debt→`retireOrDefer`补准入和缺record→continue；不变量破坏统一处理。batch保留原批量、前台立即退休和8/max pump，History在原owner gate内只转record而不调用provider。未登记结果的原`retireOrDefer`仍有真实失败来源，不与已接受effect混淆。

Read的5处effect调用均只传空数组，改为`processRetirementsUnlocked`直接推进原queue，保留后台短路、锁外窗口和activeProviderCalls配对。删除无consumer的公开`Store::preparedPageExtent`、其私有`preparedPageExtentLocked`完整body，以及backend `resolveCurrentPagePresence`分配输出包装；当前联合overlay准备仍使用原`contentExtentAfterDelta`，manager直接使用`resolveCurrentPagePresenceInto`预备scratch。另删一处始终为空的局部packet、3个unused include并修正旧QHash稳定性说明，无兼容overload或新的持久阶段。

退出审计没有把零入边当作删除证明：最终图的29个非operator/特殊成员候选逐项复核，模板/ADL、Qt shutdown callback和图外Vulkan实际consumer继续保留；Foundation及BR2/BR4 fail-closed接口、纯值访问器没有被已实施的新合同替代，不属于本轮旧恢复协议。列明旧符号和分支的19项[删除检查](evidence/br1_protocol_residue_20261002/deletion-checks.json)均通过。在上述BR1责任闭包内，未再发现具备删除条件而未处理的旧协议；以下仍可达内容均有具体依据，不能为了清空分支改掉原责任：

| 暂留内容 / 原consumer | 当前真实来源 | 后续删除条件 |
|---|---|---|
| Read/captured的metadataReleased、versionReleased、snapshotReleased、historyPending及原retry | provider access释放、metadata/last-use解保护、epoch释放和history key接受是不同不可重放步骤；metadata/key准备仍可拒绝 | 原准备保证覆盖所有实际release/ack/cancel/close和晚通知后，合并失去来源的事实/恢复 |
| retirementResult、readiness incarnation/rechecked、subscription和预付Delay、owned/orphan Debt | pin/last-use、真实Pending、subscriber容量与Debt额度仍可能阻止终结；原record保存有效结果避免重放 | 取得对应物理ready/完成/订阅准入的新保证后，传播到全部原consumer；当前没有该保证 |
| generic effects batch及公开complete/generic Pending binding | cancel/abort/seal/publication实际产出effects；公开ticket身份/重复拒绝合法，reference显式Pending仍与退休共存 | 真实batch/外部Pending consumer迁移并保留原调度/身份语义后删除；本轮已删其过时fallback |
| Ledger provider/proof、generic metadata及adapter Qt准备拒绝 | provider/pending registry、route cut、sealedProofs和Qt容量尚未完整预付；参数/footprint/source/ticket/pin/预算/transition拒绝真实 | 同一CP1包关闭容量与接纳/seal/revoke后，同批删除消失的恢复；不凭backing准备推定已关闭 |
| raw/legacy恢复、复杂模式和Failed/原job取消 | 未迁移source/iterator/复杂模式仍消费旧路径，scheduler返回后销毁job，尚无安全重排所有权 | CP5接续及CP6–CP7实际模式的读/适配/undo/终结联合迁移完成 |

最终同源双架构7组 **5352 passed / 0 failed / 0 skipped**，14进程正常退出；中间源码亦有5352通过，单独保留，不能与最终数累加。生产14文件 **+38/-117，净-79**；测试1文件 **+6/-0**；生成审计/ownership3文件 **+4665/-4892**单列。新增私有方法吸收两个实际入口的完整接受政策，没有新增持久状态/队列、上层生产/API或新业务保证。最终图1941 APIs/21625 edges/20 callbacks，结构门21 manifest/25 ownership/16 census/19 intrusion通过、阈值不变。

**本次旧协议持续清理目标在已审计BR1范围内完成，完整CP1未结算，M6/M7/M8正式资格0/3、默认关闭。** 下一provider/pending登记、route cut及proof接纳/撤销不变；固定成本/完整永久尾退出、CP0、TSAN、公平/原job接续和BR1-PERF仍开放，不从净删行或测试数扣人日。活动函数映射见[CODE_INDEX](br1_modification_guide/CODE_INDEX.md#protocol-residue-code-index)、[API](br1_modification_guide/API_CONVERGENCE_MAP.md#protocol-residue-api-delivery)。

<a id="ledger-provider-proof-delivery"></a>
### 16.46 CP1 实施：Ledger provider 接纳、共同切点与 proof 节点生命周期（2026-10-02）

本轮从产品`64dd930babedfb71d9edabc7be97f11199cd5e6c`、文档`48c279a1dcb3fa6b23b936ad65a20889c0547330`继续完整BR1目标，关闭原Ledger provider登记→accepted cut/route→sealed proof→revoke/析构这一有限端点。唯一authority仍为原Ledger，不增加结果队列、公开API或上层生产改动。目标形态及原入口替代见[CODE_INDEX](br1_modification_guide/CODE_INDEX.md#ledger-provider-proof-code-index)、[API](br1_modification_guide/API_CONVERGENCE_MAP.md#ledger-provider-proof-api-delivery)，Git/源码/运行物见[证据](evidence/br1_ledger_provider_proof_20261002/README.md)。

provider原真实节点在外部domain admission前收费准备并以pending状态插入原索引；pending不参与任何accepted provider查询和路由，重复/同ID登记仍拒绝。拒绝或异常unlink同节点，locker先退出再free；admission成功只在原节点记录acceptance revision，不再分配第二索引。accepted记录在Ledger寿命内稳定，domain同步和route选择共用scalar accepted cut及门内逐项cursor，provider callback在门外；cut排除pending及后来接受者。原pending QSet、provider QHash隐式共享snapshot和values/list全部删除，provider/result/backing/retirement消费者迁到共同accepted lookup。

proof先准备实际收费节点，再做provider validation；接受只链接该节点，成功后才推进stamp和修改caller输出。真实存储拒绝保留原prepared metadata/authority和输出，重试不跳stamp；validate/owns在原节点核对完整proof，revoke unlink后门外free。两种节点共用局部storage/index释放原语，成员析构次序保留。每个节点保存其原allocator预算来源，budgetless及挂接前节点保持实际bootstrap兼容合同，后续节点使用挂接预算；本批没有追溯收费或整体bootstrap资格。相比整表换成单allocator map，该形态避免cold挂接时重分配既有节点或改变实际兼容consumer，不新增第二登记表。

最终7组双架构 **5354 passed / 0 failed / 0 skipped**，14进程正常退出。新provider行实际耗尽64KiB MetadataArena，验证callback零进入、pending隐藏/重入重复拒绝、provider拒绝/异常归还同费用、callback期间硬满后仍可接受和最终析构归费；原route/domain行验证callback登记不进入旧cut、下一cut看见新provider/拒绝歧义。原proof行实际硬满拒绝，输出stamp77不变、下一接受stamp1；provider validate边界再次耗尽剩余额度，准备的节点仍可安装；多个proof收费、硬满validate/revoke及重复revoke精确归费。初始C++20 construct_at编译失败保留，改用C++17 allocator_traits::construct后构建通过；加validation压力前的中间5354仅保留日志，没有冻结其运行物身份，不授予最终源码资格。

生产1文件 **+158/-67，净+91**；测试/模型4文件 **+153/-3，净+150**；生成审计/ownership3文件 **+8219/-7152**单列。净增为paid实际节点、准备前移和共同cut遍历的保证成本，不能记作纯去重；没有新后置重试阶段。冷登记allocator和map/cursor查找成本未测性能，S05与BR1-PERF不变。最终图1953 APIs/21701 edges/20 callbacks，21 manifest/25 ownership/16 census/19上层intrusion结构门通过、阈值不变；21项[删除/替代检查](evidence/br1_ledger_provider_proof_20261002/deletion-checks.json)通过。

**有限Ledger端点已交付，完整BR1目标继续、完整CP1未结算，M6/M7/M8正式资格0/3、默认关闭。** proof节点准备拒绝仍可达，不删除native seal和generic finishWrite的原Failed/cancel消费者；Ledger保留prepared结果不等于scheduler自动接续。metadata.versionSnapshot/通用projection及overlay Qt准备、capture辅助、TileDataStore observer登记、tree/deferred/一次性task、close handles/seen/诊断、Qt本体/control/bootstrap（含上述兼容节点）、Store/provider/Ledger和runtime/clock固定成本仍欠。旧失败native PID43034/87095仍UE/parent1，完整永久压力/最后handle退出、全局allocator、TSAN、公平/原job接续、CP0同依赖对照和正式性能均无新增资格。下一按原metadata准备→安装→清理实际consumer闭包推进，并继续复核随新增保证消失的旧分支；不重领本批已删除容器。

<a id="capture-metadata-delivery"></a>
### 16.47 CP1 实施：exact 查询、原 capture cut 与保护释放（2026-10-02）

本轮从产品`e3d6161b99a9c668f3d9aee5502741d562e74ce7`、文档`243c9711694e870c78b1cfc6891ad54ec9c4d49e`继续完整BR1目标，关闭原exact查询与capture准备→保护→查询→释放这一有限端点。唯一事实仍在原metadata/epoch/publication/read owner，无新增队列或上层生产API。目标替代见[CODE_INDEX](br1_modification_guide/CODE_INDEX.md#capture-metadata-code-index)、[API](br1_modification_guide/API_CONVERGENCE_MAP.md#capture-metadata-api-delivery)，同源身份及失败日志见[证据](evidence/br1_capture_metadata_20261002/README.md)。

产品聚焦提交为`e08545e5f2e77d1d8598032b8546f70eb93e932d`，47份源码blob、15份运行物及5份构建依赖匹配；普通编辑为显式patch，产品tracked树干净，没有push。活动文档与证据在外层单独提交。

所有生产versionSnapshot consumer改读原record的scalar VersionInfo；generic read在Store/shard gate外准备实际收费的最小replica候选数组，再取完整cut，拒绝不改变输出。native CPU discovery直接借原slot，保留Prepared必须已有captured保护及authority/歧义规则。原projectVersionPair只有mutationBase一个consumer，包装与countMutationInput开关删除，原body归mutationBaseSnapshot；mutationBase和generic transition/publication的真实Qt投影仍保留。

capture直接从原PreparedTransactionState填入原release记录的paid version/removal/surface数组，容量先于root/token，锁外准备后重选原cut；旧transactionDeltaLocked导出调用、Private removed QSet/staged QHash删除。已排序immutable数组共用查询与释放，surface format的Qt字节仍共享原数据，不宣称全部default/epoch存储已收费。Private连实际std共享控制块由原retained allocator收费，per-cut default map节点先于buffer创建准备；最后Store引用在成员/root/default销毁后归还，控制块之后释放仍归原收费owner。

singleton retain/release直接操作原overflow链，retention增长在shard gate外准备并复验revision，release不构造投影；空block及charge转入同release记录，到原gate-free disposal才归费。旧投影输入/安装路径在该范围退出。mixed sequence和StateMachine/reference oracle仍有真实消费者，不删其语义；解保护后的history/key和epoch交接仍可能拒绝，原versionReleased/snapshotReleased/next保留，不能重放已完成token，也不新建恢复阶段。

最终双架构7组 **5358 passed / 0 failed / 0 skipped**，14进程正常退出。新增Reference真实MetadataArena-full行验证retain拒绝不修改、scalar/native查询可用、paid candidates拒绝保留输出、hard-full release及detached block实际归费；新增CPU原shared-parent行覆盖default map/capture拒绝、immutable removed/default cut、更新后旧cut、abort/facade销毁/晚guard与最后free。原capture/read/history/close/manual/brush压力及取消保持。目标首次失败为并发测试仍要求1600次投影输入，改为0 input/0 install并保留原record/oracle/1600转换断言；中间完整矩阵x86_64取消写后default read空结果暴露新增锁外查询窗口回归，修为只在容量不足时打开准备窗口、首candidate先于default materialization准备，容量齐全后查询/准入保持原owner gate。两类失败及中间源码/运行物身份保留，不与最终结果累加。

生产10文件 **+363/-147，净+216**，测试2文件 **+137/-10，净+127**；生成审计单列。新增成本来自actual scope/control/aux收费、锁外准备和无投影slot修改保证，不能称为纯去重净简化或性能收益。一个test friend只用于原private shared-budget边界，没有公开probe/API。18项替代/删除检查及结构门见证据，未提高门限；未测分配、gate、查找或长期尾延迟。

**有限端点已交付，完整BR1继续、CP1开放，M6/M7/M8正式资格0/3、默认关闭。** 下一为generic applyProjectedSequence、mutationBase/preparePublication及overlay准备→安装→清理的实际Qt容量；native seal/generic finishWrite仍有paid proof准备和其他Qt拒绝，Failed/cancel继续由真实consumer使用，自动job接续归CP5。TileDataStore登记、tree/deferred task、close handles/seen/诊断、Qt本体/bootstrap、Store/provider/Ledger及runtime/clock固定成本与完整永久压力最后handle仍欠。旧PID43034/87095仍UE/parent1，全局allocator、TSAN、公平、CP0同依赖对照与正式性能无新增资格。

<a id="publication-residue-delivery"></a>
### 16.48 CP1 清理：删除空 publication 效果协议与 detach 快照残余（2026-10-02）

按用户“回收过时分支、清理残余”核对§16.44–16.47之后的实际调用链。本轮产品父提交`e08545e5f2e77d1d8598032b8546f70eb93e932d`，聚焦提交`31dabb9789400c697851f553342f9051e4664c99`；文档父提交`6fb29d37f017112b7b48dfbaae22ed8e21445b1c`。示例中的allocate/retire/transfer/alias completion政策已由§16.44统一，本轮没有重复领取或新增终结保证。

StateMachine和生产consumer共同证明：CommitTransaction、ReplaceDefaultPixel、RestoreCommittedVersion保留旧replica为history；DetachPreparedVersion只改publication/preparedBy；AcquireRecoverableWrite→PrepareWrite转交backing。这些准备种类均不产生退休效果。删除PreparedPublication的effects容器、retirementEffects getter、install输出参数，以及PreparedMutationCommit的publicationRetirements字段和commit搬运空packet。原backing class reservation、history GC、foreground queue pump与abort实际效果交接继续承担各自责任。此处收紧§16.45中“publication效果”的宽泛表述：普通commit/restore自身不产出效果，真正的退休生产者为abort/cancel/discard/GC。

detach准备、activity复验和安装统一查询原record的isPreparedBy；删除前两个位置的完整版本/replica/protection快照及仅由复制带来的分配来源。writer、缺失/foreign版本、publication claim与整批原子拒绝仍可达，保留原检查；晚lease/pin/last-use/capture/handoff保护仍从原记录安装，未增加重试阶段。

一次完成universal构建后，最终双架构7组 **5358 passed / 0 failed / 0 skipped**，14进程正常退出。复用全状态oracle与实际CPU/Resident/Physical/Freehand压力取消测试，无新增数据行；原oracle改断言expected.effects为空，完整版本/保护对照保留。12项删除/保留检查通过。图在构建完成后生成：87 TUs、1956 APIs、21840 edges、21 callbacks；21 manifest/25 ownership/16 census/19 intrusion结构门通过，门限未变。47份源码、15份运行物、5份构建依赖身份绑定本轮提交。见[同源证据](evidence/br1_publication_residue_20261002/README.md)、[代码](br1_modification_guide/CODE_INDEX.md#publication-residue-code-index)和[API](br1_modification_guide/API_CONVERGENCE_MAP.md#publication-residue-api-delivery)。

生产3文件 **+14/-33，净-19**；测试2文件 **+31/-44，净-13**；生成审计2文件+3569/-3652单列，ownership未改。删除空协议、重复检查和快照，不新增业务保证、持久状态、队列或上层生产/API；未测性能。

本轮清理完成。read/capture进度事实、Pending/subscription/Delay/Debt、公开ticket拒绝、generic effects及Failed/cancel仍有真实consumer和拒绝来源，[检查结果](evidence/br1_publication_residue_20261002/deletion-checks.json)列明删除条件。generic metadata/overlay真实Qt容量、bootstrap/固定成本和完整永久压力最后handle等原CP1差集仍开放；M6/M7/M8正式资格0/3、默认关闭，排期与性能/TSAN/CP5接续资格不变。

<a id="publication-storage-delivery"></a>
### 16.49 CP1 实施：原 publication 候选存储与延迟释放的完整寿命（2026-10-02）

继续§16.48后的原generic metadata准备→安装→清理责任，产品父提交`31dabb9789400c697851f553342f9051e4664c99`，本轮提交`d9f15aa3ae0e29857873c1f3c7492a18694eb4e5`；文档父提交`e5e892c91187c419b145537b6f9d6f3fa0decd68`。最小目标为原PreparedPublication持有实际收费的安装值和原reservation，所有接受/拒绝/取消/晚清理沿同一候选；没有新增结果队列、持久阶段、预算权威或上层生产/API。

删除Data的make_unique未收费分配、entries/growth普通vector、delta/authority Qt容器和安装值嵌套Qt数组；原allocator直接支付实际Data、数组容量、hash节点/buckets及lease/last-use/capture数组。Entry.next只留原scalar header，重置versions释放Qt保留容量。原assign/putReserved/install共同政策消费这两种输入形态；安装physical重复检查删除局部QSet，采用无分配前缀扫描，generic batch的真实QSet consumer保留。MetadataArenaGrowth所有入口（publication、registerPage、captured、projected）删除未绑定预算的默认构造；未挂接payload先free再release reservation，holder容量继续收费至free。过时fused retirement注释同批清除。

MetadataBudgetAuthority原directory/block reservation提交后，把已经支付的费用记入同一KisMutationStorageOwner的保活字节，不重复收费；detach不再令晚release直接忽略费用。原controller销毁后，DeferredPublicationCleanup持有的shard/arena和candidate由该owner保留原shared parent/child，实际free才释放费用，最后owner free后unregister。clearBatch终点显式替换空DataPointer，连同deleter的allocator引用一起释放；拒绝候选的原activity/reservation仍由它取消。合法identity/revision/claim/writer冲突未消失，保留；paid准备拒绝仍终态返回原失败，未新建重试协议。

生产4文件 **+168/-56，净+112**；测试2文件 **+186/-23，净+163**；生成/ownership3文件+8560/-6534单列。净增用于实际收费、安装值所有权和controller晚退场缺口修复，不能计为等价去重；与保留Qt共享值并另行估算费用相比，直接使用原allocator可约束真实容量和实际free。复制/准备发生在原准备入口，锁域/claim与原安装顺序保持；未取得性能或短gate资格，physical单记录前缀扫描为O(replica²)，不宣称性能收益。

一次构建写者完成最终universal构建后，双架构7组最终 **5390 passed / 0 failed / 0 skipped**，14进程正常退出。新增16行覆盖commit/recoverable/default restore/detach的成功、取消、read churn及controller死后清理；真实parent恰满准备拒绝不改state/activity，释放压力后同输入可准备，再次恰满仍能安装，最终物理费用回到精确parent baseline。原full oracle和晚保护完整对照保留。旧压力夹具改为完成冷注册后实际filler恰满，缓存先暖至稳定容量，未放松被测压力或退出断言。初次编译错误、定向及完整矩阵失败和修正均保留在[证据](evidence/br1_publication_storage_20261002/README.md)。

最终图在构建结束后生成：87 TUs、1967 APIs、22024 edges、21 callbacks；21 manifest/25 ownership/16 census/19 intrusion结构门通过，门限不变。17项[删除/保留检查](evidence/br1_publication_storage_20261002/deletion-checks.json)、47份源码/15份运行物/5份依赖与本轮commit同源绑定。[代码](br1_modification_guide/CODE_INDEX.md#publication-storage-code-index)和[API](br1_modification_guide/API_CONVERGENCE_MAP.md#publication-storage-api-delivery)记录全部迁移与真实剩余消费者。本有限责任已交付；generic临时Qt投影/集合、mutationBase/overlay、既有shared核心与其他wrapper/bootstrap/固定成本和完整永久压力尾出口仍属CP1，M6/M7/M8正式资格0/3、默认关闭；TSAN、公平/CP5接续及BR1-PERF未取得。

<a id="mutation-base-query-delivery"></a>
### 16.50 CP1 实施：原首写 base 查询退出 Qt 投影（2026-10-02）

沿§16.49列明的mutationBase实际消费者，产品父提交`d9f15aa3ae0e29857873c1f3c7492a18694eb4e5`，本轮提交`276c675f6af1a80321aca7be4087fc05a086223a`；文档父提交`35e0f16661f5d660952234f962e833edbc62aee9`。原prepareWriteBaseLocked由native首写、generic acquireWrite及semantic alias/private replacement共同消费。它只需root base是否存在、writer、nextGeneration、sealed-or-root的exact authority与一个before候选，不需保留两个完整版本及lease/pin/last-use/capture列表。因此直接删除投影，未为该观察引入收费副本、重试阶段或协调owner。

删除mutationBaseSnapshot接口和所有调用，改为私有queryMutationBase：同一次原shard锁内读取标量与原replica链，保留root存在与selected存在的区别、原候选顺序/validity/operation/CPU/layout/physical条件。小型stack MutationBaseInfo无动态容器、持久事实或授权能力；原versionSnapshot与首写共用record VersionInfo描述，避免独立写两份authority/protection字段。调用者候选循环和快照findVersion删除，pending/removal/default发现控制保留；三入口不新增参数或分支。缺页/foreign、writer、缺selected authority、default materialization及descriptor等真实拒绝仍存在；联合准备继续复验并取得physical claim，不把观察当成handoff成功。

生产3文件 **+79/-52，净+27**；测试1文件 **+75/-9，净+66**；生成审计2文件+4150/-3801单列，ownership未变，上层生产/API零改动。净增用于必要标量结果、原record描述与完整候选读取；两个独立versionSnapshot调用无法维持同一shard cut，保留Qt投影并收费仍会复制消费者不用的保护容量，故采用直接原记录查询。此处消除查询分配来源，不宣称整体净删、性能或整个generic metadata已收口。

一次完成universal构建后，双架构7组 **5390 passed / 0 failed / 0 skipped**，14进程退出0，无新增数据行。原indexedMutationBaseLookup的0/255/4095 history行迁移并补实际MetadataArena恰满：候选顺序含wrong domain/layout/Allocated控制与带lease/pin/last-use/capture的有效before；验证writer、root/selected分别缺失、foreign拒绝保留输出、关闭候选发现和virtual default，live/backpressure不变；完整StateMachine结果与原记录对照保持。原production handoff/Fresh回退、native/generic首写、semantic/default/private replacement、publication/cancel及真实Freehand压力取消都在最终矩阵内。[本轮证据](evidence/br1_mutation_base_query_20261002/README.md)保留命令和边界，不能将恰满查询推定成后续写入准备必成功。

图在构建完成后生成：87 TUs、1968 APIs、22059 edges、21 callbacks；门限未变，21 manifest/25 ownership/16 census/19 intrusion通过。12项[删除/保留检查](evidence/br1_mutation_base_query_20261002/deletion-checks.json)、47份源码/15份运行物/5份依赖绑定本轮commit。[代码](br1_modification_guide/CODE_INDEX.md#mutation-base-query-code-index)、[API](br1_modification_guide/API_CONVERGENCE_MAP.md#mutation-base-query-api-delivery)同步。原首写观察投影不再列待办；generic StateMachine临时Qt投影/集合、overlay准备与清理、其他wrapper/shared核心/bootstrap/固定成本及完整永久压力尾出口仍属CP1。完整BR1目标保持；M6/M7/M8正式资格0/3、默认关闭，TSAN、公平/CP5接续和BR1-PERF未取得。

<a id="read-failure-residue-delivery"></a>
### 16.51 CP1 清理：原 read 终结链的过时分配失败分支（2026-10-02）

按用户“回收过时分支、清理残余”复核当前代码与§16.44–16.50的准备保证。provider allocate/alias/transfer/retire已共用prepared completion；空publication效果及首写投影已删除，不重复实施。本轮产品父提交`276c675f6af1a80321aca7be4087fc05a086223a`，聚焦提交`e8a9f1f34a19b1e65bf2d2bcde3698da9d4e7d2f`；文档父提交`c1745dcb4509f5f256d676cf30c8548ecbf32a7c`。未读archive，未push。

取消、lease释放、last-use确认共用原metadata保护节点的复用/移除；ReleasedBlocks只转移intrusive链，cleanup只保留原费用和活动。ack的registry订阅清理只unlink原记录；订阅冷分配拒绝已在armLastUseLocked归原retry，history准备/交接拒绝已在cancel/finishHistory入口保存原责任。因此删除cancel的metadata bad_alloc捕获、finishReleasedReadLocked/acknowledgeRecordLocked的外层捕获，以及后台retryCancelledRequests外层捕获和allocationFailed标记/重复计数。订阅前同一owner锁内的重复检查删除；锁外watch后的完整复验保留。原publication claim/identity拒绝继续返回false，已完成release不重放；history/captured/Pending/Debt与Failed/cancel仍有真实来源，[检查](evidence/br1_read_failure_residue_20261002/deletion-checks.json)列明保留依据和删除条件。

生产1文件 **+6/-17，净-11**；测试源码零改动、无新增数据行；生成审计2文件 **+218/-227，净-9**单列，ownership与门限不变。没有新增保证、状态、队列或API。一个universal构建完成后，双架构7组 **5390 passed / 0 failed / 0 skipped**，14进程退出0；复用真实hard-full last-use、subscription拒绝、cancel/close/stop、capture晚guard及Freehand压力取消。图为87 TUs、1968 APIs、22058 edges、21 callbacks，21 manifest/25 ownership/16 census/19 intrusion通过；16项删除/保留检查、47源码/15运行物/5依赖同源绑定见[证据](evidence/br1_read_failure_residue_20261002/README.md)。没有新增全局allocator、性能或完整永久尾退出资格。

本次read过时失败归属清理完成，[代码](br1_modification_guide/CODE_INDEX.md#read-failure-residue-code-index)与[API](br1_modification_guide/API_CONVERGENCE_MAP.md#read-failure-residue-api-delivery)同步。generic StateMachine/overlay的实际准备容量、shared核心/bootstrap/固定成本与完整永久压力尾出口继续原CP1；CP5原job接续仍开放。**M6/M7/M8正式资格0/3、默认关闭，完整CP1未结算。**

<a id="metadata-working-storage-delivery"></a>
### 16.52 CP1 实施与残余清理：同一付费 metadata 工作值贯穿转换与安装（2026-10-02）

沿§16.51之后的实际差集收口generic applyProjectedSequence与preparePublicationImpl临时工作责任。产品父提交`e8a9f1f34a19b1e65bf2d2bcde3698da9d4e7d2f`，聚焦提交`8896ac1dab5364e403048d9069703c4ed9dd0978`；文档父提交`603a936e19e083af1922a8ce622e678508189af5`。示例中的provider completion旧失败政策和read外层捕获在起点已回收，不重复实施；本批删除剩余转换/安装副本和可推导集合，同时补齐其实际收费，不新增持久阶段、队列或上层生产API。未读archive、未push。

原publication付费Version/Replica值扩为私有工作视图，直接从原record投影；lease、last-use、capture、version、effects数组和batch physical节点/buckets均使用原retained metadata allocator。公开Qt oracle和私有生产值共用一段StateMachine转换/身份/生命周期政策，删除公开Qt applyKnownValid及applyImpl包装。首份before/input保留供authority/delta/移除复验，后续transition消费并移动同一工作值；publication安装接收同一Version，旧Qt→paid二次复制删除。拒绝的私有工作值未安装即丢弃，公开apply拒绝仍返回原快照。

seen/included/previous/retained分别由原entries/before/next值见证，临时discard集合改用输入前缀和membership检查；无consumer的新增const工作state查询在退出审查删除。batch physical集合保留实际跨record唯一性责任并收费，全部插入和reservation先于record修改。原单record前缀检查仍为O(replica²)，其他集合改扫描也有查找成本，未取得性能或短gate资格。相比两套转换算法，共享政策避免生命周期分叉；相比直接修改原records再补回滚，付费局部值使混合sequence和effects准备拒绝继续发生在权威修改之前。

公共Qt effects/reason packet及Store/publication的下游聚合仍有真实cancel/abort/private-replacement consumer。本批先完成producer输出，再准备Debt和安装；后续付费工作区拒绝由原scope guard取消同cookie，没有新增恢复阶段。不能由此推定下游Qt搬运也已收费或不可失败。合法claim/revision/physical冲突、arena/activity/proof/overlay准备拒绝以及原Failed/cancel、read/capture/history/epoch进度仍保留，[23项删除/保留检查](evidence/br1_metadata_working_storage_20261002/deletion-checks.json)列明真实来源和删除条件。

最终universal构建完成后，双架构7组 **5396 passed / 0 failed / 0 skipped**，14进程退出0；每架Registry87、CPU1297、Reference680、Physical381、Resident221、Foundation28、Freehand压力/取消4。新增3个Reference数据行实际耗尽MetadataArena，覆盖read/release、private replacement和write/prepare/cancel；Debt准备后再次硬满，拒绝不改records/installed计数，原cookie全部取消、工作区费用回到精确baseline，解除压力后同输入成功并与完整Qt oracle对照。Debt receiver属于synthetic metadata oracle，真实provider/backing/queue交接由原矩阵验证，不能将替身当完整永久尾出口。中间working-02/03各5396通过及源码/运行物身份独立保留，不与最终数相加；初次signed warning修正，调用图审计输入变化拒绝及重新生成均保留在[证据](evidence/br1_metadata_working_storage_20261002/README.md)。

生产4文件 **+422/-266，净+156**；测试1文件 **+123/-0**；生成审计/ownership3文件 **+33655/-13528**单列。净增用于原预算下的实际工作值与共享容器操作，属于收费保证成本，不能计作等价去重净简化。最终图87 TUs、1989 APIs、24221 edges、21 callbacks；21 manifest/25 ownership/16 census/19 intrusion通过，门限未改。50份源码blob、15份运行物、5份构建依赖绑定本轮commit，tracked产品树干净；[代码](br1_modification_guide/CODE_INDEX.md#metadata-working-storage-code-index)与[API](br1_modification_guide/API_CONVERGENCE_MAP.md#metadata-working-storage-api-delivery)同步。

本有限工作责任已交付。下一沿公共effect packet及下游聚合到queue的真实接受/取消责任，与overlay准备→安装→清理继续原CP1；外部Qt oracle/注册/诊断、Transition输入、shared核心/bootstrap/固定成本及完整永久压力最后handle仍欠。CP5原job接续、TSAN、公平、CP0同依赖对照与BR1-PERF无新增资格。**完整CP1未结算，M6/M7/M8正式资格0/3、默认关闭。**

<a id="effect-acceptance-delivery"></a>
### 16.53 CP1 残余清理：原 Debt 提交直接接受退休 effects（2026-10-02）

本批从产品`8896ac1dab5364e403048d9069703c4ed9dd0978`、文档`24e432ad1ac31300db027806b7c405efd306d72a`收口producer→caller聚合→queue的完整责任，产品聚焦提交`7c90a4f07d9486391df22eb2cc7aed6bf8a5e171`。原paid effect span在metadata改变前准备，Debt提交回调直接转交exact backing的原退休record。metadata只返回accepted/rejectionReason；Qt effects输出、Store/publication聚合与append/copy、cancelPage/prepareAlias/PrepareAbort输出参数、History输出及二次交接、旧retireEffects入口同批删除。manifest原退休service符号同步替换，门限和其余内容不变。前几轮provider prepared completion和read旧捕获没有反弹；不重复计作本轮改动。

没有新持久阶段、队列或恢复record。相比给Qt聚合另配allocator，直接转交消除了权威改变后的第二份接受/增长责任。effect-bearing generic transition缺少receiver时在修改前拒绝，是本批补齐的保证；独立oracle consumer明确配置receiver，公共Qt StateMachine oracle保持原输出合同。真实paid working/Debt/arena/activity/index/claim/proof/overlay准备拒绝仍由原owner/cookie/Failed/cancel承担，不改报已发生事实。

同一m_ready保存原record的首次尝试，原backgroundRetirement决定worker许可；显式process额度包含foreground首次尝试，后台仍至多32条。foreground pump、worker和manual共用retireBatch，provider仍在Store/queue门外。operation未触及页回滚在后页Debt拒绝时也经过原退出pump，前页责任已接受且首次处理不会遗漏；原borrow仍保留两页逻辑claim，活动计数不被改成物理记录数。permission扫描及额外pump窗口有成本，未取得短gate或性能资格。

最终universal build-08后，双架构7组 **5404 passed / 0 failed / 0 skipped**，14进程均退出0；每架Registry87、CPU1301、Reference680、Physical381、Resident221、Foundation28、Freehand压力/取消4。新增generic三行实际耗尽原MetadataArena，验证Debt提交后硬满仍完成同node交接、foreground process(0/1)、原record许可与close物理释放、missing receiver拒绝不移除/不转Debt；新增双页operation回滚行只容纳一页Debt，后页拒绝泵送前页，解除压力后只取消剩余页，未重放且像素/close/费用正确。原partialCancellation、History无新输入retry、Pending不重发、晚通知和完整oracle继续通过。Reference旧receiver假设、两个新回滚夹具断言失败与编译错误均保留；修正以保持原claim和default读取materialization语义，中间通过不累加为最终资格，见[证据](evidence/br1_effect_acceptance_20261002/README.md)。

生产11文件 **+144/-156，净-12**；测试/模型3文件 **+240/-49，净+191**；生成审计/ownership/manifest4文件 **+13593/-13125**单列。compact result、共享batch和许可选择的保证成本计入生产差集；Store.h一行friend仅供原operation私有端点的integration test，不增加上层生产API。最终图87 TUs、1990 APIs、24268 edges、21 callbacks；21 manifest/25 ownership/16 census/19 intrusion门通过，阈值未改。50份源码blob、15份运行物、5份构建依赖绑定本地commit，tracked产品树干净，[23项删除/保留检查](evidence/br1_effect_acceptance_20261002/deletion-checks.json)、[代码](br1_modification_guide/CODE_INDEX.md#effect-acceptance-code-index)与[API](br1_modification_guide/API_CONVERGENCE_MAP.md#effect-acceptance-api-delivery)同步。

本有限接受责任已交付，overlay及外部Qt/注册/诊断/Transition输入、其他wrapper/bootstrap/控制本体/固定成本和完整永久压力最后handle仍属原CP1。CP5原job接续、全局allocator、TSAN、公平、CP0同依赖对照及BR1-PERF无新增资格。**完整CP1未结算，M6/M7/M8正式资格0/3、默认关闭。**

<a id="overlay-storage-delivery"></a>
### 16.54 CP1 原 overlay 存储与 History 拒绝政策收口（2026-10-02）

本批从产品`7c90a4f07d9486391df22eb2cc7aed6bf8a5e171`、文档`348c921f86972e4202bdfa9cc17358117a26ec28`继续，聚焦提交`5188f8d9c5c2a2e0e726a3ef667890e49b630585`。原交易state唯一保存overlay，candidate/index/state/control、proof/removal nodes/buckets、surface/version/change数组及旧node holders接真实MetadataArena。所有在途插入计入准备容量，surface准备与exact复验先于metadata install；安装只转交原nodes。commit/abort完成原owner cut的可见性修改后解锁释放聚合；已安装/收集候选晚于facade/controller的存储费用保持到实际free。

同批回收重复keys set、historical数组、derived extent完整Qt delta投影及临时RemovalSet、Qt surface detach/后置容量拒绝；私有detachment仅接受version身份，完整Transition数组和不可再进入的kind/operation/epoch检查删除。公共Qt oracle/commit/restoration仍保留真实consumer，writer、Prepared transaction及全页claim复验不变。producer输入在原解锁窗口交回容量，未增加锁外可见性缝隙。

History对同一节点拒绝原先后台保留rescanRequested、前台抛出，政策不一致。现在metadata持续拥有未退休版本，原collector保留missing-key扫描；foreground/worker复用collectPassLocked的一次枚举和原冷retry，后续清理拒绝不改报已发布结果。最初为候选复制History Work节点的方案使x86共享24MiB压力失败；沿原owner事实收敛后整套candidate节点删除。没有新增持久阶段、队列或恢复记录，真正的节点/GC/Debt和身份拒绝继续由原责任承担。

最终universal build-14与双架构7组 **5410 passed / 0 failed / 0 skipped**，14进程退出0；每架Registry87、CPU1304、Reference680、Physical381、Resident221、Foundation28、Freehand压力/取消4。新增三行实际硬满验证candidate/surface拒绝、两个在途候选、取消容量归还、安装后History节点真实拒绝；释放额度后无新key泵送原collector，两次物理退休且不重放安装。原controller销毁后候选仍收费，最后候选释放后child费用精确回到parent自有reservation cache基线。正常24MiB stroke、慢reader、finish、undo和取消断言未改。所有中间编译/配置/观察时序/cache及x86压力失败保留，[证据](evidence/br1_overlay_storage_20261002/README.md)只将最终同源结果裁作本批通过。

生产9文件 **+279/-181，净+98**；测试/模型2文件 **+228/-26，净+202**；验证工具1文件 **+2/-1**；生成审计/ownership3文件 **+11746/-10261**单列。净增包括actual收费/保活及无后置增长的保证成本，不能声称等价去重净减。图87 TUs、1996 APIs、24407 edges、21 callbacks；21 manifest/25 ownership/16 census/19 intrusion门通过，checker旧QHash假设同步迁移到原paid TransactionMap，ratchet未改。API净+6是原私有存储构造/deleter、排序lookup/comparator与extent投影，无上层生产变化。52份源码blob、15份运行物、5份依赖绑定产品提交，tracked产品树干净；[22项检查](evidence/br1_overlay_storage_20261002/deletion-checks.json)、[代码](br1_modification_guide/CODE_INDEX.md#overlay-storage-code-index)和[API](br1_modification_guide/API_CONVERGENCE_MAP.md#overlay-storage-api-delivery)同步。

有限overlay责任已关闭；commit facade/descriptor/configuration indexes、外部Qt oracle/注册/诊断/Transition输入、其他wrapper/bootstrap/固定成本与完整永久拒绝尾出口仍属CP1。未安装candidate仍要求原owner/activity保活，不授予任意晚capability操作资格。CP0同依赖对照、CP5原job接续、全局allocator、TSAN、公平和BR1-PERF无新增资格。**完整CP1未结算，M6/M7/M8正式0/3、默认关闭。**

<a id="commit-descriptor-storage-delivery"></a>
### 16.55 CP1 原 commit/descriptor 实际存储与旧协议回收（2026-10-02）

从产品`5188f8d9c5c2a2e0e726a3ef667890e49b630585`、文档`c9bd8ded50c40084e6c6895ac3d3eef4af08eb24`继续，聚焦提交`7141769304ae83437db17339383e6f43e464963c`。全部 descriptor 登记在 metadata 成功前准备实际 paid 节点，native/generic/alias/implicit fresh 路径也早于其 provider 调用；初始 adoption 接收 caller 已拥有的 replicas，bytes helper 的真正拒绝继续由原预付退休记录承担，不宣称全初始化存储都早于外部 physical allocation。安装只转交节点或交换已有值；旧 putDescriptorLocked/post-success 插入、hash/bucket 容量协议删除。原索引唯一决定描述，相同布局共用 immutable 值/control；native Page 在原 claim/session 保护下借用该值，删除重复 Page 描述。冷准备的相等查找为线性扫描，版本查询为 O(log N)，不取得性能资格。

commit/restore Data、descriptor-change 数组和 descriptor/configuration 节点/control 接原 MetadataArena 与实际 free；旧未收费 make_unique、Qt 数组、额外 History key 数组和递归 virtual-default 重复准备删除。原同步调用栈持有 intrusive commit/abort claim，删除分配 QSet 的准入来源，不新增活动含义、阶段或 retry 队列。high-water 配置一次准备完整 paid 值，原子交换先于 owner/metadata/epoch 初始化；逐 surface 后置导入删除。真实 descriptor revision、metadata/root/claim/physical/backing 拒绝和原 History rescan/retry 保留；仅消除本批存储拒绝的后置副作用，不授予其他 bootstrap 失败全局原子配置资格。

最终 universal build-09 与双架构 7 组 **5412 passed / 0 failed / 0 skipped**，14 进程退出 0；每架 Registry87、CPU1305、Reference680、Physical381、Resident221、Foundation28、Freehand压力/取消4。新增一行实际 hard-full 验证节点/Data 冷拒绝、virtual-default 不注册 metadata、两个候选安装无增长、相同值不准备节点、配置拒绝无部分表、恢复后成功，以及 controller 退场后的 inert Data/node/control 最后释放。Data 测试触发 wrapper 实际 allocation，不替代所有语义 commit 阶段的硬满资格。原 24MiB stroke/慢 reader/finish/undo/取消断言保持；两次 x86 压力失败促使删除重复描述，空 allocator tail 和诊断合同失败均保留，只有无临时诊断的最终源码取得资格，见[同源证据](evidence/br1_commit_descriptor_storage_20261002/README.md)。

生产4文件 **+287/-134，净+153**；测试1文件 **+103/-1**；验证工具1文件 **+8/-3**；生成审计/ownership3文件 **+9471/-8060** 单列。净增为实际收费、准备前移与安全借用的保证成本，不能声称净减行重构。图87 TUs、2000 APIs、24547 edges、21 callbacks；21 manifest/25 ownership/16 census/19 intrusion门及[18项删除/保留检查](evidence/br1_commit_descriptor_storage_20261002/deletion-checks.json)通过，API净+4为原私有存储/claim/comparator及签名替代合计，无上层新生产API。native Page ceiling 收紧688→512，baseline ratchet字段不变。52源码blob、15运行物、5依赖绑定本地commit，tracked产品树干净；[代码](br1_modification_guide/CODE_INDEX.md#commit-descriptor-storage-code-index)与[API](br1_modification_guide/API_CONVERGENCE_MAP.md#commit-descriptor-storage-api-delivery)同步。

原Data/descriptor/configuration有限端点已关闭；下一为 commit/restore 的 Qt 工作输入/投影及真实 downstream consumer，公共边界和 epoch/core 依赖继续清点。外部Qt oracle/注册/诊断、其他wrapper/bootstrap/固定成本及完整永久拒绝尾出口仍属CP1；活 semantic candidate 仍依赖原owner，未授予任意晚capability操作资格。CP0、CP5原job接续、全局allocator、TSAN、公平及BR1-PERF无新增资格。**完整CP1未结算，M6/M7/M8正式0/3、默认关闭。**

<a id="prepared-fact-residue-delivery"></a>
### 16.56 CP1 准备保证传播与终结残余清理（2026-10-02）

从产品`7141769304ae83437db17339383e6f43e464963c`、文档`c52c547b1dc8e286d8031e7ede11fc5983f4164a`继续，最终产品提交`1427f464d57e54e9a16245ef4dfd7163d47cdb06`；中间提交`bdba047303e80570afc6698811eb88c0f28a04c9`及补齐 epoch 之前的完整身份/结果单独保留，未改写历史。Store 配置已经准备并成功终结唯一 host ticket，全部实际 seal/commit/restore consumer 删除旧缺票业务失败与候选回滚。commit/abort 的原同步 claim 保护原交易/proof；Ledger revoke 只 unlink/free paid node，私有 owned revoke 改为 void noexcept；同一 claim 内的 epoch 身份失配也不再回报可重试失败。身份破坏按不变量处理，两个 abort 假退出删除。公开身份拒绝与真实 metadata/root/backing/proof 容量拒绝保留。commit 直接查询原付费交易 state，删除 surfaceChanges QHash/preparedKeys QSet及重复 include；完整 input validity、数量和值比较仍保留，原 claim 覆盖全部解锁。

最终 universal build-02 与七组双架构 **5414 passed / 0 failed / 0 skipped**，14 进程正常退出。新增同一真实 Store 的混合 delta 行验证8类非法 export 拒绝后仍保留原交易/proof、合法乱序可提交；原一次 host ticket、claim/晚 capture、重准备/冲突、硬满与 24MiB Freehand压力/取消回归保持。生产3文件 **+49/-67净-18**，测试1文件 **+48/-0**；生成2文件 **+7535/-7167** 单列，覆盖本包两个提交的完整差集。没有新持久阶段、队列、上层生产 API 或业务保证；surface 查询采用原 vector 线性查找，多 surface 性能未测。最终图2000 APIs/24588 edges/21 callbacks，21 manifest/25 ownership/16 census/19 intrusion独立门及14项删除/保留检查通过，ratchet不变，52源码blob与15运行物绑定最终本地提交。见[同源证据](evidence/br1_prepared_fact_residue_20261002/README.md)、[代码](br1_modification_guide/CODE_INDEX.md#prepared-fact-residue-code-index)和[API](br1_modification_guide/API_CONVERGENCE_MAP.md#prepared-fact-residue-api-delivery)。

surface 准备仍实际分配工作数组，不能删除其阶段或把拒绝改为断言；metadata/root/revision、Debt/physical Pending、公共身份及未迁移 consumer 的拒绝继续原责任。下一 Qt 输入/投影只领取剩余 proofDescriptors/directory/transitions/backing 与 restore 输入，不重领已删两份容器和缺票/owned revoke恢复。其他 epoch/core/bootstrap/固定成本和完整永久尾退出仍归CP1；排期估算不因净删行扣减。**本轮列明清理完成；完整CP1开放，M6/M7/M8正式0/3、默认关闭。**

<a id="publication-input-storage-delivery"></a>
### 16.57 CP1 原 publication 工作输入、候选释放与完整 write set（2026-10-02）

本批沿原commit/restore→metadata/epoch/Ledger→复验/安装/释放收口工作输入。目录只保留paid version identities，target查询同shard cut返回必要标量；publicationHeaders/publicationSnapshot及唯一Qt oracle调用迁移删除。原immutable描述只保留付费shared_ptr数组；commit compact changes与restore target数组归原Data，metadata逐页stack Transition复用既有转换政策，两个完整Transition数组删除。restore从原immutable surfaces推导default变化，原target prefix排序去重/二分查询替代changedDefaults/seen/targeted，full root直接写入已付费容量，manifest中间副本删除。backing数组移动到原Ledger cookie/slot，private friend seam替代生产Qt→付费复制。

metadata/epoch候选从准备起就在原Data，所有冷拒绝、revision retry及安装后释放共用原门外discardCommit；独立discardPreparedCandidates、四处手动discard和后置move同批删除。真实硬满暴露原epoch已接收完整delta后，backing拒绝再commit会按incremental generation重放。private preparePublication与公开prepare共享prepareImpl验证/原子写回：生产完整owner-validated write set替换原交易记录；公开incremental仍拒绝相同generation。同交易可以原输入重试，也能拒绝后继续改写原proof，不新增重试阶段或第二权威。

最终universal build-10后七组双架构 **5534 passed / 0 failed / 0 skipped**，14进程正常退出。实际目录硬满/scalar查询/晚数组归费、大容量Ledger原数组交接/hard-full class commit/slot替换、早晚容量拒绝后的原交易重试和继续写入、Qt/native 54对oracle、full/重复乱序delta restore及晚目录复验通过；原claim/reader/rebase/conflict/descriptor和24MiB Freehand压力/取消保持。初始epoch接续失败及修正夹具/错误方法名的日志完整保留，不混入最终资格。见[同源证据](evidence/br1_publication_input_storage_20261002/README.md)、[代码](br1_modification_guide/CODE_INDEX.md#publication-input-storage-code-index)和[API](br1_modification_guide/API_CONVERGENCE_MAP.md#publication-input-storage-api-delivery)。

生产7文件 **+336/-237净+99**，测试2文件 **+202/-9**，生成2文件 **+13919/-12472**单列。这是实际收费/拒绝和完整write set接续的保证增量，不能记为等价净简化；无新持久阶段、队列或上层生产API。保留付费descriptor pointer数组以避免逐proof反复获取owner gate；Qt数组附加估算额度不能限制实际容量。partial restore内部准备顺序改为页键排序，K去重O(K log K)、目录查原prefix O(log K)；多surface及峰值/正式性能未测。最终图87TUs/2005APIs/24727edges/21callbacks，21manifest/25ownership/16census/19intrusion独立门、16项删除/保留检查通过，ratchet不变，52源码blob/15运行物绑定产品`36189cb3b1bc91d77ea565894bb1fd51f9b6056a`。

实际metadata/epoch/descriptor/backing/Debt准备及revision拒绝继续由原责任承接。公开Qt输入验证/oracle与原epoch工作值、root/core/control，TileDataStore observer、tree/deferred/close、其他wrapper/bootstrap/固定成本和完整永久尾出口仍欠；旧未退出进程不因本轮14进程成功而获退出资格。下一只领取epoch/core等实际差集。**本批列明输入/释放/重试清理完成；完整CP1开放，M6/M7/M8正式0/3、默认关闭。**

<a id="epoch-protocol-residue-delivery"></a>
### 16.58 CP1 残余清理：epoch 保护事实与 restore 验证复用（2026-10-03）

产品父提交`36189cb3b1bc91d77ea565894bb1fd51f9b6056a`，提交`9e0534018d9db0e1376272fb5889ae0d46deb639`，文档父提交`00cd19212d15d6e6a8935d049ba6d2d8e1947820`。provider completion旧分支在起点已删除，不重复领取，未读archive、未push。

current/active transaction/retention与collector在同一mutex下保护root；protectedRoot统一后续查询，删除两处base丢失业务失败、current capture缺root软失败及默认空root投影。release接受token后直接消耗原count，缺count静默成功分支删除。restore复制原已验证root，仅改受exhaustion guard约束的发布身份；逐字段重建、重复QSet验证及validation假拒绝删除。公开非法/过期/foreign/伪造身份与真实准备/晚revision/activity/metadata拒绝保持。

initialize先插入root再发布current；transaction/retention先准备count槽，记录插入异常时局部guard撤销空槽，成功后才计保护。此异常安全修补支撑同一不变量，无新持久阶段/队列/重试政策。**Qt索引异常边界未注入真实allocator拒绝，不能声称实际容量或完整硬满保证已验收。**

最终universal build后七组双架构 **5534 passed / 0 failed / 0 skipped**，14进程exit0。原collector测试补验证最后token释放/GC后交易读旧base、继续prepare及真实conflict，三surface restore内容/revision及发布身份，epoch0非法surface view仍拒绝；原交错/候选/完整write set重试与Freehand压力取消保持。生产1文件 **+51/-64净-13**，测试1文件 **+28/-1净+27**，生成2文件 **+4578/-4299**单列。图87TUs/2006APIs/24753edges/21callbacks，21manifest/25ownership/16census/19intrusion及12项删除检查通过，ratchet不变。见[同源证据](evidence/br1_epoch_protocol_residue_20261003/README.md)、[代码](br1_modification_guide/CODE_INDEX.md#epoch-protocol-residue-code-index)及[API](br1_modification_guide/API_CONVERGENCE_MAP.md#epoch-protocol-residue-api-delivery)。

**本批列明清理完成；epoch工作/root/core/control及tree释放仍欠，完整CP1开放，M6/M7/M8正式0/3、默认关闭。** §17剩余估算不按净删行或通过数扣减。

<a id="epoch-transaction-storage-delivery"></a>
### 16.59 CP1 原 epoch 写集：实际容量、同记录准备与门外释放（2026-10-03）

产品父提交`9e0534018d9db0e1376272fb5889ae0d46deb639`，提交`1bc171aefe59b5931fead205155311292f3534ca`，文档父提交`bb4e659b9db39467e7015fd9285d1f476b4071f7`。本批围绕原交易写集的准备→复验→commit共享→最终释放，不重复领取§16.58已删分支，未读archive、未push。

原record保有一个immutable delta：值/实际shared控制块和changes、surfaceChanges、removedPages三数组容量由原retained allocator收费。prepare同锁捕获base/旧值/revision，门外准入和构造，回锁重新查原record并验证revision后替换；拒绝保留原值及revision，局部存储自动归还，不增失败阶段/队列。私有native完整集相同则复用原值和revision，检查前于exhaustion与分配，不使已准备root失效；公开incremental仍要求generation推进。修复公开增量“先remove后write”与相反顺序的政策不一致，两种交叉都原子拒绝，完整集替换保持合法。

prepareCommit共享同一原immutable delta；dense分支用原收费数组按页键merge，删除replacement QHash、removal QSet、current.manifest Qt中间副本及重排。原sparse AVL与dense阈值保留。collection用原finished链摘取原记录，门外释放实际值/容量，回锁重新取下一记录。Store/Publication全部7处生产transaction Qt导出迁到私有active identity查询；公开transaction仅作为有实际consumer的冷Qt oracle导出。辅助change/surface/removal索引和旧Qt写集删除。

最终universal build后七组双架构 **5562 passed / 0 failed / 0 skipped**，14进程exit0。每架新增14个Reference案例：真实硬满共享值/control与三数组拒绝、同原交易接续、root准备后硬满相同完整集复用、controller退出后的原收费owner尾释放、并发prepare只接受一个revision、相反incremental顺序与complete替换。并发案例不宣称强制双方同时处于锁外窗口。原commit/rebase/conflict/collector、候选与Freehand压力取消保持。图87TUs/2011APIs/24882edges/21callbacks，21manifest/25ownership/16census/19intrusion独立门和15项删除/保留检查通过，ratchet不变；52源码blob/15运行物绑定本提交，见[证据](evidence/br1_epoch_transaction_storage_20261003/README.md)、[代码](br1_modification_guide/CODE_INDEX.md#epoch-transaction-storage-code-index)及[API](br1_modification_guide/API_CONVERGENCE_MAP.md#epoch-transaction-storage-api-delivery)。

生产4文件 **+229/-130净+99**，测试1文件 **+199/-0**，生成2文件 **+8147/-6806**单列。实际收费、门外准备/释放、原值保留及相反输入政策修复是保证增量，不能记为纯去重收益。Qt数组附加估算额度不能限制实际容量；原位可变数组不能同时满足三字段拒绝原子性及解锁共享，故使用原交易唯一不可变值，无新上层生产API/持久阶段/队列。surface membership仍线性，正式峰值/多surface性能未测。

**本批原写集及dense工作数组已交付；完整CP1开放，M6/M7/M8正式0/3、默认关闭。** 下一实际差集为epoch root surfaces/tree/core/control与Qt registry、原tree最后释放/deferred task。公开Qt输入验证/oracle/嵌套format数据、原QShared core及standalone bootstrap、其他wrapper/登记/固定成本和完整永久尾出口仍欠，不把原工作数组重新列入待改。CP0、TSAN、全局allocator、公平/原job接续及BR1-PERF无新增资格，§17估算不按净增行或通过数扣减。

<a id="epoch-root-storage-delivery"></a>
### 16.60 CP1 原 epoch root/core：实际存储、原保护事实与冷尾释放（2026-10-03）

产品父提交`1bc171aefe59b5931fead205155311292f3534ca`，提交`e0fc83ab79a2d761bd61cdae64226a569330d3bb`，文档父提交`7a88750a74b4c00b981cd6509d5d11e003bfb433`。本批沿原configure/initialize→root候选→保护/collector→最后immutable引用实际free闭合，不重领§16.59原写集，未读archive、未push。

原Private及实际std共享控制块在首次initialize门外收费准备，最后原子安装；未初始化facade不创建Private。roots/transactions/retainedSnapshots三组original ordered节点使用同一retained allocator，实际node在epoch gate外准备，重新查原事实、复验逻辑准入/revision/token后无增长插入。transactionBaseCounts与retainedRootCounts删除，保护计数放回原root record，已有protected list继续作唯一可达遍历；原cancel/release/finished/root collector抽出实际节点，门外析构归费。已验证root与完整输入成为构造权威，重复root验证/QSet及“surface替换找不到base”业务失败出口删除；公开输入、身份、晚复验/真实容量拒绝保留。

immutable root surfaces的原值/control/实际数组、tree原节点/实际共享control同原owner收费，页变化共享旧surfaces，仅实际surface变化复制原数组。Publication restore直接遍历原surfaces，生产Qt导出删除；公开Qt oracle/retention/serializer仍有消费者。每个原tree storage冷准备一个收费reusable task；最终deleter只把已失去最后共享引用的原节点接入intrusive list，每pass最多实际free128节点，taskPin覆盖invoke/finished。TreeReleaseBatch、deque、TLS activeTreeRelease、析构时创建task和前台树节点析构删除。原raw root/cancelled candidate可在facade/controller退出后保有惯性收费至实际free，不能据此恢复逻辑准入。

Store先准备原epoch候选，全部冷配置准备成功后才安装可见epoch。default high-water和已接受metadata配置直接复用原事实；host source已接受而首ticket拒绝时，原Store用两个必要字段保留registry/source receipt，同入口重试只续allocatePending，foreign registry拒绝。未增失败阶段或恢复队列。只调整顺序不足以消除外部Registry的source→ticket部分接受；跨Registry改为原子bundle需要扩大其API，本批保留最小原接受事实，未宣称完整bootstrap/close资格。

最终universal build后七组双架构 **5594 passed / 0 failed / 0 skipped**，14进程exit0。每架13个新Reference有效案例覆盖core/control、manifest/surface数组、部分树构造、transaction/retention/restore节点、sparse/dense/surface准备真实拒绝、单次初始化竞争及8192节点满额尾释放；controller存活/退出两行均验证下一预存job在128个实际free后得到执行，最终精确归费。3个新CPU有效案例覆盖metadata/source/首ticket真实拒绝，同Store接续且source不重登记。并发初始化不强制双方同时进入门外窗口；旧fee测试修正为分开事务/scope/collector寿命。失败及中间通过日志保留，仅最终源码授予本批资格。图87TUs/2019APIs/25183edges/21callbacks，21manifest/25ownership/16census/19intrusion独立门和22项删除/保留检查通过，ratchet不变；52源码blob/15运行物绑定本提交，见[证据](evidence/br1_epoch_root_storage_20261003/README.md)、[代码](br1_modification_guide/CODE_INDEX.md#epoch-root-storage-code-index)及[API](br1_modification_guide/API_CONVERGENCE_MAP.md#epoch-root-storage-api-delivery)。

生产4文件 **+553/-356净+197**，测试2文件 **+328/-14净+314**，ownership合同1文件 **+3/-2**，生成2文件 **+15946/-12949**单列。收费/门外准备释放/满额最后free与配置接续是保证增量，不计纯去重收益。Qt索引附加估算不能约束实际node/control容量，ordered node支持门外准备及无增长安装；查找由hash平均O(1)变O(logH)，冷default复用核对O(S²)，正式性能/峰值未测。上层生产API零新增，两个配置receipt字段不隐藏为等价删除。

**本批原epoch root/core/三registry/surfaces/tree及raw最后释放已交付；完整CP1开放，M6/M7/M8正式0/3、默认关闭。** 下一实际差集为其余原wrapper/登记/shared控制本体/bootstrap与close/runtime固定成本，TileDataStore observer登记及全部参与者的完整永久拒绝最后handle退出；公开Qt输入/oracle/嵌套format数据和standalone controller/facade/process bootstrap仍保留实际消费者及欠项。原seal/generic准备拒绝仍由Failed/cancel承担，自动job接续归CP5；CP0、TSAN、全局allocator、公平及BR1-PERF无新增资格。§17估算不按净增行或通过数扣减。

<a id="residency-protocol-cleanup-delivery"></a>
### 16.61 CP1 驻留协议残余清理（2026-10-03）

产品父提交`e0fc83ab79a2d761bd61cdae64226a569330d3bb`，提交`69a01e929abce246bfeed0603dbf0825088e28a1`，文档父提交`8f597fcbbbde4bdc015db9808f27353bdf391dc8`。本批执行旧协议回收，alias/allocate/retire的completePrepared政策在起点已经统一，不重复计作新增交付。未读archive，未push。

原Transition一经创建即接受serial取消责任，局部guard只覆盖接受前的真实分配拒绝；删除接受后的第二份局部取消责任。原physical commit已经移动像素，untrack又等待原serial，丢失payload/serial或非新revision只能是合同违例；两个静默return删除。原allocation唯一持有准确的physical引用，releaseReference不再把丢失payload/slot/count改报“非最后引用”。真实reader/active transition、非法source/identity、冷容量拒绝和失败前回滚继续保留。

登记删空重建后数值revision可能相同，swap原Qt数组已被准备候选保留，因此直接比较constData身份即可拒绝旧候选；无需第二generation表、持久阶段或新容器。新增确定性暂停callback时序，旧候选取消一次、新候选提交一次，同数值revision仍成立。该ABA修复是保证增量，不能算等价去重。

未提交observer收费迁移曾扩大本次清理责任：其build-05候选七个新CPU数据行通过，但x86_64原24 MiB freehand出现实际metadata容量拒绝，隔离运行复现；该候选已撤回，原diff/失败日志保留，不降低预算或断言。最终build-06只含上述有限协议清理，原登记/observer/Transition Qt存储仍欠CP1收费，不授予候选资格，见[完整证据](evidence/br1_residency_protocol_cleanup_20261003/README.md)。

最终双架构八组5614/0/0，16进程退出0；每架Registry87、CPU1315、Reference762、Physical381、Resident221、Foundation28、Freehand4、tile-store9。生产2文件+14/-10净+4，测试1文件+44/-0，ownership1文件+3/-2，生成2文件+6109/-6107单列；新增身份复验及必要合同说明不隐藏为净删。主干仅TileDataStore.cc+3/-0，API/字段/include/friend/锁/TLS新增0，普通未观察tile没有新增存储或扫描。最终图87 TUs、2019 APIs、25183 edges、21 callbacks；21 manifest/25 ownership/16 census/19 intrusion及原ratchet保持，17项删除/保留检查、56源码blob/16运行物绑定本地commit，见[代码及MI账本](br1_modification_guide/CODE_INDEX.md#residency-protocol-cleanup-code-index)、[API替代](br1_modification_guide/API_CONVERGENCE_MAP.md#residency-protocol-cleanup-api-delivery)。

本有限残余清理已交付；完整CP1、CP0、全局allocator/TSAN、公平/原job接续、全部参与者永久尾出口及BR1-PERF仍开放，M6/M7/M8正式0/3、默认关闭。下一实际存储差集不因撤回候选或通过数缩减，按NEXT及§17继续。

<a id="cp0-matched-baseline-delivery"></a>
### 16.62 CP0 同依赖 upstream 与真实普通 freehand 基线（2026-10-03）

本批从完整§17领取最早缺失的同依赖对照。产品父提交`69a01e929abce246bfeed0603dbf0825088e28a1`，产品提交`cd6c8394a6e49b9758176f120efe49a5df02611f`，文档父提交`eb9cbccf00bb25a6f21fbac05a97399df4ac763f`，固定upstream`9a24ae0d8c070884fb013594191002e1a1b39a19`。独立upstream universal构建的15项实际cache选项与current相同，共用Qt6.8.0/Core、Xcode17/SDK26.2、RelWithDebInfo、deployment12及相同common运行依赖路径/hash，各自image/ui/brush/LCMS来自各自build。upstream只增加同字节测试入口/夹具和CMake登记，生产未改；身份、命令、预注册与全部失败见[证据](evidence/br1_cp0_matched_baseline_20261003/README.md)。

独立`MatchedFreehandBaselineTest`共用原SDK image/resources、普通FreehandStrokeStrategy、真实brush/jobs/update/scheduler：快照前显式Buildup/OVER，512² RGBA8、48px auto brush、4 workers、8条固定pressure线段及4次正常update，验证一次undo/redo和原strategy/image最后引用释放。双方用lazy原plugin registry和同一五插件，避开该preset不需要的全字体DB启动；旧slot、临时调试、QObject destroyed误报探针删除。该入口不授予全应用启动或全插件cold setup资格。

能力运行暴露当前原memento缺canonical dirty extent：undo清空图层但projection仍painted。原history commit从同一prepared/removal delta取得bounds，接受后在原gate写入原memento四个字段，原transaction undo/redo继续setDirty；没有新phase/队列或手动refresh。低层`KisMemento::setExtent(QRect)`新增一个真实consumer，上层生产API新增0。生产2文件+25/-1净+24是已证实保证修复，不能算等价去重；普通history终结增加原delta查询/扫描，其Qt导出、收费和拒绝仍归CP1，不声称零分配/commit-only。

双架构目标回归 **4210/0/0**、8进程退出0（每架CPU1315、Reference762、Freehand普通/持久/失败/24MiB压力/取消11、相关DataManager17）；四个最终dyld能力进程各3/0/0。每架12对独立交替进程，48进程均3/0/0、blank/painted hash相同。描述性均值current/upstream：arm64 stroke→projection-ready **10.621/3.870 ms**、undo **0.803/0.087 ms**、redo **1.832/0.171 ms**；x86_64对应 **18.370/6.073、1.337/0.143、2.871/0.324 ms**。fixture total被setup主导，接近不能抵消这些回退。普通strategy未opt-in persistent mutation，不表示DataManager PageStore adapter关闭；原constructor仍配置该adapter。此小样本不授予关闭状态成本、M/K/E、canvas-visible、2%非劣或P95/P99资格。

完整arm64 DataManager另有 **353 passed/25 failed**：24行writablePinsAcquired为旧期望两倍，ChangedStorage抛bad_alloc后未完成退出。缺同父版本全套运行，不能把它们都断定为旧失败；未改期望/额度或删测试。原testui启动PID59123与完整DataManager PID70089在TERM/KILL后仍UE；前者sample定位字体thumbnail，attach未能暂停。不宣称所有尝试drain、全套回归或永久尾出口通过，失败不混入成功计数。

架构门保持87 TUs、2019 indexed APIs、25183 edges、21 callbacks及原19-file ratchet，source checkpoint更新而ratchet未放宽。测试+245/-0、ownership+1/-0、生成+1361/-1361单列。CP0取得可运行同依赖对照和该代表性基线；完整required及其他场景/正式样本仍开放。完整BR1、CP1、M6/M7/M8正式0/3、默认策略资格、公平/原job接续、TSAN/allocator及BR1-PERF不缩减。下一审查原pin/prepare成本和DataManager容量/退出，并补齐CP0 required inventory及真实canvas/M/K/E准备；不按pilot或通过数扣人日。

<a id="execution-preparation-reuse-delivery"></a>
### 16.63 原 execution 准备复用与 extent 增长修复（2026-10-03）

本地产品提交`43799912101df77e6ebae0dc4d5c3622b7f0a6b3`，产品父提交`cd6c8394a6e49b9758176f120efe49a5df02611f`，文档父提交`4a6ecf258c2bd2bb4436051cc20ca285d9b45109`。本批沿§16.62已暴露失败查原owner：pin计数并非重复fold，prepareWrites和callback确实各取得guard；ChangedStorage独立K257也抛bad_alloc，debugger定位原ExtentManager增长/tryCommit刷新。完整失败、原始调试与身份见[证据](evidence/br1_execution_preflight_20261003/README.md)，未读archive/未push。

原execution只为缺失Page前置mutable backing，已有pending由同linked BoundEntry/原reservation承接，暖页重复prepare guard/pin/restore删除；真实guard仍重新pin并按需swap-in，不保留像素指针、不增加resident保证。cold refusal和未写页取消保持。D=1/10/1000实际pin由6/42/4002变为6/24/2004；`2D+1` callback加3次冷准备明确计账，checkpoint fresh generation、旧capture及commit/abort仍正确。原Growth过去每次向左扩展都把slack留在右边，导致小负坐标序列指数扩容；现在同Growth在扩展侧保留slack，原两轴先分配、复验/共同安装和实际拒绝不变。没有新阶段/容器/恢复协议。

首个完整arm64 manager1055/2正常退出，又暴露两条旧并发generation期望：cursor前置声明两页后，未写页取消仍消耗一次generation。按真实合同更新并补sealed/cancelled/活动写页归零断言，不缩范围/加预算。最终双架构十进程 **6304/0/0**、均exit0：每架CPU1319、完整manager1057、Reference762、Freehand普通/持久/失败/24MiB压力/取消11、Matched3。原`LIMIT_LONG_TESTS=1`及stress/benchmark包含在manager结果；新四BPP真实swap验证warm prepare pin/materialize0、实际guard各1、原版本/字节/最后退出。Matched同一五插件/共享fixture像素与§16.62一致，本轮未取得新upstream独立配对性能，不能把pin减少视为普通stroke回退已经关闭。

生产2文件 **+14/-4净+10**，测试3文件 **+90/-4**，ownership+1/-0、生成+8182/-7858单列。暖页减少实际重复工作，extent是缺口修复，不计等价净删；主干仅ExtentManager.cpp+8/-2，API/字段/类型/状态/锁/TLS/队列新增0。架构87TUs/2019APIs/25219edges/21callbacks，21manifest/25ownership/16census/19原侵入及ratchet不变，20份改动/关键consumer源码和107运行物绑定本地提交。

旧失败进程59123/70089及本轮独立复现83020仍UE，不能声明所有尝试drain或完整永久尾出口通过。extent原数组和其余Qt/控制本体收费未关闭；完整CP0/CP1、allocator/TSAN、公平/原job接续、M6/M7/M8正式0/3、默认persistent策略资格与BR1-PERF仍开放。下一继续实际wrapper/bootstrap/固定成本和尾出口差集，同时补齐CP0 required/canvas/M/K/E；不重领本批准备/增长修复，不按通过数或pin计数扣排期。

<a id="resident-binding-storage-delivery"></a>
### 16.64 原 CPU binding 实际存储与最后 handle（2026-10-03）

本地产品提交`50304c3da6881c535e790b3b64dd0f02a812469c`，产品父提交`43799912101df77e6ebae0dc4d5c3622b7f0a6b3`、文档父提交`296fb283024b41a50c0de3a9d7c818677c91f9a0`，见[Git身份](evidence/br1_resident_binding_storage_20261003/git-round-identity.json)。本批闭合原binding对象/control的实际准入与最后free，未读archive、未push；完整设计、失败和同源证据见[记录](evidence/br1_resident_binding_storage_20261003/README.md)。

原adopt的Qt创建未收费，若只在该位置收费会新增像素工作后的资源拒绝。现prepareAdoption在原allocation node内用observer retained allocator准备唯一binding及实际shared control容量，候选尚不持tile；原adopt只接受tile引用和原节点。所有生产provider、generic/native guard、reservation/handoff、read cache及metadata link共享同一std binding，测试三个实际派生类共同迁移。旧Qt binding创建、字段/参数/返回/cast同批删除，无桥接control block、第二binding或新回收协议；原身份/local gate/pin/readiness/retag/prepared completion政策保持。既有低层seam的表示发生变更，消费者需要共同重建，不声明旧二进制ABI兼容。

真实allocation/payload/slot拒绝补一行binding/control只少一个字节，证明拒绝发生于fresh像素准备前，原alias/fee/committed bytes/ticket不变，解除压力后同入口成功。四BPP×retire/provider退出/带read pin退出共12行证明退出后拒绝新pin、原pin字节仍正确；provider/controller已销毁时原allocation继续收费，最后强引用后weak尾仍收费，最后weak释放精确回parent基线。新增四BPP×33代read→release→fill→原retirement idle探针验证metadata cache每代1→0、像素正确；当前retirement/close已移除link，该探针在未改metadata路径上通过，未新增重复GC。

首轮双架十四进程 **7533/1/0**且全部正常退出：x86_64组合Freehand的24MiB pressure在checkpoint metadata preparation拒绝，slowReaderChecks=0。单独pressure及同组合复验通过，最终矩阵也通过，**首轮反例原因仍未确定、未关闭**；不能把索引共时当因果，不加额度/缩输入/降低断言。最终源码双架七组十四进程 **7542/0/0、全部exit0**：每架CPU1324、Physical393、Resident221、Reference762、完整manager1057、Freehand11、Matched3。manager保留原LIMIT_LONG_TESTS=1和stress/benchmark、线程/worker配置；92份源码与109个运行物冻结，最终测试前后运行物逐项相同。Matched像素/callback/原owner释放与§16.63一致，没有新的upstream独立配对性能，原stroke/undo/redo回退继续开放。

生产9文件 **+53/-43净+10**是实际收费、准备顺序及最后free保证增量；测试5文件 **+102/-19**、ownership **+2/-1**、生成 **+7374/-6992**单列。上层API/持久字段/状态/锁/TLS/队列新增0；TU内adoptTile一个真实consumer，生产改动仅原PageStore范围，主干原19文件ratchet未放宽。图87TUs/2020APIs/25258edges/21callbacks，架构21manifest/25ownership/16census/19intrusion通过，仅刷新source checkpoint。

此前59123/70089/83020仍UE，当前正常退出不证明全部尝试drain。首轮24MiB压力反例、provider/observer/Transition/Reservation本体及Qt控制、metadata link本体/control、source/read cache、Ledger/Registry/facade/bootstrap、固定成本与全部永久尾出口继续原CP1/CP5；原binding/control与已存在cache清理不重领。完整CP0/CP1、allocator/TSAN、公平/原job continuation、M6/M7/M8正式0/3与BR1-PERF均未结算，默认persistent策略资格不改变，不按通过数/净增扣人日。

<a id="checkpoint-preparation-pressure-delivery"></a>
### 16.65 原 detachment 候选残余与实际压力反例（2026-10-03）

产品提交`c8de106aacba42a9b4e5fbaafc6fa4d358bddbfa`，产品父提交`50304c3da6881c535e790b3b64dd0f02a812469c`、文档父提交`99c2b7223f13b07fcae1d7819c037447770c5f03`。同一原PreparedPublication负责准备、全部claim复验、安装、取消和最后分批释放，见[证据及全部失败](evidence/br1_checkpoint_pressure_20261003/README.md)。未读取archive、未push，不增加阶段或重建已有cache清理。

原六方法组合串行复现两种真实边界：上一轮运行物15进程164/1，24MiB入口在仍有活跃product Store时改变共享配置被拒绝，原夹具没有先完成排队终结；诊断8进程86/2进一步重现同一checkpoint拒绝，324页detachment为旧Entry数组申请269568字节，被共享进程预算拒绝。该Entry无条件保留完整发布快照和安装容器，detachment实际只用version/shard/activity/claim。旧记录的“原因未解释”是当时结论；本批确认该checkpoint准备拒绝来源，但不因此关闭完整24MiB场景。

原Entry只保留共同事实，完整Publication数据在同一Data内按实际种类准备；detachment不分配该数组。所有准备/安装消费者迁移，旧detachedVersion与Entry中的next/deltas/installRecords/arenaDemand/growthIndex访问删除。原cancel/claim/slot reservation政策保持，clearBatch每页先释放可选发布载荷，再释放其shard owner，收费随实际free归还。inline optional/variant仍需最大布局，逐页heap增加分配，因此采用同owner的publication-only批量数组；新增一个TU内载荷类型及数组，准备/安装/cleanup三处共同维护其配对，不称整体复杂度净删。

实际编译布局：旧Entry832字节，现共同Entry64、Publication768；detachment候选头部200→240，324页完整候选实测20976字节，双架四行一致。普通publication每页合计仍832字节，但多40字节头部及一次批量数组分配，代价单列。新测试给共享父预算仅留64KiB准备324页，再填满实际父额度，原安装和取消均完成；每页身份/Prepared或Historical/事务、published/nextGeneration与原17页cleanup单位正确，活动计数归零、实际费用精确返还。

TinyTileBudget只在切换/恢复全局配置的静止测试边界调用原reclamation drain，笔触中不加drain。保留24MiB/swap0、原输入/线程/慢reader/递归producer/undo-redo断言。诊断候选三进程32/1仍出现后续surface extent准备8304字节的共享容量拒绝；8MiB取消场景另有backend初始准入拒绝，现有cancel断言不能授予完整准入后取消资格。两者保留为同CP1固定成本/峰值/接受及退出差集，不能移走拒绝点或增加额度来宣称修复。

最终去掉全部临时生产诊断后，同源码双架七组十四进程**7546/0/0、均exit0**：每架CPU1324、Physical393、Resident221、Reference764、完整manager1057、Freehand11、Matched3。93源码及109运行物绑定本地commit，运行物前后相同，原LIMIT_LONG_TESTS=1和stress/benchmark保持；Matched像素/callback/owner释放同前，无新upstream配对性能。最终通过不关闭已保留的surface压力反例或8MiB准入缺口。

生产1文件**+50/-43净+7**，测试2文件**+70/-0**，ownership**+1/-1**、生成**+5279/-5035**单列；上层生产API、持久阶段、锁/TLS/队列新增0。架构87TUs/2020APIs/25285edges/21callbacks及21manifest/25ownership/16census/原19-file ratchet不变。此前三个UE进程仍未退出；完整CP0/CP1、全部参与者永久尾出口、allocator/TSAN、公平/原job接续和BR1-PERF仍开放，M6/M7/M8正式0/3、默认persistent策略资格不变，不据行数/通过数扣人日。

<a id="metadata-directory-storage-delivery"></a>
### 16.66 原 metadata 配置目录/control的实际收费与残余回收（2026-10-03）

产品提交`3959672c4a2bb134adcb171dedb19dadcba37ad1`，产品父提交`c8de106aacba42a9b4e5fbaafc6fa4d358bddbfa`、文档父提交`ae9332c73304c660b432b684b4a94c71240ce573`，见[Git身份](evidence/br1_metadata_directory_storage_20261003/git-round-identity.json)和[全部尝试](evidence/br1_metadata_directory_storage_20261003/README.md)。本批接续同CP1的实际固定成本与最后释放，没有读取archive或push。

原configure用shard对象+两指针控制块估算、三个arena最大目录和pointer数组汇总reservation，实际分配后再算容量、手工commit/登记fee；拒绝清空元素后仍保留数组capacity。现在同一原retained allocator实际收费shard对象/shared control、immutable shard pointer数组、三个typed arena directory和publication identity。原配置锁下准备局部完整候选，全部成功后安装原directory/identity，再release发布原operational；拒绝只销毁该候选，同对象可重试。私有arena constructor接受同allocator，三个实际consumer同步迁移，默认无预算bootstrap形式保留原测试consumer；block/hash收费、slot generation和4/8/4MiB各arena hardceil保持。

同批删除directoryCharge、shardObjectBytes、maximumDirectoryBytes、allocatedDirectoryBytes、directoryBytesForLimit、directoryReservation、目录手工commit/释放及“分配后超出预留再拒绝”协议，不新增持久阶段或收费权威。publication identity从构造期未收费分配移到原配置候选；prepare与install都先acquire原operational再读identity，未配置/foreign安装仍消费候选、共用原拒绝/cleanup。最终审查发现install原入口欠该acquire，已补齐并重新构建/验证，不继承初始运行物资格。原owningCapacity字段只有诊断/测试consumer，去掉两指针估算并明确为对象payload+原hash/index容量；实际directory/control费查原backing usage，未将它升为准入、关闭或调度事实。

新7数据行分别为1/4/64 shards真实共享父容量少一个字节、1/64 shards × cancel/已安装cleanup晚释放。连续三次配置拒绝没有残余shards/pages/owning capacity或reserved，完整候选费用回原基线；释放原filler后同对象成功配置，第二次配置仍拒绝，真实registerPage可用。空配置实际请求费为25,824/103,152/1,649,712字节，双架一致；coordinator和child controller退出后原candidate仍保留shard/parent费用，最后cancel或clearBatch(1)精确返还，最后parent引用退出。原合法publication向未配置owner安装的候选消费/后续配置也验证；此行为断言不代替TSAN或并发两次序资格。

初始目标31/0/0、十四进程7560/0/0与六方法三对压力66/0/0绑定构建03，全部原样保留。最终构建04对应双架七组十四进程**7559/1/0、均正常退出**：每架CPU1324、Physical393、Resident221、Reference771、完整manager1057、Matched3；Freehand arm64为10/1、x86_64为11/0。唯一失败是arm64 24MiB pressure在overlay surface storage preparation拒绝、cancelCallbacks实际1期望0；同一已保留surface准备边界仍可达，本次没有独立请求字节测量，不继承旧8304字节。原24/8MiB限额、输入/线程/慢reader/递归producer/undo-redo断言和manager LIMIT_LONG_TESTS=1、stress/benchmark保持，没有通过重复绿样本关闭失败。

93份源码、109个运行物和四份构建配置绑定产品提交，最终测试前后运行物逐项相同；Matched像素/callback/owner释放同§16.65，无新upstream独立配对性能。生产3文件**+36/-86净-50**、测试1文件**+128/-0**，ownership**+1/-1**、生成**+6648/-6403**单列；实际收费增加allocator成员保留成本，不把净删行当作资源/性能资格。上层API、持久业务阶段、锁/TLS/队列和外部生产侵入新增0；图87TUs/2017APIs/25322edges/21callbacks，架构21manifest/25ownership/16census及原19-file ratchet不放宽。

本批实际配置收费和拒绝/晚free闭环完成；eager最大arena目录仍使64 shard空配置约1.65MB，下一沿同一配置/增长owner审查固定容量与峰值，不降hardceil或另建失败阶段。metadata Private/authority本体/control、standalone/bootstrap、Qt注册/map/输入、link本体/control、source/read cache及其他wrapper继续原CP1差集。24MiB surface准备、8MiB初始backend准入、旧三个UE尝试、全部参与者永久拒绝/停止/晚handle/自主drain仍开放。完整CP0/CP1、全局allocator/TSAN、公平/原job continuation和BR1-PERF未结算，M6/M7/M8正式0/3、persistent默认关闭；不从通过数/净删行扣人日。

<a id="metadata-directory-growth-delivery"></a>
### 16.67 原 metadata 目录按需准备、竞争复验与旧数组释放（2026-10-03）

产品提交`453a5e9d1403da28aad85e51b68d1c995080ed6c`，产品父`3959672c4a2bb134adcb171dedb19dadcba37ad1`、文档父`737044ea4660a4315907b1004f09f265e4ea1f69`，见[身份](evidence/br1_metadata_directory_growth_20261003/git-round-identity.json)及[同源证据与全部尝试](evidence/br1_metadata_directory_growth_20261003/README.md)。本批关闭§16.66的eager最大目录差集，未读取archive、未push。

空arena不再分配最大目录；原MetadataArenaGrowth在shard gate内捕获块需求及目录几何，门外用同retained allocator准备，门内移动原DirectoryEntry并swap。Released可复用条目先抵扣，quarantine保持；block/slot payload地址、索引、generation及原4/8/4MiB hardceil保持。三个原growth carrier承接候选和退下的旧目录数组，门外实际free才归费；重准备先释放已不够用的候选，避免第三份无用数组。竞争使几何过时，publication通过原growMetadataArenasOutsideLock/revalidate接续，再预约原slot/index；有效PreparedPublication的install不增长目录。

同批删除constructor最大目录预留、fullMetadataArenaGrowthPlan重复规划及attach隐式vector增长；attach只能使用已经准备的容量。真实存储拒绝和stale几何沿原Exhausted/Stale/NeedsMore及候选清理，不新增业务阶段、锁、TLS、队列或收费owner。直接在attach中reserve违反门外准备约束，固定小预留不能兑现后续增长，分层目录会改变原查询/存储边界，因此继续原平坦目录和growth。仍保留一次增长的线性移动、新旧数组共存及原block/hash手工费用；不宣称全部释放均已移出gate或全部allocator精确收费。

双架1/4/64 shard空配置实际请求费为**1,248/4,848/76,848B**，比父源码分别减少24,576/98,304/1,572,864B，严格等于24KiB×shards；64 shard减少**1.5MiB、约95.3%**。这是backing预算请求费，不是RSS或全部bootstrap。生产2文件**+132/-44净+88**，测试1文件**+139/-9**，ownership**+1/-1**、生成**+8074/-6109**单列。新增一个私有PreparedDirectory类型和每原growth三个40B目录carrier，共120B；局部plan24→48B，实际目录数组另收费。此为按需增长、锁外准备和竞争接续的保证成本，不能记等价复杂度净删；上层API、持久业务阶段及外部生产侵入新增0，原19-file ratchet不放宽。

新leaf以真实父额度只差一个字节拒绝目录增长，原值/地址/fee保持；压力解除准备成功后再填满父额，安装目录和第二block仍完成。竞争候选确实不足时保留原数据，重捕获几何成功，最后目录fee精确归基线；该leaf的raw block本身不裁决完整收费。原晚candidate扩为1/64 shards×cancel/cleanup×detachment/default publication八行；真实ReplaceDefaultPixel在恰满四个version block后新增目录，coordinator/controller退场后原Data保有旧数组/shard/parent，最后cancel或clearBatch(1)精确归费。两轮夹具31/4/0失败保留：普通commit原位复用slot，改用真实新增version入口后35/0/0；未降低增长断言。

最终构建05同源码双架七组十四进程**7570/0/0、全部exit0**：每架CPU1324、Physical393、Resident221、Reference776、完整manager1057、Freehand11、Matched3。原六方法压力组合另跑三对**66/0/0、六进程exit0**，24/8MiB限额、输入/线程/慢reader/递归producer/undo-redo及manager LIMIT_LONG_TESTS=1、stress/benchmark保持。93源码、109运行物、四项构建配置绑定产品commit，测试前后运行物逐项相同。图87TUs/2025APIs/25510edges/21callbacks、架构21manifest/25ownership/16census/19intrusion通过；Matched像素/callback/owner释放同父源码，没有新upstream配对性能。

原24MiB surface准备反例在本轮矩阵和三对组合未重现；已证实固定预留消失，有限样本不关闭完整总峰值/永久压力尾出口。8MiB取消仍未独立证明完整准入后取消，旧59123/70089/83020仍UE，历史8304B只属其冻结源码。下一为原metadata Private/authority本体/control、standalone/bootstrap、其余wrapper/注册/link/cache及全部参与者接受/最后free/自主drain，不重领目录预留。完整CP0/CP1、全局allocator/TSAN、公平、原job continuation、BR1-PERF开放，M6/M7/M8正式0/3、persistent默认关闭；不从通过数或行数扣人日。

<a id="metadata-authority-storage-delivery"></a>
### 16.68 原 metadata authority 的配置准入与最后释放（2026-10-03）

产品提交`4c45738186bccf095b8cefd409e409c8accd637a`，产品父`453a5e9d1403da28aad85e51b68d1c995080ed6c`、文档父`413b7e03454b68f52b889fd32826e2d071a3a6ff`，见[Git身份](evidence/br1_metadata_authority_storage_20261003/git-round-identity.json)和[同源证据](evidence/br1_metadata_authority_storage_20261003/README.md)。本批接续原配置/收费/最后free责任，未读取archive、未push。

原Private构造期make_shared创建未收费authority，attach再重设其budget/accounting owner，第一次reserve另有补建owner的分配拒绝。现在配置前只由原configurationMutex保存预算选择；configure以同retained allocator先准备实际authority/control，再准备原shards/目录/identity，完整局部候选成功后一起release发布operational。authority在发布前已持原accounting owner；拒绝只销毁局部候选，原对象可重试。原shard、publication Data和read cleanup保有同一authority，coordinator退出detach其新准入，原controller退出后最后free仍沿原accounting寿命归费。

同批删除authority::attach、构造期未收费make_shared和reserve时补建owner/catch分支。原read/captured cleanup身份检查移到原shardFor的operational acquire之后，以原shard authority核对，避免读取尚未发布的共享指针；foreign拒绝保持。上层API、业务阶段、锁/TLS/队列和外部生产侵入新增0。原Private增加一个8B预算选择指针，配置前承担原attach事实，未增加第二活跃收费权威。生产1文件**+17/-29净-12**、测试1文件**+99/-2**、ownership**+1/-1**、生成**+6063/-5901**单列。实际配置请求费双架1/4/64 shard为**1,312/4,912/76,912B**，均比父源码增加**64B**，为原authority对象和实际共享控制块收费，不能记内存删除收益。

原配置拒绝扩为1/4/64 shards×第一笔只余1B/完整候选少1B六行，各连续三次拒绝、原对象重试；constructor/预算选择不触发authority收费。原晚publication/detachment八行继续通过。新增read-release/last-use ack×显式clear/析构四行，coordinator/controller退出后只剩detached read cleanup、没有shard或Data支撑寿命；原parent仍被保活，重新填满真实父额后clear/析构无需分配，原authority/control/child费用精确归基线、最后parent弱引用失效。原不可变目录并发consumer同时检查可见authority；不授予全局TSAN或完整并发两次序资格。

首个目标命令含两个未核对的方法名，QtTest执行前拒绝，0/2/0原样保留；改用实际方法名后50/0/0。最终同源码双架七组十四进程**7584/0/0、全部exit0**：每架CPU1324、Physical393、Resident221、Reference783、完整manager1057、Freehand11、Matched3；原六方法压力组合追加三对**66/0/0、六进程exit0**。93源码/109运行物/四项构建配置绑定产品commit，运行物前后相同；原预算/输入/线程/断言及manager LIMIT_LONG_TESTS=1、stress/benchmark保持。图87TUs/2023APIs/25535edges/21callbacks、原21manifest/25ownership/16census/19-file ratchet通过；Matched字节/callback/owner释放同父源码，没有新upstream性能配对。

authority本体/control有限收费与尾释放闭合；Private本体和内嵌standalone controller、其他bootstrap/Qt注册/link/cache及全参与者总峰值/永久拒绝/停止/晚handle/自主drain继续原CP1。直接在constructor收费会使后续configureLimits/shared挂接被既有非零live合同拒绝，不能为本批放宽它；这些bootstrap依赖应随原root准备/配置责任闭合。有限绿矩阵不关闭24MiB全压力或8MiB准入后取消，旧三个UE仍在；完整CP0/CP1、全局allocator/TSAN、公平、原job continuation及BR1-PERF开放，M6/M7/M8正式0/3、persistent默认关闭，不按提交/行数扣人日。

<a id="metadata-core-storage-delivery"></a>
### 16.69 原 metadata Private 的配置准入与生产固定成本清理（2026-10-03）

产品提交`ec3cebba5b4652c04c856b262065dde092c938b4`，产品父`4c45738186bccf095b8cefd409e409c8accd637a`、文档父`2c534180589f7910dbe81daaf7a668544d535645`，见[Git身份](evidence/br1_metadata_core_storage_20261003/git-round-identity.json)及[同源证据](evidence/br1_metadata_core_storage_20261003/README.md)。本批继续同一配置/收费/最后free责任，未读取archive、未push。

constructor不再未收费new Private。原预算选择、配置锁和Debt接收事实移到冷facade；configure以原retained allocator准备实际Private，连同authority/shards/目录/identity构成同一局部候选，成功后一次release发布core指针。全部shard/prepare/install/query/诊断入口acquire这一事实，独立operational删除；失败与最终析构使用同一Private::destroy，实际free后才归费。原owner静止析构、不可重配、foreign/claim及真实预算拒绝保持，raw core不增加shared控制块或RCU寿命。生产沿原attached controller，不再创建无用standalone controller；真正未attach的reference入口仍在configure创建自己的controller。

直接constructor收费会阻断既有Store的shared/limits→configure顺序；事后估算补费另建收费权威，shared core又引入当前consumer不需要的共享寿命和控制存储。沿原配置入口准备完整runtime core，原配置事实不复制，无新业务阶段/锁/TLS/队列/上层API。私有constructor和destroy有真实候选/析构consumer；两个原shard helper改签名后旧方法同步删除。生产两文件**+128/-94净+34**，测试**+21/-2**、ownership**+1/-1**、生成物**+3935/-3719**单列。净增兑现实际Private收费与冷配置完整回滚，不记纯去重收益。

实际编译器布局双架Private **1,488→104B**、facade **8→56B**，attached生产对象尺寸合计**1,496→160B，减少1,336B**；这是对象尺寸，未包含allocator开销，不是RSS/峰值性能证据。实际配置费1/4/64 shard为**1,416/5,016/77,016B**，均新增原Private **104B**请求费，不能与尺寸删除混记。真正standalone仍创建1,352B controller，facade+core+controller尺寸合计1,512B，比旧形态多16B；该controller体及含facade的Store根对象、其他bootstrap尚未获得完整收费资格。

原真实拒绝六行新增冷shared/limits配置顺序及未配置空core消费者检查：只余1B时首个Private分配拒绝，完整候选少1B时局部对象全部释放，各连续三次无core/目录费用残余，压力解除后原对象配置/注册通过。原晚Data八行、仅read cleanup保活的controller后父硬满clear/析构四行、foreign/claim与并发一次配置继续通过；原standalone recoverable outcome9晚候选在两架完整矩阵中实际执行并释放。不以这些交错代替全局TSAN/两次序。

首轮构建测试漏传configureLimits第二参数，修正后构建02 exit0；冻结脚本首次在压力runner结束前按六进程完整性断言拒绝，原日志保留，等待实际退出后冻结通过。目标**50/0/0**；最终双架七组十四进程**7584/0/0、全部exit0**，原六方法压力组合追加三对**66/0/0、六进程exit0**。93源码/109运行物/四构建配置绑定产品commit且运行物前后相同；原24/8MiB/输入/线程/断言和manager LIMIT_LONG_TESTS=1、stress/benchmark保持。图87TUs/2025APIs/25550edges/22callbacks，21manifest/25ownership/16census/19-file ratchet通过；新增一个callback registration是原Private候选deleter地址。Matched字节/callback/owner释放同父源码，没有新upstream性能配对。

runtime Private收费及生产无用controller有限收口完成；真正standalone/controller、Store/其他根对象及process bootstrap、Qt注册/link/cache与全部参与者总峰值/永久拒绝/停止/晚handle/自主drain继续原CP1。有限绿矩阵不关闭24MiB完整总峰值或8MiB完整准入后取消，旧59123/70089/83020仍UE。原block/hash手工fee和合法准入拒绝保留；完整CP0/CP1、全局allocator/TSAN、公平、原job continuation及BR1-PERF开放，M6/M7/M8正式0/3、persistent默认关闭，不按提交/行数扣人日。

<a id="store-root-storage-delivery"></a>
### 16.70 生产 Store 根存储的冷准入与最后释放（2026-10-03）

产品提交`edd8eb815e99f4b845c659a5f1957d6cfa051c53`，产品父`ec3cebba5b4652c04c856b262065dde092c938b4`、文档父`4d62c749a5c926ac266bc4403c87f71186ec2327`，见[Git身份](evidence/br1_store_root_storage_20261003/git-round-identity.json)及[同源证据](evidence/br1_store_root_storage_20261003/README.md)。沿原backend prepareStore→Store配置→原lifetime最后free收口，未读取archive、未push。

生产唯一Store创建点已先取得共享父预算，configure和configureClone共用该点。现在原冷入口以临时栈controller挂同父预算，原retained allocator实际分配facade和原Private；返回前controller退出，原accounting继续持有原parent/child登记到最后free。Store内部controller仍按shared→limits→configure原顺序配置，未放宽非零live/reserved冻结。后置补费会另立收费权威；直接向process controller收费不能自行保活最后释放所需controller；逐尾pin或转移费用引入额外协议，因此复用原child/accounting，不新增业务阶段、队列或恢复owner。保存的根allocator仅用于释放，不在已退出controller上作新准入。

同批删除backend的`new KisPageStore`、Store的`new Private`及两处`delete owner`。局部构造拒绝原位回滚，原PrivateReleaser同步/退休线程共用Private::destroy，晚captured scope沿原lifetime释放；facade的destroyStorage独立退还实际facade存储。默认reference构造继续使用无预算allocator，仍未取得根存储收费资格；真实foreign/claim、内部配置及其他准备拒绝保持。

生产三文件**+66/-7净+59**、测试**+117/-0**、ownership**+1/-1**、生成物**+9135/-8416**单列。双架实际冷根收费**4,520B**＝facade8B＋Private4,392B＋原accounting/child登记120B；Private原4,376B新增16B allocator，facade一指针ABI8B保持。backend handle另存8B deleter函数指针，临时栈controller对象尺寸1,352B；这些为收费保证成本，不是减行、总峰值、RSS或性能收益。原metadata配置费1/4/64 shard **1,416/5,016/77,016B**保持。图2025→2029 APIs为私有构造/销毁与factory净增4，22→24 callback registrations为同一facade deleter的两个真实登记，未新增上层API。

新增四数据行：真实父额仅余1B时冷child登记拒绝、完整冷候选少1B时回滚，各连续三次无费/保留额度残余，解除压力后同父重试；cold facade及配置后late captured两行释放外部parent，原parent仍保活，再填满真实父额后最后释放/原drain精确归基线，原弱引用最终失效。不能把首child拒绝称为首Private分配拒绝。目标**7/0/0**，最终双架七组十四进程**7592/0/0、全部exit0**；原六方法压力组合三对**66/0/0、六exit0**。两次构建均exit0；首个冻结脚本误把MementoManager的new匹配成Store，修正精确类型检查后通过，原日志保留。93源码/109运行物/四构建配置绑定产品commit，运行物前后逐项相同；原预算/输入/manager LIMIT_LONG_TESTS=1、stress/benchmark及Matched字节/callback/owner释放保持，没有新upstream性能配对。图87TUs/2029APIs/25603edges/24callbacks，原21manifest/25ownership/16census/19-file ratchet通过。

生产Store facade及Private本体有限收费与实际释放已关闭，不重领；默认/reference/真正standalone根、其余嵌套Ledger/domainAdmission/statistics等heap/control、backend/provider/history根及process bootstrap继续原CP1。有限绿样本不关闭24MiB完整峰值、8MiB完整准入后取消、全参与者永久拒绝/停止/晚handle/自主drain；旧59123/70089/83020仍UE。完整CP0/CP1、全局allocator/TSAN、公平、原job continuation与BR1-PERF开放，M6/M7/M8正式0/3、persistent默认关闭，不按提交/行数扣人日。

<a id="ledger-control-storage-delivery"></a>
### 16.71 原 Ledger／domain admission 控制与无操作 receipt 收敛（2026-10-03）

产品提交`1d29ff82487bf6b936b1d187ec9816db0fe7c204`，产品父`edd8eb815e99f4b845c659a5f1957d6cfa051c53`、文档父`ac5f667112332aa7c5399c34fe6da4b29f7fd839`，见[Git身份](evidence/br1_ledger_control_storage_20261003/git-round-identity.json)与[同源证据](evidence/br1_ledger_control_storage_20261003/README.md)。接续原Store冷准备／Ledger准入／最后free责任，未读取archive、未push。

原Ledger Private和admission/control现在随Store同一冷allocator实际准备，内部shared→limits配置顺序保持，无第二补费权威或新child协议。Ledger cleanup保存原allocator到实际free；原admission强/弱引用、provider weak登记和transition reservation consumer同批迁移到allocator-backed std shared存储，旧Qt创建与类型删除。真实claim仍在发布domainClaim前准备inactive receipt/control和原ClaimMap节点，失败从原prepare返回并回滚。原detach、claim取消/提交、provider身份/拒绝和保守singleOwner政策、锁序与执行者保持。

无physical record时原receipt只有保活authority和无操作commit职责：现在admission直接实现原reservation接口，返回共享原控制的别名，删除该分支独立Reservation::create及其分配拒绝。实际transition仍在commit后清空原receipt vector，取消沿原vector析构；没有新终结owner。仅给旧无操作receipt补收费的候选会新增预算失败；复用原authority保留实际consumer所需强寿命，避免全局无主singleton或另建结果阶段。真实claim仍有独立receipt，不能泛化为所有prepare均不可失败。

生产七文件**+58/-28净+30**、测试二文件**+171/-2**、ownership**+2/-2**、生成物**+8937/-8275**分列。双架Store冷根实际费**4,520→5,104B，新增584B**＝Ledger Private440B＋admission/control144B；原accounting/child120B不再新增。Ledger Private **424→440B**保存16B allocator，admission **96→104B**新增8B receipt接口；Store/Ledger facade均8B，Store Private4,392B保持。真实claim候选费424B＝claim节点352B＋receipt/control72B，无操作receipt新增存储费0。单独构造测试的Ledger冷费704B含它自己的120B child/accounting，不能叠加到生产同child，测试heap facade及默认standalone仍未qualified。净增属于实际收费与弱尾释放保证，不能记纯去重或峰值/性能收益。

原冷拒绝/重试四行继续覆盖最后admission/control少1B回滚；新增两行验证原无操作receipt在真实父硬满时连续成功，并以strong/receipt保活到最后弱控制释放；新增真实physical claim行验证完整候选少1B连续三次拒绝、source domain/revision保持、同owner重试及取消，再令Ledger/controller退出，仅receipt弱控制在父硬满后free，精确回baseline、原parent弱引用失效。目标最终**14/0/0**；首次11/2/0为新夹具在finalize后注册provider，按原顺序修正。收费无操作receipt的候选双架矩阵7596/0/0保存；最终删除分配后同源双架七组十四进程**7598/0/0、全部exit0**，原压力三对**66/0/0、六exit0**。四次构建均exit0；首冻结在压力runner结束前按六记录完整性拒绝，日志保留，实际退出后冻结通过。93源码/109运行物/四配置绑定产品commit，运行物前后相同；原预算/输入/manager LIMIT_LONG_TESTS=1、stress/benchmark与Matched字节/callback/释放保持。图87TUs/2033APIs/25660edges/24callbacks，21manifest/25ownership/16census/19-file ratchet保持；原签名同批替换，新增私有构造/cleanup及无操作commit有真实consumer，无新增上层API/业务队列。

生产Ledger Private、admission/control、attached真实claim receipt及无操作分配收口，不重领；默认/reference/真正standalone根、statistics等其他Qt heap/control、backend/provider/history/process及observer/Transition根、其他wrapper/登记/link/cache和全部参与者总峰值/永久拒绝/停止/晚handle/自主drain继续CP1。有限样本不关闭24MiB完整总峰值、8MiB完整准入后取消，旧59123/70089/83020仍UE。完整CP0/CP1、全局allocator/TSAN、公平、原job continuation和BR1-PERF开放，M6/M7/M8正式0/3、persistent默认关闭；不按提交/行数扣人日。

<a id="cp1-concentrated-storage-delivery"></a>
### 16.72 CP1 集中存储补齐与原失败／退出责任收敛（2026-10-03）

产品提交`b10b2913a69604d42b51cac83ba81214d30d43de`，产品父`1d29ff82487bf6b936b1d187ec9816db0fe7c204`，文档父`c5a829a958ce85a06461fe60de0eb341a6d3e32a`；源码和运行身份见[证据](evidence/br1_cp1_concentrated_20261003/README.md)。本包按用户要求一次完成下列实现后集中验证，没有读取archive、push或提高原业务预算。

| 原责任 | 本包实际实现及同步回收 |
|---|---|
| provider／Registry／Ledger根与bootstrap | 原冷allocator准备实际facade/Private/control；无预算入口进入同一有界process storage。bootstrap原parent仅在所有存活容量仍适配时接受产品额度，拒绝恢复原额度；observer/Transition/source/receipt与强弱consumer统一迁移，最后control实际free才归费。 |
| TileDataStore observer登记 | 原adoption先准备两种实际登记节点，接受后转交原intrusive记录；像素前拒绝，删除登记后置新分配。原observer资源保活到最后登记析构。 |
| metadata／oracle／format／capture | paid COW数组和byte值承接公开oracle、嵌套format及Transition输入；验证扫描原输入，删除重复集合。原page/activity/link map节点和index vector按实际allocator请求收费，删除估算容器；同Entry的releaseActivity贯穿cancel与clear，修复先pop丢失原publication活动的136B尾容量。 |
| source/read cache／history／backend／extent | 缓存list、准备set、原history/memento及线程map真实收费；匿名lease用原链，clear不复制两份列表。client/跟踪节点/输出容量先于事务或像素接受。extent经通用PMR实际准备两轴，删除eager空数组和Qt行列投影；资源由实际buffer保活。 |
| deferred／runtime固定成本 | 原publication Data直接充当cleanup job，删除独立shared job；statistics/control收费。原executor队列替代Qt pool/runnable；Darwin worker/monitor各512KiB显式stack、native control/TLS region先预留64KiB并在回调前按测量归差额。stop取消原task并join，晚delay handle保留实际control费用至free。 |
| close／永久拒绝 | Ledger转交原backing terminal节点，保留原pending retirement，不复制shutdown handles或建seenReplicas；诊断为常量，计数来自原statistics。拒绝不重放physical动作，同owner释放后接续close。 |
| 竞争复验与归费政策 | 删除固定三次revision变化后的业务拒绝；同Growth复用已准备容量，重新capture/build并复验当前需求，真实不足或身份/取消仍返回原失败。实际free helper统一先检查非空指针，修复空scope cleanup把存活controller费用也退掉的问题。 |

[16组分配合同](evidence/br1_cp1_concentrated_20261003/allocation-contracts.json)列出准备、接受、拒绝、最后free及实际测试；[92个参与者源码的1642处复核位置](evidence/br1_cp1_concentrated_20261003/allocation-sites.json)绑定同候选。位置清单包含别名、容器、准备/释放调用，并非全局运行分配trace或每个表达式都独立故障注入的资格。外部caller Qt导出、既有DataManager/Tile/undo对象、Qt/OS全局及malloc内部容量明确留在原owner边界；Vulkan与BR3 persistence未纳入本CPU构建资格。

本包先集中实现再运行矩阵，最终编译exit0；115个生产/测试/tool源码与4个audit生成/合同文件共119源码身份、113运行物及四配置冻结，原预算、输入、manager LIMIT_LONG_TESTS=1和Matched字节/callback/实际释放保持。双架11组22进程**8082/0/0、全部exit0**，原压力三对**66/0/0、六exit0**，压力前后源码和运行物相同。架构门及六个tool自测通过，图87TUs/2158APIs/27137edges/25callbacks、21manifest/25ownership/16census；外部19-file侵入门未放宽，backend_duplicate_state两项删除、manager引用25→24使ratchet收紧。初冻结把“收紧”误判为必须完全相等，失败日志保留；最终逐字段验证无扩张，未放宽门限。

生产63文件**+2,274/-1,327净+947**，测试14文件**+513/-358净+155**、audit三文件**+30/-17**、生成两文件**+109,825/-92,211**分别记账。新增paid COW/native storage及最后free保证有真实consumer，不能称纯等价去重或性能收益。Store factory子根5,104→5,448B，非整管线合计；Darwin stop原live容量arm64 **1,100,296→2,128B**、x86_64 **1,067,536→2,136B**，晚handle已释放，剩余为fixed anchor，非RSS或完整static退出。原三次竞争拒绝曾使普通freehand像素比较失败；同Growth复用修复后矩阵/压力通过，有限样本不证明永久热点进度界。

全部失败按原链保留：首次stop移动clock后误解引用，CPU进程32658仍UE；第二矩阵还发现clear活动泄漏、实际node收费与测试旧估算不符，以及原worker未结束时ref断言竞争；第三绿矩阵后的压力捕获旧三次竞争导致真实笔画像素差。后续增长夹具64KiB不足令Reference进程48549仍UE，修为256KiB只调整该局部夹具，原业务压力额度不变；精确归费断言进一步暴露空free退掉312B存活controller费，统一free政策后保留原断言通过。第五矩阵在该已知失败后中止，不作最终资格。旧59123/70089/83020等UE进程也未退出，不能用当前28个正常退出记录证明所有尝试drain。

**列明CPU存储实现已补齐；完整CP1仍开放，M6/M7/M8正式0/3、persistent默认关闭。** 下一只补完整参与者逐拒绝点/峰值及永久停止/最终退出资格、全局allocator/TSAN与外部框架/平台边界；已收费对象不再反复领取。持续公平、自动原job接续仍按CP5，正式性能按CP10；不从行数或通过数推算人日。

<a id="cp1-qualification-attempt"></a>
### 16.73 CP1 实际拒绝／并发修复与同源结算尝试（2026-10-03）

沿§16.72的当前代码补真实allocator拒绝，发现并修复三处原责任错误：冷virtual-default snapshot COW的`bad_alloc`逃出execution准备回滚，未执行像素的原history owner因析构失效、同owner无法重试；metadata成功安装后activity scope guard在解锁后访问map，与publication并发删除产生实际TSAN竞态；retirement receiver拒绝在解锁后递增shard统计。现在分别进入原`finishPreparedWrites`失败回滚、在锁内成功安装后dismiss原guard、callback后先relock再处理拒绝。无新业务失败阶段、上层生产API、锁、队列或恢复owner，见[完整证据与八项登记](evidence/br1_cp1_qualification_20261003/README.md)。

原8MiB/swap0取消方法增加实际准入后数据行：原stroke未终结时，3个producer已经执行、2个正常checkpoint像素可见，实际memento/Store session和resident存在；然后取消原笔，cancel已执行/finish零次、无undo、恢复空像素和resident零。queued-input行仍保留。首轮fixture错误等待未结束的自身stroke已取样并实际kill退出；有超时的producer handshake修正后通过。该准入后取消缺口已关闭，不据此推为完整永久拒绝/自动进度资格。

最终双架11组22进程**8086/0/0、全部exit0**，原压力三对**72/0/0、六exit0**；115生产/测试/tool源码、113运行物与四配置同源冻结，所有失败和运行中改源导致freeze拒绝的候选保留。Darwin真实allocator工具有普通malloc12345B数值正控制；连续COW拒绝、1/9/65页实际调用链首末拒绝、像素回调零次、原default保留与同owner重试及commit/purge/close有有限证据。冷Store/订阅/task-runtime两架各16次真实拒绝和3个成功控制。工具从main起测请求heap，故障只注入测试线程能识别的paid调用链；未出现的暖site、所有外部/native/TLS/pre-main、全参与者同时峰值与每笔物理对账仍未取得完整资格。识别子集static后零不能证明全部fixed anchor最终free。

同源TSAN两个受影响并发方法**4/0/0、exit0无报告**，clean/race控制分别正常exit0/66；完整八目标的三组正常通过、五组double-lock实际exit66，**全局仍Inconclusive**。同依赖独立正确Qt mutex/condition控制复现double-lock，证明当前未插桩Qt wait/relock的观测边界；不能自动豁免其他真实竞态。七个旧UE全部取样、核对命令后kill，重启用户ReportCrash服务后仍UE；首轮默认abort的TSAN控制新增87052 UE也保留。新的正常退出不能覆盖这些未drain事实，宿主环境复位和失败退出复验仍欠。

生产两cpp**+43/-29净+14**，测试三文件**+97/-2净+95**；生成物单列。图87TUs/2158APIs/27153edges/25callbacks，21manifest/25ownership/16census和19-file ratchet与父提交完全相同，结构门与六tool自测通过。**本轮交付真实反例修复、8MiB准入后取消和有限同源资格；完整CP1不勾选，M6/M7/M8正式0/3、persistent默认关闭。** 剩余具体端点按证据八项登记：完整allocation/free对账与各阶段实际故障、整管线总硬界、全部anchor/static退出、外部持有存储及非Darwin资格、TSAN和旧失败环境。已关闭入口不重领，不以报告通过数代替这些结清条件。

<a id="cp1-reconciliation-delivery"></a>
### 16.74 CP1 全局探针与实际接续差集（2026-10-03）

产品`1103defd830d463c50f8c6a83dd05cc8077e0bf3`收敛原seal三段provider activity为一次异常安全终结；已安装overlay后仅捕获拒绝保原session，连续三次硬满后同scope恢复不增加sealed/provider准备；关闭诊断不再触碰Darwin TLS，原process fixed新增4B实际presence counter。生产四文件+29/-13、测试两文件+49/-0；新保证和只读atomic成本明确单列，无新业务owner或上层API。见[实际八项结算与全部失败](evidence/br1_cp1_reconciliation_20261003/README.md)。

同源双架22原进程**8088/0/0**、原压力三对**72/0/0**均exit0，115已提交源码/113运行物/四配置绑定；图87TUs/2158APIs/27197edges/25callbacks，21manifest/25ownership/16census与19侵入门不放宽，六工具自测通过。当前92文件1693复核位置加入fixed/TLS，仍不是完整覆盖证明。新逐点隔离矩阵505进程＝18控制＋487首末目标，383成功、**122同owner接续失败正常exit9**；capture/default read/rollback/已接受release留债子集通过，但前期seal取消、partial private publish重放和commit后capability丢失仍须回原记录修复。

原freehand业务从框架初始化后、测试方法前测真实合计heap，两架12/0/0、数值正控制12345B且无overflow；请求heap峰值98,933,679/98,642,358B、节点峰值29,402/27,657，含caller既有Tile/Qt。可识别paid链峰值6,855,482/6,722,034B不是完整owned对账或总硬界。新增实测**PageStore自己持有的QWaitCondition私有heap每个120B未收费**，不能自动排除为caller内部；等待/唤醒与该存储寿命是下一收敛单元。pre-main/框架启动、malloc usable/RSS及非Darwin资格仍欠。

实际cxa析构和最后free已闭合辨认出的Resource48B与Executor624/632B；原stop后固定2132/2140B，parent释放后732/740B，dynamic paid最终0、进程exit0，固定60B保持至进程映射释放。未用已析构账本伪造零费用，也不据此结算全部晚引用。TSAN八目标三组正常、五组Qt wait/relock double-lock实际66，全局仍**Inconclusive**；原两并发方法4/0/0和诊断方法3/0/0无报告，新增capture被double-lock截断。八旧UE仍未drain。**完整CP1不通过、M6/M7/M8正式0/3、persistent默认关闭。**

<a id="cp1-wait-storage-delivery"></a>
### 16.75 CP1 原owner等待容量与TSAN裁决（2026-10-03）

产品`0d3b9f5d87e16e01587acdb03e00985ac07aae80`删除九类owned `QWaitCondition`成员的隐藏120B私有heap，改为原body内嵌native等待存储，实际`sizeof`随原allocator收费，随原owner最后引用析构。原业务谓词/owner gate/close-drain保持；通知gate闭合unlock到sleep窗口，恢复先释放通知gate再取owner。生产13文件+74/-22净+52，测试三文件+14/-7净+7，生成物单列。无新业务owner/阶段/队列或上层API；等待新增native通知gate成本。见[owner/free清点与八项处置](evidence/br1_cp1_wait_storage_20261003/README.md)。

双架最终22原进程**8088/0/0**、原压力三对**72/0/0**均exit0；116已提交源码/113运行物/四配置绑定。87TUs/2160APIs/27231edges/25callbacks，21manifest/25ownership/16census/19侵入门，ratchet不放宽，六工具自测通过。93文件1713复核位置仍非完整覆盖。allocator每架224操作拒绝+17冷拒绝保持；505生命周期进程仍383成功、**122接续失败exit9**：108取消原scope、8重放partial publish、6安装root后retention/capability丢失，未用新绿表覆盖。

Darwin native原六方法两架12/0/0、malloc12345B live/free正控制、overflow0；owned wait pimpl消失。合计requested heap峰值98,932,537/98,918,738B、节点28,630/29,643，paid识别子集峰值6,803,114/6,896,146B；不是完整owned逐笔硬界资格。实际static paid尾0，固定stop2132/2140B及静态60B保持。caller既有容量不重复计费，其他Qt/OS/TLS/malloc和非Darwin仍欠。

TSAN越过旧wait/relock误报，确认并关闭read测试hook与后台retirement的实际竞态；CPU fixture故障开关改atomic消除对未插桩semaphore同步证据的依赖。当前七目标**2892/0/0**无报告。DataManager报告双方均持原migration读写gate；独立标准shared_mutex控制0、Qt QReadWriteLock完整保护及semaphore handoff各race66，clean/race正控制0/66；无广泛suppression，完整TSAN仍**Inconclusive**。原登记八旧UE未drain，全进程复查另发现早期pressure进程91827（10月2日晚开始），SIGKILL仍UE，当前至少九个退出欠账，需宿主处置后默认失败退出复验。本轮新进程均真实退出。两个fixture修复前后的生产image和工具输入closure不变，冻结文件明确记录该差异；未改写原失败身份。

增补91827的实际sample定位原资源初始化`getInstallationPrefix → fatal → abort → pthread_kill/Rosetta`，尚未进入压力方法；当前新压力通过不覆盖这个旧失败出口，宿主不响应kill原因未彻底裁决。

直接下一责任是前移commit after-root retention，随后收敛原seal部分准备与同owner重试；接受事实留原metadata/proof/history，不重放provider、不按错误新增旁路恢复模型。**完整CP1不通过，M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-commit-retention-delivery"></a>
### 16.76 CP1 commit retention 原子准入与失败保留（2026-10-03）

产品`f6fb240a2648140b704a414acdafb4d76c557d00`将原after-root retention的registry node和structural snapshot输出前移至原`PreparedCommit`；未接受时不增加可见root/token，epoch gate内接受root并转移已准备存储。原history record在拒绝时保留；删除publication后置`retainSnapshot`、memento已安装后失败返回、`orphanedAfter`字段及其cleanup。生产五文件+73/-42净+31，测试两文件+61/-12净+49，生成JSON单列；候选新增字段/容量按原allocator实际sizeof收费，非性能/峰值减少资格。无新公共生产API、owner、恢复队列或锁，私有description helper由正常retention与候选共用。见[八项结算与全部失败](evidence/br1_cp1_commit_retention_20261003/README.md)。

最终双架22进程**8100/0/0**、原压力三对**72/0/0**均exit0；候选不可见、single-use、原token/root保护、重验拒绝、move assignment及foreign owner/晚candidate目标14通过。116已提交源码/113运行物/四配置绑定；87TUs/2161APIs/27260edges/25callbacks，原21manifest/25ownership/16census/19侵入门与ratchet保持，六自测通过。93文件1715词法位置仍非完整覆盖。

真实生命周期最终**505进程 = 18 controls + 487首末拒绝目标，389成功、116接续失败exit9**；原六个已安装后retention失败关闭，拒绝保原root/像素、reservation归还、原capability重试，不重放body/安装。仍有108 seal取消和8 partial private publish重放，未用绿矩阵覆盖。初轮fixture及source变更导致的冻结失败均保留；各旧probe与最终生产image/实际inputs未变，无关fixture差异单列。

native两架原六方法12/0/0，malloc12345B live/free正控制、overflow0；total requested峰值98,736,045/99,071,472B，paid识别子集6,576,538/6,952,186B，节点27,621/27,018。main后paid672/680B、static后0；不是完整owned逐笔对账/硬界或全部平台退出。七TSAN目标**2898/0/0**无报告；最新DataManager仍Qt extent读写锁边界race66，同Qt独立控制沿§16.75，整体**Inconclusive**。

原完整矩阵中的新PID88291在history clear fixture解引用空backend，超时kill后仍UE；sample和失败身份保留。fixture现先drain原terminal cleanup再恢复压力配置，并断言backend准入；六个独立复验60通过，最终完整双架通过。首次构造拒绝原因未直接取得，cleanup/policy时序为代码支持的解释；宿主不退出未裁决。原九UE加本批一例，当前**至少十个未drain**；不得以新绿表结清旧/本批失败出口。

直接下一责任是原seal部分准备、frozen input与同owner重试；接受事实留原metadata/proof/history，不重放物理动作。完整清点/总硬界、联合永久拒绝恢复、其他尾容量/外部及nonDarwin仍欠。**完整CP1不通过，M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-seal-retry-delivery"></a>
### 16.77 CP1 原seal冻结输入与拒绝接续（2026-10-03）

产品`71c8b27e08517408102ee03a367338543f3a1225`让原session在seal准备期冻结输入，真实storage拒绝保留原claim/page/proof，原metadata接受事实阻止重放private publish，原proof保留到overlay install接受才转移。删除prepare时提前清空proof、候选cancel撤销借用proof及resource拒绝取消原scope；单次generic lease caller同批迁移。语义/provider validation拒绝仍取消本segment，保留前次接受结果；checkpoint成功恢复原Active。无新owner/恢复队列/锁/上层API，原state增加Sealing值，原publication失败bool改同字节typed枚举。生产九文件+114/-58净+56，测试一文件+73/-0，生成JSON+10047/-9503单列；这是保证增量，未授性能或完整alias拒绝资格。见[八项结算与原失败](evidence/br1_cp1_seal_retry_20261003/README.md)。

最终双架22原进程**8108/0/0**、原压力三对**72/0/0**均exit0；连续硬满及语义拒绝目标13通过，四种seal/checkpoint×retry/cancel各三次拒绝后原输入冻结且可恢复。116已提交源码/113运行物/四配置绑定。87TUs/2162APIs/27317edges/25callbacks，原21manifest/25ownership/16census/19侵入门、ratchet保持，六自测通过；93文件1715词法位置非完整覆盖。

最终生命周期**505进程＝18 controls＋487实际首末拒绝目标全部exit0**；原108 seal取消及8partial publish重放缺口关闭。456拒绝后原owner重试、31后续清理拒绝保已接受结果，无exception、reservation均0、旧captured像素和body一次保持。operation每架224实拒/3controls，另一个1248B父reservation首次增长被discovery消费；冷进程每架ordinal0–42共43实拒、43为control，补同owner原窗口（ordinal11，+632/+772），合计88进程86实拒/2controls全exit0。cold root/subscription/runtime每架17实拒/3controls保持。中间二进制首轮505通过不混为最终资格；fixture编译错误、operation300秒超时kill且已reap、native旧表overflow资格拒绝均完整保留。

native最终两架原六方法12/0/0，malloc12345B live/free正控制、overflow0；总requested峰值98,702,277/98,732,438B，paid识别子集6,609,338/6,728,562B、峰值节点26,762/28,728，main paid672/680B、static paid0。caller既有容量包含在总heap，不重复收费；这仍非所有owned逐笔ledger或同时硬界，fixed stop2132/2140B及其他外部/platform边界保留。七TSAN目标**2902/0/0**无报告；DataManager原Qt extent读写锁边界race66，独立Qt/标准同步控制沿§16.75，整体**Inconclusive**。十旧UE仍未drain，本批新进程已reap，不能覆盖旧默认失败出口。

直接下一责任是联合永久拒绝及容量/保护释放后的无新输入内部清理：原orphan mutation链仅abort/close推进，现fixture显式process/abort不证明自主恢复；沿原责任核验接续。完整allocation/free、alias/provider所有拒绝族、整体owned硬界、全部尾handle/外部/nonDarwin、TSAN和旧UE仍欠。**完整CP1不通过，M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-orphan-progress-delivery"></a>
### 16.78 CP1 原 orphan scope 自主取消与真实绘画失败裁决（2026-10-03）

产品`35dc0c4574bb1f2a4283ea6e0de5149333a21789`将原 orphan mutation 链接入现有 semantic collector 的冷准备 task/delay：owner gate 内查询原链，锁外沿原`retryOrphans → cancelLocked`推进；未完成页/proof/claim和费用仍留原scope，接受取消才实际destroy。显式abort/close与后台复用原终结，原后台许可、close冻结与stop latch保持。没有新owner、恢复队列、持久阶段、task/timer或上层生产API；两个内部callback指针16B按原Private实际sizeof收费。生产三文件+46/-7净+39，测试一文件+89/-0，两个生成JSON+8503/-7928单列；是无输入进度保证增量，非纯去重或性能收益。见[八项登记及所有失败](evidence/br1_cp1_orphan_progress_20261003/README.md)。

原反例两种实际拒绝解除后仍留3/4页、进程正常exit2，现每架16新增行（四bpp×active/frozen scope×provider/arena）在解除拒绝后只观察stats/usage和等待即可归零，原Debt硬限一页不放宽；四页cancel、物理退休恰接受四次、claim/proof/debt/reservation归零，旧capture/current仍0x31。原caller transaction在观察后才显式abort，本保证不等于全部transaction自动终结或facade先退出的全联合恢复。最终三方法目标每架26/0/0，实际exit0。

同源原11组22行矩阵实际为**8139/1/0**：x86 MatchedFreehand projection/layer摘要失败且有`legacy mutation conflicts with an active page writer`，正常exit1；失败停止派发后，仅补未运行五目标，原失败行不替换。十次同源短复验30/0/0不能关闭它。隔离父版本机械提取父提交两owner TU/private header、复用373未改image对象，实际DYLD加载路径/哈希核验；24个x86配对进程中父一例、候选两例同claim/像素失败、均exit1已reap。**该缺陷在本批前已存在，仍未修复；当前矩阵不全绿。** 正控制loader最初失败、fixture编译/配置错误和native路径错误均保留。

原压力三对**72/0/0**、六exit0；505生命周期进程＝18controls＋487首末实拒全部exit0，456接受前拒绝同owner重试、31接受后清理拒绝保结果。operation每架224实拒/3controls、暖父增长缺席1；88冷首次operation进程86实拒/2controls，ordinal11真实父数组增长保持；cold root/订阅/runtime每架17实拒/3controls。116已提交源码/113运行物/四配置绑定；87TUs/2164APIs/27370edges/27callbacks、21manifest/25ownership/16census/19侵入门，ratchet未放宽、六自测通过。93文件1715词法复核位置非完整分配覆盖。

native原六方法每架12/0/0、malloc12345B live/free正控制、overflow0；requested heap峰值arm64 **98,779,037B**、x86_64 **150,965,290B**，paid识别子集峰值 **6,751,530/7,034,114B**、节点峰值 **28,699/30,307**。x86请求峰值增加照录，未判定原因，也不是owned硬界资格；caller既有Qt/Tile包含其中，不能重复计费。main paid672/680B、static paid0，fixed stop2132/2140B及60B静态寿命边界保持。七TSAN目标**2918/0/0**无报告，DataManager原Qt extent读写锁边界仍race66，整体**Inconclusive**。十旧UE复查仍未drain，本轮新进程已退出，未杀app-server或重启宿主。

直接下一责任是普通绘画原legacy writer/adapter准入及失败交接：固定真实并发claim冲突，保持原4worker、输入、像素摘要和预算，不能等待持有自身tile/manager gate或丢掉已接纳像素。随后继续完整allocation/free逐笔对账、所有alias/provider/node/control/task/线程实拒、整管线owned同时硬界、联合read/capture/history/close及晚handle/static/外部/nonDarwin；TSAN与旧失败退出缺口保留。**完整CP1不通过，M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-legacy-admission-delivery"></a>
### 16.79 CP1 原 clear 全范围准入与实际 claim 增长竞争（2026-10-03）

产品 `0da7ba0889` 关闭两条已定位的普通绘画 writer 准入反例。原 image 诊断副本的实际 Matched 栈固定 `reserveLegacyMutationPage → acquireTile → fillRect → DataManager.clear → setupProjection → updatejob`。原 clear 现于 capture/pixel 前以付费 target 数组取得完整 range，原 batch 持有 claim 到 adapter install；manager clear、packed、cursor 共用已有 `PreparedTileUpdates::install`，原 gate 内 publication/presence/index/extent 一致，三处重复安装/诊断/解锁删除。另一个中间 Matched 像素失败由真实 paid malloc 增长窗口固定：A 准备 claim table 时 B 接受原 delivery，A 尚未执行 body 就误报失败。私有 `claimAll` 返回临时 Acquired/Contended/Failed；原 managed range 对竞争复验并等待既有 condition，真实 storage 拒绝仍返回，generic/native terminal conflict 保持。没有新 owner/队列/锁/持久失败状态或上层生产 API；完整 receipt 懒准备并原位复用。生产六文件 +105/-59 净 +46 为保证增量，测试三文件 +126/-25，两个生成 JSON +2872/-2495 单列。见[八项结算及全部失败](evidence/br1_cp1_legacy_claim_20261003/README.md)。

新增 range 32 行覆盖四 bpp、partial/full、default-remove/nondefault-alias、history/anonymous；foreign 原 delivery 等待时独立页执行，原 claim 到 adapter install、旧 capture/current 和 history undo/redo 保持。fresh fixture 增加 clear 16 行。实际增长探针两架均等待、A/B body 各一次、成功、current 0x71 / capture 0x31、claim 0。最后 40 个原 Matched 进程 120/0/0、无原两种 warning。最终同源 22 行矩阵 **8236/0/0**、原压力三对 **72/0/0**；中间 Matched actual exit1/摘要失败和 matrix-02 cleanup 断言失败均保留。最终 cleanup fixture 只观察真实 RootPublication 后的接受清理，仍要求一次发布/一次接受 cleanup 及 reader 当场完成，并未放宽为非零次数。

clear bpp1/九页四模式 **718 进程＝8 controls＋702 首末真实分配拒绝＋8 同 history owner 三次连续拒绝后恢复进程**，另24次连续拒绝，全部 exit0、claim/reservation0、原 current/capture 保持；接受后 cleanup 拒绝不重放 clear。其他 bpp 的行为行不替代其逐点实际 fault 资格。116 源码/113 运行物/四配置冻结，最后仅 DataManager fixture 边界修正的旧 clear/native/growth/Matched/pressure 证据保留自身身份并明列差异，生产 image/header/其他输入相同；完整最终矩阵及 TSAN 使用最终源码。87TUs/2164APIs/27412edges/27callbacks，21manifest/25ownership/16census/19intrusion、六工具自测通过；ratchet 未放宽。93文件1718词法位置仍不是全分配覆盖。

native 六原方法每架12/0/0、malloc12345B live/free正控制、overflow0；requested heap peak **100,224,689/99,140,058B**，paid识别子集 peak **6,682,866/7,093,802B**、节点 peak **48,505/30,823**，main paid672/680B、static paid0。节点上升照录；它们含 caller/Qt/Tile，不能替代owned账本总峰值/硬界。新失败独立保留：原probe在facade/capture存活时 permanent stop，随后 destructor 在 HistoryCollector idle 死等，sample显示worker已退出且晚job插入停止队列；只TERM自有probe50484，实际-15已reap，后续先关owner再stop仅隔离增长断言，没有修复生产退出。tsan-02 DataManager在TileSwapper `forgetTileData → freeTileData → pass`实际SEGV/66已reap，不能归为Qt误报；普通map ref从零复活final-free对象的风险已识别，确定性复现/修复未完成。最终TSAN报告及原Qt边界Inconclusive如实绑定；十旧UE仍未drain，未处置app-server/宿主。

最终tsan-03六目标 **1564/0/0** 无报告；CPU **1353/1/0**、`proof-rejected-after-publish` 在解除拒绝、process/idle后abort仍失败，actual exit1；DataManager报TileSwapper读age对main `blockSwapping → resetAge`实际竞态，actual exit66。二者均已reap、尚待独立复现和修复，不能沿用前轮七组通过或将新竞态/SEGV一并标成Qt边界误报。最新TSAN资格未取得；原Qt extent非插桩边界仍Inconclusive，无suppression。

直接下一责任是 permanent stop 拒绝后的原pin/activity回收及最后引用物理free，和上述TileSwapper崩溃/age竞态及CPU abort失败裁决；不能向已退出worker晚排job、创建新callback或提前退费。全部实际allocation/free、其他fault族、整管线owned硬界、联合永久拒绝恢复、全部晚handle/static、外部/nonDarwin仍欠。**完整CP1不通过，M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-terminal-convergence-delivery"></a>
### 16.80 CP1 永久停止接受、原尾释放及并发残留集中收口（2026-10-03）

产品`406bacb448997a2b63bf2d452a0a71d90587abdd`；本轮起点为产品`0da7ba08899344496b3528e60cb98696f5007f07`、文档`07650746`，包含工作区已有TileData候选；原增量、最终产品提交和全部中间失败绑定[本轮证据](evidence/br1_cp1_terminal_convergence_20261003/README.md)。收口单位为原executor接受事实到最后物理free，所有生产consumer同批迁移，不新增恢复owner/queue/lock/callback或上层PageStore API。

原private enqueue由void改bool，在原gate拒绝永久stop后的新producer，已接受worker continuation继续排空。history/read/retirement/waiter拒绝时撤回本次scheduled/pin/activity，原业务记录保留；retirement idle与原notification gate共读已接受计数。Store final releaser先取出原terminal node再转交，拒绝则原destroy；tree沿原非递归list，publication Data沿原clearBatch完成同步尾释放，删除晚排至退出worker和无实际接受的ghost计数。正常tree每pass仍128节点；停止后caller可能遍历完整树，不能作为交互线程有界销毁。新增真实foreground统计8B，四个静态统计实际32B纳入原固定费用，其中原24B补齐收费。

TileSwapper及debugSwapAll在iterator barrier内使用只增加正计数的tryRef，零计数仍属于原final free；原age标量改atomic。独立TSAN又固定pooler testingRereadConfig与worker读limit的真实竞态，原body改atomic读写，不改变限额政策。PhysicalClaim四bpp确定性固定最后ref窗口；CPU原最后stop方法覆盖四bpp×facade保留/先退出、晚capture/read、provider三次拒绝/解除及父账本回到准备前基线。proof-rejected-after-publish原abort失败实际为Debt仍16384B占用原one-page硬预算；fixture改观察真实Debt释放后再abort，生产拒绝和硬限保持。该诊断及错误fixture假设、注释编辑使旧hash不成立、mixed native表overflow等失败全部保留。

本批累计生产15文件+143/-67净+76、测试两文件+106/-0，生成两JSON+5773/-5360单列；起点已有生产+19/-7及测试+40/-0，不能全称新增独立实现。最终123源码输入/245运行物（含配置）核对提交blob；双架22进程完整矩阵 **8244/0/0**、原压力三对 **72/0/0**、七PageStore TSAN **2922/0/0**，全部actual exit0；pooler预算方法十TSAN进程 **60/0/0**，正反控制clean0/race66。原manager TSAN已越过Swapper故障点，最终在现行Qt extent锁观测边界actual66、已reap、仍Inconclusive，无suppression；十旧UE实际仍在，未处置app-server/宿主。native六原方法每架12/0/0，malloc12345B live/free正控制、overflow0，requested heap峰值98,667,099/98,771,600B、paid栈识别子集峰值6,552,674/6,774,834B、节点peak27,193/28,865，main paid672/680B、static paid0；它们不是全部owned账本或总硬界证明。

**完整CP1仍未通过；剩余只领取四组：** ①全部owned实际request/capacity/control/native/TLS/static、reserved/live/peak到physical free的逐笔账本及总硬界；②尚未覆盖的alias/provider registration/node/control/task/冷线程真实拒绝，与read/capture/history/publication/retirement/close联合阻塞、晚fence及caller transaction终结；③Qt/OS/usable/TLS和非Darwin平台证据；④Qt TSAN边界及十旧UE宿主退出/默认失败复验。已验证的停止后八种组合不重领，也不外推完整联合退出。持续公平和原job接续归CP5，正式性能归CP10。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-owned-qualification-delivery"></a>
### 16.81 CP1 arena实际请求、有限拒绝及可观测Qt依赖续验（2026-10-04）

产品 `d7e91efc39d965be49c748859fd384f91cda2c64`；产品父 `406bacb448997a2b63bf2d452a0a71d90587abdd`、文档父 `bf69fa0b654aef269e53f9b09aebde65f7391009`。从干净产品父版本领取实际owned计费及拒绝/依赖资格差集，全部身份、成功与失败绑定[本轮证据](evidence/br1_cp1_owned_qualification_20261003/README.md)。原arena的BlockBytes保持slot几何，blockByteSize改sizeof(Block)，原capacity/attach/live/detached/free和Growth reservation共用实际单位16328/32696/16352B，真实malloc/少1B拒绝/最后free独立验证。生产一文件+11/-9、测试一文件+6/-2，无新owner/API/字段/锁/队列。

真实分配分类补齐直接metadata block/default payload；两架四bpp的controller先退出、私有写/发布/旧reader、facade先退出/最后free及cold/stop共34静止端点，heap与原process费用对账成立。该式不是独立native精确总额证明：arm64两个线程实际各16KiB，原mach_vm_region合并后累计收费48KiB，多收16KiB。独立四线程探针的recurse/object ID也已合并，不能换API或以opaque sizeof猜测解决；下一沿原ReclamationThread收敛。x86本次每线程8KiB无同差额，不外推全部地址布局。

最终审计器两架provider登记/source/alias共64实拒/24控制，operation/COW每架234实拒/3控制/1 absent，九族lifecycle共515进程497实拒/18控制，原worker/monitor连续pthread_create EAGAIN共12拒绝/4控制，全部actual0。只覆盖记录的有限第一/最后真实调用点；read/purge/close本次malloc目标为零，不记拒绝通过；audit abort handler不算默认失败出口。已接受publication保留结果，未接受候选沿原owner重试，源码输入快照和所有错误fixture/早轮失败保留。

匹配现行Qt6.8/c3cc的隔离QtCore插桩库正反控制clean0/race66；完整21864 source在首次构建/控制后冻结，no-op及最终源码/库核验保持，无suppression，产品dyld确认实际加载。最终七PageStore TSAN **2922/0/0、七actual0**，越过原extent锁观测反例。完整manager同body/48任务/16线程/100000 cycles仍未结束：早轮300s外超时actual-9已reap；单函数watchdog/QFATAL在1098通过后新增UE23256；后续放大观察窗口，在1302.4s诊断截止于watchdog前终止，actual-9已reap、完整仍Inconclusive。早轮plugins路径遗漏新增UE16996；十旧加两新实际仍UE，未杀宿主/app-server或重启，不将未退出进程算通过。

普通最终双架22进程 **8244/0/0**、原压力三对 **72/0/0**、原六freehand方法每架 **12/0/0**全部actual0；expanded paid peak13448338/13151954B是跨方法/政策子集，不代表全owned硬界。生成两JSON+4416/-4326；图87TUs/2164APIs/27464edges/27callbacks、原ratchet未放宽。最终123源输入合并，其中121编译输入匹配测试/产品blob；两派生JSON在测试后刷新，旧hash保留。复用普通runner原116输入与Qt/native/probe完整123输入分列，不伪造统一预采集范围。

**完整CP1仍未通过，下一只领取四组差集：** ①原native合并重收费及所有owned request/capacity/control/TLS/static、reserved/live/并存peak/physical free的独立逐笔账本与总硬界；②有限sweep之外的真实node/control/task，read/capture/history/publication/retirement/close联合永久拒绝、晚fence和caller transaction终结；③Qt/OS/usable/TLS外部容量及非Darwin运行证据；④完整可观测manager TSAN终点与十二UE宿主/默认失败退出。已交付arena、有限拒绝和停止后八组合不重领；CP5 continuation/fairness、CP10正式性能仍归原包。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-native-span-delivery"></a>
### 16.82 CP1 原worker/monitor合并容量去重（2026-10-04）

产品 `46eab867ed37da42921c5618cc349171454fe5c7`；产品父 `d7e91efc39d965be49c748859fd384f91cda2c64`、文档父 `d1fd1095fd0902a8a2e7abfc1ccf7301aa26f09d`。[本轮证据](evidence/br1_cp1_native_span_20261004/README.md)关闭§16.81真实反例：原ReclamationThread保存查询span，monitor在原gate扣除原worker已付交集，只给唯一容量归费，原64KiB未付容量上限保持。worker先接受/ready且最后join，monitor借用期间该交集持续收费；失败仍原catch/join、无回调接受，正常归费只在对应join后。没有新owner/队列/锁/公共PageStore API或生产debug hook。

生产原CPP +26/-5净+21，两个span字段每实例16B，使原executor actual malloc +32B并随原allocator收费，测试修改0；生成两JSON+131/-129单列。两架各34静止端点native差额全部0，arm64两控制区真实/收费32KiB，旧48KiB消失，x86仍16KiB；原join地址实际unmapped且stop后native请求/费用同为0，固定executor仍保留至实际析构。worker/monitor连续EAGAIN共12拒绝/4控制actual0；双架原CPU/Reference完整body四进程 **4288/0/0**，匹配插桩QtCore原目标两进程 **12/0/0**，全部actual0。图87TUs/2164APIs/27464edges/27callbacks、原ratchet保持；123源输入/161运行及审计输入核对产品blob，派生JSON测试后刷新单列，不借旧完整矩阵资格。

**完整CP1仍不通过，四组差集继续：** ①初次native查询可能合并外部容量，及全部owned request/capacity/control/TLS/static、reserved/live/并存peak/physical free与总硬界；②有限fault之外的原node/control/task，以及read/capture/history/publication/retirement/close联合永久拒绝、晚fence、caller transaction/最后facade和handle终结；③Qt/OS/usable/TLS与非Darwin运行资格；④完整可观测manager TSAN和十二UE宿主/默认失败出口。原两线程重费和此前arena/有限fault/停止后八组合不重领。**M6/M7/M8正式0/3，persistent默认关闭；CP5 continuation/fairness和CP10正式性能归原包。**

<a id="cp1-orphan-terminal-delivery"></a>
### 16.83 CP1 orphan scope最后façade/handle退出与原单transition接受边界（2026-10-04）

产品 `61a0e28bdd1d8d6ac56f471550eb3f0e1db42b4b`，产品父 `46eab867ed37da42921c5618cc349171454fe5c7`、文档父 `159fca58`。[证据及全部失败](evidence/br1_cp1_orphan_terminal_20261004/README.md)关闭两个真实反例：遗弃scope在façade停止重试后通过自保pin保留278,500B/parent refs2；后台单transition临时export array在process硬满下于原接受边界之前抛bad_alloc。

原Private在owner gate保存façade消失事实，原scope链和最后scope/后台retry沿原scope→owner锁序释放声明，exposed guard/execution仍保护字节；活façade拒绝/自动恢复和正常晚guard退休保持。外部provider仍实际拥有未退休物理分配，不将声明释放伪报物理退休。单值和序列借用const输入/count，共用原project/install/拒绝，删除单值临时数组control/payload分配，没有新增owner/queue/lock/公共API。生产3文件+51/-23净+28、测试+120/-2、生成+8633/-8055；新增bool填原padding，两架Private实际请求仍4960B。scope最终同步释放成本不记纯去重或性能收益。

最终双架CPU/Reference完整body四进程 **4352/0/0**；同源插桩Qt前五完整body加Reference/CPU两补测共 **2954/0/0**，七actual0、实际Core加载、无suppression。Reference180秒cutoff实际-9/reaped保留，按旧同Core约234秒记录补测outer290、function watchdog300，actual219.8秒/0，不写一次runner全通过。新32行覆盖四bpp、provider/metadata永久拒绝、active/frozen、原orphan/晚scope；原stop另补四bpp orphan＋晚scope/reader＋双预算满额＋永久拒绝/stop及原close控制。双架独立实际free/parent暖高水位/refs1/reserved0/static paid0成立；123源/121编译/169运行及审计身份匹配产品blob，派生JSON测试后更新。图87TUs/2164APIs/27528edges/27callbacks、原ratchet保持。

**完整CP1仍不通过：** ①全owned实际容量、并存peak/physical free与总硬界、初次native外部合并；②其余真实fault和read/capture/history/publication/retirement/close、晚fence/caller联合终点，不能以本轮scope组合外推；③Qt/OS/usable/TLS和非Darwin；④完整可观测manager TSAN与宿主/default失败退出。ordinary02默认abort新增UE61801，累计十三UE；最终测试无新增UE，全部诊断/超时/身份失败保留，未清理宿主。原arena、两线程重费、此次scope自保环和单transition临时数组不重领。**M6/M7/M8正式0/3，persistent默认关闭；CP5/CP10归原包。**

<a id="cp1-finite-default-qualification"></a>
### 16.84 CP1 有限并存容量与已处理真实拒绝的默认退出续验（2026-10-04）

产品保持 `61a0e28bdd1d8d6ac56f471550eb3f0e1db42b4b`，文档父 `579fd72f`；生产、产品测试和派生JSON增删均0。[本轮结算及全部失败](evidence/br1_cp1_final_qualification_20261004/README.md)只补当前源码资格，没有新增owner/queue/lock/API/恢复阶段。

原Freehand两个完整body在两架共 **14/0/0、四actual0**。8MiB取消的已识别paid请求＋实际native请求＋启动前固定费92B并存观察峰值为 **8,025,662/8,009,390B**，24MiB压力为 **13,290,222/13,300,270B**，均无观察界越界。每次独立12,345B正控制在审计界93B观察到12,437B/一次越界后复位；产品政策未放宽。两线程实际join原地址unmapped，native归零、static后classified paid0/overflow0。框架初始化完整，fixed92B仍取自产品启动前计数，Qt/OS/usable/TLS及未归类容量不在此式，不能授予全owned独立总硬界。

原provider64实拒/24控制、operation468实拒/6控制/2 absent、worker/monitor EAGAIN12实拒/4控制均在默认终止行为下actual0。lifecycle先保留带审计处理器的515进程，再仅删除terminate/SIGABRT替换，按原九族/原body/原发现点重跑 **515 actual0、497实拒/18控制**。默认矩阵合计 **1041已处理实拒/52控制**，加容量共primary527 actual0；read/purge/close无malloc目标仍只记控制。该资格只代表这些拒绝被处理后正常退出，不证明默认abort或历史UE已退出。captured release沿原Store metadata/history/epoch/close路径复核未建立新反例，不据潜在收益扩张产品。123源与产品blob核对、前轮169依赖哈希保持及本轮运行/审计输入绑定；图/ratchet保持。

完整可观测manager原48任务/16线程/100000 cycles/seed12345仍在同次执行，outer7200s、函数watchdog10800000ms；插桩Core实际加载、无suppression。不可变观察点只有1098 passing prefix、无Totals，当前 **Pending**，不写完整通过或死锁。十三历史UE仍实际存在，未清理宿主；两次未到body的字体审计停止actual-15/reaped，全部身份/源码快照保留。

**完整CP1四组仍开放：** ①全owned独立request/capacity/control/TLS/static、reserved/live/并存peak到physical free与总硬界、首次native外部span；②有限矩阵外真实node/control/task及read/capture/history/publication/retirement/close、晚fence/caller联合终点；③Qt/OS/usable/TLS和非Darwin实际资格；④完整manager实际终点与十三UE/宿主默认abort退出。上述有限handled-refusal默认退出和两个body的容量观察不重领。**M6/M7/M8正式0/3，persistent默认关闭；CP5/CP10保持原包。**

<a id="cp1-static-root-extent-delivery"></a>
### 16.85 CP1 命名固定根计费与原extent读取竞态收敛（2026-10-04）

产品 `7804582f93bb1eb841b7520728169f0e228b046c`，产品父 `61a0e28bdd1d8d6ac56f471550eb3f0e1db42b4b`、文档父 `4d913ae24d98b11967f1bd44762b4a8a0ccb06dd`。[本轮证据](evidence/br1_cp1_static_root_20261004/README.md)补两个实际缺口：独立编译产物清点发现原固定费92B遗漏identity/handle/guard；§16.84完整manager最终实际退出66，竞态在原Data::remove写入与未加锁min读取，失败后123源码/61运行输入未变、进程已回收，不再以Pending解释该旧运行。

原process两个gate使用内嵌std::mutex，锁序及消费者保持；固定费补齐九identity、worker identity、Resource/executor handle和三个实际guard。capability改为返回相同inline值，删除原静态值及guard。原命名固定存储实际arm64/x86_64为220/292B，候选和主树均332B，冷启动运行计数也332B；费用新增240B，物理存储新增112/40B单列。原三个extent getter使用已有读gate，原updateExtent已持gate的consumer直接读同一字段，避免递归获取。没有新锁/owner/队列/公共API。生产五文件+50/-15、产品测试修改0、派生两JSON+1159/-1067；两个私有constexpr函数仅用于固定费及ABI guard类型推导，旧常量删除，保证成本不算去重或性能收益。

隔离候选和当前主树双架各8进程4414/0/0、全部actual0且实际加载各自库；前两轮未加载候选的actual0保持Inconclusive。原extent TSAN 3/0/0、actual0；七个完整PageStore TSAN body同次2954/0/0、七actual0，匹配插桩QtCore实际加载且无suppression。原worker/monitor双架12实拒/4恢复、四actual0，拒绝后计数回到准备前基线，static后paid0/overflow0。图87TUs/2166APIs/27531edges/27callbacks，21manifest/25ownership/16census/19-file原ratchet保持。123输入分为120个C++源/头、1个审计Python、2个派生JSON；121非派生输入不能全部称编译源码，早期标签修正保留且所有hash未变。最终123输入匹配产品blob、174运行/审计输入复核。

原两个Freehand完整body双架14/0/0、四actual0；E8识别paid请求＋实际native请求＋独立命名固定费332B，8MiB取消并存观察峰值arm64/x86_64为7,960,366/8,031,374B，24MiB压力为13,269,222/13,072,630B，均无观察越界。12,345B正控制在333B观察界得到12,677B/一次越界后复位；join实际地址unmapped、native及static后paid归零。x86_64首次因与arm64共享资源DB，在原body之前SQLite busy等待，诊断-15/reaped及采样保留，最终顺序复验通过；框架初始化完整。未归类/Qt/OS/usable/TLS及全owned总硬界仍不授资格。新完整manager按原48tasks/16threads/100000cycles/seed12345继续单次运行，实际终点前保持Pending。

**完整CP1仍不通过，剩余只取四组差集：** ①全owned实际容量/并存peak/physical free与独立总硬界、初次native外部合并；②其余真实fault和read/capture/history/publication/retirement/close、晚fence/caller联合终点；③Qt/OS/usable/TLS及非Darwin实际资格；④修复后同次完整manager阳性实际终点与十三UE/宿主default abort退出。该命名固定根和已修复extent竞态不重领，旧有限族不外推。**M6/M7/M8正式0/3、persistent默认关闭；CP5/CP10归原包。**

<a id="cp1-unclassified-storage-observation"></a>
### 16.86 CP1 未归类容量观察与调用内工作区候选（2026-10-04）

主树仍为 `7804582f93bb1eb841b7520728169f0e228b046c`，隔离候选 `38451ac4f16272c64a13c26770ebc384b0abacdd`、父780，文档父 `9b504fd8c630267aae52575b3e66c24e4b5170ce`。[本轮记录](evidence/br1_cp1_unclassified_owned_20261004/README.md)扩大原heap观察到未归类调用链及实际malloc usable，原完整CPU body发现recoverable handoff调用内Prepared用普通堆，双架均296次/416B且无预算owner。候选沿同一调用栈与原锁外reset改为optional，删除该分配及拒绝来源；无新owner/gate/队列/API。生产候选+3/-1、测试0、派生0；Prepared416B、optional424B两架相同，不称整体容量或性能收益。候选尚未合入，派生图/架构清点待最终候选统一生成。

最终主树/候选双架四个原完整body5544/0/0、四actual0/reaped，实际加载选定库；候选旧Prepared site及296次请求均消失。原handoff/fallback/九类并发消费者三个TSAN方法290/0/0、actual0，实际加载匹配插桩QtCore、无suppression，未用heap interposer。120编译源/头逐一匹配候选commit及已构建源，不把未生成派生图写成架构通过。

前三诊断轮12110溢出全部来自2048个image析构观察槽，堆/native/site/symbol/地址表未溢出；16384槽后实际14158/14190回调全执行、溢出0，无效symbol扩容撤回。早期实际加载`.21.0.0`但runner误判的退出0及溢出日志保留。arm原trace352个未归类site中4个为Prepared、4个32864B为审计器TLS，其余344个仅定位，framework标志不能替代ownership。已识别paid的usable−request同时余量峰值96,463/96,471B，原费按请求字节，完整容量/总硬界不能通过。原全CPU约12.9GB峰值含填满process硬限的filler，不称8MiB freehand越界或RSS。

主树manager同次仍Pending，50:25快照复核121非派生source/audit、61runtime及当前123冻结输入，1098 PASS前缀没有Totals；调用时HEAD61加记录的dirty修复，source对应780，原identity保留。主树输入本轮无改动，十三UE/宿主退出未结清。**完整CP1仍不通过，§16.85四组差集保持；下一源码主责为原reserve/allocate/retained fee/physical free实际容量及arena/slot/direct consumer共同结算，再统一候选合入与派生核验。M6/M7/M8正式0/3、persistent默认关闭。**

<a id="cp1-actual-capacity-delivery"></a>
### 16.87 CP1 原分配责任的实际容量收费及物理释放（2026-10-04）

产品提交 `6ddccc30979ab859060ed5a19b936d5322aaa1cb`、父780，文档父 `7285fe4fc924257409e627c4aadf1fec4d339499`。[本批证据](evidence/br1_cp1_actual_capacity_20261004/README.md)将§16.86调用内optional候选合入，并把process/Mutation/retained owner、reservation slots、arena、readiness、metadata map/index及默认读缓冲统一到原分配责任的完整capacity预留、保活和最后free；不新增owner/gate/队列或上层API。默认缓冲的逻辑read span仍是stride×height，实际capacity另计，3 BPP用例约束12,288B可读范围与16,384B native费用，不把padding暴露为已初始化像素。

中间候选证实`malloc_good_size`不能决定大块复用及memalign的实际费：先释放16MiB再申请16MiB−32KiB，native仍返回16MiB；32-byte alignment的992B计划可返回1,024B。最终Darwin策略让普通小对象使用native size class，小型超对齐对象在普通size class内保留对齐及free事实，超过64KiB的完整raw容量使用预付的按页映射，避免large cache的不可预知余量。原16KiB reclamation task预算、8/24MiB业务预算及全部拒绝边界不放宽。非Darwin fallback尚未取得usable/native容量资格。

最终normal七个原完整body×双架**5,908/0/0**，原8MiB取消和24MiB压力四进程**14/0/0**；匹配插桩QtCore的七个完整TSAN body **2,954/0/0**，21+4个进程均actual0/reaped，无suppression、heap interposer、退出guard、缩减或重启。独立malloc/mmap/munmap观察两架各72次，实际API span/heap usable与收费一致、created/free均72、live及prepayment violations均0、process固定费回到332B；此有限观察不代替OS合并region、RSS或全参与者总硬界。旧库同探针实际3/reaped，保留32KiB少收费反例。原780完整manager的同次Pending另已结算为**1,105/0/0、actual0/reaped、4,221.39s**，原48 tasks/16 threads/100,000 cycles保留；它不授予本次容量源码的完整manager资格。

原主构建产物未覆盖，最终证据使用明确加载的隔离库。normal/TSAN各40个受影响TU完整重编底座之后，仅本CPP再次变化，依赖核对重编1、其余39按哈希复用；测试20 TU底座无后续头/测试变化，重链接原七body。主树Clang图87 TUs/2,172 APIs/27,405 edges/27 callbacks；结构门及六工具自测通过，21 manifest/25 ownership/16 census/19-file ratchet保持，127个源码/头blob匹配提交。生产九文件**+270/−95、净+175**，测试六文件**+360/−206、净+154**，两派生JSON单列；这是容量/释放保证成本，不计整体内存或性能收益。27个失败/诊断轮及所有原日志保留，最新只读检查仍为**20个UE**，未清理宿主。

**本批有限源码交付完成，完整CP1仍开放；下一只取四组差集：** ①其余未归类owned/Qt/control/native/TLS/static、完整reserved/live/并存peak到physical free的独立账本及总硬界，初次native外部合并；②剩余真实node/control/task故障与read/capture/history/publication/retirement/close、晚fence/caller共同终点；③Qt/OS/usable/TLS及非Darwin对应实现和实际运行；④新容量源码的完整manager跨模块资格、20 UE及宿主默认abort出口。原780 manager Pending、调用内Prepared及本次共同容量规则不重领；CP5公平/continuation、CP10正式性能归原包。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-physical-release-reset-delivery"></a>
### 16.88 CP1 VM释放拒绝、语义默认值ownership及实际故障结算（2026-10-04）

产品 `8f84cc8461ca621bc284342dbcdeb6490470b66e`（父6dd）补原VM释放，随后 `3c22a0226a858ef16d150b2dfe5523d9bfbc684e` 关闭语义删除的默认像素副本；文档父 `bd3783367b3b18f6d3710cb634adbb730859649f`。[本批证据](evidence/br1_cp1_physical_fault_20261004/README.md)保留两次源码边界，不将旧运行改标最终源码。§16.87的6dd完整manager现已实际结算：原48 tasks/16 threads/100,000 cycles/seed12345，**1,105/0/0、actual0/reaped、4,193.50s**，匹配插桩QtCore且无TSAN警告。8f完整manager仍在独立冻结库上单次运行。3c的Pending检查点后已取得**actual66/reaped、345.72s、无Totals**：TSAN两访问栈位于KConfigPrivate构造/改文件名，经KisImageConfig和原prepareStore到达；各1,979源码/107运行输入最终复核通过。当前KConfig库未插桩，根因须以同版本依赖同步核验，不将其标成通过或继续Pending，也不凭此提前添加生产锁；后继记录见[配置依赖排查](evidence/br1_cp1_config_tsan_20261004/README.md)。

真实munmap拒绝暴露6dd原free返回0后丢失地址、保留已收费用及映射；双架负例actual3/reaped，保留原地址的诊断探针再清理，不能当生产恢复。8f在同一free入口对相同base/span调用Darwin native deallocate，成功物理解除映射后才归费；双架阳性actual0/reaped，forced mmap ENOMEM及munmap EINVAL均实际命中，native free成功、地址unmapped、费用回332B。两个OS释放均失败时仍fail-fast，这一出口及宿主默认abort未获资格。生产仅原CPP **+12/−3**，无新owner、队列或API。

8f七个原完整normal body双架 **5,908/0/0**、匹配Qt的七个完整TSAN body **2,954/0/0**、原8MiB取消和24MiB压力 **14/0/0**，25进程均actual0/reaped。独立完整CPU body两架各1,386/0/0，已识别paid的同时usable−request余量峰值0，static后paid heap/VM均0、观察表溢出0；约12.9GB paid峰值包含原硬限填充用例，不是8MiB业务峰值或RSS。350/349个未收费PageStore可达site逐个依据实际调用栈和源码定位到TileData/pool、异常/TLS、配置/Qt、原memento、测试回调、调用方输出和临时值；归类只解决owner定位，不授予全局容量硬界。

其中原Mutation::Private::Page::resetPixel仍为QByteArray，从已收费format隐式复制；原完整CPU两架均172次未收费请求。3c将该字段改为KisPageByteArray，共享原不可变付费字节，原clear、读取和最终析构消费不变。生产 **+1/−1**、测试0、无新类型/owner/API；双架完整CPU **2,772/0/0**、匹配Qt TSAN **1,386/0/0**均actual0/reaped，独立两架完整body确认该site消失及paid尾0，其他site的次数变化不计作本次节省。最终127源/头匹配产品blob，图87 TUs/2,172 APIs/27,412 edges/27 callbacks及21 manifest/25 ownership/16 census/19-file ratchet通过；工具未改，不重复工具自测。

九类原生命周期扩大到16 BPP/1,024页以触及真实VM分配，arm64/x86_64分别取得**2,280/2,277次实际拒绝、各9控制、各13次mmap拒绝**，actual0/reaped，耗时661.41/879.53s，static后paid heap/VM0。观察槽不足的首轮诊断-15/reaped，扩到明确有界的16,384 site后两架各表溢出0；不把诊断轮当通过。该范围仅调用线程已观察site的首/末出现，未授予其他线程、全部晚fence/caller或双OS释放失败资格。最新只读宿主清点为**24个UE**，本批新增四个均在缺Qt插件路径或观察器早期TLS递归的启动失败，无产品body终点；原采样和失败记录保留，未清理宿主。

**完整CP1仍开放，剩余四组按本节更新：** ①已定位的TileData/pool、异常/Qt/OS/TLS、caller输出及临时值，与所有owned/storage/native的完整reserved/live/并存peak/physical free独立总硬界及初次native外部合并；②其余真实node/control/task故障、其他线程与read/capture/history/publication/retirement/close、晚fence/caller共同终点；③非Darwin实际capacity/free对应实现及运行、平台Qt/OS/TLS资格；④最终源码完整manager实际终点、24 UE及默认abort/双释放失败出口。旧6dd manager Pending及本次两个具体漏项不重领；CP5公平/continuation与CP10正式性能仍归原包。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-config-initialization-delivery"></a>
### 16.89 CP1 完整manager的KConfig测试模式初始化竞争（2026-10-04）

产品 `2e471d5efb`、父3c，文档父 `d0819a2a26361c0dece775497e3655fa4cf3b74b`。[本轮证据](evidence/br1_cp1_config_tsan_20261004/README.md)补录3c完整manager在Pending检查点后的实际66/reaped、345.72s、无Totals；各1,979源码/107运行输入最终未变，原退出不是UE。匹配QtCore已能观察到KConfig全局QString读写，但KConfig本身未插桩，先用同版本6.7.0完整TSAN依赖核验：16线程cold探针直接报告`s_wasTestModeEnabled`读写竞争、实际66；在主线程完成惰性测试模式转换的warm控制实际0，无suppression。原未插桩cold/warm均实际0只是该次未触发，不抹除原manager失败。

根因是KConfig在第一个全局配置构造之后，延迟到后续构造才记录test-mode并改写全局文件名；原stress worker首次各自配置时可能竞争。原manager fixture新增initTestCase，在主线程构造两个配置对象完成初始化；测试两文件**+11/−0，生产0/0**，原压力body、48tasks/16threads/100000cycles/seed12345和预算完全保持。没有在PageStore增加锁、缓存、owner或API，没有修改依赖源码或主安装。该初始化仅修复此fixture的测试模式前置，不授予KConfig任意运行时切换模式资格。

隔离MOC重生、原8个manager/支持TU完整重编及链接通过；最终127源码匹配产品blob，图87TUs/2172APIs/27412edges/27callbacks及原结构门通过，工具未改。新原完整manager已实际加载插桩QtCore和KConfigCore、通过initTestCase，原完整body继续单次运行；实际终点前Pending。旧8f完整运行仍按原身份保留，不合并为新源码通过。

**完整CP1仍开放，四组差集继承§16.88：** ①全部owned及已定位外部native/Qt/TLS/caller存储的独立完整容量/并存peak/physical free总硬界；②其余真实故障及其他线程、晚fence/caller共同终点；③非Darwin实际capacity/free实现及平台运行；④修复后完整manager实际终点、24 UE/default abort/双native释放失败出口。本次KConfig前置与3c Pending不重领；CP5/CP10保持原包，**M6/M7/M8正式0/3、persistent默认关闭。**

<a id="cp1-qt-temporary-delivery"></a>
### 16.90 CP1 原失败回报及格式编号临时存储（2026-10-04）

产品 `87a8b43ae98bcf13fb437ee7fe2b941701035fe3`、父2e，文档父 `0e4cfdff`。[本轮证据](evidence/br1_cp1_qt_temporaries_20261004/README.md)沿原CPU实际栈关闭三处内部Qt临时分配：beginWriteImpl/sealImpl的拒绝原因直接共享原QString，空原因使用静态文本，删除拒绝后的再次拼接；backend configure在10字节栈数组转换相同quint32格式编号后直接构造原paid KisPageByteArray。具体失败原因保留、外层前缀不再拼接，原状态/取消/退休/接续及格式值不变，无新owner/锁/队列/API。

生产两文件**+8/−3**、测试0/0、派生两JSON+1800/−1799。normal/TSAN各只重编两受影响TU，189源码及1496外部编译输入冻结，407/398个继承链接输入与父构建逐项相同，127产品源/头匹配Git blob。原完整CPU双架普通**2772/0/0**，匹配插桩QtCore TSAN **1386/0/0、122.05s**，全部actual0/reaped、无TSAN警告。原observer05独立两架各1386/0/0：每架原**139次错误拼接和10次格式临时分配全部消失**，其他site变化不计收益；static后已识别paid heap/VM0、paid usable余量并存峰值0、全部表溢出0。图87TUs/2172APIs/27412edges/27callbacks及原结构门通过，工具未改。首轮依赖扫描过重的主动终止143/reaped保留，未启动产品测试；后继构建/五次完整body无失败。

8f与2e的原完整manager仍各1098 PASS前缀、无Totals，实际Pending；各1979/1615源输入及107运行输入复核，2e额外1716依赖补充亦未变。它们不是87a同源完整manager资格，实际终点后应结算。只读宿主仍24 UE，本轮无新增UE。

**完整CP1仍未关闭。** 剩余共同责任为①原TileData/pool、异常/Qt/OS/TLS/caller及所有owned/native的独立reserved/live/并存peak/physical free总硬界，含首次native外部合并；②其余真实node/control/task拒绝、其他线程、read/capture/history/publication/retirement/close与晚fence/caller共同终点；③非Darwin实际capacity/free实现和平台运行；④最终源码完整manager、24 UE/default abort/双native释放失败出口。不能再把已定位临时值逐一包装成新的主要出口；下一实施应按上述原owner的完整容量与失败责任领取，有限观察不外推全域资格。本轮三个分配来源及先前已交付项不重领，CP5/CP10保持原包。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-tile-lifetime-delivery"></a>
### 16.91 CP1 TileData 原分配、候选、交换与释放生命周期（2026-10-04）

产品 `1177fa5ecab8318fe044b071342eb0ab51654e27`、父87a，文档父 `9c338049fa41958750be1aff031e3f60e6e36862`。[本轮证据](evidence/br1_cp1_tile_lifetime_20261004/README.md)领取一条完整责任：Store预留后构造/复制nullable TileData候选、登记，pooler可选preclone，swapper取得iterator和pin，swap store转换resident/chunk，最后由TileData/cache/Boost pool物理释放。父87a双架8种control/fault共32进程：16个control实际0；default/rows/copy/clone-payload共8次SIGSEGV，cache-node两次terminate，clone-node两次payload/pin泄漏，iterator两次gate泄漏，只有swap-in两次原本安全。额外worker实际拒绝和未登记4BPP backing跨pool清理双架再暴露4个失败进程。

`allocateData`把全部native null统一为`std::bad_alloc`，Store四个nullable入口在原reservation/source pin责任内收回构造和登记失败。cache节点拒绝直接回原free/ordered pool；4/8BPP统一ordered allocate/free。`releaseInternalPools`删除复制全部活像素、purge整池再分配的窗口，只清理可选clone/cache并释放完全空闲block，含活chunk的block保留到最后原owner。Pooler的source pin、候选、iterator和统计快照使用作用域清理，失败进入既有timed cycle；Swapper的临时候选改固定64项数组并保证全部成功pin退出；swap-out/in在resident/chunk转换提交前保留回滚。没有新增公共/保护API、字段、状态、锁、队列、调度阶段或产品测试hook。生产五文件 **+198/−202、净减4行**，测试0/0；两份派生JSON **+31/−23**。

最终第三候选冻结196源码、1444外部编译输入、129产品源和五个受影响TU；normal/TSAN六步全部0，复用404/395个链接输入。最终双架8种control/fault和两项额外fault共 **36进程全部actual0/reaped**，每项实际拒绝恰命中一次，worker无需第二kick恢复，未登记backing跨pool清理后由最后owner实际free。完整CPU双架 **2772/0/0**，匹配QtCore TSAN **1386/0/0**、无警告；Store/Pooler/SwappedStore目标普通 **40/0/0**、TSAN **20/0/0**，24MiB pressure/8MiB cancel业务 **14/0/0**。图仍87 TUs/2172 APIs/27412 edges/27 callbacks，21 manifest/25 ownership/16 census/19-file ratchet通过。

最终同源完整manager绑定第三候选、2e初始化前置、插桩QtCore/KConfigCore及1716个补充Ninja输入，原48tasks/16threads/100000cycles/seed12345不减，实际 **1105/0/0、4127.357s、actual0/reaped**，无TSAN警告且三项目标镜像均确认加载。旧8f与2e manager也分别 **1105/0/0、4371.97s** 和 **1105/0/0、4348.24s** actual0/reaped，结清历史Pending但不迁作本候选资格。

本节检查点曾保留`KisLowMemoryTests::readWriteOnSharedTiles`的lazy-read SIGSEGV；后继§16.92以可靠PC、对象DWARF和当前布局双架复验确认它来自陈旧测试对象ABI，不属于产品故障。探索轮使只读宿主UE由24增至28，失败样本保留且不计通过。Boost含活block保留和ordered cold-free成本归CP10，Swapper无新增无输入重试保证归CP5。

**完整CP1仍开放，剩余出口由§16.92更新。** 本节已关闭的TileData实例和最终源码manager不重领；CP5/CP10保持原包。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-low-memory-abi-ruling"></a>
### 16.92 CP1 低内存陈旧测试ABI裁决（2026-10-04）

产品保持 `1177fa5ecab8318fe044b071342eb0ab51654e27`，生产、产品测试及派生审计改动0。[本轮证据](evidence/br1_cp1_low_memory_20261004/README.md)先用async-signal-safe守护取得§16.91反例的可靠上下文：实际SIGSEGV/reaped，fault address与FAR均`0x18`，PC相对最终候选`libkritaimage`为`0x1328d0`，LR为`0x13207c`，`x20=0`、`x24=0x18`。符号和指令确认外层`KisTiledDataManager::getReadOnlyTileLazy`从`this+0x18`载入hash table并调用内层，内层在空first-argument的`+0x18`执行原子计数；直接原因是manager对象布局错误，不是nullable tile或QSBR内部并发先损坏。

原两次父/候选运行复用同一个2026-09-25测试对象。其arm64/x86_64 DWARF均记录`KisTiledDataManager` **232B/声明行63**；当前头在2026-10-03已变化，按当前compile database、MOC和原链接输入隔离重建的对象双架均为 **288B/声明行87**，差56B。旧测试按232B在栈上布置两个manager，却调用当前动态库按288B布局写对象的构造函数，发生越界覆盖并从错误偏移读取空`m_hashTable`。旧/新库同样崩溃因此只证明二者共用无效测试可执行文件，不能作为产品共同缺陷。

当前布局测试冻结1,644个构建输入，绑定最终候选并使用独立配置与同一故障守护执行原body：arm64 **3/0/0、10260ms、actual0/reaped**，x86_64 **3/0/0、10327ms、actual0/reaped**；两架均确认候选镜像和守护加载，故障上下文0，退出后全部运行输入复核未变。§16.91低内存SIGSEGV从CP1产品残留撤销，旧失败不改计通过，相关4个宿主UE仍留在28个历史UE清单。

**完整CP1仍开放，当前剩余为三组产品责任加宿主出口：** ①全部owned/外部native独立reserved/live/并存peak/physical-free总硬界与首次外部span合并；②其他真实node/control/task拒绝、其他线程与read/capture/history/publication/retirement/close、晚fence/caller共同终点；③非Darwin实际capacity/free实现与平台运行；另结算28个历史UE、默认abort及双native释放失败出口。最终manager、TileData已修实例及本轮陈旧ABI均不重领；CP5/CP10保持原包。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-default-exit-ruling"></a>
### 16.93 CP1 双native释放失败与默认宿主退出裁决（2026-10-04）

产品保持 `1177fa5ecab8318fe044b071342eb0ab51654e27`，生产、产品测试及派生审计改动0。[本轮证据](evidence/br1_cp1_default_exit_20261004/README.md)对同一1,064,960B映射依次真实注入`munmap` EINVAL和`mach_vm_deallocate` KERN_FAILURE。首轮不安装信号处理器，日志到达`libc++abi: terminating`；只读采样确认`kisFreePageProcessStorage`经`std::terminate`、`abort`到`pthread_kill`。macOS宿主将子进程保留为UE，父进程无法回收，外层超时/reaped且子PID5915仍UE；该轮不计通过，没有继续x86默认崩溃，宿主只读清点增为29个UE。

后继只在诊断子进程安装async-signal-safe SIGABRT守护，产品和OS调用不变。父进程通过管道独立收到munmap拒绝、mach_vm拒绝和abort三个标记并回收子进程；arm64/x86_64均`child_exit=134`、父actual0/reaped，最终候选和interposer确认加载。由此确认“双native释放失败真实到达fail-fast”，不把守护结果外推为默认SIGABRT宿主资格。void deleter无法归还地址或撤销收费时继续`std::terminate`，不改成静默泄漏、伪报free或继续运行。

**完整CP1仍开放，当前剩余为三组产品责任加一个宿主出口：** ①全部owned/外部native独立reserved/live/并存peak/physical-free总硬界与首次外部span合并；②其他真实node/control/task拒绝、其他线程与read/capture/history/publication/retirement/close、晚fence/caller共同终点；③非Darwin实际capacity/free实现与平台运行；另结算29个历史UE和默认abort可回收资格。双native失败路径、最终manager、TileData已修实例及陈旧ABI不重领；CP5/CP10保持原包。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-background-retirement-failure-delivery"></a>
### 16.94 CP1 后台退休分配拒绝与晚 capture 联合终点（2026-10-04）

产品 `ee67754c0297e596f9a5b1d1cbe21166488df1e1`、父1177。[本轮证据](evidence/br1_cp1_background_retirement_20261004/README.md)补齐原 retirement queue 已接纳记录在 worker 调用 provider 时抛出 `std::bad_alloc` 的责任。旧路径的异常越过 `retireBatch`/reclamation job；executor虽以scope cleanup调用finished，但本地batch已先析构，逐记录requeue/active归还和executor post-invoke状态没有执行，随后到达worker terminate，close/idle没有恢复终点。provider正常返回invalid的既有重试不能覆盖该路径。

现在只在`retireRecord`原owner内收回该分配拒绝：provider未返回accepted result时，原scope guard取消prepared operation，同一record进入已有wait/1–100ms retry、Debt和close规则；已接受result、pending completion及不可重放分支不经过catch。没有给通用executor增加吞异常策略，也没有新增owner、队列、状态、锁或API。生产一文件 **+10/−2**，测试一文件 **+34/−0**。

联合用例先由晚captured view保留`0x31`旧版本，再发布当前`0x77`；确认旧读后设置provider连续三次抛`bad_alloc`并释放晚view，此后无新mutation、显式process或第二次close输入。原history/retirement任务自动重试，最终pending retirement/provider operation/Debt归零，当前像素保持，close后capability与provider backing归零。定向normal双架和TSAN各 **3/0/0**；完整CPU normal arm64/x86_64各 **1387/0/0**，完整TSAN arm64 **1387/0/0、无报告**。已完成长manager/pressure不重复运行。

**完整CP1仍开放，剩余收紧为三组产品责任加一个宿主出口：** ①全部owned/外部native独立reserved/live/并存peak/physical-free总硬界与首次外部span合并；②除本次retirement provider拒绝外，其余node/control/task真实allocator fault、其他线程及read/publication/晚fence/caller共同终点；③非Darwin实际capacity/free实现与平台运行；另结算29个历史UE和默认abort可回收资格。本次只是确定性provider合同拒绝，不替代跨线程allocator site census；最终manager、§16.91实例、陈旧ABI和双native路径不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-external-native-span-delivery"></a>
### 16.95 CP1 外部 pthread span 合并与原生控制块计费（2026-10-04）

产品 `e1c328ce8d275f32d2a53f2b2782c09a890016ed`、父ee67754。[本轮证据](evidence/br1_cp1_external_native_span_20261004/README.md)关闭§16.82保留的首次外部native span合并反例。旧`ReclamationThread`在创建pthread后查询其所在的整段`mach_vm_region`，把未与第一个PageStore worker重叠的全部页记为本线程控制存储；Darwin将PageStore控制对象与先存外部pthread控制页合并时，外部页会被误收费。arm64反例先保持外部线程存活并形成旧64KiB准备边界，父提交上的新用例随即因`scheduled == false`失败。

现在仍由原线程owner预留64KiB并查询真实映射，但只对SDK不透明`pthread_t`对象的页对齐owned span计费；查询负责验证该span完整映射、地址页对齐且不超过准备额，不再把相邻外部或另一个PageStore线程的页纳入本线程。旧`alreadyPaid`参数、region交集和两个span字段删除，monitor/worker各自收费并在原join后释放；无新owner、锁、队列、状态或API。生产一文件 **+20/−26**，测试一文件 **+105/−0**。

定向normal arm64/x86_64及TSAN arm64各 **3/0/0**；完整CPU normal双架各 **1388/0/0**，完整TSAN arm64 **1388/0/0、无报告**。x86_64本轮验证外部线程共存与收费上界，未观察到arm64式region合并；不外推其映射形态。已完成长manager/pressure不重复运行。

**完整CP1仍开放，剩余仍为三组产品责任加一个宿主出口：** ①全部owned/native独立reserved/live/并存peak/physical-free管线总硬界；②除§16.94 provider拒绝外的其他node/control/task真实allocator fault、其他线程及read/publication/晚fence/caller共同终点；③非Darwin实际capacity/free实现与平台运行；另结算29个历史UE和默认abort可回收资格。首次外部span合并、最终manager、§16.91实例、陈旧ABI及双native路径不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-process-storage-accounting-delivery"></a>
### 16.96 CP1 进程/原生存储的预留、存活、峰值与物理释放（2026-10-04）

产品 `02a92eb98d4ccfa02462f59ec04999bf7873dedb`、父e1c328ce。[本轮证据](evidence/br1_cp1_process_storage_accounting_20261004/README.md)关闭process/native allocator把准备额直接报告成live的缺口。父提交上的测试只建立4KiB reservation，live便从575932增加到580028，得到2/1/0；因此旧实现不能独立证明reserved、live、二者并存peak和physical free后的退费。

现在原`ProcessStorageState`分别维护live、reserved和精确总量，写端沿原gate串行，以一致快照避免和controller mutex形成反向锁序。reserve只增加reserved；commit把实际容量转为live并退回未用准备额；取消只释放reserved；allocator物理free或pthread join之后才撤销live。预算域准入与aggregate pending纳入对应process分量，usage和peak保持独立值。原`ReclamationThread`的64KiB准备额在映射验证后只提交实际控制块容量。三个原子字段由`sizeof(ProcessStorageState)`进入固定费用，normal/TSAN尾账各增加24B。无新owner、锁、队列、业务状态或公共PageStore API；生产/私有四文件**+117/−16**，测试一文件**+77/−12**。

新联合用例验证纯预留、大于实际映射的准备额提交、live与第二个reservation并存峰值，以及物理free后精确恢复。目标组normal双架与TSAN各**6/0/0**；完整CPU normal双架及TSAN各**1389/0/0**；Reference、PhysicalClaim、Completion三个核心套件每个环境合计**1274/0/0**。全部TSAN日志无报告，长manager和应用压力路径未改且不重复运行。

**完整CP1仍开放，剩余收紧为三组产品责任加一个宿主出口：** ①其他owned分配与本轮process/native子管线共同组成的完整总硬界；②除§16.94 provider拒绝外的其他node/control/task真实allocator fault、其他线程及read/publication/晚fence/caller共同终点；③非Darwin实际capacity/free实现与平台运行；另结算29个历史UE和默认abort可回收资格。本轮转换、首次外部span合并、最终manager、§16.91实例、陈旧ABI和双native路径不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-memento-storage-delivery"></a>
### 16.97 CP1 PageStore memento 存储归属与分配型 presence 包装删除（2026-10-04）

产品 `0933ea04ddbe8bb58c04dc891d864be8cd95d778`、父 `02a92eb98d4ccfa02462f59ec04999bf7873dedb`。[本轮证据](evidence/br1_cp1_memento_storage_20261004/README.md)关闭PageStore history桥仍由普通heap持有memento对象及old/new默认像素副本的缺口，并删除无生产caller的分配型`resolvePagePresence`包装。父提交上的测试创建PageStore memento后process live没有增加，得到**2/1/0**；因此§16.96的process转换当时尚未覆盖这组真实owned存储。

`KisMemento`现在区分legacy与PageStore分配来源：legacy仍使用原全局heap；PageStore工厂把对象与存储头、old/new默认像素副本交给§16.96的process allocator，释放时按同一存储头选择匹配的物理free和退费。默认像素替换仍先分配/复制候选再释放旧值，保留别名安全及commit拒绝后的重试语义。生产backend只在PageStore history入口使用新工厂。原`resolvePagePresence`分配型包装没有生产caller，现已删除；测试直接使用生产backend已有的caller-owned `resolvePagePresenceInto` scratch，避免为保持未消费的“失败不改输出”保证继续留一条Qt分配路径。五个生产/私有文件**+121/−55**，测试一文件**+44/−15**。

目标memento/presence组normal双架各**7/0/0**；CPU完整normal双架与TSAN arm64各**1390/0/0**；Reference完整三环境各**790/0/0**；`kis_tiled_data_manager_test`在正确`KIS_TEST_PREFIX_PATH`下normal双架各**1105/0/0**。legacy定向normal双架与TSAN arm64各**8/0/0**；本轮CPU、Reference及legacy定向TSAN日志无报告。首次漏传安装前缀的manager运行在848项后由资源路径检查主动终止，补上源码明确要求的测试前缀后normal双架完整通过，不计产品失败。完整manager TSAN复现未改`KisTiledExtentManager::prepareTileRange`的既有并发报告后停止；此前同一套件的活动证据也记录extent并发报告，本轮不把它写成memento回归或通过。

**完整CP1仍开放，但已从owned总界中排除本轮memento对象/像素和已删除包装：** ①清点并关闭其他owned分配与process/native子管线共同组成的完整总硬界；②除§16.94 provider拒绝外的其余node/control/task真实allocator fault、其他线程及read/publication/晚fence/caller共同终点；③非Darwin实际capacity/free实现与平台运行；另结算29个历史UE和默认abort可回收资格。§16.96转换、本轮memento、首次外部span合并、最终manager、§16.91实例、陈旧ABI和双native路径不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-owned-total-bound-delivery"></a>
### 16.98 CP1 owned存储总硬界清点（2026-10-04）

产品保持 `0933ea04ddbe8bb58c04dc891d864be8cd95d778`，生产与产品测试改动0。[本轮清点](evidence/br1_cp1_owned_total_bound_20261004/README.md)沿§16.97第一项逐个核对当前BR1 CPU/PageStore生产路径的动态owner。backend facade/Private、Store/provider/history/completion根、history/thread/source map、write batch、iterator read/write scope、lease/read cache、uniform source、extent和操作内transfer storage均由`KisPageProcessStorageObject`、`KisMutationStorageAllocator`、`KisPageByteArray`或process PMR承担；PageStore memento及两个默认像素已由§16.97补齐。未发现新的PageStore侧普通heap residue。

普通heap余项按当前ownership合同明确留在三类边界：既有`KisTiledDataManager`/hash/memento manager/Tile兼容对象；调用者输入输出及`PreparedTileUpdates`操作内候选；没有BR1 CPU产品consumer的BR0/BR3原型和持久化记录。PageStore不取得这些对象的第二份所有权，也不为它们重复收费。[机器清点](evidence/br1_cp1_owned_total_bound_20261004/owned-storage-audit.json)逐项记录分配、owner和最后释放入口。

当前完整owned硬界因此由两个不重复求和的同时上限组成：控制存储只进入product process metadata budget，按`live + reserved <= limit`准入；TileData物理payload继续由原provider/ledger的logical/resident/history/pending/retirement域硬界约束，同一backing只收费一次。§16.87祖先实际capacity与8/24MiB压力、§16.95外部pthread边界、§16.96预留/存活/物理释放、§16.97 memento当前结果共同覆盖这条边界；`6ddccc3097..0933ea04dd`的生产分配增量已逐项核对，没有把不同源码的通过数累加成新阶段资格，也不重复长压测。

**完整CP1仍开放，剩余收紧为三组：** ①除§16.94 provider拒绝外的其余node/control/task真实allocator fault、其他线程及read/publication/晚fence/caller共同终点；②非Darwin实际capacity/free实现与平台运行；③29个历史UE和默认abort可回收资格。owned总硬界、§16.96转换、memento、首次外部span、最终manager、§16.91实例、陈旧ABI及双native路径不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-read-capture-fault-delivery"></a>
### 16.99 CP1 Tiles3 read/capture真实分配拒绝（2026-10-04）

产品 `a7f0d7c537ddfbed4809136e3530ada00fd4d406`，父 `0933ea04ddbe8bb58c04dc891d864be8cd95d778`。测试先把product process metadata budget用真实allocator填到`live + reserved == limit`，保留一个实际resident read guard，再调用completed tile source capture和派生read cache冷创建；父实现泄漏`std::bad_alloc`，定向用例以 **2/1/0** 失败，确认是实际read/capture端点。

[本轮实现与结果](evidence/br1_cp1_read_capture_fault_20261004/README.md)把`captureCompletedTileSource`的分配拒绝写回原`QString *error`并返回空source；`Tiles3TileReadCache::prepare`把可选read hint的冷对象拒绝折叠为原空lease。两条路径不改变binding、guard或物理tile，也不新增重试协议。反例在硬限上确认原guard仍读到旧字节；释放filler后同一guard同时重试source/cache成功，finish与销毁后process用量回到拒绝前基线。

最终CPU mutation normal双架各 **1391/0/0**、TSAN arm64 **1391/0/0**且无报告；PhysicalClaim normal双架各 **397/0/0**；Reference normal双架各 **790/0/0**。生产一文件+13/−2、测试一文件+70/−0，无API、owner、线程或队列新增；§16.98已经绑定的8/24MiB压力不重跑。

**完整CP1仍开放，剩余仍为三组：** ①本轮completed-source/read-cache之外的node/control/task真实allocator fault，以及其他线程、publication、晚fence与caller共同终点；②非Darwin实际capacity/free实现与平台运行；③29个历史UE和默认abort可回收资格。本轮两个端点与§16.94 provider retirement不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-caller-storage-fault-delivery"></a>
### 16.100 CP1 PageStore caller联合分配失败（2026-10-04）

产品 `caaafcf58d21f5d5470dc28fa80ef146fbdb59f2`，父 `a7f0d7c537ddfbed4809136e3530ada00fd4d406`。初始化字节导入的定向用例在provider request和write-access resolve两个点分别把共享4 MiB process metadata controller的剩余容量用真实allocator填满，再发起一字节分配；调用边界把`std::bad_alloc`收回原错误返回，整个provider区间的`activeProviderCalls`由作用域归还。resolve拒绝时本轮新建backing沿原retirement路径退出；释放filler、等待退休后provider物理字节为零，同一import重试成功并读回`0x27`。

[本轮实现与结果](evidence/br1_cp1_caller_fault_20261004/README.md)还覆盖exact-generation archive caller：archive内部存储拒绝不再越过`archiveRead`，原resident lease与active计数归还，不安装pending记录；原published byte保持不变，同一版本立即重试进入原async completion/cancel/close协议。两条路径没有新增owner、队列、线程、API或重试阶段，caller-owned输入输出责任不变。

最终CPU Mutation normal双架各 **1392/0/0**，Reference normal双架各 **790/0/0**；两个受影响方法的arm64 TSAN各 **3/0/0**且无报告。生产一文件+37/−13、测试两文件+90/−0。§16.98已绑定的8/24 MiB长压测不重跑；活动architecture checkpoint早于最近已提交源码，本轮不把其stale source/callgraph结果记为通过，也不刷新生成基线换取通过。

**完整CP1仍开放，剩余仍为三组：** ①除§16.99 read/capture与本轮import/archive caller之外，有实际反例的其他node/control/task allocator fault、其他线程及publication/晚fence/close共同终点；②非Darwin实际capacity/free实现与平台运行；③29个历史UE和默认abort可回收资格。已关闭端点不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-archive-terminal-fault-delivery"></a>
### 16.101 CP1 archive完成轮询与取消终点（2026-10-04）

产品 `65746168836602d1700eefac67b083dd9e80d696`，父 `caaafcf58d21f5d5470dc28fa80ef146fbdb59f2`。扩展后的异步archive用例先完成原写入，再让最终`contains()`检查抛出`std::bad_alloc`；父版本虽返回空事件，却把已经领取的pending record永久留在`busy`，第二次轮询仍无事件，定向结果 **2/1/0**。当前`pollArchiveCompletions`在terminal candidates领取后安装无分配作用域回滚：原成功记录继续erase，失败只解除身份仍匹配的surviving record；第一次保持原空事件和pending 1，第二次收割同一成功事件。

[本轮实现与结果](evidence/br1_cp1_archive_terminal_fault_20261004/README.md)同时让`cancelStoreExact()`在分配拒绝时回到原`false`：作用域归还`activeProviderCalls`并解除同一pending record的`busy`，紧接着对同一completion重试取消成功，后续poll仍产生原Cancelled事件。两条路径不重放archive write、不复制pending状态，也不新增owner、队列、线程、API或恢复阶段。

Reference normal双架各 **790/0/0**；受影响方法arm64 TSAN **3/0/0**且无报告。生产一文件+23/−7、测试一文件+21/−0。§16.98已绑定的8/24 MiB长压测不重跑；活动architecture checkpoint仍为旧生成基线，本轮不把它记为通过或刷新以掩盖差异。

**完整CP1仍开放，剩余仍为三组：** ①除§16.99 read/capture、§16.100 import/archive read caller及本轮archive poll/cancel terminal之外，有实际反例的其他node/control/task allocator fault、其他线程及publication/晚fence/close共同终点；②非Darwin实际capacity/free实现与平台运行；③29个历史UE和默认abort可回收资格。已关闭端点不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-initial-validation-fault-delivery"></a>
### 16.102 CP1 initial replica validation活动终点（2026-10-04）

产品 `65e7d60aba9d4da5312764736157571a6b1648c5`，父 `65746168836602d1700eefac67b083dd9e80d696`。已有provider包装器在外部initial replica的`validate()`中抛出`std::bad_alloc`；父实现的函数级catch虽返回`false`，却跨过手工relock/decrement，使`activeProviderCalls`永久为1，定向结果 **2/1/0**，后继初始化被残留活动门阻断。

[本轮实现与结果](evidence/br1_cp1_initial_validation_fault_20261004/README.md)把全部provider validation放入无分配作用域：拒绝先恢复owner gate并归还活动计数，再沿原caller错误返回；未接受的外部replica仍由原provider持有，同一handle立即重试成功并继续原native-copy/read/close流程。没有新增owner、队列、线程、API或恢复阶段。

Reference normal双架各 **790/0/0**；受影响方法arm64 TSAN **3/0/0**且无报告。生产一文件+6/−5、测试一文件+14/−0。§16.98已绑定的8/24 MiB长压测不重跑；活动architecture checkpoint仍为旧生成基线，本轮不把它记为通过或刷新以掩盖差异。

**完整CP1仍开放，剩余仍为三组：** ①除§16.99 read/capture、§16.100 import/archive read caller、§16.101 archive poll/cancel terminal及本轮initial replica validation之外，有实际反例的其他node/control/task allocator fault、其他线程及publication/晚fence/close共同终点；②非Darwin实际capacity/free实现与平台运行；③29个历史UE和默认abort可回收资格。已关闭端点不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-default-materialization-fault-delivery"></a>
### 16.103 CP1 implicit default materialization终点（2026-10-04）

产品 `c19c6d83016423f4cdd7c8894e0ee7305caa6ebe`，父 `65e7d60aba9d4da5312764736157571a6b1648c5`。稀疏默认页用例让provider `requestReplica()`抛出`std::bad_alloc`；父版本异常越过`acquireRead`，并同时跳过`activeProviderCalls`递减与`finishPreparationLocked`，定向结果 **2/1/0**。这会让close看到永久活动调用，同一页的后续读取也会永久等待未完成preparation。

[本轮实现与结果](evidence/br1_cp1_default_materialization_fault_20261004/README.md)以无分配作用域覆盖provider request，并在同一`bad_alloc`终点完成default preparation、写入原read错误并返回失败。拒绝后provider/default两个活动计数均为0，同一稀疏页立即重试并继续原默认读取、首次写入、undo/redo与close流程。没有新增owner、队列、线程、API或恢复阶段。

Reference normal双架各 **790/0/0**；受影响方法arm64 TSAN **3/0/0**且无报告。生产一文件+11/−5、测试一文件+18/−2。§16.98已绑定的8/24 MiB长压测不重跑；活动architecture checkpoint仍为旧生成基线，本轮不把它记为通过或刷新以掩盖差异。

**完整CP1仍开放，剩余仍为三组：** ①除§16.99 read/capture、§16.100 import/archive read caller、§16.101 archive poll/cancel terminal、§16.102 initial validation及本轮implicit default materialization之外，有实际反例的其他node/control/task allocator fault、其他线程及publication/晚fence/close共同终点；②非Darwin实际capacity/free实现与平台运行；③29个历史UE和默认abort可回收资格。已关闭端点不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-mutation-prepare-fault-delivery"></a>
### 16.104 CP1 native mutation provider preparation终点（2026-10-04）

产品 `f0246c95c4ecb7fd2abce8f689b63d52878087f9`，父 `c19c6d83016423f4cdd7c8894e0ee7305caa6ebe`。原mutation session在稀疏默认页进入Fresh/Discard准备，provider `prepareWrite()`抛出`std::bad_alloc`；父版本异常越过`beginWrite`并跳过owner gate恢复和`activeProviderCalls`递减，定向结果 **2/1/0**。原session、transaction和close因此不能沿正常终点收敛。

[本轮实现与结果](evidence/br1_cp1_mutation_prepare_fault_20261004/README.md)以无分配作用域覆盖provider preparation。拒绝先恢复owner gate和活动计数，再写入原mutation错误并返回无效guard；当前active为0，原session取消、transaction abort及同fixture后续generic写/读/retirement全部继续。没有新增owner、队列、线程、API或恢复阶段。

Reference normal双架各 **790/0/0**；受影响方法arm64 TSAN **3/0/0**且无报告。生产一文件+8/−2、测试一文件+40。§16.98已绑定的8/24 MiB长压测不重跑；活动architecture checkpoint仍为旧生成基线，本轮不把它记为通过或刷新以掩盖差异。

**完整CP1仍开放，剩余仍为三组：** ①除§16.99 read/capture、§16.100 import/archive read caller、§16.101 archive poll/cancel terminal、§16.102 initial validation、§16.103 implicit default materialization及本轮native mutation preparation之外，有实际反例的其他node/control/task allocator fault、其他线程及publication/晚fence/close共同终点；②非Darwin实际capacity/free实现与平台运行；③29个历史UE和默认abort可回收资格。已关闭端点不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-commit-validation-fault-delivery"></a>
### 16.105 CP1 commit provider validation终点（2026-10-04）

产品 `5b4c65ae4bd6ead34e910391472a007930bad372`，父 `f0246c95c4ecb7fd2abce8f689b63d52878087f9`。原publication commit在owner gate外复验prepared proof时，provider `validate()`抛出`std::bad_alloc`；父版本异常越过`commit`，定向结果 **2/1/0**。原`commitClaim`虽能在栈展开时恢复owner gate和preparing标记，caller仍无法取得普通失败结果并沿同输入重试终点处理。

[本轮实现与结果](evidence/br1_cp1_commit_validation_fault_20261004/README.md)把该分配拒绝收回`validatePreparedPage`原`false`结果和错误文本。第一次commit返回无效ticket，`activeCommitPreparations`为0，原transaction与sealed proof各保留一份，当前committed像素不变；解除故障后同一prepared input提交成功并正常close。没有新增owner、队列、线程、API或恢复阶段。

CPU normal双架各 **1393/0/0**；受影响方法arm64 TSAN **3/0/0**且无报告。生产一文件+6、测试一文件+34。§16.98已绑定的8/24 MiB长压测不重跑；活动architecture checkpoint仍为旧生成基线，本轮不把它记为通过或刷新以掩盖差异。

**完整CP1仍开放，剩余仍为三组：** ①除§16.99 read/capture、§16.100 import/archive read caller、§16.101 archive poll/cancel terminal、§16.102 initial validation、§16.103 implicit default materialization、§16.104 native mutation preparation及本轮commit provider validation之外，有实际反例的其他node/control/task allocator fault、其他线程及publication late-fence/close共同终点；②非Darwin实际capacity/free实现与平台运行；③29个历史UE和默认abort可回收资格。已关闭端点不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-alias-prepare-fault-delivery"></a>
### 16.106 CP1 native mutation alias provider preparation终点（2026-10-04）

产品 `db7930797f4661e3a030b4004bca85c8a7011d4d`，父 `5b4c65ae4bd6ead34e910391472a007930bad372`。原native mutation alias在seal阶段调用provider `prepareSynchronousSource()`时，`std::bad_alloc`越过`seal`；父版本定向结果 **2/1/0**。原作用域保护虽恢复owner gate及`activeProviderCalls`，caller仍无法取得普通storage-refused结果并沿同alias输入重试。

[本轮实现与结果](evidence/br1_cp1_alias_prepare_fault_20261004/README.md)把该拒绝收回`prepareAliasLocked`原storage-refused结果和错误文本。第一次seal返回`false`，active为0，原transaction、page claim与alias输入保留，committed像素不变；解除故障后同一mutation seal、commit及close成功。没有新增owner、队列、线程、API或恢复阶段。

CPU normal双架各 **1394/0/0**；受影响方法arm64 TSAN **3/0/0**且无报告。生产一文件+13/−6、测试一文件+45。§16.98已绑定的8/24 MiB长压测不重跑；活动architecture checkpoint仍为旧生成基线，本轮不把它记为通过或刷新以掩盖差异。

**完整CP1仍开放，剩余仍为三组：** ①除§16.99 read/capture、§16.100 import/archive read caller、§16.101 archive poll/cancel terminal、§16.102 initial validation、§16.103 implicit default materialization、§16.104 native mutation Fresh preparation、§16.105 commit validation及本轮alias preparation之外，有实际反例的其他node/control/task allocator fault、其他线程及publication late-fence/close共同终点；②非Darwin实际capacity/free实现与平台运行；③29个历史UE和默认abort可回收资格。已关闭端点不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-platform-exit-audit"></a>
### 16.107 CP1 实际 fault 停止规则与平台出口审计（2026-10-04）

产品保持 `db7930797f4661e3a030b4004bca85c8a7011d4d`，生产/测试改动0。[清点与宿主反例](evidence/br1_cp1_platform_exit_audit_20261004/README.md)逐项反查PageStore、publication、read、retirement及archive的真实分配边界：provider分配调用均已由§16.94及§16.99–§16.106的原caller/owner终点覆盖；publication/restore付费候选在内部返回无效结果；生产archive `contains()`、provider capabilities/release及只读presence不分配；foreign/no-record retirement没有生产caller。没有得到新的生产allocator反例。

后续fault只有同时具备**生产allocator栈、父版本红例、原owner恢复终点**才重新进入CP1；不再对无分配接口增加测试throw hook，也不再以开放式搜索保持此项未完成。该裁决没有扩大已通过范围，发现具体新反例时仍按同一规则回开。

当前宿主复验前UE/E为0，原29个历史UE已不在进程表；最小非PageStore默认`SIGABRT`控制关闭core后仍在30秒内不可`waitpid`，PID90016进入`UE`且`SIGKILL`无效，采样停在`abort → pthread_kill`。因此历史残留数量已由外部宿主复位清空，但默认abort可回收资格仍失败，并留下1个当前UE。当前机器也没有容器、VM或SSH目标，不能在Darwin上猜测非Darwin allocator usable-size规则并冒充平台运行。

**完整CP1现只保留两个平台出口：** ①真实Linux/Windows runner上的actual capacity/free实现及运行；②可正常回收默认`SIGABRT`的macOS宿主复验，或对该宿主能力作合同处置。8/24 MiB压测不重跑，已关闭fault、owned总硬界、manager及双native实际路径不重领。**M6/M7/M8正式0/3，persistent默认关闭。**

<a id="cp1-platform-exits-delivery"></a>
### 16.108 CP1 非 Darwin 实际容量与平台出口结算（2026-10-04）

产品 `b51a7602c82bbee6bf2a0df79400dd943d6df5b6`，父 `db7930797f4661e3a030b4004bca85c8a7011d4d`。非 Darwin 平台存储差异收进私有 `KisPagePlatformStorage_p.h`：Linux/Unix 在分配前把 payload、同笔 mapping record 和 alignment padding 按系统页取整，用匿名 `mmap` 分配并以原 base/span `munmap`；Windows 按 `GetSystemInfo().dwPageSize` 计算同一容量，用 `VirtualAlloc(MEM_RESERVE | MEM_COMMIT)` 分配并以原 base 调用 `VirtualFree(..., 0, MEM_RELEASE)`。reserve、live、peak、查询和最后 physical free 共用一个预先确定的容量事实；释放失败保持 fail-fast。Darwin 已通过的分支未改变，其他不具备上述合同的平台保留 fallback 且不随本轮取得资格。没有新增公共/受保护 API、owner、状态、锁或队列。

[目标平台结果](evidence/br1_cp1_non_darwin_capacity_20261004/README.md)绑定同一产品提交和 GitHub Actions [37196520779](https://github.com/DesperateZero/krita/actions/runs/37196520779)：Ubuntu 24.04 与 Windows Server 2025 均以 4096 页大小通过 48 个 size/alignment 边界和 8 线程 1024 次并发 allocate/write/bytes/free；Windows 另以 `VirtualQuery` 核对 allocation base/region size。首次运行的 Linux 已通过，Windows 因 runner 未初始化 `cl.exe` 在编译前失败；只修 CI 环境初始化后双平台通过，原失败日志保留。本地共享 Unix 探针 48+1024、Android aarch64 API 28 交叉编译及 Darwin arm64/x86_64 目标各 3/0/0 通过。§16.98 已绑定的 8/24 MiB 长压测没有重跑。活动 architecture checkpoint 仍为旧生成基线，本轮不刷新，也不记为通过。

默认 abort 出口按合同处置：§16.93 已证明两个 Darwin 物理释放机制都失败时产品到达不返回的 fail-fast，且不伪报 physical free、不撤销 live charge。§16.107 的最小非 PageStore 默认 `SIGABRT` 控制在当前 macOS 15.7.3 宿主仍形成不可 `waitpid`、不可 `SIGKILL` 的 UE PID 90016，产品没有继续运行或安全恢复点。因此“默认 signal 必须被当前宿主回收”改为测试宿主健康前置；当前宿主不合格，须由宿主复位清除，不再重复崩溃探针。该处置不改变产品 fail-fast 合同，也不宣称当前宿主健康。

**§16.107 的两个平台出口均已结算，完整 CP1 关闭。** 后续只有新的生产 allocator 栈、父版本红例和原 owner 恢复终点同时成立时才重开具体 fault；当前 CP1 不再留开放项。M6/M7/M8 正式资格仍为 0/3，persistent 默认关闭，下一工作包为 CP2。

<a id="cp2-raw-access-delivery"></a>
### 16.109 CP2 原 raw 写准入与拒绝清理收敛（2026-10-04）

产品 `4b108d316c360b2d752d788799a9fffbe07ea863`，父 `b51a7602c82bbee6bf2a0df79400dd943d6df5b6`。CP2 检查发现真实写 claim 冲突或 payload 容量耗尽后，`tryWriteData` 拒绝，但 `data/tileData/setData` 在 SAFE ASSERT 后仍暴露或复制到缓存 before-image。父版本四 BPP × 四入口 × standalone/batch × 两种拒绝的 64 行中，原 fallible 入口 16 行通过，其他 48 行失败，正常 exit 48/reaped；失败样本及测试源码保留在[本轮证据](evidence/br1_cp2_raw_access_20261004/README.md)。

原私有 `markPageStoreWriteDirty` 现在返回准入事实，三个 raw 入口在拒绝时返回空结果或不复制；`tryWriteData` 保留 ABI 并直接消费同一政策，删除重复 ensure。copy/purge 用原局部 scope 合并散布的解锁分支；clear、extent、debug 与两种 codec 消费空结果，沿原终点解锁/回滚或返回既有 false。旧 codec 的 header buffer 改由原局部 RAII 归还。iterator/wrapper 已有空结果处理继续使用；memento 的旧注册路径在 bridge 存在时不执行。生产五文件 +70/-71，测试两文件 +180/-0；无新增公共/受保护签名、字段、include、friend、锁、TLS、owner、队列或费用。新增拒绝保证与等价清理分别记录，净行数不构成性能收益。

最终源码双架构每架：当前配置的完整 DataManager **1185/0/0**（含 80 个新 raw/codec 场景）、完整 PhysicalClaim **397/0/0**、完整 ResidentRead **221/0/0**、生产 recoverable/fallback/concurrent-consumer handoff 目标方法 **290/0/0**。八进程合计 **4186/0/0**，均实际 exit 0/reaped、未超时，实际加载库及源码哈希前后不变；单独 arm64 82/0/0 目标运行不重复计入该总数。`LIMIT_LONG_TESTS=1`、seed 12345 及所有命令/依赖身份明确冻结；这些计数不是分支覆盖率。原 exact bytes 在拒绝和后续新操作成功后保持不变，原 guard/intent/batch 归还；两种 codec 真实拒绝后可恢复。CP1 的 8/24 MiB 长压测没有重跑。

当前 87 TU 调用图重新生成成功：2175 APIs、27663 edges、27 callbacks、unresolved 0；实际语法解析覆盖本轮 header 的消费者。结构 checker 使用新图后仍因旧 source checkpoint 和既有 `kis_memento_manager.cc` include ratchet 差异失败；不刷新上限、不记结构门通过。完整 ON/OFF、TSAN、M6/性能资格本轮未取得。

**本段只关闭 raw 写准入拒绝后的旧值暴露/修改缺口及对应 caller 清理，不关闭完整 CP2。** 接续仍按 §17 的原 exact 受保护选择、Reserved batch 权限、epoch/ABA/晚 completion 与所有准备拒绝联动审计；未迁移 raw pin、TileData refs/users 和 Fresh 保持原保护，不以放宽 claim 条件取得命中。只有这些实际消费者与终点闭合后进入 CP3 的最终 M6 资格；M6/M7/M8 正式 0/3，persistent 默认关闭。

<a id="cp2-batch-read-delivery"></a>
### 16.110 CP2 原 parked batch wrapper 再次读取与失败归还（2026-10-04）

产品 `7d425255e2364339cc5f9cedf4472e1377f44053`，父 `4b108d316c360b2d752d788799a9fffbe07ea863`。父batch lease没有未来read cache，tile unlock后只留下ready标记，foreign wrapper reader直接blockSwapping取得仍Reserved的unpublished target。四BPP × anonymous/history共8行真实反例全部失败，actual exit8/reaped；[父源码、日志与当前证据](evidence/br1_cp2_batch_read_20261004/README.md)保留。

独立与batch写共用有效guard下的expected准备及局部失败归还。原bridge的writable布尔替换为ReadSelection/ReadCache/Write意图，所有override/caller同批迁移，旧overload不保留。ReadCache只查询原session已有parked target，先核对expected、再由原beginWrite重借并复验version；无batch/foreign/oldData/失配均拒绝，不准备新页或改选最新current。read unlock归还原guard并留下dormant hint，nested read→write移交同一活跃guard。hint不持batch/root/RAM pin，wrapper真实COW引用和binding排斥保留。

target已准备后的cache/lease交接拒绝进入原batch failed/finish/cancel，failed写入共用原leaseMutex→backend mutex顺序；standalone沿原session析构和transaction归还。生产六文件+96/-54（净+42），测试四文件+178/-28（净+150）：增加一个内部意图枚举、一个私有原target查询及既有lease构造参数，未新增字段、include、friend、mutex、TLS、owner或队列。新增权限/拒绝保证与等价合并分别计成本；净增不是去重或性能收益，上层公共API没有增长。

最终双架构每架当前配置完整DataManager **1194/0/0**、CPU Mutation **1394/0/0**、Reference **790/0/0**、PhysicalClaim **397/0/0**、ResidentRead **221/0/0**；十进程共 **7992/0/0**，actual0/reaped、未超时、实际加载与source/runtime前后哈希一致。8个新读取组合检查foreign拒绝、同owner live读取、nested写、一代/一次seal/pin归还、exact及named undo/redo、无额外capture/generic request。真实metadata硬满拒绝cache/lease交接后，释放容量仍不能静默seal；原scope取消、current/exact保持、后续新owner成功。该恢复不是同一失败操作的自动continuation。早先18个诊断消息失败及修复前矩阵单独保留，不累加成当前源码通过数；LIMIT_LONG_TESTS=1、seed12345，CP1长压力与abort探针不重跑。

当前87 TU调用闭包重新解析，unresolved0。结构checker仍失败：旧checkpoint/memento include债务之外，本轮kis_tile.cc对同一个bridge意图的四处实际caller使identifier_occurrences 13超过原上限9；CP3必须具体审阅结算，不刷新或提高ratchet、不用alias隐藏增量。ON/OFF、TSAN、完整M6及性能资格本轮未取得。

**只关闭原parked batch wrapper再次读取与该交接拒绝的有限缺口，完整CP2仍开放。** 原受保护exact重解析、其他raw/batch寿命与handoff、epoch/ABA/晚completion、全部其他实际准备拒绝继续按§17推进；refs/users及Fresh不放宽，CP1保持关闭，M6/M7/M8正式0/3、persistent默认关闭。

<a id="cp2-tile-selection-delivery"></a>
### 16.111 CP2 原 G0 选择、拒绝返回与 wrapper 寿命（2026-10-04）

产品 `5a3767cc6f9af6e3885c3eb634822798ed99553e`，父 `7d425255e2364339cc5f9cedf4472e1377f44053`。[同源证据](evidence/br1_cp2_tile_selection_20261004/README.md)用真实 process metadata 硬满验证两个 getter：父版本 32 行全部失败，正常 exit32/reaped；其中 8 个 commit/old 场景在首次准备拒绝后仍交出 wrapper，history 结束后的冷读把原 `0x31` 改选为 current `0x72`。首次夹具误把同默认值写入当作 allocated，修正后另行取得上述父红，旧运行保留、不计有效覆盖。

`getOldTile` 现在先 capture 原 G0，再从同一有效 ReadPage 取得 TileData；构造在原 pin 下取得 COW 引用，presence 从该 read 的 version 导出。失败返回空值并报告原 job failure context，不交出等待以后重选的 oldData flag。独立 old wrapper 不在 manager hash/detach 生命周期内，返回后只保留原存储和既有只读标记，不保留 backend、root 或 idle cache；短 read 沿原 release 退出。只读拒绝前移到原 `lockForWrite`，后置重复检查删除。修复中间候选四 BPP 的 owner-lifetime 负例为4失败/exit4/reaped，最后候选在manager销毁后仍读原字节且写锁明确拒绝。

current writable getter 同步消费冷准备拒绝，new miss 仍是未暴露字节的 intent。删除 `attachPageStoreTile`、复制 current 再刷新 G0、独立 presence 查询、无消费者的 bridge oldData 参数/分支及全部旧实参；桥现在只服务 current wrapper，G0 只走原受保护 capture。临时 read-cache factory 也删除，直接借既有 read→TileData 转换。实际 refs/users、raw pin 与 Fresh 排斥不放宽。

生产六文件 **+44/-31（净+13）**，测试四文件 **+160/-31（净+129）**；没有新类型、字段、owner、队列、线程、锁或上层 API。等价删除与拒绝/原版本/外层寿命保证分列，净增不计去重或性能收益。普通 write lock 在原 barrier 中检查既有只读标记，其成本仍由性能门裁决。

最终同源 arm64/x86_64 每架：完整注册 DataManager **1230/0/0**、CPU Mutation **1394/0/0**、Reference **790/0/0**、PhysicalClaim **397/0/0**、ResidentRead **221/0/0**；十进程共 **8064/0/0**，均actual0/reaped、无超时，源码/运行库前后哈希及产品Git blobs已核对。runner补齐 `.cc` 哈希；早先候选及目标子集不累加成最终资格。87 TU 当前调用图2176 APIs/27715 edges/27 callbacks、unresolved0；结构门仍因旧source checkpoint、memento include及此前bridge引用13>9未通过，没有抬高ratchet。

**完整CP2保持开放。** 下一轮按[有限差集](evidence/br1_cp2_tile_selection_20261004/cp2-audit.json)先核验 manager/hash clone 在 raw 准入拒绝后的构造与接续，再核对生产 provider epoch/allocation ABA/晚completion 联合时序，以及共同 plan 从 before/pin、physical、accounting、metadata、descriptor 到 install 的全部实际准备拒绝。原生 captured read 的原 version 重解析已有生产代码和当前 CPU/ResidentRead 结果，不重复制造同义修复；原语结果仍不能替代缺失的生产联合证明。CP1关闭、长压测/默认abort不重跑；CP3及M6/M7/M8正式资格仍未取得，persistent默认关闭。

<a id="cp2-clone-refusal-delivery"></a>
### 16.112 CP2 clone 拒绝与构造清理收敛（2026-10-04）

产品 `39700f0d53f249eed4ea189fe7d0ed98635a9ee0`，父 `5a3767cc6f9af6e3885c3eb634822798ed99553e`。[有效父红](evidence/br1_cp2_clone_refusal_20261004/parent-final-arm64/run.log)四BPP各验证已暴露字节的anonymous write拒绝和legacy源：前者backend拒绝被manager吞掉，后者clone读成默认值，共8失败、actual exit8/reaped；未暴露字节的intent及普通native clone各四行通过。最初夹具误拒绝未暴露字节的intent，以及候选的表达式/默认用户计数错误原样保留，不算额外有效覆盖；没有执行父版本已知空TileData直接复制或故意crash探针。

manager先准备canonical clone，再建兼容hash；canonical源拒绝抛已有std::bad_alloc，legacy源继续legacy，删除两条空backend回退。native memento bridge前移到hash复制前，旧memento登记不再参与；extent沿原recalculateExtent在局部RAII资源交出前准备。三个Tile复制构造共用原init，空TileData在acquire/register前进入既有构造失败。chained hash委托原空表构造，每个成功tile立即使用原link/count，部分失败沿正常析构归还；重复array/default/manager/count初始化和局部未安装链删除。lock-free原委托/析构政策保持，两模板均直接验证部分失败及同源重试。

生产三文件 **+17/-35（净-18）**，测试两文件 **+217/-0**；没有新生产类型、公共API、字段、owner、队列、线程或锁，新增一个标准new include。拒绝保证与等价清理分列，不以净删行数领取性能。原工厂返回类型承接局部backend候选，初轮新增manager类型引用超限已消除；pin、raw refs/users、Reserved和Fresh不放宽。

最终同源arm64/x86_64每架：完整注册DataManager **1311/0/0**、CPU Mutation **1394/0/0**、Reference **790/0/0**、PhysicalClaim **397/0/0**、ResidentRead **221/0/0**，十进程共 **8226/0/0**，actual0/reaped、无超时。新增81场景验证active intent/exposed、真实claim/physical预算拒绝下三Tile构造及manager的standalone/batch、两hash部分构造清理和native/legacy源；失败终结后原exact字节保持、活动write为零，解除拒绝后clone成功。171份source、95份runtime并集前后hash及产品Git blobs核对，早先候选不累加；LIMIT_LONG_TESTS=1不代表未注册的长测试，也不代表完整另一hash/OFF配置。

当前图87 TU、2176 APIs/27925 edges/27 callbacks、unresolved0，完整图无损gzip保留。[结构门](evidence/br1_cp2_clone_refusal_20261004/architecture-final.log)仍有26旧source checkpoint、inventory变化及原memento include1>0/tile bridge引用13>9差异；未改baseline或提高ratchet，没有新增manager超限。源码、运行库、所有失败及删除证明见[本轮证据](evidence/br1_cp2_clone_refusal_20261004/README.md)。

**完整CP2保持开放。** 下一按[有限差集](evidence/br1_cp2_clone_refusal_20261004/cp2-audit.json)核对生产provider epoch/allocation ABA/晚completion联合时序，以及共同plan从before pin、physical、accounting、metadata、descriptor到install的实际准备拒绝与原Fresh/cancel/close终点。clone拒绝不再重领；原语结果不代替联合生产证明。CP1关闭，长压测/默认abort不重跑；CP3和M6/M7/M8正式资格未取得，persistent默认关闭。

<a id="cp2-epoch-preparation-delivery"></a>
### 16.113 CP2 epoch、共同准备拒绝与代码安全结算（2026-10-05）

产品 `25ae0dbf8149e8c6620fc5a42d3b15b957bc37b3`，父 `39700f0d53f249eed4ea189fe7d0ed98635a9ee0`。[逐要求审查](evidence/br1_cp2_epoch_completion_20261004/cp2-audit.json)核对§17的CP2范围及§16.112两个有限差集：原legacy expected/exact重解析、raw/batch排斥、clone拒绝，真实provider epoch/numeric allocation token重用/晚completion，以及共同plan的before binding/pin、physical、accounting、metadata、descriptor和原cleanup/Fresh/终结。**完整CP2代码与安全范围结算；CP3及正式M6仍未验收。**

共同生产plan的真实收费vector136B和descriptor树节点80B拒绝会抛出std::bad_alloc，generic已有catch而native原调用未处理。最终同测试源码父版双架各98 passed/24 failed、actual exit24/reaped，仅native point0/2失败；主线程真实allocator栈与generic/其他压力controls保留。修复只在原beginWriteImpl捕获共同plan拒绝，接回原fail/discardUnprepared和cancel/abort；gate恢复、before pin及所有候选继续由原共同cleanup承担。execution的外层catch仍覆盖其他冷准备，preparationOnly/finishPreparedWrites政策保留，没有新增恢复框架或CP5 job接续。

新增每架48个epoch联合场景：真实两代provider和各自Store/Ledger共用completion registry、provider ID及numeric slot/allocation token，旧provider拒绝原地改epoch；旧handle/proof在新准备前/安装后拒绝，不能释放新pending ticket。正确新ticket完成后handoff进展，两次各在其provider内实际复用地址，旧G1暖缓存改经独立B保持0x31。没有伪造可变epoch，不声称跨重启物理地址或完整allocationIdentity相同。

新增每架120个准备场景：四BPP、两载体、五有限压力点和三原终结。真实candidate/descriptor容量拒绝、accounting成功后的metadata拒绝、ActivePending满额和实际cancelled payload的Debt满额均不留半转移；metadata压力在descriptor前解除，排除后续拒绝冒充metadata拒绝。Fresh关闭时原A/字节不变，cleanup后A/B真实claim/reset证明原pin/claim归还；原失败cancel/abort后同Store新transaction成功handoff，覆盖cancel+abort/seal+abort/seal+commit、旧exact及close归零。原冷Ledger实际容量扫描验证共同storePreparedChange的部分节点失败rollback；原64个fallback、144个生产双次序和完整oracle补齐classClaim/revision/物理排斥，详见[审查](evidence/br1_cp2_epoch_completion_20261004/cp2-audit.json)。不为同一rollback scope增建逐分配故障框架。

生产一文件 **+10/-4（净+6）**，测试一文件 **+358/-2（净+356）**；无新生产类型、公共API、字段、owner、队列、线程、锁或include。这是拒绝保证成本，不计等价删除或性能收益；原refs/users/raw pin/Reserved/Fresh保护不放宽。业务idle强引用和其他consumer迁移仍属CP6–CP9，物理Tiles3替换不扩入CP2。

完整CP2从首包父提交 `b51a7602c82bbee6bf2a0df79400dd943d6df5b6` 到当前产品的实际差集为生产12文件 **+229/-187（净+42）**、测试4文件 **+1063/-31（净+1032）**，见[整包收敛账本](evidence/br1_cp2_epoch_completion_20261004/convergence.json)。原raw/batch/G0/clone责任与同批删除逐项关联；不把逐批增删机械相加，不据净行数推定功能密度或性能收益。

最终同源arm64/x86_64每架：完整注册DataManager **1311/0/0**、CPU Mutation **1562/0/0**、Reference **790/0/0**、PhysicalClaim **397/0/0**、ResidentRead **221/0/0**；十进程共 **8562/0/0**，全部actual0/reaped、无超时，171source/96runtime并集与Git blobs核对。磁盘满造成的两个不完整x86_64记录不计通过；最后manager实际exit0及输入核对先输出、后写artifact发生ENOSPC，按保留的实际输出、PID/command/log和全部hash恢复，来源见[本轮证据](evidence/br1_cp2_epoch_completion_20261004/README.md)。原初次未处理异常后的宿主UE、fixture错误及无关debugger异常全部保留，不从Qt totals推测actual exit。2026-10-05磁盘写入恢复后同步活动文档，未重跑或累加已有完整矩阵。

当前图87 TU、2176 APIs/28175 edges/27 callbacks、unresolved0；[结构门](evidence/br1_cp2_epoch_completion_20261004/architecture.log)仍有26旧checkpoint、inventory变化及memento include1>0/tile bridge13>9。未刷新baseline或提高ratchet；CP3需当前源码完整M6合同、oracle/生产双次序、真实共同安装allocator、结构/caller/ownership及参与资源/close/Fresh统一冻结。CP1保持关闭，不重跑已结算长压测或默认abort；M6/M7/M8正式0/3、persistent默认关闭，CP5 continuation与正式性能不由本包授予资格。

<a id="cp3-install-containment-delivery"></a>
### 16.114 CP3：成功handoff安装free与结构越界关闭，性能候选未过门（2026-10-05）

产品 `500fd0702cfa07ba447d538fb9aad2b086e3160f`，父 `25ae0dbf8149e8c6620fc5a42d3b15b957bc37b3`。[本批证据](evidence/br1_cp3_m6_freeze_20261005/README.md)关闭三个当前阻塞：父真实安装probe为alloc0/free2、actual exit3，free栈落在Ledger成功撤销两个prepared index node；原冷slot先准备最多两个node handle容量，commit立即撤销原逻辑/物理claims而保留实际节点收费，到冷复用或Ledger析构才free。新增容量拒绝由原rollback承担；cancel/generic清理保持，不增加owner/队列/结果层。

完整paid/unpaid memento存储生命周期移入已有PageStore history TU，old/new default保存共用prepare/copy/free政策；原97行移动不计删除收益。四个Tile lease caller共用一个私有意图转换，ReadSelection/ReadCache/Write、原expected/dormant cache及拒绝保持。memento内部include恢复0、tile标识9/include1，原ratchet不提高。[旧checkpoint至当前34文件审阅](evidence/br1_cp3_m6_freeze_20261005/checkpoint-review.json)关联已结算CP1/CP2与本批责任后才刷新源码checkpoint；ownership/graph同步。生产六文件 **+136/-124净+12**，审计三文件 **+25766/-18203**单列；新增冷存储为保证成本，没有公开/受保护API、tile字段或新队列，不能据行数推定收益。

当前同源双架每架16目标5335/0/0、ReadBaseline45/0/0、persistent正常/cancel/四拒绝/24MiB压力/8MiB取消11/0/0及Vulkan foundation14/0/0，共 **38进程10810/0/0**，actual0/reaped、无超时、加载指定库。两架实际共同安装各 **31080区间alloc0/bytes0/free0**，共享Qt正控制分配4次；所有source SHA对应产品Git blobs、两个构建目录运行物前后核对。图87TU/2186APIs/28191edges/27callbacks，21manifest/25ownership/16census/19intrusion及六项工具自测通过。最初DYLD加载不合格、probe编译、Vulkan缺deployment环境及ownership stale图拒绝均保留；不与最终矩阵累加。LIMIT_LONG_TESTS未注册范围及TSAN不授新资格。

诊断关闭的[当前受控selector配对](evidence/br1_cp3_m6_freeze_20261005/latency-paired/analysis.json)预注册40对/四桶轮换/顺序平衡、每进程8warmup+64操作、单桶单侧98.75%及整体至少95%。H=0 retained history、同一旧exact验证capture、N=K/B4，端点为native首写→seal→canonical commit，setup/validation/close另计；两侧唯一差异为已有exact alternate。arm64 K1/K16配对延迟降幅 **-6.59%/-5.18%**，x86_64 **-6.49%/-4.75%**，四桶均未达20%/30%门。320进程/23040操作实际正常退出，像素、复用、payload delta、close和hash均正确；这是当前受控场景，不能代替正式required/upstream/stroke、固定M5回退或尾延迟资格。失败样本完整保留，不延长/挑样/修改门槛。

已有timer的额外诊断将下一排查限定到[共同冷准备](br1_modification_guide/CODE_INDEX.md#cp3-install-containment-code-index)：K1 recoverable prepare约9.25μs、install0.667μs；K16 prepare118.96μs、install9.35μs。诊断有开销且嵌套interval重叠，不能相加或推定单个分配的因果收益。下一完整责任为 `prepareWritePlanLocked → prepareBackingHandoff / preparePublicationImpl` 的候选/工作收敛，保留严格revision/claim及全部首字节前失败保证；不再添加同义helper或新的selector。回修后才按受影响范围复验，并补固定 `5173c807c87b` 同依赖Fresh/history≤2%及common metadata实际驻留≥25%重构前同义分母。CP0完整required/正式样本仍开放，现有layout ceilings不替代驻留门。

**本批结算安装free、结构与当前同源验证；完整CP3/M6未通过，M6/M7/M8仍0/3，persistent默认关闭。** CP1/CP2保持已完成，M7主包仍以M6资格为前置；没有可靠实际人日记录，不从关闭三个缺陷反推工时或减去整包估算。

<a id="cp3-cold-preparation-delivery"></a>
### 16.115 CP3：共同冷准备与 activity 安装释放收敛，性能仍未达门（2026-10-05）

产品 `840d14ae71f5c5ed4999b7ce545bbeee685fb7cf`，父 `500fd0702cfa07ba447d538fb9aad2b086e3160f`。[当前证据](evidence/br1_cp3_cold_preparation_20261005/README.md)收敛原收费 working array→StateMachine→installRecords，recoverable base/target authority从同一值派生；原slot内联两个node handles。全部publication/restore/recoverable只为实际未预留容量缺口门外增长，锁内立即取得完整slot/index reservations，删除full-demand预分配及重复growth政策。严格revision、claims、拒绝rollback及原Fresh保留，无新selector/owner/队列/公共API或业务字段。

扩展probe在明确加载父critical image后取得恢复additions **alloc0/free129、actual24/reaped**，栈落在清除publication claim时erase activity节点。原Entry现在继续持有原prepared reservation，瞬时claim立即撤销，费用到原Data的延迟clear/析构释放；成功、取消、拒绝及coordinator/controller后cleanup共用原releaseActivity。删除提前消费count/清除Entry标记的私有函数，checker同批要求现有claim和release责任、拒绝恢复安装期消费保护；原layout/intrusion上限保持。生产两文件 **+67/-96净-29**，已有测试+3、checker+6/-1、生成/ownership三文件+5162/-4678分列，不从净行数领取性能。

外部首写冷计数K1 handoff **31次/56608B→16次/3776B**，K16 **447次/909744B→238次/89728B**，请求字节减少93.3%/90.1%；Fresh保持26次/5144B及457次/99280B。此分母是malloc family请求，未含VM payload或common metadata完整驻留；不能代替≥25%结构门。最终两架各31080 handoff安装及28 index/root/descriptor/restore区间均alloc0/bytes0/free0，覆盖明确audit线程的malloc family和mmap/munmap，有实际拒绝和Qt正控制。

当前双架完整16目标各5335/0/0、业务11/0/0、ReadBaseline45/0/0、重建foundation14/0/0，共 **38进程10810/0/0**、actual0/reaped。source/Git blobs、库/探针/harness及前后SHA见[最终核对](evidence/br1_cp3_cold_preparation_20261005/final-verification.json)；87TU/2185APIs/28248edges/27callbacks、21manifest/25ownership/16census/19intrusion与六工具通过。旧probe故障未命中、VM bootstrap退出、soname加载不合格及旧checker拒绝原样保留；早先候选不累加最终资格。LIMIT_LONG_TESTS、TSAN及其他完整配置/模式的限制不变。

最终[40对受控场景](evidence/br1_cp3_cold_preparation_20261005/latency-final/analysis.json)保持四桶轮换、每进程8warmup+64操作、诊断关闭、单侧98.75%/桶和整体至少95%；320进程23040操作全部正常，H0/N=K/B4及同一exact验证capture，native首写至seal/canonical commit。arm64 K1/K16配对降幅 **5.36%/11.79%**，下界4.81%/10.38%；x86_64 **5.49%/11.64%**，下界4.74%/10.76%。四桶仍未达20%/30%，不改门或挑样；未授fixed-M5/history、upstream、stroke E或尾分位数资格。

连续两次CP3局部交付未关闭主性能门，按§17.4先重审原完整publication准备及seal/commit的可见性、失败和保活边界。现有普通publication仍保留before→StateMachine深复制，两个原准备端点均有真实consumer；下一从共同责任和必须独立的边界决定可消除工作，不新增同义helper/selector或继续拆单个allocator。opt-in嵌套阶段仅定位，不能相加或计算因果收益。固定5173同依赖Fresh/history≤2%、common metadata实际驻留≥25%的重构前同义分母、CP0完整required/正式样本继续开放。

**本批有限冷准备/安装释放责任结算，完整CP3/M6未通过，M6/M7/M8仍0/3，persistent默认关闭。** CP1/CP2不重领，M7主包仍以M6正式资格为前置；没有可靠实际人日，§17原低置信预算不因请求减少或净删而扣掉整包。

<a id="cp3-transition-values-delivery"></a>
### 16.116 CP3：共同工作值收束与固定 M5 真实性能阻塞（2026-10-05）

产品 `b8581139d22bc68d1ff15d93f44167c18bac4db3`，父 `840d14ae71f5c5ed4999b7ce545bbeee685fb7cf`，文档父 `01104423a30cd09d329265d1795cfb636cbd5c10`。[本包](evidence/br1_cp3_transition_values_20261005/README.md)核对完整seal/private publication与canonical commit：前者产生可capture/取消/重试的Prepared/overlay，后者推进root，两个边界保留。普通publication在原deltas数组暂存旧发布字段并原位压缩，同一working array交给StateMachine及additions安装；局部sequence只保留原version identities供删除和竞争记账，消费原完整工作值。删除两处嵌套状态深复制、第二additions数组及重复authority插入，无新owner/公开API/常驻字段/队列/helper。生产+47/-27净+20是轻量留存/压缩替代完整副本的成本，测试新增0，三个ownership/生成文件+524/-542；不报净删或驻留25%收益。

当前38进程双架完整CPU/业务/ReadBaseline/foundation **10810/0/0**、actual0/reaped；每架31080 handoff及28 index/root/restore安装区间malloc/VM alloc/bytes/free皆0。原oracle、拒绝/取消、并存候选、竞争、预算和延迟释放保持。87TU/2185APIs/28246edges/27callbacks、原21manifest/25ownership/16census/19intrusion与六工具通过。[同源核对](evidence/br1_cp3_transition_values_20261005/final-verification.json)绑定2315Git blobs/202运行和harness输入；早先目标组不累加，LIMIT_LONG_TESTS/其他模式/OFF/TSAN限制不变。

原40配对受控H0/N=K/B4场景，320进程/23040操作、固定样本/顺序平衡/每桶单侧98.75%，四桶仍未达20%/30%：arm64 K1/K16降幅 **5.25%/11.11%**，下界4.55%/10.43%；x86_64 **5.32%/11.15%**，下界3.09%/10.41%。不同批绝对计时不能相减计算本批因果收益。首写冷malloc计数Fresh K1/K16为25/4680B、441/91856B；handoff保持16/3776B、238/89728B，不是metadata驻留分母。

固定 `5173c807c87b` 已同依赖/工具链/双架/核心选项重建。原public H0 scanline CPP两侧完全同源并各自真实编译；新H4 public full-payload/commit/逐页sentinel/四memento/purge fixture两侧同源，末端undo/redo/close验证。两个scope各40对/四桶/250ms直接completed-work throughput/20顺序平衡blocks、50000 bootstrap seed260926、每桶单侧98.75%与原0.98下界门；各自95% family，不合称完整required family。640有效性能进程均正常；16能力进程另计。Fresh当前÷M5：arm K1/K16 **0.6934/0.4017**、x86 **0.7270/0.3988**；H4为arm **0.8945/0.5787**、x86 **0.7844/0.5876**，八桶均未过门。这是当前累计差距，不能归因本批；原“固定对照未运行”改为**真实性能回退阻塞**，下一优先原存储准入→实际分配/收费→释放/wake/close责任，保留收费与硬界，再处理handoff相对门。hot sample指向fitsLocked/reserveLocked/commitRetaining与mutation storage收费/锁链，只作定位，不从占比计算收益。

首轮current原fixture actual-11/reaped：旧对象布局未重编，extent读取落到MUTZ header；Ninja随后实际重编CPP/重链接，产品源码未修，失败/协议/runner/IPS保留且不混入新完整40对。新probe首次用CPU-test link list缺M5 testsupport而失败，改用public fixture真实link list；启动sample只捕获dyld，后继等待实际init/setup才作定位。全部失败保留。共同工作值责任结算，**完整CP3/M6仍未通过，M7/M8无资格，persistent默认关闭**。common metadata重构前used/reserved/slack同义驻留≥25%分母已询问材料路径，CP0完整required/正式样本仍欠；不把sizeof/cold请求当分母。

<a id="cp3-storage-admission-delivery"></a>
### 16.117 CP3：原同步 storage 准入/费用结算与受保护控制（2026-10-05）

产品 `9c707902d68130a17de4cbd6d64a761215387be0`，父 `b8581139d22bc68d1ff15d93f44167c18bac4db3`，文档父 `d0a7df98ca71f9334c4c506e552aef4ae464ad89`。[本包](evidence/br1_cp3_storage_admission_20261005/README.md)核对ordinary/retained/pmr全部consumer及原allocation→physical bytes→fee commit/refusal→真实free/晚尾→wake/close。同步预留留在原allocator栈，继续计入原controller domain/aggregate reserved与shared child；删除该入口generic slot/cookie及通用commit搬运。原fits/先前waiter检查、parent先准入/local先结算、预算锁外分配保持；成功/失败共用scalar结算和原wake。raw free及retained stop/detach/最后weak/control/child unregister保持。payload/class变化、cold arena/slot-array及异步grant仍有真实transferable slot consumer。无新公开API/常驻字段/owner/队列；生产+73/-8净+65、原两个测试+8/-8净0，三个audit+7022/-6998，ratchet不变，净增成本单列，不声称全项目复杂度下降。

双架完整16 CPU目标各5335/0/0、业务/ReadBaseline/foundation合计 **38进程10810/0/0**，actual0/reaped/指定库与SHA通过；每架31080 handoff及28 publication安装区间alloc/bytes/free0。每架22实际heap/VM/两级少1B拒绝/失败预留归还/硬满/最后weak及retained尾释放边界通过；allocator interposer内读取两级usage及嵌套拒绝证明budget gate释放且capacity不能二次消费。87TU/2185APIs/28248edges/27callbacks、原21manifest/25ownership/16census/19intrusion及六工具通过。[最终核对](evidence/br1_cp3_storage_admission_20261005/final-verification.json)绑定当前2315/M5 1143 Git blobs、263 runtime/harness输入和17身份集；原LIMIT_LONG_TESTS/其他模式/OFF/TSAN限制保持。

固定M5沿用同依赖/源码fixture/真实头文件与17构建选项。Fresh/H4各40对/四桶、250ms直接completed-work throughput、20顺序平衡blocks、50000 bootstrap seed260926、单侧98.75%每桶、原0.98下界，两个scope640进程全正常。Fresh当前÷M5 arm K1/K16 **0.8961/0.5369**（下界0.8796/0.5235），x86 **0.9400/0.5462**（0.9292/0.5280），四桶失败。H4为arm **1.1449/0.7554**（1.1188/0.7258）、x86 **1.0148/0.7661**（0.9973/0.7582），**K1两架过门**，K16仍低约23–24%，整体family失败；H为四个undo事务。原handoff40对320进程23040操作全正常，arm K1/K16降幅 **4.45%/9.85%**（下界3.82%/8.52%），x86 **5.19%/10.46%**（3.30%/9.24%），仍未达20%/30%。各scope独立family，不合称完整required；跨包绝对值不相减为本提交因果收益。

首轮CPU1561/1、两架Reference各786/4保留：waiter测量已暖slot而拒绝分支依赖普通allocation自动建slot，现显式匹配geometry保留少1B与候选cancel；write-set旧320B slot cache尾费实际消失，现更强断言live0/reserved0。首control编译遗漏history source、缺interposer符号，首次H4身份目录残留旧名而在启动前失败，最终另开完整40对；全部日志/runner保留，失败不计成功样本。最终K16 Fresh body的真实sample/test均正常，exclusive计算栈仍以fitsLocked为主，所有profile吞吐排除统计；下一先审原每类/域/aggregate/durable限额与generic物理delta完整政策，以及recoverable/Fresh准备真实差异，不跳检查、不放宽预算或盲拆helper。

**本批同步存储责任结算，完整CP3/M6未通过；M6/M7/M8仍0/3，persistent默认关闭。** Fresh四桶、H4 K16、handoff20%/30%、common metadata重构前同义驻留≥25%分母、CP0完整required和正式资格继续开放。CP1/CP2不重领，CP4/M7仍等待M6正式资格，原目标与§17估算限制保持。

<a id="cp3-budget-limits-delivery"></a>
### 16.118 CP3：原限额一次计算与完整准入政策等价（2026-10-05）

产品 `822456732bd02a13d128b855ed9856415544ec00`，父 `9c707902d68130a17de4cbd6d64a761215387be0`，文档父 `5a808ce5f24e2cd63799eff5681899319398319e`。[完整政策审查](evidence/br1_cp3_budget_limits_20261005/policy-review.json)覆盖原全部limiter caller、配置/usage/retained reservation/signed physical delta/process root/FIFO waiter及fee/free/晚尾/wake/close。domain限额按类一次取得、aggregate限额按调用一次取得，两个scalar selector的原消费者全部迁移；七类四域、负请求、饱和sum、empty usage/irreducible metadata、净aggregate/SSD和原process snapshot检查保持，不跳无变化类、不放宽预算、无常驻cache/字段/owner/队列/公共API。生产+22/-30净-8、测试0改动、两生成audit+867/-867，ratchet相等。arm64实际指令264→212、164→136只记录静态结果，不计因果收益。

原38同源进程 **10810/0/0**、actual0/reaped，每架31080 handoff、28 publication安装alloc/VM/bytes/free0及22真实allocator边界通过；正确VulkanFoundationContracts每架14，误选的两个中间PageStoreFoundation结果不累加。87TU/2185APIs/28248edges/27callbacks、21manifest/25ownership/16census/19intrusion和六工具通过。原父库SHA绑定§16.117实际库，相同binary加载父/当前库，两架每进程800000实际准入判断的digest/接受分布完全相同；evidence-only访问未进入生产。[最终核对](evidence/br1_cp3_budget_limits_20261005/final-verification.json)绑定2315当前/1143 M5 Git blobs、271 runtime/harness与18身份集合，资格限制保持。

三个scope沿原完整40对/四桶和独立置信/停止规则，960实际正常退出进程无并行build/benchmark。Fresh当前÷M5：arm64 K1/K16 **0.9410/0.5535**，下界 **0.9299/0.5432**；x86 **0.9887/0.5536**，下界 **0.9718/0.5433**，四桶失败。H4：arm **1.2062/0.7884**，下界 **1.1753/0.7716**；x86 **1.0620/0.8048**，下界 **1.0506/0.7846**，K1两桶通过，K16仍低约20–21%。handoff arm降幅 **4.44%/9.83%**，下界3.95%/7.91%；x86 **4.25%/9.62%**，下界3.63%/8.96%，仍未达20%/30%。不把x86 Fresh K1点估计、H4两桶或跨包绝对值相减当完整资格，见[结果与协议](evidence/br1_cp3_budget_limits_20261005/README.md)。

首次父库缺loader别名被指定image检查拒绝，另开完整差分；证据输入生成在执行前修正signed边界，旧binary不参与。误跑完整Freehand current/精确父库均15/4、相同四失败case，两个失败都保留且不计成功业务，不改容差或产品源码。兼容入口及性能预检查错误均在正式性能前修正，没有失败样本混入成功组。[原准备审查](evidence/br1_cp3_budget_limits_20261005/plan-preparation-review.json)确认native已合并Acquire/Prepare；generic初始化/readiness/失败终结及private/canonical可见性仍有独立consumer。下一审实际首写metadata/ledger工作存储与每页分配的完整值/转交/refusal/free责任，不继续加同义helper或盲合真实边界。

**本批原限额计算与完整政策审查结算，完整CP3/M6未通过，M6/M7/M8仍0/3，persistent默认关闭。** Fresh/H4 K16、handoff20%/30%、common metadata重构前used/reserved/slack同义驻留≥25%分母与CP0完整required继续欠缺。CP1/CP2不重领，CP4/M7前置保持；没有可靠实际人日和完整回修闭环，不从指令/行数/局部速度调整工期承诺。

<a id="cp3-epoch-batch-delivery"></a>
### 16.119 CP3：原工作值收费关联与稀疏 epoch 批量构造（2026-10-05）

产品 `6d439e0437c86b5214064eef5bc5134f2160cf43`，父 `822456732bd02a13d128b855ed9856415544ec00`，文档父 `98b688d3b655e432bea385185c7a5a6d503c79b2`。[领取/整包审查](evidence/br1_cp3_epoch_batch_20261005/start-review.json)、[实际结果与失败](evidence/br1_cp3_epoch_batch_20261005/README.md)、[最终身份](evidence/br1_cp3_epoch_batch_20261005/final-verification.json)绑定组合后的当前源码。原 working versions/replicas 和 removal witness 使用常见inline capacity，堆内字节属于原paid carrier、spill原费用保持。真实三版本compaction首轮actual-11，GuardMalloc/LLDB定位moved-from allocator复用失去收费owner、随后retained deallocation多减引用；原显式copy操作保持原关联，覆盖reuse/controller detach/最终free，未新增owner或字段。

原prepareCommit的sparse sorted changes/removals共同构造受影响路径，未变子树共享；AVL join处理批量增删的任意高度差，原dense threshold/build保留。原insertPageRoot/removePageRoot/minimumPageRoot及其唯一外部consumer同步替换；原conflict/revision guard、paid node/control、cold cancel/install/reclamation责任保持。生产+76/-51净+25、测试+129/-0，无新增常驻字段/owner/队列/公开API。四个独立flat oracle行各96步核对mixed insert/remove/replace、manifest/点查询/extent、树高及旧根不变性。

原38同源进程 **10818/0/0** actual0/reaped，每架Reference794、正确ReadBaseline45、selected business11、VulkanFoundationContracts14；31080 handoff/28 publication安装alloc/VM/bytes/free0和24 allocator边界通过。新增真实batch fault每架359个分配拒绝点，费用回基线/reserved0、原根/事务不变、重试成功、安装alloc/free0、最终parent live/reserved0。87TU/2187 APIs/28499 edges/27callbacks、21manifest/25ownership/16census/19intrusion与六工具通过，原ratchet相等。中间read误选后正确45项已补，两架原38总10810；旧960性能进程因read前置晚补仅作诊断，本批全部前置完成后另开完整三个scope。所有失败/修复保留，不拼接不同源码/前置的日志。

三个scope沿原四桶/完整40对与独立置信/停止规则，960进程actual0/reaped，无并行build/benchmark。Fresh arm K1/K16 current÷M5 **0.9337/0.7181**，单侧98.75%下界 **0.9182/0.7058**；x86 **0.9697/0.7326**，下界 **0.9452/0.7275**，四桶失败。H4 arm **1.2043/0.9672**，下界 **1.1874/0.9483**；x86 **1.0598/0.9952**，下界 **1.0368/0.9827**。**H4 x86 K16本轮过0.98，H4三桶通过，整族仍失败。** handoff arm降幅 **2.46%/8.10%**，下界2.04%/7.35%；x86 **2.35%/8.45%**，下界0.97%/7.44%，仍未达20%/30%。不把跨轮绝对值相减、请求次数或三桶通过当完整资格。

父库/当前两架16进程128样本只证明working数组实际请求减少，N=K沿原dense root，不能替代sparse成本或metadata驻留分母。首次继承profile只捕获dyld/init，不用于热点裁决；等待真实init marker的后继[steady stack](evidence/br1_cp3_epoch_batch_20261005/public-fresh-steady-profile/localization.json)位于原public fixture计时loop，2535 main samples中metadata applyProjectedSequence contextual524、preparePublication191、epoch prepareCommit37；inclusive定位重叠，不相加或当因果收益。下一审原私有working value在shared policy、projection和publication真实consumer间的按值移动/重复转交、拒绝和安装，保留公共oracle语义及原唯一owner，不继续无证据的容器/scalar微优化或盲合native已合并序列、generic异步与private/canonical边界。

**本批工作值/收费关联与稀疏root构造结算，完整CP3/M6未通过，M6/M7/M8仍0/3，persistent默认关闭。** Fresh四桶、H4 arm K16、handoff20%/30%、common metadata重构前used/reserved/slack同义驻留≥25%分母及CP0完整required继续欠缺。CP1/CP2不重领，CP4/M7前置保持；没有可靠实际人日，§17旧低置信估算不因节点/请求/行数或单桶速度而扣掉整包。

<a id="cp3-working-policy-delivery"></a>
### 16.120 CP3：原共同工作结果原位推进与 Fresh/H4 控制（2026-10-05）

产品 `58b4dfc09c3048d2f344ccb35a3d92d80adc390f`，父 `6d439e0437c86b5214064eef5bc5134f2160cf43`。[完整责任](evidence/br1_cp3_working_policy_20261005/checkpoint-review.json)将metadata projection/publication创建的原收费工作结果按引用贯穿shared policy，删除两种transitionResult及工作state/result的按值传入/返回/逐步接回；全部三个私有consumer迁移。公共oracle仍独立快照、执行原前后不变量检查并在拒绝时恢复current。每步effects清空、原序列carrier累计，实际容量收费及退出free保持；原revision/claim/protection/retirement debt/arena增长/活动准备与安装owner不改。生产四文件+34/-41净-7，测试0改动，生成audit+4652/-4730单列，无新字段/owner/队列/公开API或保证增量。

双架原38同源进程 **10818/0/0**、actual0/reaped，正确ReadBaseline、selected persistent business及Vulkan foundation齐全；额外六探针每架31080 handoff和28 publication/restore安装alloc/VM/bytes/free0，24实际allocator边界通过。87TU/2185APIs/28497edges/27callbacks、21manifest/25ownership/16census/19intrusion及原ratchet、六工具自测通过。[最终核对](evidence/br1_cp3_working_policy_20261005/final-verification.json)绑定2315当前/1143 M5 Git blobs、265 runtime/harness与18身份集合。

完成全部build/safety/control后沿原三个完整40对/四桶协议顺序运行960性能进程，无并行build/benchmark/采样、无截尾或扩样；各family独立裁决。Fresh当前÷M5 arm K1/K16 **0.9944/0.7711**（单侧98.75%下界 **0.9913/0.7667**），x86 **1.0673/0.8087**（**1.0486/0.8045**）：K1两桶通过，K16仍低约19–23%。H4 arm **1.2733/1.0206**（**1.2644/1.0159**），x86 **1.1300/1.0747**（**1.1226/1.0648**），**四桶及scoped family均过原0.98门**。handoff arm降幅 **2.46%/6.85%**（下界1.80%/6.35%），x86 **1.98%/7.88%**（0.80%/7.14%），四桶仍未达20%/30%。协议、原始结果及限制见[本包](evidence/br1_cp3_working_policy_20261005/README.md)。跨轮归一化结果只作趋势，不推算本提交因果收益；H4及Fresh K1不替代完整M6或真实stroke/upstream资格。

独立实际write-loop采样仍指向完整预算准入、分配/收费/释放及Ledger preparation，只作exclusive各线程定位，不计因果占比。下一沿失败桶实际物理请求与收费/转交/free责任审完整小存储单位，保持原限额、预算及真实边界，不继续堆同义helper或重领本批移动、sparse batch、CP1/CP2。首次const alias编译拒绝保留，修正后另开完整构建/同源验证。metadata重构前同义used/reserved/slack≥25%分母、CP0完整required、正式样本及长/OFF/其他完整模式/TSAN限制保持。**本批等价责任重构结算，完整CP3/M6未通过，M6/M7/M8仍0/3，persistent默认关闭。**

<a id="cp3-backing-batch-delivery"></a>
### 16.121 CP3：backing 分类合并、物理投影与 prepared claim 批量准备（2026-10-05）

产品 `feff9031b1e356c7967e1b5066ec6896549dc491`，父 `58b4dfc09c3048d2f344ccb35a3d92d80adc390f`。[完整责任](evidence/br1_cp3_backing_batch_20261005/checkpoint-review.json)在原 Ledger gate 下将 target merge、逻辑重复检查、物理别名投影与 prepared claim 去重的四组临时收费哈希存储替换为连续 pointer/index 数组及分组栈值，删除逐 backing 线性 claim 查找。原效果追加顺序、class priority、原 retirement record、首个物理 credit、预算/claims/rollback与handoff实际转交/free保持。生产一文件+98/-60净+38、独立 flat 测试+92/-0；生成audit+6349/-5897单列，无新常驻字段/owner/队列/公开API。多项非法输入并存时首个诊断可改变；接受、单项拒绝及权威状态保持。

双架原38同源进程 **10820/0/0**、actual0/reaped，正确ReadBaseline、selected persistent business及Vulkan foundation齐全；额外每架31080 handoff和28 publication/restore安装alloc/VM/bytes/free0，24实际allocator边界通过。新增测试八组24逻辑/8物理页打乱批次，以独立flat charging模型核对重复退休effect、竞争分类、并存claim、取消、安装与最终释放。87TU/2185APIs/28547edges/27callbacks、21manifest/25ownership/16census/19intrusion及原ratchet、六工具通过。[最终核对](evidence/br1_cp3_backing_batch_20261005/final-verification.json)绑定2315当前/1143 M5 Git blobs、301 runtime/harness与19身份集合。

全部前置完成后沿原四桶/40对/置信与停止规则，三个scope顺序运行960正常进程，无并行build/benchmark/采样。Fresh当前÷固定M5 arm K1/K16 **1.0307/0.8355**（单侧98.75%下界 **1.0260/0.8262**），x86 **1.1136/0.8737**（**1.0918/0.8660**）：K1两桶通过，K16仍低约13–16%，整族失败。H4 arm **1.3601/1.0924**（**1.3511/1.0799**），x86 **1.1695/1.1398**（**1.1653/1.1316**），四桶及scoped family继续过0.98。handoff arm降幅 **4.03%/9.44%**（下界3.03%/8.59%），x86 **3.87%/9.22%**（2.85%/8.52%），仍未达20%/30%。[协议、结果与限制](evidence/br1_cp3_backing_batch_20261005/README.md)区分公共scanline Fresh、H4和native N=K完整commit；跨轮归一化只描述趋势，不推算本提交因果收益或绘画体验。

父库由§16.120最终运行库SHA冻结，当前/父同ABI加载同一harness，两架16进程128样本验证实际payload、原before、新内容和close。首次完整begin/write/seal/commit的外部malloc-family请求：Fresh K1 **74次/16888B→66次/16168B**、K16 **758次/208400B→656次/196400B**；handoff K1 **68次/18128B→58次/17312B**、K16 **622次/237088B→500次/223456B**，两架一致。[实际请求](evidence/br1_cp3_backing_batch_20261005/allocation-summary.json)不等于common metadata used/reserved/slack驻留分母或速度资格。

后继实际write-loop的[steady定位](evidence/br1_cp3_backing_batch_20261005/public-fresh-steady-profile/localization.json)仍指向完整费用准入/分配/释放和首写metadata/claims，仅作all-thread exclusive定位，不计因果占比。下一重审完整首写publication内原authority/候选容量及费用准入，先核对真实consumer和拒绝/安装边界，再确定可删除的重复存储；不继续添加同义helper/第二selector或重领本批merge/claim去重、工作值移动、sparse root、CP1/CP2。**本批结算，完整CP3/M6未通过，M6/M7/M8仍0/3，persistent默认关闭。** Fresh K16、handoff20%/30%、metadata重构前同义驻留≥25%分母及CP0完整required继续开放；原长/OFF/其他完整模式/TSAN限制保持，不由请求次数或局部速度扣减旧工时。

<a id="cp3-publication-authority-delivery"></a>
### 16.122 CP3：publication authority 快照的收费批量构造与查询（2026-10-05）

产品 `5086aa6ef92e81575eca58e6862d411a593cfb7c`，父 `feff9031b1e356c7967e1b5066ec6896549dc491`。[完整责任](evidence/br1_cp3_publication_authority_20261005/checkpoint-review.json)将Data独占的authority hash快照替换为收费连续数组：首次按真实authority数reserve，后续原vector增长，一次既有MetadataKeyLess排序和二分查询；原页键/工作版本已唯一，旧节点/桶、VersionHash及insert-or-assign删除。完整查询内容与recoverable base/target派生、revision、claims、arena/activity准备、取消/安装及实际free保持。生产+22/-16净+6、测试+65，生成audit+7459/-6646单列；无新常驻字段/owner/队列/公开API。

原双架38同源进程 **10822/0/0** actual0/reaped，正确ReadBaseline、selected persistent business及Vulkan foundation齐全；每架额外31080 handoff/28 publication安装alloc/VM/bytes/free0，24 allocator边界通过。新增独立64 authority/32乱序页核对完整身份、缺失查询、移动/取消/重试/安装。87TU/2184APIs/28641edges/27callbacks、21manifest/25ownership/16census/19intrusion、原ratchet与六工具通过。[最终核对](evidence/br1_cp3_publication_authority_20261005/final-verification.json)绑定2315当前/1143 M5 Git blobs、301 runtime/harness与19身份集合。

全部前置后原三个scope各四桶/40对顺序运行960正常进程，无并行build/benchmark/采样或截尾/扩样。Fresh当前÷固定M5 arm K1/K16 **1.0409/0.8604**（单侧98.75%下界 **1.0256/0.8539**），x86 **1.1059/0.8940**（**1.0705/0.8907**）：K1过门，K16仍低约11–14%，整族失败。H4 arm **1.3777/1.1188**（**1.3648/1.1116**），x86 **1.1782/1.1820**（**1.1735/1.1765**），四桶及scoped family过0.98。handoff arm降幅 **3.31%/10.29%**（下界2.83%/8.84%），x86 **3.66%/10.35%**（2.16%/9.34%），仍未达20%/30%。[协议与限制](evidence/br1_cp3_publication_authority_20261005/README.md)区分原公共scanline Fresh、H4和native N=K完整commit；跨轮归一化只作趋势，不推算本提交因果收益或绘画体验。

父库由§16.121最终运行库SHA冻结，两架同ABI同harness的16进程/128样本验证payload、before、新内容与close。[首次完整操作请求](evidence/br1_cp3_publication_authority_20261005/allocation-summary.json)：Fresh K1 **66次/16168B→64次/16088B**、K16 **656次/196400B→624次/200176B**；handoff K1 **58次/17312B→56次/17200B**、K16 **500次/223456B→468次/226720B**，两架一致。K16请求少32次，数组增长的累计请求字节增3776B/3264B；该分母不替代common metadata实际驻留或速度门。

后继[steady实际write-loop](evidence/br1_cp3_publication_authority_20261005/public-fresh-steady-profile/localization.json)仍指向完整准入/分配/释放和prepared claims，all-thread exclusive仅定位。按§17.4重审下一完整claim责任：[原消费者清点](evidence/br1_cp3_publication_authority_20261005/next-claim-audit.json)记录既有source键与physical classClaim/slot changes的可能重叠，以及future target未登记保护和same-class no-op选中源/未选中别名的真实区别；不直接删logical guards，不新增第二claim owner或放宽limiter。**本批结算，完整CP3/M6未通过，M6/M7/M8仍0/3，persistent默认关闭。** Fresh K16、handoff20%/30%、metadata重构前used/reserved/slack同义驻留≥25%分母及CP0完整required继续缺；原长/OFF/其他完整模式/TSAN限制保持，不由请求/行数或局部速度扣旧工时。

<a id="cp3-claim-ownership-delivery"></a>
### 16.123 CP3：登记源 claim 归回原 slot，性能继续改善但未过门（2026-10-05）

产品 `84b5d5aad9f4c0c890ea2fc6dd5fb92548111524`，父 `5086aa6ef92e81575eca58e6862d411a593cfb7c`；[证据](evidence/br1_cp3_claim_ownership_20261005/README.md)、[完整责任](evidence/br1_cp3_claim_ownership_20261005/checkpoint-review.json)与[补丁/身份](evidence/br1_cp3_claim_ownership_20261005/delivery.json)绑定本批。

已登记source的原physical classClaim cookie/generation及slot.changes已表达选中的逻辑身份；所有查询迁回这项原事实，空闲查询用既有free-slot计数。删除源键reserve/insert/erase/extract、收费节点/桶增长及第二个detached handoff node；未登记future target仍由原键索引保护，安装后原冷slot保留其唯一detached node至实际复用/析构。选中源拒绝same-class no-op、未选中alias接受no-op，实际class/domain变更及新alias仍被全物理claim排斥。取消、并发、generation、退休、完整limiter及原实际free保持；busy membership仅扫其原slot O(K)。生产**+139/-133净+6**（含91行原projection移入既有Private），独立行为测试**+80**覆盖12并存physical groups/24aliases、增长、no-op、部分取消、slot复用、commit/退休；无新常驻字段、owner、队列、公开API或保证。

原双架38进程**10824/0/0**，正确ReadBaseline/selected persistent business/Vulkan foundation及真实安装探针全正常/reaped。每架31080 handoff/28 publication安装alloc/bytes/free0，24 allocator边界/registration64通过。结构87TU/2185 indexed APIs/28716 edges/27callbacks，21manifest/25ownership/16census/19intrusion及六工具通过，ratchet不提高。原三scope各四桶40对顺序运行**960正常进程**，单侧98.75%桶下界、family至少95%置信与停止规则保持，不截尾/扩样或并行build/benchmark/采样。

| 当前scope | ARM K1 比值/下界 | ARM K16 比值/下界 | x86 K1 比值/下界 | x86 K16 比值/下界 |
|---|---:|---:|---:|---:|
| Fresh 当前÷固定M5 | **1.070406/1.061202** | 0.880968/0.873217 | **1.130742/1.114984** | 0.924066/0.915081 |
| H4 当前÷固定M5 | **1.380261/1.371002** | **1.150955/1.149004** | **1.187510/1.182093** | **1.194990/1.190232** |
| handoff延迟降幅 | 4.4011%/3.3880% | 10.9183%/10.0624% | 4.4963%/3.1402% | 12.0681%/11.5382% |

[Fresh](evidence/br1_cp3_claim_ownership_20261005/fixed-m5-fresh-summary.json) K1两桶过0.98，K16仍低固定M5约8–12%，整族失败；[H4](evidence/br1_cp3_claim_ownership_20261005/fixed-m5-history-summary.json)四桶/scoped family通过；[handoff](evidence/br1_cp3_claim_ownership_20261005/latency-summary.json)四桶未过20%/30%。固定5173同依赖/选项保持。Fresh是原scanline N1024/K16端点，H4包含四个undo事务，native handoff是N=K/H0/B4 full-payload首写→seal→canonical commit；分母不互换，跨轮归一化只描述趋势，不计算本提交因果速度或真实brush体验。

父库由§16.122最终运行库SHA冻结，两架同ABI同harness的16进程/128样本核对before、新内容/payload/close。[首次完整请求](evidence/br1_cp3_claim_ownership_20261005/allocation-summary.json)：Fresh K1 **64次/16088B→61次/15944B**、K16 **624次/200176B→591次/198352B**；handoff K1 **56次/17200B→53次/17024B**、K16 **468次/226720B→419次/224128B**，两架一致。该audit线程malloc-family累计请求不替代common metadata实际驻留。[最终核对](evidence/br1_cp3_claim_ownership_20261005/final-verification.json)绑定2315当前/1143 M5 Git blobs、301runtime/harness及19身份集合；[原始日志/SHA](evidence/br1_cp3_claim_ownership_20261005/raw-log-manifest.json)完整保留。

[真实write-loop定位](evidence/br1_cp3_claim_ownership_20261005/public-fresh-steady-profile/localization.json)仍指向原完整预算/收费/free、working snapshot和projection，仅作all-thread exclusive定位。按§17.4重审[下一完整metadata batch责任](evidence/br1_cp3_claim_ownership_20261005/next-metadata-batch-audit.json)：原putBatch临时physical去重逐replica建hash节点，canonical碰撞、完整输入及arena/index预留必须另保持；先闭合所有consumer/拒绝/安装/free再选表示，不新增snapshot owner或放宽limiter。**本批结算，完整CP3/M6未通过，M6/M7/M8仍0/3，persistent默认关闭。** Fresh K16、handoff20%/30%、metadata重构前used/reserved/slack同义驻留≥25%分母及CP0完整required继续开放；本批源claim及已结算authority/工作值移动/sparse root、CP1/CP2不重领，原长/OFF/其他完整模式/TSAN限制保持，不从请求/行数/局部速度扣旧工时。

<a id="cp3-metadata-batch-delivery"></a>
### 16.124 CP3：已接受 metadata batch 删除重复物理索引，Fresh 改善但 handoff 优势缩小（2026-10-05）

产品 `864627f95737c62fe79da87677c8f4b0ab44c55a`，父 `84b5d5aad9f4c0c890ea2fc6dd5fb92548111524`；[证据](evidence/br1_cp3_metadata_batch_20261005/README.md)、[完整责任](evidence/br1_cp3_metadata_batch_20261005/checkpoint-review.json)和[补丁/身份](evidence/br1_cp3_metadata_batch_20261005/delivery.json)绑定本批。原 ShardRecordStore 直接消费原accepted working result：canonical输入唯一、所有引入/转移身份的状态机守卫保留，删除batchPhysicalSlots的临时hash、桶及逐replica节点构造/free。canInstallPhysical仍核对版本内重复和跨页面canonical碰撞；原arena/index预留、输入顺序、revision重试、Debt、拒绝和安装不变。无替代数组/排序器、新owner/常驻字段/队列/公开API或绕过开关。

生产一文件+10/-14净-4，测试两文件+127/-3，生成audit另列。24组独立oracle/global collision覆盖1/2/3/33 replicas、provider/epoch/full物理身份、新/新及已有跨版本重复、foreign页面碰撞和整体拒绝。旧压力fixture的真实176B后台epoch root free与两个合法无临时分配的接受反例保留：[全部失败/父控制/修正](evidence/br1_cp3_metadata_batch_20261005/execution-issues.json)。seal每次重试前恰满原4MiB，拒绝后live/peak≤原上限、reserved0；Debt用例占满真实spare replica slots后注入原2MiB硬满，原拒绝/原子状态/效果/cookie/收费/最终重试保持。没有修改生产换通过。

原三族四桶40对协议共960正常退出/reaped进程，未扩样、截尾或改变原下界/门槛：

| 指标（中位数 / 原单侧98.75%下界） | ARM K1 | ARM K16 | x86 K1 | x86 K16 |
|---|---:|---:|---:|---:|
| Fresh 当前÷固定M5 | **1.0881 / 1.0697** | 0.9075 / 0.8873 | **1.1421 / 1.1185** | 0.9666 / 0.9625 |
| H4 当前÷固定M5 | **1.4034 / 1.3844** | **1.1837 / 1.1445** | **1.2144 / 1.1875** | **1.2582 / 1.2417** |
| native handoff延迟降幅 | 1.48% / 0.90% | 8.14% / 7.12% | 2.23% / -0.13% | 8.64% / 7.71% |

[Fresh](evidence/br1_cp3_metadata_batch_20261005/fixed-m5-fresh-summary.json)K1通过，K16仍低固定M5约3–9%，整族失败；[H4](evidence/br1_cp3_metadata_batch_20261005/fixed-m5-history-summary.json)四桶/scoped family通过；[handoff](evidence/br1_cp3_metadata_batch_20261005/latency-summary.json)四桶未过20%/30%。Fresh K16跨轮比值0.8810/0.9241→0.9075/0.9666；handoff相对本轮Fresh优势10.92%/12.07%→8.14%/8.64%。ARM native K16绝对中位延迟的描述趋势Fresh177.38→158.75μs、handoff158.20→145.43μs；跨轮归一化或绝对值不授予本提交因果速度/真实brush体验。固定5173同依赖/选项保持；公共Fresh N1024/K16、H4四undo事务、native handoff N=K/H0/B4完整首写→seal→canonical commit的端点/分母不互换。

[首次完整操作请求](evidence/br1_cp3_metadata_batch_20261005/allocation-summary.json)同ABI同harness父/当前两架16进程128样本核对before、新内容、payload及close：Fresh K1 **61次/15944B→55次/15720B**、K16 **591次/198352B→495次/194768B**；handoff K1 **53次/17024B→50次/16912B**、K16 **419次/224128B→371次/222336B**，两架一致。Fresh每页少6次、handoff少3次；累计malloc-family请求不替代common metadata驻留或时间门。

[安全结算](evidence/br1_cp3_metadata_batch_20261005/validation-summary.json)38双架进程10872/0/0，每架16目标5366、Read45、selected business11、Vulkan14；每架31080 handoff/28 publication实际区间alloc/bytes/free0、正allocator控制4、24真实边界及registration64。结构87TU/2185API/28750edges/27callbacks、21manifest/25ownership/16census/19intrusion及六工具通过，ratchet保持。[最终核对](evidence/br1_cp3_metadata_batch_20261005/final-verification.json)绑定2315当前/1143 M5 Git blobs、302runtime/harness及20身份集合；[原始日志/SHA](evidence/br1_cp3_metadata_batch_20261005/raw-log-manifest.json)完整保留。

[公共实际write-loop](evidence/br1_cp3_metadata_batch_20261005/public-fresh-steady-profile/localization.json)仍定位预算准入/收费/free；[原生准备栈](evidence/br1_cp3_metadata_batch_20261005/native-handoff-profile-02/localization.json)使用原harness4096上界、实际completed-operation marker后采样，确认prepareWritePlanLocked/preparePublicationImpl。后者含setup/validation/cleanup，exclusive各线程与context rows仅定位，不相加或当因果占比。按§17.4，[下一完整recoverable候选责任](evidence/br1_cp3_metadata_batch_20261005/next-recoverable-candidate-audit.json)先核对单页候选输入/容量/收费/revision/claim/安装/拒绝/冷free及shared Data的publication/restore/detachment全部真实消费者，再选择等价表示；不新增owner或放宽limiter。

**本批结算，完整CP3/M6未通过，M6/M7/M8仍0/3，persistent默认关闭。** Fresh K16、handoff20%/30%、metadata重构前used/reserved/slack同义驻留≥25%分母及CP0完整required继续开放。已交付临时索引、源claim、authority/backing batch、工作值移动/sparse root及CP1/CP2不重领；长/OFF/其他完整模式/TSAN限制保持，不从请求/行数/局部速度扣工时。

<a id="cp3-candidate-storage-delivery"></a>
### 16.125 CP3：原 metadata 候选合并收费容量和 free，handoff 改善但主门仍未通过（2026-10-06）

产品 `6ffe097909e23adf3afd229a2a14e93986fae00b`，父 `864627f95737c62fe79da87677c8f4b0ab44c55a`；[结果与原始证据](evidence/br1_cp3_candidate_storage_20261006/README.md)、[完整责任/增长审查](evidence/br1_cp3_candidate_storage_20261006/checkpoint-review.json)和[补丁/身份](evidence/br1_cp3_candidate_storage_20261006/delivery.json)绑定本批。原PreparedPublication::Data的entries/publications/arenaGrowth三套独立收费vector改为同一Data分配中的有界尾部存储，所有原准备、查询、claim/install、取消、分批/延迟清理和物理free消费者一起迁移；三套reserve/growth/free删除。detachment不分配publication/growth，多页按实际分片数预留，单页跳过census；嵌套保护/arena/authority仍收费。原身份、revision、容量、activity、预算和失败政策保持，无新owner/队列/公开API/许可开关/恢复域。

生产+110/-17净+93为原owner的检查对齐布局和有界视图；直接固定内嵌会增加detachment/batch成本，按kind再建owner/allocator会分裂清理规则。测试+31/-21把原生命周期fixture扩到0/1/2/33页及1/4分片和六终结；旧复用物理slot导致的54注册失败修正为每页独立身份，原碰撞检查保持。修正后当前/父同ABI专项均282/0/0；初次失败、构建目录拒绝及回修全部[独立登记](evidence/br1_cp3_candidate_storage_20261006/execution-issues.json)，不计最终矩阵通过数，ratchet不提高。

原三个四桶40对协议顺序运行960进程，全部正常退出/reaped/身份绑定。Fresh/H4原单侧98.75%桶下界≥0.98；handoff下界K1≥20%/K16≥30%，四桶family至少95%置信，未扩样或改门限。

| 指标 | ARM K1 | ARM K16 | x86 K1 | x86 K16 |
|---|---:|---:|---:|---:|
| Fresh 当前÷固定M5 | 1.106449 | 0.906407 | 1.159416 | 0.978972 |
| Fresh 单侧下界 | **1.090748** | 0.863452 | **1.132937** | 0.964833 |
| H4 当前÷固定M5 | 1.292764 | 1.197647 | 1.230340 | 1.260605 |
| H4 单侧下界 | **1.273135** | **1.136630** | **1.211147** | **1.250843** |
| handoff降幅 | 5.54% | 12.60% | 4.80% | 13.48% |
| handoff单侧下界 | 4.78% | 11.37% | 3.35% | 12.56% |

[Fresh](evidence/br1_cp3_candidate_storage_20261006/fixed-m5-fresh-summary.json) K1通过、K16失败；[H4](evidence/br1_cp3_candidate_storage_20261006/fixed-m5-history-summary.json)四桶/scoped family通过；[handoff](evidence/br1_cp3_candidate_storage_20261006/latency-summary.json)四桶失败。与上一轮相比，handoff K16约8.1%/8.6%→12.6%/13.5%，Fresh K16比值0.9075/0.9666→0.9064/0.9790，这是[跨轮描述](evidence/br1_cp3_candidate_storage_20261006/performance-comparison.json)，不计算本提交因果收益。当前native K16 Fresh/handoff中位延迟ARM155.59/136.56μs、x86 240.61/207.99μs。固定M5 `5173c807c87bb1619325249a07a8b4f4f8f09f09` [依赖/选项](evidence/br1_cp3_candidate_storage_20261006/matched-control-build-options.json)相同，原public Fresh、H4 undo与native完整first-write/seal/canonical commit端点/分母不混用，不外推brush FPS。

[同ABI首次MutableGuard完整操作](evidence/br1_cp3_candidate_storage_20261006/allocation-summary.json)两架16进程128样本，核对before/新像素/实际物理增量/close。Fresh K1 55次/15720B→52次/15864B、K16 495次/194768B→490次/192928B；handoff K1 50次/16912B→44次/17200B、K16 371次/222336B→318次/222800B。请求减少，累计字节不一致下降；不能替代common metadata used/reserved/slack驻留分母或速度门，合法后台free差异亦保留。

[安全结算](evidence/br1_cp3_candidate_storage_20261006/validation-summary.json)原双架38进程11112/0/0，每架16目标5486/0/0、正确Read45、selected persistent五方法11和Vulkan14。[实际安装](evidence/br1_cp3_candidate_storage_20261006/install-counts.json)每架31080 handoff/28 publication区间alloc/bytes/free0，正allocator控制4，24真实storage边界/registration64保持。结构87TU/2207 indexed APIs/28842edges/27callbacks、21manifest/25ownership/16census/19intrusion及六工具通过；indexed私有方法不表示公开API增长。[最终核对](evidence/br1_cp3_candidate_storage_20261006/final-verification.json)绑定2315当前/1143M5 Git blobs、358runtime/harness及21身份集合。

[原public实际write-loop](evidence/br1_cp3_candidate_storage_20261006/public-fresh-steady-profile/localization.json)在6s write/3s sample与真实init marker后确认writeBytes/provider allocation/adoption等13上下文。exclusive各线程仅定位预算/收费/free，不计因果占比。按§17.4，[下一原provider完整候选](evidence/br1_cp3_candidate_storage_20261006/next-provider-candidate-audit.json)先核对冷adoption、物理tracking、residency注册、稳定binding、logical/physical基数与拒绝/retire/free再选等价表示；尚未实现下一设计，不新增owner、放宽limiter或扩恢复域。本批原候选packet及已结算责任不重领。

**本批代码/安全结算，完整CP3/M6未通过，M6/M7/M8仍0/3，persistent默认关闭。** Fresh K16、handoff20%/30%、common metadata重构前同义驻留≥25%分母及CP0完整required/正式样本继续开放。原长/OFF/其他完整模式/TSAN限制保持，不从请求/行数/局部速度扣旧工时。

<a id="cp3-cost-model-review"></a>
### 16.126 CP3：实际工作量与门槛可达性审查，先闭合成本账再选实现（2026-10-06）

按用户要求从算法工作量、比较口径和理论可达性重新诊断；产品保持`6ffe097909e23adf3afd229a2a14e93986fae00b`，固定M5保持`5173c807c87bb1619325249a07a8b4f4f8f09f09`，没有产品、阈值或资格变更。[有限协议/源码/全部结果/成本模型](evidence/br1_cp3_cost_model_20261006/README.md)绑定144顺序进程、2128结果及前后源码/实际运行库身份；所有检查正常通过，四个诊断块只作描述，不加入原40对协议。

原public Fresh每页只写一行，K16/B4输入4KiB；当前和M5的所有first/steady计数均为每次16页/256KiB原生foreground duplicate、16generation/16seal、1session/1commit，preclone hit和default初始化均0。预测次数与计数器实测相符；64倍before-copy放大两版都有，不能解释本轮回退。full-payload/history/native端点与pre-bound kernel不能混比。N/K交叉后，K16在小N仍观察到回退；实际COW字节增四倍时当前wall仅增约9%，支持优先排查管理，不证明全部实现没有O(N)或已测DRAM带宽。

native粗分的handoff K16 beginWrite+seal+commit约占instrumented wall的96.5%，共同seal/commit约55%/54%；cuts开关总时间有最高约10%偏移，不能授予无扰动因果占比。public recorder仍是nested inclusive，current/M5时钟密度不同；provider/prepare/compare定位不能相加或据此宣布已解释全部回退。x86_64为本机Rosetta，不能当另一台x86硬件。

原冻结样本的Fresh K16配对块绝对缺口中位约ARM21.79μs、Rosetta0.42μs，置信余量另需保留；handoff K16在Fresh中位固定时还需减少约27.65/39.56μs。共同优化会改变Fresh分母，不能机械沿用这两个缺口。20%/30%是既有工程目标，活跃入口尚缺校准后的可达性推导；零copy不代表零handoff候选/claim/发布成本。既不认定目标不可能，也不认定没有瓶颈只能零散优化。**先建立互斥CPU/wall/等待账及F/H/C预算，证明候选可删除工作能承担缺口，再选择实现；原provider候选暂不直接领取容器重写。**

原正式失败、metadata驻留分母、CP0完整required/upstream/stroke/tail/drain欠项保持；完整CP3/M6仍未通过，M6/M7/M8仍0/3，persistent默认关闭。不重跑无改动的产品安全矩阵或CP1长压测，不因本诊断放宽门槛。

<a id="cp3-management-attribution"></a>
### 16.127 CP3：管理成本归因到完整预算检查和 allocator 保活周转（2026-10-06）

按用户要求进一步明确管理瓶颈；产品仍为`6ffe097909e23adf3afd229a2a14e93986fae00b`、固定M5仍为`5173c807c87bb1619325249a07a8b4f4f8f09f09`。本轮[有限协议、CPU表、计数、扰动及全部尝试](evidence/br1_cp3_management_attribution_20261006/README.md)包含原库/原public K16 fixture的4个Time Profiler进程，独立budget TU计数的8个有效OFF/ON进程，以及1个库加载见证失败后立即停止的control尝试；失败保留，修正启动方式后另开有限批次，没有补入原正式统计或修改产品。

四份采样的主线程全部落在原timed write lambda，CPU Running、waiting threads关闭、每样本1ms，后台及未符号化覆盖单列。按互斥mechanism，current预算政策/账本与storage owner/收费衔接合计约25.9%–27.2%，CPU量级投影约63.9–66.2μs/op；其中完整`fitsLocked` leaf为11.82%/12.99%，不能与其父调用再相加。底层heap约12.3%–14.7%，低于M5约29.4%–30.0%；canonical commit也明显下降。μs是2s采样比例×6s thread CPU/op的稳定混合假设投影，不是逐阶段wall、等待或可删除收益。

独立TLS计数确认原public K16每次约524个control allocation请求、339个retained owner allocate、446套local/parent prepare及settle、988次完整预算检查；约892次直接对应两级逐对象prepare。预算对单MetadataArena/CpuRam请求仍检查7类×4域及aggregate/durable政策。allocator `deref`约6157次而foreground retained deallocate仅48次，采样指向working/projection/publication的引用临时值周转，不能把引用次数当物理free。K1对应约82分配/153检查/571引用归还；两K点不证明全局复杂度。K16所有实际copy/generation/seal/session/commit计数与§16.126相同，不能与旧native cold的490次malloc口径混比。

互斥区域投影显示page acquire净增约35–40μs CPU、adapter begin/finish/其他约18μs；commit减少约17–30μs、seal减少约3–7μs，before-read整段略减。故读link安装增加和opt-in compare高值不能独自解释净回退。provider `prepareAdoption` inclusive仅约13–15μs CPU且含预算/heap/binding，不足以证明仅改几个节点可承担正式Fresh K16约21.8μs wall缺口。下一候选先审查原全链条控制容量准入/两级结算及短命working值的retained allocator传播，给合法等价删除、预测调用降幅和预算，不先选容器重写或新增owner。

计数K16 ON/OFF wall最高+7.53%、thread CPU最高+7.49%，只授予数量；原库CPU采样只授予定位。锁等待wall、后台最终drain、M5同口径计数、Rosetta/native handoff机制账及真实stroke敏感度仍开放，不能将public投影直接用于handoff变动分母可达性。原正式失败/阈值/metadata驻留分母/CP0 required均保持，完整CP3/M6未通过，M6/M7/M8仍0/3，persistent默认关闭。

<a id="cp3-algorithm-budget"></a>
### 16.128 CP3：全路径算法预算、固定矩阵及 root 分支工作量放大（2026-10-06）

按用户要求从同一用例的算法理论建立整条责任账，而非逐热点试改；产品保持`6ffe097909e23adf3afd229a2a14e93986fae00b`、固定M5保持`5173c807c87bb1619325249a07a8b4f4f8f09f09`，没有产品或门槛变更。[完整三层预算、责任账、协议、源码模型及全部残差](evidence/br1_cp3_algorithm_budget_20261006/README.md)绑定N64/N1024×K1/2/4/8/16/32及两个B/h控制点：84个未插桩时间进程、14个原同源budget计数进程，共98顺序进程，前后源/库/helper身份、实际加载、像素/extent、退出/reap全部通过。原TU及fixture均`-O2 -g -DNDEBUG`；三块仅作描述，不补入正式40对协议。

API语义下界与冻结Fresh页表示分开。K16/B4/h1输入4KiB，当前页粒度不可变before保证要求256KiB before-copy，合计260KiB逻辑目标字节；不是实测DRAM流量。全部98进程的copy/generation/seal/session/commit预测误差0，两版均2K局部序列、3K局部版本输入、K mutation-base输入，完整snapshot导出0，发布约2K版本/K页且保留微量重验。索引、相关V/R、root路径并集U、实际容量/parent child账本、引用/晚free、异步债务和调度共同进入模型，不能把4KiB memcpy当整次性能下界。

未插桩N1024/K16主线程CPU中位M5约207.15μs、current约238.38μs；描述性a+bK斜率current约14.0–14.1μs/页、M5约10.4–12.2。B增四倍current CPU仅约+9.9%，支持同阶状态动作的实现/生命周期成本增加，不证明无全局复杂度缺点或全部时间系数可辨识。§16.127互斥CPU分区继续提供整次时间账，不能与inclusive层或单独copy控制相加。

源码模型确认旧`K >= ceil(N/4)` dense启发式仍在，但current sparse已改为union-path批量构造。连续前16页已有键替换时，N64的sparse只需18个新root节点，实际选择dense构造64个；N1024实际sparse22个、M5逐键150个。每current root节点2个storage请求/4次两级fits，dense另1个buffer/2次fits；从N1024实测非root参考量预测N64首次差额，6个K×两字段共12项误差全0，K16差额85请求/170检查精确闭合。这是运行后源码推导的跨N差额验证，非事前绝对全链条预测；steady残差最大约2.62请求/5.23检查继续保留。N1024主门已用较优sparse，native N=K的dense与union节点量相同，不能把选择策略缺点冒充整个主门修复。

另有publication输入去重K(K−1)/2次key比较（K16为120、K32为496），复杂度缺点明确，CPU权重尚未授予。完整工作量/时间账覆盖原operation到retire全部责任，但必要系数、真实等待/最终drain、M5同口径管理计数、两架构/native及实际stroke仍有缺项；算法理论不给凭空精确理想μs，也未证明只能积累零散优化或门槛必不可达。下一实施须先给完整对象/容量/lifetime图、合法等价删除及`ΔA/ΔB/ΔF/ΔR/Δbytes`预测和可承担缺口的保守预算，再做有限因果验证。全部原正式失败、metadata驻留分母、CP0 required保持；CP3/M6未通过，M6/M7/M8仍0/3、persistent默认关闭。

<a id="cp3-capacity-lifetime-attribution"></a>
### 16.129 CP3：原控制容量、allocator引用及实际寿命分布（2026-10-06）

按优先项继续测试，产品保持`6ffe097909e23adf3afd229a2a14e93986fae00b`，没有产品/门槛变更。[冻结协议、全部事件、源补丁及方向分析](evidence/br1_cp3_capacity_lifetime_20261006/README.md)覆盖public N64/K1、N1024/K16、N64/K16和native Fresh/handoff各K1/K16，两个顺序平衡control/trace块，共28进程actual0/reaped；像素/工作量/extent或旧新exact/物理增量/close、实际加载和前后身份通过。只机械插桩一个budget TU、复用374个实际对象，原收费/引用/失败政策保持；14个追踪进程358815事件，重插桩时间全部排除。首次atos分隔符解析失败及摘要过宽覆盖断言保留，分析同一原始批次，没有补样。

public N1024/K16后次写入两块均524控制请求、446套两级prepare/settle、988 fits、6157 deref。working值2640、projection1296、metadata publication633合计4569，即74.21%的引用归还；不等于free或可删除比例。524中78经原process storage，其余446个controller-backed成功对象有实际地址匹配：144在操作阶段内释放、257在后续验证/manager销毁释放、45到捕获结束尚未闭合。provider96、retirement48、completion32均有跨操作责任；不据此建立commit即free的统一operation arena。首写后未追踪warm区间断开地址匹配；全线程phase只表时间窗口，原尾/最终drain仍有明确边界。

native K16完整操作Fresh/handoff分别471/313控制请求、893/624 fits、5830/5286 deref，分配/检查约减少33.55%/30.12%，引用只减少9.33%。seal两侧同74请求/116 fits/1629 deref，commit两侧同1489 deref；seal+commit共3118次，占handoff58.99%，314 fits占其50.32%。handoff的working/projection/publication引用合计4829/5286。两块数量一致，补强共同管理定位，但不授予native CPU占比或30%可达性，不能把public64–66μs搬用。

N64/K16仍比N1024多85个root来源请求；两块总请求609/601、fits1158/1142的差额落在8个MetadataPageActivity节点准入，状态残差不抹去。主线程被测control request/success和deref均可归属；public仍有36个fits及各2个prepare/settle、native每次2个raw free未归具体责任，原栈/总数保留。局部dense选择仍为次优先级，不能解释N1024或native全部缺口。

下一完整候选继续先给原控制容量/working值的owner、实际容量和lifetime图，区分短命scratch、移入prepared值及真实尾；按原owner证明可合并分组与`ΔA/Δfits/Δref`，保持两级限额/公平/失败归还/最后free。单独引用参数微调或provider容器替换没有承担主缺口的充分收益证据；候选后才做有限未插桩因果验证。本轮没有优化前后速度结果或新置信区间，原Fresh/handoff失败、metadata驻留同义分母、CP0 required及M6/M7/M8 0/3保持，persistent默认关闭。

<a id="cp3-scoped-storage-delivery"></a>
### 16.130 CP3：metadata作用域保活、内部借用及理论/实际验收（2026-10-06）

产品`57e59e6b0e53c625b0e4853985a242b5433ca618`，父`6ffe097909e23adf3afd229a2a14e93986fae00b`。[设计、全改动清单与S1–S7/V1–V3完成矩阵](evidence/br1_cp3_scoped_storage_20261006/README.md)、[完整责任/增删](evidence/br1_cp3_scoped_storage_20261006/closure-review.json)、[提交与实际库身份](evidence/br1_cp3_scoped_storage_20261006/delivery.json)绑定本包。原allocator增加编译期拥有/借用区别，local scope、原PreparedPublication::Data、arena目录和shard budgetAuthority分别覆盖真实寿命，嵌套working/projection/delta/authority/growth/map allocator不再重复保活。实际allocation引用、收费、revision/claim/失败/重试、worker及controller detach后free保持；provider/retirement/completion等独立尾保持拥有。生产5文件+72/-38（净+34），测试+68/-5，结构/所有权+4/-2，派生调用图另列；无新逻辑owner、队列、公开业务API或恢复域。每arena根从原目录allocator移至成员，布局额外16B/每shard48B（取整前），不声称内存优化。

初版继承基类rebind使Store::MutationAllocator丢失原MutationLifetime，原runtimeStopsAtCapacity真实失败留下512B；LLDB/39131事件确定4个Store的64B控制块及64B登记，现已显式rebind回本族并增加编译期断言。原归零断言未放宽；全部[失败与回修](evidence/br1_cp3_scoped_storage_20261006/execution-issues.json)保留。最终双架38个QTest进程**11114/0/0**，另6探针通过；每架31080/28个实际install区间alloc/free0，24 storage边界通过。87 TU/2209 APIs/28868逆边/27 callbacks、21 manifest/25 ownership/16 runtime census/19 intrusion和6工具测试通过，ratchet不放宽；[Git blobs/库/样本复核](evidence/br1_cp3_scoped_storage_20261006/final-verification.json)通过。

同一public N1024/K16/B4/h1/H0后次写入，[28进程数量矩阵](evidence/br1_cp3_scoped_storage_20261006/quantity-comparison.json)的两块目标链均**4569→54，减少98.82%**，working2640→0、projection1296→48、publication633→6；32局部根+1发布准备根+20实际free+E的事前模型得到**E=1**。整次deref6157→1645/1642（减少73.28%/73.33%）；3次差异为publication descriptor清理落点，逐块保留。524请求/446 controller成功/78 process/339 retained allocation/988 fits、目标链20实际free及每操作controller容量保持。14 trace进程277699事件，语义/库/前后身份与正常退出通过；45个epoch尾仍在捕获窗口外，不宣称全量drain。native K16共同seal/commit引用3118→279。53+E是本设计可达模型，不是所有合法算法的严格下界。

[父版本40对未插桩对照](evidence/br1_cp3_scoped_storage_20261006/parent-comparison-summary.json)：ARM K1/K16吞吐+2.63%/+5.04%，各双侧95%区间[1.91%,3.50%]/[2.78%,7.44%]；Rosetta +2.17%/+3.63%，区间[1.74%,2.93%]/[3.13%,4.97%]。ARM K16每次CPU节省**15.06μs [7.53,19.35]**，wall节省14.81μs [7.65,21.08]；这些为20个顺序平衡块的配对估计，不与边际中位差混算，也不是family阶段门。Rosetta线程CPU计数未校准翻译执行覆盖，只以wall吞吐论收益。[4次CPU Running采样](evidence/br1_cp3_scoped_storage_20261006/cpu-comparison.json)显示目标链deref约6.03–6.38→0–0.12μs，全部owner deref8.59–9.26→1.69–1.79μs，兑现原直接成本约6μs的预测。总收益还包含ref/构造/编译简化等，未精确拆分；短采样与约3%–4%未符号化leaf不支持零成本或全机器外推。

原正式规则的[Fresh](evidence/br1_cp3_scoped_storage_20261006/fixed-m5-fresh-summary.json)/[H4](evidence/br1_cp3_scoped_storage_20261006/fixed-m5-history-summary.json)/[native](evidence/br1_cp3_scoped_storage_20261006/latency-paired-summary.json)仍各40对、四桶单侧98.75%下界，不补样。Fresh K1/H4四桶通过；Fresh K16 current/M5为ARM0.9464（下界0.9261）、Rosetta1.0169（0.9308），两桶仍未过0.98门。native K1 handoff延迟减少5.58%/4.29%（下界4.57%/3.48%）未达20%；K16为14.29%/14.91%（13.89%/13.42%）未达30%。Rosetta点估计超过M5不等于取得置信下界资格；共同成本改变使Fresh分母也变，旧新native比值差不冒充本轮因果收益。1280性能进程全部正常、身份/语义通过，性能门失败单列。

本轮优化与矩阵完成，完整CP3/M6仍未通过，M7/M8不提前开放，persistent默认关闭。剩余public单leaf热点为**988次fitsLocked，约28.55–30.65μs/次**；预算政策+owner收费互斥合计约57.13–58.31μs（约24% CPU），不等于可全部删除。下一优先对原两级准入/settle重复政策扫描与批次边界建可删除工作预算，保持实际capacity、总硬界、公平/拒绝归还/晚free；引用模型已经兑现，不再重领借用迁移或provider无证据容器重写。metadata同义驻留≥25%分母、CP0 required、TSAN等欠项保持，本包不关闭完整stroke资格。

<a id="cp3-metadata-admission-delivery"></a>
### 16.131 CP3：算法成本skill与metadata准入依赖范围优化（2026-10-06）

本线程方法已固化为个人[algorithm-cost-optimization skill](/Users/apple/.codex/skills/algorithm-cost-optimization/SKILL.md)，[版本快照](evidence/br1_cp3_metadata_admission_20261006/skill/SKILL.md)随证据保存。它要求先固定同义工作量和源/库身份，区分必要成本、可构造理想实现及当前重复工作，事前预测数量与条件时间空间，完成consumer/寿命/失败闭包，再用固定矩阵分别裁决机制、增量与正式资格。本包从父`57e59e6b0e53c625b0e4853985a242b5433ca618`选择原988次完整准入里的重复六类扫描；[B1–B5/V1–V3矩阵](evidence/br1_cp3_metadata_admission_20261006/README.md)、[责任及增删](evidence/br1_cp3_metadata_admission_20261006/closure-review.json)绑定源码，最终产品和库身份见[delivery](evidence/br1_cp3_metadata_admission_20261006/delivery.json)。

原controller在同一mutex内保存六类零增量可行性（含false）及饱和live SSD和；activate/commit/成功改限额/非metadata释放/退休换域保守失效。metadata四域/aggregate、实时process snapshot和全局durable预留每次检查。三处已知metadata CPU caller全部迁移，通用signed/empty-usage路径保留完整政策并共用bucket函数。原公平、总硬界、parent/local准入与settle、拒绝和最后free保持，无新逻辑owner/账本/队列/公开业务API/恢复域。生产2文件+81/-25（净+56）、ownership+1/-1、派生物+1195/-1018；每controller布局1360→1376B，新增16B沿原实际容量收费。

双架38个QTest进程**11114/0/0**及原6探针通过；每架31080/28实际安装区间alloc/free0，24 storage边界通过。87 TU/2211 APIs/28880逆边/27 callbacks、21 manifest/25 ownership/16 runtime census/19 intrusion和6工具检查通过，ratchet不放宽。另8个[实际函数策略差分进程](evidence/br1_cp3_metadata_admission_20261006/policy-differential-summary.json)：每架父/新库各800000通用判断digest一致，每架1200000组metadata cold/warm/full比较及14个状态序列通过；非法状态注入用于验证等价和缓存失效，不宣称其业务可达，也不并入QTest通过数。

原[28进程数量矩阵](evidence/br1_cp3_metadata_admission_20261006/quantity-comparison.json)完成，K16保持Q=988、524请求/446 controller成功/78 process路由/339 retained请求及两级prepare/settle和操作收费容量。实测G=17、M=971、R=63/61，原成功扫描`7Q=6916`对应候选`7G+M+6R=1468/1456`，**类别检查减少78.77%/78.95%**，逐块无模型残差，超过事前≥50%目标。1090是忽略刷新后的条件数量界，实际额外366～378次为刷新；不能把78.9%当时间节省，也不把晚free强制搬到同一窗口。

[父库40对四桶增量](evidence/br1_cp3_metadata_admission_20261006/parent-comparison-summary.json)给出ARM K1/K16吞吐+13.42%/+17.29%，双侧95%区间[12.88%,14.23%]/[12.39%,20.53%]；Rosetta +11.73%/+12.86%，区间[10.88%,12.12%]/[12.19%,13.61%]。ARM K16 CPU节省35.14μs [29.44,39.16]，wall节省42.07μs [30.86,47.81]。总补丁收益超过事前仅扫描成本24.5～26.3μs的条件估算，差额保留，未全部归因于缓存。Rosetta线程CPU覆盖未校准，不作物理CPU结论。原[Fresh M5四桶](evidence/br1_cp3_metadata_admission_20261006/fixed-m5-fresh-summary.json)全部通过：K16 current/M5 ARM1.0986、Rosetta1.1397，单侧98.75%下界1.0621/1.1214，均超过0.98，关闭此前Fresh K16置信下界缺口；整阶段仍由其余正式门共同裁决。

最终产品`0a00bd3fe3fe71e44c04b987f9558bcd37f00dc6`的[源码/样本身份复核](evidence/br1_cp3_metadata_admission_20261006/final-verification.json)通过。[H4](evidence/br1_cp3_metadata_admission_20261006/fixed-m5-history-summary.json)四桶全部通过；[native](evidence/br1_cp3_metadata_admission_20261006/latency-paired-summary.json)K1 handoff改善3.68%/2.90%（下界2.81%/0.84%）未达20%，K16改善11.99%/12.60%（10.90%/11.38%）未达30%。四组1280进程全部正常，性能门失败独立保留；旧新handoff比值的差不能替代原生父/新增量配对，因为Fresh也受共同优化影响。

[4份CPU诊断](evidence/br1_cp3_metadata_admission_20261006/cpu-comparison.json)的可识别准入上下文约28.88～30.70→1.61～2.06μs；独占预算+owner约54.94～56.22→25.25～28.34μs，方向符合重复扫描移除。短采样不是精确阶段计时，约3.2%～4.0% leaf未符号化；三份各1个外层测试循环样本触发初版分析器过严断言，保留旧脚本和失败后重析同一XML，无重采样，见[回修](evidence/br1_cp3_metadata_admission_20261006/analysis-repair.json)。

本责任完成，完整CP3/M6仍未通过。下一先核对native差异准备与必要收费/settle，保持真实capacity/失败/独立尾。当前ARM K16边际中位数Fresh125.17μs、handoff110.10μs；假设Fresh不变，30%门还需handoff约22.49μs，Rosetta约33.50μs。若只等量删除两边公共成本，则所需C约74.96/111.66μs；这是条件可达性预算而非置信判定，不能继续凭剩余少量公共扫描预报关闭主门。metadata实际驻留分母、CP0 required及其余正式欠项保持，persistent默认关闭。

<a id="cp3-handoff-storage-reuse-delivery"></a>
### 16.132 CP3：原handoff准备槽存储复用及增量核验（2026-10-06）

用户要求继续解决下一处算法实现开销。按原算法成本skill从native差异准备审查到：ledger原冷槽已保留空changes缓冲区和detached目标claim节点，但每页重建数组并销毁/重建同一节点。产品父`0a00bd3fe3fe71e44c04b987f9558bcd37f00dc6`，最终`f0c40a5d195f1c20a0f915faaef18b1f3ee5b575`。[完整H1–H3/V1–V3清单、预测、实测和失败记录](evidence/br1_cp3_handoff_storage_reuse_20261006/README.md)、[代码](br1_modification_guide/CODE_INDEX.md#cp3-handoff-storage-reuse-code-index)、[身份](evidence/br1_cp3_handoff_storage_reuse_20261006/final-verification.json)共同绑定本包。

在原ledger mutex内通过原准备参数移出/移回单元素数组，改写并插回同一个目标节点。大于一元素的旧普通批量容量仍冷缩减；原预算/retirement、源/目标/物理claim、rollback、取消、generic复用及最后释放保持。生产+23/−6、净+17，无新字段、owner、队列或公共API；测试+72（行为66、全局压力fixture6），ownership+1/−1，派生物+2131/−1681。原真实安装零alloc/free保持。

事前模型为顺序成功K页两类请求`2K→2`，不代表并发P份准备或取消重试也只需一份。ARM原28进程/14 trace共333111事件，两个K16 handoff块均精确兑现：目标32→2（−93.75%），整个ledger准备36→6、累计收费分配容量3456→576 B，完整事务请求313→283（−9.58%）、controller成功279→249、两级准备/结算各合计−60、判断624→564、raw free124→94；deref575/retained166不变。K1/Fresh/public数量保持，public K16仍524请求/446成功/988判断，旧引用目标链仍54。

固定native父/候选640进程，每桶40对/20预定顺序块，双侧95%区间：K16 handoff wall减少为ARM1.79% [−0.12%,2.87%]、节省1.880μs [−0.140,2.963]；Rosetta1.99% [1.47%,3.07%]、节省3.287μs [2.396,5.078]。ARM尚不能确认收益；更严格的handoff增量减Fresh增量两架也均跨零。ARM Fresh K1约慢0.146μs的直接配对结果保留。public父比较另320进程，四桶吞吐区间均跨1，无确认变化；native无CPU计量，不将wall写成CPU收益。

原M5 Fresh/H4共640进程四桶全过；Fresh K16候选/M5为1.1026/1.1324，单侧98.75%下界1.0474/1.1053均≥0.98。原native320进程K1减少4.40%/3.89%、下界4.03%/2.42%仍不足20%；K16减少13.55%/14.50%、下界12.06%/13.98%仍不足30%。全部1920未插桩进程语义、加载库、退出及输入身份通过，未加样或修改门。旧/新selector比值差不是本次增量，以同期父库配对为准。

最终38个双架QTest为11116/0/0，另6原资源探针（每架31080 joint/28 publication安装区间零alloc/free、24 storage边界）；4个父红/新绿容量对照和4个压力fixture对照单列。87 TU/2211 APIs/28930逆边/27 callbacks、原结构/6工具检查通过；最终2315当前/1143 M5/1158父Git blobs及319运行/工具输入核对通过。中途旧全局压力测试出现两个“额度已释放少量”的准备失败，修复为原全局回收drain后重跑；额度/拒绝断言未放宽。数量汇总另发现一处非目标epoch地址复用的free缺失，两个160B记录继续标记寿命歧义；同一原始trace重析、不重采样，不推定其释放时点。原成功和失败全部保留。

本包确认并消除的是小额重复准备，不能承担M6主缺口。当前边际K16 Fresh/handoff为ARM124.614/107.240μs、Rosetta195.615/166.302μs；若Fresh固定，handoff仍需约20.01/29.37μs，若两边等量减少共同成本则需约66.70/97.91μs。这只是条件预算，不是置信结果或可删证明。剩余handoff准备中metadata publication32次/51456B、working16次/7424B及共同seal/commit314次准入/279次deref仍是待归因工作，不把容量/次数当时间占比。下一先补native独占CPU、等待及必要下界，证明足够预算后再实施。已完成借用/扫描/槽复用不重领，metadata驻留/CP0 required及M6–M8正式资格仍开放。

<a id="cp3-handoff-value-diagnosis"></a>
### 16.133 CP3：handoff成本、门槛可达性与真实价值诊断（2026-10-06）

用户要求执行下一步并深入判断30%门禁和handoff是否值得。产品保持`f0c40a5d195f1c20a0f915faaef18b1f3ee5b575`，生产改动0；[有限矩阵、统计、CPU归因和判断](evidence/br1_cp3_handoff_value_20261006/README.md)冻结50个语义/时钟检查进程、534个固定诊断进程和另行预注册的6个CPU采样进程。全部实际正常退出、reap、语义、加载库和输入身份通过；2315原源码hash/109原运行输入复核一致。仅证据目录的两TU诊断副本增加scope和“准备前拒绝handoff、走原安全Fresh”的开关，未改变产品选择或安全条件。

双架6种形状×3变体×12顺序平衡块，每进程8warmup+32测量。同样2个初始exact副本时，K16/B4 Preserve首写handoff延迟减少ARM16.93% [14.81%,18.77%]、Rosetta16.23% [10.67%,21.03%]；partial约19.60%/20.23%，完整输入约13.01%/15.44%，B16约24.66%/24.93%。这些是双侧95%描述性诊断，不是family或原40对门；初始状态效应不作产品改动收益。连续4次发布命中严格为16/0/0/0，累计优势降为3.64% [0.89%,6.01%]/5.20% [4.00%,7.07%]。旧alternate仍只恢复G0，不自动成为新G1的alternate；同段pending复用不属于每次重新handoff。

同状态512KiB provider预算下，K16/B4 handoff无新增payload并完成，现有双副本Fresh安全拒绝；普通单副本Fresh仍能在512KiB完成。容量价值成立，但不证明所有“先驱逐冗余副本再Fresh”策略不可行。若将专门制造第二副本的setup、验证、close/drain纳入完整synthetic sample，相对单副本Fresh反而慢25.92%/26.71%；不将该sample当实际stroke E。

CPU校准ARM约99.97%覆盖，Rosetta仅2.40%故不解释其CPU。逐段CPU时钟对handoff约32.5%扰动，保留并改用固定6条Running CPU采样；约3127个操作内样本按唯一fixture函数/内联lambda划界，setup/后台另计。ARM handoff CPU约101.64–104.82μs，其中beginWrite约40.57–46.59、seal+commit约49.08–59.09；handoff plan inclusive约27.44–34.88，内含metadata准备约9.85–14.20、accounting约5.16–5.98。阶段与机制、父与子不相加；短采样不是下界或可删量。metadata单项量级不足以合理承担原20.01μs条件缺口，尚无预算支持下一生产重写；不由此证明所有算法都不可能达到30%。

当前生产caller审查发现普通byte import和tiles3 clone只提供单authority；未找到传入独立readyAlternates集合的生产caller，首版发现条件只接受同generation/layout的Valid CpuRam副本。真实stroke自然正例与命中率p未建立，不能从fixture的100%推定业务价值，也不据此宣称任何未来provider都不可能命中。建议保留机会型handoff能力，先补真实来源/命中/拒绝与完整业务收益；30%可作为指定形状目标，缺少产品预算时不宜作为机制价值的唯一代理。此建议不修改§6阈值、不追认通过、不改变M6→M7→M8顺序。必要下界、metadata驻留、CP0 required及正式出口继续开放。

关闭态库校准有两个ARM production慢进程，置信区间很宽，全部保留，未声称诊断库严格等价。一次0ns drain导致比值分析失败、一次CPU内联符号识别失败，均保存原脚本和日志后重析原数据，没有重采样。原§16.132门结果继续裁决当前产品；本包关闭可达性/价值诊断，不启动无预算的容器试改。

<a id="m6-gate-revision"></a>
### 16.134 M6门禁与CPU/GPU价值口径修订（2026-10-06）

本次按用户明确要求修订活动合同，产品仍为`f0c40a5d195f1c20a0f915faaef18b1f3ee5b575`，文档起点`f3609018cf2d2265e5e779d839b3c03287f49fd1`。没有生产代码、benchmark规则实现或运行数据改动；旧证据包与§16.133以前的批次裁决保留冻结含义，不能把其中“原门保持”读成现行规范。现行M6判据只由[§6.1](#m6-opportunity-gate)管理，业务默认策略由[§6.2](#m6-business-value)及39管理，GPU条件预测由[§6.3](#m6-gpu-prediction)管理。

| 原判断 | 修订后 | 当前状态 |
|---|---|---|
| K1≥20%、K16≥30%是M6硬出口 | 保留研究目标；新同状态命中门要求各桶正收益的置信下界>0，拒绝路径及原控制要求完成吞吐下界≥0.98 | 新门未运行；原四桶失败不改写 |
| 预装双副本的收益代表业务收益 | 分开能力资格、自然producer/命中率、维护/退出成本及真实stroke端点 | 诊断首写16.93%/16.23%、四代3.64%/5.20%仅属原CPU描述性范围 |
| 省复制即可证明机制或整体值得 | 同时验安全、零额外copy、容量、miss成本、结构；产品再验完整净收益及交互预算 | CP2保留；metadata驻留≥25%分母与CP0 required继续开放 |
| GPU会自动放大CPU收益 | 自然跨域exact副本和显存压力可能提高价值；UMA alias、在途旧读和代际消费可能限制价值 | Vulkan执行未实现，GPU百分比/命中率/性能资格均未测 |

下一包为CP0/CP3新协议和来源清点，再在固定样本上验证；无足够可删成本证据不启动容器/provider重写。M6/M7/M8仍为0/3，persistent默认关闭，M6→M7→M8及BR1→后继production依赖不变。修改入口、性能合同、副本语义、领取/清点、代码/API索引和验证指南同批同步；[文档校验](evidence/br1_m6_gate_revision_20261006/verification.json)只证明文档一致性，不授予产品资格。

<a id="m6-opportunity-baseline"></a>
### 16.135 新M6门首轮基线与拒绝路径成本（2026-10-06）

产品仍为`f0c40a5d195f1c20a0f915faaef18b1f3ee5b575`，生产改动0；文档起点`1be6fd7623c06da12474dc9c6cfa535e46702b4a`。[事前协议](evidence/br1_m6_opportunity_baseline_20261006/protocol.json)与[冻结身份](evidence/br1_m6_opportunity_baseline_20261006/freeze.json)先于新样本：校准640、hit320、miss1280、固定M5 Fresh320、history320，加62个preflight，共**2942个运行进程**，全部正常退出并回收，输入/实际库核对通过；首次fixture编译错误发生于采样前，原失败保留。没有可选扩样、慢样本排除、阶段计时或profiler；arm64原生，x86_64为Rosetta。

同状态两边均有两个分别初始化的Ready exact副本。证据库只重编译一个复制TU，在`queryMutationBase`前禁用`discoverBefore`取得原安全Fresh，其余374个对象复用，原产品库不改。[完整结果](evidence/br1_m6_opportunity_baseline_20261006/README.md)区分同库比较与生产资格：

| 门项 | 本轮结果 | 裁决 |
|---|---|---|
| 命中四桶，各40对，单侧98.75%降幅下界>0 | arm64 K1/K16下降8.93%/18.80%，下界7.94%/17.26%；Rosetta下降7.82%/18.90%，下界5.63%/18.36% | 同库4/4通过；开关库等价未成立，暂不授予生产性能资格 |
| miss十六桶，各40对，单侧99.6875%完成吞吐下界≥0.98 | single3/4通过，Rosetta K1证据不足；native pin、generic lease、pending last-use十二桶吞吐损失9.57%～18.63%，上界也低于0.98 | 明确的同库拒绝成本，优先修复；不直接外推原生产精确损失 |
| 开关库正常选择/原产品等价校准 | 八桶40对，双侧99.375%区间要求包含于[0.98,1.02]；仅arm64 K1 single成立，其余七桶未建立等价 | 不是七桶证明开关变慢；不减校准均值、不放宽2%、不追加样本 |
| 原生产/固定M5 Fresh与H4 | 八桶全过；Fresh K16下界arm64/Rosetta为1.10157/1.12099，H4为1.39701/1.39814 | 两个原family独立成立，不依赖开关校准 |
| 安全、容量与代际 | 双库双架五组函数1832/0/0；512KiB provider预算下双副本handoff成功且无新copy，双副本普通Fresh安全拒绝，单副本Fresh成功；连续四代命中[16,0,0,0] | 有限子范围成立，不代替完整required、总进程驻留或真实stroke trace |

[源码审查](evidence/br1_m6_opportunity_baseline_20261006/source-audit.json)定位下一完整责任：`queryMutationBase`尚未先排除旧authority的pin/readLeases/pendingLastUses；`prepareHandoff`尚未利用已有binding锁排除reader/write state，直到后续`tryClaimHandoff`才拒绝。当前完整plan在最终claim前准备accounting、metadata和descriptor。拟从原权威状态提前拒绝明确不合格候选，保留最终nonblocking claim、identity/provider epoch/revision复核和原Fresh/cleanup；不新增第二owner、不放松安全或创建alternate。K16三类miss配对新增wall为arm64 16.875～28.063μs、Rosetta 28.979～44.739μs，是完整操作差而非全部可删的阶段成本。

下一独立协议先改善固定进程内有效测量时长/校准覆盖，再按同义hit/miss/原控制验证修复；本轮固定样本已结束。生产来源清点未找到传非空readyAlternates的caller，自然正例与业务命中率仍未建立。容量逐类live/reserved/peak及close尾存于原始样本；Store仍存活时metadata未归零，类峰值不能相加为全进程峰值。metadata≥25%重构前同义驻留分母、CP0完整required和适用构建仍开放；[门项清单](evidence/br1_m6_opportunity_baseline_20261006/required-matrix.json)不冒充完整CP0 census。**M6/M7/M8仍0/3，persistent默认关闭，无GPU或业务默认资格。** 新基线支持优先减少拒绝准备成本，不再以30%差值驱动猜改。

<a id="m6-early-rejection-delivery"></a>
### 16.136 已知handoff拒绝提前：机制兑现与实际收益（2026-10-06）

产品父`f0c40a5d195f1c20a0f915faaef18b1f3ee5b575`，最终`79e1c8d1ef`。[完整M1–M3/C1/V1–V2清单与结果](evidence/br1_m6_early_rejection_20261006/README.md)、[源码闭包](evidence/br1_m6_early_rejection_20261006/source-review.json)和[身份核验](evidence/br1_m6_early_rejection_20261006/verification.json)绑定本包。原metadata shard在发现alternate前排除已有writer与authority pin/lease/last-use，原binding mutex排除reader/write state，原plan把非占有physical观察放在before pin和冷存储准备前。生产4文件+30/−15、测试3文件+48/−1；没有新字段、公共API或owner。最终physical claim、provider epoch/revision、安装和原Fresh/锁外cleanup保持。

K16两架机制相同：generic lease与last-use的完整recoverable准备16→0；native pin的后续准备/安装尝试16→0，仍有原source观察和cleanup；hit的16次成功与single的零尝试保持。原测试同步覆盖释放后重试和晚到reader；busy时准备失败的tileReadCacheLifetime改为解除pin后重新prepare。完整38个QTest进程**11116 passed、0 failed、0 skipped**，6个原安装/publication/storage探针和原结构/6项工具自测通过；父库6个负控制102行预期失败，同一最终测试在候选全过。fixture漏include及首次四行旧重试假设失败发生于采样前，完整保留并迁移修复；没有据此替换性能样本。

[新协议](evidence/br1_m6_early_rejection_20261006/protocol.json)与冻结身份先于样本：父子1600、校准1600、hit320、miss1280、固定M5 Fresh/H4各320，加preflight92与独立机制40，共**5572个实验进程、550660条原始fixture样本**，全部正常退出/回收与工作/库身份通过。正式5440进程串行、无profiler/阶段时钟，固定40对不扩样；候选2500项输入及24项冻结文件一致。arm64原生，x86_64为Rosetta，不代表Intel原生或GPU。

| 结论层 | 当前结果 | 解释边界 |
|---|---|---|
| 原产品父/子实际增量 | 12/12个blocker桶吞吐增加10.68%～22.16%；在20桶family双侧99.75%区间中，这12个下界均>1 | family名义至少95%；不依赖证据开关等价。另8个hit/single控制区间含1，不把未显著当等价 |
| K16绝对收益 | native pin配对中位wall节省ARM28.906/Rosetta41.979μs；lease17.698/29.073μs；last-use18.771/31.677μs | 中位延迟差与完成吞吐分别报告，不把阶段次数当CPU比例 |
| 同状态hit | K16延迟降低ARM17.92%/Rosetta19.85%，单侧98.75%下界17.17%/19.03%；四桶均>0 | 生产资格仍受逐桶开关校准限制 |
| miss | 6/16通过；10桶不劣性证据不足，0桶明确证明超过2%回退 | K16 native pin点估计吞吐比0.98079/0.97369，Rosetta上界0.98356仍跨0.98，不把点估计作为失败证明 |
| 开关校准 | 4/20等价、16证据不足；点估计0.98797～1.01411，没有区间完全位于容许带外 | ARM K1 hit/single/pin/last-use过；不能跨桶借资格、减法校正或归咎未定位的某个环境原因 |
| 原生产Fresh/H4保护 | 固定同依赖M5八桶全部下界≥0.98 | 不替代新门miss、metadata驻留或真实stroke资格 |

本包已消除有机制和因果证据的多余准备；未证明所有miss满足2%。下一优先区分无改动控制的测量分辨率与native pin剩余source检查、beforeProvider引用和gate往返成本，先给合法删除/绝对收益预算再实施，校准按独立事前协议，不续采本包、不放宽门。metadata实际驻留≥25%重构前同义分母、CP0完整required、自然业务分布与M7/M8/GPU分别开放。**M6/M7/M8仍0/3，persistent默认关闭**；[门项差集](evidence/br1_m6_early_rejection_20261006/required-matrix.json)不冒充完整CP0清点，旧20%/30%原协议失败保留。

<a id="m6-provider-borrow-delivery"></a>
### 16.137 冷准备延后、已有provider借用与测量分辨率（2026-10-06）

产品父`79e1c8d1eff509e683c120df25861eb21512fb5f`，最终`38834c4e26`。[B1–B3/V1–V2完整清单、理论与实际](evidence/br1_m6_provider_borrow_20261006/README.md)、[源码寿命证明](evidence/br1_m6_provider_borrow_20261006/source-review.json)和[最终身份](evidence/br1_m6_provider_borrow_20261006/verification.json)绑定本包。原共同plan保留physical调用栈值，合格观察后才emplace其余冷Prepared；before与已验证source的provider id/epoch相同则借用原调用方强引用，foreign仍取得原ledger强引用。cleanup先reset physical，再释放before pin及冷存储，均在owner gate外；native/generic admission、最终claim、revision/epoch、安装和Fresh保持。生产1文件+19/−13净+6、测试1文件+28/−4，两个派生audit另列；无新公共API、持久字段或owner。

两架K1/K16的40个独立机制进程兑现预测：K16 hit额外before ledger lookup **16→0**，必要冷Prepared仍16；native pin额外lookup与冷构造均 **16→0**，原Prepare/Cleanup仍各16，成功install和其他早拒绝阶段不变。附加shared retain/release减少由删除返回值寿命推导，未冒称独立ref计数器或CPU占比。原安全fixture增加32个foreign before数据行，四BPP、generic Preserve/Discard和四终结；当前完整安全与计时后的冻结父库目标控制均通过，保证不同provider没有错误借用。

[独立事前协议](evidence/br1_m6_provider_borrow_20261006/protocol.json)每arm固定累计≥64ms操作wall及≥128个完成操作；每内部样本保持独立完整Store、exact副本、旧/新字节与close/drain校验。原库父子与校准仍分进程，同库hit/miss在独立进程内逐样本交替两arm、跨进程反转初始顺序；内循环不作独立重复。正式3680性能进程、preflight104、机制40合计**3824实验进程**全部正常退出/回收，正式3840窗口arm完成**9424983操作**、实际每arm最少190次。21冻结文件、2504候选输入、复制TU/镜像及各374复用对象一致，提交diff仍为实测patch。另有父库foreign合同控制2进程228/0/0，不计性能family；不追加样本。

| 独立family | 当前固定结果 | 裁决边界 |
|---|---|---|
| 原库父子增量，8桶双侧99.375% | 仅ARM K1 native pin确认+1.76%，区间[1.005179,1.029219]；其余7桶跨1 | family名义95%；K16增益未确认，跨1不证明等价 |
| 同库hit，4桶单侧98.75% | 4/4数值过门；K1减少ARM6.233%/Rosetta6.453%，K16为17.451%/19.283% | K16下界17.244%/19.188%；校准未过，不能授正式资格 |
| 同库miss，16桶单侧99.6875% | 16/16数值过门；native pin K16下界ARM0.983279/Rosetta0.980792 | K16配对中位额外wall仍1.8335/2.58325μs，不声称拒绝零成本 |
| 开关等价，20桶双侧99.75% | 仅ARM K1 single/last-use等价，其余18桶证据不足 | 全部区间包含1，无清晰非等价证据；联合校准hit0/4、miss2/16 |
| 原固定M5 Fresh/H4 | 两family各4/4通过 | 各自名义95%；当前累计产品保护，不是本包因果收益 |

理论可删数量已闭合，实际只确认一个小额增量桶；ARM K1配对中位节省约0.115μs为辅助估计量，K16正的中位延迟节省不能覆盖完成吞吐区间。新协议同时改变窗口与配对设计，miss从上一包6/16变成数值16/16不能全部归因代码；不能将不同批百分比相减或减校准偏差追认通过。分进程校准仍宽，当前不能区分镜像扰动与进程间环境变异，64ms并未独自解决资格问题。

当前完整安全38个QTest进程**11180/0/0**，6资源探针实际加载候选；87 TUs、2211 APIs、28983 edges、27 callbacks及原ratchet、6工具自测通过。原资源二进制继承并核验，不声称重新编译。下一先用独立同镜像无改动控制诊断校准、次序/慢变因素及完整wall分布，证明协议能分辨±2%后冻结新正式实验；没有已确认K16可删时间预算，不继续猜改provider/容器。metadata≥25%重构前同义驻留分母、CP0完整required并行取证；[门项差集](evidence/br1_m6_provider_borrow_20261006/required-matrix.json)不冒充完整CP0 census。**有限本包完成，M6/M7/M8仍0/3，persistent默认关闭**；旧20%/30%原协议失败、自然业务来源/分布与M7/M8/GPU/默认资格分别保持。

<a id="m6-calibration-resolution-delivery"></a>
### 16.138 跨进程计量分辨率：窗口改进兑现、完整校准仍开放（2026-10-06启动，10-07收口）

产品保持`38834c4e2612c819f9d088dfd59c59889f295a49`，文档父`43314f0443cec886f1afcf9bef8a85054e140840`。从§16.137的未闭合校准领取[有限D1–D4/F1/V1矩阵](evidence/br1_m6_calibration_resolution_20261006/README.md)，没有足够K16可删时间预算，不再按冗余数量猜改生产微路径。本轮生产/测试改动0、新公共API/字段/owner0；变化只在证据夹具、协议、分析及活动文档。

D1核验旧1600个校准过程的全部向量，存在8～20ms单次慢操作，吞吐比波动普遍大于中位延迟比；不能删尾、换成median门或把它们全归为OS抢占。D2固定768个过程，未改QoS的原库A/A仅2/8描述性区间落入±2%，异镜像也2/8；原主线程QoS33（user-interactive），显式user-initiated改成25，并非提高优先级，没有一致改善。D3固定384个K16过程，捕获实际QHashSeed并比较random/0；hit变异下降、native-pin不一致，不改生产哈希。三轮诊断区间均未经family调整，不授予正式资格。

D4事前固定768个过程，K1/K16×ARM/Rosetta×hit/native-pin，A/A/异镜像及64/512ms完整交叉；反转组次序和process左右次序组成6个平衡块。**16/16匹配组合的paired log吞吐标准差下降14.17%～86.32%，中位降幅48.35%；同轮描述性±2%组合4/16→12/16，A/A和异镜像各2/8→6/8。** 完整sample函数体、首写/seal/canonical commit及退出保持；只增加累计有效操作数。它证明计量改进方向一致，不是生产时间收益或正式family通过。

512ms仍有4个诊断组合未满足±2%：ARM K1 native-pin A/A [0.96722,0.99688]、ARM K16 hit异镜像 [0.98051,1.02812]、Rosetta K1 native-pin A/A [0.98457,1.03602]、其异镜像 [0.97990,1.01002]。均为**两侧95%诊断区间**，比正式20桶99.75%界宽松；边界差0.00010仍不四舍五入通过。两个相同原库控制也未证明等价，不能写成控制镜像的确定回退。具体CPU执行/锁等待/后台/调度仍未严格分摊。

[最终核验](evidence/br1_m6_calibration_resolution_20261006/verification.json)通过1920诊断+72预检共1992新过程、10982226有效操作向量、2504当前输入及1602旧诊断输入；内循环不是独立统计单位。当前11180/0/0安全、6资源及结构/工具证据继承同一输入，未重跑完整安全。首次QoS API签名编译失败及修复、全部原始日志/向量/命令/退出/两个加载镜像字节保存在[原始归档](evidence/br1_m6_calibration_resolution_20261006/raw-evidence.tar.xz)与[成员/SHA](evidence/br1_m6_calibration_resolution_20261006/artifact-manifest.json)。Store存活时close的metadata live不冒称已归零；销毁/drain完整执行。

**有限诊断包完成，完整计量责任未闭合，按事前规则不启动昂贵正式扩样。** 下一先对剩余组合做有界CPU/wall、等待/后台与慢变归因，验证实际分辨率后独立冻结完整20桶及匹配hit/miss正式family；不把512ms设成已合格正式协议、不借它追认旧64ms数值，不修改±2%/0.98或置信规则。§16.137正式校准仍2/20，联合hit0/4、miss2/16及原Fresh/H4八桶保持。metadata≥25%同义used/reserved/slack实际驻留分母、CP0完整required继续独立取证；[门项差集](evidence/br1_m6_calibration_resolution_20261006/required-matrix.json)不冒充完整CP0 census。**M6/M7/M8仍0/3、persistent默认关闭**；旧20%/30%失败、自然来源/业务分布、GPU及默认资格保持。

<a id="m6-execution-variance-delivery"></a>
### 16.139 CPU覆盖与执行条件：瓶颈重定位及配对编排实测（2026-10-07）

产品保持`38834c4e2612c819f9d088dfd59c59889f295a49`，文档父`a5bff4ea5bbbba58d453a01683b1e7fdfb56f828`。[有限矩阵及理论成本账](evidence/br1_m6_slow_operation_attribution_20261007/README.md)针对§16.138未分清的执行/等待/慢变领取C1/D1–D3及I1/V1，不重开已完成的allocator/扫描/槽复用/借用责任。生产/产品测试改动0，业务开关/API/字段/owner新增0。

busy/sleep校验确认ARM thread/process CPU覆盖正常，Rosetta thread CPU只覆盖约2.4%、无效，process约100%、有效但含后台；不能拿wall减无效thread CPU宣称大额等待。D1固定32过程/161087操作未出现预注册≥1ms事件，不加样到出现尾。旧D4全部768过程/769输入精确拆为median和mean/median形状因子，保留协方差；512ms极慢尾合并每架/K/case只占约0.034%–0.217%操作时间，单cell最高约0.278%，不能解释全部残差或改用median过门。

D2固定16过程/601409操作，前后32768步算术与CPU编号旁证；预注册全量Pearson判据仅4/16，不能宣布全部同步解释。D3固定32过程/654950操作，去掉CPU/rusage/reference，只在原wall外查询CPU编号，原timed work保持。**30个有两组同编号样本的过程均观察到0–5组中位比6–9组慢3.11–5.33倍，另2过程无0–5组。** SDK查询仅瞬时有效、同起止不保证中间未迁移；K1全部16过程两组存在，K16部分慢组仅1–2操作。后继有效当前原库K16 trace补出0–5 E Core、6–9 P Core标签，异构执行条件是变异来源之一；仍缺频率/缓存/外部负载的精确因果分摊，不能把差异全记为算法可删空间或由30/30虚构全局概率置信。

I1/V1事前固定192过程，四个旧长窗残留组合，原global与新local就地ABBA同期交叉；直接复用未插桩原seed probe、512ms、12pair/6块，完整输出/所有尾/预算/销毁/drain保持。**两策略均0/4组合的双侧95%诊断区间满足±2%；local在3/4组合增加paired log吞吐SD，另一组合仅微降。候选否决，不推广成正式协议、不扩样追通过。** 就地顺序块只保证共同线性漂移的理想抵消，不保证随机核选择、cache和process layout被控制；不删核样本、CPU归一化或扣镜像偏差。

P1两个固定3s trace中，K1累计5s操作目标超过原100000次安全上限，实际exit3，保留失败、不重录；只继续原已登记K16，实际49177操作通过。有效K16有493个明确API上下文Running样本，seal125/commit144仍为共同工作，不转换成精确μs或可删量；失败K1不授成本。source-only inline歧义归因修正保留原分析。独立helper的公开affinity接口返回46/not supported，SDK该接口也不保证指定CPU；不改产品或全局调度。

[统一核验](evidence/br1_m6_slow_operation_attribution_20261007/verification.json)确认2527冻结输入及769旧D4输入、相同timed work SHA；274/274测量过程和6188927操作通过，P1另计2尝试、1通过/1失败。[原始归档](evidence/br1_m6_slow_operation_attribution_20261007/raw-evidence.tar.xz)与[SHA/成员](evidence/br1_m6_slow_operation_attribution_20261007/artifact-manifest.json)保留全部向量/命令/退出/trace、原分析和实际加载镜像。本包不增加新的产品加速百分比或严格CPU理论下界。下一稳定并验证执行条件后再独立完整20桶及匹配hit/miss，不继续同义runner调参或无预算产品微优化；metadata分母/CP0 required独立补证。旧正式校准2/20、联合hit0/4和miss2/16、原Fresh/H4八桶保持；当前11180/0/0安全、6资源与结构继承同一冻结输入，不冒称本轮重跑。metadata≥25%同义重构前used/reserved/slack驻留分母、CP0完整required、自然来源/业务分布及GPU/default资格独立开放。**M6/M7/M8仍0/3、persistent默认关闭**；旧20%/30%失败不改写。

<a id="cp0-current-applicability-delivery"></a>
### 16.140 CP0当前普通业务基线、required责任清单与archive容量补证（2026-10-07）

产品起点`38834c4e2612c819f9d088dfd59c59889f295a49`，测试提交`128fb32a71`，文档父`bb479be2c085d8363f42d2ec5ceaeafd16d0fee8`。[本包](evidence/br1_cp0_current_applicability_20261007/README.md)沿§16.139独立推进CP0；没有生产改动或新的加速声明。当前库与之前已验证输入匹配，不延长旧计量包。

复用同依赖upstream及四个同字节夹具/资源，15个构建选项相同。四能力过程后，两架各24个独立配对、12个顺序平衡块，96个计时过程；全部100过程正常退出，300 QTest passed，像素/undo/redo/原callback/owner检查及实际加载身份通过。预注册块log latency ratio的当前/upstream几何均值：**stroke到projection-ready为ARM 2.258 [2.107,2.426]、Rosetta 2.318 [2.180,2.448]；undo 6.490/6.881、redo 7.688/6.482、owner teardown 2.183/2.089。** 方括号为端点独立、未经family调整的双侧95%诊断区间。total约1.000/1.011因setup主导，不抵消业务回退；不从不同批绝对时间计算本批收益，不倒算吞吐或授予visible/尾延迟/M/K资格。

下一业务成本账沿普通operation-wide写入、seal/private publication和canonical commit，以及history restore/index/projection边界核对实际重复与必要冻结。达到upstream时间需要约55.7%/56.9%的stroke目标降幅，但这只是目标距离，不是已证明可删预算。stroke优先于绝对时间较短的undo；普通路径仍非persistent opt-in，不因此自动启用默认或跳过M7/M8依赖。

[required执行清单](evidence/br1_cp0_current_applicability_20261007/required-census.json)落实31个合同组、15个源码文件、8个实际测试日志，以及已有校准20/hit4/miss16/Fresh4/H4四组共48数值桶；保留各组consumer、测试方法、实际PASS行、阶段及缺证。它是可执行追踪清单，不是全交叉组合/全部formal协议完成，完整CP0仍开放。清点发现archive原例仅注入写失败；现保留ample原场景，新增1/4/8/16 BPP一页实际byteBudget耗尽，第二代拒绝后旧archive整页/current/retained View保持，forget后同owner重试及全页内容通过，最后records/retention清理。两架完整Reference各946/0/0，合计**1892/0/0**；测试1文件+61/−5，生产0。不授物理磁盘满/全进程SSD压力或SSD alternate能力。

[metadata分母审计](evidence/br1_cp0_current_applicability_20261007/metadata-denominator.md)明确footprint used、map/index capacity和arena block之间的重叠/缺口，未取得可同义重建的重构前used/reserved/slack分母，≥25%仍未测。旧生产11180/0/0、六资源、结构和Fresh/H4八桶保留各自证据，未重跑；新1892不相加为完整矩阵。原正式校准2/20、联合hit0/4和miss2/16保持，**M6/M7/M8仍0/3、persistent默认关闭**。

<a id="business-cost-localization-delivery"></a>
### 16.141 普通绘画实际成本定位：projection作用域与session数量反证（2026-10-07）

产品`128fb32a71fef69f462da2c2dfa8d187ed94db52`、生产仍同`38834c4e26`，外层父`875f364b77c5667f0c2ca85bc68bc245b35f3ef3`。[本包](evidence/br1_business_cost_localization_20261007/README.md)完成诊断，没有产品改动或加速声明。原matched业务只在计时外加阶段signpost，ARM双方能力2过程后固定current/upstream/upstream/current各64完整replay；四trace各阶段64完整区间。再固定普通/已有opt-in/opt-in/普通四过程读原累计计数。10夹具过程、262语义replay、30 QTest passed，四profiler亦正常退出、全部reaped；不把内部replay当独立性能样本，未重跑完整产品矩阵。

Stroke区间Running样本当前1084/1097、upstream468/512；互斥画笔上下文当前626/619、upstream363/382，projection当前299/308、upstream25/46，后台history/retirement与调度另列。当前projection约27.6%/28.1%样本，**不是可删CPU或wall比例**。源码确认clear→fillRect与合成→writePageStoreOperation分别准备和seal；匿名并发client原来已合并部分canonical commit，不能简单称每个操作都根发布。普通stroke本身也已共享history transaction。

实际去重计数：node的operation session普通27→opt-in1，但两者页代际准备/seal均76、默认初始化56、native duplicate20、写pin2420、canonical commit1；root projection在四次都为session32、页代际149、默认初始化60、native duplicate89、pin245，commit12/14受并发分组影响。root占两manager的66.2%代际和81.7% duplicate页；89页为1,458,176 B逻辑复制，preclone hit0。两manager合计225代际、116默认初始化、109复制和3,686,400 B初始化/复制工作未随opt-in减少。**仅减少session不是本例页工作减少的证据。** 计数只覆盖仍存活manager；profile后续replay暖cache，不混入§16.140统计。

下一优先责任为原projection merge单元的clear→composite作用域：按各操作页集合与必要冻结/读者/独立失败边界核定可共享并集，再考虑原owner借用与统一交付。不得把全部89复制或149准备直接算为可删；旧读隔离、重叠页并发、部分页、预算拒绝、dirty cut、取消和晚释放保持。[候选位置/验证矩阵](evidence/br1_business_cost_localization_20261007/README.md#下一包位置与验证矩阵)已列；2420次画笔pin仅列第二候选，未取得足以据次数开启cache重写的独占时间预算。热点定位证据较强，可删量/实际收益仍待因果验证，不编造概率置信度。

两次分析分类修正均保留旧版本并重读原trace，机制fixture一次缺include编译失败也保留；无运行换样。旧生产安全/资源/结构、Fresh/H4及§16.140 Reference保留各自冻结资格；本包不增加正式桶通过。正式校准2/20、联合hit0/4和miss2/16、metadata实际驻留分母与完整CP0缺项保持；**M6/M7/M8仍0/3、persistent默认关闭**。

<a id="projection-redundancy-delivery"></a>
### 16.142 Projection可删量兑现：稀疏default clear与净收益估价修正（2026-10-07）

产品父`128fb32a71`→`2f22452e2dc76dca3e60c6231783534f44716ce4`，外层父`2a94f65dd`。[本包](evidence/br1_projection_redundancy_20261007/README.md)完成诊断、修改与有限验证。原merger/backend/PageStore三TU的低扰动v3恢复本例19更新、root149准备/89复制/32session；各merge成功准备页并集共96，clear→composite直接source链53。若合法共享完整merge写入责任，条件上限为53准备/复制、868,352 B和13clear session；读者冻结、独立失败与并发合同未联合证明，不能称已可删53。

其中17条clear没有native source，逻辑默认页被部分清为同值属于空操作。原fillRect只检查整页，本次把default判定扩到部分页，在既有managed range、固定before及原adapter/失败边界下跳过实体化。没有新增owner/API/锁/缓存，[完整迁移矩阵](evidence/br1_projection_redundancy_20261007/README.md#实施与验证矩阵)已结算。四过程parent/candidate/candidate/parent完全兑现事前数量：root代际149→132、复制89→72、pin245→228，默认初始化60/session32保持；node76代际/20复制/2420pin保持。两manager准备225→208、复制109→92，逻辑复制−278,528 B；不是DRAM流量。产品3文件64增/3删，其中生产8增/3删、测试56增。

原时间预测把17个clear及后继composite准备CPU合计0.322833/0.312337 ms当净预算，**估价偏高**：必要default初始化移到composite，合计116页初始化仍在，不能删掉两段准备。事后修正不覆盖原计划/输出：若必要初始化单价相同，净准备约为原17个duplicate的0.085166/0.081504 ms，均值0.083335 ms；关键路径25%/50%/100%且其它成本不变时wall约0.254%/0.508%/1.017%，另扣新增resolve，seal/回收/等待变化未定价。它是条件模型而非CPU实测删除或95%置信区间。全53重复composite准备均值0.418334 ms、100%关键路径约5.10%；剩余36条约0.335 ms/4.09%，仍需合法共享和净成本证明。projection28%样本从未成为可删时间承诺。

未插桩同一原业务程序：四能力+两架各24对/12顺序块，共100过程全部像素/callback/owner/身份通过，20,000块bootstrap/seed261018、pointwise双侧95%。ARM stroke candidate/parent **0.992888 [0.974041,1.013705]**，降幅0.71% [−1.37%,2.60%]，48过程均19更新；Rosetta **0.988387 [0.958566,1.026803]**，降幅1.16% [−2.68%,4.14%]，parent/candidate各3/5过程为18更新，全部保留，不能纯归因。主端点均未确认正收益。ARM setup比1.013348 [1.000124,1.033665]保留变慢信号，未作7端点family校正；total比1.011825 [0.999354,1.030471]跨零。其它次端点跨1，不用setup主导total宣称stroke改善，不续采到通过。

新增四BPP×history开关8行稀疏洞/非零默认/非default填充/旧读/边缘/undo-redo反例，在parent库8/8预期失败；候选完整manager、merger、Reference双架**4554/0/0**。首批merger缺blur插件SIGSEGV保留log/IPS/退出，修正runner插件目录后只继续剩余五过程。结构21manifest/25ownership/16census/2211 APIs/29025 edges/19intrusion、六工具自测通过；原固定M5 Fresh/H4各四桶40对重验，640过程、**8/8不劣性通过**。旧全安全11180/0/0与6资源仍属原冻结版本，不冒称本包完整重跑。

全部构建/加载/插桩扰动失败、成本模型旧输出、原样本和实际镜像见[归档核验](evidence/br1_projection_redundancy_20261007/verification.json)。本包保留为确定的稀疏页工作消除，不能包装成显著业务加速或M6主解。下一先判断剩余36条共享责任是否在原合同下净值为正，预算不足或语义不成立即转向画笔准备/其它projection结算的独占成本。正式校准2/20、联合hit0/4、miss2/16、metadata实际驻留分母与完整CP0保持；**M6/M7/M8仍0/3，persistent默认关闭**。

<a id="structural-cost-attribution"></a>
### 16.143 upstream大差距的结构归因与优先级纠正（2026-10-07）

产品仍`2f22452e2dc76dca3e60c6231783534f44716ce4`，外层父`5da3a9adf`。本包只重读§16.141四个固定64 replay的原选栈及当前/upstream源码，没有新性能过程、产品修改或新阶段资格。普通stroke ARM2.258/Rosetta2.318倍的时延区间仍属§16.140独立批次；旧profile属128fb32a71、生产同38834c4e26，不能冒称2f224实测。

对称分类修正：原规则漏认KoStreamedMath/OverCompositor内层像素kernel，被外层adapter遮蔽；当前117/106个原adapter样本转回pixel，upstream也分别纠正6/5个。原actor与总量、所有样本及区间不变，旧输出保留。重算互斥Running类别：当前两次pixel347/342、管理协议上下文507/524、heap144/131、其余86/100；upstream为pixel277/303、管理协议10/11、heap77/77、其余104/121。协议上下文还含copy/fill叶76/92、同步原语150/161、其它协议叶281/271，upstream对应2/4、3/1、5/6；不是纯控制指令，同步原语也不等于已定价CPU/等待。管理均值差505/总样本均值差600.5=84.1%，**仅描述样本差的分布，不能换算wall归因、可删百分数或置信区间**。旧adapter199/180不能再作为纯管理预算，actor定位及persistent反证保持。

更深核心是普通同步CPU写入承担了逐operation目标集合重建/规范化、范围准入/执行准备和adapter交付，逐新代际的通用provider/metadata/预算/completion协议，以及逐访问的guard/pin借还与最终寿命结算。upstream主要在原tile/accessor上保留保护并按共享状态触发COW。新增预算、版本/读者隔离、物理身份和晚free合同确有必要，但同一事实的跨层重表达、原owner寿命未传到下层持续复用，是实现粒度问题；不是把合同全部删除，也不是引入第二CPU账本。

已有persistent把node session27→1，但76代际/20复制/2420pin不动，canonical commit原本就1；证明仅复用会话没有覆盖完整数据路径。backend按row/column排序、borrowExecution按column/row重排，原v3各19个root composite范围有11个不同序；borrowExecution非const局部数组迭代还会detach共享输入。这些是同一结构问题的具体症状，未定价，不单独领取const/排序补丁作为主解。§16.142合计代际225→208仅降7.6%，必要初始化116页保持；17页条件净预算约0.083ms无法解释主差距。

下一优先责任改为**原同步CPU写入完整的准备—使用—交付**：分first-touch、同页暖复写、必要capture后复写核定合法段G、首次写页D、必要cut与保护重取R，比较原plan/admission、资源记录、pin/lock、实际delta交付及终结尾的数量和独占成本。保留独立失败、旧读、并发writer、预算/pressure、显示和物理free；不通过禁用计账/锁/COW做消融，不先泛化cache。余36条clear→composite的0.335ms条件准备预算降为该完整责任的子项，不再自动作为下一主包。

“共同管理协议是主要额外执行上下文”有较强采样/源码/数量交叉证据；“责任粒度与表示/寿命不匹配”有强源码证据；可删总量与最终业务收益尚无可靠区间。回到upstream量级所需约55.7%的当前stroke降幅只是代数目标，不是已证明空间。完整清单、理论模型、对称纠正与冻结输入见[结构归因证据](evidence/br1_structural_cost_attribution_20261007/README.md)，位置见[CODE_INDEX](br1_modification_guide/CODE_INDEX.md#structural-cost-attribution-code-index)。正式校准2/20、hit0/4/miss2/16、metadata分母与完整CP0缺项保持；**M6/M7/M8仍0/3，persistent默认关闭**。

<a id="cpu-write-blueprint"></a>
### 16.144 CPU写入的不良路径、理想算法与实施蓝图（2026-10-07）

产品仍`2f22452e2dc76dca3e60c6231783534f44716ce4`，外层父`c21d9896b`。本轮交付[03c详细蓝图](br1_modification_guide/03c_cpu_write_execution_blueprint.md)、B1–B12迁移/删除/验收矩阵及[可复算证据](evidence/br1_cpu_write_blueprint_20261007/README.md)，未修改产品、未新跑性能或增加正式资格。

纠正§16.143的解释边界：`prepareWrites`已跳过已有`bound.page`，`beginWriteImpl`暖命中已跳过全局冷plan/provider路径。两页重复1/10/1000次仍只准备两页、checkpoint后改一页累计三页的既有测试也支持这一点，本轮未重跑。session27→1而76代际不变不能证明暖复用失效；普通canonical commit也不是每dab一次。真正确定的重复是目标范围跨层重表达、异序排序/非const detach，以及固定源dab交错页导致原单页guard反复借还。

确定的首个实施方案：同一原operation中，保留全冷页准备、job/显示/cut/提交边界，将固定不可变源的**原kernel矩形**稳定按目标页分组。每页内dab/clip次序和重复clip次数保持，源参数逐片段重设；同时最多pin一页。范围由原manager规范化一次，下层const借用；原BoundEntry完成唯一有界查验，删除cursor重复contains。没有第二owner、全页pin cache或每页一个job。首版无wrap/selection，未知跨页依赖保持原路径；原adapter、错误终结、预算与实际free保留。

令P为operation实际不同页数，R为旧页序列连续段数，C为冷preflight pin，E为必要中途让出；目标pin由`Σ(C+R)`降到`Σ(C+P+E)`，新增片段计划/容量/释放必须扣除。代际、payload复制/初始化、completion ticket、job/operation/checkpoint/canonical commit的预期变化均为0。**仅当完整trace核定全部2420次相关pin都适用、ΣC=ΣP=76、E=0，才有2420→152、删2268对的预测**；现有76代际不能证明这些前提。以冻结CP0的8.103ms作示例，新增计划0.1ms、每对0.25/0.5µs、关键路径系数1时，对应5.76%/12.76%；不是当前实测或置信区间，不能承诺追回55.7%差距。

另确认一个通用协议的结构模型：同source交错分配短readiness与长retirement时，N次串行成功准备、尚无retirement完成将保留2N−1个interval；按寿命分source可降到N，但两边仍分配2N次interval，另增一个source记录。它揭示完成序列寿命干扰，尚无真实峰值/独占时间，**不纳入B1–B8必改清单**；若以后实施须在原Registry闭合原子注册、失败ticket及原provider所有consumer，不能删掉readiness或retirement事实。

30组独立逐像素顺序模型保留原kernel矩形，反转同像素次序的负控制被检出；四页反复构造为400→4，同页100dab为1→1、稀疏16页为16→16。模型不是实际Krita compositor/资源/性能验证。下一先按03c §9有限采集真实序列和价格，再完整实施B1–B8并执行B11/B12；不能把单独const/sort微改报为方案完成。阶段状态、metadata分母、完整CP0及正式校准缺项不变，**M6/M7/M8仍0/3，persistent默认关闭**。

<a id="cpu-write-execution-experiment"></a>
### 16.145 CPU写入蓝图完整候选：数量兑现、业务收益未确认并回退（2026-10-07）

产品父`2f22452e2dc76dca3e60c6231783534f44716ce4`，外层父`fa18481b472f349cccd983fd06f68d6dfa8984c8`。完整候选`f9714b4d31`保存在本地`codex/br1-cpu-write-ordered-experiment`；工作分支回退提交`fb57b8b69be74a38602fb2f0cd1c6e4374b843e3`与产品父的Git tree完全相同。**本批没有把未确认收益的新增实现留在主线，也没有留下仅const/sort的半包领取完整优化。** [实施证据及全部失败](evidence/br1_cpu_write_execution_20261007/README.md)、[03c §11](br1_modification_guide/03c_cpu_write_execution_blueprint.md#11-完整实施后的理论实际比较与取舍)记录实际实现、有限实验与取舍。

候选完成B1–B8的原fixed consumer闭包：真实scalar/SIMD RGBA8 OVER独立固定源、无selection/wrap；私有PaintDevice/strategy/transaction桥共用原target/mapping复验；原manager形成一次canonical范围，原prepareAdapter hook内实际收费的计数/前缀和/稳定填充，全部冷准备后按页消费。原kernel矩形、dab/clip次序与重复clip、opacity/flow/隐藏RGB、单guard、owner、job/patch/cut、联合交付及物理free保持。QSet/values/native数组重表达、异序排序/非const detach、BoundEntry多余重排、cursor contains同批删除。未知同名`over`继续原序；R=P不建片段buffer，但计数/offset成本仍在。

前置四过程与后置四过程均核定27个operation，ΣP/R/F/C=76/2344/5363/76。候选R降76、F/C不变，E=0，总pin **2420→152，精确删2268对/93.72%**。node代际/复制/初始化76/20/56、operation/session/canonical commit27/27/1保持；root132/72/60/228pin、19projection更新保持。root canonical commit随原并发client归并波动，parent12/13、candidate12/12；初版分析器误将前置11作常量而失败，修正后只分析原四过程，不换样或领取commit删除。最大单operationF516/P4，有效计划容量界12416B；实际费用走原store allocator，真实超预算拒绝保留已有pending并可重试。ordinary/opt-in各一次诊断最长单页body pin62.750/62.625µs；单pin/压力/swap等原边界保持，不外推为压力尾界。

两架各24配对、12平衡块，共96未插桩业务过程及4能力过程，原stroke-to-projection-ready端点、20,000块bootstrap/seed261019、pointwise双侧95%。**ARM延迟减少0.276%[−2.150%,+5.859%]；Rosetta1.400%[−1.495%,+2.341%]，均未确认收益。** pen-up、undo、redo、teardown同样跨零，不相加。独立R=P负控制另96过程，四桶均未确认改善，ARM单页点估计慢4.599%[−7.016%,+0.333%]。其v0两过程因夹具漏资源初始化、输入hash不一致停止；修正确定像素字节与原资源初始化后独立重开固定完整批，失败保留，不续采至通过。

候选两架最终选定用例9470/0/0，原结构阈值保持、2214 indexed APIs/29079 edges、6工具自测通过；原固定M5 Fresh/H4两family×4桶×40对共640过程，单侧98.75%吞吐下界均≥0.98，8/8过门，**它们是保护资格，不是本轮增量收益**。PaintDevice原memory-fragmentation stress在候选与冻结parent均因跨页worker拒绝后memcpy空指针崩溃；最终枚举其它全部方法，失败/崩溃栈保留，不授该stress或完整PaintDevice组通过。回退构建/相关验证与实际源绑定另见证据，不能把候选9470移作回退后的当前计数。

回退后两架同一选定范围9402/0/0，原stress仍排除；构建成功、实际Ninja no-op，结构恢复2211 APIs/29025 edges及6工具通过。冻结common库回放parent/candidate两过程仍复核2420/152及同像素，仅作回放能力、不加入原性能样本。候选生产19文件+390/−59、测试4文件+271/−27，主线上层public/protected净增长0，无新owner/队列/锁/TLS/长期字段。每个桥有消费者仍不证明整体复杂度值得；本case未给其业务收益依据，故完整回退，有限包结算。数量模型成立，`Δwall≈α·((R−P−E)c−A)`中的独占单价、新准备成本和关键路径映射仍不能由次数反推。该结果否定“高pin次数足以解释整笔大差距”的推断，不等于没有实际瓶颈。未变的208代际、92复制/116初始化及完整冷provider/metadata/预算/ready+retire登记、联合交付和真实退役是下一计价责任；不凭旧sample百分比或两ticket构造模型开改。**正式校准仍2/20，metadata驻留分母、完整CP0仍欠；M6/M7/M8仍0/3，persistent默认关闭。**

<a id="upstream-cpu-cost-accounting"></a>
### 16.146 upstream差距的CPU时间账与默认填充因果校准（2026-10-07）

产品`fb57b8b69be74a38602fb2f0cd1c6e4374b843e3`未改，外层父`c00b3ae965`；upstream沿用`9a24ae0d8c070884fb013594191002e1a1b39a19`。[本包](evidence/br1_upstream_cost_accounting_20261007/README.md)以原真实RGBA8、4 workers、8 segments/4 callbacks、19 projection updates和全部像素/undo/析构端点建立CPU账。先前完整pin候选仍回退，不借计数恢复该方案。

ARM原库固定8配对16过程，stroke wall当前/upstream边际中位7.946/3.848ms，CPU18.232/8.725ms；配对差中位分别**4.208/9.233ms**，8对均为正。这是描述性新批次，不能与旧约2.3倍批次相减报收益。jobs-only两侧各两过程均为937 stroke+19 merge任务，CPU均值差**画笔3.856ms、projection4.654ms、未被job覆盖1.412ms**；三项为该批互斥CPU账，非wall/可删份额。当前累计job非执行时间8.24～8.33ms，upstream0.89～1.40ms，线程间重叠，不当锁等待或加到wall差。

完整诊断按父子相减：冷代际3.93～4.12ms CPU，private seal0.98～1.07、canonical commit0.66～0.77、operation/adapter/交付1.11～1.18、prepare循环残差0.11～0.12，合计约7.02ms观察CPU，包含必要工作与扰动，不全授可删。独立v2核定当前208代际=116默认fill+92额外复制，upstream写锁COW116次均为真实整页memcpy、preclone命中0；两侧首批页stroke/projection均56/60。额外92个代际的当前合同必要性尚未核定，116不是当前合法下界。

原库反汇编确认默认页fill每页4096次外部memcpy；当前116页循环CPU1.062～1.127ms，对比upstream116次整页memcpy0.051～0.054ms。当前额外92次memcpy只有0.0635～0.0638ms：数据移动不是复制次数所暗示的主成本，代际连带协议和首次初始化方式都必须计价。冷准备v2还核定登记/pin/验证/安装约1.00ms、prepareBase约0.45～0.48、backing预留0.32～0.38、provider身份准备0.35ms；这些是有观察扰动的合并区间，不能据此直接删权限或ticket。

在独立实验库把原等量fill改为一次pixel加倍增块复制，每页4096→13次调用。父/实验能力通过后固定24配对/12块48过程，无内部观察器，20,000块bootstrap/seed261021、各端点pointwise95%。**stroke wall减少6.564%[3.634%,9.082%]，CPU减少5.237%[3.672%,6.644%]，配对中位省0.597ms wall/1.123ms CPU**，符合事前约1ms CPU数量级。redo wall减少33.05%，原诊断有56次fill；**undo wall反而慢6.313%[−12.516%,−0.849%]（配对多43µs）**，原undo无fill调用，跨阶段/布局/调度/统计原因未区分。保留负控制，不升为生产，不以主端点收益掩盖回退。

共88业务过程/264 QTest passed、两观察器方法自检；库/像素/回调/退出核定，原相关大矩阵/原stress/Rosetta/正式门未重跑。内部观察带来明显扰动（当前CPU mode0/jobs/完整/v2均值约17.58/18.88/19.62/20.74ms）；只把原库和独立fill批授增量时延证据，其他层仍是粗价。原源码/头/布局/预算未改；实验库、差异、原始失败与全部结果独立冻结。

冻结核对发现fill过程38为18次projection更新，其余87过程为19；保留全部48主样本，不能称全部内部工作量相同。事后排除该整个四过程平衡块的22配对/11块敏感性仍为stroke wall减少7.061%[3.928%,9.599%]、CPU减少5.610%[4.070%,6.937%]，正向结果不依赖此例；敏感性不替代主结果或独立验证。undo wall敏感性区间跨零，主批回退仍需解释。保留冻结v0失败及原分析，未换样或扩样。

当前结论是**成本集中于两个业务责任，并含多层协议与高单价默认初始化，不能再概括成只有均摊维护**。fill只解释部分差距；主责任仍为projection冷准备—交付，先证明额外代际和多层记录的合法可删量。约1.4ms额外CPU未覆盖、body内kernel/暖访问及真实锁/关键路径仍开放。填充产品化先解释undo和补格式/边界/原控制，不用6.6%局部收益关闭upstream目标。**M6/M7/M8仍0/3，校准2/20、metadata分母与完整CP0未完成，persistent默认关闭。**

<a id="cpu-cost-calibrated-blueprint"></a>
### 16.147 用量化报告修订理想路径与预测（2026-10-08）

产品仍`fb57b8b69b`、源码树等同`2f22452e2d`；外层父`732dfee416bd5fbc203c3f1a80a710763b1ede47`。本轮将§16.146冻结证据落实为[03d修订蓝图](br1_modification_guide/03d_cpu_cost_calibrated_blueprint.md)、[项目复制粒度经验](br1_modification_guide/CONVERGENCE.md#copy-granularity-lesson)及[可复算预测](evidence/br1_cpu_cost_blueprint_20261008/README.md)，没有产品/测试改动或新业务测量。原03c事前设计及回退结果保留，修正指南仍称其“待实施”的过时导航。

确定方案A在原`fillWithPixel`内seed+倍增，116页请求475136→1508，少473628（99.6826%），初始化写入字节和版本/交付合同保持。收益预期从未定单价改为已有ARM实验校准：约1ms CPU、约0.6ms stroke wall；原主批降低5.2366%/6.5637%及各自95%区间只属于原实验，不是下一批预测区间或产品资格。undo主结果多43µs、一例projection更新合并及事后敏感性均保留，产品化先解释负控制并补格式/边界/原控制。

结构方案B继续覆盖投影冷准备—seal—commit—adapter原owner闭包。208对116、projection132对60均不是合法可删数，先按first-touch、reader/freeze、失败/交付cut证明删除集合，再以分支匹配的互斥成本减新增表示/复验/释放；A/B重叠与交互另计。约7.02ms诊断CPU不是全可删预算，额外92次memcpy仅约0.064ms也不能代表其连带协议价格。尚不能承诺再降20%/30%或回到upstream。

新基线2.028102倍的代数量级对应约50.69%当前wall降幅才到同一参考upstream，替代旧批次55.7%的规划分母；不是新门阈值或正式置信结论，不将独立fill批与旧baseline拼成新实测比值。实施矩阵与有限退出在03d；**M6/M7/M8仍0/3、校准2/20、metadata分母和完整CP0未完成，persistent默认关闭。**

<a id="projection-cost-attribution"></a>
### 16.148 投影CPU责任、代际来源与必要维护成本（2026-10-08）

产品`fb57b8b69b`未改，tree仍等同`2f22452e2d`；外层父`3e97333c79c22dbc5306233c288dc693fe0add69`。本包按§16.147/03d深化投影归因，[完整报告/协议/数值](evidence/br1_projection_cost_attribution_20261008/README.md)、[源码](br1_modification_guide/CODE_INDEX.md#projection-cost-attribution-code-index)和[蓝图更新](br1_modification_guide/03d_cpu_cost_calibrated_blueprint.md#projection-quantified-refinement)保存初始有限矩阵及一次独立判别追加。无产品补丁，不领取优化收益。

对称粗观察固定四配对，当前/upstream投影CPU均值5.322/0.583ms，差**4.739ms**；其中composite差**3.584ms（75.63%）**、clear差**1.151ms（24.29%）**，其它互斥外框净差约0.004ms。各对差均正、范围4.330～5.238ms；份额只属于诊断CPU，非wall、可删份额或概率置信度。95次composite中76次无观察到的像素写入仅约0.04～0.05ms，非主要差距。

两个详细及两个追加current均通过page/source→target generation核定：**132=56个不同页首次fill+4次整页default移除后fill+36次后续merge clear复制旧投影+36次同merge composite复制clear结果**。clear页分支36 partial/4 removal/22 skip；原13 clear+19 composite共32个mutation batch，匿名transaction共享不复用已seal的pending。后36条整段冷准备约**0.469～0.491ms CPU**，memcpy只约0.022～0.023ms；若完整共同owner方案合法且其它量不变，才有132→96/copy72→36/fill60不变的条件预测。新价替代旧0.335ms规划价，不把不同观察批次价差当回退。

追加原base查询已有事实：72个copy源均单replica、独立recoverableBefore无效，60 default为虚拟页；同merge源可为Published或Prepared，取决于真实匿名client归并。页级captured全为0不代表无旧reader，epoch root retention独立保护旧选择，clear自身有before快照。不得据此原位改已发布页或推定自然handoff收益。

当前投影v2互斥CPU：冷准备2.25～2.41ms（含payload），seal+commit1.15～1.18ms，operation/batch/adapter0.56～0.74ms；其余落入clear、source捕获、manager与bitBlt外框。source 37次捕获=18 overlay+18 before+1 committed，overlay约0.20～0.22ms、before仅约0.04ms；原约1ms外框残差不再全部叫adapter。数据支持“独立写段反复付冷协议与终结、必要代际本身也有多层维护”，不能用删除36次copy代表主差距已解。

共**21业务过程/63 QTest passed**，实际库/像素/回调/undo/redo/析构/退出核定，全部19更新；17个有事件过程的投影矩形多重集合一致。父子互斥账与标签检查通过；构建脚本两次上下文歧义及分析器一次迭代器消费错误均保留，未换样。详细观察有扰动、样本有限，不产生新正式CI、纯kernel/锁价或wall预测。未跑Rosetta、产品安全大矩阵和正式M6。**M6/M7/M8仍0/3，校准2/20、metadata分母及完整CP0开放，persistent默认关闭。**

<a id="bulk-fill-implementation-delivery"></a>
### 16.149 批量填充实施、pin寿命修复与未通过的负控制（2026-10-08）

产品父`fb57b8b69be74a38602fb2f0cd1c6e4374b843e3`，外层父`88662bce446ae3ece7078b03652b80237dea542d`。[完整实施/所有失败/有限协议](evidence/br1_cpu_blueprint_implementation_20261008/README.md)、[consumer与生命周期账](evidence/br1_cpu_blueprint_implementation_20261008/IMPLEMENTATION.md)、[03d矩阵](br1_modification_guide/03d_cpu_cost_calibrated_blueprint.md#bulk-fill-implementation-result)区分候选和当前源码。完整填充候选`725fe331af259e9fabc18625be547893cad2c1c5`保存在本地`codex/br1-bulk-fill-candidate`；当前原分支`a918e45e028c426874d9aa13d8080f2d69170d9f`只保留确定性pin修复及oracle，第一版修复为`751bceff23`，**未将填充优化升为默认实现**。

方案A在原private默认构造内seed+倍增，实际ARM/x86汇编均核定每页4096→13 memcpy调用、字节量保持；116页条件下少473628次请求。无新owner/字段/API/锁实例。双架九BPP×零/非零、偏移源/隐藏字节/源寿命/独立页/真实分配复用覆盖通过。24配对同布局仅fill对照，stroke wall下降**6.30% [4.10,8.34]**、CPU**5.53% [3.47,7.39]**，配对节省中位0.514/1.111ms，支持约1ms CPU预算；完整静态候选另24配对下降**7.88% [5.87,9.87] / 6.99% [5.04,9.08]**，包含pin修复，不能全归fill。

完整候选index26为18更新，其余47个19更新；主结果保留，移除所属整个ABBA块的事后敏感性wall7.63% [5.54,9.77]。同布局批全部19更新。所有区间pointwise双侧95%，未调整端点family；Undo仍含可观回退，完整候选wall区间−11.30%～12.04%、CPU−9.99%～11.92%，配对中位多17/11µs，Teardown也未获非劣证据。原定有限批已结束，**不因“不显著”宣告等价，不追加到通过**。候选Fresh/H4各320过程、两架K1/K16的八桶按原单侧98.75%规则全部通过，不能替代真实负控制。

完整候选直接对固定同依赖upstream8配对/4块，stroke wall仍**2.055倍 [1.928,2.215]**、CPU**2.011倍 [1.911,2.121]**，额外配对中位3.885/8.803ms；不拼旧baseline与新局部收益。它支持“一个约1ms项可消除，但主差距仍在”，不是完整CP0或GPU资格。本轮未重测全部actor分解，不从§16.148投影差额简单减本轮总CPU收益。

首次fill-only低内存组SIGSEGV保留。后续固定反例在父库与fill-only均失败：未暴露writer先退出、reader最后退出后，原native-pin拥有标记未清，下一writer错误归还活reader的物理pin。原Tile最后native unlock共同结束pin和标记、删除writer重复终结后，第一版独立8配对却测到stroke wall多4.12% [2.26,6.28]、CPU多4.92% [3.79,6.06]。最终将原私有函数完整替代为`unblockSwappingLocked`，read/write复用已有锁域，两个COW失败caller显式持锁，消除解锁后重新加锁的工作，不预先把全部实测回退都归给锁。完整填充候选、两版pin-only各自8组×两架，各架4610/0/0；最终生产两文件+12/−17、测试四文件+97/−0，私有签名一增一删、公共/保护/字段/owner净增0。原ratchet与6自测通过，未扩大阈值。

最终single-lock-fix独立8配对/4块，stroke wall下降−0.93% [−6.97,3.85]、CPU−1.51% [−6.47,2.53]，未证明业务非劣/收益。index6为18更新保留，去所在整块的事后3块敏感性仍不确定，不把首版4.12%回退宣称已因果消除。最终Fresh/H4八桶按原规则再次全过；当前保留理由为不可替代的pin安全保证及唯一终结，不领取性能收益，有限批在此停止。

B进一步核定clear/composite之间的调整层original visitor、recalculate、filter/selection是真实中间读者；clear也没有与composite共用historyOwner的完整入口。transaction共享不保持已seal pending。36链约0.47～0.49ms仍是条件冷预算，合法已删集合为空、B净收益未授；完整owner方案必须覆盖读选择、全目标准备、独立失败和联合交付并扣新增成本。现有descriptor值已经共享，不再用新增缓存或调用数微改替代结构论证。**M6/M7/M8仍0/3，正式校准2/20、metadata分母和完整CP0开放，persistent默认关闭。**

<a id="projection-complete-plan-scope"></a>
### 16.150 投影优化的完整责任与验收范围修订（2026-10-08）

产品仍为`a918e45e028c426874d9aa13d8080f2d69170d9f`，文档父`7cd33c886552058f8b1ddd7668a122b2242ce5b3`。本次按用户反馈复核当前冷准备、seal、backend交付及读选择代码，原位更新[03d §5/§8](br1_modification_guide/03d_cpu_cost_calibrated_blueprint.md#projection-complete-responsibility)和[执行经验](br1_modification_guide/CONVERGENCE.md#complete-cost-responsibility)，无生产修改、无新性能样本。

上次蓝图识别了完整维护链，但只将fill形成确定实施；B仍以约束清单和36条同merge条件准备为主，必要代际单价、seal/commit、adapter和读取没有同等深度的替代方案。局部A收益基本兑现，不能作为原upstream差距任务完成。5.322ms是投影总CPU，额外为4.739ms；实测1.111ms是116页整笔fill收益，投影仅60页、原fill体约0.54～0.56ms，两者不能相除报投影差额改善份额。

当前下一实施责任改为完整的投影CPU准备→写入→seal→联合交付→释放，按03d九行矩阵处理所有已发现成本。保留正确性合同，同时重新审查现有对象、遍历、检查及中间表示的必要性。跨clear/composite合并若不合法，仍须推进单个必要写段的内部简化；A的Undo待决只限制启用，不阻塞其它结构设计。已证明等价且同属该责任的改动进入一个完整候选，迁移全部consumer和删除旧路径；尚未闭合的结构方案继续明示未完成。

开发中运行必要编译和安全测试，完整候选后统一做父/候选/upstream性能、投影actor和机制账、实际工作量、负控制与原Fresh/H4及受影响M6检查；局部消融仅解决明确因果缺口，不每个点重跑完整矩阵。理论净价按删除集合减新增成本、扣重叠计算；未定项既不当零，也不当整桶可删。旧证据与有限停止规则不重写，不从文档修订领取收益。**M6/M7/M8仍0/3，正式校准2/20、metadata分母和完整CP0开放，persistent默认关闭。**

<a id="projection-lifecycle-candidate-delivery"></a>
### 16.151 完整投影生命周期候选：删量兑现、Stroke改善、Undo回退（2026-10-08）

沿§16.150及[03d九行责任矩阵](br1_modification_guide/03d_cpu_cost_calibrated_blueprint.md#projection-lifecycle-result)完成同一准备、写入、seal、交付、读侧与释放的有限审查，形成候选 `6644249a4cfd2c48225685a2c27f1a8318def1c3`，分支 `codex/br1-projection-lifecycle-candidate`。当前检出该候选；原 `refactor/brush-s2-predefined-sanity` 保持 `a918e45e02`，没有晋升或push。[完整报告](evidence/br1_projection_lifecycle_20261008/README.md)、[逐行处置](evidence/br1_projection_lifecycle_20261008/PLAN.md)、[冻结身份](evidence/br1_projection_lifecycle_20261008/delivery-identity.json)与[API迁移](br1_modification_guide/API_CONVERGENCE_MAP.md#projection-lifecycle-api)共同限定交付范围。

五项替代一起实施：两步metadata输入由栈借用；同步CPU provider在配置时准备唯一Ready事实，所有同步生产者共用、retirement仍逐allocation独立；seal从原write-set直接生成候选最终输入；原Payload嵌入slot索引并共同解除dirty/slot后释放；默认填充4096→13块调用。投影132必要代际、60 fill、32 overlay不变，按真实次数核算少528+132+132+32=**824次分配请求**，整笔对应1307次，两者不相加。数量不是malloc全计数或时间份额。原中间filter/selection读者、锁外source/domain复验、公开commit的proof校验/epoch delta、adapter各集合寿命及oldData快照cut给出具体保留理由；保留不表示当前每项费用都已证明不可避免。

最终配置修复后独立固定ARM批：父/候选20个ABBA块、40对/80过程，pointwise双侧95%。Stroke wall降低**9.89% [8.43,11.31]**、CPU降低**8.28% [6.71,9.84]**，配对节省中位0.818/1.614ms；Redo wall/CPU降低35.51%/32.44%。**Undo wall增加5.06% [1.20,9.10]、CPU增加4.17% [0.86,7.60]**，配对增加中位9.5/18µs，未满足≤2%控制，不能用Stroke/Redo抵扣。Teardown无回退；最终两组80过程均19更新、同像素、完成销毁，无删样。另20块直接对同依赖upstream，Stroke仍为wall **1.950× [1.891,2.025]**、CPU **1.946× [1.887,2.023]**。最终库不是较早read-fix库，后者11.17%中间结果单独保存、不混样或择优。

粗投影CPU父/候选/upstream中位5.133/4.422/0.398ms，边际残差**4.024ms**，描述性关闭15.0%；四对节省0.528/0.684/0.809/−1.821ms，最后慢值保留，不授精确投影收益或置信下界。细诊断fill约0.560→0.043ms，cold约2.248→1.515ms但self约0.882→0.883ms，seal/commit/capture仍约0.575/0.555/0.359ms；嵌套中位数不可相加。数据不支持已经达到upstream投影效率，也不足以将全部残差宣称为可删维护。容量独立检查物理record收费160→144 B，完整MetadataArena峰值一对降、一对升，不能领取metadata≥25%资格或零尾容量。

最终库 `2442a100b543448c798e71ddfe6f9eb18625013aabc65f8e1d57f2e6e3aec9de` 双架八组**9222/0/0**，结构21 manifest/25 ownership/16 runtime census/2214 APIs/29035逆边及6工具自测通过；原Fresh/H4八桶均按固定规则通过，最低吞吐比下界1.198。生产10文件+128/−87、测试2文件+93/−30，未新增owner/队列/缓存或主干public/protected API。新内部reader接口、Ready字段和Payload hook有实际消费者和被替代对象，净增不自动算结构改善。

开发安全失败暴露默认物化后空descriptor清理也会解锁，collector可在AcquireRead pin登记前回收：原临时map移至外层read栈，在pin登记及owner解锁后清理；真实collector干预旧49/1、新50/0。配置复核又发现源登记成功而Ready拒绝后的重试遗弃源；改为原source接续，精确容量测试验证，不增加恢复队列。两次编译错误、误用旧库的无效开发批、旧容量假设测试失败及派生容量工具编译失败全部保存。修复导致源码变化才另开固定最终批，没有为越门扩样。

**有限候选实施和统一验收已结束，默认晋升失败，upstream差距目标未达成。** 下一启用阻塞是对Undo交付/读取/回收的新增成本作有依据的归因；下一结构预算仍是必要代际的准备、发布及读保护，不重新领取824删量或假定132→96合法。M6/M7/M8仍0/3，正式校准2/20、metadata同义分母和完整CP0开放，persistent默认关闭。

<a id="projection-remaining-cost-diagnosis"></a>
### 16.152 剩余投影成本分组深挖与优先级修正（2026-10-08）

产品仍为§16.151的`6644249a4cfd2c48225685a2c27f1a8318def1c3`，原分支a918不动；文档父`d277af01c8e61699b7393da08dc9ac5ba8e8cf18`。本轮只有外部派生观察库和源码归因，无产品修改。[完整报告/原始数据](evidence/br1_projection_remaining_cost_20261008/README.md)、[03d §10](br1_modification_guide/03d_cpu_cost_calibrated_blueprint.md#projection-remaining-cost-priority)与[消费者清单](br1_modification_guide/CODE_INDEX.md#projection-remaining-cost-code-index)定义下一方案边界。

按预定第一批4能力+10观察，再因测得观察扰动作一次预定3能力+16分组补证，合计**33过程/99 QTest通过**；像素、8 segment/4回调、19 projection updates、析构、实际加载库、退出与reap均核对，事件无overflow/栈错误/活跃尾，逐事件CPU/wall父子账及每过程互斥CPU账闭合。首次全细分投影CPU4.327→5.791ms，中位观察增量33.8%；冷链/metadata/发布与operation分组仍增加17.4%/16.4%/25.2%。这些是描述性诊断，既不授正式CI，也不能按比例扣观察成本或拼接旧4.024ms残差。

新证据降低“local metadata是最大单点”的预期：内部时钟关闭时prepare+publish整个外层约**0.407ms**，开启后metadata_local自身0.755～0.803ms；后者不能当作新发现的产品成本。四个组2过程均264个local sequence=132 prepare+132 publish，每相位同次数，无局部重试放大，源码只投影相关版本。组1将cold细分到base约0.209、预算reserve0.131、register0.077、private prepare0.246、provider0.372ms；尚未单列的binding/写权、终态/descriptor、锁交接、清理和观察边界合计约**0.568ms**，不能全部标成锁、析构或可删。

下一按完整责任排序：**①同步CPU冷准备→预算/登记→绑定→清理；②operation范围/batch/execution建立与终结；③seal/canonical delta贯穿metadata/root/预算及清理；④read capture与merge余项。** 19次operation的范围准入与后续作用域建立约0.136+0.200ms，优先于changed export约0.004ms；commit public proof输入核验仅约0.017ms，不能为删这一循环领取整个commit约0.65ms。各阶段真实消费者已经对照源码，Completion含预算准备、MetadataApply为联合安装、seal proof区间还含reservation释放。组4commit11/14/12/12，各prepare/install同数；未见此组重准备放大。capture约0.35ms、merge余项约1.1ms仍未完全归因，保留开放。

没有找到一个已证明可删≥1ms的单点，也未证明剩余负担全不可避免。新优先级选择有界责任，尚不承诺净收益百分比；实现前须证明原reservation/已接纳事实的有效区间、重复接收删除集合及必要重验，不新增第二状态权威。首次派生脚本边界断言、计数上下文错误与分析输出命名错误均保存；修正分析器只复算原样本，分组后按规则停止采样。原候选Undo回退、默认不晋升及M6未通过保持；**M6/M7/M8仍0/3、正式校准2/20、metadata分母和完整CP0开放，persistent默认关闭。**

<a id="cpu-management-pipeline-design"></a>
### 16.153 同步CPU管理管线：沿原owner传递已接纳事实（2026-10-08）

产品固定`6644249a4cfd2c48225685a2c27f1a8318def1c3`，文档父`7762c71d1478543e72cc6485dd29b3b21c8e940b`。本轮按§16.152的责任继续比较当前与理想算法，形成[03e完整管线/十项删除与consumer矩阵](br1_modification_guide/03e_cpu_management_pipeline.md)、[源码索引](br1_modification_guide/CODE_INDEX.md#cpu-management-pipeline-code-index)及[冻结证据](evidence/br1_cpu_management_pipeline_20261008/README.md)。产品增删0、新性能过程0；四个原分组过程只复算数量，不算新样本。

这次更明确的共同问题是：原ClaimSet、稳定entry和execution已经接受的事实，在下一层又被当作未接纳输入重新扫描/申请；部分锁交接没有读取新的受保护事实。最小探针直接包含当前SnapshotArray模板，确认非const容器的只读range-for触发COW；backend行优先与execution列优先不一致又导致重排，BoundEntry有序构造后还再sort。四元素的两个当前案例均复制4元素；const遍历及一致排序的两个对照均0复制。首轮loader身份缺证被拒，第二轮同一二进制取得实际库哈希，4案例通过、退出0且正常reap；这是容器机制验证，不是产品矩阵。

可证伪的数量预测为：同路径19个非空operation消除19次数组clone、38个容器分配请求；132条成功Fresh链合并reserve/provider间空交接，少132对relock/unlock；96条operation内冷链沿原execution保留claim，省96次重入。另有cursor线性contains与execution二分检查重复、已接受范围的adopt/claimRange/entry重复查询、seal稳定claim三次全查及空candidate/descriptor清理交接。N/S/M/B/E尚未计数则保持符号模型，不能将cold/seal数冒充这些计数。范围转交、seal及空descriptor删除均附私有producer、scope/session有效期和真实释放条件；泛型新键及错误输入不直接跳过。

目标管线为一次规范目标/claim→原session直接绑定→一个锁外冷准备段→仅复验真实可变事实→原seal/delta联合发布→实际释放后归还预算。reader/last-use、provider返回、CPU swap/domain registration、metadata/root接受和失败重试仍保留；132→96仍未合法。已接纳事实复用不新增第二权限表或状态机。源码重复工作的证据强，净时间收益尚未测定；约0.34ms operation准备、0.568ms冷余项及0.04ms seal输入都是混合观察桶，不能全作本方案预算。原候选Undo回退与默认不晋升保持；**M6/M7/M8仍0/3，正式校准2/20，metadata分母与完整CP0开放，persistent默认关闭。**

<a id="cpu-management-cleanup-blueprint"></a>
### 16.154 管理协议清理的代码索引、追踪矩阵与防漂移约束（2026-10-08）

产品仍`6644249a4cfd2c48225685a2c27f1a8318def1c3`，文档父`02f7383d8ebb3c139826623135255899cf7e18d0`。本轮按用户要求把§16.153算法落实为[03f代码改动位置索引](br1_modification_guide/03f_cpu_management_cleanup_index.md)和[03g唯一实施追踪矩阵](br1_modification_guide/03g_cpu_management_cleanup_tracker.md)，[源码与文档核验](evidence/br1_cpu_management_blueprint_20261008/README.md)绑定身份。MP01–MP10一一对应原A–J，拆成22个核销点，覆盖10条入口/终结路径和R01–R09保留责任；产品增删0，未新增产品测试或性能过程。

全caller复查补齐了上一轮未单列的同类工作：legacy已有页重复预留的全scope扫描；alias reserve/provider中间交接；generic provisional request同类窗口的独立证明；alias/generic/初始化空descriptor清理；terminal且retainAdmission时空write-set清理；packed只读消费与bound冷页二次定位。default物化窗口实际复验准备槽、cancel尾pump及非空capacity释放保留，不能按“空容器”批量删锁。新项无本用例计数者保持未知，不扩大19 clone/38请求、132对锁及96冷claim的原预测。

03e只维护算法，03f维护源码consumer与删除规格，03g维护唯一状态/证据和预测实际差额。每个产品hunk归属固定ID，旧字段/参数/helper无consumer即同批退出；待证明项不能迁出矩阵求全绿。范围转交、已接纳execution及已有entry绑定分母分开，查询模型为`N_a + 4N_r + 2N_e`，同一独立operation三者相等才为7N；fillRect只领取转交项。完整候选统一验收，不每小项各跑完整性能矩阵；净时间仍待测。未实现、机制兑现、安全通过、净收益、默认晋升与M6分别裁决；原Undo回退、默认不晋升、M6/M7/M8 0/3、正式校准2/20、metadata分母和完整CP0缺口保持。

<a id="cpu-management-cleanup-result"></a>
### 16.155 CPU管理管线清理实施与有限收益结算（2026-10-08）

候选`704d96e81cf29d16191bc3db8785859d79775e27`，tree `4e7fc164db46c02b968fdd04400b9e4402e289d0`，父6644249、文档父1dc64c25；当前分支`codex/br1-cpu-management-cleanup`，原a918分支及6644249候选分支保持，不push。[03g唯一账本](br1_modification_guide/03g_cpu_management_cleanup_tracker.md)22项迁移与适用安全验证完成；[报告/原始数据](evidence/br1_cpu_management_cleanup_20261008/README.md)、[证明及59个hunk归属](evidence/br1_cpu_management_cleanup_20261008/PLAN.md)、[冻结身份](evidence/br1_cpu_management_cleanup_20261008/delivery-identity.json)限定结果。生产7文件+158/−106、测试3文件+66/−28；没有新增永久字段、owner、锁实例、队列、权限表或生产计数器。

原reservation原子移交并直接沿slot绑定execution；history仍完整处理新键/重叠。排序统一且只读消费，cursor只查execution，bound冷页沿用claim/index，native/alias/generic合并空准备交接，原publication统一空descriptor清理，seal稳定claim只全查一次，legacy单页查原token。generic的Preparing request/preparation activity证明不依赖domain或同步终态，R09仅此窗口闭合；provider后验收、default物化、读保护、真实新键、proof重试/预算/退休及实际free保持。

8个外部派生观察过程保持19 operation/32写段/132冷链，其中96 bound冷；19 clone/96元素/768B、96 contains、96冷claim重入和二次定位归零；38请求是模板结构推导。Fresh132＋candidate32＋descriptor132＋retainAdmission32，合计328对空/中间锁交接退出。write-set findIndex1218/1222→454；40次legacy重复预留从284/316个claim查询收为40单键查询。父clear范围154/158键及commit10–14的实际波动保留；seal按实际S核对3S→S，候选另64动态判断。直接slot比原一次定位再少N_d=96，逻辑查询模型补为N_a+4N_r+2N_e+N_d，原事前7N条件模型保留。未触发alias/generic/read/init投影分支不外推数量或价格。

未插桩ARM64固定父/候选40对：Stroke CPU降低**3.08%**，pointwise双侧95% CI[0.33,6.86]，配对节省中位数0.182ms；wall降低3.08%，CI[−0.07,7.35]，尚未显著。Undo wall/CPU降低9.31%/7.83%，Redo降低5.95%/5.39%；Teardown wall/CPU点估计增加1.38%/1.42%，区间跨零且未证明≤2%非劣。独立upstream40对仍为Stroke wall **1.8795倍**（CI[1.7492,2.0099]）、CPU **1.8649倍**（CI[1.7592,1.9704]）；CPU配对额外成本中位数7.769ms属于该批分母，不与旧5.3ms或旧观察桶拼接。upstream一过程20 updates，其余19，像素/回调/析构同义，按预定规则保留。

按独立采样前协议另对原a918做40对，旧Undo回退在本批诊断层恢复：wall降低8.35%，CI[1.96,14.25]，CPU降低6.60%，CI[0.35,12.43]；Stroke wall/CPU降低11.34%/9.90%。原控制Teardown CPU上界仍约+2.10%，不授2%非劣或完整默认qualification。Fresh/H4双架K1/K16共8桶640过程均通过各自原保护fixture非劣；这些为相对固定M5累计结果，不领本包增量或handoff资格。全部统计不替代正式校准。

双架同源16安全组**9224/0/0**，定向55/0/0；结构2216 APIs/29062 edges和工具6自测通过，实际加载库/退出/reap及成功/失败全部留存。数量目标兑现，净收益有限，剩余upstream差距未被解释为全不可避免管理成本。本有限包结束，不重领扫描/空锁，不盲加样；下一围绕canonical发布/allocator联合责任及read/merge余项建立必要成本下界、实际可删除集合与预算。**默认不晋升；M6/M7/M8仍0/3，正式校准2/20、metadata分母及完整CP0 required开放，persistent默认关闭。**

<a id="cpu-residual-ranking"></a>
### 16.156 清理后性能回退来源重新排序（2026-10-09）

产品仍为704d96e81c/tree4e7fc164，文档父36fb72baf；本轮仅复算§16.155原80个未插桩upstream过程和8个计数诊断过程，没有新采样、产品或测试修改。[完整报告/分析器/输入哈希](evidence/br1_cpu_residual_ranking_20261009/README.md)及[03d §11](br1_modification_guide/03d_cpu_cost_calibrated_blueprint.md#cpu-residual-ranking)定义当前优先级，不新增03g的第二份实施状态。

按配对额外CPU中位数排序：**Stroke7.7685 ms → Redo0.7585 → Undo0.5125 → Teardown0.4735**。Stroke比率1.8649，沿原pointwise95% CI[1.7592,1.9704]；四阶段配对额外CPU均值合计9.55595 ms，其中Stroke81.60%。均值份额只描述这四端点，不含Setup/间隙、不授归因置信；所有慢值及upstream一例20 updates保留。

内部审查第一梯队为**逐代际冷准备及接收 → private seal → canonical联合发布及释放**：当前4过程208冷链2.581–2.836 ms，seal+commit逐过程合计1.512–1.637 ms，互斥完整链4.129–4.393 ms。第二梯队operation混合余项3.231–3.372 ms与capture/merge余项1.411–1.600 ms暂不互排；前者含真实pixel，后者含多种source消费者。观察事件尚未覆盖同过程8.205–8.779 ms Stroke CPU，不能填为零或全当额外管理。当前桶价含观察扰动、没有同期upstream细桶，不与7.7685 ms相除、不承诺净删量。

已清理clone/claim/空锁、旧fill小调用和旧生命周期824请求退出下一热点；metadata算术、public proof小循环及R08历史descriptor搜索没有新大额预算，不盲重写。当前证据支持多层生命周期和混合路径共同形成差距，尚不证明均为必要成本。下一最小诊断先恢复当前/upstream低扰动job差额账，再按必要成本及真实重复集合选择完整责任；本轮不执行新诊断。原Undo诊断恢复及Teardown≤2%非劣欠项保持。**默认不晋升，M6/M7/M8仍0/3，正式校准2/20、metadata同义分母和完整CP0 required开放。**

<a id="current-upstream-cpu-ledger"></a>
### 16.157 当前/upstream CPU差额对账与后台终结归属（2026-10-09）

产品仍704d96e81c/tree4e7fc164，上游9a24ae0d8c，文档父a5004b383；本轮只派生观察库与边界fixture，产品/产品测试改动0。[事前协议、一次追加与完整证据](evidence/br1_current_upstream_cpu_ledger_20261009/README.md)、[03d §12](br1_modification_guide/03d_cpu_cost_calibrated_blueprint.md#current-upstream-cpu-ledger)更新§16.156优先级，不改03g已完成矩阵。

首批8能力+64主过程，原库/off/jobs/detail各4平衡ABBA块、8配对；追加4能力+32主过程区分主线程与其它线程，随后停止。**108过程/324 QTest通过，0失败/跳过**；全部8 segment/4callbacks/19 projection updates、像素/undo/redo/销毁、加载与退出/reap通过，79共享安装依赖哈希一致；观察CPU/wall父子账、同stage、无overflow/活跃尾通过。两次运行前开发失败（协议文档哈希、fixture重复头定义）及全部慢值保留，无替换采样。

首批detail同批CPU均值账：projection jobs **4.236547−0.539031=3.697516ms额外**，stroke jobs **10.597545−8.283157=2.314388ms**，job外 **1.779033−0.480062=1.298971ms**，合计**7.310875ms**；份额50.58%/31.66%/17.77%仅属该诊断分母。仅jobs额外3.752084/1.961726/1.377064ms；两边均937 stroke/19 merge jobs。原来未覆盖的约8.4ms，在本批同源桥接为stroke job内6.573695、merge外框0.074297、job外1.779033ms，不把整段当新回退。

唯一追加取得原reclaimer线程**1.265625ms**、原delay/wake monitor **0.175500ms**累计CPU，upstream无对应线程；它们在Stroke前已存在。主线程严格事件current/upstream仅0.086114/0.092896ms。新增4线程均为job workers，无消失线程。快照窗口略宽，线程累计差额7.201250ms减去显式快照/严格端点差0.029750ms，对上同批Stroke差额7.171500ms；不把后台1.441125ms与另一批1.298971ms硬拼或宣称全可删。该证据将任务外主要差额定位为**实际后台终结/唤醒CPU**，不是主线程等待。

当前责任层账已闭合，不继续扩大采样。前台cold/seal/commit在本批current为2.142911/0.792826/0.654004ms，callback扣除cold等为2.286166ms；均非upstream差额或净可删预算。下一完整责任必须把投影冷准备/private/canonical交付与原metadata cleanup、reader/history/retirement及实际free/通知一起审查；后台约1.4ms已提升为同包必要审查，不能只移走前台费用。源码消费者索引见报告§5，类型级次数/价格和合法删量未证，不盲删异步、公平界或新增owner。operation/读合成余项保持第二梯队，已退出claim/空锁/旧fill不重领。

原库current过程52为31.813ms、追加upstream过程9为17.125ms，均保留；各模式/配置漂移不支持固定扣钟或新的概率CI，绘画任务额外量以约2–3ms描述。**默认不晋升，M6/M7/M8 0/3、正式校准2/20、metadata同义分母及完整CP0 required继续开放。**

<a id="cpu-lifecycle-blueprint"></a>
### 16.158 CPU全生命周期优化蓝图与删除追踪（2026-10-09）

产品仍`704d96e81cf29d16191bc3db8785859d79775e27`/tree`4e7fc164db46c02b968fdd04400b9e4402e289d0`，文档父`c2556c725d4ff8bd63fe09535694c6bf97f7f3b6`。按§16.157责任账完成[03h理想算法](br1_modification_guide/03h_cpu_lifecycle_ideal_blueprint.md)、[03i代码改动与删除索引](br1_modification_guide/03i_cpu_lifecycle_edit_index.md)、[03j唯一实施矩阵](br1_modification_guide/03j_cpu_lifecycle_tracking_matrix.md)；[源定位、消费者及文档核验](evidence/br1_cpu_lifecycle_blueprint_20261009/README.md)绑定当前源码。产品/产品测试改动0、新性能过程0，未实施或宣称收益。

核心差异从重复协议细化为**相关版本仍被完整投影/重装、普通发布复制状态后再求少量字段差分、候选按页重复取分片锁**。目标是Fresh/Adopt、同步private发布和普通canonical共享原语义策略、直接安装最小变化，未变lease/pin/last-use/capture链留在原记录；保留真实capacity/provider接纳、revision复验和全批claim。原Data分片分组贯穿prepare/install/rollback/cleanup，不新增owner、第二状态表或layout cache。后台队列的idle通知、取头/完成锁合并、worker身份寿命以及monitor等待条件通知同包设计。

LP01–LP10分28子项、12条入口/终结路径与七类后台责任；19项设计固定待实施、5项待证明、3项有据保留、1项整包待核验。待实施不等于并发安全已证；条件read调度、epoch摘链、effects、descriptor/读选择仍在同账。history/retirement/budget与最后owner的真实保护不以“管理开销”一概删除；原03g已结算22项不重领。

预测使用镜像元素/重装、N/S/G分片run、J/B任务/idle启动、有效deadline/ready变化等分母，并扣新增排序、字段、复验、引用和持锁/释放代价。不把不同配置的3.589741ms前台链和1.441125ms后台相加为可删预算；无单位净价，不作新ms或百分比承诺。统一候选完成后按03j反例、机制计数、未插桩父/upstream/原控制及全生命周期验收；不再重跑108过程覆盖对账，也不以小通知优化先取得正值结束主项。

当前资格保持：默认不晋升、persistent关闭、M6/M7/M8 0/3、正式校准2/20、metadata同义分母/完整CP0及Teardown原控制缺口开放。

<a id="cpu-lifecycle-implementation"></a>
### 16.159 CPU全生命周期优化实施、删量与有限净收益裁决（2026-10-09）

产品候选`d182a34bd0196079bc40d2ab7d00b8e326e4a58a`/tree`e03a63d2a33324a55c72b7eb8ec097deab96b171`，分支`codex/br1-cpu-lifecycle`，父704；image SHA256 `da4304d429134da577087e15004b4d98d93b7fc5c97a1bf6d8da4f4a615d66d1`，文档父e333942d9。按03j完成22项结构/语义实现、5项有据保留和1项整包审查；[报告/完整证据](evidence/br1_cpu_lifecycle_implementation_20261009/README.md)、[28项唯一矩阵](br1_modification_guide/03j_cpu_lifecycle_tracking_matrix.md)、[实际改动索引](br1_modification_guide/03i_cpu_lifecycle_edit_index.md#implemented-index)绑定14文件/109 hunk/32个转换。原704/a918分支保留，不push。

原applyPolicy继续唯一决定guards；限定Fresh/Adopt/private消费必要标量事实，不再复制保护链/重装旧record；canonical由原policy直接产生实际delta。原Data按稳定分片/key排序，贯穿prepare/claim/install/rollback/清理，原全claim后首改、capacity/revision和实际free归费保持。executor/monitor删无等待条件变化的通知，完成与下一取头共锁；epoch原链≤remaining128摘取，descriptor借精确base的原共享值。必要标量WorkingVersion仍存在，不把它们计为删除。recoverable、effects原子工作图、history/retirement/预算接续、真实读cut及最后owner保留。生产净增349行，未宣称源码复杂度净降低。

最终双架16组**9370通过/0失败/0跳过**，结构门/callgraph/工具自测通过。新16/17页、乱序重复/晚组冲突和descriptor不等反例通过；失败/中止证据全部保留。Fresh/H4各双架K1/K16、40配对/桶，八桶全部通过各自固定M5控制family；不授本包增量或handoff优势资格。

8机制过程均19投影更新。projection Stroke旧record整装**396→0**，private额外snapshot **132→0**，descriptor历史比较少**132**；完整保护投影628–672→0，但必要薄事实仍640–672。独立统计锁248–292→0；正常小batch的分组锁每pass只减少约10次，且新增sort413–501比较。全阶段job通知177–192→39–44，空cancel通知196–207→0；真实job/free不消失。last-use/ready/arm在匹配fixture未触发，保留实际边界，不虚报它们的删量。

父、upstream、a918各20块/40配对，共240未插桩过程，全部19updates、相同像素/输入/加载/退出通过。相对父：Stroke CPU降**3.88%[−0.28%,8.82%]**、wall降**3.07%[−1.61%,8.62%]**，收益未证；Undo/Redo/Teardown CPU降11.45%/7.33%/9.08%。五阶段含Setup的总CPU降**0.20%[−0.81%,1.29%]**。区间为pointwise95%，无正式family资格。a918的Teardown wall非劣在本批通过，父对照上界1.0219仍未满足≤2%；a918的Setup/五阶段总wall回退2.63%/2.25%也保留。原a918 Stroke累计CPU下降10.06%不能领取为本包增量。

候选对upstream仍额外约**7.643ms Stroke CPU、3.283ms wall**（配对差中位）。数量预测兑现，但旧镜像保护元素本来只有0–13个（全阶段），没有统一高单价；标量构造/索引、owner/provider/proof和真实root/读cut仍在。本批不能证明剩余差额全是正常管理成本，也不能精确判定哪项新费用抵消。下一归因须建立必要事实/索引与原owner等工作的单位净价，不继续凭小动作删量预报大幅收益。

**候选分支保存，默认不晋升；M6/M7/M8仍0/3、校准2/20，metadata同义分母、完整CP0及正式多端点/资源性能资格开放，persistent默认关闭。** 本包有限验收已停止，不加样到正值，不重跑108过程覆盖账。

<a id="first-principles-selection-trial"></a>
### 16.160 第一性候选选择流程试行与技能升级边界（2026-10-09）

产品保持d182a34bd0，文档起点875beadf2；产品/产品测试改动0、新性能过程0。新增[03k候选筛选](br1_modification_guide/03k_first_principles_candidate_selection.md)与[反例回放/前瞻追踪](evidence/br1_first_principles_selection_20261009/README.md)，保留原蓝图—实现比对—代码索引—唯一矩阵—统一验收。当前安装的algorithm-cost-optimization保持原版，前瞻闭环后才按有效经验升级；本篇是项目内试行，不授方法成功率。

§16.159主要端点净收益未证暴露的是蓝图选项准入缺口：责任桶归属不等于具体动作可删除时间。原方案虽明确未知单价且不承诺ms，仍将结构冗余列为待实施；后续须先从事实消费者、保证来源、失效窗口和最终寿命构造合法理想算法，再以实际频率/大小和净预算选择。未知项只领取有限判别，完整责任依赖项不虚领独立收益；设计降为薄状态等较弱删量时重新评价优先级。

已知案例回放覆盖LP镜像、分组锁、通知、未触发分支、小memcpy和整页copy；9个冻结端点bootstrap复算一致、14类计数来源绑定。小memcpy有约1.1ms因果价格，但其18/19次更新偏差和Undo回退继续保留；新规则只能解释为何值得判别，不能事后宣称原LP各项必然无效。含Setup五阶段0.20%不作主目标命中判据，Stroke与各阶段绝对成本及原控制分别判断。

下一工作先区分H1临时标量状态构造、H2原索引/owner/provider/proof、H3真实读cut/合同工作；它们均未获新净ms预算，不能由“仍存在640–672次薄事实”直接指定核心。补最小互斥责任/分布价格，再冻结合法局部替代预测与有限实验。108过程覆盖账和LP包保持停止；新候选事前选择、完整实施与独立净收益确认尚未完成。M6/M7/M8仍0/3、校准2/20、persistent默认关闭。

<a id="first-principles-candidate-probe"></a>
### 16.161 第一性候选首次前瞻判别：metadata降级与H2具体责任定价（2026-10-09）

产品保持d182a34bd0/原image da4304d4，文档父e5a529aab。按03k先冻结[D1协议](evidence/br1_first_principles_probe_20261009/PROTOCOL.md)，根据其结果只追加一次[D2协议](evidence/br1_first_principles_probe_20261009/SUPPLEMENT.md)。[报告/源码差异/原始证据](evidence/br1_first_principles_probe_20261009/README.md)完成38真实过程、114 QTest通过/0失败/0跳过；全部19updates、同像素/历史/销毁/退出/实际库核验。产品与产品测试改动0，未宣称新提速、未重新跑upstream。

D1 outer全部Stroke metadata write+prepare+install为0.85148ms（0.83986–0.86312）；包括必要策略/容量/索引/安装，不能全计删除。facts的事实选择观察约0.24940ms，但投影CPU比outer增加18.09%、Stroke中位高1.9685ms，触发事前扰动限制。观察量不作精确净价。Fresh/private投影分别132/264输入版本，单版本sizeof488B、版本数组最高2；不等同复制字节或全部数组零spill。H1未获得支撑再次改写共享政策表示的0.5ms本轮价值参考预算，优先级下降而非证明零收益。

D2在同一库比较coarse/h2，投影CPU比1.03745、Stroke中位增加0.102ms，未触发本协议限制；仍仅描述统计，无新概率CI。全部Stroke的base解析、backing预留、登记、proof封装分别0.43671/0.22374/0.14050/0.13891ms中位，均含真实必要工作；不能以完整线程/冷链价格领取单项。D1的25.251ms与D2的32.789ms慢值全部保留。

下一责任是同批cold外框0.88158ms、operation外框0.96918ms、merge外框1.07971ms的实际事实/消费者与跨层粒度；这些是当前独占桶的各自中位，不是净回退或可删除预算，不相加到旧7.643ms。seal/commit/capture继续有具体原合同，不能把未知外框统称正常成本。先形成合法替代与条件净价再入蓝图，不重领H1薄事实或孤立backing/proof小项。

本包完成前瞻筛选和观察失真限制，未选择产品优化包；D1+D2到此停止，不加第三组细时钟或追显著性。技能仍试行、未正式升级：正向收益预测—完整实施—独立确认尚缺。M6/M7/M8仍0/3、校准2/20、persistent默认关闭，完整CP0/metadata同义分母和正式资格保持开放。

<a id="read-intent-selection-trial"></a>
### 16.162 第一性读意图因果试行：未消费before删量兑现，净价未决（2026-10-09）

按[03k](br1_modification_guide/03k_first_principles_candidate_selection.md)从实际consumer选择新责任，完成[受限current读者原型与固定判别](evidence/br1_read_intent_trial_20261009/README.md)。产品保持d182a34bd0；无产品/产品测试改动，安装skill未变。不是D1/D2第三组细时钟，也不重领03j。painter false source只消费current，通用accessor却同时准备before；原型只在其局部构造及mask current意图中省未消费before，保持current cut/guard，公共双视图、old source和legacy合同保留。产品化须显式贯穿factory/strategy/iterator，不采用实验TLS。

计数A/B各1过程：eligible19、有history18均相同，跳过before捕获0→18；全部iterator before页获取80→0，current仍96。像素/历史/19updates/原销毁通过，不能将80次获取等同payload分配或复制。未命中的old source/mask不领收益。

时间关闭计数，同库4固定块/16过程，CPU节省逐块+0.956/−0.459/−0.253/+7.9855ms，中位0.3515ms；wall中位0.3425ms。2/4块反向，A过程13的32.526ms保留，未通过事前方向一致且≥本项δ0.3ms的探索准入。Setup未命中却有表观7.305ms CPU节省，不能领取全程差额。无确认CI、无零收益断言，不续采、不与旧upstream差额机械抵扣。

总19过程57/0/0，同输入像素/UndoRedo/销毁、实际库/共享依赖hash和退出/reap通过。原始包、事前协议、三TU差异与完整索引/追踪随报告冻结。本包完成合法替代和净价判别，未准入跨层产品改造；正向预测—完整实施—独立净收益确认仍缺，技能继续试行。下一项只领取有新事实放大/合法替代依据的责任，不能把cold/operation桶价直接当收益。M6/M7/M8仍0/3、校准2/20、persistent默认关闭，CP0/metadata同义分母与正式资格保持开放。

<a id="history-admission-selection-trial"></a>
### 16.163 第一性技能实际试行：空历史任务删量兑现，独立净收益未准入并回退（2026-10-10）

从产品d182a34bd0/image da4304d4开始，先完成[Darwin free重复查询定价](evidence/br1_storage_release_trial_20261009/README.md)：约6000次Stroke free，每次仅约4–6ns条件节省，整笔约0.02–0.04ms，不实施、不跑未准入的64过程。唯一释放栈普查320条/overflow0，Stroke185条中40条经过history collectSlice、21条释放Work map节点；初步手工26更正40，事前原文与勘误保留。这只是定位，不作CPU比例。

据此形成[空历史Work准入蓝图/预测/唯一索引](evidence/br1_history_admission_trial_20261009/PREDICTION.md)：原owner内新任务先查既存history事实，空则免分配/收费/排队/worker空扫描/free；已有Work repeat、非空回收保护/失败/最终退休保持。8块探索CPU节省0.66025ms [0.2315,1.696]，通过探索后才给0.2–1.0ms工程预测、δ0.1ms并实施。首版容量重扫callback已持metadata shard锁，新增getter造成死锁；保存sample/SIGTERM/reap，修订visitor走原准入后双架构16组9370 QTest通过。新增真实96页“空历史读释放→后续supersede→晚读者释放/drain”覆盖。

[产品计数与独立确认](evidence/br1_history_admission_trial_20261009/README.md)：新Work **868→212（−656）**，非空候选均212；B760次skip不是净删760，且父任务数量超出700–750预测。B普通新候选972次需查询，压力visitor未命中；Undo/Redo各56个真实任务不删却各增56次查询，是原预算未充分定价的副作用。独立16块/64新过程CPU节省 **0.4545ms，95% pointwise区间[−0.028,1.404]**，未过事前下界>0；wall0.18575ms [−0.303,0.5815]。Redo CPU/wall分别增加0.05875/0.04125ms，描述性pointwise区间指向回退，不能精确全归新增查询。所有慢值保留，无追加样本、无新upstream差额结算。

Fresh/H4各四桶40对/桶、250ms完成率、原2%非劣均通过；每个四桶family各至少95%，不借它们覆盖主端点失败。按[最终决定](evidence/br1_history_admission_trial_20261009/DECISION.md)回退两个生产文件，只保留13行边界测试；源码/库/全部原始过程与首版失败冻结。安装skill仍原版，03k只更新已暴露的“caller已持锁”和“零过滤收益路径必付新增成本”试行要求。完成否决闭环不等于正向预测能力已证；不以宽预测范围内的点估计授成功。

下一候选仅考察能否从已有metadata状态迁移/保护释放事件传递原事实，避免统一getter重复查，先证明producer/consumer、失效窗口和非空路径净价，再准入。当前批次全部停止，不扩样。M6/M7/M8仍0/3、校准2/20、persistent默认关闭，完整CP0、metadata同义分母与正式资格保持开放。

<a id="candidate-rank-prediction-audit"></a>
### 16.164 候选预测与榜首复核：history降为次级，前台大责任仍需可删预算（2026-10-10）

产品保持c13c442493，生产源码相同于d182a34bd0；无产品/测试改动，安装skill不变。[误差审计](evidence/br1_candidate_rank_audit_20261010/README.md)复算旧64过程：独立Stroke CPU点估计0.4545ms比探索0.66025少0.20575ms（31.16%），实际节点删量656却比探索522多25.67%。原0.2–1.0ms是宽工程范围，没有单点预测；落入范围不证明准确。主区间[−0.028,1.404]宽1.432ms，为δ0.1ms的14.32倍。按块合计Stroke/Undo/Redo/Teardown后的事后描述性CPU净节省0.30225ms [−0.02075,1.471]，不换成新准入门、不扩候选样本。

为区分释放频率榜与时间榜，另冻[有限责任协议](evidence/br1_candidate_rank_audit_20261010/PROTOCOL.md)，只新增history job/pass两完整范围并复用前台粗边界，关闭细facts计时，无逐key时钟或产品getter。4配置各1能力+4主过程共20过程/60 QTest通过，全部19updates/像素/历史/销毁/实际库与共享依赖一致；所有慢值保留。

同一history配置4过程独占归组的当前CPU中位：**前台cold→seal→commit 4.0432ms**，pixel callback余项2.3730ms，merge余项1.0741ms，operation余项0.8661ms，history后台已观测阶段内部分0.6369ms，capture0.3569ms。history在此明确分组排第五，其pass仅约0.5015ms且包含必要非空历史处理。前台链子项cold2.4475/seal0.8755/commit0.6967ms不能与父项重复加；cold扣已观察子责任后的外框约1.419ms仍待合法删除证明。

新history观察使Stroke比coarse多0.2125ms、投影比1.01377，未触发原0.25ms/1.15扰动线，但不证明无扰动。每过程约0.0184–0.0208ms后台job跨出Stroke，原分析器拒绝后按[边界修订](evidence/br1_candidate_rank_audit_20261010/ANALYSIS-REVISION.md)单列，未改样本。stage0开始的scope、前台request/队列等仍不全被history范围覆盖，0.637ms不能作该候选严格上界或全寿命总量。

本轮已观测阶段内scope合计中位9.3244ms，同过程未覆盖7.4102ms；未覆盖部分不是新增差额或纯管理费。既有§16.157已在其冻结产品将任务/线程层差额对账，本轮没有重跑该账，也不能把有限scope榜说成全CPU或当前upstream差额的完整排名。

裁决：**没有证明找到了性能榜首或前列的可优化项；证据支持空任务降为次级候选。** 原21/185 Work free栈只是事件频率。当前成本榜、upstream额外成本榜、合法净回收榜必须分开；本轮未测upstream，不机械抵扣旧7.643ms。下一调查优先回到逐代际前台准备/发布的事实交接，以及operation/read-merge，先取得合法删量和净价；不默认继续§16.163的history事实传递小改造。03k补排名分母与精度要求，技能仍试行。当前批次停止，M6/M7/M8仍0/3、校准2/20、persistent默认关闭。

<a id="optimization-skill-corrective-update"></a>
### 16.165 优化技能纠错更新：已合入反例规则，正向预测能力仍待验证（2026-10-10）

根据用户“技能可以更新吗，还是需要继续优化”的询问，区分规则维护与效果验证：无需等待新的正收益才修复已知判断缺口，但不能因此宣称完整选择/预测流程已有效。[algorithm-cost-optimization](/Users/apple/.codex/skills/algorithm-cost-optimization/SKILL.md)已作有限纠错更新，[前后快照、差异与验证](evidence/br1_optimization_skill_correction_20261010/README.md)随证据保存。旧批次“技能未改”是当时状态，原样保留。

正文合入必要事实/失效者推导、当前/额外/净可回收三榜区分、未知净价先判别、零删除路径新增成本、caller持锁/回调重入、δ与实验精度、探索参考与预测校准边界；候选记录和冻结反例放references。原理想路径—实现比对—索引—追踪矩阵—统一验收保持，BR1数字不变成通用门槛。结构校验通过仅说明技能格式有效，不是新性能或行为验证。

产品仍c13c442493，生产源码与d182a34bd0相同；本轮无产品/测试改动，无新性能过程。空history候选否决、前台较大责任的调查优先级和全部原控制结论保持；后续先证明其合法删量、净预算与可行精度，不为技能升级追逐一次正结果。**本轮完成纠错更新；可靠选中前列瓶颈及预测有价值净收益的正向闭环仍未完成。M6/M7/M8仍0/3、校准2/20、persistent默认关闭。**

<a id="descriptor-search-selection-trial"></a>
### 16.166 更新后技能试行：R08后备搜索未放大，节点计数语义修订（2026-10-10）

用户要求继续下一轮并注意技能欠缺。产品仍c13c442493，生产同d182a34bd0；安装技能保持§16.165版本。沿[前台事实/消费者/失效窗口索引](evidence/br1_descriptor_search_trial_20261010/PIPELINE_AUDIT.md)检查原base/provider/binding/metadata/proof责任，选择R08 descriptor共享搜索做有限判别，不把前台4.043ms授为其可删预算。[协议与结果](evidence/br1_descriptor_search_trial_20261010/README.md)保存初版四过程和探针修订后两个过程，全部6过程/18 QTest通过，像素、19updates、Undo/Redo、销毁、实际依赖及退出核验；无产品/测试修改或新性能资格。

修订观察的全Stroke：208次base hint均相等；全索引比较110–114次、命中110–114次，候选表比较0，故每次后备搜索首项即命中，超出首项的遍历为0。索引最大112项并未形成112倍工作。helper333–334次处理320–324输入，实际成功插入320–324节点，仅新建2个descriptor对象。每个过程的Undo有两次helper调用、合计56输入，每个输入一次首项比较；不能把单次helper的56比较误认作搜索长度。R08“消除向后遍历”在该端点的可删量为0，不实施缓存/索引重写；这不是整条descriptor责任零成本或所有管理费用必要的证明。

首版观察器在emplace调用后累计“新节点”，未检查inserted结果；[修订](evidence/br1_descriptor_search_trial_20261010/CORRECTION.md)保持所有旧数据，将尝试与成功插入分别计数。两个修订过程分别320/324，不能当优化减少4。原搜索计数结论保持；复现一致与内部等式自洽不证明探针语义正确，观察器作用域自检也不替代实际操作结果核验。

技能反测：本轮支持了有限判别能够避免一处假热点，但**仍未证明可靠生成前列高净收益候选**。项目03k补快路径/每输入迭代及探针结果语义检查；跨层布局值、版本映射、独立proof身份和驻留事实分开。数百版本节点的全寿命是待论证问题，净价格及合法合并均未知，不能自动晋升榜首。本批结束，不扩同包时间样本，不再改通用技能正文。M6/M7/M8仍0/3、校准2/20、persistent默认关闭。

<a id="pipeline-boundary-audit"></a>
### 16.167 前台算法与调度不能由局部排除担保，选择层级纠正（2026-10-10）

用户指出中上层拆分可能使下层维护成本合理化，并被局部优化固化。[源码与证据审查](evidence/br1_pipeline_boundary_audit_20261010/README.md)确认目前**没有前台算法足够优或调度无额外成本的证据**。§16.166只排除共享搜索遍历；旧937/19相同job数只排除任务数量倍增，不覆盖每job的operation/版本/发布，也没有ready/dispatch/真实依赖的关键路径证据。当前区域队列、updater context、async merger沿用固定upstream；面积合并与整块accessRect排斥是否适合新下层成本未知，不能直接授予新增CPU差额或判为最优。

此前B项研究过clear/composite融合，已有真实中间reader、失败和root寿命障碍；尚未逐条证明所有内部独立边界必要。“不能直接融合”不等于“现有拆分足够优”。下一主判别改为一次投影更新的业务必要状态、失败/交付边界与当前执行图对照，再选择跨层完整替代或保留边界；不自动续做descriptor节点/页内小项，不重开旧失败实验。原fixture只要求projection通知大于0，局部runner固定19属诊断匹配；结构实验应另冻真实显示/顺序/延迟/取消/资源oracle，把内部次数作为因变量，不能回改旧数据或只验最终像素。

安装`algorithm-cost-optimization`已作有限纠错：新增中上层工作拆分/调度审查，区分公共合同与内部机制，要求说明干预层级并避免固化上层替代；03k与默认提示同步。[前后快照、差异、校验](evidence/br1_pipeline_boundary_audit_20261010/README.md)只证明规则修正与静态检查，不代表发现能力或跨层净收益已通过前瞻验证。本轮产品c13c442493保持，生产/测试改动0、新过程0；M6/M7/M8仍0/3、校准2/20、persistent默认关闭。

<a id="projection-boundary-selection-trial"></a>
### 16.168 清零/首层合成中层边界命中；独立原型价值通过，生产合同仍开放（2026-10-10）

按§16.167更新后的技能，以同 merge 的`clear → first composite`为下一主判别，完成[两版派生原型、数量和独立确认](evidence/br1_projection_boundary_trial_20261010/README.md)。四TU由当前c13c442493派生，生产同d182a34bd0，原build/bin库未覆盖，产品生产/测试改动0。复杂层/真实下层依赖、temp、old source、selection、alias、format/default/wrap及非over走原路径；支持路径在原pixel operation完整准备后初始化清除域，再运行原kernel，未绕过预算、保护、seal或adapter。实验TLS/保活不是生产接口与资源资格。

r1计数的Stroke：19 merge/19 pixel operation保持，13独立fill删除；成功冷准备**132→96**，新batch/成功seal均**32→19**，13次融合实际初始化566464B。冷准备计数是成功prepareWriteBaseLocked，不是唯一节点；commit随调度变化，不授固定删量。Undo无首层，原fill/batch/seal各1；Redo清除域为空，不融合，56冷准备/1batch/1seal保持，额外初始化0。19通知只是实际结果，原4显式callback和8segment保持，不把内部19当新合同。

r0四探索块Stroke CPU收益中位1.50925ms，但Redo一致回退约0.2135ms，零冷准备删量却新增917504B初始化。保留旧版，在r1构建前另冻旧extent裁剪/空域原路径及[预测](evidence/br1_projection_boundary_trial_20261010/R1_PREDICTION.md)：Stroke约1–2ms、δ0.5ms、Redo额外初始化0。先四能力过程和原merger/projection测试，再独立16个ABBA/BAAB块、64个未计数过程。全部慢值保留、不续采；主Stroke CPU块差中位**1.05775ms，pointwise 95% [0.716,1.5455]ms**，逐块相对收益中位6.6419%，16/16块方向改善，原型价值筛选通过。Stroke wall节省0.4895ms [0.2615,0.6475]，只到projection-ready，非canvas-visible。

r1 Redo CPU差0.0015ms [−0.019,0.01225]，未再见r0的大回退但不证明零成本。Undo wall回退0.00925ms [0.00225,0.0365]有信号；Undo/Teardown CPU区间跨零，时间非劣未授。均为描述性pointwise、无family或M6资格。成功批次97过程/327 QTest，另保留初始control与原库两个SIGSEGV、LLDB诊断和两次编译前准备脚本匹配失败。SIGSEGV来自语义测试缺blur插件，按事前补充协议仅修测试插件前置，新测试批次通过；性能插件目录不变。实际库、对象、依赖、hash、原失败/原始样本均随证据冻结。

技能反测第一次支持了**中层展开产生可删维护工作，且受限替代有独立净收益**；不是只优化一次memcpy。分支净账也否决r0无收益初始化。仍不能称剩余榜首/前列、精确预测或命中概率：1–2ms是宽工程范围，没有冻结点预测；r0探索与r1确认不是同一效应估计；没有新upstream对照，不能扣旧7–9ms差额。整条前台算法充分性与调度关键路径仍未知，安装skill本批不再改正文。

[条件算法/代码索引/唯一追踪](evidence/br1_projection_boundary_trial_20261010/BOUNDARY_PLAN.md)将B06–B09列为产品准入缺口：current/exact中间消费者、拒绝时原clear副作用、稀疏presence/实际峰值费用、取消/重入。尤其外部failure context活跃时，融合失败先reportFailure，之后deferred clear可能被failed guard阻断，而原clear可能已成功；这是未动态验证的静态反例条件。下一先对这些必要合同做有限反例判别，再决定由原merge/painter明确表达初始化的完整替代；不先加新owner/队列，不续采本性能包。机制与受限价值通过，生产安全/资源、完整技能实施闭环、CP0及正式M6仍未完成。M6/M7/M8保持0/3、校准2/20、persistent默认关闭。

<a id="projection-boundary-production"></a>
### 16.169 清零/首层合成已落生产：独立CPU节省1.204ms，严格阶段非劣仍开放（2026-10-10）

产品 **8198c36ed7**，父c13c442493；[生产证据](evidence/br1_projection_boundary_production_20261010/README.md)将§16.168的受限原型收拢到原merger→plane→painter调用闭包。[原B01–B11矩阵](evidence/br1_projection_boundary_trial_20261010/BOUNDARY_PLAN.md)原位结算：具体独立首paint layer、无额外源投影/下层依赖/mask/style、非temp、源与更新域相交时才传本leaf局部clearRect；painter进一步限制over/format/default/独立manager/selection/stroke/wrap。旧clear域必须包含于实际paintRect，不扩大原composite准备页集合。公共clear、kernel、source读、原预算/claim/adapter和scheduler责任保留，没有原型pending TLS、第二owner/队列或设备延期保活；已有failure context内部TLS仍使用。

通过native-only私有入口阻止候选尝试的legacy隐式重放。准备失败未进callback时原clear+bitBlt一次；callback已进入后原native撤销、完成clear效果再向原上下文报告，不重放失败合成。双架构各880/合计**1760 passed / 0 failed / 0 skipped**，含30等价数据行、中间reader反例、初始化前/写后未发布的当前/固定旧view、真实kernel写后拒绝、prepare/prepublish finish失败、history/取消、硬满/稀疏及原adapter控制。真实压力两臂同拒绝/效果且reservations、活跃写归零，压力解除可重试；没有据此授全配置/所有异常/全平台资格。

生产观察保留19 merge/19 composite，fill13→0、成功冷准备132→96、新batch/成功seal32→19，13成功融合、失败0、初始化566464B；Undo/Redo工作量不增。r0独立64过程主CPU节省1.23975ms，但Undo CPU回退27μs [10,64]、wall回退32.25μs [6.5,60.5]；全部保留。r1只恢复空源setup阶段先clear的原顺序，在确认前另冻协议，不混池、不追样。

r1另16个ABBA/BAAB块/64进程，主CPU块差中位 **1.20375ms，pointwise95% [0.922,1.781]ms**，逐块相对节省中位**7.33%**；wall节省0.51025ms [0.371,0.7265]，端点仍projection-ready。事前工程范围0.5–1.5ms和δ0.5ms保持，主值通过；数量预测完整兑现。相比旧原型1.05775ms点高0.146ms仅作描述，不是两候选同批显著性比较或精确预测证明。

控制CPU节省：Undo −0.01825ms [−0.051,0.028]，Redo −0.02175ms [−0.0465,0.023]，Teardown −0.0095ms [−0.047,0.0145]；各wall区间也跨0。未再见r0单独区间排除0的控制回退，但点仍稍慢，**严格≤2%非劣未证明**，不得因主收益而授控制通过。本有限生产包停止；原失败、源patch、实际库及全部运行依赖/hash归档。代码在提交前测试，其源与提交逐文件一致；git元信息变化后的CMake再配置提示不伪称构建no-op。

本轮形成中层边界选择→完整生产实施→安全反例→独立收益的技能正例；安装skill不再改正文，仍不证明全局榜首/整链充分优化/调度最优。没有新upstream对照，不能扣旧7–9ms差额。**有限生产实现和主增量价值已交付，M6/M7/M8仍0/3，persistent默认关闭，原校准2/20、metadata分母及CP0 required保持开放。** 后继补正式门及业务阶段控制，不续采本包或重领36次冷准备/13套生命周期。

<a id="post-fusion-boundary-audit"></a>
### 16.170 融合后差额刷新与同批区域放大：原库额外CPU 6.390ms，下一候选尚未报价（2026-10-10）

**后续裁决：本节冻结测量保留；下文“下一主判别”的优先级已由[§16.171](#pagestore-equivalent-performance-scope)撤销。区域合并属于独立通用候选，当前整链差额不等于PageStore本体差额。**

产品仍为8198c36ed7、原image库与§16.169 candidate-r1相同。按[68进程协议](evidence/br1_post_fusion_boundary_audit_20261010/PROTOCOL.md)刷新固定upstream对照，再由新发现触发[4进程来源判别](evidence/br1_post_fusion_boundary_audit_20261010/QUEUE_ORIGIN_PROTOCOL.md)，合计72进程、216 QTest passed / 0 failed / 0 skipped；未改产品或增加生产收益。[完整报告/原始证据](evidence/br1_post_fusion_boundary_audit_20261010/README.md)及[候选算法/代码位置/唯一矩阵](evidence/br1_post_fusion_boundary_audit_20261010/CANDIDATE_PLAN.md)冻结当前结论。

原库8个ABBA/BAAB块的Stroke current−upstream CPU块差中位为**6.390ms，pointwise 95% [5.9365,6.763]ms**，wall额外2.8985ms [2.5445,2.9585]。Undo/Redo/Teardown额外CPU分别0.53025/0.750/0.40375ms；这些是对upstream的差额，不是相对上包的新增回退。不得从旧7–9ms中扣1.204ms替代新测量。

jobs模式的绘画/投影额外块中位约3.560/3.089ms，两者排序各胜两块，唯一榜首未证。该模式可相加责任均值合计7.438ms，原库差额均值6.336ms；跨模式1.102ms仍未闭合，不将重观察责任按比例分摊到原库或全领为净预算。

四个current lineage过程均为投影96次成功冷准备=56首次页+24次同页不相交区域+16次相交区域；19 native operation/seal，不能把40页复访全算冗余。来源判别四次均显示：四批27个原始dirty矩形互不重叠、面积164128；queue collect取包围矩形后19个merge实际访问207840，其中43008重访、704补洞。两侧沿用同一机制；当前页协议使这部分无效工作更贵。实际canvas在通知中同步readBytes后才压缩，不能用后置压缩删除前面真实读cut。

下一主判别聚焦原addJob内精确合并同列相邻区域、joinRects避免补洞；固定输入可构造16矩形/78页访问/164128像素，但尚无产品实施、净时间或显示控制验证。按候选矩阵Q01–Q07进入有界原型，不直接重写scheduler或改M7权限。几何改善未兑现时转绘画职责，禁止追加本包样本到通过。安装技能本批不改；03k补当前状态和实际反例，正向排名/预测校准仍开放。

**M6/M7/M8仍0/3、校准2/20、persistent默认关闭。** §16.169的生产收益与1760测试保留原身份；本批216次仅为诊断fixture校验，Undo/Redo/Teardown严格非劣、metadata分母、CP0 required及正式资格不变。

<a id="pagestore-equivalent-performance-scope"></a>
### 16.171 PageStore基础性能优先：通用收益与同语义替代效率分账（2026-10-10）

按用户补充，首要目标恢复为**PageStore相对upstream同语义能力的性能基础**。此前把两侧共有的queue包围矩形放大升为下一主线，混淆了减少业务工作与提高存储替代效率，现纠正。代码范围按责任划分：PageStore、必要adapter/manager及发布/历史/最终回收均计入；不是只测pagestore目录，也不禁止原业务owner表达必要语义。

[证据口径与P01–P05准备矩阵](evidence/br1_pagestore_comparison_scope_20261010/README.md)明确：§16.169的1.204ms只证明BR1内融合收益，upstream同样融合后的收益未知；§16.170的6.390ms是当前融合、upstream拆分策略下的实际整链差额，不能标成纯PageStore税。19→16任务/96→78页访问仍只是通用候选的几何构造。原始数据、失败、局部生产收益与产品8198不变。

下一先用当前PageStore加仅恢复原拆分的派生诊断控制，并清点调用闭包内其余通用算法/kernel/调度差异；只恢复clear拆分不足以自动授予同策略身份。核验输入、真实读者、版本/历史保活、失败与完整释放的合同，匹配共有策略后再冻结实测并排序额外成本。内部版本/复制/分配次数允许随合法算法改变。通用优化如要声称缩小后端差额，应分别测双方优化前后，差额改善为双方节省之差；单侧收益不可替代。Q01–Q07暂缓，不能以通用收益关闭基础问题，也不先指定metadata或锁为新榜首。

本轮只有文档与候选准入纠正，没有新产品修改或性能实验；安装技能不晋升。**M6/M7/M8仍0/3、校准2/20、persistent默认关闭**；既有阶段非劣、metadata分母、CP0 required及正式机会型handoff门均不变。

<a id="pagestore-equivalent-pipeline-diagnosis"></a>
### 16.172 同义公共存储基线：逐操作Fresh周转与缺失恢复副本（2026-10-10）

产品8198不变。按§16.171先完成[调用闭包差异审查](evidence/br1_pagestore_equivalent_pipeline_20261010/SOURCE_AUDIT.md)：clear融合可在派生库恢复拆分，但页分区/失败接线、通用参数外提和OVER透明像素修复仍不同，不能据此宣称整笔纯后端归因。因此另以双方完全相同的公共data manager操作测基础能力，不经画笔/区域队列/compositor。[本轮报告及原始证据](evidence/br1_pagestore_equivalent_pipeline_20261010/README.md)共87过程成功，368行存储矩阵/1472次manager寿命，freehand123 QTest passed/0 failed/0 skipped；生产/产品测试均0改动。

8块32过程的公共K16/N16、四寿命合计64次write，额外CPU H0为**8.256ms [8.052,8.442]**、H1为**6.976ms [6.924,7.257]**，逐块时间比中位24.77×/20.48×；全case额外14.239/14.282ms。区间均pointwise95%，不是整应用倍数或联合门。每次当前读、H1的Undo/Redo和销毁核验一致；额外exact reader、失败/预算合同仍单列，未证明全部费用可删。

机制两次/侧一致：K16一次覆写两侧各64次冷准备/COW；16次覆写当前1024次、upstream仍64次。H1的canonical commit降至4，但seal仍64。追加计划判别确认当前公共矩阵全为FreshPayload；未融合freehand的208次为116 FreshDiscard+92 FreshCow；全部recoverableBefore无效。native已接共同selector，缺恢复副本是首个不命中条件，不是尚未找到一个可放松的锁检查。历史起点A不能充当本操作前B的恢复副本。

原read区间额外process CPU约4.95ms，经另冻4过程前台时钟判别，K16/N16的read调用线程额外仅约1.73–1.80ms，其余线程约3.17–3.21ms；具体后台归属仍未闭合。不得把整段差额全给read循环定价。未融合业务控制的Stroke差额为7.439ms [7.0835,7.823]，仍含上述接线/kernel差异，不与旧6.390ms直接相减。

[T01–T08理想管线/代码索引](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md)收敛到新版本准备→交付→退出。五处首字节后拒绝已静态清点；下一形成原owner的准备前移方案，保持Fresh先核验完整接受/终结，再证明受控不可失败入口。无alternate原地覆盖属于未开放M7，8页fence不自动覆盖K16；不能把960次周转差直接许诺为93.75%提速。**P01/P02/P03的本次诊断完成；P04机制与主责任明确、合法净价未授，P05产品实施未开始。M6/M7/M8仍0/3、校准2/20、persistent默认关闭。** 原始79过程及两个各4过程追加协议分别冻结；构建/分析准备失败保留，未换样、未扩样到通过，技能资格不晋升。

<a id="pagestore-final-payload-trial"></a>
### 16.173 最终输入直接接纳：存储净收益成立，业务控制未闭合，候选未晋升（2026-10-10）

按§16.172主线实施[完整最终输入候选](evidence/br1_final_payload_pipeline_20261010/README.md)，保存在产品提交`20fd6d9897f5f0ef3f89d215df0cfb2e6a1b63b9`、`codex/br1-final-payload-candidate`分支。活动分支恢复8198及原image；本节收益不是当前检出产品已获得的收益。

packed完整页的provider已初始化独立Fresh目标，原实现仍进入可变Acquire/Prepare、writer reservation/pin/临时guard，再经BeginPublish/Publish成为Prepared。候选借原AdoptPreparedWrite直接接纳私有完成目标，seal跳过重复mutable publication；原selector/entry/claim/预算/ledger/proof/overlay/canonical/回收全保留。普通overwrite仍可继续修改pending，partial、无同步payload和RecoverableHandoff仍用原可变路径。没有新增owner或许可开关，也没有做M7原地覆盖。

K16/N16四寿命两次/侧机制一致：generation/pages sealed各1024不变，write pin/unpin各1024→0，前台metadata inputs3072→1024，installs1024不变，local transition sequences H0 2048→1024、H1 6016→4992。每页policy四转一与实际执行序列二转一是不同计数，不能给3072次转换直接定价为3072把锁或时间份额。

R3最终八块32进程父/新独立确认：write CPU节省H0 **1.18575ms [1.014,1.6975]**、H1 **1.35975ms [0.835,1.6405]**；完整case **1.3515 [0.8995,1.807] / 1.572 [1.0205,1.9675]ms**。pointwise95%，达到事前0.5ms工程价值目标，非正式M6family。另八块新/upstream的write额外CPU仍 **7.912 [7.7595,8.284] / 6.68675 [6.3565,7.2035]ms**，完整case额外14.63775/14.83875ms。不同批次绝对时间不同，不能将旧差额减局部收益当最新实测残差；read过程额外5.54/5.37ms也仍含后台。

原控制阻止晋升：r1/r2 freehand Stroke CPU父减新分别−0.14875 [−0.4245,−0.0135] / −0.30725 [−1.184,−0.023]ms。去掉临时guard搬移后仍未恢复；R3最后修订以编译期返回消除runtime wrapper，控制仍为 **−0.540 [−1.2865,0.2165]ms**，wall −0.209 [−0.4255,0.135]ms。最后区间跨零不确认回退，也不证明恢复或严格非劣；各源码批次不混池，不授wrapper独立因果价格。按事前最后协议停止，保存全部正负结果并恢复父产品，未做第四轮微调或追样。

R3 ARM64/x86_64各四套完整回归，合计**7266 passed/0 failed/0 skipped**，包含97新增数据行及full/partial、1/4/8/16BPP、旧reader、default并发materialize、provider/后页/proof拒绝、seal预算拒绝重试、handoff/Undo/Redo和close归零。r0的14个失败为原full-write pin预期，修正后各版均通过，失败原样保留。结构21 manifest/25 ownership/16 census、2222 API/29434边/19外部侵入通过；生产5文件+87/−25、测试2文件+122/−9仅存在候选。源码/库/协议/原始退出绑定见报告与验证文件。

[T01–T08唯一矩阵](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md)已结算本候选；它证明最终输入重复可变协议有局部价格，但不证明找到可回收榜首。下一仍审查完整Fresh准备/交付/退出及真实后台；重新接纳本候选前先定位普通可变控制回退，而非继续微调输出形式。物理1024对64周转、五处post-byte拒绝、M7依赖与K16超过8页边界仍未解决。技能完成负控制拒绝闭环，未升级安装版本；**M6/M7/M8仍0/3、校准2/20、persistent默认关闭**。

<a id="pagestore-write-protocol-design"></a>
### 16.174 写入协议的理想算法审查：准备、借用、私有完成须有界收敛（2026-10-10）

对活动8198和未接纳20fd完成[深入设计审查](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#write-protocol-design-review)，源码身份见[审查绑定](evidence/br1_write_protocol_design_20261010/identity.json)。本轮仅更新设计和原T01–T08代码/删除闭包，没有产品修改、新测试或新性能样本，不重新授予候选资格。

新确认的结构差距是：`prepareWrites`为预备冷页调用完整`beginWriteImpl`，进入Exposed、pin并构造guard，随后立刻reset；真正callback再次借用。预备不需要虚构调用者借用，但首次物理pin是否承担驻留验证须分别证明。另有三项设计耦合：InputBytesReady不表达最终性；entry的Prepared与metadata的Prepared语义不同；alias和候选seal用writable是否存在推断完成阶段。源码足以支持这些结构判断，尚不足以给P命中、可删物理pin或净毫秒定价。

推荐在原session/execution/coordinator内抽取完整冷目标准备，保留已有pending的直接热借用；preflight停在可借用就绪，真实调用者才获得guard。独立Fresh最终输入完成后由原AdoptPreparedWrite直接接纳；recoverable/fallback保留所需物理可变能力。原entry状态记录metadata已接受的Finalized，seal/alias/重试/取消共同迁移；其含义只是私有不可变，不是已经可见。禁止重复借用或隐式重开final目标，不增加第二owner、并列状态位或全热函数模板返回模式。

失败边界同步纠正：Fresh独立目标可在填入字节后撤销，不必把所有晚失败前移；覆盖当前可见backing才要求首字节前准备全部真实接受能力。输出终结中的使用前提、adapter已有预备节点的身份/归属检查、真实容量拒绝、revision竞争及发布后清理必须分开，不能把所有false都当随机分配失败，更不能用assert替换未证明的拒绝。

实施层次为：**A准备/能力/私有完成收敛优先；B单独operation直接canonical交付仅作条件设计；C物理原地复用仍受M7约束。** B须证明唯一anonymous client、无其他mutation/中间overlay消费者、原admission到commit的原子责任交接；owned或无memento均不够。C保持M6前置、外部reader/history/epoch保护及8页/256KiB/P99≤100μs，K16不以拆fence绕过原子性。A不以C开放为前提。

下一先有界统计实际mutable借用A、preflight guard P及可直接接纳final Fresh F，覆盖业务各阶段和前后台/末尾drain。现有guard模型约A+P+F，20fd为A+P，目标约A；P的物理pin不预报全删。20fd的1.186/1.360ms只是已测final冗余参考，不能再加一遍当新收益；P价格及新交接净增未知，不承诺追回7–8ms余差。freehand−0.540ms尚不能归因普通guard/wrapper/布局，亦不能据“普通入口零删量”认定整段业务F=0。新设计通过诊断准入后另冻协议，旧r1–r3不续采、不混池。**产品仍8198，M6/M7/M8仍0/3、校准2/20、persistent默认关闭。**

<a id="pagestore-whole-pipeline-blueprint"></a>
### 16.175 完整写入与交付管线蓝图：统一差量流向、接受规则与consumer闭包（2026-10-10）

依用户要求扩大§16.174的设计审查，原位深化[唯一蓝图第9–16节](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-blueprint)及[T01–T08修改/删除索引](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-change-index)，覆盖packed/cursor、fill/clear/copy/alias、普通与persistent history、native legacy/generic lease、overlay/canonical、adapter、memento/restore、collector/retirement/close。源码及静态consumer绑定见[扩大索引](evidence/br1_write_protocol_design_20261010/expanded-source-index.json)。本轮为设计交付，无产品修改、测试或新性能样本，不将“扩大范围”当性能准入。

理想表达为**原准入→专有生产能力→私有最终结果→最终差量→所需观察点的共同接受→原责任退出**。InputKind/物理计划/结果归属/交付目标正交；普通热借用不增加final分派，Finalized只记metadata私有接受。复用已有selector、OverlayChange、prepared overlay/commit和retirement record，不新建统一coordinator、第二write set或恢复队列。各入口保留真实线程、访问结束与失败范围；统一共同政策，不抹平history working值、checkpoint、overlay和canonical的不同观察点。

扩大后确认两类可疑交接：内部backend/memento提交先导出preparedPages、commit再回比原transaction集合，可研究用原CommitPreparation保护原delta直接形成必要投影；对外validator、provider动态校验及epoch不可变delta仍保留。native seal、generic finishWrite与conditional removal虽已共用prepared overlay，prepare/install/cleanup编排仍在各caller，须在原publication责任中统一完整接受政策，不能仅再包一层helper。

adapter审查不能只覆盖packed/cursor：clear发布后再解析presence；copy完成batch后独立refresh；history底层已有稀疏changedPages，但manager的restore/trim仍全量rebuild，重新创建wrapper；allocatedPages合并overlay含逐项线性find/erase。目标是已知差量贯穿兼容交付，在原claim/gate下准备真实安装能力，合格稀疏路径只处理D；必要全量/default路径仍保留其N规模工作。tryAbort已有先备后换的正确原则可复用，不要求每个小操作复制整表。以上静态路径差异不是已经复现的安全漏洞，也尚未获净价格。

成功、拒绝、重试、取消和最后free已统一列入接受点表、锁上下文表、修改删除矩阵及反证清单。发布后的普通失败分支只能在其失败来源被证明消失后删除；checkpoint输出拒绝只重试输出；provider retire已接受后不重发；原collector/retry进度不重写。新增内部借用必须贯穿原claim/close保护，不把一个trusted布尔当授权。

数量预测分别给出P+F临时guard、内部commit导出、clear presence、稀疏adapter和全量合并的条件删量，未测价格仍未知；H0的64次commit与H1的4次commit不同，不能把H1的64次seal都领作提交往返。restore/trim的N对D模型和allocatedPages最坏D×(N+D)的合并放大不冒充K16 write瓶颈；旧1.186/1.360ms与相关机制不重复相加。按蓝图先有限诊断，再按完整责任迁移并同步删除；单独operation直接canonical仍有条件，M7物理复用不是本蓝图的隐含前提。**产品仍8198，20fd未晋升，M6/M7/M8仍0/3、正式校准2/20、persistent默认关闭。**

<a id="pagestore-blueprint-soundness-review"></a>
### 16.176 管线蓝图健全性复审：接受事实分清，旧分支按真实consumer彻底核销（2026-10-10）

已原位修订[唯一蓝图](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#soundness-and-deletion-review)及[原T修改/删除矩阵](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-change-index)，复审源码绑定见[review-source-index.json](evidence/br1_write_protocol_design_20261010/review-source-index.json)。上版方向保留，但三个实现前提必须纠正：metadata已Prepared不代表待替换alias已接受；memento.changedPages不自动覆盖任意current到retained target的整根恢复；adapter无晚分配不等于所有身份/归属拒绝已经消失。前两项有明确源码反例，后一项须以原claim、表寿命及覆盖关系证明，不用新增全量扫描或改断言替代。

entry沿原quint8区分PrivatePrepared与AliasAccepted，删除资源有效性推阶段时同时覆盖writer成功而alias拒绝、alias成功而proof拒绝两段重试。restore必须证明实际差量覆盖，否则维持先备后换的全量算法；非相邻恢复还要检查底层metadata与整根一致性，目前是设计资格缺口及待验证风险，未宣称复现产品bug。共同overlay接受收紧到原aggregate，caller保留各自锁转换和动态复验；不能增加统一runner或回调模式再留三份旧恢复树。

补齐T04.12文件read失败的第三个rebuild caller、T06.3普通/rough legacy copy、borrowed packed、planar四个raw cache恢复caller，原矩阵共33子项。蓝图给出九组同批删除契约，覆盖旧函数/声明、模式参数、阶段别名、回滚与重试附属状态、测试替身及诊断consumer。rebuild全量语义有时必要，但原“接受后清表再分配”的实现不应因此永久保留；反之仍有真实raw消费者的恢复不能冒充死代码删除。trim全局活动拒绝也要随重建迁移重新证明其所有用途，既不永久冻结也不直接盲删。

高效性出口新增零删量路径的分派/查找/锁/分配账、额外adapter验证成本、实际restore差量生成成本，以及清理顺序/资源峰值验证。最终分别裁决行为、净简化与性能；没有新收益价格，不能承诺追回剩余7–8ms。**本轮仅复审及蓝图修订，生产/测试代码未改、产品删除量0、未运行新性能样本；8198、20fd未晋升、M6/M7/M8 0/3、正式校准2/20均保持。**

<a id="pagestore-pipeline-refactor-core"></a>
### 16.177 完整管线实施首包：冷准备、真实借用与私有完成分离（2026-10-10）

**最新版本统一（2026-10-12，ed0f229821）。** CPU final/mutable/source/alias/recoverable统一为原entry私有结果，通用writer fallback、封印快照往返及测试专用壳删除；captured full/range例外共用原exact-ref保护和释放队列。6760文件全量检索17退役符号归零，生产净−170行；真正异步lease与参考模型能力按具体consumer保留，无第二owner/队列。双架同库10816/0/0及结构门通过。固定48过程主格读写省1.065M指令、process省0.944M；CPU节省−0.418125ms [−1.376591,0.299878]，收益/非劣/包门未过。新upstream读写差额52.407M/3.535ms仍未证明必要，完整process余76.195M/5.936ms。range保留精确K页，新增688+16K B，未采用扩大历史保留的完整root替代；锁批次、物理预算合批与proof重复验证仍可优化。后续仅沿新版推进，M6/M7/M8 0/3、calibration2/20、默认关闭保持。[完整报告](evidence/br1_pipeline_refactor_20261010/unified-rw-r1/RESULT.md)、[原33行实施明细](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#unified-rw-implementation)。下方各“当前/下一”均为旧批冻结记载，不覆盖本裁决。

**当前候选计价（2026-10-12）：02bccf1d12。** [完整设计及原33项](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#resident-operation-implementation)已完成同一候选；[实现/数量/安全](evidence/br1_pipeline_refactor_20261010/RESIDENT_OPERATION_RESULT.md)保留H1 backing1088→192、896reuse、960直接退出、H0 overlay68→0与双架10626/0/0、实际安装544窗口/架alloc/free0及结构资格。重启后[126过程计价](evidence/br1_pipeline_refactor_20261010/RESIDENT_OPERATION_PRICE.md)通过全部身份/语义/退出：H1独立确认指令省16.7419%（单侧95%下界16.5468%）、CPU省2.8586ms（下界2.4320ms）、前台增费上界0.1601ms，局部门通过。进程减前台少37.1641M指令而前台多7.1553M，write多8.4426M；upstream余122.6434M/9.1133ms，write占余差66.74%/55.33%。5个存储CPU控制、业务Stroke收益和Undo/Teardown非劣、完整资源仍未闭；Stroke省0.4158ms [−0.3950,0.6205]，不能称绘画改善。下一原T02/T04审查复用写的准备→收费/metadata转换→接受，不补样追门。生产净+625行/新facts/保留费用保持，已验收基线仍11c689，候选未push；M6/M7/M8 0/3、校准2/20、默认关闭。旧native断言后OS退出失败与错误锁归因修正保留。以下为各自冻结状态。

**下一完整设计（2026-10-12，产品仍11c689）。** [蓝图§19.15](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#resident-operation-pipeline)重新从公共cut、失败前值、真实reader与预算推导，选定操作级准备/接受、原版本证明/布局归并、H1有界物理容量循环及合格H0直接canonical作为一个完整验证对象。明确cold表示上限、原owner/锁/原子接受及全部出口；[源码/条件事件索引](evidence/br1_pipeline_refactor_20261010/resident-operation-design.json)关联原33项，不另建状态表。H1条件physical1088→192、未保护旧Prepared进入Historical960→0、内部proof及非默认descriptor独立节点各1088→0；必要generation/接受和真实保护保留，新增字段/checkout/保留/失败/drain全部扣回。H0过渡overlay68次为代码路径推导，真实canonical仍68，不能按31.2M scope全领收益。原地K16仍不绕过M7的8页fence，亦不全盘改RC/删除GC。该设计已可指导完整实现，实际净指令/毫秒未知，不授榜首/生产收益资格；无新基准/产品/产品测试改动，M6/M7/M8 0/3、校准2/20、默认关闭不变。

**当前预算闭环裁决（2026-10-12再次复审，产品仍11c689）。** [集中报告与更新图](evidence/br1_pipeline_refactor_20261010/BUDGET_COMPLETENESS.md)明确：仅冻结同义用例的支出加法已闭合；必要/额外/可删机制、完整实际交接和净价、资源/合同资格仍有缺口。即时960个ActivePending可接和192/196/256模型不等于retag/metadata移交已验证；60/64同义、2次冷压力失败、资源观察门和旧live-copy欠项均保留。旧H1慢态仍是机制推断，不能声称全锁/调度最优。当前图与机器账承接donor事实并明示未知；原CPU树标注mode0非plain，数值/分母保持。有限完整候选只需补其合法性、净价与回退依赖，不要求先穷举全部锁/平台；不能以此授最优生产方案。按[蓝图§19.14](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#budget-closure-recheck)执行，原33行不改状态，无新基准/产品/产品测试；M6/M7/M8 0/3、校准2/20、默认关闭不变。以下为各批冻结裁决。

**最新交接补缺（2026-10-12，产品仍11c689、零产品/产品测试改动）。** [实测与设计](evidence/br1_pipeline_refactor_20261010/DONOR_LIFECYCLE_DESIGN.md)完成2能力＋6正式诊断过程、512个公共case记录、7900项复核。普通H1旧proof撤销后960个backing仍收费ActivePending，原prepare/claim/cancel 960/960成功；下一写896个有来源目标的metadata及owner记录均已退出。纠正上轮过宽推断：Historical不等于RetirementDebt；现有即时handoff接口已可接，缺的是提交退休前的跨操作保留，不能从已交队列的record反向取回。clone64次物理claim拒绝、native4次binding准备拒绝，故metadata idle不授写许可。最小设计以原transaction/page槽保留最多1份有收费工作容量，原owner及预付退休责任唯一，实际checkout才独占；不增加960次重复保留时claim。2616状态有界模型把四寿命K16/W16源非默认physical建立量1088条件降至192，无外部holder少896；保留一页/完整clone时为196/256，非优化后实测。实际metadata原子移交、retag、压力/晚释放及完整净价仍未验证，不授生产方案榜首；仅将候选收敛为明确可反测的完整替代，原CPU/指令预算及旧门禁不变。按[唯一蓝图§19.13](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#donor-lifecycle-capability)与原33行推进；M6/M7/M8 0/3、校准2/20、默认关闭保持。以下“最新”为此前冻结账期。

**最新预算完整性裁决（2026-10-12，产品11c689、无新增产品/测试/基准）。** [完整性报告与图](evidence/br1_pipeline_refactor_20261010/BUDGET_COMPLETENESS.md)从冻结原始包重算1393项，原33行六列/12流程覆盖保持。H1原库额外153.246962M＝write73.659212M＋显式read13.420408M＋其余前台15.244819M＋进程减前台50.922523M；scope on当前另有11.235415M未命名角色工作及−0.114702M两层窗口修正。旧11.962375ms CPU图保持原账期。支出归属已闭合，合法完整替代净预算未闭；99.7M成组当前责任不能授予净收益榜首，上一轮复用选择收紧为待比较候选。当前源码的metadata删除先预备/提交RetirementDebt，现有handoff只接Current/ActivePending，必须补原owner持有、收费类及退出→复用交接，不能简单连接接口。15%指令门是27.469453M工程价值阈值，若仅达此门仍余125.777509M upstream差额；不宣称已接近upstream。下一按[唯一蓝图§19.12](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#budget-completeness-review)先闭合法路径及联合事件差，再以有限完整替代定价；只补候选依赖的资源/失败/控制，不原样续采scope，也不要求无关全平台/全锁穷举。净预算及生产方案仍null，M6/M7/M8 0/3、校准2/20、默认关闭和旧控制欠项保持。下方各“最新”仅为此前冻结裁决。

**最新指令责任裁决（2026-10-12，产品11c689、零产品/测试改动）。** 54个根责任过程＋4个细分过程全部自身语义/身份/退出通过；同批原库H1额外153.246962M条，pointwise95% [151.456203,155.037721]M，前台102.324439M、其他线程50.922523M。派生注册角色支持后台主要是reclaimer；cold53.95M、history25.19M、retirement task20.60M构成最大的成组责任，H0另有31.20M canonical责任。CPU观察粗门失败，约99.7M observed指令不能冒充可删价，旧6.84倍差额也不能视为必要管理费。下一有界候选为原owner内旧不可见Prepared目标及完整身份复用：H1条件1088→192、少896非默认对象，generation/必要写字节/接受点仍保留；不是82.35% CPU预测。原33行索引已列donor唯一持有、不可达凭证、retag旧handle拒绝、收费/压力、失败/drain五项设计门，未完成前不晋升生产；本次没有兑现收益，不重跑本包scope追精度。原型须达到事前指令15%工程推进门及原CPU净收益门，独立确认，不重复已否决的前台立即销毁/私有票据小项。详见[指令实账与限制](evidence/br1_pipeline_refactor_20261010/INSTRUCTION_LEDGER.md)、[唯一蓝图§19.11](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#instruction-lifecycle-design)。M6/M7/M8 0/3、校准2/20、默认关闭和原控制缺口保持；下面各“最新”为当时冻结批次。

**最新慢过程归因（2026-10-12，产品11c689、零产品/测试改动）。** 68自然过程与72对称QoS干预全部自身语义/身份/退出通过，42760项复核。3个自然慢态同过程指令仅多0.3～1.0%、P核CPU份额2～49%，CPI/有效速率变化解释67～122% CPU增量；H1干预off组current 13.256→47.0585ms、upstream 1.3405→6.114ms，说明执行条件能显著放大。旧32.070ms最有力解释为同类执行条件变化，但本轮自然H1未重现>20ms，旧事件无内核计数，归因仅中等置信推断。自然H0/H1观察门通过；干预default/background门均失败，其on机制与off效应分账，不移授精确份额。正常P核H1额外CPU中位11.5975ms [11.112,11.808]，约6.84倍指令；counter均值额外11.5341ms可代数分成8.3409ms数量项＋3.1932ms每指令成本项，均非合法删除预算，不替换旧图。事前1.5～3.5倍预测上限未全兑现，不追加修饰通过。下一保留同过程执行条件观测，产品侧仍按原管线寻找额外指令的具体来源；A完整机制价、B全锁因果、C/D缺项和E净预算不自动关闭，M6/M7/M8 0/3及旧资格保持。[完整归因/置信边界](evidence/br1_pipeline_refactor_20261010/SLOW_PROCESS_ATTRIBUTION.md)、[唯一流程账§19.10](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#slow-process-attribution)。

**最新沿预算图补数（2026-10-11，产品11c689、零产品/测试改动）。** 固定36公共过程、64格中60同义，4格坏尾导入均拒绝但副作用不同，禁止性能比较。真正plain H1有32.070ms慢态，新批额外CPU中位11.93675ms [11.439,20.803]不替换旧图11.962375ms均值。12098796条资源事件/5557317个身份配对：H1 payload周转1092/132、峰值49/33，provider/binding/owner各1088建立、峰值48、末端0，root128/峰值32；累计960不能当峰值删量。H1观察扰动门未过，峰值/寿命不移授原库。current外部追踪64case前台状态闭合，upstream缺前台tid，未解释同一plain慢过程。压力12过程682/2/0，两模式均有冷基线断言失败；573680 B增量中557056＋240 B直接观察且最终释放，16KiB与原生控制收费一致但未独立打点，原库暖序控制通过，原失败保留。A/B及C/D类型、移授、压力分布/合同缺口未全闭，E仍未选定；不实施产品优化或追加到过门。详见[补数账本/图](evidence/br1_pipeline_refactor_20261010/BUDGET_COVERAGE_LEDGER.md)、[64格](evidence/br1_pipeline_refactor_20261010/BUDGET_ENTRY_MATRIX.md)、[同一流程账§19.9](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#budget-resource-entry-coverage)。M6/M7/M8 0/3、正式校准2/20、默认关闭及旧live-copy/业务控制保持。以下为此前冻结批次。

**预算总览（2026-10-11，仅整理，无新采样/产品改动）。** [预算图与完整账本](evidence/br1_pipeline_refactor_20261010/PERFORMANCE_BUDGET_LEDGER.md)固定原32个mode0过程，重算8case共576项加法核对；K16/W16/H1额外process CPU均值11.962375ms，write/read/reclaimer合占88.09%。这是阶段/线程归属，不是可回收预算；合法全设计净价仍未知。后批工作事件、资源数量、两个候选净价及旧整包收益独列，不跨批抵扣。原33项状态、补数缺口与以下最新B裁决保持。

**最新补数B：操作/任务/计数关联闭合，完整等待因果仍开放（产品11c689、零改动）。** 固定36过程全部像素/历史/身份/退出通过；112313事件含12096个phase、9084次成功enqueue→dequeue→job、72965个有限gate获取，288个case/role工作分配及1656项生命周期数量恒等通过。H1退休1088次尝试全成功，history版本1280/root1600访问保持，所测重启/重试为0；前台退休80–128、后台960–1008，任务数与分工仍变化。首次setup单列：current进程首case首manager约1.37–1.46ms，其后约0.19–0.27ms；upstream首个也约0.87–0.96ms，不能全归PageStore稳态成本。H1 process观察扰动1.9545ms [−2.4410,2.2425]未过±0.75ms，H0亦失败，事件时间不作机制单价或可删预算。所测gate不覆盖全管线锁/持锁/内核blocked，端点CPU不证明驻留/频率，mode0慢态保留而未归因。B只完成有限子集，A/C/D仍有空格，E未选设计；下一补资源/入口并保留实际执行条件缺口，不续采同类时钟。详见[同一流程账§19.8](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#execution-work-correlation)、[36过程证据与审计](evidence/br1_pipeline_refactor_20261010/README.md#execution-work-correlation)。M6/M7/M8 0/3、校准2/20、默认关闭及live-copy/业务控制欠项不变。下方为前批冻结结果。

**最新补数A：观察器能力试验完成，目标机制价格仍未合格（产品11c689、零改动）。** 复用原产品派生对象，最外层调用树按1/4抽样，后代完整计时，实际数量与入选时间分开。固定68过程全部通过语义/身份/退出，1360个case/role随机序列和exclusive守恒校验通过。H1时钟比例24.98%，前台on−off 0.0792ms [−0.5546,0.2889]通过单项粗门，但process 0.0667ms [−0.9475,0.4810]未过±0.75ms联合门；H0也失败。八case仅0/2/4/5/6通过观察联合粗门，不外推目标case或M6。最后一块两个current-off过程H1 CPU14.968/34.149ms，写/读/后台共同变慢、drain只多0.023ms；不能只归时钟或漏尾，也不能断言外部噪声/E-core。主case机制估计不作排名或删除预算，全部数据保留，不续采、不改优化方案。下一按B关联实际执行条件与重试/锁/调度事件，C资源与D入口独立补齐；完整设计未选定。详见[同一流程账§19.7](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#sampled-cost-capability)、[68过程证据与复算](evidence/br1_pipeline_refactor_20261010/README.md#sampled-cost-capability)。旧正式资格、业务控制及live-copy欠项保持，下文均为此前冻结批次。

**最新全流程账本审计（2026-10-11，产品仍11c689、零改动）。** 按用户要求，先补全面事实再比较完整设计；本节下方各批“下一/优先”不再授权优化选项实施。原33项已映射12条完整流程，状态仍只在原矩阵维护。[蓝图§19](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#full-flow-ledger-audit)统一算法/consumer、所有当前方案、未知价格及补数门。原106过程内32个mode0过程重新逐块对账，H1额外CPU算术均值11.962375ms中write4.649351、read1.698595、其余前台1.424722、reclaimer4.189938，具名其他线程和边界余项保留；不能与170过程的阶段数拼账。本次仅新增4个基线数量过程：Fresh/provider/binding/owner/proof各1088建立/退出；metadata和descriptor各1152建立，包含64虚拟default和64最终容器记录；物理free1092对upstream132。两次总量相同但H1前台退休96/64，证明不能把线程工作转移当净删除。Pending1096只测发行，不冒称所有对象全寿命已闭。H1独占机制价格、等待因果、资源峰值、全入口性能和合法全设计净价仍未齐；先补数据，不预选复用、collector或读侧，不续做微项。详见[证据/协议/复算](evidence/br1_pipeline_refactor_20261010/README.md#full-flow-ledger-audit)。正式资格、原业务控制和live-copy失败保持。下方为此前冻结批次。

**最新同步退休证明净价（仍11c689，产品最终零改动）。** 44成功过程验证每allocation私有Pending可被provider原有同步Succeeded证据替代，真实物理释放后才返回exact operation/replica，原pin/last-use/replay/owner/异步语义保留。K16/W16申请1096→8、Allocation记录56→24 B；初报1092删量多算4个manager默认对象，实际1088，Fresh/rows/retire/free保持。ARM64六组5233/0/0、4数量、34plain时间通过；1构建失败和1新增测试压力布置失败保留。H1完整process节省中位**−0.0155ms [−0.265,1.0285]**，均值前台0.064357＋其他线程0.145143＝0.209500ms，含尾部。未过0.75ms下界推进门，四文件候选撤回，不追加样本；不是证明零收益，也不能解释主要差额。原T03/T07登记本项未合格净价，下一仍是完整backing/binding/owner身份建立和退出，T06一致读保持竞争解释。详见[预测/差异/完整索引](evidence/br1_pipeline_refactor_20261010/LIFECYCLE_DECISION.md#synchronous-retirement-proof)、[证据](evidence/br1_pipeline_refactor_20261010/README.md#completion-net-decision)。整体机制净账、原控制、两个live-copy失败及M6/M7/M8资格不变；下段为前一批。

**当前11c689生命周期净价判别（产品/产品测试改动0）。** 最新56成功过程完成一个合法替代的净价：已接受、从未进canonical的旧Prepared可由原metadata保护/债务检查直接回收，H1两次均960命中，但逐页前台执行令完整process增1.62125ms [0.838,2.793]、前台增1.83310ms [1.27506,2.60490]；其他线程仅省0.26127ms。原型否决，不追加样本、不落产品。r1 ARM64六组5233/0/0、两过程2040次实际metadata reserve前bad_alloc接续通过；初版漏catch由静态复核发现并保留纠错。另4过程证实H1当前payload请求1092、cache hit1076/1042（95.4–98.5%），所有payload归还进cache；对象free不等于系统malloc/free。下一仍沿原T03/T04/T07建立/解绑完整身份，条件双工作目标加undo origin的H1可构造数量为192对当前1088，条件少896；无原位生命周期/预算/ABA实现与净价前不批准新pool。详见[消费者/预测/实际/代码索引](evidence/br1_pipeline_refactor_20261010/LIFECYCLE_DECISION.md)、[完整证据](evidence/br1_pipeline_refactor_20261010/README.md#lifecycle-net-decision)。整体净预算、原业务控制、live-copy两个exact-view失败、M6/M7/M8 0/3及校准2/20不变。

前一106成功诊断过程＋1观察器失败capability按冻结身份保留：K16/W16/H1额外process均值11.962375ms＝前台7.772667＋reclaimer4.189938＋monitor0.002313−swapper0.002875＋线程/端点残差0.000333；reclaimer差额中位4.21875ms [4.035,4.278]，额外drain尾0.02225ms。含边界读数/drain，不能与新净价混加或改写原170过程整包收益。H0/H1 Fresh/rows/retire1088，upstream副本请求128，实际free1092/132；r1/r2细分扰动门失败。线程净账和物理数量闭合，细机制总体净预算未闭。[前一机制账](evidence/br1_pipeline_refactor_20261010/README.md#mechanism-net-ledger)、[唯一33行及§18](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#current-cost-ledger-blueprint)。

**当前11c689成本账补齐（产品/产品测试改动0）。** 三方整包102过程＋两个34过程粗责任诊断，共170过程；原安全库身份相同。较重构前8198，H1完整前台省2.175ms（17.08%，95% [11.48,19.88]），业务Stroke省0.609ms（3.77%，[2.32,7.17]）；相对upstream仍多8.330ms [7.659,9.399]、6.992ms [6.764,7.102]。H1额外前台均值8.517ms，其中write4.936/read1.951；另有同期其他线程4.610ms，不能归作已证明必要管理成本。17张阶段账逐块守恒，原33项已补必要/删除/新增及合并计价列。业务33次非空commit仅34–35次准备、root重基0，直接commit约1.038ms，owned中间段0.149ms；通过±0.75ms粗规模诊断，不替代旧±0.2ms或净预算。存储H0/H1均1088次cold、68次seal，commit分别68/8；H0粗责任精度成立，H1观察on−off 0.737ms [0.367,1.812]未通过，全部样本保留无扩样。因此下一责任优先逐页目标准备与生命周期周转、读侧保护/归还；不能再把小额中间表示当多毫秒主线，也不凭数量删除失败恢复或绕过M7。业务Undo/Redo/teardown和整进程非劣仍未全闭、两个live-copy exact-view失败及M6/M7/M8 0/3保持。[当前完整账本与复核](evidence/br1_pipeline_refactor_20261010/README.md#current-cost-ledger)、[蓝图§18与原33项](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#current-cost-ledger-blueprint)。旧批次判断保留各自身份，不跨批相加。

**前置11c689读终结实施：删除闭包完成。** 父库反例证明footprint分配异常逃出原债务准入边界，已在OwnerLedger转为拒绝；初次handoff和原queue重试复用同record/reservation。通知已由collector接受后，cancel/lease/last-use/captured在解锁pump前移交原记录，删Released/Collecting、5布尔、1计数器和三处读侧异常树；metadata真实拒绝、last-use、captured逐版本processing、GC rescan/repeat及退休重试仍有真实消费者。生产+71/−127、测试+112/−5，无新owner/队列。定向31/0/0，双架六组10466/0/0，结构门与6工具测试通过；903身份及86原始成员核验。此为健全性/净简化，未运行新性能比较，不能改判原H0/Setup信号或计入upstream收益。T02.4净预算、全包同义比较、T06.3两个live-copy exact-view失败及M6/M7/M8 0/3仍开放。[接受点、全部caller/删除/保留、失败与最终证据](evidence/br1_pipeline_refactor_20261010/README.md#read-terminal-deletion)。原33项原位更新；下文旧检查点按各自身份解释。

**6f769后反面结果归因：生产/测试改动0。** 12个固定观察过程显示Setup未执行两个metadata保护入口或原GC/读释放工作，89.36–92.15% CPU在共有image创建，内部责任及二进制间接影响未细分。H0父/新全部24计数相同，均1088真实历史节点/扫描/移除及68调度；H1实际删1968–1984空节点、必要历史工作保持。不能用该小诊断重判原Setup/整进程回退或H0非劣。下一原T07/T08先反测退休记录的provider footprint异常接续，完成read终结删除闭包；H0“直接交原退休记录，免短暂历史/GC”的条件算法须与cold/commit/physical同分母定价，不能按次数批准新框架，也不越过M7门。接受点逻辑保护、epoch mutex callback不可重入、late capture及可选准备失败均有明确前置。[完整结果/代码索引/原始包](evidence/br1_pipeline_refactor_20261010/README.md#setup-h0-attribution)。当前源码、双架资格及M6/M7/M8 0/3保持。

**最新6f76902d4a：T07保护释放事实交接已实施并实测。** 复审发现历史默认与captured abort可能尚无work，故不能让read只requeue；独立getter备选因已有否决证据在采价前撤回。最终由metadata原ReleaseRead/AcknowledgeLastUse/ReleaseCapturedVersion在原锁内返回短寿命历史通知，ReadCoordinator在原Store gate交原requestKey；删除候选key数组/循环及临时getter，不新增锁、查找、持久状态或队列。生产+27/−22、测试+43/−7，双架10454/0/0、结构门和6工具测试通过。4观察过程新work698、804→208、212、全部历史移除324保持；68过程同义存储K16/W16/H1完整前台CPU省0.903ms [0.533,1.021]、业务Stroke省0.630ms [0.172,0.955]。H0/Undo/尾控制尚未闭，Setup和整进程有回退信号，整体性能不能通过；下一核对这些反面责任，不继续按GC节点数排名。未测新upstream，不跨批相加，不授精确预测闭环。[算法、全部删除/保留、净价与原始失败](evidence/br1_pipeline_refactor_20261010/README.md#history-release-event-delivery)及原33项更新；M6/M7/M8仍0/3，live-copy语义缺口保持。以下“最新”属于各自冻结检查点。

最新净价与归因（产品仍cb942b6eff，未改产品）：68个未插桩过程确认业务Stroke CPU节省0.401ms [0.2405,0.7145]；4个count-only过程全metadata pass由18–20降为0、新建work由1200–1230降为706–818，全部历史移除仍324。证据说明过大的维护范围会放大节点和后台工作，不能统称必要管理费；存储基础端和所有控制尚未获资格。下一按原T07检查work准入是否在无历史时产生空工作，先证锁序/未来登记/失败恢复和新增查询净价；不另扩direct-canonical框架。所有输入、失败和字面bootstrap核验见[本轮净价与计数](evidence/br1_pipeline_refactor_20261010/README.md#epoch-exit-net-price)。以下“净价未知”仅指各包当时冻结状态，整体M6和live-copy仍开放。

最新产品**cb942b6eff6d2afe19f87311e1febf2ccb98c655**：生产+22/−16、测试+100，最终双架六组合计10450/0/0；结构门及6工具自测通过，原33项/旧删除承诺复核。本轮完整身份和原始失败已冻结，净时间未知，下一补原T08.2增量价。

最新原T07包补齐事务base退出的D外回收，并以“最后逻辑保护消失”代替“base不是current”的宽泛重扫条件；普通事件只访问原H，缺key登记失败才补扫N。snapshot前台重复H扫描同步清理，无新owner/状态/队列。前置反例是commit/abort各遗漏16KiB，以及受保护事务/快照多扫1页；净毫秒收益未知。原T02.4的34过程粗计时扰动门失败，不授direct-canonical重构预算。代码索引、原33项及完整反例见[本包](evidence/br1_pipeline_refactor_20261010/README.md#epoch-exit-closure)，统计结果见[定价判别](evidence/br1_pipeline_refactor_20261010/README.md#owned-terminal-budget)。本包不关闭live-copy两个exact-view失败、原0.723ms业务回退或正式M6。以下按前置包冻结资格解释。

产品`3f2826d4647b75a49488ad88b8f499d214af62f3`相对8198完成共同冷准备，preflight不再制造guard/伪Exposed；完整最终Fresh输入不借用未消费的可写guard。原entry明确PrivatePrepared和AliasAccepted两次接受，保留普通overwrite再借用、真实handoff、动态provider/proof验证及取消终点。`preparationOnly`、`recordPrepared`、旧Prepared状态及资源有效性阶段推断已删除。生产+383/−220，测试+188/−9；净增来自原冷热混合路径的职责分离，完整重构仍待收敛，不能称全管线已简化。

双架CpuMutation/manager/PhysicalClaim/ResidentRead共**7270通过、0失败、0跳过**，99新数据行/架覆盖最终输入终结、真实存储拒绝重试、alias前后接受点、强制handoff和资源释放。全部实际加载身份及源diff核验；首轮14个旧pin断言失败、DYLD身份收集错误、一次构建失败均保留。固定4进程机制观察证明K16/N16四生命周期pin1024→0、version inputs3072→1024，Fresh/sealed/install均仍1024。预备物理驻留pin有真实用途保留，计数不当作时间占比。

[事前协议、结果及完整失败证据](evidence/br1_pipeline_refactor_20261010/README.md)、[可复算审计](evidence/br1_pipeline_refactor_20261010/core-audit.json)；状态只在[原33子项矩阵](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-change-index)原位结算。共同发布、adapter/copy/history恢复、内部commit导出仍继续；新实现未插桩性能/业务控制/完整upstream差额未测，旧20fd时间不移授。完整重构目标未完成，M6/M7/M8与默认资格不变。

随后`4dc89bada34d746364a5eb3ed04c40f962d1c274`完成三caller的共同overlay清理，删除collected及原collect入口，候选metadata处置→旧proof交接→候选和allocator尾释放由原aggregate负责。native顺序保持，generic/removal改变为先处置metadata；新增的一次短owner重取净价未知。双架再次7270/0/0，真实满额/延迟回收测试首轮发现128B allocator尾并修复，全部失败及[审计](evidence/br1_pipeline_refactor_20261010/overlay-audit.json)保留。生产+56/−51、测试+35/−12，无新持久字段/owner/队列。动态observed复查、producer释放和取消拒绝接续有真实用途保留，不能作为死分支删除；完整方案仍开放。

`7c36dceb858b06b0dbb3ed66adc7ef21a1c34a58`进一步将四seal终点改为明确SealMode，统一fill/operation的batch交付及最后槽撤离，删除重复execution.finish/changed清空和已证不可达的privateCancelled/abort分支。checkpoint try-lock、history先安装pending adapter、clear barrier、late unlock及锁外source析构保持。复用原真实边界测试，双架7270/0/0；生产+52/−58、测试0。[审计/运行身份](evidence/br1_pipeline_refactor_20261010/operation-audit.json)与[完整原始记录](evidence/br1_pipeline_refactor_20261010/operation-raw.tar.xz)保存。下一仍为adapter/copy和内部提交完整责任，结构收敛不新增性能资格。

`ccbf0bcb0db6f13bab5c87ca03936439f25ee04d`完成packed/cursor/clear三caller的prepared adapter消费：删除晚业务拒绝和隐式unlock，clear由producer直交最终presence，删每次发布后的重解。coverage唯一性、原admission、表寿命/屏障与两种hash的不可拒绝安装条件逐条核验；不增加逐页再验证或新登记表，hash公共foreign/closed/consumed拒绝仍保留。双架四组加hash8边界函数共7290/0/0；首轮101个诊断边界/旧计数失败、修复与运行身份全部保存，[审计](evidence/br1_pipeline_refactor_20261010/adapter-audit.json)及[完整说明](evidence/br1_pipeline_refactor_20261010/README.md)。生产+62/−32、测试+6/−2；净价仍待全包，copy和三处history/restore/read失败rebuild未完成，不能宣称完整重构完成。

`081afa7072adeb6035c80dcfa211ca0d8603e097`将copy接回原范围准入、共同batch结束及prepared adapter，删除发布后presence重解、专有容量helper和三参数refresh。真实并发反测发现旧target在等待后仍误判no-op，已改为固定source、预读目标几何、准入后唯一target capture；只在原请求的实际裁剪矩形变化时前置拒绝，范围外extent变化通过，不额外创建capture或逐页锁。最终双架四组7364/0/0，首轮计数/合同预期失败与独立错误像素反例全部保留，[审计](evidence/br1_pipeline_refactor_20261010/copy-audit.json)、[机制与保证增量](evidence/br1_pipeline_refactor_20261010/README.md)。生产+113/−48、测试+138/−44；一个surface查询、矩形重算和K页准入/准备的净价未知，不能作为K16 write或upstream收益。内部commit及三类history/restore/trim/read失败尾继续开放。

`ce903fe3e91dd4826d5d2e14374771da8dd2e9ac` 完成内部提交表示收敛：原 CommitPreparation 内直接借用 publication delta，公共 validator 后进入同一核心，epoch/history 必要输出保留；删除内部三容器导出与自比、旧包装和 memento 重复成功终点。空事务保留原 abort/身份/活动语义；proof map 在 history 取得 key 后锁外释放。双架五组9410/0/0，[审计与完整构建失败](evidence/br1_pipeline_refactor_20261010/commit-audit.json)、[说明](evidence/br1_pipeline_refactor_20261010/README.md)。生产+214/−166、测试+89/−13；新增内部/外部重入、拒绝、rebase及空身份反例，Reference测试旧consumer一并迁移。独立clone/prune/history/allocatedPages导出保留；restore实际差量、三类manager rebuild、枚举算法及全包性能尚未关闭，不晋升M6。

`2363d824b73f34a1508c80b5e2b595ae61bba65c` 将恢复改为原不可变树的实际current→target差量，跳过共享子树，保留共同原子安装及默认目录重试；跨节点恢复后读值正确但新写拒绝的反例已修。继续追到purge发现前台误用record delta遗留16KiB，已统一原history work释放；删除memento两字段、commit对应输出、restore/release delta入口和单caller locked包装。双架五组9438/0/0，[两个先失败反例、全部失败和审计](evidence/br1_pipeline_refactor_20261010/restore-audit.json)、[算法/计价边界](evidence/br1_pipeline_refactor_20261010/README.md)。生产+98/−136（净−38），测试+132/−25；一个用例恢复输入3→2、目录枚举2→0，实际安装仍2。字段存在consumer并不证明必要；此前内部commit包保留的history输出已按本次证据彻底清理。manager实际差量交付、trim/read失败尾、枚举及完整净价继续开放，安全通过不授M6资格。

`0e55a60932c2d50c099e566f08f514b5f113244c` 完成枚举同一cut：原owner固定事务base及D个key，原root锁外直接有序输出，删除N-version manifest、N-key中间表、完整prepared-set导出及逐项搜索。独立事务推进current后枚举与单页查询矛盾的反例已先失败后修复；rebase夹具原本有extent冲突，已约束到既有bounds，未放松产品规则。双架五组9456/0/0，生产+72/−37、测试+103；[审计](evidence/br1_pipeline_refactor_20261010/enumeration-audit.json)、[全部尝试与计价边界](evidence/br1_pipeline_refactor_20261010/README.md)。manager交付与完整候选净价仍开放，安全及复杂度不作M6通过证据。

`faffef592cff360f4b7baa0ae53fd129f97e3bd1` 完成manager恢复的接受前准备，删除接受后全量清表/重建，保留未变wrapper。反测修正三个前提：intent扩大extent而无root D、独立backend使root/hash集合不同（数量相等也不足）、持backend/publication锁交付与真实tile读者环等。最终核对原hash与目标root完整集合，只准备多项/缺项；原root D直接失效缓存，安装前释放读者需要的门锁。不能宣称纯D，最坏H log M+M+S log S加D仍收费。两hash原PreparedTile还补齐删除GC/key准备，clear/copy同步迁移并用producer准入后default事实裁减准备；无新持久索引或队列。双架六组9588/0/0，[审计](evidence/br1_pipeline_refactor_20261010/restore-delivery-audit.json)、[完整失败/新增成本](evidence/br1_pipeline_refactor_20261010/README.md)。生产+309/−83、测试+186/−8，新增保证不能冒充总代码减少或CPU净收益。trim/read失败仍是rebuild的两个caller；commit/checkpoint及最终同语义性能继续开放，M6不晋升。

`ee8a165fc701eee34de5f1254669a2eea151c1f5` 将read解码失败接回原tryAbort的准备→取消→安装政策，并将空流/坏头移到history创建前直接拒绝；删除重复取消及忽略取消结果便rebuild的尾路。原两个候选锁外释放，不增加持久恢复owner；拒绝保留原history/index/default，原提交可继续。双架六组9628/0/0，[审计及全部尝试](evidence/br1_pipeline_refactor_20261010/import-audit.json)、[反测和成本](evidence/br1_pipeline_refactor_20261010/README.md)。生产+75/−69、测试+77；失败恢复仍需N页基线准备，净价未知。rebuild只剩trim caller；commit/checkpoint和全包性能尚未关闭，M6不晋升。

`e03742b0ef30667d88ed955dad525cd6d6616eb1` 完成trim接受前准备与原D交付，rebuildPageStoreIndex定义/声明/全部caller删除。restore/trim穷举目标成员并准备缺项M后，以H=N−M证明没有多项时省去反向扫描，否则查原hash准备删除；仍可正确处理“数量相等但集合不同”和D=0的adapter变化。保留活动准入屏障、原batch寿命和必要N发现；删重复嵌套检查和有序过滤后的sort。双架六组9694/0/0，[删除/身份审计](evidence/br1_pipeline_refactor_20261010/trim-audit.json)、[算法、全部失败和费用边界](evidence/br1_pipeline_refactor_20261010/README.md)。生产+138/−80、测试+84/−1。commit/checkpoint、全矩阵审计与最终同语义性能继续开放，M6不晋升。

`1249396fa8203570df42ee031eb9c946a45394d9` 通过同源公共API分别链接冻结upstream，证明自动commit prune和空页packed默认no-op不合法：丢失显式extent，redo及改默认色后像素亦不同。已删除整段prune责任并修正native/fallback presence判定；生产+17/−77、测试+84/−5，双架六组9750/0/0。四类写入/clear的20观察点与upstream相同；只取得writable tile、不借像素仍在redo/改默认色有两处差异，保留为T01/T04必修。每次旧prune导出、proof非空capture及实际D读取/比较可删；新增必要显式页费用和净时间未定价，fallback修复不算PageStore性能。[身份与删除审计](evidence/br1_pipeline_refactor_20261010/history-audit.json)、[全部失败、独立探针与局限](evidence/br1_pipeline_refactor_20261010/README.md)。不为无效裁剪新增交付框架；显式purge/clearAll纳入原T04.10闭包。完整矩阵、最终性能及M6继续开放。

`73a9fde6b3dfe7a76724d6797b1470233b7de4a1` 修复公开writable缺页：原准入后判断原entry/transaction，先准备索引，再alias原默认backing；已有batch借用、不提前seal，独立入口复用原交付。无新持久状态/存在账本/伪guard。双架六组9784/0/0，七类公共upstream探针42观察点全部一致，含无history、commit前改default、clone；真实准入拒绝不留wrapper、retry不覆盖已有彩色页及同批先前工作保留通过。生产+139/−32、测试+117/−16，属于保证增量而非净去重收益；CPU generationsReserved不含alias，版本存活计数按drain终点。全部失败、源/库身份和费用见[审计](evidence/br1_pipeline_refactor_20261010/intent-audit.json)、[记录](evidence/br1_pipeline_refactor_20261010/README.md)。batch取消/raw恢复、checkpoint/commit及显式purge/clearAll仍按原矩阵推进；源头修复后重审完整集合扫描。旧父8198的性能比较须先排除已知语义混杂，M6不晋升。

`75dc8fca5f006b546f5774d5b2aa4a3b99318e46` 清除legacy clear中恒空PageStore batch、replace/finish及无效bridge接线，函数局部守卫保留真实失败报告。生产+9/−16、测试+26/−0；受影响manager双架3006/0/0、独立upstream42点一致，预算耗尽拒绝/释放后重试通过。[审计](evidence/br1_pipeline_refactor_20261010/clear-cleanup-audit.json)、[删除依据与全量原始记录](evidence/br1_pipeline_refactor_20261010/README.md)。不删除仍可用的fallback或其他真实Scoped consumer，不把这项通用控制流清理当PageStore性能收益；原矩阵余项及M6资格不变。

同产品75dc上的追加取消反测尚未修复：双架各32业务组合中缺页16项失败、已有页16项通过（含init/cleanup为18/16/0），真实预算拒绝覆盖cache准备和最终root准备。取消后canonical已撤销而wrapper/extent残留，后续writable取得及改默认色再次丢失显式页语义。只有成功路径42点并不足以关闭本责任。[原矩阵§17.5](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#cancellation-terminal-review)已把原session→transaction终结交接、最后lease持锁及匿名共享粒度纳入同一修改闭包；当前保留有真实失败依据的恢复分支，不授优化收益或完整重构通过。[诊断身份/全部失败](evidence/br1_pipeline_refactor_20261010/cancel-diagnosis.json)。

追加所有权竞争复审：raw lease独立transaction/ownedMutation/dirty及seal/cancel/commit序列已合入原WriteBatch控制块，最后引用在Tile barrier外终结；未提交生产候选+125/−140（净−15），53项针对检查通过，双架完整manager各1531/28/0，28是尚未修复的working adapter缓存/presence失败。新的真实Tile读取证明已有页也可返回已取消私有数据，不能沿用首次反测“已有页通过”的范围外推。

更高层反例已实测：24行业务组合中，原隐式共享在8个root预算拒绝行撤销了已返回Succeeded的兄弟operation；独立owner保住兄弟但4个cold成功行遇到派生extent假冲突；改由原合并root的bounds派生后24行通过。首改history revision回退已反测修正，未新增N-page输出。完整竞争原型双架各manager1441/146/0、Reference1018/1/0，除28个local取消失败外，还须迁移seal读/clone提前可见和原共享约定，不能仅改测试值。原型已冻结撤回，当前仍为raw统一候选；[原33项§17.5](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#cancellation-terminal-review)选择显式operation/iterator/history分组及canonical发布点，列出字段/分支删除和下游准入闭包，不为错误cohort另建回滚体系。[结果与完整身份](evidence/br1_pipeline_refactor_20261010/cancel-owner-review.json)、[全部失败/费用边界](evidence/br1_pipeline_refactor_20261010/README.md#cancel-owner-review)。独立重叠操作的root提交可能1→r，控制已见1→2；无净时间或相对upstream收益，M6/M7/M8仍0/3，完整重构未完成。

`67ae4a8caa2d95d3184032dd841c82b3ffcc6353` 已实际实施该竞争结果：独立operation自行提交；普通read/clone在seal仍见旧current、root接受后见新current，显式history仍选overlay。迁移测试保留独立线程、旧exact reader、clone前后两点，新增16个真实root预算拒绝行；原合并root bounds派生extent并保持revision。删除匿名三状态/selector、raw私有mutation/transaction/dirty/第二终结链，以及owned commit/abort的publication写锁和跨层参数；保留有history切换消费者的transactionMutex。生产12文件+200/−254（净−54）、测试3文件+420/−25。双架六组各4961/28/0，28失败全部为local adapter取消；同源公共upstream探针七类42点一致。213项针对检查和raw最后unlock四个真实锁窗通过，但scoped取消交付锁窗尚待实施验证。[源码/库及101成员归档审计](evidence/br1_pipeline_refactor_20261010/owned-publication.json)、[记录与限制](evidence/br1_pipeline_refactor_20261010/README.md#owned-publication-migration)。

[原蓝图§17.6](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#owned-publication-migration)同步细化剩余责任：原D/claim贯穿root拒绝与adapter恢复，B仅含实际新增wrapper并比较复用原PreparedTile能力；不让manager回调逃入晚于facade的orphan；按iterator、packed/planar和clear的真实锁上下文收敛，不在共同helper盲取manager锁。当前abort返回被忽略及物理cancel拒绝后的owned transaction尾必须进一步反测和关闭，不能把scope清理等同整笔终结。四个raw refresh caller仍有实际失败依据，先修32个取消组合再同批删除。新增控制块、独立提交次数和派生surface准备均须计价；本批无时间或相对upstream性能结论，M6/M7/M8仍0/3，完整重构继续。

`e6fc6d687c`接续关闭working adapter的28个取消失败：原D/claim贯穿root结果，B仅复用实际冷插入的原PreparedTile/key/GC能力；物理取消前锁外交付，manager不进入orphan，匹配成功cache保持ready。finish释放准入不等待facade析构。删cold getTile的双回调/OperationDelivery及无consumer单页installLocked；生产+173/−68、测试+37/−8，属于保证增量，净价未知。双架六组各4993/0/0、upstream42点相同，8个真实最后归还锁窗及两hash逆操作通过。[审计](evidence/br1_pipeline_refactor_20261010/local-adapter-audit.json)、[全部尝试和限制](evidence/br1_pipeline_refactor_20261010/README.md#local-adapter-delivery)。四raw恢复仍须迁移真实producer：旧copy在root前替换已有warm wrapper，不由B新插入逆操作覆盖；owned物理取消/abort拒绝后的事务和弱槽责任继续实证。完整原33项和性能尚未完成，M6/M7/M8仍0/3。

`11adac3e3a66a25bca54de0e4a12583269f8f955`关闭真实owned终结缺口：父e6fc的8个硬预算反例在解除压力后页claim为0、事务仍为1；现把owned事实移入原mutation，最后release/原orphan重试共用cancel→abort，不新增队列或manager回调。普通finish/cancel释放无消费者facade引用，真实lease保持原batch及线程槽至最后归还，OperationDelivery保留真实交付引用。删除Backend abort wrapper、忽略返回、batch owned副本及default重复退出；surface-only保持直接路径且验证不增scope。生产+128/−53、测试+124；双架六组10022/0/0、upstream42点一致。[源码/库/删除审计](evidence/br1_pipeline_refactor_20261010/owned-terminal-audit.json)、[原始失败及边界](evidence/br1_pipeline_refactor_20261010/README.md#owned-terminal-delivery)。12个私有cancel压力行无新输入清零；4个root拒绝已现场abort为0，不能算作持续abort拒绝证据。四raw producer/history交付及最终同义性能仍开放，M6/M7/M8不晋升。

`f25d3085d0201fd0585daeb9c645e1dbc405e752`继续删除packed/planar两处失败后区域refresh：原D/B已在claim内完成其取消交付，外部raw owner保持原边界。12个真实后页swap-in拒绝/重试/undo组合通过；最终双架六组各5023/0/0、合计10046/0/0，公共upstream42点一致。生产+4/−10、测试+74；原planar诊断保留。静态删除1次capture及至多A页恢复只作用于失败路径，未实测时间，不宣称M6性能收益。[源码审计](evidence/br1_pipeline_refactor_20261010/raw-write-audit.json)、[全部尝试和范围](evidence/br1_pipeline_refactor_20261010/README.md#raw-write-recovery-deletion)。

同次健全性复审发现**live source仍能修改目标已经捕获的exact view**，普通/rough两个真实失败；只保活TileData的source并非不可变。公共API探针当前/upstream24点相同，源未来写也改变目标clone及redo，因此修复涉及真实语义选择。逐live页冻结的可构造复制上界为K_live×4096×BPP字节，不是严格下界；理想应按独立mutable payload的U冻结、让多个目标共享已冻结source，真正immutable页不复制。保留live alias则尚缺简明的exact capture隔离设计。选择待确认，未暗改upstream比较口径。诊断patch和原始失败独立保存，**不计入上述全组通过，也未修复**。[反例、同义边界与费用](evidence/br1_pipeline_refactor_20261010/README.md#live-copy-contract-conflict)。两copy仍保留原refresh；其余交付按原33项收敛，M6/M7/M8仍0/3。

`e9d2048b4ca202c3c60d97ea53c855991735c997`关闭全量clear的接受后删除准备：原PreparedTileUpdates准备map key/GC动作，原remove batch和OperationDelivery保持claim到安装及候选锁外释放；空canonical/非空wrapper也交付，不建空事务。保留原表、队列和same-thread raw barrier，不扩展并发clear合同。删除PageStore成功后hash clear的晚分配/重试；legacy-only路径仍有consumer。生产+97/−30、测试+73；新增key/候选保活及claim延长未定价，不能称为纯净删。双架六组 **10070/0/0**、upstream42点同义；真实allocator在双架各64个安装场景中 **alloc/free=0**，正控制有效且开始/结束事件完整。只证明该线程安装区间，不证明整次clear零分配或性能改善。[源码与真实拦截审计](evidence/br1_pipeline_refactor_20261010/clear-delivery-audit.json)、[失败记录及完整范围](evidence/br1_pipeline_refactor_20261010/README.md#clear-prepared-delivery)。两copy、purge、history commit/checkpoint和最终同义性能继续，阶段不晋升。

`c1f4efcf07c44577454302e0a5c708325cff9826`把purge迁到原remove batch的预备交付：保留K页内容判定与实际外部写排序，只为D个默认页claim，不加整域claim或大锁；删TileSP选择列表/keys复制、PageStore晚deleteTile和无锁Absent候选的无用查找/保活。链式hash引用仍保护同步unlink。生产+45/−12、测试+115；最终双架六组 **10142/0/0**、公共upstream purge42点同义，真实metadata拒绝后索引/canonical不变并可重试。allocator双架各64场景包含48实际安装和16零命中，安装alloc0；各删除1776页而free为1832/1835，初始零free假设明确否决。额外实际栈定位到read cache和最后binding控制块，仍在原detach锁域；未加队列来追求零free，未将正常释放或通用容器清理计为PageStore性能收益。[源码/库与机制审计](evidence/br1_pipeline_refactor_20261010/purge-delivery-audit.json)、[所有反例及修订口径](evidence/br1_pipeline_refactor_20261010/README.md#purge-prepared-delivery)。该冻结包时history commit/checkpoint、两copy及完整父/新/upstream性能未完成，后续history迁移见下段。

`a24062b966c05236c171e43b90b35fd3b86931a8`完成history commit/checkpoint交付：直接借原overlay已有的有序D，接受前准备兼容能力、接受后/候选清理前安装；原claim贯穿，不新建D或owner。删除historyChangedPages、累计变化晚刷新、bool-presence refresh、重复排序和无人消费的内部checkpoint capture及其拒绝分支。公开exact checkpoint保持原合同，累计H只在提交时由原publication owner直接求脏区；root拒绝后不重放已sealed段。原型r2漏安装导致48个真实失败，r3修复时序，最终进一步删除对coldPages/整段声明集合的依赖；所有失败和身份保留。

本包生产 **+200/−110、净+90**，测试+139/−2；最终六组双架 **10198/0/0**，相同公共history源码与upstream42点一致。双架128个allocator场景中96个实际安装窗口alloc/free0，32空段无安装，内部capture增量0；warm旧缓存与cold缺wrapper分别覆盖。该零free不外推至purge或完整退出。r次新增不重叠d页的checkpoint交付工作由d·r(r+1)/2降为d·r；高重复同页不享该删量，候选/锁域/脏区H扫描仍收费，未测净耗时或性能置信区间。[源码/运行/删除审计](evidence/br1_pipeline_refactor_20261010/history-segment-audit.json)、[模型与全部反例](evidence/br1_pipeline_refactor_20261010/README.md#history-segment-delivery)。两copy的已知exact-view失败、clone投影、导入history必要性及完整父/新/upstream性能仍开放；M6/M7/M8维持0/3、校准2/20、默认关闭。

**clone固定视图与下游目录清理（2026-10-11）。** 产品`667c8d65162017f872352b19a8c4a8e3e5815521`从原capture的retained root/有序delta直接生成最终manifest，采用同一版本像素后移动给manager建索引。删除current另取样、完整prepared-set投影及逐项搜索/删除、updateSnapshotDerivedExtent与canonical源working hash复制；private pending页不再混入目标索引，clone不再误物化未暴露写意图。Epoch初始化有序输入直接建树，真正无序的公共输入继续排序，无新owner/状态/队列。

生产**+119/−107、净+12**，测试+178/−1；最终r6六组双架**10302/0/0**，同源码公共clone与upstream的**42观察点相同**。父选基4失败、r2的32失败及r3的4个旧物化拒绝断言全部保留并归因。归并子责任最坏O(ND+D²)→O(N+D)，两遍访问换取精确M输出容量，有序初始化再删M-entry临时数组/排序；必要capture、节点、metadata/adoption、wrapper与最终释放仍收费，无本包净耗时或置信区间结论。[算法/删除/反例](evidence/br1_pipeline_refactor_20261010/README.md#clone-fixed-view-delivery)、[源码与运行身份审计](evidence/br1_pipeline_refactor_20261010/clone-view-audit.json)。该冻结点原33项T06.2/T08.1及代码索引同步；当时两copy冲突、import history必要性及全包性能仍开放，M6/M7/M8 **0/3**、正式校准**2/20**、默认关闭。

**导入结果寿命收敛（2026-10-11）。** 产品`e1a26e14d91f26db4e4f03b470842105fda00165`核对真实read/readFrame、KRA及clipboard caller后，删除无人接收的private nothing及before/after输出，导入使用原owned batch完成解码、D/B交付与取消，原scope/orphan接最终raw归还；不新建import owner/恢复队列。有效空文件仍执行idle-store准入，保持已有history/外部事务拒绝；公共undo/abort及legacy的真实history消费者保留。旧“取消受阻后提交私有history”随原机制删除，测试改验嵌套拒绝、取消、raw跨返回及异常展开，未只删断言。

父667c8d6516四BPP各四次read/clear/drain的retained root反例2/4/6/8已变为0/0/0/0。N17/257×四BPP在每页后真实换出，16/256次成功、最终像素正确、单顺序session最大pin1；无需为整文件增加checkpoint，但D/B元数据/逆安装存储峰值仍计费。实际MetadataArena满额造成最终root拒绝、无history/索引残留及释放后重试通过。生产+31/−29（净+2）、测试+216/−16；最终r2双架六组**10366/0/0**，新/父公共**42点保持**，upstream成功输入**24点同义**，坏尾/空流的10点差异原样保留，未转授全场景同义。

[原始反例](evidence/br1_pipeline_refactor_20261010/README.md#import-history-retention-counterexample)、[实现/理论实际/删除闭包](evidence/br1_pipeline_refactor_20261010/README.md#import-owned-lifecycle)、[源库审计](evidence/br1_pipeline_refactor_20261010/import-owned-audit.json)、[合同审计](evidence/br1_pipeline_refactor_20261010/import-owned-contract-audit.json)。本项关闭导入私有结果保活，未测相对upstream驻留字节或净时间；两copy冲突、完整管线净价和最终删除核验仍开放，M6/M7/M8保持**0/3**。

**两copy交付与最后raw恢复清理（2026-10-11）。** 产品`2eb9f4236ff3cf28550716717ec43c676336cd9d`修复父e1a26的八个真实root拒绝反例：旧普通/rough路径在接受前改变目标索引。新路径像素循环结束后，持一次manager gate，以原overlay D准备实际缺项/删除能力，再接受root或借用history段，借原保留write set安装。成功候选在gate外、原claim释放前销毁；失败复用原raw失效/B撤销/scope orphan政策，不增加D数组、owner或恢复队列。

普通/rough合为一个模板循环；PageStore root前warm替换、两个失败矩形扫描及refreshPageStoreIndex/refreshPageStorePage定义声明全部删除，原四raw恢复caller完成迁移。生产**+101/−189（净−88）**、测试+152/−3；最终双架六组**10414/0/0**，公共42点和live-copy24点分别与upstream一致。16个新混合页/history用例覆盖真实overlay预算拒绝、先前结果保留、自动取消、重试及undo/redo；硬满时取消可能依赖原future retry，立即或单次drain归零的错误假设与所有失败日志均保留。两架各64个allocator场景，96个实际安装窗口无分配、32空矩形无事件；free578/577、单窗最多32，不授零free或净时间资格。

可删除的是W个warm wrapper重建以及失败时额外capture/A页恢复；原A页取值/比较、D/B准备、alias、锁域和最终释放仍收费。循环去重是通用维护简化，不能算作PageStore相对upstream性能收益。[算法/模型/全部原始失败](evidence/br1_pipeline_refactor_20261010/README.md#copy-prepared-delivery)、[源库/双架/分配审计](evidence/br1_pipeline_refactor_20261010/copy-delivery-audit.json)、[同义及反例审计](evidence/br1_pipeline_refactor_20261010/copy-delivery-contract-audit.json)。两个live-copy exact-view失败未修复，语义选择、最终全矩阵删除审核和完整净价仍开放；M6/M7/M8保持**0/3**、正式校准**2/20**、默认关闭。

**结构门的当前侵入复审（16a4ff59eb删除闭包已交付）。** 实际结构门发现旧检查点和调用图已过期，并仍要求已删除的refresh、anonymous组、iteratorScope及PreparedTransactionState。门禁已改认当前实际责任与源码，不恢复旧状态或放弃校验。最后copy恢复consumer迁走后，KisTile的installPageStoreReadCache/takeIdleReadCache已无调用者，连定义声明删除；Backend的readCacheForPage仍服务两个内部读选择，保留并收回private。tileDataForReadPage、真实raw lease、scope orphan和动态provider验证继续保留。

manager源码现有PageStore标识计数为60：diagnostic timer/phase共32，Backend12、结果/operation枚举6、MutationSession4、WriteBatch2、IteratorReadScope3、ReadPage1；直接include为4（Backend、diagnostics、Epoch、IteratorReadScope）。该词法计数不是新状态数或性能成本。此前原33项明确要求manager原gate覆盖prepare/accept/install，缺项/删除/extent准备和固定root交付的新增引用有实际consumer；唯一权威仍在Store/publication，manager没有新增持久字段/事务目录/恢复队列。局部B/R候选、栈能力、claim寿命、准备锁域、真实缓存释放均继续收费，复制/别名及业务可见性不因门禁更新改变。只将这一文件上限据实审定为60/4，其他文件/字段上限不扩大；raw adapter迁出或对应诊断撤除时必须降低。这个更新承认已实现保证的侵入代价，不能解释为最优、零开销或M6资格。

最终同源双架10414/0/0、公共upstream42点相同；结构门及6项工具自测通过，图覆盖87 TU/2253 API/30565边/26 callback。原收敛起点和retired-protocol证明未刷新。生产+1/−28、检查器+2/−2、审查清单+72/−40、派生图/检查点+49286/−33288、测试0/0分别记账，不能将大JSON变化算作运行时代码。当前死接口动态命中原本为0，只确认维护简化；原T04.6/T05/T07.3保留项分别用surface/proof/provider身份、物理阻碍、晚completion/close的真实断言核验，未授全局最优或M7资格。原T06.3 live-source语义与T08.2全包净价仍未闭合。[删除/保留/理论边界与全部证据](evidence/br1_pipeline_refactor_20261010/README.md#deletion-closure-review)。

**当前完整净价判别（产品16a4ff59eb未改）。** 原T08.2完成存储及普通freehand两矩阵，各3个capability＋8块三方镜像顺序/48计时进程，总102过程全部核验源/库/共享依赖、业务语义及退出。K16/16覆写/H1存储write前台节省1.188ms（17.90%）、全case前台节省1.342ms（11.70% [4.78,20.33]），process CPU节省1.790ms（10.51% [2.54,19.50]）；故这条端点的收益并未被后台全部抵消。当前对upstream仍有write前台5.232ms、完整前台8.798ms及process CPU13.901ms额外成本，不能当作全部可回收预算。短控制、H0进程CPU及整存储进程收益仍未闭合。

真实业务两边都恢复独立clear后，当前Stroke CPU较父增加**0.723ms [0.503,0.976]，回退4.50% [3.07,6.18]**；wall增加0.247ms，Setup及整进程CPU也回退。三方均19次projection update，但不足以排除job/operation/页访问/交付放大。前述区间均为pointwise诊断，未授联合正式门；**完整重构性能验收保持未通过**。下一按原T08.2量化业务回退的实际责任，区分新增必要语义、adapter准备/锁域与调度/清理，不能另猜一个小容器优化或删除正确保证。没有事前总时间点预测，不能声称本次验证预测准确或技能完成升级；live exact-view独立待解，M6/M7/M8仍0/3。全部控制、原始数据及独立bootstrap核验见[整包净价报告](evidence/br1_pipeline_refactor_20261010/README.md#whole-package-net-price)。

**后续工作量判别（仍16a4，产品/测试0改动）。** 两轮各4个ARM64观察过程通过语义、加载身份、事件完整性及退出；937 stroke job、46 operation、208 cold和59 seal均未增长。projection内部32个producer/132次冷准备，由父11～14个匿名事务变为32个独立事务，Stroke commit入口12～15→33。当前33次均含proof且实际成功，新增ensureWritablePage命中0。原匿名合并造成成功兄弟被后续root拒绝撤销已有反例，故独立责任不能删除；原蓝图必须补计其发布频率增量。观察CPU不能分摊0.723ms，也未证明其全为必要成本。下一按原T02.4收敛owned终态的原entry→canonical路径，审查无consumer的overlay移交/重复extent/附属恢复，保留history、真实动态验证/失败及最终释放，不新增第二owner/写集或借共有融合过门。原33行矩阵不扩表，完整净价/控制/live exact-view仍未闭。详见[归因、条件模型和代码闭包](evidence/br1_pipeline_refactor_20261010/README.md#business-work-attribution)。

<a id="br1-closure-schedule"></a>
## 17. BR1 完整收敛收口排期（2026-09-30，后续原位更新）

> 本节保留各批次的原始判断与索引。涉及当前产品、领取顺序与性能价格时，先核对[§1](#native-cpu-baseline)和[证据适用范围](README.md#evidence-scope)。

本节统一当前排期，替代其他活动指南里旧检查点的“现在、随后、下一批”。§16.28 的完成矩阵和各批冻结证据不因排期更新改变。CP0–CP10 是工作包编号，映射既有 S/BC/JP/U/C/V 责任，**不是新阶段、版本号或新的状态权威**。2026-09-30初始排期只做规划；2026-10-01结合§16.36重估，2026-10-04按§16.88–§16.108结算VM释放、语义默认值ownership、三次manager终点、KConfig测试前置、TileData生命周期、真实fault终点、当前Darwin owned总硬界、非Darwin精确capacity/free与默认abort宿主合同处置。2026-10-05按§16.109–§16.113结算CP2代码/安全范围，下一主包为CP3。完整CP1/CP2已关闭；CP0及M6/M7/M8阶段资格未完成。

<a id="closure-schedule-principles"></a>
### 17.1 排期优化与范围控制

**2026-10-12优先级覆盖：** 先执行[读写核心重写§19.19](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#read-write-core-rewrite)的native操作选择、紧凑准备/接受和范围读能力；CP6中与此直接相关的读/写责任前移，不等待CP4/M7。必要的metadata/预算/adapter/history/retirement接口与布局一并重构；下列“已交付不重开”不限制这个经用户授权的替代范围。无关通用优化、孤立容器微调、非依赖模式扩展和正式计价重复采样后移。CP0继续保障同源基线/原控制，当前正确性和硬预算不后移，M7生产资格仍须M6正式通过。§17.2原人日窗口是重写决策前的旧估算，本次不将其冒称新计划；完成首个完整候选的机制与净价后重估，未编造工期。

1. **停止重领已交付项目。** copy bounds、packed/cursor add 联合窗口、首条 direct owner/显示/finish/cancel、BC10 联合 fixture、普通 direct cursor 的 backing preflight，以及 §16.22–§16.27 已收费/删除的控制存储，只在新改动破坏其断言时回修。不能继续把“准备真实 harness”当下一主线。
2. **完整控制存储工作包已经关闭。** CP1 已枚举 callback/capture、worker task、read/retirement context、retry/pass/terminal 和尾内存的真实分配、保活和收费 owner，并由§16.108关闭非Darwin capacity/free与默认abort宿主合同出口。除非出现满足§16.107停止规则的新生产反例，不再重开CP1。
3. **区分 M6 前置与 M8 全出口。** M6 参与对象的实际收费、claim 安全、拒绝保债和退出不能延期；真实多文档无饥饿、完整 brush continuation、全部模式/undo/context 不反向成为 M6 的无限前置。M6 范围内若实际依赖后续能力，必须提前补该具体依赖，不能用这条拆分豁免安全/预算要求。
4. **补上长期缺席的 M7。** M6 验收后直接进入 CP4；cursor preflight、普通可取消 painter callback 或新增 prepared 包装不能替代 commit-only 生产 consumer。M7 的 fence 上限与不可失败区间沿用 §4。
5. **性能对照从 CP0 准备。** 固定 upstream、实际修改前工作树和同 Qt/工具链/架构对照；预注册实际显示和完整 drain 的 workload，尽早取得缺测清单及代表性基线。正式性能裁决在 CP10，不等到全部实现结束才发现基线不可运行或测量不包含真实工作。
6. **合并/删除跟随 caller 迁移。** 每包同时维护 API 替代账本；保留不同语义，不为减行数删除失败保证。新增上层 API 仍受 MI1–MI8 限制；原 scheduler 唯一拥有 job/cancel/finish，PageStore 的页、预算、waiter 不越过适配边界。
7. **测试验证工作包结果。** 正常开发不在每个小改动后重复全矩阵；一个工作包完成后运行能证伪其交付的目标测试。跨模块阶段冻结和最终候选运行所需完整矩阵；发现新失败或后续改动才补跑受影响范围。

当前 M6 的实际生产正例为 resident CPU exact alternate。CP0 必须按 §3/§6 和 39 核定 required bucket：不自动增加 SSD/archive before producer、GPU/UMA/discrete 或 BR2/BR3 接线；未支持恢复源必须有拒绝/Fresh 控制。**已有合同明确要求的能力不能后移或删掉，SSD 耗尽与资源/退出场景也不能因 alternate 未接入而省略。** 若 required 清点确认有超出现实现的硬要求，归入对应 CP 并同步重估。

<a id="closure-work-packages"></a>
### 17.2 完整工作包、交付物与排期

估算以一个主实施者串行推进为基准，1 人日按8小时工程工作计，包含实现、审查及目标验证；不给未安排的多人并行折扣。2026-10-05按§16.108/§16.113移除已完成CP1/CP2；表中是**当前剩余工作**，CP2行只保留完成范围。D0是本次重估后的工程起点，D不是日历日期、agent运行时间或轮次数。已交付子范围不再次计入。实际工程人日尚无可靠记录，不能从提交数量推算；下列区间仍是低置信估算，CP3出口再校准。

CP1原2–4人日估算没有充分覆盖保护移除后的效果保债、provider不可重放副作用及最后handle退出。§16.37–§16.106已交付CPU参与者实际根/control/bootstrap、真实容量/释放、owned总硬界和已发现生产fault终点；§16.107建立新fault反例停止规则，§16.108关闭非Darwin实现/平台运行并完成默认abort宿主合同处置。上述范围不再计入剩余工时。CP0按§16.140已有当前同依赖普通freehand基线、31组required责任清单和真实archive容量补证；完整场景实例化/适用构建/正式样本仍欠，不因清单存在而关闭CP0。

§16.61撤回的observer收费候选、§16.64–16.66压力拒绝及§16.65 detachment尺寸是各冻结源码的事实；当前observer/control/登记、metadata link、source/read cache及bootstrap/runtime已由§16.72集中实现。原24MiB/8MiB业务压力合同未放宽；§16.73已补实际准入后取消，§16.98已把当前Darwin完整owned峰值/总硬界绑定到既有实际压力及后继专项证据。§16.107未找到新的生产拒绝反例，后续只按明确父红重开；§16.108未重跑已结算长压测。

§16.66–16.71的目录/authority/Private及Store/Ledger冷根、真实receipt和无操作复用不重领；§16.72的Store factory子根实际费5,104→5,448B，仅指该子根，不能充当backend/provider/history/process及全部runtime的合计。Darwin stop释放线程/clock存储后仍有固定executor/process anchor至static析构，不写零尾容量。当前源码owned清单和总硬界由§16.98统一关联；§16.108完成平台出口后完整CP1关闭。

§16.136/§16.137提前拒绝与冷准备/借用已冻结，K16增量时间收益未确认。§16.139补CPU覆盖和执行变异：低扰动30/30有两组样本的过程慢组3.11–5.33倍；同期global/local均0/4满足±2%，就地ABBA候选否决。产品未改，下一稳定实际执行条件后独立完整20桶校准及匹配hit/miss；不继续同义runner调参或无预算微路径猜改，metadata驻留分母/CP0 required独立推进。原当前安全11180/0/0、资源/结构、hit/miss数值及Fresh/H4保持，正式校准仍2/20。各有限包均不续采；自然正例/业务分布仍未建立，旧20%/30%失败不改写。CP3原1–2人日及整体区间仍属低置信旧估算，没有可靠实际人日，不按进程数扣工时，M6未通过。

| 包 / 对应责任 | 前置 | 主交付及必须关闭的断言 | 预计人日 | 累计无缓冲窗口 |
|---|---|---|---:|---:|
| **CP0 范围、基线与证据准备** / V01 | 当前矩阵 | 固定 required 模式/恢复域、M6/M7/M8 分支清单、源码/库身份、同依赖 upstream 对照与正式样本规则；从真实工作量准备代表性性能基线 | 0.5–1 | D0–D1 |
| **CP2 M6 代码与安全边界（已完成）** / S05/S06/S07/S09/S10 | CP1已完成 | §16.109–§16.113结算legacy expected/原exact重解析、raw/batch保护、epoch/ABA/晚completion、实际准备拒绝及统一终结；未迁移路径继续保守排斥，Fresh保留。正式M6另由CP3验收 | — | — |
| **CP3 M6 冻结验收** / V01 | CP2已完成 | §16.139执行变异已定位、就地ABBA否决；稳定实际执行条件后独立完整正式family，旧校准18桶证据不足。metadata≥25%分母、CP0 required及适用身份仍须齐全；不继续无预算微优化，当前安全/资源/结构及Fresh/H4不替代其余资格 | 1–2 | D1–D3 |
| **CP4 M7 生产协议和验收** / S06/S05/S10/V01 | M6 正式通过 | 唯一 selector 的 commit-only 分支、共同 epoch admission、全部页/输入/claims/安装存储；实际内部同步 consumer；首字节后失败0、第二页拒绝未写第一页、≤8页/256KiB/P99≤100μs；超限安全 fallback | 4–6 | D2–D9 |
| **CP5 压力进度、公平与原 job 接续** / S01/S08–S10/BC9 | CP1已完成；主线在 CP4 后 | 持续热点、慢 reader/retirement、SSD耗尽、多文档；活跃 demand 的 work-conserving 公平；永久拒绝不排队；可等待工作由原 owner 持有、取消/finish 有序、释放后无新输入继续、兄弟 job 不重放 | 4–7 | D6–D16 |
| **CP6 读意图与剩余发布/operation 族** / S02–S05/JP1–JP8 | CP4/CP5 | current/G0/operation-start/exact 分责；clear/remove/default/copy/alias/planar/restore/purge 及 working extent 的 prepare/revalidate/install/cleanup；保留真实 rollback/capture 边界，各族不新增第二 write set/选择权威 | 3–5 | D10–D21 |
| **CP7 M8 全业务入口与生命周期** / S01–S04/BC1–BC10 | CP5/CP6 | 按模式扩展通用 direct/source-dependent、selection/path、indirect/mask、多 painter，再到 wrapped/LoD/异步 target；H/V/random/repeat iterator、packed/planar/clone/history 共用原 scope；每族联合写/读/显示/失败/undo/drain，并删除已迁走的兼容分支 | 5–8 | D13–D29 |
| **CP8 Undo 然后 context 收敛** / U01/U02→C01/C02 | stroke 核心出口 CP7 | 普通 undo 用 delta 安装/失效，固定K无全量export/sort/rebuild；extent/purge 成本分责；有界 preset 准备复用与完整失效 key，layer/frame/LoD/offset/wrap/format/外部内容变化不污染旧 stroke | 4–6 | D18–D35 |
| **CP9 API/配置收口与 M8 验收** / 全责任/V01/MI1–MI8 | CP8 | 汇总此前同步删除，清除无 caller 的包装/字段/注册/回调；必要 ABI/不同语义逐项保留理由；适用 ON/OFF/hash 配置完整验证；M8 全模式/资源/退出通过后，再按性能门评估各入口默认策略 | 2–3 | D22–D38 |
| **CP10 BR1 正式性能与最终裁决** / V01 | CP9，CP0对照就绪 | 当前同源 required M/K/E、冷暖/N/K/H、first-dab/input-to-visible P95/P99/pen-up/drain、峰值容量及主干关闭状态成本；保留所有失败，达标后冻结最终矩阵/删除证明/默认策略与 BR1 裁决 | 3–5 | D24–D43 |

表中累计区间表示低估/高估两条串行路径的开始至结束范围，并非某包可在任意 D 值跳过前置启动。剩余基础工作量合计约 **27–43 人日**；另保留约20%的共享风险缓冲，完整收口剩余预算约 **33–52 人日**，按每周5个工程日约 **7–11周**。这不是 agent 实时运行时长或固定交付日期。缺少可运行 upstream、M7 不可失败区间/continuation 方案受阻、新的跨模式正确性反例，会消耗缓冲；不能为保日期降低安全、预算或性能门。重估只移除已完成CP1/CP2的计划剩余，其他包沿用原估算，不据此反推实际工时，也不将控制存储的速度倍率机械乘到M7或全模式迁移。

可感知检查点为：**CP1/CP2已完成；D1–D3左右争取M6正式出口；D2–D9左右争取M7生产与资格；D13–D29左右争取完整stroke模式/生命周期出口；D24–D43左右争取无缓冲的完整BR1候选。** CP0 的基线准备持续复用已有构建/fixture，不每包重新搭建。若只交付“首条 direct 可用”，它已有开发入口事实，不能将该较小范围计作本计划完成。

<a id="closure-dependencies"></a>
### 17.3 关键路径与压力接续的有限设计门

CP1/CP2已作为完成前置退出剩余路径。主实施线为 **CP0 → CP3（M6）→ CP4（M7）→ CP5 → CP6 → CP7 → CP8 → CP9（M8）→ CP10（BR1-PERF）**。对照环境、样本格式、静态 caller/配置清单可提前准备；这些准备不授予阶段资格，也不改变一个主实施者的工时估算。各模式所需准备/发布/取消与资源消费者在同一模式包内共同审查，不能先做一个纯 API 扩展包再等待 caller。

CP5 的 continuation 有真实所有权障碍，不能填成普通枚举扩展。现有 `popOneJob → updater → setDone` 会销毁 job/data，一次 update 有并发兄弟和后继 cut。先用**不超过1人日的方案检查**比较两种实际端点：

- 优先核对 dispatch 前完成业务准入、原队列仍保留未执行 job 的可行性；目标是避免执行后重建 job 和 replay，但必须证明所需输入/footprint/取消能力当时已存在。
- 若实际只能在运行端拒绝，则只转交 callback 尚未进入的原工作单元；原 scheduler 接回队列位置、取消及析构责任，不克隆 runnable/closure，不重放已执行兄弟 job。

二者只选择一条可实现路线。实现前必须列原 owner、输入寿命、唯一 waiter/取消/唤醒点、finish/checkpoint 排序及失败销毁；typed result、实际 consumer 和旧模糊失败分支的合并同批交付。PageStore 内部保留 page/reservation/budget revision，scheduler 只消费业务继续/等待/失败语义；`tool/strokes` 不保存预算、不轮询、不拥有第二完成队列。没有闭环方案时保持现有 Failed，记录具体阻塞和影响工时，转做不依赖该能力的 CP6 静态/族内准备；**CP5/M8 仍未完成，不用 safe cancellation 替代自动进度资格。**

公平以原活跃且可取消的等待请求为 demand，不按注册 backend 数静态分额；同图像的投影/辅助 store 不能压缩空闲时主目标可用容量。回收 pass 的 nodes/bytes/time、热点失效重启、冷页进展和最后 pin 后自主 drain 与 admission 同一包取得结果，不能只测一次 reserve/释放后由测试重新发起请求。

<a id="closure-testing-policy"></a>
### 17.4 验证安排与停止条件

最新按[§16.175](#pagestore-whole-pipeline-blueprint)：原[T01–T08完整蓝图](evidence/br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#whole-pipeline-blueprint)扩到最终差量、共同overlay接受、内部commit输入、adapter/history和最终退出。先判别F/P/A、内部导出往返及业务回退，再冻结相应准入实验；copy/restore/trim和全量列举另记实际命中与净价，不默认进入K16 write预算。完整consumer按同一责任迁移和删除，未迁移者保留具体依据，不以准备侧完成宣称全管线完成。单独operation省overlay仅为条件设计；Fresh可撤销与原地首字节不可失败分开。§16.173候选20fd未晋升、活动产品8198，旧有限包不续采。后台归属、M7/8页fence、严格非劣及正式资格保持开放；[§16.171](#pagestore-equivalent-performance-scope)分账原则不变，通用Q01–Q07不授PageStore基础性能证据。

最新[§16.169生产交付](#projection-boundary-production)已完成原B01–B11有限范围的实现及语义/资源反例：无原型pending TLS、无新owner/队列，冷准备132→96、batch/seal32→19。双架构1760测试通过，独立Stroke CPU节省1.204ms [0.922,1.781]；r0 Undo控制失败和r1空源顺序修正均保留，两个固定批次停止。严格阶段非劣仍未授，后继须单独处理Undo/Redo/Teardown控制与正式M6/CP0资格，不把局部净收益或区间跨0当全门通过。

当前实际产品为67ae4a8caa；[§16.163](#history-admission-selection-trial)的空历史候选仍保持否决，未被本次重新引入。§16.167工作拆分/调度审查继续适用：技能已得到从中层边界到生产净收益的正向实例，精确预测、全局排名与整链算法充分性仍开放。原§16.168派生原型只作冻结父证据，不续采；§16.166 R08判别及旧CPU观测亦不续采。不能把约4.04ms前台或0.64ms后台外框全部视作可删除工作。

此前[§16.159全生命周期结果](#cpu-lifecycle-implementation)已有限收口，03j的28项均有具体处置。§16.161 D1/D2已降级H1临时表达与H2孤立backing/proof小项；[§16.162读意图因果原型](#read-intent-selection-trial)已证明18次未消费before捕获和80次页获取可删，但4块净价未通过探索准入，不进行跨层产品改造。cold的Page/descriptor/binding交接、operation原scope等仍须新的事实/消费者放大及合法替代依据，不能领取整个外框价。108过程覆盖账、LP配对、D1/D2及读意图19过程均停止，不继续重复加样。正向流程确认、完整CP0、metadata同义分母与正式资格仍开放。

§16.155结算[03f改动索引](br1_modification_guide/03f_cpu_management_cleanup_index.md)和[03g唯一追踪矩阵](br1_modification_guide/03g_cpu_management_cleanup_tracker.md)的22项/10路径；59个hunk均归属MP，R01–R09逐一证明或保留。不得把这些已退出工作重领为下一痛点；结构/数量、安全、净收益、原控制及M6资格分开。

当前有限管线清理包已结束：§16.155数量兑现而Stroke CPU仅再降3.08%，wall区间跨零；新鲜a918对照支持旧Undo回退在诊断层恢复，但Teardown CPU非劣及正式计量仍未闭合，默认不晋升。下一优先围绕canonical发布/allocator联合责任和read/merge余项建立必要下界与可删预算，不启动无证据容器重写，也不重复本包克隆/claim/空锁矩阵。完整生命周期原824请求及五项替代不重领；旧0.34/0.568ms混合桶、0.407ms metadata外层及内插桩约0.8ms均不能拼成收益预报。reader/domain仍复验，132→96仍未合法，旧画笔/未覆盖3.86/1.41ms等独立分母保持限制。已回退pin重排和旧17准备/复制不重领，默认资格、upstream完整目标、metadata分母及CP0 required仍分别开放。

§16.132–§16.138均保留冻结裁决，K16原库增量不追认收益。§16.139修正Rosetta线程CPU覆盖误用风险，低扰动查询定位执行条件关联；就地ABBA同期两策略均0/4满足±2%，候选否决，按固定规则停止。下一稳定实际执行条件后独立完整正式family；不继续同义runner调参、无预算产品微优化或昂贵盲扩样，不以更宽松诊断区间、删尾/扣偏差、CPU归一化、借512ms给旧64ms数值授原库资格。旧正式校准2/20、联合hit0/4和miss2/16、Fresh/H4八桶及旧30%失败保持；metadata驻留/CP0 required独立补证。

§16.126的[成本预算与停止规则](evidence/br1_cp3_cost_model_20261006/README.md#后续排查和退出规则)保留冻结证据；当前实施按§6.1–§6.3。原provider审查仍是候选，不能仅从malloc次数、全线程sample热点或未拆开的inclusive阶段启动容器重写。先验证逐页准备/读/收费/保护与共同发布的次数、独占成本和等待归属；候选须说明合法可删工作、预期绝对收益及产品敏感度，因果验证不符预测则修正模型并停止猜测。原40对结果、原协议阈值及停止条件不修改；新协议另行冻结。

§16.127定位的短命allocator引用由§16.130收束，重复全类扫描由§16.131收束；原目标链仍54次，准入可识别上下文只剩约1.6～2.1μs。下一有限设计仍须绑定prepare/settle等数量变化与未插桩CPU/wall结果，区分共同成本和handoff特有成本；真实逃逸尾保活、实际capacity、parent child费用、限额/公平/失败/晚free保持。provider节点或剩余allocator热点尚无足以支撑下一重写的因果预算；§16.133已有CPU归因不重做，仍未取得的必要下界、真实业务等待/后台及硬件证据分别保留缺项。

§16.128的[完整算法/实现预算](evidence/br1_cp3_algorithm_budget_20261006/README.md)继续指导实现：先按字节、K事实、相关V/R、root路径并集和真实lifetime推导应有工作，再解释分支与容量残差。候选事前列明`ΔA/ΔB/ΔF/ΔR/Δbytes`、全部保留consumer、必要费用及可删除上界；不按一个map/allocator或每页平均成本逐点试改。root dense按实际工作量比较，不重领已完成sparse batch；K²去重按实际上界定优先级。模型缺项先补共同状态变量/联合端点；不再把证明所有合法算法均无法达到30%作为采用§6.1新门的前置。

§16.129的[原容量/引用/寿命追踪](evidence/br1_cp3_capacity_lifetime_20261006/README.md)是§16.130的冻结父证据；目标链4569→54，native共同seal/commit3118→279。§16.131的446个controller成功对象有193/144个观测到操作内释放，208/257个在后阶段释放，两块均45个窗口外尾；这个时序差异保持可见，不能统一operation释放。继续在原owner内推导合法分组，不新增第二预算owner，不把计数减少当速度收益；原28数量进程与固定未插桩验证已完成，不扩样或重跑无改动矩阵，原native协议失败保持。

| 时点 | 运行内容 | 禁止替代 |
|---|---|---|
| CP0 | 核验现有 fixture 真正执行目标模式；冻结 required 场景/配对规则和同依赖对照可运行性，取得代表性基线 | 不在尚未合格模式上预报收益，不把 broker/库编译成功当产品资格 |
| CP2 完成时 | 目标 handoff/legacy/读写终结、参与资源及原 Fresh 控制；触及 ownership 时检查结构和 caller | 不重跑已由CP1结算的长压测；不在每种 state/包装的小改动后跑历史全矩阵 |
| CP3、CP4 阶段冻结 | M6 或 M7 所需双架构完整矩阵、真实 allocator/竞争/失败、参与生命周期、构建/库身份与 foundation 兼容；门限沿用 §3/§4/§6/39 | 累加不同源码旧日志不能取得阶段通过；reference 原语不能替代生产 selector/consumer |
| CP5–CP8 每包完成时 | 与目标相关的真实 scheduler/brush/manager/undo/context 结果；成功、拒绝、取消、无输入进度、峰值/尾延迟；每个模式一条联合生命周期证据 | 不用独立 fixture 的测试总数代替同一个模式的整链；不对镜像实现或纯文档改动新增产品测试 |
| CP9 最终业务候选 | 当前同源完整 CPU/业务/配置/资源/退出矩阵、结构与工具自测、caller/runtime census、临时接口债务和实际 ON/OFF 差异 | 两 backend 关闭测试不等于完整 OFF 配置；只测正常预算不等于 BC9 |
| CP10 正式候选 | required M/K/E 独立配对、正式样本与原始失败；全部适用性能门；最终源码/依赖/二进制一致 | 不用 allocator=0、历史 M5 吞吐或 microbenchmark 推定真实 stroke/主干收益 |

同一构建目录只由一个构建进程写入。最终性能调优改变源码后，只重跑受影响结果并在最终候选补齐必需矩阵；代码未变、检查已通过且无新风险时不继续扩大/重复测试。TSAN 仍按实际运行报告，不把当前 Inconclusive 改成 Pass。

每包开始登记有限端点、原责任、目标断言、同批合并/删除和退出条件；完成即冻结。§16.136已知拒绝清单和当前§16.137的[冷准备/借用B1–B3/V1–V2清单](evidence/br1_m6_provider_borrow_20261006/README.md)均已完成，不重领或用追加样本延长本包；最终claim、foreign保活与安装复核保持。原20%/30%失败不改写，当前miss仅数值过门、校准未闭合，不宣布M6通过。没有充分预算不启动容器/provider重写、不扩大恢复域、不重领已完成借用/扫描/槽复用/packet/工作值/索引或无改动长压测。CP3原1–2人日及整体27–43人日仍是低置信旧规划，没有可靠实际工时，不能作当前M6承诺或因改门扣工时。新发现仅在真实consumer违反既有合同并阻塞本包时进入关键路径；可选优化不延长已关闭工作包，真实失败必须回修并保留原证据。

<a id="closure-exit-register"></a>
### 17.5 阶段裁决、文档落点与更新责任

| 冻结点 | 必须留下的结果 | 更新位置 |
|---|---|---|
| CP1 资源闭环（已完成） | 所有实际分配 owner/bytes/count/失败/物理释放清单；Linux/Windows精确capacity/free与默认abort宿主合同均已结算 | [§16.108](#cp1-platform-exits-delivery)、§16.28资源行、[CP代码索引](br1_modification_guide/CODE_INDEX.md#cp1-platform-exits-code-index) |
| CP2代码/安全（已完成） | legacy/raw/batch/clone、epoch/ABA/晚completion及共同准备/终结逐项核验 | [§16.113](#cp2-epoch-preparation-delivery)、[完整审查](evidence/br1_cp2_epoch_completion_20261004/cp2-audit.json) |
| CP3 M6 | 全合同核验、正反例/时序/失败/预算/退出及当前源码身份；资格确实通过才更新 §1 | 本文§1/§16.28、[包清点](br1_modification_guide/CONVERGENCE_CHECKLIST.md#closure-package-checklist)、V01证据 |
| CP4 M7 | 实际 consumer/epoch gate/预构造安装；fence分布和首字节后失败0；保留fallback | 本文§1/§16.28、S06/V01、API替代账本 |
| CP7 stroke 核心 | 每入口写/读/显示/undo/cancel/drain 与复用次数、压力/峰值；哪些模式仍未完成逐项保留 | §16.28、BC1–BC10及S01–S05清单；此时不提前宣布完整M8 |
| CP9 M8 | 全业务、undo/context、资源/进度/退出、迁移/删除及适用配置均通过；默认策略仍等待正式性能门 | 本文§1/§16.28、API/CODE_INDEX、MI1–MI8及V01 |
| CP10 BR1 | 正式性能与最终同源资格通过，明确最终默认入口和未开放域；才能按31开放后继production | 本文§1/§7、README导航与39证据；不靠更新排期文字宣告完成 |

工时/累计窗口只维护本节；源码映射只维护 CODE_INDEX，领取/结算只维护 NEXT_EDITS/CONVERGENCE_CHECKLIST，新增/替代/删除只维护 API_CONVERGENCE_MAP。专题指南描述具体契约，不再各自维护“下个版本”。每次完成工作包只更新当前矩阵及原位排期，冻结证据单独保留源码范围；不复制一份新的“当前总计划”。

2026-09-30 本次排期同步核验覆盖12份活动文档、1779个本地链接和617个锚点，CP0–CP10在领取/代码/API/验收映射中齐全，人日求和一致；最近实现批的17份源码/运行身份哈希未变。仅完成规划和文档校验，没有修改生产代码、重跑产品测试或新增阶段通过。
