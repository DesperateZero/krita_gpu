# CP1：原 metadata / Ledger 准备与 history 效果接受

本包从产品父提交 `8f07d43ec1646ad0e979f93f9564fcdd8838dcef`、文档父提交 `6b675c9617d5b2eb78c538cc2da5a003d19f0b58` 继续同一capture→history→retirement责任。最终产品身份由 [Git绑定](git-round-identity.json)记录；源码、库、测试与实际增删见 [source-metrics](source-metrics.json)、[源码哈希](source-sha256.txt)、[运行物哈希](runtime-sha256.txt)。只提交本包明确路径，不push。

## 目标与实际替代

比较了为旧Qt投影逐层增设收费/异常包装，以及只提取实际consumer所需identity、把准备前移回原owner。后者删除了两次版本投影和调用者拼装，且不需要持久失败阶段。本包未替换独立reference状态机：它继续作为oracle，generic snapshots/discard有真实消费者。

| 原路径 | 最终责任与同批删除 |
|---|---|
| historySlice完整version projection → history逐版本versionSnapshot/eligibility → discard.versions → applyProjectedSequence | 原slice只枚举固定32 identity。metadata discardHistory在compact records检查capture/read/last-use/pin/operation/authority，准备精确收费effects和Debt，复验真实page revision后原位unlink。旧history筛选helper、snapshot循环和Qt discard数组删除 |
| Work Qt effects；重扫pageKeys整目录Qt数组 | 原Work持有charged vector；metadata detach前准备实际capacity，接受后move同一packet，原effect cursor逐项转交；全部接受后释放真实capacity。visitPageKeys在原目录锁内流式喂原Work，public reference pageKeys保留输出但删除中间shard数组 |
| Ledger准备的Qt分类/maps/set、默认std slot/free-list/credit存储 | 原prepareBackingChangesImpl共同消费generic Qt输入及history pointer/count；scratch和原slot/free-list/changes/physicals/credits/claim index使用同一实际收费allocator。physicals自己去重，claimedPhysicals set删除。全部容量/node齐备才发布physical class claims；异常撤销同slot全部已插入claims和reservation |
| Queue已接管单record仍重新组装effect/cookie/batch Debt准备 | 复用原atomic reclassifyBacking，保留原预算、exact physical/class/claim/headroom检查。删除单effect临时对象及batch准备绕路，Metadata硬满不会新增批量scratch依赖 |
| Default冷backing准备的owner解锁窗口 | 两侧复用原等待政策，重新拿锁后复查key去重、64项准入及已materialized版本。修复真实并发上限违反；不增加计数、队列或准入owner |

语义增量是实际容量拒绝前不detach、准备异常不遗留claims、效果存储实际收费及冷准备后的Default准入复验；不是纯等价去重。生产8文件 **+290/-132，净+158**，测试4文件 **+160/-33，净+127**；派生图/基线/ownership单列。新增3个私有方法分别有metadata删除、目录枚举和共用准备的实际consumer；无新owner、队列、deadline、失败状态或上层API。固定identity slice增加约1KiB调用栈，Ledger收费cache保留到实际销毁，physicals去重线性查找和锁内准备成本仍未取得BR1-PERF资格。

## 行为证据与限制

最终双架构各CPU1275、Reference659、PhysicalClaim379、ResidentRead221、Foundation28、Freehand压力/取消4，合计 **5132 passed / 0 failed / 0 skipped**，原始输出和命令见 [accepted结果](accepted-results.json)、[运行汇总](run-accepted.log)。这些是当前源码结果，不能与此前聚焦/失败运行累加。

- 新增effect容量和Ledger scratch真实硬满行：原Work已存在后占满固定Metadata额度；版本仍归metadata，provider零次；释放实际容量后原task/Delay无新输入恢复并实际free。
- 新增两backing、0–4096字节/64字节阶梯的冷Ledger真实配额扫描：准备拒绝/cancel保持原class和原Debt reservation，释放filler后同backings立即准备/commit，防止key/physical claims遗留。扫描能证伪回滚，不声称逐个全局allocator故障覆盖。
- 新增实际Debt准备后、shard解锁窗口内AcquireRead：真实page revision变化，旧准备cancel，不detach受保护版本；ReleaseRead后沿原history继续，provider只执行一次。
- bounded history oracle现在直接消费目标discardHistory，与原状态机比较精确effect集合、removed bitmap、版本结果；删除cursor自身后继续、4095历史、default revision重启仍通过。
- 原record恰满、无输入Debt恢复、sync GC、root长历史/变化、多页共享预算、close/stop和最后handle测试保留。ResidentRead明确区分payload清零与常驻Metadata费用，并在实际Ledger/子controller销毁后验证共享process回到预热实测cache基线。

最初编译包括错误replicaHandle归属、遗漏Reference/PhysicalClaim调用者和测试链接可见性，日志保留。`focused-initial-*`是在完整链接前误启动的新库/旧测试混合运行，明确不计作当前源码行为或验收。后续冷callback与两backing夹具修复保留：单页Debt额度、caller-owned adoption fallback和既有reserved Debt不能用零假定。第一次完整组暴露单record在Metadata硬满绕回batch准备的实际回归，以及ResidentRead旧Metadata清零断言；前者修复原调用路径，后者改验实际收费和销毁退费，不放宽payload/身份/像素断言。[qualified失败](qualified-results.json)与所有原始日志不覆盖。

第一次`frozen`运行又暴露Default准备在冷backing解锁后未复查原准入政策，provider并发65/2违反原64/1限制；通过同一原等待政策和精确materialization复查修复，保留全部断言与失败日志。最终资格使用后续`accepted`运行；不能把较早的`frozen`标签当通过。

结构门在调用图重建、原authority核对后刷新source checkpoint；当前manifest/上层侵入阈值保持，结果见 [最终结构门](architecture-frozen.log)。不是新增耦合额度。普通补丁和脚本检查通过；原始日志及unified diff保留原有空白。所有最终源码/运行物身份与本地提交blob绑定。

**完整CP1未闭合，M6/M7/M8正式资格0/3、默认关闭。** generic metadata applyProjectedSequence/versionSnapshot、provider journal Qt输出、generic operation前置登记/有效result归属、core backings/physical/registry、本体、capture辅助存储、tree/deferred/一次性task、close handles/seen/诊断、runtime/clock及完整永久拒绝最后handle仍欠。指定history保证不推广为foreground全局bad_alloc或全部退出资格；自动恢复的测试不等于永久压力一定可drain。CP0同依赖upstream、TSAN、公平/原job接续和性能无新增资格。当前范围和下一有限端点在 [92 §16.38/§17](../../92_br1_m6_m8_execution_baseline.md#metadata-retirement-preparation)、[NEXT_EDITS](../../br1_modification_guide/NEXT_EDITS.md#closure-next-work)原位维护。
