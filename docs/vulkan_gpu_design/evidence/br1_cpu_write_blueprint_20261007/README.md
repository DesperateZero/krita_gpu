# CPU写入算法蓝图与可复算模型

本轮落实[03c详细蓝图](../../br1_modification_guide/03c_cpu_write_execution_blueprint.md)和[92 §16.144](../../92_br1_m6_m8_execution_baseline.md#cpu-write-blueprint)。产品`2f22452e2dc76dca3e60c6231783534f44716ce4`，外层父`c21d9896b`；产品改动0、新产品测试/性能过程0、新正式通过0。M6/M7/M8仍0/3；以前4554/0/0及Fresh/H4 8/8保留原证据身份，不宣称本轮重跑。

确定的实现蓝图是在同一原CPU operation内：固定源的原kernel矩形稳定按页分组，目标范围规范化一次，consumer只读借用，保留原全冷页准备与交付/取消；按页处理完后归还guard，最多同时pin一页。B1–B12列出原caller、同批删除、失败、预算/进度及有限验收。当前暖复用已经实现，session27→1而代际不变不能证明它失效。新方案不预报代际、复制、初始化、completion ticket或operation/cut/commit下降。

## 本轮实际完成的核验

- 审阅当前暖/冷/必要cut、范围/guard、adapter、provider/ledger、完成区间及真正free路径；当前源码和原已有测试断言见蓝图与冻结源码。
- [model.py](model.py)对30组输入用独立逐像素顺序oracle检查稳定分组，要求原kernel矩形和每像素dab/clip序列同时保持。包含负坐标/offset、重叠clip、空输入、64边界及24组固定seed生成输入；反转同像素次序的负控制被检出。这不是实际Krita compositor、资源压力或运行性能测试。
- 同页100dab：body pin 1→1；四页100dab交错：400→4；16个稀疏页：16→16。详见[输入](model-inputs.json)、[输出](model-results.json)。低重用输入可能因计划成本变慢，不能删掉负控制。
- [completion模型](completion-model.json)核验N=1/2/16/76/132/256：串行准备全部成功且无retirement完成时，同source live interval为2N−1、分寿命source为N。两者均分配2N个节点，另多一个source。模型未证明真实replay驻留量或速度，拆分仅为独立条件候选。

## 预测与可证范围

对每个适用operation，R为原页访问连续段数、P为实际不同页数、C为冷preflight pin、E为必要让出：`Δpin对=Σ(R−P−E)`。现有node76代际/2420pin来自冻结projection包的机制结果；**只有真实trace另证ΣC=ΣP=76、所有相关pin适用且E=0**，才可预测2420→152、少2268对（93.72%）。原计数不包含该逐operation序列，不能直接授权此删量。

[prediction.json](prediction.json)给出36组价格/新增成本/关键路径敏感度，使用前CP0冻结边际stroke 8.103ms作为示例分母，非当前candidate时间。每对0.25µs、新计划0.1ms、关键路径系数1时为5.76%；每对0.5µs时为12.76%。这些参数未实测，结果不是置信区间、时间下界或收益承诺。管理采样差84.1%同样不能作为可删时间。

## 冻结与复算

[PLAN](PLAN.md)记录范围，[freeze.py](freeze.py)冻结当前源码、核对前包机制输入的原SHA、保存前包CP0/结构输出与身份；[manifest](raw-manifest.json)列出`raw-evidence.tar.xz`每个成员及SHA。[verification.json](verification.json)记录源码身份、归档核验、模型逐字节复算和文档链接检查。上游比较和历史性能沿各原包，不用本轮模型替代。

模型可直接运行：`python3 model.py`。核验冻结包：`python3 freeze.py --verify`；核验不改冻结身份，不要求工作树HEAD停留在文档父提交。需要查看源码时将`raw-evidence.tar.xz`解包到本目录即可；不要重新冻结覆盖原身份。所有源码以产品当前检出内容为准，本包没有读取项目archive。

下一实施前依03c §9固定四过程真实序列诊断，先裁决P/R/C/E与成本，再实施完整B1–B8并验证B11/B12。provider整体压平、减少checkpoint、默认persistent启用和跨clear/composite合并均未获本蓝图的正确性证明。
