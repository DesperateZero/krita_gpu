# CP1 orphan scope 的最后 façade/handle 退出

产品 `61a0e28bdd1d8d6ac56f471550eb3f0e1db42b4b`，产品父 `46eab867ed37da42921c5618cc349171454fe5c7`，文档父 `159fca58`。[最终身份](final-freeze.json)核对123源输入、121编译输入及169运行/审计输入；两派生JSON在全部最终测试后刷新，测试时旧hash单列。完整CP1仍开放，M6/M7/M8正式0/3，persistent默认关闭。

原两事务、四private pages在一页Debt和provider拒绝下遗弃scope。原scope的手工Private lifetime pin留在intrusive orphan链，façade析构却停止自动重试；最后reader/provider释放后仍有原根和费用。[改前03](probe-before-03-arm64/identity.json)实际exit20，保留278,500B metadata及parent refs2；没有强制abort或手工pump。最早02的physical零断言不符合原facadeLifetime合同：外部provider仍拥有committed页；03补入真正最后provider释放，独立的refs2已证明自保环。初次编译失败及全部后续诊断均保留。

原Private增加唯一的façade消失事实，仍受原owner gate保护。façade停止唤醒后沿原scope链执行不访问provider的最终声明释放；最后scope与后台重试在原scope→owner锁序中复验同一事实，不能在最后扫描之后重新挂入自保环。活着的façade仍保留原拒绝/自动重试；晚scope先尝试原正常取消，只有façade已消失且拒绝才释放声明。exposed guard/execution仍阻止scope释放，原cold/writes/admission/control allocator负责最后实际free。未接受的物理退休不伪报成功；外部provider/实际capability仍持有原物理分配至其真正释放。

联合满额夹具另暴露真实worker异常：[repeat03](runtime-diagnostic-repeat-03/run-0.log)记录`applyOwner(key,{transition})`临时SnapshotArray control在process硬满下抛出bad_alloc，发生在原projected拒绝边界之前。现在单transition借用同步调用的const输入，序列借用原constData/count，共用原local校验、project/install和工作存储拒绝；删除单值临时export array的control/payload分配，不加另一套失败或重试政策。fixture预付原executor barrier后填满两个预算，避免后台重试在usage观察/填充准入之间改变占用；在cap下显式取消四个原scope，必须返回拒绝而不抛出，再释放原worker并执行permanent stop。

生产3文件 **+51/-23，净+28**；测试原1文件 **+120/-2**；生成JSON **+8633/-8055** 单列。唯一新增bool使用原Private padding，两架真实malloc请求仍4960B；没有新owner/queue/lock/公共API，原scope终结带来的同步释放成本不记纯去重或性能收益。图87TUs/2164APIs/27528edges/27callbacks、physical production/test 1/12，原21manifest/25ownership/16census/19外部文件ratchet保持。

最终ordinary03双架原CPU/Reference完整body四进程 **4352/0/0**，实际exit0。[Qt续验](qt-concurrency-final-02/results.json)前五个完整actual0与[Reference03](qt-reference-final-03/results.json)/[CPU03](qt-cpu-final-03/results.json)两个完整actual0在同一源码/运行物下合并为七body **2954/0/0**，匹配插桩QtCore实际加载，无suppression。Reference02的180秒outer cutoff实际-9已reaped，不能算通过；旧同Core完整Reference约234秒，补测保留全部输入，outer290秒在300秒function watchdog之前，实际219.8秒/0。这里是同源七body组合，不写一次runner全通过。

新32行覆盖四bpp × provider/metadata永久拒绝 × active/frozen × 已遗弃/晚scope，均保留晚原reader字节。原runtime stop body另覆盖四bpp的orphan＋晚scope/reader＋双预算满额＋permanent拒绝/stop组合，原四close控制仍保留。独立final02双架actual0、parent退回原19,968B暖高水位且refs1/reserved0，static之后paid live0/overflow0；固定executor、外部provider及暖controller实际存活时不写零尾费用。旧final01只资格化其当时源码，不借给最后metadata修复。

失败清单：ordinary01四actual0但与最终relink重叠，最终hash检查拒绝，Inconclusive；ordinary02 x86原worker bad_alloc/default abort留下新UE **61801**，runner一次SIGKILL仍未reap；Qt01在已知失败后对自己正在运行的Reference诊断SIGTERM，实际-15/reaped，不是timeout或通过；diagnostic12在源码更新时结束，最终身份断言失败，不能当当前资格；所有诊断terminate/abort handler只用于安全记录，不能资格化默认失败退出。最终运行没有新增UE，但累计十三UE仍保留，宿主/应用服务器未被自动清理。

下一差集仍是四组：全owned actual request/capacity/control/TLS/static、reserved/live/并存peak/physical free与总硬界及初次native外部合并；其余真实node/control/task拒绝与read/capture/history/publication/retirement/close、晚fence/caller联合终点；Qt/OS/usable/TLS和非Darwin边界；完整manager TSAN及十三UE/default失败宿主出口。已关闭原arena/两线程重费/这组scope退出和单transition临时数组不重新领取；CP5 continuation/fairness、CP10正式性能归原包。
