# CP1 低内存测试陈旧 ABI 裁决（2026-10-04）

本目录复核 §16.91 保留的 `KisLowMemoryTests::readWriteOnSharedTiles` SIGSEGV。结论是：该崩溃由 2026-09-25 的陈旧测试对象与 2026-10-04 候选 `libkritaimage` 的 `KisTiledDataManager` 布局不一致造成，不是产品并发或 TileData 生命周期缺陷。产品源码、产品测试和派生审计文件均未修改；当前产品仍为 `1177fa5ecab8318fe044b071342eb0ab51654e27`。

## 可靠故障位置

`fault-context-guard.cpp` 仅安装 async-signal-safe 的 SIGSEGV/SIGBUS/SIGABRT 处理器并在替代栈写出寄存器，随后用 `_exit(128 + signal)` 回收进程。原陈旧二进制在 arm64 实际退出139，1.535秒，fault address/FAR均为 `0x18`，PC相对候选 `libkritaimage` 为 `0x1328d0`，LR为 `0x13207c`，`x20=0`、`x24=0x18`，候选镜像和守护均确认加载。

`atos` 将PC定位到 `KisTileHashTableTraits2<KisTile>::getReadOnlyTileLazy` 的 `kis_tile_hash_table2.h:523`，LR定位到 `KisTiledDataManager::getReadOnlyTileLazy` 的 `kis_tiled_data_manager.cc:329`。反汇编显示外层从 manager `this+0x18` 载入 hash table 作为内层第一个参数；内层保存为 `x20`，再以 `x20+0x18` 执行 `ldaddal`。因此直接原因是调用者对象中 `m_hashTable` 位置为空，不是 nullable tile 返回值或QSBR内部状态先损坏。原寄存器、符号和指令见 `arm64-01/`、`fault-symbolication.log` 及 `fault-disassembly.log`。

## ABI 对照

陈旧 `_build-br0-cpu` 测试对象的时间为 2026-09-25 02:48:01；DWARF在arm64/x86_64都记录 `KisTiledDataManager` 为 **232字节（0xe8）**、声明行63。当前头文件在2026-10-03已由 `b10b2913a69604d42b51cac83ba81214d30d43de` 修改；用当前编译命令、MOC和链接输入隔离重建的测试对象在双架都记录 **288字节（0x120）**、声明行87，差56字节。陈旧测试仍在栈上按232字节为两个 manager 分配空间，却调用当前动态库中按288字节布局写对象的构造函数；越界覆盖后续栈对象并使外层 getter 从错误布局读取空 `m_hashTable`。`abi-comparison.json` 冻结两对象、当前头、候选库、故障结果和收集脚本的哈希。

## 当前布局复验

`build_current_test.py` 从原 compile database 和实际 Ninja 链接命令重建测试与MOC，保留1,644个直接/依赖/链接输入哈希，产出双架构当前布局二进制。`run_current_test.py` 使用独立XDG配置、最终候选镜像和同一故障守护执行原 `readWriteOnSharedTiles` body：

- arm64：**3 passed / 0 failed / 0 skipped，10260ms，actual0/reaped**；
- x86_64：**3 passed / 0 failed / 0 skipped，10327ms，actual0/reaped**。

两架均确认当前测试二进制、候选 `libkritaimage` 和守护加载，`fault_contexts=0`，所有冻结运行输入在退出后复核未变。故障守护在正常路径不改变测试语义，只阻止意外致命信号成为新的宿主未预期退出。

## 裁决

§16.91 的旧/新库同样崩溃只证明两次运行复用了同一个陈旧测试可执行文件，不能证明父库与候选共有产品缺陷。本轮将该SIGSEGV从CP1产品残留撤销，不修改产品代码，也不把陈旧失败改计为通过。探索形成的4个宿主未预期退出仍保留在28个历史UE清单中，等待统一宿主出口结算。

完整CP1仍有三组产品责任：全部owned/外部native的独立reserved/live/并存peak/physical-free总硬界及首次外部span合并；其他真实node/control/task拒绝、其他线程和read/capture/history/publication/retirement/close、晚fence/caller共同终点；非Darwin实际capacity/free实现与平台运行。另有28个历史UE、默认abort和双native释放失败出口。M6/M7/M8正式0/3，persistent默认关闭。
