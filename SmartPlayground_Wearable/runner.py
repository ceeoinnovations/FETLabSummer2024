import network
from mqtt import MQTTClient
import bluetooth
import time
import struct
import utime
import machine
from neopixel import NeoPixel
from machine import Pin, PWM
import urandom
import ubinascii


# Configuration
RUNNER_ID = ubinascii.hexlify(machine.unique_id()).decode()
WIFI_SSID = "tufts_eecs"
WIFI_PASSWORD = "foundedin1883"
MQTT_BROKER = "test.mosquitto.org"
MQTT_TOPIC = "game/status"
SAFE_DISTANCE = -50  # RSSI threshold for being "safe"
CAUGHT_DISTANCE = -40  # RSSI threshold for being caught

pin = Pin(28, Pin.OUT)   # set GPIO0 to output to drive NeoPixels
np = NeoPixel(pin, 1)   # create NeoPixel driver on GPIO0 for 8 pixels

NAME_FLAG = 0x09
SCAN_RESULT = 5
SCAN_DONE = 6

class Listen:   
    def __init__(self): 
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self.callback)
        self.scanning = False
        self.caught_count = 0
        self.last_tagger_rssi = 0
        self.save_count = 0

    def callback(self, event, data):
        if event == SCAN_RESULT:
            self.read_scan(data)

        elif event == SCAN_DONE:
            if self.scanning:
                self.stop_scan()
                
    def find_name(self, payload):
        start = 0
        name = None
        while (len(payload) - start) > 1:
            size = payload[start]
            end =  start + size + 1
            if payload[start+1] == NAME_FLAG:
                name = payload[start + 2:end]
                break
            start = end
        return str(name, "utf-8") if name else ""

    def read_scan(self, data):
            global active, caught
            addr_type, addr, adv_type, rssi, adv_data = data
            name = self.find_name(adv_data)
#             if name:
#                 print("name: %s, rssi: %d"%(name, rssi))

            if "Tagger" in name:
                # print("name: %s, rssi: %d"%(name, rssi))
                if rssi > CAUGHT_DISTANCE and not caught:
                    self.caught_count += 1
                    if self.caught_count >= 3:
                        caught = True
                        print("caught")
                        # print(rssi)
                        # Publish that this runner is caught
                        mqtt_client.publish(MQTT_TOPIC + "/caught", RUNNER_ID)
                else:
                    self.caught_count = 0
                self.last_tagger_rssi = rssi
            elif "Beacon" in name:
                # print("name: %s, rssi: %d"%(name, rssi))
                if rssi > SAFE_DISTANCE and not caught:
                    self.save_count += 1
                    if self.save_count >= 3:
                        mqtt_client.publish(MQTT_TOPIC + "/save", "save_runner")
#                         print("Attempting to save a caught runner")
                        self.save_count = 0
                else:
                    self.save_count = 0
            
    def scan(self, duration = 2000):
        self.scanning = True
        return self._ble.gap_scan(duration, 30000, 30000)

    def wait_for_scan(self):
        while self.scanning:
            #print('.',end='')
            time.sleep(0.1)
        
    def stop_scan(self):
        self.scanning = False
        self._ble.gap_scan(None)

# Setup
ble = Listen()

active = False
caught = False


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        pass
    print('WiFi connected')

def mqtt_connect():
    client = MQTTClient(f"runner_{RUNNER_ID}", MQTT_BROKER)
    client.connect()
    print('Connected to MQTT Broker')
    return client        

def mqtt_callback(topic, msg):
    global active, caught
    if topic == MQTT_TOPIC.encode():
        if msg == b"game_start":
            active = True
            caught = False
            print("game_start")
        elif msg == b"game_end":
            active = False
            print("game_end")
    elif topic == (MQTT_TOPIC + "/save_" + RUNNER_ID).encode():
        if msg == b"you_are_saved":
            caught = False
            print("You have been saved!")

# Setup
connect_wifi()
mqtt_client = mqtt_connect()
mqtt_client.set_callback(mqtt_callback)
mqtt_client.subscribe(MQTT_TOPIC)
mqtt_client.subscribe(MQTT_TOPIC + "/save_" + RUNNER_ID)

count = 1

# Main loop
while True:
    if active:
        ble.scan(0)
    if active and not caught:
        # if (count % 10 == 0):
        #     np[0] = (0, 255, 0)  # set the first pixel to green
        #     np.write()
        #     count = 1
        # else:
        #     np[0] = (255, 255, 255)
        #     np.write()
        np[0] = (0, 255, 0)  # set the first pixel to green
        np.write()
        print("active")
    else:
        # if (count % 10 == 0):
        #     np[0] = (255, 0, 0)  # set the first pixel to blue
        #     np.write()
        #     count = 1
        # else:
        #     np[0] = (255, 255, 255)
        #     np.write()
        np[0] = (255, 0, 0)  # set the first pixel to blue
        np.write()
        print("caught or inactive")
    mqtt_client.check_msg()
    count += 1
    utime.sleep(0.2)



