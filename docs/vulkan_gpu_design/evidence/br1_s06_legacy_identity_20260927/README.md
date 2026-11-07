# S06.3：Legacy canonical 读缓存的身份与短 pin 接线

本批实现 provider 签发的 expected cache、canonical 暖读重新取 pin、manager refresh 的缓存存储复用、独立写入结束后的缓存移交，以及 detach/dead 的 bridge 断开。它不完成整个 legacy/raw consumer 迁移，也不授予 M6/M7/M8 或 BR1-PERF 资格。当前要求及剩余责任见 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)，函数关系见 [03b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03b_legacy_cache_migration.md)。

## 源码与构建身份

- HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09` 加累计工作树；完整源码为 [source.patch](checks-01/source.patch)。
- 源码补丁 SHA-256：`8017105a9dfb79ba74bab614cf3690e7bdfbbc0b097003bcbc920dd7b17b2100`。
- image dylib：`c8a82a1ee3ce52bf16af46788f0aa84b56c5f004761461527364e01375c26cb8`。
- UI dylib：`f20fe2f83feab2784405119e7a2650d5c2fc2bc9c16765905c182f596e5d33bc`。
- [identity.json](checks-01/identity.json)记录构建配置、环境、库及全部测试 binary 哈希；[manifest.json](checks-01/manifest.json)记录各命令、终态和原始日志。
- [legacy-identity.patch](legacy-identity.patch)对照接口草案写入前的 13 文件快照；[incremental-review.json](incremental-review.json)列出范围。生成的调用图、ownership 和 baseline 则由完整 source.patch 绑定。

最终运行期间源码和构建均未变化，末尾 dry-run 无待构建项。各 allocator 探针与矩阵使用相同 image dylib；探针 identity 记录其自身编译、链接、运行命令和哈希。

## 实现及边界

`Tiles3TileReadCache` 只保留 stable binding、expected identity 和非 owning TileData 指针。factory 验证原 native guard / generic read lease；native 还核对同 provider 的 binding 对象。每次外层 read 在 binding gate 内重新校验和取 pin；最终 unlock 归还 pin，闲置 cache 不保留 root 或 RAM pin。嵌套 lock 共用原能力。

manager refresh 用 `takeIdleReadCache` 回收闲置对象并清 ready，再通过原 ReadPage 签发、安装；活跃借用不被撤销。独立 writer 在有效 guard 下准备未来缓存，原 finish 成功后才移交；活跃旧 reader 不被挪用。bulk caller 未请求缓存时不增加该对象。

真正 identity 失配拒绝访问；Busy/资源不可用不转读 current。Retired 表示原 binding 已永久关闭，wrapper 仍持有原 TileData 的 COW 引用，因此可按旧 immutable 存储读取而不重连当前坐标。detach/dead 清 bridge，已有指针及 clear barrier pin 保持到原 unlock。**这一行为依赖仍存在的 TileData 强引用，不能先放宽 refs/users。**

iterator/batch 的 tile unlock 只归还 guard，mutation 中的 writer 可能仍 Reserved。它尚未接成新身份缓存，继续原 raw/TileData 保护；不能将 Busy 改为“允许读”，也不能在这里另加 seal。后续须接原 mutation borrow、原 exact 选择的重解析、idle 引用释放和 raw consumer 生命周期。活跃物理 pin 导致退休拒绝后的自主唤醒仍须由 S09 闭合；本批不证明无后续编辑时债务自动收敛或完整 S10 计账。

## 最终验证

| 项目 | 结果 | 证明范围 |
|---|---|---|
| 17 目标 × arm64/x86_64 | 各 2,741 passed；合计 **5,482 passed，0 failed / skipped** | 累计 CPU/业务正确性；新增每架构 16 个 manager 和 12 个 physical cache case |
| architecture 与工具自测 | 1,536 APIs、15,156 call edges；21 manifest / 22 ownership / 16 census / 19 intrusion；6 自测通过 | 没有新增状态 owner；布局上限未提高 |
| ratchet | kis_tile.cc 标识符计数 10→9，其余原始字段不变 | 使用同一 opaque lease alias，未向 tiles3 暴露 provider identity；[检查结果](ratchet-check.json) |
| canonical 暖读 allocator | 每架构 96 区间，**98,304 次外层读、196,608 次含嵌套的 read lock**；allocations/bytes/frees 全零，正控制为 4 | 1/4/8/16 BPP × 初始读 / 独立写后读 / manager refresh 后读 × 8 cycles，每区间 1,024 次外层读 |
| 生产联合 install allocator | 每架构 **31,080 区间**，成功、physical 拒绝、metadata revision 竞争各 10,360；allocations/bytes/frees 全零，正控制为 4 | 同一生产五条入口、commit/cancel、1/64/65/129 页；不是 M7 多页原子批 |

manager 测试直接验证 canonical 暖缓存无新增 request/capture、nested lock、swap/unpin、独立写后读、detach、真实 hash 替换及 oldData 在 history purge 后仍读旧值。物理测试验证 cache 对象复用、读 pin 对 swap/claim/retire 的排斥、writer Busy、真实 retag 后 Stale，以及 retire/revoke 后 Retired；该物理 fixture 没有 PageStore root，不代替生产 M6。

暖读区间包含 lock、pin、嵌套 lock、读取像素和 unlock；不包含初建缓存、写入、refresh、swap-in、publication 或最终销毁。联合安装区间沿用 `RecoverableInstall` 至 `RecoverableInstalled` / 拒绝时 `RecoverableCleanup` 入口，包含 claim、metadata、retag、ledger、descriptor 消费；不包含准备、pixel kernel、adapter 返回、seal/root publication 和 deferred cleanup。两类探针都不是端到端时间或吞吐结果。

最终日志：暖读 [arm64](install-arm64-warm-final.log) / [x86_64](install-x86_64-warm-final.log)，联合安装 [arm64](install-arm64-joint-final.log) / [x86_64](install-x86_64-joint-final.log)。汇总与库身份一致性检查见 [result-summary.json](result-summary.json)。

## 保留的中间失败

- [build-01](build-01.log)：强类型 ID 不提供 `!=`，改用既有 `==` 契约。
- [build-03](build-03.log)：测试对 move-only access 使用了已删除赋值；改为第二个具名 capability。
- [targeted-02](arm64-targeted-02.log)：44 passed / 4 failed，fixture 错把 canonical clear 当作 wrapper 替换。实际 clear 原地刷新；现通过真实 hash `addTile` 替换触发 `notifyDeadWithoutDetaching`，完整 manager 矩阵通过。没有为满足错误预期修改 clear 语义。
- 初始 [targeted-01](arm64-targeted-01.log)、[physical-cache-01](arm64-cache-physical-01.log)、[manager-01](arm64-manager-01.log)及首次 warm 探针保留为开发检查点；最终资格仅引用上面的冻结矩阵与 final 探针。

## 复现

在工作区根目录运行；每次使用未存在的 tag，脚本拒绝覆盖证据：

```sh
python3 docs/vulkan_gpu_design/evidence/br1_s06_legacy_identity_20260927/run_checks.py checks-NEW
python3 docs/vulkan_gpu_design/evidence/br1_s06_legacy_identity_20260927/run_install_probe.py arm64 warm-NEW warm-tile-read-allocation-probe.cpp
python3 docs/vulkan_gpu_design/evidence/br1_s06_legacy_identity_20260927/run_install_probe.py x86_64 warm-NEW warm-tile-read-allocation-probe.cpp
python3 docs/vulkan_gpu_design/evidence/br1_s06_legacy_identity_20260927/run_install_probe.py arm64 joint-NEW joint-install-allocation-probe.cpp
python3 docs/vulkan_gpu_design/evidence/br1_s06_legacy_identity_20260927/run_install_probe.py x86_64 joint-NEW joint-install-allocation-probe.cpp
```

源码有新变化时先生成对应调用图并通过原 architecture ratchet，不能直接复用本批 generated artifacts。所有测试构建配置和参数见脚本及 manifest。

**仍缺：** batch 内权限、idle cache/raw consumer 全迁移；M6 完整准备故障/epoch/晚 completion/压力/退出；S09/S10 自主进度和完整实际收费；M7 fence；M8 persistent stroke scope、剩余失败/可见性/undo/context；真实 stroke replay、Fresh 2% 回退、Vulkan/TSAN 与正式 BR1-PERF。完整实施目标继续进行。
