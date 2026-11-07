# BR1 长历史续扫与局部退休

实现与限制见 [67 §23](../../67_br1_target_structure_reconstruction_20260920.md#23-2026-09-21长历史续扫与局部退休)。
生产 worker 使用有序 Historical 索引和值游标，32 records/key × 16 keys/pass，FIFO continuation 和事件驱动重扫。
局部历史/Prepared discard 执行共享安全 guards；每轮缓存全 root 可达版本，head 改变刷新，替换/完成后集合在 owner 外销毁。

## 构建和证据阶段

- `initial-build/initial-*`：CPU/Vulkan 成功后，原 Reference 211、CpuMutation 346 通过。
- `indexed-build-*`：新测试链接失败，x86_64 找不到 private `kisSchedulePageStoreReclamation` 的导出符号。
- **`indexed-*` 测试不可用于本轮实现验证**：在上述失败之后误运行到旧二进制，仍为 211/346；日志原样保留并由 verifier 排除，不能宣称新增回归通过。
  调度器仍是 private runtime/test 边界，补齐符号导出供确定性排队 barrier；不授予 page mutation 权限。
  runner 增加“最新 build 必须两套均成功”的前置门禁，防止再次误跑旧二进制。
- `guards-build/guards-*`：重新完成两套构建，新增场景确实进入二进制；Reference **237**、CpuMutation **358** 全部通过。
- `final-build/final-*`：加入空切片不刷新 root 缓存，以及活动 sweep/cache 债务计数；15 套 1133 passed、选定 9、360 次重复通过。
  随后仅加固测试早退时 barrier 捕获对象的生命期；此批保留为上一测试源码版本，不用来替代最后一版的重新验证。
- `verified-build/verified-*`：按最后源码重建并重跑完整矩阵，为当前检查点输入；同时重建两个 CPU benchmark consumer，
  避免新增统计结构后遗留旧 ABI 可执行文件。只构建，不运行性能采样。

最终 **15 套 1133 passed**、paint-device 选定 **9 passed**、**360 次重复**全部通过，共 **376 个测试进程**。
Reference 237、CpuMutation 358、painter 99、tiled manager 291；Qt totals 含 init/cleanup，不将重复混入完整套件总数。
最终无 FAIL/SAFE ASSERT/QFATAL。`verify-checkpoint.mjs --capture` 一次性生成 final-manifest，之后无参数核验，不覆盖旧检查点。

runner 拒绝覆盖标签；所有构建结束后才跑测试，不与链接重叠。full 清单为 15 套、paint-device 7 个选定槽、18 组各 20 次重复。
verifier 核对源码/二进制/文档 hashes、阶段时序、失败/旧二进制排除、实际库/插件、oracle/长历史矩阵、架构与文档链接；
旧检查点不覆盖，D11/D12 仅 archive-only。所有正确性耗时均不是性能样本。

## 新增证据与限制

新增 38 行：6 个 history cursor 边界、20 个 historical/superseded discard guard、8 个真实长历史矩阵、4 个跨 pass 恢复再写。
H=65/257 × BPP=1/4/8/16：切片最多 32，保留轮 reachability 刷新 1–2 次而非逐切片刷新，最终精确移除 H 条，metadata 全页导出为零。
旧 View/pin 可读，最后释放后 debt/cache/physical bytes 正确清理；跨 pass 恢复旧 generation 再写不会漏掉游标之前的新 history。
退休 effects 按集合比较，不把不同合法退休顺序当成安全差异。

GC 已进入局部 metadata 计数；backgroundLocal* 为总数子集，native 首写断言用前台差值，不能从完整 E/drain 中扣掉后台成本。
32×16 只约束历史记录枚举，不约束 root 集合扫描、每版本 replica/保护列表、哈希/有序索引分配、缓存构造或总积压。
原位 permit、全部 producer 迁移、短发布/回收总预算及最终同义主干 M/同域 K/实际跨域 X/完整 E 尚未完成。
structural_completion=false，performance_qualification=false；没有 TSAN/全局无锁或性能等价资格。
