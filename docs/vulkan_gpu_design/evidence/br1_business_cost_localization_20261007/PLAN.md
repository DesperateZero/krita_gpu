# 普通 freehand 的实际成本定位

产品起点 128fb32a71fef69f462da2c2dfa8d187ed94db52（生产仍与 38834c4e26 相同），文档起点 875f364b77c5667f0c2ca85bc68bc245b35f3ef3。当前入口 92 §16.140；不读 archive，不改变产品默认，不延长旧性能包。

## 问题与边界

已知普通 freehand 当前/upstream stroke 时间比约 2.26/2.32，不能直接视为管理的可删预算。本轮先定位 CPU 真正运行的责任，再核对可省工作与必要像素/可见性/失败边界；不按分配或引用次数猜改产品。

## 固定首轮

- 共用原 matched_freehand_baseline.h 的全部业务输入、计时区间和断言。仅证据副本在原 setup/stroke/undo/redo/teardown 区间外加 os_signpost，原像素验证独立归为区间外。逐项生成差异，原 timed statement 字节和顺序保持。每次完整 replay 仍创建/释放 image；同一过程后续 replay 的全局 cache 是暖的，明确区别于上一批一过程一笔的基线。
- 使用双方原 MatchedFreehandBaselineTest 的实际编译参数、link libraries、同源共享头和插件集合，编译 ARM 原生诊断入口。先双方各一过程一次 replay 能力验证，不计性能资格。
- 固定 4 个 profiling 过程，顺序 current/upstream/upstream/current；每过程先输出 ready、等待 8 秒供 attach，随后完整 replay 64 次。Time Profiler + Points of Interest 各录 25 秒，捕获完整 signpost 区间中的所有线程 Running 样本；边界不完整的区间只记未覆盖，不当零成本。进程须跑完 64 次断言后正常退出。
- 每过程 120 秒上限；超时 kill，5 秒 reap。语义/退出/身份失败保留并停止对应批次，不换样。profiling/export 故障保留；分析器修正可重读原 trace，不重录。所有计时/profile与构建/其他基准串行。
- 报告每个阶段的样本、exclusive leaf 与互斥责任分类；inclusive caller 仅作上下文，不相加。线程 Running sample 是粗 CPU 定位，不转换为精确 CPU 微秒或理论可删比例。主线程/worker、stroke/projection/validation/后台分开；未解释残差保留。
- 按结果选择一个完整候选，再以实际调用点计数/同义消融确定可删量和保留边界。后续机制实验先另行登记，不把本轮 profiler 时延作为生产收益；没有足够证据时只交付已证实定位及可验证候选。

正式 M6 校准 2/20、metadata 实际重构前驻留分母、完整 CP0/业务/GPU 资格保持各自独立。
