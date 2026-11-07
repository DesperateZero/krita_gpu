# CP1 Tiles3 read/capture 分配拒绝收敛（2026-10-04）

本批产品 `a7f0d7c537ddfbed4809136e3530ada00fd4d406`，父 `0933ea04ddbe8bb58c04dc891d864be8cd95d778`。它只领取 §16.98 剩余第一组中的两个实际端点：completed tile source capture 与派生 read cache 冷创建。生产改动集中在 `KisTiles3PageReplicaProvider.cpp`，测试改动集中在 `KisPageStoreCpuMutationTest.cpp`；没有新增 API、owner、线程、队列或恢复阶段。

## 先失败的实际反例

在父产品上加入 `tiles3ReadCaptureStorageRefusalIsRecoverable` 后，把 product process metadata budget 用真实 process allocator 填到 `live + reserved == limit`，再用仍有效的 resident read guard 依次执行 completed-source capture 与 read-cache 创建。旧实现从 `captureCompletedTileSource` 泄漏 `std::bad_alloc`，定向运行 **2 passed / 1 failed**，失败为 `completed source capture leaked bad_alloc`。这证明是现存产品端点的实际容量拒绝，不是模拟 provider 返回值。

## 改动与共同终点

- `captureCompletedTileSource` 在原 provider mutex 和原 retained allocator 上分配；容量拒绝现在写入原 `QString *error` 并返回空 source。
- `Tiles3TileReadCache::prepare` 的新对象只是派生读提示；其 process object 冷分配被拒时返回空 lease，原 binding、read guard 和物理 tile 不变。
- 同一测试在拒绝后确认 process 用量仍等于硬限、原 guard 仍读到 `0x31`；释放 filler 后用同一 guard 重试，source 与 cache 均成功，cache finish、source/cache 销毁后 process 用量精确回到拒绝前基线。

因此 read/capture 两个调用链现在都沿既有空结果/错误返回终结，caller 不再需要捕获 allocator 异常，也没有建立第二套重试协议。

## 当前提交验证

[机器结果](results.json)绑定最终产品与两个源码哈希；原始日志保存在本目录：

- CPU mutation normal：[arm64](cpu-arm64.txt)与[x86_64](cpu-x86_64.txt)各 **1391/0/0**。
- PhysicalClaim normal：[arm64](physical-arm64.txt)与[x86_64](physical-x86_64.txt)各 **397/0/0**。
- Reference normal：[arm64](reference-arm64.txt)与[x86_64](reference-x86_64.txt)各 **790/0/0**。
- CPU mutation TSAN：[arm64](cpu-tsan-arm64.txt) **1391/0/0**，日志中无 ThreadSanitizer 报告。

§16.98 已绑定的 8/24 MiB 业务压力没有重复运行；本批只验证新增实际拒绝、恢复以及受影响的完整 CPU/provider/caller 套件。

## 剩余

完整 CP1 仍未关闭。第一组继续保留 completed-source/read-cache 之外的 node/control/task allocator fault，以及其他线程、publication、晚 fence 与 caller 共同终点；另有非 Darwin capacity/free 实现和平台运行、29 个历史 UE/default abort 可回收资格。M6/M7/M8 正式资格仍为 0/3。
