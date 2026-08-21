#!/usr/bin/env python3
"""Generate an 8-bit RGB relative depth condition image with Depth Anything V2 Small."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


DEFAULT_MODEL = "depth-anything/Depth-Anything-V2-Small-hf"


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def ensure_input(path_value: str) -> Path:
    path = Path(path_value).expanduser().resolve()
    if not path.is_file() or path.stat().st_size == 0:
        fail(f"输入图片不存在或为空：{path}")
    return path


def prepare_output(path_value: str, input_path: Path, force: bool) -> Path:
    path = Path(path_value).expanduser().resolve()
    if path == input_path:
        fail("深度图不能覆盖输入图片")
    if path.exists() and not force:
        fail(f"深度图已存在：{path}；使用 --force 才能覆盖")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def validate_python() -> None:
    version = sys.version_info[:2]
    if not (3, 10) <= version <= (3, 12):
        fail(
            "需要 Python 3.10–3.12；"
            f"当前解释器为 Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )


def load_dependencies():
    try:
        import numpy as np
        import PIL
        import torch
        import torchvision
        import transformers
        from PIL import Image, ImageOps
        from transformers import AutoImageProcessor, AutoModelForDepthEstimation
    except Exception as error:
        fail(
            "深度估计依赖缺失或不兼容。需要相互兼容的 torch、torchvision，以及 "
            "transformers、Pillow 和 NumPy；可先在隔离环境中安装 "
            "`torch torchvision transformers Pillow NumPy`。"
            f"原始错误：{error}"
        )
    return (
        np,
        PIL,
        torch,
        torchvision,
        transformers,
        Image,
        ImageOps,
        AutoImageProcessor,
        AutoModelForDepthEstimation,
    )


def processor_options(transformers) -> dict[str, object]:
    version_text = str(getattr(transformers, "__version__", "0"))
    first_component = version_text.split(".", 1)[0]
    major = int(first_component) if first_component.isdigit() else 0
    if major >= 5:
        return {"backend": "pil"}
    return {"use_fast": False}


def resolve_device(torch, requested: str) -> str:
    mps = getattr(torch.backends, "mps", None)
    mps_available = bool(mps and mps.is_built() and mps.is_available())
    if requested == "cuda":
        if not torch.cuda.is_available():
            fail("请求了 CUDA，但当前环境不可用")
        return "cuda"
    if requested == "mps":
        if not mps_available:
            fail("请求了 MPS，但当前 PyTorch 或运行环境不支持该设备")
        return "mps"
    if requested == "cpu":
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"
    if mps_available:
        return "mps"
    return "cpu"


def normalize_depth(np, depth, low_percentile: float, high_percentile: float, near: str):
    finite = np.isfinite(depth)
    if not finite.any():
        fail("模型输出不包含有效深度值")
    valid = depth[finite]
    low = float(np.percentile(valid, low_percentile))
    high = float(np.percentile(valid, high_percentile))
    if high <= low:
        low = float(valid.min())
        high = float(valid.max())
    if high <= low:
        fail("模型输出深度范围为零")
    clipped = np.clip(depth, low, high)
    normalized = (clipped - low) / (high - low)
    normalized[~finite] = 0.0
    if near == "black":
        normalized = 1.0 - normalized
    return normalized


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="输入图片（PNG/JPEG/WebP 等 Pillow 支持的格式）")
    parser.add_argument("output", nargs="?", help="供生图模型使用的 8 位 RGB 相对深度 PNG")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Hugging Face 模型 ID")
    parser.add_argument(
        "--device", choices=("auto", "mps", "cuda", "cpu"), default="auto", help="推理设备"
    )
    parser.add_argument("--cache-dir", help="模型缓存目录；未指定时使用 Hugging Face 默认缓存")
    parser.add_argument(
        "--local-files-only", action="store_true", help="禁止联网，只使用已缓存的模型文件"
    )
    parser.add_argument("--low-percentile", type=float, default=2.0, help="归一化低百分位")
    parser.add_argument("--high-percentile", type=float, default=98.0, help="归一化高百分位")
    parser.add_argument(
        "--near", choices=("white", "black"), default="white", help="近处使用白色或黑色"
    )
    parser.add_argument("--force", action="store_true", help="允许覆盖已有输出")
    parser.add_argument(
        "--check-env", action="store_true", help="只检查 Python、依赖和推理设备，不加载模型"
    )
    args = parser.parse_args()

    validate_python()

    if args.check_env:
        np, PIL, torch, torchvision, transformers, *_ = load_dependencies()
        device = resolve_device(torch, args.device)
        print(
            "环境检查通过："
            f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}, "
            f"torch {torch.__version__}, torchvision {torchvision.__version__}, "
            f"transformers {transformers.__version__}, Pillow {PIL.__version__}, "
            f"NumPy {np.__version__}, device={device}"
        )
        return

    if not args.input or not args.output:
        parser.error("input 和 output 为必填参数；仅检查环境时使用 --check-env")

    if not 0 <= args.low_percentile < args.high_percentile <= 100:
        fail("百分位必须满足 0 <= low < high <= 100")

    input_path = ensure_input(args.input)
    output = prepare_output(args.output, input_path, args.force)
    if output.suffix.lower() != ".png":
        fail("深度图必须使用 .png 扩展名")

    (
        np,
        _PIL,
        torch,
        _torchvision,
        transformers,
        Image,
        ImageOps,
        AutoImageProcessor,
        AutoModelForDepthEstimation,
    ) = load_dependencies()
    device = resolve_device(torch, args.device)
    cache_dir = Path(args.cache_dir).expanduser().resolve() if args.cache_dir else None
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)

    try:
        image = ImageOps.exif_transpose(Image.open(input_path)).convert("RGB")
    except Exception as error:
        fail(f"无法读取输入图片：{error}")

    load_options = {
        "cache_dir": str(cache_dir) if cache_dir else None,
        "local_files_only": args.local_files_only,
    }
    load_options = {key: value for key, value in load_options.items() if value is not None}
    try:
        processor = AutoImageProcessor.from_pretrained(
            args.model, **processor_options(transformers), **load_options
        )
        model = AutoModelForDepthEstimation.from_pretrained(args.model, **load_options)
    except Exception as error:
        fail(
            f"无法加载模型 {args.model}。首次运行需要联网；缓存目录不可写时请传入 "
            f"--cache-dir <writable-cache>；离线运行需要预先缓存完整模型。原始错误：{error}"
        )

    model = model.to(device).eval()
    inputs = processor(images=image, return_tensors="pt")
    inputs = {name: tensor.to(device) for name, tensor in inputs.items()}
    try:
        with torch.inference_mode():
            predicted = model(**inputs).predicted_depth
            resized = torch.nn.functional.interpolate(
                predicted.unsqueeze(1),
                size=(image.height, image.width),
                mode="bicubic",
                align_corners=False,
            )
        depth = resized.squeeze().float().cpu().numpy()
    except Exception as error:
        fail(f"深度推理失败（device={device}）：{error}")

    normalized = normalize_depth(
        np, depth, args.low_percentile, args.high_percentile, args.near
    )
    depth_u8 = np.round(normalized * 255.0).astype(np.uint8)
    Image.fromarray(depth_u8).convert("RGB").save(output)

    if not output.is_file() or output.stat().st_size == 0:
        fail(f"深度图创建失败：{output}")
    print(f"深度图已生成：{output}")


if __name__ == "__main__":
    main()
