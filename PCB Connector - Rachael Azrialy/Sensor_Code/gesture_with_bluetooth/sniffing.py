from hub import port
import motor
from hub import light_matrix
from hub import sound
import bluetooth
import time
import struct

NAME_FLAG = 0x09
IRQ_SCAN_RESULT = 5
IRQ_SCAN_DONE = 6

L = port.A
R = port.B
motors = [L, R]

class Sniff: 
    def __init__(self): 
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self.scanning = False 
        self.names = []
        self.command = 5

    def _irq(self, event, data):
        if event == IRQ_SCAN_RESULT: #check to see if it is a serialperipheral
            addr_type, addr, adv_type, rssi, adv_data = data
            name = self.decode_name(adv_data)
            #print('.',end='')
            if name == '':
                return
            if name[0] != '~':
                return
            self.command = int(name[1])

        elif event == IRQ_SCAN_DONE:  # close everything
            self.scanning = False

    def decode_field(self, payload, adv_type):
        i = 0
        result = []
        while i + 1 < len(payload):
            if payload[i + 1] == adv_type:
                result.append(payload[i + 2 : i + payload[i] + 1])
            i += 1 + payload[i]
        return result
        
    def decode_name(self,payload):
        n = self.decode_field(payload, NAME_FLAG)
        return str(n[0], "utf-8") if n else ""

    def scan(self, duration = 2000):
        self.scanning = True
        #run for duration sec, with checking every 30 ms for 30 ms
        duration = 0 if duration < 0 else duration
        return self._ble.gap_scan(duration, 30000, 30000)

    def stop_scan(self):
        self._scan_callback = None
        self._ble.gap_scan(None)
        self.scanning = False

c = Sniff()
d = 100
while True:
    c.scan(d)
    time.sleep_ms(d)
    c.stop_scan()
    command = c.command
    print(command, end = '')

    #nothing
    if command == 0: 
        print('nothing')
    #honk horn
    elif command == 1:
        sound.volume(100)
        sound.beep(600, 500)
        time.sleep(1)
        sound.beep(600, 1000)
        print('honk')
    #stop
    elif command == 2:
        motor.stop(R)
        motor.stop(L)
        print('stop')
    #right
    elif command == 3:
        motor.run_for_time(L, 675, -200)
        motor.run_for_time(R, 675, -200)
        print('right')
    #left
    elif command == 4:
        motor.run_for_time(L, 675, 200)
        motor.run_for_time(R, 675, 200)
        print('left')
    #up/straight
    elif command == 5:
        motor.run_for_time(L, 1000, 200)
        motor.run_for_time(R, 1000, -200)
        print('straight')
    #down/reverse
    elif command == 6:
        motor.run_for_time(L, 1000, -200)
        motor.run_for_time(R, 1000, 200)
        print('reverse')
    #clockwise spin
    elif command == 7:
        motor.run_for_time(L, 1250, -500)
        motor.run_for_time(R, 1250, -500)
        print('clock spin')
    #counterclockwise spin
    elif command == 8:
        motor.run_for_time(L, 1250, 500)
        motor.run_for_time(R, 1250, 500)
        print('counter spin')
    #wave
    elif command == 9:
        light_matrix.write("HELLO!")
        print('wave')
    else:
        print('unknown')
  
