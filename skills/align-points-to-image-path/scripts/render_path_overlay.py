#!/usr/bin/env python3
"""Render numbered percentage coordinates over an image for visual auditing."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_points(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        items = sorted(data.items(), key=lambda item: int(item[0]))
        points = [(str(key), value) for key, value in items]
    elif isinstance(data, list):
        points = [(str(index), value) for index, value in enumerate(data, 1)]
    else:
        raise ValueError("points JSON must be a list or an object keyed by step")

    normalized = []
    for label, point in points:
        x = float(point["x"])
        y = float(point["y"])
        if not 0 <= x <= 100 or not 0 <= y <= 100:
            raise ValueError(f"point {label} is outside 0–100 percent")
        normalized.append((label, x, y))
    if not normalized:
        raise ValueError("points JSON is empty")
    return normalized


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="source background image")
    parser.add_argument("points", help="JSON coordinates in percentages")
    parser.add_argument("output", help="PNG or WebP diagnostic output")
    parser.add_argument("--max-width", type=int, default=1200)
    parser.add_argument("--radius", type=int, default=10)
    parser.add_argument("--connect", action="store_true")
    args = parser.parse_args()

    source = Image.open(args.image).convert("RGB")
    scale = min(1.0, args.max_width / source.width)
    size = (round(source.width * scale), round(source.height * scale))
    preview = source.resize(size, Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(preview)
    font = ImageFont.load_default()
    points = load_points(args.points)
    pixels = [(label, x / 100 * size[0], y / 100 * size[1]) for label, x, y in points]

    if args.connect:
        draw.line([(x, y) for _, x, y in pixels], fill=(0, 255, 255), width=2)

    radius = max(3, round(args.radius * scale))
    for label, x, y in pixels:
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(0, 220, 255),
            outline="white",
            width=max(1, round(2 * scale)),
        )
        draw.text((x + radius + 2, y - radius), label, fill="white", font=font)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    preview.save(args.output)
    print(f"Rendered {len(points)} points to {args.output}")


if __name__ == "__main__":
    main()
