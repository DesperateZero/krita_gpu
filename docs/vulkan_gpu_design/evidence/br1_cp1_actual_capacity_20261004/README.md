# CP1 共同分配容量与最后释放：有限交付

产品 `6ddccc30979ab859060ed5a19b936d5322aaa1cb`，父 `7804582f93bb1eb841b7520728169f0e228b046c`；文档父 `7285fe4fc924257409e627c4aadf1fec4d339499`。当前裁决仅由[92 §16.87](../../92_br1_m6_m8_execution_baseline.md#cp1-actual-capacity-delivery)维护。主树源已提交，原主构建库未覆盖；所有最终运行明确加载隔离的build-08或tsan-build-05。隔离源HEAD384加记录的diff与主树提交127个源码/头blob逐一相同，见[source freeze](source-freeze-final.json)和[完整审阅diff](product-review-final.patch)。

## 原责任及真实反例

原process/Mutation allocator、retained owner、slots、arena、readiness、metadata map/index和默认buffer共同预留完整capacity，并保留费用至最后physical free。调用内Prepared从普通堆转原栈上optional；原unlock/reset/relock与失败责任保持。默认buffer的byteSize保持逻辑stride×height，allocationBytes只负责真实费用/cache/free；3 BPP原读合同保持12,288B，native容量16,384B。

`malloc_good_size`不能决定large cache复用容量：16MiB块释放后，16MiB−32KiB的请求仍得到16MiB，旧库少收费32KiB；memalign亦有992B计划得到1,024B的反例。最终Darwin将普通小对象留在native size class，小型超对齐对象在普通分配内保存base/capacity；完整raw容量超过64KiB时按页预付映射，保留对应最后unmap事实。没有第二owner、收费表、锁、队列或上层API，原16KiB任务和8/24MiB业务预算没有提高。非Darwin的request/prefix fallback仍欠实际usable/native资格。

## 最终同源结果

| 资格范围 | 实际结果 | 身份/原日志 |
|---|---|---|
| 七个原完整normal body×arm64/x86_64 | 5,908/0/0，14 actual0/reaped | [normal及业务汇总](native-normal-business-final.json)，各native-final-02目录 |
| 原8MiB两取消行、24MiB真实压力，双架 | 14/0/0，4 actual0/reaped | 同上，各freehand-native-final-02目录 |
| 七个完整body，匹配插桩QtCore TSAN | 2,954/0/0，7 actual0/reaped，无TSAN报告 | [TSAN汇总](native-tsan-final.json)，各native-final-tsan-02目录 |
| 独立heap usable及malloc/mmap/free API span | 双架各72次，created/freed均72，live及预付违例0，process回到332B | [物理span观察及旧库反例](physical-capacity-final-02/results.json) |
| 原780完整manager的同次Pending | 1,105/0/0，actual0/reaped，4,221.39s | [源码/终点裁决](manager-terminal-adjudication.json)、[原运行结果](../br1_cp1_static_root_20261004/qt-manager-full-02/results.json) |

最终完整body没有heap interposer、退出guard、TSAN suppression、工作量缩减或重启；原seed12345与原QTest完整body保持。独立物理span探针有自身固定观察表，仅证明所测的API请求/释放span与heap usable及预付关系，不证明OS合并region、驻留页/RSS、Qt/TLS或全owned总硬界。旧build-06同探针actual3/reaped，少收费反例被真实捕获。

normal/TSAN各40 TU完整重编底座之后，最后仅WriteCoordinator.cpp再次变化，经依赖核对重编1、39按哈希复用；原20 test/support TU无需再编，全部七body重链接，Freehand原三TU另重编。每轮builder、commands、输入/输出hash及源快照保留。主树Clang图87 TUs/2172 APIs/27405 edges/27 callbacks；[结构门](main-architecture-03.log)和[六工具自测](tool-self-tests-01.log)通过，21 manifest/25 ownership/16 census/19-file ratchet保持。

生产九文件+270/−95、净+175；测试六文件+360/−206、净+154；两派生JSON单列。容量/失败/释放保证成本不计整体内存或性能收益，旧约12.9GB测试filler峰值也不解释为8MiB业务或RSS。

## 失败保留与可复验边界

[失败及诊断目录索引](failed-and-diagnostic-rounds.json)记录27个运行轮；构建、身份、超时及全部原日志也保留。早期普通CPP prefix候选的8MiB业务终点失败、错误120s TSAN deadline、未迁移的四个压力deallocate导致invalid free、遗漏PhysicalClaim filler，以及native大块复用失败都不计最终资格。全映射候选因4KiB align128任务占满16KiB而拒绝，最终小型超对齐size class策略修复该真实原预算反例。

单独processStorage方法的cold runtime尾量与完整body既有暖态前提不同；最终原完整body通过，不改原末尾断言。错误方法名/数据tag保留。throw观察器出现递归、LLDB轮未加载候选，均只作无效诊断，不作为产品缺陷证据。退出guard仅避免诊断异常再次进入已观察的宿主abort停滞，所有带guard的阳性都不计验收。

原日志、每轮源快照与命令同时保存在[evidence bundle](evidence-bundle.tar.gz)；[bundle manifest](evidence-bundle-manifest.json)将原相对路径映射到内容hash。大体量重复Ninja依赖/源码按内容去重压缩，原工作区文件保留；bundle不包含二进制/dSYM，不改原hash或删失败样本。最终资格目录和核心汇总另外作为普通文件提交便于查看。

## 完整CP1剩余四组

1. 其余未归类owned/Qt/control/native/TLS/static，独立reserved/live/并存peak/physical free总账与硬界，初次native外部region合并。344个旧arm未归类site仍须实际归属；框架标志不授ownership。
2. 其余真实node/control/task拒绝，与read/capture/history/publication/retirement/close、晚fence/caller transaction共同终点；有限sweep与本次数组收费不代替联合最后出口。
3. Qt/OS/usable/TLS、非Darwin对应容量实现及实际运行。当前没有取得非Darwin宿主资格。
4. 新容量源码的完整manager跨模块资格，以及[20 UE只读检查](host-ue-20-checkpoint/ps.log)所示宿主默认abort出口。原780完整manager已取得实际终点，其Pending不重领，也不迁移为新源码资格；未杀宿主或重启环境。

本包冻结结束；完整CP1仍开放，M6/M7/M8正式0/3，persistent默认关闭。CP5 continuation/fairness、CP10正式性能归原包。
