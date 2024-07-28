from BLE_CEEO import Yell, Listen
from nrf24l01 import NRF24L01
from machine import SPI, Pin
import machine
import time
import struct

csn = Pin(5, mode = Pin.OUT, value = 1)
ce = Pin(0, mode = Pin.OUT, value = 0)
led = Pin("LED", Pin.OUT)
payload_size = 32

led.value(1)

role = "send"
#role = "receive"

# Constants for I2C
I2C_ADDRESS = 0x20  # Default I2C address of Qwiic Joystick

# Register addresses
X_AXIS_REG = 0x03
Y_AXIS_REG = 0x05

# Initialize I2C
i2c = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2), freq=400000)

try:
    p = Yell('bob', verbose = True)
        
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
    nrf = NRF24L01(SPI(0, sck = Pin(6), mosi = Pin(7), miso = Pin(4)), csn, ce, channel = 98, payload_size = payload_size)
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
        print("message sent")
    except OSError:
         pass
    nrf.start_listening()
    
def read_joystick_position():
    try:
        #Read Joystick 0#
        # enable channel 0 (SD0,SC0)
        i2c.writeto(0x70, b'\x01')
        
        # Send command to read X axis
        i2c.writeto(I2C_ADDRESS, bytes([X_AXIS_REG]))
        x0_val = i2c.readfrom(I2C_ADDRESS, 1)[0]

        # Send command to read Y axis
        i2c.writeto(I2C_ADDRESS, bytes([Y_AXIS_REG]))
        y0_val = i2c.readfrom(I2C_ADDRESS, 1)[0]
        
        #Read Joystick 1#
        # enable channel 1 (SD1,SC1)
        i2c.writeto(0x70, b'\x02')
        
        # Send command to read X axis
        i2c.writeto(I2C_ADDRESS, bytes([X_AXIS_REG]))
        x1_val = i2c.readfrom(I2C_ADDRESS, 1)[0]

        # Send command to read Y axis
        i2c.writeto(I2C_ADDRESS, bytes([Y_AXIS_REG]))
        y1_val = i2c.readfrom(I2C_ADDRESS, 1)[0]

        return x0_val, y0_val, x1_val, y1_val
    
    except OSError as e:
        print(f"OSError: {e}")
        return None, None, None, None
    
    
#main
nrf = setup()
nrf.set_channel(98)
nrf.start_listening()
print(f"doing {role}")
msg_string = ""

try:
    while True:
        if p.is_any:
            spike_controls = p.read()
            spike_controls = str(spike_controls.split(".")[0])
            spike_controls = spike_controls.split(",")
            throttle = spike_controls[0]
            #print(throttle)
            button = spike_controls[1]
            
            if button == "True":
                button = "T"
            else:
                button = "F"
            #print(button)
        
        msg = ""
        if role == "send":
            x0, y0, x1, y1 = read_joystick_position()
            if x0 != None:
                x0_trunc = int(x0)//10
                x1_trunc = int(x1)//10
                y0_trunc = int(y0)//10
                y1_trunc = int(y1)//10
                control_input = f"{x0_trunc},{y0_trunc},{x1_trunc},{y1_trunc},{throttle},{button}"
                #control_input = f"{x0},{y0},{x1},{y1}"
                #print(f"X0: {x0}, Y0: {y0}, X1: {x1}, Y1: {y1}")
                send(nrf, control_input)
        else: #wait for messages
            if nrf.any(): #if msg
                package = nrf.recv()
                len_pack = len(package)
                message = struct.unpack(f"{len_pack}s", package)
                msg = message[0].decode()
                #print(msg)

        time.sleep_ms(10)

except KeyboardInterrupt:
    print ("RF stopped")
