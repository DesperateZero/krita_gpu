# BR0 构建、测试与 upstream 对照证据（2026-09-18）

> 状态更新：本文只冻结 BR0 当时的证据与边界；51 记录 2026-09-19 的 BR1 功能/正确性 cutover，2026-09-20
> resident CPU 性能审计后 BR1 以 `BR1-PERF` 重开，见
> [52_br1_cpu_fast_path_optimization_plan_20260920.md](archive/br1_pre_m6_20260925/documents/52_br1_cpu_fast_path_optimization_plan_20260920.md)。本文中的
> “BR1–BR6 尚未实现/后续从 BR1 开始”均为 BR0 关闭时点的历史表述。

本文记录 BR0 F6 的本机可复现证据。它只证明 foundation、依赖边界和选定 CPU/OpenGL 核心路径，不证明
BR1–BR6 的 production PageStore、GPU stroke、合成、WSI 或性能目标。

## 1. 结论与正式状态

| 检查项 | 结果 |
|---|---|
| 最新未修改 `origin/master` CPU/OpenGL configure/build | 通过 |
| 最新未修改 `origin/master` 稳定核心回归 | 5/5 通过 |
| 当前树 CPU-only configure/build | 通过，构建图无 Vulkan target |
| 当前树 Vulkan foundation/UI adapter configure/build | 通过 |
| PageStore/Evaluation Graph foundation contracts | 9/9 通过（7 个命名 case + init/cleanup） |
| Foundation contracts | 11/11 通过 |
| 真实 Vulkan/VMA compute offscreen smoke | 通过，checksum `32896` |
| shader 二次构建确定性 | `ninja: no work to do.` |
| architecture guard / `git diff --check` | 通过 |
| 当前树稳定 CPU/OpenGL 核心回归 | 6/6 通过 |
| 产品 `kritaui` 对 Vulkan backend 的链接 | 无 |
| 当前 BR0 改动位于最新 upstream 之上 | 通过，`origin/master...HEAD` 为 `0 1` |

因此 BR0 已正式关闭。该结论只适用于 foundation、依赖边界及本文列出的基线回归；BR1–BR6 的 production
能力仍未实现，产品 Vulkan 入口继续保持关闭。

## 2. Revision 与分支关系

- 当前 HEAD：`f5fbbde618df6fb4e1068ace7381c339a70dd4c0`
- 目标 upstream：`9a24ae0d8c070884fb013594191002e1a1b39a19`
- merge-base：`9a24ae0d8c070884fb013594191002e1a1b39a19`
- `git rev-list --left-right --count origin/master...HEAD`：`0 1`
- 重放前归档分支：`archive/br0-pre-upstream-replay-20260918`
- 重放前归档提交：`58bc9bbf3fd33c340ef571f5197e45ce982c8355`
- 旧 Vulkan 原型归档：`archive/vulkan-prototype-pre-br0-20260918`，提交 `7207640968`

未修改 upstream 通过 detached worktree 验证。随后先把原工作区完整提交到重放前归档，从目标 upstream 建立
校正分支，并以 squash 方式只重放 BR0 净变更。冲突仅位于两个测试 CMake 清单：保留 upstream 新增测试、
不恢复 upstream 已删除测试，并加入 PageStore foundation test；解决后完成本文全部复验。

## 3. 工具链和设备

| 组件 | 版本/值 |
|---|---|
| macOS | 15.7 |
| 架构 | universal `x86_64;arm64`，测试运行于 arm64 |
| CMake | 3.29.3 |
| Ninja | 1.13.2.git.kitware.jobserver-pipe-1 |
| 编译器 | Apple clang 17.0.0 (`clang-1700.6.4.2`) |
| Qt | 6.8.0 |
| Vulkan loader/SDK | instance 1.4.341 |
| `glslc` / shaderc | 2026.1 |
| SPIRV-Tools | 2026.1 |
| SPIRV-Cross | `vulkan-sdk-1.4.335.0-28-ga0fba56c` |
| GPU | Apple M4 integrated GPU |
| Vulkan device API | 1.4.334 |
| driver | MoltenVK 1.4.1，driverVersion 0.2.2209，conformance 1.4.4.0 |
| ICD | `/usr/local/share/vulkan/icd.d/MoltenVK_icd.json` |

## 4. 配置和构建

### 4.1 未修改 upstream baseline

配置关键项：

```text
-DBUILD_WITH_QT6=ON
-DALLOW_UNSTABLE=QT6
-DBUILD_TESTING=ON
-DCMAKE_BUILD_TYPE=RelWithDebInfo
-DCMAKE_OSX_ARCHITECTURES=x86_64;arm64
-DCMAKE_DISABLE_FIND_PACKAGE_Vulkan=TRUE
```

在 detached `origin/master` worktree 中构建 `kritaimage` 和 `kritaui`，1629/1629 步成功。

### 4.2 当前树 CPU-only

除上面的公共项外：

```text
-DBUILD_VULKAN_FOUNDATION=OFF
-DBUILD_VULKAN_UI_ADAPTER=OFF
-DCMAKE_DISABLE_FIND_PACKAGE_Vulkan=TRUE
```

CMake 明确输出 `Vulkan foundation disabled; Vulkan SDK and shader tools are not required`。在全新的
`_build-br0-cpu` 中构建 `kritaimage`、`kritaui` 和六个稳定测试 target 成功；`ninja -t targets` 未找到
`kritavulkan` 或 `vulkan_shader` target。

### 4.3 当前树 foundation

```text
-DBUILD_VULKAN_FOUNDATION=ON
-DBUILD_VULKAN_UI_ADAPTER=ON
```

在重新配置到当前 HEAD 的 `_build` 中构建 `krita_vulkan_shader_assets`、`kritavulkanbackend`、
`kritavulkanoffscreen`、`kritavulkanuiadapter`、PageStore 与 foundation contracts 成功。`kritaui`、backend、
UI adapter 和 offscreen 产物均为 `x86_64;arm64` universal binary；产品 `libkritaui.dylib` 不链接 Vulkan
backend/loader，offscreen smoke 不链接 `kritaui` 或 UI adapter。VMA include 已标记为 system include，
offscreen Vulkan 结构均先零初始化再显式设置 `sType`；最终该 target 复编译无新增告警。

## 5. Shader asset 与 ABI 证据

`foundation_checksum.comp` 由 `glslc --target-env=vulkan1.2 -O` 编译，经 `spirv-val` 校验、
SPIRV-Cross reflection 和生成器 ABI 检查后嵌入 `kritavulkanbase`。

| 资产 | SHA-256 |
|---|---|
| GLSL source | `625931d49b0cd98d4e76b3e57947b6c0526ac0c9fa1737d77a97f2163d65eeb4` |
| SPIR-V（254 words） | `7635dd81a1fd778b947017418a7ea6b7e3a05911befc41e97ebd17ca0a651ff0` |
| canonical reflection | `6404a2d50644ecdc175bbd69ace4f07343d19fe3829ee96f2bb51a14dd124467` |

冻结 ABI：compute `main`、workgroup `64x1x1`、set 0 binding 0/1 storage buffers、4-byte uint push
constant。完成一次构建后再次构建 target 输出 `ninja: no work to do.`。

## 6. 测试结果

本轮 upstream 重放、Evaluation Graph 接口调整和 offscreen 告警修正后，重新构建 CPU/Vulkan foundation 的
`kritaimage`、`KisPageStoreFoundationTest`、`kritavulkanbackend`、`KisVulkanFoundationContractsTest` 与
`kritavulkanoffscreen` 均通过；不是沿用改动前二进制。

`KisPageStoreFoundationTest` 当前 9/9 通过，除原 PageStore/state-machine/SSD fail-closed 外还覆盖：

- EvalGraphIR 不要求非空 MutationRootSet；
- Layer Stack 只是 schema-specific lowerer，BR4 前 fail closed；
- duplicate producer/cycle 等 malformed DAG 被拒绝；
- GPU evaluation capability 必须同时匹配 feature、operation semantic version、open value type 与逐端口 format；
- `KisEvaluationPlanner`、`KisDerivedSurfaceCache` 在 BR4 前不伪造可运行结果。

### 6.1 当前树 foundation

```text
libs-vulkanbackend-KisVulkanFoundationContractsTest: 11 passed
libs-vulkanbackend-kritavulkanoffscreen: passed
Vulkan BR0 offscreen smoke passed on Apple M4; checksum=32896;
shader=7635dd81a1fd778b947017418a7ea6b7e3a05911befc41e97ebd17ca0a651ff0
```

offscreen smoke 实际创建 portability Vulkan instance、Vulkan 1.2 logical device、compute queue、VMA allocator、
两个 mapped storage buffer、descriptor/pipeline、timeline semaphore；提交 compute dispatch，并使用 5 秒上限等待结果。

### 6.2 当前树 CPU/OpenGL

稳定核心套件 6/6 通过：

- `libs-image-kis_transaction_test`
- `libs-image-kis_stroke_test`
- `libs-image-kis_strokes_queue_test`
- `libs-image-KisPageStoreFoundationTest`
- `libs-image-tiles3-kis_tiled_data_manager_test`
- `libs-ui-KisFrameCacheStoreTest`

### 6.3 未修改 upstream 对照

相同套件去掉当前树新增的 PageStore test 后，5/5 通过。另行探索的
`kis_image_test`、`kis_paint_device_test`、`kis_simple_update_queue_test` 和 `kis_update_scheduler_test` 在最新
未修改 upstream 与当前树上以相同方式失败：前两项要求已安装的 macOS Krita bundle 资源，后两项在当前
Qt 6.8/arm64 测试环境的 checksum/scheduler 路径收到 SIGSEGV。这四项记录为 upstream parity 限制，不作为
BR0 引入的回归，也不被写成通过。

## 7. 静态与依赖边界

- `build-tools/ci-scripts/check-vulkan-architecture.sh`：通过，并已接入 `.gitlab-ci.yml`。
- `git diff --check`：通过。
- CPU-only target graph：无 backend、shader、offscreen 或 UI adapter target。
- `libkritaui.dylib`：无 Vulkan/backend 动态依赖。
- offscreen executable：无 `kritaui`/UI adapter 动态依赖。
- legacy `KisVulkanCanvas` 产品引用已从 `libs/ui` 非 adapter 路径删除。

## 8. 正式关闭判定

- upstream 历史条件已满足：HEAD 是目标 `origin/master` 的直接后继，分叉计数 `0 1`；
- CPU-only、Vulkan foundation、shader、真实设备 offscreen、PageStore、稳定 CPU/OpenGL 回归及静态边界全部通过；
- 产品 Vulkan 入口仍关闭，foundation skeleton 没有被声明为 BR1–BR6 implementation；
- 重放前状态与更早的旧原型均有独立归档分支可追溯。

据此，BR0 于 2026-09-18 正式关闭；后续工作从 BR1 开始，并继续遵守 BR1–BR6 的顺序与各自出口。
