# BR1 收敛第二批：共享终结与正确性检查点

对应 [84](../../84_br1_full_optimization_convergence_and_cleanup_20260923.md)。不是全链路 C2–C5 或性能资格验收。
`manifest.json` 绑定本批前后源码摘要、当前调用图/checkpoint、实际测试二进制与日志；首批证据保持不变。

## 结果

- Foundation / Completion / Reference：28 / 11 / 303 passed。
- ReadBaseline / ResidentRead / CpuMutation / PhysicalClaim：41 / 32 / 474 / 30 passed；合计 919。
- 新定向回归：六条有限 Debt 数据行、一条并发 captured reader/commit/restore，含 init/cleanup totals 9。
- Painter：99 passed；tiles3 完整套件：334 passed；最终日志均无 FAIL/SAFE ASSERT。
- 独立 stress：seed 12345、8 线程通过；该日志早于最后的纯收敛调整，最终源码以完整 tiles3 日志为准。
- architecture：1,610 APIs、13,662 edges、14 callbacks、85 TUs；physical gate production/test 0/20。

首批 stress 的第一个 history commit 拒绝来自 metadata 准备期 revision 冲突，定位时观察到
`metadata changed while preparing publication storage` / `metadata changed while reserving publication capacity`。
`stress-diagnostic-excerpt.txt` 只是中间诊断版本日志节选（临时 trace 已删除），不冒充最终二进制输出。
最终提交/恢复使用 typed conflict outcome 进入原重准备循环；预算耗尽及非法输入仍失败。
QtTest stress 现在把 SAFE ASSERT 视为失败；没有减少循环数、线程数或删除压力操作。

本批生产新增 189 / 删除 265，净减 76；测试净增 134。两个批次生产累计净减 599；无新增生产文件。
仍未完成：所有准备/seal 协议统一、native 析构遇 Debt 满的退出保证、增量预算/生产限额、读侧和 metadata 全面收敛。

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
env QT_QPA_PLATFORM=offscreen arch -arm64 _build-br0-cpu/bin/KisPageStoreCpuMutationTest \
  publicationWhileCapturedReadersChange consumedGenericLeaseCanRetryAbort partialCancellationRetiresBeforeRetry
env QT_QPA_PLATFORM=offscreen KIS_BR1_SEED=12345 \
  arch -arm64 _build-br0-cpu/bin/kis_tiled_data_manager_test
env QT_QPA_PLATFORM=offscreen KIS_BR1_SEED=12345 \
  arch -arm64 _build-br0-cpu/bin/kis_tiled_data_manager_test stressTest
env QT_QPA_PLATFORM=offscreen \
  KIS_TEST_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install \
  KIS_TEST_PLUGIN_PATH=/Users/apple/krita_gpu/krita/_build-br0-cpu/bin \
  arch -arm64 _build-br0-cpu/bin/kis_painter_test
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py
```

日志保留 swap 回退、资源/插件等环境告警；这些不是 SAFE ASSERT。QtTest totals 含 init/cleanup 与数据行。
测试与索引曾并行运行，耗时不作性能对比。没有运行 upstream M/K/X/E 配对，不授予 BR1-PERF Pass。
