# BR1 待改代码段与实施入口

本表记录较早的代码定位和任务拆分。当前 M6 任务见 [92 §1](../92_br1_m6_m8_execution_baseline.md#native-cpu-baseline)。查某个业务或共享服务的修改历史时，按[证据适用范围](../README.md#evidence-scope)核对本表中的 owner、调用点和测试。03h–03j 记录的是旧 CPU 管理管线的生命周期优化批次。

优先级固定为 **stroke → undo/redo → 上下文切换**。必要的错误、容量与回收保证属于 stroke 前置工作。M6 → M7 → M8 的阶段出口顺序保持不变；能力可先在测试中建立，业务启用必须闭合整条责任链。所有拟议 token、borrow、checkpoint 接口先沿既有 owner 扩展，不另建状态权威。

真实绘画下一批的跨项入口为 [BC1–BC10：真实 stroke 联合接线](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01j_real_stroke_integration.md#stroke-integration-map)：BC1–BC3 接原事务、painter 与 job；BC4/BC8 明确同步旁路与真实目标；BC5–BC7 联合读选择、显示 cut 和终结；BC9/BC10 对应资源前置及完整验证。它细分现有 S01–S05/S10/C02/V01，不新增阶段。


<a id="closure-next-work"></a>
**每轮先裁决：** 核对当前 caller、owner、失败和退出边界。已暴露的重复分支、无 consumer API、责任重叠或实际存储/引用泄漏阻塞目标时，先修复并同批合并、删除；否则实现排期中最早可执行的缺失能力。记录选择依据、替代对象、有限结果和未关闭条件，不能只加 API 或反复跑历史矩阵。

**每轮审阅与提交：** 普通源码/文档使用显式补丁，Python保留给分析、运行与派生证据；每个完成的实施包统一检查后做聚焦本地Git提交，按 [编辑与提交合同](CONVERGENCE.md#round-edit-and-commit)核对该轮起点、暂存范围及产品/文档两仓库身份。已有跨轮未提交内容先明确累积基线，不能当本轮提交或混入未归属文件。

已交付的prepared task/terminal、typed通知与唯一退休节点见§16.31–16.33；§16.34再把原queue context/retry Wait/task/capture/Delay移到物理adoption前一次冷准备，删除每retry重建和旧scheduleAfter。必要record订阅准备拒绝时保留同一debt，由预付retry自动继续；generation/晚取消/在途coalesce与实际Debt释放的结果见 [92 §16.34](../92_br1_m6_m8_execution_baseline.md#prepared-retirement-retry)。这些对象不再重复领取。

§16.35已替代原read cancel/release ID deques、ack matching/pending/released数组与Store聚合，并把last-use订阅拒绝接入原固定retry。原request冷准备前移到选择前，选择/AcquireRead保护共同持锁；同request准备拒绝恢复和原记录实际free已验证。已交付范围见 [当前代码差集](CODE_INDEX.md#read-terminal-storage-code-index)，不再重领这些通知/节点或新增等价包装。

§16.36已把capture查询和释放合为同一收费排序版本数组，必要释放节点/容量在root/version保护前准备；销毁和部分准入回滚直接转交该节点，原read task/Delay按已完成事实继续。版本QHash/复制、旧PendingCapturedRelease/deque及failed/released数组删除，纯节点free不阻塞restore，实际fee随物理free归还。见 [当前代码差集](CODE_INDEX.md#captured-release-code-index)，不再领取这些容器或增加等价capture包装。

§16.37已将history五组容器收为一个收费key工作记录及intrusive ready link，固定32 candidates和16-pointer pass，前台/后台共用扫描。当时的detach后效果记录由§16.44进一步删除；provider注册时固定后台退休许可，交接不调用provider或分配节点。原退休记录在物理准入前准备实际operation map node，provider有效result只保存/绑定/轮询，不重放retire。实际key/Debt拒绝由原task/冷Delay无输入继续；两段扫描间解保护也标记repeat。该批冻结映射见 [代码索引](CODE_INDEX.md#history-handoff-code-index)，不再领取这些已删除容器或效果聚合。

§16.38已消除history的完整版本投影、逐版本snapshot筛选、discard临时数组和重扫目录Qt数组：固定identity枚举、原metadata compact guard和实际收费effects容量共同服务foreground/background；当时Work保存的未接受效果由§16.44收回slice局部packet。Debt共用准备的scratch、slot/free-list、change/physical/credit数组及claim nodes按实际allocator收费，中途拒绝回滚同cookie下全部claims和reservation。真实硬满拒绝、无新输入恢复、Debt准备窗口中新read保护与原oracle已验证；不是generic transition或永久压力全出口资格。

§16.39已核对同步consumer的更直接形态：原request/adoption/write activity持有result，Ledger直接验证原operation/provider/registry终态；5个Store点、transfer及foreign同步retire全部迁移，旧consumeTerminalProviderOperation及bind→verify→release临时登记删除。实满Metadata接受、foreign物理释放、错误transfer ID与registry终态已验证。退休预付node及显式pending/reference binding合同保留；不再领取同步登记准备，也不为它增加结果队列。

§16.40把Registry Private/shared控制块、source节点和实际ticket区间接入原process预算；allocatePending收费准备后才铸造ID，complete只更新/合并原节点，删除terminalRanges/nonSuccess两索引和终结时分配/回滚。真实provider原allocation记录在物理创建/alias/initial adoption前保存退休ticket，拒绝退休沿用同一Pending，物理free后完成；transfer和archive准备/失败也在原scope中收口。硬满三终态、实际provider双节点准备拒绝及pin拒绝后退休已验证，不再领取这些终结节点或增加失败阶段。

§16.41已删除第二m_changes journal、live弱数组和acknowledged数组：原Payload存domain/revision及dirty link，实际收费稳定payload/slot节点、weak admissions和准备容量；physical commit只更新原事实。domain admission全部准备后才发布claim，cancel/commit/detach转交节点到门外free；Ledger实际收费changes及单Probe，整个cut通过后才精确ack。实际硬满snapshot/probe拒绝、claim准备失败后同payload重试、恰满physical commit及stale ack/晚snapshot释放通过。见[当前差集](CODE_INDEX.md#domain-journal-code-index)，不再领取这些容器或增加等价journal。

§16.42已把logicalReferences收回原Payload，删除physicalPayloads/Tiles3PhysicalPayload。三个adoption入口共用原prepareAdoption/adopt：fresh前置actual allocation/Payload/slot三个节点，已有alias只准备一个逻辑node，安装转交同nodes；实际lease节点/buckets接原retained root，拒绝不丢旧pin/未占用ID。统计等待原serial后读domain，避免observer→tile逆序。actual三节点拒绝、alias/initial保留、lease硬满/同ID重试及统计交错通过，见[当前差集](CODE_INDEX.md#provider-adoption-code-index)；这些索引和已删Qt physical表不再领取。

§16.43将actual backing/physical nodes并入原retirement record的cold准备，registerBacking只转移同nodes；原backing内嵌成员link替代sharedPhysicalMembers，接管保留同节点和退休记录，last physical与backing节点门外free。同步登记标记由该调用栈持有，allocated registration index删除；初次安装才绑定已准备allocator，挂接仍不分配且保持冷限额/共享父预算配置。actual两节点拒绝、直接结果保留、rollback后同record补齐、硬满安装/原queue接续、登记窗口阻止swap/同physical竞争及三alias任意顺序退休已验证，见[当前差集](CODE_INDEX.md#ledger-backing-code-index)。

§16.44已统一所有实际producer的prepared completion政策，删除物理成功后的业务Failed/rollback和退休ticket缺失的旧分配失败解释。History在detach前验证Debt owner、已登记backing及原退休record，成功只转交同record；Work.effects/nextEffect、finishEffectsLocked、pendingEffects和close guard/诊断删除。退休bind只消费原预付node，后置generic分配fallback及detachedRetirement缓存删除，generic Pending模型保留真实consumer。双架构5352/0/0及实际删除检查见[当前差集](CODE_INDEX.md#retired-policy-code-index)，这些旧失败政策不再领取。

§16.45完成本次旧协议退出审计：Read空effects协议、后台许可第二事实及retry重查、batch effects缺Debt补准入/缺record跳过、无consumer的独立extent查询及backend分配输出包装全部删除；batch/History共用原record接受不变量，调度差异保留。剩余read/capture阶段、Pending/subscription/Delay/Debt、generic effects/公开身份拒绝、未前置provider/proof/Qt容量及旧模式/Failed各有真实依据与删除条件，统一见[92审计](../92_br1_m6_m8_execution_baseline.md#protocol-residue-delivery)。不再领取已清除残余，也不把该清理目标完成记为完整CP1通过。

§16.46已关闭原Ledger provider/pending→accepted cut/route→proof接纳/撤销的paid节点生命周期：provider节点在外部admission前准备，同节点pending/accepted；domain与route共用scalar cut，原pending集合和Qt snapshot/list删除。proof真实节点在provider validate前准备，接受后才推进stamp，revoke门外归费。实际硬满拒绝及准备后硬满安装、pending隐藏/callback切点、输出/结果保留和最后free已验证，见[当前差集](CODE_INDEX.md#ledger-provider-proof-code-index)；这些paid容量不再领取。无预算及挂接前节点仍归bootstrap兼容，不能追溯宣称完整收费。

§16.47已关闭exact scalar查询/native discovery与capture原cut/protection/release有限端点：生产versionSnapshot退出嵌套Qt副本，generic read候选在原Store/shard gate外付费准备后重取cut；capture Private/control、version/removal/surface数组及default map归原budget。旧capture Qt delta导出/removed/staged容器、singleton保护投影及projectVersionPair包装删除；同release记录保留detached block费用到实际free。真实硬满和晚guard已验证，见[当前差集](CODE_INDEX.md#capture-metadata-code-index)，这些容量不再领取。

§16.48按当前实际consumer删除空publication effects容器/getter/安装输出、commit空packet字段与搬运；detach准备和复验改用安装已有的原record isPreparedBy，旧完整快照删除。真正的abort/discard/GC退休效果与queue pump继续；read/capture进度、Pending/subscription/Delay/Debt和Failed/cancel仍有真实来源，见[审计](../evidence/br1_publication_residue_20261002/deletion-checks.json)。已删对象不再领取，完整CP1和排期不因本轮净删而结算。

§16.49已关闭原PreparedPublication独占Data/数组/authority hash/嵌套安装保护容量与晚清理，全部MetadataArenaGrowth holder使用原allocator；controller退场后的原directory/block费用归同一accounting寿命。旧未收费容器、默认无预算构造和空deleter保活残余删除，无新结果队列或阶段，见[证据](../evidence/br1_publication_storage_20261002/README.md)。这些对象不再领取，generic临时Qt准备仍未关闭。

§16.50删除首写mutationBaseSnapshot及caller完整版本/保护列表复制；queryMutationBase在原shard cut返回必要标量和一个before候选，三个native/generic/semantic consumer同原入口，实际恰满查询及full oracle已验证，见[证据](../evidence/br1_mutation_base_query_20261002/README.md)。它不授予write/physical claim，后续联合准备与真实拒绝仍在原责任链。

§16.51删除read cancel/release/ack与后台取消重试的过时外层bad_alloc捕获及allocationFailed标记，订阅前同锁检查去重；原保护节点复用/移除和intrusive cleanup无新分配。真实subscription/history准备拒绝在各自原入口保留，同一claim/identity拒绝与晚guard进度不变，见[清理及保留依据](../evidence/br1_read_failure_residue_20261002/deletion-checks.json)。这些旧分支不再领取。

§16.52已把generic/publication的StateMachine临时值接原allocator，Qt oracle与私有生产值共用同一转换政策；后续转换和publication安装移动同一Version，旧二次复制、seen/included/previous/retained/discard集合及公开Qt known-valid入口删除。真实硬满准备拒绝、Debt后再次硬满取消cookie及精确归费、完整oracle已验证，见[证据](../evidence/br1_metadata_working_storage_20261002/README.md)。这些工作值不再领取；其effects下游已由§16.53继续收口，外部Qt oracle仍有真实consumer。

§16.53已把原paid effect span在Debt提交时直接转交原退休record；Qt输出、Store/publication聚合及append/copy、History输出与二次交接、旧retireEffects入口删除。原ready list按record许可承接首次尝试，worker/manual/pump共用retireBatch，operation部分回滚提前返回同一退出pump。真实提交后硬满、原node/许可、foreground process额度、missing receiver原子拒绝及双页后页Debt拒绝接续已验证；[23项删除/保留检查](../evidence/br1_effect_acceptance_20261002/deletion-checks.json)列明真实剩余来源。该有限交接不再领取，没有新持久阶段或恢复队列。

§16.54已关闭原overlay candidate/state/index/control、proof/removal节点和buckets、surface/version/change数组及抽出node holders的实际收费和晚释放；重复keys/historical/完整Qt delta投影、surface后置容量拒绝及完整detachment Transition输入删除。History missing-key拒绝统一由原metadata/rescanRequested保留，foreground/worker复用同一collection pass，候选History节点协议删除。真实硬满拒绝、安装不重放、原collector续行和controller退场后tail收费已验证，见[证据](../evidence/br1_overlay_storage_20261002/README.md)。这些旧路径不再领取。

§16.55已关闭原commit/restore Data、descriptor-change数组、ordered descriptor/configuration nodes/control的实际收费和释放。全部原consumer提前准备实际节点；post-success插入、hash/bucket容量协议、QSet准入分配、Qt描述数组、额外History key packet和native Page描述副本删除，相同布局在原索引共享immutable值。真实hard-full准备拒绝、安装无增长、配置表原子准备和controller退场后inert尾收费已验证，见[证据](../evidence/br1_commit_descriptor_storage_20261002/README.md)。活semantic候选仍要求原owner，其他bootstrap失败和全永久尾出口未获资格；已删对象不再领取。

§16.56删除已初始化host ticket的seal/commit/restore假拒绝、owned proof撤销/epoch abort身份失配的假重试出口及commit重复surfaceChanges QHash/preparedKeys QSet。原claim下直接查询唯一交易state，公共非法身份和实际准备拒绝保留；[证据](../evidence/br1_prepared_fact_residue_20261002/README.md)绑定5414/0/0，列明清理不再领取。

§16.57把原commit/restore工作输入接入paid Data，删除publicationHeaders/publicationSnapshot、完整Transition数组、restore三组重复集合及manifest中间副本；backing数组移动到原Ledger slot，metadata/epoch候选从准备起共用原Data门外清理，独立discard helper删除。生产完整write set更新原epoch记录，修复真实backing拒绝后重试误用增量协议；公开incremental/Qt oracle保留。[证据](../evidence/br1_publication_input_storage_20261002/README.md)绑定5534/0/0，这些对象不再领取。

§16.58统一原保护政策下root查询，删除active base丢失/current capture缺root/retention count缺失软失败及restore逐字段重建/重复验证；登记顺序和空槽回滚支撑同一不变量。[证据](../evidence/br1_epoch_protocol_residue_20261003/README.md)绑定5534/0/0。真实Qt索引分配边界未注入，不当作实际存储收费交付；这些旧分支不再领取，下一实际存储端点不变。

§16.59把原epoch三字段写集、值/实际shared控制块及dense manifest工作数组接入原预算，prepare/commit/collection共享一个immutable值，门外准备/释放；真实拒绝保留原记录，相同native完整集复用revision。辅助索引、dense Qt中间副本及7处生产transaction导出删除；public oracle保留，incremental两种相反操作顺序统一原子拒绝。[证据](../evidence/br1_epoch_transaction_storage_20261003/README.md)绑定5562/0/0，原写集责任不再领取；root/core/control/Qt registry及tree释放未包含在本批收费保证中。

§16.60已关闭原epoch core/实际std共享control、三组registry节点、root surfaces/实际数组/control和tree节点/control；保护计数归原root，两张Qt count表删除，原cancel/release/collector门外抽出实际节点。最后tree引用复用一次冷准备的收费task，batch/deque/TLS及析构时分配删除；controller退出/满额8192节点尾释放与精确归费已验证。原Store配置先准备epoch候选，default/metadata复用原接受事实，source已接受而首ticket拒绝由两个registry/source receipt字段接续；无新增失败stage。见[证据](../evidence/br1_epoch_root_storage_20261003/README.md)及[当前代码差集](CODE_INDEX.md#epoch-root-storage-code-index)，这些已交付对象不重领。

§16.61只回收驻留协议残余：Transition接受后唯一承担serial取消；物理移动后的原提交和原allocation引用释放不再静默拒绝；原准备数组身份阻止同数值revision的登记重建ABA。生产净+4，无新类型/状态/容器/API，双架构八组5614/0/0，见[证据](../evidence/br1_residency_protocol_cleanup_20261003/README.md)。observer实际收费候选扩大了本次清理范围且未通过原24 MiB压力场景，已撤回；其Qt登记/本体/control仍属欠项，不能从候选日志领取已交付资格。

§16.62已取得固定upstream同依赖可运行对照和普通真实freehand代表性基线，并补齐原history commit→memento dirty extent→TransactionData投影失效交接；没有新终结协议。共享夹具/构建/五插件可复用，不再重建对照。目标回归4210/0/0与48个独立配对进程同像素通过；stroke/undo/redo描述性结果明显回退。完整arm64 DataManager的24行pin次数翻倍及ChangedStorage bad_alloc、两个UE尝试仍未关闭，见[证据](../evidence/br1_cp0_matched_baseline_20261003/README.md)。下一先沿原pin/preparation/metadata容量和退出owner审查实际失败；缺同父全套对照，不能直接改期望或断定旧失败。原delta Qt导出/收费与真实拒绝归CP1；完整CP0 required清点、canvas/M/K/E及正式样本继续补齐。

§16.63已关闭上述原准备重复及小范围extent容量反例：暖pending不重复prepare guard/pin/restore，真实guard仍按需swap-in；原Growth在扩展侧复用slack，负坐标不再指数扩容。冷pin和未写generation实际计账，旧并发consumer新增sealed/cancelled/活动页归零断言。双架构完整manager1057、CPU1319及原reference/freehand控制合计6304/0/0、十进程exit0，见[证据](../evidence/br1_execution_preflight_20261003/README.md)。这些路径不重领，三个失败尝试仍UE；上一轮普通stroke性能回退未取得新的配对关闭证据。下一继续原wrapper/登记/shared控制本体、bootstrap/固定成本与完整尾出口，并补CP0 required/测量端点；extent原数组/Qt导出实际收费仍在CP1，不据pin减少或通过数结算整体。

§16.64已补齐原CPU binding对象/control的实际容量准入、像素前准备及最后weak尾free，全部消费者共同迁移，旧Qt binding创建/持有/cast删除；双架十四进程7542/0/0、均正常退出。该批首轮组合freehand的24MiB checkpoint metadata preparation拒绝当时未解释，单独及组合复验通过不能关闭它；当前原因和剩余边界见下述§16.65。原retirement/close已移除metadata cache，四BPP×33代探针1→0通过，无需再建清理协议，见[证据](../evidence/br1_resident_binding_storage_20261003/README.md)。原binding/control不重领，旧UE尝试及性能回退继续保留。

§16.65已复现原324页detachment请求269568字节的共享容量拒绝，原Entry去掉此路径不用的发布载荷；同候选实测20976字节，父硬满后安装/取消及原分批释放通过。原配置切换测试边界先完成排队终结；全部临时生产诊断删除。[证据](../evidence/br1_checkpoint_pressure_20261003/README.md)保留后续surface准备8304字节拒绝及8MiB backend准入不足，最终十四进程7546/0/0不关闭完整压力资格，不重领已经缩小的候选。

§16.66原metadata配置shard/control、immutable数组、三个arena目录及identity按实际retained请求收费，一次发布完整局部候选；旧估算/手工目录fee/超预留拒绝删除。真实少一字节连续拒绝不留capacity、原对象重试及晚cancel/cleanup归费通过；该轮最终十四进程7559/1/0正常退出，arm64 24MiB surface准备反例再次出现。[该轮证据](../evidence/br1_metadata_directory_storage_20261003/README.md)保留全部尝试，固定目录差集由下一段更新。

§16.67已删除eager最大目录、重复full-growth规划及attach隐式增长。原MetadataArenaGrowth承接同allocator目录候选、竞争后原grow/revalidate和退下旧数组，门外准备/实际free；slot地址/generation/hardceil保持。64 shard空配置实际请求费1,649,712→76,848B，真实少一字节拒绝、准备后父硬满安装、stale几何接续和晚Data释放通过。最终双架十四进程7570/0/0，原六方法三对压力66/0/0，全部exit0；[证据](../evidence/br1_metadata_directory_growth_20261003/README.md)保留两次失败夹具。净+88生产行、三目录carrier共120B和增长峰值是保证成本，不记去重收益。有限样本未关闭完整24MiB总峰值/永久尾出口或8MiB准入后取消；已清目录固定预留不重领。

§16.68已把原authority/control实际64B请求并入同configure候选，删除未收费构造/重挂接及reserve后置补owner拒绝。原预算选择先于收费，完整候选一次发布，read/captured cleanup在operational acquire后核对原authority；真实第一笔拒绝/完整候选少1B/原对象重试及仅read cleanup的controller后硬满clear/析构归费通过。最终十四进程7584/0/0、压力三对66/0/0均exit0；生产净-12、Private预算选择指针+8B、原authority64B实际fee单列，见[证据](../evidence/br1_metadata_authority_storage_20261003/README.md)。该authority和原目录不重领，Private/standalone bootstrap仍欠。

§16.69把实际Private104B并入同配置候选，原冷配置事实移到facade，core指针一次发布替代独立operational；eager new Private和生产无用standalone controller删除。真实首Private/少1B拒绝、冷预算配置及空core入口、原晚Data/read cleanup和standalone晚候选通过；双架十四进程7584/0/0、原压力三对66/0/0均exit0。生产净+34承担收费与候选完整清理；attached对象尺寸减少1,336B、实际配置新增104B费分列，见[证据](../evidence/br1_metadata_core_storage_20261003/README.md)。runtime Private不重领，真正standalone controller体和含facade的根对象bootstrap仍欠。

§16.70生产Store facade及原Private通过唯一prepareStore冷入口实际收费4,520B，configure/clone共用，内部shared/limits冻结顺序保持；原new Store/new Private/两处delete owner删除，原child/accounting、lifetime和terminal task承接拒绝及最后free。四数据行验证原父真实拒绝/同父重试、cold与晚captured父硬满归费，双架十四进程7592/0/0、原压力三对66/0/0均exit0。生产净+59、Private allocator16B、backend deleter8B及120B accounting/登记为保证成本，不记纯去重，见[证据](../evidence/br1_store_root_storage_20261003/README.md)。默认/reference及嵌套heap/control仍未qualified。

§16.71生产Ledger Private/admission/control并入同Store冷allocator，原Qt强/弱控制与provider/transition consumer迁移；无physical record的receipt复用已收费authority，删除其分配及拒绝点。真实claim receipt/control72B和claim节点352B按实际请求收费，原cancel/commit/detach保留。当前生产冷根5,104B，新增584B；Private allocator16B及receipt接口8B、生产净+30为保证成本。目标14/0/0、最终双架十四进程7598/0/0、原压力三对66/0/0均exit0，原parent满额下无操作返回与最后weak free已验证，见[证据](../evidence/br1_ledger_control_storage_20261003/README.md)。默认standalone和测试heap Ledger facade仍未qualified。

**当前集中实现：** [§16.72](../92_br1_m6_m8_execution_baseline.md#cp1-concentrated-storage-delivery)已补齐当前CPU参与者的默认/standalone/process根、provider/Registry/observer/Transition本体/control、TileDataStore登记、format/oracle输入值、metadata link/map/index、source/read cache、history/backend/extent及Darwin runtime/deferred；close改用原Ledger terminal节点，删除handles/seen集合与动态诊断。同Growth原候选复验替代固定三次业务拒绝，实际free才归费。原分配/owner合同见[16组清单](../evidence/br1_cp1_concentrated_20261003/allocation-contracts.json)，已实现对象不再次领取。

**§16.73已交付：** 实际allocator暴露的冷COW准备逃逸已进入原execution回滚，同owner可重试；metadata活动guard解锁后访问及拒绝计数解锁更新已修复。原8MiB方法已覆盖producer执行和像素可见后的实际准入取消，不重新领取这一缺口。双架8086/0/0、原压力72/0/0同源，实际allocator有限首末调用链、冷根/订阅/task及COW连续拒绝和局部TSAN通过；完整资格仍开放，见[八项登记](../evidence/br1_cp1_qualification_20261003/README.md)。
**§16.74–16.80已交付：** 原seal/retention/orphan接续、clear完整范围及真实claim增长修复不重领。private enqueue现返回实际接受事实，history/read/retirement/waiter拒绝时撤回本次临时pin/activity；原terminal/tree/publication清理在停止后沿原owner完成物理free。Swapper/map不再复活零引用，age及pooler配置使用原body原子标量。CPU abort fixture观察真实Debt释放，预算拒绝政策保持。所有通过与失败绑定[本轮同源结算](../evidence/br1_cp1_terminal_convergence_20261003/README.md)，完整CP1仍未通过。

**§16.81已交付：** 原arena的capacity/reserve/live/detached/free共用实际 `sizeof(Block)`，新增独立malloc记录补齐直接block及default payload分类；provider登记/source/alias、operation/COW、九族lifecycle和worker/monitor连续EAGAIN有限端点通过，原同输入freehand保持。隔离插桩QtCore正反控制及最终七组2922/0/0越过旧锁观测反例，无suppression。[同源证据](../evidence/br1_cp1_owned_qualification_20261003/README.md)保留所有失败与边界，不能推定完整manager或CP1通过。

**§16.82已交付：** 原worker/monitor span在既有初始化/接受/join次序内去掉已付交集，32B实际本体增量沿原allocator收费；两架各34 native端点差额0，原连续EAGAIN拒绝/恢复及stop/容量目标通过。[证据](../evidence/br1_cp1_native_span_20261004/README.md)只关闭原两线程重费，不外推第一次查询的外部合并容量。

**§16.83已交付：** 原orphan与晚scope在façade消失后不再通过原pin自保，原guard/execution/外部provider继续保护真实字节；单transition不再在projected拒绝边界前构造临时数组。32行及四bpp双预算满额permanent-stop联合退出、最终4352普通/2954同源Qt七body及双架独立free成立。[全部证据和失败](../evidence/br1_cp1_orphan_terminal_20261004/README.md)保留新增UE61801，不能资格化默认abort出口。

**§16.84已取得有限资格：** 同产品双架原8MiB取消/24MiB压力body共14/0/0，已识别paid＋实际native＋启动前固定费并存观察均在界内、static paid0；原provider/operation/native和去除审计fatal替换的lifecycle共1041 handled实拒/52控制默认正常退出，加容量primary527 actual0。[当前结算](../evidence/br1_cp1_final_qualification_20261004/README.md)保留未归类/Qt/OS/TLS容量、其余联合拒绝、非Darwin、仍Pending的完整manager及十三UE/宿主abort出口，不重跑已结算有限族来替代这些差集。生产/测试/派生改动0。

**§16.85已关闭命名固定根与extent竞态：** 独立编译产物及运行计数均332B，补齐原identity/handle/guard，原两个process gate内嵌；旧完整manager实际TSAN66暴露的getter竞态沿已有读gate修复。候选及主树双架各4414/0/0，七个完整PageStore TSAN body同次2954/0/0、目标TSAN3/0/0，原EAGAIN12实拒/4恢复均actual0。新完整manager仍Pending；其余实际结果与成本以[当前证据](../evidence/br1_cp1_static_root_20261004/README.md)和[92当前裁决](../92_br1_m6_m8_execution_baseline.md#cp1-static-root-extent-delivery)为准。

**CP1/CP2已关闭，当前按§16.139和[新M6门](../92_br1_m6_m8_execution_baseline.md#m6-opportunity-gate)推进：** 已知晚拒绝、冷准备/借用均已交付，不重领；最终物理/逻辑复核保持。CPU覆盖与执行变异已定位，ABBA候选否决、完整校准仍开放；按上方实际执行条件与分辨率验证后独立事前注册，不能续采已结包到通过。来源清点未发现生产非空readyAlternates caller，自然正例/业务p、metadata驻留分母及CP0 required仍欠。原生产Fresh/H4全过；旧20%/30%失败保留，诊断组合数不授予生产资格。已完成借用/扫描/槽复用不重领，真实业务默认归CP7–CP10，GPU不扩大当前实现域，job所有权转交归CP5。

§16.72列明实现及删除完成，先前各批留下的本体/登记/bootstrap/close/runtime实现待办以它更新；历史冻结结果仍保留原范围。完整BR1目标继续，CP0、M6/M7/M8、全局TSAN、公平/原job接续及BR1-PERF仍未结算；工程人日未记录，不从轮次推算完成率。

**当前领取顺序：** 执行下表及 [92 §17](../92_br1_m6_m8_execution_baseline.md#closure-work-packages)，按 [CP代码索引](CODE_INDEX.md#closure-code-index)定位，按 [包清点](CONVERGENCE_CHECKLIST.md#closure-package-checklist)结算。copy bounds、packed/cursor add、首条direct及联合fixture、单文档压力、cursor preflight和已收敛收费控制存储不重复领取。当前 `Failed` 保留到 CP5 的真实所有权转交；不会先加 typed result 再找 consumer。

| 领取组 | 当前应做的内容 | 有限停止条件 |
|---|---|---|
| CP3 | 已知晚拒绝/冷准备/借用、§16.139执行变异诊断完成，ABBA候选否决；稳定执行条件后独立正式family；metadata同义驻留分母及CP0 required独立补证；自然正例未建立 | 旧hit4/4、miss16/16仅数值过门，正式校准2/20；新旧诊断不拼接或授资格。原Fresh/H4八桶保持，完整新门共同条件未通过 |
| CP4 | M7的共同epoch admission、全部claims、不可失败安装与实际同步consumer | 首字节后失败0，第二页冲突未写第一页，fence分布过门；不拿cursor preflight替代 |
| CP5→CP6→CP7 | 完整压力进度/真实多文档、原job接续；读/发布/operation族和复杂模式联合迁移 | 每模式的写/读/显示/失败/undo/drain与预算结果成立，兼容分支随caller迁移删除 |
| CP8 | undo delta贯穿适配，然后有界preset准备和context失效 | 普通恢复固定K无全量重建；完整依赖矩阵正确且不拖慢stroke |
| CP9→CP10 | 全API/配置收口、M8完整资格和正式BR1-PERF | 最终同源证据、保留理由、默认策略和各独立性能门全部关闭 |

任何领取若涉及 UI、tool、paintop、PaintDevice/DataManager 等主干文件，先按 [MI1–MI8 主干低耦合合同](MAINLINE_INTRUSION_POLICY.md)填写 [清点 §20](CONVERGENCE_CHECKLIST.md#mainline-intrusion-contract)。无法证明原 owner、最窄桥、关闭状态成本和退出条件时，不得以管线需要为由扩大主干 diff。

首条 direct harness 已接原 owner、display checkpoint 和 finish/cancel；联合 fixture 又证明两次 update 属于一个策略 undo 单元、递归 producer 在 finish 前排空，且 admission/像素失败信号/checkpoint/finish 均回到唯一 cancel 终点。当前源码与结果见 [92 §16.17](../92_br1_m6_m8_execution_baseline.md#direct-stroke-joint-fixture)，按 [清点 §18](CONVERGENCE_CHECKLIST.md#direct-stroke-pilot-delivery)结算。原 autobrush 的 Wash 配置不能证明 direct persistent，现已在测试资源快照前显式改为 Buildup 并断言 incremental。资源与主干对照在默认启用前完成，兼容包装按具体消费者条件删除。后续测试只覆盖实际修改的真实链/资源出口；到默认启用或新的跨模块冻结点再跑完整矩阵。

下列 15 项是完整责任库存，不是顺序全部重做的任务清单。每批写出本次观察结果、直接依赖、停止条件与暂不涉及的入口；新增阻塞按 CONVERGENCE 的反例规则进入。资源/压力和双 hash 完整验证仍是默认启用门；受控真实接线测试可先建立。

具体领取范围和批次结束条件见 [收敛清点 §3](CONVERGENCE_CHECKLIST.md#work-orders)，实现前核对 [验收断言](CONVERGENCE_CHECKLIST.md#acceptance)与 [接口处置](CONVERGENCE_CHECKLIST.md#change-disposition)。下文按 ID 提供完整责任，不能代替这次有边界的领取。

**§16.88两个实际漏项已交付：** 原VM free在munmap拒绝后沿相同base/span执行native释放，成功后归费；Mutation::Page::resetPixel直接共享原付费格式值，双架原body各172次未收费分配消失。6dd完整manager1105/0/0 actual0/reaped已结算；3c双架完整CPU2772/0/0和匹配Qt TSAN1386/0/0通过，派生门通过。未归类350/349个site已按实际栈定位owner，但TileData/pool、异常/Qt/TLS、配置、caller输出和临时值的总硬界并未因此获得。下一只取[92 §16.88四组差集](../92_br1_m6_m8_execution_baseline.md#cp1-physical-release-reset-delivery)：完整owned/外部native总硬界、其余fault及晚fence/caller共同终点、非Darwin实现与平台运行、最终源码manager和24 UE/default abort出口。已交付容量规则、6dd manager Pending及本批两个漏项不重领。[本批记录](../evidence/br1_cp1_physical_fault_20261004/README.md)。

§16.89随后结算3c完整manager实际66，KConfig测试模式全局状态竞争已由同版本插桩依赖冷负例确认，原fixture初始化修复+11行、生产0。新完整运行实际终点与上述四组共同出口继续，不能用目标控制actual0替代最终manager通过。

## 第一优先级：绘画与必要前置

### S01：补齐失败后的最终责任

- **定位 / 已有：** [TransactionData::tryEndTransaction / tryAbortTransaction](/Users/apple/krita_gpu/krita/libs/image/kis_transaction_data.cpp:225)已有结果和取消状态；[mergeToLayerThreaded](/Users/apple/krita_gpu/krita/libs/image/kis_indirect_painting_support.cpp:149)仍存在 legacy `endAndTake` 终结。不能再次从“所有事务都没有失败结果”出发重写。
- **待改段：** 沿 [01a 的 caller 清单](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01a_transaction_completion_callers.md)迁移忽略结果的 void/命令包装；为 indirect 多设备合并、interstroke 和拒绝后析构保留明确终结 owner。压力拒绝与实际执行失败分开上送，失败后不重放像素操作。
- **联动终点：** 像素入口 → painter/job 故障 → scheduler 必需后继与取消 → transaction owner → undo 命令交付。单操作回退与整笔取消不能共用含糊的失败标志；已不可取消的合并不能套用普通 freehand 取消。
- **完成判据：** 第二页、中途、finish 和 cancel 拒绝均不误登记成功 undo；晚 guard/重复取消仍只有一个终结。具体代码与验证见 [01 / S01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01_stroke_scope_and_failure.md:5)、[01b](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01b_pixel_failure_boundaries.md)。

### S02：把 mutation 生命周期从 batch 提升到 stroke

- **定位 / 已有：** [beginMutationBatch](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:846)创建新 session，复用槽按线程保存；[finishClient / finish](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:532)仍由最后 client 触发 seal。 [Session::Private](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:741)已有唯一 write set；冷热 overflow 已改稳定块，原索引的实际容量已计账且插入拒绝保持旧集合。原 slot/incarnation、guard、live 枚举及部分取消单项 claim 释放已按 [本批实现](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#reusable-slot-implementation)同步验证；首条显式 direct 开发入口已让真实 async/1px job 借用原 transaction session，正式工具与复杂模式仍未启用。受测范围借用及 managed/packed 消费者见 [S02 第四批：执行范围借用](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#execution-borrow-implementation)。原 claim/activity 的实际桶、scope/range/control block 收费和原 orphan 链见 [S02 第三批：实际准入与寿命](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-implementation)。
- **待改段：** 原 history 显式持有 session 及 cursor 消费者已见 [HS1–HS8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01f_history_owned_mutation_scope.md#history-scope-map)。沿现有 execution 范围继续补全整体 job 冷资源准入、读写 footprint、producer、current/read 和 subset seal，保持原 slot/incarnation 与 claim 身份；借用内 resident 命中和 guard 归还已按 01c §14 接局部 gate，完整 session seal/capture 与再开放已按 [CP1–CP5](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#checkpoint-implementation)提供受测能力，原 scheduler cut 已按 [SC1–SC6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01e_scheduler_cut_and_job_admission.md#scheduler-cut-map) 接线。job ID/continuation 不再作为可独立预埋的参数；只有 [API §19](API_CONVERGENCE_MAP.md#stroke-continuation-ownership-audit) 的原 job ownership transfer 能同批闭合时才接入。client/iterator 退出只归还 borrow，standalone 操作仍按原语义终结。
- **联动终点：** transaction → backend scope → scheduler job → painter/iterator → entry/短 pin → borrow 归还；freeze/finish/cancel 经 job cut 等待已接纳工作，不能持自身 borrow 等自身完成。
- **完成判据：** 跨 worker 接续、slot ABA、容器增长、晚 guard、不相交并行与重叠顺序均成立；无真实冻结时，同页 1/10/1000 dab 不重复分配/COW/seal。与 S01/S03/S04/S05 及必要资源保证共同启用，函数级改法、SS1–SS10 联动与实施批次见 [S02 / SS1–SS10：持久 session、稳定存储与 job 借用](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md)。

S02 已实施的准入子范围见 [S02 第三批：实际准入与寿命](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-implementation)；完整要求保留在 [01c §11 / J1–J8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-implementation-map)。范围执行能力已按 [S02 第四批](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#execution-borrow-implementation) 接入原 session 和 managed/packed 入口；首条 direct 开发入口现将原 transaction 非拥有绑定送到真实 async/1px painter，并在 dirty 前 checkpoint，见 [01j §6–§7](01j_real_stroke_integration.md#direct-stroke-pilot-delivery)。同一 fixture 的两次 update、一次策略 undo/redo、三步递归 drain 和四类失败终点已完成。普通 direct cursor 又已在 callback 前准备全部目标 backing，压力失败不 poison 原 history scope并可用同一 owner 重试。当前不把该边界直接接成 scheduler continuation；先完成必要终结存储、共享父额度和多文档公平。continuation 重新领取须满足 [API §19](API_CONVERGENCE_MAP.md#stroke-continuation-ownership-audit) 的同批所有权门；正式工具默认仍关闭。

### S03：将真实绘画和写后适配接到 scope

MR5/BC9 的具体代码领取见 [OP1–OP10：operation 资源准备](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#operation-storage-map)：按 A–D 批次先处理 cursor/packed 的 touched 与 changed，再处理 presence、两种 hash 的新增/删除、extent、协调安装及旁路。每项给出原 owner、拒绝终点和探针边界；触页/输出子范围已按 [OP2 实施与剩余边界](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#operation-storage-implementation) 实施，presence 已按 OP3 实施记录接入；下一段按 [HX1–HX10：hash 存储与回收](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01n_hash_storage_and_reclamation.md#hash-storage-map) 领取 wrapper/hash/GC 的原函数、引用归属与退出责任；OP5 容量已前移，删除扫描和整体协调安装继续。

[WC1–WC8：目标映射复验](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01l_write_context.md#write-context-map) 已把原事务与真实 producer 的映射值复验接到写入/checkpoint/完成上报，变化后经原取消链处理；等价 bounds 与 inactive wrap 参数有成功对照。下一段继续原 owner/job 生命周期、current/source/cut、必要资源与执行期间 metadata 稳定，不能把 WriteContext 当权限 token。

固定源及 1px sharpness 的同步消费者已按 [FC1–FC8：固定源与 sharpness](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01k_fixed_source_and_sharpness.md#fixed-cursor-map) 改为原 cursor，单一 painter owner 绑定可贯穿独立源 bitBlt 与 H/HV/V 镜像；source/selection 提前捕获，保留 wrap 首周期，Alpha Darken 统一 scalar/SIMD alpha 运算。只有测试使用的 public 显式 owner overload 已删除，同步传递收回 private helper。新增测试和完整身份见 [固定源验证记录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s03_fixed_cursor_20260928/README.md)。下一批继续 BC1–BC3/BC5–BC9 的原 owner、读选择、producer cut、终结与资源；此处不再把 scalar fixed 消费者列为未迁移，也不将它当作默认长 stroke 已启用。

函数级领取单元见 [S03 / MD1–MD7：真实 multi-dab 与 painter scope](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01g_multi_dab_and_painter_scope.md#multi-dab-map)：MD1 owner/producer → MD2 映射后页依赖 → MD3 有序 kernel → MD4 读取与 cut → MD5 终结 → MD6 必要准备 → MD7 验证。普通/镜像共用的 `addDabJobs` 已删除显式空 owner，在显式开发入口中消费 painter 的原 transaction 绑定；默认工具没有 opt-in，绑定为空。[S03 / SR1–SR7：稀疏写范围](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01h_sparse_write_footprints.md#sparse-range-map) 与 [PG1–PG8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01i_page_owned_brush_jobs.md#page-partition-map) 保留同页归属和镜像阶段次序。direct fixture 的 producer/drain 与四类失败已关闭；下一段只补 current/self-source、save 和必要资源，不据局部目标结果给默认笔刷启用 owner。

- **定位 / 已有：** [FreehandStrokeStrategy::doStrokeCallback](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/freehand_stroke.cpp:143)是业务 job 入口；[runCpuMutationOperation](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1897)在默认路径仍每 operation 建 batch/finish；显式原 memento 路径现借用持久 session；[refreshPageStorePages](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1016)已按 [MR1–MR3](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01d_metadata_refresh_and_pending_visibility.md)改为批量存在性查询及缓存失效，兼容失败回滚保留 exact-view 字节恢复。
- **待改段：** 已迁移 job 显式借用 S02 scope，并传到同步调用和必需后继；成功刷新已拆分存在性/失效/像素读取；继续完成 [MR5–MR6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01d_metadata_refresh_and_pending_visibility.md)的发布前适配存储准入、current 读与真实业务 checkpoint；已接显式 cursor 的 pending touched 适配和完整 cut 缓存失效见 [HS1–HS8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01f_history_owned_mutation_scope.md#history-scope-map)。保留中途同步查询、source/self-copy 和 MR4 的失败恢复语义。
- **联动终点：** strategy → painter/pixel operation/iterator → backend → manager 索引 → dirty/projection。按 direct/common composite、indirect/mask/source-dependent、wrapped/LoD/async 分批，独立 target 不共享可变 token。
- **完成判据：** 同 seed/输入像素一致，真实 brush 不出现无必要的 per-dab seal/COW；pen-up 计入最终 merge。只改 operation 函数不能交付，详见 [01 / S03](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01_stroke_scope_and_failure.md:41)。

### S04：显式实现读意图与完整 checkpoint

- **定位 / 已有：** [captureIteratorReadScope](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1148)、[captureReadView](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStore.cpp:2684)及 [tryDoUpdate](/Users/apple/krita_gpu/krita/libs/ui/tool/strokes/freehand_stroke.cpp:228)是选择、冻结和展示的接点。
- **待改段：** 区分 job current、operation-start source、G0 oldData 与外部 exact；在现有 seal/发布之前定义 scheduler cut 和完整 dirty delta。内部子集 seal 只服务资源窗口，不能单独推进完整 exact view。
- **联动终点：** cut 前 jobs 及必需子 jobs → 归还 borrow → checkpoint → 读选择切换 → projection/save → 释放 snapshot；cut 后 jobs 排队，显示完成不额外延长 canonical 保护。
- **完成判据：** 屏幕外页、save、异步子 job、慢 reader、取消均无半提交 exact view；保持输入量与显示工作，详见 [02 / S04](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/02_visibility_and_publication.md:5)。

### S05：把短安装边界扩到外层锁

- **定位 / 已有：** [finishOwnedTransaction](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:947)已将匿名 root 成功后的 cleanup 移出 `publicationLock`，`transactionMutex` 仍串行最终 writer；准备外移因持续读下进度回退撤回，history/checkpoint/abort/restore 外层锁仍待完成。JP4 已把页与派生 extent 接入原候选，见 [02a §9](02a_joint_publication_boundaries.md#overlay-extent-implementation)。[commitLocked](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPagePublicationCoordinator.cpp:834)和 restore 已有核心准备/安装协议。
- **待改段：** 把同一协议接到 page/surface/adapter 和真实 history/checkpoint，保留合法 immutable 选择及晚读复验。普通路径的有界重试必须先有原 owner 接续；本批固定次数拒绝已被并发写回归否定。M7 首字节后只消费已完成准备。
- **联动终点：** manager/history 锁 → backend 选择 → publication metadata/descriptor/root → adapter 索引 → 旧事务移除/清理；commit 与 restore 同时审查。
- **完成判据：** capture 两种先后次序和 head 竞争正确；测最外层 wait/hold，真实安装区间 allocator/rehash/大析构为零。仅缩核心锁不足，详见 [02 / S05](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/02_visibility_and_publication.md:22)。

### S06：补齐 M6 资格，再实现 M7

- **定位 / 已有：** [prepareWritePlanLocked](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1472)已让 native/generic 共用驻留 CPU exact alternate 生产计划；不是尚待新建的第二个 selector。legacy canonical 读/独立写缓存已有部分接线，batch borrow 与 idle/raw consumer 仍须继续迁移。
- **待改段：** 依 [03a](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md)、[03b / L1–L10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03b_legacy_cache_migration.md)完成 before 保活、身份/失配重解析、剩余 consumers、故障/epoch/资源矩阵；只消费已 Ready 的独立恢复凭据。M6 验收后，再给受控 kernel 接 epoch admission 与全部页首字节前 claims。
- **联动终点：** 唯一 selector → metadata/descriptor/预算准备 → provider claim/retag → access/cache → 原 seal/commit/cancel；取消仍从 alternate 解析旧 G，不倒写已改字节、不降低 Busy/pin 排斥条件。
- **完成判据：** M6 没有人为 before copy 且全部终结闭合；M7 遵守 ≤8 页、≤256 KiB、hold P99≤100 μs、首字节后失败零。当前 CPU 子集与局部探针不能授予完整 M6/M7。

### S07：消除重复准入和无变化对账成本

- **定位 / 已有：** [reserveBacking](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:1582)仍进入 [synchronizeBackingDomains](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageOwnerLedger.cpp:1028)；后者已有 `mayHaveBackingDomainChanges()` 提示，不能把它再列为完全缺失。
- **待改段：** S02 的同段 pending 命中直接消费既有额度；测量并缩减无变化路径的 provider 枚举/调用。非空 journal 继续按 owner 登记、revision 和 domain 准入复验，登记前观察不得提前 acknowledge。
- **联动终点：** pending 命中/新 backing → 原 budget 与 ledger → provider journal → 各真实 owner acknowledge；不得以本地布尔缓存替代跨 owner 状态。
- **完成判据：** no-change 的调用/临时分配下降，wrap、swap、多 owner 与登记前观察仍正确，详见 [03 / S07](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03_write_plans_and_hot_path.md:28)。

### S08：从有界枚举推进到有界且有进度的回收

- **定位 / 已有：** [collectSliceLocked](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageHistoryCollector.cpp:159)已用原 epoch owner 游标、有限候选和整轮 root 访问预算，失效后复验候选；保留这些正确性边界。
- **待改段：** 对持续改写导致的扫描重启补热点 admission/进度策略；为节点与字节销毁、锁持有时间、跨 store 轮转补真实预算，延后重析构时仍保留并计量其所有权。
- **联动终点：** 保护释放/按 key 发布失效 → 原扫描游标 → detach 前 exact 状态复验 → S09 实际退休 → S10 归还额度；close 取消游标且债务不消失。
- **完成判据：** 持续热点与冷页并存时均有进展，多文档公平；整轮 roots/versions/destruction 守界。已有枚举计数不能替代销毁与时间证明，详见 [04 / G1–G7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04_reclamation_and_budgets.md)。

### S09：补全退休事件上游与退出收敛

- **定位 / 已有：** [finishAttemptLocked](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageRetirementQueue.cpp:340)、[releaseRead](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp:181)、[watchTerminal](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCompletionRegistry.cpp:245)已有 CPU 事件和无信号退避消费者。
- **待改段：** 单次 `applyReadProtection/finishReadProtection` 已消费原 overflow slot，保留 claim/revision、exact identity 和 mixed sequence 原子性；局部空块归还和线程首次访问探针见 [04a §12](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#metadata-terminal-implementation)。外层空块 free、原 charge 与 close/idle 责任已按 [04a §13](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#outer-read-cleanup)接线。下一批按 [T4–T6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#terminal-cleanup)闭合整轮节点/字节/时间与其他临时对象的销毁预算、真实可达的 `retryReleasedReadsLocked/processLastUses` 拒绝接续（先按 [04a §14](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#completion-failure-atomicity)核对 owner 串行前提），以及通知/派发预备存储和 S10 计账。原上游 last-use、取消空 signal/空表清理继续使用现有记录；不要重建第二份 operation/退休权威。
- **联动终点：** 登记订阅并复验 → 最后 pin/completion → 原 ready 去重 → provider 真实终态 → ledger 释放 → S10 等待者授额；late callback 用弱身份拒绝已退出 owner。
- **完成判据：** 事件先/后到都无丢唤醒，无新编辑也可自行收敛；`idle` 与债务全清的 `drained` 分开验证，详见 [04a / R1–R10](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md)。

早期completion原子性记录见 [04a §14](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#completion-failure-atomicity)；当前prepared terminal、必要retry/task及实际producer completePrepared已按92 §16.31–16.44交付，成功后complete(false)业务恢复已删除，不再领取。下一只按本文顶部差集处理尚欠metadata/辅助/bootstrap/永久尾出口，不由局部终结保证推定完整自动进度。

读请求、lease 与 CPU/tiles3 provider 的原节点已按 [04a §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#read-storage-admission)前移到保护/pin 之前；下一批继续必要通知/派发/retry/pass 容量和原预算收费。通用写路径的 GW1–GW3、GW5 及 GW4 准备调用边界已按 [04c：通用写准入 GW1–GW7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04c_generic_write_admission.md) 接线；activity/admission 原表子范围现见 01c §12；下一段继续整个 job 的冷资源准入、metadata/descriptor/ledger 与 producer 内部故障，GW6 的实际存储收费，以及 GW7 的完整压力/性能资格。不能由原节点前移推定整个准入链完成。

### S10：把局部预算扩大为完整资源与压力契约

前台 operation 的实际资源清单和责任链见 [OP1–OP10：operation 资源准备](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01m_operation_storage_preparation.md#operation-storage-map)。特别核对 lock-free hash 删除时的回收节点、Qt 输出 buffer、新旧 extent 共存峰值；提前 reserve 和局部 scratch 收费均不能替代全部资源或共享父额度。

- **定位 / 已有：** [waitForChange/reserveLocked/commitRetaining](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:454)已删除 context 的 Qt shared control block和独立 `m_freeSlots` vector。intrusive handle 只保留小型 context 锚点+sequence；请求数组实际收费、固定 32 项，并在 controller 退出时先释放。空载预检含 context+数组+state+wake，并纳入实际 slot cache；冷候选失败/竞争输掉时先取消 wake。已有共享父总额与 wake 内嵌链继续复用；§16.26 的双架构目标结果 146/0/0 只绑定其冻结源码。当前 `prepareReservationSlot` 已把普通/父 reserve 和 waiter 数组增长接入原内嵌 reservation 与父 token，实际收费、锁外分配/free、重新复验；metadata 恰满仍可复用，实际 slot cache 不足以容纳的等待需求在登记前拒绝。最终源码结果见 [92 §16.27](../92_br1_m6_m8_execution_baseline.md#reservation-storage-admission)。
- **待改段：** 下一批按完整控制存储闭环处理 **callback capture、`QRunnable`/dispatch、retry/pass/必要终结和 inert anchor 实际内存**。slot 已由 `prepareReservationSlot` 用内嵌冷 reservation 和原父 token 收费，在 gate 外分配/free 并重新复验，见 [92 §16.27](../92_br1_m6_m8_execution_baseline.md#reservation-storage-admission)；父自身仍存活时缓存继续收费。callback/task 的分配失败须有原 owner 恢复出口；墓碑的账外尾存储须确定进程 owner 和字节/数量界。全部绑定同一退出责任后再做真实多文档压力和 [API §19](API_CONVERGENCE_MAP.md#stroke-continuation-ownership-audit) 的原 job ownership transfer。没有可取消 owner 时沿现有 `Failed`；process-global executor 不按 store 重复收费，32-request 上限不替代字节预算。
- **联动终点：** 产品 RAM/SSD 容量 → 全局/局部 reservation → allocator/物理 identity → commit/reclassify/release → 原 waiter grant → 原 job 或退休记录继续；alias 单次收费，尚被 snapshot 持有的 cache 继续收费。
- **完成判据：** tiny budget、长 stroke、多文档、慢 reader/retirement、SSD 与元数据耗尽均守界且有明确终点；完整矩阵与新源码身份重新绑定。实施关系及未验收边界见 [04b / W1–W8](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04b_budget_waiter_implementation_map.md)，不能据局部 waiter 接线启用长 scope。

## 第二优先级：Undo / redo

### U01：把 changed delta 送到最外层

- **定位 / 已有：** [MementoManager::restore](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreMementoManager.cpp:259)已有 delta；[DataManager::restoreHistory](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:465)成功后仍调用 [rebuildPageStoreIndex](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1000)，清表并全量枚举。
- **待改段：** 从原 history 结果传 changed keys、存在性/default 标志与受保护目标 view；适配索引在 root 安装前准备实际存储，安装时只增删/失效变化项。复用 S03 的索引职责分解，不复用其 current 读语义。
- **联动终点：** memento delta → backend restore → manager 索引/default → extent/cache → 用户可见更新；普通 undo 移出全量 API，保留 clone/序列化等真实全量 caller。
- **完成判据：** 固定 K 放大 N/H，普通恢复无 full export/sort/hash clear；准备失败不留下 root 与适配索引半更新，详见 [05 / U01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/05_undo_delta.md:5)。

### U02：分开 extent、像素缓存和历史回收

- **定位 / 已有：** [ExtentManager::Data::updateMin / updateMax](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTiledExtentManager.cpp:270)维护坐标边界；[MementoManager::purge](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreMementoManager.cpp:284)释放历史保护。
- **待改段：** extent 消费 U01 增删 delta，按稀疏场景实测再选择有序计数/分块摘要；像素 bounds/cache 按真实内容失效，保留中途同步查询。purge 将剩余回收交 S08/S09 有界推进。
- **联动终点：** restored delta → extent 与像素缓存各自失效 → 真实滤镜 halo/dirty；保护释放 → 回收/退休，禁止把大扫描与大析构推给下一笔首 dab。
- **完成判据：** 删除边缘 tile、巨大稀疏坐标、exact bounds、冷 undo、purge 同时绘画正确；分别测 root 安装、可见结果与 drain，详见 [05 / U02](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/05_undo_delta.md:22)。

## 第三优先级：笔刷与内容上下文

### C01：沿原 preset owner 建有界准备缓存

- **定位 / 已有：** [PresetShadowUpdater::Private / slotPresetChanged](/Users/apple/krita_gpu/krita/libs/ui/KisPresetShadowUpdater.cpp:78)维护 current preset，准备结果按 sequence 检查；完整多 key 有界复用尚需实现。
- **待改段：** 热切换命中直接使用，冷 miss 低优先准备，连续设置变更保留 debounce；key 包含 settings cookie 与真实依赖版本，完成按 key+sequence 复验。LRU 移出索引后仍被引用的 bytes 继续占 S10 额度。
- **联动终点：** UI preset/settings → 原 ShadowUpdater/resource cache → immutable resources snapshot → 新 painter；不缓存 mutable paintop、随机源或 writer 权限。
- **完成判据：** A→B→A、冷准备、旧完成、依赖变化、超额均正确；预热时 stroke 控制桶不退化，补实际 UI fixture 注册，详见 [06 / C01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/06_context_switching.md:5)。

### C02：按内容依赖复验上下文

- **定位 / 已有：** [ResourcesSnapshot 构造 / setupPainter](/Users/apple/krita_gpu/krita/libs/ui/tool/kis_resources_snapshot.cpp:66)固定本笔资源；[interstroke factory](/Users/apple/krita_gpu/krita/libs/image/KisInterstrokeDataTransactionWrapperFactory.cpp:110)已有兼容性与事务命令语义。
- **待改段：** 按 92 §12.3 逐行实现保留/失效：preset/颜色、selection、device、frame/LoD/offset/wrap、format/profile、undo/外部写、zoom/display。切换后的新 job 取得匹配实际目标的新 token，旧 stroke snapshot 不被重写。
- **联动终点：** 内容/配置变化 → 依赖 key 与 scope incarnation → 新 painter/job；interstroke 有 undo 语义的状态继续由原 transaction 管理。
- **完成判据：** 每行同时验应保留与应失效两侧；smudge、LoD、undo 正确，切笔刷不触发无必要的全层搬迁/history 清空，详见 [06 / C02](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/06_context_switching.md:20)。

## 贯穿全部优先级

### V01：将修改闭环绑定到可复现证据

- **定位 / 已有：** [Diagnostics](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisPageStoreDiagnostics_p.h:22)与现有 CPU/业务 tests 已提供部分计数和行为证据；[FreehandStrokeBenchmark](/Users/apple/krita_gpu/krita/libs/ui/tests/FreehandStrokeBenchmark.cpp:156)仍须核对 broken-test 注册和实际 replay 资格。
- **待改段：** 每批先冻结包含未跟踪生产文件的源码和真实构建身份；补同输入真实 stroke 的首 dab、steady state、P95/P99、pen-up、显示与 drain，再覆盖 undo/context。并发测试夹具日志必须自身正确，修正夹具后重新构建，旧矩阵不能代表新源码。
- **联动终点：** 修改 ID → 实际符号与 caller → 行为/故障/资源 → 主桶和控制桶 → 删除/保留适配理由 → 92 阶段裁决。旧失败样本原样保留。
- **完成判据：** 正式门、阶段门与局部能力证据分别成立；文档链接检查只证明可定位，不授予生产正确性或性能资格，详见 [07](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/07_validation_and_migration.md)。

## 每批修改的最小领取与交付格式

```text
修改 ID / 92 条款：
本批要关闭的观察问题、子范围与直接前置；停止条件：
主改函数（文件、符号、入口行）：
必须联动的 caller / override / callback：
唯一状态 owner；进入、成功、失败、取消、析构终点：
本批改变的行为；保留的未迁移入口及具体原因：
测试目标 / case / 实际命令；源码与 binary 身份：
stroke 主桶与控制桶；undo/context（如适用）：
新增/删除的复杂度及实际消费者：
未闭合项、阻塞入口/阶段与下一段代码：
92 的证据入口与阶段裁决：
```

提交审查时，从 [CODE_INDEX](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/CODE_INDEX.md)查出本批每个文件涉及的全部 ID；再从 [CHANGE_MAP](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/CHANGE_MAP.md)反查是否遗漏下游终点。修改函数、删 caller 或移动代码后，主题指南和这两个索引同时更新。

统一结果分类、比较身份和结束规则见 [CONVERGENCE §6](CONVERGENCE.md#delivery)；各批冻结验证回到 92 §15，当前裁决回到 §16。本页后续只更新对应 ID，不再追加重复“当前验证”段落。
