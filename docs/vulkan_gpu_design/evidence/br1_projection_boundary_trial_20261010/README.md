# 投影清零与首层合成：中层边界试行结果

后继已完成[8198c36ed7生产实现及独立验证](../br1_projection_boundary_production_20261010/README.md)，[原B01–B11矩阵](BOUNDARY_PLAN.md)已原位结算。下文保持此前受限原型的冻结结论，不代表当前生产状态。

本轮按更新后的 `algorithm-cost-optimization` 选择工作拆分边界，完成两版派生库原型和独立确认。**本 fixture 的独立 clear 生命周期确实制造了可删除工作；r1 Stroke CPU 节省 1.05775ms，95% pointwise 区间 [0.716, 1.5455]ms，块相对收益中位 6.6419%。** 这是一例中层因果删量及受限原型净收益的正向证据，尚不是生产合法性、可靠候选排名或精确收益预测的完整闭环。

当前 authority 见 [92 §16.168](../../92_br1_m6_m8_execution_baseline.md#projection-boundary-selection-trial)。文档父 e8fb76960；产品 c13c44249338bf10477b9b07c65726e5933e51f9，tree 05182f0ad631460934e4298e8c71cf5cc0f36c2d，四个生产 TU 与 d182a34bd0 相同。**产品生产/测试改动均为 0**；实验库不覆盖 build/bin 原库，不授 M6/M7/M8 资格，persistent 默认关闭。安装技能保持 cad39cc5，本批没有再修改技能正文。

## 1. 为何选择这一层

原路径在同一个 merge 内先 `parentOriginal->clear(rect)`，再由 projection plane 调用 painter 合成；每个独立操作分别进行范围准备、版本保护、像素执行、seal 和 adapter 交付。每次调用内部合理，不证明上层必须产生两次完整生命周期。

竞争解释已在构建前的 [PROTOCOL](PROTOCOL.md) 登记：P1 所有独立 clear 都有必要中间消费者；P2 简单、独立源首层可在同一次 pixel operation 内初始化后执行原合成；P3 融合扩大准备集合、增加初始化或稀疏资源，抵消收益。选择 P2 的有限判别，不沿已经排除的 descriptor 后备搜索继续改造。复杂层、mask/style、依赖下层、临时 projection 和不兼容 painter 路由保留原 clear 先行；这只能覆盖已有路由，不能证明所有并发读者均不需要原 cut。

受限理想路径是：由原 merge owner 判断没有必要中间消费者，确定旧目标实际清除域与真实 paint 域的并集，**一次完整准备，在原 cursor 上初始化清除域，再执行原 over kernel，统一完成和交付**。不能直接把 over 改为 raw copy：透明像素的隐藏 RGB、opacity/channel 等仍由原 kernel 决定。公共 clear 保持原合同；本轮没有移动原 scheduler 的 job/cancel/finish 责任。

## 2. 实际删量与预测

下表计数只覆盖 merge 内部，来自独立计数过程；未插桩时间批次不使用这些计数。`accepted_cold_plans` 是成功 `prepareWriteBaseLocked` 的调用数，**不是唯一版本节点或最终页数**。seal 按实际成功结果计数，不把尝试当成功。

| 量 / 阶段 | control | r0 | r1 | 裁决 |
|---|---:|---:|---:|---|
| Stroke merge / pixel operation | 19 / 19 | 19 / 19 | 19 / 19 | 本次未减少 job 或合成工作；19 通知是观测结果，不是强制同义合同 |
| Stroke 独立 fill | 13 | 0 | 0 | 删除 13 次独立清除生命周期 |
| Stroke 成功冷准备 | 132 | 96 | 96 | 同 merge 删除 36 次，r1 预测兑现 |
| Stroke 新 batch / 成功 seal | 32 / 32 | 19 / 19 | 19 / 19 | 各删除 13 次，r1 预测兑现 |
| Stroke 成功融合 / 初始化字节 | 0 / 0 | 19 / 831360 | 13 / 566464 | r1 排除 6 次空 clear；字节是 callback 实际 memset 量，不是复制/容量/驻留 |
| Undo 独立 fill / batch / seal | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 | 无首层合成，原清除保留；r1 defer 后 flush 一次 |
| Redo 冷准备 / batch / seal | 56 / 1 / 1 | 56 / 1 / 1 | 56 / 1 / 1 | 没有可删生命周期 |
| Redo 成功融合 / 初始化字节 | 0 / 0 | 1 / 917504 | 0 / 0 | r0 新增无收益初始化；r1 预测归零并兑现 |

全部计数过程 failed fusion 为 0；r1 deferred = flushed + fused，两个 fusion 过程计数一致。实际 commit 次数随交付调度变化，control Stroke 11–14、r1 7；没有冻结确定 commit 删量，不能把这一差值当作固定算法收益。

计数证明 36 次重复准备来自本边界在该 fixture 的展开。它们与独立 batch、seal、extent/adapter 维护和尾释放一同改变，不能把净 1.058ms 全部授予 cold 单价，也不能用 27.3% 准备删量推导 27.3% 时间收益。旧 36 链约 0.48ms 只是另一冻结报告的毛成本参考，本次没有单项消融，不能倒推出每次准备价格。

## 3. 两版实验和独立确认

首版固定五能力过程通过后，原 merger 测试在 control 配置 SIGSEGV；换回原库同样失败。LLDB 指向测试取得不存在的 blur filter 后解引用：该 fixture 插件目录只有画笔所需插件。按事前 [SUPPLEMENT](SUPPLEMENT.md) 保留原失败、原库复现与回溯，仅给语义测试使用当前构建完整插件链接目录及 166 个目标 hash；匹配性能仍使用原插件目录。不是删除失败样本或修复产品以隐藏回归。

r0 修正测试前置后，四探索块 Stroke CPU 收益中位 1.50925ms，但 Redo 一致回退 0.2095–0.230ms，中位 0.2135ms。零删量分支却新增 917504B 初始化，是清晰的算法新增工作；本轮未消融定价其精确因果份额。保留 r0，不进入生产；在 r1 构建前另冻 [R1_PREDICTION](R1_PREDICTION.md)：清除域裁剪到旧 extent，空域沿原路径，预测 Stroke 1–2ms、δ=0.5ms、Redo 初始化为零。

r1 四能力过程和现有 merger/projection 各 control/fusion 测试通过后，按固定 16 个 ABBA/BAAB 块运行 **64 个独立未计数进程**。每块两次 control 与两次 fusion，均值差后取 16 块中位；bootstrap 50000，seed 20261010。全部慢值保留，包括一个 CPU 收益 7.642ms 的块；没有删尾、换端点或追加样本。

| r1 端点，control − fusion，正值为节省 | 块差中位 ms | pointwise 95% 区间 ms | 解释 |
|---|---:|---:|---|
| **Stroke process CPU（主）** | **1.05775** | **[0.716, 1.5455]** | 16/16 块方向改善；点≥δ 且下界>0，受限原型价值筛选通过 |
| Stroke wall | 0.4895 | [0.2615, 0.6475] | projection-ready，非真实 canvas-visible 或输入延迟资格 |
| Undo CPU | −0.01175 | [−0.034, 0.004] | 不能确认无回退 |
| Undo wall | −0.00925 | [−0.0365, −0.00225] | 有小幅回退信号，原 clear 仍存在；没有据此断言具体新增检查的价格 |
| Redo CPU | 0.0015 | [−0.019, 0.01225] | r0 的一致大回退不再出现；不是严格零成本证明 |
| Redo wall | 0.00275 | [−0.01625, 0.0175] | 未授正式非劣资格 |
| Teardown CPU | −0.00725 | [−0.0255, 0.0125] | 原型退出语义通过，时间非劣未知 |
| Teardown wall | −0.008 | [−0.0195, 0.0125] | 同上 |
| Setup CPU | 0.66225 | [−0.65625, 4.618] | 未删除目标工作，不领取收益 |

control / fusion 的 Stroke 块均值边际中位为 16.0835 / 15.0245ms；它们之差及其比值不是配对估计量。6.6419% 是逐块相对收益的中位。其它区间均为描述性 pointwise，没有 family 修正、非劣界或正式 M6 门；不能把测试通过和这些区间合称“原控制全面通过”。

本包成功批次合计 **97 进程、327 QTest passed**，另完整保留初始 control 与原库两个 SIGSEGV 过程、一次 LLDB 诊断；两次准备脚本文本匹配失败发生在编译/业务过程前，同样保留。r0 探索不进入 r1 确认统计。所有成功进程像素/Undo/Redo、8 segment / 4 显式 callback、更新输出和 image/strategy 销毁通过。现有复杂层测试不能替代下节缺证。

## 4. 技能效果和进入产品前的限制

本次支持：更新后的选择层可以从“每次准备怎样便宜”转到“为何要有两个准备生命周期”，找到一项有可测净收益的中层边界；分支净账暴露 r0 的 Redo 无删量新增工作，事前修订后独立验证数量和价值。**仍不支持**：该项是剩余榜首/前列、可靠命中率、精确预测校准、整条前台算法充分优化、调度无多余等待。r1 点在 1–2ms 宽范围内不证明预测准确；与 r0 探索点相差约 0.45ms，同时算法和独立样本改变，不能归因为裁剪退化。没有新 upstream 同义对照，不能扣除旧 7–9ms 差额或改变 handoff 性能门。

原型 TLS/强引用和类型路由只用于有界因果实验，不是生产接口或参与容量资格。公开 current/exact 并发观察点、拒绝时原 clear 副作用、稀疏/default presence、实际峰值/预算/尾释放、取消和嵌套调用尚缺直接证据。源码还暴露具体失败风险：外部 job failure context 活跃时，融合失败先 `reportFailure`，之后 deferred clear 可被 `currentJobHasFailed()` 阻断；原分拆 clear 则可能早已成功。**这是静态反例条件，未动态复现**，不能凭成功像素豁免。

条件方案及唯一有限索引/追踪见 [BOUNDARY_PLAN](BOUNDARY_PLAN.md)。下一优先先证实/排除必要中间 cut 与上述失败副作用，再决定明确由原 merge/painter 传递初始化语义的完整生产替代；本包停止性能扩样。若必要 cut 无法省，保留原边界；若资源/失败代价吞掉收益，撤回产品准入。当前仅“受限原型价值通过”，不称完整生产优化完成。

## 5. 复现与冻结

[summary.json](summary.json) 是计数、完整阶段块差、区间和预测对照；[verification.json](verification.json) 核对产品/构建/实际库/依赖/插件/过程；[EVIDENCE.json](EVIDENCE.json) 绑定全部原始文件及两版原型。首版复核器过度要求不同测试依赖相同，已[保存并修订分组](VERIFICATION_CORRECTION.md)，未改样本。workspace 输入/实际库有前后hash；外部实体库仅有相同加载路径和事后hash补证，系统shared-cache文件未hash，不能声称全依赖均已前后核验。原库 SHA256 `ba5876d6b155e84f27087577d50243c6913cb4a62236634699b3a2d57b12e612`；r1 派生库 `38262431edb71d7caf8961c8a0da497febbe1f536b742ae770c210314230c3a0`。相同派生库以 env 选择 control/fusion；两臂都含实验公共开销，不能将此收益数值直接保证给未来移除 TLS 的生产实现。

```sh
# 原始矩阵、派生 TU/对象/库、失败记录均在包内；原对象/依赖按 manifest 引用。
tar -xf docs/vulkan_gpu_design/evidence/br1_projection_boundary_trial_20261010/raw.tar.xz -C docs/vulkan_gpu_design/evidence/br1_projection_boundary_trial_20261010
python3 docs/vulkan_gpu_design/evidence/br1_projection_boundary_trial_20261010/analyze.py
python3 docs/vulkan_gpu_design/evidence/br1_projection_boundary_trial_20261010/verify.py
```

runner 的目录不可覆盖规则防止重写冻结样本；重跑实验须另建证据包，不能覆盖本目录。重建需要 manifest 绑定的原构建对象及依赖，raw 包并非可跨机器独立构建的完整工程。
