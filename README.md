# eink-master

Capture and display web pages at the panel's native `1200 x 1600` portrait
resolution on an Inky Impression 13.3-inch e-ink display.

## Raspberry Pi setup

1. Enable SPI with `sudo raspi-config` under **Interface Options**, then reboot.
2. Install a Chromium executable and the build/runtime packages required by Inky:

	```bash
	sudo apt update
	sudo apt install -y chromium  libopenjp2-7 python3-dev python3-pip
	```

3. Install this package on the Pi:

	```bash
	uv sync
	```

The program uses the Chromium already installed on Raspberry Pi OS. This avoids
downloading a desktop-sized Playwright browser. The Inky adapter detects the
connected display through `inky.auto`.

## Usage

```bash
uv run eink-master https://example.com \
  --browser-executable /usr/bin/chromium \
  --output /tmp/page.png
```

`--output` is optional and is useful for checking the screenshot before sending
it to the display. The URL must use `http` or `https`.

## Modules

- `capture.py` defines the `PageCapturer` interface and the Playwright adapter.
- `display.py` defines the display boundary and the Inky adapter.
- `__init__.py` contains the command-line interface and orchestration.

This separation allows the capture and display parts to be tested independently
with fakes, without requiring a browser or e-ink hardware.
