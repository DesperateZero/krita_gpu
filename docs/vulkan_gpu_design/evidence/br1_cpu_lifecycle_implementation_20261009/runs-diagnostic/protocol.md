# CPU全生命周期优化：事前实施与验收协议

产品父704d96e81cf29d16191bc3db8785859d79775e27/tree4e7fc164db46c02b968fdd04400b9e4402e289d0，文档父e333942d99cff2785d99ad0b62d13b592138e1d7。按03h/03i/03j的LP01–LP10、28子项和12路径实施，保留原分支，候选分支codex/br1-cpu-lifecycle，不push。每个产品hunk归属LP；设计偏离先记录原因并同步原蓝图，条件项保留具体consumer，不删除行求完成。

目标为Fresh/Adopt、同步private和普通canonical只处理依赖事实/实际改写，原Data按分片组织准备/claim/安装/失败/清理，原executor/monitor去掉不改变等待条件的动作。完整owner生命周期、真实读cut/provider接纳、capacity/revision/claim和实际free后归费保持。数量预测沿03j，不承诺新的ms/百分比。

实施形态比较优先检查现有applyKnownValid是否可直接消费不含保护链的最小事实，并直接输出原候选delta；若可成立，复用现有唯一策略优于另建三套guards/helper。任何此类调整须记录参与guard的字段、未复制字段及不可适用kind，原完整oracle和固定反例共同验证。

开发：编译实际universal image/受影响测试，按责任运行Reference/CpuMutation及必要manager定向组，保留失败。完整候选受影响原八安全组各ARM64/x86_64一次；新修复后仅重复受影响检查，最终同源资格必须对应最终候选。

机制：完整候选沿原matched Freehand fixture，父/候选一次能力后各4个平衡过程（8总），低扰动派生计数验证19projection updates、8segments/4callbacks及版本/镜像/安装/分片run/job/notify等实际分母。不得再跑108过程覆盖账，不授观察库时间收益；未命中/无法测的条件项明确记录。

性能：最终未内部插桩库先父/候选/upstream/原a918能力检查。独立父-候选-候选-父、upstream-候选-候选-upstream、原a918-候选-候选-原a918，各20ABBA块/40配对。使用原同依赖fixture/输入/seed，原始5阶段CPU/wall、像素/历史/销毁/退出reap、实际加载库和共享依赖hash均保存。20,000次块bootstrap、seed261021、pointwise双侧95%（不授正式family资格）；另报告配对绝对差及全部慢值。不与构建/其它性能过程竞争，不替换异常值、不加样到通过；工作量偏差保留并解释。

受保护Fresh/H4双架K1/K16各40配对，复用原M5控制、50,000次块bootstrap/seed260926和单侧98.75%每桶（各四桶family≥95%），不能当本包增量或handoff优势资格。若新产品失败或真实回归修复，冻结该失败，修复后开始新标签批次，不覆盖旧结果。Teardown≤2%非劣、Undo/Redo和metadata真实驻留/终结全部独立裁决。

有限收口：28行有实施验证或有据保留结论，预测/实际/新增成本/剩余差额同表；数量、安全、净收益、默认晋升、M6分开。M6/M7/M8当前0/3、计量2/20、metadata同义分母和完整CP0缺口保持，不能凭本包优化授资格。
