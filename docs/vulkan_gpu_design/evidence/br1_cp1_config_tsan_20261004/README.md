# CP1 完整manager配置依赖TSAN排查

产品`2e471d5efb`，父`3c22a0226a858ef16d150b2dfe5523d9bfbc684e`，文档父`d0819a2a26361c0dece775497e3655fa4cf3b74b`。上批冻结包保留运行中的checkpoint；其后的原`manager-reset-full-01`已取得actual66/reaped、345.72s、无Totals，不能继续标为Pending。[实际结果](manager-failure-results.json)及原日志、最终identity在本包保留。最终1,979源码输入及107运行输入核对未变；原48tasks/16threads/100000cycles/seed12345、匹配插桩QtCore、无suppression/guard/interposer保持。

TSAN报告读取来自`QtPrivate::compareStrings → KConfigPrivate::changeFileName`，相同heap块的前写入来自`QAbstractConcatenable::appendLatin1To → KConfigPrivate::KConfigPrivate`；两端均为原stressTest并发构造DataManager、KisImageConfig、prepareStore调用。现有KF6ConfigCore 6.7.0未插桩，必须先核验依赖内全局静态初始化与同步，不能从未插桩边界直接推定生产锁缺失或用suppression将警告改成通过。

对照源码来自[KDE官方v6.7.0](https://github.com/KDE/kconfig/tree/v6.7.0)，[KConfig源码](https://raw.githubusercontent.com/KDE/kconfig/v6.7.0/src/core/kconfig.cpp)及[KSharedConfig源码](https://raw.githubusercontent.com/KDE/kconfig/v6.7.0/src/core/ksharedconfig.cpp)。下载tar SHA256 `29303e8ba9711991b118e197def2a2e8184d098c75a2f187362ba8f0f5543a42`。隔离构建路径`build/br1-cp1-config-tsan-20261004`，只构建同版本Core并保留compile commands/flags；不覆盖主安装或仍运行8f manager的任何输入。首次cmake命令不在PATH、exit127，日志保留，随后使用仓库`.venv/bin/cmake`。

## 根因与修复

同版本KConfigCore完整TSAN构建的16线程cold探针实际66/reaped，直接定位`kconfig.cpp:81–83`的`s_wasTestModeEnabled`读写竞争。第一配置构造建立全局文件名但未记录当前test-mode；线程首次配置构造时，多个worker竞争执行全局文件名转换。主线程先完成第二个配置对象的控制组actual0/reaped，无TSAN警告。原未插桩依赖的cold/warm两个控制都actual0，仅为该次未触发，不据此撤销完整manager原失败。[四轮矩阵](probe-matrix-01.json)保留源/库/Qt身份和实际退出。

原manager fixture新增`initTestCase`，在主线程构造两个配置对象完成上述惰性初始化后再执行原测试。生产源码+0/−0，测试两文件+11/−0，派生两JSON+1068/−1067；压力body、任务数、线程数、循环数、seed及预算不改，不加生产锁或suppression。该修复约束测试模式初始化，不声称修复KConfig全应用任意线程切换测试模式的行为。

最终127源/头匹配[产品blob](product-source-freeze-final.json)，Clang图仍87TUs/2172APIs/27412edges/27callbacks，原21manifest/25ownership/16census/19-file ratchet通过。MOC在隔离目录重生，原8个manager/支持TU完整重编及链接actual0；主安装及旧8f在途manager输入未改变。初次manager构建的freeze比较误把预期两测试文件变化视为失败、首次graph命令PATH错误均保留，均未启动测试，不覆盖失败记录。

新完整manager同时加载插桩QtCore和KConfigCore，已经通过fixture初始化并继续原完整body；实际终点前保持Pending。[冻结检查点](manager-checkpoint.json)只报告当前输入核对、PASS前缀及进程状态，不能当Totals或阶段通过。KConfig的TSAN隔离构建使用记录的RelWithDebInfo/arm64选项和本机SDK，不作性能对照或未改配置的二进制等价声明。完整CP1四组差集仍按[92 §16.89](../../92_br1_m6_m8_execution_baseline.md#cp1-config-initialization-delivery)执行。
