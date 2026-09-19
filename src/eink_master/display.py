from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .capture import DISPLAY_HEIGHT, DISPLAY_WIDTH


_BANNER_FONT_SIZE = 28
_BODY_FONT_SIZE = 30
_FOOTER_FONT_SIZE = 22
_MARGIN_X = 64
_MARGIN_Y = 56
_LINE_GAP = 10

_ASCII_BANNER: dict[str, list[str]] = {
    "S": [
        " ##### ",
        "#      ",
        " ####  ",
        "     # ",
        "#####  ",
    ],
    "T": [
        "###### ",
        "  ##   ",
        "  ##   ",
        "  ##   ",
        "  ##   ",
    ],
    "A": [
        "  ##   ",
        " #  #  ",
        "###### ",
        "#    # ",
        "#    # ",
    ],
    "R": [
        "#####  ",
        "#    # ",
        "#####  ",
        "#   #  ",
        "#    # ",
    ],
    "U": [
        "#    # ",
        "#    # ",
        "#    # ",
        "#    # ",
        " ####  ",
    ],
    "P": [
        "#####  ",
        "#    # ",
        "#####  ",
        "#      ",
        "#      ",
    ],
}


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
        self._display.set_image(image.transpose(Image.Transpose.ROTATE_90))
        self._display.show()

    def render_startup_text(self, text: list[str]) -> None:
        self.show(self._render_startup_overview(text))

    def render_disconnected_text(self) -> None:
        self.show(self._render_connection_status("MQTT DISCONNECTED", ["MQTT client disconnected"]))

    def _render_connection_status(self, title: str, lines: list[str]) -> Image.Image:
        image = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), "white")
        draw = ImageDraw.Draw(image)

        title_font = self._load_monospace_font(56)
        body_font = self._load_monospace_font(34)

        title_height = self._line_height(title_font)
        body_height = self._line_height(body_font)
        total_height = title_height + 24 + (len(lines) * body_height) + max(0, (len(lines) - 1) * 14)
        y = max(_MARGIN_Y, (DISPLAY_HEIGHT - total_height) // 2)

        title_x = (DISPLAY_WIDTH - self._text_width(title, title_font)) // 2
        draw.text((title_x, y), title, fill="black", font=title_font)
        y += title_height + 24

        for line in lines:
            line_x = (DISPLAY_WIDTH - self._text_width(line, body_font)) // 2
            draw.text((line_x, y), line, fill="black", font=body_font)
            y += body_height + 14

        return image

    def _render_startup_overview(self, text: list[str]) -> Image.Image:
        image = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), "white")
        draw = ImageDraw.Draw(image)

        banner_font = self._load_monospace_font(_BANNER_FONT_SIZE)
        body_font = self._load_monospace_font(_BODY_FONT_SIZE)
        footer_font = self._load_monospace_font(_FOOTER_FONT_SIZE)

        y = _MARGIN_Y
        y = self._draw_ascii_banner(draw, banner_font, y)
        y += 18
        draw.line((_MARGIN_X, y, DISPLAY_WIDTH - _MARGIN_X, y), fill="black", width=3)
        y += 28

        for index, line in enumerate(text):
            boot_prefix = f"[{index * 0.137:10.6f}] "
            prefix_width = self._text_width(boot_prefix, body_font)
            wrapped_lines = self._wrap_text(
                line,
                body_font,
                DISPLAY_WIDTH - (_MARGIN_X * 2) - prefix_width,
            )

            for wrapped_index, wrapped_line in enumerate(wrapped_lines):
                prefix = boot_prefix if wrapped_index == 0 else " " * len(boot_prefix)
                draw.text((_MARGIN_X, y), prefix + wrapped_line, fill="black", font=body_font)
                y += self._line_height(body_font) + _LINE_GAP

            y += 6

        footer = "systemd: startup overview complete"
        footer_y = DISPLAY_HEIGHT - _MARGIN_Y - self._line_height(footer_font)
        draw.text((_MARGIN_X, footer_y), footer, fill="black", font=footer_font)
        return image

    def _draw_ascii_banner(self, draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont, y: int) -> int:
        banner_lines = self._compose_banner("STARTUP")
        for line in banner_lines:
            draw.text((_MARGIN_X, y), line, fill="black", font=font)
            y += self._line_height(font)
        return y

    def _compose_banner(self, word: str) -> list[str]:
        rows = ["" for _ in range(5)]

        for character in word.upper():
            pattern = _ASCII_BANNER.get(character)
            if pattern is None:
                pattern = ["   ???   "] * 5

            for row_index, row in enumerate(pattern):
                rows[row_index] += row + "  "

        return rows

    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
        if not text:
            return [""]

        words = text.split()
        if not words:
            return [text]

        wrapped_lines: list[str] = []
        current_line = words[0]

        for word in words[1:]:
            candidate_line = f"{current_line} {word}"
            if self._text_width(candidate_line, font) <= max_width:
                current_line = candidate_line
            else:
                wrapped_lines.append(current_line)
                current_line = word

        wrapped_lines.append(current_line)
        return wrapped_lines

    def _load_monospace_font(self, size: int) -> ImageFont.ImageFont:
        for font_path in (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
            Path("/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf"),
        ):
            if font_path.exists():
                return ImageFont.truetype(str(font_path), size=size)

        return ImageFont.load_default()

    def _text_width(self, text: str, font: ImageFont.ImageFont) -> int:
        left, _, right, _ = font.getbbox(text)
        return right - left

    def _line_height(self, font: ImageFont.ImageFont) -> int:
        _, top, _, bottom = font.getbbox("Ag")
        return bottom - top
        