# BR1 D2 定向阶段与事务起点实验

配套报告：[55](../../55_br1_d2_phase_measurement_and_atomic_transaction_begin_20260920.md)。这些是 CPU/CpuRam 切片诊断，
不是主干 M 不劣性、隔离 K 吞吐、P95/P99 或 GPU/UMA 资格。BR1-PERF 仍未结清。

## 版本与环境

- 内层 base `f5fbbde618df6fb4e1068ace7381c339a70dd4c0` 加现有未提交改动；机器/构建配置沿用 53，实际运行 arm64。
- before：D1 + opt-in 分阶段诊断/固定页集 fixture；匿名事务仍导出完整 manifest 以取得 epoch。
- after：增加 `beginCurrentTransaction()` 并接入匿名事务起点；没有实施 prepared metadata batch，也没有关闭 state/proof 校验。
- `before-artifact-sha256.txt`、`after-artifact-sha256.txt` 分别记录源码/二进制/动态库身份。历史 D1 hash 不再描述此二进制。
- `after-tracked-image.patch`、`after-untracked-image.tar.gz` 是最终 `libs/image` 源码切片；内层仓库相对路径，不是完整
  全仓/依赖构建包。before 没有另存完整源码归档，不能把 base commit 当作精确 before 源码。
- `evidence-artifact-sha256.txt` 校验源码归档、分析脚本及全部 plain/profile 性能原件；不覆盖旧版本 hash。

## 原件和覆盖

- `fixed-initial-correctness.log`：36 passed / 6 failed。初版误把历史 setup 改变 uniform 缓存后的相同内容当作零工作。
  保留该性能假设失败；修订 fixture 分开 `noop`（明确 warmup）和 `identical`（无 warmup），后者冗余 adoption 如实计入。
- `fixed-diagnostics-correctness.log`、`fixed-after-correctness.log`：52 个数据桶 + init/cleanup，均 54 passed。
- `reference-diagnostics.log`：32 passed；`reference-after.log`：33 passed，增加原子 current-base/历史读取/零 manifest 导出测试。
- `foundation-after.log`：24 passed；`full-tiles-after.log`：完整 tiled-manager suite 88 passed，含新增 52 桶。
- `before-fixed-01.log` 至 `05`、`after-fixed-01.log` 至 `05`：每桶 256 次、单线程、无 scope 计时的操作区间；含 setup 的
  Qt 总时长另列，不能混作 operation latency。每个 N/K/H/bpp/mode 五次重复，before 全部先于 after，非交替、非主干配对。
- `before-fixed-profile.log`、`after-fixed-profile.log`：独立 opt-in 阶段计时；原生 PageStore manifest 导出在 after 的操作区间为 0。
- `before-stress-01.log` 至 `05`、`after-stress-01.log` 至 `05`：原混合 stress，seed 12345、8 workers/8 threads、1 BPP，
  无 profiler/scope；Qt elapsed 与 `/usr/bin/time -lp` 分开。所有计时顺序运行，不与构建或其他 benchmark 并发。
- `before-stress-profile.log`、`after-stress-profile.log`：外层 `BR1_PROFILE` 与新 `BR1_STAGES`；scope 只过滤目标 manager，
  不含 bitBlt 临时 source manager。开启细粒度阶段计时有明显扰动，不能作为性能 Pass/Fail。
- `analysis.json` 与 SVG 由 `analyze.py` 复算，检查 52 桶、工作量、完成日志和重复次数。每个 phase 是调用区间，未消除
  时钟端点成本；CPU 略高于 wall 不能解释为负锁等待。`*_owner_wait` 是入口区间，不是完整锁等待/持锁采样。

## 固定 workload 与计时端点

- 主 sweep：N=64/1024/4096，K=1/16，H=0/4，4 BPP，alias/noop/identical/real，共 48 桶；另 4 桶覆盖 8/16 BPP 真写。
- `alias` 每轮换色整页覆盖；`real` 每页仅改一条 scanline，真实修改 K 页且保持其他 63 行；这不是 isolated K。
- `noop` 先在区间外明确恢复当前 uniform backing 缓存，再重复相同 fill；warmup 时间及 adoption 数单列。
- `identical` 不做该 warmup；字节逻辑变化为 0，首次额外 adoption/commit 仍计入。日志分别记录
  `logical_changed_pages`、`canonical_changed_pages` 和 `submitted_page_visits`，不把同字节版本改写当像素带宽。
- H 个 distinct retained roots 在 setup 建立；正确性读取在 operation 外验证旧 bytes，随后 release 所有 roots 的时间单列。
  live version 终值不是累计创建/峰值，更不是异步长期 drain 有界证明；所有 release 工作不能从完整产品 E 扣除。
- scope 的 owner-filter、thread-local/nested 生命周期由 Reference 测试约束。禁用时不读时钟、不加诊断锁/原子统计；
  TLS 查询与分支仍存在。关闭诊断的五次 stress 只检查明显扰动，不证明绝对零开销。

## 复现

以下从外层仓库根目录执行。重复计时应保存新日志，不覆盖原件；profile 与 plain 分开运行。

```sh
.venv/bin/cmake --build krita/_build-br0-cpu --target kis_tiled_data_manager_test KisPageStoreReferenceTest KisPageStoreFoundationTest -j6
krita/_build-br0-cpu/bin/KisPageStoreReferenceTest
krita/_build-br0-cpu/bin/KisPageStoreFoundationTest
krita/_build-br0-cpu/bin/kis_tiled_data_manager_test
env KIS_BR1_FIXED_LOOPS=256 KIS_BR1_STAGE_PROFILE=0 krita/_build-br0-cpu/bin/kis_tiled_data_manager_test testPageStoreFixedPageWork
env KIS_BR1_FIXED_LOOPS=256 KIS_BR1_STAGE_PROFILE=1 krita/_build-br0-cpu/bin/kis_tiled_data_manager_test testPageStoreFixedPageWork
env KIS_BR1_SEED=12345 KIS_BR1_THREADS=8 KIS_BR1_PROFILE=0 KIS_BR1_STAGE_PROFILE=0 /usr/bin/time -lp krita/_build-br0-cpu/bin/kis_tiled_data_manager_test stressTest
env KIS_BR1_SEED=12345 KIS_BR1_THREADS=8 KIS_BR1_PROFILE=1 KIS_BR1_STAGE_PROFILE=1 krita/_build-br0-cpu/bin/kis_tiled_data_manager_test stressTest
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_d2_20260920/analyze.py
shasum -a 256 -c docs/vulkan_gpu_design/evidence/br1_d2_20260920/after-artifact-sha256.txt
shasum -a 256 -c docs/vulkan_gpu_design/evidence/br1_d2_20260920/evidence-artifact-sha256.txt
```
