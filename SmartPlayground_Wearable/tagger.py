import network
from mqtt import MQTTClient
import bluetooth
import time
import struct
import utime
import machine
from machine import Pin

# Configuration
WIFI_SSID = "tufts_eecs"
WIFI_PASSWORD = "foundedin1883"
MQTT_BROKER = "test.mosquitto.org"
MQTT_TOPIC = "game/status"
NAME_FLAG = 0x09

class Yell:
    def __init__(self):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        
    def advertise(self, name = 'Tagger', interval_us=100000):
        short = name[:8]
        payload = struct.pack("BB", len(short) + 1, NAME_FLAG) + name[:8]  # byte length, byte type, value
        self._ble.gap_advertise(interval_us, adv_data=payload)
        
    def stop_advertising(self):
        self._ble.gap_advertise(None)
# Setup
ble = Yell()

# Game state
active = False

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        pass
    print('WiFi connected')

def mqtt_connect():
    client = MQTTClient("tagger", MQTT_BROKER)
    client.connect()
    print('Connected to MQTT Broker')
    return client

def mqtt_callback(topic, msg):
    global active
    if msg == b"game_start":
        active = True
    elif msg == b"game_end":
        active = False

# Setup
connect_wifi()
mqtt_client = mqtt_connect()
mqtt_client.set_callback(mqtt_callback)
mqtt_client.subscribe(MQTT_TOPIC)

# Main loop
while True:
    if active:
        ble.advertise('Tagger')
    mqtt_client.check_msg()
    utime.sleep(0.1)


