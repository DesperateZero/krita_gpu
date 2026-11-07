# S02 第三批：真实 admission、activity 与原终结寿命

日期：2026-09-28。执行入口仍为 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)；要求到代码的对应关系见 [01c §11–§12](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#admission-implementation)。本批实现 J1–J8 的原表存储、生产 caller、scope/range 计账与原 orphan 链子范围。持久 stroke/job borrow、整个 job 冷资源准入、S09/S10 完整边界和 M6–M8 均未完成。

## 1. 源码、二进制与最终结果

HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`；含未跟踪生产/测试文件的完整工作树差异 SHA-256：`5ab80e160b49847121ec2a7040913696d6c8cd4500b55aa6fc7f7f384a81b388`。不是只用 HEAD 标识本批修改。

- 最终 [checks-02 manifest](checks-02/manifest.json)：17 个 CPU/业务目标 × arm64/x86_64，**6,380 passed、0 failed、0 skipped**。结构门、六项调用图工具自测、最终 no-work 构建检查通过。
- [最终探针 manifest](probes-manifest.json)：两架构共 **26 次**，全部返回 0；20 次已有 install/native/read/legacy/cleanup/storage 探针重新运行，另加 6 次本批 admission 探针。
- [identity](checks-02/identity.json)保存 CMake/cache、源码、image/UI 库及测试程序哈希；每个 `install-*-final-01-identity.json` 保存命令、运行环境、探针/拦截器源码与二进制哈希。[evidence-scope](evidence-scope.json)逐个核对全部 26 个探针与同一 image、完整源码、最终测试程序绑定，运行期间源码不变。
- [architecture](checks-02/architecture.log)：21 manifest entries、24 ownership facts、16 census groups、1,759 indexed APIs、17,717 reverse-call edges、19 frozen intrusion files；原布局上限与唯一 owner 合同保留。
- [本批代码差异](admission-code.patch)只覆盖开始时保存的 11 个手工修改文件；完整累积源码见 [source.patch](checks-02/source.patch)。[diff-check](diff-check.log)通过。没有提交或暂存工作树。

`run_checks.py` 复用上一批执行器，其 identity 的 `scope` 字段保留上一批 slot 子范围文字；本批扩展范围明确登记在 `evidence-scope.json` 和本页。不能用执行器文字扩大资格，也不改写旧运行记录。

## 2. 本批行为与实际消费者

1. 原 `m_claims` 和 `transactionActivities` 改为 `KisMutationAdmissionTable`。8 个 inline 桶容纳 4 条记录；更大容量由原 allocator 收费。只有增长才准备 snapshot/replacement，gate 内复验 revision，gate 外重建，gate 内安装真实已备桶；成功和拒绝都锁外释放候选/旧数组。无第二张可查询 authority。
2. managed `claimAll`、native `claimOne`、generic `claimDirectLocked` 共同接入。安装前再次检查全范围冲突、原 set/handle 和 operational；保留旧 claims，原调用者跨 unlock 保活并串行保护 write set。revision 竞争最多准备 3 次，之后未执行拒绝。
3. session/preparation 首次 activity 有结果，已有记录加减不分配；generic 只能交接已有 preparation。每次计数改变推进 revision，溢出拒绝。generic 与 page removal 在 base/plan/proof 副作用前开始 activity，解锁后复验；成功才 end。
4. scope 对象、std shared control block、range 对象与前缀向原 MetadataArena 收费。scope 先为 Detached 候选，activity 成功并复验事务后才 Active；实际对象和控制块释放/还账前原 owner 保持存活。native 仅在新 entry 时锁外准备 write set。
5. 原 scope 内嵌 `nextOrphan`，原 orphan vector 改为同一 scope 的 intrusive 链。最后共享 owner 的取消拒绝不再依赖新增队列节点；原事务重试成功后销毁，失败挂回。token 耗尽拒绝新 ClaimSet，已有 set 仍可释放。

## 3. 新探针的测量范围

所有结果两架构一致，真实 allocator 有命中与无故障控制；源码随身份文件冻结。

| 探针 | 最终证据 | 结论与范围 |
|---|---|---|
| admission-allocation | [arm64](driver-arm64-admission-allocation-final-01.log)、[x86_64](driver-x86_64-admission-allocation-final-01.log) | 1/4/5/65/1,000 claims；每组 1,000 次已有集合命中和单项 release/reclaim 均 allocation/bytes/free=0/0/0。小表冷接纳也为零；不包含所有像素与其他 metadata 成本 |
| admission-failure | [arm64](driver-arm64-admission-failure-final-01.log)、[x86_64](driver-x86_64-admission-failure-final-01.log) | 每架构 132 区间、122 次真实拒绝；scope/generic/removal 覆盖 0/4 已有 activity；managed 1/5/9/65 页。命中拒绝不抛到调用者，managed body=0，随后真实 fill/close 成功。无注入 managed 控制 body=1，callback 故意返回失败以测试原终结 |
| admission-gate | [arm64](driver-arm64-admission-gate-final-01.log)、[x86_64](driver-x86_64-admission-gate-final-01.log) | 2 个旧 native claims、请求 17 页；准备期间其他线程分别插入冲突 claim、关闭 operational、插入无关 claim。前两者拒绝且旧状态保持，第三者复验后成功。真实 allocation/free 暂停时其他线程取得原 gate；观察 free 前 live charge=3,456 |

冷表成本（allocation 次数 / 申请 bytes / free 次数，含原 budget bookkeeping 的实际申请）：

| claims | 冷接纳 | 留存动态桶收费 |
|---|---|---|
| 1、4 | 0 / 0 / 0 | 0 B |
| 5 | 4 / 1,452 / 1 | 768 B |
| 65 | 4 / 12,972 / 1 | 12,288 B |
| 1,000 | 4 / 98,988 / 1 | 98,304 B |

零动态收费的小表使用原 Store 内嵌空间，不表示整个 Store 内存为零。动态容量为空时暂不缩减，保持收费到表析构。增长 capture 在 gate 内复制旧容量，重建在 gate 外；这不是有界 hold 或真实 brush 加速的证明。本批未增加独立 install 阶段 hook，不能将上述局部测量当作完整 M5/M7 安装资格。

新增测试还覆盖 growth 的纯计数 revision 失配、1,000 项碰撞/擦除复用、5/9/65 页整组预算拒绝、token 终值、四类 BPP 的 scope 预算与双 scope 原 orphan 链。测试清单和所有实际结果在最终 manifest 中。

## 4. 保留的失败与修正

- `build-01.log`：在嵌套类型尚未完整时实例化默认构造 noexcept 断言导致编译失败；断言移到 allocator 实例化位置，合同保留。
- [checks-01](checks-01/manifest.json)：6,370 passed、2 failed；两架构同一个 `metadataArenaBudgetTracksAllocator` 旧夹具只预算目录，新增 scope 收费导致更早拒绝。修正为测量并准入实际 scope/control block 后，继续验证首个 metadata arena 块拒绝；scope 真实释放后再检查目录收费。未放宽产品预算或忽略失败。
- `probe-failure-arm64-01.log/-02.log`：探针编译参数遗漏，未生成运行资格；补完整 acquire/resolve 参数后重新编译。
- gate 初次探针按 free 栈符号过滤未观察到释放；改为记录从实际 allocator 栈返回的指针并匹配真实 free，最终两架构探针通过。未将观察器错误算作生产故障。
- `build-04`、定向测试和 graph-03 后才冻结最终 checks-02/26 探针。之前的预运行不与最终源码混用。

## 5. 仍待改的边界

持久 scope 身份、scheduler job/cut/footprint、跨 worker borrow、局部 entry 热路径及 painter/iterator/refresh 接线按 SS1/SS5–SS8 继续。整个 job 的冷 metadata/descriptor/provider 存储、borrow 和必要失败容量还未提前备齐；当前结果仍是 bool/error，没有新增像素 replay。

本批只关闭原 orphan 保留链的节点分配。其他取消 effects、通知/派发/重试存储和 facade 消失后的自动进度仍属 S09；generic request/lease 控制块、Store/controller 内部 bookkeeping 和共享父额度仍属 S10。动态表 shrink/压力、增长 capture 的 hold 上界和真实 stroke 成本待测。

M6 完整故障/epoch/SSD/资源资格、M7、M8、Fresh 2% 控制和 BR1-PERF 开放；没有新增 Vulkan、TSAN 或真实 stroke 性能资格。undo 和上下文优化仍排在 stroke 之后。

指南校验见 [validation.json](validation.json)：20 篇指南加基线/入口/证据页共 23 篇，15 个修改 ID、28 个要求源码锚点及 21 个实现源码锚点均通过。源码行和文档行链接分别按实施前快照重定位，归档链接跳过且未读取。
