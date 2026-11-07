# 跨阶段后台事件的分析修订

首版复用前台分析器要求所有stage2事件end_stage=2，实际四个history过程均有最后一对pass/job结束于stage0，触发断言。原脚本保存analyze-v0.py，原20过程不修改、不追加。每过程这类job CPU为0.018375–0.020791ms，pass为0.015875–0.017791ms。

修订只改变报表表达：先对全部已记录事件核验父子CPU/wall和线程账；Stroke内完全闭合的event self计入closed账，跨阶段event self单列crossing账；对history完整范围另列closed inclusive及crossing inclusive，不能将嵌套job+pass相加。started阶段的总量仅作上下文数，不再冒称精确Stroke成本。

closed到closed+crossing只约束**这些被记录且在Stroke开始的scope**在Stroke内的贡献，不能约束所有history CPU：stage0启动而跨入Stroke的scope原观察器未记录，未覆盖线程/队列/前台request也仍不在history pass里。本包不能给候选严格上界或完整history占比。该限制降低精确归因能力，但保留了可与其它责任比较的完整已观察调用的粗价格。

不因跨阶段而删整个过程、截断时间或统一扣偏差。observer errors/overflow/active仍须0。新观察价格是否触发原扰动线继续按原协议，不修改阈值、不重采。
