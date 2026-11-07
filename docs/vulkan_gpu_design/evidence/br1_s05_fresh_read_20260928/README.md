# JP5：fresh manager 读取与旧 reader 隔离

本批关闭 JP4 源码上已复现的 fresh raw 陈旧读取：两个 manager getter 在 seal/operation 窗口以及 writer 返回后，均可取得已发布值；旧 raw/captured 读稳定。**manager extent 仍有窗口，JP5/JP6 联合出口和 M8 未完成。** 当前裁决见 [92 §16.8](../../92_br1_m6_m8_execution_baseline.md#fresh-read-implementation)，实际处置见 [清点 §11](../../br1_modification_guide/CONVERGENCE_CHECKLIST.md#fresh-read-delivery)，代码责任见 [02a §11](../../br1_modification_guide/02a_joint_publication_boundaries.md#fresh-read-implementation)。

## 身份与增量

| 项目 | 最终事实 |
|---|---|
| 产品 HEAD | `5173c807c87bb1619325249a07a8b4f4f8f09f09` |
| 包含 6 个未跟踪源码的 diff SHA-256 | `73c04adf447603eaad0cfd272f0d055136a6c8c833cd8f73bc00ee9b3a0f84a3` |
| 改动前身份 | JP4 的 `66e7ff89c8a9208ef3253e2d8e0c0b4fc6d2f92e07f664caae4e05138dd1f54d`，见 [before.json](before.json)；反例来源见 [前次审查](../br1_current_read_convergence_20260928/README.md) |
| 相对 JP4 的实际产品改动 | 13 个生产文件 +184/−11，净 +173 行；2 个测试文件 +205 行；无新增生产文件 |
| 全工作树范围 | 124 文件；生产净增 8,102，测试净增 11,503；这是相对 HEAD 的未提交增量，不是整个 BR1 相对 upstream 的规模 |
| 冻结内容 | [实际增量](final-increment.patch)、[增量 JSON](final-increment.json)、[完整清点](inventory-final.md)、[运行身份](checks-01/identity.json) |

## 实际实现与责任

两个 fresh getter 共用 backend private `selectCurrentReadTile`。Store 在原 owner 锁下解析逻辑版本与必要 default surface；暖 cache 通过原 binding 比较 version + allocation identity，之后实际 lock 仍 pin backing。失配才 capture 精确 view。旧 wrapper 有 active reader 时不重绑它，新 wrapper 在精确 pin 有效时取得原 TileData COW 引用，再按原 detached Tile 寿命读写，不持 manager/bridge 裸指针。

default 选择从原 hash 取稳定引用，pin 后验证选定 default 字节；真正 sparse default 不注册 canonical 页、不增加 default materialization。metadata 与兼容 default 不同的冷路径可向原 allocator 请求 uniform TileData，预算不足明确失败。wrapper/base iterator/精确与 rough copy 的 nullable caller 已处理；原 job failure context 保留失败，旧像素不被当成新读成功。

没有修改 `KisTile::lockForRead` 的原嵌套语义，没有第二份 current/default 表、write set 或 TLS。现有 live legacy iterator/write intent 仍按原能力消费 pending；外部普通读仍在最后 checkpoint。`existingTile` 对新 canonical 选择反映页是否分配，避免 copy 的 sparse/no-op 分支误判。

## 同源验证

[run_checks.py](run_checks.py)在最终源码上构建原 20 目标及 brush 插件，运行 arm64/x86_64，完成架构检查、6 项 reachability 工具自测与实际 final Ninja no-op。记录见 [manifest](checks-01/manifest.json)、[驱动日志](checks-driver-01.log)和 [源码 patch](checks-01/source.patch)：**9,332 passed / 0 failed / 0 skipped**。其中新增 47 个 case/架构覆盖 publication 冷/暖、packed/cursor、active reader、BPP、两个 getter、writer 返回后新线程、warm 重复 getter、manager 析构后的独立 wrapper、default revision 往返、Store 关闭和实际 default 预算拒绝。

原矩阵同时保留 history/pending、嵌套 legacy 读写、default 生命周期、copy fallback、claim、并发提交进度、scheduler/painter 和 completion 回归。这是 CPU ON 开发配置，不能替代 OFF 完整产品、TSAN、Vulkan、正式性能或真实 persistent brush 整链。各次 selected/pressure 运行是开发定位，不与全矩阵累加。

### 原窗口 probe 保留整体失败

最终 [probe](current-read-probe.cpp)沿用前次 44 场景/架构、172 个观察点。新增 `raw_violations` 单列两个 getter 的像素结果，脚本要求为 0；旧指针、captured view、pending/intent/abort 控制仍要求通过。

| 项目 | 改动前 / 架构 | 最终 / 架构 |
|---|---:|---:|
| publication 不一致观察点 | 80 | 32 |
| raw getter 与同点 canonical 像素不一致 | 原日志中存在 | **0** |
| 控制错误 | 0 | 0 |
| `--require-converged` | 返回 3 | **仍返回 3** |

剩余 32 个观察点均是冷页 seal/operation cleanup 时 manager extent 为空，而 canonical 页/extent 已发布；不包含 warm active-old raw 陈旧读取。没有把整体 probe 改成只看容易通过的 raw 条件。两架构原始结果、命令和 hashes 见 [arm64](arm64-final-01-identity.json)、[x86_64](x86_64-final-01-identity.json)；记录/整体验收失败分别保留在对应日志。`after-01` 属于开发过程，最终身份以 `final-01` 为准。

### 暖读取成本

[真实 allocator interposer](allocation-interposer.cpp)在每架构 BPP=1/4/8/16 × 有/无同版本 active reader 的 8 组中，测量 **16,384 次 fresh getter**：allocations=0、bytes=0、frees=0、额外 capture=0、generic request=0，返回 wrapper/像素一致。每次先以 8,210 B 分配验证探针能记录真实 malloc。

源码为 [warm-read-probe.cpp](warm-read-probe.cpp)，最终日志与编译/库/探针身份：[arm64 日志](install-arm64-warm-final-01.log)、[身份](install-arm64-warm-final-01-identity.json)，[x86_64 日志](install-x86_64-warm-final-01.log)、[身份](install-x86_64-warm-final-01-identity.json)。统计不覆盖 cold mismatch、sparse wrapper 的既有分配、锁等待或整笔耗时；新增 metadata/binding 检查的整体成本仍须正式对照，不能由零分配推出 Fresh 2% 或“更快”。

## 架构与失败记录

- [architecture-01](architecture-01.log)真实拒绝了两处新增 friend：Tile header 6→7、manager header 10→11。按 audit README 要求，先在 92 §16.8 记录所有权、内存、锁序和移除后果，再显式更新 reviewed ceiling；没有仅刷新 hash 绕过。直接 include 仍各 1，manager `.cc` 25 标识/3 include 与全部布局门不变，无新常驻字段。两个 friend 随 raw-read adapter 迁移删除。
- [graph-02](graph-02.log)从实际 compile database 生成 87 TUs / 1,809 APIs / 19,614 edges / 17 callbacks；[architecture-02](architecture-02.log)及最终矩阵架构检查为 21 manifest / 25 ownership / 16 census / 19 intrusion。源级 [raw caller 搜索](raw-callers.txt)辅助人工检查，不能替代生成图和 runtime coverage。
- `build-01` 记录 private helper 声明缺少 `KisTileSP` 可见性的编译失败；改为已有 shared pointer 的前置声明后构建通过。中间默认存储的异常清理在编译测试前改为先清空再释放引用，避免构造失败时二次 deref。曾评估为 transient wrapper 保留 provider cache，最终沿原 detached COW 存储消除了 manager 裸指针和额外读写寿命分支；未将中间候选计入最终验证。
- 一个生成文件全量文本比较的辅助脚本运行过慢后被终止，未改产品或证据；最终清点只对实际生产/测试增量做文本 diff，生成审计按原分类单列。无产品测试或最终 probe 超时/中断。

## 停止条件与剩余工作

本批冻结为 **JP5 fresh raw 子范围通过**。下一批必须继续 JP6 的 manager extent / PaintDevice bounds / adapter 和固定 read selection 联合边界，保留 pending/intent 工作范围；不能把所有 `extent()` 一律改为 canonical，也不能把已复现窗口重新命名成兼容行为。原 JP3/JP4 行为保留，BC10 真业务 harness 可继续准备；联合出口后进入 direct stroke 的 owner/display/finish/cancel/drain。

完整短 gate、全部必要资源/压力、其他 restore/default/异步模式组合、OFF、同依赖 upstream、Fresh 2%、M6/M7/M8 与 BR1-PERF 仍开放。最终 [validation.json](validation.json)核对源码、124 文件清点、28 个构建/运行文件、probe 身份、文档链接与增量；验证范围不越过这些证据。
