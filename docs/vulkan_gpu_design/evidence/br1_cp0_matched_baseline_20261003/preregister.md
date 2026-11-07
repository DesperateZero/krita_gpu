# CP0 matched baseline：运行前冻结

运行库检查修订，仍早于定时配对：current完整build/bin会额外扫描mypaint等14个paintop插件，而upstream本次只构建default/LCMS/colorspaces/png五个插件。为同一preset提供同一可用插件集合，current采用五个原build插件的独立symlink测试目录；upstream仍用其独立build插件。最终四个dyld身份样本必须加载完全相同的common依赖路径/hash，并各自加载自己的image/ui/paintop/LCMS库；旧未匹配集合的capability-04保留，但不能作为配对准入。定时入口并非完整应用启动，不能给全插件cold setup或正式关闭状态成本资格。

能力检查修订，仍早于定时配对：KisImage析构在QObject::destroyed前disconnect，因此原destroyed信号探针会误报未释放。最终使用原KisImageWSP失效证明最后strong owner释放，不加入延时/事件轮询，也不改变projection/undo/drain终点。

能力运行修订，仍早于首个定时配对：原FreehandStrokeTest/testui启动在upstream字体thumbnail生成停滞，独立入口 `MatchedFreehandBaselineTest` 在双方都采用相同SIMPLE_TEST_MAIN及lazy原plugin registry；该auto brush无外部texture/brush/font依赖，不绕过brush/kernel/scheduler。旧slot与临时图像调试输出删除。当前侧能力样本证明undo像素为空而projection仍painted，实际缺失为backend未向原memento交接canonical delta extent；本轮修复该原owner事实，旧失败/图像保留。最终像素比较统一采用上述RGBA8888逐行hash，不增加容差或手动refresh；双方源码/夹具最终hash在运行器中冻结。生产修复单列成本，不算封装去重收益。

冻结于首个定时样本之前。固定产品父提交 `69a01e929abce246bfeed0603dbf0825088e28a1`，固定 upstream `9a24ae0d8c070884fb013594191002e1a1b39a19`。upstream 只增加与当前分支同字节的测试夹具和调用 slot，生产代码不修改。双方共用当前 `_install` 的依赖、RelWithDebInfo、universal x86_64/arm64、Qt6、FOUNDATION_BUILD 和原 lock-free hash 配置；实际 cache/运行库身份另核验。

本轮先验收同依赖对照和代表性普通 CPU 基线的可运行性，不给 opt-in persistent、正式 M/K/E、M6/M7/M8 或 BR1-PERF 资格。固定 workload `rgba8-buildup-over-512-8-lines-v1`：512×512、五个原 paint layer、RGB8/4 BPP、autobrush_300px.kpp 的圆形 auto brush，快照前显式 Buildup、OVER、48 px、4 workers；8 个左右交替的 384 px 线段，y=64+48*i，压力0.5→1.0，每两条提交一个正常 UpdateData。输入全部入队后 pen-up，不人为在中途 waitForDone；原 open stroke 的完整排空需要 endStroke。

验收实际8个segment callback、4个update callback、一次finish、strategy销毁、projection更新信号非零、projection等于paint layer、一次undo回到blank、redo回到painted、image释放。双方blank/painted的RGBA8888逐行SHA256必须完全相同。更新信号次数可能被合并，不要求相同。`KIS_BR1_SEED=12345`沿用测试环境，不能宣称它给原brush RNG设种子；本圆形preset未启用随机散布/纹理，实际重复与双方像素hash是确定性依据。

定时边界：fixture setup包含原image/resources/preset/blank转换；stroke包含startStroke、固定job入队、endStroke及waitForDone；pen-up包含endStroke及waitForDone；undo/redo各含原command操作及waitForDone；owner teardown包含原snapshot/preset/manager/node/image释放；total包含setup、stroke、像素转换/验证、undo/redo和teardown，不包含进程启动/全局资源注册与最后singleton退出。projection-ready不是canvas-visible。进程正常退出另记录，不把owner销毁等同全部全局缓存/预算归零。

运行顺序：先每架双方各一个能力样本；通过且两个build均静止后，每架12个独立进程配对，交替upstream→current/current→upstream，不并行运行被计时进程。保留全部日志、失败/超时和运行顺序。能力样本不混入定时配对。配对结果只作描述性分布/mean ratio和后续样本规模参考；12对不能支持2%非劣、P95/P99、first-dab/input-to-visible等正式声明，不进行显著性或阶段裁决。不要在看见时延后修改输入、容忍度或剔除慢样本。

CP0及CP10仍需按92 §3/§6/§14、39清点完整required：实际M/K/E分离、N/K/H/1–16 BPP、1/10/1000dab、opaque/alpha/texture/scatter/smudge/source、cold/warm/大brush/压力、正常canvas可见与慢projection、save/旧View、async/multipainter/mask/indirect/wrap/LoD、history/multidoc、SSD耗尽/不支持恢复源Fresh控制、真实allocator安装、永久拒绝/close/最后handle、峰值容量、足量独立配对95%CI及各门分别非劣。该清单不因pilot成功缩减；生产正例仍是resident CPU exact alternate，不自动增加BR2/BR3/GPU恢复源。
