from PIL import Image

from eink_master.capture import DISPLAY_HEIGHT, DISPLAY_WIDTH, OUTPUT_HEIGHT, OUTPUT_WIDTH


def test_display_dimensions_are_native_resolution() -> None:
    image = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT))
    landscape_image = image.transpose(Image.Transpose.ROTATE_90)

    assert image.size == (1200, 1600)
    assert landscape_image.size == (OUTPUT_WIDTH, OUTPUT_HEIGHT)
    assert landscape_image.size == (1600, 1200)