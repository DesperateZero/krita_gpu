# BR1 收敛第三批：共同写入基准准备

对应 [84](../../84_br1_full_optimization_convergence_and_cleanup_20260923.md) 的 C2 局部执行。
目录 `c3` 是第三个批次，不表示 C3 读侧已验收；不授予 BR1-PERF Pass。
`manifest.json` 绑定操作前后源码摘要、当前调用图/checkpoint、实际二进制及最终日志；前两批证据未修改。

## 变更与退出的重复实现

- native/generic/alias 共用 `prepareWriteBaseLocked`：exact base、sealed proof、removal/default descriptor、generation/token。
  删除 Store 中三套对应逻辑及 `latestPreparedVersion`；不增加生产文件、长期状态或第二套可见性权威。
- generic 不再导出整页历史，也不再为了写默认页先物化 before-image；目标直接按 descriptor 初始化。
- native/generic 共用 provider 解锁期间默认 authority 变化的复验；两者保留各自同步/异步 completion 边界。
- 虚拟默认登记由已有 PublicationCoordinator 承担；首次旧事务访问必须先登记当前 root 的 Published head，
  旧 revision 只作为 Historical。既有 StateMachine 拒绝 Historical 写入的规则不变。

生产新增 208 / 删除 286，净减 **78**；测试新增 92 / 删除 18，净增 **74**。
pagestore `.h/.cpp` 合计 **32,872**；Store.cpp **4,047**；三批生产累计净减 **677** 行。
按本批操作前独立快照比较，不把整个 dirty worktree 当作本批变更，也不以测试/文档增长抵扣生产数字。

## 验证结果

- Foundation / Completion / Reference：28 / 11 / 303。
- ReadBaseline / ResidentRead / CpuMutation / PhysicalClaim：41 / 32 / 482 / 30；合计 **927**，七个 ctest 全过。
- 定向 totals **34**：native/generic 默认目标唯一分配；准备时读者物化默认；旧事务首次 native/generic/alias 写拒绝并清理；
  并发页/事务 claim；H=0/7/63 × bpp=1/4/8/16 的 generic bounded base 查询和 sealed 内容延续。
- Painter **99**；tiles3 全套 **334**，seed 12345，包含 stress。最终日志无 FAIL/SAFE ASSERT。
- 当前 Clang 图：**1,611 APIs / 13,680 edges / 14 callbacks / 85 TUs**；physical gate production/test **0/20**。
  刷新 checkpoint 前遵守原外部侵入上限，architecture gate 通过；固定 convergence 起点未刷新。

两处旧注入点跟随删除的 before 分配迁到真实 `prepareWrite`：仍验证 preparation/claim 阻止竞争、commit 和 abort，
此时 provisional request 已建立，故数量由 0 改为 1。旧 explicit manifest 没有 surface 元数据的兼容用例保持通过。
默认页新用例按现有 StateMachine 的冲突规则检查拒绝，不通过扩展 Historical 写权限使测试通过。
保留 swap/资源/插件环境告警。QtTest totals 包含 init/cleanup 与数据行；并行索引/回归耗时不作吞吐比较。

## 复现

工作目录 `/Users/apple/krita_gpu/krita`：

```sh
/Users/apple/krita_gpu/.venv/bin/ninja -C _build-br0-cpu \
  KisPageStoreCpuMutationTest KisPageStoreFoundationTest KisCompletionRegistryTest \
  KisPageStoreReferenceTest KisPageStoreReadBaselineTest KisPageStoreResidentReadTest \
  KisPageStorePhysicalClaimTest kis_tiled_data_manager_test kis_painter_test
env QT_QPA_PLATFORM=offscreen /Users/apple/krita_gpu/.venv/bin/ctest \
  --test-dir _build-br0-cpu -R '^libs-image-(KisPageStore.*|KisCompletionRegistryTest)$' \
  --output-on-failure -j1
env QT_QPA_PLATFORM=offscreen _build-br0-cpu/bin/KisPageStoreCpuMutationTest \
  staleFirstWriteKeepsCurrentDefault virtualDefaultOnlyAllocatesTarget \
  defaultMaterializedDuringWritePreparation concurrentWritePreparationClaims \
  genericPreparationProtectsTransactionBeforeRequest nativeMetadataWorkIgnoresRetainedHistory
env QT_QPA_PLATFORM=offscreen KIS_BR1_SEED=12345 \
  arch -arm64 _build-br0-cpu/bin/kis_tiled_data_manager_test
env QT_QPA_PLATFORM=offscreen \
  KIS_TEST_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install \
  KIS_TEST_PLUGIN_PATH=/Users/apple/krita_gpu/krita/_build-br0-cpu/bin \
  arch -arm64 _build-br0-cpu/bin/kis_painter_test
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py
```

尚未闭合：统一 provider 执行/overlay seal、entry/cold 双层状态与 pending/semantic selector，native 析构时 Debt 满的
退出保证，增量预算和有限生产配置，以及 C3 读侧/C5 metadata 全面收敛。结构性减少 allocation/query 不等于性能资格。
