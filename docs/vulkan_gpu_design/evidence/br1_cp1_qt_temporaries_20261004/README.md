# CP1 原错误回报及格式编号临时字节

当前裁决：[92 §16.90](../../92_br1_m6_m8_execution_baseline.md#cp1-qt-temporary-delivery)。产品 `87a8b43ae98bcf13fb437ee7fe2b941701035fe3`，父 `2e471d5efb7e99ee323541fe499478af9d43e73c`；文档父 `0e4cfdff`。完整 CP1 仍开放，M6/M7/M8 正式 0/3，persistent 默认关闭。

## 完整责任与实际差异

原 beginWriteImpl 和 sealImpl 在拒绝之后拼接 QString，错误回报自己再次申请未收费存储；即使 error 输出为空，实参求值仍发生。两入口直接传播原 failure，共享其已有存储；原因为空时使用静态通用文本。具体原因保持，外层前缀不再拼接，拒绝状态、原取消/退休和同 owner 接续不变。仓库没有依赖旧完整前缀的消费者。

原 backend configure 的 QByteArray::number 先分配临时 Qt 字节，再复制到已收费格式值。现用 10 字节栈数组和 to_chars 转换相同 quint32 表达式，直接构造原 KisPageByteArray；其控制块、字节和最后释放继续由原 allocator 承担。没有改变 pixelSize 算术语义，没有增加格式缓存或收费 owner。

生产两文件 **+8/−3**，测试 **0/0**，派生两 JSON **+1800/−1799**；无新类型、公共 API、锁、队列或测试 hook。净增五行用于有界的栈转换和无额外分配的错误传播，不当作性能收益。

## 身份与实际验证

[最终 127 源/头身份](product-source-freeze-final.json)匹配产品 Git blob。两受影响 TU 的原 Ninja 依赖完整保存；冻结 189 份源码输入及 1,496 份外部编译输入。normal/TSAN 各重编两个 TU 并链接，其余 407/398 个实际链接输入及复制的 8/7 个原测试二进制逐项匹配父构建记录，见 [复用验证](reuse-verification.json)。主安装、在途旧 manager 库和源输入未改。图仍 87 TUs / 2,172 APIs / 27,412 edges / 27 callbacks；21 manifest / 25 ownership / 16 census / 19-file ratchet 通过，工具未改，不重复工具自测。

| 同源范围 | 结果 | 边界 |
|---|---|---|
| 原完整 CPU body，arm64 + x86_64 普通版 | 2,772 passed / 0 failed / 0 skipped | 两进程 actual0/reaped，无观察器或退出 guard |
| 原完整 CPU body，arm64 TSAN | 1,386 / 0 / 0 | actual0/reaped，122.05s，匹配插桩 QtCore，无 suppression / interposer / TSAN 警告 |
| 原完整 CPU body，两架独立账本 | 各 1,386 / 0 / 0 | 同一 observer05，actual0/reaped，观察表 overflow0 |

[逐栈对照及结果](summary.json)以 3c 的原完整观察为基线：**每架 139 次错误拼接、10 次格式编号临时分配，共六个已观察 stack site，修复后全部消失**。原路径的真实拒绝测试没有减少。其他 site 数量和分配次数的变化不计本次收益；当前仍有 345/340 个未收费 PageStore 可达 site，包含既有外部/调用者/测试责任。两架 static 后已识别 paid heap/VM 均为 0，paid usable 同时余量峰值 0，各表溢出 0。约 12.9GB 峰值含原 runtimeStopsAtCapacity 限额填充，不称业务峰值、RSS 或全部进程硬界。

首轮构建前扫描误解析所有 Ninja 对象的依赖路径，约 2.5 分钟/4 GiB RSS 后主动终止本轮 scanner，shell143/reaped；没有编译或启动测试。保留原脚本及 [终止记录](preflight-01-termination.json)。修正仅解析两个受影响对象，同时保存完整原 Ninja 输出；随后两构建和全部五个测试进程实际正常退出。

## 仍在运行及未完成出口

[manager 冻结检查点](manager-checkpoint.json)分别复核 8f 的 1,979 源/107 运行输入和 2e 的 1,615 源/107 运行输入；2e 补充 1,716 份原 Ninja 输入也逐项未变。两者各 1,098 PASS 前缀、无 Totals，实际仍 Pending。这些运行属于原冻结源码，不是 87a 的完整 manager 资格；终点应另行结算，不能无限保留 Pending。宿主只读清点仍 24 UE，本轮无新增 UE，未清理宿主。

剩余按 92 四组共同出口：全部 owned/TileData/pool/异常/Qt/OS/TLS/caller 及首次 native 外部合并的独立总硬界；其他线程真实故障与 read/capture/history/publication/retirement/close、晚 fence/caller 共同终点；非 Darwin 实际 capacity/free 实现与平台运行；最终源码完整 manager、24 UE/default abort/双 native 释放失败。此处关闭的三处临时分配不再重领。调用者输出、C++异常/TLS和外部 Qt 共享存储没有因本轮消失；CP5/CP10 仍归原包。

文本证据按内容寻址封装到 `evidence-bundle.tar.gz`，`evidence-bundle-manifest.json` 映射原路径和逐 blob SHA256；源码、编译/运行命令、原始日志、失败与固定 manager 前缀全部保留，二进制/dSYM 不入 Git。原始文件仍在工作区。
