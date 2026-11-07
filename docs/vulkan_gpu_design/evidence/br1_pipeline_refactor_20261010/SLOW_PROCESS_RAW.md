# 慢过程归因原始证据

[原始包](slow-process-raw.tar.xz)与[逐成员及整包SHA256](slow-process-manifest.json)保存r0编译失败、r1能力原始值/单位纠错依据、r2两侧fixture源码/构建命令、140个业务过程完整stdout/stderr、退出/timeout/reap、实际加载库SHA、结果、各批冻结协议与runner、Apple XNU接口说明及下载来源。二进制和对象不入包。

在本目录展开包后，`python3 analyze_slow_process.py`、`python3 analyze_slow_qos.py`、`python3 build_slow_cause_ledger.py`复算数值；`python3 audit_slow_process.py`还依赖本机冻结产品源码与库，不能用不同构建冒充通过。runner和builder使用一次性目录，不覆盖或重跑原样本。

`slow-cause-r2/natural/run_slow_process.py`是自然批原runner；顶层版本只修正了期望case顺序的读取方式，以允许后续干预固定正序，实际测量代码未改变。干预目录另保存其准确helper。原主图与上一批raw包均未重写。

`slow-cause-r1/probe.log`的`user_ns/system_ns/puser_ns/psystem_ns/runnable_ns`名称有误，实际存的是原始Mach ticks；该日志作为能力/纠错保留，不用于业务账。正式fixture各`ri_*`时间仍为ticks，`cpu_ns/pcpu_ns`才是按numer/denom换算后的纳秒。
