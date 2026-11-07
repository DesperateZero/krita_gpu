# S03：真实 multi-dab painter 与原事务 cursor

日期：2026-09-28。当前设计/阶段入口为 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)；逐段实施关系见 [S03 / MD1–MD7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01g_multi_dab_and_painter_scope.md#multi-dab-map)。默认 brush 实际调用现在消费声明范围的 cursor；显式 owner overload 可复用原 history session，默认 brush caller 尚未传入持久 owner。

## 身份与验证

HEAD `5173c807c87bb1619325249a07a8b4f4f8f09f09`；含未跟踪生产/测试文件的源码差异 SHA-256 `62187b32744af5a5b7360a0e2726cc42d20cb419b0fa5113cb8579e3f69bf63c`。

最终 17 目标 × arm64/x86_64：**6,866 passed、0 failed、0 skipped**。见 [完整 manifest](checks-01/manifest.json)、[源码/库/测试二进制 identity](checks-01/identity.json)、[完整源码差异](checks-01/source.patch)、[绑定检查](evidence-scope.json)。末次构建 no work，结构门、六项工具自测通过。调用图为 [85 TUs / 1,788 APIs / 18,420 edges / 17 callbacks](graph-01.log)，结构清单为 [21 manifest / 25 ownership / 16 census / 19 intrusion](baseline-01.log)，没有提高 ratchet。

[36 次继承探针](probes-manifest-01.json)在本批源码/image 下重编译运行通过；源码与二进制绑定见各 `install-*-final-01-identity.json` 及上述绑定检查。它们保留安装/存储/准入/execution/checkpoint/刷新等底层约束，不测整个新增 painter 入口的 allocator 或端到端性能。[本批代码增量](multi-dab-code.patch)以本批开始前的 9 文件快照为比较范围。

## 实现与新增覆盖

`bltFixed` 保持原 dab 次序及 source/mask/通道/opacity/flow 语义，使用一个有界 cursor 操作；明确传入 owner 时选择同一原事务并只归还 borrow，拒绝不 fallback。PaintDevice 继续负责 wrap/offset 与 manager-local 映射。composite lookup 使用调用局部结果，避免并行 job 写共享 painter cache。新 overload 以 const 引用借用列表，旧二参数 ABI 保留。

| 新增场景 | 数量/架构 | 实际证明 |
|---|---:|---|
| 像素 oracle | 48 | 1/4/8/16 BPP × 独立/显式 commit/显式 abort × mask × wrap；非零 offset、源 bounds、重叠 dabs、通道、opacity/averageOpacity/flow、cut、旧 reader、undo/redo。整数精确；F32 有限值且绝对误差 ≤5e-6 |
| 重复准备 | 3 | D=1/10/1000，首轮两页准备恰好两次；同段不增加、不 seal；checkpoint 后再写两页累计四次 |
| 并行 | 1 | 同 painter、同 owner、两真实 worker 同时持有独立页 execution；活跃时 cut 拒绝，归还后 cut/像素/abort 正确 |
| 写后取消 | 1 | Alpha8 原 Copy kernel 改完第一页后暂停；取消记录意图但活跃 borrow 拒绝终结；第二页不执行，原 owner 重试 abort 恢复 G0 |
| 遮罩快照 | 1 | cursor body 开始后修改独立 selection，跨页 composite 仍消费此前捕获的 immutable mask |
| owner 拒绝 | 1 | 错 target 的空/非空请求不执行 callback，multi-dab failure 上送；已结束 owner 不获得权限 |

上述为每架构 55 个新增 case；测试 init/cleanup 另计在完整目标总数中。初步 [focused-02](kis_painter_test-focused-02.log)为 57 passed，之后新增 overload 改为 const 引用并完成最终完整矩阵；因此以完整矩阵身份作为最终源码资格。

## 失败保留与修订

[focused-01](kis_painter_test-focused-01.log)保留 52 passed / 4 failed：三个重复写 case 错计 `MutationSourceInitialize`，一个取消 case 等待不会触发的 observer。重复写改计实际 `WriteProviderPrepare`，并将正控制收紧为恰好两页；取消改为测试私有 Copy composite 写后暂停，没有新增生产 hook、删断言或放宽超时。[build-03](build-03.log)保留 Alpha 模板构造/析构符号不可链接，[build-04](build-04.log)保留基类 protected 析构错误；改为经已有虚函数 clone、使用公开派生析构的局部实例后，[build-05](build-05.log)、[build-06](build-06.log)和最终完整构建成功。测试私有 composite ID 的显示名 warning 不影响断言。

## 剩余范围与文档关系

真实默认 brush 两个 caller 仍使用独立操作 overload。默认持久接线须共同完成原 strategy/target 寿命、映射后页范围依赖、读意图、异步 producer/scheduler cut、finish/cancel 及必要存储和压力保证。scalar fixed/general bitBlt、其他 iterator/source-dependent、indirect/mask/LoD 不因此自动迁移。完整 M6/M7/M8、Fresh 2%、实际 brush 性能、Vulkan、TSAN 和 BR1-PERF 仍开放。

[导航与符号校验](validation.json)核对 24 篇指南、15 个全局 ID、MD1–MD7、正反向文件关系和当前矩阵身份；[继续实施时的行号重定位](continued-source-link-remap.json)保留映射记录，[文档增量](guide-update.patch)对照本轮继续前的指南快照。前次纯文档核对记录保留在自己的证据目录，不能与本批运行身份混用。
