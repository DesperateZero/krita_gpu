# S02 第一批：稳定增长、原索引拒绝原子性与容器实际计账

本批落实 [01c / SS2–SS3、SS10 的存储前置](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#stable-storage-implementation)。完整阶段状态仍由 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)裁决；本批没有启用跨 job stroke scope。

## 源码与构建身份

- HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。
- 全部累积差异（含原五个未跟踪生产/测试文件及新 `KisMutationStorage_p.h`）：`4d0db8a75988529ce53adad9ed1af976cf267fb6ec9bd804f392a2393fa29fac`。
- 本批前源码差异：`f4564c579d730a9efd269269255136fbaa67feda9c27d995ee7330a04012ea94`。
- 最终 `libkritaimage.21.0.0.dylib`：`1d399b29c9918e5b70169efa50b6dbb26f57fcd716488136a53c6c30ff49ad2d`。
- [完整矩阵身份](checks-01/identity.json)、[矩阵命令与结果](checks-01/manifest.json)、[实际累积源码](checks-01/source.patch)。
- 手工修改 8 个生产/测试/架构文件的前后 hash 见 [incremental-review.json](incremental-review.json)，仅本批源码差异见 [incremental-source.patch](incremental-source.patch)。调用图及 baseline 为生成产物；没有放宽 intrusion ratchet 或 layout ceiling。

## 实际实现

原 MutationWriteSet 继续唯一持有 entries 和 PageKey 索引，保留单页 inline。热 overflow 改为 8-slot 块，冷 Page overflow 同步改为 2-slot 块；目录增长移动块句柄，entry/Page 地址保持。原第 9 项稀疏索引先在候选中完整构建，再安装新 entry；已存在索引插入使用标准容器的异常保证，entry 构造为 noexcept。move/rebind 仍移交原 write set，并清空移出集合。

块、vector 目录和 unordered index 的 node/bucket 使用同一原 budget controller 的 MetadataArena 类，在实际分配前 reserve，成功后 commit，实际 delete 后 release。按 allocator 请求容量收费，不声称这是 allocator 内部开销或 RSS。失败期间已经取得、仍保留的目录/块容量继续计账，随原 scope 的取消/终结释放；本批没有承诺所有容量变化都回滚到准备前大小。

native/semantic entry、冷记录和 managed range 的存储拒绝回到既有失败/取消链；storage 错误不伪报其他 writer 冲突。尚有 guard 时终结拒绝，guard 继续保活原 owner；释放后原取消链归还所有权。密集热索引与冷空位暂不复用的语义保持，因此本批没有引入未接线的 slot ABA 权限。

## 验证结果

最终 `checks-01`：**17 目标 × arm64/x86_64，6,292 passed，0 failed/skipped**；新增 14 项/架构。结构门：21 manifest、24 ownership、16 census、1,681 APIs、16,833 edges、15 callbacks、19 intrusion；六项工具自测通过。最后 Ninja dry-run 无待构建项，源码与二进制身份未变。

新增用例覆盖：稳定增长 1,000 entries、原索引 8→9、已有索引增长及预算拒绝、move/rebind、拒绝后原 keys/address 保持、语义写准入耗尽后取消/再用、inline/overflow guards 跨 65 页增长并晚于 session façade 释放。首轮相关 fixture 合计 51 passed；正式结论绑定最终完整矩阵。

| 实际 allocator 探针，每架构 | 结果 |
|---|---|
| address-final | 2→1,000 entries，首个 overflow entry 地址保持；旧 image 的 before-01 返回 10，地址不保持 |
| storage-final | 1/2/8/9/1,000 页分别重复命中 1,000 次，allocation/bytes/free 全零；单页无 overflow/index 动态分配 |
| write-set-final | 24 区间、20 次真实分配拒绝；原 size/keys/address 保持，随后重试和销毁后预算归零 |
| native-final | 50 区间、42 次真实分配拒绝；native/semantic 的 storage 失败不外抛，取消、重新写入、abort、close 均正确 |
| joint-final | 原共同生产安装矩阵 31,080 区间，allocation/bytes/free 全零 |
| legacy-final、warm-read-final | 原 legacy install 28 区间、暖读 96 区间继续零 allocation/bytes/free |
| outer-final / outer-final-02 | 原外层读保护清理与预算归还探针继续通过 |

**16 次最终探针**全部绑定矩阵同一 image，见 [probes-manifest.json](probes-manifest.json) 与对应 `install-*-identity.json`。原先与本批不直接相关的其他 S09 探针没有全部重跑；其旧记录只代表旧源码。故障探针保留实际 malloc/calloc/realloc/aligned allocation 调用栈。write-set 探针覆盖整个直接插入；native 探针只选择 `kisAllocateMutationStorage` 栈，不能外推到 admission/activity/metadata/provider 的所有内部 allocator。

存储构造成本如下，两架构数值相同；这张表只描述 write-set 容器，不包含 payload、session/control block 或整笔 brush。

| 页数 | 构造 allocations | 累计请求 bytes | 构造期间 frees | 最终 charged live bytes |
|---|---:|---:|---:|---:|
| 1 | 0 | 0 | 0 | 0 |
| 2 | 2 | 912 | 0 | 912 |
| 8 | 2 | 912 | 0 | 912 |
| 9 | 12 | 1,360 | 0 | 1,360 |
| 1,000 | 1,141 | 181,408 | 14 | 166,824 |

计量前预热原 controller 的可复用 reservation slot，因此单页 bucket peak 中的 1 byte 来自正向预留控制，不是容器 live charge。累计请求 bytes 包含已释放的旧目录/桶；最终 charge 只统计仍存活的容量。块尺寸和节点成本仍须结合真实 Fresh/stroke 性能裁决，本批没有新增 2% 回退门或 BR1-PERF 资格。

## 可复现命令与保留失败

```text
python3 docs/vulkan_gpu_design/evidence/br1_s02_stable_storage_20260928/run_checks.py <new-checks-directory>
python3 docs/vulkan_gpu_design/evidence/br1_s02_stable_storage_20260928/run_install_probe.py arm64 <new-tag> write-set-failure-probe.cpp completion-failure-interposer.cpp
python3 docs/vulkan_gpu_design/evidence/br1_s02_stable_storage_20260928/run_install_probe.py arm64 <new-tag> native-storage-failure-probe.cpp mutation-storage-failure-interposer.cpp
python3 docs/vulkan_gpu_design/evidence/br1_s02_stable_storage_20260928/validate_guides.py
```

`before-01` 是旧源码/旧 image 的真实地址移动反例，不把它当成原线程约束下已经发生的悬空访问。`build-01` 暴露 explicit ColdPageSet 构造不接受 `= {}`，改为显式空对象；`build-02/03` 成功。第一次 outer probe 误配普通 allocator interposer，链接缺少 `auditOnBlockFree`；失败日志及 `probes-manifest-01.json` 保留，改用原专用 interposer 后重新取证。`finalize_docs-01.py` 的长物理行在系统 Python 3.9 解析时报编码错误，未执行修改；换为可读多行脚本后运行一次。没有豁免生产失败。

## 尚未交付

仍需可回收 slot/incarnation、对应密集遍历与 subset claim 改造、空块收敛、job/range 批量准备与跨 worker borrow、完整 checkpoint/窗口、业务读取与写后刷新。当前 append-only 分块是前置，不能当作长 stroke 最终方案。

scope/range/control-block、admission/activity QHash、metadata/descriptor/provider 内部全部失败、必要终结/通知/派发容量、共享父额度和完整自动接续仍开放。本批只对已接入 allocator 的容器实际收费，不授予完整 S10 或应用级 OOM 保证。A 批、S02–S05、必要 S08–S10、完整 M6/M7/M8、undo/context、真实 stroke、Fresh 2%、Vulkan、TSAN、BR1-PERF 均按 92 继续。

指南的源码行号、当前事实和待改入口已同步；[文档差异](guide-update.patch)、[源码定位核对](mapping-validation.json)、[链接/身份检查](guide-validation.json)保留本批修改与代码之间的关系。归档链接只跳过，不读取。
