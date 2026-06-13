#!/usr/bin/env python3
# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10"]
# ///

"""Convert PNG or JPEG to WebP at fixed quality, preserving image dimensions.

After a successful write, the original file is removed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

ALLOWED_SUFFIXES = frozenset({".png", ".jpg", ".jpeg"})
WEBP_QUALITY = 80


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Convert a PNG or JPEG image to WebP (quality %d, same pixel dimensions); "
            "remove the source file after success."
        )
        % WEBP_QUALITY
    )
    p.add_argument(
        "input",
        type=Path,
        help="Path to input .png, .jpg, or .jpeg file",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output .webp path (default: same directory as input, .webp extension)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    src = args.input.expanduser().resolve()

    if not src.is_file():
        print(f"error: not a file: {src}", file=sys.stderr)
        return 1

    suffix = src.suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        print(
            f"error: expected extension .png, .jpg, or .jpeg; got {src.suffix!r}",
            file=sys.stderr,
        )
        return 1

    if args.output is not None:
        out = args.output.expanduser().resolve()
    else:
        out = src.with_suffix(".webp")

    if src.resolve() == out.resolve():
        print(
            "error: input and output paths resolve to the same file; refusing to overwrite",
            file=sys.stderr,
        )
        return 1

    try:
        with Image.open(src) as im:
            im.save(out, format="WEBP", quality=WEBP_QUALITY)
    except OSError as e:
        print(f"error: could not read or write image: {e}", file=sys.stderr)
        return 1

    try:
        src.unlink()
    except OSError as e:
        print(
            f"error: wrote {out} but could not remove original {src}: {e}",
            file=sys.stderr,
        )
        return 1

    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
