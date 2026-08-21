# 深度估计后端

## 默认方案

使用官方 [Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2) 的 `Depth-Anything-V2-Small-hf`：

- 类型：单目相对深度，不是米制距离；
- 规模：约 24.8M 参数，模型权重约 99 MB；
- 用途：直接生成隐藏纹理、保留人物与场景轮廓的灰度深度效果图；
- 许可证：Small 模型为 Apache-2.0；
- 加载方式：按官方说明通过 Transformers 的 `AutoImageProcessor` 和 `AutoModelForDepthEstimation` 加载；
- 默认输出：一张供生图模型使用的 8 位 RGB PNG，三个通道数值相同；近处为白色。

不要为了使用该模型克隆整个 GitHub 仓库。当前 skill 已封装官方 Transformers 推理方式。

## 运行环境

使用 Python 3.10–3.12，并确保同一环境中安装以下依赖：

- PyTorch
- torchvision
- Transformers
- Pillow
- NumPy

`torch` 与 `torchvision` 必须使用相互兼容的版本。虽然图像预处理显式使用 PIL 后端，当前 Transformers 的 `AutoImageProcessor` 入口仍可能在初始化时检查 torchvision，因此不要把它视为可选依赖。

优先复用已经满足要求的虚拟环境；不要假定某个操作系统、用户名、工作区或 Python 的固定路径。命令中的 `<python>` 可以替换为 `python`、`python3`、`py -3` 或虚拟环境解释器的绝对路径。先运行：

```text
<python> "<skill-dir>/scripts/estimate_depth.py" --check-env --device auto
```

只有预检失败时才创建隔离环境。使用任务可写的临时目录，不要修改项目锁文件或把依赖安装到系统 Python。可以使用环境中已有的工具，例如：

```text
<python-3.10-to-3.12> -m venv <temp-venv>
<temp-python> -m pip install torch torchvision transformers Pillow NumPy
```

或：

```text
uv venv --python <python-3.10-to-3.12> <temp-venv>
uv pip install --python <temp-python> torch torchvision transformers Pillow NumPy
```

若安装器默认缓存目录不可读写，将其缓存改到同一临时目录；若模型默认缓存目录不可写，运行推理时传入 `--cache-dir <writable-cache>`。联网失败时先确认是否需要授权或离线缓存，不要反复执行相同的失败命令。

首次运行可能会从 Hugging Face 下载模型权重。默认使用 Hugging Face 缓存；需要可复现或共享缓存时，通过 `--cache-dir <cache-dir>` 显式指定。离线且模型已经缓存时使用 `--local-files-only`。

## 设备选择

- `--device auto`：依次选择 CUDA、MPS、CPU，适合作为通用默认值；
- `--device cuda`：用于安装了兼容 PyTorch 和驱动的 NVIDIA GPU；
- `--device mps`：用于支持 MPS 的 Apple Silicon 环境；
- `--device cpu`：用于没有可用加速设备或明确要求 CPU 的环境。

显式指定的设备不可用时脚本会停止并报告错误。若受沙箱或容器限制而无法访问本机加速设备，应先尝试在允许访问设备的环境中重跑，再决定是否改用 CPU。

## 输出语义

- 白色表示相对更近，黑色表示相对更远；可用 `--near black` 反转。
- 输出经过 2%–98% 百分位裁剪，减少极少量异常值对对比度的影响。
- 这是单张图推断出的相对深度，适合直接表现层次、轮廓和遮挡，不适合测量真实距离或尺寸。
- 原图中的镜面、透明玻璃、极细发丝和严重虚化区域可能产生错误深度，应目视检查输出图。
- 将视觉上为灰度的 8 位 RGB PNG 视为最终交付，不再生成 16 位深度图、JSON 元数据或彩色模糊图。

## 备选方案

需要绝对米制深度、焦距估计或更强边界精度时，可评估其他专用模型，例如 Apple 官方 [ml-depth-pro](https://github.com/apple/ml-depth-pro)。它更重，安装与模型下载成本更高，不作为本 skill 默认依赖。

旧 MiDaS 仓库已归档，不作为新实现的首选。
