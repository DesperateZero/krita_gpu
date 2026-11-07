# CP3 coordinator-owned 工作值与共同状态策略（2026-10-05）

产品 `58b4dfc09c3048d2f344ccb35a3d92d80adc390f`，父 `6d439e0437c86b5214064eef5bc5134f2160cf43`。本批完成共享工作值生命周期的等价重构；**完整 CP3/M6 未通过，M6/M7/M8仍0/3，persistent默认关闭**。[领取](start-review.json)、[责任与拒绝审查](checkpoint-review.json)、[交付](delivery.json)及[最终身份](final-verification.json)绑定同一源码。

Metadata projection/publication 直接创建一个原收费工作结果，shared policy按引用推进同一值，直到拒绝丢弃或准备安装。删除两种transitionResult及工作state/result的按值传入、返回、逐步接回；三个私有调用点全部迁移。公共oracle仍创建独立快照、执行原前后不变量检查，拒绝恢复原current。每步effects仍清空、由原序列carrier累计；保留的容量继续实际收费，序列退出时按原allocator释放。原revision/physical-slot/lease/pin/retirement debt/arena growth/活动容量与安装顺序保持，没有合并generic readiness或private/canonical可见性。生产四文件+34/-41净-7，测试0改动，生成audit+4652/-4730单列；无新字段/owner/队列/公开API。

双架原38同源测试进程 **10818/0/0**，全部实际正常退出、reaped；包括独立oracle/多步拒绝/竞争、正确ReadBaseline、selected persistent business及Vulkan foundation。额外六个实际探针每架覆盖31080 handoff和28 publication/restore安装，alloc/VM/bytes/free均0；24实际allocator生命周期边界通过。结构21manifest/25ownership/16census/19intrusion及原ratchet保持；87TU、2185APIs、28497edges、27callbacks，六工具自测通过。

全部build/safety/control结束后，沿原未改协议运行三个scope，各四桶、完整40对，合计960实际正常退出性能进程，输入身份核验通过；无并行build/benchmark或采样。Fresh/H4均20顺序平衡blocks、50000 bootstrap/seed260926；handoff为20000 bootstrap/seed12345。下界为原单侧98.75%/桶；三个family独立裁决。

| scope / bucket | arm64 K1 | arm64 K16 | x86 K1 | x86 K16 |
|---|---:|---:|---:|---:|
| Fresh current÷M5 | 0.9944 | 0.7711 | 1.0673 | 0.8087 |
| Fresh下界，需≥0.98 | **0.9913** | 0.7667 | **1.0486** | 0.8045 |
| H4 current÷M5 | 1.2733 | 1.0206 | 1.1300 | 1.0747 |
| H4下界，需≥0.98 | **1.2644** | **1.0159** | **1.1226** | **1.0648** |
| handoff延迟降幅 | 2.46% | 6.85% | 1.98% | 7.88% |
| handoff下界，K1需20%/K16需30% | 1.80% | 6.35% | 0.80% | 7.14% |

H4四桶及该scoped family通过；Fresh K1两桶通过，K16仍低M5约19–23%，Fresh family失败；handoff四桶失败。见[Fresh](fixed-m5-fresh-summary.json)、[H4](fixed-m5-history-summary.json)、[handoff](latency-summary.json)。H4为四个undo事务；Fresh公共夹具N1024/K16与native handoff的N=K不是同一端点。不同轮归一化结果只描述趋势，不相减为本提交因果收益；这些局部结果不替代真实绘画/upstream/尾分位数资格。

独立[steady采样](public-fresh-steady-profile/localization.json)确认实际init marker及write loop，exclusive产品栈仍指向fitsLocked、实际分配/收费/释放和Ledger preparation；包含所有线程，只定位，不计因果百分比或收益。下一审失败桶内实际小存储的物理请求与收费/转交/释放整体责任，优先消除重复工作，保留完整limiter政策及实际预算。已结算的私有工作值移动、sparse batch和CP1/CP2不重领。

首次编译因const引用调用原非const findVersion拒绝，修正为同一工作值的可变引用后重新完整构建；失败与修复见[执行问题](execution-issues.json)，不混入成功样本。最终核验2315当前及1143 M5 Git blobs、265 runtime/harness输入、18身份集合。原长压测、OFF、其他完整模式及TSAN限制保持；metadata重构前同义used/reserved/slack≥25%分母和CP0完整required仍欠。日志保留为[压缩附件](raw-logs.tar.gz)，[SHA清单](raw-log-manifest.json)逐member验证；构建二进制、对象和测试图片不入库。
