from __future__ import annotations

from eink_master.display import InkyDisplay
from eink_master.mqtt.mqtt_ha import MQTTHandler


class _FakeClient:
    def __init__(self) -> None:
        self.reconnect_called = False

    def username_pw_set(self, username, password) -> None:
        pass

    def connect(self, broker, port):
        return 0

    def subscribe(self, topic):
        return 0, 0

    def publish(self, *args, **kwargs):
        return 0, 0

    def loop_forever(self):
        pass

    def loop_start(self):
        pass

    def loop_stop(self):
        pass

    def reconnect(self):
        self.reconnect_called = True


class _FakeDisplayTarget:
    def __init__(self) -> None:
        self.image = None

    def set_image(self, image) -> None:
        self.image = image

    def show(self) -> None:
        pass


def test_render_disconnected_text_draws_content() -> None:
    fake_display = _FakeDisplayTarget()
    display = InkyDisplay(display=fake_display)

    display.render_disconnected_text()

    assert fake_display.image is not None
    assert fake_display.image.getbbox() is not None


def test_mqtt_disconnect_triggers_display_callback(monkeypatch) -> None:
    fake_client = _FakeClient()
    callback_calls = []

    monkeypatch.setattr("eink_master.mqtt.mqtt_ha.mqtt.Client", lambda *args, **kwargs: fake_client)

    handler = MQTTHandler(
        broker="example.org",
        on_disconnect_callback=lambda: callback_calls.append(True),
    )
    handler.is_it_connected = True

    handler.on_disconnect(fake_client, None, None, 0, None)

    assert handler.is_it_connected is False
    assert callback_calls == [True]