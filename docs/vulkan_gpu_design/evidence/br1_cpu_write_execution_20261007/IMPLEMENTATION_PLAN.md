# 实施前核定与删除映射

四个固定前置过程均成功，普通/opt-in/opt-in/普通各一笔：像素/undo/redo相同、19次projection更新、每笔node 27个fixed multi-dab operation。每笔ΣP=76、ΣR=2344、ΣF=5363、ΣC=76，Σ(C+R)=2420与原计数一致。诊断存储无overflow；所有node operation成功且无selection。故本用例可核定目标body 2344→76、总pin2420→152，删除2268对；必要让出E仍须资源/进度验证，目标代际76、copy20、init56不变。各operation最大F=516，计划规模是单operation而非整笔5363。

| 责任/原owner | 目标表达与同批删除 | 具体边界 |
|---|---|---|
| painter fixed multi-dab | 借用原dab列表，构建矩形+sourceOrdinal输入；适用路径删除filtered devices副本及opaque dab-major body | 首版只接经实际factory类型验证的RGBA8 OVER；其它op、selection、wrap保持原顺序，不能仅凭op字符串重排 |
| PaintDevice strategy与原transaction | 一条私有ordered pixel桥；原映射、目标/owner校验及失败终点共用原实现 | 映射后的有序矩形同步借用；public/protected方法净增长0，不传PageStore/budget类型到上层 |
| manager原operation | generic与ordered共用coverage、legacy intent、adapter prepare/install；QRegion互斥页直接形成canonical SnapshotArray | 同批删除QSet/values；extent和必要missing wrapper保留 |
| backend原共同执行 | private canonical入口；首字节前以原store allocator完成片段计划，稳定计数/前缀和/填充；R=P不建片段buffer | 原range借用后，在原prepareAdapter hook内完成计划，再做全部冷准备；拒绝走原execution.finish且不进入像素body，保住此前pending工作 |
| PageStore原execution | public任意输入只在边界规范化，内部canonical const借用并绑定原entry | 删除共享数组detach、内部二次规范化和已按同序绑定后的BoundEntry重排；原admission/rollback/touched保留 |
| cursor | 原BoundEntry唯一范围验证，单guard按页连续消费 | 删除targets.contains和第二targets引用；越界首次失败仍poison，原不适用callback继续执行原序 |
| provider/adapter/job/scheduler | 保留真实cold、版本/读者/资源/释放、更新和owner | 不改provider/ledger/completion、patch/job/cut、默认persistent；无新增队列/锁/TLS/长期字段 |

03c B2的最窄桥需经过已有transaction的目标校验：因此KisTransaction/KisTransactionData各增加一个**私有**ordered转接，并让原generic与新ordered共用同一个校验/执行实现。它们不成为第二owner，不新增公共overload；直接绕过transaction调用manager会丢失原saved target/mapping复验，不采用。该闭包更新B2/B3清单，不能因蓝图原文件列表未列transaction而绕过校验。

实际factory判定留在原pigment factory内：私有query比较真实scalar/SIMD OVER32动态类型，未知第三方同id op仍走原路径；不在image引入SIMD实现头、在每operation创建临时composite、保存全局类型cache或改变KoCompositeOp对象布局。

计划只持矩形/sourceOrdinal和短期分组位置，无权限/commit/cancel；真实容量由原store allocator收费到释放。完整B1–B8及调用迁移在一个实现包中完成，再跑PLAN的固定验证；仅改sort/const不领取完成。时间敏感度沿03c，2268对已核定但独占单价与关键路径仍未知，不预报保证收益。

实现位置复核修正：初稿表格写了“借用/像素前”，实际使用原prepareAdapter hook，位于range借用后、冷准备及任何像素前。不能在borrowed/unsupported兼容路径先付分组成本，也不能绕过已有hook的异常终点；该位置满足03c首字节前完整准备，拒绝由同一execution正常finish释放本次临时范围，保留此前owner pending。新增真实容量拒绝与第二冷页压力测试验证这一点。
