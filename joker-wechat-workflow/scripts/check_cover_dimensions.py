#!/usr/bin/env python3
import argparse
import struct
from pathlib import Path


def image_size(path: Path):
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("ERROR: Pillow is required; install Pillow before validating images")
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image.load()
            return image.size
    except (OSError, ValueError, SyntaxError) as exc:
        raise SystemExit(f"FAIL: image cannot be fully decoded: {path}: {exc}")



parser = argparse.ArgumentParser()
parser.add_argument("--image", required=True)
parser.add_argument("--width", type=int, required=True)
parser.add_argument("--height", type=int, required=True)
args = parser.parse_args()

path = Path(args.image)
width, height = image_size(path)
if (width, height) != (args.width, args.height):
    raise SystemExit(
        f"FAIL: {path.name} is {width}x{height}; expected {args.width}x{args.height}"
    )
print(f"PASS: {path.name} is exactly {width}x{height}")
