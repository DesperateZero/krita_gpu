# CP1 未归类容量观察与调用内工作区候选（2026-10-04）

本目录冻结§16.86观察；后继候选合入、共同容量规则及manager终点已由[§16.87证据](../br1_cp1_actual_capacity_20261004/README.md)结算，当前裁决见[92 §16.87](../../92_br1_m6_m8_execution_baseline.md#cp1-actual-capacity-delivery)。下述“仍、未合入、Pending”仅指本目录冻结时。

冻结主树产品为 `7804582f93bb1eb841b7520728169f0e228b046c`，文档父 `9b504fd8c630267aae52575b3e66c24e4b5170ce`。隔离候选 `38451ac4f16272c64a13c26770ebc384b0abacdd`，父780，分支 `codex/cp1-owned-local-prepared`。**该冻结时候选未合入主树，派生图及架构清点未更新；完整CP1不通过。** 冻结裁决见 [92 §16.86](../../92_br1_m6_m8_execution_baseline.md#cp1-unclassified-storage-observation)。

## 有限责任及结果

原 `prepareWritePlanLocked` 的 Prepared 只在本调用内使用，却用普通 `make_unique`，没有预算owner。独立原body在两架均记录四个调用链、296次416B请求；完整trace确认普通 `operator new`，深层framework标志不能替代ownership。候选使用调用栈中的 `optional<Prepared>`，沿原qScopeGuard的unlock → diagnostic → reset → relock清理，保留pin/physical/accounting/metadata/descriptor寿命和锁外析构，删除该堆请求及拒绝来源。没有新owner、gate、队列或公共API。

候选生产一文件+3/-1、测试0、派生0（待最终候选统一生成），本轮主树产品差集0。两架DWARF均为Prepared416B、optional424B；原堆416B及栈上8B句柄改为424B调用内值，不称总容量或性能收益。[补丁](prepared-candidate.diff)、[表示大小](dwarf-representation.json)、[候选commit冻结](candidate-commit-freeze.json)保留。旧隔离原型的120个C++源/头与此候选逐一相同；库沿主树不变的compile/link输入只替换该cpp对象，未写主树构建输出。

| 最终同次原body观察 | 主树 arm64 / x86_64 | 候选 arm64 / x86_64 |
|---|---|---|
| 完整CPU原body | 各1386/0/0、各actual0/reaped | 各1386/0/0、各actual0/reaped |
| Prepared普通堆请求 | 各296次、每次416B | 两架均0次、旧site0 |
| 各域审计溢出 | 全部0 | 全部0 |
| paid usable−request同时余量峰值 | 96,463 / 96,471B | 96,463 / 96,471B |

四进程最终对照5544/0/0，不累加早期诊断轮；[逐运行对照](prepared-comparison.json)含actual、实际加载及输入复核。原handoff/fallback/九类并发消费者三个TSAN方法290/0/0、actual0/reaped，实际加载匹配插桩QtCore、无suppression、未加载heap interposer。仅证明候选这些消费者及锁外清理，不替代完整manager及其余fault/平台终点。

## 观察边界及诊断失败

原生命周期heap interposer扩大到全部请求，添加malloc_size、逐site usable、实际模块和未归类trace；固定观察表独立于预算，审计器本身不是产品存储。arm原完整trace352个未归类Page调用链site中，4个为Prepared、4个32864B请求为dyld在trackedFree前建立审计器自身TLS（含原2048个thread-local site槽），其余344个仅作定位。见[triage](triage.json)、[完整trace](cpu-all-05-arm64/unclassified-site-traces.json)。实际payload/Tile池、调用者输出、测试callback、异常/诊断TLS、Qt/OS须按[当前外部边界](../br1_cp1_concentrated_20261003/allocation-contracts.json)追到owner，不能把image栈全当未收费或全排除。

01实际1386/0/0、退出0，但runner只认`.21.dylib`，实际加载`.21.0.0.dylib`而误判；[裁决](cpu-all-01-arm64/diagnostic-adjudication.json)及原输入保留。01–03均有12110溢出，不授完整观察资格。03确认堆/地址/site/symbol/native均0，全部来自2048个image析构槽；原body实际登记14158/14190回调，主要为符号合并到image的QString析构，不能当同数量PageStore owned根。审计槽改16384后回调全执行、溢出0，无效symbol扩容撤回。04为首次零溢出诊断，05/06为最终原trace对照；原日志/source/runner/hash均保留。

paid余量峰值逐次取同时malloc usable−request，未以两个独立峰值相减。96KB余量证明原请求费与usable容量不同，尚未匹配全部owner或建立总硬界。CPU全body约12.9GB峰值含原runtimeStopsAtCapacity填满当前process硬限的filler，不能当8MiB freehand结果、RAM/RSS或全owned峰值。全heap/site累加只是观察结果。

## 冻结及下一责任

主树manager PID20883保持原48tasks/16threads/100000cycles/seed12345，未缩减、未重启。[50:25快照](manager-live-checkpoint-01.json)复核121非派生source/audit、61runtime及当前123冻结输入；1098 PASS前缀没有Totals，实际终点Pending。原调用HEAD61加记录的dirty修复，source对应780；HEAD不能单独命名该运行。此轮未改主树source、库或manager输入，未处理十三UE/宿主退出。

四组差集保持：全owned实际容量/并存硬界/physical free及初次native外部合并；其余fault及read/capture/history/publication/retirement/close、晚fence/caller终点；Qt/OS/TLS/非Darwin实际资格；完整manager阳性终点及十三UE/default abort退出。下一源码责任为原reserve → allocate → retained fee → physical free的实际容量规则，连同arena/slot/direct consumer一次结算，再统一候选合入和派生核验，不新增同义通知或只重复paid探针。M6/M7/M8正式0/3、persistent默认关闭，CP5/CP10归原包。
