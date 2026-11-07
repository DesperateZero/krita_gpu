# BR1 BC9 / OP9 operation backing 原子准备边界，2026-09-29

本批把 §16.18 的压力反例收敛成一个可供后续 continuation 使用的底层事实：普通 direct `writeOperation` 在 callback 进入前准备全部声明目标的 mutable backing。准备失败时 callback 不执行，只回滚本 execution 新准备的页；同一 history owner、既有 pending 和原 claim 仍可在压力解除后重试。

## 实现范围

生产修改只位于 PageStore、write coordinator 和 `KisTiledDataManagerPageStoreBackend`：

- `KisPageMutationExecution::prepareWrites` 复用原 `beginWriteImpl`、provider、budget、claim 和 descriptor 链，逐页取得再释放 preserve-content guard；
- execution 按原排序 `BoundEntry` 位置保存 touched 与 preflight-owned 两组 bits。≤64 页各一个 inline word；更多页由原 `KisMutationStorageAllocator` 一次收费 `2 * ceil(K/64)` 个 word；
- `finishPreparedWrites` 先取消仍为 preflight-owned 的页，再导出 touched keys。准备成功但 callback 未触碰的页不 seal generation；
- `recordCancelled` 在 metadata cancel 成功后清空 transition 身份并把 entry 恢复为 `IntentOnly`，保证持久 scope 可重试；
- backend 的私有模板只为现有两个 ABI 选择政策：`writeOperation=true`，packed full-payload `writeBytes=false`。

semantic removal 和 staged alias initialization 返回内部 `Unsupported` 并保持原路径；clear/copy/planar/restore 不在本批范围。结果仍是既有 `Failed`，没有加入 `RetryablePressure`、waiter 或 scheduler continuation。

## 主干侵入账本

生产文件为六个内部文件：`KisPageStore.h/.cpp`、`KisPageWriteCoordinator_p.h/.cpp`、`KisTiledDataManagerPageStoreBackend.h/.cpp`。测试修改为 `kis_tiled_data_manager_test.h/.cpp`。

新增 public/protected 产品 API、manager/Tile/UI 字段、include、friend、锁和 TLS 为零。`tool/strokes`、paintop、painter、PaintDevice、DataManager 公开接口与 scheduler 均未修改。PageStore 负责物理准备及回滚，backend 只选择内部政策；page、budget、reservation 和 waiter 身份没有越过适配层。

## 目标验证

`testPageStorePixelOperationPreflightBudgetPressure` 在同一 history mutation 中保留已有 pending 页，再用 8.5 MiB 产品预算制造两页 operation 的 backing 拒绝。第一次调用必须失败且 callback 次数为零；解除压力后用同一 history owner 重试并提交，验证两页字节与 active write pages 归零。

完整参数化 `testPageStoreChangedStorage` 覆盖 BPP 1/4/8/16、K 1/9/65/257、standalone/history 和四种 outcome，共 128 个数据行；新增 `pagesSealed` 增量必须等于实际 changed 页数的断言，证明 preflight-only 页不会成为新版本。

| 命令范围 | 结果 |
|---|---:|
| arm64：压力用例 + 完整 changed-storage 参数组 | 131 passed / 0 failed / 0 skipped |
| x86_64：压力用例 | 3 passed / 0 failed / 0 skipped |
| PageStore 架构门 | 21 manifest / 25 ownership / 16 census / 1,824 APIs / 19,890 edges / 17 callbacks / 19 intrusion files |

输出见 [arm64 日志](tiled-arm64.log)、[x86_64 日志](tiled-x86_64.log)和[架构日志](architecture.log)。只运行能够证伪本批结果的测试，没有重跑历史全矩阵。

## 裁决与下一步

本批只证明普通 direct cursor 的 backing 容量失败可以在 callback 前原子拒绝，并可由同一 history owner 重试。它没有证明所有资源都已收费，也没有完成 permanent/waitable/cancel 分类、自动恢复或多文档公平。

下一改动只在 PageStore/DataManager operation 结果边界增加可靠分类，并与原 scheduler 的实际 continuation consumer 同批交付；同时合并被替代的模糊失败分支。只有 callback 未进入的原 job 输入可接续，已经进入 callback 的 operation 不重放。`tool/strokes` 保持零扩张，正式工具默认仍关闭。

