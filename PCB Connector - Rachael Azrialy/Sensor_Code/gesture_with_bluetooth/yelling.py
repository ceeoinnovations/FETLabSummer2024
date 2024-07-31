import bluetooth
import time
import struct
import gesture
import SoftI2C
from hub import pins as Pin
from hub import uart
from time import sleep

i2c = SoftI2C.SoftwareI2C(scl_pin=Pin.TX, sda_pin=Pin.RX)

g=gesture.Gesture(i2c)

NAME_FLAG = 0x09

class Yell:
    def __init__(self):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        
    def advertise(self, name = 'Pico', interval_us=100000):
        short = name[:8]
        payload = struct.pack("BB", len(short) + 1, NAME_FLAG) + name[:8]  # byte length, byte type, value
        self._ble.gap_advertise(interval_us, adv_data=payload)
        
    def stop_advertising(self):
        self._ble.gap_advertise(None)

p = Yell()


while True:
    value=g.return_gesture()
    #print(value)
    
    #nothing
    if value==0:
        p.advertise('~0')
        print('0, nothing')
    #honk horn
    elif value==1:
        p.advertise('~1')
        print('1, honk')
    #stop
    elif value==2:
        p.advertise('~2')
        print('2, stop')
    #right
    elif value==3:
        p.advertise('~3')
        print('3, right')
    #left
    elif value==4:
        p.advertise('~4')
        print('4, left')
    #up/straight
    elif value==5:
        p.advertise('~5')
        print('5, straight')
    #down/reverse
    elif value==6:
        p.advertise('~6')
        print('6, reverse')
    #clockwise spin
    elif value==7:
        p.advertise('~7')
        print('7, clock spin')
    #counterclockwise spin
    elif value==8:
        p.advertise('~8')
        print('8, counter spin')
    #wave
    elif value==9:
        p.advertise('~9')
        print('9, wave')
    time.sleep(0.1)
    
p.stop_advertising()
