# Krita 像素笔刷引擎索引

## 概览

- Krita 里的“像素笔刷引擎”在代码里对应的 paintop id 是 `paintbrush`，不是单独叫 `pixelbrush`。它的注册入口在 `defaultpaintops_plugin.cc:L31-L36`。
- 真正的 CPU 主实现集中在 `kis_brushop.h:L33-L90`、`kis_brushop.cpp:L103-L149` 和 `kis_brushop.cpp:L207-L369`。
-  `kis_abr_brush.h` 不是“像素笔刷引擎本体”，它是“预定义笔尖资源”的一种实现，属于引擎会调用的笔尖类型之一。

## 核心代码

- **注册与实例化**：`paintbrush` 这个引擎由 `defaultpaintops_plugin.cc:L31-L36` 注册到全局画笔引擎注册表；真正创建 paintop 的流程在 `kis_paintop_registry.cc:L43-L55` 和 `kis_paintop_registry.cc:L67-L85`。
- **引擎主体**：`KisBrushOp` 就是像素笔刷引擎本体，成员里直接挂了大小、比例、速率、柔和度、间距、散布、锐利度、旋转、不透明度/流量等选项，见 `kis_brushop.h:L33-L90`。
- **单个 dab 的绘制逻辑**：`paintAt()` 里会按传感器求出 `size / ratio / rotation / scatter / opacity / flow`，再构造 `KisDabShape`，最后丢给 dab 渲染执行器，见 `kis_brushop.cpp:L103-L149`。
- **多线程/异步 dab 合成**：`doAsynchronousUpdate()` 会从 dab 队列里取出已准备好的笔尖，分块、镜像、wrap-around、并发 blit，这部分就是像素笔刷“多线程笔尖”实现的核心之一，见 `kis_brushop.cpp:L207-L369`；配套类在 `KisDabRenderingExecutor.h` 和 `KisDabRenderingQueue.h`。
- **1px 特殊优化**：1 像素、开启 `sharpness` 时会走专门的直线缓存路径，不走普通 dab 流程，见 `kis_brushop.cpp:L384-L406`。
- **模块文件列表**：默认像素笔刷模块的构成在 `CMakeLists.txt:L7-L15` 一眼能看全。

## 共享基类

- **笔刷型 paintop 公共层**：`KisBrushBasedPaintOp` 负责加载当前笔尖、建立 dab cache、挂接 `texture / mirror / precision` 等后处理，这一层是像素笔刷和其他“基于笔尖”的引擎共享的基础，见 `kis_brush_based_paintop.cpp:L68-L115`。
- **间距计算**：真正把 brush 自身 `spacing`、`auto spacing`、LOD、镜像翻转、airbrush 计时等折到一起的是 `kis_brush_based_paintop.cpp:L166-L187`。
- **堆积 / 渲染模式**：文档里的 `buildup / wash` 对应到设置层 `paintIncremental()`，像素笔刷走的是 `kis_brush_based_paintop_settings.cpp:L68-L73`。
- **笔刷轮廓、auto spacing、size/angle**：这些统一放在 `kis_brush_based_paintop_settings.cpp` 和 `kis_brush_based_paintop_settings.h`。

## 笔尖系统

- **总入口**：所有“笔尖类型”最终都落在 `KisBrush` 抽象层，XML 反序列化与笔尖实例化在 `kis_brush.cpp:L453-L475` 和 `kis_brush.h:L172-L188`。
- **笔尖工厂注册**：自动笔尖、预定义位图笔尖、ABR、PNG、SVG、文本笔尖都由 `kis_brush_registry.cpp:L37-L46` 注册。
- **自动笔尖**：文档里的“自动笔尖”核心实现是 `kis_auto_brush.cpp` 和 `kis_auto_brush_factory.cpp`，其中 mask 生成与尺寸逻辑见 `kis_auto_brush.cpp:L66-L101` 和 `kis_auto_brush.cpp:L176-L197`。
- **图像/预定义笔尖**：`GBR / ABR / PNG / SVG` 通过 `kis_predefined_brush_factory.cpp:L20-L58` 加载，通过 `kis_predefined_brush_factory.cpp:L197-L216` 区分子类型；具体类就是 `kis_gbr_brush.h`、`kis_abr_brush.h`、`kis_png_brush.h`、`kis_svg_brush.h`。
- **文本笔尖**：对应 `kis_text_brush.cpp` 和 `kis_text_brush_factory.cpp`。
- **UI 侧的三种笔尖模式**：笔刷面板里 `Auto / Predefined / Text` 三种模型集中在 `kis_brush_option_widget.cpp:L20-L36` 和 `kis_brush_option_widget.cpp:L51-L75`。

## 文档选项对应

- **Brush Tip / Size / Ratio / Spacing / Mirror / Softness / Rotation / Sharpness / Scatter / Opacity / Flow**：这些选项在像素笔刷设置界面里是一起装配的，见 `kis_brushop_settings_widget.cpp:L46-L89`。
- **Color Source / Mix / Darken / Hue / Saturation / Value / Texture**：这几项不是在 `kis_brushop.cpp` 里直接做，而是在每个 dab 的“资源同步”阶段处理，核心在 `KisBrushOpResources.cpp:L39-L85`。
- **传感器映射**：所有“压力/速度/随机度/时间/距离/绘制角度”等曲线映射的公共框架在 `KisCurveOption.h:L17-L73` 和 `plugins/paintops/libpaintop/sensors/` 目录下的各个 `KisDynamicSensor*.cpp`。
- **标准参数定义**：不透明度、流量、比例、柔和度、旋转、变暗、混色、HSV、速率、纹理强度等参数名与控件工厂集中在 `KisStandardOptionData.h:L12-L156`。
- **Mask Brush**：像素笔刷设置页里也把 masking brush 相关选项挂进来了，入口同样在 `kis_brushop_settings_widget.cpp:L74-L89`。
