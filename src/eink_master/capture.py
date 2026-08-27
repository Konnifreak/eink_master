from __future__ import annotations

from io import BytesIO
from typing import Protocol
from urllib.parse import urlparse

from PIL import Image


DISPLAY_WIDTH = 1200
DISPLAY_HEIGHT = 1600


class PageCapturer(Protocol):
    def capture(self, url: str) -> Image.Image:
        """Capture a page at the display's native pixel dimensions."""


class PlaywrightPageCapturer:
    def __init__(
        self,
        browser_executable: str | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        self.browser_executable = browser_executable
        self.timeout_ms = timeout_seconds * 1000

    def capture(self, url: str) -> Image.Image:
        self._validate_url(url)

        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                executable_path=self.browser_executable,
            )
            try:
                page = browser.new_page(
                    viewport={"width": DISPLAY_WIDTH, "height": DISPLAY_HEIGHT},
                    device_scale_factor=1,
                )
                page.goto(url, wait_until="networkidle", timeout=self.timeout_ms)
                screenshot = page.screenshot(type="png", full_page=False)
            finally:
                browser.close()

        with Image.open(BytesIO(screenshot)) as image:
            return image.convert("RGB")

    @staticmethod
    def _validate_url(url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("url must be an absolute HTTP or HTTPS URL")