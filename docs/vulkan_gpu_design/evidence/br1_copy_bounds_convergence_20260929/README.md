# JP6 copy bounds 与复制政策收敛

本批关闭一个真实业务反例：非 wrapped `makeCloneFrom/Rough` 在新 canonical 页已发布、manager working extent 尚未刷新时提前裁剪，丢掉本次应复制的像素。原实现的 [32 场景失败记录](reproduction-before-arm64.log)与[运行身份](reproduction-before-identity.json)保留。修复让范围和像素消费同一组 source/target 固定视图，已按最终源码完成验收；manager 的整体 extent 窗口仍未关闭。

## 改动与替代

- manager 新增一个私有 `copyPageStore`，接替 precise/rough 两条 native 选择、准备和复制分支。四个公开 bitBlt 入口、legacy 算法及不同读意图保留。
- backend 原 `copyFrom` 的 oldSource 参数改为 caller 的 sourceView/targetView，内部不再重新捕获。没有保留旧内部签名包装；[编译图](copy-callgraph.json)确认唯一生产 caller 来自共同 helper，另一个直接 caller 是原失败测试。
- 非 wrapped clone 删除独立 working extent 预裁剪。相同 default 的固定范围包含 source 和 target，避免空源漏清目标旧页；default 不同消费整个请求范围。两个 store 各自固定视图，不承诺跨 store 原子快照。
- 只增加原调用栈上的 view 保活与一个私有声明；无新 owner、session、manager/Tile 字段、TLS 或 friend。manager 头部 identifier 11→12 的原因、锁/寿命与移除条件已在 [92 §16.13](../../92_br1_m6_m8_execution_baseline.md#copy-bounds-convergence)审查后写入原 intrusion manifest，其他上限保持。
- [增量 patch](implementation.patch)相对 copy 开始前保存源码：生产五文件 +96/-64，净增 32；测试三文件 +167/-6。另更新三份审计文件（侵入说明、source baseline、生成图），它们不混入生产/测试行数。

## 最终验证范围

| 检查 | 实际结果与边界 |
|---|---|
| 新增 manager 场景 | 每架构 32 个 clone 发布窗口、32 个 native 固定 bounds、32 个两端 backend 关闭的 legacy 对照；保留旧 copy/presence/history/失败断言。legacy 对照不是完整 OFF 构建资格 |
| 20 完整目标 × 两架构 | manager、mutation、resident/read、painter、transaction、调度、stroke completion、iterator、dab queue 等完整目标；具体命令见 [manifest](checks-01/manifest.json) |
| 选定 PaintDevice 方法 × 两架构 | 14 个业务相关方法：copy/clone、duplication、geometry/default/region、wrapped read/accessor、LoD、frame undo/copy；每次含 init/cleanup 为 16 项。未运行压力/benchmark 全集 |
| 合计 | **9,560 passed / 0 failed / 0 skipped**，42 次 Qt 执行；无 SAFE ASSERT、失败项或 tile 泄漏警告。runner 将这些警告视为失败 |
| 架构与工具 | 21 manifest / 25 ownership / 16 census / 19 intrusion 检查与工具自测通过；87 TUs / 1,815 indexed APIs / 19,661 edges / 17 callbacks。indexed API 不等于公共函数数 |
| 最终构建 | [实际 Ninja no-op](checks-01/final-build-no-op.log)，不是 dry-run；源码和库在运行后再次比对 |
| 原 reader-window | 每架构 44 场景 / 172 观察，raw 违例 0、控制错误 0、**extent 不一致 32**；`--require-converged` 仍退出 3，整体 JP6 未完成 |
| 成本 | native fixture 的准备/复制范围为 1/4/6 页且一次 source/target capture，证明具体请求不按原巨大 bbox 工作；不是所有稀疏布局的复杂度或整链性能上界。本批未重测暖 getter/adapter 分配探针 |

[最终源码/二进制身份](checks-01/identity.json)的源码差异 SHA-256（含六份未跟踪源码）为 `182a7d820fff8003c50fdbb23b84be44be79b4f5549eb06ed8cc40c6d46aca1a`；[125 文件清点](source-inventory.json)逐文件存 hash，运行身份另绑定 29 个库、插件、测试与配置文件。原窗口 [arm64](arm64-final-01-identity.json) / [x86_64](x86_64-final-01-identity.json)和矩阵使用相同源码/库；探针 runner 的退出 0 只表示成功记录了已知的整体验收失败，不能当作窗口修复通过。

## 失败记录与测试所有权

最初的 compile alias 错误见 `build-fix-01.log`；新 bounds fixture 将栈上 manager 隐式传成智能指针，发生非法释放，见 [诊断](bounds-lldb-01.log)。调用改为显式基类入口后重建，最终矩阵全部通过，未删除或放宽断言。

PaintDevice 首轮通过但在退出时报 6 个 tile 泄漏。逐方法[隔离记录](paintdevice-isolation.json)确认只有 `testLodDevice` 告警；原 `syncLodCache` 创建的 `LodDataStruct` 未释放，HEAD 也有同样代码。以测试局部 unique_ptr 管理这份原资源后，单项及最终双架构运行均无告警。没有改生产回收策略，也没有过滤日志换通过。

`architecture-refresh-01.log` 因生成调用图先于 intrusion manifest 更新而拒绝；更新全部输入后重新生成，`architecture-refresh-02.log` 及最终矩阵中的 architecture 才是有效结果。所有失败/中间记录保留，未被最终通过覆盖。

## 停止条件与下一项

copy 子项完成，下一步按 [API §12.2](../../br1_modification_guide/API_CONVERGENCE_MAP.md#joint-window-design)确定原联合安装的成功/commit 拒绝时序与锁序，并关闭 manager page/bounds/adapter 的共同窗口。LoD/transfer/frame copy 和 wrapped 等未迁移入口继续逐项登记；真实 direct owner/显示/finish/cancel/drain 随联合窗口完成后接线。没有新反例，不继续扩展 copy 的框架或 helper。

默认启用、完整 OFF、Vulkan/TSAN、全部资源/进度、同依赖主干/Fresh 性能及 M6/M7/M8 均未由本批授予资格。实际接口清点见 [API §13](../../br1_modification_guide/API_CONVERGENCE_MAP.md#copy-bounds-delivery)，当前裁决仍以 92 为准。

[最终校验脚本](validate_final.py)与[结果](validation.json)核对源码、运行文件、矩阵、实际 no-op、固定 copy caller、原窗口剩余失败和文档；最终文档检查输出为 `document-check-final.json`，首轮 `document-check.json` 保留。[本轮文档增量](documents.patch)相对收敛行动文档发布后的状态；[103 处源码链接重定位](source-link-remap-final.json)按各文档已映射的起点执行，没有重写旧冻结证据。未读取 archive。
