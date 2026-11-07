# S01 补充：事务终结调用者迁移清单

返回[指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)或 [S01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01_stroke_scope_and_failure.md:5)。本篇是代码关系索引；行为与阶段状态仍以 92 §9.3、§15 为准，不另立完成状态。

核对 2026-09-27 当前工作树，比较基线 `5173c807c87b`。以下列出 libs/plugins 非 tests/benchmarks 中 `endAndTake(` 的直接调用及已迁移的原入口；这是文本核对，不能替代生成调用图、虚调用/模板/回调审查，尤其不能据此删除兼容 API。

## 共同迁移约束

`tryEndAndTake` 失败会保留事务，不代表 caller 已能处理失败。迁移必须同时回答：原 transaction 谁持有、parent 是否已经拥有子命令、拒绝时谁继续取消/重试、何时允许登记 undo 或释放临时内容。局部栈对象在返回后析构仍可能走 purge；仅写一个 `if (!tryEndAndTake(...)) return` 并不完成迁移。

区分“未发生工作”“提交成功”“执行失败”“取消待完成”；Failed 不得重放像素 callback。普通操作继续其原回退保证，只有错误链和取消进度闭合的 freehand 才启用整笔回退。辅助 interstroke、indirect merge 的多设备结果不能靠主设备的 bool 代替。

## 直接调用清单

原 28 个调用点分布于 20 个文件；当前 direct stroke 的一处已改为 tryEndAndTake，剩余 legacy 直接调用为 27 处 / 19 文件。保留原入口关系，每一行的全部位置都要复核；迁移证据与剩余出口见 92 §15。

| 代码位置 | 当前所有权 / 后继行为 | 必须联动的修改 |
|---|---|---|
| `libs/image/KisAnimAutoKey.cpp` [105](/Users/apple/krita_gpu/krita/libs/image/KisAnimAutoKey.cpp:105) | LoD blank-mode 临时事务，返回 auto-key 命令 | 先验证 clear 和终结；失败不得把空指针当作“本来无需 auto-key”，由初始化失败通道恢复并停止本笔。 |
| `libs/image/KisOverlayPaintDeviceWrapper.cpp` [343](/Users/apple/krita_gpu/krita/libs/image/KisOverlayPaintDeviceWrapper.cpp:343) | overlay 子事务与 grid 命令树 | 当前先释放 root，再逐个 endAndTake；改为先完整准备 grid/子事务终结，成功后才释放 root、清事务数组。辅助事务失败须向 interstroke 返回。 |
| `libs/image/kis_image.cc` [979](/Users/apple/krita_gpu/krita/libs/image/kis_image.cc:979) | 多设备 purge 事务，子命令已连到 finalCommand | 每个事务保留结果和 owner；全部成功前不交付 finalCommand；失败时不能解引用 cmd->hasParent，也不能丢掉其他未终结设备。 |
| `libs/image/kis_indirect_painting_support.cpp` [224](/Users/apple/krita_gpu/krita/libs/image/kis_indirect_painting_support.cpp:224) | 异步合并 sharedState，事务命令由 parent 保存 | 共享状态记录失败与终结结果；清临时资源和外层 parent 登记必须依赖成功，已开始的不可取消 merge 不得被普通 stroke cancel 截断。 |
| `libs/image/kis_painter.cc` [377](/Users/apple/krita_gpu/krita/libs/image/kis_painter.cc:381) | endAndTakeTransaction 二次包装，随后删除 owner | 新增/迁移带结果的 command transfer；拒绝时保留 d->transaction。联动 gradient 入口，不能只在包装层返回 null。 |
| `libs/image/processing/KisSelectionBasedProcessingHelper.cpp` [45](/Users/apple/krita_gpu/krita/libs/image/processing/KisSelectionBasedProcessingHelper.cpp:45) | KisTransactionBasedCommand::paint 返回事务命令 | 联动命令基类区分未执行、已成功、失败；失败不得在 redo 中再次调用 m_func，也不能释放未恢复事务。 |
| `libs/ui/actions/kis_selection_action_factories.cpp` [174](/Users/apple/krita_gpu/krita/libs/ui/actions/kis_selection_action_factories.cpp:174)、[431](/Users/apple/krita_gpu/krita/libs/ui/actions/kis_selection_action_factories.cpp:431)、[546](/Users/apple/krita_gpu/krita/libs/ui/actions/kis_selection_action_factories.cpp:546) | SelectAll、ClearSelection、RasterizeSelection 三类 paint | 逐项传播处理与终结结果；保留 rasterize/flatten 的选择恢复语义，不能把 null 当作 no-op 或允许 redo 重放。 |
| `libs/ui/kis_node_manager.cpp` [1451](/Users/apple/krita_gpu/krita/libs/ui/kis_node_manager.cpp:1451) | alpha 写回后登记 extra command，随后删 node、结束宏 | 终结失败必须停止 removeNode/endMacro 的成功路径；先收口像素写与所属宏的恢复责任。 |
| `libs/ui/operations/kis_filter_selection_operation.cpp` [40](/Users/apple/krita_gpu/krita/libs/ui/operations/kis_filter_selection_operation.cpp:40) | 选区 filter 返回 savedCommand，可能继续 deselect | 失败不继续空选区判断和 deselect 命令组装；保留原选择及终结 owner，联动命令基类结果。 |
| `libs/ui/tool/kis_selection_tool_helper.cpp` [134](/Users/apple/krita_gpu/krita/libs/ui/tool/kis_selection_tool_helper.cpp:134)、[200](/Users/apple/krita_gpu/krita/libs/ui/tool/kis_selection_tool_helper.cpp:200) | 选区组合与清除两个 paint，成功后释放 selection | 成功前不清 m_selection；终结拒绝恢复 outline/projection/flatten，命令基类不能重复 paint。 |
| `libs/ui/tool/kis_tool_utils.cpp` [249](/Users/apple/krita_gpu/krita/libs/ui/tool/kis_tool_utils.cpp:249) | 清内容后向 composite 添命令并释放 parent | 成功后才能向外转移完整 composite；失败不能仅省略像素命令而释放部分成功的树。 |
| `libs/ui/tool/strokes/kis_filter_stroke_strategy.cpp` [279](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_filter_stroke_strategy.cpp:279)、[291](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_filter_stroke_strategy.cpp:291) | 临时 filterDevice 终结与目标复制终结两个阶段 | 第一阶段失败不继续目标复制；第二阶段失败不登记命令或报告完成。跨 job 的 shared owner 必须保留，拒绝后不 reset 临时事务。 |
| `libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp` [467](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:468) | direct 改为 tryEndAndTake，成功后移交 auto-key/像素命令 | 拒绝后由 stroke queue 保活并取消，tryRevert 成功后才释放 owner。继续接入像素 callback failure sink；此入口的迁移不覆盖 indirect merge 与辅助 interstroke 的旧终结。 |
| `libs/ui/tool/strokes/move_stroke_strategy.cpp` [168](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/move_stroke_strategy.cpp:168) | 取命令后立即 redo，再加入 composite | 失败不得 redo 空/未完成命令；move session 保留 transaction 和 offset 恢复责任，接通 finishMove 的结果。 |
| `plugins/dockers/animation/KisAnimUtils.cpp` [81](/Users/apple/krita_gpu/krita/plugins/dockers/animation/KisAnimUtils.cpp:81) | 清当前帧，事务构造时已挂 parent | 成功终结后才能置 success=true、交付命令树；失败保留 frame/parent 的唯一恢复责任，不能只忽略返回值。 |
| `plugins/paintops/colorsmudge/KisColorSmudgeInterstrokeData.cpp` [46](/Users/apple/krita_gpu/krita/plugins/paintops/colorsmudge/KisColorSmudgeInterstrokeData.cpp:46) | heightmap 与 overlay 两组辅助事务由 parent 保存 | 两组终结均成功才释放 parent；重试不得重复 end/redo。主设备取消与辅助失败必须统一收口，不能由 void end 掩盖。 |
| `plugins/tools/basictools/strokes/move_selection_stroke_strategy.cpp` [75](/Users/apple/krita_gpu/krita/plugins/tools/basictools/strokes/move_selection_stroke_strategy.cpp:75) | cut 后登记命令，随后安装 indirect temporary target | cut 成功是 temporary target 安装的前置；拒绝时保留原层与选区回退责任，不能继续进入移动阶段。 |
| `plugins/tools/tool_smart_patch/kis_tool_smart_patch.cpp` [49](/Users/apple/krita_gpu/krita/plugins/tools/tool_smart_patch/kis_tool_smart_patch.cpp:49) | patchImage 后由 paint 返回命令 | 把 patch 和终结失败传给命令/作业结果；禁止因为 null 而再次执行 patchImage。 |
| `plugins/tools/tool_transform2/strokes/inplace_transform_stroke_strategy.cpp` [201](/Users/apple/krita_gpu/krita/plugins/tools/tool_transform2/strokes/inplace_transform_stroke_strategy.cpp:201)、[833](/Users/apple/krita_gpu/krita/plugins/tools/tool_transform2/strokes/inplace_transform_stroke_strategy.cpp:833)、[944](/Users/apple/krita_gpu/krita/plugins/tools/tool_transform2/strokes/inplace_transform_stroke_strategy.cpp:944) | 选区变换、设备 transform/merge、清除三个入口 | 三处同时迁移 executeAndAddCommand/runAndSaveCommand 的结果；保持命令组、dirty 与取消顺序，不把失败组保存为成功 transform。 |
| `plugins/tools/tool_transform2/strokes/transform_stroke_strategy.cpp` [313](/Users/apple/krita_gpu/krita/plugins/tools/tool_transform2/strokes/transform_stroke_strategy.cpp:313)、[370](/Users/apple/krita_gpu/krita/plugins/tools/tool_transform2/strokes/transform_stroke_strategy.cpp:370)、[429](/Users/apple/krita_gpu/krita/plugins/tools/tool_transform2/strokes/transform_stroke_strategy.cpp:429) | 设备变换、选区变换、clearSelection 三个入口 | 各自先终结成功，再向既有 undo strategy 提交；失败进入本操作取消，避免后续变换与 updateData 继续宣告完成。 |

## 必须沿包装继续追踪

- [KisTransactionBasedCommand::redo](/Users/apple/krita_gpu/krita/libs/image/commands_new/kis_transaction_based_command.cpp:19) 在没有 transactionData 时再次调用 paint。失败返回 null 与尚未执行混在一起；必须先增加明确结果/失败状态，再迁移 selection、smart-patch 等返回命令的入口，避免重复绘画。
- [gradient 包装调用](/Users/apple/krita_gpu/krita/plugins/tools/basictools/kis_tool_gradient.cc:187) 经过 Painter 的 endAndTakeTransaction；与 Painter 的结果接口一起修改，不能只检索 endAndTake。
- [indirect finish barrier](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:446) 还会 redo/addCommand 外层 parent；底层 merge 的终结结果必须抵达这里。non-cancellable 是调度承诺，不代表合并一定成功。
- [取消回调](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp:488) 使用 tryRevert，拒绝后保留 owner 并请求 scheduler 重试；恢复 frame 内容后再撤销 auto-key。其他调用者不能继续忽略 void revert 的结果，也不能把此处的 continuation 当成全应用取消责任已迁走。

验证按关系选用：拒绝后 undo 栈不增长；原 owner 仍可重试；parent 子命令没有提前执行、泄漏或双删；callback 计数不因 redo 增加；多设备第二个终结失败不丢第一个和其余设备的恢复责任；frame/auto-key、selection/outline、interstroke、indirect 非取消阶段均保持正确时序。具体测试与证据身份仍按 V01 记录，不以本清单的文件数作为完成标准。
