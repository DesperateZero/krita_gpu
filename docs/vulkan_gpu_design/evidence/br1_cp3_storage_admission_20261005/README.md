# CP3 原同步存储准入与费用结算（2026-10-05）

产品 `9c707902d68130a17de4cbd6d64a761215387be0`，父 `b8581139d22bc68d1ff15d93f44167c18bac4db3`；文档父 `d0a7df98ca71f9334c4c506e552aef4ae464ad89`。当前裁决见 [92 §16.117](../../92_br1_m6_m8_execution_baseline.md#cp3-storage-admission-delivery)。**完整 CP3/M6 未通过，M6/M7/M8仍0/3，persistent默认关闭。**

## 原责任及替换

全部 ordinary、retained allocator 与 pmr consumer 经过原 `kisAllocateMutationStorage`。真实同步分配的预留只存在于原allocator调用栈，原controller的domain/aggregate reserved及shared child继续收费；删除该入口的通用slot/cookie准备与七类四域通用commit搬运。父先于local准入，原fitsLocked全部限制和先前waiter政策保持；实际malloc/mmap在两个budget gate之外，local先于parent把同一预留结算为live或在失败时归零，两种终点共用原wake。没有新常驻字段、owner、队列或公开API。

raw free、retained accounting的stop/detach及最后weak/control free端点保持：物理free先于退费，controller退场后保留原parent/child费用至实际释放，最后owner释放才unregister。payload/class-change、cold arena block、slot-array growth及异步waiter grant仍需要原可转交reservation，不能删除这些真实consumer。

生产两文件 **+73/-8净+65**；两个原测试 **+8/-8净0**，case/数据行新增0。三个audit文件 **+7022/-6998** 单列，原ratchet未放宽。两个scoped phase承接同步scalar费用而替代generic transferable protocol；净增是这项直接表达的成本，不声称全项目复杂度/净删改善。费用、limiter及cold refusal保证没有关闭。审阅及同批删除见 [final-review.json](final-review.json)和七份源码/audit `.patch`。

## 当前同源验证

双架完整16 CPU目标各5335/0/0、业务11/0/0、ReadBaseline45/0/0、重建foundation14/0/0，共 **38进程10810/0/0**，actual0/reaped/指定库及前后SHA通过。原LIMIT_LONG_TESTS、其他完整模式/OFF/TSAN资格限制保持，不把测试总数授予M6资格。

两架各 **31080 handoff及28 index/root/descriptor/restore**真实安装区间，malloc family及明确audit线程mmap/munmap均alloc0/bytes0/free0。新增原allocation生命周期probe每架 **22边界**，覆盖五种size/alignment的heap及VM、local/shared实际物理拒绝、parent先拒绝、local拒绝后归还parent、实际capacity前后live/reserved、硬满后的下一请求、weak control及retained allocator在controller退场后的真实free/停止新分配。物理allocation interposer内读取两级usage并嵌套拒绝请求，证明budget gate已释放且预留不能再次消费。probe与产品矩阵计数分开。

结构为87TU/2185APIs/**28248edges**/27callbacks，21manifest/25ownership/16census/19intrusion及六项工具自测通过。[最终核对](final-verification.json)绑定当前2315/M5 1143 source/audit Git blobs及263 runtime/harness输入、17身份集合；测试运行时的工作树字节随后绑定当前提交，不凭旧source_head授予新源码资格。

## 控制与资格

固定M5 `5173c807c87bb1619325249a07a8b4f4f8f09f09` 复用已匹配依赖、工具链、universal架构及17核心选项的独立构建。原H0 scanline公共CPP两侧相同并按各自头文件编译；H4 full-payload/history公共probe两侧相同并独立编译。每scope原40对/四桶轮换、变体顺序平衡、250ms直接completed-work throughput、20独立blocks、50000 bootstrap seed260926、单侧98.75%每桶及0.98下界保持。各scope分别95% family，不合称完整required family。setup、最终validation/undo-redo/close不计入timer；H4为四个undo事务，不冒充native root handle H。

Fresh当前÷M5为arm64 K1/K16 **0.8961/0.5369**、x86_64 **0.9400/0.5462**，下界 **0.8796/0.5235/0.9292/0.5280**，四桶未达0.98。当前K1仍低约6–10%、K16约45–46%，见 [Fresh结果](fixed-m5-fresh-summary.json)。前一包与本包绝对数据不是直接源码配对，不相减为本提交因果收益。

H4当前÷M5：arm64 K1/K16 **1.1449/0.7554**、x86_64 **1.0148/0.7661**，下界 **1.1188/0.7258/0.9973/0.7582**。K1两架通过0.98，K16仍低约23–24%，四桶family未通过，见 [history结果](fixed-m5-history-summary.json)。两个控制scope共640实际正常退出进程；启动前失败不计样本。

原handoff协议40对/四桶、8warmup+64测量、诊断关闭、单侧98.75%和20%/30%门保持；320实际正常进程23040操作。arm64 K1/K16降幅 **4.45%/9.85%**、下界3.82%/8.52%；x86_64 **5.19%/10.46%**、下界3.30%/9.24%，四桶仍未达门，见 [延迟结果](latency-summary.json)。两种路径绝对计时降低不等于相对gate通过；不同批绝对值不能相减为本提交因果收益。三个统计scope分别裁决，不能合称完整required或M6资格。

最终当前K16 Fresh实际body采样等待QTest init及setup后运行，test/sampler均actual0/reaped。exclusive栈仍以原fitsLocked为主要计算热点（190采样），其后是allocator/accounting/free与原Ledger preparation；thread wait含后台闲等，不计算因果百分比。采样改变timer，所有profile throughput排除统计结果。下一完整责任为原每类/域/aggregate/durable限额计算及generic物理delta准入，同时核对recoverable与Fresh共同准备/真实差异；先审全部状态转换和消费者，再决定实现，不能跳过检查、放宽限额或继续盲拆allocator helper。

## 失败及剩余

首次CPU mutation为1561/1/0；原waiter费用测量先准备slot，拒绝分支却依赖普通分配自动建slot。拒绝分支现在显式准备同一测量geometry，保留少1B/实际request-state拒绝/候选cancel及费用归还断言。首次两个Reference各786/4/0，仅四行期待旧320B slot cache尾费，实际0；现断言最终物理free后的live0/reserved0，保留全部写集原子性/拒绝重试断言。失败组不累加到38最终进程。

首次control builder漏传外部history源码，默认install源码缺interposer符号而链接失败，日志/命令保留；正确probe另建control-history目录。首次H4 runner身份路径残留旧control-public目录，写入协议后、启动任何性能进程前失败；原runner和日志保留，新 `fixed-m5-history-02` 另开完整40对。首个storage probe编译有unused变量警告，移除并另建最终binary；该旧binary未授予资格。证据工具失败不能记为生产修复或成功性能样本。

本批同步存储责任结算，完整CP3继续未通过。固定M5吞吐回修、handoff20%/30%、common metadata同义实际used/reserved/slack驻留≥25%的可运行旧分母、CP0完整required及正式统计资格仍欠；不把移除slot、sizeof或cold请求当驻留证明。后续沿实际热段修复共同成本，保持完整原目标及CP4–CP10依赖；不重开没有新生产反例的CP1长fault/压力工作。

原raw日志及全部失败统一保留于压缩包和逐文件SHA清单，二进制/object/dylib/构建目录和外层gitlink不提交。
