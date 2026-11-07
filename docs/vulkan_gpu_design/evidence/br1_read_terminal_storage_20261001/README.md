# CP1：原 read 终结存储、固定重试与选择保护

2026-10-01，产品分支 `refactor/brush-s2-predefined-sanity`。产品父提交 `125ed0c0e2a7d5224a062239330066a638803e88`，文档父提交 `fe39219ea0c6c76bb5e2cef050a21642017cd644`。当前合同为 [92 §16.35](../../92_br1_m6_m8_execution_baseline.md#read-terminal-storage)；本目录只冻结这一子范围，不是完整CP1或M6–M8资格。

原cancel/release重试还分配ID deques，ack/close/worker复制matching/pending/released列表；last-use订阅准备拒绝后原债务只能等手动输入。此轮复用原request/lease身体的hooks、ready节点及冷准备context/task/Delay，同批替代上述容器、旧懒prepare/dispatch停摆和Store聚合。GC通知拒绝在原记录保留key/阶段；接受后节点转移到原cleanup，owner锁外实际free后才归还activity。effects异常出口用作用域保证重锁与活动计数归还。代码审查不等于整个history/core的全局分配失败原子性证明。

request节点准备必须先于版本选择，随后选择与AcquireRead保护共享owner锁区间；原register填值/转节点。准备后的候选和terminal节点复用原cleanup预算map，无第二request表、worker、GC或payload权限。新增两个private操作及19个原方法的测试链接可见性见 [API账本](../../br1_modification_guide/API_CONVERGENCE_MAP.md#read-terminal-storage-api-delivery)，具体原文件、consumer和剩余改动见 [CODE_INDEX](../../br1_modification_guide/CODE_INDEX.md#read-terminal-storage-code-index)。

[生产差异](production-incremental.diff)为6文件增419/删227，[测试差异](tests-incremental.diff)为1文件增204/删0；另3个审计JSON，共10个产品路径，见 [source-metrics.json](source-metrics.json)。派生调用图的行号/边关系不算人工生产行数。tool/strokes/Painter/PaintDevice/scheduler生产改动和public/protected API净增0，没有上层业务协议扩展。

## 最终目标结果

[build-qualified.log](build-qualified.log)之后的同源统一结果：

| 目标 | arm64 | x86_64 | 范围 |
|---|---:|---:|---|
| KisPageStoreCpuMutationTest | 1262/0/0 | 1262/0/0 | 全组；9个新增原read组合数据行，既有真实Store history/last-use/lifetime/close及overlay目标重测 |
| KisPageStoreReferenceTest | 659/0/0 | 659/0/0 | 全组 |
| KisPageStorePhysicalClaimTest | 379/0/0 | 379/0/0 | 全组 |
| FreehandStrokeTest | 4/0/0 | 4/0/0 | 原persistent autobrush pressure及cancelled两个方法，含init/cleanup |

合计 **4608 passed / 0 failed / 0 skipped**。实际argv、exit、用时见 [results.json](results.json)；原始日志为各目标arm64/x86_64文件，统一执行记录见 [run-qualified.log](run-qualified.log)。[runner](run_results.py)固定 `_build-br0-cpu/bin`、同目录插件、原 `_install` prefix、offscreen、seed12345和目标期望数量。新增与曾失败的overlay目标先按受影响范围检查，[focused-results.json](focused-results.json)两架构各18/0/0；不将该次数累加到最终4608。

9个新数据行组合原read/metadata/epoch/history/retirement和真实imported provider replica，MetadataArena从构造前固定为64KiB，用实际storage allocator占满并释放。覆盖Succeeded/Failed/Cancelled与begin/cancel-close重臂，stop后晚completion不再派发；订阅无法准备时至少三次自动pass，终态无新request/手动ack恢复，原read/metadata保护清空，实际节点退费、activity及root pin归还。另两行分别拒绝request准备和lease准备：原request保留，provider resolve计数为0；真实释放容量后同request恢复，或取消原request后实际node费用归还并可再请求。

这些组合目标没有放宽Store初始化后冻结budget的合同，没有friend probe、owner字段修改或新增预算getter。它们不证明整Store恰满close、历史版本物理退休、history内部全局bad_alloc或完整公平性；原真实Store对应目标是在当前CPU全组重新通过。

## 初始失败及修复

- [initial-fixture-failures/reason.json](initial-fixture-failures/reason.json)：首轮9个新行错误地在Store初始化后调预算，现有冻结合同拒绝；旧目标通过。原八份日志及结果保留，改用预算构造前冻结的原owner组合，未修改产品合同。
- [selection-window-failure/reason.json](selection-window-failure/reason.json)：组合夹具的published cache最初把physical版本default revision设为1，实际应取replica完整身份；另外arm64原 `genericRemovalRemainsAbsentUntilSeal(lease-cancel)` 读返回空，是真实新窗口。原register在选择后为request节点解锁，历史GC可先移除临时default；现在原cleanup在选择前准备节点。该轮9个夹具失败和1个产品失败全部保留，不计最终通过。
- 构建过程中一次private query使用被编译器拒绝，改用原公开pageSnapshot验证真实保护；[build-fixture.log](build-fixture.log)保留。所有普通产品/测试/文档改动使用显式patch；过程构建日志不授予最终身份。

## 审计、身份和提交

[最终图](callgraph-qualified.log)为1907 APIs / 20761 edges / 20 callbacks。[正常结构门](architecture.log)通过21 manifest / 25 ownership / 16 census / 19既有侵入文件；没有新增manifest或放宽上层限制。[首次门](architecture-initial.log)只报7份源码checkpoint失配，在原owner审查/调用图重建后更新 [前](baseline-before.json)/[后](baseline-after.json)checkpoint，再独立运行正常门。

[source-sha256.txt](source-sha256.txt)冻结33个源码/测试/审计文件，[runtime-sha256.txt](runtime-sha256.txt)冻结实际4个目标及8份库/插件；与前批相同清单并新增本轮Publication源码。image/ui由本轮build目录rpath解析，CPU Mach-O加载配置见 [runtime-rpaths.txt](runtime-rpaths.txt)；完整同依赖upstream对照仍属CP0，不能由12份identity推定完成。[freeze_evidence.py](freeze_evidence.py)只读产品/文档，写派生证据，不改实现。

产品提交见 [code-commit.txt](code-commit.txt)，父固定上述§16.34提交；[git-round-identity.json](git-round-identity.json)核对暂存集合、父提交及33份源码blob。文档仓单独提交8份活动文档、本证据与Gitlink。原未跟踪build/图片及其他证据不收录，无push或历史重写。纯提交和文档编辑不额外重跑产品矩阵。[文档与身份验证](document-validation.json)对应 [validate_documents.py](validate_documents.py)，归档不参与当前校验。

产品提交 **`9a5e24a88901681f2595d0ddaeed3adf3fa99e35`** 已完成，33份源码blob及12份runtime身份相同，tracked产品树清空。审阅从上述父提交取本轮差集；文档仓Gitlink同步指向该提交。

产品源码及指导文档空白检查通过。外层格式检查只排除两份原始unified diff和保留Ninja失败行尾空格的 `build-fixture.log`，逐项见 [document-whitespace-exceptions.json](document-whitespace-exceptions.json)；不改写失败日志或放宽普通源码/文档规则。

## 仍须关闭

完整CP1未结算，M6/M7/M8正式资格仍0/3、默认关闭。captured release deque/版本复制、history scans/keys/candidates/effects/metadata snapshots、retirement core effect/operation及ledger/provider/registry索引、close handles/seen/诊断、tree/deferred对象及一次性task、控制本体与runtime/clock固定成本继续开放。本批不是全pass allocator interposition、全局分配失败原子性、TSAN、多文档公平/原job continuation或BR1-PERF资格。

下一沿原captured/history/pass owner整包准备必要容量、实际收费、保留原token/key/effect、无输入恢复及最后free，见 [NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)。已经删除的read包装、ID索引、ack快照和冷任务通知不再领取。
