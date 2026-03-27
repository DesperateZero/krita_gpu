# Vulkan 纯异步 CPU 回传重构方案 (Async CPU Sync Refactor Plan)

## 1. 现状与痛点分析
当前在 feature/vulkan-phase7d-undo-save 分支中，笔画结束（Stroke End）时，Vulkan 引擎需要将 GPU 渲染的瓦片数据（Tiles）回传给 CPU 的 KisPaintDevice，以供 Krita 的撤销/重做（Undo/Redo）和保存系统使用。

虽然 Phase 7D 引入了 downloadTilesBatched 将 DMA 传输开销从 O(N) 降到了 O(1)，但其本质仍然是**同步阻塞**的：
在 UI 线程（主线程）中，KisVulkanPaintRouter::strokeEnd() 最终调用了 submitAndWait()，这会执行 vkWaitSemaphores 强制阻塞主线程，直到所有几十兆的像素通过 PCIe 总线传回主存，最后再同步执行 KisPaintDevice::writeBytes。

对于追求极致手感的绘图软件，这种设计在处理超大笔刷或长笔画时，会导致用户抬笔瞬间感受到明显的 UI 冻结（微卡顿）。

## 2. 目标与设计原则
*   **纯异步无阻塞**：UI 线程在鼠标抬起时，只负责提交 DMA 命令，绝不等待传输完成。
*   **最小入侵原则**：不修改 Krita 核心的 KisTransaction 和 KisPaintDevice 底层锁机制。
*   **安全与一致性**：完美融入 Krita 原有的 KisStrokeStrategy 调度器，利用现有的防并发和任务排队机制，避免撤销数据损坏或状态不一致。

## 3. 架构设计：基于 KisStrokeJob 的异步回传机制

Krita 拥有成熟的 KisStrokeStrategy 后台任务调度系统。我们将 Vulkan 的回传过程拆分为两个阶段：

*   **阶段一：主线程提交 (UI Thread)**
    鼠标抬起时，计算受影响的 Tile，向 Transfer Queue 提交 DMA 复制命令 (vkCmdCopyImageToBuffer)，拿到一个 Timeline Semaphore 值。**不等待**，直接返回。
*   **阶段二：后台线程等待与写入 (Worker Thread)**
    利用 KisStrokeStrategy 创建一个后台 Job。这个 Job 在 Krita 的线程池中执行：它先调用 vkWaitSemaphores 等待 DMA 完成，然后将 Staging Buffer 的数据写入 KisPaintDevice，最后执行 KisTransaction::commit。

### 时序图比对

**当前同步阻塞模式 (Phase 7D):**
```text
UI Thread:
User Pen Up -> strokeEnd() 
  -> m_renderThread->flushAndPause()
  -> scheduleImageToStaging(...)
  -> vkQueueSubmit()
  -> vkWaitSemaphores()    [!!! UI THREAD BLOCKED !!!]
  -> m_paintDevice->writeBytes()
  -> m_renderThread->resumeRendering()
  -> KisTransaction::commit()
```

**目标纯异步模式:**
```text
UI Thread:
User Pen Up -> strokeEnd()
  -> m_renderThread->flushAndPause()
  -> scheduleImageToStaging(...)
  -> timelineVal = vkQueueSubmit() [Returns immediately]
  -> m_renderThread->resumeRendering()
  -> image->startStroke(new KisVulkanSyncStrokeStrategy(timelineVal, ...))
  -> image->endStroke()

Worker Thread (KisImage Scheduler):
KisVulkanSyncStrokeStrategy::doStrokeCallback()
  -> vkWaitSemaphores(timelineVal) [Background thread blocks, UI is free]
  -> m_paintDevice->writeBytes()
KisVulkanSyncStrokeStrategy::finishStrokeCallback()
  -> KisTransaction::commit()
```

## 4. 详细实施步骤 (Implementation Steps)

### Step 1: 改造 KisVulkanTransferQueue 支持纯异步提交
当前 KisVulkanTileManager::downloadTilesBatched 直接调用了 submitAndWait()。我们需要拆分它。

*   修改 KisVulkanTileManager.h / .cpp：
    新增方法 `uint64_t downloadTilesBatchedAsync(const QVector<KisVulkanTileDataSP> &tiles)`
    该方法内部调用 m_transferQueue->submitAsync() 并返回生成的 timelineValue，但不执行 wait。

### Step 2: 实现 KisVulkanSyncStrokeStrategy
在 libs/image_vulkan 目录下新建 KisVulkanSyncStrokeStrategy，继承自 KisSimpleStrokeStrategy。

```cpp
class KisVulkanSyncStrokeStrategy : public KisSimpleStrokeStrategy {
public:
    KisVulkanSyncStrokeStrategy(
        KisVulkanTileManager *tileManager,
        KisPaintDeviceSP paintDevice,
        const QVector<KisVulkanTileDataSP> &tiles,
        uint64_t timelineValue,
        KisTransaction *transaction); // 接管 Transaction 的所有权

    void initStrokeCallback() override;
    void doStrokeCallback(KisStrokeJobData *data) override;
    void finishStrokeCallback() override;
    void cancelStrokeCallback() override;

private:
    KisVulkanTileManager *m_tileManager;
    KisPaintDeviceSP m_paintDevice;
    QVector<KisVulkanTileDataSP> m_tiles;
    uint64_t m_timelineValue;
    QScopedPointer<KisTransaction> m_transaction;
};
```

**关键逻辑**：
*   在 doStrokeCallback 中：调用 m_tileManager->transferQueue()->waitForValue(m_timelineValue)。等待完成后，遍历 m_tiles，执行 m_paintDevice->writeBytes()。
*   在 finishStrokeCallback 中：执行 m_transaction->commit(new KisPostExecutionUndoAdapter())。

### Step 3: 修改 KisVulkanPaintRouter 和 KisVulkanPaintOp
将 strokeEnd 的逻辑重定向到新的 Strategy。

*   **修改 KisVulkanPaintOp**：
    原本在 ~KisVulkanPaintOp 中直接 m_transaction->endAndTake() 并 commit。现在需要将 KisTransaction 的所有权传递给 KisVulkanPaintRouter 或直接封装进 KisVulkanSyncStrokeStrategy。
*   **修改 KisVulkanPaintRouter::syncToCPUAsync()**：
    ```cpp
    void KisVulkanPaintRouter::syncToCPUAsync(const QRect &dirtyRect, KisTransaction *transaction) {
        auto tiles = m_tileManager->tilesInRect(dirtyRect);
        uint64_t timelineVal = m_tileManager->downloadTilesBatchedAsync(tiles);
        
        KisImageSP image = m_paintDevice->image();
        KisStrokeId strokeId = image->startStroke(
            new KisVulkanSyncStrokeStrategy(m_tileManager, m_paintDevice, tiles, timelineVal, transaction)
        );
        image->endStroke(strokeId);
    }
    ```

### Step 4: 解决 Staging Buffer 竞态问题 (Critical)
**问题**：如果用户极快地画了两笔。笔画 1 正在后台等待 DMA，此时它的 Tile 处于 L1_Hot 状态且关联了 Staging Buffer A。笔画 2 开始画，如果它复用了同一个 Tile 的 Staging Buffer A，就会破坏笔画 1 尚未写回主存的数据。

**解决方案**：
*   在 KisVulkanTileData 中，不再维持单一的 stagingBuffer 指针。
*   在 downloadTilesBatchedAsync 发生时，将当前 Tile 的 Staging Buffer **剥离（Detach）** 并转移给 KisVulkanSyncStrokeStrategy 独占拥有。
*   KisVulkanTileData 的 staging 指针置空。如果下一笔立刻需要下载，缓存系统（KisVulkanTileCache）会为该 Tile 分配一个新的 Staging Buffer。
*   当后台线程的 KisVulkanSyncStrokeStrategy 完成 writeBytes 后，负责将剥离的 Staging Buffer 归还给 KisVulkanTileCache 的内存池。

## 5. 风险与回退预案
*   **风险**：Krita 的调度器可能会因为某些屏障任务（Barrier Jobs）推迟 KisVulkanSyncStrokeStrategy 的执行。如果延迟过长，用户可能会看到历史状态不一致。
*   **对策**：Krita 的 KisStrokeStrategy 天然支持 Exclusivity 设置。将此任务设置为适当的并发级别，由于它只是回读数据并不改变图层拓扑，可以安全地并发执行。
*   **回退预案**：通过 KisConfig 提供一个开关 useAsyncVulkanSync。如果遇到难以解决的撤销栈崩溃问题，可以一键退回到当前的同步 submitAndWait() 模式。

## 6. 结论
此方案完美契合了 Krita 的现有架构，利用了经过千锤百炼的 KisStrokeStrategy 机制来处理 Vulkan 的异步回读。它以**最小的系统入侵**，彻底解除了主线程的 PCIe 总线等待，将为 Krita 的 Vulkan 引擎带来真正“零延迟”的电竞级手感。
