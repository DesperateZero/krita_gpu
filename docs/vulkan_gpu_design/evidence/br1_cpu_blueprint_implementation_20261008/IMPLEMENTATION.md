# 03d 实施责任与投影合并的准入结论

本包沿 `PLAN.md` 的有限实验，不恢复03c已回退的pin重排。量化基线见前包 `br1_projection_cost_attribution_20261008`；以下结构结论以本包冻结源码为准。

## A：原默认页构造内的批量填充

`KisTileData::fillWithPixel` 是private，仅默认构造在 `allocateData` 成功后调用。strided构造按行复制，copy构造整页复制，均不调用它。既有Store/provider/legacy caller仍经原构造；没有新的共享可写默认页或跨调用缓存。以一个像素为seed，每次从已初始化前缀复制到其末尾，复制区间不相交；4096像素共seed一次与12次倍增，目标字节总量保持4096×pixelSize。

| 责任 | 原路径→候选 | 保持的终点/新增成本 |
|---|---|---|
| 初始化 | 原构造→4096次动态长度memcpy，改为原构造→13次块memcpy | 原分配、收费、失败、释放；同样写满整页，读源改为已初始化页前缀 |
| 使用者 | provider default、Store default、legacy default共用原private函数 | 全部无需迁移签名；copy/rows不改 |
| 验证 | 18个真实Store字节oracle，BPP 1/2/3/4/6/8/12/16/32×零/非零 | 偏移源、隐藏非零色字节、源修改、独立页、三轮回收；没有测试专用生产API |
| 生命周期 | 原TileData owner | 公共/保护/私有函数、字段、owner、锁、TLS、队列新增均0；仅新增标准库algorithm include |

在观察到116次默认填充且更新同量的stroke中，理论请求从475136降为1508，少473628（99.6826%）。这是调用数量，不是速度倍数；原约1ms CPU预算仍要扣新填充和调度效应。候选性能主结果保留一例18更新，不能把116次诊断直接冒充该过程的实测调用数。

## 安全阻塞：原pin拥有标记未与最后读者一起退出

实际low-memory用例在fill-only候选发生 `bitBltRoughImpl<false>` 的空backing memcmp。LLDB单次未复现不抹去失败。确定性反例随后在父库及fill-only库均失败，支持这是原生命周期缺陷；不能仅凭一次父库压力通过将其归因于填充。

```text
未暴露write intent取得native pin → 嵌套reader
→ writer先退出 → reader最后退出、归还物理pin
→ 旧代码仍保留“write intent拥有native pin”标记
→ 下一轮reader取得ReadLease → writer取得新代际
→ stale标记驱动多归还旧backing的pin → 活跃reader期间可被swap
```

第一版在原 `KisTile::unblockSwapping` 最后native解锁处一起结束物理pin和原拥有标记，删除 `unlockForWrite` 中的重复native终结分支。独立8配对测到stroke wall增加4.12%，且源码确有未暴露writer释放/重新取得已有swap barrier的新增工作；不能声称零成本或把它算fill收益。

最终将原私有函数完整替代为 `unblockSwappingLocked`，四个caller全部迁移：read/write正常退出在已有barrier锁域内终结，两个legacy COW失败出口先显式取得该锁。原物理pin、旧TileData清理与拥有标记在同一原锁域完成，不再退出锁域后重取。相对父库，未暴露writer仍一次锁域，native读/普通native写退出由两次降为一次；已暴露PageStore lease仍走原 `releasePageStoreLeasesLocked`。私有签名一增一删、净0，公共/保护签名、字段、owner、锁实例、TLS、队列新增0。最后native解锁多一次清零原bool；实际时间仍以独立有限批为准，不将第一版全部回退预先归因于锁。

MI1–MI8：仅原tiles3责任；上层API/依赖、事务、scheduler、finish/cancel/undo均不变。原Tile继续唯一负责锁/pin寿命，失败沿原拒绝与取消；删除重复终结，不增加第二释放域。生产私有签名一增一删、净0，字段/布局不变。测试slot和证据派生库另列；switch的环境选择只在证据派生库，不进入产品。

## B：36条同merge重复冷准备仍不能直接领取

| 实际消费者/边界 | 当前行为 | 对理想融合的约束 |
|---|---|---|
| `KisAsyncMerger::setupProjection` | parentOriginal先clear；临时投影路径则prepareClone | 两条路径不能仅凭当前简单RGBA8用例合并 |
| `startMerge`中的original visitor/recalculate | 在clear与composite之间执行；N_EXTRA与dependsOnLowerNodes有独立路径 | 必须保留中间读选择与前序层结果 |
| `KisUpdateOriginalVisitor::visit(KisAdjustmentLayer*)` | 读extent、copyAreaOptimized、filter->process，selection还读取/复制中间投影 | 真实消费者，不是可忽略的回调；共同pending不能无条件暴露为current |
| `KisLayerProjectionPlane::applyImpl` | 按opacity/channel/composite配置执行原painter bitBlt | 不是所有层都可退化为copy；须预备全部目标并保持操作顺序 |
| backend `fillRect` | 全范围claim、独立batch、adapter准备、before view、稀疏default/no-op、最后联合安装 | 先前clear的独立失败终点不可凭共享transaction消失 |
| `runCpuMutationOperation` | 无historyOwner时新batch；有owner时借原historyMutation | clear没有相同owner入口；简单绑定persistent owner不能覆盖两者 |
| `beginMutationBatch` / `Private::finish` | 每次新mutation，每次seal，最后anonymous client决定事务终结 | transaction身份偶尔相同不代表pending跨operation保留 |
| root retention / captured reader | epoch root另保旧版本，clear自身持before | page captured=false、单replica不能证明backing可原位覆盖 |

132→96、copy72→36、fill60保持，仍只是满足全部条件后的数量目标。匹配36条冷准备约0.469～0.491ms CPU，其中copy体0.022～0.023ms。新增owner借用、读选择、预备、取消和联合安装的成本未知；因此本包**合法已删集合为空，B净收益未授予**，不拿A收益填B矩阵。

下一结构方案必须在首字节前确定完整作用范围，明确所有中间读者读哪一版、每个失败点保留哪一结果、joint publication如何迁移原adapter/canonical/extent，且扣除新增代价。简单无依赖层的受限入口若值得实施，也必须由实际模式/consumer资格验证；不能凭一个测试preset开启。当前约0.48ms的局部预算不支持承诺关闭约一倍的upstream总差距。

必要代际单价方向也要先定价。当前publication的 `prepareDescriptorAdditionsLocked` 已复用相等的不可变descriptor值，不能再把“加一个descriptor缓存”当新方案；`prepareWriteBaseLocked`及分配后重新查询还承载base/并发复验。后继应找相同事实在同一有效期内的重复构造，并用独占成本给价，不能先删合同再测速度。
