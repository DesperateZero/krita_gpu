# CP1 进程/原生存储的预留、存活、峰值与物理释放（2026-10-04）

本批绑定产品 `02a92eb98d4ccfa02462f59ec04999bf7873dedb`、父 `e1c328ce8d275f32d2a53f2b2782c09a890016ed`。范围关闭 process/native allocator 从准备额度到实际映射、存活收费和物理释放的独立状态转换，不把该子管线外推为全部 owned 参与者的总硬界。当前裁决见 [92 §16.96](../../92_br1_m6_m8_execution_baseline.md#cp1-process-storage-accounting-delivery)。

## 原缺口

`kisReservePageProcessStorage()` 原来直接增加单一 process 总量，process budget 的 `usage()` 又把全部总量报告为 `live`。因此一个尚未执行物理分配的准备窗口已经显示为存活容量，无法独立证明 reserved、live、二者并存 peak 及 physical free 后退费。测试先在父提交上只做 4 KiB process reservation；`live` 从 575932 增至 580028，得到 **2 passed / 1 failed**，见 [基线失败](baseline-failure-arm64.log)。

## 实现

process storage 仍由原 `ProcessStorageState` 和原预算 controller 唯一拥有，新增 `liveBytes`、`reservedBytes` 与序列号；原 `bytes` 保持精确总量和硬限判定。写端继续由原 process gate 串行，读端用一致快照避免把 controller mutex 与 process gate 组成反向锁序。三个原子字段通过 `sizeof(ProcessStorageState)` 自动进入固定费用，normal/TSAN 固定尾账分别增加 24 B 至 2644/2492 B。

- reserve 只增加 reserved；allocation 成功后 commit 将实际容量从 reserved 移到 live，并退回未使用的准备额度。
- 取消只释放 reserved；实际 allocator free 或 pthread join 完成物理生命周期后才释放 live。
- process budget 的域准入和 aggregate pending 分别计入 process live/reserved；usage 与 peak 保留二者独立值，并以并存和更新峰值。
- `ReclamationThread` 仍准备 64 KiB；真实控制映射验证成功后提交实际 `controlBytes`，未用准备额立即退回，join 后释放 live。
- 普通 process allocation 保持 reserve → physical allocate → commit；分配异常取消 reservation，free 先完成物理释放再撤销 live 费用。

没有新增 owner、锁、队列、业务状态或公共 PageStore API。四个生产/私有文件 **+117/−16**，测试一文件 **+77/−12**，合计 **+194/−28**。

## 联合用例与结果

`processStorageReportsReservationSeparately` 逐项验证：纯 reservation 不改变 live；大于实际映射的 preparation 提交后只保留真实 capacity；live allocation 与第二个 reservation 共存时 peak 至少覆盖二者之和；最后先物理 free、再撤销 live，精确回到基线。目标组同时保留首次外部 pthread、容量拒绝/保留和 runtime stop 终点。

- 目标组 normal arm64/x86_64、TSAN arm64各 **6/0/0**。
- `KisPageStoreCpuMutationTest` 完整 normal arm64/x86_64各 **1389/0/0**；完整 TSAN arm64 **1389/0/0**，无 ThreadSanitizer 报告。
- `KisPageStoreReferenceTest`、`KisPageStorePhysicalClaimTest`、`KisCompletionRegistryTest` 每个环境合计 **1274/0/0**；normal 双架及 TSAN arm64均通过，无 ThreadSanitizer 报告。
- 本批复用现有 `_build-br0-cpu` 和 `_build-br1-tsan`。已完成且路径未改变的长 manager 与应用压力不重复运行。

完整源码、二进制、命令、日志哈希和逐进程 Totals 见 [results.json](results.json)。产品提交后 tracked tree clean。

## 边界

本批关闭 process/native allocator 的独立 reserved/live/coexist peak/physical-free 转换，包括原生线程控制映射的准备额到实际额。它不证明其他 owned 分配与该子管线共同组成的完整总硬界；其余 node/control/task 真实 allocator fault 和联合终点、非 Darwin capacity/free 实现与平台运行、29 个历史 UE 与默认 abort 可回收资格继续开放。完整 CP1 不通过，M6/M7/M8 正式资格保持 0/3，persistent 默认关闭。
