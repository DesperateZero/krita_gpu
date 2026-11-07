# QtCore 修复构建的可复现输入

这是本地依赖修复，不是产品源码修改。旧安装库的完整构建来源没有恢复；本次明确使用下列固定源码重建候选，并验证现有消费者兼容性，不能把它称为与旧库相同的构建。旧库使用 Apple LLVM 21，新库使用本机 Apple LLVM 17；今后的性能比较必须使控制组和改动组使用同一 Qt 运行库，不能直接沿用旧库的性能比值。

## 固定源码

- Qt 原版 `v6.8.0`：[下载身份](qt-source-download.json)。纯 Qt 对照的两个版本只差 [acquire 回植](qt-6.8-qreadwritelock-acquire.patch)。[配置](baseline-CMakeCache.txt)、[源码/库身份](qt-comparison-source.json)保留对照边界。
- Krita fork：`dimula73/qtbase`，commit `c3ccedb3057b5eda84653887954572f016f1157a`。[源码 tar 身份](krita-qt-source-download.json)固定 SHA-256 为 `9e578e2d68a571a06c731bbfcbf95279576f8b71c8b663ab7507531bcba23dc2`。
- 在该 tar 根目录用 `patch -p1` 应用 [候选源码补丁](krita-qtbase-candidate.patch)。它将 Core 的旧 signal compressor 更新为与现有安装头文件一致的 frame-rate compressor（对应 `d706364`、`cb01d4e`），保留现有安装的 `qyieldcpu.h` 编译器分支顺序，再回植两项 Qt 锁修复。完整候选文件散列见 [source manifest](krita-qtbase-candidate-source.json)。
- Core 源文件头部的许可保留；fork 中 QFile 同步落盘、ICU 兼容及 Windows assert 行为等原有 Core 修改继续保留。没有把整套 Qt 升级到其他版本。

## 配置与构建

使用项目 `.venv/bin/cmake`、`.venv/bin/ninja`，在独立目录配置 Qt fork，只构建 `Core` target。最终完整 cache 是 [final-04-CMakeCache.txt](final-04-CMakeCache.txt)，配置摘要是 [final-04-config.summary](final-04-config.summary)。关键参数如下（路径均以本 workspace 为准）：

```sh
/Users/apple/krita_gpu/.venv/bin/cmake -S <已应用补丁的源码目录> -B <独立构建目录> -G Ninja \
  -DCMAKE_MAKE_PROGRAM=/Users/apple/krita_gpu/.venv/bin/ninja \
  -DCMAKE_BUILD_TYPE=Release '-DCMAKE_OSX_ARCHITECTURES=x86_64;arm64' \
  -DCMAKE_PREFIX_PATH=/Users/apple/krita_gpu/krita/_install \
  -DCMAKE_INSTALL_PREFIX=/Users/apple/krita_gpu/krita/_install \
  -DQT_BUILD_TESTS=OFF -DQT_BUILD_EXAMPLES=OFF -DQT_BUILD_TOOLS_BY_DEFAULT=OFF \
  -DQT_FEATURE_gui=ON -DQT_FEATURE_widgets=ON -DQT_FEATURE_network=OFF \
  -DQT_FEATURE_sql=OFF -DQT_FEATURE_dbus=OFF -DQT_FEATURE_testlib=OFF \
  -DQT_FEATURE_icu=ON -DQT_FEATURE_system_zlib=ON -DQT_FEATURE_zstd=OFF \
  -DQT_FEATURE_glib=OFF -DQT_FEATURE_openssl_linked=ON \
  -DQT_FEATURE_mimetype_database=OFF -DBUILD_WITH_PCH=OFF \
  -DZLIB_INCLUDE_DIR=/Users/apple/krita_gpu/krita/_install/include \
  -DZLIB_LIBRARY_RELEASE=/Users/apple/krita_gpu/krita/_install/lib/libz.dylib \
  -DCMAKE_SHARED_LINKER_FLAGS=-L/Users/apple/krita_gpu/krita/_install/lib
/Users/apple/krita_gpu/.venv/bin/ninja -C <独立构建目录> -j6 Core
```

Qt 的 Darwin zlib wrapper 实际传 `-lz`，只设置 `ZLIB_LIBRARY_RELEASE` 不能确保使用安装前缀的 zlib；最终链接搜索路径也必须明确。最终 dylib 确认链接原 `libz.1.3.1` 与 ICU 72。GUI/widgets 开关用于保持 Core 编译配置一致，不要求重建或替换其他 Qt 模块。

最终候选的 `qconfig.h`、`qtcore-config.h`、`qtcore-config_p.h` 与旧安装逐字相同；421 个源头文件也逐字一致。两架构原有导出集合全部保持，arm64 为 7,132，x86_64 为 7,161。完整结果见 [最终运行库身份](qt-final-runtime-identity.json)。这些静态检查与运行回归共同使用，单独不授予所有 ABI/行为兼容保证。

## 运行和安装

[最终 Qt 自身测试](qt-upstream-test-manifest.json)与两架构各 1,000 次真实 extent 重复测试先在 `final-runtime/lib` 运行。测试都检查实际加载库路径；x86_64 启动时在 `arch` 后通过 `/usr/bin/env` 赋予 DYLD override，避免变量被启动器丢弃。构建树运行还要指定原 Qt plugin 目录。

[install_qtcore.py](install_qtcore.py)校验原库和候选 SHA，要求上述测试已通过，备份完整原 framework 后仅原子替换 `Versions/A/QtCore`。它没有执行整个 Qt 的 `install` target，不修改原头文件和其他 Qt 模块。备份与实际替换记录见 [qt-installation.json](qt-installation.json)。再次执行时，原库 SHA 条件会阻止无意的重复安装。

恢复原库时，应先校验 [备份目录](/Users/apple/krita_gpu/build/br1-qt-core-20260928/original-runtime/lib/QtCore.framework/Versions/A/QtCore)仍为 `bb833c978a108733cca3375aa14a5b618be62dd195bcbf95e60b3f75ca38aee6`，通过临时文件加原子替换恢复；恢复后，修复库下的当前回归资格随之失效，不能继续沿用。
