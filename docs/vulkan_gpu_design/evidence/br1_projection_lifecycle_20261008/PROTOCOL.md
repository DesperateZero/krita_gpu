# 完整候选统一验收（测量前冻结）

父版本 a918e45e028c426874d9aa13d8080f2d69170d9f；candidate 为本目录 candidate 下冻结的完整工作树及 universal image 库。所有开发失败保留。最终语义先跑双架八组，再做结构审计和机制观察，最后进行无内部插桩测量。构建、诊断和性能批串行，不竞争采样。

- 完整生产差集：原生两步 metadata 输入借用；同步 provider ready 事实一次准备且 retirement 逐物理分配独立；write-set 直接构造 overlay 候选；物理 payload 内嵌 slot 索引；块填充。原 prepare/publish/retry/alias/transfer/ack/untrack/retire consumers 同批迁移。
- 每个未改责任的具体保留理由及替代比较见 PLAN；本包不声称达到 CPU 理论下界或删除全部相对 upstream 维护成本。
- 事前数量预测：每次原生两步序列少一个 shared-control 和一个 vector 分配/归还；每次同步成功操作少一次 ready allocate+complete（每 provider 新增一个常量事实）；每次非空 seal 少一个临时 OverlayChange vector；每个新物理 payload 少一个独立 slot map 节点分配/归还；每次默认 fill 从4096次 memcpy 到13次，字节相同。原代际、copy、提交和读选择数量不应改变。
- 事前时间预测：仅已有独立测价的投影60页fill约0.55ms可作局部规划价，整笔116页fill曾净省1.111ms；新结构项尚无同版本单价，不能把其所属约数毫秒桶全算收益。记录数量、诊断包围成本及总净收益，价格不明项不伪造精确预测。
- 机制：从各自真实源码和对象生成外部诊断库；先验证能力，再按 parent/candidate/candidate/parent 两个块和 upstream 两次，保留事件及嵌套完整性。用于数量和投影归因，非正式时间置信或无插桩价格。仅 outer mode 的投影时间另跑相同有限顺序，避免细粒度 clock 费用污染结论。
- 无内部插桩：沿用已冻结 matched freehand fixture；arm64，seed12345，全部像素哈希、8 segment/4 update callbacks、析构及5阶段检查；两组比较分别 parent/candidate 与 upstream/candidate，每组20个ABBA块（40对80进程）。全部样本保留，projection_updates偏离19单列，不筛选。Stroke、Undo、Redo、Teardown 的 wall/CPU，同时报告绝对差与比值。
- 统计：顺序块为独立单位，block log ratio 均值；20,000 bootstrap、seed261028，pointwise双侧95%区间。局部Stroke改善要求收益区间下界>0；各负控制要求耗时比上界≤1.02，不以跨0当等价。这是本包判断，不代替正式M6 family。
- 受保护Fresh/H4：复用固定M5原协议和源码，各双架K1/K16，40对、20顺序块、250ms，50,000 bootstrap、seed260926，四桶family至少95%，throughput下界≥0.98。
- 停止规则：身份、像素、进程失败即停并保留；真实修复后开新命名批。无剔除、无到通过为止扩样；性能不达标保留未通过结论，必要时回退对应候选，阶段仍0/3。

首次性能采样前修订：candidate原冻结库7000cf8f在安全批复现默认页读与回收竞态，停止验收；最终候选改为candidate-read-fix（3f6248c2）。临时描述符清理归读请求所有，发生在注册pin之后；竞争物化分支若期间被回收则重新选择。开发编译两次类型表达错误保留；dev-read-fix误加载未修复库，INVALID.md明确作废。外部强制真实collector介入的复现：旧路径49通过/1失败，新路径50通过；外部介入不进入产品。最终双架八组共9220通过，源/库身份一致。新修复不另领取性能预算；其成本包括在整包净收益中。
