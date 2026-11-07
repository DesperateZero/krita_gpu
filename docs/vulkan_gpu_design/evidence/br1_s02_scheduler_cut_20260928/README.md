# S02 第七批：scheduler checkpoint 切点

日期：2026-09-28。唯一阶段入口为 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)；逐段要求、函数及后续责任见 [01e / SC1–SC6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01e_scheduler_cut_and_job_admission.md)。本批把原 job 队列与前批的 session checkpoint 能力联合验证；业务持久 scope、完整 job 身份/读写 footprint 和 producer 接线尚未完成。

## 1. 身份与验证范围

HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含未跟踪生产/测试文件的源码差异 SHA-256：`6e99c2bcbf4d0b9af8c45bc7079394ed4ba9d69568655a716f68f477ea6b84fb`。

最终资格由 [matrix manifest](checks-01/manifest.json)、[源码/二进制 identity](checks-01/identity.json)、[源码差异](checks-01/source.patch)及 [绑定检查](evidence-scope.json)共同给出，不能由定向测试数代替完整矩阵。最终同源码 17 CPU/业务目标 × arm64/x86_64 为 **6,646 passed、0 failed、0 skipped**；结构门与六项工具自测通过，最后构建 no work。[本批代码增量](scheduler-cut-code.patch)只包含相对上一批快照的本次修改。

[36 次继承探针](probes-manifest-01.json)在本批源码/image 下重新编译运行并全部通过，涉及安装、稳定存储、准入、execution、metadata refresh 和 session checkpoint。它们不测量新 scheduler 切点的请求分配量或等待时延；未授予切点零分配、尾延迟或真实 stroke 性能资格。各 `install-*-final-01-identity.json` 保存命令、环境、探针/interposer 源码和哈希。

[调用图](graph-01.log)：85 个翻译单元，1,785 APIs / 18,331 edges / 17 callbacks。[结构基线](baseline-01.log)：21 manifest / 25 ownership / 16 census / 19 intrusion；新增的 `BR1-OWN-STROKE-CUT` 明确由原 `KisStroke` 队列维护切点顺序，未新增页面状态或事务权威。原布局约束、侵入上限和预算负载保持。

## 2. 修改与职责

普通 `addMutatedJobs` 把新子任务放在队首，直接用它安排 checkpoint 会越过已排队的普通 dab。新增 `addCheckpointJob` 在原 queue mutex 内把 continuation 放在所有已接纳输入之后；必要 child/grandchild 仍按原规则插到前面。之后接纳的普通输入留在 cut 后，调用者立即返回并释放自己的 borrow，无须等待自己结束。

pen-up 已排队时，checkpoint 放在 finish 前；finish 开始后拒绝新请求。原 finish 用一个 non-owning 指针标记其队列位置，删除或派发时清除；正常输入已关闭、子任务只 prepend，因此 finish 保持队尾，定位无需扫描 job backlog。该指针不持有 job，也不构成第二份 job registry。

SEQUENTIAL 只等待已有 stroke jobs；BARRIER 另沿原规则等待 merge/external work。两者均由原 dab strategy 执行。请求必须 cancellable，错误 LoD、并发类型、已取消或已离队 stroke 均拒绝；data 在接受/拒绝时保持唯一所有权。取消删除未开始的 cut，必要 non-cancellable child 仍先于取消终结执行。正在运行的 cut 的发布/回退责任仍属于原 scope/transaction。

## 3. 新增行为证据

每架构新增 **33 项**，原定向日志为 [Stroke 14 passed](kis_stroke_test-focused-01.log)与 [Queue 23 passed](kis_strokes_queue_test-focused-01.log)，各含两项 init/cleanup。定向运行早于“队尾直接定位”修正，最终完整矩阵包含该修正；不混用源码身份。

| 组 | 场景与实际断言 |
|---|---|
| 4 项 cut 排序 | SEQUENTIAL/BARRIER × pen-up 两种次序；旧排队 job、必要 child、多次 cut、新输入和 finish 的位置保持 |
| 8 项拒绝 | CONCURRENT、UNIQUELY_CONCURRENT、non-cancellable、错误 LoD、取消、失败、finish 已派发、null；队列不变，data 析构一次 |
| 16 项真实 worker/像素 | 四种 BPP × 两种 cut × pen-up 两种次序；原 Tiles3 provider + Store/session，两个 worker 同时持 guard，请求方持 guard 时入队仍立即返回。后产生 child/grandchild 及旧排队 job 共五页全部进入精确视图；后输入重写不改变旧 view；只创建一个 session，generation/pin 计数准确，最终 commit/close |
| 4 项取消 | 用户 cancel/worker failure × pen-up 两种次序；未开始 cut 不运行，新 cut 拒绝，必要 child 执行一次且先于 cancel，finish 不运行 |
| 1 项保留句柄 | 模拟已离队但被 LoD buddy 保留的 strong owner，weak handle 仍有效也不能接纳 cut；无效 handle 同样释放 data |

真实 worker 测试通过测试 strategy 直接持有原 session，不冒称已经使用 TransactionData/freehand 的持久业务 token。已有 session checkpoint 的完整性、失败、存储证据保留在 [前批](../br1_s02_checkpoint_20260928/README.md)，其 allocator 探针已在本批 image 重跑；本批没有新增 capture 内部分配失败资格。

构建记录 [build-01](build-01.log)、[build-02](build-02.log)均通过。当前没有生产/行为失败样本被跳过或削减；已有预算、原矩阵场景及所有旧测试断言保持。

## 4. 指南与剩余工作

[SC1–SC6](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01e_scheduler_cut_and_job_admission.md#scheduler-cut-map)建立 15 个具体代码符号的对应关系；[导航校验](validation.json)及 [符号校验](scheduler-cut-mapping-validation.json)检查正反向目录、15 个全局修改 ID 和局部入口。本批重定位 6 个受源码移动影响的链接，见 [source-link-remap](source-link-remap.json)；完整文档增量见 [guide-update.patch](guide-update.patch)。校验不读取归档。

下一段必须联合完成原 history/TransactionData 持久 scope、job 身份与读写 footprint、backend/painter/iterator 借用及 current/G0/source；Freehand/mask/indirect 的异步 producer 必须先明确 flush/停接纳或 continuation，队列位置不会自动包含 job 返回后才产生的外部工作。不同 LoD/store 不自动共享切点或可变权限。

不能每 dab 都提交 cut 来替代真正跨 dab 复用。切点仅用于真实冻结/终结/压力边界；pressure subset、完整 capture/派发/终结存储、共享预算与无新输入进度仍按 SS7、S04/S05/S09/S10 闭合。完整 S02、M6/M7/M8、真实 stroke / Fresh 2% / BR1-PERF、Vulkan 与 TSAN 均未新增完成资格。
