# BR1 painter 显式目标写操作

本目录验证真实 `KisPainter::bitBltImpl` 的目标写迁移，不是性能报告或核心重构整体结清。
使用 `KisPaintDevice::applyPixelOperation`，经坐标/wrap 适配和目标范围预约，进入一个操作私有 native 目标写游标。
不复用 compatibility tile writer；范围内首次访问准备 pending backing，同一操作重访复用，最终统一 seal。
`KisPixelWriteCursor` 不含 oldRawData；源/历史输入独立捕获。早期通用 random-accessor 接线已替换为直接 mutation guard，
不额外取得未消费的目标 before-image View/pin。`initial-*` 是替换前的定向通过，不外推为最终实现资格。

## 路由与失败边界

- 目标已有 legacy write intent/lease：执行 callback 前返回 Borrowed，产品保留原兼容语义。
- 其他 native 操作预约：不持部分目标等待全范围可用；同线程重入保留范围直接失败，不死锁、不降级。
- native 路由显式取得指定 provider 的 mutation，不因 begin 失败选择 generic。callback 失败、游标获取失败及超范围访问均取消私有段；失败后不 replay。
- callback/accessor/pointer 是同步借用；source/mask 在自身 View 内读取，不能在 callback 内重入目标写。
- 调用方 history 中既有 sealed 修改保留；owned batch 的终结沿用现有匿名事务/client 协议，不把它说成所有并发 producer 的独立事务。
- 发布成功才刷新实际 touched keys；范围预约不是原位 permit，legacy 借用不会被撤销。

共享匿名事务的负向回归实际发现两条路径的丢数据：外部 tile writer 保持 client、此前操作已 seal 后，
新操作或既有 CPU batch 取消私有段却连带 abort 整个匿名事务。`client-negative-*` 中这两例均丢失已成功页，
外部 unlock 出现 SAFE ASSERT；painter 其余 84 项、目标操作其余 37 项通过。
修复仅在 canonical cancel 确认私有段已撤销时正常归还本 client，操作本身仍返回失败。
无法证明私有取消或可能已发布的失败继续事务级 abort；不以“忽略所有 abort”修测试。

## 构建与验证

`run-checkpoint.mjs build <新标签>` 顺序构建 CPU 和 Vulkan 相关目标；全部结束后才运行 focused/full。
focused 包含 painter 产品用例及新目标操作用例；full 包含 15 套完整测试、7 个 paint-device 选定槽及 12 组各 20 次重复。
脚本拒绝覆盖已有标签。初次 compile 中新增测试误用了被 KisDataManager 隐藏的 clear 重载，编译失败记录保留；
随后改为现有公开坐标参数接口，未修改生产 clear 语义。

最终以 `closure-build` 和随后 `closure-*` 为准：15 套完整测试 **951 passed**（painter 99、tiled manager 291），
paint-device 选定 **9 passed**；12 组各 20 次、**240 次重复**，合计 **256 个测试进程**，均通过且无 SAFE ASSERT。
Qt totals 含 init/cleanup；重复进程不混入完整套件 totals。共新增 46 个数据场景，完整矩阵见 [67 §20](../../67_br1_target_structure_reconstruction_20260920.md#204-正确性验收与版本边界)。

`verify-checkpoint.mjs --capture` 一次性保存当前源码/二进制/文档及日志 hashes，后续不带参数复核。
它核对全部测试清单、负向两例、构建先于测试、painter/iterator 实际加载库与插件、架构、whitespace 和本地文档链接。
旧检查点不覆盖，D11/D12 仅 archive-only；本记录明确 structural_completion=false、performance_qualification=false。

## 相位及剩余工作

`pixel_operation_range_prepare/wait/body/finish` 是业务区间，不等于纯 owner 锁耗时；wait 入口仍持 backend registry mutex，
测试 observer 只允许发信号，不得重入 backend/owner。等待释放该 mutex，body 进入时不持它。
prepare 仅覆盖 backend 集合/预约与 native 准备；此前 DataManager 矩形扫描、wrapper 探测、首份去重集合和 m_lock 等待
仍在 painter prepare/E，未单独隔离，不能归零。callback 前失败的收尾也留在 prepare。
finish 包含 callback 后的 seal/owned finish、私有 cursor 和范围预约释放，不含外层索引更新前的 m_lock 等待或
changed-key 缓存更新；更新自身由 mutation_index_refresh 另计。
新的 painter_bitblt_finish 覆盖调用方 callback 返回后的上述终结及缓存刷新，仍不是最终后台 drain。
所有嵌套相位为 inclusive，不重复相加；并发/observer 的正确性日志不是性能样本。

范围分类、QSet/预约表、输入 View/pin、每页 proof 和 map 安装仍有成本；没有无锁、零软件开销或性能不劣性结论。
原位 permit、全部 multi-dab/fill/line producer、legacy 借用归属的最终迁移、单页历史及回收总预算仍开放。
完整 M/K/X/E、RAM/显存/UMA 分离验收仍待整体结构完成。
