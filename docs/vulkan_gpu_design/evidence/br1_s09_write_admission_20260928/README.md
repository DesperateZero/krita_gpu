# S09 第九批：通用写准入与失败终结

设计与代码映射见 [04c：通用写准入 GW1–GW7](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04c_generic_write_admission.md)；阶段权威仍为 [92](../../92_br1_m6_m8_execution_baseline.md)。

## 改动与边界

原 write request node 先于共同写计划；原 ActiveWriteRecord/control block 与 detached active node 先于 provider pin。拒绝保持 Pending，成功后转入实际节点不分配。resolve 校验全部 request 身份及返回 access 的 mode/replica/lease/operation，失配的有效能力锁外归还。没有新增 canonical owner，native resident pending 不进入 generic map。

共同计划 cleanup 检查锁状态，锁外异常时不重复 unlock；generic 在共同计划、Fresh provider 准备和初始化调用边界捕获 bad_alloc。已有 private writer 的初始化拒绝走原取消；取消被拒绝时 request/claim 留给 abort。finishWrite 的已消费记录、事务 activity、retirement 与 close 沿原责任链。

这些是已验证的调用边界，不是 provider 部分分配、所有 metadata/ledger/descriptor 内部或应用级 OOM 恢复资格。索引使用 std::map，cold generic lookup 为 O(log L)；尚未证明通用写或真实 stroke 的性能收益。

## 同源码验证

17 目标 × arm64/x86_64：**6,264 passed，零失败/跳过**，每架构新增 68 项。完整命令、seed、源码与 binary 在 [manifest](checks-01/manifest.json) / [identity](checks-01/identity.json)。

调用图 1,655 APIs / 16,633 edges / 15 callbacks；21 manifest / 24 ownership / 16 census / 19 intrusion，6 项工具自测通过，ratchet 未改。

| 新增探针 / 每架构 | 区间 / 真实拒绝 | 覆盖 |
|---|---|---|
| write-request-final | 4 / 2 | 实际 PendingWriteRequestRecord node 的调用栈筛选；0/257 个已有请求保持。本次无悬挂 claim，重试、取消与 close 成功；不覆盖更早 activity/admission 或 metadata 内部分配。 |
| write-resolve-final | 9 / 7 | 控制块、active node 与 provider 登记按真实分配顺序拒绝；同请求重试/取消，其他 0/257 个 lease 的字节保持，最终物理 bytes 归零。 |
| write-post-pin-final | 2 / 0 | provider 返回真实 pin 后启用首分配拒绝；0/257 个已有 lease 两区间均没有分配尝试，合法能力交付。并发索引增长由生产 fixture 另行覆盖。 |

十五组既有预算/root/安装/暖读/共同 handoff/清理/completion/read/provider 探针按原边界继续通过。共 36 次 final 的 image 哈希与完整矩阵相同，见 [probe manifest](probes-manifest.json)。零分配声明没有扩展到冷通知/派发或整个写调用。

源码 HEAD：5173c807c87bb1619325249a07a8b4f4f8f09f09。累计 patch SHA-256：f4564c579d730a9efd269269255136fbaa67feda9c27d995ee7330a04012ea94。image SHA-256：f0a57291b5047a53a118579f8326662cefc3755de2a3bae11cdf3b72b1bb14d8。四个手改文件的增量在 [review](incremental-review.patch)，生成图与基线另在完整 source.patch；[改前身份](before-source.json)和 [改前源码](before-source.patch)保留。

## 失败与中间验证记录

before-01 使用改前 image，真实 post-pin malloc 拒绝命中 ActiveWriteRecord make_shared：threw=1、lease_valid=0、pending_requests=1、active_leases=0；探针退出码 10，原始栈与身份保留。

build-01 为新测试误用 Host 枚举的编译失败，修正为既有 HostLogical。focused-arm64-01 至 -04 保留夹具失败：提前禁用同步 copy 阻止 native setup；过早占满退休预算被前置 admission 正确拒绝；初始化期间仍有真实 fallback reservation，单页额度不足以创建竞争债务；测试直接创建未登记 provider allocation 触发原 journal/owner 准入拒绝。夹具改用两个实际退休额度、先后填充竞争债务和已由 PageStore 准入的另一写请求，不绕过原 budget/owner。没有修改生产预算条件来满足夹具。

文档收尾首次脚本有字符串语法错误，解析时即退出、未改动文档；修正后的 finalize-docs-02 完成回写。首次链接检查器只识别带 `::` 的方法，误拒绝合法静态成员 `preparePublicationAbort`；补充准确符号模式后重新核验，原失败日志保留。

focused-arm64-05 为 75 passed；其中 68 项新增、5 项既有终结回归与 init/cleanup。随后重新生成调用图并运行 checks-01/final；早期 after-01 探针只作调试，不作为最终源码资格。

## 剩余实施

更早 activity/admission、metadata/descriptor/ledger/provider 内部存储故障、GW6 全局/metadata 实际容量收费、必要 notification/dispatch/retry/pass 准入及自动接续、T4 整轮预算继续。完整 M6、M7/M8、stroke scope/可见性/短发布、undo/context 与正式 BR1-PERF 未完成；未新增真实 stroke、Fresh 2%、Vulkan 或 TSAN 资格。
