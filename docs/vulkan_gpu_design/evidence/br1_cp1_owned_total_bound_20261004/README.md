# CP1 owned 存储总硬界清点（2026-10-04）

本检查点绑定产品 `0933ea04ddbe8bb58c04dc891d864be8cd95d778`，父 `02a92eb98d4ccfa02462f59ec04999bf7873dedb`。它沿 §16.97 的清单第一项，核对当前 BR1 CPU/PageStore 生产路径仍存活的动态 owner，并把既有实际 capacity 压测、§16.95 原生控制边界、§16.96 `live/reserved` 转换及 §16.97 memento 修复合并为当前源码的总硬界裁决。产品代码和产品测试改动为 0。

## 当前 owned 清点

[逐项清点](owned-storage-audit.json)覆盖 backend facade/Private、Store/provider/history/completion 根、history/thread/source map、write batch、iterator scope、read scope、lease/read cache、uniform source、memento、extent 及操作内 transfer storage。每一项要么继承 `KisPageProcessStorageObject`，要么由 `KisMutationStorageAllocator`／`KisPageByteArray`／process PMR 持有；memento 对象及 old/new 默认像素由 §16.97 的 process 工厂补齐。释放均沿原对象、shared/weak control 或物理 allocator 的最后引用执行，§16.96 只在物理 free/join 后撤销 live 费用。

源码复核也列出三类不重复收费边界：

- `KisTiledDataManager` 自己的 hash/memento manager、默认像素、Tile wrapper 和兼容安装候选属于既有 caller adapter；PageStore 不取得第二份所有权。
- API 输入、输出 `QVector`/`QByteArray` 和 `PreparedTileUpdates` 是调用者操作内存储，在进入像素或发布前准备并由 caller 销毁。
- Surface/BackendService/EvaluationGraph 原型和 `KisUnifiedSsdPageStore` 持久化记录没有 BR1 CPU 产品 consumer，继续归 BR0/BR3 或测试边界。

因此当前 BR1 CPU/PageStore 的完整 owned 硬界是一个不重复求和的联合界：控制存储只进入 product process metadata budget，按 `live + reserved <= limit` 准入；TileData 物理 payload 仍由原 provider/ledger 的 logical、resident、history、pending、retirement 各域硬界约束，同一 backing 只收费一次。caller adapter 与产品输出不加入第二份 PageStore 费用。

## 证据复用与当前增量

- §16.87 当前祖先产品 `6ddccc3097` 的实际 capacity 交付已经在普通双架七套件 **5,908/0/0**、8/24 MiB 业务压力 **14/0/0**、TSAN 七套件 **2,954/0/0** 和双架各 72 次物理 span 中通过；它关闭 allocator request 与实际 native capacity、最后 physical free 的差异。
- §16.95 当前祖先关闭首次外部 pthread 合并误收费；§16.96 当前源码分别验证 reserved/live、并存 peak 和 physical free；§16.97 当前源码补齐唯一新增的 PageStore memento 普通堆 residue，并在完整 CPU/Reference normal 双架及 TSAN、完整 manager normal 双架通过。
- [当前增量核对](source-delta-audit.txt)确认 `6ddccc3097..0933ea04dd` 的 PageStore/tiles3 生产分配新增只有已结算的 memento process 工厂、TileData 生命周期修复及原生线程计费修复；没有新的未分类 PageStore owner。当前两个仓库 tracked tree 在核对前均干净。

本检查点不把不同源码的测试数量相加为新的整阶段运行；它以祖先源码逐文件不变或后继专项证据绑定的方式关闭“其他 owned 分配 + process/native 子管线总硬界”这一清单项。已完成的长压测不重复运行。

## 剩余

完整 CP1 仍未关闭。剩余三组为：其余 node/control/task 真实 allocator fault 与其他线程、read/publication/晚 fence/caller 的共同终点；非 Darwin 实际 capacity/free 实现及平台运行；29 个历史 UE 与默认 abort 可回收资格。M6/M7/M8 正式资格保持 0/3，persistent 默认关闭。
