# CP1 外部 pthread span 合并与原生控制块计费（2026-10-04）

本批绑定产品 `e1c328ce8d275f32d2a53f2b2782c09a890016ed`、父 `ee67754c0297e596f9a5b1d1cbe21166488df1e1`。范围只关闭 Darwin `ReclamationThread` 首次查询落入外部 pthread 合并 region 时的误收费和错误拒绝，不领取完整 owned/native 总硬界、其他 allocator fault、非 Darwin 或宿主默认 abort 资格。

## 原缺口

旧实现创建 worker 后查询 `pthread_t` 所在的整段 `mach_vm_region`，并把该 region 的未付部分全部记为 PageStore 原生控制存储。Darwin 可将相邻 pthread 控制对象合并到一个 VM region；原先只知道如何从 monitor 查询结果扣除第一个 PageStore worker 的已付 span，无法区分在 PageStore 之前由外部线程持有的页。

arm64 反例先保持外部 pthread 存活并把合并 region 推到旧 64 KiB 准备边界，再启动 PageStore worker。父提交上的新用例立即得到 `scheduled == false`：新 worker 的控制对象本身仍有容量，但包含它的 region 已超过准备额，旧实现把外部页误算为 PageStore 所有。本轮保留 `baseline-failure-arm64.log`；x86_64 当前运行中控制对象保持独立映射，因此只作为外部线程共存与硬界控制，不声称复现 arm64 合并形态。

## 实现

`ReclamationThread` 仍先准备 64 KiB 并用 `mach_vm_region` 验证真实映射，但收费范围改为 Darwin SDK `pthread_t` 不透明对象的页对齐大小。查询只证明该 owned span 完整映射、地址页对齐且不超过准备额；相邻外部线程和另一个 PageStore 线程的页不再进入本线程费用。旧 `alreadyPaid` 参数、region 交集计算及每实例两个 span 字段删除，monitor 和 worker 各自持有自己的控制块费用，join 后由原 owner 释放。

没有新增 owner、锁、队列、业务状态或 API。生产一文件 **+20/−26**，测试一文件 **+105/−0**；删除的两个 span 字段在 worker 与 monitor 两个 `ReclamationThread` 实例上同时减少固定控制存储。

## 联合用例与结果

`nativeControlExcludesExternalThreads` 在任何 PageStore executor 创建前启动外部自有栈 pthread。arm64 形成 64 KiB 合并边界并保持全部外部线程存活；x86_64 保持至少四个外部线程。随后同一进程依次启动 PageStore worker 和 monitor，验证调度执行、实际 process storage 增量只覆盖两个 512 KiB 栈的实际容量及至多 64 KiB 控制/小型运行时存储，最后由原 drain/reset 回收。

- 定向 normal arm64、normal x86_64、TSAN arm64各 **3/0/0**。
- `KisPageStoreCpuMutationTest` 完整 normal arm64 **1388/0/0、10417ms**，x86_64 **1388/0/0、11311ms**。
- 同目标完整 TSAN arm64 **1388/0/0、125088ms**，日志无 ThreadSanitizer 报告。
- 本批复用现有 `_build-br0-cpu` 和 `_build-br1-tsan`；已经完成的长 manager/pressure 不重复运行。

源码、二进制、日志哈希和命令范围见 `results.json`。提交后产品 tracked tree clean。

## 边界

本批关闭 §16.82 留下的“首次外部 span 合并”具体反例，也取消了用整个 VM region 近似单个线程所有权的政策。它没有证明全部 owned/native reserved、live、并存 peak 和 physical-free 的管线总硬界；其他 node/control/task 的真实 allocator fault 与 read/publication/晚 fence/caller 联合终点仍需结算。非 Darwin 仍沿原 `std::thread` 合同，没有本批的实际 capacity/free 实现或平台运行；29 个历史 UE 与默认 abort 可回收资格不变。完整 CP1 与 M6/M7/M8 正式资格保持 0/3。
