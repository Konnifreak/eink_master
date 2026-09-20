from __future__ import annotations

import datetime

from pathlib import Path

from .capture import PlaywrightPageCapturer
from .display import InkyDisplay
from .mqtt.mqtt_ha import MQTTHandler
from .setup.env_setup import get_env_variable
from .setup.get_ip import get_ip_address


def render_to_display(in_display: InkyDisplay, url: str, browser_executable: Path | None = None, timeout_seconds: int = 30) -> None:
    capturer = PlaywrightPageCapturer(
        browser_executable=browser_executable,
        timeout_seconds=timeout_seconds,
    )
    image = capturer.capture(url)
    in_display.show(image)

def startup() -> tuple[dict[str, str | None], MQTTHandler, InkyDisplay]:
    env_vars = get_env_variable()
    if env_vars is None:
        raise ValueError("Could not load environment configuration")

    display = InkyDisplay()
    first_startup_dict = ["Load Settings - DateTime: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]

    mqtt_client = MQTTHandler(
        broker=env_vars.get("mqtt_server"),
        port=int(env_vars.get("mqtt_port", 1883)),
        client_id=env_vars.get("mqtt_client_id"),
        username=env_vars.get("mqtt_username") if env_vars.get("mqtt_username") and env_vars.get("mqtt_password") else None,
        password=env_vars.get("mqtt_password") if env_vars.get("mqtt_username") and env_vars.get("mqtt_password") else None,
        on_disconnect_callback=display.render_disconnected_text,
    )

    first_startup_dict.append("MQTT Server: " + env_vars.get("mqtt_server", ""))
    first_startup_dict.append("MQTT Status: " + ("Connected" if mqtt_client.is_it_connected else "Disconnected"))

    first_startup_dict.append("IP Address: " + get_ip_address())
    display.render_startup_text(first_startup_dict)

    return env_vars, mqtt_client, display


def main() -> None:
    envs, mqtt_client, display = startup()
    mqtt_client.publish_homeassistant_text_data("render_url", "eInky Frame", "eink_frame_001", "", qos=0, retain=True)
    mqtt_client.publish_homeassistant_sensor_data("status", "eInky Frame", "eink_frame_001", "Connected", qos=0, retain=True)

    def handle_render_url(topic: str, payload: str) -> None:
        mqtt_client.publish("homeassistant/text/render_url/state", payload, qos=0, retain=True)
        render_to_display(
            in_display=display,
            url=payload,
            browser_executable=Path(envs.get("browser_executable")),
            timeout_seconds=int(envs.get("timeout_seconds", 30)),
        )

    mqtt_client.subscribe("homeassistant/text/render_url/command", handle_render_url)


    mqtt_client.loop_forever()
