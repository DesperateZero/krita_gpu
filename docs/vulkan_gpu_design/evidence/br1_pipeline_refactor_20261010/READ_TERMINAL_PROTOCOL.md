# T07 读终结与退休交接的删除闭包

起点为产品 `6f76902d4a`。本轮属于原 PIPELINE_PLAN 的 T07.2/T07.3/T08，不增加追踪矩阵。前轮 Setup/H0 的12个观察过程独立封存，不混入本轮验证或性能估计。

## 接受点与目标

读保护解除成功时，metadata 已给出是否需要重访历史；原 collector 的 requestKey 已无条件承接通知（实际节点或缺 key 重扫）。读记录不应再拥有 GC 完成责任。普通 cancel、lease release、last-use ack、captured release 均在各自最后一个语义接受点撤出原活动容器，再由原 cleanup/原 captured 记录保活锁外销毁。GC 和物理 retirement 的拒绝分别留在原 owner；不增加队列、阶段或账本。

先验证 `retainRetirementDebtReservation → provider.backingFootprint` 的分配异常。该虚拟接口没有 noexcept 合同；实际 tiles3 查询当前不分配，本轮注入证明接口接续责任，不声称已观察到 tiles3 的真实 OOM。若异常可逃逸，优先在原 debt 准入边界转为拒绝，保持原 reservation/record，复用已有重试。不会扩大到吞掉任意异常或重放已接受的 provider retire。

## 有限替换和保留

- pending cancel：原 Released/Collecting → 接受后立即提取原 map node；保留 Pending/Resolving/Cancelling 和真实 metadata 拒绝重试。
- active read：historyPending/historyProcessing、m_pendingHistoryReads、finishHistoryReadLocked 的恢复树 → 原 cleanup 接收 node 后推进原 GC；worker/manual/release/close 全迁移。真实 last-use/metadata release 和 provider access 继续保留。
- captured release：versionReleased/snapshotReleased/historyPending → 已接受 prefix `next` 与原 snapshot 接受点；先推进 prefix，最终提取原记录。`processing` 仍排除逐版本 pump 解锁时的重入，不能仅因同名字段就删除。
- collector 的 rescan/repeat、退休队列的 debt/accepted operation/retry 和最后资源释放保持；晚通知只表达继续处理原记录。

退出需核对全部 consumer 和真实失败源。源码审查不足以证明 pump 不抛出；先复现边界，再实现删除。若新的反例推翻目标，保留原样本并修改此处理由，不另建恢复模型。

## 验证与预测

先在未改生产代码的父版本运行 footprint 拒绝反例，安全清理后报告失败；再验证队列初次交接、原 node 的重复尝试、自动/显式推进及最终债务释放。复用 hard-full MetadataArena、captured 中途停止/恢复、GPU last-use、共享 ticket、并发 read/close 等现有真实边界测试。新增反例针对解锁重入：通知已交接的记录不得继续使 admission/restore Busy，也不得重复解除保护。

最终构建六个产品测试目标，ARM64/x86_64 各运行一遍；每过程600秒 timeout/kill/reap，绑定完整 diff、测试和真实加载库，不并发构建或改源码。失败全部保留；修复后新批次，不追加旧性能样本。随后运行架构/调用图与工具测试，并核对旧符号删除和33项索引。

本轮可预测的是上述阶段/分支删除，必要历史扫描、像素复制和物理退休次数不减少；未建立可靠时间预算，**不预报毫秒收益，不授性能排名或M6资格**。这是原责任收敛和失败接续修复。上一轮性能区间及两个 live-copy exact-view 失败继续保持，通用优化不计为 PageStore 相对 upstream 的基础优势。
