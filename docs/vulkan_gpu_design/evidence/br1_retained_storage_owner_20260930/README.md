# CP1 实际存储收费寿命收口

执行入口为 [92 §16.30](../../92_br1_m6_m8_execution_baseline.md#retained-storage-owner)。本轮先核对实际 owner 与 API：原 wake reset 和 controller 析构会提前返还仍由 monitor/inert handle 持有的真实存储费用；读、退休通知的 shared 弱控制块也没有收费寿命。选择补齐这项 CP1 必需能力，并同批删除提前退费、raw storageBudget 字段及原 ensureWakeContextLocked 包装。原 executor、原 budget 和语义 owner 继续承担责任。

## 已落地的边界

既有 `KisMutationStorageAllocator` 增加 retained 模式，真实 controller 懒准备一个收费寿命 owner。每个真实 allocation 及 allocator handle 持有该 owner；普通 raw 模式不加 allocation header，仍要求原 controller 存活。retained 模式实际使用原 MetadataArena reserve/commit，按 allocator 请求的容量收费，`allocate_shared` 包含实际弱控制块。allocator 对象新增一个 intrusive 指针，其所在实际分配的大小一并收费；不将这一成本宣称为零。

controller 退出先关闭新 retained 分配，释放原 requests/array/slots，再把原共享父预算和原 child 注册交给收费寿命 owner。controller 后的实际分配只允许释放；存储物理释放后才退费，最后 owner 本体物理释放后才注销原 child。残留弱控制块、inert handle 和 monitor callback 继续占用原全局父额度，不能让弱父池另建容量绕过硬界；它们不 pin PageStore、payload 或 mutation 权限。孤立 controller 没有共享父时仍是其局部预算域，不据此授予产品全局资格。

| 实际对象 | 原责任与当前收费 | 尚未关闭的范围 |
|---|---|---|
| waiter Context、prepared wake、本轮预算化的 typed task | 复用一个 retained accounting owner；monitor/inert 尾仍存活时继续收费 | waiter 的外置 std::function capture、未传预算的 waiter/退休/history task 尚欠 |
| read ActiveReadRecord 及其弱控制块 | allocate_shared 经实际 retained allocator；active map node 经原 raw allocator | requests、其他临时容器、provider/registry 控制对象未整体结算 |
| read last-use context/wake | 冷准备在原 store owner gate 外，安装前重验 closing/stop/active identity；失败保留原记录 | callback 外置 capture、pass scratch 和完整耗尽恢复未结算 |
| retirement Wait/WakeContext/grant control block、retry DelayState | 原 queue 的 allocate_shared 复用预算；weak 身份不拥有 PageStore，冷 context 在 queue gate 外准备 | deadline multimap node/capture、record list/orphan storage、pass/task/terminal/runtime 仍欠 |

读 resolve 在真实 record/node 冷准备前将原 request 标成 Resolving，离开原 owner gate 准备；拒绝回到 Pending，provider 尚未进入。准备后沿原 provider access 和 owner identity 重验，失败候选在 owner gate 外释放。cancel/close 在遍历 active map 前准备 context，避免解锁期间迭代失效。原队列物理 debt 不因通知收费拒绝而丢失。

## 目标结果与失败保留

最终运行表以 [results.json](results.json) 为准，测试在最后构建之后绑定最终源码和实际二进制。双架构 CPU 全组各 **1246/0/0**、Reference 全组各 **653/0/0**、原 Freehand 压力/取消各 **4/0/0**，合计 **3806 passed**。新增 Reference 结果覆盖弱控制块与原父容量硬界、32 次并发 controller 退出/对齐存储释放、monitor callback 执行中 controller 退出及最后父寿命释放。原 wake 测试现在明确断言 in-flight wake 继续收费，真正释放后才退费；slot cache 和 owner cache 存活时仍计费。

运行 argv/退出码/架构保留于 results；UI 使用 offscreen、seed=12345 和 `_install`/`_build/bin` 路径，24 MiB 成功与 8 MiB 取消预算未改。新增测试中的 semaphore 只建立析构交错，不代表生产 callback 可以阻塞 monitor，也不是 TSAN 资格。

[初始结果](results-initial.json) 和 `initial/` 原样保留：并发 retained 分配实际增长父 slot cache；wake 缓存以及 in-flight 存储过去被误断言提前返还；failed-read cleanup 冷准备费用混进保护块释放测量。分别预热实际 slot/cold resolve，保留实际收费 cache，等待物理异步释放，未放宽产品硬界或三块保护存储释放断言。`before-restore-fixture/` 保留随后 x86_64 的恢复夹具失败：ticket 完成后自动 pass 与显式 drain 竞争，显式调用只拿到 1/2 项。该夹具在初始化前关闭自动退休，明确让原显式 drain 拥有两项；其他自主进度测试继续启用自动退休。编译和这些必要回修后才冻结结果，没有为每个 hunk 扩跑历史矩阵。

## 身份与未关闭条件

[architecture.log](architecture.log)、[callgraph.log](callgraph.log)、[旧身份失配](architecture-initial.log)、[前](baseline-before.json)/[后](baseline-after.json) 架构身份明确实际源码变化。只刷新身份和原 admission 的 ownership 说明，不放宽 intrusion ratchet；UI/tool/paintop/painter/PaintDevice/scheduler 本批生产改动及 public/protected API 净增均为 **0**。逐方法替代见 [API](../../br1_modification_guide/API_CONVERGENCE_MAP.md#retained-storage-api-delivery)，实际 caller 与剩余改动见 [CODE_INDEX](../../br1_modification_guide/CODE_INDEX.md#retained-storage-code-index)。

[source-sha256.txt](source-sha256.txt)、[runtime-sha256.txt](runtime-sha256.txt)、[HEAD](head.txt) 和 [文档/结果校验](document-validation.json) 标识当前脏工作树。source-union.diff 为列明文件相对 HEAD 的累计差异，包含之前实现，不能算作本轮净增。构建日志继续出现 Ninja premature-end 恢复，属于保留的工具事实；本批最后构建后才运行目标、冻结哈希，没有再次启动所谓 no-op 构建改变 binary 身份。

**CP1 仍未整体结算；M6/M7/M8 正式资格仍为 0/3，默认入口关闭。** 全控制存储清单中的 capture/map/list/scratch、剩余 task、必要 terminal/runtime 收费、硬满时必要终结与自主进度必须同一 CP1 包完成；下一段从这些真实消费者和必需冷预留端点推进，不重写已经收敛的通知服务。CP0 同依赖 upstream、全局公平、原 job 接续、正式性能与 TSAN 未获本批资格。
