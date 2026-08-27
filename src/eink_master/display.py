from __future__ import annotations

from typing import Any

from PIL import Image


class EInkDisplay:
    def show(self, image: Image.Image) -> None:
        """Send an image to the physical display."""


class InkyDisplay(EInkDisplay):
    def __init__(self, display: Any | None = None) -> None:
        if display is None:
            from inky.auto import auto

            display = auto()
        self._display = display

    def show(self, image: Image.Image) -> None:
        self._display.set_image(image)
        self._display.show()