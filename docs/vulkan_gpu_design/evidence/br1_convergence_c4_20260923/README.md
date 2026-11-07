# BR1 收敛第四批：整层删除、瘦身与共同读协议

对应 [84 第四批](../../84_br1_full_optimization_convergence_and_cleanup_20260923.md)。
`c4` 是批次编号，不表示 C4 预算阶段完成；不授予 BR1-PERF Pass。

## 已执行

- 移除无外部生产调用的独立 H/V LineIterator 原型、构建项；原负坐标/跨页回归迁到真实 tiles3 H/V 入口和 captured scope。
- 移除空 handoff 实现、未消费的 context/plan、每 entry 的空 binding/budget/coverage；保留真实资源持有者及校验。
- CPU session 的 read/before 与业务 iterator/backend 共用现有 `KisPageStoreReadPage`，统一 native/fallback 和释放协议。

生产 `.h/.cpp` **+63/-710，净减 647**；CMake -1；测试 **+61/-19，净增 42**。
pagestore **32,225** 行；四批生产累计净减 **1,324** 行。不包含测试、脚本、文档或证据体积。
删除两个生产文件，无新生产文件。删除文件的原件保存在 `retired/`，可恢复，不参与生产构建。
`retired/KisPageWriteCoordinator_p.h` 保存删改前布局，不能当作当前有效 schema。

arm64/x86_64 均由实际 compile_commands 的 Clang 参数测得：intent **48 → 24 B**，entry **280 → 104 B**。
当前静态上限为 intent 32 B、entry 128 B；并非只变更上限数字。
`deletion-proof.json` 保存删除前当前图中 45 项原型/空 claim API 的调用、构造和 override 证据以及原图 hash。
原型构造不存在外部生产调用；测试依赖已迁移，不删除真实业务测试以制造死代码。

## 最终验证

- Foundation / Completion / Reference：28 / 11 / 303。
- ReadBaseline / ResidentRead / CpuMutation / PhysicalClaim：41 / 32 / 484 / 30，合计 **929**；七个 ctest 全过。
- Reference 定向 totals **4**；CPU 定向 totals **7**。新增两行失败注入验证 request 清理、重试、cursor/operation pin 寿命、
  root 变化后的 captured cache miss；既有 Busy、默认 before-image、captured overlay 断言保留。
- Painter **99**；tiles3 全套 **334**（seed 12345，包含 stress）；最终日志无 FAIL/SAFE ASSERT。
- Clang 当前图 **1,560 APIs / 13,587 edges / 14 callbacks / 84 TUs**；physical gate production/test **0/20**。
- 首次静态 gate 拒绝旧 schema 名称变化；审计规则改为实际更紧布局、禁止空资源字段回流和提前 handoff。
  放宽 entry 上限、恢复空 budget、提前返回 handoff 三种内存负例均被拒绝。外部侵入上限和固定起点未提高/刷新。
- 最终依赖检查 `ninja: no work to do`，源码/checkpoint/gate 一致；历史证据不改写。

保留资源/插件及 swap 环境告警；不将其与 SAFE ASSERT 混淆。QtTest totals 含 init/cleanup 和数据行。
构建为 RelWithDebInfo、x86_64/arm64 universal；回归和索引可并行，耗时不作性能比较。
`manifest.json` 绑定前后源码/删除文件、构建项、审计脚本、测试二进制、日志及当前图/检查点。

## 复现

工作目录 `/Users/apple/krita_gpu/krita`：

```sh
/Users/apple/krita_gpu/.venv/bin/ninja -C _build-br0-cpu \
  KisPageStoreCpuMutationTest KisPageStoreFoundationTest KisCompletionRegistryTest \
  KisPageStoreReferenceTest KisPageStoreReadBaselineTest KisPageStoreResidentReadTest \
  KisPageStorePhysicalClaimTest kis_tiled_data_manager_test kis_painter_test
env QT_QPA_PLATFORM=offscreen /Users/apple/krita_gpu/.venv/bin/ctest \
  --test-dir _build-br0-cpu -R '^libs-image-(KisPageStore.*|KisCompletionRegistryTest)$' --output-on-failure -j1
env QT_QPA_PLATFORM=offscreen _build-br0-cpu/bin/KisPageStoreReferenceTest \
  randomAccessorMatchesTiles3AcrossNegativePageBoundary freshWriteSelectorAndBackingBudgetAreBounded
env QT_QPA_PLATFORM=offscreen _build-br0-cpu/bin/KisPageStoreCpuMutationTest \
  sharedReadFailureReleasesOnlyExpiredPins capturedOverlayGenericSessionKeepsExactVersion \
  busyIsNotAMaterializationFallback nativeSessionDoesNotMaterializeDefaultBeforeImage
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

布局测量将实际 WriteCoordinator 编译命令的源文件替换成 `#include WRITE_HEADER` 与两个 `sizeof` 常量，
分别指向旧/新 header，用 `-arch arm64/x86_64 -S -emit-llvm -o -` 读取常量；不修改生产或执行二进制。

剩余问题明确保留：provider 执行/overlay seal、实际 entry/cold 生命周期、pending/semantic 策略接线、有限 Debt 退出保障，
其余读 cache/兼容层，以及预算/metadata 全面收敛。未实施 handoff，不以删除空 schema 认领功能完成。
