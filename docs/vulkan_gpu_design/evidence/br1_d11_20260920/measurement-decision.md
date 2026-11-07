# D11 upstream 装载纠正（有效 upstream 计时开始前）

初版 `run.mjs` 的 D10/D11 比较已完成，二者可使用同一 native fixture 二进制。
但 upstream loader 检查立即失败：候选 fixture 引用 out-of-line `KisTiledDataManager::commit()`，
固定主干头文件却内联该方法，不提供相同符号。失败原件保留在 `native_reference-paired/`，**没有取得有效 upstream 计时结果**。
这也纠正 `identity.json` 的简写：对象/接口兼容描述仅适用于 D10→D11，不适用于 PageStore 分支→原主干。

按 D5 的同源方式纠正为 `run-v2.mjs`：两侧使用 byte-identical fixture source，在各自头文件/源码下编译的
独立 executable + 对应冻结 runtime；实际库由 loader 验证。新输出为 `native_reference-v2-paired/`。
`identity.json` 已包含两套 executable/runtime hash，源码 fixture hash 在 snapshot 时逐字比对；不替换身份，不调整
cases、8 pair、200 ms 窗口、统计或停止规则，不排除性能样本。`run.mjs` 保留原版，D10/D11 的 manifest hash 继续可核验。

本纠正是 ABI 装载修正，不是性能优化；不能把“同一 fixture 源码”写成所有公共 tiles3 对象布局完全相同。
