#!/usr/bin/env python3
import argparse
import struct
from pathlib import Path


def image_size(path: Path):
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            i += 2
            if marker in (0xD8, 0xD9):
                continue
            if i + 2 > len(data):
                break
            length = struct.unpack(">H", data[i:i + 2])[0]
            if marker in range(0xC0, 0xC4):
                height, width = struct.unpack(">HH", data[i + 3:i + 7])
                return width, height
            i += length
    raise SystemExit(f"ERROR: unsupported or invalid image: {path}")


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
