# 操作级管线完整替代：实施与验证记录

2026-10-12。目标及删除闭包以唯一蓝图§19.15为准，状态仍写回§13原33项。本文件记录本轮身份、实验规则和实际偏差，不另建实施矩阵。

起点：产品11c6895ddfeae074df727c76dcbf9e12988479ee，文档febcdb4e1。开始编辑前产品tracked clean，外层既有krita gitlink差异保留。首个产物为完整候选，不改变默认关闭和M6/M7/M8资格。原scope/CPU/指令基线与失败样本不修改。

实施闭包：原版本事实及内部证明 → 原operation接受 → H1逻辑直接退出和收费容量循环 → 合格H0直接canonical → 所有受影响消费者和退出迁移。技术分批不领取整包收益。与版本事实相关的generic多次签发证明仍有独立consumer，不能把内部CPU单次凭证模型强加给公开能力；真实多凭证与内部冗余注册分别裁决。

顺序：先构建及针对原合同的安全/预算/安装测试，再单独机制计数，最后不含内部热scope的同义净价。构建和性能采样不并行。保留每写即时读取、历史、四寿命和drain；不以内部次数相同为约束。实际文件、命令、源/库哈希、退出及全部失败记录于resident-operation-r1。原库在重建前保存；测试通过只授对应合同，不授性能资格。

实施开始时只冻结实施与安全检查顺序；后续在首个数量/价格过程之前补冻下方有限实验规则。完整候选通过安全/资源、实际删量核对后才能净定价；最终独立八块确认沿原门。既定指令15%工程门、CPU净省95%下界0.75ms和前台增费限制保持，失败不加样追门。增量未合格的候选不得默认为已验收生产版本，当前执行结果见RESIDENT_OPERATION_RESULT.md。

数量预测保持原表：H1无持续holder的physical1088→192、旧Prepared进入Historical960→0、CPU独立proof和非默认descriptor节点各1088→0；必要generation1088不变。H0过渡overlay68是路径推导，真实canonical68不变。新增arena实际块容量、字段、动态重验、备用保留/压力、失败和末端释放必须记净账。

## 有限测量预注册（首个数量/价格过程之前）

使用`build_resident_operation_validation.py`生成相同公共fixture：原8格，加原14入口×4BPP、K16/H1/W2、首结果full clone、首结果native单页读者、重复partial和no-op，共69格。所有格保留4寿命、即时读取、必要undo/redo和最后drain。original使用已保存11c689库；candidate使用本次完整普通构建；upstream仍为固定9a24ae0d8c构建。每批固化dirty diff、源码/二进制/库、实际dyld依赖及末尾复验，不能用HEAD代替候选。

依次执行：双架构安全与实际install allocator → arm64隔离数量库13格（原8＋新5，所有计时弃用）→ 三方各一轮69格能力与结果签名（时间弃用）→ arm64有限探索4个顺序块。每块三方轮转后反向，共6过程，奇偶块反转用例顺序；块内同方两个过程取均值作为一个独立观测。process CPU含后台和drain，foreground、wall及指令独立报告，不把它们相加。量库只在派生对象插入原子事件计数，绝不拿它定价。

探索后仅当H1指令点估计至少省15%、process CPU至少省0.75ms、foreground增费不大于0.75ms，且原13格其他控制无超过2%的指令点估计回退，才进入新批独立8块确认。否则保留完整负结果并停止本包扩样，不追加节点微调追门。确认采用同一轮转/反向顺序，seed12345，10000次块级配对bootstrap；H1单侧95%指令/CPU节省下界分别需达到15%/0.75ms，foreground增费上界≤0.75ms。控制单列CPU/指令95%区间与2%非劣性，不用H1收益抵消；控制未辨明时不授整包资格。探索和确认均不是正式M6校准。

每过程180秒硬限，timeout必须kill/reap；崩溃、像素/顺序/加载身份/端点检查失败全部保存并停批。当前与original同格结果签名必须相同；upstream差异逐项展示并沿原合同裁决，不能静默排除。性能运行时无构建、结构生成、另一基准或分析器竞争。未修改源码不得因结果差加样；安全缺陷修复后另立身份/批次，旧失败不删。这里冻结的是有限实验判据，不是预测收益。

首轮能力批修订（任何净价样本之前）：case66直接持有目标manager同一tile的read指针再写同页，不能作为upstream同义不可变快照前提；该用例只保留PageStore能力结果。新case66明确先由公共bitBlt建立一页不可变副本，再持续持有其read lock并覆写原manager，三方承担相同新增快照工作。validation-r5、quantity-r2、capability-r2绑定这个修订；探索块数/顺序/门槛不变。原case52–55为bad-tail导入，前66个已完成upstream结果与11c689存在同样的部分写入差异，candidate与original的69格完全相同；这些仅核验保持原语义，不作为同义净价端点。净价仍只含原8＋新5格。

2026-10-12恢复诊断补正：原case66日志已有断言失败，进程栈为`fixture.cpp:76 → abort → pthread_kill`；原先“upstream读写锁等待”的解释撤回。退出阻塞及timeout/reap失败保留。定向清理后进程仍残留，有限净价规则和环境前置条件均不放宽，详见[恢复证据](resident-operation-r1/environment-recovery-r1/README.md)。

## 原业务控制计价（业务首过程之前冻结）

宿主重启后已完成修订能力3过程、探索24过程及独立确认48过程；H1主门通过，5个CPU控制尚未辨明，不补存储样本。继续原先要求的业务控制是另一已保护端点，不能用于抵消这些缺口。沿原cost-ledger-business-r0的同一cost_fixture/matched_freehand_baseline/stage_probe、8段/4callback/19 projection、像素/undo/redo及销毁断言。original固定该批11c689的plain-current库和对应ABI夹具；candidate从02bcc普通构建仅替换同一取消clear融合的merger对象，按当前头重编同一夹具；upstream固定9a24ae。三方相同clear→composite拆分，所有派生源码/对象/库及实际加载依赖冻结，产品代码和原库不改。

ARM64，三方各1次能力后独立8块×6过程，共51过程。沿原六排列轮转加镜像，seed12345、QT offscreen及原plugin路径，120秒硬限，失败保存并停止，kill/reap失败如实记录。没有构建/其他基准/分析器竞争。三方前后身份、共享依赖及无内部observer输出检查沿原控制；能力时间弃用。

沿业务原统计：每侧块内两过程均值，8块配对中位数，100000次seed20261011 bootstrap，逐端点双侧95%区间，不授联合family资格。完整报告Setup/Stroke/Undo/Redo/Teardown的CPU/wall、阶段总和及含启动/退出的整进程CPU；同时给均值可加账但不与中位数混加。Stroke CPU节省下界>0才支持局部业务收益，其余四阶段CPU及整进程CPU的节省率区间下界≥−2%才关闭对应非劣性；区间跨界保留未知、不加样。业务对upstream仍保留原源码审计混杂，不替代存储的同义基础价格；不预报业务收益点值，不授M6/资源资格。
