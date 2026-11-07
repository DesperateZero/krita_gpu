# 本轮原始证据

三个原始包保存准备/构建失败、派生源码/diff/命令、冻结身份、全部成功和失败过程stdout/stderr、退出/reap、运行依赖、压力与冷尾诊断；不包含二进制、对象或外部库。

- [A：r4公共矩阵前半及完整汇总](budget-coverage-raw-a.tar.xz)
- [B：r4公共矩阵后半、压力及冷尾](budget-coverage-raw-b.tar.xz)
- [C：准备/前批失败、追踪目标事件及元数据](budget-coverage-raw-c.tar.xz)
- [逐成员SHA、包SHA及可重建数组](budget-raw-manifest.json)

在本目录提取三包，再执行`python3 restore_budget_events.py`，会从原始日志恢复被省略的重复`events.json`，并逐一匹配原SHA。随后可运行`analyze_budget_coverage.py`、`analyze_budget_pressure.py`和`audit_budget_coverage.py`；源码/运行库核验仍需本机冻结构建，不能用不同库替代。

完整System Trace和未过滤内核XML保留在本机`budget-coverage-r0/`、`budget-coverage-r4/system-trace/`，不入包。包内保存目标进程全部解码state、signpost边界、原stdout、工具警告和toc；对应原始导出SHA在`budget-trace-summary.json`。这些足以复核目标区间状态加法与缺口；从全量XML重新解码则仍需本机原导出，不能声称包内有全部内核事件。没有使用非目标进程做归因。

首次文档补丁因代码块中一行缺少patch前缀被拒绝，修正后重新应用；没有改变测量样本。原产品和原安全库保持，所有新时间独立于旧预算图。
