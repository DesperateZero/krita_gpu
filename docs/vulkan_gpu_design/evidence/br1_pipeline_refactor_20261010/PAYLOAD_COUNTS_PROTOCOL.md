# 页面对象周转与payload分配的分母核对

运行前冻结；只计数，永不作时间样本。产品11c689与upstream9a24，同前一net-r3的8case/四寿命。额外960次freeTileData已经证实，但allocateData先查原m_cache，4/8BPP还用Boost pool；不能把它写成960次系统malloc或额外payload复制。

在net-r3两侧派生库各替换TileData TU，仅记录allocateData中cache命中/未命中及freeData成功回cache/未回cache。保持原实际分支、异常政策和像素行为。cache miss只表示进入Boost/system后备，不自动等于系统分配。固定4过程current/upstream/upstream/current，mode3关闭scope时钟，case顺序按过程奇偶翻转；真实加载库、依赖、源哈希、全部像素/undo/redo、free数量和退出核验，120s timeout后kill/reap。先等净价批完成再构建与运行，无并行基准。

预期当前allocateData请求=rows+默认alloc，upstream请求=duplicate+默认alloc；这是待验假设，不能先替代真实计数。每case的cache hit/miss受原缓存跨case状态和释放调度影响，不要求重复完全相同；报告两个过程原始值与范围。全8case总allocate=hit+miss、freeData=cache return+fallback；按实际计数核对首尾，不用短窗口的请求/归还差直接宣称泄漏。

本批只决定后续是否应优先研究payload缓存还是围绕TileData/provider/binding/metadata的对象注册与解绑。即使几乎全命中cache，也仍有初始化字节和缓存同步成本；没有单位时间，不能宣布malloc成本为零或全部差额属于metadata。

r0构建在upstream freeData锚点处拒绝：upstream使用`if (!push) { free }`，current使用成功return并捕获可选cache准入bad_alloc，两侧形态不同。没有运行过程。r1分别在实际成功/后备分支计数，不改各侧原异常政策；r0已生成的current源、diff、库和失败日志保留。
