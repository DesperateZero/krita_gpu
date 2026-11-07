# P1 当前核类型标签与原库执行上下文

CPU查询本身和IORegistry输出没有核类型映射；旧Time Profiler表具有core标签，但旧source的成本不能当当前38834成本。因此另固定两个当前原库ARM过程（K1 native-pin、K16 hit），各一段3s Time Profiler，绝不与I1/V1测量并行。直接复用未插桩seed probe，fixed累计5s有效操作、min128、8warmup；没有CPU/rusage/reference/编号插桩。120s fixture超时，45s profiler超时，kill/reap；保存全部失败，不补录。

从已flush的LAYOUT行之后attach；它不是operation就绪证明。只取Running，按当前fixture原timed范围的sample source行或明确API入口(beginCurrentTransaction/beginMutation/beginWrite/seal/preparedPages/commit)划定操作上下文，setup/close/drain/后台分开。若operation样本不足100，不授粗定位且不重录。每种core标签记录实际编号和计数，未出现编号不填映射。只授本次实际trace标签，不把旧表或数量转换成精确CPU微秒/可删量。

P1不是收益测试或新增门禁，不用采样替换全量吞吐，CPU份额不得当可删除空间；少见慢核样本不足时不推定已排除其影响。不加样到凑齐核映射或候选热点。
