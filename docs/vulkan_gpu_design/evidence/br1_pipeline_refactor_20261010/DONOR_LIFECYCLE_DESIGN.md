# 补齐旧目标交接：实际窗口、最小保留协议与净账输入

2026-10-12。产品仍 `11c6895ddf`，生产/产品测试改动0。按[事前协议](DONOR_PROTOCOL.md)完成8个隔离能力/诊断过程、512个公共case记录；无新CPU收益资格。[机器账](donor-summary.json)、[参考模型](donor-model.json)及原始包见文末。原33行仍是唯一实施状态，当前设计落在[§19.13](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#donor-lifecycle-capability)。

**本轮关闭了两个关键不确定项：即时旧目标的实际收费类/原handoff可接性，以及不主动保留时下一次写入的可用量。** 它们把方案从“可能复用某个历史页”收敛为“在原transaction中保留一个已失去逻辑可见性的工作目标，下一次使用时才申请物理写权限”。尚未完成metadata原子移交/retag的产品实现及完整净定价，不宣称全预算闭合。

## 1. 新实测，以及对上轮判断的纠正

四manager寿命，K16/W16/H1。普通两次mode2（能力、正式）数量一致；下表不把重复内部操作当独立样本。

| 真实端点/条件 | 旧proof撤销后 | 下一次同页冷准备 |
|---|---:|---:|
| 普通H1 | 960个Historical逻辑版本；backing **960个ActivePending** | 查询896个已记录旧目标；**896个metadata版本均已退出，owner登记亦均退出** |
| 普通H1原组件prepare→claim→cancel | **960/960成功**，旧handle保留；owner准备全部成功 | 可用目标0；另192次冷准备尚无旧目标来源 |
| 保留首个Prepared结果的完整clone | metadata仍960个无逻辑保护；owner准备960；物理claim拒绝64，成功896 | 896个metadata目标全退出 |
| 保留首个Prepared结果的一页原生读锁 | metadata仍960个无逻辑保护；binding准备拒绝4、成功956 | 896个metadata目标全退出，但4个owner记录仍在RetirementDebt等待物理读者，其余892已退出 |

前两列中的“下一次”不是同一物理身份完成全部未来的概率，是该观察运行中逐page/transaction记录后再查询的事实。mode1只查状态、mode2另执行原组件prepare/cancel，两种模式的普通H1结果都表明没有自然留下可复用目标。观察器会改变调度，不将0/896移授成所有plain运行的永远零命中；但它足以否定“现有账本已保证下一写有旧目标可取”。

**上轮源码事实正确，推导过宽。** `prepareBackingHandoff`确实只接Current/ActivePending；`discardHistory`确实先转RetirementDebt再退出。但“metadata Historical”不等于“backing已经RetirementDebt”。窗口在提交退债之前存在，实测原owner接口已能prepare；不需要先放宽收费类或从退休队列抢回record。已提交退休的记录仍不可反向取走。

全64case每过程有12776次冷查询、1020次旧Prepared记录、952次有来源的下一查询。一个普通mode2能力过程在较小case里曾看到1个尚存版本，但physical准备拒绝；该例保留，不能把H1结果扩大成全部case完全一致。H0原路径没有该Prepared替换命中。六个正式过程分别覆盖普通/held clone/held tile的mode1/2，正反case顺序交替；两模式全部signature/accepted相同，原八格还逐写验证像素及undo/redo。四个坏尾格仍不授跨upstream等价资格，新held控制只证明当前实现自身合同。

## 2. 不能把“保留”和“允许覆写”合成一个强保证

新反例说明：metadata中无capture/pin，不代表physical没有使用者。完整clone使64次物理独占拒绝；原生读锁使4次binding准备拒绝，而metadata检查全部显示idle。删除物理检查会破坏真实旧读者。

但反过来，**仅保留一个对象，并不要求它现在就独占可写**。现有正常回收也可先删除不再逻辑可见的版本，再由退休队列等待native pin；逻辑与物理寿命本来就是分离的。因此目标设计应为：

```text
新结果已具备接受能力；旧Prepared将失去overlay可见性
  → 原metadata内验证逻辑保护与真实来源
  → 接受时将旧逻辑记录退出；原owner继续保留有收费的physical责任
  → 同一transaction/page原槽记录最多一个备用工作目标
  → 下一次写：匹配布局与代次，才做owner准入 + physical claim
       成功：准备新逻辑generation → retag/原节点rekey → 私有写 → 原接受点
       拒绝：原退休记录承接备用目标，Fresh/原拒绝继续
  → commit / abort / removal / pressure / close：原责任统一交给原退休队列
```

不在保留阶段预先运行一遍完整handoff，再在取用阶段重跑。对本fixture，前者会额外增加960次物理准备/claim/cancel；后者仍需要896次真实取用许可。该960次是可避免的**拟议新增工作**，不是已经从产品删掉的工作，也没有被换算为CPU收益。保留不授字节修改许可；native holder、alias和驻留条件必须在实际checkout重新验证。

## 3. 五项设计问题现在如何落定

以下是同一候选的设计约束，不是宣告生产验证通过，也不是另一张实施状态表。

| 问题 | 选定的最小表达 | 尚需实现验证 |
|---|---|---|
| 谁持有旧目标 | 原publication transaction/page节点附带最多一个备用handle；唯一physical所有者仍为原owner backing及其预付retirement record。保留字段不成为第二版本查询表；所有读、导出、commit只读当前proof | 原ProofMap值需要显式区分当前proof与备用容量；遍历/捕获/导出不得把备用目标重新发布 |
| metadata如何退出 | 在原overlay接受准备/安装中，为精确superseded Prepared准备“退出或继续Historical”的条件动作；复用既有page claim/revision与captured/overflow/pin/operation检查。当前可见cut接受后才交出旧责任 | 不能调用一次完整逐页`discardHistory`再补回对象；逻辑删除、备用槽交接、旧proof撤销与descriptor退出必须一致；拒绝继续原collector |
| physical身份如何重用 | 下一次取用走原`KisCpuBackingHandoff`及owner节点rekey；新逻辑generation/descriptor与必要安装须先备好，claim成功才retag。不覆写仍可见的上一成功值，不是M7当前值原地写 | 此次只测prepare/claim/cancel，尚未测metadata安装→retag→owner提交的实际原子窗口、stale handle、provider revoke/swap和故障 |
| 收什么费、占多少 | 本候选明确把它作为**当前transaction的一份ActivePending工作容量**，继续保留原physical登记、管理存储和已预付退休headroom；每个原page槽最多1份。不能提前释放预算、伪报provider retired，也不另建OptionalCache池 | 保留时间延长是真实新增成本；低额度先放弃保留/排空备用槽。现有store限额初始化后冻结，父共享额度及实际压力/管理容量仍需验证，不冒称动态改限已测 |
| 拒绝/取消/终结 | 未接受前准备失败保持原overlay；取用失败不改上一成功值；接受后清理不能改报操作未执行。已有备用、quota不足、布局不合、原生保护拒绝均走同一原退出政策。已交队列只由队列继续 | commit/abort提取delta、单页erase/removal、scope取消和close必须先转交所有备用责任再销毁槽。保留真实晚释放与无新输入进度；不能在map析构中临时拼provider释放 |

选择ActivePending并非声称保留“免费”：此前这些同源backing实际就在该类，且拥有退出headroom。它表示有界transaction工作容量，生命周期可能更长；若完整压力结果表明保留挤占预算不值得，就禁用/放弃保留。`maxTransientVersionsPerPage`继续约束逻辑版本，physical容量和节点存储仍由原实际预算约束，不能因metadata删除而漏收费。

备用槽只有选择事实，不再保留一份旧descriptor/proof/metadata快照作为查询权威。实际目标类型只覆盖同provider/布局、同步完整输入且可保留上一成功值的H1域；其他producer继续原Fresh/既有计划。无命中入口的查询应并入已有write-base/原page节点查找，不能为H0再增加一轮全表检查。

## 4. 原33项内的实现与删除索引

| 原索引 / 当前位置 | 本次具体要求 |
|---|---|
| T03.1/T03.2：`Store::prepareTarget`、`WriteCoordinator::prepareWriteBaseLocked/prepareWritePlanLocked` | 从原page槽取得备用事实；空槽并入原查找；checkout失败只清退该备用、保持Fresh。命中替代reserveBacking/provider Fresh/registerBacking整段，不保留一条另行复制的安装/取消政策 |
| T04.1–T04.3：`PublicationDelta::ProofMap`、`PreparedOverlayUpdate::{prepare,tryAcceptLocked,finishUnlocked}` | 原槽容纳当前proof与最多一个备用；接受准备时形成可无分配安装的交接，避免先Historical→完整Debt→立即重新注册。旧未命中路径保留collector；已命中不再同时安排同一record回收 |
| T04/T07.2：`MetadataCoordinator::{preparePublicationImpl,installPublicationImpl,discardHistory}` | 在原精确Prepared detachment政策内添加合法的逻辑退出，不增加第二状态机。保护不满足仍转Historical；并发capture/revision冲突不能被“先前idle”覆盖 |
| T05：`OwnerLedger::{prepareBackingHandoff,commitBackingHandoff}`、binding/provider | 复用已有physical、binding、backing节点及退休存储。新代次拒绝旧handle，保留alias/驻留/last-use与真实physical独占；不为通过而放宽RetirementDebt入口 |
| T04.4–T04.12/T06：publication原proof读者及导出 | `resolveVersionLocked`、prepared set校验/导出、capture inputs、commit准备、extent/clone/枚举只消费当前proof。备用字段不增加可见版本、不改变history/restore结果 |
| T02.2/T07.1/T07.2/T07.3：delta退出/原retirement queue | 覆盖`m_preparedTransactions.extract`的commit/abort两处，单页`proofs.erase`、removal、shutdown；所有备用的原record先交接，再销毁含它的节点。`retireRecord`的已接受provider结果、重试/最后free沿原政策 |
| T08.1/T08.2 | 真实逻辑capture、native/alias、checkout后拒绝、跨页接受、满额/取消/close/晚释放、H0/未命中与业务控制；模式命中和删量先于独立净价格 |

所有具体当前符号/行和源码SHA在[索引](donor-source-index.json)。备用目标不进入root/overlay查询，是相对现有API拆分的核心责任调整；仅加入free-list然后保留全部新建/退出并未实现本方案。

## 5. 数量模型的修正与仍欠的净价

有界模型覆盖单页最多4个physical、6次开始、3次接受、深度10，**2616个状态、5640条转换**；每状态均验证最后reader释放后可以由原退出责任排空，并验证held字节/上一成功值不变、pending不能与held重叠、所有physical均有收费责任。故意复用held目标的反例被拒绝。v1将保留也错误要求独占，已保留旧模型；v2将保留与checkout分开。该模型不证明C++锁/metadata安装或精确父子预算，不计产品测试通过数。

四manager寿命、K16/W16、同布局完整写，**仅源manager非默认physical建立量**：

| 构造环境 | 原模型建立量 | 条件目标建立量 | 条件少建 | 每寿命源physical峰值模型 |
|---|---:|---:|---:|---:|
| 无持续外部holder | 1088 | **192** | **896** | 48 |
| 首个Prepared结果的一页持续原生holder | 1088 | **196** | **892** | 49 |
| 首个Prepared结果的16页持续clone | 1088 | **256** | **832** | 64 |

后三列是构造结果，非实测优化后结果；不含clone侧metadata/默认对象/额外provider登记，不能当全fixture驻留预测。W1保持`4K×2`，删量0。保护阻止一次取用时需要另一个物理工作目标，不能用原896预测所有压力格。原库资源观察门未获补授。

以普通H1为条件，完整实现应同时验证：provider Fresh、binding/physical登记、owner backing/退休record建立与最终退出随实际physical建立从1088向192变化；逻辑generation、每次接受、公共17MiB写和18MiB显式读保持。960个逻辑旧版本退出仍要发生，只应合并到原接受流程；不是删除960个版本事实。新增约896次checkout准入/retag、备用槽保留/清退与失败代价必须扣除。不能再把这些生命周期中completion、预算锁、节点清理各领一次独立收益。

**净指令/CPU仍未知。** 本包排除了“只在下一prepare查找现有历史目标”和“先放宽Debt类”的实施方向，关闭了原组件即时可接性；它没有运行完整重用，不拿probe额外开销给目标算法定价。净价现在缺的是一个明确的完整替代：原接受内逻辑退出＋有收费备用槽＋下一次原claim/retag＋所有槽出口清退。确定这条实际差集后才能冻结探索报价；最终15%指令/原CPU门及八块独立确认保持，不将工程门写成预期收益。

## 6. 复现、失败与证据边界

两能力＋六正式过程全部完成。r1派生库构建成功、夹具误用KisSharedPtr::reset而编译拒绝，未测量；r2修成空赋值，另目录重建，原失败完整保留。mode2只做真实prepare/claim/cancel，**没有commit retag或metadata删除**。查询采用完整metadata快照并释放owner gate，价格和调度均不移授plain。

[donor-raw.tar.xz](donor-raw.tar.xz)保留源码派生diff、两版构建与失败、协议、命令、8个完整日志/JSON、实际加载库和依赖SHA、两版模型；[76个成员清单](donor-raw-manifest.json)。二进制/对象不打包，哈希与本地构建命令保留。7900项复核含471份身份文件、全部计数分区/claim-cancel/输出、23处源码符号定位和原33行，不是新增7900项产品测试。包SHA256：`8a5811bc18a38bc36b5a828b90906b290f550b6193fbcc439b9b0c67072cf646`。

```sh
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_pipeline_refactor_20261010/model_donor_lifecycle.py
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_pipeline_refactor_20261010/finalize_donor_probe.py
```

复算要求冻结本地依赖仍在；身份不匹配应拒绝。全局CPU观察门、合法净收益排名、正式M6/M7/M8 0/3、校准2/20、默认关闭及旧控制欠项均保持。下一工作应实现并反测上述完整有界替代，不再把这次探针扩成新的热路径scope采样。
