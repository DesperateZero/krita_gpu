# CP1 PageStore caller 联合分配失败收敛（2026-10-04）

本批产品 `caaafcf58d21f5d5470dc28fa80ef146fbdb59f2`，父 `a7f0d7c537ddfbed4809136e3530ada00fd4d406`。它继续领取 §16.99 第一组中的 caller 联合终点，只修改初始化字节导入和 exact-generation archive read 两条现存入口；没有新增 API、owner、线程、队列或恢复阶段。

## 实际反例与失败终点

`initialByteImportProviderStorageFailureIsRecoverable` 使用与 Store/provider 共享的 4 MiB process metadata controller。在 provider request 和 write-access resolve 两个调用点分别用真实 allocator 填满剩余容量，再发起一字节实际分配；旧调用边界没有接住 `std::bad_alloc`，且 request 区间的 `activeProviderCalls` 只在正常返回时归还。当前实现把整个 provider 区间放入原计数的作用域终点：request 拒绝返回原错误，resolve 拒绝退休本轮刚建 backing；两次均保持计数为零。释放 filler 后等待退休为空，同一 import 重试成功并读回 `0x27`。

`FakeAsyncExactArchive` 在 `storeExact` 的分配点确定性抛出 `std::bad_alloc`。`archiveRead` 现在将它收回原无效 ticket/错误返回，同时释放 resident read lease、归还 active provider 计数且不安装 pending archive。原 published byte 保持 `0x61`，紧接着同一版本重试进入原 async completion/cancel/close 协议。

两条路径只把跨组件分配失败送回已有 caller 返回值；不把 caller-owned 输出改成第二份 PageStore 存储，也不改变 provider/archive 自身的失败原子性责任。

## 当前提交验证

[机器结果](results.json)绑定产品、父提交、三份源码和六份原始日志：

- CPU Mutation normal：[arm64](cp1-caller-cpu-arm64.txt)与[x86_64](cp1-caller-cpu-x86_64.txt)各 **1392/0/0**。
- Reference normal：[arm64](cp1-caller-reference-arm64.txt)与[x86_64](cp1-caller-reference-x86_64.txt)各 **790/0/0**。
- 两个受影响方法的 arm64 TSAN：[CPU](cp1-caller-cpu-tsan-arm64.txt)与[Reference](cp1-caller-reference-tsan-arm64.txt)各 **3/0/0**，日志中无 ThreadSanitizer 报告。

本批没有重复运行 §16.98 已绑定的 8/24 MiB 长压测。活动 architecture checkpoint 早于最近多批已提交源码，直接检查会报告已知 stale source/callgraph；本批未把该结果记为通过，也未刷新生成基线掩盖差异。

## 剩余

完整 CP1 仍未关闭。第一组现在排除 completed-source/read-cache 和本批 import/archive caller 联合终点，继续处理有实际分配反例的其他 node/control/task、线程、publication、late-fence 与 close 端点；第二组为非 Darwin capacity/free 实现和平台运行；第三组为 29 个历史 UE/default abort 可回收资格。M6/M7/M8 正式资格仍为 0/3。
