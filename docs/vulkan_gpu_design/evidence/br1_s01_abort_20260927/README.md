# S01 第二批开发验证：直接取消主像素事务

本证据对应 [92 §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:474) 的部分实施，日期 2026-09-27。S01、M6/M7/M8 和 BR1-PERF 均未因此完成。

## 源码和运行身份

基础提交为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`；实际源码为该提交加 [source.patch](checks-01/source.patch)，补丁 SHA256 为 `88546fcf3d29a70cd7cb36f88c0029b31d75aa05ea2bff6272bbd2d1df0b7f19`。补丁包含 S01 第一批与本批的累计改动，不能用 HEAD 单独标记实际运行源码。

[identity.json](checks-01/identity.json) 保存构建配置、编译数据库、image dylib 与 11 个测试 binary 的哈希；[manifest.json](checks-01/manifest.json) 保存 22 个测试进程的完整命令、环境、起止时间和返回值。构建为 RelWithDebInfo、arm64/x86_64 双架构、Vulkan OFF，seed 为 12345。运行沿用 [开发验证脚本](../br1_s01_20260927/run_checks.py)，结束确认源码补丁不变、构建无剩余工作。

## 修改与验证关系

| 修改 | 实际测试与边界 |
|---|---|
| manager 先准备兼容索引/extent，再 abort 并交换；保留原 default backing | `testPageStoreAbortUnderBudgetPressure`：1/4/8/16 BPP，硬物理预算饱和仍能恢复 default，不增加 commit；旧 memento 不得取消新事务 |
| TransactionData 直接取消、重复取消幂等、取消后不得提交 | `testDirectAbort`：no-op、全清、移除与新增、default 改变，分别覆盖 SuppressUpdates；比较像素、default、region、bounds、offset，并断言取消区间 CommitRootPublication 为零 |
| exact reader 独立保活 | 同一测试保留取消前的 reader，取消后仍读到捕获内容；当前设备恢复开始值 |
| 拒绝不丢所有权，取消只可重试 | `testAbortWithLiveWriter`：持有另一页 writer 时拒绝；释放后重试成功，新事务仍可提交和 undo |
| interstroke 与内容上下文恢复 | `testAbortInterstrokeData`：继续、替换、清除三行；`testAbortWithUnswitchedFrame`：事务 frame 与当前 frame 不同；`testAbortSelectionCache`：outline 与选区边界恢复 |

取消前准备的是完整兼容索引，仍为 O(N)，并占用 manager 外层锁。保留 default backing 避免取消时重新申请像素 backing；这不等于兼容元数据零分配或所有资源压力下都能成功。interstroke 辅助 command 仍使用 legacy 终结/undo 协议，不能把“主像素没有 commit”外推到所有辅助设备。

## 结果与保留的失败

| 检查 | 结果 |
|---|---|
| arm64：7 个 PageStore + painter / TileDataStore / DataManager / Transaction | 1,513 passed，0 failed，0 skipped |
| x86_64：相同源码与目标 | 1,513 passed，0 failed，0 skipped |
| 总数 | 3,026 passed；含 QtTest init/cleanup 和参数化行 |
| architecture gate | 21 manifest、21 ownership、16 census、1,469 API、13,757 edges、19 intrusion files；通过 |
| 工具自测 | 6 passed |
| intrusion ratchet | 与受保护 HEAD 完全一致，未放宽 |

[build-01.log](build-01.log) 保留测试误用 `KisPixelSelection::exactBounds` 私有成员的编译失败；改为公开 `selectedExactRect` 后，[build-02.log](build-02.log) 成功。首次 arm64 定向记录为 [transaction](targeted-transaction-01.log) 和 [manager](targeted-manager-01.log)，不与最终矩阵累计。调用图[生成](callgraph-generation.log)、源码 checkpoint [刷新](source-checkpoint-refresh.log) 和最终 [checks-01](checks-01/manifest.json) 分别保存，未覆盖第一批证据。

测试通过还要求日志没有 `SAFE ASSERT` / `FAIL!`；插件、颜色配置、swap 路径告警原样保留。未运行新的 Vulkan、TSAN、真实 allocator 探针、heap leak 检测、产品 stroke replay 或正式性能比较。旧 endAndTake/parent caller、析构、scheduler failure sink、取消进度与 delta/预算闭环以 92 的剩余出口为准。

重跑时在 workspace 根目录执行 `python3 docs/vulkan_gpu_design/evidence/br1_s01_20260927/run_checks.py /Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s01_abort_20260927/checks-02`；目录必须不存在，并先重新核对当前源码和审计产物。
