# S09 第八批：读保护与 pin 之前准备原记录

设计与代码入口见 [04a §15](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/04a_retirement_wakeup_implementation_map.md#read-storage-admission)；阶段权威仍为 [92](../../92_br1_m6_m8_execution_baseline.md)。

## 实际改动及范围

原 request node 先于 AcquireRead，ActiveReadRecord/control block 与 detached active node 先于 provider resolveAccess。拒绝准备保留 Pending，provider bad_alloc 在重新取得 owner gate 后恢复 Pending；成功 transfer node 不分配。CPU/tiles3 原 activeLeases 的实际插入先于 acquireAccess，异常/拒绝 pin 撤销本次预备节点。release、revocation、cache、last-use 与 close 仍沿原 owner。

binding acquireRead 用 RAII 归还 gate；native try/wait 语义保持。四个 pinStorage 异常 fixture 是确定性协议测试，不代替全部真实 swap/SSD 故障。

request/active index 是 std::map，cold generic lookup 为 O(log L)；provider index 是 unordered_map。未复制整表或增设状态权威，未授予通用读/真实 stroke 性能资格。

## 验证与身份

17 目标 × arm64/x86_64：**6,128 passed，零失败/跳过**。每架构新增 28 项用例。完整命令、seed 与 binary 见 [manifest](checks-01/manifest.json) / [identity](checks-01/identity.json)。

结构门 1,655 APIs / 16,459 edges / 15 callbacks；21 manifest / 24 ownership / 16 census / 19 intrusion，6 项工具自测通过，ratchet 未改。

| 每架构探针 | 区间 / 真实拒绝 | 检查边界 |
|---|---|---|
| request-final | 4 / 2 | 0/257 个已有 request 保持，取消后 close/physical bytes 归零；调用栈筛选 request 自身节点，排除 metadata 内部。 |
| resolve-final | 9 / 7 | 控制块、active node、provider node/buckets 逐次拒绝；已有 0/257 lease 保持。Pending 可重试，provider 直接拒绝后按原取消语义重新请求。 |
| provider-final | 10 / 6 | read/write × 0/257 个已有 lease；拒绝后 native writer 可取得，同身份重试成功，释放后 writer 恢复，最终 retire/close。 |
| post-pin-final | 2 / 0 | 真实 provider 返回 pin 后才启用首分配拒绝；两个 active 规模均无分配尝试，lease 正确交付，最终 close。 |

十一组既有探针继续通过，共三十次 final 与矩阵 image 一致，见 [probe manifest](probes-manifest.json)。allocator 有实际拒绝与调用栈控制，不把“未触发注入”单独当作有效性证明。

源码 HEAD：5173c807c87bb1619325249a07a8b4f4f8f09f09。累计 patch SHA-256：c58faaf12d3b7f45453e1c92e9b73592cbb9fec8fe505e009752b9937694b966。image SHA-256：a60614da6c0602941ca304d08affb700f3069906e6bc4057c0cc75118de33576。七文件增量见 [review](incremental-review.patch)，改前源码见 [before](before-source.json)。

## 修复前与中间记录

before-02 在旧 image 的真实 post-pin 区间注入首分配失败，栈命中 ActiveReadRecord make_shared：threw=1、lease_valid=0、pending_requests=1、active_leases=0。探针明确退出并保留旧源码/image 身份，不计为成功。before-01 为 probe 使用错误统计字段名的编译失败；修正后以新 tag 运行，原日志保留。

早期 build/focused/after-01 用于调试；随后审查发现 acquireRead 手动 gate 在 pinStorage 异常时未归还，追加 RAII 与四项用例，重新构建并生成 callgraph-generation-02。最终判断只取 checks-01 与 final tags。

## 继续实施

必要 notification/wake/dispatch/retry/pass 存储和 S10 收费、自动进度、完整 metadata/swap/SSD 故障、T4 整轮预算/T5 真实拒绝终点仍开放。通用 write coordinator 的 pin 后记录未由本批 provider 改动自动闭合。完整 M6、M7/M8、stroke scope/可见性/短发布、undo/context 和正式 BR1-PERF 继续；未新增真实 stroke、Fresh 2%、Vulkan 或 TSAN 资格。
