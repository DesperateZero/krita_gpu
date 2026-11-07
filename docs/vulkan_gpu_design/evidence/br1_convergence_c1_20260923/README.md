# BR1 收敛首批正确性检查点（2026-09-23）

对应 [84](../../84_br1_full_optimization_convergence_and_cleanup_20260923.md)。不是性能资格，也不是全链路验收。
工作树未提交；未改写任何历史性能证据。`manifest.json` 绑定本次当前源码图/checkpoint、测试二进制和原始日志。

## 结果

| 检查 | 结果 |
|---|---|
| Foundation / Completion / Reference | 28 / 11 / 303 passed |
| ReadBaseline / ResidentRead / CpuMutation / PhysicalClaim | 41 / 32 / 467 / 30 passed |
| Painter | 99 passed，正确配置后无 SAFE ASSERT |
| tiles3 data manager 完整套件 | 334 passed，但有 1,984 条 SAFE ASSERT；不接受为通过 |
| 独立 stress | 3 passed，但超过 2,000 warning 上限；同样不接受 |
| architecture | 当前 graph/source gate 通过；六类陈旧/扩张负例拒绝 |

QtTest totals 含 init/cleanup 与数据行。PageStore/Completion 和 Painter 日志无 FAIL/SAFE ASSERT。
tiles3 首个告警是 `KisTiledDataManager::commit()` 的 history commit 拒绝，完整运行随后还有 exact-generation
无有效 replica 的读/写失败。根因未确认；无法根据本检查点区分既有问题与本批回归。
测试目前只警告而不失败，此处显式按失败门槛记录。首次 Painter 因未设测试 prefix 在 QtTest 正文前中止，
补用仓库现有测试环境重跑，无代码修补。LLDB 尝试未进入测试正文，已结束自建调试进程，不构成根因证据。

## 复现命令

工作目录 `/Users/apple/krita_gpu/krita`：

```sh
/Users/apple/krita_gpu/.venv/bin/ninja -C _build-br0-cpu \
  KisPageStoreReferenceTest KisPageStoreCpuMutationTest KisPageStorePhysicalClaimTest \
  KisPageStoreResidentReadTest KisPageStoreReadBaselineTest KisPageStoreFoundationTest \
  KisCompletionRegistryTest kis_tiled_data_manager_test kis_painter_test
env QT_QPA_PLATFORM=offscreen /Users/apple/krita_gpu/.venv/bin/ctest \
  --test-dir _build-br0-cpu -R '^libs-image-(KisPageStore.*|KisCompletionRegistryTest)$' \
  --output-on-failure -j1
env QT_QPA_PLATFORM=offscreen arch -arm64 _build-br0-cpu/bin/kis_tiled_data_manager_test
env QT_QPA_PLATFORM=offscreen arch -arm64 _build-br0-cpu/bin/kis_tiled_data_manager_test stressTest
env QT_QPA_PLATFORM=offscreen \
  KIS_TEST_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install \
  KIS_TEST_PLUGIN_PATH=/Users/apple/krita_gpu/krita/_build-br0-cpu/bin \
  arch -arm64 _build-br0-cpu/bin/kis_painter_test
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py
```

收集新日志时使用新输出目录，不覆盖本检查点。验收还必须检查日志中的 SAFE ASSERT，不能只看退出码或 totals。
本次未运行 upstream M/K/X/E 配对；不要将上述测试时长解释为性能变化。
