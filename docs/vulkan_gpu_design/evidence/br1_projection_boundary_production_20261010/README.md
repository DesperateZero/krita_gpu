# 投影 clear / 首层合成：生产交付

产品提交 **8198c36ed7**（父 c13c442493）；原型已替换为原 merger → plane → painter 内的生产实现。本机 ARM64 固定同义用例中，最终独立16块/64进程确认 **Stroke CPU节省1.20375ms，pointwise 95% [0.922,1.781]ms，逐块相对节省中位7.33%**；wall节省0.51025ms [0.371,0.7265]ms。保留当前代码，不依赖环境开关或实验 pending TLS。不是发布到外部应用，也不代表M6整体资格通过。

## 实现与必要边界

证据归属补充：上面的1.204ms是BR1分支内融合前后收益；没有测量upstream采用相同通用融合思想后的收益，不能作为PageStore本体算法或相对同策略upstream的效率证据。当前基础性能优先级与比较设计见[92 §16.171](../../92_br1_m6_m8_execution_baseline.md#pagestore-equivalent-performance-scope)及[证据分账](../br1_pagestore_comparison_scope_20261010/README.md)。本补充不改变本包原始测量、有限产品实现或未通过的阶段控制。

完整算法和唯一B01–B11矩阵仍在[原方案](../br1_projection_boundary_trial_20261010/BOUNDARY_PLAN.md)，本包只保存证据及结论。

```text
原 merge owner / 稳定图及输入
  ├─ temp、复杂层/自定义类型、额外源投影、不可见、空源 → 原 clear → 原 visitor/plane/composite
  └─ 具体独立首 paint layer → 当前 leaf 栈上的 clearRect → 原源更新 → 原 plane 参数
       ├─ painter 不支持或旧清除域不能包含在实际 paintRect 内 → 原 clear + bitBlt
       ├─ 旧清除域为空 → 原 bitBlt
       └─ 原 native operation（只准备原合成页集合）
            → 初始化旧清除域 → 原 over kernel → 原 finish / seal / adapter
            ├─ 未进入回调就拒绝：原 clear + bitBlt 一次
            └─ 回调已进入后失败：原撤销 → 完成 clear 效果 → 原错误上下文；不重放合成
原 write/reset、clone通知、scheduler完成及取消权威不变
```

进入融合必须是具体 `KisPaintLayer` / `KisLayerProjectionPlane`，无下层依赖、effect mask、style、temporary/onion-skin投影；源非空且与更新域相交。painter保留over、等format、零default、独立data manager、无selection/stroke owner/wrap等条件。旧extent是矩形，不能当存在页集合；要求`clearRect ∩ target extent ⊆ 实际裁剪paintRect`，故不为clear-only稀疏页扩大准备集合。公共clear与普通bitBlt合同没有修改。

新增准备页数上界为0，不等于物理峰值增加为0：全页原clear可能先释放旧页，融合仍持有原before。候选继续受原真实预算/claim保护，准备拒绝可退回原序列；不增预算、不保留延期设备引用，不新增队列、owner或恢复域。原型自建TLS已退出，既有stack failure context仍使用原有TLS错误桥接。

`tryNativePixelOperation`仅供原friend painter使用，候选尝试不允许下层legacy fallback，避免像素回调已执行后隐式重放。所有prepare/claim/seal/adapter机制及其锁保持原实现。真实合法失败在publication前处理；prepared adapter安装依赖既有完整预备、保护和manager写锁，没有新增“发布后补分配”路径，也没有把发布后人为throw当合法失败。

## 验证与全部失败

最终r1同一产品构建在ARM64/x86_64各 **880 passed / 0 failed / 0 skipped**：完整painter742、merger13、projection3、相关manager122，合计1760。覆盖RGB8/16、partial/sparse、透明非零RGB、opacity/channel/offset、空/小源、空目标、default/selection/wrap/alias/borrow回原路径；固定旧view和当前view在初始化前、像素回调后尚未发布时均稳定；history revert以及现有并发/取消控制通过。新增自定义paint层visitor读取反例确认需要clear cut的层仍走原顺序。

失败测试分别注入准备bad_alloc、真正kernel改首块后bad_alloc、finish但未publish时bad_alloc、既有failed上下文；验证clear效果、无已执行compositor重放和后续写可继续。真实进程payload硬满下，整页与partial两种原路径/候选均拒绝且像素效果一致；原reservation及活跃写归零，压力释放后重试成功。没有据此宣称所有满额情形原操作都能成功，也不宣称全配置/全平台正式矩阵已完成。

原始失败均保留：`build-core.log`为本机PATH没有cmake；`build-tests-r1.log`为新增测试误把非virtual函数写成override及pixel调用签名错误；`tests-new-r0.log`两个borrow失败来自测试错误假定原clear在活跃legacy写者下应成功，修正为两臂相同冲突/失败合同后通过。诊断phase observer抛异常仅作为本次一次性fault，异常后不依赖该recorder继续通知；未改生产诊断器。

r0生产候选首轮也完整保留：Stroke CPU节省1.23975ms [0.77775,1.786]，但Undo CPU回退27μs [10,64]、wall回退32.25μs [6.5,60.5]。量上Undo无融合工作，代码却把空源clear推迟到plane阶段；r1明确恢复空源原顺序，并承担一次eligible source extent读取。修正前后样本没有混池，r0没有被删除或改判通过。

## 数量、预测与最终独立定价

r1两父/两候选观察库均验证：19 merge / 19 composite保持；独立fill **13→0**，成功冷准备 **132→96**，新batch / successful seal **32→19**，13次融合、失败0，初始化566464B。Undo仍1 fill / 1 batch / 1 seal，Redo仍1 composite / 56冷准备 / 1 batch / 1 seal，没有新增初始化。commit随调度变化，不作为固定删量。父观察库为旧c13派生且FUSE=0；新观察库只插计数，未改算法；计数时间不参与定价。

事前预测0.5–1.5ms为宽工程范围，主点1.204ms落在其中；相比旧受限原型1.058ms高0.146ms（约13.8%），不是同批两候选显著性比较。36次冷准备、13套batch/seal的预测均完整兑现。各阶段使用固定块内两进程均值差、块间中位，bootstrap50000次/seed20261010；正数表示节省：

| 阶段 | CPU节省ms [pointwise 95%] | wall节省ms [pointwise 95%] |
|---|---:|---:|
| Setup | −0.28775 [−1.81225,1.23025] | −0.571 [−2.4195,4.186] |
| Stroke | **1.20375 [0.922,1.781]** | **0.51025 [0.371,0.7265]** |
| Undo | −0.01825 [−0.051,0.028] | −0.01025 [−0.046,0.021] |
| Redo | −0.02175 [−0.0465,0.023] | −0.014 [−0.038,0.0245] |
| Teardown | −0.0095 [−0.047,0.0145] | −0.00625 [−0.03625,0.0045] |

主端点超过事前δ0.5ms且区间下界>0，增量价值成立。控制阶段没有单独区间排除0的回退信号，**但Undo/Redo/Teardown点估计仍稍慢，严格≤2%非劣未证明**；不能将“区间跨0”写成“无成本/已消除回退”。r1不证明r0的27μs全由clear顺序造成；数量相同也不证明跨阶段释放与调度完全相同。本轮有限确认到此停止，不追加无改动样本，不事后放宽门。

全部64个最终进程像素/undo/redo哈希、8segment/4显式callback、有效projection输出和对象销毁均通过，实际加载库/同批依赖一致。CPU为进程user+system，wall到projection-ready，非canvas-visible。源码在提交前编译测试，提交8198与该被测dirty patch逐文件相同；二进制与生成构建身份另冻结，不能仅用HEAD代替。提交改变git构建元信息后，Ninja dry-run提示CMake再配置，未宣称提交后构建no-op，也未覆盖被测库。

## 技能与阶段裁决

本轮补齐“中层边界假设 → 理想路径 → 代码索引 → 有限实施 → 安全/资源反例 → 独立收益”的生产正例。其价值来自避免产生整套维护工作，而非再调一个小memcpy。分支控制也找到并修正了无融合收益路径的时序改动。

仍不证明全局榜首、整链算法最优、调度无多余成本或精确预测校准；也没有新upstream对照，不能从旧7–9ms差额直接扣1.204ms。安装skill不再改正文；本次结论可作为它的生产正向样例，严格阶段非劣仍独立开放。

**生产实现、安全反例及局部净收益已交付；M6/M7/M8仍0/3，persistent默认关闭，原校准2/20、metadata分母、CP0 required和其它正式资格不变。** 后继应按92的正式门及完整业务控制补证，不重新领取本包36次冷准备/13套生命周期，也不继续原型TLS。

## 可复算证据

- [事前协议](PROTOCOL.md)、[最终确认前登记](PRE_CONFIRMATION.md)、[空源修正协议](R1_PROTOCOL.md)。
- [最终结果JSON](summary-r1.json)、[r0完整负控制](summary-r0.json)、[运行器](run.py)、[分析器](analyze.py)、[只观察派生构建](build_observer.py)。
- [验证/构建与提交绑定](verification.json)、[归档清单](raw-manifest.json)、[全部原始证据](raw.tar.xz)、[归档校验](EVIDENCE.json)。raw含原库/两版生产库、观察库、源码patch与最终源码、所有过程stdout/command/env/runtime hashes、失败、测试及构建日志。运行二进制依赖原工程工具链及安装目录，依赖身份冻结，不声称脱离该环境即可运行。
