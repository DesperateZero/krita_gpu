# D10 冷热查询分离：完成的诊断证据

结果与偏差登记见 [64 报告](../../64_br1_warm_cold_lookup_split_and_destructor_endpoint_20260920.md)。
本目录保存冻结协议、源码/运行库身份、全部原始日志、分析及校验；D6–D9 历史证据不变。
诊断与正确性通过不代表 upstream 不劣性、BR1-PERF 结清或 GPU/UMA 资格。

## 处理变量与版本

暖 cache lookup 与 out-of-line 冷 replica discovery 分离，命中不再构造/重置完整冷 handle。
冷 miss 多一次 metadata shard 查询；exact 安装复验、root retention、provider shared read/write/transfer/retire gate 保留。

`identity.json` 冻结 497 项 hash：69 个当前源码、69 个目录内源码及四套 runtime：

- `before` D9：`/tmp/br1-d9-runtime.IcwSzu`。
- `reference` D8：`/tmp/br1-d8-runtime.DEnywg`。
- `original` D7：`/tmp/br1-d7-runtime.othEAo`，仅独立旧 native fixture。
- `after` D10：`/tmp/br1-d10-runtime.f0fE3p`。

共用新 read fixture 只装载 D8+ guard/view ABI；不得对 D7 使用新 read executable。
源码基点 `f5fbbde618df6fb4e1068ace7381c339a70dd4c0` 加 dirty patch/source，不是只 checkout HEAD 即可复现。
环境 Mac16,10 / 24 GiB / macOS 15.7.3，Qt 6.8、RelWithDebInfo universal/arm64 执行。
runtime 位于本机 `/tmp`，尚未打包为脱离该机器的自足归档；目录缺失时校验/重跑失败，不允许替换为身份不符的新库。

## 覆盖与结果

`protocol.json` 在计时前冻结。14 组、111 个配对桶各 8 对，共 **888 对/1,776 次计时运行**，另 **28 次 loader**。
独立进程、轮换桶顺序和两侧先后；rate 窗口至少 200 ms；fixed-work 为相同 256 cycle、至少 100 ms。
保留全部 pair；探索性 bootstrap 不是正式不劣性判定。

- 暖 K16 held-view guard 相对 D9 吞吐约提高 5%–7%，完整 session/accessor 约 4%。
- 直接 D8 宽格式/单页仍有负偏移；首次 K16 read scope 时间比约 1.63–1.73，未关闭成本转移。
- 真实写 D10/D9 未确认变化；直接 D8 吞吐约 1.021–1.050、直接 D7 约 0.984–0.989，不是 upstream 对照。
- fixed-work 补 configure→facade/provider 容器实际析构；旧 close 端点另存，**不是全局 pool/worker drain**。
- cold profile 是 inclusive scope，另有 plain/profile 扰动对照；不将其命名为 binding/锁 self。
- 未记录每进程实际 hash seed/完整后台活动；不反推原因、不删去负面样本。正式环境控制是后续工作。

`*-paired/manifest.json` 与每次日志对应，`*-analysis.json` 保存全部桶及 pair 比值，`.log` 为分析输出。
`guard` 不含 capture/release，session/accessor 每页触达一个 byte，rect 含分配/清零/完整 copy；范围不能混同。
`cold_fixed*` 报固定-work 总墙钟/CPU/析构时间，不计算持续吞吐或事件尾分位。

## 构建与正确性

最终日志：ResidentRead 28、read fixture 41、Reference 59、Foundation 24、tiled-manager 88、native baseline 34、
Vulkan contracts 13（Qt totals 含 init/cleanup），`architecture.log` 通过。`read-initial.log` 保留早期回归，
最终以 `final-read.log` 为准。构建日志为 `build-cpu.log`、`build-read-final.log`、`build-vulkan.log`；回归墙钟不作性能测量。
未运行 GUI/长压/sanitizer；性能阶段不与构建、功能测试或 profiler 并发。

## 校验与复算

在仓库根执行只读核验（分析输出写入新临时目录，不修改原件）：

```sh
node docs/vulkan_gpu_design/evidence/br1_d10_20260920/verify.mjs
node docs/vulkan_gpu_design/evidence/br1_d10_20260920/verify.mjs --archive-only
```

普通模式检查 497 项身份、原件/manifest、协议/driver/loader、14 组逐字节复算、回归、D6–D9 历史封存和文档链接。
`--archive-only` 仅跳过 69 项**当前工作树源码**，仍查冻结源码、四套 runtime 与本目录封存；不是无需本机 runtime 的模式。
Vulkan hash 是封存时构建身份，不代替性能循环 loader 证明。

首次完成时 `verify.mjs --seal` 生成 `verification.json` 和 `artifacts.sha256`；已存在则拒绝覆盖。
后续只复核封存，不修改原 protocol/driver/日志/分析或补造缺失记录。若需新运行，先冻结新切片并使用新输出目录，不能覆盖本目录。
最新权威状态以 [52 的实施计划](../../52_br1_cpu_fast_path_optimization_plan_20260920.md) 为准，本文只描述 D10。
