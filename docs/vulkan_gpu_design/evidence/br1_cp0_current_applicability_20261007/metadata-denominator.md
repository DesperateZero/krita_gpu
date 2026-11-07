# common metadata 25% 的分母审计

本表从当前 `KisPageMetadataCoordinator::footprint()`、`KisPageMetadataFootprint`、arena/index 的真实分配和收费表达核定。检查起点为产品 38834c4e26；本轮仅修改测试，相关生产字节不变。

| 当前观测量 | 覆盖 | 不能做的加法或替代 |
|---|---|---|
| trackedPayloadBytes | 实际存活 page/activity/version/replica/overflow/index 项的类型尺寸和数量 | 属 used payload 表达；不是 allocator resident，也不含全部目录/control/slot 空余 |
| owningCapacityBytes | mapAllocationBytes、两个 flat index 的实际 allocatedBytes，加 shard 对象 sizeof | map/index 已含对应 used 数据；与上项直接相加会重复；shard sizeof 不含实际 shared control/对齐开销 |
| version/replica/overflow allocatedBytes | 实际附着 block 容量，保留 free/quarantine slot、header/alignment；released 单列 | used record 是它的子集；不代表全部目录或门外 prepared candidate 仍拥有的 block |
| arena used/free/reservation/high-water | 原 slot 和候选生命周期事实 | slot 数不是 bytes；reservation 既有逻辑位置也有预算待分配，不能统称额外 resident |
| backing budget 的 Metadata usage | 原真实 allocator/retained 存储的 live/reserved/peak | 包含超出 common record 的 owner/control/其他短寿命对象，且 live/reserved 是不同状态；不是可随意追加到 footprint 的独立项 |

合格实验必须先固定 common record 的唯一物理 allocation 所有者闭包，分别报对象使用、已分配容量中 slack、尚未物理分配的 reservation、峰值和实际 free。prepared/installed/cleanup/晚 handle/owner destroy 的端点分别比较；共享 storage 只计一次，不能靠末端销毁把两侧都归零比较。RSS 另报也不能隔离这个闭包。

本轮检查了当前 footprint 实现、metadata 目录收费/按需增长的活动证据，以及 arena 路径 Git 可见起点：`0db3434678` 已包含 `KisPageMetadataArena_p.h`，其父 `f5fbbde618df6fb4e1068ace7381c339a70dd4c0` 在该路径没有文件。这个事实不能自动指定父提交为一个已完整保存、可同义运行的重构前系统。固定 M5 `5173c807c87b` 也已经有该结构；正式 upstream 无同样的 PageStore representation。没有读取 archive，也不声称穷尽其他外部材料。

因此本轮没有新 25% 数值。下一有效步骤是确定可重建旧实现及其完整 source/dependency/fixture 身份，然后以同一业务状态和上述不重叠 owner 闭包双边实测。只有当前容量或局部目录节省的数字仍不足以结算该门。门的适用分母尚未建立，与是否存在代码瓶颈是两个问题。
