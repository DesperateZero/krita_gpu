# JP5/JP6 收敛审查：新读取、旧 reader 与 extent

本次交付是**可执行反例、兼容语义对照和有限改动清单**，没有修改产品源码或修复窗口。当前裁决见 [92 §16.7](../../92_br1_m6_m8_execution_baseline.md#current-read-convergence)，改动领取见 [收敛清点 §10](../../br1_modification_guide/CONVERGENCE_CHECKLIST.md#current-read-work-order)，函数与语义见 [02a §10](../../br1_modification_guide/02a_joint_publication_boundaries.md#current-read-contract)。不将复现成功计为产品验收通过。

## 身份与执行范围

- 产品 HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含 6 个未跟踪源码的差异 SHA-256：`66e7ff89c8a9208ef3253e2d8e0c0b4fc6d2f92e07f664caae4e05138dd1f54d`。
- [执行前核对](before.json)确认与 JP4 的源码和 28 个构建/运行文件相同。JP4 的 9,238 / 0 / 0 是此前完整矩阵的冻结结果，本次没有重跑该矩阵。
- [探针源码](current-read-probe.cpp)覆盖每架构 44 个场景：32 个 publication 场景（BPP=1/4/8/16 × packed/cursor × 冷/暖 × 保持/释放旧 reader）、8 个 history pending 对照、4 个无像素暴露的 write-intent 对照。诊断窗口中的读取是同线程同步观察；写调用返回后的 fresh reader 在另一线程执行，此时旧 reader 仍可持 pin。
- [运行脚本](run_probe.py)沿现有测试的 compile/link 参数链接实际 `kritaimage` / `kritapigment`；没有 interposer 或产品临时补丁。日志、命令、源码及二进制 hash 分别见 [arm64 身份](arm64-01-identity.json)和 [x86_64 身份](x86_64-01-identity.json)。每个子进程超时为 60 秒；两架构本次均正常退出。

执行命令（仓库根目录）：

```sh
python3 docs/vulkan_gpu_design/evidence/br1_current_read_convergence_20260928/run_probe.py arm64 01
python3 docs/vulkan_gpu_design/evidence/br1_current_read_convergence_20260928/run_probe.py x86_64 01
```

重跑必须使用新的 tag，脚本拒绝覆盖证据。每架构先记录现状，再以 `--require-converged` 执行相同输入；**后者实际返回 3，明确表示验收未通过**。记录模式返回 0 仅表示反例采集及旧读/取消等控制成立。运行日志：[arm64 记录](arm64-01-record.log)、[验收失败](arm64-01-require-converged.log)，[x86_64 记录](x86_64-01-record.log)、[验收失败](x86_64-01-require-converged.log)。

## 实际观察及含义

两个架构结果相同：每次 172 个观察点，0 个控制错误，80 个 publication 不一致观察点。80 是同类缺口在不同输入和观察点上的重复观察数，不是 80 个独立缺陷。

| 固定观察点 | 场景数 / 架构 | 与同点 canonical 一致 | 结论 |
|---|---:|---:|---|
| metadata prepare | 32 | 32 | 发布前仍是旧选择 |
| seal cleanup | 32 | 0 | canonical 已是新值；冷页 hash 未装，暖页读旧缓存 |
| operation cleanup | 32 | 0 | adapter 尚未完成交付 |
| adapter installed | 32 | 24 | 剩余 8 例都是暖页且旧 reader 仍持同一 wrapper |
| 写调用返回后，另一线程 fresh read | 32 | 24 | 上述 8 例继续读旧值，不能用“writer 已返回”规避 |

冷页中 canonical 像素为 97、extent 为 64×64，而 `getTile(false)` / `getReadOnlyTileLazy` 都返回 default 0、`existingTile=false`、manager extent 为空。暖页旧值为 49，新 canonical 为 97；旧 reader 未释放时，两个 fresh API 均返回相同的旧 wrapper / 49，直至最后旧锁归还后再取才读到 97。原 captured view 和已借出的旧 raw 指针在所有场景保持旧值，这是必须保留的控制。

history pending 对照证明：新写页尚未 checkpoint 时，外部 exact 仍读 default，canonical extent 保持上个 cut，manager extent 已包含 pending 页；checkpoint 后两者相符，abort 恢复原 extent。write-intent 对照证明：仅 `getTile(..., true)` 并 lock/unlock、未暴露可写数据，也能让 manager extent 包含该页而 canonical extent 为空。**这两种差异没有计为 publication 违例**；它们说明兼容工作范围和已发布 extent 具有不同的现存语义，不能无条件替换 `extent()` 或从 hash 命中推定 canonical 页存在。

这些观察固定了后续要关闭的边界，没有证明任意并发历史都是线性一致的，也没有测量耗时、分配率或 TSAN。独立页进度、default 变更、删除/restore、资源拒绝和所有 caller 的失败上送仍需实现批补齐。

## 源码与主干对照

[源码审计](source-audit.json)冻结 13 个相关文件、23 个入口标记及固定 upstream `9a24ae0d8c070884fb013594191002e1a1b39a19` 的可用文件 hash/行数；[收集脚本](collect_audit.py)保存两组 scoped `rg` 查询：[raw caller](callers-1.txt)、[extent caller](callers-2.txt)。文本匹配包含模板及同名 API；经手工分类后用于 02a 的责任表，不冒充完整静态调用图或 runtime census。

主干以原 hash/TileData/memento 管理 current；新增 PageStore 引入独立的 canonical 选择与物理能力验证。现有 `Tiles3TileReadCache::repinRead` 证明 backing 身份仍可 pin，不证明它仍是最新逻辑版本；`lockForRead` 的非零 `m_lockCounter` 分支直接复用已有能力。把这两个职责混在一个“缓存有效”标志里会遮蔽本次反例。修复应沿原 selector 和 read lease 完成选择核对，保留旧 pin，不增加新的 current 注册表。

质量判断：局部能力和反例证据可复核，新增协议尚未形成完整产品收益。当前应优先关闭 fresh read 及外部 extent 的实际消费者，之后交付首条真实 direct stroke，再统一 owner 参数和 adapter 交付；增加更多底层子层不能替代这些结果。本次新增代码仅是证据 harness，产品改动增量为 0，既有生产/测试/生成审计规模见 [JP4 清点](../br1_s05_overlay_extent_20260928/inventory-final.md)。

## 文档收敛与验证

沿用现有清点和 02a，未新增一套实施阶段或当前状态入口。清点补充下一批实际函数、必须保留的兼容语义、不能采用的简化以及完成后去向；README/NEXT_EDITS/CODE_INDEX 只导航，当前结论仍回写 92。旧冻结记录不覆盖，archive 未读取。

最终文档链接/锚点/行号边界、源码与运行文件身份、增量 patch 检查见 [validation.json](validation.json)，其中记录对应的 `document-check.json`；它们不扩大产品资格。
