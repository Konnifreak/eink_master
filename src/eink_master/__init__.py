from __future__ import annotations

import argparse
from pathlib import Path

from .capture import PlaywrightPageCapturer
from .display import InkyDisplay


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture a web page and show it on an Inky Impression display."
    )
    parser.add_argument("url", help="URL to capture")
    parser.add_argument(
        "--browser-executable",
        help="Path to Chromium or Chrome (useful with Raspberry Pi system Chromium)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Also save the captured PNG to this path",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Page load timeout in seconds (default: 30)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    capturer = PlaywrightPageCapturer(
        browser_executable=args.browser_executable,
        timeout_seconds=args.timeout,
    )
    image = capturer.capture(args.url)

    if args.output is not None:
        image.save(args.output, format="PNG")

    InkyDisplay().show(image)
