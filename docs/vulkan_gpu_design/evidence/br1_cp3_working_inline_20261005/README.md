# CP3 工作存储中间候选（2026-10-05）

本目录保留产品父 `822456732bd02a13d128b855ed9856415544ec00` 上的工作值 inline 候选、真实失败及修复。完整目标仍为 M6–M8；此中间候选没有独立取得正式阶段或性能资格，随后并入[稀疏 epoch 批量构造包](../br1_cp3_epoch_batch_20261005/README.md)。

原版本/replica 数组采用常见二版本/一 replica 的 inline capacity；保护数组保持动态容量和原硬预算。堆上的 inline 字节属于原 enclosing paid allocation，spill 仍由原 allocator 收费。真实三版本 compaction 首轮崩溃（actual -11）；GuardMalloc/LLDB 与原工作数组 moves 定位了 moved-from allocator 丢失 accounting owner，临时普通分配随后按 retained allocator 释放而多减引用。原 allocator 的显式默认 copy 操作保留移动后源 allocator 的收费关联，覆盖 reuse、controller detach 和最终 free；没有新增 owner/字段/队列。布局及 source hash 见[working-layouts.json](working-layouts.json)，失败、定位及修复见[执行问题](execution-issues.json)。

修复后的实际两架矩阵与安装/allocator 检查成功。最初 read 误选 public tiles3 fixture，38 进程真实总数是 10788/0/0，先前口头 10810 属误报；此后补齐真正的 KisPageStoreReadBaselineTest（每架45）。[正确汇总](validation-corrected-summary.json)为38进程10810/0/0；额外 public fixture 的68项不重复计入。先运行的960个完整性能进程因 required read 前置晚补，保留为诊断，不授予最终资格。Fresh 四桶、H4 K16 及 handoff 20%/30%均未达门。

[父库/当前实际分配](working-allocation-summary.json)覆盖16进程128样本：两架 Fresh K1 88→74、K16 982→758，handoff K1 79→68、K16 798→622；这是请求次数/字节诊断，不是 used/reserved/slack 同义驻留或性能门。原 public Fresh N1024/K16 的真实 steady stack 指向 per-page insertPageRoot 重复复制共享前缀；[原结果恢复核对](public-fresh-profile/recovered-verification.json)保留错误 parser 的 result.json，只恢复 prefixed CPU_BASELINE 数据，并在批量源码改动前核对91个未变输入。

[pre-batch-production.patch](pre-batch-production.patch)冻结上述三个原生产文件，SHA256 `b5e45fa03be211995ce027dd6eaf43939b70ea23a3bd89d912a6a829d2930463`。后继包对组合后的最终源码重新构建、验证和运行完整协议；此处旧日志不累加为新源码资格。原始日志、失败与已找到的实际crash报告保留在[压缩附件](raw-logs.tar.gz)，逐member核对的[SHA清单](raw-log-manifest.json)绑定全部字节；构建二进制不入库。
