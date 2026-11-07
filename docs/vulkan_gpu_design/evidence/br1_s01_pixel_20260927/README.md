# S01 第四批：像素故障边界与写指针拒绝（2026-09-27）

本目录记录当前工作树的实现与未通过项，**不授予完整 S01、M6/M7/M8 或 BR1-PERF 资格**。唯一状态见 [92 §15](../../92_br1_m6_m8_execution_baseline.md:475)，逐入口设计/代码/验证关系见 [01b](../../br1_modification_guide/01b_pixel_failure_boundaries.md)。

## 实现范围

- `KisStrokeJobFailureContext` 是 job 栈上的 TLS 错误桥，不拥有事务、像素或取消回调。SimpleStrokeJobStrategy 仅为显式启用的 cancellable DOSTROKE 安装它，callback 退出后才交给既有队列取消；nested disabled job 与其他线程不继承故障状态。
- typed `applyPixelOperation(false)` 仍保留单操作回退。Painter 的普通 composite / fast copy、fixed selection，以及 DataManager 的 void 写/读入口报告不能返回给调用者的失败；已失败 job 停止相关后续写，不重放失败 operation。
- fixed/selection 临时缓冲改由作用域清理；分配/读取失败后的早退释放已取得的缓冲。
- `KisTileDataWrapper` 与 base iterator 通过 `tryWriteData` 取得可写指针。写 intent 成功但 canonical admission 拒绝时不再暴露 cached before-image；空指针不加页内 offset，兼容 partial copy 释放已取得的 source pin 后退出。
- ScopedPageStoreWriteBatch 的未完成早退向当前 job 上报，`finish(false)` 明确保持写失败，不以取消返回值替代写结果。此前底层 cancel 本来返回 false，因此不把该表达式整理夸大为已复现的“取消成功误报写成功”生产故障。

## 构建与源码身份

源码 HEAD 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`，工作树 [source.patch](checks-02/source.patch) SHA-256 为 `e29bc28303d63845e7e345b0beed4bf24ab4f941dbd52870329bf0b193925338`。补丁显式包括未进入 git index 的两个故障上下文文件和 UI test；不是只对 tracked diff 取哈希。

[identity.json](checks-02/identity.json) 绑定 CMakeCache、compile_commands、image/UI dylib 与 17 个测试 binary；RelWithDebInfo、arm64+x86_64、Vulkan OFF，seed=12345，offscreen。[manifest.json](checks-02/manifest.json) 保留每条命令、时间、退出码和 Qt totals。checks-01 与 checks-02 的源码补丁相同；中间对照重建后的 binary identity 单独记录，最终验证使用 checks-02 的库与测试。

最终调用图来自 `callgraph-generation-03.log`，source checkpoint 来自 `source-checkpoint-refresh-02.log`。结构门记录 21 manifest entries、21 ownership facts、16 runtime census groups、1,472 indexed APIs、13,836 reverse-call edges、19 external intrusion files。

[ratchet-check.json](ratchet-check.json) 对比 HEAD：已有 reviewed ceiling 没有提高，tile fields / duplicate state 未增加。DataManager 的类型名出现次数从 20 到 21，来自显式列举 Borrowed/Unavailable，仍在原本已审议的 21 上限内。原始 census **不是完全相同**；`ratchet-check-01.json` 保留首次以全等比较发现此差异的结果。manifest 没有修改。

## 故障验证与保留记录

新增验证覆盖九类 DataManager void 写的第二页拒绝/同 job 后续写阻止、history 取消与 foreign writer 保留；H/V/random × 1/4/8/16 BPP 的非零 offset 写准入拒绝；真实 painter/queue/transaction 的 direct/indirect × composite/fast copy/fixed selection × swap mapping/allocation/decompression 故障。主动返回 false 的 callback 保留之前 dab 并可继续完成与 undo。

UI fixture 运行真实 painter 合成和事务边界，不执行 brush paintop/freehand kernel；不是产品 replay 或性能测试。新增 TLS 的热路径成本、Vulkan、TSAN、install allocator 和正式性能未在本批重新取证。

`build-01.log` 保留新测试错误调用隐藏的 clear overload；`build-02.log` 保留误用 private swap fault hook；`build-06.log` 保留 H/V 构造参数类型错误，均已修正并重新构建。`development-arm64-manager-01.log` / `development-manager-debug-01.log` 保留 fixture 把栈对象交给 shared-pointer overload 引发的 invalid free；改用非 owning raw-pointer API 后消失。`development-arm64-manager-02.log` 保留实际生产反例：写 intent 成功后未经准入仍暴露旧页。修复后 `-03` / `-04` 验证通过。

## 扩展 iterator 回归尚未通过

`kis_iterators_ng_test` 的 vLineIter / hLineIter / randomAccessor 在存活 iterator 期间 clear，再修改 device offset / 创建新 iterator 后，exactBounds 包含旧内容。此项没有通过，不能将本轮称为全矩阵通过。

[对照脚本](run_iterator_control.py) 暂时将 DataManager、tile wrapper、base iterator 三个文件恢复为上一批证据中的内容，构建并运行同一 iterator 测试，然后在 finally 中恢复当前源码并重新构建。对照也得到 **8 passed / 3 failed，66 条逐颜色空间断言详情完全相同**；见 [comparison](iterator-control-comparison.json)、[控制源码/库身份](iterator-control.json) 和 `iterator-control-arm64.log`。这是三文件隔离对照，**不是完整 HEAD-only 基线构建**，不据此改写历史资格。

下一项修改必须把 `clearAll/cancelAnonymousLeasesForBarrier` 与 `beginIteratorMutationScope` 的 batch/client 生命周期一起收口，保留旧 raw pointer 的存储寿命但阻止旧写重新发布，并保持 offset、exact read 与 extent 一致。明确代码关系与验收位置已回填 01b；不通过提前销毁测试 iterator 来回避原语义。

`checks-01` 在 arm64 iterator 失败时停止，完整保留。`run_checks.py` 随后改为继续收集两架构所有 Qt 结果，最后仍以非零退出码报告任何失败；不跳过、豁免或改写失败结果。后续修复使用新的检查目录，不覆盖本轮失败记录。

## 最终结果（checks-02）

| 架构 | 目标数 | passed | failed | skipped |
|---|---:|---:|---:|---:|
| arm64 | 17 | 1,656 | 3 | 0 |
| x86_64 | 17 | 1,656 | 3 | 0 |
| 合计 | 34 个进程 | 3,312 | 6 | 0 |

其中 16 个原有 CPU/业务目标在两个架构均通过，共 3,296 passed；扩展 iterator 目标每架构 8 passed / 3 failed。**全矩阵未通过，脚本退出码为 1。** 失败完整保留，不计作新的阶段资格。

结构门、6 项 reachability 自测通过，最终 ninja dry-run 无待构建项，运行前后源码补丁一致，见 [result-summary.json](result-summary.json)。当前实现的独立新增故障场景已通过；clear/offset 与 live iterator 的生命周期问题仍须修复后重新跑全部 required targets。
