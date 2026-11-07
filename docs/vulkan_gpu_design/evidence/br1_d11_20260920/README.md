# D11 CPU mutation 段证据

结论见 [65报告](../../65_br1_native_cpu_mutation_segment_20260920.md)，状态以 [52](../../52_br1_cpu_fast_path_optimization_plan_20260920.md) 为准。
安全COW段接通生产writeBytes，K16有收益、K1有回归，未取得主干性能资格；不是原位permit/短发布/有界回收完成。

`identity.json` 冻结94份生产/测试源码及本机runtime，共418项hash：D10 `/tmp/br1-d10-runtime.f0fE3p`，
D11 `/tmp/br1-d11-runtime.Fpdfyt`，固定upstream `/tmp/br1-d11-upstream-runtime.FSZ4sp`。
upstream为`9a24ae0d8c`，候选为`f5fbbde618df6fb4e1068ace7381c339a70dd4c0`加dirty源码。
runtime仍依赖本机`/tmp`与安装依赖，不是脱离本机的自足归档。

- `native-paired/`：原driver，D10/D11同binary，11桶×8对=176次rate。
- `native_reference-paired/`：仅失败的跨ABI loader，非有效性能样本；保留不覆盖。
- `native_reference-v2-paired/`：同源分别编译，upstream/D11，11桶×8对=176次rate；见 `measurement-decision.md`。
- `diagnostic-paired/`：D11-only plain/sample，6桶×4对=48次，8192固定操作，每16次采样一次；不是正式固定-work主干差分。
- `*-analysis.json`：全部pair与探索区间，由 `analyze.mjs` 从日志重建。
- `pre-fix-history-clear-failure.log`：原生写段初版history clear失败，最终修复覆盖1/4/8/16 BPP。
- `cpu-mutation-final.log`：17项；tiled-regression88、Reference59、Foundation24、ResidentRead28、read fixture41、native fixture34、Vulkan13和architecture通过。
  `cpu-mutation.log` 为较早15项通过，不能替代新增两个失败位置/分配失败覆盖后的最终17项。

测量前冻结protocol、source/runtime身份；未同时构建/回归/profile。共有400次有效计时、6次有效loader及1次失败loader。
全部结果保留。管理proxy、resident RAM copy K、操作E分开，吞吐均摊不是事件延迟；GPU/UMA产品、全后台drain、
长期pin预算与正式NI仍未测。实际hash seed和完整后台活动未记录，不能事后推断原因。

只读复核与独立复算：

```sh
node docs/vulkan_gpu_design/evidence/br1_d11_20260920/verify.mjs
node docs/vulkan_gpu_design/evidence/br1_d11_20260920/verify.mjs --archive-only
```

`--archive-only` 只跳过当前工作树源码身份，仍验证冻结源码/runtime/协议/日志/分析/loader与封存。首次使用`--seal`生成
`verification.json`和`artifacts.sha256`，存在时拒绝覆盖；之后新研究使用新目录与协议，不修改本目录既有性能原件。
