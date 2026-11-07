# CP2 epoch、晚 completion 与共同准备终结

产品提交 `25ae0dbf8149e8c6620fc5a42d3b15b957bc37b3`，父 `39700f0d53f249eed4ea189fe7d0ed98635a9ee0`。当前裁决只见 [92 §16.113](../../92_br1_m6_m8_execution_baseline.md#cp2-epoch-preparation-delivery)。[逐要求审查](cp2-audit.json)结合当前代码和完整结果，关闭 §16.112 的两个有限差集及 CP2 代码/安全范围；CP3/M6 正式资格仍开放。

实际共同计划在 metadata/physical 安装前可能因收费 candidate 或 descriptor 分配拒绝抛出 `std::bad_alloc`。generic 已有拒绝入口，native 原调用未捕获。修复只在原 `beginWriteImpl` 接回既有 `fail` 和空 slot 清理，后续 cancel/abort 继续原 owner；没有新状态、结果类型、API、字段、队列或锁。生产 +10/-4（净+6），测试 +358/-2（净+356）；这是拒绝保证增量，不记等价删除或性能收益。完整差异见 [candidate.patch](candidate.patch)，成本与 Git blob 核对见 [delivery.json](delivery.json)。

完整CP2相对首包父提交 `b51a7602c82bbee6bf2a0df79400dd943d6df5b6` 的实际Git差集为生产12文件 +229/-187（净+42）、测试4文件 +1063/-31（净+1032），见[整包收敛账本](convergence.json)。raw准入/解锁、原batch能力、G0只读存储和clone构造分别接回原责任，同批删除旧oldData/attach桥、空backend回退、重复初始化与解锁分支。原真实consumer保留理由和最后净+6的保证成本分列；净行数不表示量化功能密度或性能收益。

## 有效父红与真实分配栈

最终父版使用与最终候选完全相同的测试源码：[parent-final-test.cpp](parent-final-test.cpp)。arm64/x86_64 的 `parent-debt-corrected-*` 均为 98 passed、24 failed、actual exit24/reaped，失败仅为 native 的 point0/2；generic、metadata、ActivePending/实际 Debt 的 controls 通过。测试外层捕获把异常记录为正常失败，避免再次进入宿主异常退出。

- [point0 真实栈](parent-stack-native-point0.log)：136B `KisBackingClassChange` vector，从 `prepareBackingHandoff` 经共同 plan 到 native `beginWriteImpl`。
- [point2 真实栈](parent-stack-native-point2.log)：80B descriptor 树节点，在 physical claim 前拒绝。

上述 LLDB 以主线程 `__cxa_throw` 停在实际 allocator，继续后 target 正常 exit1；JSON 的 `debugger_exit=0` 只属于 debugger。更早 `parent-stack-point0/2` 停在 Qt Security 线程的无关异常，不能作为 allocator 证明。

## 联合验证

`productionHandoffEpochAndLateCompletion` 每架48项：四BPP × native/generic × 准备后/安装后 × 三terminal。真实两个 provider/Store/Ledger 使用同 provider ID、numeric slot/allocation token 与共享 registry。原 provider 拒绝原地改 epoch；旧 handle/proof 不得释放新 pending last-use，新 ticket 完成后真实 handoff 可进展。每个 incarnation 内实际复用原地址，G1 暖缓存重新解析独立 B 保持0x31；不声称跨重启复用地址或完整 allocationIdentity。

`productionHandoffPreparationCapacity` 每架120项：四BPP × 两载体 × 五有限压力点 × 三终结。实际 parent metadata 实满触发 charged candidate/descriptor；保留1024B令 accounting 成功、metadata 拒绝，然后在 descriptor 前解除压力；ActivePending 用另一真实 pending 页占满；Debt 用拒绝 retire 的真实 cancelled payload 占满。Fresh 关闭时拒绝不能被绕过，cleanup 后 A/B 都能真实 claim/reset；原失败终结后同 Store 新 transaction 成功 handoff，覆盖 cancel+abort、seal+abort、seal+commit、旧 exact 字节与 close 归零。

原 `retirementPreparationRollsBackAtCapacity` 用冷 Ledger 的0–4096B/64B扫描覆盖共同 `storePreparedChange` 的 scratch/slot/claim-node 部分失败后重试；accounting 原语负例和144项生产双次序验证 class claim/revision/物理排斥。审查不以原语代替 epoch 与 allocator 拒绝的联合生产结果，也不为同一 rollback scope 增加故障框架。execution 外层 catch 仍有隐式 default 等其他冷准备消费者，保留原 `preparationOnly/finishPreparedWrites` 政策。

## 最终同源结果与身份恢复

| 目标 | arm64 | x86_64 |
|---|---:|---:|
| 完整注册 DataManager | 1311/0/0 | 1311/0/0 |
| CPU Mutation | 1562/0/0 | 1562/0/0 |
| Reference | 790/0/0 | 790/0/0 |
| PhysicalClaim | 397/0/0 | 397/0/0 |
| ResidentRead | 221/0/0 | 221/0/0 |

十个进程合计 **8562/0/0**，全部实际 exit0/reaped、无超时且加载指定 libkritaimage。[results.json](results.json)合并171份source和96份runtime，全部重核，source与产品commit blobs一致。每个架构和目标的完整命令/环境/输入在各轮 `identity*.json`，原始输出在 `run.log`；当前配置仍为 LIMIT_LONG_TESTS=1，不代表未注册长测试、完整另一hash/OFF配置或正式性能。

[最终核验](verification.json)由[证据检查脚本](verify_delivery.py)重新读取实际结果、日志、source/runtime/Git blobs和调用图：两架新48/120项的完整参数集合、60条具体方法覆盖记录、有效父红及新增本地链接均核对。脚本只检查交付记录，不执行产品测试；逐要求语义仍以代码审查和实际触发/控制/终结为据，不由测试总数代替。

文档新增链接固定相对本次文档父提交核对，暂存与提交后可复查。冻结 launcher 的末尾空行按运行时实际哈希保留，不纳入格式清理；新编写文档、JSON 与恢复/核验脚本另作 whitespace 检查。

磁盘满使 `final-cpu-x86_64` 和 `final-02-manager-x86_64` 的身份/实际结果未落盘，二者不计最终通过，也不从Qt totals猜测 actual exit。最终 manager 使用另一个冻结 launcher，在产品 exit及全部输入核对后先输出实际结果，再写证据；产品 PID94629、exit0/reaped/未超时和 `inputs_verified=true` 已实际观察，但证据写出再次 ENOSPC。该输出单独保存在 [observed-manager-result.json](observed-manager-result.json)，[恢复脚本](recover_final_evidence.py)核对 running PID、command、日志 totals 和每个当前输入，再生成身份与结果。原 launcher 未改写，其 artifact writer 的退出1与产品退出0分别记录；不重跑已完成的九个目标。

## 保留失败与结构边界

初次 `candidate-capacity-arm64` 在尚未加外部测试捕获时，native 未处理异常经 Qt/libc++终止；[initial-host-exit.json](initial-host-exit.json)记录 PID80990 宿主 UE、未回收、actual child exit未知。后续安全父红与修复后最终结果均正常退出，不把旧 UE 算通过，也不再做已知终止探针。

首次 epoch 测试在释放 protected view 后断言 B 仍占容量，3项 fixture失败；改为释放前断言，原日志保留。`parent-final-*`/`parent-corrected-arm64` 的 Debt 夹具错误地把 pending 页当作 Debt 满额，24项额外失败无效；改用真实 cancelled payload 后得到最终有效父红。早期目标、初始故障、这些夹具和更早72项 safe父红均不累加到最终通过数。

当前调用图87 TU、2176 APIs、28175 edges、27 callback registrations，unresolved0。[完整图](reverse-callgraph.json.gz)无损 gzip，原 JSON SHA/压缩身份与命令在 [callgraph-summary.json](callgraph-summary.json)。[结构门](architecture.log)仍失败：26旧 source checkpoints、inventory变化、memento direct include1>0及 tile bridge引用13>9；未刷新baseline或提高上限。CP3须作正式源码/ownership/安装审阅。

磁盘压力中只删除本轮刚重建、可再生成的 Store/CPU测试两个 `.o`，并无损压缩本轮调用图；既有源码、运行镜像和其他任务文件保持。后续 build 会重新生成这两个对象，不将缓存移除记作产品删除收益。活动92文档写出和额外冻结副本压缩也因ENOSPC失败，已确认原文件及全部raw副本未变，未产生不完整gzip。2026-10-05磁盘恢复约14GiB可用后完成活动文档同步；源/运行hash仍一致，未重跑或累加完整矩阵。CP1保持关闭，M6/M7/M8正式0/3，persistent默认关闭；CP5接续、CP6–CP9业务/配置与BR1正式性能各保留其原出口。
