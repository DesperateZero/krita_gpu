# BR1 packed/cursor 联合 adapter 窗口证据（2026-09-29）

本目录冻结 JP6 的一个有限实现批：普通 standalone packed write、operation-private cursor 与 history cursor 在像素执行结束后，都通过原 manager gate 完成 **canonical 发布（standalone）/保留 pending（history）与已准备的 tiles3 wrapper、cache 失效、working extent 安装**。该批关闭上一冻结点每架构 32 个冷页联合观察违例；它不覆盖 clear/remove/default/copy/restore/purge 的全部发布路径，也不授予真实 stroke、默认启用或 M6–M8 资格。

## 代码结果

- `runCpuMutationOperation` 把原 publish closure 交给可选 `AdapterCompletion`。像素 body 不持 manager 锁；completion 只包围 publish 与预备 adapter 安装。
- manager 的 `writeBytes` 和 `writePageStoreOperation` 复用原 `m_lock` 作为短完成 gate；`extent()` / `region()` 的独立读取取得同一 gate，因此不能观察到新 canonical 页与旧 working extent 的组合。
- `MutationAdapterInstalled` 在 manager gate 释放后发出，允许诊断 callback 重入，且原 standalone admission 或 history execution 仍在该时点存活。
- `OperationDelivery` 只保留已完成 standalone batch 的原 admission。旧 `finish()`、history execution 分支及两个只验证该分支的测试项已删除；没有新增具名函数。两个既有写入口各增加一个 completion 参数，导出头增加一个 callback 类型别名。
- 首字节前 adapter 准备拒绝继续不执行像素；standalone publish 拒绝不会安装 adapter；history completion 失败进入原 mutation 失败/取消责任。旧 legacy conflict 不能污染已存在的匿名 transaction。

相对 `br1_copy_bounds_convergence_20260929`，生产三文件为 **+95/-67，净增 28 行**；测试两文件为 **+31/-76，净减 45 行**。生成调用图从 1,815 个 indexed APIs / 19,661 edges 变为 **1,814 / 19,634**，callback registration 仍为 17。这里的 indexed API 是编译图节点，不等于公开 API；下降一项与删除 `OperationDelivery::finish` 及 history delivery 状态一致。

## 冻结身份与验证

- HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`
- 工作树差异 SHA-256：`7e1c6465029f5dffac8d5fb8df310df65aa1c60de63846b8b4fbc183b3bf317b`
- [源码清单](source-inventory.json)：125 个范围文件；[本批增量 patch](implementation.patch)只列相对 copy 冻结点改变的五个源码/测试文件。
- [矩阵 manifest](checks-01/manifest.json)与[运行身份](checks-01/identity.json)：20 个完整目标加 14 个选定 PaintDevice 方法，arm64/x86_64 共 **9,556 passed / 0 failed / 0 skipped**；无 tile leak warning；构建结束为实际 no-op。
- [架构检查](architecture-final.log)：21 manifest entries、25 ownership facts、16 census groups、1,814 indexed APIs、19,634 edges、19 frozen intrusion files；[源码 diff 检查](source-diff-check.log)为空并成功退出。
- 最终联合探针：arm64 与 x86_64 各 **44 scenarios / 172 observations / 0 publication violations / 0 raw violations / 0 control errors**，`--require-converged` 均退出 0。最终同源记录使用 `probe02` 文件；`probe01` 是刷新架构 graph/baseline 前的中间运行，只保留过程可追溯性。

## 探针覆盖与边界

`current-read-probe.cpp` 在 `MutationSealCleanup` 启动独立 reader：它先确认 canonical/raw 已选择新像素，再调用 manager `extent()`；该调用必须在短完成 gate 上等待。到 `MutationAdapterInstalled` 后 reader 返回，并同时看到新 extent。原 retained raw/captured read、pending/history、write-intent、冷暖页、packed/cursor 与 BPP 组合仍运行；没有通过删除控制桶取得零违例。

本批没有证明 delete/default/copy/restore/purge 都共享上述 completion。那些路径继续按各自原语义审查：不能用只增不减的 extent union 掩盖删除，不能将 working bounds 全部替换成 canonical surface extent，也不能形成 publication write → tile barrier。下一实现批先核对这些剩余 publication family 与首条 direct stroke 的实际依赖；不再重开本批已经闭合的 packed/cursor add 窗口。
