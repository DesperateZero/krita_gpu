# BR1 累积 Git 审阅基线（2026-10-01）

用户选择“先建立累积基线，再逐轮提交”。产品仓库 `/Users/apple/krita_gpu/krita` 的累积提交为 **`9697196acab538329359a2d6c5bc45c2cf001a36`**，父提交为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`，原分支 `refactor/brush-s2-predefined-sanity` 保持不变。

范围是 [批准的131个产品文件](cumulative-code-baseline-paths.txt)：123个已跟踪改动与8个新增源码，包含此前多轮源码、测试、兼容构建及审计资料。暂存集合与文件清单严格相等，暂存diff检查通过；不是重新拆分历史，不把153283 added / 50639 removed的累积差异声称为上一轮工作量。许多行来自审计清单和调用图。没有收录构建目录、测试图片或其他未归属文件，没有push或改写历史。

外层 `/Users/apple/krita_gpu` 是独立文档仓库，原先的`krita`项已经是Gitlink。文档基线单独提交两个当前入口、36份活动修改指南及本证据目录，并把Gitlink更新到上述产品提交；文档commit的身份由Git日志和最终交付报告提供，避免提交内容对自身哈希产生循环引用。此前其他未跟踪证据与文档仍保留本地，不纳入本次基线，也不重新授予资格。

活动文档及结构化资料的暂存diff检查通过。原始`.log`与`.diff`逐字节保留：构建日志原有尾空格、unified diff的空白上下文会触发通用whitespace检查，不能为了清零告警改写原始证据；这些文件不参与文档格式检查，产品源码的暂存检查已经独立通过。

提交未改动实际源码字节或运行binary。提交后 [architecture-after-baseline-commit.log](architecture-after-baseline-commit.log)仍通过原21 manifest / 25 ownership / 16 census / 19上层侵入文件门；[提交与冻结身份绑定](git-baseline-identity.json)逐个比较32份源码commit blob与原SHA256，并验证12份运行binary/库身份未变。上一轮4580/0/0仅属于 [原目标范围](README.md)，不是131个文件的全功能验收；完整CP1及M6/M7/M8仍未关闭，默认关闭。

上一轮9个生产文件381 added / 176 removed的精确增量保留在 [source-incremental.diff](source-incremental.diff)。原测试没有完整轮次起点，不伪造逐轮测试diff；从本基线之后的轮次才有完整Git起点。

后续执行 [编辑与提交合同](../../br1_modification_guide/CONVERGENCE.md#round-edit-and-commit)：普通源码、测试、文档用显式patch；Python用于分析、运行和派生资料，必要机械迁移须附完整受影响清单及本轮diff。每个完成的实施包统一目标验证后作聚焦本地提交，报告code/doc commit、真实删除与欠项。已有存储/通知范围不重复领取，产品检查不因单纯提交或文档编辑重跑。
