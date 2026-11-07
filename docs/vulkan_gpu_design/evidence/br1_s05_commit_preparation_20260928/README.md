# JP3 收敛批：成功提交后的清理释放 publication 锁

最终交付仅是匿名 root **成功安装后的 cleanup**，由 [92 §16.5](../../92_br1_m6_m8_execution_baseline.md#jp3-commit-preparation)裁决；[收敛清点 §8](../../br1_modification_guide/CONVERGENCE_CHECKLIST.md#jp3-delivery)列目标、处置、停止条件和下一批。目录名保留最初准备外移实验的名称，不表示该候选已交付。

## 最终改动与质量口径

最终改动 5 个生产文件、2 个测试文件。生产增加 27 / 删除 3，**净增 24 行**；测试增加 85 行，覆盖 16 组 BPP × packed/cursor × cold/warm。没有新增事务、selector 回调、长期候选或 writer 表；没有放宽原并发写断言。新增的私有同步入口只借用 backend 的原 RAII publication 锁，root/metadata 安装成功后先解 Store owner，再解 publication 锁并清理；失败和准备继续沿原路径。

逐项增量见 [补丁](final-increment.patch)和 [统计](final-increment.json)。完整未提交范围见 [124 文件清点](inventory-final.md)和 [JSON](inventory-final.json)：90 个生产 C/C++ 文件净增 7,833 行，25 个测试/注册文件净增 11,086 行；生成审计文件分列。这里都是相对产品 HEAD 的工作树增量，不是整个 BR1 相对 upstream 的规模或质量分数。

最终 HEAD 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`，含 6 个未跟踪源码的差异 SHA-256 为 `fd89833d8f20e5532b9f184f8d77e3c16199e3adb3e2646163eef36fa7e14220`。QtCore、测试和运行库身份见 [最终 identity](checks-02/identity.json)。架构图机械生成，原 intrusion 上界没有提高；[结构检查](architecture-refresh-02.log)记录 19 个受限外部文件不变。

## 修复前反例与最终验证

- [修复前日志](install-arm64-before-02.log)中冷/暖 cleanup reader 都不能在观察阶段完成，之后仍能读取合法结果，证明是外层锁阻塞。[身份核对](before-binary-match.json)确认 QtCore、kritaimage、kritapigment 与 JP1 冻结二进制一致。该探针的现场 dirty-source 字段不是旧二进制源码身份；旧源码以 JP1 冻结记录为准。
- 最终 `testPageStoreCommitCleanupAllowsReader` 断言 cleanup reader 完成、新字节 `0x61`、canonical extent `64×64`、旧 view 保持 `0/0x31`、最终无活跃事务。每架构所选测试 **18 passed / 0 failed / 0 skipped**，含 init/cleanup。日志见 [arm64](cleanup-final-arm64-kis_tiled_data_manager_test.log)、[x86_64](cleanup-final-x86_64-kis_tiled_data_manager_test.log)。
- 原产品并发写各架构连续 5 次保留原成功及 `<10,000 ms` 断言，共 10 次通过，见 [运行清点](cleanup-progress-final.json)。这些是进度回归检查，不是正式性能数据。
- 最终原 20 个目标 × arm64/x86_64 完整矩阵合计 **9,186 passed / 0 failed / 0 skipped**，架构检查、6 项 reachability 自测、最终 no-op 构建和源码身份检查通过。实际结果见 [manifest](checks-02/manifest.json)，对应 [运行器](run_checks.py)与 [driver](checks-driver-02.log)。原 20 个目标在 arm64/x86_64 下运行；运行器确认源码和构建未再改变。
- [最终探针清点](probes-manifest-02.json)包含 12 次有通过断言的回归运行，以及 2 次 reader-window 的**已知缺口复现**。后者退出码 0 只说明探针运行成功，不能计为联合可见性修复。记录原 root/cursor、overlay 安装/拒绝、adapter 交付/拒绝和本批 cleanup 读；没有把未重跑的原 66 项全部移用为新资格。

## 已撤回候选与失败证据

1. 固定三次候选重准备后拒绝：原独立页并发提交和产品并发写失败，见 [CPU 失败](checks-01/arm64-KisPageStoreCpuMutationTest.log)、[产品失败](checks-01/arm64-KisPageStoreReferenceTest.log)。该矩阵在确认设计失败后停止，见 [停止记录](checks-01/stopped.json)，不作为完整矩阵。配套的重复 prepare 规则也已撤回。
2. 去掉次数限制后继续把全部 root 准备放锁外：持续 reader 下原产品进度断言失败，记录为 14,950 ms，见 [失败日志](progress-x86_64-KisPageStoreReferenceTest-01.log)；隔离复查第 3 次运行在 45 秒超时，见 [未完成日志](isolated-progress-x86_64-02.log)及 [超时记录](isolated-progress-timeout.json)。候选补丁保存在 [rejected-preparation.patch](rejected-preparation.patch)，最终生产代码不含其 callback、额外取锁或候选状态组合。
3. 该候选的外层 gate 探针还捕获一次 free，见 [x86_64 日志](install-x86_64-commit-gate-after-01.log)。随后带 free 栈的单次诊断未复现，见 [诊断](install-x86_64-free-diagnostic-01.log)；没有据此抹掉失败或宣称完整零释放。
4. `before-driver.log` 是缺少 interposer 文件的探针启动错误；`build-05.log` 是收缩改动时声明放错类的编译错误。两者已修正并保留，均不作为有效行为证据。

隔离复查使用原 `KisPageStoreReferenceTest tiles3BackendCoalescesConcurrentProductWrites`、`arch -x86_64`、offscreen 与 seed 12345，每次 subprocess 设置 45 秒 timeout；前两次 1.341/1.243 秒，第三次超时被终止。进度失败未通过放宽时限处理，最终实现恢复原锁内准备后重新验证。

## 剩余范围与复现入口

当前代码仍在准备期间持 publication 锁。完整短 gate、持续读下的重准备进度、history/checkpoint/abort/restore、page/extent/adapter 联合可见性、业务持久 owner、完整资源、ON/OFF 产品配置、主干不劣性和 M6/M7/M8 均未完成。下一主线是已复现的 reader-window 联合一致性；若准备外移成为必要改动，先提供持续读下原 owner 的进度与拒绝接续。

```sh
python3 docs/vulkan_gpu_design/evidence/br1_s05_commit_preparation_20260928/run_checks.py checks-03
python3 docs/vulkan_gpu_design/evidence/br1_s05_commit_preparation_20260928/run_probes.py 03
```

运行器拒绝覆盖同名证据；源码变化后旧 identity 不授予新资格。最终文档链接检查只证明可定位，不授予生产或性能资格。

最终文档核验覆盖 38 份文档；局部链接、锚点与源码行界限通过。记录见 `document-check-final-02.json` 及 `validation-final-02.json`，检查范围不包含 archive。
