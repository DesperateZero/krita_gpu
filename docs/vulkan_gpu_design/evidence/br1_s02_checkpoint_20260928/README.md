# S02 第六批：完整 checkpoint 与同一 session 再开放

日期：2026-09-28。唯一阶段入口为 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)；逐段要求、代码及后续责任见 [01c §15 / CP1–CP5](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#checkpoint-implementation)。本批交付能力层的完整 checkpoint，业务仍每 operation seal；未启用持久 stroke，也未关闭 S02 或 M6–M8。

## 1. 身份与最终验证

HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`；包含未跟踪生产/测试文件的源码差异 SHA-256：`57eea020a6423c8f4b3fb2baee6e04b24112da37e3dad522ed30a65708c2fe86`。

同源码 17 CPU/业务目标 × arm64/x86_64：**6,580 passed、0 failed、0 skipped**，每架构新增 48 个场景。结构门与六项工具自测通过，最后构建 no work。命令、seed、源码和二进制哈希见 [matrix manifest](checks-01/manifest.json)、[identity](checks-01/identity.json)、[source.patch](checks-01/source.patch)。[绑定检查](evidence-scope.json)逐一校验最终源码、测试 binary 与探针 image；[本批代码增量](checkpoint-code.patch)相对上一批快照，只包含本次修改。

[36 次最终探针](probes-manifest-01.json)全部通过，34 次继承探针在本批 image 重新编译/运行，2 次新增 checkpoint 分配探针分别覆盖两架构。各 `install-*-final-01-identity.json` 保存实际命令、环境、探针/interposer 源码和哈希。[graph-01](graph-01.log)为 1,785 APIs / 18,267 edges / 17 callbacks；[baseline-01](baseline-01.log)通过 21 manifest / 24 ownership / 16 census / 19 intrusion，原布局上限和原预算负载保持。

## 2. 实际行为与失败边界

- `checkpointForRead` 完整消费原 session 的 live entries，沿原 seal/proof 安装 transaction overlay，再调用与公开 capture 共用的 helper 取得完整精确视图。没有 viewport 过滤，也没有第二份 write set、snapshot authority 或事务终结器。
- 原 page claims、冷热段存储和源按原终点归还，实际释放在 owner gate 外；原 session activity/owner 跨 checkpoint 保留。空新段继续使用原 allocator；下一段首次写从刚 sealed 的 overlay 准备，未重写页面保持原版本。
- scope gate 保持到 capture 完成，新 borrow 此后才可进入。checkpoint 可由其他 worker 在 quiescent 状态调用；普通 borrow 的 worker 限制保持。存在活跃 execution/guard 或结构 gate 忙时立即拒绝，保持 Active 状态，既不 seal 也不等待冷准备。
- seal/proof 拒绝沿原段取消，更早 sealed overlay 和已冻结 view 保持。seal 成功后若 capture 正常返回拒绝，该段已在 overlay，接口停止继续写并终结空 scope；整笔回退必须由原 transaction owner 完成。接口不承诺跨 checkpoint 的 Operation rollback。
- 完整 capture/retention/map/metadata 分配异常、必要终结容量和全部 owner gate 内准备仍未完成故障资格。本批不能作为默认启用持久业务 scope 的充分前提。

## 3. 针对性验证与保留失败

| 记录 | 结果与含义 |
|---|---|
| [focused-01](focused-01.log) | 46 passed，含首批 44 个场景与 init/cleanup；尚未加入资源与语义页组合 |
| [focused-02](focused-02.log) | 50 passed，含全部新增 48 个场景与 init/cleanup；最终资格另由完整双架构矩阵绑定 |
| [build-01](build-01.log) | 测试误用 `beforePrepare`，实际 provider 字段为 `beforePrepareWrite`；编译拒绝，修正后构建通过 |
| [storage-focused-01](storage-focused-01.log) | 2 passed / 4 failed；错误地要求 checkpoint 后 total MetadataArena 必须下降，忽略新增 frozen-view 保护 |
| [checkpoint trial-01](driver-checkpoint-trial-01.log) | 同一错误判据在 K=1 给出反例：125,848 → 142,232 B；失败记录保留 |
| [checkpoint trial-02](driver-checkpoint-trial-02.log) | 分开检验声明未写范围的真实释放与像素 view 保护后，K=1/9/65/257、三个周期全部通过；最终资格仅使用下面两架构 final 运行 |

新增 48 项/架构由五组组成：24 项跨 worker、1/10/1,000 次重复写与 commit/abort；12 项直接 guard、无 guard execution、execution guard 的拒绝；4 项下一段 proof 失败后旧视图；4 项真实阻塞冷准备时非等待拒绝；4 项范围存储及 remove/default/rewrite。测试保留远页、generation、旧/新像素、计数只归并一次、原事务活动、完整 close 断言。

资源判据修正没有放宽 payload/旧视图或预算断言：先对声明未写范围测量回收，再对实际写入测量冻结 metadata；两者同属 MetadataArena，总量不能单独证明范围回收与否。

## 4. 实际 checkpoint 成本

[探针源码](checkpoint-allocation-probe.cpp)使用真实 Tiles3 provider、原 transaction/session 和 allocator interposition。K=1/9/65/257 各在同一个 session 连续写入和 checkpoint 三次；每段 1,000 次已准备 guard/version 访问在两架构均为 **0 allocations / 0 requested bytes / 0 frees**。首次及末次精确 view、取消/abort 和 close 同时验证；正控制与继承探针保留。

声明未写范围完成 checkpoint 后，两架构的实际 MetadataArena 读数一致：

| K 页 | checkpoint 前 / 后（B） | 含义 |
|---|---|---|
| 1 | 108,440 / 108,440 | inline 范围，无 overflow 可释放 |
| 9 | 111,560 / 109,976 | 原范围动态存储已归还 |
| 65 | 133,136 / 120,728 | 原范围动态存储已归还 |
| 257 | 207,152 / 157,592 | 原范围动态存储已归还 |

真正写入后的 checkpoint 有 seal、capture 和 retention 成本。下表仅列首个周期的 **allocation / requested bytes / free**；每次调用的完整记录见 [arm64](install-arm64-checkpoint-allocation-final-01.log)及 [x86_64](install-x86_64-checkpoint-allocation-final-01.log)。

| K 页 | arm64 | x86_64 |
|---|---|---|
| 1 | 65 / 58,240 / 49 | 65 / 58,128 / 49 |
| 9 | 329 / 183,552 / 330 | 329 / 183,056 / 330 |
| 65 | 2,190 / 1,137,184 / 2,279 | 2,190 / 1,133,976 / 2,279 |
| 257 | 8,594 / 4,619,528 / 8,976 | 8,594 / 4,607,056 / 8,976 |

requested bytes 是本区间累计请求量，不是 live bytes 或 allocator 实际占用。free 可以包括区间前已创建的对象，不能由次数直接推断泄漏。探针覆盖整个 checkpoint 调用，不据此推断 publication install 有分配；也不能把暖 guard 零分配外推为 checkpoint 零分配、恒定 gate hold、Fresh 2% 或真实 stroke 加速。

## 5. 修改指南与下一段

[CP1–CP5](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#checkpoint-implementation)对应入口、段终结、共享 capture、语义/失败测试和资源测试，均链接具体函数。原 SS1/SS5 负责 history-owned scope、真实 job 身份、读写 footprint 与 cut；SS8 负责 current/G0/source 和 painter/iterator；SS7 的 pressure subset 与 S04/S05/S09/S10 的发布准备、必要终结和资源进度继续。空闲 mutex 不证明 cut 前排队 jobs 或必要子任务已经完成，跨 store 与其他 mutation 也需业务 owner 协调。

[导航校验](validation.json)覆盖 21 份指南、15 个修改 ID 和入口/证据文档；[checkpoint 映射校验](checkpoint-mapping-validation.json)核对 CP1–CP5 的 11 个代码符号。191 个受本批源码移动影响的链接已重新定位，见 [source-link-remap](source-link-remap.json)；完整文档增量见 [guide-update.patch](guide-update.patch)。校验跳过归档，不从归档推导当前状态。

完整 S02/S03、S09/S10、M6 SSD/epoch/故障/资源、M7/M8、真实 stroke / Fresh 2% / BR1-PERF、Vulkan 与 TSAN 均未新增完成资格。优先级继续为 stroke → undo → 上下文切换。
