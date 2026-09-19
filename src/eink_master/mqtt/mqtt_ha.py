import json
from collections.abc import Callable

import paho.mqtt.client as mqtt

class MQTTHandler:
    def __init__(
        self,
        broker,
        port=1883,
        client_id=None,
        username=None,
        password=None,
        on_disconnect_callback: Callable[[], None] | None = None,
    ):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
        if username and password:
            self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.message_callbacks = {}
        self.topics = []
        self.on_disconnect_callback = on_disconnect_callback
        self.client.connect(broker, port)
        self.is_it_connected = False

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if str(reason_code) == "Success":
            self.is_it_connected = True


    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        self.is_it_connected = False
        if self.on_disconnect_callback is not None:
            self.on_disconnect_callback()

        if str(reason_code) != "Success":
            self.client.reconnect()

    #def is_connected(self):
        #return self.client.is_connected()

    def on_message(self, client, userdata, msg):
        if msg.topic in self.message_callbacks:
            self.message_callbacks[msg.topic](msg.topic, msg.payload.decode())

    def subscribe(self, topic, callback):
        if topic not in self.topics:
            self.topics.append(topic)
            self.client.subscribe(topic)
        self.message_callbacks[topic] = callback

    def publish(self, topic, payload, qos=0, retain=False):
        self.client.publish(topic, payload, qos, retain)
    
    def publish_homeassistant_sensor_data(self, sensor_name, device_name, identifier, value, qos=2, retain=True):
        state_topic = f"homeassistant/sensor/{sensor_name}/state"
        payload = value

        # add configuration topic for Home Assistant discovery
        config_topic = f"homeassistant/sensor/{sensor_name}/config"
        config_payload = {
            "name": sensor_name,
            "state_topic": state_topic,
            "unique_id": f"{device_name}_{sensor_name}",
            "device": {
                "name": device_name,
                "identifiers": identifier,
                "manufacturer": "Kjasny",
                "model": "eInky Frame",
                "sw_version": "1.0.0"
            },
            "qos": qos,
            "retain": retain
        }
        # publish configuration topic
        check_config = self.client.publish(config_topic, json.dumps(config_payload), qos=qos, retain=retain)
        check_publish = self.client.publish(state_topic, json.dumps(payload), qos=qos, retain=retain)
        return check_publish[0]

    def publish_homeassistant_text_data(self, sensor_name, device_name, identifier, value, qos=2, retain=True):
        state_topic = f"homeassistant/text/{sensor_name}/state"
        payload = value

        # add configuration topic for Home Assistant discovery
        config_topic = f"homeassistant/text/{sensor_name}/config"
        config_payload = {
            "name": sensor_name,
            "state_topic": state_topic,
            "unique_id": f"{device_name}_{sensor_name}",
            "device": {
                "name": device_name,
                "identifiers": identifier,
                "manufacturer": "Kjasny",
                "model": "eInky Frame",
                "sw_version": "1.0.0"
            },
            "max": 255,
            "platform": "text",
            "qos": qos,
            "retain": retain
        }
        # publish configuration topic
        check_config = self.client.publish(config_topic, json.dumps(config_payload), qos=qos, retain=retain)
        check_publish = self.client.publish(state_topic, json.dumps(payload), qos=qos, retain=retain)
        return check_publish[0]


    def loop_forever(self):
        self.client.loop_forever()

    def connect(self):
        self.client.connect()

    def loop_start(self):
        self.client.loop_start()

    def loop_stop(self):
        self.client.loop_stop()