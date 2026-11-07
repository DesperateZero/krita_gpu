# D4 native COW 初始化证据

报告：[58](../../58_br1_native_cow_initialization_and_payload_accounting_20260920.md)。CPU/CpuRam 分支内切片诊断，非 upstream
不劣性、isolated M/K、完整产品 E/tail 或 GPU/UMA 性能资格。环境沿用 D3：Mac16,10、24 GiB、macOS15.7.3、arm64 运行，
Qt6.8、RelWithDebInfo、universal x86_64/arm64 构建；CPU 测量的 Vulkan foundation/UI adapter 关闭。

## 版本

- base `f5fbbde618df6fb4e1068ace7381c339a70dd4c0` 加已有 dirty worktree。`*-tracked-image.patch` 与
  `*-untracked-image.tar.gz` 保存 image 源码切片，不是整个仓库/依赖包。original 源码见 D3 after 归档。
- original 是 D3 测量 binary；before 是本轮测量/API/安全脚手架（native 能力 false），after 仅打开 native 能力。
- `/tmp/br1-d4-runtime.qCAUV2/` 保存 original/before executable 及 original/before/after library；系统可能清理这些运行副本。
  复现需从相应归档重新构建，不可用 after 冒充 before。两个 loader 日志证明实际装载路径；每个 run manifest 保存
  executable/library SHA256、顺序、命令、循环数及 sample period/offset。
- paired 两侧使用同一 before/test（ABI 相同）；scaffold 两侧分别使用对应 original/test、before/test。

## 运行与复算

```sh
.venv/bin/cmake --build krita/_build-br0-cpu --target kis_tiled_data_manager_test KisPageStoreReferenceTest KisPageStoreFoundationTest -j6
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_d4_20260920/run.py paired --runtime /tmp/br1-d4-runtime.qCAUV2 --output /tmp/new-d4-paired
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_d4_20260920/run.py sampled --variant before --runtime /tmp/br1-d4-runtime.qCAUV2 --output /tmp/new-d4-sampled-before
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_d4_20260920/run.py sampled --variant after --runtime /tmp/br1-d4-runtime.qCAUV2 --output /tmp/new-d4-sampled-after
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_d4_20260920/run.py scaffold --runtime /tmp/br1-d4-runtime.qCAUV2 --output /tmp/new-d4-scaffold
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_d4_20260920/analyze.py
env MACOSX_DEPLOYMENT_TARGET=12 CMAKE_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install .venv/bin/cmake --build krita/_build --target KisVulkanFoundationContractsTest -j6
krita/_build/bin/KisVulkanFoundationContractsTest
shasum -a 256 -c docs/vulkan_gpu_design/evidence/br1_d4_20260920/evidence-artifact-sha256.txt
```

driver 拒绝覆盖输出目录，六对/桶、交替版本与轮换桶顺序；K1 32768 操作，K16 4096 操作。paired 十桶共120运行，
sampled 每版本六桶72运行，scaffold 两桶24运行。采样以完整操作为单位（period127，按 pair 轮换 offset），不是全程细采样。
analyzer 校验全部日志完成、实际页工作/提交数、payload 计数、同 ABI/binary/library 身份、sample 数和 provider phase 次数，
每个实际计时区间须 ≥100 ms。六对探索性 median bootstrap 不授予 NI Pass，不用单次循环事件冒充独立重复。

setup、正确性读取和 retained-root release 在 operation 之外，release 时间/版本终值另列；不是完整产品 trace 或长期 drain。
preclone 命中数可观测，但后台补充/峰值 reserve/DRAM 流量尚未计量；没有把零命中等同于后台零工作。
Reference/Foundation/full tiled-manager 原始结果在 `*-before.log`/`*-after.log`；历史失败或限制不得用最终状态覆盖。

补充 tile store 5、pooler 3、Vulkan foundation contracts 13 passed。pooler 在 original/after 都有6条既有 QEXPECT_FAIL，
不能作为完整 preclone 资格。`build-vulkan-api.log` 保留首次缺 deployment target 的配置失败，按既有 cache 补12后在
`build-vulkan-api-retry.log` 重建成功。新增 API 未让 Vulkan provider 自动声明 native copy/产品 UMA 能力。

首次分析遇到 zero-interval phase 在 fixture JSON 中被省略，解析器已按现有 schema 处理并以实际 payload counter 交叉
核对；没有修改测量日志。所有 analysis 的采样均是实际记录的操作，不外推为无扰动 E 或尾分位数。
