# 虚拟纹理统一 SSD Segment Store、耐久性与恢复方案

> 本文定义 `kritaimage` 中唯一 SSD replica store。它由现有 `KisTileDataStore`/
> `KisSwappedDataStore` 演进，不属于 Vulkan backend，也不替代 Krita 文档格式。PageStore 提交语义见
> [33_virtual_texture_pagestore_state_machine.md](33_virtual_texture_pagestore_state_machine.md)。

## 1. 决策

最终方案：

```text
append-only segment files
+ versioned per-record header
+ exact PageVersion index
+ commit sequence / manifest
+ per-record checksum
+ async batched I/O
+ background live-record cleaner
+ SessionSpill / RecoveryCheckpoint durability classes
```

不保留当前 mmap window + 可变 chunk allocator 作为 production store。可以迁移现有 LZF codec、格式语义和测试样本，
不能迁移“写入后立即释放且无 generation/index 校验”的生命周期。

## 2. 作用域

SSD store 保存运行时 PageVersion replica：

- canonical cold page；
- COW/undo retained generation；
- immutable save/recovery 所需 generation；
- 仅在重建收益足够时保存 derived cache。

它不保存：

- Vulkan pipeline/driver cache；
- brush source 的唯一正式文件；
- Krita 文档正式序列化格式；
- 没有 PageVersion/format 的 backend 私有 blob。

全项目只允许一个 page record index、预算和 GC owner。

## 3. Record format

```text
RecordHeader
  magic
  record format version
  header length
  flags / durability class
  DocumentSessionId or store namespace
  SurfaceId
  LogicalPageId
  Generation
  SurfaceFormatId
  CodecId / CodecVersion
  ChecksumAlgorithmId / ChecksumVersion
  UncompressedSize
  CompressedSize
  EncodedPayloadChecksum
  CanonicalContentChecksum
  HeaderChecksum
  CommitSequence
  PayloadOffset/alignment

Payload
```

要求：

- 整数编码、endianness 和对齐固定并版本化；
- 未知 version/codec/format 不可发布为 Valid replica；
- 未知 checksum algorithm/version 不可接受 record；具体算法可由 benchmark选择，但必须写入 header且同一 record 内固定；
- `EncodedPayloadChecksum` 覆盖落盘后的 encoded payload，在 decode 前发现短写/位翻转；
- `CanonicalContentChecksum` 覆盖解压后的 canonical uncompressed bytes，保证 codec/格式恢复精确；
- default/solid page 使用规范 special record，不省略 SurfaceFormat/default generation；
- record 不保存裸指针、allocator 地址或 GPU handle。

## 4. Key 与 index

主键：

```text
(StoreNamespace, SurfaceId, LogicalPageId, Generation)
```

index value：

```text
SegmentId / RecordOffset / RecordLength
Format/Codec
EncodedPayloadChecksum / CanonicalContentChecksum / HeaderChecksum
CommitSequence
DurabilityClass
State = Committed | Superseded | Corrupt
```

内存 index 是加速结构，持久恢复依靠 committed segment metadata/manifest。不能仅把 `KisTileData*` 或 chunk offset
当 key。

旧 generation 只有在 PageStore 确认没有 undo/save/reader/transaction reference 后才可从 live set 移除。

## 5. Segment layout

- segment 顺序 append，达到目标大小后 seal；
- record 独立压缩，保留随机页读取；
- 多 record 在 I/O 层聚合为大 write/read；
- segment header/footer 记录版本、sequence range、record count 和校验；
- active segment 只有一个 append owner 或确定的 offset reservation protocol；
- partial tail 在恢复时通过长度/checksum/commit sequence 截断或忽略。

segment 目标大小、I/O alignment 和最大并发是策略参数，不进入 record identity。

### 5.1 Commit log

index/manifest 使用单调 commit sequence 的 append-only commit log：

```text
CommitRecord
  CommitSequence
  PreviousCommitSequence
  added/replaced record locations
  retired segment ids
  durability class
  record checksum
```

- SessionSpill commit 在 payload I/O completion 后进入进程内有效 index；commit log 是否落盘不提升其 crash 等级。
- RecoveryCheckpoint 先使 payload/segment metadata durable，再写 CommitRecord 并执行 manifest durability barrier。
- recovery 只接受 checksum 正确、previous chain 连续且引用完整 record 的最高 commit sequence。
- GC switch 也是 CommitRecord；旧 segment 在 commit durable 且 reader ref 释放前不删除。
- 可以使用周期性完整 index checkpoint 缩短恢复扫描，但它只是 commit log 的可验证快照，不能成为第二套真相。

## 6. 写入事务

```text
PageStore pins exact source G
-> reserve SSD operation/index intent
-> compute canonical checksum, encode/compress, then compute encoded payload checksum
-> append record to active segment
-> receive I/O completion
-> commit index/manifest sequence according to durability class
-> PageStore validates operation/G/format/checksum metadata
-> add Valid Ssd replica G
-> optional authority/recoverability handoff
-> release source pin
```

关键规则：

- source pin 覆盖压缩和 write completion；
- 写入期间产生 G+1 不取消 G 的物理写，但 completion 只注册 exact historical G；
- I/O completion 前不能释放唯一 source；
- index commit 失败时 record 是 unreachable garbage，不是 Valid replica；
- 不在正常路径立即读回整页验证；checksum 在读取时验证，写入使用 I/O completion、header/index 一致性和故障注入保证；
- 每页 fsync 被禁止。

## 7. 耐久级别

### 7.1 SessionSpill

目的：释放 live session 的 RAM/UMA/VRAM 容量。

- 要求成功的 write completion 和进程内 index commit；
- 读取时必须 checksum；
- 允许 OS/设备缓存，默认不为每批强制持久化到介质；
- process/power crash 后可以丢失，不得冒充 auto-recovery；
- store 生命周期随 session/临时目录策略结束。

PageStore 可以在 SessionSpill valid 后把它作为当前进程内 authority/recoverability backing，但 capability descriptor 必须
标记其 crash durability 等级。

### 7.2 RecoveryCheckpoint

目的：支持明确声明的 crash recovery/恢复点。

- data record 分组写入；
- data durable barrier/fsync；
- manifest/index commit；
- manifest durable barrier；
- 只有完成组提交后才报告 RecoveryDurable。

文档正式保存仍由 serializer/Krita 文件格式完成；RecoveryCheckpoint 不是文档文件。

### 7.3 SaveSource

保存可从已验证 SSD exact generation 读取，但 serializer 输出成功前不能把 SSD store 当作最终保存结果。

## 8. 读取事务

```text
lookup exact PageVersion
-> pin record/segment reader ref
-> async read record
-> validate header/version/size and encoded payload checksum
-> decode/decompress
-> validate uncompressed size/canonical content checksum/SurfaceFormat
-> publish RAM/UMA target replica
-> release record reader ref
```

失败不得返回透明/default 像素。可选恢复来源按顺序尝试其他 exact replica、journal replay 或明确失败；不得读取最新
generation 代替调用者请求的历史 generation。

## 9. I/O 调度

SSD provider 暴露 backend-neutral async operation。平台实现可使用异步 API 或专用 I/O worker pool，但必须满足：

- worker 等待不占 UI/render/submission thread；
- 同 segment 邻近 record 可合并 read/write；
- current target fault/save deadline 高于 background GC；
- cancellation 区分尚未发起和已提交 I/O；
- completion 始终回到 PageStore transition，而不是直接修改 tile 指针；
- I/O buffer 属于有预算、按 operation 退休的 pool。

最终热路径不依赖大范围 mmap window，避免 SSD working set 被 OS page cache 重新记作不可控 RAM tier。平台
cache/direct-I/O/fadvise 策略可以按 benchmark 选择，但不改变 store 语义。

## 10. Codec policy

基线 codec chain：

```text
Default/Solid canonical special encoding
-> existing LZF-compatible codec
-> Raw escape when compression is not beneficial
```

规则：

- codec 输入/输出严格为 SurfaceFormat canonical bytes；
- codec/version写入 record；
- 压缩输出不得大于 provider buffer 上限；
- codec 失败时可退 raw，但必须生成新 header/checksum，不能伪装原 codec 成功；
- 更重 codec、GPU compression 或 dictionary 只能在端到端 SSD trace 获益后增加；
- codec 选择阈值是策略参数，不是文件格式隐含规则。

## 11. GC/compaction

### 11.1 Live set

记录存活由 PageStore generation refs 和 index 决定。GC 不自行判断“旧 generation 应该没用了”。

### 11.2 Cleaner

```text
select sealed segment by dead-byte ratio and pressure
-> snapshot its live records
-> pin segment/readers
-> copy/re-encode live records into new segment
-> validate new records
-> atomically publish new index locations/manifest sequence
-> wait old readers
-> delete/truncate old segment
```

GC crash 在 manifest switch 前保留旧记录；switch 后恢复选择新 manifest。任何时刻至少有一套 committed location。

### 11.3 Write amplification controls

- background GC 在 current target/read fault deadline 前让路；
- 避免清理 live ratio 过高的 segment；
- 临时 derived record 优先放入独立寿命类别 segment；
- undo/save retained generation 可按 lifetime hint 分组，但不能改变 exact key。

## 12. Budget 与磁盘空间

分别统计：

- live committed payload；
- obsolete/dead bytes；
- active segment slack；
- GC temporary duplicate bytes；
- I/O/compression buffers；
- SessionSpill 与 RecoveryCheckpoint；
- per document/session usage。

达到 soft limit：停止 derived 写入、加速安全 GC、降低 speculative prefetch。达到 hard limit且无法 reclaim：新 SSD
handoff 显式失败，RAM/VRAM authority 保留并触发上层 backpressure，不能删除未保存像素。

## 13. 恢复与清理

启动/重开 store：

1. 验证 store/manifest version；
2. 选择最后完整 durable manifest；
3. 扫描必要 segment tail/commit sequence；
4. 忽略半写、未知或 checksum metadata 失败的 record；
5. 重建/校验 index；
6. 将 record 暴露为候选 replica，实际 payload 在 read 时再校验；
7. 清理不可达 session spill。

Session close：拒绝新 operation，完成或取消已知 I/O，释放 index/segment refs，再按 store policy 删除临时文件。

## 14. 故障注入

必须逐点注入：

- encode/compress fail；
- short write/partial record；
- I/O completion error；
- data durable 前/后 crash；
- manifest durable 前/后 crash；
- checksum corruption；
- unsupported codec/version；
- disk full/permission change；
- GC copy/switch/delete 中断；
- cancel before/after submission；
- 同页多个 generation 完成乱序。

每个失败都验证 source authority、index、live record 和 PageStore generation。

## 15. 指标

- logical/raw/compressed bytes；
- compression ratio和 encode/decode P50/P95/P99；
- read/write queue delay与吞吐；
- record/index/manifest commits；
- checksum failure；
- spill fault latency；
- GC copied/dead/freed bytes；
- write amplification；
- OS page-cache/direct-I/O policy；
- durability batch size/fsync latency；
- disk-pressure backpressure duration。

## 16. 实施顺序

### SSD0：In-memory/reference store

- record/index/commit sequence；
- exact-generation tests；
- codec/checksum failure。

### SSD1：Append segment

- SessionSpill write/read；
- async worker/I/O buffer；
- current swap behavior differential tests。

### SSD2：Cleaner

- live set integration；
- manifest switch；
- interruption recovery。

### SSD3：RecoveryCheckpoint

- group durability；
- startup recovery；
-明确 capability/状态。

### SSD4：Cutover

- `KisSwappedDataStore` 调用统一 provider；
- 删除 mmap/chunk production path；
- 禁止 Vulkan 私有 SSD store。

## 17. 完成门槛

- exact generation/key/checksum 全链一致；
- write/index 失败不释放最后 authority；
- SessionSpill 与 RecoveryCheckpoint 不混称；
- 每页 fsync 和立即读回不存在；
- GC 任意中断可恢复到一套 committed record；
- disk full 时触发 backpressure而非数据删除；
- CPU 与 Vulkan page 使用同一个 index/budget/GC；
- 临时 store 不替代 Krita 文档保存格式。
