# PageStore 同语义管线判别：事前协议

产品8198c36ed722030edae715b7423554036bf1bcf7；upstream9a24ae0d8c070884fb013594191002e1a1b39a19。只编译派生诊断库与共同夹具，不改产品或两侧原始对象。输入/实际链接对象/库/源码哈希冻结，ARM64，同依赖、同编译选项；运行与构建不并发。

本包先完成两层判别。第一层用双方完全相同的data manager公共操作，避开画笔任务分区、clear融合和像素kernel的通用优化，比较基础存储替代管线。第二层用已有真实freehand夹具，将当前clear融合恢复原拆分，保留PageStore必需的页分区、失败与可见性交接成本，检查业务差额。后者仍须披露其余未隔离差异，不能冒称纯后端成本。

## 共同操作矩阵

K=1/16个64×64、4BPP页；每个case四个独立manager寿命；先写入A并commit，再做1/16次整域覆写，交替B/C，每次立即readBytes核对当前可见结果。H=0无undo保留；H=1先getMemento，全部覆写后commit，再rollback核对A、rollforward核对最终值，purgeHistory并释放memento。最后销毁manager。8个case，顺序在每个配对块固定、奇偶块反转，避免行顺序一贯偏向一端。

相同源码、输入字节和API顺序；本矩阵不调用PageStore私有写捷径，不关闭预算/错误/读者保证。CPU/wall分别累计setup、write、current-read、history-finish、undo、redo、teardown，另记整个case，核验完整结果后才接纳。每次公共write之间可见，未声明一个跨全部write的原子操作；允许双方不同内部版本/COW/分配。四次寿命和case内循环不是独立统计样本。

该矩阵是同义公共存储能力的有限诊断，不替代复杂并发/晚exact reader、资源压力、实际canvas或正式M6。manager销毁和history释放计时，进程退出/reap也核对；全局pool/runtime及跨case后台尾另列，不将case差额宣称为全部最终物理free的精确独占账。

## 固定运行

1. capability：共同矩阵原库current/upstream各一次；派生unfused当前freehand一次；观察库current/upstream各一次共同矩阵、各一次freehand，共7进程。全部通过再进入后续。
2. storage：8个ABBA/BAAB交替块，每块current/upstream各两次，32进程。主端点为8行write CPU及全case CPU，read/history/teardown、wall分别报告。统计单位为顺序块，各侧块内均值之差；100000次固定seed bootstrap中位数pointwise95%区间，不作8端点联合门资格。
3. business：8个相同块，32进程；current使用只去除clear融合的派生库，upstream原库。相同旧fixture/seed/8segment/4显式callback/像素/销毁断言。仅更新该控制下的业务差额。
4. mechanism：共同矩阵和freehand各current/upstream/upstream/current，共8进程；观察库mode2，前者每case清空观察输出。跟踪当前冷准备、seal、capture、operation及upstream写锁/COW。事件父子账和作用域核验，计数定位，不把细粒度观察CPU当净收益价格。

总79进程，禁止追加到显著。每进程120秒，失败/超时kill及reap并保存后停止。语义错、错误库、观察溢出/作用域错误均不剔样补跑；如夹具有错误，保留失败并另冻修订。source audit、机制和未插桩计时分开；不得从旧6.390ms或1.204ms代数扣除来代替新对照。

## 竞争解释与停止

- 管理成本主要由前台任务/通用kernel差异制造：若没有这些差异的共同存储矩阵仍有显著额外成本，该解释不足。
- 额外成本只在首次COW：比较相同K下1与16次覆写，记录两侧真正COW/冷准备与history保留；禁止把调用次数自动当必要新版本数。
- 必要history是全部差距来源：H=0与H=1分开，已有before不可变与每次current可见保留；不能通过丢history加速。
- 费用只转移到生命周期尾：write与全case、teardown/退出分别核验；跨case全局尾未闭合时不授全生命周期净预算。

没有事前产品收益预测。先据有限对照确定差额来源和下一完整责任；若缺合法替代与净价，本包不以微改制造优化成果。P04/P05只有取得合同、实际命中与可回收净预算才能晋升。
