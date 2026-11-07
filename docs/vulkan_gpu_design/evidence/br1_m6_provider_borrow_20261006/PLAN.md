# M6候选冷准备延后与已有provider借用：事前设计

产品起点`79e1c8d1eff509e683c120df25861eb21512fb5f`，文档起点`2614383c1`。上一批已删除已知blocker的accounting/metadata/descriptor准备；本包只领取尚存在的候选冷对象构造、同provider重新查找和引用责任，当前M6完整资格未通过。

| ID | 原位置/consumer与owner | 可达到的表达与删除 | 保留合同 | 事前预测/验收 |
|---|---|---|---|---|
| B1 | prepareWritePlanLocked的局部Prepared；native/generic共同调用 | physical候选继续是原调用栈值；确认非占有physical eligibility后才emplace其余冷Prepared，删除busy路径的无用构造/析构 | physical先reset，再before pin/其余prepared；所有provider访问和重对象销毁在owner gate外；任何异常恢复原gate | 稳定native pin冷Prepared构造K→0；必要physical观察、unlock/relock、Fresh仍有成本 |
| B2 | 原beforeProvider的ledger查询/强引用；native session的d->provider、generic acquireWrite的局部provider已保活 | before的provider id/epoch与传入source provider相同就直接借用参数；不同provider才用原ledger取得强引用 | 参数强引用跨整个调用与cleanup；foreign provider仍保活到before pin释放；最终identity/epoch/revision/claim不删 | hit/native-pin同provider的额外before ledger查找K→0，附加shared retain/release K→0；foreign合格hit仍K次查找 |
| B3 | 原productionRecoverableHandoff测试 | 在原BPP、generic Preserve/Discard与四终结上增加不同provider的独立before | Fresh拒绝时仍能handoff，旧值/undo恢复/取消/close以及两个provider实际payload清零 | 新跨provider边界在父/子均应通过，不能用语义测试冒充时间收益 |
| V1 | 原完整安全、真实安装/存储、结构与工具自测 | 同源有限相关矩阵，保留失败与实际库 | 不放宽限额、断言、owner或ratchet | 当前完整安全/资源/结构通过后才采性能 |
| V2 | 原同义首写fixture与固定M5控制 | 用独立预注册更长有效计时窗口和同进程配对，评估小额增量与新门 | 40独立配对，单侧门/多重比较校正保持；全像素/工作/退出逐样本验证 | 原库父子增量、校准、hit/miss、原Fresh/H4分别裁决；不续采上一批，不追加到通过 |

数量差由实际调用点和另行诊断副本计数验证。未测单价不预报精确μs；上一批native pin同库K16的1.927/4.771μs净差并非全部可删下界。本包删除同寿命内重复查找/保活和无用冷准备，不引入第二owner、持久字段或公共API。正常成功仍须source物理候选、独立before读pin、全部可失败存储、最终physical claim和logical install。

性能协议须在新样本前冻结：每arm至少64ms实际操作计时（setup/校验/close/drain外计）；原库父子与开关校准仍分进程，同库hit/miss可在同一独立进程内交替两arm以控制短时环境变异。循环内样本不算独立重复，停止窗口事前固定，不根据置信区间延长。自然producer、metadata驻留同义分母、CP0完整required、GPU/M7/M8和默认策略资格保持独立开放。
