# CP1 等待存储结清：九类原 owner 的隐藏容量关闭

产品 `0d3b9f5d87e16e01587acdb03e00985ac07aae80`，父 `1103defd830d463c50f8c6a83dd05cc8077e0bf3`；外层父 `9acec8f97ed086922186dfd6f1364a0fcf2c76ec`。依据代码、92、cohesive-refactor；未读取 archive。**整包 CP1 仍不通过，M6/M7/M8 正式 0/3，persistent 默认关闭。**

## 实际存储与唯一释放责任

上一轮真实栈确认 owned `QWaitCondition` 每个另有 120B 私有 heap，原 enclosing `sizeof` 只含指针。本批删除九类成员的 Qt pimpl，改成 `KisPageWaitCondition` 内嵌 mutex、condition_variable 和通知序列。原业务谓词、owner mutex、等待 caller、close/drain 和最后引用不新增第二套状态。等待释放 owner 前占通知 gate；恢复先释放通知 gate 再取 owner，避免与持 owner 的 wake 反向锁序。

| 原实际 owner | 等待成员 | 收费与最后 free |
|---|---|---|
| Store Private | writeAdmissionChanged | 原冷根 allocator / Private 最后释放 |
| DeferredMetadataCleanupStatistics | idle | 原统计 body/control allocator / 最后 cleanup 引用 |
| Ledger Private | physicalClaimsChanged | 原 Ledger 冷根 allocator / Private 析构 |
| DefaultStorage | m_preparationChanged | 原 Store 内嵌 body / Store 最后释放 |
| RetirementQueue | m_idle | 原 Store 内嵌 body / 已接受工作 drain 后释放 |
| HistoryCollector | m_idle | 原 Store 内嵌 body / collector drain 后释放 |
| HistoryCollectorWakeContext | idle | 原 wake body/control allocator / 最后 callback 引用 |
| ReadCoordinatorWakeContext | idle | 原 wake body/control allocator / 最后 callback 引用 |
| Tiles3 TransitionGate | m_transitionChanged | 原 provider shared body allocator / 最后 observer/transition 引用 |

Darwin native 探针中该组 owned 120B 分配消失；内嵌容量随上述原 body 的实际 `sizeof` 收费和析构。caller Image/Tile/undo 的 Qt 对象仍属于 caller。不能据此推定所有 Qt/OS/malloc 内部容量和未验证平台都已覆盖。

生产13文件 **+74/-22，净+52**，测试三文件 **+14/-7，净+7**；两个审计生成物另计。私有 helper 有九类生产 owner 和原 WriteAdmission 消费者，删除全部 PageStore `QWaitCondition` 成员及旧借用签名。上层生产 API、业务 owner、队列和阶段净增0；每次 wait/wake 新增内嵌通知 gate 的同步成本。

## TSAN 报告与裁决

[首轮八目标](tsan-01/runs.json)越过旧 Qt wait/relock double-lock：Completion、Foundation、PhysicalClaim、ReadBaseline、Reference 五组正常退出；ResidentRead、CpuMutation、DataManager各实际66，原报告完整保留。

ResidentRead 测试 hook 清除与后台 retirement 读取是实际无同步访问。hook现限定到原测试线程，后台直接调用原 provider，关闭捕获测试 stack/counter 的晚寿命竞态。CpuMutation 故障开关已有 semaphore handoff，未插桩 Qt 不向 TSAN 提供同步证据；改成 atomic，使证据无需依赖隐藏实现。两组完整重验 **221/0/0、1334/0/0，exit0，无报告**，见[第二轮](tsan-02/runs.json)。

DataManager 的 `planGrowth`/`install` 均持同一 migration `QReadWriteLock` 的读/写 gate，不能将报告裁定为实际无锁竞态。[独立控制](tsan-qt-sync-controls-01.json)对同一 Qt/TSAN：标准 shared_mutex保护20000次共享写exit0；Qt QReadWriteLock完整保护仍报race66，Qt semaphore handoff也报race66。clean/race正控制0/66。未重写 extent gate或加广泛suppression；DataManager被首报截断，后续测试没有全局clean证据。

当前八目标最新同源二进制：**七组通过，2892项，无报告；全局仍Inconclusive**。两个fixture修复后生产image及其余六目标二进制未变，[冻结文件](final-freeze.json)验证原结果和最终文件。原登记八旧UE的[快照](old-ue-final.txt)仍未drain；全进程复查又发现此前未登记的pressure进程91827（10月2日晚开始），SIGKILL后仍UE，当前退出欠账至少九个，见[增补清点](old-ue-discovery-final.json)。需宿主处置后默认失败退出复验；本轮全部新测试进程真实退出。

91827的[实际sample](old-ue-91827-sample.txt)停在原资源初始化 `registerResources → KoResourcePaths::getInstallationPrefix → QMessageLogger::fatal → abort → pthread_kill`，并带Rosetta exceptionserver。尚未进入压力测试方法，因此不是压力合同已运行失败或成功的证据；其失败退出仍未drain。只能定位原资源初始化fatal与当前退出栈，不能凭sample判定Darwin/Rosetta为何不响应kill已彻底解决。

## 实际分配与同源结果

最终双架22原进程 **8088/0/0**，原压力三对 **72/0/0**，全部exit0。116已提交源码、113运行物、四配置，工具输入和产品image绑定。allocator/native的生产源码closure在两个fixture修复间未变，冻结文件明确列出两个无关fixture的inventory差异，没有改写原身份。图 **87 TUs / 2160 APIs / 27231 edges / 25 callbacks**，21manifest/25ownership/16census/19intrusion，ratchet不放宽，六工具自测通过。

allocator每架原操作 **224拒绝/3控制**，冷构造/订阅/task **17拒绝/3控制**通过；最后弱控制、连续COW拒绝、数组新旧重叠与费用恢复保持。static executor/resource实际析构后paid heap为0；stop固定仍为2132/2140B，静态60B保持至进程映射退出。

原freehand native六方法两架12/0/0、exit0；普通malloc12345B live/free正控制，无overflow。

| 观测指标 | arm64 | x86_64 |
|---|---:|---:|
| 全参与者requested heap峰值 | 98,932,537B | 98,918,738B |
| 可识别paid链峰值 | 6,803,114B | 6,896,146B |
| 合计节点峰值 | 28,630 | 29,643 |
| 原main结束paid尾 | 672B | 680B |
| static后paid尾 | 0B | 0B |

测量从原框架初始化后、测试方法前开始，包含caller；paid分类是识别子集，不是完整owned对账或总硬界证明。pre-main/框架启动、符号服务递归、usable/RSS和非Darwin未纳入。生产硬预算未放宽。

生命周期矩阵 **505原进程：18控制、487首末目标；383成功、122实际失败exit9**，与上一候选逐组数量一致，见[全部结果](lifecycle-matrix-01/results.json)和[失败集合](failed-processes-final.json)。checkpoint54/commit54前期拒绝后原session取消；checkpoint4/commit4重放已准备页而stale；commit6 root已安装、后置retention拒绝后原capability失效。计数、旧冻结像素和一次pixel body有检查，仍未满足同owner retry/不重放接受事实的完整条件。probe fatal handler不是产品默认失败退出证明。

93文件 **1713复核位置**仍是lexical输入，不能当完整覆盖证明。

## 用户八项的当前处置

| 项 | 本批结清与剩余 |
|---|---|
| 1分配/free | 九类owned Qt wait关闭；其余每笔owner/capacity/accept/free完整对账仍欠 |
| 2逐拒绝矩阵 | 原操作/冷矩阵保持；505进程122接续失败开放，不用常规绿矩阵覆盖 |
| 3全局/峰值 | 正控制、请求heap/node及已识别paid/static尾可复现；全费用与同时reserved/live/peak仍欠 |
| 4拒绝/恢复 | 8MiB准入后取消、capture硬满恢复保持；partial seal、commit输出前置和联合永久拒绝/自主恢复仍欠 |
| 5最后引用/退出 | 等待容量随原owner释放，识别的anchor实际free保持；完整晚guard/Data/weak/callback逐笔仍欠 |
| 6框架/平台 | caller不重复收费，九类owned Qt wait已修；其余Qt/OS/TLS/malloc和非Darwin仍欠 |
| 7并发/失败退出 | read fixture实际竞态关闭，七组TSAN通过；QReadWriteLock边界Inconclusive，原八旧UE加新增发现的早期pressure UE共至少九个未drain |
| 8冻结 | 当前单位绑定完成；1–7剩余未通过，整包CP1不勾选 |

下一责任是前移commit可失败after-root retention，再收敛原segment seal的部分准备和同owner重试：接受事实留在原metadata/proof/history记录，provider不重放，拒绝不销毁可恢复scope。不得按错误种类新增旁路阶段或恢复队列。
