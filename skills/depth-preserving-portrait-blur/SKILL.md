---
name: depth-preserving-portrait-blur
description: 将人物图片转为供生图模型使用的近白远黑灰度相对深度条件图，弱化五官与纹理，保留人物、发型、场景轮廓和前后层次。只输出一张 8 位 RGB PNG，不生成彩色模糊图。
---

# 人物相对深度图

## 输出契约

- 输入：一张 PNG、JPEG 或 WebP 图片。
- `output`：一张 8 位 RGB PNG；三个通道数值相同，视觉上为灰度图，便于作为生图模型的深度条件输入。
- 默认白色表示相对更近，黑色表示相对更远。这不是米制深度。

## 执行

1. 使用 `view_image` 检查输入。
2. 将 `scripts/estimate_depth.py` 相对于本 `SKILL.md` 解析。
3. 使用当前项目或系统中可用的 Python 3.10–3.12 环境；该环境需要安装 PyTorch、torchvision、Transformers、Pillow 和 NumPy。不要假定固定的 Python 安装路径，也不要直接修改项目依赖。
4. 先预检解释器、依赖及设备：

```text
<python> "<skill-dir>/scripts/estimate_depth.py" --check-env --device auto
```

预检失败时再读取 [references/depth-estimation.md](references/depth-estimation.md)，在任务可写的临时目录中创建隔离环境，并把安装器缓存和模型缓存放到可写位置。不要在同一个不兼容解释器或不可写缓存路径上重复运行。

5. 预检通过后运行：

```text
<python> "<skill-dir>/scripts/estimate_depth.py" "input.png" "outputs/depth.png" --device auto
```

将 `<python>` 替换为当前环境的解释器命令或绝对路径，例如 `python`、`python3`、`py -3` 或虚拟环境中的 Python。输入和输出使用当前任务可访问的路径；脚本会创建尚不存在的输出目录。

`--device auto` 按 CUDA、MPS、CPU 的顺序选择可用设备。也可显式指定：NVIDIA GPU 使用 `--device cuda`，Apple Silicon 使用 `--device mps`，无可用加速设备或明确需要 CPU 时使用 `--device cpu`。显式指定的设备不可用时应报告错误，不要擅自更换设备。

模型缓存默认由 Hugging Face 管理；需要固定缓存位置时再传入 `--cache-dir <cache-dir>`。首次运行可能需要联网下载模型，离线且已有缓存时使用 `--local-files-only`。需要模型、环境或备选方案细节时，读取 [references/depth-estimation.md](references/depth-estimation.md)。

## 验收

- 使用 `view_image` 检查输出：人物、发型、姿势、遮挡和场景大轮廓应与原图一致，五官和表面纹理应被平滑深度曲面弱化。
- 检查前后关系，不得把原图的明暗直接当作远近。方向反了时使用 `--near black` 重跑。
- 确认 PNG 与自动旋转后的原图同尺寸，模式为 8 位 RGB，文件非空。
- 不要覆盖原图或将伪深度结构引导冒充为模型深度图。
