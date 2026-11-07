# 当前/upstream CPU差额对账事前协议

2026-10-09，产品704d96e81cf29d16191bc3db8785859d79775e27/tree4e7fc164db46c02b968fdd04400b9e4402e289d0，upstream9a24ae0d8c070884fb013594191002e1a1b39a19，外层父a5004b3836c4b08fb76b9adcc1a00f3a0127ad4f。仅外部派生观察库，不改产品、fixture语义或门禁。目标是补上§16.156未覆盖8–9ms中的正常与额外CPU，检验冷准备/发布的优先级；不以对账代替可删除量证明。

## 边界和方法

复用br1_upstream_cost_accounting_20261007冻结ARM64 fixture/stage observer，普通RGBA8 512、8 segments、4更新callback、4workers，projection-ready终点及原undo/redo/销毁检查。同依赖两边分别按实际原compile/link命令构建。原库current SHA256为9f138c80f6b9c66223f3411684069f3a082f6a39d5ed58d7bd2c4c0cf92daed6，upstream为a288ac214124c80c4d3961112c3b4ca8c13ee922e8208a63b204dd597f441908。运行记录实际加载库与共享依赖哈希。

四种配置：original原库；off派生库但BR1_COST_MODE=0；jobs模式1，两侧仅包围实际job循环（stroke/merge/spontaneous，含原run、setDone、usefulWork、jobFinished，退出在解锁后）；detail模式2，在相同jobs上，双方加startMerge，current加cold、seal、commit、capture、operation及其pixel callback（未逐像素加钟）。cold与seal/commit等按事件祖先拆互斥，callback内cold仍单列，不能把整callback叫纯kernel。两侧jobs边界相同，内部PageStore责任只代表current，不造upstream同名函数。

固定观察器沿用原32banks×8192events、每线程栈及thread CPU，不提高预算或移用资源资格。off与original用于观察编译布局/关闭分支影响；jobs与off比较观察扰动；detail与jobs比较内部边界扰动。不同模式的差额只能交叉检查稳定性，不能机械按比例扣钟，也不能把某模式的子项拼到另一模式总量。

## 有限批次与停止规则

先完成observer关闭/嵌套/异常自检；各配置各侧1个能力过程，共8个，不进主统计。能力全通过后，主批4个块，每块四配置各一个ABBA：current/upstream/upstream/current，共64过程、每配置8配对。配置按块循环移位，以减少固定先后漂移；样本数不按结果追加。记录stage CPU/user/system/wall、所有job/子事件、像素、内部update数量、退出/timeout/reap和runtime。运行时不与构建、其它基准或CPU分析竞争。

本协议实际总过程为8能力+64主批=72；仅这两个有限批次。每过程timeout120s，timeout后kill并reap；语义、加载、阶段/观察失败则停止并保留全部证据。源码/观察修复需新目录和修订协议，不覆盖旧样本。实际内部update/job数量变化全部保存，像素等语义通过者不因慢或数量波动删除；差异足以影响归因时明确限制结论。

主结果为描述性同批均值差、配对差中位数、逐块/过程范围和数量；只有4独立块，不授新的正式CI/性能资格。各过程先完成exclusive账，再取均值，差额可相加；中位数不能相加。核验self+children=inclusive、同线程父子、stage边界、无overflow/活跃尾。跨stage事件若存在，保留并标明不可分配，不强行截取CPU。

对账输出：process CPU = job_stroke + job_merge + job_spontaneous + 非job已观察根 + 未覆盖；detail再将job内部拆为原生命周期、callback余项、read/merge及job余项。与上轮相同观察集合建立覆盖桥接，说明8–9ms中新增job边界覆盖了哪些区间；不是使用旧source时间相减。

主要差额已落到明确责任且未覆盖额外不足以改变实施优先级即停止。若还有可改变排序的大额差异，只允许先依据本批结果另行冻结一次具体、最小的判别追加；不得为每个未知函数扩大矩阵或用更多样本取得门禁。产品/安全大矩阵不重跑，M6原缺项保持。
