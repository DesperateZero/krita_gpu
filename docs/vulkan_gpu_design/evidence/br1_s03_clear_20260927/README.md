# BR1 clear / 存活 iterator 修复证据（2026-09-27）

本目录记录 S03/S04 的前置生命周期修复及累计工作树 CPU 正确性。阶段状态只在 [92 §15](../../92_br1_m6_m8_execution_baseline.md:475) 维护；本批不授予 M6/M7/M8、Vulkan、TSAN、install allocator 或 BR1-PERF 资格。

## 最终运行与身份

最终证据为 [checks-03 清单](checks-03/manifest.json)、[身份](checks-03/identity.json) 与 [结果摘要](result-summary.json)。源码是 `5173c807c87bb1619325249a07a8b4f4f8f09f09` 加 [完整累计补丁](checks-03/source.patch)，SHA-256：`c3fbe408e5fcb1af8898b54a265c6ee84dc4e2970c77d39d1ccb6af4dda6b013`。没有创建新提交。构建参数、seed、环境、image/UI 库和 17 个测试二进制的哈希保存在身份文件中。

| 架构 | 测试进程 | Passed | Failed | Skipped |
|---|---:|---:|---:|---:|
| arm64 | 17 | 1,687 | 0 | 0 |
| x86_64 | 17 | 1,687 | 0 | 0 |
| 合计 | 34 | 3,374 | 0 | 0 |

[驱动日志](checks-03-driver.log) 包含全部进程出口；最终 build dry-run 为 no work，源码前后相同。结构门与 6 项工具自测通过；调用图为 1,479 APIs / 13,883 edges，21 manifest、21 ownership facts、16 census groups、19 external intrusion files。刷新记录为 [graph-03](callgraph-generation-03.log) 和 [checkpoint-04](source-checkpoint-refresh-04.log)。

## 本批修改与验证关系

逐函数关系见 [01b 的 clear 边界](../../br1_modification_guide/01b_pixel_failure_boundaries.md)。[增量审阅补丁](clear-implementation.patch) 只包含相对上一批的 7 个实现/测试/所有权文件，来源哈希见 [incremental-review](incremental-review.json)；复现完整源码应使用上面的累计补丁。

- 原 batch owner 在 clear 前预检本线程 iterator；foreign batch、终结中的槽和 native batch 不被强行取消。intrusive links 仅追踪存活 lease，由局部 gate 协调晚解锁，不复制 page write set。
- 冷路径只尝试取得额外 resident pin，成功后保留 backing 引用，再释放 native guard 和取消 mutation。旧 raw pointer 存储到原 lease 归还前保持有效，迟到写入不发布；新 batch 可以在旧 iterator 析构前开始。
- 旧 scope 再取新页返回空指针；晚 scope finish 不清理新线程槽。history 保留 G0；已排序的 clear 继续通过正常 semantic removal 发布。
- 原 `kis_iterators_ng_test` H/V/random clear→offset 调用顺序未修改，两架构均 11 passed。新 manager 用例覆盖 24 组 H/V/random × BPP × history，多 iterator、旧 exact View、undo/redo、旧指针晚写、scope 交错及外来 batch 拒绝。
- swap 的反向验证确认：clear 后原 raw pointer 存活时不能 swap，原 iterator 解锁后允许 swap。bare lease 用例没有 Tile wrapper 保活，验证独立引用不能省略。最终定向运行见 [clear-dev-03](clear-dev-03.log)，31 passed；它与完整矩阵重叠，不重复加进总数。

[ratchet 检查](ratchet-check.json) 确认相对上一累计批次的原始计数、tile fields、backend duplicate-state 不变，HEAD 的 reviewed ceilings 未提高。所有权清单只补充原 owner 内部的取消和存储保活职责，没有放宽单一 writer 规则。

## 保留的开发记录

上一批 [像素故障证据](../br1_s01_pixel_20260927/README.md) 的 3,312 passed / 6 failed 保留，不替换或删掉失败样本。本批修复对应这六个架构/用例组合。

[checks-01](checks-01/manifest.json) 先以阻塞式保活 pin 的版本取得 3,374 passed；之后收紧为 nonblocking resident pin，因此不能用 checks-01 冒充最终源码。初始 build-01 至 build-05、iterators-dev-01、manager-dev-01、clear-dev-01/02/03 均保留为开发日志。

[checks-02](checks-02/manifest.json) 在结构门停止：所有权描述把同一 compatibility group 的内部 batch 控制块另列为第二个 current writer，违反“canonical fact exactly one current writer”。修正清单后，checkpoint-03 又因旧调用图的 state-ownership 输入哈希失效而拒绝；没有跳过门禁。graph-03 / checkpoint-04 重新绑定最终源码，checks-03 完整通过。失败详情见 [checks-02 architecture](checks-02/architecture.log)、[checkpoint-02](source-checkpoint-refresh-02.log)、[checkpoint-03](source-checkpoint-refresh-03.log)。

## 适用范围与剩余项

本批是外部已排序的 legacy clear，不是任意并发 clear 或完整 stroke checkpoint。独立 raw Tile/history lease 的 barrier 登记范围、全部 raw iterator caller 的失败消费、interstroke/indirect 多设备终结、永久资源拒绝及局部退休债务上限仍按 S01/S02/S04/S10 继续处理。

没有延长生产跨 dab pending 生命周期，也没有新增 M6/M7 handoff。局部 mutex / cache 准入检查的实际 stroke 成本尚未取得产品 replay、P95/P99 或正式性能证据；不得以正确性测试或 intrusive links 无额外容器节点推断性能改善。M6 的 cache generation 复验前提补入 [S06 指南](../../br1_modification_guide/03_write_plans_and_hot_path.md:5)。

代码链接随最终源码更新，两个映射日志为 [第一次](source-anchor-remap.json) / [最终审查后](source-anchor-remap-02.json)。最终链接检查见 [document-links](document-links.json)。
