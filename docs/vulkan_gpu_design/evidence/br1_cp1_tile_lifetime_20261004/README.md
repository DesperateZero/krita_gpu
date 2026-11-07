# CP1 TileData 原分配、候选、交换与释放生命周期（2026-10-04）

本目录绑定产品父 `87a8b43ae98bcf13fb437ee7fe2b941701035fe3`，实施范围只有 TileData 原分配到物理释放的一条生命周期：原 Store 取得 resident reservation，构造/复制候选，登记；pooler 产生可选 preclone；swapper 取得 iterator 和候选 pin；swap store 分配 chunk、压缩/解压并转换 resident 状态；最后由原 TileData/cache/Boost pool 释放。没有新增 owner、队列、持久状态、字段、公共/保护 API 或测试专用产品 hook。

## 原反例

`baseline-results.json` 在87a原库上执行8种 control/fault × arm64/x86_64，共32个实际进程。16个 control 全部实际0；真实 `malloc` 拒绝中，default、rows、copy、clone-payload 共8次触发 SIGSEGV，cache-node 2次触发析构中的 terminate，clone-node 2次遗留 payload 和 swap pin，iterator 2次遗留 iterator gate；swap-in的2次拒绝保持原 chunk、随后能恢复。即14个 fault 失败、2个 fault 原本安全。致命负例只用诊断信号退出，不能当默认退出通过。

额外夹具复现两项完整 owner 缺口。后台 pooler 在唯一一次 kick 后，真实拒绝12288字节的 clone backing 会在原 QThread 逃逸并触发双架构诊断退出101；构造但尚未登记的4BPP TileData持有原4194320字节 Boost block 时调用 `releaseInternalPools()`，旧实现会 purge 该活 backing，双架构均以诊断退出3停止在UAF读取之前。原像素地址、实际 malloc/free 和全部进程身份在 `extra-build.json`、`checks-03-old-*` 中保留。

## 最终责任形态

- `KisTileData::allocateData` 对所有 pixel size 把 native null 统一转为 `std::bad_alloc`。Store 的四个 nullable 分配/复制入口在原 reservation owner 内将该异常和登记异常收回为 `nullptr`；reservation、未登记候选和源 swap pin 由作用域 owner 释放。
- cache push 仍是可选优化；其16字节节点拒绝不再逃出 TileData 析构，原 backing直接回到 `free` 或 Boost pool。4/8BPP 改用 ordered allocate/free，使 `release_memory()` 有合法有序 free list。
- `releaseInternalPools()` 删除“复制所有活像素 → purge整池 → 再分配并写回”的失败窗口。它只清理少量 resident tile 的可选 clones、归还 cache，再由 Boost 仅释放完全空闲的 blocks；尚未登记或仍存活的 backing 不移动、不释放。含活 chunk 的 pool block 因而可以保留到最后 owner 释放，这是安全语义和可能的残留内存成本。
- pooler 的源 pin、clone候选、iterator gate 和统计快照使用原对象的作用域清理；后台 `bad_alloc` 进入既有 timed cycle，无第二次 kick 即可继续。force-update失败保留上次完整统计。
- 三个 Store iterator 入口在构造失败时统一释放原 write gate。Swapper 的64项临时候选改为固定数组，iterator和全部成功 `tryRef()` 均由作用域清理；已完成 swap 的计量不因后续分配拒绝丢失，剩余工作由原同步调用或后续既有 kick 再取，不新增调度状态。
- swap-out在 chunk 接受前保留 rollback，只有释放 resident backing 并安装 chunk 后才提交；swap-in的临时像素在解压失败/异常时释放，旧 chunk保持，成功后才清除。原 bool 合同、锁序、aging和两遍扫描保持。

生产五文件当前相对87a为 **+198/−202，净减4行**；产品测试0/0。生成的 source/graph JSON另计。`source-freeze-03.json` 冻结196个源码输入、1444个外部编译输入和129个产品源；normal/TSAN各只重编五个TU并重新链接，六步均0，分别复用404/395个实际链接输入。第一次候选能构建但公开nullable入口尚未收回异常；第二次隔离构建因将private rows构造器误用 `make_unique` 而在编译阶段失败，均保留且没有进入运行资格；第三次是本文最终候选。

## 同源结果

`checks-03-results.json` 的最终候选在双架构执行8种 control/fault和两种额外 fault，共36个进程，全部实际0、已回收、无诊断退出：每个实际 fault 恰好命中一次；default/rows/copy 返回空且reservation/计量不变，cache析构安全，clone的payload/node拒绝释放源pin和候选，iterator拒绝释放gate，swap-in保留并恢复原chunk。后台 worker 拒绝后在无新kick时取得preclone，像素相同、最终0 tile；未登记4BPP backing跨 pool清理保持原地址/内容，最后owner和cache清理后观察到实际free。

完整CPU在arm64/x86_64为 **2772/0/0**；匹配插桩QtCore的完整CPU TSAN为 **1386/0/0**、无TSAN警告。原 Store/Pooler/SwappedStore测试普通双架为各20项、合计40/0/0，TSAN为20/0/0；24MiB pressure和8MiB cancel原freehand两架分别3+4项，合计14/0/0。x86 pressure首次与三条同名Freehand进程并发，争用相同QStandardPaths测试DB并在建索引时失败；换同一二进制哈希的唯一应用名串行复验3/0/0，原失败不计产品结果。

旧8f manager已实际结束 **1105/0/0、4371.97s、actual0/reaped**，插桩QtCore已加载；旧2e manager也实际结束 **1105/0/0、4348.24s、actual0/reaped**，插桩QtCore/KConfigCore均加载。两者结清§16.90的Pending记录，不迁作本候选资格。最终候选的完整manager见 `final-manager-01/`：绑定本目录第三次候选、2e测试前置、插桩QtCore/KConfigCore和补充1716个原Ninja输入，实际结束 **1105/0/0、4127.357s、actual0/reaped**，无TSAN警告；候选产品镜像及两项插桩依赖均确认加载。

架构图最终仍为87 TUs / 2172 APIs / 27412 edges / 27 callbacks，21 manifest / 25 ownership / 16 census / 19-file ratchet均保持；未增加PageStore生产触达面。

## 后继反例裁决

`kis_low_memory_tests::readWriteOnSharedTiles` 在父87a和最终候选的初始运行都于 `KisTiledDataManager::getReadOnlyTileLazy` 触发SIGSEGV；这两次运行复用了同一陈旧测试二进制。后继[ABI裁决](../br1_cp1_low_memory_20261004/README.md)取得可靠PC并证明测试对象仍按232B布局manager，而当前动态库构造288B对象；按当前头重建后双架原body各3/0/0、actual0/reaped。该项不是产品差集，本批五文件也无需为无效测试产物修补。探索中先并行启动的两条low-memory、一次未覆盖SIGSEGV的单跑，以及一次并行Freehand测试DB失败进入宿主UE，使只读计数由24增至28；这些进程不计通过，后续用信号守护和唯一测试应用名阻止继续增加。

本批只关闭 TileData/pool/iterator/preclone/cache/swap 的已复现实际拒绝和未登记backing释放窗口。完整CP1仍开放：全部owned/外部native独立reserved/live/并存peak/physical-free总硬界与首次native外部span；其他真实node/control/task、其他线程及read/capture/history/publication/retirement/close/晚fence/caller共同终点；非Darwin实际capacity/free实现和平台运行；28个旧宿主UE、默认abort及双native释放失败出口。Boost block保留和ordered cold-free成本尚未取得正式性能结论，归CP10；Swapper没有新增无输入重试保证，持续公平/continuation仍归CP5。M6/M7/M8正式0/3，persistent默认关闭。
