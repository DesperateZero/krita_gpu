# CP1 当前源码的有限容量与默认拒绝退出续验

本轮产品保持 `61a0e28bdd1d8d6ac56f471550eb3f0e1db42b4b`，文档父为 `579fd72f99ad3928e5dc6fc2a5aeeb65a185f1c1`。生产、产品测试及派生 JSON 增删均为 0；没有新增 owner、队列、锁、公共 API 或恢复阶段。当前裁决见 [92 §16.84](../../92_br1_m6_m8_execution_baseline.md#cp1-finite-default-qualification)。完整 CP1 尚未通过。

## 有限容量结算

原 Freehand 的取消和压力方法分别完整执行，复用原 main、框架初始化及 QTest body；只将 main/qExec 转接到审计器。每架一个冻结二进制承接两种原方法，未缩小工作量、放宽产品限额或替换成手写像素 fixture。

| 原方法 / 架构 | 观察界 B | 观察峰值 B | 样本数 | 原 body / actual exit |
|---|---:|---:|---:|---|
| `testPersistentAutoBrushStrokePressureCancelled` / arm64 | 8,388,608 | 8,025,662 | 32,101 | 4/0/0 / 0 |
| 同方法 / x86_64 | 8,388,608 | 8,009,390 | 32,376 | 4/0/0 / 0 |
| `testPersistentAutoBrushStrokePressure` / arm64 | 25,165,824 | 13,290,222 | 302,946 | 3/0/0 / 0 |
| 同方法 / x86_64 | 25,165,824 | 13,300,270 | 324,417 | 3/0/0 / 0 |

[机器结算](capacity-summary.json)核对四次 actual exit0、共 14/0/0、实际 join 后原地址 unmapped、native 请求归零，以及 static 后 classified paid=0 / overflow=0。main 后仍有原 Resource/executor 的 704/712B paid，连同固定费为 796/804B；不把 main 返回写成静态对象已释放。

观察式为 **E8 路由识别的 paid malloc 请求 + 原 pthread 控制对象实际请求 + 启动前固定费用 92B**。在每次 paid 加入及 native 创建后同一审计 gate 采样；没有将不同运行的独立峰值相加。审计从原 main 入口观察，框架初始化后 body 前 paid/native 均为 0。实际 native 合计 arm64 32KiB、x86_64 16KiB。92B 来自框架启动前产品固定费用计数，仍需完整 static 容量清点，不能把该式当作全部 owned 的独立总账本。

每次运行先在实际产品政策下分配/释放 12,345B，故意仅将**审计观察界**设为 93B，独立观察到 peak12,437B / violation1；随后复位为原 body 的观察界，实际 violation0。产品限额没有因控制而改变。

审计保留固定 262,144 指针 / 65,536 符号表，只存原 classified paid 请求，并快速排除直接来自 libfontconfig 的未归类分配。框架初始化仍完整运行；Qt/OS、usable capacity、TLS、未归类 owner 和 allocator 内部瞬时容量均未取得此界资格。审计源码、二进制、实际库及 before/after 身份由 [冻结记录](final-freeze.json)绑定。

## 真实拒绝与默认退出

| 原拒绝族 | 真实拒绝 | 控制 | 进程 actual exit0 |
|---|---:|---:|---:|
| provider registration/source-control/alias，两架四 bpp | 64 | 24 | 2 |
| operation/COW，两架 | 468 | 6 | 2 |
| worker/monitor pthread_create EAGAIN，两架 | 12 | 4 | 4 |
| 原九族 lifecycle，两架 | 497 | 18 | 515 |

以上合计 **1,041 次已处理真实拒绝、52 个控制、523 个拒绝矩阵进程 actual0**；加四个容量进程，primary 527 actual0。[原拒绝结算](fault-summary.json)与 [lifecycle 默认退出结算](lifecycle-default-summary.json)保留全部原始日志和身份。

provider、operation 和 native 探针本身未替换 terminate/SIGABRT。lifecycle 先复验带审计终止处理器的原 515 进程，再仅删除两个处理器及相应注释，以相同九族、原发现点和原 body 重新执行 515 进程；两个矩阵均 497 fault / 18 control / actual0。精确派生见 [四行删除](lifecycle-default-derivation.patch)。后者证明这些拒绝被处理后正常退出，**没有执行或证明默认 abort 能退出，也没有回收十三个历史 UE**。

按实际发现的第一/最后 paid 调用点拒绝；read/purge/close 的 malloc 目标仍为 0，只记控制；operation 每架一个 absent site 保留。worker/monitor 各三次连续 EAGAIN 均未接纳、无 callback、原 paid/process 费用不增长，随后原成功控制通过。不能外推未列出的 fault、provider/fence/caller 联合永久拒绝域。

## 捕获释放复核与未关闭出口

[原 captured release 复核](captured-release-review.json)沿 metadata unlink、同步 publication claim、history 原 rescan、epoch 原 node extraction、closeSession 与后台 foreground-I/O 政策检查当前 Store 路径。没有建立新的 allocator 拒绝自保环反例，因此本轮没有改产品或增加同义测试。独立 coordinator oracle 入口与人为 operational=false 控制不取得 Store owner gate 的序列化资格。

完整 manager TSAN 原 body（48 任务、16 线程、100000 cycles、seed12345）仍在单次执行，实际使用隔离插桩 QtCore，无 suppression；outer7200s，单函数 watchdog10800000ms。[不可变观察点](manager-live-checkpoint.json)和 [前缀快照](manager-prefix-checkpoint.log)只记录正在运行的事实，1098 passing prefix 没有 Totals，**不算完整 body 通过或 deadlock 证明**。实际终点由该次 runner 后续结果另行结算；活动日志不纳入本冻结包。

十三个历史 UE 仍实际存在，见 [进程观察点](known-ue-checkpoint.txt)。本轮未清理宿主、app-server 或重启。两个早期容量审计在框架字体初始化中未到 body，独立停止 actual-15/reaped，旧审计源码快照和停止记录保留；不能当容量失败或通过。

剩余仍按四组领取：

1. 全 owned request/capacity/control/TLS/static、reserved/live/并存 peak 到 physical free 的独立逐笔账本及总硬界，含首次 native 查询与外部 span 合并。
2. 有限矩阵之外的真实 node/control/task 拒绝，read/capture/history/publication/retirement/close、晚 fence 和 caller 的联合终点。
3. Qt/OS/usable/TLS 及非 Darwin 实际平台资格；本地 dual-arch macOS 结果不能替代 Linux/Windows。
4. 完整可观测 manager TSAN 实际终点与十三 UE / 宿主默认 abort 出口。有限已处理拒绝的默认退出不再重复领取。

M6/M7/M8 正式 0/3，persistent 默认关闭。CP5 continuation/fairness 和 CP10 正式性能保持原包。

## 身份与复现入口

[final-freeze](final-freeze.json)核对 123 源文件与当前产品 commit blob（121 编译输入、两派生 JSON），169 份前轮依赖保持及本轮运行/审计输入的并集；依赖哈希保持不转授前轮测试资格。原 ratchet 与图保持，未重生成产品 JSON。`reuse_native.py`、`reuse_probe.py`、`reuse_lifecycle.py`只复用活动证据中的原 builder/runner 与精确产品 flags；父脚本 SHA 和转接差异单列。`run_capacity.py` 与 `run_native_monitor.py`复用冻结二进制， before/after 验证实际源码和库。`freeze_qualification.py`逐笔核对 raw result，不读取 archive，不把未退出 manager 纳入通过数。

活动七文档的 2,583 个本地链接核对通过，archive 链接跳过且未读取。首轮核验器把源文件的 `:行号` 后缀误作文件名，其原始结果保留；解析修正后错误为 0。[最终文档核验](docs-verification.json)不将核验器错误写成产品失败。
