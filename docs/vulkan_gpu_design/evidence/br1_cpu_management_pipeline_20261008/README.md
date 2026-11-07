# 同步CPU管理协议：重复接受事实的源码证据

产品固定`6644249a4cfd2c48225685a2c27f1a8318def1c3`，文档父`7762c71d1478543e72cc6485dd29b3b21c8e940b`。本包只交付[理想管线与实施矩阵](../../br1_modification_guide/03e_cpu_management_pipeline.md)，产品增删0、新增性能进程0。原候选Undo回退、默认未晋升及M6未通过不变。

主要新证据不是另一次热点计时，而是几处明确的重复工作：

1. `borrowExecution`的非const数组仅作只读遍历却触发COW；backend的行优先序与execution的列优先序又不一致。BoundEntry构造已按规范顺序，随后仍再sort。
2. BoundedCursor线性contains之后，execution对同一成员关系再次二分查询；越界锁存失败可以由后者唯一判定。
3. 唯一reservation生产者只返回成功claimAll的对象，接收端和借用端却再次完整查询/通用接纳；已有execution冷页还重新claimOne。可以沿原ClaimSet生命周期传递事实，但公共新键/重叠/失败分支不能直接跳过。
4. reserve到provider间有无实际受保护消费者的relock/unlock；成功move后的空candidate也执行锁外交接。空descriptor条件清理须保留allocator owner及非空释放证明。
5. seal保持scope gate和session活动，claim不会被外部线程撤销，却跨三个区间反复完整校验。可以保留首次完整校验及真实动态状态复验，删除后两次稳定集合扫描；reader、domain与metadata接受不能随之省略。

## 最小复现

[协议](PLAN.md)先固定只验证容器行为，不计时。`array_probe.cpp`直接包含当前`KisPageSnapshotArray_p.h`，以带copy计数的元素复现生产中的局部数组与range-for；候选使用const遍历/一致排序作表达对照，不修改产品模板。最终实际加载原库SHA256 `2442a100b543448c798e71ddfe6f9eb18625013aabc65f8e1d57f2e6e3aec9de`，退出0、正常reap、无timeout，四案例均通过。

| 案例（四元素） | 规范化后的复制元素数 | 只读遍历后的复制元素数 | 是否detach |
|---|---:|---:|---|
| 当前：已是execution排序 | 0 | 4 | 是 |
| 当前：backend行优先→execution列优先 | 4 | 4 | 是 |
| const遍历已有canonical输入 | 0 | 0 | 否 |
| 一致行优先＋const遍历 | 0 | 0 | 否 |

这证明当前实际模板的隐藏复制，不是单独计时收益，也不是完整borrowExecution/产品安全测试。模板一次detach调用allocate_shared复制Storage，非空vector另分配元素数组，因此每次非空成功borrow有两次可避免请求的源码预测；对应19次投影operation预测少38次，尚待实现后机制核验。

首轮构建成功、四案例输出通过，但runner将DYLD环境放在macOS系统arch程序之前，未获得加载记录，身份断言拒绝。原脚本/runner.log/probe.log保留，不领取该轮验证。`verify_probe.py`改成arch→env→probe，仅重新执行同一二进制，取得加载清单并通过。[result.json](result.json)是有效结果，[runtime.json](runtime.json)是加载哈希。合计两个微探针过程、仅后一个身份核验通过；不是八项产品测试。

## 原数量复算与预测边界

`audit.py`只读取上一冻结组1四个过程，不启动测试。四次均132 cold＝96 operation内＋36 operation外；19 operation和19内部seal，另13外部seal。`work-counts.json`保留原来源哈希。据实际分支及源码可预测：19次冗余数组clone/38分配请求、132对reserve/provider中间锁交接、96次execution冷页claim重入。N/S/M/B/E未取得独立计数，保持符号变量；不把seal数或cold数直接冒充空清理数。

本包没有新毫秒价格或收益百分比。已有局部metadata约0.407ms、operation准备约0.34ms和cold余项约0.568ms都包含必须保留的工作或观察扰动。蓝图逐行区分确定重复、需收紧入口的条件删除、真实并发复验及验证缺口；不能把整个成本桶当净删除预算。

完整源码与调用者快照、编译/运行命令、首次身份失败、有效结果及原数量来源由[清单](manifest.json)和[EVIDENCE](EVIDENCE.json)固定，原始实体在[raw.tar.xz](raw.tar.xz)。本轮未运行完整产品矩阵、未修改API或产品代码；活动文档中的测试名仅是实施时应复用的反例。
