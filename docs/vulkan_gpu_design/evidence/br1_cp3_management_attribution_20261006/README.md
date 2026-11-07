# CP3 管理成本：逐对象预算与 allocator 保活归因（2026-10-06）

当前 public Fresh K16 的管理成本已有两个具体集中点：**每个控制分配重复执行完整预算准入/两级结算，以及工作值传播 retained allocator 时的保活引用周转**。逐页 acquire 是净增成本最大的区域，canonical commit 和底层堆分配反而比固定 M5 明显减少。不能再用“malloc 多”“读比较变慢”或“发布都昂贵”概括剩余回退。

产品保持 `6ffe097909e23adf3afd229a2a14e93986fae00b`，固定 M5 为 `5173c807c87bb1619325249a07a8b4f4f8f09f09`。原正式结果、门槛及安全结算不变，M6 仍未通过。此处为本机 arm64 的成本定位，不能推广成 Rosetta/native handoff/真实 stroke 的因果结果。

## 证据口径

- [CPU 协议](protocol.json)：原 `kis_tiles3_cpu_baseline_test:testSharedBaseline:write-n1024-k16-b4`，原库/原 fixture 无插桩，6 s 吞吐循环；实际 init marker 后 500 ms 启动 Time Profiler，2 s 记录；两个块 M5→current、current→M5，4 个顺序进程。
- [CPU 结果](cpu-attribution.json)、[实际 profiler 设置](profile-metadata.json)：Time Profiler `record-waiting-threads=0`，`time-sample all-thread-states=NO`，导出 `Running` 行，每条权重 1 ms。四份主线程栈全部落在原 timed write lambda，分别有 1,950/2,031/2,101/1,901 个主线程样本，没有 setup/validation/teardown 样本混入。后台单列，不加入主线程分母。
- [计数协议](count-protocol.json)、[全部 8 个有效进程](count2-results.json)、[计数与扰动分析](management-counts.json)：独立复制一个 budget TU 加 TLS 入口计数，用原 public-work 工作负载；N1024、K1/K16、B4、height1、250 ms、两个次序平衡块，每行 OFF/ON。reset/read 均在 first/steady 计时之外，无逐调用时钟。实际读写量、像素、extent、退出、库选择、前后源/运行库身份全部通过。
- 首次计数尝试只有一个 control 进程，像素通过但因 `arch` 剥离继承的 `DYLD_*`，没有实际库加载见证；按协议停止并保留 [原协议](count-protocol-first-attempt.json)、[原 runner](run_counts_first_attempt.py)、[失败记录](count-results.json)。修正为在 `arch` 之后用 `/usr/bin/env` 设置变量，再执行新的 8 进程批次。总计保留 4 个 CPU 进程和 9 个计数尝试，没有删失败或补入正式统计。

CPU 百分比来自采样权重。下表的 μs/op 是把 **2 s 的 CPU 样本比例乘以完整 6 s 的主线程 CPU/op**，需要循环内工作混合稳定；只作量级投影，不是无扰动的逐阶段时钟，更不是 wall/锁等待。只有两个块，不声称置信门通过。

单样本只归入一个 mechanism；malloc 子调用单列，泛型 mutex/atomic/container helper 归到最近的具体语义 owner。父子 inclusive 上下文另列，不能加到 mechanism 表。未符号化 leaf 权重保留并按已有 caller 分类：current 2.46%/3.14%，M5 3.85%/3.63%。后台 M5 有 35/33 个空栈样本，也保留；不把它们当有名称的管理成本。

## 1. 新增成本集中在预算与保活链

| 互斥 CPU mechanism | current 占主线程 CPU | current 约 μs/op | M5 约 μs/op |
|---|---:|---:|---:|
| 预算政策与账本 | 12.95%–14.71% | 31.95–35.78 | 3.53–3.63 |
| 控制存储 owner 与收费衔接 | 12.52%–12.95% | 30.46–31.95 | 无此 retained storage 链 |
| 底层物理堆分配/释放 | 12.31%–14.66% | 30.37–35.67 | 64.79–65.43 |
| metadata / working state（上述机制已排除） | 13.18%–15.02% | 32.08–37.05 | 31.09–32.94 |
| provider / native 生命周期（上述机制已排除） | 7.58%–7.95% | 18.71–19.34 | 7.07–7.60 |
| 实际 TileData 像素 copy leaf | 3.00%–3.69% | 7.30–9.11 | 8.55–9.98 |

预算与 storage owner 合计 current **25.90%–27.23%，约 63.9–66.2 μs/op**。这不是全可删除成本，也不能直接拿它抵扣正式 wall 缺口。M5 没有同样的 control capacity/late accounting 实现；不能为复现 M5 的低成本取消已经关闭的 CP1 预算和尾释放保证。

其中单一 `fitsLocked` leaf 已占 **11.82%/12.99%**，约 **29.2/31.6 μs/op**；它是预算桶的子集，不能再与上表相加。`kisAllocateMutationStorage` inclusive 是 23.39%/24.42%，包括预算与 heap 子调用，也不能相加。

### 逐对象完整准入与两级结算

[原 `fitsLocked`](../../../../krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:492) 为每次请求计算 class/domain limits，遍历 7 budget classes、4 domains，再检查 aggregate 和 durable SSD。成功的单一 MetadataArena/CpuRam 请求也走这条完整政策。

[原 control allocator](../../../../krita/libs/image/pagestore/KisPageWriteCoordinator.cpp:2030) 对一个实际 size-class capacity：先 parent prepare，再 local prepare，物理分配后 local settle、parent settle。两级各取锁、查账、检查政策；settle 更新 reserved/live、父 child 账与 waiter 通知。retained allocation 还经过 storage owner gate/容量/引用；free 先物理释放，再把 live 费用归回两级账本。CPU 样本同时出现在工作值、provider adoption、读 link、metadata publication 和 begin/finish 的收费来源，不是只集中在一个 provider 容器。

### 实际调用数量

下表为 steady 主线程计数除以 completed op 的范围，异步清理的精确落点会带来少量非整数；不是全进程最终 drain 的创建/释放平衡表。

| 每次公开 partial write 的入口/事件 | K1 | K16 |
|---|---:|---:|
| `kisAllocateMutationStorage` 请求 | 82.005–82.041 | 523.993–523.999 |
| 经 retained storage owner 的分配 | 55.005–55.042 | 338.993–338.999 |
| local prepare；parent prepare 各自 | 68.005–68.041 | 445.993–445.999 |
| local settle；parent settle 各自 | 68.005–68.041 | 445.993–445.999 |
| 完整 `fitsLocked` 检查 | 153.010–153.084 | 987.987–987.998 |
| storage owner `deref` | 571.037–571.312 | 6,157.023–6,157.033 |
| retained storage 实际 deallocate 入口 | 15.002–15.015 | 48.008–48.011 |
| local releaseLive；parent releaseLive 各自 | 26.003–26.015 | 108.008–108.011 |

K16 的约 446 个两级 local/parent prepare 已解释约 **892 次**完整检查，余约 96 次来自其他 budget admission；每个计数区间的 prepare/settle 四列严格相等。因此 988 次不是“16 页产生 16 次预算检查”，而是细粒度控制存储触发的调用放大。

所有 K16 区间仍精确为每 op 16 次 native foreground duplicate、256 KiB before-copy、16 generation/seal、1 session/commit；输入仍只有 4 KiB，preclone/default/full initialization 为 0。这里约 524 是原 public steady control 请求入口，**不能与旧 native cold-operation 的 490 个 malloc interposition 请求相减**。

### allocator 保活引用周转

[retained allocator](../../../../krita/libs/image/pagestore/KisMutationStorage_p.h:100) 把 owner 的 intrusive pointer 随 container allocator 拷贝、rebind 和销毁传播；[working value](../../../../krita/libs/image/pagestore/KisPageStateMachine_p.h:22) 的 replicas/readLeases/pendingLastUses/capturedReadViews 等嵌套值都承接它。即使小数组容量没有真正分配，allocator 临时值仍可能增减 owner 引用。

约 6,157 次 `deref` 不是 6,157 次 free：同窗口 retained deallocation 仅约 48 次；`deref` 函数逐次执行原子 fetch_sub，大部分仅减少引用。未插桩 CPU profile 的 `deref` leaf 占 3.55%/3.43%，约 8.7/8.3 μs/op，主要 caller 是 `applyProjectedSequence`、working replica/result、publication preparation。它是 storage owner 桶中的可识别子集，不能重复相加，也不能把 6,157 当物理分配量。

这支持审查“短命工作值是否有必要反复拥有同一 retained allocator”，但尚未证明哪些引用可以删除。实际弱控制/晚 callback/脱离 controller 的最后 deallocation 必须继续保活原 accounting owner。

## 2. 净回退发生在哪个区域

| 互斥原调用区域 | M5 约 CPU μs/op | current 约 CPU μs/op | 配对方向 |
|---|---:|---:|---|
| page acquire / beginWrite | 72.6–77.6 | 112.9–113.0 | 增约 35–40 |
| adapter begin/finish/其他 | 23.8–25.5 | 41.7–43.6 | 增约 18 |
| canonical commit | 68.1–75.3 | 45.7–50.8 | 减约 17–30 |
| seal | 34.2–36.8 | 27.3–33.5 | 减约 3–7 |
| before-read 整段 | 12.0 | 10.5–10.9 | 略减 |

完整主线程 CPU/op：M5 222.26/215.69，current 246.70/243.30；同块差额约 **24.44/27.60 μs**。可见分配/发布收敛确实降低了 heap、commit、seal 和 epoch root 的成本，但新增的收费/保活链及逐页 provider 生命周期抵消了收益。这里的区域表与 mechanism 表是同一批样本的两个视角，不能跨表相加。

读 link 的安装 current inclusive 2.19%–2.66%，M5 0.26%–0.42%，源码也确认新 generation 冷发现会创建收费 link/map node。但 **before-read 整段 CPU 并未增加**；因此此前 opt-in compare inclusive 的高值不能据此认定为当前净回退主因。必须按完整 read endpoint 判断。

## 3. provider 和共同发布的定位边界

[prepareAdoption](../../../../krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:680) 对一个新 physical backing 分别准备 logical allocation node、physical payload index node、slot index node、stable binding shared allocation，并有 observer 登记及 completion 等另外的真实消费者。它们都有实际生命周期和容量收费；logical handle 与 physical backing 不是同基数。

该函数 inclusive current 5.37%/6.19%，约 13.3/15.1 μs/op，已包含其中的预算/heap/binding 准备。只改这几个节点，没有证据可以独自承担正式 Fresh K16 约 21.8 μs wall 缺口；该段也不可能全部删除。优先目标应是**原全链条准入/容量结算/allocator 传播责任中的重复工作**，不是先决定重写一个 map。

publication 仍需要独立 claim、revision、保护和失败取消；净 commit 已改善。对于 native handoff，旧 cuts 已定位 acquire/seal/commit，但本轮没有它的 CPU 互斥账，不能把 public 64–66 μs 投影直接搬去证明 handoff 30% 可达。共同成本被优化时 Fresh 分母也改变，沿用[前一可达性预算](../br1_cp3_cost_model_20261006/README.md)。

## 4. 可以选择的下一有限候选

1. 在原同步控制存储责任内审查一组已知实际容量的准备/结算：能否减少重复的全矩阵准入和两级锁/账本往返，同时完整保持 actual capacity、parent child 费用、限额变化、prior waiter fairness、失败 rollback 和 late free。先给合法等价删除清单与预期减少的调用数量，不引入第二预算 owner、不取消收费、不事后追认通过。
2. 在原 working value / projection / publication 责任内清点 retained allocator 的真正逃逸位置；对于始终被同一原 owner 保活的短命值，审查能否降低重复引用传播。保留真实 tail accounting 与 moved-from allocator 可重用语义，不能由“很少 heap 分配”推定引用无用。
3. 有等价候选后，做有限因果 ON/OFF：同输入、实际 copy/session/commit 不变；验证预测的 prepare/fits/ref 周转是否下降，再看未插桩 CPU、原 wall 和后台工作。若调用减少但 CPU/吞吐不跟随，修正模型并停止该猜测，不能把采样占比当收益承诺。

当前已足以否定“没有可定位集中点，只能继续零散微调”；尚不足以宣告完整成本账闭合。锁等待的 wall、后台最终 drain、调用数量的 M5 同口径差分、Rosetta 和 native handoff 的机制账、真实 stroke 的敏感度仍开放。

## 扰动、复核与复现

计数 ON/OFF 的 K16 wall 偏移 +7.53%/+0.48%，thread CPU +7.49%/+1.33%；K1 wall +3.09%/+2.89%。因此计数库只授予调用数量，计时不替代正式结果。CPU 份额则来自未插桩原库；CPU recording 自身仍有采样扰动，不把其 throughput 当新的正式 baseline。

`analyze_cpu.py` 检查实际 schema、Running、1 ms 权重、write lambda、前后身份及互斥总和；`analyze_counts.py` 检查所有有效进程、OFF=0、实际 pixels/work counters、四套 prepare/settle 相等、两级 release 相等和相同端点。复制 TU 仅新增 TLS entry counter 和两条诊断 getter，374 个其他实际对象复用，原预算算法不变；[精确 patch](diagnostic-diff.patch)、build commands/identity 与所有失败在清单内。

`raw-evidence.tar.gz` 只包含 Time Profiler CPU table XML 和原日志，SHA 在 `raw-manifest.json`；完整 `.trace`、含宿主环境的 TOC、对象/诊断库/可执行文件不进 Git。所有局部 binary 仍在本机原路径。原始表可解包后重跑 `analyze_cpu.py`，计数结果可重跑 `analyze_counts.py`；重新构建时把绑定的产品 budget 源复制到本目录同名文件，再应用 `diagnostic-diff.patch`，执行两个 build helper。任何重新运行另建输出目录并预注册，不覆盖本批。

最终清单 `evidence-manifest.json` 绑定协议、分析源、派生数据、每个进程结果与身份、构建命令/日志归档。代码没有产品改动，未重复执行已通过的产品安全矩阵或完整正式性能矩阵。
