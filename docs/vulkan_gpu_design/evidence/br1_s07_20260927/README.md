# S07 首批开发验证：空 domain journal 对账

本批落实 [92 §10.2、§15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md:284) 的无变化路径；映射入口为 [S07](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03_write_plans_and_hot_path.md:25)。没有实现 M6/M7，也没有授予 S07 整项、M8 或 BR1-PERF 资格。

## 修改与安全边界

OwnerLedger 用隐式共享 QHash 快照替代每次构造 provider values 列表，provider 调用仍在 owner gate 外。Tiles3 provider 增加原子 journal 非空提示，与插入、精确 acknowledge、untrack 同锁更新；读到 false 只代表本次观察为空，不缓存 owner 的已见序列，也不改变 domain pre-admission。未知 provider 保守返回 true，继续原读取。

有变化时仍复验物理 slot、bytes 和 revision；未登记 backing 的观察继续保留，旧 acknowledge 不能清掉新 revision。多 owner 预算接受仍在 domain 发布前完成。空路径复杂度随 provider 数量 P，不随页面 N；本批没有取消真正首写所需的 reserve，也没有改变 pending/session 生命周期。

## 源码与实测身份

- 基础 HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。
- 最终累计补丁：[source.patch](checks-01/source.patch)，SHA256 `7730b939dd4894f1b668b4934b50653f0410101e86da7fa7db6a1a93fc9f30a2`；包含此前 S01 改动。
- 矩阵 [identity.json](checks-01/identity.json) 与 [manifest.json](checks-01/manifest.json) 记录构建配置、实际 image dylib / 测试 binary 哈希、命令、seed、时间及返回值。沿用 [S01 开发矩阵脚本](../br1_s01_20260927/run_checks.py)，其 identity.scope 保留旧 S01 标签；本批范围以保存的补丁、实际命令和本说明为准。
- 探针在审计 JSON/README 刷新之前运行，完整补丁哈希为 `03421195565fa086b36c2a46e311bdf4c63fcf2e763c461cb38e09742c81430b`。没有把两种完整补丁身份混为一谈：[source-relationship.json](source-relationship.json) 逐项证明所有 libs/plugins 修改段、实际 image dylib、CMakeCache 和 compile_commands 与最终矩阵一致。各自原始补丁和身份均保存。

## 语义与构建结果

| 检查 | 结果 |
|---|---|
| arm64：7 个 PageStore + painter / TileDataStore / DataManager / Transaction | 1,519 passed，0 failed，0 skipped |
| x86_64：相同 11 个目标 | 1,519 passed，0 failed，0 skipped |
| 总数 | 3,038 passed，含 QtTest init/cleanup 和参数化行 |
| architecture gate | 21 manifest、21 ownership、16 census、1,472 API、13,805 reverse edges、19 intrusion files；通过 |
| 工具自测 | 6 passed |
| ratchet / 结束身份 | 与受保护 HEAD 相同；运行结束无待构建工作且源码补丁不变 |

新增 `cleanDomainJournalSkipsSnapshots` 对 1,000 次空同步断言 journal 调用增量为零，并覆盖保守默认和未附着预算的拒绝。`dirtyDomainJournalRetainsUnregistered` 覆盖 1/4/8/16 BPP 的登记前观察、旧 acknowledge 与 swap-out/in。`domainProviderSnapshotSurvivesRegistration` 在 provider 回调中新增注册，验证锁外执行与快照稳定性。原 stale snapshot、多 owner 未准入拒绝和 swap-in 失败用例保留并通过。

[首次构建](build-01.log)、[定向运行](targeted-01.log)、[调用图生成](callgraph-generation.log)、[checkpoint 刷新](source-checkpoint-refresh.log)及[最终矩阵](checks-01/manifest.json)均保留。本批无失败运行；之前 S01 的失败仍在原目录，不被覆盖。

## 实际分配探针

[domain-sync-allocation-probe.cpp](domain-sync-allocation-probe.cpp) 直接调用生产 OwnerLedger/Tiles3 provider，使用既有 macOS allocator interposer；不使用生产开关或替代实现。[脚本](run_domain_probe.py) 保存编译/链接/运行命令和哈希，已有输出目录会拒绝覆盖。

| 架构 | 共享 Qt 正控制 | 测量区间 |
|---|---|---|
| arm64 | 4 次分配 | P=1/4/16 各 1,024 次：分配 0、字节 0、释放 0 |
| x86_64 | 4 次分配 | P=1/4/16 各 1,024 次：分配 0、字节 0、释放 0 |

原始输出与身份：[arm64](probe-arm64-01/identity.json)、[x86_64](probe-x86_64-01/identity.json)。测量区间只包含预热后的空 domain 同步，不包含注册、dirty journal 或整个 stroke；没有提供耗时提升比例。也未重新运行 Vulkan、TSAN、publication install allocator、产品 replay 或正式 upstream 性能门。

重跑时在 workspace 根执行 `python3 docs/vulkan_gpu_design/evidence/br1_s07_20260927/run_domain_probe.py arm64 02`（x86_64 同理）；完整矩阵沿用上述脚本并传入一个新的绝对输出目录。实际重新运行前先核对当前源码、审计与二进制身份。
