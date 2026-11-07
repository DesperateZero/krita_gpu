# CP1：冷准备的原退休 retry 与恰满自动恢复

2026-10-01，当前产品分支 `refactor/brush-s2-predefined-sanity`。本轮从已授权累积基线 `9697196acab538329359a2d6c5bc45c2cf001a36` 开始；文档仓起点 `1b7ce7af9fd745e38f6d6cd41222dbdf599df7cf`。当前合同见 [92 §16.34](../../92_br1_m6_m8_execution_baseline.md#prepared-retirement-retry)，不是完整CP1/M6–M8资格。

本轮先发现实际失败链：record订阅准备被metadata硬满拒绝后，备用retry仍重新分配Wait/task/capture/Delay，也可能被拒绝，原债务只能等待新输入或手动process。选择把原queue的备用进度存储移到physical adoption前一次冷准备，同批删除重建路径及没有生产consumer的旧scheduleAfter；不新增上层业务协议。

## 实际改动与删除

- 原Queue::prepareTask一次准备pass/context/retry Wait/task/capture/Delay；全部候选成功才安装。原Store::configure冷区间已调用它，本轮没有修改Store或上层文件。
- scheduleRetryLocked只arm原Delay；cancelRetryLocked只取消资格。monitor发布当前generation，takeReady最多消费一次；完成点coalesce在途新通知并沿同一self/root活动pin重排原task。
- record订阅仍持独立弱身份并收费；准备拒绝保留同node/debt，预付retry推进原provider/budget复验。不同record的取消身份没有合并。
- 删除每retry分配/捕获、bad_alloc清空分支、prepareWait懒建context，以及 `kisSchedulePageStoreReclamationAfter` / friend / one-shot变体；六处测试caller统一消费冷Delay。原1–100 ms退避、每次最多32条、单monitor/worker不变。

[生产差异](production-incremental.diff)为4文件增111/删69；[测试差异](tests-incremental.diff)为2文件增110/删12。另有原ownership说明及两个派生审计JSON，共9个产品文件，逐项见 [清点](source-metrics.json)。调用图的行号/边关系派生变化不计作人工生产行数。上层生产改动/public-protected API净增0；API逐项处置见 [账本](../../br1_modification_guide/API_CONVERGENCE_MAP.md#prepared-retirement-retry-api-delivery)。

## 最终统一目标结果

最终构建 [build-qualified.log](build-qualified.log) 后，一次统一运行4个目标的两架构结果：

| 目标 | arm64 | x86_64 | 范围 |
|---|---:|---:|---|
| KisPageStoreCpuMutationTest | 1253/0/0 | 1253/0/0 | 全组；新增registered/orphan auto与Debt额度释放3行，原manual/close及自主取消/退出继续覆盖 |
| KisPageStoreReferenceTest | 659/0/0 | 659/0/0 | 全组；新增恰满32次arm/cancel和旧callback拒绝新generation两个方法 |
| KisPageStorePhysicalClaimTest | 379/0/0 | 379/0/0 | 全组，原physical/alias/handoff结果 |
| FreehandStrokeTest | 4/0/0 | 4/0/0 | 原persistent autobrush pressure与cancelled两个方法，包含init/cleanup |

合计 **4590 passed / 0 failed / 0 skipped**。实际argv、exit与用时见 [results.json](results.json)，原始日志见 [arm64 CPU](cpu-arm64.log)、[Reference](reference-arm64.log)、[Physical](physical-arm64.log)、[Freehand](freehand-arm64.log)及对应x86_64文件。执行器见 [run_results.py](run_results.py)，固定 `_build-br0-cpu/bin`、同目录插件、offscreen、seed12345和每目标期望通过数；prefix为原 `_install`。没有因单个hunk额外测试或重复跑历史全矩阵。

新增结果明确开启自动wake：metadata计费恰为64 KiB、record订阅无法准备时原timer至少重试三次；provider恢复后registered/orphan自动drain。另一个registered对照先占满Debt额度，实际释放后无新request/input也能继续；payload归零、实际node释放退费、原root活动pin归还。Reference在metadata恰满下32次arm/cancel费用不增；阻塞第一代callback后cancel/rearm，第二代monitor尚未发布时takeReady拒绝，发布后只接受一次。

**首轮结果不合格：** 最初复制的runner误用了另一套 `_build/bin`，而本轮构建在 `_build-br0-cpu`。该轮旧binary通过不计入本轮验证，原日志/结果与原因保留在 [initial-unqualified/reason.json](initial-unqualified/reason.json)。修正path与期望数量后运行上述最终目标；没有用旧binary结果覆盖当前源码。早期build与run记录保留为过程证据，最终身份只绑定qualified构建和最终八份日志。

## 审计、身份及提交

[最终调用图](callgraph-final.log)为1905 APIs / 20654 edges / 20 callbacks；[独立正常结构门](architecture.log)通过21 manifest / 25 ownership / 16 census / 19既有侵入文件。最初正常门只报6份改动源码checkpoint失配，见 [architecture-initial.log](architecture-initial.log)；在原owner责任审查和重建图后刷新 [前](baseline-before.json)/[后](baseline-after.json)source checkpoint，再独立运行正常门。未修改manifest或放宽主干ratchet。

[source-sha256.txt](source-sha256.txt)冻结32个相关源码/测试/审计文件，[runtime-sha256.txt](runtime-sha256.txt)冻结实际 `_build-br0-cpu` 4个目标与8个运行库/插件。`_install/lib`无同名image/ui覆盖，实际image/ui由本轮build目录的rpath解析；CPU Mach-O加载配置保留在 [runtime-rpaths.txt](runtime-rpaths.txt)。完整依赖/正式upstream同环境对照仍属于CP0，不由这12项身份推定完成。派生脚本 [freeze_evidence.py](freeze_evidence.py)只读源码并写证据，不改产品或指导文档。

普通源码/文档均经显式补丁，提交分别在产品和文档仓库；产品提交见 [code-commit.txt](code-commit.txt)，其父固定为上述累积基线。范围、结果、身份、旧API删除和剩余责任一起可审查，没有push或改写历史。[文档与身份校验](document-validation.json)对应 [validate_documents.py](validate_documents.py)，归档不参与当前校验。

产品提交 `125ed0c0e2a7d5224a062239330066a638803e88` 的32份源码blob与冻结身份逐一相同，tracked产品工作树已清空；原未跟踪build/图片不收录。[git-round-identity.json](git-round-identity.json)保存该提交及范围核对，文档仓同批更新Gitlink到此提交。

产品源码和指导文档的diff空白检查通过。证据中的两个原始 `.diff` 文件保留统一补丁格式的单空格上下文空行；文档仓空白检查仅排除这两个数据文件，不改写原始差异或放宽源码检查。

## 未关闭条件

完整CP1未结算，正式M6/M7/M8仍0/3、默认关闭。此处仅证明原退休retry列明的恰满自主进度：`prepareRetirementDebt({effect})`及ledger/provider/registry operation索引、close handles/seen set/诊断仍分配；history scans/keys/candidates/effects、read释放/取消/效果及captured retry、tree/deferred对象和一次性task、Store/registry/provider本体与runtime/clock/线程固定成本继续开放。没有全pass allocator interposition、TSAN、完整多文档公平/原job continuation或BR1-PERF资格。

下一轮先核对原read/history/pass的必要终结存储和失败接续，整包关闭容量/收费/保债/自主恢复/最终free，见 [当前CODE_INDEX](../../br1_modification_guide/CODE_INDEX.md#prepared-retirement-retry-code-index)与 [NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)。已删除的每retry重建、record分区或通知框架不再领取。
