# CP3 工作值与稀疏 epoch 批量构造（2026-10-05）

产品 `6d439e0437c86b5214064eef5bc5134f2160cf43`，父 `822456732bd02a13d128b855ed9856415544ec00`，文档父 `98b688d3b655e432bea385185c7a5a6d503c79b2`。本批结算原共同工作存储及 sparse root 构造，**完整 CP3/M6 未通过，M6/M7/M8 仍0/3，persistent 默认关闭**。[领取](start-review.json)、[提交前审查](checkpoint-review.json)、[交付](delivery.json)及[最终身份](final-verification.json)绑定组合后的同一源码。

原 working versions/replicas 和 removal witness 使用常见 inline capacity；保护数组继续动态增长、受原硬预算约束。inline 字节计入原堆 carrier 的实际 paid capacity；spill 继续收费。初始三版本 compaction 的真实 UAF 经 GuardMalloc/LLDB 定位：moved-from allocator 被复用后丢失收费 owner，随后按 retained allocator 释放而多减引用。原 allocator copy 操作保留原关联，没有添加字段/owner/队列。中间源、失败和修复保留在[前一候选](../br1_cp3_working_inline_20261005/README.md)。

prepareCommit 原 sparse per-key insert/remove 改为共同消费已接受的 sorted/disjoint changes/removals。每个受影响共享路径一次构造，未变子树共享；AVL join 对批量增删造成的任意高度差沿高侧合并，再用原 balance 保持平衡。旧 insertPageRoot/removePageRoot/minimumPageRoot 全部删除，唯一外部 consumer 同批迁移；原 dense threshold/build、冲突/revision guard、paid node/control、取消及冷回收 owner 保持。生产+76/-51净+25，测试+129/-0，无新字段/owner/队列/公开API。新增独立 flat oracle 的四行各96步覆盖集中/左右边界/分散改动、mixed insert/remove/replace、点查询、manifest/extent、树高及旧根不变性。

完整原38同源进程 **10818/0/0**，实际0/reaped。Reference 每架794，正确 ReadBaseline 每架45，selected persistent business 每架11，VulkanFoundationContracts每架14。每架31080 handoff、28 publication安装alloc/VM/bytes/free0与24实际allocator边界通过。新增真实 batch fault 每架覆盖 **359** 个分配拒绝点：费用回到基线、reserved为0、原根和事务保持、重试通过、安装alloc/free0、最终parent live/reserved0。结构为87TU/2187 APIs/28499 edges/27 callbacks，21 manifest/25 ownership/16 census/19 intrusion，原ratchet相等，六工具通过。

三个 scope 各四桶、完整40对，合计960实际正常退出进程；先完成所有build/safety/control，再冻结同源码顺序运行，无并行build/benchmark，不截尾或扩样。Fresh/H4为20预定 order-balanced blocks、50000 bootstrap/seed260926；handoff为20000 paired bootstrap/seed12345。下表为单侧98.75%下界，门限未改。

| scope / bucket | arm64 K1 | arm64 K16 | x86 K1 | x86 K16 |
|---|---:|---:|---:|---:|
| Fresh current÷M5 点估计 | 0.9337 | 0.7181 | 0.9697 | 0.7326 |
| Fresh 下界，需≥0.98 | 0.9182 | 0.7058 | 0.9452 | 0.7275 |
| H4 current÷M5 点估计 | 1.2043 | 0.9672 | 1.0598 | 0.9952 |
| H4 下界，需≥0.98 | **1.1874** | 0.9483 | **1.0368** | **0.9827** |
| handoff 延迟降幅点估计 | 2.46% | 8.10% | 2.35% | 8.45% |
| handoff 下界，K1需20%/K16需30% | 2.04% | 7.35% | 0.97% | 7.44% |

H4三桶通过，其中x86 K16本轮过门；三scope整族均未通过。Fresh K16本轮仍低于M5约27–28%，不得把不同轮绝对速度相减当因果收益。各实际结果见[Fresh](fixed-m5-fresh-summary.json)、[history](fixed-m5-history-summary.json)、[handoff](latency-summary.json)。[16进程128样本分配](working-allocation-summary.json)只证明原 working array 的请求减少；N=K走原dense tree，不能据此声称 sparse batch 因果速度或metadata同义驻留≥25%。

失败全部保留。[执行问题](execution-issues.json)记录中间read误选、profile parser、oracle初始未推进semantic-default generation、private probe访问及patch格式拒绝；修正后另开完整scope。旧候选的960进程因required read前置晚补只作诊断，不与本轮拼接。第一个继承profile只采到dyld/init，保留且不用于热点裁决；后继等待实际init marker的[steady采样](public-fresh-steady-profile/localization.json)在原fixture真实计时loop捕获2535 main samples：metadata applyProjectedSequence contextual524、preparePublication191，epoch prepareCommit37。它是重叠inclusive定位，不能相加或当因果收益。下一审私有 working value 从shared policy到全部真实consumer的按值移动/重复转交、拒绝和安装；不盲合native已合并序列、generic异步或private/canonical边界。

common metadata重构前used/reserved/slack同义驻留≥25%分母、CP0完整required及正式样本继续开放；CP1/CP2不重领，CP4/M7仍等M6正式资格。没有可靠实际人日，§17低置信规划不从请求/节点/行数扣预算。原始日志保留在[压缩附件](raw-logs.tar.gz)，逐member核对的[SHA清单](raw-log-manifest.json)绑定全部原始字节；构建二进制/对象/图片不入库，没有推送或更新外层krita gitlink。
