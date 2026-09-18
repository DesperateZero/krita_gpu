# PageWorkCompiler 与页级 GPU Kernel

> 本文细化 resolved dab 如何被编译为保持像素语义的 page/microtile work，以及 GPU 如何在不逐 dab
> dispatch/barrier 的前提下完成严格有序混合。命令协议见
> [12_stroke_protocol_and_journal.md](12_stroke_protocol_and_journal.md)。
> logical page geometry、generation 和 lease 由 canonical PageStore 提供；Vulkan sparse/atlas 物理粒度不得
> 反向决定 Krita tile identity。全局边界见
> [22_p0_vulkan_baseline_reconstruction.md](22_p0_vulkan_baseline_reconstruction.md)。

## 1. 要解决的问题

当前“一 dab 一 dispatch”同时存在两个冲突：

- 不加 dab 间 memory dependency，重叠像素的 read-modify-write 不正确；
- 每 dab 加 barrier，执行被强制串行且保留高 CPU 录制成本。

正确的并行轴不是 dab，而是互不重叠的目标像素/页面。对同一个像素，blend 顺序属于绘画语义，不能
并行重排；对不同页面或不同像素，可以并行。

## 2. 输入与输出契约

### 2.1 输入

`PageWorkCompiler` 接收：

```text
StrokeEpochDesc
sealed StrokeBatch（连续 sequence range）
ResolvedDab[]
logical page geometry
target surface format
PreparedBrushProgram metadata
previous page writer ledger
BatchCostPolicy
```

输入不可变。compiler 不修改 journal、不执行像素读写、不提交 Vulkan queue。

### 2.2 输出

```text
CompiledStrokeBatch
  batch id / sequence range
  target set
  PageJob[]
  packed DabPayload[]
  packed DabRef[]
  indirect dispatch records
  prerequisite tickets
  predicted cost
  accounting summary
```

每个 accepted dab 必须出现在 accounting summary 中：

- 不影响任何像素的空 bounds 可以记为 `NoOp`；
- 正常 dab 必须引用至少一个 PageJob；
- compiler 不能静默过滤未知 flag/blend/resource；
- 不能因为页面未驻留而删除 work，只能附加 residency dependency。

## 3. 页面与 microtile 几何

### 3.1 逻辑页面

compiler 只使用 PageStore 公布的逻辑 page geometry，不使用 Vulkan sparse granularity 计算绘画覆盖。
逻辑页面到 shared buffer、VRAM block、sparse region 或 atlas slot 的映射由 backend lease 决定。

### 3.2 页面内 microtile

页面内可以再划分固定 shader work granularity 的 microtile，例如 8×8 或 16×16 像素，但该值是 kernel
variant 的属性，不等于 Krita tile 或物理 sparse block。

目的：

- 小 dab 只进入相交 microtile 的 list；
- 每个像素无需测试整页所有 dab；
- workgroup 与硬件 local size 对齐；
- 仍保持 page generation 和 write lease 作为外部一致性单元。

microtile 边界不允许产生像素重复所有权。抗锯齿 fringe 通过 conservative bounds 扩大引用集合，但最终
像素坐标仍只属于一个 microtile invocation。

## 4. 稳定分桶算法

### 4.1 基础算法

按 `(sequence, subSequence)` 顺序遍历 batch：

1. 读取 conservative dab bounds。
2. 与 target surface bounds/wrap policy 求交。
3. 枚举相交逻辑页面。
4. 枚举页面内相交 microtile。
5. 向对应 list 追加 `DabRef`。

list 不再按面积、材质、blend 或资源排序。追加顺序即混合顺序。

### 4.2 确定性

- hash map 只用于找到 list，不能用 hash iteration 顺序决定输出顺序。
- 最终 PageJob 按稳定 `(targetIndex, PageId)` 顺序排列，便于测试和 trace。
- 每个 microtile list 严格保持 sequence/subSequence。
- 并行 compiler 必须使用 stable prefix-sum/fill，或先按 sequence 分段后做稳定 merge。
- 同一输入、几何和 compiler version 必须生成逻辑等价 work；物理 buffer offset 可以不同。

### 4.3 两遍紧凑布局

推荐实现：

1. count pass：统计每个 `(target,page,microtile)` 的引用数。
2. prefix pass：分配连续 `DabRef` range。
3. stable fill pass：再次按 sequence 遍历并写入各 range 的 next cursor。
4. compact pass：生成非空 PageJob/microtile dispatch record。

CPU 首版可以串行完成 stable fill，先验证正确性。后续并行或 GPU binning只能替换内部实现，不能改变输出契约。

### 4.4 引用压缩

可选优化必须保持顺序：

- 页面全覆盖 dab 与 microtile-local dab 分开存储时，shader 必须按 sequence merge 两个有序流；
- 连续共享资源/算法参数可以字典化，但每个 DabRef 仍能恢复完整顺序；
- 重复 bounds 或 payload 可去重，不能合并两个具有不同 sequence 的 blend 操作；
- opacity 为零等语义 NoOp 只能由经过 CPU reference 测试的规范化阶段消除。

## 5. `PageJob` 结构

建议逻辑字段：

```text
PageJobId
StrokeId / BatchId
TargetSurfaceId / LogicalPageId
baseGeneration
pendingGeneration
pageRect / validRect
microtile table range
ordered DabRef ranges
target write lease handle
resource read lease set
before-image ticket
residency/binding publish ticket
previous-writer ticket
kernel variant
format/color metadata
predicted cost
```

规则：

- 一个 PageJob 只写一个 target page 的一个 pending generation。
- 多个 microtile job 可以并行写同一 page 的互不重叠像素，但共同属于同一 page generation。
- 页面外或 validRect 外 invocation 必须退出。
- page lease 直到 execution ticket 完成后才释放。
- generation 发布由 PageStateMachine 完成，kernel 不能直接修改 CPU 状态。

## 6. GPU 数据布局

### 6.1 Command buffer

GPU 读取的 command payload 至少包含：

- compact `ResolvedDab` payload；
- PageJob header；
- microtile offset/count table；
- ordered `DabRef` index；
- target opaque GpuPageHandle/offset；
- immutable resource table；
- indirect dispatch arguments。

禁止 per-dab push constants 和 per-dab descriptor update。batch 级常量可以使用 push constants；可变列表放在
storage buffer。

### 6.2 Descriptor 与地址

- UMA/dGPU buffer-page backend 优先以少量稳定 storage buffer descriptor + direct handle/operation-scoped local table访问。
- brush resources 使用 `PreparedBrushProgram` 的稳定 ResourceSet。
- 不支持 descriptor indexing 的设备使用固定上限 variant，不在热路径动态分配 descriptor set。
- GPU address/descriptor 只在 compiled batch 内有效，不写回 journal。

## 7. Kernel 执行模型

### 7.1 像素所有权

一个 workgroup 处理一个 microtile，local invocation 以 stride 覆盖该 microtile 的像素。每个有效目标像素
只由一个 invocation 负责：

```text
dst = loadTarget(pixel)
for dabRef in orderedMicrotileList:
    if dab covers pixel:
        src = evaluateBrush(dab, pixel, resources)
        dst = blend(dst, src, dab.blend)
storeTarget(pixel, dst)
```

同一 invocation 内普通程序顺序即该像素的严格 blend 顺序，不需要 dab 间全局 barrier。

### 7.2 页面内并行

- 不同 pixel invocation 不写同一地址。
- 不同 microtile 不写同一像素。
- 不同页面天然无写重叠。
- shader 只在 job 结束时产生页面写入；外部通过 batch memory dependency 对后续 reader/writer 可见。

### 7.3 目标加载和存储

- direct incremental brush 从 `baseGeneration` target page 加载当前像素并产生 `pendingGeneration`。
- 页第一次写前必须完成 before-image dependency。
- 若 page 是新透明页，可由 PageStore 提供规范化 clear generation，不能依赖未初始化 allocation。
- format/color conversion 必须由 `SurfaceFormat`、codec 和 kernel variant 明确处理；可以先让 Auto Round 的
  第一条 GPU golden 使用 RGBA8，但首个 MVP 必须同时验证 4/8/16 字节像素支持矩阵，并在 stroke 开始前把
  不支持格式完整路由 CPU，不能把固定 RGBA8 写入底层数据模型。

### 7.4 资源采样

- tip/texture/mask 只通过 immutable resource table 访问。
- sampler、wrap、filter 和 color interpretation 属于 brush semantic version。
- resource ticket 未完成时 submission 在 GPU dependency 上等待，host/compiler 不阻塞。
- resource generation 不匹配时 compiled batch 失败，不允许采样新版本代替旧版本。

## 8. Micro-batch 与屏障

### 8.1 为什么切分

单页长 dab list 或超大 dab 可能生成长时间 kernel。`BatchCostModel` 根据：

- page/microtile 数；
- DabRef 数；
- 估算覆盖像素；
- texture/mask 采样次数；
- blend/kernel variant；
- 历史 GPU timestamp；

把连续 sequence 切为有上限 micro-batch。

### 8.2 同页跨 micro-batch

同一页连续 micro-batch 必须：

1. 后一 batch 的 base/pending chain 引用前一 writer ticket；
2. 使用 compute storage write -> compute storage read/write dependency；
3. generation ledger 保持顺序；
4. 失败时停止发布后续依赖 generation。

每个 micro-batch 一次页面级依赖可以接受；禁止退回每 dab barrier。

### 8.3 大 dab

一个大 dab 覆盖多个页面时，各页面像素独立，可分不同 submission 执行。显示层只有在对应页面 generation
完成后更新，因此允许视觉上按页渐进，但不能显示半个尚未完成的页面 generation。

## 9. 非 direct 笔刷

### 9.1 Wash/Indirect painting

- 使用独立 stroke-local transient/derived surface；它不能成为文档 canonical authority。
- dab kernel 写 indirect surface。
- stroke opacity/composite 是单独 stage，依赖 indirect page tickets。
- undo 只捕获最终目标 canonical page before-image；indirect derived page 可丢弃。

### 9.2 Smudge/邻域读取

- 明确 read halo 和 write region。
- 输入 generation 与输出 generation 分离，必要时 ping-pong，禁止原位跨像素数据竞争。
- compiler 为邻页获取 read lease，为目标页获取 write lease。
- stage DAG 明确采样源与写目标，不能复用 direct RMW kernel 的隐含假设。

### 9.3 多目标

- 以 `(targetIndex, PageId)` 建立 PageJob。
- 独立目标可并行。
- 若算法定义目标间顺序，epoch 必须携带 stage graph，并用 ticket 串联。
- 未声明在 stroke writable target set 中的 surface 不能获得 write lease。

## 10. CPU Reference Executor

reference executor 必须消费同一 `CompiledStrokeBatch` 逻辑结构，而不是另一套独立笔刷解释器：

- 同样的 PageJob/microtile/DabRef 顺序；
- 使用高精度或明确规范化的 blend；
- 输出每页 checksum/generation；
- 支持任意 batch/micro-batch 切分；
- 可在无 Vulkan 环境运行随机测试。

GPU golden test 比较 reference page 与 GPU readback。允许容差必须按算法/格式定义，不能使用一个全局宽松阈值。

## 11. 实现路线

### PW0：几何与 reference

- 定义 page/microtile mapping。
- 实现 conservative bounds 和 stable lists。
- CPU reference page executor。
- page boundary、mirror、wrap 和 overlap 测试。

### PW1：Packed work format

- PageJob/DabRef buffer schema。
- 两遍 count/prefix/fill。
- command upload arena 与 schema version。

### PW2：Auto Round kernel

- RGBA8/Normal direct kernel。
- 一个 invocation 独占一个像素。
- indirect dispatch 和 batch-level descriptor。
- 与 reference 做重叠 dab golden test。

### PW3：Generation/lease 接入

- write lease、before-image、previous writer 和 completion ticket。
- 同页 micro-batch dependency。
- 空白页规范化 clear。

### PW4：成本和大工作负载

- timestamp 驱动成本模型。
- 大 dab、多页和长 list 拆分。
- 验证切分不改变输出。

### PW5：资源和特殊 stage

- predefined/texture/mask ResourceSet。
- indirect wash surface。
- 邻域读取的 read-halo/stage DAG。

## 12. 验收门槛

- 任意 batch、page 和 micro-batch 切分与 CPU reference 一致。
- 同页数千重叠半透明 dab 结果稳定，不依赖 dispatch 调度顺序。
- 每个目标像素只有一个 invocation writer。
- 不存在 per-dab dispatch、descriptor allocation 或 barrier。
- 页面边界、valid rect、镜像、wrap 和超大 dab 无接缝。
- previous-writer 和 resource/residency ticket 缺失时 submission 被测试拒绝。
- 预测成本能把超大 workload 拆成有限 submission，且 resolved dab accounting 不变。
