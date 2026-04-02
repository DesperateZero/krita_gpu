# Vulkan 分支笔刷能力差距分析与首个完整版本路线

**日期**：2026-04-02  
**目的**：基于 `docs/krita_background_knowlage_index/paintbrush.md` 对照当前 Vulkan 分支实现，重新判断距离“完整接入像素笔刷引擎（paintbrush）”还有多远，并据此修正首个完整笔刷版本的落地路线与定版判断。

---

## 1. 文档定位

本文件承接：

- `01_vision_and_direction.md` 的 **GPU-first** 总方向
- `03_development_steps.md` 中 **Phase 7 已完成主链路闭环，后续进入功能覆盖与正确性扩展** 的阶段判断
- `06_branch_vs_design_analysis.md` 中 **“接口适配层 + GPU 原生计算”** 的工程策略
- `08_brush_engine_refactor_fix_plan.md` 中 **“问题清单 → 目标架构 → 修复步骤 → 验收标准”** 的执行计划

本次更新的重点不是重新讨论 Vulkan 画布底座，而是基于当前代码状态回答四个问题：

1. 现在的 Vulkan 笔刷到底已经走到了哪一步  
2. 与 CPU `paintbrush` 的真实基线相比，还剩哪些关键缺口  
3. 哪些原先属于“架构缺口”的问题已经被补上  
4. 首个完整笔刷版本接下来应该如何收敛

---

## 2. 重新结论：距离已经明显缩短，但当前仍不满足定版条件

### 2.1 现状已从“窄路径原型”升级为“可控接入架构”

与上一次评估相比，当前 Vulkan 分支最重要的变化不是单个 shader 的增强，而是笔刷接入方式发生了结构升级：

- `paintbrush` 仍是当前唯一正式接入 GPU 路由的引擎
- GPU/CPU 分流不再依赖 `paintbrush + auto_brush` 这样的粗字符串判断
- 现在已经引入 **feature gate + shared runtime + brush tip backend** 三层结构
- 预设只要命中未支持特性，就会稳定回退 CPU，而不是带着缺功能进入 GPU

这意味着当前状态已经不应再被描述为“只有一条硬编码的 auto brush 路线”，而应描述为：

> **Vulkan 笔刷已经具备了生产化接入骨架，但功能覆盖面仍然刻意收窄。**

### 2.2 现在的主要矛盾已经变化

之前的主要问题是：

- 缺共享抽象
- 缺严格门禁
- 缺 brush tip backend 设计

现在这些问题已经不再是“没有”，而是变成：

1. **三层抽象已经落地，但覆盖范围仍窄**  
   目前仍主要服务于 `paintbrush`，并且 GPU 可用集合被故意限制在很小范围内。

2. **shared runtime 已形成，但共享语义还不完整**  
   spacing、基础 brush resource、composite passthrough 已经进入公共层，但 texture、masking、mirror、wrap-around、timing 等仍未进入真正可用状态。

3. **brush tip backend 已建模，但热路径闭环尚未完成**  
   代码里已经存在 `AutoBrushBackend / StampBrushBackend / TextBrushBackend` 的方向设计，并且 backend 已进入真实 dispatch 路径；当前问题不再是“有没有 backend”，而是“backend 路径是否已完成初始化与扩展参数闭环”。

4. **首个完整版本的阻断项已从“先搭架构”转为“补功能覆盖 + 做一致性验证”**

### 2.3 现在的距离判断

- 距离 **“基础 GPU 笔刷原型可画”**：已完成
- 距离 **“具备严格门禁与可控回退的 GPU paintbrush 接入”**：已基本完成
- 距离 **“首个完整 paintbrush 版本”**：还有一段实现距离，但已不再是架构重建问题
- 距离 **“其他现有笔刷可沿同一模式无缝接入”**：基础方向已经立住，但还需要把 backend 与共享语义真正做实

一句话判断：

> 现在离完整像素笔刷更近了；最难的架构转向已经完成，但当前代码仍存在热路径闭环和验证层面的关键断点，因此还不能视为可定版版本。

### 2.4 当前定版判断

当前不建议把 Vulkan `paintbrush` 判定为可定版版本。阻断项并未收敛到“两项”，而是已经重新暴露为以下五类：

1. **Stamp backend 的端到端初始化闭环仍未真正完成**
   `BrushEngine::ensureBackendInitialized()` 与 `StampBrushBackend::setPending*()` / `uploadPendingImages()` 这套机制已经写入代码，但 `BrushEngine::initialize()` 新增的 allocator 仍未从 `KisVulkanCanvas` 正确传入，导致依赖 `StampBrushBackend` 的 `predefined / texture / masking` 路径仍不能视为真实闭合。

2. **texture / masking 的“参数通路”已补齐，但“资源可用性”尚未达到可定版状态**
   `setStrokeTextureParams()` 解决了 per-stroke 参数绕过 ring buffer 的问题，pending image 延迟上传模型也已建立；但当前仍缺预加载、显存常驻、资源缓存与端到端验证，因此不能把它等同于“纹理能力已完成”。

3. **feature gate 已明显改善，但颜色能力与部分运行时语义仍存在口径不一致**
   wrap-around 的运行时检测、sharpness 三种存储模式提取、Krita 5.x `Pressure{ID}` + `{ID}Sensor` 双模式覆盖都已具备；但 `LightnessStrength` 目前是“已提取”而非“已完成语义闭环”，`color_source` gate 已放开但实现依据仍需补强。

4. **blend / composite 架构已出现重复实现扩散**
   当前 brush path、layer compositor、preset analyzer 各自维护 blend mode 支持与映射，shader 侧也已出现多份近似实现。这已经是工程性问题，而不再只是功能覆盖问题。

5. **缺少足以支撑定版的验证证据**
   目前能看到 validation、benchmark 和 fallback 基础设施，但尚未看到与 Vulkan 笔刷直接对应的自动化测试、系统性预设回归矩阵、或可冻结的 GPU 白名单。

---

## 3. CPU `paintbrush` 的真实基线仍然不变

根据 `docs/krita_background_knowlage_index/paintbrush.md`，CPU `paintbrush` 的基线仍然是一整套协作体系，而不是单个圆形 dab：

### 3.1 引擎本体

- `paintbrush` 是 paintop registry 里的真实引擎 id
- 主体是 `KisBrushOp`
- `paintAt()` 负责每个 dab 的几何与墨迹参数求值
- `doAsynchronousUpdate()` 负责 CPU 端的 dab 合成、分块、镜像、wrap-around
- `paintLine()` 对 1px + sharpness 有专门快路径

### 3.2 共享笔刷层

`paintbrush` 依赖 `KisBrushBasedPaintOp` 提供通用语义：

- 笔尖资源加载与缓存
- `KisDabCache`
- texture / mirror / precision
- brush spacing / auto spacing / LOD / airbrush 相关折算

### 3.3 CPU 版 `paintbrush` 的能力边界

CPU 基线仍覆盖以下能力族：

- Brush Tip：Auto / Predefined / Text
- Geometry：Size / Ratio / Rotation / Softness / Sharpness / Scatter / Spacing / Mirror
- Ink：Opacity / Flow / Painting Mode / Composite Op
- Color：Color Source / Mix / Darken / Hue / Saturation / Value / Lightness Strength
- Brush Post-process：Texture / Masking Brush
- Timing：Airbrush / Rate
- Runtime：异步 dab 合成 / wrap-around / 1px 特化 / undo-save 语义

因此，“完整接入像素笔刷引擎”的标准并没有因为 Vulkan 代码进展而降低。

---

## 4. 当前 Vulkan 分支已经做到什么

### 4.1 总体架构

当前 Vulkan 笔刷已经形成如下分层：

1. **接入层**  
   `KisVulkanCanvas` 在初始化时激活路由器，并包装 `paintbrush` 工厂。

2. **门禁层**  
   `KisVulkanPaintOpFactory` 通过 `KisVulkanPresetAnalyzer` 做 feature-level GPU 兼容性判断。

3. **共享运行时层**  
   `KisVulkanBrushRuntime` 统一负责 capability snapshot、brush resource、dynamics、spacing、composite passthrough。

4. **paintop 适配层**  
   `KisVulkanPaintOp` 已退化为很薄的桥接器，只负责把 runtime 产出的 dab 送进 ring buffer。

5. **GPU 执行层**
   当前热路径由 `KisVulkanBrushEngine` 统一调度，按 backend 选择 `dab_round.comp` 或 `dab_stamp.comp`。backend-aware dispatch、延迟初始化机制、pending image 上传模型、per-stroke 参数绕过 ring buffer 的通路都已存在；但 `StampBrushBackend` 的端到端初始化仍受 allocator 透传缺口影响，尚不能视为真正闭合。

### 4.2 已经实装的关键改进

与上版评估相比，以下问题已经明显前进：

- **严格门禁已建立**  
  预设分析现在已经覆盖 brush tip、texture、masking、color、airbrush、painting mode、composite 等维度。

- **共享 runtime 已建立**  
  基础参数读取、`brush_definition` 解析、dynamics、spacing 与 composite passthrough 已集中到 `KisVulkanBrushRuntime`。

- **Composite 不再是硬编码 normal**  
  现在已存在 Krita composite string → 共享 GPU blend enum / 映射 → shader switch 的完整链路；brush runtime、preset analyzer、node sync 已引用同一份 C++ 映射，brush / layer shader 的 blend 数学也已下沉到共享 GLSL include；`brush / layer / analyzer` 的支持矩阵已冻结到共享 path-aware blend matrix，但端到端一致性验证仍未完成。

- **CPU fallback 已从“宽松误入”改为“严格拒绝”**  
  这对稳定性和用户预期都非常关键。

### 4.3 仍需谨慎的地方

虽然三层抽象已经出现，但还不能把它描述成“全部完全打通”：

1. **Brush tip backend 已进入热路径，但 Stamp path 端到端初始化仍未完全闭合**
   `BrushEngine::ensureBackendInitialized()` 在 `recordDabs()` / `processStrokePoints()` 首次触发时延迟初始化 backend，并自动上传 pending images；`recordDabs()` 在初始化失败时也不会消费 dab。但 `BrushEngine::initialize()` 新增的 allocator 当前未从 `KisVulkanCanvas` 透传，导致 `StampBrushBackend` 的纹理上传链仍不能算完全打通。

2. **shared runtime 仍是“基础共享语义”而不是“完整共享语义”**  
  它已经比之前健康得多，但尚未吸收生产级资源常驻策略、texture/masking 的显存缓存、mirror / airbrush / sharpness / wash 的完整共享语义；brush 与 layer 的 blend 支持口径虽已冻结到统一矩阵，但端到端图像验证仍未收口。

3. **feature gate 严格了很多，但“放行条件”和“真实运行时能力”并未完全对齐**  
   wrap-around 已改为运行时检测，sharpness / scatter / lightness strength 的提取都已增强；但 `LightnessStrength` 当前仍是“已提取未完全生效”，`color_source` 的 gate 已放开而运行时依据仍需补强。

因此，当前状态最准确的描述是：

> **门禁和共享骨架已经成型，brush path 已具备真实接入形态；但 Stamp path 初始化、资源常驻模型、颜色语义闭环、blend 架构统一与验证矩阵仍未达标，因此距离可定版版本还有明显距离。**

---

## 5. 重新评估后的功能矩阵

| 能力维度 | CPU `paintbrush` 基线 | Vulkan 当前状态 | 当前评估 |
| :--- | :--- | :--- | :--- |
| 引擎注册与接线 | 已完整接入 registry | 已包装 `paintbrush`，透明 GPU/CPU 分流 | 已具备 |
| GPU/CPU 门禁 | CPU 天然完整 | 已改为 feature-level capability gate | 已显著改善 |
| paintop 适配 | `KisBrushOp` 直接承载逻辑 | `KisVulkanPaintOp` 已变成薄桥接器 | 架构方向正确 |
| shared runtime | `KisBrushBasedPaintOp` 完整共享层 | `KisVulkanBrushRuntime` 已建立基础共享层 | 已建立但未完整 |
| brush tip backend 抽象 | CPU 通过 `KisBrush` 体系支持多种笔尖 | backend 接口已建立并进入热路径，lazy init 机制已落地 | 已具备，但 Stamp path 仍未完全闭合 |
| auto brush | 完整支持 | 已支持，当前 GPU 主路径 | 已具备 |
| predefined brush | 完整支持 | analyzer 已允许进入 GPU，runtime / shader 路径已存在，目标走 stamp backend | 已进入目标范围，但仍受 allocator 透传缺口与端到端验证阻断 |
| text brush | 完整支持 | analyzer 识别到，但明确回退 CPU | 可后置 |
| spacing / auto spacing | 完整统一折算 | runtime 已有基础实现 | 已改善但仍需对齐 CPU 语义 |
| composite op | Krita 真实透传 | 已抽出共享 GPU blend enum / composite 映射与共享 GLSL blend 库，并把 brush / layer / analyzer 的支持矩阵冻结到共享 path-aware 查询；端到端验证仍待完成 | 架构已明显收口，但未完全定版 |
| texture | 完整支持 | per-stroke 参数链已闭合（bypass ring buffer），pending image 延迟上传已实现 | 参数通路已具备，但资源常驻与 stamp 端到端验证未完成 |
| masking brush | 完整支持 | pending image 延迟上传已实现，依赖 stamp path | 参数通路已具备，但资源常驻与 stamp 端到端验证未完成 |
| color source / mix / HSV / darken | 完整支持 | HSV / Mix / Darken 已有 CPU 侧实现；`LightnessStrength` 已提取；`color_source` 已放开 gate | 部分具备，但状态描述需分级，不能视为整体完成 |
| airbrush / rate | 完整支持 | timing 接口已接入，但重采样闭环未见验证 | 高风险未验证 |
| mirror | 完整支持 | runtime 已能生成镜像 dab | 已有实现，但需系统验证 |
| wrap-around | 完整支持 | 运行时由 factory 通过 `KisImage::wrapAroundModeActive()` 检查，稳定回退 CPU | 已具备 gate |
| sharpness / 1px 快路径 | 完整支持 | 提取已覆盖 softness/factor/alignoutline，稳定回退 CPU | 已具备 gate |
| undo / save 闭环 | 完整支持 | 已具备 | 已具备 |
| 结果一致性验证 | CPU 路径成熟 | 仍缺系统性预设矩阵与对照验证 | 重要剩余项 |

---

## 6. 阻断项已经重排

### 6.1 已从阻断项中移除的问题

以下问题在本轮代码更新后，不再属于“必须先从 0 搭建”的阻断项：

1. **严格门禁机制**
2. **基础 shared runtime**
3. **brush tip backend 的接口设计**
4. **composite passthrough 的基础通路**

它们仍有后续改进空间，但已经不是“没有这层就无法继续”的状态。

### 6.2 现在真正阻断 Brush V1 的问题

1. **Stamp path 的真实初始化闭环尚未完成**
   - lazy init 机制、pending image 模型、参数链都已落地
   - 但 allocator 透传缺口使 `predefined / texture / masking` 仍不能视为真实稳定可用

2. **Predefined Brush 尚未形成端到端可验证支持**
   - 这是从单一 auto brush 走向完整 paintbrush 的第一道硬门槛
   - 也是验证 backend 抽象是否真的可用的第一块试金石

3. **Texture / Masking Brush 的参数通路已有，但资源模型仍停留在原型态**
   - 当前有 pending image 延迟上传与 per-stroke params bypass ring buffer
   - 但缺少生产级资源常驻、缓存、预热、回收与验证体系

4. **颜色能力存在“提取 / gate / 运行时语义”不一致**
   - `LightnessStrength` 尚未完成完整语义闭环
   - `color_source` gate 已放开，但实现依据仍需补强

5. **Airbrush / Wash / Mirror / Sharpness / Wrap-around 尚未闭合**
   - 这些都属于 paintbrush 的真实使用面
   - 其中部分已经被 gate 住，部分仍需继续补 feature extraction 与语义对齐

6. **blend / composite 架构已出现重复实现扩散**
   - brush path、layer path、analyzer 各自维护支持与映射
   - 这会直接影响后续可维护性与结果一致性

7. **缺系统化验证矩阵**
   - 现在可以更安全地回退了，但“可控回退”不等于“已达成功版本”
   - 仍需要明确哪些预设应该走 GPU、哪些应该回退、两边结果如何对照

---

## 7. 对 Brush V1 的定义需要微调，但总体目标不变

建议继续保留 Brush V1 这个目标，但把它从“先把架构抽出来”调整为“在现有架构上完成第一个真正完整的 paintbrush 功能版本”。

### 7.1 Brush V1 的建议定义

> **Brush V1：在 Vulkan 模式下，`paintbrush` 作为一个真实可用引擎进入日常创作主链路；支持集合不再只限于 auto brush 基础预设，而是覆盖常用 paintbrush 预设的关键能力，同时所有未覆盖预设都能被稳定识别并自动回退。**

### 7.2 Brush V1 必须达到的能力

- `paintbrush` 引擎透明接入
- feature gate 与 fallback 稳定可依赖
- `Auto Brush` 与 `Predefined Brush` 两类笔尖
- Size / Ratio / Rotation / Softness / Scatter / Spacing 的一致语义
- 至少一组真实可用的 composite 模式集合
- Texture 的最小完整实现
- Masking Brush 的最小完整实现
- Airbrush / Wash / Mirror 中至少完成 Brush V1 所定义的最小闭环
- 多图层绘制、撤销、保存一致
- OpenGL / Vulkan 对照验证矩阵

### 7.3 Brush V1 暂可后置的内容

- Text Brush
- 更多 blend/composite 模式扩展
- 更多 brush engine 的 GPU 原生接入
- 非破坏节点与滤镜图层的系统扩展

---

## 8. 现在最缺的不是“再造一层”，而是“把现有三层真正打实”

上一次评估认为最关键的是先把三层抽象立住。  
这次重新看代码后，应改成：

> **三层抽象已经出现，当前最关键的是把它们真正接到位、补到位、验证到位。**

### 8.1 第一层：Preset / Feature Analysis

这一层已经具备雏形，价值很高：

- feature flag 取代粗字符串判断
- 预设级 unsupported reason 可直接用于 routing
- 能明确拒绝 engine / brush tip / composite / sharpness / wrap-around 等不支持能力，并为 texture / masking / color / wash 等能力提供更细粒度的分流基础

这一层已经过增强补全：

- ✅ `checkCurveOptionEnabled()` 覆盖 Krita 5.x `Pressure{ID}` + `{ID}Sensor` 双模式
- ✅ sharpness 提取增强：`softness` / `factor` / `alignoutline` 三种存储路径
- ✅ wrap-around 由 factory 运行时检测 `KisImage::wrapAroundModeActive()`
- ✅ lightness strength 提取能力已补齐
- ✅ scatter 提取（GPU 通过 dynamics 支持，不 gate）

### 8.2 第二层：Brush-based Shared Runtime

这一层已经开始承担真正的公共职责：

- 统一加载 brush resources
- 统一读取 size / opacity / flow / spacing / angle / ratio / softness
- 统一 dynamics 与 spacing 计算
- 统一 composite passthrough

剩下的关键不是简单增加字段，而是把更多 CPU `KisBrushBasedPaintOp` 共享语义真正吸收进来，包括：

- 生产级 brush resource 常驻与缓存
- texture / masking 的显存生命周期策略
- color feature 的真实支持边界
- brush path 与 layer path 的 blend 统一口径

而不是再回到 `KisVulkanPaintOp` 手工堆逻辑。

### 8.3 第三层：Brush Tip Backend

这一层目前最像“方向已对、落地未满”：

- `AutoBrushBackend / StampBrushBackend` 已存在
- `TextBrushBackend` 仍未实现
- backend 已经进入真实 GPU dab dispatch 路径，扩展参数链已补齐，但 `StampBrushBackend` 的端到端初始化仍未完全闭合

第三层的关键进展：

- ✅ backend-aware dispatch 已建立 — 后续新增 tip 不必回到旧的 `DabRound` 直通路径
- ✅ lazy init 机制已写入 — `ensureBackendInitialized()` 可在 render thread 侧初始化 backend
- ✅ 扩展参数通路已补齐 — per-stroke texture params bypass ring buffer
- 🔲 allocator 透传未完全闭合 — `StampBrushBackend` 仍未达到可定版运行时状态

---

## 9. 更新后的实施顺序

### 阶段 A：先修热路径闭环问题 **[机制已落地，端到端未完成]**

目标：让当前 backend-aware 路径从”进入主链路”变成”真实可靠可用”。

已完成事项：

- ✅ 补齐 backend 初始化调用链 — `BrushEngine::ensureBackendInitialized()` 延迟初始化
- ✅ backend 未初始化时不会吞掉 ring buffer 中的 dab — init 失败时返回 0，不消费
- ✅ texture 参数链闭合 — `StampBrushBackend::setStrokeTextureParams()` bypass ring buffer
- ✅ 延迟 image 上传 — `setPending*()` + `uploadPendingImages()` UI/render 线程分离
- ✅ allocator 从 `KisVulkanCanvas` 到 `BrushEngine::initialize()` 的透传已补齐
- ✅ `processStrokePoints()` 的失败路径已收口 — backend init / legacy pipeline 缺失时会中止当前 command buffer 录制并保留 dab
- ✅ Stamp backend 初始化链已补充可定位日志 — allocator / queue / pipeline / pending image 上传失败会给出明确错误点
- ✅ Predefined Brush 输入范围已收敛 — 当前仅将 raster(`png/jpg/jpeg/bmp`) 与 `gbr` 视为 Brush V1 目标范围，`abr/svg` 明确回退 CPU
- ✅ raster predefined tip 的 alpha 语义已补强 — alpha/灰度预处理已前移到 `BrushRuntime` 资源准备阶段，并通过 preset cache 复用；`StampBrushBackend` 上传路径不再承担像素级语义转换
- 🔲 验证 auto / stamp 两条路径都能稳定出图 — 待运行时验证

### 阶段 B：巩固现有门禁与共享层 **[已完成]**

目标：把已经出现的抽象变成稳定可依赖的基础设施。

已完成事项：

- ✅ 新增 `checkCurveOptionEnabled()` — 覆盖 Krita 5.x `Pressure{ID}` bool + `{ID}Sensor` XML 双模式
- ✅ sharpness 提取增强 — 覆盖 `Sharpness/softness`、`Sharpness/factor`（legacy）、`Sharpness/alignoutline`
- ✅ scatter 提取 — `checkCurveOptionEnabled("Scatter")`，GPU 通过 dynamics 系统支持，不 gate
- ✅ lightness strength 提取增强 — `checkCurveOptionEnabled("LightnessStrength")` 已可识别该能力
- ✅ wrap-around 运行时检测 — canvas 级属性由 `KisVulkanPaintOpFactory::createOp()` 通过 `KisImage::wrapAroundModeActive()` 检查，而非 preset analyzer
- ✅ `checkFeatureEnabled()` 增强 — 自动 fallback 到 `checkCurveOptionEnabled()` 覆盖新旧两种存储模式

### 阶段 C：补齐 Brush V1 的功能覆盖 **[进行中]**

目标：让 GPU paintbrush 的功能覆盖面从"窄集合"扩展到"常用预设可用"。

已完成事项：

- ✅ **Color HSV 随机变化** — CPU 侧在 `BrushRuntime::applyColorEffects()` 中实现，对色相/饱和度/明度施加随机偏移，使用 `KisPaintInformation::randomSource()` 保持可复现性
- ✅ **Color Mix（前景/背景混合）** — 通过 `KisVulkanDynamics` 的 `m_colorMix` 参数驱动，sensor 曲线控制混合比例，CPU 侧在 `applyColorEffects()` 中线性混合
- ✅ **Color Darken（暗化）** — 通过 `KisVulkanDynamics` 的 `m_darken` 参数驱动，对 RGB 做亮度缩放
- ⚠️ **Lightness Strength** — 当前已进入 `KisVulkanDynamics` 提取与评估结果，但仍需补齐真正的运行时语义闭环后才能视为完成
- ✅ **扩展 blend mode 集合** — 从 8 种增加到 15 种（新增 SoftLight/HardLight/Difference/Exclusion/Add/Subtract/Divide），三个 shader 同步更新
- ✅ **Wash mode（非增量模式）V1** — shader 级 `FLAG_WASH_MODE` 使用 max-alpha 合成防止重叠加深；per-dab 不乘 opacity；完整间接绘制层待后续迭代
- ⚠️ **PresetAnalyzer gate 更新** — `color_hsv`、`color_mix`、`color_darken`、`wash_mode` 的 gate 已移除；`lightness_strength` 与 `color_source` 的运行时依据仍需补强，当前不应直接视为“完全闭合”
- ⚠️ **Composite 架构收口** — 已抽出共享 `GpuBlendMode`、统一 `compositeOpId -> GpuBlendMode` 映射，并把 brush / layer shader 的 blend 数学下沉到共享 GLSL include；`brush / layer / analyzer` 的支持矩阵也已冻结到共享 path-aware blend matrix，并补充单元测试防止三处漂移；端到端验证仍未完成

待完成事项：

- 🔲 allocator 透传修复后的 Stamp path 端到端验证
- 🔲 Brush 资源预加载 / 显存常驻 / 缓存回收模型
- 🔲 `LightnessStrength` 运行时语义闭环
- 🔲 `color_source` 的真实支持范围收敛
- 🔲 Wash mode V2：独立间接绘制 GPU buffer + stroke-end 通过 `layer_composite.comp` 合成
- ⚠️ Predefined Brush 验证基础已补第一版 —— 已新增样本级 sanity：`testing_predefined_lod_spc13.kpp`、`testing_predefined_lod.kpp`、`testing_1000px_stamp_450_rotated.kpp` 的 preset analyzer + runtime 资源准备测试，并补上 `VULKAN_STARTED` canvasState 持久化修复；但 CPU / OpenGL / Vulkan 出图对照与 UV/旋转/ratio/softness 验证仍待完成
- 🔲 Sharpness 的 1px 快路径（整数坐标对齐）
- 🔲 完成 brush / layer / analyzer 三处 composite 支持矩阵的端到端验证
- 🔲 一致性修正与性能回归

### 阶段 D：建立验收与回归体系

目标：让 Brush V1 不是“看起来能用”，而是“有可持续验证边界”。

应做事项：

- 建立 paintbrush 预设分层清单
- 明确 GPU 白名单、CPU 回退清单
- 建立 OpenGL / Vulkan 对照结果基线
- 建立性能与正确性回归流程

---

## 10. 重新量化：还差几步

### 已经跨过的关键台阶

1. Vulkan 画布与 GPU 常驻底座已完成
2. `paintbrush` 工厂包装与 GPU/CPU 分流已完成
3. feature-level capability gate 已建立
4. shared runtime 已形成基础形态
5. backend 已进入真实调度路径，composite passthrough 与 undo/save 闭环已进入可用状态
6. **backend 延迟初始化机制已落地** — `ensureBackendInitialized()` + 未初始化时不消费 dab
7. **texture/masking 参数通路已补齐** — per-stroke params bypass ring buffer + pending image deferred upload

### 仍未跨过的关键台阶

1. 补齐 allocator 从 `KisVulkanCanvas` 到 `BrushEngine` 的透传，真正完成 Stamp path 初始化闭环
2. 补齐 `Predefined Brush` 端到端运行时验证
3. 把 Texture / Masking 从“参数链具备”推进到“显存资源模型 + 运行时验证闭合”
4. 把 color features 从“部分提取/部分放行”推进到“真实支持边界清晰”
5. 统一 brush / layer / analyzer 的 composite / blend 架构
6. Wash mode V2：独立间接绘制 GPU buffer
7. Sharpness 1px 快路径
8. 建立预设级验证矩阵
9. 建立生产级 brush resource preload / cache / reclaim 体系

因此更准确的判断是：

> 功能覆盖面确实已比早期原型大幅扩展，但距离 Brush V1 的主要距离已重新明确为：Stamp path 初始化闭环、资源常驻模型、颜色语义对齐、blend 架构统一，以及预设级验证矩阵。

---

## 11. 对当前代码的直接建议

### 11.1 高优先级修正点

1. **补齐 allocator 透传，真正完成 Stamp path 初始化闭环**
   - `BrushEngine::ensureBackendInitialized()` 机制已在，但 `KisVulkanCanvas` 仍需把 allocator 正确传入 `BrushEngine::initialize()`
   - `processStrokePoints()` 的失败路径也需要一起收口

2. **以 `Predefined Brush` 作为下一阶段主攻点**
   - 这是验证 brush tip backend 是否真的成立的第一块硬石头
   - allocator 修复后应立即做端到端运行时验证

3. **建立生产级 brush 资源模型**
   - 从“pending image + 首次 dab 上传”升级到“预加载 / 显存常驻优先 / 可回收缓存”
   - 目标是降低首笔延迟、切笔抖动与重复上传

4. **继续补齐 analyzer 与运行时能力的一致性**
   - wrap-around: factory 运行时检测 `KisImage::wrapAroundModeActive()`
   - sharpness: 覆盖 `softness/factor/alignoutline` 三种存储
   - `checkCurveOptionEnabled()`: 覆盖 Krita 5.x `Pressure{ID}` + `{ID}Sensor` 双模式
   - `LightnessStrength` 与 `color_source` 必须在运行时语义确认后再冻结支持状态

5. **统一 blend / composite 架构**
   - 统一 brush / layer / analyzer 的支持矩阵
   - 抽出共享 GLSL blend 函数库与共享 C++ 映射
   - 不做万能 shader，但必须消除重复实现继续扩散

6. **尽快建立预设级验证矩阵**
   - 现在的门禁已经足够严格，正适合开始建立 GPU 白名单与回归样本

### 11.2 不建议的方向

- 不建议重新把逻辑塞回 `KisVulkanPaintOp`
- 不建议继续增加“只为某个功能服务的临时特例路径”
- 不建议在 backend 抽象之外再开一条新的 tip dispatch 分支

这些做法会削弱这轮代码更新最有价值的成果。

---

## 12. 更新后的验收标准

Brush V1 完成时，建议至少满足以下验收条件：

### 功能验收

- `paintbrush` 常用预设存在明确的 GPU 支持集合
- `auto brush` 与 `predefined brush` 都可在 GPU 路径正常工作
- texture、masking、airbrush、wash 中至少完成 Brush V1 定义范围内的最小闭环
- 不支持的预设稳定回退 CPU
- backend 初始化缺失、吞 dab、扩展参数丢失这类热路径问题全部清零

### 架构验收

- capability gate 成为唯一可信的路由依据
- `KisVulkanBrushRuntime` 成为 brush-based 共享语义的主落点
- `BrushTipBackend` 成为 GPU tip dispatch 的真实统一入口
- brush 资源具备明确的 preload / residency / reclaim 策略
- brush path 与 layer path 的 composite / blend 支持矩阵一致且可维护

### 一致性验收

- OpenGL 与 Vulkan 在规定预设集合上结果可对照一致
- 撤销 / 重做 / 保存 / 重开一致
- 多图层绘制与支持的 composite 模式结果一致

### 质量验收

- 有明确的预设回归集合
- 有可执行的白名单 / 回退矩阵
- 有性能基线，确认架构收口没有破坏实时绘画主链路
- 有文档状态冻结机制，避免“代码未闭环、文档已完成”的漂移

---

## 13. 最终判断

这次代码更新之后，Vulkan 笔刷项目的状态应当重新定性：

- 它已经不再是“只有 auto brush 的单线试验”
- 也还没有到“完整 paintbrush 已完成”的阶段
- 它现在处在 **“架构骨架已成型，但热路径闭环与版本验证仍未达标”** 的阶段

当前最重要的三件事是：

1. 先补齐 Stamp path 的真实初始化闭环与运行时验证
2. 建立面向生产级的 brush 资源常驻 / 缓存 / 回收模型
3. 把 `Predefined Brush + Texture + Masking + Airbrush/Wash + 颜色语义 + blend 架构统一` 这些 Brush V1 阻断项逐个收掉

如果这三件事做对了，那么：

- Brush V1 可以在现有架构上自然收敛
- 后续其他 brush-based paintop 的接入会有可复用模板
- Vulkan 路径会从“严格受控的 GPU 接入版本”进一步走向“真实可扩展的笔刷后端”

因此，更新后的核心建议应改为：

> **当前不应定版；应先补齐 Stamp path 初始化闭环、资源常驻模型、颜色语义闭环、blend 架构统一与验证矩阵，再考虑创建定版分支和提交版本。**
