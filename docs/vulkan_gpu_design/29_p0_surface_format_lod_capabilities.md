# P0：SurfaceFormat、颜色/位深、LoD 与能力真实性

> 本文解决固定 RGBA8、只按 `pixelSize` 猜 VkFormat、raw `readBytes()` 直接上传、display filter空实现和
> Vulkan canvas 无条件报告 LoD 支持。

## 1. `SurfaceFormat`

```text
SurfaceFormatId
KoColorSpace identity/revision
ColorModel
ColorDepth/ChannelType
ChannelOrder/Layout
ChannelCount
PixelStride/Alignment
AlphaPresence
AlphaSemantics
PremultiplicationSemantics
Endianness/Packing
DefaultPixel
CodecVersion
```

- PageVersion始终绑定SurfaceFormatId。
- `pixelSize=4/8/16`只用于容量，不能决定通道、类型或颜色空间。
- colorspace变化创建format/surface conversion operation和新generation，不只触发repaint。

## 2. Codec 层

CPU/GPU之间不直接把任意Krita raw bytes当RGBA8。定义：

```text
SurfaceCodec
  decode canonical page -> shader working representation
  encode shader result -> canonical format
  default pixel materialization
  blend/color semantics
  transfer/SSD serialization metadata
```

### CPU codec

- 位于 `kritaimage`/颜色基础设施；
- reference/golden使用；
- 支持PageStore RAM/SSD format validation。

### GPU codec

- 位于 `kritavulkanbackend`；
- capability descriptor按SurfaceFormat/operation声明支持；
- storage buffer load/store显式处理channel type/order；
- sampled image view只能用于确有匹配VkFormat/转换路径的derived replica；
- 不能用“字节数相同”替代codec。

## 3. Operation Capability

能力不是Canvas全局bool，而是descriptor查询：

```text
queryCapability(OperationId,
                OperationSemanticVersion,
                Input/Output PortSignature(
                    ValueType(typeId/version/storage class),
                    SurfaceFormatId?),
                Brush/Node semantics,
                DeviceDescriptor)
-> Supported variant / Unsupported reason
```

`SurfaceFormatId` 与端口位置绑定；一次 capability entry 表达一个精确 input/output signature。不能把所有
格式压成无位置的集合，否则 A→B 转换、多输入混合与同格式 pass 会被错误地视为同一能力。

OperationId 至少覆盖：

- canonical page read/write；
- AutoRound/brush algorithm；
- blend/composite；
- mask/selection；
- display transform/filter；
- LoD pyramid build/sample；
- upload/download/SSD codec；
- undo/snapshot/recovery。

一个format支持display不等于支持GPU brush写入。

semantic capability 只回答“能否正确执行”，不等于“应否自动选择”。后端另以 operation variant、SurfaceFormat、
page-count/work-size、device/driver/power state 和 profile version 查询性能资格：

```text
PerformanceQualification = AutoPreferred | ForcedDiagnosticOnly | StaleOrUnknown
CpuEta / AcceleratorEta / confidence / risk margin
```

它服从 39 的同机成熟 CPU product baseline。`ForcedDiagnosticOnly` 仍可在测试中验证正确性，但产品 Auto 必须前置 CPU
route；不能把 correctness `Supported` 展示成该 workload 已获得 GPU 加速。

## 4. Format 支持矩阵

每个backend build生成可查询矩阵：

```text
SurfaceFormat family
Canonical storage representation
CPU codec
GPU read
GPU write
Blend variants
Composite variants
Display conversion
Snapshot/recovery
Known limitations
Golden test id
```

首个MVP可以只放行明确格式，但PageStore identity/API从第一天完整保存format。未放行格式在begin operation前路由CPU，
不能先截断/转换成RGBA8继续写canonical。

## 5. 4/8/16 字节测试不是全部语义

CI至少覆盖不同pixel stride：

- 4字节；
- 8字节；
- 16字节；

同时必须覆盖：

- 不同channel type/order；
- alpha/no-alpha；
- premultiplied/unpremultiplied；
- non-RGBA model；
- unsupported format前置CPU route；
- default pixel/clear；
- SSD roundtrip；
- COW/undo/save；
- display color conversion。

只检查bytes-per-pixel不会发现通道解释错误。

## 6. Alpha、Selection 与 Lock

- Alpha lock影响write mask/target semantics，进入BrushSemanticManifest和kernel variant。
- selection/mask是独立canonical surface/format，通过read lease参与stroke/composite。
- erase/composite遵守KoCompositeOp/alpha semantics，不硬编码UNORM source-over。
- selection/alpha lock capability没有golden test时整笔CPU route。

## 7. Display Color 与 Filter

DisplaySurface dependency包含：

- document SurfaceFormat/colorspace generation；
- monitor/output profile；
- rendering intent/flags；
- exposure/gamma/HDR state；
- `KisDisplayFilter`/OCIO generation；
- swapchain color format/colorspace。

`setDisplayFilter()`不能只request repaint。后端不支持所需filter时：

- 使用CPU/成熟OpenGL display；或
- capability明确不支持Vulkan view。

不能显示未经转换的raw canonical bytes并报告成功。

## 8. LoD 能力

### 定义

LoD支持至少需要：

- canonical-to-pyramid derived build；
- per-level page identity/generation/dependency；
- dirty propagation到mip/page pyramid；
- viewport/zoom level选择；
- sampling/filter语义；
- rebuild/eviction；
- 与stroke/EvaluationEpoch/display同步。

### Capability

- 后端descriptor只有在上述路径和测试存在时返回LoD supported。
- 没有pyramid时返回unsupported，Canvas不能因为有tile cache就无条件true。
- `KisVulkanUpdateInfo::levelOfDetail`字段存在不代表LoD实现。
- paintop `lodSizeThresholdSupported()`与canvas display LoD是不同能力，分别查询。

## 9. Capability 证据

每个声明需要：

```text
CapabilityId
SemanticVersion
Device/feature prerequisites
Supported SurfaceFormat set
Operation variants
Fallback route
Golden/validation/stress test ids
Recovery support
PerformanceProfileId / qualification（不进入 semantic identity）
```

无对应test id的capability在CI中不能进入allow list。

## 10. 前置路由

operation 开始前：

1. 从 EvalGraphIR 解析 operation/version、value types、target/input formats 和完整语义。
2. 查询document/backend correctness capability snapshot。
3. 查询当前 workload/device-state 的 performance qualification；只有 `AutoPreferred` 才选择 GPU/UMA，否则选择 CPU
   PageStore、成熟 display backend 或 reject。
4. 冻结到operation/stroke/view epoch。
5. 不在执行一半因format/resource miss切换。

CPU fallback写同一canonical SurfaceFormat/PageStore，不建立转换后RGBA8 shadow authority。

## 11. 实现路线

### FC0：Format identity

- SurfaceFormat/registry/serialization。
- 从KoColorSpace提取稳定identity/revision。

### FC1：CPU codec/reference

- default/read/write/SSD/golden。
- 4/8/16与通道/alpha矩阵。

### FC2：Capability descriptor

- operation+format+device查询。
- unsupported reason和前置route。

### FC3：GPU codec variants

- 从首个明确RGBA8语义开始。
- 逐format/operation增加variant与golden。

### FC4：Display color/filter

- DisplaySurface color dependency。
- monitor/filter/swapchain转换与fallback。

### FC5：LoD

- page pyramid derived surface。
- dirty/build/sample/eviction tests。
- 完成前capability保持false。

## 12. 必须删除/修正

- `pixelSize=4`默认canonical假设；
- `pixelSize -> VkFormat`粗略switch作为能力证明；
- LayerCompositor/NodeSync固定`VK_FORMAT_R8G8B8A8_UNORM`；
- raw projection bytes直接作为RGBA8；
- color-space changed只repaint；
- display filter空实现却保持Vulkan view；
- Vulkan canvas无条件LoD true；
- capability没有golden test仍放行。

## 13. 验收门槛

- 每个canonical/derived page有完整SurfaceFormat。
- GPU operation按format+semantic查询能力，不按pixelSize猜测。
- 不支持格式在开始前CPU/成熟backend路由。
- 4/8/16字节和多通道/alpha语义测试通过。
- SSD/COW/undo/save保持format identity。
- display filter/color conversion真实应用。
- 无pyramid时LoD返回unsupported。
- 每个capability allow项存在golden/validation/stress证据。
