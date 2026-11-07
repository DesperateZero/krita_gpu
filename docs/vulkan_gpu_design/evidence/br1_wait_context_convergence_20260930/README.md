# Wait context 与 reservation 空闲链收敛

当前裁决见 [92 §16.26](../../92_br1_m6_m8_execution_baseline.md#wait-context-control-convergence)。本批删除 context 的 Qt shared/weak 控制块与独立 free-list；固定 32 项请求数组实际收费并在退出时释放，未安装候选先取消 wake 解除引用环。waiter 产品方法集合不变。

最终代码构建见 [build.log](build.log)。CPU waiter、退休与 read last-use 目标矩阵为 [arm64](tests-arm64.log) 和 [x86_64](tests-x86_64.log) 各 68 passed / 0 failed / 0 skipped；共享父额度、Fresh budget 和实际 mutation storage 为 [arm64](reference-arm64.log) 和 [x86_64](reference-x86_64.log) 各 5 / 0 / 0，合计 146 / 0 / 0。这是目标回归，不能称为完整 M8 矩阵。

新增覆盖父额度少 1 B 的准备拒绝、八线程首次登记候选清理、dormant handle 在 controller 退出后的失效，以及 128 个 grant 的交错回收、move、commit 和后续复用。

[调用图](callgraph.log)为 1,832 APIs / 19,946 edges / 17 callbacks；[结构门](architecture.log)与[基线刷新](architecture-baseline.log)记录 21 manifest / 25 ownership / 16 census / 19 intrusion files。[源码身份](source-sha256.txt)绑定本批实际文件；[HEAD](head.txt)不代表脏工作树已提交。

仍开放：slot 数组本体和自身准入、callback/task/retry/pass/terminal 存储、小型 inert anchor 在 controller 退出后实际内存的进程级字节/数量界，以及跨 store 公平和原 job continuation。controller 退出时退 charge 只证明不再访问已死预算，不证明墓碑尾存储的硬上界。完整 S09/S10/BC9/M6–M8 和默认工具启用均未关闭。

后续 reservation 数组自身准入和 controller cache 的当前计账见 [92 §16.27](../../92_br1_m6_m8_execution_baseline.md#reservation-storage-admission)。本目录 146 项、结构结果和 hash 保留原冻结身份；不得用后续源码沿用本目录资格。
