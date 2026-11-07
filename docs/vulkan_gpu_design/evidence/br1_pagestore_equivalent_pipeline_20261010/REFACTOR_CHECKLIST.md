# 完整重构排查表单与放行条件

> 生成的填写规范。状态只写入 [唯一索引](PIPELINE_REVIEW_INDEX.json) 的 `refactor_execution_matrix`；[22项任务矩阵](REFACTOR_TASK_MATRIX.md)是同一数据的展开。不要创建另一份进度表。

原型优化迁移阶段已验收。下列规则保留原包的证据要求；当前方案及新工作包见 [V3](PIPELINE_PLAN_V3.md#next-package)，状态在同一索引的 `pipeline_plan_v3`。RF20/21证据开放不重开已完成迁移。

本包要解决的是原型与生产的**工作生成率、事实传递和生命周期**差距。旧8项契约已删，不等于现在每段重建、跨层接受、付费服务、root/读/退出责任已达到目标。保持原33行，不把某几个改动的提交或测量称作整体落实。

## 每项必须填写的表单

| 字段 | 填写要求 | 不能接受的替代 |
|---|---|---|
| 必要输入/输出与观察点 | 本责任何时必须发生、真实消费者需要什么、允许何种失败 | 现有函数被调用所以必要 |
| 当前与理想路径 | 操作顺序、访问集合、最小状态变化；每个跨层边界的合同理由 | 新helper包住旧调用 |
| 唯一权威与寿命 | 原owner、稳定位置/容量与当代权限分开、失效事件、最后使用者 | 再加影子Record、全Store busy或第二账本 |
| 锁/回调图 | caller已持锁、需要的锁、解锁后失效、provider/析构回调重入 | 同名入口假定同一锁上下文 |
| 全量消费者 | 路径/符号、调用条件、模板rebind/override/callback/worker/晚尾、迁移或必要保留 | 用本表的种子清单冒充完整census |
| 替换删除 | 旧符号/字段/分支→最终原owner/表达→同批删除证据；包括旧失败恢复 | 改名包装、注释“以后清理”、沿用r6旧PASS |
| 保留边界 | 实际合同、真实消费者、不能更直接表达的理由、成本归属 | “可能以后需要”或“最小成本开放”掩盖待做 |
| 失败与退出 | 接受点、已发生副作用、谁承接、是否真实可重试、取消/close/最后free | 成功后清理失败改报未执行、所有拒绝一律重试 |
| 数量预测 | F/N/D/S/U等真实变量；冷/暖/规模/压力；删量与新量分列 | 把次数降幅当指令降幅，K1716当下界 |
| 净价预测 | 当前责任价、相对差额、合法可回收价分列，纳入新责任/后台/尾 | 父子桶相加、未知填0、把20.340M全认领 |
| 行为与资源证据 | 真实反例、源/库身份、峰值/驻留/保留时长/最终退款 | 总PASS数替代合同覆盖、最终归零替代峰值 |
| 联合验收 | 同一完整候选的预测/实际/新增/残差及置信范围 | 每改一点就启动普通对账、局部下降宣布落实 |
| 交付与剩余 | 每批更新同一任务的delivery_summary，累计已落地子责任、未完成事项和审查源摘要分列 | 只写“进行中”；用已启动比例冒充完成比例 |

机器字段：`consumer_census`每条至少含`source_location`、`disposition`（`migrated`或`retained_required`）、`evidence`；全量检索闭合后才置`consumer_census_complete=true`。`retained_boundaries`每条含`contract/consumer/minimum_representation/cost_scope/evidence`。`deletion_proofs`保存零命中/语义替换diff等实际证据；至少覆盖卡片全部删除登记，人工审查数量以外的语义闭包。

每个状态证据是对象：`path`（相对此目录或绝对路径）、`sha256`、`candidate_source_digest`、`summary`。`verified`必须绑定最终候选，已有旧证据可引用背景，但不能冒充本轮验证。实施行的迁移/删除不允许标“不适用”；非实施行的对应责任由依赖项承担。

## 固定执行顺序和停止规则

1. RF00冻结同义合同、锁/寿命边界；RF01–RF16补足各自设计与消费者调查，RF18形成完整数量/净预算。关键选择缺证据时只登记有限判别（假设、范围、停止条件），不展开逐点普通计价。
2. 在原owner内完成RF01–RF16全部替换，迁移真实入口并同步删除。可做技术提交、构建、结构检查和聚焦的正确性/并发/失败/资源测试；这些只推进相应维度，不触发整体收益声明。
3. RF17全量删除审计，RF19完整受影响行为/资源验证。所有待迁、临时桥、没有理由的保留项必须清空；必要保留由具体合同与最小表达论证。
4. RF00–RF19完成并冻结候选、RF18预测和完整实验协议后，执行严格预检，才能进入RF20。机制/资源数量先核，再做未插桩联合净价。任何旧源码PASS、缺身份、缺消费者或缺退出证据都不放行。
5. RF21分别裁决结构落实、行为正确、预测兑现、成本目标和正式资格。负结果可完成一次评估，不能称目标通过；未完成实施不能以“仍可优化”改写成完成。修复真实回归须重新冻结受影响证据和新批次，不能不断补样追通过。

实施期间不得缩减本包22项和原33行。新发现属于既定合同的缺口填回同一矩阵；不以新主线绕开旧欠账。真实外部合同允许保留最小边界，不要求盲删原型没有的生产能力。

## 五个状态维度

| 维度 | 何时可标已证 |
|---|---|
| 设计 | 理想表达、锁/寿命/失败和数量预测已审定；未决关键问题有明确结论 |
| 消费者迁移 | 实际census完成，所有consumer迁移或有必要保留证据，且无第二核心协议 |
| 旧实现删除 | 原定旧状态/分支/恢复被删除，保留项有合同和最小表达说明 |
| 行为验证 | 本候选的正常/失败/取消/晚读者/回调/压力/close/尾端点已覆盖 |
| 联合计价 | RF20整包测量覆盖该责任，并报告预测、实际、净增和残差；不要求每项都有可分离正收益 |

“设计完成”“代码完成”“整体已评估”“成本目标通过”“M6资格”是不同结论。整包代码完成也必须经过联合验证才能按本用户要求宣告整体落实；目标没过就明说未过。

## 量价约束与尚未闭合项

冻结H1 P/K申请2976/1716，1260差额逐栈100%覆盖，只是**次数来源账**。前台指令模型仍偏差−0.518070M；H0后台/尾差约6.109835M待拆。两页8cuts多8投影行已在当前同条件逐行归因：最终commit旧Current→Idle并逐出同key原Idle；同32KiB Current限额P成功/K拒绝，不能把少8行当同义下界。见[来源与硬额反例](refactor-fee-trigger-r0/RESULT.md)。 保留未知，不能自动归为必要管理成本。

stage/seal、paid等互斥桶只入总账一次；P内部细分价与粗分净差不混加。原型缺生产语义，也不是upstream；20.340236M仅受限参照距离。完整paid<1M仍是工程目标，搬到别的阶段/线程的服务成本须加回来。管理/内容比与同语义upstream差额各自需要真实分母，通用优化不能算PageStore特有性能证明。

正式门仍见 [92 §6.1](../../92_br1_m6_m8_execution_baseline.md#61-m6机会型能力门当前cpu范围)：命中正收益下界>0，原控制/miss吞吐下界≥0.98，校准/安全/资源/结构/family分别满足。旧20%/30%不是硬门。本表不授M6/M7/M8资格；当前0/3、calibration2/20、默认关闭。

## 预检命令与证据约定

在仓库根目录运行（不运行任何产品或性能测试）：

```sh
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_pagestore_equivalent_pipeline_20261010/refactor_tracking.py --render
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_pagestore_equivalent_pipeline_20261010/refactor_tracking.py --check
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_pagestore_equivalent_pipeline_20261010/refactor_tracking.py --require-ready-for-performance
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_pagestore_equivalent_pipeline_20261010/refactor_tracking.py --require-closed
```

`--check`只证明表结构/映射/生成视图有效，不授放行。`--require-ready-for-performance`检查RF00–19、候选身份与完整协议；前置尚未结清时必须非零退出，不能将永远失败写成门禁目标。`--require-closed`还要求所有22项联合证据与结果；它表示完整评估，不代表成本目标通过，目标裁决另列。

`candidate_identity`需填产品HEAD、`git_tree`、实际参与构建的`source_files`（产品相对路径→SHA256）、`source_digest_schema=sha256-path-map-json-v1`及`source_digest`，以及`ordinary_library`和`build_manifest`的`path/sha256`。摘要采用UTF-8、排序键、紧凑JSON分隔符及ensure_ascii=True。构建清单必须绑定同一源/树/实际库、成功退出和构建命令，列出的构建输入哈希也须一致；包括未受git跟踪但实际参与编译的输入。工具检查列出的内容，不替代构建依赖审计。最终计价要求受跟踪产品改动冻结到提交。

历史consumer/deletion/retained登记保留原来源和哈希；不得改签为当前候选。`acceptance_revalidation`可为整份原登记提供当前重审回执：绑定当前源、完整登记摘要、逐项决策、实际源码锚点，以及在当前源重新执行并通过的检查。工具拒绝漏登记、漏决策、旧候选、假检查、失效锚点和篡改历史来源。它只解决证据身份，不自动完成设计、行为、资源或联合计价。

`frozen_joint_protocol`除证据对象字段外，需含全部`covered_task_ids`以及`prediction_account/endpoints/sample_plan/failure_stop_rules/controls/resource_plan`。`joint_result`需含全部任务及`prediction_vs_actual/residual_account/raw_manifest/semantic_checks/ordinary_controls/target_verdicts`；详细文件均须可复核。

预检已接入本包RF20实际启动器，尚未接入生产CI。它能阻止缺字段、缺证据和明显局部完成被标成整包就绪，不能自动证明设计最优、consumer清单穷尽或证据内容真实；这些仍须按每项表单审查。候选源码改变后重审受影响证据，不能修改hash让旧结论自动适用。
