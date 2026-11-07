# M5 修复基线与验证证据（2026-09-25）

**结论：本轮修复通过，`krita@5173c807c87bb1619325249a07a8b4f4f8f09f09` 可作为 M6 前置基线。** 当前执行和剩余 BR1 出口仅见 [92](../../92_br1_m6_m8_execution_baseline.md)；不代表 M6/M7/M8 或正式 BR1-PERF 已完成。

## 修复对应关系

| 原反例/延伸发现 | 当前实现 | 本轮证据 |
|---|---|---|
| 90 M5-R1：默认像素 canonical/compatibility 分裂 | prepare 默认 backing → canonical 更新/restore → 无分配 install；统一 undo/redo helper；拒绝时不移动两侧默认值 | manager 新回归覆盖 1/4/8/16 BPP、满 RAM、更新/undo/redo 拒绝、释放后重试、clear/clone |
| 90 M5-R2：构造返回无效对象后 clone 崩溃 | 默认 backing 必须先准入；失败抛 `std::bad_alloc`；构造中间资源用 RAII；clone 共享已准入默认 backing | 零、不足一页、满预算、多次失败、已有 manager clone、释放后构造/复制/读取 |
| 90 M4-R1：QHash reserve 后 insert 分配 | 既有 shard owner 使用单一平坦索引；实际 bucket 在 prepare 构造；令牌覆盖并存候选；无 tombstone 的回移删除；按实际 entry 大小为新旧数组增长重叠计费 | 碰撞/环绕/增长/删除与独立 QHash oracle 对照；真实 exact/physical 模板分配探针；prepare bad_alloc 保留原索引；预算用尽回归 |
| 延伸发现：descriptor 同样只预留 QHash capacity | 既有 publication owner 改用标准 unordered_map node handle；提前准备 node/bucket，安装转移 node，替换的旧值留到候选清理 | root/metadata/descriptor 的实际完整发布区间分配跟踪 |
| 动态跟踪发现：重复 root isValid 创建临时 surface 集合 | 初始/commit/restore 的 root 构造保留完整校验；私有不可变 root 保存校验结果，后续查询不重建集合 | 第一轮跟踪捕获 12 次分配/2,336 字节；修复后两架构均为零；原有 root/epoch/restore 正反例矩阵全部通过 |

没有增加第二个逻辑 owner；旧 QHash slot-index 实现、旧 descriptor 安装方式和安装期临时验证集合已被替代，不并存。构造失败沿用 C++ 分配异常契约，调用方的 `new KisDataManager` 不会收到无效对象；不宣称这新增了全应用 OOM 恢复 UI。构造/clone/转换调用者见 `kis_datamanager.h`、`kis_paint_device_data.h`、`kis_paint_device.cc`；资源拒绝没有预算外兜底。

## 同源码验证

- `protocol-final.json`、`run_correctness.py`、`correctness-final/`：冻结提交后重新构建、运行 10 套 CPU/业务测试，arm64+x86_64 共 **2,964 passed、0 failed**；Vulkan foundation 两架构各 **14 passed**。结构门与 **6 项工具自测**通过。每个命令、配置、seed、时间、binary/library 哈希及原始日志保留。
- `default-targeted-initial.log`、`default-targeted-final.log`、`index-targeted-initial.log`：开发期定向回归，不能与上述正式矩阵相加后声称更多独立覆盖。
- `allocation-interposer.cpp`、`install-allocation-probe.cpp`、`run_install_probe.py`：macOS malloc/calloc/realloc/posix_memalign/aligned_alloc/free 的线程局部 interposition，含共享 Qt 正控制；沿用现有 test friend 和 opt-in diagnostic observer，不向生产添加新的 allocator 开关。
- `install-{arm64,x86_64}-final.log` 及 identity：真实 exact/physical index、1/64/65/129 页各 4 次 root+metadata+descriptor 发布、129 页 restore additions（并存 prepare 和取消候选）均 **0 allocations、0 frees**。index prepare 注入 bad_alloc 后全部原 entry 仍可读；identity 记录编译/链接参数、环境、源码和库/探针哈希。该动态覆盖不是对所有平台或未来 M7 的自动资格。
- `callgraph-generation.log`、`architecture-refresh*.log`：1467 APIs、13730 edges、21 manifest、21 ownership、16 census、19 intrusion files。分类为 1007 production、284 indirect、133 test-only、43 unreached；不是删除清单。未放宽 intrusion ratchet。
- `repair_protocol.json` 在测量前冻结：arm64、两个 forced-COW 桶、40 对/20 个顺序平衡 block、750 ms completed-throughput 窗口、每桶单侧 97.5% bootstrap 下界，两个桶整体至少 95% 置信口径；保留全部样本。`repair-runtime-identity.json` 校验旧控制库哈希及其与 `095193d11a` 完整机器码相同的既有证明；两侧使用同一 fixture executable。
- `repair-performance-analysis.json`：修复/修复前吞吐比中位数 K1 **1.06196**、K16 **1.04452**；下界 **1.05792 / 1.03223**，均高于 **0.98**。这是两桶整条管线修复回归，不是新的 selector-only 因果实验或正式 upstream BR1-PERF。selector 源码未改，旧局部控制资格不被本轮整管线加速替代。
- 固定 K 增长 N/H、native/generic、预算/生命周期/确定性交错均随当前完整矩阵运行。TSAN 沿用已有工具链资格结论 **Inconclusive**，本轮不冒称重跑或通过。

## 失败保留与复现

`install-probe-initial.cpp` 保存初轮运行的探针原文，哈希与两次开发期 identity 一致；最终探针另增 physical index 验证。`install-arm64-initial.log` 保留修复中捕获的 root 重复验证分配；`install-arm64-root-validation.log` 是后续开发验证。最初两次 probe 编译缺少完整 ReadPage 头和 test friend 上下文，原编译输出保留；补齐探针后运行成功。`br1-m5-repair-build4.log` 保存 descriptor hasher 的 const 成员导致 move-assignment 编译失败，移除该 const 后构建通过。首次结构门仍要求旧 `m_entries.insert` 拼写，已改成预构造 bucket 及禁止 QHash 回退检查；初次拒绝日志保留，未放宽行为或侵入门。

复现完整矩阵：`python3 run_correctness.py`（拒绝覆盖已有输出；在新的证据副本运行）。复现分配探针：`python3 run_install_probe.py arm64 <新标签>` 或 `x86_64`；同样拒绝覆盖已有日志。性能协议、运行器、分析器与原始数据都在本目录，不得挑选或替换失败样本。最终 `artifacts.sha256` 绑定目录内容；`final-verification.json` 绑定归档、文档和当前源码/二进制一致性。

`raw-log-preservation.json` 保存可读日志中规范化行尾/末尾空白前的逐字节原文与哈希；未改动实验数据。
