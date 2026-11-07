# 未发布中间版本的回收判别（运行前冻结）

产品11c6895ddfeae074df727c76dcbf9e12988479ee不变。沿原33项T04.2/T07.2：比较原finishUnlocked与隔离派生原型，不增加产品owner/字段/队列。只处理已经成功安装替换、原Prepared proof已撤销的superseded版本。该版本从未进入canonical root；prepareMutation与installMutation两次确认isPreparedBy，owner gate内接受后不能再被同事务提交。capture/lease/pin/activeOperation/last-use仍由原discardHistory检查；预算/债务拒绝及未删除均回原requestKey/collector。普通已发布Historical完全保持原路径，H0不领取命中。

三个消费者分开：undo origin在root/retention中；上一成功operation在本次接受前保留；exact capture/alias/last-use须在接受后继续保活。原型只用已接受的Prepared来源证明免root扫描，不授予覆盖当前字节的权限，不跳M7，不改变Fresh或物理free数量。新请求在owner gate外不能以已撤销proof产生保护；已有保护须被原metadata拒绝。alias物理共享仍由provider/binding生命周期处理。

静态反例核对后，先跑原六类ARM64安全测试（CPU mutation含252条superseded reader/failure/terminal组合、reference、resident read、physical claim、tiled manager、lockless stack），保留失败。然后4个数量过程baseline/prototype/prototype/baseline，原8case、四manager寿命；原scope计时关闭。预期H1 K16/W16最多960个superseded候选；无外部读者且债务接受时全部可由原discardHistory删除。H0及W1为0；Fresh/rows/retire/free与上轮相同。实际命中不足先查原因，不随意改候选。

数量成立且无安全失败后，才领取**单批34个完全无热路径观察器的时间过程**：两侧各capability，8独立块，偶base/proto/proto/base、奇相反；case顺序随奇偶反转。派生plain库只替换Publication TU，双方同一空begin/end及显式drain接口，不链接scope/count/thread观察器。原write/read/finish/undo/redo/teardown端点保留，process/foreground额外drain尾单列。无构建/其他基准并跑；每过程120s timeout后kill/reap，身份、实际库/依赖、像素、undo/redo和全部8case顺序必须通过。无排除、无追加样本。

统计块内双过程均值，配对节省base−proto，8块中位数及100000次固定seed20261011的pointwise95% bootstrap；可加成本账用均值。主判别K16/W16/H1增广process CPU：值得推进的净收益δ=0.75ms（约旧同义额外成本的6.3%，亦要求比几十分之一毫秒清理更有价值）；独立确认需区间下界≥δ。H1前台及H0 process/foreground不容许超过0.75ms回退，区间下界须≥−0.75ms。该阈值是原型筛选精度，不替代产品2%控制或正式M6门。

没有事前净时间点预测：1.736ms history pass是扰动未过的描述性父桶，包含保留工作，不能填为可回收预算。数量有预测，净价未知，故只授权本判别实验，不预授权生产迁移。若命中成立而时间不足，报告调度/前后台搬移及替代检查成本，不把父桶或free差额改写成收益。无论通过与否，保留全部源/差分/命令/失败并回原矩阵；不重写第二张状态矩阵。

## r0审计纠错与r1（首次数量/时间运行前）

r0六组5233/0/0通过，但静态审查发现直接discardHistory可在effects或债务准备抛bad_alloc；原collectPassLocked接住它，原型遗漏。安全测试未命中此具体新caller，因此不授r0安全完备性。r0不运行数量/时间。r1补原caller相同catch，原身份和六组记录保留，新身份重跑六组后执行原固定数量/时间协议。另在正式时间前进行两个故障过程：只在直接调用内、discardHistory选出可删集合后、原prepared.reserve之前抛bad_alloc；catch后恢复标记，原collector可正常继续。断言全部业务结果、undo/redo及Fresh/retire/free守恒不变，superseded全部落入refused并由原流程释放。故障源独立，不进入性能库。
