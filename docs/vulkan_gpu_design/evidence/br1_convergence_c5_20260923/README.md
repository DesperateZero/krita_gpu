# BR1 第五批：可达性驱动的孤立层清理

对应 [84 第五批](../../84_br1_full_optimization_convergence_and_cleanup_20260923.md)。`c5` 是批次号，不表示 C5 metadata 全面验收。
本批范围完成；C2–C5 的全链路协议、预算和性能资格仍未完成，不授予 BR1-PERF Pass。

## 实际收益

| 范围 | 新增 | 删除 | 净变化 |
|---|---:|---:|---:|
| 生产 `.h/.cpp` | 14 | 895 | -881 |
| 构建项 | 0 | 1 | -1 |
| 测试 | 170 | 224 | -54 |
| 两个审计脚本＋工具回归 | 193 | 2 | +191 |

PageStore **32,225 → 31,344 行**；五批生产累计净减 **2,205**（PageStore 自身累计 -2,207，第二批外围诊断 +2）。
没有新生产文件；删除 Shadow 两个文件。没有把生产实现搬到测试后计作删除收益。

## 状态与职责裁决

- metadata 的独立 reserve/bind/reject/queue/drain 调度层仅由旧测试产生工作。移除其 shard materialization map、
  completion queue、两个 seen-ID 集合、identity mutex、序列/统计、page activity 分量和 Store 的恒零投影。
  部分 getter/guard 原本有生产调用，删除依据是其唯一生产者不可达、状态恒零，不是这些 getter 自身零调用。
  Store 的真实 default preparation、read request/lease、owner operation、verified completion、预算和关闭边界保持。
- Shadow 观察器的 digest→observed generation、影子 default/extent、独立 map/mutex 整体退出。
  其测试现直接检查 backend/captured read/provider 的真实版本、共享 backing、clone COW、负坐标、默认 revision 和旧视图。
- 无调用的 overload/getter、未接线 tryInstall+assert 包装、自分配 prepared additions 入口退出。
  使用中的 non-const overload、reserved additions、prepared 状态、tryInstall/cancel 不变。
- `DeferredPublicationCleanup::clear` 实际被模板调用：此项是合并，不是死代码删除。
  小候选 inline cleanup 改为既有 `clearBatch(units)`，仍在原锁外终结；大候选仍按原后台预算清理。

## 引用图与逐函数记录

当前生成图包含 **1,523 API、13,430 调用点、14 callbacks、83 TUs**；退出 37 个符号，没有新生产 API。
生产/测试/间接调用分别遍历，保存前驱路径，并对非生产子图计算强连通分量；互相调用不构成生产根。
完整逐函数分类在 `krita/build-tools/ci-scripts/pagestore-audit/reverse-callgraph.json` 的 `reachability-review` 中。

自动分类为 987 个生产边界可达、314 个间接调用待复核、167 个测试可达待裁决、55 个无已知入口待复核。
这不是全程序或全配置认证：边界外 caller 被保守视为根，当前 Vulkan 构建关闭；IndexStore 仍会遗漏依赖模板中的成员调用。
因此没有把分类直接用于删除。`backingAuthority`、`clearBatch`、captured view 析构释放和 prepared publication cancel
均经过源码复核而保留；reference oracle、CPU facade、checkpoint、GPU/BR0 接口与 physical claim 契约不因测试驱动而自动删除。

[function-dispositions.json](function-dispositions.json) 记录 37 个退出符号的 USR、定义位置、原 caller 数及裁决；
另列必要的误报反例和 54 个尚待配置/契约复核的无入口候选（第 55 个 backingAuthority 已明确保留）。
该文件绑定前后图 hash，完整旧边位于源码存档，不冒充已经人工裁决了全部 1,523 个函数的必要性。

六个工具回归通过：生产文件内部环不作为根、测试不保活生产、边界传递、RAII、callback/override、非调用引用。
architecture gate 使用生成器的同一实现重算分类，拒绝手改裁决或根；原 source/config/hash/侵入上限检查保持。
内存负例确认篡改分类、移除 production roots、使用旧图均被拒绝；三个 retired 标识符命中禁回流规则。
没有提高外部侵入上限，也没有刷新固定 `convergence-start-source.json`。

## 最终验证

- 构建成功，最终 `ninja: no work to do`；当前源码 checkpoint 和 architecture gate 一致。
- PageStore/Completion 七个 ctest 全过，QtTest totals **930**：28 / 11 / 303 / 41 / 33 / 484 / 30。
- Painter **99**，tiles3 **334**，后者使用 seed 12345 并包含 stress；最终日志无 FAIL/SAFE ASSERT。
- 三个 Reference 定向测试 totals **5**；默认准备定向 totals **4**。
  65 页/64 并发背压用例保留，并增加 65 请求同页去重、唯一 ID、late request、伪造身份/重放拒绝、取消、关闭归零。
- materialization 的 reference oracle 保留成功/失败/陈旧 operation/ABA；compact metadata 验证在途 source pin
  阻止 fused retirement，普通 publication 保留保护；public metadata 的未验证 completion 拒绝仍然生效。

`reference-targeted.log` 是迁移中失败样本：尝试从 public metadata 直接提交 completion 被正确拒绝。
最终改为 reference oracle＋实际生产请求验证，没有放宽生产 gate，见 `reference-targeted-final.log`。
首次编译还揭示 clear 的依赖模板调用，已按上述共同 clearBatch 收敛处理，不将它记为零调用死函数。
保留资源/插件和 swap 环境告警；QtTest totals 包含 init/cleanup 及数据行。并行验证耗时不作吞吐结论。

## 恢复与复现

[before-source.tar.gz](before-source.tar.gz) 保存删改前完整 PageStore、两个测试、CMake、审计脚本和旧 audit 数据。
它包括两个已删除文件，可解压到独立临时目录后按需恢复；不要直接覆盖当前工作树。
临时原始快照也位于 `/tmp/krita-br1-convergence-c5-bYJ2mv`。用户原有未提交修改没有回滚或提交。

工作目录 `/Users/apple/krita_gpu/krita`：

```sh
/Users/apple/krita_gpu/.venv/bin/ninja -C _build-br0-cpu -j4 \
  KisPageStoreReferenceTest KisPageStoreResidentReadTest KisPageStoreCpuMutationTest \
  KisPageStoreFoundationTest KisCompletionRegistryTest KisPageStoreReadBaselineTest \
  KisPageStorePhysicalClaimTest kis_tiled_data_manager_test kis_painter_test
env QT_QPA_PLATFORM=offscreen /Users/apple/krita_gpu/.venv/bin/ctest \
  --test-dir _build-br0-cpu -R '^libs-image-(KisPageStore.*|KisCompletionRegistryTest)$' -V -j1
env QT_QPA_PLATFORM=offscreen KIS_BR1_SEED=12345 arch -arm64 _build-br0-cpu/bin/kis_tiled_data_manager_test
env QT_QPA_PLATFORM=offscreen KIS_TEST_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install \
  KIS_TEST_PLUGIN_PATH=/Users/apple/krita_gpu/krita/_build-br0-cpu/bin arch -arm64 _build-br0-cpu/bin/kis_painter_test
python3 build-tools/ci-scripts/tests/test_pagestore_reachability.py -v
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --jobs 4
python3 build-tools/ci-scripts/check-pagestore-architecture.py --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py
```

下一阶段重点仍是可达但重复的 provider prepare/overlay seal、entry/cold 状态、有限 Debt 退出保障及 backing/metadata
表示收敛；不能用本批 881 行减少宣称剩余实现均必要，也不能用正确性回归代替性能出口。
