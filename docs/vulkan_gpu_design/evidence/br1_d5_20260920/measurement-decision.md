# D5 pilot 后的测量分支（rate 配对开始前冻结）

`protocol.json` 与 pilot 原件保留。32 桶 fixture 已在双方通过；pilot 仅使用 upstream 选择固定循环量，
三个 K1 真写桶达到 200 ms 的循环量为 8,388,608，K16 为 1,048,576。

源码复核：`KisCompletionRegistry.cpp` 的每 source `tickets` 为逐 ticket 的 QHash，`allocatePending()` 插入，
`complete()` 修改终态，当前没有逐 ticket 释放/压缩。它随该 source 累计分配增长；此外 provider/owner 的防重放记录
也必须独立审计，不能推断其全都已被 completion 问题解释。尚未实测这些记录的逐项字节及长桶内存峰值。

因此先执行同一 protocol 的 **rate-only 子集**：全部十桶、每桶十二个交替进程 pair、每个进程独立 200 ms 完成量窗口。
它不依赖固定 work loops，保留实际完成数、CPU、RSS；不将吞吐倒数称为 latency，不以不同完成数下 RSS 的比值证明
每操作内存效率。`run.mjs rate` 与 `analyze.mjs` 的版本 hash 随结果保存。

这不是取消固定工作量或修改通过阈值：固定-work 配对、同初始累计状态的伸缩性/有界回收、尾延迟仍缺测，不能给 M/E
不劣性或 BR1-PERF Pass。先取得吞吐差异，再按操作累计量和记录类型建立受资源预算约束的增长实验；不得以更短候选
运行替代相同 work 配对并宣称管理等价，也不为基准删除必要完成校验。

后续候选研究：对**已逐项确认的终态**按连续相同状态压缩，保持 pending gap、Failed/Cancelled、乱序完成、重复 complete
拒绝和 registry/source/value identity；不能从更大 host ticket 已完成推断所有较小 ticket 都完成。需要先补统计与负例，
验证后再做 before/after；本文尚不声称该优化已经实装或具有某一收益。
