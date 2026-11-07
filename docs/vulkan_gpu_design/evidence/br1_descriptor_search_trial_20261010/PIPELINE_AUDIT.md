# 前台事实交接审查与候选边界

本表检查当前c13c442493生产实现；是候选判别的代码索引，不是已获净预算的实施蓝图。理想表达必须先区别事实单位，再讨论能否少一次查找、锁或对象。当前4.043ms责任粗价不能重复分给下列各项。

| 事实与实际位置 | 当前生产/消费者/变化窗口 | 可构造方向及本轮结论 |
|---|---|---|
| 写入base、代际、descriptor：[prepareWriteBaseLocked](../../../../krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2668) | 原root/overlay与metadata选择exact base；sealed优先；默认页可在provider解锁期间被reader物化 | 不能把“已持写claim”理解为所有reader事实不变。原preparePrivateWrite会重取实际默认authority，保留此窗口；不再次优化已定价的小base入口 |
| 物理目标及原准备：[beginWriteImpl](../../../../krita/libs/image/pagestore/KisPageStore.cpp:2019) | budget/retirement先接纳，provider返回目标，registerBacking接受物理费用；binding独立控制write/read/swap | 原一次锁外准备已合并；不能再领取旧空锁删除。provider返回可能无效、binding可撤销，不能以“同步”跳过身份/终态核验 |
| 驻留及归费：[registerBacking](../../../../krita/libs/image/pagestore/KisPageOwnerLedger.cpp:968)、[reserved writer](../../../../krita/libs/image/pagestore/KisCpuResidentBinding.cpp:287) | domain注册及CPU swap使物理状态可变；reservation与pin是不同权限 | 同一allocation身份不等于驻留不变。合并接纳需要交付真实稳定能力，不能简单删除第二次footprint观察或pin |
| 布局值共享：[prepareDescriptorLocked](../../../../krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1706)、[prepareDescriptorAdditionsLocked](../../../../krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1734) | 有base hint先复用；否则全索引/候选节点查相等值；每个版本安装自己的索引节点 | 原结构含线性后备，但本次208个Stroke hint全命中，修订过程110–114次后备比较均首项命中，额外遍历0；共享搜索不准入本端点主优化 |
| 版本到布局的映射：[descriptorLocked](../../../../krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1722)、[install/remove](../../../../krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:1716) | 冷页、泛型读写、seal、commit、历史/default restore和延迟清理都消费具体版本的布局；局部Page借用原值指针 | 新建布局值数量不等于版本映射数量。将映射并入原metadata版本记录是待论证替代，需覆盖旧default/layout revision、raw pointer寿命、失败前置和最终收费；不能仅以“值相同”删掉版本映射 |
| 成功completion：[verifyTerminalProviderResult](../../../../krita/libs/image/pagestore/KisPageOwnerLedger.cpp:1958)、[seal/validate](../../../../krita/libs/image/pagestore/KisPageOwnerLedger.cpp:2129) | completion终态不可重写，原registry owner保持存在；provider/metadata状态则可以在后续阶段变化 | 已验证终态可作为原责任里的复用候选，但不是全部proof验证都可省。旧proof完整入口粗价已小，不能因存在重复查询就命名头部责任 |
| proof身份：[seal/validate/revoke](../../../../krita/libs/image/pagestore/KisPageOwnerLedger.cpp:2129) | 同一版本可多次签发不同stamp，并单独撤销；消费者须验证原owner的具体proof与当前metadata/provider | 不能将每个版本简化成一个sealed bool或一个最新stamp；[原测试](../../../../krita/libs/image/tests/KisPageStoreReferenceTest.cpp:10435)明确同时持有两个proof，撤销一个后另一个仍有效。这里的基数是独立capability，不是唯一版本数 |
| operation范围和执行：[runCpuMutationOperation](../../../../krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2063)、[prepareWrites](../../../../krita/libs/image/pagestore/KisPageStore.cpp:1530) | reservation/session/execution分别承载接纳、结构寿命与worker借用；未触碰的预备页需要原路径取消 | 不能用“最终写了同样像素”删预备/回滚保证。仍是未充分定价的较大责任，尚未证明存在值得实施的完整替代 |

本轮从这些竞争解释中选择成本最低的R08命中判别，因为它能排除一个仍被文档标为开放的明显复杂度候选。它没有取得“最可能追回最多CPU”的排名资格；两种选择理由须分别记录。

下一轮仍比较前台事实交接与operation/read-merge的合法净预算，不默认把版本索引节点升为榜首。若要研究descriptor全寿命，须另列包括旧布局、独立版本映射、真实释放和接纳拒绝的模型；搜索本体的结论不能外推为整条descriptor责任零成本。已测小项、此次R08搜索及旧空history不续采。
