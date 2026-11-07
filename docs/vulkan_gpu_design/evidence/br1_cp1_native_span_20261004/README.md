# CP1 原worker/monitor合并区域归费

产品 `46eab867ed37da42921c5618cc349171454fe5c7`，产品父 `d7e91efc39d965be49c748859fd384f91cda2c64`，文档父 `d1fd1095fd0902a8a2e7abfc1ccf7301aa26f09d`。本包关闭§16.81已经独立复现的原两线程重收费，完整CP1仍开放。[最终身份](final-freeze.json)核对123源输入、161运行物/配置及审计输入；121编译输入匹配测试和产品blob，两派生JSON在测试后刷新，旧hash单列。

原ReclamationThread记录查询区域的base/bytes；monitor仍在原初始化gate内创建，扣除与原worker已付费区域的交集，再按唯一未付容量复验64KiB上限并释放未用准备费。原worker从executor构造时即已接受且ready，monitor join始终先于worker join，借用的重叠容量在整个monitor寿命中持续收费。失败仍不接受回调，沿原catch/join归还本次费用；正常join只释放各自原收费。没有新owner/队列/锁/公共PageStore API或调试hook依赖。

两区域字段每个线程16B，两实例使原executor实际malloc请求增加32B，由原ProcessStorageObject allocator自动计入；生产一CPP +26/-5净+21，测试修改0。它是实际计费保证成本，不记纯去重或性能收益。生成两JSON +131/-129单列，图87TUs/2164APIs/27464edges/27callbacks，原21manifest/25ownership/16census/19外部文件ratchet保持。

复用§16.81同一ledger/native fault body和最后审计器，cpp输入快照保存于每个probe目录。两架各34静止端点均 `charged == actual_request`、native excess0；arm64 worker/monitor合计32KiB，原48KiB重收费消失，x86_64仍16KiB。两次原join后原native地址均unmapped，runtime-stopped费用/真实请求同为0；固定executor等原存储仍收费至其实际析构，不写零尾容量。

worker/monitor各连续三次pthread_create EAGAIN，两架共12次拒绝及4正常控制actual0；所有拒绝回到原准备前账本，拒绝的回调不执行。这里注入的是明确的原API返回值，不是OS真实线程耗尽，也不资格化默认abort退出。双架CPU/Reference原完整body共4进程 **4288/0/0**，插桩QtCore下原wake/capacity/deadline/process/stop及reclamation目标共2进程 **12/0/0**，全部实际exit0；没有重跑或借用旧完整22进程矩阵来授予本源码全矩阵资格。

本包只证明原活着的worker区域与monitor区域之间的已付容量不重复计算。第一次查询若合并外部线程、其他OS/runtime容量、外部TLS/usable/固定static并存peak及全owned硬界仍待资格化；不将opaque sizeof或本机16/8KiB当跨平台保证。read/capture/history/publication/retirement/close联合永久拒绝、晚fence、caller transaction/最后facade与handle退出仍欠；完整manager TSAN及十二UE默认失败/宿主退出沿§16.81保留。本包无新增UE，M6/M7/M8正式0/3，persistent默认关闭。
