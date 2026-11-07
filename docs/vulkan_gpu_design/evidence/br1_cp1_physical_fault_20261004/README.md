# CP1 VM释放拒绝、语义reset字节及owner清点

当前裁决：[92 §16.88](../../92_br1_m6_m8_execution_baseline.md#cp1-physical-release-reset-delivery)。完整CP1开放，M6/M7/M8正式0/3，persistent默认关闭。本目录冻结有限源码交付和真实运行，不替代四组总出口。

## 源码及构建身份

| 边界 | 产品身份 | 本轮实际变更 |
|---|---|---|
| 进入本批 | `6ddccc30979ab859060ed5a19b936d5322aaa1cb` | 上批共同capacity规则；完整manager在本批取得实际终点 |
| VM物理释放 | `8f84cc8461ca621bc284342dbcdeb6490470b66e`，父6dd | 原KisPageWriteCoordinator.cpp +12/−3；两派生JSON +854/−853 |
| 最终语义reset | `3c22a0226a858ef16d150b2dfe5523d9bfbc684e`，父8f | 原KisPageStore.cpp +1/−1；两派生JSON +84/−20 |
| 文档起点 | `bd3783367b3b18f6d3710cb634adbb730859649f` | 外层文档独立提交；继承krita gitlink不暂存 |

两项均无产品测试修改、上层API、新owner、锁、队列或生产测试hook。8f normal/TSAN各复用上批40 TU完整底座，依赖核对只重编WriteCoordinator，其余39对象按hash复用；3c再仅重编PageStore.cpp。完整ninja deps、编译/链接命令及所有链接输入保存在各build identity；moc扫描目标不构成额外受影响C++对象。测试头和body未变，保留原二进制依赖复用记录。主构建库未覆盖。

[8f最终127源码身份](product-source-freeze-final.json)与[3c最终127源码身份](reset-product-source-freeze-final.json)逐项匹配Git blob；前者保留不覆盖，以便在途8f测试继续验证原输入。隔离候选/运行identity中的旧HEAD只作构建来源，真实源码由sources哈希及明确dirty状态绑定，不能仅按旧HEAD误归类。最终图87 TUs/2,172 APIs/27,412 edges/27 callbacks，21 manifest/25 ownership/16 census/19-file外部侵入ratchet通过；工具源码未改，本轮不重复工具自测。

## 两个实际缺陷与修复

1. 6dd的VM free在munmap失败时返回0，调用owner退出后丢失地址，但收费和物理映射都保留。负例两架真实注入EINVAL，actual3/reaped；诊断探针保留地址后再次free只用于清理负例，不是生产恢复。8f在原free内对同base/span调用mach_vm_deallocate；物理free成功才返回完整capacity归费。两架阳性均实际native free一次，地址查询unmapped，paid回332B、paid VM0，actual0/reaped；mmap ENOMEM拒绝亦实际命中且无遗留。双native释放都失败仍terminate，默认abort出口不授资格。
2. 未收费调用栈发现Mutation::Private::Page::resetPixel为QByteArray，stageSemantic从已收费format.defaultPixel隐式复制，双架完整CPU body均172次19–34B请求。3c字段改为原KisPageByteArray，共享同一不可变付费值，beginWriteImpl的读取/clear和Page析构延续原owner。独立原body重跑确认该site完全消失；其他site变化不计作此修复收益。[逐架对照](reset-observation-summary.json)保留完整原stack及源日志hash。

## 实际运行结果

| 源码与范围 | 结果 | 进程及边界 |
|---|---|---|
| 6dd原完整manager TSAN | 1,105/0/0，4,193.50s | actual0/reaped，48 tasks/16 threads/100,000 cycles/seed12345原样；匹配插桩QtCore，无suppression/guard/interposer |
| 8f原七完整body×双架normal | 5,908/0/0 | 14 actual0/reaped |
| 8f原七完整body TSAN | 2,954/0/0 | 7 actual0/reaped，匹配插桩QtCore，无suppression/interposer |
| 8f原8MiB取消/24MiB压力×双架 | 14/0/0 | 4 actual0/reaped，原业务body/预算不变 |
| 8f真实物理故障负/正对照 | 两负例actual3，两正例actual0 | 全部reaped，观察器loaded，未用退出guard |
| 8f完整CPU独立heap/VM账本 | 各1,386/0/0 | 双架actual0/reaped，paid usable余量并存峰值0，static后paid heap/VM0、overflow0 |
| 3c原完整CPU×双架normal | 2,772/0/0 | 2 actual0/reaped |
| 3c原完整CPU TSAN | 1,386/0/0 | actual0/reaped，匹配插桩QtCore、无TSAN警告 |
| 3c完整CPU独立heap/VM账本 | 各1,386/0/0 | 双架actual0/reaped，reset旧site消失、paid尾0/overflow0 |
| 8f九类生命周期真实故障×双架 | 2,280/2,277次实际拒绝，各9控制 | 双架actual0/reaped，各13次mmap拒绝、static后paid尾0/overflow0 |
| 8f原完整manager TSAN | Pending | 独立冻结库运行，不能将6dd结果迁用 |
| 3c原完整manager TSAN | Pending | 独立冻结库运行，实际终点后另结算 |

普通、TSAN、业务分别见[8f矩阵](normal-tsan-business-summary.json)；6dd实际终点见[manager-full-02结果](manager-full-02/results.json)。各round identity验证源、实际加载库、测试、Qt及插件hash，结果均含PID、actual exit和reaped事实。3c使用原完整CPU body覆盖内部Page所有消费者；已通过的8f七body/业务矩阵不重复计为3c的同源完整矩阵。

## 从未归类site到具体owner

[分类清单](owned-residue-summary.json)对8f原完整CPU观察的arm64 350、x86_64 349个未收费PageStore可达site逐项审阅完整stack，不以framework标志推断owner：

| 实际责任 | arm64/x86_64 site数 | 仍欠断言 |
|---|---:|---|
| 原TileData、pool/cache/swap | 202/201 | retained容量、物理free与参与者总硬界 |
| C++异常对象 | 82/84 | 并存exception容量及runtime分配失败 |
| 配置/应用/Qt服务 | 39/37 | 共享native/framework容量边界 |
| 原测试callback | 12/12 | 已定位fixture，不记生产owner分配 |
| QString error输出 | 5/5 | 临时错误存储及其拒绝保证 |
| 原memento | 3/3 | caller/undo共同容量，不建第二owner |
| exception TLS | 2/2 | 实际线程退出、TLS容量 |
| diagnostic TLS、Qt post routine、caller输出、format临时值 | 各1/各1 | 各自运行容量和最后退出 |
| resetPixel副本 | 1/1 | 本批3c修复，原172次请求消失 |

3c观察剩余348/346个site；除已验证reset副本外，数量差异来自各次运行，不当作其他owner删除证明。已识别paid heap/VM实际费用与usable/API span一致，仅覆盖这些已识别分配。约12.9GB峰值包含runtimeStopsAtCapacity填充process限额，不称RSS或8MiB业务越界。最后保留的非paid mappings及Qt/OS/runtime存储仍在总硬界差集中；native API span与OS合并region不能混用。

## 生命周期真实故障与诊断边界

沿原九族checkpoint/capture/read/default-read/commit/rollback/purge/release/close，16 BPP、1,024页使真实控制/metadata路径进入VM分配。arm64/x86_64完整轮分别2,280/2,277实际故障，各9控制、0 absent、13次mmap ENOMEM，actual0/reaped，661.41/879.53s；[实际API汇总](lifecycle-vm-summary.json)逐族保留。本探针只注入调用线程已观察paid site的首/末出现，不声称穷尽全部occurrence、其他线程或晚fence/caller。

原observer 2,048个discovery槽不足，首次运行在commit溢出，主动终止本次探针，actual−15/reaped；保留日志，不算通过。最终observer06使用16,384槽，探针32,768目标并显式拒绝overflow，两架各表0溢出。drain到永久stop前原worker/monitor映射仍合法保活；stop后paid VM0，static后paid heap0，不把stop前费用写成泄漏。

启动/构建失败均保留：缺mach_task_self声明的两个构建失败；manager漏Qt插件路径；observer02在libSystem初始化前访问TLS；observer04的native interposer经TLS初始化递归进入malloc；reset首构建误将autogen扫描目标当C++对象；x86 reset观察首次preflight使用错误二进制目录、未启动子进程。修正范围限各自构建/审计runner，产品body未缩减。最新只读清点24 UE，比上批20新增四个启动abort；采样、ps、adjudication保留，未清理宿主。

## 保留的总出口与复用方式

只继续92 §16.88四组差集：全部owned及已识别外部owner的完整容量/并存peak/free总硬界、其余真实故障及共同终点、非Darwin实现和平台运行、最终manager/default abort/24 UE。非Darwin当前fallback仍按请求加前缀，缺真实usable/native规则，不能表述为“仅待另一台机器测试”。CP5公平/continuation与CP10性能归原包。

文本证据按内容寻址打包，原始工作文件保留；`evidence-bundle-manifest.json`将原路径映射到`evidence-bundle.tar.gz`中`blobs/<sha256>`，逐blob复核，二进制/dSYM不入Git。仍在运行的manager目录不打包可变日志，使用[冻结checkpoint](pending-manager-checkpoint.json)记录各1,979源码/107运行输入复核与日志前缀；最终结果后继提交。源码、命令、observer、失败记录和完整日志均保留，不用摘要替代原始证据。
