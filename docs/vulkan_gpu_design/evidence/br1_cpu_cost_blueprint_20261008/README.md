# CPU成本蓝图修订：推导记录

本包只复算[前包冻结报告](../br1_upstream_cost_accounting_20261007/README.md)，服务[03d理想路径与预测](../../br1_modification_guide/03d_cpu_cost_calibrated_blueprint.md)和[92 §16.147](../../92_br1_m6_m8_execution_baseline.md#cpu-cost-calibrated-blueprint)。产品`fb57b8b69be74a38602fb2f0cd1c6e4374b843e3`未修改，外层父`732dfee416bd5fbc203c3f1a80a710763b1ede47`。没有新benchmark、产品测试或统计置信区间。

[model.py](model.py)读取前包summary、fill-summary、CPU差额账，核对两次v2的208/116/92及upstream116、互斥actor差额之和和固定fill批身份。输入JSON、报告/协议、两份实际汇编均记录SHA256；不修改前包冻结材料。[model.json](model.json)保存可复算结果：

- seed+倍增13次请求的各次大小、总初始化字节保持；116页请求475136→1508，删473628（99.6826%）。这是数量算术，不是新的生产或像素测试。
- 原fill全部端点、负控制、一例内部工作量差异与事后敏感性一并引用；不改写主估计、不把CI当未来预测区间。
- 2.028102倍原配对比值的量级换算约50.69%，以及整数2倍起点的假设敏感度；不跨批拼接候选/upstream实测比值，不调整性能门。
- 结构方案合法删量、匹配价格、新增维护、与fill的重叠/交互及wall收益均为`null`，明确尚未证明，而非零或保证收益。

复算命令（从仓库根目录执行）：

```sh
python3 docs/vulkan_gpu_design/evidence/br1_cpu_cost_blueprint_20261008/model.py --check
```

初次派生使用`model.py > model.json`；之后`--check`只读校验。设计文档、输入引用和Git差异另作本轮审阅；这类文档检查不增加M6、安全或性能通过数。生产实验仍须完成undo解释、格式/边界/原控制，并按03d有限协议单独冻结身份与结果。

本轮`model.py --check`、30处新增/修改的本地链接与显式锚点、`git diff --check`均通过；未读取archive。另核定产品tracked工作树干净且Git tree等同`2f22452e2d`，前包冻结证据无差异。外层已有`krita` gitlink变动不纳入本轮文档提交。
