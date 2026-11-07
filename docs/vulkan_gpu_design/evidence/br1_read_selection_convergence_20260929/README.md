# JP5/S04 六处读取选择的 API 收敛

本批落实 [API 映射 §3](../../br1_modification_guide/API_CONVERGENCE_MAP.md#read-selection)的第一个实施单元。此前文档规划属于有实际状态变更的进展；本次转为生产重构，完整 BR1/M8 目标保持。

## 改动与删除

生产只修改 `KisTiledDataManagerPageStoreBackend.cpp`，相对 JP5 增加 24 行、删除 38 行，净减 14 行。原 Private 内增加 `selectReadViewLocked(bool oldData)`，六个入口删除同源的 history/anonymous/committed 选择分支：`captureIteratorReadScope`、`captureReadView`、`resolveCurrentPagePresenceInto`、`selectCurrentReadTile`、`acquireTile`、`pageAllocated`。iterator 同时需要 current 与 before，因此六个入口共有七个 helper 调用点。

这不是六个入口全部删除：入口的读取能力和寿命不同。合并的是唯一选择政策；不增加公共声明、字段、friend、TLS、事务、session 或 write set。原 operational/访问模式检查、iterator 是否捕获 before、live legacy 旁路、Store 联合 version/default 查询、cache 版本与物理 pin 仍在原处。

锁范围不变：所有 helper 调用均在原 `d->mutex` 下，只计算选择值；捕获/解析前的 publication 保护由原 caller 维持。helper 不分配、不 capture/freeze、不取得 pin、不调用回调或新增等待。`acquireTile` 的 writable 分支继续原有保护方式，不能把该纯选择值当作新写入权限。

[生产增量](production-increment.patch)和[改动前源码](backend-before.cpp)保留精确替代关系。原 JP5 清点的 124 个范围内文件在修改前全部匹配，见 [改动前身份](before-identity.json)。调用图/架构刷新只更新源码与结构事实，原侵入上限、ownership/manifest/census 责任不放宽；这项审查不授予行为或性能资格。

## 验证范围

复用已有 manager、iterator、read baseline、resident read、transaction、painter、stroke completion 七个产品测试目标，分别运行 arm64/x86_64；不新增镜像实现的 helper 单元测试。测试覆盖旧读/新读、base/captured、legacy、default/关闭/拒绝、adapter、提交进度及实际 painter 消费。运行入口为 [run_checks.py](run_checks.py)。

沿用原 [reader-window 探针](../br1_s05_fresh_read_20260928/current-read-probe.cpp)，用 [run_read_probe.py](run_read_probe.py)记录新二进制上的 raw 正确性与仍开放的 manager extent；不能把预期的整体验收失败转成“整体收敛”。沿用原 JP5 暖读取分配探针，通过 [run_install_probe.py](run_install_probe.py)检测零额外分配/capture/generic request；这不是全链性能证据。

最终七目标 × arm64/x86_64 为 **4,116 passed / 0 failed / 0 skipped**；6 项调用图工具自测、架构 gate 与实际 Ninja no-op 通过。源码差异 SHA-256 为 `740dd7f48e86c7111dfb98b429782d9fdf3a015dc725980874c9b463fd50ac0d`，运行身份见 [identity](checks-01/identity.json)，逐目标命令/结果见 [manifest](checks-01/manifest.json)。本次没有重跑此前的全部 20 目标，也不将旧测试数累加到新结果。

每架构原窗口探针仍为 44 场景/172 个观察点：raw 违例 0、控制错误 0，**manager extent 仍有 32 个不一致观察点**，整体 `--require-converged` 仍返回 3；这是保留的已知缺口，不是整体通过。每架构暖 getter 16,384 次，分配/释放/capture/generic request 均为 0，8,210 字节分配正对照通过。冷失配/旧读持有下的新 wrapper 成本和全链锁/性能不在该零值范围内。

生成图为 87 TUs / 1,810 indexed APIs / 19,599 edges / 17 callbacks；indexed API 包括新增的内部 helper。原 21 manifest / 25 ownership / 16 census / 19 intrusion 通过，未改上限。唯一生产改动和两份生成审计文件见 [源码范围](source-inventory.json)，六个调用者/七个调用点见 [Clang 索引证据](selector-callgraph.json)。最终 [核验结果](validation.json)、[文档检查](document-check.json)、[核验脚本](validate_final.py)与[文档增量](documents.patch)绑定同一源码/运行库，不覆盖旧证据。

## 剩余与停止条件

本单元以“重复政策已删除且既有行为保持”为出口。下一个实际交付仍是 JP6 bounds/caller/adapter，联动单次交付接口；当前修复不关闭 extent 窗口、不接默认持久 brush owner，也不改变 M6/M7/M8、预算、OFF 或正式性能要求。已合并的选择规则没有新反例时，不再继续为它增加通用读取框架。

首轮补充 probe 的 runner 误引用 JP4 时的旧输出格式，运行后因缺少 `raw_violations` 字段报脚本错误；原日志保留在 `probes-driver-01.log`。已改为 JP5 实际使用的探针源码，以 `final-02` 重新运行；产品源码及已通过回归未改变。
