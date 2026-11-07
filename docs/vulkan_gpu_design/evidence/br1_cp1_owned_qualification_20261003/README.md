# CP1 实际 owned 请求与可观测 Qt 续验

本包起于 2026-10-03，运行跨至 2026-10-04。产品 `d7e91efc39d965be49c748859fd384f91cda2c64`，产品父 `406bacb448997a2b63bf2d452a0a71d90587abdd`，文档父 `bf69fa0b654aef269e53f9b09aebde65f7391009`；完整 CP1 仍开放。产品只改原 arena 计费单位及原统计断言，不新增 owner、队列、线程、锁、状态或 PageStore 公共 API。提交 blob、最终运行和审计输入绑定 [final-freeze.json](final-freeze.json)。

## 已确认的改动与独立证据

`BlockBytes` 继续决定 slot 几何，原 `blockByteSize()` 改为 `sizeof(Block)`。容量预检、attach、live 统计、detached 费用及释放全部消费这一原单位；原 MetadataArenaGrowth 预留本来就使用此入口，不再按名义大小多收费。原 Reference causal 断言同步使用实际单位。

| 原 arena | 原名义费 | 实际 `new Block` 请求 | detached 后仍可观察 | 最后 physical free |
|---|---:|---:|---|---|
| version | 16,384B | 16,328B | 同请求 | 原地址已无记录 |
| replica | 32,768B | 32,696B | 同请求 | 原地址已无记录 |
| overflow | 16,384B | 16,352B | 同请求 | 原地址已无记录 |

原最大容量及少 1B 两种拒绝都保留未接受候选。独立 audit 固定表拦截真实 malloc/calloc/realloc/alignment/free，包含此前漏识别的直接 metadata block 和默认读 payload；原 malloc 12,345B live/free 正控制保留。`owned-ledger-probe.cpp` 在四 bpp 的默认缓冲、controller 先退出、真实九页私有写入、发布/旧 reader、facade 先退出、最后 reader/free，以及 cold/stop 共 34 个静止端点核对。

两架均满足 `parent Metadata.live = observed paid heap + process counter - observed process heap` 且 reserved=0；此式只补齐 heap 请求与原 process 计数的结合，**不是独立 native 精确总额证明**。默认 payload 通过 OptionalCache 镜像进父 Metadata；裸缓冲可晚于 child/controller，最后释放原费用，未发现需另建释放 owner 的依据。对账输出、实际 requested byte、费用及物理地址由 `probe-ledger-native-04-{arm64,x86_64}` 保存。

## native 实际边界和保留的反例

仅在审计 dylib 使用并链原 hook 的 pthread introspection，记录实际 control/TLS mapping 请求；生产不依赖该调试 API。[Apple API 明确限定为调试/内省用途](https://github.com/apple-oss-distributions/libpthread/blob/main/include/pthread/introspection.h)。custom-stack 分配/释放的源码依据见 [Apple pthread 原实现](https://github.com/apple-oss-distributions/libpthread/blob/main/src/pthread.c)。

arm64 两个原 runtime 线程各请求 16,384B，但 `mach_vm_region` 返回相邻合并区域 16,384/32,768B，原计数累计 49,152B，实际为 32,768B；多收 16,384B。原 `ReclamationThread::start` 把整个区域当本线程请求，需要在该 owner 收敛 native 计费政策。x86_64 本次每线程请求 8,192B，费用合计 16,384B，无同样合并差额；不能外推所有地址布局。每次 join 后查询原地址均 unmapped，归费时点的这组 physical free 有直接证据。

`native-region-probe.cpp` 两架各三轮四个 custom-stack 线程并存，独立 hook 记录每个真实请求。arm64 的 basic 和 recurse 查询同样返回 16/32/48/64KiB，recurse object ID/offset 也已合并；x86_64 本次均保持8KiB独立区域。两个 probe actual0，只证明公开递归查询不能恢复被合并的分配边界；不把 SDK opaque sizeof8192B 当所有 OS/runtime 的真实请求保证。

`native-fault-probe.cpp` 在原 pthread_create 边界注入 EAGAIN：worker 和 monitor 各连续三次拒绝，再原入口重试/取消/stop。两架十二次拒绝均原费用回到准备前，回调零次；四个正常控制退出。原冷 heap/custom stack/64KiB native preparation 不遗留，实际退出日志保留；这不等于 OS 真耗尽线程或默认 abort 退出资格。

## 真实分配拒绝

`provider-fault-probe.cpp` 覆盖 provider 登记节点、domain observer vector、source control 和 immutable alias 实际请求。两架四 bpp 共 64 次 malloc 拒绝、24 个正控制；未接受时原 provider/源仍有效，解除拒绝使用新的 operation ID 恢复，旧源像素不变。source control 的 bad_alloc 由原调用边界接住，不能称该 API 已改为不抛异常。初轮 alias 重试误复用已终结的 operation ID，保留 actual15；修正的是 audit caller，不改生产身份政策。

复用原 operation/COW sweep，仅扩展实际 owner 分类：每架 234 次 operation 拒绝、3 个正控制、1 个 absent site；连续 COW 拒绝、原 private 准入、发布/像素及 close 检查全部退出 0。拒绝覆盖是有限第一/最后调用链，不能替代 read/capture/history/publication/retirement/close 联合永久拒绝、晚 fence 及 caller transaction 全部出口。

原九族 lifecycle body/输入和第一/最后实际 malloc 策略保持；扩展分类后两架 515 个隔离进程，497 次真实拒绝、18 个正控制，全部 exit0、零失败。checkpoint/capture/default-read/commit/rollback/release 有本次实际调用点，read/purge/close 本次目标为零，只记正常控制；不把 absent 当拒绝覆盖。接受后的原 publication installs 保持，不将清理准备拒绝改报未发布；未接受候选沿原 ID/owner 重试。生命周期探针的 abort/terminate audit handler 不构成默认失败退出证据。

原六个 freehand 方法的 body/输入/worker/显示/drain 保持，audit 分类扩展后每架 12/0/0、exit0、overflow0。requested heap peak arm64/x86_64 为 99,160,175/98,887,910B，paid 请求子集 peak 13,448,338/13,151,954B；这些 peak 跨方法/政策且不含全部 native/external/TLS，不能直接与某一 8MiB 上限比较。main 后 paid 为 672/680B、原 process counter 764/772B，static 后 paid0。旧较小 paid peak 是漏识别的子集，不能作为新分类对照。

## Qt TSAN 可观测依赖

隔离构建匹配现行 Qt 6.8.0 的 c3ccedb3057b5eda84653887954572f016f1157a QtCore，仅 arm64，Core 使用 ThreadSanitizer；不覆盖 `_install`。库 SHA256 `5325ae35efbbd9d8b419bd23ddd30c83a23e03a3f0e3b4b8c9e1c6eeccfeab10`。完整 21,864 个 Qt source 文件在初次构建/控制后建立冻结，随后 ninja Core no-op、库及源码不变；没有初构建前 source hash 的虚构记录。

`qt-observability-control.cpp` 的 QMutex/条件等待与 QReadWriteLock clean actual0；同二进制去锁后真实竞态 actual66。产品日志通过 dyld 路径确认加载插桩 Core。系统 arch 启动器会剥掉 DYLD 配置，因此产品 TSAN 直接运行 arm64 executable，明确沿用现行 Qt plugins；无 suppression。目标 extent 并发/default-budget 共7/0/0、exit0，已跨过原观测反例。

七组初验 2922/0/0；最终依赖重建包含 ResidentRead 旧 object 和 Brush/UI/transaction 等依赖，重建后 ResidentRead 补验 221/0/0。最终统一七组 `qt-current-concurrency-final-02` 共 2922/0/0、七进程全部 actual0，源码/运行库不变且均实际加载插桩 Core。整 manager 第一轮 300s 外超时 actual-9/reap；同源码第二轮被原 QtTest 300s 单函数 watchdog 在 stressTest 终止，此前1098通过，新增 UE PID23256。日志、原 seed/worker 和采样保留；sample 显示真实 stress 工作，没有削减任务。

后续 `qt-current-manager-full-02` 仅把 QtTest function timeout 改为1,200,000ms，外时限1800s；原body、48任务/16线程、每任务100000 cycles、seed12345、输入/断言保持。采样显示真实stress读写/history回收，运行1302.4s仍未结束；在已知会产生UE的watchdog/QFATAL前，按记录的诊断截止终止本进程，actual-9且已reap。此前1098项通过只是prefix，完整manager仍Inconclusive；该主动截止不是runner超时，也未产生通过的Totals，原因和actual wait分列于该目录。后续需在完整最终候选以外时限先于watchdog的安排结清，不能反复制造未reap退出。

插桩 Qt plugins 初次路径遗漏触发 QFATAL，新增 UE PID16996，实际仍未 reap。旧十 UE 保留，新两 UE 分列；没有杀 app-server、宿主或重启系统。产品 stop 正常退出不能覆盖默认失败出口。

普通最终双架 22 进程完整矩阵 8244/0/0，原压力三对 72/0/0，均实际 exit0，冻结于前包的 `owned-matrix-final-01` / `owned-pressure-final-01`。它们与本包产品绑定，不能自动授予后续修改资格。

最终provider/operation又使用最后审计器复验同一body，两架分别32实拒/12控制和234实拒/3控制/1 absent；`probe-*-final-*` 保存完整cpp输入快照，避免把早轮后来变更的审计源称为同一最终输入。早轮的hash/二进制/所有失败保留。

## 冻结与实际成本

生产一文件+11/-9净+2，测试一文件+6/-2净+4；对象布局、arena slot几何和上层API新增均为零。生成两JSON +4416/-4326 单列，图87TUs/2164APIs/27464edges/27callbacks，原21manifest/25ownership/16census/19外部文件ratchet保持。旧checkpoint检查actual1只因两处source checkpoint过期；更新派生checkpoint后actual0，不提高ceiling。

最终源输入合计123，其中121编译输入匹配实际测试与产品blob；两派生JSON在测试后刷新，旧hash保留在 `tested_sources`，不宣称其新字节已用于此前运行。复用普通runner只冻结原116项，Qt/native/probe冻结完整123项，该区别在每个结果保留。原固定QtCore完整source另计21864项，冻结是在首次构建/控制之后建立；final核验源码仍未改变。最终280个运行物/配置及审计输入逐项核对，未把初期runner schema假设错误掩盖为产品失败或通过；全部freeze失败日志保留，最终核验以最后成功日志为准。

## 剩余完整 CP1 出口

1. 原 native owner 的合并区域重收费；全部 owned/request/capacity/control/TLS/static 的独立逐笔、并存 peak、reserved/live/physical free 和总硬界。
2. 其余实际 node/control/task/alias/fault 端点及 read/capture/history/publication/retirement/close 联合拒绝、晚 fence、caller transaction 终结；已验证的 finite sweep 和停止后组合不重领。
3. Qt/OS/usable/TLS 外部容量边界及非 Darwin 运行证据。本机仅取得 Darwin arm64/Rosetta，已询问可用的非 Darwin 环境，未假定存在。
4. 完整可观测 manager TSAN 终点、旧十和新两 UE 宿主/默认失败退出。M6/M7/M8 正式0/3，persistent 默认关闭；CP5 continuation/fairness 与 CP10 性能仍属原后续包。
