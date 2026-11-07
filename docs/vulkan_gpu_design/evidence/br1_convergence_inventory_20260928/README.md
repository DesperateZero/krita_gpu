# BR1 收敛目标与文件清点证据

本轮将前次原则细化为[可领取目标和改动处置清单](../../br1_modification_guide/CONVERGENCE_CHECKLIST.md)，并清点当前产品未提交增量。没有修改生产源码、重新构建产品或运行新产品测试；没有把前次 smoke/矩阵扩大为新资格。

## 实际执行

- 再次读取引用任务状态，任务为 idle；以检出代码和 92 建立结论。
- 用前次只读收集器重新核对源码及 28 个构建/运行文件，身份仍匹配最后 JP1 批，见 [identity-review.json](identity-review.json)。
- 生成包含全部 124 个范围内文件、6 个未跟踪源码的 [文件清点](inventory.md)及 [机器记录](inventory.json)，逐项记录路径、增删量、分类、责任路由和文件 SHA-256。
- 定点读取 owner overload、backend 完成交付参数、native packed/cursor adapter、job failure bridge、普通 restore 全量 rebuild，以及真实 freehand fixture。形成明确的保留、修复接通、合并候选、条件删除与暂缓判断；没有声称全部 124 文件都完成逐行语义审查。

## 清点口径

[collect_inventory.py](collect_inventory.py)读取 `git diff HEAD -- libs plugins build-tools`，再纳入 libs/plugins 未跟踪 C/C++；排除构建目录、测试输出图片及范围外资料。它与前次 review 的分类总量对账，未知责任组或重复路径会失败，输出使用独占创建，不能覆盖冻结记录。

生产 C/C++ 为 90 文件、净增 7,809 行；测试文件为 25、净增 11,001 行；其他构建/检查文件 3、净增 19 行；生成审计与配套 manifest 6、净增 64,424 行。分类不是整个 BR1 相对 upstream 的 diff，也不是质量分数。责任分组互斥用于完整清点，真实跨项职责继续参考 CODE_INDEX。

复现时在新的同层证据目录使用相同脚本：先运行前次 `collect_review.py`，输出该目录的 `identity-review.json`，再运行生成器。当前目录的输出保持冻结。对后续已变更源码，应先更新清点基准，不绕过身份或总量差异复用旧结论。

## 深化后的主要裁决

先关闭 JP 的实际读取窗口，并准备 V01/BC10 真实业务对照；随后联合接通首条 direct 链。在首条链通过后、扩大模式前，重点审查 painter owner 参数族、backend 相互依赖的交付输出及重复 adapter 交付逻辑。合并要减少实际责任组合，不预先指定新框架。

当前 job 错误桥、legacy 分支和普通 restore 全量 rebuild 均有真实消费者；没有立即删除的生产项。删除候选已给出具体释放条件。原 freehand fixture 使用 `setBaseFuzziness(3)`，后续需另外用精确版本/字节断言证明发布语义，不能靠放宽图像容差通过。

默认启用仍要求完整资源/进度和真实对照；M6 → M7 → M8 及 39 不变。当前结果只代表目标/清点文档与身份审查完成。

## 对前轮测试模式判断的纠正

进一步核对 [StrokeTester::testOneStroke](/Users/apple/krita_gpu/krita/sdk/tests/stroke_testing_utils.cpp:191)：`indirectPainting` 只用于命名，调用 `doStroke` 时并未传入；实际模式由 preset/资源和原 strategy 决定。`benchmark()` 的旧注释写 indirect，但实际参数只决定取消、外部 layer、更新和是否取 QImage，不能据注释推定模式。前轮“已覆盖 direct/indirect 变体”“benchmark 默认 indirect”的语义解释不成立；smoke 的实际通过结果、关闭普通更新及缺少持久 owner 断言等事实不变。

本轮已更正活动 CONVERGENCE、V01 和 92，旧冻结审查记录保留并由此条勘误说明。首条验收固定参考配置并强制检查实际模式/target/owner，防止名称不同却运行同一分支的假覆盖。

## 校验

[check_inventory.py](check_inventory.py)核对全部 124 个文件 hash、完整产品差异身份、分类总数、两层 git diff 空白检查，并复用只读文档检查器验证新增和受影响文档的链接/锚点/行号范围。结果分别写入 `document-check.json` 与 `verification.json`，均拒绝覆盖；archive 链接跳过，不读取其中内容。这些检查不代表新的产品测试或阶段资格。
