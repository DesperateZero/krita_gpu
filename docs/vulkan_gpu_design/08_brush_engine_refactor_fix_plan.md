# Vulkan 笔刷重构施工方案

**日期**：2026-04-02  
**适用范围**：`krita/libs/image_vulkan`、`krita/libs/ui/vulkan`、`docs/vulkan_gpu_design/07_brush_engine_gap_and_roadmap.md`  
**用途**：把 Vulkan `paintbrush` 从“已有骨架但状态失真、能力未闭环”的阶段，推进到可按顺序实施、可验证、可收敛的生产级施工方案。

---

## 1. 使用方式

本文件不是问题清单，而是**执行清单**。

阅读方式：

1. 按阶段顺序实施，不跳阶段
2. 每个阶段只在“完成判定”全部满足后再进入下阶段
3. 如果某个阶段需要改动 `07_brush_engine_gap_and_roadmap.md` 的状态判断，必须同步修订
4. 若某个任务完成后发现前置判断失效，应先回到本文件修订任务顺序，再继续开发

执行原则：

- 先修真实阻断项，再做能力扩展
- 先做资源与生命周期闭环，再做性能优化
- 先统一支持边界，再扩大支持范围
- 不为短期“可画”牺牲长期可维护性

---

## 2. 最终交付目标

实施完成后，应达到以下目标：

- `paintbrush` 在 Vulkan 模式下可作为真实可用引擎进入日常绘画主链路
- `Auto Brush` 与 `Predefined Brush` 都可稳定走 GPU
- Texture / Masking / Airbrush / Wash / Mirror / 常用 Composite 模式具备明确支持边界
- brush 资源具备预加载、显存常驻优先、缓存复用、可控回收能力
- brush path / layer path / analyzer 的 blend/composite 口径统一
- 文档、代码、门禁、验证矩阵四者一致

---

## 3. 总施工顺序

必须按以下顺序执行：

1. **S0：状态冻结与基线建立**
2. **S1：修复 Stamp path 初始化闭环**
3. **S2：完成 Predefined Brush 端到端跑通**
4. **S3：建立生产级 brush 资源模型**
5. **S4：补齐颜色语义闭环**
6. **S5：统一 blend / composite 架构**
7. **S6：补齐 Brush V1 功能闭环**
8. **S7：建立验证矩阵与定版门槛**

禁止跳过：

- 没修完 S1，不做 S2 结论
- 没修完 S3，不宣布 texture / masking 可定版
- 没修完 S5，不继续扩展新的 blend mode
- 没修完 S7，不宣布 Brush V1 可定版

---

## 4. S0：状态冻结与基线建立

### 目标

- 把当前代码状态、文档状态、后续施工范围锁定为同一口径

### 输入

- 当前 `07_brush_engine_gap_and_roadmap.md`
- 当前 `08_brush_engine_refactor_fix_plan.md`
- 当前 `libs/image_vulkan` 代码状态

### 任务

#### T0-1 文档口径冻结

- 把 `07` 文档中所有“已完成 / 已修复 / 已具备”的表述重新分类为：
  - 机制已写入
  - 参数链已具备
  - 运行时已跑通
  - 已验证可纳入支持范围

输出：

- `07` 文档不再把以下内容写成“已完成”：
  - Stamp path 初始化闭环
  - `LightnessStrength` 完整语义
  - `color_source` 真实支持
  - texture / masking 的生产级资源能力
  - blend 架构统一

#### T0-2 建立当前真实阻断项清单

- 在 `07` 与本文件中保持同一阻断项集合：
  - allocator 透传缺口
  - Stamp path 端到端验证缺失
  - 资源模型仍为原型态
  - 颜色语义不一致
  - blend 架构重复实现
  - 验证矩阵缺失

输出：

- `07` 与 `08` 的阻断项列表一致

### 完成判定

- `07` 与 `08` 的状态描述一致
- 当前已知问题没有遗漏
- 后续所有施工阶段都能在本文件中找到入口

---

## 5. S1：修复 Stamp path 初始化闭环

### 目标

- 让 `StampBrushBackend` 真正具备可初始化、可上传、可绘制、可失败回退的端到端能力

### 依赖

- S0 完成

### 任务

#### T1-1 补齐 allocator 透传

改动点：

- `KisVulkanCanvas`
- `KisVulkanBrushEngine`

执行：

- 把 `memoryPool->allocator()` 从 `KisVulkanCanvas` 正确传入 `BrushEngine::initialize()`
- 确认 `BrushEngine` 保存的 allocator 在 lazy init 路径中进入 `StampBrushBackend::InitParams`

完成标准：

- `StampBrushBackend::initialize()` 使用到的 allocator 不再为 `VK_NULL_HANDLE`
- 当前状态：已完成代码落地，待运行时验证

#### T1-2 收口 `processStrokePoints()` 失败路径

改动点：

- `KisVulkanBrushEngine.cpp`

执行：

- 检查 `beginCommandBuffer()` 后 backend init 失败时的退出路径
- 保证命令缓冲状态不会悬挂
- 保证失败不消费 dab
- 保证后续重试仍可继续工作

完成标准：

- 所有 early return 路径都具备明确的 command buffer 状态收口
- 当前状态：已完成代码落地，待结合手工验证确认重试链路

#### T1-3 核对 Stamp backend 初始化链

改动点：

- `KisVulkanBrushTipBackend.cpp`
- `KisVulkanBrushEngine.cpp`

执行：

- 复核以下链路：
  - `ensureBackendInitialized()`
  - `StampBrushBackend::initialize()`
  - `createDummyTexture()`
  - `uploadPendingImages()`
  - `uploadTexture()`

完成标准：

- 初始化失败时有可定位日志
- 初始化成功后 `brush/pattern/mask/dummy` descriptor 状态正确
- 当前状态：日志补强已完成；descriptor 正确性仍待运行时验证

#### T1-4 增加最小运行时验证点

不要求先写完整自动化测试，但至少需要可重复验证：

- auto brush 路径能画
- predefined brush 路径能画
- texture 开启时不会因初始化失败而掉回空输出
- masking 开启时不会吞 dab

输出：

- 一份最小手工验证清单，纳入 `07` 或后续验证矩阵文档
- 建议最小清单：
  - `Auto Brush / 无 texture / 无 masking`：确认 GPU 路径可稳定出图
  - `Predefined Brush / raster( png jpg jpeg bmp )`：确认 GPU 路径可稳定出图
  - `Predefined Brush / gbr`：确认 GPU 路径可稳定出图
  - `Predefined Brush / abr 或 svg`：确认会被稳定 gate 并回退 CPU
  - `Texture + Auto Brush`：确认不会因 stamp backend init 失败而空输出
  - `Masking Brush + Auto Brush`：确认不会吞 dab，失败时可重试

### 完成判定

- allocator 透传已落地
- Stamp path 能稳定初始化
- init fail 不消费 dab 且不会留下脏状态
- auto / predefined 最小绘制链都可验证

---

## 6. S2：完成 Predefined Brush 端到端跑通

### 目标

- 把 `Predefined Brush` 从“代码路径存在”推进到“真实可用”

### 依赖

- S1 完成

### 任务

#### T2-1 固化 Predefined Brush 的输入资源路径

改动点：

- `KisVulkanBrushRuntime::loadPredefinedBrushTip()`

执行：

- 统一 `filename / resource path / fallback` 的解析顺序
- 明确哪些格式进入 Brush V1 支持范围
- 对不在支持范围内的格式明确 gate 或 fallback 策略

完成标准：

- 支持清单明确
- fallback 不再掩盖真实不支持问题
- 当前状态：已完成第一版范围收敛，当前支持 raster(`png/jpg/jpeg/bmp`) 与 `gbr`；`abr/svg` 明确 gate 回退 CPU

#### T2-2 跑通 shader 采样链

改动点：

- `dab_stamp.comp`
- `StampBrushBackend`

执行：

- 验证 `FLAG_PREDEFINED_TIP` 下的 UV、边界、maskAlpha 逻辑
- 确认 brush tip 纹理上传格式、采样格式与 shader 预期一致
- 修正必要的尺寸、旋转、缩放或 alpha 解释问题

完成标准：

- predefined tip 出图正确
- 不出现“初始化成功但视觉错误”的假闭环
- 当前状态：已完成第一版 alpha 语义修正，`StampBrushBackend` 对 brush tip / masking brush 优先提取 alpha 通道，texture pattern 继续按灰度采样；仍待运行时对照验证 UV、旋转、ratio 与 softness
- 实现路径修正：alpha / 灰度预处理不再停留在 `StampBrushBackend` 上传热路径，而是前移到 `BrushRuntime::loadResources()` 的资源准备阶段；backend 只接收已准备好的单通道图像并负责上传/绑定

#### T2-3 建立 Predefined Brush 验收样本

执行：

- 选出一组 representative 预设：
  - 简单位图笔尖
  - 带旋转
  - 带 ratio
  - 带 softness
- 对照 CPU / OpenGL / Vulkan 输出差异
- 当前样本候选：
  - `testing_predefined_lod_spc13.kpp`：现有 predefined LOD 基线
  - `testing_predefined_lod.kpp`：备用 predefined LOD 基线
  - `testing_1000px_stamp_450_rotated.kpp`：旋转类样本
  - `colorsmudge_predefined.kpp`：真实复杂预设（用于覆盖更多 runtime 组合）

完成标准：

- 至少有一组可冻结的 predefined brush 样本集
  - 样本集已接入最小自动化 sanity（preset analyzer + runtime 资源准备），避免“文件存在但链路断开”

### 完成判定

- Predefined Brush 不再只是“目标范围”
- 至少一组常用预设可稳定进入 GPU 路径并正确出图

---

## 7. S3：建立生产级 brush 资源模型

### 目标

- 从“pending image + 首次 dab 上传”升级为“预加载 + 显存常驻优先 + 可复用缓存”

### 依赖

- S2 完成

### 任务

#### 最终实现路径（冻结口径）

- **资源语义准备层**：`KisVulkanBrushRuntime::loadResources()` 负责 `brush tip / texture / masking` 的资源定位、文件解码、alpha/灰度语义整理
- **preset 级缓存层**：优先使用 `KisPaintOpSettings::resourceCacheInterface()` 缓存“已准备好的单通道 QImage”，key 与资源路径/定义绑定；cache miss 时才本地生成并回填
- **backend 上传层**：`StampBrushBackend` 只处理 Vulkan upload / descriptor bind / pending image 生命周期，不再承担像素级语义转换
- **render thread 契约**：render thread 上允许的工作仅包含 lazy init、staging/upload、descriptor 更新；不再做 `QImage` 像素遍历类预处理
- **后续 S3 延展**：在此基础上再引入 GPU residency cache，把“已准备好的单通道资源”进一步提升为“可复用的显存常驻纹理”

冻结原则：

- 不把“为纠正 alpha 语义而新增的像素遍历”长期留在 backend 上传热路径
- 不让 fallback circle mask 掩盖资源缺失或格式不支持
- 不在 shader 中额外承担本应在资源准备阶段完成的静态语义转换

#### T3-1 定义 brush resource cache 接口

需要明确的对象：

- brush tip 资源
- texture pattern 资源
- masking brush 资源

需要明确的 key：

- preset id
- resource file / checksum / generation key
- 与尺寸无关和与尺寸有关的部分分别建模

输出：

- 一份 C++ 结构设计与 ownership 约定
- 约定第一阶段 cache payload 先存“已准备好的单通道 QImage”，第二阶段再引入 GPU residency 对象

#### T3-2 把资源加载从 paintop 实例化路径拆分

当前问题：

- `loadResources()` 同时负责读取、保存、上传准备

执行：

- 拆分为：
  - resource description resolve
  - CPU side decode
  - CPU side semantic prepare（alpha 提取 / 灰度化 / fallback 判定）
  - GPU cache lookup / populate
  - stroke-time bind

完成标准：

- `KisVulkanBrushRuntime` 不再直接承担所有资源生命周期
- `StampBrushBackend` 不再做像素语义预处理

#### T3-3 实现预热策略

目标：

- 选中 preset 或创建 paintop 时尽早触发资源准备
- 避免首笔承担重上传

执行：

- 先实现“preset 激活后预解析 + 尝试预上传”
- 若现阶段不便接 UI 选笔事件，则至少在 paintop 创建时提前完成上传，而不是拖到首个 dab

完成标准：

- 常用 preset 首笔延迟明显下降

#### T3-4 实现缓存回收策略

要求：

- 不再依赖频繁 `vkDeviceWaitIdle()`
- 回收必须安全
- 支持引用计数或 LRU

完成标准：

- 重复切笔不再频繁重复上传同一资源
- 回收路径不会引入明显卡顿

### 完成判定

- 有独立 brush resource cache
- 有预热策略
- 有回收策略
- 首笔延迟和切笔体验比原型路径明显改善

---

## 8. S4：补齐颜色语义闭环

### 目标

- 让颜色能力从“部分提取、部分放行”变成“真实支持范围清晰”

### 依赖

- S1 完成
- S3 建议完成后再做，以免资源路径变化影响验证

### 任务

#### T4-1 完成 `LightnessStrength` 真正生效链

执行：

- 明确它应在 CPU 侧还是 shader 侧生效
- 把 `KisVulkanDynamics` 求出的结果真正接入最终颜色路径
- 与 CPU 行为做对照

完成标准：

- `LightnessStrength` 不再只是“已提取”，而是“已生效”

#### T4-2 收敛 `Color Source` 支持范围

执行：

- 明确支持哪些 `ColorSource/Type`
- 对支持项补齐运行时实现
- 对不支持项恢复 gate 或明确 fallback

完成标准：

- 文档、analyzer、运行时三者口径一致

#### T4-3 颜色功能分级冻结

将颜色能力冻结为三类：

- Brush V1 支持
- 明确回退 CPU
- 后续版本再做

完成标准：

- 颜色功能不再有“代码看起来支持、文档说支持、运行时不稳定”的灰区

### 完成判定

- `LightnessStrength` 已完成闭环
- `Color Source` 支持范围已冻结
- 颜色能力支持矩阵可写入 `07`

---

## 9. S5：统一 blend / composite 架构

### 目标

- 统一口径，不统一成单个万能 shader

### 依赖

- S2 完成

### 任务

#### T5-1 抽取共享 `GpuBlendMode`

执行：

- 建立唯一的 GPU blend enum 定义
- brush path、layer path、analyzer 都引用这份定义

完成标准：

- 不再维护多份枚举映射

#### T5-2 抽取共享 C++ composite 映射

执行：

- 统一 `compositeOpId -> GpuBlendMode`
- brush runtime、node sync、preset analyzer 使用同一来源

完成标准：

- 新增 mode 时只改一份主映射

#### T5-3 抽取共享 GLSL blend 函数库

执行：

- 把 `dab_round.comp`、`dab_stamp.comp`、`layer_composite.comp` 中重复的 blend 数学下沉到共享 include
- 各 shader 保留各自入口和上下文，不强行合并

完成标准：

- blend 数学只维护一份
- shader 仍保持各自职责

#### T5-4 冻结支持矩阵

执行：

- 明确 brush path 支持哪些 mode
- 明确 layer path 支持哪些 mode
- 文档里写清楚“相同”“子集”“尚未对齐”的地方

完成标准：

- 不再出现文档与代码支持数不一致

当前状态：

- ✅ T5-1 已完成第一版：已新增共享 `KisVulkanGpuBlendMode`，brush runtime、preset analyzer、node sync 改为引用同一份 GPU blend enum / composite 映射
- ✅ T5-2 已完成第一版：`compositeOpId -> GpuBlendMode` 已收口到共享 C++ 映射，不再在三处各自维护表
- ✅ T5-3 已完成第一版：`dab_round.comp`、`dab_stamp.comp`、`dab_round_subgroup.comp`、`layer_composite.comp` 的 blend 数学已下沉到共享 `shaders/common/kis_blend.glsl`
- ⚠️ T5-4 已完成第一版：`brush / layer / analyzer` 的支持矩阵已冻结到共享 path-aware blend matrix，并补充单元测试防止三处漂移；文档口径已同步，但端到端一致性验证仍未收口

### 完成判定

- brush / layer / analyzer 三处不再各自漂移
- 新增 blend mode 的成本和风险都显著下降

---

## 10. S6：补齐 Brush V1 功能闭环

### 目标

- 把 Brush V1 剩余能力收口为“可正式支持”的集合

### 依赖

- S1-S5 完成

### 任务

#### T6-1 Texture / Masking Brush 最小完整实现验收

执行：

- 在 S3 资源模型基础上验证 texture / masking 的真正运行时稳定性
- 确认 shader 结果、资源绑定、生命周期、回收都稳定

#### T6-2 Airbrush 重采样闭环

执行：

- 对照 CPU timing 语义
- 验证长笔触、停顿、重采样节奏是否正确

#### T6-3 Wash V2

执行：

- 建立独立间接绘制 buffer
- 在 stroke-end 通过专门 composite pass 合成
- 不再依赖仅靠 max-alpha 模拟全部 wash 语义

#### T6-4 Sharpness 1px 快路径

执行：

- 设计并接入整数坐标对齐快路径
- 保持与 CPU 行为的可解释差异边界

#### T6-5 Mirror / spacing / auto spacing 语义对齐

执行：

- 把运行时结果与 CPU 路径做系统对照
- 修正偏差较大的行为

### 完成判定

- Brush V1 支持集合形成
- 不支持集合也形成
- `07` 可给出明确支持边界

---

## 11. S7：建立验证矩阵与定版门槛

### 目标

- 给定版提供硬证据，而不是凭主观判断

### 依赖

- S1-S6 完成

### 任务

#### T7-1 建立预设白名单 / 回退清单

输出：

- GPU 支持预设集
- CPU 回退预设集
- 每类原因说明

#### T7-2 建立 OpenGL / Vulkan 对照基线

输出：

- 按预设分类的对照结果
- 明确“允许差异”和“不可接受差异”

#### T7-3 建立性能基线

必须覆盖：

- 首笔延迟
- 连续笔触稳定性
- 切笔耗时
- 撤销后恢复时间

#### T7-4 建立文档更新规则

要求：

- 没有验证证据，不允许把功能写成“已完成”
- 状态更新必须同步 `07`
- 若支持矩阵变化，必须同步修改白名单 / 回退清单

### 完成判定

- 可以明确回答：
  - 哪些预设支持 GPU
  - 哪些必须回退 CPU
  - 为什么支持
  - 为什么不支持
  - 改动后是否退化

---

## 12. 每阶段交付物

每个阶段结束时必须产生可检查交付物：

- **S0**：修订后的 `07` 与本文件
- **S1**：可运行的 Stamp path + 最小验证记录
- **S2**：Predefined Brush 样本集与对照结果
- **S3**：brush resource cache 设计与实现
- **S4**：颜色支持矩阵
- **S5**：统一 blend 映射与共享 GLSL 库
- **S6**：Brush V1 支持集合
- **S7**：白名单 / 回退矩阵 / 对照基线 / 性能基线

---

## 13. 不允许的施工方式

- 不允许继续把共享逻辑塞回 `KisVulkanPaintOp`
- 不允许为了快速接功能继续增加临时特判分支
- 不允许在 blend 架构未统一前继续复制粘贴 shader 数学
- 不允许在资源缓存未建立前，把“首次 dab 上传”方案包装成最终方案
- 不允许在验证矩阵缺失时宣布 Brush V1 可定版

---

## 14. 当前立即开工项

如果现在开始施工，第一批必须直接执行的是：

1. S1 / T1-1：补齐 allocator 透传
2. S1 / T1-2：收口 `processStrokePoints()` 失败路径
3. S1 / T1-3：复核 Stamp backend 初始化链
4. S1 / T1-4：建立最小运行时验证
5. S2 / T2-1：冻结 Predefined Brush 输入资源支持范围

只有这批完成后，后面的资源模型、颜色闭环、blend 统一才有可信基础。

---

## 15. 最终判断

本施工方案的核心不是“再讨论问题”，而是把后续开发改成一条明确的工程路径：

- **先把 Stamp path 做成真的**
- **再把资源模型做成生产级**
- **再把颜色与 blend 的支持口径做一致**
- **最后用验证矩阵给 Brush V1 定版**

因此，后续是否可以宣布某项能力“完成”，不再取决于代码里是否出现了对应分支，而取决于它是否同时满足：

1. 有正确门禁
2. 有运行时闭环
3. 有清晰生命周期
4. 有一致文档口径
5. 有可复现验证证据
