# 机制计数补充协议（profile 固定四过程完成后登记）

当前 profile 把额外工作分为画笔 mutation 与 projection mutation；`KisUpdateJobItem` 同时调度二者，初版 actor 分类已纠正，原分析器/输出保留在 analysis-revision-0，未重采样。

固定 4 个 ARM 过程：ordinary / persistent-opt-in / persistent-opt-in / ordinary，各一遍原业务。只使用当前原生产库及已有 setter；不启用产品默认，不新增产品 API。派生夹具通过已有 `KisTiledDataManagerTest` friend 在原计时边界外读取 store/provider 现有累计计数，记录 node paint/original/projection、root original/projection、image projection，按实际 backend 指针去重，不把别名相加。它仅覆盖这些仍存活的 manager，不代表被销毁临时设备或进程总量。

假设：ordinary 已共享整笔 history transaction；opt-in 若进入持久机制，可减少 operation session / prepare / seal，canonical commit 不应从逐 dab 变成一次，因为原来也不是逐 dab commit。projection 无 stroke owner，未被 setter 迁移，其额外工作应保留。这个实验只检验数量责任；采样及计数均不能给真实速度收益或概率置信度。

派生差异为计数快照与 constructor setter。原输入、8 segment / 4 update、更新、像素、undo/redo、销毁检查完整保留；两种模式必须通过原 expected hash。保存源码差异、编译命令、实际库哈希、全部失败和进程终点。每过程 120 秒、超时 kill + 5 秒 reap；任何语义/退出失败停止本批，不换样。四过程完成即停，不做本批 wall 性能检验或额外 profiler。persistent 数量变化只作本例机制证据，资格与默认策略仍按原合同。
