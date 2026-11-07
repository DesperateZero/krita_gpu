# Descriptor publication capacity（2026-09-21）

对应 [67 §30](../../67_br1_target_structure_reconstruction_20260920.md#30-2026-09-21descriptor-容量准备与解锁期变更复验)：
PageStore descriptor 语义增删统一推进 revision；default commit/restore 在解锁构造 metadata/root 前预留新增容量，重锁复验 revision，
最终 metadata → descriptor → root callback 断言新增 descriptor 不改变 hash capacity。

`checked-build` 的 CPU/Vulkan 两套构建通过；`checked-focus` 为 **104/75/52 passed**；`checked-full` 最终
**15 套 1336 passed、选定 9 passed、60 次重复全过，共 76 个测试进程**。Reference 291、CpuMutation 465；Qt totals 含
init/cleanup，完整套件与重复独立记账。最终无 FAIL/SAFE ASSERT/QFATAL，构建/链接与测试未并发。

```sh
node docs/vulkan_gpu_design/evidence/br1_descriptor_storage_20260921/verify-checkpoint.mjs
```

新增真实测试在 default publication 解锁点创建并取消 disjoint private generation，使 descriptor revision 改变但 directory/root 不变；
首个候选必须重做，第二次才安装，旧像素保持不变。缺失 default restore 另验证每个成功候选一次 capacity preparation、一次 installation。

reserve 本身仍在较早 owner gate 内，Qt insert 没有 allocator hook；保守全局 revision 可能因无关私有 generation 重做。completion、旧
metadata/candidate 析构、effects/postwork 和物理回收仍开放。本轮没有 benchmark、TSAN、原位 permit、完整短发布或性能资格结论。
