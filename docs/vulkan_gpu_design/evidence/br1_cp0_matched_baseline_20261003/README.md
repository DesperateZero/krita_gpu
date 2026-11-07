# CP0 同依赖 upstream 与普通 freehand 代表性基线

当前裁决唯一落在[92 §16.62/§17](../../92_br1_m6_m8_execution_baseline.md#cp0-matched-baseline-delivery)。本批取得一个真实可运行对照及有限dirty extent修复；完整CP0、CP1和M6/M7/M8/BR1-PERF仍开放。产品父提交`69a01e929abce246bfeed0603dbf0825088e28a1`，产品提交`cd6c8394a6e49b9758176f120efe49a5df02611f`，文档父提交`eb9cbccf00bb25a6f21fbac05a97399df4ac763f`，对应身份见[Git记录](git-round-identity.json)。未读archive、未push。

## 同源对照及测量范围

固定upstream `9a24ae0d8c070884fb013594191002e1a1b39a19`，独立checkout/build在workspace的`build/br1-cp0-20261003`。[upstream补丁](upstream-test-only.diff)只有测试CMake及两个同字节新测试文件；生产不改。双方共用原SDK stroke_testing_utils.cpp和preset，实际四份共享文件hash在[最终能力身份](capability-05-results.json)。[配置01](configure-01.log)因缺ALLOW_UNSTABLE失败保留，[配置02](configure-02.log)通过后[配置03](configure-03.log)匹配FOUNDATION_BUILD；[初始独立构建](upstream-build-01.log)完成全部七target，后续03–06构建独立夹具。不是旧目录里的QtBase baseline。

[15项实际选项](build-options-comparison.json)完全相同：Qt6.8.0、Xcode17/SDK26.2、RelWithDebInfo、x86_64;arm64、deployment12、FOUNDATION_BUILD、lock-free hash、PCH关闭。QtCore SHA256 `cd0a48d2948af55889625ae0750a7d08895068deae9b6e85bdc3e1fac6dc9434`。dyld证明各自image/ui/brush/LCMS来自各自build，79个common依赖路径及hash相同。current只选原build五个插件的独立symlink目录，upstream用其五个built插件；原capability-04扫描current全插件，额外加载mypaint/json-c而不匹配，保留但不能给配对准入。最终[127份运行文件](runtime-identity.json)绑定结果；[13份源码](source-identity.json)、[冻结检查器](freeze_evidence.py)及[输出](freeze-final.log)确认同源、选项、未修改upstream生产及原ratchet。

[运行前预注册](preregister.md)冻结512×512 RGBA8、五原paint layer、Buildup/OVER、48px circle auto brush、4 workers、8条固定pressure线段和4次正常update。原FreehandStrokeStrategy未opt-in persistent mutation；DataManager原constructor仍配置PageStore adapter，因此本current不是“整个adapter关闭”对照。SIMPLE入口采用双方相同lazy原registry，不初始化本preset不需要的全字体DB；没有手写像素kernel或修改production flag。

测到projection-ready并比较RGBA8888逐行hash，再测原command undo/redo排空和owner释放。setup、stroke、pen-up、undo/redo、teardown及fixture total分别记录；total包括转换/核对，但不含进程启动/全局资源注册/最后singleton退出。原KisImage析构先disconnect，最后strong引用通过原KisImageWSP失效验证。canvas-visible、实际dab计数、M/K/E拆分、峰值收费/全局缓存归零、正式P95/P99/95%CI仍未取得。

## 有限语义修复

能力失败[candidate04](capability-current-arm64-04.log)及[candidate05](capability-current-arm64-05.log)证明：undo后图层exactBounds为空，但projection仍等于painted，blank摘要不同；不是单纯QImage格式差异。最初将失败归因于对象比较不准确，后来用实际摘要/图层及projection验证纠正，失败和blank/undone PNG保留。

原backend没有把canonical history delta填入legacy memento。现在commitHistory共用原prepared/removal delta，在default prune前保留必要keys，commit接受后在原gate填入四个extent标量；原TransactionData undo/redo继续setDirty，测试不手动refresh。低层新增setExtent(QRect)一个consumer，上层API/state/队列/锁/TLS新增0；不向主干header引入PageStore类型。history终结增加原delta查询/扫描，Qt导出/收费及真实准备拒绝仍欠CP1，不能声称零分配或commit-only。

[生产diff](production-incremental.diff)2文件+25/-1净+24是保证增量；[测试diff](tests-incremental.diff)5文件+245/-0；[ownership](ownership-incremental.diff)+1/-0；[生成物](generated-incremental.diff)+1361/-1361。[逐文件成本](source-metrics.json)包括共享夹具191行、独立入口20行、CMake3行及DataManager31行。临时旧slot、图像输出、错误destroyed探针和候选friend删除；没有把这些候选计成额外生产净删收益。

## 成功结果及实际回退

[目标回归](targeted-01-results.json)双架构每架CPU1315、Reference762、Freehand普通/持久/失败/24MiB压力/取消11、相关DataManager17，共 **4210/0/0**、8进程退出0。新dirty extent用负坐标写入、最后页删除、undo/redo及empty history；相关原packed/iterator/history路径保留。四个[最终dyld能力进程](capability-05-results.json)各3/0/0，加载身份与像素一致。

[运行器](run_matched.py)在build/graph/正常回归停止后顺序运行每架12个独立进程配对，交替upstream/current，不并行计时，不剔除慢样本。[48进程](paired-01-results.json)均3/0/0且正常退出，共144 passed；所有blank/painted hash一致，segment callbacks8、update callbacks4、finish与strategy销毁一次、projection更新非零、一次undo/redo及image最后引用成立。能力和早期失败样本不混入配对。

| 指标均值，ms | arm64 current | arm64 upstream | x86_64 current | x86_64 upstream |
|---|---:|---:|---:|---:|
| stroke→projection-ready | 10.621 | 3.870 | 18.370 | 6.073 |
| pen-up→projection-ready | 10.542 | 3.793 | 18.190 | 5.913 |
| undo及drain | 0.803 | 0.087 | 1.337 | 0.143 |
| redo及drain | 1.832 | 0.171 | 2.871 | 0.324 |
| owner teardown | 0.832 | 0.277 | 1.813 | 0.667 |
| fixture total | 408.692 | 410.942 | 1033.256 | 1020.725 |

[描述性原数据](paired-01-descriptive.json)还提供median及paired-ratio mean。total被setup主导，不能用其接近来抵消stroke/undo/redo回退；普通current adapter有明确成本信号。12对不足以作2%非劣、P95/P99或正式M/K/E裁决，也未给persistent opt-in收益资格。完整required矩阵和正式样本仍按92/39保留。

## 未通过及未退出尝试

[完整arm64 DataManager日志](regression-manager-arm64.log) **353 passed/25 failed**：24个HistoryMutation行writablePinsAcquired为旧期望两倍；ChangedStorage首个大owner场景抛未处理bad_alloc，随后异常终止未完成。没有同父版本完整运行，不能将它们全部断定为旧失败。本批不改期望/额度或删除测试；后续从真实pin/preparation/metadata容量及原owner退出责任审查。目标组成功不等于完整DataManager或全仓库通过。

该进程PID70089处于UE，原runner因子进程退出无法完成而停止；[原成功组输出](regression-runner.log)只保留已返回的三组，不伪造full result。原upstream FreehandStrokeTest/testui启动PID59123没有到达stroke；[sample](upstream-startup-sample-01.txt)定位font thumbnail/textOutline，[attach](upstream-startup-debugger-01.log)未能暂停。[TERM/KILL后状态](broad-failure-processes.txt)两者仍UE，完整manager被原parent退出后PPID1。这些尝试不是正常drain，不授予全部参与者永久尾出口；新独立fixture的正常退出与它们分开记录。正式性能/resource资格仍受这些未退出尝试和完整required缺口约束。

前期编译错误、普通testui失败、destroyed探针误报、未匹配插件集合以及architecture旧source checkpoint失败均保留。最终[架构门](architecture-qualified.log)87 TUs、2019 indexed APIs、25183 edges、21 callbacks、21 manifest/25 ownership/16 census，原19-file ratchet与[起点](baseline-before.json)相同；未放宽ratchet。indexed API数不包括新增低层memento setter，实际API成本单列，见[责任及MI账本](../../br1_modification_guide/CODE_INDEX.md#cp0-matched-baseline-code-index)和[API处置](../../br1_modification_guide/API_CONVERGENCE_MAP.md#cp0-matched-baseline-api-delivery)。
