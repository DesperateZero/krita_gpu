# 独立确认前裁决

生产算法保持r0；r1/r2仅补齐测试计数和反例、源码审计。双架构四套件各3633 passed/0 failed/0 skipped，合计7266。新finalPayload 80行、seal硬容量拒绝/原目标重试1行、final-input真实handoff16行通过。原CPU mutation、manager、physical claim、resident read全部通过。首轮manager14个失败均为原完整输入写pin计数仍要求非零，失败保留；只改其预期删量，像素/history/资源断言保持。

原架构检查因库存及调用图来源哈希陈旧失败；更新生成库存和图后通过，未放宽intrusion ratchet或layout ceiling。六项工具自测通过。当前源码/实际image在确认前冻结至candidate-identity.json。

独立两进程/版本机制矩阵一致：K16/N16两种history各Fresh 1024、sealed pages 1024不变；写pin/unpin 1024→0；前台localVersionInputs 3072→1024，localVersionInstalls仍1024；localTransitionSequences H0 2048→1024，H1 6016→4992（其余history保护工作保留）。四次write状态转换合一的静态模型，实际对应每页少一个共同metadata执行序列和两个投影版本输入；不把转换数当锁次数。

固定2块/8过程探索：K16/N16 write父减新H0 0.92025ms（块1.2295/0.611）、H1 1.598ms（2.0945/1.1015），完整case为1.3725/2.0805ms。仅作方向/价值选择，无置信资格；两种history均超过事前工程目标0.5ms，进入原协议32过程独立增量确认，再32过程新/upstream与16过程业务控制。探索不混入确认，不追加样本到显著。

保持没有可信窄时间预测的判断：只验证了删量模型。确认估计不与旧8.256/6.976差额直接相减；新/upstream另测。Fresh反复周转的物理数量差尚未消除，M6/M7/M8、默认值和正式门均不改变。
