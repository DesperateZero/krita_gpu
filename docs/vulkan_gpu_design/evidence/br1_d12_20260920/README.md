# D12 physical exclusivity 前置切片证据

本切片仅接通 TileData/binding 的物理 claim，不开放 canonical allocation 原位覆写；报告见
[66](../../66_br1_physical_exclusivity_prerequisite_20260920.md)，整体状态见52。

`protocol.json` 在本轮 rate 计时前冻结。`capture.mjs` 冻结当前源码、匹配runtime及旧D11/固定upstream身份。
`run-regressions.mjs` 保存回归原件；`regressions/` 是新增preclone测试前的15项版本，`regressions-final/` 为补齐后的版本。
`run.mjs native` 和 `native_reference` 用各自编译的共同fixture+匹配runtime，不混用旧inline ref与新claim。
分析复用已封存D11的 `analyze.mjs`，其hash随manifest冻结；无交叉版本ABI假设，无正式NI、事件尾或GPU/UMA资格。

两组各11桶×8对，共352次有效rate和4次loader；原始数据、每个pair与探索区间全部保留。
K1/B8写约-1.9%、K16读约-1.6%，copy控制桶有变动/宽区间，不能宣称gate零成本或先验归因噪声。
真写吞吐仍仅固定upstream约0.25%–0.43%，不是生产原位写完成后的结果。

最终 PhysicalClaim16、Mutation17、ResidentRead28、Reference59、Foundation24、read fixture41、tiled88、native34、
pooler3、store5、Vulkan13和architecture均通过；rate结束后补跑low-memory4/swap-store4，身份见`supplement.json`。
`identity.json`冻结95份源码与3套本机runtime共424项hash；补充测试的2份源码/binary/log另验。未测sanitizer/长压、
完整owner-permit并发、claim尾延迟、全后台drain、GPU/UMA；这些不因低层primitive通过而获得资格。

只读校验及分析复算：

```sh
node docs/vulkan_gpu_design/evidence/br1_d12_20260920/verify.mjs
node docs/vulkan_gpu_design/evidence/br1_d12_20260920/verify.mjs --archive-only
```

`--archive-only`跳过当前工作树源身份，仍核验冻结源码/runtime/协议/原始日志/分析/封存。`--seal`只用于首次封存，
拒绝覆盖。后续研究使用新目录；不能修改本目录原件来覆盖负偏移。D11的539项封存不变。
