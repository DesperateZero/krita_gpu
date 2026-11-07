# 批量默认填充实施、真实负控制与投影结构边界

本包执行[03d](../../br1_modification_guide/03d_cpu_cost_calibrated_blueprint.md)的A资格和B消费者审查。起点产品 `fb57b8b69be74a38602fb2f0cd1c6e4374b843e3`，外层 `88662bce446ae3ece7078b03652b80237dea542d`；[事前协议及有限修订](PLAN.md)、[算法/生命周期/消费者清单](IMPLEMENTATION.md)和 `delivery-identity.json` 区分父库、fill-only、完整候选和最终保留修复。未读archive，未push。

**结果：填充调用放大是确实存在、可消除的成本，真实stroke收益约6%～8%；它没有关闭upstream主差距，也没有取得真实Undo非劣资格。** 完整候选保存在本地 `codex/br1-bulk-fill-candidate` / `725fe331af259e9fabc18625be547893cad2c1c5`。当前原工作分支只保留pin寿命修复及字节/寿命oracle，最终提交 `a918e45e028c426874d9aa13d8080f2d69170d9f`，第一版修复为 `751bceff23e61ba7ea7312def8f6f4b15936db33`；不把候选收益记到当前默认实现。M6/M7/M8仍0/3，校准2/20，persistent默认关闭。

## 1. 理论删量与实际实现

原 `KisTileData::fillWithPixel` 每64×64页执行4096次动态pixelSize的memcpy。候选在同一独立页内seed一个像素，再做12次不重叠倍增，总字节保持，原分配/预算/失败/释放与copy/rows构造保持。ARM和x86实际候选汇编均展开为12次call和末尾一次memcpy跳转；父库仍是4096次循环。源、库、compile/link记录、反汇编与哈希冻结，不根据源码短小臆测编译效果。

| 层次 | 理论或观察 | 实际裁决 |
|---|---|---|
| 每页调用 | 4096→13，少99.6826% | 源码和两个架构的实际汇编确认 |
| 同量116页stroke | 475136→1508，少473628；1,900,544 B不变 | 同布局详细观察4过程均116页；最终候选一例更新合并，不借用计数冒充该过程 |
| 原CPU预算 | 前包原小调用约1.062～1.127ms，upstream同量整页copy约0.051～0.054ms | 是前包带观察粗价；不是本包各事件的严格净差 |
| 真实同布局净收益 | 预期约1ms CPU量级 | 本包配对CPU节省中位1.111ms，wall0.514ms |
| 完整静态候选 | fill＋必要pin修复 | 配对CPU节省中位1.148ms，wall0.606ms；不把全额归给fill |
| 投影结构B | 条件36链约0.469～0.491ms CPU | 合法删除集合尚未成立，实际B删除0，净收益未授予 |

数量降低不是315倍整笔加速。页仍要初始化，实际只消掉一个约1ms的CPU项。A与B的价格重叠必须扣除，不能将旧fill价和整个冷代际预算相加。

## 2. 无内部观察的有限业务比较

均为同Qt/工具链、ARM、RGBA8、4workers、8输入callback/4更新callback、同像素/undo/redo/析构断言的真实freehand。switch和最终候选各24配对/12 ABBA块；upstream直接比较8配对/4块。20,000次block bootstrap，seed261028，表中为pointwise双侧95%区间，**未做端点family调整，不是正式M6资格**。各批另有双方各一能力过程；不计入估计，不扩样、不裁剪。

正值表示当前比较中的候选时间下降：

| 端点 | 同布局仅fill，下降% [95%区间] | 完整候选对父库，下降% [95%区间] |
|---|---:|---:|
| Stroke wall | 6.30 [4.10, 8.34] | 7.88 [5.87, 9.87] |
| Stroke CPU | 5.53 [3.47, 7.39] | 6.99 [5.04, 9.08] |
| Undo wall | −1.11 [−7.35, 4.69] | 0.01 [−11.30, 12.04] |
| Undo CPU | −1.52 [−6.05, 2.83] | 0.73 [−9.99, 11.92] |
| Redo wall | 31.51 [29.68, 33.04] | 35.18 [32.25, 39.34] |
| Redo CPU | 28.67 [26.67, 30.32] | 32.68 [29.49, 37.02] |
| Teardown wall | 0.31 [−1.95, 2.34] | 1.38 [−2.23, 5.67] |
| Teardown CPU | 0.03 [−2.93, 2.53] | 2.25 [−1.02, 6.32] |

主候选index26为18更新，其余47过程19更新；全部像素/callback/drain断言通过。主结果完整保留。事后移除该过程所在整个ABBA块的11块同更新敏感性：stroke wall下降7.63% [5.54,9.77]、CPU6.89% [4.78,9.21]，仍正向；这是限制解释的补充，不取代主结果或新增通过数。switch48过程全部19更新。

Undo不能凭区间跨0宣布等价。完整候选的配对wall/CPU节省中位分别为−17/−11µs；各侧独立中位分别从0.495→0.526ms、0.6315→0.675ms。不同统计量反映短端点波动，不能只挑几何均值接近0来抹去前包+43µs负信号。Teardown也未取得明确非劣证据。按实施前协议，A不直接升默认实现；不另跑同一批直到区间收窄或方向通过。

## 3. 相对upstream的剩余差距

完整候选直接对固定同依赖upstream：stroke wall时间比 **2.055 [1.928,2.215]**，CPU比 **2.011 [1.911,2.121]**；配对额外wall中位3.885ms、CPU8.803ms。两侧分别用各自真实image/ui及相同common依赖，实际加载哈希有记录，16过程全部19更新。

这是当前候选的独立直接比较，不把前包2.028倍乘本包7.88%得到“实测新比值”，也不据不同批的2.028→2.055断言优化反而退步。upstream样本只有4平衡块，单用例、单架构、离屏业务；不能授完整CP0、GPU或普遍性能结论。

诊断继续指向必要代际维护与多次操作交付，而非纯整页数据搬运。前包projection额外CPU约4.739ms、composite75.6%/clear24.3%，仍是旧诊断分母；本轮fill＋pin候选未重新插桩完整actor账，不能把其CPU收益全部从projection差额里扣掉后伪造新分解。

## 4. Undo判别与安全失败的归因

同一派生二进制的legacy/block开关只在进程初始化读取。4次详细观察均stroke116 fill、redo56 fill、Undo0 fill；选择开关不进入生产。Undo大部分调用数相同，`tile_release_memory`为16/16/15/16；一个block过程有292ns释放事件处于Undo marker内、采样end时间之外，原样记录，不宣称所有事件均包含在阶段时钟内。主要独占CPU差额仅微秒级，尚不能给旧43µs一个确定机制原因。

stroke canonical commit数12/13/15/14，反映anonymous client终结分组变化；全部19更新，但不是每个内部事件同量。父子event唯一身份、阶段标签、包含关系及self+children=inclusive已核对。详细观察有扰动，只用于职责与数量；不将小段wall当锁等待或各inclusive相加。

首个fill-only候选完整安全批在ARM low-memory的memcpy比较路径发生SIGSEGV，已保留实际−11/回收、加载身份与OS栈。父库一次相同压力通过、LLDB候选一次通过，都不能说明缺陷不存在。新确定性反例在**父库和fill-only候选均失败**：未暴露writer先解锁，reader最后解锁后，旧pin拥有标记残留；下一轮write错误归还活reader pin，实际 `trySwapTileData(before)` 成功。原Tile最后native解锁统一结束pin与标记后，两架目标组各8/0/0；这是独立的正确性修复，不是fill收益。

完整候选8组×两架均通过，各架：TileDataStore27、TiledDataManager1320、CPU mutation1594、Reference946、Painter708、low-memory4、pooler3、swapped store8，共4610/0/0。首次字节oracle排在旧clock iterator前，在父库触发其排序断言并遗留锁；识别PID42500后SIGTERM/−15回收，失败源slot顺序及日志保留。oracle移到原slot之后，父库双架各27/0/0；不把这个夹具顺序问题当产品回归或删去失败。

## 5. 原保护控制、结构与实际复杂度

完整候选Fresh和H4各320过程：两架K1/K16、40配对/20块、250ms、loops4，固定同依赖M5。单侧98.75%每桶、四桶family至少95%、吞吐下界≥0.98。Fresh四下界1.2968/1.0708/1.3302/1.1306，H4为1.4829/1.3966/1.4172/1.4616，八桶通过；不可据此替代Undo或授M6。

完整填充候选生产两文件+11/−14，测试四文件+97/−0。第一版保留修复生产一文件+3/−10，独立8配对却测到stroke wall增加4.12% [2.26,6.28]、CPU4.92% [3.79,6.06]，配对多0.422/0.846ms；原保护八桶仍通过。不能用安全或M5控制通过掩盖真实业务代价。

最终原函数改为明确持锁的 `unblockSwappingLocked`，四个caller全部迁移，删除先解锁再取同一barrier的重复工作。正常read/write复用已有锁域，两个legacy COW失败显式持锁清理；原pin/旧backing/标记仍在同一终点，未恢复重复writer分支。相对本包父提交，最终生产两文件+12/−17，测试四文件+97/−0；公共/保护API新增0，私有签名一增一删、净0，字段/owner/锁实例/TLS/队列新增0。源码证实避免了重复锁工作，但第一版全部回退不能未经因果隔离就归给锁。

候选结构检查：原ratchet保持，21manifest、25ownership facts、16census groups、2211indexed APIs、29025edges、19主干侵入文件，6工具自测通过。派生图只存证据，不更新原阈值或借行数授性能资格。B的真实中间读者、失败/发布边界及需要的所有consumer详见IMPLEMENTATION，当前没有跨层wrapper或生产B补丁。

最终single-lock-fix独立8配对/4块对父库：stroke wall下降−0.93% [−6.97,3.85]、CPU下降−1.51% [−6.47,2.53]，**未确认收益，也未证明业务非劣**。主样本index6为18更新，原样保留；去掉整个ABBA块的事后3块敏感性分别−3.01% [−10.38,2.64]、−3.27% [−9.26,1.47]，仍不确定。不能将第一版的显著回退变成“已证明全部消除”；源码删除重复锁工作和端到端时间是两种证据。

最终同源16安全过程再次各架4610/0/0、结构/6自测通过。最终Fresh四下界1.3299/1.0940/1.3784/1.1311，H4为1.5065/1.4065/1.4566/1.4757，按原规则八桶通过；第一版控制和候选控制另列、不能相加成正式M6资格。当前保留该实现的理由是父库确定性反例证明的必要安全保证及唯一终结，**不以它领取性能优化收益**。本有限包在预定批结束，不继续采样到区间通过。

## 6. 复算与交付边界

`analyze.py switch|candidate|upstream`复算三个原批次，`analyze_sensitivity.py`复算事后同更新敏感性；`analyze_retained.py`、`analyze_single.py`分别复算两版pin修复。`analyze_controls.py --round fixed-m5-fresh --output <新文件>`及其他round复算原保护。源/库分为parent、candidate（fill-only）、fixed-candidate（fill＋第一版pin）、retained-fix（原fill＋第一版pin）、single-lock-fix（最终原fill＋单锁域终结）；不得用当前build库重放旧候选而沿用旧哈希。

本轮取得的是实际算法候选、确定性安全修复和有限收益证据。填充的数量及正向stroke效应置信较高；真实Undo非劣、B合法净删量和upstream总出口仍缺证据。后续A资格应先固定真实Undo的接受界、隔离方法和统计分辨率，再登记独立有限协议；B先闭合中间读选择/全量准备/失败/joint publication及新增价格。不重复已完成的132代际来源计数，不再按copy次数挑小点。

`freeze_evidence.py`核对160业务过程：两个测量过程18更新，另一个upstream能力过程20更新，全部保留；能力过程不进入估计。freeze-v0漏列该能力例外而停止，修正清单并保留脚本/错误，不换样。另核对三版各16安全过程、六个320过程保护批和全部失败身份；源、库、命令、原始日志及派生统计冻结至`raw-evidence.tar.xz`，逐成员哈希与回读在`MANIFEST.json`。可重建`.o`不入tar。首次错误测试slot顺序的可执行文件、增加pin反例前的旧manager可执行文件已被后续构建覆盖，未伪称保有；原命令/哈希/失败header/Git源保留，确定性反例所用同一manager二进制及最终安全二进制已另存。前包fixture与依赖由prerequisites中的原manifest/哈希指向，不改旧冻结包。
