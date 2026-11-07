# 唯一有界追加：主线程与任务外线程CPU

首批72过程完成且全部通过。jobs/detail同批分别留下1.377/1.299ms额外非job CPU；四个detail块残差1.249–1.330ms，足以与seal/canonical或read余项比较，满足原协议的一次判别追加条件。原样本/协议/分析不改。

只追加线程边界归属，不加细粒度页时钟。新fixture在原Stroke边界前后各取一次Mach task_threads/THREAD_BASIC_INFO CPU累计值、THREAD_IDENTIFIER_INFO ID及线程名；保留begin/end快照的时间窗口、出生/消失线程与求和残差，不将活线程快照冒充已退出线程CPU。current派生ReclamationExecutor仅在原worker/monitor启动时命名BR1-reclaim/BR1-delay，用于身份匹配；不改循环或工作量。两侧fixture另以原observer包围主线程start+strategy、输入提交、endStroke、waitForDone，全部结果在计时外输出。计时标记本身属于观察，不按名称将waitForDone CPU解释为等待时长。

两配置共用同一侧诊断运行库、mode2：control用原fixture，census用新增主线程/线程快照fixture。4能力过程后固定4平衡块；每块两配置各current/upstream/upstream/current，配置交替先后，共32主过程；追加总36，整包总108真实fixture过程。描述性同批差额、逐块范围，无新CI或门资格。像素/回调/销毁、19 update实际数量、退出/加载/父子账及原失败规则保持，慢值不删，不继续扩样。

线程快照不能与严格Stroke端点完全同时：保存快照前后process CPU/wall，量化窗口扩张。若出现消失线程、计量不闭合或名未知，明确保留，禁止填成零或任意分摊。优先检验1.3ms是否位于主线程提交/队列处理、原reclamation worker/monitor或其它线程；不再开启第三轮探针。若主责任及该剩余量已定界，停止采样并交付实际可解释份额和实现审查顺序。
