# CP0 当前适用清单与普通 freehand 对照

本包在新样本前冻结。文档父 bb479be2c085d8363f42d2ec5ceaeafd16d0fee8，产品 38834c4e2612c819f9d088dfd59c59889f295a49，固定 upstream 9a24ae0d8c070884fb013594191002e1a1b39a19。沿 92 §2/§3/§6/§14/§17、39 §5.6–5.9/§10 工作，不读 archive，不修改生产代码或旧证据。

## 有限交付

1. 将当前合同要求映射为阶段、实际 consumer、现有测试/证据、尚缺证明及下一动作。清单建立不等于这些要求通过；完整 CP0 还需要正式样本协议、可运行能力与基线。M6 已支持 resident CpuRam/CpuPointer；其他恢复域不能冒充正例，既有资源/SSD 耗尽/退出要求保留。
2. 复用 CP0 20261003 同依赖 upstream 构建和四个同字节文件，不改变输入、普通策略、4 workers、8 段/4 更新、projection-ready/undo/redo/owner teardown 端点。确认当前 test target 可构建且产品树未改。四次 dyld 能力过程验证实际加载、相同依赖、语义和像素，能力过程不进统计。
3. 能力全部通过后，arm64 和 x86_64/Rosetta 各 24 个独立进程配对，共 96 个计时过程。每相邻两对为一个顺序平衡块，架构逐块交替；块内 upstream→current、current→upstream。固定种子 261017，20,000 次按 12 个平衡块 bootstrap，估计量为块内 log(current/upstream) latency ratio 的均值，再对块取均值并 exp。每架七个端点分别给描述性双侧 95% 区间，不是多指标正式资格，也不从 latency 倒数生成吞吐。
4. 全部尝试写日志和 actual exit/timeout/reap；240 秒超时后 kill 并最多 5 秒 reap。身份、语义或退出失败即停止本批，不换样、不扩样到通过。既有 failed process 不删除。每次过程都保留 dyld 实际加载集合，启动加载输出在夹具计时之外；能力阶段计算 hash、计时阶段核对加载集合，整个定时批次前后再验 hash。无 profiler、无阶段计时、无并行 build/benchmark；保留默认 hash/QoS/调度，不按 CPU 编号删样或归一化。
5. 性能结果只回答当前普通业务路径相对同依赖 upstream 的代表性差距。无 canvas-visible、first-dab、P95/P99、M/K 分拆、自然 alternate 统计或全过程资源峰值资格；persistent 默认仍关闭，局部 handoff 正收益不替代本结果。若有大差距，按当前源码列出下一完整责任，禁止把旧热点或本批粗时间直接定价为可删 CPU 成本。
6. metadata 仅核清分母和观测覆盖。trackedPayloadBytes、owningCapacityBytes、arena allocatedBytes 不可直接相加为完整实际驻留；不给缺失 pre-reconstruction used/reserved/slack 同义分母填零，不选已重构 M5 或空 upstream 作为便宜替代。

有限包完成后停止；保留正式校准 2/20、联合 hit 0/4、miss 2/16、原 Fresh/H4 8/8 及 M6/M7/M8 0/3 的独立裁决。
