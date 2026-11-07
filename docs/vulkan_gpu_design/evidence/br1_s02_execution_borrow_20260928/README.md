# S02 第四批：原 session 的显式执行范围借用

日期：2026-09-28。执行入口为 [92](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)；要求、实际代码与剩余修改见 [01c §13](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01c_mutation_session_storage_and_borrow.md#execution-borrow-implementation)。这是 B 的部分前置，已接 managed pixel operation / packed write 的生产消费者；未完成整个 B、业务持久 stroke 或 M6–M8。

## 1. 当前源码与资格

HEAD：`5173c807c87bb1619325249a07a8b4f4f8f09f09`。含未跟踪生产/测试文件的源码差异 SHA-256：`dda3c393a0a1dc03f01fba8f71eff113f821f39bf79c154e3aaebc6eb63391c2`。

最终 [checks-02 manifest](checks-02/manifest.json)：17 CPU/业务目标 × arm64/x86_64，**6,412 passed、0 failed、0 skipped**。结构门、六项调用图工具自测与最终 no-work 构建检查通过。结构清单为 21 manifest / 24 ownership / 16 census / 1,778 APIs / 17,941 edges / 18 callback registrations / 19 frozen intrusion files。

最终探针为 [probes-manifest-02](probes-manifest-02.json)，共 30 次，两架构全部返回 0；对应标签为 `final-02`。源/构建身份见 [checks-02 identity](checks-02/identity.json)，完整源码见 [source.patch](checks-02/source.patch)。每个探针的 `install-*-final-02-identity.json` 保存命令、环境、源码和二进制哈希；最终逐个绑定结果见 [evidence-scope](evidence-scope.json)。之前 `checks-01` 与 `final-01` 是未压缩范围记录的冻结证据，不是本批最终资格。

[本批代码差异](execution-borrow-code.patch)按开始时保存的 8 个源文件生成；[git diff --check](diff-check.log)与指南检查分别验证源码空白和导航。未创建提交、暂存或 PR。

## 2. 改动与实际调用链

- 原 session 签发 move-only `KisPageMutationExecution`；跨 worker 使用通过新 borrow 接续，同一个 borrow 只允许创建它的 worker 获取 guard/成功 finish。原 session 的直接/legacy 接口保留旧线程约束，且不能进入活跃借用的结构。
- borrow 保留原 scope，记录原 write set 的 `slot index + incarnation`。不复制 PageKey→pending authority。原 `claimRange` 只检查本次选择的 slots，全范围复验后一次接纳新增 claims；拒绝回滚本次未接纳的新 entries，保留旧 claims 与像素。
- 候选 record/control block、slot 数组和临时回滚位图通过原 allocator 计账；单页 slot 内嵌。prepare 拒绝、重叠范围、错误 surface、外部 writer 拒绝均先于该 execution 的像素访问。
- guard 的 aliasing shared owner 保留原 execution，再保留原 scope。晚 guard 存活时范围继续链接，不能被另一 borrow 重用。成功 finish 只归还 execution；abandon 或 active borrow 期间的 cancel 将原 scope 设为 Failed，原取消在 guards/borrows 归还后继续。
- `runCpuMutationOperation` 在原 managed reservation 移交后获取 borrow。bounded cursor 与 packed overwrite 消费同一能力；operation 成功先 finish execution，再由原 batch seal。失败仍走原 operation 取消，未启用新的整笔 rollback 策略。

活跃 borrow 是受 session gate 保护的 intrusive 链，只表达执行占用与寿命，不持有独立 generation、before 或 writer authority。成员实际释放后才结束原预算 owner 的寿命。

## 3. 并发、故障与成本

四个新增测试均覆盖 1/4/8/16 BPP：

| 测试 | 验证内容 |
|---|---|
| executionBorrowWorkers | 两 worker 同时持有不相交 writable guards；第二 worker 扩展 65 页 hot/cold/index 时，第一 guard 的原 slot 与字节保持。后续另一 worker 对同页访问 1,000 次，generation 不变，最终像素和旧 exact view 正确 |
| executionBorrowExclusionAndFailure | 重叠范围、错误 worker/surface、直接 session/semantic/seal 入口被排斥；外部 writer 拒绝无部分新增 claim；abandon 停新借用，唯一原 scope 取消 |
| executionBorrowStorageRejection | 真实 record/control block 或范围存储的 tiny-budget 拒绝，旧 session/claims 保持、实际 charge 归还，随后小范围可再借用 |
| executionBorrowLateGuard | cancel 记录不可逆失败意图，borrow/public scope/facade 依次释放后 guard 仍有效；其他线程最终 unpin，旧 captured view 保持，abandoned pending 清理 |

late-facade 场景中的外部 provider 继续持有 committed 数据，按原 `facadeLifetime` 契约测量；它不等于显式 closeSession 的全量归零。

最终真实 allocator 探针，两架构结果一致：

| 探针 | 实际证据 | 范围 |
|---|---|---|
| execution-failure | [arm64](driver-arm64-execution-failure-final-02.log)、[x86_64](driver-x86_64-execution-failure-final-02.log) | 每架构 121 区间 / 117 次真实拒绝；1/5/9/65 个新页的 record、范围、bitmap、原 slot/index/claim 准备。旧 pending 的版本和 0x5c 字节保留，随后范围重试、cancel、abort、close 成功，无外抛 bad_alloc |
| execution-allocation | [arm64](driver-arm64-execution-allocation-final-02.log)、[x86_64](driver-x86_64-execution-allocation-final-02.log) | 1/9/65/1,000 页范围内各 1,000 次 resident guard 获取/归还，allocation/bytes/free=0/0/0；完整再次借用的成本单独列在下表，不冒称 job 进入零分配 |
| 原 admission-failure 重跑 | [arm64](driver-arm64-admission-failure-final-02.log)、[x86_64](driver-x86_64-admission-failure-final-02.log) | 实际 managed/native/generic/removal 入口，含本批新增 borrow 存储；结果按日志的实际命中数计，拒绝时 managed body=0，恢复后可重试与 close |
| 其余原探针 | [完整 manifest](probes-manifest-02.json) | 既有 install/native/read/legacy/cleanup/storage/admission gate 等探针全部以新 image 重新运行 |

一次完整 reborrow（包含 finish/free）的实际申请量：

| 范围页数 | 初版 allocation/bytes/free | 最终 allocation/bytes/free |
|---|---|---|
| 1 | 1 / 176 / 1 | 1 / 152 / 1 |
| 9 | 2 / 536 / 2 | 2 / 296 / 2 |
| 65 | 2 / 2,776 / 2 | 3 / 1,208 / 3 |
| 1,000 | 2 / 40,176 / 2 | 3 / 16,280 / 3 |

65 页以上多一个短寿命 bitmap 分配，但它不进入像素 body；常驻范围从每页 40 B 改为原 16 B slot handle。每次完整借用归还后，`live` charge 回到借用前的值；留下的原表/索引容量仍收费。初版成本来自 `final-01` 源码的实测，最终成本来自 `final-02`；这不是时延或 throughput 对比。

## 4. 发现并修复的回归

1. `focused-01`：14 passed / 4 failed。新增 late-facade 断言误要求外部 provider 所持 committed 分配归零；按既有明确契约修正为保留 committed、归还 abandoned pending，并等待已有 reclamation drain。没有改动产品销毁协议。
2. `checks-01`：**6,410 passed / 2 failed**。两架构均在原 `tiles3BackendsShareProcessResidentLimit` 第一份 6 MiB packed write 中出现 `mutation cold storage is unavailable`。独立 [product-limit-01](product-limit-01.log) 复现 metadata peak=8,388,040 B，接近原 8 MiB ceiling。
3. 原借用重复存 key/slot/回滚标记，每页 40 B。改为仅原 slot handle + 准备期 bitmap，降低执行期占用；[product-limit-02](product-limit-02.log) 在同样 8 MiB、384 页、6 MiB 输入下恢复通过，第二 backend 的失败与 process resident 上界、最终 close 断言全部保留。ReferenceTest 只增加失败时 live/peak/reserved 诊断。
4. `driver-arm64-execution-failure-01` 是探针路径参数错误的编译失败，没有执行资格。改为执行器接受的文件路径后重新编译；初版与最终源身份分开。

全部失败日志保留。修复后重新生成 graph-02、architecture baseline-02，构建并执行 checks-02 和 30 次 final-02 探针；不以初版通过的局部用例覆盖完整矩阵反例。

## 5. 下一段及未授予的资格

每个 guard 的获取/归还仍经过 session mutex，首次冷准备也串行。不同范围同时进入 kernel 不证明 SS6 局部热路径已完成；下一段应把已绑定 resident entry 的复验/pin/unpin 和统计归并从共享结构锁中移出，同时保持 slot、exposure 与原取消寿命。

业务 history/TransactionData 尚未持有长期 scope token；scheduler job ID、read footprint、cut/continuation、完整 checkpoint/压力 subset，以及 painter/iterator/refresh 的迁移仍继续。当前 managed/packed 消费者仍每 operation seal。未迁移的 Operation rollback、不可取消 indirect merge 与普通 brush 非 Commit-only 的语义保持。

全部 cold metadata/provider 和必要终结存储、共享预算及 facade 消失后的自动进度仍按 S09/S10 收口。M6 完整故障/epoch/SSD/资源、M7、M8、Fresh 2% 和 BR1-PERF 开放，没有新增 Vulkan、TSAN 或真实 stroke 性能资格。undo 与上下文仍排在 stroke 之后。

## 6. 指南与代码关系核对

[导航及关系校验](validation.json)覆盖 20 份指南与 3 份入口/证据文档、15 个修改 ID；主题涉及的 131 个源码文件全部纳入反向索引。01c §11–§13 的 28 个要求、21 个准入实现及 14 个范围借用锚点逐一匹配实际符号，全部通过。源码身份保持 checks-02 冻结值；文档检查不授予新的行为、性能或阶段资格。
