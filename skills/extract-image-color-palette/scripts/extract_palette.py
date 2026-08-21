#!/usr/bin/env python3
"""使用 Pillow 和 NumPy 提取图片主色，并向标准输出打印文字色卡。"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageOps, UnidentifiedImageError
except ImportError as exc:
    print(
        "错误：缺少依赖。请使用同时安装了 Pillow 和 NumPy 的 Python 环境运行此脚本。",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


@dataclass(frozen=True)
class PaletteColor:
    rank: int
    red: int
    green: int
    blue: int
    pixel_count: int
    proportion: float

    @property
    def hex(self) -> str:
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"


@dataclass(frozen=True)
class Analysis:
    source_name: str
    source_size: tuple[int, int]
    sample_size: tuple[int, int]
    analyzed_pixel_count: int
    alpha_threshold: int
    colors: list[PaletteColor]


def bounded_integer(minimum: int, maximum: int):
    def parse(value: str) -> int:
        try:
            result = int(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError("必须是整数") from exc
        if not minimum <= result <= maximum:
            raise argparse.ArgumentTypeError(f"必须在 {minimum}...{maximum} 范围内")
        return result

    return parse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="使用 Pillow 从图片中提取主色，并直接输出文字色卡。"
    )
    parser.add_argument("image", type=Path, help="输入图片路径")
    parser.add_argument(
        "--colors",
        type=bounded_integer(1, 16),
        default=8,
        help="提取颜色数，默认 8",
    )
    parser.add_argument(
        "--max-size",
        type=bounded_integer(128, 2048),
        default=640,
        help="分析缩略图的最大边长，默认 640",
    )
    parser.add_argument(
        "--alpha-threshold",
        type=bounded_integer(0, 255),
        default=12,
        help="忽略 alpha 小于等于该值的像素，默认 12",
    )
    return parser.parse_args()


def load_sample(
    path: Path, max_size: int, alpha_threshold: int
) -> tuple[tuple[int, int], tuple[int, int], np.ndarray]:
    if not path.is_file():
        raise ValueError(f"找不到图片：{path}")

    try:
        with Image.open(path) as source:
            source.seek(0)
            oriented = ImageOps.exif_transpose(source)
            source_size = oriented.size
            sample = oriented.convert("RGBA")
            sample.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            sample_size = sample.size
            pixels = np.asarray(sample, dtype=np.uint8)
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError(f"图片无法解码：{path}") from exc

    visible = pixels[..., 3] > alpha_threshold
    rgb_pixels = np.ascontiguousarray(pixels[..., :3][visible])
    if rgb_pixels.size == 0:
        raise ValueError(
            "没有可分析像素；图片可能完全透明，可尝试降低 --alpha-threshold"
        )
    return source_size, sample_size, rgb_pixels


def quantize_colors(rgb_pixels: np.ndarray, requested: int) -> list[PaletteColor]:
    # 将不透明像素排成一行再量化，确保透明区域完全不参与颜色统计。
    pixel_strip = Image.fromarray(rgb_pixels.reshape(1, -1, 3))
    quantized = pixel_strip.quantize(
        colors=requested,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    )
    counts = quantized.getcolors(maxcolors=256) or []
    palette = quantized.getpalette() or []
    total = int(rgb_pixels.shape[0])

    extracted: list[tuple[int, int, int, int]] = []
    for pixel_count, palette_index in counts:
        offset = palette_index * 3
        if offset + 2 >= len(palette):
            continue
        red, green, blue = palette[offset : offset + 3]
        extracted.append((int(pixel_count), int(red), int(green), int(blue)))

    extracted.sort(key=lambda item: (-item[0], item[1], item[2], item[3]))
    return [
        PaletteColor(
            rank=index,
            red=red,
            green=green,
            blue=blue,
            pixel_count=pixel_count,
            proportion=pixel_count / total,
        )
        for index, (pixel_count, red, green, blue) in enumerate(extracted, start=1)
    ]


def analyze(path: Path, colors: int, max_size: int, alpha_threshold: int) -> Analysis:
    resolved = path.expanduser().resolve()
    source_size, sample_size, rgb_pixels = load_sample(
        resolved, max_size, alpha_threshold
    )
    palette = quantize_colors(rgb_pixels, colors)
    if not palette:
        raise ValueError("未能提取颜色")
    return Analysis(
        source_name=resolved.name,
        source_size=source_size,
        sample_size=sample_size,
        analyzed_pixel_count=int(rgb_pixels.shape[0]),
        alpha_threshold=alpha_threshold,
        colors=palette,
    )


def print_analysis(result: Analysis) -> None:
    print("图片色卡")
    print(f"图片：{result.source_name}")
    print(f"尺寸：{result.source_size[0]} × {result.source_size[1]} px")
    print(
        f"采样：{result.sample_size[0]} × {result.sample_size[1]} px，"
        f"有效像素 {result.analyzed_pixel_count}"
    )
    print(
        "算法：Pillow MEDIANCUT 中位切分量化；"
        f"忽略 alpha ≤ {result.alpha_threshold} 的像素"
    )
    print()
    for color in result.colors:
        print(
            f"{color.rank}. {color.hex} | "
            f"RGB({color.red}, {color.green}, {color.blue}) | "
            f"{color.proportion * 100:.2f}%"
        )


def main() -> int:
    args = parse_args()
    try:
        result = analyze(
            args.image,
            colors=args.colors,
            max_size=args.max_size,
            alpha_threshold=args.alpha_threshold,
        )
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    print_analysis(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
