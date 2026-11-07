# JP4：页与派生 extent 的一次安装

本批关闭 Tiles3 冷页 seal 后「新 canonical 像素 / 旧 canonical extent」。原 overlay 候选统一承接 surface change，backend 事后 `stageDerivedExtent` 定义、声明和两处调用删除。新增/覆盖按本 segment 的 K 个 key 扩边；删除将原 overlay 与本次候选合成差量，沿原 persistent tree 的删除路径查询，复用未变子树边界，不再构造临时 tree。普通 PageStore 的显式 surface 语义保持。

- 当前裁决：[92 §16.6](../../92_br1_m6_m8_execution_baseline.md#jp4-overlay-extent)。
- 目标、保留/修复/删除/剩余项：[收敛清点 §9](../../br1_modification_guide/CONVERGENCE_CHECKLIST.md#jp4-delivery)。
- 原 owner、锁序、失败和成本范围：[02a §9](../../br1_modification_guide/02a_joint_publication_boundaries.md#overlay-extent-implementation)。

## 身份与实际增量

产品 HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；改动前差异 `fd89833d8f20e5532b9f184f8d77e3c16199e3adb3e2646163eef36fa7e14220`，最终包含 6 个未跟踪源码的差异 `66e7ff89c8a9208ef3253e2d8e0c0b4fc6d2f92e07f664caae4e05138dd1f54d`。QtCore 与前批相同。

[实际增量](final-increment.patch)／[JSON](final-increment.json)：10 个生产文件增加 185、删除 89、净增 96 行；3 个测试文件增加 213、删除 1、净增 212 行。没有新增生产文件、manager 字段或 TLS。候选状态沿原 aggregate 销毁，唯一 sealed delta 沿原 transaction 查询。完整 [124 文件清点](inventory-final.md)／[JSON](inventory-final.json)是相对 HEAD 的未提交改动，不是整个 BR1 相对 upstream 的规模：生产净增 7,929、测试净增 11,298 行；6 个生成审计文件单列。

旧二进制复现 [before-01](install-arm64-before-01.log) 在两次观察中有一次 canonical extent 失败；当时 image/pigment/QtCore 三个实际库与前批冻结记录完全匹配，见 [身份核对](before-binary-match.json)。源码当时已有未构建的编辑，因此不能拿该日志里的当前工作树文字充当旧库源码；旧库来源以匹配的前批身份为准。

## 最终验证

最终完整开发矩阵见 [checks-02 manifest](checks-02/manifest.json)、[源码和运行库身份](checks-02/identity.json)及 [完整源码差异](checks-02/source.patch)。实际命令与环境由 [run_checks.py](run_checks.py)记录；20 目标 × arm64/x86_64 合计 **9,238 passed / 0 failed / 0 skipped**，6 项工具自测、结构门和实际最终构建 no-op 通过，见 [最终汇总](final-results.json)。这是 CPU ON 开发正确性回归，不授予正式阶段或性能资格。

14 次最终针对性探针全部通过，见 [manifest-05](probes-manifest-05.json)。以下均为每架构实测：

| 观察范围 | 结果 |
|---|---|
| 冷/暖 seal 窗口的 canonical page/extent | 2 次观察，0 个失败；fresh raw/manager 的剩余差异继续打印，不算已关闭 |
| `MutationSealInstall → Cleanup` | BPP 1/4/8/16 × K=1/9/65 × 新增/覆盖/删除/删除后重写 × sibling；96 次安装 allocations/frees 为 0，8,210 B 正控制成立 |
| 新 surface 准备故障 | 104 个真实分配拒绝、9 个成功对照；此前 sealed 页与 extent、旧固定读、正常重试及最终 tracked blocks/bytes=0 |
| 原 overlay 存储故障 | 627 个实际拒绝、12 个成功对照；原失败与恢复断言保持 |
| adapter 候选拒绝 | 原 510 个实际拒绝、9 个成功对照保持 |
| adapter 交付、root 成功 cleanup reader | 原能力寿命和新/旧读回归通过 |

新 surface 故障测量只包围 `MutationSealSurfacePrepare`，不覆盖完整 seal 或 root commit 的所有分配。派生准备仍可在 owner 锁内分配，不能从安装零值推出完整短 gate 或硬预算资格。所有探针的 product tracked diff 与 image/pigment/QtCore 库均匹配最终矩阵，见 [最终匹配](final-probe-identity.json)；探针期间生成审计刷新被单独排除，没有排除产品差异。

原 manager 新增 25 个 case / 架构，覆盖 packed/cursor、四 BPP、冷暖扩边、sibling 和 QRect 范围拒绝；原 history 测试补 checkpoint 的 extent 精确断言。Reference 新增 generic publish → conditional removal 的一个 case / 架构，并检查 extent A→B→A 修订号；原显式 surface metadata 与 persistent bounds/manifest oracle 回归继续运行。已有 history default/extent 测试将中间扩边的 revision=3 单独断言，最终 clear 的 revision=4；没有放宽断言。

最终调用图 87 TUs / 1,804 APIs / 19,556 edges / 17 callbacks。架构检查 21 manifest / 25 ownership / 16 census / 19 intrusion；既有 manager 25 标识 / 3 include 和布局门未提高。结构生成日志保留三次刷新，最终使用 [graph-03](graph-03.log)与 [architecture-refresh-03](architecture-refresh-03.log)。文档/链接、最终源码及 28 个构建运行文件的复核见 [源码与二进制核对](validation-final.json)；更新后的文档与身份复核见 `validation-final-03.json`。

## 失败和修正记录

1. build-01/02 保留类型没有 `!=`、测试 void 指针及 move-only view 使用错误；修正后实际构建通过。
2. selected-01、probes-01 暴露 extent 往返后修订号未被原 `KisSurfaceEpochChange` 接受，以及 Qt 空 vector reserve 被拒绝后容量仍为 0。修订号按既有 default identity 的往返规则单调前进；无修订号的内容改变、降序和空变化仍拒绝。vector 检查实际容量和独占性，不能把无存储候选交给安装。
3. probes-02 的新删除临时 QSet 在分配失败时经过 Qt hash 的 noexcept 插入终止，见 [采样](surface-terminate-sample-01.txt)。改用协调器原标准 removal 容器类型，异常回到原 segment 拒绝。checks-01 因此中止，见 [说明](checks-01/interrupted.json)，不能累加为最终矩阵。
4. 后续删除探针在 K=9 / ordinal=15 进入原 `contentExtentAfterDelta` 临时 tree 的 Qt shared-pointer 创建异常路径，见 [逐次输出](install-arm64-surface-failure-after-04.log)和 [稳定采样](surface-failure-sample-03b.txt)。最终直接查询原树，不再为测边界构造/销毁节点；这不是豁免该分配失败。该修正不代表所有 root commit 的 Qt 分配路径已取得故障资格。
5. 三个早期崩溃诊断进程进入 macOS kernel exit 状态；已向本任务所属进程组发送 SIGKILL，LLDB 也未能暂停该退出过程。记录见 [清理说明](interrupted-debug-probes.json)和 [LLDB 输出](cleanup-terminated-probe-01.log)。不把这些未正常结束的实验计为通过；最终 14 个探针独立正常退出。

## 保持开放的结果

下一主线是 JP5/JP6：同一 read selection 下的 fresh `getTile`、warm cache、manager extent 与 adapter 一致，同时保留旧 raw/captured 读的声明语义。随后联合真实 direct stroke 的原 owner、显示 cut、finish/cancel 和 drain。完整外层准备/终结、首字节前实际收费与共享峰值、OFF 产品配置、同依赖 upstream 性能、Fresh 2%、M6/M7/M8、Vulkan/TSAN/BR1-PERF 均保持开放。本批没有提交或推送代码。
