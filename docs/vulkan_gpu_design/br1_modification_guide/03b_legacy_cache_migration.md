# 03b：Legacy tile 缓存迁移的修改指南

返回[修改指南目录](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/README.md)、[设计与代码总表](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/CHANGE_MAP.md)和[S06 总体接线](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/03a_handoff_implementation_map.md)。本篇展开 **S06.3**，联动 S03/S04/S09/S10；契约来自 [92 §2–§3、§5、§10.1](/Users/apple/krita_gpu/docs/vulkan_gpu_design/92_br1_m6_m8_execution_baseline.md)。阶段资格仍只在 92 裁决。

定位依据为 `5173c807c87bb1619325249a07a8b4f4f8f09f09` 加 2026-09-27 当前工作树。本篇说明实际接线与剩余修改要求；同源码构建、测试和 allocator 证据统一见 92 §15 与本批 evidence，不以本文条目代替阶段验收。

## 1. 先确认当前代码边界

2026-10-05按[92 §16.113](../92_br1_m6_m8_execution_baseline.md#cp2-epoch-preparation-delivery)结算完整CP2代码/安全范围：§16.109–§16.112的raw/batch/G0/clone拒绝已由当前完整manager再次验证；真实epoch/晚completion与共同准备/原终结见[完整审查](../evidence/br1_cp2_epoch_completion_20261004/cp2-audit.json)。当前下一包为CP3/M6正式冻结。L10 idle强引用及其他业务consumer迁移仍随CP6–CP9推进，不能因CP2结算放宽refs/users/raw pin/Reserved；下方冻结定位和分批描述不覆盖当前排期。

| 当前代码段 | 实际关系 | 继续实施的边界 |
|---|---|---|
| [bridge 接口](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTilePageStoreBridge.h:17)与[backend override](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.h:139) | 四参数声明、定义和 caller 一致；§16.111删除无生产consumer的oldData参数；`Access` 替换原 writable 布尔，明确 ReadSelection / ReadCache / Write；`ReadPinResult` 保留四种物理 pin 结果 | ReadCache 只能复验原 expected 并借原 iterator mutation，不能选择最新 current 或准备新页；意图枚举不成为状态权威 |
| [provider cache 与 factory](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:144)、[native/generic factory](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:878) | factory 只从有效 guard/lease 导出 binding 与 expected；native 还核对同 provider 的实际 binding 对象；每次 repin 由 binding gate 校验 | 闲置 candidate 不持 root/RAM pin，也不拥有 TileData；wrapper 的既有 COW 引用仍提供存储寿命 |
| [binding::readIdentity](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp:334) | 已由 native factory 消费；检查 reader、retired、version 后导出 expected | 该私有 helper 不成为通用授权入口 |
| [KisTile::lockForRead](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:349)、[refreshPageStoreData](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:143) | canonical cache 暖读重新取 pin；真正失配拒绝，不跳到最新 current；final unlock 保留缓存存储、释放 pin | retired binding 不再复用，其 wrapper 仍拥有的原 COW bytes 可继续作为 immutable 存储读取。移除 idle 强引用前必须替换这项寿命保证 |
| [writer 的未来缓存](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1548)与[batch 终结](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:410) | 独立与 batch 写共用有效 guard 下的 expected 准备；final unlock 归还 guard、保留 dormant hint；原 batch 内读取重新借同一 mutation，嵌套写复用该 guard | Reserved 仍排斥普通/foreign reader，hint 不持 batch/root/RAM pin。已准备 target 的缓存/lease交接拒绝由原 batch 取消；原 exact 重解析、其他 raw consumer 与 idle 引用迁移仍开放 |

§16.111的[当前G0交接](../92_br1_m6_m8_execution_baseline.md#cp2-tile-selection-delivery)先取得原ReadPage，直接从有效capability取得TileData并建立只读COW wrapper；presence由同一read导出。独立old wrapper无backend/root/idle cache，写锁在原barrier中拒绝；getter失败不交出wrapper。attach helper及bridge oldData参数/旧caller全部删除；旧字段只保留只读事实，不承担读取选择。

[§16.112的clone交接](../92_br1_m6_m8_execution_baseline.md#cp2-clone-refusal-delivery)先准备canonical clone，拒绝沿原std::bad_alloc构造终点，legacy源继续legacy；空backend回退删除。三Tile复制构造共用原init空值拒绝，chained复制与lock-free已有委托/正常析构政策收为同一规则；extent先于局部RAII交出，native memento登记退出旧索引。未暴露字节的intent仍允许克隆原版本，已暴露anonymous write明确拒绝；两模板部分失败/重试与真实raw拒绝验证不放宽refs/users。

之前“provider 只有声明、backend override 不匹配”的草案已被上述接线取代。原 parked batch wrapper 的再次读取按 [92 §16.110](../92_br1_m6_m8_execution_baseline.md#cp2-batch-read-delivery)收口；完整 legacy 迁移仍包括其他 batch/raw 交接、失配后原选择的保活/重解析、idle 引用及所有 raw consumer，不能只靠 canonical 缓存测试关闭 S06.3 或 M6。

## 2. 把四种责任分清

2026-10-04 的 [CP2 raw 准入交付](../92_br1_m6_m8_execution_baseline.md#cp2-raw-access-delivery)将 `data/tryWriteData/tileData/setData` 的首次写暴露统一到原 `markPageStoreWriteDirty → ensurePageStoreWriteAccess`。真实拒绝时返回空指针或不复制，caller 仍归还原 intent；copy/purge 的嵌套读用原局部 scope 统一解锁，两种序列化 codec 返回既有 `false`。iterator/wrapper 已有空结果处理继续使用。该交付不取消 batch Reserved/raw pin、wrapper 的 COW 引用或原 exact 保护，L5/L6/L10 的剩余迁移条件保持。

| 事实 | 唯一责任位置 | 缓存可保留什么 |
|---|---|---|
| 读取哪个 logical version | 既有 read scope、history/current 选择和 PageStore | 由有效选择导出的候选；不能用旧地址猜测版本，也不能失配后偷偷读取最新 current |
| allocation 的 provider/epoch/slot/generation | provider 的 stable binding | expected identity；它是校验输入，不是第二份可写 generation 记录 |
| 当前是否允许解引用 bytes | binding gate 下取得的有效 read/write pin | 本次外层 lock 的短 lease；嵌套 lock 复用，到原外层 unlock 才释放 |
| 解锁后的存储寿命、copy 与 detached tile | 既有 TileData 引用/COW 及原 raw consumer 的生命周期 | 本次迁移先保留现有保护；只有逐个消费者迁走后才能移除 idle 强引用 |

普通 manager cache 不永久保留整个 captured root。需要精确旧版本的 oldData、copy/source 和活跃 reader 仍须具有真实保护，不能为了 handoff 命中率移除它们。明确区分“缓存记住候选”与“读者保留版本”。

## 3. 待改内容 → 函数段 → 必须联动的终点

下列 L 编号仅为 S06.3 内部定位，不新增阶段。主改、调用者和失败终点必须在同一批中对应起来。

| 段 | 主改代码段 | 具体改法及联动终点 |
|---|---|---|
| L1：签发紧凑缓存 | [Tiles3ResidentBinding](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:67)、[tileDataForCpuReadGuard](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:872)、[tileDataForLease / tileDataForCpuWriteGuard](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiles3PageReplicaProvider.cpp:1205) | 当前由 `Tiles3TileReadCache` 和三处 factory 消费既有 guard/lease，只从有效 native guard、有效 generic read lease 或有效 writer 导出 binding/expected。读缓存初建时原 guard 不先释放；writer 仅准备未来候选，finish 前不授予读 pin。缓存对象无 PageStore/root/逻辑写权限 |
| L2：每次读取重新取得权限 | [binding::acquireRead / releaseRead](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisCpuResidentBinding.cpp:149)、[bridge lease](/Users/apple/krita_gpu/krita/libs/image/tiles3/KisTilePageStoreBridge.h:18) | 本次 expected 校验与取 pin 在同一局部 gate 内完成；`tileData()` 只在有效借用期暴露。区分 stale/retired、Busy、NonResident，现有 `ReadPinResult` 区分身份失配、退休与暂时不可用；Busy/资源失败保持失败语义，不能转读 current |
| L3：backend 读冷路径 | [acquireTile 读分支](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1486)、[tileDataForReadPage](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:2310) | 复用已取得的 `KisPageStoreReadPage` 签发 cache；不为转换再 capture/read 一次。当前 `readCacheForPage` 只做 adapter。保留 default 稀疏读取，不因统一接口强制物化默认页 |
| L4：manager 安装缓存 | [refreshPageStorePage](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1058)、[installPageStoreReadCache](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:81)及[声明](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.h:84) | 当前接收已签发缓存，在原有效 pin 下取得存储引用；安装后释放短 pin。`takeIdleReadCache` 复用闲置对象并先清 ready，转移过程中不能落回未验证的暖读。tile 正被借用时不得替换其已暴露 bytes。该 exact 安装现保留于兼容失败回滚；成功 delta 已改存在性查询/缓存失效，见 [S03 MR3–MR4](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/01d_metadata_refresh_and_pending_visibility.md)。raw consumer 迁走前不能取消失败后的立即字节恢复 |
| L5：KisTile 暖读取 | [lockForRead](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:349)、[refreshPageStoreData](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:143) | 复用原 ReadLease 槽，外层 lock 先校验 expected 并 repin；暖命中不新增 generic request、provider 全局查找或 root capture。嵌套借用保持原指针；真正失配当前拒绝；未来重解析必须使用原受保护读取语义，不能单凭 ready 标记放行 |
| L6：写后缓存复用 | [ensurePageStoreWriteAccess](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:420)、[backend lease 构造与 finish](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:183)、[backend 写分支](/Users/apple/krita_gpu/krita/libs/image/pagestore/KisTiledDataManagerPageStoreBackend.cpp:1548) | 独立与 batch 写共用 expected 准备；batch 内读先确认原 mutation 已有 target，再 beginWrite 复验并借回原 guard，foreign 拒绝。nested read→write 移交同一活跃 guard，旧 immutable reader 的 pin 不被挪用。无后续 tile cache 的 bulk caller 不强制新建缓存；取消后的 hint 不标为已提交读结果 |
| L7：释放与活跃状态 | [releasePageStoreLeasesLocked](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:118)、[hasPageStoreLeases](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.h:154) | “有缓存对象”与“有活跃 lease”分开。最终 unlock 释放 read pin，保留可复用的闲置缓存；write finish 沿用原唯一终点；失败恢复责任的完整迁移仍属 S01，缓存移交本身不授予终结资格。`m_oldTileData`、barrier pin 与 nested lock 一起核对，不能多减 lock counter 或重复 unpin |
| L8：detach/dead 与存储寿命 | [notifyDetachedFromDataManager / notifyDeadWithoutDetaching](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:213)、[copy 构造与析构](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:172) | 断开失效 bridge/闲置缓存，已有借用保留至原 unlock；detached tile 继续代表其原存储，不因下次 read 连接到相同坐标的新页。manager 回调放在 tile 局部锁外；不得遗留悬空 backend，也不能提前释放 clear barrier 保留的 pin |
| L9：默认值与 immutable 特例 | [getTile](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:309)、[getOldTile](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:347)、[write lock](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile.cc:487) | batch再读由§16.110借原mutation；§16.111旧G0独立只读存储不保留bridge/cache，attach与旧选择布尔删除。new writable miss仍只是intent；普通default/immutable真实存储保护不放宽，不把默认读取改成逐页分配 |
| L10：后续解除 idle 强引用 | [TileData 引用与 pin](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data.h:35)、[raw wrapper](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_wrapper.h)、[copy 源使用](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tiled_data_manager.cc:1229)、[physical claim](/Users/apple/krita_gpu/krita/libs/image/tiles3/kis_tile_data_store.cc:331) | 先列全 copy/source、alias、preclone、swap/compressor、iterator 与 detached 消费者，再将 idle 可重建缓存与真实保活分离。L1–L9 本身不允许放宽 refs/users 检查；待 raw 消费者闭合后才能让“缓存仍存在但未借用”不再阻止合法 handoff |

## 4. 读取语义与失败出口

| 入口 / 情况 | 允许的处理 | 禁止的简化 |
|---|---|---|
| current cache 身份仍匹配 | 本地 gate 取短 pin，返回本次借用 | 每次暖读重新走完整 generic request |
| exact read / oldData 身份失配 | 从仍受保护的原 version 重解析；无法证明时返回现有失败结果并保留必要寿命 | 用当前坐标最新页替代 G0 或原 captured version |
| Busy / NonResident | 沿既有等待、驻留恢复或明确失败语义；等待时不持 owner gate | 将 Busy 当 stale 删除有效选择；为了读缓存占住全局锁等待 I/O |
| writer finish/cancel 失败 | 保留原事务/取消 owner 的恢复责任；不可用 cache 不对外授予权限 | 缓存对象存在就报告写成功，或释放唯一终结记录 |
| detach / clear 后旧借用仍活跃 | 维持原字节与 pin 到原 unlock，之后依独立存储语义访问 | 旧指针 republish 到新页面；提前 unpin 造成 swap 后悬空指针 |

纯 candidate 不保证逻辑版本仍受保护；对 oldData/exact 的保护责任必须能追到现有 scope/history owner。若某个长期 wrapper 没有这条责任链，先保留其真实物理保活，不能伪造“按原版本重解析”的能力。

## 5. 修改顺序和每批验收

1. **L1–L4 联合接线：** 已有定义/声明/override/caller 同步；后续保持provider factory 只接真实 guard/lease，manager 安装不增加重复读取；先证明构建与冷读/default 行为。
2. **L5–L9 联合迁移：** canonical 暖读 repin、独立写后复用、最终 unlock、嵌套读写与 detach/clear 已有消费者；batch borrow、G0 getter交接与clone/hash拒绝由§16.110–16.112结算；接续生产epoch/ABA/晚完成联合时序及共同plan全部实际准备拒绝。仍保留 TileData 强引用保护；这批只能宣告身份缓存迁移，不能宣告 idle-cache handoff 已开放。
3. **L10 解除真实阻碍：** 每个 raw consumer 逐一落实 lifetime/pin；再证明闲置可重建 cache 存活时生产 handoff 可发生，活跃 reader/source 时仍拒绝。不得凭减少 refs 数值宣布完成。
4. **回到 M6 总出口：** 联合生产 selector、独立 before、取消、epoch/ABA、资源/退出与真实性能取证；M7/M8 仍分别验收。

| 验证入口 | 须新增或扩展的场景 | 直接证明什么 |
|---|---|---|
| [身份缓存寿命测试](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:4516)与[resident read 复用测试](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:4128) | 冷读后 1/10/1000 次外层锁；暖写→读循环；带有效正控制的 allocator 观测 | 暖读无新增 request/capture/缓存分配；不能只用 request 计数推断零分配 |
| [virtual default 测试](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:827) | 稀疏默认值、uniform clear、只取得 write intent 未暴露数据 | 无新增默认页物化，未写不产生新 payload |
| [clear barrier 测试](/Users/apple/krita_gpu/krita/libs/image/tiles3/tests/kis_tiled_data_manager_test.cpp:4726) | 已借出 read/write、clear/detach/dead、原 unlock、detached 私有写；补 nested read→write 与失败路径 | 指针直到原 unlock 有效；旧事务不能复活，pin/ref 最终归还 |
| [tileReadCacheLifetime](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStorePhysicalClaimTest.cpp:180)与其他 PhysicalClaimTest | 错 provider/epoch/generation、reader 先到/claim 先到、swap、retire、late release；L10 后增加 idle wrapper 存活 | 物理排斥与身份校验一致；原语测试不代替生产 root 链 |
| [ResidentReadTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreResidentReadTest.cpp)和[CpuMutationTest](/Users/apple/krita_gpu/krita/libs/image/tests/KisPageStoreCpuMutationTest.cpp) | 原 exact/G0、当前页发布/取消、旧缓存失配、provider 撤销、压力与 close | 原版本语义不变、没有永久 root/RAM 保活或无人归还的资源 |
| [V01](/Users/apple/krita_gpu/docs/vulkan_gpu_design/br1_modification_guide/07_validation_and_migration.md) | 同源码双架构、layout/ownership/调用图、真实 stroke 主桶与 Fresh 控制桶 | 新证据绑定新源码；局部缓存收益不能替代 stroke/BR1-PERF 资格 |

交付记录写明 `L编号 → 实际符号/调用者 → pin 与存储 lifetime → 成功/失败/取消终点 → case/命令/源码身份`。更新本篇、CHANGE_MAP、CODE_INDEX 及 92 的记录时，不将尚未接线声明或未运行测试写成已完成。

2026-09-27冻结的16个manager场景覆盖 1/4/8/16 BPP 的暖读/嵌套、swap、独立写后读、detach、实际 hash 替换和 oldData purge；12 个物理场景覆盖缓存复用、pin 排斥、Busy、retag、retire/revoke。真实暖读 allocator 探针定位 [warm-tile-read-allocation-probe.cpp](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s06_legacy_identity_20260927/warm-tile-read-allocation-probe.cpp)。这些范围不包含完整 batch borrow、idle 引用释放或产品 stroke 性能；最终结果与身份见 [本批证据](/Users/apple/krita_gpu/docs/vulkan_gpu_design/evidence/br1_s06_legacy_identity_20260927/README.md)。
