# Production planar / trim mutation reconstruction

范围见 [67 §15](../../67_br1_target_structure_reconstruction_20260920.md#15-2026-09-21生产-planar-写与-trim-共用原生段)。
实际 data-manager planar 写与 trim 部分页共用原生 mutation 段；trim 四带不重复首写/COW/seal，
空/全部缺失 channel 与整页删除不做像素准备。不是原位 permit、全产品迁移或最终 M/K/X/E 资格。

最终 `current-*`：14 套完整回归 **514 passed / 0 failed / 0 skipped**，paint-device 选定槽 **9 passed**（均含 init/cleanup）；
十一组各 40 次，共 **440 次重放、455 次运行**全部成功，无 SAFE ASSERT。`latest-*` CPU/Vulkan 构建、架构门禁和旧 D11/D12
归档检查通过。并发放弃槽在完整套件和 40 次 batch-failure 重放中每次各运行 128 轮，不把内部轮数当作独立 Qt 场景。

较早 `final-*`（513 项，终结竞态修正前）和 `verified-*`（514 项，最后 planar 地址运算修正前）只保留为开发历史；
不与最终结果合计。当前 live manifest 绑定最后完整重跑及源码；旧日志不回写成新版本的结果。

## 证据范围

- 新增 58 个 Qt 场景：planar 16、trim 32、坐标边界与 no-op 各 1、nested rejection 1、owned/history batch failure 2、真实入口中途失败 4、并发放弃/重入 1。
  覆盖 1/4/8/16 BPP、缺失/零大小通道、负偏移、多页、四裁剪带、整页删除、旧 View、提交及 undo/redo。
- 需要像素写的操作一 native 段；每个变化页 generation/seal/pin 各一次、必要 COW 至多一次、目标 pin 峰值 1。
  compatibility wrapper/租约、trim 页面枚举/变更计划及索引重建仍存在，不把这些工作移出完整 E。
- `markFailed` 在指针仍借出时不能撤销访问，最后 guard 归还后取消 pending；caller history 已 sealed/staged 的修改保留。
  私有语义 delta 与混合操作全段撤销仍待实现，不以本轮原生像素路径通过来宣称它已完成。
- 实际 planar/trim 由外部 writer 占用第二页触发中途失败：第一页已写但未 seal，须取消 pending、保留旧 history 与外部 writer，
  且无 root commit。测试精确期待冲突 warning；不是忽略任意错误或仅调用 batch 的 cancel API。
- 最后强引用负责未完成 batch 的取消，替换跨线程 `abandoned` 标志交接；注册表槽位保留至匿名 client 终结。
  并发回归每次运行 128 轮，交错 batch 析构、异线程最后 unlock 和原线程立即重入，检查无半批结果、遗留 claim 或新事务污染。
  这来自源码审查及新增回归，未保存修改前确定性复现；不是 TSAN 或完整无锁资格。
- `development-tests-build.log` 保留首轮测试编译失败：派生 KisDataManager 隐藏基类 QRect clear 重载，改用实际公开参数签名。
- `development-nested-tests.log` 保留 1 个真实失败：拒绝嵌套前先加入匿名事务，取消新 client 导致外层被错误 abort。
  现前置拒绝，测试继续确认外层可成功提交，以及 owned/history 失败、仍借出指针与 abandoned cleanup。
- `development-production-tests2.log` 虽显示 52 passed，却有 8 条 SAFE ASSERT，**不算通过**。
  qint32 极限超出现有 packed compatibility index 范围，旧路径返回 detached tile，像素正确但不满足产品索引契约。
  现 hash 显式提供范围能力，planar 入场前拒绝；同时验证合法边界和四方向越界无事务/版本/索引副作用。
  纯 canonical PageStore 的 qint32 边界回归保留，不把 legacy index 上限解释成 PageStore 或硬件限制。
- planar 最终采用行/像素有效偏移，不在末行/末像素把带 channel 偏移的指针推进至 one-past 之外；范围端点使用宽整数。
  全矩阵在最后修改后重新运行；这是源码审查修正与功能回归，不宣称 sanitizer 资格。

## 重放与核验

```sh
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_production_mutation_20260921/run-checkpoint.mjs current
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_production_mutation_20260921/verify-checkpoint.mjs
```

runner 拒绝覆盖日志，CPU 与 Vulkan 二进制使用各自 build/bin 插件、offscreen 及源码 `_install` prefix。
完成构建/链接后才运行完整 14 套、paint-device 选定 7 槽、此前九组及新增 production-regions/batch-failure 各 40 次。
首次 `--capture` 建 live manifest，默认核验 source、binary/plugin、文档链接和日志；旧目录不回写为新源码资格。
计时含诊断/并发/故障，不用于性能结论；完整结构和主干 M/驻留 K/交接 X/操作 E 仍未结清。
