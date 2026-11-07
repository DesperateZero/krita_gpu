# BR1 优化实验记录

本目录保存 54 的原始实验输出，不替代 39/52 的最终配对验收。

## D1：删除/default 的语义化

- 假设：`commit(removal)` 和 history restore-to-default 只需更新虚拟 default 状态，不应调用 provider allocation/fill。
- 预期结构变化：这些操作的 `defaultMaterializationRequests` 增量为零；旧 reader/retained root 的像素保持正确，
  `nextGeneration` 不回退。首次真正需要 default 像素的通用读取/写入另计，不能把成本平移后隐去。
- 风险：虚拟 default 没有物理 authority；必须由精确 default revision/descriptor 恢复，不能放宽普通像素版本的 authority 不变量。
- 本轮混合 stress 采用固定 seed 12345、8 workers/默认线程、1 BPP，连续 5 次 plain before/after；只作完整操作诊断，
  seed 不固定交错和实际删除页数。profile 独立采集，不能将该结果称为 M 等价、真实像素 K 或 GPU/UMA 性能通过。
- 先保存 before，再构建 after；两者不并发运行，性能计时不与编译/其他测试重叠。边界为 Qt test elapsed，进程 time 单列。
- 最终还需同 harness upstream 配对、固定 K/N 及 4/8/16 BPP、独立 M/K/E、预冻结不劣性容差与尾统计；全部保持待测。

偏离预期的结构计数、总耗时/热点变化和未消除开销必须记入 54，不以假设替代结果。

## 当前保存状态

- `before-plain-01.log` 至 `before-plain-05.log`：已保存；Qt elapsed 中位数 26.556 s，范围 26.059–26.789 s。
  进程 real/user/sys/RSS 保留原件，不与 Qt 计时混算。
- `after-plain-01.log` 至 `after-plain-05.log`：首轮 D1，中位数 16.528 s，范围 16.026–16.593 s。
- `d1-final-plain-01.log` 至 `d1-final-plain-05.log`：含 overlay 修正与 clear facade 简化的最终 D1，中位数 16.212 s，
  范围 16.006–16.350 s；相对 before 中位耗时下降约 39.0%。非交替、非主干配对，不能授予 M/K/E 不劣性资格。
  两组 after 区间重叠，不把其间约 0.3 s 中位数差单独归功于后补修正。
- before tiled-test SHA256：`0a6d8795e8f0504d3ce695b23a99898fe0e7f4d86f0f783bde4319e850cc3b7c`；
  before libkritaimage：`9a068ab0530ed8e44115f0726c03bf977e6eb019a63f9e00760a61067596d81f`，与 53 检查点一致。
- `after-targeted-tiles.log`：初版 5 passed / 5 failed，保留失败；v2 为修正后定向 10 passed，不是全量 tiles3。
- `after-foundation-v2.log`：修正后 24 passed；`after-reference-v3.log`：新增 reader/default-revision 用例后的 31 passed。
  Reference 无后缀及 v2 均为旧集合 30 passed，不覆盖该新增用例。所有 Qt totals 包含 init/cleanup。
- `after-full-tiles.log`：首轮完整 tiled-manager suite 32 passed。
- `d1-overlay-before-fix.log`：新增 overlay read 一致性测试先失败；`d1-overlay-reference.log`：初次修正触发 4 项既有
  fixture 失败；修正前置条件后 `d1-overlay-reference-v2.log` 为 31 passed，失败原件保留。
- `d1-history-clear-before-fix.log`：4 个 BPP 用例在 facade 简化前已经通过零 write-request/default-materialization
  断言；不能再宣称该简化消除了旧像素复制。详细偏差 D1-A–F 见 54。
- `d1-final-foundation.log` / `d1-final-reference.log` / `d1-final-full-tiles.log`：最终 24/31/36 passed，
  不等于其余 iterator/paint-device/CPU/OpenGL 产品套件及长压已经全部重跑。
- `timed-01-d1.log` 与 `timed-02-d1-final.log`：分别为首轮/最终独立 opt-in profile，Qt 16.443/16.146 s。
  最终目标 manager 的 default materializations 为 0、generic write requests 为 0、read requests 为 1,043,134；
  counter 不含 bitBlt 临时 source manager，pages/versions/replicas 512/512/64 是销毁前存活终值，不是累计量或 drain 后值。
- `sample-d1-5ms.txt` / `sample-d1-1ms.txt`：首轮粗/细采样；`sample-d1-final-5ms.txt`：最终采样。
  对应 `*-test.log`、`*-tool.log` 保留 Qt 运行及采样输出。主要宏观热点排序一致；采样占比不是 CPU 时间。
- `analysis.json` / `summary.json` 与 SVG：由下方脚本复算；operation/history 图显式选最终 profile。
  两套互斥调用路径分类是同一批样本的不同切面，不能相加；脚本核对非等待 worker 样本守恒。

## 版本身份与复现边界

- `after-artifact-sha256.txt` 属于首轮 D1，`d1-final-artifact-sha256.txt` 属于最终 D1；两者不相互覆盖。
  工作树 base 为 `f5fbbde618df6fb4e1068ace7381c339a70dd4c0` 加未提交改动，仅 base commit 不足以复现。
- `d1-final-tracked-image.patch` 保存最终 `libs/image` tracked diff；`d1-final-untracked-image.tar.gz` 保存该区域未跟踪的
  PageStore、Reference 测试及 bridge/profile 源文件，路径相对内层 `krita` 仓库。二者是源码切片归档，不是可单独构建的
  全仓快照；其他 BR0 工程文件、依赖和配置仍须使用对应工作树/构建环境。before/首轮未另存完整源码归档，不冒充完整复现包。
- `d1-evidence-artifact-sha256.txt` 记录上述归档及分析脚本身份；机器/编译 profile 见 53 第 3 节。
  归档/分析 hash 不替代测试二进制和动态库身份，后续重建必须保存新身份，不能沿用本次性能结论。

构建/正确性复现（仓库根目录；性能运行不得与构建/其他测试重叠）：

```sh
.venv/bin/cmake --build krita/_build-br0-cpu --target kis_tiled_data_manager_test KisPageStoreReferenceTest KisPageStoreFoundationTest -j6
krita/_build-br0-cpu/bin/KisPageStoreFoundationTest
krita/_build-br0-cpu/bin/KisPageStoreReferenceTest
krita/_build-br0-cpu/bin/kis_tiled_data_manager_test
```

当前检查点计时命令（每次顺序独立启动；plain 至少重复 5 次并保存新日志，不覆盖本次原件）：

```sh
env KIS_BR1_SEED=12345 KIS_BR1_THREADS=8 KIS_BR1_PROFILE=0 /usr/bin/time -lp krita/_build-br0-cpu/bin/kis_tiled_data_manager_test stressTest
env KIS_BR1_SEED=12345 KIS_BR1_THREADS=8 KIS_BR1_PROFILE=1 krita/_build-br0-cpu/bin/kis_tiled_data_manager_test stressTest
```

分析复现（只重算已有日志，不启动性能测试）：

```sh
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_perf_20260920/analyze.py docs/vulkan_gpu_design/evidence/br1_optimization_20260920 --timed-run timed-02-d1-final.log
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_optimization_20260920/summarize.py
shasum -a 256 -c docs/vulkan_gpu_design/evidence/br1_optimization_20260920/d1-evidence-artifact-sha256.txt
```
