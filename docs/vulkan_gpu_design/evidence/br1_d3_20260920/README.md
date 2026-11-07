# D3 操作级抽样与 immutable metadata directory

报告：[57](../../57_br1_sampled_write_pipeline_and_immutable_directory_20260920.md)。这是 CPU/CpuRam 分支内诊断，不是
主干 M NI、isolated K、产品 E/tail 或 GPU/UMA 资格。环境沿用 56（Mac16,10/macOS15.7.3/24GiB，arm64，Qt6.8，RelWithDebInfo）。

## 版本与复现资产

- original：56 refined binary；仅用于关闭态诊断扰动对照，旧 fixture 上限 4096。
- before：D2-B + operation sampling / writeBytes 完整管线计时 / 长 fixture。没有目录优化。
- after：仅再加入 immutable directory release/acquire publication 与并发测试；所有页面状态安全校验不变。
- before/after 源码切片分别为 tracked image patch + untracked image tar（相对 nested repo，包含既有 dirty 工作区，不是完整
  全仓/依赖构建包）。base `f5fbbde618df6fb4e1068ace7381c339a70dd4c0`；original 的切片归档见 56。
- `/tmp/br1-d3-runtime.amRbwL/` 保存本次 executable/library 运行副本，可能被系统清理；SHA256 在各 manifest 和 artifact
  文件中。重现前需从对应源码重建保存版本，不能用 after 库替代 before。loader-proof 日志验证库路径。
- `run.py` 接受新的 output 目录，拒绝覆盖。六对每桶，反转版本顺序、轮换 case 顺序，串行运行；`paired` 两边使用同一个
  `before/test` executable，只有 `DYLD_LIBRARY_PATH` 指向不同的 saved libkritaimage。环境的 hash/allocator/OS 调度状态
  未强行等同，六对仍有漂移/随机性限制。保存 source/binary 身份不等于封闭的环境可复现性。

## 原件

- `disabled/`：24 runs（2桶×6对×2版本），4096 操作，部分区间 <100ms，仅扰动诊断。
- `sampled/`：72 runs（6桶×6对×plain/sample），K1 16384、K16 4096 操作；每个实际区间 ≥100ms。
  sample period127、offset按 pair 轮换，阶段中只统计真实采到的操作，不乘系数冒充精确全量时间。
- `paired/`：72 runs，关闭 recorder，相同长区间；目录优化 before/after。每个子目录 manifest 记录顺序、命令、循环数、
  executable/library hashes。固定 canonical page work 与语义变化计数逐对校验。
- `before-sampled.log` / `after-sampled.log`：补充各一次 K1/K16 的 16384 操作、offset37 profile；不是独立配对资格。
- Reference 39 / Foundation 24 / full tiled-manager 88 passed，见 `*-after.log`；harness 阶段 Reference 为38。
- `analysis.json` 包含每对原始操作时长、ratio、六对 median bootstrap95 和 sampled phase 聚合。bootstrap 以进程 pair
  为单位，seed937，10000重采样；不把循环内各操作当独立样本。未预先冻结正式 NI margin，不授予 NI Pass。
- setup、warmup、正确性读取、retained release 不在 operation 区间，仍单列；长循环会影响协议 replay 集合/缓存历史，
  不能与 56 的256-loop小桶直接拼接。live versions不是累计或峰值，也不是 metadata/replay 内存有界证明。

## 命令

```sh
.venv/bin/cmake --build krita/_build-br0-cpu --target kis_tiled_data_manager_test KisPageStoreReferenceTest KisPageStoreFoundationTest -j6
krita/_build-br0-cpu/bin/KisPageStoreReferenceTest
krita/_build-br0-cpu/bin/KisPageStoreFoundationTest
krita/_build-br0-cpu/bin/kis_tiled_data_manager_test
env KIS_BR1_FIXED_LOOPS=16384 KIS_BR1_STAGE_PROFILE=1 KIS_BR1_STAGE_SAMPLE_PERIOD=127 KIS_BR1_STAGE_SAMPLE_OFFSET=37 krita/_build-br0-cpu/bin/kis_tiled_data_manager_test testPageStoreFixedPageWork:real-N4096-K1-H0-B4
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_d3_20260920/run.py paired --runtime /tmp/br1-d3-runtime.amRbwL --output /tmp/new-d3-paired-results
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_d3_20260920/analyze.py
```

`analyze.py` 校验全部完成日志、工作量、sample interval、无 manifest 导出及有效时长；文件 hash 清单单独验证证据未被修改。
