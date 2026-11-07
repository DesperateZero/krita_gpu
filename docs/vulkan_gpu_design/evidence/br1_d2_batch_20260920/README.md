# D2-B prepared metadata publication 实验

配套报告：[56](../../56_br1_prepared_metadata_publication_20260920.md)。所有性能结果均为 CPU/CpuRam **诊断**，
不是同主干 M 不劣性、isolated K、产品 E/tail 或 GPU/UMA 资格。

## 版本和证据身份

- nested base `f5fbbde618df6fb4e1068ace7381c339a70dd4c0` 加 dirty worktree，环境沿用 55：macOS15.7.3、Mac16,10、
  24GiB、arm64 运行、RelWithDebInfo/`-O2 -DNDEBUG`、Qt6.8，Vulkan 产品关闭。
- `before-*`：D2-A。before 动态库 SHA256 与 55 的 after 完全相同；本轮重新跑五次 fixed + stress plain，不复用旧 E。
- `after-*`：第一次 prepared publication，完整 invariant prepare + 三遍 claim/install/release；保留其局部慢化结果。
- `refined-*`：复用 coordinator-owned trusted invariant 边界（完整 transition-local guards），合并 install/release shard pass。
- 各版本的 `*-tracked-image.patch` + `*-untracked-image.tar.gz` 保存相对 nested repo 的 `libs/image` 源码切片，
  包含此前工作区改动；不是全仓库/依赖构建包。`*-artifact-sha256.txt` 标识对应二进制和关键源码，不能用 after hash
  校验 refined 二进制。原件保留、不覆盖旧日志。

## 运行与统计边界

- 同一 52 桶 N/K/H/BPP/mode fixture，每 plain run 256 操作，每版本五次；包含 4/8/16 BPP 真 scanline 修改。
- 设置、noop warmup、正确性读取、retained-root release 在 operation 区间外，按旧 fixture 单列，不能从产品 E 豁免。
- 每轮先 fixed 再 stress；版本依次 before → after → refined，非交替配对。没有编译/其他 benchmark 同时运行。
  固定 seed12345、8workers/8threads、1 BPP 的 stress 仍有调度导致的实际 canonical work 差异。
- profile 独立运行，不作性能 Pass/Fail；phase 是跨 worker 目标 manager 累加，不能相加作为进程 E。
- `commit_root` 在新版本只到 candidate root 验证通过；`commit_metadata_apply` 包含全批 revision/claim、candidate 安装
  和 descriptor 维护；新增 `commit_root_publication` 包含最后 root switch/return。preflight 现覆盖 write+default/removal，
  不能将旧同名 phase 当作同端点。新版本仍没有对 claim 复验与每页安装分别加时钟，避免进一步放大短区间扰动。
- `preparedPublicationPages`/`installedPublicationPages`/`rejectedPublicationInstalls` 是 coordinator lifetime 累计统计，
  与 immediate `apply()` 的 accepted/rejected/timer 分开，避免把批次安装数混进旧平均 decision timer 的分母。
- `MetadataPage` 新增 revision/claim/materialization count，tracked footprint 已包括内部记录尺寸；candidate/effects 是
  operation 临时内存，不等于 live page footprint，长期峰值与 drain 有界性仍需独立测量。
- 图表中旧 profile 来自 `../br1_d2_20260920/after-stress-profile.log`，仅提供历史方向对照，不冒充本轮新鲜配对。

## 复现

最终回归 `reference-refined.log` **38 passed**、`foundation-refined.log` **24 passed**、`full-tiles-refined.log` **88 passed**。
初版分别是 37/24/88，单独保留；initial/reference-batch 是更早骨架验证，不冒充最终覆盖。
refined 五次 stress median 15.118 s，before 16.037 s；小 K 真实写的反向结果见报告，未授予正式资格。
`analysis.json` 与图从三版本原件复算；脚本还检查 refined 固定桶的 manifest export 为零、每次成功 commit 都经过
root-publication phase、metadata install 的 page work 与 canonical changed pages 一致。

从外层根目录执行；计时必须保存新目录/前缀，不覆盖原件。无 profiler 和 profile 分开、串行运行。

```sh
.venv/bin/cmake --build krita/_build-br0-cpu --target kis_tiled_data_manager_test KisPageStoreReferenceTest KisPageStoreFoundationTest -j6
krita/_build-br0-cpu/bin/KisPageStoreReferenceTest
krita/_build-br0-cpu/bin/KisPageStoreFoundationTest
krita/_build-br0-cpu/bin/kis_tiled_data_manager_test
env KIS_BR1_FIXED_LOOPS=256 KIS_BR1_STAGE_PROFILE=0 krita/_build-br0-cpu/bin/kis_tiled_data_manager_test testPageStoreFixedPageWork
env KIS_BR1_SEED=12345 KIS_BR1_THREADS=8 KIS_BR1_PROFILE=0 KIS_BR1_STAGE_PROFILE=0 /usr/bin/time -lp krita/_build-br0-cpu/bin/kis_tiled_data_manager_test stressTest
env KIS_BR1_FIXED_LOOPS=256 KIS_BR1_STAGE_PROFILE=1 krita/_build-br0-cpu/bin/kis_tiled_data_manager_test testPageStoreFixedPageWork
env KIS_BR1_SEED=12345 KIS_BR1_THREADS=8 KIS_BR1_PROFILE=1 KIS_BR1_STAGE_PROFILE=1 krita/_build-br0-cpu/bin/kis_tiled_data_manager_test stressTest
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_d2_batch_20260920/analyze.py
shasum -a 256 -c docs/vulkan_gpu_design/evidence/br1_d2_batch_20260920/refined-artifact-sha256.txt
shasum -a 256 -c docs/vulkan_gpu_design/evidence/br1_d2_batch_20260920/evidence-artifact-sha256.txt
```
