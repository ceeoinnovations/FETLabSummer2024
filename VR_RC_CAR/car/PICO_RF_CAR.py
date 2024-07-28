from nrf24l01 import NRF24L01
from machine import SPI, Pin
from BLE_CEEO import Yell, Listen
import time
import struct

csn = Pin(5, mode = Pin.OUT, value = 1)
ce = Pin(0, mode = Pin.OUT, value = 0)
led = Pin("LED", Pin.OUT)
payload_size = 32

led.value(1)

#role = "send"
role = "receive"

msg = "placeholder"

try:
    p = Yell('dave', verbose = True)
        
    if p.connect_up():
        print('P connected')
        time.sleep(2)
except Exception as e:
    print(e)

if role == "send":
    send_pipe = b"\xe1\xf0\xf0\xf0\xf0"
    recieve_pipe = b"\xd2\xf0\xf0\xf0\xf0"
else:
    send_pipe = b"\xd2\xf0\xf0\xf0\xf0"
    recieve_pipe = b"\xe1\xf0\xf0\xf0\xf0"
    
def setup():
    print("initialising the nRF24L0+ module")
    nrf = NRF24L01(SPI(0, sck = Pin(2), mosi = Pin(3), miso = Pin(4)), csn, ce, channel = 98, payload_size = payload_size)
    nrf.open_tx_pipe(send_pipe)
    nrf.open_rx_pipe(1, recieve_pipe)
    nrf.start_listening()
    return nrf

def send(nrf, msg):
    nrf.stop_listening()
    try:
        encoded_string = msg.encode()
        byte_array = bytearray(encoded_string)
        barr_len = len(byte_array)
        buf = struct.pack(f"{barr_len}s", byte_array)
        nrf.send(buf, 1000)
    except OSError:
        pass
    nrf.start_listening()
        
#main
nrf = setup()
nrf.set_channel(98)
nrf.start_listening()

while True:
    if role == "send":
        send(nrf, "test")
    else: #wait for messages
        if nrf.any(): #if msg
            package = nrf.recv()
            len_pack = len(package)
            message = struct.unpack(f"{len_pack}s", package)
            msg = message[0].decode()
            msg = msg.strip('\x00')
            print(msg)
            p.send(msg)
            
    time.sleep_ms(10)
