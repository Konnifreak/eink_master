from PIL import Image

from eink_master.capture import DISPLAY_HEIGHT, DISPLAY_WIDTH


def test_display_dimensions_are_native_resolution() -> None:
    image = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT))

    assert image.size == (1200, 1600)