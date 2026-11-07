# D5 共享 upstream CPU 基准证据

报告：[59](../../59_br1_shared_upstream_cpu_baseline_20260920.md)。本目录是 CPU/CpuRam 诊断，非 BR1-PERF 结清或 GPU/UMA 资格。

## 身份与实现

- 固定 upstream `9a24ae0d8c070884fb013594191002e1a1b39a19`；隔离 worktree/build 在 `/tmp/br1-d5-upstream.FgSkoZ/`。
  仅添加 source-identical 的 `kis_tiles3_cpu_baseline_test.cpp` 与一个测试 CMake 入口，不改变 upstream 算法。
- current 为 `f5fbbde618df6fb4e1068ace7381c339a70dd4c0` 加已有 BR1/D4 dirty tree；本轮只新增测试和测量工具，没有生产性能修改。
- `identity/identity.json`、两侧 CMake cache/fixture/编译命令、tracked-image patch/untracked-image tar 保存重建所需的 image
  源码差异。不是整个依赖包。32 桶双方各 34 passed 的日志已保存；current 初版与增加 CPU/RSS 后的复验分开保留。
- 配置首次缺 Ninja 路径、尝试直接构建 interface target `kritatestsdk` 失败的日志保留；正确 target 为新 fixture，
  `CMAKE_MAKE_PROGRAM=/Users/apple/krita_gpu/.venv/bin/ninja`。两侧 FOUNDATION_BUILD 最终均为 ON。
- 所有测量进程串行运行，不与构建或其他 benchmark 并发；功能 smoke 的短计时不用于性能结论。各次 loader 日志确认 image
  library，manifest 保存 executable 和所有所列 Krita library hash，运行末复核没有变更。依赖库由各 build 的 rpath/同一 `_install` 提供。

## 协议与结果

- `protocol.json`：十桶、十二对；`pilot/` 只用 upstream 选固定 work loops。K1 write 校准到 8,388,608 次。
- `measurement-decision.md`：在 rate 配对前记录累计 completion ticket 存储的源码事实；因此先跑 rate-only 子集，
  fixed-work 配对尚未执行，不谎报超时/OOM，也不把短候选与长主干的不同 work 作为固定-work 配对。
- `rate-paired/` + `rate-analysis.json`：240 次配对运行，独立 200 ms 完成量。`run-rate-v1.mjs` 是该阶段实际执行的 driver
  版本；`run-pilot-v1.mjs` 保存此前 pilot 实际版本，其 SHA256 与 pilot manifest 完全一致；二者差异仅新增 rate-only 调度。
- `protocol-read.json`、`read-pilot/`、`read-rate-paired/` + `read-rate-analysis.json`：单独冻结 readBytes 补充协议，再跑24次。
  当前 `run.mjs` 仅增加 `--protocol` 路由；不能把补充运行伪装成原十桶同一批次。
- `analyze.mjs` 核对每桶十二对、日志与 manifest、像素 PASS、实际完成数、scope、端点、区间长度，再以进程 pair 作
  20000 次 bootstrap。区间是探索性的；没有冻结 M 容差，不给 NI Pass。rate 的倒数不输出为 latency。
- 全进程 peak RSS 包含 setup/allocator；不同 rate 完成量下不能作为每操作内存对照。manager destruction 不是完整后台
  retirement/drain。H=0、单线程，不代表旧 reader、history、压力、尾分位或产品 trace。
- 配对之后 `foundation-regression.log`、`reference-regression.log` 分别为当前 24/42 passed，`architecture.log` 通过。
  完整 tiled-manager/产品套件及 Vulkan 本轮未重跑，D4 的旧记录不改写为本轮测试。
- 校准时复算 `rate-analysis.json` 与 `read-rate-analysis.json`，与归档结果逐字节一致；四阶段 manifest 的 driver/protocol
  hash 均与保留文件相符。`artifacts.sha256` 固定本目录交付文件（不含校验表自身），后续切片另建目录，不能覆盖本轮原件。

## 复算与重跑

```sh
node docs/vulkan_gpu_design/evidence/br1_d5_20260920/analyze.mjs docs/vulkan_gpu_design/evidence/br1_d5_20260920/rate-paired/manifest.json /tmp/d5-rate-new-analysis.json
node docs/vulkan_gpu_design/evidence/br1_d5_20260920/analyze.mjs docs/vulkan_gpu_design/evidence/br1_d5_20260920/read-rate-paired/manifest.json /tmp/d5-read-new-analysis.json
node docs/vulkan_gpu_design/evidence/br1_d5_20260920/run.mjs pilot --upstream-build /tmp/br1-d5-upstream.FgSkoZ/build --current-build /Users/apple/krita_gpu/krita/_build-br0-cpu --output /tmp/d5-new-pilot
node docs/vulkan_gpu_design/evidence/br1_d5_20260920/run.mjs rate --upstream-build /tmp/br1-d5-upstream.FgSkoZ/build --current-build /Users/apple/krita_gpu/krita/_build-br0-cpu --pilot /tmp/d5-new-pilot/manifest.json --output /tmp/d5-new-rate
```

输出路径必须不存在，driver/analyzer 均拒绝覆盖。temp worktree/build 可能被系统清理；重建时从固定 revision 加 identity
中的 fixture/CMake 测试差异，依照保存的 cache/命令配置。当前库若已改变必须重做 pilot 和保存新身份，不能复用本轮历史
结果冒充新 after。尚未执行的 `paired` 模式保留为后续固定-work 入口，先落实资源预算及记录增长测量，不能因本目录存在便标通过。
