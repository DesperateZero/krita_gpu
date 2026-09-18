# CPU/GPU 一致性与异步访问方案

> 旧版仅围绕“stroke end 下载 staging”设计，现已被 canonical PageStore 架构取代。本文保留 Krita
> transaction 的业务要求，不保留旧 `KisVulkanSyncStrokeStrategy` runtime。统一状态与 MVP 边界见
> [00_status_and_mvp_contract.md](00_status_and_mvp_contract.md)，PageStore 权威设计见
> [25_p0_canonical_pagestore_krita_tile_cow_swap.md](25_p0_canonical_pagestore_krita_tile_cow_swap.md)。

## 1. 统一原则

- 页面只能有一个明确的 authoritative version。
- CPU/GPU 访问通过 read/write lease 获取，不能由调用者直接 map、copy 或 wait。
- 每次写入增加 generation。
- dirty、pin、in-flight、transfer batch 和 evaluation epoch 必须可观察。
- Krita stroke/undo transaction 需求通过新 document session/commit job 接入；当前
  `KisVulkanSyncStrokeStrategy` 的 stroke-end 下载模型在 BR0 删除，不作为兼容层保留。
- stroke end 只追加 End marker 并取得 `StrokeCommitTicket`，不得暂停 render/executor 或等待 GPU。
- transaction 在新 generation 可恢复后由后台 job 发布；新笔迹通过 page last-writer ticket 排序。

## 2. UMA 路径

UMA 使用共享 mapped canonical page：

```text
GPU write
-> signal timeline
-> CPU read lease waits
-> invalidate（仅 non-coherent）
-> CPU pointer access
```

CPU 写入后：

```text
CPU write lease
-> flush（仅 non-coherent）
-> release + generation update
-> GPU barrier/wait
```

不执行画布像素 staging copy。stroke end 只封口 journal；只有实际 CPU consumer 获取 read lease 时才执行
必要的 CPU 可见性同步。undo transaction 依赖 snapshot/journal 的 Recoverable ticket。

## 3. dGPU 路径

dGPU 页面在 VRAM cache 与 RAM backing 间转录：

- GPU 写入使 VRAM version authoritative。
- CPU 消费或 VRAM 淘汰触发页级回写。
- transfer batch 返回 timeline value 和受影响 page generation。
- graphics/compute submit 显式等待上传；CPU job 只等待自己消费的下载。
- 回写失败时保留 VRAM page，禁止解绑或复用。
- 松笔不自动回写全部 dirty page；journal 与 before-image 保留到新 generation 有安全恢复来源。

## 4. SSD 路径

- SSD 路径只能是 `KisTileDataStore`/`KisSwappedDataStore` 演进出的 unified store；Vulkan 不创建独立 swap。
- 只有 RAM/UMA 中有 CPU 可读的有效 exact generation（VRAM-only 内容须先 materialize）后才能写入 SSD。
- SSD record 包含 surface/page id、generation、format、checksum。
- SSD 完成前 RAM authoritative page 不得释放。
- 恢复时先校验，再发布新的 RAM backing。

## 5. Undo/Redo

- 在第一次写目标页前创建 copy-on-write before-image。
- UMA 可以复制到同一 shared arena 的 snapshot page；压力下异步下沉到 SSD。
- dGPU 可以在 GPU 内复制或回写到 RAM snapshot，由 backend 选择。
- derived composite/cache page 不进入文档 undo，只保留 canonical target page 变化。
- transaction 只有在所有 required snapshot 可恢复时才能 commit。

## 6. 当前代码状态

已有：

- async download result；
- timeline wait；
- detached staging buffer；
- `KisStrokeJob` 内 `writeBytes()`；
- transaction commit。

未完成：

- 统一 lease/state machine；
- GPU-side transfer wait；
- UMA pointer path；
- 把现有 Krita swap 升级为 generation-aware unified SSD backing，并接入同一 PageStore；
- failure/cancel generation 处理；
- undo/save/reopen 测试。

因此当前实现只能作为 Krita transaction 业务接入和错误案例的参考。新基线不得直接延续
`flushAndPause -> download -> writeBytes` 状态机，也不能用兼容 wrapper 把它包装成 PageStore commit。

目标 stroke 时序与完成状态见 [10_gpu_stroke_foundation.md](10_gpu_stroke_foundation.md)。
Queue/ticket 细节见 [14_submission_tickets_and_queue_topology.md](14_submission_tickets_and_queue_topology.md)，
Krita canonical PageStore 接入见 [17_krita_pagestore_integration.md](17_krita_pagestore_integration.md)，transaction/保存/恢复见
[18_undo_save_cancel_and_recovery.md](18_undo_save_cancel_and_recovery.md)。
