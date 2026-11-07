# CPU写入蓝图实施：事前范围与固定协议

起点产品`2f22452e2dc76dca3e60c6231783534f44716ce4`，外层`fa18481b472f349cccd983fd06f68d6dfa8984c8`。实施目标为03c B1–B8完整固定源consumer及同步删除，随后B11/B12；completion分source仍为独立条件候选。本包不改变M6正式门或默认persistent。

1. 产品修改前冻结原image库及源码；派生三个TU的独立诊断库，用预分配POD记录每operation目标页、原页访问连续段、片段move次数和实际成功冷preflight pin。仅在夹具全部工作与清理后dump；overflow、加载错误或语义失败必须保留并停止。
2. 前置真实序列固定ARM四过程：普通/opt-in/opt-in/普通，每过程原8段/4update/4workers一笔。复用原计数夹具，核对Setup→Stroke差值、像素/undo/redo/终点及库身份；120s timeout，kill后5s reap。所有失败保留，不追加至所需计数。其时延不作为收益。
3. 根据真实ΣR/ΣP/ΣC及适用域修正条件预测，登记最终私有桥与同批删除映射再动产品。保留全冷准备、原transaction校验、callback失败、单页pin和真实cut/free；新增计划在首字节前完整准备并实际收费。
4. 安全覆盖原painter/manager/CPU mutation/producer相关测试和新独立像素/数量/拒绝反例，两架完整目标组；必要修复保留失败，另批验证。结构、预算/释放及源绑定caller图同步刷新。
5. 机制固定parent/candidate/candidate/parent四过程，普通真实夹具，核对页序列及Σ(C+R)→Σ(C+P+E)，代际/copy/init/ticket/job/operation/cut预期不变。适用外路径单列，不能把少工作算收益。
6. 机制/安全通过后，未插桩两架各24配对、12顺序平衡块，共96过程，另先各side/arch一次能力检查。原MatchedFreehandBaselineTest，主端点stroke-to-projection-ready；pen-up/undo/redo/teardown为次端点。沿CP0块log ratio、20,000 bootstrap/seed261019、pointwise双侧95%；120s/kill+5s reap。所有原始失败保留、身份/语义失败停止、不删尾不延长到通过；性能期间无构建/采样竞争。低重用输入另以固定独立夹具覆盖，不混主端点。
7. 共同准备/范围变更后串行复用原M5 Fresh/H4保护协议：两family×四桶×40对，250ms、20顺序块、50,000 bootstrap/seed260926、单侧98.75%、throughput lower≥0.98。原正式M6校准、metadata实际驻留分母及完整CP0独立保留缺项。

退出要求是完整caller迁移和原路径删除、行为/资源/真实数量以及未插桩结果比对，不以单独const/sort补丁或算法模型通过替代。失败或收益不足须解释并修正模型；不盲扩样。

安全失败后的事前修订：safety-full-0前三组通过，PaintDevice的stressTestMemoryFragmentation在81像素patch跨64像素页的并行写拒绝后memcpy空指针崩溃。冻结parent单独同方法也SIGSEGV（shell139），不是本候选引入；保留两边日志及崩溃栈。本批不改该独立原测试/并行入口，最终safety-full-1对两架各六组重跑，PaintDevice由-functions枚举其它全部方法，明确不授该stress通过或完整PaintDevice组资格。该限制与原正式M6缺项一起保留。

结构首轮拒绝后收回上层结果枚举：transaction仅消费原manager bool语义；DataManager在原适配边界用一个PixelOperationResult别名统一既有结果类型声明，原PageStore类型集合不增，identifier计数cc25→24/header12→11，布局/公开上层API及原ratchet阈值不变。最终caller图重新绑定这些实际源码。

低重用负控制在任何该端点采样前固定：low_reuse.cpp同一个未插桩可执行文件、冻结parent/当前candidate image、其它库共同；ARM/Rosetta×同页16dab/16独立页各12配对、6顺序平衡块，共96过程。每过程原ordinary transaction中固定256次bltFixed，端点是完整operation循环（含每次准备/执行/交付，排除源构造、最后像素校验/commit/cleanup）。像素逐字节与独立覆盖oracle相等，P=R、F=16；这些循环不算独立样本。沿块log ratio、20,000 bootstrap/seed261020、pointwise双侧95%；120s/kill+5s reap，全部失败停止并保留，不追加至通过。此负控制不是stroke或M6正式样本。

负控制首轮只有两过程即因跨side像素hash不一致停止：独立main漏了原SIMPLE_MAIN的EXTRA_RESOURCE_DIRS，出现缺失profile SAFE ASSERT，QColor转换生成不确定源；两个过程各自覆盖oracle通过不能证明输入同义。保留v0源码/库/两日志，不进入收益统计。修正夹具沿原SIMPLE_MAIN设置资源目录，显式要求profile存在并直接给固定RGBA8字节，避免颜色转换输入；产品不改。lowreuse-1沿同一原定96过程/端点/停止/统计协议新开一批，不续采或挑除样本。
