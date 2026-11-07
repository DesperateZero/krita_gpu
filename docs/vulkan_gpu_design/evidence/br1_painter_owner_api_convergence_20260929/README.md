# BR1 Painter owner 公共接口收缩，2026-09-29

本批落实“主干侵入必须优雅、新管线保持内聚”的接口裁决：Painter 对外只保留一个非拥有 transaction 绑定，具体写入口不再并列暴露 owner 参数。它是接口收缩和 caller 统一，不改变 PageStore 像素、版本或终结语义。

## 改动与责任

- `KisPainter::setStrokeMutationOwner(KisTransaction *)` 是唯一 public owner 语义桥。strategy 负责保活和清空绑定，painter 不取得所有权。
- 删除 `bitBlt`、标量 `bltFixed`、QRect/vector multi-dab `bltFixed` 和 PaintDevice-source `renderMirrorMask` 的 5 个 public 显式 owner 变体；增加 1 个无 owner vector multi-dab public 入口承接生产调用。本批前工作树到当前工作树的 public 声明净变化为 -4。
- owner 参数只保留在 private `bitBltImpl`、`bltFixedImpl` 和 `renderMirrorMaskImpl`。测试在 worker 启动前绑定 painter，再调用与生产 brush 相同的 public API。
- `KisTransaction` 仍唯一拥有 commit/cancel/undo，scheduler 仍唯一拥有 job 顺序和失败终点；page、reservation、budget、waiter 与 PageStore 内部结果没有越过 DataManager 适配边界。

代码范围为 `libs/image/kis_painter.h`、`libs/image/kis_painter.cc`、`libs/image/kis_painter_blt_multi_fixed.cpp` 和 `libs/image/tests/kis_painter_test.cpp`。架构生成物只刷新源码身份与真实调用图，未提高 manifest、ownership、census 或 external intrusion 上限。

## 目标验证

构建只覆盖本批的真实消费者：

```text
/Users/apple/Library/Android/sdk/cmake/3.22.1/bin/ninja -C _build-br0-cpu kis_painter_test KisDabRenderingQueueTest -j2
/Users/apple/Library/Android/sdk/cmake/3.22.1/bin/ninja -C _build-br0-cpu kritadefaultpaintops -j2
```

第一条构建完成 Painter 与 brush 测试目标。首次 Painter 启动还检测到构建目录中的旧动态 `kritadefaultpaintops.so` 引用了已删除的 owner overload；第二条命令重建真实动态插件，随后加载复验不再出现该未解析符号。没有为兼容陈旧构建物恢复 public overload。

目标运行环境为 `QT_QPA_PLATFORM=offscreen`、`KIS_TEST_PREFIX_PATH=$PWD/_install`、`KIS_TEST_PLUGIN_PATH=$PWD/_build-br0-cpu/bin` 和对应 `DYLD_LIBRARY_PATH`：

| 目标范围 | 结果 |
|---|---:|
| `kis_painter_test`：fixed/multi-dab owner、拒绝、取消、snapshot、selection、稀疏范围和并行的 16 个测试函数及其数据行 | 520 passed / 0 failed / 0 skipped |
| `KisDabRenderingQueueTest testBrushPagePartition testSharpnessLine` | 50 passed / 0 failed / 0 skipped |
| 动态插件重建后的 `kis_painter_test testFixedCursorOwnerRejection` 加载复验 | 3 passed / 0 failed / 0 skipped |

资源库扫描会输出缺失开发资源与 writable swap fallback 警告；目标断言全部通过。重建前唯一与本批相关的动态符号错误在重建后消失。

调用图按当前 `_build-br0-cpu/compile_commands.json` 重生成，随后刷新源码身份并执行结构门：

```text
python3 build-tools/ci-scripts/generate-pagestore-callgraph.py --compile-commands _build-br0-cpu/compile_commands.json
python3 build-tools/ci-scripts/check-pagestore-architecture.py --build-dir _build-br0-cpu --write-baseline
python3 build-tools/ci-scripts/check-pagestore-architecture.py --build-dir _build-br0-cpu
```

最终结果为 21 manifest entries、25 ownership facts、16 runtime census groups、1,818 indexed APIs、19,722 reverse-call edges、17 callback registrations 和 19 frozen external intrusion files。相对上一冻结结果减少 6 个 indexed APIs 和 168 条边，external intrusion 文件数不变。

活动文档检查覆盖 39 个文档、3,272 个本地链接和 690 个 Markdown fragment，错误为 0；归档目录未参与当前状态判断。`git diff --check` 通过，动态插件未解析符号表中也没有残留带 `KisTransaction` 的 `KisPainter` 调用。

## 后续边界

本批不授予默认 direct stroke、完整 BC9/BC10、M6–M8 或 BR1-PERF 资格。后续 UI/tool/paintop/painter/PaintDevice/scheduler public/protected API 默认净增长为零；测试不能要求恢复显式 owner overload。下一生产批留在 PageStore 内完成完整收费、多 store/多文档公平和释放进度。continuation 只有在原未执行 job 的 ownership transfer、可靠分类、真实 scheduler consumer 和旧失败分支删除能同批闭合时重新领取。
