# 指令责任判别的原始证据

主报告：[INSTRUCTION_LEDGER](INSTRUCTION_LEDGER.md)。实施位置及五项设计门只在[原33行蓝图§19.11](../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#instruction-lifecycle-design)维护。产品HEAD/原库不变，没有生产补丁或产品测试新增。

- [instruction-raw.tar.xz](instruction-raw.tar.xz)：288个成员，完整源码派生diff、观察器、编译/链接命令、外部夹具、全部日志、逐过程JSON、加载库及对象身份。实际二进制/对象不打包，精确SHA保留；复建依赖冻结的本地构建与工具链。
- [成员清单](instruction-raw-manifest.json)逐文件SHA256；[独立复核](instruction-audit.json)记录10775项检查、58成功过程/464case、913身份文件、33行/6列、归档逐成员校验。
- [Tier 1机器账](instruction-summary.json)、[Tier 2机器账](instruction-detail-summary.json)、[源码符号/行/哈希](instruction-source-index.json)。源码索引中没有匹配的搜索词显式保留为空，不捏造行号。

归档SHA256：`73b05936131cb120aa9459ed3d60ace2755d9ea4a110afcc338c85d4093a0852`。

包内路径：

| 路径 | 内容 |
|---|---|
| `instruction-r0/capability.cpp/.log` | 线程计数接口能力；固定百万迭代约5M指令，10次空边界1508条；以`xcrun clang++ -O2 -arch arm64 -include unistd.h`编译 |
| `instruction-r0/*private.h`、`kern_resource.c`、`apple-source-provenance.json` | 官方Apple XNU来源、接口结构、下载内容哈希；仅诊断参考，不进入产品 |
| `instruction-r0/build-r1.log`、`build-r2.log` | 两层隔离派生构建结果 |
| `instruction-r1/runs`、`instruction-r0/run-r1.log` | 旧10000条嵌套端点门造成upstream capability拒绝；两个过程完整保留，无正式样本 |
| `instruction-r0/run-r2.log` | 修订协议后原冻结哈希拒绝启动，未启动基准；原身份快照保留 |
| `instruction-r1/runs-r2`、`instruction-r0/run-r3.log` | 修正端点门/明确协议身份后的54过程完整固定批次 |
| `instruction-r2/runs`、`instruction-r0/run-detail.log` | 4个Tier 2细分过程，未并入Tier 1估计 |

每过程含退出码、timeout/reap、完整dyld路径、实际库哈希、七phase端点、进程/前台/角色指令和原语义断言。缺失/失败未补数或删除；当前主CPU观察粗门失败保持。构建与基准串行，无另一基准/分析器竞争；Tier 1结束后才分析，再构建/执行Tier 2。

复算（在当前目录，或先将归档解至同一证据布局；不运行新基准）：

```sh
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_pipeline_refactor_20261010/analyze_instruction.py
.venv/bin/python docs/vulkan_gpu_design/evidence/br1_pipeline_refactor_20261010/finalize_instruction.py
```

第二条另检查冻结本地依赖哈希，重新核对Tier 2并生成源码索引/归档/审计；若本地产品、原构建对象或依赖后来变化，应保留身份拒绝，不能修改哈希迁就。四块指令差的bootstrap用完整`4^4=256`种重采样独立核对，与100000次随机bootstrap的区间一致。再建实验的脚本使用新的输出目录，不应覆盖或删除现有原始包。
