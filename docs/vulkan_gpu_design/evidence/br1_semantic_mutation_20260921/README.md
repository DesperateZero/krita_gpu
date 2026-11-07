# Canonical semantic mutation checkpoint

范围见 [67 §16](../../67_br1_target_structure_reconstruction_20260920.md#16-2026-09-21canonical-mutation-私有删除与像素统一安装)。
本轮是 owner 私有删除与原生像素的整段安装，并迁移生产 trim/clearAll/removePages，不是只有类型重命名或 root commit 延后。
完整 alias/fill/copy、原位 permit、画笔全部边界、完整短发布/回收预算及最终 M/K/X/E 仍未结清。

最终 `checkpoint-*` 共 575 个测试进程全部通过：14 套完整回归 569 passed、paint-device 选定 9 passed、560 次专项重放。
Qt totals 含 init/cleanup；无 FAIL/SAFE ASSERT/QFATAL。相关 CPU/Vulkan 目标及 selection-tools 插件重建、架构/diff 检查通过。
运行库路径由 loader 核验；D12/D11 封存性能证据 archive-only 核验保持不变。本目录仅作正确性检查点。

## 回归范围

- 新增 55 个 Qt 场景：pure semantics 4、mixed seal/cancel/proof failure 16、delete/rewrite reuse 16、concurrent capture 1、
  metadata candidate 1、真实 mixed trim 故障 2、clearAll/removePages 故障 4、退休中历史恢复 4、异步关闭重试 2、ledger 分类 1、
  不支持 alias 时整段取消 4。
- 旧 full-reference 差分槽增加 detach 的 16 种 read lease/pin/last-use/captured-view 组合；这些是内部子循环，不增加 Qt totals。
- 删除不改变 sealed overlay、不为 absent key 创建 metadata/payload；不支持 native CPU 的 provider 仍能执行纯删除。
  旧 View、generic read lease、只存在于旧 history 的页，在 detach/commit 后继续保持可读。
- 删除后重写复用同 generation/backing，按当前 default 初始化必要 bytes；软件重置、CPU pin、语义 removal 与 root publication 独立计数。
- 真正的 provider 锁外准备期间捕获 View；并发槽每次 128 轮交替删除/写入并持续 capture，不能看到半批。
  直接 coordinator 槽检查 owner/transaction/一次消费/两类 candidate 不可混用，以及第二页 revision 失配不安装第一页。
- 实际入口先暂存删除，再在后页被外部 writer 占用时失败：保留全部 prior history 与外部 writer，随后可重试；含 undo/redo。
- `development-build.log` 保留 const snapshot 查找重载导致的编译失败；改用既有 mutable snapshot 重载，没有去除 const 安全。
  `development-build2.log` 保留测试引用不存在的 COW 字段；改用实际 provider payload counters，并分开默认初始化/复制/adoption。
- 首轮 `current-*` 中 reference 新用例漏传 prepared-version read 的 transaction，状态机正确拒绝；修正 fixture 的身份，
  不放宽跨 transaction 读取约束。该轮不是通过资格，原日志保留。
- `verified-*` 的 14 套完整回归 558 passed，但第 24 次 iterator-lifetime 重放中 HLine/history rollback 失败，
  整轮不具通过资格。`rollback-negative.log` 将其对应的错误阻塞条件放大为四个稳定失败：已 detached 的 retirement
  ledger operation 被错误地当作历史恢复阻塞。owner 分类修复保持旧 View、source retention 与 metadata 复验。
- `close-negative.log` 的两个稳定失败说明异步 retirement 完成后 close 也无法重试；修复只放行 pre-drain 的退休项，
  必须保存 operation 并查询 terminal success，不能重发 retire 或跳过关闭债务。公开 operation 总计数未被删减。
- `rollback-negative-build.log` 保留测试直接调用 private delta API 的编译拒绝；改为真实 memento manager 稀疏恢复入口，
  未开放 private API 或添加测试 friend。`rollback-negative-build2.log` 及后续构建成功。
- `repaired-*` 的 14 套完整回归 565 passed，但 5 次 retirement-history 重放中测试假设手动 drain 必然处理两个记录，
  忽略恢复触发的后台 history worker 也会轮询退休队列。修正 fixture：在确认 ticket 前等待历史/退休任务 idle，
  再严格检查手动退休 2 项、不重发调用、总 ledger 归零；没有把期望放宽为 0 或 2，该轮日志保留。
- `batch-negative.log` 四个稳定失败覆盖 owned/history × 显式 finish/析构：此前 private batch 拒绝未支持 alias
  后仍可 seal 已暂存的删除。现在拒绝会标记整个 private batch 失败，保留 caller prior history；不是补齐 alias 功能。

## 重放与核验

```sh
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_semantic_mutation_20260921/run-checkpoint.mjs checkpoint
/opt/homebrew/bin/node docs/vulkan_gpu_design/evidence/br1_semantic_mutation_20260921/verify-checkpoint.mjs
```

runner 拒绝覆盖，构建/链接全部结束后运行，CPU/Vulkan 各用对应 build/bin、offscreen 和 `_install` prefix。
14 套完整回归、paint-device 选定槽、14 组各 40 次重放；首次 `--capture` 保存源码/运行库/插件/日志/文档 live manifest，
默认校验 hash、测试 inventory、运行库路径和本地链接。未来源码变化使 live checkpoint 失效，不回写旧 manifest。
计时含诊断、故障和并发，不是性能数据；无 TSAN、GPU/UMA 或最终 M/K/X/E 资格。
