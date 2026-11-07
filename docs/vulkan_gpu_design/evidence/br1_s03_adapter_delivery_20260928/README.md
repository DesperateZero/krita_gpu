# BR1 / OP6、HX7 前置：原能力延续至 adapter 交付

本批在原 managed cursor/packed operation 与显式 history operation 中，把原 ClaimSet/write set 或原 execution 保留到 manager 完成索引刷新；没有新增权限表、manager 常驻字段、TLS 或能力转交分配。代码关系、锁序和下一批具体改法见 [AD1–AD6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#adapter-delivery-implementation)。当前阶段由 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)裁决。

最终 **20 个测试目标 × arm64/x86_64：9,006 passed、0 failed、0 skipped**，58 个最终探针通过。源码差异 SHA-256 `c57edb423118c85e851a0962a3a936463df61b9bb11c6202f68a8820489f5d45`；QtCore 沿用前批 `cd0a48d2948af55889625ae0750a7d08895068deae9b6e85bdc3e1fac6dc9434`。结构门、六项工具自测、实际最终 Ninja no-op 与源码/库/插件/测试/probe 身份复验通过，见 [完整核验结果](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/evidence-scope.json)。这属于开发正确性回归，未授予新的阶段或性能资格。

## 实现与限定范围

- standalone seal 后原 scope 不可再写，事务 activity 正常结束，原 admission/write set 随同一个 completed batch 交给 manager。索引刷新后先释放 manager gate，再销毁 batch；原存储继续按实际寿命收费。
- history operation 转交同一个 execution，pending 索引刷新后显式 finish；这段区间同页借用与 checkpoint 被原能力排斥。没有每 dab 新建 history/session。
- legacy 页准入的 caller 可能持 tile swap barrier 或 manager gate，冲突因此即时失败。同 session 已有 claim 的复用不变，同线程重入保留原错误原因；foreign writer 的失败明确区分。managed 等待仍在持有这些 gate 之前。
- 新增 conflict 用例中的 raw 指真实 `setPixel → wrapper → tryWriteData`，不代表全部直接 `tileData()->data()` 消费者已经迁移。借用 packed 的比较入口改用可失败获取，拒绝时不拿旧 cache 比较、不触发 raw assertion；已有兼容 batch 仍走取消及 exact 恢复。
- `kis_tiled_data_manager.cc` 的现有 PageStore 标识计数经 92 明确审查由 **21 → 23**，两处原 batch 局部持有点；direct includes=3，未增类型集合或对象布局。其他侵入与布局门不变。该上调未通过改名掩盖。

这只是 HX7 候选与 OP6/OP7 联合发布的前置。wrapper/hash/通知写前准备、canonical/index reader 的整体发布、完整预算与默认 brush 持久 owner/current/source/producer 接线继续；M6–M8、TSAN、Vulkan、Fresh 2% 与 BR1-PERF 未完成。性能优先级保持 stroke → undo → context。

## 行为与 allocator 证据边界

新增每架构 47 个 case：四 BPP × cursor/packed/history × 写/空/拒绝共 36 个；两种 standalone 的 close/输出占用/foreign worker 等待/异线程析构；三种写模式 × setPixel/planar/borrowed packed 共 9 个持锁冲突用例。检查真实像素、索引、extent、旧 view、history、取消和释放后重试。定向最终入口见 [focused-arm64-05.log](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/focused-arm64-05.log)。

[实际 allocator 探针](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/adapter-delivery-probe.cpp)覆盖四 BPP × K=1/9/65/257 × cursor/packed/history × 四次转交，即每架构 192 次。测量 `ChangedDeliver → Cleanup` 的 changed buffer 交换与原 capability move；不包含准备、seal、manager 索引安装或销毁。保留共享旧输出、held claim、checkpoint 拒绝与最终字节检查；QByteArray 实际分配是正控制：两架构均记录 1 次 / 8,210 B；每架构 192 次转交 allocations/frees 均为 0。

## 保留的失败与修正

首轮完整矩阵 [checks-01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/checks-01/manifest.json)为 **8,930 passed / 76 failed / 0 skipped**，每架构 manager 38 个原测试期待同线程重入原因，统一替换后的错误文字使它们失败。两个新增 borrowed packed 场景还触发了 SAFE ASSERT，完整 runner 同样判失败。修正保留原同线程原因，并让实际比较入口先处理获取失败；没有降低断言、忽略 SAFE ASSERT 或删除测试。该轮和首轮 58 个已通过探针绑定各自源码，不能代表最终改动。

局部编译失败 `build-02/04/05`、探针缺完整声明的 `adapter-initial-01-driver.log` 均保留。初版正控制 `make_unique<char[]>` 被优化消除，记录 `positive_control=0` 并失败；随后改成实际 Qt 分配，重新验证正控制。没有把看不到分配的探针视作有效证据。

## 重现及对应文件

以下是本批实际运行命令；重现时用新的 evidence 目录和标签，既有日志不可覆盖。运行脚本绑定当前 HEAD、包含未跟踪生产文件的工作树差异、QtCore 与实际库/插件/测试二进制；源码在测试途中变化会失败。

```sh
python3 run_checks.py checks-02
python3 run_final_probes.py 02
python3 finalize_evidence.py
python3 validate_guides.py
```

- [完整矩阵及命令](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/checks-02/manifest.json)、[源码与二进制身份](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/checks-02/identity.json)。
- [最终探针清单](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/probes-manifest-02.json)、[探针冻结源码](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/probes-source-02.json)。
- [指南核验](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/validation.json)、[指南差异](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/guide-update.patch)。文档检查只证明关系可定位，不授予行为或性能资格。


产品改动相对前一合格批次的逐段差异见 [adapter-delivery-code.patch](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_adapter_delivery_20260928/adapter-delivery-code.patch)。所有权与侵入门已按本批明确范围更新；完整工作树身份仍以 checks-02 的 source.patch 为准。
