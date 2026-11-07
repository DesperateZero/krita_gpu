# 释放路径试行：高频重复查询没有足够净价，转查完整任务寿命

产品父d182a34bd0 / image da4304d4。本包不改产品、不实施free清理、不执行未准入的64过程确认。事前范围见[协议](PROTOCOL.md)，定价后裁决见[PREDICTION](PREDICTION.md)，唯一追加的调用者判别见[SUPPLEMENT](SUPPLEMENT.md)。这是候选筛选的排除案例；完整任务的后续工作另见[空历史任务试行](../br1_history_admission_trial_20261009/README.md)。

Darwin原free先取capacity，分支又重复malloc_size。可构造替代每个native free少1次查询，低对齐映射少2次，高对齐前缀少1次，仍按原容量返回并保留munmap/mach_vm_deallocate失败处理。真实Stroke两次能力过程native free为5930/6066，低对齐映射各1；调度不同，不能把136次差领取为删除。

隔离微测只计实际batch free：8种size/alignment × 8个平衡块 × 4位置 × 1024次free，共256行/262144次释放，返回capacity全部准确。native 64/512/4096/16384B中位单价仅5.626/4.526/5.197/4.791ns；65536和mmap含显著正反块，不能用极值外推。没有真实逐size分布，故只给**约0.02–0.04ms Stroke CPU条件量级**，不是统计区间。几千次并不自动形成值得改造的毫秒预算。

一次每32次free取栈的系统抽样记录320条，overflow0；Stroke185条中40条经过history collectSlice，21条包含Work map erase。初步手工归类写成26条，完整解符号复核更正为40条；后续事前协议中的26保留原文，以本处勘误为准。它只定位具体对象，不能将40/185当CPU占比或精确总体份额。新问题成为“无历史为何创建完整Work并由worker再删除”，而非继续优化每次free里的几ns。

分析器v0将Work erase字符串错匹配为erase(，所得0无效；现按实际libc++的__erase_unique模板符号匹配得到21。旧分析器/summary-v0保留，无补样。

验证为4个真实matched过程/12 QTest通过，加1个微测过程；所有matched像素、19updates、Undo/Redo、销毁、加载库和退出通过。原始值与复现分析在[summary.json](summary.json)、[analyze.py](analyze.py)，构建及采样原型未进入产品。后续产品重建不覆盖本包冻结原型与运行身份；旧build/bin身份以当时before/final记录和冻结父库核验。

技能反测：排除了“次数大所以收益大”的候选；尚不能仅凭正确排除证明正向预测能力。没有将业务目标缩到微基准，未继续扩样。
