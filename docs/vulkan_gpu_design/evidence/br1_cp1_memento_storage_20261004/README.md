# CP1 PageStore memento 存储归属与 presence 包装收敛（2026-10-04）

本批绑定产品 `0933ea04ddbe8bb58c04dc891d864be8cd95d778`、父 `02a92eb98d4ccfa02462f59ec04999bf7873dedb`。范围是把 PageStore history 实际持有的 memento 对象与 old/new 默认像素副本纳入 §16.96 的 process 硬界，并删除没有生产 caller 的分配型 presence 包装。当前裁决见 [92 §16.97](../../92_br1_m6_m8_execution_baseline.md#cp1-memento-storage-delivery)。

## 测试先行反例

父提交上的 `pageStoreMementoStorageIsProcessOwned` 创建 PageStore memento 后检查 process live。对象仍来自普通 heap，`object > before` 失败，得到 **2 passed / 1 failed**，见[基线失败](baseline-failure-arm64.log)。这证明 §16.96 的 process 状态转换正确，但尚未覆盖 PageStore history 桥自己持有的对象和默认像素副本。

## 实现与删除

`KisMemento` 保留两种明确来源。legacy `KisMementoManager` 仍使用全局 heap；PageStore backend 改用专用工厂，对象前缀记录 process/legacy 释放责任。PageStore memento 本体和 old/new 默认像素副本通过 `kisAllocatePageProcessStorage()` 分配，并由匹配的物理 free 退费。默认像素替换仍先分配并复制候选，再释放旧值，因此保留别名安全和 commit 拒绝后的重试语义。析构测试验证三个 process allocation 全部回到进入测试前的精确值；同一测试也锁定 legacy 对象和像素不进入 PageStore 账本。

`KisPageStore::resolvePagePresence()` 只被测试调用，生产 backend 已使用 caller-owned `resolvePagePresenceInto()` scratch。旧包装为了“失败不改输出”额外建立 `QVector` 候选，但没有产品 consumer。现在删除该声明和实现，测试直接覆盖唯一生产 selector；invalid surface、结束的 overlay、空 batch 和空输出继续由 `resolvePagePresenceInto()` 验证。

没有新增 owner、锁、队列或业务状态。五个生产/私有文件 **+121/−55**，测试一文件 **+44/−15**，合计 **+165/−70**。

## 验证结果

- memento/presence 目标组 normal arm64/x86_64 各 **7/0/0**。
- `KisPageStoreCpuMutationTest` 完整 normal arm64/x86_64 及 TSAN arm64 各 **1390/0/0**；TSAN 无报告。
- `KisPageStoreReferenceTest` 完整 normal arm64/x86_64 及 TSAN arm64 各 **790/0/0**；TSAN 无报告。
- legacy history/default/undo/purge 定向组 normal arm64/x86_64 及 TSAN arm64 各 **8/0/0**；TSAN 无报告。
- `kis_tiled_data_manager_test` 在 `QT_QPA_PLATFORM=offscreen`、`KIS_TEST_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install` 下 normal arm64/x86_64 各 **1105/0/0**。

首次 manager 全量调用没有传 `KIS_TEST_PREFIX_PATH`，在 848 项通过后由资源路径检查主动终止；补上源码明确要求的测试前缀后 normal 双架完整通过。完整 manager TSAN 尝试复现未改 `KisTiledExtentManager::prepareTileRange` 等路径的既有并发报告后停止；[此前活动证据](../br1_cp1_final_qualification_20261004/qt-manager-full-01/results.json)也记录同套件的 extent 并发报告。本轮没有把该运行计为 memento 回归或通过，直接受影响的 legacy history/default 定向 TSAN 与完整 CPU/Reference TSAN 均为零报告。

完整源码、二进制、命令、日志哈希和逐进程 Totals 见 [results.json](results.json)。产品提交后 tracked tree clean。

## 边界

本批关闭 PageStore memento 对象、old/new 默认像素副本和无 caller 分配型 presence 包装三处具体 residue。它不证明其他 owned 分配与 process/native 子管线共同组成的完整总硬界；其余 node/control/task 真实 allocator fault 和联合终点、非 Darwin capacity/free 实现与平台运行、29 个历史 UE 与默认 abort 可回收资格继续开放。完整 manager 的既有 extent TSAN 报告也未由本批改动或关闭。完整 CP1 不通过，M6/M7/M8 正式资格保持 0/3，persistent 默认关闭。
