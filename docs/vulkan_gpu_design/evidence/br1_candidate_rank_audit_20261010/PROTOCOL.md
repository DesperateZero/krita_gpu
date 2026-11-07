# 预测误差与候选排名审计：新问题、有限观测

用户要求核查实际/预测偏差，以及是否命中性能榜首/前列。当前产品c13c442493，只有测试相对d182a34bd0增加13行，生产源码相同；运行原库ba5876d6。上一空历史getter候选已回退，64过程确认和Fresh/H4批次保持冻结，不续采候选收益。

先复算原预测0.2–1.0ms、探索0.66025ms与独立0.4545ms及区间；逐块直接求Stroke+Undo+Redo+Teardown联合端点（事后描述性，不能用各阶段中位数相加），明确删除量和时间来自不同过程，不能反推节点单价。不将旧upstream差额与此次候选收益相减，也不报排名概率。

排名证据缺口：原21/185 Work free栈是释放事件频率，既非CPU份额又不含必要/可删分离。D1/D2已有同生产源码的前台责任粗价，但没有history自身同批价格。本包只新增**collectPassLocked完整pass和history job完整invoke**两个嵌套计时范围，复用原前台粗粒度scope作为同过程参照。关闭旧facts细时钟和所有metadata数量观察，不新增逐key/字段时钟。history job包括epoch/retirement等，pass是其子区间，不能相加。request/新Work/empty slice等用线程本地计数，不测每次请求的短时钟。

这只能建立当前责任价格与排名，不能直接建立相对upstream的独占差额排名或合法可删排名。history pass也不包含全部前台Work准入/队列控制；不把它伪装为候选严格上界。没有新算法替代，不在本包实施新的history优化。

配置：raw原产品；off同观察库关闭；coarse原前台责任计时mode2；history增加两完整history范围及计数mode3。ARM64原matched fixture，1个能力过程/配置；通过后固定4个Latin顺序块，每配置4过程，共16测量过程，合计20过程。顺序沿用raw/off/coarse/history平衡轮转。120秒超时kill/reap；保留所有慢值/失败、不删尾、不续采。像素、19projection updates、8segments/4callback、UndoRedo、真实销毁/实际加载库及依赖hash必须一致。全部构建先结束，无并发性能进程。

观察器沿用已自检的CPU/wall嵌套observer，检查所有父子独占账与跨阶段/overflow/活跃尾。新计数验证requests≥created、slices≥empty且实际empty>0。历史计时启用相对coarse：若Stroke CPU中位增加>0.25ms或投影CPU比>1.15，则新增价格仅为扰动条件下粗价；即便未触发，也只报告4过程描述性中位/范围，无新CI。raw/off/coarse的布局/总体观察差异全部列出，不统一扣clock费用。

结束产物：误差分项表、同批当前责任inclusive及exclusive榜、可删排名证据缺项、明确继续/降级决定，更新03k与92。只有收益选择缺口补齐才进入下一蓝图；不以新的粗价重复领取旧LP或getter候选，不改安装技能/M6资格。
