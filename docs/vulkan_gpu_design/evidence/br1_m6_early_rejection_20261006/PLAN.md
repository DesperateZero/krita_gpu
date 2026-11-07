# 已知不合格handoff候选提前拒绝：事前设计

产品起点 `f0c40a5d195f1c20a0f915faaef18b1f3ee5b575`，文档起点 `b86bde1cda8de014e3d9d431803f80a7efdac5b5`。本包解决上一轮M6新门的已知blocker晚拒绝，范围止于原metadata、binding和共同准备顺序；不重写容器、不增加owner/字段/API、不改变门槛。

必要工作是保持exact旧值、新输入、Fresh回退、物理排斥、epoch/revision复核及预算/释放责任。可达到的实现只用原锁内已存在的事实拒绝候选；预检不是写权限，晚到reader仍须在最终claim或安装处拒绝。

| ID | 位置/consumer与原owner | 改动及保留 | 预测/验证 | 初始状态 |
|---|---|---|---|---|
| M1 | queryMutationBase，原metadata shard/compact records | authority非Valid、active operation、pin或overflow阻挡时不选alternate；overflow只承载该replica的read lease与pending last-use，captured View在version上独立保留 | 稳定generic lease/last-use的每页完整recoverable准备K→0；不扫描/导出完整版本，不改最终StateMachine | 待实施 |
| M2 | prepareHandoff，原binding mutex | 现有reader或非Idle writer提前拒绝；最终tryClaim原复核不删 | 稳定native pin的账务/metadata/descriptor准备K→0，晚到reader仍安全拒绝 | 待实施 |
| M3 | prepareWritePlanLocked，原局部Prepared与cleanup | 在独立before pin前做非占有的physical prepare；明确失败即回原Fresh；成功仍先pin before，再准备所有可失败存储，最后claim/install | native pin避免额外before读pin和后续准备；保留owner gate外provider访问与清理，未成功claim不retag | 待实施 |
| V1 | 原reference/physical/production fallback/concurrent tests | 原测试补保护建立/释放后重试、已准备候选遇晚到reader、metadata lease→last-use→ack、取消与旧值 | 新行为测试父库应失败、候选通过；双架相关完整安全/资源及结构检查 | 待验证 |
| V2 | 同状态CPU fixture及原固定M5控制 | 固定父/候选原库增量，候选同库hit/miss与独立开关等价校准；全部新样本在协议冻结后运行 | 不将次数减少当时间比例；不把当前16.9～44.7μs差额全部预报可删；不追加样本到通过 | 待验证 |

命中与single路径仍须保留其原输出和局部收益；两份Ready副本的创建成本继续在计时外单列，不用于真实业务默认资格。本次性能前另行冻结样本、统计family和校准设计；既有失败原样保留。metadata驻留≥25%分母、CP0完整required和业务/GPU/M7/M8不由本包自动关闭。
