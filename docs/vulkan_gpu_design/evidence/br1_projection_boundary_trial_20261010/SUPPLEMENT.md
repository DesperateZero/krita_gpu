# 测试依赖纠正；旧失败保留

初版tests的control在testMerger内SIGSEGV；原库单次同样失败。LLDB定位到kis_async_merger_test.cpp:67：filterRegistry的blur为空；固定的freehand插件目录只有5个插件，没有测试所需blur。Release的Q_ASSERT未阻止随后解引用。两份失败、命令及LLDB均保留，未记为fusion独有回归或通过。

在任何探索过程之前冻结这次依赖纠正：tests-r1使用本次包内的测试插件目录，链接同_build-br0-cpu/bin现有krita*.so，各真实目标hash保存。它只用于原merger/projection两套测试，四配置顺序不变；不变更产品、测试源码、原型或matched性能夹具插件。实际加载libkritaimage须仍为同派生库。失败则停止。

run.py及旧tests结果不改；run-r1.py执行新tests-r1。只有全部通过，才能按原协议启动固定16过程explore，使用原freehand插件路径、原能力五过程和原prototype。此修订补运行依赖，不调整任何性能门、像素oracle、样本数量或失败选择规则。
